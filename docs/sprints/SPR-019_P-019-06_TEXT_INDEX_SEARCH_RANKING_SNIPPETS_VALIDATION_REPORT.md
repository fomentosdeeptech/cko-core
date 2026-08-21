# SPR-019 P-019-06 — Text Index, Search, Ranking and Snippets Validation Report

**Date:** 2026-08-20
**Result:** `IMPLEMENTED / VALIDATED / CONSOLIDATED`

## Scope and schema

The closed allowlist contained exactly 21 paths: seven production modules, ten tests, and four documentation paths. No dependency declaration, Core source, or root public API changed. Migration 1 remains byte-for-byte logically stable with checksum `f64f4e1049529cec2005fac4d346248f5f92199f39b1d2c815ab0a20b39f463b`. Migration 2 upgrades search-enabled databases to schema 2 and creates `search_index_documents`, one external-content `search_fts` virtual table, three strict synchronization triggers, and one conventional filter index. Upgrade, new database, checksum, rerun, rollback, and future-version behavior passed.

FTS5 uses `unicode61 remove_diacritics 2` and indexes only title and body. The title is the representative relative filename stem; content is the latest successful non-empty extraction. Extension, media type, root, representative relative path, and SHA-256 remain structured filter fields. No vector object exists.

## Indexing and rebuild

Indexing is explicit, transactional, idempotent by document SHA-256, updates reextracted content, and removes projections whose latest extraction is empty or not successful. Multiple source locations remain in the primary tables while a representative location is chosen by deterministic ordering. Rebuild clears only derived projection rows and reconstructs entirely from documents, locations, and extractions without discovery, extraction, or source-file reads. Rebuild equivalence and failure rollback passed.

## Safe search, ranking, snippets, and filters

User text is normalized, bounded to 1,000 characters, rejected when empty or containing NUL, tokenized into escaped literal terms, joined with AND, and passed to MATCH as a parameter. Raw FTS syntax is never accepted. All filters and pagination values are parameterized; wildcard characters in path prefixes are escaped and path traversal is rejected.

Ranking uses SQLite `bm25(search_fts)`, orders the lower raw BM25 value first, and exposes its negation so a larger displayed score is better. Exact ties use SHA-256 and relative path. Snippets use fixed `[[` and `]]` markers, Unicode ellipsis, 24 default tokens, and a 64-token maximum; tests confirm bounded Unicode output without HTML or ANSI injection.

## Validation

The 110-test baseline was preserved. P-019-06 added 23 collected tests. The final suite collected 133 tests and completed with 131 passed and two preexisting Windows symlink permission skips. FTS5, ranking, snippets, filters, and rebuild tests were not skipped.

```text
PREEXISTING_TEST_COUNT: 110
P_019_06_TEST_COUNT: 23
TOTAL_LOCAL_FINDER_TEST_COUNT: 133
TEST_RESULT: PASS — 131 PASSED / 2 SKIPPED
SQLITE_SCHEMA_VERSION: 2
PERSISTENT_FTS_TABLE_COUNT: 1
VECTOR_INDEX_COUNT: 0
RUNTIME_DEPENDENCY_COUNT: 2
PUBLIC_API_IMPACT: NONE
```

Repeat packaging builds, isolated installation, coexistence with CKO and CKO-FCP, and simultaneous imports used external temporary directories. No tracked database, wheel, sdist, environment, cache, build artifact, secret, CLI, OCR, embedding, vector search, RAG, network behavior, or P-019-07 implementation was introduced.

Initial Git state was `main` at `2be4020774f616ed8a5d037e9f7e969ac4e2ad21`, equal to local and real remote `origin/main`, with empty staging and zero tracked worktree differences. The 11 preexisting untracked artifacts, recovery state, baseline, databases, documents, and Python global were preserved. This report intentionally has no mandatory self-hash.

`P-019-06 IMPLEMENTED / VALIDATED / CONSOLIDATED — P-019-07 NOT AUTHORIZED`
