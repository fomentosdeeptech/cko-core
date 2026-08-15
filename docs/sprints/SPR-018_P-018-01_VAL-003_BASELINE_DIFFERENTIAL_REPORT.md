# CKO — SPR-018 — P-018-01 VAL-003 Baseline Differential Report

**Date:** 2026-08-13  
**Operation:** VAL-003 — P1-R17 Baseline Differential Regression  
**Verdict:** `VAL-003 COMPLETE — P-018-01 INTRODUCES ZERO NEW REGRESSIONS`

## A. Initial state

- Repository: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`
- Branch: `main`
- HEAD, local `origin/main`, and remote `origin/main`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Peeled baseline: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
- Staging: empty
- Tracked diff: empty
- Existing untracked content was preserved.

## B. Clean-reference construction

The clean reference was created outside CORE from the exact tracked contents of commit `45d3bf87f9f01b663971b0dd6fa306aa207ab679` using read-only `git archive`, then extracted under the user temporary directory. No checkout, reset, clean, ref update, index update, or working-tree mutation was performed.

- Reference file count: 490 tracked files.
- `external/fcp/`: absent.
- `tests/fcp/`: absent.
- P-018-01 implementation and ENV/DIAG reports: absent.
- The reference therefore represents canonical HEAD without P-018-01.

## C. Runtime

- Executable: `C:\Users\ANDRÉ\AppData\Local\CKO\cko-py313-validation\Scripts\python.exe`
- CPython: 3.13.15 x64
- pytest: 9.1.1
- Same installed dependencies and Windows host as ENV-002D.
- `PYTHONPATH` was set only for clean-reference processes to `<TEMP_REFERENCE>\src`.
- No package was installed or updated.

## D–F. Absence proof, smoke, and API

The clean reference contained neither P-018-01 production files nor its dedicated tests. Its smoke passed:

- `import cko`: PASS
- `import cko.core`: PASS
- `cko.core.__version__`: 1.0.0
- Public API: 646 exports / 646 unique / 646 resolved
- Public API fingerprint: `d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`

## G. Clean HEAD regression

Command: the same approved Python 3.13 runtime, `-B -m pytest -ra`, from the clean archived tree, with no exclusions, configuration changes, or warning suppression.

- Collected: 930
- Passed: 925
- Failed: 5
- Errors/skipped/xfail/xpass: 0
- Duration: 12.81 s
- Exit code: 1

Failures:

1. `tests/test_core_consolidation_spr009a.py::test_official_version_is_consistent` — `FileNotFoundError` for `src/cko.egg-info/PKG-INFO`. This is additional baseline debt: the tracked test depends on an artifact absent from the tracked commit but present as untracked content in the main working tree.
2. `tests/test_file_metadata.py::test_collect_metadata` — `TypeError: collect_metadata() got an unexpected keyword argument 'calculate_hash'`.
3. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved` — `PermissionError [WinError 32]` deleting the open temporary SQLite file during teardown.
4. `tests/test_workspace_manager.py::test_environment_validation_covers_all_requirements` — environment invalid because encoding values include `cp1252`.
5. `tests/test_workspace_manager.py::test_cli_validation_uses_installed_python_and_powershell` — CLI exit 1 because the same encoding check fails.

## H. ENV-002D regression

ENV-002D, from the main working tree with P-018-01 present, collected 952 tests: 948 passed and the four target tests failed. Its additional 22 tests are exactly the dedicated P-018-01 suite, all of which passed.

## I. Test-by-test differential

| ENV-002D failure | Clean HEAD result | Classification | Differential evidence |
|---|---|---|---|
| `test_collect_metadata` | Failed at the same call | `REPRODUCED_IDENTICALLY` | Same node ID, `TypeError`, keyword `calculate_hash`, assertion phase, and apparent signature mismatch. |
| `test_existing_table_is_preserved` | Failed during the same teardown | `REPRODUCED_WITH_ENVIRONMENTAL_VARIATION` | Same node ID, `PermissionError`, WinError 32, open `cko.db`, and cleanup phase; only randomized temporary paths differ. |
| `test_environment_validation_covers_all_requirements` | Failed at the same assertion | `REPRODUCED_WITH_ENVIRONMENTAL_VARIATION` | Same node ID, `AssertionError`, invalid encoding check, and `cp1252`; only temporary paths/free-space values differ. |
| `test_cli_validation_uses_installed_python_and_powershell` | Failed at the same assertion | `REPRODUCED_WITH_ENVIRONMENTAL_VARIATION` | Same node ID, CLI result 1, and failed `cp1252` encoding check; timestamps, paths, and free-space values vary. |

