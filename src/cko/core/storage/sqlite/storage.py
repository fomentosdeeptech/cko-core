"""Concrete standard-library SQLite implementation of Storage."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import sqlite3
from collections.abc import Callable, Sequence
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Mapping

from cko.core.logging import get_logger
from cko.core.storage import (
    Storage,
    StorageDescriptor,
    StorageException,
    StorageLocation,
    StorageObject,
    StorageOperation,
    StorageResult,
    StorageSession,
    StorageValidator,
)

from .descriptor import SQLiteDescriptor
from .resolver import SQLiteLocationResolver


_SCHEMA = """
CREATE TABLE IF NOT EXISTS cko_storage_objects (
    namespace TEXT NOT NULL,
    object_key TEXT NOT NULL,
    payload TEXT NOT NULL,
    payload_size INTEGER NOT NULL,
    digest TEXT NOT NULL,
    object_metadata TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (namespace, object_key)
)
"""
_SELECT = """
SELECT namespace, object_key, payload, payload_size, digest,
       object_metadata, created_at, updated_at
FROM cko_storage_objects
"""


@dataclass(slots=True)
class _Transaction:
    connection: sqlite3.Connection
    owner: object
    failed: bool = False


class SQLiteStorage(Storage):
    """Persist structured logical objects in one SQLite database."""

    def __init__(
        self,
        database: str | Path,
        descriptor: StorageDescriptor | None = None,
        validator: StorageValidator | None = None,
        *,
        timeout: float = 5.0,
    ) -> None:
        self._resolver = SQLiteLocationResolver(database)
        self._descriptor = descriptor or SQLiteDescriptor().storage
        self._validator = validator or StorageValidator()
        if not isinstance(self._validator, StorageValidator):
            raise StorageException("validator must be StorageValidator")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            raise StorageException("timeout must be a positive number")
        self._timeout = float(timeout)
        self._validator.validate_descriptor(self._descriptor)
        self._logger = get_logger("core.storage.sqlite")
        self._current: ContextVar[_Transaction | None] = ContextVar(
            f"cko_sqlite_transaction_{id(self)}",
            default=None,
        )
        self._closed = False
        self._resolver.database.parent.mkdir(parents=True, exist_ok=True)
        connection = self._connect()
        try:
            connection.execute(_SCHEMA)
            connection.commit()
        except sqlite3.DatabaseError as error:
            raise self._database_error(error) from error
        finally:
            self._close_connection(connection)

    @property
    def descriptor(self) -> StorageDescriptor:
        """Return the canonical public Storage descriptor."""
        return self._descriptor

    @property
    def resolver(self) -> SQLiteLocationResolver:
        """Return the database and logical location resolver."""
        return self._resolver

    @property
    def database(self) -> Path:
        """Return the normalized SQLite database path."""
        return self._resolver.database

    def __enter__(self) -> SQLiteStorage:
        """Return an open adapter context."""
        if self._closed:
            raise StorageException("SQLiteStorage is closed")
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: object,
    ) -> bool:
        """Close the adapter context."""
        self.close()
        return False

    def close(self) -> None:
        """Roll back an active transaction and close the adapter."""
        transaction = self._current.get()
        if transaction is not None:
            try:
                transaction.connection.rollback()
                self._log("sqlite_rollback", reason="storage_close")
            finally:
                self._close_connection(transaction.connection)
                self._current.set(None)
        if not self._closed:
            self._closed = True
            self._log("sqlite_close", database=str(self.database))

    def execute(self, session: StorageSession) -> StorageResult:
        """Execute the operation represented by a validated StorageSession."""
        self._ensure_open()
        self._validator.validate_session(session, self._descriptor)
        operation = session.context.operation
        sqlite_operation = session.context.parameters.get(
            "sqlite_operation",
            operation.value,
        )
        dispatch: dict[str, Callable[[StorageSession], StorageResult]] = {
            "copy": self.copy,
            "create": self.create,
            "delete": self.delete,
            "exists": self.exists,
            "list": self.list,
            "metadata": self.metadata,
            "move": self.move,
            "read": self.read,
            "write": self.write,
        }
        if not isinstance(sqlite_operation, str):
            return self._failure(session, "sqlite_operation must be a string")
        handler = dispatch.get(sqlite_operation)
        if handler is None:
            return self._failure(
                session,
                f"unsupported SQLite operation: {sqlite_operation}",
            )
        mapped = {
            "copy": StorageOperation.WRITE,
            "create": StorageOperation.WRITE,
            "move": StorageOperation.WRITE,
        }
        compatible = mapped.get(sqlite_operation)
        if compatible is None:
            try:
                compatible = StorageOperation(sqlite_operation)
            except ValueError:
                return self._failure(
                    session,
                    f"unsupported SQLite operation: {sqlite_operation}",
                )
        if operation is not compatible:
            return self._failure(
                session,
                "SQLite operation is incompatible with StorageOperation",
            )
        return handler(session)

    def create(self, session: StorageSession) -> StorageResult:
        """Create one structured object without replacing an existing row."""
        return self._run(session, "sqlite_write", self._create)

    def read(self, session: StorageSession) -> StorageResult:
        """Read and deserialize one structured object."""
        return self._run(session, "sqlite_read", self._read)

    def write(self, session: StorageSession) -> StorageResult:
        """Create or replace one structured object atomically."""
        return self._run(session, "sqlite_write", self._write)

    def delete(self, session: StorageSession) -> StorageResult:
        """Delete one structured object."""
        return self._run(session, "sqlite_delete", self._delete)

    def exists(self, session: StorageSession) -> StorageResult:
        """Report whether one logical location exists."""
        return self._run(session, "sqlite_exists", self._exists)

    def list(self, session: StorageSession) -> StorageResult:
        """List a logical namespace in deterministic key order."""
        return self._run(session, "sqlite_list", self._list)

    def metadata(self, session: StorageSession) -> StorageResult:
        """Return metadata for one structured object."""
        return self._run(session, "sqlite_metadata", self._metadata)

    def copy(self, session: StorageSession) -> StorageResult:
        """Copy one structured object to another logical location."""
        return self._run(session, "sqlite_write", self._copy)

    def move(self, session: StorageSession) -> StorageResult:
        """Move one structured object to another logical location."""
        return self._run(session, "sqlite_write", self._move)

    def transaction(self, session: object) -> object:
        """Bind a SQLiteSession to this adapter for explicit transactions."""
        from .session import SQLiteSession

        if not isinstance(session, SQLiteSession):
            raise StorageException("session must be SQLiteSession")
        return session.bind(self)

    def _run(
        self,
        session: StorageSession,
        event: str,
        operation: Callable[[sqlite3.Connection, StorageSession], StorageResult],
    ) -> StorageResult:
        self._validator.validate_session(session, self._descriptor)
        transaction = self._current.get()
        local = transaction is None
        connection: sqlite3.Connection | None = None
        try:
            if local:
                connection = self._connect()
                connection.execute("BEGIN")
                self._log("sqlite_begin", session_id=session.session_id)
            else:
                connection = transaction.connection
            result = operation(connection, session)
            if local:
                connection.commit()
                self._log("sqlite_commit", session_id=session.session_id)
        except (
            StorageException,
            sqlite3.Error,
            TypeError,
            ValueError,
            UnicodeError,
        ) as error:
            if transaction is not None:
                transaction.failed = True
            if local and connection is not None:
                try:
                    connection.rollback()
                finally:
                    self._log(
                        "sqlite_rollback",
                        session_id=session.session_id,
                    )
            result = self._failure(session, self._error_message(error))
        finally:
            if local and connection is not None:
                self._close_connection(connection)
        self._log(
            event,
            location=session.context.location.to_dict(),
            success=result.success,
        )
        return result

    def _create(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        namespace, key = self._resolver.resolve(session.context.location)
        payload, size, digest = self._payload(session.context.parameters)
        metadata = self._metadata_json(session.context.parameters)
        instant = self._instant()
        connection.execute(
            """
            INSERT INTO cko_storage_objects (
                namespace, object_key, payload, payload_size, digest,
                object_metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                namespace,
                key,
                payload,
                size,
                digest,
                metadata,
                instant,
                instant,
            ),
        )
        row = self._fetch(connection, namespace, key)
        return self._success(session, (self._object(row),))

    def _write(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        namespace, key = self._resolver.resolve(session.context.location)
        payload, size, digest = self._payload(session.context.parameters)
        metadata = self._metadata_json(session.context.parameters)
        instant = self._instant()
        connection.execute(
            """
            INSERT INTO cko_storage_objects (
                namespace, object_key, payload, payload_size, digest,
                object_metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(namespace, object_key) DO UPDATE SET
                payload = excluded.payload,
                payload_size = excluded.payload_size,
                digest = excluded.digest,
                object_metadata = excluded.object_metadata,
                updated_at = excluded.updated_at
            """,
            (
                namespace,
                key,
                payload,
                size,
                digest,
                metadata,
                instant,
                instant,
            ),
        )
        row = self._fetch(connection, namespace, key)
        return self._success(session, (self._object(row),))

    def _read(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        namespace, key = self._resolver.resolve(session.context.location)
        row = self._fetch(connection, namespace, key)
        decoded = json.loads(str(row["payload"]))
        metadata: dict[str, object] = {
            "serialized_value": str(row["payload"]),
        }
        if (
            isinstance(decoded, dict)
            and decoded.get("kind") == "bytes"
            and set(decoded) == {"kind", "content_base64"}
        ):
            metadata["content_base64"] = decoded["content_base64"]
        elif (
            isinstance(decoded, dict)
            and decoded.get("kind") == "json"
            and set(decoded) == {"kind", "value"}
        ):
            metadata["value"] = decoded["value"]
        else:
            raise StorageException("stored payload envelope is invalid")
        return self._success(session, (self._object(row),), metadata)

    def _delete(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        namespace, key = self._resolver.resolve(session.context.location)
        row = self._fetch(connection, namespace, key)
        cursor = connection.execute(
            """
            DELETE FROM cko_storage_objects
            WHERE namespace = ? AND object_key = ?
            """,
            (namespace, key),
        )
        if cursor.rowcount != 1:
            raise StorageException("SQLite object deletion failed")
        return self._success(session, (self._object(row),))

    def _exists(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        namespace, key = self._resolver.resolve(session.context.location)
        row = connection.execute(
            """
            SELECT 1 FROM cko_storage_objects
            WHERE namespace = ? AND object_key = ?
            """,
            (namespace, key),
        ).fetchone()
        return self._success(session, metadata={"exists": row is not None})

    def _list(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        namespace, prefix = self._resolver.resolve(session.context.location)
        if prefix == ".":
            rows = connection.execute(
                f"{_SELECT} WHERE namespace = ? ORDER BY object_key",
                (namespace,),
            ).fetchall()
        else:
            escaped = self._like(prefix.rstrip("/") + "/")
            rows = connection.execute(
                f"""
                {_SELECT}
                WHERE namespace = ?
                  AND (object_key = ? OR object_key LIKE ? ESCAPE '\\')
                ORDER BY object_key
                """,
                (namespace, prefix, f"{escaped}%"),
            ).fetchall()
        objects = tuple(self._object(row) for row in rows)
        return self._success(
            session,
            objects,
            {"count": len(objects)},
        )

    def _metadata(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        namespace, key = self._resolver.resolve(session.context.location)
        return self._success(
            session,
            (self._object(self._fetch(connection, namespace, key)),),
        )

    def _copy(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        source_namespace, source_key = self._resolver.resolve(
            session.context.location
        )
        target_namespace, target_key = self._resolver.resolve(
            self._target(session)
        )
        source = self._fetch(connection, source_namespace, source_key)
        instant = self._instant()
        connection.execute(
            """
            INSERT INTO cko_storage_objects (
                namespace, object_key, payload, payload_size, digest,
                object_metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                target_namespace,
                target_key,
                source["payload"],
                source["payload_size"],
                source["digest"],
                source["object_metadata"],
                instant,
                instant,
            ),
        )
        return self._success(
            session,
            (self._object(self._fetch(
                connection,
                target_namespace,
                target_key,
            )),),
        )

    def _move(
        self,
        connection: sqlite3.Connection,
        session: StorageSession,
    ) -> StorageResult:
        result = self._copy(connection, session)
        source_namespace, source_key = self._resolver.resolve(
            session.context.location
        )
        connection.execute(
            """
            DELETE FROM cko_storage_objects
            WHERE namespace = ? AND object_key = ?
            """,
            (source_namespace, source_key),
        )
        return result

    def _fetch(
        self,
        connection: sqlite3.Connection,
        namespace: str,
        key: str,
    ) -> sqlite3.Row:
        row = connection.execute(
            f"{_SELECT} WHERE namespace = ? AND object_key = ?",
            (namespace, key),
        ).fetchone()
        if row is None:
            raise StorageException(
                "SQLite object does not exist",
                code="object_not_found",
                storage_id=self._descriptor.identifier,
            )
        return row

    def _object(self, row: sqlite3.Row) -> StorageObject:
        return StorageObject(
            object_id=f"{row['namespace']}:{row['object_key']}",
            location=StorageLocation(
                namespace=str(row["namespace"]),
                key=str(row["object_key"]),
            ),
            size=int(row["payload_size"]),
            digest=str(row["digest"]),
            metadata={
                "created_at": str(row["created_at"]),
                "updated_at": str(row["updated_at"]),
                "value_metadata": json.loads(str(row["object_metadata"])),
            },
        )

    @classmethod
    def _payload(
        cls,
        parameters: Mapping[str, object],
    ) -> tuple[str, int, str]:
        content = parameters.get("content_base64")
        if content is not None:
            if "value" in parameters or "content" in parameters:
                raise StorageException(
                    "content_base64 is mutually exclusive with value and content"
                )
            if not isinstance(content, str):
                raise StorageException("content_base64 must be a string")
            try:
                binary = base64.b64decode(content, validate=True)
            except (binascii.Error, ValueError) as error:
                raise StorageException("content_base64 is invalid") from error
            envelope: object = {
                "kind": "bytes",
                "content_base64": base64.b64encode(binary).decode("ascii"),
            }
        else:
            if "value" in parameters and "content" in parameters:
                raise StorageException(
                    "value and content are mutually exclusive"
                )
            value = parameters.get("value", parameters.get("content"))
            envelope = {"kind": "json", "value": cls._primitive(value)}
        serialized = cls._json(envelope, "value")
        encoded = serialized.encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        return serialized, len(encoded), f"sha256:{digest}"

    @classmethod
    def _metadata_json(cls, parameters: Mapping[str, object]) -> str:
        metadata = parameters.get("metadata", {})
        if not isinstance(metadata, Mapping):
            raise StorageException("metadata must be a mapping")
        return cls._json(cls._primitive(metadata), "metadata")

    @staticmethod
    def _json(value: object, name: str) -> str:
        try:
            return json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        except (TypeError, ValueError) as error:
            raise StorageException(
                f"{name} must be deterministically JSON serializable"
            ) from error

    @classmethod
    def _primitive(cls, value: object) -> object:
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, Mapping):
            return {
                str(key): cls._primitive(item)
                for key, item in value.items()
            }
        if isinstance(value, (tuple, list)):
            return [cls._primitive(item) for item in value]
        raise StorageException(
            f"value must be deterministically JSON serializable: "
            f"{type(value).__name__}"
        )

    @staticmethod
    def _target(session: StorageSession) -> StorageLocation:
        target = session.context.parameters.get("target")
        if isinstance(target, StorageLocation):
            return target
        if not isinstance(target, Mapping):
            raise StorageException("target must be a StorageLocation envelope")
        return StorageLocation.from_dict(target)

    def _success(
        self,
        session: StorageSession,
        objects: Sequence[StorageObject] = (),
        metadata: Mapping[str, object] | None = None,
    ) -> StorageResult:
        return StorageResult(
            storage_id=self._descriptor.identifier,
            operation=session.context.operation,
            success=True,
            objects=tuple(objects),
            metadata={} if metadata is None else metadata,
        )

    def _failure(self, session: StorageSession, message: str) -> StorageResult:
        transaction = self._current.get()
        if transaction is not None:
            transaction.failed = True
        return StorageResult(
            storage_id=self._descriptor.identifier,
            operation=session.context.operation,
            success=False,
            message=message or "SQLite operation failed",
        )

    def _connect(self) -> sqlite3.Connection:
        self._ensure_open(allow_initial=True)
        try:
            connection = sqlite3.connect(
                self.database,
                timeout=self._timeout,
                isolation_level=None,
            )
            connection.row_factory = sqlite3.Row
            connection.execute(
                f"PRAGMA busy_timeout = {int(self._timeout * 1000)}"
            )
            connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as error:
            raise self._database_error(error) from error
        self._log("sqlite_open", database=str(self.database))
        return connection

    def _close_connection(self, connection: sqlite3.Connection) -> None:
        try:
            connection.close()
        finally:
            self._log("sqlite_close", database=str(self.database))

    def _begin_session(self, session: object) -> None:
        self._ensure_open()
        if self._current.get() is not None:
            raise StorageException("a SQLite transaction is already active")
        connection = self._connect()
        try:
            connection.execute("BEGIN")
        except sqlite3.Error as error:
            self._close_connection(connection)
            raise self._database_error(error) from error
        self._current.set(_Transaction(connection, session))
        self._log("sqlite_begin", session_id=self._session_id(session))

    def _commit_session(self, session: object) -> None:
        transaction = self._owned_transaction(session)
        if transaction.failed:
            raise StorageException("failed SQLite transaction cannot be committed")
        try:
            transaction.connection.commit()
            self._log("sqlite_commit", session_id=self._session_id(session))
        except sqlite3.Error as error:
            raise self._database_error(error) from error
        finally:
            self._close_connection(transaction.connection)
            self._current.set(None)

    def _rollback_session(self, session: object) -> None:
        transaction = self._owned_transaction(session)
        try:
            transaction.connection.rollback()
            self._log("sqlite_rollback", session_id=self._session_id(session))
        except sqlite3.Error as error:
            raise self._database_error(error) from error
        finally:
            self._close_connection(transaction.connection)
            self._current.set(None)

    def _session_failed(self, session: object) -> bool:
        return self._owned_transaction(session).failed

    def _owned_transaction(self, session: object) -> _Transaction:
        transaction = self._current.get()
        if transaction is None or transaction.owner is not session:
            raise StorageException("SQLite transaction is not owned by session")
        return transaction

    def _ensure_open(self, *, allow_initial: bool = False) -> None:
        if getattr(self, "_closed", False) and not allow_initial:
            raise StorageException("SQLiteStorage is closed")

    def _database_error(self, error: sqlite3.Error) -> StorageException:
        return StorageException(
            f"SQLite database error: {error}",
            code="sqlite_database_error",
            storage_id=self._descriptor.identifier,
        )

    @staticmethod
    def _error_message(error: Exception) -> str:
        if isinstance(error, sqlite3.Error):
            return f"SQLite database error: {error}"
        return str(error) or "SQLite operation failed"

    @staticmethod
    def _instant() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _like(value: str) -> str:
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    @staticmethod
    def _session_id(session: object) -> str:
        storage_session = getattr(session, "storage_session", None)
        return str(getattr(storage_session, "session_id", "unknown"))

    def _log(self, event: str, **context: object) -> None:
        self._logger.info(
            event,
            extra={"event": event, "context": context},
        )


__all__ = ["SQLiteStorage"]
