# CKO — REV-002 — RFC-002 Architectural Decision Review

**Status:** ARCHITECTURAL REVIEW / HUMAN-RATIFIED DECISION / NON-EXECUTABLE
**Objeto:** RFC-002 — Federated Catalog Protocol, versão 1.0-draft
**Data da revisão:** 12/08/2026
**Ratificação humana:** 12/08/2026
**Baseline protegida:** CKO-BASELINE-2026.07
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos
**Recomendação:** `APPROVE_WITH_CONDITIONS`
**Veredito:** `RFC-002 ARCHITECTURALLY APPROVABLE WITH CONDITIONS`

> Este parecer é exclusivamente documental. Não aprova implementação, não altera
> ADR, Sprint, SDK, API ou baseline e não autoriza implementação.

## Registro de ratificação humana

A recomendação `APPROVE_WITH_CONDITIONS` e o veredito deste parecer foram
**RATIFICADOS HUMANAMENTE** em 12/08/2026. A RFC-002 passa ao estado institucional
`APPROVED WITH CONDITIONS`. As condições COND-001, COND-002, COND-003, COND-004 e
COND-005 tornam-se vinculantes nos momentos e gates definidos na seção U.

Esta ratificação não satisfaz automaticamente as condições, D0–D4, especificações
por pacote, auditorias prévias ou autorizações de implementação. A SPR-018 permanece
`OPEN ADMINISTRATIVELY / TECHNICAL IMPLEMENTATION BLOCKED`.

## A. Estado inicial

O repositório estava em `main`, no marco REL-001 esperado. O worktree já continha
itens não rastreados anteriores à revisão: `.vscode/`, três artefatos OPS-004/004R,
`inventory.txt`, `src/cko.egg-info/` e `src/main.py.txt`. Eles foram tratados como
estado preexistente, não examinados como nova auditoria e preservados sem alteração.

## B. HEAD, origin e baseline

| Evidência | Valor | Resultado |
|---|---|---|
| branch | `main` | conforme |
| HEAD | `318c5584653fa3ecaa4dc6a66e19ce7352080bf0` | conforme |
| `origin/main` local | `318c5584653fa3ecaa4dc6a66e19ce7352080bf0` | conforme |
| `origin/main` remoto | `318c5584653fa3ecaa4dc6a66e19ce7352080bf0` | conforme |
| tag object | `ffa9cd23909c01e13cbc9926048dc69e12ff11fc` | conforme |
| peeled commit | `faa51ac6568dc2aa0e11d2333671b1098a1a89fa` | conforme |

Não houve sincronização, fetch, pull, checkout, reset ou alteração de histórico.

## C. Documentos analisados

Foram analisados integralmente os documentos obrigatórios: RFC-002, ADR-006,
índice canônico de ADRs, ARCH-002, GOV-002, GOV-003, GOV-006, GOV-007, GOV-008 e
o Termo de Abertura da SPR-018, nos caminhos indicados pelo corpus canônico.

Para compatibilidade do Ciclo I foram considerados os artefatos reais localizados:
`ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md`,
`CKO_CORE_V1_PUBLIC_API_CATALOG.md`, `CKO_CORE_BASELINE_EXECUTION_REPORT.md`,
`docs/architecture/CKO_CORE_BASELINE_2026-07-11.md`,
`SPR017_IMPLEMENTATION_REPORT.md`, `SPR017_HOMOLOGATION_REPORT.md`, a família
`CKO_PROVENANCE_STATEMENT_*`, `pyproject.toml` e `src/cko/core/__init__.py`.
CKO-GOV-001 não foi inventado nem localizado como arquivo neste repositório; sua
autoridade predecessora é registrada documentalmente por GOV-008 e pelas
referências normativas da RFC-002/ARCH-002.

## D. Objetivo reconstruído da RFC-002

O FCP resolve a descoberta governada de ativos distribuídos sem transferir
conteúdo, ownership ou autoridade. Separa fonte, observação, registro, projeção e
consulta; torna identidade, autoridade, acesso, confiança, conflitos e Provenance
explícitos; e define um protocolo lógico auditável, paginável, resiliente e
compatível, externo ao Core.

