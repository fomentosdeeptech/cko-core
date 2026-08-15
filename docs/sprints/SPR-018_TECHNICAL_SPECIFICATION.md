# CKO — SPR-018 — Technical Specification and Gate Preparation

**Status:** TECHNICAL SPECIFICATION / NON-EXECUTABLE / AWAITING HUMAN GATES
**Version:** 1.0
**Date:** 2026-08-12
**Scope:** P-018-01 through P-018-05
**Authority chain:** CKO-GOV-001 → CKO-ARCH-001 → ARCH-001 → CKO-ARCH-002 → GOV-002/GOV-003 → ADR-006 → RFC-002/REV-002 → SPR-018
**Protected baseline:** `CKO-BASELINE-2026.07` (`faa51ac6568dc2aa0e11d2333671b1098a1a89fa`)
**Protected SDK/API:** `cko` 1.0.0; exactly 646 root exports, unique and resolved
**Implementation authorization:** NONE

> This specification makes the approved FCP architecture implementable and testable. It does not implement code, select infrastructure, approve D0–D4, authorize access to a real source, promote FCP contracts to the SDK, or authorize a package.

## 1. Preflight and documentary basis

Preflight on 2026-08-12: branch `main`; HEAD, local `origin/main`, and remote `origin/main` all `45d3bf87f9f01b663971b0dd6fa306aa207ab679`; tag object `ffa9cd23909c01e13cbc9926048dc69e12ff11fc`; peeled baseline `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`. Pre-existing untracked files were observed and are outside this operation.

Read authorities: external `CKO-GOV-001_BASELINE_ARQUITETURAL_1.0.md`; external `CKO-ARCH-001_ARQUITETURA_CANONICA.md`; `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md`; `CKO-ARCH-002_ECOSYSTEM_EVOLUTION_ARCHITECTURE.md`; GOV-002, GOV-003, GOV-006, GOV-007 and GOV-008; ADR-006; RFC-002; REV-002; SPR-018 Termo de Abertura; SPR-017 implementation/homologation and Provenance documents; and the public API catalog. `SPR018_DISCOVERY_AND_SCOPE.md` is exploratory and does not override the Termo de Abertura.

## 2. Scope, invariants, and boundaries

The official decomposition P-018-01 through P-018-05 is preserved. All future implementation is external to `cko.core`, composed by an Application, with replaceable Provider/Adapter boundaries. The Core must not depend on a database, Drive, network, IAM, transport, framework, product, or source.

Invariants:

1. FCP logical contract ≠ future internal Python contract ≠ SDK public API.
2. No FCP item is implicitly exported by `cko.core`.
3. Source identity, ownership, authority, content, and custody remain at their governed origins.
4. Discovery does not imply admission; admission does not imply publication; publication of metadata does not imply publication of content or official status.
5. Effective access is the intersection of applicable policies. Indeterminate or conflicting authority fails safe.
6. Read-only is the default. No package writes to a real source.
7. Published statements and decisions are immutable/append-only; correction creates a successor linked to the prior statement.
8. Partiality, omissions, unavailability, conflicts, validity, and coverage remain explicit without revealing protected existence.
9. Cache, index, projection, export, and telemetry never acquire authority.
10. SPR-017 Provenance Statement is reused; no competing provenance mechanism is created.
11. SDK version remains 1.0.0 and the root API remains 646/646/646 before and after every package.
12. A package stops on a baseline/API change, non-deterministic authority, unapproved real access, material RFC ambiguity, or a required breaking change.

## 3. Common logical type system

These are language-neutral schemas, not Python classes or public exports.

