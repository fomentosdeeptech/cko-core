"""Immutable provenance qualifier and aggregate models."""

from __future__ import annotations

from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import ClassVar

from .constants import (
    PROVENANCE_SCHEMA_VERSION,
    PROVENANCE_SERIALIZATION_VERSION,
    PROVENANCE_VERSION,
)
from .contracts import (
    CanonicalValue,
    canonical_json,
    canonical_primitive,
    canonical_value,
    instant,
    model_tuple,
    require_versions,
    sha256,
    text,
    unique,
)
from .enums import ProvenanceStatementCategory
from .identity import ProvenanceStatementIdentity
from .references import (
    ProvenanceActivityRef,
    ProvenanceActorRef,
    ProvenanceEntityRef,
    ProvenanceEvidenceRef,
    ProvenanceStatementRef,
    ProvenanceSubjectRef,
)
from .versioning import ProvenanceStatementVersion


_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceQualifier:
    name: str
    value: CanonicalValue
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_qualifier"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", text(self.name, "name", self.model))
        object.__setattr__(self, "value", canonical_value(self.value, "value", self.model))
        require_versions(self.schema_version, self.serialization_version, self.model)

    @property
    def sort_value(self) -> str:
        return canonical_json(canonical_primitive(self.value)).decode("utf-8")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceStatement:
    identity: ProvenanceStatementIdentity
    category: ProvenanceStatementCategory
    subject: ProvenanceSubjectRef
    version: ProvenanceStatementVersion
    digest: str
    entities: tuple[ProvenanceEntityRef, ...] = ()
    actors: tuple[ProvenanceActorRef, ...] = ()
    activity: ProvenanceActivityRef | None = None
    evidence: tuple[ProvenanceEvidenceRef, ...] = ()
    predecessors: tuple[ProvenanceStatementRef, ...] = ()
    qualifiers: tuple[ProvenanceQualifier, ...] = ()
    declared_at: datetime | None = None
    foundation_version: str = PROVENANCE_VERSION
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    _factory_token: InitVar[object | None] = None
    model: ClassVar[str] = "provenance_statement"

    def __post_init__(self, _factory_token: object | None) -> None:
        from .contracts import enum_value, semver, validation
        from .errors import ProvenanceFactoryError

        if _factory_token is not _FACTORY_TOKEN:
            raise ProvenanceFactoryError("PF001", self.model, "construction", "must be created by factory")
        if not isinstance(self.identity, ProvenanceStatementIdentity):
            raise validation("PV001", self.model, "identity", "must be ProvenanceStatementIdentity")
        object.__setattr__(self, "category", enum_value(
            self.category, ProvenanceStatementCategory, "category", self.model,
        ))
        if not isinstance(self.subject, ProvenanceSubjectRef):
            raise validation("PV001", self.model, "subject", "must be ProvenanceSubjectRef")
        if not isinstance(self.version, ProvenanceStatementVersion):
            raise validation("PV001", self.model, "version", "must be ProvenanceStatementVersion")
        object.__setattr__(self, "digest", sha256(self.digest, "digest", self.model))
        collections = (
            ("entities", ProvenanceEntityRef, lambda item: (
                item.role.value, item.target_type.value, item.namespace, item.target_id,
                item.target_version or "", item.target_digest or "",
            )),
            ("actors", ProvenanceActorRef, lambda item: (
                item.role.value, item.actor_type.value, item.namespace, item.actor_id,
                item.actor_version or "", item.actor_digest or "",
            )),
            ("evidence", ProvenanceEvidenceRef, lambda item: (
                item.evidence_type.value, item.namespace, item.evidence_id,
                item.evidence_version or "", item.evidence_digest or "",
            )),
            ("predecessors", ProvenanceStatementRef, lambda item: (
                str(item.statement_id), item.statement_version, item.digest,
            )),
            ("qualifiers", ProvenanceQualifier, lambda item: (item.name, item.sort_value)),
        )
        for field, expected, key in collections:
            normalized = model_tuple(getattr(self, field), expected, field, self.model, sort_key=key)
            unique(normalized, key, field, self.model)
            object.__setattr__(self, field, normalized)
        if self.activity is not None and not isinstance(self.activity, ProvenanceActivityRef):
            raise validation("PV001", self.model, "activity", "must be ProvenanceActivityRef")
        object.__setattr__(self, "declared_at", instant(
            self.declared_at, "declared_at", self.model, optional=True,
        ))
        object.__setattr__(self, "foundation_version", semver(
            self.foundation_version, "foundation_version", self.model,
        ))
        if self.foundation_version != PROVENANCE_VERSION:
            raise validation("PV005", self.model, "foundation_version", "unsupported foundation version")
        require_versions(self.schema_version, self.serialization_version, self.model)

    @property
    def node_key(self) -> str:
        return f"{self.identity.statement_id}@{self.version.revision}"


__all__ = ["ProvenanceQualifier", "ProvenanceStatement"]
