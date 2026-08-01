"""Contracts and normalization primitives for canonical query models."""

from __future__ import annotations

import math
import re
from abc import ABC
from dataclasses import fields
from datetime import UTC, datetime
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Protocol, runtime_checkable
from uuid import UUID

from .errors import QuerySerializationError, QueryValidationError


QUERY_SCHEMA_VERSION = "1.0"
QUERY_VERSION = "1.0.0"
_SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


def text(value: object, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise QueryValidationError(f"{name} must be a non-empty string")
    return value.strip()


def semantic_version(value: object, name: str = "version") -> str:
    normalized = text(value, name)
    assert isinstance(normalized, str)
    if _SEMVER.fullmatch(normalized) is None:
        raise QueryValidationError(f"{name} must be a semantic version")
    return normalized


def instant(value: object, name: str, *, optional: bool = False) -> datetime | None:
    if value is None and optional:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise QueryValidationError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def parse_instant(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise QuerySerializationError(f"{name} must be an ISO-8601 string")
    try:
        normalized = instant(datetime.fromisoformat(value), name)
    except (ValueError, QueryValidationError) as error:
        raise QuerySerializationError(f"{name} must be an ISO-8601 UTC instant") from error
    assert isinstance(normalized, datetime)
    return normalized


def non_negative_int(value: object, name: str, *, optional: bool = False) -> int | None:
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise QueryValidationError(f"{name} must be a non-negative integer")
    return value


def finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QueryValidationError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise QueryValidationError(f"{name} must be a finite number")
    return result


def model_sequence(value: object, name: str, expected: type) -> tuple:
    if not isinstance(value, (tuple, list)):
        raise QueryValidationError(f"{name} must be a sequence")
    result = tuple(value)
    if any(not isinstance(item, expected) for item in result):
        raise QueryValidationError(f"{name} contains an invalid model")
    return result


def unique_texts(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        raise QueryValidationError(f"{name} must be a sequence")
    result = tuple(text(item, name) for item in value)
    if len(result) != len(set(result)):
        raise QueryValidationError(f"{name} must not contain duplicates")
    return result  # type: ignore[return-value]


def deep_freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str, UUID, Enum, QueryModel)):
        return value
    if isinstance(value, datetime):
        return instant(value, "datetime")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise QueryValidationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            normalized = text(key, "mapping key")
            assert isinstance(normalized, str)
            if normalized in frozen:
                raise QueryValidationError("mapping keys must be unique")
            frozen[normalized] = deep_freeze(item)
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list)):
        return tuple(deep_freeze(item) for item in value)
    raise QueryValidationError(f"unsupported immutable value: {type(value).__name__}")


def primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        normalized = instant(value, "datetime")
        assert isinstance(normalized, datetime)
        return normalized.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, QueryModel):
        return value.to_dict()
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            raise QuerySerializationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        return {str(key): query_value_primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [primitive(item) for item in value]
    raise QuerySerializationError(f"unsupported serialized value: {type(value).__name__}")


def query_value_primitive(value: object) -> object:
    """Encode open constraint values without losing canonical scalar types."""
    if isinstance(value, datetime):
        normalized = instant(value, "datetime")
        assert isinstance(normalized, datetime)
        return {"__query_scalar__": "datetime", "value": normalized.isoformat()}
    if isinstance(value, UUID):
        return {"__query_scalar__": "uuid", "value": str(value)}
    if isinstance(value, Enum):
        return {"__query_scalar__": "enum", "value": value.value}
    if isinstance(value, QueryModel):
        return value.to_dict()
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            raise QuerySerializationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        return {str(key): query_value_primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [query_value_primitive(item) for item in value]
    raise QuerySerializationError(f"unsupported query value: {type(value).__name__}")


class QueryModel(ABC):
    __slots__ = ()
    discriminator: ClassVar[str]
    schema_version: str

    @property
    def model(self) -> str:
        return self.discriminator

    def _validate_schema(self) -> None:
        if self.schema_version != QUERY_SCHEMA_VERSION:
            raise QueryValidationError(f"unsupported {self.discriminator} schema_version")

    def to_dict(self) -> dict[str, object]:
        payload = {
            item.name: primitive(getattr(self, item.name))
            for item in fields(self)
            if item.name != "schema_version"
        }
        return {"schema_version": self.schema_version, "model": self.model, **payload}


def strict(payload: object, model: str, names: set[str]) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise QuerySerializationError(f"{model} must be an object")
    if set(payload) != names | {"model", "schema_version"}:
        raise QuerySerializationError(f"invalid or unknown {model} fields")
    if payload.get("model") != model:
        raise QuerySerializationError(f"invalid {model} discriminator")
    if payload.get("schema_version") != QUERY_SCHEMA_VERSION:
        raise QuerySerializationError(f"unsupported {model} schema_version")
    return payload


@runtime_checkable
class QuerySerializer(Protocol):
    def serialize(self, value: QueryModel) -> bytes:
        raise NotImplementedError

    def deserialize(self, payload: bytes | str) -> QueryModel:
        raise NotImplementedError

    def digest(self, value: QueryModel) -> str:
        raise NotImplementedError


@runtime_checkable
class QueryValidatorContract(Protocol):
    def validate(self, value: QueryModel) -> None:
        raise NotImplementedError


__all__ = [
    "QUERY_SCHEMA_VERSION", "QUERY_VERSION", "QueryModel", "QuerySerializer",
    "QueryValidatorContract", "deep_freeze", "finite_number", "instant",
    "model_sequence", "non_negative_int", "parse_instant", "primitive",
    "query_value_primitive",
    "semantic_version", "strict", "text", "unique_texts",
]
