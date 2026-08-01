"""Canonical identity models for Knowledge Objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID, uuid4, uuid5

from .contracts import KNOWLEDGE_SCHEMA_VERSION, SerializableKnowledgeModel, primitive, require_text
from .enums import KnowledgeType
from .errors import KnowledgeValidationError


_KNOWLEDGE_UUID_NAMESPACE = UUID("9a6c67c6-bbdd-4f05-aef5-2d9a279eeed6")


@dataclass(frozen=True, order=True, slots=True)
class KnowledgeObjectId(SerializableKnowledgeModel):
    value: UUID
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_object_id"

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            try:
                object.__setattr__(self, "value", UUID(str(self.value)))
            except (TypeError, ValueError, AttributeError) as error:
                raise KnowledgeValidationError("value must be a UUID") from error
        self._validate_schema()

    @classmethod
    def new(cls) -> KnowledgeObjectId:
        return cls(uuid4())

    @classmethod
    def canonical(cls, namespace: str, logical_id: KnowledgeObjectId) -> KnowledgeObjectId:
        normalized = require_text(namespace, "namespace")
        if not isinstance(logical_id, KnowledgeObjectId):
            raise KnowledgeValidationError("logical_id must be KnowledgeObjectId")
        return cls(uuid5(_KNOWLEDGE_UUID_NAMESPACE, f"{normalized}:{logical_id.value}"))

    @classmethod
    def parse(cls, value: str | UUID) -> KnowledgeObjectId:
        return cls(value if isinstance(value, UUID) else UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "value": str(self.value)}


@dataclass(frozen=True, slots=True)
class KnowledgeObjectIdentity(SerializableKnowledgeModel):
    logical_id: KnowledgeObjectId
    canonical_id: KnowledgeObjectId
    origin: str
    namespace: str
    knowledge_type: KnowledgeType
    version: str
    external_id: str | None = None
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_object_identity"

    def __post_init__(self) -> None:
        if not isinstance(self.logical_id, KnowledgeObjectId) or not isinstance(self.canonical_id, KnowledgeObjectId):
            raise KnowledgeValidationError("logical_id and canonical_id must be KnowledgeObjectId")
        for name in ("origin", "namespace", "version"):
            object.__setattr__(self, name, require_text(getattr(self, name), name))
        object.__setattr__(self, "external_id", require_text(self.external_id, "external_id", optional=True))
        try:
            object.__setattr__(self, "knowledge_type", KnowledgeType(self.knowledge_type))
        except (TypeError, ValueError) as error:
            raise KnowledgeValidationError("knowledge_type must be KnowledgeType") from error
        expected = KnowledgeObjectId.canonical(self.namespace, self.logical_id)
        if self.canonical_id != expected:
            raise KnowledgeValidationError("canonical_id does not match namespace and logical_id")
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model,
                "logical_id": primitive(self.logical_id), "canonical_id": primitive(self.canonical_id),
                "external_id": self.external_id, "origin": self.origin, "namespace": self.namespace,
                "knowledge_type": self.knowledge_type.value, "version": self.version}


__all__ = ["KnowledgeObjectId", "KnowledgeObjectIdentity"]
