"""Production contracts for SPR-008L statistics and cost foundation."""

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
    STATISTICS_SCHEMA_VERSION,
    AttributeStatistics,
    CostEstimate,
    CostEstimator,
    EstimationStrategy,
    FilterGroup,
    FilterGroupOperator,
    Histogram,
    HistogramBucket,
    HistogramBuilder,
    HistogramPolicy,
    IndexStrategy,
    LogicalIndex,
    LogicalIndexBuilder,
    LogicalStatistics,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryPlan,
    StatisticsBuilder,
    StatisticsPolicy,
    StatisticsReport,
    StatisticsValidationError,
    StatisticsValidator,
)


INSTANT = datetime(2026, 7, 17, 18, 0, tzinfo=timezone.utc)
SUBJECTS = (
    {"id": "asset-a", "kind": "document", "size": 10, "active": True},
    {"id": "asset-b", "kind": "document", "size": 20, "active": True},
    {"id": "asset-c", "kind": "image", "size": 30, "active": False},
    {"id": "asset-d", "kind": None, "size": 40, "active": True},
)


def build_index(attribute: str = "kind") -> LogicalIndex:
    """Build a deterministic SPR-008K index fixture."""
    return LogicalIndexBuilder().build(
        f"idx-{attribute}",
        f"Index {attribute}",
        SUBJECTS,
        (attribute,),
        strategy=IndexStrategy.HASH,
        relevant_attributes=("kind", "size", "active"),
        timestamp=INSTANT,
    )


def build_statistics(attribute: str = "kind") -> LogicalStatistics:
    """Build deterministic SPR-008L statistics from the index fixture."""
    return StatisticsBuilder().build(build_index(attribute))


def plan(*filters: object, ordering: tuple[QueryOrdering, ...] = ()) -> QueryPlan:
    """Build a deterministic homologated query plan."""
    return QueryPlan(
        query_id="query-l",
        effective_filters=filters,
        projections=(),
        ordering=ordering,
        pagination=None,
        timestamp=INSTANT,
    )


def test_models_are_frozen_deeply_immutable_and_versioned() -> None:
    statistics = build_statistics()
    with pytest.raises(FrozenInstanceError):
        statistics.index_id = "changed"
    with pytest.raises(FrozenInstanceError):
        statistics.attributes[0].attribute_name = "changed"
    with pytest.raises(TypeError):
        statistics.metadata["changed"] = True
    assert statistics.schema_version == STATISTICS_SCHEMA_VERSION
    assert statistics.to_dict()["schema_version"] == STATISTICS_SCHEMA_VERSION


@pytest.mark.parametrize(
    "model",
    (
        HistogramBucket(0, (1, 2), 2, 2),
        Histogram("h", "size", "numeric", (HistogramBucket(0, (1, 2), 2, 2),), 2),
        AttributeStatistics("size", 2, 0, 0, 1, 2, 1.0, "h", 0.5),
        StatisticsPolicy(),
        CostEstimate(2.0, 1, 0.5, 0.8, "deterministic estimate"),
    ),
)
def test_models_round_trip_with_strict_schema(model: object) -> None:
    assert type(model).from_json(model.to_json()) == model
    malformed = model.to_dict()
    malformed["unknown"] = True
    with pytest.raises(ValueError, match="unknown"):
        type(model).from_dict(malformed)


def test_logical_statistics_and_report_round_trip() -> None:
    statistics = build_statistics()
    estimate = CostEstimator().estimate(
        plan(QueryFilter("kind", QueryOperator.EQUALS, "document")), statistics
    )
    report = StatisticsReport(
        statistics_used=(statistics.statistics_id,),
        histograms_used=(statistics.histograms[0].reference,),
        justifications=(estimate.justification,),
        cost=estimate,
        timestamp=INSTANT,
    )
    assert LogicalStatistics.from_json(statistics.to_json()) == statistics
    assert StatisticsReport.from_json(report.to_json()) == report
    assert "document" in statistics.to_json()


