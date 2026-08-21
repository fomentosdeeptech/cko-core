import sqlite3
import pytest
from cko_local_finder.infrastructure.migrations import MIGRATIONS,Migration,apply_migrations
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def test_upgrade_v1_to_v2_and_rerun(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); assert repo.apply_migrations()==1
    assert MIGRATIONS[0].checksum=="f64f4e1049529cec2005fac4d346248f5f92199f39b1d2c815ab0a20b39f463b"
    assert repo.apply_search_migrations()==repo.apply_search_migrations()==2
    with repo.connection() as db:
        assert db.execute("PRAGMA user_version").fetchone()[0]==2
        assert db.execute("SELECT checksum FROM schema_migrations WHERE version=2").fetchone()[0]==MIGRATIONS[1].checksum

def test_new_search_database_objects_and_no_vector(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_search_migrations()
    with repo.connection() as db:
        objects={r[0] for r in db.execute("SELECT name FROM sqlite_master")}
        assert {"search_index_documents","search_fts","search_index_ai","search_index_ad","search_index_au"}<=objects
        assert not any("vector" in name.lower() for name in objects)

def test_migration_2_rolls_back(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_migrations()
    bad=Migration(2,"bad",("CREATE TABLE transient(x)","INVALID SQL"))
    with repo.connection() as db:
        with pytest.raises(sqlite3.Error): apply_migrations(db,(MIGRATIONS[0],bad))
        assert db.execute("PRAGMA user_version").fetchone()[0]==1
        assert not db.execute("SELECT 1 FROM sqlite_master WHERE name='transient'").fetchone()
