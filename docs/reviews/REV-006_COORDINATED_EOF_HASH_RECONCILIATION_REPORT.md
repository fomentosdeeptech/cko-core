# CKO — REV-006 — Coordinated EOF and Hash Reconciliation Report

Date: 2026-08-14
Operation: WS-003 — Coordinated EOF and Hash Reconciliation
Status: CREATED / NOT STAGED / PENDING_HUMAN_REVIEW

## A. Authority and scope

WS-003 authorized eleven existing files and this evidence report only. No commit, push, REL-002R resumption, POLICY_B expansion, P-018-02, or human ratification was authorized.

## B. REL-002R history

REL-002R stopped before commit after 154 ratified hard breaks and eight new-blank-line-at-EOF diagnostics. Staging returned to empty.

## C. WS-002 block

WS-002 stopped before modification because isolated VAL-003 EOF removal would invalidate REV-004, allowlist, and VAL-004 bindings.

## D. REV-005 result

The dependency closure was CLOSED; no cryptographic cycle existed; a safe recalculation order existed.

## E. WS-003 preflight

Branch main; HEAD/local origin/remote 45d3bf87f9f01b663971b0dd6fa306aa207ab679; baseline faa51ac6568dc2aa0e11d2333671b1098a1a89fa; staging empty; no Git operation or lock. The eleven paths belonged to the explicit preserved 30-path REL-002R list.

## F. Eleven existing authorized paths

1. docs/reviews/REV-003_SPR-018_HUMAN_GATE_REVIEW.md
2. docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002B_REPLAY_REPORT.md
3. docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002C_REPLAY_REPORT.md
4. docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002D_FINAL_VALIDATION_REPORT.md
5. docs/sprints/SPR-018_P-018-01_P1-R17_VALIDATION_REPORT.md
6. docs/sprints/SPR-018_P-018-01_VAL-003_BASELINE_DIFFERENTIAL_REPORT.md
7. packages/cko-fcp/README.md
8. packages/cko-fcp/pyproject.toml
9. docs/sprints/SPR-018_P-018-01_VAL-004_WHEEL_REPLAY_REPORT.md
10. docs/reviews/REV-004_REL2_R13_WHITESPACE_ALLOWLIST.csv
11. docs/reviews/REV-004_REL2_R13_WHITESPACE_SEMANTIC_REVIEW.md

All were preexisting and untracked.

## G. External recovery snapshot

Path: C:\Users\ANDRÉ\AppData\Local\Temp\CKO_WS-003_RECOVERY_20260814_230214_ebb02598158f416fb8bbbdf30ce89c71
Files: 11
Byte equivalence: PASS
Manifest SHA-256: a5ff626cbb6a2964c6f47f793b11da10fce997b34e4402d842c7a9321ff3853c
Preservation: retained pending human decision and consolidation.

## H. Pre-remediation baseline

The eight targets were UTF-8, pure LF, non-mixed, ended in 0a 0a, and had two logical EOF terminators. All binding hashes reproduced.

## I. Eight EOF transformations

One final LF was removed from each target. Each now has one final LF. Internal content, order, encoding, EOL style, and hard breaks were preserved. VAL-003 and ENV-002D additionally received only their authorized embedded-digest update.

## J. VAL-003 reconciliation

Pre raw: 8c3f2f086073bc6568d5b2e1e73b5d3346511239f387c146e0ce3308dde53795
Pre canonical: f473556536dcb39f947769880e130a3c55f7689489bf08521d2cdf55f3424f2b
Post raw: 81a69c228c471b765cd519297338aed206ec87fe882486ac8cad49dff1b70d58
Post canonical candidate: 7164e1839dc102110385c9f86af377ab36d6e433e246e5de98523fa77bccbdcc
Expected match: YES
Semantic change: NO

## K. ENV-002D reconciliation

Pre raw: e63336293b795d79835ef2738f079a321b740d97c3919401db1820ff5ac59094
Post raw: 211ea1c09bcd87f971b42689e0a016975851a1e3a51270fb90d6bdfb26d0f3a0
Post canonical candidate: 2584e2d4a039d7b21ccc91191a19fbe5992afb8e049e2431626f40a713826823
Semantic change: NO

## L. VAL-004 reconciliation

VAL-004 references the candidate VAL-003 hash and declares PENDING_HUMAN_RE_RATIFICATION. Technical conclusions remain unchanged.
Pre raw: 4dacaf7513c0aba375669f6e9397fea4a68fff467231667058e4052f7b178e6b
Post raw: 81a63d74781749f5f76d574b87bd9c1e0d090f158c0c4003e51bd35419f0fd23
Post canonical candidate: a48a5ac699ee41ecd78a8ca1a4df22c18f6c11792bf83e39d64f471c99d0a4fe
Re-ratification required: YES

