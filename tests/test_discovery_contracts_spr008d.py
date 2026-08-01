"""Contract, model and orchestration tests for SPR-008D."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from cko.core import Asset, CanonicalId, UniversalMetadata
from cko.core.discovery import (
    DISCOVERY_BATCH_COMPLETED,
    DISCOVERY_CANCELLED,
    DISCOVERY_COMPLETED,
    DISCOVERY_EVENT_NAMES,
    DISCOVERY_FAILED,
    DISCOVERY_ITEM_OBSERVED,
    DISCOVERY_STARTED,
    DefaultDiscoveryAssetMapper,
    DefaultDiscoveryValidator,
    DiscoveredItem,
    DiscoveryBatch,
    DiscoveryCapability,
    DiscoveryContext,
    DiscoveryError,
    DiscoveryErrorRecord,
    DiscoveryEvidence,
    DiscoveryMappingError,
    DiscoveryMetrics,
    DiscoveryPolicy,
    DiscoveryProviderError,
    DiscoveryRequest,
    DiscoveryResult,
    DiscoveryScope,
    DiscoveryService,
    DiscoverySource,
    DiscoverySourceId,
    DiscoveryStatus,
    DiscoveryValidationError,
    DiscoveryWarning,
    InvalidDiscoveredItemError,
    InvalidDiscoveryRequestError,
    InvalidDiscoverySourceError,
    UnsupportedDiscoveryCapabilityError,
    create_discovery_event,
    discovery_model_from_dict,
    ensure_supported_capabilities,
    validate_policy,
)
from cko.core.exceptions import CKOError
from cko.core.models import CanonicalEvent


NOW = datetime(2026, 7, 14, 21, 0, tzinfo=UTC)
SOURCE_ID = DiscoverySourceId("logical:unit-test")


def _metadata() -> UniversalMetadata:
    return UniversalMetadata(
        media_type="application/octet-stream",
        created_at=NOW,
        modified_at=NOW,
        language="pt-BR",
        attributes={"observed": {"size": 42}},
    )


def _context() -> DiscoveryContext:
    return DiscoveryContext(
        correlation_id="corr-008d",
        requested_at=NOW,
        actor="unit-test",
        attributes={"tenant": "neutral"},
    )


def _request() -> DiscoveryRequest:
    return DiscoveryRequest(
        id=CanonicalId.new(),
        source_id=SOURCE_ID,
        scope=DiscoveryScope("collection:canonical", {"depth": 2}),
        policy=DiscoveryPolicy(
            include_patterns=("*.md",),
            exclude_patterns=("temporary-*",),
            max_items=20,
            page_size=10,
            timeout_seconds=30.0,
            continue_on_error=True,
        ),
        context=_context(),
        required_capabilities=(
            DiscoveryCapability.LISTING,
            DiscoveryCapability.METADATA_READ,
        ),
    )


def _item(*, canonical: bool = True) -> DiscoveredItem:
    evidence = DiscoveryEvidence(
        method="adapter-observation",
        observed_at=NOW,
        confidence=0.98,
        attributes={"etag": "v1"},
    )
    return DiscoveredItem(
        source_id=SOURCE_ID,
        external_reference="logical:item-001",
        observed_at=NOW,
        observation_method="metadata-listing",
        correlation_id="corr-008d",
        metadata=_metadata(),
        evidence=(evidence,),
        confidence=0.95,
        adapter_version="1.2.0",
        canonical_id=CanonicalId.new() if canonical else None,
        attributes={"name": "Observed item", "technical": {"size": 42}},
    )


def _result(
    request: DiscoveryRequest,
    *,
    status: DiscoveryStatus = DiscoveryStatus.COMPLETED,
) -> DiscoveryResult:
    item = _item()
    warnings = ()
    if status is DiscoveryStatus.COMPLETED_WITH_WARNINGS:
        warnings = (DiscoveryWarning("partial", "Partial metadata"),)
    batch = DiscoveryBatch(
        id=CanonicalId.new(),
        sequence=0,
        items=(item,),
        warnings=warnings,
        final=True,
    )
    return DiscoveryResult(
        request_id=request.id,
        source_id=request.source_id,
        status=status,
        items=(item,),
        warnings=warnings,
        errors=(),
        metrics=DiscoveryMetrics(
            observed_count=1,
            accepted_count=1,
            rejected_count=0,
            warning_count=len(warnings),
            error_count=0,
            started_at=NOW,
            completed_at=NOW,
        ),
        batches=(batch,),
    )


@dataclass(frozen=True, slots=True)
class Source:
    id: DiscoverySourceId = SOURCE_ID
    capabilities: frozenset[DiscoveryCapability] = frozenset(
        {
            DiscoveryCapability.LISTING,
            DiscoveryCapability.METADATA_READ,
            DiscoveryCapability.PAGINATION,
        }
    )


class Provider:
    def __init__(self, result: DiscoveryResult) -> None:
        self.result = result

    def discover(
        self,
        source: DiscoverySource,
        request: DiscoveryRequest,
    ) -> DiscoveryResult:
        assert source.id == request.source_id
        return self.result


class BrokenProvider:
    def discover(
        self,
        source: DiscoverySource,
        request: DiscoveryRequest,
    ) -> DiscoveryResult:
        raise RuntimeError(f"adapter failed for {source.id}:{request.id}")


class Publisher:
    def __init__(self) -> None:
        self.events: list[CanonicalEvent] = []

    def publish(self, event: CanonicalEvent) -> None:
        self.events.append(event)


class FixedClock:
    def now(self) -> datetime:
        return NOW


def test_source_contract_and_all_capabilities_are_declarative() -> None:
    source = Source()

    assert isinstance(source, DiscoverySource)
    assert source.id == SOURCE_ID
    assert {capability.value for capability in DiscoveryCapability} == {
        "listing",
        "metadata_read",
        "content_read",
        "incremental",
        "pagination",
        "checkpoints",
        "cancellation",
        "filtering",
        "continuous_observation",
    }


def test_request_policy_scope_context_and_identity_are_immutable() -> None:
    request = _request()

    assert request.scope.attributes["depth"] == 2
    assert request.context.correlation_id == "corr-008d"
    assert request.policy.page_size == 10
    with pytest.raises(FrozenInstanceError):
        request.scope.reference = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        request.scope.attributes["depth"] = 3  # type: ignore[index]
    with pytest.raises(TypeError):
        _item().metadata.attributes["observed"]["size"] = 0  # type: ignore[index]


@pytest.mark.parametrize(
    "model",
    [
        SOURCE_ID,
        DiscoveryScope("logical:root", {"depth": 1}),
        DiscoveryPolicy(max_items=10, page_size=5),
        _context(),
        _request(),
        DiscoveryEvidence("listing", NOW, 0.9, {"proof": "metadata"}),
        DiscoveryWarning("warning", "message", "logical:item", {"retry": False}),
        DiscoveryErrorRecord("error", "message", True, "logical:item", {"attempt": 1}),
        _item(),
        DiscoveryMetrics(1, 1, 0, 0, 0, NOW, NOW),
        DiscoveryBatch(CanonicalId.new(), 0, (_item(),), final=True),
        _result(_request()),
    ],
)
def test_every_public_model_has_deterministic_versioned_round_trip(model: object) -> None:
    encoded = model.to_json()  # type: ignore[union-attr]
    restored = type(model).from_json(encoded)

    assert restored.to_dict() == model.to_dict()
    assert restored.to_json() == encoded
    assert discovery_model_from_dict(model.to_dict()) == restored


def test_unknown_version_model_field_and_non_object_json_are_rejected() -> None:
    payload = _request().to_dict()
    with pytest.raises(ValueError, match="schema_version"):
        DiscoveryRequest.from_dict({**payload, "schema_version": "2.0"})
    with pytest.raises(ValueError, match="unknown discovery model"):
        discovery_model_from_dict({**payload, "model": "scanner"})
    with pytest.raises(ValueError, match="unknown discovery fields"):
        DiscoveryRequest.from_dict({**payload, "absolute_path": "C:/forbidden"})
    with pytest.raises(ValueError, match="object"):
        DiscoveryRequest.from_json("[]")


def test_model_construction_rejects_invalid_states() -> None:
    with pytest.raises(ValueError, match="whitespace"):
        DiscoverySourceId("invalid source")
    with pytest.raises(ValueError, match="max_items"):
        DiscoveryPolicy(max_items=0)
    with pytest.raises(ValueError, match="confidence"):
        DiscoveryEvidence("method", NOW, 1.1)
    with pytest.raises(ValueError, match="exceed"):
        DiscoveryMetrics(1, 1, 1, 0, 0, NOW)
    with pytest.raises(ValueError, match="duplicates"):
        replace(
            _request(),
            required_capabilities=(
                DiscoveryCapability.LISTING,
                DiscoveryCapability.LISTING,
            ),
        )
    with pytest.raises(ValueError, match="negative"):
        DiscoveryBatch(CanonicalId.new(), -1)


def test_statuses_are_complete_and_tool_independent() -> None:
    assert {status.value for status in DiscoveryStatus} == {
        "pending",
        "running",
        "completed",
        "completed_with_warnings",
        "failed",
        "cancelled",
    }


def test_policy_and_capability_validation() -> None:
    with pytest.raises(ValueError, match="absolute paths"):
        DiscoveryPolicy(include_patterns=("C:/external/*",))
    with pytest.raises(ValueError, match="page_size"):
        validate_policy(DiscoveryPolicy(max_items=5, page_size=10))
    with pytest.raises(UnsupportedDiscoveryCapabilityError, match="content_read"):
        ensure_supported_capabilities(
            (DiscoveryCapability.CONTENT_READ,),
            (DiscoveryCapability.LISTING,),
        )
    ensure_supported_capabilities(
        (DiscoveryCapability.LISTING,),
        (DiscoveryCapability.LISTING,),
    )


def test_validator_accepts_valid_boundaries_and_rejects_mismatches() -> None:
    validator = DefaultDiscoveryValidator()
    source = Source()
    request = _request()
    result = _result(request)

    validator.validate_source(source)
    validator.validate_request(source, request)
    validator.validate_item(request, result.items[0])
    validator.validate_result(request, result)
    with pytest.raises(InvalidDiscoveryRequestError, match="source_id"):
        validator.validate_request(
            source,
            replace(request, source_id=DiscoverySourceId("logical:other")),
        )
    with pytest.raises(InvalidDiscoveredItemError, match="correlation"):
        validator.validate_item(
            request,
            replace(result.items[0], correlation_id="other"),
        )
    with pytest.raises(DiscoveryValidationError, match="accepted_count"):
        validator.validate_result(
            request,
            replace(
                result,
                metrics=replace(result.metrics, accepted_count=0),
            ),
        )


def test_validator_rejects_invalid_source_capability_and_warning_state() -> None:
    validator = DefaultDiscoveryValidator()
    request = _request()

    with pytest.raises(InvalidDiscoverySourceError):
        validator.validate_source(object())  # type: ignore[arg-type]
    with pytest.raises(UnsupportedDiscoveryCapabilityError):
        validator.validate_request(
            Source(capabilities=frozenset({DiscoveryCapability.LISTING})),
            request,
        )
    result = _result(request)
    with pytest.raises(DiscoveryValidationError, match="warning status"):
        validator.validate_result(
            request,
            replace(result, status=DiscoveryStatus.COMPLETED_WITH_WARNINGS),
        )


def test_mapper_creates_asset_without_inventory_or_classification() -> None:
    item = _item()
    asset = DefaultDiscoveryAssetMapper().map_item(item)

    assert isinstance(asset, Asset)
    assert asset.id == item.canonical_id
    assert asset.name == "Observed item"
    assert asset.classifications == ()
    assert asset.attributes["discovery_source_id"] == str(item.source_id)
    with pytest.raises(DiscoveryMappingError, match="canonical_id"):
        DefaultDiscoveryAssetMapper().map_item(_item(canonical=False))


def test_service_orchestrates_provider_validation_mapping_and_events() -> None:
    request = _request()
    result = _result(request)
    publisher = Publisher()
    service = DiscoveryService(
        DefaultDiscoveryValidator(),
        publisher,
        FixedClock(),
        DefaultDiscoveryAssetMapper(),
    )

    returned = service.discover(Source(), Provider(result), request)
    assets = service.map_assets(returned)
    names = [event.name for event in publisher.events]

    assert returned is result
    assert len(assets) == 1
    assert names == [
        DISCOVERY_STARTED,
        DISCOVERY_ITEM_OBSERVED,
        DISCOVERY_BATCH_COMPLETED,
        DISCOVERY_COMPLETED,
    ]
    assert all(event.origin.system == "cko.core.discovery" for event in publisher.events)


def test_service_controls_provider_failure_and_publishes_failed_event() -> None:
    request = _request()
    publisher = Publisher()
    service = DiscoveryService(DefaultDiscoveryValidator(), publisher, FixedClock())

    with pytest.raises(DiscoveryProviderError) as captured:
        service.discover(Source(), BrokenProvider(), request)

    assert isinstance(captured.value.__cause__, RuntimeError)
    assert [event.name for event in publisher.events] == [
        DISCOVERY_STARTED,
        DISCOVERY_FAILED,
    ]
    with pytest.raises(ValueError, match="mapper"):
        service.map_assets(_result(request))


def test_service_uses_cancelled_terminal_event() -> None:
    request = _request()
    result = _result(request, status=DiscoveryStatus.CANCELLED)
    publisher = Publisher()
    service = DiscoveryService(DefaultDiscoveryValidator(), publisher, FixedClock())

    service.discover(Source(), Provider(result), request)

    assert publisher.events[-1].name == DISCOVERY_CANCELLED


def test_event_names_and_factory_are_stable() -> None:
    expected = {
        "discovery.started",
        "discovery.item.observed",
        "discovery.item.rejected",
        "discovery.batch.completed",
        "discovery.completed",
        "discovery.failed",
        "discovery.cancelled",
    }
    event = create_discovery_event(
        DISCOVERY_STARTED,
        NOW,
        SOURCE_ID,
        {"request_id": "request"},
    )

    assert DISCOVERY_EVENT_NAMES == expected
    assert event.name == DISCOVERY_STARTED
    assert event.occurred_at == NOW
    with pytest.raises(ValueError, match="unsupported"):
        create_discovery_event("discovery.scanned", NOW, SOURCE_ID)


def test_public_error_hierarchy_derives_from_cko_error() -> None:
    error_types = (
        DiscoveryError,
        InvalidDiscoveryRequestError,
        InvalidDiscoverySourceError,
        InvalidDiscoveredItemError,
        UnsupportedDiscoveryCapabilityError,
        DiscoveryProviderError,
        DiscoveryMappingError,
        DiscoveryValidationError,
    )
    assert all(issubclass(error_type, CKOError) for error_type in error_types)


def test_discovery_namespace_has_no_forbidden_infrastructure_imports() -> None:
    root = Path(__file__).parents[1] / "src" / "cko" / "core" / "discovery"
    forbidden = {
        "os", "pathlib", "sqlite3", "watchdog", "requests", "urllib",
        "pypdf", "pdfplumber", "openai", "networkx",
    }
    imported: set[str] = set()
    banned_tokens = ("TODO", "NotImplementedError", "absolute_path", "C:\\\\")

    for path in root.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert not any(token in source for token in banned_tokens), path.name

    assert imported.isdisjoint(forbidden)
