"""Deterministic batch orchestration for text extraction."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Protocol

from cko_local_finder.application.ports import DocumentRepositoryPort
from cko_local_finder.domain.models import (
    DiscoveredFile, ExtractionBatchResult, ExtractionIssue, ExtractionResult,
)


class RecoverableExtractionError(RuntimeError):
    def __init__(self, code: str, message: str, *, observed_size: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.observed_size = observed_size


class SelectedExtractor(Protocol):
    def extract(self, source: DiscoveredFile) -> ExtractionResult: ...


class ExtractorSelector(Protocol):
    def select(self, source: DiscoveredFile) -> SelectedExtractor: ...


def extract_documents(
    files: tuple[DiscoveredFile, ...],
    registry: ExtractorSelector,
    repository: DocumentRepositoryPort,
    *,
    observed_at: str | None = None,
    on_results_persisted: Callable[[tuple[ExtractionResult, ...]], None] | None = None,
) -> ExtractionBatchResult:
    timestamp = observed_at or datetime.now(timezone.utc).isoformat()
    results: list[ExtractionResult] = []
    issues: list[ExtractionIssue] = []
    completed = False
    try:
        for source in sorted(files, key=lambda item: (item.relative_path.casefold(), item.relative_path)):
            try:
                result = registry.select(source).extract(source)
                with repository.transaction():
                    repository.save_extraction(result, timestamp)
                results.append(result)
            except RecoverableExtractionError as exc:
                issue = ExtractionIssue(source.sha256, source.relative_path, exc.code, str(exc), True, exc.observed_size)
                with repository.transaction():
                    repository.record_extraction_issue(issue, timestamp)
                issues.append(issue)
        completed = True
    finally:
        if not completed and on_results_persisted is not None and results:
            on_results_persisted(tuple(results))
    return ExtractionBatchResult(tuple(results), tuple(issues), len(files), len(results), len(issues))
