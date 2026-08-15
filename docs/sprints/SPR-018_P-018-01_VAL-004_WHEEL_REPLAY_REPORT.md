# CKO — SPR-018 — P-018-01 VAL-004 Wheel Replay Report

**Date:** 2026-08-13  
**Operation:** VAL-004 — P1-R17 Wheel Build and Isolated Replay  
**Verdict:** `VAL-004 BLOCKED — P-018-01 PACKAGING DECISION REQUIRED`

## A. Human decision

This reconciled candidate references VAL-003 and its candidate canonical SHA-256
`7164e1839dc102110385c9f86af377ab36d6e433e246e5de98523fa77bccbdcc`.
`RECONCILIATION_STATUS: PENDING_HUMAN_RE_RATIFICATION`
`VAL003_NEW_HASH_STATUS: CANDIDATE_PENDING_HUMAN_RE_RATIFICATION`
The five clean-HEAD failures are recognized only for this differential validation
as pre-existing baseline technical debt. VAL-003 established mechanically:

- `P_018_01_NEW_REGRESSIONS: 0`
- `P_018_01_CAUSAL_RELATION_TO_FAILURES: NO`
- `BASELINE_TECHNICAL_DEBT_PRESENT: YES`

The decision authorized only wheel build, mechanical inspection, isolated replay,
and the technical P1-R17 conclusion. It did not authorize changes to code, tests,
Core, packaging, requirements, API, or P-018-02.

## B. Authorities

The following required authorities were read before execution:

- `docs/sprints/SPR-018_P-018-01_IMPLEMENTATION_REPORT.md`
- `docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002D_FINAL_VALIDATION_REPORT.md`
- `docs/sprints/SPR-018_P-018-01_VAL-003_BASELINE_DIFFERENTIAL_REPORT.md`
- `docs/sprints/SPR-018_P-018-01_DIAG-001_CKO_CORE_IMPORT_REPORT.md`
- `docs/sprints/SPR-018_TECHNICAL_SPECIFICATION.md`
- `docs/reviews/REV-003_SPR-018_HUMAN_GATE_REVIEW.md`

VAL-003 was treated as the latest differential authority. Its canonical digest
was independently recalculated with its documented LF/placeholder convention and
matched the reconciled candidate value; human re-ratification remains pending.

## C. Preflight

- Branch: `main`
- HEAD: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Local `origin/main`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Peeled `CKO-BASELINE-2026.07`: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
- Staging: empty
- Tracked diff before this report: empty
- Existing untracked artifacts documented by prior authorities were preserved.

No material divergence was found.

## D. Minimum integrity checks

Authorized runtime:
`C:\Users\ANDRÉ\AppData\Local\CKO\cko-py313-validation\Scripts\python.exe`.

- CPython: `3.13.15`, 64-bit
- `import cko`: pass from repository `src` layout
- `import cko.core`: pass from repository `src` layout
- SDK: `1.0.0`
- Public API: `646 / 646 / 646`
- Fingerprint: `d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`
- Dedicated command: authorized Python `-B -m pytest tests/fcp -ra`
- Dedicated result: `22 passed in 0.82s`, exit code `0`

An initial evidence-harness expression did not handle a builtin type whose
signature is unavailable and exited `1`. The check was immediately repeated with
the VAL-003 algorithm, representing unavailable signatures as null; imports,
counts, resolution, SDK, and fingerprint then all matched with exit code `0`.
This was a harness correction only and did not alter the repository.

## E. Wheel build

Packaging remained the current PEP 517 configuration:
`setuptools.build_meta`, build requirement `setuptools>=68`, source discovery
under `src`, project `cko`, version `1.0.0`.

Two unavailable local-frontend attempts were retained as evidence:

1. authorized Python `-B -m build --wheel --outdir <TEMP>\dist .` — exit `1`;
   the optional `build` module was not installed.
2. authorized Python `-B -m pip wheel --no-deps --no-build-isolation
   --wheel-dir <TEMP>\dist .` — exit `2`; the runtime did not contain the declared
   `setuptools` backend.

The effective build used normal PEP 517 isolation, installing only the declared
build requirement into pip's temporary build environment:

`<authorized-python> -B -m pip wheel --no-deps --wheel-dir <TEMP>\dist .`

