"""Production contract and architecture tests for SPR-008K."""

from __future__ import annotations

import ast
import inspect
import logging
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

import cko.core as core
import cko.core.discovery as discovery
from cko.core.discovery import (
    QUERY_INDEX_SCHEMA_VERSION,
    DiscardedLogicalIndex,
    DuplicateBehavior,
    FilterGroup,
    FilterGroupOperator,
    IndexStrategy,
    LogicalIndex,
    LogicalIndexBuilder,
    LogicalIndexEntry,
    LogicalIndexPolicy,
    LogicalIndexReport,
    LogicalIndexStatistics,
    LogicalIndexValidationError,
    LogicalIndexValidator,
    QueryFilter,
    QueryIndexPlan,
    QueryIndexPlanner,
    QueryOperator,
    QueryOrdering,
    QueryPlan,
)


INSTANT = datetime(2026, 7, 17, 15, 0, tzinfo=timezone.utc)
SUBJECTS = (
    {"id": "asset-b", "kind": "document", "name": "Beta", "size": 20},
    {"id": "asset-a", "kind": "document", "name": "Alpha", "size": 10},
    {"id": "asset-c", "kind": "image", "name": "Atlas", "size": 30},
)


def query_plan(
    *filters: QueryFilter,
    ordering: tuple[QueryOrdering, ...] = (),
) -> QueryPlan:
    """Create a deterministic homologated query plan."""
    return QueryPlan(
        query_id="query-k",
        effective_filters=filters,
        projections=(),
        ordering=ordering,
        pagination=None,
        timestamp=INSTANT,
    )


def build(
    index_id: str = "idx-kind",
    attributes: tuple[str, ...] = ("kind",),
    strategy: IndexStrategy = IndexStrategy.HASH,
) -> LogicalIndex:
    """Build a deterministic logical index fixture."""
    return LogicalIndexBuilder().build(
        index_id,
        f"Index {index_id}",
        SUBJECTS,
        attributes,
        strategy=strategy,
        relevant_attributes=("kind", "name", "size"),
        timestamp=INSTANT,
    )


def test_models_are_frozen_deeply_immutable_and_versioned() -> None:
    index = build()
    with pytest.raises(FrozenInstanceError):
        index.name = "changed"
    with pytest.raises(FrozenInstanceError):
        index.entries[0].logical_identity = "changed"
    with pytest.raises(TypeError):
        index.statistics.estimates["new"] = 1
    with pytest.raises(TypeError):
        index.entries[0].attributes["kind"] = "changed"
    assert index.schema_version == QUERY_INDEX_SCHEMA_VERSION
    assert index.to_dict()["schema_version"] == QUERY_INDEX_SCHEMA_VERSION


@pytest.mark.parametrize(
    "model",
    (
        LogicalIndexEntry("one", "document", {"kind": "document"}, INSTANT),
        LogicalIndexStatistics(1, 1, {'"document"': 1}, 1.0, {"cost": 1}),
        LogicalIndexPolicy(),
        DiscardedLogicalIndex("idx-old", "less compatible", 2.0),
    ),
)
def test_canonical_models_round_trip_strictly(model: object) -> None:
    restored = type(model).from_json(model.to_json())
    assert restored == model
    malformed = model.to_dict()
    malformed["unknown"] = True
    with pytest.raises(ValueError, match="unknown"):
        type(model).from_dict(malformed)


def test_index_round_trip_preserves_entries_statistics_and_schema() -> None:
    index = build()
    restored = LogicalIndex.from_json(index.to_json())
    assert restored == index
    assert restored.logical_cardinality == 3
    assert restored.statistics.entry_count == 3
    assert restored.statistics.distinct_key_count == 2
    assert restored.statistics.logical_distribution == {
        '"document"': 2, '"image"': 1
    }


def test_builder_is_deterministic_and_does_not_mutate_inputs() -> None:
    source = [dict(item) for item in reversed(SUBJECTS)]
    snapshot = [dict(item) for item in source]
    builder = LogicalIndexBuilder()
    first = builder.build(
        "idx", "Index", source, ("kind",), timestamp=INSTANT
    )
    second = builder.build(
        "idx", "Index", reversed(source), ("kind",), timestamp=INSTANT
    )
    assert first.to_json() == second.to_json()
    assert tuple(item.logical_identity for item in first.entries) == (
        "asset-a", "asset-b", "asset-c"
    )
    assert source == snapshot


def test_composite_keys_and_relevant_attributes_are_canonical() -> None:
    index = build(
        "idx-composite", ("kind", "name"), IndexStrategy.COMPOSITE
    )
    assert index.entries[0].indexed_key == ("document", "Alpha")
    assert index.indexed_attributes == ("kind", "name")
    assert index.strategy is IndexStrategy.COMPOSITE