| Type | Required fields / constraints |
|---|---|
| `OperationEnvelope` | opaque `operation_id`, `correlation_id`, FCP `major.minor`, requested capabilities, technical/human actor refs, purpose, audience, authorization context, issued/deadline instants, scope, policy refs, read-only=true, optional page/version/idempotency tokens |
| `OperationResult<T>` | one of `success`, `partial`, `denied`, `unavailable`, `conflict`, `invalid`; correlation, negotiated version/capabilities, observed instant, validity, authorized coverage, source status, applied policy refs, authorized data/errors, Provenance refs, continuation |
| `SourceIdentity` | `source_id` + opaque `local_id`; neither component is rewritten; source revision optional but explicit |
| `CatalogRecord` | opaque stable `record_id`; record/FCP version; asset class/type/purpose; protected source reference; authority/owner/steward/custody assertions; maturity/publication/visibility/trust axes; access, Provenance, relationships, lifecycle |
| `AuthorityAssertion` | authority ref, competence, operation, source/domain/asset scope, valid-from/to, delegation ref, precedence, block powers, evidence ref, version |
| `DecisionStatement` | decision ID, operation, subject, requester, executor, authorizer, blockers consulted, result, reason code, effective interval, version precondition, idempotency key, Provenance ref |
| `PageRequest` | opaque continuation or initial request, positive bounded page size, immutable query/scope fingerprint |
| `PageResult<T>` | ordered authorized items, opaque next continuation, coverage, validity, source statuses; no total count unless policy authorizes it |
| `ErrorDetail` | stable code, category, retryability, safe message, correlation; no secret, protected identifier, policy internals, or existence leak |

Cardinalities: one subject per decision/Provenance statement; exactly one accountable owner for a publishable asset unless a formally approved co-owner tie-break rule exists; zero-or-one steward only where policy permits, otherwise exactly one for published Dataset/Corpus; zero-or-many assertions and evidence refs, canonically ordered; operation IDs and idempotency keys are unique in their declared scope.

## 4. Executable logical contracts (COND-001)

All contracts require deterministic canonical input validation, deny-by-default policy evaluation, typed semantic results, secure observability, and synthetic-fixture contract tests.

| Contract | Layer / owner | Inputs → outputs | Preconditions and postconditions | Failure / idempotency / version |
|---|---|---|---|---|
| `DescribeCapabilities` | FCP; participant owner | envelope → supported versions, classes, operations, limits | authenticated participant; returns only authorized capabilities | read-only/repeatable; incompatible major=`invalid`; unknown safe minor ignored/negotiated |
| `Discover` | Provider via Adapter | source/scope/filter/page → observations + coverage | source/read grant valid; no mutation; every observation links source and Provenance | repeatable; timeout may be `partial`/`unavailable`; opaque stable continuation |
| `SubmitForAdmission` | governed Application | observation, candidate record, evidence → accept/reject/request-more | authority matrix resolves admission; accepted record is not published | decision idempotency key; optimistic version; conflict never overwrites |
| `GetRecord` | Application query | record/version/context → authorized view or safe negative | policy intersection evaluated before existence disclosure | read-only; indistinguishable safe negative where existence protected |
| `ResolveIdentity` | authorized external component | qualified identities/evidence → candidates/conflicts/confidence | no automatic merge/canonicalization | repeatable; conflict explicit; no side effect |
| `VerifyRecord` | authorized verification function | record/version/evidence → successor statement or failure | matching version; verified evidence; authority resolved | idempotent decision; may reach T2 only; timeout requires status query |
| `CurateRecord` | governed stewardship | record/version/opinion/evidence → steward decision | steward competence and scope valid | append-only; may reach T3 only; conflict fails closed |
| `DecidePublication` | governed Application | record/audience/validity/approvals → publication decision | owner + publication authority + security/data blocks clear | idempotent; metadata only; never content or Official/T4 implicitly |
| `DeclareOfficial` | institutional authority | record/scope/decision → Official/T4 assertion | explicit institutional authority, scope, validity, human decision | no automatic promotion; append-only; conflict blocks |
| `RestrictRecord` | competent blocker | record/reason/policy → narrower visibility | blocker competence verified | monotonic restriction; retry safe by same idempotency key |
| `SuspendRecord` | competent authority | record/risk/authority → suspension | risk/incident evidence and authority | blocks use; propagates invalidation; never deletes history |
| `RestoreRecord` | competent authority | suspended record/revalidation → successor active state | revalidation and current approvals | new version required; stale restore conflicts |
| `WithdrawRecord` | owner/authority | record/reason/retention → tombstone/protected ref | retention/privacy policy resolved | ends publication; no ID reuse; idempotent |
| `QueryCatalog` | consuming Application | context/expression/projection/page → authorized result | authorization before filter/count/order/facet; purpose valid | repeatable; partial coverage explicit; continuations scope-bound |
| `TraceProvenance` | audit/Application | entity/depth/context → authorized subgraph | policy checked per node/edge | read-only; omissions explicit but non-revealing; uses SPR-017 statements |
| `Revalidate` | external governed component | record/source/policy → confirm/correct/suspend/conflict | current source authorization and version | does not correct source; successor statement on change |
| `Conformance` | every participant | profile/evidence → conformity report | declared FCP version/capabilities | deterministic; no self-authorization; evidence digest required |

