# CKO — SPR-018 — P-018-01 ADR-007 Packaging Implementation Report

**Date:** 2026-08-13  
**Scope:** ADR-007 ratification and P-018-01 packaging only  
**Verdict:** `ADR-007 IMPLEMENTED — P1-R17 SATISFIED — P-018-01 READY FOR CONTROLLED CONSOLIDATION`

## A. ADR-007 ratification

The competent human instruction ratified **ADR-007 — FCP Distribution and
Packaging Architecture**. The document's canonical hash convention was replayed
(substitute the embedded digest with `<SHA256>`, normalize line endings to LF,
then SHA-256 the UTF-8 bytes) and produced:

`e73c2f51c609a239aecb029a65bb01f3d4d10b6961fef909f76e2509f238cca2`

`ADR_007_STATUS: RATIFIED`

## B. Files moved

The seven production modules were moved without logical contract, schema,
serialization, lifecycle, or semantic-error changes:

- `external/fcp/__init__.py` → `packages/cko-fcp/src/cko_fcp/__init__.py`
- `external/fcp/_validation.py` → `packages/cko-fcp/src/cko_fcp/_validation.py`
- `external/fcp/contracts.py` → `packages/cko-fcp/src/cko_fcp/contracts.py`
- `external/fcp/errors.py` → `packages/cko-fcp/src/cko_fcp/errors.py`
- `external/fcp/lifecycle.py` → `packages/cko-fcp/src/cko_fcp/lifecycle.py`
- `external/fcp/models.py` → `packages/cko-fcp/src/cko_fcp/models.py`
- `external/fcp/serialization.py` → `packages/cko-fcp/src/cko_fcp/serialization.py`

The existing test module, package marker, and two JSON fixtures were moved from
`tests/fcp/` to `packages/cko-fcp/tests/`.

## C. Files created

- `packages/cko-fcp/pyproject.toml`
- `packages/cko-fcp/README.md`
- `packages/cko-fcp/tests/test_packaging.py`
- this report

The final FCP wheel is retained at
`packages/cko-fcp/dist/cko_fcp-0.1.0-py3-none-any.whl`. Intermediate
`build/`, `cko_fcp.egg-info/`, and cache directories were removed.

## D. Imports altered

Only the migrated tests changed absolute imports:

- `external.fcp` → `cko_fcp`
- `external.fcp._validation` → `cko_fcp._validation`

Production modules retain their existing relative imports. No alias named
`fcp`, `external.fcp`, or `cko.fcp` was created.

## E. Distribution and versioning

- Distribution: `cko-fcp`
- Canonical import namespace: `cko_fcp`
- `DISTRIBUTION_VERSION: 0.1.0`
- Python: `>=3.13`
- Backend: `setuptools.build_meta`
- Discovery: distribution-local `src` only, include `cko_fcp*`
- Runtime dependencies: none

No earlier binding initial distribution version was found. Therefore the
human-authorized candidate `0.1.0` was selected. Distribution SemVer is
independent from protocol compatibility. Protocol compatibility continues to be
represented and negotiated by the unchanged `FCPVersion` contract.

## F. Tests

Python `3.13.15`:

- Existing dedicated P-018-01 tests: **22 passed**
- New packaging/isolation tests: **8 passed**
- Combined pytest replay: **30 passed in 0.66 s**
- FCP-only unittest replay: **30 passed**
- `pip check`: passed in build, FCP-only, and dual environments
- deterministic serialization: passed, including golden fixture and 100 repeats
- no I/O/network/database/Core import: passed
- no credentials/P-018-02 modules: passed

## G. cko-fcp wheel

- Name: `cko_fcp-0.1.0-py3-none-any.whl`
- Version: `0.1.0`
- Size: `9,779 bytes`
- Entries: 11

Content listing:

1. `cko_fcp/__init__.py`
2. `cko_fcp/_validation.py`
3. `cko_fcp/contracts.py`
4. `cko_fcp/errors.py`
5. `cko_fcp/lifecycle.py`
6. `cko_fcp/models.py`
7. `cko_fcp/serialization.py`
8. `cko_fcp-0.1.0.dist-info/METADATA`
9. `cko_fcp-0.1.0.dist-info/WHEEL`
10. `cko_fcp-0.1.0.dist-info/top_level.txt`
11. `cko_fcp-0.1.0.dist-info/RECORD`

No tests, fixtures, reports, `external`, `src/cko`, caches, egg-info source
directories, credentials, or local artifacts are present.

## H. SHA-256

`FCP_WHEEL_SHA256: 78c58f872b214d91e65a34045abcea57e633188ce1422457e78a6269235021dc`

The separately built current `cko-1.0.0-py3-none-any.whl` was produced only in
a temporary directory:

- size: `438,680 bytes`
- SHA-256: `b3c1e6240a0fd097313f7d703f4ae1fbfc009114178c3f981e20da13cda86906`
- entries: 280
- Python files under `cko/`: 276
- FCP entries: 0

