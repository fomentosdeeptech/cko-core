"""Immutable models for the in-memory Discovery query index foundation."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from .query_index_errors import (
    InvalidLogicalIndexError,
    InvalidLogicalIndexPolicyError,
)


QUERY_INDEX_SCHEMA_VERSION = "1.0"


class IndexStrategy(str, Enum):
    """Canonical logical organization strategies."""

    HASH = "hash"
    ORDERED = "ordered"
    PREFIX = "prefix"
    COMPOSITE = "composite"


class DuplicateBehavior(str, Enum):
    """Policy behavior when a logical identity occurs more than once."""

    REJECT = "reject"
    KEEP_FIRST = "keep_first"
    KEEP_LAST = "keep_last"


def _text(value: object, name: str, error: type[ValueError]) -> str:
    if not isinstance(value, str) or not value.strip():
        raise error(f"{name} must be a non-empty string")
    return value.strip()


def _positive(value: object, name: str, *, allow_zero: bool = False) -> int:
    minimum = 0 if allow_zero else 1
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        qualifier = "non-negative" if allow_zero else "positive"
        raise InvalidLogicalIndexError(f"{name} must be a {qualifier} integer")
    return value


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidLogicalIndexError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidLogicalIndexError("numeric values must be finite")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            normalized = _text(key, "mapping key", InvalidLogicalIndexError)
            frozen[normalized] = _freeze(nested)
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise InvalidLogicalIndexError(
        f"unsupported logical index value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, _IndexModel):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported index serialization value: {type(value).__name__}")


def _envelope(
    payload: Mapping[str, object],
    model: str,
    names: tuple[str, ...],
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise InvalidLogicalIndexError(f"{model} payload must be a mapping")
    expected = {"schema_version", "model", *names}
    actual = set(payload)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        detail = []
        if missing:
            detail.append(f"missing fields: {', '.join(missing)}")
        if unknown:
            detail.append(f"unknown fields: {', '.join(unknown)}")
        raise InvalidLogicalIndexError(
            f"invalid {model} envelope ({'; '.join(detail)})"
        )
    if payload["schema_version"] != QUERY_INDEX_SCHEMA_VERSION:
        raise InvalidLogicalIndexError("unsupported query index schema version")
    if payload["model"] != model:
        raise InvalidLogicalIndexError(f"payload does not represent {model}")
    return {name: payload[name] for name in names}


def _array(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, list):
        raise InvalidLogicalIndexError(f"{name} must be a JSON array")
    return tuple(value)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InvalidLogicalIndexError(f"{name} must be a mapping")
    return value


def _instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise InvalidLogicalIndexError("timestamp must be an ISO-8601 string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidLogicalIndexError("timestamp must be valid ISO-8601") from error


class _IndexModel:
    model_name: ClassVar[str]
    schema_version: ClassVar[str] = QUERY_INDEX_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Serialize this model with the canonical versioned envelope."""
        return {
            "schema_version": self.schema_version,
            "model": self.model_name,
            **{item.name: _primitive(getattr(self, item.name)) for item in fields(self)},
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
            raise InvalidLogicalIndexError("query index JSON is invalid") from error
        if not isinstance(decoded, dict):
            raise InvalidLogicalIndexError("query index JSON must contain an object")
        return cls.from_dict(decoded)


@dataclass(frozen=True, slots=True)
class LogicalIndexEntry(_IndexModel):
    """One immutable association between an identity and an indexed key."""

    model_name: ClassVar[str] = "logical_index_entry"
    logical_identity: str
    indexed_key: object
    attributes: Mapping[str, object]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "logical_identity",
            _text(self.logical_identity, "logical_identity", InvalidLogicalIndexError),
        )
        object.__setattr__(self, "indexed_key", _freeze(self.indexed_key))
        object.__setattr__(self, "attributes", _freeze(self.attributes))
        object.__setattr__(self, "timestamp", _aware(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a logical index entry from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("logical_identity", "indexed_key", "attributes", "timestamp"),
        )
        return cls(
            logical_identity=data["logical_identity"],
            indexed_key=data["indexed_key"],
            attributes=_mapping(data["attributes"], "attributes"),
            timestamp=_instant(data["timestamp"]),
        )


@dataclass(frozen=True, slots=True)
class LogicalIndexStatistics(_IndexModel):
    """Immutable cardinality and distribution metrics for a logical index."""

    model_name: ClassVar[str] = "logical_index_statistics"
    entry_count: int
    distinct_key_count: int
    logical_distribution: Mapping[str, int]
    density: float
    estimates: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        entries = _positive(self.entry_count, "entry_count", allow_zero=True)
        distinct = _positive(
            self.distinct_key_count, "distinct_key_count", allow_zero=True
        )
        if distinct > entries:
            raise InvalidLogicalIndexError(
                "distinct_key_count cannot exceed entry_count"
            )
        distribution = _mapping(self.logical_distribution, "logical_distribution")
        normalized: dict[str, int] = {}
        for key, count in distribution.items():
            normalized[_text(key, "distribution key", InvalidLogicalIndexError)] = (
                _positive(count, "distribution count")
            )
        if sum(normalized.values()) != entries:
            raise InvalidLogicalIndexError(
                "logical distribution must account for every entry"
            )
        if distinct != len(normalized):
            raise InvalidLogicalIndexError(
                "distinct_key_count must match logical distribution"
            )
        if isinstance(self.density, bool) or not isinstance(self.density, (int, float)):
            raise InvalidLogicalIndexError("density must be a finite number")
        density = float(self.density)
        expected = distinct / entries if entries else 0.0
        if not math.isfinite(density) or not math.isclose(density, expected):
            raise InvalidLogicalIndexError("density is inconsistent with cardinality")
        object.__setattr__(self, "logical_distribution", _freeze(normalized))
        object.__setattr__(self, "density", density)
        object.__setattr__(self, "estimates", _freeze(self.estimates))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize logical index statistics from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            (
                "entry_count", "distinct_key_count", "logical_distribution",
                "density", "estimates",
            ),
        )
        return cls(
            entry_count=data["entry_count"],
            distinct_key_count=data["distinct_key_count"],
            logical_distribution=_mapping(
                data["logical_distribution"], "logical_distribution"
            ),
            density=data["density"],
            estimates=_mapping(data["estimates"], "estimates"),
        )