Logical error catalog: `FCP_INVALID_INPUT`, `FCP_UNSUPPORTED_MAJOR`, `FCP_CAPABILITY_ABSENT`, `FCP_AUTHORITY_UNKNOWN`, `FCP_AUTHORITY_CONFLICT`, `FCP_DENIED`, `FCP_EXISTENCE_PROTECTED`, `FCP_VERSION_CONFLICT`, `FCP_IDEMPOTENCY_CONFLICT`, `FCP_RESULT_UNKNOWN`, `FCP_SOURCE_UNAVAILABLE`, `FCP_PARTIAL_COVERAGE`, `FCP_CONTINUATION_INVALID`, `FCP_EXPIRED`, `FCP_REVOKED`, `FCP_PROVENANCE_INCOMPLETE`, `FCP_INTEGRITY_FAILED`. Error exposure is filtered by policy.

Future Python contracts, if authorized, must be internal to the external implementation, protocol-oriented, dependency-injected, and traceable one-to-one to these logical contracts. Their naming, module layout, and libraries are P2 implementation choices. They must not be imported or re-exported by `cko.core`.

## 5. Deterministic authority matrix (COND-002)

The following is a role template. Before real implementation, a human-approved instance must replace each role with an identified authority per source/domain/act/validity. Missing instance data means fail-safe denial.

| Operation | Requests | Executes | Authorizes | May block | Audits | Required evidence | Missing/conflicting authority |
|---|---|---|---|---|---|---|---|
| register source | source owner | technical operator | governance + source authority | security, privacy, data authority | governance/audit | mandate, source profile, purpose, access, validity | deny registration / escalate without side effect |
| admission | owner/steward | governed Application | owner + admission authority | security/privacy/domain authority | catalog auditor | observation, identity, rights, policy, Provenance | reject or retain only authorized restricted observation |
| verification | steward | verification function | designated verifier | source/security authority | independent reviewer | source evidence, integrity, version | remain Registered/T1; no T2 |
| curation | steward | governed Application | steward within delegation | owner/domain authority | domain reviewer | review, taxonomy/context, conflicts | remain Verifed; no T3 |
| metadata publication | owner/steward | publication function | owner + publication authority | security/privacy/data/domain authority | governance/audit | T2+, audience, purpose, approvals, withdrawal path | not published |
| officialization | competent authority | governed Application records act | institutional authority | security/privacy/domain authority | governance/audit | human decision, scope, validity, T4 evidence | never Official |
| restriction | competent blocker | publication function | blocker within competence | any stronger competent blocker | security/audit | risk/policy/incident evidence | choose most restrictive valid result; otherwise suspend |
| suspension | owner/authority/security | publication function | competent authority | security/privacy/source authority | incident/audit | reason, scope, correlation, revocation plan | suspend if a valid blocker exists; otherwise deny mutation |
| restoration | owner/steward | publication function | original/competent authority | security/privacy/source authority | independent reviewer | revalidation, current policy, version | remain suspended |
| withdrawal | owner/authority | publication function | owner + retention authority | legal/privacy/security | audit | reason, retention/tombstone policy | remain restricted/suspended; escalate |
| query | authenticated consumer | query Application | policy decision point from approved policy set | source/security/privacy/domain policy | proportional audit | purpose, audience, grants, resource policy, validity | safe deny; no existence/count leak |
| Provenance trace | authorized consumer/auditor | trace function | policy decision point | security/privacy/source authority | audit | trace purpose, depth, per-node policy | return safe denied/authorized partial graph |
| conflict resolution | owner/steward/authority | records decision only | authority explicitly competent for conflict type | security/privacy/domain/source authority | independent governance | competing assertions, precedence, evidence, signed decision | no merge/promotion; conflict remains explicit |

