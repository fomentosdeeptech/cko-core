"""Typed, presentation-neutral application facade for all user interfaces."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from cko_local_finder.application.discovery import Scanner, run_discovery
from cko_local_finder.application.extraction import ExtractorSelector, extract_documents
from cko_local_finder.application.indexing import index_documents
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.application.ports import DocumentRepositoryPort, ProvenancePort, SearchIndexPort
from cko_local_finder.application.provenance import provenance_for_sha256
from cko_local_finder.application.reporting import build_duplicate_report, build_failure_report, build_ingestion_report
from cko_local_finder.application.search import search_documents
from cko_local_finder.domain.models import (
    DatabaseCapability, DiscoveryPolicy, DuplicateReport, FailureReport, IngestionReport,
    ProvenanceBundle, SearchFilter, SearchPage, SearchQuery,
)


class ProgressStage(str, Enum):
    INGESTION_STARTED = "INGESTION_STARTED"
    DISCOVERY_STARTED = "DISCOVERY_STARTED"
    DISCOVERY_COMPLETED = "DISCOVERY_COMPLETED"
    PERSISTENCE_STARTED = "PERSISTENCE_STARTED"
    PERSISTENCE_COMPLETED = "PERSISTENCE_COMPLETED"
    EXTRACTION_STARTED = "EXTRACTION_STARTED"
    EXTRACTION_COMPLETED = "EXTRACTION_COMPLETED"
    INDEXING_STARTED = "INDEXING_STARTED"
    INDEXING_COMPLETED = "INDEXING_COMPLETED"
    REPORTING_STARTED = "REPORTING_STARTED"
    REPORTING_COMPLETED = "REPORTING_COMPLETED"
    INGESTION_COMPLETED = "INGESTION_COMPLETED"
    STAGE_FAILED = "STAGE_FAILED"


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    stage: ProgressStage
    count: int | None = None


ProgressCallback = Callable[[ProgressEvent], None]
Repository = DocumentRepositoryPort | SearchIndexPort | ProvenancePort
RepositoryFactory = Callable[[str, bool], Repository]


@dataclass(frozen=True, slots=True)
class IngestRequest:
    root: str
    database: str
    include_hidden: bool = False
    follow_symlinks: bool = False


@dataclass(frozen=True, slots=True)
class IngestResult:
    root: str
    database: str
    discovered_documents: int
    unique_documents: int
    locations: int
    duplicate_groups: int
    successful_extractions: int
    recoverable_failures: int
    indexed_documents: int
    report: IngestionReport


@dataclass(frozen=True, slots=True)
class SearchRequest:
    query: str
    database: str
    limit: int = 20
    extension: str | None = None
    media_type: str | None = None
    root: str | None = None
    path_prefix: str | None = None
    sha256: str | None = None
    offset: int = 0


class ApplicationFacade:
    def __init__(self, repository_factory: RepositoryFactory, scanner: Scanner,
                 extractor_factory: Callable[[], ExtractorSelector], *,
                 clock: Callable[[], str] | None = None) -> None:
        self._repositories = repository_factory
        self._scanner = scanner
        self._extractors = extractor_factory
        self._clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def _emit(callback: ProgressCallback | None, stage: ProgressStage, count: int | None = None) -> None:
        if callback is not None:
            callback(ProgressEvent(stage, count))

    def _repository(self, database: str, create: bool) -> Repository:
        return self._repositories(database, create)

    def validate_database(self, database: str, *, create: bool = False) -> DatabaseCapability:
        return self._repository(database, create).capabilities()  # type: ignore[union-attr]

    def ingest(self, request: IngestRequest, *, on_progress: ProgressCallback | None = None) -> IngestResult:
        source_root = Path(request.root).expanduser()
        if not source_root.is_dir():
            raise FileNotFoundError("source root not found")
        repository = self._repository(request.database, True)
        observed_at = self._clock()
        self._emit(on_progress, ProgressStage.INGESTION_STARTED)
        try:
            self._emit(on_progress, ProgressStage.DISCOVERY_STARTED)
            discovery = run_discovery(source_root, DiscoveryPolicy(
                ignore_hidden=not request.include_hidden, follow_symlinks=request.follow_symlinks,
            ), scanner=self._scanner)
            self._emit(on_progress, ProgressStage.DISCOVERY_COMPLETED, discovery.discovered_count)
            self._emit(on_progress, ProgressStage.PERSISTENCE_STARTED)
            persistence = persist_discovery_report(discovery, repository, observed_at=observed_at)  # type: ignore[arg-type]
            self._emit(on_progress, ProgressStage.PERSISTENCE_COMPLETED,
                       persistence.locations_inserted + persistence.locations_updated)
            self._emit(on_progress, ProgressStage.EXTRACTION_STARTED)
            indexing = None

            def index_persisted(results):
                nonlocal indexing
                self._emit(on_progress, ProgressStage.INDEXING_STARTED)
                indexing = index_documents(tuple(item.source_id for item in results), repository,
                                           observed_at=observed_at)  # type: ignore[arg-type]
                self._emit(on_progress, ProgressStage.INDEXING_COMPLETED, indexing.documents_indexed)

            extraction = extract_documents(discovery.files, self._extractors(), repository,
                                           observed_at=observed_at,
                                           on_results_persisted=index_persisted)  # type: ignore[arg-type]
            self._emit(on_progress, ProgressStage.EXTRACTION_COMPLETED, extraction.success_count)
            if indexing is None:
                self._emit(on_progress, ProgressStage.INDEXING_STARTED)
                indexing = index_documents(tuple(item.source_id for item in extraction.results), repository,
                                           observed_at=observed_at)  # type: ignore[arg-type]
                self._emit(on_progress, ProgressStage.INDEXING_COMPLETED, indexing.documents_indexed)
            self._emit(on_progress, ProgressStage.REPORTING_STARTED)
            report = build_ingestion_report(discovery.root, observed_at, repository)  # type: ignore[arg-type]
            self._emit(on_progress, ProgressStage.REPORTING_COMPLETED)
            result = IngestResult(discovery.root, str(Path(request.database).expanduser()),
                report.discovered_locations, report.unique_documents, report.discovered_locations,
                report.duplicate_groups, report.successful_extractions,
                discovery.issue_count + extraction.issue_count + indexing.failures,
                report.indexed_documents, report)
            self._emit(on_progress, ProgressStage.INGESTION_COMPLETED)
            return result
        except Exception:
            self._emit(on_progress, ProgressStage.STAGE_FAILED)
            raise

    def search(self, request: SearchRequest) -> SearchPage:
        repository = self._repository(request.database, False)
        repository.apply_provenance_migrations()  # type: ignore[union-attr]
        filters = SearchFilter(request.extension, request.media_type, request.root,
                               request.path_prefix, request.sha256)
        return search_documents(SearchQuery(request.query, filters, request.limit, request.offset), repository)  # type: ignore[arg-type]

    def get_document_details(self, sha256: str, database: str) -> ProvenanceBundle:
        return provenance_for_sha256(sha256, self._repository(database, False))  # type: ignore[arg-type]

    def get_ingestion_report(self, database: str, root: str) -> IngestionReport:
        return build_ingestion_report(root, self._clock(), self._repository(database, False))  # type: ignore[arg-type]

    def get_failure_report(self, database: str, root: str | None = None) -> FailureReport:
        return build_failure_report(root, self._clock(), self._repository(database, False))  # type: ignore[arg-type]

    def get_duplicate_report(self, database: str, root: str | None = None) -> DuplicateReport:
        return build_duplicate_report(root, self._clock(), self._repository(database, False))  # type: ignore[arg-type]
