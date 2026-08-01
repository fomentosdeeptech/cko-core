"""Dedicated acceptance and defensive suite for SPR-013."""

from dataclasses import FrozenInstanceError, is_dataclass, replace
from datetime import UTC, datetime, timedelta
from types import MappingProxyType
from uuid import uuid4

import pytest

from cko.core import (
    CKOError, GRAPH_SCHEMA_VERSION, CanonicalGraph, DeterministicGraphSerializer,
    GraphCollection, GraphConsistency, GraphDescriptor, GraphEdge, GraphEdgeType,
    GraphError, GraphFactory, GraphFactoryError, GraphId, GraphIdentity,
    GraphIdentityError, GraphIndexes, GraphMetadata, GraphNavigation,
    GraphNavigationError, GraphNode, GraphNodeType, GraphPath, GraphQuery,
    GraphResult, GraphSerializationError, GraphSnapshot, GraphSnapshotType,
    GraphStatistics, GraphStatus, GraphTraversal, GraphTraversalMode,
    GraphValidationError, GraphValidator,
)
from cko.core.documents import (
    DocumentDescriptor, DocumentFactory, DocumentMetadata, DocumentSource,
    DocumentSourceType, DocumentType,
)
from cko.core.graph.contracts import deep_freeze, primitive, strict
from cko.core.graph.contracts import (
    finite_number, instant, model_sequence, non_negative_int, parse_instant,
    semantic_version, text, unique_texts,
)
from cko.core.knowledge import (
    KnowledgeCategory, KnowledgeContent, KnowledgeMetadata, KnowledgeObjectFactory,
    KnowledgeType,
)
from cko.core.relationships import (
    RelationshipDirection, RelationshipDirectionType, RelationshipEndpoint,
    RelationshipFactory, RelationshipType,
)


NOW = datetime(2026, 7, 26, 20, 0, tzinfo=UTC)


def foundation():
    knowledge_factory = KnowledgeObjectFactory(clock=lambda: NOW)
    first = knowledge_factory.create(
        namespace="cko.science", origin="curation", knowledge_type=KnowledgeType.CONCEPT,
        metadata=KnowledgeMetadata(NOW, NOW, author="Alice", domain="science",
                                   category=KnowledgeCategory.SCIENTIFIC),
        content=KnowledgeContent.empty(), created_by="tester",
    )
    second = knowledge_factory.create(
        namespace="cko.science", origin="curation", knowledge_type=KnowledgeType.CONCEPT,
        metadata=KnowledgeMetadata(NOW, NOW, author="Bob"),
        content=KnowledgeContent.empty(), created_by="tester",
    )
    document = DocumentFactory(clock=lambda: NOW).create(
        namespace="cko.documents",
        metadata=DocumentMetadata("Canonical", NOW, NOW, creator="Alice",
                                  category="reference",
                                  sources=(DocumentSource(DocumentSourceType.INTERNAL,
                                                          "source:canonical", "test"),)),
        descriptor=DocumentDescriptor(DocumentType.ARTICLE), created_by="tester",
    )
    relationship_factory = RelationshipFactory(clock=lambda: NOW)
    first_edge = relationship_factory.create(
        namespace="cko.graph", source=RelationshipEndpoint.from_knowledge_object(first),
        target=RelationshipEndpoint.from_knowledge_object(second),
        relationship_type=RelationshipType.RELATED_TO, created_by="tester",
    )
    second_edge = relationship_factory.create(
        namespace="cko.graph", source=RelationshipEndpoint.from_knowledge_object(second),
        target=RelationshipEndpoint.from_document(document),
        relationship_type=RelationshipType.REFERENCES, created_by="tester",
        direction=RelationshipDirection(RelationshipDirectionType.BIDIRECTIONAL),
    )
    factory = GraphFactory(clock=lambda: NOW)
    graph = factory.create(
        namespace="cko.graphs", name="Foundation", created_by="tester",
        description="Structural graph", category="knowledge",
        attributes={"labels": ["canonical"]},
        nodes=(first, second, document), edges=(first_edge, second_edge),
    )
    return factory, graph, first, second, document, first_edge, second_edge


