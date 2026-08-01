"""Contract and architecture tests for SPR-008I query foundation."""

from __future__ import annotations

import ast
import inspect
import json
import logging
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

import cko.core as core
import cko.core.discovery as discovery
from cko.core.discovery import (
    QUERY_SCHEMA_VERSION,
    DiscoveryQuery,
    FilterGroup,
    FilterGroupOperator,
    InvalidFilterError,
    InvalidOrderingError,
    InvalidPaginationError,
    InvalidProjectionError,
    InvalidQueryError,
    QueryError,
    QueryFilter,
    QueryOperator,
    QueryOrdering,
    QueryOrderingDirection,
    QueryPagination,
    QueryPlan,
    QueryProjection,
    QueryResolutionError,
    QueryResolver,
    QueryValidationEngine,
    QueryValidationError,
)


INSTANT = datetime(2026, 7, 15, 12, 30, tzinfo=timezone.utc)


def atomic_filter(
    attribute: str = "media_type",
    operator: QueryOperator = QueryOperator.EQUALS,
    value: object = "application/pdf",
) -> QueryFilter:
    """Build a valid atomic filter for query tests."""
    return QueryFilter(attribute, operator, value)


def canonical_query(**changes: object) -> DiscoveryQuery:
    """Build a representative valid query with deterministic declarations."""
    values: dict[str, object] = {
        "id": "query-documents",
        "name": "Documents",
        "description": "Select canonical PDF documents",
        "filters": (
            FilterGroup(
                FilterGroupOperator.AND,
                (
                    atomic_filter(),
                    QueryFilter(
                        "status",
                        QueryOperator.IN,
                        ("active", "review"),
                    ),
                ),
            ),
        ),
        "projections": (
            QueryProjection("canonical_id"),
            QueryProjection("name"),
        ),
        "ordering": (
            QueryOrdering(
                "name", QueryOrderingDirection.ASCENDING, priority=1
            ),
            QueryOrdering(
                "canonical_id",
                QueryOrderingDirection.DESCENDING,
                priority=0,
            ),
        ),
        "pagination": QueryPagination(
            page=2,
            page_size=25,
            offset=25,
            limit=25,
        ),
        "limit": 25,
        "offset": 25,
    }
    values.update(changes)
    return DiscoveryQuery(**values)


def test_models_are_frozen_and_nested_values_are_deeply_immutable() -> None:
    source = {"tags": ["approved", {"level": 2}]}
    query_filter = QueryFilter("metadata", QueryOperator.EQUALS, source)
    query = canonical_query(filters=(query_filter,))
    plan = QueryResolver().resolve(query, timestamp=INSTANT)

    with pytest.raises(FrozenInstanceError):
        query.name = "changed"
    with pytest.raises(TypeError):
        query_filter.value["new"] = True
    source["tags"].append("changed")
    assert query_filter.value["tags"] == ("approved", {"level": 2})
    with pytest.raises(TypeError):
        plan.estimates["new"] = 1


@pytest.mark.parametrize("operator", tuple(QueryOperator))
def test_all_canonical_filter_operators_are_supported(
    operator: QueryOperator,
) -> None:
    if operator in {QueryOperator.EXISTS, QueryOperator.NOT_EXISTS}:
        value: object = None
    elif operator in {QueryOperator.IN, QueryOperator.NOT_IN}:
        value = ("one", "two")
    elif operator in {
        QueryOperator.CONTAINS,
        QueryOperator.STARTS_WITH,
        QueryOperator.ENDS_WITH,
    }:
        value = "text"
    else:
        value = 10
    query_filter = QueryFilter("attribute", operator, value)
    assert query_filter.operator is operator
    assert QueryFilter.from_json(query_filter.to_json()) == query_filter


def test_filter_value_and_operator_invariants_are_enforced() -> None:
    with pytest.raises(InvalidFilterError):
        QueryFilter("attribute", "unknown", 1)
    with pytest.raises(InvalidFilterError):
        QueryFilter("attribute", QueryOperator.EXISTS, True)
    with pytest.raises(InvalidFilterError):
        QueryFilter("attribute", QueryOperator.IN, ())
    with pytest.raises(InvalidFilterError):
        QueryFilter("attribute", QueryOperator.EQUALS, float("inf"))
    with pytest.raises(InvalidFilterError):
        QueryFilter("attribute", QueryOperator.EQUALS, object())


