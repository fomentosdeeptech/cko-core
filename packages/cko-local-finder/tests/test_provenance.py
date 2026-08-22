import hashlib
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.domain.models import DiscoveredFile,DiscoveryIssue,DiscoveryReport,ExtractionIssue,ExtractionResult
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def seeded(tmp_path,duplicate=True):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); repo.apply_provenance_migrations(); d=hashlib.sha256(b"doc").hexdigest()
    paths=("a.txt","z.txt") if duplicate else ("a.txt",)
    files=tuple(DiscoveredFile(d,str(tmp_path/p),p,d,3,".txt",1,"text/plain") for p in paths)
    persist_discovery_report(DiscoveryReport("/root",files,(),0,(),len(files),0,0),repo,observed_at="t")
    with repo.transaction(): repo.save_extraction(ExtractionResult(d,"body","test","1"),"t")
    repo.apply_search_migrations(); repo.index_document(d,"t")
    return repo,d

def test_by_sha_location_multiple_origins_extraction_index(tmp_path):
    repo,d=seeded(tmp_path); bundle=repo.provenance_by_sha256(d)
    assert [o.relative_path for o in bundle.document.origins]==["a.txt","z.txt"]
    assert bundle.document.extraction.status=="SUCCESS" and bundle.document.indexing.indexed
    assert bundle.document.duplicate.sha256==d
    assert repo.provenance_by_location("/root","a.txt")==bundle

def test_new_discovery_and_extraction_issue_identity(tmp_path):
    repo,d=seeded(tmp_path,False)
    with repo.transaction(): repo.record_issue(DiscoveryIssue("unknown.txt","discovery","denied","safe"),"t",root="/root")
    with repo.transaction(): repo.record_extraction_issue(ExtractionIssue(d,"a.txt","bad","safe"),"t")
    with repo.connection() as db:
        discovery=db.execute("SELECT document_sha256,root FROM processing_issues WHERE stage='discovery'").fetchone()
        extraction=db.execute("SELECT document_sha256,root FROM processing_issues WHERE stage='extraction'").fetchone()
    assert tuple(discovery)==(None,"/root") and tuple(extraction)==(d,"/root")

def test_invalid_location_is_rejected(tmp_path):
    repo,_=seeded(tmp_path,False)
    try: repo.provenance_by_location("/root","../escape")
    except ValueError: pass
    else: raise AssertionError("escape accepted")
