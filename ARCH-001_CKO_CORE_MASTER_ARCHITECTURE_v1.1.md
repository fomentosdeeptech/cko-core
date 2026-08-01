# ARCH-001 — CKO CORE SDK — Arquitetura Oficial

> **Status documental:** registro histórico. As referências a `cko` 0.1.0 abaixo pertencem à data de corte original. A baseline vigente é o CKO CORE SDK 1.0.0, homologado até a SPR-017, com 646 exports públicos únicos e resolvidos.

**Classificação:** Documento Mestre Oficial de Arquitetura  
**Status:** Oficial  
**Versão documental:** 1.1  
**Versão arquitetural consolidada:** Baseline Arquitetural 1.0 + CORE-001 + SPR-008A–SPR-008T  
**Data de corte:** 21/07/2026  
**Última entrega considerada:** SPR-008T homologada  
**Próxima Sprint:** não definida por este documento  
**Produto:** CKO CORE SDK  
**Namespace canônico:** `cko.core`  
**Runtime de referência:** Python 3.13 ou superior  
**Distribuição na data de corte:** `cko` 0.1.0  

> Este documento consolida, mas não substitui, os termos, critérios, evidências e
> relatórios individuais das entregas homologadas. Os relatórios das SPRs são os
> registros históricos primários. Nenhuma entrega posterior à SPR-008T integra
> esta arquitetura e este documento não autoriza o início de nova Sprint.

## Controle normativo

As palavras **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **PODE** e **RECOMENDADO** são
normativas. O documento descreve a arquitetura canônica da plataforma, o baseline
efetivamente homologado até a SPR-008T e os limites permitidos para evolução. Um
item futuro não constitui autorização de implementação.

---

## 1. Visão Geral do CORE SDK

O CKO CORE SDK é o núcleo técnico compartilhado da Plataforma CKO. Ele fornece
contratos, modelos, motores, coordenação de execução e portas de infraestrutura
neutras para que CKO, CID, Aurora, Biblioteca Digital, Governança, Downloads e
aplicações futuras componham seus casos de uso sem duplicar capacidades.

A arquitetura oficial é um **monólito modular orientado a domínio**, estruturado
segundo **Ports and Adapters**, com dependências orientadas para o núcleo. O SDK
não é aplicação final e não decide políticas institucionais. Após a SPR-008T, a
baseline contém cinco superfícies:

1. **Fundação canônica:** contratos, identidade, modelos, metadata, configuração,
   exceções, logging e utilitários.
2. **Motores de domínio:** Inventory e Discovery, incluindo consulta, avaliação,
   índices lógicos, estatísticas, optimizer e planners.
3. **Coordenação de execução:** Execution Planner, Execution Engine e Runtime.
4. **Portas de infraestrutura:** Connector Abstraction Foundation e Storage
   Abstraction Foundation, sem I/O concreto.
5. **Adaptadores homologados:** Filesystem Storage Adapter, primeiro adaptador
   concreto, composto pelas portas `Connector` e `Storage`.

Planos, índices, estatísticas, recursos e execuções continuam representações
canônicas e predominantemente em memória. O acesso físico ao filesystem existe
somente dentro de `cko.core.storage.filesystem`; não foi incorporado ao Runtime,
ao Discovery, ao Inventory nem às fundações abstratas.

---

## 2. Objetivos do Projeto

- estabelecer linguagem canônica para ativos, identidades, descobertas,
  consultas, planos, execuções, runtime, conectores e armazenamento;
- permitir reutilização sem acoplamento a produto, cliente ou tecnologia;
- assegurar determinismo, imutabilidade, serialização versionada, validação e
  auditabilidade;
- proteger o legado por evolução aditiva e migração incremental;
- separar domínio, aplicação, portas, adaptadores e governança;
- tornar integrações concretas substituíveis por contratos, registries,
  factories, validators e injeção;
- oferecer planejamento e coordenação lógicos sem confundi-los com execução
  física de dados;
- confinar detalhes físicos aos adaptadores autorizados;
- preservar evidências técnicas suficientes para homologação.

Não são objetivos: GUI, identidade visual, fluxos específicos de cliente,
credenciais, caminhos absolutos de produção, bancos concretos, cloud providers,
OCR/LLM, RAG, embeddings, índices vetoriais ou automações destrutivas.

---

## 3. Princípios Arquiteturais

1. **Domain First.** Modelos e invariantes precedem integrações.
2. **Ports and Adapters.** Tecnologias concretas implementam portas do núcleo.
3. **SDK First.** Capacidades transversais pertencem ao SDK; jornadas ficam nas
   aplicações.
4. **Monólito modular incremental.** Evolução por módulos coesos e ADRs.
5. **Dependências para dentro.** Domínio não importa adaptadores concretos.
6. **Imutabilidade por padrão.** Modelos, snapshots e saídas são imutáveis.
7. **Determinismo.** Ordem, identidade lógica e JSON são reprodutíveis.
8. **Validação antes do commit.** Falhas não deixam estado parcial.
9. **Serialização estrita e versionada.** Campos, tipos, modelos e versões
   desconhecidos são rejeitados.
10. **Preservação do legado.** Módulos históricos não são movidos implicitamente.
11. **Registries por instância.** Estado global e singleton são proibidos por
    padrão.
