from cko_local_finder.domain.models import DatabaseCapability
from cko_local_finder.infrastructure import sqlite
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def test_real_fts5_capability_is_temporary(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_migrations(); result=repo.capabilities()
    assert isinstance(result,DatabaseCapability) and result.fts5_available and result.sqlite_version
    assert result.foreign_keys_enabled and result.schema_version==1
    with repo.connection() as db: assert db.execute("SELECT count(*) FROM sqlite_master WHERE name LIKE '%fts%'").fetchone()[0]==0

def test_simulated_unavailable_fts5(tmp_path,monkeypatch):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_migrations()
    monkeypatch.setattr(sqlite,"_probe_fts5",lambda connection:False)
    assert not repo.capabilities().fts5_available
