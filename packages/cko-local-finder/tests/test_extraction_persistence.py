import hashlib
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.domain.models import DiscoveredFile,DiscoveryReport,ExtractionResult
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def setup(tmp_path):
    path=tmp_path/"a.txt"; path.write_text("text",encoding="utf-8"); d=hashlib.sha256(path.read_bytes()).hexdigest()
    source=DiscoveredFile(d,str(path),path.name,d,4,".txt",1,"text/plain")
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); persist_discovery_report(DiscoveryReport(str(tmp_path),(source,),(),0,(),1,0,0),repo)
    return repo,source

def test_success_no_text_metadata_and_query(tmp_path):
    repo,source=setup(tmp_path)
    for status,text in (("SUCCESS","text"),("NO_TEXT","")):
        result=ExtractionResult(source.sha256,text,"test",status.lower(),(("z","2"),("a","1")),status)
        with repo.transaction(): repo.save_extraction(result,"t")
        stored=repo.get_extraction(source.sha256,"test",status.lower())
        assert stored.text==result.text and stored.status==result.status
        assert stored.metadata==tuple(sorted(result.metadata))
    with repo.connection() as db:
        assert db.execute("SELECT metadata_json FROM extractions ORDER BY id LIMIT 1").fetchone()[0]=='{"a":"1","z":"2"}'
        assert db.execute("SELECT count(*) FROM sqlite_master WHERE sql LIKE '%FTS%'").fetchone()[0]==0

def test_same_identity_updates_without_duplicate_and_versions_coexist(tmp_path):
    repo,source=setup(tmp_path)
    with repo.transaction(): repo.save_extraction(ExtractionResult(source.sha256,"one","x","1"),"t1")
    with repo.transaction(): repo.save_extraction(ExtractionResult(source.sha256,"two","x","1"),"t2")
    with repo.transaction(): repo.save_extraction(ExtractionResult(source.sha256,"three","x","2"),"t3")
    with repo.connection() as db: assert db.execute("SELECT count(*) FROM extractions").fetchone()[0]==2
    assert repo.get_extraction(source.sha256,"x","1").text=="two"

def test_extraction_transaction_rollback(tmp_path):
    repo,source=setup(tmp_path)
    try:
        with repo.transaction():
            repo.save_extraction(ExtractionResult(source.sha256,"x","x","1"),"t")
            raise RuntimeError("controlled")
    except RuntimeError: pass
    assert repo.get_extraction(source.sha256,"x","1") is None
