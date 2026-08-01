"""Models for deterministic, infrastructure-free physical-plan execution."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Self

from cko.core.discovery.execution_models import ExecutionPlan

from .errors import InvalidExecutionEngineModelError


ENGINE_SCHEMA_VERSION = "1.0"
EXECUTION_ENGINE_VERSION = "1.0.0"


class ExecutionState(str, Enum):
    """Lifecycle states supported by the synchronous execution engine."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


_TRANSITIONS: dict[ExecutionState, frozenset[ExecutionState]] = {
    ExecutionState.CREATED: frozenset({
        ExecutionState.READY, ExecutionState.FAILED, ExecutionState.CANCELLED,
    }),
    ExecutionState.READY: frozenset({
        ExecutionState.RUNNING, ExecutionState.FAILED, ExecutionState.CANCELLED,
    }),
    ExecutionState.RUNNING: frozenset({
        ExecutionState.COMPLETED, ExecutionState.FAILED,
        ExecutionState.CANCELLED,
    }),
    ExecutionState.COMPLETED: frozenset(),
    ExecutionState.FAILED: frozenset(),
    ExecutionState.CANCELLED: frozenset(),
}


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidExecutionEngineModelError(
            f"{name} must be a non-empty string"
        )
    return value.strip()


def _count(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvalidExecutionEngineModelError(f"{name} must be non-negative")
    return value


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidExecutionEngineModelError(f"{name} must be non-negative")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        raise InvalidExecutionEngineModelError(f"{name} must be non-negative")
    return normalized


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidExecutionEngineModelError(
                "metadata numbers must be finite"
            )
        return value
    if isinstance(value, Mapping):
        frozen = {
            _text(key, "metadata key"): _freeze(item)
            for key, item in value.items()
        }
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    raise InvalidExecutionEngineModelError(
        f"unsupported metadata value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, ExecutionPlan):
        return value.to_dict()
    if isinstance(value, ExecutionMetrics):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported engine serialization: {type(value).__name__}")


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InvalidExecutionEngineModelError(f"{name} must be a mapping")
    return value


def _array(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, list):
        raise InvalidExecutionEngineModelError(f"{name} must be a JSON array")
    return tuple(value)


def _decode(payload: str) -> Mapping[str, object]:
    try:
        value = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        raise InvalidExecutionEngineModelError("execution JSON is invalid") from error
    if not isinstance(value, dict):
        raise InvalidExecutionEngineModelError(
            "execution JSON must contain an object"
        )
    return value


def deterministic_execution_id(plan: ExecutionPlan) -> str:
    """Derive a stable execution identifier solely from the physical plan."""
    if not isinstance(plan, ExecutionPlan):
        raise InvalidExecutionEngineModelError("plan must be ExecutionPlan")
    encoded = plan.to_json().encode("utf-8")
    return f"execution-{hashlib.sha256(encoded).hexdigest()}"


@dataclass(slots=True)
class ExecutionContext:
    """Mutable lifecycle context for one deterministic plan execution."""

    execution_plan: ExecutionPlan
    state: ExecutionState = ExecutionState.CREATED
    metadata: Mapping[str, object] = field(default_factory=dict)
    statistics: Mapping[str, object] = field(default_factory=dict)
    execution_id: str | None = None
    execution_stack: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.execution_plan, ExecutionPlan):
            raise InvalidExecutionEngineModelError(
                "execution_plan must be ExecutionPlan"
            )
        try:
            self.state = ExecutionState(self.state)
        except (TypeError, ValueError) as error:
            raise InvalidExecutionEngineModelError(
                "state must be ExecutionState"
            ) from error
        identifier = self.execution_id or deterministic_execution_id(
            self.execution_plan
        )
        self.execution_id = _text(identifier, "execution_id")
        self.metadata = _freeze(_mapping(self.metadata, "metadata"))
        self.statistics = _freeze(_mapping(self.statistics, "statistics"))
        self.execution_stack = tuple(
            _text(item, "execution_stack item")
            for item in self.execution_stack
        )

    def transition_to(self, state: ExecutionState) -> None:
        """Apply a valid lifecycle transition or reject it deterministically."""
        try:
            target = ExecutionState(state)
        except (TypeError, ValueError) as error:
            raise InvalidExecutionEngineModelError(
                "target state must be ExecutionState"
            ) from error
        if target not in _TRANSITIONS[self.state]:
            raise InvalidExecutionEngineModelError(
                f"invalid state transition: {self.state.value} -> {target.value}"
            )
        self.state = target

    def push(self, node_id: str) -> None:
        """Push a node onto the observable execution stack."""
        normalized = _text(node_id, "node_id")
        if normalized in self.execution_stack:
            raise InvalidExecutionEngineModelError(
                "execution stack contains a cycle"
            )
        self.execution_stack = (*self.execution_stack, normalized)

    def pop(self) -> str:
        """Pop and return the current node from the execution stack."""
        if not self.execution_stack:
            raise InvalidExecutionEngineModelError("execution stack is empty")
        node_id = self.execution_stack[-1]
        self.execution_stack = self.execution_stack[:-1]
        return node_id

    def to_dict(self) -> dict[str, object]:
        """Serialize the current context with a versioned envelope."""
        return {
            "schema_version": ENGINE_SCHEMA_VERSION,
            "model": "execution_engine_context",
            "execution_plan": self.execution_plan.to_dict(),
            "state": self.state.value,
            "metadata": _primitive(self.metadata),
            "statistics": _primitive(self.statistics),
            "execution_id": self.execution_id,
            "execution_stack": list(self.execution_stack),
        }

    def to_json(self) -> str:
        """Serialize context to deterministic UTF-8-compatible JSON."""
        return json.dumps(
            self.to_dict(), allow_nan=False, ensure_ascii=False,
            separators=(",", ":"), sort_keys=True,
        )


@dataclass(frozen=True, slots=True)
class ExecutionMetrics:
    """Immutable deterministic metrics for one logical execution."""

    duration: float
    nodes_executed: int
    maximum_depth: int
    warnings: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "duration", _number(self.duration, "duration"))
        nodes = _count(self.nodes_executed, "nodes_executed")
        depth = _count(self.maximum_depth, "maximum_depth")
        if nodes and depth < 1:
            raise InvalidExecutionEngineModelError(
                "maximum_depth must be positive when nodes execute"
            )
        object.__setattr__(self, "nodes_executed", nodes)
        object.__setattr__(self, "maximum_depth", depth)
        object.__setattr__(self, "warnings", tuple(
            _text(item, "warning") for item in self.warnings
        ))
        object.__setattr__(self, "metadata", _freeze(
            _mapping(self.metadata, "metadata")
        ))

    def to_dict(self) -> dict[str, object]:
        """Serialize metrics to primitives."""
        return {
            "duration": self.duration,
            "nodes_executed": self.nodes_executed,
            "maximum_depth": self.maximum_depth,
            "warnings": list(self.warnings),
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize metrics from a strict primitive mapping."""
        data = _mapping(payload, "metrics")
        expected = {
            "duration", "nodes_executed", "maximum_depth", "warnings",
            "metadata",
        }
        if set(data) != expected:
            raise InvalidExecutionEngineModelError("invalid metrics envelope")
        return cls(
            duration=data["duration"],
            nodes_executed=data["nodes_executed"],
            maximum_depth=data["maximum_depth"],
            warnings=tuple(_array(data["warnings"], "warnings")),
            metadata=_mapping(data["metadata"], "metadata"),
        )


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Immutable, versioned outcome of deterministic logical execution."""

    execution_id: str
    success: bool
    executed_nodes: tuple[str, ...]
    skipped_nodes: tuple[str, ...]
    warnings: tuple[str, ...]
    metadata: Mapping[str, object]
    statistics: ExecutionMetrics
    schema_version: str = ENGINE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "execution_id", _text(
            self.execution_id, "execution_id"
        ))
        if not isinstance(self.success, bool):
            raise InvalidExecutionEngineModelError("success must be boolean")
        executed = tuple(
            _text(item, "executed node") for item in self.executed_nodes
        )
        skipped = tuple(
            _text(item, "skipped node") for item in self.skipped_nodes
        )
        if len(set(executed)) != len(executed):
            raise InvalidExecutionEngineModelError(
                "executed_nodes must be unique"
            )
        if len(set(skipped)) != len(skipped) or set(executed) & set(skipped):
            raise InvalidExecutionEngineModelError(
                "skipped_nodes must be unique and disjoint"
            )
        if not isinstance(self.statistics, ExecutionMetrics):
            raise InvalidExecutionEngineModelError(
                "statistics must be ExecutionMetrics"
            )
        object.__setattr__(self, "executed_nodes", executed)
        object.__setattr__(self, "skipped_nodes", skipped)
        object.__setattr__(self, "warnings", tuple(
            _text(item, "warning") for item in self.warnings
        ))
        object.__setattr__(self, "metadata", _freeze(
            _mapping(self.metadata, "metadata")
        ))
        if self.schema_version != ENGINE_SCHEMA_VERSION:
            raise InvalidExecutionEngineModelError(
                "unsupported execution-engine schema version"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize result to a strict, versioned primitive mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "execution_result",
            "execution_id": self.execution_id,
            "success": self.success,
            "executed_nodes": list(self.executed_nodes),
            "skipped_nodes": list(self.skipped_nodes),
            "warnings": list(self.warnings),
            "metadata": _primitive(self.metadata),
            "statistics": self.statistics.to_dict(),
        }

    def to_json(self) -> str:
        """Serialize result to deterministic UTF-8-compatible JSON."""
        return json.dumps(
            self.to_dict(), allow_nan=False, ensure_ascii=False,
            separators=(",", ":"), sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict execution-result mapping."""
        data = _mapping(payload, "execution result")
        expected = {
            "schema_version", "model", "execution_id", "success",
            "executed_nodes", "skipped_nodes", "warnings", "metadata",
            "statistics",
        }
        if set(data) != expected or data.get("model") != "execution_result":
            raise InvalidExecutionEngineModelError(
                "invalid execution result envelope"
            )
        return cls(
            execution_id=data["execution_id"], success=data["success"],
            executed_nodes=tuple(_array(
                data["executed_nodes"], "executed_nodes"
            )),
            skipped_nodes=tuple(_array(
                data["skipped_nodes"], "skipped_nodes"
            )),
            warnings=tuple(_array(data["warnings"], "warnings")),
            metadata=_mapping(data["metadata"], "metadata"),
            statistics=ExecutionMetrics.from_dict(
                _mapping(data["statistics"], "statistics")
            ),
            schema_version=data["schema_version"],
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize an execution result from strict JSON."""
        return cls.from_dict(_decode(payload))


__all__ = [
    "ENGINE_SCHEMA_VERSION", "EXECUTION_ENGINE_VERSION", "ExecutionContext",
    "ExecutionMetrics", "ExecutionResult", "ExecutionState",
    "deterministic_execution_id",
]
