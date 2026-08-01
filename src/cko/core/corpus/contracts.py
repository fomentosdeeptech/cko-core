"""Contracts and canonical normalization primitives for knowledge corpora."""

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

from .errors import CorpusSerializationError, CorpusValidationError, CorpusVersionError

CORPUS_SCHEMA_VERSION = "1.0"
CORPUS_VERSION = "1.0.0"
CORPUS_SERIALIZATION_VERSION = "1.0"
_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def text(value: object, name: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise CorpusValidationError(f"{name} must be a non-empty string")
    return value.strip()


def semantic_version(value: object, name: str = "version") -> str:
    result = text(value, name)
    assert isinstance(result, str)
    if not _SEMVER.fullmatch(result):
        raise CorpusVersionError(f"{name} must be a semantic version")
    return result


def non_negative(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CorpusValidationError(f"{name} must be a non-negative integer")
    return value


def instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise CorpusValidationError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def deep_freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str, UUID, Enum, CorpusModel)):
        return value
    if isinstance(value, datetime):
        return instant(value, "datetime")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CorpusValidationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen = {text(key, "mapping key"): deep_freeze(item) for key, item in value.items()}
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list, frozenset, set)):
        return tuple(deep_freeze(item) for item in value)
    raise CorpusValidationError(f"unsupported immutable value: {type(value).__name__}")


def primitive(value: object) -> object:
    if isinstance(value, CorpusModel):
        return value.to_dict()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return instant(value, "datetime").isoformat()
    if isinstance(value, UUID):
        return str(value)
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CorpusSerializationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        return {str(key): primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [primitive(item) for item in value]
    raise CorpusSerializationError(f"unsupported serialized value: {type(value).__name__}")


class CorpusModel(ABC):
    __slots__ = ()
    discriminator: ClassVar[str]
    schema_version: str

    @property
    def model(self) -> str:
        return self.discriminator

    def _validate_schema(self) -> None:
        if self.schema_version != CORPUS_SCHEMA_VERSION:
            raise CorpusVersionError(f"unsupported {self.discriminator} schema_version")

    def to_dict(self) -> dict[str, object]:
        data = {field.name: primitive(getattr(self, field.name))
                for field in fields(self) if field.name != "schema_version"}
        return {"schema_version": self.schema_version, "model": self.model, **data}


@runtime_checkable
class CorpusSerializer(Protocol):
    def serialize(self, value: CorpusModel) -> bytes: ...
    def deserialize(self, payload: bytes | str) -> CorpusModel: ...
    def digest(self, value: CorpusModel) -> str: ...


@runtime_checkable
class CorpusValidatorContract(Protocol):
    def validate(self, value: CorpusModel) -> None: ...


@runtime_checkable
class CorpusFactoryContract(Protocol):
    def create_corpus(self, *args, **kwargs): ...


@runtime_checkable
class CorpusBuilderContract(Protocol):
    def build(self, *args, **kwargs): ...


__all__ = [
    "CORPUS_SCHEMA_VERSION", "CORPUS_SERIALIZATION_VERSION", "CORPUS_VERSION",
    "CorpusBuilderContract", "CorpusFactoryContract", "CorpusModel",
    "CorpusSerializer", "CorpusValidatorContract", "deep_freeze", "instant",
    "non_negative", "primitive", "semantic_version", "text",
]
