# CKO — GOV-006 — Project Dossier

**Processo:** CKO — GOV-006 — Project Dossier
**Título institucional:** Dossiê Institucional do Projeto CKO
**Status:** vigente
**Versão:** 1.0
**Data de corte:** 03/08/2026, `America/Sao_Paulo`
**Natureza:** documento executivo e institucional; exclusivamente documental
**Repositório oficial:** `https://github.com/fomentosdeeptech/cko-core.git`
**Branch oficial:** `main`
**HEAD oficial observado:** `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
**Baseline publicada:** `CKO-BASELINE-2026.07`
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos
**Ciclo encerrado:** Ciclo Arquitetural I
**Ciclo em curso:** Ciclo Arquitetural II, em estágio documental e de preparação governada
**Escopo de mudança desta GOV:** criação deste documento, sem alteração de documento preexistente

> Este dossiê consolida o estado institucional do projeto no corte indicado. Ele
> não substitui arquitetura, ADR, RFC, GOV, termo de Sprint, especificação,
> auditoria, relatório, política, catálogo ou baseline existente. Em caso de
> divergência, prevalece o artefato canônico competente segundo sua matéria, seu
> status e a ordem de autoridade registrada neste documento.

---

## Sumário executivo

O CKO evoluiu de uma fundação de inventário, scanner e persistência para uma
plataforma de conhecimento organizada em torno do **CKO CORE SDK**, um monólito
modular orientado a domínio e estruturado segundo Ports and Adapters. O Ciclo
Arquitetural I formou o Core, consolidou a camada semântica de Knowledge Object
até Provenance Statement, estabilizou o SDK `cko` em 1.0.0 e publicou a baseline
`CKO-BASELINE-2026.07` sobre o commit
`faa51ac6568dc2aa0e11d2333671b1098a1a89fa`.

No corte institucional, a plataforma possui **26 componentes diretos em
`cko.core`**, **277 módulos Python de produção**, **43.929 linhas físicas de
código operacional**, **38 arquivos de teste**, **930 casos coletados na
regressão final documentada** e **646 exports públicos raiz**. A fotografia
documental auditada antes da GOV-005 continha 158 documentos Markdown canônicos
e 23.450 linhas físicas; a GOV-005 e este dossiê são acréscimos institucionais
posteriores e são discriminados na seção de indicadores.

O Ciclo Arquitetural II foi instituído documentalmente pela CKO-ARCH-002 e pelo
GOV-002. Seu modelo é de **federação governada**, composição externa,
Provenance by Design, autoridade preservada na fonte e evolução por ondas e
gates D0–D7. O ADR-006 foi aceito; a RFC-002 permanece proposta para aprovação;
a SPR-018 está formalmente aberta, mas sua execução técnica continua
condicionada. Nenhum artefato do Ciclo II observado neste corte altera o SDK
1.0.0, seus 646 exports ou a baseline publicada.

O ativo principal do projeto não é apenas o volume de código. É a combinação de
arquitetura, contratos, implementação modular, testes, especificações,
auditorias, decisões e mecanismos de homologação. Essa combinação torna o CKO
tecnicamente rastreável e institucionalmente governável, embora a reconstrução
temporal do esforço permaneça limitada por um histórico Git consolidado e pela
ausência de apontamento de horas.

## Como interpretar este dossiê

### Classes de informação

| Classe | Significado obrigatório neste documento |
|---|---|
| **Comprovada** | Contagem mecânica ou declaração sustentada por artefato canônico e evidência convergente. |
| **Inferida** | Conclusão lógica obtida de várias evidências, sem registro direto de mesma natureza. |
| **Estimada** | Valor derivado de modelo explícito e sujeito a faixa; não é valor contábil nem medição exata. |

Quando uma tabela não repete a classe em todas as linhas, a coluna
“Natureza/evidência” cumpre essa função. Termos como “atual”, “vigente” e
“publicado” são usados com cuidado:

- **baseline publicada** é o conteúdo protegido pelo tag
  `CKO-BASELINE-2026.07`;
- **estado presente** inclui documentos posteriores ou ainda não incorporados à
  baseline, observados no workspace no corte;
- **vigente** significa que o artefato possui força no seu escopo;
- **proposta** identifica artefato existente, mas ainda sem força normativa de
  aprovação;
- **aberta** não significa “implementada”, “homologada” ou “incorporada à
  baseline”.

### Ordem de autoridade

Para interpretar o estado consolidado, aplica-se a seguinte ordem material:

1. CKO-GOV-001 e a baseline publicada `CKO-BASELINE-2026.07`;
2. CKO-ARCH-001 e os contratos/evidências homologados do SDK 1.0.0;
3. CKO-ARCH-002, como arquitetura complementar do Ciclo II;
4. ADRs aceitos, conforme o índice canônico reconciliado pelo GOV-003;
5. programas e atos de governança vigentes, inclusive GOV-002, GOV-003,
   GOV-005 e este GOV-006;
6. RFCs aprovadas; RFCs propostas apenas informam intenção e especificação
   candidata;
7. termos, especificações e entregas de Sprint dentro dos limites expressamente
   autorizados.

---

## 1. História resumida do projeto

O projeto nasceu da necessidade de organizar ativos, documentos, metadados e
conhecimento sem destruir o legado nem concentrar decisões institucionais em
automação técnica. As primeiras entregas estabeleceram estrutura de repositório,
inventário, scanner, metadados, persistência e migrações. Em seguida, a série
SPR-008 formou progressivamente o núcleo modular: contratos, modelos, Discovery,
identidade, avaliação, planejamento, execução, runtime, conectores, storage,
checkpoint e Unit of Work.

A SPR-009 submeteu o Core a certificação arquitetural. A SPR-009A eliminou as
ressalvas prioritárias e consolidou o SDK 1.0.0. As SPR-010 a SPR-016 construíram
de forma aditiva a camada semântica — Knowledge Object, Document, Relationship,
Graph, Query, Index e Corpus. A SPR-017 acrescentou Provenance Statement após
especificação extensa, reprovação documental, reespecificação, nova auditoria,
verificação final, implementação e homologação.

O Ciclo I encerrou-se tecnicamente com 646 exports públicos e a publicação da
baseline. O Ciclo II começou como evolução arquitetural e institucional: o
Discovery do ecossistema foi convertido em arquitetura de federação governada,
programa por ondas, decisão sobre autoridade do catálogo, protocolo lógico
proposto e abertura condicionada da SPR-018. Até o corte, essa evolução não foi
promovida ao Core nem alterou sua superfície pública.

**Classificação:** síntese **comprovada** pelos documentos de Sprint, arquitetura,
governança, baseline e histórico Git; a ligação narrativa entre fases é
**inferida** a partir dessa cadeia.

## 2. Linha do tempo

| Data/fase | Evento consolidado | Estado | Classe |
|---|---|---|---|
| 11/07/2026 | Fundação do repositório, SPR-001, inventário, scanner e primeiro commit. | Fundação do Core. | Comprovada |
| 12/07/2026 | Persistência, migração, banco canônico, CVFs, releases e checkpoints das fundações. | Base operacional e histórica. | Comprovada por artefatos |
| 14–15/07/2026 | SPR-008A–I: Core canônico, assets, inventory, Discovery, identidade, capabilities e query foundation. | Núcleo modular em formação. | Comprovada |
| 17–19/07/2026 | SPR-008J–Q/OA: avaliação, índices lógicos, estatísticas, planner, optimizer, execution, runtime e workspace. | Crescimento aditivo. | Comprovada |
| 20–23/07/2026 | SPR-008R–W: connectors, storage, filesystem, SQLite, checkpoint e Unit of Work. | Portas e infraestrutura substituível. | Comprovada |
| 25/07/2026 | SPR-009 certifica com ressalvas; SPR-009A encerra P1 e consolida SDK 1.0.0. | 334 → 346 exports; 703 aprovações e duas falhas legadas. | Comprovada |
| 26–28/07/2026 | SPR-010–016 e auditorias: Knowledge, Document, Relationship, Graph, Query, Index e Corpus. | Camada semântica aditiva. | Comprovada |
| 29–30/07/2026 | Especificação SPR-017, auditoria com reprovação, reespecificação, nova auditoria e verificação final. | Gate documental convergente. | Comprovada |
| 31/07/2026 | Implementação/homologação da SPR-017, 646 exports, consolidação Git e baseline. | Ciclo I tecnicamente encerrado. | Comprovada |
| 02/08/2026 | CKO-ARCH-002, GOV-002, GOV-003, ADR-006 e RFC-002. | Ciclo II instituído documentalmente. | Comprovada |
| 03/08/2026 | SPR-018 formalmente aberta, com execução técnica condicionada. GOV-005 audita esforço histórico. | Planejamento governado; nenhuma implementação da SPR-018 comprovada. | Comprovada |
| 03/08/2026 | Criação deste dossiê institucional GOV-006. | Consolidação executiva, sem mudança técnica. | Comprovada |

## 3. Principais marcos

1. Instituição da Baseline Arquitetural 1.0 e da arquitetura canônica.
2. Preservação explícita do legado e adoção de evolução incremental.
3. Formação do monólito modular `cko.core` durante a família SPR-008.
4. Certificação arquitetural SPR-009 e correção das ressalvas na SPR-009A.
5. Publicação do SDK `cko` 1.0.0.
6. Construção da camada semântica completa de Knowledge Object a Corpus.
7. Reespecificação controlada e homologação de Provenance Statement na SPR-017.
8. Estabilização da API pública em 646 exports raiz, únicos e resolvidos.
9. Publicação do tag anotado `CKO-BASELINE-2026.07` sobre o HEAD oficial.
10. Instituição da arquitetura de federação governada para o Ciclo II.
11. Aceitação do ADR-006 sobre autoridade do Catálogo Federado Institucional.
12. Abertura condicionada da SPR-018, sem autorização irrestrita de código.
13. Produção da auditoria histórica GOV-005 e deste dossiê GOV-006.

Os itens 1–13 são **comprovados** pelos artefatos referenciados; “marco” é uma
qualificação institucional deste dossiê.

## 4. Evolução arquitetural

### 4.1 Da fundação ao Core modular

A arquitetura evoluiu de módulos operacionais e persistência inicial para um
monólito modular orientado a domínio. A decisão não foi de reescrita integral:
contratos passaram a envolver gradualmente capacidades existentes, com Ports and
Adapters, compatibilidade e rollback.

### 4.2 Da infraestrutura à semântica

Após consolidar execution, runtime, connectors, storage, checkpoint, UoW e
composition, o projeto adicionou uma cadeia semântica coerente:

```text
Knowledge Object
  -> Document
  -> Relationship
  -> Graph
  -> Query
  -> Index
  -> Corpus
  -> Provenance Statement
