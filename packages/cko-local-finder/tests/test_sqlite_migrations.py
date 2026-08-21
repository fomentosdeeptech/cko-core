import sqlite3
import subprocess
import sys
import pytest
from cko_local_finder.infrastructure.migrations import MIGRATIONS, Migration, MigrationError, apply_migrations
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def test_schema_migration_and_idempotency(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite")
    assert repo.apply_migrations()==repo.apply_migrations()==1
    with repo.connection() as db:
        tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"schema_migrations","documents","document_locations","processing_issues","extractions"}<=tables
        assert db.execute("PRAGMA user_version").fetchone()[0]==1
        assert tuple(db.execute("SELECT version,name,checksum FROM schema_migrations").fetchone())==(1,MIGRATIONS[0].name,MIGRATIONS[0].checksum)
        indexes={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        assert {"idx_document_locations_document","idx_document_locations_relative_path","idx_processing_issues_stage_code"}<=indexes
        assert db.execute("PRAGMA foreign_keys").fetchone()[0]==1
        assert db.execute("SELECT count(*) FROM sqlite_master WHERE sql LIKE '%VIRTUAL TABLE%FTS%'").fetchone()[0]==0

def test_checksum_and_future_version_rejected(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_migrations()
    with repo.connection() as db:
        with pytest.raises(MigrationError,match="checksum"): apply_migrations(db,(Migration(1,"changed",("SELECT 1",)),))
        db.execute("PRAGMA user_version=99")
        with pytest.raises(MigrationError,match="newer"): apply_migrations(db,MIGRATIONS)

def test_invalid_migration_rolls_back(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_migrations()
    bad=Migration(2,"bad",("CREATE TABLE transient(value)","INVALID SQL"))
    with repo.connection() as db:
        with pytest.raises(sqlite3.Error): apply_migrations(db,MIGRATIONS+(bad,))
        assert db.execute("SELECT count(*) FROM sqlite_master WHERE name='transient'").fetchone()[0]==0
        assert db.execute("PRAGMA user_version").fetchone()[0]==1

def test_import_has_no_database_side_effect(tmp_path):
    subprocess.run([sys.executable,"-c","import cko_local_finder.infrastructure.sqlite"],cwd=tmp_path,check=True)
    assert not list(tmp_path.iterdir())