12. **Composição explícita.** Construtores e validators são injetados.
13. **Cancelamento cooperativo.** O núcleo não embute concorrência de plataforma.
14. **Observabilidade sem destino imposto.** O consumidor escolhe handlers.
15. **Fronteira física confinada.** Caminhos e bytes das operações de Storage só
    aparecem no adaptador; o workspace interno mantém sua fronteira própria.
16. **Localização não é identidade.** `StorageLocation` é lógica; caminho físico
    não integra o contrato canônico.
17. **Governança soberana.** O SDK não substitui CMC ou validação humana.
18. **Evolução por ADR.** Mudanças materiais exigem decisão formal.

---

## 4. Baseline Arquitetural Oficial

A arquitetura descende da Baseline Arquitetural 1.0, composta por
`DISCOVERY-ECOSYSTEM-001`, `DISCOVERY-ECOSYSTEM-002`, `CKO-ARCH-001` e
`CKO-GOV-001`. O baseline técnico deste documento é o estado composto por
**CORE-001** e **SPR-008A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, OA, P, Q,
R, S e T**. A SPR-008OA é a entrega interna de workspace entre O e P.

```text
CKO-GOV-001 / Baseline 1.0
          |
          v
CKO-ARCH-001 / arquitetura canônica da plataforma
          |
          v
ARCH-001 v1.1 / CORE SDK até SPR-008T
          |
          +----> ADRs aceitos
          +----> SPRs homologadas e evidências
          v
Código, namespaces e contratos públicos homologados
```

Em divergência, governança e ADR formal prevalecem sobre interpretação local.

---

## 5. Arquitetura em Camadas

```text
+----------------------------------------------------------------------------+
| PRODUTOS / APLICAÇÕES                                                      |
| CKO | CID | Aurora | Biblioteca Digital | Governança | Downloads           |
+-----------------------------------+----------------------------------------+
                                    | consomem e compõem
                                    v
+----------------------------------------------------------------------------+
| CKO CORE SDK                                                               |
|                                                                            |
| +--------------------------+  +------------------------------------------+ |
| | Fundação canônica        |  | Motores e coordenação                    | |
| | contracts, identity,     |  | inventory, discovery, execution,        | |
| | models, metadata, config |  | runtime                                  | |
| +--------------------------+  +------------------------------------------+ |
|                                                                            |
| +-----------------------------------------------------------------------+  |
| | Portas de infraestrutura                                              |  |
| | cko.core.connectors              cko.core.storage                      |  |
| +------------------------------+-----------------------------+----------+  |
+--------------------------------|-----------------------------|-------------+
                                 | implementadas por            |
                                 v                              v
+----------------------------------------------------------------------------+
| ADAPTADORES                                                               |
| cko.core.storage.filesystem: FilesystemConnector + FilesystemStorage       |
| futuros: bancos | Drive | APIs | OCR | IA | cache | filas                 |
+----------------------------------------------------------------------------+

Camada transversal externa: GOVERNANÇA
CMC | Taxonomia | confidencialidade | canonicidade | validação humana
```

Regras de dependência:

- produtos dependem do SDK e compõem adaptadores;
- adaptadores dependem das portas públicas do SDK;
- `connectors` e `storage` dependem apenas da fundação canônica e não fazem I/O;
- `storage.filesystem` depende de `connectors`, `storage`, logging e biblioteca
  padrão; não depende diretamente de Runtime;
- `discovery` e `inventory` não dependem do adaptador filesystem;
- `execution` consome o plano produzido em Discovery;
- `runtime` compõe o Engine e não executa operadores diretamente;
- `workspace` é interno e não é reexportado por `cko.core`;
- o SDK não depende de produtos ou de tecnologias futuras.

---

## 6. Ports and Adapters

```text
                         +-------------------------+
                         | Aplicação / Composition |
                         +------------+------------+
                                      |
                     registra construtores e cria
                                      v
 +------------------+      +----------+-----------+      +------------------+
 | Connector port   |<-----| FilesystemConnector  |----->| FilesystemSession|
 | ConnectorSession |      +----------+-----------+      +--------+---------+
 +------------------+                 | delega                      |
                                      v                             | vincula
 +------------------+      +----------+-----------+      +----------v-------+
 | Storage port     |<-----| FilesystemStorage    |----->| StorageSession   |
 | StorageLocation  |      +----------+-----------+      +------------------+
 +------------------+                 |
                                      v
                         FilesystemLocationResolver
                                      |
                                      v
                           pathlib / shutil / hashlib
```

`Connector` é a porta operacional genérica; `Storage` é a porta de armazenamento
lógico. O adaptador filesystem implementa ambas sem alterar seus contratos. A
aplicação controla a raiz física e a composição por factories.

---

## 7. Namespaces Oficiais

| Namespace | Natureza | Responsabilidade | Exposição |
|---|---|---|---|
| `cko.core` | fachada | API agregada e aliases compatíveis | pública |
| `cko.core.contracts` | fundação | portas base | pública |
| `cko.core.identity` | fundação | identidade, origem e versão | pública |
| `cko.core.models` | domínio | documentos, eventos e ativos | pública |
| `cko.core.metadata` | domínio | metadata universal | pública |
| `cko.core.config` | fundação | configuração | pública |
| `cko.core.exceptions` | fundação | hierarquia base de erros | pública |
| `cko.core.logging` | transversal | logging estruturado | pública |
| `cko.core.inventory` | motor | inventário canônico em memória | subnamespace público |
| `cko.core.discovery` | motor | Discovery e pipeline de consulta | pública |
| `cko.core.execution` | motor | execução lógica de planos | pública |
| `cko.core.runtime` | coordenação | lifecycle e coordenação do Engine | pública |
| `cko.core.connectors` | porta | abstração genérica de conectores | pública e reexportada |
| `cko.core.storage` | porta | abstração lógica de storage | pública e reexportada |
| `cko.core.storage.filesystem` | adaptador | implementação concreta de filesystem | subnamespace público |
| `cko.core.workspace` | infraestrutura interna | paths, limpeza, validação e build | interna |
| `cko.core.utils` | utilitário | texto e tempo | suporte técnico |

