"""Result bridge between public Connector and Storage contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping, Self

from cko.core.connectors import ConnectorResult
from cko.core.storage import StorageException, StorageResult

from .descriptor import SQLITE_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SQLiteResult:
    """Bind equivalent public ConnectorResult and StorageResult values."""

    connector_result: ConnectorResult
    storage_result: StorageResult
    schema_version: str = SQLITE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.connector_result, ConnectorResult):
            raise StorageException("connector_result must be ConnectorResult")
        if not isinstance(self.storage_result, StorageResult):
            raise StorageException("storage_result must be StorageResult")
        if self.connector_result.connector_id != self.storage_result.storage_id:
            raise StorageException("SQLite result identifiers differ")
        if self.connector_result.success != self.storage_result.success:
            raise StorageException("SQLite result success values differ")
        if self.schema_version != SQLITE_SCHEMA_VERSION:
            raise StorageException("unsupported SQLiteResult version")

    @classmethod
    def from_storage(cls, session: object, result: StorageResult) -> Self:
        """Create a ConnectorResult containing the public StorageResult."""
        from .session import SQLiteSession

        if not isinstance(session, SQLiteSession):
            raise StorageException("session must be SQLiteSession")
        if not isinstance(result, StorageResult):
            raise StorageException("result must be StorageResult")
        errors = () if result.success else (result.message or "storage failure",)
        connector = ConnectorResult(
            session_id=session.connector_session.session_id,
            connector_id=result.storage_id,
            success=result.success,
            data={"storage_result": result.to_dict()},
            errors=errors,
            metadata={"operation": session.connector_session.context.operation},
        )
        return cls(connector, result)

    def to_dict(self) -> dict[str, object]:
        """Serialize both public result contracts."""
        return {
            "schema_version": self.schema_version,
            "model": "sqlite_result",
            "connector_result": self.connector_result.to_dict(),
            "storage_result": self.storage_result.to_dict(),
        }

    def to_json(self) -> str:
        """Serialize this result bridge to deterministic JSON."""
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Self:
        """Deserialize a strict SQLite result envelope."""
        expected = {
            "schema_version",
            "model",
            "connector_result",
            "storage_result",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise StorageException("invalid sqlite_result envelope")
        if (
            payload.get("schema_version") != SQLITE_SCHEMA_VERSION
            or payload.get("model") != "sqlite_result"
        ):
            raise StorageException("invalid sqlite_result envelope")
        connector = payload["connector_result"]
        storage = payload["storage_result"]
        if not isinstance(connector, Mapping) or not isinstance(storage, Mapping):
            raise StorageException("invalid SQLite result models")
        return cls(
            ConnectorResult.from_dict(connector),
            StorageResult.from_dict(storage),
            str(payload["schema_version"]),
        )

    @classmethod
    def from_json(cls, payload: str) -> Self:
        """Deserialize a SQLite result from strict JSON."""
        try:
            decoded = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as error:
            raise StorageException("SQLite result JSON is invalid") from error
        if not isinstance(decoded, Mapping):
            raise StorageException("SQLite result JSON is invalid")
        return cls.from_dict(decoded)


__all__ = ["SQLiteResult"]