| Elemento | Classificação | Síntese |
|---|---|---|
| problema, contexto, motivação e fronteiras | DEFINED | federação governada sem consolidação física nem autoridade automática |
| atores e componentes | DEFINED | fonte, Aplicação, Adapter, Provider, autoridades, owner e steward |
| descoberta, admissão, publicação e consulta | DEFINED | fluxos, pré-condições e efeitos separados |
| identidade, estados, Provenance e versão lógica | DEFINED | identidades em camadas, quatro eixos de estado, append-only, `major.minor` |
| operações, resultados e invariantes | DEFINED | 15 operações, seis resultados normativos e invariantes explícitos |
| resolução, conflito, concorrência e idempotência | PARTIALLY_DEFINED | semântica arquitetural definida; schema e algoritmos ficam para especificações próprias |
| tipos concretos, schemas e catálogo estruturado de erros | PARTIALLY_DEFINED | envelopes e campos mínimos existem, mas sem representação executável |
| segurança e observabilidade | PARTIALLY_DEFINED | limites e comportamento fail-safe definidos; mecanismos e SLOs diferidos |
| transporte, persistência, IAM, índice, cache e topologia | OUT_OF_SCOPE | corretamente diferidos para instrumento próprio |
| escrita/sincronização bidirecional em fonte | OUT_OF_SCOPE | leitura é o padrão; mutação de fonte não é autorizada |

Não há funcionalidade essencial silenciosamente ausente no nível arquitetural da
RFC; há decisões operacionais deliberadamente delegadas às especificações dos
pacotes.

## E. Alinhamento com ADR-006

**Classificação global: `ALIGNED`.**

| Tema | Resultado | Evidência documental |
|---|---|---|
| autoridade federada e fonte de verdade | ALIGNED | RFC §§4.2, 12–16; ADR §§2, 3, 7 |
| identidade dos catálogos/ativos | ALIGNED | RFC §§5–7; ADR §10 |
| ownership e stewardship | ALIGNED | RFC §§7–9, 12, 14; ADR §§8–9 |
| resolução e conflitos | ALIGNED | RFC §§6, 11, 15; ADR §§10, 17 |
| delegação e precedência | ALIGNED | competência não é delegada a operador; bloqueios prevalecem |
| descoberta e governança | ALIGNED | descoberta não admite/publica; atos humanos permanecem separados |

A RFC materializa a decisão de que integração técnica não transfere autoridade.
Não foi encontrada divergência material. A identidade interna histórica
“ADR-001” no arquivo da ADR é preservada e administrada como ADR-006 por GOV-003,
INDEX e GOV-008; isso não é conflito técnico da RFC.

## F. Alinhamento com ARCH-002

**Classificação global: `ALIGNED`.** A RFC preserva separação de responsabilidades,
limites de domínio, interoperabilidade por capacidades, extensibilidade por versão,
composição externa e evolução incremental/reversível. Core permanece neutro;
Aplicações são composition roots; Adapters encapsulam conectividade; Providers
produzem observações sem autoridade. Não há acoplamento indevido ao Core, fonte,
transporte, persistência, produto ou tecnologia.

## G. Modelo de autoridade

1. A autoridade sobre o ativo permanece na fonte e nos órgãos competentes; atos
   institucionais pertencem às autoridades específicas, com owner e steward.
2. É representada por `AuthorityAssertion`, escopo, competência e vigência, além
   das decisões append-only.
3. É descoberta por `SourceDescriptor`, metadados de responsabilidade e matriz de
   autoridades aprovada por fonte/domínio.
4. Conflitos são explícitos e encaminhados à autoridade competente; não há votação,
   fusão ou escolha automática.
5. Não existe autoridade global substantiva do catálogo.
6. Existe autoridade local por fonte, ativo, domínio e ato.
7. Delegação operacional é possível dentro de escopo/vigência, sem transferência
   implícita de competência; sua forma concreta requer a matriz do pacote.
