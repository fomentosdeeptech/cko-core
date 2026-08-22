"""Immutable domain values used by future Local Knowledge Finder use cases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


Metadata = tuple[tuple[str, str], ...]


def _require_text(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True, slots=True)
class SourceFile:
    """Stable identity and descriptive metadata for a source candidate."""

    source_id: str
    path: str
    sha256: str
    size_bytes: int
    media_type: str

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source_id")
        _require_text(self.path, "path")
        _require_text(self.sha256, "sha256")
        _require_text(self.media_type, "media_type")
        if self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """Text and provenance metadata produced by a future extractor."""

    source_id: str
    text: str
    extractor: str
    extractor_version: str
    metadata: Metadata = ()
    status: str = "SUCCESS"

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source_id")
        _require_text(self.extractor, "extractor")
        _require_text(self.extractor_version, "extractor_version")
        _require_text(self.status, "status")


@dataclass(frozen=True, slots=True)
class ExtractionPolicy:
    max_source_file_size: int = 50 * 1024 * 1024
    max_extracted_characters: int = 5_000_000
    max_docx_archive_entries: int = 10_000
    max_docx_uncompressed_bytes: int = 100 * 1024 * 1024
    default_text_encoding: str = "utf-8"

    def __post_init__(self) -> None:
        if min(self.max_source_file_size, self.max_extracted_characters,
               self.max_docx_archive_entries, self.max_docx_uncompressed_bytes) <= 0:
            raise ValueError("extraction limits must be positive")


@dataclass(frozen=True, slots=True)
class ExtractionIssue:
    source_id: str
    path: str
    code: str
    message: str
    recoverable: bool = True
    observed_size: int | None = None


@dataclass(frozen=True, slots=True)
class ExtractionBatchResult:
    results: tuple[ExtractionResult, ...]
    issues: tuple[ExtractionIssue, ...]
    processed_count: int
    success_count: int
    issue_count: int


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Technology-neutral projection of a future textual search result."""

    source_id: str
    score: float
    snippet: str
    path: str
    sha256: str
    title: str = ""
    extension: str = ""
    media_type: str = ""
    root: str = ""

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source_id")
        _require_text(self.path, "path")
        _require_text(self.sha256, "sha256")


@dataclass(frozen=True, slots=True)
class SearchFilter:
    extension: str | None = None
    media_type: str | None = None
    root: str | None = None
    path_prefix: str | None = None
    sha256: str | None = None

    def __post_init__(self) -> None:
        if self.path_prefix is not None:
            path = PurePosixPath(self.path_prefix)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("path_prefix must remain relative")


@dataclass(frozen=True, slots=True)
class SearchQuery:
    text: str
    filters: SearchFilter = SearchFilter()
    limit: int = 20
    offset: int = 0
    snippet_tokens: int = 24


@dataclass(frozen=True, slots=True)
class SearchPage:
    normalized_query: str
    results: tuple[SearchResult, ...]
    total_matches: int
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class IndexingSummary:
    documents_considered: int
    documents_indexed: int
    documents_updated: int
    documents_removed: int
    documents_ignored: int
    failures: int
    schema_version: int


@dataclass(frozen=True, slots=True)
class SearchIndexStatus:
    fts5_available: bool
    indexed_count: int
    schema_version: int
    rebuild_required: bool


@dataclass(frozen=True, slots=True)
class DocumentOrigin:
    root: str
    relative_path: str
    observed_size_bytes: int
    mtime_ns: int


@dataclass(frozen=True, slots=True)
class ExtractionProvenance:
    extractor: str
    extractor_version: str
    status: str
    observed_at: str


@dataclass(frozen=True, slots=True)
class IndexingProvenance:
    indexed: bool
    indexed_at: str | None


@dataclass(frozen=True, slots=True)
class ProcessingIssueRecord:
    document_sha256: str | None
    root: str | None
    relative_path: str
    stage: str
    code: str
    message: str
    recoverable: bool
    observed_at: str


@dataclass(frozen=True, slots=True)
class DuplicateEvidence:
    sha256: str
    origins: tuple[DocumentOrigin, ...]


@dataclass(frozen=True, slots=True)
class DocumentProvenance:
    sha256: str
    size_bytes: int
    extension: str
    media_type: str
    origins: tuple[DocumentOrigin, ...]
    extraction: ExtractionProvenance | None
    indexing: IndexingProvenance
    issues: tuple[ProcessingIssueRecord, ...]
    duplicate: DuplicateEvidence | None


