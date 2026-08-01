"""Storage-backed implementation of the checkpoint repository port."""

from __future__ import annotations

import base64
import binascii
import logging
from datetime import datetime, timezone
from typing import Callable, Mapping
from uuid import uuid4

from cko.core.storage import (
    Storage,
    StorageContext,
    StorageException,
    StorageLocation,
    StorageObject,
    StorageOperation,
    StorageResult,
    StorageSession,
)

from .contracts import CheckpointRepository, CheckpointSerializer
from .errors import (
    CheckpointConflictError,
    CheckpointException,
    CheckpointNotFoundError,
    CheckpointStorageError,
)
from .models import (
    CheckpointCollection,
    CheckpointIdentifier,
    CheckpointOperation,
    CheckpointQuery,
    CheckpointRecord,
    CheckpointResult,
)
from .serializer import DefaultCheckpointSerializer
from .validator import CheckpointValidator


_LOGGER = logging.getLogger("cko.core.checkpoint.repository")
_STORAGE_NAMESPACE = "checkpoints"


class StorageCheckpointRepository(CheckpointRepository):
    """Persist checkpoints exclusively through the public Storage port."""

    def __init__(
        self,
        storage: Storage,
        serializer: CheckpointSerializer | None = None,
        validator: CheckpointValidator | None = None,
        *,
        clock: Callable[[], datetime] | None = None,
        session_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._validator = validator or CheckpointValidator()
        if not isinstance(self._validator, CheckpointValidator):
            raise CheckpointStorageError(
                "validator must be CheckpointValidator"
            )
        self._storage = self._validator.validate_storage(storage)
        self._serializer = serializer or DefaultCheckpointSerializer()
        if not isinstance(self._serializer, CheckpointSerializer):
            raise CheckpointStorageError(
                "serializer must implement CheckpointSerializer"
            )
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._session_id_factory = session_id_factory or (
            lambda: uuid4().hex
        )

    @property
    def storage(self) -> Storage:
        """Return the injected Storage port instance."""
        return self._storage

    @property
    def serializer(self) -> CheckpointSerializer:
        """Return the injected checkpoint serializer."""
        return self._serializer

    def store(self, record: CheckpointRecord) -> CheckpointResult:
        """Persist a validated record at its deterministic logical key."""
        self._validator.validate_record(record)
        existing = self._read_optional(record.identifier)
        if existing is not None:
            try:
                self._validator.validate_transition(
                    existing.state, record.state
                )
            except CheckpointException:
                error = CheckpointConflictError(
                    "checkpoint already exists with incompatible state",
                    checkpoint_id=record.identifier.checkpoint_id,
                )
                return self._failure(CheckpointOperation.STORE, error)
        payload = self._serializer.serialize(record)
        result = self._execute(
            StorageOperation.WRITE,
            self._location(record.identifier),
            {
                "content_base64": base64.b64encode(payload).decode("ascii"),
                "metadata": {
                    "checkpoint_id": record.identifier.checkpoint_id,
                    "schema_version": record.schema_version,
                },
            },
            record.correlation_id,
        )
        if not result.success:
            return self._storage_failure(
                CheckpointOperation.STORE,
                result,
                record.identifier.checkpoint_id,
            )
        _LOGGER.info(
            "checkpoint_stored",
            extra={
                "event": "checkpoint_stored",
                "context": self._safe_context(record),
            },
        )
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.STORE,
            checkpoint=record,
            metadata={"storage_id": result.storage_id},
        )

    def restore(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Restore and verify one checkpoint through Storage READ."""
        self._validator.validate_identifier(identifier)
        if not self._exists(identifier):
            return self._failure(
                CheckpointOperation.RESTORE,
                CheckpointNotFoundError(
                    "checkpoint does not exist",
                    checkpoint_id=identifier.checkpoint_id,
                ),
            )
        result = self._execute(
            StorageOperation.READ,
            self._location(identifier),
            {},
            self._correlation(identifier),
        )
        if not result.success:
            return self._storage_failure(
                CheckpointOperation.RESTORE,
                result,
                identifier.checkpoint_id,
                not_found=True,
            )
        record = self._record_from_result(result)
        self._ensure_identity(identifier, record)
        _LOGGER.info(
            "checkpoint_restored",
            extra={
                "event": "checkpoint_restored",
                "context": self._safe_context(record),
            },
        )
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.RESTORE,
            checkpoint=record,
            metadata={"storage_id": result.storage_id},
        )

    def list(self, query: CheckpointQuery) -> CheckpointResult:
        """List, restore, filter, and order checkpoints deterministically."""
        self._validator.validate_query(query)
        location = StorageLocation(
            namespace=_STORAGE_NAMESPACE,
            key=self._query_prefix(query),
        )
        listed = self._execute(
            StorageOperation.LIST,
            location,
            {"recursive": True},
            uuid4().hex,
        )
        if not listed.success:
            message = (listed.message or "").lower()
            if self._is_not_found(message) or (
                "list location must be a directory" in message
            ):
                collection = CheckpointCollection()
                return CheckpointResult(
                    success=True,
                    operation=CheckpointOperation.LIST,
                    collection=collection,
                )
            return self._storage_failure(
                CheckpointOperation.LIST, listed, None
            )
        records: list[CheckpointRecord] = []
        for storage_object in listed.objects:
            if not self._is_checkpoint_object(storage_object):
                continue
            read = self._execute(
                StorageOperation.READ,
                storage_object.location,
                {},
                uuid4().hex,
            )
            if not read.success:
                return self._storage_failure(
                    CheckpointOperation.LIST, read, None
                )
            record = self._record_from_result(read)
            if query.matches(record):
                records.append(record)
        records.sort(key=self._sort_key, reverse=query.descending)
        total = len(records)
        if query.limit is not None:
            records = records[:query.limit]
        collection = CheckpointCollection(
            checkpoints=tuple(records),
            total=total,
        )
        self._validator.validate_collection(collection)
        _LOGGER.info(
            "checkpoint_listed",
            extra={
                "event": "checkpoint_listed",
                "context": {"count": len(collection), "total": total},
            },
        )
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.LIST,
            collection=collection,
        )

    def inspect(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Inspect one checkpoint without changing persisted state."""
        restored = self.restore(identifier)
        if not restored.success:
            return CheckpointResult(
                success=False,
                operation=CheckpointOperation.INSPECT,
                error_code=restored.error_code,
                error_message=restored.error_message,
                metadata=restored.metadata,
            )
        assert restored.checkpoint is not None
        _LOGGER.info(
            "checkpoint_inspected",
            extra={
                "event": "checkpoint_inspected",
                "context": self._safe_context(restored.checkpoint),
            },
        )
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.INSPECT,
            checkpoint=restored.checkpoint,
            metadata=restored.metadata,
        )

    def delete(self, identifier: CheckpointIdentifier) -> CheckpointResult:
        """Delete exactly one explicitly identified checkpoint."""
        self._validator.validate_identifier(identifier)
        if not self._exists(identifier):
            return self._failure(
                CheckpointOperation.DELETE,
                CheckpointNotFoundError(
                    "checkpoint does not exist",
                    checkpoint_id=identifier.checkpoint_id,
                ),
            )
        result = self._execute(
            StorageOperation.DELETE,
            self._location(identifier),
            {},
            self._correlation(identifier),
        )
        if not result.success:
            return self._storage_failure(
                CheckpointOperation.DELETE,
                result,
                identifier.checkpoint_id,
                not_found=True,
            )
        _LOGGER.info(
            "checkpoint_deleted",
            extra={
                "event": "checkpoint_deleted",
                "context": {
                    "checkpoint_id": identifier.checkpoint_id,
                    "namespace": identifier.namespace,
                    "subject_id": identifier.subject_id,
                    "sequence": identifier.sequence,
                },
            },
        )
        return CheckpointResult(
            success=True,
            operation=CheckpointOperation.DELETE,
            metadata={"storage_id": result.storage_id},
        )

    def _read_optional(
        self, identifier: CheckpointIdentifier
    ) -> CheckpointRecord | None:
        if not self._exists(identifier):
            return None
        result = self._execute(
            StorageOperation.READ,
            self._location(identifier),
            {},
            self._correlation(identifier),
        )
        if not result.success:
            message = (result.message or "").lower()
            if self._is_not_found(message):
                return None
            raise CheckpointStorageError(
                result.message or "storage read failed",
                checkpoint_id=identifier.checkpoint_id,
            )
        return self._record_from_result(result)

    def _exists(self, identifier: CheckpointIdentifier) -> bool:
        result = self._execute(
            StorageOperation.EXISTS,
            self._location(identifier),
            {},
            self._correlation(identifier),
        )
        if not result.success:
            raise CheckpointStorageError(
                result.message or "Storage existence check failed",
                checkpoint_id=identifier.checkpoint_id,
            )
        exists = result.metadata.get("exists")
        if not isinstance(exists, bool):
            raise CheckpointStorageError(
                "Storage EXISTS result omitted boolean existence metadata",
                checkpoint_id=identifier.checkpoint_id,
            )
        return exists

    def _execute(
        self,
        operation: StorageOperation,
        location: StorageLocation,
        parameters: Mapping[str, object],
        correlation_id: str,
    ) -> StorageResult:
        context = StorageContext(
            correlation_id=correlation_id,
            operation=operation,
            location=location,
            parameters=parameters,
        )
        session = StorageSession.start(
            session_id=self._session_id_factory(),
            storage_id=self._storage.descriptor.identifier,
            context=context,
            started_at=self._clock(),
        )
        try:
            result = self._storage.execute(session)
        except StorageException as error:
            raise CheckpointStorageError(
                "Storage port raised an operation error",
                details={"operation": operation.value},
            ) from error
        except Exception as error:
            raise CheckpointStorageError(
                "unexpected Storage port failure",
                details={"operation": operation.value},
            ) from error
        if not isinstance(result, StorageResult):
            raise CheckpointStorageError(
                "Storage port returned an invalid result",
                details={"operation": operation.value},
            )
        if result.operation is not operation:
            raise CheckpointStorageError(
                "Storage result operation is incompatible",
                details={"operation": operation.value},
            )
        return result

    def _record_from_result(self, result: StorageResult) -> CheckpointRecord:
        encoded = result.metadata.get("content_base64")
        if not isinstance(encoded, str):
            raise CheckpointStorageError(
                "Storage READ result omitted Base64 content"
            )
        try:
            payload = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as error:
            raise CheckpointStorageError(
                "Storage READ result contains invalid Base64"
            ) from error
        record = self._serializer.deserialize(payload)
        return self._validator.validate_deserialized(record)

    @staticmethod
    def _ensure_identity(
        expected: CheckpointIdentifier,
        record: CheckpointRecord,
    ) -> None:
        if record.identifier != expected:
            raise CheckpointStorageError(
                "stored checkpoint identity does not match its logical key",
                checkpoint_id=expected.checkpoint_id,
            )

    def _location(
        self, identifier: CheckpointIdentifier
    ) -> StorageLocation:
        self._validator.validate_identifier(identifier)
        key = (
            f"{identifier.namespace}/{identifier.subject_id}/"
            f"{identifier.sequence}/{identifier.checkpoint_id}.json"
        )
        return StorageLocation(namespace=_STORAGE_NAMESPACE, key=key)

    @staticmethod
    def _query_prefix(query: CheckpointQuery) -> str:
        if query.namespace is None:
            return "."
        if query.subject_id is None:
            return query.namespace
        return f"{query.namespace}/{query.subject_id}"

    @staticmethod
    def _is_checkpoint_object(storage_object: StorageObject) -> bool:
        return storage_object.location.key.lower().endswith(".json")

    @staticmethod
    def _sort_key(record: CheckpointRecord) -> tuple[object, ...]:
        identifier = record.identifier
        return (
            identifier.namespace,
            identifier.subject_id,
            identifier.sequence,
            identifier.created_at,
            identifier.checkpoint_id,
        )

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

    @staticmethod
    def _correlation(identifier: CheckpointIdentifier) -> str:
        return f"checkpoint:{identifier.checkpoint_id}"

    @staticmethod
    def _failure(
        operation: CheckpointOperation,
        error: CheckpointException,
    ) -> CheckpointResult:
        _LOGGER.error(
            "checkpoint_operation_failed",
            extra={
                "event": "checkpoint_operation_failed",
                "context": {
                    "operation": operation.value,
                    "error_code": error.code,
                },
            },
        )
        return CheckpointResult(
            success=False,
            operation=operation,
            error_code=error.code,
            error_message=str(error),
        )

    def _storage_failure(
        self,
        operation: CheckpointOperation,
        result: StorageResult,
        checkpoint_id: str | None,
        *,
        not_found: bool = False,
    ) -> CheckpointResult:
        message = result.message or "Storage operation failed"
        normalized = message.lower()
        if not_found and self._is_not_found(normalized):
            error: CheckpointException = CheckpointNotFoundError(
                "checkpoint does not exist",
                checkpoint_id=checkpoint_id,
            )
        else:
            error = CheckpointStorageError(
                message,
                checkpoint_id=checkpoint_id,
                details={"storage_id": result.storage_id},
            )
        return self._failure(operation, error)

    @staticmethod
    def _is_not_found(message: str) -> bool:
        return any(
            marker in message
            for marker in (
                "does not exist",
                "no such file",
                "not exist",
                "not found",
            )
        )


__all__ = ["StorageCheckpointRepository"]
