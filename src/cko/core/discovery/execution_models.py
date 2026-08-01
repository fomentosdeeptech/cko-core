"""Immutable physical-plan models for the canonical execution planner."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from .execution_errors import InvalidExecutionModelError
from .optimizer_models import OptimizationResult
from .planner_models import (
    PlannerDecision,
    QueryExecutionPlan,
    QueryExecutionStrategy,
)
from .statistics_models import LogicalStatistics


EXECUTION_SCHEMA_VERSION = "1.0"


class ExecutionNodeType(str, Enum):
    """Canonical types available in a physical execution tree."""

    SCAN = "scan"
    INDEX_SCAN = "index_scan"
    COMPOSITE_INDEX_SCAN = "composite_index_scan"
    PREFIX_SCAN = "prefix_scan"
    ORDERED_SCAN = "ordered_scan"
    FILTER = "filter"
    PROJECTION = "projection"
    SORT = "sort"
    LIMIT = "limit"
    ROOT = "root"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidExecutionModelError(f"{name} must be a non-empty string")
    return value.strip()


def _count(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvalidExecutionModelError(f"{name} must be non-negative")
    return value


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidExecutionModelError(f"{name} must be non-negative")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        raise InvalidExecutionModelError(f"{name} must be non-negative")
    return normalized


def _instant(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidExecutionModelError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidExecutionModelError("metadata numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen = {_text(key, "metadata key"): _freeze(item)
                  for key, item in value.items()}
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise InvalidExecutionModelError(
        f"unsupported execution metadata value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, ExecutionNode):
        return value.to_dict()
    if isinstance(value, _ExecutionModel):
        return value.to_dict()
    if isinstance(value, (QueryExecutionPlan, OptimizationResult,
                          PlannerDecision, LogicalStatistics)):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported execution serialization: {type(value).__name__}")


def _envelope(
    payload: Mapping[str, object], model: str, names: tuple[str, ...],
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise InvalidExecutionModelError(f"{model} payload must be a mapping")
    expected = {"schema_version", "model", *names}
    actual = set(payload)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown fields: {', '.join(unknown)}")
        raise InvalidExecutionModelError(
            f"invalid {model} envelope ({'; '.join(details)})"
        )
    if payload["schema_version"] != EXECUTION_SCHEMA_VERSION:
        raise InvalidExecutionModelError("unsupported execution schema version")
    if payload["model"] != model:
        raise InvalidExecutionModelError(f"payload does not represent {model}")
    return {name: payload[name] for name in names}


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InvalidExecutionModelError(f"{name} must be a mapping")
    return value


def _array(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, list):
        raise InvalidExecutionModelError(f"{name} must be a JSON array")
    return tuple(value)


def _timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise InvalidExecutionModelError("timestamp must be ISO-8601")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidExecutionModelError("timestamp must be valid ISO-8601") from error


class _ExecutionModel:
    model_name: ClassVar[str]
    schema_version: ClassVar[str] = EXECUTION_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Serialize this model with a strict versioned envelope."""
        return {
            "schema_version": self.schema_version,
            "model": self.model_name,
            **{item.name: _primitive(getattr(self, item.name))
               for item in fields(self)},
        }

    def to_json(self) -> str:
        """Serialize this model to deterministic UTF-8-compatible JSON."""
        return json.dumps(
            self.to_dict(), allow_nan=False, ensure_ascii=False,
            separators=(",", ":"), sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize this model from a strict JSON object."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise InvalidExecutionModelError("execution JSON is invalid") from error
        if not isinstance(decoded, dict):
            raise InvalidExecutionModelError("execution JSON must contain an object")
        return cls.from_dict(decoded)


@dataclass(frozen=True, slots=True)
class ExecutionNode(_ExecutionModel):
    """Abstract immutable node shared by all physical operations."""

    model_name: ClassVar[str] = "execution_node"
    expected_type: ClassVar[ExecutionNodeType | None] = None
    node_id: str
    parent: str | None = None
    children: tuple[ExecutionNode, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)
    node_type: ExecutionNodeType = field(init=False)

    def __post_init__(self) -> None:
        if type(self) is ExecutionNode or self.expected_type is None:
            raise InvalidExecutionModelError("ExecutionNode is abstract")
        object.__setattr__(self, "node_id", _text(self.node_id, "node_id"))
        if self.parent is not None:
            object.__setattr__(self, "parent", _text(self.parent, "parent"))
        descendants = tuple(self.children)
        if any(not isinstance(item, ExecutionNode) for item in descendants):
            raise InvalidExecutionModelError("children must be execution nodes")
        object.__setattr__(self, "children", descendants)
        object.__setattr__(self, "metadata", _freeze(self.metadata))
        object.__setattr__(self, "node_type", self.expected_type)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> ExecutionNode:
        """Deserialize a canonical node and all of its descendants."""
        if not isinstance(payload, Mapping):
            raise InvalidExecutionModelError("execution node must be a mapping")
        if cls is ExecutionNode:
            node_type = payload.get("node_type")
            try:
                concrete = _NODE_CLASSES[ExecutionNodeType(node_type)]
            except (KeyError, TypeError, ValueError) as error:
                raise InvalidExecutionModelError("unknown execution node type") from error
            return concrete.from_dict(payload)
        names = ("node_id", "parent", "children", "metadata", "node_type")
        data = _envelope(payload, cls.model_name, names)
        if data["node_type"] != cls.expected_type.value:
            raise InvalidExecutionModelError("node_type does not match node model")
        raw_children = _array(data["children"], "children")
        return cls(
            node_id=data["node_id"],
            parent=data["parent"],
            children=tuple(ExecutionNode.from_dict(
                _mapping(item, "child")
            ) for item in raw_children),
            metadata=_mapping(data["metadata"], "metadata"),
        )


@dataclass(frozen=True, slots=True)
class ScanNode(ExecutionNode):
    """Physical full-scan operation without executing it."""

    model_name: ClassVar[str] = "scan_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.SCAN


@dataclass(frozen=True, slots=True)
class IndexScanNode(ExecutionNode):
    """Physical single-index scan operation."""

    model_name: ClassVar[str] = "index_scan_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.INDEX_SCAN


@dataclass(frozen=True, slots=True)
class CompositeIndexScanNode(ExecutionNode):
    """Physical composite-index scan operation."""

    model_name: ClassVar[str] = "composite_index_scan_node"
    expected_type: ClassVar[ExecutionNodeType] = (
        ExecutionNodeType.COMPOSITE_INDEX_SCAN
    )


@dataclass(frozen=True, slots=True)
class PrefixScanNode(ExecutionNode):
    """Physical prefix-index scan operation."""

    model_name: ClassVar[str] = "prefix_scan_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.PREFIX_SCAN


@dataclass(frozen=True, slots=True)
class OrderedScanNode(ExecutionNode):
    """Physical ordered-index scan operation."""

    model_name: ClassVar[str] = "ordered_scan_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.ORDERED_SCAN


@dataclass(frozen=True, slots=True)
class FilterNode(ExecutionNode):
    """Physical filter operation over its single child."""

    model_name: ClassVar[str] = "filter_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.FILTER


@dataclass(frozen=True, slots=True)
class ProjectionNode(ExecutionNode):
    """Physical projection operation over its single child."""

    model_name: ClassVar[str] = "projection_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.PROJECTION


@dataclass(frozen=True, slots=True)
class SortNode(ExecutionNode):
    """Physical sort operation over its single child."""

    model_name: ClassVar[str] = "sort_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.SORT


@dataclass(frozen=True, slots=True)
class LimitNode(ExecutionNode):
    """Physical limit and offset operation over its single child."""

    model_name: ClassVar[str] = "limit_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.LIMIT


@dataclass(frozen=True, slots=True)
class RootNode(ExecutionNode):
    """Unique root of a canonical physical execution tree."""

    model_name: ClassVar[str] = "root_node"
    expected_type: ClassVar[ExecutionNodeType] = ExecutionNodeType.ROOT


_NODE_CLASSES: dict[ExecutionNodeType, type[ExecutionNode]] = {
    item.expected_type: item for item in (
        ScanNode, IndexScanNode, CompositeIndexScanNode, PrefixScanNode,
        OrderedScanNode, FilterNode, ProjectionNode, SortNode, LimitNode,
        RootNode,
    )
}


@dataclass(frozen=True, slots=True)
class ExecutionPlan(_ExecutionModel):
    """Immutable and auditable canonical physical execution plan."""

    model_name: ClassVar[str] = "execution_plan"
    plan_id: str
    root_node: RootNode
    execution_strategy: QueryExecutionStrategy
    planner_version: str
    timestamp: datetime
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "plan_id", _text(self.plan_id, "plan_id"))
        if not isinstance(self.root_node, RootNode):
            raise InvalidExecutionModelError("root_node must be RootNode")
        try:
            strategy = QueryExecutionStrategy(self.execution_strategy)
        except (TypeError, ValueError) as error:
            raise InvalidExecutionModelError("execution_strategy is invalid") from error
        object.__setattr__(self, "execution_strategy", strategy)
        object.__setattr__(self, "planner_version", _text(
            self.planner_version, "planner_version"
        ))
        object.__setattr__(self, "timestamp", _instant(self.timestamp))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict physical execution plan."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        root = ExecutionNode.from_dict(_mapping(data["root_node"], "root_node"))
        if not isinstance(root, RootNode):
            raise InvalidExecutionModelError("root_node must represent RootNode")
        return cls(
            plan_id=data["plan_id"], root_node=root,
            execution_strategy=data["execution_strategy"],
            planner_version=data["planner_version"],
            timestamp=_timestamp(data["timestamp"]),
            metadata=_mapping(data["metadata"], "metadata"),
        )


