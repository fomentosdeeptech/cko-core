# CKO — ADR-007 — FCP Distribution and Packaging Architecture

**Date:** 2026-08-13  
**Status:** `PROPOSED — READY FOR HUMAN RATIFICATION`  
**Scope:** P-018-01 distribution architecture only  
**Verdict:** `ADR-007 READY FOR HUMAN RATIFICATION — FCP PACKAGING ARCHITECTURE DEFINED`

## A. Context

RFC-002 defines the Federated Catalog Protocol as a logical, external protocol
whose implementations must remain independent of `cko.core`. REV-003 authorized
only the pure P-018-01 foundation. That implementation exists under
`external/fcp/`, uses only the Python standard library, introduces no Core import,
and has 22 dedicated passing tests.

VAL-003 established zero P-018-01 regressions. VAL-004 built and installed the
current `cko` wheel successfully and preserved SDK `1.0.0`, API `646 / 646 / 646`,
and fingerprint
`d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`.
It also proved mechanically that `external/fcp` is absent from that wheel and is
not importable from the installed artifact. P1-R17 is therefore blocked on a
human packaging decision.

The human direction for this ADR is binding: P-018-01 must not remain
repository-only; it must become consumable as an installed artifact while staying
external to Core. This ADR selects an architecture but does not implement it.

## B. Problem

The repository currently has one Python distribution, `cko`, discovered only
under `src`. P-018-01 is physically outside that discovery root. Simply making the
current wheel include the existing directory would solve file presence but would
not, by itself, establish a clear public namespace, ownership boundary,
versioning policy, or independent release path.

The decision must distinguish three concepts:

1. the canonical public API of `cko.core`, measured by its 646 ordered exports;
2. Python import namespace and package discovery;
3. installable distribution identity and release lifecycle.

Conflating these concepts would either couple FCP to Core or create an ambiguous
package that is difficult to evolve safely.

## C. Architectural forces

- `cko.core` must remain neutral and must not import or re-export FCP.
- RFC-002 defines protocol contracts, not new Core SDK contracts.
- SDK `cko` must remain `1.0.0`; `cko.core.__all__` must remain unchanged.
- FCP requires an explicit, collision-resistant import namespace.
- Installed-artifact validation must not depend on the repository working tree.
- The protocol needs an independent compatibility and release cadence.
- P-018-01 currently has no runtime dependency outside the standard library.
- Packaging must not accidentally include tests, fixtures, reports, caches, or
  unrelated content.
- A future split to a separate repository should not force consumers to change
  imports or distribution identity.
- Rollback must not require rolling back the Core SDK.
- P-018-02 through P-018-05 remain unauthorized.
- The five baseline failures remain unrelated technical debt.

## D. Alternatives

### A — top-level `fcp` inside the existing `cko` wheel

This is mechanically small but gives a generic top-level name to one project while
the installed distribution is named `cko`. It couples FCP delivery and versioning
to every `cko` release, increases namespace-collision and dependency-confusion
risk, and makes later separation require coordination around ownership of the same
import package. It preserves the Core export list only if no re-export is added.

### B — `cko.fcp` inside the existing `cko` wheel

This provides a clear CKO-qualified import and can preserve `cko.core.__all__` if
`cko.core` and root initializers do not re-export it. However, being inside the
`cko` distribution and namespace communicates product-family ownership more
strongly than architectural independence. It couples releases to SDK `1.0.0` and
makes later extraction into a separate distribution sharing the `cko` namespace
operationally delicate, especially across installers and independently owned
package fragments.

### C — independent FCP distribution

This gives FCP its own dependency graph, version, wheel, release, rollback, and
future repository. Its quality depends on choosing a non-generic, stable import
namespace and a clear monorepo layout. A bare `fcp` namespace is not required by
this alternative and is rejected for collision reasons.

### D — retain `external/fcp` and explicitly include it in the `cko` wheel

Setuptools can be configured with additional package mappings or explicit package
lists, but mixing sources outside the configured `src` root creates exceptional
discovery rules. The physical path remains repository-centric, the distribution
is still coupled to `cko`, and the mapping between source path, import name, and
wheel ownership becomes less obvious. This is the smallest textual packaging
change but not the smallest long-term architectural change.

