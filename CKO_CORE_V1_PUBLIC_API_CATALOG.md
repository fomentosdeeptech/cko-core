# CKO CORE v1 — Catálogo da API pública

## Estado vigente após a SPR-017

A API pública homologada contém **646 exports raiz, únicos e resolvidos**: os 610 exports anteriores foram preservados e a SPR-017 acrescentou 36 exports de Provenance Statement, sem colisões nominais. O pacote vigente é `cko` **1.0.0**. O inventário mecânico e a homologação estão registrados em `SPR017_IMPLEMENTATION_REPORT.md` e `SPR017_HOMOLOGATION_REPORT.md`.

## Resultado histórico da auditoria pré-camada semântica

No corte histórico anterior às SPR-010–017, `cko.core.__all__` continha **334 símbolos**, sem duplicatas, nomes não resolvidos ou imports públicos omitidos. A única importação de pacote não exportada é `FilterGroupEvaluator` em `cko.core.discovery.__init__`; ela continua disponível na fachada raiz e no módulo `query_evaluation`, caracterizando assimetria P3, não quebra. Todos os símbolos abaixo são **ESTÁVEIS** por homologação da Sprint indicada, exceto aliases marcados e `workspace`, que é **INTERNO**. Não foi encontrada API explicitamente experimental/deprecada.

## Superfícies por pacote

| Pacote | Exports | Origem | Classificação |
|---|---:|---|---|
| `cko.core` | 334 | A–W | valor histórico do corte pré-camada semântica; fachada agregada |
| `cko.core.discovery` | 297 | D–O | estável; superfície excessivamente ampla (P3) |
| `cko.core.checkpoint` | 28 | V | estável |
| `cko.core.connectors` | 15 | R | estável |
| `cko.core.execution` | 30 | P | estável |
| `cko.core.runtime` | 18 | Q | estável |
| `cko.core.storage` | 18 | S | estável |
| `cko.core.storage.filesystem` | 12 | T | estável, adapter explícito |
| `cko.core.storage.sqlite` | 12 | U | estável, adapter explícito |
| `cko.core.uow` | 20 | W | estável |
| `cko.core.inventory` | 16 | C | estável |
| `config/contracts/exceptions/identity/logging/metadata/models/utils` | 44 combinados | A–B | estáveis |
| `cko.core.workspace` | 8 | OA | interno por decisão arquitetural |

## Catálogo nominal por módulo

Cada linha é a lista exata do `__all__` do arquivo. O arquivo relativo é evidência de namespace, responsabilidade e dependência; o status é estável conforme a família/Sprint da tabela anterior.

### Fundação, modelos e inventário

| Módulo | Símbolos públicos |
|---|---|
| `config` | `SDKConfig`, `load_config` |
| `contracts.base` | `Repository`, `Clock`, `EventPublisher`, `Plugin`, `Identifiable` |
| `exceptions.errors` | `CKOError`, `ContractError`, `ModelValidationError`, `IdentityError`, `MetadataError`, `ConfigurationError` |
| `identity` | `CanonicalId`, `Origin`, `SemanticVersion` |
| `logging` | `JsonFormatter`, `configure_logging`, `get_logger` |
| `metadata` | `UniversalMetadata` |
| `models.asset` | `Asset`, `AssetClassification`, `AssetFingerprint`, `AssetHash`, `AssetLifecycle`, `AssetRelation`, `AssetStatus`, `AudioAsset`, `DatabaseAsset`, `DocumentAsset`, `FolderAsset`, `ImageAsset`, `KnowledgeAsset`, `ProjectAsset`, `ReferenceAsset`, `VideoAsset`, `asset_from_dict` |
| `models.document` | `CanonicalDocument`, `DocumentLocation`, `InventoryItem` |
| `models.event` | `CanonicalEvent` |
| `inventory` | `AssetNotFoundError`, `DuplicateAssetError`, `Inventory`, `InventoryBuilder`, `InventoryCollection`, `InventoryError`, `InventoryFilter`, `InventoryItem`, `InventoryQuery`, `InventoryResult`, `InventoryService`, `InventorySnapshot`, `InventoryStatistics`, `InventorySummary`, `InventoryValidationError`, `InventoryValidator` |
| `utils` | `ensure_aware`, `require_non_empty`, `utc_now` |