Normalized-LF SHA-256 comparison confirmed identical tracked content between the main working tree and clean archive for all four implicated test files and `src/cko/core/workspace/validator.py`. Raw hashes differed only because the working tree used CRLF while `git archive` emitted LF; `git diff` remained empty.

## J–K. Causality and new regressions

H0 is mechanically supported. All four target failures reproduce without `external/fcp` and `tests/fcp`. P-018-01 adds 22 passing tests and does not alter the tracked sources/tests responsible for the failures.

`P_018_01_NEW_REGRESSIONS: 0`  
`P_018_01_CAUSAL_RELATION_TO_FULL_REGRESSION_FAILURES: NO`

## L. Impact on P1-R17

Interpretation demonstrated:

`FULL REGRESSION HAS PRE-EXISTING FAILURES AND P-018-01 INTRODUCES ZERO NEW REGRESSIONS`

VAL-003 does not change P1-R17 automatically. There is technical evidence for a competent human authority to consider allowing wheel build/replay while explicitly recognizing the five clean-HEAD failures as baseline technical debt. Such authorization was not issued or inferred here.

`P1_R17_WHEEL_REPLAY_CAN_BE_CONSIDERED: YES — SUBJECT TO HUMAN DECISION`

## M. Pre-existing technical debt

`BASELINE_TECHNICAL_DEBT_PRESENT: YES`

The canonical tracked HEAD has five failures under the approved Python 3.13 environment. Four match ENV-002D. The fifth shows that a tracked version-consistency test depends on untracked `src/cko.egg-info/PKG-INFO`. These remain real global-quality defects even though none was introduced by P-018-01.

## N. Recommendation

1. Preserve P1-R17's current state pending a human decision.
2. The authority may separately allow wheel build/replay for P-018-01 based on zero differential regressions, while recording the clean-HEAD failures as accepted baseline debt for that validation step.
3. Address the five baseline failures in a separately authorized maintenance operation; do not modify P-018-01 to mask them.
4. Do not authorize or initiate P-018-02.

## O. Canonical SHA-256

`CANONICAL_SHA256: 7164e1839dc102110385c9f86af377ab36d6e433e246e5de98523fa77bccbdcc`

Convention: SHA-256 of the complete UTF-8 report after replacing the embedded hexadecimal digest with `<SHA256>` and normalizing line endings to LF.

## P. Final Git state and mandatory results

- Main repository staging: empty.
- Main repository tracked diff: empty.
- No code, test, environment, requirement, packaging, Core, or FCP file was changed.
- This report is the only repository artifact created by VAL-003.

`CLEAN_HEAD_TESTS: 930`  
`CLEAN_HEAD_PASSED: 925`  
`CLEAN_HEAD_FAILED: 5`  
`FAILURE_1_REPRODUCED: REPRODUCED_IDENTICALLY`  
`FAILURE_2_REPRODUCED: REPRODUCED_WITH_ENVIRONMENTAL_VARIATION`  
`FAILURE_3_REPRODUCED: REPRODUCED_WITH_ENVIRONMENTAL_VARIATION`  
`FAILURE_4_REPRODUCED: REPRODUCED_WITH_ENVIRONMENTAL_VARIATION`  
`P_018_01_NEW_REGRESSIONS: 0`  
`P_018_01_CAUSAL_RELATION_TO_FAILURES: NO`  
`BASELINE_TECHNICAL_DEBT_PRESENT: YES`  
`P1_R17_WHEEL_REPLAY_CAN_BE_CONSIDERED: YES — SUBJECT TO HUMAN DECISION`  
`PROJECT_CODE_CHANGE_REQUIRED_FOR_P_018_01: NO`  
`P_018_02_AUTHORIZED: NO`

## Verdict

`VAL-003 COMPLETE — P-018-01 INTRODUCES ZERO NEW REGRESSIONS`
