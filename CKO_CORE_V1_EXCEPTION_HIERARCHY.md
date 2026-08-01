# CKO CORE SDK v1.0 — Hierarquia canônica de exceções

**Versão normativa:** 1.0  
**Data de consolidação:** 2026-07-25  
**Sprint:** SPR-009A  
**Estado:** homologação técnica concluída

## 1. Regra canônica

`CKOError` é a única raiz de todas as exceções declaradas por `cko.core`.
Consumidores que precisam tratar qualquer falha tipada do SDK podem capturar
`CKOError`. As raízes históricas permanecem públicas e conservam seus nomes,
construtores, atributos e compatibilidade com exceções nativas.

```text
BaseException
└── Exception
    └── CKOError
        ├── erros fundamentais
        ├── Inventory e Discovery
        ├── Query, Planner, Optimizer e Execution
        ├── Runtime
        ├── Connector e Storage
        ├── Checkpoint
        ├── Unit of Work
        └── Composition Root
```

Não existem raízes paralelas declaradas pelo CORE. Erros nativos propagados por
biblioteca padrão, como `OSError`, `TypeError` e `KeyError`, continuam sujeitos
ao contrato específico de cada operação e não passam a ser erros declarados pelo
SDK por efeito desta consolidação.

## 2. Compatibilidade retroativa

| Família histórica | Nova ancestralidade | Compatibilidade preservada |
|---|---|---|
| `ConnectorException` | `CKOError` | nome, código, contexto e construtor |
| `StorageException` | `CKOError` | nome, código, contexto e construtor |
| `CheckpointException` | `CKOError` | subclasses, códigos e contexto |
| `RuntimeErrorBase` | `CKOError` | subclasses e captura histórica |
| `UnitOfWorkException` | `CKOError` | subclasses, códigos e contexto |
| `LogicalIndexError` | `CKOError`, `ValueError` | captura como `ValueError` |
| `StatisticsError` | `CKOError`, `ValueError` | captura como `ValueError` |
| `PlannerError` | `CKOError`, `ValueError` | captura como `ValueError` |
| `OptimizerError` | `CKOError`, `ValueError` | captura como `ValueError` |
| `ExecutionPlannerError` | `CKOError`, `ValueError` | captura como `ValueError` |
| `ExecutionEngineError` | `CKOError`, `ValueError` | captura como `ValueError` |

Não houve remoção, renomeação ou alteração de formato de serialização. A mudança
é estritamente aditiva na relação de herança.

## 3. Hierarquia completa

### 3.1 Fundação e composição

```text
CKOError
├── ContractError
│   └── ModelValidationError
│       ├── IdentityError
│       ├── MetadataError
│       └── InventoryValidationError
├── ConfigurationError
└── CompositionError

ContractError
└── InventoryError
    ├── DuplicateAssetError
    └── AssetNotFoundError + KeyError
```

`CompositionError` é emitida somente para configuração ou resolução inválida do
grafo oficial. Falhas tipadas dos componentes preservam sua família de origem.

### 3.2 Discovery base, provider e streaming

```text
CKOError
└── DiscoveryError
    ├── InvalidDiscoveryRequestError + ValueError
    ├── InvalidDiscoverySourceError + ValueError
    ├── InvalidDiscoveredItemError + ValueError
    ├── UnsupportedDiscoveryCapabilityError
    ├── DiscoveryProviderError
    ├── DiscoveryMappingError
    ├── DiscoveryValidationError + ValueError
    ├── DiscoveryProviderRegistrationError + ValueError
    ├── DiscoveryProviderNotFoundError + LookupError
    ├── DiscoveryProviderResolutionError + LookupError
    ├── DiscoverySessionStateError + RuntimeError
    ├── DiscoveryCancelledError
    ├── DiscoveryExecutionError + RuntimeError
    ├── InvalidDiscoveryStreamError + ValueError
    ├── DiscoveryStreamTransitionError + RuntimeError
    ├── InvalidBatchSequenceError + ValueError
    │   └── DuplicateBatchError
    ├── InvalidBatchCursorError + ValueError
    ├── InvalidBatchAcknowledgementError + ValueError
    ├── BatchProducerError + RuntimeError
    ├── BatchConsumerError + RuntimeError
    └── BackpressureViolationError + RuntimeError
```

### 3.3 Capability e Identity Resolution

