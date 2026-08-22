# SPR-019 P-019-07R — Schema 3, Provenance and Reporting Validation Report

**Date:** 2026-08-21
**Result:** `IMPLEMENTED / VALIDATED / CONSOLIDATED`

## Reconciliation and schema 3

The original P-019-07 stopped before writing because schema 2 stored processing issues without root or document SHA-256. The reconciled human mandate authorized migration 3 and a maximum 32-path allowlist. Migration 3 adds nullable `document_sha256` with a foreign key to `documents.sha256`, nullable `root`, and indexes for document identity and `(root, relative_path)`. Migrations 1 and 2 and their checksums remain unchanged.

Historical rows are preserved with NULL identity/origin unless previously proven; no relative-path-only backfill is attempted. Reports place issues without a persisted document identity into a deterministic unresolved-historical section. New discovery issues persist the authorized root when known. New extraction issues persist the identified SHA-256 and resolve the root only through the matching document location.

## Provenance, reports, and Core mapping

Immutable internal models describe document origins, extraction, indexing, issues, duplicate evidence, provenance bundles, report metadata, three report families, and conceptual Core mappings. Provenance lookup supports SHA-256 and confined `(root, relative_path)`, preserves all ordered locations, and never uses an absolute path as identity.

Ingestion reports summarize locations, unique documents, extraction states, recoverable failures, indexed documents, and duplicate evidence. Failure reports separate resolved issues from unresolved historical rows. Duplicate reports exclude single-location documents. Reports serialize as sorted-key UTF-8 JSON with Unicode preserved and exactly one final newline; identical state, parameters, and explicit timestamp produce identical bytes.

Pure mapping functions cover the direct or derived correspondence to `core.documents` and `core.provenance` without importing, requiring, or writing to Core. SHA-256 is the mapped identity; origins remain `(root, relative_path)` pairs; extraction, derived content, issues, and duplicate evidence remain explicit.

## Validation

The 133-test baseline first passed as 131 passed and two preexisting Windows symlink skips. P-019-07R added 17 tests. The final 150-test suite completed with 148 passed and the same two skips. Migration clean install, 2→3 upgrade, checksum preservation, idempotency, rollback, future-version behavior, nullable columns, FK, indexes, issue identity, provenance, reports, deterministic serialization, and Core isolation passed.

```text
SQLITE_SCHEMA_VERSION_BEFORE: 2
SQLITE_SCHEMA_VERSION_AFTER: 3
PREEXISTING_TEST_COUNT: 133
P_019_07_TEST_COUNT: 17
TOTAL_LOCAL_FINDER_TEST_COUNT: 150
TEST_RESULT: PASS — 148 PASSED / 2 SKIPPED
AMBIGUOUS_BACKFILL_CREATED: NO
PROVENANCE_FALSE_ASSOCIATION_COUNT: 0
CORE_IMPORT_COUNT: 0
CORE_WRITE_COUNT: 0
```

Packaging, repeat builds, isolated installation, CKO and CKO-FCP coexistence, and simultaneous imports used external temporary directories. No new dependency, tracked database, user report output, wheel, sdist, environment, cache, build artifact, secret, Core modification, CLI, or P-019-08 implementation was introduced.

Initial and resumption Git state was `main` at `11b4844ae55b5dc58ce7031cc3f2d08055a81d9b`, equal to local and real remote `origin/main`, with empty staging, zero tracked differences, and zero files preserved from the blocked attempt. All 11 preexisting untracked artifacts were preserved. This report intentionally has no mandatory self-hash.

`P-019-07R IMPLEMENTED / VALIDATED / CONSOLIDATED — P-019-08 NOT AUTHORIZED`
