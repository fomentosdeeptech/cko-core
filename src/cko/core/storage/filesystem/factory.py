"""Factory composition for filesystem Connector and Storage adapters."""

from __future__ import annotations

from pathlib import Path

from cko.core.connectors import ConnectorFactory, ConnectorRegistry
from cko.core.storage import (
    StorageException,
    StorageFactory,
    StorageRegistry,
)

from .connector import FilesystemConnector
from .descriptor import FilesystemDescriptor
from .storage import FilesystemStorage
from .validator import FilesystemStorageValidator


class FilesystemStorageFactory:
    """Compose concrete adapters through the public generic factories."""

    def __init__(
        self,
        root: str | Path,
        descriptor: FilesystemDescriptor | None = None,
        validator: FilesystemStorageValidator | None = None,
    ) -> None:
        self._validator = validator or FilesystemStorageValidator()
        if not isinstance(self._validator, FilesystemStorageValidator):
            raise StorageException(
                "validator must be FilesystemStorageValidator"
            )
        self._resolver = self._validator.validate_root(root)
        self._descriptor = self._validator.validate_descriptor(
            descriptor or FilesystemDescriptor()
        )

    @property
    def descriptor(self) -> FilesystemDescriptor:
        """Return the descriptor used for factory composition."""
        return self._descriptor

    def create(self) -> FilesystemStorage:
        """Create FilesystemStorage through StorageRegistry and StorageFactory."""
        registry = StorageRegistry()
        registry.register(
            self._descriptor.storage,
            lambda: FilesystemStorage(
                self._resolver.root,
                self._descriptor.storage,
            ),
        )
        storage = StorageFactory(registry).create(
            self._descriptor.storage.identifier
        )
        if not isinstance(storage, FilesystemStorage):
            raise StorageException("factory did not create FilesystemStorage")
        return storage

    def create_storage(self) -> FilesystemStorage:
        """Create and return the concrete Storage adapter."""
        return self.create()

    def create_connector(self) -> FilesystemConnector:
        """Create FilesystemConnector through the public ConnectorFactory."""
        registry = ConnectorRegistry()
        registry.register(
            self._descriptor.connector,
            lambda: FilesystemConnector(
                self._resolver.root,
                self._descriptor,
            ),
        )
        connector = ConnectorFactory(registry).create(
            self._descriptor.connector.identifier
        )
        if not isinstance(connector, FilesystemConnector):
            raise StorageException("factory did not create FilesystemConnector")
        return connector


__all__ = ["FilesystemStorageFactory"]
