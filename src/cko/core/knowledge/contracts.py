"""Shared contracts and normalization primitives for Knowledge Objects."""

from __future__ import annotations

import base64
import binascii
import math
import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Protocol, runtime_checkable

from .errors import KnowledgeSerializationError, KnowledgeValidationError


KNOWLEDGE_SCHEMA_VERSION = "1.0"
KNOWLEDGE_VERSION = "1.0.0"
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def require_text(value: object, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeValidationError(f"{name} must be a non-empty string")
    return value.strip()


def require_instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise KnowledgeValidationError(f"{name} must be timezone-aware")
    if value.utcoffset() is None:
        raise KnowledgeValidationError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def parse_instant(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise KnowledgeSerializationError(f"{name} must be an ISO-8601 string")
    try:
        return require_instant(datetime.fromisoformat(value), name)
    except (ValueError, KnowledgeValidationError) as error:
        raise KnowledgeSerializationError(f"{name} must be an ISO-8601 UTC instant") from error


def require_probability(value: object, name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise KnowledgeValidationError(f"{name} must be a finite number")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise KnowledgeValidationError(f"{name} must be between 0 and 1")
    return normalized


def require_hash(value: object, name: str = "hash") -> str:
    normalized = require_text(value, name)
    assert isinstance(normalized, str)
    if _HEX_64.fullmatch(normalized.lower()) is None:
        raise KnowledgeValidationError(f"{name} must be a SHA-256 hexadecimal digest")
    return normalized.lower()


def deep_freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str, bytes)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise KnowledgeValidationError("numbers must be finite")
        return value
    if isinstance(value, Enum):
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            normalized = require_text(key, "mapping key")
            assert isinstance(normalized, str)
            if normalized in frozen:
                raise KnowledgeValidationError("mapping keys must be unique")
            frozen[normalized] = deep_freeze(item)
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list)):
        return tuple(deep_freeze(item) for item in value)
    if isinstance(value, SerializableKnowledgeModel):
        return value
    raise KnowledgeValidationError(f"unsupported immutable value: {type(value).__name__}")


def primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return require_instant(value, "datetime").isoformat()
    if isinstance(value, SerializableKnowledgeModel):
        return value.to_dict()
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            raise KnowledgeSerializationError("numbers must be finite")
        return value
    if isinstance(value, bytes):
        return {"$binary": base64.b64encode(value).decode("ascii"), "$encoding": "base64"}
    if isinstance(value, Mapping):
        return {str(key): primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [primitive(item) for item in value]
    raise KnowledgeSerializationError(f"unsupported serialized value: {type(value).__name__}")


def restore_primitive(value: object) -> object:
    if isinstance(value, Mapping):
        if set(value) == {"$binary", "$encoding"}:
            if value.get("$encoding") != "base64" or not isinstance(value.get("$binary"), str):
                raise KnowledgeSerializationError("invalid binary envelope")
            try:
                return base64.b64decode(value["$binary"], validate=True)
            except (binascii.Error, ValueError) as error:
                raise KnowledgeSerializationError("invalid base64 payload") from error
        return {str(key): restore_primitive(item) for key, item in value.items()}
    if isinstance(value, list):
        return tuple(restore_primitive(item) for item in value)
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            raise KnowledgeSerializationError("numbers must be finite")
        return value
    raise KnowledgeSerializationError(f"unsupported decoded value: {type(value).__name__}")


def strict_envelope(payload: object, model: str, fields: set[str]) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise KnowledgeSerializationError(f"{model} must be a mapping")
    if set(payload) != fields | {"model", "schema_version"}:
        raise KnowledgeSerializationError(f"invalid or unknown {model} fields")
    if payload.get("model") != model:
        raise KnowledgeSerializationError(f"invalid {model} discriminator")
    if payload.get("schema_version") != KNOWLEDGE_SCHEMA_VERSION:
        raise KnowledgeSerializationError(f"unsupported {model} schema_version")
    return payload


def model_sequence(value: object, name: str, expected: type) -> tuple:
    if not isinstance(value, (tuple, list)):
        raise KnowledgeValidationError(f"{name} must be a sequence")
    result = tuple(value)
    if any(not isinstance(item, expected) for item in result):
        raise KnowledgeValidationError(f"{name} contains an invalid model")
    return result


def unique_texts(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        raise KnowledgeValidationError(f"{name} must be a sequence")
    normalized: list[str] = []
    for item in value:
        text = require_text(item, name)
        assert isinstance(text, str)
        normalized.append(text)
    if len(set(normalized)) != len(normalized):
        raise KnowledgeValidationError(f"{name} must not contain duplicates")
    return tuple(normalized)


class SerializableKnowledgeModel(ABC):
    """Base behavior implemented by every canonical model."""

    __slots__ = ()
    model_name: ClassVar[str]
    schema_version: str

    @property
    def model(self) -> str:
        return self.model_name

    def _validate_schema(self) -> None:
        if self.schema_version != KNOWLEDGE_SCHEMA_VERSION:
            raise KnowledgeValidationError(f"unsupported {self.model_name} schema_version")

    @abstractmethod
    def to_dict(self) -> dict[str, object]:
        """Return the strict serialization envelope."""


@runtime_checkable
class KnowledgeSerializer(Protocol):
    def serialize(self, value: SerializableKnowledgeModel) -> bytes: ...
    def deserialize(self, payload: bytes | str) -> SerializableKnowledgeModel: ...
    def digest(self, value: SerializableKnowledgeModel) -> str: ...


@runtime_checkable
class KnowledgeValidatorContract(Protocol):
    def validate(self, value: SerializableKnowledgeModel) -> None: ...


__all__ = [
    "KNOWLEDGE_SCHEMA_VERSION", "KNOWLEDGE_VERSION", "KnowledgeSerializer",
    "KnowledgeValidatorContract", "SerializableKnowledgeModel", "deep_freeze",
    "model_sequence", "parse_instant", "primitive", "require_hash",
    "require_instant", "require_probability", "require_text", "restore_primitive",
    "strict_envelope", "unique_texts",
]