### E — independent `cko-fcp` distribution with `cko_fcp` namespace

This is a constrained form of C and the recommended architecture. The distribution
is `cko-fcp`; its Python namespace is `cko_fcp`; its project lives at
`packages/cko-fcp/` with a conventional `src/cko_fcp/` layout. The underscore
namespace is valid, explicit, collision-resistant, and separate from both
`cko.core` and the shared `cko` namespace. The distribution can remain in this
monorepo initially and move to another repository later without changing either
its install name or import path.

## E. Comparative matrix

Scores use `5` as strongest and `1` as weakest. A low implementation-size score
means more immediate file changes; it is not a quality defect by itself.

| Criterion | A: `fcp` in `cko` | B: `cko.fcp` in `cko` | C: independent, unspecified namespace | D: map `external/fcp` into `cko` | E: `cko-fcp` / `cko_fcp` |
|---|---:|---:|---:|---:|---:|
| Core isolation | 4 | 4 | 5 | 4 | 5 |
| RFC-002 compatibility | 3 | 4 | 5 | 3 | 5 |
| Preserve SDK/API/fingerprint | 4 | 4 | 5 | 4 | 5 |
| Namespace clarity | 2 | 4 | 3 | 2 | 5 |
| Discovery simplicity | 4 | 5 | 4 | 2 | 5 |
| pip/wheel clarity | 3 | 4 | 5 | 2 | 5 |
| Testability | 4 | 4 | 5 | 3 | 5 |
| Independent versioning | 1 | 1 | 5 | 1 | 5 |
| Future independent distribution | 2 | 3 | 5 | 2 | 5 |
| Dependency isolation | 2 | 2 | 5 | 2 | 5 |
| Security/namespace collision | 2 | 4 | 3 | 2 | 5 |
| Maintenance/rollback | 2 | 3 | 5 | 2 | 5 |
| Future migration | 2 | 3 | 5 | 2 | 5 |
| Immediate implementation size | 4 | 4 | 3 | 5 | 3 |
| **Total / 70** | **39** | **49** | **63** | **38** | **68** |

Alternative E is superior because it resolves the unspecified-namespace weakness
of C while retaining distribution independence. Its modestly larger initial move
eliminates a later consumer migration and avoids exceptional packaging rules.

## F. Recommended decision

Adopt an independently installable Python distribution named `cko-fcp`, exposing
only the top-level Python package `cko_fcp`, initially maintained in this monorepo
as a self-contained project under `packages/cko-fcp/`.

The FCP distribution is part of the CKO ecosystem but is not part of `cko.core`,
not a `cko.core` export, and not transitively installed by `cko` unless a future
separate human decision explicitly introduces an optional integration dependency.

Required decision fields:

- `TARGET_NAMESPACE: cko_fcp`
- `TARGET_DISTRIBUTION: cko-fcp`
- `TARGET_REPOSITORY_LOCATION: packages/cko-fcp/src/cko_fcp/`
- `VERSIONING_POLICY: INDEPENDENT SEMANTIC DISTRIBUTION VERSION PLUS EXPLICIT FCP PROTOCOL COMPATIBILITY VERSION`
- `PACKAGE_DISCOVERY_POLICY: DISTRIBUTION-LOCAL SRC LAYOUT; DISCOVER ONLY packages/cko-fcp/src`
- `PUBLIC_API_POLICY: NO IMPORT OR RE-EXPORT FROM cko OR cko.core; PROTECT cko.core.__all__ AND ITS FINGERPRINT`
- `DEPENDENCY_POLICY: STANDARD LIBRARY ONLY FOR P-018-01; NO cko DEPENDENCY; FUTURE DEPENDENCIES EXPLICIT, MINIMAL, AUDITED, AND PACKAGE-LOCAL`
- `TEST_POLICY: DISTRIBUTION-LOCAL CONTRACT TESTS PLUS REPOSITORY BOUNDARY AND DUAL-INSTALL TESTS`
- `WHEEL_VALIDATION_POLICY: BUILD, INSPECT, INSTALL, pip check, IMPORT, CONTRACT REPLAY, API NON-REGRESSION, AND WORKING-TREE ISOLATION`
- `ROLLBACK_POLICY: WITHDRAW/REMOVE cko-fcp ARTIFACT OR REVERT ONLY THE FCP PACKAGING CHANGE; cko WHEEL REMAINS UNCHANGED`
- `FUTURE_SEPARATION_POLICY: PRESERVE DISTRIBUTION NAME, IMPORT NAMESPACE, VERSION CONTRACT, TEST VECTORS, AND RELEASE METADATA WHEN MOVING REPOSITORIES`