def test_filter_groups_support_and_or_not_recursively() -> None:
    left = atomic_filter("left", QueryOperator.EQUALS, 1)
    right = atomic_filter("right", QueryOperator.NOT_EQUALS, 2)
    group = FilterGroup(
        FilterGroupOperator.OR,
        (
            left,
            FilterGroup(FilterGroupOperator.NOT, (right,)),
        ),
    )
    assert FilterGroup.from_json(group.to_json()) == group
    assert group.operator is FilterGroupOperator.OR
    assert group.filters[1].operator is FilterGroupOperator.NOT


def test_invalid_filter_groups_are_rejected() -> None:
    with pytest.raises(InvalidFilterError):
        FilterGroup(FilterGroupOperator.AND, ())
    with pytest.raises(InvalidFilterError):
        FilterGroup(FilterGroupOperator.NOT, (atomic_filter(), atomic_filter()))
    with pytest.raises(InvalidFilterError):
        FilterGroup("XOR", (atomic_filter(),))
    with pytest.raises(InvalidFilterError):
        FilterGroup(FilterGroupOperator.AND, (object(),))


def test_filter_validation_checks_operator_specific_value_shapes() -> None:
    validator = QueryValidationEngine()
    with pytest.raises(InvalidFilterError):
        validator.validate_filters(
            (QueryFilter("name", QueryOperator.CONTAINS, 10),)
        )
    with pytest.raises(InvalidFilterError):
        validator.validate_filters(
            (
                QueryFilter(
                    "size",
                    QueryOperator.GREATER_THAN,
                    {"unexpected": "mapping"},
                ),
            )
        )


def test_projection_validation_rejects_duplicate_attributes() -> None:
    validator = QueryValidationEngine()
    with pytest.raises(InvalidProjectionError, match="duplicate"):
        validator.validate(canonical_query(projections=(
            QueryProjection("id"),
            QueryProjection("id"),
        )))
    with pytest.raises(InvalidProjectionError):
        QueryProjection(" ")


def test_ordering_validation_is_deterministic_and_rejects_duplicates() -> None:
    validator = QueryValidationEngine()
    ordered = validator.validate_ordering((
        QueryOrdering("second", priority=2),
        QueryOrdering("first", priority=1),
    ))
    assert tuple(item.attribute for item in ordered) == ("first", "second")
    with pytest.raises(InvalidOrderingError, match="attributes"):
        validator.validate(canonical_query(ordering=(
            QueryOrdering("id", priority=0),
            QueryOrdering("id", priority=1),
        )))
    with pytest.raises(InvalidOrderingError, match="priorities"):
        validator.validate(canonical_query(ordering=(
            QueryOrdering("id", priority=0),
            QueryOrdering("name", priority=0),
        )))


def test_ordering_model_rejects_invalid_direction_and_priority() -> None:
    with pytest.raises(InvalidOrderingError):
        QueryOrdering("id", "sideways")
    with pytest.raises(InvalidOrderingError):
        QueryOrdering("id", priority=-1)
    with pytest.raises(InvalidOrderingError):
        QueryOrdering("id", priority=True)


def test_pagination_supports_page_and_offset_forms() -> None:
    page = QueryPagination(page=3, page_size=20)
    offset = QueryPagination(offset=40, limit=20)
    assert QueryPagination.from_json(page.to_json()) == page
    assert QueryPagination.from_json(offset.to_json()) == offset
    resolved = QueryResolver().resolve(
        canonical_query(pagination=page, limit=None, offset=None),
        timestamp=INSTANT,
    )
    assert resolved.pagination == QueryPagination(
        page=3,
        page_size=20,
        offset=40,
        limit=20,
    )


