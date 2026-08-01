from pathlib import Path
import sqlite3

from cko.migrations import MigrationRunner


def test_initial_schema_is_created(tmp_path: Path) -> None:
    database = tmp_path / "cko_canonical.db"
    migrations = Path(__file__).resolve().parents[1] / "src" / "cko" / "migrations"

    runner = MigrationRunner(database, migrations)
    applied = runner.apply_all()

    assert applied == [1]

    with sqlite3.connect(database) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

    assert "schema_version" in tables
    assert "documents" in tables
    assert "locations" in tables


def test_migrations_are_idempotent(tmp_path: Path) -> None:
    database = tmp_path / "cko_canonical.db"
    migrations = Path(__file__).resolve().parents[1] / "src" / "cko" / "migrations"

    runner = MigrationRunner(database, migrations)

    assert runner.apply_all() == [1]
    assert runner.apply_all() == []
