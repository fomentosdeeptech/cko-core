"""Structural and finite-graph validation for provenance statements."""

from __future__ import annotations

from dataclasses import is_dataclass

from .contracts import require_versions, validation
from .enums import (
    ProvenanceActivityType,
    ProvenanceActorRole,
    ProvenanceEntityRole,
    ProvenanceStatementCategory,
)
from .errors import (
    ProvenanceChainError,
    ProvenanceDigestError,
    ProvenanceIdentityError,
    ProvenanceVersionError,
)
from .identity import _calculate_statement_id
from .models import ProvenanceStatement
from .results import ProvenanceChainValidationResult


_MATRIX = {
    ProvenanceStatementCategory.ORIGIN: (
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.ORIGINAL, ProvenanceEntityRole.SUPPORTING_ENTITY},
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.ORIGINAL},
        {ProvenanceActivityType.GENERATION, ProvenanceActivityType.COPYING, ProvenanceActivityType.OTHER_DECLARED},
        {ProvenanceActorRole.CREATOR, ProvenanceActorRole.PRODUCER, ProvenanceActorRole.RESPONSIBLE_PARTY, ProvenanceActorRole.PUBLISHER},
        False,
    ),
    ProvenanceStatementCategory.ATTRIBUTION: (
        {ProvenanceEntityRole.SUPPORTING_ENTITY},
        set(),
        {ProvenanceActivityType.OTHER_DECLARED},
        {ProvenanceActorRole.CREATOR, ProvenanceActorRole.AUTHOR, ProvenanceActorRole.CONTRIBUTOR, ProvenanceActorRole.RESPONSIBLE_PARTY, ProvenanceActorRole.REVIEWER, ProvenanceActorRole.PUBLISHER},
        False,
    ),
    ProvenanceStatementCategory.DERIVATION: (
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.ORIGINAL, ProvenanceEntityRole.CONTRIBUTING_SOURCE, ProvenanceEntityRole.SUPPORTING_ENTITY},
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.ORIGINAL, ProvenanceEntityRole.CONTRIBUTING_SOURCE},
        {ProvenanceActivityType.TRANSFORMATION, ProvenanceActivityType.ADAPTATION, ProvenanceActivityType.EXTRACTION, ProvenanceActivityType.INCORPORATION, ProvenanceActivityType.COPYING, ProvenanceActivityType.OTHER_DECLARED},
        {ProvenanceActorRole.CONTRIBUTOR, ProvenanceActorRole.PRODUCER, ProvenanceActorRole.RESPONSIBLE_PARTY, ProvenanceActorRole.TRANSFORMER},
        False,
    ),
    ProvenanceStatementCategory.GENERATION: (
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.CONTRIBUTING_SOURCE, ProvenanceEntityRole.SUPPORTING_ENTITY},
        set(),
        {ProvenanceActivityType.GENERATION},
        {ProvenanceActorRole.CREATOR, ProvenanceActorRole.PRODUCER, ProvenanceActorRole.RESPONSIBLE_PARTY},
        True,
    ),
    ProvenanceStatementCategory.TRANSFORMATION: (
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.ORIGINAL, ProvenanceEntityRole.CONTRIBUTING_SOURCE},
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.ORIGINAL, ProvenanceEntityRole.CONTRIBUTING_SOURCE},
        {ProvenanceActivityType.TRANSFORMATION},
        {ProvenanceActorRole.CONTRIBUTOR, ProvenanceActorRole.PRODUCER, ProvenanceActorRole.RESPONSIBLE_PARTY, ProvenanceActorRole.TRANSFORMER},
        True,
    ),
    ProvenanceStatementCategory.ADAPTATION: (
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.ORIGINAL, ProvenanceEntityRole.CONTRIBUTING_SOURCE},
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.ORIGINAL, ProvenanceEntityRole.CONTRIBUTING_SOURCE},
        {ProvenanceActivityType.ADAPTATION},
        {ProvenanceActorRole.AUTHOR, ProvenanceActorRole.CONTRIBUTOR, ProvenanceActorRole.RESPONSIBLE_PARTY, ProvenanceActorRole.TRANSFORMER},
        True,
    ),
    ProvenanceStatementCategory.EXTRACTION: (
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.ORIGINAL},
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.ORIGINAL},
        {ProvenanceActivityType.EXTRACTION},
        {ProvenanceActorRole.CONTRIBUTOR, ProvenanceActorRole.PRODUCER, ProvenanceActorRole.RESPONSIBLE_PARTY, ProvenanceActorRole.TRANSFORMER},
        True,
    ),
    ProvenanceStatementCategory.INCORPORATION: (
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.CONTRIBUTING_SOURCE},
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.INPUT, ProvenanceEntityRole.CONTRIBUTING_SOURCE},
        {ProvenanceActivityType.INCORPORATION},
        {ProvenanceActorRole.CONTRIBUTOR, ProvenanceActorRole.PRODUCER, ProvenanceActorRole.RESPONSIBLE_PARTY, ProvenanceActorRole.TRANSFORMER},
        True,
    ),
    ProvenanceStatementCategory.SOURCE_USAGE: (
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.CONTRIBUTING_SOURCE, ProvenanceEntityRole.SUPPORTING_ENTITY},
        {ProvenanceEntityRole.SOURCE, ProvenanceEntityRole.CONTRIBUTING_SOURCE},
        {ProvenanceActivityType.COPYING, ProvenanceActivityType.OTHER_DECLARED},
        {ProvenanceActorRole.AUTHOR, ProvenanceActorRole.CONTRIBUTOR, ProvenanceActorRole.RESPONSIBLE_PARTY, ProvenanceActorRole.PUBLISHER},
        False,
    ),
}


