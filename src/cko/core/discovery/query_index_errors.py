"""Errors raised by the logical Discovery query index foundation."""

from __future__ import annotations

from cko.core.exceptions import CKOError


class LogicalIndexError(CKOError, ValueError):
    """Base error for invalid logical index operations and models."""


class InvalidLogicalIndexError(LogicalIndexError):
    """Raised when a logical index or entry violates its contract."""


class InvalidLogicalIndexPolicyError(LogicalIndexError):
    """Raised when a logical index policy is internally inconsistent."""


class LogicalIndexValidationError(LogicalIndexError):
    """Raised when validation detects inconsistent index content."""


class LogicalIndexResolutionError(LogicalIndexError):
    """Raised when index resolution receives invalid input."""


__all__ = [
    "InvalidLogicalIndexError",
    "InvalidLogicalIndexPolicyError",
    "LogicalIndexError",
    "LogicalIndexResolutionError",
    "LogicalIndexValidationError",
]