8. Há fallback fail-safe: indeterminação, conflito ou indisponibilidade não promove
   cache/projeção nem amplia acesso.
9. Split-brain é evitado por identidade qualificada, versões imutáveis,
   precondição otimista, conflitos explícitos e ausência de merge automático.
10. Provenance é append-only e acompanha observação, transformação e decisão.
11. Autoridade qualifica decisões sobre identidades, mas não reescreve identidade
    da fonte.
12. O modelo é deterministicamente conservador: conflito/indeterminação falha
    fechado. A seleção concreta da autoridade aplicável depende da matriz P1.

## H. Contratos do protocolo

| Área | Avaliação | Observação |
|---|---|---|
| identificadores | SUFFICIENT | identidades institucionais, qualificadas e de declaração separadas |
| tipos e estruturas | PARTIAL | entidades e envelopes mínimos definidos; schema/tipos concretos diferidos |
| estados e transições | SUFFICIENT | eixos ortogonais, guardas e efeitos definidos |
| comandos, consultas e respostas | SUFFICIENT | operações, entradas, saídas, efeitos e resultados normativos definidos |
| erros | PARTIAL | classes semânticas definidas; catálogo estruturado e exposição por operação faltam |
| invariantes | SUFFICIENT | invariantes centrais e fail-safe explícitos |
| resolução e precedência | PARTIAL | não fusão e bloqueios definidos; matriz/algoritmo por domínio faltam |
| versionamento e compatibilidade | SUFFICIENT | major/minor, negociação e extensões desconhecidas definidos |
| idempotência e concorrência | PARTIAL | chave, precondição e resultado desconhecido definidos; duração/deduplicação faltam |

O contrato é suficiente como arquitetura de referência, mas não deve ser
codificado diretamente sem as especificações P1 dos pacotes.

## I. Identidade e versionamento

`record_id` é estável, opaco e não reutilizável; `source_id + local_id` preserva a
identidade de origem; revisão do ativo e alegações têm identidade própria. Colisão
gera conflito, nunca overwrite. O FCP usa versão lógica `major.minor`, negocia a
interseção de capacidades e exige major para mudança semântica ou nova obrigação.
Upgrade/downgrade seguro depende de interseção compatível; downgrade que prejudique
segurança, Provenance ou semântica é recusado. Evolução aditiva é arquiteturalmente
possível sem quebrar consumidores existentes.

## J. Consistência e concorrência

A RFC define versões publicadas imutáveis, correção append-only, precondição da
última versão, conflito sem perda, resultados parciais, cobertura, validade,
timeout com resultado desconhecido, retry não cego, paginação estável, cache sem
autoridade e isolamento por fonte. Duplication é contida por idempotency key e
identidades não reutilizáveis. Permanecem P1: escopo temporal da chave, token de
versão, ordenação de eventos concorrentes, política de retry/backoff/timeout,
freshness e prazos de revogação. Isso é proporcional ao desenho e não exige um
sistema distribuído mais complexo que o escopo.

## K. Proveniência

A RFC preserva e amplia semanticamente — sem modificar — as garantias homologadas
da SPR-017: origem, identidade, agentes, atividade, timestamp, entradas,
transformações, resultado, evidência, autoridade e acesso. Cada transição relevante
gera declaração identificável e append-only; correções usam
`supersedes_statement`; lacunas permanecem explícitas e traces respeitam acesso.
Não há redução das garantias do Provenance Statement existente.

## L. Segurança

| Risco | Severidade | Controle/pendência |
|---|---|---|
| spoofing de fonte/autoridade | HIGH | identidade qualificada, autenticação externa e assertions; mecanismo concreto é P1 |
| ampliação de acesso/inferência | HIGH | interseção de políticas, filtro antes de contagem e negativa segura |
| replay/duplicação decisória | MEDIUM | idempotency key, version precondition e consulta segura; janela é P1 |
| alteração/sobrescrita | HIGH | imutabilidade, append-only, conflito otimista e evidência de integridade |
| exposição em logs/Provenance | HIGH | minimização e políticas do trace; esquema de redaction é P1 |
| falha de nó/autoridade indeterminada | MEDIUM | `partial`/`unavailable`, fail-safe e isolamento |

