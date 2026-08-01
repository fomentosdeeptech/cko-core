"""Production contract, behavior and architecture tests for SPR-008J."""

from __future__ import annotations

import ast
import asyncio
import inspect
import logging
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType

import pytest

import cko.core as core
import cko.core.discovery as discovery
from cko.core.discovery import (
    QUERY_EVALUATION_SCHEMA_VERSION,
    AttributeResolutionError,
    CancellationToken,
    DefaultAttributeResolver,
    DefaultQueryEvaluationStream,
    EvaluationErrorBehavior,
    FilterGroup,
    FilterGroupOperator,
    IncompatibleTypeBehavior,
    InvalidQueryEvaluationPolicyError,
    InvalidQueryEvaluationSubjectError,
    MappingQueryEvaluationSubject,
    MissingAttributeBehavior,
    OrderingValuePosition,
    PredicateEvaluationError,
    PredicateEvaluationRecord,
    QueryEvaluationCancelledError,
    QueryEvaluationContext,
    QueryEvaluationEngine,
    QueryEvaluationLimitError,
    QueryEvaluationPolicy,
    QueryEvaluationResult,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryOrderingDirection,
    QueryOrderingEvaluationError,
    QueryPagination,
    QueryPlan,
    QueryProjection,
    QueryResolver,
)


INSTANT = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def plan(
    *,
    filters: tuple[object, ...] = (),
    projections: tuple[QueryProjection, ...] = (),
    ordering: tuple[QueryOrdering, ...] = (),
    pagination: QueryPagination | None = None,
) -> QueryPlan:
    """Create a deterministic homologated plan for evaluation tests."""
    return QueryPlan(
        query_id="query-evaluation",
        effective_filters=filters,
        projections=projections,
        ordering=ordering,
        pagination=pagination,
        timestamp=INSTANT,
    )


def context(token: CancellationToken | None = None) -> QueryEvaluationContext:
    """Create a deterministic evaluation context."""
    return QueryEvaluationContext(
        correlation_id="correlation-1",
        actor="test-suite",
        timestamp=INSTANT,
        attributes={"purpose": "verification"},
        cancellation_token=token,
    )


def subject(identity: str, **values: object) -> MappingQueryEvaluationSubject:
    """Create a mapping-backed subject with a stable logical identity."""
    return MappingQueryEvaluationSubject({"id": identity, **values})


def evaluate(
    query_plan: QueryPlan,
    subjects: list[MappingQueryEvaluationSubject],
    *,
    policy: QueryEvaluationPolicy | None = None,
) -> QueryEvaluationResult:
    """Evaluate using the deterministic test context."""
    return QueryEvaluationEngine(policy=policy).evaluate(
        query_plan, subjects, context=context()
    )


def test_models_are_frozen_deeply_immutable_and_versioned() -> None:
    policy = QueryEvaluationPolicy()
    evaluation_context = context()
    record = PredicateEvaluationRecord(
        "metadata", "equals", {"level": [1]}, {"level": [1]}, True,
        True, "values match", "MATCH", ("metadata",),
    )
    with pytest.raises(FrozenInstanceError):
        policy.max_subjects = 2
    with pytest.raises(TypeError):
        evaluation_context.attributes["new"] = True
    with pytest.raises(TypeError):
        record.expected_value["new"] = True
    assert record.expected_value["level"] == (1,)
    assert record.to_dict()["schema_version"] == QUERY_EVALUATION_SCHEMA_VERSION
    assert PredicateEvaluationRecord.from_json(record.to_json()) == record


def test_strict_deserialization_rejects_missing_unknown_and_versions() -> None:
    payload = QueryEvaluationPolicy().to_dict()
    del payload["max_subjects"]
    with pytest.raises(ValueError, match="missing"):
        QueryEvaluationPolicy.from_dict(payload)
    payload = QueryEvaluationPolicy().to_dict()
    payload["unknown"] = True
    with pytest.raises(ValueError, match="unknown"):
        QueryEvaluationPolicy.from_dict(payload)
    payload = QueryEvaluationPolicy().to_dict()
    payload["schema_version"] = "99.0"
    with pytest.raises(ValueError, match="version"):
        QueryEvaluationPolicy.from_dict(payload)


def test_policy_validation_and_context_round_trip() -> None:
    with pytest.raises(InvalidQueryEvaluationPolicyError):
        QueryEvaluationPolicy(max_subjects=0)
    with pytest.raises(InvalidQueryEvaluationPolicyError):
        QueryEvaluationPolicy(
            evaluation_error=EvaluationErrorBehavior.RECORD,
            allow_partial_evaluation=False,
        )
    restored = QueryEvaluationContext.from_json(context().to_json())
    assert restored.correlation_id == "correlation-1"
    assert restored.attributes == {"purpose": "verification"}


