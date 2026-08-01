# ARCH-001 — CKO CORE Master Architecture v1.2

**Documento:** ARCH-001  
**Versão:** 1.2  
**Produto:** CKO CORE SDK  
**Release:** 1.0.0  
**Data de corte:** 2026-07-25  
**Sprint de consolidação:** SPR-009A  
**Estado:** arquitetura normativa homologada

## 1. Propósito e autoridade

Este documento é a arquitetura normativa do CKO CORE SDK 1.0.0. Ele substitui
a v1.1 como referência corrente e preserva o histórico das versões anteriores.
A arquitetura descrita corresponde aos 153 módulos Python implementados sob
`src/cko/core`, incluindo as entregas SPR-008A–W, SPR-008OA e a consolidação
SPR-009A.

O CORE é uma fundação modular, síncrona, local-first, sem dependências externas
de produção. Ele oferece modelos canônicos, Discovery, planejamento, execução,
Runtime, ports de Connector e Storage, adapters Filesystem e SQLite, Checkpoint,
Unit of Work, workspace/build e Composition Root. A Camada Semântica e Knowledge
Objects não fazem parte desta baseline.

## 2. Princípios obrigatórios

1. Dependências apontam para contratos e modelos, nunca para tecnologia.
2. Runtime, Discovery e Execution não importam adapters concretos.
3. Connector e Storage são ports independentes de infraestrutura.
4. Registries são por instância; estado global de composição é proibido.
5. `CompositionRoot` é a entrada oficial de inicialização integrada.
6. `CKOError` é a única raiz de exceções declaradas pelo CORE.
7. Modelos e serializações homologados não mudam sem versionamento explícito.
8. Workspace e Build são infraestrutura lateral, não dependências de domínio.
9. O CORE de produção usa somente a biblioteca padrão do Python.
10. APIs homologadas permanecem retrocompatíveis durante a linha 1.x.

## 3. Visão em camadas

```text
Aplicação ou produto CKO
└── CompositionRoot
    ├── Coordenação
    │   ├── Runtime
    │   ├── Checkpoint
    │   └── Unit of Work
    ├── Motores
    │   ├── Inventory
    │   ├── Discovery e Query
    │   ├── Planner e Optimizer
    │   ├── Execution Planner
    │   └── Execution Engine
    ├── Ports
    │   ├── Connector
    │   └── Storage
    ├── Adapters
    │   ├── Filesystem
    │   └── SQLite
    ├── Infraestrutura lateral
    │   ├── Workspace
    │   ├── Build
    │   └── Logging
    └── Fundação
        ├── contracts e exceptions
        ├── identity e metadata
        ├── models e config
        └── utils
```

## 4. Árvore implementada

```text
cko.core
├── checkpoint
│   ├── contracts.py
│   ├── engine.py
│   ├── errors.py
│   ├── models.py
│   ├── repository.py
│   ├── serializer.py
│   └── validator.py
├── composition
│   ├── models.py
│   └── root.py
├── config
│   └── settings.py
├── connectors
│   ├── contracts.py
│   ├── errors.py
│   ├── factory.py
│   ├── models.py
│   ├── registry.py
│   └── validator.py
├── contracts
│   └── base.py
├── discovery
│   ├── base, providers, service, session e pipeline
│   ├── streaming
│   ├── identity resolution
│   ├── capability negotiation
│   ├── query e evaluation
│   ├── logical index e statistics
│   ├── cost-based planner e optimizer
│   └── execution planner
├── exceptions
│   └── errors.py
├── execution
│   ├── engine.py
│   ├── errors.py
│   ├── models.py
│   ├── operators.py
│   ├── pipeline.py
│   └── validator.py
├── identity
│   ├── identifier.py
│   ├── origin.py
│   └── version.py
├── inventory
│   ├── builder.py
│   ├── engine.py
│   ├── errors.py
│   ├── models.py
│   ├── service.py
│   └── validator.py
├── logging
│   └── structured.py
├── metadata
│   └── universal.py
├── models
│   ├── asset.py
│   ├── document.py
│   └── event.py
├── runtime
│   ├── cancellation.py
│   ├── errors.py
│   ├── lifecycle.py
│   ├── models.py
│   ├── resources.py
│   ├── runtime.py
│   └── validator.py
├── storage
│   ├── contracts.py, models.py, registry.py, factory.py e validator.py
│   ├── filesystem
│   │   ├── connector.py, storage.py, descriptor.py e factory.py
│   │   └── resolver.py, result.py, session.py e validator.py
│   └── sqlite
│       ├── connector.py, storage.py, descriptor.py e factory.py
│       └── resolver.py, result.py, session.py e validator.py
├── uow
│   ├── contracts.py
│   ├── engine.py
│   ├── errors.py
│   ├── models.py
│   └── validator.py
├── utils
│   ├── text.py
│   └── time.py
└── workspace
    ├── build.py
    ├── cleaner.py
    ├── cli.py
    ├── manager.py
    ├── paths.py
    └── validator.py
```

