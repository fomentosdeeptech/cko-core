"""Production contracts for the SPR-008N canonical query optimizer."""

from __future__ import annotations

import ast
import inspect
import logging
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import cko.core as core
import cko.core.discovery as discovery
from cko.core.discovery import (
    OPTIMIZER_SCHEMA_VERSION,
    BooleanNormalizationRule,
    ConstantExpressionRule,
    DuplicateProjectionRemovalRule,
    EmptyPredicateRule,
    FilterGroup,
    FilterGroupOperator,
    IdentityTransformationRule,
    LimitNormalizationRule,
    OptimizationCategory,
    OptimizationContext,
    OptimizationDecision,
    OptimizationDecisionStatus,
    OptimizationError,
    OptimizationMetrics,
    OptimizationPipeline,
    OptimizationReport,
    OptimizationResult,
    OptimizationRule,
    OptimizerValidationError,
    OptimizerValidator,
    PredicateSimplificationRule,
    ProjectionNormalizationRule,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryOrderingDirection,
    QueryPagination,
    QueryPlan,
    QueryProjection,
    RedundantFilterRemovalRule,
    SortNormalizationRule,
)


INSTANT = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)


def plan(
    *,
    filters: tuple[object, ...] = (),
    projections: tuple[QueryProjection, ...] = (),
    ordering: tuple[QueryOrdering, ...] = (),
    pagination: QueryPagination | None = None,
) -> QueryPlan:
    """Build one immutable logical plan without executing a query."""
    return QueryPlan(
        query_id="query-n", effective_filters=filters,
        projections=projections, ordering=ordering, pagination=pagination,
        estimates={"rows": 10}, justifications=("fixture",),
        timestamp=INSTANT,
    )


def context(query_plan: QueryPlan) -> OptimizationContext:
    """Build a minimal optimizer context for direct rule tests."""
    return OptimizationContext(query_plan, query_plan)


def complex_plan() -> QueryPlan:
    """Build a plan requiring several ordered passes to converge."""
    member = QueryFilter("kind", QueryOperator.IN, ("document",))
    group = FilterGroup(FilterGroupOperator.AND, (member, member))
    return plan(
        filters=(group, group),
        projections=(
            QueryProjection("zeta"), QueryProjection("alpha"),
            QueryProjection("zeta"),
        ),
        ordering=(QueryOrdering("name", priority=8),),
        pagination=QueryPagination(page=2, page_size=10),
    )


def optimized() -> OptimizationResult:
    """Return a complete deterministic optimization fixture."""
    return OptimizationPipeline().optimize(complex_plan())


def test_rule_contract_metadata_and_priority_order_are_complete() -> None:
    pipeline = OptimizationPipeline()
    assert [item.priority for item in pipeline.rules] == sorted(
        item.priority for item in pipeline.rules
    )
    assert {type(item) for item in pipeline.rules} == {
        PredicateSimplificationRule, BooleanNormalizationRule,
        RedundantFilterRemovalRule, DuplicateProjectionRemovalRule,
        ProjectionNormalizationRule, ConstantExpressionRule,
        SortNormalizationRule, LimitNormalizationRule, EmptyPredicateRule,
        IdentityTransformationRule,
    }
    for rule in pipeline.rules:
        assert rule.id and rule.name and rule.description and rule.version
        assert isinstance(rule.category, OptimizationCategory)
        assert rule.enabled and rule.deterministic


def test_predicate_simplification_collapses_unary_groups_and_double_not() -> None:
    member = QueryFilter("kind", QueryOperator.EQUALS, "document")
    unary = FilterGroup(FilterGroupOperator.AND, (member,))
    double_not = FilterGroup(
        FilterGroupOperator.NOT,
        (FilterGroup(FilterGroupOperator.NOT, (unary,)),),
    )
    result = PredicateSimplificationRule().apply(context(plan(filters=(double_not,))))
    assert result.effective_filters == (member,)


def test_boolean_normalization_flattens_and_orders_commutative_members() -> None:
    first = QueryFilter("z", QueryOperator.EQUALS, 1)
    second = QueryFilter("a", QueryOperator.EQUALS, 2)
    nested = FilterGroup(FilterGroupOperator.OR, (first, second))
    group = FilterGroup(FilterGroupOperator.OR, (first, nested))
    result = BooleanNormalizationRule().apply(context(plan(filters=(group,))))
    normalized = result.effective_filters[0]
    assert isinstance(normalized, FilterGroup)
    assert len(normalized.filters) == 3
    assert tuple(item.to_json() for item in normalized.filters) == tuple(sorted(
        item.to_json() for item in normalized.filters
    ))


