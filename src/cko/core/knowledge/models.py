"""Canonical immutable aggregate and transport models for knowledge."""

from __future__ import annotations

import hashlib
import json
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from typing import ClassVar, Mapping
from uuid import UUID

from .contracts import (KNOWLEDGE_SCHEMA_VERSION, SerializableKnowledgeModel, deep_freeze,
                        model_sequence, primitive, require_hash, require_instant,
                        require_text, unique_texts)
from .enums import KnowledgeContentKind, KnowledgeStatus, KnowledgeType
from .errors import KnowledgeFactoryError, KnowledgeValidationError
from .identity import KnowledgeObjectId, KnowledgeObjectIdentity
from .metadata import KnowledgeMetadata, KnowledgeReference
from .relationships import KnowledgeRelationship
from .versioning import KnowledgeVersion


_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True)
class KnowledgeContent(SerializableKnowledgeModel):
    kind: KnowledgeContentKind
    value: object = None
    fragments: tuple[KnowledgeContent, ...] = ()
    references: tuple[KnowledgeReference, ...] = ()
    derived_from: tuple[KnowledgeObjectId, ...] = ()
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_content"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "kind", KnowledgeContentKind(self.kind))
        except (TypeError, ValueError) as error:
            raise KnowledgeValidationError("kind must be KnowledgeContentKind") from error
        object.__setattr__(self, "value", deep_freeze(self.value))
        object.__setattr__(self, "fragments", model_sequence(self.fragments, "fragments", KnowledgeContent))
        object.__setattr__(self, "references", model_sequence(self.references, "references", KnowledgeReference))
        object.__setattr__(self, "derived_from", model_sequence(self.derived_from, "derived_from", KnowledgeObjectId))
        if self.kind is KnowledgeContentKind.EMPTY and (self.value is not None or self.fragments or self.references or self.derived_from):
            raise KnowledgeValidationError("empty content cannot carry payload")
        if self.kind is KnowledgeContentKind.TEXT and not isinstance(self.value, str):
            raise KnowledgeValidationError("text content requires a string value")
        if self.kind is KnowledgeContentKind.BYTES and not isinstance(self.value, bytes):
            raise KnowledgeValidationError("bytes content requires bytes")
        if self.kind is KnowledgeContentKind.FRAGMENTS and not self.fragments:
            raise KnowledgeValidationError("fragment content requires fragments")
        if self.kind is KnowledgeContentKind.REFERENCES and not self.references:
            raise KnowledgeValidationError("reference content requires references")
        if self.kind is KnowledgeContentKind.DERIVED and not self.derived_from:
            raise KnowledgeValidationError("derived content requires source object ids")
        self._validate_schema()

    @classmethod
    def empty(cls) -> KnowledgeContent:
        return cls(KnowledgeContentKind.EMPTY)

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "kind": self.kind.value,
                "value": primitive(self.value), "fragments": primitive(self.fragments),
                "references": primitive(self.references), "derived_from": primitive(self.derived_from)}


@dataclass(frozen=True, slots=True)
class KnowledgeContext(SerializableKnowledgeModel):
    name: str
    values: Mapping[str, object] = field(default_factory=dict)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_context"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", require_text(self.name, "name"))
        if not isinstance(self.values, Mapping):
            raise KnowledgeValidationError("values must be a mapping")
        object.__setattr__(self, "values", deep_freeze(self.values))
        start = None if self.valid_from is None else require_instant(self.valid_from, "valid_from")
        end = None if self.valid_to is None else require_instant(self.valid_to, "valid_to")
        if start is not None and end is not None and end < start:
            raise KnowledgeValidationError("valid_to cannot precede valid_from")
        object.__setattr__(self, "valid_from", start); object.__setattr__(self, "valid_to", end)
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "name": self.name,
                "values": primitive(self.values), "valid_from": None if self.valid_from is None else self.valid_from.isoformat(),
                "valid_to": None if self.valid_to is None else self.valid_to.isoformat()}