Cada diretório também contém seu `__init__.py`. O inventário total é de 153
arquivos Python e 29.911 linhas físicas.

## 5. Responsabilidades

| Componente | Responsabilidade | Não pode fazer |
|---|---|---|
| Foundation | identidade, metadata, contratos e erros | importar engines ou adapters |
| Inventory | agregado e consulta in-memory | persistência direta |
| Discovery | descoberta, query, avaliação e planning | escolher storage concreto |
| Execution Planner | produzir árvore física validada | executar operadores |
| Execution Engine | executar operadores lógicos | acessar infraestrutura |
| Runtime | lifecycle, recursos, cancelamento e relatório | compor adapters |
| Connector | contrato de integração orientado a sessão | fixar tecnologia |
| Storage | contrato de objeto/localização/operação | importar adapter |
| Filesystem | implementar Connector e Storage em filesystem | importar SQLite |
| SQLite | implementar Connector e Storage em SQLite | importar Filesystem |
| Checkpoint | snapshot versionado por Storage port | importar adapter concreto |
| Unit of Work | commit lógico e compensação | transação distribuída implícita |
| Workspace | paths, limpeza e validação do ambiente | entrar no domínio |
| Build | wheel determinístico | resolver dependências externas |
| Logging | formatter e logger estruturado | decidir política de produto |
| Composition Root | montar o grafo completo | executar função de negócio |

## 6. Ports oficiais

| Família | Ports e protocolos públicos |
|---|---|
| Foundation | `Repository`, `Clock`, `EventPublisher`, `Plugin`, `Identifiable` |
| Discovery | `DiscoverySource`, `DiscoveryProvider`, `DiscoveryAssetMapper`, `DiscoveryEventPublisher`, `DiscoveryValidator` |
| Discovery execution | `AsyncDiscoveryProvider`, `ContextualDiscoveryProvider` |
| Streaming | `BatchProducer`, `BatchConsumer`, `AsyncBatchProducer`, `AsyncBatchConsumer` |
| Identity | `IdentityCandidateProvider`, `IdentityEvidenceEvaluator`, `CanonicalIdentityAllocator` |
| Query evaluation | `AttributeResolver`, `QueryEvaluationSubject`, `QueryEvaluationStream` |
| Connector | `Connector` |
| Storage | `Storage` |
| Execution | `ExecutionOperator` |
| Checkpoint | `CheckpointEngine`, `CheckpointRepository`, `CheckpointSerializer` |
| Unit of Work | `UnitOfWork` |

## 7. Adapters e implementações padrão

| Port | Implementações oficiais |
|---|---|
| Connector | `FilesystemConnector`, `SQLiteConnector` |
| Storage | `FilesystemStorage`, `SQLiteStorage` |
| CheckpointRepository | `StorageCheckpointRepository` |
| CheckpointSerializer | `DefaultCheckpointSerializer` |
| CheckpointEngine | `DefaultCheckpointEngine` |
| UnitOfWork | `DefaultUnitOfWork` |
| DiscoveryValidator | `DefaultDiscoveryValidator` |
| DiscoveryAssetMapper | `DefaultDiscoveryAssetMapper` |
| AttributeResolver | `DefaultAttributeResolver` |
| QueryEvaluationStream | `DefaultQueryEvaluationStream` |
| CanonicalIdentityAllocator | `DefaultCanonicalIdentityAllocator` |
| IdentityEvidenceEvaluator | `DefaultNeutralEvidenceEvaluator` |

## 8. Registries e factories

