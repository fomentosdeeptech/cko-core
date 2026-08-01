"""Streaming and batch foundation contracts for SPR-008F."""

from __future__ import annotations

import ast
import asyncio
import inspect
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import AsyncIterator, Iterable, Mapping

import pytest

from cko.core import CanonicalId, UniversalMetadata
from cko.core.discovery import (
    BATCH_CURSOR_SCHEMA_VERSION,
    AsyncBatchConsumer,
    AsyncBatchProducer,
    BackpressurePolicy,
    BackpressureViolationError,
    BatchAcknowledgement,
    BatchAcknowledgementStatus,
    BatchConsumer,
    BatchConsumerError,
    BatchConsumptionContext,
    BatchCursor,
    BatchProducer,
    BatchProducerError,
    BatchProductionContext,
    CancellationToken,
    ConsumerUnavailableBehavior,
    DiscoveredItem,
    DiscoveryBatch,
    DiscoveryCancelledError,
    DiscoveryCheckpoint,
    DiscoveryContext,
    DiscoveryError,
    DiscoveryPolicy,
    DiscoveryRequest,
    DiscoveryScope,
    DiscoverySession,
    DiscoverySessionState,
    DiscoverySourceId,
    DiscoveryStream,
    DiscoveryStreamState,
    DiscoveryStreamTransitionError,
    DuplicateBatchError,
    InvalidBatchAcknowledgementError,
    InvalidBatchCursorError,
    InvalidBatchSequenceError,
    InvalidDiscoveryStreamError,
    StreamMetrics,
    StreamingDiscoveryPipeline,
    StreamingExecution,
)


NOW = datetime(2026, 7, 14, 23, 0, tzinfo=UTC)
SOURCE_ID = DiscoverySourceId("logical:spr008f")


class AdvancingClock:
    """Deterministic clock used by stream and session lifecycle tests."""

    def __init__(self, step: float = 1.0) -> None:
        self._value = NOW
        self._step = timedelta(seconds=step)

    def now(self) -> datetime:
        """Return the current value and advance deterministically."""
        value = self._value
        self._value += self._step
        return value


def _request() -> DiscoveryRequest:
    return DiscoveryRequest(
        id=CanonicalId.new(),
        source_id=SOURCE_ID,
        scope=DiscoveryScope("logical:streaming"),
        policy=DiscoveryPolicy(page_size=10),
        context=DiscoveryContext("corr-008f", NOW, actor="test"),
    )


def _item(reference: str) -> DiscoveredItem:
    return DiscoveredItem(
        source_id=SOURCE_ID,
        external_reference=reference,
        observed_at=NOW,
        observation_method="incremental-listing",
        correlation_id="corr-008f",
        metadata=UniversalMetadata(
            media_type="application/octet-stream",
            created_at=NOW,
            modified_at=NOW,
            language="pt-BR",
        ),
    )


def _batch(
    sequence: int,
    *,
    final: bool,
    items: tuple[DiscoveredItem, ...] = (),
    batch_id: CanonicalId | None = None,
) -> DiscoveryBatch:
    return DiscoveryBatch(
        id=batch_id or CanonicalId.new(),
        sequence=sequence,
        items=items,
        final=final,
    )


def _ack(
    batch: DiscoveryBatch,
    session: DiscoverySession,
    *,
    status: BatchAcknowledgementStatus = (
        BatchAcknowledgementStatus.CONFIRMED
    ),
    processed: int | None = None,
    rejected: int = 0,
    reason: str | None = None,
) -> BatchAcknowledgement:
    return BatchAcknowledgement(
        batch.id,
        session.id,
        status,
        len(batch.items) if processed is None else processed,
        rejected,
        NOW,
        reason,
        {"logical_latency": 1.0},
    )


class SyncProducer:
    """In-memory test double implementing only the public producer port."""

    def __init__(
        self,
        batches: Iterable[DiscoveryBatch],
        *,
        failure: Exception | None = None,
    ) -> None:
        self._batches = tuple(batches)
        self._failure = failure
        self.context: BatchProductionContext | None = None
        self.closed = False
        self.cancelled_reason: str | None = None

    def produce(
        self,
        context: BatchProductionContext,
    ) -> Iterable[DiscoveryBatch]:
        self.context = context

        def generate() -> Iterable[DiscoveryBatch]:
            for batch in self._batches:
                yield batch
            if self._failure is not None:
                raise self._failure

        return generate()

    def close(self) -> None:
        self.closed = True

    def cancel(self, reason: str) -> None:
        self.cancelled_reason = reason


