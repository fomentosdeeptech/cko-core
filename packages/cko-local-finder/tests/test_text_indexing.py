import hashlib
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.domain.models import DiscoveredFile,DiscoveryReport,ExtractionResult
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def seeded_repo(tmp_path,items=(("a.txt","alpha common", "a"),)):
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); files=[]
    for name,text,marker in items:
        digest=hashlib.sha256((name+marker).encode()).hexdigest()
        files.append(DiscoveredFile(digest,str(tmp_path/name),name,digest,len(text),"."+name.rsplit(".",1)[-1],1,"text/plain"))
    persist_discovery_report(DiscoveryReport("/root",tuple(files),(),0,(),len(files),0,0),repo,observed_at="t")
    for source,(_,text,_) in zip(files,items):
        with repo.transaction(): repo.save_extraction(ExtractionResult(source.sha256,text,"test","1"),"t")
    repo.apply_search_migrations()
    return repo,files

def test_valid_index_idempotency_title_and_reextraction(tmp_path):
    repo,files=seeded_repo(tmp_path); first=repo.index_document(files[0].sha256,"t1"); second=repo.index_document(files[0].sha256,"t2")
    assert first.documents_indexed==1 and second.documents_updated==1
    with repo.connection() as db:
        assert tuple(db.execute("SELECT count(*),title FROM search_index_documents").fetchone())==(1,"a")
    with repo.transaction(): repo.save_extraction(ExtractionResult(files[0].sha256,"updated term","test","1"),"t3")
    repo.index_document(files[0].sha256,"t3")
    with repo.connection() as db: assert db.execute("SELECT body FROM search_index_documents").fetchone()[0]=="updated term"

def test_invalid_or_empty_extraction_removes_projection(tmp_path):
    repo,files=seeded_repo(tmp_path); digest=files[0].sha256; repo.index_document(digest,"t")
    with repo.transaction(): repo.save_extraction(ExtractionResult(digest,"","test","2",(),"NO_TEXT"),"t2")
    assert repo.index_document(digest,"t2").documents_removed==1

def test_multiple_locations_choose_deterministic_representative(tmp_path):
    repo,files=seeded_repo(tmp_path); source=files[0]
    second=DiscoveredFile(source.sha256,str(tmp_path/"Z.txt"),"Z.txt",source.sha256,source.size_bytes,".txt",1,"text/plain")
    persist_discovery_report(DiscoveryReport("/root",(second,),(),0,(),1,0,0),repo)
    repo.index_document(source.sha256,"t")
    with repo.connection() as db: assert db.execute("SELECT relative_path FROM search_index_documents").fetchone()[0]=="a.txt"
