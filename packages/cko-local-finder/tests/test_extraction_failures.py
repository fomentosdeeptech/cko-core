import hashlib
import pytest
from cko_local_finder.application.extraction import extract_documents
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.domain.models import DiscoveredFile,DiscoveryReport,ExtractionPolicy
from cko_local_finder.infrastructure.extractors import ExtractorRegistry
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def test_character_limit_failure_is_recorded_without_partial_success(tmp_path):
    path=tmp_path/"a.txt"; path.write_text("abcd",encoding="utf-8"); d=hashlib.sha256(path.read_bytes()).hexdigest()
    source=DiscoveredFile(d,str(path),path.name,d,4,".txt",1,"text/plain")
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); persist_discovery_report(DiscoveryReport(str(tmp_path),(source,),(),0,(),1,0,0),repo)
    result=extract_documents((source,),ExtractorRegistry(policy=ExtractionPolicy(max_extracted_characters=3)),repo)
    assert result.success_count==0 and result.issues[0].code=="TEXT_TOO_LARGE" and result.issues[0].observed_size==4
    with repo.connection() as db: assert db.execute("SELECT count(*) FROM extractions").fetchone()[0]==0

def test_pipeline_does_not_swallow_repository_failure(tmp_path,monkeypatch):
    path=tmp_path/"a.txt"; path.write_text("ok",encoding="utf-8"); d=hashlib.sha256(path.read_bytes()).hexdigest(); source=DiscoveredFile(d,str(path),path.name,d,2,".txt",1,"text/plain")
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); persist_discovery_report(DiscoveryReport(str(tmp_path),(source,),(),0,(),1,0,0),repo)
    monkeypatch.setattr(repo,"save_extraction",lambda *args: (_ for _ in ()).throw(RuntimeError("controlled")))
    with pytest.raises(RuntimeError,match="controlled"): extract_documents((source,),ExtractorRegistry(),repo)
    with repo.connection() as db: assert db.execute("SELECT count(*) FROM extractions").fetchone()[0]==0