```

Essa cadeia não implica dependência rígida entre todos os módulos, mas representa
a progressão de capacidades e documentos arquiteturais das SPR-010–017.

### 4.3 Do Core ao ecossistema federado

O Ciclo II não expande automaticamente o Core. A unidade de evolução passa a ser
a composição externa por fronteiras: aplicações compõem jornadas; Providers
oferecem capacidades semânticas; Adapters encapsulam tecnologia; datasets e
corpora permanecem sob autoridade de origem; o Core conserva neutralidade.

**Classificação:** evolução **comprovada** por CKO-ARCH-001, revisões da
ARCH-001, CKO-ARCH-002 e relatórios; a representação em três estágios é
**inferida** para fins executivos.

## 5. Evolução da governança

| Fase | Instrumento predominante | Resultado institucional |
|---|---|---|
| Fundação | termos de abertura, políticas, inventários e relatórios | disciplina inicial de escopo, evidência e preservação |
| Baseline Arquitetural 1.0 | CKO-GOV-001 + CKO-ARCH-001 + Discoverys | arquitetura e critérios de evolução oficializados |
| Decisões do Ciclo I | ADR-001 a ADR-005A-001 | modularidade, identidade, legado, banco separado e persistência aditiva |
| Gates técnicos | especificações, auditorias, certificações e homologações | separação entre construir, testar, auditar e aceitar |
| Baseline técnica | consolidação/execução da baseline + tag | estado reproduzível e superfície protegida |
| Ciclo II | CKO-ARCH-002 + GOV-002 | ondas II.0–II.7, gates D0–D7 e federação governada |
| Reconciliação | GOV-003 + índice de ADRs | numeração global, status e imutabilidade histórica |
| Decisão/protocolo | ADR-006 + RFC-002 | autoridade aceita; protocolo ainda proposto |
| Execução futura | Termo da SPR-018 | autorização administrativa com implementação condicionada por pacote |
| Transparência institucional | GOV-005 + GOV-006 | esforço auditado e estado global consolidado |

Não foi localizado GOV-004 no corte auditado. A ausência é **comprovada por
busca**, mas não autoriza criação retroativa, renumeração ou preenchimento por
inferência.

## 6. Evolução do SDK

| Corte | Estado do SDK | Evidência/classificação |
|---|---|---|
| Fundação | módulos operacionais e estrutura inicial | Comprovada pelo commit inicial e acervo histórico |
| SPR-008 | formação incremental de `cko.core` | Comprovada pelos relatórios A–W/OA |
| SPR-009 | certificação com ressalvas | Comprovada pelo relatório de certificação |
| SPR-009A | versão `cko` 1.0.0 | Comprovada por relatório e `pyproject.toml` |
| SPR-010–016 | namespaces semânticos adicionados | Comprovada por código, relatórios e Git |
| SPR-017 | 15 módulos de provenance e 36 novos exports | Comprovada por implementação/homologação |
| Baseline | SDK 1.0.0 congelado no tag | Comprovada |
| Ciclo II | versão e empacotamento preservados | Comprovada documentalmente no corte; sem nova release técnica |

O número da versão permaneceu 1.0.0 enquanto a superfície evoluiu de forma
aditiva antes do congelamento da baseline. Este dossiê não reinterpreta SemVer
nem autoriza futuras adições sob a mesma versão.

## 7. Evolução da API pública

| Marco | Exports raiz | Evolução | Classe |
|---|---:|---|---|
| SPR-009 | 334 | fachada auditada antes da consolidação final | Comprovada |
| SPR-009A | 346 | +12 de exceções/composition | Comprovada |
| Pré-SPR-017 | 610 | crescimento aditivo nas SPR-010–016 | Comprovada pela homologação SPR-017 |
| SPR-017/baseline | 646 | 610 preservados + 36 de Provenance Statement | Comprovada |

O estado final foi validado nos relatórios por catálogo, AST, importação e smoke
de wheel. Valores intermediários entre 346 e 610 não são reconstruídos neste
dossiê porque nem todos os relatórios publicam a contagem raiz por Sprint.

## 8. Evolução dos testes

| Marco | Resultado cumulativo documentado |
|---|---:|
| SPR-008A | 9 aprovados |
| SPR-008F | 122 aprovados |
| SPR-008I | 224 aprovados |
| SPR-008R | 486 aprovados + 2 falhas legadas |
| SPR-008W | 686 aprovados + 2 falhas legadas |
| SPR-009A | 703 aprovados + 2 falhas legadas |
| SPR-010 | 732 aprovados + 2 falhas legadas |
| SPR-015 | 850 aprovados + 2 falhas legadas |
| SPR-017 final | 928 aprovados + 2 falhas legadas |

No corte auditado existem 38 arquivos `test_*.py`, 659 funções estáticas de teste,
16.131 linhas físicas de testes e 930 casos coletados na regressão final
documentada. As duas falhas históricas conhecidas referem-se ao argumento
`calculate_hash` em `collect_metadata` e a um handle SQLite aberto no teardown
Windows. Os relatórios registram zero falha nova atribuída à SPR-017.

Esses resultados são **comprovados como evidência histórica**, mas não constituem
nova execução pela GOV-006. Cobertura agregada total não está comprovada por uma
medição única metodologicamente comparável.

## 9. Baseline publicada

| Atributo | Valor | Classe |
|---|---|---|
| Identificador | `CKO-BASELINE-2026.07` | Comprovada |
| Tipo de ref | tag Git anotado | Comprovada |
| Objeto tag | `ffa9cd23909c01e13cbc9926048dc69e12ff11fc` | Comprovada mecanicamente |
| Commit apontado | `faa51ac6568dc2aa0e11d2333671b1098a1a89fa` | Comprovada mecanicamente |
| Branch de referência | `main` | Comprovada |
| SDK | `cko` 1.0.0 | Comprovada |
| API | 646 exports raiz, únicos e resolvidos | Comprovada |
| Ciclo representado | encerramento técnico do Ciclo Arquitetural I | Comprovada documentalmente |

A baseline é uma referência imutável. Documentos do Ciclo II presentes após o
tag não integram automaticamente essa baseline, ainda que sejam vigentes no
estado institucional atual.

## 10. Estado atual da plataforma

No corte de 03/08/2026:

- o repositório oficial está em `main`, no HEAD oficial da baseline;
- o SDK publicado permanece em 1.0.0;
- a API pública protegida permanece em 646 exports;
- o Ciclo I está tecnicamente encerrado;
- a arquitetura do Ciclo II está oficial e vigente como complemento;
- o programa GOV-002 organiza o Ciclo II por ondas e gates;
- os seis ADRs do índice canônico estão aceitos;
- a RFC-001 e a RFC-002 existem, mas permanecem propostas e não autorizam
  implementação;
- a SPR-018 está formalmente aberta, com especificação permitida e execução
  técnica condicionada aos critérios de entrada de cada pacote;
- nenhuma implementação de SPR-018 foi comprovada no corte;
- a baseline, o SDK e a API não foram alterados pelos documentos do Ciclo II.

**Classificação:** fatos **comprovados** por Git e pelos documentos vigentes.

## 11. Arquitetura vigente

A arquitetura vigente é composta, sem substituição, por duas camadas:

1. **CKO-ARCH-001 — Arquitetura Canônica:** monólito modular orientado a domínio,
   Ports and Adapters, Core SDK compartilhado, aplicações consumidoras,
   infraestrutura substituível e dependências dirigidas ao núcleo;
2. **CKO-ARCH-002 — Ecosystem Evolution Architecture:** federação governada,
   composição antes de promoção, reutilização antes de construção, Provenance by
   Design, autoridade na fonte, read-before-write, mínimo privilégio,
   reversibilidade e evolução por evidência.

```text
Governança institucional
        |
