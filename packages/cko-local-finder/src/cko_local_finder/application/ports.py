"""Abstract application boundaries with no concrete operations or adapters."""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import AbstractContextManager
from typing import Protocol

from cko_local_finder.domain.models import (
    DatabaseCapability,
    DiscoveryIssue,
    DiscoveryReport,
    DiscoveredFile,
    DuplicateGroup,
    ExtractionResult,
    ExtractionIssue,
    PersistenceSummary,
    SearchResult,
    SearchIndexStatus,
    SearchPage,
    SearchQuery,
    IndexingSummary,
    SourceFile,
    StoredDocument,
    StoredLocation,
)


class DiscoveryPort(Protocol):
    """Provide confined source candidates for a future ingestion use case."""

    def discover(self, root: str) -> Iterable[SourceFile]: ...


class ExtractorPort(Protocol):
    """Describe a future document extraction capability."""

    def supports(self, source: DiscoveredFile) -> bool: ...

    def extract(self, source: DiscoveredFile) -> ExtractionResult: ...


class DocumentRepositoryPort(Protocol):
    """Persist discovery state without exposing SQLite implementation details."""

    def apply_migrations(self) -> int: ...

    def transaction(self) -> AbstractContextManager[None]: ...

    def persist_report(self, report: DiscoveryReport, observed_at: str) -> PersistenceSummary: ...

    def get_document(self, sha256: str) -> StoredDocument | None: ...

    def list_locations(self, sha256: str) -> tuple[StoredLocation, ...]: ...

    def find_duplicates(self) -> tuple[DuplicateGroup, ...]: ...

    def record_issue(self, issue: DiscoveryIssue, observed_at: str) -> bool: ...

    def save_extraction(self, result: ExtractionResult, observed_at: str) -> None: ...

    def get_extraction(self, document_sha256: str, extractor: str, extractor_version: str) -> ExtractionResult | None: ...

    def record_extraction_issue(self, issue: ExtractionIssue, observed_at: str) -> None: ...

    def capabilities(self) -> DatabaseCapability: ...


class SearchIndexPort(Protocol):
    """Index and query extracted text without exposing storage details."""

    def apply_search_migrations(self) -> int: ...

    def index_document(self, document_sha256: str, observed_at: str) -> IndexingSummary: ...

    def remove_from_index(self, document_sha256: str) -> bool: ...

    def rebuild_index(self, observed_at: str) -> IndexingSummary: ...

    def search(self, query: SearchQuery) -> SearchPage: ...

    def search_index_status(self) -> SearchIndexStatus: ...


class ProvenancePort(Protocol):
    """Record future source and extraction provenance."""

    def record(self, source: SourceFile, extraction: ExtractionResult) -> None: ...
