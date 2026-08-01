"""Dedicated acceptance and defensive suite for SPR-014."""

from dataclasses import FrozenInstanceError, dataclass, is_dataclass, replace
from datetime import UTC, datetime, timedelta, timezone
from types import MappingProxyType
from uuid import uuid4

import pytest

from cko.core import CKOError
from cko.core.documents import (
    DocumentDescriptor, DocumentFactory, DocumentMetadata, DocumentSource,
    DocumentSourceType, DocumentType,
)
from cko.core.graph import GraphFactory
from cko.core.knowledge import (
    KnowledgeContent, KnowledgeMetadata, KnowledgeObjectFactory, KnowledgeType,
)
from cko.core.query import (
    QUERY_SCHEMA_VERSION, CanonicalQuery, DeterministicQuerySerializer,
    QueryCollection, QueryConsistency, QueryConstraint, QueryDescriptor,
    QueryDirection, QueryError, QueryExpression, QueryFactory,
    QueryFactoryError, QueryFilter, QueryId, QueryIdentity,
    QueryIdentityError, QueryMetadata, QueryOperator, QueryOrdering,
    QueryPagination, QueryProjection, QueryResult, QueryScope,
    QueryModel, QuerySerializationError, QuerySerializer, QueryStatistics,
    QueryStatus, QueryTarget, QueryValidationError, QueryValidator,
    QueryValidatorContract,
)
from cko.core.query.contracts import (
    deep_freeze, finite_number, instant, model_sequence, non_negative_int,
    parse_instant, primitive, query_value_primitive, semantic_version, strict,
    text, unique_texts,
)
from cko.core.query.models import _FACTORY_TOKEN
from cko.core.query.serializer import _list, _mapping
from cko.core.relationships import (
    RelationshipEndpoint, RelationshipFactory, RelationshipType,
)


NOW = datetime(2026, 7, 26, 20, 0, tzinfo=UTC)


def foundation():
    knowledge = KnowledgeObjectFactory(clock=lambda: NOW).create(
        namespace="cko.science", origin="curation",
        knowledge_type=KnowledgeType.CONCEPT,
        metadata=KnowledgeMetadata(NOW, NOW, author="Alice"),
        content=KnowledgeContent.empty(), created_by="tester",
    )
    document = DocumentFactory(clock=lambda: NOW).create(
        namespace="cko.documents",
        metadata=DocumentMetadata(
            "Canonical", NOW, NOW, creator="Alice",
            sources=(DocumentSource(
                DocumentSourceType.INTERNAL, "source:canonical", "test",
            ),),
        ),
        descriptor=DocumentDescriptor(DocumentType.ARTICLE),
        created_by="tester",
    )
    relationship = RelationshipFactory(clock=lambda: NOW).create(
        namespace="cko.relationships",
        source=RelationshipEndpoint.from_knowledge_object(knowledge),
        target=RelationshipEndpoint.from_document(document),
        relationship_type=RelationshipType.REFERENCES,
        created_by="tester",
    )
    graph = GraphFactory(clock=lambda: NOW).create(
        namespace="cko.graphs", name="Canonical", created_by="tester",
        nodes=(knowledge, document), edges=(relationship,),
    )
    return knowledge, document, relationship, graph


def canonical_models():
    factory = QueryFactory(clock=lambda: NOW)
    namespace_filter = factory.create_filter(
        "namespace", QueryOperator.EQUAL, "cko.science",
    )
    temporal_filter = factory.create_filter(
        "created_at", QueryOperator.BETWEEN,
        NOW - timedelta(days=30), NOW,
    )
    expression = factory.create_expression(
        QueryOperator.AND, (namespace_filter, temporal_filter),
    )
    ordering = factory.create_ordering(
        "created_at", QueryDirection.DESCENDING, 0,
    )
    projection = factory.create_projection(("identity", "metadata.title"))
    pagination = factory.create_pagination(25, 0, "logical:cursor")
    descriptor = factory.create_descriptor(
        targets=(
            QueryTarget.KNOWLEDGE_OBJECT, QueryTarget.CANONICAL_DOCUMENT,
            QueryTarget.CANONICAL_RELATIONSHIP, QueryTarget.CANONICAL_GRAPH,
        ),
        scope=QueryScope.GLOBAL,
        consistency=QueryConsistency.SNAPSHOT,
        expression=expression,
        orderings=(ordering,),
        projection=projection,
        pagination=pagination,
    )
    query = factory.create(
        namespace="cko.queries", name="Canonical intent", created_by="tester",
        targets=descriptor.targets, scope=descriptor.scope,
        consistency=descriptor.consistency, expression=descriptor.expression,
        orderings=descriptor.orderings, projection=descriptor.projection,
        pagination=descriptor.pagination, tags=("canonical",),
        attributes={"requested_at": NOW},
    )
    items = foundation()
    statistics = factory.create_statistics(10, 4, 3.5, {"sources": 4})
    result = factory.create_result(
        query, items, total_expected=10, logical_time=3.5,
        metrics={"sources": 4}, warnings=("declarative-result",),
        metadata={"trace": "logical"},
    )
    collection = factory.create_collection((query,), "canonical")
    return (
        query.identity.logical_id, query.identity, query.metadata,
        namespace_filter.constraint, namespace_filter, temporal_filter,
        expression, ordering, projection, pagination, descriptor, query,
        statistics, result, collection,
    )


