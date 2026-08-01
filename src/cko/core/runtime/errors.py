"""Canonical errors raised by the infrastructure-free Runtime foundation."""

from cko.core.exceptions import CKOError


class RuntimeErrorBase(CKOError):
    """Base error for every canonical Runtime failure."""


class InvalidRuntimeModelError(RuntimeErrorBase, ValueError):
    """Raised when a Runtime model violates its canonical contract."""


class RuntimeLifecycleError(RuntimeErrorBase, ValueError):
    """Raised when a Runtime lifecycle transition is not allowed."""


class RuntimeValidationError(RuntimeErrorBase, ValueError):
    """Raised when Runtime integrity validation fails."""


class RuntimeCancellationError(RuntimeErrorBase):
    """Raised when cooperative Runtime cancellation is observed."""


class ResourceRegistryError(RuntimeErrorBase, ValueError):
    """Raised when a logical Runtime resource operation is invalid."""


__all__ = [
    "InvalidRuntimeModelError", "ResourceRegistryError", "RuntimeCancellationError",
    "RuntimeErrorBase", "RuntimeLifecycleError", "RuntimeValidationError",
]
