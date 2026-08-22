import sqlite3
import pytest
from cko_local_finder.infrastructure.migrations import MIGRATIONS,Migration,apply_migrations
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def test_clean_and_upgrade_schema_3_preserve_checksums(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); assert repo.apply_search_migrations()==2
    before=[m.checksum for m in MIGRATIONS[:2]]
    assert repo.apply_provenance_migrations()==repo.apply_provenance_migrations()==3
    assert before==["f64f4e1049529cec2005fac4d346248f5f92199f39b1d2c815ab0a20b39f463b","ca2a9b3d60b351c0c723353548fbaa27e25a4f770b06523977edaec500f86fef"]
    with repo.connection() as db:
        columns={r[1]:r for r in db.execute("PRAGMA table_info(processing_issues)")}
        assert columns["document_sha256"][3]==0 and columns["root"][3]==0
        assert {r[3] for r in db.execute("PRAGMA foreign_key_list(processing_issues)")}=={"document_sha256"}
        indexes={r[1] for r in db.execute("PRAGMA index_list(processing_issues)")}
        assert {"idx_processing_issues_document","idx_processing_issues_location"}<=indexes

def test_historical_nulls_fk_and_rollback(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_search_migrations()
    with repo.connection() as db: db.execute("INSERT INTO processing_issues(relative_path,stage,code,message,recoverable,observed_at) VALUES('x','old','c','safe',1,'t')")
    repo.apply_provenance_migrations()
    with repo.connection() as db:
        assert tuple(db.execute("SELECT document_sha256,root FROM processing_issues").fetchone())==(None,None)
        with pytest.raises(sqlite3.IntegrityError): db.execute("UPDATE processing_issues SET document_sha256=?",("f"*64,))

def test_migration_3_transactional_failure(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_search_migrations()
    bad=Migration(3,"bad",("ALTER TABLE processing_issues ADD COLUMN transient TEXT","INVALID SQL"))
    with repo.connection() as db:
        with pytest.raises(sqlite3.Error): apply_migrations(db,MIGRATIONS[:2]+(bad,))
        assert db.execute("PRAGMA user_version").fetchone()[0]==2