class ProvenanceStatementValidator:
    """Validate values without I/O, resolution, or mutable state."""

    def validate(self, *, value: object) -> None:
        if not is_dataclass(value) or not hasattr(type(value), "__slots__"):
            raise validation("PV001", "provenance_model", "value", "must be frozen slotted dataclass")
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen:
            raise validation("PV001", "provenance_model", "value", "must be frozen slotted dataclass")
        if not type(value).__module__.startswith("cko.core.provenance."):
            raise validation("PV001", "provenance_model", "value", "must be a closed provenance model")
        require_versions(value.schema_version, value.serialization_version, value.model)
        if isinstance(value, ProvenanceStatement):
            self._validate_statement(value)

    def _validate_statement(self, value: ProvenanceStatement) -> None:
        expected_id = _calculate_statement_id(
            business_namespace=value.identity.business_namespace,
            lineage_key=value.identity.lineage_key,
            category=value.category,
            subject=value.subject,
        )
        if value.identity.statement_id != expected_id:
            raise ProvenanceIdentityError("PI001", value.model, "identity", "statement ID does not match payload")
        previous = value.version.previous_revision
        if previous is not None:
            if previous.statement_id != value.identity.statement_id:
                raise ProvenanceVersionError("PR002", value.model, "previous_revision", "must use same statement ID")
            if previous.digest == value.digest:
                raise ProvenanceVersionError("PR002", value.model, "previous_revision", "digest must differ")
        statement_id = value.identity.statement_id
        if any(item.statement_id == statement_id for item in value.predecessors):
            raise ProvenanceChainError("PC001", value.model, "predecessors", "statement cannot reference itself")
        subject_key = (value.subject.target_type, value.subject.namespace, value.subject.target_id)
        if any((item.target_type, item.namespace, item.target_id) == subject_key for item in value.entities):
            raise validation("PV005", value.model, "entities", "subject cannot also be an entity")
        entity_allowed, entity_required, activity_allowed, actor_allowed, activity_required = _MATRIX[value.category]
        roles = {item.role for item in value.entities}
        if not roles <= entity_allowed or (entity_required and not roles & entity_required):
            raise validation("PV005", value.model, "entities", "category/entity matrix violation")
        if value.category is ProvenanceStatementCategory.ATTRIBUTION and not value.actors:
            raise validation("PV005", value.model, "actors", "attribution requires actor")
        if any(item.role not in actor_allowed for item in value.actors):
            raise validation("PV005", value.model, "actors", "category/actor matrix violation")
        if activity_required and value.activity is None:
            raise validation("PV005", value.model, "activity", "category requires activity")
        if value.activity is not None and value.activity.activity_type not in activity_allowed:
            raise validation("PV005", value.model, "activity", "category/activity matrix violation")

    def validate_chain_in_supplied_set(
        self,
        *,
        statements: object,
    ) -> ProvenanceChainValidationResult:
        if not isinstance(statements, (tuple, list)):
            try:
                values = tuple(statements)
            except TypeError as error:
                raise validation("PV001", "provenance_chain", "statements", "must be iterable") from error
        else:
            values = tuple(statements)
        if any(not isinstance(item, ProvenanceStatement) for item in values):
            raise validation("PV001", "provenance_chain", "statements", "must contain ProvenanceStatement")
        nodes: dict[str, ProvenanceStatement] = {}
        for statement in values:
            self._validate_statement(statement)
            if statement.node_key in nodes:
                raise ProvenanceChainError("PC002", statement.model, "node_key", "duplicate or conflicting node")
            nodes[statement.node_key] = statement
        adjacency: dict[str, set[str]] = {key: set() for key in nodes}
        external: set[str] = set()
        edge_count = 0
        for key, statement in nodes.items():
            refs = list(statement.predecessors)
            if statement.version.previous_revision is not None:
                refs.append(statement.version.previous_revision)
            for ref in refs:
                target = nodes.get(ref.node_key)
                if target is None:
                    external.add(ref.node_key)
                    continue
                if (
                    target.identity.statement_id != ref.statement_id
                    or target.version.revision != ref.revision
                    or target.version.statement_version != ref.statement_version
                    or target.digest != ref.digest
                ):
                    raise ProvenanceChainError("PC003", statement.model, "reference", "found node does not match reference")
                adjacency[key].add(ref.node_key)
                edge_count += 1
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise ProvenanceChainError("PC004", "provenance_chain", "cycle", "cycle in supplied set")
            if node in visited:
                return
            visiting.add(node)
            for target in sorted(adjacency[node]):
                visit(target)
            visiting.remove(node)
            visited.add(node)

        for key in sorted(nodes):
            visit(key)
        undirected = {key: set(targets) for key, targets in adjacency.items()}
        for source, targets in adjacency.items():
            for target in targets:
                undirected[target].add(source)
        components = []
        remaining = set(nodes)
        while remaining:
            seed = min(remaining)
            stack = [seed]
            component: set[str] = set()
            while stack:
                node = stack.pop()
                if node in component:
                    continue
                component.add(node)
                stack.extend(sorted(undirected[node] - component, reverse=True))
            remaining -= component
            components.append(tuple(sorted(component)))
        roots = tuple(sorted(key for key, targets in adjacency.items() if not targets))
        return ProvenanceChainValidationResult(
            node_keys=tuple(sorted(nodes)),
            root_keys=roots,
            external_predecessors=tuple(sorted(external)),
            components=tuple(components),
            edge_count=edge_count,
        )


__all__ = ["ProvenanceStatementValidator"]
