"""Technology-neutral canonical relationship identities and endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID, uuid4, uuid5

from .contracts import RELATIONSHIP_SCHEMA_VERSION, RelationshipModel, text, version
from .errors import RelationshipIdentityError, RelationshipValidationError


_RELATIONSHIP_UUID_NAMESPACE = UUID("a899f825-bd53-4e68-b9d2-1e2597f2fc75")


@dataclass(frozen=True, order=True, slots=True)
class RelationshipId(RelationshipModel):
    value: UUID
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_id"

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            try:
                object.__setattr__(self, "value", UUID(str(self.value)))
            except (TypeError, ValueError, AttributeError) as error:
                raise RelationshipIdentityError("value must be a UUID") from error
        self._validate_schema()

    @classmethod
    def new(cls) -> RelationshipId:
        return cls(uuid4())

    @classmethod
    def canonical(cls, namespace: str, semantic_key: str) -> RelationshipId:
        normalized_namespace = text(namespace, "namespace")
        normalized_key = text(semantic_key, "semantic_key")
        return cls(uuid5(_RELATIONSHIP_UUID_NAMESPACE, f"{normalized_namespace}:{normalized_key}"))

    @classmethod
    def parse(cls, value: str | UUID) -> RelationshipId:
        try:
            return cls(value if isinstance(value, UUID) else UUID(value))
        except (TypeError, ValueError, AttributeError) as error:
            raise RelationshipIdentityError("value must be a UUID") from error

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class RelationshipIdentity(RelationshipModel):
    logical_id: RelationshipId
    canonical_id: RelationshipId
    namespace: str
    semantic_key: str
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_identity"

    def __post_init__(self) -> None:
        if not isinstance(self.logical_id, RelationshipId) or not isinstance(self.canonical_id, RelationshipId):
            raise RelationshipIdentityError("logical_id and canonical_id must be RelationshipId")
        object.__setattr__(self, "namespace", text(self.namespace, "namespace"))
        object.__setattr__(self, "semantic_key", text(self.semantic_key, "semantic_key"))
        if self.canonical_id != RelationshipId.canonical(self.namespace, self.semantic_key):
            raise RelationshipIdentityError("canonical_id does not match namespace and semantic_key")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class RelationshipEndpoint(RelationshipModel):
    object_id: UUID
    namespace: str
    entity_type: str
    version: str
    canonical_id: UUID | None = None
    external_id: str | None = None
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_endpoint"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "object_id", self.object_id if isinstance(self.object_id, UUID) else UUID(str(self.object_id)))
            if self.canonical_id is not None:
                object.__setattr__(self, "canonical_id", self.canonical_id if isinstance(self.canonical_id, UUID) else UUID(str(self.canonical_id)))
        except (TypeError, ValueError, AttributeError) as error:
            raise RelationshipIdentityError("endpoint identifiers must be UUID values") from error
        object.__setattr__(self, "namespace", text(self.namespace, "namespace"))
        object.__setattr__(self, "entity_type", text(self.entity_type, "entity_type"))
        object.__setattr__(self, "version", version(self.version))
        object.__setattr__(self, "external_id", text(self.external_id, "external_id", optional=True))
        self._validate_schema()

    @classmethod
    def from_knowledge_object(cls, value: object) -> RelationshipEndpoint:
        from cko.core.knowledge import KnowledgeObject

        if not isinstance(value, KnowledgeObject):
            raise RelationshipIdentityError("value must be a compatible KnowledgeObject")
        try:
            identity = value.identity
            return cls(
                identity.logical_id.value,
                identity.namespace,
                "knowledge_object",
                identity.version,
                identity.canonical_id.value,
                identity.external_id,
            )
        except (AttributeError, TypeError, RelationshipValidationError) as error:
            raise RelationshipIdentityError("value must be a compatible KnowledgeObject") from error

    @classmethod
    def from_document(cls, value: object) -> RelationshipEndpoint:
        from cko.core.documents import CanonicalDocument

        if not isinstance(value, CanonicalDocument):
            raise RelationshipIdentityError("value must be a compatible CanonicalDocument")
        try:
            identity = value.identity
            model_version = value.metadata.version
            external_id = next(iter(identity.external_ids.values()), None)
            return cls(
                identity.logical_id.value,
                identity.namespace,
                "canonical_document",
                model_version,
                identity.document_id.value,
                external_id,
            )
        except (AttributeError, TypeError, RelationshipValidationError) as error:
            raise RelationshipIdentityError("value must be a compatible CanonicalDocument") from error


__all__ = ["RelationshipEndpoint", "RelationshipId", "RelationshipIdentity"]
