"""Immutable models for Discovery logical statistics and cost estimates."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from .statistics_errors import (
    InvalidStatisticsError,
    InvalidStatisticsPolicyError,
)


STATISTICS_SCHEMA_VERSION = "1.0"


class HistogramPolicy(str, Enum):
    """Canonical in-memory histogram construction policies."""

    EQUAL_WIDTH = "equal_width"
    EQUAL_FREQUENCY = "equal_frequency"


class EstimationStrategy(str, Enum):
    """Canonical logical selectivity estimation strategies."""

    DENSITY = "density"
    HISTOGRAM = "histogram"
    HYBRID = "hybrid"


def _text(value: object, name: str, error: type[ValueError]) -> str:
    if not isinstance(value, str) or not value.strip():
        raise error(f"{name} must be a non-empty string")
    return value.strip()


def _count(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvalidStatisticsError(f"{name} must be a non-negative integer")
    return value


def _ratio(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidStatisticsError(f"{name} must be a finite ratio")
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise InvalidStatisticsError(f"{name} must be between zero and one")
    return result


def _number(value: object, name: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidStatisticsError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise InvalidStatisticsError(f"{name} must be at least {minimum}")
    return result


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidStatisticsError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _value(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise InvalidStatisticsError(
        "statistical range values must be finite scalars or null"
    )


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidStatisticsError("metadata numbers must be finite")
        return value
    if isinstance(value, Mapping):
        normalized = {
            _text(key, "mapping key", InvalidStatisticsError): _freeze(item)
            for key, item in value.items()
        }
        return MappingProxyType(dict(sorted(normalized.items())))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    raise InvalidStatisticsError(
        f"unsupported statistics value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, _StatisticsModel):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported statistics serialization: {type(value).__name__}")


def _envelope(
    payload: Mapping[str, object], model: str, names: tuple[str, ...]
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise InvalidStatisticsError(f"{model} payload must be a mapping")
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
        raise InvalidStatisticsError(
            f"invalid {model} envelope ({'; '.join(details)})"
        )
    if payload["schema_version"] != STATISTICS_SCHEMA_VERSION:
        raise InvalidStatisticsError("unsupported statistics schema version")
    if payload["model"] != model:
        raise InvalidStatisticsError(f"payload does not represent {model}")
    return {name: payload[name] for name in names}


def _array(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, list):
        raise InvalidStatisticsError(f"{name} must be a JSON array")
    return tuple(value)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InvalidStatisticsError(f"{name} must be a mapping")
    return value


def _instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise InvalidStatisticsError("timestamp must be an ISO-8601 string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidStatisticsError("timestamp must be valid ISO-8601") from error


class _StatisticsModel:
    model_name: ClassVar[str]
    schema_version: ClassVar[str] = STATISTICS_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """Serialize this model with its strict versioned envelope."""
        return {
            "schema_version": self.schema_version,
            "model": self.model_name,
            **{item.name: _primitive(getattr(self, item.name)) for item in fields(self)},
        }

    def to_json(self) -> str:
        """Serialize this model as deterministic UTF-8-compatible JSON."""
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
            raise InvalidStatisticsError("statistics JSON is invalid") from error
        if not isinstance(decoded, dict):
            raise InvalidStatisticsError("statistics JSON must contain an object")
        return cls.from_dict(decoded)


@dataclass(frozen=True, slots=True)
class HistogramBucket(_StatisticsModel):
    """One ordered histogram bucket and its cumulative frequency."""

    model_name: ClassVar[str] = "histogram_bucket"
    bucket: int
    range: tuple[object, object]
    frequency: int
    cumulative_frequency: int

    def __post_init__(self) -> None:
        if isinstance(self.bucket, bool) or not isinstance(self.bucket, int):
            raise InvalidStatisticsError("bucket must be a non-negative integer")
        if self.bucket < 0:
            raise InvalidStatisticsError("bucket must be a non-negative integer")
        declared = tuple(self.range)
        if len(declared) != 2:
            raise InvalidStatisticsError("range must contain lower and upper values")
        frequency = _count(self.frequency, "frequency")
        cumulative = _count(self.cumulative_frequency, "cumulative_frequency")
        if cumulative < frequency:
            raise InvalidStatisticsError(
                "cumulative_frequency cannot be below frequency"
            )
        object.__setattr__(self, "range", (_value(declared[0]), _value(declared[1])))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize one histogram bucket from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("bucket", "range", "frequency", "cumulative_frequency"),
        )
        return cls(
            bucket=data["bucket"],
            range=tuple(_array(data["range"], "range")),
            frequency=data["frequency"],
            cumulative_frequency=data["cumulative_frequency"],
        )


@dataclass(frozen=True, slots=True)
class Histogram(_StatisticsModel):
    """Canonical immutable in-memory histogram for one logical attribute."""

    model_name: ClassVar[str] = "histogram"
    reference: str
    attribute_name: str
    value_type: str
    buckets: tuple[HistogramBucket, ...]
    total_frequency: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "reference", _text(
                self.reference, "reference", InvalidStatisticsError
            )
        )
        object.__setattr__(
            self, "attribute_name", _text(
                self.attribute_name, "attribute_name", InvalidStatisticsError
            )
        )
        kind = _text(self.value_type, "value_type", InvalidStatisticsError)
        if kind not in {"numeric", "string", "boolean"}:
            raise InvalidStatisticsError("unsupported histogram value_type")
        buckets = tuple(self.buckets)
        if any(not isinstance(item, HistogramBucket) for item in buckets):
            raise InvalidStatisticsError("buckets must be HistogramBucket models")
        total = _count(self.total_frequency, "total_frequency")
        if [item.bucket for item in buckets] != list(range(len(buckets))):
            raise InvalidStatisticsError("histogram bucket ids must be contiguous")
        cumulative = 0
        for item in buckets:
            cumulative += item.frequency
            if item.cumulative_frequency != cumulative:
                raise InvalidStatisticsError(
                    "histogram cumulative frequencies are inconsistent"
                )
        if cumulative != total:
            raise InvalidStatisticsError(
                "histogram buckets must account for total_frequency"
            )
        object.__setattr__(self, "value_type", kind)
        object.__setattr__(self, "buckets", buckets)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a histogram from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("reference", "attribute_name", "value_type", "buckets",
             "total_frequency"),
        )
        declared = _array(data["buckets"], "buckets")
        if any(not isinstance(item, Mapping) for item in declared):
            raise InvalidStatisticsError("buckets must contain JSON objects")
        return cls(
            reference=data["reference"],
            attribute_name=data["attribute_name"],
            value_type=data["value_type"],
            buckets=tuple(HistogramBucket.from_dict(item) for item in declared),
            total_frequency=data["total_frequency"],
        )


@dataclass(frozen=True, slots=True)
class AttributeStatistics(_StatisticsModel):
    """Immutable distribution statistics for one indexed attribute."""

    model_name: ClassVar[str] = "attribute_statistics"
    attribute_name: str
    distinct_values: int
    null_count: int
    duplicated_count: int
    minimum: object
    maximum: object
    average_length: float
    histogram_reference: str | None
    selectivity: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "attribute_name", _text(
                self.attribute_name, "attribute_name", InvalidStatisticsError
            )
        )
        distinct = _count(self.distinct_values, "distinct_values")
        nulls = _count(self.null_count, "null_count")
        duplicates = _count(self.duplicated_count, "duplicated_count")
        minimum = _value(self.minimum)
        maximum = _value(self.maximum)
        if (minimum is None) != (maximum is None):
            raise InvalidStatisticsError("minimum and maximum must both be null or set")
        if type(minimum) is not type(maximum):
            raise InvalidStatisticsError("minimum and maximum must share a type")
        if minimum is not None and minimum > maximum:
            raise InvalidStatisticsError("minimum cannot exceed maximum")
        length = _number(self.average_length, "average_length")
        reference = self.histogram_reference
        if reference is not None:
            reference = _text(
                reference, "histogram_reference", InvalidStatisticsError
            )
        object.__setattr__(self, "distinct_values", distinct)
        object.__setattr__(self, "null_count", nulls)
        object.__setattr__(self, "duplicated_count", duplicates)
        object.__setattr__(self, "minimum", minimum)
        object.__setattr__(self, "maximum", maximum)
        object.__setattr__(self, "average_length", length)
        object.__setattr__(self, "histogram_reference", reference)
        object.__setattr__(self, "selectivity", _ratio(self.selectivity, "selectivity"))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize attribute statistics from a strict mapping."""
        return cls(**_envelope(
            payload, cls.model_name,
            ("attribute_name", "distinct_values", "null_count",
             "duplicated_count", "minimum", "maximum", "average_length",
             "histogram_reference", "selectivity"),
        ))


