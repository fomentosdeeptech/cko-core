"""Deterministic cost-based planning without query execution or rewriting."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping

from cko.core.logging import get_logger

from .planner_errors import PlanningError, PlannerValidationError
from .planner_models import (
    PlannerDecision,
    PlannerMetrics,
    PlannerPolicy,
    PlannerReport,
    QueryExecutionPlan,
    QueryExecutionStrategy,
)
from .query_index import LogicalIndexValidator
from .query_index_models import IndexStrategy, LogicalIndex
from .query_models import FilterGroup, QueryFilter, QueryOperator, QueryPlan
from .statistics import CostEstimator, StatisticsValidator
from .statistics_models import CostEstimate, LogicalStatistics


PLANNER_VERSION = "1.0.0"


def _event(logger: object, action: str, **context: object) -> None:
    getattr(logger, "info")(
        "Cost-based query planner lifecycle event",
        extra={
            "event": f"discovery.query.planner.{action}",
            "context": dict(sorted(context.items())),
        },
    )


def _filters(expressions: Iterable[object]) -> tuple[QueryFilter, ...]:
    result: list[QueryFilter] = []
    for expression in expressions:
        if isinstance(expression, QueryFilter):
            result.append(expression)
        elif isinstance(expression, FilterGroup):
            result.extend(_filters(expression.filters))
    return tuple(result)


def _coverage(requested: set[str], indexed: set[str]) -> float:
    return len(requested & indexed) / len(requested) if requested else 1.0


def _supported(index: LogicalIndex, query_filter: QueryFilter) -> bool:
    equality = {QueryOperator.EQUALS, QueryOperator.IN}
    ranged = equality | {
        QueryOperator.GREATER_THAN,
        QueryOperator.GREATER_OR_EQUAL,
        QueryOperator.LOWER_THAN,
        QueryOperator.LOWER_OR_EQUAL,
    }
    if index.strategy is IndexStrategy.HASH:
        return query_filter.operator in equality
    if index.strategy is IndexStrategy.ORDERED:
        return query_filter.operator in ranged
    if index.strategy is IndexStrategy.PREFIX:
        return query_filter.operator is QueryOperator.STARTS_WITH
    return query_filter.operator in equality


def _strategy(index: LogicalIndex) -> QueryExecutionStrategy:
    return {
        IndexStrategy.HASH: QueryExecutionStrategy.INDEX_SCAN,
        IndexStrategy.COMPOSITE: QueryExecutionStrategy.COMPOSITE_INDEX_SCAN,
        IndexStrategy.PREFIX: QueryExecutionStrategy.PREFIX_INDEX_SCAN,
        IndexStrategy.ORDERED: QueryExecutionStrategy.ORDERED_INDEX_SCAN,
    }[index.strategy]


@dataclass(frozen=True, slots=True)
class _Candidate:
    name: str
    strategy: QueryExecutionStrategy
    indexes: tuple[str, ...]
    cost: float
    rows: int
    selectivity: float
    coverage: float
    density: float
    confidence: float
    justification: str


def _index_candidate(
    index: LogicalIndex,
    query_plan: QueryPlan,
    estimate: CostEstimate,
    statistics: LogicalStatistics,
) -> _Candidate | None:
    atomic = _filters(query_plan.effective_filters)
    indexed = set(index.indexed_attributes)
    supported = {
        item.attribute for item in atomic
        if item.attribute in indexed and _supported(index, item)
    }
    ordered = {item.attribute for item in query_plan.ordering}
    ordering_match = ordered & indexed if index.strategy in {
        IndexStrategy.ORDERED, IndexStrategy.COMPOSITE,
    } else set()
    if not supported and not ordering_match:
        return None
    filtered = {item.attribute for item in atomic}
    projected = {item.attribute for item in query_plan.projections}
    dimensions = (
        _coverage(filtered, supported),
        _coverage(ordered, ordering_match),
        _coverage(projected, indexed),
    )
    relevant = [value for value, source in zip(
        dimensions, (filtered, ordered, projected), strict=True
    ) if source]
    coverage = sum(relevant) / len(relevant) if relevant else 0.0
    density = index.statistics.density
    factor = {
        IndexStrategy.HASH: 0.42,
        IndexStrategy.COMPOSITE: 0.28,
        IndexStrategy.PREFIX: 0.36,
        IndexStrategy.ORDERED: 0.34,
    }[index.strategy]
    selectivity_factor = 0.5 + estimate.estimated_selectivity
    coverage_factor = 1.5 - 0.5 * coverage
    density_factor = 1.25 - 0.5 * density
    cost = estimate.estimated_cost * factor * selectivity_factor
    cost *= coverage_factor * density_factor
    if statistics.total_entries:
        lookup = math.log2(statistics.total_entries + 1)
        cost = max(lookup, cost)
    confidence = estimate.confidence * (0.75 + 0.25 * coverage)
    strategy = _strategy(index)
    return _Candidate(
        name=f"{strategy.value}:{index.id}",
        strategy=strategy,
        indexes=(index.id,),
        cost=cost,
        rows=estimate.estimated_rows,
        selectivity=estimate.estimated_selectivity,
        coverage=coverage,
        density=density,
        confidence=min(1.0, confidence),
        justification=(
            f"{index.id} supports {len(supported)} filter attribute(s), "
            f"{len(ordering_match)} ordering attribute(s), coverage={coverage:.6f}, "
            f"density={density:.6f}"
        ),
    )


def _combined_candidate(
    candidates: tuple[_Candidate, ...],
    policy: PlannerPolicy,
) -> _Candidate | None:
    if not policy.allow_multiple_indexes or len(candidates) < 2:
        return None
    ranked = sorted(candidates, key=lambda item: (item.cost, item.indexes))
    selected = tuple(ranked[:policy.index_limit])
    if len(selected) < 2:
        return None
    indexes = tuple(sorted(item.indexes[0] for item in selected))
    coverage = min(1.0, sum(item.coverage for item in selected))
    density = sum(item.density for item in selected) / len(selected)
    cost = min(item.cost for item in selected) * (0.85 ** (len(selected) - 1))
    confidence = min(item.confidence for item in selected)
    return _Candidate(
        name=f"{QueryExecutionStrategy.COMPOSITE_INDEX_SCAN.value}:{'+'.join(indexes)}",
        strategy=QueryExecutionStrategy.COMPOSITE_INDEX_SCAN,
        indexes=indexes,
        cost=cost,
        rows=min(item.rows for item in selected),
        selectivity=min(item.selectivity for item in selected),
        coverage=coverage,
        density=density,
        confidence=confidence,
        justification=(
            f"combined {len(indexes)} compatible indexes under the multiple-index policy; "
            f"coverage={coverage:.6f}, density={density:.6f}"
        ),
    )


def _score(candidate: _Candidate, maximum_cost: float, policy: PlannerPolicy) -> float:
    weights = policy.weights
    cost_value = 1.0 - min(1.0, candidate.cost / max(maximum_cost, 1.0))
    values = {
        "selectivity": 1.0 - candidate.selectivity,
        "cardinality": 1.0 - candidate.selectivity,
        "cost": cost_value,
        "coverage": candidate.coverage,
        "density": candidate.density,
        "confidence": candidate.confidence,
    }
    weighted = sum(getattr(weights, name) * value for name, value in values.items())
    return weighted / weights.total


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


class PlannerValidator:
    """Validate execution strategy, cost, indexes, coherence and policy."""

    def validate(
        self,
        execution_plan: QueryExecutionPlan,
        *,
        policy: PlannerPolicy | None = None,
        indexes: Iterable[LogicalIndex] | None = None,
    ) -> QueryExecutionPlan:
        """Return a coherent plan or raise a precise policy validation error."""
        if not isinstance(execution_plan, QueryExecutionPlan):
            raise PlannerValidationError(
                "execution_plan must be a QueryExecutionPlan"
            )
        selected_policy = policy or PlannerPolicy()
        if not isinstance(selected_policy, PlannerPolicy):
            raise PlannerValidationError("policy must be PlannerPolicy")
        if execution_plan.estimated_cost > selected_policy.max_acceptable_cost:
            raise PlannerValidationError("estimated cost exceeds the policy maximum")
        if execution_plan.confidence < selected_policy.minimum_confidence:
            raise PlannerValidationError("confidence is below the policy minimum")
        full_scan = execution_plan.execution_strategy is QueryExecutionStrategy.FULL_SCAN
        if full_scan and not selected_policy.allow_full_scan:
            raise PlannerValidationError("full scan is disabled by policy")
        if len(execution_plan.selected_indexes) > selected_policy.index_limit:
            raise PlannerValidationError("selected indexes exceed the policy limit")
        if len(execution_plan.selected_indexes) > 1:
            if not selected_policy.allow_multiple_indexes:
                raise PlannerValidationError("multiple indexes are disabled by policy")
            if execution_plan.execution_strategy is not (
                QueryExecutionStrategy.COMPOSITE_INDEX_SCAN
            ):
                raise PlannerValidationError(
                    "multiple indexes require the composite index strategy"
                )
        declared = tuple(indexes or ())
        if any(not isinstance(item, LogicalIndex) for item in declared):
            raise PlannerValidationError("indexes must contain LogicalIndex models")
        if declared:
            available = {item.id for item in declared}
            if not set(execution_plan.selected_indexes) <= available:
                raise PlannerValidationError("plan selects an unavailable index")
        metadata = execution_plan.metadata
        try:
            decision = PlannerDecision.from_dict(_thaw(metadata["decision"]))
            report = PlannerReport.from_dict(_thaw(metadata["report"]))
            metrics = PlannerMetrics.from_dict(_thaw(metadata["metrics"]))
        except (KeyError, TypeError, ValueError) as error:
            raise PlannerValidationError("planner audit metadata is invalid") from error
        if decision.strategy is not execution_plan.execution_strategy:
            raise PlannerValidationError("decision strategy is inconsistent")
        if report.chosen_strategy is not execution_plan.execution_strategy:
            raise PlannerValidationError("report strategy is inconsistent")
        if report.indexes_used != execution_plan.selected_indexes:
            raise PlannerValidationError("report indexes are inconsistent")
        if not math.isclose(report.final_cost, execution_plan.estimated_cost):
            raise PlannerValidationError("report cost is inconsistent")
        if metrics.chosen_candidate not in metadata["candidate_scores"]:
            raise PlannerValidationError("chosen candidate metric is inconsistent")
        return execution_plan

    def is_valid(
        self,
        execution_plan: QueryExecutionPlan,
        *,
        policy: PlannerPolicy | None = None,
        indexes: Iterable[LogicalIndex] | None = None,
    ) -> bool:
        """Return whether an execution plan satisfies all canonical invariants."""
        try:
            self.validate(execution_plan, policy=policy, indexes=indexes)
        except (TypeError, ValueError):
            return False
        return True


class CostBasedPlanner:
    """Choose one reproducible logical execution strategy without executing it."""

    def __init__(
        self,
        policy: PlannerPolicy | None = None,
        estimator: CostEstimator | None = None,
    ) -> None:
        self._policy = policy or PlannerPolicy()
        if not isinstance(self._policy, PlannerPolicy):
            raise TypeError("policy must be PlannerPolicy")
        self._estimator = estimator or CostEstimator()
        if not isinstance(self._estimator, CostEstimator):
            raise TypeError("estimator must be CostEstimator")
        self._logger = get_logger("core.discovery.planner")

    def plan(
        self,
        query_plan: QueryPlan,
        statistics: LogicalStatistics,
        indexes: Iterable[LogicalIndex],
        *,
        timestamp: datetime | None = None,
    ) -> QueryExecutionPlan:
        """Plan a deterministic strategy from a plan, statistics and indexes."""
        if not isinstance(query_plan, QueryPlan):
            raise PlanningError("query_plan must be a QueryPlan")
        if not isinstance(statistics, LogicalStatistics):
            raise PlanningError("statistics must be LogicalStatistics")
        declared = tuple(indexes)
        if any(not isinstance(item, LogicalIndex) for item in declared):
            raise PlanningError("indexes must contain LogicalIndex models")
        if len({item.id for item in declared}) != len(declared):
            raise PlanningError("index ids must be unique")
        if len(declared) > self._policy.index_limit and (
            self._policy.allow_multiple_indexes
        ):
            declared = tuple(sorted(declared, key=lambda item: item.id))
        instant = (timestamp or query_plan.timestamp).astimezone(timezone.utc)
        _event(
            self._logger, "planning_started", query_id=query_plan.query_id,
            indexes=len(declared),
        )
        StatisticsValidator().validate(statistics)
        for index in declared:
            LogicalIndexValidator().validate(index)
        estimate = self._estimator.estimate(query_plan, statistics)
        singles = tuple(
            candidate for candidate in (
                _index_candidate(index, query_plan, estimate, statistics)
                for index in sorted(declared, key=lambda item: item.id)
            ) if candidate is not None
        )
        candidates = list(singles)
        combined = _combined_candidate(singles, self._policy)
        if combined is not None:
            candidates.append(combined)
        if self._policy.allow_full_scan:
            candidates.append(_Candidate(
                name=QueryExecutionStrategy.FULL_SCAN.value,
                strategy=QueryExecutionStrategy.FULL_SCAN,
                indexes=(),
                cost=estimate.estimated_cost,
                rows=estimate.estimated_rows,
                selectivity=estimate.estimated_selectivity,
                coverage=0.0,
                density=statistics.average_density,
                confidence=estimate.confidence,
                justification=(
                    "full scan baseline derived from canonical logical statistics"
                ),
            ))
        _event(
            self._logger, "analysis_completed", query_id=query_plan.query_id,
            candidates=len(candidates),
        )
        eligible = tuple(
            item for item in candidates
            if item.cost <= self._policy.max_acceptable_cost
            and item.confidence >= self._policy.minimum_confidence
        )
        if not eligible:
            raise PlanningError("no candidate satisfies planner cost and confidence policy")
        maximum = max(item.cost for item in candidates) if candidates else 1.0
        scores = {item.name: _score(item, maximum, self._policy)
                  for item in candidates}
        chosen = sorted(
            eligible,
            key=lambda item: (
                -scores[item.name],
                item.strategy is not self._policy.default_strategy,
                item.cost,
                item.strategy.value,
                item.indexes,
            ),
        )[0]
        _event(
            self._logger, "comparison_completed", query_id=query_plan.query_id,
            eligible=len(eligible), chosen_candidate=chosen.name,
        )
        discarded = tuple(item for item in candidates if item.name != chosen.name)
        strategies = tuple(sorted(
            {item.strategy for item in discarded if item.strategy is not chosen.strategy},
            key=lambda item: item.value,
        ))
        discarded_indexes = tuple(sorted(
            item.id for item in declared if item.id not in chosen.indexes
        ))
        full_cost = next(
            (item.cost for item in candidates
             if item.strategy is QueryExecutionStrategy.FULL_SCAN),
            estimate.estimated_cost,
        )
        gain = max(0.0, full_cost - chosen.cost)
        decision = PlannerDecision(
            strategy=chosen.strategy,
            justification=(
                f"selected {chosen.name} with deterministic score "
                f"{scores[chosen.name]:.12f}; {chosen.justification}"
            ),
            discarded_strategies=strategies,
            discarded_indexes=discarded_indexes,
            confidence=chosen.confidence,
            estimated_gain=gain,
            timestamp=instant,
        )
        report = PlannerReport(
            chosen_strategy=chosen.strategy,
            discarded_strategies=strategies,
            indexes_used=chosen.indexes,
            discarded_indexes=discarded_indexes,
            justifications=(decision.justification, estimate.justification),
            statistics_used=(statistics.statistics_id,),
            final_cost=chosen.cost,
            timestamp=instant,
        )
        metrics = PlannerMetrics(
            planning_duration=0.0,
            indexes_evaluated=len(declared),
            strategies_evaluated=len({item.strategy for item in candidates}),
            total_candidates=len(candidates),
            chosen_candidate=chosen.name,
            discarded_candidates=tuple(item.name for item in discarded),
        )
        _event(
            self._logger, "decision_completed", query_id=query_plan.query_id,
            strategy=chosen.strategy.value, selected_indexes=chosen.indexes,
        )
        metadata = {
            "candidate_scores": dict(sorted(scores.items())),
            "decision": decision.to_dict(),
            "metrics": metrics.to_dict(),
            "policy": self._policy.to_dict(),
            "report": report.to_dict(),
            "statistics_id": statistics.statistics_id,
        }
        plan_id = self._plan_id(
            query_plan, statistics, declared, chosen, metadata
        )
        result = QueryExecutionPlan(
            plan_id=plan_id,
            query_plan=query_plan,
            execution_strategy=chosen.strategy,
            selected_indexes=chosen.indexes,
            estimated_cost=chosen.cost,
            estimated_rows=chosen.rows,
            estimated_selectivity=chosen.selectivity,
            confidence=chosen.confidence,
            planning_time=metrics.planning_duration,
            planner_version=PLANNER_VERSION,
            timestamp=instant,
            metadata=metadata,
        )
        PlannerValidator().validate(
            result, policy=self._policy, indexes=declared
        )
        _event(
            self._logger, "planning_completed", query_id=query_plan.query_id,
            plan_id=result.plan_id, outcome="planned_without_execution",
        )
        return result

    @staticmethod
    def decision(execution_plan: QueryExecutionPlan) -> PlannerDecision:
        """Recover the canonical decision embedded in an execution plan."""
        return PlannerDecision.from_dict(_thaw(execution_plan.metadata["decision"]))

    @staticmethod
    def report(execution_plan: QueryExecutionPlan) -> PlannerReport:
        """Recover the canonical planner report embedded in an execution plan."""
        return PlannerReport.from_dict(_thaw(execution_plan.metadata["report"]))

    @staticmethod
    def metrics(execution_plan: QueryExecutionPlan) -> PlannerMetrics:
        """Recover the canonical metrics embedded in an execution plan."""
        return PlannerMetrics.from_dict(_thaw(execution_plan.metadata["metrics"]))

    def _plan_id(
        self,
        query_plan: QueryPlan,
        statistics: LogicalStatistics,
        indexes: tuple[LogicalIndex, ...],
        chosen: _Candidate,
        metadata: Mapping[str, object],
    ) -> str:
        payload = {
            "indexes": [item.to_dict() for item in sorted(indexes, key=lambda item: item.id)],
            "metadata": metadata,
            "planner_version": PLANNER_VERSION,
            "query_plan": query_plan.to_dict(),
            "selected_candidate": chosen.name,
            "statistics": statistics.to_dict(),
        }
        encoded = json.dumps(
            payload, allow_nan=False, ensure_ascii=False,
            separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")
        return f"qep-{hashlib.sha256(encoded).hexdigest()}"


__all__ = ["CostBasedPlanner", "PLANNER_VERSION", "PlannerValidator"]
