# SPR-019 P-019-04 — Versioned SQLite Persistence Validation Report

**Date:** 2026-08-20
**Increment:** P-019-04 — Versioned SQLite Persistence
**Result:** `IMPLEMENTED / VALIDATED / CONSOLIDATED`

## Scope and implementation

The closed allowlist contained exactly 16 paths: five production modules, seven tests, the package README, this report, the SPR-019 plan, and the Sprint index. No Core source, dependency declaration, root public API, or seventeenth path changed. P-019-05 remains planned and not authorized.

Schema version 1 is embedded in `migrations.py` and creates five application tables: `schema_migrations`, `documents`, `document_locations`, `processing_issues`, and the future-only `extractions` placeholder. Three explicit conventional indexes cover document-location lookup, relative paths, and issue stage/code. The migration history stores a SHA-256 checksum, agrees with `PRAGMA user_version`, reruns idempotently, rejects altered checksums and unknown future versions, and rolls back failed migrations.

The standard-library `sqlite3` adapter requires an explicit database path, refuses to create parent directories, enables foreign keys, sets a finite busy timeout, uses parameterized queries and explicit transactions, and closes every connection deterministically. It does not enable WAL. Discovery report persistence is idempotent by SHA-256 and by `(root, relative_path)`, preserves multiple legitimate locations, updates `last_seen`, transactionally reassigns a changed path without deleting the old document, records sanitized issues, and reconstructs equivalent logical state in a new database.

## FTS5 and scope gates

The canonical SQLite runtime reports FTS5 available. The capability check creates, exercises, and removes an FTS5 table exclusively in the temporary schema. The persistent schema contains zero FTS tables. There is no extraction implementation, search, ranking, CLI, OCR, network access, ORM, or remote database behavior.

## Validation

The Local Finder suite collected 85 tests: the 67-test baseline plus 18 P-019-04 tests. It finished with 83 passed and two preexisting Windows symlink skips. Migration, rollback, path reassignment, reconstruction, real FTS5, architecture, and scope gates passed. Packaging, reproducibility, isolated and joint installation, simultaneous imports, and permanent Core gates were validated in temporary external directories.

```text
PREEXISTING_TEST_COUNT: 67
P_019_04_TEST_COUNT: 18
TOTAL_LOCAL_FINDER_TEST_COUNT: 85
TEST_RESULT: PASS — 83 PASSED / 2 SKIPPED
SQLITE_SCHEMA_VERSION: 1
DATABASE_TABLE_COUNT: 5
EXPLICIT_DATABASE_INDEX_COUNT: 3
SQLITE_FTS5_AVAILABLE: YES
PERSISTENT_FTS_TABLE_COUNT: 0
RUNTIME_DEPENDENCY_COUNT: 0
PUBLIC_API_IMPACT: NONE
```

The global Python remained unchanged and without pytest. Test and build tooling lived outside the repository. No database, journal, WAL, SHM, wheel, sdist, virtual environment, cache, secret, or local absolute path was added to the authorized diff. The 11 preexisting untracked artifacts, recovery state, baseline, preexisting databases, and real user documents were preserved.

Initial Git state was `main` at `3e810e639b268b109ac1cb6fe02ca6897beb98ee`, equal to local and real remote `origin/main`, with empty staging and zero tracked worktree differences. This report intentionally has no mandatory self-hash.

`P-019-04 IMPLEMENTED / VALIDATED / CONSOLIDATED — P-019-05 NOT AUTHORIZED`