Precedence algorithm: (1) discard expired/out-of-scope assertions; (2) require verifiable competence and evidence; (3) intersect all applicable access restrictions; (4) any valid blocker prevails inside its competence; (5) only an explicitly designated decision authority can choose among substantive assertions; (6) ties or incompatible authorities produce `FCP_AUTHORITY_CONFLICT`; (7) unknown authority produces `FCP_AUTHORITY_UNKNOWN`; (8) both outcomes deny promotion/publication/access and preserve auditable evidence without exposing protected facts.

## 6. Resilience and versioning profile (COND-003)

Technology-neutral policy to freeze in package configuration and tests:

- Deadline is supplied in the operation envelope; each dependency receives a smaller remaining budget. A package-specific numeric SLO must be approved before real-source use. No unbounded call.
- Automatic retry is allowed only for read-only operations and demonstrably pre-effect transport failures. Decision operations retry only with the same idempotency key after a safe status query.
- Backoff is bounded exponential with jitter; exact base/cap/attempt count are environment profile values approved and test-fixed, not library constants inferred by code.
- Quota exhaustion returns explicit partial/unavailable coverage and never falls back to broader credentials.
- Circuit breaking is per source + Adapter + Provider + operation. Opening one circuit cannot block unrelated sources; half-open probes are read-only and least privilege.
- Unknown result after timeout remains `FCP_RESULT_UNKNOWN`; no blind replay. Recovery queries by operation/idempotency key.
- Idempotency scope is authority domain + operation + subject + key. TTL must exceed the maximum uncertainty/reconciliation window and is a human-approved environment value.
- Optimistic concurrency uses an opaque version token over the last authorized immutable state. Mismatch returns conflict; no last-write-wins.
- Pagination continuation is opaque, integrity-protected, expires, binds to caller/purpose/query/scope/version/order, and cannot broaden access. Invalid/expired continuation restarts only by explicit caller choice.
- Stable deterministic order uses approved non-sensitive keys plus an opaque tie-breaker. Total counts/facets are omitted unless authorized.
- Cache entries carry source, policy, record/version, observation time, validity, and Provenance. Cache never outlives the minimum of data validity, authorization, revocation, and retention constraints.
- Revocation/suspension invalidates affected projections/caches within an approved SLO. Until confirmation, access fails closed.
- Partial failure isolates source/Provider/Adapter. Results state consulted, omitted, and unavailable coverage only to the degree disclosure policy permits.
- Rollback disables external composition, revokes credentials, invalidates projections, restores legacy flow, preserves append-only evidence, and rechecks 1.0.0/646.
- Shutdown stops new work, drains/cancels within deadline, records unresolved operation IDs, closes external sessions, and leaves no implicit retry worker.

FCP versions are `major.minor`. Major changes alter semantics, required fields, security, authority, or Provenance obligations and are incompatible. Minor changes are additive and optional under capability negotiation. Participants negotiate the intersection of compatible major and capabilities; absence is explicit. Unknown extensions are preserved only if their container is declared opaque and cannot affect authority, access, state, identity, Provenance, or validation; otherwise reject. Downgrade is refused if it weakens security, Provenance, failure semantics, or required capability.

## 7. Security and observability profile (COND-004)

Trust boundaries: consumer↔Application, Application↔Provider, Provider↔Adapter, Adapter↔source, and every telemetry/audit sink. Authentication and IAM mechanisms are external choices; the specification requires verified participant identity, explicit purpose, scoped/revocable credentials, and separation of technical operator from institutional authority.

Effective authorization = intersection of institutional, source, asset, application, purpose, audience, temporal, and legal/privacy policies. Deny before revealing existence, metadata, counts, ordering, facets, latency distinctions, or error details. Read-only credentials are mandatory by default. Secrets never enter records, fixtures, source control, general logs, metrics labels, traces, or Provenance qualifiers.

