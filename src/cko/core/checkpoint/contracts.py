"""Public ports of the canonical checkpoint foundation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import (
    CheckpointContext,
    CheckpointIdentifier,
    CheckpointMetadata,
    CheckpointPayload,
    CheckpointQuery,
    CheckpointRecord,
    CheckpointResult,
)


class CheckpointRepository(ABC):
    """Technology-neutral persistence port for checkpoint records."""

    @abstractmethod
    def store(self, record: CheckpointRecord) -> CheckpointResult:
        """Persist a validated record."""

    @abstractmethod
    def restore(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Restore and verify one persisted record."""

    @abstractmethod
    def list(self, query: CheckpointQuery) -> CheckpointResult:
        """List records matching a logical query."""

    @abstractmethod
    def inspect(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Inspect one record without changing it."""

    @abstractmethod
    def delete(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Explicitly delete one record."""


class CheckpointSerializer(ABC):
    """Port for deterministic checkpoint record serialization."""

    @abstractmethod
    def serialize(self, record: CheckpointRecord) -> bytes:
        """Serialize a record to canonical UTF-8 bytes."""

    @abstractmethod
    def deserialize(self, payload: bytes) -> CheckpointRecord:
        """Deserialize and verify canonical UTF-8 bytes."""

    @abstractmethod
    def digest(self, record: CheckpointRecord) -> str:
        """Calculate the SHA-256 digest of a canonical record."""


class CheckpointEngine(ABC):
    """Application port coordinating the checkpoint lifecycle."""

    @abstractmethod
    def create(
        self,
        context: CheckpointContext,
        metadata: CheckpointMetadata,
        payload: CheckpointPayload | object,
        *,
        checkpoint_id: str | None = None,
        sequence: int = 0,
        parent_checkpoint_id: str | None = None,
    ) -> CheckpointResult:
        """Create an in-memory checkpoint without persisting it."""

    @abstractmethod
    def store(self, record: CheckpointRecord) -> CheckpointResult:
        """Persist an explicitly supplied checkpoint."""

    @abstractmethod
    def restore(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Restore one checkpoint and capture a restored snapshot."""

    @abstractmethod
    def list(self, query: CheckpointQuery) -> CheckpointResult:
        """List persisted checkpoints."""

    @abstractmethod
    def inspect(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Inspect one persisted checkpoint."""

    @abstractmethod
    def supersede(
        self,
        checkpoint: CheckpointRecord,
        successor: CheckpointRecord,
    ) -> CheckpointResult:
        """Mark a checkpoint as superseded by a traceable successor."""

    @abstractmethod
    def delete(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Explicitly delete one checkpoint."""


__all__ = [
    "CheckpointEngine",
    "CheckpointRepository",
    "CheckpointSerializer",
]