The pre-existing repository wheel at `runtime/reports/build/` was inspected
but rejected as final evidence because it is stale (610 exports). It was not
changed. The freshly built wheel matches the protected current source API.

## I. Isolated install

A fresh Python 3.13 virtual environment received only the FCP wheel with
`--no-deps`. Isolated `-I` import resolved from `site-packages`;
distribution metadata reported `cko-fcp 0.1.0`, no `Requires-Dist`, and
`pip check` passed. All 30 applicable unittest cases passed.

`FCP_ONLY_INSTALL: PASS`

## J. Dual install

A separate Python 3.13 environment received the freshly built canonical
`cko 1.0.0` wheel and the `cko-fcp 0.1.0` wheel. Isolated imports of `cko`,
`cko.core`, and `cko_fcp` resolved from `site-packages`. `fcp` and
`external` specs were absent. `pip check` passed.

`DUAL_INSTALL: PASS`

## K. SDK, API, and fingerprint

Source-layout and installed-wheel checks agree:

- `SDK_VERSION: 1.0.0`
- `PUBLIC_API_COUNTS: 646 / 646 / 646`
- `PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`
- `PUBLIC_API_IMPACT: NONE`
- `BREAKING_CHANGE: NO`

No file under `src/cko/`, no `cko.core.__all__` entry, and no root packaging
metadata was changed.

## L. Dependencies

`cko-fcp` declares no runtime dependencies and does not import `cko`.
The root `cko` project does not declare or import `cko-fcp`. Both dependency
directions are absent.

## M. Security

AST/import and wheel-content checks confirm no network, database, subprocess,
filesystem I/O capability, credentials, or external service dependency in the
P-018-01 distribution. Runtime validation remained pure and read-only. No
P-018-02 authority, publication service, query service, or real-source function
was introduced.

## N. P1-R17 incremental replay

The authorized incremental replay covered the 22 original tests, eight packaging
tests, namespace/import isolation, wheel content, FCP-only installation, dual
installation, protected API/fingerprint, dependency direction, no-I/O, and
no-P-018-02 checks.

`P_018_01_NEW_REGRESSIONS: 0`

`P1_R17_INCREMENTAL_STATUS: SATISFIED`

The full repository regression was intentionally not repeated. VAL-003 remains
the controlling evidence that the five known failures are pre-existing baseline
technical debt.

## O. Rollback

Rollback was demonstrated as a bounded file-operation plan and was not executed
because validation passed:

1. remove only `packages/cko-fcp/` and withdraw its wheel;
2. restore the seven production files to `external/fcp/`;
3. restore the original test module/package marker/fixtures to `tests/fcp/`;
4. reverse only the two test import substitutions;
5. rerun the 22 dedicated tests and protected API/fingerprint check.

No rollback step touches `pyproject.toml`, `src/cko/`, `cko.core`, the SDK
wheel, the 646 exports, or the canonical baseline.

## P. Baseline debt preserved

The five known global failures remain classified as
`PRE_EXISTING_BASELINE_TECHNICAL_DEBT`. No P-018-01 code or packaging change
masks or remediates them.

## Q. Git status final

No `git add`, commit, push, pull, reset, clean, rebase, merge, or tag was run.
The repository already contained multiple unrelated untracked files before this
operation; they were preserved. This operation contributes the new untracked
`packages/cko-fcp/` tree and this report. The protected tracked diff for root
`pyproject.toml` and `src/cko/` is empty.

## R. Decision

`ADR_007_STATUS: RATIFIED`  
`DISTRIBUTION: cko-fcp`  
`IMPORT_NAMESPACE: cko_fcp`  
`DISTRIBUTION_VERSION: 0.1.0`  
`PROTOCOL_VERSION_POLICY: SEPARATE FCP PROTOCOL COMPATIBILITY VERSION`  
`DEDICATED_TESTS: 22 PASSED`  
`PACKAGING_TESTS: 8 PASSED`  
`FCP_WHEEL_BUILD: PASS`  
`FCP_WHEEL_SHA256: 78c58f872b214d91e65a34045abcea57e633188ce1422457e78a6269235021dc`  
`FCP_ONLY_INSTALL: PASS`  
`DUAL_INSTALL: PASS`  
`SDK_VERSION: 1.0.0`  
`PUBLIC_API_COUNTS: 646 / 646 / 646`  
`PUBLIC_API_FINGERPRINT: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`  
`PUBLIC_API_IMPACT: NONE`  
`BREAKING_CHANGE: NO`  
`P_018_01_NEW_REGRESSIONS: 0`  
`P1_R17_INCREMENTAL_STATUS: SATISFIED`  
`READY_FOR_GIT_CONSOLIDATION: YES — PENDING HUMAN REVIEW`  
`P_018_02_AUTHORIZED: NO`

`ADR-007 IMPLEMENTED — P1-R17 SATISFIED — P-018-01 READY FOR CONTROLLED CONSOLIDATION`
