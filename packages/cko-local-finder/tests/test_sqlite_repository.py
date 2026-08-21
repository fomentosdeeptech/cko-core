import json
import sqlite3
import pytest
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.domain.models import DiscoveredFile,DiscoveryIssue,DiscoveryReport
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def f(d,p): return DiscoveredFile(d,"/r/"+p,p,d,4,".txt",1,"text/plain")
def report(files=(),issues=()): return DiscoveryReport("/r",tuple(files),(),0,tuple(issues),len(files),0,len(issues))

def test_repository_round_trip_duplicates_and_order(tmp_path):
    d="a"*64; repo=SQLiteDocumentRepository(tmp_path/"db.sqlite")
    summary=persist_discovery_report(report([f(d,"z.txt"),f(d,"A.txt")]),repo,observed_at="t1")
    assert (summary.documents_inserted,summary.locations_inserted)==(1,2)
    assert repo.get_document(d).physical_metadata==(("hidden","false"),)
    assert [x.relative_path for x in repo.list_locations(d)]==["A.txt","z.txt"]
    assert repo.find_duplicates()[0].relative_paths==("A.txt","z.txt")
    with repo.connection() as db:
        assert db.execute("SELECT physical_metadata_json FROM documents").fetchone()[0]==json.dumps({"hidden":False},sort_keys=True,separators=(",",":"))
        assert db.execute("SELECT count(*) FROM extractions").fetchone()[0]==0

def test_issue_parameterization_and_connection_lifecycle(tmp_path):
    d="b"*64; repo=SQLiteDocumentRepository(tmp_path/"db.sqlite")
    issue=DiscoveryIssue("x'); DROP TABLE documents;--","hash","denied","safe")
    persist_discovery_report(report([f(d,issue.path)],[issue]),repo)
    assert repo.get_document(d)
    with repo.connection() as db: db.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError): db.execute("SELECT 1")

@pytest.mark.parametrize("value",[None,"","   "])
def test_explicit_database_path(value):
    with pytest.raises(ValueError): SQLiteDocumentRepository(value)

def test_parent_and_foreign_key_guards(tmp_path):
    with pytest.raises(ValueError): SQLiteDocumentRepository(tmp_path/"missing"/"db.sqlite")
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_migrations()
    with repo.connection() as db,pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO document_locations(document_sha256,root,relative_path,observed_size_bytes,mtime_ns,first_seen,last_seen) VALUES(?,?,?,?,?,?,?)",("f"*64,"/","x",1,1,"t","t"))