The wheel was produced successfully. No project dependency, packaging file,
metadata, version, source, or runtime environment was changed.

## F. Wheel SHA-256

- Name: `cko-1.0.0-py3-none-any.whl`
- Size: `438680` bytes
- SHA-256: `8e2c7cf609855a9f88779bfbef4d9cc16c542e00c6468dfe143887928d12a650`

## G. Wheel content

Mechanical ZIP inspection found 280 entries: 276 Python files under `cko/` and
four standard `cko-1.0.0.dist-info/` entries (`METADATA`, `RECORD`,
`top_level.txt`, and `WHEEL`). The 276 packaged Python files matched the 276
Python files under `src/cko`; none was missing or extra.

- `FCP_INCLUDED_IN_WHEEL: NO`
- `EXTERNAL_FCP_INCLUDED: NO`
- `UNEXPECTED_FILES: NONE`
- `PUBLIC_API_CHANGED: NO`
- `PACKAGING_CHANGE_REQUIRED: YES — HUMAN DECISION REQUIRED; NOT AUTHORIZED HERE`

P-018-01 is implemented under `external/fcp/`, outside the current `src` package
discovery. Its absence is consistent with the current architecture and packaging
configuration, but it prevents the installed artifact from exposing the validated
foundation. Therefore:

`P_018_01_PACKAGING_STATUS: PACKAGING_GAP_REQUIRING_HUMAN_DECISION`

No packaging correction was attempted.

## H. Isolated environment

A temporary Python 3.13 virtual environment was created outside the repository
from the authorized runtime. `PYTHONPATH` was removed. Replay ran from the
temporary directory, not the working tree, and the imported modules resolved from
the virtual environment's `Lib\site-packages`.

## I. Installation

The newly built wheel was the only project artifact installed. Its metadata
declared no runtime `Requires-Dist` dependencies. pip reported:

`Successfully installed cko-1.0.0`

`WHEEL_INSTALL: PASS`

## J. pip check

`No broken requirements found.`

`PIP_CHECK: PASS`

## K. SDK

- `ISOLATED_CKO_IMPORT: PASS`
- `ISOLATED_CKO_CORE_IMPORT: PASS`
- `SDK_VERSION: 1.0.0`
- `SDK_VERSION_UNCHANGED: YES`

## L. Public API

- `PUBLIC_EXPORT_COUNT: 646`
- `UNIQUE_EXPORT_COUNT: 646`
- `RESOLVED_EXPORT_COUNT: 646`
- `PUBLIC_API_COUNTS: 646 / 646 / 646`
- `PUBLIC_API_COUNTS_UNCHANGED: YES`
- `PUBLIC_API_CHANGED: NO`
- `CORE_CHANGED: NO`
- `BREAKING_CHANGE: NO`

## M. Fingerprint

The installed wheel was measured with the same ordered-export algorithm used by
VAL-003: name, module, qualname, type, and signature; unavailable values represented
as null; compact UTF-8 JSON with sorted object keys; SHA-256 of those bytes.

- `PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`
- `PUBLIC_API_FINGERPRINT_UNCHANGED: YES`

## N. P-018-01 presence and importability

- `P_018_01_PRESENT_IN_REPOSITORY: YES`
- `P_018_01_PRESENT_IN_WHEEL: NO`
- `P_018_01_IMPORTABLE_FROM_INSTALLED_ARTIFACT: NO`
- isolated `import external.fcp`: `ModuleNotFoundError: No module named 'external'`
- isolated `import fcp`: `ModuleNotFoundError: No module named 'fcp'`
- `P_018_01_PACKAGING_STATUS: PACKAGING_GAP_REQUIRING_HUMAN_DECISION`

Repository presence was not treated as artifact presence. The negative import
result is mechanical evidence from the installed wheel with no working-tree import
path.

## O. P1-R17 evaluation

ENV-002D established Python 3.13 smoke, dedicated tests, protected API, and four
full-suite failures. VAL-003 established that those four failures reproduce on the
clean baseline, identified a fifth clean-reference packaging-artifact-dependent
failure, and established zero P-018-01 regressions. VAL-004 successfully built,
installed, and replayed the current wheel, preserving SDK/API/fingerprint.