Namespaces legados sob `cko` são preservados por compatibilidade, mas não
constituem extensões do domínio canônico. Novas capacidades DEVEM usar o
namespace autorizado, sem duplicar conceitos.

---

## 8. Árvore Completa do SDK

```text
CORE/
|-- src/
|   |-- main.py
|   `-- cko/
|       |-- core/
|       |   |-- __init__.py                 # fachada pública
|       |   |-- config/                     # settings.py
|       |   |-- connectors/                 # contracts, models, registry,
|       |   |                               # factory, validator, errors
|       |   |-- contracts/                  # base.py
|       |   |-- discovery/                  # foundation, provider, stream,
|       |   |                               # identity, capability, query,
|       |   |                               # index, statistics, optimizer,
|       |   |                               # planners e execution plan
|       |   |-- exceptions/                 # errors.py
|       |   |-- execution/                  # engine, models, operators,
|       |   |                               # pipeline, validator, errors
|       |   |-- identity/                   # identifier, origin, version
|       |   |-- inventory/                  # builder, engine, models,
|       |   |                               # service, validator, errors
|       |   |-- logging/                    # structured.py
|       |   |-- metadata/                   # universal.py
|       |   |-- models/                     # asset, document, event
|       |   |-- runtime/                    # lifecycle, models, resources,
|       |   |                               # runtime, validator, errors
|       |   |-- storage/
|       |   |   |-- contracts.py
|       |   |   |-- models.py
|       |   |   |-- registry.py
|       |   |   |-- factory.py
|       |   |   |-- validator.py
|       |   |   |-- errors.py
|       |   |   `-- filesystem/
|       |   |       |-- connector.py
|       |   |       |-- descriptor.py
|       |   |       |-- factory.py
|       |   |       |-- resolver.py
|       |   |       |-- result.py
|       |   |       |-- session.py
|       |   |       |-- storage.py
|       |   |       `-- validator.py
|       |   |-- utils/                      # text.py, time.py
|       |   `-- workspace/                  # interno
|       |-- classifier/                     # legado preservado
|       |-- contracts/                      # legado preservado
|       |-- kb/                             # legado preservado
|       |-- metadata/                       # legado preservado
|       |-- migrations/                     # histórico
|       |-- models/                         # legado preservado
|       |-- organizer/                      # legado preservado
|       |-- persistence/                    # legado/aditivo
|       |-- repository/                     # legado/adaptador
|       |-- scanner/                        # legado preservado
|       |-- services/                       # legado preservado
|       `-- utils/                          # legado preservado
|-- tests/                                  # suítes legadas e SPR-008A–T
|-- docs/                                   # arquitetura e ADRs históricos
|-- runtime/                                # temp/cache/traces/logs/reports/
|                                           # database/snapshots
|-- CKO_CLEAN.cmd
|-- CKO_TESTS.cmd
|-- CKO_BUILD.cmd
`-- CKO_RUNTIME.cmd
```

Os `__init__.py` definem as superfícies públicas. Consumidores DEVEM evitar
imports de detalhes internos quando o símbolo é exportado pelo pacote.

---

## 9. Fluxo Completo do SDK

### 9.1 Descoberta e incorporação explícita

```text
DiscoveryRequest -> validação -> Provider injetado -> DiscoverySession
       |                                  |
       |                                  +-> DiscoveryResult
       |                                  `-> DiscoveryBatch* / cursor / ack
       v
DiscoveredItem -> IdentityResolutionEngine -> ResolutionDecision
       -> DefaultDiscoveryAssetMapper -> Asset
       -> chamada explícita do consumidor -> InventoryService
```

Discovery NÃO insere automaticamente no Inventory. Identidade, mapping e
persistência permanecem responsabilidades separadas.

### 9.2 Consulta, planejamento e coordenação

```text
DiscoveryQuery
  -> QueryValidationEngine
  -> QueryResolver -> QueryPlan
  -> QueryEvaluationEngine (opcional, em memória)
  -> LogicalIndex / Statistics
  -> OptimizationPipeline
  -> CostBasedPlanner -> QueryExecutionPlan
  -> ExecutionPipeline -> ExecutionPlan
  -> Runtime -> ExecutionEngine -> operadores lógicos -> RuntimeReport
```

### 9.3 Conector e armazenamento

```text
Aplicação
  -> ConnectorRegistry.register(descriptor, constructor)
  -> ConnectorFactory.create(identifier)
  -> ConnectorSession.start(...)
  -> Connector.execute(session)
  -> ConnectorResult

Aplicação
  -> StorageRegistry.register(descriptor, constructor)
  -> StorageFactory.create(identifier)
  -> StorageSession.start(...)
  -> Storage.execute(session)
  -> StorageResult
