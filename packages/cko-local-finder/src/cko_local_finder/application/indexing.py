"""Application coordination for explicit indexing and rebuilds."""

from datetime import datetime, timezone
from cko_local_finder.application.ports import SearchIndexPort
from cko_local_finder.domain.models import IndexingSummary


def index_documents(digests: tuple[str, ...], index: SearchIndexPort, *, observed_at: str | None = None) -> IndexingSummary:
    timestamp = observed_at or datetime.now(timezone.utc).isoformat()
    index.apply_search_migrations()
    totals = [0] * 6
    schema = 2
    for digest in sorted(set(digests)):
        item = index.index_document(digest, timestamp)
        totals = [a + b for a, b in zip(totals, (item.documents_considered, item.documents_indexed,
                  item.documents_updated, item.documents_removed, item.documents_ignored, item.failures))]
        schema = item.schema_version
    return IndexingSummary(*totals, schema)


def rebuild_search_index(index: SearchIndexPort, *, observed_at: str | None = None) -> IndexingSummary:
    index.apply_search_migrations()
    return index.rebuild_index(observed_at or datetime.now(timezone.utc).isoformat())