@dataclass(frozen=True, slots=True)
class LogicalIndex(_IndexModel):
    """Immutable, infrastructure-neutral logical index and its entries."""

    model_name: ClassVar[str] = "logical_index"
    id: str
    name: str
    indexed_attributes: tuple[str, ...]
    strategy: IndexStrategy
    logical_cardinality: int
    statistics: LogicalIndexStatistics
    entries: tuple[LogicalIndexEntry, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _text(self.id, "id", InvalidLogicalIndexError))
        object.__setattr__(
            self, "name", _text(self.name, "name", InvalidLogicalIndexError)
        )
        attributes = tuple(
            _text(item, "indexed attribute", InvalidLogicalIndexError)
            for item in self.indexed_attributes
        )
        if not attributes or len(set(attributes)) != len(attributes):
            raise InvalidLogicalIndexError(
                "indexed_attributes must be non-empty and unique"
            )
        try:
            strategy = IndexStrategy(self.strategy)
        except (TypeError, ValueError) as error:
            raise InvalidLogicalIndexError("unsupported index strategy") from error
        if strategy is IndexStrategy.COMPOSITE and len(attributes) < 2:
            raise InvalidLogicalIndexError(
                "composite strategy requires at least two attributes"
            )
        entries = tuple(self.entries)
        if any(not isinstance(item, LogicalIndexEntry) for item in entries):
            raise InvalidLogicalIndexError("entries must be LogicalIndexEntry models")
        cardinality = _positive(
            self.logical_cardinality, "logical_cardinality", allow_zero=True
        )
        if not isinstance(self.statistics, LogicalIndexStatistics):
            raise InvalidLogicalIndexError(
                "statistics must be LogicalIndexStatistics"
            )
        if cardinality != len(entries):
            raise InvalidLogicalIndexError(
                "logical_cardinality must match the number of entries"
            )
        if self.statistics.entry_count != cardinality:
            raise InvalidLogicalIndexError(
                "statistics entry count must match logical_cardinality"
            )
        object.__setattr__(self, "indexed_attributes", attributes)
        object.__setattr__(self, "strategy", strategy)
        object.__setattr__(self, "entries", entries)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a logical index from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            (
                "id", "name", "indexed_attributes", "strategy",
                "logical_cardinality", "statistics", "entries",
            ),
        )
        entries = _array(data["entries"], "entries")
        if any(not isinstance(item, Mapping) for item in entries):
            raise InvalidLogicalIndexError("entries must contain JSON objects")
        return cls(
            id=data["id"], name=data["name"],
            indexed_attributes=tuple(_array(
                data["indexed_attributes"], "indexed_attributes"
            )),
            strategy=data["strategy"],
            logical_cardinality=data["logical_cardinality"],
            statistics=LogicalIndexStatistics.from_dict(
                _mapping(data["statistics"], "statistics")
            ),
            entries=tuple(LogicalIndexEntry.from_dict(item) for item in entries),
        )