class SyncConsumer:
    """Configurable consumer that returns canonical acknowledgements."""

    def __init__(
        self,
        status: BatchAcknowledgementStatus = (
            BatchAcknowledgementStatus.CONFIRMED
        ),
        *,
        failure: Exception | None = None,
        token: CancellationToken | None = None,
    ) -> None:
        self.status = status
        self.failure = failure
        self.token = token
        self.received: list[int] = []
        self.closed = False
        self.reported_failure: Exception | None = None

    def consume(
        self,
        batch: DiscoveryBatch,
        context: BatchConsumptionContext,
    ) -> BatchAcknowledgement:
        self.received.append(batch.sequence)
        if self.failure is not None:
            raise self.failure
        if self.token is not None:
            self.token.cancel("consumer requested stop")
        if self.status is BatchAcknowledgementStatus.CONFIRMED:
            return _ack(batch, context.session)
        if self.status is BatchAcknowledgementStatus.REJECTED:
            return _ack(
                batch,
                context.session,
                status=self.status,
                processed=0,
                rejected=len(batch.items),
                reason="consumer rejected batch",
            )
        return _ack(
            batch,
            context.session,
            status=self.status,
            processed=0,
            rejected=len(batch.items),
            reason="consumer unavailable",
        )

    def close(self) -> None:
        self.closed = True

    def fail(self, error: Exception) -> None:
        self.reported_failure = error


class AsyncProducer:
    """Asynchronous producer test double."""

    def __init__(self, batches: Iterable[DiscoveryBatch]) -> None:
        self._batches = tuple(batches)
        self.context: BatchProductionContext | None = None
        self.closed = False
        self.cancelled_reason: str | None = None

    def produce_async(
        self,
        context: BatchProductionContext,
    ) -> AsyncIterator[DiscoveryBatch]:
        self.context = context

        async def generate() -> AsyncIterator[DiscoveryBatch]:
            for batch in self._batches:
                yield batch

        return generate()

    async def close_async(self) -> None:
        self.closed = True

    async def cancel_async(self, reason: str) -> None:
        self.cancelled_reason = reason


class AsyncConsumer:
    """Asynchronous confirming consumer test double."""

    def __init__(self) -> None:
        self.received: list[int] = []
        self.closed = False
        self.reported_failure: Exception | None = None

    async def consume_async(
        self,
        batch: DiscoveryBatch,
        context: BatchConsumptionContext,
    ) -> BatchAcknowledgement:
        self.received.append(batch.sequence)
        return _ack(batch, context.session)

    async def close_async(self) -> None:
        self.closed = True

    async def fail_async(self, error: Exception) -> None:
        self.reported_failure = error


@dataclass(frozen=True, slots=True)
class Checkpoint:
    """Read-only checkpoint fixture compatible with the SPR-008E port."""

    id: CanonicalId
    session_id: CanonicalId
    sequence: int
    context: Mapping[str, object]


def test_stream_states_and_valid_transitions_are_canonical() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    stream = DiscoveryStream.synchronous(
        request,
        session,
        (_batch(0, final=True),),
        AdvancingClock(),
    )

    assert stream.state is DiscoveryStreamState.CREATED
    stream.open()
    assert stream.state is DiscoveryStreamState.OPEN
    with pytest.raises(DiscoveryStreamTransitionError):
        stream.open()
    stream.cancel("operator cancelled")
    assert stream.state is DiscoveryStreamState.CANCELLED
    with pytest.raises(DiscoveryStreamTransitionError):
        stream.fail("late failure")


def test_synchronous_stream_iteration_is_ordered_and_one_pass() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    stream = DiscoveryStream.synchronous(
        request,
        session,
        (_batch(0, final=False), _batch(1, final=True)),
        AdvancingClock(),
    )

    assert [batch.sequence for batch in stream] == [0, 1]
    assert stream.state is DiscoveryStreamState.COMPLETED
    with pytest.raises(Exception, match="only be iterated once"):
        list(stream)


def test_asynchronous_stream_iteration_is_ordered() -> None:
    request = _request()
    session = DiscoverySession.create(request)

    async def batches() -> AsyncIterator[DiscoveryBatch]:
        yield _batch(0, final=False)
        yield _batch(1, final=True)

    stream = DiscoveryStream.asynchronous(
        request,
        session,
        batches(),
        AdvancingClock(),
    )

    async def collect() -> list[int]:
        return [batch.sequence async for batch in stream]

    assert asyncio.run(collect()) == [0, 1]
    assert stream.state is DiscoveryStreamState.COMPLETED


