"""Dedicated acceptance, defensive, integration, and architecture suite for SPR-016."""

from dataclasses import FrozenInstanceError, is_dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from uuid import UUID, uuid4
import json

import pytest

import cko.core as core
from cko.core.corpus import *
from cko.core.documents import (DocumentDescriptor, DocumentFactory, DocumentMetadata,
                                DocumentSource, DocumentSourceType, DocumentType)
from cko.core.graph import GraphFactory
from cko.core.index import IndexFactory, IndexField, IndexTarget, IndexType
from cko.core.knowledge import (KnowledgeContent, KnowledgeMetadata,
                                KnowledgeObjectFactory, KnowledgeType)
from cko.core.query import QueryFactory, QueryTarget
from cko.core.relationships import (RelationshipEndpoint, RelationshipFactory,
                                    RelationshipType)
from cko.core.corpus.contracts import deep_freeze, instant, primitive, text
from cko.core.corpus.models import _FACTORY_TOKEN

NOW = datetime(2026, 7, 28, 12, 0, tzinfo=UTC)
SHA_A = "a" * 64
SHA_B = "b" * 64


def ref(member_id="1", category=CorpusMemberCategory.KNOWLEDGE_OBJECT,
        version="1.0.0", digest=SHA_A, namespace="cko.test", **attributes):
    return CorpusMemberReference(member_id, category, version, category.value,
                                 namespace, digest, attributes)


@pytest.fixture
def factory():
    return CorpusFactory(clock=lambda: NOW)


@pytest.fixture
def corpus(factory):
    return factory.create_corpus(
        name="Principal", namespace="cko.test",
        members=(ref("2", CorpusMemberCategory.CANONICAL_GRAPH, digest=None), ref("1")),
        description="Acervo lógico", labels=("produção", "canônico"),
        metadata={"owner": "architecture"})


def test_constants_identity_namespace_and_public_exports(factory):
    assert CORPUS_SCHEMA_VERSION == "1.0"
    assert CORPUS_SERIALIZATION_VERSION == "1.0"
    assert CORPUS_VERSION == "1.0.0"
    assert CORPUS_UUID_NAMESPACE == UUID("0d0ee5a8-e17e-5ae1-b9e4-7801131bf190")
    assert CORPUS_UUID_NAMESPACE not in {
        UUID("a991df55-391c-53c6-b83a-b6de53e1f9a6"),
        UUID("ac032d0c-3e79-4eb0-970e-dd3328e873e4")}
    assert CorpusId.canonical("n", "x") == CorpusId.canonical("n", "x")
    assert CorpusId.canonical("n", "x") != CorpusId.canonical("n", "y")
    assert CorpusId.parse(str(CorpusId.new()))
    for name in core.corpus.__all__:
        assert hasattr(core.corpus, name)
    for name in ("KnowledgeCorpus", "CorpusFactory", "CorpusBuilder",
                 "CorpusMemberReference", "CorpusMemberCategory"):
        assert getattr(core, name) is getattr(core.corpus, name)


def test_identity_and_version_validation():
    identity = CorpusIdentity(CorpusId.canonical("cko", "Main"), " cko ", " Main ")
    assert identity.namespace == "cko" and identity.name == "Main"
    assert CorpusVersion("1.2.3", 4).revision == 4
    with pytest.raises(CorpusIdentityError):
        CorpusId("invalid")
    with pytest.raises(CorpusIdentityError):
        CorpusIdentity(CorpusId.new(), "cko", "Main")
    with pytest.raises(CorpusVersionError):
        CorpusVersion("1")
    with pytest.raises(CorpusValidationError):
        CorpusVersion("1.0.0", -1)


def test_categories_are_closed_and_query_is_absent():
    assert {item.value for item in CorpusMemberCategory} == {
        "knowledge_object", "canonical_document", "canonical_relationship",
        "canonical_graph", "canonical_index"}
    assert "canonical_query" not in {item.value for item in CorpusMemberCategory}
    with pytest.raises(CorpusCategoryError):
        CorpusMemberReference("x", "canonical_query", "1.0.0", "canonical_query", "n")