```

### 9.4 Filesystem integrado

```text
ConnectorSession
  -> FilesystemConnector.execute
  -> FilesystemSession.from_connector
  -> StorageContext + StorageSession
  -> FilesystemStorage.execute
  -> FilesystemLocationResolver.resolve
  -> operação física confinada à raiz
  -> StorageResult
  -> FilesystemResult.from_storage
  -> ConnectorResult
```

`create`, `copy` e `move` são operações do Connector traduzidas localmente para
`StorageOperation.WRITE`, com `filesystem_operation` no `StorageContext`. Essa
ponte não altera o enum canônico de Storage.

---

## 10. Pipeline de Consultas

O pipeline homologado valida, resolve, avalia opcionalmente subjects em memória,
considera índices e estatísticas lógicos, otimiza, seleciona estratégia, produz
plano físico descritivo e coordena sua execução lógica. Nenhuma etapa traduz
consulta para SQL, ORM, API, filesystem ou índice externo.

Ordem de avaliação em memória: filtros, projeção, ordenação e paginação. Missing
attributes, tipos incompatíveis e erros seguem políticas explícitas. Índices e
custos são lógicos e não representam mecanismos físicos.

---

## 11. Execution Planner e Execution Engine

O Execution Planner transforma `QueryExecutionPlan` em `ExecutionPlan` composto
por dez nós canônicos: `RootNode`, `ScanNode`, `IndexScanNode`,
`CompositeIndexScanNode`, `PrefixScanNode`, `OrderedScanNode`, `FilterNode`,
`ProjectionNode`, `SortNode` e `LimitNode`.

O Engine registra e invoca os dez operadores correspondentes. Ele valida a
árvore, controla lifecycle e produz resultados, relatórios e métricas lógicos;
não lê dados concretos. Operadores físicos futuros devem ser adaptadores e não
podem alterar o contrato do plano por conveniência.

---

## 12. Runtime

```text
Runtime.run(ExecutionPlan, RuntimeContext)
        |
        +-> RuntimeValidator
        +-> LifecycleController: CREATED -> RUNNING -> terminal
        +-> ResourceRegistry (recursos lógicos por instância)
        +-> ExecutionEngine.execute
        `-> RuntimeReport + RuntimeMetrics + RuntimeSession
```

O Runtime compõe o Engine, não executa operadores diretamente, não cria threads,
não persiste sessão e não conhece `FilesystemStorage`. `RuntimeCancellationToken`
é alias explícito para evitar colisão com o token de Discovery.

---

## 13. Connector Abstraction Foundation

`cko.core.connectors` é uma porta de integração genérica, homologada na
SPR-008R. O pacote não acessa filesystem, banco, rede, cloud, APIs, OCR ou IA.

| Componente | Responsabilidade |
|---|---|
| `Connector` | ABC com `descriptor` e `execute(ConnectorSession)` |
| `ConnectorDescriptor` | identidade, metadata, capacidades e versão contratual |
| `ConnectorMetadata` | nome, descrição, versão e labels neutros |
| `ConnectorCapabilities` | operações, features e streaming declarado |
| `ConnectorContext` | correlação, operação, parâmetros e metadata |
| `ConnectorSession` | snapshot imutável do lifecycle |
| `ConnectorSessionState` | `started`, `finished`, `failed` |
| `ConnectorResult` | saída lógica sem payload tecnológico obrigatório |
| `ConnectorRegistry` | registro determinístico por instância |
| `ConnectorFactory` | criação por construtor injetado |
| `ConnectorValidator` | invariantes isolados e cruzados |
| `ConnectorException` | falha tipada de contrato/lifecycle |

Registry e Factory armazenam descritor serializável separado do construtor. A
Factory exige que a instância implemente `Connector` e que seu descritor seja
exatamente igual ao registrado. Sessões são imutáveis: `start` cria snapshot e
`finish` retorna novo estado terminal.

---

## 14. Storage Abstraction Foundation

`cko.core.storage` é a porta tecnológica neutra homologada na SPR-008S. O pacote
não faz I/O nem contém provider concreto.

| Componente | Responsabilidade |
|---|---|
| `Storage` | ABC com `descriptor` e `execute(StorageSession)` |
| `StorageDescriptor` | identidade, metadata, capacidades e versão |
| `StorageMetadata` | nome, descrição, versão e labels neutros |
| `StorageCapabilities` | operações e garantias comportamentais |
| `StorageLocation` | namespace e chave lógicos, sem path/URL físico |
| `StorageObject` | descritor lógico, sem conteúdo físico obrigatório |
| `StorageOperation` | `read`, `write`, `delete`, `exists`, `list`, `metadata` |
| `StorageContext` | correlação, operação, localização e parâmetros |
| `StorageSession` | snapshot imutável do lifecycle |
| `StorageSessionState` | `started`, `finished`, `failed` |
| `StorageResult` | resultado lógico de operação |
| `StorageRegistry` | registro determinístico por instância |
| `StorageFactory` | criação por construtor injetado |
| `StorageValidator` | invariantes e compatibilidade de operação |
| `StorageException` | falha tipada de contrato/lifecycle |

O contrato não contém caminho, URL, credencial, handle, conexão ou bytes. A
Factory valida implementação e igualdade do descritor. As garantias de atomic
write, streaming e transações são capacidades declaradas, não presumidas.

---