def test_duplicate_sequence_and_identity_are_rejected() -> None:
    request = _request()
    duplicate_id = CanonicalId.new()
    stream = DiscoveryStream.synchronous(
        request,
        DiscoverySession.create(request),
        (
            _batch(0, final=False, batch_id=duplicate_id),
            _batch(0, final=True),
        ),
        AdvancingClock(),
    )
    with pytest.raises(DuplicateBatchError, match="sequence"):
        list(stream)

    request = _request()
    stream = DiscoveryStream.synchronous(
        request,
        DiscoverySession.create(request),
        (
            _batch(0, final=False, batch_id=duplicate_id),
            _batch(1, final=True, batch_id=duplicate_id),
        ),
        AdvancingClock(),
    )
    with pytest.raises(DuplicateBatchError, match="identity"):
        list(stream)


def test_invalid_or_missing_final_sequence_is_rejected() -> None:
    request = _request()
    stream = DiscoveryStream.synchronous(
        request,
        DiscoverySession.create(request),
        (_batch(1, final=True),),
        AdvancingClock(),
    )
    with pytest.raises(InvalidBatchSequenceError, match="expected"):
        list(stream)

    request = _request()
    stream = DiscoveryStream.synchronous(
        request,
        DiscoverySession.create(request),
        (_batch(0, final=False),),
        AdvancingClock(),
    )
    with pytest.raises(InvalidBatchSequenceError, match="final"):
        list(stream)


def test_cursor_is_versioned_deterministic_and_round_trips() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    cursor = BatchCursor(
        request.id,
        session.id,
        7,
        {"partition": "alpha", "offsets": [1, 2]},
    )

    assert cursor.schema_version == BATCH_CURSOR_SCHEMA_VERSION
    assert BatchCursor.from_json(cursor.to_json()) == cursor
    assert cursor.to_json() == BatchCursor.from_dict(cursor.to_dict()).to_json()
    with pytest.raises(TypeError):
        cursor.state["partition"] = "beta"  # type: ignore[index]


def test_cursor_rejects_unknown_fields_versions_and_locations() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    payload = BatchCursor(request.id, session.id, 0).to_dict()

    with pytest.raises(InvalidBatchCursorError, match="unknown"):
        BatchCursor.from_dict({**payload, "provider_token": "opaque"})
    with pytest.raises(InvalidBatchCursorError, match="schema_version"):
        BatchCursor.from_dict({**payload, "schema_version": "2.0"})
    with pytest.raises(InvalidBatchCursorError, match="location"):
        BatchCursor(request.id, session.id, 0, {"path": "logical"})
    with pytest.raises(InvalidBatchCursorError, match="location"):
        BatchCursor(request.id, session.id, 0, {"value": "C:/data"})


def test_acknowledgements_cover_confirmation_rejection_and_partial() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    batch = _batch(
        0,
        final=True,
        items=(_item("logical:1"), _item("logical:2")),
    )
    confirmed = _ack(batch, session)
    rejected = _ack(
        batch,
        session,
        status=BatchAcknowledgementStatus.REJECTED,
        processed=0,
        rejected=2,
        reason="policy rejection",
    )
    partial = _ack(
        batch,
        session,
        status=BatchAcknowledgementStatus.PARTIAL,
        processed=1,
        rejected=1,
        reason="one invalid item",
    )

    assert confirmed.status is BatchAcknowledgementStatus.CONFIRMED
    assert rejected.rejected_items == 2
    assert partial.processed_items == partial.rejected_items == 1
    with pytest.raises(InvalidBatchAcknowledgementError, match="partial"):
        _ack(
            batch,
            session,
            status=BatchAcknowledgementStatus.PARTIAL,
            processed=2,
            rejected=0,
            reason="invalid partial",
        )


def test_synchronous_pipeline_processes_incrementally_and_closes() -> None:
    request = _request()
    producer = SyncProducer(
        (_batch(0, final=False), _batch(1, final=True))
    )
    consumer = SyncConsumer()

    execution = StreamingDiscoveryPipeline(AdvancingClock()).execute(
        request,
        producer,
        consumer,
        provider_id="provider.streaming",
    )

    assert consumer.received == [0, 1]
    assert producer.closed and consumer.closed
    assert execution.session.state is DiscoverySessionState.COMPLETED
    assert execution.cursor.next_sequence == 2
    assert execution.metrics.batches_produced == 2
    assert execution.metrics.batches_consumed == 2


