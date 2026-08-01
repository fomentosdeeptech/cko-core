"""Errors raised by the cost-based query planner foundation."""

from cko.core.exceptions import CKOError


class PlannerError(CKOError, ValueError):
    """Base error for deterministic query planning."""


class InvalidPlannerModelError(PlannerError):
    """Raised when a planner model violates its canonical invariants."""


class PlanningError(PlannerError):
    """Raised when no coherent execution strategy can be planned."""


class PlannerValidationError(PlannerError):
    """Raised when an execution plan violates its planner policy."""


__all__ = [
    "InvalidPlannerModelError",
    "PlannerError",
    "PlannerValidationError",
    "PlanningError",
]
