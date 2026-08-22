from tests.test_provenance import seeded

def test_duplicates_only_and_ordered(tmp_path):
    repo,d=seeded(tmp_path); report=repo.duplicate_report(None,"fixed")
    assert len(report.duplicates)==1 and report.duplicates[0].sha256==d
    assert [o.relative_path for o in report.duplicates[0].origins]==["a.txt","z.txt"]

def test_single_location_excluded(tmp_path):
    repo,_=seeded(tmp_path,False); assert repo.duplicate_report(None,"fixed").duplicates==()
