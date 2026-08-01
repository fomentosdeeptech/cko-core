"""Infrastructure-neutral Discovery identity evaluator and resolution engine."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime

from cko.core.identity import CanonicalId
from cko.core.logging import get_logger

from .cancellation import CancellationToken
from .foundation_errors import DiscoveryCancelledError
from .identity_contracts import (
    CanonicalIdentityAllocator,
    IdentityCandidateProvider,
    IdentityEvidenceEvaluator,
)
from .identity_errors import (
    IdentityAllocationError,
    IdentityCandidateProviderError,
    IdentityEvidenceEvaluationError,
    IdentityResolutionCancelledError,
    InvalidIdentityResolutionRequestError,
)
from .identity_models import (
    ConflictBehavior,
    ConflictSeverity,
    EvidenceEvaluation,
    IdentityCandidate,
    IdentityConflict,
    IdentityEvidence,
    IdentityResolutionRequest,
    InsufficientEvidenceBehavior,
    ResolutionDecision,
    ResolutionStatus,
)


class DefaultCanonicalIdentityAllocator:
    """Allocate transient identities exclusively through ``CanonicalId.new``."""

    def allocate(self, request: IdentityResolutionRequest) -> CanonicalId:
        """Allocate a new canonical identity without side effects."""
        if not isinstance(request, IdentityResolutionRequest):
            raise InvalidIdentityResolutionRequestError("request is invalid")
        return CanonicalId.new()

    async def allocate_async(self, request: IdentityResolutionRequest) -> CanonicalId:
        """Allocate asynchronously without threads or I/O."""
        return self.allocate(request)


class DefaultNeutralEvidenceEvaluator:
    """Compare declared logical values with exact, platform-neutral semantics."""

    def evaluate(
        self,
        request: IdentityResolutionRequest,
        candidate: IdentityCandidate,
    ) -> EvidenceEvaluation:
        """Evaluate exact matches, differences and absent comparable values."""
        if not isinstance(request, IdentityResolutionRequest):
            raise InvalidIdentityResolutionRequestError("request is invalid")
        if not isinstance(candidate, IdentityCandidate):
            raise InvalidIdentityResolutionRequestError("candidate is invalid")
        observed = {(item.evidence_type.value, item.key): item for item in request.evidence}
        known = {(item.evidence_type.value, item.key): item for item in candidate.evidence}
        favorable: list[IdentityEvidence] = []
        contrary: list[IdentityEvidence] = []
        conflicts: list[IdentityConflict] = []
        missing: list[str] = []
        favorable_weight = 0.0
        comparable_weight = 0.0

        for identity_key in sorted(set(observed) | set(known)):
            observation = observed.get(identity_key)
            candidate_evidence = known.get(identity_key)
            label = f"{identity_key[0]}:{identity_key[1]}"
            if observation is None or candidate_evidence is None:
                missing.append(label)
                continue
            weight = request.policy.evidence_weights.get(
                label,
                request.policy.evidence_weights.get(identity_key[0], 1.0),
            )
            comparable_weight += weight
            if _normalized(observation.value) == _normalized(candidate_evidence.value):
                favorable.append(observation)
                favorable_weight += weight
            else:
                contrary.append(observation)
                conflicts.append(
                    IdentityConflict(
                        attribute=label,
                        observed_value=observation.value,
                        candidate_value=candidate_evidence.value,
                        severity=ConflictSeverity.ERROR,
                        evidence=observation,
                        code="identity.value_mismatch",
                        description="Supplied comparable identity values differ.",
                    )
                )

        score = 0.0 if comparable_weight == 0.0 else favorable_weight / comparable_weight
        confidence = score * candidate.confidence
        return EvidenceEvaluation(
            candidate=candidate,
            favorable=tuple(favorable),
            contrary=tuple(contrary),
            missing=tuple(missing),
            score=score,
            confidence=confidence,
            conflicts=tuple(conflicts),
        )

    async def evaluate_async(
        self,
        request: IdentityResolutionRequest,
        candidate: IdentityCandidate,
    ) -> EvidenceEvaluation:
        """Evaluate asynchronously with behavior equivalent to sync mode."""
        return self.evaluate(request, candidate)


class IdentityResolutionEngine:
    """Canonical deterministic engine for explicit identity decisions."""

    def __init__(
        self,
        *,
        candidate_provider: IdentityCandidateProvider | None = None,
        evaluator: IdentityEvidenceEvaluator | None = None,
        allocator: CanonicalIdentityAllocator | None = None,
        clock: Callable[[], datetime] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Create an engine composed only from injected public strategies."""
        self._provider = candidate_provider
        self._evaluator = evaluator or DefaultNeutralEvidenceEvaluator()
        self._allocator = allocator or DefaultCanonicalIdentityAllocator()
        self._clock = clock or (lambda: datetime.now(UTC))
        self._logger = logger or get_logger("core.discovery.identity_resolution")

    def resolve(
        self,
        request: IdentityResolutionRequest,
        cancellation_token: CancellationToken | None = None,
    ) -> ResolutionDecision:
        """Resolve identity synchronously with cooperative cancellation."""
        token = cancellation_token or CancellationToken.create()
        self._validate(request, token)
        candidates = list(request.known_candidates)
        if self._provider is not None:
            try:
                token.throw_if_cancelled()
                supplied = self._provider.provide(request, token)
                candidates.extend(supplied)
            except DiscoveryCancelledError as error:
                raise IdentityResolutionCancelledError(str(error)) from error
            except Exception as error:
                raise IdentityCandidateProviderError(
                    "identity candidate provider failed"
                ) from error
        prepared = self._prepare_candidates(candidates, request)
        evaluations: list[EvidenceEvaluation] = []
        for candidate in prepared:
            self._check_cancelled(token)
            try:
                evaluations.append(self._evaluator.evaluate(request, candidate))
            except Exception as error:
                raise IdentityEvidenceEvaluationError(
                    "identity evidence evaluator failed"
                ) from error
        return self._decide(request, evaluations, self._allocate_sync)

    async def resolve_async(
        self,
        request: IdentityResolutionRequest,
        cancellation_token: CancellationToken | None = None,
    ) -> ResolutionDecision:
        """Resolve identity asynchronously without threads or multiprocessing."""
        token = cancellation_token or CancellationToken.create()
        self._validate(request, token)
        candidates = list(request.known_candidates)
        if self._provider is not None:
            try:
                token.throw_if_cancelled()
                supplied = await self._provider.provide_async(request, token)
                candidates.extend(supplied)
            except DiscoveryCancelledError as error:
                raise IdentityResolutionCancelledError(str(error)) from error
            except Exception as error:
                raise IdentityCandidateProviderError(
                    "identity candidate provider failed"
                ) from error
        prepared = self._prepare_candidates(candidates, request)
        evaluations: list[EvidenceEvaluation] = []
        for candidate in prepared:
            self._check_cancelled(token)
            try:
                evaluations.append(await self._evaluator.evaluate_async(request, candidate))
            except Exception as error:
                raise IdentityEvidenceEvaluationError(
                    "identity evidence evaluator failed"
                ) from error
        return await self._decide_async(request, evaluations)

    def _validate(
        self,
        request: IdentityResolutionRequest,
        token: CancellationToken,
    ) -> None:
        if not isinstance(request, IdentityResolutionRequest):
            raise InvalidIdentityResolutionRequestError(
                "request must be IdentityResolutionRequest"
            )
        if not isinstance(token, CancellationToken):
            raise InvalidIdentityResolutionRequestError(
                "cancellation_token must be CancellationToken"
            )
        self._check_cancelled(token)

    @staticmethod
    def _check_cancelled(token: CancellationToken) -> None:
        try:
            token.throw_if_cancelled()
        except DiscoveryCancelledError as error:
            raise IdentityResolutionCancelledError(str(error)) from error

    @staticmethod
    def _prepare_candidates(
        candidates: list[IdentityCandidate],
        request: IdentityResolutionRequest,
    ) -> tuple[IdentityCandidate, ...]:
        if any(not isinstance(item, IdentityCandidate) for item in candidates):
            raise InvalidIdentityResolutionRequestError(
                "candidate provider returned an invalid candidate"
            )
        identifiers = [item.canonical_id for item in candidates]
        if len(set(identifiers)) != len(identifiers):
            raise InvalidIdentityResolutionRequestError(
                "duplicate candidate CanonicalId values are not allowed"
            )
        ordered = sorted(candidates, key=lambda item: str(item.canonical_id))
        return tuple(ordered[: request.policy.max_candidates])

    def _decide(
        self,
        request: IdentityResolutionRequest,
        evaluations: list[EvidenceEvaluation],
        allocate: Callable[[IdentityResolutionRequest], CanonicalId],
    ) -> ResolutionDecision:
        status, selected, confidence, conflicts, warnings, rationale = self._classify(
            request, evaluations
        )
        canonical_id: CanonicalId | None = None
        if status is ResolutionStatus.RESOLVED_EXISTING and selected is not None:
            canonical_id = selected.canonical_id
        elif status is ResolutionStatus.RESOLVED_NEW:
            canonical_id = allocate(request)
        return self._decision(
            request, evaluations, status, selected, canonical_id,
            confidence, conflicts, warnings, rationale,
        )

    async def _decide_async(
        self,
        request: IdentityResolutionRequest,
        evaluations: list[EvidenceEvaluation],
    ) -> ResolutionDecision:
        status, selected, confidence, conflicts, warnings, rationale = self._classify(
            request, evaluations
        )
        canonical_id: CanonicalId | None = None
        if status is ResolutionStatus.RESOLVED_EXISTING and selected is not None:
            canonical_id = selected.canonical_id
        elif status is ResolutionStatus.RESOLVED_NEW:
            try:
                canonical_id = await self._allocator.allocate_async(request)
            except Exception as error:
                raise IdentityAllocationError("canonical identity allocation failed") from error
            if not isinstance(canonical_id, CanonicalId):
                raise IdentityAllocationError("allocator returned an invalid CanonicalId")
        return self._decision(
            request, evaluations, status, selected, canonical_id,
            confidence, conflicts, warnings, rationale,
        )

    def _allocate_sync(self, request: IdentityResolutionRequest) -> CanonicalId:
        try:
            canonical_id = self._allocator.allocate(request)
        except Exception as error:
            raise IdentityAllocationError("canonical identity allocation failed") from error
        if not isinstance(canonical_id, CanonicalId):
            raise IdentityAllocationError("allocator returned an invalid CanonicalId")
        return canonical_id

    @staticmethod
    def _classify(
        request: IdentityResolutionRequest,
        evaluations: list[EvidenceEvaluation],
    ) -> tuple[
        ResolutionStatus, IdentityCandidate | None, float,
        tuple[IdentityConflict, ...], tuple[str, ...], dict[str, object]
    ]:
        policy = request.policy
        present_keys = {item.key for item in request.evidence}
        missing_required = sorted(set(policy.required_attributes) - present_keys)
        if not request.evidence or missing_required:
            status = (
                ResolutionStatus.REJECTED
                if policy.insufficient_evidence_behavior is InsufficientEvidenceBehavior.REJECT
                else ResolutionStatus.INSUFFICIENT_EVIDENCE
            )
            return status, None, 0.0, (), tuple(
                f"missing required evidence: {item}" for item in missing_required
            ), {"reason": "insufficient_evidence", "missing_required": missing_required}

        ordered = sorted(
            evaluations,
            key=lambda item: (-item.confidence, -item.score, str(item.candidate.canonical_id)),
        )
        if not ordered:
            if policy.allow_new_identity:
                return ResolutionStatus.RESOLVED_NEW, None, 1.0, (), (), {
                    "reason": "no_known_candidate", "evaluated_candidates": 0
                }
            return ResolutionStatus.REJECTED, None, 0.0, (), (
                "new identity allocation is prohibited by policy",
            ), {"reason": "new_identity_prohibited", "evaluated_candidates": 0}

        best = ordered[0]
        second_confidence = ordered[1].confidence if len(ordered) > 1 else 0.0
        margin = best.confidence - second_confidence
        conflicts = best.conflicts
        rationale: dict[str, object] = {
            "reason": "candidate_evaluated",
            "best_candidate": str(best.candidate.canonical_id),
            "best_confidence": best.confidence,
            "second_confidence": second_confidence,
            "candidate_margin": margin,
            "evaluated_candidates": len(ordered),
        }
        if conflicts and policy.conflict_behavior is ConflictBehavior.REJECT:
            rationale["reason"] = "conflict_detected"
            return ResolutionStatus.CONFLICT, None, best.confidence, conflicts, (), rationale
        if best.confidence >= policy.minimum_match_confidence:
            if len(ordered) > 1 and margin < policy.minimum_candidate_margin:
                rationale["reason"] = "candidate_margin_below_minimum"
                return ResolutionStatus.AMBIGUOUS, None, best.confidence, conflicts, (), rationale
            rationale["reason"] = "existing_candidate_matched"
            return (
                ResolutionStatus.RESOLVED_EXISTING,
                best.candidate,
                best.confidence,
                conflicts,
                (),
                rationale,
            )
        if best.confidence >= policy.minimum_duplicate_confidence:
            rationale["reason"] = "possible_duplicate"
            return (
                ResolutionStatus.DUPLICATE_CANDIDATE,
                None,
                best.confidence,
                conflicts,
                (),
                rationale,
            )
        if policy.allow_new_identity:
            rationale["reason"] = "no_candidate_above_threshold"
            return ResolutionStatus.RESOLVED_NEW, None, best.confidence, conflicts, (), rationale
        rationale["reason"] = "new_identity_prohibited"
        return ResolutionStatus.REJECTED, None, best.confidence, conflicts, (
            "new identity allocation is prohibited by policy",
        ), rationale

    def _decision(
        self,
        request: IdentityResolutionRequest,
        evaluations: list[EvidenceEvaluation],
        status: ResolutionStatus,
        selected: IdentityCandidate | None,
        canonical_id: CanonicalId | None,
        confidence: float,
        conflicts: tuple[IdentityConflict, ...],
        warnings: tuple[str, ...],
        rationale: dict[str, object],
    ) -> ResolutionDecision:
        considered = tuple(
            item.candidate for item in sorted(
                evaluations,
                key=lambda item: (-item.confidence, -item.score, str(item.candidate.canonical_id)),
            )
        )
        evidence_used = tuple(
            evidence for evaluation in evaluations
            for evidence in evaluation.favorable + evaluation.contrary
        )
        decision = ResolutionDecision(
            status=status, canonical_id=canonical_id, selected_candidate=selected,
            considered_candidates=considered, confidence=confidence,
            evidence_used=evidence_used, conflicts=conflicts, warnings=warnings,
            justification=rationale, timestamp=self._clock(),
            request_id=request.context.correlation_id, session_id=request.session.id,
        )
        self._logger.info(
            "identity resolution completed",
            extra={"context": {"request_id": decision.request_id,
                               "session_id": str(decision.session_id),
                               "status": decision.status.value,
                               "candidate_count": len(considered)}},
        )
        return decision


def _normalized(value: object) -> str:
    """Return a stable exact-comparison representation for supplied values."""
    if isinstance(value, str):
        return value.strip().casefold()
    return str(value)


__all__ = [
    "DefaultCanonicalIdentityAllocator",
    "DefaultNeutralEvidenceEvaluator",
    "IdentityResolutionEngine",
]
