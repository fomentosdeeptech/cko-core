"""Production contracts for the SPR-008O canonical execution planner."""

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
    EXECUTION_SCHEMA_VERSION,
    CompositeIndexScanNode,
    ExecutionContext,
    ExecutionMetrics,
    ExecutionNode,
    ExecutionNodeType,
    ExecutionPipeline,
    ExecutionPlan,
    ExecutionPlanningError,
    ExecutionPlanValidator,
    ExecutionReport,
    ExecutionValidationError,
    FilterNode,
    IndexScanNode,
    LimitNode,
    OrderedScanNode,
    PrefixScanNode,
    ProjectionNode,
    QueryExecutionPlan,
    QueryExecutionStrategy,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryPagination,
    QueryPlan,
    QueryProjection,
    RootNode,
    ScanNode,
    SortNode,
)


INSTANT = datetime(2026, 7, 18, 20, 0, tzinfo=timezone.utc)


def logical_plan(*, complete: bool = True) -> QueryPlan:
    """Build one immutable logical plan without executing it."""
    return QueryPlan(
        query_id="query-o",
        effective_filters=(
            QueryFilter("kind", QueryOperator.EQUALS, "document"),
        ) if complete else (),
        projections=(QueryProjection("name"),) if complete else (),
        ordering=(QueryOrdering("name"),) if complete else (),
        pagination=QueryPagination(page=2, page_size=10) if complete else None,
        estimates={"rows": 4}, justifications=("fixture",),
        timestamp=INSTANT,
    )


def query_execution_plan(
    strategy: QueryExecutionStrategy = QueryExecutionStrategy.INDEX_SCAN,
    *, complete: bool = True,
) -> QueryExecutionPlan:
    """Build a deterministic homologated planner output fixture."""
    indexes = () if strategy is QueryExecutionStrategy.FULL_SCAN else ("idx-kind",)
    return QueryExecutionPlan(
        plan_id=f"qep-{strategy.value}", query_plan=logical_plan(complete=complete),
        execution_strategy=strategy, selected_indexes=indexes,
        estimated_cost=2.0, estimated_rows=4, estimated_selectivity=0.5,
        confidence=0.9, planning_time=0.0, planner_version="1.0.0",
        timestamp=INSTANT, metadata={"source": "test"},
    )


def physical_plan(
    strategy: QueryExecutionStrategy = QueryExecutionStrategy.INDEX_SCAN,
    *, complete: bool = True,
) -> ExecutionPlan:
    """Build one canonical physical plan entirely in memory."""
    return ExecutionPipeline().build(
        query_execution_plan(strategy, complete=complete)
    )


def flatten(node: ExecutionNode) -> tuple[ExecutionNode, ...]:
    """Return deterministic pre-order nodes from a physical tree."""
    return (node, *(child for item in node.children for child in flatten(item)))


def test_node_types_and_canonical_node_classes_are_complete() -> None:
    assert {item.value for item in ExecutionNodeType} == {
        "scan", "index_scan", "composite_index_scan", "prefix_scan",
        "ordered_scan", "filter", "projection", "sort", "limit", "root",
    }
    classes = (
        ScanNode, IndexScanNode, CompositeIndexScanNode, PrefixScanNode,
        OrderedScanNode, FilterNode, ProjectionNode, SortNode, LimitNode,
        RootNode,
    )
    assert len({item.expected_type for item in classes}) == 10
    with pytest.raises(ValueError, match="abstract"):
        ExecutionNode(node_id="invalid")


@pytest.mark.parametrize(
    ("strategy", "access_type"),
    (
        (QueryExecutionStrategy.FULL_SCAN, ScanNode),
        (QueryExecutionStrategy.INDEX_SCAN, IndexScanNode),
        (QueryExecutionStrategy.COMPOSITE_INDEX_SCAN, CompositeIndexScanNode),
        (QueryExecutionStrategy.PREFIX_INDEX_SCAN, PrefixScanNode),
        (QueryExecutionStrategy.ORDERED_INDEX_SCAN, OrderedScanNode),
    ),
)
def test_pipeline_maps_every_strategy_to_its_access_node(
    strategy: QueryExecutionStrategy,
    access_type: type[ExecutionNode],
) -> None:
    result = physical_plan(strategy, complete=False)
    nodes = flatten(result.root_node)
    assert len(nodes) == 2
    assert isinstance(nodes[-1], access_type)
    assert ExecutionPlanValidator().validate(result) is result


