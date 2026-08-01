"""Official technology-neutral enumerations for Knowledge Objects."""

from enum import Enum


class KnowledgeType(str, Enum):
    TEXT = "text"
    FACT = "fact"
    CONCEPT = "concept"
    CLAIM = "claim"
    RULE = "rule"
    PROCEDURE = "procedure"
    EVENT = "event"
    ENTITY = "entity"
    OBSERVATION = "observation"
    DATA = "data"
    COMPOSITE = "composite"
    OTHER = "other"


class RelationshipType(str, Enum):
    REFERENCES = "references"
    CONTAINS = "contains"
    DERIVED_FROM = "derived_from"
    DUPLICATES = "duplicates"
    UPDATES = "updates"
    SUPERSEDES = "supersedes"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    SUMMARIZES = "summarizes"
    RELATED_TO = "related_to"


class KnowledgeStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    REVIEWED = "reviewed"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class KnowledgeConfidence(str, Enum):
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class KnowledgeSourceType(str, Enum):
    HUMAN = "human"
    SYSTEM = "system"
    IMPORTED = "imported"
    DERIVED = "derived"
    OBSERVED = "observed"
    EXTERNAL = "external"


class KnowledgeCategory(str, Enum):
    GENERAL = "general"
    BUSINESS = "business"
    TECHNICAL = "technical"
    SCIENTIFIC = "scientific"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    GOVERNANCE = "governance"
    OTHER = "other"


class KnowledgeContentKind(str, Enum):
    EMPTY = "empty"
    TEXT = "text"
    JSON = "json"
    STRUCTURE = "structure"
    FRAGMENTS = "fragments"
    REFERENCES = "references"
    BYTES = "bytes"
    DERIVED = "derived"


__all__ = [
    "KnowledgeCategory",
    "KnowledgeConfidence",
    "KnowledgeContentKind",
    "KnowledgeSourceType",
    "KnowledgeStatus",
    "KnowledgeType",
    "RelationshipType",
]
