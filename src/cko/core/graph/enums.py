"""Official enumerations for canonical in-memory graphs."""

from enum import Enum


class GraphStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class GraphTraversalMode(str, Enum):
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"


class GraphNodeType(str, Enum):
    KNOWLEDGE_OBJECT = "knowledge_object"
    CANONICAL_DOCUMENT = "canonical_document"


class GraphEdgeType(str, Enum):
    CANONICAL_RELATIONSHIP = "canonical_relationship"


class GraphSnapshotType(str, Enum):
    FULL = "full"
    STRUCTURAL = "structural"


class GraphConsistency(str, Enum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"


__all__ = [
    "GraphConsistency", "GraphEdgeType", "GraphNodeType", "GraphSnapshotType",
    "GraphStatus", "GraphTraversalMode",
]
