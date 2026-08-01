# ARCH-001 — CKO CORE SDK — Arquitetura Oficial

> **Status documental:** registro histórico. As referências a `cko` 0.1.0 abaixo pertencem à data de corte original. A baseline vigente é o CKO CORE SDK 1.0.0, homologado até a SPR-017, com 646 exports públicos únicos e resolvidos.

**Classificação:** Documento Mestre Oficial de Arquitetura  
**Status:** Oficial  
**Versão documental:** 1.0.0  
**Versão arquitetural consolidada:** Baseline Arquitetural 1.0 + CORE-001 + SPR-008A–SPR-008Q  
**Data de corte:** 19/07/2026  
**Última entrega considerada:** SPR-008Q homologada  
**Próxima Sprint:** não definida por este documento  
**Produto:** CKO CORE SDK  
**Namespace canônico:** `cko.core`  
**Runtime de referência:** Python 3.13 ou superior  
**Distribuição na data de corte:** `cko` 0.1.0  

> Este documento consolida, mas não substitui, os termos, critérios, evidências e
> relatórios individuais das entregas homologadas. Em caso de investigação de uma
> decisão ou de uma evidência de aceite, a SPR de origem continua sendo o registro
> histórico primário. Nenhuma entrega posterior à SPR-008Q integra esta arquitetura.

## Controle normativo

As palavras **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **PODE** e **RECOMENDADO** são
normativas. O documento descreve simultaneamente: (a) a arquitetura canônica da
plataforma que rege o SDK; (b) o baseline efetivamente homologado até a SPR-008Q;
e (c) a direção permitida para evolução futura. A presença de um componente no
roadmap arquitetural não significa autorização de implementação.

---

## 1. Visão Geral do CORE SDK

O CKO CORE SDK é o núcleo técnico compartilhado da Plataforma CKO. Sua função é
fornecer contratos, modelos e motores neutros de produto para que CKO, CID,
Aurora, Biblioteca Digital, Governança, Downloads e aplicações futuras componham
seus casos de uso sem duplicar capacidades transversais.

A arquitetura oficial é um **monólito modular orientado a domínio**, estruturado
segundo **Ports and Adapters**, evoluído incrementalmente e com dependências
orientadas para o núcleo. O SDK não é uma aplicação final, não decide políticas
institucionais e não incorpora tecnologias concretas de armazenamento, busca,
IA, OCR ou transporte.

Na baseline consolidada, o CORE possui quatro grandes superfícies:

1. **Fundação canônica:** contratos, identidade, modelos, metadados,
   configuração, erros, logging e utilitários.
2. **Motores de domínio:** inventário e Discovery, incluindo consulta,
   avaliação, índices lógicos, estatísticas, optimizer e planners.
3. **Coordenação de execução:** Execution Planner, Execution Engine e Runtime.
4. **Infraestrutura interna de desenvolvimento:** workspace, limpeza, validação
   ambiental e build determinístico, sem exposição pela fachada pública.

O comportamento homologado é predominantemente lógico e em memória. Planos,
índices, estatísticas, recursos e execuções são representações canônicas; eles não
implicam acesso a dados físicos. Adaptadores concretos permanecem fora do domínio.

---

## 2. Objetivos do Projeto

O CKO CORE SDK tem os seguintes objetivos permanentes:

- estabelecer uma linguagem técnica canônica para ativos, identidades,
  metadados, descobertas, consultas, planos, execuções e runtime;
- permitir reutilização entre produtos sem acoplamento a regras exclusivas de um
  produto, cliente, tecnologia ou repositório;
- assegurar determinismo, imutabilidade de saídas, serialização versionada,
  auditabilidade e validação explícita;
- proteger o legado por evolução aditiva, janelas de compatibilidade e migração
  incremental;
- separar domínio, aplicação, infraestrutura e governança;
- tornar integrações concretas substituíveis por meio de contratos e injeção;
- impedir que decisões humanas de canonicidade, taxonomia, confidencialidade e
  certificação sejam assumidas silenciosamente por automação;
- oferecer uma cadeia completa de planejamento e coordenação lógica de consultas,
  sem antecipar persistência ou execução física de dados;
- preservar evidências técnicas suficientes para homologação e evolução segura.

Não são objetivos do SDK: prover GUI, identidade visual, fluxos específicos de
cliente, conteúdo documental, credenciais, caminhos absolutos de produção,
bancos concretos, providers concretos, executores de OCR/LLM, RAG, embeddings,
índices vetoriais ou automações destrutivas.

---

## 3. Princípios Arquiteturais

1. **Domain First.** Modelos e invariantes canônicos precedem integrações.
2. **Ports and Adapters.** Tecnologias concretas implementam portas do núcleo.
3. **SDK First.** Capacidades neutras e comprovadamente transversais pertencem ao
   SDK; jornadas permanecem nas aplicações.
4. **Monólito modular incremental.** O sistema evolui por módulos coesos, não por
   microserviços ou reestruturações amplas sem decisão formal.
5. **Dependências para dentro.** Domínio não importa infraestrutura concreta.
6. **Imutabilidade por padrão.** Modelos, snapshots, planos, relatórios e saídas
   são imutáveis; mutabilidade só existe onde representa ciclo de vida explícito.
7. **Determinismo e reprodutibilidade.** Mesmas entradas canônicas produzem a
   mesma estrutura, ordenação, identidade lógica e JSON quando o timestamp é
   controlado ou herdado.
8. **Validação antes do commit.** Entradas e transições são validadas antes de
   alterar estado; falhas não deixam mutações parciais.
9. **Serialização estrita e versionada.** Envelopes rejeitam versões, modelos,
   campos ou tipos desconhecidos.
10. **Evidência antes de automação.** Toda resolução relevante deve ser
    explicável e auditável.
11. **Preservação do legado.** Módulos históricos não são movidos ou removidos
    por conveniência local.
12. **Infraestrutura substituível.** Filesystem, bancos, APIs e serviços externos
    permanecem adaptadores.
13. **Estado global proibido por padrão.** Registries são instanciáveis e
    injetáveis; singletons não são base arquitetural.
14. **Cancelamento cooperativo.** O núcleo não depende de threads ou mecanismos
    específicos de plataforma para cancelar trabalho.
15. **Observabilidade sem destino imposto.** O núcleo produz eventos estruturados,
    mas o consumidor escolhe handlers e destinos.
16. **Governança soberana.** O SDK representa e aplica políticas aprovadas; não
    substitui CMC, Taxonomia Oficial, validação humana ou autoridade institucional.
17. **Evolução por ADR.** Mudança material de fronteira, contrato, persistência,
    segurança ou compatibilidade exige decisão arquitetural formal.

---

## 4. Baseline Arquitetural Oficial

A arquitetura consolidada descende da Baseline Arquitetural 1.0, composta
indivisivelmente por `DISCOVERY-ECOSYSTEM-001`, `DISCOVERY-ECOSYSTEM-002`,
`CKO-ARCH-001` e `CKO-GOV-001`. Essa baseline definiu:

- monólito modular orientado a domínio;
- Ports and Adapters;
- CORE SDK como núcleo compartilhado;
- produtos como consumidores;
- infraestrutura como adaptadores substituíveis;
- preservação do legado pelo padrão Strangler Fig;
- separação entre decisão lógica e execução física;
- promoção ao SDK somente mediante neutralidade, contrato, testes e homologação.

O baseline técnico oficial deste documento é o estado composto por **CORE-001** e
**SPR-008A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, OA, P e Q**. A SPR-008OA é
uma entrega interna de workspace posicionada entre O e P. Nenhuma Sprint posterior
integra a baseline.

Para o escopo específico do CKO CORE SDK, o ARCH-001 é a referência técnica
principal. Os documentos canônicos da Plataforma permanecem sua autoridade de
governança e os relatórios das SPRs permanecem as evidências históricas de origem.

