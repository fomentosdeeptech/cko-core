"""Mandatory validated creation boundary for canonical graphs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable, Mapping
from uuid import UUID, uuid4

from cko.core.documents import CanonicalDocument
from cko.core.knowledge import KnowledgeObject
from cko.core.relationships import CanonicalRelationship

from .enums import (
    GraphConsistency, GraphNodeType, GraphSnapshotType, GraphStatus,
    GraphTraversalMode,
)
from .errors import GraphError, GraphFactoryError
from .identity import GraphId, GraphIdentity
from .metadata import GraphMetadata
from .models import (
    _FACTORY_TOKEN, CanonicalGraph, GraphCollection, GraphDescriptor, GraphEdge,
    GraphNode, GraphPath, GraphQuery, GraphResult, GraphSnapshot, GraphStatistics,
    GraphTraversal,
)
from .validator import GraphValidator


class GraphFactory:
    """Create graph values through one validation boundary."""

    def __init__(self, validator: GraphValidator | None = None,
                 clock: Callable[[], datetime] | None = None) -> None:
        self._validator = validator or GraphValidator()
        self._clock = clock or (lambda: datetime.now(UTC))

    def create_node(self, value: KnowledgeObject | CanonicalDocument,
                    node_id: GraphId | None = None) -> GraphNode:
        if isinstance(value, KnowledgeObject):
            node_type = GraphNodeType.KNOWLEDGE_OBJECT
        elif isinstance(value, CanonicalDocument):
            node_type = GraphNodeType.CANONICAL_DOCUMENT
        else:
            raise GraphFactoryError("node value must be KnowledgeObject or CanonicalDocument")
        selected_id = node_id or GraphId.canonical(
            value.identity.namespace,
            f"{node_type.value}:{value.identity.logical_id.value}",
        )
        node = GraphNode(selected_id, value, node_type)
        self._validator.validate(node)
        return node

    def create_edge(self, relationship: CanonicalRelationship,
                    edge_id: GraphId | None = None) -> GraphEdge:
        if not isinstance(relationship, CanonicalRelationship):
            raise GraphFactoryError("relationship must be CanonicalRelationship")
        selected_id = edge_id or GraphId.canonical(
            relationship.identity.namespace,
            f"canonical_relationship:{relationship.identity.logical_id.value}",
        )
        edge = GraphEdge(selected_id, relationship)
        self._validator.validate(edge)
        return edge

    def create(self, *, namespace: str, name: str, created_by: str,
               nodes: tuple[GraphNode | KnowledgeObject | CanonicalDocument, ...] = (),
               edges: tuple[GraphEdge | CanonicalRelationship, ...] = (),
               description: str | None = None,
               status: GraphStatus = GraphStatus.ACTIVE,
               category: str | None = None,
               attributes: Mapping[str, object] | None = None,
               version: str = "1.0.0",
               logical_id: GraphId | None = None) -> CanonicalGraph:
        try:
            selected_nodes = tuple(item if isinstance(item, GraphNode) else self.create_node(item)
                                   for item in nodes)
            selected_edges = tuple(item if isinstance(item, GraphEdge) else self.create_edge(item)
                                   for item in edges)
            selected_id = logical_id or GraphId.new()
            identity = GraphIdentity(
                selected_id, GraphId.canonical(namespace, f"{selected_id}:{name}"),
                namespace, name, version,
            )
            now = self._clock()
            metadata = GraphMetadata(now, now, created_by, status, category, attributes or {})
            descriptor = GraphDescriptor(name, description, status, GraphConsistency.CONSISTENT)
            return self.from_parts(identity=identity, metadata=metadata,
                                   descriptor=descriptor, nodes=selected_nodes,
                                   edges=selected_edges)
        except GraphError:
            raise
        except Exception as error:
            raise GraphFactoryError("canonical graph creation failed") from error

    def from_parts(self, *, identity: GraphIdentity, metadata: GraphMetadata,
                   descriptor: GraphDescriptor, nodes: tuple[GraphNode, ...] = (),
                   edges: tuple[GraphEdge, ...] = ()) -> CanonicalGraph:
        graph = CanonicalGraph(identity, metadata, descriptor, nodes, edges,
                               _factory_token=_FACTORY_TOKEN)
        self._validator.validate(graph)
        return graph

    def create_collection(self, graphs: tuple[CanonicalGraph, ...] = (),
                          name: str | None = None) -> GraphCollection:
        value = GraphCollection(graphs, name, _factory_token=_FACTORY_TOKEN)
        self._validator.validate(value)
        return value

    def create_path(self, node_ids: tuple[GraphId, ...],
                    edge_ids: tuple[GraphId, ...] = ()) -> GraphPath:
        value = GraphPath(node_ids, edge_ids); self._validator.validate(value); return value

    def create_traversal(self, start_node_id: GraphId, mode: GraphTraversalMode,
                         visited_node_ids: tuple[GraphId, ...],
                         traversed_edge_ids: tuple[GraphId, ...] = (),
                         paths: tuple[GraphPath, ...] = ()) -> GraphTraversal:
        value = GraphTraversal(start_node_id, mode, visited_node_ids,
                               traversed_edge_ids, paths)
        self._validator.validate(value); return value

    def create_snapshot(self, graph: CanonicalGraph,
                        snapshot_type: GraphSnapshotType = GraphSnapshotType.FULL,
                        version: str | None = None,
                        snapshot_id: UUID | None = None) -> GraphSnapshot:
        if not isinstance(graph, CanonicalGraph):
            raise GraphFactoryError("graph must be CanonicalGraph")
        from .serializer import DeterministicGraphSerializer
        value = GraphSnapshot(snapshot_id or uuid4(), graph, self._clock(),
                              DeterministicGraphSerializer(self).digest(graph),
                              snapshot_type, version or graph.identity.version)
        self._validator.validate(value); return value

    def create_statistics(self, graph: CanonicalGraph) -> GraphStatistics:
        from .navigation import GraphNavigation
        value = GraphNavigation(graph).statistics(); self._validator.validate(value); return value

    def create_query(self, **values) -> GraphQuery:
        value = GraphQuery(**values); self._validator.validate(value); return value

    def create_result(self, query: GraphQuery, nodes: tuple[GraphNode, ...],
                      edges: tuple[GraphEdge, ...] = (), total_nodes: int = 0,
                      total_edges: int = 0) -> GraphResult:
        value = GraphResult(query, nodes, edges, total_nodes, total_edges)
        self._validator.validate(value); return value


__all__ = ["GraphFactory"]
