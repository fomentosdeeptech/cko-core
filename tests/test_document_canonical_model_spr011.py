"""Dedicated acceptance and regression suite for SPR-011."""

from dataclasses import FrozenInstanceError, is_dataclass
from datetime import UTC, datetime, timedelta
from types import MappingProxyType
from uuid import uuid4

import pytest

from cko.core import CKOError, DocumentCanonicalModel
from cko.core.knowledge import KnowledgeObjectId
from cko.core.documents import (
    DOCUMENT_SCHEMA_VERSION, CanonicalDocument, DeterministicDocumentSerializer,
    DocumentAuthor, DocumentCollection, DocumentContentDescriptor, DocumentDescriptor,
    DocumentFactory, DocumentFactoryError, DocumentFormat, DocumentId, DocumentIdentity,
    DocumentIntegrity, DocumentLanguage, DocumentLanguageCode, DocumentMetadata,
    DocumentRepresentation, DocumentRights, DocumentSerializationError, DocumentSource,
    DocumentSourceType, DocumentStatistics, DocumentStatus, DocumentType,
    DocumentValidationError, DocumentValidator, DocumentVersion, IntegrityStatus,
)
from cko.core.documents.contracts import (
    deep_freeze, instant, model_sequence, non_negative, parse_instant, primitive,
    probability, sha256, strict, text, unique_texts,
)


NOW = datetime(2026, 7, 26, 18, 30, tzinfo=UTC)


def document_models():
    author = DocumentAuthor("Ana", "orcid:1", "CKO", "author")
    coauthor = DocumentAuthor("Bruno", "orcid:2", "CKO", "coauthor")
    language = DocumentLanguage(DocumentLanguageCode.PORTUGUESE, "pt-BR", "Português")
    source = DocumentSource(DocumentSourceType.INTERNAL, "source:1", "curation", "ext:1", NOW)
    integrity = DocumentIntegrity(
        "a" * 64, 100, 120, "signature", True, IntegrityStatus.VERIFIED,
    )
    metadata = DocumentMetadata(
        "Canonical title", NOW, NOW, "Subtitle", author, (coauthor,), "Creator", "Editor",
        language, ("document", "canonical"), ("tag",), "science", "report",
        "CC-BY-4.0", (source,), "a" * 64, NOW, "CKO", "1.0.0", 0.98,
    )
    descriptor = DocumentDescriptor(DocumentType.REPORT, DocumentStatus.ACTIVE, "Summary")
    content = DocumentContentDescriptor("text", ("fragment:1",), ("extraction:future",), 100)
    representation = DocumentRepresentation(
        DocumentFormat.PDF, "application/pdf", "binary", ".PDF", "none", "b" * 64,
    )
    statistics = DocumentStatistics(2, 100, 20, 5, 1, 1, 0, 2)
    rights = DocumentRights("CC-BY-4.0", "CKO", "public", NOW + timedelta(days=365))
    factory = DocumentFactory(clock=lambda: NOW)
    document = factory.create(
        namespace="cko.documents", metadata=metadata, descriptor=descriptor,
        created_by="tester", content=content, physical_ids=("physical:1",),
        external_ids={"doi": "10.1/example"}, representations=(representation,),
        statistics=statistics, integrity=integrity, rights=rights,
    )
    collection = factory.create_collection((document,), "accepted")
    return (
        document.identity.logical_id, document.identity, author, coauthor, language, source,
        metadata, descriptor, content, representation, document.versions[0], statistics,
        integrity, rights, document, collection,
    )


def test_required_models_are_frozen_slotted_versioned_and_discriminated():
    for value in document_models():
        assert is_dataclass(value)
        assert type(value).__dataclass_params__.frozen
        assert hasattr(type(value), "__slots__")
        assert value.schema_version == DOCUMENT_SCHEMA_VERSION
        assert value.model == type(value).discriminator
        with pytest.raises((FrozenInstanceError, AttributeError)):
            value.schema_version = "2.0"


def test_all_models_have_deterministic_strict_round_trip():
    serializer = DeterministicDocumentSerializer()
    for value in document_models():
        payload = serializer.serialize(value)
        assert payload == serializer.serialize(value)
        assert serializer.deserialize(payload) == value
        assert payload.decode("utf-8").startswith("{")
        assert b"NaN" not in payload and b"Infinity" not in payload