def graph_models():
    factory, graph, *_ = foundation()
    navigation = GraphNavigation(graph)
    path = navigation.list_paths(graph.nodes[0].node_id, graph.nodes[2].node_id)[0]
    traversal = navigation.traverse(graph.nodes[0].node_id)
    statistics = navigation.statistics()
    query = GraphQuery(authors=("Alice",), limit=10)
    result = GraphIndexes.build(graph).execute(graph, query)
    snapshot = factory.create_snapshot(graph)
    collection = factory.create_collection((graph,), "canonical")
    return (
        graph.identity.logical_id, graph.identity, graph.metadata, graph.nodes[0],
        graph.edges[0], path, traversal, snapshot, statistics, graph.descriptor,
        graph, collection, query, result,
    )


def test_required_models_are_frozen_slotted_versioned_and_discriminated():
    for value in graph_models():
        assert is_dataclass(value)
        assert type(value).__dataclass_params__.frozen
        assert hasattr(type(value), "__slots__")
        assert value.schema_version == GRAPH_SCHEMA_VERSION
        assert value.model == type(value).discriminator
        with pytest.raises((FrozenInstanceError, AttributeError)):
            value.schema_version = "2.0"


def test_all_models_round_trip_as_strict_deterministic_utf8_json():
    serializer = DeterministicGraphSerializer()
    for value in graph_models():
        payload = serializer.serialize(value)
        assert payload == serializer.serialize(value)
        assert serializer.deserialize(payload) == value
        assert b"NaN" not in payload and b"Infinity" not in payload
        assert len(serializer.digest(value)) == 64


def test_factory_is_mandatory_for_aggregates_and_supports_empty_graphs():
    factory, graph, *_ = foundation()
    with pytest.raises(GraphFactoryError):
        CanonicalGraph(graph.identity, graph.metadata, graph.descriptor)
    with pytest.raises(GraphFactoryError):
        GraphCollection((graph,))
    empty = factory.create(namespace="cko.empty", name="Empty", created_by="tester")
    assert len(empty) == 0
    assert factory.create_statistics(empty) == GraphStatistics(0, 0, 0.0, 0.0, 0, 0, 0)
    GraphValidator().validate(empty)


def test_nodes_and_edges_only_encapsulate_homologated_models():
    factory, graph, first, _, document, first_edge, _ = foundation()
    assert factory.create_node(first).node_type is GraphNodeType.KNOWLEDGE_OBJECT
    assert factory.create_node(document).node_type is GraphNodeType.CANONICAL_DOCUMENT
    assert factory.create_edge(first_edge).edge_type is GraphEdgeType.CANONICAL_RELATIONSHIP
    assert graph.nodes[0].payload is first
    assert graph.edges[0].value is first_edge
    with pytest.raises(GraphFactoryError):
        factory.create_node(object())
    with pytest.raises(GraphFactoryError):
        factory.create_edge(object())
    with pytest.raises(GraphValidationError):
        GraphNode(GraphId.new(), first, GraphNodeType.CANONICAL_DOCUMENT)
    with pytest.raises(GraphValidationError):
        GraphEdge(GraphId.new(), object())


