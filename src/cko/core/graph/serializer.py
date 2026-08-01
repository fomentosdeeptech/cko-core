"""Strict deterministic UTF-8 JSON serialization for graph models."""

from __future__ import annotations

import hashlib
import json
from typing import Mapping
from uuid import UUID

from cko.core.documents import DeterministicDocumentSerializer
from cko.core.knowledge import DeterministicKnowledgeSerializer
from cko.core.relationships import DeterministicRelationshipSerializer

from .contracts import GraphModel, parse_instant, strict
from .enums import (
    GraphConsistency, GraphEdgeType, GraphNodeType, GraphSnapshotType,
    GraphStatus, GraphTraversalMode,
)
from .errors import GraphError, GraphSerializationError
from .factory import GraphFactory
from .identity import GraphId, GraphIdentity
from .metadata import GraphMetadata
from .models import (
    CanonicalGraph, GraphCollection, GraphDescriptor, GraphEdge, GraphNode,
    GraphPath, GraphQuery, GraphResult, GraphSnapshot, GraphStatistics,
    GraphTraversal,
)
from .validator import GraphValidator


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise GraphSerializationError(f"{name} must be an object")
    return value


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise GraphSerializationError(f"{name} must be an array")
    return value


class DeterministicGraphSerializer:
    """Serialize and restore closed canonical graph envelopes."""

    def __init__(self, factory: GraphFactory | None = None,
                 validator: GraphValidator | None = None) -> None:
        self._validator = validator or GraphValidator()
        self._factory = factory or GraphFactory(self._validator)
        self._knowledge = DeterministicKnowledgeSerializer()
        self._documents = DeterministicDocumentSerializer()
        self._relationships = DeterministicRelationshipSerializer()

    def serialize(self, value: GraphModel) -> bytes:
        self._validator.validate(value)
        try:
            return json.dumps(value.to_dict(), ensure_ascii=False, allow_nan=False,
                              sort_keys=True, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError, UnicodeError) as error:
            raise GraphSerializationError("graph serialization failed") from error

    def deserialize(self, payload: bytes | str) -> GraphModel:
        try:
            encoded = payload.decode("utf-8") if isinstance(payload, bytes) else payload
            if not isinstance(encoded, str):
                raise TypeError
            decoded = json.loads(encoded, parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
        except (TypeError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
            raise GraphSerializationError("payload must be strict UTF-8 JSON") from error
        try:
            value = self.from_dict(_mapping(decoded, "payload"))
        except GraphSerializationError:
            raise
        except (GraphError, TypeError, ValueError, KeyError, AttributeError) as error:
            raise GraphSerializationError("payload violates the graph schema") from error
        if self.serialize(value).decode("utf-8") != encoded:
            raise GraphSerializationError("payload is not canonical JSON")
        return value

    def digest(self, value: GraphModel) -> str:
        return hashlib.sha256(self.serialize(value)).hexdigest()

    def _embedded(self, payload: object) -> object:
        value = _mapping(payload, "embedded model")
        model = value.get("model")
        if not isinstance(model, str):
            raise GraphSerializationError("embedded model discriminator is required")
        if model.startswith("knowledge_"):
            return self._knowledge.from_dict(value)
        if model.startswith("document_") or model == "canonical_document":
            return self._documents.from_dict(value)
        if model.startswith("relationship_") or model == "canonical_relationship":
            return self._relationships.from_dict(value)
        raise GraphSerializationError("unsupported embedded canonical model")

    def from_dict(self, payload: Mapping[str, object]) -> GraphModel:
        model = payload.get("model")
        if not isinstance(model, str):
            raise GraphSerializationError("model discriminator is required")
        nested = lambda item: self.from_dict(_mapping(item, "nested graph model"))

        if model == "graph_id":
            p = strict(payload, model, {"value"}); return GraphId.parse(p["value"])  # type: ignore[arg-type]
        if model == "graph_identity":
            p = strict(payload, model, {"logical_id", "canonical_id", "namespace", "name", "version"})
            return GraphIdentity(nested(p["logical_id"]), nested(p["canonical_id"]), p["namespace"], p["name"], p["version"])  # type: ignore[arg-type]
        if model == "graph_metadata":
            p = strict(payload, model, {"created_at", "modified_at", "created_by", "status", "category", "attributes"})
            return GraphMetadata(parse_instant(p["created_at"], "created_at"), parse_instant(p["modified_at"], "modified_at"), p["created_by"], GraphStatus(p["status"]), p["category"], _mapping(p["attributes"], "attributes"))  # type: ignore[arg-type]
        if model == "graph_node":
            p = strict(payload, model, {"node_id", "value", "node_type"})
            return GraphNode(nested(p["node_id"]), self._embedded(p["value"]), GraphNodeType(p["node_type"]))  # type: ignore[arg-type]
        if model == "graph_edge":
            p = strict(payload, model, {"edge_id", "relationship", "edge_type"})
            return GraphEdge(nested(p["edge_id"]), self._embedded(p["relationship"]), GraphEdgeType(p["edge_type"]))  # type: ignore[arg-type]
        if model == "graph_path":
            p = strict(payload, model, {"node_ids", "edge_ids"})
            return GraphPath(tuple(nested(item) for item in _list(p["node_ids"], "node_ids")), tuple(nested(item) for item in _list(p["edge_ids"], "edge_ids")))
        if model == "graph_traversal":
            p = strict(payload, model, {"start_node_id", "mode", "visited_node_ids", "traversed_edge_ids", "paths"})
            return GraphTraversal(nested(p["start_node_id"]), GraphTraversalMode(p["mode"]), tuple(nested(item) for item in _list(p["visited_node_ids"], "visited_node_ids")), tuple(nested(item) for item in _list(p["traversed_edge_ids"], "traversed_edge_ids")), tuple(nested(item) for item in _list(p["paths"], "paths")))  # type: ignore[arg-type]
        if model == "graph_statistics":
            p = strict(payload, model, {"node_count", "edge_count", "density", "average_degree", "components", "depth", "width"})
            return GraphStatistics(p["node_count"], p["edge_count"], p["density"], p["average_degree"], p["components"], p["depth"], p["width"])  # type: ignore[arg-type]
        if model == "graph_descriptor":
            p = strict(payload, model, {"name", "description", "status", "consistency"})
            return GraphDescriptor(p["name"], p["description"], GraphStatus(p["status"]), GraphConsistency(p["consistency"]))  # type: ignore[arg-type]
        if model == "canonical_graph":
            p = strict(payload, model, {"identity", "metadata", "descriptor", "nodes", "edges"})
            return self._factory.from_parts(identity=nested(p["identity"]), metadata=nested(p["metadata"]), descriptor=nested(p["descriptor"]), nodes=tuple(nested(item) for item in _list(p["nodes"], "nodes")), edges=tuple(nested(item) for item in _list(p["edges"], "edges")))  # type: ignore[arg-type]
        if model == "graph_snapshot":
            p = strict(payload, model, {"snapshot_id", "graph", "captured_at", "digest", "snapshot_type", "version"})
            value = GraphSnapshot(UUID(p["snapshot_id"]), nested(p["graph"]), parse_instant(p["captured_at"], "captured_at"), p["digest"], GraphSnapshotType(p["snapshot_type"]), p["version"])  # type: ignore[arg-type]
            if self.digest(value.graph) != value.digest:
                raise GraphSerializationError("snapshot graph digest mismatch")
            return value
        if model == "graph_collection":
            p = strict(payload, model, {"graphs", "name"})
            return self._factory.create_collection(tuple(nested(item) for item in _list(p["graphs"], "graphs")), p["name"])  # type: ignore[arg-type]
        if model == "graph_query":
            p = strict(payload, model, {"node_ids", "namespaces", "node_types", "authors", "categories", "statuses", "versions", "limit", "offset"})
            return GraphQuery(tuple(nested(item) for item in _list(p["node_ids"], "node_ids")), tuple(_list(p["namespaces"], "namespaces")), tuple(GraphNodeType(item) for item in _list(p["node_types"], "node_types")), tuple(_list(p["authors"], "authors")), tuple(_list(p["categories"], "categories")), tuple(_list(p["statuses"], "statuses")), tuple(_list(p["versions"], "versions")), p["limit"], p["offset"])  # type: ignore[arg-type]
        if model == "graph_result":
            p = strict(payload, model, {"query", "nodes", "edges", "total_nodes", "total_edges"})
            return GraphResult(nested(p["query"]), tuple(nested(item) for item in _list(p["nodes"], "nodes")), tuple(nested(item) for item in _list(p["edges"], "edges")), p["total_nodes"], p["total_edges"])  # type: ignore[arg-type]
        raise GraphSerializationError(f"unknown model discriminator: {model}")


__all__ = ["DeterministicGraphSerializer"]
