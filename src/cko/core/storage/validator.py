"""Validation services for canonical storage contracts."""

from __future__ import annotations

from cko.core.logging import get_logger

from .contracts import Storage
from .errors import StorageException
from .models import (
    STORAGE_VERSION,
    StorageCapabilities,
    StorageContext,
    StorageDescriptor,
    StorageLocation,
    StorageOperation,
    StorageSession,
    StorageSessionState,
)


class StorageValidator:
    """Validate storage values and their cross-contract invariants."""

    def __init__(self) -> None:
        self._logger = get_logger("core.storage.validator")

    def _validated(self, component: str, storage_id: str | None = None) -> None:
        self._logger.info(
            "storage_validated",
            extra={
                "event": "storage_validated",
                "context": {
                    "component": component,
                    "storage_id": storage_id,
                },
            },
        )

    def validate_capabilities(
        self, capabilities: StorageCapabilities
    ) -> StorageCapabilities:
        """Validate a normalized storage capability declaration."""
        if not isinstance(capabilities, StorageCapabilities):
            raise StorageException(
                "capabilities must be StorageCapabilities",
                code="invalid_capabilities",
            )
        if not capabilities.operations:
            raise StorageException(
                "storage must declare at least one operation",
                code="invalid_capabilities",
            )
        self._validated("capabilities")
        return capabilities

    def validate_descriptor(
        self, descriptor: StorageDescriptor
    ) -> StorageDescriptor:
        """Validate descriptor identity, version, metadata, and capabilities."""
        if not isinstance(descriptor, StorageDescriptor):
            raise StorageException(
                "descriptor must be StorageDescriptor",
                code="invalid_descriptor",
            )
        if descriptor.contract_version != STORAGE_VERSION:
            raise StorageException(
                "unsupported storage contract version",
                code="unsupported_contract_version",
                storage_id=descriptor.identifier,
            )
        self.validate_capabilities(descriptor.capabilities)
        self._validated("descriptor", descriptor.identifier)
        return descriptor

    def validate_location(self, location: StorageLocation) -> StorageLocation:
        """Validate a technology-neutral logical storage location."""
        if not isinstance(location, StorageLocation):
            raise StorageException(
                "location must be StorageLocation", code="invalid_location"
            )
        self._validated("location")
        return location

    def validate_operation(
        self,
        operation: StorageOperation | str,
        capabilities: StorageCapabilities | None = None,
    ) -> StorageOperation:
        """Validate an operation and optional capability compatibility."""
        try:
            normalized = StorageOperation(operation)
        except (TypeError, ValueError) as error:
            raise StorageException(
                "operation must be StorageOperation", code="invalid_operation"
            ) from error
        if capabilities is not None:
            self.validate_capabilities(capabilities)
            if not capabilities.supports(normalized):
                raise StorageException(
                    f"unsupported storage operation: {normalized.value}",
                    code="unsupported_operation",
                )
        self._validated("operation")
        return normalized

    def validate_context(
        self,
        context: StorageContext,
        descriptor: StorageDescriptor | None = None,
    ) -> StorageContext:
        """Validate context structure and optional operation compatibility."""
        if not isinstance(context, StorageContext):
            raise StorageException(
                "context must be StorageContext", code="invalid_context"
            )
        self.validate_location(context.location)
        capabilities = None
        storage_id = None
        if descriptor is not None:
            self.validate_descriptor(descriptor)
            capabilities = descriptor.capabilities
            storage_id = descriptor.identifier
        self.validate_operation(context.operation, capabilities)
        self._validated("context", storage_id)
        return context

    def validate_session(
        self,
        session: StorageSession,
        descriptor: StorageDescriptor | None = None,
    ) -> StorageSession:
        """Validate session identity, lifecycle, and descriptor binding."""
        if not isinstance(session, StorageSession):
            raise StorageException(
                "session must be StorageSession", code="invalid_session"
            )
        if descriptor is not None:
            self.validate_descriptor(descriptor)
            if session.storage_id != descriptor.identifier:
                raise StorageException(
                    "session storage identity does not match descriptor",
                    code="invalid_session",
                    storage_id=descriptor.identifier,
                )
        self.validate_context(session.context, descriptor)
        if (
            session.state is StorageSessionState.STARTED
            and session.finished_at is not None
        ):
            raise StorageException(
                "started session cannot have finished_at",
                code="invalid_session",
                storage_id=session.storage_id,
            )
        self._validated("session", session.storage_id)
        return session

    def validate_storage(
        self,
        storage: Storage,
        expected: StorageDescriptor | None = None,
    ) -> Storage:
        """Validate a storage instance against its registered contract."""
        if not isinstance(storage, Storage):
            raise StorageException(
                "factory did not create a Storage", code="invalid_storage"
            )
        descriptor = self.validate_descriptor(storage.descriptor)
        if expected is not None and descriptor != expected:
            raise StorageException(
                "storage descriptor does not match its registration",
                code="descriptor_mismatch",
                storage_id=expected.identifier,
            )
        self._validated("storage", descriptor.identifier)
        return storage


__all__ = ["StorageValidator"]
