"""Factory composition for SQLite Connector and Storage adapters."""

from __future__ import annotations

from pathlib import Path

from cko.core.connectors import ConnectorFactory, ConnectorRegistry
from cko.core.storage import StorageException, StorageFactory, StorageRegistry

from .connector import SQLiteConnector
from .descriptor import SQLiteDescriptor
from .storage import SQLiteStorage
from .validator import SQLiteStorageValidator


class SQLiteStorageFactory:
    """Compose concrete adapters through the public generic factories."""

    def __init__(
        self,
        database: str | Path,
        descriptor: SQLiteDescriptor | None = None,
        validator: SQLiteStorageValidator | None = None,
        *,
        timeout: float = 5.0,
    ) -> None:
        self._validator = validator or SQLiteStorageValidator()
        if not isinstance(self._validator, SQLiteStorageValidator):
            raise StorageException("validator must be SQLiteStorageValidator")
        self._resolver = self._validator.validate_database(database)
        self._descriptor = self._validator.validate_descriptor(
            descriptor or SQLiteDescriptor()
        )
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            raise StorageException("timeout must be a positive number")
        self._timeout = float(timeout)

    @property
    def descriptor(self) -> SQLiteDescriptor:
        """Return the descriptor used for factory composition."""
        return self._descriptor

    def create(self) -> SQLiteStorage:
        """Create SQLiteStorage through StorageRegistry and StorageFactory."""
        registry = StorageRegistry()
        registry.register(
            self._descriptor.storage,
            lambda: SQLiteStorage(
                self._resolver.database,
                self._descriptor.storage,
                timeout=self._timeout,
            ),
        )
        storage = StorageFactory(registry).create(
            self._descriptor.storage.identifier
        )
        if not isinstance(storage, SQLiteStorage):
            raise StorageException("factory did not create SQLiteStorage")
        return storage

    def create_storage(self) -> SQLiteStorage:
        """Create and return the concrete Storage adapter."""
        return self.create()

    def create_connector(self) -> SQLiteConnector:
        """Create SQLiteConnector through the public ConnectorFactory."""
        registry = ConnectorRegistry()
        registry.register(
            self._descriptor.connector,
            lambda: SQLiteConnector(
                self._resolver.database,
                self._descriptor,
            ),
        )
        connector = ConnectorFactory(registry).create(
            self._descriptor.connector.identifier
        )
        if not isinstance(connector, SQLiteConnector):
            raise StorageException("factory did not create SQLiteConnector")
        return connector


__all__ = ["SQLiteStorageFactory"]
