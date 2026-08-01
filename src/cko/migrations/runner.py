"""Executor de migrações SQLite do CKO."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import sqlite3


@dataclass(frozen=True, slots=True)
class Migration:
    version: int
    name: str
    path: Path


class MigrationRunner:
    def __init__(self, database_path: Path, migrations_dir: Path) -> None:
        self.database_path = database_path
        self.migrations_dir = migrations_dir

    def discover(self) -> list[Migration]:
        migrations: list[Migration] = []
        for path in sorted(self.migrations_dir.glob("*.sql")):
            prefix, _, name = path.stem.partition("_")
            if not prefix.isdigit():
                continue
            migrations.append(Migration(int(prefix), name, path))
        return migrations

    def apply_all(self) -> list[int]:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        applied_now: list[int] = []

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                )
                """
            )
            applied = {
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_version"
                ).fetchall()
            }

            for migration in self.discover():
                if migration.version in applied:
                    continue

                sql = migration.path.read_text(encoding="utf-8")
                connection.executescript(sql)
                connection.execute(
                    """
                    INSERT INTO schema_version(version, name, applied_at)
                    VALUES (?, ?, ?)
                    """,
                    (
                        migration.version,
                        migration.name,
                        datetime.now(UTC).isoformat(),
                    ),
                )
                applied_now.append(migration.version)

            connection.commit()

        return applied_now
