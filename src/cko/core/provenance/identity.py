"""Deterministic provenance statement identity models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID, uuid5

from .constants import (
    PROVENANCE_SCHEMA_VERSION,
    PROVENANCE_SERIALIZATION_VERSION,
    PROVENANCE_UUID_NAMESPACE,
)
from .contracts import canonical_json, require_versions, text, uuid_value
from .enums import ProvenanceStatementCategory


@dataclass(frozen=True, order=True, slots=True, kw_only=True)
class ProvenanceStatementId:
    value: UUID
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_statement_id"

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", uuid_value(self.value, "value", self.model, version_five=True))
        require_versions(self.schema_version, self.serialization_version, self.model)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceStatementIdentity:
    statement_id: ProvenanceStatementId
    business_namespace: str
    lineage_key: str
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_statement_identity"

    def __post_init__(self) -> None:
        from .errors import ProvenanceIdentityError

        if not isinstance(self.statement_id, ProvenanceStatementId):
            raise ProvenanceIdentityError("PI001", self.model, "statement_id", "must be ProvenanceStatementId")
        object.__setattr__(self, "business_namespace", text(
            self.business_namespace, "business_namespace", self.model,
        ))
        object.__setattr__(self, "lineage_key", text(self.lineage_key, "lineage_key", self.model))
        require_versions(self.schema_version, self.serialization_version, self.model)


def _identity_payload(
    *,
    business_namespace: str,
    lineage_key: str,
    category: ProvenanceStatementCategory,
    subject: object,
) -> dict[str, object]:
    return {
        "business_namespace": business_namespace,
        "category": category.value,
        "kind": "provenance_statement_identity",
        "lineage_key": lineage_key,
        "subject": {
            "namespace": subject.namespace,
            "target_id": subject.target_id,
            "target_type": subject.target_type.value,
        },
    }


def _calculate_statement_id(
    *,
    business_namespace: str,
    lineage_key: str,
    category: ProvenanceStatementCategory,
    subject: object,
) -> ProvenanceStatementId:
    name = canonical_json(_identity_payload(
        business_namespace=business_namespace,
        lineage_key=lineage_key,
        category=category,
        subject=subject,
    )).decode("utf-8")
    return ProvenanceStatementId(value=uuid5(PROVENANCE_UUID_NAMESPACE, name))


__all__ = ["ProvenanceStatementId", "ProvenanceStatementIdentity"]
