# CKO — GOV-005 — Auditoria Histórica de Esforço do Projeto

**Data de corte:** 2026-08-03, `America/Sao_Paulo`
**Natureza:** auditoria histórica exclusivamente analítica
**Repositório canônico:** `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`
**Diretório complementar consultado:** `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO`
**Branch observada:** `main`
**HEAD observado:** `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
**Baseline observada:** tag `CKO-BASELINE-2026.07`, CKO CORE SDK `1.0.0`
**Modo:** leitura de todo o acervo; a criação deste relatório foi a única gravação realizada pela GOV-005

## Sumário executivo

O projeto CKO possui evidência material de atividade entre **2026-07-11 e
2026-08-03**, intervalo de **24 dias corridos inclusivos**. Foram identificados
**18 dias com evidência de trabalho** por data de modificação de artefatos, dos
quais 16 pertencem ao Ciclo Arquitetural I/baseline e dois ao início documental
do Ciclo Arquitetural II. Datas de modificação são evidência auxiliar, não folha
de ponto.

O histórico Git canônico é deliberadamente consolidado: há **13 commits**, um
único branch local/remoto visível (`main`), uma tag de baseline e somente dois
dias de commit. O repositório contém, porém, relatórios e arquivos datados ao
longo de todo o período. Por isso, os commits comprovam a consolidação, mas não
medem sozinhos o trabalho diário.

No corte anterior à criação desta GOV-005, o núcleo auditado apresentava:

- **471 arquivos rastreados** no baseline Git;
- **158 documentos Markdown canônicos por caminho**: 129 no CORE e 29 no
  diretório pai canônico, totalizando **23.450 linhas físicas**;
- **45 relatórios nomeados e rastreados** no baseline CORE; 46 no CORE presente,
  devido ao relatório JSON local adicional; há ainda relatórios históricos no
  diretório pai e em releases, tratados como evidência e não somados às métricas
  canônicas para evitar duplicação;
- **6 ADRs canônicos**, **2 RFCs localizadas** e **2 ciclos arquiteturais**;
- **41 incrementos de Sprint concluídos identificáveis** até a SPR-017 e uma
  SPR-018 administrativamente aberta, sem implementação;
- **277 módulos Python** sob `src` (234 arquivos de implementação, excluídos os
  43 `__init__.py`) e **26 componentes/pacotes diretos** sob `cko.core`;
- **42.542 linhas físicas de Python de produção**, mais 1.387 linhas em scripts
  e migrações auxiliares, perfazendo **43.929 linhas de código operacional**;
- **38 arquivos de testes**, **659 funções de teste estáticas** e **16.131 linhas
  físicas de testes**;
- **930 casos coletados** na regressão final documentada: 928 aprovados e duas
  falhas históricas conhecidas, sem regressão nova;
- **646 exports públicos raiz**, únicos e resolvidos: 610 preservados e 36
  adicionados pela SPR-017.

A estimativa primária de esforço diretamente empregado é **160 homem-horas**,
com intervalo plausível de **113 a 234 horas** e confiança baixa a média. Ela
representa supervisão humana e execução intensiva assistida inferidas dos 18 dias
ativos; não é tempo comprovado. Como referência econômica separada, a reprodução
convencional do mesmo acervo é estimada em **1.990 homem-horas equivalentes**,
faixa de 1.490 a 2.735 horas. Esse segundo número é custo técnico normalizado,
não afirmação de horas cronológicas efetivamente trabalhadas.

## 1. Escopo, fontes e regras de contagem

### 1.1 Fontes examinadas

Foram inspecionados, sem alteração:

1. histórico Git, refs, reflog, tag, objetos, `log`, `numstat`, status e árvore;
2. código de produção, scripts, migrações, configurações e testes;
3. relatórios de implementação, certificação, homologação e baseline;
4. termos de Sprint, manifests, logs e relatórios JSON;
5. arquiteturas ARCH-001, suas revisões e ARCH-002;
6. ADRs, RFCs, GOVs, políticas, roadmaps e catálogos;
7. releases, checkpoints e arquivos históricos do diretório pai;
8. evidências internas de contagem de testes, cobertura, build e API pública.

### 1.2 Universo primário e universo histórico

O **universo primário** é a árvore presente do CORE, acrescida dos 29 documentos
canônicos do diretório pai. O **universo histórico secundário** contém releases,
checkpoints, instaladores, backups e arquivos extraídos. Ele confirma fases
anteriores, mas contém muitas cópias dos mesmos arquivos. Seus caminhos não são
somados a linhas de código, documentos, módulos ou componentes correntes.

Essa separação evita transformar duplicação de pacote, backup ou release em
esforço novo.

### 1.3 Semântica das evidências

| Classe | Significado nesta auditoria |
|---|---|
| **Comprovado** | Contagem mecânica ou declaração corroborada por artefato canônico e evidência compatível. |
| **Inferido** | Resultado lógico de várias evidências, sem registro direto equivalente a folha de ponto. |
| **Estimado** | Faixa calculada por modelo explícito; não deve ser tratada como valor contábil exato. |

### 1.4 Regras métricas

- **Linha física:** cada linha do arquivo, incluindo branco e comentário. Linhas
  não vazias são apresentadas quando úteis, mas LOC principal é físico.
- **Documento:** arquivo Markdown canônico por caminho; cópias em release,
  checkpoint e backup não entram no total principal.
- **Módulo:** arquivo `.py` sob `src`; o número sem `__init__.py` também é dado.
- **Componente:** pacote direto sob `src/cko/core`, excluído `__pycache__`.
- **Teste:** função estática `test_*` e, separadamente, caso coletado documentado
  pelo pytest. Parametrização explica a diferença.
- **Sprint:** há duas granularidades. “Macro” é a família numérica; “incremento”
  preserva sufixos como 008A–008W, 008OA e 009A. 017E/017G são gates documentais,
  não novas Sprints.
- **Relatório:** arquivo cujo nome contém `REPORT`/`RELATORIO`; relatórios sem essa
  palavra são descritos à parte, sem alterar a contagem mecânica.

## 2. Estado Git e integridade histórica

### 2.1 Fatos Git comprovados

| Métrica | Valor | Classe |
|---|---:|---|
| Commits alcançáveis por todas as refs | 13 | Comprovado |
| Commits em 2026-07-11 | 1 | Comprovado |
| Commits em 2026-07-31 | 12 | Comprovado |
| Branches locais | 1 (`main`) | Comprovado |
| Branches remotos visíveis | 1 (`origin/main`) | Comprovado |
| Tags | 1 (`CKO-BASELINE-2026.07`) | Comprovado |
| Autores Git distintos | 1 | Comprovado |
| Arquivos rastreados no HEAD | 471 | Comprovado |
| Inserções acumuladas registradas | 78.822 | Comprovado pelo `shortstat` |
| Remoções acumuladas registradas | 33 | Comprovado pelo `shortstat` |
| Objetos inalcançáveis | 12 blobs; nenhum commit inalcançável | Comprovado |

O Git não contém branches de feature ou commits intermediários suficientes para
reconstruir sessão a sessão. O commit inicial foi feito em 11/07. Em 31/07, os
artefatos foram consolidados em dez commits de fundações/SPR-010–017, seguidos de
três commits documentais. O próprio relatório de execução da baseline confirma
que o estado inicial daquela consolidação possuía 462 entradas visíveis, das
quais 460 eram não rastreadas.

### 2.2 Consolidação por commit

| Marco Git | Arquivos | Inserções | Remoções | Interpretação |
|---|---:|---:|---:|---|
| SPR-001, 11/07 | 10 | 140 | 0 | Fundação inicial do repositório. |
| Fundações até SPR-009A | 282 | 51.788 | 9 | Grande consolidação retroativa do Ciclo I. |
| SPR-010 | 17 | 1.713 | 0 | Knowledge Object. |
| SPR-011 | 16 | 1.930 | 0 | Document. |
| SPR-012 | 17 | 2.107 | 0 | Relationships. |
| SPR-013 | 18 | 1.921 | 0 | Graph. |
| SPR-014 | 16 | 2.247 | 0 | Query. |
| SPR-015 | 21 | 1.758 | 0 | Index. |
| SPR-016 | 19 | 2.031 | 0 | Corpus. |
| SPR-017 | 30 | 6.926 | 0 | Provenance e dossiê técnico. |
| Reconciliação arquitetural/documental | 29 | 5.582 | 24 | Coerência transversal e baseline. |
| Relatório de execução | 1 | 677 | 0 | Registro controlado. |
| Qualificação histórica do preparo | 1 | 2 | 0 | Fechamento da governança da baseline. |

As 78.822 inserções Git são churn de consolidação, não LOC corrente: incluem
código, testes, documentação e arquivos que foram adicionados tardiamente ao
controle de versão.

## 3. Linha do tempo do projeto

| Data/fase | Evidência e evento | Situação |
|---|---|---|
| **11/07/2026** | Estrutura inicial, SPR-001, primeiro commit, inventário, scanner e documentação inicial. | Fundação comprovada. |
| **12/07/2026** | SPR-003–007B, persistência/migração, banco canônico, relatórios CVF, releases e checkpoints. | Execução comprovada por arquivos, logs e pacotes históricos. |
| **14/07/2026** | SPR-008A–008F: núcleo, modelo canônico, inventário e Discovery inicial. | 122 testes aprovados ao fim de 008F. |
| **15/07/2026** | SPR-008G–008I: identidade, capabilities e query foundation. | 224 testes aprovados. |
| **17–19/07/2026** | SPR-008J–008Q/008OA: evaluation, index lógico, estatísticas, planner, optimizer, execution e runtime/workspace. | API aditiva; regressão cresce para 446 aprovações. |
| **20–23/07/2026** | SPR-008R–008W: connectors, storage, filesystem, SQLite, checkpoint e Unit of Work. | 686 aprovados e duas falhas legadas. |
| **25/07/2026** | SPR-009 certifica com ressalvas; SPR-009A elimina P1 e consolida SDK 1.0.0. | 334 → 346 exports; 703 aprovações. |
| **26/07/2026** | SPR-010–015: Knowledge Object, Document, Relationship, Graph, Query e Index. | Camada semântica cresce de forma aditiva. |
| **28/07/2026** | SPR-016 Corpus; auditorias prévias da SPR-016 e SPR-017. | Gate da SPR-017 aprovado com ajustes. |
| **29/07/2026** | Especificação técnica da SPR-017 e auditoria formal com reprovação para reespecificação. | Revisão arquitetural/documental explícita. |
| **30/07/2026** | Nova auditoria formal e verificação final da especificação. | Reespecificação convergente. |
| **31/07/2026** | Implementação e homologação da SPR-017; 646 exports; baseline consolidada em 12 commits e tag. | Ciclo I tecnicamente encerrado. |
| **02/08/2026** | ARCH-002, GOV-002, GOV-003, ADR-006 e RFC-002. | Ciclo Arquitetural II instituído documentalmente. |
| **03/08/2026** | Termo da SPR-018 presente: planejamento/especificação autorizados; implementação condicionada. | Nenhum código de SPR-018 observado. |

## 4. Dias do projeto e dias trabalhados

### 4.1 Contagens

| Métrica | Valor | Classe | Método |
|---|---:|---|---|
| Dias corridos inclusivos | 24 | Comprovado/inferido | 11/07 a 03/08, inclusive. |
| Dias com artefato modificado | 18 | Inferido | Datas distintas de arquivos canônicos, excluídos `.git`, runtime, cache e egg-info. |
| Dias com commit | 2 | Comprovado | Datas distintas no `git log`. |
| Dias sem evidência canônica | 6 | Inferido | Diferença, não prova de ausência de trabalho. |

Datas ativas: **11, 12, 14, 15, 17, 18, 19, 20, 21, 23, 25, 26, 28, 29,
30 e 31 de julho; 2 e 3 de agosto**.

### 4.2 Gráfico cronológico descrito em texto

Cada bloco representa aproximadamente dez arquivos com a mesma data de
modificação no universo CORE filtrado; um ponto significa atividade menor que
dez arquivos. O gráfico mede densidade de artefatos, não horas.

```text
11/jul  ██████       63   Fundação e inventários
12/jul  ███          31   Persistência, migração, releases
14/jul  █████        51   SPR-008A–F
15/jul  █            14   SPR-008G–I
17/jul  ███          33   SPR-008J–N
18/jul  ███          31   SPR-008O–Q/OA
19/jul  ·             2   Continuidade/validação
20/jul  ·             7   Connectors
21/jul  ██           20   Storage/filesystem
23/jul  ███          27   SQLite/checkpoint/UoW
25/jul  ███          29   Certificação e SDK 1.0.0
26/jul  ██████████  105   Camada semântica SPR-010–015
28/jul  ██           20   Corpus e auditorias
29/jul  ·             1   Especificação extensa da SPR-017
30/jul  ██           16   Reauditoria e verificação
31/jul  ██████████████████████████ 263   Provenance e baseline Git
02/ago  █             6   Arquitetura/governança do Ciclo II
03/ago  ·             1   Abertura da SPR-018
```

O pico de 31/07 reflete principalmente consolidação Git e normalização de datas,
não criação instantânea de todo o conteúdo.

## 5. Evolução por Sprint

### 5.1 Quantidade

Foram identificados **41 incrementos concluídos** até a SPR-017:

- SPR-001;
- SPR-003, 004, 005, 005A, 006A e 007B;
- SPR-008A–008W e SPR-008OA, total de 24 incrementos;
- SPR-009 e 009A;
- SPR-010–017, oito incrementos.

A SPR-018 é a **42ª unidade nomeada no corpus corrente**, mas está apenas aberta
administrativamente e não conta como incremento técnico concluído. A ausência de
artefato canônico suficiente para SPR-002 e a existência histórica de 006B/007A
em releases mostram que a numeração não é uma sequência simples. Para a série
macro, a governança declara homologadas as fundações até 009A e as SPR-010–017;
esta auditoria não inventa uma contagem exata onde o corpus usa granularidades
diferentes.

### 5.2 Evolução funcional resumida

| Família | Resultado predominante |
|---|---|
| 001–007B | Estrutura, scanner/inventário, arquitetura, persistência, migração e motores iniciais. |
| 008A–I | CORE canônico, assets, inventory e fundações de Discovery. |
| 008J–Q/OA | Evaluation, índices lógicos, estatísticas, planning, optimization, execution, runtime e workspace. |
| 008R–W | Portas, adapters, checkpoint e transação/UoW. |
| 009/009A | Auditoria arquitetural, correção de P1 e release SDK 1.0.0. |
| 010–016 | Camada semântica: Knowledge, Document, Relationship, Graph, Query, Index e Corpus. |
| 017 | Provenance Statement, especificação revisada, implementação, testes e homologação. |
| 018 | Primeira Sprint do Ciclo II; somente planejamento/especificação condicionados. |

## 6. Evolução arquitetural

### 6.1 Ciclos

Há **2 ciclos arquiteturais comprovados**:

1. **Ciclo I:** formação e homologação do CKO CORE, encerrado na baseline
   `CKO-BASELINE-2026.07`;
2. **Ciclo II:** evolução federada governada, instituída em 02/08 por ARCH-002 e
   GOV-002, ainda em estágio documental no corte.

O GOV-002 define oito ondas II.0–II.7 e gates D0–D7. Ondas não são contadas como
ciclos nem como Sprints executadas.

### 6.2 Componentes e estrutura

Os **26 componentes diretos** de `cko.core` são: contracts, models, identity,
metadata, exceptions, logging, config, utils, inventory, discovery, workspace,
execution, runtime, connectors, storage, checkpoint, uow, composition,
knowledge, documents, relationships, graph, query, index, corpus e provenance.

Essa contagem é comprovada mecanicamente. “Componente” não significa serviço
implantável: o desenho é de monólito modular SDK, conforme ADR-001.

### 6.3 ADRs e decisões

O índice reconciliado pelo GOV-003 comprova **6 ADRs canônicos**:

| ADR | Decisão | Ciclo |
|---|---|---|
| ADR-001 | Monólito Modular Incremental | I |
| ADR-002 | Identidade Documental | I |
| ADR-003 | Preservação dos Módulos Operacionais | I |
| ADR-004 | Banco Canônico Separado | I |
| ADR-005A-001 | Persistência Aditiva | I |
| ADR-006 | Federated Catalog Authority | II |

Há cópias e ADRs alternativos em pacotes históricos; eles não prevalecem sobre o
índice canônico. O próximo identificador reservado é ADR-007.

### 6.4 RFCs

Foram localizadas **2 RFCs**:

- RFC-001, no diretório pai, proposta de Project Workspace Automation Module,
  não autorizada e não definidora da SPR-018;
- RFC-002, no CORE, Federated Catalog Protocol, versão `1.0-draft`, proposta para
  aprovação e sem autorização automática de implementação.

### 6.5 Revisões arquiteturais

Há **3 versões formais** da arquitetura mestra do Core — ARCH-001 original,
v1.1 e v1.2 — e **3 gates arquiteturais explicitamente nomeados**: certificação
SPR-009, auditoria pré-implementação SPR-016 e auditoria pré-implementação
SPR-017. A auditoria da especificação da SPR-017 constitui ainda uma quarta
revisão técnica documental. Assim, dependendo da definição:

- revisões de versão da arquitetura: **3, comprovadas**;
- eventos formais de revisão/certificação arquitetural: **4, inferidos pelos
  artefatos**.

## 7. Evolução documental e de governança

### 7.1 Documentos e linhas

| Universo no corte pré-GOV-005 | Arquivos `.md` | Linhas físicas | Linhas não vazias | Classe |
|---|---:|---:|---:|---|
| CORE presente | 129 | 22.020 | 16.915 | Comprovado |
| CORE rastreado no baseline | 123 | 18.535 | 14.177 | Comprovado |
| Diretório pai canônico | 29 | 1.430 | 1.015 | Comprovado |
| **Corpus canônico presente** | **158** | **23.450** | **17.930** | Comprovado por caminho |

O diretório pai contém adicionalmente 115 caminhos Markdown ao considerar
releases, checkpoints, instaladores e backups. Eles são úteis historicamente,
mas não foram adicionados ao total canônico porque incluem versões repetidas.

### 7.2 Relatórios

- **45 arquivos rastreados no baseline CORE** possuem `REPORT` ou `RELATORIO` no
  nome;
- **46 arquivos presentes no CORE**, excluído runtime, satisfazem a mesma regra;
- o diretório pai possui **17 caminhos históricos adicionais nomeados como
  relatório**, além de relatórios CVF cujo nome não contém a palavra;
- portanto, “45” é a medida canônica de baseline; “63 caminhos nomeados” é o
  alcance histórico bruto, sem deduplicação de conteúdo.

### 7.3 Governança

No corpus principal há GOV-001 no diretório pai, GOV-002 e GOV-003 no CORE, além
desta GOV-005. Não foi localizado GOV-004 no corte. A ausência é registrada, não
corrigida. Políticas de versionamento, Git, restore, mudança, checkpoints,
baseline e status complementam a governança.

## 8. Evolução do SDK

| Fase | Estado do SDK | Evidência |
|---|---|---|
| Fundação | Estrutura inicial e módulos operacionais | Commit SPR-001 e arquivos históricos. |
| SPR-008 | Formação do `cko.core` modular | Relatórios A–W/OA e testes cumulativos. |
| SPR-009 | Certificação com ressalvas | 686 testes aprovados; P1 documentadas. |
| SPR-009A | Release `cko` 1.0.0 | Quatro P1 eliminadas; composição e exceções consolidadas. |
| SPR-010–016 | Camada semântica aditiva | Novos namespaces sem remoção de API anterior. |
| SPR-017 | Provenance aditiva | 15 módulos de provenance e 36 exports raiz. |
| Baseline | SDK 1.0.0 congelado | Tag `CKO-BASELINE-2026.07`. |
| Ciclo II | Nenhuma alteração no SDK | Documentos exigem preservação de 1.0.0/646. |

No corte, há **277 arquivos Python de produção** sob `src`; 43 são fachadas
`__init__.py` e 234 são módulos de implementação. A extensão arquitetural foi
predominantemente aditiva, com a fachada raiz crescendo e os domínios ganhando
pacotes especializados.

## 9. Evolução da API pública

| Corte | Exports raiz | Situação | Classe |
|---|---:|---|---|
| SPR-009 | 334 | Fachada auditada antes da consolidação pós-certificação. | Comprovado |
| SPR-009A | 346 | +12 para exceções/composition; únicos e resolvidos. | Comprovado |
| Pré-SPR-017 | 610 | Superfície preservada após SPR-010–016. | Comprovado por homologação SPR-017 |
| SPR-017/baseline | 646 | 610 anteriores + 36 provenance; zero colisão. | Comprovado |

Os valores intermediários entre 346 e 610 não foram reconstruídos nominalmente
nesta auditoria porque os relatórios nem sempre publicam o total raiz após cada
Sprint. O resultado final foi validado por catálogo, AST, importação e smoke de
wheel nos relatórios existentes. Nenhuma alteração de API foi realizada pela
GOV-005.

## 10. Evolução dos testes

| Marco | Resultado cumulativo documentado |
|---|---:|
| SPR-008A | 9 aprovados |
| SPR-008F | 122 aprovados |
| SPR-008I | 224 aprovados |
| SPR-008Q/OA | 446/407 aprovações em recortes diferentes |
| SPR-008R | 486 aprovados + 2 falhas legadas |
| SPR-008W | 686 aprovados + 2 falhas legadas |
| SPR-009A | 703 aprovados + 2 falhas legadas |
| SPR-010 | 732 aprovados + 2 falhas legadas |
| SPR-015 | 850 aprovados + 2 falhas legadas |
| SPR-017 final | 928 aprovados + 2 falhas legadas |

Métricas presentes:

- 38 arquivos `test_*.py`;
- 659 funções estáticas `test_*`;
- 16.131 linhas físicas e 14.013 linhas não vazias em testes;
- 930 casos coletados na regressão final documentada;
- duas falhas herdadas conhecidas: argumento `calculate_hash` em
  `collect_metadata` e handle SQLite aberto no teardown Windows;
- zero falha nova atribuída à SPR-017;
- cobertura agregada total não comprovada; os relatórios registram cobertura por
  entrega, geralmente acima de 90%, com limitações ambientais explícitas.

Nenhum teste foi executado por esta auditoria, para preservar rigorosamente o
estado do workspace. Os números são evidência histórica documentada e contagem
estática, não nova homologação.

## 11. Estatísticas gerais consolidadas

| Métrica solicitada | Valor principal | Natureza/observação |
|---|---:|---|
| Dias do projeto | 24 | Comprovado/inferido pelo intervalo inclusivo. |
| Dias efetivamente trabalhados | 18 | Inferido por artefatos; não folha de ponto. |
| Sprints/incrementos concluídos | 41 | Inferido com granularidade de sufixos. |
| Sprint aberta sem implementação | 1 (SPR-018) | Comprovado documentalmente. |
| Ciclos arquiteturais | 2 | Comprovado. |
| ADRs canônicos | 6 | Comprovado pelo índice/GOV-003. |
| RFCs localizadas | 2 | Comprovado: RFC-001 e RFC-002. |
| Documentos canônicos | 158 | Comprovado por caminho, pré-GOV-005. |
| Relatórios nomeados no baseline CORE | 45 | Comprovado. |
| Relatórios nomeados históricos brutos | 63 caminhos | Inferido; inclui cópias externas. |
| Commits | 13 | Comprovado. |
| Módulos Python em `src` | 277 | Comprovado. |
| Módulos Python sem `__init__` | 234 | Comprovado. |
| Componentes diretos de `cko.core` | 26 | Comprovado. |
| LOC Python de produção | 42.542 | Comprovado, linhas físicas. |
| LOC operacional com auxiliares | 43.929 | Comprovado; produção + scripts/migrações. |
| Linhas de documentação | 23.450 | Comprovado, Markdown canônico. |
| Arquivos de teste | 38 | Comprovado. |
| Funções de teste estáticas | 659 | Comprovado. |
| Casos de teste finais | 930 | Comprovado pelos relatórios: 928 + 2. |
| Exports públicos raiz | 646 | Comprovado. |
| Revisões da arquitetura mestra | 3 | Comprovado. |
| Eventos formais de revisão arquitetural | 4 | Inferido por certificação/auditorias. |
| Homologações explicitamente nomeadas em arquivo | 1 | Comprovado: SPR-017. |
| Linhagens macro declaradas homologadas até SPR-017 | 17 | Inferido do roadmap; não equivale a 17 relatórios formais. |
| Auditorias históricas distintas identificadas | 8 | Inferido por artefatos canônicos/históricos. |

As oito auditorias identificadas são: governança/baseline CKO-AUDIT-001,
auditoria canônica SPR-006B, auditoria/certificação SPR-009, pré-implementação
SPR-016, pré-implementação SPR-017, auditoria da especificação SPR-017, nova
auditoria SPR-017E e preparação/consolidação da baseline. Esta GOV-005 é a nona
atividade de auditoria após sua criação, mas não entra na fotografia histórica.

## 12. Metodologia de estimativa de esforço

Nenhuma fonte registra horas de início/fim, time tracking, agenda ou folha de
ponto. Por isso foram usados dois modelos independentes.

### 12.1 Modelo A — esforço direto inferido

1. Identificaram-se 18 dias com evidência material.
2. Cada dia foi classificado por densidade e natureza dos artefatos: leve,
   médio ou intenso.
3. Aplicaram-se faixas de 4–6 h, 6–9 h e 8–13 h, respectivamente.
4. O centro foi calibrado para o padrão observado de produção intensiva e
   assistida, incluindo elaboração, execução, revisão e homologação no mesmo dia.
5. As horas foram alocadas por atividade dominante, sem somar o mesmo documento
   simultaneamente como documentação, auditoria e governança.

Resultado: **160 homem-horas diretas**, faixa **113–234 h**.

### 12.2 Modelo B — esforço humano equivalente convencional

Este modelo estima o esforço de reposição por equipe convencional:

- código: 43.929 LOC operacionais, complexidade de contratos/modelos e taxa
  efetiva integrada de 35–60 LOC/h;
- documentação: 23.450 linhas canônicas, classificadas por tipo para evitar
  contabilizar auditorias/GOVs duas vezes;
- arquitetura: 26 componentes, três versões mestras, seis ADRs e dois ciclos;
- qualidade: 16.131 linhas de teste, 930 casos finais, builds, cobertura e
  regressões repetidas;
- revisão/auditoria: gates, catálogos, reconciliação de 471 arquivos e 646
  exports;
- governança: ADRs, RFCs, GOVs, baseline, políticas e abertura condicionada.

Resultado: **1.990 homem-horas equivalentes**, faixa **1.490–2.735 h**.

O Modelo B mede custo/reprodutibilidade e não pode ser apresentado como horas
cronológicas efetivamente consumidas pelo autor ou por ferramentas.

## 13. Estimativa de esforço e homem-hora

| Categoria | Direto inferido (h) | Faixa direta | Equivalente convencional (h) | Faixa convencional | Base metodológica |
|---|---:|---:|---:|---:|---|
| Arquitetura | 22 | 16–32 | 190 | 140–260 | Componentes, ARCHs, ADRs, dependências e ciclos. |
| Documentação | 30 | 22–42 | 300 | 220–390 | Documentos gerais e relatórios não classificados em gates/GOV. |
| Desenvolvimento | 58 | 40–82 | 880 | 730–1.255 | 43.929 LOC operacionais, integração e empacotamento. |
| Homologação/testes | 14 | 10–22 | 120 | 80–160 | 930 casos, builds, cobertura e smoke isolado. |
| Revisão técnica | 10 | 7–16 | 170 | 110–230 | Reconciliação, API, catálogos e revisão transversal. |
| Auditoria | 16 | 11–24 | 190 | 120–250 | Oito atividades históricas e gates formais. |
| Governança | 10 | 7–16 | 140 | 90–190 | GOV, baseline, RFC, políticas e rastreabilidade. |
| **Total** | **160** | **113–234** | **1.990** | **1.490–2.735** | Soma não sobreposta das categorias. |

### 13.1 Interpretação correta

- **Valor comprovado de horas:** inexistente.
- **Valor inferido recomendado para esforço direto:** 160 h.
- **Valor estimado de reposição convencional:** 1.990 h.
- **Equivalência direta em jornadas de 8 h:** 20 dias-pessoa centrais, faixa de
  14,1 a 29,3 dias-pessoa.
- **Equivalência convencional em jornadas de 8 h:** 248,8 dias-pessoa centrais,
  faixa de 186,3 a 341,9 dias-pessoa.

O fato de 160 h exceder 18 × 8 h é compatível com dias intensos, trabalho em fim
de semana e sessões longas sugeridas pelas datas e horários. Não prova cada hora.

## 14. Produtividade por fase

| Fase | Dias ativos | Entrega observável | Leitura de produtividade |
|---|---:|---|---|
| Fundação, 11–12/07 | 2 | Estrutura, inventários, persistência, migração e pacotes iniciais | Alta densidade de bootstrap e material legado. |
| CORE/Discovery, 14–23/07 | 8 | 24 incrementos SPR-008; 686 testes aprovados ao final | Pico de construção modular; forte automação/assistência implícita. |
| Certificação, 25/07 | 1 | Auditoria SPR-009, correção SPR-009A, SDK 1.0.0 | Alto valor de estabilização em um único dia. |
| Semântica, 26–28/07 | 2 | SPR-010–016; API pré-017 em 610 exports | Maior crescimento de domínios por dia. |
| Provenance/baseline, 29–31/07 | 3 | Especificação, duas reauditorias, implementação, homologação e 12 commits | Maior densidade de revisão e formalização. |
| Ciclo II, 02–03/08 | 2 | ARCH-002, GOV-002/003, ADR-006, RFC-002 e abertura SPR-018 | Produtividade documental, sem desenvolvimento. |

Indicadores brutos sobre 18 dias ativos:

- 2.441 LOC operacionais por dia ativo;
- 1.303 linhas Markdown canônicas por dia ativo;
- 2,3 incrementos concluídos por dia ativo;
- 51,7 casos finais de teste por dia ativo;
- 8,9 horas diretas centrais por dia ativo.

Esses indicadores não são produtividade humana convencional. Eles refletem
consolidação, reaproveitamento, automação e provável assistência de ferramentas;
servem para comparar fases, não para metas de equipe.

## 15. Complexidade crescente

A complexidade cresceu em cinco dimensões:

1. **Estrutural:** de repositório/scan inicial para 277 módulos e 26 componentes
   do Core.
2. **Arquitetural:** de módulos operacionais para execução, runtime, storage,
   adapters, checkpoint, UoW e composição.
3. **Semântica:** Knowledge Object → Document → Relationship → Graph → Query →
   Index → Corpus → Provenance.
4. **Contratual:** API raiz de 334 exports auditados para 646 exports homologados.
5. **Governança:** de uma baseline arquitetural para dois ciclos, seis ADRs,
   duas RFCs, gates D0–D7 e execução por ondas/pacotes condicionados.

O crescimento não foi apenas de volume. A SPR-017 introduziu critérios
normativos, canonicalização, hashes, versionamento, validação e provenance que
exigiram reespecificação e múltiplos gates. O Ciclo II amplia a complexidade
organizacional, de autoridade e segurança sem ampliar o SDK no corte atual.

## 16. Principais marcos

1. Fundação do repositório e primeiro commit em 11/07.
2. Persistência/migração e pacotes históricos em 12/07.
3. Formação progressiva do CORE SDK nas SPR-008A–W/OA.
4. Certificação arquitetural SPR-009 e resolução das ressalvas na SPR-009A.
5. Publicação do SDK `cko` 1.0.0.
6. Formação completa da camada semântica SPR-010–016.
7. Reespecificação controlada e homologação da Provenance na SPR-017.
8. API estabilizada em 646 exports e regressão em 928 aprovações/2 falhas
   históricas.
9. Consolidação Git e tag `CKO-BASELINE-2026.07` em 31/07.
10. Instituição documental do Ciclo Arquitetural II em 02/08.
11. Abertura condicionada da SPR-018, sem implementação, em 03/08.

## 17. Principais decisões

- adotar monólito modular incremental;
- estabelecer identidade documental canônica;
- preservar módulos operacionais legados;
- separar banco canônico;
- fazer persistência aditiva;
- manter SDK 1.0.0 e compatibilidade retroativa;
- estender a API somente de forma aditiva;
- separar contratos neutros de adapters concretos;
- exigir arquitetura, especificação, auditoria, testes e homologação por gate;
- adotar federação governada, não centralização física, no Ciclo II;
- manter autoridade, ownership, stewardship e Provenance explícitos;
- impedir que RFC ou termo documental autorize código implicitamente.

## 18. Nível de confiança

| Resultado | Confiança | Justificativa |
|---|---|---|
| Commits, refs, arquivos, LOC, módulos e componentes | Alta | Contagem mecânica reproduzível. |
| API pública 646 | Alta | Catálogo, código e homologação convergem. |
| Testes finais 928 + 2 | Alta para evidência histórica | Três relatórios convergem; não reexecutado pela GOV-005. |
| ADRs 6, RFCs 2 e ciclos 2 | Alta | Índice reconciliado e documentos canônicos. |
| 18 dias ativos | Média | Datas de arquivo podem ser copiadas ou normalizadas. |
| 41 incrementos concluídos | Média | Sufixos e arquivos históricos tornam a taxonomia irregular. |
| Homologações macro | Média-baixa | Roadmap declara estado; relatórios formais não existem para cada macro. |
| 160 h diretas | Baixa-média | Sem time tracking; modelo cronológico e de densidade. |
| 1.990 h equivalentes | Média-baixa | Modelo de reposição sensível a equipe, ferramentas e reuso. |

Confiança global das **métricas técnicas:** alta. Confiança global das
**estimativas de horas:** baixa a média. O intervalo, e não apenas o ponto
central, deve orientar decisões.

## 19. Limitações da estimativa

1. O Git contém consolidação retroativa e não preserva microcommits diários.
2. Há um único autor Git e nenhum registro de horas, sessões ou pessoas.
3. Datas de modificação podem refletir cópia, extração, sincronização do Drive ou
   consolidação, não momento de autoria.
4. Releases, checkpoints, ZIPs e backups duplicam artefatos; contá-los como
   produção nova inflaria o esforço.
5. Linhas físicas não medem complexidade, originalidade ou qualidade sozinhas.
6. Parametrização faz funções estáticas e casos coletados divergirem.
7. Cobertura total agregada não está metodologicamente disponível.
8. A GOV-005 não reexecutou testes, builds ou imports para não alterar o estado.
9. O workspace já estava sujo no início desta auditoria; alterações preexistentes
   foram preservadas e não são atribuídas à GOV-005.
10. A velocidade observada é incompatível com pressupostos convencionais sem
    automação, reuso ou assistência; por isso esforço direto e equivalente foram
    separados.
11. Não é possível comprovar pausas, trabalho off-line, revisão mental ou esforço
    descartado que não deixou artefato.
12. O corte inclui documentos do Ciclo II ainda não rastreados no Git do CORE;
    eles são estado presente, não baseline homologada.

## 20. Recomendações

1. Registrar `start`, `end`, responsável, ferramenta e horas por Sprint/gate.
2. Fazer commits menores e tempestivos, preservando autoria e data real.
3. Adotar manifesto versionado de artefatos com SHA-256, tipo, origem, Sprint,
   status e relação canônico/cópia.
4. Manter índice único de Sprints que diferencie macro, sub-Sprint e gate.
5. Manter índices canônicos de GOV, RFC, ADR, auditoria e homologação.
6. Publicar snapshot mecânico por baseline: LOC, módulos, componentes, API,
   testes, cobertura, documentos e hashes.
7. Separar “horas humanas”, “horas de ferramenta” e “horas equivalentes” nas
   futuras auditorias.
8. Preservar relatórios de pytest em formato máquina, com collection count,
   ambiente, duração e hash do código testado.
9. Resolver ou formalmente aceitar as duas falhas históricas antes do próximo
   baseline técnico.
10. Incorporar os documentos do Ciclo II ao controle de versão somente por
    processo autorizado, sem reabrir a baseline 2026.07.
11. Criar GOV-004 ou registrar formalmente a reserva/ausência do identificador.
12. Repetir a auditoria ao final de cada ciclo, usando a GOV-005 como referência
    metodológica, mas recalibrando taxas com horas reais.

## 21. Conclusões

O CKO evoluiu, em 24 dias corridos e 18 dias com evidência material, de uma
fundação de repositório para um SDK modular 1.0.0 com 26 componentes Core, 646
exports públicos, camada semântica completa até Provenance e forte disciplina
documental. O Ciclo I culminou em baseline tecnicamente consolidada; o Ciclo II
foi instituído documentalmente sem alteração do SDK ou da API no corte.

O acervo é volumoso e tecnicamente denso: 43.929 linhas operacionais, 16.131
linhas de testes e 23.450 linhas Markdown canônicas. A qualidade da rastreabilidade
por artefato é superior à rastreabilidade temporal: decisões, testes e gates são
ricos, mas o Git e a ausência de time tracking não permitem comprovar horas.

Por isso, a conclusão responsável é uma faixa. O esforço direto mais plausível é
**113–234 homem-horas**, centro **160 h**. O esforço convencional de reposição é
**1.490–2.735 homem-horas**, centro **1.990 h**. Usar 1.990 h como se fossem horas
cronológicas realizadas seria incorreto; usar apenas os 13 commits também seria
incorreto e subestimaria radicalmente o trabalho.

## 22. Protocolo de reprodutibilidade

As métricas podem ser reproduzidas com operações de leitura equivalentes a:

```text
git rev-list --all --count
git branch -a -vv
git log --all --reverse --shortstat
git ls-files
contagem recursiva de *.py, *.md e test_*.py
contagem física e não vazia de linhas
busca estática de funções test_* e declarações __all__
classificação de artefatos por nome e diretório
```

O hash SHA-256 final deste documento deve ser calculado após sua gravação e é
apresentado no fechamento externo da auditoria, porque inserir o próprio hash no
arquivo alteraria recursivamente o valor.

## 23. Declaração de não alteração

Durante a GOV-005:

- nenhum código foi implementado ou alterado;
- nenhum teste, SDK, API pública ou baseline foi alterado;
- nenhum documento preexistente foi modificado;
- nenhum arquivo foi removido, movido ou renomeado;
- nenhum commit, push, merge, checkout, restore ou staging foi realizado;
- a única criação foi `GOV-005_PROJECT_EFFORT_AUDIT.md`.

O estado Git inicial já continha `docs/adr/INDEX.md` modificado e diversos
arquivos não rastreados. Eles permaneceram fora do escopo de escrita e devem
continuar aparecendo no status final, juntamente com este novo relatório.
