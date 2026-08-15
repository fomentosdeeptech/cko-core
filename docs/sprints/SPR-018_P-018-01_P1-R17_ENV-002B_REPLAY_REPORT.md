# CKO — SPR-018 — P-018-01 P1-R17 ENV-002B Replay Report

**Date:** 2026-08-13  
**Operation:** ENV-002B — P1-R17 validation replay  
**Outcome classification:** `VALIDATION_PROCEDURE_FAILURE`

## Initial Git state

- Repository: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`
- Branch: `main`
- HEAD: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Local `origin/main`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Remote `origin/main`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Peeled `CKO-BASELINE-2026.07`: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
- Staging: empty
- Tracked diff: empty
- Existing untracked content was preserved.
- All eleven P-018-01 implementation/test artifacts were present and their SHA-256 values exactly matched the implementation report.

## Runtime and dependency revalidation

- Runtime used exclusively: `C:\Users\ANDRÉ\AppData\Local\CKO\cko-py313-validation\Scripts\python.exe`
- CPython: `3.13.15`
- Architecture: `64-bit WindowsPE`
- pip: `26.2.1`
- pytest: `9.1.1`
- Individual imports passed:
  - pytest `9.1.1`
  - typer `0.27.1`
  - rich `15.0.0`
  - pydantic `2.13.4`
  - networkx `3.6.1`
  - fastapi `0.141.1`
  - uvicorn `0.52.3`
  - python-dotenv `1.2.2`
  - pyyaml `6.0.3`
- `pip check`: `No broken requirements found`

`PYTHON_3_13_VALIDATED: YES`

## Environmental smoke and stop condition

The smoke independently confirmed Python, pip, pytest, typer, and import of the `cko` root package. The command then attempted to read `cko.__version__` and failed:

```text
AttributeError: module 'cko' has no attribute '__version__'
```

Read-only inspection after the stop confirmed that the canonical SDK version attribute is `cko.core.__version__`, defined as `1.0.0`. The root `src/cko/__init__.py` does not define `__version__`. Therefore this is not evidence of an environment defect, P-018-01 defect, API change, or SDK regression; it is a validation-procedure error caused by checking the version on the wrong module.

ENV-002B explicitly requires an immediate stop after any Phase 2 smoke failure. The smoke was not retried with the corrected module.

`ENVIRONMENT_SMOKE: FAIL (VALIDATION_PROCEDURE_FAILURE)`

## Phases not executed

Because the stop rule triggered, the following were not executed in ENV-002B:

- dedicated `tests/fcp/` suite;
- full repository pytest regression;
- current mechanical API 646/646/646 calculation;
- current API fingerprint calculation;
- wheel build and wheel-content inspection;
- isolated wheel replay;
- installed-wheel tests.

Historical values were not promoted to current replay results:

- dedicated tests: 22 passed historically;
- SDK: 1.0.0 historically and confirmed read-only in `cko.core.__version__` source;
- API: 646/646/646 historically;
- fingerprint: `d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232` historically.

## Gates P1-R0–P1-R20

The implementation report records historical PASS for P1-R0–R16 and P1-R18–R20, with P1-R17 blocked. ENV-002B did not presume or overwrite those results. Current replay evidence is:

| Gate | ENV-002B status | Evidence |
|---|---|---|
| P1-R0–P1-R16 | NOT REPLAYED | Historical PASS only; replay stopped before dedicated/full validation. |
| P1-R17 | FAILED | Phase 2 smoke invocation failed because the validation procedure queried `cko.__version__` instead of `cko.core.__version__`. |
| P1-R18–P1-R20 | NOT REPLAYED | Historical PASS only; final replay phases were not reached. |

## Required results

`PYTHON_3_13_VALIDATED: YES`  
`ENVIRONMENT_SMOKE: FAIL`  
`DEDICATED_TESTS: NOT EXECUTED`  
`FULL_REGRESSION: NOT EXECUTED`  
`SDK_VERSION: NOT MECHANICALLY VALIDATED IN THE AUTHORIZED SEQUENCE`  
`PUBLIC_API_COUNTS: NOT EXECUTED`  
`PUBLIC_API_FINGERPRINT: NOT EXECUTED`  
`WHEEL_BUILD: NOT EXECUTED`  
`ISOLATED_WHEEL_REPLAY: NOT EXECUTED`  
`P1_R17_STATUS: FAILED`  
`P_018_01_VALIDATION_STATUS: FAILED`  
`READY_FOR_GIT_CONSOLIDATION: NO`  
`PUBLIC_API_IMPACT: NONE DETECTED; CURRENT MECHANICAL CHECK NOT EXECUTED`  
`BREAKING_CHANGE: NO EVIDENCE; CURRENT MECHANICAL CHECK NOT EXECUTED`  
`P_018_02_AUTHORIZED: NO`

## Repository effects and next action

- No production code, tests, requirements, packaging, Core, API, or SDK files were changed.
- No staging, commit, push, pull, reset, clean, checkout, rebase, merge, move, or deletion was performed.
- This report is the only repository artifact created by ENV-002B.
- Next action: obtain a new explicit replay authorization and run the Phase 2 version smoke against `cko.core.__version__`; only after it passes may the dedicated suite and later P1-R17 phases proceed.

## Verdict

`P1-R17 FAILED — P-018-01 NOT READY FOR CONSOLIDATION`