May log: correlation/operation IDs; pseudonymous participant/source IDs; contract and negotiated version; coarse operation; semantic result; bounded duration; retry/circuit state; authorized coverage category; stable safe error code; policy decision ID/digest; Provenance statement ID/digest. Must not log: content, secrets/tokens, raw source/local IDs, protected paths/URLs/titles, personal data, policy internals, query literals, existence of restricted assets, full records, evidence payloads, or unrestricted stack/local-variable dumps. Minimize all fields; pseudonymize stable identifiers with a governed per-environment transform; encrypt and access-control audit evidence; set human-approved retention by event class.

Metrics use bounded dimensions only: operation, result, version/capability, source class pseudonym, retry/circuit state, latency bucket, coverage class. No asset/user/query/source-local ID labels. Traces propagate correlation IDs but redact attributes at creation. Security events include failed authority validation, denied/ambiguous access, replay/idempotency conflict, integrity failure, protected-existence probing, revocation/suspension, credential misuse, unsafe downgrade, and telemetry redaction failure. A telemetry leak suspends the affected perimeter.

## 8. Provenance integration

Use the homologated `cko.core.provenance` public contracts without modification. FCP code creates authorized `ProvenanceStatement` values through `ProvenanceStatementFactory`, serializes with `DeterministicProvenanceSerializer`, and validates/digests with the existing services. FCP must not resolve opaque references or mutate Graph, Query, Index, Corpus, Inventory, source, or statement.

Statements are produced for source observation, admission/rejection, verification, curation, publication/officialization, restriction/suspension/restoration/withdrawal, transformation/projection, query result production where proportional, revalidation, conflict decision, correction, and supersession. Subjects are the FCP record/decision/result reference; entities are source observation, prior record/version, policy/evidence refs, and input statements; actors are declared human/technical agents; activity describes the governed act; result is represented by the subject/version/digest. Correction uses a new revision and explicit predecessor/supersession relation; history is never overwritten. Trace authorization applies to every returned node and relationship. Retention is the intersection of audit, privacy, source, and legal policies; unknown retention blocks real evidence persistence.

## 9. Public API protection (COND-005)

Before and after every package, in source and isolated built artifact:

1. import the approved `cko.core` root;
2. capture `tuple(cko.core.__all__)` and resolve every name with `getattr`;
3. assert length=646, unique-name count=646, resolved count=646;
4. compare ordered/name→module→qualname/type/signature fingerprint with the approved baseline catalog and characterization fixture;
5. assert no removals, additions, renames, rebindings, signature changes, semantic characterization changes, or FCP names;
6. assert SDK/package version remains 1.0.0 and no `src/cko`, packaging, dependency, or build metadata diff exists;
7. store machine-readable evidence and digest in the package dossier.

Any difference is a blocker and triggers rollback. A future new export is a separate architectural change, outside SPR-018, requiring its own decision. This specification requires zero public API impact and zero breaking change.

## 10. Package specifications

### P-018-01 — External protocol foundation

Objective: implement, externally and technology-neutrally, the logical types, identities, records, four state axes, lifecycle validation, capability/version negotiation, strict validation, and semantic errors. Out of scope: persistence, transport, IAM, source access, publication authority, SDK changes. Inputs: RFC-002, this specification, approved profiles and D1–D3 evidence. Outputs: internal external-package types/validators/serializers and conformance fixtures. Interfaces: common type system, `DescribeCapabilities`, `Conformance`. Invariants: immutable/versioned values, source identity preserved, no authority inference, no I/O in the domain. Expected failures: invalid/unknown version, closed-field violation, identity collision, illegal transition, unknown capability. Security/Provenance/observability: no sensitive payload logging; validation statements only when policy requires. Resilience: pure/deterministic; idempotent validation; concurrency not applicable except version comparison; pagination only schema validation. Tests: unit schemas/state transitions; contract envelopes/errors/version negotiation; integration entirely in memory; regression 646 and dependency direction. Acceptance: every schema/cardinality/error/transition has a passing and failing fixture, deterministic serialization, no Core diff. Rollback: remove external composition/artifact. Evidence: schema inventory, vectors, contract report, AST/dependency report, API regression.

