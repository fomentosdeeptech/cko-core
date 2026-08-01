"""Default coordinator for checkpoint lifecycle operations."""

from __future__ import annotations

import logging
from dataclasses import replace
from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

from .contracts import (
    CheckpointEngine,
    CheckpointRepository,
    CheckpointSerializer,
)
from .errors import CheckpointException, CheckpointValidationError
from .models import (
    CheckpointContext,
    CheckpointIdentifier,
    CheckpointMetadata,
    CheckpointOperation,
    CheckpointPayload,
    CheckpointQuery,
    CheckpointRecord,
    CheckpointResult,
    CheckpointSnapshot,
    CheckpointState,
)
from .serializer import DefaultCheckpointSerializer
from .validator import CheckpointValidator


_LOGGER = logging.getLogger("cko.core.checkpoint.engine")


class DefaultCheckpointEngine(CheckpointEngine):
    """Coordinate checkpoint behavior without performing direct I/O."""

    def __init__(
        self,
        repository: CheckpointRepository,
        serializer: CheckpointSerializer | None = None,
        validator: CheckpointValidator | None = None,
        *,
        clock: Callable[[], datetime] | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        if not isinstance(repository, CheckpointRepository):
            raise CheckpointValidationError(
                "repository must implement CheckpointRepository"
            )
        self._repository = repository
        self._serializer = serializer or DefaultCheckpointSerializer()
        if not isinstance(self._serializer, CheckpointSerializer):
            raise CheckpointValidationError(
                "serializer must implement CheckpointSerializer"
            )
        self._validator = validator or CheckpointValidator()
        if not isinstance(self._validator, CheckpointValidator):
            raise CheckpointValidationError(
                "validator must be CheckpointValidator"
            )
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._id_factory = id_factory or (lambda: uuid4().hex)

    @property
    def repository(self) -> CheckpointRepository:
        """Return the injected repository port."""
        return self._repository

    @property
    def serializer(self) -> CheckpointSerializer:
        """Return the injected serializer port."""
        return self._serializer

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
        """Create a checkpoint and snapshot without persistence."""
        self._validator.validate_context(
            context, CheckpointOperation.CREATE
        )
        self._validator.validate_metadata(metadata)
        instant = self._instant()
        identifier = CheckpointIdentifier(
            checkpoint_id=checkpoint_id or self._id_factory(),
            namespace=context.namespace,
            subject_id=context.subject_id,
            sequence=sequence,
            created_at=instant,
        )
        checkpoint_payload = (
            payload
            if isinstance(payload, CheckpointPayload)
            else CheckpointPayload(
                content_type="application/json",
                encoding="utf-8",
                data=payload,
            )
        )
        record = CheckpointRecord(
            identifier=identifier,
            metadata=metadata,
            payload=checkpoint_payload,
            state=CheckpointState.CREATED,
            correlation_id=context.correlation_id,
            parent_checkpoint_id=parent_checkpoint_id,
            created_at=instant,
            updated_at=instant,
        )
        self._validator.validate_record(record)
        snapshot = self._snapshot(record)
        _LOGGER.info(
            "checkpoint_created",
            extra={
                "event": "checkpoint_created",
                "context": self._safe_context(record),
            },
        )
        _LOGGER.info(
            "checkpoint_validated",
            extra={
                "event": "checkpoint_validated",
                "context": self._safe_context(record),
            },
        )
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.CREATE,
            checkpoint=record,
            snapshot=snapshot,
        )

    def store(self, record: CheckpointRecord) -> CheckpointResult:
        """Validate and explicitly persist a new stored record."""
        self._validator.validate_record(record)
        self._validator.validate_transition(
            record.state, CheckpointState.STORED
        )
        stored = replace(
            record,
            state=CheckpointState.STORED,
            updated_at=self._instant_not_before(record.updated_at),
        )
        result = self._repository.store(stored)
        if not result.success:
            return result
        snapshot = self._snapshot(stored)
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.STORE,
            checkpoint=stored,
            snapshot=snapshot,
            metadata=result.metadata,
        )

    def restore(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Restore, validate, and capture a non-persisted restored view."""
        self._validator.validate_identifier(identifier)
        result = self._repository.restore(identifier)
        if not result.success:
            return result
        assert result.checkpoint is not None
        self._validator.validate_record(result.checkpoint)
        self._validator.validate_transition(
            result.checkpoint.state, CheckpointState.RESTORED
        )
        restored = replace(
            result.checkpoint,
            state=CheckpointState.RESTORED,
            updated_at=self._instant_not_before(
                result.checkpoint.updated_at
            ),
        )
        snapshot = self._snapshot(restored)
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.RESTORE,
            checkpoint=restored,
            snapshot=snapshot,
            metadata=result.metadata,
        )

    def list(self, query: CheckpointQuery) -> CheckpointResult:
        """Delegate logical listing to the injected repository."""
        self._validator.validate_query(query)
        return self._repository.list(query)

    def inspect(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Inspect a checkpoint without changing its lifecycle state."""
        self._validator.validate_identifier(identifier)
        return self._repository.inspect(identifier)

    def supersede(
        self,
        checkpoint: CheckpointRecord,
        successor: CheckpointRecord,
    ) -> CheckpointResult:
        """Persist a logical superseded state with successor traceability."""
        self._validator.validate_record(checkpoint)
        self._validator.validate_record(successor)
        if (
            checkpoint.identifier.checkpoint_id
            == successor.identifier.checkpoint_id
        ):
            raise CheckpointValidationError(
                "successor must be a different checkpoint"
            )
        if (
            checkpoint.identifier.namespace
            != successor.identifier.namespace
            or checkpoint.identifier.subject_id
            != successor.identifier.subject_id
            or successor.identifier.sequence
            <= checkpoint.identifier.sequence
        ):
            raise CheckpointValidationError(
                "successor must advance the same logical checkpoint subject"
            )
        if (
            successor.parent_checkpoint_id
            != checkpoint.identifier.checkpoint_id
        ):
            raise CheckpointValidationError(
                "successor must reference the superseded checkpoint as parent"
            )
        self._validator.validate_transition(
            checkpoint.state, CheckpointState.SUPERSEDED
        )
        superseded = replace(
            checkpoint,
            state=CheckpointState.SUPERSEDED,
            updated_at=self._instant_not_before(checkpoint.updated_at),
        )
        result = self._repository.store(superseded)
        if not result.success:
            return CheckpointResult(
                success=False,
                operation=CheckpointOperation.SUPERSEDE,
                error_code=result.error_code,
                error_message=result.error_message,
                metadata=result.metadata,
            )
        snapshot = self._snapshot(superseded)
        _LOGGER.info(
            "checkpoint_superseded",
            extra={
                "event": "checkpoint_superseded",
                "context": {
                    **self._safe_context(superseded),
                    "successor_checkpoint_id": (
                        successor.identifier.checkpoint_id
                    ),
                },
            },
        )
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.SUPERSEDE,
            checkpoint=superseded,
            snapshot=snapshot,
            metadata={
                **dict(result.metadata),
                "successor_checkpoint_id": (
                    successor.identifier.checkpoint_id
                ),
            },
        )

    def delete(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Delegate one explicit non-cascading deletion."""
        self._validator.validate_identifier(identifier)
        return self._repository.delete(identifier)

    def _snapshot(self, record: CheckpointRecord) -> CheckpointSnapshot:
        snapshot = CheckpointSnapshot.capture(
            snapshot_id=self._id_factory(),
            checkpoint=record,
            captured_at=self._instant_not_before(record.updated_at),
        )
        return self._validator.validate_snapshot(snapshot)

    def _instant(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise CheckpointValidationError(
                "clock must return a timezone-aware datetime"
            )
        return value.astimezone(timezone.utc)

    def _instant_not_before(self, minimum: datetime) -> datetime:
        value = self._instant()
        return minimum if value < minimum else value

    @staticmethod
    def _safe_context(record: CheckpointRecord) -> dict[str, object]:
        identifier = record.identifier
        return {
            "checkpoint_id": identifier.checkpoint_id,
            "namespace": identifier.namespace,
            "subject_id": identifier.subject_id,
            "sequence": identifier.sequence,
            "state": record.state.value,
        }


__all__ = ["DefaultCheckpointEngine"]
