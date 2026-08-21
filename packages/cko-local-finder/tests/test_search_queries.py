import pytest
from cko_local_finder.domain.models import SearchQuery
from cko_local_finder.infrastructure.search import SearchError,compile_query
from tests.test_text_indexing import seeded_repo

def test_terms_case_diacritics_and_parameterization(tmp_path):
    repo,files=seeded_repo(tmp_path,(("a.txt","ação Alpha beta", "a"),)); repo.index_document(files[0].sha256,"t")
    for text in ("acao","ALPHA","alpha beta"):
        assert repo.search(SearchQuery(text)).total_matches==1
    assert repo.search(SearchQuery("alpha' OR 1=1 --")).total_matches==0

@pytest.mark.parametrize("text",["","   ","\x00", "x"*1001])
def test_invalid_queries(text):
    with pytest.raises(SearchError): compile_query(text)

def test_fts_operators_and_quotes_are_literal():
    normalized,compiled=compile_query('alpha OR "beta"')
    assert normalized and compiled=='"alpha" AND "OR" AND "beta"'