def test_required_models_are_frozen_slotted_versioned_and_discriminated():
    for value in canonical_models():
        assert is_dataclass(value)
        assert type(value).__dataclass_params__.frozen
        assert hasattr(type(value), "__slots__")
        assert value.schema_version == QUERY_SCHEMA_VERSION
        assert value.model == type(value).discriminator
        with pytest.raises((FrozenInstanceError, AttributeError)):
            value.schema_version = "2.0"


def test_all_models_have_deterministic_strict_round_trip_and_sha256():
    serializer = DeterministicQuerySerializer()
    for value in canonical_models():
        payload = serializer.serialize(value)
        assert payload == serializer.serialize(value)
        assert serializer.deserialize(payload) == value
        assert b"NaN" not in payload and b"Infinity" not in payload
        assert len(serializer.digest(value)) == 64


def test_factory_is_mandatory_for_query_result_and_collection():
    factory = QueryFactory(clock=lambda: NOW)
    query = factory.create(
        namespace="cko.queries", name="Factory", created_by="tester",
        targets=(QueryTarget.KNOWLEDGE_OBJECT,),
    )
    with pytest.raises(QueryFactoryError):
        CanonicalQuery(query.identity, query.metadata, query.descriptor)
    with pytest.raises(QueryFactoryError):
        QueryResult(query)
    with pytest.raises(QueryFactoryError):
        QueryCollection((query,))


def test_all_official_filter_dimensions_are_declarative():
    factory = QueryFactory()
    dimensions = {
        "identity": "id", "namespace": "cko", "type": "concept",
        "category": "science", "author": "Alice", "origin": "curation",
        "version": "1.0.0", "status": "active", "created_at": NOW,
        "modified_at": NOW, "temporal": NOW, "tags": "canonical",
        "keywords": "knowledge", "attributes.domain": "science",
        "properties.title": "Canonical",
    }
    filters = tuple(
        factory.create_filter(field, QueryOperator.EQUAL, value)
        for field, value in dimensions.items()
    )
    assert tuple(item.field for item in filters) == tuple(dimensions)
    assert all(not hasattr(item, "execute") for item in filters)


def test_all_comparison_and_logical_operators_are_modeled():
    factory = QueryFactory()
    values = {
        QueryOperator.EQUAL: "a", QueryOperator.NOT_EQUAL: "a",
        QueryOperator.GREATER_THAN: 1, QueryOperator.LESS_THAN: 1,
        QueryOperator.GREATER_OR_EQUAL: 1, QueryOperator.LESS_OR_EQUAL: 1,
        QueryOperator.CONTAINS: "a", QueryOperator.STARTS_WITH: "a",
        QueryOperator.ENDS_WITH: "a", QueryOperator.IN: ("a", "b"),
    }
    filters = tuple(
        factory.create_filter("properties.value", operator, value)
        for operator, value in values.items()
    )
    between = factory.create_filter("properties.value", QueryOperator.BETWEEN, 1, 2)
    assert {item.constraint.operator for item in filters + (between,)} == set(values) | {QueryOperator.BETWEEN}
    left, right = filters[:2]
    assert factory.create_expression(QueryOperator.AND, (left, right)).operator is QueryOperator.AND
    assert factory.create_expression(QueryOperator.OR, (left, right)).operator is QueryOperator.OR
    assert factory.create_expression(QueryOperator.NOT, (left,)).operator is QueryOperator.NOT


