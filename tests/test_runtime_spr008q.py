"""Production contracts for the SPR-008Q canonical Runtime foundation."""

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
    ExecutionPlan,
    ExecutionPipeline as PlannerPipeline,
    QueryExecutionPlan,
    QueryExecutionStrategy,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryPagination,
    QueryPlan,
    QueryProjection,
)
from cko.core.execution import ExecutionEngine, ExecutionResult
from cko.core.runtime import (
    RUNTIME_SCHEMA_VERSION,
    CancellationToken,
    InvalidRuntimeModelError,
    LifecycleController,
    ResourceRegistry,
    ResourceRegistryError,
    Runtime,
    RuntimeCancellationError,
    RuntimeContext,
    RuntimeErrorBase,
    RuntimeLifecycleError,
    RuntimeMetrics,
    RuntimeReport,
    RuntimeSession,
    RuntimeState,
    RuntimeValidationError,
    RuntimeValidator,
)


INSTANT = datetime(2026, 7, 19, 12, 0, tzinfo=timezone.utc)
SOURCE = Path(__file__).parents[1] / "src" / "cko" / "core" / "runtime"


def physical_plan() -> ExecutionPlan:
    """Build one canonical physical plan entirely in memory."""
    logical = QueryPlan(
        query_id="query-q",
        effective_filters=(QueryFilter("kind", QueryOperator.EQUALS, "document"),),
        projections=(QueryProjection("name"),),
        ordering=(QueryOrdering("name"),),
        pagination=QueryPagination(page=1, page_size=10),
        estimates={"rows": 4},
        justifications=("fixture",),
        timestamp=INSTANT,
    )
    planned = QueryExecutionPlan(
        plan_id="qep-runtime",
        query_plan=logical,
        execution_strategy=QueryExecutionStrategy.INDEX_SCAN,
        selected_indexes=("idx",),
        estimated_cost=2.0,
        estimated_rows=4,
        estimated_selectivity=0.5,
        confidence=0.9,
        planning_time=0.0,
        planner_version="1.0.0",
        timestamp=INSTANT,
        metadata={"source": "test"},
    )
    return PlannerPipeline().build(planned)


def test_runtime_coordinates_engine_and_complete_lifecycle() -> None:
    runtime = Runtime(runtime_id="runtime-q", session_id="session-q")
    result = runtime.execute(physical_plan())
    assert result.success is True
    assert runtime.state is RuntimeState.COMPLETED
    assert runtime.context.execution_id == result.execution_id
    assert runtime.metrics.executions == 1
    assert runtime.metrics.completed == 1
    assert runtime.metrics.failed == runtime.metrics.cancelled == 0


def test_context_contains_all_required_runtime_fields() -> None:
    context = RuntimeContext(
        runtime_id="runtime-context",
        execution_id="execution-context",
        metadata={"ação": "validação"},
        statistics={"executions": 0},
        resources={"logical": {"kind": "memory"}},
    )
    restored = RuntimeContext.from_json(context.to_json())
    assert restored == context
    assert "validação" in context.to_json()
    assert set(context.to_dict()) >= {
        "runtime_id", "execution_id", "state", "metadata", "statistics",
        "resources",
    }


def test_lifecycle_controller_covers_eight_states_and_transitions() -> None:
    assert {item.value for item in RuntimeState} == {
        "created", "initialized", "ready", "running", "paused", "completed",
        "failed", "cancelled",
    }
    context = RuntimeContext("runtime-lifecycle", "execution-lifecycle")
    controller = LifecycleController()
    for state in (
        RuntimeState.INITIALIZED, RuntimeState.READY, RuntimeState.RUNNING,
        RuntimeState.PAUSED, RuntimeState.RUNNING, RuntimeState.COMPLETED,
    ):
        assert controller.can_transition(context.state, state)
        controller.transition(context, state)
    with pytest.raises(RuntimeLifecycleError, match="invalid"):
        controller.transition(context, RuntimeState.RUNNING)


def test_cooperative_cancellation_is_idempotent_and_synchronous() -> None:
    token = CancellationToken()
    assert token.is_cancelled is False
    assert token.cancel("pedido do usuário") is True
    assert token.cancel("ignored") is False
    assert token.reason == "pedido do usuário"
    with pytest.raises(RuntimeCancellationError, match="usuário"):
        token.throw_if_cancelled()
    assert token.to_dict() == {
        "cancelled": True, "reason": "pedido do usuário",
    }


