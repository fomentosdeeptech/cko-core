"""Strict deterministic UTF-8 JSON serialization for all knowledge models."""

from __future__ import annotations

import hashlib
import json
from typing import Mapping
from uuid import UUID

from .contracts import SerializableKnowledgeModel, parse_instant, restore_primitive, strict_envelope
from .enums import (KnowledgeCategory, KnowledgeConfidence, KnowledgeContentKind,
                    KnowledgeSourceType, KnowledgeStatus, KnowledgeType, RelationshipType)
from .errors import KnowledgeSerializationError
from .factory import KnowledgeObjectFactory
from .identity import KnowledgeObjectId, KnowledgeObjectIdentity
from .metadata import (KnowledgeAttribute, KnowledgeClassification, KnowledgeMetadata,
                       KnowledgeProvenance, KnowledgeReference)
from .models import (KnowledgeCollection, KnowledgeContent, KnowledgeContext, KnowledgeDescriptor,
                     KnowledgeObject, KnowledgeQuery, KnowledgeResult, KnowledgeSnapshot)
from .relationships import KnowledgeRelationship
from .validator import KnowledgeObjectValidator
from .versioning import KnowledgeVersion


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping): raise KnowledgeSerializationError(f"{name} must be an object")
    return value


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list): raise KnowledgeSerializationError(f"{name} must be an array")
    return value


