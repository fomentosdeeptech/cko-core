"""Validation policy for the canonical Unit of Work foundation."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Mapping

from .errors import (
    UnitOfWorkClosedError,
    UnitOfWorkRegistrationError,
    UnitOfWorkStateError,
    UnitOfWorkValidationError,
)
from .models import (
    UnitOfWorkContext,
    UnitOfWorkOperation,
    UnitOfWorkRepository,
    UnitOfWorkResult,
    UnitOfWorkState,
)


_TRANSITIONS = {
    UnitOfWorkState.CREATED: {
        UnitOfWorkState.STARTED,
        UnitOfWorkState.CLOSED,
    },
    UnitOfWorkState.STARTED: {
        UnitOfWorkState.COMMITTED,
        UnitOfWorkState.ROLLED_BACK,
        UnitOfWorkState.FAILED,
    },
    UnitOfWorkState.COMMITTED: {UnitOfWorkState.CLOSED},
    UnitOfWorkState.ROLLED_BACK: {UnitOfWorkState.CLOSED},
    UnitOfWorkState.FAILED: {
        UnitOfWorkState.ROLLED_BACK,
        UnitOfWorkState.CLOSED,
    },
    UnitOfWorkState.CLOSED: set(),
}
_FORBIDDEN_KEYS = {
    "connection",
    "connection_string",
    "credentials",
    "database",
    "dsn",
    "password",
    "path",
    "secret",
    "sql",
    "token",
    "url",
}


class UnitOfWorkValidator:
    """Centralize model, registration, result, and lifecycle validation."""

    def validate_state(self, state: UnitOfWorkState) -> UnitOfWorkState:
        """Validate and normalize one lifecycle state."""
        try:
            return UnitOfWorkState(state)
        except (TypeError, ValueError) as error:
            raise UnitOfWorkValidationError(
                "state must be UnitOfWorkState"
            ) from error

    def validate_transition(
        self,
        current: UnitOfWorkState,
        target: UnitOfWorkState,
    ) -> None:
        """Reject invalid transitions, including duplicate terminal actions."""
        source = self.validate_state(current)
        destination = self.validate_state(target)
        if source is UnitOfWorkState.CLOSED:
            raise UnitOfWorkClosedError("Unit of Work is closed")
        if destination not in _TRANSITIONS[source]:
            raise UnitOfWorkStateError(
                f"invalid Unit of Work transition: "
                f"{source.value} -> {destination.value}"
            )

    def validate_context(
        self, context: UnitOfWorkContext
    ) -> UnitOfWorkContext:
        """Validate context type and reject physical or sensitive metadata."""
        if not isinstance(context, UnitOfWorkContext):
            raise UnitOfWorkValidationError(
                "context must be UnitOfWorkContext"
            )
        self._validate_safe_mapping(context.metadata)
        return context

    def validate_repository(
        self, repository: UnitOfWorkRepository
    ) -> UnitOfWorkRepository:
        """Validate one public port registration."""
        if not isinstance(repository, UnitOfWorkRepository):
            raise UnitOfWorkRegistrationError(
                "repository must be UnitOfWorkRepository"
            )
        self._validate_safe_mapping(repository.metadata)
        return repository

    def validate_repositories(
        self, repositories: Iterable[UnitOfWorkRepository]
    ) -> tuple[UnitOfWorkRepository, ...]:
        """Validate a registration collection and duplicate identities."""
        if isinstance(repositories, (str, bytes)) or not isinstance(
            repositories, Iterable
        ):
            raise UnitOfWorkRegistrationError(
                "repositories must be an iterable"
            )
        normalized = tuple(
            self.validate_repository(item) for item in repositories
        )
        identifiers = [item.identifier for item in normalized]
        if len(identifiers) != len(set(identifiers)):
            raise UnitOfWorkRegistrationError(
                "repository identifiers must be unique"
            )
        resource_ids = [id(item.repository) for item in normalized]
        if len(resource_ids) != len(set(resource_ids)):
            raise UnitOfWorkRegistrationError(
                "repository instances must be unique"
            )
        return normalized

    def validate_operation(
        self, operation: UnitOfWorkOperation
    ) -> UnitOfWorkOperation:
        """Validate one operation model and safe metadata."""
        if not isinstance(operation, UnitOfWorkOperation):
            raise UnitOfWorkValidationError(
                "operation must be UnitOfWorkOperation"
            )
        self._validate_safe_mapping(operation.metadata)
        return operation

    def validate_result(
        self, result: UnitOfWorkResult
    ) -> UnitOfWorkResult:
        """Validate one immutable public result."""
        if not isinstance(result, UnitOfWorkResult):
            raise UnitOfWorkValidationError(
                "result must be UnitOfWorkResult"
            )
        self.validate_state(result.state)
        self._validate_safe_mapping(result.metadata)
        return result

    @classmethod
    def _validate_safe_mapping(cls, value: Mapping[str, object]) -> None:
        for key, item in value.items():
            normalized = key.strip().lower().replace("-", "_")
            if normalized in _FORBIDDEN_KEYS:
                raise UnitOfWorkValidationError(
                    "metadata contains a forbidden physical or "
                    "sensitive field"
                )
            if isinstance(item, Mapping):
                cls._validate_safe_mapping(item)


__all__ = ["UnitOfWorkValidator"]