Aplicações e composition roots
        |
CKO CORE SDK 1.0.0 — 646 exports protegidos
        ^
Providers e Adapters externos
        |
Datasets, corpora e fontes sob autoridade de origem
```

O diagrama é uma **síntese inferida** fiel às arquiteturas. Não cria novo
componente, contrato ou direção de dependência.

## 12. Governança vigente

| Instrumento | Status no corte | Função |
|---|---|---|
| CKO-GOV-001 | vigente | institucionaliza a Baseline Arquitetural 1.0 e políticas de evolução |
| GOV-002 | vigente | programa de execução do Ciclo II, ondas, gates e precedências |
| GOV-003 | vigente | reconcilia inventário, numeração e ciclo de vida dos ADRs |
| GOV-005 | auditoria vigente como evidência | consolida esforço, métricas, limitações e confiança |
| GOV-006 | vigente | consolida o estado institucional sem substituir fontes especializadas |
| Políticas de Git, mudança, restore, versionamento e checkpoint | vigentes em seus escopos | controles operacionais e de preservação |

Princípios de governança em vigor: mudança material exige instrumento apropriado;
documento não autoriza código implicitamente; evidência de teste não equivale a
homologação humana; autoridade institucional não é transferida por integração;
artefatos históricos não são reescritos; a baseline só muda por processo formal.

## 13. ADRs vigentes

O `docs/adr/INDEX.md`, reconciliado pelo GOV-003, é a fonte canônica de
identificador, título, ciclo e status.

| ADR canônico | Decisão | Ciclo | Status |
|---|---|---|---|
| ADR-001 | Monólito Modular Incremental | I | Aceito |
| ADR-002 | Identidade Documental | I | Aceito |
| ADR-003 | Preservação dos Módulos Operacionais | I | Aceito |
| ADR-004 | Banco Canônico Separado | I | Aceito |
| ADR-005A-001 | Persistência Aditiva | I | Aceito |
| ADR-006 | Federated Catalog Authority | II | Aceito |

O arquivo do ADR-006 conserva internamente a designação histórica “ADR-001”. O
GOV-003 o renumerou administrativamente como ADR-006 sem reescrever o conteúdo;
prevalece o índice. O próximo identificador disponível é ADR-007.

## 14. RFCs vigentes no corpus

“Vigentes no corpus” significa presentes e relevantes para navegação; não
significa aprovadas.

| RFC | Tema | Status | Efeito institucional |
|---|---|---|---|
| RFC-001 | Project Workspace Automation Module (PWAM) | Proposta, prioridade baixa, horizonte futuro | não normativa; implementação não autorizada; não define a SPR-018 |
| RFC-002 | Federated Catalog Protocol | Proposta para aprovação, versão `1.0-draft` | especifica protocolo lógico; não cria contrato no SDK nem autoriza implementação |

Assim, há **duas RFCs localizadas e zero RFCs comprovadamente aprovadas** no
corte. A SPR-018 trata a aprovação da RFC-002 como critério de entrada.

## 15. Roadmap vigente

O roadmap executivo vigente do Ciclo II é o GOV-002, derivado da CKO-ARCH-002:

| Onda | Finalidade resumida | Situação no corte |
|---|---|---|
| II.0 — Preservação | fixar baseline, autoridades e controles | base documental estabelecida |
| II.1 — Inventário federado | mapear fontes, owners, fronteiras e capacidades | direção definida; execução não comprovada |
| II.2 — Contratos e mapeamentos | mapear capacidades aos contratos existentes | futura e condicionada |
| II.3 — Adapters e Providers | especificar composições externas substituíveis | futura e condicionada |
| II.4 — Pilotos supervisionados | validar integrações delimitadas | futura e condicionada |
| II.5 — Federação de conhecimento | executar federação delimitada | SPR-018 aberta; execução técnica condicionada |
| II.6 — Consolidação de evidências | reunir evidências e deliberar | futura; depende de D5 |
| II.7 — Escala governada | expandir somente padrões homologados | futura e condicionada |

O `ROADMAP.md` rastreado na baseline registra corretamente o corte anterior, no
qual a SPR-018 ainda não possuía termo. O Termo de Abertura posterior atualiza o
estado presente sem reescrever o roadmap histórico e sem alterar a baseline.

## 16. Resumo das Sprints

| Família/incremento | Entrega predominante | Estado |
|---|---|---|
| SPR-001 | fundação do repositório, inventário e scanner | concluída |
| SPR-003–007B | arquitetura, metadados, persistência, migração, auditoria e motores iniciais | concluídas conforme corpus histórico |
| SPR-008A–I | Core, asset model, inventory e fundações de Discovery | concluídas |
| SPR-008J–Q/OA | evaluation, índices, estatísticas, planning, optimization, execution, runtime e workspace | concluídas |
| SPR-008R–W | connectors, storage, adapters, checkpoint e UoW | concluídas |
| SPR-009/009A | certificação, correções P1 e SDK 1.0.0 | concluídas |
| SPR-010 | Knowledge Object | homologada na linhagem macro |
| SPR-011 | Document | homologada na linhagem macro |
| SPR-012 | Relationship | homologada na linhagem macro |
| SPR-013 | Graph | homologada na linhagem macro |
| SPR-014 | Query | homologada na linhagem macro |
| SPR-015 | Index | homologada na linhagem macro |
| SPR-016 | Corpus | homologada na linhagem macro |
| SPR-017 | Provenance Statement | tecnicamente homologada |
| SPR-018 | Federação de conhecimento/FCP externo | aberta; implementação condicionada; não homologada |

A auditoria GOV-005 identifica **41 incrementos concluídos** quando os sufixos
são tratados como unidades e a SPR-018 como a 42ª unidade nomeada. Essa contagem
é **inferida**, pois a taxonomia histórica contém lacunas e granularidades
diferentes; o número institucional seguro de linhagens macro homologadas é “até
SPR-017”, não “17 relatórios formais independentes”.

## 17. Principais componentes

Os 26 componentes/pacotes diretos comprovados sob `cko.core` são:

| Grupo executivo | Componentes |
|---|---|
| Fundamentos | `contracts`, `models`, `identity`, `metadata`, `exceptions`, `logging`, `config`, `utils` |
| Operação e descoberta | `inventory`, `discovery`, `workspace`, `execution`, `runtime` |
| Integração e consistência | `connectors`, `storage`, `checkpoint`, `uow`, `composition` |
| Semântica | `knowledge`, `documents`, `relationships`, `graph`, `query`, `index`, `corpus`, `provenance` |

“Componente” significa pacote direto do monólito modular, não serviço implantável
independente.

## 18. Principais módulos

Há **277 arquivos Python sob `src`**, dos quais 43 são `__init__.py` e 234 são
módulos de implementação. Além de `cko.core`, a árvore preserva módulos
operacionais e de compatibilidade em `cko.api`, `cko.classifier`,
`cko.contracts`, `cko.kb`, `cko.metadata`, `cko.migrations`, `cko.models`,
`cko.organizer`, `cko.persistence`, `cko.repository`, `cko.scanner`,
`cko.services` e `cko.utils`.

Os módulos de maior relevância institucional agrupam-se em:

- fachadas e contratos públicos;
- modelos, identidade, metadados, erros e eventos;
- Discovery, inventário, avaliação, planning, optimization e execution;
- runtime, workspace e composition root;
- conectores, abstrações de storage, filesystem e SQLite;
- checkpoint e Unit of Work;
- modelos/serviços semânticos de Knowledge, Document, Relationship, Graph,
  Query, Index, Corpus e Provenance.

A lista é **comprovada** quanto à estrutura; a seleção de “maior relevância” é
**inferida** para orientar novos leitores.

## 19. Principais capacidades

| Capacidade | Estado consolidado |
|---|---|
| Inventário e scanner | presentes desde a fundação e preservados |
| Identidade e metadados | contratos/modelos canônicos e evolução documentada |
| Discovery | contratos, providers, streaming, resolução, avaliação, índices, estatísticas e planejamento |
| Execução | planner, optimizer, engine, runtime e controles associados |
| Persistência | legado preservado, banco canônico separado e persistência aditiva |
| Integração | connectors e adapters por portas; tecnologias concretas fora do domínio |
| Consistência | checkpoint, Unit of Work e composição |
| Conhecimento semântico | Knowledge Object, Document, Relationship, Graph, Query, Index e Corpus |
| Proveniência | Provenance Statement homologado e transversal |
| API/SDK | pacote 1.0.0 com 646 exports públicos protegidos |
| Governança | baseline, ADRs, RFCs, ondas, gates, auditorias e homologação humana |
| Federação futura | arquitetura, autoridade e protocolo lógico documentados; implementação ainda condicionada |

## 20. Patrimônio intelectual produzido

O patrimônio técnico e documental produzido compreende:

1. arquitetura canônica, suas revisões e arquitetura de evolução do ecossistema;
2. decisões arquiteturais e políticas permanentes de governança;
3. SDK modular, contratos, modelos, motores, adapters e camadas semânticas;
4. catálogo de API pública, matrizes de dependência, exceções, logging e
   composition root;
5. especificações técnicas, guias de modelo, serialização, APIs e operações;
6. suítes de teste, fixtures, evidências de regressão, build e cobertura por
   entrega;
7. termos, relatórios de implementação, certificações, homologações e auditorias;
8. Discoverys, inventários, roadmaps e análises de prontidão;
9. baseline Git anotada e cadeia de consolidação reproduzível;
10. modelos institucionais de federação, autoridade, ownership, stewardship,
    confiança, acesso e Provenance.

Essa enumeração descreve **ativos intelectuais produzidos**. Ela não constitui
parecer jurídico sobre autoria, titularidade, licenciamento, patenteabilidade ou
valor econômico.

## 21. Indicadores do projeto

| Indicador | Valor de referência | Natureza/evidência |
|---|---:|---|
| Ciclos arquiteturais | 2 | Comprovada |
| Sprints/incrementos concluídos | 41 | Inferida pela granularidade histórica |
| Sprint aberta | 1 (`SPR-018`) | Comprovada; sem implementação comprovada |
| ADRs canônicos | 6 | Comprovada pelo índice/GOV-003 |
| RFCs localizadas | 2 | Comprovada; ambas propostas |
| Commits alcançáveis | 13 | Comprovada mecanicamente |
| Tags/baselines Git | 1 | Comprovada mecanicamente |
| Releases técnicas canônicas do SDK | 1 (`1.0.0`) | Comprovada; pacotes históricos não são somados |
| Arquivos rastreados no HEAD | 471 | Comprovada mecanicamente no corte GOV-005 |
| Componentes diretos de `cko.core` | 26 | Comprovada mecanicamente |
| Módulos Python sob `src` | 277 | Comprovada mecanicamente |
| Módulos de implementação, sem `__init__.py` | 234 | Comprovada mecanicamente |
| Exports públicos raiz | 646 | Comprovada |
| Arquivos de teste | 38 | Comprovada mecanicamente |
| Funções estáticas de teste | 659 | Comprovada mecanicamente |
| Casos finais coletados | 930 | Comprovada como evidência histórica: 928 + 2 |
| Documentos Markdown canônicos pré-GOV-005 | 158 | Comprovada por caminho no GOV-005 |
| Documentos institucionais acrescentados depois desse corte | 2 (`GOV-005`, `GOV-006`) | Comprovada por caminho |
| Corpus Markdown canônico no fechamento da GOV-006 | 160 | Inferência aritmética rastreável; ver seção 22 |
| Relatórios nomeados no baseline CORE | 45 | Comprovada |
| Revisões da arquitetura mestra do Core | 3 | Comprovada |
| Eventos formais de revisão/certificação arquitetural | 4 | Inferida por artefatos |

## 22. Estatísticas técnicas

| Métrica | Valor | Regra/classe |
|---|---:|---|
| LOC Python de produção | 42.542 | linhas físicas; comprovada no GOV-005 |
| Scripts e migrações auxiliares | 1.387 | linhas físicas; comprovada no GOV-005 |
| LOC operacional total | 43.929 | soma das duas linhas anteriores; comprovada |
| Linhas físicas de testes | 16.131 | comprovada |
| Linhas não vazias de testes | 14.013 | comprovada |
| Linhas Markdown canônicas no fechamento da GOV-006 | 25.002 | 23.450 do corte pré-GOV-005 + 694 da GOV-005 + 858 desta GOV-006; comprovada por contagem física |
| Linhas Markdown canônicas pré-GOV-005 | 23.450 | comprovada por caminho no GOV-005 |
| Linhas Markdown institucionais adicionadas por GOV-005 e GOV-006 | 1.552 | soma mecânica de 694 + 858 linhas físicas |
| Inserções acumuladas no histórico Git | 78.822 | comprovada por `shortstat`; churn, não LOC corrente |
| Remoções acumuladas no histórico Git | 33 | comprovada por `shortstat` |
| API pública | 646 | 610 preservados + 36 Provenance; comprovada |
| Regressão final documentada | 930 | 928 aprovados + 2 falhas históricas |

As estatísticas são fotografias metodológicas, não medidas universais de
qualidade. Cópias em releases, checkpoints, instaladores e backups não são
somadas ao corpus canônico.

## 23. Esforço histórico

Não existe registro de horas de início/fim, agenda, time tracking ou folha de
ponto. O GOV-005 separa dois modelos:

| Modelo | Centro | Faixa | Classe | Interpretação correta |
|---|---:|---:|---|---|
| Esforço direto empregado | 160 h | 113–234 h | Inferido/estimado, confiança baixa-média | supervisão humana e execução assistida plausíveis em 18 dias ativos |
| Reposição convencional | 1.990 h | 1.490–2.735 h | Estimado, confiança média-baixa | custo técnico normalizado para reproduzir o acervo |

Equivalências em jornadas de oito horas: 20 dias-pessoa centrais para o modelo
direto e 248,8 dias-pessoa centrais para reposição convencional. O segundo valor
**não** é o tempo cronológico realizado; o primeiro **não** é comprovado por
apontamento.

Distribuição central estimada do modelo direto: arquitetura 22 h, documentação
30 h, desenvolvimento 58 h, homologação/testes 14 h, revisão técnica 10 h,
auditoria 16 h e governança 10 h.

## 24. Indicadores de maturidade

| Dimensão | Evidência | Leitura institucional | Classe |
|---|---|---|---|
| Arquitetura | duas arquiteturas complementares, 6 ADRs e 26 componentes | alta formalização de fronteiras | Inferida sobre fatos comprovados |
| Contratos | 646 exports catalogados e protegidos | superfície pública estabilizada | Comprovada |
| Qualidade | 930 casos finais documentados e gates por Sprint | validação ampla, com duas dívidas legadas explícitas | Inferida |
| Governança | baseline, políticas, ondas, gates, auditorias e homologação | maturidade institucional elevada para o estágio | Inferida |
| Documentação | corpus canônico extenso e especializado | alta densidade de conhecimento transferível | Inferida |
| Rastreabilidade técnica | relatórios, hashes, tag, commits de consolidação | forte por artefato | Inferida |
| Rastreabilidade temporal | 13 commits em apenas dois dias de commit, sem horas | limitada | Comprovada/inferida |
| Compatibilidade | 610 exports preservados na SPR-017 e baseline congelada | forte disciplina aditiva | Comprovada |
| Operação | falhas legadas e cobertura agregada sem medida única | maturidade ainda não plenamente demonstrada em produção | Inferida |
| Ciclo II | arquitetura e governança prontas; implementação não comprovada | maturidade documental anterior à maturidade operacional | Comprovada/inferida |

Não se atribui nível CMMI, TRL, ISO ou outro selo externo: nenhum processo de
certificação desse tipo foi comprovado.

## 25. Estado do Ciclo II

O Ciclo II está **instituído e governado**, porém ainda não consolidado como
entrega técnica. Seu estado é:

- CKO-ARCH-002: oficial e vigente;
- GOV-002: programa vigente com ondas II.0–II.7 e gates D0–D7;
- GOV-003: reconciliação vigente;
- ADR-006: aceito;
- RFC-002: proposta para aprovação, `1.0-draft`;
- SPR-018: aberta e autorizada administrativamente;
- especificação: permitida dentro do Termo;
- implementação: condicionada por pacote, precedências e aprovação da RFC-002;
- impacto no Core: nenhum comprovado;
- impacto no SDK/API/baseline: nenhum autorizado ou comprovado.

A SPR-018 está vinculada à onda II.5 e visa produzir evidências para o gate D5.
Ela não autoriza II.6, II.7 ou promoção automática de qualquer capacidade ao
Core.

## 26. Próximos passos

Os próximos passos institucionais, sem constituir autorização de execução, são:

1. deliberar formalmente sobre a RFC-002;
2. manter a SPR-018 bloqueada para implementação enquanto critérios de entrada
   não estiverem satisfeitos;
3. produzir e aprovar especificação própria para cada pacote P-018 antes de
   qualquer código;
4. comprovar isolamento externo ao Core, reversibilidade, segurança, acesso e
   preservação de autoridade;
5. fixar inventário mecânico de 646 exports antes/depois de qualquer futura
   execução autorizada;
6. executar testes contratuais, resiliência, segurança, Provenance e regressão
   somente em ambientes autorizados;
7. homologar e auditar cada pacote separadamente;
8. consolidar matriz requisito–teste–evidência para submissão ao D5;
9. resolver ou aceitar formalmente as duas falhas históricas antes de nova
   baseline técnica;
10. atualizar índices canônicos de GOV, RFC, Sprint, auditoria e homologação sem
    reescrever artefatos históricos;
11. registrar horas, responsáveis, datas e evidências em futuras Sprints;
12. publicar um snapshot métrico mecânico em cada futura baseline.

## 27. Glossário institucional

| Termo | Definição neste projeto |
|---|---|
| **CKO** | plataforma e ecossistema institucional de conhecimento; também nome da aplicação integradora conforme o contexto |
| **CKO CORE SDK** | núcleo técnico compartilhado, neutro e modular da plataforma |
| **Baseline** | referência publicada e imutável de código, contratos e evidências em um corte |
| **Ciclo Arquitetural** | período governado por arquitetura, objetivos e critérios de evolução próprios |
| **SPR/Sprint** | unidade formal de trabalho com escopo, gates, evidências e aceite definidos |
| **ADR** | registro de decisão arquitetural; torna-se normativo quando aceito |
| **RFC** | proposta/especificação para discussão e aprovação; não autoriza código por si só |
| **GOV** | ato, programa, auditoria ou consolidação de governança institucional |
| **Core** | contratos, modelos e motores neutros compartilhados no SDK |
| **Aplicação** | composition root responsável por jornadas, políticas contextuais e integração |
| **Adapter** | tradução entre portas/modelos e tecnologia ou fonte concreta |
| **Provider** | componente externo que apresenta capacidades ou observações semânticas |
| **Dataset** | conjunto de dados com finalidade, schema, origem, owner e ciclo de vida próprios |
| **Corpus Institucional** | coleção governada para uso de conhecimento; não se torna canônica automaticamente |
| **Knowledge Object** | unidade semântica de conhecimento com identidade e regras próprias |
| **Provenance** | evidência rastreável de origem, transformação, responsabilidade e decisão |
| **CMC** | autoridade/modelo canônico de conhecimento referido pela governança da plataforma |
| **Export público** | símbolo exposto pela fachada pública raiz do pacote `cko` |
| **Gate** | ponto formal de decisão baseado em evidências e autoridade definida |
| **Homologação** | aceite formal por autoridade competente; não se confunde com teste aprovado |
| **Federação governada** | integração de referências e capacidades distribuídas sem centralização ou transferência automática de autoridade |
| **Owner** | responsável pela autoridade e ciclo de vida do ativo em seu domínio |
| **Steward** | responsável por curadoria e qualidade delegadas, sem adquirir automaticamente autoridade |
| **Comprovado** | sustentado por contagem mecânica ou evidência canônica convergente |
| **Inferido** | conclusão lógica sustentada indiretamente |
| **Estimado** | resultado de modelo explícito sujeito a faixa e incerteza |

## 28. Mapa documental resumido

| Domínio | Artefatos principais | Localização canônica/observada |
|---|---|---|
| Baseline arquitetural | CKO-GOV-001, CKO-ARCH-001, DSC-001/002 | `../docs/governance`, `../docs/arquitetura` e `../docs/arquitetura/discovery` |
| Arquitetura do Core | ARCH-001 original, v1.1, v1.2, mapas e matrizes | raiz do repositório CORE |
| Arquitetura do Ciclo II | CKO-ARCH-002 | `docs/arquitetura/` |
| Governança do Ciclo II | GOV-002 e GOV-003 | `docs/governance/` |
| Auditoria de esforço | GOV-005 | raiz do repositório CORE no corte |
| Dossiê institucional | GOV-006 | `docs/governance/` |
| ADRs | índice, ADR-001–004, ADR-006 e ADR-005A-001 | `docs/adr/` e `docs/decisoes/` |
| RFCs | RFC-001 PWAM e RFC-002 FCP | `../docs/arquitetura/` e `docs/rfc/` |
| Sprints iniciais | termos e relatórios SPR-003–006A | `docs/sprint/` |
| Sprints de formação do Core | relatórios SPR-008A–W/OA e SPR-009/009A | raiz do CORE |
| Camada semântica | relatórios e famílias documentais SPR-010–017 | raiz do CORE |
| SPR-018 | Discovery/Scope histórico e Termo de Abertura vigente | raiz do CORE e `docs/sprints/` |
| Baseline técnica | relatórios de consolidação e execução | raiz do CORE |
| API e qualidade | catálogo de API, dependências, exceções, logging, testes/cobertura, certificação | raiz do CORE |
| Roadmap | `ROADMAP.md`, CKO-ARCH-002 e GOV-002 | raiz, `docs/arquitetura/` e `docs/governance/` |
| Políticas | mudança, Git, restore, versão, checkpoint e status | `../docs/governance/` |

O prefixo `..` indica o diretório institucional pai `CKO`, fora da raiz Git do
CORE, mas integrante do corpus canônico consultado pelo GOV-005.

## 29. Referências oficiais

### Baseline, arquitetura e governança

- `../docs/governance/CKO-GOV-001_BASELINE_ARQUITETURAL_1.0.md`
- `../docs/arquitetura/CKO-ARCH-001_ARQUITETURA_CANONICA.md`
- `../docs/arquitetura/discovery/DISCOVERY-ECOSYSTEM-001.md`
- `../docs/arquitetura/discovery/DISCOVERY-ECOSYSTEM-002.md`
- `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md`
- `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.1.md`
- `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md`
- `docs/arquitetura/CKO-ARCH-002_ECOSYSTEM_EVOLUTION_ARCHITECTURE.md`
- `docs/governance/GOV-002_CYCLE_II_EXECUTION_PROGRAM.md`
- `docs/governance/GOV-003_ADR_GOVERNANCE_RECONCILIATION.md`
- `GOV-005_PROJECT_EFFORT_AUDIT.md`

### Decisões e propostas

- `docs/adr/INDEX.md`
- `docs/adr/ADR-001_MONOLITO_MODULAR_INCREMENTAL.md`
- `docs/adr/ADR-002_IDENTIDADE_DOCUMENTAL.md`
- `docs/adr/ADR-003_PRESERVACAO_DO_LEGADO.md`
- `docs/adr/ADR-004_BANCO_CANONICO_SEPARADO.md`
- `docs/decisoes/ADR-005A-001_PERSISTENCIA_ADITIVA.md`
- `docs/adr/ADR-006_FEDERATED_CATALOG_AUTHORITY.md`
- `../docs/arquitetura/CKO-RFC-001_PROJECT_WORKSPACE_AUTOMATION_MODULE.md`
- `docs/rfc/RFC-002_FEDERATED_CATALOG_PROTOCOL.md`

### Baseline, API, testes e execução

- `CKO_CORE_BASELINE_CONSOLIDATION_REPORT.md`
- `CKO_CORE_BASELINE_EXECUTION_REPORT.md`
- `CKO_CORE_V1_PUBLIC_API_CATALOG.md`
- `CKO_CORE_V1_TEST_AND_COVERAGE_REPORT.md`
- `CKO_CORE_V1_RELEASE_CERTIFICATION.md`
- `SPR017_TECHNICAL_SPECIFICATION.md`
- `SPR017_TECHNICAL_SPECIFICATION_AUDIT.md`
- `SPR017E_NOVA_AUDITORIA_FORMAL.md`
- `SPR017G_VERIFICACAO_FINAL.md`
- `SPR017_IMPLEMENTATION_REPORT.md`
- `SPR017_HOMOLOGATION_REPORT.md`
- `docs/sprints/SPR-018_TERMO_DE_ABERTURA.md`
- `README.md`, `CHANGELOG.md`, `ROADMAP.md` e `pyproject.toml`

### Referência externa oficial

- Repositório: `https://github.com/fomentosdeeptech/cko-core.git`
- Branch: `main`
- Commit: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
- Tag: `CKO-BASELINE-2026.07`

