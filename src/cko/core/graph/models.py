"""Canonical immutable graph models and aggregates."""

from __future__ import annotations

from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from cko.core.documents import CanonicalDocument
from cko.core.knowledge import KnowledgeObject
from cko.core.relationships import CanonicalRelationship

from .contracts import (
    GRAPH_SCHEMA_VERSION, GraphModel, finite_number, instant, model_sequence,
    non_negative_int, semantic_version, text, unique_texts,
)
from .enums import (
    GraphConsistency, GraphEdgeType, GraphNodeType, GraphSnapshotType,
    GraphStatus, GraphTraversalMode,
)
from .errors import GraphFactoryError, GraphValidationError
from .identity import GraphId, GraphIdentity
from .metadata import GraphMetadata


_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True)
class GraphNode(GraphModel):
    node_id: GraphId
    value: KnowledgeObject | CanonicalDocument
    node_type: GraphNodeType
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_node"

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, GraphId):
            raise GraphValidationError("node_id must be GraphId")
        try:
            object.__setattr__(self, "node_type", GraphNodeType(self.node_type))
        except (TypeError, ValueError) as error:
            raise GraphValidationError("node_type must be GraphNodeType") from error
        expected = (KnowledgeObject if self.node_type is GraphNodeType.KNOWLEDGE_OBJECT
                    else CanonicalDocument)
        if not isinstance(self.value, expected):
            raise GraphValidationError("node value does not match node_type")
        self._validate_schema()

    @property
    def payload(self) -> KnowledgeObject | CanonicalDocument:
        return self.value


@dataclass(frozen=True, slots=True)
class GraphEdge(GraphModel):
    edge_id: GraphId
    relationship: CanonicalRelationship
    edge_type: GraphEdgeType = GraphEdgeType.CANONICAL_RELATIONSHIP
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_edge"

    def __post_init__(self) -> None:
        if not isinstance(self.edge_id, GraphId):
            raise GraphValidationError("edge_id must be GraphId")
        if not isinstance(self.relationship, CanonicalRelationship):
            raise GraphValidationError("relationship must be CanonicalRelationship")
        try:
            object.__setattr__(self, "edge_type", GraphEdgeType(self.edge_type))
        except (TypeError, ValueError) as error:
            raise GraphValidationError("edge_type must be GraphEdgeType") from error
        self._validate_schema()

    @property
    def value(self) -> CanonicalRelationship:
        return self.relationship


@dataclass(frozen=True, slots=True)
class GraphPath(GraphModel):
    node_ids: tuple[GraphId, ...]
    edge_ids: tuple[GraphId, ...] = ()
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_path"

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_ids", model_sequence(self.node_ids, "node_ids", GraphId))
        object.__setattr__(self, "edge_ids", model_sequence(self.edge_ids, "edge_ids", GraphId))
        if not self.node_ids:
            raise GraphValidationError("path must contain at least one node")
        if len(self.edge_ids) != len(self.node_ids) - 1:
            raise GraphValidationError("path edge count must connect every consecutive node")
        if len(self.node_ids) != len(set(self.node_ids)):
            raise GraphValidationError("path must be simple")
        self._validate_schema()

    @property
    def length(self) -> int:
        return len(self.edge_ids)


@dataclass(frozen=True, slots=True)
class GraphTraversal(GraphModel):
    start_node_id: GraphId
    mode: GraphTraversalMode
    visited_node_ids: tuple[GraphId, ...]
    traversed_edge_ids: tuple[GraphId, ...] = ()
    paths: tuple[GraphPath, ...] = ()
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_traversal"

    def __post_init__(self) -> None:
        if not isinstance(self.start_node_id, GraphId):
            raise GraphValidationError("start_node_id must be GraphId")
        try:
            object.__setattr__(self, "mode", GraphTraversalMode(self.mode))
        except (TypeError, ValueError) as error:
            raise GraphValidationError("mode must be GraphTraversalMode") from error
        object.__setattr__(self, "visited_node_ids", model_sequence(self.visited_node_ids, "visited_node_ids", GraphId))
        object.__setattr__(self, "traversed_edge_ids", model_sequence(self.traversed_edge_ids, "traversed_edge_ids", GraphId))
        object.__setattr__(self, "paths", model_sequence(self.paths, "paths", GraphPath))
        if not self.visited_node_ids or self.visited_node_ids[0] != self.start_node_id:
            raise GraphValidationError("traversal must begin at start_node_id")
        if len(self.visited_node_ids) != len(set(self.visited_node_ids)):
            raise GraphValidationError("visited_node_ids must be unique")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class GraphStatistics(GraphModel):
    node_count: int
    edge_count: int
    density: float
    average_degree: float
    components: int
    depth: int
    width: int
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_statistics"

    def __post_init__(self) -> None:
        for name in ("node_count", "edge_count", "components", "depth", "width"):
            object.__setattr__(self, name, non_negative_int(getattr(self, name), name))
        object.__setattr__(self, "density", finite_number(self.density, "density"))
        object.__setattr__(self, "average_degree", finite_number(self.average_degree, "average_degree"))
        if not 0.0 <= self.density <= 1.0:
            raise GraphValidationError("density must be between zero and one")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class GraphDescriptor(GraphModel):
    name: str
    description: str | None = None
    status: GraphStatus = GraphStatus.ACTIVE
    consistency: GraphConsistency = GraphConsistency.CONSISTENT
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_descriptor"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", text(self.name, "name"))
        object.__setattr__(self, "description", text(self.description, "description", optional=True))
        try:
            object.__setattr__(self, "status", GraphStatus(self.status))
            object.__setattr__(self, "consistency", GraphConsistency(self.consistency))
        except (TypeError, ValueError) as error:
            raise GraphValidationError("invalid graph descriptor enum") from error
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class CanonicalGraph(GraphModel):
    identity: GraphIdentity
    metadata: GraphMetadata
    descriptor: GraphDescriptor
    nodes: tuple[GraphNode, ...] = ()
    edges: tuple[GraphEdge, ...] = ()
    schema_version: str = GRAPH_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "canonical_graph"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise GraphFactoryError("CanonicalGraph must be created by GraphFactory")
        if not isinstance(self.identity, GraphIdentity) or not isinstance(self.metadata, GraphMetadata) or not isinstance(self.descriptor, GraphDescriptor):
            raise GraphValidationError("canonical graph contains an invalid required model")
        object.__setattr__(self, "nodes", model_sequence(self.nodes, "nodes", GraphNode))
        object.__setattr__(self, "edges", model_sequence(self.edges, "edges", GraphEdge))
        self._validate_schema()

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self) -> int:
        return len(self.nodes)