def test_duplicate_policy_is_explicit_and_cardinality_is_enforced() -> None:
    duplicate = SUBJECTS + ({"id": "asset-a", "kind": "other"},)
    with pytest.raises(LogicalIndexValidationError, match="duplicate"):
        LogicalIndexBuilder().build("idx", "Index", duplicate, ("kind",))
    first = LogicalIndexBuilder(LogicalIndexPolicy(
        duplicate_behavior=DuplicateBehavior.KEEP_FIRST
    )).build("idx", "Index", duplicate, ("kind",), timestamp=INSTANT)
    assert first.logical_cardinality == 3
    assert next(
        item for item in first.entries if item.logical_identity == "asset-a"
    ).indexed_key == "document"
    with pytest.raises(LogicalIndexValidationError, match="cardinality"):
        LogicalIndexBuilder(LogicalIndexPolicy(max_cardinality=2)).build(
            "idx", "Index", SUBJECTS, ("kind",)
        )


def test_validator_checks_keys_attributes_statistics_and_identity() -> None:
    index = build()
    validator = LogicalIndexValidator()
    assert validator.validate(index) is index
    assert validator.is_valid(index)
    inconsistent = LogicalIndexEntry(
        "asset-a", "wrong", {"kind": "document"}, INSTANT
    )
    entries = (inconsistent, *index.entries[1:])
    distribution = {'"wrong"': 1, '"document"': 1, '"image"': 1}
    broken = LogicalIndex(
        "broken", "Broken", ("kind",), IndexStrategy.HASH, 3,
        LogicalIndexStatistics(3, 3, distribution, 1.0), entries,
    )
    with pytest.raises(LogicalIndexValidationError, match="inconsistent key"):
        validator.validate(broken)


def test_resolver_selects_best_index_deterministically_and_auditably() -> None:
    hash_index = build("z-hash")
    ordered = build("a-ordered", ("size",), IndexStrategy.ORDERED)
    prefix = build("p-prefix", ("name",), IndexStrategy.PREFIX)
    plan = query_plan(QueryFilter("name", QueryOperator.STARTS_WITH, "A"))
    report = discovery.LogicalIndexResolver().resolve(
        plan, (ordered, hash_index, prefix), timestamp=INSTANT
    )
    assert report.selected_index_id == "p-prefix"
    assert "deterministically" in report.justification
    assert {item.index_id for item in report.discarded_indexes} == {
        "a-ordered", "z-hash"
    }
    assert LogicalIndexReport.from_json(report.to_json()) == report


def test_resolver_uses_stable_index_id_tie_breaker() -> None:
    first = build("a-index")
    second = build("b-index")
    plan = query_plan(QueryFilter("kind", QueryOperator.EQUALS, "document"))
    report = discovery.LogicalIndexResolver().resolve(
        plan, (second, first), timestamp=INSTANT
    )
    assert report.selected_index_id == "a-index"


def test_planner_produces_utilization_cost_and_justifications() -> None:
    plan = query_plan(QueryFilter("kind", QueryOperator.EQUALS, "document"))
    result = QueryIndexPlanner().plan(plan, (build(),), timestamp=INSTANT)
    assert result.selected_index_id == "idx-kind"
    assert result.matched_attributes == ("kind",)
    assert result.estimated_logical_cost >= 0
    assert result.justifications
    assert QueryIndexPlan.from_json(result.to_json()) == result


def test_planner_explicitly_represents_full_scan_without_match() -> None:
    plan = query_plan(QueryFilter("absent", QueryOperator.EQUALS, 1))
    result = QueryIndexPlanner().plan(plan, (build(),), timestamp=INSTANT)
    assert result.selected_index_id is None
    assert result.matched_attributes == ()
    assert "full scan" in result.justifications[1]


def test_policy_and_serialization_reject_invalid_contracts() -> None:
    for arguments in (
        {"max_indexes": 0},
        {"max_cardinality": 0},
        {"selection_rules": ()},
        {"selection_rules": ("cost", "cost")},
        {"duplicate_behavior": "unknown"},
    ):
        with pytest.raises(ValueError):
            LogicalIndexPolicy(**arguments)
    payload = LogicalIndexPolicy().to_dict()
    payload["schema_version"] = "99.0"
    with pytest.raises(ValueError, match="version"):
        LogicalIndexPolicy.from_dict(payload)
    with pytest.raises(ValueError, match="invalid"):
        LogicalIndexPolicy.from_json("not-json")
    with pytest.raises(ValueError, match="object"):
        LogicalIndexPolicy.from_json("[]")


def test_statistics_and_index_models_reject_inconsistent_values() -> None:
    with pytest.raises(ValueError, match="exceed"):
        LogicalIndexStatistics(1, 2, {"a": 1, "b": 1}, 2.0)
    with pytest.raises(ValueError, match="account"):
        LogicalIndexStatistics(2, 1, {"a": 1}, 0.5)
    with pytest.raises(ValueError, match="distinct_key_count"):
        LogicalIndexStatistics(2, 2, {"a": 2}, 1.0)
    with pytest.raises(ValueError, match="density"):
        LogicalIndexStatistics(1, 1, {"a": 1}, 0.5)
    empty = LogicalIndexStatistics(0, 0, {}, 0.0)
    with pytest.raises(ValueError, match="composite"):
        LogicalIndex(
            "bad", "Bad", ("kind",), IndexStrategy.COMPOSITE, 0, empty
        )
    with pytest.raises(ValueError, match="unique"):
        LogicalIndex("bad", "Bad", (), IndexStrategy.HASH, 0, empty)


