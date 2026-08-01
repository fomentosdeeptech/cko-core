"""Abstract storage port for future infrastructure adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import StorageDescriptor, StorageResult, StorageSession


class Storage(ABC):
    """Technology-independent port implemented by future storage adapters."""

    @property
    @abstractmethod
    def descriptor(self) -> StorageDescriptor:
        """Return the immutable public descriptor of this storage provider."""

    @abstractmethod
    def execute(self, session: StorageSession) -> StorageResult:
        """Execute the logical operation represented by a validated session."""


__all__ = ["Storage"]
