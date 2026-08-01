"""Official semantic enumerations for canonical relationships."""

from enum import Enum


class RelationshipType(str, Enum):
    REFERENCES = "references"
    CONTAINS = "contains"
    CONTAINED_BY = "contained_by"
    DERIVED_FROM = "derived_from"
    DERIVED_INTO = "derived_into"
    DUPLICATES = "duplicates"
    EQUIVALENT_TO = "equivalent_to"
    SUPERSEDES = "supersedes"
    UPDATED_BY = "updated_by"
    SUPPORTS = "supports"
    SUPPORTED_BY = "supported_by"
    CONTRADICTS = "contradicts"
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"
    REQUIRED_BY = "required_by"
    GENERATED_FROM = "generated_from"
    GENERATED_INTO = "generated_into"
    CLASSIFIED_AS = "classified_as"
    MEMBER_OF = "member_of"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"


class RelationshipStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class RelationshipDirectionType(str, Enum):
    DIRECTED = "directed"
    BIDIRECTIONAL = "bidirectional"
    UNDIRECTED = "undirected"


class RelationshipEvidenceType(str, Enum):
    SOURCE = "source"
    DOCUMENT = "document"
    ASSERTION = "assertion"
    ALGORITHM = "algorithm"
    AUTHOR = "author"
    PIPELINE = "pipeline"


class RelationshipConstraintType(str, Enum):
    UNIQUENESS = "uniqueness"
    MULTIPLICITY = "multiplicity"
    BIDIRECTIONALITY = "bidirectionality"
    TRANSITIVITY = "transitivity"
    SYMMETRY = "symmetry"
    REFLEXIVITY = "reflexivity"


class RelationshipStrength(str, Enum):
    UNKNOWN = "unknown"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    ABSOLUTE = "absolute"


__all__ = [
    "RelationshipConstraintType", "RelationshipDirectionType",
    "RelationshipEvidenceType", "RelationshipStatus", "RelationshipStrength",
    "RelationshipType",
]
