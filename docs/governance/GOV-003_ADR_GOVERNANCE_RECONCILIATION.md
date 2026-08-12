# CKO — GOV-003 — ADR Governance Reconciliation

**Status:** oficial
**Natureza:** governança documental
**Data:** 02/08/2026
**Escopo:** Architectural Decision Records do projeto CKO

## 1. Objetivo

Reconciliar a numeração dos ADRs, preservar a série histórica e instituir uma política permanente para identificação, registro e ciclo de vida das decisões arquiteturais.

Este ato não altera o conteúdo, o mérito, o status material nem a decisão de qualquer ADR. Não autoriza alteração de código, arquitetura ou baseline.

## 2. Inventário reconciliado

| Identificador canônico | Título | Ciclo | Status | Localização |
|---|---|---|---|---|
| ADR-001 | Monólito Modular Incremental | Ciclo Arquitetural I | Aceito | `docs/adr/ADR-001_MONOLITO_MODULAR_INCREMENTAL.md` |
| ADR-002 | Identidade Documental | Ciclo Arquitetural I | Aceito | `docs/adr/ADR-002_IDENTIDADE_DOCUMENTAL.md` |
| ADR-003 | Preservação dos Módulos Operacionais | Ciclo Arquitetural I | Aceito | `docs/adr/ADR-003_PRESERVACAO_DO_LEGADO.md` |
| ADR-004 | Banco Canônico Separado | Ciclo Arquitetural I | Aceito | `docs/adr/ADR-004_BANCO_CANONICO_SEPARADO.md` |
| ADR-005A-001 | Persistência Aditiva | Ciclo Arquitetural I | Aceito | `docs/decisoes/ADR-005A-001_PERSISTENCIA_ADITIVA.md` |
| ADR-006 | Federated Catalog Authority | Ciclo Arquitetural II | Aceito | `docs/adr/ADR-006_FEDERATED_CATALOG_AUTHORITY.md` |

O inventário abrange todos os arquivos identificados como ADR no repositório na data deste ato. `ADR-005A-001` é uma exceção histórica qualificada e ocupa, para fins de reserva, a família numérica 005.

## 3. Deliberação sobre o conflito

A série histórica **não será reorganizada**. Seus identificadores permanecem estáveis para preservar rastreabilidade, links, evidências e referências.

O documento *Federated Catalog Authority*, produzido no Ciclo Arquitetural II com a designação duplicada ADR-001, fica **registrado e renumerado administrativamente como ADR-006**. O arquivo é renomeado, mas seu conteúdo não é reescrito. As ocorrências internas de ADR-001 nesse artefato são designações de produção anteriores ao registro e não prevalecem sobre o identificador canônico ADR-006.

## 4. Autoridade do registro

O `docs/adr/INDEX.md` é a fonte canônica para identificador, título, ciclo, status e relações de ciclo de vida. Em caso de divergência com metadados internos de um ADR imutável, prevalece o índice, acompanhado do ato de governança que fundamentou a mudança administrativa.

Um ADR aceito ou encerrado permanece imutável. Mudanças posteriores de status, substituição ou aplicabilidade são registradas no índice e em novo ADR ou ato de governança; o documento histórico não é apagado nem reescrito.

## 5. Política permanente de numeração

1. Todo novo ADR recebe um identificador global no formato `ADR-NNN`, com no mínimo três algarismos.
2. A numeração é única, monotônica e independente de Ciclo Arquitetural, Sprint, produto, módulo ou diretório.
3. O próximo número é o sucessor do maior número ou família reservada no índice.
4. Números atribuídos nunca são reutilizados, inclusive quando o ADR é Rejeitado ou Withdrawn.
5. Identificadores qualificados históricos, como `ADR-005A-001`, permanecem congelados, mas esse formato não será usado em novos ADRs.
6. A reserva e o registro ocorrem no `INDEX.md` antes da circulação do novo ADR.
7. O nome de arquivo segue `ADR-NNN_TITULO_EM_SNAKE_CASE.md`.
8. Após esta reconciliação, o próximo identificador disponível é `ADR-007`.

## 6. Estados e relações de ciclo de vida

### Proposto

Decisão submetida, ainda sem força normativa. Pode evoluir antes da deliberação.

### Aceito

Decisão aprovada e vigente, salvo limitação expressa registrada no índice.

### Rejeitado

Proposta deliberada e não aprovada. Permanece como evidência histórica e seu número não é reutilizado.

### Superseded (substituído)

Aplica-se quando um ADR aceito posterior substitui integralmente uma decisão anterior. O novo ADR identifica o substituído; o índice registra a relação bidirecional `supersedes`/`superseded by`. O anterior deixa de reger novas decisões, mas permanece preservado.

Substituição parcial não recebe o status Superseded: o índice registra o escopo alterado e ambos os ADRs permanecem Aceitos nos respectivos limites.

### Deprecated (depreciado)

Indica decisão ainda reconhecida durante transição, mas desaconselhada para novos usos. O registro informa motivo, escopo, alternativa recomendada, responsável e critério ou prazo de saída. Deprecated não equivale a substituição.

### Obsoleto

Indica decisão que deixou de ser aplicável porque seu contexto, sistema ou premissa cessou, sem que outra decisão necessariamente a tenha substituído. Exige evidência de inaplicabilidade e registro da data e do ato que reconheceu o estado.

### Withdrawn (retirado)

Aplica-se somente a uma proposta retirada antes da aceitação. O ADR nunca teve força normativa. O motivo e a data ficam registrados, e o número não é reutilizado.

## 7. Transições permitidas

| Origem | Destino permitido |
|---|---|
| Proposto | Aceito, Rejeitado ou Withdrawn |
| Aceito | Deprecated, Superseded ou Obsoleto |
| Deprecated | Aceito, Superseded ou Obsoleto |
| Rejeitado | estado terminal |
| Superseded | estado terminal |
| Obsoleto | estado terminal |
| Withdrawn | estado terminal |

Reabertura de estado terminal exige novo ADR com novo identificador e vínculo explícito ao registro anterior.

## 8. Regras de substituição e preservação

- Nenhum ADR é apagado, renumerado ou reescrito após seu registro canônico.
- Toda substituição exige ADR posterior Aceito.
- O sucessor declara escopo, transição, compatibilidade e consequências.
- O índice conserva a cadeia completa entre predecessor e sucessor.
- Links e caminhos históricos são preservados ou redirecionados em reorganização meramente administrativa.
- Correções editoriais materiais são feitas por novo ADR ou errata governada, nunca por reescrita silenciosa de uma decisão aceita.

## 9. Resultado da reconciliação

- Ciclo Arquitetural I: ADR-001, ADR-002, ADR-003, ADR-004 e ADR-005A-001.
- Ciclo Arquitetural II: ADR-006.
- Série histórica: preservada.
- Novo ADR conflitante: renumerado administrativamente para ADR-006.
- Próximo identificador: ADR-007.
- Conteúdo e decisões dos ADRs: inalterados.
- Código: inalterado.
