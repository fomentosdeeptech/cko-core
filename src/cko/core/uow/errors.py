"""Typed errors for the canonical Unit of Work foundation."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import CKOError


class UnitOfWorkException(CKOError):
    """Base error for Unit of Work contracts and lifecycle operations."""

    default_code = "uow_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        unit_of_work_id: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        normalized = message.strip() if isinstance(message, str) else ""
        normalized_code = (
            self.default_code
            if code is None
            else code.strip() if isinstance(code, str) else ""
        )
        if not normalized:
            raise ValueError("message must be a non-empty string")
        if not normalized_code:
            raise ValueError("code must be a non-empty string")
        if unit_of_work_id is not None:
            unit_of_work_id = unit_of_work_id.strip()
            if not unit_of_work_id:
                raise ValueError(
                    "unit_of_work_id must be non-empty when provided"
                )
        if details is not None and not isinstance(details, Mapping):
            raise ValueError("details must be a mapping when provided")
        self.code = normalized_code
        self.unit_of_work_id = unit_of_work_id
        self.details = MappingProxyType(dict(details or {}))
        super().__init__(normalized)

    def to_dict(self) -> dict[str, object]:
        """Return a safe, serializable representation."""
        return {
            "code": self.code,
            "unit_of_work_id": self.unit_of_work_id,
            "message": str(self),
            "details": dict(self.details),
        }


class UnitOfWorkValidationError(UnitOfWorkException):
    """Report an invalid model, registration, context, or result."""

    default_code = "uow_validation_error"


class UnitOfWorkStateError(UnitOfWorkException):
    """Report an invalid lifecycle transition or duplicate terminal action."""

    default_code = "uow_state_error"


class UnitOfWorkRegistrationError(UnitOfWorkException):
    """Report an invalid, duplicate, or missing repository registration."""

    default_code = "uow_registration_error"


class UnitOfWorkExecutionError(UnitOfWorkException):
    """Report failure while executing a coordinated logical operation."""

    default_code = "uow_execution_error"


class UnitOfWorkRollbackError(UnitOfWorkException):
    """Report failure while compensating an executed operation."""

    default_code = "uow_rollback_error"


class UnitOfWorkClosedError(UnitOfWorkException):
    """Report an operation attempted after the Unit of Work was closed."""

    default_code = "uow_closed"


__all__ = [
    "UnitOfWorkClosedError",
    "UnitOfWorkException",
    "UnitOfWorkExecutionError",
    "UnitOfWorkRegistrationError",
    "UnitOfWorkRollbackError",
    "UnitOfWorkStateError",
    "UnitOfWorkValidationError",
]