def test_reference_normalization_hash_and_deep_freeze():
    source = {"nested": ["a", {"b": 1}]}
    value = CorpusMemberReference(" id ", CorpusMemberCategory.KNOWLEDGE_OBJECT,
        "1.0.0", " object ", " ns ", SHA_A.upper(), source)
    source["nested"].append("changed")
    assert value.member_id == "id" and value.member_digest == SHA_A
    assert isinstance(value.attributes, MappingProxyType)
    assert value.attributes["nested"] == ("a", value.attributes["nested"][1])
    assert isinstance(hash(value), int)
    with pytest.raises(TypeError):
        value.attributes["x"] = 1
    with pytest.raises(CorpusDigestError):
        ref(digest="bad")
    with pytest.raises(CorpusVersionError):
        ref(version="latest")


def test_models_are_frozen_slotted_and_versioned(factory, corpus):
    changed = CorpusReferenceChange(ref(), ref(version="2.0.0"), True, False)
    comparison = CorpusComparisonResult(changed=(changed,))
    values = (corpus.identity.corpus_id, corpus.identity, corpus.corpus_version,
              *corpus.manifest.members, corpus.manifest, corpus.metadata, corpus,
              corpus_statistics(corpus), changed, comparison, factory.create_snapshot(corpus))
    for value in values:
        assert is_dataclass(value)
        assert type(value).__dataclass_params__.frozen
        assert hasattr(type(value), "__slots__")
        assert value.schema_version == CORPUS_SCHEMA_VERSION
        with pytest.raises((FrozenInstanceError, AttributeError)):
            value.schema_version = "2.0"


def test_empty_corpus_is_valid_and_deterministic(factory):
    first = factory.create_corpus(name="Empty", namespace="cko")
    second = factory.create_corpus(name="Empty", namespace="cko")
    assert first == second
    assert first.manifest.members == ()
    assert corpus_statistics(first).total_members == 0
    assert len(first.digest) == 64


def test_manifest_is_order_independent_unique_and_iterable(factory):
    first, second = ref("b"), ref("a", CorpusMemberCategory.CANONICAL_DOCUMENT)
    left = factory.create_corpus(name="x", namespace="n", members=(first, second))
    right = factory.create_corpus(name="x", namespace="n", members=(second, first))
    assert left == right and left.digest == right.digest
    assert tuple(left.manifest) == left.manifest.members and len(left.manifest) == 2
    with pytest.raises(CorpusManifestError):
        CorpusManifest((first, replace(first, member_version="2.0.0")))


def test_metadata_normalization_and_digest_participation(factory):
    base = factory.create_corpus(name="x", namespace="n", labels=("z", "a"))
    same = factory.create_corpus(name="x", namespace="n", labels=("a", "z"))
    different = factory.create_corpus(name="x", namespace="n", description="changed")
    assert base.metadata.labels == ("a", "z") and base.digest == same.digest
    assert base.digest != different.digest
    with pytest.raises(CorpusManifestError):
        CorpusMetadata(labels=("a", "a"))


def test_factory_required_and_digest_validation(factory, corpus):
    with pytest.raises(CorpusFactoryError):
        KnowledgeCorpus(corpus.identity, corpus.corpus_version, corpus.manifest,
                        corpus.metadata, corpus.digest)
    assert canonical_corpus_digest(corpus.identity, corpus.corpus_version,
                                   corpus.manifest, corpus.metadata) == corpus.digest
    payload = corpus_digest_payload(corpus.identity, corpus.corpus_version,
                                    corpus.manifest, corpus.metadata)
    assert "digest" not in payload and set(payload) == {
        "schema_version", "serialization_version", "identity", "corpus_version",
        "manifest", "metadata"}
    with pytest.raises(CorpusDigestError):
        factory.from_parts(identity=corpus.identity, corpus_version=corpus.corpus_version,
                           manifest=corpus.manifest, metadata=corpus.metadata, digest=SHA_A)


