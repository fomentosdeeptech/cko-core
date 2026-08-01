"""Validation service for checkpoint models and lifecycle."""

from __future__ import annotations

import hashlib
from typing import Mapping

from cko.core.storage import Storage, StorageOperation

from .errors import (
    CheckpointIntegrityError,
    CheckpointStateError,
    CheckpointValidationError,
)
from .models import (
    CHECKPOINT_SCHEMA_VERSION,
    CheckpointCollection,
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


_FORBIDDEN_CONTEXT_KEYS = {
    "connection",
    "credential",
    "credentials",
    "cursor",
    "database",
    "handle",
    "password",
    "path",
    "secret",
    "sql",
    "token",
    "url",
}
_TRANSITIONS = {
    CheckpointState.CREATED: {
        CheckpointState.STORED,
        CheckpointState.FAILED,
    },
    CheckpointState.STORED: {
        CheckpointState.RESTORED,
        CheckpointState.SUPERSEDED,
        CheckpointState.FAILED,
    },
    CheckpointState.RESTORED: {
        CheckpointState.SUPERSEDED,
        CheckpointState.FAILED,
    },
    CheckpointState.SUPERSEDED: set(),
    CheckpointState.FAILED: set(),
}


class CheckpointValidator:
    """Validate checkpoint invariants before logical or physical changes."""

    def validate_identifier(
        self, identifier: CheckpointIdentifier
    ) -> CheckpointIdentifier:
        """Validate a logical identifier."""
        if not isinstance(identifier, CheckpointIdentifier):
            raise CheckpointValidationError(
                "identifier must be CheckpointIdentifier"
            )
        self._safe_segment(identifier.checkpoint_id, "checkpoint_id")
        self._safe_segment(identifier.namespace, "namespace")
        self._safe_segment(identifier.subject_id, "subject_id")
        return identifier

    def validate_metadata(
        self, metadata: CheckpointMetadata
    ) -> CheckpointMetadata:
        """Validate safe checkpoint metadata."""
        if not isinstance(metadata, CheckpointMetadata):
            raise CheckpointValidationError(
                "metadata must be CheckpointMetadata"
            )
        self._validate_safe_mapping(metadata.labels, "labels")
        self._validate_safe_mapping(metadata.attributes, "attributes")
        return metadata

    def validate_payload(
        self, payload: CheckpointPayload
    ) -> CheckpointPayload:
        """Recalculate and validate payload integrity."""
        if not isinstance(payload, CheckpointPayload):
            raise CheckpointValidationError(
                "payload must be CheckpointPayload"
            )
        rebuilt = CheckpointPayload(
            content_type=payload.content_type,
            encoding=payload.encoding,
            data=payload.data,
            size=payload.size,
            sha256=payload.sha256,
            schema_version=payload.schema_version,
        )
        if rebuilt != payload:
            raise CheckpointIntegrityError("checkpoint payload is inconsistent")
        return payload

    def validate_record(self, record: CheckpointRecord) -> CheckpointRecord:
        """Validate a complete record and all nested values."""
        if not isinstance(record, CheckpointRecord):
            raise CheckpointValidationError(
                "record must be CheckpointRecord"
            )
        if record.schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointValidationError(
                "unsupported checkpoint record schema"
            )
        self.validate_identifier(record.identifier)
        self.validate_metadata(record.metadata)
        self.validate_payload(record.payload)
        return record

    def validate_snapshot(
        self, snapshot: CheckpointSnapshot
    ) -> CheckpointSnapshot:
        """Validate snapshot record and canonical digest."""
        if not isinstance(snapshot, CheckpointSnapshot):
            raise CheckpointValidationError(
                "snapshot must be CheckpointSnapshot"
            )
        self.validate_record(snapshot.checkpoint)
        expected = hashlib.sha256(
            snapshot.checkpoint.to_json().encode("utf-8")
        ).hexdigest()
        if snapshot.digest != expected:
            raise CheckpointIntegrityError("snapshot digest mismatch")
        return snapshot

    def validate_query(self, query: CheckpointQuery) -> CheckpointQuery:
        """Validate a technology-neutral query."""
        if not isinstance(query, CheckpointQuery):
            raise CheckpointValidationError(
                "query must be CheckpointQuery"
            )
        for name in ("namespace", "subject_id", "checkpoint_id"):
            value = getattr(query, name)
            if value is not None:
                self._safe_segment(value, name)
        return query

    def validate_collection(
        self, collection: CheckpointCollection
    ) -> CheckpointCollection:
        """Validate collection members and deterministic ordering."""
        if not isinstance(collection, CheckpointCollection):
            raise CheckpointValidationError(
                "collection must be CheckpointCollection"
            )
        for record in collection.checkpoints:
            self.validate_record(record)
        return collection

    def validate_result(self, result: CheckpointResult) -> CheckpointResult:
        """Validate a typed operation result."""
        if not isinstance(result, CheckpointResult):
            raise CheckpointValidationError(
                "result must be CheckpointResult"
            )
        if result.checkpoint is not None:
            self.validate_record(result.checkpoint)
        if result.snapshot is not None:
            self.validate_snapshot(result.snapshot)
        if result.collection is not None:
            self.validate_collection(result.collection)
        return result

    def validate_context(
        self,
        context: CheckpointContext,
        operation: CheckpointOperation | None = None,
    ) -> CheckpointContext:
        """Validate safe context and optional operation compatibility."""
        if not isinstance(context, CheckpointContext):
            raise CheckpointValidationError(
                "context must be CheckpointContext"
            )
        if operation is not None and context.operation is not operation:
            raise CheckpointValidationError(
                "context operation is incompatible with requested operation"
            )
        self._safe_segment(context.namespace, "namespace")
        self._safe_segment(context.subject_id, "subject_id")
        self._validate_safe_mapping(context.parameters, "parameters")
        self._validate_safe_mapping(context.metadata, "metadata")
        return context

    def validate_transition(
        self,
        current: CheckpointState,
        target: CheckpointState,
    ) -> None:
        """Reject invalid lifecycle transitions and terminal reopening."""
        try:
            source = CheckpointState(current)
            destination = CheckpointState(target)
        except (TypeError, ValueError) as error:
            raise CheckpointStateError("checkpoint state is invalid") from error
        if destination not in _TRANSITIONS[source]:
            raise CheckpointStateError(
                f"invalid checkpoint transition: "
                f"{source.value} -> {destination.value}"
            )

    def validate_storage(self, storage: Storage) -> Storage:
        """Validate Storage port compatibility without adapter knowledge."""
        if not isinstance(storage, Storage):
            raise CheckpointValidationError(
                "storage must implement the Storage port"
            )
        descriptor = storage.descriptor
        required = {
            StorageOperation.READ,
            StorageOperation.WRITE,
            StorageOperation.LIST,
            StorageOperation.DELETE,
            StorageOperation.EXISTS,
        }
        if not all(
            descriptor.capabilities.supports(operation)
            for operation in required
        ):
            raise CheckpointValidationError(
                "storage does not support checkpoint operations"
            )
        return storage

    def validate_deserialized(
        self, record: CheckpointRecord
    ) -> CheckpointRecord:
        """Validate integrity after deserialization."""
        return self.validate_record(record)

    @staticmethod
    def _safe_segment(value: str, name: str) -> None:
        if (
            value in {".", ".."}
            or "/" in value
            or "\\" in value
            or any(ord(character) < 32 for character in value)
        ):
            raise CheckpointValidationError(
                f"{name} is not a safe logical key segment"
            )

    @classmethod
    def _validate_safe_mapping(
        cls,
        value: Mapping[str, object],
        name: str,
    ) -> None:
        for key, item in value.items():
            normalized = key.strip().lower().replace("-", "_")
            if normalized in _FORBIDDEN_CONTEXT_KEYS:
                raise CheckpointValidationError(
                    f"{name} contains forbidden physical or sensitive field"
                )
            if isinstance(item, Mapping):
                cls._validate_safe_mapping(item, name)


__all__ = ["CheckpointValidator"]
