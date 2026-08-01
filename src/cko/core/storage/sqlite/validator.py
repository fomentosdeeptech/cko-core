"""Validation service for SQLite storage adapter composition."""

from __future__ import annotations

from pathlib import Path

from cko.core.connectors import ConnectorValidator
from cko.core.storage import StorageException, StorageValidator

from .descriptor import SQLiteDescriptor
from .resolver import SQLiteLocationResolver
from .result import SQLiteResult
from .session import SQLiteSession


class SQLiteStorageValidator:
    """Validate SQLite values through public foundation validators."""

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

    def validate_database(
        self,
        database: str | Path,
    ) -> SQLiteLocationResolver:
        """Validate and normalize one SQLite database path."""
        return SQLiteLocationResolver(database)

    def validate_descriptor(
        self,
        descriptor: SQLiteDescriptor,
    ) -> SQLiteDescriptor:
        """Validate both public descriptors of this adapter."""
        if not isinstance(descriptor, SQLiteDescriptor):
            raise StorageException("descriptor must be SQLiteDescriptor")
        self._storage_validator.validate_descriptor(descriptor.storage)
        self._connector_validator.validate_descriptor(descriptor.connector)
        if descriptor.storage.identifier != descriptor.connector.identifier:
            raise StorageException("SQLite descriptor identifiers differ")
        return descriptor

    def validate_session(
        self,
        session: SQLiteSession,
        descriptor: SQLiteDescriptor,
    ) -> SQLiteSession:
        """Validate the paired public sessions and their bindings."""
        if not isinstance(session, SQLiteSession):
            raise StorageException("session must be SQLiteSession")
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

    def validate_result(self, result: SQLiteResult) -> SQLiteResult:
        """Validate a paired public result."""
        if not isinstance(result, SQLiteResult):
            raise StorageException("result must be SQLiteResult")
        return result


__all__ = ["SQLiteStorageValidator"]
