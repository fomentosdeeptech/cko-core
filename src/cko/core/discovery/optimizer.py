"""Deterministic, auditable and infrastructure-neutral query optimizer."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import datetime
from typing import Iterable, Mapping

from cko.core.logging import get_logger

from .optimizer_errors import OptimizationError, OptimizerValidationError
from .optimizer_models import (
    OptimizationContext,
    OptimizationDecision,
    OptimizationDecisionStatus,
    OptimizationMetrics,
    OptimizationReport,
    OptimizationResult,
)
from .optimizer_rules import CANONICAL_OPTIMIZATION_RULES, OptimizationRule
from .query_models import (
    FilterGroup,
    FilterGroupOperator,
    QueryExpression,
    QueryFilter,
    QueryOperator,
    QueryPagination,
    QueryPlan,
)
from .query_validation import QueryValidationEngine


OPTIMIZER_VERSION = "1.0.0"


def _event(logger: object, name: str, **context: object) -> None:
    logger.info(
        name.replace("_", " "),
        extra={
            "event": f"discovery.query.optimizer.{name}",
            "context": dict(sorted(context.items())),
        },
    )


def _fingerprint(plan: QueryPlan) -> str:
    return hashlib.sha256(plan.to_json().encode("utf-8")).hexdigest()


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return value
    serializer = getattr(value, "to_dict", None)
    if callable(serializer):
        result = serializer()
        if isinstance(result, Mapping):
            return result
    raise OptimizationError(f"{name} must be a mapping or canonical model")


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _expression_signature(expression: QueryExpression) -> tuple[object, ...]:
    if isinstance(expression, QueryFilter):
        operator = expression.operator
        value = expression.value
        if operator is QueryOperator.IN and len(value) == 1:
            operator, value = QueryOperator.EQUALS, value[0]
        elif operator is QueryOperator.NOT_IN and len(value) == 1:
            operator, value = QueryOperator.NOT_EQUALS, value[0]
        rendered = QueryFilter(expression.attribute, operator, value).to_json()
        return ("filter", rendered)
    nested = [_expression_signature(item) for item in expression.filters]
    operator = expression.operator
    if operator in {FilterGroupOperator.AND, FilterGroupOperator.OR}:
        flattened = []
        for item in nested:
            if item[:2] == ("group", operator.value):
                flattened.extend(item[2])
            else:
                flattened.append(item)
        unique = {repr(item): item for item in flattened}
        members = tuple(unique[key] for key in sorted(unique))
        if len(members) == 1:
            return members[0]
        return ("group", operator.value, members)
    child = nested[0]
    if child[:2] == ("group", FilterGroupOperator.NOT.value):
        return child[2][0]
    return ("group", operator.value, tuple(nested))


def _semantic_signature(plan: QueryPlan) -> tuple[object, ...]:
    filters = [_expression_signature(item) for item in plan.effective_filters]
    unique_filters = {repr(item): item for item in filters}
    predicates = tuple(unique_filters[key] for key in sorted(unique_filters))
    projections = tuple(sorted({item.attribute for item in plan.projections}))
    ordering = tuple((item.attribute, item.direction.value)
                     for item in plan.ordering)
    pagination = plan.pagination
    if pagination is None:
        boundary = None
    else:
        offset = ((pagination.page - 1) * pagination.page_size
                  if pagination.page is not None
                  else pagination.offset or 0)
        limit = pagination.limit or pagination.page_size
        boundary = (offset, limit)
    return (plan.query_id, predicates, projections, ordering, boundary)


class OptimizerValidator:
    """Validate structural integrity and semantic preservation of query plans."""

    def structurally_equivalent(
        self, original: QueryPlan, optimized: QueryPlan
    ) -> bool:
        """Return whether both plans have the same normalized logical meaning."""
        if not isinstance(original, QueryPlan) or not isinstance(optimized, QueryPlan):
            return False
        return _semantic_signature(original) == _semantic_signature(optimized)

    def validate(
        self, original: QueryPlan, optimized: QueryPlan
    ) -> QueryPlan:
        """Return the optimized plan or raise on integrity or semantic loss."""
        self.validate_equivalence(original, optimized)
        validator = QueryValidationEngine()
        try:
            validator.validate_filters(optimized.effective_filters)
            validator.validate_projections(optimized.projections)
            validator.validate_ordering(optimized.ordering)
        except ValueError as error:
            raise OptimizerValidationError(
                "optimized plan failed canonical consistency validation"
            ) from error
        return optimized

    def validate_equivalence(
        self, original: QueryPlan, optimized: QueryPlan
    ) -> QueryPlan:
        """Validate an intermediate plan before all normalizers have run."""
        if not isinstance(original, QueryPlan):
            raise OptimizerValidationError("original must be QueryPlan")
        if not isinstance(optimized, QueryPlan):
            raise OptimizerValidationError("optimized must be QueryPlan")
        self._assert_acyclic(optimized)
        if original.estimates != optimized.estimates:
            raise OptimizerValidationError("optimization changed plan estimates")
        if original.timestamp != optimized.timestamp:
            raise OptimizerValidationError("optimization changed plan timestamp")
        if not self.structurally_equivalent(original, optimized):
            raise OptimizerValidationError(
                "optimized plan is not structurally and semantically equivalent"
            )
        return optimized

    def is_valid(self, original: object, optimized: object) -> bool:
        """Return a boolean validation result without suppressing strict errors."""
        try:
            self.validate(original, optimized)
        except (TypeError, ValueError):
            return False
        return True

    @classmethod
    def _assert_acyclic(cls, plan: QueryPlan) -> None:
        active: set[int] = set()

        def visit(expression: QueryExpression) -> None:
            identity = id(expression)
            if identity in active:
                raise OptimizerValidationError("filter expression cycle detected")
            if not isinstance(expression, FilterGroup):
                return
            active.add(identity)
            for item in expression.filters:
                visit(item)
            active.remove(identity)

        for expression in plan.effective_filters:
            visit(expression)


class OptimizationPipeline:
    """Run ordered optimization rules to a validated deterministic fixed point."""

    def __init__(
        self,
        rules: Iterable[OptimizationRule] | None = None,
        *,
        max_iterations: int = 8,
        validator: OptimizerValidator | None = None,
    ) -> None:
        """Create a pipeline with canonical rules and bounded convergence."""
        if isinstance(max_iterations, bool) or not isinstance(max_iterations, int):
            raise TypeError("max_iterations must be a positive integer")
        if max_iterations < 1:
            raise ValueError("max_iterations must be a positive integer")
        declared = (tuple(rules) if rules is not None else
                    tuple(rule() for rule in CANONICAL_OPTIMIZATION_RULES))
        if any(not isinstance(item, OptimizationRule) for item in declared):
            raise TypeError("rules must contain OptimizationRule instances")
        ids = [item.id for item in declared]
        if len(ids) != len(set(ids)):
            raise ValueError("optimization rule ids must be unique")
        self._rules = tuple(sorted(declared, key=lambda item: (
            item.priority, item.id
        )))
        self._max_iterations = max_iterations
        self._validator = validator or OptimizerValidator()
        if not isinstance(self._validator, OptimizerValidator):
            raise TypeError("validator must be OptimizerValidator")
        self._logger = get_logger("core.discovery.query.optimizer")

    @property
    def rules(self) -> tuple[OptimizationRule, ...]:
        """Return rules in their deterministic execution order."""
        return self._rules

    def optimize(
        self,
        query_plan: QueryPlan,
        *,
        statistics: object = None,
        indexes: Iterable[object] = (),
        metadata: Mapping[str, object] | None = None,
        timestamp: datetime | None = None,
    ) -> OptimizationResult:
        """Optimize a query plan without selecting or executing a strategy."""
        if not isinstance(query_plan, QueryPlan):
            raise OptimizationError("query_plan must be QueryPlan")
        normalized_indexes = tuple(_mapping(item, "index") for item in indexes)
        instant = timestamp or query_plan.timestamp
        context = OptimizationContext(
            original_plan=query_plan,
            current_plan=query_plan,
            statistics=_mapping(statistics, "statistics"),
            indexes=normalized_indexes,
            metadata=metadata or {},
        )
        history: list[OptimizationDecision] = []
        seen = {_fingerprint(query_plan)}
        converged = False
        _event(self._logger, "optimization_started",
               query_id=query_plan.query_id, rule_count=len(self._rules))
        for iteration in range(1, self._max_iterations + 1):
            modified = False
            for rule in self._rules:
                _event(self._logger, "rule_started", iteration=iteration,
                       rule_id=rule.id)
                before = context.current_plan
                before_hash = _fingerprint(before)
                reason = "rule reached a fixed point"
                status = OptimizationDecisionStatus.SKIPPED
                after = before
                if not rule.enabled:
                    reason = "rule is disabled"
                elif not rule.deterministic:
                    reason = "non-deterministic rules are not permitted"
                else:
                    try:
                        candidate = rule.apply(context)
                    except Exception as error:
                        raise OptimizationError(
                            f"optimization rule {rule.id} failed"
                        ) from error
                    if not isinstance(candidate, QueryPlan):
                        raise OptimizationError(
                            f"optimization rule {rule.id} did not return QueryPlan"
                        )
                    candidate_hash = _fingerprint(candidate)
                    if candidate_hash != before_hash and candidate_hash in seen:
                        reason = "rule result was skipped to prevent an optimization loop"
                    elif candidate_hash != before_hash:
                        self._validator.validate_equivalence(query_plan, candidate)
                        after = candidate
                        status = OptimizationDecisionStatus.APPLIED
                        reason = "rule produced a validated equivalent plan"
                        modified = True
                        seen.add(candidate_hash)
                after_hash = _fingerprint(after)
                decision = OptimizationDecision(
                    rule.id, rule.name, iteration, status, reason,
                    before_hash, after_hash,
                )
                history.append(decision)
                context = replace(
                    context, current_plan=after, history=tuple(history),
                    iterations=iteration,
                )
                event = ("rule_applied" if status is OptimizationDecisionStatus.APPLIED
                         else "rule_skipped")
                _event(self._logger, event, iteration=iteration,
                       rule_id=rule.id, justification=reason)
            if not modified:
                converged = True
                break
        self._validator.validate(query_plan, context.current_plan)
        gain = self._gain(query_plan, context.current_plan)
        applied = tuple(item.rule_id for item in history
                        if item.status is OptimizationDecisionStatus.APPLIED)
        skipped = tuple(item.rule_id for item in history
                        if item.status is OptimizationDecisionStatus.SKIPPED)
        metrics = OptimizationMetrics(
            duration=0.0, iterations=context.iterations,
            rules_executed=len(history), rules_skipped=len(skipped),
            convergence=converged, optimization_score=gain,
        )
        report = OptimizationReport(
            rules_executed=applied, rules_skipped=skipped,
            justifications=tuple(item.justification for item in history),
            original_plan=query_plan, final_plan=context.current_plan,
            timestamp=instant,
        )
        result = OptimizationResult(
            original_plan=query_plan, optimized_plan=context.current_plan,
            rules_applied=applied, rules_skipped=skipped,
            total_iterations=context.iterations, optimization_gain=gain,
            metadata={
                "converged": converged,
                "history": [item.to_dict() for item in history],
                "metrics": metrics.to_dict(),
                "optimizer_version": OPTIMIZER_VERSION,
                "report": report.to_dict(),
            },
        )
        _event(self._logger, "optimization_finished",
               query_id=query_plan.query_id, converged=converged,
               iterations=context.iterations, gain=gain)
        return result

    @staticmethod
    def report(result: OptimizationResult) -> OptimizationReport:
        """Recover the canonical audit report embedded in a result."""
        if not isinstance(result, OptimizationResult):
            raise TypeError("result must be OptimizationResult")
        return OptimizationReport.from_dict(_thaw(result.metadata["report"]))

    @staticmethod
    def metrics(result: OptimizationResult) -> OptimizationMetrics:
        """Recover deterministic metrics embedded in a result."""
        if not isinstance(result, OptimizationResult):
            raise TypeError("result must be OptimizationResult")
        return OptimizationMetrics.from_dict(_thaw(result.metadata["metrics"]))

    @classmethod
    def _gain(cls, original: QueryPlan, optimized: QueryPlan) -> float:
        before = cls._size(original)
        after = cls._size(optimized)
        return max(0.0, min(1.0, (before - after) / before))

    @classmethod
    def _size(cls, plan: QueryPlan) -> int:
        def expression_size(expression: QueryExpression) -> int:
            if not isinstance(expression, FilterGroup):
                return 1
            return 1 + sum(expression_size(item) for item in expression.filters)

        return max(1, 1 + sum(expression_size(item)
                              for item in plan.effective_filters)
                   + len(plan.projections) + len(plan.ordering)
                   + int(plan.pagination is not None))


__all__ = [
    "OPTIMIZER_VERSION", "OptimizationPipeline", "OptimizerValidator",
]
