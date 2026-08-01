"""Provider foundation, execution and regression contracts for SPR-008E."""

from __future__ import annotations

import asyncio
import ast
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Mapping

import pytest

from cko.core import CanonicalId
from cko.core.discovery import (
    AsyncDiscoveryProvider,
    CancellationToken,
    ContextualDiscoveryProvider,
    DefaultDiscoveryValidator,
    DiscoveryCancelledError,
    DiscoveryCapability,
    DiscoveryCheckpoint,
    DiscoveryContext,
    DiscoveryExecutionContext,
    DiscoveryExecutionError,
    DiscoveryExecutionMode,
    DiscoveryExecutor,
    DiscoveryMetrics,
    DiscoveryPipeline,
    DiscoveryPolicy,
    DiscoveryProviderDescriptor,
    DiscoveryProviderFactory,
    DiscoveryProviderNotFoundError,
    DiscoveryProviderRegistrationError,
    DiscoveryProviderRegistry,
    DiscoveryProviderResolutionError,
    DiscoveryProviderResolver,
    DiscoveryRequest,
    DiscoveryResult,
    DiscoveryScope,
    DiscoverySession,
    DiscoverySessionState,
    DiscoverySessionStateError,
    DiscoverySourceId,
    DiscoveryStatus,
)


NOW = datetime(2026, 7, 14, 22, 0, tzinfo=UTC)
SOURCE_ID = DiscoverySourceId("logical:spr008e")
CAPABILITIES = frozenset(
    {
        DiscoveryCapability.LISTING,
        DiscoveryCapability.METADATA_READ,
        DiscoveryCapability.CANCELLATION,
        DiscoveryCapability.CHECKPOINTS,
    }
)


@dataclass(frozen=True, slots=True)
class Source:
    id: DiscoverySourceId = SOURCE_ID
    capabilities: frozenset[DiscoveryCapability] = CAPABILITIES


class AdvancingClock:
    def __init__(self) -> None:
        self._value = NOW

    def now(self) -> datetime:
        value = self._value
        self._value += timedelta(seconds=1)
        return value


def _request(
    capabilities: tuple[DiscoveryCapability, ...] = (
        DiscoveryCapability.LISTING,
        DiscoveryCapability.METADATA_READ,
    ),
) -> DiscoveryRequest:
    return DiscoveryRequest(
        id=CanonicalId.new(),
        source_id=SOURCE_ID,
        scope=DiscoveryScope("logical:provider-foundation"),
        policy=DiscoveryPolicy(max_items=10),
        context=DiscoveryContext("corr-008e", NOW, actor="test"),
        required_capabilities=capabilities,
    )


def _result(request: DiscoveryRequest) -> DiscoveryResult:
    return DiscoveryResult(
        request_id=request.id,
        source_id=request.source_id,
        status=DiscoveryStatus.COMPLETED,
        items=(),
        warnings=(),
        errors=(),
        metrics=DiscoveryMetrics(0, 0, 0, 0, 0, NOW, NOW),
    )


class SyncProvider:
    def discover(self, source: Source, request: DiscoveryRequest) -> DiscoveryResult:
        assert source.id == request.source_id
        return _result(request)


class ContextProvider:
    def __init__(self) -> None:
        self.context: DiscoveryExecutionContext | None = None

    def discover_context(
        self,
        context: DiscoveryExecutionContext,
    ) -> DiscoveryResult:
        self.context = context
        context.cancellation_token.throw_if_cancelled()
        return _result(context.request)


class AsyncProvider:
    def __init__(self) -> None:
        self.context: DiscoveryExecutionContext | None = None

    async def discover_async(
        self,
        context: DiscoveryExecutionContext,
    ) -> DiscoveryResult:
        self.context = context
        await asyncio.sleep(0)
        context.cancellation_token.throw_if_cancelled()
        return _result(context.request)


class CancellingProvider(ContextProvider):
    def discover_context(
        self,
        context: DiscoveryExecutionContext,
    ) -> DiscoveryResult:
        self.context = context
        context.cancellation_token.cancel("consumer stopped")
        return _result(context.request)