@dataclass(frozen=True, slots=True)
class LogicalStatistics(_StatisticsModel):
    """Canonical immutable statistics derived from one logical index."""

    model_name: ClassVar[str] = "logical_statistics"
    statistics_id: str
    index_id: str
    timestamp: datetime
    total_entries: int
    distinct_keys: int
    null_values: int
    duplicated_keys: int
    average_density: float
    average_selectivity: float
    estimated_cardinality: int
    metadata: Mapping[str, object] = field(default_factory=dict)
    attributes: tuple[AttributeStatistics, ...] = ()
    histograms: tuple[Histogram, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "statistics_id", _text(
                self.statistics_id, "statistics_id", InvalidStatisticsError
            )
        )
        object.__setattr__(
            self, "index_id", _text(self.index_id, "index_id", InvalidStatisticsError)
        )
        total = _count(self.total_entries, "total_entries")
        distinct = _count(self.distinct_keys, "distinct_keys")
        nulls = _count(self.null_values, "null_values")
        duplicates = _count(self.duplicated_keys, "duplicated_keys")
        cardinality = _count(self.estimated_cardinality, "estimated_cardinality")
        if distinct > total or nulls > total or duplicates > total:
            raise InvalidStatisticsError("statistics counts exceed total_entries")
        attributes = tuple(self.attributes)
        histograms = tuple(self.histograms)
        if any(not isinstance(item, AttributeStatistics) for item in attributes):
            raise InvalidStatisticsError("attributes contain an invalid model")
        if any(not isinstance(item, Histogram) for item in histograms):
            raise InvalidStatisticsError("histograms contain an invalid model")
        if len({item.attribute_name for item in attributes}) != len(attributes):
            raise InvalidStatisticsError("attribute statistics must be unique")
        if len({item.reference for item in histograms}) != len(histograms):
            raise InvalidStatisticsError("histogram references must be unique")
        references = {item.reference for item in histograms}
        if any(
            item.histogram_reference not in references
            for item in attributes if item.histogram_reference is not None
        ):
            raise InvalidStatisticsError("attribute references an unknown histogram")
        object.__setattr__(self, "timestamp", _aware(self.timestamp))
        object.__setattr__(self, "total_entries", total)
        object.__setattr__(self, "distinct_keys", distinct)
        object.__setattr__(self, "null_values", nulls)
        object.__setattr__(self, "duplicated_keys", duplicates)
        object.__setattr__(self, "average_density", _ratio(
            self.average_density, "average_density"
        ))
        object.__setattr__(self, "average_selectivity", _ratio(
            self.average_selectivity, "average_selectivity"
        ))
        object.__setattr__(self, "estimated_cardinality", cardinality)
        object.__setattr__(self, "metadata", _freeze(self.metadata))
        object.__setattr__(self, "attributes", attributes)
        object.__setattr__(self, "histograms", histograms)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize logical statistics from a strict mapping."""
        names = (
            "statistics_id", "index_id", "timestamp", "total_entries",
            "distinct_keys", "null_values", "duplicated_keys",
            "average_density", "average_selectivity", "estimated_cardinality",
            "metadata", "attributes", "histograms",
        )
        data = _envelope(payload, cls.model_name, names)
        attributes = _array(data["attributes"], "attributes")
        histograms = _array(data["histograms"], "histograms")
        if any(not isinstance(item, Mapping) for item in (*attributes, *histograms)):
            raise InvalidStatisticsError("nested statistics must be JSON objects")
        return cls(
            statistics_id=data["statistics_id"], index_id=data["index_id"],
            timestamp=_instant(data["timestamp"]),
            total_entries=data["total_entries"],
            distinct_keys=data["distinct_keys"], null_values=data["null_values"],
            duplicated_keys=data["duplicated_keys"],
            average_density=data["average_density"],
            average_selectivity=data["average_selectivity"],
            estimated_cardinality=data["estimated_cardinality"],
            metadata=_mapping(data["metadata"], "metadata"),
            attributes=tuple(AttributeStatistics.from_dict(item) for item in attributes),
            histograms=tuple(Histogram.from_dict(item) for item in histograms),
        )


@dataclass(frozen=True, slots=True)
class StatisticsPolicy(_StatisticsModel):
    """Immutable limits and strategies for statistics construction."""

    model_name: ClassVar[str] = "statistics_policy"
    max_buckets: int = 16
    granularity: int = 1
    histogram_policy: HistogramPolicy = HistogramPolicy.EQUAL_WIDTH
    estimation_strategy: EstimationStrategy = EstimationStrategy.HYBRID
    limits: Mapping[str, object] = field(default_factory=lambda: {
        "max_entries": 1_000_000,
        "minimum_confidence": 0.25,
    })

    def __post_init__(self) -> None:
        for value, name in (
            (self.max_buckets, "max_buckets"), (self.granularity, "granularity")
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise InvalidStatisticsPolicyError(f"{name} must be positive")
        try:
            histogram = HistogramPolicy(self.histogram_policy)
            strategy = EstimationStrategy(self.estimation_strategy)
        except (TypeError, ValueError) as error:
            raise InvalidStatisticsPolicyError("policy strategy is unsupported") from error
        limits = _freeze(self.limits)
        max_entries = limits.get("max_entries")
        confidence = limits.get("minimum_confidence")
        if isinstance(max_entries, bool) or not isinstance(max_entries, int):
            raise InvalidStatisticsPolicyError("max_entries limit must be positive")
        if max_entries < 1:
            raise InvalidStatisticsPolicyError("max_entries limit must be positive")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise InvalidStatisticsPolicyError("minimum_confidence must be a ratio")
        if not 0.0 <= float(confidence) <= 1.0:
            raise InvalidStatisticsPolicyError("minimum_confidence must be a ratio")
        object.__setattr__(self, "histogram_policy", histogram)
        object.__setattr__(self, "estimation_strategy", strategy)
        object.__setattr__(self, "limits", limits)

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a statistics policy from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("max_buckets", "granularity", "histogram_policy",
             "estimation_strategy", "limits"),
        )
        data["limits"] = _mapping(data["limits"], "limits")
        return cls(**data)


@dataclass(frozen=True, slots=True)
class CostEstimate(_StatisticsModel):
    """Immutable logical cost, row and selectivity estimate for a query plan."""

    model_name: ClassVar[str] = "cost_estimate"
    estimated_cost: float
    estimated_rows: int
    estimated_selectivity: float
    confidence: float
    justification: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "estimated_cost", _number(self.estimated_cost, "estimated_cost")
        )
        object.__setattr__(self, "estimated_rows", _count(
            self.estimated_rows, "estimated_rows"
        ))
        object.__setattr__(self, "estimated_selectivity", _ratio(
            self.estimated_selectivity, "estimated_selectivity"
        ))
        object.__setattr__(self, "confidence", _ratio(self.confidence, "confidence"))
        object.__setattr__(
            self, "justification", _text(
                self.justification, "justification", InvalidStatisticsError
            )
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a cost estimate from a strict mapping."""
        return cls(**_envelope(
            payload, cls.model_name,
            ("estimated_cost", "estimated_rows", "estimated_selectivity",
             "confidence", "justification"),
        ))


