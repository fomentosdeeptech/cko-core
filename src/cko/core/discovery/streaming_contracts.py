"""Public producer and consumer ports for Discovery batch streaming."""

from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator, Iterable, Protocol, runtime_checkable

from .cancellation import CancellationToken
from .checkpoints import DiscoveryCheckpoint
from .models import DiscoveryBatch, DiscoveryRequest
from .session import DiscoverySession
from .streaming_errors import BatchConsumerError, BatchProducerError
from .streaming_models import (
    BackpressurePolicy,
    BatchAcknowledgement,
    BatchCursor,
)


@dataclass(frozen=True, slots=True)
class BatchProductionContext:
    """Complete neutral context supplied to an incremental batch producer."""

    request: DiscoveryRequest
    session: DiscoverySession
    cancellation_token: CancellationToken
    backpressure: BackpressurePolicy
    cursor: BatchCursor | None = None
    checkpoint: DiscoveryCheckpoint | None = None

    def __post_init__(self) -> None:
        """Validate shared request, session, cursor and checkpoint identities."""
        if self.session.request != self.request:
            raise ValueError("production session does not match request")
        if self.cursor is not None:
            if self.cursor.request_id != self.request.id:
                raise ValueError("cursor request_id does not match request")
            if self.cursor.session_id != self.session.id:
                raise ValueError("cursor session_id does not match session")
        if self.checkpoint is not None:
            if self.checkpoint.session_id != self.session.id:
                raise ValueError("checkpoint session_id does not match session")
            if self.cursor is not None:
                if self.checkpoint.sequence > self.cursor.next_sequence:
                    raise ValueError("checkpoint sequence exceeds cursor sequence")


@dataclass(frozen=True, slots=True)
class BatchConsumptionContext:
    """Neutral context supplied to a consumer for one stream session."""

    request: DiscoveryRequest
    session: DiscoverySession
    cancellation_token: CancellationToken

    def __post_init__(self) -> None:
        """Validate that the consumer observes the same canonical request."""
        if self.session.request != self.request:
            raise ValueError("consumption session does not match request")


@runtime_checkable
class BatchProducer(Protocol):
    """Synchronous producer port implemented outside the CORE foundation."""

    def produce(
        self,
        context: BatchProductionContext,
    ) -> Iterable[DiscoveryBatch]:
        """Yield canonical batches incrementally from a logical cursor."""
        raise BatchProducerError("abstract batch producer was invoked")

    def close(self) -> None:
        """Release producer-owned logical resources deterministically."""
        raise BatchProducerError("abstract batch producer cannot be closed")

    def cancel(self, reason: str) -> None:
        """Observe cooperative cancellation without platform primitives."""
        raise BatchProducerError(
            f"abstract batch producer cannot be cancelled: {reason}"
        )


@runtime_checkable
class AsyncBatchProducer(Protocol):
    """Asynchronous producer port implemented outside the CORE foundation."""

    def produce_async(
        self,
        context: BatchProductionContext,
    ) -> AsyncIterator[DiscoveryBatch]:
        """Yield canonical batches asynchronously from a logical cursor."""
        raise BatchProducerError("abstract async batch producer was invoked")

    async def close_async(self) -> None:
        """Release producer-owned logical resources asynchronously."""
        raise BatchProducerError("abstract async batch producer cannot be closed")

    async def cancel_async(self, reason: str) -> None:
        """Observe cooperative asynchronous cancellation."""
        raise BatchProducerError(
            f"abstract async batch producer cannot be cancelled: {reason}"
        )


@runtime_checkable
class BatchConsumer(Protocol):
    """Synchronous consumer port returning a logical acknowledgement."""

    def consume(
        self,
        batch: DiscoveryBatch,
        context: BatchConsumptionContext,
    ) -> BatchAcknowledgement:
        """Process one batch without automatic persistence."""
        raise BatchConsumerError("abstract batch consumer was invoked")

    def close(self) -> None:
        """Close the consumer deterministically after stream termination."""
        raise BatchConsumerError("abstract batch consumer cannot be closed")

    def fail(self, error: Exception) -> None:
        """Receive a controlled upstream or orchestration failure."""
        raise BatchConsumerError(
            f"abstract batch consumer cannot receive failure: {error}"
        )


@runtime_checkable
class AsyncBatchConsumer(Protocol):
    """Asynchronous consumer port returning a logical acknowledgement."""

    async def consume_async(
        self,
        batch: DiscoveryBatch,
        context: BatchConsumptionContext,
    ) -> BatchAcknowledgement:
        """Process one batch asynchronously without automatic persistence."""
        raise BatchConsumerError("abstract async batch consumer was invoked")

    async def close_async(self) -> None:
        """Close the asynchronous consumer after stream termination."""
        raise BatchConsumerError("abstract async batch consumer cannot be closed")

    async def fail_async(self, error: Exception) -> None:
        """Receive a controlled asynchronous pipeline failure."""
        raise BatchConsumerError(
            f"abstract async batch consumer cannot receive failure: {error}"
        )


__all__ = [
    "AsyncBatchConsumer",
    "AsyncBatchProducer",
    "BatchConsumer",
    "BatchConsumptionContext",
    "BatchProducer",
    "BatchProductionContext",
]