def test_asynchronous_pipeline_processes_incrementally_and_closes() -> None:
    request = _request()
    producer = AsyncProducer(
        (_batch(0, final=False), _batch(1, final=True))
    )
    consumer = AsyncConsumer()

    execution = asyncio.run(
        StreamingDiscoveryPipeline(AdvancingClock()).execute_async(
            request,
            producer,
            consumer,
            provider_id="provider.streaming.async",
        )
    )

    assert isinstance(producer, AsyncBatchProducer)
    assert isinstance(consumer, AsyncBatchConsumer)
    assert consumer.received == [0, 1]
    assert producer.closed and consumer.closed
    assert execution.metrics.terminal_state is DiscoveryStreamState.COMPLETED


def test_pipeline_reuses_session_token_checkpoint_and_cursor() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    token = CancellationToken.create()
    cursor = BatchCursor(request.id, session.id, 3, {"partition": "alpha"})
    checkpoint = Checkpoint(CanonicalId.new(), session.id, 3, {"safe": True})
    producer = SyncProducer((_batch(3, final=True),))

    execution = StreamingDiscoveryPipeline(AdvancingClock()).execute(
        request,
        producer,
        SyncConsumer(),
        provider_id="provider.resume",
        session=session,
        cancellation_token=token,
        checkpoint=checkpoint,
        cursor=cursor,
    )

    assert execution.session is session
    assert execution.checkpoint is checkpoint
    assert isinstance(checkpoint, DiscoveryCheckpoint)
    assert producer.context is not None
    assert producer.context.cancellation_token is token
    assert producer.context.cursor is cursor
    assert execution.cursor.next_sequence == 4
    assert execution.cursor.state == cursor.state


def test_cooperative_cancellation_stops_pipeline_and_notifies_producer() -> None:
    request = _request()
    token = CancellationToken.create()
    producer = SyncProducer(
        (_batch(0, final=False), _batch(1, final=True))
    )
    consumer = SyncConsumer(token=token)

    with pytest.raises(DiscoveryCancelledError, match="consumer requested stop"):
        StreamingDiscoveryPipeline(AdvancingClock()).execute(
            request,
            producer,
            consumer,
            provider_id="provider.cancel",
            cancellation_token=token,
        )

    assert producer.cancelled_reason == "consumer requested stop"
    assert producer.closed and consumer.closed


def test_producer_failure_is_controlled_and_preserves_cause() -> None:
    request = _request()
    cause = RuntimeError("provider connection lost")
    producer = SyncProducer((_batch(0, final=False),), failure=cause)
    consumer = SyncConsumer()

    with pytest.raises(BatchProducerError) as captured:
        StreamingDiscoveryPipeline(AdvancingClock()).execute(
            request,
            producer,
            consumer,
            provider_id="provider.failure",
        )

    assert captured.value.__cause__ is cause
    assert consumer.reported_failure is captured.value


def test_consumer_failure_is_controlled_and_preserves_cause() -> None:
    request = _request()
    cause = RuntimeError("consumer unavailable")
    consumer = SyncConsumer(failure=cause)

    with pytest.raises(BatchConsumerError) as captured:
        StreamingDiscoveryPipeline(AdvancingClock()).execute(
            request,
            SyncProducer((_batch(0, final=True),)),
            consumer,
            provider_id="provider.consumer-failure",
        )

    assert captured.value.__cause__ is cause
    assert consumer.reported_failure is captured.value


def test_backpressure_enforces_batch_size_and_timeout() -> None:
    request = _request()
    oversized = _batch(
        0,
        final=True,
        items=(_item("logical:1"), _item("logical:2")),
    )
    with pytest.raises(BackpressureViolationError, match="limit"):
        StreamingDiscoveryPipeline(AdvancingClock()).execute(
            request,
            SyncProducer((oversized,)),
            SyncConsumer(),
            provider_id="provider.backpressure",
            backpressure=BackpressurePolicy(max_items_per_batch=1),
        )

    with pytest.raises(BackpressureViolationError, match="timeout"):
        StreamingDiscoveryPipeline(AdvancingClock(step=2.0)).execute(
            _request(),
            SyncProducer((_batch(0, final=True),)),
            SyncConsumer(),
            provider_id="provider.timeout",
            backpressure=BackpressurePolicy(timeout_seconds=0.5),
        )