## G. Justification

The protocol is external by responsibility, dependency direction, release
authority, and lifecycle—not by the spelling of a repository directory. A
distribution boundary is stronger and more enforceable than placing a second
package inside the Core SDK wheel.

`cko_fcp` makes ecosystem affiliation explicit without claiming membership in the
`cko.core` API. It avoids the generic `fcp` name and the shared-namespace concerns
of independently distributing `cko.fcp`. An independent wheel ensures that FCP
can change only when its own compatibility policy permits, while Core consumers
receive no new code or dependency unless they explicitly install `cko-fcp`.

This design has a slightly larger one-time implementation than editing the root
package discovery, but it is the smallest change that satisfies all long-term
forces without planting a known migration obligation.

## H. Namespace

The canonical import is:

```python
import cko_fcp
from cko_fcp.models import CatalogRecord
```

The names `fcp`, `external.fcp`, and `cko.fcp` are not public aliases. Adding
aliases would create multiple canonical identities, complicate deprecation, and
increase collision risk. P-018-01 symbols may be exported by `cko_fcp.__all__`
under a distribution-local API policy, but they must never be appended to
`cko.core.__all__` or rebound through `cko`/`cko.core`.

## I. Distribution

`cko-fcp` is installed explicitly, for example by a future validated command
equivalent to `pip install cko-fcp`. It produces its own wheel and metadata. The
root `cko` project does not declare `cko-fcp` as a mandatory dependency, and
`cko-fcp` does not depend on `cko` for P-018-01.

Distribution-name normalization by Python tooling may display `cko_fcp` in some
metadata contexts; the declared project name remains `cko-fcp`, while the import
package remains `cko_fcp`.

## J. Physical repository location

Architectural location and physical location are separate:

- architectural location: external protocol foundation outside Core;
- initial physical location: `packages/cko-fcp/src/cko_fcp/` in the current
  monorepo;
- test location: `packages/cko-fcp/tests/`;
- project metadata: `packages/cko-fcp/pyproject.toml`.

The current `external/fcp/` location should not remain after implementation. It
was appropriate for proving isolation before a distribution decision, but a
conventional distribution-local `src` layout is clearer, gives deterministic
discovery, and makes the package independently buildable. Moving the files is an
implementation action and is not performed by this ADR.

## K. Versioning

FCP must have an independent distribution version governed by Semantic
Versioning. It must not necessarily equal SDK `cko` version `1.0.0`.

Two versions serve different purposes and must remain explicit:

1. **distribution version** — release identity of `cko-fcp`, used by package
   management and changed under SemVer;
2. **protocol compatibility version** — the logical FCP version negotiated by
   P-018-01 contracts.

A package release may change without changing protocol compatibility, and a
future protocol-major change requires an explicit compatibility decision. The
initial distribution version is a human release decision for implementation and
is not assigned or changed here.

## L. Public API

The protected fingerprint measures ordered symbols in `cko.core.__all__`, not all
importable packages installed in an environment. An independent `cko_fcp` package
can therefore be importable without changing the canonical Core API, provided the
implementation obeys all of these mechanical constraints:

- no edit to `src/cko/`;
- no import of `cko_fcp` from `cko` or `cko.core`;
- no addition to `cko.core.__all__`;
- no root-level re-export or lazy binding;
- no `cko` dependency from `cko-fcp` for P-018-01;
- fingerprint recalculation from both the source layout and installed `cko` wheel.

Expected result: SDK `1.0.0`, counts `646 / 646 / 646`, fingerprint
`d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`,
`PUBLIC_API_IMPACT: NONE`, and `BREAKING_CHANGE_REQUIRED: NO`.

