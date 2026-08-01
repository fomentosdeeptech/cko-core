from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from .database import Database, DatabaseError

PATTERN = re.compile(r"^(?P<version>\d+)_(?P<name>[A-Za-z0-9_-]+)\.sql$")


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path


class MigrationManager:
    def __init__(self, database: Database, migrations_dir: str | Path) -> None:
        self.database = database
        self.migrations_dir = Path(migrations_dir)

    def discover(self) -> list[Migration]:
        if not self.migrations_dir.exists():
            raise DatabaseError(f"Pasta de migrações não encontrada: {self.migrations_dir}")

        result: list[Migration] = []
        for path in sorted(self.migrations_dir.glob("*.sql")):
            match = PATTERN.match(path.name)
            if match:
                result.append(
                    Migration(
                        int(match.group("version")),
                        match.group("name"),
                        path,
                    )
                )

        versions = [m.version for m in result]
        if len(versions) != len(set(versions)):
            raise DatabaseError("Versões de migração duplicadas.")

        return result

    @staticmethod
    def ensure_control(conn) -> None:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS cko_schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )"""
        )

    def current_version(self) -> int:
        conn = self.database.connect()
        try:
            self.ensure_control(conn)
            conn.commit()
            row = conn.execute(
                "SELECT COALESCE(MAX(version), 0) FROM cko_schema_migrations"
            ).fetchone()
            return int(row[0])
        finally:
            conn.close()

    def migrate(self) -> list[int]:
        applied: list[int] = []

        conn = self.database.connect()
        try:
            self.ensure_control(conn)
            conn.commit()
            existing = {
                int(r[0])
                for r in conn.execute(
                    "SELECT version FROM cko_schema_migrations"
                ).fetchall()
            }
        finally:
            conn.close()

        for migration in self.discover():
            if migration.version in existing:
                continue

            sql = migration.path.read_text(encoding="utf-8")
            conn = self.database.connect()
            try:
                conn.executescript("BEGIN IMMEDIATE;\n" + sql)
                conn.execute(
                    """INSERT INTO cko_schema_migrations(
                        version, name, applied_at
                    ) VALUES (?, ?, ?)""",
                    (
                        migration.version,
                        migration.name,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

            applied.append(migration.version)

        return applied