def test_redundant_filters_are_removed_at_top_level_and_inside_groups() -> None:
    member = QueryFilter("kind", QueryOperator.EQUALS, "document")
    group = FilterGroup(FilterGroupOperator.AND, (member, member))
    result = RedundantFilterRemovalRule().apply(
        context(plan(filters=(group, group)))
    )
    assert len(result.effective_filters) == 1
    assert result.effective_filters[0].filters == (member,)


def test_projection_rules_deduplicate_then_normalize() -> None:
    source = plan(projections=(
        QueryProjection("z"), QueryProjection("a"), QueryProjection("z"),
    ))
    deduplicated = DuplicateProjectionRemovalRule().apply(context(source))
    normalized = ProjectionNormalizationRule().apply(context(deduplicated))
    assert tuple(item.attribute for item in normalized.projections) == ("a", "z")


@pytest.mark.parametrize(
    ("operator", "expected"),
    ((QueryOperator.IN, QueryOperator.EQUALS),
     (QueryOperator.NOT_IN, QueryOperator.NOT_EQUALS)),
)
def test_constant_expression_reduces_singleton_membership(
    operator: QueryOperator, expected: QueryOperator
) -> None:
    source = plan(filters=(QueryFilter("kind", operator, ("document",)),))
    result = ConstantExpressionRule().apply(context(source))
    assert result.effective_filters[0] == QueryFilter("kind", expected, "document")


def test_constant_expression_preserves_multi_value_membership() -> None:
    query_filter = QueryFilter("kind", QueryOperator.IN, ("a", "b"))
    source = plan(filters=(query_filter,))
    assert ConstantExpressionRule().apply(context(source)) is not source
    assert ConstantExpressionRule().apply(context(source)) == source


def test_sort_normalization_renumbers_and_removes_exact_duplicates() -> None:
    source = plan(ordering=(
        QueryOrdering("name", QueryOrderingDirection.ASCENDING, 5),
        QueryOrdering("name", QueryOrderingDirection.ASCENDING, 8),
        QueryOrdering("size", QueryOrderingDirection.DESCENDING, 12),
    ))
    result = SortNormalizationRule().apply(context(source))
    assert [(item.attribute, item.priority) for item in result.ordering] == [
        ("name", 0), ("size", 1),
    ]


@pytest.mark.parametrize(
    ("pagination", "expected"),
    ((QueryPagination(page=3, page_size=5), QueryPagination(offset=10, limit=5)),
     (QueryPagination(offset=4, limit=7), QueryPagination(offset=4, limit=7))),
)
def test_limit_normalization_preserves_result_boundaries(
    pagination: QueryPagination, expected: QueryPagination
) -> None:
    result = LimitNormalizationRule().apply(context(plan(pagination=pagination)))
    assert result.pagination == expected


def test_empty_and_identity_rules_preserve_the_same_plan() -> None:
    source = plan()
    assert EmptyPredicateRule().apply(context(source)) is source
    assert IdentityTransformationRule().apply(context(source)) is source


def test_pipeline_converges_over_multiple_iterations_and_is_reproducible() -> None:
    first = optimized()
    second = optimized()
    assert first.to_json() == second.to_json()
    assert first.total_iterations == 3
    assert first.optimized_plan.effective_filters == (
        QueryFilter("kind", QueryOperator.EQUALS, "document"),
    )
    assert first.optimization_gain > 0
    assert OptimizationPipeline.metrics(first).convergence


def test_pipeline_retains_original_plan_and_supports_reversal() -> None:
    source = complex_plan()
    result = OptimizationPipeline().optimize(source)
    assert result.original_plan is source
    assert result.revert() is source
    assert result.optimized_plan is not source


def test_disabled_rule_is_audited_as_skipped() -> None:
    pipeline = OptimizationPipeline((
        ConstantExpressionRule(enabled=False), IdentityTransformationRule(),
    ))
    result = pipeline.optimize(plan(filters=(
        QueryFilter("kind", QueryOperator.IN, ("document",)),
    )))
    assert result.rules_applied == ()
    assert "constant_expression" in result.rules_skipped