`cko_fcp` has its own public package surface. That surface is not part of the 646
Core exports and must be versioned under the FCP distribution policy.

## M. Packaging

The future FCP project should use PEP 517 with an explicit build backend and
distribution-local discovery rooted only at `packages/cko-fcp/src`. The build
configuration must explicitly exclude tests, fixtures not required at runtime,
reports, caches, generated metadata, and the repository's root `src/cko` tree.

The root `pyproject.toml` should remain unchanged unless repository-wide tooling
later requires explicit workspace metadata. Such workspace convenience is not a
prerequisite for packaging and must not couple the two distributions.

No editable install, `PYTHONPATH`, current-working-directory import, or source-tree
fallback may count as artifact validation.

## N. Tests

Implementation requires:

1. move/update the existing 22 P-018-01 tests to import `cko_fcp` and preserve all
   positive, negative, invariant, lifecycle, negotiation, serialization,
   dependency-direction, and no-I/O assertions;
2. source-layout tests for the new package;
3. wheel content allow-list and RECORD verification;
4. isolated `cko-fcp`-only installation, `pip check`, import, and all P-018-01
   contract tests against installed code;
5. dual isolated installation of canonical `cko` and new `cko-fcp`, proving both
   imports and absence of namespace shadowing;
6. AST/dependency checks proving neither package imports the other and FCP remains
   standard-library-only for P-018-01;
7. source and installed-wheel checks of SDK version, `646 / 646 / 646`, and the
   protected fingerprint;
8. checks that `cko-fcp` contains no P-018-02 functionality, real data, I/O,
   network, persistence, IAM, credentials, or publication authority;
9. deterministic clean-environment replay and rollback/uninstall verification.

The five baseline failures remain `PRE_EXISTING_BASELINE_TECHNICAL_DEBT`; they are
not corrected or used to weaken these tests.

## O. Security

An independent, qualified namespace reduces collision and dependency-confusion
risk compared with `fcp`. Release control must reserve and govern the distribution
name before any public publication. Builds should use locked or controlled build
requirements, produce reproducible evidence, inspect wheel contents, and verify
hashes before installation.

P-018-01 must retain zero I/O and no credentials. Distribution independence does
not authorize network access, data access, publication, trust decisions, or any
P-018-02 behavior. Future dependencies require separate review for provenance,
licenses, vulnerabilities, transitive scope, and necessity.

## P. Rollback

Before consolidation, rollback is removal of the new FCP project and restoration
of the current `external/fcp` and `tests/fcp` paths, followed by the existing
P-018-01 and API checks. After a released artifact, rollback is an FCP-only release
withdrawal/yank or corrected FCP release according to repository policy; the
canonical `cko` artifact does not need rollback because it was not changed.

Every rollback replay must prove that `cko` remains importable with SDK `1.0.0`,
API `646 / 646 / 646`, and the authorized fingerprint. No destructive Git action
is implied by this policy.

## Q. Future evolution

The monorepo location is an operational convenience, not an ownership commitment.
If governance later separates repositories, the following remain stable:

- distribution name `cko-fcp`;
- import namespace `cko_fcp`;
- protocol compatibility semantics;
- distribution version history;
- canonical test vectors and serialization;
- release provenance and wheel validation requirements.

Future optional adapters or integrations should be separate packages or explicitly
reviewed extras rather than expanding the P-018-01 base dependency graph. A future
decision may define an application composition package; it must not make Core
depend on FCP.

## R. Impact on P1-R17

Implementation of the ratified ADR-007 is a precondition for concluding P1-R17,
because VAL-004 proved the current artifact does not expose P-018-01.

A packaging-focused incremental replay is sufficient; repeating the entire
repository regression is not required solely by this ADR because VAL-003 already
proved zero differential regressions and the human decision isolated the five
baseline failures. The replay must nevertheless include:

- all 22 dedicated P-018-01 tests after namespace migration;
- build and mechanical inspection of the `cko-fcp` wheel;
- isolated FCP-only and dual-wheel installation;
- `pip check`;
- installed `import cko_fcp` and negative source-tree fallback proof;
- P-018-01 contract/serialization replay from the installed artifact;
- canonical `cko` source and wheel SDK/API/fingerprint verification;
- dependency-direction, no-I/O, no-P-018-02, and working-tree checks;
- wheel and report SHA-256 evidence.

