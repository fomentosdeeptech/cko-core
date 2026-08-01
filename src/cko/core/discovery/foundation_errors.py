"""Public errors for the Discovery Provider Foundation."""

from __future__ import annotations

from .errors import DiscoveryError


class DiscoveryProviderRegistrationError(DiscoveryError, ValueError):
    """Raised when a provider registration is invalid or duplicated."""


class DiscoveryProviderNotFoundError(DiscoveryError, LookupError):
    """Raised when no registered provider satisfies an execution request."""


class DiscoveryProviderResolutionError(DiscoveryError, LookupError):
    """Raised when provider resolution cannot produce a valid candidate."""


class DiscoverySessionStateError(DiscoveryError, RuntimeError):
    """Raised when a session receives an invalid state transition."""


class DiscoveryCancelledError(DiscoveryError):
    """Raised when cooperative cancellation stops a Discovery execution."""


class DiscoveryExecutionError(DiscoveryError, RuntimeError):
    """Raised when a selected provider violates its execution contract."""


__all__ = [
    "DiscoveryCancelledError",
    "DiscoveryExecutionError",
    "DiscoveryProviderNotFoundError",
    "DiscoveryProviderRegistrationError",
    "DiscoveryProviderResolutionError",
    "DiscoverySessionStateError",
]
