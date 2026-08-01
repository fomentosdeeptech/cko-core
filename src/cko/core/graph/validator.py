"""Structural and cross-model validation for canonical graphs."""

from __future__ import annotations

from dataclasses import is_dataclass

from cko.core.documents import CanonicalDocument
from cko.core.knowledge import KnowledgeObject
from cko.core.relationships import (
    CanonicalRelationship, RelationshipEndpoint, RelationshipValidator,
)

from .contracts import GraphModel
from .enums import GraphConsistency, GraphNodeType
from .errors import GraphValidationError
from .models import CanonicalGraph, GraphCollection, GraphEdge, GraphNode, GraphSnapshot


class GraphValidator:
    """Validate immutable graph models without inference or persistence."""

    def validate(self, value: GraphModel) -> None:
        if not isinstance(value, GraphModel) or not is_dataclass(value):
            raise GraphValidationError("value must be a canonical graph dataclass")
        value._validate_schema()
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen or not hasattr(type(value), "__slots__"):
            raise GraphValidationError("graph models must be frozen and slotted")
        if value.model != type(value).discriminator:
            raise GraphValidationError("invalid graph model discriminator")
        if isinstance(value, CanonicalGraph):
            self._validate_graph(value)
        elif isinstance(value, GraphCollection):
            identifiers = [graph.identity.canonical_id for graph in value.graphs]
            if len(identifiers) != len(set(identifiers)):
                raise GraphValidationError("collection graphs must be unique")
            for graph in value.graphs:
                self._validate_graph(graph)
        elif isinstance(value, GraphSnapshot):
            self._validate_graph(value.graph)

    def _validate_graph(self, graph: CanonicalGraph) -> None:
        if graph.metadata.status is not graph.descriptor.status:
            raise GraphValidationError("metadata and descriptor status mismatch")
        if graph.descriptor.consistency is not GraphConsistency.CONSISTENT:
            raise GraphValidationError("canonical graph must declare consistent structure")
        node_ids = [node.node_id for node in graph.nodes]
        edge_ids = [edge.edge_id for edge in graph.edges]
        if len(node_ids) != len(set(node_ids)):
            raise GraphValidationError("graph node identities must be unique")
        if len(edge_ids) != len(set(edge_ids)):
            raise GraphValidationError("graph edge identities must be unique")
        payload_keys = [self.node_endpoint(node) for node in graph.nodes]
        if len(payload_keys) != len(set(payload_keys)):
            raise GraphValidationError("graph node payload identities must be unique")
        relationships = [edge.relationship.identity.canonical_id for edge in graph.edges]
        if len(relationships) != len(set(relationships)):
            raise GraphValidationError("graph relationships must be unique")
        endpoints = set(payload_keys)
        relationship_validator = RelationshipValidator()
        for edge in graph.edges:
            relationship_validator.validate(edge.relationship)
            source = self.endpoint_key(edge.relationship.source)
            target = self.endpoint_key(edge.relationship.target)
            if source not in endpoints or target not in endpoints:
                raise GraphValidationError("edge endpoint does not reference a graph node")

    @staticmethod
    def endpoint_key(endpoint: RelationshipEndpoint) -> tuple[str, object, str]:
        return endpoint.namespace, endpoint.object_id, endpoint.entity_type

    @staticmethod
    def node_endpoint(node: GraphNode) -> tuple[str, object, str]:
        value = node.value
        if node.node_type is GraphNodeType.KNOWLEDGE_OBJECT:
            if not isinstance(value, KnowledgeObject):
                raise GraphValidationError("knowledge node payload is invalid")
            endpoint = RelationshipEndpoint.from_knowledge_object(value)
        else:
            if not isinstance(value, CanonicalDocument):
                raise GraphValidationError("document node payload is invalid")
            endpoint = RelationshipEndpoint.from_document(value)
        return GraphValidator.endpoint_key(endpoint)


__all__ = ["GraphValidator"]