## 15. Filesystem Storage Adapter

`cko.core.storage.filesystem`, homologado na SPR-008T, é o primeiro adaptador
concreto do CORE. Depende das portas R e S e da biblioteca padrão, sem dependência
direta do Runtime.

| Componente | Responsabilidade |
|---|---|
| `FilesystemStorage` | implementa as operações físicas |
| `FilesystemConnector` | expõe nove operações pela porta Connector |
| `FilesystemDescriptor` | agrupa descritores de Connector e Storage |
| `FilesystemSession` | vincula sessões por ID, correlação e lifecycle |
| `FilesystemResult` | vincula resultados e sucesso equivalentes |
| `FilesystemLocationResolver` | traduz localização lógica para path confinado |
| `FilesystemStorageFactory` | compõe registries e factories públicas |
| `FilesystemStorageValidator` | delega validação às fundações |

Operações: `create`, `read`, `write`, `delete`, `exists`, `list`, `copy`, `move`
e `metadata`. Conteúdo binário cruza envelopes como Base64; texto exige encoding
explícito; listagens são lexicograficamente determinísticas; digests usam SHA-256;
timestamps são normalizados para UTC.

Segurança de localização:

```text
StorageLocation(namespace, key)
        -> rejeita absoluto e ".."
        -> root / namespace / key
        -> resolve(strict=False)
        -> exige candidate.is_relative_to(root)
        -> Path físico autorizado
```

O resolver é a fronteira exclusiva entre localização lógica e caminho físico. A
raiz é fornecida pela aplicação. O adaptador não embute credenciais ou paths de
produção.

---

## 16. Modelos Fundamentais

- identidade e proveniência: `CanonicalId`, `Origin`, `SemanticVersion`;
- documentos e eventos: `CanonicalDocument`, `DocumentLocation`,
  `CanonicalEvent`;
- ativos: `Asset` e subclasses, lifecycle, status, hash, fingerprint,
  classificação e relações;
- inventário: agregado, snapshots, consultas, resultados e estatísticas;
- Discovery: requests, contexts, items, evidências, sessões, batches e planos;
- execução: planos, nós, operadores, resultados, relatórios e métricas;
- Runtime: context, session, state, report, metrics e cancellation;
- Connector e Storage: descritores, capacidades, contextos, sessões e resultados;
- Filesystem: bridges versionadas de descriptor, session e result.

Modelos públicos serializáveis usam envelopes estritos, `schema_version`, campo
`model`, round-trip e JSON determinístico. As fundações R e S usam
`dataclass(frozen=True, slots=True)` e congelamento profundo.

---

## 17. Estados e Lifecycle

| Agregado | Estados principais | Regra |
|---|---|---|
| Asset | status/lifecycle canônicos | transições exigem política aprovada |
| DiscoverySession | created/running/completed/failed/cancelled | terminal não reabre |
| Execution | created/running/succeeded/failed/cancelled | terminal não reabre |
| Runtime | created/running/succeeded/failed/cancelled | controlado pelo lifecycle |
| ConnectorSession | started/finished/failed | snapshots imutáveis |
| StorageSession | started/finished/failed | snapshots imutáveis |

No filesystem, `FilesystemSession` exige igualdade entre IDs de sessão e provider,
correlation IDs equivalentes e mapeamento coerente dos estados públicos.

---

## 18. Validação

Cada fronteira valida seus próprios modelos e invariantes. Validators não fazem
persistência e devem validar antes de mutação. Registries rejeitam duplicidade;
factories preservam a causa de construção; envelopes rejeitam campos extras;
filesystem rejeita traversal e destinos fora da raiz.

```text
entrada -> validação estrutural -> validação semântica -> validação cruzada
        -> construção/execução -> resultado tipado
```

---

## 19. Logging e Observabilidade

O CORE emite eventos estruturados sem configurar sink. Eventos adicionados:

| Módulo | Eventos |
|---|---|
| Connectors | `connector_registered`, `connector_created`, `connector_validated`, `connector_session_started`, `connector_session_finished` |
| Storage | `storage_registered`, `storage_created`, `storage_validated`, `storage_session_started`, `storage_session_finished` |
| Filesystem | `filesystem_open`, `filesystem_read`, `filesystem_write`, `filesystem_delete`, `filesystem_copy`, `filesystem_move`, `filesystem_list` |

Logs não devem conter conteúdo integral, credenciais ou caminhos sensíveis além
do mínimo aprovado para rastreabilidade.

---

## 20. Diagramas Arquiteturais

### 20.1 Contexto da plataforma

```text
[Produtos] ---> [CKO CORE SDK] <--- [Governança]
                     ^
                     |
              [Adaptadores]
                     |
       [Filesystem homologado]
```

### 20.2 Módulos do CORE

```text
contracts identity models metadata config exceptions logging utils
    ^         ^        ^
    |         |        +---- inventory
    |         +------------- discovery -> execution -> runtime
    +----------------------- connectors
    +----------------------- storage <--- storage.filesystem
                              ^               |
                              `---------------+ usa Connector também
```

### 20.3 Sequência de composição do filesystem

```text
App          FSFactory       Registry/Factory      Connector       Storage
 |               |                  |                  |              |
 |-- root ------>|                  |                  |              |
 |               |-- register ---->|                  |              |
 |               |-- create ------>|-- validate ----->|              |
 |<-- adapter ---|                  |                  |              |
 |-- session ---------------------------------------->|              |
 |                                                   |-- translate ->|
 |                                                   |<-- result ----|
 |<-------------------------------- ConnectorResult --|              |