class InvalidResultProvider:
    def discover(self, source: Source, request: DiscoveryRequest) -> object:
        return {"request_id": str(request.id), "source_id": str(source.id)}


@dataclass(frozen=True, slots=True)
class Checkpoint:
    id: CanonicalId
    session_id: CanonicalId
    sequence: int
    context: Mapping[str, object]


def _descriptor(
    provider_id: str = "provider.sync",
    provider: object | None = None,
    *,
    capabilities: frozenset[DiscoveryCapability] = CAPABILITIES,
    modes: frozenset[DiscoveryExecutionMode] = frozenset(
        {DiscoveryExecutionMode.SYNCHRONOUS}
    ),
    priority: int = 0,
) -> DiscoveryProviderDescriptor:
    return DiscoveryProviderDescriptor(
        provider_id=provider_id,
        provider=provider or SyncProvider(),
        capabilities=capabilities,
        execution_modes=modes,
        priority=priority,
    )


def _pipeline(
    descriptor: DiscoveryProviderDescriptor,
) -> tuple[DiscoveryProviderRegistry, DiscoveryPipeline]:
    registry = DiscoveryProviderRegistry()
    registry.register(descriptor)
    factory = DiscoveryProviderFactory(registry, DiscoveryProviderResolver())
    executor = DiscoveryExecutor(DefaultDiscoveryValidator())
    return registry, DiscoveryPipeline(factory, executor, AdvancingClock())


def test_registry_register_get_snapshot_and_unregister() -> None:
    registry = DiscoveryProviderRegistry()
    descriptor = _descriptor()

    registry.register(descriptor)

    assert len(registry) == 1
    assert registry.get("provider.sync") is descriptor
    assert registry.descriptors() == (descriptor,)
    assert registry.snapshot()["provider.sync"] is descriptor
    with pytest.raises(TypeError):
        registry.snapshot()["other"] = descriptor  # type: ignore[index]
    assert registry.unregister("provider.sync") is descriptor
    assert len(registry) == 0


def test_registry_rejects_duplicates_and_unknown_identity() -> None:
    registry = DiscoveryProviderRegistry()
    registry.register(_descriptor())

    with pytest.raises(DiscoveryProviderRegistrationError):
        registry.register(_descriptor())
    with pytest.raises(DiscoveryProviderNotFoundError):
        registry.get("provider.unknown")
    with pytest.raises(DiscoveryProviderNotFoundError):
        registry.unregister("provider.unknown")


@pytest.mark.parametrize(
    ("provider", "capabilities", "modes"),
    [
        (SyncProvider(), frozenset(), frozenset({DiscoveryExecutionMode.SYNCHRONOUS})),
        (SyncProvider(), CAPABILITIES, frozenset()),
        (object(), CAPABILITIES, frozenset({DiscoveryExecutionMode.SYNCHRONOUS})),
        (object(), CAPABILITIES, frozenset({DiscoveryExecutionMode.ASYNCHRONOUS})),
    ],
)
def test_descriptor_rejects_incompatible_declarations(
    provider: object,
    capabilities: frozenset[DiscoveryCapability],
    modes: frozenset[DiscoveryExecutionMode],
) -> None:
    with pytest.raises(DiscoveryProviderRegistrationError):
        _descriptor(provider=provider, capabilities=capabilities, modes=modes)


def test_resolver_prefers_priority_then_capability_specificity() -> None:
    resolver = DiscoveryProviderResolver()
    requested = frozenset({DiscoveryCapability.LISTING})
    broad = _descriptor("broad", capabilities=CAPABILITIES, priority=1)
    exact = _descriptor("exact", capabilities=requested, priority=1)
    high = _descriptor("high", capabilities=CAPABILITIES, priority=2)

    assert resolver.resolve(
        (broad, exact), requested, DiscoveryExecutionMode.SYNCHRONOUS
    ) is exact
    assert resolver.resolve(
        (exact, high), requested, DiscoveryExecutionMode.SYNCHRONOUS
    ) is high


def test_resolver_uses_identity_as_deterministic_tie_breaker() -> None:
    resolver = DiscoveryProviderResolver()
    first = _descriptor("provider.a")
    second = _descriptor("provider.b")

    selected = resolver.resolve(
        (second, first),
        frozenset({DiscoveryCapability.LISTING}),
        DiscoveryExecutionMode.SYNCHRONOUS,
    )

    assert selected is first