@pytest.mark.parametrize(
    ("values", "kind", "frequencies"),
    (
        ((1, 2, 3, 4), "numeric", 4),
        (("b", "a", "a"), "string", 3),
        ((True, False, True), "boolean", 3),
    ),
)
def test_histogram_builder_supports_required_scalar_types(
    values: tuple[object, ...], kind: str, frequencies: int
) -> None:
    histogram = HistogramBuilder(StatisticsPolicy(max_buckets=2)).build(
        "field", values
    )
    assert histogram.value_type == kind
    assert len(histogram.buckets) <= 2
    assert sum(item.frequency for item in histogram.buckets) == frequencies
    assert histogram.buckets[-1].cumulative_frequency == frequencies


def test_histogram_equal_frequency_is_deterministic_and_bounded() -> None:
    builder = HistogramBuilder(StatisticsPolicy(
        max_buckets=3,
        histogram_policy=HistogramPolicy.EQUAL_FREQUENCY,
    ))
    first = builder.build("size", reversed(range(10)))
    second = builder.build("size", range(10))
    assert first.to_json() == second.to_json()
    assert [bucket.bucket for bucket in first.buckets] == [0, 1, 2]


def test_histogram_rejects_empty_mixed_unsupported_and_bad_buckets() -> None:
    builder = HistogramBuilder()
    for values in ((), (1, "one"), (object(),)):
        with pytest.raises(ValueError):
            builder.build("field", values)
    with pytest.raises(ValueError, match="contiguous"):
        Histogram("h", "x", "numeric", (HistogramBucket(1, (1, 1), 1, 1),), 1)
    with pytest.raises(ValueError, match="cumulative"):
        Histogram("h", "x", "numeric", (HistogramBucket(0, (1, 1), 1, 2),), 1)


def test_statistics_builder_produces_cardinality_selectivity_and_distribution() -> None:
    statistics = build_statistics()
    assert statistics.total_entries == 4
    assert statistics.distinct_keys == 2
    assert statistics.null_values == 1
    assert statistics.duplicated_keys == 1
    assert statistics.average_density == 0.5
    assert statistics.average_selectivity == 0.5
    assert statistics.estimated_cardinality == 2
    assert statistics.metadata["logical_distribution"]
    attribute = statistics.attributes[0]
    assert attribute.null_count == 1
    assert attribute.distinct_values == 2
    assert attribute.duplicated_count == 1


def test_statistics_builder_is_deterministic_and_does_not_mutate_index() -> None:
    index = build_index("size")
    before = index.to_json()
    first = StatisticsBuilder().build(index)
    second = StatisticsBuilder().build(index)
    assert first.to_json() == second.to_json()
    assert index.to_json() == before


def test_statistics_builder_handles_empty_index_without_histograms() -> None:
    index = LogicalIndexBuilder().build(
        "empty", "Empty", (), ("kind",), timestamp=INSTANT
    )
    statistics = StatisticsBuilder().build(index)
    assert statistics.total_entries == 0
    assert statistics.attributes[0].histogram_reference is None
    assert statistics.histograms == ()
    assert StatisticsValidator().is_valid(statistics)


def test_validator_detects_cardinality_distribution_and_bucket_limits() -> None:
    valid = build_statistics("size")
    assert StatisticsValidator().validate(valid) is valid
    broken = LogicalStatistics(
        statistics_id="broken",
        index_id="idx",
        timestamp=INSTANT,
        total_entries=4,
        distinct_keys=2,
        null_values=0,
        duplicated_keys=2,
        average_density=0.25,
        average_selectivity=0.5,
        estimated_cardinality=2,
    )
    with pytest.raises(StatisticsValidationError, match="density"):
        StatisticsValidator().validate(broken)
    assert not StatisticsValidator().is_valid(broken)
    with pytest.raises(StatisticsValidationError, match="bucket"):
        StatisticsValidator().validate(valid, policy=StatisticsPolicy(max_buckets=1))