def test_runtime_cancels_before_engine_execution_and_reports_it() -> None:
    runtime = Runtime(runtime_id="runtime-cancel")
    runtime.initialize(physical_plan())
    runtime.cancellation_token.cancel("stop")
    with pytest.raises(RuntimeCancellationError, match="stop"):
        runtime.start()
    assert runtime.state is RuntimeState.CANCELLED
    assert runtime.metrics.cancelled == runtime.metrics.executions == 1
    assert runtime.result is None


def test_resource_registry_tracks_only_logical_serializable_values() -> None:
    registry = ResourceRegistry()
    registry.register("buffer", {"capacity": 10, "labels": ["a", "b"]})
    assert registry.contains("buffer")
    assert registry.get("buffer")["capacity"] == 10  # type: ignore[index]
    assert tuple(registry) == ("buffer",)
    with pytest.raises(ResourceRegistryError, match="already"):
        registry.register("buffer")
    with pytest.raises(ResourceRegistryError, match="unsupported"):
        registry.register("external", object())
    assert registry.unregister("buffer")
    assert len(registry) == 0


def test_runtime_synchronizes_resources_with_context() -> None:
    runtime = Runtime(runtime_id="runtime-resource")
    runtime.register_resource("workspace", {"scope": "logical"})
    assert runtime.context.resources["workspace"]["scope"] == "logical"
    assert runtime.unregister_resource("workspace")
    runtime.register_resource("temporary")
    runtime.release_resources()
    assert runtime.context.resources == {}


def test_session_metrics_and_report_are_serializable_and_immutable() -> None:
    runtime = Runtime(runtime_id="runtime-report", session_id="session-report")
    runtime.execute(physical_plan())
    report = runtime.report()
    restored = RuntimeReport.from_json(report.to_json())
    assert restored == report
    assert report.schema_version == RUNTIME_SCHEMA_VERSION
    assert report.session.runtime == runtime.runtime_id
    assert report.state is RuntimeState.COMPLETED
    with pytest.raises(FrozenInstanceError):
        report.state = RuntimeState.FAILED  # type: ignore[misc]


def test_metrics_validate_counts_duration_and_round_trip() -> None:
    metrics = RuntimeMetrics(
        runtime_duration=1.5, executions=3, cancelled=1, failed=1,
        completed=1, metadata={"unit": "seconds"},
    )
    assert RuntimeMetrics.from_dict(metrics.to_dict()) == metrics
    with pytest.raises(InvalidRuntimeModelError, match="non-negative"):
        RuntimeMetrics(runtime_duration=-1)
    with pytest.raises(InvalidRuntimeModelError, match="exceed"):
        RuntimeMetrics(executions=1, completed=2)


def test_validator_checks_context_session_transition_and_integrity() -> None:
    runtime = Runtime(runtime_id="runtime-validator")
    validator = RuntimeValidator()
    assert validator.validate_context(runtime.context) is runtime.context
    assert validator.validate_session(runtime.session).runtime == runtime.runtime_id
    assert validator.is_valid(runtime.context, runtime.session, runtime.resources)
    validator.validate_transition(RuntimeState.CREATED, RuntimeState.INITIALIZED)
    with pytest.raises(RuntimeValidationError, match="invalid"):
        validator.validate_transition(RuntimeState.CREATED, RuntimeState.RUNNING)
    with pytest.raises(RuntimeValidationError, match="context"):
        validator.validate_context("bad")  # type: ignore[arg-type]


class FailingEngine(ExecutionEngine):
    """Execution Engine test double that fails before operator coordination."""

    def execute(
        self, plan: ExecutionPlan, *, metadata: object = None,
    ) -> ExecutionResult:
        """Raise a stable logical failure."""
        raise RuntimeError("engine failure")


def test_engine_failure_moves_runtime_to_failed_and_updates_metrics() -> None:
    runtime = Runtime(FailingEngine(), runtime_id="runtime-failure")
    with pytest.raises(RuntimeError, match="engine failure"):
        runtime.execute(physical_plan())
    assert runtime.state is RuntimeState.FAILED
    assert runtime.metrics.failed == runtime.metrics.executions == 1


def test_required_structured_logging_events_are_emitted(caplog) -> None:
    caplog.set_level(logging.INFO, logger="cko.core.runtime")
    runtime = Runtime(runtime_id="runtime-log")
    runtime.execute(physical_plan())
    events = {getattr(record, "event", "") for record in caplog.records}
    assert {
        "core.runtime.runtime_created", "core.runtime.runtime_initialized",
        "core.runtime.runtime_started", "core.runtime.runtime_finished",
    } <= events
    caplog.clear()
    cancelled = Runtime(runtime_id="runtime-log-cancel")
    assert cancelled.cancel("test")
    assert cancelled.report().state is RuntimeState.CANCELLED
    assert any(
        getattr(record, "event", "") == "core.runtime.runtime_cancelled"
        for record in caplog.records
    )