def test_navigation_is_complete_structural_and_deterministic():
    _, graph, *_ = foundation(); nav = GraphNavigation(graph)
    first, second, third = (node.node_id for node in graph.nodes)
    assert nav.get_node(first) == graph.nodes[0]
    assert nav.get_edges() == tuple(sorted(graph.edges, key=lambda edge: str(edge.edge_id)))
    assert nav.degree(second) == 2
    assert tuple(node.node_id for node in nav.neighbors(second)) == tuple(sorted((first, third), key=str))
    assert len(nav.incoming(second)) == 2
    assert len(nav.outgoing(second)) == 1
    paths = nav.list_paths(first, third)
    assert len(paths) == 1 and paths[0].length == 2
    assert nav.connected_components() == (tuple(sorted((first, second, third), key=str)),)
    assert nav.maximum_depth() == 2
    assert nav.width() == 2
    breadth = nav.traverse(first, GraphTraversalMode.BREADTH_FIRST)
    depth = nav.traverse(first, GraphTraversalMode.DEPTH_FIRST)
    assert breadth.visited_node_ids[0] == first
    assert depth.visited_node_ids[0] == first
    statistics = nav.statistics()
    assert (statistics.node_count, statistics.edge_count, statistics.components,
            statistics.depth, statistics.width) == (3, 2, 1, 2, 2)
    assert statistics.density == pytest.approx(1 / 3)
    assert statistics.average_degree == pytest.approx(4 / 3)


def test_indexes_cover_every_required_dimension_and_execute_queries():
    _, graph, *_ = foundation(); indexes = GraphIndexes.build(graph)
    first = graph.nodes[0]
    assert indexes.lookup("identity", first.node_id) == (first.node_id,)
    assert first.node_id in indexes.lookup("namespace", "cko.science")
    assert first.node_id in indexes.lookup("type", GraphNodeType.KNOWLEDGE_OBJECT)
    assert first.node_id in indexes.lookup("author", "Alice")
    assert first.node_id in indexes.lookup("category", KnowledgeCategory.SCIENTIFIC)
    assert first.node_id in indexes.lookup("status", "active")
    assert first.node_id in indexes.lookup("version", "1.0.0")
    result = indexes.execute(graph, GraphQuery(authors=("Alice",)))
    assert result.total_nodes == 1 and result.nodes == (first,)
    assert isinstance(indexes.identity, MappingProxyType)
    with pytest.raises(GraphError):
        indexes.lookup("missing", "x")


def test_snapshots_are_versioned_immutable_and_integrity_checked():
    factory, graph, *_ = foundation(); serializer = DeterministicGraphSerializer()
    snapshot = factory.create_snapshot(graph, GraphSnapshotType.STRUCTURAL)
    assert snapshot.version == graph.identity.version
    assert snapshot.digest == serializer.digest(graph)
    assert serializer.deserialize(serializer.serialize(snapshot)) == snapshot
    invalid = replace(snapshot, digest="0" * 64)
    with pytest.raises(GraphSerializationError):
        serializer.deserialize(serializer.serialize(invalid))


def test_validator_rejects_duplicates_and_broken_cross_references():
    factory, graph, first, second, _, first_edge, _ = foundation()
    with pytest.raises(GraphValidationError):
        factory.from_parts(identity=graph.identity, metadata=graph.metadata,
                           descriptor=graph.descriptor, nodes=(graph.nodes[0], graph.nodes[0]))
    with pytest.raises(GraphValidationError):
        factory.from_parts(identity=graph.identity, metadata=graph.metadata,
                           descriptor=graph.descriptor, nodes=graph.nodes,
                           edges=(graph.edges[0], graph.edges[0]))
    other = KnowledgeObjectFactory(clock=lambda: NOW).create(
        namespace="cko.outside", origin="test", knowledge_type=KnowledgeType.CONCEPT,
        metadata=KnowledgeMetadata(NOW, NOW), content=KnowledgeContent.empty(),
        created_by="tester",
    )
    broken = RelationshipFactory(clock=lambda: NOW).create(
        namespace="cko.graph", source=RelationshipEndpoint.from_knowledge_object(first),
        target=RelationshipEndpoint.from_knowledge_object(other),
        relationship_type=RelationshipType.RELATED_TO, created_by="tester",
    )
    with pytest.raises(GraphValidationError):
        factory.create(namespace="cko.graphs", name="Broken", created_by="tester",
                       nodes=(first, second), edges=(broken,))