| Categoria | Símbolos | Escopo |
|---|---|---|
| Registry | `DiscoveryProviderRegistry` | instância do composition graph |
| Registry | `ConnectorRegistry` | instância do composition graph |
| Registry | `StorageRegistry` | instância do composition graph |
| Factory | `DiscoveryProviderFactory` | seleção por capability e modo |
| Factory | `ConnectorFactory` | construção por descriptor registrado |
| Factory | `StorageFactory` | construção por descriptor registrado |
| Factory de adapter | `FilesystemStorageFactory` | Connector e Storage Filesystem |
| Factory de adapter | `SQLiteStorageFactory` | Connector e Storage SQLite |
| Composition factory | `CompositionRoot.compose`, `compose_core` | grafo completo |
| Lifecycle factory | `CoreComposition.create_runtime` | Runtime fresco |
| Lifecycle factory | `CoreComposition.create_unit_of_work` | UoW fresco |

## 9. Validators

O Composition Root instancia e publica 16 validators:

| Chave | Implementação |
|---|---|
| `checkpoint` | `CheckpointValidator` |
| `connector` | `ConnectorValidator` |
| `discovery` | `DefaultDiscoveryValidator` |
| `environment` | `EnvironmentValidator` |
| `execution_engine` | `ExecutionEngineValidator` |
| `execution_plan` | `ExecutionPlanValidator` |
| `filesystem` | `FilesystemStorageValidator` |
| `inventory` | `InventoryValidator` |
| `logical_index` | `LogicalIndexValidator` |
| `optimizer` | `OptimizerValidator` |
| `planner` | `PlannerValidator` |
| `runtime` | `RuntimeValidator` |
| `sqlite` | `SQLiteStorageValidator` |
| `statistics` | `StatisticsValidator` |
| `storage` | `StorageValidator` |
| `unit_of_work` | `UnitOfWorkValidator` |

`QueryValidationEngine`, `CapabilityValidationEngine` e validadores internos de
modelos preservam suas responsabilidades, mas não são classificados como classes
`*Validator` no registry transversal.

## 10. Modelos públicos

### 10.1 Fundação, assets e Inventory

```text
SDKConfig
CanonicalId, Origin, SemanticVersion, UniversalMetadata
Asset, AssetClassification, AssetFingerprint, AssetHash, AssetLifecycle
AssetRelation, AssetStatus, AudioAsset, DatabaseAsset, DocumentAsset
FolderAsset, ImageAsset, KnowledgeAsset, ProjectAsset, ReferenceAsset, VideoAsset
CanonicalDocument, DocumentLocation, InventoryItem, CanonicalEvent
InventoryCollection, InventoryFilter, InventoryQuery, InventoryResult
InventorySnapshot, InventoryStatistics, InventorySummary
```

### 10.2 Discovery, streaming, identity e capability

```text
DiscoveredItem, DiscoveryBatch, DiscoveryCapability, DiscoveryContext
DiscoveryErrorRecord, DiscoveryEvidence, DiscoveryMetrics, DiscoveryPolicy
DiscoveryRequest, DiscoveryResult, DiscoveryScope, DiscoverySourceId
DiscoveryStatus, DiscoveryWarning
DiscoveryExecutionContext, DiscoveryExecution, DiscoveryCheckpoint
DiscoverySession, DiscoverySessionMetrics, DiscoverySessionState
DiscoveryProviderDescriptor, DiscoveryExecutionMode
BatchConsumptionContext, BatchProductionContext, BackpressurePolicy
BatchAcknowledgement, BatchAcknowledgementStatus, BatchCursor
ConsumerUnavailableBehavior, DiscoveryStreamState, StreamMetrics
StreamingExecution
ConflictBehavior, ConflictSeverity, EvidenceEvaluation
IdentityCandidate, IdentityConflict, IdentityEvidence, IdentityEvidenceType
IdentityFingerprint, IdentityResolutionRequest, InsufficientEvidenceBehavior
ResolutionDecision, ResolutionPolicy, ResolutionStatus
Capability, CapabilityCategory, CapabilityReport, CapabilityRequirement
CapabilityRequirementType, CapabilitySet
```

### 10.3 Query, index, statistics e planning