## 30. Conclusões institucionais

O CKO concluiu o Ciclo Arquitetural I com um resultado material e verificável:
um SDK 1.0.0 modular, 646 exports públicos protegidos, uma camada semântica de
Knowledge Object a Provenance Statement, ampla suíte de testes documentada e uma
baseline Git publicada. A evolução foi predominantemente aditiva e acompanhada
por decisões, especificações, auditorias e homologação.

O projeto atingiu maturidade institucional suficiente para ser compreendido por
arquitetos, desenvolvedores, auditores, parceiros e investidores a partir de uma
visão consolidada. Essa maturidade decorre sobretudo da combinação entre ativos
técnicos e governança: o Core tem fronteiras; a API tem inventário; as mudanças
têm gates; as decisões têm registro; a baseline tem identidade; as incertezas de
esforço são declaradas.

O Ciclo II amplia a ambição do projeto sem reabrir o Core. Seu foco é integrar o
ecossistema por federação governada, preservar autoridade e provar reutilização
antes de promover capacidades. No corte, a arquitetura e a governança estão mais
maduras do que a execução: ADR-006 está aceito, RFC-002 aguarda aprovação e
SPR-018 está aberta sob condições estritas. Essa assimetria é deliberada e
constitui mecanismo de controle, não atraso técnico comprovado.