def test_membership_find_filter_add_remove_are_pure(corpus):
    original_digest = corpus.digest
    selected = corpus.manifest.members[0]
    assert contains_member(corpus, selected)
    assert contains_member(corpus, selected.identity_key)
    assert find_member(corpus, *selected.identity_key) == selected
    assert find_member(corpus, CorpusMemberCategory.CANONICAL_INDEX, "n", "missing") is None
    assert filter_members(corpus, selected.category) == (selected,)
    added_ref = ref("index", CorpusMemberCategory.CANONICAL_INDEX)
    added = add_member(corpus, added_ref)
    assert corpus.digest == original_digest and not contains_member(corpus, added_ref)
    assert contains_member(added, added_ref) and added.corpus_version.revision == 1
    removed = remove_member(added, added_ref)
    assert removed.manifest == corpus.manifest and removed.corpus_version.revision == 2
    with pytest.raises(DuplicateCorpusMemberError):
        add_member(corpus, selected)
    with pytest.raises(CorpusOperationError):
        remove_member(corpus, added_ref)
    with pytest.raises(CorpusOperationError):
        add_member(corpus, object())


def test_builder_builds_new_corpus_and_rejects_duplicates(factory, corpus):
    builder = CorpusBuilder(name="Build", namespace="cko", factory=factory)
    builder.add_reference(ref())
    with pytest.raises(DuplicateCorpusMemberError):
        builder.add_reference(ref(version="2.0.0"))
    built = builder.build()
    assert len(built.manifest) == 1
    updated = CorpusBuilder.from_corpus(corpus, factory=factory)
    updated.remove_reference(corpus.manifest.members[0])
    assert len(updated.build().manifest) == 1
    with pytest.raises(CorpusOperationError):
        CorpusBuilder.from_corpus(object())
    with pytest.raises(CorpusOperationError):
        builder.remove_reference(ref("missing"))


def test_comparison_distinguishes_all_structural_outcomes(factory):
    stable = ref("stable")
    changed_before = ref("changed", version="1.0.0", digest=SHA_A)
    changed_after = ref("changed", version="2.0.0", digest=SHA_B)
    before = factory.create_corpus(name="before", namespace="n",
        members=(stable, changed_before, ref("removed")))
    after = factory.create_corpus(name="after", namespace="n",
        members=(stable, changed_after, ref("added", CorpusMemberCategory.CANONICAL_INDEX)))
    result = compare_corpora(before, after)
    assert [item.member_id for item in result.added] == ["added"]
    assert [item.member_id for item in result.removed] == ["removed"]
    assert result.preserved == (stable,)
    assert len(result.changed) == 1
    assert result.changed[0].version_changed and result.changed[0].digest_changed
    assert CorpusOperations.compare(before, after) == result


def test_change_contract_validation():
    with pytest.raises(CorpusReferenceError):
        CorpusReferenceChange(ref("a"), ref("b"), True, False)
    with pytest.raises(CorpusReferenceError):
        CorpusReferenceChange(ref(), ref(), False, False)
    with pytest.raises(CorpusReferenceError):
        CorpusReferenceChange(ref(), ref(version="2.0.0"), 1, False)


def test_statistics_are_structural_only(factory):
    value = factory.create_corpus(name="stats", namespace="n", members=(
        ref("1", digest=SHA_A), ref("2", digest=None),
        ref("3", CorpusMemberCategory.CANONICAL_GRAPH, version="2.0.0")))
    stats = corpus_statistics(value)
    assert stats.total_members == 3 and stats.members_with_digest == 2
    assert stats.categories_present == 2
    assert dict(stats.by_category) == {"canonical_graph": 1, "knowledge_object": 2}
    assert dict(stats.by_member_version) == {"1.0.0": 2, "2.0.0": 1}
    with pytest.raises(CorpusValidationError):
        CorpusStatistics(1, 2, 1, {}, {})


