import sqlite3
import pytest
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.domain.models import DiscoveredFile,DiscoveryReport
from cko_local_finder.infrastructure.sqlite import RepositoryError,SQLiteDocumentRepository

def report():
    d="a"*64; f=DiscoveredFile(d,"/r/a","a",d,1,".txt",1,"text/plain")
    return DiscoveryReport("/r",(f,),(),0,(),1,0,0)

def test_integral_rollback(tmp_path,monkeypatch):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); original=repo.persist_report
    def fail(*args): original(*args); raise RuntimeError("controlled")
    monkeypatch.setattr(repo,"persist_report",fail)
    with pytest.raises(RuntimeError): persist_discovery_report(report(),repo)
    with repo.connection() as db: assert db.execute("SELECT count(*) FROM documents").fetchone()[0]==0

def test_invalid_database_error_is_sanitized(tmp_path):
    path=tmp_path/"bad.sqlite"; path.write_bytes(b"invalid")
    with pytest.raises(RepositoryError,match="database operation failed") as error: SQLiteDocumentRepository(path).apply_migrations()
    assert str(path) not in str(error.value)

def test_interrupted_connection_and_no_residue(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_migrations()
    with pytest.raises(sqlite3.ProgrammingError):
        with repo.transaction(): repo._active.close(); repo.persist_report(report(),"t")
    assert set(tmp_path.iterdir())=={tmp_path/"db.sqlite"}
