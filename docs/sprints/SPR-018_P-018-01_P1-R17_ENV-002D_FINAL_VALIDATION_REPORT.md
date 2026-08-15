# CKO — SPR-018 — P-018-01 P1-R17 ENV-002D Final Validation Report

**Date:** 2026-08-13  
**Operation:** ENV-002D — P1-R17 Final Validation Replay  
**Verdict:** `P1-R17 FAILED — P-018-01 REQUIRES TECHNICAL REVIEW`

## A. Documentary authority

All nine authorities required by ENV-002D were read. DIAG-001 was verified with its self-contained convention: SHA-256 of UTF-8 content with LF endings and the embedded digest replaced by `<SHA256>`. Result: `6a53401201d8136f80cf5442a08e2a1ddd7edeaacfc450c4ae8db8475680405d`.

## B. Initial Git state

- Branch: `main`
- HEAD: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Local and remote `origin/main`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Peeled baseline: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
- Staging: empty
- Tracked diff: empty
- Existing untracked files were preserved.

## C–D. Environment and instrumented smoke

- Executable: `C:\Users\ANDRÉ\AppData\Local\CKO\cko-py313-validation\Scripts\python.exe`
- Runtime: CPython 3.13.15, 64-bit AMD64
- Source layout supplied only to the process through `PYTHONPATH=<repository>\src`.
- `cko.__file__`: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE\src\cko\__init__.py`
- `import cko`: PASS in 0.010407 s.
- `import cko.core`: PASS in 2.468840 s.
- Whole-process wall time: 2.687022 s.
- Python subprocess exit code: 0.
- `cko.core.__version__`: 1.0.0.
- `faulthandler.dump_traceback_later(10)` was armed and cancelled after successful completion; no stack dump was needed.

`ENVIRONMENT_SMOKE: PASS`

## E. Dedicated tests

Command: validation Python 3.13 `-B -m pytest tests/fcp -ra`.

- Collected: 22
- Passed: 22
- Failed/errors/skipped/xfail/xpass: 0
- Duration: 0.98 s
- Exit code: 0

`DEDICATED_TESTS: PASS — 22/22`

## F. Full regression

Command: validation Python 3.13 `-B -m pytest -ra`, without exclusions or warning suppression.

- Collected: 952
- Passed: 948
- Failed: 4
- Errors/skipped/xfail/xpass: 0
- Duration: 85.75 s
- Pytest result: failed

Failures:

1. `tests/test_file_metadata.py::test_collect_metadata` — `TypeError`: pre-existing `collect_metadata()` does not accept the test's `calculate_hash` keyword. Classification: `HISTORICAL_REGRESSION`.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved` — Windows `PermissionError [WinError 32]` deleting an open temporary SQLite file during teardown. Classification: `ENVIRONMENT_FAILURE` / pre-existing persistence surface.
3. `tests/test_workspace_manager.py::test_environment_validation_covers_all_requirements` — encoding validation observed `UTF-8, cp1252, utf-8` and returned invalid. Classification: `ENVIRONMENT_FAILURE`.
4. `tests/test_workspace_manager.py::test_cli_validation_uses_installed_python_and_powershell` — same cp1252 encoding condition caused CLI validation exit 1. Classification: `ENVIRONMENT_FAILURE`.

None is in `external/fcp` or `tests/fcp`; the dedicated package suite passed. No causal relation to P-018-01 was found. Nevertheless, the required full regression did not pass.

`FULL_REGRESSION: FAIL — 948 passed, 4 failed`

## G–I. SDK, public API, and fingerprint

Recalculated from the source layout in a fresh Python process:

- `SDK_VERSION: 1.0.0`
- `PUBLIC_EXPORT_COUNT: 646`
- `UNIQUE_EXPORT_COUNT: 646`
- `RESOLVED_EXPORT_COUNT: 646`
- `PUBLIC_API_COUNTS: 646 / 646 / 646`
- `PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`

Fingerprint algorithm reproduced mechanically: ordered `cko.core.__all__`; fields `name`, `module`, `qualname`, `type`, and `signature`; unavailable module/qualname/signature represented as null; compact UTF-8 JSON with sorted object keys; SHA-256 of the resulting bytes.

## J–L. Wheel build and isolated replay

ENV-002D permits wheel construction only if smoke, dedicated tests, full regression, and API all pass. The full regression failed, so:

- `WHEEL_BUILD: NOT EXECUTED — PRECONDITION FAILED`
- `WHEEL_SHA256: NOT AVAILABLE`
- `WHEEL_CONTENT: NOT INSPECTED`
- `ISOLATED_WHEEL_REPLAY: NOT EXECUTED — NO ELIGIBLE WHEEL`

Packaging was not changed.

## M. P-018-01 protection