def test_snapshot_is_representational_deterministic_and_consistent(factory, corpus):
    first = factory.create_snapshot(corpus, captured_at=NOW)
    second = factory.create_snapshot(corpus, captured_at=NOW)
    assert first == second and first.snapshot_id == second.snapshot_id
    assert first.manifest is corpus.manifest and first.digest == corpus.digest
    CorpusValidator().validate(first, corpus=corpus)
    other = factory.create_corpus(name="other", namespace="n")
    with pytest.raises(CorpusValidationError):
        CorpusValidator().validate(first, corpus=other)
    with pytest.raises(CorpusFactoryError):
        factory.create_snapshot(object())


def test_serializer_round_trip_for_every_public_model(factory, corpus):
    changed = CorpusReferenceChange(ref(), ref(version="2.0.0"), True, False)
    values = (corpus.identity.corpus_id, corpus.identity, corpus.corpus_version,
              *corpus.manifest.members, corpus.manifest, corpus.metadata, corpus,
              corpus_statistics(corpus), changed,
              CorpusComparisonResult(changed=(changed,)), factory.create_snapshot(corpus))
    serializer = DeterministicCorpusSerializer(factory)
    for value in values:
        payload = serializer.serialize(value)
        assert payload == serializer.serialize(value)
        assert serializer.deserialize(payload) == value
        assert len(serializer.digest(value)) == 64
        assert b"NaN" not in payload and b"Infinity" not in payload