def test_pipeline_prevents_a_two_state_optimization_loop() -> None:
    class ToggleProjectionRule(OptimizationRule):
        id = "toggle"
        name = "Toggle"
        description = "Reverses projection order for loop testing."
        priority = 1
        category = OptimizationCategory.PROJECTION

        def apply(self, state: OptimizationContext) -> QueryPlan:
            """Reverse projection order."""
            return replace(
                state.current_plan,
                projections=tuple(reversed(state.current_plan.projections)),
            )

    result = OptimizationPipeline((ToggleProjectionRule(),)).optimize(
        plan(projections=(QueryProjection("a"), QueryProjection("b")))
    )
    assert result.total_iterations == 2
    assert result.rules_applied == ("toggle",)
    assert result.rules_skipped == ("toggle",)
    history = result.metadata["history"]
    assert "prevent an optimization loop" in history[-1]["justification"]


def test_maximum_iterations_is_enforced_when_a_rule_never_converges() -> None:
    class AuditRule(OptimizationRule):
        id = "audit"
        name = "Audit"
        description = "Adds a reversible audit justification."
        priority = 1
        category = OptimizationCategory.SAFETY

        def apply(self, state: OptimizationContext) -> QueryPlan:
            """Append one non-semantic audit entry."""
            reasons = (*state.current_plan.justifications,
                       f"iteration-{state.iterations}")
            return replace(state.current_plan, justifications=reasons)

    result = OptimizationPipeline((AuditRule(),), max_iterations=2).optimize(plan())
    metrics = OptimizationPipeline.metrics(result)
    assert result.total_iterations == 2
    assert not metrics.convergence
    assert result.rules_applied == ("audit", "audit")


def test_context_result_report_and_metrics_round_trip_strictly() -> None:
    result = optimized()
    report = OptimizationPipeline.report(result)
    metrics = OptimizationPipeline.metrics(result)
    decision = OptimizationDecision(
        "rule", "Rule", 1, OptimizationDecisionStatus.APPLIED, "valid",
        "before", "after",
    )
    state = OptimizationContext(
        result.original_plan, result.optimized_plan,
        statistics={"rows": 10}, indexes=({"id": "idx"},),
        history=(decision,), iterations=1, metadata={"locale": "pt-BR"},
    )
    models = (decision, state, report, metrics, result)
    for model in models:
        assert type(model).from_json(model.to_json()) == model
        malformed = model.to_dict()
        malformed["unknown"] = True
        with pytest.raises(ValueError, match="unknown"):
            type(model).from_dict(malformed)
    assert result.schema_version == OPTIMIZER_SCHEMA_VERSION


def test_result_report_and_metrics_are_coherent_and_immutable() -> None:
    result = optimized()
    report = OptimizationPipeline.report(result)
    metrics = OptimizationPipeline.metrics(result)
    assert report.original_plan == result.original_plan
    assert report.final_plan == result.optimized_plan
    assert metrics.iterations == result.total_iterations
    assert metrics.rules_executed == len(result.rules_applied) + len(
        result.rules_skipped
    )
    assert metrics.optimization_score == result.optimization_gain
    with pytest.raises(FrozenInstanceError):
        result.total_iterations = 99
    with pytest.raises(TypeError):
        result.metadata["changed"] = True


def test_optimizer_models_reject_malformed_values_and_envelopes() -> None:
    with pytest.raises(ValueError, match="invalid"):
        OptimizationMetrics.from_json("invalid")
    with pytest.raises(ValueError, match="object"):
        OptimizationMetrics.from_json("[]")
    wrong_schema = OptimizationMetrics(0, 0, 0, 0, True, 0).to_dict()
    wrong_schema["schema_version"] = "2.0"
    with pytest.raises(ValueError, match="schema"):
        OptimizationMetrics.from_dict(wrong_schema)
    wrong_model = OptimizationMetrics(0, 0, 0, 0, True, 0).to_dict()
    wrong_model["model"] = "other"
    with pytest.raises(ValueError, match="represent"):
        OptimizationMetrics.from_dict(wrong_model)
    with pytest.raises(ValueError, match="duration"):
        OptimizationMetrics(-1, 0, 0, 0, True, 0)
    with pytest.raises(ValueError, match="at most"):
        OptimizationMetrics(0, 0, 0, 0, True, 2)
    with pytest.raises(ValueError, match="status"):
        OptimizationDecision("rule", "Rule", 1, "invalid", "why", "a", "b")
    with pytest.raises(ValueError, match="indexes"):
        OptimizationContext(plan(), plan(), indexes=("invalid",))
    with pytest.raises(ValueError, match="timezone"):
        OptimizationReport((), (), (), plan(), plan(), datetime(2026, 1, 1))