def test_builder_supports_object_subjects_and_keep_last() -> None:
    class Subject:
        def __init__(self, identity: int, kind: str) -> None:
            self.identity = identity
            self.kind = kind

    source = (Subject(1, "first"), Subject(1, "last"))
    policy = LogicalIndexPolicy(duplicate_behavior=DuplicateBehavior.KEEP_LAST)
    index = LogicalIndexBuilder(policy).build(
        "objects", "Objects", source, ("kind",), timestamp=INSTANT
    )
    assert index.entries[0].logical_identity == "1"
    assert index.entries[0].indexed_key == "last"
    with pytest.raises(ValueError, match="expose"):
        LogicalIndexBuilder().build("bad", "Bad", ({"kind": "x"},), ("kind",))


def test_resolution_validates_input_and_covers_ordered_composite_groups() -> None:
    resolver = discovery.LogicalIndexResolver(LogicalIndexPolicy(max_indexes=1))
    plan = query_plan(QueryFilter("size", QueryOperator.GREATER_THAN, 5))
    ordered = build("ordered", ("size",), IndexStrategy.ORDERED)
    assert resolver.resolve(plan, (ordered,), timestamp=INSTANT).selected_index_id == (
        "ordered"
    )
    with pytest.raises(ValueError, match="policy limit"):
        resolver.resolve(plan, (ordered, build()), timestamp=INSTANT)
    with pytest.raises(ValueError, match="QueryPlan"):
        resolver.resolve("invalid", ())
    duplicate = discovery.LogicalIndexResolver().resolve
    with pytest.raises(ValueError, match="unique"):
        duplicate(plan, (ordered, ordered), timestamp=INSTANT)
    grouped = query_plan(FilterGroup(
        FilterGroupOperator.AND,
        (QueryFilter("kind", QueryOperator.EQUALS, "document"),),
    ))
    composite = build(
        "composite", ("kind", "name"), IndexStrategy.COMPOSITE
    )
    assert discovery.LogicalIndexResolver().resolve(
        grouped, (composite,), timestamp=INSTANT
    ).selected_index_id == "composite"


def test_structured_logging_covers_required_lifecycle(
    caplog: pytest.LogCaptureFixture,
) -> None:
    plan = query_plan(QueryFilter("kind", QueryOperator.EQUALS, "document"))
    with caplog.at_level(logging.INFO):
        index = build()
        QueryIndexPlanner().plan(plan, (index,), timestamp=INSTANT)
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "discovery.query.index.construction_started",
        "discovery.query.index.validation_completed",
        "discovery.query.index.selection_completed",
        "discovery.query.index.planning_completed",
        "discovery.query.index.completed",
    } <= events


def test_public_api_type_hints_docstrings_utf8_pep8_and_boundaries() -> None:
    public = (
        LogicalIndex, LogicalIndexEntry, LogicalIndexStatistics,
        LogicalIndexPolicy, LogicalIndexReport, LogicalIndexBuilder,
        LogicalIndexValidator, discovery.LogicalIndexResolver,
        QueryIndexPlanner, QueryIndexPlan,
    )
    assert all(inspect.getdoc(item) for item in public)
    for method in (
        LogicalIndexBuilder.build, LogicalIndexValidator.validate,
        discovery.LogicalIndexResolver.resolve, QueryIndexPlanner.plan,
    ):
        signature = inspect.signature(method)
        assert signature.return_annotation is not inspect.Signature.empty
        assert inspect.getdoc(method)
    for name in (
        "LogicalIndex", "LogicalIndexBuilder", "LogicalIndexResolver",
        "QueryIndexPlanner", "IndexStrategy",
    ):
        assert getattr(core, name) is getattr(discovery, name)
        assert name in core.__all__ and name in discovery.__all__

    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    prohibited = {
        "os", "pathlib", "sqlite3", "requests", "urllib", "http", "socket",
        "redis", "sqlalchemy", "cko.persistence", "cko.repository",
    }
    for name in (
        "query_index_errors.py", "query_index_models.py", "query_index.py",
    ):
        content = (root / name).read_bytes()
        assert not content.startswith(b"\xef\xbb\xbf")
        text = content.decode("utf-8")
        assert max(map(len, text.splitlines())) <= 99
        tree = ast.parse(text)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not any(
            imported == blocked or imported.startswith(f"{blocked}.")
            for imported in imports for blocked in prohibited
        )
        assert "NotImplementedError" not in text
        assert "TODO" not in text
