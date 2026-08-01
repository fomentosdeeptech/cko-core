"""Session bridge between public Connector and Storage contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping, Self

from cko.core.connectors import ConnectorSession, ConnectorSessionState
from cko.core.storage import (
    StorageContext,
    StorageException,
    StorageLocation,
    StorageOperation,
    StorageSession,
    StorageSessionState,
)

from .descriptor import FILESYSTEM_SCHEMA_VERSION


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


@dataclass(frozen=True, slots=True)
class FilesystemSession:
    """Bind equivalent public ConnectorSession and StorageSession values."""

    connector_session: ConnectorSession
    storage_session: StorageSession
    schema_version: str = FILESYSTEM_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.connector_session, ConnectorSession):
            raise StorageException(
                "connector_session must be ConnectorSession"
            )
        if not isinstance(self.storage_session, StorageSession):
            raise StorageException("storage_session must be StorageSession")
        if self.connector_session.session_id != self.storage_session.session_id:
            raise StorageException("filesystem session identifiers differ")
        if self.connector_session.connector_id != self.storage_session.storage_id:
            raise StorageException("filesystem provider identifiers differ")
        if (
            self.connector_session.context.correlation_id
            != self.storage_session.context.correlation_id
        ):
            raise StorageException("filesystem correlation identifiers differ")
        if self.schema_version != FILESYSTEM_SCHEMA_VERSION:
            raise StorageException("unsupported FilesystemSession version")

    @classmethod
    def from_connector(cls, session: ConnectorSession) -> Self:
        """Translate a public ConnectorSession into a StorageSession bridge."""
        if not isinstance(session, ConnectorSession):
            raise StorageException("session must be ConnectorSession")
        operation = session.context.operation
        try:
            storage_operation = _STORAGE_OPERATIONS[operation]
        except KeyError as error:
            raise StorageException(
                f"unsupported filesystem operation: {operation}"
            ) from error
        parameters = dict(session.context.parameters)
        if "location" not in parameters:
            raise StorageException("filesystem session requires location")
        location = _location(parameters.pop("location"), "location")
        parameters["filesystem_operation"] = operation
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
        return cls(session, storage_session)

    def to_dict(self) -> dict[str, object]:
        """Serialize both public session contracts."""
        return {
            "schema_version": self.schema_version,
            "model": "filesystem_session",
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
        """Deserialize a strict filesystem session envelope."""
        expected = {
            "schema_version",
            "model",
            "connector_session",
            "storage_session",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise StorageException("invalid filesystem_session envelope")
        if (
            payload.get("schema_version") != FILESYSTEM_SCHEMA_VERSION
            or payload.get("model") != "filesystem_session"
        ):
            raise StorageException("invalid filesystem_session envelope")
        connector = payload["connector_session"]
        storage = payload["storage_session"]
        if not isinstance(connector, Mapping) or not isinstance(storage, Mapping):
            raise StorageException("invalid filesystem session models")
        return cls(
            ConnectorSession.from_dict(connector),
            StorageSession.from_dict(storage),
            str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize a filesystem session from strict JSON."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise StorageException("filesystem session JSON is invalid") from error
        if not isinstance(decoded, Mapping):
            raise StorageException("filesystem session JSON is invalid")
        return cls.from_dict(decoded)


__all__ = ["FilesystemSession"]
