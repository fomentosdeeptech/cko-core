"""Canonical descriptive metadata for logical documents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from .contracts import (
    DOCUMENT_SCHEMA_VERSION, DocumentModel, instant, model_sequence, probability,
    sha256, text, unique_texts,
)
from .enums import DocumentLanguageCode, DocumentSourceType
from .errors import DocumentValidationError


@dataclass(frozen=True, slots=True)
class DocumentLanguage(DocumentModel):
    code: DocumentLanguageCode
    locale: str | None = None
    name: str | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_language"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "code", DocumentLanguageCode(self.code))
        except (TypeError, ValueError) as error:
            raise DocumentValidationError("code must be DocumentLanguageCode") from error
        object.__setattr__(self, "locale", text(self.locale, "locale", optional=True))
        object.__setattr__(self, "name", text(self.name, "name", optional=True))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentAuthor(DocumentModel):
    name: str
    identifier: str | None = None
    organization: str | None = None
    role: str | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_author"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", text(self.name, "name"))
        for name in ("identifier", "organization", "role"):
            object.__setattr__(self, name, text(getattr(self, name), name, optional=True))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentSource(DocumentModel):
    source_type: DocumentSourceType
    identifier: str
    origin: str
    external_id: str | None = None
    retrieved_at: datetime | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_source"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "source_type", DocumentSourceType(self.source_type))
        except (TypeError, ValueError) as error:
            raise DocumentValidationError("source_type must be DocumentSourceType") from error
        object.__setattr__(self, "identifier", text(self.identifier, "identifier"))
        object.__setattr__(self, "origin", text(self.origin, "origin"))
        object.__setattr__(self, "external_id", text(self.external_id, "external_id", optional=True))
        object.__setattr__(self, "retrieved_at", instant(self.retrieved_at, "retrieved_at", optional=True))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentMetadata(DocumentModel):
    title: str
    created_at: datetime
    modified_at: datetime
    subtitle: str | None = None
    author: DocumentAuthor | None = None
    coauthors: tuple[DocumentAuthor, ...] = ()
    creator: str | None = None
    editor: str | None = None
    language: DocumentLanguage | None = None
    keywords: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    domain: str | None = None
    category: str | None = None
    license: str | None = None
    sources: tuple[DocumentSource, ...] = ()
    checksum: str | None = None
    published_at: datetime | None = None
    organization: str | None = None
    version: str = "1.0.0"
    confidence: float | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_metadata"

    def __post_init__(self) -> None:
        object.__setattr__(self, "title", text(self.title, "title"))
        created = instant(self.created_at, "created_at")
        modified = instant(self.modified_at, "modified_at")
        assert isinstance(created, datetime) and isinstance(modified, datetime)
        if modified < created:
            raise DocumentValidationError("modified_at cannot precede created_at")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "modified_at", modified)
        published = instant(self.published_at, "published_at", optional=True)
        object.__setattr__(self, "published_at", published)
        if self.author is not None and not isinstance(self.author, DocumentAuthor):
            raise DocumentValidationError("author must be DocumentAuthor")
        object.__setattr__(self, "coauthors", model_sequence(self.coauthors, "coauthors", DocumentAuthor))
        identities = tuple((item.identifier or item.name.casefold()) for item in self.coauthors)
        if len(identities) != len(set(identities)):
            raise DocumentValidationError("coauthors must not contain duplicates")
        if self.author is not None and (self.author.identifier or self.author.name.casefold()) in identities:
            raise DocumentValidationError("author cannot also be a coauthor")
        if self.language is not None and not isinstance(self.language, DocumentLanguage):
            raise DocumentValidationError("language must be DocumentLanguage")
        for name in ("subtitle", "creator", "editor", "domain", "category", "license", "organization"):
            object.__setattr__(self, name, text(getattr(self, name), name, optional=True))
        object.__setattr__(self, "version", text(self.version, "version"))
        object.__setattr__(self, "keywords", unique_texts(self.keywords, "keywords"))
        object.__setattr__(self, "tags", unique_texts(self.tags, "tags"))
        object.__setattr__(self, "sources", model_sequence(self.sources, "sources", DocumentSource))
        source_keys = tuple((item.source_type, item.identifier) for item in self.sources)
        if len(source_keys) != len(set(source_keys)):
            raise DocumentValidationError("sources must not contain duplicates")
        object.__setattr__(self, "checksum", sha256(self.checksum, "checksum", optional=True))
        object.__setattr__(self, "confidence", probability(self.confidence, "confidence"))
        self._validate_schema()


__all__ = ["DocumentAuthor", "DocumentLanguage", "DocumentMetadata", "DocumentSource"]