def test_unavailable_consumer_policy_can_reject_or_cancel() -> None:
    item = _item("logical:unavailable")
    reject_execution = StreamingDiscoveryPipeline(AdvancingClock()).execute(
        _request(),
        SyncProducer((_batch(0, final=True, items=(item,)),)),
        SyncConsumer(BatchAcknowledgementStatus.FAILED),
        provider_id="provider.reject-unavailable",
        backpressure=BackpressurePolicy(
            consumer_unavailable=ConsumerUnavailableBehavior.REJECT
        ),
    )
    assert reject_execution.metrics.batches_rejected == 1

    with pytest.raises(DiscoveryCancelledError, match="unavailable"):
        StreamingDiscoveryPipeline(AdvancingClock()).execute(
            _request(),
            SyncProducer((_batch(0, final=True, items=(item,)),)),
            SyncConsumer(BatchAcknowledgementStatus.FAILED),
            provider_id="provider.cancel-unavailable",
            backpressure=BackpressurePolicy(
                consumer_unavailable=ConsumerUnavailableBehavior.CANCEL
            ),
        )


def test_metrics_account_for_partial_processing_and_duration() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    batch = _batch(
        0,
        final=True,
        items=(_item("logical:1"), _item("logical:2")),
    )
    stream = DiscoveryStream.synchronous(
        request,
        session,
        (batch,),
        AdvancingClock(),
    )
    yielded = next(iter(stream))
    stream.record_acknowledgement(
        yielded,
        _ack(
            yielded,
            session,
            status=BatchAcknowledgementStatus.PARTIAL,
            processed=1,
            rejected=1,
            reason="partial",
        ),
    )
    stream.complete()

    assert stream.metrics.items_produced == 2
    assert stream.metrics.items_consumed == 1
    assert stream.metrics.items_rejected == 1
    assert stream.metrics.batches_rejected == 1
    assert stream.metrics.duration_seconds == 1.0


def test_public_streaming_api_and_error_hierarchy_are_canonical() -> None:
    from cko.core import discovery

    names = {
        "BatchCursor",
        "BackpressurePolicy",
        "BatchAcknowledgement",
        "BatchProducer",
        "AsyncBatchProducer",
        "BatchConsumer",
        "AsyncBatchConsumer",
        "DiscoveryStream",
        "StreamingDiscoveryPipeline",
    }
    assert names.issubset(set(discovery.__all__))
    assert isinstance(SyncProducer(()), BatchProducer)
    assert isinstance(SyncConsumer(), BatchConsumer)
    for name in names:
        value = getattr(discovery, name)
        assert value.__module__.startswith("cko.core.discovery")
    for error_type in (
        InvalidBatchCursorError,
        InvalidBatchSequenceError,
        DuplicateBatchError,
        BatchProducerError,
        BatchConsumerError,
        BackpressureViolationError,
    ):
        assert issubclass(error_type, DiscoveryError)


def test_streaming_modules_are_documented_typed_utf8_and_pep8() -> None:
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    filenames = (
        "stream.py",
        "streaming_contracts.py",
        "streaming_errors.py",
        "streaming_models.py",
        "streaming_pipeline.py",
    )
    for filename in filenames:
        source = (root / filename).read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert ast.get_docstring(tree)
        assert max(len(line) for line in source.splitlines()) <= 88
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assert ast.get_docstring(node), (filename, node.name)
                assert node.returns is not None, (filename, node.name)
                arguments = (*node.args.posonlyargs, *node.args.args)
                for argument in arguments:
                    if argument.arg not in {"self", "cls"}:
                        assert argument.annotation is not None, (
                            filename,
                            node.name,
                            argument.arg,
                        )


def test_streaming_modules_have_no_forbidden_imports_or_placeholders() -> None:
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    paths = [
        root / name
        for name in (
            "stream.py",
            "streaming_contracts.py",
            "streaming_errors.py",
            "streaming_models.py",
            "streaming_pipeline.py",
        )
    ]
    forbidden = {
        "os",
        "pathlib",
        "sqlite3",
        "requests",
        "urllib",
        "threading",
        "multiprocessing",
        "google",
        "openai",
    }
    banned_tokens = ("TODO", "NotImplementedError")

    for path in paths:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        assert imports.isdisjoint(forbidden), path.name
        assert not any(token in source for token in banned_tokens), path.name
        assert not any(
            isinstance(node, ast.Constant) and node.value is Ellipsis
            for node in ast.walk(tree)
        ), path.name


