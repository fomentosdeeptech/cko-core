"""Canonical metadata, classification, provenance, reference, and attribute models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Mapping

from .contracts import (KNOWLEDGE_SCHEMA_VERSION, SerializableKnowledgeModel, deep_freeze,
                        model_sequence, primitive, require_instant, require_probability,
                        require_text, unique_texts)
from .enums import KnowledgeCategory, KnowledgeConfidence, KnowledgeSourceType
from .errors import KnowledgeValidationError
from .identity import KnowledgeObjectId


@dataclass(frozen=True, slots=True)
class KnowledgeAttribute(SerializableKnowledgeModel):
    name: str
    value: object
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_attribute"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", require_text(self.name, "name"))
        object.__setattr__(self, "value", deep_freeze(self.value))
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model,
                "name": self.name, "value": primitive(self.value)}


@dataclass(frozen=True, slots=True)
class KnowledgeReference(SerializableKnowledgeModel):
    reference_id: str
    target: str
    title: str | None = None
    target_object_id: KnowledgeObjectId | None = None
    attributes: tuple[KnowledgeAttribute, ...] = ()
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_reference"

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_id", require_text(self.reference_id, "reference_id"))
        object.__setattr__(self, "target", require_text(self.target, "target"))
        object.__setattr__(self, "title", require_text(self.title, "title", optional=True))
        if self.target_object_id is not None and not isinstance(self.target_object_id, KnowledgeObjectId):
            raise KnowledgeValidationError("target_object_id must be KnowledgeObjectId")
        object.__setattr__(self, "attributes", model_sequence(self.attributes, "attributes", KnowledgeAttribute))
        names = tuple(item.name for item in self.attributes)
        if len(names) != len(set(names)):
            raise KnowledgeValidationError("reference attributes must have unique names")
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model,
                "reference_id": self.reference_id, "target": self.target, "title": self.title,
                "target_object_id": primitive(self.target_object_id), "attributes": primitive(self.attributes)}


@dataclass(frozen=True, slots=True)
class KnowledgeProvenance(SerializableKnowledgeModel):
    origin: str
    pipeline: str
    generating_process: str
    original_source: str
    timestamp: datetime
    pipeline_version: str
    source_type: KnowledgeSourceType = KnowledgeSourceType.SYSTEM
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_provenance"

    def __post_init__(self) -> None:
        for name in ("origin", "pipeline", "generating_process", "original_source", "pipeline_version"):
            object.__setattr__(self, name, require_text(getattr(self, name), name))
        object.__setattr__(self, "timestamp", require_instant(self.timestamp, "timestamp"))
        try:
            object.__setattr__(self, "source_type", KnowledgeSourceType(self.source_type))
        except (TypeError, ValueError) as error:
            raise KnowledgeValidationError("source_type must be KnowledgeSourceType") from error
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "origin": self.origin,
                "pipeline": self.pipeline, "generating_process": self.generating_process,
                "original_source": self.original_source, "timestamp": self.timestamp.isoformat(),
                "pipeline_version": self.pipeline_version, "source_type": self.source_type.value}


@dataclass(frozen=True, slots=True)
class KnowledgeClassification(SerializableKnowledgeModel):
    domain: str
    category: KnowledgeCategory
    subcategory: str | None = None
    taxonomy: str | None = None
    origin: str | None = None
    confidence: float | None = None
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_classification"

    def __post_init__(self) -> None:
        object.__setattr__(self, "domain", require_text(self.domain, "domain"))
        for name in ("subcategory", "taxonomy", "origin"):
            object.__setattr__(self, name, require_text(getattr(self, name), name, optional=True))
        try:
            object.__setattr__(self, "category", KnowledgeCategory(self.category))
        except (TypeError, ValueError) as error:
            raise KnowledgeValidationError("category must be KnowledgeCategory") from error
        object.__setattr__(self, "confidence", require_probability(self.confidence, "confidence"))
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "domain": self.domain,
                "category": self.category.value, "subcategory": self.subcategory, "taxonomy": self.taxonomy,
                "origin": self.origin, "confidence": self.confidence}


@dataclass(frozen=True, slots=True)
class KnowledgeMetadata(SerializableKnowledgeModel):
    created_at: datetime
    modified_at: datetime
    author: str | None = None
    creator: str | None = None
    published_at: datetime | None = None
    language: str | None = None
    domain: str | None = None
    category: KnowledgeCategory = KnowledgeCategory.GENERAL
    tags: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    confidence: KnowledgeConfidence = KnowledgeConfidence.UNKNOWN
    confidence_score: float | None = None
    source: str | None = None
    license: str | None = None
    provenances: tuple[KnowledgeProvenance, ...] = ()
    classifications: tuple[KnowledgeClassification, ...] = ()
    attributes: tuple[KnowledgeAttribute, ...] = ()
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_metadata"

    def __post_init__(self) -> None:
        created = require_instant(self.created_at, "created_at")
        modified = require_instant(self.modified_at, "modified_at")
        if modified < created:
            raise KnowledgeValidationError("modified_at cannot precede created_at")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "modified_at", modified)
        if self.published_at is not None:
            published = require_instant(self.published_at, "published_at")
            object.__setattr__(self, "published_at", published)
        for name in ("author", "creator", "language", "domain", "source", "license"):
            object.__setattr__(self, name, require_text(getattr(self, name), name, optional=True))
        try:
            object.__setattr__(self, "category", KnowledgeCategory(self.category))
            object.__setattr__(self, "confidence", KnowledgeConfidence(self.confidence))
        except (TypeError, ValueError) as error:
            raise KnowledgeValidationError("invalid metadata enum") from error
        object.__setattr__(self, "tags", unique_texts(self.tags, "tags"))
        object.__setattr__(self, "keywords", unique_texts(self.keywords, "keywords"))
        object.__setattr__(self, "confidence_score", require_probability(self.confidence_score, "confidence_score"))
        for name, expected in (("provenances", KnowledgeProvenance), ("classifications", KnowledgeClassification),
                               ("attributes", KnowledgeAttribute)):
            object.__setattr__(self, name, model_sequence(getattr(self, name), name, expected))
        names = tuple(item.name for item in self.attributes)
        if len(names) != len(set(names)):
            raise KnowledgeValidationError("metadata attributes must have unique names")
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "author": self.author,
                "creator": self.creator, "created_at": self.created_at.isoformat(),
                "modified_at": self.modified_at.isoformat(),
                "published_at": None if self.published_at is None else self.published_at.isoformat(),
                "language": self.language, "domain": self.domain, "category": self.category.value,
                "tags": primitive(self.tags), "keywords": primitive(self.keywords),
                "confidence": self.confidence.value, "confidence_score": self.confidence_score,
                "source": self.source, "license": self.license, "provenances": primitive(self.provenances),
                "classifications": primitive(self.classifications), "attributes": primitive(self.attributes)}


__all__ = ["KnowledgeAttribute", "KnowledgeClassification", "KnowledgeMetadata",
           "KnowledgeProvenance", "KnowledgeReference"]
