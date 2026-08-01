"""Production contracts for the SPR-008M cost-based planner foundation."""

from __future__ import annotations

import ast
import inspect
import logging
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

import cko.core as core
import cko.core.discovery as discovery
from cko.core.discovery import (
    PLANNER_SCHEMA_VERSION,
    CostBasedPlanner,
    IndexStrategy,
    LogicalIndex,
    LogicalIndexBuilder,
    PlannerDecision,
    PlannerMetrics,
    PlannerPolicy,
    PlannerReport,
    PlannerValidationError,
    PlannerValidator,
    PlannerWeights,
    PlanningError,
    QueryExecutionPlan,
    QueryExecutionStrategy,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryPlan,
    QueryProjection,
    StatisticsBuilder,
)


INSTANT = datetime(2026, 7, 17, 21, 0, tzinfo=timezone.utc)
SUBJECTS = (
    {"id": "a", "kind": "document", "name": "Alpha", "size": 10},
    {"id": "b", "kind": "document", "name": "Beta", "size": 20},
    {"id": "c", "kind": "image", "name": "Atlas", "size": 30},
    {"id": "d", "kind": "video", "name": "Delta", "size": 40},
)


def index(
    index_id: str,
    attributes: tuple[str, ...],
    strategy: IndexStrategy,
) -> LogicalIndex:
    """Build a deterministic homologated logical index."""
    return LogicalIndexBuilder().build(
        index_id, f"Index {index_id}", SUBJECTS, attributes,
        strategy=strategy, relevant_attributes=("kind", "name", "size"),
        timestamp=INSTANT,
    )


def indexes() -> tuple[LogicalIndex, ...]:
    """Return candidates for every canonical index strategy."""
    return (
        index("idx-kind", ("kind",), IndexStrategy.HASH),
        index("idx-name", ("name",), IndexStrategy.PREFIX),
        index("idx-size", ("size",), IndexStrategy.ORDERED),
        index("idx-kind-name", ("kind", "name"), IndexStrategy.COMPOSITE),
    )


def query(
    query_filter: QueryFilter | None = None,
    *,
    ordering: tuple[QueryOrdering, ...] = (),
    projections: tuple[QueryProjection, ...] = (),
) -> QueryPlan:
    """Build an immutable query plan without executing it."""
    filters = (query_filter,) if query_filter is not None else ()
    return QueryPlan(
        query_id="query-m", effective_filters=filters,
        projections=projections, ordering=ordering, pagination=None,
        timestamp=INSTANT,
    )


def planned(
    query_plan: QueryPlan | None = None,
    declared: tuple[LogicalIndex, ...] | None = None,
    policy: PlannerPolicy | None = None,
) -> QueryExecutionPlan:
    """Plan one deterministic in-memory fixture."""
    candidates = declared or indexes()
    selected_query = query_plan or query(
        QueryFilter("kind", QueryOperator.EQUALS, "document")
    )
    statistics = StatisticsBuilder().build(candidates[0])
    return CostBasedPlanner(policy).plan(
        selected_query, statistics, candidates, timestamp=INSTANT
    )


def test_execution_strategies_are_complete_and_stable() -> None:
    assert {item.name for item in QueryExecutionStrategy} == {
        "FULL_SCAN", "INDEX_SCAN", "COMPOSITE_INDEX_SCAN",
        "PREFIX_INDEX_SCAN", "ORDERED_INDEX_SCAN",
    }


def test_weights_policy_and_models_are_frozen_and_versioned() -> None:
    weights = PlannerWeights()
    policy = PlannerPolicy(weights=weights)
    with pytest.raises(FrozenInstanceError):
        weights.cost = 10
    with pytest.raises(FrozenInstanceError):
        policy.index_limit = 2
    assert weights.total == 7.0
    assert policy.decision_weights is weights
    assert policy.schema_version == PLANNER_SCHEMA_VERSION


@pytest.mark.parametrize(
    "model",
    (
        PlannerWeights(),
        PlannerPolicy(),
        PlannerDecision(
            QueryExecutionStrategy.INDEX_SCAN, "lowest deterministic cost",
            (QueryExecutionStrategy.FULL_SCAN,), ("idx-old",), 0.9, 10.0,
            INSTANT,
        ),
        PlannerMetrics(0.0, 2, 2, 2, "chosen", ("discarded",)),
        PlannerReport(
            QueryExecutionStrategy.INDEX_SCAN,
            (QueryExecutionStrategy.FULL_SCAN,), ("idx-kind",), ("idx-old",),
            ("lowest deterministic cost",), ("stats",), 2.0, INSTANT,
        ),
    ),
)
def test_planner_models_round_trip_with_strict_schema(model: object) -> None:
    assert type(model).from_json(model.to_json()) == model
    malformed = model.to_dict()
    malformed["unknown"] = True
    with pytest.raises(ValueError, match="unknown"):
        type(model).from_dict(malformed)


