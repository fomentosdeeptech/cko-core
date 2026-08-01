"""Public errors for Discovery identity resolution."""

from __future__ import annotations

from .errors import DiscoveryError


class IdentityResolutionError(DiscoveryError):
    """Base error for every identity-resolution failure."""


class InvalidIdentityResolutionRequestError(IdentityResolutionError, ValueError):
    """Raised when a resolution request violates a public invariant."""


class InvalidIdentityCandidateError(IdentityResolutionError, ValueError):
    """Raised when a supplied candidate is incomplete or inconsistent."""


class InvalidIdentityEvidenceError(IdentityResolutionError, ValueError):
    """Raised when identity evidence is invalid."""


class InvalidIdentityPolicyError(IdentityResolutionError, ValueError):
    """Raised when a resolution policy is invalid."""


class IdentityCandidateProviderError(IdentityResolutionError):
    """Raised when an injected candidate provider fails."""


class IdentityEvidenceEvaluationError(IdentityResolutionError):
    """Raised when an injected evidence evaluator fails."""


class IdentityAmbiguityError(IdentityResolutionError):
    """Raised when callers require a definitive but ambiguous decision."""


class IdentityConflictError(IdentityResolutionError):
    """Raised when callers require a conflict-free decision."""


class IdentityAllocationError(IdentityResolutionError):
    """Raised when a new canonical identity cannot be allocated."""


class IdentityResolutionCancelledError(IdentityResolutionError):
    """Raised when cooperative identity resolution is cancelled."""


__all__ = [
    "IdentityAllocationError",
    "IdentityAmbiguityError",
    "IdentityCandidateProviderError",
    "IdentityConflictError",
    "IdentityEvidenceEvaluationError",
    "IdentityResolutionCancelledError",
    "IdentityResolutionError",
    "InvalidIdentityCandidateError",
    "InvalidIdentityEvidenceError",
    "InvalidIdentityPolicyError",
    "InvalidIdentityResolutionRequestError",
]