```text
DiscoveryQuery, FilterGroup, FilterGroupOperator, QueryFilter, QueryOperator
QueryOrdering, QueryOrderingDirection, QueryPagination, QueryPlan, QueryProjection
AttributeValue, MappingQueryEvaluationSubject, EvaluationErrorBehavior
IncompatibleTypeBehavior, MissingAttributeBehavior, OrderingValuePosition
PredicateEvaluationRecord, ProjectedQueryItem, QueryEvaluationContext
QueryEvaluationPolicy, QueryEvaluationResult, QueryMatchResult
DiscardedLogicalIndex, DuplicateBehavior, IndexStrategy, LogicalIndex
LogicalIndexEntry, LogicalIndexPolicy, LogicalIndexReport
LogicalIndexStatistics, QueryIndexPlan
AttributeStatistics, CostEstimate, EstimationStrategy, Histogram
HistogramBucket, HistogramPolicy, LogicalStatistics, StatisticsPolicy
StatisticsReport
PlannerDecision, PlannerMetrics, PlannerPolicy, PlannerReport, PlannerWeights
QueryExecutionPlan, QueryExecutionStrategy
OptimizationCategory, OptimizationContext, OptimizationDecision
OptimizationDecisionStatus, OptimizationMetrics, OptimizationReport
OptimizationResult, OptimizationRule
```

### 10.4 Execution Planner, Execution Engine e Runtime

```text
CompositeIndexScanNode, ExecutionContext, ExecutionMetrics, ExecutionNode
ExecutionNodeType, ExecutionPlan, ExecutionReport, FilterNode, IndexScanNode
LimitNode, OrderedScanNode, PrefixScanNode, ProjectionNode, RootNode, ScanNode
SortNode
execution.ExecutionContext, execution.ExecutionMetrics, ExecutionResult
ExecutionState, OperatorResult, PipelineResult
RuntimeContext, RuntimeMetrics, RuntimeReport, RuntimeSession, RuntimeState
```

Na fachada raiz, os modelos de Execution Engine usam os aliases
`EngineExecutionContext`, `EngineExecutionMetrics` e `EngineExecutionPipeline`.
O cancellation token de Runtime usa `RuntimeCancellationToken`.

### 10.5 Connector, Storage, adapters, Checkpoint e Unit of Work

```text
ConnectorCapabilities, ConnectorContext, ConnectorDescriptor
ConnectorMetadata, ConnectorResult, ConnectorSession, ConnectorSessionState
StorageCapabilities, StorageContext, StorageDescriptor, StorageLocation
StorageMetadata, StorageObject, StorageOperation, StorageResult
StorageSession, StorageSessionState
FilesystemDescriptor, FilesystemResult, FilesystemSession
SQLiteDescriptor, SQLiteResult, SQLiteSession
CheckpointCollection, CheckpointContext, CheckpointIdentifier
CheckpointMetadata, CheckpointOperation, CheckpointPayload, CheckpointQuery
CheckpointRecord, CheckpointResult, CheckpointSnapshot, CheckpointState
UnitOfWorkContext, UnitOfWorkOperation, UnitOfWorkRepository
UnitOfWorkResult, UnitOfWorkState
```

### 10.6 Workspace, Build e Composition

```text
RuntimePaths, CleanResult, EnvironmentValidationResult, ValidationCheck
BuildResult
CoreCompositionSettings, CoreComposition, BuildInfrastructure
```

Workspace e `BuildResult` são públicos no subnamespace de infraestrutura.
Composition é API pública da fachada raiz.

## 11. Modelos de versão e schemas

| Escopo | Versão |
|---|---|
| distribuição `cko` | `1.0.0` |
| `cko.core.__version__` | `1.0.0` |
| Connector, Storage, Filesystem, SQLite, Checkpoint, UoW | componente `1.0.0` |
| Runtime, Execution e planners | constantes próprias homologadas |
| schemas serializados | preservados sem alteração |

`pyproject.toml`, `PKG-INFO`, nome do wheel e `METADATA` declaram `1.0.0`.

## 12. Matriz de dependências

`X` indica import direto permitido. `CR` indica dependência exclusiva do
Composition Root.

