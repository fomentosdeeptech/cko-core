"""Immutable, strict, and versioned checkpoint models."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Self

from .errors import (
    CheckpointIntegrityError,
    CheckpointSerializationError,
    CheckpointValidationError,
)


CHECKPOINT_SCHEMA_VERSION = "1.0"
CHECKPOINT_VERSION = "1.0.0"


class CheckpointState(str, Enum):
    """Canonical lifecycle states of a checkpoint."""

    CREATED = "created"
    STORED = "stored"
    RESTORED = "restored"
    SUPERSEDED = "superseded"
    FAILED = "failed"


class CheckpointOperation(str, Enum):
    """Canonical operations supported by the checkpoint engine."""

    CREATE = "create"
    STORE = "store"
    RESTORE = "restore"
    LIST = "list"
    INSPECT = "inspect"
    SUPERSEDE = "supersede"
    DELETE = "delete"


def _text(value: object, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise CheckpointValidationError(
            f"{name} must be a non-empty string"
        )
    return value.strip()


def _boolean(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise CheckpointValidationError(f"{name} must be boolean")
    return value


def _integer(
    value: object,
    name: str,
    *,
    minimum: int = 0,
    optional: bool = False,
) -> int | None:
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise CheckpointValidationError(f"{name} must be an integer")
    if value < minimum:
        raise CheckpointValidationError(
            f"{name} must be at least {minimum}"
        )
    return value


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise CheckpointValidationError(f"{name} must be a mapping")
    return value


def _instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise CheckpointValidationError(f"{name} must be timezone-aware")
    if value.utcoffset() is None:
        raise CheckpointValidationError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _parse_instant(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise CheckpointSerializationError(f"{name} must be an ISO string")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise CheckpointSerializationError(
            f"{name} must be an ISO string"
        ) from error
    try:
        return _instant(parsed, name)
    except CheckpointValidationError as error:
        raise CheckpointSerializationError(str(error)) from error


def _freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str, bytes)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CheckpointValidationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        normalized: dict[str, object] = {}
        for key, item in value.items():
            normalized_key = _text(key, "mapping key")
            assert isinstance(normalized_key, str)
            normalized[normalized_key] = _freeze(item)
        return MappingProxyType(dict(sorted(normalized.items())))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    raise CheckpointValidationError(
        f"unsupported serializable value: {type(value).__name__}"
    )


def _primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return {
            "$binary": base64.b64encode(value).decode("ascii"),
            "$encoding": "base64",
        }
    if isinstance(value, Mapping):
        return {
            str(key): _primitive(item)
            for key, item in sorted(value.items())
        }
    if isinstance(value, (tuple, list)):
        return [_primitive(item) for item in value]
    raise CheckpointSerializationError(
        f"unsupported checkpoint serialization: {type(value).__name__}"
    )


def _restore_primitive(value: object) -> object:
    if isinstance(value, Mapping):
        if set(value) == {"$binary", "$encoding"}:
            if value.get("$encoding") != "base64":
                raise CheckpointSerializationError(
                    "binary envelope encoding is unsupported"
                )
            encoded = value.get("$binary")
            if not isinstance(encoded, str):
                raise CheckpointSerializationError(
                    "binary envelope payload must be a string"
                )
            try:
                return base64.b64decode(encoded, validate=True)
            except (binascii.Error, ValueError) as error:
                raise CheckpointSerializationError(
                    "binary envelope payload is invalid"
                ) from error
        return {
            str(key): _restore_primitive(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return tuple(_restore_primitive(item) for item in value)
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            raise CheckpointSerializationError("numbers must be finite")
        return value
    raise CheckpointSerializationError(
        f"unsupported decoded value: {type(value).__name__}"
    )


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            _primitive(value),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise CheckpointSerializationError(
            "value is not canonical JSON"
        ) from error


def _decode(payload: str | bytes) -> Mapping[str, object]:
    try:
        if isinstance(payload, bytes):
            text = payload.decode("utf-8")
        elif isinstance(payload, str):
            text = payload
        else:
            raise TypeError
        decoded = json.loads(
            text,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(value)
            ),
        )
    except (TypeError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        raise CheckpointSerializationError(
            "checkpoint JSON is invalid UTF-8 canonical JSON"
        ) from error
    if not isinstance(decoded, Mapping):
        raise CheckpointSerializationError(
            "checkpoint JSON must contain an object"
        )
    return decoded


def _envelope(
    payload: Mapping[str, object],
    model: str,
    fields: set[str],
) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise CheckpointSerializationError(f"{model} must be a mapping")
    expected = fields | {"schema_version", "model"}
    if set(payload) != expected:
        raise CheckpointSerializationError(
            f"invalid {model} fields"
        )
    if payload.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
        raise CheckpointSerializationError(
            f"unsupported {model} schema_version"
        )
    if payload.get("model") != model:
        raise CheckpointSerializationError(f"invalid {model} model")
    return payload


class _SerializableModel(ABC):
    """Shared deterministic serialization behavior."""

    __slots__ = ()
    model_name: ClassVar[str]
    schema_version: str

    @property
    def model(self) -> str:
        """Return the stable serialized model discriminator."""
        return self.model_name

    @abstractmethod
    def to_dict(self) -> dict[str, object]:
        """Serialize this model to its strict envelope."""

    def to_json(self) -> str:
        """Serialize this model to deterministic JSON."""
        return _canonical(self.to_dict()).decode("utf-8")


@dataclass(frozen=True, slots=True)
class CheckpointIdentifier(_SerializableModel):
    """Logical, provider-neutral identity of one checkpoint."""

    checkpoint_id: str
    namespace: str
    subject_id: str
    sequence: int
    created_at: datetime
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_identifier"

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "checkpoint_id", _text(self.checkpoint_id, "checkpoint_id")
        )
        object.__setattr__(
            self, "namespace", _text(self.namespace, "namespace")
        )
        object.__setattr__(
            self, "subject_id", _text(self.subject_id, "subject_id")
        )
        object.__setattr__(
            self, "sequence", _integer(self.sequence, "sequence")
        )
        object.__setattr__(
            self, "created_at", _instant(self.created_at, "created_at")
        )
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointIdentifier version"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize the identifier."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "checkpoint_id": self.checkpoint_id,
            "namespace": self.namespace,
            "subject_id": self.subject_id,
            "sequence": self.sequence,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict identifier envelope."""
        data = _envelope(
            payload,
            cls.model_name,
            {
                "checkpoint_id", "namespace", "subject_id", "sequence",
                "created_at",
            },
        )
        return cls(
            checkpoint_id=data["checkpoint_id"],  # type: ignore[arg-type]
            namespace=data["namespace"],  # type: ignore[arg-type]
            subject_id=data["subject_id"],  # type: ignore[arg-type]
            sequence=data["sequence"],  # type: ignore[arg-type]
            created_at=_parse_instant(data["created_at"], "created_at"),
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize an identifier from JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class CheckpointMetadata(_SerializableModel):
    """Safe descriptive metadata associated with a checkpoint."""

    name: str
    description: str
    producer: str
    producer_version: str
    labels: Mapping[str, object] = field(default_factory=dict)
    attributes: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_metadata"

    def __post_init__(self) -> None:
        for name in ("name", "description", "producer", "producer_version"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(
            self, "labels", _freeze(_mapping(self.labels, "labels"))
        )
        object.__setattr__(
            self,
            "attributes",
            _freeze(_mapping(self.attributes, "attributes")),
        )
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointMetadata version"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize metadata."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "name": self.name,
            "description": self.description,
            "producer": self.producer,
            "producer_version": self.producer_version,
            "labels": _primitive(self.labels),
            "attributes": _primitive(self.attributes),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize strict checkpoint metadata."""
        data = _envelope(
            payload,
            cls.model_name,
            {
                "name", "description", "producer", "producer_version",
                "labels", "attributes",
            },
        )
        return cls(
            name=data["name"],  # type: ignore[arg-type]
            description=data["description"],  # type: ignore[arg-type]
            producer=data["producer"],  # type: ignore[arg-type]
            producer_version=data["producer_version"],  # type: ignore[arg-type]
            labels=_mapping(data["labels"], "labels"),
            attributes=_mapping(data["attributes"], "attributes"),
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize metadata from JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class CheckpointPayload(_SerializableModel):
    """Neutral canonical payload with calculated integrity metadata."""

    content_type: str
    encoding: str
    data: object = field(repr=False)
    size: int | None = None
    sha256: str | None = None
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_payload"

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "content_type", _text(self.content_type, "content_type")
        )
        encoding = _text(self.encoding, "encoding")
        if not isinstance(encoding, str) or encoding.lower() != "utf-8":
            raise CheckpointValidationError("encoding must be utf-8")
        object.__setattr__(self, "encoding", "utf-8")
        frozen = _freeze(self.data)
        object.__setattr__(self, "data", frozen)
        canonical = _canonical(frozen)
        calculated_size = len(canonical)
        calculated_digest = hashlib.sha256(canonical).hexdigest()
        if self.size is not None and self.size != calculated_size:
            raise CheckpointIntegrityError("checkpoint payload size mismatch")
        if self.sha256 is not None:
            digest = _text(self.sha256, "sha256")
            if digest != calculated_digest:
                raise CheckpointIntegrityError(
                    "checkpoint payload SHA-256 mismatch"
                )
        object.__setattr__(self, "size", calculated_size)
        object.__setattr__(self, "sha256", calculated_digest)
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointPayload version"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize the payload and its integrity metadata."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "content_type": self.content_type,
            "encoding": self.encoding,
            "data": _primitive(self.data),
            "size": self.size,
            "sha256": self.sha256,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize and verify a strict payload envelope."""
        data = _envelope(
            payload,
            cls.model_name,
            {"content_type", "encoding", "data", "size", "sha256"},
        )
        return cls(
            content_type=data["content_type"],  # type: ignore[arg-type]
            encoding=data["encoding"],  # type: ignore[arg-type]
            data=_restore_primitive(data["data"]),
            size=data["size"],  # type: ignore[arg-type]
            sha256=data["sha256"],  # type: ignore[arg-type]
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize and verify a payload from JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class CheckpointRecord(_SerializableModel):
    """Complete persistable checkpoint record."""

    identifier: CheckpointIdentifier
    metadata: CheckpointMetadata
    payload: CheckpointPayload
    state: CheckpointState
    correlation_id: str
    parent_checkpoint_id: str | None
    created_at: datetime
    updated_at: datetime
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_record"

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, CheckpointIdentifier):
            raise CheckpointValidationError(
                "identifier must be CheckpointIdentifier"
            )
        if not isinstance(self.metadata, CheckpointMetadata):
            raise CheckpointValidationError(
                "metadata must be CheckpointMetadata"
            )
        if not isinstance(self.payload, CheckpointPayload):
            raise CheckpointValidationError(
                "payload must be CheckpointPayload"
            )
        try:
            object.__setattr__(self, "state", CheckpointState(self.state))
        except (TypeError, ValueError) as error:
            raise CheckpointValidationError(
                "state must be CheckpointState"
            ) from error
        object.__setattr__(
            self,
            "correlation_id",
            _text(self.correlation_id, "correlation_id"),
        )
        object.__setattr__(
            self,
            "parent_checkpoint_id",
            _text(
                self.parent_checkpoint_id,
                "parent_checkpoint_id",
                optional=True,
            ),
        )
        created = _instant(self.created_at, "created_at")
        updated = _instant(self.updated_at, "updated_at")
        if created != self.identifier.created_at:
            raise CheckpointValidationError(
                "record created_at must equal identifier created_at"
            )
        if updated < created:
            raise CheckpointValidationError(
                "updated_at cannot precede created_at"
            )
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "updated_at", updated)
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointRecord version"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete record."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "identifier": self.identifier.to_dict(),
            "metadata": self.metadata.to_dict(),
            "payload": self.payload.to_dict(),
            "state": self.state.value,
            "correlation_id": self.correlation_id,
            "parent_checkpoint_id": self.parent_checkpoint_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize and verify a strict record envelope."""
        data = _envelope(
            payload,
            cls.model_name,
            {
                "identifier", "metadata", "payload", "state",
                "correlation_id", "parent_checkpoint_id", "created_at",
                "updated_at",
            },
        )
        return cls(
            identifier=CheckpointIdentifier.from_dict(
                _mapping(data["identifier"], "identifier")
            ),
            metadata=CheckpointMetadata.from_dict(
                _mapping(data["metadata"], "metadata")
            ),
            payload=CheckpointPayload.from_dict(
                _mapping(data["payload"], "payload")
            ),
            state=data["state"],  # type: ignore[arg-type]
            correlation_id=data["correlation_id"],  # type: ignore[arg-type]
            parent_checkpoint_id=data["parent_checkpoint_id"],  # type: ignore[arg-type]
            created_at=_parse_instant(data["created_at"], "created_at"),
            updated_at=_parse_instant(data["updated_at"], "updated_at"),
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize and verify a record from JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class CheckpointSnapshot(_SerializableModel):
    """Immutable view of a checkpoint at a logical instant."""

    snapshot_id: str
    checkpoint: CheckpointRecord
    captured_at: datetime
    digest: str
    sequence: int
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_snapshot"

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "snapshot_id", _text(self.snapshot_id, "snapshot_id")
        )
        if not isinstance(self.checkpoint, CheckpointRecord):
            raise CheckpointValidationError(
                "checkpoint must be CheckpointRecord"
            )
        object.__setattr__(
            self, "captured_at", _instant(self.captured_at, "captured_at")
        )
        sequence = _integer(self.sequence, "sequence")
        if sequence != self.checkpoint.identifier.sequence:
            raise CheckpointValidationError(
                "snapshot sequence must equal checkpoint sequence"
            )
        object.__setattr__(self, "sequence", sequence)
        calculated = hashlib.sha256(
            _canonical(self.checkpoint.to_dict())
        ).hexdigest()
        digest = _text(self.digest, "digest")
        if digest != calculated:
            raise CheckpointIntegrityError("checkpoint snapshot digest mismatch")
        object.__setattr__(self, "digest", calculated)
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointSnapshot version"
            )

    @classmethod
    def capture(
        cls,
        snapshot_id: str,
        checkpoint: CheckpointRecord,
        captured_at: datetime,
    ) -> Self:
        """Capture a checkpoint and calculate its canonical digest."""
        digest = hashlib.sha256(
            _canonical(checkpoint.to_dict())
        ).hexdigest()
        return cls(
            snapshot_id=snapshot_id,
            checkpoint=checkpoint,
            captured_at=captured_at,
            digest=digest,
            sequence=checkpoint.identifier.sequence,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the snapshot."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "snapshot_id": self.snapshot_id,
            "checkpoint": self.checkpoint.to_dict(),
            "captured_at": self.captured_at.isoformat(),
            "digest": self.digest,
            "sequence": self.sequence,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize and verify a strict snapshot envelope."""
        data = _envelope(
            payload,
            cls.model_name,
            {
                "snapshot_id", "checkpoint", "captured_at", "digest",
                "sequence",
            },
        )
        return cls(
            snapshot_id=data["snapshot_id"],  # type: ignore[arg-type]
            checkpoint=CheckpointRecord.from_dict(
                _mapping(data["checkpoint"], "checkpoint")
            ),
            captured_at=_parse_instant(data["captured_at"], "captured_at"),
            digest=data["digest"],  # type: ignore[arg-type]
            sequence=data["sequence"],  # type: ignore[arg-type]
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize and verify a snapshot from JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class CheckpointContext(_SerializableModel):
    """Safe logical context for one checkpoint operation."""

    correlation_id: str
    operation: CheckpointOperation
    namespace: str
    subject_id: str
    parameters: Mapping[str, object] = field(default_factory=dict)
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_context"

    def __post_init__(self) -> None:
        for name in ("correlation_id", "namespace", "subject_id"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        try:
            object.__setattr__(
                self, "operation", CheckpointOperation(self.operation)
            )
        except (TypeError, ValueError) as error:
            raise CheckpointValidationError(
                "operation must be CheckpointOperation"
            ) from error
        object.__setattr__(
            self,
            "parameters",
            _freeze(_mapping(self.parameters, "parameters")),
        )
        object.__setattr__(
            self, "metadata", _freeze(_mapping(self.metadata, "metadata"))
        )
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointContext version"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize the logical context."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "correlation_id": self.correlation_id,
            "operation": self.operation.value,
            "namespace": self.namespace,
            "subject_id": self.subject_id,
            "parameters": _primitive(self.parameters),
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict context envelope."""
        data = _envelope(
            payload,
            cls.model_name,
            {
                "correlation_id", "operation", "namespace", "subject_id",
                "parameters", "metadata",
            },
        )
        return cls(
            correlation_id=data["correlation_id"],  # type: ignore[arg-type]
            operation=data["operation"],  # type: ignore[arg-type]
            namespace=data["namespace"],  # type: ignore[arg-type]
            subject_id=data["subject_id"],  # type: ignore[arg-type]
            parameters=_mapping(data["parameters"], "parameters"),
            metadata=_mapping(data["metadata"], "metadata"),
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize a context from JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class CheckpointQuery(_SerializableModel):
    """Technology-neutral logical checkpoint query."""

    namespace: str | None = None
    subject_id: str | None = None
    checkpoint_id: str | None = None
    state: CheckpointState | None = None
    sequence_min: int | None = None
    sequence_max: int | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    limit: int | None = None
    descending: bool = False
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_query"

    def __post_init__(self) -> None:
        for name in ("namespace", "subject_id", "checkpoint_id"):
            object.__setattr__(
                self,
                name,
                _text(getattr(self, name), name, optional=True),
            )
        if self.state is not None:
            try:
                object.__setattr__(
                    self, "state", CheckpointState(self.state)
                )
            except (TypeError, ValueError) as error:
                raise CheckpointValidationError(
                    "state must be CheckpointState"
                ) from error
        minimum = _integer(
            self.sequence_min, "sequence_min", optional=True
        )
        maximum = _integer(
            self.sequence_max, "sequence_max", optional=True
        )
        if minimum is not None and maximum is not None and minimum > maximum:
            raise CheckpointValidationError(
                "sequence_min cannot exceed sequence_max"
            )
        object.__setattr__(self, "sequence_min", minimum)
        object.__setattr__(self, "sequence_max", maximum)
        start = (
            None
            if self.created_from is None
            else _instant(self.created_from, "created_from")
        )
        end = (
            None
            if self.created_to is None
            else _instant(self.created_to, "created_to")
        )
        if start is not None and end is not None and start > end:
            raise CheckpointValidationError(
                "created_from cannot exceed created_to"
            )
        object.__setattr__(self, "created_from", start)
        object.__setattr__(self, "created_to", end)
        object.__setattr__(
            self, "limit", _integer(self.limit, "limit", minimum=1, optional=True)
        )
        object.__setattr__(
            self, "descending", _boolean(self.descending, "descending")
        )
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointQuery version"
            )

    def matches(self, record: CheckpointRecord) -> bool:
        """Return whether a record satisfies all logical filters."""
        identifier = record.identifier
        return all(
            (
                self.namespace is None
                or identifier.namespace == self.namespace,
                self.subject_id is None
                or identifier.subject_id == self.subject_id,
                self.checkpoint_id is None
                or identifier.checkpoint_id == self.checkpoint_id,
                self.state is None or record.state is self.state,
                self.sequence_min is None
                or identifier.sequence >= self.sequence_min,
                self.sequence_max is None
                or identifier.sequence <= self.sequence_max,
                self.created_from is None
                or identifier.created_at >= self.created_from,
                self.created_to is None
                or identifier.created_at <= self.created_to,
            )
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the logical query."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "namespace": self.namespace,
            "subject_id": self.subject_id,
            "checkpoint_id": self.checkpoint_id,
            "state": None if self.state is None else self.state.value,
            "sequence_min": self.sequence_min,
            "sequence_max": self.sequence_max,
            "created_from": (
                None
                if self.created_from is None
                else self.created_from.isoformat()
            ),
            "created_to": (
                None if self.created_to is None else self.created_to.isoformat()
            ),
            "limit": self.limit,
            "descending": self.descending,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict query envelope."""
        data = _envelope(
            payload,
            cls.model_name,
            {
                "namespace", "subject_id", "checkpoint_id", "state",
                "sequence_min", "sequence_max", "created_from", "created_to",
                "limit", "descending",
            },
        )
        return cls(
            namespace=data["namespace"],  # type: ignore[arg-type]
            subject_id=data["subject_id"],  # type: ignore[arg-type]
            checkpoint_id=data["checkpoint_id"],  # type: ignore[arg-type]
            state=data["state"],  # type: ignore[arg-type]
            sequence_min=data["sequence_min"],  # type: ignore[arg-type]
            sequence_max=data["sequence_max"],  # type: ignore[arg-type]
            created_from=(
                None
                if data["created_from"] is None
                else _parse_instant(data["created_from"], "created_from")
            ),
            created_to=(
                None
                if data["created_to"] is None
                else _parse_instant(data["created_to"], "created_to")
            ),
            limit=data["limit"],  # type: ignore[arg-type]
            descending=data["descending"],  # type: ignore[arg-type]
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize a query from JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class CheckpointCollection(_SerializableModel):
    """Deterministically ordered immutable checkpoint collection."""

    checkpoints: tuple[CheckpointRecord, ...] = ()
    total: int | None = None
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_collection"

    def __post_init__(self) -> None:
        if not isinstance(self.checkpoints, (tuple, list)):
            raise CheckpointValidationError(
                "checkpoints must be a sequence"
            )
        normalized = tuple(self.checkpoints)
        if any(
            not isinstance(item, CheckpointRecord) for item in normalized
        ):
            raise CheckpointValidationError(
                "checkpoints must contain CheckpointRecord values"
            )
        object.__setattr__(self, "checkpoints", normalized)
        total = len(normalized) if self.total is None else _integer(
            self.total, "total"
        )
        if total is None or total < len(normalized):
            raise CheckpointValidationError(
                "total cannot be less than collection size"
            )
        object.__setattr__(self, "total", total)
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointCollection version"
            )

    def __iter__(self):
        """Iterate over immutable checkpoint records."""
        return iter(self.checkpoints)

    def __len__(self) -> int:
        """Return the number of records in this collection."""
        return len(self.checkpoints)

    def to_dict(self) -> dict[str, object]:
        """Serialize the collection."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "checkpoints": [item.to_dict() for item in self.checkpoints],
            "total": self.total,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict collection envelope."""
        data = _envelope(
            payload,
            cls.model_name,
            {"checkpoints", "total"},
        )
        items = data["checkpoints"]
        if not isinstance(items, list):
            raise CheckpointSerializationError(
                "checkpoints must be a list"
            )
        return cls(
            checkpoints=tuple(
                CheckpointRecord.from_dict(_mapping(item, "checkpoint"))
                for item in items
            ),
            total=data["total"],  # type: ignore[arg-type]
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize a collection from JSON."""
        return cls.from_dict(_decode(payload))


@dataclass(frozen=True, slots=True)
class CheckpointResult(_SerializableModel):
    """Typed immutable result of a checkpoint operation."""

    success: bool
    operation: CheckpointOperation
    checkpoint: CheckpointRecord | None = None
    snapshot: CheckpointSnapshot | None = None
    collection: CheckpointCollection | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema_version: str = CHECKPOINT_SCHEMA_VERSION
    model_name: ClassVar[str] = "checkpoint_result"

    def __post_init__(self) -> None:
        object.__setattr__(self, "success", _boolean(self.success, "success"))
        try:
            object.__setattr__(
                self, "operation", CheckpointOperation(self.operation)
            )
        except (TypeError, ValueError) as error:
            raise CheckpointValidationError(
                "operation must be CheckpointOperation"
            ) from error
        if self.checkpoint is not None and not isinstance(
            self.checkpoint, CheckpointRecord
        ):
            raise CheckpointValidationError(
                "checkpoint must be CheckpointRecord when provided"
            )
        if self.snapshot is not None and not isinstance(
            self.snapshot, CheckpointSnapshot
        ):
            raise CheckpointValidationError(
                "snapshot must be CheckpointSnapshot when provided"
            )
        if self.collection is not None and not isinstance(
            self.collection, CheckpointCollection
        ):
            raise CheckpointValidationError(
                "collection must be CheckpointCollection when provided"
            )
        object.__setattr__(
            self,
            "error_code",
            _text(self.error_code, "error_code", optional=True),
        )
        object.__setattr__(
            self,
            "error_message",
            _text(self.error_message, "error_message", optional=True),
        )
        if self.success and (
            self.error_code is not None or self.error_message is not None
        ):
            raise CheckpointValidationError(
                "successful result cannot contain an error"
            )
        if not self.success and (
            self.error_code is None or self.error_message is None
        ):
            raise CheckpointValidationError(
                "failed result requires error_code and error_message"
            )
        object.__setattr__(
            self, "metadata", _freeze(_mapping(self.metadata, "metadata"))
        )
        if self.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported CheckpointResult version"
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize the typed result."""
        return {
            "schema_version": self.schema_version,
            "model": self.model,
            "success": self.success,
            "operation": self.operation.value,
            "checkpoint": (
                None if self.checkpoint is None else self.checkpoint.to_dict()
            ),
            "snapshot": (
                None if self.snapshot is None else self.snapshot.to_dict()
            ),
            "collection": (
                None if self.collection is None else self.collection.to_dict()
            ),
            "error_code": self.error_code,
            "error_message": self.error_message,
            "metadata": _primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict result envelope."""
        data = _envelope(
            payload,
            cls.model_name,
            {
                "success", "operation", "checkpoint", "snapshot",
                "collection", "error_code", "error_message", "metadata",
            },
        )
        return cls(
            success=data["success"],  # type: ignore[arg-type]
            operation=data["operation"],  # type: ignore[arg-type]
            checkpoint=(
                None
                if data["checkpoint"] is None
                else CheckpointRecord.from_dict(
                    _mapping(data["checkpoint"], "checkpoint")
                )
            ),
            snapshot=(
                None
                if data["snapshot"] is None
                else CheckpointSnapshot.from_dict(
                    _mapping(data["snapshot"], "snapshot")
                )
            ),
            collection=(
                None
                if data["collection"] is None
                else CheckpointCollection.from_dict(
                    _mapping(data["collection"], "collection")
                )
            ),
            error_code=data["error_code"],  # type: ignore[arg-type]
            error_message=data["error_message"],  # type: ignore[arg-type]
            metadata=_mapping(data["metadata"], "metadata"),
            schema_version=data["schema_version"],  # type: ignore[arg-type]
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> Self:
        """Deserialize a typed result from JSON."""
        return cls.from_dict(_decode(payload))


__all__ = [
    "CHECKPOINT_SCHEMA_VERSION",
    "CHECKPOINT_VERSION",
    "CheckpointCollection",
    "CheckpointContext",
    "CheckpointIdentifier",
    "CheckpointMetadata",
    "CheckpointOperation",
    "CheckpointPayload",
    "CheckpointQuery",
    "CheckpointRecord",
    "CheckpointResult",
    "CheckpointSnapshot",
    "CheckpointState",
]
