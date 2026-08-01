"""Dedicated acceptance and defensive suite for SPR-012."""

from dataclasses import FrozenInstanceError, is_dataclass, replace
from datetime import UTC, datetime, timedelta
from types import MappingProxyType
from uuid import UUID, uuid4

import pytest

from cko.core import CKOError, CanonicalRelationshipType
from cko.core.documents import (
    DocumentDescriptor, DocumentFactory, DocumentMetadata, DocumentSource,
    DocumentSourceType, DocumentType,
)
from cko.core.knowledge import (
    KnowledgeContent, KnowledgeMetadata, KnowledgeObjectFactory, KnowledgeObjectId,
    KnowledgeType,
)
from cko.core.relationships import (
    RELATIONSHIP_SCHEMA_VERSION, CanonicalRelationship,
    DeterministicRelationshipSerializer, RelationshipCollection,
    RelationshipConstraint, RelationshipConstraintError, RelationshipConstraintType,
    RelationshipDescriptor, RelationshipDirection, RelationshipDirectionType,
    RelationshipEndpoint, RelationshipError, RelationshipEvidence,
    RelationshipEvidenceError, RelationshipEvidenceType, RelationshipFactory,
    RelationshipFactoryError, RelationshipId, RelationshipIdentity,
    RelationshipIdentityError, RelationshipMetadata, RelationshipQuery,
    RelationshipResult, RelationshipSerializationError, RelationshipStatus,
    RelationshipStrength, RelationshipType, RelationshipValidationError,
    RelationshipValidator, RelationshipVersion, RelationshipWeight,
)
from cko.core.relationships.contracts import (
    deep_freeze, instant, model_sequence, non_negative, parse_instant, primitive,
    probability, strict, text, version,
)


NOW = datetime(2026, 7, 26, 18, 30, tzinfo=UTC)
SOURCE_UUID = UUID("00000000-0000-4000-8000-000000000101")
TARGET_UUID = UUID("00000000-0000-4000-8000-000000000102")


def relationship_models():
    source = RelationshipEndpoint(SOURCE_UUID, "cko.knowledge", "knowledge_object", "1.0.0")
    target = RelationshipEndpoint(TARGET_UUID, "cko.documents", "canonical_document", "1.0.0")
    direction = RelationshipDirection(RelationshipDirectionType.BIDIRECTIONAL, "supporter", "supported")
    constraint = RelationshipConstraint(True, "many_to_many", True, False, True, False)
    evidence = RelationshipEvidence(
        RelationshipEvidenceType.PIPELINE, "curation", "reviewed assertion",
        "relationship-classifier", 0.95, NOW, "reviewer", "pipeline:1", "1.0.0",
    )
    weight = RelationshipWeight(0.8, 0.95, 0.9, 0.85)
    factory = RelationshipFactory(clock=lambda: NOW)
    relationship = factory.create(
        namespace="cko.relationships", source=source, target=target,
        relationship_type=RelationshipType.SUPPORTS, created_by="tester",
        direction=direction, constraint=constraint, evidence=(evidence,),
        weights=(weight,), strength=RelationshipStrength.STRONG,
        source_name="curation", attributes={"review": {"accepted": True}},
        label="supports", description="Explicit supporting evidence",
    )
    collection = factory.create_collection((relationship,), "accepted")
    query = RelationshipQuery(
        (relationship.identity.logical_id,), (SOURCE_UUID,), (TARGET_UUID,),
        (RelationshipType.SUPPORTS,), (RelationshipStatus.ACTIVE,),
        "cko.relationships", 10, 0,
    )
    result = RelationshipResult(query, (relationship,), 1)
    return (
        relationship.identity.logical_id, relationship.identity, source, target,
        relationship.metadata, direction, constraint, evidence, weight,
        relationship.version, relationship.descriptor, relationship, collection,
        query, result,
    )


def test_required_models_are_frozen_slotted_versioned_and_discriminated():
    for value in relationship_models():
        assert is_dataclass(value)
        assert type(value).__dataclass_params__.frozen
        assert hasattr(type(value), "__slots__")
        assert value.schema_version == RELATIONSHIP_SCHEMA_VERSION
        assert value.model == type(value).discriminator
        with pytest.raises((FrozenInstanceError, AttributeError)):
            value.schema_version = "2.0"