Hierarquia de autoridade para evolução:

```text
CKO-GOV-001 / Baseline 1.0
          |
          v
CKO-ARCH-001 / arquitetura canônica da plataforma
          |
          v
ARCH-001 / consolidação mestre do CORE SDK até SPR-008Q
          |
          +----> ADRs aceitos
          |
          +----> SPRs homologadas e respectivas evidências
          |
          v
Código e contratos públicos homologados
```

Se houver divergência, a governança e uma decisão arquitetural formal prevalecem
sobre interpretação local. Este documento não retroage para reescrever fatos
históricos das SPRs.

---

## 5. Arquitetura em Camadas

As camadas são lógicas; podem residir no mesmo processo e repositório.

```text
+-----------------------------------------------------------------------+
| PRODUTOS / APLICAÇÕES                                                  |
| CKO | CID | Aurora | Biblioteca Digital | Governança | Downloads       |
| Jornadas, UI/CLI de produto, permissões contextuais, casos de uso      |
+-------------------------------+---------------------------------------+
                                | consomem contratos públicos
                                v
+-----------------------------------------------------------------------+
| CKO CORE SDK                                                           |
|                                                                       |
|  +-------------------------+  +-------------------------------------+  |
|  | Fundação canônica       |  | Motores canônicos                  |  |
|  | identity, models,       |  | inventory, discovery, query,       |  |
|  | metadata, contracts,    |  | statistics, optimizer, planners,   |  |
|  | errors, config, logging |  | execution engine, runtime          |  |
|  +-------------------------+  +-------------------------------------+  |
|                    ^ portas e modelos neutros                         |
+--------------------|--------------------------------------------------+
                     | implementam / são injetados
                     v
+-----------------------------------------------------------------------+
| ADAPTADORES / INFRAESTRUTURA                                           |
| Filesystem | bancos | Drive | APIs | OCR | IA | cache | filas | logs   |
+-----------------------------------------------------------------------+

Camada transversal externa: GOVERNANÇA
CMC | Taxonomia | confidencialidade | canonicidade | validação humana
```

Regras de dependência:

- produtos podem depender do SDK e de adaptadores compostos pela aplicação;
- adaptadores podem depender dos contratos do SDK;
- o SDK não pode depender de produto, cliente ou adaptador concreto;
- `cko.core.discovery` pode depender da fundação canônica, mas não de Inventory;
- `cko.core.inventory` depende de modelos canônicos, não de Discovery;
- `cko.core.execution` consome o plano físico produzido em Discovery;
- `cko.core.runtime` compõe o Engine e não executa operadores diretamente;
- `cko.core.workspace` é infraestrutura interna de desenvolvimento e não é
  reexportada por `cko.core`.

---

## 6. Namespaces Oficiais

| Namespace | Natureza | Responsabilidade | Exposição |
|---|---|---|---|
| `cko.core` | fachada pública | API canônica agregada e aliases compatíveis | pública |
| `cko.core.contracts` | fundação | portas `Repository`, `Clock`, `EventPublisher`, `Plugin`, `Identifiable` | pública |
| `cko.core.identity` | fundação | `CanonicalId`, `SemanticVersion`, `Origin` | pública |
| `cko.core.models` | domínio | documentos, eventos, ativos e relações | pública |
| `cko.core.metadata` | domínio | metadados universais neutros | pública |
| `cko.core.config` | fundação | `SDKConfig` e `load_config` | pública |
| `cko.core.exceptions` | fundação | hierarquia base de erros | pública |
| `cko.core.logging` | observabilidade | formatter JSON e configuração idempotente | pública |
| `cko.core.inventory` | motor | agregado e consultas de inventário em memória | pública pelo subnamespace |
| `cko.core.discovery` | motor | Discovery, query, índices, estatísticas, optimizer e planners | pública |
| `cko.core.execution` | motor | interpretação lógica do plano físico | pública |
| `cko.core.runtime` | coordenação | lifecycle, sessão, recursos e coordenação do Engine | pública |
| `cko.core.workspace` | infraestrutura interna | workspace, limpeza, validação e build | interna; não reexportada |
| `cko.core.utils` | utilitário | texto não vazio e datas com fuso | suporte interno/público técnico |

Namespaces legados sob `cko` — por exemplo `cko.scanner`, `cko.metadata`,
`cko.kb`, `cko.persistence`, `cko.repository`, `cko.migrations`, `cko.models`,
`cko.services` e `cko.contracts` — são preservados por compatibilidade, mas não
constituem extensões do domínio canônico `cko.core`. Novas capacidades do SDK
DEVEM ser introduzidas no namespace canônico autorizado ou por adaptadores
externos, nunca pela duplicação de conceitos em namespaces paralelos.

---

## 7. Organização dos Pacotes

```text
CORE/
|-- src/
|   `-- cko/
|       |-- core/
|       |   |-- contracts/
|       |   |-- identity/
|       |   |-- models/
|       |   |-- metadata/
|       |   |-- config/
|       |   |-- exceptions/
|       |   |-- logging/
|       |   |-- inventory/
|       |   |-- discovery/
|       |   |-- execution/
|       |   |-- runtime/
|       |   |-- workspace/       # interno, não reexportado
|       |   `-- utils/
|       |-- scanner/             # legado preservado
|       |-- metadata/            # legado preservado
|       |-- kb/                  # legado preservado
|       |-- persistence/         # legado/aditivo, fora do domínio canônico
|       |-- repository/          # legado/adaptador
|       `-- migrations/          # infraestrutura histórica
|-- tests/                       # matrizes por entrega e testes legados
|-- docs/                        # arquitetura, ADRs e termos históricos
|-- runtime/
|   |-- temp/
|   |-- cache/
|   |-- traces/
|   |-- logs/
|   |-- reports/
|   |-- database/
|   `-- snapshots/
|-- CKO_CLEAN.cmd
|-- CKO_TESTS.cmd
|-- CKO_BUILD.cmd
`-- CKO_RUNTIME.cmd
```

O pacote `discovery` é internamente organizado por capacidades coesas:

- contratos e modelos base (`contracts`, `models`, `service`, `validator`);
- providers, sessão, cancelamento e checkpoints;
- streaming e batches;
- resolução de identidade;
- capacidades;
- query model, validação, resolução e avaliação;
- índices lógicos;
- estatísticas e custo;
- Cost-Based Planner;
- Query Optimizer;
- Execution Planner.

Cada capacidade separa, sempre que necessário, modelos, erros, contratos,
validação e orquestração. Arquivos `__init__.py` definem as superfícies públicas;
imports diretos de detalhes internos devem ser evitados pelos consumidores.

---

## 8. Fluxo Completo do SDK

O fluxo arquitetural completo possui duas cadeias complementares.

### 8.1 Cadeia de descoberta e incorporação explícita

```text
Fonte declarada
     |
     v
DiscoveryRequest ---> validação de política/capacidade
     |
     v
Provider externo injetado ---> DiscoverySession / CancellationToken
     |
     +---- modo agregado ----> DiscoveryResult
     |
     `---- modo streaming ---> DiscoveryBatch* ---> acknowledgements/cursor
                                      |
                                      v
                                DiscoveredItem
                                      |
                                      v
                            IdentityResolutionEngine
                                      |
                                      v
                              ResolutionDecision
                                      |
                         CanonicalId validado/alocado
                                      |
                                      v
                         DefaultDiscoveryAssetMapper
                                      |
                                      v
                                    Asset
                                      |
                         chamada explícita do consumidor
                                      |
                                      v
                              InventoryService
```

Discovery NÃO insere automaticamente no Inventory. Resolução de identidade NÃO
cria `Asset`; alocação de `CanonicalId` NÃO persiste identidade; mapper NÃO
classifica institucionalmente.

### 8.2 Cadeia de consulta, planejamento e coordenação

