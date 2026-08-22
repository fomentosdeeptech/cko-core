from cko_local_finder.infrastructure.reporting import report_json
from tests.test_provenance import seeded

def test_same_state_parameters_and_time_are_byte_identical(tmp_path):
    repo,_=seeded(tmp_path)
    assert report_json(repo.ingestion_report("/root","fixed"))==report_json(repo.ingestion_report("/root","fixed"))

def test_no_absolute_source_path_disclosed(tmp_path):
    repo,_=seeded(tmp_path); payload=report_json(repo.duplicate_report(None,"fixed"))
    assert str(tmp_path) not in payload
