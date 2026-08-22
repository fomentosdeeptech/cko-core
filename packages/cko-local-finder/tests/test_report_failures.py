import pytest
from cko_local_finder.application.reporting import build_ingestion_report
from cko_local_finder.infrastructure.reporting import report_json
from tests.test_provenance import seeded

def test_explicit_time_required(tmp_path):
    repo,_=seeded(tmp_path)
    with pytest.raises(ValueError): build_ingestion_report("/root","",repo)

def test_serialization_never_contains_sql_or_traceback(tmp_path):
    repo,_=seeded(tmp_path); payload=report_json(repo.failure_report(None,"fixed"))
    assert "Traceback" not in payload and "sqlite3" not in payload