```text
DiscoveryQuery
     |
     v
QueryValidationEngine
     |
     v
QueryResolver -------------------------------> QueryPlan
     |                                             |
     |                                             +--> avaliação em memória
     |                                             |    QueryEvaluationEngine
     |                                             |
     |                                             +--> índices lógicos
     |                                                  QueryIndexPlanner
     |
     v
OptimizationPipeline ---> OptimizationResult ---> QueryPlan otimizado
     |
     v
LogicalStatistics + LogicalIndex[]
     |
     v
CostBasedPlanner ---> QueryExecutionPlan (estratégia lógica)
     |
     v
Execution Planner ---> ExecutionPlan (árvore física descritiva)
     |
     v
Runtime ---> ExecutionEngine ---> operadores lógicos ---> ExecutionResult
     |
     v
RuntimeSession / RuntimeReport / RuntimeMetrics
```

O fluxo pode ser composto de formas diferentes pela aplicação. O optimizer é
reversível; o planner de custo escolhe estratégia; o Execution Planner materializa
a árvore; o Engine percorre e coordena operadores; o Runtime governa lifecycle.
Nenhum desses estágios acessa fonte de dados concreta na baseline atual.

---

## 9. Pipeline de Consultas

### 9.1 Descrição canônica

1. `DiscoveryQuery` expressa filtros, grupos booleanos, projeções, ordenação e
   paginação.
2. `QueryValidationEngine` verifica operadores, valores, duplicidades ambíguas e
   coerência de paginação.
3. `QueryResolver` produz `QueryPlan` lógico versionado, preserva a intenção e
   registra justificativas e estimativas puramente lógicas.
4. Opcionalmente, `QueryEvaluationEngine` aplica o plano diretamente a subjects
   em memória.
5. `LogicalIndexBuilder`, `LogicalIndexResolver` e `QueryIndexPlanner` descrevem
   índices lógicos e sua aplicabilidade.
6. `StatisticsBuilder` cria histogramas e estatísticas lógicas; `CostEstimator`
   estima seletividade, cardinalidade e custo relativo.
7. `OptimizationPipeline` aplica regras equivalentes e retorna plano reversível.
8. `CostBasedPlanner` compara candidatos e produz `QueryExecutionPlan`.
9. O Execution Planner converte a estratégia lógica em `ExecutionPlan` físico.

### 9.2 Semântica homologada de filtros

Operadores: `equals`, `not_equals`, `greater_than`, `greater_or_equal`,
`lower_than`, `lower_or_equal`, `contains`, `starts_with`, `ends_with`, `in`,
`not_in`, `exists` e `not_exists`. Grupos suportam `AND`, `OR` e `NOT`.

O avaliador distingue atributo ausente de atributo existente com valor `None`;
não faz coerção implícita string/número, booleano/inteiro ou datetime/string.
Resolução de caminhos pontuados é limitada a mappings e dataclasses públicas do
CORE; segmentos privados e chamadas de método são proibidos.

### 9.3 Ordem operacional da avaliação

```text
subjects
   -> resolver atributos
   -> avaliar filtros/grupos com curto-circuito
   -> registrar decisão auditável por subject
   -> projetar aprovados
   -> ordenar com desempate por identidade lógica
   -> paginar
   -> QueryEvaluationResult
```

Execuções síncrona e assíncrona preservam a mesma semântica. Ordenação global
pode reter subjects aprovados; rejeitados não são mantidos após sua auditoria.

### 9.4 Índices e estatísticas

Índices lógicos suportam estratégias `HASH`, `ORDERED`, `PREFIX` e `COMPOSITE`.
Eles são estruturas imutáveis em memória, não índices físicos. Histogramas
suportam granularidade `equal_width` e `equal_frequency` para números, strings e
booleanos. Custos são relativos, não benchmarks de infraestrutura.

---

## 10. Execution Planner

Há dois níveis distintos de planejamento e eles NÃO DEVEM ser confundidos:

- **Cost-Based Planner (SPR-008M):** escolhe uma estratégia lógica e produz
  `QueryExecutionPlan`.
- **Canonical Execution Planner (SPR-008O):** transforma essa estratégia em
  `ExecutionPlan`, uma árvore física descritiva.

O Cost-Based Planner considera seletividade, cardinalidade, custo, cobertura de
filtros/ordenação/projeção, densidade e confiança. Candidatos são ordenados por
score, preferência de estratégia, custo, nome da estratégia e IDs de índices.
Estratégias homologadas: `FULL_SCAN`, `INDEX_SCAN`, `COMPOSITE_INDEX_SCAN`,
`PREFIX_INDEX_SCAN` e `ORDERED_INDEX_SCAN`.

O Execution Planner gera uma árvore unária com dez tipos canônicos de nó:
`ScanNode`, `IndexScanNode`, `CompositeIndexScanNode`, `PrefixScanNode`,
`OrderedScanNode`, `FilterNode`, `ProjectionNode`, `SortNode`, `LimitNode` e
`RootNode`.

```text
Root
 `-- Limit? 
      `-- Sort?
           `-- Projection?
                `-- Filter?
                     `-- Scan | IndexScan | CompositeIndexScan |
                         PrefixScan | OrderedScan
```

O validador exige raiz única, IDs únicos, links de pai íntegros, ausência de
ciclos e órfãos, aridade correta, um único acesso folha e compatibilidade entre
estratégia e nó de acesso. IDs são derivados do conteúdo canônico e da posição.
O planner descreve; não executa.

---

## 11. Execution Engine

`cko.core.execution.ExecutionEngine` interpreta o `ExecutionPlan` homologado,
valida contexto e registro de operadores e percorre a árvore em pré-ordem
determinística. A fronteira foi separada de `cko.core.discovery` para não quebrar
os nomes homônimos já publicados pelo Execution Planner.

O Engine coordena dez operadores: scan, index scan, composite index scan, prefix
scan, ordered scan, filter, projection, sort, limit e root. Na baseline, eles
confirmam o contrato lógico do nó e produzem `OperatorResult`; não materializam
registros nem acessam dados.

Invariantes:

- cada objeto de nó é visitado no máximo uma vez;
- a ordem da tupla `children` é preservada;
- ciclo ou reutilização indevida é erro;
- `execution_stack` é restaurada mesmo em falha;
- o registro de operadores é completo, tipado e imutável;
- saída é `ExecutionResult` imutável, versionado e serializável;
- `execution_id` é SHA-256 determinístico do plano canônico;
- duração do Engine é métrica lógica `0.0`, não tempo físico.

Para evitar colisões de API, a fachada raiz usa `EngineExecutionContext`,
`EngineExecutionPipeline` e `EngineExecutionMetrics` para os homônimos do Engine;
os nomes sem prefixo permanecem associados ao Planner onde já homologados.

---

## 12. Runtime

`cko.core.runtime.Runtime` coordena um único ciclo terminal de uma execução física.
Ele compõe o Engine; não executa operadores e não acessa dados.

Responsabilidades:

- criar `runtime_id` e `session_id`;
- vincular e inicializar `ExecutionPlan`;
- preparar contexto e recursos lógicos;
- iniciar, pausar logicamente, retomar, concluir, falhar ou cancelar;
- coordenar o `ExecutionEngine` de modo síncrono;
- reter `ExecutionResult`;
- produzir snapshots de `RuntimeSession`, `RuntimeReport` e `RuntimeMetrics`;
- liberar o registro lógico de recursos;
- emitir eventos estruturados do lifecycle.

`ResourceRegistry` aceita somente descritores serializáveis em memória. Handles,
arquivos, conexões, sockets e objetos externos são rejeitados. Pausa, retomada e
cancelamento são cooperativos; não interrompem concorrentemente uma chamada
síncrona em andamento.

Existem dois tokens distintos e intencionais:

- `cko.core.CancellationToken`: token homologado de Discovery;
- `cko.core.runtime.CancellationToken` e
  `cko.core.RuntimeCancellationToken`: token do Runtime.

Essa distinção é contrato permanente de compatibilidade.

---

## 13. Workspace

`cko.core.workspace` é infraestrutura interna de desenvolvimento homologada na
SPR-008OA. Não pertence à fachada pública `cko.core` e não altera regras de
negócio.

`RuntimePaths` centraliza:

```text
runtime/
|-- temp/
|-- cache/
|-- traces/
|-- logs/
|-- reports/
|-- database/
`-- snapshots/
```

