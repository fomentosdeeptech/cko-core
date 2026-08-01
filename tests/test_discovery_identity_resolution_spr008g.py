"""Acceptance tests for SPR-008G Discovery identity resolution."""

from __future__ import annotations

import asyncio
import ast
import dataclasses
import inspect
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType

import pytest

from cko.core import CanonicalId, UniversalMetadata
from cko.core.discovery import (
    CancellationToken,
    ConflictBehavior,
    DefaultNeutralEvidenceEvaluator,
    DiscoveredItem,
    DiscoveryContext,
    DiscoveryPolicy,
    DiscoveryRequest,
    DiscoveryScope,
    DiscoverySession,
    DiscoverySourceId,
    EvidenceEvaluation,
    IdentityCandidate,
    IdentityCandidateProviderError,
    IdentityAllocationError,
    IdentityEvidence,
    IdentityEvidenceEvaluationError,
    IdentityEvidenceType,
    IdentityFingerprint,
    IdentityResolutionCancelledError,
    IdentityResolutionEngine,
    IdentityResolutionRequest,
    InsufficientEvidenceBehavior,
    InvalidIdentityCandidateError,
    InvalidIdentityEvidenceError,
    InvalidIdentityPolicyError,
    InvalidIdentityResolutionRequestError,
    ResolutionPolicy,
    ResolutionStatus,
    DefaultCanonicalIdentityAllocator,
)


NOW = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)
ID_A = CanonicalId.parse("00000000-0000-4000-8000-000000000001")
ID_B = CanonicalId.parse("00000000-0000-4000-8000-000000000002")
ID_NEW = CanonicalId.parse("00000000-0000-4000-8000-000000000099")


def evidence(value: object = "doc-1", *, key: str = "external_id") -> IdentityEvidence:
    """Build exact logical evidence."""
    return IdentityEvidence(
        IdentityEvidenceType.EXTERNAL_IDENTIFIER,
        key,
        value,
        "test",
    )


def candidate(
    canonical_id: CanonicalId = ID_A,
    *,
    value: object = "doc-1",
    confidence: float = 1.0,
) -> IdentityCandidate:
    """Build a supplied candidate."""
    return IdentityCandidate(
        canonical_id=canonical_id,
        attributes={"kind": "document"},
        evidence=(evidence(value),),
        logical_origin="test-provider",
        confidence=confidence,
        metadata={"tenant": "neutral"},
    )


def resolution_request(
    *,
    candidates: tuple[IdentityCandidate, ...] = (),
    supplied_evidence: tuple[IdentityEvidence, ...] | None = None,
    policy: ResolutionPolicy | None = None,
) -> IdentityResolutionRequest:
    """Build a request associated with canonical Discovery contracts."""
    context = DiscoveryContext("corr-008g", NOW, actor="tests")
    source_id = DiscoverySourceId("logical-source")
    discovery_request = DiscoveryRequest(
        CanonicalId.parse("00000000-0000-4000-8000-000000000010"),
        source_id,
        DiscoveryScope("logical-root"),
        DiscoveryPolicy(),
        context,
    )
    session = DiscoverySession(
        CanonicalId.parse("00000000-0000-4000-8000-000000000011"),
        discovery_request,
        context,
    )
    metadata = UniversalMetadata("application/pdf", NOW, NOW, attributes={})
    item = DiscoveredItem(
        source_id,
        "logical/document.pdf",
        NOW,
        "declared",
        context.correlation_id,
        metadata,
    )
    return IdentityResolutionRequest(
        item,
        session,
        context,
        (evidence(),) if supplied_evidence is None else supplied_evidence,
        policy or ResolutionPolicy(),
        candidates,
    )


class FixedAllocator:
    """Deterministic test allocator implementing both public modes."""

    def allocate(self, request: IdentityResolutionRequest) -> CanonicalId:
        return ID_NEW

    async def allocate_async(self, request: IdentityResolutionRequest) -> CanonicalId:
        return ID_NEW


