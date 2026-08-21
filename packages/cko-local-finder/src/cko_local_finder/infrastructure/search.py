"""Safe FTS5 query compilation and execution."""

from __future__ import annotations

import sqlite3

from cko_local_finder.domain.models import SearchPage, SearchQuery, SearchResult

MAX_QUERY_CHARACTERS = 1000
MAX_RESULT_LIMIT = 100
MAX_SNIPPET_TOKENS = 64


class SearchError(ValueError):
    pass


def compile_query(value: str) -> tuple[str, str]:
    normalized = " ".join(value.split())
    if not normalized or "\x00" in value:
        raise SearchError("query must contain safe text")
    if len(value) > MAX_QUERY_CHARACTERS:
        raise SearchError("query exceeds 1000 characters")
    terms = normalized.replace('"', " ").split()
    if not terms:
        raise SearchError("query must contain terms")
    return normalized, " AND ".join('"' + term.replace('"', '""') + '"' for term in terms)


def _filters(query: SearchQuery) -> tuple[str, list[object]]:
    clauses: list[str] = []
    values: list[object] = []
    filters = query.filters
    for column, value in (("media_type", filters.media_type), ("root", filters.root),
                          ("document_sha256", filters.sha256)):
        if value is not None:
            clauses.append(f"d.{column} = ?")
            values.append(value)
    if filters.extension is not None:
        clauses.append("lower(d.extension) = lower(?)")
        values.append(filters.extension if filters.extension.startswith(".") else "." + filters.extension)
    if filters.path_prefix is not None:
        escaped = filters.path_prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        clauses.append("d.relative_path LIKE ? ESCAPE '\\'")
        values.append(escaped + "%")
    return (" AND " + " AND ".join(clauses) if clauses else ""), values


def execute_search(connection: sqlite3.Connection, query: SearchQuery) -> SearchPage:
    normalized, match = compile_query(query.text)
    if not 1 <= query.limit <= MAX_RESULT_LIMIT or query.offset < 0:
        raise SearchError("invalid result pagination")
    if not 1 <= query.snippet_tokens <= MAX_SNIPPET_TOKENS:
        raise SearchError("invalid snippet size")
    where, values = _filters(query)
    total = connection.execute(
        "SELECT count(*) FROM search_fts JOIN search_index_documents d ON d.id=search_fts.rowid WHERE search_fts MATCH ?" + where,
        [match, *values],
    ).fetchone()[0]
    rows = connection.execute(
        "SELECT d.*,bm25(search_fts) rank,snippet(search_fts,1,'[[',']]','…',?) snippet "
        "FROM search_fts JOIN search_index_documents d ON d.id=search_fts.rowid "
        "WHERE search_fts MATCH ?" + where +
        " ORDER BY rank ASC,d.document_sha256 ASC,d.relative_path ASC LIMIT ? OFFSET ?",
        [query.snippet_tokens, match, *values, query.limit, query.offset],
    ).fetchall()
    results = tuple(SearchResult(row["document_sha256"], -float(row["rank"]), row["snippet"] or "",
                                 row["relative_path"], row["document_sha256"], row["title"],
                                 row["extension"], row["media_type"], row["root"]) for row in rows)
    return SearchPage(normalized, results, int(total), query.limit, query.offset)