### Discovery — contratos, provider, streaming, identity e capability

| Módulo | Símbolos públicos |
|---|---|
| `cancellation` | `CancellationToken` |
| `contracts` | `DiscoveryAssetMapper`, `DiscoveryEventPublisher`, `DiscoveryProvider`, `DiscoverySource`, `DiscoveryValidator` |
| `errors` | `DiscoveryError`, `DiscoveryMappingError`, `DiscoveryProviderError`, `DiscoveryValidationError`, `InvalidDiscoveredItemError`, `InvalidDiscoveryRequestError`, `InvalidDiscoverySourceError`, `UnsupportedDiscoveryCapabilityError` |
| `events` | `DISCOVERY_BATCH_COMPLETED`, `DISCOVERY_CANCELLED`, `DISCOVERY_COMPLETED`, `DISCOVERY_EVENT_NAMES`, `DISCOVERY_FAILED`, `DISCOVERY_ITEM_OBSERVED`, `DISCOVERY_ITEM_REJECTED`, `DISCOVERY_STARTED`, `create_discovery_event` |
| `execution` | `AsyncDiscoveryProvider`, `ContextualDiscoveryProvider`, `DiscoveryExecutionContext`, `DiscoveryExecutor` |
| `foundation_errors` | `DiscoveryCancelledError`, `DiscoveryExecutionError`, `DiscoveryProviderNotFoundError`, `DiscoveryProviderRegistrationError`, `DiscoveryProviderResolutionError`, `DiscoverySessionStateError` |
| `models` | `DISCOVERY_SCHEMA_VERSION`, `DiscoveredItem`, `DiscoveryBatch`, `DiscoveryCapability`, `DiscoveryContext`, `DiscoveryErrorRecord`, `DiscoveryEvidence`, `DiscoveryMetrics`, `DiscoveryPolicy`, `DiscoveryRequest`, `DiscoveryResult`, `DiscoveryScope`, `DiscoverySourceId`, `DiscoveryStatus`, `DiscoveryWarning`, `discovery_model_from_dict` |
| `pipeline` | `DiscoveryExecution`, `DiscoveryPipeline` |
| `providers` | `DiscoveryExecutionMode`, `DiscoveryProviderDescriptor`, `DiscoveryProviderFactory`, `DiscoveryProviderRegistry`, `DiscoveryProviderResolver` |
| `service/session/validator/mapper/checkpoint` | `DiscoveryService`, `DiscoverySession`, `DiscoverySessionMetrics`, `DiscoverySessionState`, `DefaultDiscoveryValidator`, `DefaultDiscoveryAssetMapper`, `DiscoveryCheckpoint` |
| `streaming_contracts` | `AsyncBatchConsumer`, `AsyncBatchProducer`, `BatchConsumer`, `BatchConsumptionContext`, `BatchProducer`, `BatchProductionContext` |
| `streaming_errors` | `BackpressureViolationError`, `BatchConsumerError`, `BatchProducerError`, `DiscoveryStreamTransitionError`, `DuplicateBatchError`, `InvalidBatchAcknowledgementError`, `InvalidBatchCursorError`, `InvalidBatchSequenceError`, `InvalidDiscoveryStreamError` |
| `streaming_models` | `BATCH_CURSOR_SCHEMA_VERSION`, `BackpressurePolicy`, `BatchAcknowledgement`, `BatchAcknowledgementStatus`, `BatchCursor`, `ConsumerUnavailableBehavior`, `DiscoveryStreamState`, `StreamMetrics` |
| `stream/streaming_pipeline` | `DiscoveryStream`, `StreamingDiscoveryPipeline`, `StreamingExecution` |
| `identity_contracts` | `CanonicalIdentityAllocator`, `IdentityCandidateProvider`, `IdentityEvidenceEvaluator` |
| `identity_errors` | `IdentityAllocationError`, `IdentityAmbiguityError`, `IdentityCandidateProviderError`, `IdentityConflictError`, `IdentityEvidenceEvaluationError`, `IdentityResolutionCancelledError`, `IdentityResolutionError`, `InvalidIdentityCandidateError`, `InvalidIdentityEvidenceError`, `InvalidIdentityPolicyError`, `InvalidIdentityResolutionRequestError` |
| `identity_models` | `ConflictBehavior`, `ConflictSeverity`, `EvidenceEvaluation`, `IDENTITY_RESOLUTION_SCHEMA_VERSION`, `IdentityCandidate`, `IdentityConflict`, `IdentityEvidence`, `IdentityEvidenceType`, `IdentityFingerprint`, `IdentityResolutionRequest`, `InsufficientEvidenceBehavior`, `ResolutionDecision`, `ResolutionPolicy`, `ResolutionStatus` |
| `identity_resolution` | `DefaultCanonicalIdentityAllocator`, `DefaultNeutralEvidenceEvaluator`, `IdentityResolutionEngine` |
| `capability_errors` | `CapabilityConflictError`, `CapabilityDependencyError`, `CapabilityError`, `CapabilityNegotiationError`, `CapabilityValidationError`, `InvalidCapabilityError` |
| `capability_models` | `CAPABILITY_SCHEMA_VERSION`, `Capability`, `CapabilityCategory`, `CapabilityReport`, `CapabilityRequirement`, `CapabilityRequirementType`, `CapabilitySet` |
| `capability_negotiation/validation` | `CapabilityNegotiationEngine`, `CapabilityResolver`, `CapabilityValidationEngine` |

