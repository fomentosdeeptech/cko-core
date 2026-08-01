"""Dedicated acceptance and regression suite for SPR-010."""

from dataclasses import FrozenInstanceError, is_dataclass
from datetime import UTC, datetime, timedelta
from types import MappingProxyType
from uuid import uuid4
from enum import Enum

import pytest

from cko.core import (
    CKOError, KNOWLEDGE_SCHEMA_VERSION, DeterministicKnowledgeSerializer,
    KnowledgeAttribute, KnowledgeCategory, KnowledgeClassification, KnowledgeCollection,
    KnowledgeConfidence, KnowledgeContent, KnowledgeContentKind, KnowledgeContext,
    KnowledgeDescriptor, KnowledgeFactoryError, KnowledgeMetadata, KnowledgeObject,
    KnowledgeObjectFactory, KnowledgeObjectId, KnowledgeObjectIdentity,
    KnowledgeObjectValidator, KnowledgeProvenance, KnowledgeQuery, KnowledgeReference,
    KnowledgeRelationship, KnowledgeResult, KnowledgeSerializationError, KnowledgeSnapshot,
    KnowledgeSourceType, KnowledgeStatus, KnowledgeType, KnowledgeValidationError,
    KnowledgeVersion, RelationshipType,
)
from cko.core.knowledge.contracts import (
    deep_freeze, model_sequence, parse_instant, primitive, require_hash,
    require_instant, require_probability, require_text, restore_primitive,
    strict_envelope, unique_texts,
)


NOW = datetime(2026, 7, 26, 18, 30, tzinfo=UTC)


def models():
    attribute = KnowledgeAttribute("quality", {"scores": [1, 0.5], "approved": True})
    provenance = KnowledgeProvenance("cko", "curation", "normalize", "source:A", NOW,
                                     "1.0.0", KnowledgeSourceType.IMPORTED)
    classification = KnowledgeClassification("science", KnowledgeCategory.SCIENTIFIC,
                                             "biology", "internal-v1", "curator", 0.9)
    metadata = KnowledgeMetadata(
        NOW, NOW, "Author", "Creator", NOW, "pt-BR", "science",
        KnowledgeCategory.SCIENTIFIC, ("canonical", "verified"), ("knowledge",),
        KnowledgeConfidence.VERIFIED, 0.98, "source:A", "CC-BY-4.0",
        (provenance,), (classification,), (attribute,),
    )
    source_id = KnowledgeObjectId.parse("00000000-0000-4000-8000-000000000001")
    target_id = KnowledgeObjectId.parse("00000000-0000-4000-8000-000000000002")
    reference = KnowledgeReference("ref-1", "cko:target", "Target", target_id, (attribute,))
    content = KnowledgeContent(KnowledgeContentKind.STRUCTURE,
                               {"title": "Conhecimento", "values": [1, 2]},
                               references=(reference,))
    relationship = KnowledgeRelationship(
        uuid4(), source_id, target_id, RelationshipType.REFERENCES, NOW, 0.95, (attribute,)
    )
    context = KnowledgeContext("validity", {"region": "BR"}, NOW, NOW + timedelta(days=1))
    factory = KnowledgeObjectFactory(clock=lambda: NOW)
    obj = factory.create(namespace="cko.science", origin="curation",
                         knowledge_type=KnowledgeType.CONCEPT, metadata=metadata,
                         content=content, created_by="tester", logical_id=source_id,
                         external_id="external-1", relationships=(relationship,), contexts=(context,))
    descriptor = KnowledgeDescriptor(obj.identity, "Canonical object", "summary",
                                     KnowledgeStatus.ACTIVE, ("canonical",))
    query = KnowledgeQuery((source_id,), (KnowledgeType.CONCEPT,),
                           (KnowledgeStatus.ACTIVE,), ("science",), ("canonical",), 10, 0)
    collection = KnowledgeCollection((obj,), "accepted")
    serializer = DeterministicKnowledgeSerializer(factory)
    snapshot = KnowledgeSnapshot(uuid4(), obj, NOW, serializer.digest(obj))
    result = KnowledgeResult(query, (obj,), 1)
    version = obj.version
    identity = obj.identity
    return (source_id, identity, attribute, reference, provenance, classification, metadata,
            version, relationship, content, context, obj, collection, snapshot, descriptor,
            query, result)


