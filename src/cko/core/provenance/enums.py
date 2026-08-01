"""Closed vocabularies used by provenance statements."""

from enum import Enum


class ProvenanceStatementCategory(str, Enum):
    ORIGIN = "origin"
    ATTRIBUTION = "attribution"
    DERIVATION = "derivation"
    GENERATION = "generation"
    TRANSFORMATION = "transformation"
    ADAPTATION = "adaptation"
    EXTRACTION = "extraction"
    INCORPORATION = "incorporation"
    SOURCE_USAGE = "source_usage"


class ProvenanceTargetType(str, Enum):
    KNOWLEDGE_OBJECT = "knowledge_object"
    DOCUMENT = "document"
    RELATIONSHIP = "relationship"
    GRAPH = "graph"
    INDEX = "index"
    CORPUS = "corpus"
    EXTERNAL_RESOURCE = "external_resource"


class ProvenanceEntityRole(str, Enum):
    SOURCE = "source"
    INPUT = "input"
    ORIGINAL = "original"
    CONTRIBUTING_SOURCE = "contributing_source"
    SUPPORTING_ENTITY = "supporting_entity"


class ProvenanceActorType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    SYSTEM = "system"
    PROCESS = "process"


class ProvenanceActorRole(str, Enum):
    CREATOR = "creator"
    AUTHOR = "author"
    CONTRIBUTOR = "contributor"
    PRODUCER = "producer"
    RESPONSIBLE_PARTY = "responsible_party"
    TRANSFORMER = "transformer"
    REVIEWER = "reviewer"
    PUBLISHER = "publisher"


class ProvenanceActivityType(str, Enum):
    GENERATION = "generation"
    TRANSFORMATION = "transformation"
    ADAPTATION = "adaptation"
    EXTRACTION = "extraction"
    INCORPORATION = "incorporation"
    COPYING = "copying"
    OTHER_DECLARED = "other_declared"


class ProvenanceEvidenceType(str, Enum):
    DOCUMENTARY = "documentary"
    RECORD = "record"
    RELATIONSHIP = "relationship"
    OBSERVATION = "observation"
    ASSERTION = "assertion"


__all__ = [
    "ProvenanceActivityType",
    "ProvenanceActorRole",
    "ProvenanceActorType",
    "ProvenanceEntityRole",
    "ProvenanceEvidenceType",
    "ProvenanceStatementCategory",
    "ProvenanceTargetType",
]