```

### 20.4 Sequência de acesso físico

```text
StorageSession -> FilesystemStorage -> Validator -> Resolver -> filesystem
       ^                                      |             |
       |                                      +-- confined -+
       `---------------- StorageResult -----------------------
```

---

## 21. Dependências entre módulos

| Consumidor | Dependências permitidas | Dependências proibidas |
|---|---|---|
| `inventory` | models, identity, metadata, logging | discovery, adapters |
| `discovery` | foundation, logging | inventory, filesystem |
| `execution` | execution plan models, logging | storage físico |
| `runtime` | execution, foundation, logging | filesystem direto |
| `connectors` | logging, biblioteca padrão | I/O, tecnologia concreta |
| `storage` | logging, biblioteca padrão | I/O, tecnologia concreta |
| `storage.filesystem` | connectors, storage, logging, stdlib | runtime direto, produto |
| `workspace` | pathlib e infraestrutura local | fachada pública |

Direção consolidada:

```text
Produto -> Runtime -> Execution -> Discovery -> Fundação
Produto -> Connector port --------------------> Fundação
Produto -> Storage port ----------------------> Fundação
Produto -> Filesystem adapter -> Connector + Storage ports
```

Não existe dependência inversa do núcleo para o adaptador.

---

## 22. Contratos Públicos

### 22.1 Fundação

`Repository`, `Clock`, `EventPublisher`, `Plugin`, `Identifiable`, `CanonicalId`,
`Origin`, `SemanticVersion`, modelos canônicos, metadata, config, erros e logging.

### 22.2 Inventory, Discovery, Execution e Runtime

As superfícies públicas permanecem as homologadas nas SPR-008A–Q: modelos,
contratos, services, providers, streaming, identidade, capability, query,
indexação, estatísticas, optimizer, planners, nós, operadores, Engine, Runtime,
reports, metrics, validators e erros. `cko.core` reexporta a seleção canônica;
subnamespaces mantêm suas superfícies especializadas.

### 22.3 Connector

`CONNECTOR_SCHEMA_VERSION`, `CONNECTOR_VERSION`, `Connector`,
`ConnectorCapabilities`, `ConnectorConstructor`, `ConnectorContext`,
`ConnectorDescriptor`, `ConnectorException`, `ConnectorFactory`,
`ConnectorMetadata`, `ConnectorRegistry`, `ConnectorResult`, `ConnectorSession`,
`ConnectorSessionState`, `ConnectorValidator`.

### 22.4 Storage

`STORAGE_SCHEMA_VERSION`, `STORAGE_VERSION`, `Storage`, `StorageCapabilities`,
`StorageConstructor`, `StorageContext`, `StorageDescriptor`, `StorageException`,
`StorageFactory`, `StorageLocation`, `StorageMetadata`, `StorageObject`,
`StorageOperation`, `StorageRegistry`, `StorageResult`, `StorageSession`,
`StorageSessionState`, `StorageValidator`.

### 22.5 Filesystem

`FILESYSTEM_IDENTIFIER`, `FILESYSTEM_OPERATIONS`, `FILESYSTEM_SCHEMA_VERSION`,
`FILESYSTEM_VERSION`, `FilesystemConnector`, `FilesystemDescriptor`,
`FilesystemLocationResolver`, `FilesystemResult`, `FilesystemSession`,
`FilesystemStorage`, `FilesystemStorageFactory`, `FilesystemStorageValidator`.

Os contratos R e S são reexportados por `cko.core`; o adaptador filesystem é
exposto pelo subnamespace `cko.core.storage.filesystem` e não é reexportado pela
fachada raiz. Essa assimetria é intencional: portas pertencem à API canônica;
adaptadores são selecionados explicitamente pela aplicação.

---

## 23. Pontos de Extensão

| Ponto | Mecanismo | Regra |
|---|---|---|
| Connector | subclasse de `Connector` | descritor e sessão compatíveis |
| Storage | subclasse de `Storage` | localização permanece lógica |
| Registro | constructor zero-argument injetado | sem singleton |
| Validação | validators compostos | sem I/O implícito |
| Discovery Provider | contracts e registry próprios | sem inserção automática |
| Execution Operator | registry de operadores | respeitar nó e lifecycle |
| Logging | handlers da aplicação | SDK não escolhe destino |
| Filesystem | root injetada e resolver | confinamento obrigatório |

Adaptadores futuros de Drive, banco ou cloud DEVEM implementar as portas sem
introduzir detalhes tecnológicos nos modelos canônicos.

---

## 24. Compatibilidade e Versionamento

- evolução pública é aditiva por padrão;
- breaking change exige major version, migração, rollback, ADR e homologação;
- `schema_version` é independente da versão do pacote;
- aliases públicos aprovados não podem mudar de semântica;
- construtores, métodos abstratos e envelopes não podem ser alterados por
  conveniência de adaptador;
- Python 3.13, UTF-8 e biblioteca padrão permanecem o baseline homologado;
- Connector, Storage e Filesystem usam schema `1.0` e versão `1.0.0`.

---

## 25. Padrões de Desenvolvimento e Testes

