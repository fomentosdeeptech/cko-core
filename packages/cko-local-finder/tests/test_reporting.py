from cko_local_finder.infrastructure.reporting import report_dict,report_json
from tests.test_provenance import seeded

def test_typed_dict_json_unicode_and_sorted_keys(tmp_path):
    repo,_=seeded(tmp_path); report=repo.ingestion_report("/root","2026-é")
    payload=report_json(report)
    assert report_dict(report)["metadata"]["observed_at"]=="2026-é"
    assert "é" in payload and "\\u00e9" not in payload and payload.endswith("\n") and not payload.endswith("\n\n")
    assert payload.index('"discovered_locations"')<payload.index('"unique_documents"')

def test_non_report_rejected():
    try: report_json({})
    except TypeError: pass
    else: raise AssertionError("untyped report accepted")
