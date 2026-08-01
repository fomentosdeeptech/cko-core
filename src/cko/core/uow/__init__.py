"""Canonical Unit of Work foundation for the CKO CORE SDK."""

from .contracts import RepositoryCollection, UnitOfWork
from .engine import DefaultUnitOfWork
from .errors import (
    UnitOfWorkClosedError,
    UnitOfWorkException,
    UnitOfWorkExecutionError,
    UnitOfWorkRegistrationError,
    UnitOfWorkRollbackError,
    UnitOfWorkStateError,
    UnitOfWorkValidationError,
)
from .models import (
    UOW_SCHEMA_VERSION,
    UOW_VERSION,
    UnitOfWorkAction,
    UnitOfWorkCompensation,
    UnitOfWorkContext,
    UnitOfWorkOperation,
    UnitOfWorkRepository,
    UnitOfWorkResult,
    UnitOfWorkState,
)
from .validator import UnitOfWorkValidator


__all__ = [
    "UOW_SCHEMA_VERSION",
    "UOW_VERSION",
    "DefaultUnitOfWork",
    "RepositoryCollection",
    "UnitOfWork",
    "UnitOfWorkAction",
    "UnitOfWorkClosedError",
    "UnitOfWorkCompensation",
    "UnitOfWorkContext",
    "UnitOfWorkException",
    "UnitOfWorkExecutionError",
    "UnitOfWorkOperation",
    "UnitOfWorkRegistrationError",
    "UnitOfWorkRepository",
    "UnitOfWorkResult",
    "UnitOfWorkRollbackError",
    "UnitOfWorkState",
    "UnitOfWorkStateError",
    "UnitOfWorkValidationError",
    "UnitOfWorkValidator",
]