def test_execution_plan_is_deeply_immutable_and_serializable() -> None:
    result = planned()
    with pytest.raises(FrozenInstanceError):
        result.estimated_cost = 0
    with pytest.raises(TypeError):
        result.metadata["new"] = True
    assert QueryExecutionPlan.from_json(result.to_json()) == result
    assert result.schema_version == PLANNER_SCHEMA_VERSION


@pytest.mark.parametrize(
    ("arguments", "message"),
    (
        ({"max_acceptable_cost": 0}, "positive"),
        ({"minimum_confidence": 2}, "between"),
        ({"allow_full_scan": 1}, "boolean"),
        ({"allow_multiple_indexes": False, "index_limit": 2}, "must be one"),
        ({"default_strategy": "invalid"}, "invalid"),
    ),
)
def test_policy_rejects_invalid_limits(arguments: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        PlannerPolicy(**arguments)


def test_strict_model_guards_reject_malformed_envelopes_and_invariants() -> None:
    with pytest.raises(ValueError, match="invalid"):
        PlannerWeights.from_json("invalid")
    with pytest.raises(ValueError, match="object"):
        PlannerWeights.from_json("[]")
    wrong_schema = PlannerWeights().to_dict()
    wrong_schema["schema_version"] = "2.0"
    with pytest.raises(ValueError, match="schema"):
        PlannerWeights.from_dict(wrong_schema)
    wrong_model = PlannerWeights().to_dict()
    wrong_model["model"] = "other"
    with pytest.raises(ValueError, match="represent"):
        PlannerWeights.from_dict(wrong_model)
    with pytest.raises(ValueError, match="at least one"):
        PlannerWeights(0, 0, 0, 0, 0, 0)
    with pytest.raises(ValueError, match="account"):
        PlannerMetrics(0.0, 1, 1, 3, "one", ("two",))
    with pytest.raises(ValueError, match="chosen"):
        PlannerDecision(
            QueryExecutionStrategy.FULL_SCAN, "invalid",
            (QueryExecutionStrategy.FULL_SCAN,), (), 1.0, 0.0, INSTANT,
        )
    with pytest.raises(ValueError, match="also be discarded"):
        PlannerReport(
            QueryExecutionStrategy.INDEX_SCAN, (), ("idx",), ("idx",),
            ("invalid",), ("stats",), 1.0, INSTANT,
        )


def test_execution_plan_strategy_and_index_invariants_are_enforced() -> None:
    result = planned()
    with pytest.raises(ValueError, match="full scan"):
        replace(
            result, execution_strategy=QueryExecutionStrategy.FULL_SCAN,
            selected_indexes=("idx",),
        )
    with pytest.raises(ValueError, match="requires selected"):
        replace(result, selected_indexes=())
    with pytest.raises(ValueError, match="unique"):
        replace(result, selected_indexes=("idx", "idx"))


def test_invalid_planner_and_validator_inputs_fail_explicitly() -> None:
    with pytest.raises(TypeError, match="policy"):
        CostBasedPlanner("invalid")
    with pytest.raises(TypeError, match="estimator"):
        CostBasedPlanner(estimator="invalid")
    assert not PlannerValidator().is_valid("invalid")
    candidate = indexes()[0]
    statistics = StatisticsBuilder().build(candidate)
    planner = CostBasedPlanner()
    with pytest.raises(PlanningError, match="query_plan"):
        planner.plan("invalid", statistics, (candidate,))
    with pytest.raises(PlanningError, match="statistics"):
        planner.plan(query(), "invalid", (candidate,))


def test_planner_is_deterministic_reproducible_and_does_not_mutate_inputs() -> None:
    candidates = indexes()
    selected_query = query(QueryFilter("kind", QueryOperator.EQUALS, "document"))
    statistics = StatisticsBuilder().build(candidates[0])
    before = tuple(item.to_json() for item in candidates)
    planner = CostBasedPlanner()
    first = planner.plan(selected_query, statistics, reversed(candidates))
    second = planner.plan(selected_query, statistics, candidates)
    assert first.to_json() == second.to_json()
    assert first.plan_id == second.plan_id
    assert tuple(item.to_json() for item in candidates) == before


def test_hash_composite_prefix_and_ordered_strategies_are_planned() -> None:
    scenarios = (
        (QueryFilter("kind", QueryOperator.EQUALS, "document"), indexes()[0],
         QueryExecutionStrategy.INDEX_SCAN),
        (QueryFilter("kind", QueryOperator.EQUALS, "document"), indexes()[3],
         QueryExecutionStrategy.COMPOSITE_INDEX_SCAN),
        (QueryFilter("name", QueryOperator.STARTS_WITH, "A"), indexes()[1],
         QueryExecutionStrategy.PREFIX_INDEX_SCAN),
        (QueryFilter("size", QueryOperator.GREATER_THAN, 20), indexes()[2],
         QueryExecutionStrategy.ORDERED_INDEX_SCAN),
    )
    for query_filter, candidate, expected in scenarios:
        result = planned(query(query_filter), (candidate,))
        assert result.execution_strategy is expected
        assert result.selected_indexes == (candidate.id,)


def test_ordered_index_can_cover_ordering_without_a_filter() -> None:
    candidate = indexes()[2]
    result = planned(query(ordering=(QueryOrdering("size"),)), (candidate,))
    assert result.execution_strategy is QueryExecutionStrategy.ORDERED_INDEX_SCAN


def test_full_scan_is_a_policy_controlled_fallback() -> None:
    candidate = indexes()[0]
    selected_query = query(QueryFilter("unknown", QueryOperator.EQUALS, "x"))
    result = planned(selected_query, (candidate,))
    assert result.execution_strategy is QueryExecutionStrategy.FULL_SCAN
    assert result.selected_indexes == ()
    with pytest.raises(PlanningError, match="no candidate"):
        planned(selected_query, (candidate,), PlannerPolicy(allow_full_scan=False))


def test_multiple_index_policy_can_produce_a_composite_plan() -> None:
    candidates = (indexes()[0], indexes()[2])
    selected_query = QueryPlan(
        query_id="multi",
        effective_filters=(
            QueryFilter("kind", QueryOperator.EQUALS, "document"),
            QueryFilter("size", QueryOperator.GREATER_THAN, 10),
        ),
        projections=(), ordering=(), pagination=None, timestamp=INSTANT,
    )
    policy = PlannerPolicy(allow_multiple_indexes=True, index_limit=2)
    result = planned(selected_query, candidates, policy)
    assert result.execution_strategy is QueryExecutionStrategy.COMPOSITE_INDEX_SCAN
    assert result.selected_indexes == ("idx-kind", "idx-size")


def test_decision_report_and_metrics_are_coherent_and_auditable() -> None:
    result = planned()
    decision = CostBasedPlanner.decision(result)
    report = CostBasedPlanner.report(result)
    metrics = CostBasedPlanner.metrics(result)
    assert decision.strategy is result.execution_strategy
    assert report.chosen_strategy is result.execution_strategy
    assert report.indexes_used == result.selected_indexes
    assert report.final_cost == result.estimated_cost
    assert metrics.indexes_evaluated == 4
    assert metrics.total_candidates == len(metrics.discarded_candidates) + 1
    assert "no query was executed" in report.justifications[1]


def test_validator_checks_strategy_cost_indexes_coherence_and_policy() -> None:
    candidates = indexes()
    result = planned(declared=candidates)
    validator = PlannerValidator()
    assert validator.validate(result, indexes=candidates) is result
    assert validator.is_valid(result, indexes=candidates)
    strict = PlannerPolicy(max_acceptable_cost=0.0001)
    with pytest.raises(PlannerValidationError, match="cost"):
        validator.validate(result, policy=strict, indexes=candidates)
    with pytest.raises(PlannerValidationError, match="unavailable"):
        validator.validate(result, indexes=(candidates[1],))


def test_tie_breaking_is_independent_of_index_input_order() -> None:
    first = index("idx-a", ("kind",), IndexStrategy.HASH)
    second = index("idx-b", ("kind",), IndexStrategy.HASH)
    selected_query = query(QueryFilter("kind", QueryOperator.EQUALS, "document"))
    statistics = StatisticsBuilder().build(first)
    planner = CostBasedPlanner()
    forward = planner.plan(selected_query, statistics, (first, second))
    backward = planner.plan(selected_query, statistics, (second, first))
    assert forward.plan_id == backward.plan_id
    assert forward.selected_indexes == ("idx-a",)


def test_logging_covers_required_planner_lifecycle(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        planned()
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "discovery.query.planner.planning_started",
        "discovery.query.planner.analysis_completed",
        "discovery.query.planner.comparison_completed",
        "discovery.query.planner.decision_completed",
        "discovery.query.planner.planning_completed",
    } <= events


def test_public_api_type_hints_docstrings_utf8_pep8_and_boundaries() -> None:
    public = (
        QueryExecutionStrategy, QueryExecutionPlan, PlannerDecision,
        PlannerPolicy, PlannerWeights, CostBasedPlanner, PlannerValidator,
        PlannerReport, PlannerMetrics,
    )
    assert all(inspect.getdoc(item) for item in public)
    for method in (
        CostBasedPlanner.plan, CostBasedPlanner.decision, CostBasedPlanner.report,
        CostBasedPlanner.metrics, PlannerValidator.validate,
    ):
        assert inspect.signature(method).return_annotation is not inspect.Signature.empty
        assert inspect.getdoc(method)
    for name in (
        "CostBasedPlanner", "PlannerPolicy", "PlannerWeights", "PlannerMetrics",
        "PlannerValidator", "QueryExecutionPlan", "QueryExecutionStrategy",
    ):
        assert getattr(core, name) is getattr(discovery, name)
        assert name in core.__all__ and name in discovery.__all__
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    prohibited = {
        "os", "pathlib", "sqlite3", "requests", "urllib", "http", "socket",
        "redis", "sqlalchemy", "cko.persistence", "cko.repository",
    }
    for name in ("planner_errors.py", "planner_models.py", "planner.py"):
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
