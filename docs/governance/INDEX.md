# CKO — Índice Canônico da Família GOV no CORE

## Identificação e autoridade

Este é o índice canônico da família documental GOV mantida no repositório
`CORE`. Sua autoridade deriva do
[GOV-009](GOV-009_GOVERNANCE_INDEX_AUTHORITY_RECONCILIATION.md) e constitui a
única autoridade de alocação de novos números GOV mantidos no CORE.

| Campo | Valor |
|---|---|
| Data de corte | 16/08/2026 |
| Autoridade derivada | GOV-009 |
| Escopo | Documentos GOV mantidos no CORE |
| Próximo número disponível | GOV-011 |

O índice institucional externo foi preservado sem alteração como instrumento
histórico reconhecido e degradado. Ele não é autoridade para novas alocações GOV
no CORE. Documentos externos não recebem links absolutos nem dependentes de letra
de unidade neste índice.

## Registro canônico

### GOV-001

NUMBER: GOV-001

TITLE: Baseline Arquitetural 1.0

PATH_OR_LOCATION_CLASS: EXTERNAL_INSTITUTIONAL_PREDECESSOR

STATUS: OFFICIAL / ACTIVE / PRESERVED

AUTHORITY: HUMAN-RATIFIED INSTITUTIONAL BASELINE PREDECESSOR

NOTES: Documento externo histórico; seu arquivo não integra o CORE, não foi
copiado e sua proveniência institucional permanece preservada.

### GOV-002

NUMBER: GOV-002

TITLE: Cycle II Execution Program

PATH_OR_LOCATION_CLASS: [docs/governance/GOV-002_CYCLE_II_EXECUTION_PROGRAM.md](GOV-002_CYCLE_II_EXECUTION_PROGRAM.md)

STATUS: OFFICIAL / ACTIVE

AUTHORITY: HUMAN-RATIFIED BY GOV-008; ACTIVE INDEX REFERENCE RECONCILED BY GOV-009

NOTES: Programa das ondas II.0–II.7; a reconciliação do índice não altera seu
escopo semântico nem autoriza implementação.

### GOV-003

NUMBER: GOV-003

TITLE: ADR Governance Reconciliation

PATH_OR_LOCATION_CLASS: [docs/governance/GOV-003_ADR_GOVERNANCE_RECONCILIATION.md](GOV-003_ADR_GOVERNANCE_RECONCILIATION.md)

STATUS: OFFICIAL / ACTIVE

AUTHORITY: HUMAN-RATIFIED BY GOV-008

NOTES: Governa a reconciliação administrativa, a numeração e o ciclo de vida da
família ADR.

### GOV-004

NUMBER: GOV-004

TITLE: NOT ASSIGNED

PATH_OR_LOCATION_CLASS: NO FILE / HISTORICAL GAP

STATUS: HISTORICAL_GAP / NOT_REUSABLE

AUTHORITY: HISTORICAL SERIES PRESERVATION; GOV-009

NOTES: Nenhum documento foi localizado no corte auditado. Nenhum título ou
conteúdo é atribuído, e o número não pode ser reutilizado.

### GOV-005

NUMBER: GOV-005

TITLE: Auditoria Histórica de Esforço do Projeto

PATH_OR_LOCATION_CLASS: [GOV-005_PROJECT_EFFORT_AUDIT.md](../../GOV-005_PROJECT_EFFORT_AUDIT.md)

STATUS: OFFICIAL EVIDENCE / HISTORICAL SNAPSHOT

AUTHORITY: HUMAN-RATIFIED CLASSIFICATION BY GOV-008

NOTES: Evidência analítica histórica, não norma material; permanece em seu
caminho real na raiz do CORE e não é movida por esta operação.

### GOV-006

NUMBER: GOV-006

TITLE: Project Dossier

PATH_OR_LOCATION_CLASS: [docs/governance/GOV-006_PROJECT_DOSSIER.md](GOV-006_PROJECT_DOSSIER.md)

STATUS: OFFICIAL / ACTIVE

AUTHORITY: HUMAN-RATIFIED BY GOV-008

NOTES: Dossiê institucional de corte; preserva a distinção entre fatos,
inferências, estimativas, baseline publicada e estado presente.

### GOV-007

NUMBER: GOV-007

TITLE: Repository Canonical Organization

PATH_OR_LOCATION_CLASS: [docs/governance/GOV-007_REPOSITORY_CANONICAL_ORGANIZATION.md](GOV-007_REPOSITORY_CANONICAL_ORGANIZATION.md)

STATUS: OFFICIAL / ACTIVE

AUTHORITY: HUMAN-RATIFIED BY GOV-008

NOTES: Define organização documental e a autoridade do índice de família, sem
autorizar migração ou OPS-005.

### GOV-008

NUMBER: GOV-008

TITLE: Cycle II Institutional Reconciliation

PATH_OR_LOCATION_CLASS: [docs/governance/GOV-008_CYCLE_II_INSTITUTIONAL_RECONCILIATION.md](GOV-008_CYCLE_II_INSTITUTIONAL_RECONCILIATION.md)

STATUS: HUMAN_RATIFIED / OFFICIAL / ACTIVE / CONSOLIDATED

AUTHORITY: EXPRESS HUMAN RATIFICATION

NOTES: Consolida a cadeia institucional e os status aplicados aos documentos
anteriores; não autoriza OPS-005 nem implementação técnica.

### GOV-009

NUMBER: GOV-009

TITLE: Governance Index Authority Reconciliation

PATH_OR_LOCATION_CLASS: [docs/governance/GOV-009_GOVERNANCE_INDEX_AUTHORITY_RECONCILIATION.md](GOV-009_GOVERNANCE_INDEX_AUTHORITY_RECONCILIATION.md)

STATUS: HUMAN_RATIFIED / ACTIVE

AUTHORITY: EXPRESS HUMAN RATIFICATION; GOVERNANCE INDEX AUTHORITY RECONCILIATION

NOTES: Cria este índice como autoridade canônica de alocação GOV no CORE,
preserva o índice externo e estabelece GOV-010 como próximo número disponível.

### GOV-010

NUMBER: GOV-010

TITLE: CKO Product Direction and Local Knowledge Finder MVP

PATH_OR_LOCATION_CLASS: [docs/governance/GOV-010_CKO_PRODUCT_DIRECTION_AND_LOCAL_KNOWLEDGE_FINDER_MVP.md](GOV-010_CKO_PRODUCT_DIRECTION_AND_LOCAL_KNOWLEDGE_FINDER_MVP.md)

STATUS: HUMAN_RATIFIED / ACTIVE

AUTHORITY: EXPRESS HUMAN RATIFICATION; PRODUCT DIRECTION DERIVED FROM EXE-001

NOTES: Formaliza a direção `LOCAL_FIRST / VALUE_ORIENTED / GOVERNED` e define o
CKO Local Knowledge Finder como primeiro MVP. Incorpora as conclusões da EXE-001;
implementação, AUD-MVP-001 e P-018-02 permanecem não autorizados.

## Regra de alocação e atualização

Novos números GOV mantidos no CORE somente podem ser alocados mediante atualização
atômica deste índice no mesmo commit do novo documento. Identificadores são
crescentes e imutáveis; números emitidos ou lacunas históricas não são
reutilizáveis. Toda entrada deve registrar `NUMBER`, `TITLE`,
`PATH_OR_LOCATION_CLASS`, `STATUS`, `AUTHORITY` e `NOTES`.

NEXT_AVAILABLE_GOV_NUMBER:

GOV-011

OPS_005_AUTHORIZED:

NO

P_018_02_AUTHORIZED:

NO