@dataclass(frozen=True, slots=True)
class ProvenanceBundle:
    document: DocumentProvenance
    unresolved_historical_issues: tuple[ProcessingIssueRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportMetadata:
    root: str | None
    observed_at: str


@dataclass(frozen=True, slots=True)
class IngestionReport:
    metadata: ReportMetadata
    discovered_locations: int
    unique_documents: int
    new_documents: int
    known_documents: int
    successful_extractions: int
    no_text_extractions: int
    recoverable_failures: int
    indexed_documents: int
    duplicate_groups: int
    duplicate_locations: int


@dataclass(frozen=True, slots=True)
class FailureReport:
    metadata: ReportMetadata
    issues: tuple[ProcessingIssueRecord, ...]
    unresolved_historical_issues: tuple[ProcessingIssueRecord, ...]


@dataclass(frozen=True, slots=True)
class DuplicateReport:
    metadata: ReportMetadata
    duplicates: tuple[DuplicateEvidence, ...]


@dataclass(frozen=True, slots=True)
class CoreDocumentMapping:
    identity: str
    document_type: str
    size_bytes: int
    locations: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class CoreProvenanceMapping:
    document_identity: str
    source_locations: tuple[tuple[str, str], ...]
    extraction_status: str | None
    derived_content_relation: str | None
    issue_codes: tuple[str, ...]
    duplicate_location_count: int


@dataclass(frozen=True, slots=True)
class ProcessingError:
    """Structured description of an isolated future processing failure."""

    source_id: str
    stage: str
    code: str
    message: str
    recoverable: bool

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source_id")
        _require_text(self.stage, "stage")
        _require_text(self.code, "code")
        _require_text(self.message, "message")


@dataclass(frozen=True, slots=True)
class DiscoveryPolicy:
    """Immutable policy for one local discovery operation."""

    supported_extensions: tuple[str, ...] = (".pdf", ".docx", ".txt", ".md", ".markdown")
    ignore_hidden: bool = True
    follow_symlinks: bool = False
    hash_chunk_size: int = 1024 * 1024

    def __post_init__(self) -> None:
        normalized = tuple(sorted({item.lower() for item in self.supported_extensions}))
        if not normalized or any(not item.startswith(".") for item in normalized):
            raise ValueError("supported_extensions must contain dotted extensions")
        if self.hash_chunk_size <= 0:
            raise ValueError("hash_chunk_size must be positive")
        object.__setattr__(self, "supported_extensions", normalized)


@dataclass(frozen=True, slots=True)
class DiscoveryIssue:
    """Sanitized, deterministic description of an isolated discovery failure."""

    path: str
    stage: str
    code: str
    message: str
    recoverable: bool = True

    def __post_init__(self) -> None:
        for name in ("path", "stage", "code", "message"):
            _require_text(getattr(self, name), name)


@dataclass(frozen=True, slots=True)
class DiscoveredFile:
    """Physical identity and one observed location below an authorized root."""

    file_id: str
    absolute_path: str
    relative_path: str
    sha256: str
    size_bytes: int
    extension: str
    modified_at_ns: int
    media_type: str
    hidden: bool = False

    def __post_init__(self) -> None:
        for name in ("file_id", "absolute_path", "relative_path", "sha256", "extension", "media_type"):
            _require_text(getattr(self, name), name)
        if len(self.sha256) != 64 or any(char not in "0123456789abcdef" for char in self.sha256):
            raise ValueError("sha256 must be 64 lowercase hexadecimal characters")
        if self.file_id != self.sha256:
            raise ValueError("file_id must equal the physical SHA-256 identity")
        if self.size_bytes < 0 or self.modified_at_ns < 0:
            raise ValueError("observed file metadata must not be negative")
        relative = PurePosixPath(self.relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("relative_path must be confined and relative")


@dataclass(frozen=True, slots=True)
class DuplicateGroup:
    """All observed locations sharing one byte-level identity."""

    sha256: str
    size_bytes: int
    relative_paths: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.sha256) != 64:
            raise ValueError("sha256 must contain 64 characters")
        if self.size_bytes < 0 or len(self.relative_paths) < 2:
            raise ValueError("duplicate group requires at least two locations")
        if self.relative_paths != tuple(sorted(set(self.relative_paths), key=lambda value: (value.casefold(), value))):
            raise ValueError("relative_paths must be unique and deterministically ordered")


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    """Immutable in-memory result of one confined discovery operation."""

    root: str
    files: tuple[DiscoveredFile, ...]
    duplicate_groups: tuple[DuplicateGroup, ...]
    ignored_count: int
    issues: tuple[DiscoveryIssue, ...]
    discovered_count: int
    duplicate_group_count: int
    issue_count: int

    def __post_init__(self) -> None:
        _require_text(self.root, "root")
        if min(self.ignored_count, self.discovered_count, self.duplicate_group_count, self.issue_count) < 0:
            raise ValueError("summary counts must not be negative")
        if self.discovered_count != len(self.files):
            raise ValueError("discovered_count must match files")
        if self.duplicate_group_count != len(self.duplicate_groups):
            raise ValueError("duplicate_group_count must match duplicate_groups")
        if self.issue_count != len(self.issues):
            raise ValueError("issue_count must match issues")


@dataclass(frozen=True, slots=True)
class StoredDocument:
    sha256: str
    size_bytes: int
    extension: str
    media_type: str
    first_seen: str
    last_seen: str
    physical_metadata: Metadata = ()


@dataclass(frozen=True, slots=True)
class StoredLocation:
    document_sha256: str
    root: str
    relative_path: str
    observed_size_bytes: int
    mtime_ns: int
    first_seen: str
    last_seen: str


@dataclass(frozen=True, slots=True)
class StoredIssue:
    relative_path: str
    stage: str
    code: str
    message: str
    recoverable: bool
    observed_at: str


@dataclass(frozen=True, slots=True)
class PersistenceSummary:
    documents_inserted: int
    documents_updated: int
    locations_inserted: int
    locations_updated: int
    issues_recorded: int
    schema_version: int


@dataclass(frozen=True, slots=True)
class DatabaseCapability:
    sqlite_version: str
    fts5_available: bool
    foreign_keys_enabled: bool
    schema_version: int