### Discovery — query, index, statistics, planner, optimizer e execution plan

| Módulo | Símbolos públicos |
|---|---|
| `query_models` | `DiscoveryQuery`, `FilterGroup`, `FilterGroupOperator`, `QUERY_SCHEMA_VERSION`, `QueryFilter`, `QueryOperator`, `QueryOrdering`, `QueryOrderingDirection`, `QueryPagination`, `QueryPlan`, `QueryProjection` |
| `query_errors` | `InvalidFilterError`, `InvalidOrderingError`, `InvalidPaginationError`, `InvalidProjectionError`, `InvalidQueryError`, `QueryError`, `QueryResolutionError`, `QueryValidationError` |
| `query_resolution/validation` | `QueryResolver`, `QueryValidationEngine` |
| `query_evaluation_contracts` | `AttributeResolver`, `AttributeValue`, `MappingQueryEvaluationSubject`, `QueryEvaluationStream`, `QueryEvaluationSubject` |
| `query_evaluation_errors` | `AttributeResolutionError`, `FilterGroupEvaluationError`, `InvalidQueryEvaluationPolicyError`, `InvalidQueryEvaluationSubjectError`, `PredicateEvaluationError`, `QueryEvaluationCancelledError`, `QueryEvaluationError`, `QueryEvaluationLimitError`, `QueryOrderingEvaluationError`, `QueryPaginationEvaluationError`, `QueryProjectionEvaluationError` |
| `query_evaluation_models` | `EvaluationErrorBehavior`, `IncompatibleTypeBehavior`, `MissingAttributeBehavior`, `OrderingValuePosition`, `PredicateEvaluationRecord`, `ProjectedQueryItem`, `QUERY_EVALUATION_SCHEMA_VERSION`, `QueryEvaluationContext`, `QueryEvaluationPolicy`, `QueryEvaluationResult`, `QueryMatchResult` |
| `query_evaluation` | `DefaultAttributeResolver`, `DefaultQueryEvaluationStream`, `FilterGroupEvaluator`, `QueryEvaluationEngine`, `QueryOrderingEngine`, `QueryPaginationEngine`, `QueryPredicateEvaluator`, `QueryProjectionEngine` |
| `query_index_models` | `DiscardedLogicalIndex`, `DuplicateBehavior`, `IndexStrategy`, `LogicalIndex`, `LogicalIndexEntry`, `LogicalIndexPolicy`, `LogicalIndexReport`, `LogicalIndexStatistics`, `QUERY_INDEX_SCHEMA_VERSION`, `QueryIndexPlan` |
| `query_index_errors` | `InvalidLogicalIndexError`, `InvalidLogicalIndexPolicyError`, `LogicalIndexError`, `LogicalIndexResolutionError`, `LogicalIndexValidationError` |
| `query_index` | `LogicalIndexBuilder`, `LogicalIndexResolver`, `LogicalIndexValidator`, `QueryIndexPlanner` |
| `statistics_models` | `AttributeStatistics`, `CostEstimate`, `EstimationStrategy`, `Histogram`, `HistogramBucket`, `HistogramPolicy`, `LogicalStatistics`, `STATISTICS_SCHEMA_VERSION`, `StatisticsPolicy`, `StatisticsReport` |
| `statistics_errors/statistics` | `CostEstimationError`, `InvalidStatisticsError`, `InvalidStatisticsPolicyError`, `StatisticsError`, `StatisticsValidationError`, `CostEstimator`, `HistogramBuilder`, `StatisticsBuilder`, `StatisticsValidator` |
| `planner_models` | `PLANNER_SCHEMA_VERSION`, `PlannerDecision`, `PlannerMetrics`, `PlannerPolicy`, `PlannerReport`, `PlannerWeights`, `QueryExecutionPlan`, `QueryExecutionStrategy` |
| `planner_errors/planner` | `InvalidPlannerModelError`, `PlannerError`, `PlannerValidationError`, `PlanningError`, `CostBasedPlanner`, `PLANNER_VERSION`, `PlannerValidator` |
| `optimizer_models` | `OPTIMIZER_SCHEMA_VERSION`, `OptimizationCategory`, `OptimizationContext`, `OptimizationDecision`, `OptimizationDecisionStatus`, `OptimizationMetrics`, `OptimizationReport`, `OptimizationResult` |
| `optimizer_errors/optimizer` | `InvalidOptimizerModelError`, `OptimizationError`, `OptimizerError`, `OptimizerValidationError`, `OPTIMIZER_VERSION`, `OptimizationPipeline`, `OptimizerValidator` |
| `optimizer_rules` | `BooleanNormalizationRule`, `CANONICAL_OPTIMIZATION_RULES`, `ConstantExpressionRule`, `DuplicateProjectionRemovalRule`, `EmptyPredicateRule`, `IdentityTransformationRule`, `LimitNormalizationRule`, `OptimizationRule`, `PredicateSimplificationRule`, `ProjectionNormalizationRule`, `RedundantFilterRemovalRule`, `SortNormalizationRule` |
| `execution_models` | `EXECUTION_SCHEMA_VERSION`, `CompositeIndexScanNode`, `ExecutionContext`, `ExecutionMetrics`, `ExecutionNode`, `ExecutionNodeType`, `ExecutionPlan`, `ExecutionReport`, `FilterNode`, `IndexScanNode`, `LimitNode`, `OrderedScanNode`, `PrefixScanNode`, `ProjectionNode`, `RootNode`, `ScanNode`, `SortNode` |
| `execution_errors/planner` | `ExecutionPlannerError`, `ExecutionPlanningError`, `ExecutionValidationError`, `InvalidExecutionModelError`, `EXECUTION_PLANNER_VERSION`, `ExecutionPipeline`, `ExecutionPlanValidator`, `ExecutionValidator` |