def engine(**kwargs: object) -> IdentityResolutionEngine:
    """Build a deterministic engine."""
    allocator = kwargs.pop("allocator", FixedAllocator())
    return IdentityResolutionEngine(
        allocator=allocator,  # type: ignore[arg-type]
        clock=lambda: NOW,
        **kwargs,
    )


def test_models_are_immutable_and_defensively_freeze_mappings() -> None:
    item = evidence()
    assert isinstance(item.metadata, MappingProxyType)
    with pytest.raises(dataclasses.FrozenInstanceError):
        item.key = "changed"  # type: ignore[misc]
    current = candidate()
    with pytest.raises(TypeError):
        current.attributes["new"] = "value"  # type: ignore[index]


def test_versioned_serialization_is_deterministic_and_round_trips() -> None:
    item = evidence()
    assert IdentityEvidence.from_json(item.to_json()) == item
    assert item.to_json() == item.to_json()
    current = candidate()
    assert IdentityCandidate.from_json(current.to_json()) == current
    policy = ResolutionPolicy(evidence_weights={"external_identifier": 0.8})
    assert ResolutionPolicy.from_json(policy.to_json()) == policy


def test_unknown_fields_and_versions_are_rejected() -> None:
    payload = evidence().to_dict()
    payload["unknown"] = True
    with pytest.raises(InvalidIdentityEvidenceError):
        IdentityEvidence.from_dict(payload)
    payload.pop("unknown")
    payload["schema_version"] = "99.0"
    with pytest.raises(InvalidIdentityEvidenceError):
        IdentityEvidence.from_dict(payload)


def test_logical_fingerprint_is_stable_and_declares_components() -> None:
    first = evidence("A", key="a")
    second = evidence("B", key="b")
    one = IdentityFingerprint.create((first, second))
    two = IdentityFingerprint.create((second, first))
    assert one == two
    assert one.components == (
        "external_identifier:a",
        "external_identifier:b",
    )
    assert IdentityFingerprint.from_json(one.to_json()) == one


def test_invalid_evidence_candidate_and_policy_are_rejected() -> None:
    with pytest.raises(InvalidIdentityEvidenceError):
        evidence(None)
    with pytest.raises(InvalidIdentityCandidateError):
        candidate(confidence=1.1)
    with pytest.raises(InvalidIdentityPolicyError):
        ResolutionPolicy(minimum_match_confidence=0.5, minimum_duplicate_confidence=0.6)


def test_neutral_evaluator_explains_favorable_contrary_and_missing() -> None:
    evaluator = DefaultNeutralEvidenceEvaluator()
    request = resolution_request(
        supplied_evidence=(evidence("same"), evidence("extra", key="missing")),
    )
    result = evaluator.evaluate(request, candidate(value="same"))
    assert len(result.favorable) == 1
    assert not result.contrary
    assert result.missing == ("external_identifier:missing",)
    contrary = evaluator.evaluate(resolution_request(), candidate(value="different"))
    assert len(contrary.contrary) == 1
    assert len(contrary.conflicts) == 1
    assert contrary.to_dict()["conflicts"]


def test_unique_candidate_resolves_existing_canonical_id() -> None:
    decision = engine().resolve(resolution_request(candidates=(candidate(),)))
    assert decision.status is ResolutionStatus.RESOLVED_EXISTING
    assert decision.canonical_id == ID_A
    assert decision.selected_candidate == candidate()


def test_no_candidate_allocates_new_identity_without_creating_asset() -> None:
    request = resolution_request()
    decision = engine().resolve(request)
    assert decision.status is ResolutionStatus.RESOLVED_NEW
    assert decision.canonical_id == ID_NEW
    assert decision.selected_candidate is None
    assert request.item.canonical_id is None


def test_possible_duplicate_is_reported_below_match_threshold() -> None:
    decision = engine().resolve(
        resolution_request(candidates=(candidate(confidence=0.7),))
    )
    assert decision.status is ResolutionStatus.DUPLICATE_CANDIDATE


def test_multiple_equal_candidates_are_explicitly_ambiguous() -> None:
    decision = engine().resolve(
        resolution_request(candidates=(candidate(ID_A), candidate(ID_B)))
    )
    assert decision.status is ResolutionStatus.AMBIGUOUS
    assert decision.selected_candidate is None
    assert decision.canonical_id is None