@dataclass(frozen=True, slots=True)
class ExecutionContext(_ExecutionModel):
    """Immutable inputs and audit context for physical planning."""

    model_name: ClassVar[str] = "execution_context"
    query_execution_plan: QueryExecutionPlan
    optimization_result: OptimizationResult | None = None
    planner_decision: PlannerDecision | None = None
    statistics: LogicalStatistics | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.query_execution_plan, QueryExecutionPlan):
            raise InvalidExecutionModelError(
                "query_execution_plan must be QueryExecutionPlan"
            )
        if self.optimization_result is not None and not isinstance(
            self.optimization_result, OptimizationResult
        ):
            raise InvalidExecutionModelError(
                "optimization_result must be OptimizationResult"
            )
        if self.planner_decision is not None and not isinstance(
            self.planner_decision, PlannerDecision
        ):
            raise InvalidExecutionModelError(
                "planner_decision must be PlannerDecision"
            )
        if self.statistics is not None and not isinstance(
            self.statistics, LogicalStatistics
        ):
            raise InvalidExecutionModelError("statistics must be LogicalStatistics")
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict execution context."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        optional = {}
        for name, model in (
            ("optimization_result", OptimizationResult),
            ("planner_decision", PlannerDecision),
            ("statistics", LogicalStatistics),
        ):
            value = data[name]
            optional[name] = None if value is None else model.from_dict(
                _mapping(value, name)
            )
        return cls(
            query_execution_plan=QueryExecutionPlan.from_dict(
                _mapping(data["query_execution_plan"], "query_execution_plan")
            ),
            metadata=_mapping(data["metadata"], "metadata"),
            **optional,
        )