def test_mapping_subject_and_attribute_resolution_distinguish_missing_none() -> None:
    resolver = DefaultAttributeResolver()
    item = subject(
        "one",
        metadata=MappingProxyType({"owner": {"name": "Ana"}}),
        nullable=None,
    )
    assert resolver.resolve(item, "metadata.owner.name").value == "Ana"
    nullable = resolver.resolve(item, "nullable")
    missing = resolver.resolve(item, "absent")
    assert nullable.exists and nullable.value is None
    assert not missing.exists and missing.value is None
    with pytest.raises(AttributeResolutionError):
        resolver.resolve(item, "_private")


@pytest.mark.parametrize(
    ("operator", "observed", "expected", "matched"),
    (
        (QueryOperator.EQUALS, 3, 3, True),
        (QueryOperator.NOT_EQUALS, 3, 4, True),
        (QueryOperator.GREATER_THAN, 3, 2, True),
        (QueryOperator.GREATER_OR_EQUAL, 3, 3, True),
        (QueryOperator.LOWER_THAN, 2, 3, True),
        (QueryOperator.LOWER_OR_EQUAL, 3, 3, True),
        (QueryOperator.CONTAINS, "canonical", "non", True),
        (QueryOperator.CONTAINS, ("a", "b"), "b", True),
        (QueryOperator.CONTAINS, {"key": 1}, "key", True),
        (QueryOperator.STARTS_WITH, "canonical", "can", True),
        (QueryOperator.ENDS_WITH, "canonical", "cal", True),
        (QueryOperator.IN, "a", ("a", "b"), True),
        (QueryOperator.NOT_IN, "c", ("a", "b"), True),
    ),
)
def test_all_value_operators(
    operator: QueryOperator,
    observed: object,
    expected: object,
    matched: bool,
) -> None:
    result = evaluate(
        plan(filters=(QueryFilter("value", operator, expected),)),
        [subject("one", value=observed)],
    )
    assert result.evaluation_records[0].matched is matched
    assert result.evaluation_records[0].predicate_records[0].operator == operator.value


def test_exists_and_not_exists_ignore_none_value() -> None:
    query_plan = plan(filters=(
        QueryFilter("nullable", QueryOperator.EXISTS),
        QueryFilter("absent", QueryOperator.NOT_EXISTS),
    ))
    result = evaluate(query_plan, [subject("one", nullable=None)])
    assert result.total_matched == 1
    assert [item.code for item in result.evaluation_records[0].predicate_records] == [
        "EXISTS", "NOT_EXISTS"
    ]


def test_incompatible_types_and_boolean_integer_are_explicit() -> None:
    query_plan = plan(filters=(QueryFilter("value", QueryOperator.EQUALS, 1),))
    with pytest.raises(PredicateEvaluationError) as captured:
        evaluate(query_plan, [subject("one", value=True)])
    assert isinstance(captured.value.__cause__, TypeError)
    policy = QueryEvaluationPolicy(
        incompatible_type=IncompatibleTypeBehavior.NO_MATCH
    )
    result = evaluate(query_plan, [subject("one", value=True)], policy=policy)
    assert result.total_rejected == 1
    assert result.evaluation_records[0].predicate_records[0].code == (
        "INCOMPATIBLE_TYPE"
    )


def test_missing_attribute_policy_is_explicit() -> None:
    query_plan = plan(filters=(QueryFilter("missing", QueryOperator.EQUALS, 1),))
    result = evaluate(query_plan, [subject("one")])
    assert result.evaluation_records[0].missing_attributes == ("missing",)
    policy = QueryEvaluationPolicy(
        missing_attribute=MissingAttributeBehavior.ERROR
    )
    with pytest.raises(PredicateEvaluationError):
        evaluate(query_plan, [subject("one")], policy=policy)


