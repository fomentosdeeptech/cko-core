from cko_local_finder.domain.models import SearchQuery
from tests.test_text_indexing import seeded_repo

def test_snippet_markers_unicode_and_no_html_ansi(tmp_path):
    repo,files=seeded_repo(tmp_path,(("a.txt","prefix ação suffix "*20,"a"),)); repo.index_document(files[0].sha256,"t")
    snippet=repo.search(SearchQuery("ação",snippet_tokens=8)).results[0].snippet
    assert "[[ação]]" in snippet and "…" in snippet and "<" not in snippet and "\x1b" not in snippet

def test_short_content_and_term_edges(tmp_path):
    repo,files=seeded_repo(tmp_path,(("a.txt","start middle end","a"),)); repo.index_document(files[0].sha256,"t")
    assert "[[start]]" in repo.search(SearchQuery("start")).results[0].snippet
    assert "[[end]]" in repo.search(SearchQuery("end")).results[0].snippet
