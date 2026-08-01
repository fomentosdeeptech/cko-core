"""Mandatory construction boundary for provenance statements."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .constants import PROVENANCE_VERSION
from .enums import ProvenanceStatementCategory
from .errors import ProvenanceDigestError
from .identity import (
    ProvenanceStatementIdentity,
    _calculate_statement_id,
)
from .models import _FACTORY_TOKEN, ProvenanceQualifier, ProvenanceStatement
from .references import (
    ProvenanceActivityRef,
    ProvenanceActorRef,
    ProvenanceEntityRef,
    ProvenanceEvidenceRef,
    ProvenanceStatementRef,
    ProvenanceSubjectRef,
)
from .versioning import ProvenanceStatementVersion


class ProvenanceStatementFactory:
    """Create complete, validated statements without ambient state."""

    def create(
        self,
        *,
        business_namespace: str,
        lineage_key: str,
        category: ProvenanceStatementCategory,
        subject: ProvenanceSubjectRef,
        entities: Iterable[ProvenanceEntityRef] = (),
        actors: Iterable[ProvenanceActorRef] = (),
        activity: ProvenanceActivityRef | None = None,
        evidence: Iterable[ProvenanceEvidenceRef] = (),
        predecessors: Iterable[ProvenanceStatementRef] = (),
        qualifiers: Iterable[ProvenanceQualifier] = (),
        declared_at: datetime | None = None,
    ) -> ProvenanceStatement:
        if not isinstance(category, ProvenanceStatementCategory):
            from .contracts import validation
            raise validation("PV003", "provenance_statement", "category", "must be ProvenanceStatementCategory")
        if not isinstance(subject, ProvenanceSubjectRef):
            from .contracts import validation
            raise validation("PV001", "provenance_statement", "subject", "must be ProvenanceSubjectRef")
        from .contracts import text
        normalized_namespace = text(business_namespace, "business_namespace", "provenance_statement_identity")
        normalized_lineage = text(lineage_key, "lineage_key", "provenance_statement_identity")
        identity = ProvenanceStatementIdentity(
            statement_id=_calculate_statement_id(
                business_namespace=normalized_namespace,
                lineage_key=normalized_lineage,
                category=category,
                subject=subject,
            ),
            business_namespace=normalized_namespace,
            lineage_key=normalized_lineage,
        )
        return self._build(
            identity=identity,
            category=category,
            subject=subject,
            version=ProvenanceStatementVersion(),
            entities=entities,
            actors=actors,
            activity=activity,
            evidence=evidence,
            predecessors=predecessors,
            qualifiers=qualifiers,
            declared_at=declared_at,
            foundation_version=PROVENANCE_VERSION,
        )

    def from_parts(
        self,
        *,
        identity: ProvenanceStatementIdentity,
        category: ProvenanceStatementCategory,
        subject: ProvenanceSubjectRef,
        version: ProvenanceStatementVersion,
        digest: str,
        entities: Iterable[ProvenanceEntityRef] = (),
        actors: Iterable[ProvenanceActorRef] = (),
        activity: ProvenanceActivityRef | None = None,
        evidence: Iterable[ProvenanceEvidenceRef] = (),
        predecessors: Iterable[ProvenanceStatementRef] = (),
        qualifiers: Iterable[ProvenanceQualifier] = (),
        declared_at: datetime | None = None,
        foundation_version: str = PROVENANCE_VERSION,
    ) -> ProvenanceStatement:
        value = self._build(
            identity=identity,
            category=category,
            subject=subject,
            version=version,
            entities=entities,
            actors=actors,
            activity=activity,
            evidence=evidence,
            predecessors=predecessors,
            qualifiers=qualifiers,
            declared_at=declared_at,
            foundation_version=foundation_version,
        )
        if value.digest != digest:
            raise ProvenanceDigestError("PD001", value.model, "digest", "digest does not match canonical payload")
        return value

    def _build(
        self,
        *,
        identity: ProvenanceStatementIdentity,
        category: ProvenanceStatementCategory,
        subject: ProvenanceSubjectRef,
        version: ProvenanceStatementVersion,
        entities: Iterable[ProvenanceEntityRef],
        actors: Iterable[ProvenanceActorRef],
        activity: ProvenanceActivityRef | None,
        evidence: Iterable[ProvenanceEvidenceRef],
        predecessors: Iterable[ProvenanceStatementRef],
        qualifiers: Iterable[ProvenanceQualifier],
        declared_at: datetime | None,
        foundation_version: str,
    ) -> ProvenanceStatement:
        from .serializer import DeterministicProvenanceSerializer
        from .validator import ProvenanceStatementValidator

        provisional = ProvenanceStatement(
            identity=identity,
            category=category,
            subject=subject,
            version=version,
            digest="0" * 64,
            entities=tuple(entities),
            actors=tuple(actors),
            activity=activity,
            evidence=tuple(evidence),
            predecessors=tuple(predecessors),
            qualifiers=tuple(qualifiers),
            declared_at=declared_at,
            foundation_version=foundation_version,
            _factory_token=_FACTORY_TOKEN,
        )
        validator = ProvenanceStatementValidator()
        validator.validate(value=provisional)
        digest = DeterministicProvenanceSerializer().digest(statement=provisional)
        value = ProvenanceStatement(
            identity=provisional.identity,
            category=provisional.category,
            subject=provisional.subject,
            version=provisional.version,
            digest=digest,
            entities=provisional.entities,
            actors=provisional.actors,
            activity=provisional.activity,
            evidence=provisional.evidence,
            predecessors=provisional.predecessors,
            qualifiers=provisional.qualifiers,
            declared_at=provisional.declared_at,
            foundation_version=provisional.foundation_version,
            _factory_token=_FACTORY_TOKEN,
        )
        validator.validate(value=value)
        return value


__all__ = ["ProvenanceStatementFactory"]
