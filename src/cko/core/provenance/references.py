"""Opaque, typed references used by provenance statements."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from urllib.parse import urlsplit
from uuid import UUID

from .constants import PROVENANCE_SCHEMA_VERSION, PROVENANCE_SERIALIZATION_VERSION
from .contracts import (
    enum_value,
    instant,
    model_tuple,
    require_versions,
    semver,
    sha256,
    text,
    unique,
)
from .enums import (
    ProvenanceActivityType,
    ProvenanceActorRole,
    ProvenanceActorType,
    ProvenanceEntityRole,
    ProvenanceEvidenceType,
    ProvenanceTargetType,
)
from .identity import ProvenanceStatementId


def _target_id(value: object, target_type: ProvenanceTargetType, field: str, model: str) -> str:
    normalized = text(value, field, model)
    if target_type is ProvenanceTargetType.EXTERNAL_RESOURCE:
        parsed = urlsplit(normalized)
        if not parsed.scheme:
            from .contracts import validation
            raise validation("PV005", model, field, "external resource must be an absolute URI")
        return normalized
    try:
        return str(UUID(normalized))
    except (ValueError, TypeError, AttributeError) as error:
        from .contracts import validation
        raise validation("PV005", model, field, "CORE target ID must be canonical UUID") from error


def _optional_uuid_text(value: object, field: str, model: str) -> str | None:
    if value is None:
        return None
    normalized = text(value, field, model)
    try:
        return str(UUID(normalized))
    except (ValueError, TypeError, AttributeError) as error:
        from .contracts import validation
        raise validation("PV005", model, field, "must be canonical UUID") from error


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceSubjectRef:
    target_type: ProvenanceTargetType
    namespace: str
    target_id: str
    target_canonical_id: str | None = None
    target_external_id: str | None = None
    target_version: str | None = None
    target_digest: str | None = None
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_subject_ref"

    def __post_init__(self) -> None:
        object.__setattr__(self, "target_type", enum_value(
            self.target_type, ProvenanceTargetType, "target_type", self.model,
        ))
        object.__setattr__(self, "namespace", text(self.namespace, "namespace", self.model))
        object.__setattr__(self, "target_id", _target_id(
            self.target_id, self.target_type, "target_id", self.model,
        ))
        object.__setattr__(self, "target_canonical_id", _optional_uuid_text(
            self.target_canonical_id, "target_canonical_id", self.model,
        ))
        object.__setattr__(self, "target_external_id", text(
            self.target_external_id, "target_external_id", self.model, optional=True,
        ))
        if self.target_version is not None:
            object.__setattr__(self, "target_version", semver(
                self.target_version, "target_version", self.model,
            ))
        if self.target_digest is not None:
            object.__setattr__(self, "target_digest", sha256(
                self.target_digest, "target_digest", self.model,
            ))
        require_versions(self.schema_version, self.serialization_version, self.model)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceEntityRef:
    target_type: ProvenanceTargetType
    namespace: str
    target_id: str
    role: ProvenanceEntityRole
    target_canonical_id: str | None = None
    target_external_id: str | None = None
    target_version: str | None = None
    target_digest: str | None = None
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_entity_ref"

    def __post_init__(self) -> None:
        object.__setattr__(self, "target_type", enum_value(
            self.target_type, ProvenanceTargetType, "target_type", self.model,
        ))
        object.__setattr__(self, "role", enum_value(self.role, ProvenanceEntityRole, "role", self.model))
        object.__setattr__(self, "namespace", text(self.namespace, "namespace", self.model))
        object.__setattr__(self, "target_id", _target_id(
            self.target_id, self.target_type, "target_id", self.model,
        ))
        object.__setattr__(self, "target_canonical_id", _optional_uuid_text(
            self.target_canonical_id, "target_canonical_id", self.model,
        ))
        object.__setattr__(self, "target_external_id", text(
            self.target_external_id, "target_external_id", self.model, optional=True,
        ))
        if self.target_version is not None:
            object.__setattr__(self, "target_version", semver(
                self.target_version, "target_version", self.model,
            ))
        if self.target_digest is not None:
            object.__setattr__(self, "target_digest", sha256(
                self.target_digest, "target_digest", self.model,
            ))
        require_versions(self.schema_version, self.serialization_version, self.model)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceActorRef:
    actor_type: ProvenanceActorType
    namespace: str
    actor_id: str
    role: ProvenanceActorRole
    actor_version: str | None = None
    actor_digest: str | None = None
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_actor_ref"

    def __post_init__(self) -> None:
        object.__setattr__(self, "actor_type", enum_value(
            self.actor_type, ProvenanceActorType, "actor_type", self.model,
        ))
        object.__setattr__(self, "role", enum_value(self.role, ProvenanceActorRole, "role", self.model))
        object.__setattr__(self, "namespace", text(self.namespace, "namespace", self.model))
        object.__setattr__(self, "actor_id", text(self.actor_id, "actor_id", self.model))
        if self.actor_version is not None:
            object.__setattr__(self, "actor_version", semver(
                self.actor_version, "actor_version", self.model,
            ))
        if self.actor_digest is not None:
            object.__setattr__(self, "actor_digest", sha256(
                self.actor_digest, "actor_digest", self.model,
            ))
        require_versions(self.schema_version, self.serialization_version, self.model)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceActivityRef:
    activity_type: ProvenanceActivityType
    namespace: str
    activity_id: str
    label: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    qualifiers: tuple["ProvenanceQualifier", ...] = ()
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_activity_ref"

    def __post_init__(self) -> None:
        from .models import ProvenanceQualifier
        from .contracts import validation

        object.__setattr__(self, "activity_type", enum_value(
            self.activity_type, ProvenanceActivityType, "activity_type", self.model,
        ))
        object.__setattr__(self, "namespace", text(self.namespace, "namespace", self.model))
        object.__setattr__(self, "activity_id", text(self.activity_id, "activity_id", self.model))
        object.__setattr__(self, "label", text(self.label, "label", self.model, optional=True))
        object.__setattr__(self, "started_at", instant(
            self.started_at, "started_at", self.model, optional=True,
        ))
        object.__setattr__(self, "ended_at", instant(
            self.ended_at, "ended_at", self.model, optional=True,
        ))
        qualifiers = model_tuple(
            self.qualifiers, ProvenanceQualifier, "qualifiers", self.model,
            sort_key=lambda item: (item.name, item.sort_value),
        )
        unique(qualifiers, lambda item: item.name, "qualifiers", self.model)
        object.__setattr__(self, "qualifiers", qualifiers)
        if self.started_at is not None and self.ended_at is not None and self.ended_at < self.started_at:
            raise validation("PV006", self.model, "ended_at", "cannot precede started_at")
        if self.activity_type is ProvenanceActivityType.OTHER_DECLARED:
            if self.label is None or "vocabulary" not in {item.name for item in qualifiers}:
                raise validation("PV005", self.model, "activity_type", "other_declared requires label and vocabulary")
        require_versions(self.schema_version, self.serialization_version, self.model)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceEvidenceRef:
    evidence_type: ProvenanceEvidenceType
    namespace: str
    evidence_id: str
    evidence_version: str | None = None
    evidence_digest: str | None = None
    qualifiers: tuple["ProvenanceQualifier", ...] = ()
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_evidence_ref"

    def __post_init__(self) -> None:
        from .models import ProvenanceQualifier

        object.__setattr__(self, "evidence_type", enum_value(
            self.evidence_type, ProvenanceEvidenceType, "evidence_type", self.model,
        ))
        object.__setattr__(self, "namespace", text(self.namespace, "namespace", self.model))
        object.__setattr__(self, "evidence_id", text(self.evidence_id, "evidence_id", self.model))
        if self.evidence_version is not None:
            object.__setattr__(self, "evidence_version", semver(
                self.evidence_version, "evidence_version", self.model,
            ))
        if self.evidence_digest is not None:
            object.__setattr__(self, "evidence_digest", sha256(
                self.evidence_digest, "evidence_digest", self.model,
            ))
        qualifiers = model_tuple(
            self.qualifiers, ProvenanceQualifier, "qualifiers", self.model,
            sort_key=lambda item: (item.name, item.sort_value),
        )
        unique(qualifiers, lambda item: item.name, "qualifiers", self.model)
        object.__setattr__(self, "qualifiers", qualifiers)
        require_versions(self.schema_version, self.serialization_version, self.model)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceStatementRef:
    statement_id: ProvenanceStatementId
    revision: int
    statement_version: str
    digest: str
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_statement_ref"

    def __post_init__(self) -> None:
        from .contracts import positive_int, validation

        if not isinstance(self.statement_id, ProvenanceStatementId):
            raise validation("PV001", self.model, "statement_id", "must be ProvenanceStatementId")
        object.__setattr__(self, "revision", positive_int(self.revision, "revision", self.model))
        object.__setattr__(self, "statement_version", semver(
            self.statement_version, "statement_version", self.model,
        ))
        expected = f"1.0.{self.revision - 1}"
        if self.statement_version != expected:
            from .errors import ProvenanceVersionError
            raise ProvenanceVersionError("PR001", self.model, "statement_version", f"must be {expected}")
        object.__setattr__(self, "digest", sha256(self.digest, "digest", self.model))
        require_versions(self.schema_version, self.serialization_version, self.model)

    @property
    def node_key(self) -> str:
        return f"{self.statement_id}@{self.revision}"


__all__ = [
    "ProvenanceActivityRef",
    "ProvenanceActorRef",
    "ProvenanceEntityRef",
    "ProvenanceEvidenceRef",
    "ProvenanceStatementRef",
    "ProvenanceSubjectRef",
]