def test_complete_tree_has_canonical_order_and_parent_links() -> None:
    result = physical_plan()
    nodes = flatten(result.root_node)
    assert [type(item) for item in nodes] == [
        RootNode, LimitNode, SortNode, ProjectionNode, FilterNode, IndexScanNode,
    ]
    assert nodes[0].parent is None
    assert all(child.parent == parent.node_id
               for parent, child in zip(nodes, nodes[1:]))
    assert all(len(item.children) == 1 for item in nodes[:-1])
    assert not nodes[-1].children


def test_same_input_produces_exactly_the_same_execution_plan() -> None:
    source = query_execution_plan()
    first = ExecutionPipeline().build(source)
    second = ExecutionPipeline().plan(source)
    assert first == second
    assert first.to_json() == second.to_json()
    assert first.plan_id == second.plan_id
    assert first.timestamp == source.timestamp


def test_models_are_deeply_immutable_and_strictly_serializable() -> None:
    result = physical_plan()
    report = ExecutionPipeline.report(result)
    metrics = ExecutionPipeline.metrics(result)
    context = ExecutionContext(query_execution_plan())
    for model in (result, report, metrics, context):
        assert type(model).from_json(model.to_json()) == model
        malformed = model.to_dict()
        malformed["unknown"] = True
        with pytest.raises(ValueError, match="unknown"):
            type(model).from_dict(malformed)
    assert result.schema_version == EXECUTION_SCHEMA_VERSION
    with pytest.raises(FrozenInstanceError):
        result.plan_id = "changed"
    with pytest.raises(TypeError):
        result.metadata["changed"] = True


def test_every_node_round_trips_recursively() -> None:
    root = physical_plan().root_node
    restored = ExecutionNode.from_json(root.to_json())
    assert restored == root
    assert isinstance(restored, RootNode)
    malformed = root.to_dict()
    malformed["node_type"] = "scan"
    with pytest.raises(ValueError, match="match"):
        RootNode.from_dict(malformed)


def test_report_and_metrics_are_coherent_with_the_tree() -> None:
    result = physical_plan()
    nodes = flatten(result.root_node)
    report = ExecutionPipeline.report(result)
    metrics = ExecutionPipeline.metrics(result)
    assert isinstance(report, ExecutionReport)
    assert report.tree_created == result.root_node
    assert report.nodes_created == tuple(item.node_id for item in nodes)
    assert report.strategy is result.execution_strategy
    assert isinstance(metrics, ExecutionMetrics)
    assert metrics.planning_duration == 0.0
    assert metrics.nodes_created == len(nodes)
    assert metrics.maximum_depth == len(nodes)
    assert metrics.planning_score == 0.9


def test_validator_rejects_invalid_root_parent_and_child_links() -> None:
    result = physical_plan()
    invalid_root = replace(result.root_node, parent="orphan")
    with pytest.raises(ExecutionValidationError, match="root"):
        ExecutionPlanValidator().validate(replace(result, root_node=invalid_root))
    child = result.root_node.children[0]
    invalid_child = replace(child, parent="wrong")
    invalid_root = replace(result.root_node, children=(invalid_child,))
    with pytest.raises(ExecutionValidationError, match="parent"):
        ExecutionPlanValidator().validate(replace(result, root_node=invalid_root))


def test_validator_rejects_duplicate_nodes_and_strategy_mismatch() -> None:
    result = physical_plan(complete=False)
    access = result.root_node.children[0]
    duplicate = replace(access, children=(access,))
    invalid_root = replace(result.root_node, children=(duplicate,))
    assert not ExecutionPlanValidator().is_valid(
        replace(result, root_node=invalid_root)
    )
    with pytest.raises(ExecutionValidationError, match="strategy"):
        ExecutionPlanValidator().validate(replace(
            result, execution_strategy=QueryExecutionStrategy.FULL_SCAN
        ))


def test_pipeline_rejects_invalid_input_without_side_effects() -> None:
    with pytest.raises(ExecutionPlanningError, match="context"):
        ExecutionPipeline().build("invalid")


