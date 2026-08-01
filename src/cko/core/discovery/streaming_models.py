"""Canonical immutable models for incremental Discovery processing."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Self

from cko.core.identity import CanonicalId
from cko.core.utils import ensure_aware, require_non_empty

from .streaming_errors import (
    InvalidBatchAcknowledgementError,
    InvalidBatchCursorError,
)


BATCH_CURSOR_SCHEMA_VERSION = "1.0"


class DiscoveryStreamState(str, Enum):
    """Canonical lifecycle states of a Discovery stream."""

    CREATED = "created"
    OPEN = "open"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConsumerUnavailableBehavior(str, Enum):
    """Neutral behavior when a consumer cannot process a batch."""

    FAIL = "fail"
    REJECT = "reject"
    CANCEL = "cancel"


class BatchAcknowledgementStatus(str, Enum):
    """Canonical outcomes reported by a batch consumer."""

    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    PARTIAL = "partial"
    FAILED = "failed"


def _is_location(value: str) -> bool:
    """Return whether text represents an absolute infrastructure location."""
    normalized = value.replace("\\", "/")
    return (
        normalized.startswith("/")
        or normalized.startswith("//")
        or (len(normalized) >= 3 and normalized[1:3] == ":/")
    )


def _freeze_logical(value: object) -> object:
    """Validate and freeze JSON-compatible, infrastructure-neutral state."""
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidBatchCursorError(
                "cursor state numbers must be finite"
            )
        return value
    if isinstance(value, str):
        if _is_location(value):
            raise InvalidBatchCursorError(
                "cursor state cannot contain an absolute location"
            )
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested in value.items():
            if not isinstance(key, str) or not key.strip():
                raise InvalidBatchCursorError(
                    "cursor state keys must be non-empty strings"
                )
            normalized = key.casefold().replace("_", "")
            if normalized in {"path", "filepath", "filesystem", "database"}:
                raise InvalidBatchCursorError(
                    "cursor state cannot declare infrastructure locations"
                )
            frozen[key] = _freeze_logical(nested)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_logical(item) for item in value)
    raise InvalidBatchCursorError(
        f"unsupported cursor state value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    """Convert frozen logical state into deterministic JSON primitives."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, tuple):
        return [_primitive(item) for item in value]
    raise InvalidBatchCursorError(
        f"cursor state cannot serialize {type(value).__name__}"
    )


