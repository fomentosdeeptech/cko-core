"""Decoupled orchestration pipeline for Discovery provider execution."""

from __future__ import annotations

from dataclasses import dataclass

from cko.core.contracts import Clock

from .cancellation import CancellationToken
from .checkpoints import DiscoveryCheckpoint
from .contracts import DiscoverySource
from .execution import DiscoveryExecutionContext, DiscoveryExecutor
from .foundation_errors import DiscoveryCancelledError
from .models import DiscoveryRequest, DiscoveryResult
from .providers import (
    DiscoveryExecutionMode,
    DiscoveryProviderDescriptor,
    DiscoveryProviderFactory,
)
from .session import DiscoverySession, DiscoverySessionState


@dataclass(frozen=True, slots=True)
class DiscoveryExecution:
    """Successful terminal output of a Discovery pipeline execution."""

    session: DiscoverySession
    result: DiscoveryResult
    provider_id: str
    execution_mode: DiscoveryExecutionMode
    checkpoint: DiscoveryCheckpoint | None = None

    def __post_init__(self) -> None:
        """Validate that the execution output is terminal and consistent."""
        if self.session.state not in {
            DiscoverySessionState.COMPLETED,
            DiscoverySessionState.FAILED,
            DiscoverySessionState.CANCELLED,
        }:
            raise ValueError("execution requires a terminal session")
        if self.result.request_id != self.session.request.id:
            raise ValueError("result request_id does not match execution session")


class DiscoveryPipeline:
    """Resolve, execute and close Discovery sessions without infrastructure."""

    def __init__(
        self,
        factory: DiscoveryProviderFactory,
        executor: DiscoveryExecutor,
        clock: Clock,
    ) -> None:
        """Initialize the pipeline with injected foundation dependencies."""
        self._factory = factory
        self._executor = executor
        self._clock = clock

    def execute(
        self,
        source: DiscoverySource,
        request: DiscoveryRequest,
        *,
        cancellation_token: CancellationToken | None = None,
        checkpoint: DiscoveryCheckpoint | None = None,
        provider_id: str | None = None,
    ) -> DiscoveryExecution:
        """Execute the synchronous provider pipeline to a terminal session."""
        token = cancellation_token or CancellationToken.create()
        session = DiscoverySession.create(request)
        try:
            token.throw_if_cancelled()
            descriptor = self._factory.create(
                source,
                request,
                DiscoveryExecutionMode.SYNCHRONOUS,
                provider_id=provider_id,
            )
            context = self._start_context(
                descriptor,
                source,
                request,
                session,
                token,
                checkpoint,
            )
            result = self._executor.execute(descriptor, context)
            session.complete(result, self._clock.now())
            return DiscoveryExecution(
                session,
                result,
                descriptor.provider_id,
                DiscoveryExecutionMode.SYNCHRONOUS,
                checkpoint,
            )
        except DiscoveryCancelledError as error:
            self._cancel_session(session, token, error)
            raise
        except Exception as error:
            self._fail_session(session, error)
            raise

    async def execute_async(
        self,
        source: DiscoverySource,
        request: DiscoveryRequest,
        *,
        cancellation_token: CancellationToken | None = None,
        checkpoint: DiscoveryCheckpoint | None = None,
        provider_id: str | None = None,
    ) -> DiscoveryExecution:
        """Execute the asynchronous provider pipeline without creating threads."""
        token = cancellation_token or CancellationToken.create()
        session = DiscoverySession.create(request)
        try:
            token.throw_if_cancelled()
            descriptor = self._factory.create(
                source,
                request,
                DiscoveryExecutionMode.ASYNCHRONOUS,
                provider_id=provider_id,
            )
            context = self._start_context(
                descriptor,
                source,
                request,
                session,
                token,
                checkpoint,
            )
            result = await self._executor.execute_async(descriptor, context)
            session.complete(result, self._clock.now())
            return DiscoveryExecution(
                session,
                result,
                descriptor.provider_id,
                DiscoveryExecutionMode.ASYNCHRONOUS,
                checkpoint,
            )
        except DiscoveryCancelledError as error:
            self._cancel_session(session, token, error)
            raise
        except Exception as error:
            self._fail_session(session, error)
            raise

    def _start_context(
        self,
        descriptor: DiscoveryProviderDescriptor,
        source: DiscoverySource,
        request: DiscoveryRequest,
        session: DiscoverySession,
        token: CancellationToken,
        checkpoint: DiscoveryCheckpoint | None,
    ) -> DiscoveryExecutionContext:
        """Start a session and construct its complete provider context."""
        session.start(descriptor.provider_id, self._clock.now())
        return DiscoveryExecutionContext(
            source=source,
            request=request,
            session=session,
            cancellation_token=token,
            checkpoint=checkpoint,
        )

    def _cancel_session(
        self,
        session: DiscoverySession,
        token: CancellationToken,
        error: DiscoveryCancelledError,
    ) -> None:
        """Close an active session with its cooperative cancellation reason."""
        if session.state in {
            DiscoverySessionState.CREATED,
            DiscoverySessionState.RUNNING,
        }:
            session.cancel(token.reason or str(error), self._clock.now())

    def _fail_session(
        self,
        session: DiscoverySession,
        error: Exception,
    ) -> None:
        """Close an active session with a controlled failure description."""
        if session.state in {
            DiscoverySessionState.CREATED,
            DiscoverySessionState.RUNNING,
        }:
            session.fail(str(error) or type(error).__name__, self._clock.now())


__all__ = ["DiscoveryExecution", "DiscoveryPipeline"]
