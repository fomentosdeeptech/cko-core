"""Exclusive validated construction path for Knowledge Objects."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Callable
from uuid import UUID

from .contracts import primitive
from .enums import KnowledgeStatus, KnowledgeType
from .errors import KnowledgeFactoryError
from .identity import KnowledgeObjectId, KnowledgeObjectIdentity
from .metadata import KnowledgeMetadata
from .models import (_FACTORY_TOKEN, KnowledgeContent, KnowledgeContext, KnowledgeObject)
from .relationships import KnowledgeRelationship
from .validator import KnowledgeObjectValidator
from .versioning import KnowledgeVersion


class KnowledgeObjectFactory:
    """Create every KnowledgeObject through one validation boundary."""

    def __init__(self, validator: KnowledgeObjectValidator | None = None,
                 clock: Callable[[], datetime] | None = None) -> None:
        self._validator = validator or KnowledgeObjectValidator()
        self._clock = clock or (lambda: datetime.now(UTC))

    def create(self, *, namespace: str, origin: str, knowledge_type: KnowledgeType,
               metadata: KnowledgeMetadata, content: KnowledgeContent, created_by: str,
               version: str = "1.0.0", status: KnowledgeStatus = KnowledgeStatus.ACTIVE,
               logical_id: KnowledgeObjectId | None = None, external_id: str | None = None,
               parent_version: UUID | None = None,
               relationships: tuple[KnowledgeRelationship, ...] = (),
               contexts: tuple[KnowledgeContext, ...] = ()) -> KnowledgeObject:
        try:
            selected_id = logical_id or KnowledgeObjectId.new()
            identity = KnowledgeObjectIdentity(selected_id, KnowledgeObjectId.canonical(namespace, selected_id),
                                               origin, namespace, knowledge_type, version, external_id)
            digest = self.content_digest(content)
            version_model = KnowledgeVersion.create(version, self._clock(), created_by, digest, status,
                                                     parent_version, selected_id)
            return self.from_parts(identity=identity, metadata=metadata, content=content,
                                   version=version_model, relationships=relationships, contexts=contexts)
        except KnowledgeFactoryError:
            raise
        except Exception as error:
            from .errors import KnowledgeError
            if isinstance(error, KnowledgeError):
                raise
            raise KnowledgeFactoryError("Knowledge Object creation failed") from error

    def from_parts(self, *, identity: KnowledgeObjectIdentity, metadata: KnowledgeMetadata,
                   content: KnowledgeContent, version: KnowledgeVersion,
                   relationships: tuple[KnowledgeRelationship, ...] = (),
                   contexts: tuple[KnowledgeContext, ...] = ()) -> KnowledgeObject:
        value = KnowledgeObject(identity, metadata, content, version, relationships, contexts,
                                _factory_token=_FACTORY_TOKEN)
        self._validator.validate(value)
        return value

    @staticmethod
    def content_digest(content: KnowledgeContent) -> str:
        if not isinstance(content, KnowledgeContent):
            raise KnowledgeFactoryError("content must be KnowledgeContent")
        encoded = json.dumps(primitive(content), ensure_ascii=False, allow_nan=False,
                             sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


__all__ = ["KnowledgeObjectFactory"]