### P-018-02 — Authority, publication, and query

Objective: apply the approved authority instance, lifecycle decisions, policy intersection, safe query, and separation of publication/officialization. Out of scope: IAM implementation, policy authorship, real source access, content publication. Inputs: P-018-01; human-approved authority matrix and policy fixtures; D0–D4 evidence applicable. Outputs: external policy/decision orchestration and audit-safe results. Interfaces: Admission, Verification, Curation, Publication, query, restriction/suspension/restoration/withdrawal. Invariants: no operator authority; blockers prevail within competence; authority unknown/conflict fails closed; filter before count/order/facet; metadata publication ≠ Official. Failures: denied, protected existence, authority unknown/conflict, stale version, expired/revoked policy. Security: least privilege and safe negatives. Provenance: statement for every decision and correction. Observability: decision IDs/digests, never protected facts. Resilience/idempotency/concurrency/pagination: as sections 6–7; decisions keyed and version-preconditioned; query continuations scope-bound. Tests: exhaustive role/operation matrix, conflicting/expired delegation, non-inference timing/error tests, query leakage tests, concurrent decisions, replay. Acceptance: approved matrix instance exists and all deny paths proven; no real identity or data. Rollback: disable decision/query component and revoke test credentials. Evidence: authority decision table, policy vectors, security/privacy report, audit trail, API regression.

### P-018-03 — Federation and resilience

Objective: compose approved synthetic/authorized source projections through external Adapter/Provider boundaries with discovery, pagination, partial failure, timeout, retry, quota, circuit isolation, shutdown, and rollback. Out of scope: production operation, source writes, mandatory physical centralization/cache/index, unapproved technology. Inputs: P-018-01/02; approved D3/D4; isolated environment, source profiles and credentials. Outputs: replaceable external composition and resilience evidence. Interfaces: SourceCapability, Discover, Revalidate plus internal Adapter/Provider ports. Invariants: read-only; one source failure cannot contaminate others; projection never becomes source; unknown outcome not blindly retried. Failures: unavailable/partial/quota/timeout/continuation invalid/result unknown. Security: per-source credentials and isolation. Provenance: observation/transformation/source status. Observability: low-cardinality per-perimeter health. Idempotency/concurrency/pagination: full section 6 profile. Tests: contract fakes, fault injection at every boundary, deterministic pagination under changes, circuit transitions, quota, cancellation, shutdown, cache expiry/revocation, rollback. Acceptance: numeric environment SLO profile approved; no writes; recovery and isolation demonstrated. Evidence: fault matrix, timing profile, circuit/retry traces, shutdown/rollback report, API regression.

### P-018-04 — Provenance and conflicts

Objective: bind the FCP lifecycle to SPR-017 Provenance, represent conflicts/lacunae/corrections/supersession, and provide authorized trace. Out of scope: second provenance model, automatic trust/canonicalization, Graph mutation, global chain claims. Inputs: P-018-01/02/03 and approved retention/redaction/profile. Outputs: mapping profile, statement fixtures, authorized trace behavior. Interfaces: TraceProvenance, ResolveIdentity, conflict decision, existing Provenance public services. Invariants: append-only; opaque refs; digest is integrity not truth; partial chain limitations explicit; no protected-node inference. Failures: invalid/incomplete statement, digest failure, cycle/conflicting ref, trace denied/partial. Security: per-node/edge trace filtering and retention. Observability: IDs/digests only. Resilience: unavailable evidence blocks promotion; revalidation required after expiry. Tests: every lifecycle mapping, correction/revision, supersession, partial/external chain, integrity failure, redaction and graph-shape leakage. Acceptance: end-to-end synthetic trace reconstructs source→observation→decision→projection→query without duplicated mechanism. Rollback: disable mapping/trace while preserving statements under retention. Evidence: mapping matrix, canonical vectors/digests, privacy/security test report, API regression.

### P-018-05 — Conformance and D5 dossier