def test_pagination_ordering_projection_and_descriptor_constraints():
    factory = QueryFactory()
    orderings = (
        factory.create_ordering("author", QueryDirection.ASCENDING, 0),
        factory.create_ordering("created_at", QueryDirection.DESCENDING, 1),
    )
    descriptor = factory.create_descriptor(
        targets=(QueryTarget.KNOWLEDGE_OBJECT,), orderings=orderings,
        projection=factory.create_projection(("identity",)),
        pagination=factory.create_pagination(50, 10),
    )
    assert descriptor.orderings == orderings
    assert descriptor.pagination.limit == 50
    with pytest.raises(QueryValidationError):
        QueryPagination(10, 1, "cursor")
    with pytest.raises(QueryValidationError):
        QueryPagination(0)
    with pytest.raises(QueryValidationError):
        QueryOrdering("field", priority=-1)
    with pytest.raises(QueryValidationError):
        QueryProjection(("field", "field"))


def test_validator_rejects_filter_expression_and_ordering_duplicates():
    factory = QueryFactory(clock=lambda: NOW)
    item = factory.create_filter("author", QueryOperator.EQUAL, "Alice")
    with pytest.raises(QueryValidationError):
        factory.create_descriptor(
            targets=(QueryTarget.KNOWLEDGE_OBJECT,), filters=(item, item),
        )
    with pytest.raises(QueryValidationError):
        factory.create_expression(QueryOperator.AND, (item, item))
    with pytest.raises(QueryValidationError):
        factory.create_descriptor(
            targets=(QueryTarget.KNOWLEDGE_OBJECT,),
            orderings=(
                factory.create_ordering("author", priority=0),
                factory.create_ordering("created_at", priority=0),
            ),
        )
    expression = factory.create_expression(
        QueryOperator.NOT,
        (factory.create_filter("status", QueryOperator.EQUAL, "archived"),),
    )
    QueryValidator().validate(expression)


def test_results_integrate_only_homologated_foundations_without_execution():
    query = canonical_models()[11]
    factory = QueryFactory(clock=lambda: NOW)
    items = foundation()
    result = factory.create_result(
        query, items, total_expected=4, logical_time=1.0,
    )
    assert result.total_expected == 4
    assert result.total_returned == 4
    assert result.logical_time == 1.0
    assert len(result) == 4 and tuple(result) == items
    assert not hasattr(query, "execute")
    with pytest.raises(QueryValidationError):
        factory.create_result(query, (object(),))


def test_result_target_status_total_and_duplicate_consistency():
    factory = QueryFactory(clock=lambda: NOW)
    knowledge = foundation()[0]
    query = factory.create(
        namespace="cko.queries", name="Documents", created_by="tester",
        targets=(QueryTarget.CANONICAL_DOCUMENT,),
    )
    with pytest.raises(QueryValidationError):
        factory.create_result(query, (knowledge,))
    all_query = canonical_models()[11]
    with pytest.raises(QueryValidationError):
        factory.create_result(all_query, (knowledge, knowledge))
    with pytest.raises(QueryValidationError):
        factory.create_result(all_query, (knowledge,), status=QueryStatus.EMPTY)
    empty = factory.create_result(
        all_query, status=QueryStatus.EMPTY, total_expected=0,
    )
    assert empty.total_returned == 0


def test_identity_metadata_constraints_and_expression_defenses():
    logical_id = QueryId.new()
    with pytest.raises(QueryIdentityError):
        QueryId("invalid")
    with pytest.raises(QueryIdentityError):
        QueryIdentity(logical_id, QueryId.new(), "cko", "name")
    assert QueryId.parse(str(logical_id)) == logical_id
    assert QueryId.canonical("cko", "key") == QueryId.canonical("cko", "key")
    with pytest.raises(QueryValidationError):
        QueryMetadata(NOW, NOW - timedelta(seconds=1), "tester")
    with pytest.raises(QueryValidationError):
        QueryConstraint(QueryOperator.AND, "value")
    with pytest.raises(QueryValidationError):
        QueryConstraint(QueryOperator.BETWEEN, 2, 1)
    with pytest.raises(QueryValidationError):
        QueryConstraint(QueryOperator.IN, ())
    with pytest.raises(QueryValidationError):
        QueryConstraint(QueryOperator.STARTS_WITH, 1)
    with pytest.raises(QueryValidationError):
        QueryExpression(QueryOperator.NOT, ())
    with pytest.raises(QueryValidationError):
        QueryExpression(QueryOperator.AND, (QueryFilter("author", QueryConstraint(QueryOperator.EQUAL, "x")),))