def test_identity_metadata_descriptor_and_query_defenses():
    logical = GraphId.new()
    with pytest.raises(GraphIdentityError): GraphId("bad")
    with pytest.raises(GraphValidationError): GraphId.canonical("cko", object())
    with pytest.raises(GraphIdentityError): GraphIdentity(logical, GraphId.new(), "cko", "x")
    with pytest.raises(GraphValidationError): GraphMetadata(NOW, NOW - timedelta(seconds=1), "u")
    with pytest.raises(GraphValidationError): GraphMetadata(NOW, NOW, "u", attributes=[])
    with pytest.raises(GraphValidationError): GraphDescriptor("x", status="invalid")
    with pytest.raises(GraphValidationError): GraphQuery(limit=0)
    with pytest.raises(GraphValidationError): GraphQuery(offset=-1)
    with pytest.raises(GraphValidationError): GraphQuery(authors=("x", "x"))
    with pytest.raises(GraphValidationError): GraphPath(())
    with pytest.raises(GraphValidationError): GraphPath((GraphId.new(), GraphId.new()), ())
    with pytest.raises(GraphValidationError): GraphStatistics(1, 0, float("nan"), 0, 1, 0, 1)


def test_serialization_rejects_unknown_noncanonical_invalid_and_nonfinite_json():
    serializer = DeterministicGraphSerializer(); value = graph_models()[0]
    payload = serializer.serialize(value)
    for invalid in (
        payload.replace(b"{", b'{"unknown":1,', 1),
        b'{"model":"unknown","schema_version":"1.0"}',
        b'{"value":NaN}', b" " + payload, b"\xff",
    ):
        with pytest.raises(GraphSerializationError):
            serializer.deserialize(invalid)


def test_contract_and_service_defensive_paths():
    _, graph, *_ = foundation(); nav = GraphNavigation(graph)
    frozen = deep_freeze({"items": [1, {"x": True}]})
    assert isinstance(frozen, MappingProxyType)
    assert primitive(NOW).endswith("+00:00")
    assert strict({"model": "x", "schema_version": "1.0", "value": 1}, "x", {"value"})["value"] == 1
    for call in (
        lambda: deep_freeze(float("inf")), lambda: deep_freeze(object()),
        lambda: primitive(object()), lambda: strict([], "x", set()),
        lambda: GraphValidator().validate(object()), lambda: GraphNavigation(object()),
        lambda: nav.get_node(GraphId.new()), lambda: nav.list_paths(graph.nodes[0].node_id, graph.nodes[1].node_id, -1),
    ):
        with pytest.raises(CKOError):
            call()
    error = GraphValidationError("invalid", model="graph", details={"field": "nodes"})
    assert isinstance(error, CKOError)
    assert error.to_dict()["details"] == {"field": "nodes"}
    with pytest.raises(ValueError): GraphValidationError("")


def test_root_api_exports_graph_foundation():
    import cko.core as core
    for name in ("CanonicalGraph", "GraphFactory", "GraphNavigation", "GraphIndexes",
                 "DeterministicGraphSerializer", "GraphValidator"):
        assert name in core.__all__ and hasattr(core, name)


