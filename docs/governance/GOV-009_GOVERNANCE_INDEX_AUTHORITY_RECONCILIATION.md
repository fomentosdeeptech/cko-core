# CKO — GOV-009 — Governance Index Authority Reconciliation

## A. Identificação

| Campo | Valor |
|---|---|
| Identificador | GOV-009 |
| Título | Governance Index Authority Reconciliation |
| Data | 15/08/2026 |
| Classe | Governança documental |
| Repositório canônico | `CORE` |
| Caminho canônico | `docs/governance/GOV-009_GOVERNANCE_INDEX_AUTHORITY_RECONCILIATION.md` |

GOV_009_STATUS:

HUMAN_RATIFIED / ACTIVE

## B. Autoridade humana

O responsável humano pelo projeto ratifica a decisão
`CREATE_CANONICAL_CORE_GOV_INDEX` e confere a esta GOV autoridade para criar o
índice canônico da família GOV mantida no CORE, reconciliar a referência ativa
do GOV-002 e definir a regra futura de alocação dessa família.

## C. Contexto da inconsistência cross-root

O índice histórico da família GOV reside fora do repositório Git canônico. Essa
topologia separou a autoridade de alocação do histórico versionável dos atos que
ela deveria governar e impediu que documento, índice e atualização normativa
fossem consolidados atomicamente no CORE.

## D. Resultado da AUD-GOV-001

A AUD-GOV-001 concluiu que a autoridade cross-root estava diagnosticada e que a
correção poderia ser proposta. Confirmou que o índice externo registrava apenas
GOV-001 e GOV-002, omitia GOV-003 e GOV-005–008, não registrava a lacuna GOV-004
e não oferecia commit, branch, rollback ou atomicidade conjunta com o CORE.

## E. Topologia institucional e Git

O diretório institucional externo `CKO/` não é repositório Git. `CKO/CORE` é o
único repositório Git canônico da plataforma. Atos GOV mantidos no CORE devem,
portanto, ter sua autoridade de alocação no próprio CORE, sem apagar a
proveniência dos documentos institucionais externos.

## F. Estado do índice externo

O índice externo permanece reconhecido como evidência histórica da governança
anterior. Ele não é modificado, movido, copiado nem revogado por esta operação.

EXTERNAL_INDEX_STATUS:

INSTITUTIONALLY_RECOGNIZED / DEGRADED / PRESERVED / NOT_AUTHORITY_FOR_NEW_CORE_GOV_ALLOCATION

## G. Decisão de criar índice canônico no CORE

Fica criado `docs/governance/INDEX.md` como índice canônico da família GOV
mantida no CORE, com autoridade derivada desta GOV-009.

CANONICAL_GOV_INDEX:

docs/governance/INDEX.md

CANONICAL_GOV_INDEX_AUTHORITY:

SOLE_ALLOCATION_AUTHORITY_FOR_GOV_DOCUMENTS_MAINTAINED_IN_CORE

## H. Escopo da autoridade do novo índice

O índice governa identificadores, títulos, localizações, status, autoridade,
notas de proveniência e o próximo número disponível para documentos GOV
mantidos no CORE. Ele não transforma automaticamente documentos externos em
arquivos do CORE e não altera a autoridade material de outros instrumentos.

## I. Tratamento dos GOVs anteriores

GOV-001 é registrado como predecessor institucional histórico externo, sem
cópia e sem link dependente de unidade. GOV-002, GOV-003 e GOV-005–008 são
registrados em seus caminhos reais, com classificação baseada no conteúdo e na
ratificação posterior do GOV-008. Nenhum documento anterior é reescrito, salvo
a reconciliação normativa estritamente localizada do GOV-002.

## J. Preservação da lacuna GOV-004

A ausência de GOV-004 já foi constatada no corpus auditado. O número integra o
histórico da série, não recebe título ou conteúdo inventado e jamais poderá ser
reutilizado.

GOV_004_STATUS:

HISTORICAL_GAP / NOT_REUSABLE

## K. Relação com GOV-002

O GOV-002 permanece `OFFICIAL / ACTIVE` e semanticamente inalterado. Sua única
mudança é substituir a referência normativa ativa ao índice externo pela
referência ao índice canônico no CORE, registrando a origem desta reconciliação.
Programa, ondas, gates, decisões técnicas e autorizações permanecem intactos.

## L. Relação com GOV-007

Esta decisão concretiza exclusivamente a previsão do GOV-007 de que o índice da
família é a autoridade de alocação. Não executa a reorganização documental geral,
não move arquivos e não atravessa os gates da migração canônica.

## M. Relação com GOV-008

Os status dos documentos anteriores seguem a ratificação humana consolidada no
GOV-008. Esta GOV acrescenta a reconciliação de autoridade do índice sem reabrir
as decisões D01–D08 nem alterar a cadeia institucional já reconhecida.

## N. Preservação de OPS-004, OPS-004R e OPS-005

OPS-004 e OPS-004R permanecem preservados em seus estados documentais atuais.
Esta operação não os reabre, não os executa e não altera seus artefatos. OPS-005
não é criado, iniciado ou autorizado.

OPS_005_AUTHORIZED:

NO

## O. Preservação das auditorias históricas

AUD-GOV-001 e todas as demais auditorias históricas permanecem evidências
imutadas. Esta GOV registra suas conclusões vinculantes sem reconstruir,
substituir, mover ou editar seus artefatos.

## P. Regras futuras de alocação GOV

Todo novo identificador GOV mantido no CORE deve ser crescente, imutável e
alocado pelo índice canônico. Números emitidos, retirados ou registrados como
lacuna não podem ser reutilizados. A alocação exige autoridade humana aplicável,
ausência de colisão e declaração explícita de status e escopo.

## Q. Regra de atomicidade

A criação de um GOV no CORE deve ocorrer no mesmo commit documental que sua
entrada no índice canônico e as referências normativas cuja atualização seja
expressamente autorizada. A atomicidade não amplia o escopo autorizado de cada
operação.

## R. Regra de atualização do índice

Nenhum número GOV pode ser considerado alocado para o CORE sem atualização
atômica de `docs/governance/INDEX.md`. Cada entrada deve registrar número,
título, caminho ou classe de localização, status, autoridade e observações.

## S. Destino futuro do índice externo

O índice externo permanece preservado como instrumento histórico degradado e em
transição. Qualquer arquivamento, anotação, migração ou substituição física futura
exige autorização própria; esta GOV não autoriza qualquer escrita nesse arquivo.

## T. Itens expressamente não autorizados

Esta GOV não autoriza migração documental geral, alteração de README ou ROADMAP,
mudança de código, testes, SDK, API pública, baseline, pacote, RFC-002, SPR-018,
OPS-004, OPS-004R, OPS-005, documento de direção de produto ou GOV-010.

## U. Próximo número disponível

Após a alocação atômica desta GOV-009, o próximo número disponível é GOV-010.
Esta declaração reserva a sequência administrativa, mas não cria nem autoriza o
documento correspondente.

NEXT_AVAILABLE_GOV_NUMBER:

GOV-010

## V. Impacto sobre o P-018-02

Esta reconciliação é exclusivamente documental. Ela não satisfaz gates técnicos,
não implementa o MVP e não concede autorização ao P-018-02.

P_018_02_AUTHORIZED:

NO

## W. Veredito

A autoridade de alocação da família GOV mantida no CORE passa a residir
exclusivamente em `docs/governance/INDEX.md`. O índice externo permanece íntegro,
reconhecido e degradado; GOV-004 permanece lacuna histórica não reutilizável; e
GOV-010 é o próximo número disponível, ainda não criado nem autorizado.