As principais limitações permanecem transparentes: o histórico Git foi
consolidado retrospectivamente, não existem horas comprovadas, a cobertura total
agregada não possui uma medição única e duas falhas históricas permanecem
registradas. Nenhuma dessas limitações invalida a baseline; todas orientam a
disciplina exigida para o próximo ciclo.

Institucionalmente, a plataforma encontra-se **estável no Ciclo I, protegida por
baseline e preparada documentalmente para evolução federada no Ciclo II**. Toda
evolução futura deve preservar a cadeia de autoridade, a neutralidade do Core, a
compatibilidade pública, a evidência determinística, a reversibilidade e a
homologação humana.

---

## Apêndice A — Justificativa da estrutura adotada

| Bloco | Razão institucional |
|---|---|
| Sumário e método | permite leitura executiva sem ocultar nível de evidência |
| História, timeline e marcos | fornece orientação cronológica para quem chega ao projeto |
| Evolução arquitetural, governança, SDK, API e testes | explica como o estado atual foi alcançado |
| Baseline e estado atual | separa referência publicada de documentos posteriores |
| Arquitetura, GOV, ADR, RFC e roadmap | explicita autoridade, status e limites normativos |
| Sprints, componentes, módulos e capacidades | traduz o acervo para uma visão técnica navegável |
| Patrimônio, indicadores e esforço | atende análise institucional, auditoria e investimento sem misturar fato e estimativa |
| Maturidade e Ciclo II | mostra prontidão, lacunas e restrições atuais |
| Glossário, mapa e referências | torna o documento autossuficiente como porta de entrada, sem substituir as fontes |
| Compatibilidade e declarações finais | prova o caráter exclusivamente documental do processo |