Não foi identificado risco CRITICAL intrínseco à proposta. Autenticação, IAM e
trust establishment concretos não devem ser improvisados; são gates P1.

## M. Observabilidade

Correlação, resultado, instante, cobertura, fontes, políticas, Provenance, erros e
decisões fornecem base diagnosticável e auditável. Eventos e logs são requisito
arquitetural; métricas, tracing e SLOs são aplicáveis conforme risco. Nomes de
eventos, cardinalidade, redaction, retenção e métricas/SLOs pertencem às
especificações dos pacotes, sem exposição de existência ou conteúdo protegido.

## N. Compatibilidade com SDK 1.0.0

Módulos existentes potencialmente reutilizáveis apenas por seus contratos públicos:
`identity`, `metadata`, `relationships`, `query`, `index`, `corpus`, `provenance`,
`contracts`, `exceptions`, `logging` e `composition`. Não se deve reinterpretar
nenhum deles como autoridade do catálogo.

Superfície futura conceitual: um conjunto externo à árvore `cko.core`, dividido em
modelos lógicos FCP, portas de `Discovery/Admission/Publication/Query/Provenance`,
Adapters/Providers por fonte e composition root de Aplicação. A RFC não exige novo
export público do SDK. Qualquer proposta de promoção ao Core ou novo export exige
decisão arquitetural separada e gate `BEFORE_PUBLIC_API_CHANGE`.

## O. Impacto sobre 646 exports

Evidência convergente: catálogo público, ARCH-001 v1.2, relatório de implementação
e homologação da SPR-017 registram 610 exports preservados + 36 de Provenance,
totalizando 646 entradas, nomes únicos e símbolos resolvidos. O código declara
`cko.core.__version__ = "1.0.0"`. A RFC congela essa superfície.

**Impacto previsto: `NO_PUBLIC_API_IMPACT`.** Uma implementação externa pode ser
estritamente aditiva fora do SDK sem alterar os 646 exports. Não há breaking change
obrigatório.

## P. Testabilidade

Registro, descoberta, resolução, conflito, falha, duplicação, idempotência,
versionamento, autoridade e Provenance possuem comportamentos esperados deriváveis.
Fixtures fixas, golden files, contrato por interface, falha parcial, precondição de
versão, rastreabilidade e regressão 646/646/646 permitem testes determinísticos.
Valores concretos de timeout, retry, validade e matriz de autoridades devem ser
congelados em cada especificação para eliminar variação de teste.

## Q. Relação RFC-002 × SPR-018

| SPR018_REQUIREMENT | RFC002_SUPPORT | STATUS | GAP | BLOCKING |
|---|---|---|---|---|
| P-018-01: modelo, identidades, estados e negociação | §§4–11, 17 | suportado | schemas concretos | antes do pacote |
| P-018-02: autoridade, publicação e consulta | §§7–15, 21 | suportado | matriz/políticas concretas | antes do pacote |
| P-018-03: federação e resiliência | §§11–15, 19 | suportado | SLOs e algoritmos operacionais | antes do pacote |
| P-018-04: Provenance e conflitos | §§6, 11, 16, 19 | suportado | perfil de mapeamento/redaction | antes do pacote |
| P-018-05: conformidade e dossiê D5 | §§18–20 | suportado | evidência depende dos pacotes | antes de D5 |
| preservar baseline/SDK/API | §17 e critérios de teste | suportado | nenhuma lacuna arquitetural | sim, se divergir |
| D0–D4 e autorizações | reconhecidos como precedência | externo à RFC | decisões ainda devem ser comprovadas | sim para implementação |

Gates diretamente dependentes da RFC-002: aprovação como critério de entrada,
especificações P-018-01 a 05, matrizes requisito–teste–evidência, homologações por
pacote e dossiê D5. Ratificação da RFC não satisfaz D0–D4 nem autoriza código.

## R. Lacunas P0

