"""Immutable models for deterministic cost-based query planning."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from .planner_errors import InvalidPlannerModelError
from .query_models import QueryPlan


PLANNER_SCHEMA_VERSION = "1.0"


class QueryExecutionStrategy(str, Enum):
    """Canonical logical strategies available to the execution planner."""

    FULL_SCAN = "full_scan"
    INDEX_SCAN = "index_scan"
    COMPOSITE_INDEX_SCAN = "composite_index_scan"
    PREFIX_INDEX_SCAN = "prefix_index_scan"
    ORDERED_INDEX_SCAN = "ordered_index_scan"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidPlannerModelError(f"{name} must be a non-empty string")
    return value.strip()


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidPlannerModelError(f"{name} must be a non-negative number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        raise InvalidPlannerModelError(f"{name} must be a non-negative number")
    return normalized


def _ratio(value: object, name: str) -> float:
    normalized = _number(value, name)
    if normalized > 1:
        raise InvalidPlannerModelError(f"{name} must be between zero and one")
    return normalized


def _count(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvalidPlannerModelError(f"{name} must be a non-negative integer")
    return value


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidPlannerModelError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidPlannerModelError("metadata numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen = {_text(key, "metadata key"): _freeze(item)
                  for key, item in value.items()}
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise InvalidPlannerModelError(
        f"unsupported planner metadata value: {type(value).__name__}"
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
    if isinstance(value, _PlannerModel):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported planner serialization: {type(value).__name__}")


def _envelope(
    payload: Mapping[str, object],
    model: str,
    names: tuple[str, ...],
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise InvalidPlannerModelError(f"{model} payload must be a mapping")
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
        raise InvalidPlannerModelError(
            f"invalid {model} envelope ({'; '.join(details)})"
        )
    if payload["schema_version"] != PLANNER_SCHEMA_VERSION:
        raise InvalidPlannerModelError("unsupported planner schema version")
    if payload["model"] != model:
        raise InvalidPlannerModelError(f"payload does not represent {model}")
    return {name: payload[name] for name in names}


def _array(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, list):
        raise InvalidPlannerModelError(f"{name} must be a JSON array")
    return tuple(value)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InvalidPlannerModelError(f"{name} must be a mapping")
    return value


def _instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise InvalidPlannerModelError("timestamp must be an ISO-8601 string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidPlannerModelError("timestamp must be valid ISO-8601") from error


def _strings(value: object, name: str) -> tuple[str, ...]:
    return tuple(_text(item, f"{name} item") for item in value)


def _strategies(value: object, name: str) -> tuple[QueryExecutionStrategy, ...]:
    try:
        strategies = tuple(QueryExecutionStrategy(item) for item in value)
    except (TypeError, ValueError) as error:
        raise InvalidPlannerModelError(f"{name} contains an invalid strategy") from error
    if len(set(strategies)) != len(strategies):
        raise InvalidPlannerModelError(f"{name} must not contain duplicates")
    return strategies


class _PlannerModel:
    model_name: ClassVar[str]
    schema_version: ClassVar[str] = PLANNER_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Serialize this model with its strict versioned envelope."""
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
            raise InvalidPlannerModelError("planner JSON is invalid") from error
        if not isinstance(decoded, dict):
            raise InvalidPlannerModelError("planner JSON must contain an object")
        return cls.from_dict(decoded)