def test_all_models_have_deterministic_strict_round_trip():
    serializer = DeterministicRelationshipSerializer()
    for value in relationship_models():
        payload = serializer.serialize(value)
        assert payload == serializer.serialize(value)
        assert serializer.deserialize(payload) == value
        assert payload.startswith(b"{")
        assert b"NaN" not in payload and b"Infinity" not in payload
        assert len(serializer.digest(value)) == 64


def test_factory_identity_deep_free_and_public_api():
    relationship = relationship_models()[11]
    assert CanonicalRelationshipType is RelationshipType
    assert relationship.identity.canonical_id == RelationshipId.canonical(
        relationship.identity.namespace, relationship.identity.semantic_key,
    )
    assert isinstance(relationship.metadata.attributes, MappingProxyType)
    assert isinstance(relationship.metadata.attributes["review"], MappingProxyType)
    with pytest.raises(TypeError):
        relationship.metadata.attributes["x"] = 1
    RelationshipValidator().validate(relationship)


def test_all_official_relationship_types_and_declarative_enums():
    expected = {
        "references", "contains", "contained_by", "derived_from", "derived_into",
        "duplicates", "equivalent_to", "supersedes", "updated_by", "supports",
        "supported_by", "contradicts", "related_to", "depends_on", "required_by",
        "generated_from", "generated_into", "classified_as", "member_of",
        "parent_of", "child_of",
    }
    assert {item.value for item in RelationshipType} == expected
    assert {item.value for item in RelationshipConstraintType} == {
        "uniqueness", "multiplicity", "bidirectionality", "transitivity",
        "symmetry", "reflexivity",
    }


def test_factory_is_exclusive_and_collections_reject_duplicates():
    values = relationship_models()
    relationship = values[11]
    with pytest.raises(RelationshipFactoryError):
        CanonicalRelationship(*(
            relationship.identity, relationship.metadata, relationship.source,
            relationship.target, relationship.descriptor, relationship.version,
        ))
    with pytest.raises(RelationshipFactoryError):
        RelationshipCollection((relationship,))
    with pytest.raises(RelationshipValidationError):
        RelationshipFactory().create_collection((relationship, relationship))
    assert tuple(values[12]) == (relationship,) and len(values[12]) == 1


def test_direction_constraints_and_self_relationship_rules():
    source = relationship_models()[2]
    factory = RelationshipFactory(clock=lambda: NOW)
    with pytest.raises(RelationshipValidationError):
        factory.create(namespace="cko", source=source, target=source,
                       relationship_type=RelationshipType.RELATED_TO, created_by="tester")
    reflexive = factory.create(
        namespace="cko", source=source, target=source,
        relationship_type=RelationshipType.RELATED_TO, created_by="tester",
        constraint=RelationshipConstraint(reflexive=True),
    )
    assert reflexive.source == reflexive.target
    with pytest.raises(RelationshipValidationError):
        factory.create(
            namespace="cko", source=source, target=relationship_models()[3],
            relationship_type=RelationshipType.RELATED_TO, created_by="tester",
            direction=RelationshipDirection(RelationshipDirectionType.BIDIRECTIONAL),
            constraint=RelationshipConstraint(),
        )


def test_evidence_weights_and_constraints_are_optional_declarations():
    empty = RelationshipWeight()
    assert empty.weight is empty.confidence is empty.relevance is empty.probability is None
    assert RelationshipConstraint(transitive=True).transitive
    for field in ("weight", "confidence", "relevance", "probability"):
        with pytest.raises(RelationshipValidationError):
            RelationshipWeight(**{field: float("nan")})
        with pytest.raises(RelationshipValidationError):
            RelationshipWeight(**{field: 1.1})
    with pytest.raises(RelationshipEvidenceError):
        RelationshipEvidence(RelationshipEvidenceType.SOURCE)
    with pytest.raises(RelationshipConstraintError):
        RelationshipConstraint(symmetric=True)


