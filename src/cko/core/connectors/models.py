"""Immutable and versioned models for canonical connector contracts."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Self

from cko.core.logging import get_logger

from .errors import ConnectorException


CONNECTOR_SCHEMA_VERSION = "1.0"
CONNECTOR_VERSION = "1.0.0"
_LOGGER = get_logger("core.connectors.session")


class ConnectorSessionState(str, Enum):
    """Canonical states of an immutable connector session."""

    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConnectorException(
            f"{name} must be a non-empty string",
            code="invalid_model",
        )
    return value.strip()


def _optional_text(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _text(value, name)


def _string_tuple(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list, frozenset, set)):
        raise ConnectorException(f"{name} must be a collection of strings")
    normalized = tuple(sorted({_text(item, name) for item in value}))
    return normalized


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ConnectorException(f"{name} must be a mapping")
    return value


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ConnectorException("mapping numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen = {_text(key, "mapping key"): _freeze(item)
                  for key, item in value.items()}
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    raise ConnectorException(
        f"unsupported serializable value: {type(value).__name__}"
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
    raise ConnectorException(
        f"unsupported connector serialization: {type(value).__name__}"
    )


def _instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ConnectorException(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _json(payload: Mapping[str, object]) -> str:
    return json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _decode(payload: str) -> Mapping[str, object]:
    try:
        decoded = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        raise ConnectorException("connector JSON is invalid") from error
    return _mapping(decoded, "connector JSON")


def _envelope(
    payload: Mapping[str, object], model: str, fields: set[str]
) -> Mapping[str, object]:
    data = _mapping(payload, model)
    expected = fields | {"schema_version", "model"}
    if (
        set(data) != expected
        or data.get("schema_version") != CONNECTOR_SCHEMA_VERSION
        or data.get("model") != model
    ):
        raise ConnectorException(f"invalid {model} envelope")
    return data


class _SerializableModel:
    """Shared deterministic JSON behavior for connector value objects."""

    def to_dict(self) -> dict[str, object]:
        raise NotImplementedError

    def to_json(self) -> str:
        """Serialize this model to deterministic UTF-8-compatible JSON."""
        return _json(self.to_dict())


@dataclass(frozen=True, slots=True)
class ConnectorMetadata(_SerializableModel):
    """Human-readable, technology-neutral connector metadata."""

    name: str
    description: str
    version: str
    labels: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = CONNECTOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _text(self.name, "name"))
        object.__setattr__(
            self, "description", _text(self.description, "description")
        )
        object.__setattr__(self, "version", _text(self.version, "version"))
        object.__setattr__(
            self, "labels", _freeze(_mapping(self.labels, "labels"))
        )
        if self.schema_version != CONNECTOR_SCHEMA_VERSION:
            raise ConnectorException("unsupported ConnectorMetadata version")

    def to_dict(self) -> dict[str, object]:
        """Serialize metadata to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "connector_metadata",
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "labels": _primitive(self.labels),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize metadata from a strict versioned mapping."""
        data = _envelope(
            payload,
            "connector_metadata",
            {"name", "description", "version", "labels"},
        )
        return cls(
            name=data["name"],
            description=data["description"],
            version=data["version"],
            labels=_mapping(data["labels"], "labels"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize metadata from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class ConnectorCapabilities(_SerializableModel):
    """Operations and optional features declared by a connector."""

    operations: tuple[str, ...]
    features: tuple[str, ...] = ()
    supports_streaming: bool = False
    schema_version: str = CONNECTOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        operations = _string_tuple(self.operations, "operations")
        if not operations:
            raise ConnectorException("operations must not be empty")
        object.__setattr__(self, "operations", operations)
        object.__setattr__(
            self, "features", _string_tuple(self.features, "features")
        )
        if not isinstance(self.supports_streaming, bool):
            raise ConnectorException("supports_streaming must be boolean")
        if self.schema_version != CONNECTOR_SCHEMA_VERSION:
            raise ConnectorException("unsupported ConnectorCapabilities version")

    def supports(self, operation: str) -> bool:
        """Return whether an operation is explicitly declared."""
        return _text(operation, "operation") in self.operations

    def to_dict(self) -> dict[str, object]:
        """Serialize capabilities to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "connector_capabilities",
            "operations": list(self.operations),
            "features": list(self.features),
            "supports_streaming": self.supports_streaming,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize capabilities from a strict versioned mapping."""
        data = _envelope(
            payload,
            "connector_capabilities",
            {"operations", "features", "supports_streaming"},
        )
        return cls(
            operations=data["operations"],
            features=data["features"],
            supports_streaming=data["supports_streaming"],
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize capabilities from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class ConnectorDescriptor(_SerializableModel):
    """Stable identity and public contract of one connector registration."""

    identifier: str
    metadata: ConnectorMetadata
    capabilities: ConnectorCapabilities
    contract_version: str = CONNECTOR_VERSION
    schema_version: str = CONNECTOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", _text(self.identifier, "identifier")
        )
        if not isinstance(self.metadata, ConnectorMetadata):
            raise ConnectorException("metadata must be ConnectorMetadata")
        if not isinstance(self.capabilities, ConnectorCapabilities):
            raise ConnectorException(
                "capabilities must be ConnectorCapabilities"
            )
        object.__setattr__(
            self,
            "contract_version",
            _text(self.contract_version, "contract_version"),
        )
        if self.schema_version != CONNECTOR_SCHEMA_VERSION:
            raise ConnectorException("unsupported ConnectorDescriptor version")

    def to_dict(self) -> dict[str, object]:
        """Serialize the descriptor to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "connector_descriptor",
            "identifier": self.identifier,
            "metadata": self.metadata.to_dict(),
            "capabilities": self.capabilities.to_dict(),
            "contract_version": self.contract_version,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a descriptor from a strict versioned mapping."""
        data = _envelope(
            payload,
            "connector_descriptor",
            {"identifier", "metadata", "capabilities", "contract_version"},
        )
        return cls(
            identifier=data["identifier"],
            metadata=ConnectorMetadata.from_dict(
                _mapping(data["metadata"], "metadata")
            ),
            capabilities=ConnectorCapabilities.from_dict(
                _mapping(data["capabilities"], "capabilities")
            ),
            contract_version=data["contract_version"],
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize a descriptor from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class ConnectorContext(_SerializableModel):
    """Immutable logical input supplied when a connector is invoked."""

    correlation_id: str
    operation: str
    parameters: Mapping[str, object] = field(default_factory=dict)
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = CONNECTOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "correlation_id", _text(self.correlation_id, "correlation_id")
        )
        object.__setattr__(self, "operation", _text(self.operation, "operation"))
        object.__setattr__(
            self,
            "parameters",
            _freeze(_mapping(self.parameters, "parameters")),
        )
        object.__setattr__(
            self, "metadata", _freeze(_mapping(self.metadata, "metadata"))
        )
        if self.schema_version != CONNECTOR_SCHEMA_VERSION:
            raise ConnectorException("unsupported ConnectorContext version")

    def to_dict(self) -> dict[str, object]:
        """Serialize context to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "connector_context",
            "correlation_id": self.correlation_id,
            "operation": self.operation,
            "parameters": _primitive(self.parameters),
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize context from a strict versioned mapping."""
        data = _envelope(
            payload,
            "connector_context",
            {"correlation_id", "operation", "parameters", "metadata"},
        )
        return cls(
            correlation_id=data["correlation_id"],
            operation=data["operation"],
            parameters=_mapping(data["parameters"], "parameters"),
            metadata=_mapping(data["metadata"], "metadata"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize context from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class ConnectorSession(_SerializableModel):
    """Immutable lifecycle snapshot for one connector invocation."""

    session_id: str
    connector_id: str
    context: ConnectorContext
    state: ConnectorSessionState
    started_at: datetime
    finished_at: datetime | None = None
    failure: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = CONNECTOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", _text(self.session_id, "session_id"))
        object.__setattr__(
            self, "connector_id", _text(self.connector_id, "connector_id")
        )
        if not isinstance(self.context, ConnectorContext):
            raise ConnectorException("context must be ConnectorContext")
        try:
            object.__setattr__(self, "state", ConnectorSessionState(self.state))
        except (TypeError, ValueError) as error:
            raise ConnectorException("state must be ConnectorSessionState") from error
        object.__setattr__(
            self, "started_at", _instant(self.started_at, "started_at")
        )
        if self.finished_at is not None:
            finished = _instant(self.finished_at, "finished_at")
            if finished < self.started_at:
                raise ConnectorException("finished_at cannot precede started_at")
            object.__setattr__(self, "finished_at", finished)
        object.__setattr__(self, "failure", _optional_text(self.failure, "failure"))
        object.__setattr__(
            self, "metadata", _freeze(_mapping(self.metadata, "metadata"))
        )
        if self.state is ConnectorSessionState.STARTED:
            if self.finished_at is not None or self.failure is not None:
                raise ConnectorException("started session cannot be terminal")
        elif self.finished_at is None:
            raise ConnectorException("terminal session requires finished_at")
        if self.state is ConnectorSessionState.FAILED and self.failure is None:
            raise ConnectorException("failed session requires failure")
        if self.state is ConnectorSessionState.FINISHED and self.failure is not None:
            raise ConnectorException("finished session cannot contain failure")
        if self.schema_version != CONNECTOR_SCHEMA_VERSION:
            raise ConnectorException("unsupported ConnectorSession version")

    @classmethod
    def start(
        cls,
        session_id: str,
        connector_id: str,
        context: ConnectorContext,
        started_at: datetime,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> Self:
        """Create and log a started immutable connector session."""
        session = cls(
            session_id=session_id,
            connector_id=connector_id,
            context=context,
            state=ConnectorSessionState.STARTED,
            started_at=started_at,
            metadata={} if metadata is None else metadata,
        )
        _LOGGER.info(
            "connector_session_started",
            extra={
                "event": "connector_session_started",
                "context": {
                    "connector_id": session.connector_id,
                    "session_id": session.session_id,
                },
            },
        )
        return session

    def finish(
        self,
        finished_at: datetime,
        *,
        failure: str | None = None,
    ) -> Self:
        """Return and log the terminal snapshot of a started session."""
        if self.state is not ConnectorSessionState.STARTED:
            raise ConnectorException("only a started session can be finished")
        state = (
            ConnectorSessionState.FINISHED
            if failure is None
            else ConnectorSessionState.FAILED
        )
        session = replace(
            self,
            state=state,
            finished_at=finished_at,
            failure=failure,
        )
        _LOGGER.info(
            "connector_session_finished",
            extra={
                "event": "connector_session_finished",
                "context": {
                    "connector_id": session.connector_id,
                    "session_id": session.session_id,
                    "state": session.state.value,
                },
            },
        )
        return session

    def to_dict(self) -> dict[str, object]:
        """Serialize session to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "connector_session",
            "session_id": self.session_id,
            "connector_id": self.connector_id,
            "context": self.context.to_dict(),
            "state": self.state.value,
            "started_at": self.started_at.isoformat(),
            "finished_at": (
                None if self.finished_at is None else self.finished_at.isoformat()
            ),
            "failure": self.failure,
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize session from a strict versioned mapping."""
        data = _envelope(
            payload,
            "connector_session",
            {
                "session_id", "connector_id", "context", "state",
                "started_at", "finished_at", "failure", "metadata",
            },
        )
        started_at = _parse_instant(data["started_at"], "started_at")
        finished_value = data["finished_at"]
        finished_at = (
            None
            if finished_value is None
            else _parse_instant(finished_value, "finished_at")
        )
        return cls(
            session_id=data["session_id"],
            connector_id=data["connector_id"],
            context=ConnectorContext.from_dict(
                _mapping(data["context"], "context")
            ),
            state=data["state"],
            started_at=started_at,
            finished_at=finished_at,
            failure=data["failure"],
            metadata=_mapping(data["metadata"], "metadata"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize session from strict JSON."""
        return cls.from_dict(_decode(payload))