def test_remaining_contract_model_and_error_boundaries():
    factory, graph, *_ = foundation(); node = graph.nodes[0]; edge = graph.edges[0]
    assert text(None, "x", optional=True) is None
    assert instant(None, "x", optional=True) is None
    assert finite_number(1, "x") == 1.0
    assert primitive(GraphStatus.ACTIVE) == "active"
    assert primitive(uuid4())
    assert primitive({"b": 2, "a": [1]}) == {"a": [1], "b": 2}
    assert tuple(factory.create_collection((graph,))) == (graph,)
    assert len(factory.create_collection((graph,))) == 1
    for call in (
        lambda: text(" ", "x"), lambda: semantic_version("1", "x"),
        lambda: instant(datetime.min, "x"), lambda: parse_instant(1, "x"),
        lambda: parse_instant("invalid", "x"), lambda: non_negative_int(True, "x"),
        lambda: finite_number("x", "x"), lambda: model_sequence("x", "x", GraphId),
        lambda: model_sequence((object(),), "x", GraphId),
        lambda: unique_texts("x", "x"), lambda: strict({}, "x", set()),
        lambda: strict({"model": "x", "schema_version": "2.0"}, "x", set()),
        lambda: GraphNode(object(), node.value, node.node_type),
        lambda: GraphNode(node.node_id, node.value, "invalid"),
        lambda: GraphEdge(object(), edge.relationship),
        lambda: GraphEdge(edge.edge_id, edge.relationship, "invalid"),
        lambda: GraphTraversal(object(), GraphTraversalMode.BREADTH_FIRST, (node.node_id,)),
        lambda: GraphTraversal(node.node_id, "invalid", (node.node_id,)),
        lambda: GraphTraversal(node.node_id, GraphTraversalMode.BREADTH_FIRST, (edge.edge_id,)),
        lambda: GraphTraversal(node.node_id, GraphTraversalMode.BREADTH_FIRST, (node.node_id, node.node_id)),
        lambda: GraphStatistics(1, 0, 2.0, 0.0, 1, 0, 1),
        lambda: GraphQuery(node_types=("invalid",)),
        lambda: GraphResult(object(), (), (), 0, 0),
        lambda: GraphResult(GraphQuery(), (node,), (), 0, 0),
    ):
        with pytest.raises(CKOError):
            call()
    for call in (
        lambda: GraphValidationError("x", code=" "),
        lambda: GraphValidationError("x", model=" "),
        lambda: GraphValidationError("x", details=[]),
    ):
        with pytest.raises(ValueError):
            call()


def test_remaining_factory_serializer_validator_and_navigation_boundaries():
    factory, graph, *_ = foundation(); serializer = DeterministicGraphSerializer()
    node_ids = tuple(node.node_id for node in graph.nodes)
    edge_ids = tuple(edge.edge_id for edge in graph.edges)
    assert factory.create_path(node_ids[:2], edge_ids[:1]).length == 1
    assert factory.create_traversal(node_ids[0], GraphTraversalMode.BREADTH_FIRST,
                                    node_ids[:1]).start_node_id == node_ids[0]
    assert factory.create_query(authors=("Alice",)).authors == ("Alice",)
    assert factory.create_result(GraphQuery(), (), (), 0, 0).total_nodes == 0
    with pytest.raises(GraphValidationError):
        factory.from_parts(identity=graph.identity, metadata=graph.metadata,
                           descriptor=replace(graph.descriptor, status=GraphStatus.ARCHIVED))
    with pytest.raises(GraphValidationError):
        factory.from_parts(identity=graph.identity, metadata=graph.metadata,
                           descriptor=replace(graph.descriptor,
                                              consistency=GraphConsistency.INCONSISTENT))
    with pytest.raises(GraphValidationError):
        factory.create_collection((graph, graph))
    with pytest.raises(GraphSerializationError): serializer.from_dict({})
    with pytest.raises(GraphSerializationError): serializer.deserialize(1)
    with pytest.raises(GraphSerializationError):
        serializer.from_dict({"model": "graph_node", "schema_version": "1.0",
                              "node_id": node_ids[0].to_dict(), "node_type": "knowledge_object",
                              "value": {"model": "unsupported"}})
    disconnected = factory.create(namespace="cko.graphs", name="Disconnected",
                                  created_by="tester", nodes=(graph.nodes[0].value,))
    nav = GraphNavigation(disconnected)
    assert nav.get_edges() == () and nav.incoming(disconnected.nodes[0].node_id) == ()
    assert nav.outgoing(disconnected.nodes[0].node_id) == ()