class DeterministicKnowledgeSerializer:
    """Serialize, deserialize, validate, and canonicalize closed model envelopes."""

    def __init__(self, factory: KnowledgeObjectFactory | None = None,
                 validator: KnowledgeObjectValidator | None = None) -> None:
        self._validator = validator or KnowledgeObjectValidator()
        self._factory = factory or KnowledgeObjectFactory(self._validator)

    def serialize(self, value: SerializableKnowledgeModel) -> bytes:
        self._validator.validate(value)
        try:
            return json.dumps(value.to_dict(), ensure_ascii=False, allow_nan=False,
                              sort_keys=True, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError, UnicodeError) as error:
            raise KnowledgeSerializationError("knowledge serialization failed") from error

    def deserialize(self, payload: bytes | str) -> SerializableKnowledgeModel:
        try:
            text = payload.decode("utf-8") if isinstance(payload, bytes) else payload
            if not isinstance(text, str): raise TypeError
            decoded = json.loads(text, parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
        except (TypeError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
            raise KnowledgeSerializationError("payload must be strict UTF-8 JSON") from error
        value = self.from_dict(_mapping(decoded, "payload"))
        if self.serialize(value).decode("utf-8") != text:
            raise KnowledgeSerializationError("payload is not canonical JSON")
        return value

    def digest(self, value: SerializableKnowledgeModel) -> str:
        return hashlib.sha256(self.serialize(value)).hexdigest()

    def from_dict(self, p: Mapping[str, object]) -> SerializableKnowledgeModel:
        model = p.get("model")
        if not isinstance(model, str): raise KnowledgeSerializationError("model discriminator is required")
        d = lambda x: self.from_dict(_mapping(x, "nested model"))
        if model == "knowledge_object_id":
            q=strict_envelope(p,model,{"value"}); return KnowledgeObjectId.parse(q["value"])  # type: ignore[arg-type]
        if model == "knowledge_object_identity":
            q=strict_envelope(p,model,{"logical_id","canonical_id","external_id","origin","namespace","knowledge_type","version"})
            return KnowledgeObjectIdentity(d(q["logical_id"]),d(q["canonical_id"]),q["origin"],q["namespace"],KnowledgeType(q["knowledge_type"]),q["version"],q["external_id"])  # type: ignore[arg-type]
        if model == "knowledge_attribute":
            q=strict_envelope(p,model,{"name","value"}); return KnowledgeAttribute(q["name"],restore_primitive(q["value"]))  # type: ignore[arg-type]
        if model == "knowledge_reference":
            q=strict_envelope(p,model,{"reference_id","target","title","target_object_id","attributes"}); return KnowledgeReference(q["reference_id"],q["target"],q["title"],None if q["target_object_id"] is None else d(q["target_object_id"]),tuple(d(x) for x in _list(q["attributes"],"attributes")))  # type: ignore[arg-type]
        if model == "knowledge_provenance":
            q=strict_envelope(p,model,{"origin","pipeline","generating_process","original_source","timestamp","pipeline_version","source_type"}); return KnowledgeProvenance(q["origin"],q["pipeline"],q["generating_process"],q["original_source"],parse_instant(q["timestamp"],"timestamp"),q["pipeline_version"],KnowledgeSourceType(q["source_type"]))  # type: ignore[arg-type]
        if model == "knowledge_classification":
            q=strict_envelope(p,model,{"domain","category","subcategory","taxonomy","origin","confidence"}); return KnowledgeClassification(q["domain"],KnowledgeCategory(q["category"]),q["subcategory"],q["taxonomy"],q["origin"],q["confidence"])  # type: ignore[arg-type]
        if model == "knowledge_metadata":
            q=strict_envelope(p,model,{"author","creator","created_at","modified_at","published_at","language","domain","category","tags","keywords","confidence","confidence_score","source","license","provenances","classifications","attributes"})
            return KnowledgeMetadata(parse_instant(q["created_at"],"created_at"),parse_instant(q["modified_at"],"modified_at"),q["author"],q["creator"],None if q["published_at"] is None else parse_instant(q["published_at"],"published_at"),q["language"],q["domain"],KnowledgeCategory(q["category"]),tuple(_list(q["tags"],"tags")),tuple(_list(q["keywords"],"keywords")),KnowledgeConfidence(q["confidence"]),q["confidence_score"],q["source"],q["license"],tuple(d(x) for x in _list(q["provenances"],"provenances")),tuple(d(x) for x in _list(q["classifications"],"classifications")),tuple(d(x) for x in _list(q["attributes"],"attributes")))  # type: ignore[arg-type]
        if model == "knowledge_version":
            q=strict_envelope(p,model,{"version_id","parent_version","created_at","created_by","hash","version","status","object_id"}); return KnowledgeVersion(UUID(q["version_id"]),q["version"],parse_instant(q["created_at"],"created_at"),q["created_by"],q["hash"],KnowledgeStatus(q["status"]),None if q["parent_version"] is None else UUID(q["parent_version"]),None if q["object_id"] is None else d(q["object_id"]))  # type: ignore[arg-type]
        if model == "knowledge_relationship":
            q=strict_envelope(p,model,{"relationship_id","source_id","target_id","relationship_type","created_at","confidence","attributes"}); return KnowledgeRelationship(UUID(q["relationship_id"]),d(q["source_id"]),d(q["target_id"]),RelationshipType(q["relationship_type"]),parse_instant(q["created_at"],"created_at"),q["confidence"],tuple(d(x) for x in _list(q["attributes"],"attributes")))  # type: ignore[arg-type]
        if model == "knowledge_content":
            q=strict_envelope(p,model,{"kind","value","fragments","references","derived_from"}); return KnowledgeContent(KnowledgeContentKind(q["kind"]),restore_primitive(q["value"]),tuple(d(x) for x in _list(q["fragments"],"fragments")),tuple(d(x) for x in _list(q["references"],"references")),tuple(d(x) for x in _list(q["derived_from"],"derived_from")))  # type: ignore[arg-type]
        if model == "knowledge_context":
            q=strict_envelope(p,model,{"name","values","valid_from","valid_to"}); return KnowledgeContext(q["name"],restore_primitive(q["values"]),None if q["valid_from"] is None else parse_instant(q["valid_from"],"valid_from"),None if q["valid_to"] is None else parse_instant(q["valid_to"],"valid_to"))  # type: ignore[arg-type]
        if model == "knowledge_object":
            q=strict_envelope(p,model,{"identity","metadata","content","version","relationships","contexts"}); return self._factory.from_parts(identity=d(q["identity"]),metadata=d(q["metadata"]),content=d(q["content"]),version=d(q["version"]),relationships=tuple(d(x) for x in _list(q["relationships"],"relationships")),contexts=tuple(d(x) for x in _list(q["contexts"],"contexts")))  # type: ignore[arg-type]
        if model == "knowledge_collection":
            q=strict_envelope(p,model,{"objects","name"}); return KnowledgeCollection(tuple(d(x) for x in _list(q["objects"],"objects")),q["name"])  # type: ignore[arg-type]
        if model == "knowledge_snapshot":
            q=strict_envelope(p,model,{"snapshot_id","object","captured_at","hash"}); return KnowledgeSnapshot(UUID(q["snapshot_id"]),d(q["object"]),parse_instant(q["captured_at"],"captured_at"),q["hash"])  # type: ignore[arg-type]
        if model == "knowledge_descriptor":
            q=strict_envelope(p,model,{"identity","title","summary","status","tags"}); return KnowledgeDescriptor(d(q["identity"]),q["title"],q["summary"],KnowledgeStatus(q["status"]),tuple(_list(q["tags"],"tags")))  # type: ignore[arg-type]
        if model == "knowledge_query":
            q=strict_envelope(p,model,{"object_ids","knowledge_types","statuses","domains","tags","limit","offset"}); return KnowledgeQuery(tuple(d(x) for x in _list(q["object_ids"],"object_ids")),tuple(KnowledgeType(x) for x in _list(q["knowledge_types"],"knowledge_types")),tuple(KnowledgeStatus(x) for x in _list(q["statuses"],"statuses")),tuple(_list(q["domains"],"domains")),tuple(_list(q["tags"],"tags")),q["limit"],q["offset"])  # type: ignore[arg-type]
        if model == "knowledge_result":
            q=strict_envelope(p,model,{"query","objects","total"}); return KnowledgeResult(d(q["query"]),tuple(d(x) for x in _list(q["objects"],"objects")),q["total"])  # type: ignore[arg-type]
        raise KnowledgeSerializationError(f"unknown model discriminator: {model}")


__all__ = ["DeterministicKnowledgeSerializer"]
