import hashlib
from cko_local_finder.application.extraction import extract_documents
from cko_local_finder.application.persistence import persist_discovery_report
from cko_local_finder.domain.models import DiscoveredFile,DiscoveryReport
from cko_local_finder.infrastructure.extractors import ExtractorRegistry
from cko_local_finder.infrastructure.sqlite import SQLiteDocumentRepository

def source(path,extension=None):
    b=path.read_bytes(); d=hashlib.sha256(b).hexdigest(); return DiscoveredFile(d,str(path),path.name,d,len(b),extension or path.suffix,1,"text/plain")

def test_registry_selection_and_unsupported(tmp_path):
    registry=ExtractorRegistry()
    for name,expected in (("a.TXT","plain-text"),("a.PDF","pypdf"),("a.DOCX","python-docx")):
        path=tmp_path/name; path.write_bytes(b""); assert registry.select(source(path)).name==expected
    path=tmp_path/"a.bin"; path.write_bytes(b"")
    try: registry.select(source(path))
    except Exception as error: assert error.code=="UNSUPPORTED_FORMAT"

def test_batch_continues_orders_and_preserves_sources(tmp_path):
    good=tmp_path/"b.txt"; good.write_text("ok",encoding="utf-8"); bad=tmp_path/"a.txt"; bad.write_bytes(b"\xff")
    files=(source(good),source(bad)); before={p:p.read_bytes() for p in (good,bad)}
    repo=SQLiteDocumentRepository(tmp_path/"db.sqlite"); persist_discovery_report(DiscoveryReport(str(tmp_path),files,(),0,(),2,0,0),repo)
    result=extract_documents(files,ExtractorRegistry(),repo,observed_at="t")
    assert result.processed_count==2 and result.success_count==1 and result.issue_count==1
    assert result.issues[0].path=="a.txt" and result.results[0].text=="ok"
    assert before=={p:p.read_bytes() for p in (good,bad)}
    with repo.connection() as db:
        assert db.execute("SELECT count(*) FROM processing_issues WHERE stage='extraction'").fetchone()[0]==1
        assert db.execute("SELECT count(*) FROM sqlite_master WHERE sql LIKE '%FTS%'").fetchone()[0]==0