**Nenhuma.** Não há ambiguidade que impeça aprovação arquitetural, conflito com
ADR-006/ARCH-002, quebra obrigatória da baseline ou duas arquiteturas materiais
incompatíveis autorizadas simultaneamente.

## S. Lacunas P1

1. Schema lógico executável, tipos, cardinalidades e catálogo de erros por operação.
2. Matriz de autoridade/delegação/precedência por fonte, domínio, ato e vigência.
3. Política concreta de optimistic concurrency, idempotência, retry e resultado
   desconhecido.
4. Perfis de versão/serialização, extensão e negociação por participante.
5. Trust establishment, autenticação, autorização, redaction e retenção aplicáveis.
6. SLOs de timeout, freshness, revalidação, revogação e retirada.
7. Contrato de observabilidade seguro e matriz requisito–teste–evidência.

## T. Lacunas P2 e P3

P2: nomes de classes concretas, bibliotecas, formato de configuração, nomes de
métricas, layout de fixtures, algoritmo de backoff e detalhes de deployment.

P3: escrita bidirecional, persistência/índice canônico, operação em escala,
promoção ao Core e expansão de classes/fontes além da federação delimitada.

## U. Condições

### COND-001 — Contratos executáveis por pacote

- **Descrição:** congelar schemas, tipos, cardinalidades, invariantes, erros e
  transições aplicáveis ao pacote.
- **Justificativa:** elimina decisões semânticas durante codificação.
- **Prioridade:** P1.
- **Momento:** `BEFORE_SPR018_IMPLEMENTATION`.
- **Gate:** entrada de P-018-01 e pacote correspondente.
- **Impacto se ausente:** implementações incompatíveis e testes não conclusivos.

### COND-002 — Matriz determinística de autoridade

- **Descrição:** registrar por fonte/domínio/ato autoridades, owner, steward,
  delegação, vigência, precedência, bloqueios e escalonamento de conflitos.
- **Justificativa:** concretiza o modelo federado sem transferir competência.
- **Prioridade:** P1.
- **Momento:** `BEFORE_SPR018_IMPLEMENTATION`.
- **Gate:** D0–D4 aplicáveis e entrada de P-018-02.
- **Impacto se ausente:** decisão operacional indeterminada deve falhar fechada.

### COND-003 — Políticas de resiliência e versão

- **Descrição:** definir tokens de versão, escopo/TTL de idempotência, recuperação
  após timeout, retry/backoff, ordenação, freshness, revogação e negociação.
- **Justificativa:** torna concorrência e falha parcial reproduzíveis.
- **Prioridade:** P1.
- **Momento:** `BEFORE_SPR018_IMPLEMENTATION`.
- **Gate:** entrada de P-018-03.
- **Impacto se ausente:** duplicação, stale data ou divergência não determinística.

### COND-004 — Perfil de segurança e observabilidade

- **Descrição:** aprovar trust boundaries, autenticação/autorização, minimização,
  redaction, retenção, eventos, métricas e SLOs por perímetro.
- **Justificativa:** impede vazamento e autoridade falsificada.
- **Prioridade:** P1.
- **Momento:** `BEFORE_SPR018_IMPLEMENTATION`.
- **Gate:** entrada de P-018-02/03/04.
- **Impacto se ausente:** pacote não pode acessar fonte ou produzir evidência real.

### COND-005 — Proteção explícita da API pública

- **Descrição:** manter FCP externo ao Core e executar inventário/regressão
  646/646/646 antes e depois; qualquer promoção ou export exige ADR própria.
- **Justificativa:** preserva SDK 1.0.0 e contratos homologados.
- **Prioridade:** P1.
- **Momento:** `BEFORE_PUBLIC_API_CHANGE` e `BEFORE_RELEASE`.
- **Gate:** compatibilidade por pacote, P-018-05 e D5.
- **Impacto se ausente:** potencial breaking change e bloqueio automático.

Nenhuma condição precisa ser satisfeita antes da ratificação arquitetural; todas
controlam a transição da arquitetura aprovada para implementação/homologação.

## V. Riscos arquiteturais