| Consumidor / Provedor | found. | discovery | execution | runtime | connector | storage | adapters | checkpoint | uow | workspace |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| foundation | X | — | — | — | — | — | — | — | — | — |
| inventory | X | — | — | — | — | — | — | — | — | — |
| discovery | X | X | — | — | — | — | — | — | — | — |
| execution | — | X | X | — | — | — | — | — | — | — |
| runtime | — | X | X | X | — | — | — | — | — | — |
| connector port | — | — | — | — | X | — | — | — | — | — |
| storage port | — | — | — | — | X | X | — | — | — | — |
| adapters | — | — | — | — | X | X | X | — | — | — |
| checkpoint | — | — | — | — | — | X | — | X | — | — |
| uow | — | — | — | — | X | X | — | X | X | — |
| workspace/build | — | — | — | — | — | — | — | — | — | X |
| composition | CR | CR | CR | CR | CR | CR | CR | CR | CR | CR |

Não há ciclos entre módulos. Não há import de adapter por domínio, Runtime,
Discovery, Execution, Checkpoint ou Unit of Work.

## 13. Dependências efetivas

O código de produção do CORE usa exclusivamente:

```text
abc, argparse, base64, binascii, collections, contextvars, csv, dataclasses
datetime, enum, functools, hashlib, inspect, io, json, locale, logging, math
os, pathlib, re, shutil, sqlite3, subprocess, sys, tempfile, time, tomllib
types, typing, urllib, uuid, zipfile
```

`pytest` é dependência de teste. Os demais itens de `requirements.txt` pertencem
ao ambiente amplo do projeto e não são importados por `src/cko/core` nem
declarados como dependências do wheel.

## 14. Fluxos canônicos

### 14.1 Inicialização

```text
CoreCompositionSettings
-> CompositionRoot
-> Workspace + Logging + Validators
-> Registries + Adapter Factories
-> Connector/Storage instances
-> Checkpoint + UoW
-> Discovery + Planner + Optimizer
-> Execution Engine + Runtime
-> CoreComposition
```

### 14.2 Discovery até Runtime

```text
DiscoveryRequest
-> DiscoveryService / DiscoveryProvider
-> QueryResolution / QueryEvaluation
-> LogicalIndex + Statistics
-> CostBasedPlanner
-> OptimizationPipeline
-> Execution Planner
-> ExecutionPlan
-> ExecutionEngine
-> Runtime lifecycle e RuntimeReport
```

### 14.3 Storage

```text
StorageSession
-> Storage port
-> FilesystemStorage | SQLiteStorage
-> StorageResult

ConnectorSession
-> Connector port
-> FilesystemConnector | SQLiteConnector
-> ConnectorResult
```

### 14.4 Checkpoint e Unit of Work

```text
DefaultCheckpointEngine
-> StorageCheckpointRepository
-> Storage port selecionado no Composition Root

DefaultUnitOfWork
-> registered Connector | Storage | CheckpointRepository
-> execute
-> commit | compensation e rollback
-> close
```

### 14.5 Build

```text
CKO_BUILD.cmd
-> workspace init
-> build_wheel
-> fontes UTF-8 compiladas
-> METADATA + WHEEL + RECORD
-> cko-1.0.0-py3-none-any.whl
```

## 15. Exceções

`CKOError` é a raiz única de 120 classes declaradas pelo CORE. As famílias
históricas preservam múltipla herança com `ValueError`, `KeyError`, `LookupError`
ou `RuntimeError` quando aplicável. A hierarquia completa está em
`CKO_CORE_V1_EXCEPTION_HIERARCHY.md`.

## 16. API pública

Na data de corte da v1.2, `cko.core.__all__` possuía 346 símbolos únicos e resolvidos. A fachada agrega as
APIs homologadas e agora inclui a raiz de exceções e o Composition Root. Imports
por subpacote continuam recomendados para reduzir ambiguidade cognitiva. Nenhum
export anterior foi removido.

## 17. Build e execução suportados

| Dimensão | Requisito certificado |
|---|---|
| Sistema operacional | Windows 10 e Windows 11 |
| Shell | PowerShell 5.1 ou superior |
| Python | 3.13 ou superior dentro da linha suportada |
| Encoding | UTF-8 sem BOM nos fontes novos |
| Wheel | pure Python `py3-none-any` |
| Build | determinístico, timestamps ZIP fixos |

## 18. Segurança arquitetural

- paths de Storage são normalizados pelos resolvers;
- SQLite usa prepared statements e transações explícitas;
- registries rejeitam duplicatas;
- mappings do Composition Root são read-only;
- logs de composição não incluem payload de negócio;
- Checkpoint persiste somente pela porta Storage;
- Unit of Work não mascara falhas de compensação;
- o wheel rejeita fontes inválidas no build.

