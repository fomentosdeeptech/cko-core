from cko_local_finder.domain.models import SearchQuery
from tests.test_text_indexing import seeded_repo

def test_bm25_relevance_ties_and_stability(tmp_path):
    items=(("b.txt","term term term", "b"),("a.txt","term", "a"))
    repo,files=seeded_repo(tmp_path,items)
    for source in reversed(files): repo.index_document(source.sha256,"t")
    first=repo.search(SearchQuery("term")); second=repo.search(SearchQuery("term"))
    assert first==second and first.results[0].score>=first.results[1].score
    repo.rebuild_index("r"); assert [r.sha256 for r in repo.search(SearchQuery("term")).results]==[r.sha256 for r in first.results]

def test_exact_ties_use_sha256_then_path(tmp_path):
    repo,files=seeded_repo(tmp_path,(("b.txt","same", "b"),("a.txt","same", "a")))
    for source in files: repo.index_document(source.sha256,"t")
    results=repo.search(SearchQuery("same")).results
    assert [r.sha256 for r in results]==sorted(r.sha256 for r in results)
