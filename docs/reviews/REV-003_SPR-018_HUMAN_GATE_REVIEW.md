# CKO — REV-003 — SPR-018 Human Gate Review

**Natureza:** HUMAN GATE REVIEW / IMPLEMENTATION AUTHORIZATION DECISION
**Data:** 2026-08-12
**Escopo:** SPR-018, pacotes P-018-01 a P-018-05
**Autoridade desta decisão:** revisão humana solicitada à Release Authority
**Baseline protegida:** `CKO-BASELINE-2026.07`
**SDK/API protegidos:** `cko` 1.0.0; 646 exports, 646 nomes únicos, 646 símbolos resolvidos

Esta decisão não altera arquitetura, Core, API, baseline, RFC-002, REV-002, Sprint,
OPS-004/OPS-004R, repositório físico ou operação. Não autoriza produção, fonte real,
escrita, persistência, IAM, piloto, D4, D5 ou OPS-005.

## A. Estado inicial

O repositório canônico foi confirmado em `main`. O working tree já continha itens
locais não rastreados, inclusive os documentos da SPR-018, OPS-004/OPS-004R,
`.vscode/`, `inventory.txt`, `src/cko.egg-info/` e `src/main.py.txt`. Todos foram
preservados. Nenhuma operação Git mutante foi executada.

## B. HEAD, origin e baseline

- `git rev-parse --is-inside-work-tree`: `true`.
- branch: `main`.
- `HEAD`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`.
- `origin/main` local: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`.
- `ls-remote origin/main`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`.
- tipo de `CKO-BASELINE-2026.07`: `tag`.
- objeto da annotated tag: `ffa9cd23909c01e13cbc9926048dc69e12ff11fc`.
- peeled commit: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`.

## C. Documentos de autoridade examinados

Foram examinados os documentos locais vigentes relevantes: CKO-ARCH-002,
GOV-002, GOV-003, GOV-006, GOV-007, GOV-008, ADR-006, RFC-002, REV-001, REV-002,
SPR-018 Termo de Abertura, SPR-018 Technical Specification, SPR-018 Implementation
Readiness Matrix, Provenance Statements e AUD-001 a AUD-004. Também foram
consultados `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md` e as evidências de baseline.

Não foram localizados neste checkout documentos com os nomes CKO-GOV-001,
CKO-ARCH-001, REL-001, WS-001 ou artefatos documentais nomeados de SPR-017. A
ausência não foi tratada como aprovação. A fundação de Provenance existente e a
evidência de SPR-017 foram consideradas somente até onde materializadas nos
Provenance Statements, testes e referências vigentes.

## D. Definição reconstruída de D0–D4

| Gate | Significado canônico | Autoridade e evidência | Dependência e momento | Ratificação nesta operação |
|---|---|---|---|---|
| D0 | Autorizar o início do ciclo/trilha sob controles suficientes. | Governança/Release Authority; baseline, escopo, owners, superfícies, proteções, riscos e escalonamento. | Antes de trabalho executável da trilha. | **SIM, exclusivamente para a trilha transversal sintética P-018-01.** Não é D0 global nem de fonte. |
| D1 | Aceitar base de evidência/inventário por trilha. | Owner da fonte e autoridade de dados; cobertura, limites, autorização e Provenance reproduzível. | Antes de mapeamento e acesso/uso de fonte real. | **NÃO.** Faltam inventários aceitos e decisões de owners; não é necessário para codificar P-018-01. |
| D2 | Selecionar tratamento de capacidade: composição externa, legado, decisão futura ou encerramento. | Arquitetura e owners de domínio; matriz capacidade–contrato–consumidor e gaps. | Antes de composição/integracão da capacidade observada. | **NÃO globalmente.** Para P-018-01, a direção “fundação externa, sem API/Core” já é decisão explícita de ADR-006/RFC-002 e não requer inventário de fonte. |
| D3 | Autorizar preparação controlada de piloto para composição aprovada. | Arquitetura, segurança e dados; especificação, segurança, testes e rollback. | Depois da composição especificada e antes de piloto. | **NÃO.** Não há composição/piloto a ratificar; não é necessário para codificar P-018-01. |
| D4 | Homologar, repetir, rejeitar ou encerrar piloto supervisionado. | Owner do domínio e governança; métricas, testes, ausência de mutação/regressão e homologação humana. | Após piloto e antes de federação/homologação subsequente. | **NÃO.** Não existe piloto nem evidência; depende de decisão humana futura. |

D0 permanece `UNSATISFIED` globalmente, mas fica `SATISFIED_FOR_P-018-01_SCOPE_ONLY`
por esta decisão. D1–D4 permanecem globalmente `UNSATISFIED`. Nenhuma ausência de
evidência foi convertida em aprovação tácita.

