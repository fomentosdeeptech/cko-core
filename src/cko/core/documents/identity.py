"""Logical, documentary, physical, and external document identity."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import ClassVar, Mapping
from uuid import UUID, uuid4, uuid5

from cko.core.knowledge import KnowledgeObjectId

from .contracts import DOCUMENT_SCHEMA_VERSION, DocumentModel, deep_freeze, primitive, text, unique_texts
from .errors import DocumentValidationError


_DOCUMENT_NAMESPACE = UUID("53ebc8dc-30dd-4f6d-971f-ef5900b63ed3")


@dataclass(frozen=True, order=True, slots=True)
class DocumentId(DocumentModel):
    value: UUID
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_id"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "value", self.value if isinstance(self.value, UUID) else UUID(str(self.value)))
        except (TypeError, ValueError, AttributeError) as error:
            raise DocumentValidationError("value must be a UUID") from error
        self._validate_schema()

    @classmethod
    def new(cls) -> DocumentId:
        return cls(uuid4())

    @classmethod
    def canonical(cls, namespace: str, logical_id: DocumentId) -> DocumentId:
        normalized = text(namespace, "namespace")
        if not isinstance(logical_id, DocumentId):
            raise DocumentValidationError("logical_id must be DocumentId")
        return cls(uuid5(_DOCUMENT_NAMESPACE, f"{normalized}:{logical_id.value}"))

    @classmethod
    def parse(cls, value: str | UUID) -> DocumentId:
        return cls(value)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class DocumentIdentity(DocumentModel):
    logical_id: DocumentId
    document_id: DocumentId
    knowledge_object_id: KnowledgeObjectId
    namespace: str
    physical_ids: tuple[str, ...] = ()
    external_ids: Mapping[str, str] = field(default_factory=dict)
    schema_version: str = DOCUMENT_SCHEMA_VERSION
    discriminator: ClassVar[str] = "document_identity"

    def __post_init__(self) -> None:
        if not isinstance(self.logical_id, DocumentId) or not isinstance(self.document_id, DocumentId):
            raise DocumentValidationError("logical_id and document_id must be DocumentId")
        if not isinstance(self.knowledge_object_id, KnowledgeObjectId):
            raise DocumentValidationError("knowledge_object_id must be KnowledgeObjectId")
        object.__setattr__(self, "namespace", text(self.namespace, "namespace"))
        if self.document_id != DocumentId.canonical(self.namespace, self.logical_id):
            raise DocumentValidationError("document_id does not match logical identity")
        if str(self.knowledge_object_id) != str(self.logical_id):
            raise DocumentValidationError("knowledge_object_id must specialize logical_id")
        object.__setattr__(self, "physical_ids", unique_texts(self.physical_ids, "physical_ids"))
        if not isinstance(self.external_ids, Mapping):
            raise DocumentValidationError("external_ids must be a mapping")
        frozen = deep_freeze(self.external_ids)
        assert isinstance(frozen, MappingProxyType)
        if any(not isinstance(value, str) or not value.strip() for value in frozen.values()):
            raise DocumentValidationError("external identity values must be non-empty strings")
        object.__setattr__(self, "external_ids", frozen)
        self._validate_schema()


__all__ = ["DocumentId", "DocumentIdentity"]