### Execution e Runtime

| Pacote | Símbolos públicos |
|---|---|
| `execution` | `ENGINE_SCHEMA_VERSION`, `EXECUTION_ENGINE_VERSION`, `CompositeIndexScanOperator`, `ExecutionContext`, `ExecutionEngine`, `ExecutionEngineError`, `ExecutionEngineValidationError`, `ExecutionEngineValidator`, `ExecutionMetrics`, `ExecutionOperator`, `ExecutionOperatorError`, `ExecutionPipeline`, `ExecutionPipelineError`, `ExecutionResult`, `ExecutionState`, `ExecutionValidator`, `FilterOperator`, `IndexScanOperator`, `InvalidExecutionEngineModelError`, `LimitOperator`, `OperatorResult`, `OrderedScanOperator`, `PipelineResult`, `PrefixScanOperator`, `ProjectionOperator`, `RootOperator`, `ScanOperator`, `SortOperator`, `canonical_operators`, `deterministic_execution_id` |
| `runtime` | `RUNTIME_SCHEMA_VERSION`, `RUNTIME_VERSION`, `CancellationToken`, `InvalidRuntimeModelError`, `LifecycleController`, `ResourceRegistry`, `ResourceRegistryError`, `Runtime`, `RuntimeCancellationError`, `RuntimeContext`, `RuntimeErrorBase`, `RuntimeLifecycleError`, `RuntimeMetrics`, `RuntimeReport`, `RuntimeSession`, `RuntimeState`, `RuntimeValidationError`, `RuntimeValidator` |

