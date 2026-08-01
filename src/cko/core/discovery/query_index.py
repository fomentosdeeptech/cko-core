"""Deterministic in-memory construction and planning of logical indexes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Mapping

from cko.core.logging import get_logger

from .query_index_errors import (
    InvalidLogicalIndexError,
    LogicalIndexResolutionError,
    LogicalIndexValidationError,
)
from .query_index_models import (
    DiscardedLogicalIndex,
    DuplicateBehavior,
    IndexStrategy,
    LogicalIndex,
    LogicalIndexEntry,
    LogicalIndexPolicy,
    LogicalIndexReport,
    LogicalIndexStatistics,
    QueryIndexPlan,
)
from .query_models import (
    FilterGroup,
    QueryFilter,
    QueryOperator,
    QueryPlan,
)


_MISSING = object()


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    raise InvalidLogicalIndexError(
        f"unsupported indexed value: {type(value).__name__}"
    )


def _key_token(value: object) -> str:
    return json.dumps(
        _primitive(value), allow_nan=False, ensure_ascii=False,
        separators=(",", ":"), sort_keys=True,
    )


def _resolve(subject: object, path: str) -> object:
    current = subject
    for segment in path.split("."):
        if isinstance(current, Mapping):
            current = current.get(segment, _MISSING)
        elif not segment.startswith("_") and hasattr(current, segment):
            current = getattr(current, segment)
        else:
            current = _MISSING
        if current is _MISSING:
            raise InvalidLogicalIndexError(
                f"attribute {path!r} is absent from an indexed subject"
            )
    return current


def _identity(subject: object) -> str:
    for name in ("logical_identity", "identity", "id"):
        try:
            value = _resolve(subject, name)
        except InvalidLogicalIndexError:
            continue
        if isinstance(value, str) and value.strip():
            return value.strip()
        if value is not None and not isinstance(value, (Mapping, list, tuple)):
            rendered = str(value).strip()
            if rendered:
                return rendered
    raise InvalidLogicalIndexError(
        "indexed subjects must expose logical_identity, identity, or id"
    )


def _event(logger: object, action: str, **context: object) -> None:
    getattr(logger, "info")(
        "Discovery logical index lifecycle event",
        extra={
            "event": f"discovery.query.index.{action}",
            "context": dict(sorted(context.items())),
        },
    )


class LogicalIndexBuilder:
    """Build immutable logical indexes exclusively from in-memory objects."""

    def __init__(self, policy: LogicalIndexPolicy | None = None) -> None:
        self._policy = policy or LogicalIndexPolicy()
        self._logger = get_logger("core.discovery.query_index")

    def build(
        self,
        index_id: str,
        name: str,
        subjects: Iterable[object],
        indexed_attributes: Iterable[str],
        *,
        strategy: IndexStrategy | None = None,
        relevant_attributes: Iterable[str] | None = None,
        timestamp: datetime | None = None,
    ) -> LogicalIndex:
        """Build and validate one deterministic in-memory logical index."""
        attributes = tuple(indexed_attributes)
        relevant = tuple(dict.fromkeys((*attributes, *(relevant_attributes or ()))))
        instant = (timestamp or datetime.now(timezone.utc)).astimezone(timezone.utc)
        try:
            selected_strategy = IndexStrategy(
                strategy or self._policy.default_strategy
            )
        except (TypeError, ValueError) as error:
            raise InvalidLogicalIndexError("unsupported index strategy") from error
        _event(
            self._logger, "construction_started", index_id=index_id,
            strategy=selected_strategy.value,
        )
        by_identity: dict[str, LogicalIndexEntry] = {}
        for subject in subjects:
            identity = _identity(subject)
            values = {attribute: _resolve(subject, attribute) for attribute in relevant}
            key_parts = tuple(_resolve(subject, attribute) for attribute in attributes)
            key: object = key_parts[0] if len(key_parts) == 1 else key_parts
            entry = LogicalIndexEntry(identity, key, values, instant)
            if identity in by_identity:
                behavior = self._policy.duplicate_behavior
                if behavior is DuplicateBehavior.REJECT:
                    raise LogicalIndexValidationError(
                        f"duplicate logical identity: {identity}"
                    )
                if behavior is DuplicateBehavior.KEEP_FIRST:
                    continue
            by_identity[identity] = entry
            if len(by_identity) > self._policy.max_cardinality:
                raise LogicalIndexValidationError(
                    "logical index exceeds policy cardinality limit"
                )
        entries = tuple(sorted(
            by_identity.values(),
            key=lambda item: (item.logical_identity, _key_token(item.indexed_key)),
        ))
        distribution: dict[str, int] = {}
        for entry in entries:
            token = _key_token(entry.indexed_key)
            distribution[token] = distribution.get(token, 0) + 1
        count = len(entries)
        distinct = len(distribution)
        statistics = LogicalIndexStatistics(
            entry_count=count,
            distinct_key_count=distinct,
            logical_distribution=distribution,
            density=distinct / count if count else 0.0,
            estimates={
                "average_entries_per_key": count / distinct if distinct else 0.0,
                "maximum_bucket_size": max(distribution.values(), default=0),
            },
        )
        index = LogicalIndex(
            id=index_id, name=name, indexed_attributes=attributes,
            strategy=selected_strategy, logical_cardinality=count,
            statistics=statistics, entries=entries,
        )
        LogicalIndexValidator().validate(index, policy=self._policy)
        _event(
            self._logger, "construction_completed", index_id=index.id,
            entries=count, distinct_keys=distinct,
        )
        return index


class LogicalIndexValidator:
    """Validate identity, key, statistics, strategy and policy consistency."""

    def __init__(self) -> None:
        self._logger = get_logger("core.discovery.query_index")

    def validate(
        self,
        index: LogicalIndex,
        *,
        policy: LogicalIndexPolicy | None = None,
    ) -> LogicalIndex:
        """Return the index unchanged when every invariant is satisfied."""
        if not isinstance(index, LogicalIndex):
            raise LogicalIndexValidationError("index must be a LogicalIndex")
        active_policy = policy or LogicalIndexPolicy()
        _event(self._logger, "validation_started", index_id=index.id)
        if index.logical_cardinality > active_policy.max_cardinality:
            raise LogicalIndexValidationError(
                "logical index exceeds policy cardinality limit"
            )
        identities = [item.logical_identity for item in index.entries]
        if len(identities) != len(set(identities)):
            raise LogicalIndexValidationError("duplicate logical identities detected")
        distribution: dict[str, int] = {}
        for entry in index.entries:
            missing = [
                attribute for attribute in index.indexed_attributes
                if attribute not in entry.attributes
            ]
            if missing:
                raise LogicalIndexValidationError(
                    f"entry {entry.logical_identity} lacks indexed attributes: "
                    f"{', '.join(missing)}"
                )
            parts = tuple(
                entry.attributes[attribute]
                for attribute in index.indexed_attributes
            )
            expected: object = parts[0] if len(parts) == 1 else parts
            if _key_token(expected) != _key_token(entry.indexed_key):
                raise LogicalIndexValidationError(
                    f"entry {entry.logical_identity} has an inconsistent key"
                )
            token = _key_token(entry.indexed_key)
            distribution[token] = distribution.get(token, 0) + 1
        statistics = index.statistics
        if (
            statistics.entry_count != len(index.entries)
            or statistics.distinct_key_count != len(distribution)
            or dict(statistics.logical_distribution) != distribution
        ):
            raise LogicalIndexValidationError("logical index statistics are inconsistent")
        _event(
            self._logger, "validation_completed", index_id=index.id,
            entries=len(index.entries),
        )
        return index

    def is_valid(
        self,
        index: LogicalIndex,
        *,
        policy: LogicalIndexPolicy | None = None,
    ) -> bool:
        """Return whether an index satisfies every canonical invariant."""
        try:
            self.validate(index, policy=policy)
        except (InvalidLogicalIndexError, LogicalIndexValidationError):
            return False
        return True


@dataclass(frozen=True, slots=True)
class _Candidate:
    index: LogicalIndex
    matched_attributes: tuple[str, ...]
    compatibility: int
    cost: float
    reason: str


def _filters(expressions: Iterable[object]) -> tuple[QueryFilter, ...]:
    result: list[QueryFilter] = []
    for expression in expressions:
        if isinstance(expression, QueryFilter):
            result.append(expression)
        elif isinstance(expression, FilterGroup):
            result.extend(_filters(expression.filters))
    return tuple(result)


def _compatibility(index: LogicalIndex, plan: QueryPlan) -> _Candidate | None:
    filters = _filters(plan.effective_filters)
    operators = {
        item.attribute: item.operator for item in filters
    }
    ordering = {item.attribute for item in plan.ordering}
    matched = tuple(
        attribute for attribute in index.indexed_attributes
        if attribute in operators or attribute in ordering
    )
    if not matched:
        return None
    equality = {QueryOperator.EQUALS, QueryOperator.IN}
    ranged = {
        QueryOperator.EQUALS, QueryOperator.IN, QueryOperator.GREATER_THAN,
        QueryOperator.GREATER_OR_EQUAL, QueryOperator.LOWER_THAN,
        QueryOperator.LOWER_OR_EQUAL,
    }
    compatible = 0
    for attribute in matched:
        operator = operators.get(attribute)
        if index.strategy is IndexStrategy.HASH and operator in equality:
            compatible += 4
        elif index.strategy is IndexStrategy.ORDERED and (
            operator in ranged or attribute in ordering
        ):
            compatible += 3
        elif index.strategy is IndexStrategy.PREFIX and operator is QueryOperator.STARTS_WITH:
            compatible += 4
        elif index.strategy is IndexStrategy.COMPOSITE and operator in equality:
            compatible += 5
        elif attribute in ordering and index.strategy in {
            IndexStrategy.ORDERED, IndexStrategy.COMPOSITE,
        }:
            compatible += 2
    if compatible == 0:
        return None
    coverage = len(matched) / len(index.indexed_attributes)
    selectivity = max(index.statistics.density, 1 / max(index.logical_cardinality, 1))
    cost = index.logical_cardinality / (1 + compatible * coverage * selectivity)
    reason = (
        f"strategy {index.strategy.value} supports {len(matched)} attribute(s) "
        f"with compatibility score {compatible} and coverage {coverage:.3f}"
    )
    return _Candidate(index, matched, compatible, cost, reason)


class LogicalIndexResolver:
    """Select the best logical index deterministically and audit the decision."""

    def __init__(self, policy: LogicalIndexPolicy | None = None) -> None:
        self._policy = policy or LogicalIndexPolicy()
        self._logger = get_logger("core.discovery.query_index")

    def resolve(
        self,
        query_plan: QueryPlan,
        indexes: Iterable[LogicalIndex],
        *,
        timestamp: datetime | None = None,
    ) -> LogicalIndexReport:
        """Resolve available indexes into one deterministic selection report."""
        if not isinstance(query_plan, QueryPlan):
            raise LogicalIndexResolutionError("query_plan must be a QueryPlan")
        declared = tuple(indexes)
        if len(declared) > self._policy.max_indexes:
            raise LogicalIndexResolutionError("available indexes exceed policy limit")
        if any(not isinstance(item, LogicalIndex) for item in declared):
            raise LogicalIndexResolutionError(
                "available indexes must contain LogicalIndex models"
            )
        if len({item.id for item in declared}) != len(declared):
            raise LogicalIndexResolutionError("available index ids must be unique")
        instant = (timestamp or datetime.now(timezone.utc)).astimezone(timezone.utc)
        _event(
            self._logger, "selection_started", query_id=query_plan.query_id,
            available_indexes=len(declared),
        )
        candidates = tuple(
            candidate for candidate in (
                _compatibility(index, query_plan) for index in declared
            ) if candidate is not None
        )
        ranked = sorted(
            candidates,
            key=lambda item: (
                -item.compatibility, -len(item.matched_attributes),
                item.cost, item.index.id,
            ),
        )
        selected = ranked[0] if ranked else None
        discarded: list[DiscardedLogicalIndex] = []
        for index in sorted(declared, key=lambda item: item.id):
            if selected is not None and index.id == selected.index.id:
                continue
            candidate = next(
                (item for item in candidates if item.index.id == index.id), None
            )
            discarded.append(DiscardedLogicalIndex(
                index_id=index.id,
                reason=(
                    "no compatible query predicate or ordering"
                    if candidate is None
                    else f"ranked below {selected.index.id}: {candidate.reason}"
                ),
                estimated_cost=(
                    float(index.logical_cardinality)
                    if candidate is None else candidate.cost
                ),
            ))
        if selected is None:
            fallback = max(
                (float(item.logical_cardinality) for item in declared), default=0.0
            )
            report = LogicalIndexReport(
                selected_index_id=None,
                justification="no available logical index is compatible with the query plan",
                discarded_indexes=tuple(discarded),
                estimated_logical_cost=fallback,
                timestamp=instant,
            )
        else:
            report = LogicalIndexReport(
                selected_index_id=selected.index.id,
                justification=(
                    f"selected {selected.index.id} deterministically: {selected.reason}"
                ),
                discarded_indexes=tuple(discarded),
                estimated_logical_cost=selected.cost,
                timestamp=instant,
            )
        _event(
            self._logger, "selection_completed", query_id=query_plan.query_id,
            selected_index=report.selected_index_id or "none",
            estimated_cost=report.estimated_logical_cost,
        )
        return report


class QueryIndexPlanner:
    """Produce an auditable logical index utilization plan for a QueryPlan."""

    def __init__(
        self,
        policy: LogicalIndexPolicy | None = None,
        resolver: LogicalIndexResolver | None = None,
    ) -> None:
        self._policy = policy or LogicalIndexPolicy()
        self._resolver = resolver or LogicalIndexResolver(self._policy)
        self._logger = get_logger("core.discovery.query_index")

    def plan(
        self,
        query_plan: QueryPlan,
        indexes: Iterable[LogicalIndex],
        *,
        timestamp: datetime | None = None,
    ) -> QueryIndexPlan:
        """Plan deterministic logical index utilization without infrastructure."""
        instant = (timestamp or datetime.now(timezone.utc)).astimezone(timezone.utc)
        declared = tuple(indexes)
        _event(
            self._logger, "planning_started", query_id=query_plan.query_id,
            available_indexes=len(declared),
        )
        report = self._resolver.resolve(
            query_plan, declared, timestamp=instant
        )
        selected = next(
            (
                item for item in declared
                if item.id == report.selected_index_id
            ),
            None,
        )
        candidate = _compatibility(selected, query_plan) if selected else None
        matched = candidate.matched_attributes if candidate else ()
        reasons = (
            report.justification,
            (
                "query evaluation should use the selected immutable logical index"
                if selected else
                "query evaluation should perform an infrastructure-neutral full scan"
            ),
        )
        result = QueryIndexPlan(
            query_id=query_plan.query_id,
            selected_index_id=report.selected_index_id,
            matched_attributes=matched,
            estimated_logical_cost=report.estimated_logical_cost,
            justifications=reasons,
            resolution_report=report,
            timestamp=instant,
        )
        _event(
            self._logger, "planning_completed", query_id=query_plan.query_id,
            selected_index=result.selected_index_id or "none",
            estimated_cost=result.estimated_logical_cost,
        )
        _event(
            self._logger, "completed", query_id=query_plan.query_id,
            outcome="planned",
        )
        return result


__all__ = [
    "LogicalIndexBuilder",
    "LogicalIndexResolver",
    "LogicalIndexValidator",
    "QueryIndexPlanner",
]
