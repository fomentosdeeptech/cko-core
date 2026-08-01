"""Mandatory validated creation boundary for canonical relationships."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable, Mapping
from uuid import UUID, uuid4

from .enums import (
    RelationshipDirectionType, RelationshipStatus, RelationshipStrength,
    RelationshipType,
)
from .errors import RelationshipError, RelationshipFactoryError
from .identity import RelationshipEndpoint, RelationshipId, RelationshipIdentity
from .metadata import (
    RelationshipConstraint, RelationshipDirection, RelationshipEvidence,
    RelationshipMetadata, RelationshipWeight,
)
from .models import (
    _FACTORY_TOKEN, CanonicalRelationship, RelationshipCollection,
    RelationshipDescriptor, RelationshipVersion,
)
from .validator import RelationshipValidator


class RelationshipFactory:
    """Create relationship aggregates through one validation boundary."""

    def __init__(
        self,
        validator: RelationshipValidator | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator = validator or RelationshipValidator()
        self._clock = clock or (lambda: datetime.now(UTC))

    def create(
        self,
        *,
        namespace: str,
        source: RelationshipEndpoint,
        target: RelationshipEndpoint,
        relationship_type: RelationshipType,
        created_by: str,
        direction: RelationshipDirection | None = None,
        constraint: RelationshipConstraint | None = None,
        evidence: tuple[RelationshipEvidence, ...] = (),
        weights: tuple[RelationshipWeight, ...] = (),
        status: RelationshipStatus = RelationshipStatus.ACTIVE,
        strength: RelationshipStrength = RelationshipStrength.UNKNOWN,
        version: str = "1.0.0",
        logical_id: RelationshipId | None = None,
        parent_version: UUID | None = None,
        source_name: str | None = None,
        attributes: Mapping[str, object] | None = None,
        label: str | None = None,
        description: str | None = None,
    ) -> CanonicalRelationship:
        try:
            selected_direction = direction or RelationshipDirection()
            selected_constraint = constraint or RelationshipConstraint(
                bidirectional=selected_direction.direction in {
                    RelationshipDirectionType.BIDIRECTIONAL,
                    RelationshipDirectionType.UNDIRECTED,
                }
            )
            descriptor = RelationshipDescriptor(
                relationship_type,
                selected_direction,
                selected_constraint,
                strength,
                label,
                description,
            )
            semantic_key = RelationshipValidator.build_semantic_key(
                source=source,
                target=target,
                relationship_type=descriptor.relationship_type.value,
                direction=descriptor.direction.direction.value,
                multiplicity=descriptor.constraint.multiplicity,
            )
            selected_id = logical_id or RelationshipId.new()
            identity = RelationshipIdentity(
                selected_id,
                RelationshipId.canonical(namespace, semantic_key),
                namespace,
                semantic_key,
            )
            now = self._clock()
            metadata = RelationshipMetadata(
                now, now, created_by, status, source_name, attributes or {},
            )
            version_model = RelationshipVersion(
                uuid4(), version, now, created_by, status, parent_version,
            )
            return self.from_parts(
                identity=identity,
                metadata=metadata,
                source=source,
                target=target,
                descriptor=descriptor,
                version=version_model,
                evidence=evidence,
                weights=weights,
            )
        except RelationshipError:
            raise
        except Exception as error:
            raise RelationshipFactoryError("canonical relationship creation failed") from error

    def from_parts(
        self,
        *,
        identity: RelationshipIdentity,
        metadata: RelationshipMetadata,
        source: RelationshipEndpoint,
        target: RelationshipEndpoint,
        descriptor: RelationshipDescriptor,
        version: RelationshipVersion,
        evidence: tuple[RelationshipEvidence, ...] = (),
        weights: tuple[RelationshipWeight, ...] = (),
    ) -> CanonicalRelationship:
        value = CanonicalRelationship(
            identity, metadata, source, target, descriptor, version,
            evidence, weights, _factory_token=_FACTORY_TOKEN,
        )
        self._validator.validate(value)
        return value

    def create_collection(
        self,
        relationships: tuple[CanonicalRelationship, ...] = (),
        name: str | None = None,
    ) -> RelationshipCollection:
        value = RelationshipCollection(
            relationships, name, _factory_token=_FACTORY_TOKEN,
        )
        self._validator.validate(value)
        return value


__all__ = ["RelationshipFactory"]