def test_all_required_models_are_frozen_slotted_versioned_and_discriminated():
    for value in models():
        assert is_dataclass(value)
        assert type(value).__dataclass_params__.frozen
        assert hasattr(type(value), "__slots__")
        assert value.schema_version == KNOWLEDGE_SCHEMA_VERSION
        assert value.model == type(value).model_name
        with pytest.raises((FrozenInstanceError, AttributeError)):
            value.schema_version = "2.0"


def test_all_models_have_deterministic_strict_round_trip():
    serializer = DeterministicKnowledgeSerializer()
    for value in models():
        payload = serializer.serialize(value)
        assert payload == serializer.serialize(value)
        assert serializer.deserialize(payload) == value
        assert payload.decode("utf-8").startswith("{")
        assert b"NaN" not in payload and b"Infinity" not in payload


def test_deep_free_and_binary_round_trip():
    content = KnowledgeContent(KnowledgeContentKind.JSON, {"nested": [b"abc", {"x": 1}]})
    assert isinstance(content.value, MappingProxyType)
    assert isinstance(content.value["nested"], tuple)
    serializer = DeterministicKnowledgeSerializer()
    assert serializer.deserialize(serializer.serialize(content)) == content
    with pytest.raises(TypeError):
        content.value["new"] = 1


@pytest.mark.parametrize("content", [
    KnowledgeContent.empty(),
    KnowledgeContent(KnowledgeContentKind.TEXT, "text"),
    KnowledgeContent(KnowledgeContentKind.BYTES, b"bytes"),
    KnowledgeContent(KnowledgeContentKind.FRAGMENTS, fragments=(KnowledgeContent.empty(),)),
    KnowledgeContent(KnowledgeContentKind.REFERENCES,
                     references=(KnowledgeReference("r", "target"),)),
    KnowledgeContent(KnowledgeContentKind.DERIVED,
                     derived_from=(KnowledgeObjectId.new(),)),
])
def test_content_forms_round_trip(content):
    serializer = DeterministicKnowledgeSerializer()
    assert serializer.deserialize(serializer.serialize(content)) == content


def test_factory_is_exclusive_and_validates_hash_identity_and_utc():
    source_id, identity, _, _, _, _, metadata, version, _, content, _, _, *_ = models()
    with pytest.raises(KnowledgeFactoryError):
        KnowledgeObject(identity, metadata, content, version)
    assert identity.canonical_id == KnowledgeObjectId.canonical(identity.namespace, source_id)
    assert version.hash == KnowledgeObjectFactory.content_digest(content)
    assert metadata.created_at.tzinfo is UTC
    KnowledgeObjectValidator().validate(models()[11])


def test_strict_serializer_rejects_unknown_noncanonical_and_invalid_json():
    serializer = DeterministicKnowledgeSerializer()
    payload = serializer.serialize(models()[0])
    with pytest.raises(KnowledgeSerializationError):
        serializer.deserialize(payload.replace(b"{", b'{"unknown":1,', 1))
    with pytest.raises(KnowledgeSerializationError):
        serializer.deserialize(b'{"model":"unknown","schema_version":"1.0"}')
    with pytest.raises(KnowledgeSerializationError):
        serializer.deserialize(b'{"value":NaN}')
    with pytest.raises(KnowledgeSerializationError):
        serializer.deserialize(b' {"model":"knowledge_object_id","schema_version":"1.0","value":"00000000-0000-4000-8000-000000000001"}')
    with pytest.raises(KnowledgeSerializationError):
        serializer.deserialize(b"\xff")