`WorkspaceManager` localiza o projeto por `pyproject.toml` ancestral ou
`CKO_WORKSPACE_ROOT`. `WorkspaceCleaner` e `TemporaryFileManager` removem apenas
temporários validados, nunca a raiz e nunca diretórios permanentes. Caminhos
resolvidos devem permanecer estritamente dentro do workspace e não podem escapar
por link simbólico.

`database`, `reports`, `snapshots` e `logs` são protegidos. Limpeza possui modo
`dry-run`, retorna `CleanResult` e recria a árvore canônica. Os scripts oficiais
internos são `CKO_CLEAN.cmd`, `CKO_TESTS.cmd`, `CKO_BUILD.cmd` e
`CKO_RUNTIME.cmd`. O build de wheel é determinístico e usa somente a biblioteca
padrão; a distribuição continua definida pelo `pyproject.toml`.

A infraestrutura de workspace pode acessar filesystem porque sua função é
explicitamente operacional e interna. Essa exceção não autoriza I/O nos motores
de domínio.

---

## 14. Modelos Fundamentais

### 14.1 Identidade e proveniência

- `CanonicalId`: identidade UUID canônica, independente de nome ou caminho.
- `SemanticVersion`: parsing e precedência semântica.
- `Origin`: origem técnica rastreável com data consciente de fuso.
- `UniversalMetadata`: atributos universais sem taxonomia de produto.

### 14.2 Documentos e eventos

- `CanonicalDocument`, `DocumentLocation` e o `InventoryItem` documental da
  fundação permanecem públicos por compatibilidade.
- `CanonicalEvent` é o envelope neutro de eventos.

### 14.3 Modelo Canônico de Ativos

`Asset` é a raiz. Especializações: `DocumentAsset`, `ImageAsset`, `AudioAsset`,
`VideoAsset`, `ProjectAsset`, `DatabaseAsset`, `KnowledgeAsset`, `FolderAsset` e
`ReferenceAsset`. Tipos associados: `AssetRelation`, `AssetFingerprint`,
`AssetHash`, `AssetClassification`, `AssetStatus` e `AssetLifecycle`.

Igualdade e hash de entidades seguem `CanonicalId`. Relações armazenam IDs, não
objetos ou mecanismos de Graph. `FolderAsset` é agrupamento lógico, sem path;
`DatabaseAsset` não é conexão; `ReferenceAsset` não resolve URI.

### 14.4 Inventário

`cko.core.inventory.InventoryItem` é diferente do `InventoryItem` documental
exportado pela raiz. O agregado `Inventory` é o único dono do estado corrente.
`InventorySnapshot`, `InventoryStatistics`, `InventorySummary` e resultados são
imutáveis.

### 14.5 Discovery

Os modelos base incluem `DiscoverySourceId`, `DiscoveryRequest`,
`DiscoveryScope`, `DiscoveryPolicy`, `DiscoveryCapability`, `DiscoveryContext`,
`DiscoveryEvidence`, `DiscoveredItem`, `DiscoveryBatch`, `DiscoveryResult` e
`DiscoveryMetrics`. Um `DiscoveredItem` é observação com proveniência; não é uma
segunda entidade de `Asset`.

### 14.6 Query e execução

`DiscoveryQuery` resolve para `QueryPlan`; optimizer mantém plano original e
otimizado; Cost-Based Planner produz `QueryExecutionPlan`; Execution Planner
produz `ExecutionPlan`; Engine produz `ExecutionResult`; Runtime produz sessão,
relatório e métricas.

### 14.7 Regras gerais de modelagem

- dataclasses congeladas e `slots` quando aplicável;
- mappings copiados e congelados recursivamente;
- sequências normalizadas para tuplas;
- timestamps com fuso e, em regra, normalizados para UTC;
- valores numéricos não finitos rejeitados;
- JSON determinístico com chaves ordenadas;
- `schema_version = "1.0"` nos modelos homologados, salvo constante pública
  específica do pacote;
- desserialização estrita e rejeição de campos desconhecidos.

---

## 15. Validação

Validação é uma responsabilidade explícita em todas as fronteiras:

| Fronteira | Validador principal | Invariantes centrais |
|---|---|---|
| Fundação | construção dos modelos | texto, datas, identidade, schema |
| Inventory | `InventoryValidator` | identidade, referências, duplicidade, atomicidade |
| Discovery | `DiscoveryValidator` | source, request, item, resultado, proveniência |
| Capacidades | `CapabilityValidationEngine` | requisitos, versões, dependências, conflitos |
| Query | `QueryValidationEngine` | operadores, valores, projeção, sort, paginação |
| Índices | `LogicalIndexValidator` | chaves, cardinalidade, estatísticas, duplicidade |
| Estatísticas | `StatisticsValidator` | frequências, histogramas, densidade, limites |
| Cost Planner | `PlannerValidator` | estratégia, custo, confiança, índices, auditoria |
| Optimizer | `OptimizerValidator` | equivalência, ciclos, integridade, reversibilidade |
| Execution Planner | `ExecutionPlanValidator` | árvore, IDs, links, ciclos, estratégia |
| Engine | `ExecutionEngineValidator` | plano, contexto, estado e operadores |
| Runtime | `RuntimeValidator` | contexto, sessão, lifecycle, recursos e métricas |
| Workspace | `EnvironmentValidator` | runtime, permissões, encoding e espaço |

Padrão obrigatório: modelos rejeitam inconsistências o mais cedo possível;
orquestradores encapsulam falhas externas em erros públicos específicos com
`raise ... from ...`; validadores estritos lançam erro e métodos `is_valid()`
podem oferecer consulta booleana sem substituir o caminho estrito.

---

## 16. Sistema de Logging

O logging canônico usa a biblioteca padrão, namespace `cko` e formatter JSON.
Um registro pode conter timestamp UTC, nível, logger, mensagem, evento, contexto e
exceção. `configure_logging` é idempotente por namespace; motores não configuram
handlers próprios nem criam arquivos.

Princípios:

- nomes de evento são estáveis e orientados a domínio;
- contexto contém IDs, estados, contadores e decisões, não conteúdo integral;
- exceções externas preservam a causa;
- falha secundária de fechamento ou notificação não substitui causa primária;
- destino e retenção são responsabilidades do consumidor/adaptador;
- dados sensíveis e conteúdo de subjects não devem ser registrados.

Famílias homologadas incluem `discovery.*`, `discovery.query.statistics.*`,
eventos de optimization/planning/execution, eventos de workspace e:
`core.runtime.runtime_created`, `runtime_initialized`, `runtime_started`,
`runtime_finished` e `runtime_cancelled`.

```text
Componente CORE
     |
     v
get_logger("cko") + event/context
     |
     v
JsonFormatter canônico
     |
     v
handler fornecido pelo consumidor
     |
     +--> console | arquivo | coletor | serviço externo
```

---

## 17. Estados

### 17.1 Ativos

- `AssetStatus`: `active`, `inactive`, `archived`, `deleted`.
- `AssetLifecycle`: `draft`, `registered`, `validated`, `published`,
  `deprecated`, `retired`.

O modelo valida vocabulário, mas a baseline não implementa workflow institucional
de transição entre esses valores.

### 17.2 Discovery

- Resultado: `pending`, `running`, `completed`, `completed_with_warnings`,
  `failed`, `cancelled`.
