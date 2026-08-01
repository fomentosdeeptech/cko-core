"""Production contracts for the SPR-008P canonical execution engine."""

from __future__ import annotations

import ast
import inspect
import logging
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

import cko.core as core
from cko.core.discovery import (
    ExecutionNode,
    ExecutionNodeType,
    ExecutionPipeline as PlannerPipeline,
    ExecutionPlan,
    QueryExecutionPlan,
    QueryExecutionStrategy,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryPagination,
    QueryPlan,
    QueryProjection,
)
from cko.core.execution import (
    ENGINE_SCHEMA_VERSION,
    CompositeIndexScanOperator,
    ExecutionContext,
    ExecutionEngine,
    ExecutionEngineError,
    ExecutionEngineValidationError,
    ExecutionEngineValidator,
    ExecutionMetrics,
    ExecutionOperator,
    ExecutionOperatorError,
    ExecutionPipeline,
    ExecutionPipelineError,
    ExecutionResult,
    ExecutionState,
    FilterOperator,
    IndexScanOperator,
    InvalidExecutionEngineModelError,
    LimitOperator,
    OperatorResult,
    OrderedScanOperator,
    PrefixScanOperator,
    ProjectionOperator,
    RootOperator,
    ScanOperator,
    SortOperator,
    canonical_operators,
    deterministic_execution_id,
)


INSTANT = datetime(2026, 7, 18, 20, 0, tzinfo=timezone.utc)
SOURCE = Path(__file__).parents[1] / "src" / "cko" / "core" / "execution"


def logical_plan(*, complete: bool = True) -> QueryPlan:
    """Build one immutable logical plan without executing it."""
    return QueryPlan(
        query_id="query-p",
        effective_filters=(
            QueryFilter("kind", QueryOperator.EQUALS, "document"),
        ) if complete else (),
        projections=(QueryProjection("name"),) if complete else (),
        ordering=(QueryOrdering("name"),) if complete else (),
        pagination=QueryPagination(page=2, page_size=10) if complete else None,
        estimates={"rows": 4},
        justifications=("fixture",),
        timestamp=INSTANT,
    )


def query_execution_plan(
    strategy: QueryExecutionStrategy = QueryExecutionStrategy.INDEX_SCAN,
    *,
    complete: bool = True,
) -> QueryExecutionPlan:
    """Build a deterministic homologated planner output fixture."""
    indexes = () if strategy is QueryExecutionStrategy.FULL_SCAN else ("idx",)
    return QueryExecutionPlan(
        plan_id=f"qep-{strategy.value}",
        query_plan=logical_plan(complete=complete),
        execution_strategy=strategy,
        selected_indexes=indexes,
        estimated_cost=2.0,
        estimated_rows=4,
        estimated_selectivity=0.5,
        confidence=0.9,
        planning_time=0.0,
        planner_version="1.0.0",
        timestamp=INSTANT,
        metadata={"source": "test"},
    )


def physical_plan(
    strategy: QueryExecutionStrategy = QueryExecutionStrategy.INDEX_SCAN,
    *,
    complete: bool = True,
) -> ExecutionPlan:
    """Build one canonical physical plan entirely in memory."""
    return PlannerPipeline().build(
        query_execution_plan(strategy, complete=complete)
    )


def flatten(node: ExecutionNode) -> tuple[ExecutionNode, ...]:
    """Return nodes in deterministic pre-order."""
    return (node, *(child for item in node.children for child in flatten(item)))


def test_engine_executes_complete_tree_in_deterministic_preorder() -> None:
    plan = physical_plan()
    expected = tuple(node.node_id for node in flatten(plan.root_node))
    first = ExecutionEngine().execute(plan)
    second = ExecutionEngine().execute(plan)
    assert first.executed_nodes == expected
    assert first.skipped_nodes == ()
    assert first.success is True
    assert first == second
    assert first.to_json() == second.to_json()
    assert first.metadata["final_state"] == "completed"


@pytest.mark.parametrize("strategy", tuple(QueryExecutionStrategy))
def test_every_access_strategy_has_an_executable_operator(
    strategy: QueryExecutionStrategy,
) -> None:
    plan = physical_plan(strategy, complete=False)
    result = ExecutionEngine().execute(plan)
    assert len(result.executed_nodes) == 2
    assert result.statistics.nodes_executed == 2
    assert result.statistics.maximum_depth == 2