def test_resolver_rejects_missing_mode_or_capabilities() -> None:
    resolver = DiscoveryProviderResolver()
    with pytest.raises(DiscoveryProviderResolutionError):
        resolver.resolve(
            (_descriptor(),),
            frozenset({DiscoveryCapability.CONTENT_READ}),
            DiscoveryExecutionMode.SYNCHRONOUS,
        )
    with pytest.raises(DiscoveryProviderResolutionError):
        resolver.resolve(
            (_descriptor(),),
            frozenset({DiscoveryCapability.LISTING}),
            DiscoveryExecutionMode.ASYNCHRONOUS,
        )


def test_factory_validates_source_request_and_explicit_provider() -> None:
    registry = DiscoveryProviderRegistry()
    registry.register(_descriptor())
    factory = DiscoveryProviderFactory(registry, DiscoveryProviderResolver())
    request = _request()

    assert factory.create(
        Source(), request, DiscoveryExecutionMode.SYNCHRONOUS
    ).provider_id == "provider.sync"
    assert factory.create(
        Source(),
        request,
        DiscoveryExecutionMode.SYNCHRONOUS,
        provider_id="provider.sync",
    ).provider_id == "provider.sync"

    incompatible_source = Source(capabilities=frozenset({DiscoveryCapability.LISTING}))
    with pytest.raises(Exception, match="required capabilities"):
        factory.create(
            incompatible_source,
            request,
            DiscoveryExecutionMode.SYNCHRONOUS,
        )


def test_cancellation_token_is_canonical_idempotent_and_cooperative() -> None:
    token = CancellationToken.create()

    assert isinstance(token.id, CanonicalId)
    assert token.is_cancelled is False
    assert token.cancel("operator request") is True
    assert token.cancel("ignored second request") is False
    assert token.reason == "operator request"
    with pytest.raises(DiscoveryCancelledError, match="operator request"):
        token.throw_if_cancelled()


def test_session_tracks_identity_state_metrics_and_context() -> None:
    request = _request()
    session = DiscoverySession.create(request)

    assert isinstance(session.id, CanonicalId)
    assert session.context == request.context
    assert session.state is DiscoverySessionState.CREATED

    session.start("provider.sync", NOW)
    session.complete(_result(request), NOW + timedelta(seconds=2))

    assert session.state is DiscoverySessionState.COMPLETED
    assert session.provider_id == "provider.sync"
    assert session.metrics.started_at == NOW
    assert session.metrics.completed_at == NOW + timedelta(seconds=2)
    assert session.metrics.observed_count == 0
    with pytest.raises(DiscoverySessionStateError):
        session.start("provider.sync", NOW)


def test_session_records_failure_and_cancellation_as_terminal_states() -> None:
    failed = DiscoverySession.create(_request())
    failed.start("provider.sync", NOW)
    failed.fail("provider failure", NOW + timedelta(seconds=1))
    assert failed.state is DiscoverySessionState.FAILED
    assert failed.metrics.error_count == 1
    assert failed.failure == "provider failure"

    cancelled = DiscoverySession.create(_request())
    cancelled.cancel("cancelled before resolution", NOW)
    assert cancelled.state is DiscoverySessionState.CANCELLED
    assert cancelled.failure == "cancelled before resolution"


def test_checkpoint_is_only_a_runtime_checkable_abstract_contract() -> None:
    checkpoint = Checkpoint(CanonicalId.new(), CanonicalId.new(), 3, {"cursor": "x"})

    assert isinstance(checkpoint, DiscoveryCheckpoint)
    assert checkpoint.sequence == 3
    assert checkpoint.context == {"cursor": "x"}


def test_sync_pipeline_supports_legacy_provider_contract() -> None:
    _, pipeline = _pipeline(_descriptor())
    request = _request()

    execution = pipeline.execute(Source(), request)

    assert execution.result == _result(request)
    assert execution.provider_id == "provider.sync"
    assert execution.execution_mode is DiscoveryExecutionMode.SYNCHRONOUS
    assert execution.session.state is DiscoverySessionState.COMPLETED