## E. Estado de COND-001–COND-005

| Condição | Estado global | Suficiência por pacote |
|---|---|---|
| COND-001 | SATISFIED | Suficiente para P-018-01: schemas, tipos, cardinalidades, invariantes, erros, transições, fixtures e aceite estão especificados. Deve ser auditada em cada pacote. |
| COND-002 | PARTIALLY_SATISFIED | Não aplicável à codificação pura de P-018-01. Insuficiente para P-018-02/04 sem instância nominal por fonte/domínio/ato/vigência e tratamento de conflitos. |
| COND-003 | PARTIALLY_SATISFIED | Suficiente para negociação e validação abstratas de P-018-01. Valores numéricos de SLO/TTL/quota/backoff/revogação continuam necessários antes de P-018-03 e uso integrado. |
| COND-004 | PARTIALLY_SATISFIED | Regras abstratas bastam para P-018-01 sem I/O, identidade real ou telemetria. Trust/IAM, retenção, pseudonimização e incidente concretos continuam pendentes para P-018-02/03/04. |
| COND-005 | SATISFIED | Suficiente como regra; deve ser executada antes/depois de cada pacote. Qualquer diferença bloqueia e exige rollback. |

## F. Matriz PACKAGE × GATE

A matriz estruturada canônica desta decisão é
`REV-003_SPR-018_GATE_DECISION_MATRIX.csv`. Cada célula usa exatamente uma das
seis classificações permitidas.

Justificativas objetivas:

- contratos congelados e proteção 646 são pré-condições de qualquer código;
- autoridade nominal é pré-condição de lógica que execute atos institucionais,
  não de tipos puros;
- perfis numéricos são necessários quando resiliência deixa de ser schema e passa
  a governar integração;
- perfis concretos de IAM, retenção e pseudonimização antecedem identidade,
  evidência ou telemetria real;
- D1 pertence a inventário/fonte real; D2 a composição de capacidade observada;
  D3 à preparação de piloto; D4 à homologação posterior ao piloto;
- P-018-05 depende da evidência homologada dos pacotes anteriores, por isso D4 é
  pré-condição de sua implementação substantiva.

## G. Pendências de autoridade

Faltam instâncias nomeadas de autoridade, owner e steward por fonte, domínio, ato,
competência, vigência, delegação, precedência, bloqueio e escalonamento. Isso não
impede P-018-01, que não executa ato institucional, mas impede P-018-02 e qualquer
uso real posterior.

## H. Pendências de segurança

Trust boundaries abstratos estão definidos. Permanecem pendentes os mecanismos e
perfis concretos de IAM, credenciais com escopo/revogação, retenção por classe de
evento, pseudonimização por ambiente, redaction, tratamento de incidente e poder
de suspensão. São gates de P-018-02/04 ou de acesso real em P-018-03, não da
fundação pura P-018-01.

## I. Pendências operacionais

Permanecem sem aprovação numérica: SLO, deadline, TTL de idempotência, quota,
base/cap/tentativas de backoff, freshness, janela de reconciliação, prazo de
revogação, perfis de fonte e credenciais. São necessários para integração,
fontes reais e piloto; P-018-01 só pode representar e validar esses valores sem
fixar defaults operacionais.

## J. Avaliação específica de P-018-01

P-018-01 é externo ao Core, puro, determinístico, sem I/O, persistência,
transporte, IAM, credenciais, fontes reais, publicação ou autoridade executada.
Pode usar exclusivamente fixtures sintéticas. Os contratos e a estratégia de
testes estão suficientemente especificados; o rollback é a remoção da composição
externa. Não há gap P0 nem necessidade de alterar API/SDK.

**Decisão:** `AUTHORIZED_FOR_IMPLEMENTATION`.

Escopo autorizado: tipos lógicos, identidades, registros, quatro eixos de estado,
validação de lifecycle, negociação de versão/capacidade, validação estrita, erros
semânticos, serialização determinística e fixtures de contrato/conformidade.

Limites e localização conceitual: somente novos módulos de fundação externa em
`external/fcp/` e testes/fixtures dedicados em `tests/fcp/`, ou estrutura externa
equivalente previamente demonstrada; nunca `src/cko/`, packaging, build metadata
ou dependências. Esta autorização não decide reorganização física do repositório.

Operações proibidas: I/O, rede, banco, persistência, fonte/identidade/credencial
real, IAM, publicação, decisão institucional, escrita, importação reversa pelo
Core, novo export, mudança de assinatura ou dependência do Core para o FCP.

