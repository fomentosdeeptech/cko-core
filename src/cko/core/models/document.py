"""Representações canônicas de documento, localização e inventário."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

from cko.core.identity import CanonicalId, Origin, SemanticVersion
from cko.core.metadata import UniversalMetadata
from cko.core.utils import ensure_aware, require_non_empty


@dataclass(frozen=True, slots=True)
class CanonicalDocument:
    """Documento identificado sem dependência de caminho ou armazenamento."""

    id: CanonicalId
    version: SemanticVersion
    origin: Origin
    metadata: UniversalMetadata
    title: str | None = None

    def __post_init__(self) -> None:
        if self.title is not None:
            object.__setattr__(self, "title", require_non_empty(self.title, "title"))


@dataclass(frozen=True, slots=True)
class DocumentLocation:
    """Referência observada para um documento, expressa como URI."""

    id: CanonicalId
    document_id: CanonicalId
    uri: str
    observed_at: datetime

    def __post_init__(self) -> None:
        normalized_uri = require_non_empty(self.uri, "uri")
        if not urlparse(normalized_uri).scheme:
            raise ValueError("uri deve possuir um esquema explícito")
        object.__setattr__(self, "uri", normalized_uri)
        object.__setattr__(self, "observed_at", ensure_aware(self.observed_at))


@dataclass(frozen=True, slots=True)
class InventoryItem:
    """Associação neutra entre documento e localização inventariada."""

    id: CanonicalId
    document: CanonicalDocument
    location: DocumentLocation
    inventoried_at: datetime

    def __post_init__(self) -> None:
        if self.location.document_id != self.document.id:
            raise ValueError("location.document_id deve referenciar document.id")
        object.__setattr__(self, "inventoried_at", ensure_aware(self.inventoried_at))