@pytest.mark.parametrize("call", [
    lambda: KnowledgeContent(KnowledgeContentKind.EMPTY, "x"),
    lambda: KnowledgeContent(KnowledgeContentKind.TEXT, 1),
    lambda: KnowledgeContent(KnowledgeContentKind.BYTES, "x"),
    lambda: KnowledgeContent(KnowledgeContentKind.FRAGMENTS),
    lambda: KnowledgeContent(KnowledgeContentKind.REFERENCES),
    lambda: KnowledgeContent(KnowledgeContentKind.DERIVED),
    lambda: KnowledgeMetadata(NOW, NOW - timedelta(seconds=1)),
    lambda: KnowledgeMetadata(NOW, NOW, tags=("x", "x")),
    lambda: KnowledgeClassification("d", KnowledgeCategory.GENERAL, confidence=1.1),
    lambda: KnowledgeRelationship(uuid4(), KnowledgeObjectId.new(), KnowledgeObjectId.new(),
                                  RelationshipType.RELATED_TO, datetime.min),
    lambda: KnowledgeQuery(limit=0),
    lambda: KnowledgeQuery(offset=-1),
    lambda: KnowledgeResult(KnowledgeQuery(), (), -1),
])
def test_invalid_models_are_rejected(call):
    with pytest.raises(CKOError):
        call()


def test_relationship_duplicates_references_and_collections_are_validated():
    values = models(); obj = values[11]; relation = values[8]
    with pytest.raises(KnowledgeValidationError):
        KnowledgeObjectFactory().from_parts(identity=obj.identity, metadata=obj.metadata,
            content=obj.content, version=obj.version, relationships=(relation, relation))
    with pytest.raises(KnowledgeValidationError):
        KnowledgeCollection((obj, obj))
    self_ref = KnowledgeReference("self", "self", target_object_id=obj.identity.logical_id)
    content = KnowledgeContent(KnowledgeContentKind.REFERENCES, references=(self_ref,))
    with pytest.raises(KnowledgeValidationError):
        KnowledgeObjectFactory(clock=lambda: NOW).create(
            namespace="cko", origin="test", knowledge_type=KnowledgeType.TEXT,
            metadata=KnowledgeMetadata(NOW, NOW), content=content, created_by="test",
            logical_id=obj.identity.logical_id)


def test_exception_hierarchy_and_safe_payload():
    error = KnowledgeValidationError("invalid", model="knowledge_object", details={"field": "id"})
    assert isinstance(error, CKOError)
    assert error.to_dict()["code"] == "knowledge_validation_error"
    assert error.to_dict()["details"] == {"field": "id"}


def test_contract_defensive_validation_paths():
    class LocalEnum(str, Enum):
        VALUE = "value"

    assert require_probability(None, "p") is None
    assert deep_freeze(LocalEnum.VALUE) is LocalEnum.VALUE
    assert deep_freeze(models()[0]) == models()[0]
    assert primitive(NOW).endswith("+00:00")
    assert primitive((1, 2)) == [1, 2]
    for call in (
        lambda: require_text(" ", "text"),
        lambda: require_instant(datetime.min, "instant"),
        lambda: parse_instant(1, "instant"),
        lambda: parse_instant("invalid", "instant"),
        lambda: require_probability(True, "p"),
        lambda: require_hash("bad"),
        lambda: deep_freeze(float("nan")),
        lambda: deep_freeze({1: "bad"}),
        lambda: deep_freeze(object()),
        lambda: primitive(float("inf")),
        lambda: primitive(object()),
        lambda: restore_primitive({"$binary": "abc", "$encoding": "wrong"}),
        lambda: restore_primitive({"$binary": "%%%", "$encoding": "base64"}),
        lambda: restore_primitive(float("nan")),
        lambda: restore_primitive(object()),
        lambda: strict_envelope([], "x", set()),
        lambda: strict_envelope({"model": "y", "schema_version": "1.0"}, "x", set()),
        lambda: strict_envelope({"model": "x", "schema_version": "2.0"}, "x", set()),
        lambda: model_sequence("bad", "items", KnowledgeAttribute),
        lambda: model_sequence((object(),), "items", KnowledgeAttribute),
        lambda: unique_texts("bad", "items"),
    ):
        with pytest.raises(CKOError):
            call()