- `src/cko` contains no reference/import to `external/fcp` or `tests/fcp`.
- `external/fcp` contains no import of `cko` or `cko.core`.
- Production FCP scan found no I/O, network, database, subprocess, credentials, real URLs, secrets, or personal-data surface.
- Matches for publication in `external/fcp` are the P-018-01 logical publication state axis and its fail-closed invariants, not P-018-02 publication authority/query implementation.
- P-018-02–05 were not implemented or authorized.
- Core, SDK, API, requirements, tests, and packaging have no tracked diff.

## N. Gates P1-R0–P1-R20

| Gate | Status | Current ENV-002D evidence |
|---|---|---|
| P1-R0 | PASS | Git refs, peeled baseline, empty staging, and preserved working tree verified. |
| P1-R1 | PASS | Eleven implementation/test artifacts present with their authorized SHA-256 values. |
| P1-R2 | PASS | Strict ordered version behavior covered by current dedicated run. |
| P1-R3 | PASS | Opaque immutable source identity covered by current dedicated run. |
| P1-R4 | PASS | Closed schemas reject missing/unknown fields. |
| P1-R5 | PASS | Strict validation rejects coercion. |
| P1-R6 | PASS | Record cardinality, uniqueness, and canonical ordering tests passed. |
| P1-R7 | PASS | Four state axes remain independent. |
| P1-R8 | PASS | Record invariants fail closed. |
| P1-R9 | PASS | Valid and invalid single-axis lifecycle transitions passed. |
| P1-R10 | PASS | Terminal publication states cannot be restored. |
| P1-R11 | PASS | Version/capability intersection passed. |
| P1-R12 | PASS | Incompatible major version fails semantically. |
| P1-R13 | PASS | Missing required capability fails. |
| P1-R14 | PASS | Unsafe downgrade can be refused. |
| P1-R15 | PASS | Read-only envelope acceptance and write/deadline rejection passed. |
| P1-R16 | PASS | Golden serialization, repeated determinism, canonical mapping order, negative codes, and no-I/O tests passed. |
| P1-R17 | FAIL | Python 3.13 smoke and dedicated tests passed, but full regression has four failures; wheel build/replay therefore ineligible. |
| P1-R18 | PASS | SDK 1.0.0, API 646/646/646, and authorized fingerprint recalculated exactly. |
| P1-R19 | PASS | Mechanical scans show no Core↔FCP dependency and no prohibited production I/O/network/database/credential surface. |
| P1-R20 | PASS | P-018-01 remains external; no P-018-02–05 implementation or tracked protected-surface change detected. |

## O–Q. Final working tree, blockers, and decision

- Staging remains empty.
- Tracked diff remains empty.
- No add, commit, push, reset, clean, merge, rebase, code edit, test edit, requirement edit, packaging edit, or environment reprovisioning occurred.
- This ENV-002D report is the only authorized new artifact from this operation.

Blocking evidence: four failures in the mandatory full regression. Although they are not attributable to P-018-01, ENV-002D requires the full suite to pass before wheel build/replay and final satisfaction of P1-R17.

`PYTHON_3_13_VALIDATED: YES`  
`CKO_ROOT_IMPORT: IMPORT_OK`  
`CKO_CORE_IMPORT: IMPORT_OK`  
`CKO_CORE_IMPORT_DURATION: 2.468840 s`  
`ENVIRONMENT_SMOKE: PASS`  
`DEDICATED_TESTS: PASS — 22/22`  
`FULL_REGRESSION: FAIL — 948 passed, 4 failed`  
`SDK_VERSION: 1.0.0`  
`PUBLIC_API_COUNTS: 646 / 646 / 646`  
`PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`  
`WHEEL_BUILD: NOT EXECUTED — PRECONDITION FAILED`  
`WHEEL_SHA256: NOT AVAILABLE`  
`ISOLATED_WHEEL_REPLAY: NOT EXECUTED`  
`P1_R17_STATUS: FAILED`  
`P_018_01_VALIDATION_STATUS: FAILED`  
`READY_FOR_GIT_CONSOLIDATION: NO`  
`PUBLIC_API_IMPACT: NONE`  
`BREAKING_CHANGE: NO`  
`P_018_01_CAUSAL_RELATION_TO_PREVIOUS_TIMEOUT: NO`  
`P_018_02_AUTHORIZED: NO`

## R. Canonical SHA-256

`CANONICAL_SHA256: 2584e2d4a039d7b21ccc91191a19fbe5992afb8e049e2431626f40a713826823`

Convention: SHA-256 of the complete UTF-8 file after replacing the embedded hexadecimal digest with `<SHA256>` and normalizing line endings to LF.

## Verdict

`P1-R17 FAILED — P-018-01 REQUIRES TECHNICAL REVIEW`
