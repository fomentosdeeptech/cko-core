# CKO Sprint Canonical Index

**Authority:** [GOV-007 — Repository Canonical Organization](../governance/GOV-007_REPOSITORY_CANONICAL_ORGANIZATION.md)
**Reconciliation date:** 2026-08-16
**Status:** canonical Sprint-family index

This index is the canonical navigation and allocation register for the CKO Sprint family. It was created by reconciling tracked repository content under the authority assigned by GOV-007. It does not rename, move, supersede, or infer the completion status of historical artifacts.

## Allocation rules

- Historical numbering is preserved. Missing or qualified identifiers are not reusable.
- A Sprint number may be allocated only after consulting and atomically updating this index under explicit human authority.
- Multiple reports, specifications, tests, or implementation records for one Sprint family are auxiliary evidence, not duplicate Sprint allocations.
- Unless a status is explicitly evidenced below, the neutral classification is `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION`.
- Planning does not authorize implementation. Every SPR-019 increment requires a separate human mandate.

## Reconciliation summary

```text
TRACKED_SPRINT_FILE_COUNT_IN_DOCS_SPRINTS: 12
OBSERVED_SPRINT_NUMBERS: SPR-003–SPR-018
LOWEST_OBSERVED_SPRINT_NUMBER: SPR-003
HIGHEST_OBSERVED_SPRINT_NUMBER_BEFORE_THIS_INDEX: SPR-018
HISTORICAL_SPRINT_GAPS: SPR-001 AND SPR-002 HAVE NO TRACKED PRIMARY ARTIFACT; NONE WITHIN SPR-003–SPR-018
RESERVED_SPRINT_NUMBERS: SPR-001–SPR-019
DUPLICATE_SPRINT_NUMBER_COUNT: 0
SPR_019_COLLISION_STATUS: NONE
```

`SPR-001` and `SPR-002` remain historically reserved pending a separate reconciliation; their absent primary artifacts do not make those numbers available. Qualified families observed in tracked names include `SPR-005A`, `SPR-006A`, `SPR-007B`, `SPR-008A` through `SPR-008W` (including `SPR-008OA`), `SPR-009A`, `SPR-017E`, `SPR-017G`, and the `P-018-*` increment family. These variants remain attached to their base number.

## Sprint register

| Sprint | Title or family | Primary plan or opening document | Reports and auxiliary evidence | Proven status |
|---|---|---|---|---|
| SPR-003 | Historical Sprint family | [Opening term](../sprint/CKO-SPR-003_TERMO_DE_ABERTURA.md) | [Family README](../../README_SPR_003.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-004 | Historical Sprint family | [Opening term](../sprint/CKO-SPR-004_TERMO_DE_ABERTURA.md) | [Report](../sprint/SPR004_REPORT.md), [family README](../../README_SPR_004.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-005 | Historical Sprint family, including SPR-005A | [Opening term](../sprint/CKO-CORE-SPR-005_TERMO_DE_ABERTURA.md); [SPR-005A official term](../sprint/CKO-SPR-005A_TERMO_OFICIAL.md) | [Report](../sprint/SPR005_REPORT.md), [architecture record](../architecture/CKO_CORE_ARQUITETURA_SPR005.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-006 | Historical Sprint family, observed as SPR-006A | [SPR-006A opening term](../sprint/CKO-CORE-SPR-006A_TERMO_DE_ABERTURA.md) | [SPR-006A report](../sprint/SPR006A_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-007 | Historical Sprint family, observed as SPR-007B | — | [SPR-007B report](../../reports/SPR007B_ADVANCED_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-008 | Historical qualified family SPR-008A–SPR-008W and SPR-008OA | — | [SPR-008A report](../../SPR008A_IMPLEMENTATION_REPORT.md) through [SPR-008W report](../../SPR008W_IMPLEMENTATION_REPORT.md), including [SPR-008OA report](../../SPR008OA_IMPLEMENTATION_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-009 | Historical Sprint family, including SPR-009A | — | [Implementation report](../../SPR009_IMPLEMENTATION_REPORT.md), [architecture certification](../../SPR009_ARCHITECTURE_CERTIFICATION_REPORT.md), [SPR-009A report](../../SPR009A_IMPLEMENTATION_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-010 | Historical Sprint family | — | [Implementation report](../../SPR010_IMPLEMENTATION_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-011 | Historical Sprint family | — | [Implementation report](../../SPR011_IMPLEMENTATION_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-012 | Historical Sprint family | — | [Implementation report](../../SPR012_IMPLEMENTATION_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-013 | Historical Sprint family | — | [Implementation report](../../SPR013_IMPLEMENTATION_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-014 | Historical Sprint family | — | [Implementation report](../../SPR014_IMPLEMENTATION_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-015 | Historical Sprint family | — | [Implementation report](../../SPR015_IMPLEMENTATION_REPORT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-016 | Historical Sprint family | — | [Implementation report](../../SPR016_IMPLEMENTATION_REPORT.md), [preimplementation audit](../../SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-017 | Historical Sprint family, including SPR-017E and SPR-017G | [Technical specification](../../SPR017_TECHNICAL_SPECIFICATION.md) | [Implementation report](../../SPR017_IMPLEMENTATION_REPORT.md), [homologation report](../../SPR017_HOMOLOGATION_REPORT.md), [audits and verification](../../SPR017G_VERIFICACAO_FINAL.md) | `HISTORICAL / STATUS NOT RECONCILED BY THIS OPERATION` |
| SPR-018 | Cycle II Sprint and P-018 increment family | [Opening term](SPR-018_TERMO_DE_ABERTURA.md), [technical specification](SPR-018_TECHNICAL_SPECIFICATION.md) | [Readiness matrix](SPR-018_IMPLEMENTATION_READINESS_MATRIX.csv), [P-018-01 implementation report](SPR-018_P-018-01_IMPLEMENTATION_REPORT.md), related P-018-01 validation reports in this directory | `AUTHORIZED / TECHNICAL EXECUTION CONDITIONED`; `P-018-02: NOT AUTHORIZED` |
| SPR-019 | CKO Local Knowledge Finder MVP Implementation | [Implementation plan](SPR-019_CKO_LOCAL_KNOWLEDGE_FINDER_MVP_IMPLEMENTATION_PLAN.md) | [P-019-01 validation report](SPR-019_P-019-01_PACKAGE_FOUNDATION_VALIDATION_REPORT.md); [P-019-02 validation report](SPR-019_P-019-02_SYNTHETIC_CORPUS_TEST_HARNESS_VALIDATION_REPORT.md) | `IN_PROGRESS / P-019-01 AND P-019-02 CONSOLIDATED` |

## Next allocation

```text
ALLOCATED_SPRINT_NUMBER: SPR-019
NEXT_AVAILABLE_SPRINT_NUMBER_AFTER: SPR-020
```

`SPR-020` is only the expected next number after this reconciliation. It is not allocated or authorized, and future allocation remains subject to an effective inventory and an atomic update of this index.
