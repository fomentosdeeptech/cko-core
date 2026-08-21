from cko_local_finder.domain.models import SearchQuery
from tests.test_text_indexing import seeded_repo

def test_empty_and_equivalent_rebuild(tmp_path):
    repo,files=seeded_repo(tmp_path,(("a.txt","rebuild term","a"),("b.txt","term","b")))
    assert repo.rebuild_index("t").documents_indexed==2
    before=repo.search(SearchQuery("term"))
    with repo.connection() as db: db.execute("DELETE FROM search_index_documents WHERE document_sha256=?",(files[0].sha256,))
    assert repo.rebuild_index("t").documents_indexed==2
    assert repo.search(SearchQuery("term"))==before

def test_rebuild_needs_no_source_files(tmp_path):
    repo,files=seeded_repo(tmp_path); repo.rebuild_index("t")
    assert repo.search_index_status().indexed_count==1