def test_deep_freeze_utc_and_finite_number_guarantees():
    local = datetime(2026, 7, 26, 17, 0, tzinfo=timezone(timedelta(hours=-3)))
    frozen = deep_freeze({"when": local, "nested": [1, {"ok": True}]})
    assert isinstance(frozen, MappingProxyType)
    assert frozen["when"] == NOW
    assert isinstance(frozen["nested"], tuple)
    assert finite_number(1, "value") == 1.0
    for invalid in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(QueryValidationError):
            deep_freeze(invalid)


def test_serialization_rejects_unknown_noncanonical_invalid_and_nonfinite_json():
    serializer = DeterministicQuerySerializer()
    value = canonical_models()[11]
    payload = serializer.serialize(value)
    invalid_payloads = (
        payload.replace(b"{", b'{"unknown":1,', 1),
        b'{"model":"unknown","schema_version":"1.0"}',
        b'{"value":NaN}', b" " + payload, b"\xff",
    )
    for invalid in invalid_payloads:
        with pytest.raises(QuerySerializationError):
            serializer.deserialize(invalid)
    with pytest.raises(QuerySerializationError):
        serializer.deserialize(1)
    with pytest.raises(QuerySerializationError):
        serializer.from_dict({})


def test_contract_defensive_paths_and_closed_schema():
    query_id = QueryId.new()
    assert text(None, "value", optional=True) is None
    assert instant(None, "value", optional=True) is None
    assert non_negative_int(None, "value", optional=True) is None
    assert primitive(QueryStatus.READY) == "ready"
    assert primitive(uuid4())
    assert model_sequence((query_id,), "ids", QueryId) == (query_id,)
    assert unique_texts(("a", "b"), "values") == ("a", "b")
    assert semantic_version("1.0.0") == "1.0.0"
    assert parse_instant(NOW.isoformat(), "when") == NOW
    assert strict(
        {"model": "x", "schema_version": "1.0", "value": 1},
        "x", {"value"},
    )["value"] == 1
    invalid_calls = (
        lambda: text(" ", "value"),
        lambda: instant(datetime.min, "value"),
        lambda: non_negative_int(True, "value"),
        lambda: finite_number("x", "value"),
        lambda: semantic_version("1"),
        lambda: model_sequence("x", "ids", QueryId),
        lambda: model_sequence((object(),), "ids", QueryId),
        lambda: unique_texts(("x", "x"), "values"),
        lambda: parse_instant(1, "when"),
        lambda: parse_instant("invalid", "when"),
        lambda: strict({}, "x", set()),
        lambda: strict({"model": "x", "schema_version": "2.0"}, "x", set()),
        lambda: QueryValidator().validate(object()),
    )
    for call in invalid_calls:
        with pytest.raises(CKOError):
            call()


def test_query_errors_are_core_errors_with_stable_payloads():
    error = QueryValidationError(
        "invalid", model="query_filter", details={"field": "author"},
    )
    assert isinstance(error, CKOError)
    assert error.to_dict() == {
        "code": "query_validation_error", "message": "invalid",
        "model": "query_filter", "details": {"field": "author"},
    }
    for call in (
        lambda: QueryError(""), lambda: QueryError("x", code=" "),
        lambda: QueryError("x", model=" "), lambda: QueryError("x", details=[]),
    ):
        with pytest.raises(ValueError):
            call()


def test_root_api_preserves_discovery_contracts_and_exports_query_aliases():
    import cko.core as core

    assert core.QueryFilter.__module__.startswith("cko.core.discovery")
    assert core.QueryOperator.__module__.startswith("cko.core.discovery")
    assert core.CanonicalQueryFilter is QueryFilter
    assert core.CanonicalQueryOperator is QueryOperator
    for name in (
        "CanonicalQuery", "QueryFactory", "DeterministicQuerySerializer",
        "QueryValidator", "QueryDescriptor", "QueryResult",
    ):
        assert name in core.__all__ and hasattr(core, name)


