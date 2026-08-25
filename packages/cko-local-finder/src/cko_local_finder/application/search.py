"""Application-level search validation."""

from cko_local_finder.application.ports import SearchIndexPort
from cko_local_finder.domain.models import SearchPage, SearchQuery
MAX_QUERY_CHARACTERS = 1000
MAX_RESULT_LIMIT = 100


def search_documents(query: SearchQuery, index: SearchIndexPort) -> SearchPage:
    if not query.text or len(query.text) > MAX_QUERY_CHARACTERS:
        raise ValueError("invalid query text")
    if not 1 <= query.limit <= MAX_RESULT_LIMIT or query.offset < 0:
        raise ValueError("invalid pagination")
    return index.search(query)
