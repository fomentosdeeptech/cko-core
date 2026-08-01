"""Deterministic structural navigation over canonical in-memory graphs."""

from __future__ import annotations

from collections import deque

from cko.core.relationships import RelationshipDirectionType

from .enums import GraphTraversalMode
from .errors import GraphNavigationError
from .identity import GraphId
from .models import (
    CanonicalGraph, GraphEdge, GraphNode, GraphPath, GraphStatistics, GraphTraversal,
)


class GraphNavigation:
    """Read-only structural operations with stable ordering."""

    def __init__(self, graph: CanonicalGraph) -> None:
        if not isinstance(graph, CanonicalGraph):
            raise GraphNavigationError("graph must be CanonicalGraph")
        self._graph = graph
        self._nodes = {node.node_id: node for node in graph.nodes}
        self._endpoint_nodes = {self._endpoint_key(node): node.node_id for node in graph.nodes}

    @staticmethod
    def _endpoint_key(node: GraphNode) -> tuple[str, object, str]:
        value = node.value
        return (value.identity.namespace, value.identity.logical_id.value,
                node.node_type.value)

    def _ends(self, edge: GraphEdge) -> tuple[GraphId, GraphId]:
        source = edge.relationship.source
        target = edge.relationship.target
        try:
            return (self._endpoint_nodes[(source.namespace, source.object_id, source.entity_type)],
                    self._endpoint_nodes[(target.namespace, target.object_id, target.entity_type)])
        except KeyError as error:
            raise GraphNavigationError("edge references a node outside the graph") from error

    def get_node(self, node_id: GraphId) -> GraphNode:
        if not isinstance(node_id, GraphId):
            raise GraphNavigationError("node_id must be GraphId")
        try:
            return self._nodes[node_id]
        except KeyError as error:
            raise GraphNavigationError("node was not found") from error

    def get_edges(self, node_id: GraphId | None = None) -> tuple[GraphEdge, ...]:
        if node_id is not None:
            self.get_node(node_id)
        result = tuple(edge for edge in self._graph.edges
                       if node_id is None or node_id in self._ends(edge))
        return tuple(sorted(result, key=lambda edge: str(edge.edge_id)))

    def incoming(self, node_id: GraphId) -> tuple[GraphEdge, ...]:
        self.get_node(node_id)
        result = []
        for edge in self._graph.edges:
            source, target = self._ends(edge)
            direction = edge.relationship.descriptor.direction.direction
            if target == node_id or (source == node_id and direction in {
                RelationshipDirectionType.BIDIRECTIONAL,
                RelationshipDirectionType.UNDIRECTED,
            }):
                result.append(edge)
        return tuple(sorted(result, key=lambda edge: str(edge.edge_id)))

    def outgoing(self, node_id: GraphId) -> tuple[GraphEdge, ...]:
        self.get_node(node_id)
        result = []
        for edge in self._graph.edges:
            source, target = self._ends(edge)
            direction = edge.relationship.descriptor.direction.direction
            if source == node_id or (target == node_id and direction in {
                RelationshipDirectionType.BIDIRECTIONAL,
                RelationshipDirectionType.UNDIRECTED,
            }):
                result.append(edge)
        return tuple(sorted(result, key=lambda edge: str(edge.edge_id)))

    def neighbors(self, node_id: GraphId) -> tuple[GraphNode, ...]:
        self.get_node(node_id)
        ids: set[GraphId] = set()
        for edge in self.get_edges(node_id):
            source, target = self._ends(edge)
            ids.add(target if source == node_id else source)
        return tuple(self._nodes[item] for item in sorted(ids, key=str))

    def degree(self, node_id: GraphId) -> int:
        return len(self.get_edges(node_id))

    def connected_components(self) -> tuple[tuple[GraphId, ...], ...]:
        remaining = set(self._nodes)
        components: list[tuple[GraphId, ...]] = []
        while remaining:
            start = min(remaining, key=str)
            queue = deque([start]); visited = {start}
            while queue:
                current = queue.popleft()
                for neighbor in self.neighbors(current):
                    if neighbor.node_id not in visited:
                        visited.add(neighbor.node_id); queue.append(neighbor.node_id)
            remaining -= visited
            components.append(tuple(sorted(visited, key=str)))
        return tuple(components)

    def list_paths(self, source_id: GraphId, target_id: GraphId,
                   max_depth: int | None = None) -> tuple[GraphPath, ...]:
        self.get_node(source_id); self.get_node(target_id)
        limit = len(self._nodes) - 1 if max_depth is None else max_depth
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise GraphNavigationError("max_depth must be a non-negative integer")
        found: list[GraphPath] = []

        def visit(current: GraphId, nodes: tuple[GraphId, ...], edges: tuple[GraphId, ...]) -> None:
            if current == target_id:
                found.append(GraphPath(nodes, edges)); return
            if len(edges) >= limit:
                return
            candidates = []
            for edge in self.get_edges(current):
                left, right = self._ends(edge)
                next_id = right if left == current else left
                if next_id not in nodes:
                    candidates.append((str(next_id), str(edge.edge_id), next_id, edge.edge_id))
            for _, __, next_id, edge_id in sorted(candidates):
                visit(next_id, nodes + (next_id,), edges + (edge_id,))

        visit(source_id, (source_id,), ())
        return tuple(found)

    def traverse(self, start_node_id: GraphId,
                 mode: GraphTraversalMode = GraphTraversalMode.BREADTH_FIRST) -> GraphTraversal:
        self.get_node(start_node_id)
        try:
            selected_mode = GraphTraversalMode(mode)
        except (TypeError, ValueError) as error:
            raise GraphNavigationError("mode must be GraphTraversalMode") from error
        pending = deque([start_node_id]); visited: list[GraphId] = []
        seen = {start_node_id}; traversed: list[GraphId] = []
        while pending:
            current = pending.popleft() if selected_mode is GraphTraversalMode.BREADTH_FIRST else pending.pop()
            visited.append(current)
            candidates = []
            for edge in self.get_edges(current):
                left, right = self._ends(edge); next_id = right if left == current else left
                if next_id not in seen:
                    candidates.append((next_id, edge.edge_id))
            candidates.sort(key=lambda item: str(item[0]), reverse=selected_mode is GraphTraversalMode.DEPTH_FIRST)
            for next_id, edge_id in candidates:
                if next_id not in seen:
                    seen.add(next_id); traversed.append(edge_id); pending.append(next_id)
        paths_list: list[GraphPath] = []
        for item in visited[1:]:
            candidates = self.list_paths(start_node_id, item)
            if candidates:
                paths_list.append(min(candidates, key=lambda path: (path.length, tuple(map(str, path.node_ids)))))
        paths = tuple(paths_list)
        return GraphTraversal(start_node_id, selected_mode, tuple(visited), tuple(traversed), paths)

    def maximum_depth(self) -> int:
        maximum = 0
        for start in sorted(self._nodes, key=str):
            distances = self._distances(start)
            maximum = max(maximum, max(distances.values(), default=0))
        return maximum

    def width(self) -> int:
        maximum = 0
        for start in sorted(self._nodes, key=str):
            counts: dict[int, int] = {}
            for distance in self._distances(start).values():
                counts[distance] = counts.get(distance, 0) + 1
            maximum = max(maximum, max(counts.values(), default=0))
        return maximum

    def _distances(self, start: GraphId) -> dict[GraphId, int]:
        distances = {start: 0}; queue = deque([start])
        while queue:
            current = queue.popleft()
            for node in self.neighbors(current):
                if node.node_id not in distances:
                    distances[node.node_id] = distances[current] + 1; queue.append(node.node_id)
        return distances

    def statistics(self) -> GraphStatistics:
        nodes = len(self._graph.nodes); edges = len(self._graph.edges)
        density = 0.0 if nodes < 2 else min(1.0, edges / (nodes * (nodes - 1)))
        average = 0.0 if nodes == 0 else (2.0 * edges) / nodes
        return GraphStatistics(nodes, edges, density, average,
                               len(self.connected_components()),
                               self.maximum_depth(), self.width())


GraphNavigator = GraphNavigation

__all__ = ["GraphNavigation", "GraphNavigator"]