Código de produção deve possuir type hints, docstrings públicas, UTF-8, estilo
consistente, erros tipados e ausência de dependências externas não autorizadas.
Testes devem cobrir contratos, invariantes, round-trip, determinismo, falhas,
logging e regressão.

Para adaptadores de I/O, são obrigatórios testes de confinamento, entradas
inválidas, arquivos ausentes, conteúdo textual/binário, ordenação e não
dependência do Runtime. Testes não tornam uma integração canônica sem homologação.

---

## 26. Critérios de Homologação

Uma entrega integra o baseline somente quando escopo, contratos, dependências,
testes dedicados, regressão, cobertura, encoding, documentação, compatibilidade,
rollback e aceite formal estão registrados. Mudanças de fronteira, persistência,
segurança ou breaking changes exigem ADR quando aplicável.

As evidências registradas para R, S e T são:

| Entrega | Suíte dedicada | Cobertura ponderada | Regressão registrada |
|---|---:|---:|---:|
| SPR-008R | 40 passed | 96% | 486 passed, 2 falhas legadas |
| SPR-008S | 86 passed | 96% | 572 passed, 2 falhas legadas |
| SPR-008T | 29 passed | 92,85% | 601 passed, 2 falhas legadas |

As duas ocorrências legadas são independentes das três entregas: divergência do
argumento `calculate_hash` em `collect_metadata` e arquivo SQLite aberto no
teardown Windows de persistência.

---

## 27. Roadmap Arquitetural

### 27.1 Homologado

| Marco | Evolução consolidada |
|---|---|
| CORE-001 | Fundação versionável do repositório e preservação incremental |
| SPR-008A | Fundação `cko.core` |
| SPR-008B | Modelo Canônico de Ativos |
| SPR-008C | Inventory Engine em memória |
| SPR-008D | Contratos públicos de Discovery |
| SPR-008E | Provider Foundation |
| SPR-008F | Streaming e batch incremental |
| SPR-008G | Resolução de identidade |
| SPR-008H | Capability model e negociação |
| SPR-008I | Query Foundation |
| SPR-008J | Avaliação de query em memória |
| SPR-008K | Índices lógicos |
| SPR-008L | Estatísticas e custo |
| SPR-008M | Cost-Based Planner |
| SPR-008N | Query Optimizer |
| SPR-008O | Execution Planner |
| SPR-008OA | Workspace interno e build determinístico |
| SPR-008P | Execution Engine lógico |
| SPR-008Q | Runtime canônico |
| SPR-008R | Connector Abstraction Foundation |
| SPR-008S | Storage Abstraction Foundation |
| SPR-008T | Filesystem Storage Adapter |

### 27.2 Em desenvolvimento

Nenhum componente ou Sprint em desenvolvimento integra este baseline.

### 27.3 Planejado

Nenhuma Sprint posterior é planejada ou autorizada por este documento. As
capacidades futuras da seção 29 exigem termo próprio e homologação.

---

## 28. Componentes Homologados

Além das fundações, motores e coordenação A–Q, estão homologados:

- porta Connector completa, registry, factory, validator e modelos;
- porta Storage completa, localização lógica, registry, factory e validator;
- adaptador filesystem com nove operações, bridges Connector/Storage, resolver
  confinado, composição por factories e logging estruturado;
- APIs aditivas e matrizes de testes A–T.

Somente o adaptador filesystem realiza I/O concreto. Isso não transforma Engine,
Runtime, Discovery ou Storage Foundation em executores físicos.

---

## 29. Componentes Futuros

Capacidades candidatas, não autorizadas:

- adaptadores de Discovery e fontes externas;
- adaptadores Storage para Drive, banco, S3, Azure Blob e equivalentes;
- persistência de sessões, checkpoints, cursores, inventários e relatórios;
- Unit of Work, transações e auditoria transversal;
- plugins e descoberta controlada de plugins;
- busca física, Knowledge Graph, OCR, embeddings, vetores, RAG e LLM;
- operadores de dados concretos, joins, árvores não unárias e paralelismo;
- cache físico e índices externos;
- políticas institucionais adicionais de lifecycle e classificação.

O storage abstrato e o adaptador filesystem deixam de ser itens futuros nesta
versão; ambos estão homologados. Novos adaptadores devem reutilizar os contratos
existentes.

---

## 30. Architectural Decision Records (ADR)

### 30.1 ADRs históricos aceitos

| ADR | Decisão |
|---|---|
| ADR-001 | Monólito modular incremental |
| ADR-002 | Identidade documental não depende apenas de nome/path |
| ADR-003 | Preservação dos módulos operacionais legados |
| ADR-004 | Banco canônico separado |
| ADR-005A-001 | Persistência aditiva em `cko.persistence` |

### 30.2 Decisões consolidadas A–Q

Permanecem aceitas as decisões do baseline anterior: namespace `cko.core`,
modelos imutáveis, `CanonicalId`, Inventory independente, Discovery por portas,
registries por instância, streaming incremental, resolução de identidade
separada, capacidades negociadas, query neutra, estruturas lógicas, optimizer
separado do planner, planejamento separado da execução, Engine lógico, Runtime
compondo Engine, cancelamento cooperativo, workspace interno e logging sem sink.

### 30.3 Decisões consolidadas R–T

**ADR-C19 — Connector como porta genérica.** Decisão: padronizar descritor,
capacidades, contexto, sessão, resultado, registry, factory e validator sem
tecnologia concreta. Consequência: adaptadores implementam `Connector` e são
compostos pela aplicação.