@dataclass(frozen=True, slots=True)
class LogicalIndexPolicy(_IndexModel):
    """Immutable limits and deterministic selection policy for indexes."""

    model_name: ClassVar[str] = "logical_index_policy"
    max_indexes: int = 64
    max_cardinality: int = 1_000_000
    duplicate_behavior: DuplicateBehavior = DuplicateBehavior.REJECT
    default_strategy: IndexStrategy = IndexStrategy.HASH
    selection_rules: tuple[str, ...] = (
        "operator_compatibility", "attribute_coverage", "logical_cost", "index_id",
    )

    def __post_init__(self) -> None:
        try:
            duplicate = DuplicateBehavior(self.duplicate_behavior)
            strategy = IndexStrategy(self.default_strategy)
        except (TypeError, ValueError) as error:
            raise InvalidLogicalIndexPolicyError(
                "policy contains an unsupported enum value"
            ) from error
        if isinstance(self.max_indexes, bool) or not isinstance(self.max_indexes, int):
            raise InvalidLogicalIndexPolicyError("max_indexes must be positive")
        if self.max_indexes < 1:
            raise InvalidLogicalIndexPolicyError("max_indexes must be positive")
        if (
            isinstance(self.max_cardinality, bool)
            or not isinstance(self.max_cardinality, int)
            or self.max_cardinality < 1
        ):
            raise InvalidLogicalIndexPolicyError("max_cardinality must be positive")
        rules = tuple(
            _text(item, "selection rule", InvalidLogicalIndexPolicyError)
            for item in self.selection_rules
        )
        if not rules or len(set(rules)) != len(rules):
            raise InvalidLogicalIndexPolicyError(
                "selection_rules must be non-empty and unique"
            )
        object.__setattr__(self, "duplicate_behavior", duplicate)
        object.__setattr__(self, "default_strategy", strategy)
        object.__setattr__(self, "selection_rules", rules)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize an index policy from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            (
                "max_indexes", "max_cardinality", "duplicate_behavior",
                "default_strategy", "selection_rules",
            ),
        )
        return cls(
            max_indexes=data["max_indexes"],
            max_cardinality=data["max_cardinality"],
            duplicate_behavior=data["duplicate_behavior"],
            default_strategy=data["default_strategy"],
            selection_rules=tuple(_array(data["selection_rules"], "selection_rules")),
        )


