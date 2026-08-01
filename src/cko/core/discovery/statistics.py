"""In-memory builders, validation and logical cost estimation for Discovery."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Iterable, Mapping, Sequence

from cko.core.logging import get_logger

from .query_index_models import LogicalIndex
from .query_models import (
    FilterGroup,
    FilterGroupOperator,
    QueryFilter,
    QueryOperator,
    QueryPlan,
)
from .statistics_errors import (
    CostEstimationError,
    InvalidStatisticsError,
    StatisticsValidationError,
)
from .statistics_models import (
    AttributeStatistics,
    CostEstimate,
    EstimationStrategy,
    Histogram,
    HistogramBucket,
    HistogramPolicy,
    LogicalStatistics,
    StatisticsPolicy,
    StatisticsReport,
)


def _event(logger: object, action: str, **context: object) -> None:
    getattr(logger, "info")(
        "Discovery statistics lifecycle event",
        extra={
            "event": f"discovery.query.statistics.{action}",
            "context": dict(sorted(context.items())),
        },
    )


def _kind(value: object) -> str | None:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        return "numeric"
    if isinstance(value, str):
        return "string"
    return None


def _serializable(value: object) -> object:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {
            str(key): _serializable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_serializable(item) for item in value]
    return repr(value)


def _token(value: object) -> str:
    return json.dumps(
        _serializable(value), ensure_ascii=False, allow_nan=False,
        separators=(",", ":"), sort_keys=True,
    )


def _contains_null(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, Mapping):
        return any(_contains_null(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_null(item) for item in value)
    return False


def _chunks(values: Sequence[object], maximum: int) -> tuple[tuple[object, ...], ...]:
    if not values:
        return ()
    size = max(1, math.ceil(len(values) / maximum))
    return tuple(
        tuple(values[start:start + size])
        for start in range(0, len(values), size)
    )


class HistogramBuilder:
    """Build deterministic numeric, string and boolean histograms in memory."""

    def __init__(self, policy: StatisticsPolicy | None = None) -> None:
        self._policy = policy or StatisticsPolicy()
        self._logger = get_logger("core.discovery.statistics")

    def build(
        self,
        attribute_name: str,
        values: Iterable[object],
        *,
        reference: str | None = None,
    ) -> Histogram:
        """Build a canonical histogram without mutating or persisting input values."""
        declared = tuple(item for item in values if item is not None)
        if not isinstance(attribute_name, str) or not attribute_name.strip():
            raise InvalidStatisticsError("attribute_name must be non-empty")
        if not declared:
            raise InvalidStatisticsError("histogram requires at least one non-null value")
        kinds = {_kind(item) for item in declared}
        if None in kinds or len(kinds) != 1:
            raise InvalidStatisticsError(
                "histogram values must share a supported scalar type"
            )
        kind = kinds.pop()
        identity = reference or f"histogram:{attribute_name.strip()}"
        _event(
            self._logger, "histogram_construction_started",
            attribute=attribute_name, values=len(declared),
        )
        if kind == "numeric":
            buckets = self._numeric(declared)
        else:
            buckets = self._categorical(declared)
        result = Histogram(
            reference=identity,
            attribute_name=attribute_name,
            value_type=kind,
            buckets=buckets,
            total_frequency=len(declared),
        )
        _event(
            self._logger, "histogram_construction_completed",
            attribute=result.attribute_name, buckets=len(result.buckets),
        )
        return result

    def _numeric(self, values: Sequence[object]) -> tuple[HistogramBucket, ...]:
        ordered = sorted(float(item) for item in values)
        maximum = min(self._policy.max_buckets, len(set(ordered)))
        if self._policy.histogram_policy is HistogramPolicy.EQUAL_FREQUENCY:
            groups = _chunks(ordered, maximum)
        else:
            lower, upper = ordered[0], ordered[-1]
            if lower == upper:
                groups = (tuple(ordered),)
            else:
                width = (upper - lower) / maximum
                mutable: list[list[object]] = [[] for _ in range(maximum)]
                for value in ordered:
                    position = min(int((value - lower) / width), maximum - 1)
                    mutable[position].append(value)
                groups = tuple(tuple(group) for group in mutable if group)
        return self._buckets(groups)

    def _categorical(self, values: Sequence[object]) -> tuple[HistogramBucket, ...]:
        frequencies: dict[object, int] = {}
        for value in values:
            frequencies[value] = frequencies.get(value, 0) + 1
        expanded: list[object] = []
        for value in sorted(frequencies):
            expanded.extend([value] * frequencies[value])
        unique = sorted(frequencies)
        if len(unique) <= self._policy.max_buckets:
            groups = tuple(tuple([value] * frequencies[value]) for value in unique)
        else:
            groups = _chunks(tuple(expanded), self._policy.max_buckets)
        return self._buckets(groups)

    @staticmethod
    def _buckets(groups: Sequence[Sequence[object]]) -> tuple[HistogramBucket, ...]:
        result: list[HistogramBucket] = []
        cumulative = 0
        for position, group in enumerate(groups):
            cumulative += len(group)
            lower, upper = group[0], group[-1]
            if isinstance(lower, float) and lower.is_integer():
                lower = int(lower)
            if isinstance(upper, float) and upper.is_integer():
                upper = int(upper)
            result.append(HistogramBucket(
                bucket=position,
                range=(lower, upper),
                frequency=len(group),
                cumulative_frequency=cumulative,
            ))
        return tuple(result)


class StatisticsBuilder:
    """Build deterministic logical and attribute statistics from a LogicalIndex."""

    def __init__(self, policy: StatisticsPolicy | None = None) -> None:
        self._policy = policy or StatisticsPolicy()
        self._histograms = HistogramBuilder(self._policy)
        self._logger = get_logger("core.discovery.statistics")

    def build(
        self,
        index: LogicalIndex,
        *,
        statistics_id: str | None = None,
        timestamp: datetime | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> LogicalStatistics:
        """Derive immutable logical statistics exclusively from an in-memory index."""
        if not isinstance(index, LogicalIndex):
            raise InvalidStatisticsError("index must be a LogicalIndex")
        maximum = self._policy.limits["max_entries"]
        if index.logical_cardinality > maximum:
            raise InvalidStatisticsError("logical index exceeds statistics policy limit")
        instant = timestamp or max(
            (item.timestamp for item in index.entries),
            default=datetime(1970, 1, 1, tzinfo=timezone.utc),
        )
        _event(
            self._logger, "construction_started", index_id=index.id,
            entries=index.logical_cardinality,
        )
        keys = tuple(item.indexed_key for item in index.entries)
        non_null_keys = tuple(item for item in keys if not _contains_null(item))
        distinct_keys = len({_token(item) for item in non_null_keys})
        null_values = len(keys) - len(non_null_keys)
        duplicated_keys = len(non_null_keys) - distinct_keys
        total = len(keys)
        density = distinct_keys / total if total else 0.0
        selectivity = 1.0 / distinct_keys if distinct_keys else 0.0
        cardinality = round(total * selectivity) if total else 0
        attribute_models: list[AttributeStatistics] = []
        histograms: list[Histogram] = []
        for attribute in index.indexed_attributes:
            values = tuple(item.attributes.get(attribute) for item in index.entries)
            non_null = tuple(item for item in values if item is not None)
            supported = bool(non_null) and len({_kind(item) for item in non_null}) == 1
            supported = supported and _kind(non_null[0]) is not None
            histogram = None
            if supported:
                histogram = self._histograms.build(
                    attribute, non_null,
                    reference=f"{index.id}:{attribute}:histogram",
                )
                histograms.append(histogram)
            distinct = len({_token(item) for item in non_null})
            minimum, maximum_value = self._bounds(non_null)
            average_length = (
                sum(len(str(item)) for item in non_null) / len(non_null)
                if non_null else 0.0
            )
            attribute_models.append(AttributeStatistics(
                attribute_name=attribute,
                distinct_values=distinct,
                null_count=total - len(non_null),
                duplicated_count=len(non_null) - distinct,
                minimum=minimum,
                maximum=maximum_value,
                average_length=average_length,
                histogram_reference=histogram.reference if histogram else None,
                selectivity=1.0 / distinct if distinct else 0.0,
            ))
        combined_metadata = {
            "index_strategy": index.strategy.value,
            "indexed_attributes": index.indexed_attributes,
            "logical_distribution": index.statistics.logical_distribution,
            **dict(metadata or {}),
        }
        result = LogicalStatistics(
            statistics_id=statistics_id or f"{index.id}:statistics",
            index_id=index.id,
            timestamp=instant,
            total_entries=total,
            distinct_keys=distinct_keys,
            null_values=null_values,
            duplicated_keys=duplicated_keys,
            average_density=density,
            average_selectivity=selectivity,
            estimated_cardinality=cardinality,
            metadata=combined_metadata,
            attributes=tuple(attribute_models),
            histograms=tuple(histograms),
        )
        StatisticsValidator().validate(result, policy=self._policy)
        _event(
            self._logger, "construction_completed", index_id=index.id,
            attributes=len(result.attributes), histograms=len(result.histograms),
        )
        _event(self._logger, "completed", index_id=index.id, outcome="built")
        return result

    @staticmethod
    def _bounds(values: Sequence[object]) -> tuple[object, object]:
        if not values:
            return None, None
        kind = _kind(values[0])
        if kind is None or any(_kind(item) != kind for item in values):
            return None, None
        if kind == "numeric" and any(isinstance(item, float) for item in values):
            normalized = tuple(float(item) for item in values)
            return min(normalized), max(normalized)
        return min(values), max(values)


class StatisticsValidator:
    """Validate logical counts, distributions, attributes and histogram buckets."""

    def __init__(self) -> None:
        self._logger = get_logger("core.discovery.statistics")

    def validate(
        self,
        statistics: LogicalStatistics,
        *,
        policy: StatisticsPolicy | None = None,
    ) -> LogicalStatistics:
        """Return statistics unchanged after all canonical invariants pass."""
        if not isinstance(statistics, LogicalStatistics):
            raise StatisticsValidationError(
                "statistics must be LogicalStatistics"
            )
        active = policy or StatisticsPolicy()
        _event(
            self._logger, "validation_started",
            statistics_id=statistics.statistics_id,
        )
        if statistics.total_entries > active.limits["max_entries"]:
            raise StatisticsValidationError("statistics exceed policy entry limit")
        expected_density = (
            statistics.distinct_keys / statistics.total_entries
            if statistics.total_entries else 0.0
        )
        expected_selectivity = (
            1.0 / statistics.distinct_keys if statistics.distinct_keys else 0.0
        )
        expected_cardinality = (
            round(statistics.total_entries * expected_selectivity)
            if statistics.total_entries else 0
        )
        if not math.isclose(statistics.average_density, expected_density):
            raise StatisticsValidationError("average density is inconsistent")
        if not math.isclose(statistics.average_selectivity, expected_selectivity):
            raise StatisticsValidationError("average selectivity is inconsistent")
        if statistics.estimated_cardinality != expected_cardinality:
            raise StatisticsValidationError("estimated cardinality is inconsistent")
        references = {item.reference: item for item in statistics.histograms}
        for histogram in statistics.histograms:
            if len(histogram.buckets) > active.max_buckets:
                raise StatisticsValidationError("histogram exceeds bucket limit")
            previous = None
            for bucket in histogram.buckets:
                if previous is not None and bucket.range[0] < previous:
                    raise StatisticsValidationError("histogram ranges overlap or regress")
                previous = bucket.range[1]
        for attribute in statistics.attributes:
            non_null = statistics.total_entries - attribute.null_count
            if attribute.distinct_values + attribute.duplicated_count != non_null:
                raise StatisticsValidationError(
                    f"attribute {attribute.attribute_name} counts are inconsistent"
                )
            if attribute.histogram_reference is not None:
                histogram = references[attribute.histogram_reference]
                if histogram.total_frequency != non_null:
                    raise StatisticsValidationError(
                        f"attribute {attribute.attribute_name} histogram is inconsistent"
                    )
        _event(
            self._logger, "validation_completed",
            statistics_id=statistics.statistics_id,
        )
        return statistics

    def is_valid(
        self,
        statistics: LogicalStatistics,
        *,
        policy: StatisticsPolicy | None = None,
    ) -> bool:
        """Return whether logical statistics satisfy all canonical invariants."""
        try:
            self.validate(statistics, policy=policy)
        except (InvalidStatisticsError, StatisticsValidationError):
            return False
        return True


class CostEstimator:
    """Estimate logical query cost without executing or optimizing a query."""

    def __init__(self, policy: StatisticsPolicy | None = None) -> None:
        self._policy = policy or StatisticsPolicy()
        self._logger = get_logger("core.discovery.statistics")

    def estimate(
        self,
        query_plan: QueryPlan,
        statistics: LogicalStatistics,
    ) -> CostEstimate:
        """Estimate selectivity, cardinality and relative logical processing cost."""
        if not isinstance(query_plan, QueryPlan):
            raise CostEstimationError("query_plan must be a QueryPlan")
        if not isinstance(statistics, LogicalStatistics):
            raise CostEstimationError("statistics must be LogicalStatistics")
        StatisticsValidator().validate(statistics, policy=self._policy)
        _event(
            self._logger, "estimation_started", query_id=query_plan.query_id,
            statistics_id=statistics.statistics_id,
        )
        attributes = {item.attribute_name: item for item in statistics.attributes}
        estimates = tuple(
            self._expression(item, attributes, statistics)
            for item in query_plan.effective_filters
        )
        selectivity = math.prod(item[0] for item in estimates) if estimates else 1.0
        selectivity = min(1.0, max(0.0, selectivity))
        rows = round(statistics.total_entries * selectivity)
        if query_plan.pagination is not None:
            limit = query_plan.pagination.limit or query_plan.pagination.page_size
            if limit is not None:
                rows = min(rows, limit)
        filter_work = len(estimates) * math.log2(statistics.total_entries + 1)
        row_work = rows * (1.0 + 0.1 * len(query_plan.projections))
        ordering_work = (
            rows * math.log2(rows + 1) if query_plan.ordering else 0.0
        )
        cost = row_work + filter_work + ordering_work
        known = sum(item[1] for item in estimates)
        confidence = known / len(estimates) if estimates else 1.0
        confidence = max(
            float(self._policy.limits["minimum_confidence"]), confidence
        )
        reason = (
            f"logical estimate from {len(estimates)} filter expression(s), "
            f"{known} backed by attribute statistics; no query was executed"
        )
        result = CostEstimate(
            estimated_cost=cost,
            estimated_rows=rows,
            estimated_selectivity=selectivity,
            confidence=min(confidence, 1.0),
            justification=reason,
        )
        _event(
            self._logger, "estimation_completed", query_id=query_plan.query_id,
            estimated_rows=result.estimated_rows,
            estimated_cost=result.estimated_cost,
        )
        _event(
            self._logger, "completed", query_id=query_plan.query_id,
            outcome="estimated",
        )
        return result

    def report(
        self,
        query_plan: QueryPlan,
        statistics: LogicalStatistics,
        *,
        timestamp: datetime | None = None,
    ) -> StatisticsReport:
        """Create an auditable report for a logical cost estimate."""
        cost = self.estimate(query_plan, statistics)
        referenced = {
            item.attribute for item in _atomic_filters(query_plan.effective_filters)
        }
        histograms = tuple(
            item.reference for item in statistics.histograms
            if item.attribute_name in referenced
        )
        return StatisticsReport(
            statistics_used=(statistics.statistics_id,),
            histograms_used=histograms,
            justifications=(cost.justification,),
            cost=cost,
            timestamp=timestamp or query_plan.timestamp,
        )

    def _expression(
        self,
        expression: object,
        attributes: Mapping[str, AttributeStatistics],
        statistics: LogicalStatistics,
    ) -> tuple[float, int]:
        if isinstance(expression, QueryFilter):
            attribute = attributes.get(expression.attribute)
            if attribute is None:
                return 0.25, 0
            return self._filter(expression, attribute, statistics), 1
        if not isinstance(expression, FilterGroup):
            return 0.25, 0
        children = tuple(
            self._expression(item, attributes, statistics)
            for item in expression.filters
        )
        values = tuple(item[0] for item in children)
        known = int(all(item[1] for item in children))
        if expression.operator is FilterGroupOperator.AND:
            return math.prod(values), known
        if expression.operator is FilterGroupOperator.OR:
            return 1.0 - math.prod(1.0 - item for item in values), known
        return 1.0 - values[0], known

    @staticmethod
    def _filter(
        query_filter: QueryFilter,
        attribute: AttributeStatistics,
        statistics: LogicalStatistics,
    ) -> float:
        operator = query_filter.operator
        base = attribute.selectivity or statistics.average_selectivity or 0.1
        null_ratio = (
            attribute.null_count / statistics.total_entries
            if statistics.total_entries else 0.0
        )
        if operator is QueryOperator.EQUALS:
            return base
        if operator is QueryOperator.NOT_EQUALS:
            return 1.0 - base
        if operator is QueryOperator.EXISTS:
            return 1.0 - null_ratio
        if operator is QueryOperator.NOT_EXISTS:
            return null_ratio
        if operator is QueryOperator.IN:
            return min(1.0, base * len(query_filter.value))
        if operator is QueryOperator.NOT_IN:
            return max(0.0, 1.0 - base * len(query_filter.value))
        if operator in {
            QueryOperator.GREATER_THAN, QueryOperator.GREATER_OR_EQUAL,
            QueryOperator.LOWER_THAN, QueryOperator.LOWER_OR_EQUAL,
        }:
            return CostEstimator._range_selectivity(query_filter, attribute)
        if operator is QueryOperator.STARTS_WITH:
            return min(1.0, max(base, 0.1))
        if operator in {QueryOperator.CONTAINS, QueryOperator.ENDS_WITH}:
            return min(1.0, max(base, 0.2))
        return 0.25

    @staticmethod
    def _range_selectivity(
        query_filter: QueryFilter,
        attribute: AttributeStatistics,
    ) -> float:
        lower, upper, value = attribute.minimum, attribute.maximum, query_filter.value
        if not all(isinstance(item, (int, float)) for item in (lower, upper, value)):
            return 1.0 / 3.0
        if lower == upper:
            matched = value < lower if query_filter.operator in {
                QueryOperator.GREATER_THAN, QueryOperator.GREATER_OR_EQUAL,
            } else value > upper
            return 1.0 if matched else 0.0
        position = min(1.0, max(0.0, (value - lower) / (upper - lower)))
        if query_filter.operator in {
            QueryOperator.GREATER_THAN, QueryOperator.GREATER_OR_EQUAL,
        }:
            return 1.0 - position
        return position


def _atomic_filters(expressions: Iterable[object]) -> tuple[QueryFilter, ...]:
    result: list[QueryFilter] = []
    for expression in expressions:
        if isinstance(expression, QueryFilter):
            result.append(expression)
        elif isinstance(expression, FilterGroup):
            result.extend(_atomic_filters(expression.filters))
    return tuple(result)


__all__ = [
    "CostEstimator",
    "HistogramBuilder",
    "StatisticsBuilder",
    "StatisticsValidator",
]
