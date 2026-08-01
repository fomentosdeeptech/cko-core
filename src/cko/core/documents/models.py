"""Immutable canonical document models and aggregate."""

from __future__ import annotations

from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from cko.core.knowledge import KnowledgeObject

from .contracts import (
    DOCUMENT_SCHEMA_VERSION, DocumentModel, instant, model_sequence, non_negative,
    probability, sha256, text, unique_texts,
)
from .enums import DocumentFormat, DocumentStatus, DocumentType, IntegrityStatus
from .errors import DocumentFactoryError, DocumentValidationError
from .identity import DocumentId, DocumentIdentity
from .metadata import DocumentMetadata


_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True)
class DocumentDescriptor(DocumentModel):
    document_type: DocumentType
    status: DocumentStatus = DocumentStatus.ACTIVE
    summary: str | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_descriptor"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "document_type", DocumentType(self.document_type))
            object.__setattr__(self, "status", DocumentStatus(self.status))
        except (TypeError, ValueError) as error:
            raise DocumentValidationError("invalid document descriptor enum") from error
        object.__setattr__(self, "summary", text(self.summary, "summary", optional=True))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentContentDescriptor(DocumentModel):
    content_type: str | None = None
    fragment_ids: tuple[str, ...] = ()
    extraction_ids: tuple[str, ...] = ()
    logical_size: int | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_content_descriptor"

    def __post_init__(self) -> None:
        object.__setattr__(self, "content_type", text(self.content_type, "content_type", optional=True))
        object.__setattr__(self, "fragment_ids", unique_texts(self.fragment_ids, "fragment_ids"))
        object.__setattr__(self, "extraction_ids", unique_texts(self.extraction_ids, "extraction_ids"))
        object.__setattr__(self, "logical_size", non_negative(self.logical_size, "logical_size"))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentRepresentation(DocumentModel):
    format: DocumentFormat
    mime_type: str | None = None
    encoding: str | None = None
    extension: str | None = None
    compression: str | None = None
    hash: str | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_representation"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "format", DocumentFormat(self.format))
        except (TypeError, ValueError) as error:
            raise DocumentValidationError("format must be DocumentFormat") from error
        for name in ("mime_type", "encoding", "extension", "compression"):
            object.__setattr__(self, name, text(getattr(self, name), name, optional=True))
        if self.extension is not None:
            object.__setattr__(self, "extension", self.extension.lower().lstrip("."))
        object.__setattr__(self, "hash", sha256(self.hash, "hash", optional=True))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentVersion(DocumentModel):
    version_id: UUID
    version: str
    created_at: datetime
    created_by: str
    status: DocumentStatus = DocumentStatus.ACTIVE
    parent_version: UUID | None = None
    checksum: str | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_version"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "version_id", self.version_id if isinstance(self.version_id, UUID) else UUID(str(self.version_id)))
            if self.parent_version is not None:
                object.__setattr__(self, "parent_version", self.parent_version if isinstance(self.parent_version, UUID) else UUID(str(self.parent_version)))
        except (TypeError, ValueError, AttributeError) as error:
            raise DocumentValidationError("version identifiers must be UUID values") from error
        if self.parent_version == self.version_id:
            raise DocumentValidationError("version cannot be its own parent")
        object.__setattr__(self, "version", text(self.version, "version"))
        object.__setattr__(self, "created_by", text(self.created_by, "created_by"))
        object.__setattr__(self, "created_at", instant(self.created_at, "created_at"))
        try:
            object.__setattr__(self, "status", DocumentStatus(self.status))
        except (TypeError, ValueError) as error:
            raise DocumentValidationError("status must be DocumentStatus") from error
        object.__setattr__(self, "checksum", sha256(self.checksum, "checksum", optional=True))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentStatistics(DocumentModel):
    pages: int | None = None
    characters: int | None = None
    words: int | None = None
    lines: int | None = None
    tables: int | None = None
    images: int | None = None
    attachments: int | None = None
    links: int | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_statistics"

    def __post_init__(self) -> None:
        for name in ("pages", "characters", "words", "lines", "tables", "images", "attachments", "links"):
            object.__setattr__(self, name, non_negative(getattr(self, name), name))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentIntegrity(DocumentModel):
    sha256: str
    logical_size: int | None = None
    physical_size: int | None = None
    signature: str | None = None
    is_intact: bool | None = None
    status: IntegrityStatus = IntegrityStatus.UNKNOWN
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_integrity"

    def __post_init__(self) -> None:
        object.__setattr__(self, "sha256", sha256(self.sha256))
        object.__setattr__(self, "logical_size", non_negative(self.logical_size, "logical_size"))
        object.__setattr__(self, "physical_size", non_negative(self.physical_size, "physical_size"))
        object.__setattr__(self, "signature", text(self.signature, "signature", optional=True))
        if self.is_intact is not None and not isinstance(self.is_intact, bool):
            raise DocumentValidationError("is_intact must be boolean when provided")
        try:
            object.__setattr__(self, "status", IntegrityStatus(self.status))
        except (TypeError, ValueError) as error:
            raise DocumentValidationError("status must be IntegrityStatus") from error
        if self.status is IntegrityStatus.VERIFIED and self.is_intact is not True:
            raise DocumentValidationError("verified integrity requires is_intact true")
        if self.status is IntegrityStatus.MISMATCH and self.is_intact is not False:
            raise DocumentValidationError("mismatched integrity requires is_intact false")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentRights(DocumentModel):
    license: str | None = None
    copyright_holder: str | None = None
    access: str | None = None
    expires_at: datetime | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_rights"

    def __post_init__(self) -> None:
        for name in ("license", "copyright_holder", "access"):
            object.__setattr__(self, name, text(getattr(self, name), name, optional=True))
        object.__setattr__(self, "expires_at", instant(self.expires_at, "expires_at", optional=True))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CanonicalDocument(DocumentModel):
    identity: DocumentIdentity
    metadata: DocumentMetadata
    descriptor: DocumentDescriptor
    content: DocumentContentDescriptor
    knowledge_object: KnowledgeObject
    representations: tuple[DocumentRepresentation, ...] = ()
    versions: tuple[DocumentVersion, ...] = ()
    statistics: DocumentStatistics | None = None
    integrity: DocumentIntegrity | None = None
    rights: DocumentRights | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "canonical_document"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise DocumentFactoryError("CanonicalDocument must be created by DocumentFactory")
        expected = (
            (self.identity, DocumentIdentity), (self.metadata, DocumentMetadata),
            (self.descriptor, DocumentDescriptor), (self.content, DocumentContentDescriptor),
            (self.knowledge_object, KnowledgeObject),
        )
        if any(not isinstance(value, model) for value, model in expected):
            raise DocumentValidationError("canonical document contains an invalid required model")
        object.__setattr__(self, "representations", model_sequence(self.representations, "representations", DocumentRepresentation))
        object.__setattr__(self, "versions", model_sequence(self.versions, "versions", DocumentVersion))
        for value, model, name in (
            (self.statistics, DocumentStatistics, "statistics"),
            (self.integrity, DocumentIntegrity, "integrity"),
            (self.rights, DocumentRights, "rights"),
        ):
            if value is not None and not isinstance(value, model):
                raise DocumentValidationError(f"{name} contains an invalid model")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class DocumentCollection(DocumentModel):
    documents: tuple[CanonicalDocument, ...] = ()
    name: str | None = None
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "document_collection"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise DocumentFactoryError("DocumentCollection must be created by DocumentFactory")
        object.__setattr__(self, "documents", model_sequence(self.documents, "documents", CanonicalDocument))
        object.__setattr__(self, "name", text(self.name, "name", optional=True))
        identifiers = tuple(item.identity.document_id for item in self.documents)
        if len(identifiers) != len(set(identifiers)):
            raise DocumentValidationError("collection documents must be unique")
        self._validate_schema()

    def __iter__(self):
        return iter(self.documents)

    def __len__(self) -> int:
        return len(self.documents)


__all__ = [
    "CanonicalDocument", "DocumentCollection", "DocumentContentDescriptor",
    "DocumentDescriptor", "DocumentIntegrity", "DocumentRepresentation",
    "DocumentRights", "DocumentStatistics", "DocumentVersion", "_FACTORY_TOKEN",
]
