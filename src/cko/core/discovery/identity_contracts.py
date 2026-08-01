"""Public injection contracts for Discovery identity resolution."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from cko.core.identity import CanonicalId

from .cancellation import CancellationToken
from .identity_models import (
    EvidenceEvaluation,
    IdentityCandidate,
    IdentityResolutionRequest,
)


@runtime_checkable
class IdentityCandidateProvider(Protocol):
    """Supply known candidates without prescribing storage or infrastructure."""

    def provide(
        self,
        request: IdentityResolutionRequest,
        cancellation_token: CancellationToken,
    ) -> tuple[IdentityCandidate, ...]:
        """Return candidates synchronously."""

    async def provide_async(
        self,
        request: IdentityResolutionRequest,
        cancellation_token: CancellationToken,
    ) -> tuple[IdentityCandidate, ...]:
        """Return candidates asynchronously without requiring threads."""


@runtime_checkable
class IdentityEvidenceEvaluator(Protocol):
    """Evaluate supplied evidence for one observation/candidate pair."""

    def evaluate(
        self,
        request: IdentityResolutionRequest,
        candidate: IdentityCandidate,
    ) -> EvidenceEvaluation:
        """Return a deterministic synchronous evaluation."""

    async def evaluate_async(
        self,
        request: IdentityResolutionRequest,
        candidate: IdentityCandidate,
    ) -> EvidenceEvaluation:
        """Return a deterministic asynchronous evaluation."""


@runtime_checkable
class CanonicalIdentityAllocator(Protocol):
    """Allocate a CanonicalId without persisting or creating an Asset."""

    def allocate(self, request: IdentityResolutionRequest) -> CanonicalId:
        """Allocate an identity synchronously."""

    async def allocate_async(self, request: IdentityResolutionRequest) -> CanonicalId:
        """Allocate an identity asynchronously without requiring threads."""


__all__ = [
    "CanonicalIdentityAllocator",
    "IdentityCandidateProvider",
    "IdentityEvidenceEvaluator",
]