## M. Allowlist reconciliation

Entries: 154 before and after. Hash fields updated: 98. Line references updated: 20, mechanically caused by two authorized VAL-004 status lines. Rows added/removed: 0/0. Semantic content changes: 0.
Pre SHA-256: df66795b334505197c5d4f5384975dedf4caa18c64930d85fdc78b26535c6ce5
Post SHA-256 candidate: b6940a23ac228529ce1e85284c0877ae78ed297af4950290a101b69cc19ddf7f
Status: RECONCILED_CANDIDATE_PENDING_HUMAN_RE_RATIFICATION

## N. REV-004 reconciliation

Reconciled after VAL-003, ENV-002D, VAL-004, and allowlist.
Pre raw: 92398b957e0792dace3a7f71c467bbd5cc723e0e4aeab900b9ec57afd71dc22b
Post raw candidate: bb4b3770492bc7d8e81cbb55e82e502f1852c3a3c09f5d2b9471e04dc8d87efd
Canonical convention: N/A
Status: PENDING_HUMAN_RE_RATIFICATION
POLICY_B semantic status: UNCHANGED
POLICY_B hash bindings: RECONCILED_CANDIDATE
Semantic conclusion/scope changed: NO/NO

## O. Complete pre/post hashes

| Path | Pre raw | Post raw | Post canonical |
|---|---|---|---|
| REV-003 human gate | 4dcb74e8e1f63a2389977edea1057c4d31d7bf60c0643d5cf546e627b03157eb | be6db1dbd734effbdaf0988c202d490871b6b45e700905ff9401e69d10576733 | N/A |
| ENV-002B | 1a78ec1ebe0cd86835544f27f2ff419900926f69fa4edb1c179b9dd4b48591c2 | bd1d0568b3e4cfd41866b92ddd4552a84e53bef28e82531f80312c718eb16035 | N/A |
| ENV-002C | 85d47757bcf5f814d3d22bd93648a025fad1647f146b8db1a1ae8a8510725f97 | ca33c2125edc4ad6ad5d08f59cd2260bc93258fdff9addfbdcb8bc04ea0f6dba | N/A |
| ENV-002D | e63336293b795d79835ef2738f079a321b740d97c3919401db1820ff5ac59094 | 211ea1c09bcd87f971b42689e0a016975851a1e3a51270fb90d6bdfb26d0f3a0 | 2584e2d4a039d7b21ccc91191a19fbe5992afb8e049e2431626f40a713826823 |
| P1-R17 report | 86ee20254285af2c7836382bd0982b3b63f43e4856819cd2d21f12ff0f1a213a | 0aa06652e2985827512c0f6c5d4f0f92c49596ed8b964ed8fc2573329302f32e | N/A |
| VAL-003 | 8c3f2f086073bc6568d5b2e1e73b5d3346511239f387c146e0ce3308dde53795 | 81a69c228c471b765cd519297338aed206ec87fe882486ac8cad49dff1b70d58 | 7164e1839dc102110385c9f86af377ab36d6e433e246e5de98523fa77bccbdcc |
| package README | 24395da301028d4c6bbad7bf76ccc290da03ff7a64da117998161a516395daf1 | c507ebc666462ca921b9c0b311a2173dbd106d83fd22bf8ce20d6a141ad4d1ec | N/A |
| package pyproject | 299911a6757718f3fbe42d3a58ca123dd916a20850dece7311375061a493d72e | ccecd137edb7a693e0b7c913fcc6a3aad18a57657cfb3cbb40ca79467d02df16 | N/A |
| VAL-004 | 4dacaf7513c0aba375669f6e9397fea4a68fff467231667058e4052f7b178e6b | 81a63d74781749f5f76d574b87bd9c1e0d090f158c0c4003e51bd35419f0fd23 | a48a5ac699ee41ecd78a8ca1a4df22c18f6c11792bf83e39d64f471c99d0a4fe |
| allowlist | df66795b334505197c5d4f5384975dedf4caa18c64930d85fdc78b26535c6ce5 | b6940a23ac228529ce1e85284c0877ae78ed297af4950290a101b69cc19ddf7f | N/A |
| REV-004 | 92398b957e0792dace3a7f71c467bbd5cc723e0e4aeab900b9ec57afd71dc22b | bb4b3770492bc7d8e81cbb55e82e502f1852c3a3c09f5d2b9471e04dc8d87efd | N/A |