def test_model_guards_reject_invalid_scalars_json_and_metadata() -> None:
    with pytest.raises(ValueError, match="invalid"):
        ExecutionMetrics.from_json("invalid")
    with pytest.raises(ValueError, match="object"):
        ExecutionMetrics.from_json("[]")
    with pytest.raises(ValueError, match="non-negative"):
        ExecutionMetrics(-1, 1, 1, 1, {})
    with pytest.raises(ValueError, match="positive"):
        ExecutionMetrics(0, 1, 0, 1, {})
    with pytest.raises(ValueError, match="at most"):
        ExecutionMetrics(0, 1, 1, 2, {})
    with pytest.raises(ValueError, match="finite"):
        ExecutionMetrics(0, 1, 1, 1, {"score": float("nan")})
    with pytest.raises(ValueError, match="unsupported"):
        ScanNode("scan", metadata={"invalid": object()})
    with pytest.raises(ValueError, match="children"):
        ScanNode("scan", children=("invalid",))


def test_strict_envelopes_and_context_types_are_rejected() -> None:
    payload = ExecutionMetrics(0, 1, 1, 1, {}).to_dict()
    payload.pop("metadata")
    with pytest.raises(ValueError, match="missing"):
        ExecutionMetrics.from_dict(payload)
    payload = ExecutionMetrics(0, 1, 1, 1, {}).to_dict()
    payload["schema_version"] = "2.0"
    with pytest.raises(ValueError, match="schema"):
        ExecutionMetrics.from_dict(payload)
    payload = ExecutionMetrics(0, 1, 1, 1, {}).to_dict()
    payload["model"] = "other"
    with pytest.raises(ValueError, match="represent"):
        ExecutionMetrics.from_dict(payload)
    with pytest.raises(ValueError, match="query_execution_plan"):
        ExecutionContext("invalid")
    with pytest.raises(ValueError, match="optimization_result"):
        ExecutionContext(query_execution_plan(), optimization_result="invalid")
    with pytest.raises(ValueError, match="planner_decision"):
        ExecutionContext(query_execution_plan(), planner_decision="invalid")
    with pytest.raises(ValueError, match="statistics"):
        ExecutionContext(query_execution_plan(), statistics="invalid")
    with pytest.raises(ValueError, match="unknown"):
        ExecutionNode.from_dict({"node_type": "unknown"})


def test_logging_covers_the_required_execution_planning_lifecycle(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        physical_plan()
    events = {getattr(record, "event", None) for record in caplog.records}
    required = {
        "execution_planning_started", "node_created", "validation_started",
        "validation_finished", "execution_planning_finished",
    }
    assert all(any(event and event.endswith(name) for event in events)
               for name in required)


def test_public_api_type_hints_docstrings_utf8_pep8_and_boundaries() -> None:
    public = (
        ExecutionNode, ExecutionPlan, ExecutionContext, ExecutionReport,
        ExecutionMetrics, ExecutionPipeline, ExecutionPlanValidator,
        ScanNode, IndexScanNode, CompositeIndexScanNode, PrefixScanNode,
        OrderedScanNode, FilterNode, ProjectionNode, SortNode, LimitNode,
        RootNode,
    )
    assert all(inspect.getdoc(item) for item in public)
    for method in (
        ExecutionPipeline.build, ExecutionPipeline.plan,
        ExecutionPipeline.report, ExecutionPipeline.metrics,
        ExecutionPlanValidator.validate, ExecutionPlanValidator.is_valid,
    ):
        assert inspect.signature(method).return_annotation is not (
            inspect.Signature.empty
        )
        assert inspect.getdoc(method)
    for name in (
        "ExecutionNode", "ExecutionPlan", "ExecutionContext", "ExecutionReport",
        "ExecutionMetrics", "ExecutionPipeline", "ExecutionPlanValidator",
        "ScanNode", "IndexScanNode", "RootNode",
    ):
        assert getattr(core, name) is getattr(discovery, name)
        assert name in core.__all__ and name in discovery.__all__
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    prohibited = {
        "os", "pathlib", "sqlite3", "requests", "urllib", "http", "socket",
        "redis", "sqlalchemy", "threading", "asyncio", "cko.persistence",
        "cko.repository",
    }
    for name in (
        "execution_errors.py", "execution_models.py", "execution_planner.py",
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
