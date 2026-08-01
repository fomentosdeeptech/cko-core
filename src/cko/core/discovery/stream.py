"""Incremental synchronous and asynchronous Discovery stream."""

from __future__ import annotations

import logging
from dataclasses import replace
from typing import AsyncIterable, AsyncIterator, Iterable, Iterator

from cko.core.contracts import Clock
from cko.core.identity import CanonicalId
from cko.core.logging import get_logger
from cko.core.utils import require_non_empty

from .models import DiscoveryBatch, DiscoveryRequest
from .session import DiscoverySession
from .streaming_errors import (
    DiscoveryStreamTransitionError,
    DuplicateBatchError,
    InvalidBatchAcknowledgementError,
    InvalidBatchSequenceError,
    InvalidDiscoveryStreamError,
)
from .streaming_models import (
    BatchAcknowledgement,
    BatchAcknowledgementStatus,
    BatchCursor,
    DiscoveryStreamState,
    StreamMetrics,
)


class DiscoveryStream:
    """Stateful one-pass stream that never retains produced batch contents."""

    def __init__(
        self,
        *,
        stream_id: CanonicalId,
        request: DiscoveryRequest,
        session: DiscoverySession,
        clock: Clock,
        batches: Iterable[DiscoveryBatch] | None = None,
        async_batches: AsyncIterable[DiscoveryBatch] | None = None,
        cursor: BatchCursor | None = None,
    ) -> None:
        """Initialize one synchronous or asynchronous canonical stream."""
        if not isinstance(stream_id, CanonicalId):
            raise InvalidDiscoveryStreamError("stream_id must be CanonicalId")
        if session.request != request:
            raise InvalidDiscoveryStreamError(
                "stream session does not match request"
            )
        if (batches is None) == (async_batches is None):
            raise InvalidDiscoveryStreamError(
                "stream requires exactly one batch source"
            )
        if cursor is not None:
            if cursor.request_id != request.id:
                raise InvalidDiscoveryStreamError(
                    "cursor request_id does not match stream request"
                )
            if cursor.session_id != session.id:
                raise InvalidDiscoveryStreamError(
                    "cursor session_id does not match stream session"
                )
        self.id = stream_id
        self.request_id = request.id
        self.session_id = session.id
        self.state = DiscoveryStreamState.CREATED
        self.metrics = StreamMetrics()
        self.failure: str | None = None
        self._clock = clock
        self._batches = batches
        self._async_batches = async_batches
        self._expected_sequence = cursor.next_sequence if cursor else 0
        self._seen_sequences: set[int] = set()
        self._seen_batch_ids: set[CanonicalId] = set()
        self._final_seen = False
        self._iteration_started = False
        self._logger: logging.Logger = get_logger("core.discovery.stream")

    @classmethod
    def synchronous(
        cls,
        request: DiscoveryRequest,
        session: DiscoverySession,
        batches: Iterable[DiscoveryBatch],
        clock: Clock,
        *,
        cursor: BatchCursor | None = None,
    ) -> "DiscoveryStream":
        """Create a canonical synchronous one-pass stream."""
        return cls(
            stream_id=CanonicalId.new(),
            request=request,
            session=session,
            clock=clock,
            batches=batches,
            cursor=cursor,
        )

    @classmethod
    def asynchronous(
        cls,
        request: DiscoveryRequest,
        session: DiscoverySession,
        batches: AsyncIterable[DiscoveryBatch],
        clock: Clock,
        *,
        cursor: BatchCursor | None = None,
    ) -> "DiscoveryStream":
        """Create a canonical asynchronous one-pass stream."""
        return cls(
            stream_id=CanonicalId.new(),
            request=request,
            session=session,
            clock=clock,
            async_batches=batches,
            cursor=cursor,
        )

    def open(self) -> None:
        """Transition a created stream into its open state."""
        self._transition(DiscoveryStreamState.CREATED, DiscoveryStreamState.OPEN)
        self.metrics = replace(self.metrics, started_at=self._clock.now())

    def complete(self) -> None:
        """Complete an open stream after its declared final batch."""
        if not self._final_seen:
            raise InvalidBatchSequenceError(
                "stream ended without a final DiscoveryBatch"
            )
        self._terminate(DiscoveryStreamState.COMPLETED, None)

    def fail(self, reason: str) -> None:
        """Move a created or open stream to controlled failure."""
        self._terminate(
            DiscoveryStreamState.FAILED,
            require_non_empty(reason, "reason"),
        )

    def cancel(self, reason: str) -> None:
        """Move a created or open stream to cooperative cancellation."""
        self._terminate(
            DiscoveryStreamState.CANCELLED,
            require_non_empty(reason, "reason"),
        )

    def __iter__(self) -> Iterator[DiscoveryBatch]:
        """Iterate a synchronous source while validating every batch."""
        if self._batches is None:
            raise InvalidDiscoveryStreamError(
                "asynchronous stream cannot be iterated synchronously"
            )
        self._begin_iteration()
        try:
            for batch in self._batches:
                yield self._accept_batch(batch)
            self.complete()
        except Exception as error:
            if self.state in {
                DiscoveryStreamState.CREATED,
                DiscoveryStreamState.OPEN,
            }:
                self.fail(str(error) or type(error).__name__)
            raise

    async def __aiter__(self) -> AsyncIterator[DiscoveryBatch]:
        """Iterate an asynchronous source while validating every batch."""
        if self._async_batches is None:
            raise InvalidDiscoveryStreamError(
                "synchronous stream cannot be iterated asynchronously"
            )
        self._begin_iteration()
        try:
            async for batch in self._async_batches:
                yield self._accept_batch(batch)
            self.complete()
        except Exception as error:
            if self.state in {
                DiscoveryStreamState.CREATED,
                DiscoveryStreamState.OPEN,
            }:
                self.fail(str(error) or type(error).__name__)
            raise

    def record_acknowledgement(
        self,
        batch: DiscoveryBatch,
        acknowledgement: BatchAcknowledgement,
    ) -> None:
        """Validate and account for one consumer acknowledgement."""
        if self.state is not DiscoveryStreamState.OPEN:
            raise DiscoveryStreamTransitionError(
                "acknowledgements require an open stream"
            )
        if acknowledgement.batch_id != batch.id:
            raise InvalidBatchAcknowledgementError(
                "acknowledgement batch_id does not match batch"
            )
        if acknowledgement.session_id != self.session_id:
            raise InvalidBatchAcknowledgementError(
                "acknowledgement session_id does not match stream"
            )
        total = acknowledgement.processed_items + acknowledgement.rejected_items
        if total != len(batch.items):
            raise InvalidBatchAcknowledgementError(
                "acknowledgement item counts do not match batch"
            )
        rejected_batch = acknowledgement.status in {
            BatchAcknowledgementStatus.REJECTED,
            BatchAcknowledgementStatus.PARTIAL,
            BatchAcknowledgementStatus.FAILED,
        }
        self.metrics = replace(
            self.metrics,
            batches_consumed=self.metrics.batches_consumed + 1,
            batches_rejected=(
                self.metrics.batches_rejected + int(rejected_batch)
            ),
            items_consumed=(
                self.metrics.items_consumed + acknowledgement.processed_items
            ),
            items_rejected=(
                self.metrics.items_rejected + acknowledgement.rejected_items
            ),
        )

    def _begin_iteration(self) -> None:
        """Open the stream exactly once."""
        if self._iteration_started:
            raise InvalidDiscoveryStreamError("stream can only be iterated once")
        self._iteration_started = True
        self.open()

    def _accept_batch(self, batch: object) -> DiscoveryBatch:
        """Validate identity and monotonic sequence without retaining content."""
        if not isinstance(batch, DiscoveryBatch):
            raise InvalidDiscoveryStreamError(
                "stream source must yield DiscoveryBatch values"
            )
        if self._final_seen:
            raise InvalidBatchSequenceError(
                "a batch cannot follow the declared final batch"
            )
        if batch.sequence in self._seen_sequences:
            raise DuplicateBatchError(
                f"duplicate batch sequence: {batch.sequence}"
            )
        if batch.id in self._seen_batch_ids:
            raise DuplicateBatchError(f"duplicate batch identity: {batch.id}")
        if batch.sequence != self._expected_sequence:
            raise InvalidBatchSequenceError(
                f"expected batch sequence {self._expected_sequence}, "
                f"received {batch.sequence}"
            )
        self._seen_sequences.add(batch.sequence)
        self._seen_batch_ids.add(batch.id)
        self._expected_sequence += 1
        self._final_seen = batch.final
        self.metrics = replace(
            self.metrics,
            batches_produced=self.metrics.batches_produced + 1,
            items_produced=self.metrics.items_produced + len(batch.items),
        )
        self._logger.info(
            "discovery batch yielded",
            extra={
                "context": {
                    "stream_id": str(self.id),
                    "session_id": str(self.session_id),
                    "batch_id": str(batch.id),
                    "sequence": batch.sequence,
                    "items": len(batch.items),
                    "final": batch.final,
                }
            },
        )
        return batch

    def _transition(
        self,
        expected: DiscoveryStreamState,
        target: DiscoveryStreamState,
    ) -> None:
        """Apply an exact non-terminal state transition."""
        if self.state is not expected:
            raise DiscoveryStreamTransitionError(
                f"cannot transition stream from {self.state.value} "
                f"to {target.value}"
            )
        self.state = target
        self._log_transition()

    def _terminate(
        self,
        target: DiscoveryStreamState,
        failure: str | None,
    ) -> None:
        """Apply a valid terminal transition and freeze terminal metrics."""
        if self.state not in {
            DiscoveryStreamState.CREATED,
            DiscoveryStreamState.OPEN,
        }:
            raise DiscoveryStreamTransitionError(
                f"cannot transition terminal stream from {self.state.value}"
            )
        completed_at = self._clock.now()
        started_at = self.metrics.started_at or completed_at
        self.state = target
        self.failure = failure
        self.metrics = replace(
            self.metrics,
            started_at=started_at,
            completed_at=completed_at,
            terminal_state=target,
        )
        self._log_transition()

    def _log_transition(self) -> None:
        """Emit a structured stream transition record."""
        self._logger.info(
            "discovery stream transitioned",
            extra={
                "context": {
                    "stream_id": str(self.id),
                    "request_id": str(self.request_id),
                    "session_id": str(self.session_id),
                    "state": self.state.value,
                    "failure": self.failure,
                }
            },
        )


__all__ = ["DiscoveryStream"]
