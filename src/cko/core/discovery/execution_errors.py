"""Public errors for canonical physical execution planning."""

from cko.core.exceptions import CKOError


class ExecutionPlannerError(CKOError, ValueError):
    """Base error raised by the execution-planning foundation."""


class InvalidExecutionModelError(ExecutionPlannerError):
    """Raised when an execution model violates its canonical contract."""


class ExecutionPlanningError(ExecutionPlannerError):
    """Raised when a physical plan cannot be built safely."""


class ExecutionValidationError(ExecutionPlannerError):
    """Raised when a physical execution plan is structurally invalid."""


__all__ = [
    "ExecutionPlannerError", "ExecutionPlanningError",
    "ExecutionValidationError", "InvalidExecutionModelError",
]
