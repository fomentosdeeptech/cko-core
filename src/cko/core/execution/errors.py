"""Errors raised by the canonical execution-engine foundation."""

from cko.core.exceptions import CKOError


class ExecutionEngineError(CKOError, ValueError):
    """Base error for deterministic logical execution."""


class InvalidExecutionEngineModelError(ExecutionEngineError):
    """Raised when an execution-engine model violates its contract."""


class ExecutionEngineValidationError(ExecutionEngineError):
    """Raised when a plan, context, state, or operator is invalid."""


class ExecutionOperatorError(ExecutionEngineError):
    """Raised when a canonical operator cannot execute its logical contract."""


class ExecutionPipelineError(ExecutionEngineError):
    """Raised when deterministic tree traversal cannot be completed."""


__all__ = [
    "ExecutionEngineError", "ExecutionEngineValidationError",
    "ExecutionOperatorError", "ExecutionPipelineError",
    "InvalidExecutionEngineModelError",
]