def test_remaining_model_and_validator_boundaries():
    factory = QueryFactory(clock=lambda: NOW)
    query = factory.create(
        namespace="cko.queries", name="Boundaries", created_by="tester",
        targets=(QueryTarget.KNOWLEDGE_OBJECT,),
    )
    with pytest.raises(QueryValidationError):
        QueryDescriptor(())
    with pytest.raises(QueryValidationError):
        QueryDescriptor((QueryTarget.KNOWLEDGE_OBJECT, QueryTarget.KNOWLEDGE_OBJECT))
    with pytest.raises(QueryValidationError):
        QueryFilter("unknown", QueryConstraint(QueryOperator.EQUAL, "x"))
    with pytest.raises(QueryValidationError):
        QueryFilter("attributes", QueryConstraint(QueryOperator.EQUAL, "x"))
    with pytest.raises(QueryValidationError):
        QueryStatistics(0, 1)
    with pytest.raises(QueryValidationError):
        QueryStatistics(None, 0, -1)
    with pytest.raises(QueryValidationError):
        factory.create_collection((query, query))
    with pytest.raises(QueryValidationError):
        factory.from_parts(
            identity=query.identity,
            metadata=replace(query.metadata, status=QueryStatus.COMPLETED),
            descriptor=query.descriptor,
        )


def test_serializer_detects_tampered_result_counts_and_scalar_types():
    serializer = DeterministicQuerySerializer()
    result = canonical_models()[13]
    payload = serializer.serialize(result)
    tampered = payload.replace(b'"total_returned":4', b'"total_returned":3', 1)
    with pytest.raises(QuerySerializationError):
        serializer.deserialize(tampered)
    scalar = b'{"__query_scalar__":"missing","value":"x"}'
    with pytest.raises(QuerySerializationError):
        serializer._value(__import__("json").loads(scalar))