def test_public_functions_expose_runtime_type_hints() -> None:
    public_types = (
        BatchCursor,
        BatchAcknowledgement,
        BackpressurePolicy,
        DiscoveryStream,
        StreamingDiscoveryPipeline,
    )
    for public_type in public_types:
        for name, member in inspect.getmembers(public_type, inspect.isfunction):
            if name.startswith("_") and name not in {"__iter__", "__aiter__"}:
                continue
            signature = inspect.signature(member)
            assert signature.return_annotation is not inspect.Signature.empty
            for parameter in signature.parameters.values():
                if parameter.name not in {"self", "cls"}:
                    assert parameter.annotation is not inspect.Signature.empty


def test_defensive_stream_boundaries_reject_inconsistent_sources() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    other_request = _request()
    other_session = DiscoverySession.create(other_request)

    with pytest.raises(InvalidDiscoveryStreamError, match="stream_id"):
        DiscoveryStream(
            stream_id="invalid",  # type: ignore[arg-type]
            request=request,
            session=session,
            clock=AdvancingClock(),
            batches=(),
        )
    with pytest.raises(InvalidDiscoveryStreamError, match="session"):
        DiscoveryStream(
            stream_id=CanonicalId.new(),
            request=request,
            session=other_session,
            clock=AdvancingClock(),
            batches=(),
        )
    with pytest.raises(InvalidDiscoveryStreamError, match="exactly one"):
        DiscoveryStream(
            stream_id=CanonicalId.new(),
            request=request,
            session=session,
            clock=AdvancingClock(),
        )

    wrong_request_cursor = BatchCursor(other_request.id, session.id, 0)
    with pytest.raises(InvalidDiscoveryStreamError, match="request_id"):
        DiscoveryStream.synchronous(
            request,
            session,
            (),
            AdvancingClock(),
            cursor=wrong_request_cursor,
        )
    wrong_session_cursor = BatchCursor(request.id, other_session.id, 0)
    with pytest.raises(InvalidDiscoveryStreamError, match="session_id"):
        DiscoveryStream.synchronous(
            request,
            session,
            (),
            AdvancingClock(),
            cursor=wrong_session_cursor,
        )


def test_stream_rejects_wrong_iteration_mode_values_and_late_batches() -> None:
    request = _request()
    session = DiscoverySession.create(request)

    async def async_batches() -> AsyncIterator[DiscoveryBatch]:
        yield _batch(0, final=True)

    async_stream = DiscoveryStream.asynchronous(
        request,
        session,
        async_batches(),
        AdvancingClock(),
    )
    with pytest.raises(InvalidDiscoveryStreamError, match="synchronously"):
        list(async_stream)

    sync_stream = DiscoveryStream.synchronous(
        request,
        session,
        (_batch(0, final=True),),
        AdvancingClock(),
    )

    async def consume_wrong_mode() -> None:
        async for _ in sync_stream:
            raise AssertionError("wrong-mode stream yielded a batch")

    with pytest.raises(InvalidDiscoveryStreamError, match="asynchronously"):
        asyncio.run(consume_wrong_mode())

    invalid_value_stream = DiscoveryStream.synchronous(
        request,
        session,
        (object(),),  # type: ignore[arg-type]
        AdvancingClock(),
    )
    with pytest.raises(InvalidDiscoveryStreamError, match="DiscoveryBatch"):
        list(invalid_value_stream)

    late_batch_stream = DiscoveryStream.synchronous(
        request,
        session,
        (_batch(0, final=True), _batch(1, final=True)),
        AdvancingClock(),
    )
    with pytest.raises(InvalidBatchSequenceError, match="follow"):
        list(late_batch_stream)


def test_stream_rejects_inconsistent_acknowledgements() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    batch = _batch(0, final=True, items=(_item("logical:ack"),))
    unopened = DiscoveryStream.synchronous(
        request,
        session,
        (batch,),
        AdvancingClock(),
    )
    with pytest.raises(DiscoveryStreamTransitionError, match="open"):
        unopened.record_acknowledgement(batch, _ack(batch, session))

    stream = DiscoveryStream.synchronous(
        request,
        session,
        (batch,),
        AdvancingClock(),
    )
    yielded = next(iter(stream))
    wrong_batch_ack = BatchAcknowledgement(
        CanonicalId.new(),
        session.id,
        BatchAcknowledgementStatus.CONFIRMED,
        1,
        0,
        NOW,
    )
    with pytest.raises(InvalidBatchAcknowledgementError, match="batch_id"):
        stream.record_acknowledgement(yielded, wrong_batch_ack)
    wrong_session_ack = BatchAcknowledgement(
        yielded.id,
        CanonicalId.new(),
        BatchAcknowledgementStatus.CONFIRMED,
        1,
        0,
        NOW,
    )
    with pytest.raises(InvalidBatchAcknowledgementError, match="session_id"):
        stream.record_acknowledgement(yielded, wrong_session_ack)
    wrong_count_ack = BatchAcknowledgement(
        yielded.id,
        session.id,
        BatchAcknowledgementStatus.CONFIRMED,
        0,
        0,
        NOW,
    )
    with pytest.raises(InvalidBatchAcknowledgementError, match="counts"):
        stream.record_acknowledgement(yielded, wrong_count_ack)