def test_serializer_rejects_unknown_fields_discriminators_schemas_and_noncanonical_json():
    serializer = DeterministicRelationshipSerializer()
    payload = serializer.serialize(relationship_models()[0])
    invalid = (
        payload.replace(b"{", b'{"unknown":1,', 1),
        b'{"model":"unknown","schema_version":"1.0"}',
        b'{"model":"relationship_weight","schema_version":"1.0","weight":NaN,"confidence":null,"relevance":null,"probability":null}',
        b' {"model":"relationship_id","schema_version":"1.0","value":"00000000-0000-4000-8000-000000000101"}',
        b"\xff",
    )
    for item in invalid:
        with pytest.raises(RelationshipSerializationError):
            serializer.deserialize(item)
    with pytest.raises(RelationshipSerializationError):
        serializer.deserialize(1)
    with pytest.raises(RelationshipSerializationError):
        serializer.from_dict({"schema_version": "1.0"})


@pytest.mark.parametrize("call", [
    lambda: RelationshipId("invalid"),
    lambda: RelationshipId(uuid4(), "2.0"),
    lambda: RelationshipIdentity(RelationshipId.new(), RelationshipId.new(), "cko", "key"),
    lambda: RelationshipEndpoint("bad", "cko", "knowledge_object", "1.0.0"),
    lambda: RelationshipEndpoint(uuid4(), "cko", "knowledge_object", "1"),
    lambda: RelationshipMetadata(NOW, NOW - timedelta(seconds=1), "tester"),
    lambda: RelationshipMetadata(NOW, NOW, "tester", "invalid"),
    lambda: RelationshipDirection("invalid"),
    lambda: RelationshipConstraint(multiplicity="invalid"),
    lambda: RelationshipEvidence("invalid", source="x"),
    lambda: RelationshipWeight(weight=-0.1),
    lambda: RelationshipVersion("bad", "1.0.0", NOW, "tester"),
    lambda: RelationshipVersion((identifier := uuid4()), "1.0.0", NOW, "tester", parent_version=identifier),
    lambda: RelationshipDescriptor("invalid", RelationshipDirection(), RelationshipConstraint()),
    lambda: RelationshipQuery(limit=0),
    lambda: RelationshipQuery(offset=-1),
    lambda: RelationshipResult(RelationshipQuery(), (), -1),
])
def test_invalid_atomic_models_are_typed(call):
    with pytest.raises(CKOError):
        call()


def test_validator_rejects_cross_model_mismatches_and_duplicate_evidence():
    relationship = relationship_models()[11]
    factory = RelationshipFactory()
    with pytest.raises(RelationshipValidationError):
        factory.from_parts(
            identity=relationship.identity,
            metadata=replace(relationship.metadata, status=RelationshipStatus.ARCHIVED),
            source=relationship.source, target=relationship.target,
            descriptor=relationship.descriptor, version=relationship.version,
        )
    with pytest.raises(RelationshipValidationError):
        factory.from_parts(
            identity=relationship.identity, metadata=relationship.metadata,
            source=relationship.source, target=relationship.target,
            descriptor=relationship.descriptor, version=relationship.version,
            evidence=(relationship.evidence[0], relationship.evidence[0]),
        )
    wrong_key = "different"
    wrong_identity = RelationshipIdentity(
        relationship.identity.logical_id,
        RelationshipId.canonical(relationship.identity.namespace, wrong_key),
        relationship.identity.namespace,
        wrong_key,
    )
    with pytest.raises(RelationshipValidationError):
        factory.from_parts(
            identity=wrong_identity, metadata=relationship.metadata,
            source=relationship.source, target=relationship.target,
            descriptor=relationship.descriptor, version=relationship.version,
        )


def test_endpoint_adapters_integrate_with_knowledge_and_document_models():
    knowledge = KnowledgeObjectFactory(clock=lambda: NOW).create(
        namespace="cko.knowledge", origin="test", knowledge_type=KnowledgeType.CONCEPT,
        metadata=KnowledgeMetadata(NOW, NOW), content=KnowledgeContent.empty(),
        created_by="tester", logical_id=KnowledgeObjectId.parse(SOURCE_UUID),
    )
    document = DocumentFactory(clock=lambda: NOW).create(
        namespace="cko.documents", metadata=DocumentMetadata(
            "Title", NOW, NOW,
            sources=(DocumentSource(DocumentSourceType.INTERNAL, "source:1", "test"),),
        ),
        descriptor=DocumentDescriptor(DocumentType.REPORT), created_by="tester",
    )
    knowledge_endpoint = RelationshipEndpoint.from_knowledge_object(knowledge)
    document_endpoint = RelationshipEndpoint.from_document(document)
    assert knowledge_endpoint.entity_type == "knowledge_object"
    assert document_endpoint.entity_type == "canonical_document"
    relationship = RelationshipFactory(clock=lambda: NOW).create(
        namespace="cko.relationships", source=knowledge_endpoint, target=document_endpoint,
        relationship_type=RelationshipType.REFERENCES, created_by="tester",
    )
    assert relationship.source.object_id == knowledge.identity.logical_id.value
    with pytest.raises(RelationshipIdentityError):
        RelationshipEndpoint.from_knowledge_object(object())
    with pytest.raises(RelationshipIdentityError):
        RelationshipEndpoint.from_document(object())