def test_serializer_rejects_noncanonical_unknown_invalid_and_tampered(factory, corpus):
    serializer = DeterministicCorpusSerializer(factory)
    payload = serializer.serialize(corpus)
    decoded = json.loads(payload)
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(json.dumps(decoded))
    decoded["unknown"] = True
    raw = json.dumps(decoded, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(raw)
    decoded.pop("unknown")
    decoded["digest"] = SHA_A
    raw = json.dumps(decoded, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(raw)
    for invalid in (b"\xff", b"not-json", 1):
        with pytest.raises(CorpusSerializationError):
            serializer.deserialize(invalid)
    with pytest.raises(CorpusSerializationError):
        serializer.serialize(object())


def test_serializer_rejects_versions_categories_and_malformed_references(factory, corpus):
    serializer = DeterministicCorpusSerializer(factory)
    decoded = json.loads(serializer.serialize(corpus))
    decoded["serialization_version"] = "2.0"
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(json.dumps(decoded, sort_keys=True, separators=(",", ":")))
    decoded = json.loads(serializer.serialize(corpus.manifest.members[0]))
    decoded["category"] = "canonical_query"
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(json.dumps(decoded, sort_keys=True, separators=(",", ":")))
    decoded["category"] = "canonical_graph"
    decoded["member_version"] = "latest"
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(json.dumps(decoded, sort_keys=True, separators=(",", ":")))


def integration_members():
    knowledge = KnowledgeObjectFactory(clock=lambda: NOW).create(
        namespace="cko.knowledge", origin="curation", knowledge_type=KnowledgeType.CONCEPT,
        metadata=KnowledgeMetadata(NOW, NOW), content=KnowledgeContent.empty(),
        created_by="tester")
    document = DocumentFactory(clock=lambda: NOW).create(
        namespace="cko.documents", metadata=DocumentMetadata(
            "Title", NOW, NOW,
            sources=(DocumentSource(DocumentSourceType.INTERNAL, "source:1", "test"),)),
        descriptor=DocumentDescriptor(DocumentType.ARTICLE), created_by="tester")
    relationship = RelationshipFactory(clock=lambda: NOW).create(
        namespace="cko.relationships",
        source=RelationshipEndpoint(uuid4(), "cko", "knowledge_object", "1.0.0"),
        target=RelationshipEndpoint(uuid4(), "cko", "canonical_document", "1.0.0"),
        relationship_type=RelationshipType.RELATED_TO, created_by="tester")
    graph = GraphFactory(clock=lambda: NOW).create(
        namespace="cko.graphs", name="Projection", created_by="tester")
    index_factory = IndexFactory(clock=lambda: NOW)
    definition = index_factory.create_definition(
        name="Projection", namespace="cko.indexes", index_type=IndexType.NAMESPACE,
        targets=(IndexTarget.KNOWLEDGE_OBJECT,), fields=(IndexField("namespace"),))
    index = index_factory.create_index(definition)
    query = QueryFactory(clock=lambda: NOW).create(
        namespace="cko.queries", name="Intent", created_by="tester",
        targets=(QueryTarget.KNOWLEDGE_OBJECT,))
    return knowledge, document, relationship, graph, index, query


def test_integration_with_spr010_through_spr015_and_query_exclusion(factory):
    knowledge, document, relationship, graph, index, query = integration_members()
    references = tuple(factory.reference_from_member(item)
                       for item in (knowledge, document, relationship, graph, index))
    assert tuple(item.category for item in references) == tuple(CorpusMemberCategory)
    assert all(item.member_digest and len(item.member_digest) == 64 for item in references)
    corpus = factory.create_corpus(name="integrated", namespace="cko", members=references)
    assert len(corpus.manifest) == 5
    assert filter_members(corpus, CorpusMemberCategory.CANONICAL_GRAPH)[0].member_id
    assert filter_members(corpus, CorpusMemberCategory.CANONICAL_INDEX)[0].member_id
    with pytest.raises(CorpusReferenceError):
        factory.reference_from_member(query)
    with pytest.raises(CorpusReferenceError):
        factory.reference_from_member(object())
    with pytest.raises(CorpusDigestError):
        factory.reference_from_member(knowledge, member_digest="")


def test_builder_accepts_materialized_public_member(factory):
    knowledge, *_ = integration_members()
    built = CorpusBuilder(name="integrated", namespace="cko", factory=factory).add(knowledge).build()
    assert built.manifest.members[0].category is CorpusMemberCategory.KNOWLEDGE_OBJECT


def test_validator_defensive_paths(corpus):
    validator = CorpusValidator()
    with pytest.raises(CorpusValidationError):
        validator.validate(object())
    altered = object.__new__(KnowledgeCorpus)
    for field_name in ("identity", "corpus_version", "manifest", "metadata",
                       "serialization_version", "schema_version"):
        object.__setattr__(altered, field_name, getattr(corpus, field_name))
    object.__setattr__(altered, "digest", SHA_A)
    with pytest.raises(CorpusDigestError):
        validator.validate(altered)


def test_no_io_runtime_persistence_reverse_imports_or_cycles():
    root = Path(core.corpus.__file__).parent
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))
    prohibited_imports = ("pathlib", "sqlite3", "socket", "requests", ".storage",
                          ".runtime", ".checkpoint", ".inventory", ".discovery")
    assert all(f"import {name}" not in source and f"from {name}" not in source
               for name in prohibited_imports)
    for namespace in ("knowledge", "documents", "relationships", "graph", "query", "index"):
        previous = root.parent / namespace
        assert all("corpus" not in path.read_text(encoding="utf-8")
                   for path in previous.glob("*.py"))
    assert "InventorySnapshot" not in source and "CorpusRepository" not in source


def test_error_contract_is_structured_and_core_compatible():
    error = CorpusError(" failure ", model="manifest", details={"member": "x"})
    assert isinstance(error, core.CKOError)
    assert error.to_dict() == {"code": "corpus_error", "message": "failure",
                               "model": "manifest", "details": {"member": "x"}}
    with pytest.raises(ValueError):
        CorpusError("")


def test_normalization_primitives_cover_defensive_types():
    assert text(None, "optional", optional=True) is None
    with pytest.raises(CorpusValidationError):
        text(" ", "empty")
    with pytest.raises(CorpusValidationError):
        instant(datetime(2026, 1, 1), "naive")
    assert deep_freeze(NOW) == NOW
    assert deep_freeze(1.5) == 1.5
    for invalid in (float("nan"), object()):
        with pytest.raises(CorpusValidationError):
            deep_freeze(invalid)
    assert primitive(1.5) == 1.5
    with pytest.raises(CorpusSerializationError):
        primitive(float("inf"))
    with pytest.raises(CorpusSerializationError):
        primitive(object())
    with pytest.raises(CorpusVersionError):
        CorpusVersion("1.0.0", schema_version="2.0")


