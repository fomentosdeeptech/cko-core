# CKO CORE SDK v1.0 — Composition Root oficial

**Versão normativa:** 1.0  
**Sprint:** SPR-009A  
**Módulo:** `cko.core.composition`  
**Estado:** oficial e homologado

## 1. Decisão arquitetural

`CompositionRoot` é o único mecanismo oficial de inicialização integrada do
CORE. A função `compose_core` é a fachada funcional equivalente. Ambos produzem
um `CoreComposition` imutável com o grafo completo e validado.

Factories locais existentes permanecem públicas por retrocompatibilidade, mas
não constituem composition roots. Aplicações novas devem obter Runtime,
Execution, Discovery, Planner, Storage, Connector, Checkpoint, Unit of Work,
Workspace, Build, Logging, registries, factories e validators por esta API.

## 2. API pública

| Símbolo | Responsabilidade |
|---|---|
| `CoreCompositionSettings` | declarar paths, storage de checkpoint, timeout e logging |
| `CompositionRoot.compose` | montar e validar o grafo completo |
| `compose_core` | fachada funcional para `CompositionRoot.compose` |
| `CoreComposition` | container imutável do grafo montado |
| `BuildInfrastructure` | vincular o builder determinístico ao workspace |
| `CompositionError` | falha de configuração ou resolução do grafo |

Todos os símbolos são exportados por `cko.core.composition`. A fachada
`cko.core` reexporta os cinco símbolos de composição e `CompositionError`.

## 3. Configuração

`CoreCompositionSettings` possui os seguintes campos:

| Campo | Tipo | Política |
|---|---|---|
| `workspace_root` | `str`, `Path` ou `None` | descoberta canônica quando ausente |
| `filesystem_root` | `str`, `Path` ou `None` | `runtime/snapshots` quando ausente |
| `sqlite_database` | `str`, `Path` ou `None` | `runtime/database/cko-core.db` quando ausente |
| `checkpoint_storage_id` | `str` | Filesystem por padrão |
| `sqlite_timeout` | `float` | 5 segundos; deve ser positivo |
| `configure_logging` | `bool` | configura logger `cko` quando verdadeiro |
| `log_level` | `int` ou `str` | nível entregue ao logging padrão |

A configuração é frozen e slots. Ela não altera qualquer schema ou formato de
serialização existente.

## 4. Grafo oficial

```text
CompositionRoot
├── Logging
│   ├── configure_logging
│   └── publisher de eventos Discovery
├── Workspace
│   ├── WorkspaceManager
│   ├── EnvironmentValidator
│   └── BuildInfrastructure -> build_wheel
├── Validators
│   ├── Connector, Storage, Filesystem e SQLite
│   ├── Discovery, Index, Statistics, Planner e Optimizer
│   ├── Execution Plan e Execution Engine
│   ├── Runtime, Checkpoint e Unit of Work
│   └── Inventory e Environment
├── Registries e Factories
│   ├── ConnectorRegistry -> ConnectorFactory
│   ├── StorageRegistry -> StorageFactory
│   └── DiscoveryProviderRegistry -> DiscoveryProviderFactory
├── Adapters
│   ├── FilesystemConnector e FilesystemStorage
│   └── SQLiteConnector e SQLiteStorage
├── Planning e Execution
│   ├── CostBasedPlanner
│   ├── OptimizationPipeline
│   ├── Execution Planner
│   └── ExecutionEngine
├── Coordination
│   ├── Runtime
│   ├── StorageCheckpointRepository -> DefaultCheckpointEngine
│   └── DefaultUnitOfWork
└── Discovery
    ├── DefaultDiscoveryValidator
    ├── DiscoveryService
    └── provider registry, resolver e factory
```

## 5. Ordem determinística de composição

1. Validar `CoreCompositionSettings`.
2. Descobrir ou normalizar o workspace.
3. Criar a árvore canônica do runtime.
4. Configurar logging quando solicitado.
5. Instanciar os 16 validators oficiais.
6. Criar registries Connector e Storage por instância.
7. Vincular factories Filesystem e SQLite.
8. Registrar constructors dos dois adapters.
9. Criar os dois connectors e os dois storages pelas factories genéricas.
10. Resolver o storage de Checkpoint pelo identificador registrado.
11. Compor serializer, repository e engine de Checkpoint.
12. Registrar storages, connectors e repository de Checkpoint no Unit of Work.
13. Compor Discovery registry, resolver, factory, validator e service.
14. Compor planner, optimizer, execution planner e execution engine.
15. Compor Runtime e Unit of Work iniciais.
16. Retornar `CoreComposition` com mappings read-only.