def test_conflict_policy_reports_a_conflict_decision() -> None:
    policy = ResolutionPolicy(conflict_behavior=ConflictBehavior.REJECT)
    decision = engine().resolve(
        resolution_request(candidates=(candidate(value="other"),), policy=policy)
    )
    assert decision.status is ResolutionStatus.CONFLICT
    assert decision.conflicts


def test_empty_or_missing_required_evidence_is_insufficient() -> None:
    empty = engine().resolve(resolution_request(supplied_evidence=()))
    assert empty.status is ResolutionStatus.INSUFFICIENT_EVIDENCE
    assert empty.canonical_id is None
    required = ResolutionPolicy(required_attributes=("checksum",))
    missing = engine().resolve(resolution_request(policy=required))
    assert missing.status is ResolutionStatus.INSUFFICIENT_EVIDENCE


def test_insufficient_and_new_identity_policy_can_reject() -> None:
    insufficient = ResolutionPolicy(
        insufficient_evidence_behavior=InsufficientEvidenceBehavior.REJECT
    )
    assert engine().resolve(
        resolution_request(supplied_evidence=(), policy=insufficient)
    ).status is ResolutionStatus.REJECTED
    no_create = ResolutionPolicy(allow_new_identity=False)
    assert engine().resolve(
        resolution_request(policy=no_create)
    ).status is ResolutionStatus.REJECTED


def test_duplicate_candidates_are_rejected_across_injected_sources() -> None:
    class Provider:
        def provide(self, request: IdentityResolutionRequest, token: CancellationToken) -> tuple[IdentityCandidate, ...]:
            return (candidate(),)

        async def provide_async(self, request: IdentityResolutionRequest, token: CancellationToken) -> tuple[IdentityCandidate, ...]:
            return (candidate(),)

    with pytest.raises(InvalidIdentityResolutionRequestError):
        engine(candidate_provider=Provider()).resolve(
            resolution_request(candidates=(candidate(),))
        )


def test_candidate_limit_and_ordering_are_deterministic() -> None:
    policy = ResolutionPolicy(max_candidates=1)
    request = resolution_request(
        candidates=(candidate(ID_B), candidate(ID_A)),
        policy=policy,
    )
    decision = engine().resolve(request)
    assert decision.considered_candidates == (candidate(ID_A),)


def test_minimum_confidence_and_margin_are_enforced() -> None:
    policy = ResolutionPolicy(minimum_match_confidence=0.9,
                              minimum_duplicate_confidence=0.8)
    decision = engine().resolve(
        resolution_request(candidates=(candidate(confidence=0.7),), policy=policy)
    )
    assert decision.status is ResolutionStatus.RESOLVED_NEW
    margin_policy = ResolutionPolicy(minimum_candidate_margin=0.2)
    ambiguous = engine().resolve(
        resolution_request(
            candidates=(candidate(ID_A, confidence=1.0), candidate(ID_B, confidence=0.9)),
            policy=margin_policy,
        )
    )
    assert ambiguous.status is ResolutionStatus.AMBIGUOUS


def test_cancellation_is_cooperative_and_uses_existing_token() -> None:
    token = CancellationToken.create()
    token.cancel("stop")
    with pytest.raises(IdentityResolutionCancelledError) as captured:
        engine().resolve(resolution_request(), token)
    assert captured.value.__cause__ is not None


