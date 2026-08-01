"""Typed immutable results for comparison and finite-chain validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .constants import PROVENANCE_SCHEMA_VERSION, PROVENANCE_SERIALIZATION_VERSION
from .contracts import require_versions, text, unique, validation


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceStatementComparisonResult:
    same_identity: bool
    left_node_key: str
    right_node_key: str
    same_digest: bool
    changed_fields: tuple[str, ...] = ()
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_statement_comparison_result"

    def __post_init__(self) -> None:
        for field in ("same_identity", "same_digest"):
            if not isinstance(getattr(self, field), bool):
                raise validation("PV001", self.model, field, "must be bool")
        for field in ("left_node_key", "right_node_key"):
            object.__setattr__(self, field, text(getattr(self, field), field, self.model))
        if not isinstance(self.changed_fields, (tuple, list)):
            raise validation("PV001", self.model, "changed_fields", "must be sequence")
        changed = tuple(sorted(text(item, "changed_fields", self.model) for item in self.changed_fields))
        unique(changed, lambda item: item, "changed_fields", self.model)
        object.__setattr__(self, "changed_fields", changed)
        require_versions(self.schema_version, self.serialization_version, self.model)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProvenanceChainValidationResult:
    node_keys: tuple[str, ...] = ()
    root_keys: tuple[str, ...] = ()
    external_predecessors: tuple[str, ...] = ()
    components: tuple[tuple[str, ...], ...] = ()
    edge_count: int = 0
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    serialization_version: str = PROVENANCE_SERIALIZATION_VERSION
    model: ClassVar[str] = "provenance_chain_validation_result"

    def __post_init__(self) -> None:
        for field in ("node_keys", "root_keys", "external_predecessors"):
            raw = getattr(self, field)
            if not isinstance(raw, (tuple, list)):
                raise validation("PV001", self.model, field, "must be sequence")
            values = tuple(sorted(text(item, field, self.model) for item in raw))
            unique(values, lambda item: item, field, self.model)
            object.__setattr__(self, field, values)
        if not isinstance(self.components, (tuple, list)):
            raise validation("PV001", self.model, "components", "must be sequence")
        components = []
        for component in self.components:
            if not isinstance(component, (tuple, list)):
                raise validation("PV001", self.model, "components", "component must be sequence")
            values = tuple(sorted(text(item, "components", self.model) for item in component))
            unique(values, lambda item: item, "components", self.model)
            components.append(values)
        object.__setattr__(self, "components", tuple(sorted(components)))
        if isinstance(self.edge_count, bool) or not isinstance(self.edge_count, int) or self.edge_count < 0:
            raise validation("PV007", self.model, "edge_count", "must be non-negative integer")
        require_versions(self.schema_version, self.serialization_version, self.model)


__all__ = ["ProvenanceChainValidationResult", "ProvenanceStatementComparisonResult"]
