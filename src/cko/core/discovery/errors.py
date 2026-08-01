"""Stable domain errors for the CKO Discovery boundary."""

from __future__ import annotations

from cko.core.exceptions import CKOError


class DiscoveryError(CKOError):
    """Base error for all public Discovery failures."""


class InvalidDiscoveryRequestError(DiscoveryError, ValueError):
    """Raised when a discovery request violates a canonical invariant."""


class InvalidDiscoverySourceError(DiscoveryError, ValueError):
    """Raised when a source does not satisfy the source contract."""


class InvalidDiscoveredItemError(DiscoveryError, ValueError):
    """Raised when an observed item is incomplete or inconsistent."""


class UnsupportedDiscoveryCapabilityError(DiscoveryError):
    """Raised when a request requires a capability absent from its source."""


class DiscoveryProviderError(DiscoveryError):
    """Raised when a provider fails behind the Discovery boundary."""


class DiscoveryMappingError(DiscoveryError):
    """Raised when an observation cannot be mapped to a canonical Asset."""


class DiscoveryValidationError(DiscoveryError, ValueError):
    """Raised when a result violates cross-model invariants."""


__all__ = [
    "DiscoveryError",
    "DiscoveryMappingError",
    "DiscoveryProviderError",
    "DiscoveryValidationError",
    "InvalidDiscoveredItemError",
    "InvalidDiscoveryRequestError",
    "InvalidDiscoverySourceError",
    "UnsupportedDiscoveryCapabilityError",
]
