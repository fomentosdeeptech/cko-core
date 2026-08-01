"""Immutable models for deterministic logical query optimization."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from .optimizer_errors import InvalidOptimizerModelError
from .query_models import QueryPlan


OPTIMIZER_SCHEMA_VERSION = "1.0"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidOptimizerModelError(f"{name} must be a non-empty string")
    return value.strip()


def _number(value: object, name: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidOptimizerModelError(f"{name} must be a finite number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < minimum:
        raise InvalidOptimizerModelError(
            f"{name} must be greater than or equal to {minimum}"
        )
    return normalized


def _integer(value: object, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise InvalidOptimizerModelError(
            f"{name} must be an integer greater than or equal to {minimum}"
        )
    return value


def _instant(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidOptimizerModelError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidOptimizerModelError("metadata numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen = {_text(key, "metadata key"): _freeze(item)
                  for key, item in value.items()}
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise InvalidOptimizerModelError(
        f"unsupported optimizer metadata value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, QueryPlan):
        return value.to_dict()
    if isinstance(value, _OptimizerModel):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported optimizer serialization: {type(value).__name__}")


def _envelope(
    payload: Mapping[str, object], model: str, names: tuple[str, ...]
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise InvalidOptimizerModelError(f"{model} payload must be a mapping")
    expected = {"schema_version", "model", *names}
    actual = set(payload)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        details = []
        if missing:
            details.append("missing fields: " + ", ".join(missing))
        if unknown:
            details.append("unknown fields: " + ", ".join(unknown))
        raise InvalidOptimizerModelError(
            f"invalid {model} envelope ({'; '.join(details)})"
        )
    if payload["schema_version"] != OPTIMIZER_SCHEMA_VERSION:
        raise InvalidOptimizerModelError("unsupported optimizer schema version")
    if payload["model"] != model:
        raise InvalidOptimizerModelError(f"payload does not represent {model}")
    return {name: payload[name] for name in names}


def _sequence(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, (list, tuple)):
        raise InvalidOptimizerModelError(f"{name} must be a JSON array")
    return tuple(value)


def _timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise InvalidOptimizerModelError("timestamp must be an ISO-8601 string")
    try:
        return _instant(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError as error:
        raise InvalidOptimizerModelError("timestamp must be valid ISO-8601") from error


class _OptimizerModel:
    model_name: ClassVar[str]
    schema_version: ClassVar[str] = OPTIMIZER_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Serialize this model with the strict optimizer envelope."""
        return {
            "schema_version": self.schema_version,
            "model": self.model_name,
            **{item.name: _primitive(getattr(self, item.name))
               for item in fields(self)},
        }

    def to_json(self) -> str:
        """Serialize this model as deterministic UTF-8-compatible JSON."""
        return json.dumps(
            self.to_dict(), allow_nan=False, ensure_ascii=False,
            separators=(",", ":"), sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize this model from strict JSON."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise InvalidOptimizerModelError("optimizer JSON is invalid") from error
        if not isinstance(decoded, dict):
            raise InvalidOptimizerModelError("optimizer JSON must be an object")
        return cls.from_dict(decoded)


class OptimizationCategory(str, Enum):
    """Stable categories for canonical optimization rules."""

    PREDICATE = "predicate"
    BOOLEAN = "boolean"
    PROJECTION = "projection"
    EXPRESSION = "expression"
    ORDERING = "ordering"
    PAGINATION = "pagination"
    SAFETY = "safety"


class OptimizationDecisionStatus(str, Enum):
    """Outcome recorded for one rule execution."""

    APPLIED = "applied"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class OptimizationDecision(_OptimizerModel):
    """Auditable outcome of applying one rule in one iteration."""

    model_name: ClassVar[str] = "optimization_decision"
    rule_id: str
    rule_name: str
    iteration: int
    status: OptimizationDecisionStatus
    justification: str
    before_fingerprint: str
    after_fingerprint: str

    def __post_init__(self) -> None:
        for name in ("rule_id", "rule_name", "justification",
                     "before_fingerprint", "after_fingerprint"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(self, "iteration", _integer(
            self.iteration, "iteration", minimum=1
        ))
        try:
            status = OptimizationDecisionStatus(self.status)
        except (TypeError, ValueError) as error:
            raise InvalidOptimizerModelError("invalid decision status") from error
        object.__setattr__(self, "status", status)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict optimization decision."""
        names = tuple(item.name for item in fields(cls))
        return cls(**_envelope(payload, cls.model_name, names))


@dataclass(frozen=True, slots=True)
class OptimizationContext(_OptimizerModel):
    """Immutable state passed through the optimization pipeline."""

    model_name: ClassVar[str] = "optimization_context"
    original_plan: QueryPlan
    current_plan: QueryPlan
    statistics: Mapping[str, object] = field(default_factory=dict)
    indexes: tuple[Mapping[str, object], ...] = ()
    history: tuple[OptimizationDecision, ...] = ()
    iterations: int = 0
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.original_plan, QueryPlan):
            raise InvalidOptimizerModelError("original_plan must be QueryPlan")
        if not isinstance(self.current_plan, QueryPlan):
            raise InvalidOptimizerModelError("current_plan must be QueryPlan")
        if not isinstance(self.statistics, Mapping):
            raise InvalidOptimizerModelError("statistics must be a mapping")
        declared_indexes = tuple(self.indexes)
        if any(not isinstance(item, Mapping) for item in declared_indexes):
            raise InvalidOptimizerModelError("indexes must contain mappings")
        decisions = tuple(self.history)
        if any(not isinstance(item, OptimizationDecision) for item in decisions):
            raise InvalidOptimizerModelError("history contains invalid decisions")
        object.__setattr__(self, "statistics", _freeze(self.statistics))
        object.__setattr__(self, "indexes", tuple(_freeze(item)
                                                   for item in declared_indexes))
        object.__setattr__(self, "history", decisions)
        object.__setattr__(self, "iterations", _integer(
            self.iterations, "iterations"
        ))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict optimization context."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        statistics = data["statistics"]
        metadata = data["metadata"]
        if not isinstance(statistics, Mapping) or not isinstance(metadata, Mapping):
            raise InvalidOptimizerModelError("context mappings are invalid")
        indexes = _sequence(data["indexes"], "indexes")
        history = _sequence(data["history"], "history")
        if any(not isinstance(item, Mapping) for item in indexes + history):
            raise InvalidOptimizerModelError("context sequences are invalid")
        return cls(
            original_plan=QueryPlan.from_dict(data["original_plan"]),
            current_plan=QueryPlan.from_dict(data["current_plan"]),
            statistics=statistics,
            indexes=tuple(indexes),
            history=tuple(OptimizationDecision.from_dict(item)
                          for item in history),
            iterations=data["iterations"],
            metadata=metadata,
        )


@dataclass(frozen=True, slots=True)
class OptimizationMetrics(_OptimizerModel):
    """Deterministic metrics for one optimization run."""

    model_name: ClassVar[str] = "optimization_metrics"
    duration: float
    iterations: int
    rules_executed: int
    rules_skipped: int
    convergence: bool
    optimization_score: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "duration", _number(self.duration, "duration"))
        for name in ("iterations", "rules_executed", "rules_skipped"):
            object.__setattr__(self, name, _integer(getattr(self, name), name))
        if not isinstance(self.convergence, bool):
            raise InvalidOptimizerModelError("convergence must be boolean")
        score = _number(self.optimization_score, "optimization_score")
        if score > 1.0:
            raise InvalidOptimizerModelError("optimization_score must be at most 1")
        object.__setattr__(self, "optimization_score", score)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize strict optimizer metrics."""
        names = tuple(item.name for item in fields(cls))
        return cls(**_envelope(payload, cls.model_name, names))


@dataclass(frozen=True, slots=True)
class OptimizationReport(_OptimizerModel):
    """Complete audit report for an optimization run."""

    model_name: ClassVar[str] = "optimization_report"
    rules_executed: tuple[str, ...]
    rules_skipped: tuple[str, ...]
    justifications: tuple[str, ...]
    original_plan: QueryPlan
    final_plan: QueryPlan
    timestamp: datetime

    def __post_init__(self) -> None:
        for name in ("rules_executed", "rules_skipped", "justifications"):
            values = tuple(_text(item, name) for item in getattr(self, name))
            object.__setattr__(self, name, values)
        if not isinstance(self.original_plan, QueryPlan):
            raise InvalidOptimizerModelError("original_plan must be QueryPlan")
        if not isinstance(self.final_plan, QueryPlan):
            raise InvalidOptimizerModelError("final_plan must be QueryPlan")
        object.__setattr__(self, "timestamp", _instant(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict optimization report."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        return cls(
            rules_executed=tuple(_sequence(data["rules_executed"],
                                           "rules_executed")),
            rules_skipped=tuple(_sequence(data["rules_skipped"],
                                          "rules_skipped")),
            justifications=tuple(_sequence(data["justifications"],
                                           "justifications")),
            original_plan=QueryPlan.from_dict(data["original_plan"]),
            final_plan=QueryPlan.from_dict(data["final_plan"]),
            timestamp=_timestamp(data["timestamp"]),
        )


@dataclass(frozen=True, slots=True)
class OptimizationResult(_OptimizerModel):
    """Canonical result retaining both optimized and reversible plans."""

    model_name: ClassVar[str] = "optimization_result"
    original_plan: QueryPlan
    optimized_plan: QueryPlan
    rules_applied: tuple[str, ...]
    rules_skipped: tuple[str, ...]
    total_iterations: int
    optimization_gain: float
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.original_plan, QueryPlan):
            raise InvalidOptimizerModelError("original_plan must be QueryPlan")
        if not isinstance(self.optimized_plan, QueryPlan):
            raise InvalidOptimizerModelError("optimized_plan must be QueryPlan")
        for name in ("rules_applied", "rules_skipped"):
            values = tuple(_text(item, name) for item in getattr(self, name))
            object.__setattr__(self, name, values)
        object.__setattr__(self, "total_iterations", _integer(
            self.total_iterations, "total_iterations", minimum=1
        ))
        gain = _number(self.optimization_gain, "optimization_gain")
        if gain > 1.0:
            raise InvalidOptimizerModelError("optimization_gain must be at most 1")
        object.__setattr__(self, "optimization_gain", gain)
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def revert(self) -> QueryPlan:
        """Return the retained original plan without mutating either plan."""
        return self.original_plan

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict optimization result."""
        names = tuple(item.name for item in fields(cls))
        data = _envelope(payload, cls.model_name, names)
        metadata = data["metadata"]
        if not isinstance(metadata, Mapping):
            raise InvalidOptimizerModelError("metadata must be a mapping")
        return cls(
            original_plan=QueryPlan.from_dict(data["original_plan"]),
            optimized_plan=QueryPlan.from_dict(data["optimized_plan"]),
            rules_applied=tuple(_sequence(data["rules_applied"],
                                          "rules_applied")),
            rules_skipped=tuple(_sequence(data["rules_skipped"],
                                          "rules_skipped")),
            total_iterations=data["total_iterations"],
            optimization_gain=data["optimization_gain"],
            metadata=metadata,
        )


__all__ = [
    "OPTIMIZER_SCHEMA_VERSION", "OptimizationCategory", "OptimizationContext",
    "OptimizationDecision", "OptimizationDecisionStatus", "OptimizationMetrics",
    "OptimizationReport", "OptimizationResult",
]
