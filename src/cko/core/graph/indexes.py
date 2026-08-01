"""Immutable in-memory indexes for canonical graph nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from .enums import GraphNodeType
from .errors import GraphIndexError
from .identity import GraphId
from .models import CanonicalGraph, GraphNode, GraphQuery, GraphResult


def _freeze_index(value: Mapping[str, set[GraphId]]) -> Mapping[str, tuple[GraphId, ...]]:
    return MappingProxyType({key: tuple(sorted(items, key=str))
                             for key, items in sorted(value.items())})


@dataclass(frozen=True, slots=True)
class GraphIndexes:
    identity: Mapping[str, tuple[GraphId, ...]] = field(default_factory=dict)
    namespace: Mapping[str, tuple[GraphId, ...]] = field(default_factory=dict)
    type: Mapping[str, tuple[GraphId, ...]] = field(default_factory=dict)
    author: Mapping[str, tuple[GraphId, ...]] = field(default_factory=dict)
    category: Mapping[str, tuple[GraphId, ...]] = field(default_factory=dict)
    status: Mapping[str, tuple[GraphId, ...]] = field(default_factory=dict)
    version: Mapping[str, tuple[GraphId, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("identity", "namespace", "type", "author", "category", "status", "version"):
            value = getattr(self, name)
            if not isinstance(value, Mapping):
                raise GraphIndexError(f"{name} index must be a mapping")
            normalized = {str(key): set(items) for key, items in value.items()}
            if any(not isinstance(item, GraphId) for items in normalized.values() for item in items):
                raise GraphIndexError(f"{name} index contains an invalid GraphId")
            object.__setattr__(self, name, _freeze_index(normalized))

    @classmethod
    def build(cls, graph: CanonicalGraph) -> "GraphIndexes":
        if not isinstance(graph, CanonicalGraph):
            raise GraphIndexError("graph must be CanonicalGraph")
        indexes: dict[str, dict[str, set[GraphId]]] = {
            name: {} for name in ("identity", "namespace", "type", "author", "category", "status", "version")
        }

        def add(index: str, key: object | None, node_id: GraphId) -> None:
            if key is not None and str(key).strip():
                indexes[index].setdefault(str(getattr(key, "value", key)), set()).add(node_id)

        for node in graph.nodes:
            value = node.value; identity = value.identity
            for identifier in (node.node_id, identity.logical_id, getattr(identity, "canonical_id", None), getattr(identity, "document_id", None)):
                if identifier is not None:
                    add("identity", getattr(identifier, "value", identifier), node.node_id)
            add("namespace", identity.namespace, node.node_id)
            add("type", node.node_type.value, node.node_id)
            if node.node_type is GraphNodeType.KNOWLEDGE_OBJECT:
                add("author", value.metadata.author or value.metadata.creator, node.node_id)
                add("category", value.metadata.category, node.node_id)
                add("status", value.version.status, node.node_id)
                add("version", value.version.version, node.node_id)
            else:
                add("author", None if value.metadata.author is None else value.metadata.author.name, node.node_id)
                add("category", value.metadata.category, node.node_id)
                add("status", value.descriptor.status, node.node_id)
                add("version", value.metadata.version, node.node_id)
        return cls(**indexes)

    def lookup(self, index: str, value: object) -> tuple[GraphId, ...]:
        selected = getattr(self, index, None)
        if not isinstance(selected, Mapping):
            raise GraphIndexError("unknown graph index")
        return selected.get(str(getattr(value, "value", value)), ())

    def execute(self, graph: CanonicalGraph, query: GraphQuery) -> GraphResult:
        if not isinstance(graph, CanonicalGraph) or not isinstance(query, GraphQuery):
            raise GraphIndexError("graph and query must be canonical graph models")
        candidates = {node.node_id for node in graph.nodes}
        filters = (
            ("identity", query.node_ids), ("namespace", query.namespaces),
            ("type", query.node_types), ("author", query.authors),
            ("category", query.categories), ("status", query.statuses),
            ("version", query.versions),
        )
        for index, values in filters:
            if values:
                matched = set().union(*(self.lookup(index, value) for value in values))
                candidates &= matched
        ordered = tuple(node for node in sorted(graph.nodes, key=lambda item: str(item.node_id))
                        if node.node_id in candidates)
        page = ordered[query.offset:query.offset + query.limit]
        page_ids = {node.node_id for node in page}
        from .navigation import GraphNavigation
        navigation = GraphNavigation(graph)
        edges = tuple(edge for edge in graph.edges
                      if set(navigation._ends(edge)).issubset(page_ids))
        return GraphResult(query, page, edges, len(ordered), len(edges))


GraphIndex = GraphIndexes

__all__ = ["GraphIndex", "GraphIndexes"]
