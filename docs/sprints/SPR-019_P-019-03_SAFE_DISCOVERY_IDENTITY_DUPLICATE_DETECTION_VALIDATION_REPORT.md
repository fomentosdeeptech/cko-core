# SPR-019 P-019-03 — Safe Discovery, Identity and Duplicate Detection Validation Report

**Date:** 2026-08-20
**Increment:** P-019-03R — Safe Discovery, Identity and Duplicate Detection
**Result:** `IMPLEMENTED / VALIDATED / CONSOLIDATED`

## 1. Authority and reconciled scope

The original P-019-03 attempt correctly stopped when the P-019-01 architecture test prohibited the two infrastructure modules required by P-019-03. Five authorized production changes were preserved without staging, commit, or push. P-019-03R then expanded the closed list from 14 to exactly 15 paths by authorizing only `packages/cko-local-finder/tests/test_architecture_boundaries.py` as the additional path. The preserved work was reused; none was discarded.

The final closed list contains five production modules, five new or updated functional test modules, the reconciled architecture test, the package README, this report, the SPR-019 plan, and the Sprint index. No 16th path was changed. P-019-04 and P-018-02 remain not authorized.

## 2. Implemented capability

Five frozen, slotted domain models were added while preserving the original four: `DiscoveryPolicy`, `DiscoveryIssue`, `DiscoveredFile`, `DuplicateGroup`, and `DiscoveryReport`. The default policy recognizes `.pdf`, `.docx`, `.txt`, `.md`, and `.markdown`; ignores hidden content; does not follow symlinks; and hashes in 1 MiB chunks.

`infrastructure.hashing` calculates lowercase SHA-256 incrementally, compares size and `mtime_ns` before and after reading, rejects mutation with a stable recoverable code, and sanitizes read errors. `infrastructure.filesystem` requires an explicit valid directory, resolves it before scanning, uses resolved descendant checks, ignores hidden and unsupported entries, refuses symlink following, and continues after isolated file failures. It performs no semantic PDF or DOCX access.

`application.duplicates` is a pure function that groups only by SHA-256, verifies consistent size, sorts groups by digest, and preserves every relative location. `application.discovery` coordinates scanning and grouping into a deterministic immutable in-memory report without persistence, printing, CLI, extraction, SQLite, or FTS.

## 3. Architectural reconciliation

The obsolete rule that allowed only `infrastructure/__init__.py` was replaced by an exact set allowing `__init__.py`, `filesystem.py`, and `hashing.py`. The test still rejects every unlisted infrastructure module and retains all dependency, CLI, packaging, and Core-isolation checks.

```text
ARCHITECTURE_BOUNDARY_RECONCILIATION: PASS
ARCHITECTURE_TEST_SKIPPED: NO
ALLOWED_INFRASTRUCTURE_MODULE_COUNT: 3
UNAUTHORIZED_INFRASTRUCTURE_MODULE_COUNT: 0
```

## 4. Synthetic corpus and behavior

Discovery of the P-019-02 corpus produced 11 supported locations, ignored the unsupported binary, and produced one duplicate group preserving both ordered locations. Corrupt PDF and DOCX cases were inventoried as bytes without extraction. Hidden-file and isolated-failure tests passed. Both tests requiring actual Windows symlink creation were skipped only after the operating system denied the operation; the unsupported-follow policy and controlled non-follow behavior remained tested.

```text
SUPPORTED_EXTENSION_COUNT: 5
DEFAULT_IGNORE_HIDDEN: YES
DEFAULT_FOLLOW_SYMLINKS: NO
HASH_ALGORITHM: SHA-256
HASH_CHUNK_SIZE: 1048576 BYTES
HASH_MUTATION_DETECTION: SIZE AND MTIME_NS BEFORE/AFTER
ROOT_CONFINEMENT_STATUS: PASS
DETERMINISTIC_ORDER_STATUS: PASS
DISCOVERY_FILE_COUNT_IN_SYNTHETIC_CORPUS: 11
DUPLICATE_GROUP_COUNT: 1
DUPLICATE_LOCATION_PRESERVATION: PASS
ISOLATED_FAILURE_CONTINUATION: PASS
```

## 5. Tests

The 33-test baseline was preserved. P-019-01 passed 11/11; the P-019-02 group collected 22 tests and passed 21 with its existing symlink skip. P-019-03 added 34 collected cases: 33 in four new files and one additional scope gate. The final suite collected 67 tests and finished with 65 passed and two justified symlink skips.

```text
P_019_01_REGRESSION: PASS — 11 PASSED
P_019_02_REGRESSION: PASS — 21 PASSED / 1 SKIPPED
PREEXISTING_TEST_COUNT: 33
P_019_03_TEST_COUNT: 34
TOTAL_LOCAL_FINDER_TEST_COUNT: 67
TEST_RESULT: PASS — 65 PASSED / 2 SKIPPED
SKIPPED_TEST_COUNT: 2
```

## 6. Packaging and installation

Two independent temporary builds used a fixed `SOURCE_DATE_EPOCH`. Wheels were byte-identical with SHA-256 `63bbe676d0002aa80e40b167e7d585b72c391b245b6f365bfa58fa94535c6b44`. The two sdists had identical names and per-file content hashes for all 31 files; only gzip container metadata varied.

Fresh temporary environments validated isolated installation, joint installation with `cko 1.0.0`, joint installation with `cko-fcp 0.1.0`, simultaneous import of all three namespaces, and `pip check`.

```text
PACKAGING_TESTS: PASS
WHEEL_REPRODUCIBILITY: PASS — IDENTICAL ARTIFACT SHA-256
SDIST_REPRODUCIBILITY: PASS — 31/31 FILE CONTENT HASHES IDENTICAL
ISOLATED_INSTALL_STATUS: PASS
CKO_DUAL_INSTALL_STATUS: PASS
CKO_FCP_DUAL_INSTALL_STATUS: PASS
IMPORT_COEXISTENCE_STATUS: PASS
```

## 7. Permanent gates

The canonical ordered-export algorithm matched in source and in the freshly installed Core wheel.

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
```

## 8. Environment, security, and Git

The global Python installation had no pytest and was not modified. All test environments, generated documents, wheels, sdists, build directories, and installations remained in the operating-system temporary area outside the repository.

Initial Git state was `main` at `3a8a28ea1fd1e26b094cd8d3cb7fd20540caecea`, matching local and real remote `origin/main`, with empty staging. The 11 preexisting untracked artifacts, recovery snapshots, historical baseline, external databases, and real user documents were preserved.

The final diff was checked for exact scope, UTF-8, final newlines, trailing whitespace, local absolute paths, secrets, binaries, databases, wheels, sdists, virtual environments, caches, extraction, SQLite, FTS, persistence, and CLI behavior. This report intentionally has no mandatory self-hash.

## 9. Conclusion

P-019-03 provides internal safe local discovery, physical SHA-256 identity, and duplicate detection only. P-019-04 remains planned and not authorized.

`P-019-03 IMPLEMENTED / VALIDATED / CONSOLIDATED — P-019-04 NOT AUTHORIZED`
