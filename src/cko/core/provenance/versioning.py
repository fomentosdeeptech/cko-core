"""Logical statement revision model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .constants import PROVENANCE_SCHEMA_VERSION, PROVENANCE_SERIALIZATION_VERSION
from .contracts import positive_int, require_versions, semver
from .references import ProvenanceStatementRef


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceStatementVersion:
    statement_version: str = "1.0.0"
    revision: int = 1
    previous_revision: ProvenanceStatementRef | None = None
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_statement_version"

    def __post_init__(self) -> None:
        from .errors import ProvenanceVersionError

        object.__setattr__(self, "revision", positive_int(self.revision, "revision", self.model))
        object.__setattr__(self, "statement_version", semver(
            self.statement_version, "statement_version", self.model,
        ))
        expected = f"1.0.{self.revision - 1}"
        if self.statement_version != expected:
            raise ProvenanceVersionError("PR001", self.model, "statement_version", f"must be {expected}")
        if self.revision == 1 and self.previous_revision is not None:
            raise ProvenanceVersionError("PR002", self.model, "previous_revision", "root must not have previous revision")
        if self.revision > 1:
            if not isinstance(self.previous_revision, ProvenanceStatementRef):
                raise ProvenanceVersionError("PR002", self.model, "previous_revision", "revision requires previous reference")
            if self.previous_revision.revision != self.revision - 1:
                raise ProvenanceVersionError("PR002", self.model, "previous_revision", "must reference revision n-1")
        require_versions(self.schema_version, self.serialization_version, self.model)


__all__ = ["ProvenanceStatementVersion"]