@dataclass(frozen=True, slots=True)
class BatchCursor:
    """Versioned immutable cursor carrying only validated logical state."""

    request_id: CanonicalId
    session_id: CanonicalId
    next_sequence: int
    state: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = BATCH_CURSOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """Validate cursor identity, version, sequence and opaque state."""
        if not isinstance(self.request_id, CanonicalId):
            raise InvalidBatchCursorError("request_id must be CanonicalId")
        if not isinstance(self.session_id, CanonicalId):
            raise InvalidBatchCursorError("session_id must be CanonicalId")
        if self.schema_version != BATCH_CURSOR_SCHEMA_VERSION:
            raise InvalidBatchCursorError("unsupported batch cursor schema_version")
        if isinstance(self.next_sequence, bool) or self.next_sequence < 0:
            raise InvalidBatchCursorError("next_sequence cannot be negative")
        frozen = _freeze_logical(self.state)
        if not isinstance(frozen, Mapping):
            raise InvalidBatchCursorError("cursor state must be an object")
        object.__setattr__(self, "state", frozen)

    def to_dict(self) -> dict[str, object]:
        """Return the strict public cursor envelope."""
        return {
            "schema_version": self.schema_version,
            "request_id": str(self.request_id),
            "session_id": str(self.session_id),
            "next_sequence": self.next_sequence,
            "state": _primitive(self.state),
        }

    def to_json(self) -> str:
        """Serialize the cursor as deterministic UTF-8 JSON text."""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Reconstruct a cursor while rejecting unknown or missing fields."""
        expected = {
            "schema_version",
            "request_id",
            "session_id",
            "next_sequence",
            "state",
        }
        unknown = set(payload) - expected
        missing = expected - set(payload)
        if unknown:
            raise InvalidBatchCursorError(
                f"unknown batch cursor fields: {sorted(unknown)}"
            )
        if missing:
            raise InvalidBatchCursorError(
                f"missing batch cursor fields: {sorted(missing)}"
            )
        try:
            request_id = CanonicalId.parse(str(payload["request_id"]))
            session_id = CanonicalId.parse(str(payload["session_id"]))
        except (TypeError, ValueError) as error:
            raise InvalidBatchCursorError("cursor identity is invalid") from error
        sequence = payload["next_sequence"]
        if not isinstance(sequence, int):
            raise InvalidBatchCursorError("next_sequence must be an integer")
        state = payload["state"]
        if not isinstance(state, Mapping):
            raise InvalidBatchCursorError("cursor state must be an object")
        version = payload["schema_version"]
        if not isinstance(version, str):
            raise InvalidBatchCursorError("schema_version must be a string")
        return cls(request_id, session_id, sequence, state, version)

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Reconstruct a cursor from a strict JSON object."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise InvalidBatchCursorError("batch cursor JSON is invalid") from error
        if not isinstance(decoded, dict):
            raise InvalidBatchCursorError("batch cursor JSON must contain an object")
        return cls.from_dict(decoded)


@dataclass(frozen=True, slots=True)
class BackpressurePolicy:
    """Neutral declared limits enforced without concurrency primitives."""

    max_pending_batches: int = 1
    max_items_per_batch: int | None = None
    memory_limit_bytes: int | None = None
    consumer_unavailable: ConsumerUnavailableBehavior = (
        ConsumerUnavailableBehavior.FAIL
    )
    timeout_seconds: float | None = None

    def __post_init__(self) -> None:
        """Reject non-positive limits and normalize unavailable behavior."""
        for name in (
            "max_pending_batches",
            "max_items_per_batch",
            "memory_limit_bytes",
        ):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value <= 0
            ):
                raise ValueError(f"{name} must be greater than zero")
        if self.timeout_seconds is not None and (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not math.isfinite(self.timeout_seconds)
            or self.timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be greater than zero")
        object.__setattr__(
            self,
            "consumer_unavailable",
            ConsumerUnavailableBehavior(self.consumer_unavailable),
        )


@dataclass(frozen=True, slots=True)
class BatchAcknowledgement:
    """Immutable logical acknowledgement returned by a batch consumer."""

    batch_id: CanonicalId
    session_id: CanonicalId
    status: BatchAcknowledgementStatus
    processed_items: int
    rejected_items: int
    timestamp: datetime
    reason: str | None = None
    metrics: Mapping[str, int | float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate identities, counts, status semantics and metric values."""
        if not isinstance(self.batch_id, CanonicalId):
            raise InvalidBatchAcknowledgementError(
                "batch_id must be CanonicalId"
            )
        if not isinstance(self.session_id, CanonicalId):
            raise InvalidBatchAcknowledgementError(
                "session_id must be CanonicalId"
            )
        try:
            status = BatchAcknowledgementStatus(self.status)
        except ValueError as error:
            raise InvalidBatchAcknowledgementError(
                "acknowledgement status is invalid"
            ) from error
        object.__setattr__(self, "status", status)
        for name in ("processed_items", "rejected_items"):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
            ):
                raise InvalidBatchAcknowledgementError(
                    f"{name} must be a non-negative integer"
                )
        try:
            timestamp = ensure_aware(self.timestamp)
        except (TypeError, ValueError) as error:
            raise InvalidBatchAcknowledgementError(
                "acknowledgement timestamp is invalid"
            ) from error
        object.__setattr__(self, "timestamp", timestamp)
        if self.reason is not None:
            try:
                reason = require_non_empty(self.reason, "reason")
            except (TypeError, ValueError) as error:
                raise InvalidBatchAcknowledgementError(
                    "acknowledgement reason is invalid"
                ) from error
            object.__setattr__(self, "reason", reason)
        if self.status is BatchAcknowledgementStatus.CONFIRMED:
            if self.rejected_items or self.reason is not None:
                raise InvalidBatchAcknowledgementError(
                    "confirmed acknowledgement cannot reject items or have a reason"
                )
        elif self.reason is None:
            raise InvalidBatchAcknowledgementError(
                "non-confirmed acknowledgement requires a reason"
            )
        if self.status is BatchAcknowledgementStatus.REJECTED:
            if self.processed_items:
                raise InvalidBatchAcknowledgementError(
                    "rejected acknowledgement cannot process items"
                )
        if self.status is BatchAcknowledgementStatus.PARTIAL:
            if not self.processed_items or not self.rejected_items:
                raise InvalidBatchAcknowledgementError(
                    "partial acknowledgement requires processed and rejected items"
                )
        if not isinstance(self.metrics, Mapping):
            raise InvalidBatchAcknowledgementError(
                "acknowledgement metrics must be an object"
            )
        normalized_metrics: dict[str, int | float] = {}
        for key, value in self.metrics.items():
            if not isinstance(key, str) or not key.strip():
                raise InvalidBatchAcknowledgementError(
                    "metric names must be non-empty strings"
                )
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise InvalidBatchAcknowledgementError(
                    "acknowledgement metrics must be numeric"
                )
            normalized_metrics[key] = value
        object.__setattr__(self, "metrics", MappingProxyType(normalized_metrics))


@dataclass(frozen=True, slots=True)
class StreamMetrics:
    """Immutable metric snapshot for a streaming execution."""

    batches_produced: int = 0
    batches_consumed: int = 0
    batches_rejected: int = 0
    items_produced: int = 0
    items_consumed: int = 0
    items_rejected: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    terminal_state: DiscoveryStreamState | None = None

    def __post_init__(self) -> None:
        """Validate counters, timestamps and terminal-state consistency."""
        for name in (
            "batches_produced",
            "batches_consumed",
            "batches_rejected",
            "items_produced",
            "items_consumed",
            "items_rejected",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.started_at is not None:
            object.__setattr__(self, "started_at", ensure_aware(self.started_at))
        if self.completed_at is not None:
            completed = ensure_aware(self.completed_at)
            if self.started_at is None or completed < self.started_at:
                raise ValueError("completed_at requires a valid started_at")
            object.__setattr__(self, "completed_at", completed)
        if self.terminal_state is not None:
            terminal = DiscoveryStreamState(self.terminal_state)
            if terminal not in {
                DiscoveryStreamState.COMPLETED,
                DiscoveryStreamState.FAILED,
                DiscoveryStreamState.CANCELLED,
            }:
                raise ValueError("terminal_state must be terminal")
            object.__setattr__(self, "terminal_state", terminal)

    @property
    def duration_seconds(self) -> float | None:
        """Return elapsed seconds when both timestamps are available."""
        if self.started_at is None or self.completed_at is None:
            return None
        return (self.completed_at - self.started_at).total_seconds()


__all__ = [
    "BATCH_CURSOR_SCHEMA_VERSION",
    "BackpressurePolicy",
    "BatchAcknowledgement",
    "BatchAcknowledgementStatus",
    "BatchCursor",
    "ConsumerUnavailableBehavior",
    "DiscoveryStreamState",
    "StreamMetrics",
]
