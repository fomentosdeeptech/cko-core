from cko_local_finder.domain.models import DiscoveryIssue
from tests.test_provenance import seeded

def test_resolved_and_historical_failures_are_separate(tmp_path):
    repo,d=seeded(tmp_path,False)
    with repo.transaction(): repo.record_issue(DiscoveryIssue("old","legacy","old","safe"),"t")
    with repo.connection() as db: db.execute("INSERT INTO processing_issues(relative_path,stage,code,message,recoverable,observed_at,document_sha256,root) VALUES(?,?,?,?,?,?,?,?)",("a.txt","index","new","safe",1,"t",d,"/root"))
    report=repo.failure_report("/root","fixed")
    assert report.issues[0].document_sha256==d
    assert report.unresolved_historical_issues[0].document_sha256 is None
    assert "Traceback" not in report.issues[0].message and "SELECT" not in report.issues[0].message