## 6. Conteúdo do container

| Campo | Tipo efetivo | Ciclo de vida |
|---|---|---|
| `workspace` | `WorkspaceManager` | composição |
| `build` | `BuildInfrastructure` | composição |
| `environment_validator` | `EnvironmentValidator` | composição |
| `validators` | mapping read-only com 16 itens | composição |
| `connector_registry` | `ConnectorRegistry` | composição |
| `connector_factory` | `ConnectorFactory` | composição |
| `connectors` | mapping read-only com 2 adapters | composição |
| `storage_registry` | `StorageRegistry` | composição |
| `storage_factory` | `StorageFactory` | composição |
| `storages` | mapping read-only com 2 adapters | composição |
| `discovery_registry` | `DiscoveryProviderRegistry` | composição |
| `discovery_factory` | `DiscoveryProviderFactory` | composição |
| `discovery` | `DiscoveryService` | composição |
| `planner` | `CostBasedPlanner` | composição |
| `optimizer` | `OptimizationPipeline` | composição |
| `execution_planner` | Execution Planner | composição |
| `execution_engine` | `ExecutionEngine` | composição |
| `checkpoint_repository` | `StorageCheckpointRepository` | composição |
| `checkpoint` | `DefaultCheckpointEngine` | composição |
| `unit_of_work_repositories` | tuple com 5 registrations | composição |
| `unit_of_work` | `DefaultUnitOfWork` | operação única |
| `runtime` | `Runtime` | execução única |

## 7. Fresh lifecycles

Runtime e Unit of Work possuem lifecycle intencionalmente finito. O container
fornece `create_runtime` e `create_unit_of_work` para criar instâncias novas sem
repetir composição manual. As instâncias frescas reutilizam somente dependências
stateless ou registradas e recebem validators canônicos.

`create_runtime` aceita `runtime_id`, `session_id` e metadata. O método não inicia
execução nem altera Runtime, Discovery ou Execution.

`create_unit_of_work` aceita contexto opcional e registra exatamente:

```text
storage:cko.storage.filesystem
storage:cko.storage.sqlite
connector:cko.storage.filesystem
connector:cko.storage.sqlite
checkpoint
```

## 8. Ports e adapters

O root depende de ports públicos. As implementações concretas ficam restritas à
etapa de composição:

```text
Connector port <- FilesystemConnector
Connector port <- SQLiteConnector
Storage port   <- FilesystemStorage
Storage port   <- SQLiteStorage

CheckpointRepository -> Storage port selecionado
UnitOfWork -> Connector | Storage | CheckpointRepository
Runtime -> ExecutionEngine -> ExecutionPlan
```

Runtime, Discovery, Execution, Checkpoint e Unit of Work não ganharam imports de
adapters concretos. Nenhum registry global foi criado.

## 9. Validators compostos

O mapping `validators` contém as chaves estáveis:

```text
checkpoint
connector
discovery
environment
execution_engine
execution_plan
filesystem
inventory
logical_index
optimizer
planner
runtime
sqlite
statistics
storage
unit_of_work
```

## 10. Logging

Quando habilitado, o root configura o logger `cko` com o formatter JSON já
homologado. O evento terminal é `core.composition.completed` e contém somente a
versão e as contagens de connectors e storages. O publisher interno de Discovery
encaminha eventos canônicos ao logging sem introduzir transporte externo.

## 11. Garantias e limites

- nenhuma funcionalidade semântica foi criada;
- nenhum Knowledge Object foi criado;
- nenhum schema ou formato serializado foi alterado;
- nenhum comportamento de Storage, Runtime, Discovery, Execution ou Checkpoint
  foi alterado;
- as factories públicas históricas permanecem disponíveis;
- os registries continuam por instância;
- o container e os mappings publicados são imutáveis;
- SQLite e Filesystem são compostos simultaneamente;
- a seleção de storage de Checkpoint é explícita e validada;
- configuração inválida falha antes da entrega do container.

## 12. Evidência de homologação

A suíte dedicada comprova a construção real do grafo com Filesystem e SQLite,
os 16 validators, cinco Unit of Work repositories, fresh lifecycles, mappings
read-only, falha tipada para storage não registrado e exports da fachada.
Resultado: 17 testes aprovados.

## 13. Decisão

A ressalva P1 de Composition Root foi eliminada. `CompositionRoot.compose` e
`compose_core` são as entradas oficiais para toda composição integrada do CORE
SDK v1.0.