def test_exhaustive_defensive_contract_and_model_paths():
    factory = QueryFactory(clock=lambda: NOW)
    constraint = factory.create_constraint(QueryOperator.EQUAL, "x")
    query = factory.create(
        namespace="cko.queries", name="Defensive", created_by="tester",
        targets=(QueryTarget.KNOWLEDGE_OBJECT,),
    )
    invalid_calls = (
        lambda: finite_number(True, "value"),
        lambda: unique_texts("x", "values"),
        lambda: deep_freeze(object()),
        lambda: primitive(float("nan")),
        lambda: primitive(object()),
        lambda: query_value_primitive(float("inf")),
        lambda: query_value_primitive(object()),
        lambda: strict([], "x", set()),
        lambda: strict({"model": "y", "schema_version": "1.0"}, "x", set()),
        lambda: QueryId.parse("invalid"),
        lambda: QueryIdentity(object(), object(), "cko", "x"),
        lambda: QueryMetadata(NOW, NOW, "x", status="invalid"),
        lambda: QueryMetadata(NOW, NOW, "x", attributes=[]),
        lambda: QueryConstraint("invalid", "x"),
        lambda: QueryConstraint(QueryOperator.EQUAL, object()),
        lambda: QueryConstraint(QueryOperator.BETWEEN, 1),
        lambda: QueryConstraint(QueryOperator.BETWEEN, 1, "2"),
        lambda: QueryConstraint(QueryOperator.BETWEEN, {"x": 1}, {"x": 2}),
        lambda: QueryConstraint(QueryOperator.EQUAL, "x", "y"),
        lambda: QueryFilter("author", object()),
        lambda: QueryFilter("created_at", constraint),
        lambda: QueryExpression(QueryOperator.EQUAL, (QueryFilter("author", constraint),)),
        lambda: QueryExpression(QueryOperator.NOT, "x"),
        lambda: QueryExpression(QueryOperator.NOT, (object(),)),
        lambda: QueryProjection((), 1, True),
        lambda: QueryDescriptor("x"),
        lambda: QueryDescriptor(("invalid",)),
        lambda: QueryDescriptor((QueryTarget.KNOWLEDGE_OBJECT,), expression=object()),
        lambda: QueryDescriptor((QueryTarget.KNOWLEDGE_OBJECT,), projection=object()),
        lambda: QueryDescriptor((QueryTarget.KNOWLEDGE_OBJECT,), pagination=object()),
        lambda: CanonicalQuery(object(), query.metadata, query.descriptor, _factory_token=_FACTORY_TOKEN),
        lambda: CanonicalQuery(query.identity, object(), query.descriptor, _factory_token=_FACTORY_TOKEN),
        lambda: CanonicalQuery(query.identity, query.metadata, object(), _factory_token=_FACTORY_TOKEN),
        lambda: QueryStatistics(metrics=[]),
        lambda: QueryResult(object(), _factory_token=_FACTORY_TOKEN),
        lambda: QueryResult(query, items="x", _factory_token=_FACTORY_TOKEN),
        lambda: QueryResult(query, logical_time=-1, _factory_token=_FACTORY_TOKEN),
        lambda: QueryResult(query, total_expected=0, total_returned=1, _factory_token=_FACTORY_TOKEN),
        lambda: QueryResult(query, statistics=object(), _factory_token=_FACTORY_TOKEN),
        lambda: QueryResult(query, total_expected=1, statistics=QueryStatistics(), _factory_token=_FACTORY_TOKEN),
        lambda: QueryResult(query, metadata=[], _factory_token=_FACTORY_TOKEN),
        lambda: QueryFactory(clock=lambda: (_ for _ in ()).throw(RuntimeError("clock"))).create(
            namespace="cko", name="x", created_by="x",
            targets=(QueryTarget.KNOWLEDGE_OBJECT,),
        ),
        lambda: _mapping([], "value"),
        lambda: _list({}, "value"),
    )
    for call in invalid_calls:
        with pytest.raises(CKOError):
            call()

    assert query_value_primitive(uuid4())["__query_scalar__"] == "uuid"
    assert query_value_primitive(QueryStatus.READY)["__query_scalar__"] == "enum"
    assert query_value_primitive(query.identity.logical_id)["model"] == "query_id"
    assert query_value_primitive({"x": [1]}) == {"x": [1]}
    serializer = DeterministicQuerySerializer()
    assert serializer._value([1, 2]) == (1, 2)
    assert isinstance(serializer._value({"__query_scalar__": "uuid", "value": str(uuid4())}), type(uuid4()))
    assert serializer._value({"__query_scalar__": "enum", "value": "ready"}) == "ready"
    assert serializer._value(query.identity.logical_id.to_dict()) == query.identity.logical_id
    with pytest.raises(QuerySerializationError):
        serializer._value({"__query_scalar__": "enum", "value": 1})
    with pytest.raises(QuerySerializationError):
        serializer._value({"model": "canonical_query"})
    with pytest.raises(QuerySerializationError):
        serializer._embedded({"model": "unsupported"})
    with pytest.raises(QuerySerializationError):
        serializer._embedded({})

    assert tuple(factory.create_collection((query,))) == (query,)
    assert len(factory.create_collection((query,))) == 1
    with pytest.raises(NotImplementedError):
        QuerySerializer.serialize(object(), query)
    with pytest.raises(NotImplementedError):
        QuerySerializer.deserialize(object(), b"{}")
    with pytest.raises(NotImplementedError):
        QuerySerializer.digest(object(), query)
    with pytest.raises(NotImplementedError):
        QueryValidatorContract.validate(object(), query)


def test_validator_nested_expression_and_cross_location_duplicates():
    factory = QueryFactory()
    first = factory.create_filter("author", QueryOperator.EQUAL, "Alice")
    second = factory.create_filter("status", QueryOperator.EQUAL, "active")
    nested = factory.create_expression(QueryOperator.NOT, (second,))
    expression = factory.create_expression(QueryOperator.AND, (first, nested))
    assert QueryValidator._flatten_filters(expression) == (first, second)
    with pytest.raises(QueryValidationError):
        factory.create_descriptor(
            targets=(QueryTarget.KNOWLEDGE_OBJECT,), filters=(first,),
            expression=factory.create_expression(QueryOperator.AND, (first, second)),
        )
    with pytest.raises(QueryValidationError):
        factory.create_descriptor(
            targets=(QueryTarget.KNOWLEDGE_OBJECT,),
            orderings=(factory.create_ordering("author", priority=0),
                       factory.create_ordering("author", priority=1)),
        )

    @dataclass
    class MutableQueryModel(QueryModel):
        schema_version: str = QUERY_SCHEMA_VERSION
        discriminator = "mutable_query_model"

    with pytest.raises(QueryValidationError):
        QueryValidator().validate(MutableQueryModel())