def test_document_specializes_knowledge_object_without_format_logic():
    document = document_models()[14]
    assert isinstance(document, CanonicalDocument)
    assert DocumentCanonicalModel is CanonicalDocument
    assert str(document.identity.logical_id) == str(document.knowledge_object.identity.logical_id)
    assert document.knowledge_object.identity.namespace == "cko.documents"
    assert document.representations[0].extension == "pdf"
    assert not hasattr(document.representations[0], "content")
    assert not hasattr(document, "file")


def test_all_official_representation_formats_are_available():
    expected = {
        "pdf", "docx", "txt", "rtf", "odt", "xlsx", "ods", "csv", "pptx", "odp",
        "html", "xml", "json", "markdown", "email", "image", "ocr",
        "audio_transcript", "video_transcript", "other",
    }
    assert {item.value for item in DocumentFormat} == expected


def test_identity_separates_logical_document_physical_and_external_values():
    identity = document_models()[1]
    assert identity.logical_id != identity.document_id
    assert identity.physical_ids == ("physical:1",)
    assert isinstance(identity.external_ids, MappingProxyType)
    with pytest.raises(TypeError):
        identity.external_ids["new"] = "value"


def test_factory_is_exclusive_and_collection_is_validated():
    values = document_models()
    document = values[14]
    with pytest.raises(DocumentFactoryError):
        CanonicalDocument(
            document.identity, document.metadata, document.descriptor, document.content,
            document.knowledge_object, document.representations, document.versions,
        )
    with pytest.raises(DocumentFactoryError):
        DocumentCollection((document,))
    with pytest.raises(DocumentValidationError):
        DocumentFactory().create_collection((document, document))
    assert len(values[15]) == 1 and tuple(values[15]) == (document,)


def test_serializer_rejects_unknown_fields_models_noncanonical_json_and_numbers():
    serializer = DeterministicDocumentSerializer()
    payload = serializer.serialize(document_models()[0])
    invalid = (
        payload.replace(b"{", b'{"unknown":1,', 1),
        b'{"model":"unknown","schema_version":"1.0"}',
        b'{"model":"document_statistics","schema_version":"1.0","pages":NaN}',
        b' {"model":"document_id","schema_version":"1.0","value":"00000000-0000-4000-8000-000000000001"}',
        b"\xff",
    )
    for item in invalid:
        with pytest.raises(DocumentSerializationError):
            serializer.deserialize(item)
    with pytest.raises(DocumentSerializationError):
        serializer.deserialize(1)


@pytest.mark.parametrize("call", [
    lambda: DocumentId("invalid"),
    lambda: DocumentId(uuid4(), "2.0"),
    lambda: DocumentId.canonical("cko", object()),
    lambda: DocumentLanguage("xx"),
    lambda: DocumentAuthor(" "),
    lambda: DocumentSource("invalid", "id", "origin"),
    lambda: DocumentDescriptor("invalid"),
    lambda: DocumentContentDescriptor(fragment_ids=("x", "x")),
    lambda: DocumentRepresentation("invalid"),
    lambda: DocumentStatistics(pages=-1),
    lambda: DocumentIntegrity("bad"),
    lambda: DocumentIntegrity("a" * 64, is_intact=False, status=IntegrityStatus.VERIFIED),
    lambda: DocumentIntegrity("a" * 64, is_intact=True, status=IntegrityStatus.MISMATCH),
    lambda: DocumentVersion("bad", "1", NOW, "tester"),
    lambda: DocumentVersion(uuid4(), "1", NOW, "tester", parent_version="bad"),
    lambda: DocumentVersion((identifier := uuid4()), "1", NOW, "tester", parent_version=identifier),
])
def test_invalid_atomic_models_are_rejected(call):
    with pytest.raises(CKOError):
        call()