def test_cost_estimator_estimates_equality_rows_selectivity_and_cost() -> None:
    statistics = build_statistics()
    estimate = CostEstimator().estimate(
        plan(QueryFilter("kind", QueryOperator.EQUALS, "document")), statistics
    )
    assert estimate.estimated_selectivity == 0.5
    assert estimate.estimated_rows == 2
    assert estimate.estimated_cost > 0
    assert estimate.confidence == 1.0
    assert "no query was executed" in estimate.justification


@pytest.mark.parametrize(
    ("operator", "value", "expected"),
    (
        (QueryOperator.NOT_EQUALS, "document", 0.5),
        (QueryOperator.EXISTS, None, 0.75),
        (QueryOperator.NOT_EXISTS, None, 0.25),
        (QueryOperator.IN, ("document", "image"), 1.0),
        (QueryOperator.NOT_IN, ("document",), 0.5),
        (QueryOperator.STARTS_WITH, "doc", 0.5),
        (QueryOperator.CONTAINS, "oc", 0.5),
    ),
)
def test_cost_estimator_supports_logical_operator_selectivity(
    operator: QueryOperator, value: object, expected: float
) -> None:
    estimate = CostEstimator().estimate(
        plan(QueryFilter("kind", operator, value)), build_statistics()
    )
    assert estimate.estimated_selectivity == expected


def test_cost_estimator_handles_ranges_groups_ordering_and_unknown_attributes() -> None:
    statistics = build_statistics("size")
    grouped = FilterGroup(FilterGroupOperator.OR, (
        QueryFilter("size", QueryOperator.LOWER_THAN, 20),
        QueryFilter("size", QueryOperator.GREATER_THAN, 30),
    ))
    ordered = plan(grouped, ordering=(QueryOrdering("size"),))
    estimate = CostEstimator().estimate(ordered, statistics)
    assert 0 < estimate.estimated_selectivity < 1
    assert estimate.estimated_cost > estimate.estimated_rows
    unknown = CostEstimator().estimate(
        plan(QueryFilter("unknown", QueryOperator.EQUALS, 1)), statistics
    )
    assert unknown.estimated_selectivity == 0.25
    assert unknown.confidence == 0.25
    negated = FilterGroup(FilterGroupOperator.NOT, (
        QueryFilter("size", QueryOperator.GREATER_THAN, 20),
    ))
    assert CostEstimator().estimate(plan(negated), statistics).estimated_rows >= 0


def test_cost_estimator_report_audits_statistics_and_histograms() -> None:
    statistics = build_statistics()
    query = plan(QueryFilter("kind", QueryOperator.EQUALS, "document"))
    report = CostEstimator().report(query, statistics, timestamp=INSTANT)
    assert report.statistics_used == (statistics.statistics_id,)
    assert report.histograms_used == (statistics.histograms[0].reference,)
    assert report.timestamp == INSTANT


def test_policy_validation_and_strict_json_errors() -> None:
    assert StatisticsPolicy().estimation_strategy is EstimationStrategy.HYBRID
    for arguments in (
        {"max_buckets": 0},
        {"granularity": 0},
        {"histogram_policy": "invalid"},
        {"estimation_strategy": "invalid"},
        {"limits": {"max_entries": 0, "minimum_confidence": 0.2}},
        {"limits": {"max_entries": 2, "minimum_confidence": 2.0}},
    ):
        with pytest.raises(ValueError):
            StatisticsPolicy(**arguments)
    with pytest.raises(ValueError, match="invalid"):
        StatisticsPolicy.from_json("invalid")
    with pytest.raises(ValueError, match="object"):
        StatisticsPolicy.from_json("[]")


