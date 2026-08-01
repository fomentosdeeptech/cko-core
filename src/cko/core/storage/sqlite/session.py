"""Transactional session bridge between Connector and Storage contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Mapping, Self

from cko.core.connectors import ConnectorSession, ConnectorSessionState
from cko.core.storage import (
    StorageContext,
    StorageException,
    StorageLocation,
    StorageOperation,
    StorageResult,
    StorageSession,
    StorageSessionState,
)

from .descriptor import SQLITE_SCHEMA_VERSION

if TYPE_CHECKING:
    from .storage import SQLiteStorage


_STORAGE_OPERATIONS = {
    "copy": StorageOperation.WRITE,
    "create": StorageOperation.WRITE,
    "delete": StorageOperation.DELETE,
    "exists": StorageOperation.EXISTS,
    "list": StorageOperation.LIST,
    "metadata": StorageOperation.METADATA,
    "move": StorageOperation.WRITE,
    "read": StorageOperation.READ,
    "write": StorageOperation.WRITE,
}
_SESSION_STATES = {
    ConnectorSessionState.STARTED: StorageSessionState.STARTED,
    ConnectorSessionState.FINISHED: StorageSessionState.FINISHED,
    ConnectorSessionState.FAILED: StorageSessionState.FAILED,
}


def _location(value: object, name: str) -> StorageLocation:
    if isinstance(value, StorageLocation):
        return value
    if not isinstance(value, Mapping):
        raise StorageException(f"{name} must be a StorageLocation envelope")
    return StorageLocation.from_dict(value)


@dataclass(slots=True)
class SQLiteSession:
    """Bind public sessions and control one isolated SQLite transaction."""

    connector_session: ConnectorSession
    storage_session: StorageSession
    schema_version: str = SQLITE_SCHEMA_VERSION
    _storage: SQLiteStorage | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    _active: bool = field(default=False, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.connector_session, ConnectorSession):
            raise StorageException(
                "connector_session must be ConnectorSession"
            )
        if not isinstance(self.storage_session, StorageSession):
            raise StorageException("storage_session must be StorageSession")
        if self.connector_session.session_id != self.storage_session.session_id:
            raise StorageException("SQLite session identifiers differ")
        if self.connector_session.connector_id != self.storage_session.storage_id:
            raise StorageException("SQLite provider identifiers differ")
        if (
            self.connector_session.context.correlation_id
            != self.storage_session.context.correlation_id
        ):
            raise StorageException("SQLite correlation identifiers differ")
        if self.schema_version != SQLITE_SCHEMA_VERSION:
            raise StorageException("unsupported SQLiteSession version")
        if self._storage is not None:
            self.bind(self._storage)

    @classmethod
    def from_connector(
        cls,
        session: ConnectorSession,
        storage: SQLiteStorage | None = None,
    ) -> Self:
        """Translate a ConnectorSession into a StorageSession bridge."""
        if not isinstance(session, ConnectorSession):
            raise StorageException("session must be ConnectorSession")
        operation = session.context.operation
        try:
            storage_operation = _STORAGE_OPERATIONS[operation]
        except KeyError as error:
            raise StorageException(
                f"unsupported SQLite operation: {operation}"
            ) from error
        parameters = dict(session.context.parameters)
        if "location" not in parameters:
            raise StorageException("SQLite session requires location")
        location = _location(parameters.pop("location"), "location")
        parameters["sqlite_operation"] = operation
        storage_context = StorageContext(
            correlation_id=session.context.correlation_id,
            operation=storage_operation,
            location=location,
            parameters=parameters,
        )
        storage_session = StorageSession(
            session_id=session.session_id,
            storage_id=session.connector_id,
            context=storage_context,
            state=_SESSION_STATES[session.state],
            started_at=session.started_at,
            finished_at=session.finished_at,
            failure=session.failure,
            metadata=session.metadata,
        )
        return cls(session, storage_session, _storage=storage)

    def bind(self, storage: SQLiteStorage) -> Self:
        """Bind this public session bridge to one concrete adapter."""
        from .storage import SQLiteStorage

        if not isinstance(storage, SQLiteStorage):
            raise StorageException("storage must be SQLiteStorage")
        if storage.descriptor.identifier != self.storage_session.storage_id:
            raise StorageException("SQLite session storage identifier mismatch")
        if self._active:
            raise StorageException("cannot rebind an active SQLiteSession")
        self._storage = storage
        return self

    def __enter__(self) -> Self:
        """Begin an isolated transaction for this session."""
        if self._storage is None:
            raise StorageException("SQLiteSession is not bound to storage")
        if self._active:
            raise StorageException("SQLiteSession is already active")
        self._storage._begin_session(self)
        self._active = True
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: object,
    ) -> bool:
        """Commit successful work and roll back failed work."""
        if not self._active or self._storage is None:
            return False
        if exception_type is not None or self._storage._session_failed(self):
            self.rollback()
        else:
            self.commit()
        return False

    def execute(self, session: StorageSession | None = None) -> StorageResult:
        """Execute a public StorageSession inside this transaction."""
        if self._storage is None:
            raise StorageException("SQLiteSession is not bound to storage")
        if not self._active:
            raise StorageException("SQLiteSession is not active")
        selected = self.storage_session if session is None else session
        if not isinstance(selected, StorageSession):
            raise StorageException("session must be StorageSession")
        if selected.storage_id != self.storage_session.storage_id:
            raise StorageException("transaction storage identifier mismatch")
        return self._storage.execute(selected)

    def commit(self) -> None:
        """Commit and close this transaction."""
        if self._storage is None or not self._active:
            raise StorageException("SQLiteSession is not active")
        self._storage._commit_session(self)
        self._active = False

    def rollback(self) -> None:
        """Roll back and close this transaction."""
        if self._storage is None or not self._active:
            raise StorageException("SQLiteSession is not active")
        self._storage._rollback_session(self)
        self._active = False

    def to_dict(self) -> dict[str, object]:
        """Serialize both public session contracts."""
        return {
            "schema_version": self.schema_version,
            "model": "sqlite_session",
            "connector_session": self.connector_session.to_dict(),
            "storage_session": self.storage_session.to_dict(),
        }

    def to_json(self) -> str:
        """Serialize this bridge to deterministic JSON."""
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict SQLite session envelope."""
        expected = {
            "schema_version",
            "model",
            "connector_session",
            "storage_session",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise StorageException("invalid sqlite_session envelope")
        if (
            payload.get("schema_version") != SQLITE_SCHEMA_VERSION
            or payload.get("model") != "sqlite_session"
        ):
            raise StorageException("invalid sqlite_session envelope")
        connector = payload["connector_session"]
        storage = payload["storage_session"]
        if not isinstance(connector, Mapping) or not isinstance(storage, Mapping):
            raise StorageException("invalid SQLite session models")
        return cls(
            ConnectorSession.from_dict(connector),
            StorageSession.from_dict(storage),
            str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize a SQLite session from strict JSON."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise StorageException("SQLite session JSON is invalid") from error
        if not isinstance(decoded, Mapping):
            raise StorageException("SQLite session JSON is invalid")
        return cls.from_dict(decoded)


__all__ = ["SQLiteSession"]
