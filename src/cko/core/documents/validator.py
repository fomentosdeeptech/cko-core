"""Structural and aggregate validation for canonical documents."""

from __future__ import annotations

from dataclasses import fields, is_dataclass

from .contracts import DocumentModel
from .errors import DocumentValidationError
from .identity import DocumentId
from .models import CanonicalDocument, DocumentCollection


class DocumentValidator:
    """Validate closed schemas and cross-model document invariants."""

    def validate(self, value: DocumentModel) -> None:
        if not isinstance(value, DocumentModel) or not is_dataclass(value):
            raise DocumentValidationError("value must be a canonical document dataclass")
        value._validate_schema()
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen or not hasattr(type(value), "__slots__"):
            raise DocumentValidationError("document models must be frozen and slotted")
        if value.model != type(value).discriminator:
            raise DocumentValidationError("invalid model discriminator")
        for item in fields(value):
            nested = getattr(value, item.name)
            if isinstance(nested, DocumentModel):
                self.validate(nested)
            elif isinstance(nested, tuple):
                for member in nested:
                    if isinstance(member, DocumentModel):
                        self.validate(member)
        if isinstance(value, CanonicalDocument):
            self._validate_document(value)
        elif isinstance(value, DocumentCollection):
            for document in value.documents:
                self._validate_document(document)

    def _validate_document(self, value: CanonicalDocument) -> None:
        knowledge_identity = value.knowledge_object.identity
        if knowledge_identity.logical_id != value.identity.knowledge_object_id:
            raise DocumentValidationError("Knowledge Object and document logical identities differ")
        if knowledge_identity.namespace != value.identity.namespace:
            raise DocumentValidationError("Knowledge Object and document namespaces differ")
        if value.knowledge_object.version.version != value.metadata.version:
            raise DocumentValidationError("Knowledge Object and document versions differ")
        if not value.metadata.sources:
            raise DocumentValidationError("a canonical document requires at least one source")
        representation_keys = tuple(
            (item.format, item.mime_type, item.extension, item.hash)
            for item in value.representations
        )
        if len(representation_keys) != len(set(representation_keys)):
            raise DocumentValidationError("document representations must be unique")
        version_ids = tuple(item.version_id for item in value.versions)
        version_names = tuple(item.version for item in value.versions)
        if len(version_ids) != len(set(version_ids)) or len(version_names) != len(set(version_names)):
            raise DocumentValidationError("document versions must be unique")
        if not value.versions or value.metadata.version != value.versions[-1].version:
            raise DocumentValidationError("last document version must match metadata version")
        if value.metadata.checksum is not None and value.integrity is not None:
            if value.metadata.checksum != value.integrity.sha256:
                raise DocumentValidationError("metadata checksum and integrity SHA-256 differ")
        if value.content.logical_size is not None and value.integrity is not None:
            if value.integrity.logical_size is not None and value.content.logical_size != value.integrity.logical_size:
                raise DocumentValidationError("content and integrity logical sizes differ")
        physical_ids = value.identity.physical_ids
        hashes = tuple(item.hash for item in value.representations if item.hash is not None)
        if physical_ids and not value.representations:
            raise DocumentValidationError("physical identities require representations")
        if len(hashes) != len(set(hashes)):
            raise DocumentValidationError("representation hashes must be unique")
        expected = DocumentId.canonical(value.identity.namespace, value.identity.logical_id)
        if value.identity.document_id != expected:
            raise DocumentValidationError("invalid canonical document identity")


__all__ = ["DocumentValidator"]
