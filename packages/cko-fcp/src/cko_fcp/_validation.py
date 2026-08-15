"""Strict, side-effect-free validation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import NoReturn

from .errors import ValidationError


def fail(message: str, error_type: type[ValidationError] = ValidationError) -> NoReturn:
    raise error_type(message)


def text(value: object, field: str, error_type: type[ValidationError] = ValidationError) -> str:
    if type(value) is not str or not value or value != value.strip():
        fail(f"{field} must be a non-empty, trimmed string", error_type)
    if any(ord(char) < 32 for char in value):
        fail(f"{field} contains a control character", error_type)
    return value


def optional_text(value: object, field: str, error_type: type[ValidationError] = ValidationError) -> str | None:
    if value is None:
        return None
    return text(value, field, error_type)


def string_tuple(
    value: object,
    field: str,
    *,
    allow_empty: bool = True,
    error_type: type[ValidationError] = ValidationError,
) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        fail(f"{field} must be an array", error_type)
    result = tuple(text(item, field, error_type) for item in value)
    if not allow_empty and not result:
        fail(f"{field} must not be empty", error_type)
    if len(result) != len(set(result)):
        fail(f"{field} must contain unique values", error_type)
    return tuple(sorted(result))


def instant(value: object, field: str, error_type: type[ValidationError] = ValidationError) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        fail(f"{field} must be a timezone-aware datetime", error_type)
    return value.astimezone(timezone.utc)


def strict_mapping(
    value: object,
    required: set[str],
    optional: set[str],
    context: str,
    error_type: type[ValidationError] = ValidationError,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        fail(f"{context} must be an object", error_type)
    keys = set(value)
    missing = required - keys
    unknown = keys - required - optional
    if missing:
        fail(f"{context} missing fields: {', '.join(sorted(missing))}", error_type)
    if unknown:
        fail(f"{context} unknown fields: {', '.join(sorted(unknown))}", error_type)
    if any(type(key) is not str for key in value):
        fail(f"{context} field names must be strings", error_type)
    return value
