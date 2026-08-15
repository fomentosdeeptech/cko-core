"""Canonical JSON serialization independent of locale, clock, and environment."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from collections.abc import Mapping

from .errors import ContractViolationError


def _canonical(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ContractViolationError("naive datetime cannot be serialized")
        normalized = value.astimezone(timezone.utc)
        text = normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")
        return text
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise ContractViolationError("object keys must be strings")
        return {key: _canonical(value[key]) for key in sorted(value)}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise ContractViolationError(f"unsupported canonical type: {type(value).__name__}")


def canonical_json(value: object) -> str:
    return json.dumps(_canonical(value), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: object) -> bytes:
    return canonical_json(value).encode("utf-8")


def canonical_digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()
