"""Versioned models for the canonical in-memory Runtime foundation."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Self

from .errors import InvalidRuntimeModelError


RUNTIME_SCHEMA_VERSION = "1.0"
RUNTIME_VERSION = "1.0.0"


class RuntimeState(str, Enum):
    """Canonical states supported by the synchronous Runtime lifecycle."""

    CREATED = "created"
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidRuntimeModelError(f"{name} must be a non-empty string")
    return value.strip()


def _count(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvalidRuntimeModelError(f"{name} must be non-negative")
    return value


def _duration(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidRuntimeModelError("runtime_duration must be non-negative")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        raise InvalidRuntimeModelError("runtime_duration must be non-negative")
    return normalized


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InvalidRuntimeModelError(f"{name} must be a mapping")
    return value


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidRuntimeModelError("mapping numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen = {_text(key, "mapping key"): _freeze(item) for key, item in value.items()}
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    raise InvalidRuntimeModelError(
        f"unsupported mapping value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {key: _primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_primitive(item) for item in value]
    raise TypeError(f"unsupported Runtime serialization: {type(value).__name__}")


def _state(value: object) -> RuntimeState:
    try:
        return RuntimeState(value)
    except (TypeError, ValueError) as error:
        raise InvalidRuntimeModelError("state must be RuntimeState") from error


def _instant(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidRuntimeModelError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _decode(payload: str) -> Mapping[str, object]:
    try:
        value = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        raise InvalidRuntimeModelError("runtime JSON is invalid") from error
    return _mapping(value, "runtime JSON")


def _json(payload: Mapping[str, object]) -> str:
    return json.dumps(
        payload, allow_nan=False, ensure_ascii=False,
        separators=(",", ":"), sort_keys=True,
    )


@dataclass(slots=True)
class RuntimeContext:
    """Mutable state and immutable snapshots for one Runtime lifecycle."""

    runtime_id: str
    execution_id: str | None = None
    state: RuntimeState = RuntimeState.CREATED
    metadata: Mapping[str, object] = field(default_factory=dict)
    statistics: Mapping[str, object] = field(default_factory=dict)
    resources: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.runtime_id = _text(self.runtime_id, "runtime_id")
        if self.execution_id is not None:
            self.execution_id = _text(self.execution_id, "execution_id")
        self.state = _state(self.state)
        self.metadata = _freeze(_mapping(self.metadata, "metadata"))
        self.statistics = _freeze(_mapping(self.statistics, "statistics"))
        self.resources = _freeze(_mapping(self.resources, "resources"))

    def to_dict(self) -> dict[str, object]:
        """Serialize context to a versioned primitive mapping."""
        return {
            "schema_version": RUNTIME_SCHEMA_VERSION,
            "model": "runtime_context",
            "runtime_id": self.runtime_id,
            "execution_id": self.execution_id,
            "state": self.state.value,
            "metadata": _primitive(self.metadata),
            "statistics": _primitive(self.statistics),
            "resources": _primitive(self.resources),
        }

    def to_json(self) -> str:
        """Serialize context to deterministic UTF-8-compatible JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize context from a strict versioned mapping."""
        data = _mapping(payload, "context")
        expected = {
            "schema_version", "model", "runtime_id", "execution_id", "state",
            "metadata", "statistics", "resources",
        }
        if (
            set(data) != expected
            or data.get("model") != "runtime_context"
            or data.get("schema_version") != RUNTIME_SCHEMA_VERSION
        ):
            raise InvalidRuntimeModelError("invalid RuntimeContext envelope")
        return cls(
            runtime_id=data["runtime_id"],  # type: ignore[arg-type]
            execution_id=data["execution_id"],  # type: ignore[arg-type]
            state=data["state"],  # type: ignore[arg-type]
            metadata=_mapping(data["metadata"], "metadata"),
            statistics=_mapping(data["statistics"], "statistics"),
            resources=_mapping(data["resources"], "resources"),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize context from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class RuntimeMetrics:
    """Immutable aggregate metrics for one Runtime lifecycle."""

    runtime_duration: float = 0.0
    executions: int = 0
    cancelled: int = 0
    failed: int = 0
    completed: int = 0
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "runtime_duration", _duration(self.runtime_duration))
        for name in ("executions", "cancelled", "failed", "completed"):
            object.__setattr__(self, name, _count(getattr(self, name), name))
        if self.cancelled + self.failed + self.completed > self.executions:
            raise InvalidRuntimeModelError("terminal counts exceed executions")
        object.__setattr__(self, "metadata", _freeze(
            _mapping(self.metadata, "metadata")
        ))

    def to_dict(self) -> dict[str, object]:
        """Serialize metrics to primitive values."""
        return {
            "runtime_duration": self.runtime_duration,
            "executions": self.executions,
            "cancelled": self.cancelled,
            "failed": self.failed,
            "completed": self.completed,
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize metrics from a strict primitive mapping."""
        data = _mapping(payload, "metrics")
        expected = {
            "runtime_duration", "executions", "cancelled", "failed",
            "completed", "metadata",
        }
        if set(data) != expected:
            raise InvalidRuntimeModelError("invalid RuntimeMetrics envelope")
        return cls(**data)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class RuntimeSession:
    """Immutable view binding a session to its Runtime context and metrics."""

    session_id: str
    runtime: str
    context: RuntimeContext
    metrics: RuntimeMetrics
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", _text(self.session_id, "session_id"))
        object.__setattr__(self, "runtime", _text(self.runtime, "runtime"))
        if not isinstance(self.context, RuntimeContext):
            raise InvalidRuntimeModelError("context must be RuntimeContext")
        if not isinstance(self.metrics, RuntimeMetrics):
            raise InvalidRuntimeModelError("metrics must be RuntimeMetrics")
        if self.runtime != self.context.runtime_id:
            raise InvalidRuntimeModelError("session Runtime does not match context")
        object.__setattr__(self, "metadata", _freeze(
            _mapping(self.metadata, "metadata")
        ))

    def to_dict(self) -> dict[str, object]:
        """Serialize session to a versioned primitive mapping."""
        return {
            "schema_version": RUNTIME_SCHEMA_VERSION,
            "model": "runtime_session",
            "session_id": self.session_id,
            "runtime": self.runtime,
            "context": self.context.to_dict(),
            "metrics": self.metrics.to_dict(),
            "metadata": _primitive(self.metadata),
        }

    def to_json(self) -> str:
        """Serialize session to deterministic UTF-8-compatible JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize session from a strict versioned mapping."""
        data = _mapping(payload, "session")
        expected = {
            "schema_version", "model", "session_id", "runtime", "context",
            "metrics", "metadata",
        }
        if (
            set(data) != expected
            or data.get("model") != "runtime_session"
            or data.get("schema_version") != RUNTIME_SCHEMA_VERSION
        ):
            raise InvalidRuntimeModelError("invalid RuntimeSession envelope")
        return cls(
            session_id=data["session_id"],  # type: ignore[arg-type]
            runtime=data["runtime"],  # type: ignore[arg-type]
            context=RuntimeContext.from_dict(
                _mapping(data["context"], "context")
            ),
            metrics=RuntimeMetrics.from_dict(
                _mapping(data["metrics"], "metrics")
            ),
            metadata=_mapping(data["metadata"], "metadata"),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize session from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class RuntimeReport:
    """Immutable, timestamped report for a canonical Runtime session."""

    session: RuntimeSession
    state: RuntimeState
    metrics: RuntimeMetrics
    timestamp: datetime
    schema_version: str = RUNTIME_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.session, RuntimeSession):
            raise InvalidRuntimeModelError("session must be RuntimeSession")
        object.__setattr__(self, "state", _state(self.state))
        if not isinstance(self.metrics, RuntimeMetrics):
            raise InvalidRuntimeModelError("metrics must be RuntimeMetrics")
        if self.state is not self.session.context.state:
            raise InvalidRuntimeModelError("report state does not match session")
        if self.metrics != self.session.metrics:
            raise InvalidRuntimeModelError("report metrics do not match session")
        object.__setattr__(self, "timestamp", _instant(self.timestamp))
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise InvalidRuntimeModelError("unsupported Runtime schema version")

    def to_dict(self) -> dict[str, object]:
        """Serialize report to a strict, versioned primitive mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "runtime_report",
            "session": self.session.to_dict(),
            "state": self.state.value,
            "metrics": self.metrics.to_dict(),
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Serialize report to deterministic UTF-8-compatible JSON."""
        return _json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a report from a strict versioned mapping."""
        data = _mapping(payload, "report")
        expected = {
            "schema_version", "model", "session", "state", "metrics",
            "timestamp",
        }
        if set(data) != expected or data.get("model") != "runtime_report":
            raise InvalidRuntimeModelError("invalid RuntimeReport envelope")
        timestamp = data["timestamp"]
        if not isinstance(timestamp, str):
            raise InvalidRuntimeModelError("timestamp must be an ISO string")
        try:
            instant = datetime.fromisoformat(timestamp)
        except ValueError as error:
            raise InvalidRuntimeModelError("timestamp must be an ISO string") from error
        return cls(
            session=RuntimeSession.from_dict(
                _mapping(data["session"], "session")
            ),
            state=data["state"],  # type: ignore[arg-type]
            metrics=RuntimeMetrics.from_dict(
                _mapping(data["metrics"], "metrics")
            ),
            timestamp=instant,
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize a Runtime report from strict JSON."""
        return cls.from_dict(_decode(payload))


__all__ = [
    "RUNTIME_SCHEMA_VERSION", "RUNTIME_VERSION", "RuntimeContext",
    "RuntimeMetrics", "RuntimeReport", "RuntimeSession", "RuntimeState",
]
