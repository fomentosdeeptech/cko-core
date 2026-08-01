"""Private normalization and canonical-value contracts."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, TypeVar
from uuid import UUID

from .constants import PROVENANCE_SCHEMA_VERSION, PROVENANCE_SERIALIZATION_VERSION
from .errors import (
    ProvenanceDigestError,
    ProvenanceValidationError,
    ProvenanceVersionError,
)


_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_SEMVER = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_MAX_INTEGER = 9_007_199_254_740_991
E = TypeVar("E", bound=Enum)


def validation(code: str, model: str, field: str, detail: str) -> ProvenanceValidationError:
    return ProvenanceValidationError(code, model, field, detail)


def require_versions(schema_version: str, serialization_version: str, model: str) -> None:
    if schema_version != PROVENANCE_SCHEMA_VERSION or serialization_version != PROVENANCE_SERIALIZATION_VERSION:
        raise validation("PV005", model, "version", "unsupported schema or serialization version")


def text(value: object, field: str, model: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str):
        raise validation("PV001", model, field, "must be string")
    normalized = unicodedata.normalize("NFC", value).strip()
    if not normalized or _CONTROL.search(normalized):
        raise validation("PV002", model, field, "must be non-empty and contain no controls")
    return normalized


def value_text(value: object, field: str, model: str) -> str:
    if not isinstance(value, str):
        raise validation("PV001", model, field, "must be string")
    try:
        normalized = unicodedata.normalize("NFC", value)
        normalized.encode("utf-8", "strict")
    except (UnicodeError, TypeError) as error:
        raise validation("PV007", model, field, "must be valid Unicode") from error
    return normalized


def enum_value(value: object, enum_type: type[E], field: str, model: str) -> E:
    if not isinstance(value, enum_type):
        raise validation("PV003", model, field, f"must be {enum_type.__name__}")
    return value


def uuid_value(value: object, field: str, model: str, *, version_five: bool = False) -> UUID:
    if not isinstance(value, UUID):
        raise validation("PV001", model, field, "must be UUID")
    if version_five and (value.version != 5 or value.variant != "specified in RFC 4122"):
        from .errors import ProvenanceIdentityError
        raise ProvenanceIdentityError("PI001", model, field, "must be RFC 4122 UUIDv5")
    return value


def semver(value: object, field: str, model: str) -> str:
    if not isinstance(value, str) or not _SEMVER.fullmatch(value):
        raise ProvenanceVersionError("PR001", model, field, "must be canonical SemVer")
    return value


def sha256(value: object, field: str, model: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ProvenanceDigestError("PD001", model, field, "must be lowercase SHA-256")
    return value


def positive_int(value: object, field: str, model: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ProvenanceVersionError("PR001", model, field, "must be positive integer")
    return value


def instant(value: object, field: str, model: str, *, optional: bool = False) -> datetime | None:
    if value is None and optional:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise validation("PV006", model, field, "must be timezone-aware datetime")
    return value.astimezone(UTC)


def instant_text(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_instant(value: object, field: str, model: str) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z", value):
        raise validation("PV006", model, field, "must be canonical UTC instant")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise validation("PV006", model, field, "must be canonical UTC instant") from error


@dataclass(frozen=True, slots=True)
class _CanonicalArray:
    values: tuple[CanonicalValue, ...]


@dataclass(frozen=True, slots=True)
class _CanonicalObject:
    entries: tuple[tuple[str, CanonicalValue], ...]


CanonicalValue = None | bool | int | str | _CanonicalArray | _CanonicalObject
CanonicalJSON = None | bool | int | str | list["CanonicalJSON"] | dict[str, "CanonicalJSON"]


def canonical_value(value: object, field: str = "value", model: str = "provenance_qualifier") -> CanonicalValue:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        if not -_MAX_INTEGER <= value <= _MAX_INTEGER:
            raise validation("PV007", model, field, "integer is outside canonical range")
        return value
    if isinstance(value, str):
        return value_text(value, field, model)
    if isinstance(value, list):
        return _CanonicalArray(tuple(canonical_value(item, field, model) for item in value))
    if isinstance(value, Mapping):
        entries: list[tuple[str, CanonicalValue]] = []
        seen: set[str] = set()
        for key, item in value.items():
            if not isinstance(key, str):
                raise validation("PV007", model, field, "object keys must be strings")
            normalized = value_text(key, field, model)
            if normalized in seen:
                raise validation("PV004", model, field, "duplicate key after NFC")
            seen.add(normalized)
            entries.append((normalized, canonical_value(item, field, model)))
        return _CanonicalObject(tuple(sorted(entries)))
    if isinstance(value, (_CanonicalArray, _CanonicalObject)):
        return value
    if isinstance(value, (tuple, float, Decimal, bytes, bytearray, datetime, set, frozenset)):
        raise validation("PV007", model, field, "type is not a CanonicalValue")
    raise validation("PV007", model, field, "type is not a CanonicalValue")


def canonical_primitive(value: CanonicalValue) -> CanonicalJSON:
    if isinstance(value, _CanonicalArray):
        return [canonical_primitive(item) for item in value.values]
    if isinstance(value, _CanonicalObject):
        return {key: canonical_primitive(item) for key, item in value.entries}
    return value


def canonical_json(value: CanonicalJSON) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8", "strict")
    except (TypeError, ValueError, UnicodeError) as error:
        raise validation("PV007", "canonical_json", "value", "cannot be encoded canonically") from error


def model_tuple(value: object, expected: type, field: str, model: str, *, sort_key=None) -> tuple:
    if not isinstance(value, (tuple, list)):
        raise validation("PV001", model, field, "must be a sequence")
    result = tuple(value)
    if any(not isinstance(item, expected) for item in result):
        raise validation("PV001", model, field, f"must contain {expected.__name__}")
    return tuple(sorted(result, key=sort_key)) if sort_key is not None else result


def unique(values: tuple, key, field: str, model: str) -> None:
    tokens = tuple(key(item) for item in values)
    if len(tokens) != len(set(tokens)):
        raise validation("PV004", model, field, "contains duplicate values")
