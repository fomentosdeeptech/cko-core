from tests.test_provenance import seeded

def test_ingestion_counts(tmp_path):
    repo,_=seeded(tmp_path); report=repo.ingestion_report("/root","fixed")
    assert report.discovered_locations==2 and report.unique_documents==1
    assert report.successful_extractions==1 and report.indexed_documents==1
    assert report.duplicate_groups==1 and report.duplicate_locations==2
