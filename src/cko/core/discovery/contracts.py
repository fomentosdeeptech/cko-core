"""Public ports for Discovery sources, providers, mappers and validators."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from cko.core.models import Asset, CanonicalEvent

from .models import (
    DiscoveredItem,
    DiscoveryCapability,
    DiscoveryRequest,
    DiscoveryResult,
    DiscoverySourceId,
)


@runtime_checkable
class DiscoverySource(Protocol):
    """Abstract source identity and declarative capabilities."""

    @property
    def id(self) -> DiscoverySourceId:
        """Return the stable logical source identity."""

    @property
    def capabilities(self) -> frozenset[DiscoveryCapability]:
        """Return capabilities without executing any of them."""


@runtime_checkable
class DiscoveryProvider(Protocol):
    """Port implemented by an infrastructure adapter outside the core."""

    def discover(
        self,
        source: DiscoverySource,
        request: DiscoveryRequest,
    ) -> DiscoveryResult:
        """Perform logical discovery and return a complete canonical result."""


@runtime_checkable
class DiscoveryAssetMapper(Protocol):
    """Map a validated observation to an Asset without persistence."""

    def map_item(self, item: DiscoveredItem) -> Asset:
        """Return a canonical Asset for an observation with validated identity."""


@runtime_checkable
class DiscoveryEventPublisher(Protocol):
    """Publish canonical Discovery events without choosing a transport."""

    def publish(self, event: CanonicalEvent) -> None:
        """Publish a canonical event."""


@runtime_checkable
class DiscoveryValidator(Protocol):
    """Validate source, request, observation and result boundaries."""

    def validate_source(self, source: DiscoverySource) -> None:
        """Validate a source or raise InvalidDiscoverySourceError."""

    def validate_request(
        self,
        source: DiscoverySource,
        request: DiscoveryRequest,
    ) -> None:
        """Validate request/source compatibility."""

    def validate_item(
        self,
        request: DiscoveryRequest,
        item: DiscoveredItem,
    ) -> None:
        """Validate an observation against its request."""

    def validate_result(
        self,
        request: DiscoveryRequest,
        result: DiscoveryResult,
    ) -> None:
        """Validate a complete provider result."""


__all__ = [
    "DiscoveryAssetMapper",
    "DiscoveryEventPublisher",
    "DiscoveryProvider",
    "DiscoverySource",
    "DiscoveryValidator",
]
