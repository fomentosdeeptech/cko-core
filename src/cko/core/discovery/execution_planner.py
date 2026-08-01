"""Deterministic construction and validation of physical execution plans."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from cko.core.logging import get_logger

from .execution_errors import ExecutionPlanningError, ExecutionValidationError
from .execution_models import (
    CompositeIndexScanNode,
    ExecutionContext,
    ExecutionMetrics,
    ExecutionNode,
    ExecutionNodeType,
    ExecutionPlan,
    ExecutionReport,
    FilterNode,
    IndexScanNode,
    LimitNode,
    OrderedScanNode,
    PrefixScanNode,
    ProjectionNode,
    RootNode,
    ScanNode,
    SortNode,
)
from .planner_models import QueryExecutionPlan, QueryExecutionStrategy


EXECUTION_PLANNER_VERSION = "1.0.0"


def _event(logger: object, name: str, **context: object) -> None:
    getattr(logger, "info")(
        name,
        extra={
            "event": f"discovery.query.execution_planner.{name}",
            "context": dict(sorted(context.items())),
        },
    )


def _json(value: object) -> str:
    return json.dumps(
        value, allow_nan=False, ensure_ascii=False,
        separators=(",", ":"), sort_keys=True,
    )


def _digest(prefix: str, value: object) -> str:
    encoded = _json(value).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()}"


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _pagination(plan: QueryExecutionPlan) -> Mapping[str, object] | None:
    pagination = plan.query_plan.pagination
    if pagination is None:
        return None
    offset = pagination.offset
    limit = pagination.limit
    if pagination.page is not None and pagination.page_size is not None:
        page_offset = (pagination.page - 1) * pagination.page_size
        offset = page_offset if offset is None else offset
        limit = pagination.page_size if limit is None else limit
    return {"limit": limit, "offset": offset}


@dataclass(frozen=True, slots=True)
class _NodeSpec:
    node_class: type[ExecutionNode]
    metadata: Mapping[str, object]


_ACCESS_NODES: dict[QueryExecutionStrategy, type[ExecutionNode]] = {
    QueryExecutionStrategy.FULL_SCAN: ScanNode,
    QueryExecutionStrategy.INDEX_SCAN: IndexScanNode,
    QueryExecutionStrategy.COMPOSITE_INDEX_SCAN: CompositeIndexScanNode,
    QueryExecutionStrategy.PREFIX_INDEX_SCAN: PrefixScanNode,
    QueryExecutionStrategy.ORDERED_INDEX_SCAN: OrderedScanNode,
}


class ExecutionPlanValidator:
    """Validate tree, cycles, parent links, metadata and physical strategy."""

    def validate(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Return a valid plan or raise a precise structural error."""
        if not isinstance(plan, ExecutionPlan):
            raise ExecutionValidationError("plan must be ExecutionPlan")
        root = plan.root_node
        if root.parent is not None:
            raise ExecutionValidationError("root node cannot have a parent")
        if len(root.children) != 1:
            raise ExecutionValidationError("root node must have exactly one child")
        seen_ids: set[str] = set()
        active_objects: set[int] = set()
        nodes: list[ExecutionNode] = []

        def visit(node: ExecutionNode, expected_parent: str | None) -> None:
            identity = id(node)
            if identity in active_objects:
                raise ExecutionValidationError("execution tree contains a cycle")
            if node.node_id in seen_ids:
                raise ExecutionValidationError("execution node ids must be unique")
            if node.parent != expected_parent:
                raise ExecutionValidationError("execution parent link is invalid")
            if not isinstance(node.metadata, Mapping):
                raise ExecutionValidationError("execution metadata is invalid")
            if node.node_type is ExecutionNodeType.ROOT:
                if node is not root:
                    raise ExecutionValidationError("execution tree has multiple roots")
            elif node.node_type in {
                ExecutionNodeType.SCAN, ExecutionNodeType.INDEX_SCAN,
                ExecutionNodeType.COMPOSITE_INDEX_SCAN,
                ExecutionNodeType.PREFIX_SCAN, ExecutionNodeType.ORDERED_SCAN,
            }:
                if node.children:
                    raise ExecutionValidationError("scan nodes cannot have children")
            elif len(node.children) != 1:
                raise ExecutionValidationError(
                    "physical operation nodes must have exactly one child"
                )
            seen_ids.add(node.node_id)
            active_objects.add(identity)
            nodes.append(node)
            for child in node.children:
                visit(child, node.node_id)
            active_objects.remove(identity)

        visit(root, None)
        access = [node for node in nodes if node.node_type in {
            ExecutionNodeType.SCAN, ExecutionNodeType.INDEX_SCAN,
            ExecutionNodeType.COMPOSITE_INDEX_SCAN,
            ExecutionNodeType.PREFIX_SCAN, ExecutionNodeType.ORDERED_SCAN,
        }]
        if len(access) != 1:
            raise ExecutionValidationError(
                "execution tree must contain exactly one access node"
            )
        expected = _ACCESS_NODES[plan.execution_strategy]
        if not isinstance(access[0], expected):
            raise ExecutionValidationError(
                "access node does not match execution strategy"
            )
        required_metadata = {"query_execution_plan_id", "report", "metrics"}
        if not required_metadata <= set(plan.metadata):
            raise ExecutionValidationError("execution plan metadata is incomplete")
        report = ExecutionReport.from_dict(
            _thaw(plan.metadata["report"])
        )
        metrics = ExecutionMetrics.from_dict(
            _thaw(plan.metadata["metrics"])
        )
        if report.tree_created != root or report.nodes_created != tuple(
            node.node_id for node in nodes
        ):
            raise ExecutionValidationError("execution report does not match tree")
        if report.strategy is not plan.execution_strategy:
            raise ExecutionValidationError("execution report strategy is invalid")
        if metrics.nodes_created != len(nodes):
            raise ExecutionValidationError("execution metrics node count is invalid")
        if metrics.maximum_depth != self.maximum_depth(root):
            raise ExecutionValidationError("execution metrics depth is invalid")
        return plan

    def is_valid(self, plan: object) -> bool:
        """Return whether an object is a valid physical execution plan."""
        try:
            self.validate(plan)  # type: ignore[arg-type]
        except (ExecutionValidationError, ValueError, TypeError, KeyError):
            return False
        return True

    @staticmethod
    def maximum_depth(root: ExecutionNode) -> int:
        """Calculate the maximum one-based depth of a physical tree."""
        if not isinstance(root, ExecutionNode):
            raise ExecutionValidationError("root must be ExecutionNode")
        if not root.children:
            return 1
        return 1 + max(ExecutionPlanValidator.maximum_depth(child)
                       for child in root.children)


