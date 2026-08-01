"""Canonical version lineage for Knowledge Objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from .contracts import (KNOWLEDGE_SCHEMA_VERSION, SerializableKnowledgeModel, primitive,
                        require_hash, require_instant, require_text)
from .enums import KnowledgeStatus
from .errors import KnowledgeVersionError
from .identity import KnowledgeObjectId


@dataclass(frozen=True, slots=True)
class KnowledgeVersion(SerializableKnowledgeModel):
    version_id: UUID
    version: str
    created_at: datetime
    created_by: str
    hash: str
    status: KnowledgeStatus
    parent_version: UUID | None = None
    object_id: KnowledgeObjectId | None = None
    schema_version: str = KNOWLEDGE_SCHEMA_VERSION
    model_name: ClassVar[str] = "knowledge_version"

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "version_id", self.version_id if isinstance(self.version_id, UUID) else UUID(str(self.version_id)))
            if self.parent_version is not None:
                object.__setattr__(self, "parent_version", self.parent_version if isinstance(self.parent_version, UUID) else UUID(str(self.parent_version)))
        except (TypeError, ValueError, AttributeError) as error:
            raise KnowledgeVersionError("version identifiers must be UUID values") from error
        if self.parent_version == self.version_id:
            raise KnowledgeVersionError("parent_version cannot equal version_id")
        object.__setattr__(self, "version", require_text(self.version, "version"))
        object.__setattr__(self, "created_by", require_text(self.created_by, "created_by"))
        object.__setattr__(self, "created_at", require_instant(self.created_at, "created_at"))
        object.__setattr__(self, "hash", require_hash(self.hash))
        if self.object_id is not None and not isinstance(self.object_id, KnowledgeObjectId):
            raise KnowledgeVersionError("object_id must be KnowledgeObjectId")
        try:
            object.__setattr__(self, "status", KnowledgeStatus(self.status))
        except (TypeError, ValueError) as error:
            raise KnowledgeVersionError("status must be KnowledgeStatus") from error
        self._validate_schema()

    @classmethod
    def create(cls, version: str, created_at: datetime, created_by: str, digest: str,
               status: KnowledgeStatus = KnowledgeStatus.ACTIVE,
               parent_version: UUID | None = None, object_id: KnowledgeObjectId | None = None) -> KnowledgeVersion:
        return cls(uuid4(), version, created_at, created_by, digest, status, parent_version, object_id)

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "model": self.model,
                "version_id": str(self.version_id), "parent_version": None if self.parent_version is None else str(self.parent_version),
                "created_at": self.created_at.isoformat(), "created_by": self.created_by, "hash": self.hash,
                "version": self.version, "status": self.status.value, "object_id": primitive(self.object_id)}


__all__ = ["KnowledgeVersion"]
