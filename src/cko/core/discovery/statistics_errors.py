"""Errors raised by the Discovery statistics and cost foundation."""

from __future__ import annotations

from cko.core.exceptions import CKOError


class StatisticsError(CKOError, ValueError):
    """Base error for statistics construction and estimation operations."""


class InvalidStatisticsError(StatisticsError):
    """Raised when a canonical statistics model is invalid."""


class InvalidStatisticsPolicyError(StatisticsError):
    """Raised when a statistics policy is internally inconsistent."""


class StatisticsValidationError(StatisticsError):
    """Raised when statistics or histogram invariants are inconsistent."""


class CostEstimationError(StatisticsError):
    """Raised when logical query cost cannot be estimated safely."""


__all__ = [
    "CostEstimationError",
    "InvalidStatisticsError",
    "InvalidStatisticsPolicyError",
    "StatisticsError",
    "StatisticsValidationError",
]
