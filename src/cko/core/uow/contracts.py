"""Public ports of the canonical Unit of Work foundation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .models import (
    UnitOfWorkContext,
    UnitOfWorkOperation,
    UnitOfWorkRepository,
    UnitOfWorkResult,
    UnitOfWorkState,
)


class UnitOfWork(ABC):
    """Provider-neutral coordinator of logical repository operations."""

    @abstractmethod
    def begin(
        self, context: UnitOfWorkContext | None = None
    ) -> UnitOfWorkResult:
        """Start this Unit of Work exactly once."""

    @abstractmethod
    def commit(self) -> UnitOfWorkResult:
        """Commit all successfully executed logical operations."""

    @abstractmethod
    def rollback(self) -> UnitOfWorkResult:
        """Compensate executed operations in reverse order."""

    @abstractmethod
    def register(
        self, repository: UnitOfWorkRepository
    ) -> UnitOfWorkRepository:
        """Register one public port."""

    @abstractmethod
    def unregister(self, identifier: str) -> UnitOfWorkRepository:
        """Remove one registered public port."""

    @abstractmethod
    def clear(self) -> int:
        """Remove all registrations and return the removed count."""

    @abstractmethod
    def execute(
        self, operation: UnitOfWorkOperation
    ) -> UnitOfWorkResult:
        """Execute one protected logical operation."""

    @abstractmethod
    def status(self) -> UnitOfWorkState:
        """Return the current lifecycle state."""

    @abstractmethod
    def history(self) -> tuple[UnitOfWorkResult, ...]:
        """Return an immutable ordered result history."""

    @abstractmethod
    def close(self) -> UnitOfWorkResult:
        """Release registrations and permanently close the coordinator."""

    @property
    @abstractmethod
    def repositories(self) -> tuple[UnitOfWorkRepository, ...]:
        """Return registrations in deterministic insertion order."""


RepositoryCollection = Iterable[UnitOfWorkRepository]


__all__ = ["RepositoryCollection", "UnitOfWork"]
