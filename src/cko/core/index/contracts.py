"""Contracts and canonical normalization primitives for indexes."""

from __future__ import annotations

import math
import re
from abc import ABC
from dataclasses import fields
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import ClassVar, Mapping, Protocol, runtime_checkable
from uuid import UUID

from .errors import IndexSerializationError, IndexValidationError

INDEX_SCHEMA_VERSION = "1.0"
INDEX_VERSION = "1.0.0"
_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def text(value: object, name: str, *, optional: bool=False, empty: bool=False) -> str | None:
    if value is None and optional: return None
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise IndexValidationError(f"{name} must be a {'string' if empty else 'non-empty string'}")
    return value.strip()


def semantic_version(value: object, name: str="version") -> str:
    result = text(value, name)
    assert isinstance(result, str)
    if not _SEMVER.fullmatch(result): raise IndexValidationError(f"{name} must be a semantic version")
    return result


def instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise IndexValidationError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def non_negative(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise IndexValidationError(f"{name} must be a non-negative integer")
    return value


def deep_freeze(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str, UUID, Enum, IndexModel)): return value
    if isinstance(value, datetime): return instant(value, "datetime")
    if isinstance(value, (float, Decimal)):
        if not value.is_finite() if isinstance(value, Decimal) else not math.isfinite(value):
            raise IndexValidationError("numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen = {text(key, "mapping key"): deep_freeze(item) for key, item in value.items()}
        return MappingProxyType(dict(sorted(frozen.items())))
    if isinstance(value, (tuple, list, frozenset, set)):
        return tuple(deep_freeze(item) for item in value)
    raise IndexValidationError(f"unsupported immutable value: {type(value).__name__}")


def primitive(value: object) -> object:
    if isinstance(value, IndexModel): return value.to_dict()
    if isinstance(value, Enum): return value.value
    if isinstance(value, datetime): return instant(value, "datetime").isoformat()
    if isinstance(value, UUID): return str(value)
    if isinstance(value, Decimal): return {"__index_scalar__":"decimal", "value":str(value)}
    if value is None or isinstance(value, (bool, int, str)): return value
    if isinstance(value, float):
        if not math.isfinite(value): raise IndexSerializationError("numbers must be finite")
        return value
    if isinstance(value, Mapping): return {str(k): primitive(v) for k,v in sorted(value.items())}
    if isinstance(value, (tuple, list)): return [primitive(v) for v in value]
    raise IndexSerializationError(f"unsupported serialized value: {type(value).__name__}")


class IndexModel(ABC):
    __slots__=()
    discriminator: ClassVar[str]
    schema_version: str
    @property
    def model(self) -> str: return self.discriminator
    def _validate_schema(self) -> None:
        if self.schema_version != INDEX_SCHEMA_VERSION:
            raise IndexValidationError(f"unsupported {self.discriminator} schema_version")
    def to_dict(self) -> dict[str, object]:
        data={f.name:primitive(getattr(self,f.name)) for f in fields(self) if f.name != "schema_version"}
        return {"schema_version":self.schema_version,"model":self.model,**data}


@runtime_checkable
class IndexSerializer(Protocol):
    def serialize(self, value: IndexModel) -> bytes: ...
    def deserialize(self, payload: bytes | str) -> IndexModel: ...
    def digest(self, value: IndexModel) -> str: ...

@runtime_checkable
class IndexValidatorContract(Protocol):
    def validate(self, value: IndexModel) -> None: ...

@runtime_checkable
class IndexFactoryContract(Protocol):
    def create_index(self, *args, **kwargs): ...

@runtime_checkable
class IndexBuilderContract(Protocol):
    def build(self, *args, **kwargs): ...

@runtime_checkable
class IndexStatisticsProvider(Protocol):
    def calculate(self, index): ...

@runtime_checkable
class IndexOperationExecutor(Protocol):
    def execute(self, index, operation): ...

@runtime_checkable
class IndexReader(Protocol):
    def read(self, index, query): ...


__all__=["INDEX_SCHEMA_VERSION","INDEX_VERSION","IndexBuilderContract",
         "IndexFactoryContract","IndexModel","IndexOperationExecutor","IndexReader",
         "IndexSerializer","IndexStatisticsProvider","IndexValidatorContract",
         "deep_freeze","instant","non_negative","primitive","semantic_version","text"]