- Sessão: `created -> running -> completed | failed | cancelled`; também
  `created -> cancelled`.
- Stream: `created -> open -> completed | failed | cancelled`; também
  `created -> failed | cancelled`; `completed` exige batch final.
- Acknowledgement: `confirmed`, `rejected`, `partial`, `failed`.
- Resolução de identidade: `resolved_existing`, `resolved_new`,
  `duplicate_candidate`, `ambiguous`, `conflict`, `insufficient_evidence`,
  `rejected`.

### 17.3 Execution Engine

```text
CREATED --> READY --> RUNNING --> COMPLETED
   |          |          |
   +----------+----------+----> FAILED
   +----------+----------+----> CANCELLED

COMPLETED, FAILED e CANCELLED são terminais.
```

### 17.4 Runtime

```text
CREATED --> INITIALIZED --> READY --> RUNNING --> COMPLETED
   |             |           |         |
   |             |           |         +--> PAUSED --> RUNNING
   |             |           |                    |
   +-------------+-----------+--------------------+--> FAILED
   +-------------+-----------+--------------------+--> CANCELLED

COMPLETED, FAILED e CANCELLED são terminais.
```

Transições não listadas são inválidas. Estados terminais nunca podem ser reabertos.

---

## 18. Fluxo de Execução

O fluxo nominal a partir de um `ExecutionPlan` é:

1. a aplicação cria `Runtime` com Engine e metadados opcionais;
2. o Runtime nasce em `CREATED`;
3. `initialize(plan)` vincula o plano, prepara contexto e transita por
   `INITIALIZED` até `READY`;
4. `start()`/`execute()` transita para `RUNNING` e verifica cancelamento;
5. o Runtime chama `ExecutionEngine.execute(plan)`;
6. o Engine cria contexto em `CREATED`, valida e transita para `READY` e
   `RUNNING`;
7. o pipeline percorre a árvore em pré-ordem e resolve cada operador;
8. o Engine produz `ExecutionResult` e termina em `COMPLETED`, ou `FAILED`;
9. o Runtime retém o resultado, atualiza métricas, libera recursos lógicos e
   termina em `COMPLETED`, `FAILED` ou `CANCELLED`;
10. sessão e relatório são snapshots imutáveis do ciclo.

```text
Application
    |
    v
Runtime.initialize(ExecutionPlan)
    |
    v
Runtime READY --cancel?--> CANCELLED
    |
    v
Runtime RUNNING
    |
    v
ExecutionEngine
    |
    +--> validate plan/context/operators
    +--> CREATED -> READY -> RUNNING
    +--> preorder(root)
    |      +--> operator(node)
    |      `--> children[]
    +--> ExecutionResult
    `--> COMPLETED | FAILED | CANCELLED
    |
    v
Runtime COMPLETED | FAILED | CANCELLED
    |
    v
RuntimeSession + RuntimeReport + RuntimeMetrics
```

O estado `PAUSED` é um ponto lógico cooperativo do Runtime e não uma suspensão
preemptiva do Engine.

---

## 19. Diagramas Arquiteturais

### 19.1 Contexto da plataforma

```text
                    +-------------------------+
                    | GOVERNANÇA INSTITUCIONAL|
                    | CMC, Taxonomia, NKs,    |
                    | validação e autoridade  |
                    +------------+------------+
                                 | políticas aprovadas
                                 v
+-----------+  +---------+  +--------------------------------+  +-----------+
| CKO / CID |  | Aurora  |  |        CKO CORE SDK            |  | Biblioteca|
| Downloads |->| e apps  |->| contratos + domínio + motores  |<-| Digital   |
+-----------+  +---------+  +---------------+----------------+  +-----------+
                                                ^
                                                |
                                  +-------------+--------------+
                                  | ADAPTADORES SUBSTITUÍVEIS   |
                                  | FS, DB, Drive, OCR, IA, API |
                                  +----------------------------+
```

### 19.2 Módulos do CORE

```text
cko.core
|
|-- contracts ----+
|-- identity -----+----> models <---- metadata
|-- exceptions ---+         |
|-- config --------         +----> inventory
|-- logging -------         |
|-- utils ----------        `----> discovery
|                                      |
|                                      +--> query/index/statistics
|                                      +--> optimizer
|                                      +--> cost planner
|                                      `--> execution planner
|                                                   |
|                                                   v
|-- execution <-------------------------------- ExecutionPlan
|       |
|       v
`-- runtime

workspace  (interno; isolado da fachada pública)
```

### 19.3 Sequência de Discovery streaming

```text
Consumer      Pipeline       Producer       Stream        BatchConsumer
   |             |              |              |                |
   | request     |              |              |                |
   |------------>| create session/token        |                |
   |             |------------->| context      |                |
   |             |              |--batch 0---->|                |
   |             |              |              |--consume------>|
   |             |              |              |<--ack-----------|
   |             |              |--batch n---->|                |
   |             |              |              |--consume------>|
   |             |              |              |<--ack-----------|
   |             |              |--final------>|                |
   |             |              |              |--> completed   |
   |             |<------------- close/cursor/metrics ----------|
   |<------------| StreamingExecution                            |
```

### 19.4 Transformação da consulta

```text
[Query]
   |
   v
[Logical Plan] --optimize/revert--> [Optimized Logical Plan]
   |                                      |
   +--> [Logical Indexes]                 +--> [Statistics]
                   \                         /
                    \                       /
                     v                     v
                      [Cost-Based Planner]
                              |
                              v
                    [QueryExecutionPlan]
                              |
                              v
                    [Execution Planner]
                              |
                              v
                      [ExecutionPlan Tree]
                              |
                              v
                    [Runtime -> Engine]
```

---

## 20. Dependências entre módulos

Matriz de dependência permitida (`A -> B` significa A pode depender de B):

| Origem | Dependências internas permitidas principais | Dependências proibidas |
|---|---|---|
| `contracts` | identity, models | adaptadores, produtos |
| `models` | identity, metadata, utils | inventory, discovery, banco |
| `inventory` | identity, models, exceptions, logging | discovery, filesystem, banco |
| `discovery` base | contracts, identity, metadata, models, logging | inventory, adaptador concreto |
| query/index/statistics | modelos Discovery anteriores | SQL, ORM, cache externo |
| optimizer | query models/validation | Engine, execução física |
| cost planner | query, index, statistics | optimizer como efeito colateral, infraestrutura |
| execution planner | query execution plan | Engine, Runtime, dados |
| `execution` | ExecutionPlan de discovery, logging | Runtime, banco, conectores |
| `runtime` | ExecutionPlan, execution, logging | operadores concretos de dados, I/O externo |
| `workspace` | biblioteca padrão, logging | domínio de produto; reexportação raiz |

Grafo resumido:

```text
utils/identity/metadata/exceptions/logging
                 ^
                 |
               models
              /      \
       inventory    discovery --> optimizer --> planners
                                      |             |
                                      `-------------+
                                                    v
                                                execution
                                                    |
                                                    v
                                                 runtime

workspace (ramo interno separado)
```

Dependências externas de runtime do domínio canônico são limitadas à biblioteca
padrão. `pytest` é dependência de teste; `setuptools` é backend declarado de build,
mas o builder interno homologado não depende dele para gerar seu wheel.

---

## 21. Contratos Públicos

A fonte executável de verdade da superfície pública são os `__all__` dos pacotes
e os imports documentados. Os grupos abaixo são normativos; uma lista completa de
símbolos deve ser obtida da versão instalada correspondente.

### 21.1 Fundação

- portas: `Identifiable`, `Repository`, `Clock`, `EventPublisher`, `Plugin`;
- identidade: `CanonicalId`, `SemanticVersion`, `Origin`;
- modelos: documentos, evento, `Asset` e especializações/tipos associados;
- metadados: `UniversalMetadata`;
- configuração: `SDKConfig`, `load_config`;
- erros: `CKOError` e especializações;
- logging: `JsonFormatter`, `configure_logging`, `get_logger`.

