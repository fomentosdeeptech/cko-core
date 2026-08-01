"""Synchronous and asynchronous execution contracts for Discovery providers."""

from __future__ import annotations

from dataclasses import dataclass
from inspect import isawaitable
from typing import Protocol, runtime_checkable

from cko.core.logging import get_logger

from .cancellation import CancellationToken
from .checkpoints import DiscoveryCheckpoint
from .contracts import DiscoveryProvider, DiscoverySource, DiscoveryValidator
from .foundation_errors import DiscoveryExecutionError
from .models import DiscoveryRequest, DiscoveryResult
from .providers import DiscoveryProviderDescriptor
from .session import DiscoverySession


@dataclass(frozen=True, slots=True)
class DiscoveryExecutionContext:
    """Complete provider call context independent of infrastructure."""

    source: DiscoverySource
    request: DiscoveryRequest
    session: DiscoverySession
    cancellation_token: CancellationToken
    checkpoint: DiscoveryCheckpoint | None = None

    def __post_init__(self) -> None:
        """Validate consistency across source, request and session."""
        if self.source.id != self.request.source_id:
            raise ValueError("source identity does not match request source_id")
        if self.session.request != self.request:
            raise ValueError("session request does not match execution request")


@runtime_checkable
class ContextualDiscoveryProvider(Protocol):
    """Optional synchronous provider contract with complete execution context."""

    def discover_context(
        self,
        context: DiscoveryExecutionContext,
    ) -> DiscoveryResult:
        """Execute synchronous Discovery with cancellation and checkpoint access."""
        raise DiscoveryExecutionError("abstract contextual provider was invoked")


@runtime_checkable
class AsyncDiscoveryProvider(Protocol):
    """Asynchronous provider contract without an event-loop dependency."""

    async def discover_async(
        self,
        context: DiscoveryExecutionContext,
    ) -> DiscoveryResult:
        """Execute asynchronous Discovery using cooperative cancellation."""
        raise DiscoveryExecutionError("abstract asynchronous provider was invoked")


class DiscoveryExecutor:
    """Execute provider contracts and validate their canonical result."""

    def __init__(self, validator: DiscoveryValidator) -> None:
        """Initialize the executor with an injected canonical validator."""
        self._validator = validator
        self._logger = get_logger("core.discovery.executor")

    def execute(
        self,
        descriptor: DiscoveryProviderDescriptor,
        context: DiscoveryExecutionContext,
    ) -> DiscoveryResult:
        """Execute a synchronous contextual or SPR-008D-compatible provider."""
        context.cancellation_token.throw_if_cancelled()
        self._validator.validate_request(context.source, context.request)
        provider = descriptor.provider
        if isinstance(provider, ContextualDiscoveryProvider):
            result = provider.discover_context(context)
        elif isinstance(provider, DiscoveryProvider):
            result = provider.discover(context.source, context.request)
        else:
            raise DiscoveryExecutionError(
                f"provider {descriptor.provider_id} has no synchronous contract"
            )
        result = self._validate_result(descriptor, context, result)
        context.cancellation_token.throw_if_cancelled()
        return result

    async def execute_async(
        self,
        descriptor: DiscoveryProviderDescriptor,
        context: DiscoveryExecutionContext,
    ) -> DiscoveryResult:
        """Execute an asynchronous provider directly, without threads."""
        context.cancellation_token.throw_if_cancelled()
        self._validator.validate_request(context.source, context.request)
        provider = descriptor.provider
        if not isinstance(provider, AsyncDiscoveryProvider):
            raise DiscoveryExecutionError(
                f"provider {descriptor.provider_id} has no asynchronous contract"
            )
        pending = provider.discover_async(context)
        if not isawaitable(pending):
            raise DiscoveryExecutionError(
                f"provider {descriptor.provider_id} returned a non-awaitable value"
            )
        result = await pending
        result = self._validate_result(descriptor, context, result)
        context.cancellation_token.throw_if_cancelled()
        return result

    def _validate_result(
        self,
        descriptor: DiscoveryProviderDescriptor,
        context: DiscoveryExecutionContext,
        result: object,
    ) -> DiscoveryResult:
        """Validate a provider result and emit a structured completion log."""
        if not isinstance(result, DiscoveryResult):
            raise DiscoveryExecutionError(
                f"provider {descriptor.provider_id} must return DiscoveryResult"
            )
        self._validator.validate_result(context.request, result)
        self._logger.info(
            "discovery provider execution completed",
            extra={
                "context": {
                    "provider_id": descriptor.provider_id,
                    "session_id": str(context.session.id),
                    "request_id": str(context.request.id),
                    "status": result.status.value,
                }
            },
        )
        return result


__all__ = [
    "AsyncDiscoveryProvider",
    "ContextualDiscoveryProvider",
    "DiscoveryExecutionContext",
    "DiscoveryExecutor",
]
