"""Neutral orchestration for incremental Discovery batch processing."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from cko.core.contracts import Clock
from cko.core.identity import CanonicalId
from cko.core.logging import get_logger
from cko.core.utils import require_non_empty

from .cancellation import CancellationToken
from .checkpoints import DiscoveryCheckpoint
from .foundation_errors import DiscoveryCancelledError
from .models import DiscoveryBatch, DiscoveryRequest
from .session import DiscoverySession, DiscoverySessionState
from .stream import DiscoveryStream
from .streaming_contracts import (
    AsyncBatchConsumer,
    AsyncBatchProducer,
    BatchConsumer,
    BatchConsumptionContext,
    BatchProducer,
    BatchProductionContext,
)
from .streaming_errors import (
    BackpressureViolationError,
    BatchConsumerError,
    BatchProducerError,
    DiscoveryStreamTransitionError,
    InvalidBatchSequenceError,
    InvalidDiscoveryStreamError,
)
from .streaming_models import (
    BackpressurePolicy,
    BatchAcknowledgement,
    BatchAcknowledgementStatus,
    BatchCursor,
    ConsumerUnavailableBehavior,
    DiscoveryStreamState,
    StreamMetrics,
)


@dataclass(frozen=True, slots=True)
class StreamingExecution:
    """Terminal output of a streaming pipeline without aggregated items."""

    session: DiscoverySession
    stream_id: CanonicalId
    metrics: StreamMetrics
    cursor: BatchCursor
    checkpoint: DiscoveryCheckpoint | None = None

    def __post_init__(self) -> None:
        """Validate terminal consistency of the streaming execution."""
        if not isinstance(self.stream_id, CanonicalId):
            raise TypeError("stream_id must be CanonicalId")
        if self.session.state is not DiscoverySessionState.COMPLETED:
            raise ValueError("streaming execution requires a completed session")
        if self.metrics.terminal_state is not DiscoveryStreamState.COMPLETED:
            raise ValueError("streaming execution requires completed stream metrics")
        if self.cursor.session_id != self.session.id:
            raise ValueError("cursor session_id does not match execution")


class StreamingDiscoveryPipeline:
    """Connect producer, stream and consumer one canonical batch at a time."""

    def __init__(self, clock: Clock) -> None:
        """Initialize the pipeline with an injected canonical clock."""
        self._clock = clock
        self._logger: logging.Logger = get_logger(
            "core.discovery.streaming_pipeline"
        )

    def execute(
        self,
        request: DiscoveryRequest,
        producer: BatchProducer,
        consumer: BatchConsumer,
        *,
        provider_id: str,
        session: DiscoverySession | None = None,
        cancellation_token: CancellationToken | None = None,
        checkpoint: DiscoveryCheckpoint | None = None,
        cursor: BatchCursor | None = None,
        backpressure: BackpressurePolicy | None = None,
    ) -> StreamingExecution:
        """Execute synchronous incremental production and consumption."""
        if not isinstance(producer, BatchProducer):
            raise TypeError("producer must implement BatchProducer")
        if not isinstance(consumer, BatchConsumer):
            raise TypeError("consumer must implement BatchConsumer")
        identity = require_non_empty(provider_id, "provider_id")
        token = cancellation_token or CancellationToken.create()
        policy = backpressure or BackpressurePolicy()
        active_session = self._prepare_session(request, session, identity)
        production = BatchProductionContext(
            request,
            active_session,
            token,
            policy,
            cursor,
            checkpoint,
        )
        consumption = BatchConsumptionContext(request, active_session, token)
        stream: DiscoveryStream | None = None
        closed = False
        try:
            token.throw_if_cancelled()
            try:
                batches = producer.produce(production)
            except Exception as error:
                raise BatchProducerError("batch producer failed to start") from error
            stream = DiscoveryStream.synchronous(
                request,
                active_session,
                batches,
                self._clock,
                cursor=cursor,
            )
            final_cursor = self._consume_sync(
                stream,
                producer,
                consumer,
                production,
                consumption,
            )
            self._close_sync(producer, consumer)
            closed = True
            active_session.complete_stream(stream.metrics, self._clock.now())
            return StreamingExecution(
                active_session,
                stream.id,
                stream.metrics,
                final_cursor,
                checkpoint,
            )
        except DiscoveryCancelledError as error:
            self._cancel_sync(producer, token.reason or str(error))
            self._terminate_cancelled(stream, active_session, token, error)
            raise
        except Exception as error:
            self._notify_failure_sync(consumer, error)
            self._terminate_failed(stream, active_session, error)
            raise
        finally:
            if not closed:
                self._close_sync_safely(producer, consumer)

    async def execute_async(
        self,
        request: DiscoveryRequest,
        producer: AsyncBatchProducer,
        consumer: AsyncBatchConsumer,
        *,
        provider_id: str,
        session: DiscoverySession | None = None,
        cancellation_token: CancellationToken | None = None,
        checkpoint: DiscoveryCheckpoint | None = None,
        cursor: BatchCursor | None = None,
        backpressure: BackpressurePolicy | None = None,
    ) -> StreamingExecution:
        """Execute asynchronous incremental production and consumption."""
        if not isinstance(producer, AsyncBatchProducer):
            raise TypeError("producer must implement AsyncBatchProducer")
        if not isinstance(consumer, AsyncBatchConsumer):
            raise TypeError("consumer must implement AsyncBatchConsumer")
        identity = require_non_empty(provider_id, "provider_id")
        token = cancellation_token or CancellationToken.create()
        policy = backpressure or BackpressurePolicy()
        active_session = self._prepare_session(request, session, identity)
        production = BatchProductionContext(
            request,
            active_session,
            token,
            policy,
            cursor,
            checkpoint,
        )
        consumption = BatchConsumptionContext(request, active_session, token)
        stream: DiscoveryStream | None = None
        closed = False
        try:
            token.throw_if_cancelled()
            try:
                batches = producer.produce_async(production)
            except Exception as error:
                raise BatchProducerError(
                    "asynchronous batch producer failed to start"
                ) from error
            stream = DiscoveryStream.asynchronous(
                request,
                active_session,
                batches,
                self._clock,
                cursor=cursor,
            )
            final_cursor = await self._consume_async(
                stream,
                producer,
                consumer,
                production,
                consumption,
            )
            await self._close_async(producer, consumer)
            closed = True
            active_session.complete_stream(stream.metrics, self._clock.now())
            return StreamingExecution(
                active_session,
                stream.id,
                stream.metrics,
                final_cursor,
                checkpoint,
            )
        except DiscoveryCancelledError as error:
            await self._cancel_async(producer, token.reason or str(error))
            self._terminate_cancelled(stream, active_session, token, error)
            raise
        except Exception as error:
            await self._notify_failure_async(consumer, error)
            self._terminate_failed(stream, active_session, error)
            raise
        finally:
            if not closed:
                await self._close_async_safely(producer, consumer)

    def _consume_sync(
        self,
        stream: DiscoveryStream,
        producer: BatchProducer,
        consumer: BatchConsumer,
        production: BatchProductionContext,
        consumption: BatchConsumptionContext,
    ) -> BatchCursor:
        """Drive a synchronous stream while isolating producer failures."""
        iterator = iter(stream)
        cursor = production.cursor
        while True:
            production.cancellation_token.throw_if_cancelled()
            try:
                batch = next(iterator)
            except StopIteration:
                break
            except (InvalidBatchSequenceError, InvalidDiscoveryStreamError):
                raise
            except Exception as error:
                raise BatchProducerError("batch producer iteration failed") from error
            self._enforce_backpressure(batch, stream, production.backpressure)
            try:
                acknowledgement = consumer.consume(batch, consumption)
            except Exception as error:
                raise BatchConsumerError("batch consumer failed") from error
            self._accept_acknowledgement(
                stream,
                batch,
                acknowledgement,
                production,
            )
            cursor = self._advance_cursor(production, batch)
        if cursor is None:
            raise InvalidBatchSequenceError("stream produced no final batch")
        return cursor

    async def _consume_async(
        self,
        stream: DiscoveryStream,
        producer: AsyncBatchProducer,
        consumer: AsyncBatchConsumer,
        production: BatchProductionContext,
        consumption: BatchConsumptionContext,
    ) -> BatchCursor:
        """Drive an asynchronous stream while isolating producer failures."""
        iterator = stream.__aiter__()
        cursor = production.cursor
        while True:
            production.cancellation_token.throw_if_cancelled()
            try:
                batch = await iterator.__anext__()
            except StopAsyncIteration:
                break
            except (InvalidBatchSequenceError, InvalidDiscoveryStreamError):
                raise
            except Exception as error:
                raise BatchProducerError(
                    "asynchronous batch producer iteration failed"
                ) from error
            self._enforce_backpressure(batch, stream, production.backpressure)
            try:
                acknowledgement = await consumer.consume_async(batch, consumption)
            except Exception as error:
                raise BatchConsumerError(
                    "asynchronous batch consumer failed"
                ) from error
            self._accept_acknowledgement(
                stream,
                batch,
                acknowledgement,
                production,
            )
            cursor = self._advance_cursor(production, batch)
        if cursor is None:
            raise InvalidBatchSequenceError("stream produced no final batch")
        return cursor

    def _accept_acknowledgement(
        self,
        stream: DiscoveryStream,
        batch: DiscoveryBatch,
        acknowledgement: object,
        production: BatchProductionContext,
    ) -> None:
        """Validate, account and apply unavailable-consumer policy."""
        if not isinstance(acknowledgement, BatchAcknowledgement):
            raise BatchConsumerError(
                "consumer must return BatchAcknowledgement"
            )
        stream.record_acknowledgement(batch, acknowledgement)
        if acknowledgement.status is not BatchAcknowledgementStatus.FAILED:
            return
        behavior = production.backpressure.consumer_unavailable
        reason = acknowledgement.reason or "consumer unavailable"
        if behavior is ConsumerUnavailableBehavior.FAIL:
            raise BatchConsumerError(reason)
        if behavior is ConsumerUnavailableBehavior.CANCEL:
            production.cancellation_token.cancel(reason)
            production.cancellation_token.throw_if_cancelled()

    def _enforce_backpressure(
        self,
        batch: DiscoveryBatch,
        stream: DiscoveryStream,
        policy: BackpressurePolicy,
    ) -> None:
        """Enforce declared batch-size and logical timeout limits."""
        if (
            policy.max_items_per_batch is not None
            and len(batch.items) > policy.max_items_per_batch
        ):
            raise BackpressureViolationError(
                f"batch contains {len(batch.items)} items; limit is "
                f"{policy.max_items_per_batch}"
            )
        if policy.max_pending_batches < 1:
            raise BackpressureViolationError(
                "sequential pipeline requires one pending batch capacity"
            )
        if policy.timeout_seconds is not None:
            started = stream.metrics.started_at
            if started is not None:
                elapsed = (self._clock.now() - started).total_seconds()
                if elapsed > policy.timeout_seconds:
                    raise BackpressureViolationError(
                        "stream exceeded its logical timeout"
                    )

    def _advance_cursor(
        self,
        production: BatchProductionContext,
        batch: DiscoveryBatch,
    ) -> BatchCursor:
        """Advance only the canonical sequence while preserving opaque state."""
        state = production.cursor.state if production.cursor is not None else {}
        return BatchCursor(
            production.request.id,
            production.session.id,
            batch.sequence + 1,
            state,
        )

    def _prepare_session(
        self,
        request: DiscoveryRequest,
        session: DiscoverySession | None,
        provider_id: str,
    ) -> DiscoverySession:
        """Reuse or create the SPR-008E session and ensure it is running."""
        active = session or DiscoverySession.create(request)
        if active.request != request:
            raise InvalidDiscoveryStreamError(
                "pipeline session does not match request"
            )
        if active.state is DiscoverySessionState.CREATED:
            active.start(provider_id, self._clock.now())
        elif active.state is DiscoverySessionState.RUNNING:
            if active.provider_id != provider_id:
                raise InvalidDiscoveryStreamError(
                    "running session provider_id does not match pipeline"
                )
        else:
            raise InvalidDiscoveryStreamError(
                "pipeline requires a created or running session"
            )
        return active

    def _terminate_cancelled(
        self,
        stream: DiscoveryStream | None,
        session: DiscoverySession,
        token: CancellationToken,
        error: DiscoveryCancelledError,
    ) -> None:
        """Close stream and session with the cooperative cancellation cause."""
        reason = token.reason or str(error)
        if stream is not None and stream.state in {
            DiscoveryStreamState.CREATED,
            DiscoveryStreamState.OPEN,
        }:
            stream.cancel(reason)
        if session.state in {
            DiscoverySessionState.CREATED,
            DiscoverySessionState.RUNNING,
        }:
            session.cancel(reason, self._clock.now())

    def _terminate_failed(
        self,
        stream: DiscoveryStream | None,
        session: DiscoverySession,
        error: Exception,
    ) -> None:
        """Close stream and session while preserving the raised exception."""
        reason = str(error) or type(error).__name__
        if stream is not None and stream.state in {
            DiscoveryStreamState.CREATED,
            DiscoveryStreamState.OPEN,
        }:
            stream.fail(reason)
        if session.state in {
            DiscoverySessionState.CREATED,
            DiscoverySessionState.RUNNING,
        }:
            session.fail(reason, self._clock.now())

    def _close_sync(
        self,
        producer: BatchProducer,
        consumer: BatchConsumer,
    ) -> None:
        """Close synchronous endpoints and expose controlled close failures."""
        try:
            consumer.close()
        except Exception as error:
            raise BatchConsumerError("batch consumer close failed") from error
        try:
            producer.close()
        except Exception as error:
            raise BatchProducerError("batch producer close failed") from error

    async def _close_async(
        self,
        producer: AsyncBatchProducer,
        consumer: AsyncBatchConsumer,
    ) -> None:
        """Close asynchronous endpoints and expose controlled close failures."""
        try:
            await consumer.close_async()
        except Exception as error:
            raise BatchConsumerError(
                "asynchronous batch consumer close failed"
            ) from error
        try:
            await producer.close_async()
        except Exception as error:
            raise BatchProducerError(
                "asynchronous batch producer close failed"
            ) from error

    def _cancel_sync(self, producer: BatchProducer, reason: str) -> None:
        """Notify a synchronous producer without replacing cancellation."""
        try:
            producer.cancel(reason)
        except Exception as error:
            self._log_secondary("producer cancellation notification failed", error)

    async def _cancel_async(
        self,
        producer: AsyncBatchProducer,
        reason: str,
    ) -> None:
        """Notify an asynchronous producer without replacing cancellation."""
        try:
            await producer.cancel_async(reason)
        except Exception as error:
            self._log_secondary("async producer cancellation failed", error)

    def _notify_failure_sync(
        self,
        consumer: BatchConsumer,
        error: Exception,
    ) -> None:
        """Notify a synchronous consumer without replacing the primary error."""
        try:
            consumer.fail(error)
        except Exception as secondary:
            self._log_secondary("consumer failure notification failed", secondary)

    async def _notify_failure_async(
        self,
        consumer: AsyncBatchConsumer,
        error: Exception,
    ) -> None:
        """Notify an async consumer without replacing the primary error."""
        try:
            await consumer.fail_async(error)
        except Exception as secondary:
            self._log_secondary("async consumer failure notification failed", secondary)

    def _close_sync_safely(
        self,
        producer: BatchProducer,
        consumer: BatchConsumer,
    ) -> None:
        """Best-effort deterministic close after a primary failure."""
        for endpoint, operation in (
            ("consumer", consumer.close),
            ("producer", producer.close),
        ):
            try:
                operation()
            except Exception as error:
                self._log_secondary(f"{endpoint} close failed", error)

    async def _close_async_safely(
        self,
        producer: AsyncBatchProducer,
        consumer: AsyncBatchConsumer,
    ) -> None:
        """Best-effort async close after a primary failure."""
        try:
            await consumer.close_async()
        except Exception as error:
            self._log_secondary("async consumer close failed", error)
        try:
            await producer.close_async()
        except Exception as error:
            self._log_secondary("async producer close failed", error)

    def _log_secondary(self, message: str, error: Exception) -> None:
        """Record a secondary lifecycle error with structured context."""
        self._logger.warning(
            message,
            extra={
                "context": {
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            },
        )


__all__ = ["StreamingDiscoveryPipeline", "StreamingExecution"]
