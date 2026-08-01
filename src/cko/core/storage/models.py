"""Immutable and versioned models for canonical storage contracts."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from cko.core.logging import get_logger

from .errors import StorageException


STORAGE_SCHEMA_VERSION = "1.0"
STORAGE_VERSION = "1.0.0"
_LOGGER = get_logger("core.storage.session")


class StorageOperation(str, Enum):
    """Technology-neutral operations that a storage provider may support."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"
    EXISTS = "exists"
    METADATA = "metadata"


class StorageSessionState(str, Enum):
    """Canonical states of an immutable storage session."""

    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StorageException(f"{name} must be a non-empty string")
    return value.strip()


def _optional_text(value: object, name: str) -> str | None:
    return None if value is None else _text(value, name)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise StorageException(f"{name} must be a mapping")
    return value


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise StorageException("mapping numbers must be finite")
        return value
    if isinstance(value, Mapping):
        normalized = {
            _text(key, "mapping key"): _freeze(item)
            for key, item in value.items()
        }
        return MappingProxyType(dict(sorted(normalized.items())))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    raise StorageException(
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
    raise StorageException(
        f"unsupported storage serialization: {type(value).__name__}"
    )


def _instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise StorageException(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _parse_instant(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise StorageException(f"{name} must be an ISO string")
    try:
        return _instant(datetime.fromisoformat(value), name)
    except ValueError as error:
        raise StorageException(f"{name} must be an ISO string") from error


def _decode(payload: str) -> Mapping[str, object]:
    try:
        decoded = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        raise StorageException("storage JSON is invalid") from error
    return _mapping(decoded, "storage JSON")


def _envelope(
    payload: Mapping[str, object], model: str, fields: set[str]
) -> Mapping[str, object]:
    data = _mapping(payload, model)
    if (
        set(data) != fields | {"schema_version", "model"}
        or data.get("schema_version") != STORAGE_SCHEMA_VERSION
        or data.get("model") != model
    ):
        raise StorageException(f"invalid {model} envelope")
    return data


class _SerializableModel:
    """Shared deterministic JSON behavior for storage value objects."""

    model_name: ClassVar[str]

    def to_dict(self) -> dict[str, object]:
        """Serialize the model to a strict versioned mapping."""
        raise NotImplementedError

    def to_json(self) -> str:
        """Serialize the model to deterministic UTF-8-compatible JSON."""
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )


@dataclass(frozen=True, slots=True)
class StorageMetadata(_SerializableModel):
    """Human-readable, technology-neutral storage metadata."""

    name: str
    description: str
    version: str
    labels: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = STORAGE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _text(self.name, "name"))
        object.__setattr__(
            self, "description", _text(self.description, "description")
        )
        object.__setattr__(self, "version", _text(self.version, "version"))
        object.__setattr__(
            self, "labels", _freeze(_mapping(self.labels, "labels"))
        )
        if self.schema_version != STORAGE_SCHEMA_VERSION:
            raise StorageException("unsupported StorageMetadata version")

    def to_dict(self) -> dict[str, object]:
        """Serialize metadata to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "storage_metadata",
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
            "storage_metadata",
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
class StorageCapabilities(_SerializableModel):
    """Operations and neutral behavioral features declared by storage."""

    operations: tuple[StorageOperation, ...]
    supports_transactions: bool = False
    supports_atomic_write: bool = False
    supports_streaming: bool = False
    schema_version: str = STORAGE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.operations, (tuple, list, set, frozenset)):
            raise StorageException("operations must be a collection")
        try:
            operations = tuple(
                sorted(
                    {StorageOperation(item) for item in self.operations},
                    key=lambda item: item.value,
                )
            )
        except (TypeError, ValueError) as error:
            raise StorageException("operations contain an invalid value") from error
        if not operations:
            raise StorageException("operations must not be empty")
        object.__setattr__(self, "operations", operations)
        flags = (
            self.supports_transactions,
            self.supports_atomic_write,
            self.supports_streaming,
        )
        if any(not isinstance(flag, bool) for flag in flags):
            raise StorageException("capability flags must be boolean")
        if self.schema_version != STORAGE_SCHEMA_VERSION:
            raise StorageException("unsupported StorageCapabilities version")

    def supports(self, operation: StorageOperation | str) -> bool:
        """Return whether an operation is explicitly declared."""
        try:
            normalized = StorageOperation(operation)
        except (TypeError, ValueError) as error:
            raise StorageException("operation is invalid") from error
        return normalized in self.operations

    def to_dict(self) -> dict[str, object]:
        """Serialize capabilities to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "storage_capabilities",
            "operations": [item.value for item in self.operations],
            "supports_transactions": self.supports_transactions,
            "supports_atomic_write": self.supports_atomic_write,
            "supports_streaming": self.supports_streaming,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize capabilities from a strict versioned mapping."""
        data = _envelope(
            payload,
            "storage_capabilities",
            {
                "operations", "supports_transactions",
                "supports_atomic_write", "supports_streaming",
            },
        )
        return cls(
            operations=data["operations"],
            supports_transactions=data["supports_transactions"],
            supports_atomic_write=data["supports_atomic_write"],
            supports_streaming=data["supports_streaming"],
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize capabilities from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class StorageDescriptor(_SerializableModel):
    """Stable identity and public contract of a storage registration."""

    identifier: str
    metadata: StorageMetadata
    capabilities: StorageCapabilities
    contract_version: str = STORAGE_VERSION
    schema_version: str = STORAGE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", _text(self.identifier, "identifier")
        )
        if not isinstance(self.metadata, StorageMetadata):
            raise StorageException("metadata must be StorageMetadata")
        if not isinstance(self.capabilities, StorageCapabilities):
            raise StorageException("capabilities must be StorageCapabilities")
        object.__setattr__(
            self,
            "contract_version",
            _text(self.contract_version, "contract_version"),
        )
        if self.schema_version != STORAGE_SCHEMA_VERSION:
            raise StorageException("unsupported StorageDescriptor version")

    def to_dict(self) -> dict[str, object]:
        """Serialize descriptor to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "storage_descriptor",
            "identifier": self.identifier,
            "metadata": self.metadata.to_dict(),
            "capabilities": self.capabilities.to_dict(),
            "contract_version": self.contract_version,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize descriptor from a strict versioned mapping."""
        data = _envelope(
            payload,
            "storage_descriptor",
            {"identifier", "metadata", "capabilities", "contract_version"},
        )
        return cls(
            identifier=data["identifier"],
            metadata=StorageMetadata.from_dict(
                _mapping(data["metadata"], "metadata")
            ),
            capabilities=StorageCapabilities.from_dict(
                _mapping(data["capabilities"], "capabilities")
            ),
            contract_version=data["contract_version"],
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize descriptor from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class StorageLocation(_SerializableModel):
    """Logical location independent of paths, URLs, buckets, or databases."""

    namespace: str
    key: str
    attributes: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = STORAGE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "namespace", _text(self.namespace, "namespace")
        )
        object.__setattr__(self, "key", _text(self.key, "key"))
        object.__setattr__(
            self,
            "attributes",
            _freeze(_mapping(self.attributes, "attributes")),
        )
        if self.schema_version != STORAGE_SCHEMA_VERSION:
            raise StorageException("unsupported StorageLocation version")

    def to_dict(self) -> dict[str, object]:
        """Serialize location to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "storage_location",
            "namespace": self.namespace,
            "key": self.key,
            "attributes": _primitive(self.attributes),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize location from a strict versioned mapping."""
        data = _envelope(
            payload, "storage_location", {"namespace", "key", "attributes"}
        )
        return cls(
            namespace=data["namespace"],
            key=data["key"],
            attributes=_mapping(data["attributes"], "attributes"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize location from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class StorageObject(_SerializableModel):
    """Logical object descriptor without stored content or implementation data."""

    object_id: str
    location: StorageLocation
    size: int | None = None
    digest: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = STORAGE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "object_id", _text(self.object_id, "object_id"))
        if not isinstance(self.location, StorageLocation):
            raise StorageException("location must be StorageLocation")
        if self.size is not None:
            if isinstance(self.size, bool) or not isinstance(self.size, int):
                raise StorageException("size must be an integer when provided")
            if self.size < 0:
                raise StorageException("size cannot be negative")
        object.__setattr__(self, "digest", _optional_text(self.digest, "digest"))
        object.__setattr__(
            self, "metadata", _freeze(_mapping(self.metadata, "metadata"))
        )
        if self.schema_version != STORAGE_SCHEMA_VERSION:
            raise StorageException("unsupported StorageObject version")

    def to_dict(self) -> dict[str, object]:
        """Serialize object descriptor to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "storage_object",
            "object_id": self.object_id,
            "location": self.location.to_dict(),
            "size": self.size,
            "digest": self.digest,
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize object descriptor from a strict mapping."""
        data = _envelope(
            payload,
            "storage_object",
            {"object_id", "location", "size", "digest", "metadata"},
        )
        return cls(
            object_id=data["object_id"],
            location=StorageLocation.from_dict(
                _mapping(data["location"], "location")
            ),
            size=data["size"],
            digest=data["digest"],
            metadata=_mapping(data["metadata"], "metadata"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize object descriptor from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class StorageContext(_SerializableModel):
    """Immutable logical input supplied for one storage operation."""

    correlation_id: str
    operation: StorageOperation
    location: StorageLocation
    parameters: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = STORAGE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "correlation_id", _text(self.correlation_id, "correlation_id")
        )
        try:
            object.__setattr__(self, "operation", StorageOperation(self.operation))
        except (TypeError, ValueError) as error:
            raise StorageException("operation must be StorageOperation") from error
        if not isinstance(self.location, StorageLocation):
            raise StorageException("location must be StorageLocation")
        object.__setattr__(
            self,
            "parameters",
            _freeze(_mapping(self.parameters, "parameters")),
        )
        if self.schema_version != STORAGE_SCHEMA_VERSION:
            raise StorageException("unsupported StorageContext version")

    def to_dict(self) -> dict[str, object]:
        """Serialize context to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "storage_context",
            "correlation_id": self.correlation_id,
            "operation": self.operation.value,
            "location": self.location.to_dict(),
            "parameters": _primitive(self.parameters),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize context from a strict versioned mapping."""
        data = _envelope(
            payload,
            "storage_context",
            {"correlation_id", "operation", "location", "parameters"},
        )
        return cls(
            correlation_id=data["correlation_id"],
            operation=data["operation"],
            location=StorageLocation.from_dict(
                _mapping(data["location"], "location")
            ),
            parameters=_mapping(data["parameters"], "parameters"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize context from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class StorageSession(_SerializableModel):
    """Immutable lifecycle snapshot for one storage operation."""

    session_id: str
    storage_id: str
    context: StorageContext
    state: StorageSessionState
    started_at: datetime
    finished_at: datetime | None = None
    failure: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = STORAGE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", _text(self.session_id, "session_id"))
        object.__setattr__(self, "storage_id", _text(self.storage_id, "storage_id"))
        if not isinstance(self.context, StorageContext):
            raise StorageException("context must be StorageContext")
        try:
            object.__setattr__(self, "state", StorageSessionState(self.state))
        except (TypeError, ValueError) as error:
            raise StorageException("state must be StorageSessionState") from error
        object.__setattr__(self, "started_at", _instant(self.started_at, "started_at"))
        if self.finished_at is not None:
            finished_at = _instant(self.finished_at, "finished_at")
            if finished_at < self.started_at:
                raise StorageException("finished_at cannot precede started_at")
            object.__setattr__(self, "finished_at", finished_at)
        object.__setattr__(self, "failure", _optional_text(self.failure, "failure"))
        object.__setattr__(
            self, "metadata", _freeze(_mapping(self.metadata, "metadata"))
        )
        if self.state is StorageSessionState.STARTED:
            if self.finished_at is not None or self.failure is not None:
                raise StorageException("started session cannot be terminal")
        elif self.finished_at is None:
            raise StorageException("terminal session requires finished_at")
        if self.state is StorageSessionState.FAILED and self.failure is None:
            raise StorageException("failed session requires failure")
        if self.state is StorageSessionState.FINISHED and self.failure is not None:
            raise StorageException("finished session cannot contain failure")
        if self.schema_version != STORAGE_SCHEMA_VERSION:
            raise StorageException("unsupported StorageSession version")

    @classmethod
    def start(
        cls,
        session_id: str,
        storage_id: str,
        context: StorageContext,
        started_at: datetime,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> Self:
        """Create and log a started immutable storage session."""
        session = cls(
            session_id=session_id,
            storage_id=storage_id,
            context=context,
            state=StorageSessionState.STARTED,
            started_at=started_at,
            metadata={} if metadata is None else metadata,
        )
        _LOGGER.info(
            "storage_session_started",
            extra={
                "event": "storage_session_started",
                "context": {
                    "storage_id": session.storage_id,
                    "session_id": session.session_id,
                },
            },
        )
        return session

    def finish(self, finished_at: datetime, *, failure: str | None = None) -> Self:
        """Return and log the terminal snapshot of a started session."""
        if self.state is not StorageSessionState.STARTED:
            raise StorageException("only a started session can be finished")
        state = (
            StorageSessionState.FINISHED
            if failure is None
            else StorageSessionState.FAILED
        )
        session = replace(
            self, state=state, finished_at=finished_at, failure=failure
        )
        _LOGGER.info(
            "storage_session_finished",
            extra={
                "event": "storage_session_finished",
                "context": {
                    "storage_id": session.storage_id,
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
            "model": "storage_session",
            "session_id": self.session_id,
            "storage_id": self.storage_id,
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
            "storage_session",
            {
                "session_id", "storage_id", "context", "state", "started_at",
                "finished_at", "failure", "metadata",
            },
        )
        finished = data["finished_at"]
        return cls(
            session_id=data["session_id"],
            storage_id=data["storage_id"],
            context=StorageContext.from_dict(
                _mapping(data["context"], "context")
            ),
            state=data["state"],
            started_at=_parse_instant(data["started_at"], "started_at"),
            finished_at=(
                None if finished is None else _parse_instant(finished, "finished_at")
            ),
            failure=data["failure"],
            metadata=_mapping(data["metadata"], "metadata"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize session from strict JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class StorageResult(_SerializableModel):
    """Immutable logical outcome of a storage operation."""

    storage_id: str
    operation: StorageOperation
    success: bool
    objects: tuple[StorageObject, ...] = ()
    message: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = STORAGE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "storage_id", _text(self.storage_id, "storage_id"))
        try:
            object.__setattr__(self, "operation", StorageOperation(self.operation))
        except (TypeError, ValueError) as error:
            raise StorageException("operation must be StorageOperation") from error
        if not isinstance(self.success, bool):
            raise StorageException("success must be boolean")
        if not isinstance(self.objects, (tuple, list)):
            raise StorageException("objects must be a collection")
        objects = tuple(self.objects)
        if any(not isinstance(item, StorageObject) for item in objects):
            raise StorageException("objects must contain StorageObject values")
        object.__setattr__(self, "objects", objects)
        object.__setattr__(self, "message", _optional_text(self.message, "message"))
        object.__setattr__(
            self, "metadata", _freeze(_mapping(self.metadata, "metadata"))
        )
        if not self.success and self.message is None:
            raise StorageException("failed result requires a message")
        if self.schema_version != STORAGE_SCHEMA_VERSION:
            raise StorageException("unsupported StorageResult version")

    def to_dict(self) -> dict[str, object]:
        """Serialize result to a strict versioned mapping."""
        return {
            "schema_version": self.schema_version,
            "model": "storage_result",
            "storage_id": self.storage_id,
            "operation": self.operation.value,
            "success": self.success,
            "objects": [item.to_dict() for item in self.objects],
            "message": self.message,
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize result from a strict versioned mapping."""
        data = _envelope(
            payload,
            "storage_result",
            {"storage_id", "operation", "success", "objects", "message", "metadata"},
        )
        if not isinstance(data["objects"], list):
            raise StorageException("objects must be a list")
        return cls(
            storage_id=data["storage_id"],
            operation=data["operation"],
            success=data["success"],
            objects=tuple(
                StorageObject.from_dict(_mapping(item, "object"))
                for item in data["objects"]
            ),
            message=data["message"],
            metadata=_mapping(data["metadata"], "metadata"),
            schema_version=data["schema_version"],
        )  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize result from strict JSON."""
        return cls.from_dict(_decode(payload))


__all__ = [
    "STORAGE_SCHEMA_VERSION",
    "STORAGE_VERSION",
    "StorageCapabilities",
    "StorageContext",
    "StorageDescriptor",
    "StorageLocation",
    "StorageMetadata",
    "StorageObject",
    "StorageOperation",
    "StorageResult",
    "StorageSession",
    "StorageSessionState",
]