def test_validator_checks_equivalence_integrity_consistency_and_timestamps() -> None:
    source = complex_plan()
    result = optimized().optimized_plan
    validator = OptimizerValidator()
    assert validator.validate(source, result) is result
    assert validator.structurally_equivalent(source, result)
    assert validator.is_valid(source, result)
    assert not validator.is_valid(source, replace(result, query_id="other"))
    with pytest.raises(OptimizerValidationError, match="estimates"):
        validator.validate(source, replace(result, estimates={"rows": 9}))
    with pytest.raises(OptimizerValidationError, match="timestamp"):
        validator.validate(
            source, replace(result, timestamp=INSTANT + timedelta(seconds=1))
        )
    invalid = replace(
        result,
        projections=(
            result.projections[0], result.projections[0], result.projections[1],
        ),
    )
    with pytest.raises(OptimizerValidationError, match="consistency"):
        validator.validate(source, invalid)


def test_invalid_pipeline_and_inputs_fail_explicitly() -> None:
    with pytest.raises(TypeError, match="positive"):
        OptimizationPipeline(max_iterations=True)
    with pytest.raises(ValueError, match="positive"):
        OptimizationPipeline(max_iterations=0)
    with pytest.raises(TypeError, match="rules"):
        OptimizationPipeline(("invalid",))
    with pytest.raises(TypeError, match="enabled"):
        IdentityTransformationRule(enabled=1)
    with pytest.raises(OptimizationError, match="query_plan"):
        OptimizationPipeline().optimize("invalid")
    with pytest.raises(OptimizationError, match="statistics"):
        OptimizationPipeline().optimize(plan(), statistics="invalid")


def test_rule_failures_and_invalid_return_types_are_wrapped() -> None:
    class FailingRule(OptimizationRule):
        id = "failing"
        name = "Failing"
        description = "Raises for testing."
        priority = 1
        category = OptimizationCategory.SAFETY

        def apply(self, state: OptimizationContext) -> QueryPlan:
            """Raise a controlled test error."""
            raise RuntimeError("failure")

    with pytest.raises(OptimizationError, match="failing"):
        OptimizationPipeline((FailingRule(),)).optimize(plan())


def test_logging_covers_the_required_optimizer_lifecycle(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        optimized()
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "discovery.query.optimizer.optimization_started",
        "discovery.query.optimizer.rule_started",
        "discovery.query.optimizer.rule_applied",
        "discovery.query.optimizer.rule_skipped",
        "discovery.query.optimizer.optimization_finished",
    } <= events


def test_public_api_type_hints_docstrings_utf8_pep8_and_boundaries() -> None:
    public = (
        OptimizationRule, OptimizationPipeline, OptimizationContext,
        OptimizationResult, OptimizationReport, OptimizationMetrics,
        OptimizerValidator, PredicateSimplificationRule,
        BooleanNormalizationRule, RedundantFilterRemovalRule,
        DuplicateProjectionRemovalRule, ProjectionNormalizationRule,
        ConstantExpressionRule, SortNormalizationRule, LimitNormalizationRule,
        EmptyPredicateRule, IdentityTransformationRule,
    )
    assert all(inspect.getdoc(item) for item in public)
    for method in (
        OptimizationPipeline.optimize, OptimizationPipeline.report,
        OptimizationPipeline.metrics, OptimizerValidator.validate,
        OptimizerValidator.structurally_equivalent,
    ):
        assert inspect.signature(method).return_annotation is not inspect.Signature.empty
        assert inspect.getdoc(method)
    for name in (
        "OptimizationPipeline", "OptimizationRule", "OptimizationResult",
        "OptimizationReport", "OptimizationMetrics", "OptimizerValidator",
        "PredicateSimplificationRule", "IdentityTransformationRule",
    ):
        assert getattr(core, name) is getattr(discovery, name)
        assert name in core.__all__ and name in discovery.__all__
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    prohibited = {
        "os", "pathlib", "sqlite3", "requests", "urllib", "http", "socket",
        "redis", "sqlalchemy", "cko.persistence", "cko.repository",
    }
    for name in (
        "optimizer_errors.py", "optimizer_models.py", "optimizer_rules.py",
        "optimizer.py",
    ):
        content = (root / name).read_bytes()
        assert not content.startswith(b"\xef\xbb\xbf")
        text = content.decode("utf-8")
        assert max(map(len, text.splitlines())) <= 99
        tree = ast.parse(text)
        imports = {
            alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not any(
            imported == blocked or imported.startswith(f"{blocked}.")
            for imported in imports for blocked in prohibited
        )
        assert "NotImplementedError" not in text
        assert "TODO" not in text
