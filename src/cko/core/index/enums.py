"""Official stable enumerations for canonical in-memory indexes."""

from enum import Enum


class IndexType(str, Enum):
    IDENTITY="identity"; NAMESPACE="namespace"; ENTITY_TYPE="entity_type"
    DOCUMENT_TYPE="document_type"; RELATIONSHIP_TYPE="relationship_type"
    GRAPH_NODE_TYPE="graph_node_type"; STATUS="status"; CATEGORY="category"
    AUTHOR="author"; CREATOR="creator"; ORGANIZATION="organization"
    SOURCE="source"; LANGUAGE="language"; VERSION="version"; TAG="tag"
    KEYWORD="keyword"; ATTRIBUTE="attribute"; PROPERTY="property"
    CREATED_AT="created_at"; UPDATED_AT="updated_at"; CHECKSUM="checksum"
    CUSTOM="custom"


class IndexTarget(str, Enum):
    KNOWLEDGE_OBJECT="knowledge_object"; CANONICAL_DOCUMENT="canonical_document"
    CANONICAL_RELATIONSHIP="canonical_relationship"; CANONICAL_GRAPH="canonical_graph"
    CANONICAL_QUERY="canonical_query"


class IndexStatus(str, Enum):
    DRAFT="draft"; ACTIVE="active"; INACTIVE="inactive"; REBUILDING="rebuilding"


class IndexOperationType(str, Enum):
    ADD="add"; REMOVE="remove"; REPLACE="replace"; REBUILD="rebuild"
    CLEAR="clear"; MERGE="merge"


class IndexSnapshotType(str, Enum):
    FULL="full"; STRUCTURAL="structural"; STATISTICS="statistics"


class IndexConsistency(str, Enum):
    DECLARED="declared"; CONSISTENT="consistent"; VERIFIED="verified"


class IndexValuePolicy(str, Enum):
    REJECT="reject"; IGNORE="ignore"; INDEX_NULL="index_null"


class IndexMultiplicity(str, Enum):
    SINGLE="single"; MULTIPLE="multiple"


class IndexOrdering(str, Enum):
    ASCENDING="ascending"; DESCENDING="descending"


class IndexKeyType(str, Enum):
    TEXT="text"; INTEGER="integer"; DECIMAL="decimal"; BOOLEAN="boolean"
    UUID="uuid"; DATETIME="datetime"; ENUM="enum"; SHA256="sha256"
    SEQUENCE="sequence"; NULL="null"


__all__ = ["IndexConsistency", "IndexKeyType", "IndexMultiplicity",
           "IndexOperationType", "IndexOrdering", "IndexSnapshotType",
           "IndexStatus", "IndexTarget", "IndexType", "IndexValuePolicy"]
