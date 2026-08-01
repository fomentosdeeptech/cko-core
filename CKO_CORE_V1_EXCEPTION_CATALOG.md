# CKO CORE v1 — Catálogo de exceções

## Visão geral

Foram encontradas **119 classes**. A arquitetura não possui uma única raiz: existem `CKOError`, `ConnectorException`, `StorageException`, `CheckpointException`, `RuntimeErrorBase` e `UnitOfWorkException`, além de famílias que nascem diretamente de `ValueError`. Todas são públicas por seus pacotes. O catálogo abaixo usa `A <- B` para “B deriva de A”; bases múltiplas preservam compatibilidade com exceções Python.

## Hierarquia completa

### Fundação e Inventory

```text
Exception <- CKOError
CKOError <- ContractError <- ModelValidationError <- IdentityError
ModelValidationError <- MetadataError
CKOError <- ConfigurationError
ContractError <- InventoryError <- DuplicateAssetError
InventoryError + KeyError <- AssetNotFoundError
ModelValidationError <- InventoryValidationError
```

### Discovery base, provider e streaming

```text
CKOError <- DiscoveryError
DiscoveryError + ValueError <- InvalidDiscoveryRequestError
DiscoveryError + ValueError <- InvalidDiscoverySourceError
DiscoveryError + ValueError <- InvalidDiscoveredItemError
DiscoveryError <- UnsupportedDiscoveryCapabilityError
DiscoveryError <- DiscoveryProviderError
DiscoveryError <- DiscoveryMappingError
DiscoveryError + ValueError <- DiscoveryValidationError
DiscoveryError + ValueError <- DiscoveryProviderRegistrationError
DiscoveryError + LookupError <- DiscoveryProviderNotFoundError
DiscoveryError + LookupError <- DiscoveryProviderResolutionError
DiscoveryError + RuntimeError <- DiscoverySessionStateError
DiscoveryError <- DiscoveryCancelledError
DiscoveryError + RuntimeError <- DiscoveryExecutionError
DiscoveryError + ValueError <- InvalidDiscoveryStreamError
DiscoveryError + RuntimeError <- DiscoveryStreamTransitionError
DiscoveryError + ValueError <- InvalidBatchSequenceError <- DuplicateBatchError
DiscoveryError + ValueError <- InvalidBatchCursorError
DiscoveryError + ValueError <- InvalidBatchAcknowledgementError
DiscoveryError + RuntimeError <- BatchProducerError
DiscoveryError + RuntimeError <- BatchConsumerError
DiscoveryError + RuntimeError <- BackpressureViolationError
```

### Capability e Identity Resolution

```text
DiscoveryError <- CapabilityError
CapabilityError <- CapabilityConflictError
CapabilityError <- CapabilityDependencyError
CapabilityError <- CapabilityValidationError
CapabilityError <- CapabilityNegotiationError
CapabilityError + ValueError <- InvalidCapabilityError

DiscoveryError <- IdentityResolutionError
IdentityResolutionError + ValueError <- InvalidIdentityResolutionRequestError
IdentityResolutionError + ValueError <- InvalidIdentityCandidateError
IdentityResolutionError + ValueError <- InvalidIdentityEvidenceError
IdentityResolutionError + ValueError <- InvalidIdentityPolicyError
IdentityResolutionError <- IdentityCandidateProviderError
IdentityResolutionError <- IdentityEvidenceEvaluationError
IdentityResolutionError <- IdentityAmbiguityError
IdentityResolutionError <- IdentityConflictError
IdentityResolutionError <- IdentityAllocationError
IdentityResolutionError <- IdentityResolutionCancelledError
```

### Query, evaluation, index, statistics, planner e optimizer