def test_provider_and_evaluator_failures_preserve_causes() -> None:
    class FailingProvider:
        def provide(self, request: IdentityResolutionRequest, token: CancellationToken) -> tuple[IdentityCandidate, ...]:
            raise RuntimeError("provider-cause")

        async def provide_async(self, request: IdentityResolutionRequest, token: CancellationToken) -> tuple[IdentityCandidate, ...]:
            raise RuntimeError("provider-cause")

    with pytest.raises(IdentityCandidateProviderError) as provider_error:
        engine(candidate_provider=FailingProvider()).resolve(resolution_request())
    assert isinstance(provider_error.value.__cause__, RuntimeError)

    class FailingEvaluator:
        def evaluate(self, request: IdentityResolutionRequest, current: IdentityCandidate) -> EvidenceEvaluation:
            raise RuntimeError("evaluator-cause")

        async def evaluate_async(self, request: IdentityResolutionRequest, current: IdentityCandidate) -> EvidenceEvaluation:
            raise RuntimeError("evaluator-cause")

    with pytest.raises(IdentityEvidenceEvaluationError) as evaluator_error:
        engine(evaluator=FailingEvaluator()).resolve(
            resolution_request(candidates=(candidate(),))
        )
    assert isinstance(evaluator_error.value.__cause__, RuntimeError)


def test_sync_and_async_modes_are_equivalent() -> None:
    request = resolution_request(candidates=(candidate(),))
    sync_decision = engine().resolve(request)
    async_decision = asyncio.run(engine().resolve_async(request))
    assert sync_decision == async_decision
    assert async_decision.session_id == request.session.id


def test_async_provider_and_new_allocation_paths_are_functional() -> None:
    class Provider:
        def provide(self, request: IdentityResolutionRequest, token: CancellationToken) -> tuple[IdentityCandidate, ...]:
            return (candidate(),)

        async def provide_async(self, request: IdentityResolutionRequest, token: CancellationToken) -> tuple[IdentityCandidate, ...]:
            return (candidate(),)

    existing = asyncio.run(
        engine(candidate_provider=Provider()).resolve_async(resolution_request())
    )
    assert existing.status is ResolutionStatus.RESOLVED_EXISTING
    new = asyncio.run(engine().resolve_async(resolution_request()))
    assert new.status is ResolutionStatus.RESOLVED_NEW
    assert new.canonical_id == ID_NEW


def test_default_allocator_and_allocation_failures_are_public() -> None:
    request = resolution_request()
    allocated = DefaultCanonicalIdentityAllocator().allocate(request)
    assert isinstance(allocated, CanonicalId)
    assert isinstance(
        asyncio.run(DefaultCanonicalIdentityAllocator().allocate_async(request)),
        CanonicalId,
    )

    class BadAllocator:
        def allocate(self, request: IdentityResolutionRequest) -> CanonicalId:
            raise RuntimeError("allocation-cause")

        async def allocate_async(self, request: IdentityResolutionRequest) -> CanonicalId:
            raise RuntimeError("allocation-cause")

    with pytest.raises(IdentityAllocationError) as sync_error:
        engine(allocator=BadAllocator()).resolve(request)
    assert isinstance(sync_error.value.__cause__, RuntimeError)
    with pytest.raises(IdentityAllocationError) as async_error:
        asyncio.run(engine(allocator=BadAllocator()).resolve_async(request))
    assert isinstance(async_error.value.__cause__, RuntimeError)


def test_additional_strict_model_invariants_are_enforced() -> None:
    with pytest.raises(InvalidIdentityEvidenceError):
        IdentityFingerprint.create(())
    with pytest.raises(InvalidIdentityEvidenceError):
        IdentityFingerprint("invalid", ("component",))
    duplicate = evidence("same")
    with pytest.raises(InvalidIdentityEvidenceError):
        IdentityFingerprint.create((duplicate, duplicate))
    with pytest.raises(InvalidIdentityPolicyError):
        ResolutionPolicy(required_attributes=("id", "id"))
    with pytest.raises(InvalidIdentityPolicyError):
        ResolutionPolicy(max_candidates=0)
    with pytest.raises(InvalidIdentityPolicyError):
        ResolutionPolicy(evidence_weights={"id": 0.0})


def test_async_external_failures_preserve_causes() -> None:
    class FailingProvider:
        def provide(self, request: IdentityResolutionRequest, token: CancellationToken) -> tuple[IdentityCandidate, ...]:
            raise RuntimeError("provider-cause")

        async def provide_async(self, request: IdentityResolutionRequest, token: CancellationToken) -> tuple[IdentityCandidate, ...]:
            raise RuntimeError("provider-cause")

    with pytest.raises(IdentityCandidateProviderError) as provider_error:
        asyncio.run(
            engine(candidate_provider=FailingProvider()).resolve_async(
                resolution_request()
            )
        )
    assert isinstance(provider_error.value.__cause__, RuntimeError)


