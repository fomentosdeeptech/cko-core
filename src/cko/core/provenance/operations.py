"""Pure immutable operations over provenance statements."""

from __future__ import annotations

import hmac
from datetime import datetime

from .contracts import validation
from .errors import ProvenanceDigestError
from .factory import ProvenanceStatementFactory
from .models import ProvenanceQualifier, ProvenanceStatement
from .references import (
    ProvenanceActivityRef,
    ProvenanceActorRef,
    ProvenanceEntityRef,
    ProvenanceEvidenceRef,
    ProvenanceStatementRef,
)
from .results import ProvenanceStatementComparisonResult
from .serializer import DeterministicProvenanceSerializer
from .validator import ProvenanceStatementValidator
from .versioning import ProvenanceStatementVersion


class ProvenanceOperations:
    """Stateless deterministic transformations and observations."""

    @staticmethod
    def revise(
        *,
        statement: ProvenanceStatement,
        entities: tuple[ProvenanceEntityRef, ...],
        actors: tuple[ProvenanceActorRef, ...],
        activity: ProvenanceActivityRef | None,
        evidence: tuple[ProvenanceEvidenceRef, ...],
        predecessors: tuple[ProvenanceStatementRef, ...],
        qualifiers: tuple[ProvenanceQualifier, ...],
        declared_at: datetime | None,
    ) -> ProvenanceStatement:
        proposed = (tuple(entities), tuple(actors), activity, tuple(evidence), tuple(predecessors), tuple(qualifiers), declared_at)
        current = (
            statement.entities, statement.actors, statement.activity, statement.evidence,
            statement.predecessors, statement.qualifiers, statement.declared_at,
        )
        if proposed == current:
            raise validation("PV005", statement.model, "revision", "revision must change content")
        previous = ProvenanceStatementRef(
            statement_id=statement.identity.statement_id,
            revision=statement.version.revision,
            statement_version=statement.version.statement_version,
            digest=statement.digest,
        )
        revision = statement.version.revision + 1
        version = ProvenanceStatementVersion(
            statement_version=f"1.0.{revision - 1}",
            revision=revision,
            previous_revision=previous,
        )
        return ProvenanceStatementFactory()._build(
            identity=statement.identity,
            category=statement.category,
            subject=statement.subject,
            version=version,
            entities=entities,
            actors=actors,
            activity=activity,
            evidence=evidence,
            predecessors=predecessors,
            qualifiers=qualifiers,
            declared_at=declared_at,
            foundation_version=statement.foundation_version,
        )

    @staticmethod
    def _member_change(*, statement, field, member, add, declared_at):
        values = getattr(statement, field)
        exists = member in values
        if add and exists:
            raise validation("PV004", statement.model, field, "member already present")
        if not add and not exists:
            raise validation("PV008", statement.model, field, "member is absent")
        changed = values + (member,) if add else tuple(item for item in values if item != member)
        content = {
            "entities": statement.entities,
            "actors": statement.actors,
            "activity": statement.activity,
            "evidence": statement.evidence,
            "predecessors": statement.predecessors,
            "qualifiers": statement.qualifiers,
            "declared_at": declared_at,
        }
        content[field] = changed
        return ProvenanceOperations.revise(statement=statement, **content)

    @staticmethod
    def with_actor(*, statement: ProvenanceStatement, actor: ProvenanceActorRef, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="actors", member=actor, add=True, declared_at=declared_at)

    @staticmethod
    def without_actor(*, statement: ProvenanceStatement, actor: ProvenanceActorRef, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="actors", member=actor, add=False, declared_at=declared_at)

    @staticmethod
    def with_entity(*, statement: ProvenanceStatement, entity: ProvenanceEntityRef, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="entities", member=entity, add=True, declared_at=declared_at)

    @staticmethod
    def without_entity(*, statement: ProvenanceStatement, entity: ProvenanceEntityRef, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="entities", member=entity, add=False, declared_at=declared_at)

    @staticmethod
    def with_evidence(*, statement: ProvenanceStatement, evidence_ref: ProvenanceEvidenceRef, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="evidence", member=evidence_ref, add=True, declared_at=declared_at)

    @staticmethod
    def without_evidence(*, statement: ProvenanceStatement, evidence_ref: ProvenanceEvidenceRef, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="evidence", member=evidence_ref, add=False, declared_at=declared_at)

    @staticmethod
    def with_predecessor(*, statement: ProvenanceStatement, predecessor: ProvenanceStatementRef, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="predecessors", member=predecessor, add=True, declared_at=declared_at)

    @staticmethod
    def without_predecessor(*, statement: ProvenanceStatement, predecessor: ProvenanceStatementRef, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="predecessors", member=predecessor, add=False, declared_at=declared_at)

    @staticmethod
    def with_qualifier(*, statement: ProvenanceStatement, qualifier: ProvenanceQualifier, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="qualifiers", member=qualifier, add=True, declared_at=declared_at)

    @staticmethod
    def without_qualifier(*, statement: ProvenanceStatement, qualifier: ProvenanceQualifier, declared_at: datetime | None) -> ProvenanceStatement:
        return ProvenanceOperations._member_change(statement=statement, field="qualifiers", member=qualifier, add=False, declared_at=declared_at)

    @staticmethod
    def with_activity(*, statement: ProvenanceStatement, activity: ProvenanceActivityRef, declared_at: datetime | None) -> ProvenanceStatement:
        if statement.activity is not None:
            raise validation("PV004", statement.model, "activity", "activity already present")
        return ProvenanceOperations.revise(
            statement=statement, entities=statement.entities, actors=statement.actors,
            activity=activity, evidence=statement.evidence, predecessors=statement.predecessors,
            qualifiers=statement.qualifiers, declared_at=declared_at,
        )

    @staticmethod
    def without_activity(*, statement: ProvenanceStatement, declared_at: datetime | None) -> ProvenanceStatement:
        if statement.activity is None:
            raise validation("PV008", statement.model, "activity", "activity is absent")
        return ProvenanceOperations.revise(
            statement=statement, entities=statement.entities, actors=statement.actors,
            activity=None, evidence=statement.evidence, predecessors=statement.predecessors,
            qualifiers=statement.qualifiers, declared_at=declared_at,
        )

    @staticmethod
    def compare(*, left: ProvenanceStatement, right: ProvenanceStatement) -> ProvenanceStatementComparisonResult:
        serializer = DeterministicProvenanceSerializer()
        left_payload = serializer.to_dict(value=left)
        right_payload = serializer.to_dict(value=right)
        fields = (
            "activity", "actors", "category", "declared_at", "entities", "evidence",
            "identity", "predecessors", "qualifiers", "subject", "version",
        )
        changed = tuple(f"/{field}" for field in fields if left_payload[field] != right_payload[field])
        return ProvenanceStatementComparisonResult(
            same_identity=left.identity == right.identity,
            left_node_key=left.node_key,
            right_node_key=right.node_key,
            same_digest=left.digest == right.digest,
            changed_fields=changed,
        )

    @staticmethod
    def verify_digest(*, statement: ProvenanceStatement) -> bool:
        calculated = DeterministicProvenanceSerializer().digest(statement=statement)
        return hmac.compare_digest(calculated, statement.digest)

    @staticmethod
    def require_valid_digest(*, statement: ProvenanceStatement) -> None:
        if not ProvenanceOperations.verify_digest(statement=statement):
            raise ProvenanceDigestError("PD001", statement.model, "digest", "digest does not match canonical payload")

    @staticmethod
    def validate_chain_in_supplied_set(*, statements):
        return ProvenanceStatementValidator().validate_chain_in_supplied_set(statements=statements)

    @staticmethod
    def project_relationships(*, statement: ProvenanceStatement):
        from .relationship_projection import project_relationships
        return project_relationships(statement)


__all__ = ["ProvenanceOperations"]
