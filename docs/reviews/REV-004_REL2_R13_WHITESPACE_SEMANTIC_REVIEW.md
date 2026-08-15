# CKO — REV-004 — REL2-R13 Whitespace Semantic Review

**Date:** 2026-08-14
**Operation:** REL2-WS-001 — Whitespace Semantic Classification and Gate Decision
**Scope:** read-only audit of REL-002 closed-list candidates
**Verdict:** `REV-004 COMPLETE — CONTROLLED MARKDOWN EXCEPTION RECOMMENDED`

`REV004_RECONCILIATION_STATUS: PENDING_HUMAN_RE_RATIFICATION`
`POLICY_B_SEMANTIC_STATUS: UNCHANGED`
`POLICY_B_HASH_BINDINGS_STATUS: RECONCILED_CANDIDATE`

## A. Authority and method

REL-002 stopped before staging at REL2-R13. This review did not modify any
preexisting document, code, packaging file, Git index, commit, remote, baseline,
or P-018-01 artifact.

The audit decoded every candidate as strict UTF-8, inspected every physical line,
recorded the exact trailing characters and adjacent logical context, and evaluated
removal in memory. A Markdown line ending in exactly two spaces followed by a
nonblank line produces a hard line break. Removing those spaces converts it to a
soft line break and therefore changes rendering.

## B. Inventory

- `TOTAL_FILES_AUDITED: 28`
- `TOTAL_FILES_WITH_TRAILING_WHITESPACE: 10`
- `TOTAL_OCCURRENCES: 154`
- `TWO_SPACE_OCCURRENCES: 154`
- `OTHER_SPACE_OCCURRENCES: 0`
- `TAB_OCCURRENCES: 0`
- `EOF_WHITESPACE_OCCURRENCES: 0`

| File | Occurrences | Lines | Current raw SHA-256 |
|---|---:|---|---|
| `docs/adr/ADR-007_FCP_DISTRIBUTION_PACKAGING_ARCHITECTURE.md` | 17 | 3, 4, 5, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481 | `f8081730000a891c74f510c1151a23f8529da71d72d10c13be7b59bc3989052f` |
| `docs/sprints/SPR-018_P-018-01_ADR-007_PACKAGING_IMPLEMENTATION_REPORT.md` | 21 | 3, 4, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232 | `d5e7da942d195ec06548f09d7eeff158b240b4e06cd3e0de2cb617ec1e25d623` |
| `docs/sprints/SPR-018_P-018-01_DIAG-001_CKO_CORE_IMPORT_REPORT.md` | 15 | 3, 4, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152 | `49625c5f83f1024aca1f454797806c8957f320172006148da8af9cbe298906e8` |
| `docs/sprints/SPR-018_P-018-01_IMPLEMENTATION_REPORT.md` | 3 | 3, 4, 55 | `7b8369e0bce642e9abd82e62c12f583625772ec53af64d96aebe732e00314879` |
| `docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002B_REPLAY_REPORT.md` | 16 | 3, 4, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99 | `bd1d0568b3e4cfd41866b92ddd4552a84e53bef28e82531f80312c718eb16035` |
| `docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002C_REPLAY_REPORT.md` | 17 | 3, 4, 32, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76 | `ca33c2125edc4ad6ad5d08f59cd2260bc93258fdff9addfbdcb8bc04ea0f6dba` |
| `docs/sprints/SPR-018_P-018-01_P1-R17_ENV-002D_FINAL_VALIDATION_REPORT.md` | 21 | 3, 4, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156 | `211ea1c09bcd87f971b42689e0a016975851a1e3a51270fb90d6bdfb26d0f3a0` |
| `docs/sprints/SPR-018_P-018-01_P1-R17_VALIDATION_REPORT.md` | 7 | 3, 4, 80, 81, 82, 83, 84 | `0aa06652e2985827512c0f6c5d4f0f92c49596ed8b964ed8fc2573329302f32e` |
| `docs/sprints/SPR-018_P-018-01_VAL-003_BASELINE_DIFFERENTIAL_REPORT.md` | 15 | 3, 4, 84, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134 | `81a69c228c471b765cd519297338aed206ec87fe882486ac8cad49dff1b70d58` |
| `docs/sprints/SPR-018_P-018-01_VAL-004_WHEEL_REPLAY_REPORT.md` | 22 | 3, 4, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262 | `81a63d74781749f5f76d574b87bd9c1e0d090f158c0c4003e51bd35419f0fd23` |

