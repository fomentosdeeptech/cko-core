"""Concrete Connector integration for SQLite structured storage."""

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

from .descriptor import SQLiteDescriptor
from .result import SQLiteResult
from .session import SQLiteSession
from .storage import SQLiteStorage


class SQLiteConnector(Connector):
    """Expose SQLiteStorage through the public Connector port."""

    def __init__(
        self,
        database: str | Path,
        descriptor: SQLiteDescriptor | None = None,
        validator: ConnectorValidator | None = None,
        storage: SQLiteStorage | None = None,
    ) -> None:
        self._sqlite_descriptor = descriptor or SQLiteDescriptor()
        self._validator = validator or ConnectorValidator()
        if not isinstance(self._validator, ConnectorValidator):
            raise ConnectorException("validator must be ConnectorValidator")
        self._storage = storage or SQLiteStorage(
            database,
            self._sqlite_descriptor.storage,
        )
        if not isinstance(self._storage, SQLiteStorage):
            raise ConnectorException("storage must be SQLiteStorage")
        if self._storage.descriptor != self._sqlite_descriptor.storage:
            raise ConnectorException("SQLite storage descriptor mismatch")
        self._validator.validate_descriptor(self.descriptor)

    @property
    def descriptor(self) -> ConnectorDescriptor:
        """Return the canonical public Connector descriptor."""
        return self._sqlite_descriptor.connector

    @property
    def storage(self) -> SQLiteStorage:
        """Return the composed SQLiteStorage adapter."""
        return self._storage

    def execute(self, session: ConnectorSession) -> ConnectorResult:
        """Execute one connector operation through public session contracts."""
        try:
            self._validator.validate_session(session, self.descriptor)
            sqlite_session = SQLiteSession.from_connector(
                session,
                self._storage,
            )
            with sqlite_session:
                storage_result = sqlite_session.execute()
            return SQLiteResult.from_storage(
                sqlite_session,
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


__all__ = ["SQLiteConnector"]
