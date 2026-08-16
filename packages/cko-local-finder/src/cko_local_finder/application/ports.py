"""Abstract application boundaries with no concrete operations or adapters."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from cko_local_finder.domain.models import ExtractionResult, SearchResult, SourceFile


class DiscoveryPort(Protocol):
    """Provide confined source candidates for a future ingestion use case."""

    def discover(self, root: str) -> Iterable[SourceFile]: ...


class ExtractorPort(Protocol):
    """Describe a future document extraction capability."""

    def supports(self, source: SourceFile) -> bool: ...

    def extract(self, source: SourceFile) -> ExtractionResult: ...


class DocumentRepositoryPort(Protocol):
    """Persist and retrieve future document records through an abstraction."""

    def save(self, source: SourceFile, extraction: ExtractionResult) -> None: ...

    def get(self, source_id: str) -> ExtractionResult | None: ...

    def find_duplicates(self, sha256: str) -> Iterable[SourceFile]: ...


class SearchIndexPort(Protocol):
    """Index and query future extracted text through an abstraction."""

    def index(self, source: SourceFile, extraction: ExtractionResult) -> None: ...

    def search(self, query: str) -> Iterable[SearchResult]: ...


class ProvenancePort(Protocol):
    """Record future source and extraction provenance."""

    def record(self, source: SourceFile, extraction: ExtractionResult) -> None: ...
