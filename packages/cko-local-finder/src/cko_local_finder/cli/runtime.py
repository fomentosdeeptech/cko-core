"""Composition of ratified application services and infrastructure adapters."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from cko_local_finder.application.discovery import run_discovery
from cko_local_finder.application.extraction import extract_documents
from cko_local_finder.application.indexing import index_documents
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.application.provenance import provenance_for_sha256
from cko_local_finder.application.reporting import build_duplicate_report, build_failure_report, build_ingestion_report
from cko_local_finder.application.search import search_documents
from cko_local_finder.domain.models import DiscoveryPolicy, DuplicateReport, IngestionReport, ProvenanceBundle, SearchFilter, SearchPage, SearchQuery
from cko_local_finder.infrastructure.extractors import ExtractorRegistry
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

class RequiredResourceUnavailable(RuntimeError):
    """A required local runtime capability is unavailable."""

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

def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

def _repository(database: str, *, create: bool) -> SQLiteDocumentRepository:
    path = Path(database).expanduser()
    if not create and not path.is_file():
        raise FileNotFoundError("database not found")
    repository = SQLiteDocumentRepository(path)
    if not repository.capabilities().fts5_available:
        raise RequiredResourceUnavailable("FTS5 is unavailable")
    return repository

def ingest(root: str, database: str, *, include_hidden: bool = False, follow_symlinks: bool = False) -> IngestResult:
    source_root = Path(root).expanduser()
    if not source_root.is_dir():
        raise FileNotFoundError("source root not found")
    repository = _repository(database, create=True)
    observed_at = _timestamp()
    discovery = run_discovery(source_root, DiscoveryPolicy(ignore_hidden=not include_hidden, follow_symlinks=follow_symlinks))
    persist_discovery_report(discovery, repository, observed_at=observed_at)
    indexing = None
    def index_persisted(results):
        nonlocal indexing
        indexing = index_documents(tuple(item.source_id for item in results), repository, observed_at=observed_at)
    extraction = extract_documents(discovery.files, ExtractorRegistry(), repository, observed_at=observed_at,
                                   on_results_persisted=index_persisted)
    if indexing is None:
        indexing = index_documents((), repository, observed_at=observed_at)
    report = build_ingestion_report(discovery.root, observed_at, repository)
    return IngestResult(discovery.root, str(Path(database).expanduser()), report.discovered_locations,
                        report.unique_documents, report.discovered_locations,
                        report.duplicate_groups, report.successful_extractions,
                        discovery.issue_count + extraction.issue_count + indexing.failures,
                        report.indexed_documents, report)

def search(query: str, database: str, *, limit: int = 20, extension: str | None = None,
           media_type: str | None = None, root: str | None = None,
           path_prefix: str | None = None, sha256: str | None = None) -> SearchPage:
    repository = _repository(database, create=False)
    repository.apply_provenance_migrations()
    return search_documents(SearchQuery(query, SearchFilter(extension, media_type, root, path_prefix, sha256), limit), repository)

def show(sha256: str, database: str) -> ProvenanceBundle:
    return provenance_for_sha256(sha256, _repository(database, create=False))

def duplicates(database: str, *, root: str | None = None) -> DuplicateReport:
    return build_duplicate_report(root, _timestamp(), _repository(database, create=False))

def report(report_type: str, database: str, *, root: str | None = None) -> Any:
    repository = _repository(database, create=False)
    observed_at = _timestamp()
    if report_type == "ingestion":
        if root is None:
            raise ValueError("ingestion report requires --root")
        return build_ingestion_report(root, observed_at, repository)
    if report_type == "failures":
        return build_failure_report(root, observed_at, repository)
    return build_duplicate_report(root, observed_at, repository)