If implementation changes any protected surface, dependency direction, P-018-01
behavior, or evidence assumption beyond packaging/namespace migration, the scope
is no longer incremental and a competent authority must require broader replay.
This ADR does not change the current `P1_R17_STATUS: BLOCKED`.

## S. Relationship with P-018-02

`P_018_02_AUTHORIZED: NO`.

The selected package boundary creates no authority to implement sources, I/O,
network, persistence, IAM, credentials, publication, real data, operational
integration, or any P-018-02 through P-018-05 behavior. Package existence is not
protocol-package authorization. Any later package must satisfy its own REV-003
conditions and human gate.

## T. Implementation plan — not executed

The smallest implementation that fully realizes this architecture is:

1. **Create** `packages/cko-fcp/pyproject.toml` with project name `cko-fcp`, Python
   requirement compatible with the approved runtime, an explicit PEP 517 backend,
   no runtime dependencies for P-018-01, and discovery rooted at `src`.
2. **Create** `packages/cko-fcp/README.md` containing distribution scope,
   architectural boundary, install/import names, version distinction, and the
   prohibition on P-018-02 behavior. Include it in distribution metadata only if
   the chosen metadata references it.
3. **Create directories and move**, preserving behavior and history where Git is
   later used:
   - `external/fcp/__init__.py` → `packages/cko-fcp/src/cko_fcp/__init__.py`
   - `external/fcp/_validation.py` → `packages/cko-fcp/src/cko_fcp/_validation.py`
   - `external/fcp/contracts.py` → `packages/cko-fcp/src/cko_fcp/contracts.py`
   - `external/fcp/errors.py` → `packages/cko-fcp/src/cko_fcp/errors.py`
   - `external/fcp/lifecycle.py` → `packages/cko-fcp/src/cko_fcp/lifecycle.py`
   - `external/fcp/models.py` → `packages/cko-fcp/src/cko_fcp/models.py`
   - `external/fcp/serialization.py` → `packages/cko-fcp/src/cko_fcp/serialization.py`
4. **Modify only imports required by the namespace move** within those seven
   modules, without changing contracts or behavior.
5. **Move** `tests/fcp/test_foundation.py` to
   `packages/cko-fcp/tests/test_foundation.py` and move its two JSON fixtures to
   `packages/cko-fcp/tests/fixtures/`; modify imports from the repository namespace
   to `cko_fcp`. Remove or relocate `tests/fcp/__init__.py` only as part of that
   controlled move.
6. **Create** distribution-boundary tests, wheel allow-list inspection, installed
   artifact replay, dual-install checks, API fingerprint checks, and negative
   import-path checks. Prefer a repository-level validation script only if it is
   required to orchestrate both independent projects; otherwise keep validation
   under `packages/cko-fcp/tests/`.
7. **Do not modify** root `pyproject.toml`, `src/cko`, `cko.core.__all__`, SDK
   version, requirements, or Core tests unless a later ratified implementation
   review demonstrates an unavoidable tooling need. Any such need reopens the
   decision before implementation.
8. Build the FCP wheel from `packages/cko-fcp/` using only its packaging metadata;
   record name, version, size, SHA-256, command, backend, and exit code.
9. Inspect every wheel entry. Require `cko_fcp` modules and distribution metadata;
   reject `cko`, tests, fixtures not explicitly runtime-required, `external`,
   caches, reports, credentials, or unexpected files.
10. Create fresh Python 3.13 environments outside the working tree: one with only
    `cko-fcp`, and one with canonical `cko` plus `cko-fcp`. Do not use `PYTHONPATH`.
    Install the built wheels, run `pip check`, imports, contract replay, and
    dependency checks.
11. Recalculate the protected SDK/API/fingerprint from canonical `cko` source and
    installed wheel. Require exact `1.0.0`, `646 / 646 / 646`, and
    `d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`.
12. Validate rollback by removing the FCP artifact/environment and proving the
    canonical `cko` wheel remains intact. Remove temporary artifacts after evidence
    collection.
