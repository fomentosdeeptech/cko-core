"""Public errors for the Discovery capability model."""

from .errors import DiscoveryError


class CapabilityError(DiscoveryError):
    """Base error for every capability-model failure."""


class CapabilityConflictError(CapabilityError):
    """Raised when mutually incompatible capabilities are selected."""


class CapabilityDependencyError(CapabilityError):
    """Raised when a capability dependency cannot be satisfied."""


class CapabilityValidationError(CapabilityError):
    """Raised when a capability set violates declared requirements."""


class CapabilityNegotiationError(CapabilityError):
    """Raised when capability negotiation cannot be performed."""


class InvalidCapabilityError(CapabilityError, ValueError):
    """Raised when a capability model violates a public invariant."""


__all__ = [
    "CapabilityConflictError",
    "CapabilityDependencyError",
    "CapabilityError",
    "CapabilityNegotiationError",
    "CapabilityValidationError",
    "InvalidCapabilityError",
]