@dataclass(frozen=True, slots=True)
class PlannerWeights(_PlannerModel):
    """Normalized decision weights used to compare logical candidates."""

    model_name: ClassVar[str] = "planner_weights"
    selectivity: float = 1.0
    cardinality: float = 1.0
    cost: float = 2.0
    coverage: float = 1.5
    density: float = 0.5
    confidence: float = 1.0

    def __post_init__(self) -> None:
        for item in fields(self):
            object.__setattr__(
                self, item.name, _number(getattr(self, item.name), item.name)
            )
        if self.total == 0:
            raise InvalidPlannerModelError("at least one planner weight must be positive")

    @property
    def total(self) -> float:
        """Return the sum used to normalize candidate scores."""
        return sum(getattr(self, item.name) for item in fields(self))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize planner weights from a strict mapping."""
        return cls(**_envelope(
            payload, cls.model_name,
            ("selectivity", "cardinality", "cost", "coverage", "density",
             "confidence"),
        ))


@dataclass(frozen=True, slots=True)
class PlannerPolicy(_PlannerModel):
    """Limits and deterministic preferences for cost-based planning."""

    model_name: ClassVar[str] = "planner_policy"
    max_acceptable_cost: float = 1_000_000_000.0
    minimum_confidence: float = 0.25
    allow_full_scan: bool = True
    allow_multiple_indexes: bool = False
    index_limit: int = 1
    default_strategy: QueryExecutionStrategy = QueryExecutionStrategy.FULL_SCAN
    weights: PlannerWeights = field(default_factory=PlannerWeights)

    def __post_init__(self) -> None:
        cost = _number(self.max_acceptable_cost, "max_acceptable_cost")
        if cost == 0:
            raise InvalidPlannerModelError("max_acceptable_cost must be positive")
        confidence = _ratio(self.minimum_confidence, "minimum_confidence")
        if not isinstance(self.allow_full_scan, bool):
            raise InvalidPlannerModelError("allow_full_scan must be boolean")
        if not isinstance(self.allow_multiple_indexes, bool):
            raise InvalidPlannerModelError("allow_multiple_indexes must be boolean")
        if isinstance(self.index_limit, bool) or not isinstance(self.index_limit, int):
            raise InvalidPlannerModelError("index_limit must be a positive integer")
        if self.index_limit < 1:
            raise InvalidPlannerModelError("index_limit must be a positive integer")
        try:
            strategy = QueryExecutionStrategy(self.default_strategy)
        except (TypeError, ValueError) as error:
            raise InvalidPlannerModelError("default_strategy is invalid") from error
        if not isinstance(self.weights, PlannerWeights):
            raise InvalidPlannerModelError("weights must be PlannerWeights")
        if not self.allow_multiple_indexes and self.index_limit != 1:
            raise InvalidPlannerModelError(
                "index_limit must be one when multiple indexes are disabled"
            )
        object.__setattr__(self, "max_acceptable_cost", cost)
        object.__setattr__(self, "minimum_confidence", confidence)
        object.__setattr__(self, "default_strategy", strategy)

    @property
    def decision_weights(self) -> PlannerWeights:
        """Expose the canonical decision weights with an explicit name."""
        return self.weights

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a planner policy from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("max_acceptable_cost", "minimum_confidence", "allow_full_scan",
             "allow_multiple_indexes", "index_limit", "default_strategy", "weights"),
        )
        data["weights"] = PlannerWeights.from_dict(_mapping(data["weights"], "weights"))
        return cls(**data)


@dataclass(frozen=True, slots=True)
class PlannerDecision(_PlannerModel):
    """Auditable explanation of a planner candidate decision."""

    model_name: ClassVar[str] = "planner_decision"
    strategy: QueryExecutionStrategy
    justification: str
    discarded_strategies: tuple[QueryExecutionStrategy, ...]
    discarded_indexes: tuple[str, ...]
    confidence: float
    estimated_gain: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        try:
            strategy = QueryExecutionStrategy(self.strategy)
        except (TypeError, ValueError) as error:
            raise InvalidPlannerModelError("strategy is invalid") from error
        discarded = _strategies(self.discarded_strategies, "discarded_strategies")
        if strategy in discarded:
            raise InvalidPlannerModelError("chosen strategy cannot be discarded")
        indexes = _strings(self.discarded_indexes, "discarded_indexes")
        if len(set(indexes)) != len(indexes):
            raise InvalidPlannerModelError("discarded_indexes must be unique")
        object.__setattr__(self, "strategy", strategy)
        object.__setattr__(self, "justification", _text(
            self.justification, "justification"
        ))
        object.__setattr__(self, "discarded_strategies", discarded)
        object.__setattr__(self, "discarded_indexes", indexes)
        object.__setattr__(self, "confidence", _ratio(self.confidence, "confidence"))
        object.__setattr__(self, "estimated_gain", _number(
            self.estimated_gain, "estimated_gain"
        ))
        object.__setattr__(self, "timestamp", _aware(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a planner decision from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("strategy", "justification", "discarded_strategies",
             "discarded_indexes", "confidence", "estimated_gain", "timestamp"),
        )
        data["discarded_strategies"] = _array(
            data["discarded_strategies"], "discarded_strategies"
        )
        data["discarded_indexes"] = _array(
            data["discarded_indexes"], "discarded_indexes"
        )
        data["timestamp"] = _instant(data["timestamp"])
        return cls(**data)


@dataclass(frozen=True, slots=True)
class PlannerMetrics(_PlannerModel):
    """Deterministic accounting metrics for one planning operation."""

    model_name: ClassVar[str] = "planner_metrics"
    planning_duration: float
    indexes_evaluated: int
    strategies_evaluated: int
    total_candidates: int
    chosen_candidate: str
    discarded_candidates: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "planning_duration", _number(
            self.planning_duration, "planning_duration"
        ))
        for name in (
            "indexes_evaluated", "strategies_evaluated", "total_candidates"
        ):
            object.__setattr__(self, name, _count(getattr(self, name), name))
        discarded = _strings(self.discarded_candidates, "discarded_candidates")
        if self.total_candidates != 1 + len(discarded):
            raise InvalidPlannerModelError(
                "total_candidates must account for chosen and discarded candidates"
            )
        object.__setattr__(self, "chosen_candidate", _text(
            self.chosen_candidate, "chosen_candidate"
        ))
        object.__setattr__(self, "discarded_candidates", discarded)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize planner metrics from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("planning_duration", "indexes_evaluated", "strategies_evaluated",
             "total_candidates", "chosen_candidate", "discarded_candidates"),
        )
        data["discarded_candidates"] = _array(
            data["discarded_candidates"], "discarded_candidates"
        )
        return cls(**data)


@dataclass(frozen=True, slots=True)
class PlannerReport(_PlannerModel):
    """Canonical report of chosen and discarded planning alternatives."""

    model_name: ClassVar[str] = "planner_report"
    chosen_strategy: QueryExecutionStrategy
    discarded_strategies: tuple[QueryExecutionStrategy, ...]
    indexes_used: tuple[str, ...]
    discarded_indexes: tuple[str, ...]
    justifications: tuple[str, ...]
    statistics_used: tuple[str, ...]
    final_cost: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        try:
            chosen = QueryExecutionStrategy(self.chosen_strategy)
        except (TypeError, ValueError) as error:
            raise InvalidPlannerModelError("chosen_strategy is invalid") from error
        discarded = _strategies(self.discarded_strategies, "discarded_strategies")
        if chosen in discarded:
            raise InvalidPlannerModelError("chosen strategy cannot be discarded")
        indexes = _strings(self.indexes_used, "indexes_used")
        rejected = _strings(self.discarded_indexes, "discarded_indexes")
        if set(indexes) & set(rejected):
            raise InvalidPlannerModelError("used indexes cannot also be discarded")
        reasons = _strings(self.justifications, "justifications")
        statistics = _strings(self.statistics_used, "statistics_used")
        if not reasons or not statistics:
            raise InvalidPlannerModelError(
                "report requires justifications and statistics_used"
            )
        object.__setattr__(self, "chosen_strategy", chosen)
        object.__setattr__(self, "discarded_strategies", discarded)
        object.__setattr__(self, "indexes_used", indexes)
        object.__setattr__(self, "discarded_indexes", rejected)
        object.__setattr__(self, "justifications", reasons)
        object.__setattr__(self, "statistics_used", statistics)
        object.__setattr__(self, "final_cost", _number(self.final_cost, "final_cost"))
        object.__setattr__(self, "timestamp", _aware(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a planner report from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("chosen_strategy", "discarded_strategies", "indexes_used",
             "discarded_indexes", "justifications", "statistics_used",
             "final_cost", "timestamp"),
        )
        for name in (
            "discarded_strategies", "indexes_used", "discarded_indexes",
            "justifications", "statistics_used",
        ):
            data[name] = _array(data[name], name)
        data["timestamp"] = _instant(data["timestamp"])
        return cls(**data)


@dataclass(frozen=True, slots=True)
class QueryExecutionPlan(_PlannerModel):
    """Immutable output of deterministic cost-based query planning."""

    model_name: ClassVar[str] = "query_execution_plan"
    plan_id: str
    query_plan: QueryPlan
    execution_strategy: QueryExecutionStrategy
    selected_indexes: tuple[str, ...]
    estimated_cost: float
    estimated_rows: int
    estimated_selectivity: float
    confidence: float
    planning_time: float
    planner_version: str
    timestamp: datetime
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "plan_id", _text(self.plan_id, "plan_id"))
        if not isinstance(self.query_plan, QueryPlan):
            raise InvalidPlannerModelError("query_plan must be a QueryPlan")
        try:
            strategy = QueryExecutionStrategy(self.execution_strategy)
        except (TypeError, ValueError) as error:
            raise InvalidPlannerModelError("execution_strategy is invalid") from error
        indexes = _strings(self.selected_indexes, "selected_indexes")
        if len(set(indexes)) != len(indexes):
            raise InvalidPlannerModelError("selected_indexes must be unique")
        if strategy is QueryExecutionStrategy.FULL_SCAN and indexes:
            raise InvalidPlannerModelError("full scan cannot select indexes")
        if strategy is not QueryExecutionStrategy.FULL_SCAN and not indexes:
            raise InvalidPlannerModelError("index scan requires selected indexes")
        object.__setattr__(self, "execution_strategy", strategy)
        object.__setattr__(self, "selected_indexes", indexes)
        object.__setattr__(self, "estimated_cost", _number(
            self.estimated_cost, "estimated_cost"
        ))
        object.__setattr__(self, "estimated_rows", _count(
            self.estimated_rows, "estimated_rows"
        ))
        object.__setattr__(self, "estimated_selectivity", _ratio(
            self.estimated_selectivity, "estimated_selectivity"
        ))
        object.__setattr__(self, "confidence", _ratio(self.confidence, "confidence"))
        object.__setattr__(self, "planning_time", _number(
            self.planning_time, "planning_time"
        ))
        object.__setattr__(self, "planner_version", _text(
            self.planner_version, "planner_version"
        ))
        object.__setattr__(self, "timestamp", _aware(self.timestamp))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a query execution plan from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("plan_id", "query_plan", "execution_strategy", "selected_indexes",
             "estimated_cost", "estimated_rows", "estimated_selectivity",
             "confidence", "planning_time", "planner_version", "timestamp",
             "metadata"),
        )
        data["query_plan"] = QueryPlan.from_dict(
            _mapping(data["query_plan"], "query_plan")
        )
        data["selected_indexes"] = _array(data["selected_indexes"], "selected_indexes")
        data["timestamp"] = _instant(data["timestamp"])
        data["metadata"] = _mapping(data["metadata"], "metadata")
        return cls(**data)


__all__ = [
    "PLANNER_SCHEMA_VERSION",
    "PlannerDecision",
    "PlannerMetrics",
    "PlannerPolicy",
    "PlannerReport",
    "PlannerWeights",
    "QueryExecutionPlan",
    "QueryExecutionStrategy",
]