def test_pipeline_requires_running_context_and_preserves_stack() -> None:
    context = ExecutionContext(physical_plan())
    pipeline = ExecutionPipeline()
    with pytest.raises(ExecutionPipelineError, match="RUNNING"):
        pipeline.execute(context)
    context.transition_to(ExecutionState.READY)
    context.transition_to(ExecutionState.RUNNING)
    result = pipeline.execute(context)
    assert result.executed_nodes
    assert context.execution_stack == ()


def test_state_machine_accepts_only_canonical_transitions() -> None:
    context = ExecutionContext(physical_plan())
    assert context.state is ExecutionState.CREATED
    context.transition_to(ExecutionState.READY)
    context.transition_to(ExecutionState.RUNNING)
    context.transition_to(ExecutionState.COMPLETED)
    with pytest.raises(InvalidExecutionEngineModelError, match="transition"):
        context.transition_to(ExecutionState.RUNNING)
    assert {item.value for item in ExecutionState} == {
        "created", "ready", "running", "completed", "failed", "cancelled",
    }


def test_context_contains_plan_metadata_statistics_id_and_stack() -> None:
    plan = physical_plan()
    first = ExecutionContext(plan, metadata={"ação": "validação"})
    second = ExecutionContext(plan, metadata={"ação": "validação"})
    assert first.execution_plan is plan
    assert first.execution_id == second.execution_id
    assert first.metadata["ação"] == "validação"
    assert first.statistics == {}
    first.push("node-x")
    assert first.execution_stack == ("node-x",)
    assert first.pop() == "node-x"


def test_result_is_immutable_versioned_and_round_trips() -> None:
    result = ExecutionEngine().execute(physical_plan())
    restored = ExecutionResult.from_json(result.to_json())
    assert restored == result
    assert restored.schema_version == ENGINE_SCHEMA_VERSION
    assert "validação" in ExecutionEngine().execute(
        physical_plan(), metadata={"texto": "validação"}
    ).to_json()
    with pytest.raises(FrozenInstanceError):
        result.success = False  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.metadata["x"] = 1  # type: ignore[index]


def test_metrics_validate_duration_counts_depth_warnings_and_metadata() -> None:
    metrics = ExecutionMetrics(
        duration=0,
        nodes_executed=2,
        maximum_depth=2,
        warnings=("logical warning",),
        metadata={"deterministic": True},
    )
    assert ExecutionMetrics.from_dict(metrics.to_dict()) == metrics
    with pytest.raises(InvalidExecutionEngineModelError):
        ExecutionMetrics(-1, 1, 1)
    with pytest.raises(InvalidExecutionEngineModelError):
        ExecutionMetrics(0, 1, 0)


def test_all_ten_canonical_operator_contracts_are_registered() -> None:
    registry = canonical_operators()
    classes = {
        ScanOperator, FilterOperator, ProjectionOperator, SortOperator,
        LimitOperator, IndexScanOperator, CompositeIndexScanOperator,
        PrefixScanOperator, OrderedScanOperator, RootOperator,
    }
    assert set(registry) == set(ExecutionNodeType)
    assert {type(item) for item in registry.values()} == classes
    assert inspect.isabstract(ExecutionOperator)
    assert all(isinstance(item, ExecutionOperator) for item in registry.values())


def test_validator_checks_plan_context_state_and_operator_integrity() -> None:
    plan = physical_plan()
    validator = ExecutionEngineValidator()
    assert validator.validate(plan) is plan
    assert validator.validate_context(ExecutionContext(plan)).execution_plan is plan
    assert validator.is_valid(plan)
    incomplete = dict(canonical_operators())
    incomplete.pop(ExecutionNodeType.ROOT)
    with pytest.raises(ExecutionEngineValidationError, match="missing"):
        validator.validate(plan, incomplete)
    assert not validator.is_valid("invalid")


class SkippingFilterOperator(FilterOperator):
    """Test operator that deterministically skips filters."""

    def execute(
        self, node: ExecutionNode, context: ExecutionContext,
    ) -> OperatorResult:
        """Return a deterministic skipped outcome."""
        assert self.supports(node)
        assert context.state is ExecutionState.RUNNING
        return OperatorResult(skipped=True, warnings=("filter skipped",))


def test_custom_operator_controls_skips_and_warnings() -> None:
    operators = dict(canonical_operators())
    operators[ExecutionNodeType.FILTER] = SkippingFilterOperator()
    result = ExecutionEngine(operators).execute(physical_plan())
    assert len(result.skipped_nodes) == 1
    assert result.warnings == ("filter skipped",)
    assert result.statistics.warnings == result.warnings
    assert result.statistics.nodes_executed == len(result.executed_nodes)