## 19. Testes e homologação

| Gate | Resultado SPR-009A |
|---|---|
| suíte dedicada | 17 passed |
| regressão completa | 703 passed, 2 falhas legadas |
| regressões novas | zero |
| Runtime | 5 checks aprovados |
| build oficial | 187 entradas |
| build reprodutível | SHA-256 idêntico em duas saídas |
| wheel | ZIP, paths, timestamps, RECORD e import aprovados |
| versão | `1.0.0` em todos os pontos oficiais |

As falhas legadas são `collect_metadata` sem o parâmetro `calculate_hash` e o
handle de `cko.db` mantido no teardown do teste SPR-005A em Windows. Elas
precedem o CORE SDK novo, foram reproduzidas sem alteração e não são regressões
da SPR-009A.

## 20. Roadmap normativo

| Marco | Estado | Conteúdo |
|---|---|---|
| SPR-008A–B | homologado | foundation e modelos canônicos |
| SPR-008C | homologado | Inventory |
| SPR-008D–N | homologado | Discovery, Query, Index, Statistics, Planner, Optimizer |
| SPR-008O/P/Q | homologado | Execution Planner, Engine e Runtime |
| SPR-008R/S/T/U | homologado | ports e adapters Filesystem/SQLite |
| SPR-008V/W | homologado | Checkpoint e Unit of Work |
| SPR-008OA | homologado | Workspace e Build |
| SPR-009 | certificado com ressalvas | auditoria arquitetural |
| SPR-009A | certificado | versão, exceções, composição e ARCH v1.2 |
| Camada Semântica | autorizada após homologação formal | não iniciada na data de corte desta v1.2; posteriormente homologada pelas SPR-010–017 |

Temas P2 registrados na SPR-009, como uniformização de eventos, cobertura por
módulo, isolamento de temporários e política transversal de configuração e
segurança, permanecem no backlog e não invalidam o CORE SDK 1.0.0.

## 21. Histórico preservado

### ARCH-001 v1.0

Estabeleceu o monólito modular incremental, a separação domain/infrastructure,
os modelos fundamentais e a direção de dependências.

### ARCH-001 v1.1

Incorporou Workspace, Build, Runtime, Execution Engine, Execution Planner,
Connector/Storage e o adapter Filesystem até a SPR-008T. SQLite, Checkpoint e
Unit of Work ainda apareciam como futuros. A distribuição ainda era `0.1.0` e
não havia Composition Root nem raiz única de exceções.

### ARCH-001 v1.2

Mantém todas as decisões válidas das versões anteriores, incorpora as entregas
SQLite, Checkpoint e Unit of Work, oficializa `1.0.0`, introduz o Composition
Root, consolida `CKOError` e atualiza árvore, fluxos, dependências, matriz,
responsabilidades, roadmap e homologação.

Nenhum histórico anterior foi removido ou reescrito.

## 22. Estado de homologação

As quatro ressalvas P1 da SPR-009 estão eliminadas:

| Ressalva | Estado |
|---|---|
| ARCH-001 desatualizada | eliminada por esta v1.2 |
| versionamento 0.1.0 | eliminado; release 1.0.0 |
| raízes paralelas de exceção | eliminadas; `CKOError` única |
| ausência de Composition Root | eliminada; `cko.core.composition` oficial |

## 23. Declaração normativa

O CKO CORE SDK 1.0.0 encontra-se arquiteturalmente consolidado. Esta arquitetura
representa fielmente a implementação e autoriza, após homologação formal da
SPR-009A, o início da Camada Semântica sem que qualquer componente semântico
tenha sido iniciado nesta Sprint.

## 24. Registro de evolução posterior à data de corte

Esta v1.2 preserva a arquitetura normativa homologada na SPR-009A e seus valores históricos. Após sua data de corte, as SPR-010–017 homologaram Knowledge Object, Document, Relationship, Graph, Query, Index, Corpus e Provenance Statement sem alterar a versão de release do SDK, que permanece `1.0.0`.

A API pública vigente contém **646 exports únicos e resolvidos**: 610 exports anteriores preservados e 36 exports adicionados pela SPR-017. Assim, a contagem de 346 da seção 16 é exclusivamente histórica e não representa a baseline corrente.
