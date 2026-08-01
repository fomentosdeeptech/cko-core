"""Mandatory validated creation boundary for canonical documents."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable, Mapping
from uuid import UUID, uuid4

from cko.core.knowledge import (
    KnowledgeCategory, KnowledgeConfidence, KnowledgeContent, KnowledgeMetadata,
    KnowledgeObject, KnowledgeObjectFactory, KnowledgeObjectId, KnowledgeStatus,
    KnowledgeType,
)

from .enums import DocumentStatus
from .errors import DocumentError, DocumentFactoryError
from .identity import DocumentId, DocumentIdentity
from .metadata import DocumentMetadata
from .models import (
    _FACTORY_TOKEN, CanonicalDocument, DocumentCollection, DocumentContentDescriptor,
    DocumentDescriptor, DocumentIntegrity, DocumentRepresentation, DocumentRights,
    DocumentStatistics, DocumentVersion,
)
from .validator import DocumentValidator


_STATUS_MAP = {
    DocumentStatus.DRAFT: KnowledgeStatus.DRAFT,
    DocumentStatus.ACTIVE: KnowledgeStatus.ACTIVE,
    DocumentStatus.REVIEWED: KnowledgeStatus.REVIEWED,
    DocumentStatus.SUPERSEDED: KnowledgeStatus.SUPERSEDED,
    DocumentStatus.ARCHIVED: KnowledgeStatus.ARCHIVED,
}


class DocumentFactory:
    """Create document aggregates while preserving Knowledge Object contracts."""

    def __init__(
        self,
        validator: DocumentValidator | None = None,
        knowledge_factory: KnowledgeObjectFactory | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator = validator or DocumentValidator()
        self._clock = clock or (lambda: datetime.now(UTC))
        self._knowledge_factory = knowledge_factory or KnowledgeObjectFactory(clock=self._clock)

    def create(
        self,
        *,
        namespace: str,
        metadata: DocumentMetadata,
        descriptor: DocumentDescriptor,
        created_by: str,
        content: DocumentContentDescriptor | None = None,
        logical_id: DocumentId | None = None,
        physical_ids: tuple[str, ...] = (),
        external_ids: Mapping[str, str] | None = None,
        representations: tuple[DocumentRepresentation, ...] = (),
        statistics: DocumentStatistics | None = None,
        integrity: DocumentIntegrity | None = None,
        rights: DocumentRights | None = None,
        parent_version: UUID | None = None,
    ) -> CanonicalDocument:
        try:
            if not isinstance(metadata, DocumentMetadata) or not isinstance(descriptor, DocumentDescriptor):
                raise DocumentFactoryError("metadata and descriptor are required document models")
            selected_id = logical_id or DocumentId.new()
            knowledge_id = KnowledgeObjectId.parse(str(selected_id))
            identity = DocumentIdentity(
                selected_id,
                DocumentId.canonical(namespace, selected_id),
                knowledge_id,
                namespace,
                physical_ids,
                external_ids or {},
            )
            knowledge_metadata = KnowledgeMetadata(
                created_at=metadata.created_at,
                modified_at=metadata.modified_at,
                author=None if metadata.author is None else metadata.author.name,
                creator=metadata.creator,
                published_at=metadata.published_at,
                language=None if metadata.language is None else metadata.language.code.value,
                domain=metadata.domain,
                category=KnowledgeCategory.OTHER,
                tags=metadata.tags,
                keywords=metadata.keywords,
                confidence=(KnowledgeConfidence.UNKNOWN if metadata.confidence is None
                            else KnowledgeConfidence.VERIFIED),
                confidence_score=metadata.confidence,
                source=metadata.sources[0].identifier if metadata.sources else None,
                license=metadata.license,
            )
            origin = metadata.sources[0].origin if metadata.sources else "document"
            knowledge_object = self._knowledge_factory.create(
                namespace=namespace,
                origin=origin,
                knowledge_type=KnowledgeType.COMPOSITE,
                metadata=knowledge_metadata,
                content=KnowledgeContent.empty(),
                created_by=created_by,
                version=metadata.version,
                status=_STATUS_MAP[descriptor.status],
                logical_id=knowledge_id,
                external_id=next(iter((external_ids or {}).values()), None),
            )
            checksum = integrity.sha256 if integrity is not None else metadata.checksum
            version = DocumentVersion(
                uuid4(), metadata.version, self._clock(), created_by,
                descriptor.status, parent_version, checksum,
            )
            return self.from_parts(
                identity=identity,
                metadata=metadata,
                descriptor=descriptor,
                content=content or DocumentContentDescriptor(),
                knowledge_object=knowledge_object,
                representations=representations,
                versions=(version,),
                statistics=statistics,
                integrity=integrity,
                rights=rights,
            )
        except DocumentError:
            raise
        except Exception as error:
            raise DocumentFactoryError("canonical document creation failed") from error

    def from_parts(
        self,
        *,
        identity: DocumentIdentity,
        metadata: DocumentMetadata,
        descriptor: DocumentDescriptor,
        content: DocumentContentDescriptor,
        knowledge_object: KnowledgeObject,
        representations: tuple[DocumentRepresentation, ...] = (),
        versions: tuple[DocumentVersion, ...] = (),
        statistics: DocumentStatistics | None = None,
        integrity: DocumentIntegrity | None = None,
        rights: DocumentRights | None = None,
    ) -> CanonicalDocument:
        value = CanonicalDocument(
            identity, metadata, descriptor, content, knowledge_object,
            representations, versions, statistics, integrity, rights,
            _factory_token=_FACTORY_TOKEN,
        )
        self._validator.validate(value)
        return value

    def create_collection(
        self, documents: tuple[CanonicalDocument, ...] = (), name: str | None = None,
    ) -> DocumentCollection:
        value = DocumentCollection(documents, name, _factory_token=_FACTORY_TOKEN)
        self._validator.validate(value)
        return value


__all__ = ["DocumentFactory"]
