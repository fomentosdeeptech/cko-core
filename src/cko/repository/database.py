"""Inicialização segura do banco canônico."""

from __future__ import annotations

from pathlib import Path

from cko.migrations import MigrationRunner


def canonical_database_path(core_root: Path) -> Path:
    return core_root / "runtime" / "database" / "cko_canonical.db"


def initialize_canonical_database(core_root: Path) -> list[int]:
    database_path = canonical_database_path(core_root)
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    runner = MigrationRunner(database_path, migrations_dir)
    return runner.apply_all()