@dataclass(frozen=True, slots=True)
class KnowledgeObject(SerializableKnowledgeModel):
    identity: KnowledgeObjectIdentity
    metadata: KnowledgeMetadata
    content: KnowledgeContent
    version: KnowledgeVersion
    relationships: tuple[KnowledgeRelationship, ...] = ()
    contexts: tuple[KnowledgeContext, ...] = ()
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    _factory_token: InitVar[object | None] = None
    model_name: ClassVar[str] = "knowledge_object"

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _FACTORY_TOKEN:
            raise KnowledgeFactoryError("KnowledgeObject must be created by KnowledgeObjectFactory")
        if not isinstance(self.identity, KnowledgeObjectIdentity) or not isinstance(self.metadata, KnowledgeMetadata):
            raise KnowledgeValidationError("identity and metadata are required canonical models")
        if not isinstance(self.content, KnowledgeContent) or not isinstance(self.version, KnowledgeVersion):
            raise KnowledgeValidationError("content and version are required canonical models")
        if self.identity.version != self.version.version:
            raise KnowledgeValidationError("identity and version values must match")
        if self.version.object_id is not None and self.version.object_id != self.identity.logical_id:
            raise KnowledgeValidationError("version object_id must match logical_id")
        object.__setattr__(self, "relationships", model_sequence(self.relationships, "relationships", KnowledgeRelationship))
        object.__setattr__(self, "contexts", model_sequence(self.contexts, "contexts", KnowledgeContext))
        ids = tuple(item.relationship_id for item in self.relationships)
        if len(ids) != len(set(ids)):
            raise KnowledgeValidationError("relationships must not contain duplicates")
        for relation in self.relationships:
            if relation.source_id != self.identity.logical_id and relation.target_id != self.identity.logical_id:
                raise KnowledgeValidationError("relationship must reference this Knowledge Object")
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "identity": primitive(self.identity),
                "metadata": primitive(self.metadata), "content": primitive(self.content), "version": primitive(self.version),
                "relationships": primitive(self.relationships), "contexts": primitive(self.contexts)}


@dataclass(frozen=True, slots=True)
class KnowledgeCollection(SerializableKnowledgeModel):
    objects: tuple[KnowledgeObject, ...] = ()
    name: str | None = None
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_collection"

    def __post_init__(self) -> None:
        object.__setattr__(self, "objects", model_sequence(self.objects, "objects", KnowledgeObject))
        object.__setattr__(self, "name", require_text(self.name, "name", optional=True))
        ids = tuple(item.identity.canonical_id for item in self.objects)
        if len(ids) != len(set(ids)):
            raise KnowledgeValidationError("collection objects must be unique")
        self._validate_schema()

    def __iter__(self): return iter(self.objects)
    def __len__(self) -> int: return len(self.objects)
    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "objects": primitive(self.objects), "name": self.name}


@dataclass(frozen=True, slots=True)
class KnowledgeSnapshot(SerializableKnowledgeModel):
    snapshot_id: UUID
    object: KnowledgeObject
    captured_at: datetime
    hash: str
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_snapshot"

    def __post_init__(self) -> None:
        try: object.__setattr__(self, "snapshot_id", self.snapshot_id if isinstance(self.snapshot_id, UUID) else UUID(str(self.snapshot_id)))
        except (TypeError, ValueError, AttributeError) as error: raise KnowledgeValidationError("snapshot_id must be UUID") from error
        if not isinstance(self.object, KnowledgeObject): raise KnowledgeValidationError("object must be KnowledgeObject")
        object.__setattr__(self, "captured_at", require_instant(self.captured_at, "captured_at"))
        object.__setattr__(self, "hash", require_hash(self.hash))
        canonical = json.dumps(
            primitive(self.object), ensure_ascii=False, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        if hashlib.sha256(canonical).hexdigest() != self.hash:
            raise KnowledgeValidationError("snapshot hash does not match object")
        self._validate_schema()

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "snapshot_id": str(self.snapshot_id),
                "object": primitive(self.object), "captured_at": self.captured_at.isoformat(), "hash": self.hash}


