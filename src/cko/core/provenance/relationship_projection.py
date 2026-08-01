"""Explicit lossy projection from statements to canonical relationships."""

from __future__ import annotations

from uuid import UUID, uuid5

from cko.core.relationships import (
    CanonicalRelationship,
    RelationshipConstraint,
    RelationshipDescriptor,
    RelationshipDirection,
    RelationshipDirectionType,
    RelationshipEndpoint,
    RelationshipFactory,
    RelationshipId,
    RelationshipIdentity,
    RelationshipMetadata,
    RelationshipStatus,
    RelationshipStrength,
    RelationshipType,
    RelationshipValidator,
    RelationshipVersion,
)

from .constants import PROVENANCE_UUID_NAMESPACE
from .contracts import canonical_json, validation
from .enums import ProvenanceStatementCategory, ProvenanceTargetType
from .models import ProvenanceStatement
from .references import ProvenanceEntityRef, ProvenanceSubjectRef


_GENERATED = {
    ProvenanceStatementCategory.ORIGIN,
    ProvenanceStatementCategory.GENERATION,
}


def _endpoint(value: ProvenanceSubjectRef | ProvenanceEntityRef) -> RelationshipEndpoint:
    if (
        value.target_type not in {ProvenanceTargetType.KNOWLEDGE_OBJECT, ProvenanceTargetType.DOCUMENT}
        or value.target_canonical_id is None
        or value.target_version is None
    ):
        raise validation(
            "PV005",
            "provenance_statement",
            "relationship_projection_not_representable",
            "target cannot be represented by RelationshipEndpoint",
        )
    return RelationshipEndpoint(
        object_id=UUID(value.target_id),
        namespace=value.namespace,
        entity_type="knowledge_object" if value.target_type is ProvenanceTargetType.KNOWLEDGE_OBJECT else "canonical_document",
        version=value.target_version,
        canonical_id=UUID(value.target_canonical_id),
        external_id=value.target_external_id,
    )


def project_relationships(statement: ProvenanceStatement) -> tuple[CanonicalRelationship, ...]:
    if statement.category is ProvenanceStatementCategory.ATTRIBUTION or not statement.entities:
        return ()
    if statement.declared_at is None:
        raise validation(
            "PV005",
            statement.model,
            "relationship_projection_not_representable",
            "declared_at is required",
        )
    target = _endpoint(statement.subject)
    relationship_type = (
        RelationshipType.GENERATED_INTO
        if statement.category in _GENERATED
        else RelationshipType.DERIVED_INTO
    )
    results = []
    for entity in statement.entities:
        source = _endpoint(entity)
        semantic_key = RelationshipValidator.build_semantic_key(
            source=source,
            target=target,
            relationship_type=relationship_type.value,
            direction=RelationshipDirectionType.DIRECTED.value,
            multiplicity="many_to_one",
        )
        logical_payload = {
            "entity": {
                "namespace": entity.namespace,
                "role": entity.role.value,
                "target_id": entity.target_id,
                "target_type": entity.target_type.value,
            },
            "kind": "relationship_projection_logical",
            "relationship_type": relationship_type.value,
            "revision": statement.version.revision,
            "statement_id": str(statement.identity.statement_id),
        }
        logical_id = uuid5(
            PROVENANCE_UUID_NAMESPACE,
            canonical_json(logical_payload).decode("utf-8"),
        )
        version_payload = {
            "kind": "relationship_projection_version",
            "logical_id": str(logical_id),
            "revision": statement.version.revision,
            "statement_digest": statement.digest,
            "statement_version": statement.version.statement_version,
        }
        version_id = uuid5(
            PROVENANCE_UUID_NAMESPACE,
            canonical_json(version_payload).decode("utf-8"),
        )
        identity = RelationshipIdentity(
            logical_id=RelationshipId(value=logical_id),
            canonical_id=RelationshipId.canonical("cko.core.provenance.projection", semantic_key),
            namespace="cko.core.provenance.projection",
            semantic_key=semantic_key,
        )
        created_by = f"provenance:{statement.identity.statement_id}"
        metadata = RelationshipMetadata(
            created_at=statement.declared_at,
            modified_at=statement.declared_at,
            created_by=created_by,
            status=RelationshipStatus.ACTIVE,
            source="cko.core.provenance",
            attributes={
                "category": statement.category.value,
                "entity_role": entity.role.value,
                "statement_digest": statement.digest,
                "statement_id": str(statement.identity.statement_id),
                "statement_revision": statement.version.revision,
            },
        )
        descriptor = RelationshipDescriptor(
            relationship_type=relationship_type,
            direction=RelationshipDirection(
                direction=RelationshipDirectionType.DIRECTED,
                source_role="provenance_entity",
                target_role="provenance_subject",
            ),
            constraint=RelationshipConstraint(
                unique=True,
                multiplicity="many_to_one",
                bidirectional=False,
                transitive=False,
                symmetric=False,
                reflexive=False,
            ),
            strength=RelationshipStrength.UNKNOWN,
            label=None,
            description=None,
        )
        version = RelationshipVersion(
            version_id=version_id,
            version=statement.version.statement_version,
            created_at=statement.declared_at,
            created_by=created_by,
            status=RelationshipStatus.ACTIVE,
            parent_version=None,
        )
        results.append(RelationshipFactory().from_parts(
            identity=identity,
            metadata=metadata,
            source=source,
            target=target,
            descriptor=descriptor,
            version=version,
            evidence=(),
            weights=(),
        ))
    return tuple(results)
