from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.domain.models import DiscoveredFile,DiscoveryReport
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def report(d="a"*64,paths=("a.txt",)):
    fs=tuple(DiscoveredFile(d,"/r/"+p,p,d,1,".txt",1,"text/plain") for p in paths)
    return DiscoveryReport("/r",fs,(),0,(),len(fs),0,0)

def test_report_idempotency_and_last_seen(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite")
    first=persist_discovery_report(report(),repo,observed_at="t1"); second=persist_discovery_report(report(),repo,observed_at="t2")
    assert (first.documents_inserted,second.documents_updated)==(1,1)
    assert repo.get_document("a"*64).last_seen=="t2"
    with repo.connection() as db: assert (db.execute("SELECT count(*) FROM documents").fetchone()[0],db.execute("SELECT count(*) FROM document_locations").fetchone()[0])==(1,1)

def test_multiple_paths_and_path_reassignment(tmp_path):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite")
    persist_discovery_report(report(paths=("a.txt","b.txt")),repo)
    assert len(repo.list_locations("a"*64))==2
    persist_discovery_report(report("b"*64),repo)
    assert repo.get_document("a"*64) and repo.list_locations("b"*64)[0].relative_path=="a.txt"

def test_two_rebuilds_are_logically_equivalent(tmp_path):
    repos=[SQLiteDocumentRepository(tmp_path/f"{n}.sqlite") for n in (1,2)]
    for repo in repos: persist_discovery_report(report(paths=("b.txt","a.txt")),repo,observed_at="fixed")
    states=[]
    for repo in repos:
        with repo.connection() as db: states.append([tuple(r) for r in db.execute("SELECT sha256,size_bytes,extension,media_type,physical_metadata_json,first_seen,last_seen FROM documents")]+[tuple(r) for r in db.execute("SELECT document_sha256,root,relative_path,observed_size_bytes,mtime_ns,first_seen,last_seen FROM document_locations ORDER BY relative_path")])
    assert states[0]==states[1]