def test_and_or_not_and_short_circuit_are_auditable() -> None:
    first = QueryFilter("value", QueryOperator.EQUALS, 1)
    unsafe = QueryFilter("other", QueryOperator.GREATER_THAN, "wrong")
    groups = (
        FilterGroup(FilterGroupOperator.AND, (first, unsafe)),
        FilterGroup(FilterGroupOperator.OR, (first, unsafe)),
        FilterGroup(FilterGroupOperator.NOT, (
            QueryFilter("value", QueryOperator.EQUALS, 2),
        )),
    )
    and_result = evaluate(plan(filters=(groups[0],)), [subject("one", value=2)])
    assert and_result.total_rejected == 1
    assert and_result.evaluation_records[0].evaluated_filters == 1
    assert "short-circuited" in and_result.evaluation_records[0].justifications[0]
    or_result = evaluate(plan(filters=(groups[1],)), [subject("one", value=1)])
    assert or_result.total_matched == 1
    assert or_result.evaluation_records[0].evaluated_filters == 1
    not_result = evaluate(plan(filters=(groups[2],)), [subject("one", value=1)])
    assert not_result.total_matched == 1


def test_projection_is_immutable_preserves_names_and_represents_missing() -> None:
    source = {"id": "one", "name": "Alpha", "nested": {"value": 2}}
    result = evaluate(
        plan(projections=(
            QueryProjection("name"),
            QueryProjection("nested.value"),
            QueryProjection("missing"),
        )),
        [MappingQueryEvaluationSubject(source)],
    )
    projected = result.projected_items[0]
    assert projected.attributes == {
        "missing": None, "name": "Alpha", "nested.value": 2
    }
    assert projected.missing_attributes == ("missing",)
    with pytest.raises(TypeError):
        projected.attributes["name"] = "changed"
    assert source["name"] == "Alpha"


def test_ordering_priorities_directions_special_values_and_identity_ties() -> None:
    items = [
        subject("c", group="x", rank=2),
        subject("b", group="x", rank=2),
        subject("a", group="x", rank=1),
        subject("none", group="x", rank=None),
        subject("missing", group="x"),
    ]
    query_plan = plan(ordering=(
        QueryOrdering("rank", QueryOrderingDirection.DESCENDING, priority=1),
        QueryOrdering("group", QueryOrderingDirection.ASCENDING, priority=0),
    ))
    result = evaluate(query_plan, items)
    assert result.matched_items == ("b", "c", "a", "missing", "none")
    first_policy = QueryEvaluationPolicy(
        missing_ordering_position=OrderingValuePosition.FIRST,
        none_ordering_position=OrderingValuePosition.FIRST,
    )
    first = evaluate(query_plan, items, policy=first_policy)
    assert first.matched_items[:2] == ("missing", "none")


def test_incompatible_ordering_values_are_rejected() -> None:
    query_plan = plan(ordering=(QueryOrdering("value"),))
    with pytest.raises(QueryOrderingEvaluationError):
        evaluate(query_plan, [subject("a", value=1), subject("b", value="1")])


@pytest.mark.parametrize(
    ("pagination", "expected", "offset", "limit"),
    (
        (QueryPagination(offset=1, limit=2), ("b", "c"), 1, 2),
        (QueryPagination(page=2, page_size=2), ("c", "d"), 2, 2),
    ),
)
def test_pagination_is_applied_after_ordering_with_coherent_totals(
    pagination: QueryPagination,
    expected: tuple[str, ...],
    offset: int,
    limit: int,
) -> None:
    items = [subject(key, rank=index) for index, key in enumerate("abcd")]
    result = evaluate(
        plan(ordering=(QueryOrdering("rank"),), pagination=pagination), items
    )
    assert result.matched_items == expected
    assert result.total_matched == 4
    assert result.total_returned == 2
    assert (result.applied_offset, result.applied_limit) == (offset, limit)


def test_subject_limit_and_partial_evaluation_policy() -> None:
    limited = QueryEvaluationPolicy(max_subjects=1)
    with pytest.raises(QueryEvaluationLimitError):
        evaluate(plan(), [subject("a"), subject("b")], policy=limited)
    partial = QueryEvaluationPolicy(
        missing_attribute=MissingAttributeBehavior.ERROR,
        evaluation_error=EvaluationErrorBehavior.RECORD,
        allow_partial_evaluation=True,
    )
    result = evaluate(
        plan(filters=(QueryFilter("required", QueryOperator.EQUALS, 1),)),
        [subject("bad"), subject("good", required=1)],
        policy=partial,
    )
    assert result.total_evaluated == 2
    assert result.total_matched == 1
    assert result.controlled_errors


def test_cancellation_reuses_canonical_token_and_preserves_cause() -> None:
    token = CancellationToken.create()
    token.cancel("test cancellation")
    with pytest.raises(QueryEvaluationCancelledError) as captured:
        QueryEvaluationEngine().evaluate(
            plan(), [subject("one")], context=context(token)
        )
    assert captured.value.__cause__ is not None