def test_metadata_dates_authors_sources_hashes_and_confidence_are_validated():
    source = DocumentSource(DocumentSourceType.INTERNAL, "source", "origin")
    author = DocumentAuthor("Ana", "id")
    invalid = (
        lambda: DocumentMetadata("x", NOW, NOW - timedelta(seconds=1)),
        lambda: DocumentMetadata("x", NOW, NOW, author=author, coauthors=(author,)),
        lambda: DocumentMetadata("x", NOW, NOW, coauthors=(author, author)),
        lambda: DocumentMetadata("x", NOW, NOW, language=object()),
        lambda: DocumentMetadata("x", NOW, NOW, sources=(source, source)),
        lambda: DocumentMetadata("x", NOW, NOW, checksum="bad"),
        lambda: DocumentMetadata("x", NOW, NOW, confidence=2),
    )
    for call in invalid:
        with pytest.raises(DocumentValidationError):
            call()


def test_aggregate_cross_model_invariants_are_enforced():
    document = document_models()[14]
    factory = DocumentFactory()
    with pytest.raises(DocumentValidationError):
        factory.from_parts(
            identity=document.identity, metadata=document.metadata,
            descriptor=document.descriptor, content=DocumentContentDescriptor(logical_size=99),
            knowledge_object=document.knowledge_object,
            representations=document.representations, versions=document.versions,
            integrity=document.integrity,
        )
    with pytest.raises(DocumentValidationError):
        factory.from_parts(
            identity=document.identity, metadata=document.metadata,
            descriptor=document.descriptor, content=document.content,
            knowledge_object=document.knowledge_object,
            representations=(document.representations[0], document.representations[0]),
            versions=document.versions, integrity=document.integrity,
        )
    no_source = DocumentMetadata("Title", NOW, NOW)
    with pytest.raises(DocumentValidationError):
        factory.create(
            namespace="cko.documents", metadata=no_source,
            descriptor=DocumentDescriptor(DocumentType.DOCUMENT), created_by="tester",
        )


def test_contract_helpers_defensively_reject_invalid_values():
    assert text(None, "x", optional=True) is None
    assert instant(None, "x", optional=True) is None
    assert probability(None, "x") is None
    assert non_negative(None, "x") is None
    assert sha256(None, optional=True) is None
    assert primitive(NOW).endswith("+00:00")
    assert primitive(uuid4())
    assert deep_freeze({"items": [1, 2]})["items"] == (1, 2)
    for call in (
        lambda: text(" ", "x"), lambda: instant(datetime.min, "x"),
        lambda: parse_instant(1, "x"), lambda: parse_instant("invalid", "x"),
        lambda: probability(True, "x"), lambda: probability(float("inf"), "x"),
        lambda: non_negative(True, "x"), lambda: non_negative(-1, "x"),
        lambda: sha256("bad"), lambda: unique_texts("bad", "x"),
        lambda: unique_texts(("x", "x"), "x"), lambda: model_sequence("bad", "x", DocumentId),
        lambda: model_sequence((object(),), "x", DocumentId), lambda: deep_freeze(float("nan")),
        lambda: deep_freeze({1: "x"}), lambda: deep_freeze(object()),
        lambda: primitive(float("inf")), lambda: primitive(object()),
        lambda: strict([], "x", set()),
        lambda: strict({"model": "y", "schema_version": "1.0"}, "x", set()),
        lambda: strict({"model": "x", "schema_version": "2.0"}, "x", set()),
    ):
        with pytest.raises(CKOError):
            call()


def test_validator_and_factory_preserve_typed_document_failures():
    with pytest.raises(DocumentValidationError):
        DocumentValidator().validate(object())
    source = DocumentSource(DocumentSourceType.INTERNAL, "source", "origin")
    metadata = DocumentMetadata("Title", NOW, NOW, sources=(source,))
    with pytest.raises(DocumentValidationError):
        DocumentFactory().create(
            namespace=" ", metadata=metadata,
            descriptor=DocumentDescriptor(DocumentType.DOCUMENT), created_by="tester",
        )


