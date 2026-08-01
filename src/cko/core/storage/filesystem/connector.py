"""Concrete Connector integration for filesystem storage."""

from __future__ import annotations

from pathlib import Path

from cko.core.connectors import (
    Connector,
    ConnectorDescriptor,
    ConnectorException,
    ConnectorResult,
    ConnectorSession,
    ConnectorValidator,
)
from cko.core.storage import StorageException

from .descriptor import FilesystemDescriptor
from .result import FilesystemResult
from .session import FilesystemSession
from .storage import FilesystemStorage


class FilesystemConnector(Connector):
    """Expose FilesystemStorage through the public Connector port."""

    def __init__(
        self,
        root: str | Path,
        descriptor: FilesystemDescriptor | None = None,
        validator: ConnectorValidator | None = None,
        storage: FilesystemStorage | None = None,
    ) -> None:
        self._filesystem_descriptor = descriptor or FilesystemDescriptor()
        self._validator = validator or ConnectorValidator()
        if not isinstance(self._validator, ConnectorValidator):
            raise ConnectorException("validator must be ConnectorValidator")
        self._storage = storage or FilesystemStorage(
            root,
            self._filesystem_descriptor.storage,
        )
        if not isinstance(self._storage, FilesystemStorage):
            raise ConnectorException("storage must be FilesystemStorage")
        if self._storage.descriptor != self._filesystem_descriptor.storage:
            raise ConnectorException("filesystem storage descriptor mismatch")
        self._validator.validate_descriptor(self.descriptor)

    @property
    def descriptor(self) -> ConnectorDescriptor:
        """Return the canonical public Connector descriptor."""
        return self._filesystem_descriptor.connector

    @property
    def storage(self) -> FilesystemStorage:
        """Return the composed FilesystemStorage adapter."""
        return self._storage

    def execute(self, session: ConnectorSession) -> ConnectorResult:
        """Execute one connector operation through public session contracts."""
        try:
            self._validator.validate_session(session, self.descriptor)
            filesystem_session = FilesystemSession.from_connector(session)
            storage_result = self._storage.execute(
                filesystem_session.storage_session
            )
            return FilesystemResult.from_storage(
                filesystem_session,
                storage_result,
            ).connector_result
        except (ConnectorException, StorageException) as error:
            session_id = getattr(session, "session_id", "invalid-session")
            return ConnectorResult(
                session_id=session_id,
                connector_id=self.descriptor.identifier,
                success=False,
                errors=(str(error),),
            )


__all__ = ["FilesystemConnector"]