ExecutionValidator = ExecutionPlanValidator


class ExecutionPipeline:
    """Build a deterministic physical tree without executing a query."""

    def __init__(self) -> None:
        self._logger = get_logger("core.discovery.query.execution_planner")

    def build(
        self, context: ExecutionContext | QueryExecutionPlan,
    ) -> ExecutionPlan:
        """Transform execution-planning input into a validated physical plan."""
        if isinstance(context, QueryExecutionPlan):
            context = ExecutionContext(query_execution_plan=context)
        if not isinstance(context, ExecutionContext):
            raise ExecutionPlanningError(
                "context must be ExecutionContext or QueryExecutionPlan"
            )
        source = context.query_execution_plan
        _event(
            self._logger, "execution_planning_started",
            query_execution_plan_id=source.plan_id,
        )
        specs = self._specifications(source)
        node_ids = tuple(
            _digest("node", {
                "position": position,
                "query_execution_plan_id": source.plan_id,
                "type": spec.node_class.expected_type.value,
                "metadata": spec.metadata,
            })
            for position, spec in enumerate(specs)
        )
        child: ExecutionNode | None = None
        created: list[ExecutionNode] = []
        for position, (spec, node_id) in enumerate(zip(specs, node_ids)):
            parent = node_ids[position + 1] if position + 1 < len(node_ids) else None
            node = spec.node_class(
                node_id=node_id, parent=parent,
                children=() if child is None else (child,),
                metadata=spec.metadata,
            )
            child = node
            created.append(node)
            _event(
                self._logger, "node_created", node_id=node.node_id,
                node_type=node.node_type.value,
            )
        if not isinstance(child, RootNode):
            raise ExecutionPlanningError("physical planning did not produce a root")
        ordered_nodes = tuple(reversed(created))
        report = ExecutionReport(
            tree_created=child,
            nodes_created=tuple(node.node_id for node in ordered_nodes),
            strategy=source.execution_strategy,
            timestamp=source.timestamp,
        )
        metrics = ExecutionMetrics(
            planning_duration=0.0,
            nodes_created=len(ordered_nodes),
            maximum_depth=len(ordered_nodes),
            planning_score=source.confidence,
            metadata={
                "deterministic": True,
                "query_execution_plan_id": source.plan_id,
            },
        )
        metadata = {
            "context": context.to_dict(),
            "deterministic": True,
            "metrics": metrics.to_dict(),
            "query_execution_plan_id": source.plan_id,
            "report": report.to_dict(),
        }
        plan_id = _digest("ep", {
            "execution_strategy": source.execution_strategy.value,
            "planner_version": EXECUTION_PLANNER_VERSION,
            "query_execution_plan_id": source.plan_id,
            "tree": child.to_dict(),
        })
        result = ExecutionPlan(
            plan_id=plan_id,
            root_node=child,
            execution_strategy=source.execution_strategy,
            planner_version=EXECUTION_PLANNER_VERSION,
            timestamp=source.timestamp,
            metadata=metadata,
        )
        _event(self._logger, "validation_started", plan_id=plan_id)
        ExecutionPlanValidator().validate(result)
        _event(
            self._logger, "validation_finished", plan_id=plan_id,
            valid=True,
        )
        _event(
            self._logger, "execution_planning_finished", plan_id=plan_id,
            outcome="planned_without_execution",
        )
        return result

    def plan(
        self, context: ExecutionContext | QueryExecutionPlan,
    ) -> ExecutionPlan:
        """Alias for build, matching the canonical planner vocabulary."""
        return self.build(context)

    @staticmethod
    def report(plan: ExecutionPlan) -> ExecutionReport:
        """Recover the immutable report embedded in a physical plan."""
        if not isinstance(plan, ExecutionPlan):
            raise ExecutionPlanningError("plan must be ExecutionPlan")
        return ExecutionReport.from_dict(_thaw(plan.metadata["report"]))

    @staticmethod
    def metrics(plan: ExecutionPlan) -> ExecutionMetrics:
        """Recover deterministic metrics embedded in a physical plan."""
        if not isinstance(plan, ExecutionPlan):
            raise ExecutionPlanningError("plan must be ExecutionPlan")
        return ExecutionMetrics.from_dict(_thaw(plan.metadata["metrics"]))

    @staticmethod
    def _specifications(plan: QueryExecutionPlan) -> tuple[_NodeSpec, ...]:
        logical = plan.query_plan
        access_metadata: dict[str, object] = {
            "estimated_cost": plan.estimated_cost,
            "estimated_rows": plan.estimated_rows,
            "indexes": list(plan.selected_indexes),
            "query_id": logical.query_id,
        }
        specs = [_NodeSpec(_ACCESS_NODES[plan.execution_strategy], access_metadata)]
        if logical.effective_filters:
            specs.append(_NodeSpec(FilterNode, {
                "filters": [item.to_dict() for item in logical.effective_filters],
            }))
        if logical.projections:
            specs.append(_NodeSpec(ProjectionNode, {
                "projections": [item.to_dict() for item in logical.projections],
            }))
        if logical.ordering:
            specs.append(_NodeSpec(SortNode, {
                "ordering": [item.to_dict() for item in logical.ordering],
            }))
        pagination = _pagination(plan)
        if pagination is not None:
            specs.append(_NodeSpec(LimitNode, pagination))
        specs.append(_NodeSpec(RootNode, {
            "query_execution_plan_id": plan.plan_id,
        }))
        return tuple(specs)


__all__ = [
    "EXECUTION_PLANNER_VERSION", "ExecutionPipeline",
    "ExecutionPlanValidator", "ExecutionValidator",
]
