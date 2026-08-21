"""Application-level search validation."""

from cko_local_finder.application.ports import SearchIndexPort
from cko_local_finder.domain.models import SearchPage, SearchQuery
from cko_local_finder.infrastructure.search import MAX_QUERY_CHARACTERS, MAX_RESULT_LIMIT


def search_documents(query: SearchQuery, index: SearchIndexPort) -> SearchPage:
    if not query.text or len(query.text) > MAX_QUERY_CHARACTERS:
        raise ValueError("invalid query text")
    if not 1 <= query.limit <= MAX_RESULT_LIMIT or query.offset < 0:
        raise ValueError("invalid pagination")
    return index.search(query)
