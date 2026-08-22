# SPR-019 — P-019-09R-LOCAL End-to-End MVP Readiness Validation Report

Date: 2026-08-22
Scope: local clone only
Decision: `READY_FOR_CONTROLLED_LOCAL_PILOT`

## Authority and isolation

The reconciled P-019-09R-LOCAL command authorized end-to-end validation, four test modules, five documentation paths, and conditional commit/push. Preflight resolved the workspace and Git root to `C:\Users\ANDRÉ\Documents\Codex\CKO-CORE-LOCAL`; branch `main`, HEAD, local main, local origin/main, and the real remote main were `bac1ec9a890ce0abcb6ee8b92768842581ed8ea4`. The peeled baseline was `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`. Staging, tracked diff, and untracked counts were zero; no Git operation was active. The original `G:` repository was neither read nor changed.

All corpus files, SQLite databases, environments, build outputs, and operational reports were placed under the system temporary directory. The corpus was synthetic. Source SHA-256 values before and after the pipeline were identical.

## End-to-end evidence

The installed `cko-local-finder` entry point ingested a 14-location corpus containing UTF-8 TXT, Markdown, textual PDF, DOCX paragraphs/table, duplicates, empty content, invalid encoding, corrupt PDF/DOCX, an unsupported format, an oversized test case, Unicode/diacritics, hidden behavior, repeated relative paths across roots, and search/filter targets. It produced 13 unique documents, 14 locations, three recoverable processing issues, one duplicate group, and zero source mutations.

Ingestion, extraction, persistence, FTS5 indexing, deterministic ranking/snippets, Unicode search, every filter, combined filters, path-escape rejection, SHA-256 provenance, location provenance, duplicate preservation, reports, idempotent reingestion, and a clean-database reconstruction passed. JSON was UTF-8, deterministically keyed, ended with exactly one newline, and exposed no traceback, SQL, ANSI control, personal data, or unrequested absolute source path.

## Tests and packaging

The preexisting suite collected 166 tests and passed as 164 passed / 2 skipped. P-019-09 added 15 tests: 14 passed and one Windows symlink-permission skip. The final complete suite passed as 178 passed / 3 skipped in 12.62 seconds. P-019-01 through P-019-08 regressions passed within the complete suite.

Two external builds with fixed `SOURCE_DATE_EPOCH` produced byte-identical wheels. The sdists contained the same 82 file members with identical per-member SHA-256 values; only the gzip envelope differed. An isolated wheel installation passed `pip check`, version/help, and the installed CLI workflow. Joint installation and simultaneous import of `cko`, `cko_fcp`, and `cko_local_finder` passed.

## Permanent gates

```text
SDK_VERSION: 1.0.0
PUBLIC_API_COUNTS: 646 / 646 / 646
PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232
PUBLIC_API_IMPACT: NONE
BREAKING_CHANGE: NO
SRC_CKO_CHANGES: 0
LOCAL_FINDER_VERSION: 0.1.0
LOCAL_FINDER_PUBLIC_API_COUNT: 1
LOCAL_FINDER_PUBLIC_API_SYMBOLS: __version__
RUNTIME_DEPENDENCY_COUNT: 2
SQLITE_SCHEMA_VERSION: 3
```

## Diagnostic measurements

These values are diagnostic observations, not an SLA: Python 3.13.15; SQLite 3.50.4; FTS5 available; first ingest 1174.027 ms; reingest 1253.221 ms; clean rebuild 986.436 ms; representative installed-CLI query 674.254 ms; temporary database 94,208 bytes.

## Readiness matrix

| Area | Result | Evidence or limitation |
|---|---|---|
| Installation | PASS | Isolated wheel and `pip check` passed. |
| CLI | PASS | Installed entry point, help/version, and all commands passed. |
| Ingestion | PASS | Complete synthetic corpus continued after isolated failures. |
| Search | PASS | Text, diacritics, ranking, snippets, limits, and filters passed. |
| Provenance | PASS | Document, locations, extraction, indexing, and issues passed. |
| Reporting | PASS | Ingestion, failure, and duplicate JSON passed. |
| Duplicates | PASS | One physical identity preserved multiple locations. |
| Failure isolation | PASS | Three recoverable issues; valid documents remained searchable. |
| Idempotency | PASS | Reingestion preserved document/location cardinality. |
| Privacy | PASS | Synthetic-only run, local processing, zero source mutations. |
| Local safety | PASS_WITH_LIMITATION | Windows denied real symlink creation; default non-follow and fail-closed request policy passed. |
| Core isolation | PASS | Zero `src/cko` changes and no Local Finder Core dependency. |
| Packaging | PASS | Reproducible wheel/sdist content and coexistence passed. |
| Documentation | PASS | Pilot procedure and known limitations recorded. |
| Controlled pilot fitness | PASS | Restricted 20–50 non-confidential document pilot recommended. |

## Decision

No material defect remains. The Windows symlink limitation is platform permission only and does not weaken the implemented default non-follow policy. P-018-02 remains unauthorized.

`MVP_READINESS_DECISION: READY_FOR_CONTROLLED_LOCAL_PILOT`
