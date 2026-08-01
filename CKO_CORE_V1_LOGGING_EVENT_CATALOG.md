# CKO CORE v1 — Catálogo de eventos de logging

## Implementação transversal

`src/cko/core/logging/structured.py` produz JSON com `timestamp`, `level`, `logger`, `message`, `event`, `context` e exceção formatada. `get_logger()` cria descendentes de `cko`; módulos novos de Checkpoint usam diretamente loggers sob o prefixo `cko.core`, ainda capturáveis. `configure_logging()` limpa handlers do logger alvo e instala um `StreamHandler`, comportamento idempotente porém potencialmente invasivo para aplicações.

## Eventos encontrados

| Evento/mensagem | Emissor | Nível | Contexto principal | Risco |
|---|---|---|---|---|
| `checkpoint_created` | checkpoint.engine | INFO | ids/estado | baixo; sem payload |
| `checkpoint_validated` | checkpoint.engine | INFO | ids | baixo |
| `checkpoint_superseded` | checkpoint.engine | INFO | sucessor | baixo |
| `checkpoint_stored` | checkpoint.repository | INFO | ids | baixo |
| `checkpoint_restored` | checkpoint.repository | INFO | ids | baixo |
| `checkpoint_listed` | checkpoint.repository | INFO | count/total | baixo |
| `checkpoint_inspected` | checkpoint.repository | INFO | ids | baixo |
| `checkpoint_deleted` | checkpoint.repository | INFO | checkpoint/namespace/subject/sequence | médio: subject pode ser sensível |
| `checkpoint_operation_failed` | checkpoint.repository | ERROR | operation/error_code | baixo |
| `checkpoint_serialized` | checkpoint.serializer | INFO | checkpoint_id/size | baixo |
| `checkpoint_integrity_failed` | checkpoint.serializer | ERROR | ids | baixo |
| `connector_created` | connectors.factory | INFO | connector_id | baixo |
| `connector_session_started` | connectors.models | INFO | connector/session id | baixo |
| `connector_session_finished` | connectors.models | INFO | connector/session/state | baixo |
| `connector_registered` | connectors.registry | INFO | connector_id | baixo |
| `connector_validated` | connectors.validator | INFO | component/connector_id | baixo |
| `storage_created` | storage.factory | INFO | storage_id | baixo |
| `storage_session_started` | storage.models | INFO | storage/session id | baixo |
| `storage_session_finished` | storage.models | INFO | storage/session/state | baixo |
| `storage_registered` | storage.registry | INFO | storage_id | baixo |
| `storage_validated` | storage.validator | INFO | component/storage_id | baixo |
| `filesystem_<operation>` | filesystem.storage | INFO | operação/estado | médio: confirmar que path não entra em contexto |
| `sqlite_<operation>` | sqlite.storage | INFO | operação/estado | médio: SQL não deve entrar; testes confirmam ausência |
| `discovery cancellation requested` | discovery.cancellation | INFO | token/reason | médio: reason livre |
| `discovery.capability.negotiation.started` | capability_negotiation | INFO | contagens | baixo |
| `discovery.capability.negotiation.completed` | capability_negotiation | INFO | contagens/valid | baixo |
| `discovery provider execution completed` | discovery.execution | INFO | provider/session/request/status | baixo |
| `identity resolution completed` | identity_resolution | INFO | request/session/status/count | baixo |
| `discovery.query.optimizer.<name>` | optimizer | INFO | decisão dinâmica | baixo, nome dinâmico dificulta catálogo |
| `discovery provider registered` | providers | INFO | id/capabilities/modes | baixo; falta `event` explícito |
| `discovery provider unregistered` | providers | INFO | provider_id | baixo; falta `event` |
| `discovery.query.resolution.started` | query_resolution | INFO | query_id | baixo |
| `discovery.query.resolution.completed` | query_resolution | INFO | query_id/contagens | baixo |
| `discovery.query.resolution.rejected` | query_resolution | WARNING | query_id | baixo |
| `discovery.query.resolution.failed` | query_resolution | ERROR | query_id | baixo |
| `discovery started` | discovery.service | INFO | request/source | médio; falta `event` explícito |
| `discovery failed` | discovery.service | ERROR | erro | médio: mensagem de causa |
| `discovery session transitioned` | discovery.session | INFO | ids/state/provider | baixo |
| `discovery batch yielded` | discovery.stream | INFO | ids/sequence/items/final | baixo |
| `discovery stream transitioned` | discovery.stream | INFO | ids/state/failure | médio: failure livre |
| mensagem dinâmica de streaming | streaming_pipeline | WARNING | error_type/error | alto: texto de exceção pode conter path/URL |
| `inventory.asset.registered` | inventory.engine | INFO | inventory/asset/revision | baixo |
| `inventory.asset.removed` | inventory.engine | INFO | inventory/asset/revision | baixo |
| `uow_<event>` | uow.engine | INFO | uow/correlation/state + ids | baixo; evento dinâmico controlado |
| `workspace_created` | workspace.manager | INFO | root/created | alto: path local completo |
| `validation_completed` | workspace.validator | INFO | checks | baixo |
| evento dinâmico de limpeza | workspace.cleaner | INFO | dry_run/count/paths | alto: lista de paths |
| `build_completed` | workspace.build | INFO | artifact/files | alto: path local completo |

Total: **48 chamadas**. Eventos de adapter/UoW são funções com conjunto finito de nomes em runtime; a tabela representa a família, enquanto o AST registra a expressão dinâmica.

## Achados

- Três padrões coexistem: `snake_case`, `dot.case` e frases com espaços.
- Parte de Discovery usa apenas `message/context`, sem `extra.event`; o JSON fica sem chave `event`.
- Não há correlation ID obrigatório transversal; UoW e vários contextos possuem um, outros não.
- Não foi encontrado `basicConfig()` em produção nem handler global fora de `configure_logging()`.
- Checkpoint omite payload e segredo por teste explícito.
- Workspace registra paths completos; streaming pode registrar `str(error)`.

## Taxonomia proposta, sem alteração de código

Formato: `cko.<domain>.<entity>.<past_tense>`; por exemplo `cko.discovery.query.resolution.completed`, `cko.storage.session.started`, `cko.checkpoint.record.stored`. Campos mínimos: `event_version`, `correlation_id`, `component`, `state`, identificadores opacos e `error_code`. Campos proibidos sem redaction: payload, conteúdo, credencial, URL com query, SQL, path absoluto e exception string não sanitizada.

Níveis: DEBUG para detalhes repetitivos; INFO para lifecycle/decisão; WARNING para rejeição recuperável; ERROR para operação falha; CRITICAL apenas indisponibilidade sistêmica. A aplicação continua proprietária de handlers/sinks.
