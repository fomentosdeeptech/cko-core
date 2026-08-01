"""Validation service for filesystem storage adapter composition."""

from __future__ import annotations

from pathlib import Path

from cko.core.connectors import ConnectorValidator
from cko.core.storage import StorageException, StorageValidator

from .descriptor import FilesystemDescriptor
from .resolver import FilesystemLocationResolver
from .result import FilesystemResult
from .session import FilesystemSession


class FilesystemStorageValidator:
    """Validate filesystem values by delegating to public foundation contracts."""

    def __init__(
        self,
        storage_validator: StorageValidator | None = None,
        connector_validator: ConnectorValidator | None = None,
    ) -> None:
        self._storage_validator = storage_validator or StorageValidator()
        self._connector_validator = connector_validator or ConnectorValidator()
        if not isinstance(self._storage_validator, StorageValidator):
            raise StorageException("storage_validator must be StorageValidator")
        if not isinstance(self._connector_validator, ConnectorValidator):
            raise StorageException(
                "connector_validator must be ConnectorValidator"
            )

    def validate_root(self, root: str | Path) -> FilesystemLocationResolver:
        """Validate and normalize one filesystem root."""
        return FilesystemLocationResolver(root)

    def validate_descriptor(
        self, descriptor: FilesystemDescriptor
    ) -> FilesystemDescriptor:
        """Validate both public descriptors of this adapter."""
        if not isinstance(descriptor, FilesystemDescriptor):
            raise StorageException(
                "descriptor must be FilesystemDescriptor"
            )
        self._storage_validator.validate_descriptor(descriptor.storage)
        self._connector_validator.validate_descriptor(descriptor.connector)
        if descriptor.storage.identifier != descriptor.connector.identifier:
            raise StorageException("filesystem descriptor identifiers differ")
        return descriptor

    def validate_session(
        self, session: FilesystemSession, descriptor: FilesystemDescriptor
    ) -> FilesystemSession:
        """Validate the paired public sessions and their bindings."""
        if not isinstance(session, FilesystemSession):
            raise StorageException("session must be FilesystemSession")
        self.validate_descriptor(descriptor)
        self._storage_validator.validate_session(
            session.storage_session,
            descriptor.storage,
        )
        self._connector_validator.validate_session(
            session.connector_session,
            descriptor.connector,
        )
        return session

    def validate_result(self, result: FilesystemResult) -> FilesystemResult:
        """Validate a paired public result."""
        if not isinstance(result, FilesystemResult):
            raise StorageException("result must be FilesystemResult")
        return result


__all__ = ["FilesystemStorageValidator"]