@dataclass(frozen=True, slots=True)
class GraphSnapshot(GraphModel):
    snapshot_id: UUID
    graph: CanonicalGraph
    captured_at: datetime
    digest: str
    snapshot_type: GraphSnapshotType = GraphSnapshotType.FULL
    version: str = "1.0.0"
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_snapshot"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "snapshot_id", self.snapshot_id if isinstance(self.snapshot_id, UUID) else UUID(str(self.snapshot_id)))
        except (TypeError, ValueError, AttributeError) as error:
            raise GraphValidationError("snapshot_id must be UUID") from error
        if not isinstance(self.graph, CanonicalGraph):
            raise GraphValidationError("graph must be CanonicalGraph")
        object.__setattr__(self, "captured_at", instant(self.captured_at, "captured_at"))
        normalized_digest = text(self.digest, "digest")
        if len(normalized_digest) != 64 or any(c not in "0123456789abcdef" for c in normalized_digest):
            raise GraphValidationError("digest must be a lowercase SHA-256 hash")
        object.__setattr__(self, "digest", normalized_digest)
        try:
            object.__setattr__(self, "snapshot_type", GraphSnapshotType(self.snapshot_type))
        except (TypeError, ValueError) as error:
            raise GraphValidationError("snapshot_type must be GraphSnapshotType") from error
        object.__setattr__(self, "version", semantic_version(self.version))
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class GraphCollection(GraphModel):
    graphs: tuple[CanonicalGraph, ...] = ()
    name: str | None = None
    schema_version: str = GRAPH_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    discriminator: ClassVar[str] = "graph_collection"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise GraphFactoryError("GraphCollection must be created by GraphFactory")
        object.__setattr__(self, "graphs", model_sequence(self.graphs, "graphs", CanonicalGraph))
        object.__setattr__(self, "name", text(self.name, "name", optional=True))
        self._validate_schema()

    def __iter__(self): return iter(self.graphs)
    def __len__(self) -> int: return len(self.graphs)


@dataclass(frozen=True, slots=True)
class GraphQuery(GraphModel):
    node_ids: tuple[GraphId, ...] = ()
    namespaces: tuple[str, ...] = ()
    node_types: tuple[GraphNodeType, ...] = ()
    authors: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    versions: tuple[str, ...] = ()
    limit: int = 100
    offset: int = 0
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_query"

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_ids", model_sequence(self.node_ids, "node_ids", GraphId))
        for name in ("namespaces", "authors", "categories", "statuses", "versions"):
            object.__setattr__(self, name, unique_texts(getattr(self, name), name))
        try:
            object.__setattr__(self, "node_types", tuple(GraphNodeType(item) for item in self.node_types))
        except (TypeError, ValueError) as error:
            raise GraphValidationError("node_types contains an invalid enum") from error
        object.__setattr__(self, "limit", non_negative_int(self.limit, "limit"))
        object.__setattr__(self, "offset", non_negative_int(self.offset, "offset"))
        if self.limit == 0:
            raise GraphValidationError("limit must be greater than zero")
        self._validate_schema()


@dataclass(frozen=True, slots=True)
class GraphResult(GraphModel):
    query: GraphQuery
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...] = ()
    total_nodes: int = 0
    total_edges: int = 0
    schema_version: str = GRAPH_SCHEMA_VERSION
    discriminator: ClassVar[str] = "graph_result"

    def __post_init__(self) -> None:
        if not isinstance(self.query, GraphQuery):
            raise GraphValidationError("query must be GraphQuery")
        object.__setattr__(self, "nodes", model_sequence(self.nodes, "nodes", GraphNode))
        object.__setattr__(self, "edges", model_sequence(self.edges, "edges", GraphEdge))
        object.__setattr__(self, "total_nodes", non_negative_int(self.total_nodes, "total_nodes"))
        object.__setattr__(self, "total_edges", non_negative_int(self.total_edges, "total_edges"))
        if self.total_nodes < len(self.nodes) or self.total_edges < len(self.edges):
            raise GraphValidationError("result totals cannot be smaller than result values")
        self._validate_schema()


__all__ = [
    "CanonicalGraph", "GraphCollection", "GraphDescriptor", "GraphEdge", "GraphNode",
    "GraphPath", "GraphQuery", "GraphResult", "GraphSnapshot", "GraphStatistics",
    "GraphTraversal", "_FACTORY_TOKEN",
]