| Risco | Nível | Tratamento |
|---|---|---|
| especificação de pacote divergir da RFC | HIGH | rastreabilidade e auditoria prévia |
| operador adquirir autoridade de fato | HIGH | COND-002 e fail-safe |
| inferência/vazamento por consulta | HIGH | COND-004 e filtro pré-agregação |
| comportamento concorrente divergente | MEDIUM | COND-003 |
| acoplamento/promover FCP ao Core | HIGH | COND-005 |
| stale cache tratado como verdade | MEDIUM | validade, revogação e Provenance |

## W. Gates RFC-R0 a RFC-R17

| Gate | Resultado | Fundamentação |
|---|---|---|
| RFC-R0 | PASS | repositório, `main` e HEAD corretos |
| RFC-R1 | PASS | HEAD, tracking ref e remoto idênticos |
| RFC-R2 | PASS | tag object e peeled commit exatos |
| RFC-R3 | PASS | RFC localizada, íntegra e 1.0-draft |
| RFC-R4 | PASS | ADR-006 localizada; ACCEPTED/ACTIVE por registro canônico |
| RFC-R5 | PASS | ARCH-002 localizada; OFFICIAL/ACTIVE |
| RFC-R6 | PASS | GOV-002/003/008 coerentes e ratificadas |
| RFC-R7 | PASS | alinhamento ADR-006 = ALIGNED |
| RFC-R8 | PASS | alinhamento ARCH-002 = ALIGNED |
| RFC-R9 | PASS | baseline, SDK e API congelados |
| RFC-R10 | PASS | garantias da SPR-017 preservadas |
| RFC-R11 | PASS WITH CONDITIONS | contratos arquiteturais suficientes; concretização P1 exigida |
| RFC-R12 | PASS WITH CONDITIONS | fail-safe determinístico; matriz concreta P1 |
| RFC-R13 | PASS WITH CONDITIONS | evolução compatível; perfis concretos P1 |
| RFC-R14 | PASS WITH CONDITIONS | testes deriváveis; parâmetros devem ser congelados por pacote |
| RFC-R15 | PASS | nenhuma lacuna P0 |
| RFC-R16 | PASS | dependências e bloqueios da SPR-018 determinados |
| RFC-R17 | PASS | nenhum arquivo preexistente alterado; apenas REV-002 criado |

## X. Recomendação arquitetural

`APPROVE_WITH_CONDITIONS`.

A RFC-002 está madura como fundamento arquitetural do FCP: é alinhada, compatível,
incremental, testável e não exige breaking change. As condições P1 não alteram a
decisão arquitetural; tornam-na executável com determinismo em cada pacote.

## Y. Respostas explícitas

- **A RFC-002 pode ser ratificada?** SIM.
- **A SPR-018 pode ser tecnicamente desbloqueada imediatamente após a ratificação?**
  NÃO. Além das condições deste parecer, dependem D0–D4 aplicáveis, especificação
  própria, auditoria prévia e autorizações expressas por pacote.
- **Existe algum bloqueador relacionado à OPS-005?** NÃO.
- **Existe algum bloqueador relacionado à organização física do repositório?** NÃO.
- **Existe algum breaking change obrigatório para implementar RFC-002?** NÃO.

## Z. REV-002 criado

Este documento é o único arquivo criado pela operação. Nenhum documento
preexistente foi modificado.

## AA. SHA-256

O SHA-256 será calculado após validação final de UTF-8, NUL, U+FFFD e whitespace e
será reportado no relatório de encerramento da operação. O arquivo não será
alterado após o cálculo.

## AB. Git status final

Deve mostrar os itens não rastreados preexistentes e este REV-002 como único novo
artefato da operação. Não houve staging, commit ou push.

## AC. Próxima ação recomendada

**satisfazer condições arquiteturais**.

Não iniciar automaticamente. Após ratificação humana, as condições devem ser
incorporadas às especificações e gates próprios dos pacotes da SPR-018.

## AD. Veredito

`RFC-002 ARCHITECTURALLY APPROVABLE WITH CONDITIONS`
