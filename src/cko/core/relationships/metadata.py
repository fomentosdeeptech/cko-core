"""Immutable metadata, evidence, weights, and declarative constraints."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Mapping

from .contracts import (
    RELATIONSHIP_SCHEMA_VERSION, RelationshipModel, deep_freeze, instant,
    probability, text, version,
)
from .enums import (
    RelationshipDirectionType, RelationshipEvidenceType, RelationshipStatus,
)
from .errors import (
    RelationshipConstraintError, RelationshipEvidenceError,
    RelationshipValidationError,
)


@dataclass(frozen=True, slots=True)
class RelationshipMetadata(RelationshipModel):
    created_at: datetime
    modified_at: datetime
    created_by: str
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    source: str | None = None
    attributes: Mapping[str, object] = ()
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_metadata"

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", instant(self.created_at, "created_at"))
        object.__setattr__(self, "modified_at", instant(self.modified_at, "modified_at"))
        object.__setattr__(self, "created_by", text(self.created_by, "created_by"))
        object.__setattr__(self, "source", text(self.source, "source", optional=True))
        try:
            object.__setattr__(self, "status", RelationshipStatus(self.status))
        except (TypeError, ValueError) as error:
            raise RelationshipValidationError("status must be RelationshipStatus") from error
        if self.modified_at < self.created_at:
            raise RelationshipValidationError("modified_at cannot precede created_at")
        if self.attributes == ():
            object.__setattr__(self, "attributes", {})
        if not isinstance(self.attributes, Mapping):
            raise RelationshipValidationError("attributes must be a mapping")
        object.__setattr__(self, "attributes", deep_freeze(self.attributes))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class RelationshipDirection(RelationshipModel):
    direction: RelationshipDirectionType = RelationshipDirectionType.DIRECTED
    source_role: str = "source"
    target_role: str = "target"
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_direction"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "direction", RelationshipDirectionType(self.direction))
        except (TypeError, ValueError) as error:
            raise RelationshipValidationError("direction must be RelationshipDirectionType") from error
        object.__setattr__(self, "source_role", text(self.source_role, "source_role"))
        object.__setattr__(self, "target_role", text(self.target_role, "target_role"))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class RelationshipConstraint(RelationshipModel):
    unique: bool = True
    multiplicity: str = "many_to_many"
    bidirectional: bool = False
    transitive: bool = False
    symmetric: bool = False
    reflexive: bool = False
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_constraint"

    def __post_init__(self) -> None:
        for name in ("unique", "bidirectional", "transitive", "symmetric", "reflexive"):
            if not isinstance(getattr(self, name), bool):
                raise RelationshipConstraintError(f"{name} must be boolean")
        normalized = text(self.multiplicity, "multiplicity")
        if normalized not in {"one_to_one", "one_to_many", "many_to_one", "many_to_many"}:
            raise RelationshipConstraintError("multiplicity is not supported")
        object.__setattr__(self, "multiplicity", normalized)
        if self.symmetric and not self.bidirectional:
            raise RelationshipConstraintError("symmetric relationships must be bidirectional")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class RelationshipEvidence(RelationshipModel):
    evidence_type: RelationshipEvidenceType
    source: str | None = None
    evidence: str | None = None
    generating_algorithm: str | None = None
    confidence: float | None = None
    timestamp: datetime | None = None
    author: str | None = None
    pipeline: str | None = None
    version: str | None = None
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_evidence"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "evidence_type", RelationshipEvidenceType(self.evidence_type))
        except (TypeError, ValueError) as error:
            raise RelationshipEvidenceError("evidence_type must be RelationshipEvidenceType") from error
        for name in ("source", "evidence", "generating_algorithm", "author", "pipeline"):
            object.__setattr__(self, name, text(getattr(self, name), name, optional=True))
        object.__setattr__(self, "confidence", probability(self.confidence, "confidence"))
        object.__setattr__(self, "timestamp", instant(self.timestamp, "timestamp", optional=True))
        if self.version is not None:
            object.__setattr__(self, "version", version(self.version))
        if all(getattr(self, name) is None for name in ("source", "evidence", "generating_algorithm", "author", "pipeline")):
            raise RelationshipEvidenceError("evidence must declare at least one origin detail")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class RelationshipWeight(RelationshipModel):
    weight: float | None = None
    confidence: float | None = None
    relevance: float | None = None
    probability: float | None = None
    schema_version: str = RELATIONSHIP_SCHEMA_VERSION
    discriminator: ClassVar[str] = "relationship_weight"

    def __post_init__(self) -> None:
        for name in ("weight", "confidence", "relevance", "probability"):
            object.__setattr__(self, name, probability(getattr(self, name), name))
        self._validate_schema()


__all__ = [
    "RelationshipConstraint", "RelationshipDirection", "RelationshipEvidence",
    "RelationshipMetadata", "RelationshipWeight",
]