@pytest.mark.parametrize(
    "values",
    (
        {"page": 0, "page_size": 10},
        {"page": 1},
        {"offset": -1, "limit": 10},
        {"offset": 0, "limit": 0},
        {},
    ),
)
def test_invalid_pagination_values_are_rejected(
    values: dict[str, int],
) -> None:
    with pytest.raises(InvalidPaginationError):
        QueryPagination(**values)


def test_cross_model_pagination_conflicts_are_rejected() -> None:
    validator = QueryValidationEngine()
    with pytest.raises(InvalidPaginationError, match="offset"):
        validator.validate(canonical_query(
            pagination=QueryPagination(
                page=2, page_size=10, offset=5, limit=10
            ),
            limit=10,
            offset=5,
        ))
    with pytest.raises(InvalidPaginationError, match="page_size"):
        validator.validate(canonical_query(
            pagination=QueryPagination(
                page=1, page_size=10, offset=0, limit=20
            ),
            limit=20,
            offset=0,
        ))
    with pytest.raises(InvalidPaginationError, match="query limit"):
        validator.validate(canonical_query(limit=50))


def test_query_model_validates_required_fields_and_member_types() -> None:
    with pytest.raises(InvalidQueryError):
        canonical_query(id="")
    with pytest.raises(InvalidQueryError):
        canonical_query(filters=(object(),))
    with pytest.raises(InvalidQueryError):
        canonical_query(projections=(object(),))
    with pytest.raises(InvalidQueryError):
        canonical_query(ordering=(object(),))
    with pytest.raises(InvalidQueryError):
        canonical_query(pagination=object())
    with pytest.raises(InvalidQueryError):
        canonical_query(limit=0)


def test_query_serialization_is_versioned_deterministic_and_reversible() -> None:
    query = canonical_query()
    serialized = query.to_json()
    assert serialized == query.to_json()
    assert json.loads(serialized)["schema_version"] == QUERY_SCHEMA_VERSION
    assert DiscoveryQuery.from_json(serialized) == query
    assert DiscoveryQuery.from_dict(query.to_dict()) == query


def test_strict_query_deserialization_rejects_malformed_envelopes() -> None:
    payload = canonical_query().to_dict()
    payload["unknown"] = True
    with pytest.raises(InvalidQueryError, match="unknown"):
        DiscoveryQuery.from_dict(payload)

    payload = canonical_query().to_dict()
    payload["schema_version"] = "2.0"
    with pytest.raises(InvalidQueryError, match="schema"):
        DiscoveryQuery.from_dict(payload)

    payload = canonical_query().to_dict()
    payload["projections"] = ["not-an-object"]
    with pytest.raises(InvalidQueryError):
        DiscoveryQuery.from_dict(payload)

    with pytest.raises(InvalidQueryError):
        DiscoveryQuery.from_json("[]")
    with pytest.raises(InvalidQueryError):
        DiscoveryQuery.from_json("not-json")


def test_resolver_creates_auditable_neutral_logical_plan() -> None:
    query = canonical_query()
    plan = QueryResolver().resolve(query, timestamp=INSTANT)
    assert plan.query_id == query.id
    assert plan.effective_filters == query.filters
    assert plan.projections == query.projections
    assert tuple(item.priority for item in plan.ordering) == (0, 1)
    assert plan.pagination == query.pagination
    assert plan.estimates["filter_predicate_count"] == 2
    assert plan.estimates["logical_group_count"] == 1
    assert plan.estimates["result_cardinality_upper_bound"] == 25
    assert plan.justifications
    assert plan.timestamp == INSTANT


def test_query_plan_serialization_is_versioned_and_reversible() -> None:
    plan = QueryResolver().resolve(canonical_query(), timestamp=INSTANT)
    assert QueryPlan.from_json(plan.to_json()) == plan
    assert QueryPlan.from_dict(plan.to_dict()) == plan
    assert '"schema_version":"1.0"' in plan.to_json()


def test_unbounded_query_plan_is_explicit_and_deterministic() -> None:
    query = canonical_query(
        filters=(),
        projections=(),
        ordering=(),
        pagination=None,
        limit=None,
        offset=None,
    )
    plan = QueryResolver().resolve(query, timestamp=INSTANT)
    assert plan.pagination is None
    assert plan.estimates["result_cardinality_upper_bound"] is None
    assert plan.justifications == (
        "top-level filters are combined by implicit AND",
        "no explicit projection requested",
        "no explicit ordering requested",
        "unbounded logical result requested",
    )


