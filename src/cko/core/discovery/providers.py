"""Dynamic registry, resolver and factory for Discovery providers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from cko.core.logging import get_logger
from cko.core.utils import require_non_empty

from .contracts import DiscoveryProvider, DiscoverySource
from .foundation_errors import (
    DiscoveryProviderNotFoundError,
    DiscoveryProviderRegistrationError,
    DiscoveryProviderResolutionError,
)
from .models import DiscoveryCapability, DiscoveryRequest
from .policies import ensure_supported_capabilities


class DiscoveryExecutionMode(str, Enum):
    """Execution styles declared by a provider registration."""

    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"


@dataclass(frozen=True, slots=True)
class DiscoveryProviderDescriptor:
    """Immutable provider registration and its declared capabilities."""

    provider_id: str
    provider: object
    capabilities: frozenset[DiscoveryCapability]
    execution_modes: frozenset[DiscoveryExecutionMode]
    priority: int = 0

    def __post_init__(self) -> None:
        """Normalize declarations and verify provider execution contracts."""
        object.__setattr__(
            self,
            "provider_id",
            require_non_empty(self.provider_id, "provider_id"),
        )
        capabilities = frozenset(
            DiscoveryCapability(value) for value in self.capabilities
        )
        modes = frozenset(
            DiscoveryExecutionMode(value) for value in self.execution_modes
        )
        if not capabilities:
            raise DiscoveryProviderRegistrationError(
                "provider must declare at least one capability"
            )
        if not modes:
            raise DiscoveryProviderRegistrationError(
                "provider must declare at least one execution mode"
            )
        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise TypeError("priority must be an integer")
        if DiscoveryExecutionMode.SYNCHRONOUS in modes and not (
            callable(getattr(self.provider, "discover_context", None))
            or isinstance(self.provider, DiscoveryProvider)
        ):
            raise DiscoveryProviderRegistrationError(
                "synchronous provider must implement discover or discover_context"
            )
        if DiscoveryExecutionMode.ASYNCHRONOUS in modes and not callable(
            getattr(self.provider, "discover_async", None)
        ):
            raise DiscoveryProviderRegistrationError(
                "asynchronous provider must implement discover_async"
            )
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "execution_modes", modes)


class DiscoveryProviderRegistry:
    """Register and expose provider descriptors without global state."""

    def __init__(self) -> None:
        """Initialize an empty instance-scoped provider registry."""
        self._providers: dict[str, DiscoveryProviderDescriptor] = {}
        self._logger = get_logger("core.discovery.provider_registry")

    def register(self, descriptor: DiscoveryProviderDescriptor) -> None:
        """Register a provider descriptor under its unique stable identity."""
        if not isinstance(descriptor, DiscoveryProviderDescriptor):
            raise TypeError("descriptor must be DiscoveryProviderDescriptor")
        if descriptor.provider_id in self._providers:
            raise DiscoveryProviderRegistrationError(
                f"provider is already registered: {descriptor.provider_id}"
            )
        self._providers[descriptor.provider_id] = descriptor
        self._logger.info(
            "discovery provider registered",
            extra={
                "context": {
                    "provider_id": descriptor.provider_id,
                    "capabilities": sorted(
                        capability.value for capability in descriptor.capabilities
                    ),
                    "execution_modes": sorted(
                        mode.value for mode in descriptor.execution_modes
                    ),
                }
            },
        )

    def unregister(self, provider_id: str) -> DiscoveryProviderDescriptor:
        """Remove and return a provider registration by stable identity."""
        normalized = require_non_empty(provider_id, "provider_id")
        try:
            descriptor = self._providers.pop(normalized)
        except KeyError as error:
            raise DiscoveryProviderNotFoundError(
                f"provider is not registered: {normalized}"
            ) from error
        self._logger.info(
            "discovery provider unregistered",
            extra={"context": {"provider_id": normalized}},
        )
        return descriptor

    def get(self, provider_id: str) -> DiscoveryProviderDescriptor:
        """Return a provider registration by stable identity."""
        normalized = require_non_empty(provider_id, "provider_id")
        try:
            return self._providers[normalized]
        except KeyError as error:
            raise DiscoveryProviderNotFoundError(
                f"provider is not registered: {normalized}"
            ) from error

    def descriptors(self) -> Sequence[DiscoveryProviderDescriptor]:
        """Return an identity-ordered immutable registry snapshot."""
        return tuple(self._providers[key] for key in sorted(self._providers))

    def snapshot(self) -> Mapping[str, DiscoveryProviderDescriptor]:
        """Return a read-only identity-indexed snapshot."""
        return MappingProxyType(dict(self._providers))

    def __len__(self) -> int:
        """Return the number of registered provider descriptors."""
        return len(self._providers)


class DiscoveryProviderResolver:
    """Select the deterministic best provider for required capabilities."""

    def resolve(
        self,
        descriptors: Sequence[DiscoveryProviderDescriptor],
        required_capabilities: frozenset[DiscoveryCapability],
        execution_mode: DiscoveryExecutionMode,
    ) -> DiscoveryProviderDescriptor:
        """Resolve by mode, capability coverage, priority and specificity."""
        required = frozenset(
            DiscoveryCapability(value) for value in required_capabilities
        )
        mode = DiscoveryExecutionMode(execution_mode)
        candidates = [
            descriptor
            for descriptor in descriptors
            if mode in descriptor.execution_modes
            and required.issubset(descriptor.capabilities)
        ]
        if not candidates:
            values = ", ".join(sorted(value.value for value in required)) or "none"
            raise DiscoveryProviderResolutionError(
                "no provider satisfies execution mode "
                f"{mode.value} and capabilities: {values}"
            )
        candidates.sort(
            key=lambda item: (
                -item.priority,
                len(item.capabilities - required),
                item.provider_id,
            )
        )
        return candidates[0]


class DiscoveryProviderFactory:
    """Create a provider selection from source and request contracts."""

    def __init__(
        self,
        registry: DiscoveryProviderRegistry,
        resolver: DiscoveryProviderResolver,
    ) -> None:
        """Initialize the factory with an injected registry and resolver."""
        self._registry = registry
        self._resolver = resolver

    def create(
        self,
        source: DiscoverySource,
        request: DiscoveryRequest,
        execution_mode: DiscoveryExecutionMode,
        *,
        provider_id: str | None = None,
    ) -> DiscoveryProviderDescriptor:
        """Return a compatible registered provider descriptor."""
        if source.id != request.source_id:
            raise DiscoveryProviderResolutionError(
                "source identity does not match request source_id"
            )
        required = frozenset(request.required_capabilities)
        ensure_supported_capabilities(required, source.capabilities)
        mode = DiscoveryExecutionMode(execution_mode)
        if provider_id is None:
            return self._resolver.resolve(
                self._registry.descriptors(),
                required,
                mode,
            )
        descriptor = self._registry.get(provider_id)
        if mode not in descriptor.execution_modes:
            raise DiscoveryProviderResolutionError(
                f"provider {descriptor.provider_id} does not support {mode.value}"
            )
        missing = required - descriptor.capabilities
        if missing:
            values = ", ".join(sorted(value.value for value in missing))
            raise DiscoveryProviderResolutionError(
                f"provider {descriptor.provider_id} lacks capabilities: {values}"
            )
        return descriptor


__all__ = [
    "DiscoveryExecutionMode",
    "DiscoveryProviderDescriptor",
    "DiscoveryProviderFactory",
    "DiscoveryProviderRegistry",
    "DiscoveryProviderResolver",
]