def test_contract_helpers_reject_invalid_values_and_preserve_utc():
    assert text(" x ", "x") == "x"
    assert version("1.2.3") == "1.2.3"
    assert instant(NOW, "now").tzinfo is UTC
    assert parse_instant(NOW.isoformat(), "now") == NOW
    assert probability(1, "p") == 1.0
    assert non_negative(0, "n") == 0
    assert primitive({"b": 1, "a": (2,)}) == {"a": [2], "b": 1}
    assert isinstance(deep_freeze({"x": [1]}), MappingProxyType)
    assert model_sequence([], "items", RelationshipId) == ()
    strict({"model": "x", "schema_version": "1.0", "a": 1}, "x", {"a"})
    invalid = (
        lambda: text(" ", "x"), lambda: version("1"),
        lambda: instant(datetime.min, "x"), lambda: parse_instant(1, "x"),
        lambda: probability(True, "x"), lambda: non_negative(True, "x"),
        lambda: deep_freeze(object()), lambda: primitive(object()),
        lambda: model_sequence(object(), "x", RelationshipId),
        lambda: strict({"model": "x", "schema_version": "2.0"}, "x", set()),
    )
    for call in invalid:
        with pytest.raises(CKOError):
            call()


def test_error_hierarchy_and_safe_payload():
    error = RelationshipValidationError("invalid", model="endpoint", details={"field": "id"})
    assert isinstance(error, RelationshipError)
    assert isinstance(error, CKOError)
    assert error.to_dict() == {
        "code": "relationship_validation_error", "details": {"field": "id"},
        "message": "invalid", "model": "endpoint",
    }
    for call in (
        lambda: RelationshipError(""), lambda: RelationshipError("x", code=" "),
        lambda: RelationshipError("x", model=" "),
        lambda: RelationshipError("x", details=object()),
    ):
        with pytest.raises(ValueError):
            call()


def test_additional_defensive_contract_and_model_paths():
    relationship = relationship_models()[11]
    assert str(relationship.identity.logical_id) == str(relationship.identity.logical_id.value)
    with pytest.raises(RelationshipIdentityError):
        RelationshipId.parse("bad")
    with pytest.raises(RelationshipValidationError):
        RelationshipMetadata(NOW, NOW, "tester", attributes=[])
    with pytest.raises(RelationshipValidationError):
        RelationshipDirection(source_role=" ")
    with pytest.raises(RelationshipValidationError):
        RelationshipVersion(uuid4(), "1.0.0", NOW, "tester", "invalid")
    with pytest.raises(RelationshipValidationError):
        RelationshipDescriptor(RelationshipType.REFERENCES, object(), RelationshipConstraint())
    with pytest.raises(RelationshipValidationError):
        RelationshipDescriptor(RelationshipType.REFERENCES, RelationshipDirection(), object())
    with pytest.raises(RelationshipValidationError):
        RelationshipQuery(source_ids=object())
    with pytest.raises(RelationshipValidationError):
        RelationshipQuery(source_ids=(SOURCE_UUID, SOURCE_UUID))
    with pytest.raises(RelationshipValidationError):
        RelationshipQuery(relationship_types=("invalid",))
    with pytest.raises(RelationshipValidationError):
        RelationshipResult(object(), (), 0)
    with pytest.raises(RelationshipValidationError):
        RelationshipResult(RelationshipQuery(), (relationship,), 0)
    with pytest.raises(RelationshipValidationError):
        RelationshipValidator().validate(object())
    with pytest.raises(RelationshipValidationError):
        deep_freeze({" ": 1})
    with pytest.raises(RelationshipSerializationError):
        parse_instant("invalid", "instant")
    with pytest.raises(RelationshipSerializationError):
        strict([], "model", set())