def _parse_instant(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise ConnectorException(f"{name} must be an ISO string")
    try:
        return _instant(datetime.fromisoformat(value), name)
    except ValueError as error:
        raise ConnectorException(f"{name} must be an ISO string") from error


@dataclass(frozen=True, slots=True)
class ConnectorResult(_SerializableModel):
    """Immutable logical result produced by a connector invocation."""

    session_id: str
    connector_id: str
    success: bool
    data: Mapping[str, object] = field(default_factory=dict)
    errors: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = CONNECTOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", _text(self.session_id, "session_id"))
        object.__setattr__(
            self, "connector_id", _text(self.connector_id, "connector_id")
        )
        if not isinstance(self.success, bool):
            raise ConnectorException("success must be boolean")
        object.__setattr__(self, "data", _freeze(_mapping(self.data, "data")))
        object.__setattr__(self, "errors", _string_tuple(self.errors, "errors"))
        object.__setattr__(
            self, "metadata", _freeze(_mapping(self.metadata, "metadata"))
        )
        if self.success and self.errors:
            raise ConnectorException("successful result cannot contain errors")
        if not self.success and not self.errors:
            raise ConnectorException("failed result requires errors")
        if self.schema_version != CONNECTOR_SCHEMA_VERSION:
            raise ConnectorException("unsupported ConnectorResult version")

    def to_dict(self) -> dict[str, object]:
        """Serialize result to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "connector_result",
            "session_id": self.session_id,
            "connector_id": self.connector_id,
            "success": self.success,
            "data": _primitive(self.data),
            "errors": list(self.errors),
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize result from a strict versioned mapping."""
        data = _envelope(
            payload,
            "connector_result",
            {
                "session_id", "connector_id", "success", "data", "errors",
                "metadata",
            },
        )
        return cls(
            session_id=data["session_id"],
            connector_id=data["connector_id"],
            success=data["success"],
            data=_mapping(data["data"], "data"),
            errors=data["errors"],
            metadata=_mapping(data["metadata"], "metadata"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize result from strict JSON."""
        return cls.from_dict(_decode(payload))


__all__ = [
    "CONNECTOR_SCHEMA_VERSION",
    "CONNECTOR_VERSION",
    "ConnectorCapabilities",
    "ConnectorContext",
    "ConnectorDescriptor",
    "ConnectorMetadata",
    "ConnectorResult",
    "ConnectorSession",
    "ConnectorSessionState",
]