def test_invalid_model_invariants_are_rejected_explicitly() -> None:
    for arguments in (
        (-1, (1, 1), 1, 1),
        (0, (1,), 1, 1),
        (0, (1, 1), 2, 1),
    ):
        with pytest.raises(ValueError):
            HistogramBucket(*arguments)
    bucket = HistogramBucket(0, (1, 1), 1, 1)
    for arguments in (
        ("h", "x", "unsupported", (bucket,), 1),
        ("h", "x", "numeric", ("bad",), 1),
        ("h", "x", "numeric", (bucket,), 2),
    ):
        with pytest.raises(ValueError):
            Histogram(*arguments)
    for arguments in (
        ("x", 1, 0, 0, None, 1, 1.0, None, 1.0),
        ("x", 1, 0, 0, 1, "2", 1.0, None, 1.0),
        ("x", 1, 0, 0, 2, 1, 1.0, None, 1.0),
    ):
        with pytest.raises(ValueError):
            AttributeStatistics(*arguments)
    with pytest.raises(ValueError, match="exceed"):
        LogicalStatistics("s", "i", INSTANT, 1, 2, 0, 0, 1.0, 0.5, 1)


def test_invalid_builder_validator_and_estimator_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="LogicalIndex"):
        StatisticsBuilder().build("invalid")
    with pytest.raises(ValueError, match="entry limit"):
        StatisticsValidator().validate(
            build_statistics(),
            policy=StatisticsPolicy(limits={
                "max_entries": 1, "minimum_confidence": 0.25,
            }),
        )
    with pytest.raises(ValueError, match="LogicalStatistics"):
        StatisticsValidator().validate("invalid")
    with pytest.raises(ValueError, match="QueryPlan"):
        CostEstimator().estimate("invalid", build_statistics())
    with pytest.raises(ValueError, match="LogicalStatistics"):
        CostEstimator().estimate(plan(), "invalid")


def test_mixed_numeric_statistics_have_canonical_bounds() -> None:
    source = (
        {"id": "a", "value": 1},
        {"id": "b", "value": 2.5},
    )
    index = LogicalIndexBuilder().build(
        "mixed", "Mixed", source, ("value",), timestamp=INSTANT
    )
    attribute = StatisticsBuilder().build(index).attributes[0]
    assert attribute.minimum == 1.0
    assert attribute.maximum == 2.5


def test_structured_logging_covers_required_lifecycle(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        statistics = build_statistics()
        CostEstimator().estimate(
            plan(QueryFilter("kind", QueryOperator.EQUALS, "document")),
            statistics,
        )
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "discovery.query.statistics.construction_started",
        "discovery.query.statistics.validation_completed",
        "discovery.query.statistics.estimation_started",
        "discovery.query.statistics.estimation_completed",
        "discovery.query.statistics.completed",
    } <= events


def test_public_api_type_hints_docstrings_utf8_pep8_and_boundaries() -> None:
    public = (
        LogicalStatistics, AttributeStatistics, Histogram, HistogramBucket,
        HistogramBuilder, StatisticsBuilder, StatisticsValidator, CostEstimate,
        CostEstimator, StatisticsPolicy, StatisticsReport,
    )
    assert all(inspect.getdoc(item) for item in public)
    for method in (
        HistogramBuilder.build, StatisticsBuilder.build,
        StatisticsValidator.validate, CostEstimator.estimate, CostEstimator.report,
    ):
        assert inspect.signature(method).return_annotation is not inspect.Signature.empty
        assert inspect.getdoc(method)
    for name in (
        "LogicalStatistics", "HistogramBuilder", "StatisticsBuilder",
        "StatisticsValidator", "CostEstimator", "StatisticsPolicy",
    ):
        assert getattr(core, name) is getattr(discovery, name)
        assert name in core.__all__ and name in discovery.__all__
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    prohibited = {
        "os", "pathlib", "sqlite3", "requests", "urllib", "http", "socket",
        "redis", "sqlalchemy", "cko.persistence", "cko.repository",
    }
    for name in ("statistics_errors.py", "statistics_models.py", "statistics.py"):
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