### 21.2 Inventory

`Inventory`, `InventoryBuilder`, `InventoryService`, `InventoryValidator`,
modelos de filtro/query/result/snapshot/statistics/summary e erros do agregado.

### 21.3 Discovery

Contratos de source/provider/mapper/event publisher/validator; modelos de request,
item, batch e result; service; registry/factory/resolver; sessão, token e
checkpoint; portas sync/async de streaming; resolução de identidade; capacidades;
query, avaliação, índice, estatística, optimizer, Cost-Based Planner e Execution
Planner.

### 21.4 Execution

`ExecutionEngine`, `ExecutionOperator`, dez operadores canônicos,
`ExecutionPipeline`, `ExecutionEngineValidator`, `ExecutionState`, context,
metrics, result, resultados de operador/pipeline e erros.

### 21.5 Runtime

`Runtime`, `RuntimeContext`, `RuntimeSession`, `RuntimeReport`, `RuntimeMetrics`,
`RuntimeState`, `LifecycleController`, `ResourceRegistry`, token, validator e erros.

### 21.6 Regras de contrato

- consumidores DEVEM importar pela fachada pública adequada;
- nomes existentes NÃO DEVEM ser redirecionados para outra semântica;
- aliases de colisão são parte do contrato;
- métodos, enums, schemas, eventos e erros públicos não podem mudar de significado
  em release compatível;
- Protocols devem permanecer implementáveis por adaptadores sem dependência
  circular;
- modelos serializados devem conservar envelope e rejeição estrita;
- qualquer expansão deve ser aditiva ou seguir processo de breaking change.

---

## 22. Política de Compatibilidade

1. Compatibilidade é preservada por padrão em código, imports, nomes, assinaturas,
   enums, formatos serializados e semântica observável.
2. Extensões compatíveis são aditivas; remoções e redirecionamentos silenciosos
   são proibidos.
3. Colisões de nome usam aliases explícitos, como nos contextos do Engine e nos
   tokens de cancelamento.
4. Módulos legados permanecem preservados até aposentadoria formal.
5. Breaking change exige versão major, ADR aprovado, inventário de consumidores,
   plano de migração, aviso, janela de depreciação, testes de equivalência e
   rollback.
6. Campos desconhecidos em envelopes da versão 1.0 são rejeitados; evolução de
   schema deve ser explícita.
7. Bancos e formatos históricos não são modificados por motores canônicos.
8. A compatibilidade deve ser demonstrada pela matriz oficial de regressão da
   entrega, não presumida apenas por revisão.
9. Preservar importabilidade não basta: significado e invariantes também devem
   permanecer compatíveis.

---

## 23. Política de Versionamento

O projeto aplica versionamento semântico `MAJOR.MINOR.PATCH`:

- **MAJOR:** mudança incompatível de contrato ou princípio arquitetural; exige ADR;
- **MINOR:** nova capacidade pública compatível;
- **PATCH:** correção compatível, inclusive editorial quando não altera semântica.

Sufixos de distribuição podem usar `-alpha`, `-rc` e `-hotfix` conforme a política
de releases. Versão do pacote, versão de schema, versão de motor e versão
arquitetural são dimensões distintas e devem ser registradas separadamente.

Na data de corte:

- pacote: `cko` 0.1.0;
- requisito: Python `>=3.13`;
- baseline arquitetural: 1.0;
- schemas dos modelos homologados: 1.0 por família;
- versões públicas de planner, optimizer, engine e runtime são constantes de suas
  respectivas APIs e não devem ser inferidas da versão do pacote.

Toda release deve manter rastreabilidade entre versão, Sprint, package, commit ou
manifesto e evidência de homologação.

---

## 24. Padrões de Desenvolvimento

- Python 3.13+; biblioteca padrão no runtime canônico, salvo ADR e aprovação.
- UTF-8 sem BOM nos novos fontes; timestamps conscientes de fuso.
- Type hints completos e docstrings na API pública.
- Estilo PEP 8, com limite histórico homologado de 88 ou 99 colunas conforme a
  entrega; código novo deve adotar um limite único definido pela governança do
  projeto, sem reformatação massiva do legado.
- Modelos públicos imutáveis e com `slots` quando apropriado.
- Mutabilidade restrita a agregados e controladores de lifecycle.
- Funções puras para normalização, hashing lógico e serialização.
- Injeção de portas, relógios, publishers, providers e operadores.
- Nenhum singleton ou registro global sem ADR.
- Nenhum caminho absoluto, credencial ou segredo no domínio.
- Nenhum `TODO`, placeholder, `NotImplementedError` não contratual ou pseudocódigo
  em entrega homologável.
- Erros públicos específicos; causa original preservada.
- Logging estruturado sem conteúdo sensível.
- IDs e desempates determinísticos; ordem de entrada não deve afetar decisões
  quando a semântica é de conjunto.
- Arquivos `__init__.py` controlam exports; mudanças públicas devem ser conscientes.
- Adaptadores concretos devem ficar fora do núcleo e possuir testes contratuais.
- Alterações arquiteturais devem começar por ADR, não por refatoração oportunista.

---

## 25. Padrões de Testes

Embora este documento não execute ou crie testes, o padrão oficial consolidado é:

1. suíte dedicada por entrega/capacidade;
2. regressão cumulativa desde a fundação homologada;
3. testes unitários de invariantes e estados;
4. testes contratuais para portas e adaptadores;
5. round-trip e rejeição estrita de serialização;
6. determinismo estrutural e, quando aplicável, byte a byte;
7. equivalência sync/async nas APIs que oferecem ambos os modos;
8. cancelamento, falhas externas e preservação da causa;
9. imutabilidade profunda e proteção contra mutação de inputs;
10. ausência de dependências/imports proibidos;
11. logging e nomes de eventos obrigatórios;
12. type hints, docstrings, AST, UTF-8 e estilo;
13. cobertura mínima agregada de 90% para novo código, salvo critério específico
    mais rigoroso;
14. classificação explícita de falhas funcionais, arquiteturais, ambientais e
    legadas;
15. temporários isolados em `runtime/temp` e cache de pytest desabilitado quando
    necessário;
16. nenhum teste deve tocar banco canônico, acervo ou dado permanente sem fixture
    isolada e autorização explícita.

Testes de caracterização são obrigatórios antes de substituir comportamento
legado. Falha ambiental não pode ser ocultada; deve ser reproduzida em ambiente
adequado ou registrada com evidência e impacto.

---

## 26. Critérios de Homologação

Uma entrega do CORE só pode ser homologada quando:

- objetivo e escopo estão fechados e aderentes à Baseline;
- superfícies protegidas e proibições foram respeitadas;
- não há arquitetura paralela ou conceito canônico duplicado;
- contratos públicos estão documentados e importáveis;
- modelos e serialização possuem invariantes e versões explícitas;
- dependências apontam para o núcleo;
- suíte dedicada está aprovada;
- regressão oficial cumulativa está aprovada;
- cobertura mínima definida foi atingida;
- validações estáticas e de encoding estão aprovadas;
- determinismo, logging, erros e cancelamento foram verificados quando aplicáveis;
- limitações e ocorrências ambientais foram classificadas;
- relatório de implementação e evidências estão completos;
- compatibilidade e rollback foram avaliados;
- homologação formal foi registrada pela autoridade competente.

Para mudanças de arquitetura, persistência, segurança, fronteira ou breaking
change, ADR aprovado é pré-condição. Aprovação técnica não substitui homologação
formal.

---

## 27. Roadmap Arquitetural

### 27.1 Homologado