def test_resolver_emits_structured_start_and_completion_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        QueryResolver().resolve(canonical_query(), timestamp=INSTANT)
    events = {
        getattr(record, "event", None)
        for record in caplog.records
    }
    assert "discovery.query.resolution.started" in events
    assert "discovery.query.resolution.completed" in events
    completed = next(
        record
        for record in caplog.records
        if getattr(record, "event", None)
        == "discovery.query.resolution.completed"
    )
    assert completed.context["query_id"] == "query-documents"
    assert completed.context["filter_count"] == 2


def test_validation_and_resolution_failures_use_public_errors(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with pytest.raises(QueryValidationError):
        QueryValidationEngine().validate(object())

    class BrokenValidator:
        def validate(self, query: DiscoveryQuery) -> DiscoveryQuery:
            raise RuntimeError("internal validation failure")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(QueryResolutionError) as captured:
            QueryResolver(BrokenValidator()).resolve(canonical_query())
    assert isinstance(captured.value.__cause__, RuntimeError)
    assert any(
        getattr(record, "event", None)
        == "discovery.query.resolution.failed"
        for record in caplog.records
    )


def test_public_error_hierarchy_and_additive_exports_are_stable() -> None:
    for error_type in (
        InvalidQueryError,
        InvalidFilterError,
        InvalidProjectionError,
        InvalidOrderingError,
        InvalidPaginationError,
        QueryValidationError,
        QueryResolutionError,
    ):
        assert issubclass(error_type, QueryError)
    for name in (
        "DiscoveryQuery",
        "QueryFilter",
        "FilterGroup",
        "QueryProjection",
        "QueryOrdering",
        "QueryPagination",
        "QueryPlan",
        "QueryValidationEngine",
        "QueryResolver",
    ):
        assert getattr(discovery, name) is getattr(core, name)
        assert name in discovery.__all__
        assert name in core.__all__


def test_public_type_hints_docstrings_utf8_and_pep8_are_present() -> None:
    public_objects = (
        DiscoveryQuery,
        QueryFilter,
        FilterGroup,
        QueryProjection,
        QueryOrdering,
        QueryPagination,
        QueryPlan,
        QueryValidationEngine,
        QueryResolver,
    )
    for item in public_objects:
        assert inspect.getdoc(item)
    for method in (
        QueryValidationEngine.validate,
        QueryResolver.resolve,
        DiscoveryQuery.to_json,
        QueryPlan.from_json,
    ):
        assert inspect.getdoc(method)
        signature = inspect.signature(method)
        assert signature.return_annotation is not inspect.Signature.empty
        assert all(
            parameter.annotation is not inspect.Signature.empty
            for name, parameter in signature.parameters.items()
            if name not in {"self", "cls"}
        )

    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    for name in (
        "query_errors.py",
        "query_models.py",
        "query_validation.py",
        "query_resolution.py",
    ):
        content = (root / name).read_bytes()
        assert not content.startswith(b"\xef\xbb\xbf")
        text = content.decode("utf-8")
        assert max(map(len, text.splitlines())) <= 99
        ast.parse(text)


def test_new_modules_have_no_prohibited_infrastructure_or_placeholders() -> None:
    prohibited = {
        "os",
        "pathlib",
        "sqlite3",
        "requests",
        "urllib",
        "http",
        "socket",
        "cko.core.inventory",
    }
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    for name in (
        "query_errors.py",
        "query_models.py",
        "query_validation.py",
        "query_resolution.py",
    ):
        text = (root / name).read_text(encoding="utf-8")
        tree = ast.parse(text)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        assert not any(
            imported == blocked or imported.startswith(f"{blocked}.")
            for imported in imports
            for blocked in prohibited
        )
        assert "NotImplementedError" not in text
        assert "TODO" not in text
        assert not any(
            isinstance(node, ast.FunctionDef)
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Pass)
            for node in ast.walk(tree)
        )