def test_public_api_is_additive_and_preserves_discovery_token() -> None:
    assert core.Runtime is Runtime
    assert core.RuntimeContext is RuntimeContext
    assert core.RuntimeSession is RuntimeSession
    assert core.RuntimeMetrics is RuntimeMetrics
    assert core.RuntimeReport is RuntimeReport
    assert core.RuntimeCancellationToken is CancellationToken
    assert core.CancellationToken.__module__.endswith("discovery.cancellation")


def test_negative_model_session_report_and_runtime_contracts() -> None:
    with pytest.raises(InvalidRuntimeModelError, match="runtime_id"):
        RuntimeContext("")
    with pytest.raises(InvalidRuntimeModelError, match="mapping"):
        RuntimeContext("runtime", metadata=[])  # type: ignore[arg-type]
    with pytest.raises(InvalidRuntimeModelError, match="JSON"):
        RuntimeReport.from_json("invalid")
    runtime = Runtime(runtime_id="runtime-negative")
    with pytest.raises(InvalidRuntimeModelError, match="does not match"):
        RuntimeSession(
            "session", "other", runtime.context, runtime.metrics,
        )
    with pytest.raises(RuntimeErrorBase):
        runtime.start()


def test_additional_negative_branches_are_deterministic() -> None:
    with pytest.raises(InvalidRuntimeModelError, match="reason"):
        CancellationToken().cancel("")
    controller = LifecycleController()
    assert controller.allowed_transitions(RuntimeState.CREATED)
    with pytest.raises(RuntimeLifecycleError, match="context"):
        controller.transition(object(), RuntimeState.READY)
    with pytest.raises(RuntimeLifecycleError, match="RuntimeState"):
        controller.can_transition("bad", RuntimeState.READY)  # type: ignore[arg-type]
    with pytest.raises(InvalidRuntimeModelError, match="state"):
        RuntimeContext("runtime", state="bad")  # type: ignore[arg-type]
    with pytest.raises(InvalidRuntimeModelError, match="finite"):
        RuntimeContext("runtime", metadata={"value": float("nan")})
    with pytest.raises(InvalidRuntimeModelError, match="unsupported"):
        RuntimeContext("runtime", metadata={"value": object()})
    nested = RuntimeContext("runtime", metadata={"items": [1, "two"]})
    assert nested.to_dict()["metadata"] == {"items": [1, "two"]}
    with pytest.raises(InvalidRuntimeModelError, match="envelope"):
        RuntimeContext.from_dict({})


def test_additional_resource_runtime_and_validator_contracts() -> None:
    registry = ResourceRegistry()
    registry.register("ratio", 0.5)
    assert registry.get("ratio") == 0.5
    with pytest.raises(ResourceRegistryError, match="finite"):
        registry.register("invalid", float("inf"))
    with pytest.raises(ResourceRegistryError, match="not registered"):
        registry.get("missing")
    with pytest.raises(ResourceRegistryError, match="not registered"):
        registry.unregister("missing")
    with pytest.raises(RuntimeErrorBase, match="runtime_id"):
        Runtime(runtime_id="")
    with pytest.raises(RuntimeErrorBase, match="engine"):
        Runtime(object())  # type: ignore[arg-type]
    runtime = Runtime(runtime_id="runtime-extra")
    runtime.initialize(physical_plan())
    with pytest.raises(RuntimeErrorBase, match="initialize"):
        runtime.initialize(physical_plan())
    runtime.ready()
    with pytest.raises(RuntimeErrorBase, match="another plan"):
        runtime.start(physical_plan())
    runtime.cancel("done")
    assert runtime.cancel("again") is False
    validator = RuntimeValidator()
    invalid = RuntimeContext(
        "runtime-invalid", state=RuntimeState.INITIALIZED,
    )
    with pytest.raises(RuntimeValidationError, match="execution_id"):
        validator.validate_context(invalid)
    assert validator.validate_state(RuntimeState.READY) is RuntimeState.READY
    with pytest.raises(RuntimeValidationError, match="RuntimeState"):
        validator.validate_state("bad")  # type: ignore[arg-type]
    fresh = Runtime(runtime_id="runtime-integrity")
    other_registry = ResourceRegistry()
    other_registry.register("different")
    assert not validator.is_valid(fresh.context, fresh.session, other_registry)


def test_type_hints_docstrings_utf8_pep8_and_architecture() -> None:
    modules = tuple(sorted(SOURCE.glob("*.py")))
    assert len(modules) == 8
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