## P. Hard-break proof

Before/after/changed: 154/154/0. Allowlist matches/mismatches: 154/0. Unauthorized whitespace and EOF diagnostics: 0/0.

## Q. Semantic-preservation proof

Unauthorized textual changes, internal EOL changes, line-order changes, removed hard breaks, and TOML key/value/structure changes: zero. TOML parse: PASS. VAL-004 and REV-004 changes were limited to reconciliation, demonstrated line references, and ratification status.

## R. REL2-R13 revalidation

Exactly the original 30 paths were temporarily staged; REV-006 was excluded. git diff --cached --check yielded 154 allowlisted diagnostics, zero unauthorized whitespace, and zero EOF diagnostics.
REL2_R13_REVALIDATION_STATUS: PASS_WITH_POLICY_B_RECONCILED_CANDIDATE
The 30 paths were then removed from staging.

## S. Final Git state

HEAD, remote, and baseline unchanged. Staging empty. Commit/push: NO/NO. Recovery snapshot preserved.

## T. SDK, Core, and API impact

SDK 1.0.0; API 646/646/646; fingerprint d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232. No src/cko, version, root packaging, or wheel change. Public API impact: NONE. Breaking change: NO.

## U. Future candidate list of 31 paths

1. docs/adr/ADR-007_FCP_DISTRIBUTION_PACKAGING_ARCHITECTURE.md
2. docs/reviews/REV-003_SPR-018_GATE_DECISION_MATRIX.csv
3. docs/reviews/REV-003_SPR-018_HUMAN_GATE_REVIEW.md
4. docs/reviews/REV-004_REL2_R13_WHITESPACE_ALLOWLIST.csv
5. docs/reviews/REV-004_REL2_R13_WHITESPACE_SEMANTIC_REVIEW.md
6. docs/sprints/SPR-018_IMPLEMENTATION_READINESS_MATRIX.csv
7. docs/sprints/SPR-018_TECHNICAL_SPECIFICATION.md
8. docs/sprints/SPR-018_P-018-01_IMPLEMENTATION_REPORT.md
9. docs/sprints/SPR-018_P-018-01_P1-R17_VALIDATION_REPORT.md
10. docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002B_REPLAY_REPORT.md
11. docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002C_REPLAY_REPORT.md
12. docs/sprints/SPR-018_P-018-01_DIAG-001_CKO_CORE_IMPORT_REPORT.md
13. docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002D_FINAL_VALIDATION_REPORT.md
14. docs/sprints/SPR-018_P-018-01_VAL-003_BASELINE_DIFFERENTIAL_REPORT.md
15. docs/sprints/SPR-018_P-018-01_VAL-004_WHEEL_REPLAY_REPORT.md
16. docs/sprints/SPR-018_P-018-01_ADR-007_PACKAGING_IMPLEMENTATION_REPORT.md
17. packages/cko-fcp/pyproject.toml
18. packages/cko-fcp/README.md
19. packages/cko-fcp/src/cko_fcp/__init__.py
20. packages/cko-fcp/src/cko_fcp/_validation.py
21. packages/cko-fcp/src/cko_fcp/contracts.py
22. packages/cko-fcp/src/cko_fcp/errors.py
23. packages/cko-fcp/src/cko_fcp/lifecycle.py
24. packages/cko-fcp/src/cko_fcp/models.py
25. packages/cko-fcp/src/cko_fcp/serialization.py
26. packages/cko-fcp/tests/__init__.py
27. packages/cko-fcp/tests/test_foundation.py
28. packages/cko-fcp/tests/test_packaging.py
29. packages/cko-fcp/tests/fixtures/valid_record.json
30. packages/cko-fcp/tests/fixtures/invalid_vectors.json
31. docs/reviews/REV-006_COORDINATED_EOF_HASH_RECONCILIATION_REPORT.md

This list is a candidate only and authorizes no staging, commit, push, or automatic REL-002R resumption.

## V. Candidate hashes

All post-reconciliation hashes are mechanical candidates pending human ratification.

## W. Human decision required

Human authority must ratify the candidate hashes, re-ratify VAL-004/REV-004/allowlist, authorize the 31-path list, and separately authorize REL-002R resumption. P-018-02 remains unauthorized.

## X. Verdict

WS-003 CONCLUÍDA — EOF E HASHES RECONCILIADOS / RATIFICAÇÃO HUMANA PENDENTE
