"""Deterministic batch orchestration for text extraction."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from cko_local_finder.application.ports import DocumentRepositoryPort
from cko_local_finder.domain.models import (
    DiscoveredFile, ExtractionBatchResult, ExtractionIssue, ExtractionResult,
)
from cko_local_finder.infrastructure.extractors import ExtractionError, ExtractorRegistry


def extract_documents(
    files: tuple[DiscoveredFile, ...],
    registry: ExtractorRegistry,
    repository: DocumentRepositoryPort,
    *,
    observed_at: str | None = None,
    on_results_persisted: Callable[[tuple[ExtractionResult, ...]], None] | None = None,
) -> ExtractionBatchResult:
    timestamp = observed_at or datetime.now(timezone.utc).isoformat()
    results: list[ExtractionResult] = []
    issues: list[ExtractionIssue] = []
    try:
        for source in sorted(files, key=lambda item: (item.relative_path.casefold(), item.relative_path)):
            try:
                result = registry.select(source).extract(source)
                with repository.transaction():
                    repository.save_extraction(result, timestamp)
                results.append(result)
            except ExtractionError as exc:
                issue = ExtractionIssue(source.sha256, source.relative_path, exc.code, str(exc), True, exc.observed_size)
                with repository.transaction():
                    repository.record_extraction_issue(issue, timestamp)
                issues.append(issue)
    finally:
        if on_results_persisted is not None and results:
            on_results_persisted(tuple(results))
    return ExtractionBatchResult(tuple(results), tuple(issues), len(files), len(results), len(issues))