| Marco | Evolução arquitetural consolidada |
|---|---|
| CORE-001 | Fundação do repositório técnico versionável: estrutura, packaging inicial, políticas básicas e baseline de preservação incremental. |
| SPR-008A | Fundação `cko.core`: contratos, identidade, modelos documentais, metadata, erros, logging, config e utils. |
| SPR-008B | Modelo Canônico de Ativos e serialização estrita. |
| SPR-008C | Canonical Inventory Engine em memória. |
| SPR-008D | Contratos públicos de Discovery, service, eventos, mapper e validação. |
| SPR-008E | Provider Foundation: registry, resolver, factory, sessão, cancelamento, checkpoint abstrato, sync/async. |
| SPR-008F | Streaming e batch incremental, cursor, acknowledgement e backpressure. |
| SPR-008G | Resolução auditável de identidade. |
| SPR-008H | Modelo, validação, resolução e negociação de capacidades. |
| SPR-008I | Query Foundation e plano lógico. |
| SPR-008J | Avaliação de QueryPlan sobre subjects em memória. |
| SPR-008K | Índices lógicos e planejamento de uso. |
| SPR-008L | Estatísticas, histogramas e estimativa de custo. |
| SPR-008M | Cost-Based Query Planner e estratégia lógica. |
| SPR-008N | Query Optimizer determinístico, convergente e reversível. |
| SPR-008O | Execution Planner e árvore física descritiva. |
| SPR-008OA | Workspace, limpeza segura, validação ambiental e build determinístico internos. |
| SPR-008P | Execution Engine lógico, operadores e lifecycle de execução. |
| SPR-008Q | Runtime canônico, sessão, recursos lógicos, lifecycle e coordenação do Engine. |

### 27.2 Em desenvolvimento

**Nenhum componente ou Sprint em desenvolvimento integra o baseline oficial deste
documento.** Trabalho não homologado, rascunho ou experimento deve permanecer fora
da arquitetura oficial e não pode ser tratado como dependência.

### 27.3 Planejado

**Nenhuma Sprint posterior está planejada ou autorizada por este documento.** A
Baseline 1.0 identifica capacidades futuras candidatas, descritas na seção 29,
mas sua implementação exige priorização, termo próprio, análise de fronteira e,
quando necessário, ADR. Este roadmap não inicia nem nomeia a SPR-008R.

---

## 28. Componentes homologados

São homologados na data de corte:

- fundação de contratos, identidade, metadata, configuração, erros e utils;
- logging estruturado sem destino imposto;
- modelos documentais e Modelo Canônico de Ativos;
- inventário canônico em memória;
- contratos, service, providers, sessão e streaming de Discovery;
- cancelamento cooperativo e checkpoint abstrato de Discovery;
- resolução de identidade e negociação de capacidades;
- modelo, validação, resolução e avaliação de consultas;
- índices lógicos, estatísticas, histogramas e estimativa de custo;
- Cost-Based Planner;
- Query Optimizer com dez regras canônicas;
- Execution Planner com dez nós canônicos;
- Execution Engine com dez operadores canônicos;
- Runtime, lifecycle, recursos lógicos, sessão, relatório e métricas;
- workspace interno, limpeza segura, validação e build determinístico;
- API pública aditiva e aliases de compatibilidade;
- matrizes de testes e relatórios de implementação A–Q como evidência histórica.

Homologação desses componentes não transforma representações lógicas em
integrações físicas. Em particular, não há provider concreto, armazenamento,
scanner canônico novo, consulta SQL, índice físico ou execução de dados no Engine.

---

## 29. Componentes futuros

As seguintes capacidades são **candidatas arquiteturais**, não implementações nem
Sprints autorizadas:

- adaptadores concretos de Discovery e fontes;
- persistência de sessões, checkpoints, cursores, inventários, planos e relatórios;
- repositórios e Unit of Work canônicos;
- transações e auditoria transversal;
- hashing físico por adaptador, separado do fingerprint lógico;
- classificação neutra e contratos de regras;
- modelos e repositórios de Knowledge Graph, relações e evidências;
- busca e providers de busca;
- relatórios neutros e writers;
- storage abstrato e adaptadores de filesystem/Drive;
- plugins e descoberta controlada de plugins;
- adaptadores de OCR, embeddings, vetores, RAG e LLM;
- operadores de dados concretos para o Engine;
- joins, árvores não unárias, execução paralela e assíncrona;
- cache físico e índices externos;
- políticas homologadas de transição de status/lifecycle;
- gestão agregada de `AssetRelation`;
- integração explícita de Discovery com casos de uso de Inventory na camada de
  aplicação.

Critério de promoção: neutralidade de produto, uso transversal comprovado ou
necessidade aprovada, contrato público, dependências corretas, segurança,
observabilidade, testes contratuais, versionamento, documentação e homologação.

---

## 30. Architectural Decision Records (ADR)

### 30.1 ADRs históricos aceitos

| ADR | Decisão | Motivo e consequência |
|---|---|---|
| ADR-001 | Monólito modular incremental | Evitar microserviços e reorganizações extensas; evoluir por contratos estáveis. |
| ADR-002 | Identidade documental não depende só de nome/path | Caminhos mudam; identidade lógica precisa sobreviver a movimentação e renomeação. |
| ADR-003 | Preservação dos módulos operacionais legados | Reduzir risco de regressão; scanner, metadata, kb, classifier, organizer e utils não são movidos implicitamente. |
| ADR-004 | Banco canônico separado | Isolar migração de bancos legados e impedir interferência em dados existentes. |
| ADR-005A-001 | Persistência aditiva em `cko.persistence` | Preservar `cko.kb`, reduzir colisão por prefixo e rastrear migração. |

### 30.2 Decisões consolidadas deste baseline

As decisões abaixo registram a razão arquitetural das entregas A–Q. Elas
consolidam decisões já implementadas; não criam autorização nova.

**ADR-C01 — Namespace canônico `cko.core`.** Decisão: concentrar novas
capacidades compartilhadas sob uma fronteira única. Motivo: impedir duplicação e
separar evolução canônica de módulos legados. Consequência: exports aditivos e
dependências orientadas ao núcleo.

**ADR-C02 — Modelos imutáveis e serialização estrita.** Decisão: congelamento
profundo, schema explícito e rejeição de campos desconhecidos. Motivo: segurança,
reprodutibilidade e compatibilidade verificável. Consequência: evolução de schema
deve ser deliberada.

**ADR-C03 — Identidade por `CanonicalId`.** Decisão: entidades usam identidade
canônica, não localização. Motivo: estabilidade lógica. Consequência: igualdade de
entidades e referências atravessam movimentações físicas.

**ADR-C04 — Inventory em memória e independente de Discovery.** Decisão: agregado
possui estado lógico próprio e recebe `Asset` explicitamente. Motivo: impedir
acoplamento e efeitos colaterais. Consequência: persistência e integração são
responsabilidade de aplicação/adaptador.

**ADR-C05 — Discovery baseado em portas.** Decisão: sources, providers, mapper,
publisher e validator são contratos. Motivo: suportar múltiplas infraestruturas.
Consequência: nenhum scanner/provider concreto no núcleo.

**ADR-C06 — Registry por instância e resolução determinística.** Decisão: evitar
singleton e ordem de registro. Motivo: testabilidade e composição. Consequência:
prioridade, especificidade e ID determinam escolha.

**ADR-C07 — Streaming incremental com backpressure lógico.** Decisão: processar
um batch por vez e não materializar todo o conjunto. Motivo: previsibilidade de
memória e escala. Consequência: cursor/checkpoint permanecem lógicos e a
persistência é externa.

**ADR-C08 — Resolução de identidade separada da criação de Asset.** Decisão:
evidência gera decisão e eventualmente ID; mapper cria Asset depois. Motivo:
auditabilidade e separação de responsabilidades. Consequência: não há deduplicação
física ou persistência automática.