def test_required_structured_logging_events_are_emitted(caplog) -> None:
    caplog.set_level(logging.INFO, logger="cko.core.execution.engine")
    result = ExecutionEngine().execute(physical_plan())
    events = [getattr(record, "event", "") for record in caplog.records]
    assert "core.execution.engine.execution_started" in events
    assert "core.execution.engine.node_execution_started" in events
    assert "core.execution.engine.node_execution_finished" in events
    assert "core.execution.engine.execution_finished" in events
    assert len([
        item for item in events if item.endswith("node_execution_started")
    ]) == len(result.executed_nodes)


def test_execution_failed_is_logged_for_invalid_plan(caplog) -> None:
    caplog.set_level(logging.ERROR, logger="cko.core.execution.engine")
    with pytest.raises(InvalidExecutionEngineModelError):
        ExecutionEngine().execute("invalid")  # type: ignore[arg-type]
    assert any(
        getattr(record, "event", "").endswith("execution_failed")
        for record in caplog.records
    )


def test_public_api_preserves_planner_names_and_adds_engine_aliases() -> None:
    assert core.ExecutionContext.__module__.endswith("execution_models")
    assert core.ExecutionPipeline.__module__.endswith("execution_planner")
    assert core.EngineExecutionContext is ExecutionContext
    assert core.EngineExecutionPipeline is ExecutionPipeline
    assert core.EngineExecutionMetrics is ExecutionMetrics
    assert core.ExecutionEngine is ExecutionEngine
    assert core.ExecutionResult is ExecutionResult


def test_model_negative_contracts_and_context_serialization() -> None:
    plan = physical_plan()
    context = ExecutionContext(plan)
    assert context.to_dict()["execution_plan"] == plan.to_dict()
    assert '"model":"execution_engine_context"' in context.to_json()
    with pytest.raises(InvalidExecutionEngineModelError, match="plan"):
        deterministic_execution_id("invalid")  # type: ignore[arg-type]
    with pytest.raises(InvalidExecutionEngineModelError, match="state"):
        ExecutionContext(plan, state="invalid")  # type: ignore[arg-type]
    with pytest.raises(InvalidExecutionEngineModelError, match="metadata"):
        ExecutionContext(plan, metadata=[])  # type: ignore[arg-type]
    with pytest.raises(InvalidExecutionEngineModelError, match="unsupported"):
        ExecutionContext(plan, metadata={"bad": object()})
    with pytest.raises(InvalidExecutionEngineModelError, match="finite"):
        ExecutionContext(plan, metadata={"bad": float("nan")})
    with pytest.raises(InvalidExecutionEngineModelError, match="target state"):
        context.transition_to("invalid")  # type: ignore[arg-type]
    context.push("node")
    with pytest.raises(InvalidExecutionEngineModelError, match="cycle"):
        context.push("node")
    context.pop()
    with pytest.raises(InvalidExecutionEngineModelError, match="empty"):
        context.pop()


def test_result_and_metrics_reject_invalid_envelopes_and_values() -> None:
    result = ExecutionEngine().execute(physical_plan())
    metrics = result.statistics
    with pytest.raises(InvalidExecutionEngineModelError, match="metrics"):
        ExecutionMetrics.from_dict({})
    with pytest.raises(InvalidExecutionEngineModelError, match="JSON"):
        ExecutionResult.from_json("invalid")
    with pytest.raises(InvalidExecutionEngineModelError, match="object"):
        ExecutionResult.from_json("[]")
    payload = result.to_dict()
    payload.pop("model")
    with pytest.raises(InvalidExecutionEngineModelError, match="envelope"):
        ExecutionResult.from_dict(payload)
    required = {
        "execution_id": result.execution_id,
        "success": True,
        "executed_nodes": ("one",),
        "skipped_nodes": (),
        "warnings": (),
        "metadata": {},
        "statistics": metrics,
    }
    with pytest.raises(InvalidExecutionEngineModelError, match="boolean"):
        ExecutionResult(**{**required, "success": 1})
    with pytest.raises(InvalidExecutionEngineModelError, match="executed"):
        ExecutionResult(**{**required, "executed_nodes": ("one", "one")})
    with pytest.raises(InvalidExecutionEngineModelError, match="disjoint"):
        ExecutionResult(**{**required, "skipped_nodes": ("one",)})
    with pytest.raises(InvalidExecutionEngineModelError, match="statistics"):
        ExecutionResult(**{**required, "statistics": {}})  # type: ignore[arg-type]
    with pytest.raises(InvalidExecutionEngineModelError, match="schema"):
        ExecutionResult(**{**required, "schema_version": "2.0"})


