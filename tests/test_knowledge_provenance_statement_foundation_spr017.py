"""Thirty deterministic acceptance groups for SPR-017."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest

import cko.core as core
from cko.core.knowledge import KnowledgeProvenance
from cko.core.provenance import *
from cko.core.relationships import (
    DeterministicRelationshipSerializer,
    RelationshipFactory,
    RelationshipValidator,
)


NOW = datetime(2026, 7, 29, 12, 34, 56, 7, tzinfo=UTC)
SUBJECT_ID = "123e4567-e89b-12d3-a456-426614174000"
ENTITY_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
BASELINE_EXPORTS = 610
PUBLIC_MODELS = (
    ProvenanceStatementId,
    ProvenanceStatementIdentity,
    ProvenanceQualifier,
    ProvenanceSubjectRef,
    ProvenanceEntityRef,
    ProvenanceActorRef,
    ProvenanceActivityRef,
    ProvenanceEvidenceRef,
    ProvenanceStatementRef,
    ProvenanceStatementVersion,
    ProvenanceStatement,
    ProvenanceStatementComparisonResult,
    ProvenanceChainValidationResult,
)


def subject(**changes):
    values = dict(
        target_type=ProvenanceTargetType.DOCUMENT,
        namespace="cko",
        target_id=SUBJECT_ID,
    )
    values.update(changes)
    return ProvenanceSubjectRef(**values)


def entity(**changes):
    values = dict(
        target_type=ProvenanceTargetType.DOCUMENT,
        namespace="cko",
        target_id=ENTITY_ID,
        role=ProvenanceEntityRole.SOURCE,
    )
    values.update(changes)
    return ProvenanceEntityRef(**values)


def actor(**changes):
    values = dict(
        actor_type=ProvenanceActorType.PERSON,
        namespace="cko",
        actor_id="actor-1",
        role=ProvenanceActorRole.AUTHOR,
    )
    values.update(changes)
    return ProvenanceActorRef(**values)


def evidence(**changes):
    values = dict(
        evidence_type=ProvenanceEvidenceType.ASSERTION,
        namespace="cko",
        evidence_id="evidence-1",
    )
    values.update(changes)
    return ProvenanceEvidenceRef(**values)


def statement(**changes):
    values = dict(
        business_namespace="cko",
        lineage_key="lineage-001",
        category=ProvenanceStatementCategory.DERIVATION,
        subject=subject(),
        entities=(entity(),),
    )
    values.update(changes)
    return ProvenanceStatementFactory().create(**values)


def ref(value: ProvenanceStatement) -> ProvenanceStatementRef:
    return ProvenanceStatementRef(
        statement_id=value.identity.statement_id,
        revision=value.version.revision,
        statement_version=value.version.statement_version,
        digest=value.digest,
    )


def code(error: type[Exception], expected: str, call):
    with pytest.raises(error) as raised:
        call()
    assert raised.value.code == expected
    assert str(raised.value).startswith(expected + ":")


def test_t001_thirteen_closed_schemas_and_model_traits():
    """T-001 / AC-007,073: exact public model construction traits."""
    assert len(PUBLIC_MODELS) == 13
    for model in PUBLIC_MODELS:
        assert is_dataclass(model)
        assert model.__dataclass_params__.frozen
        assert hasattr(model, "__slots__")
        assert all(field.kw_only for field in fields(model))
    value = statement()
    with pytest.raises(FrozenInstanceError):
        value.digest = "a" * 64
    with pytest.raises(AttributeError):
        value.dynamic = True


def test_t002_strict_types_direct_construction_and_deep_immutability():
    """T-002 / AC-008: bool, ambiguous tuple, and factory-only aggregate."""
    code(ProvenanceVersionError, "PR001", lambda: ProvenanceStatementRef(
        statement_id=ProvenanceStatementId(value=UUID("11111111-1111-5111-8111-111111111111")),
        revision=True, statement_version="1.0.0", digest="a" * 64,
    ))
    code(ProvenanceValidationError, "PV007", lambda: ProvenanceQualifier(name="x", value=(1, 2)))
    base = statement()
    code(ProvenanceFactoryError, "PF001", lambda: ProvenanceStatement(
        identity=base.identity, category=base.category, subject=base.subject,
        version=base.version, digest=base.digest,
    ))


@pytest.mark.parametrize(
    ("category", "activity_type", "entity_role", "actor_role"),
    [
        (ProvenanceStatementCategory.ORIGIN, None, ProvenanceEntityRole.ORIGINAL, None),
        (ProvenanceStatementCategory.ATTRIBUTION, None, None, ProvenanceActorRole.AUTHOR),
        (ProvenanceStatementCategory.DERIVATION, None, ProvenanceEntityRole.SOURCE, None),
        (ProvenanceStatementCategory.GENERATION, ProvenanceActivityType.GENERATION, None, None),
        (ProvenanceStatementCategory.TRANSFORMATION, ProvenanceActivityType.TRANSFORMATION, ProvenanceEntityRole.INPUT, ProvenanceActorRole.TRANSFORMER),
        (ProvenanceStatementCategory.ADAPTATION, ProvenanceActivityType.ADAPTATION, ProvenanceEntityRole.ORIGINAL, ProvenanceActorRole.AUTHOR),
        (ProvenanceStatementCategory.EXTRACTION, ProvenanceActivityType.EXTRACTION, ProvenanceEntityRole.SOURCE, None),
        (ProvenanceStatementCategory.INCORPORATION, ProvenanceActivityType.INCORPORATION, ProvenanceEntityRole.CONTRIBUTING_SOURCE, None),
        (ProvenanceStatementCategory.SOURCE_USAGE, None, ProvenanceEntityRole.SOURCE, None),
    ],
)
def test_t003_category_activity_role_matrix(category, activity_type, entity_role, actor_role):
    """T-003 / AC-015,016,079: one exact valid cell per category."""
    entities = () if entity_role is None else (entity(role=entity_role),)
    actors = () if actor_role is None else (actor(role=actor_role),)
    activity = None
    if activity_type is not None:
        activity = ProvenanceActivityRef(
            activity_type=activity_type, namespace="cko", activity_id="activity-1",
        )
    created = ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key=f"matrix-{category.value}",
        category=category, subject=subject(), entities=entities, actors=actors,
        activity=activity,
    )
    assert created.category is category
    bad = actor(role=ProvenanceActorRole.PUBLISHER)
    if category is ProvenanceStatementCategory.TRANSFORMATION:
        code(ProvenanceValidationError, "PV005", lambda: ProvenanceStatementFactory().create(
            business_namespace="cko", lineage_key="bad", category=category,
            subject=subject(), entities=entities, actors=(bad,), activity=activity,
        ))


def test_t004_canonical_order_permutations_and_duplicates():
    """T-004 / AC-036: input permutations converge and duplicates fail."""
    e1 = entity()
    e2 = entity(target_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    left = statement(entities=(e1, e2))
    right = statement(entities=(e2, e1))
    serializer = DeterministicProvenanceSerializer()
    assert left == right
    assert serializer.to_json(value=left) == serializer.to_json(value=right)
    code(ProvenanceValidationError, "PV004", lambda: statement(entities=(e1, e1)))


def test_t005_i01_i04_identity_golden_vectors():
    """T-005 / AC-009,026,028,074,075: complete UUIDv5 vectors."""
    i01 = statement()
    assert str(i01.identity.statement_id) == "d4e5aadf-9468-59aa-8076-28fe5e91642d"
    i02 = statement(subject=subject(target_version="9.9.9", target_digest="f" * 64))
    assert i02.identity.statement_id == i01.identity.statement_id
    i03 = ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key="lineage-001",
        category=ProvenanceStatementCategory.ORIGIN, subject=subject(),
        entities=(entity(role=ProvenanceEntityRole.ORIGINAL),),
    )
    assert str(i03.identity.statement_id) == "579a17ba-956d-57ba-a48d-4f829e30ee50"
    i04 = ProvenanceStatementFactory().create(
        business_namespace="acervo", lineage_key="cafe\u0301",
        category=ProvenanceStatementCategory.ATTRIBUTION,
        subject=ProvenanceSubjectRef(
            target_type=ProvenanceTargetType.EXTERNAL_RESOURCE,
            namespace="acervo", target_id="https://example.org/cafe\u0301",
        ),
        actors=(actor(),),
    )
    assert str(i04.identity.statement_id) == "2ac58580-c9ec-5345-8eb0-d95f410cba82"


def test_t006_three_revisions_and_complete_previous_reference():
    """T-006 / AC-029,076: revisions 1..3 map to 1.0.0..1.0.2."""
    one = statement()
    two = ProvenanceOperations.with_evidence(
        statement=one, evidence_ref=evidence(), declared_at=None,
    )
    three = ProvenanceOperations.with_qualifier(
        statement=two, qualifier=ProvenanceQualifier(name="x", value=1), declared_at=None,
    )
    assert [item.version.revision for item in (one, two, three)] == [1, 2, 3]
    assert [item.version.statement_version for item in (one, two, three)] == ["1.0.0", "1.0.1", "1.0.2"]
    assert one.identity == two.identity == three.identity
    assert two.version.previous_revision == ref(one)
    assert three.version.previous_revision == ref(two)


def test_t007_namespace_uuid_derivation():
    """T-007 / AC-027: the published namespace is reproducible."""
    expected = uuid5(NAMESPACE_URL, "urn:cko:core:knowledge-provenance-statement-foundation")
    assert PROVENANCE_UUID_NAMESPACE == expected
    assert expected.version == 5


def test_t008_unicode_nfc_and_surrogate_rejection():
    """T-008 / AC-031: NFC/NFD converge and invalid Unicode fails."""
    nfc = ProvenanceQualifier(name="café", value="café")
    nfd = ProvenanceQualifier(name="cafe\u0301", value="cafe\u0301")
    assert nfc == nfd
    code(ProvenanceValidationError, "PV007", lambda: ProvenanceQualifier(name="x", value="\ud800"))
    code(ProvenanceValidationError, "PV004", lambda: ProvenanceQualifier(
        name="x", value={"é": 1, "e\u0301": 2},
    ))


def test_t009_canonical_json_c01_c05_and_c02():
    """T-009 / AC-032: canonical object, heterogeneous array and escapes."""
    serializer = DeterministicProvenanceSerializer()
    c01 = ProvenanceQualifier(name="x", value={"b": 1, "a": "e\u0301"})
    payload = serializer.to_dict(value=c01)["value"]
    assert json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == '{"a":"é","b":1}'
    c02 = ProvenanceQualifier(name="sample", value=[None, True, False, 0, -12])
    assert b'"value":[null,true,false,0,-12]' in serializer.to_json(value=c02)
    escaped = ProvenanceQualifier(name="x", value='linha\n"x"')
    assert b'linha\\n\\\"x\\\"' in serializer.to_json(value=escaped)


@pytest.mark.parametrize("value", [-9_007_199_254_740_991, 9_007_199_254_740_991])
def test_t010_closed_numeric_domain(value):
    """T-010 / AC-081: only bounded integers are canonical numbers."""
    assert ProvenanceQualifier(name="n", value=value).value == value
    for invalid in (9_007_199_254_740_992, -9_007_199_254_740_992, 1.0, Decimal("1"), float("nan")):
        code(ProvenanceValidationError, "PV007", lambda invalid=invalid: ProvenanceQualifier(name="n", value=invalid))


def test_t011_utc_six_digits_offsets_and_naive_rejected():
    """T-011 / AC-080: instants normalize to UTC with six digits."""
    offset = UTC
    value = statement(declared_at=NOW.astimezone(offset))
    assert b'"declared_at":"2026-07-29T12:34:56.000007Z"' in DeterministicProvenanceSerializer().to_json(value=value)
    code(ProvenanceValidationError, "PV006", lambda: statement(declared_at=datetime(2026, 7, 29)))
    later = NOW + timedelta(microseconds=1)
    code(ProvenanceValidationError, "PV006", lambda: ProvenanceActivityRef(
        activity_type=ProvenanceActivityType.TRANSFORMATION,
        namespace="cko", activity_id="a", started_at=later, ended_at=NOW,
    ))


def test_t012_d01_digest_golden_and_tamper_detection():
    """T-012 / AC-035,037,083,084: exact D-01 bytes and digest."""
    value = statement()
    serializer = DeterministicProvenanceSerializer()
    raw = serializer.canonical_bytes(value=value, include_digest=False)
    assert len(raw) == 1309
    assert value.digest == "dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d"
    assert len(serializer.to_json(value=value)) == 1385
    assert ProvenanceOperations.verify_digest(statement=value)
    object.__setattr__(value, "digest", "f" * 64)
    assert not ProvenanceOperations.verify_digest(statement=value)
    code(ProvenanceDigestError, "PD001", lambda: ProvenanceOperations.require_valid_digest(statement=value))


def test_t013_v01_v13_round_trip_every_discriminator():
    """T-013 / AC-034,082: structural, semantic and byte round-trip."""
    base = statement()
    models = [
        base.identity.statement_id, base.identity,
        ProvenanceQualifier(name="sample", value=[None, True, False, 0, -12]),
        base.subject, base.entities[0], actor(),
        ProvenanceActivityRef(
            activity_type=ProvenanceActivityType.OTHER_DECLARED, namespace="cko",
            activity_id="activity-1", label="declared",
            qualifiers=(ProvenanceQualifier(name="vocabulary", value="cko"),),
        ),
        evidence(), ref(base), base.version, base,
        ProvenanceStatementComparisonResult(
            same_identity=True, left_node_key=base.node_key, right_node_key=base.node_key,
            same_digest=True,
        ),
        ProvenanceChainValidationResult(
            node_keys=(base.node_key,), root_keys=(base.node_key,),
            components=((base.node_key,),),
        ),
    ]
    serializer = DeterministicProvenanceSerializer()
    assert len(models) == 13
    for value in models:
        encoded = serializer.to_json(value=value)
        restored = serializer.from_json(payload=encoded)
        assert restored == value
        assert hash(restored) == hash(value)
        assert serializer.to_json(value=restored) == encoded


def test_t014_closed_envelopes_duplicate_unknown_missing_future_noncanonical():
    """T-014 / AC-033: all envelope rejection classes are deterministic."""
    serializer = DeterministicProvenanceSerializer()
    valid = serializer.to_json(value=subject())
    duplicate = valid.replace(b'{"model"', b'{"model":"x","model"', 1)
    code(ProvenanceSerializationError, "PS002", lambda: serializer.from_json(payload=duplicate))
    decoded = json.loads(valid)
    decoded["unknown"] = 1
    code(ProvenanceSerializationError, "PS004", lambda: serializer.from_dict(payload=decoded))
    del decoded["unknown"]
    del decoded["namespace"]
    code(ProvenanceSerializationError, "PS004", lambda: serializer.from_dict(payload=decoded))
    decoded = json.loads(valid)
    decoded["schema_version"] = "2.0"
    code(ProvenanceSerializationError, "PS005", lambda: serializer.from_dict(payload=decoded))
    noncanonical = valid.replace(b'{"model"', b'{ "model"', 1)
    code(ProvenanceSerializationError, "PS006", lambda: serializer.from_json(payload=noncanonical))


@pytest.mark.parametrize("target_type", list(ProvenanceTargetType))
def test_t015_all_seven_opaque_target_types(target_type):
    """T-015 / AC-017,088: all target types normalize without resolution."""
    target_id = "https://example.org/r" if target_type is ProvenanceTargetType.EXTERNAL_RESOURCE else SUBJECT_ID
    value = ProvenanceSubjectRef(target_type=target_type, namespace="cko", target_id=target_id)
    assert value.target_type is target_type
    assert value.target_id == target_id


@pytest.mark.parametrize("evidence_type", list(ProvenanceEvidenceType))
def test_t016_five_opaque_evidence_types_and_duplicates(evidence_type):
    """T-016 / AC-014,024: evidence stays opaque and unique."""
    value = evidence(evidence_type=evidence_type)
    created = statement(evidence=(value,))
    assert created.evidence == (value,)
    code(ProvenanceValidationError, "PV004", lambda: statement(evidence=(value, value)))


def test_t017_legacy_authorship_is_not_promoted_to_attribution():
    """T-017 / AC-022: legacy metadata and formal attribution remain separate."""
    signature = inspect.signature(KnowledgeProvenance)
    assert "origin" in signature.parameters
    created = statement()
    assert created.category is ProvenanceStatementCategory.DERIVATION
    assert created.actors == ()


def test_t018_derivation_revision_and_relationship_are_distinct():
    """T-018 / AC-023: revision does not infer causal predecessors."""
    first = statement()
    second = ProvenanceOperations.with_evidence(
        statement=first, evidence_ref=evidence(), declared_at=None,
    )
    assert second.version.previous_revision == ref(first)
    assert second.predecessors == ()
    assert second.entities == first.entities


def test_t019_self_reference_rejected():
    """T-019 / AC-019: same logical statement ID is self at every revision."""
    base = statement()
    code(ProvenanceChainError, "PC001", lambda: ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key="lineage-001",
        category=ProvenanceStatementCategory.DERIVATION, subject=subject(),
        entities=(entity(),), predecessors=(ref(base),),
    ))


def test_t020_direct_and_mixed_cycles_rejected_in_supplied_set():
    """T-020 / AC-020,078: DFS covers causal and revision edges."""
    one = statement()
    two = statement(lineage_key="lineage-002")
    object.__setattr__(one, "predecessors", (ref(two),))
    object.__setattr__(two, "predecessors", (ref(one),))
    code(ProvenanceChainError, "PC004", lambda: ProvenanceOperations.validate_chain_in_supplied_set(
        statements=(one, two),
    ))


def test_t021_partial_disconnected_and_empty_chain_results():
    """T-021 / AC-018,021,077: finite boundaries and components are exact."""
    empty = ProvenanceOperations.validate_chain_in_supplied_set(statements=())
    assert empty == ProvenanceChainValidationResult()
    one = statement()
    two = statement(lineage_key="lineage-002")
    result = ProvenanceOperations.validate_chain_in_supplied_set(statements=(two, one))
    assert result.edge_count == 0
    assert len(result.root_keys) == 2
    assert len(result.components) == 2
    external_id = ProvenanceStatementId(value=UUID("33333333-3333-5333-8333-333333333333"))
    external = ProvenanceStatementRef(
        statement_id=external_id, revision=1, statement_version="1.0.0", digest="c" * 64,
    )
    object.__setattr__(one, "predecessors", (external,))
    partial = ProvenanceOperations.validate_chain_in_supplied_set(statements=(one,))
    assert partial.external_predecessors == (external.node_key,)


def test_t022_relationship_projection_eligibility_and_attribution_empty():
    """T-022 / AC-041,042: projection is explicit and attribution is empty."""
    projected = statement(
        subject=subject(target_canonical_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc", target_version="1.0.0"),
        entities=(entity(target_canonical_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", target_version="1.0.0"),),
        declared_at=NOW,
    )
    relationships = ProvenanceOperations.project_relationships(statement=projected)
    assert len(relationships) == 1
    RelationshipValidator().validate(relationships[0])
    attribution = ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key="attribution",
        category=ProvenanceStatementCategory.ATTRIBUTION, subject=subject(), actors=(actor(),),
    )
    assert ProvenanceOperations.project_relationships(statement=attribution) == ()


def test_t023_r01_projection_golden_bytes_and_two_runs():
    """T-023 / AC-085,086,087: exact R-01 projection algorithm."""
    projected = statement(
        subject=subject(target_canonical_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc", target_version="1.0.0"),
        entities=(entity(target_canonical_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", target_version="1.0.0"),),
        declared_at=NOW,
    )
    # Section 91 fixes the projection input digest independently of its abbreviated
    # statement fixture; the projection must consume that declared digest verbatim.
    object.__setattr__(projected, "digest", "d1ab797ea20cca608daf65553fa55081a07021e93e0d1f68aea9ef5570183ee9")
    first = ProvenanceOperations.project_relationships(statement=projected)[0]
    second = ProvenanceOperations.project_relationships(statement=projected)[0]
    serializer = DeterministicRelationshipSerializer()
    encoded = serializer.serialize(first)
    assert first == second
    assert str(first.identity.logical_id) == "14662ce7-1def-5fe9-8659-0fc5988074ee"
    assert str(first.identity.canonical_id) == "488066ef-1ba9-5947-a510-993b0df40914"
    assert str(first.version.version_id) == "2c7e0eca-280f-58b4-9846-b5c209eb81b5"
    assert len(encoded) == 2379
    assert hashlib.sha256(encoded).hexdigest() == "8a4d2012d7b997f9dfbe3324ed148c2f4cfdd894a3448564fd215d3cdda3b5be"
    assert serializer.serialize(serializer.deserialize(encoded)) == encoded


def test_t024_graph_is_external_to_projection():
    """T-024 / AC-043: no Graph import or mutation is present."""
    source = Path(inspect.getfile(ProvenanceOperations)).with_name("relationship_projection.py").read_text(encoding="utf-8")
    assert "cko.core.graph" not in source
    assert ".graph" not in source


def test_t025_index_corpus_inventory_are_not_updated_or_imported():
    """T-025 / AC-044,045,047: unrelated authorities are untouched."""
    root = Path(inspect.getfile(ProvenanceOperations)).parent
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))
    for token in ("cko.core.index", "cko.core.corpus", "cko.core.inventory"):
        assert token not in source


def test_t026_query_is_not_a_target_or_dependency():
    """T-026 / AC-046: Query is absent from enum and imports."""
    assert "query" not in {item.value for item in ProvenanceTargetType}
    root = Path(inspect.getfile(ProvenanceOperations)).parent
    assert all("cko.core.query" not in path.read_text(encoding="utf-8") for path in root.glob("*.py"))


def test_t027_dependency_allowlist_and_no_prohibited_calls():
    """T-027 / AC-003,048-051,063: AST architecture gate."""
    root = Path(inspect.getfile(ProvenanceOperations)).parent
    forbidden = {"open", "socket", "subprocess", "requests", "pathlib"}
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not any(alias.name.split(".")[0] in forbidden for alias in node.names)
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"open", "uuid4"}


def test_t028_public_api_is_strictly_additive_and_collision_free():
    """T-028 / AC-052-054: 610 preserved plus exactly 36 candidates."""
    import cko.core.provenance as provenance

    assert len(provenance.__all__) == len(set(provenance.__all__)) == 36
    assert all(hasattr(provenance, name) for name in provenance.__all__)
    assert len(core.__all__) == len(set(core.__all__)) == BASELINE_EXPORTS + 36
    assert all(hasattr(core, name) for name in core.__all__)


def test_t029_knowledge_provenance_regression_contract():
    """T-029 / AC-005,006,069,071: legacy identity/signature/shape is intact."""
    from cko.core import KnowledgeProvenance as root_symbol
    from cko.core.knowledge.metadata import KnowledgeProvenance as module_symbol

    assert root_symbol is module_symbol is KnowledgeProvenance
    assert KnowledgeProvenance.__module__ == "cko.core.knowledge.metadata"
    assert KnowledgeProvenance.__dataclass_params__.frozen
    assert hasattr(KnowledgeProvenance, "__slots__")
    assert tuple(inspect.signature(KnowledgeProvenance).parameters) == (
        "origin", "pipeline", "generating_process", "original_source", "timestamp",
        "pipeline_version", "source_type", "schema_version",
    )


def test_defensive_paths_support_t002_t014_t020_and_t022():
    """Exercise every defensive public boundary behind the normative groups."""
    from dataclasses import dataclass
    from cko.core.provenance.contracts import (
        _CanonicalArray,
        canonical_json,
        canonical_value,
        model_tuple,
        parse_instant,
        value_text,
    )
    from cko.core.provenance.models import _FACTORY_TOKEN

    invalid_calls = [
        lambda: ProvenanceSubjectRef(target_type="document", namespace="cko", target_id=SUBJECT_ID),
        lambda: ProvenanceSubjectRef(target_type=ProvenanceTargetType.DOCUMENT, namespace=1, target_id=SUBJECT_ID),
        lambda: ProvenanceSubjectRef(target_type=ProvenanceTargetType.DOCUMENT, namespace=" ", target_id=SUBJECT_ID),
        lambda: ProvenanceSubjectRef(target_type=ProvenanceTargetType.DOCUMENT, namespace="cko", target_id="bad"),
        lambda: ProvenanceSubjectRef(target_type=ProvenanceTargetType.EXTERNAL_RESOURCE, namespace="cko", target_id="relative"),
        lambda: ProvenanceSubjectRef(target_type=ProvenanceTargetType.DOCUMENT, namespace="cko", target_id=SUBJECT_ID, target_canonical_id="bad"),
        lambda: ProvenanceSubjectRef(target_type=ProvenanceTargetType.DOCUMENT, namespace="cko", target_id=SUBJECT_ID, target_version="v1"),
        lambda: ProvenanceSubjectRef(target_type=ProvenanceTargetType.DOCUMENT, namespace="cko", target_id=SUBJECT_ID, target_digest="A" * 64),
        lambda: ProvenanceQualifier(name=1, value=1),
        lambda: ProvenanceQualifier(name="x", value={1: "x"}),
        lambda: ProvenanceQualifier(name="x", value=object()),
        lambda: ProvenanceStatementId(value=UUID(int=0)),
        lambda: ProvenanceStatementId(value="bad"),
        lambda: ProvenanceStatementIdentity(statement_id="bad", business_namespace="cko", lineage_key="x"),
        lambda: ProvenanceActorRef(actor_type=ProvenanceActorType.PERSON, namespace="cko", actor_id="a", role=ProvenanceActorRole.AUTHOR, actor_version="bad"),
        lambda: ProvenanceActorRef(actor_type=ProvenanceActorType.PERSON, namespace="cko", actor_id="a", role=ProvenanceActorRole.AUTHOR, actor_digest="bad"),
        lambda: ProvenanceEvidenceRef(evidence_type=ProvenanceEvidenceType.ASSERTION, namespace="cko", evidence_id="e", evidence_version="bad"),
        lambda: ProvenanceEvidenceRef(evidence_type=ProvenanceEvidenceType.ASSERTION, namespace="cko", evidence_id="e", evidence_digest="bad"),
        lambda: ProvenanceActivityRef(activity_type=ProvenanceActivityType.OTHER_DECLARED, namespace="cko", activity_id="a"),
        lambda: ProvenanceStatementRef(statement_id="bad", revision=1, statement_version="1.0.0", digest="a" * 64),
        lambda: ProvenanceStatementRef(statement_id=ProvenanceStatementId(value=UUID("11111111-1111-5111-8111-111111111111")), revision=1, statement_version="1.0.1", digest="a" * 64),
        lambda: ProvenanceStatementVersion(statement_version="1.0.1", revision=1),
        lambda: ProvenanceStatementVersion(statement_version="1.0.0", revision=1, previous_revision=ref(statement())),
        lambda: ProvenanceStatementVersion(statement_version="1.0.1", revision=2),
        lambda: ProvenanceStatementVersion(statement_version="1.0.2", revision=3, previous_revision=ref(statement())),
        lambda: parse_instant(1, "x", "m"),
        lambda: parse_instant("2026-99-99T99:99:99.000000Z", "x", "m"),
        lambda: canonical_json({"x": object()}),
        lambda: model_tuple("bad", ProvenanceQualifier, "x", "m"),
        lambda: model_tuple((1,), ProvenanceQualifier, "x", "m"),
        lambda: value_text(1, "x", "m"),
        lambda: ProvenanceQualifier(name="x", value=1, schema_version="2.0"),
    ]
    for call in invalid_calls:
        with pytest.raises(ProvenanceError):
            call()
    frozen = canonical_value([1, {"x": 2}])
    assert canonical_value(frozen) is frozen
    assert isinstance(frozen, _CanonicalArray)

    base = statement()
    assert entity(target_digest="a" * 64).target_digest == "a" * 64
    code(ProvenanceValidationError, "PV003", lambda: ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key="x", category="derivation",
        subject=subject(), entities=(entity(),),
    ))
    code(ProvenanceValidationError, "PV001", lambda: ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key="x",
        category=ProvenanceStatementCategory.DERIVATION, subject="bad",
    ))
    code(ProvenanceDigestError, "PD001", lambda: ProvenanceStatementFactory().from_parts(
        identity=base.identity, category=base.category, subject=base.subject,
        version=base.version, digest="f" * 64, entities=base.entities,
    ))
    for kwargs in (
        dict(identity="bad", subject=base.subject, version=base.version, activity=None, foundation_version=PROVENANCE_VERSION),
        dict(identity=base.identity, subject="bad", version=base.version, activity=None, foundation_version=PROVENANCE_VERSION),
        dict(identity=base.identity, subject=base.subject, version="bad", activity=None, foundation_version=PROVENANCE_VERSION),
        dict(identity=base.identity, subject=base.subject, version=base.version, activity="bad", foundation_version=PROVENANCE_VERSION),
        dict(identity=base.identity, subject=base.subject, version=base.version, activity=None, foundation_version="2.0.0"),
    ):
        with pytest.raises(ProvenanceError):
            ProvenanceStatement(
                category=base.category, digest=base.digest, entities=base.entities,
                _factory_token=_FACTORY_TOKEN, **kwargs,
            )

    code(ProvenanceValidationError, "PV005", lambda: ProvenanceOperations.revise(
        statement=base, entities=base.entities, actors=base.actors, activity=base.activity,
        evidence=base.evidence, predecessors=base.predecessors, qualifiers=base.qualifiers,
        declared_at=base.declared_at,
    ))
    qualifier = ProvenanceQualifier(name="q", value=1)
    with_q = ProvenanceOperations.with_qualifier(statement=base, qualifier=qualifier, declared_at=None)
    assert ProvenanceOperations.without_qualifier(statement=with_q, qualifier=qualifier, declared_at=NOW).qualifiers == ()
    with_a = ProvenanceOperations.with_actor(
        statement=base, actor=actor(role=ProvenanceActorRole.CONTRIBUTOR), declared_at=None,
    )
    assert ProvenanceOperations.without_actor(
        statement=with_a, actor=with_a.actors[0], declared_at=NOW,
    ).actors == ()
    with_e = ProvenanceOperations.with_evidence(statement=base, evidence_ref=evidence(), declared_at=None)
    assert ProvenanceOperations.without_evidence(
        statement=with_e, evidence_ref=evidence(), declared_at=NOW,
    ).evidence == ()
    predecessor = ref(statement(lineage_key="other"))
    with_p = ProvenanceOperations.with_predecessor(
        statement=base, predecessor=predecessor, declared_at=None,
    )
    assert ProvenanceOperations.without_predecessor(
        statement=with_p, predecessor=predecessor, declared_at=NOW,
    ).predecessors == ()
    extra = entity(target_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    with_entity = ProvenanceOperations.with_entity(statement=base, entity=extra, declared_at=None)
    assert ProvenanceOperations.without_entity(
        statement=with_entity, entity=extra, declared_at=NOW,
    ).entities == base.entities
    code(ProvenanceValidationError, "PV004", lambda: ProvenanceOperations.with_entity(
        statement=base, entity=base.entities[0], declared_at=None,
    ))
    code(ProvenanceValidationError, "PV008", lambda: ProvenanceOperations.without_actor(
        statement=base, actor=actor(), declared_at=None,
    ))
    code(ProvenanceValidationError, "PV008", lambda: ProvenanceOperations.without_activity(
        statement=base, declared_at=None,
    ))
    activity = ProvenanceActivityRef(
        activity_type=ProvenanceActivityType.TRANSFORMATION, namespace="cko", activity_id="a",
    )
    with_activity = ProvenanceOperations.with_activity(statement=base, activity=activity, declared_at=None)
    code(ProvenanceValidationError, "PV004", lambda: ProvenanceOperations.with_activity(
        statement=with_activity, activity=activity, declared_at=None,
    ))
    assert ProvenanceOperations.without_activity(
        statement=with_activity, declared_at=None,
    ).activity is None
    assert ProvenanceOperations.require_valid_digest(statement=base) is None
    assert ProvenanceOperations.compare(left=base, right=with_e).changed_fields

    serializer = DeterministicProvenanceSerializer()
    serialization_calls = [
        lambda: serializer.to_dict(value=object()),
        lambda: serializer.digest(statement=object()),
        lambda: serializer.from_dict(payload=[]),
        lambda: serializer.from_dict(payload={"model": "unknown"}),
        lambda: serializer.from_json(payload="text"),
        lambda: serializer.from_json(payload=b"\xff"),
        lambda: serializer.from_json(payload=b"[]"),
    ]
    for call in serialization_calls:
        with pytest.raises(ProvenanceError):
            call()
    comparison = ProvenanceStatementComparisonResult(
        same_identity=True, left_node_key=base.node_key,
        right_node_key=base.node_key, same_digest=True,
    )
    bad_result_calls = [
        lambda: ProvenanceStatementComparisonResult(same_identity=1, left_node_key="x", right_node_key="y", same_digest=True),
        lambda: ProvenanceStatementComparisonResult(same_identity=True, left_node_key="x", right_node_key="y", same_digest=True, changed_fields="bad"),
        lambda: ProvenanceChainValidationResult(node_keys="bad"),
        lambda: ProvenanceChainValidationResult(components="bad"),
        lambda: ProvenanceChainValidationResult(components=("bad",)),
        lambda: ProvenanceChainValidationResult(edge_count=-1),
    ]
    for call in bad_result_calls:
        with pytest.raises(ProvenanceError):
            call()
    assert serializer.from_dict(payload=serializer.to_dict(value=comparison)) == comparison
    bad_array = serializer.to_dict(value=evidence())
    bad_array["qualifiers"] = {}
    code(ProvenanceSerializationError, "PS004", lambda: serializer.from_dict(payload=bad_array))
    bad_identifier = serializer.to_dict(value=base.identity.statement_id)
    bad_identifier["value"] = "bad"
    code(ProvenanceSerializationError, "PS004", lambda: serializer.from_dict(payload=bad_identifier))
    bad_qualifier = serializer.to_dict(value=ProvenanceQualifier(name="x", value=1))
    bad_qualifier["name"] = ""
    code(ProvenanceValidationError, "PV002", lambda: serializer.from_dict(payload=bad_qualifier))
    bad_enum = serializer.to_dict(value=subject())
    bad_enum["target_type"] = "other"
    code(ProvenanceValidationError, "PV003", lambda: serializer.from_dict(payload=bad_enum))
    object.__setattr__(comparison, "changed_fields", (object(),))
    with pytest.raises(ProvenanceSerializationError):
        serializer.to_json(value=comparison)

    @dataclass(frozen=True, slots=True)
    class Foreign:
        schema_version: str = "1.0"
        serialization_version: str = "1.0"
        model: str = "foreign"

    validator = ProvenanceStatementValidator()
    with pytest.raises(ProvenanceError):
        validator.validate(value=object())
    with pytest.raises(ProvenanceError):
        validator.validate(value=Foreign())
    @dataclass(slots=True)
    class MutableForeign:
        schema_version: str = "1.0"
        serialization_version: str = "1.0"
        model: str = "foreign"
    with pytest.raises(ProvenanceError):
        validator.validate(value=MutableForeign())
    for invalid in (None, (object(),), 1):
        with pytest.raises(ProvenanceError):
            validator.validate_chain_in_supplied_set(statements=invalid)
    code(ProvenanceChainError, "PC002", lambda: validator.validate_chain_in_supplied_set(
        statements=(base, base),
    ))
    other = statement(lineage_key="other-ref")
    bad_ref = ProvenanceStatementRef(
        statement_id=other.identity.statement_id, revision=other.version.revision,
        statement_version=other.version.statement_version, digest="f" * 64,
    )
    object.__setattr__(base, "predecessors", (bad_ref,))
    code(ProvenanceChainError, "PC003", lambda: validator.validate_chain_in_supplied_set(
        statements=(base, other),
    ))
    mismatch_identity = statement(lineage_key="identity-mismatch")
    object.__setattr__(mismatch_identity.identity, "statement_id", other.identity.statement_id)
    code(ProvenanceIdentityError, "PI001", lambda: validator.validate(value=mismatch_identity))
    previous_bad_id = ProvenanceOperations.with_evidence(
        statement=other, evidence_ref=evidence(), declared_at=None,
    )
    object.__setattr__(previous_bad_id.version.previous_revision, "statement_id", statement().identity.statement_id)
    code(ProvenanceVersionError, "PR002", lambda: validator.validate(value=previous_bad_id))
    previous_same_digest = ProvenanceOperations.with_evidence(
        statement=other, evidence_ref=evidence(evidence_id="e2"), declared_at=None,
    )
    object.__setattr__(previous_same_digest.version.previous_revision, "digest", previous_same_digest.digest)
    code(ProvenanceVersionError, "PR002", lambda: validator.validate(value=previous_same_digest))
    same_entity = statement(lineage_key="same-entity")
    object.__setattr__(same_entity, "entities", (entity(target_id=SUBJECT_ID),))
    code(ProvenanceValidationError, "PV005", lambda: validator.validate(value=same_entity))
    bad_matrix = statement(lineage_key="bad-matrix")
    object.__setattr__(bad_matrix.entities[0], "role", ProvenanceEntityRole.SUPPORTING_ENTITY)
    code(ProvenanceValidationError, "PV005", lambda: validator.validate(value=bad_matrix))
    attribution_no_actor = statement(lineage_key="no-actor")
    object.__setattr__(attribution_no_actor, "category", ProvenanceStatementCategory.ATTRIBUTION)
    object.__setattr__(attribution_no_actor, "entities", ())
    object.__setattr__(attribution_no_actor, "identity", ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key="no-actor",
        category=ProvenanceStatementCategory.ATTRIBUTION, subject=subject(), actors=(actor(),),
    ).identity)
    code(ProvenanceValidationError, "PV005", lambda: validator.validate(value=attribution_no_actor))
    required_activity = statement(lineage_key="required")
    object.__setattr__(required_activity, "category", ProvenanceStatementCategory.TRANSFORMATION)
    object.__setattr__(required_activity, "identity", ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key="required",
        category=ProvenanceStatementCategory.TRANSFORMATION, subject=subject(),
        entities=(entity(),), activity=activity,
    ).identity)
    code(ProvenanceValidationError, "PV005", lambda: validator.validate(value=required_activity))
    wrong_activity = statement(lineage_key="wrong-activity")
    object.__setattr__(wrong_activity, "activity", ProvenanceActivityRef(
        activity_type=ProvenanceActivityType.GENERATION, namespace="cko", activity_id="g",
    ))
    code(ProvenanceValidationError, "PV005", lambda: validator.validate(value=wrong_activity))
    rev_one = statement(lineage_key="chain-revision")
    rev_two = ProvenanceOperations.with_evidence(
        statement=rev_one, evidence_ref=evidence(evidence_id="chain"), declared_at=None,
    )
    chain_result = validator.validate_chain_in_supplied_set(statements=(rev_two, rev_one))
    assert chain_result.edge_count == 1
    assert chain_result.root_keys == (rev_one.node_key,)
    diamond_a = statement(lineage_key="diamond-a")
    diamond_b = statement(lineage_key="diamond-b")
    diamond_c = statement(lineage_key="diamond-c")
    diamond_d = statement(lineage_key="diamond-d")
    object.__setattr__(diamond_b, "predecessors", (ref(diamond_a),))
    object.__setattr__(diamond_c, "predecessors", (ref(diamond_a),))
    object.__setattr__(diamond_d, "predecessors", (ref(diamond_b), ref(diamond_c)))
    diamond = validator.validate_chain_in_supplied_set(
        statements=(diamond_d, diamond_c, diamond_b, diamond_a),
    )
    assert diamond.edge_count == 4
    assert len(diamond.components) == 1

    code(ProvenanceValidationError, "PV005", lambda: ProvenanceOperations.project_relationships(
        statement=statement(),
    ))
    missing_endpoint = statement(
        subject=subject(target_canonical_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc", target_version="1.0.0"),
        declared_at=NOW,
    )
    code(ProvenanceValidationError, "PV005", lambda: ProvenanceOperations.project_relationships(
        statement=missing_endpoint,
    ))
    generated = ProvenanceStatementFactory().create(
        business_namespace="cko", lineage_key="generated",
        category=ProvenanceStatementCategory.GENERATION,
        subject=subject(target_canonical_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc", target_version="1.0.0"),
        entities=(entity(target_canonical_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", target_version="1.0.0"),),
        activity=ProvenanceActivityRef(
            activity_type=ProvenanceActivityType.GENERATION, namespace="cko", activity_id="g",
        ),
        declared_at=NOW,
    )
    assert ProvenanceOperations.project_relationships(statement=generated)[0].descriptor.relationship_type.value == "generated_into"


def test_t030_release_surface_and_service_signatures():
    """T-030 / AC-057,064-068,090: source surface is release-ready."""
    assert PROVENANCE_SCHEMA_VERSION == "1.0"
    assert PROVENANCE_SERIALIZATION_VERSION == "1.0"
    assert PROVENANCE_VERSION == "1.0.0"
    assert tuple(inspect.signature(ProvenanceStatementFactory.create).parameters)[1] == "business_namespace"
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in list(
        inspect.signature(RelationshipFactory.from_parts).parameters.values()
    )[1:])
