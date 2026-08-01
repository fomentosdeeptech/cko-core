# CKO CORE v1 — Mapa da arquitetura implementada

## Convenções do inventário

Todos os módulos abaixo estão **presentes**, com AST válido, sob `src/cko/core`. `P` significa API de pacote/raiz por `__all__`; `I`, detalhe interno. A Sprint e a direção de dependência são fatos derivados dos relatórios SPR-008 e imports reais. Em cada linha, os módulos de modelo/erro/validator pertencem à mesma responsabilidade da família, evitando repetir descrições idênticas sem perder nenhum módulo.

## Árvore canônica completa e inventário de módulos

| Namespace/família | Módulos completos | API | Origem | Responsabilidade e dependências diretas |
|---|---|---|---|---|
| `cko.core` | `__init__` | P | A–W | fachada; importa todos os pacotes públicos, exceto workspace/utils |
| `checkpoint` | `__init__`, `contracts`, `engine`, `errors`, `models`, `repository`, `serializer`, `validator` | P | V | checkpoint versionado; depende somente de Storage público, stdlib e logging |
| `config` | `__init__`, `settings` | P | A | config/env/TOML/YAML; depende de exceptions/utils/stdlib |
| `connectors` | `__init__`, `contracts`, `errors`, `factory`, `models`, `registry`, `validator` | P | R | port genérica; depende apenas de logging/stdlib |
| `contracts` | `__init__`, `base` | P | A | `Repository`, `Clock`, `EventPublisher`, `Plugin`, `Identifiable`; foundation |
| `discovery` — base | `__init__`, `cancellation`, `checkpoints`, `contracts`, `errors`, `events`, `execution`, `mapper`, `models`, `pipeline`, `policies`, `providers`, `service`, `session`, `validator` | P/I | D–F | descoberta, providers, sessão e pipeline; foundation/logging/models/utils |
| `discovery` — streaming | `stream`, `streaming_contracts`, `streaming_errors`, `streaming_models`, `streaming_pipeline` | P/I | F | batch/stream/backpressure; discovery base |
| `discovery` — identity | `identity_contracts`, `identity_errors`, `identity_models`, `identity_resolution` | P/I | G | resolução de identidade; identity, discovery base, logging |
| `discovery` — capability | `capability_errors`, `capability_models`, `capability_negotiation`, `capability_validation` | P/I | H | capability/negociação; discovery base/logging |
| `discovery` — query | `query_errors`, `query_models`, `query_resolution`, `query_validation` | P/I | I | query neutra e validação; discovery base |
| `discovery` — evaluation | `query_evaluation`, `query_evaluation_contracts`, `query_evaluation_errors`, `query_evaluation_models` | P/I | J | avaliação in-memory; query/contracts |
| `discovery` — index | `query_index`, `query_index_errors`, `query_index_models` | P/I | K | índice lógico; query/evaluation |
| `discovery` — statistics | `statistics`, `statistics_errors`, `statistics_models` | P/I | L | histogramas/custo lógico; index/query |
| `discovery` — planner | `planner`, `planner_errors`, `planner_models` | P/I | M | cost-based planner; statistics/query/index |
| `discovery` — optimizer | `optimizer`, `optimizer_errors`, `optimizer_models`, `optimizer_rules` | P/I | N | regras e pipeline de otimização; planner/query |
| `discovery` — execution plan | `execution_errors`, `execution_models`, `execution_planner` | P/I | O | plano/nós/validação; optimizer/planner |
| `exceptions` | `__init__`, `errors` | P | A | raiz histórica CKO e erros fundamentais |
| `execution` | `__init__`, `engine`, `errors`, `models`, `operators`, `pipeline`, `validator` | P | P | engine lógico; depende de plano Discovery e logging |
| `identity` | `__init__`, `identifier`, `origin`, `version` | P | A | ID/origem/SemVer; utils/stdlib |
| `inventory` | `__init__`, `builder`, `engine`, `errors`, `models`, `service`, `validator` | P | C | inventário in-memory; identity/models/logging |
| `logging` | `__init__`, `structured` | P | A | formatter JSON e logger; stdlib |
| `metadata` | `__init__`, `universal` | P | A | metadata imutável; utils |
| `models` | `__init__`, `asset`, `document`, `event` | P | B | ativos/documentos/evento; identity/metadata/utils |
| `runtime` | `__init__`, `cancellation`, `errors`, `lifecycle`, `models`, `resources`, `runtime`, `validator` | P | Q | coordena Execution; discovery plan/execution/logging |
| `storage` — port | `__init__`, `contracts`, `errors`, `factory`, `models`, `registry`, `validator` | P | S | storage lógico; connectors/logging/stdlib, sem I/O |
| `storage.filesystem` | `__init__`, `connector`, `descriptor`, `factory`, `resolver`, `result`, `session`, `storage`, `validator` | P | T | adapter filesystem; ports + pathlib/shutil/hashlib |
| `storage.sqlite` | `__init__`, `connector`, `descriptor`, `factory`, `resolver`, `result`, `session`, `storage`, `validator` | P | U | adapter SQLite; ports + sqlite3/pathlib |
| `uow` | `__init__`, `contracts`, `engine`, `errors`, `models`, `validator` | P | W | transação lógica/compensação; contracts públicos Storage/Connector/Checkpoint |
| `utils` | `__init__`, `text`, `time` | I/suporte | A | normalização e UTC; stdlib |
| `workspace` | `__init__`, `build`, `cleaner`, `cli`, `manager`, `paths`, `validator` | subnamespace interno | OA | runtime/build/clean; logging + stdlib |

