"""Contracts and normalization primitives for canonical documents."""

from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from dataclasses import fields
from datetime import UTC, datetime
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Protocol, runtime_checkable
from uuid import UUID

from .errors import DocumentSerializationError, DocumentValidationError


DOCUMENT_SCHEMA_VERSION = "1.0"
DOCUMENT_VERSION = "1.0.0"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def text(value: object, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise DocumentValidationError(f"{name} must be a non-empty string")
    return value.strip()


def instant(value: object, name: str, *, optional: bool = False) -> datetime | None:
    if value is None and optional:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise DocumentValidationError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def parse_instant(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise DocumentSerializationError(f"{name} must be an ISO-8601 string")
    try:
        result = instant(datetime.fromisoformat(value), name)
    except (ValueError, DocumentValidationError) as error:
        raise DocumentSerializationError(f"{name} must be an ISO-8601 UTC instant") from error
    assert isinstance(result, datetime)
    return result


def sha256(value: object, name: str = "sha256", *, optional: bool = False) -> str | None:
    normalized = text(value, name, optional=optional)
    if normalized is None:
        return None
    lowered = normalized.lower()
    if _SHA256.fullmatch(lowered) is None:
        raise DocumentValidationError(f"{name} must be a SHA-256 hexadecimal digest")
    return lowered


def probability(value: object, name: str, *, optional: bool = True) -> float | None:
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DocumentValidationError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise DocumentValidationError(f"{name} must be between 0 and 1")
    return result


def non_negative(value: object, name: str, *, optional: bool = True) -> int | None:
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DocumentValidationError(f"{name} must be a non-negative integer")
    return value


def unique_texts(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        raise DocumentValidationError(f"{name} must be a sequence")
    result = tuple(text(item, name) for item in value)
    if len(result) != len(set(result)):
        raise DocumentValidationError(f"{name} must not contain duplicates")
    return result  # type: ignore[return-value]


def model_sequence(value: object, name: str, expected: type) -> tuple:
    if not isinstance(value, (tuple, list)):
        raise DocumentValidationError(f"{name} must be a sequence")
    result = tuple(value)
    if any(not isinstance(item, expected) for item in result):
        raise DocumentValidationError(f"{name} contains an invalid model")
    return result


def deep_freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str, Enum, DocumentModel)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise DocumentValidationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            normalized = text(key, "mapping key")
            assert isinstance(normalized, str)
            if normalized in frozen:
                raise DocumentValidationError("mapping keys must be unique")
            frozen[normalized] = deep_freeze(item)
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list)):
        return tuple(deep_freeze(item) for item in value)
    raise DocumentValidationError(f"unsupported immutable value: {type(value).__name__}")


def primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        normalized = instant(value, "datetime")
        assert isinstance(normalized, datetime)
        return normalized.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, DocumentModel):
        return value.to_dict()
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            raise DocumentSerializationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        return {str(key): primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [primitive(item) for item in value]
    raise DocumentSerializationError(f"unsupported serialized value: {type(value).__name__}")


class DocumentModel(ABC):
    """Base behavior shared by every document model."""

    __slots__ = ()
    discriminator: ClassVar[str]
    schema_version: str

    @property
    def model(self) -> str:
        return self.discriminator

    def _validate_schema(self) -> None:
        if self.schema_version != DOCUMENT_SCHEMA_VERSION:
            raise DocumentValidationError(f"unsupported {self.discriminator} schema_version")

    def to_dict(self) -> dict[str, object]:
        payload = {
            item.name: primitive(getattr(self, item.name))
            for item in fields(self)
            if item.name != "schema_version"
        }
        return {"schema_version": self.schema_version, "model": self.model, **payload}


def strict(payload: object, model: str, names: set[str]) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise DocumentSerializationError(f"{model} must be an object")
    if set(payload) != names | {"model", "schema_version"}:
        raise DocumentSerializationError(f"invalid or unknown {model} fields")
    if payload.get("model") != model:
        raise DocumentSerializationError(f"invalid {model} discriminator")
    if payload.get("schema_version") != DOCUMENT_SCHEMA_VERSION:
        raise DocumentSerializationError(f"unsupported {model} schema_version")
    return payload


@runtime_checkable
class DocumentSerializer(Protocol):
    def serialize(self, value: DocumentModel) -> bytes:
        raise NotImplementedError

    def deserialize(self, payload: bytes | str) -> DocumentModel:
        raise NotImplementedError

    def digest(self, value: DocumentModel) -> str:
        raise NotImplementedError


@runtime_checkable
class DocumentValidatorContract(Protocol):
    def validate(self, value: DocumentModel) -> None:
        raise NotImplementedError


__all__ = [
    "DOCUMENT_SCHEMA_VERSION", "DOCUMENT_VERSION", "DocumentModel",
    "DocumentSerializer", "DocumentValidatorContract", "deep_freeze", "instant",
    "model_sequence", "non_negative", "parse_instant", "primitive", "probability",
    "sha256", "strict", "text", "unique_texts",
]