```text
DiscoveryError
├── CapabilityError
│   ├── CapabilityConflictError
│   ├── CapabilityDependencyError
│   ├── CapabilityValidationError
│   ├── CapabilityNegotiationError
│   └── InvalidCapabilityError + ValueError
└── IdentityResolutionError
    ├── InvalidIdentityResolutionRequestError + ValueError
    ├── InvalidIdentityCandidateError + ValueError
    ├── InvalidIdentityEvidenceError + ValueError
    ├── InvalidIdentityPolicyError + ValueError
    ├── IdentityCandidateProviderError
    ├── IdentityEvidenceEvaluationError
    ├── IdentityAmbiguityError
    ├── IdentityConflictError
    ├── IdentityAllocationError
    └── IdentityResolutionCancelledError
```

### 3.4 Query e avaliação

```text
DiscoveryError
└── QueryError
    ├── InvalidQueryError + ValueError
    │   ├── InvalidFilterError
    │   ├── InvalidProjectionError
    │   ├── InvalidOrderingError
    │   └── InvalidPaginationError
    ├── QueryValidationError
    ├── QueryResolutionError
    └── QueryEvaluationError
        ├── InvalidQueryEvaluationSubjectError + ValueError
        ├── InvalidQueryEvaluationPolicyError + ValueError
        ├── AttributeResolutionError
        ├── PredicateEvaluationError
        ├── FilterGroupEvaluationError
        ├── QueryProjectionEvaluationError
        ├── QueryOrderingEvaluationError
        ├── QueryPaginationEvaluationError
        ├── QueryEvaluationCancelledError
        └── QueryEvaluationLimitError
```

### 3.5 Index, Statistics, Planner, Optimizer e Execution Planner

```text
CKOError + ValueError
├── LogicalIndexError
│   ├── InvalidLogicalIndexError
│   ├── InvalidLogicalIndexPolicyError
│   ├── LogicalIndexValidationError
│   └── LogicalIndexResolutionError
├── StatisticsError
│   ├── InvalidStatisticsError
│   ├── InvalidStatisticsPolicyError
│   ├── StatisticsValidationError
│   └── CostEstimationError
├── PlannerError
│   ├── InvalidPlannerModelError
│   ├── PlanningError
│   └── PlannerValidationError
├── OptimizerError
│   ├── InvalidOptimizerModelError
│   ├── OptimizationError
│   └── OptimizerValidationError
└── ExecutionPlannerError
    ├── InvalidExecutionModelError
    ├── ExecutionPlanningError
    └── ExecutionValidationError
```

### 3.6 Execution Engine e Runtime

```text
CKOError + ValueError
└── ExecutionEngineError
    ├── InvalidExecutionEngineModelError
    ├── ExecutionEngineValidationError
    ├── ExecutionOperatorError
    └── ExecutionPipelineError

CKOError
└── RuntimeErrorBase
    ├── InvalidRuntimeModelError + ValueError
    ├── RuntimeLifecycleError + ValueError
    ├── RuntimeValidationError + ValueError
    ├── RuntimeCancellationError
    └── ResourceRegistryError + ValueError
```

### 3.7 Connector, Storage, Checkpoint e Unit of Work

```text
CKOError
├── ConnectorException
├── StorageException
├── CheckpointException
│   ├── CheckpointValidationError
│   ├── CheckpointSerializationError
│   ├── CheckpointIntegrityError
│   ├── CheckpointNotFoundError
│   ├── CheckpointConflictError
│   ├── CheckpointStorageError
│   └── CheckpointStateError
└── UnitOfWorkException
    ├── UnitOfWorkValidationError
    ├── UnitOfWorkStateError
    ├── UnitOfWorkRegistrationError
    ├── UnitOfWorkExecutionError
    ├── UnitOfWorkRollbackError
    └── UnitOfWorkClosedError
```

## 4. Regras de uso

1. Toda nova exceção declarada por `cko.core` deve herdar direta ou
   indiretamente de `CKOError`.
2. Famílias de domínio permanecem em seus módulos `errors.py`.
3. Compatibilidade com exceções nativas só deve ser adicionada quando fizer
   parte do contrato, como `ValueError`, `KeyError`, `LookupError` ou
   `RuntimeError`.
4. Traduções de falhas de infraestrutura devem preservar a causa com exception
   chaining.
5. Nenhum módulo semântico futuro pode criar uma raiz paralela.
6. Result envelopes existentes não são substituídos por exceções.
7. Códigos, contexto e mensagens existentes não foram alterados nesta Sprint.

## 5. Evidência de certificação

A suíte `tests/test_core_consolidation_spr009a.py` importa todos os módulos sob
`cko.core`, identifica cada classe de exceção declarada e comprova que todas são
subclasses de `CKOError`. A mesma suíte comprova a permanência de `ValueError`
nas seis famílias historicamente compatíveis. Resultado: 17 testes aprovados.

## 6. Decisão

A ressalva P1 de taxonomia foi eliminada. `CKOError` é a raiz canônica única e
as famílias permanecem organizadas por domínio sem breaking change.