@dataclass(frozen=True, slots=True)
class KnowledgeDescriptor(SerializableKnowledgeModel):
    identity: KnowledgeObjectIdentity
    title: str
    summary: str | None = None
    status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    tags: tuple[str, ...] = ()
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_descriptor"
    def __post_init__(self) -> None:
        if not isinstance(self.identity, KnowledgeObjectIdentity): raise KnowledgeValidationError("identity must be KnowledgeObjectIdentity")
        object.__setattr__(self, "title", require_text(self.title, "title")); object.__setattr__(self, "summary", require_text(self.summary, "summary", optional=True))
        try: object.__setattr__(self, "status", KnowledgeStatus(self.status))
        except (TypeError, ValueError) as error: raise KnowledgeValidationError("status must be KnowledgeStatus") from error
        object.__setattr__(self, "tags", unique_texts(self.tags, "tags")); self._validate_schema()
    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "identity": primitive(self.identity),
                "title": self.title, "summary": self.summary, "status": self.status.value, "tags": primitive(self.tags)}


@dataclass(frozen=True, slots=True)
class KnowledgeQuery(SerializableKnowledgeModel):
    object_ids: tuple[KnowledgeObjectId, ...] = ()
    knowledge_types: tuple[KnowledgeType, ...] = ()
    statuses: tuple[KnowledgeStatus, ...] = ()
    domains: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    limit: int = 100
    offset: int = 0
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_query"
    def __post_init__(self) -> None:
        object.__setattr__(self, "object_ids", model_sequence(self.object_ids, "object_ids", KnowledgeObjectId))
        try:
            object.__setattr__(self, "knowledge_types", tuple(KnowledgeType(item) for item in self.knowledge_types))
            object.__setattr__(self, "statuses", tuple(KnowledgeStatus(item) for item in self.statuses))
        except (TypeError, ValueError) as error: raise KnowledgeValidationError("query contains an invalid enum") from error
        object.__setattr__(self, "domains", unique_texts(self.domains, "domains")); object.__setattr__(self, "tags", unique_texts(self.tags, "tags"))
        if isinstance(self.limit, bool) or not isinstance(self.limit, int) or self.limit < 1: raise KnowledgeValidationError("limit must be a positive integer")
        if isinstance(self.offset, bool) or not isinstance(self.offset, int) or self.offset < 0: raise KnowledgeValidationError("offset must be a non-negative integer")
        self._validate_schema()
    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "object_ids": primitive(self.object_ids),
                "knowledge_types": primitive(self.knowledge_types), "statuses": primitive(self.statuses),
                "domains": primitive(self.domains), "tags": primitive(self.tags), "limit": self.limit, "offset": self.offset}


@dataclass(frozen=True, slots=True)
class KnowledgeResult(SerializableKnowledgeModel):
    query: KnowledgeQuery
    objects: tuple[KnowledgeObject, ...]
    total: int
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_result"
    def __post_init__(self) -> None:
        if not isinstance(self.query, KnowledgeQuery): raise KnowledgeValidationError("query must be KnowledgeQuery")
        object.__setattr__(self, "objects", model_sequence(self.objects, "objects", KnowledgeObject))
        if isinstance(self.total, bool) or not isinstance(self.total, int) or self.total < len(self.objects): raise KnowledgeValidationError("total cannot be less than result size")
        self._validate_schema()
    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model, "query": primitive(self.query), "objects": primitive(self.objects), "total": self.total}


__all__ = ["KnowledgeCollection", "KnowledgeContent", "KnowledgeContext", "KnowledgeDescriptor",
           "KnowledgeObject", "KnowledgeQuery", "KnowledgeResult", "KnowledgeSnapshot", "_FACTORY_TOKEN"]