def test_cursor_and_acknowledgement_defensive_validation() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    cursor = BatchCursor(request.id, session.id, 0)
    payload = cursor.to_dict()

    invalid_cursors = (
        lambda: BatchCursor("bad", session.id, 0),  # type: ignore[arg-type]
        lambda: BatchCursor(request.id, "bad", 0),  # type: ignore[arg-type]
        lambda: BatchCursor(request.id, session.id, -1),
        lambda: BatchCursor(request.id, session.id, 0, {1: "bad"}),
        lambda: BatchCursor(request.id, session.id, 0, {"value": object()}),
        lambda: BatchCursor.from_dict(
            {key: value for key, value in payload.items() if key != "state"}
        ),
        lambda: BatchCursor.from_dict({**payload, "request_id": "bad"}),
        lambda: BatchCursor.from_dict({**payload, "next_sequence": "0"}),
        lambda: BatchCursor.from_dict({**payload, "state": []}),
        lambda: BatchCursor.from_dict({**payload, "schema_version": 1}),
        lambda: BatchCursor.from_json("{"),
        lambda: BatchCursor.from_json("[]"),
    )
    for construct in invalid_cursors:
        with pytest.raises(InvalidBatchCursorError):
            construct()

    batch_id = CanonicalId.new()
    invalid_acknowledgements = (
        lambda: BatchAcknowledgement(
            "bad", session.id, "confirmed", 0, 0, NOW  # type: ignore[arg-type]
        ),
        lambda: BatchAcknowledgement(
            batch_id, "bad", "confirmed", 0, 0, NOW  # type: ignore[arg-type]
        ),
        lambda: BatchAcknowledgement(
            batch_id, session.id, "confirmed", -1, 0, NOW
        ),
        lambda: BatchAcknowledgement(
            batch_id, session.id, "confirmed", 0, 1, NOW
        ),
        lambda: BatchAcknowledgement(
            batch_id, session.id, "rejected", 1, 0, NOW, "rejected"
        ),
        lambda: BatchAcknowledgement(
            batch_id, session.id, "failed", 0, 0, NOW
        ),
        lambda: BatchAcknowledgement(
            batch_id,
            session.id,
            "confirmed",
            0,
            0,
            NOW,
            metrics={"bad": True},
        ),
    )
    for construct in invalid_acknowledgements:
        with pytest.raises(InvalidBatchAcknowledgementError):
            construct()


def test_policy_metrics_and_execution_defensive_validation() -> None:
    for kwargs in (
        {"max_pending_batches": 0},
        {"max_items_per_batch": -1},
        {"memory_limit_bytes": True},
        {"timeout_seconds": "slow"},
    ):
        with pytest.raises(ValueError, match="greater than zero"):
            BackpressurePolicy(**kwargs)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="negative"):
        StreamMetrics(batches_produced=-1)
    with pytest.raises(ValueError, match="started_at"):
        StreamMetrics(completed_at=NOW)
    with pytest.raises(ValueError, match="terminal"):
        StreamMetrics(terminal_state=DiscoveryStreamState.OPEN)

    request = _request()
    session = DiscoverySession.create(request)
    cursor = BatchCursor(request.id, session.id, 0)
    with pytest.raises(TypeError, match="stream_id"):
        StreamingExecution(
            session,
            "bad",  # type: ignore[arg-type]
            StreamMetrics(),
            cursor,
        )


def test_production_and_consumption_contexts_validate_identities() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    other_request = _request()
    other_session = DiscoverySession.create(other_request)
    token = CancellationToken.create()
    policy = BackpressurePolicy()

    with pytest.raises(ValueError, match="production session"):
        BatchProductionContext(
            request,
            other_session,
            token,
            policy,
        )
    with pytest.raises(ValueError, match="cursor request_id"):
        BatchProductionContext(
            request,
            session,
            token,
            policy,
            BatchCursor(other_request.id, session.id, 0),
        )
    with pytest.raises(ValueError, match="cursor session_id"):
        BatchProductionContext(
            request,
            session,
            token,
            policy,
            BatchCursor(request.id, other_session.id, 0),
        )
    checkpoint = Checkpoint(CanonicalId.new(), other_session.id, 0, {})
    with pytest.raises(ValueError, match="checkpoint session_id"):
        BatchProductionContext(
            request,
            session,
            token,
            policy,
            checkpoint=checkpoint,
        )
    with pytest.raises(ValueError, match="consumption session"):
        BatchConsumptionContext(request, other_session, token)


