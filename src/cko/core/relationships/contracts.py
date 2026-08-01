"""Contracts and normalization primitives for canonical relationships."""

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

from .errors import RelationshipSerializationError, RelationshipValidationError


RELATIONSHIP_SCHEMA_VERSION = "1.0"
RELATIONSHIP_VERSION = "1.0.0"
_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def text(value: object, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RelationshipValidationError(f"{name} must be a non-empty string")
    return value.strip()


def version(value: object, name: str = "version") -> str:
    normalized = text(value, name)
    assert isinstance(normalized, str)
    if _SEMVER.fullmatch(normalized) is None:
        raise RelationshipValidationError(f"{name} must be a semantic version")
    return normalized


def instant(value: object, name: str, *, optional: bool = False) -> datetime | None:
    if value is None and optional:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise RelationshipValidationError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def parse_instant(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise RelationshipSerializationError(f"{name} must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value)
        normalized = instant(parsed, name)
    except (ValueError, RelationshipValidationError) as error:
        raise RelationshipSerializationError(f"{name} must be an ISO-8601 UTC instant") from error
    assert isinstance(normalized, datetime)
    return normalized


def probability(value: object, name: str, *, optional: bool = True) -> float | None:
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RelationshipValidationError(f"{name} must be a finite number")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise RelationshipValidationError(f"{name} must be between 0 and 1")
    return normalized


def non_negative(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RelationshipValidationError(f"{name} must be a non-negative integer")
    return value


def deep_freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str, UUID, datetime, Enum, RelationshipModel)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise RelationshipValidationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            normalized = text(key, "mapping key")
            assert isinstance(normalized, str)
            if normalized in frozen:
                raise RelationshipValidationError("mapping keys must be unique")
            frozen[normalized] = deep_freeze(item)
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list)):
        return tuple(deep_freeze(item) for item in value)
    raise RelationshipValidationError(f"unsupported immutable value: {type(value).__name__}")


def model_sequence(value: object, name: str, expected: type) -> tuple:
    if not isinstance(value, (tuple, list)):
        raise RelationshipValidationError(f"{name} must be a sequence")
    result = tuple(value)
    if any(not isinstance(item, expected) for item in result):
        raise RelationshipValidationError(f"{name} contains an invalid model")
    return result


def primitive(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        normalized = instant(value, "datetime")
        assert isinstance(normalized, datetime)
        return normalized.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, RelationshipModel):
        return value.to_dict()
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            raise RelationshipSerializationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        return {str(key): primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [primitive(item) for item in value]
    raise RelationshipSerializationError(f"unsupported serialized value: {type(value).__name__}")


class RelationshipModel(ABC):
    """Shared deterministic behavior for every relationship model."""

    __slots__ = ()
    discriminator: ClassVar[str]
    schema_version: str

    @property
    def model(self) -> str:
        return self.discriminator

    def _validate_schema(self) -> None:
        if self.schema_version != RELATIONSHIP_SCHEMA_VERSION:
            raise RelationshipValidationError(f"unsupported {self.discriminator} schema_version")

    def to_dict(self) -> dict[str, object]:
        payload = {
            field.name: primitive(getattr(self, field.name))
            for field in fields(self)
            if field.name != "schema_version"
        }
        return {"schema_version": self.schema_version, "model": self.model, **payload}


def strict(payload: object, model: str, names: set[str]) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise RelationshipSerializationError(f"{model} must be an object")
    if set(payload) != names | {"model", "schema_version"}:
        raise RelationshipSerializationError(f"invalid or unknown {model} fields")
    if payload.get("model") != model:
        raise RelationshipSerializationError(f"invalid {model} discriminator")
    if payload.get("schema_version") != RELATIONSHIP_SCHEMA_VERSION:
        raise RelationshipSerializationError(f"unsupported {model} schema_version")
    return payload


@runtime_checkable
class RelationshipSerializer(Protocol):
    def serialize(self, value: RelationshipModel) -> bytes:
        raise NotImplementedError

    def deserialize(self, payload: bytes | str) -> RelationshipModel:
        raise NotImplementedError

    def digest(self, value: RelationshipModel) -> str:
        raise NotImplementedError


@runtime_checkable
class RelationshipValidatorContract(Protocol):
    def validate(self, value: RelationshipModel) -> None:
        raise NotImplementedError


__all__ = [
    "RELATIONSHIP_SCHEMA_VERSION", "RELATIONSHIP_VERSION", "RelationshipModel",
    "RelationshipSerializer", "RelationshipValidatorContract", "deep_freeze",
    "instant", "model_sequence", "non_negative", "parse_instant", "primitive",
    "probability", "strict", "text", "version",
]