The exact occurrence-level inventory, including logical content, previous line,
next line, file type, semantic effect, whitespace counts, classification, and
current file hash, is in
`docs/reviews/REV-004_REL2_R13_WHITESPACE_ALLOWLIST.csv`.

Allowlist SHA-256: `b6940a23ac228529ce1e85284c0877ae78ed297af4950290a101b69cc19ddf7f`.

## C. Classification

- `MARKDOWN_INTENTIONAL_HARD_BREAK: 154`
- `MARKDOWN_STRUCTURAL_OR_FUNCTIONAL: 0`
- `ACCIDENTAL_TRAILING_WHITESPACE: 0`
- `AMBIGUOUS_REQUIRES_HUMAN_DECISION: 0`
- `NON_MARKDOWN_INVALID_WHITESPACE: 0`

Every occurrence is in a Markdown file, consists of exactly two spaces, is not at
EOF, and is immediately followed by nonblank Markdown content. Context shows two
consistent intentional forms:

1. compact metadata lines at the beginning of institutional reports;
2. compact machine-readable result/status blocks whose line separation is
   deliberate.

No CSV, Python, TOML, README, fixture, tab, one-space, three-or-more-space, blank
line, or EOF occurrence survived the byte-accurate audit.

## D. Semantic test

For all 154 occurrences, the in-memory variant without the two final spaces
changes the Markdown construct from a hard break to a soft break. Depending on
the renderer, the soft break may collapse to an ordinary space. The logical text
tokens remain the same, but the deliberate visual record-per-line presentation is
lost.

No occurrence changes a table delimiter, fenced block, list nesting, code
indentation, CSV field, or executable content. The relevant semantic change is
exclusively the rendered line-break behavior.

## E. Hash preservation

The authoritative documents remain unchanged.

- ADR-007 canonical SHA-256:
  `e73c2f51c609a239aecb029a65bb01f3d4d10b6961fef909f76e2509f238cca2`
- VAL-003 canonical SHA-256:
  `7164e1839dc102110385c9f86af377ab36d6e433e246e5de98523fa77bccbdcc`
- VAL-004 canonical SHA-256:
  `a48a5ac699ee41ecd78a8ca1a4df22c18f6c11792bf83e39d64f471c99d0a4fe`
- FCP wheel SHA-256:
  `78c58f872b214d91e65a34045abcea57e633188ce1422457e78a6269235021dc`

`HASHES_PRESERVED: RECONCILED_CANDIDATE — PENDING_HUMAN_RE_RATIFICATION`

## F. Recommended policy

`RECOMMENDED_POLICY: POLICY_B — FUNCTIONAL_MARKDOWN_EXCEPTION`

All observed REL2-R13 whitespace is functional Markdown. Remediation is neither
required nor recommended because it changes rendering and would invalidate
applicable canonical hashes.

The exception is strict, applies only to the file/line entries in the allowlist,
and creates no repository-wide precedent.

## G. Substitute REL2-R13 gate

A reauthorized REL-002 should implement this verification without modifying the
working tree:

1. run `git diff --cached --check` and capture all whitespace diagnostics;
2. parse every diagnostic into repository-relative file and staged-file line;
3. load the REV-004 allowlist and verify its own SHA-256;
4. require every diagnostic to match exactly one allowlist row by file, line,
   two-space count, zero-tab count, logical line content, classification, and
   current file SHA-256;
5. reject tabs, EOF whitespace, non-Markdown whitespace, any count other than
   exactly two spaces, and every unlisted occurrence;
6. independently rescan staged blobs, not only working-tree files;
7. reject if an allowlisted line's content or file hash differs;
8. approve REL2-R13 only when the diagnostic set is an exact subset of the
   ratified functional rows applicable to the staged files and no other
   whitespace issue exists.

The gate must still run `git diff --cached --check`; the controlled comparison
interprets only the specifically ratified hard-break diagnostics.

## H. Decision

`REL2_R13_CAN_USE_CONTROLLED_EXCEPTION: YES — SUBJECT TO HUMAN RATIFICATION`
`REMEDIATION_REQUIRED: NO`
`REL_002_CAN_BE_REAUTHORIZED_AFTER_HUMAN_DECISION: YES`
`P_018_02_AUTHORIZED: NO`

`REV-004 COMPLETE — CONTROLLED MARKDOWN EXCEPTION RECOMMENDED`