@dataclass(frozen=True, slots=True)
class DiscardedLogicalIndex(_IndexModel):
    """Auditable explanation for an index rejected during resolution."""

    model_name: ClassVar[str] = "discarded_logical_index"
    index_id: str
    reason: str
    estimated_cost: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "index_id", _text(self.index_id, "index_id", InvalidLogicalIndexError)
        )
        object.__setattr__(
            self, "reason", _text(self.reason, "reason", InvalidLogicalIndexError)
        )
        cost = float(self.estimated_cost)
        if not math.isfinite(cost) or cost < 0:
            raise InvalidLogicalIndexError("estimated_cost must be non-negative")
        object.__setattr__(self, "estimated_cost", cost)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a discarded-index explanation."""
        return cls(**_envelope(
            payload, cls.model_name, ("index_id", "reason", "estimated_cost")
        ))


@dataclass(frozen=True, slots=True)
class LogicalIndexReport(_IndexModel):
    """Immutable and auditable result of automatic index resolution."""

    model_name: ClassVar[str] = "logical_index_report"
    selected_index_id: str | None
    justification: str
    discarded_indexes: tuple[DiscardedLogicalIndex, ...]
    estimated_logical_cost: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.selected_index_id is not None:
            object.__setattr__(
                self, "selected_index_id",
                _text(
                    self.selected_index_id, "selected_index_id",
                    InvalidLogicalIndexError,
                ),
            )
        object.__setattr__(
            self, "justification",
            _text(self.justification, "justification", InvalidLogicalIndexError),
        )
        discarded = tuple(self.discarded_indexes)
        if any(not isinstance(item, DiscardedLogicalIndex) for item in discarded):
            raise InvalidLogicalIndexError(
                "discarded_indexes must contain canonical models"
            )
        cost = float(self.estimated_logical_cost)
        if not math.isfinite(cost) or cost < 0:
            raise InvalidLogicalIndexError(
                "estimated_logical_cost must be non-negative"
            )
        object.__setattr__(self, "discarded_indexes", discarded)
        object.__setattr__(self, "estimated_logical_cost", cost)
        object.__setattr__(self, "timestamp", _aware(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize an index resolution report from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            (
                "selected_index_id", "justification", "discarded_indexes",
                "estimated_logical_cost", "timestamp",
            ),
        )
        discarded = _array(data["discarded_indexes"], "discarded_indexes")
        if any(not isinstance(item, Mapping) for item in discarded):
            raise InvalidLogicalIndexError(
                "discarded_indexes must contain JSON objects"
            )
        return cls(
            selected_index_id=data["selected_index_id"],
            justification=data["justification"],
            discarded_indexes=tuple(
                DiscardedLogicalIndex.from_dict(item) for item in discarded
            ),
            estimated_logical_cost=data["estimated_logical_cost"],
            timestamp=_instant(data["timestamp"]),
        )


@dataclass(frozen=True, slots=True)
class QueryIndexPlan(_IndexModel):
    """Immutable plan describing how a query should use a logical index."""

    model_name: ClassVar[str] = "query_index_plan"
    query_id: str
    selected_index_id: str | None
    matched_attributes: tuple[str, ...]
    estimated_logical_cost: float
    justifications: tuple[str, ...]
    resolution_report: LogicalIndexReport
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "query_id", _text(self.query_id, "query_id", InvalidLogicalIndexError)
        )
        if self.selected_index_id is not None:
            object.__setattr__(
                self, "selected_index_id",
                _text(
                    self.selected_index_id, "selected_index_id",
                    InvalidLogicalIndexError,
                ),
            )
        attributes = tuple(
            _text(item, "matched attribute", InvalidLogicalIndexError)
            for item in self.matched_attributes
        )
        reasons = tuple(
            _text(item, "justification", InvalidLogicalIndexError)
            for item in self.justifications
        )
        if not reasons:
            raise InvalidLogicalIndexError("justifications must not be empty")
        if not isinstance(self.resolution_report, LogicalIndexReport):
            raise InvalidLogicalIndexError(
                "resolution_report must be LogicalIndexReport"
            )
        cost = float(self.estimated_logical_cost)
        if not math.isfinite(cost) or cost < 0:
            raise InvalidLogicalIndexError(
                "estimated_logical_cost must be non-negative"
            )
        if self.selected_index_id != self.resolution_report.selected_index_id:
            raise InvalidLogicalIndexError(
                "selected index must agree with the resolution report"
            )
        object.__setattr__(self, "matched_attributes", attributes)
        object.__setattr__(self, "justifications", reasons)
        object.__setattr__(self, "estimated_logical_cost", cost)
        object.__setattr__(self, "timestamp", _aware(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a query index plan from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            (
                "query_id", "selected_index_id", "matched_attributes",
                "estimated_logical_cost", "justifications",
                "resolution_report", "timestamp",
            ),
        )
        return cls(
            query_id=data["query_id"], selected_index_id=data["selected_index_id"],
            matched_attributes=tuple(_array(
                data["matched_attributes"], "matched_attributes"
            )),
            estimated_logical_cost=data["estimated_logical_cost"],
            justifications=tuple(_array(data["justifications"], "justifications")),
            resolution_report=LogicalIndexReport.from_dict(
                _mapping(data["resolution_report"], "resolution_report")
            ),
            timestamp=_instant(data["timestamp"]),
        )


__all__ = [
    "DiscardedLogicalIndex",
    "DuplicateBehavior",
    "IndexStrategy",
    "LogicalIndex",
    "LogicalIndexEntry",
    "LogicalIndexPolicy",
    "LogicalIndexReport",
    "LogicalIndexStatistics",
    "QUERY_INDEX_SCHEMA_VERSION",
    "QueryIndexPlan",
]