Objective: run reproducible conformance, compatibility, rollback, integrated homologation support, and assemble evidence; never decide D5. Out of scope: automated human approval, production deployment, Core promotion. Inputs: homologated/audited P-018-01–04 evidence. Outputs: requirement-test-evidence matrix, compatibility report, rollback evidence, signed/hashed dossier manifest. Interfaces: Conformance and evidence collectors only. Invariants: evidence is immutable, attributable, minimized, reproducible, and cannot self-approve. Failures: missing/stale/unverifiable evidence, API mismatch, unresolved blocker, unauthorized data. Security: dossier access/retention and redaction. Provenance: evidence generation and supersession statements. Resilience: deterministic rerun; partial evidence never reported complete. Tests: manifest integrity, missing/tampered evidence, clean-environment replay, rollback/shutdown, full 646/source/wheel checks. Acceptance: all rows resolved or explicitly blocked with owner; independent human approvals remain pending fields. Rollback: discard generated working dossier, retain governed audit evidence. Evidence: signed manifest, hashes, test reports, package homologations/audits, final compatibility report.

## 11. Test strategy

Only isolated fixtures, synthetic data, or explicitly authorized data are permitted. No test writes to Google Drive, Downloads, `02_Knowledge`, real databases, datasets, corpora, or institutional sources.

Required suites: unit (types, validation, transition, deterministic order); logical contract (all operations/results/errors); integration (in-memory/fake Adapter/Provider); security and privacy (least privilege, inference, redaction, secret scanning); resilience/failure injection (timeouts, retry, circuit, quota, cancellation, partiality); Provenance (mapping, digest, correction, chain, trace authorization); compatibility/API regression; deterministic replay/golden vectors; idempotency/result-unknown; pagination/continuation; optimistic concurrency; rollback/shutdown/isolation. Every requirement maps to test ID, fixture, expected result, evidence path/digest, package, reviewer, and status.

## 12. Conditions and gates assessment

| ID | Current status | Objective evidence | Required before implementation |
|---|---|---|---|
| COND-001 | SATISFIED | sections 3–4 and package contract/test criteria | approve this specification and package-specific audit |
| COND-002 | PARTIALLY_SATISFIED | deterministic role/precedence template in section 5 | human-approved named authority instance per real source/domain/act/validity |
| COND-003 | PARTIALLY_SATISFIED | complete technology-neutral policy in section 6 | approve numeric SLO/TTL/quota/backoff/revocation profile per environment/source |
| COND-004 | PARTIALLY_SATISFIED | security/telemetry rules in section 7 | approve concrete trust/IAM, retention, pseudonymization and incident profile per perimeter |
| COND-005 | SATISFIED | automated mechanism specified in section 9; baseline evidence 646/646/646 | execute before/after checks during each authorized package |
| D0 | UNSATISFIED | GOV-002 defines it; no approval act/evidence located | governance approves cycle controls, authority, scope, protections |
| D1 | UNSATISFIED | no accepted authorized inventory by applicable trail located | owner validates coverage, limitations, Provenance and authorization |
| D2 | UNSATISFIED | no approved capability treatment/mapping by applicable item located | approve compose/maintain/decide/close treatment without API change |
| D3 | UNSATISFIED | no approved Adapter/Provider composition/pilot preparation located | approve specification, security, tests and rollback for applicable composition |
| D4 | UNSATISFIED | no supervised pilot homologation evidence located | human homologates/repeats/rejects applicable pilot |

No P0 architectural gap was found. P1 blockers are human/institutional instantiation and approval of D0–D4, authority, security, environment, source access, numeric operational profiles, pre-implementation audit, and explicit package authorization. No new ADR/RFC is required unless a future package demands a public export, Core change, real-source write, canonical persistence, different security model, or other material boundary change.

## 13. Readiness decision

The packages are technically specified at implementation-ready design level, but real implementation cannot start because D0–D4 and concrete perimeters are not approved and COND-002/003/004 still require human-approved instances. Required public API impact: none. Required breaking change: none.

**Verdict: `SPR-018 CONDITIONALLY READY — REMAINING GATES IDENTIFIED`.**

Next action: conduct human gate review for D0–D4 and approve the named authority/security/operational profiles per deliberately bounded trail; then perform an independent pre-implementation audit and issue explicit authorization package by package. Do not implement automatically.