def test_sync_pipeline_passes_context_to_provider() -> None:
    provider = ContextProvider()
    descriptor = _descriptor(provider=provider)
    _, pipeline = _pipeline(descriptor)
    token = CancellationToken.create()
    checkpoint = Checkpoint(CanonicalId.new(), CanonicalId.new(), 1, {"cursor": "a"})

    execution = pipeline.execute(
        Source(),
        _request(),
        cancellation_token=token,
        checkpoint=checkpoint,
    )

    assert isinstance(provider, ContextualDiscoveryProvider)
    assert provider.context is not None
    assert provider.context.cancellation_token is token
    assert provider.context.checkpoint is checkpoint
    assert provider.context.session is execution.session


def test_async_pipeline_executes_coroutine_without_thread_adapter() -> None:
    provider = AsyncProvider()
    descriptor = _descriptor(
        "provider.async",
        provider,
        modes=frozenset({DiscoveryExecutionMode.ASYNCHRONOUS}),
    )
    _, pipeline = _pipeline(descriptor)

    execution = asyncio.run(pipeline.execute_async(Source(), _request()))

    assert isinstance(provider, AsyncDiscoveryProvider)
    assert execution.provider_id == "provider.async"
    assert execution.execution_mode is DiscoveryExecutionMode.ASYNCHRONOUS
    assert execution.session.state is DiscoverySessionState.COMPLETED
    assert provider.context is not None


def test_pipeline_stops_before_provider_when_token_is_cancelled() -> None:
    provider = ContextProvider()
    _, pipeline = _pipeline(_descriptor(provider=provider))
    token = CancellationToken.create()
    token.cancel("cancel before start")

    with pytest.raises(DiscoveryCancelledError, match="cancel before start"):
        pipeline.execute(Source(), _request(), cancellation_token=token)

    assert provider.context is None


def test_pipeline_observes_cancellation_requested_by_context_provider() -> None:
    provider = CancellingProvider()
    _, pipeline = _pipeline(_descriptor(provider=provider))

    with pytest.raises(DiscoveryCancelledError, match="consumer stopped"):
        pipeline.execute(Source(), _request())

    assert provider.context is not None
    assert provider.context.session.state is DiscoverySessionState.CANCELLED


def test_executor_rejects_invalid_provider_result_and_pipeline_marks_failure() -> None:
    descriptor = _descriptor(provider=InvalidResultProvider())
    _, pipeline = _pipeline(descriptor)

    with pytest.raises(DiscoveryExecutionError, match="must return DiscoveryResult"):
        pipeline.execute(Source(), _request())


def test_public_foundation_remains_inside_cko_core_namespace() -> None:
    from cko.core import discovery

    names = {
        "CancellationToken",
        "DiscoveryCheckpoint",
        "DiscoveryExecution",
        "DiscoveryExecutor",
        "DiscoveryPipeline",
        "DiscoveryProviderFactory",
        "DiscoveryProviderRegistry",
        "DiscoveryProviderResolver",
        "DiscoverySession",
    }

    assert names.issubset(set(discovery.__all__))
    for name in names:
        assert getattr(discovery, name).__module__.startswith("cko.core.discovery")


def test_foundation_has_no_forbidden_runtime_imports_or_concrete_scanners() -> None:
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    foundation_files = (
        "cancellation.py",
        "checkpoints.py",
        "execution.py",
        "foundation_errors.py",
        "pipeline.py",
        "providers.py",
        "session.py",
    )
    forbidden_imports = {
        "os",
        "pathlib",
        "sqlite3",
        "requests",
        "google",
        "onedrive",
        "watchdog",
        "threading",
        "multiprocessing",
    }

    for filename in foundation_files:
        content = (root / filename).read_text(encoding="utf-8")
        tree = ast.parse(content)
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
        assert imports.isdisjoint(forbidden_imports)
        assert "Scanner" not in content
        assert "TODO" not in content
        assert not any(
            isinstance(node, ast.Constant) and node.value is Ellipsis
            for node in ast.walk(tree)
        )
