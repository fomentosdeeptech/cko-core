"""Canonical immutable relationship models and aggregate."""

from __future__ import annotations

from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from .contracts import (
    RELATIONSHIP_SCHEMA_VERSION, RelationshipModel, instant, model_sequence,
    non_negative, text, version,
)
from .enums import RelationshipStatus, RelationshipStrength, RelationshipType
from .errors import RelationshipFactoryError, RelationshipValidationError
from .identity import RelationshipEndpoint, RelationshipId, RelationshipIdentity
from .metadata import (
    RelationshipConstraint, RelationshipDirection, RelationshipEvidence,
    RelationshipMetadata, RelationshipWeight,
)


_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True)
class RelationshipVersion(RelationshipModel):
    version_id: UUID
    version: str
    created_at: datetime
    created_by: str
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    parent_version: UUID | None = None
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_version"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "version_id", self.version_id if isinstance(self.version_id, UUID) else UUID(str(self.version_id)))
            if self.parent_version is not None:
                object.__setattr__(self, "parent_version", self.parent_version if isinstance(self.parent_version, UUID) else UUID(str(self.parent_version)))
        except (TypeError, ValueError, AttributeError) as error:
            raise RelationshipValidationError("version identifiers must be UUID values") from error
        if self.parent_version == self.version_id:
            raise RelationshipValidationError("version cannot be its own parent")
        object.__setattr__(self, "version", version(self.version))
        object.__setattr__(self, "created_at", instant(self.created_at, "created_at"))
        object.__setattr__(self, "created_by", text(self.created_by, "created_by"))
        try:
            object.__setattr__(self, "status", RelationshipStatus(self.status))
        except (TypeError, ValueError) as error:
            raise RelationshipValidationError("status must be RelationshipStatus") from error
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class RelationshipDescriptor(RelationshipModel):
    relationship_type: RelationshipType
    direction: RelationshipDirection
    constraint: RelationshipConstraint
    strength: RelationshipStrength = RelationshipStrength.UNKNOWN
    label: str | None = None
    description: str | None = None
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_descriptor"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "relationship_type", RelationshipType(self.relationship_type))
            object.__setattr__(self, "strength", RelationshipStrength(self.strength))
        except (TypeError, ValueError) as error:
            raise RelationshipValidationError("invalid relationship descriptor enum") from error
        if not isinstance(self.direction, RelationshipDirection):
            raise RelationshipValidationError("direction must be RelationshipDirection")
        if not isinstance(self.constraint, RelationshipConstraint):
            raise RelationshipValidationError("constraint must be RelationshipConstraint")
        object.__setattr__(self, "label", text(self.label, "label", optional=True))
        object.__setattr__(self, "description", text(self.description, "description", optional=True))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CanonicalRelationship(RelationshipModel):
    identity: RelationshipIdentity
    metadata: RelationshipMetadata
    source: RelationshipEndpoint
    target: RelationshipEndpoint
    descriptor: RelationshipDescriptor
    version: RelationshipVersion
    evidence: tuple[RelationshipEvidence, ...] = ()
    weights: tuple[RelationshipWeight, ...] = ()
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "canonical_relationship"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise RelationshipFactoryError("CanonicalRelationship must be created by RelationshipFactory")
        required = (
            (self.identity, RelationshipIdentity),
            (self.metadata, RelationshipMetadata),
            (self.source, RelationshipEndpoint),
            (self.target, RelationshipEndpoint),
            (self.descriptor, RelationshipDescriptor),
            (self.version, RelationshipVersion),
        )
        if any(not isinstance(value, expected) for value, expected in required):
            raise RelationshipValidationError("canonical relationship contains an invalid required model")
        object.__setattr__(self, "evidence", model_sequence(self.evidence, "evidence", RelationshipEvidence))
        object.__setattr__(self, "weights", model_sequence(self.weights, "weights", RelationshipWeight))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class RelationshipCollection(RelationshipModel):
    relationships: tuple[CanonicalRelationship, ...] = ()
    name: str | None = None
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "relationship_collection"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise RelationshipFactoryError("RelationshipCollection must be created by RelationshipFactory")
        object.__setattr__(self, "relationships", model_sequence(self.relationships, "relationships", CanonicalRelationship))
        object.__setattr__(self, "name", text(self.name, "name", optional=True))
        identifiers = tuple(item.identity.canonical_id for item in self.relationships)
        if len(identifiers) != len(set(identifiers)):
            raise RelationshipValidationError("collection relationships must be unique")
        self._validate_schema()

    def __iter__(self):
        return iter(self.relationships)

    def __len__(self) -> int:
        return len(self.relationships)


@dataclass(frozen=True, slots=True)
class RelationshipQuery(RelationshipModel):
    relationship_ids: tuple[RelationshipId, ...] = ()
    source_ids: tuple[UUID, ...] = ()
    target_ids: tuple[UUID, ...] = ()
    relationship_types: tuple[RelationshipType, ...] = ()
    statuses: tuple[RelationshipStatus, ...] = ()
    namespace: str | None = None
    limit: int = 100
    offset: int = 0
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_query"

    def __post_init__(self) -> None:
        object.__setattr__(self, "relationship_ids", model_sequence(self.relationship_ids, "relationship_ids", RelationshipId))
        for name in ("source_ids", "target_ids"):
            values = tuple(getattr(self, name)) if isinstance(getattr(self, name), (tuple, list)) else None
            if values is None:
                raise RelationshipValidationError(f"{name} must be a sequence")
            try:
                normalized = tuple(item if isinstance(item, UUID) else UUID(str(item)) for item in values)
            except (TypeError, ValueError, AttributeError) as error:
                raise RelationshipValidationError(f"{name} must contain UUID values") from error
            if len(normalized) != len(set(normalized)):
                raise RelationshipValidationError(f"{name} must not contain duplicates")
            object.__setattr__(self, name, normalized)
        try:
            object.__setattr__(self, "relationship_types", tuple(RelationshipType(item) for item in self.relationship_types))
            object.__setattr__(self, "statuses", tuple(RelationshipStatus(item) for item in self.statuses))
        except (TypeError, ValueError) as error:
            raise RelationshipValidationError("query contains an invalid enum") from error
        object.__setattr__(self, "namespace", text(self.namespace, "namespace", optional=True))
        object.__setattr__(self, "limit", non_negative(self.limit, "limit"))
        object.__setattr__(self, "offset", non_negative(self.offset, "offset"))
        if self.limit == 0:
            raise RelationshipValidationError("limit must be greater than zero")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class RelationshipResult(RelationshipModel):
    query: RelationshipQuery
    relationships: tuple[CanonicalRelationship, ...]
    total: int
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_result"

    def __post_init__(self) -> None:
        if not isinstance(self.query, RelationshipQuery):
            raise RelationshipValidationError("query must be RelationshipQuery")
        object.__setattr__(self, "relationships", model_sequence(self.relationships, "relationships", CanonicalRelationship))
        object.__setattr__(self, "total", non_negative(self.total, "total"))
        if self.total < len(self.relationships):
            raise RelationshipValidationError("total cannot be smaller than the result page")
        self._validate_schema()


__all__ = [
    "CanonicalRelationship", "RelationshipCollection", "RelationshipDescriptor",
    "RelationshipQuery", "RelationshipResult", "RelationshipVersion", "_FACTORY_TOKEN",
]