13. Produce a separately authorized implementation and P1-R17 replay report. Do
    not stage, commit, push, publish, or start P-018-02 without the corresponding
    human authorization.

No implementation step in this section was executed by ADR-007.

## U. Risks

| Risk | Treatment required before release |
|---|---|
| Distribution name unavailable or controlled by another party | Verify/reserve ownership in the intended package index; if unavailable, return to human architecture review rather than silently rename. |
| Consumers confuse distribution and import names | Document `pip install cko-fcp` versus `import cko_fcp`; test metadata and examples. |
| Namespace move accidentally changes serialization or qualified names | Preserve logical wire serialization; run golden vectors and review whether Python qualnames are contractual before ratification of implementation. |
| Independent versions are mistaken for protocol versions | Expose and document the two version concepts explicitly; test negotiation independently of package metadata. |
| Monorepo tooling assumes one root project | Build from the FCP project directory; add workspace orchestration only by separate justified change. |
| FCP later gains accidental Core dependency | Enforce AST/import and metadata dependency tests in every release. |
| Packaging includes repository-only material | Use an explicit wheel allow-list and RECORD inspection. |
| Separate release governance is undefined | Assign owner, release authority, index, provenance, signing, retention, and vulnerability-response policy before publication. |

## V. Remaining human decisions

Human ratification is required before implementation. Ratification should confirm:

1. distribution identity `cko-fcp` and import namespace `cko_fcp`;
2. authority/ownership or reservation of the distribution name in every intended
   package index;
3. initial distribution version and release channel, without coupling it to SDK
   `cko` version;
4. FCP package owner, release authority, signing/provenance policy, vulnerability
   response, and artifact retention;
5. whether `README.md` and license metadata reuse repository-level governance or
   require package-local copies;
6. authorization of the file moves, namespace-only import edits, test edits, and
   new packaging project described in section T;
7. authorization of an incremental P1-R17 wheel replay after implementation.

Until ratified and implemented:

- `PACKAGING_CHANGE_REQUIRED: YES`
- `FILE_MOVE_REQUIRED: YES`
- `P1_R17_REPLAY_REQUIRED: YES — PACKAGING-FOCUSED INCREMENTAL REPLAY`
- `P_018_01_CONSOLIDATION_AUTHORIZED: NO`
- `P_018_02_AUTHORIZED: NO`

## Required results

`RECOMMENDED_ARCHITECTURE: INDEPENDENT CKO-FCP DISTRIBUTION WITH CKO_FCP NAMESPACE`  
`TARGET_NAMESPACE: cko_fcp`  
`TARGET_DISTRIBUTION: cko-fcp`  
`TARGET_REPOSITORY_LOCATION: packages/cko-fcp/src/cko_fcp/`  
`VERSIONING_POLICY: INDEPENDENT SEMVER DISTRIBUTION VERSION; EXPLICIT SEPARATE FCP PROTOCOL COMPATIBILITY VERSION`  
`PACKAGE_DISCOVERY_POLICY: DISTRIBUTION-LOCAL SRC DISCOVERY LIMITED TO packages/cko-fcp/src`  
`PUBLIC_API_IMPACT: NONE`  
`PUBLIC_API_COUNTS_EXPECTED: 646 / 646 / 646`  
`PUBLIC_API_FINGERPRINT_EXPECTED: d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`  
`BREAKING_CHANGE_REQUIRED: NO`  
`PACKAGING_CHANGE_REQUIRED: YES`  
`FILE_MOVE_REQUIRED: YES`  
`P1_R17_REPLAY_REQUIRED: YES — PACKAGING-FOCUSED INCREMENTAL REPLAY`  
`P_018_01_CONSOLIDATION_AUTHORIZED: NO`  
`P_018_02_AUTHORIZED: NO`

## W. Canonical SHA-256

`CANONICAL_SHA256: e73c2f51c609a239aecb029a65bb01f3d4d10b6961fef909f76e2509f238cca2`

Convention: SHA-256 of the complete UTF-8 file after replacing the embedded
digest with `<SHA256>` and normalizing line endings to LF.

## Verdict

`ADR-007 READY FOR HUMAN RATIFICATION — FCP PACKAGING ARCHITECTURE DEFINED`