A estrutura privilegia a sequência **origem → evolução → estado → evidência →
direção futura**. Ela reduz a necessidade de conhecimento prévio, mas preserva
links conceituais para os documentos especializados.

## Apêndice B — Compatibilidade com a documentação vigente

| Superfície | Compatibilidade desta GOV-006 |
|---|---|
| CKO-GOV-001 | preserva baseline, critérios de mudança, autoridade institucional e imutabilidade histórica |
| CKO-ARCH-001 | preserva monólito modular, Ports and Adapters, dependência dirigida ao núcleo e legado |
| CKO-ARCH-002 | preserva federação governada, composição externa, autoridade na fonte e Provenance by Design |
| GOV-002 | preserva ondas II.0–II.7, gates D0–D7 e ausência de autorização implícita |
| GOV-003 | usa o índice canônico, ADR-006 e próximo identificador ADR-007 |
| GOV-005 | reutiliza métricas, classes de evidência, faixas de esforço e limitações sem reestimá-las ocultamente |
| ADR-001–006 | resume as decisões sem alterar texto, status, alcance ou relação histórica |
| RFC-001 | mantém status de proposta, horizonte futuro e implementação não autorizada |
| RFC-002 | mantém `1.0-draft`, proposta para aprovação e ausência de contrato/implementação no SDK |
| SPR-001–017 | preserva resultados e status documentados; não reabre Sprint homologada |
| SPR-018 | reconhece abertura administrativa e mantém todos os gates de entrada e execução por pacote |
| Baseline Git | não altera tag, commit, branch ou conteúdo rastreado da baseline |
| SDK 1.0.0 | não altera versão, módulo, dependência, build, comportamento ou empacotamento |
| API pública | preserva exatamente 646 exports; não cria, remove, renomeia, deprecia ou reinterpreta símbolo |
| Testes | não altera nem executa teste; usa somente contagem estática e evidência histórica |
| Roadmap histórico | qualifica o corte anterior do `ROADMAP.md` sem reescrevê-lo; usa GOV-002/Termo para o estado posterior |