Total: **150 módulos**, **29.411 linhas**.

## Fronteiras e camadas reais

```text
Fachada: cko.core
  Fundação: contracts, exceptions, identity, metadata, config, models, logging, utils
  Domínio/motores: inventory, discovery, execution
  Coordenação: runtime, checkpoint, uow
  Ports: connectors, storage
  Adapters: storage.filesystem, storage.sqlite
  Infra interna: workspace
```

## Fluxos principais

```text
DiscoveryRequest
 -> DiscoveryService/ProviderRegistry
 -> Discovery Pipeline/Streaming
 -> Identity + Capability
 -> DiscoveryQuery
 -> Query Evaluation / Logical Index / Statistics
 -> CostBasedPlanner
 -> OptimizationPipeline
 -> ExecutionPlanner -> ExecutionPlan
 -> ExecutionEngine -> operators -> ExecutionResult
 -> Runtime -> lifecycle/resources/cancellation/report

ConnectorSession -> FilesystemConnector|SQLiteConnector
 -> bridge session -> Storage port implementation -> ConnectorResult

CheckpointEngine -> StorageCheckpointRepository -> Storage port
 -> FilesystemStorage|SQLiteStorage (injetado externamente)

DefaultUnitOfWork -> RepositoryCollection + UnitOfWorkOperation
 -> commit | compensation/rollback -> close

Workspace CLI -> init | validate | clean | build
```

## Pontos de extensão

- `DiscoveryProvider`, `Connector`, `Storage`, `ExecutionOperator`, `CheckpointRepository`, `CheckpointSerializer`, `UnitOfWork`.
- Registries `DiscoveryProviderRegistry`, `ConnectorRegistry`, `StorageRegistry` são por instância.
- Factories recebem registry/construtores ou compõem um adapter concreto localmente.
- `Clock`, ID factories e cancellation tokens permitem injeção parcial.

## Componentes públicos versus internos

No corte histórico pré-camada semântica, os `__init__.py` de 20 pacotes definiam as superfícies públicas. Arquivos sem export direto são detalhes internos mesmo quando classes não começam por `_`; consumidores devem importar do pacote. `workspace` é intencionalmente subnamespace interno e não é reexportado na raiz. Naquele corte, a fachada raiz reexportava 334 nomes até W. Na baseline vigente após a SPR-017, a fachada preserva 610 exports anteriores e acrescenta 36 exports de Provenance Statement, totalizando 646 nomes únicos e resolvidos.

## Divergência documental estrutural

ARCH-001 v1.1 descreve a árvore até T. A árvore efetiva contém U (`storage.sqlite`), V (`checkpoint`) e W (`uow`), todos reexportados por `cko.core`. Assim, as seções 7, 8, 22, 27–29 e 33 da ARCH requerem atualização pós-SPR-009.

## Atualização da baseline semântica — SPR-010–017

A árvore vigente contém **246 módulos Python** sob `src/cko/core`. À fundação histórica foram acrescentados os namespaces `knowledge`, `documents`, `relationships`, `graph`, `query`, `index`, `corpus` e `provenance`, homologados sucessivamente nas SPR-010–017.

`cko.core.__all__` contém **646 exports únicos e resolvidos**. A partição homologada é 610 exports preservados até a SPR-016 mais 36 exports da SPR-017. `provenance` depende apenas da biblioteca padrão, da raiz pública `cko.core.exceptions` e, para projeção explícita, da API pública `cko.core.relationships`; não introduz dependência de infraestrutura.

As contagens 150 módulos e 334 exports nas seções históricas permanecem como valores do corte original do mapa, não como estado corrente.