```text
DiscoveryError <- QueryError
QueryError + ValueError <- InvalidQueryError
InvalidQueryError <- InvalidFilterError
InvalidQueryError <- InvalidProjectionError
InvalidQueryError <- InvalidOrderingError
InvalidQueryError <- InvalidPaginationError
QueryError <- QueryValidationError
QueryError <- QueryResolutionError

QueryError <- QueryEvaluationError
QueryEvaluationError + ValueError <- InvalidQueryEvaluationSubjectError
QueryEvaluationError + ValueError <- InvalidQueryEvaluationPolicyError
QueryEvaluationError <- AttributeResolutionError
QueryEvaluationError <- PredicateEvaluationError
QueryEvaluationError <- FilterGroupEvaluationError
QueryEvaluationError <- QueryProjectionEvaluationError
QueryEvaluationError <- QueryOrderingEvaluationError
QueryEvaluationError <- QueryPaginationEvaluationError
QueryEvaluationError <- QueryEvaluationCancelledError
QueryEvaluationError <- QueryEvaluationLimitError

ValueError <- LogicalIndexError
LogicalIndexError <- InvalidLogicalIndexError
LogicalIndexError <- InvalidLogicalIndexPolicyError
LogicalIndexError <- LogicalIndexValidationError
LogicalIndexError <- LogicalIndexResolutionError

ValueError <- StatisticsError
StatisticsError <- InvalidStatisticsError
StatisticsError <- InvalidStatisticsPolicyError
StatisticsError <- StatisticsValidationError
StatisticsError <- CostEstimationError

ValueError <- PlannerError
PlannerError <- InvalidPlannerModelError
PlannerError <- PlanningError
PlannerError <- PlannerValidationError

ValueError <- OptimizerError
OptimizerError <- InvalidOptimizerModelError
OptimizerError <- OptimizationError
OptimizerError <- OptimizerValidationError

ValueError <- ExecutionPlannerError
ExecutionPlannerError <- InvalidExecutionModelError
ExecutionPlannerError <- ExecutionPlanningError
ExecutionPlannerError <- ExecutionValidationError
```

### Execution Engine e Runtime

```text
ValueError <- ExecutionEngineError
ExecutionEngineError <- InvalidExecutionEngineModelError
ExecutionEngineError <- ExecutionEngineValidationError
ExecutionEngineError <- ExecutionOperatorError
ExecutionEngineError <- ExecutionPipelineError

Exception <- RuntimeErrorBase
RuntimeErrorBase + ValueError <- InvalidRuntimeModelError
RuntimeErrorBase + ValueError <- RuntimeLifecycleError
RuntimeErrorBase + ValueError <- RuntimeValidationError
RuntimeErrorBase <- RuntimeCancellationError
RuntimeErrorBase + ValueError <- ResourceRegistryError
```

### Connector, Storage, Checkpoint e UoW

```text
Exception <- ConnectorException
Exception <- StorageException

Exception <- CheckpointException
CheckpointException <- CheckpointValidationError
CheckpointException <- CheckpointSerializationError
CheckpointException <- CheckpointIntegrityError
CheckpointException <- CheckpointNotFoundError
CheckpointException <- CheckpointConflictError
CheckpointException <- CheckpointStorageError
CheckpointException <- CheckpointStateError

Exception <- UnitOfWorkException
UnitOfWorkException <- UnitOfWorkValidationError
UnitOfWorkException <- UnitOfWorkStateError
UnitOfWorkException <- UnitOfWorkRegistrationError
UnitOfWorkException <- UnitOfWorkExecutionError
UnitOfWorkException <- UnitOfWorkRollbackError
UnitOfWorkException <- UnitOfWorkClosedError
```

## Estratégias observadas

- Discovery/Inventory preservam `CKOError`; componentes P–W criaram raízes locais.
- Muitos erros inválidos também são `ValueError`, permitindo tratamento Python idiomático.
- Connector/Storage usam uma exceção rica com `code` e identificador, mas sem subclasses.
- Checkpoint/UoW usam subclasses sem raiz CKO.
- Repositories e engines às vezes retornam result envelopes com `error_code/error_message`; invariantes e composição levantam exceções.
- Exception chaining com `raise`/`from` é usado nas traduções críticas SQLite, registries e resolvers; a causa é preservada.

## Duplicações semânticas

`*ValidationError`, `Invalid*ModelError`, `*StateError`, `*CancellationError` e `*ExecutionError` aparecem em domínios sem ancestral transversal. Isso obriga consumidores a capturar várias raízes e dificulta métricas agregadas. `ExecutionValidationError` (planner) e `ExecutionEngineValidationError` são semanticamente distintas, mas seus nomes próximos exigem qualificação.

## Taxonomia canônica proposta, sem implementação

```text
CKOError
  ContractError
    ValidationError
    CompatibilityError
  DomainError
    InventoryError
    DiscoveryError
    QueryError
    PlanningError
    ExecutionError
    CheckpointError
    UnitOfWorkError
  InfrastructureError
    ConnectorError
    StorageError
    WorkspaceError
  LifecycleError
  CancellationError
  ConfigurationError
```

A migração deve ser aditiva: raízes atuais continuam válidas por herança múltipla ou aliases; nenhum export deve ser removido. Exigir `code`, `context` seguro e cause chaining em toda fronteira. Esta proposta é P1 antes de criar novas famílias semânticas.
