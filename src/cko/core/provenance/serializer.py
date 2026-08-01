"""Closed deterministic UTF-8 JSON serialization for provenance models."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Mapping
from uuid import UUID

from .constants import PROVENANCE_SCHEMA_VERSION, PROVENANCE_SERIALIZATION_VERSION
from .contracts import (
    CanonicalJSON,
    canonical_json,
    canonical_primitive,
    instant_text,
    parse_instant,
)
from .enums import (
    ProvenanceActivityType,
    ProvenanceActorRole,
    ProvenanceActorType,
    ProvenanceEntityRole,
    ProvenanceEvidenceType,
    ProvenanceStatementCategory,
    ProvenanceTargetType,
)
from .errors import (
    ProvenanceError,
    ProvenanceSerializationError,
)
from .identity import ProvenanceStatementId, ProvenanceStatementIdentity
from .models import ProvenanceQualifier, ProvenanceStatement
from .references import (
    ProvenanceActivityRef,
    ProvenanceActorRef,
    ProvenanceEntityRef,
    ProvenanceEvidenceRef,
    ProvenanceStatementRef,
    ProvenanceSubjectRef,
)
from .results import ProvenanceChainValidationResult, ProvenanceStatementComparisonResult
from .versioning import ProvenanceStatementVersion


_MODEL_FIELDS = {
    "provenance_statement_id": {"value"},
    "provenance_statement_identity": {"statement_id", "business_namespace", "lineage_key"},
    "provenance_qualifier": {"name", "value"},
    "provenance_subject_ref": {"target_type", "namespace", "target_id", "target_canonical_id", "target_external_id", "target_version", "target_digest"},
    "provenance_entity_ref": {"target_type", "namespace", "target_id", "role", "target_canonical_id", "target_external_id", "target_version", "target_digest"},
    "provenance_actor_ref": {"actor_type", "namespace", "actor_id", "role", "actor_version", "actor_digest"},
    "provenance_activity_ref": {"activity_type", "namespace", "activity_id", "label", "started_at", "ended_at", "qualifiers"},
    "provenance_evidence_ref": {"evidence_type", "namespace", "evidence_id", "evidence_version", "evidence_digest", "qualifiers"},
    "provenance_statement_ref": {"statement_id", "revision", "statement_version", "digest"},
    "provenance_statement_version": {"statement_version", "revision", "previous_revision"},
    "provenance_statement": {"identity", "category", "subject", "version", "digest", "entities", "actors", "activity", "evidence", "predecessors", "qualifiers", "declared_at", "foundation_version"},
    "provenance_statement_comparison_result": {"same_identity", "left_node_key", "right_node_key", "same_digest", "changed_fields"},
    "provenance_chain_validation_result": {"node_keys", "root_keys", "external_predecessors", "components", "edge_count"},
}


def _error(code: str, field: str, detail: str) -> ProvenanceSerializationError:
    return ProvenanceSerializationError(code, "provenance_envelope", field, detail)


def _mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise _error("PS004", field, "must be object")
    return value


def _array(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise _error("PS004", field, "must be array")
    return value


def _strict(payload: Mapping[str, object]) -> tuple[str, dict[str, object]]:
    model = payload.get("model")
    if not isinstance(model, str) or model not in _MODEL_FIELDS:
        raise _error("PS003", "model", "unknown or missing discriminator")
    expected = _MODEL_FIELDS[model] | {"model", "schema_version", "serialization_version"}
    if set(payload) != expected:
        raise _error("PS004", model, "missing or extra field")
    if payload["schema_version"] != PROVENANCE_SCHEMA_VERSION or payload["serialization_version"] != PROVENANCE_SERIALIZATION_VERSION:
        raise _error("PS005", model, "unsupported schema or serialization version")
    return model, dict(payload)


def _enum(enum_type, value: object, field: str):
    from .contracts import validation

    try:
        return enum_type(value)
    except (TypeError, ValueError) as error:
        raise validation("PV003", "provenance_envelope", field, "unknown enum value") from error


class DeterministicProvenanceSerializer:
    """Serialize and reconstruct every closed provenance discriminator."""

    def to_dict(self, *, value: object) -> dict[str, CanonicalJSON]:
        from .validator import ProvenanceStatementValidator

        ProvenanceStatementValidator().validate(value=value)
        result: dict[str, CanonicalJSON] = {
            "model": value.model,
            "schema_version": value.schema_version,
            "serialization_version": value.serialization_version,
        }
        for field in _MODEL_FIELDS[value.model]:
            result[field] = self._primitive(getattr(value, field))
        return result

    def _primitive(self, value: object) -> CanonicalJSON:
        if isinstance(value, Enum):
            return value.value
        if value is None or isinstance(value, (bool, int, str)):
            return value
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, datetime):
            return instant_text(value)
        if isinstance(value, tuple):
            return [self._primitive(item) for item in value]
        if hasattr(value, "model"):
            return self.to_dict(value=value)
        try:
            primitive = canonical_primitive(value)
            if primitive is value:
                raise TypeError
            return primitive
        except (TypeError, AttributeError) as error:
            raise _error("PS007", "value", "unsupported canonical value") from error

    def canonical_bytes(self, *, value: object, include_digest: bool = True) -> bytes:
        payload = self.to_dict(value=value)
        if isinstance(value, ProvenanceStatement) and not include_digest:
            payload.pop("digest")
        return canonical_json(payload)

    def to_json(self, *, value: object) -> bytes:
        return self.canonical_bytes(value=value)

    def digest(self, *, statement: ProvenanceStatement) -> str:
        if not isinstance(statement, ProvenanceStatement):
            raise _error("PS004", "statement", "must be ProvenanceStatement")
        return hashlib.sha256(self.canonical_bytes(value=statement, include_digest=False)).hexdigest()

    def from_dict(self, *, payload: Mapping[str, object]) -> object:
        model, p = _strict(_mapping(payload, "payload"))
        nested = lambda item: self.from_dict(payload=_mapping(item, "nested"))
        common = {
            "schema_version": p["schema_version"],
            "serialization_version": p["serialization_version"],
        }
        try:
            if model == "provenance_statement_id":
                return ProvenanceStatementId(value=UUID(p["value"]), **common)
            if model == "provenance_statement_identity":
                return ProvenanceStatementIdentity(
                    statement_id=nested(p["statement_id"]),
                    business_namespace=p["business_namespace"],
                    lineage_key=p["lineage_key"],
                    **common,
                )
            if model == "provenance_qualifier":
                return ProvenanceQualifier(name=p["name"], value=p["value"], **common)
            if model == "provenance_subject_ref":
                return ProvenanceSubjectRef(
                    target_type=_enum(ProvenanceTargetType, p["target_type"], "target_type"),
                    namespace=p["namespace"], target_id=p["target_id"],
                    target_canonical_id=p["target_canonical_id"],
                    target_external_id=p["target_external_id"],
                    target_version=p["target_version"], target_digest=p["target_digest"], **common,
                )
            if model == "provenance_entity_ref":
                return ProvenanceEntityRef(
                    target_type=_enum(ProvenanceTargetType, p["target_type"], "target_type"),
                    namespace=p["namespace"], target_id=p["target_id"],
                    role=_enum(ProvenanceEntityRole, p["role"], "role"),
                    target_canonical_id=p["target_canonical_id"],
                    target_external_id=p["target_external_id"],
                    target_version=p["target_version"], target_digest=p["target_digest"], **common,
                )
            if model == "provenance_actor_ref":
                return ProvenanceActorRef(
                    actor_type=_enum(ProvenanceActorType, p["actor_type"], "actor_type"), namespace=p["namespace"],
                    actor_id=p["actor_id"], role=_enum(ProvenanceActorRole, p["role"], "role"),
                    actor_version=p["actor_version"], actor_digest=p["actor_digest"], **common,
                )
            if model == "provenance_activity_ref":
                return ProvenanceActivityRef(
                    activity_type=_enum(ProvenanceActivityType, p["activity_type"], "activity_type"),
                    namespace=p["namespace"], activity_id=p["activity_id"], label=p["label"],
                    started_at=None if p["started_at"] is None else parse_instant(p["started_at"], "started_at", model),
                    ended_at=None if p["ended_at"] is None else parse_instant(p["ended_at"], "ended_at", model),
                    qualifiers=tuple(nested(item) for item in _array(p["qualifiers"], "qualifiers")), **common,
                )
            if model == "provenance_evidence_ref":
                return ProvenanceEvidenceRef(
                    evidence_type=_enum(ProvenanceEvidenceType, p["evidence_type"], "evidence_type"),
                    namespace=p["namespace"], evidence_id=p["evidence_id"],
                    evidence_version=p["evidence_version"], evidence_digest=p["evidence_digest"],
                    qualifiers=tuple(nested(item) for item in _array(p["qualifiers"], "qualifiers")), **common,
                )
            if model == "provenance_statement_ref":
                return ProvenanceStatementRef(
                    statement_id=nested(p["statement_id"]), revision=p["revision"],
                    statement_version=p["statement_version"], digest=p["digest"], **common,
                )
            if model == "provenance_statement_version":
                return ProvenanceStatementVersion(
                    statement_version=p["statement_version"], revision=p["revision"],
                    previous_revision=None if p["previous_revision"] is None else nested(p["previous_revision"]),
                    **common,
                )
            if model == "provenance_statement":
                from .factory import ProvenanceStatementFactory
                return ProvenanceStatementFactory().from_parts(
                    identity=nested(p["identity"]),
                    category=_enum(ProvenanceStatementCategory, p["category"], "category"),
                    subject=nested(p["subject"]), version=nested(p["version"]), digest=p["digest"],
                    entities=tuple(nested(item) for item in _array(p["entities"], "entities")),
                    actors=tuple(nested(item) for item in _array(p["actors"], "actors")),
                    activity=None if p["activity"] is None else nested(p["activity"]),
                    evidence=tuple(nested(item) for item in _array(p["evidence"], "evidence")),
                    predecessors=tuple(nested(item) for item in _array(p["predecessors"], "predecessors")),
                    qualifiers=tuple(nested(item) for item in _array(p["qualifiers"], "qualifiers")),
                    declared_at=None if p["declared_at"] is None else parse_instant(p["declared_at"], "declared_at", model),
                    foundation_version=p["foundation_version"],
                )
            if model == "provenance_statement_comparison_result":
                return ProvenanceStatementComparisonResult(
                    same_identity=p["same_identity"], left_node_key=p["left_node_key"],
                    right_node_key=p["right_node_key"], same_digest=p["same_digest"],
                    changed_fields=tuple(_array(p["changed_fields"], "changed_fields")), **common,
                )
            return ProvenanceChainValidationResult(
                node_keys=tuple(_array(p["node_keys"], "node_keys")),
                root_keys=tuple(_array(p["root_keys"], "root_keys")),
                external_predecessors=tuple(_array(p["external_predecessors"], "external_predecessors")),
                components=tuple(tuple(_array(item, "component")) for item in _array(p["components"], "components")),
                edge_count=p["edge_count"], **common,
            )
        except ProvenanceError:
            raise
        except (TypeError, ValueError, KeyError, AttributeError) as error:
            raise _error("PS004", model, "invalid field value") from error

    def from_json(self, *, payload: bytes) -> object:
        if not isinstance(payload, bytes):
            raise _error("PS001", "payload", "must be bytes")

        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise _error("PS002", key, "duplicate JSON key")
                result[key] = value
            return result

        try:
            text_payload = payload.decode("utf-8", "strict")
            decoded = json.loads(
                text_payload,
                object_pairs_hook=pairs,
                parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
            )
        except ProvenanceSerializationError:
            raise
        except (UnicodeError, ValueError, json.JSONDecodeError) as error:
            raise _error("PS001", "payload", "must be strict UTF-8 JSON") from error
        value = self.from_dict(payload=_mapping(decoded, "payload"))
        if self.to_json(value=value) != payload:
            raise _error("PS006", "payload", "JSON is not canonical")
        return value


__all__ = ["DeterministicProvenanceSerializer"]