def test_factory_helpers_and_builder_type_guards(factory):
    created = factory.create_reference(
        member_id="x", category=CorpusMemberCategory.CANONICAL_INDEX,
        member_version="1.0.0", discriminator_name="canonical_index",
        namespace="cko", attributes={"role": "projection"})
    assert factory.create_manifest((created,)).members == (created,)
    with pytest.raises(CorpusOperationError):
        CorpusBuilder(name="x", namespace="n").add_reference(object())


def test_structural_models_reject_wrong_nested_types(factory, corpus):
    with pytest.raises(CorpusManifestError):
        CorpusManifest((object(),))
    arguments = dict(identity=corpus.identity, corpus_version=corpus.corpus_version,
                     manifest=corpus.manifest, metadata=corpus.metadata,
                     digest=corpus.digest, _factory_token=_FACTORY_TOKEN)
    for name in ("identity", "corpus_version", "manifest", "metadata"):
        invalid = dict(arguments)
        invalid[name] = object()
        with pytest.raises(CorpusReferenceError):
            KnowledgeCorpus(**invalid)
    invalid = dict(arguments)
    invalid["serialization_version"] = "2.0"
    with pytest.raises(CorpusReferenceError):
        KnowledgeCorpus(**invalid)
    with pytest.raises(CorpusManifestError):
        CorpusStatistics(0, 0, 6, {}, {})
    with pytest.raises(CorpusManifestError):
        CorpusStatistics(1, 0, 1, {"x": -1}, {})
    with pytest.raises(CorpusReferenceError):
        CorpusReferenceChange(object(), ref(), True, False)
    with pytest.raises(CorpusManifestError):
        CorpusComparisonResult(added=(object(),))
    with pytest.raises(CorpusManifestError):
        CorpusComparisonResult(changed=(object(),))


def test_snapshot_rejects_wrong_structural_models(factory, corpus):
    snapshot = factory.create_snapshot(corpus)
    fields = dict(snapshot_id=snapshot.snapshot_id, corpus_id=snapshot.corpus_id,
                  corpus_version=snapshot.corpus_version, manifest=snapshot.manifest,
                  digest=snapshot.digest, statistics=snapshot.statistics,
                  captured_at=snapshot.captured_at)
    for name in ("snapshot_id", "corpus_version", "statistics"):
        invalid = dict(fields)
        invalid[name] = object()
        with pytest.raises(CorpusReferenceError):
            CorpusSnapshot(**invalid)


def test_serializer_additional_closed_schema_guards(factory, corpus):
    serializer = DeterministicCorpusSerializer(factory)
    valid = json.loads(serializer.serialize(corpus.identity))
    valid["model"] = "corpus_id"
    raw = json.dumps(valid, sort_keys=True, separators=(",", ":"))
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(raw)
    valid = json.loads(serializer.serialize(corpus.identity))
    valid["schema_version"] = "2.0"
    raw = json.dumps(valid, sort_keys=True, separators=(",", ":"))
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(raw)
    for value in ({}, {"model": "future", "schema_version": "1.0"}):
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"))
        with pytest.raises(CorpusSerializationError):
            serializer.deserialize(raw)
    malformed = json.loads(serializer.serialize(corpus.manifest))
    malformed["members"] = {}
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(json.dumps(malformed, sort_keys=True, separators=(",", ":")))
    malformed = json.loads(serializer.serialize(corpus.metadata))
    malformed["attributes"] = []
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(json.dumps(malformed, sort_keys=True, separators=(",", ":")))
    snapshot = json.loads(serializer.serialize(factory.create_snapshot(corpus)))
    snapshot["captured_at"] = "not-a-date"
    with pytest.raises(CorpusSerializationError):
        serializer.deserialize(json.dumps(snapshot, sort_keys=True, separators=(",", ":")))