However, the wheel does not contain P-018-01 and the installed artifact cannot
import it. This is a packaging gap requiring a human architectural/release decision.

- `P1_R17_STATUS: BLOCKED`
- `P_018_01_VALIDATION_STATUS: BLOCKED — PACKAGING DECISION REQUIRED`
- `READY_FOR_GIT_CONSOLIDATION: NO`

Decision required: determine whether `external/fcp` is intentionally a
repository-only, non-distributable foundation, or authorize a separately scoped
packaging/architecture change that makes P-018-01 consumable from a built artifact
without violating the external-to-Core boundary. This operation chooses neither.

## P. Pre-existing baseline technical debt

The following are recorded separately as
`PRE_EXISTING_BASELINE_TECHNICAL_DEBT` and are not attributed to P-018-01:

1. `test_official_version_is_consistent`: tracked clean reference lacks the
   untracked `src/cko.egg-info/PKG-INFO` artifact expected by the test.
2. `test_collect_metadata`: `collect_metadata()` does not accept the test's
   `calculate_hash` keyword.
3. `test_existing_table_is_preserved`: Windows `PermissionError [WinError 32]`
   while deleting an open temporary SQLite file.
4. `test_environment_validation_covers_all_requirements`: encoding validation
   rejects the observed `cp1252` condition.
5. `test_cli_validation_uses_installed_python_and_powershell`: the same encoding
   condition causes CLI validation exit `1`.

`BASELINE_TECHNICAL_DEBT_PRESENT: YES`

None was fixed, suppressed, reclassified as permanently acceptable, or assigned
to P-018-01. A future independent operation should own remediation, regression
proof, and review for these five items.

## Q. Final working tree

The temporary build and virtual-environment artifacts were created outside the
repository and removed after evidence collection. Staging remains empty. No code,
test, Core, packaging, requirement, external/FCP, Git ref, or pre-existing artifact
was modified. This VAL-004 report is the only repository change from this operation.
No add, commit, push, reset, clean, checkout, merge, rebase, or tag operation was
performed.

## R. Recommendation

Submit the packaging status to the competent human architecture/release authority.
Do not consolidate P-018-01 until that authority explicitly chooses repository-only
scope or authorizes a separately validated packaging design. Independently schedule
the five baseline failures for technical-debt remediation. Do not begin P-018-02.

## Required results

`WHEEL_BUILD: PASS`  
`WHEEL_NAME: cko-1.0.0-py3-none-any.whl`  
`WHEEL_SHA256: 8e2c7cf609855a9f88779bfbef4d9cc16c542e00c6468dfe143887928d12a650`  
`WHEEL_INSTALL: PASS`  
`PIP_CHECK: PASS`  
`ISOLATED_CKO_IMPORT: PASS`  
`ISOLATED_CKO_CORE_IMPORT: PASS`  
`SDK_VERSION: 1.0.0`  
`PUBLIC_API_COUNTS: 646 / 646 / 646`  
`PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`  
`FCP_INCLUDED_IN_WHEEL: NO`  
`P_018_01_IMPORTABLE_FROM_INSTALLED_ARTIFACT: NO`  
`PACKAGING_CHANGE_REQUIRED: YES — HUMAN DECISION REQUIRED`  
`P_018_01_NEW_REGRESSIONS: 0`  
`BASELINE_TECHNICAL_DEBT_PRESENT: YES`  
`P1_R17_STATUS: BLOCKED`  
`P_018_01_VALIDATION_STATUS: BLOCKED — PACKAGING DECISION REQUIRED`  
`READY_FOR_GIT_CONSOLIDATION: NO`  
`PUBLIC_API_IMPACT: NONE`  
`BREAKING_CHANGE: NO`  
`P_018_02_AUTHORIZED: NO`

## S. Canonical SHA-256

`CANONICAL_SHA256: a48a5ac699ee41ecd78a8ca1a4df22c18f6c11792bf83e39d64f471c99d0a4fe`

Convention: SHA-256 of the complete UTF-8 file after replacing the embedded
digest with `<SHA256>` and normalizing line endings to LF.

## Verdict

`VAL-004 BLOCKED — P-018-01 PACKAGING DECISION REQUIRED`