@dataclass(frozen=True, slots=True)
class StatisticsReport(_StatisticsModel):
    """Auditable report of the statistics and histograms used for an estimate."""

    model_name: ClassVar[str] = "statistics_report"
    statistics_used: tuple[str, ...]
    histograms_used: tuple[str, ...]
    justifications: tuple[str, ...]
    cost: CostEstimate
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        statistics = tuple(
            _text(item, "statistics_used item", InvalidStatisticsError)
            for item in self.statistics_used
        )
        histograms = tuple(
            _text(item, "histograms_used item", InvalidStatisticsError)
            for item in self.histograms_used
        )
        reasons = tuple(
            _text(item, "justification", InvalidStatisticsError)
            for item in self.justifications
        )
        if not statistics or not reasons:
            raise InvalidStatisticsError(
                "report requires used statistics and justifications"
            )
        if not isinstance(self.cost, CostEstimate):
            raise InvalidStatisticsError("cost must be a CostEstimate")
        object.__setattr__(self, "statistics_used", statistics)
        object.__setattr__(self, "histograms_used", histograms)
        object.__setattr__(self, "justifications", reasons)
        object.__setattr__(self, "timestamp", _aware(self.timestamp))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a statistics report from a strict mapping."""
        data = _envelope(
            payload, cls.model_name,
            ("statistics_used", "histograms_used", "justifications", "cost",
             "timestamp"),
        )
        return cls(
            statistics_used=tuple(_array(data["statistics_used"], "statistics_used")),
            histograms_used=tuple(_array(data["histograms_used"], "histograms_used")),
            justifications=tuple(_array(data["justifications"], "justifications")),
            cost=CostEstimate.from_dict(_mapping(data["cost"], "cost")),
            timestamp=_instant(data["timestamp"]),
        )


__all__ = [
    "AttributeStatistics",
    "CostEstimate",
    "EstimationStrategy",
    "Histogram",
    "HistogramBucket",
    "HistogramPolicy",
    "LogicalStatistics",
    "STATISTICS_SCHEMA_VERSION",
    "StatisticsPolicy",
    "StatisticsReport",
]
