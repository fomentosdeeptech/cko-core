"""Safe resolution of the physical SQLite database and logical locations."""

from __future__ import annotations

from pathlib import Path

from cko.core.storage import StorageException, StorageLocation


class SQLiteLocationResolver:
    """Validate a database path and technology-neutral row locations."""

    def __init__(self, database: str | Path) -> None:
        if not isinstance(database, (str, Path)) or not str(database).strip():
            raise StorageException("database must be a filesystem path")
        self._database = Path(database).expanduser().resolve(strict=False)
        if self._database.exists() and self._database.is_dir():
            raise StorageException("database path must not be a directory")

    @property
    def database(self) -> Path:
        """Return the normalized physical database path."""
        return self._database

    def resolve(self, location: StorageLocation) -> tuple[str, str]:
        """Resolve a logical location into a validated namespace and key."""
        if not isinstance(location, StorageLocation):
            raise StorageException("location must be StorageLocation")
        namespace = self._part(location.namespace, "namespace")
        key = self._part(location.key, "key")
        return namespace, key

    @staticmethod
    def _part(value: str, name: str) -> str:
        if "\x00" in value:
            raise StorageException(
                f"{name} must not contain null characters",
                code="invalid_location",
            )
        return value


__all__ = ["SQLiteLocationResolver"]