class InvalidResultRootOperator(RootOperator):
    """Test operator returning an invalid result contract."""

    def execute(self, node, context):  # type: ignore[no-untyped-def]
        """Return a non-operator result intentionally."""
        return None


class FailingRootOperator(RootOperator):
    """Test operator raising a deterministic failure."""

    def execute(self, node, context):  # type: ignore[no-untyped-def]
        """Raise a stable operator failure."""
        raise RuntimeError("logical failure")


def running_context() -> ExecutionContext:
    """Create a validated context in RUNNING state for negative tests."""
    context = ExecutionContext(physical_plan())
    context.transition_to(ExecutionState.READY)
    context.transition_to(ExecutionState.RUNNING)
    return context


def test_operator_and_pipeline_negative_contracts() -> None:
    with pytest.raises(ExecutionPipelineError, match="mapping"):
        ExecutionPipeline([])  # type: ignore[arg-type]
    with pytest.raises(ExecutionPipelineError, match="context"):
        ExecutionPipeline().execute("invalid")  # type: ignore[arg-type]
    with pytest.raises(ExecutionOperatorError, match="mapping"):
        OperatorResult(metadata=[])  # type: ignore[arg-type]
    with pytest.raises(ExecutionOperatorError, match="keys"):
        OperatorResult(metadata={"": 1})
    with pytest.raises(ExecutionOperatorError, match="scalar"):
        OperatorResult(metadata={"bad": []})
    with pytest.raises(ExecutionOperatorError, match="boolean"):
        OperatorResult(skipped=1)  # type: ignore[arg-type]
    with pytest.raises(ExecutionOperatorError, match="warnings"):
        OperatorResult(warnings=("",))
    root = physical_plan().root_node
    with pytest.raises(ExecutionOperatorError, match="context"):
        RootOperator().execute(root, "invalid")  # type: ignore[arg-type]
    with pytest.raises(ExecutionOperatorError, match="does not support"):
        ScanOperator().execute(root, running_context())
    for operator, message in (
        (InvalidResultRootOperator(), "must return"),
        (FailingRootOperator(), "operator failed"),
    ):
        registry = dict(canonical_operators())
        registry[ExecutionNodeType.ROOT] = operator
        with pytest.raises(ExecutionOperatorError, match=message):
            ExecutionPipeline(registry).execute(running_context())


def test_validator_negative_registry_and_context_contracts() -> None:
    validator = ExecutionEngineValidator()
    with pytest.raises(ExecutionEngineValidationError, match="context"):
        validator.validate_context("invalid")  # type: ignore[arg-type]
    context = ExecutionContext(physical_plan())
    context.transition_to(ExecutionState.READY)
    with pytest.raises(ExecutionEngineValidationError, match="CREATED"):
        validator.validate_context(context)
    stacked = ExecutionContext(physical_plan(), execution_stack=("node",))
    with pytest.raises(ExecutionEngineValidationError, match="stack"):
        validator.validate_context(stacked)
    with pytest.raises(ExecutionEngineValidationError, match="mapping"):
        validator.validate_operators([])  # type: ignore[arg-type]
    registry = dict(canonical_operators())
    with pytest.raises(ExecutionEngineValidationError, match="keys"):
        validator.validate_operators({"root": RootOperator()})  # type: ignore[dict-item]
    with pytest.raises(ExecutionEngineValidationError, match="invalid operator"):
        validator.validate_operators({ExecutionNodeType.ROOT: object()})  # type: ignore[dict-item]
    registry[ExecutionNodeType.ROOT] = ScanOperator()
    with pytest.raises(ExecutionEngineValidationError, match="does not match"):
        validator.validate_operators(registry)
    with pytest.raises(ExecutionEngineError, match="validator"):
        ExecutionEngine(validator=object())  # type: ignore[arg-type]
    assert isinstance(ExecutionEngine().pipeline, ExecutionPipeline)


def test_type_hints_docstrings_utf8_pep8_and_architecture() -> None:
    modules = tuple(sorted(SOURCE.glob("*.py")))
    assert len(modules) == 7
    forbidden = {
        "sqlite3", "pathlib", "os", "redis", "faiss", "lucene", "threading",
        "asyncio", "socket", "requests", "urllib",
    }
    for path in modules:
        raw = path.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8")
        tree = ast.parse(text)
        imports = {
            node.names[0].name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        } | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        assert not imports & forbidden
        assert all(len(line) <= 99 for line in text.splitlines())
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and not (
                node.name.startswith("_")
            ):
                assert ast.get_docstring(node), f"missing docstring: {node.name}"
                if isinstance(node, ast.FunctionDef):
                    assert node.returns is not None, node.name