**ADR-C09 — Capacidades negociadas entre papéis.** Decisão: Provider, Pipeline,
Executor e Consumer declaram capacidades. Motivo: compatibilidade explícita.
Consequência: dependências, versões e conflitos são validados antes da execução.

**ADR-C10 — Linguagem de consulta neutra.** Decisão: `DiscoveryQuery` e
`QueryPlan` não traduzem para SQL/ORM. Motivo: independência de infraestrutura.
Consequência: adaptadores futuros traduzirão contratos homologados.

**ADR-C11 — Índices, estatísticas e custos lógicos.** Decisão: estruturas em
memória precedem índices físicos. Motivo: planejar sem escolher tecnologia.
Consequência: custos são relativos, não benchmarks.

**ADR-C12 — Otimização separada de planejamento.** Decisão: optimizer reescreve
plano equivalente; Cost-Based Planner escolhe estratégia. Motivo: preservar
responsabilidades e reversibilidade. Consequência: optimizer não executa nem
seleciona acesso físico.

**ADR-C13 — Planejamento físico separado da execução.** Decisão: Execution
Planner produz árvore descritiva; Engine a interpreta. Motivo: auditabilidade e
testabilidade. Consequência: plano é validável antes de executar.

**ADR-C14 — Engine lógico e registro de operadores.** Decisão: Engine coordena
operadores sem dados concretos. Motivo: firmar lifecycle e contratos antes de
adaptadores. Consequência: execução atual representa coordenação, não leitura.

**ADR-C15 — Runtime compõe o Engine.** Decisão: Runtime governa lifecycle,
sessão e recursos; Engine executa nós. Motivo: evitar sobreposição. Consequência:
Runtime não executa operadores.

**ADR-C16 — Cancelamento cooperativo e tokens distintos.** Decisão: Discovery e
Runtime possuem tokens próprios sem concorrência embutida. Motivo: portabilidade e
compatibilidade. Consequência: aliases explícitos são permanentes.

**ADR-C17 — Workspace interno isolado.** Decisão: filesystem operacional reside
em `cko.core.workspace` e não na fachada pública. Motivo: resolver build/testes sem
contaminar o domínio. Consequência: caminhos e limpeza são centralizados e seguros.

**ADR-C18 — Logging estruturado sem sink.** Decisão: o núcleo formata e emite,
mas não escolhe destino. Motivo: observabilidade substituível. Consequência:
aplicações configuram handlers.

Novos ADRs DEVEM registrar contexto, alternativas, decisão, consequências,
transição, status, aprovação e documentos afetados.

---

## 31. Restrições permanentes

1. Não criar arquitetura paralela ao `cko.core`.
2. Não fazer o domínio depender de filesystem, banco, rede, API, OCR, IA, Graph,
   RAG, embeddings, cache ou mensageria concretos.
3. Não inserir automaticamente resultados de Discovery no Inventory.
4. Não criar identidade concorrente de `CanonicalId` nem entidade concorrente de
   `Asset`.
5. Não usar nome ou caminho como identidade canônica exclusiva.
6. Não persistir checkpoint, cursor, sessão ou recurso lógico dentro dos motores
   sem adaptador e autorização.
7. Não transformar decisão humana de canonicidade/classificação em efeito
   automático do SDK.
8. Não alterar contratos públicos homologados por decisão local de Sprint.
9. Não reutilizar nomes públicos para semântica diferente; usar aliases explícitos.
10. Não reabrir estados terminais.
11. Não introduzir estado global ou singleton sem ADR.
12. Não registrar conteúdo sensível integral em logs.
13. Não aceitar campos ou versões desconhecidos silenciosamente em envelopes
    estritos.
14. Não remover ou mover legado sem inventário, transição, rollback e ADR.
15. Não tratar `ARCHIVE`, `RELEASES` ou `CHECKPOINTS` como fonte canônica de código.
16. Não considerar caminho absoluto, credencial ou configuração de cliente parte
    do domínio compartilhado.
17. Não medir decisão determinística por tempo de máquina; métricas lógicas devem
    permanecer distinguíveis de métricas físicas.
18. Não interpretar o roadmap como autorização de implementação.
19. Não iniciar SPR posterior a partir deste documento.
20. Não substituir as SPRs e evidências históricas por esta consolidação.

---

## 32. Glossário

**Adapter (Adaptador):** implementação concreta de uma porta do SDK para uma
tecnologia externa.

**Asset:** entidade canônica que representa um ativo do ecossistema.

**Baseline Arquitetural:** conjunto oficial de decisões e documentos que rege a
evolução.

**CanonicalId:** identidade lógica universal do CORE, baseada em UUID.

**CMC:** autoridade/metodologia institucional de canonicidade e governança do
conhecimento; não é substituída pelo SDK.

**Consumer:** aplicação ou componente que usa uma API, stream ou resultado.

**CORE SDK:** núcleo compartilhado de contratos, modelos e motores neutros.

**Discovery:** processo canônico de observar fontes e produzir itens com
proveniência, sem implicar persistência.

**DiscoveredItem:** observação de Discovery; não é `Asset`.

**Execution Plan:** árvore física descritiva produzida pelo Execution Planner.

**Execution Engine:** coordenador lógico que percorre a árvore e invoca operadores.

**Fingerprint lógico:** SHA-256 de material lógico canônico; não é hash de arquivo.

**Homologado:** tecnicamente validado e formalmente aceito na baseline declarada.

**Inventory:** agregado em memória que mantém `Asset` e revisão lógica.

**Logical Index:** representação imutável de indexação em memória; não é índice de
banco ou mecanismo externo.

**Monólito modular:** implantação/processo coeso organizado em módulos com
fronteiras explícitas.

**NK (Núcleo de Conhecimento):** unidade institucional regida por metodologia,
CMC, taxonomia e validação humana.

**Port (Porta):** contrato do núcleo implementável por aplicação ou adaptador.

**Provider:** implementação injetada que fornece observações/capacidades ao
Discovery; providers concretos não integram o baseline canônico.

**QueryPlan:** plano lógico neutro resultante da resolução de consulta.

**QueryExecutionPlan:** decisão lógica de estratégia produzida pelo Cost-Based
Planner.

**Runtime:** coordenador do ciclo de vida do Engine, sessão e recursos lógicos.

**Schema version:** versão do envelope serializado, independente da versão do
pacote.

**Snapshot:** representação imutável de um estado em determinado momento lógico.

**SPR:** unidade formal de evolução com escopo, critérios, evidências e
homologação; este documento não a substitui.

**Streaming:** processamento incremental de batches sem retenção do conjunto
completo.

**Subject:** objeto em memória avaliado por um `QueryPlan`.

**Workspace:** infraestrutura interna e segura de paths, temporários, build e
validação ambiental.

---

## 33. Conclusão

O CKO CORE SDK homologado até a SPR-008Q constitui um núcleo modular, canônico,
determinístico e independente de infraestrutura. A evolução partiu da fundação
versionável do CORE-001, instituiu `cko.core`, consolidou identidade, ativos e
inventário, construiu a cadeia de Discovery e consultas, separou otimização,
planejamento e execução, e encerrou o ciclo com Engine e Runtime coordenativos.

A arquitetura está deliberadamente preparada para adaptadores futuros sem os
antecipar. Seu principal compromisso é preservar fronteiras: domínio não acessa
infraestrutura; Discovery não muta Inventory; planner não executa; Engine não
escolhe estratégia; Runtime não executa operadores; governança não é substituída
por automação.

Todo desenvolvimento futuro DEVE conservar essas separações, a direção das
dependências, a compatibilidade pública, a serialização versionada, a
auditabilidade, a validação e a preservação do legado. Mudança material requer
ADR e homologação. Este documento encerra a consolidação arquitetural em
SPR-008Q e não autoriza, define ou inicia qualquer Sprint posterior.

---

**Fim do Documento Mestre Oficial — ARCH-001**