### Ports, adapters, Checkpoint e Unit of Work

| Pacote | Símbolos públicos |
|---|---|
| `connectors` | `CONNECTOR_SCHEMA_VERSION`, `CONNECTOR_VERSION`, `Connector`, `ConnectorCapabilities`, `ConnectorConstructor`, `ConnectorContext`, `ConnectorDescriptor`, `ConnectorException`, `ConnectorFactory`, `ConnectorMetadata`, `ConnectorRegistry`, `ConnectorResult`, `ConnectorSession`, `ConnectorSessionState`, `ConnectorValidator` |
| `storage` | `STORAGE_SCHEMA_VERSION`, `STORAGE_VERSION`, `Storage`, `StorageCapabilities`, `StorageConstructor`, `StorageContext`, `StorageDescriptor`, `StorageException`, `StorageFactory`, `StorageLocation`, `StorageMetadata`, `StorageObject`, `StorageOperation`, `StorageRegistry`, `StorageResult`, `StorageSession`, `StorageSessionState`, `StorageValidator` |
| `storage.filesystem` | `FILESYSTEM_IDENTIFIER`, `FILESYSTEM_OPERATIONS`, `FILESYSTEM_SCHEMA_VERSION`, `FILESYSTEM_VERSION`, `FilesystemConnector`, `FilesystemDescriptor`, `FilesystemLocationResolver`, `FilesystemResult`, `FilesystemSession`, `FilesystemStorage`, `FilesystemStorageFactory`, `FilesystemStorageValidator` |
| `storage.sqlite` | `SQLITE_IDENTIFIER`, `SQLITE_OPERATIONS`, `SQLITE_SCHEMA_VERSION`, `SQLITE_VERSION`, `SQLiteConnector`, `SQLiteDescriptor`, `SQLiteLocationResolver`, `SQLiteResult`, `SQLiteSession`, `SQLiteStorage`, `SQLiteStorageFactory`, `SQLiteStorageValidator` |
| `checkpoint` | `CHECKPOINT_SCHEMA_VERSION`, `CHECKPOINT_VERSION`, `CheckpointCollection`, `CheckpointConflictError`, `CheckpointContext`, `CheckpointEngine`, `CheckpointException`, `CheckpointIdentifier`, `CheckpointIntegrityError`, `CheckpointMetadata`, `CheckpointNotFoundError`, `CheckpointOperation`, `CheckpointPayload`, `CheckpointQuery`, `CheckpointRecord`, `CheckpointRepository`, `CheckpointResult`, `CheckpointSerializationError`, `CheckpointSerializer`, `CheckpointSnapshot`, `CheckpointState`, `CheckpointStateError`, `CheckpointStorageError`, `CheckpointValidationError`, `CheckpointValidator`, `DefaultCheckpointEngine`, `DefaultCheckpointSerializer`, `StorageCheckpointRepository` |
| `uow` | `UOW_SCHEMA_VERSION`, `UOW_VERSION`, `DefaultUnitOfWork`, `RepositoryCollection`, `UnitOfWork`, `UnitOfWorkAction`, `UnitOfWorkClosedError`, `UnitOfWorkCompensation`, `UnitOfWorkContext`, `UnitOfWorkException`, `UnitOfWorkExecutionError`, `UnitOfWorkOperation`, `UnitOfWorkRegistrationError`, `UnitOfWorkRepository`, `UnitOfWorkResult`, `UnitOfWorkRollbackError`, `UnitOfWorkState`, `UnitOfWorkStateError`, `UnitOfWorkValidationError`, `UnitOfWorkValidator` |

