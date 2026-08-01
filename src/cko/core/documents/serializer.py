"""Strict deterministic UTF-8 JSON serialization for document models."""

from __future__ import annotations

import hashlib
import json
from typing import Mapping
from uuid import UUID

from cko.core.knowledge import DeterministicKnowledgeSerializer, KnowledgeObject, KnowledgeObjectId

from .contracts import DocumentModel, parse_instant, strict
from .enums import (
    DocumentFormat, DocumentLanguageCode, DocumentSourceType, DocumentStatus,
    DocumentType, IntegrityStatus,
)
from .errors import DocumentSerializationError
from .factory import DocumentFactory
from .identity import DocumentId, DocumentIdentity
from .metadata import DocumentAuthor, DocumentLanguage, DocumentMetadata, DocumentSource
from .models import (
    CanonicalDocument, DocumentCollection, DocumentContentDescriptor,
    DocumentDescriptor, DocumentIntegrity, DocumentRepresentation, DocumentRights,
    DocumentStatistics, DocumentVersion,
)
from .validator import DocumentValidator


def _object(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise DocumentSerializationError(f"{name} must be an object")
    return value


def _array(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise DocumentSerializationError(f"{name} must be an array")
    return value


class DeterministicDocumentSerializer:
    """Serialize, deserialize, validate, and canonicalize closed envelopes."""

    def __init__(
        self,
        factory: DocumentFactory | None = None,
        validator: DocumentValidator | None = None,
    ) -> None:
        self._validator = validator or DocumentValidator()
        self._factory = factory or DocumentFactory(self._validator)
        self._knowledge = DeterministicKnowledgeSerializer()

    def serialize(self, value: DocumentModel) -> bytes:
        self._validator.validate(value)
        try:
            return json.dumps(
                value.to_dict(), ensure_ascii=False, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError, UnicodeError) as error:
            raise DocumentSerializationError("document serialization failed") from error

    def deserialize(self, payload: bytes | str) -> DocumentModel:
        try:
            value = payload.decode("utf-8") if isinstance(payload, bytes) else payload
            if not isinstance(value, str):
                raise TypeError
            decoded = json.loads(
                value,
                parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
            )
            model = self.from_dict(_object(decoded, "payload"))
        except DocumentSerializationError:
            raise
        except Exception as error:
            raise DocumentSerializationError("payload must be strict document JSON") from error
        if self.serialize(model).decode("utf-8") != value:
            raise DocumentSerializationError("payload is not canonical JSON")
        return model

    def digest(self, value: DocumentModel) -> str:
        return hashlib.sha256(self.serialize(value)).hexdigest()

    def from_dict(self, payload: Mapping[str, object]) -> DocumentModel:
        model = payload.get("model")
        if not isinstance(model, str):
            raise DocumentSerializationError("model discriminator is required")
        nested = lambda value: self.from_dict(_object(value, "nested model"))
        if model == "document_id":
            q = strict(payload, model, {"value"})
            return DocumentId.parse(q["value"])  # type: ignore[arg-type]
        if model == "document_identity":
            q = strict(payload, model, {"logical_id", "document_id", "knowledge_object_id", "namespace", "physical_ids", "external_ids"})
            knowledge_id = self._knowledge.from_dict(_object(q["knowledge_object_id"], "knowledge_object_id"))
            if not isinstance(knowledge_id, KnowledgeObjectId):
                raise DocumentSerializationError("knowledge_object_id has an invalid model")
            return DocumentIdentity(
                nested(q["logical_id"]), nested(q["document_id"]), knowledge_id,
                q["namespace"], tuple(_array(q["physical_ids"], "physical_ids")),
                _object(q["external_ids"], "external_ids"),
            )  # type: ignore[arg-type]
        if model == "document_language":
            q = strict(payload, model, {"code", "locale", "name"})
            return DocumentLanguage(DocumentLanguageCode(q["code"]), q["locale"], q["name"])  # type: ignore[arg-type]
        if model == "document_author":
            q = strict(payload, model, {"name", "identifier", "organization", "role"})
            return DocumentAuthor(q["name"], q["identifier"], q["organization"], q["role"])  # type: ignore[arg-type]
        if model == "document_source":
            q = strict(payload, model, {"source_type", "identifier", "origin", "external_id", "retrieved_at"})
            retrieved = None if q["retrieved_at"] is None else parse_instant(q["retrieved_at"], "retrieved_at")
            return DocumentSource(DocumentSourceType(q["source_type"]), q["identifier"], q["origin"], q["external_id"], retrieved)  # type: ignore[arg-type]
        if model == "document_metadata":
            names = {"title", "created_at", "modified_at", "subtitle", "author", "coauthors", "creator", "editor", "language", "keywords", "tags", "domain", "category", "license", "sources", "checksum", "published_at", "organization", "version", "confidence"}
            q = strict(payload, model, names)
            return DocumentMetadata(
                title=q["title"], created_at=parse_instant(q["created_at"], "created_at"),
                modified_at=parse_instant(q["modified_at"], "modified_at"), subtitle=q["subtitle"],
                author=None if q["author"] is None else nested(q["author"]),
                coauthors=tuple(nested(item) for item in _array(q["coauthors"], "coauthors")),
                creator=q["creator"], editor=q["editor"],
                language=None if q["language"] is None else nested(q["language"]),
                keywords=tuple(_array(q["keywords"], "keywords")), tags=tuple(_array(q["tags"], "tags")),
                domain=q["domain"], category=q["category"], license=q["license"],
                sources=tuple(nested(item) for item in _array(q["sources"], "sources")),
                checksum=q["checksum"],
                published_at=None if q["published_at"] is None else parse_instant(q["published_at"], "published_at"),
                organization=q["organization"], version=q["version"], confidence=q["confidence"],
            )  # type: ignore[arg-type]
        if model == "document_descriptor":
            q = strict(payload, model, {"document_type", "status", "summary"})
            return DocumentDescriptor(DocumentType(q["document_type"]), DocumentStatus(q["status"]), q["summary"])  # type: ignore[arg-type]
        if model == "document_content_descriptor":
            q = strict(payload, model, {"content_type", "fragment_ids", "extraction_ids", "logical_size"})
            return DocumentContentDescriptor(q["content_type"], tuple(_array(q["fragment_ids"], "fragment_ids")), tuple(_array(q["extraction_ids"], "extraction_ids")), q["logical_size"])  # type: ignore[arg-type]
        if model == "document_representation":
            q = strict(payload, model, {"format", "mime_type", "encoding", "extension", "compression", "hash"})
            return DocumentRepresentation(DocumentFormat(q["format"]), q["mime_type"], q["encoding"], q["extension"], q["compression"], q["hash"])  # type: ignore[arg-type]
        if model == "document_version":
            q = strict(payload, model, {"version_id", "version", "created_at", "created_by", "status", "parent_version", "checksum"})
            return DocumentVersion(UUID(q["version_id"]), q["version"], parse_instant(q["created_at"], "created_at"), q["created_by"], DocumentStatus(q["status"]), None if q["parent_version"] is None else UUID(q["parent_version"]), q["checksum"])  # type: ignore[arg-type]
        if model == "document_statistics":
            names = {"pages", "characters", "words", "lines", "tables", "images", "attachments", "links"}
            q = strict(payload, model, names)
            return DocumentStatistics(**{name: q[name] for name in names})  # type: ignore[arg-type]
        if model == "document_integrity":
            q = strict(payload, model, {"sha256", "logical_size", "physical_size", "signature", "is_intact", "status"})
            return DocumentIntegrity(q["sha256"], q["logical_size"], q["physical_size"], q["signature"], q["is_intact"], IntegrityStatus(q["status"]))  # type: ignore[arg-type]
        if model == "document_rights":
            q = strict(payload, model, {"license", "copyright_holder", "access", "expires_at"})
            expires = None if q["expires_at"] is None else parse_instant(q["expires_at"], "expires_at")
            return DocumentRights(q["license"], q["copyright_holder"], q["access"], expires)  # type: ignore[arg-type]
        if model == "canonical_document":
            names = {"identity", "metadata", "descriptor", "content", "knowledge_object", "representations", "versions", "statistics", "integrity", "rights"}
            q = strict(payload, model, names)
            knowledge = self._knowledge.from_dict(_object(q["knowledge_object"], "knowledge_object"))
            if not isinstance(knowledge, KnowledgeObject):
                raise DocumentSerializationError("knowledge_object has an invalid model")
            return self._factory.from_parts(
                identity=nested(q["identity"]), metadata=nested(q["metadata"]),
                descriptor=nested(q["descriptor"]), content=nested(q["content"]),
                knowledge_object=knowledge,
                representations=tuple(nested(item) for item in _array(q["representations"], "representations")),
                versions=tuple(nested(item) for item in _array(q["versions"], "versions")),
                statistics=None if q["statistics"] is None else nested(q["statistics"]),
                integrity=None if q["integrity"] is None else nested(q["integrity"]),
                rights=None if q["rights"] is None else nested(q["rights"]),
            )  # type: ignore[arg-type]
        if model == "document_collection":
            q = strict(payload, model, {"documents", "name"})
            return self._factory.create_collection(
                tuple(nested(item) for item in _array(q["documents"], "documents")), q["name"],
            )  # type: ignore[arg-type]
        raise DocumentSerializationError(f"unknown model discriminator: {model}")


__all__ = ["DeterministicDocumentSerializer"]