@dataclass(frozen=True, slots=True)
class ExecutionReport(_ExecutionModel):
    """Audit report describing the physical tree produced by planning."""

    model_name: ClassVar[str] = "execution_report"
    tree_created: RootNode
    nodes_created: tuple[str, ...]
    strategy: QueryExecutionStrategy
    timestamp: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.tree_created, RootNode):
            raise InvalidExecutionModelError("tree_created must be RootNode")
        nodes = tuple(_text(item, "nodes_created item")
                      for item in self.nodes_created)
        if not nodes or len(set(nodes)) != len(nodes):
            raise InvalidExecutionModelError("nodes_created must be unique")
        try:
            strategy = QueryExecutionStrategy(self.strategy)
        except (TypeError, ValueError) as error:
            raise InvalidExecutionModelError("strategy is invalid") from error
        object.__setattr__(self, "nodes_created", nodes)
        object.__setattr__(self, "strategy", strategy)
        object.__setattr__(self, "timestamp", _instant(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict execution report."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        root = ExecutionNode.from_dict(
            _mapping(data["tree_created"], "tree_created")
        )
        if not isinstance(root, RootNode):
            raise InvalidExecutionModelError("tree_created must represent RootNode")
        return cls(
            tree_created=root,
            nodes_created=tuple(_array(data["nodes_created"], "nodes_created")),
            strategy=data["strategy"], timestamp=_timestamp(data["timestamp"]),
        )


@dataclass(frozen=True, slots=True)
class ExecutionMetrics(_ExecutionModel):
    """Deterministic metrics for a physical planning operation."""

    model_name: ClassVar[str] = "execution_metrics"
    planning_duration: float
    nodes_created: int
    maximum_depth: int
    planning_score: float
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "planning_duration", _number(
            self.planning_duration, "planning_duration"
        ))
        object.__setattr__(self, "nodes_created", _count(
            self.nodes_created, "nodes_created"
        ))
        depth = _count(self.maximum_depth, "maximum_depth")
        if self.nodes_created and depth < 1:
            raise InvalidExecutionModelError("maximum_depth must be positive")
        score = _number(self.planning_score, "planning_score")
        if score > 1:
            raise InvalidExecutionModelError("planning_score must be at most one")
        object.__setattr__(self, "maximum_depth", depth)
        object.__setattr__(self, "planning_score", score)
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize strict execution metrics."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        data["metadata"] = _mapping(data["metadata"], "metadata")
        return cls(**data)


__all__ = [
    "EXECUTION_SCHEMA_VERSION", "CompositeIndexScanNode", "ExecutionContext",
    "ExecutionMetrics", "ExecutionNode", "ExecutionNodeType", "ExecutionPlan",
    "ExecutionReport", "FilterNode", "IndexScanNode", "LimitNode",
    "OrderedScanNode", "PrefixScanNode", "ProjectionNode", "RootNode",
    "ScanNode", "SortNode",
]
