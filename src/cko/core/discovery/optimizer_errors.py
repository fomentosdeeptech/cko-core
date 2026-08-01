"""Errors raised by the canonical query optimizer foundation."""

from cko.core.exceptions import CKOError


class OptimizerError(CKOError, ValueError):
    """Base error for deterministic logical query optimization."""


class InvalidOptimizerModelError(OptimizerError):
    """Raised when an optimizer model violates its invariants."""


class OptimizationError(OptimizerError):
    """Raised when a query plan cannot be optimized safely."""


class OptimizerValidationError(OptimizerError):
    """Raised when an optimized plan fails semantic validation."""


__all__ = [
    "InvalidOptimizerModelError",
    "OptimizationError",
    "OptimizerError",
    "OptimizerValidationError",
]
