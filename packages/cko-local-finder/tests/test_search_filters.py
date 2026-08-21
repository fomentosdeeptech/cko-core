import pytest
from cko_local_finder.domain.models import SearchFilter,SearchQuery
from tests.test_text_indexing import seeded_repo

def test_all_filters_and_combination(tmp_path):
    repo,files=seeded_repo(tmp_path,(("folder/a.txt","filter term","a"),)); repo.index_document(files[0].sha256,"t")
    digest=files[0].sha256
    filters=(SearchFilter(extension="TXT"),SearchFilter(media_type="text/plain"),SearchFilter(root="/root"),SearchFilter(path_prefix="folder/"),SearchFilter(sha256=digest),SearchFilter(extension=".txt",root="/root",sha256=digest))
    assert all(repo.search(SearchQuery("term",f)).total_matches==1 for f in filters)
    assert repo.search(SearchQuery("term",SearchFilter(extension="pdf"))).total_matches==0

def test_wildcard_literal_and_path_escape(tmp_path):
    repo,files=seeded_repo(tmp_path,(("100%/a.txt","term","a"),)); repo.index_document(files[0].sha256,"t")
    assert repo.search(SearchQuery("term",SearchFilter(path_prefix="100%"))).total_matches==1
    with pytest.raises(ValueError): SearchFilter(path_prefix="../escape")