def test_identity_metadata_relationship_and_version_defenses():
    source = KnowledgeObjectId.new(); target = KnowledgeObjectId.new()
    assert str(source) == str(source.value)
    relation = KnowledgeRelationship.create(source, target, RelationshipType.RELATED_TO, NOW)
    assert relation.source_id == source
    with pytest.raises(KnowledgeValidationError):
        KnowledgeObjectId("invalid")
    with pytest.raises(KnowledgeValidationError):
        KnowledgeObjectId.canonical("cko", object())
    with pytest.raises(KnowledgeValidationError):
        KnowledgeObjectIdentity(source, target, "origin", "cko", KnowledgeType.TEXT, "1.0.0")
    canonical = KnowledgeObjectId.canonical("cko", source)
    with pytest.raises(KnowledgeValidationError):
        KnowledgeObjectIdentity(source, canonical, "origin", "cko", "invalid", "1.0.0")
    attribute = KnowledgeAttribute("x", 1)
    with pytest.raises(KnowledgeValidationError):
        KnowledgeReference("r", "t", target_object_id=object())
    with pytest.raises(KnowledgeValidationError):
        KnowledgeReference("r", "t", attributes=(attribute, attribute))
    with pytest.raises(KnowledgeValidationError):
        KnowledgeProvenance("o", "p", "g", "s", NOW, "1", "invalid")
    with pytest.raises(KnowledgeValidationError):
        KnowledgeClassification("d", "invalid")
    with pytest.raises(KnowledgeValidationError):
        KnowledgeMetadata(NOW, NOW, category="invalid")
    with pytest.raises(KnowledgeValidationError):
        KnowledgeMetadata(NOW, NOW, attributes=(attribute, attribute))
    with pytest.raises(CKOError):
        KnowledgeRelationship("bad", source, target, RelationshipType.RELATED_TO, NOW)
    with pytest.raises(CKOError):
        KnowledgeRelationship(uuid4(), source, source, RelationshipType.RELATED_TO, NOW)
    with pytest.raises(CKOError):
        KnowledgeRelationship(uuid4(), source, target, "invalid", NOW)
    version_id = uuid4()
    with pytest.raises(CKOError):
        KnowledgeVersion("bad", "1", NOW, "u", "0" * 64, KnowledgeStatus.ACTIVE)
    with pytest.raises(CKOError):
        KnowledgeVersion(version_id, "1", NOW, "u", "0" * 64,
                         KnowledgeStatus.ACTIVE, version_id)
    with pytest.raises(CKOError):
        KnowledgeVersion(version_id, "1", NOW, "u", "0" * 64,
                         KnowledgeStatus.ACTIVE, object_id=object())
    with pytest.raises(CKOError):
        KnowledgeVersion(version_id, "1", NOW, "u", "0" * 64, "invalid")


def test_aggregate_and_service_defensive_paths():
    obj = models()[11]
    assert len(KnowledgeCollection((obj,))) == 1
    assert tuple(KnowledgeCollection((obj,))) == (obj,)
    with pytest.raises(KnowledgeValidationError):
        KnowledgeContext("x", [])
    with pytest.raises(KnowledgeValidationError):
        KnowledgeContext("x", {}, NOW, NOW - timedelta(seconds=1))
    with pytest.raises(KnowledgeValidationError):
        KnowledgeSnapshot("bad", obj, NOW, "0" * 64)
    with pytest.raises(KnowledgeValidationError):
        KnowledgeSnapshot(uuid4(), object(), NOW, "0" * 64)
    with pytest.raises(KnowledgeValidationError):
        KnowledgeSnapshot(uuid4(), obj, NOW, "0" * 64)
    with pytest.raises(KnowledgeValidationError):
        KnowledgeDescriptor(object(), "title")
    with pytest.raises(KnowledgeValidationError):
        KnowledgeDescriptor(obj.identity, "title", status="invalid")
    with pytest.raises(KnowledgeValidationError):
        KnowledgeQuery(knowledge_types=("invalid",))
    with pytest.raises(KnowledgeValidationError):
        KnowledgeResult(object(), (), 0)
    with pytest.raises(KnowledgeValidationError):
        KnowledgeObjectValidator().validate(object())
    KnowledgeObjectValidator().validate(KnowledgeCollection((obj,)))
    with pytest.raises(KnowledgeFactoryError):
        KnowledgeObjectFactory.content_digest(object())
    with pytest.raises(ValueError):
        KnowledgeValidationError("")
    with pytest.raises(ValueError):
        KnowledgeValidationError("x", code=" ")
    with pytest.raises(ValueError):
        KnowledgeValidationError("x", model=" ")
    with pytest.raises(ValueError):
        KnowledgeValidationError("x", details=[])
