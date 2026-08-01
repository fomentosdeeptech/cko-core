"""Official enumerations for canonical declarative queries."""

from enum import Enum


class QueryOperator(str, Enum):
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    BETWEEN = "between"
    AND = "and"
    OR = "or"
    NOT = "not"


class QueryStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    COMPLETED = "completed"
    PARTIAL = "partial"
    EMPTY = "empty"
    FAILED = "failed"


class QueryDirection(str, Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class QueryScope(str, Enum):
    CURRENT_NAMESPACE = "current_namespace"
    DESCENDANT_NAMESPACES = "descendant_namespaces"
    GLOBAL = "global"


class QueryTarget(str, Enum):
    KNOWLEDGE_OBJECT = "knowledge_object"
    CANONICAL_DOCUMENT = "canonical_document"
    CANONICAL_RELATIONSHIP = "canonical_relationship"
    CANONICAL_GRAPH = "canonical_graph"


class QueryConsistency(str, Enum):
    DECLARED = "declared"
    CONSISTENT = "consistent"
    SNAPSHOT = "snapshot"


__all__ = [
    "QueryConsistency", "QueryDirection", "QueryOperator", "QueryScope",
    "QueryStatus", "QueryTarget",
]