**ADR-C20 — Storage lógico independente de infraestrutura.** Decisão:
`StorageLocation` usa namespace/chave e `StorageObject` não contém representação
física obrigatória. Consequência: paths, URLs, conexões e bytes ficam fora do
contrato canônico.

**ADR-C21 — Registries e factories paralelos, não globais.** Decisão: Connector e
Storage possuem composição por instância e construtores injetados. Consequência:
isolamento, testabilidade e ausência de service locator global.

**ADR-C22 — Filesystem como adaptador duplo.** Decisão: implementar `Connector` e
`Storage`, vinculando sessões e resultados. Consequência: consumidores podem usar
a porta adequada sem duplicar acesso físico.

**ADR-C23 — Resolver como fronteira física exclusiva.** Decisão: concentrar a
tradução `StorageLocation`/`Path` e exigir confinamento à raiz. Consequência:
traversal e paths absolutos são rejeitados antes do I/O.

**ADR-C24 — Operações físicas adicionais traduzidas localmente.** Decisão:
`create`, `copy` e `move` usam `StorageOperation.WRITE` com discriminador
`filesystem_operation`. Consequência: o adaptador preserva o enum Storage 1.0.

**ADR-C25 — Adaptador fora do Runtime.** Decisão: não acoplar filesystem ao
coordenador lógico. Consequência: aplicações compõem explicitamente Runtime,
Connector e Storage quando um caso de uso exigir ambos.

Novos ADRs DEVEM registrar contexto, alternativas, decisão, consequências,
transição, status, aprovação e documentos afetados.

---

## 31. Restrições Permanentes

1. Não criar arquitetura paralela ao `cko.core`.
2. Não fazer domínio, Engine ou Runtime depender de adaptador concreto.
3. Não inserir resultados de Discovery automaticamente no Inventory.
4. Não criar identidade concorrente de `CanonicalId` ou `Asset`.
5. Não tratar caminho como identidade canônica.
6. Não adicionar path, URL, credencial, conexão ou bytes aos contratos Storage.
7. Não permitir que `connectors` ou `storage` façam I/O.
8. Não permitir filesystem fora da raiz configurada.
9. Não reabrir sessões terminais.
10. Não alterar contratos R/S para acomodar adaptador.
11. Não introduzir singleton ou estado global sem ADR.
12. Não registrar conteúdo sensível integral em logs.
13. Não aceitar campos ou versões desconhecidos silenciosamente.
14. Não mover legado sem inventário, transição, rollback e ADR.
15. Não interpretar roadmap como autorização.
16. Não iniciar Sprint posterior a partir deste documento.

---

## 32. Glossário

**Adapter:** implementação concreta de uma porta para tecnologia externa.

**Connector:** porta operacional genérica baseada em descritor, contexto, sessão
e resultado.

**Filesystem Adapter:** implementação concreta homologada que compõe Connector e
Storage sob uma raiz física confinada.

**Inventory:** agregado em memória de ativos canônicos.

**Port:** contrato do núcleo implementável por aplicação ou adaptador.

**Provider:** implementação injetada que fornece observações ao Discovery; não é
sinônimo de Storage.

**Runtime:** coordenador do ciclo de vida do Engine e de recursos lógicos.

**Storage:** porta de operações lógicas de armazenamento.

**StorageLocation:** localização por namespace/chave, sem representação física.

**StorageObject:** descritor lógico de um objeto armazenado.

**Snapshot:** representação imutável de estado em momento lógico.

**Schema version:** versão do envelope serializado, independente do pacote.

---

## 33. Matriz de Sincronização Arquitetural

| Dimensão | Fonte verificada | Estado v1.1 |
|---|---|---|
| Namespaces | árvore real sob `src/cko/core` | sincronizada até `storage.filesystem` |
| API raiz | `cko.core.__all__` | inclui Connector e Storage; exclui adapter |
| APIs de pacote | `__all__` de connectors/storage/filesystem | listadas na seção 22 |
| Dependências | imports de produção e testes R–T | direção Ports and Adapters confirmada |
| Runtime | implementação e testes SPR-008Q/T | sem dependência de filesystem |
| Roadmap | relatórios CORE-001 e SPR-008A–T | R, S e T homologadas |
| Evidências | relatórios e suítes dedicadas | resultados registrados na seção 26 |

Inconsistências históricas conhecidas e preservadas:

1. `tests/test_file_metadata.py` usa `calculate_hash`, ausente no contrato legado
   atual de `collect_metadata`.
2. `test_existing_table_is_preserved` pode manter `cko.db` aberto no teardown do
   Windows (`WinError 32`).

Essas ocorrências não afetam `cko.core.connectors`, `cko.core.storage` ou
`cko.core.storage.filesystem` e não foram corrigidas por esta atualização
documental.

---

## 34. Conclusão

A arquitetura oficial do CKO CORE SDK está sincronizada, na data de corte, com o
código homologado de CORE-001 e SPR-008A–SPR-008T. Connector Abstraction
Foundation, Storage Abstraction Foundation e Filesystem Storage Adapter integram
formalmente o baseline, com namespaces, contratos, dependências, fluxos,
sequências, diagramas, componentes, pontos de extensão, roadmap e ADRs refletidos
nesta versão 1.1.

Nenhuma Sprint posterior é iniciada ou autorizada por este documento.
