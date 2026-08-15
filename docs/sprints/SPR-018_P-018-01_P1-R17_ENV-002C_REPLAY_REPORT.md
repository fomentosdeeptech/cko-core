# CKO — SPR-018 — P-018-01 P1-R17 ENV-002C Replay Report

**Date:** 2026-08-13  
**Operation:** ENV-002C — corrected P1-R17 validation replay  
**Classification:** `ENVIRONMENT_FAILURE`

## A. Initial Git state

- Branch: `main`
- HEAD: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Local `origin/main`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Remote `origin/main`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Peeled baseline: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
- Staging: empty
- Tracked diff: empty
- Existing untracked files preserved.
- All eleven P-018-01 artifacts matched their authorized SHA-256 values.

## B–D. Python environment and corrected smoke

- Runtime: `C:\Users\ANDRÉ\AppData\Local\CKO\cko-py313-validation\Scripts\python.exe`
- CPython: `3.13.15`, 64-bit
- pip: `26.2.1`
- pytest: `9.1.1`
- Successful smoke imports: typer, rich, pydantic, networkx, fastapi, uvicorn, dotenv, yaml, and `cko`.
- Python, pip, and pytest smoke checks passed.

ENV-002C corrected the version target from the invalid `cko.__version__` to the canonical `cko.core.__version__`. However, the `import cko.core` verification did not complete within the 30-second execution window and produced no output, traceback, or success marker. A continuation containing only `import cko.core`, the `cko.core.__version__ == "1.0.0"` assertion, and `pip check` again exceeded the same window without output.

Because `ENVIRONMENT_SMOKE: PASS` could not be established, the mandatory stop rule was applied. No automatic environment or code correction was attempted.

`PYTHON_3_13_VALIDATED: YES`  
`ENVIRONMENT_SMOKE: FAIL (cko.core import timeout)`

## E–K. Phases not executed

- Dedicated tests: not executed.
- Full regression: not executed.
- Current SDK/API mechanical calculation: not executed.
- Current API fingerprint: not executed.
- Wheel build/content inspection: not executed.
- Isolated wheel replay: not executed.

Historical results were not reused as current ENV-002C evidence.

## L. Gates P1-R0–P1-R20

| Gate | ENV-002C status | Current evidence |
|---|---|---|
| P1-R0–P1-R16 | NOT REPLAYED | Replay stopped during the corrected environmental smoke. |
| P1-R17 | BLOCKED | `cko.core` import did not complete within the available execution window; no smoke PASS was established. |
| P1-R18–P1-R20 | NOT REPLAYED | Replay stopped before gate validation. |

## M–N. Failure and final working tree

- Failure classification: `ENVIRONMENT_FAILURE`.
- No production code, test, requirement, packaging, Core, API, or SDK file was changed.
- No staging, commit, push, reset, clean, checkout, rebase, merge, move, or deletion was performed.
- This report is the only repository artifact created by ENV-002C.

## O–P. Required results and decision

`PYTHON_3_13_VALIDATED: YES`  
`ENVIRONMENT_SMOKE: FAIL`  
`DEDICATED_TESTS: NOT EXECUTED`  
`FULL_REGRESSION: NOT EXECUTED`  
`SDK_VERSION: NOT MECHANICALLY VALIDATED IN ENV-002C`  
`PUBLIC_API_COUNTS: NOT EXECUTED`  
`PUBLIC_API_FINGERPRINT: NOT EXECUTED`  
`WHEEL_BUILD: NOT EXECUTED`  
`ISOLATED_WHEEL_REPLAY: NOT EXECUTED`  
`P1_R17_STATUS: BLOCKED`  
`P_018_01_VALIDATION_STATUS: BLOCKED`  
`READY_FOR_GIT_CONSOLIDATION: NO`  
`PUBLIC_API_IMPACT: NONE DETECTED; CURRENT MECHANICAL CHECK NOT EXECUTED`  
`BREAKING_CHANGE: NO EVIDENCE; CURRENT MECHANICAL CHECK NOT EXECUTED`  
`P_018_02_AUTHORIZED: NO`

Recommended next action: authorize a bounded diagnostic of the `cko.core` import duration/hang under Python 3.13 before another P1-R17 replay. Do not change project code or dependencies without a separate decision.

## Verdict

`P1-R17 BLOCKED — VALIDATION ENVIRONMENT NOT READY`
