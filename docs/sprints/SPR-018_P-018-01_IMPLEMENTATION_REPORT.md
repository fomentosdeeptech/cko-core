# CKO — SPR-018 — P-018-01 Implementation Report

**Date:** 2026-08-12  
**Authorization:** REV-003 `AUTHORIZED_FOR_IMPLEMENTATION`  
**Verdict:** `P-018-01 IMPLEMENTED WITH BLOCKERS — NOT READY FOR CONSOLIDATION`

## Scope and architecture

Only P-018-01 was implemented: immutable logical values, qualified source
identity, catalog record, four orthogonal state axes, strict invariants,
lifecycle validation, abstract version/capability negotiation, semantic errors,
canonical serialization, and synthetic fixtures. `external/fcp/` is outside
`src/`, performs no I/O, has no Core import, and is excluded from setuptools.
There is no transport, persistence, IAM, source access, publication authority,
real data, SDK export, or implementation of P-018-02–05.

## Repository and authority

- Branch: `main`.
- HEAD, local `origin/main`, remote main: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`.
- Annotated tag object: `ffa9cd23909c01e13cbc9926048dc69e12ff11fc`.
- Peeled baseline: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`.
- REV-003 explicitly authorizes P-018-01 only.
- Initial unrelated untracked files were preserved.

## Artifacts and contracts

Created seven modules under `external/fcp/`, two synthetic JSON fixtures and the
test suite under `tests/fcp/`, plus this report. No pre-existing file was modified.
No file in `src/cko`, packaging, dependencies/build metadata, egg-info, Git config,
tag, or baseline was modified.

The package implements strict non-coercive validation; opaque identity
preservation; required/unique canonically ordered references; four independent
state axes; minimum trust, publication, and stewardship invariants; single-axis
successor transitions; read-only envelopes and bounded page schema;
compatible-major/minor and capability intersection; safe/refused downgrade;
typed semantic errors; canonical UTF-8 JSON and SHA-256 independent of locale,
clock, environment, filesystem, random, hostname, PID, timezone, and map order.

## Tests and regression

The dedicated standard-library suite produced **22 total, 22 passed, 0 failed,
0 skipped, 0 xfail, 0.109 s**. It covers valid/invalid schemas, identity,
cardinality, immutability, four axes, invariants, transitions, envelope/page,
negotiation/downgrade, errors, golden JSON, repeated determinism, AST dependency
direction, and no-I/O behavior. `compileall` passed.

Before and after: SDK `1.0.0`; **646 exports, 646 unique names, 646 resolved**;
ordered API fingerprint SHA-256
`d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`.
Protected tracked diff: none. Core-to-FCP and FCP-to-Core imports: none. Package
discovery remains `where=["src"]`.

`PUBLIC_API_IMPACT: NONE`  
`BREAKING_CHANGE: NO`

Only the standard library is used. Local AST and pattern scans found no I/O,
network, database, HTTP, subprocess, credential value, URL, private key, password,
or personal data. `version_token` matches were reviewed as schema-field names.

## Gates, limitations, rollback, and pending work

P1-R0–R16 and P1-R18–R20 pass. P1-R17 is blocked because the available workspace
runner is Python 3.12.13 without pytest: the repository-wide pytest suite, approved
Python 3.13 replay, and isolated built-wheel replay could not be executed. No
dependency was installed or added to bypass that limitation. Thus consolidation
readiness cannot be declared.

Intentional boundaries: no operational defaults, real authority/policy execution,
source integration, publication/query orchestration, lifecycle Provenance mapping,
or D5 dossier. Rollback is removal of `external/fcp`, `tests/fcp`, and this report,
followed by the 646/646/646 check. No staging, commit, push, pull, reset, checkout,
clean, rebase, or tag operation was performed.

## SHA-256

| SHA-256 | Artifact |
|---|---|
| `2f721d42f33a7610ec71886dd0aeb22c8e5dde94e507036ca9cdfc3cc5d98c82` | `external/fcp/__init__.py` |
| `14d001d5d19de2666ad1c9d3c0782b77151fac2b19aa72e0456e2e8f15bed3eb` | `external/fcp/_validation.py` |
| `367e952f71addda17c3c976127c33c4fc151d75c58249412f1758f53fc8abcd2` | `external/fcp/contracts.py` |
| `096891ca194d84527055fe15d66fd359b1934228abb17ca3cd0bee4463c60644` | `external/fcp/errors.py` |
| `e4171980062c366063ea0dc65c4b7d78f283230230f1fd55c8391163a19aacbc` | `external/fcp/lifecycle.py` |
| `176b80d51bb37860dd0b3dcb25af5f258a2a06bacdd4cf32a264b7cd7a7d24f1` | `external/fcp/models.py` |
| `d13ddb7329d3e9150312d7a53bc6d59716831e71f49a36912b1e6d65ab2302a2` | `external/fcp/serialization.py` |
| `61897ec8c1a0cfd622ba525f14df75eecd0308d8c6468873df15f26553936840` | `tests/fcp/__init__.py` |
| `e337f5dee0c13514736a0731becaaf9386593639127d109e84c08663697b70aa` | `tests/fcp/fixtures/invalid_vectors.json` |
| `b9393465eade23a55056a42ebafaed9c386844c273390ccbc205561976251527` | `tests/fcp/fixtures/valid_record.json` |
| `e9f6fe4eeb899e8dde80de71e77fa7eded2d92b4991f0eb567cf0fbdf6bc54f6` | `tests/fcp/test_foundation.py` |

The report excludes its own self-referential digest.
