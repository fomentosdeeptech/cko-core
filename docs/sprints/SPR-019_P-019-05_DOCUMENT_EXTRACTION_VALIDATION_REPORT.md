# SPR-019 P-019-05 — Document Extraction Validation Report

**Date:** 2026-08-20
**Result:** `IMPLEMENTED / VALIDATED / CONSOLIDATED`

## Scope and dependencies

The closed allowlist contained exactly 22 paths: eight production and packaging paths, ten corpus/test paths, and four documentation paths. No Core source or root public API changed. Runtime dependencies are exactly `pypdf>=5,<7` and `python-docx>=1.1,<2`. Validation resolved pypdf 6.16.1 and python-docx 1.2.0; relevant transitives were lxml 6.1.2 and typing-extensions 4.16.0.

## Extraction policy and behavior

The immutable policy defaults to a 50 MiB source limit, 5,000,000 extracted characters, 10,000 DOCX ZIP entries, and 100 MiB uncompressed DOCX data. TXT and Markdown accept only UTF-8 or UTF-8-SIG. Normalization removes an initial BOM, converts CRLF/CR to LF, and applies Unicode NFC while preserving paragraphs, blank lines, accents, and internal spacing. Limit violations are explicit and never persist truncated success.

The PDF extractor uses pypdf page-by-page, preserves deterministic page separation, records page counts and pages without text, reports `NO_TEXT`, corrupt, and encrypted states explicitly, and performs no OCR, JavaScript, attachment, image, or external-reference processing. The DOCX extractor validates ZIP count, uncompressed size, paths, content types, and minimum document structure before python-docx parsing. It extracts paragraphs and table rows in document order and does not execute macros or embedded objects.

The registry selects by case-insensitive normalized extension without fallback. Batch orchestration is deterministic, never performs discovery or mutates sources, records isolated failures, continues the batch, and persists successes and issues transactionally.

## Persistence and schema decision

SQLite schema version remains 1. A migration v2 was not necessary: every adapter write uses an explicit `BEGIN IMMEDIATE`, serializing writers, then selects and updates the logical identity `(document_sha256, extractor, extractor_version)` in the same transaction. Tests prove same-version replacement without duplicate rows, coexistence of distinct extractor versions, deterministic metadata JSON, query-after-write, and rollback. Persistent FTS table count remains zero.

## Validation results

The 85-test baseline was preserved. P-019-05 added 25 collected tests. The final suite collected 110 tests and completed with 108 passed and two preexisting Windows symlink permission skips. Core public API gates remain unchanged because `src/cko` has zero differences.

```text
PREEXISTING_TEST_COUNT: 85
P_019_05_TEST_COUNT: 25
TOTAL_LOCAL_FINDER_TEST_COUNT: 110
TEST_RESULT: PASS — 108 PASSED / 2 SKIPPED
SQLITE_SCHEMA_VERSION: 1
PERSISTENT_FTS_TABLE_COUNT: 0
OCR_IMPLEMENTED: NO
RUNTIME_DEPENDENCY_COUNT: 2
PUBLIC_API_IMPACT: NONE
```

Packaging, repeat builds, isolated installation, coexistence with CKO and CKO-FCP, and simultaneous imports were exercised in external temporary directories. The global Python was unchanged. No tracked database, binary corpus fixture, wheel, sdist, virtual environment, cache, build artifact, secret, OCR, persistent FTS, search, ranking, CLI, or P-019-06 implementation was introduced.

Initial Git state was `main` at `15169e1f7417caf0178f7de8970993f0f50f97ac`, equal to local and real remote `origin/main`, with empty staging and zero tracked worktree differences. The 11 preexisting untracked artifacts, recovery state, historical baseline, databases, real documents, and Python global were preserved. This report intentionally has no mandatory self-hash.

`P-019-05 IMPLEMENTED / VALIDATED / CONSOLIDATED — P-019-06 NOT AUTHORIZED`