Não foi identificada incompatibilidade material criada por este dossiê. Quando
fontes representam cortes temporais distintos, o documento registra ambos em
vez de corrigir retroativamente o artefato anterior.

## Apêndice C — Limitações e controle de confiança

1. Métricas técnicas têm confiança alta quando mecanicamente reproduzíveis.
2. Resultados de testes são evidência histórica; a GOV-006 não os reexecutou.
3. A contagem de Sprints é sensível a sufixos e lacunas históricas.
4. Datas de modificação não equivalem a horas trabalhadas.
5. Commits de consolidação não representam toda a cronologia de autoria.
6. Pacotes históricos e backups contêm duplicações e não entram nas métricas
   canônicas.
7. Horas diretas e horas equivalentes são modelos diferentes e não devem ser
   somados.
8. Documentos presentes fora do tag não integram automaticamente a baseline.
9. “Produzido” não significa “aprovado”; o status individual prevalece.
10. Este dossiê é definitivo como fotografia institucional do corte, não como
    congelamento de toda evolução futura.

## Apêndice D — Declaração de integridade do processo GOV-006

Durante a produção desta GOV-006:

- nenhum código foi implementado ou alterado;
- nenhum SDK, API pública, contrato ou comportamento foi alterado;
- nenhum teste foi criado, alterado ou executado;
- a baseline e o tag oficial não foram alterados;
- nenhum documento preexistente foi alterado;
- nenhum arquivo foi removido, movido ou renomeado;
- nenhum diretório foi reorganizado;
- nenhum arquivo foi adicionado ao staging;
- nenhum commit, push, merge, checkout, restore ou reset foi realizado;
- a única gravação realizada foi a criação de
  `docs/governance/GOV-006_PROJECT_DOSSIER.md`.

O SHA-256, o `git diff` e o `git status` finais são apresentados no fechamento
externo do processo. O hash não é inserido no próprio arquivo, pois isso mudaria
recursivamente o valor calculado.