def test_async_iterable_is_equivalent_to_synchronous_execution() -> None:
    items = [subject("b", value=2), subject("a", value=1)]
    query_plan = plan(
        filters=(QueryFilter("value", QueryOperator.GREATER_THAN, 0),),
        ordering=(QueryOrdering("value"),),
        projections=(QueryProjection("value"),),
    )

    async def source() -> object:
        for item in items:
            yield item

    async def exercise() -> tuple[QueryEvaluationResult, QueryEvaluationResult]:
        engine = QueryEvaluationEngine()
        asynchronous = await engine.evaluate_async(
            query_plan, source(), context=context()
        )
        streamed = await DefaultQueryEvaluationStream(engine).evaluate_async(
            query_plan, source()
        )
        return asynchronous, streamed

    synchronous = QueryEvaluationEngine().evaluate(
        query_plan, items, context=context()
    )
    asynchronous, streamed = asyncio.run(exercise())
    assert asynchronous.to_json() == synchronous.to_json()
    assert streamed.matched_items == ("a", "b")


def test_query_plan_is_reused_and_inputs_remain_unchanged() -> None:
    query_filter = QueryFilter("value", QueryOperator.EQUALS, 1)
    query_plan = plan(filters=(query_filter,))
    original_plan_json = query_plan.to_json()
    values = {"id": "one", "value": 1}
    result = QueryEvaluationEngine().evaluate(query_plan, [values], context=context())
    assert result.plan is query_plan
    assert query_plan.to_json() == original_plan_json
    assert values == {"id": "one", "value": 1}


def test_result_round_trip_is_strict_deterministic_and_coherent() -> None:
    result = evaluate(
        plan(
            filters=(QueryFilter("value", QueryOperator.EQUALS, 1),),
            projections=(QueryProjection("value"),),
        ),
        [subject("one", value=1), subject("two", value=2)],
    )
    assert result.to_json() == result.to_json()
    restored = QueryEvaluationResult.from_json(result.to_json())
    assert restored == result
    assert result.total_received == result.total_evaluated == 2
    assert result.total_matched == result.total_returned == 1
    assert result.total_rejected == 1

    malformed = result.to_dict()
    malformed["projected_items"] = ["not-an-object"]
    with pytest.raises(ValueError, match="JSON objects"):
        QueryEvaluationResult.from_dict(malformed)


def test_structured_logging_covers_lifecycle_and_pagination(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        evaluate(plan(pagination=QueryPagination(offset=0, limit=1)), [subject("a")])
    events = {getattr(record, "event", None) for record in caplog.records}
    assert {
        "discovery.query.evaluation.started",
        "discovery.query.evaluation.received",
        "discovery.query.evaluation.pagination_applied",
        "discovery.query.evaluation.completed",
    } <= events


def test_query_resolver_integration_and_public_api_are_additive() -> None:
    from cko.core.discovery import DiscoveryQuery

    query = DiscoveryQuery(
        id="resolved", name="Resolved", description="Resolver integration",
        filters=(QueryFilter("active", QueryOperator.EQUALS, True),),
    )
    resolved = QueryResolver().resolve(query, timestamp=INSTANT)
    result = evaluate(resolved, [subject("one", active=True)])
    assert result.total_matched == 1
    for name in (
        "QueryEvaluationEngine", "QueryEvaluationPolicy",
        "QueryEvaluationContext", "QueryEvaluationResult",
        "MappingQueryEvaluationSubject", "DefaultAttributeResolver",
    ):
        assert getattr(core, name) is getattr(discovery, name)
        assert name in core.__all__ and name in discovery.__all__


def test_type_hints_docstrings_utf8_pep8_and_architecture_boundaries() -> None:
    public = (
        DefaultAttributeResolver,
        QueryEvaluationPolicy,
        QueryEvaluationContext,
        QueryEvaluationResult,
        QueryEvaluationEngine,
        DefaultQueryEvaluationStream,
    )
    assert all(inspect.getdoc(item) for item in public)
    for method in (
        DefaultAttributeResolver.resolve,
        QueryEvaluationEngine.evaluate,
        QueryEvaluationEngine.evaluate_async,
        QueryEvaluationResult.from_json,
    ):
        signature = inspect.signature(method)
        assert signature.return_annotation is not inspect.Signature.empty
        assert inspect.getdoc(method)

    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    prohibited = {
        "os", "pathlib", "sqlite3", "requests", "urllib", "http", "socket",
        "threading", "multiprocessing", "cko.core.inventory",
    }
    for name in (
        "query_evaluation_errors.py", "query_evaluation_contracts.py",
        "query_evaluation_models.py", "query_evaluation.py",
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
