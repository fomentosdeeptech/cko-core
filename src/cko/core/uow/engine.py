"""Default provider-neutral Unit of Work coordinator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Iterable
from uuid import uuid4

from cko.core.logging import get_logger

from .contracts import UnitOfWork
from .errors import (
    UnitOfWorkClosedError,
    UnitOfWorkExecutionError,
    UnitOfWorkRegistrationError,
    UnitOfWorkRollbackError,
    UnitOfWorkStateError,
)
from .models import (
    UnitOfWorkContext,
    UnitOfWorkOperation,
    UnitOfWorkRepository,
    UnitOfWorkResult,
    UnitOfWorkState,
)
from .validator import UnitOfWorkValidator


_LOGGER = get_logger("core.uow")


class DefaultUnitOfWork(UnitOfWork):
    """Coordinate public CKO ports through a logical transaction lifecycle."""

    def __init__(
        self,
        repositories: Iterable[UnitOfWorkRepository] = (),
        context: UnitOfWorkContext | None = None,
        validator: UnitOfWorkValidator | None = None,
        *,
        clock: Callable[[], datetime] | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._validator = validator or UnitOfWorkValidator()
        if not isinstance(self._validator, UnitOfWorkValidator):
            raise TypeError("validator must be UnitOfWorkValidator")
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._id_factory = id_factory or (lambda: uuid4().hex)
        generated_id = self._identifier(self._id_factory())
        if context is None:
            context = UnitOfWorkContext(
                unit_of_work_id=generated_id,
                correlation_id=generated_id,
            )
        else:
            self._validator.validate_context(context)
            generated_id = context.unit_of_work_id
        self._context = context
        normalized = self._validator.validate_repositories(repositories)
        self._repositories = {
            repository.identifier: repository for repository in normalized
        }
        self._state = UnitOfWorkState.CREATED
        self._history: list[UnitOfWorkResult] = []
        self._executed: list[tuple[UnitOfWorkOperation, object]] = []
        self._operation_ids: set[str] = set()
        self._executing = False
        self._record("uow_created")
        self._log("uow_created")

    @property
    def context(self) -> UnitOfWorkContext:
        """Return the immutable logical context."""
        return self._context

    @property
    def repositories(self) -> tuple[UnitOfWorkRepository, ...]:
        """Return registrations in deterministic insertion order."""
        return tuple(self._repositories.values())

    def begin(
        self, context: UnitOfWorkContext | None = None
    ) -> UnitOfWorkResult:
        """Start this Unit of Work exactly once."""
        self._ensure_not_executing()
        if context is not None:
            self._validator.validate_context(context)
            if context.unit_of_work_id != self._context.unit_of_work_id:
                raise UnitOfWorkStateError(
                    "context unit_of_work_id cannot change"
                )
            self._context = context
        self._transition(UnitOfWorkState.STARTED)
        result = self._record("uow_started")
        self._log("uow_started")
        return result

    def register(
        self, repository: UnitOfWorkRepository
    ) -> UnitOfWorkRepository:
        """Register one unique public port before or during execution."""
        self._ensure_mutable()
        normalized = self._validator.validate_repository(repository)
        if normalized.identifier in self._repositories:
            raise UnitOfWorkRegistrationError(
                "repository identifier is already registered",
                unit_of_work_id=self._context.unit_of_work_id,
            )
        if any(
            item.repository is normalized.repository
            for item in self._repositories.values()
        ):
            raise UnitOfWorkRegistrationError(
                "repository instance is already registered",
                unit_of_work_id=self._context.unit_of_work_id,
            )
        self._repositories[normalized.identifier] = normalized
        self._record(
            "uow_registered",
            repository_id=normalized.identifier,
            metadata={"kind": normalized.kind},
        )
        self._log(
            "uow_registered",
            repository_id=normalized.identifier,
            kind=normalized.kind,
        )
        return normalized

    def unregister(self, identifier: str) -> UnitOfWorkRepository:
        """Remove one registration when no operation is executing."""
        self._ensure_mutable()
        normalized = self._identifier(identifier)
        if any(
            operation.repository_id == normalized
            for operation, _ in self._executed
        ):
            raise UnitOfWorkRegistrationError(
                "repository has executed operations pending resolution",
                unit_of_work_id=self._context.unit_of_work_id,
                details={"repository_id": normalized},
            )
        try:
            return self._repositories.pop(normalized)
        except KeyError as error:
            raise UnitOfWorkRegistrationError(
                "repository is not registered",
                unit_of_work_id=self._context.unit_of_work_id,
                details={"repository_id": normalized},
            ) from error

    def clear(self) -> int:
        """Remove all registrations when lifecycle mutation is allowed."""
        self._ensure_mutable()
        if self._executed:
            raise UnitOfWorkRegistrationError(
                "registrations have executed operations pending resolution",
                unit_of_work_id=self._context.unit_of_work_id,
            )
        count = len(self._repositories)
        self._repositories.clear()
        return count

    def execute(
        self, operation: UnitOfWorkOperation
    ) -> UnitOfWorkResult:
        """Execute a logical action with automatic rollback on failure."""
        self._require_started()
        if self._executing:
            raise UnitOfWorkStateError(
                "nested Unit of Work operations are not allowed",
                unit_of_work_id=self._context.unit_of_work_id,
            )
        normalized = self._validator.validate_operation(operation)
        if normalized.operation_id in self._operation_ids:
            raise UnitOfWorkExecutionError(
                "operation_id has already been executed",
                unit_of_work_id=self._context.unit_of_work_id,
            )
        registration = self._repositories.get(normalized.repository_id)
        if registration is None:
            raise UnitOfWorkRegistrationError(
                "operation references an unregistered repository",
                unit_of_work_id=self._context.unit_of_work_id,
                details={"repository_id": normalized.repository_id},
            )
        self._executing = True
        self._operation_ids.add(normalized.operation_id)
        try:
            value = normalized.action(
                registration.repository,
                self._context,
            )
            if hasattr(value, "success") and value.success is False:
                raise UnitOfWorkExecutionError(
                    "public port returned an unsuccessful result",
                    unit_of_work_id=self._context.unit_of_work_id,
                    details={"operation_id": normalized.operation_id},
                )
            self._executed.append((normalized, value))
            return self._record(
                "uow_operation",
                operation_id=normalized.operation_id,
                repository_id=normalized.repository_id,
                value=value,
            )
        except Exception as error:
            failure = (
                error
                if isinstance(error, UnitOfWorkExecutionError)
                else UnitOfWorkExecutionError(
                    "Unit of Work operation failed",
                    unit_of_work_id=self._context.unit_of_work_id,
                    details={"operation_id": normalized.operation_id},
                )
            )
            self._state = UnitOfWorkState.FAILED
            self._record(
                "uow_failed",
                success=False,
                operation_id=normalized.operation_id,
                repository_id=normalized.repository_id,
                error=failure,
            )
            self._log(
                "uow_failed",
                operation_id=normalized.operation_id,
                error_code=failure.code,
            )
            self._executing = False
            try:
                self.rollback()
            except UnitOfWorkRollbackError:
                raise
            if failure is error:
                raise failure
            raise failure from error
        finally:
            self._executing = False

    def commit(self) -> UnitOfWorkResult:
        """Commit the current logical transaction."""
        self._require_started()
        self._ensure_not_executing()
        self._transition(UnitOfWorkState.COMMITTED)
        result = self._record(
            "uow_commit",
            metadata={"operation_count": len(self._executed)},
        )
        self._log("uow_commit", operation_count=len(self._executed))
        return result

    def rollback(self) -> UnitOfWorkResult:
        """Compensate completed actions in strict reverse order."""
        self._ensure_not_executing()
        if self._state not in {
            UnitOfWorkState.STARTED,
            UnitOfWorkState.FAILED,
        }:
            if self._state is UnitOfWorkState.CLOSED:
                raise UnitOfWorkClosedError(
                    "Unit of Work is closed",
                    unit_of_work_id=self._context.unit_of_work_id,
                )
            raise UnitOfWorkStateError(
                "rollback requires a started or failed Unit of Work",
                unit_of_work_id=self._context.unit_of_work_id,
            )
        failures: list[tuple[str, Exception]] = []
        compensated = 0
        for operation, value in reversed(self._executed):
            if operation.compensation is None:
                continue
            registration = self._repositories.get(operation.repository_id)
            if registration is None:
                failures.append(
                    (
                        operation.operation_id,
                        UnitOfWorkRegistrationError(
                            "repository was removed before rollback"
                        ),
                    )
                )
                continue
            try:
                operation.compensation(
                    registration.repository,
                    value,
                    self._context,
                )
                compensated += 1
            except Exception as error:
                failures.append((operation.operation_id, error))
        if failures:
            self._state = UnitOfWorkState.FAILED
            failure = UnitOfWorkRollbackError(
                "one or more compensating operations failed",
                unit_of_work_id=self._context.unit_of_work_id,
                details={
                    "operation_ids": tuple(item[0] for item in failures),
                    "failure_count": len(failures),
                },
            )
            self._record("uow_failed", success=False, error=failure)
            self._log(
                "uow_failed",
                error_code=failure.code,
                failure_count=len(failures),
            )
            raise failure from failures[0][1]
        self._transition(UnitOfWorkState.ROLLED_BACK)
        result = self._record(
            "uow_rollback",
            metadata={
                "operation_count": len(self._executed),
                "compensated_count": compensated,
            },
        )
        self._log(
            "uow_rollback",
            operation_count=len(self._executed),
            compensated_count=compensated,
        )
        return result

    def status(self) -> UnitOfWorkState:
        """Return the current lifecycle state."""
        return self._state

    def history(self) -> tuple[UnitOfWorkResult, ...]:
        """Return an immutable ordered snapshot of lifecycle results."""
        return tuple(self._history)

    def close(self) -> UnitOfWorkResult:
        """Rollback active work, release registrations, and close."""
        self._ensure_not_executing()
        if self._state is UnitOfWorkState.CLOSED:
            raise UnitOfWorkClosedError(
                "Unit of Work is already closed",
                unit_of_work_id=self._context.unit_of_work_id,
            )
        rollback_error: UnitOfWorkRollbackError | None = None
        if self._state is UnitOfWorkState.STARTED:
            try:
                self.rollback()
            except UnitOfWorkRollbackError as error:
                rollback_error = error
        self._validator.validate_transition(
            self._state, UnitOfWorkState.CLOSED
        )
        self._state = UnitOfWorkState.CLOSED
        self._repositories.clear()
        if rollback_error is None:
            result = self._record("uow_closed")
        else:
            result = self._record(
                "uow_closed",
                success=False,
                error=rollback_error,
            )
        self._log(
            "uow_closed",
            success=rollback_error is None,
        )
        return result

    def __enter__(self) -> DefaultUnitOfWork:
        """Start and return this coordinator for context management."""
        self.begin()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object,
    ) -> bool:
        """Rollback unfinished work and never suppress body exceptions."""
        if self._state is not UnitOfWorkState.CLOSED:
            self.close()
        return False

    def _transition(self, target: UnitOfWorkState) -> None:
        self._validator.validate_transition(self._state, target)
        self._state = target

    def _require_started(self) -> None:
        if self._state is UnitOfWorkState.CLOSED:
            raise UnitOfWorkClosedError(
                "Unit of Work is closed",
                unit_of_work_id=self._context.unit_of_work_id,
            )
        if self._state is not UnitOfWorkState.STARTED:
            raise UnitOfWorkStateError(
                "operation requires a started Unit of Work",
                unit_of_work_id=self._context.unit_of_work_id,
            )

    def _ensure_not_executing(self) -> None:
        if self._executing:
            raise UnitOfWorkStateError(
                "nested Unit of Work operations are not allowed",
                unit_of_work_id=self._context.unit_of_work_id,
            )

    def _ensure_mutable(self) -> None:
        self._ensure_not_executing()
        if self._state not in {
            UnitOfWorkState.CREATED,
            UnitOfWorkState.STARTED,
        }:
            if self._state is UnitOfWorkState.CLOSED:
                raise UnitOfWorkClosedError(
                    "Unit of Work is closed",
                    unit_of_work_id=self._context.unit_of_work_id,
                )
            raise UnitOfWorkStateError(
                "registrations cannot change in the current state",
                unit_of_work_id=self._context.unit_of_work_id,
            )

    def _record(
        self,
        event: str,
        *,
        success: bool = True,
        operation_id: str | None = None,
        repository_id: str | None = None,
        value: object = None,
        error: Exception | None = None,
        metadata: dict[str, object] | None = None,
    ) -> UnitOfWorkResult:
        error_code = getattr(error, "code", None)
        if error is not None and error_code is None:
            error_code = "uow_error"
        result = UnitOfWorkResult(
            success=success,
            state=self._state,
            event=event,
            unit_of_work_id=self._context.unit_of_work_id,
            timestamp=self._now(),
            operation_id=operation_id,
            repository_id=repository_id,
            value=value,
            error_code=error_code,
            error_message=None if error is None else str(error),
            metadata={} if metadata is None else metadata,
        )
        self._validator.validate_result(result)
        self._history.append(result)
        return result

    def _log(self, event: str, **context: object) -> None:
        safe_context = {
            "unit_of_work_id": self._context.unit_of_work_id,
            "correlation_id": self._context.correlation_id,
            "state": self._state.value,
        }
        safe_context.update(context)
        _LOGGER.info(
            event,
            extra={"event": event, "context": safe_context},
        )

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise UnitOfWorkStateError(
                "clock must return a timezone-aware value"
            )
        return value.astimezone(timezone.utc)

    @staticmethod
    def _identifier(value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise UnitOfWorkStateError(
                "identifier must be a non-empty string"
            )
        return value.strip()


__all__ = ["DefaultUnitOfWork"]