Testes obrigatórios: unitários de schemas/cardinalidades/transições; casos válidos
e inválidos; envelopes/erros; negociação e downgrade seguro; serialização
determinística; integração apenas em memória; regressão de dependências e
646/646/646 em fonte e artefato isolado; secret scan e comprovação de zero diff em
`src/cko`, versão, packaging, dependências e build metadata.

Gates posteriores: D1 antes de fonte real; D2 antes de composição com capacidade
observada; D3 antes de piloto; D4 antes de homologação/federação; perfis concretos
de COND-002/003/004 conforme o pacote consumidor. Rollback: remover/desabilitar o
artefato/composição externa e repetir regressão 646. Evidências: inventário de
schemas, vetores positivos/negativos, relatório contratual, serialização golden,
AST/dependency report, testes e fingerprint da API.

## K. Avaliação P-018-02

**Decisão:** `CONDITIONALLY_AUTHORIZABLE`.

Condições exatas: (1) aceite de P-018-01 com evidências; (2) matriz nominal de
autoridade aprovada por fonte/domínio/ato/vigência; (3) perfil concreto de trust,
IAM, retenção, pseudonimização, redaction e incidente; (4) fixtures de política
aprovadas sem identidade ou dado real; (5) auditoria prévia do pacote. Até isso,
nenhuma lógica de publicação, oficialização ou consulta pode ser codificada.

## L. Avaliação P-018-03

**Decisão:** `BLOCKED`.

Bloqueadores exatos: P-018-01/02 não aceitos; perfil numérico de SLO, TTL, quota,
backoff, retry, freshness e revogação não aprovado; ambiente isolado e perfis de
fonte ausentes; credenciais/autorização ausentes para fontes reais; D1/D2 da trilha
e D3 antes de piloto permanecem pendentes. Fakes não autorizam composição real.

## M. Avaliação P-018-04

**Decisão:** `BLOCKED`.

Bloqueadores exatos: P-018-01/02/03 não aceitos; mapping profile entre lifecycle
FCP e Provenance não aprovado; retenção, redaction, pseudonimização e autorização
por nó/aresta não aprovadas; instância de autoridade de conflito ausente.

## N. Avaliação P-018-05

**Decisão:** `BLOCKED`.

Bloqueadores exatos: inexistem evidências homologadas/auditadas de P-018-01 a 04,
rollback integrado e D4 aplicável. O pacote pode montar dossiê somente após essas
entradas e jamais decidir D5 automaticamente.

## O. PUBLIC_API_IMPACT

`PUBLIC_API_IMPACT: NONE`

P-018-01 deve permanecer externo e não requer importação, export, rebind ou
assinatura em `cko.core`.

## P. BREAKING_CHANGE

`BREAKING_CHANGE: NO`

Qualquer impacto detectado invalida esta autorização e bloqueia o pacote.

## Q. Decisão individual de cada pacote

- P-018-01: `AUTHORIZED_FOR_IMPLEMENTATION`.
- P-018-02: `CONDITIONALLY_AUTHORIZABLE`.
- P-018-03: `BLOCKED`.
- P-018-04: `BLOCKED`.
- P-018-05: `BLOCKED`.

## R. Arquivos criados

- `docs/reviews/REV-003_SPR-018_HUMAN_GATE_REVIEW.md`.
- `docs/reviews/REV-003_SPR-018_GATE_DECISION_MATRIX.csv`.

Nenhum código ou documento histórico foi alterado.

## S. SHA-256

Os hashes finais são reportados no encerramento da operação, após validação dos
dois artefatos. O conteúdo não deve ser alterado depois do cálculo sem gerar novos
hashes.

## T. Git status final

Será reportado no encerramento. Não haverá staging, commit ou push.

## U. Bloqueadores remanescentes

Continuam bloqueados: qualquer escopo além de P-018-01; fonte/credencial real;
autoridade/publicação/consulta; persistência/transporte; piloto/homologação; D5;
mudança no Core/API/SDK; e os perfis humanos concretos descritos nas seções G–I.

## V. Próxima ação recomendada

Iniciar uma implementação controlada somente de P-018-01, em mudança separada,
mantendo os limites e gates desta decisão. Antes de P-018-02, submeter as cinco
condições exatas da seção K à autoridade competente.

## W. Veredito final

`SPR-018 IMPLEMENTATION AUTHORIZATION PARTIALLY GRANTED`

`P-018-01 AUTHORIZED FOR IMPLEMENTATION`

P-018-01: `AUTHORIZED_FOR_IMPLEMENTATION`
P-018-02: `CONDITIONALLY_AUTHORIZABLE`
P-018-03: `BLOCKED`
P-018-04: `BLOCKED`
P-018-05: `BLOCKED`
