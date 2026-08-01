"""Declarative relationship model; this module does not implement a graph."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from .contracts import (KNOWLEDGE_SCHEMA_VERSION, SerializableKnowledgeModel, model_sequence,
                        primitive, require_instant, require_probability)
from .enums import RelationshipType
from .errors import KnowledgeRelationshipError
from .identity import KnowledgeObjectId
from .metadata import KnowledgeAttribute


@dataclass(frozen=True, slots=True)
class KnowledgeRelationship(SerializableKnowledgeModel):
    relationship_id: UUID
    source_id: KnowledgeObjectId
    target_id: KnowledgeObjectId
    relationship_type: RelationshipType
    created_at: datetime
    confidence: float | None = None
    attributes: tuple[KnowledgeAttribute, ...] = ()
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_relationship"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "relationship_id", self.relationship_id if isinstance(self.relationship_id, UUID) else UUID(str(self.relationship_id)))
        except (TypeError, ValueError, AttributeError) as error:
            raise KnowledgeRelationshipError("relationship_id must be UUID") from error
        if not isinstance(self.source_id, KnowledgeObjectId) or not isinstance(self.target_id, KnowledgeObjectId):
            raise KnowledgeRelationshipError("source_id and target_id must be KnowledgeObjectId")
        if self.source_id == self.target_id:
            raise KnowledgeRelationshipError("self relationships are invalid")
        try:
            object.__setattr__(self, "relationship_type", RelationshipType(self.relationship_type))
        except (TypeError, ValueError) as error:
            raise KnowledgeRelationshipError("relationship_type must be RelationshipType") from error
        object.__setattr__(self, "created_at", require_instant(self.created_at, "created_at"))
        object.__setattr__(self, "confidence", require_probability(self.confidence, "confidence"))
        object.__setattr__(self, "attributes", model_sequence(self.attributes, "attributes", KnowledgeAttribute))
        self._validate_schema()

    @classmethod
    def create(cls, source_id: KnowledgeObjectId, target_id: KnowledgeObjectId,
               relationship_type: RelationshipType, created_at: datetime,
               confidence: float | None = None,
               attributes: tuple[KnowledgeAttribute, ...] = ()) -> KnowledgeRelationship:
        return cls(uuid4(), source_id, target_id, relationship_type, created_at, confidence, attributes)

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model,
                "relationship_id": str(self.relationship_id), "source_id": primitive(self.source_id),
                "target_id": primitive(self.target_id), "relationship_type": self.relationship_type.value,
                "created_at": self.created_at.isoformat(), "confidence": self.confidence,
                "attributes": primitive(self.attributes)}


__all__ = ["KnowledgeRelationship"]