def test_abstract_ports_fail_explicitly_when_invoked_directly() -> None:
    request = _request()
    session = DiscoverySession.create(request)
    token = CancellationToken.create()
    production = BatchProductionContext(
        request,
        session,
        token,
        BackpressurePolicy(),
    )
    consumption = BatchConsumptionContext(request, session, token)
    batch = _batch(0, final=True)

    with pytest.raises(BatchProducerError):
        BatchProducer.produce(object(), production)  # type: ignore[misc]
    with pytest.raises(BatchProducerError):
        BatchProducer.close(object())  # type: ignore[misc]
    with pytest.raises(BatchProducerError):
        BatchProducer.cancel(object(), "stop")  # type: ignore[misc]
    with pytest.raises(BatchConsumerError):
        BatchConsumer.consume(object(), batch, consumption)  # type: ignore[misc]
    with pytest.raises(BatchConsumerError):
        BatchConsumer.close(object())  # type: ignore[misc]
    with pytest.raises(BatchConsumerError):
        BatchConsumer.fail(object(), RuntimeError("failed"))  # type: ignore[misc]

    async def invoke_async_ports() -> None:
        with pytest.raises(BatchProducerError):
            AsyncBatchProducer.produce_async(
                object(), production  # type: ignore[misc]
            )
        with pytest.raises(BatchProducerError):
            await AsyncBatchProducer.close_async(object())  # type: ignore[misc]
        with pytest.raises(BatchProducerError):
            await AsyncBatchProducer.cancel_async(
                object(), "stop"  # type: ignore[misc]
            )
        with pytest.raises(BatchConsumerError):
            await AsyncBatchConsumer.consume_async(
                object(), batch, consumption  # type: ignore[misc]
            )
        with pytest.raises(BatchConsumerError):
            await AsyncBatchConsumer.close_async(object())  # type: ignore[misc]
        with pytest.raises(BatchConsumerError):
            await AsyncBatchConsumer.fail_async(
                object(), RuntimeError("failed")  # type: ignore[misc]
            )

    asyncio.run(invoke_async_ports())


def test_async_pipeline_controls_cancellation_and_failures() -> None:
    class FailingAsyncProducer(AsyncProducer):
        def produce_async(
            self,
            context: BatchProductionContext,
        ) -> AsyncIterator[DiscoveryBatch]:
            raise RuntimeError("async producer start failed")

    class FailingAsyncConsumer(AsyncConsumer):
        async def consume_async(
            self,
            batch: DiscoveryBatch,
            context: BatchConsumptionContext,
        ) -> BatchAcknowledgement:
            raise RuntimeError("async consumer failed")

    with pytest.raises(BatchProducerError) as producer_error:
        asyncio.run(
            StreamingDiscoveryPipeline(AdvancingClock()).execute_async(
                _request(),
                FailingAsyncProducer(()),
                AsyncConsumer(),
                provider_id="provider.async-start-failure",
            )
        )
    assert isinstance(producer_error.value.__cause__, RuntimeError)

    consumer = FailingAsyncConsumer()
    with pytest.raises(BatchConsumerError) as consumer_error:
        asyncio.run(
            StreamingDiscoveryPipeline(AdvancingClock()).execute_async(
                _request(),
                AsyncProducer((_batch(0, final=True),)),
                consumer,
                provider_id="provider.async-consumer-failure",
            )
        )
    assert isinstance(consumer_error.value.__cause__, RuntimeError)
    assert consumer.reported_failure is consumer_error.value

    token = CancellationToken.create()
    token.cancel("cancel before async start")
    producer = AsyncProducer((_batch(0, final=True),))
    with pytest.raises(DiscoveryCancelledError, match="before async"):
        asyncio.run(
            StreamingDiscoveryPipeline(AdvancingClock()).execute_async(
                _request(),
                producer,
                AsyncConsumer(),
                provider_id="provider.async-cancel",
                cancellation_token=token,
            )
        )
    assert producer.cancelled_reason == "cancel before async start"
