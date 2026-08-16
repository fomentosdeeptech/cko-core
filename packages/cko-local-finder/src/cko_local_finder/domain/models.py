"""Immutable domain values used by future Local Knowledge Finder use cases."""

from __future__ import annotations

from dataclasses import dataclass


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

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source_id")
        _require_text(self.extractor, "extractor")
        _require_text(self.extractor_version, "extractor_version")


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Technology-neutral projection of a future textual search result."""

    source_id: str
    score: float
    snippet: str
    path: str
    sha256: str

    def __post_init__(self) -> None:
        _require_text(self.source_id, "source_id")
        _require_text(self.path, "path")
        _require_text(self.sha256, "sha256")


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
