# SPR-019 P-019-02 — Synthetic Corpus and Test Harness Validation Report

**Date:** 2026-08-17
**Increment:** P-019-02R — Synthetic Corpus and Test Harness
**Result:** `IMPLEMENTED / VALIDATED / CONSOLIDATED`

## 1. Reconciled authority and scope

The P-019-02R mandate superseded the earlier blocked P-019-02 attempt, which made no writes, commit, or push. It expressly authorized implementation, validation, consolidation, and publication within exactly 13 paths: `packages/cko-local-finder/pyproject.toml`; nine test-infrastructure paths below `packages/cko-local-finder/tests/`; this report; the SPR-019 plan; and the Sprint index. No path outside that closed list was changed.

P-019-03 and P-018-02 remain not authorized. No discovery, production hashing, extraction, persistence, SQLite, FTS, or functional CLI behavior was implemented.

## 2. Temporary test environment

The global Python 3.13.15 installation had no pytest before validation and remained unmodified. A virtual environment under the operating-system temporary area outside the repository received the local `cko-local-finder[test]` package and pytest 8.4.2. The declared `setuptools>=68` build backend was materialized only in that temporary environment for the mandatory sdist gate. Builds, installations, caches, wheels, sdists, and generated binary documents remained outside the repository.

```text
GLOBAL_PYTEST_STATUS: ABSENT / UNCHANGED
TEMP_TEST_ENV_STATUS: OPERATIONAL
TEMP_TEST_ENV_LOCATION_CLASS: OPERATING-SYSTEM TEMPORARY DIRECTORY OUTSIDE REPOSITORY
GLOBAL_PYTHON_CHANGED: NO
```

## 3. Synthetic corpus

The standard-library-only factory materializes 12 deterministic cases below an explicitly supplied `tmp_path`: UTF-8 TXT, UTF-8-SIG TXT, Markdown, textual PDF, DOCX, empty TXT, configurable oversized TXT, corrupt PDF, corrupt DOCX, unsupported binary, and one byte-identical TXT duplicate pair. PDF bytes are generated directly; DOCX uses ordered ZIP entries with fixed `1980-01-01 00:00:00` timestamps. The oversized fixture is only one byte above a reduced test limit.

The returned runtime manifest records relative path, case type, size, and SHA-256. Two independent materializations produced identical bytes, manifests, and hashes. The tracked JSON contract contains no absolute paths or transient hashes. All content is synthetic and contains no names, email addresses, identifiers, or real user documents. No PDF, DOCX, database, or other generated binary fixture is tracked.

```text
CORPUS_CASE_COUNT: 12
CORPUS_FORMATS: PDF / DOCX / TXT / MARKDOWN / UNSUPPORTED BINARY
VALID_CASE_COUNT: 5
CORRUPT_CASE_COUNT: 2
EMPTY_CASE_COUNT: 1
UNSUPPORTED_CASE_COUNT: 1
DUPLICATE_PAIR_COUNT: 1
OVERSIZED_CASE_COUNT: 1
UTF8_BOM_CASE_COUNT: 1
CORPUS_DETERMINISM_STATUS: PASS
PERSONAL_DATA_STATUS: ABSENT
TRACKED_BINARY_FIXTURE_COUNT: 0
```

The symlink fixture attempted safe creation inside `tmp_path`. Windows denied symlink creation under the executing permissions, so exactly one test was skipped with the operating-system error recorded by pytest; all other tests passed.

## 4. Tests and regression

```text
P_019_01_REGRESSION: PASS — 11 PASSED
P_019_02_DEDICATED_TESTS: PASS — 21 PASSED / 1 SKIPPED
TOTAL_LOCAL_FINDER_TEST_COUNT: 33 COLLECTED / 32 PASSED / 1 SKIPPED
SYMLINK_TEST_STATUS: SKIPPED — OPERATING-SYSTEM PERMISSION DID NOT ALLOW CREATION
```

The dedicated suite validates all corpus cases, byte and hash determinism, duplicate identity, unique nonduplicate payloads, PDF structure, DOCX ZIP structure and fixed timestamps, corrupt-container distinction, size limit, encodings, confinement, manifest contract, privacy patterns, final newlines, production scope boundaries, zero runtime dependencies, and import without filesystem writes.

## 5. Packaging and installation

Two builds from independent temporary copies used a fixed `SOURCE_DATE_EPOCH`. The wheels were byte-identical with SHA-256 `2c3d91f1a7ace163f83d703eefebc5a547f30aabe0d76363bf0b8dbd6065cbf2`. The gzip metadata of the two sdists differed, while all 23 archive files had identical names and per-file SHA-256 values.

Fresh temporary environments validated the local-finder wheel alone, jointly with `cko 1.0.0`, jointly with `cko-fcp 0.1.0`, and with all three namespaces imported simultaneously. Each applicable environment passed `pip check`.

```text
PACKAGING_TESTS: PASS
WHEEL_REPRODUCIBILITY: PASS — IDENTICAL ARTIFACT SHA-256
SDIST_REPRODUCIBILITY: PASS — 23/23 FILE CONTENT HASHES IDENTICAL
ISOLATED_INSTALL_STATUS: PASS
CKO_DUAL_INSTALL_STATUS: PASS
CKO_FCP_DUAL_INSTALL_STATUS: PASS
IMPORT_COEXISTENCE_STATUS: PASS
BUILD_ARTIFACTS_IN_REPOSITORY: 0
```

## 6. Permanent gates

The canonical ordered-export algorithm was executed against both source and a freshly installed `cko` wheel. Both matched exactly.

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
RUNTIME_DEPENDENCY_COUNT: 0
TEST_EXTRA_DEPENDENCY_COUNT: 1
```

## 7. Git, content, and security gates

Preflight was on `main` at `1c743badfe57cfdffbf9b879b2171653f127f456`; `main`, local `origin/main`, and the real remote branch matched. Staging and tracked worktree diff were empty. Baseline `faa51ac6568dc2aa0e11d2333671b1098a1a89fa` resolved unchanged. All 11 preexisting untracked files, recovery snapshots, baselines, external artifacts, and real user documents were preserved.

All authorized text files were validated as UTF-8 with one final newline and no unauthorized trailing whitespace. TOML and JSON parsing, relative links, scope, generated-artifact absence, and strong-secret patterns were checked before atomic staging. This report intentionally has no mandatory self-hash.

## 8. Conclusion

P-019-02 establishes only a deterministic synthetic corpus and test harness. P-019-03 remains planned and not authorized.

`P-019-02 IMPLEMENTED / VALIDATED / CONSOLIDATED — P-019-03 NOT AUTHORIZED`
