"""Structural and cross-model validation for canonical relationships."""

from __future__ import annotations

import json
from dataclasses import is_dataclass

from .contracts import RelationshipModel, primitive
from .enums import RelationshipDirectionType
from .errors import RelationshipValidationError
from .identity import RelationshipId
from .models import CanonicalRelationship, RelationshipCollection


class RelationshipValidator:
    """Validate immutable models without executing semantic inference."""

    def validate(self, value: RelationshipModel) -> None:
        if not isinstance(value, RelationshipModel) or not is_dataclass(value):
            raise RelationshipValidationError("value must be a canonical relationship dataclass")
        value._validate_schema()
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen or not hasattr(type(value), "__slots__"):
            raise RelationshipValidationError("relationship models must be frozen and slotted")
        if value.model != type(value).discriminator:
            raise RelationshipValidationError("invalid model discriminator")
        if isinstance(value, CanonicalRelationship):
            self._validate_relationship(value)
        elif isinstance(value, RelationshipCollection):
            self._validate_collection(value)

    def _validate_relationship(self, value: CanonicalRelationship) -> None:
        if value.metadata.status is not value.version.status:
            raise RelationshipValidationError("metadata and version status mismatch")
        if value.metadata.created_by != value.version.created_by:
            raise RelationshipValidationError("metadata and version author mismatch")
        if value.version.created_at < value.metadata.created_at:
            raise RelationshipValidationError("version cannot precede relationship metadata")
        source_key = (value.source.namespace, value.source.object_id)
        target_key = (value.target.namespace, value.target.object_id)
        if source_key == target_key and not value.descriptor.constraint.reflexive:
            raise RelationshipValidationError("self relationship requires declared reflexivity")
        expected_bidirectional = value.descriptor.direction.direction in {
            RelationshipDirectionType.BIDIRECTIONAL,
            RelationshipDirectionType.UNDIRECTED,
        }
        if value.descriptor.constraint.bidirectional != expected_bidirectional:
            raise RelationshipValidationError("direction and bidirectionality constraint mismatch")
        semantic_key = self.semantic_key(value)
        if value.identity.semantic_key != semantic_key:
            raise RelationshipValidationError("identity semantic_key does not match relationship")
        if value.identity.canonical_id != RelationshipId.canonical(value.identity.namespace, semantic_key):
            raise RelationshipValidationError("relationship canonical identity is inconsistent")
        evidence_payloads = tuple(
            json.dumps(primitive(item), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
            for item in value.evidence
        )
        if len(evidence_payloads) != len(set(evidence_payloads)):
            raise RelationshipValidationError("duplicate relationship evidence")

    def _validate_collection(self, value: RelationshipCollection) -> None:
        for relationship in value.relationships:
            self._validate_relationship(relationship)
        unique_keys = [
            item.identity.semantic_key
            for item in value.relationships
            if item.descriptor.constraint.unique
        ]
        if len(unique_keys) != len(set(unique_keys)):
            raise RelationshipValidationError("duplicate unique relationship declarations")

    @staticmethod
    def semantic_key(value: CanonicalRelationship) -> str:
        return RelationshipValidator.build_semantic_key(
            source=value.source,
            target=value.target,
            relationship_type=value.descriptor.relationship_type.value,
            direction=value.descriptor.direction.direction.value,
            multiplicity=value.descriptor.constraint.multiplicity,
        )

    @staticmethod
    def build_semantic_key(*, source, target, relationship_type: str, direction: str, multiplicity: str) -> str:
        return "|".join((
            source.namespace,
            str(source.object_id),
            target.namespace,
            str(target.object_id),
            relationship_type,
            direction,
            multiplicity,
        ))


__all__ = ["RelationshipValidator"]
