"""Strict deterministic UTF-8 JSON serialization for relationship models."""

from __future__ import annotations

import hashlib
import json
from typing import Mapping
from uuid import UUID

from .contracts import RelationshipModel, parse_instant, strict
from .enums import (
    RelationshipDirectionType, RelationshipEvidenceType, RelationshipStatus,
    RelationshipStrength, RelationshipType,
)
from .errors import RelationshipError, RelationshipSerializationError
from .factory import RelationshipFactory
from .identity import RelationshipEndpoint, RelationshipId, RelationshipIdentity
from .metadata import (
    RelationshipConstraint, RelationshipDirection, RelationshipEvidence,
    RelationshipMetadata, RelationshipWeight,
)
from .models import (
    CanonicalRelationship, RelationshipCollection, RelationshipDescriptor,
    RelationshipQuery, RelationshipResult, RelationshipVersion,
)
from .validator import RelationshipValidator


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RelationshipSerializationError(f"{name} must be an object")
    return value


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise RelationshipSerializationError(f"{name} must be an array")
    return value


class DeterministicRelationshipSerializer:
    """Serialize and restore closed canonical relationship envelopes."""

    def __init__(
        self,
        factory: RelationshipFactory | None = None,
        validator: RelationshipValidator | None = None,
    ) -> None:
        self._validator = validator or RelationshipValidator()
        self._factory = factory or RelationshipFactory(self._validator)

    def serialize(self, value: RelationshipModel) -> bytes:
        self._validator.validate(value)
        try:
            return json.dumps(
                value.to_dict(), ensure_ascii=False, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError, UnicodeError) as error:
            raise RelationshipSerializationError("relationship serialization failed") from error

    def deserialize(self, payload: bytes | str) -> RelationshipModel:
        try:
            encoded = payload.decode("utf-8") if isinstance(payload, bytes) else payload
            if not isinstance(encoded, str):
                raise TypeError
            decoded = json.loads(
                encoded,
                parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
            )
        except (TypeError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
            raise RelationshipSerializationError("payload must be strict UTF-8 JSON") from error
        try:
            value = self.from_dict(_mapping(decoded, "payload"))
        except RelationshipSerializationError:
            raise
        except (RelationshipError, TypeError, ValueError, KeyError, AttributeError) as error:
            raise RelationshipSerializationError("payload violates the relationship schema") from error
        if self.serialize(value).decode("utf-8") != encoded:
            raise RelationshipSerializationError("payload is not canonical JSON")
        return value

    def digest(self, value: RelationshipModel) -> str:
        return hashlib.sha256(self.serialize(value)).hexdigest()

    def from_dict(self, payload: Mapping[str, object]) -> RelationshipModel:
        model = payload.get("model")
        if not isinstance(model, str):
            raise RelationshipSerializationError("model discriminator is required")
        nested = lambda item: self.from_dict(_mapping(item, "nested model"))

        if model == "relationship_id":
            p = strict(payload, model, {"value"})
            return RelationshipId.parse(p["value"])  # type: ignore[arg-type]
        if model == "relationship_identity":
            p = strict(payload, model, {"logical_id", "canonical_id", "namespace", "semantic_key"})
            return RelationshipIdentity(nested(p["logical_id"]), nested(p["canonical_id"]), p["namespace"], p["semantic_key"])  # type: ignore[arg-type]
        if model == "relationship_endpoint":
            p = strict(payload, model, {"object_id", "namespace", "entity_type", "version", "canonical_id", "external_id"})
            return RelationshipEndpoint(UUID(p["object_id"]), p["namespace"], p["entity_type"], p["version"], None if p["canonical_id"] is None else UUID(p["canonical_id"]), p["external_id"])  # type: ignore[arg-type]
        if model == "relationship_metadata":
            p = strict(payload, model, {"created_at", "modified_at", "created_by", "status", "source", "attributes"})
            return RelationshipMetadata(parse_instant(p["created_at"], "created_at"), parse_instant(p["modified_at"], "modified_at"), p["created_by"], RelationshipStatus(p["status"]), p["source"], _mapping(p["attributes"], "attributes"))  # type: ignore[arg-type]
        if model == "relationship_direction":
            p = strict(payload, model, {"direction", "source_role", "target_role"})
            return RelationshipDirection(RelationshipDirectionType(p["direction"]), p["source_role"], p["target_role"])  # type: ignore[arg-type]
        if model == "relationship_constraint":
            p = strict(payload, model, {"unique", "multiplicity", "bidirectional", "transitive", "symmetric", "reflexive"})
            return RelationshipConstraint(p["unique"], p["multiplicity"], p["bidirectional"], p["transitive"], p["symmetric"], p["reflexive"])  # type: ignore[arg-type]
        if model == "relationship_evidence":
            p = strict(payload, model, {"evidence_type", "source", "evidence", "generating_algorithm", "confidence", "timestamp", "author", "pipeline", "version"})
            return RelationshipEvidence(RelationshipEvidenceType(p["evidence_type"]), p["source"], p["evidence"], p["generating_algorithm"], p["confidence"], None if p["timestamp"] is None else parse_instant(p["timestamp"], "timestamp"), p["author"], p["pipeline"], p["version"])  # type: ignore[arg-type]
        if model == "relationship_weight":
            p = strict(payload, model, {"weight", "confidence", "relevance", "probability"})
            return RelationshipWeight(p["weight"], p["confidence"], p["relevance"], p["probability"])  # type: ignore[arg-type]
        if model == "relationship_version":
            p = strict(payload, model, {"version_id", "version", "created_at", "created_by", "status", "parent_version"})
            return RelationshipVersion(UUID(p["version_id"]), p["version"], parse_instant(p["created_at"], "created_at"), p["created_by"], RelationshipStatus(p["status"]), None if p["parent_version"] is None else UUID(p["parent_version"]))  # type: ignore[arg-type]
        if model == "relationship_descriptor":
            p = strict(payload, model, {"relationship_type", "direction", "constraint", "strength", "label", "description"})
            return RelationshipDescriptor(RelationshipType(p["relationship_type"]), nested(p["direction"]), nested(p["constraint"]), RelationshipStrength(p["strength"]), p["label"], p["description"])  # type: ignore[arg-type]
        if model == "canonical_relationship":
            p = strict(payload, model, {"identity", "metadata", "source", "target", "descriptor", "version", "evidence", "weights"})
            return self._factory.from_parts(identity=nested(p["identity"]), metadata=nested(p["metadata"]), source=nested(p["source"]), target=nested(p["target"]), descriptor=nested(p["descriptor"]), version=nested(p["version"]), evidence=tuple(nested(item) for item in _list(p["evidence"], "evidence")), weights=tuple(nested(item) for item in _list(p["weights"], "weights")))  # type: ignore[arg-type]
        if model == "relationship_collection":
            p = strict(payload, model, {"relationships", "name"})
            return self._factory.create_collection(tuple(nested(item) for item in _list(p["relationships"], "relationships")), p["name"])  # type: ignore[arg-type]
        if model == "relationship_query":
            p = strict(payload, model, {"relationship_ids", "source_ids", "target_ids", "relationship_types", "statuses", "namespace", "limit", "offset"})
            return RelationshipQuery(tuple(nested(item) for item in _list(p["relationship_ids"], "relationship_ids")), tuple(UUID(item) for item in _list(p["source_ids"], "source_ids")), tuple(UUID(item) for item in _list(p["target_ids"], "target_ids")), tuple(RelationshipType(item) for item in _list(p["relationship_types"], "relationship_types")), tuple(RelationshipStatus(item) for item in _list(p["statuses"], "statuses")), p["namespace"], p["limit"], p["offset"])  # type: ignore[arg-type]
        if model == "relationship_result":
            p = strict(payload, model, {"query", "relationships", "total"})
            return RelationshipResult(nested(p["query"]), tuple(nested(item) for item in _list(p["relationships"], "relationships")), p["total"])  # type: ignore[arg-type]
        raise RelationshipSerializationError(f"unknown model discriminator: {model}")


__all__ = ["DeterministicRelationshipSerializer"]