### Workspace interno

`CleanResult`, `EnvironmentValidationResult`, `EnvironmentValidator`, `RuntimePaths`, `TemporaryFileManager`, `ValidationCheck`, `WorkspaceCleaner`, `WorkspaceManager`. Esses oito nomes são públicos apenas no subnamespace e classificados **INTERNO** pela ARCH.

## API raiz e aliases

A raiz reexporta as APIs canônicas de config, identity, metadata, models, Discovery selecionado, statistics/planner/optimizer/execution plan, Execution, Runtime, Connector, Storage, Checkpoint e UoW. Não reexporta adapters Filesystem/SQLite, workspace, logging, exceptions base, contracts base ou Inventory completo.

Colisões semânticas são resolvidas por aliases explícitos:

- `execution.ExecutionContext` → `EngineExecutionContext` na raiz;
- `execution.ExecutionMetrics` → `EngineExecutionMetrics`;
- `execution.ExecutionPipeline` → `EngineExecutionPipeline`;
- `runtime.CancellationToken` → `RuntimeCancellationToken`.

Os nomes sem alias `ExecutionContext`, `ExecutionMetrics` e `ExecutionPipeline` da raiz referem-se ao Execution Planner em Discovery. Não há duplicata em `__all__`, mas essa escolha é **CONFLITANTE** do ponto de vista cognitivo e deve permanecer documentada.

## Versionamento e documentação

Schemas públicos variam entre constantes `*_SCHEMA_VERSION` e campos nos envelopes. Connector, Storage, Filesystem, SQLite, Checkpoint e UoW declaram versão 1.0/1.0.0; no corte histórico, o pacote e `cko.core.__version__` permaneciam `0.1.0`. Esse conflito de versão P1 foi eliminado na baseline vigente `1.0.0`. ARCH-001 v1.1 não documenta as APIs U/V/W e deve ser atualizada após a auditoria.

## Adendo SPR-016 — Knowledge Corpus Foundation

`cko.core.corpus` publica 48 símbolos únicos. A família inclui as constantes de esquema/API/serialização e namespace UUID; onze modelos frozen/slotted; categoria fechada; factory, builder, validator, serializer, operações puras, protocolos e exceções específicas.

A fachada `cko.core` reexporta 42 desses símbolos sem duplicar qualquer entrada existente em `__all__`. Protocolos, `CorpusModel` e `corpus_digest_payload` permanecem apenas no namespace especializado. O inventário exato está em `CKO_CORPUS_API.md` e em `cko.core.corpus.__all__`.

## Adendo SPR-017 — Knowledge Provenance Statement Foundation

`cko.core.provenance` publica a fundação homologada de Provenance Statement. A integração raiz é estritamente aditiva: **610 exports anteriores + 36 exports da SPR-017 = 646 exports únicos e resolvidos**, com interseção nominal zero. O catálogo nominal dos 36 símbolos está em `CKO_PROVENANCE_STATEMENT_API.md` e em `cko.core.provenance.__all__`.

Este adendo representa o estado vigente. As contagens 334 e a versão 0.1.0 acima permanecem apenas como registro do corte histórico em que foram auditadas.