def test_request_and_decision_json_are_versioned_and_auditable() -> None:
    request = resolution_request(candidates=(candidate(),))
    decision = engine().resolve(request)
    assert '"schema_version":"1.0"' in request.to_json()
    assert IdentityResolutionRequest.from_json(
        request.to_json(), request.session
    ) == request
    assert decision.to_json() == decision.to_json()
    assert type(decision).from_json(decision.to_json()) == decision
    assert decision.request_id == request.context.correlation_id
    assert decision.evidence_used
    assert decision.justification["reason"] == "existing_candidate_matched"


def test_conflict_serialization_and_strict_request_decision_envelopes() -> None:
    policy = ResolutionPolicy(conflict_behavior=ConflictBehavior.REJECT)
    request = resolution_request(candidates=(candidate(value="other"),), policy=policy)
    decision = engine().resolve(request)
    conflict = decision.conflicts[0]
    assert type(conflict).from_json(conflict.to_json()) == conflict

    request_payload = request.to_dict()
    request_payload["unknown"] = True
    with pytest.raises(InvalidIdentityResolutionRequestError):
        IdentityResolutionRequest.from_dict(request_payload, request.session)

    decision_payload = decision.to_dict()
    decision_payload["schema_version"] = "2.0"
    with pytest.raises(InvalidIdentityResolutionRequestError):
        type(decision).from_dict(decision_payload)


def test_strict_deserialization_rejects_malformed_public_payloads() -> None:
    request = resolution_request(candidates=(candidate(),))
    with pytest.raises(InvalidIdentityResolutionRequestError):
        IdentityResolutionRequest.from_json("[]", request.session)
    wrong_session = DiscoverySession(
        ID_B,
        request.session.request,
        request.context,
    )
    with pytest.raises(InvalidIdentityResolutionRequestError):
        IdentityResolutionRequest.from_dict(
            request.to_dict(), wrong_session
        )

    conflict_policy = ResolutionPolicy(conflict_behavior=ConflictBehavior.REJECT)
    conflict_decision = engine().resolve(
        resolution_request(
            candidates=(candidate(value="other"),),
            policy=conflict_policy,
        )
    )
    conflict_payload = conflict_decision.conflicts[0].to_dict()
    conflict_payload["schema_version"] = "9.0"
    with pytest.raises(InvalidIdentityEvidenceError):
        type(conflict_decision.conflicts[0]).from_dict(conflict_payload)

    decision_payload = conflict_decision.to_dict()
    decision_payload["considered_candidates"] = "invalid"
    with pytest.raises(InvalidIdentityResolutionRequestError):
        type(conflict_decision).from_dict(decision_payload)


def test_public_api_type_hints_docstrings_and_utf8_without_bom() -> None:
    assert inspect.getdoc(IdentityResolutionEngine)
    assert inspect.getdoc(IdentityResolutionEngine.resolve)
    assert inspect.signature(IdentityResolutionEngine.resolve).return_annotation
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    for name in (
        "identity_errors.py", "identity_models.py", "identity_contracts.py",
        "identity_resolution.py",
    ):
        content = (root / name).read_bytes()
        assert not content.startswith(b"\xef\xbb\xbf")
        content.decode("utf-8")


def test_new_modules_have_no_prohibited_infrastructure_imports() -> None:
    prohibited = {
        "os", "pathlib", "sqlite3", "requests", "urllib", "threading",
        "multiprocessing", "cko.core.inventory",
    }
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    for name in ("identity_models.py", "identity_contracts.py", "identity_resolution.py"):
        tree = ast.parse((root / name).read_text(encoding="utf-8"))
        imports = {
            alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        assert not any(
            imported == blocked or imported.startswith(f"{blocked}.")
            for imported in imports for blocked in prohibited
        )