def test_identity_defensive_paths_are_typed():
    logical = DocumentId.new()
    canonical = DocumentId.canonical("cko.documents", logical)
    knowledge = KnowledgeObjectId.parse(str(logical))
    calls = (
        lambda: DocumentIdentity(object(), canonical, knowledge, "cko.documents"),
        lambda: DocumentIdentity(logical, canonical, object(), "cko.documents"),
        lambda: DocumentIdentity(logical, DocumentId.new(), knowledge, "cko.documents"),
        lambda: DocumentIdentity(logical, canonical, KnowledgeObjectId.new(), "cko.documents"),
        lambda: DocumentIdentity(logical, canonical, knowledge, "cko.documents", external_ids=[]),
        lambda: DocumentIdentity(logical, canonical, knowledge, "cko.documents", external_ids={"doi": 1}),
    )
    for call in calls:
        with pytest.raises(DocumentValidationError):
            call()


def test_additional_model_and_serializer_defensive_paths():
    with pytest.raises(DocumentValidationError):
        DocumentMetadata("Title", NOW, NOW, author=object())
    with pytest.raises(DocumentValidationError):
        DocumentVersion(uuid4(), "1", NOW, "tester", status="invalid")
    with pytest.raises(DocumentValidationError):
        DocumentIntegrity("a" * 64, is_intact="yes")
    with pytest.raises(DocumentValidationError):
        DocumentIntegrity("a" * 64, status="invalid")
    serializer = DeterministicDocumentSerializer()
    assert len(serializer.digest(document_models()[14])) == 64
    for payload in (
        b"{}",
        b'{"documents":{},"model":"document_collection","name":null,"schema_version":"1.0"}',
        b'{"document_id":[],"external_ids":{},"knowledge_object_id":{},"logical_id":{},"model":"document_identity","namespace":"cko","physical_ids":[],"schema_version":"1.0"}',
    ):
        with pytest.raises(DocumentSerializationError):
            serializer.deserialize(payload)


def test_additional_aggregate_invariants_and_factory_boundaries():
    document = document_models()[14]
    factory = DocumentFactory()
    with pytest.raises(DocumentFactoryError):
        factory.create(
            namespace="cko.documents", metadata=object(), descriptor=document.descriptor,
            created_by="tester",
        )
    with pytest.raises(DocumentValidationError):
        factory.from_parts(
            identity=object(), metadata=document.metadata, descriptor=document.descriptor,
            content=document.content, knowledge_object=document.knowledge_object,
            versions=document.versions,
        )
    with pytest.raises(DocumentValidationError):
        factory.from_parts(
            identity=document.identity, metadata=document.metadata, descriptor=document.descriptor,
            content=document.content, knowledge_object=document.knowledge_object,
            versions=document.versions, statistics=object(),
        )
    other = DocumentFactory(clock=lambda: NOW).create(
        namespace="cko.documents", metadata=document.metadata, descriptor=document.descriptor,
        created_by="tester",
    )
    with pytest.raises(DocumentValidationError):
        factory.from_parts(
            identity=document.identity, metadata=document.metadata, descriptor=document.descriptor,
            content=document.content, knowledge_object=other.knowledge_object,
            representations=document.representations, versions=document.versions,
            integrity=document.integrity,
        )
    with pytest.raises(DocumentValidationError):
        factory.from_parts(
            identity=document.identity, metadata=document.metadata, descriptor=document.descriptor,
            content=document.content, knowledge_object=document.knowledge_object,
            representations=(), versions=document.versions, integrity=document.integrity,
        )
    duplicate_hash = DocumentRepresentation(DocumentFormat.DOCX, hash=document.representations[0].hash)
    with pytest.raises(DocumentValidationError):
        factory.from_parts(
            identity=document.identity, metadata=document.metadata, descriptor=document.descriptor,
            content=document.content, knowledge_object=document.knowledge_object,
            representations=(document.representations[0], duplicate_hash),
            versions=document.versions, integrity=document.integrity,
        )
    mismatched_integrity = DocumentIntegrity(
        "c" * 64, logical_size=100, is_intact=True, status=IntegrityStatus.VERIFIED,
    )
    with pytest.raises(DocumentValidationError):
        factory.from_parts(
            identity=document.identity, metadata=document.metadata, descriptor=document.descriptor,
            content=document.content, knowledge_object=document.knowledge_object,
            representations=document.representations, versions=document.versions,
            integrity=mismatched_integrity,
        )
