# CKO CORE — Relatório de Execução da Consolidação Controlada da Baseline

**Data:** 2026-07-31  
**Repositório:** `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`  
**Branch:** `main`  
**HEAD inicial:** `e94545919db97a071f08de2c08ce1a5dde06980e`  
**HEAD após C10:** `ddb213c0e8438c6f4c41fb5316752d6fca4eee5d`  
**Resultado:** baseline técnica e documental consolidada; registro final emitido em C11.

## 1. Estado inicial e integridade

O estado inicial continha 462 entradas visíveis: 2 modificadas e 460 não rastreadas, sem staging. As 461 entradas classificadas no apêndice anterior, somadas ao próprio relatório, correspondiam exatamente ao estado Git; nenhuma alteração posterior desconhecida foi encontrada.

`CKO_CORE_BASELINE_CONSOLIDATION_REPORT.md` foi lido integralmente. SHA-256 confirmado: `45CD1A4D431EDD302FF70BD324FBD2AF29BE0945FC6C4F734E2882E638D5B66C`.

Branch e HEAD iniciais coincidiram com a baseline. O diretório pai foi usado apenas para consulta e não recebeu Git.

## 2. Decisões autorizadas

- D-01: `runtime/` foi alterado somente para `/runtime/` no `.gitignore`.
- D-02: `src/main.py.txt` permaneceu intacto e fora.
- D-03: o discovery passou a registrar a CKO-RFC-001 sem definir SPR-018.
- D-04/D-05: documentação reconciliada com 646 exports, SDK 1.0.0 e valores históricos 334/346 explicitamente qualificados.
- D-06: C01–C10 formados conforme o inventário individual.
- D-07: itens locais, temporários e reproduzíveis ficaram fora.
- D-08: nenhum push foi realizado.

SPR-018 e PWAM não foram implementados. Código, testes, fixtures, vetores e contratos homologados da SPR-017 não foram alterados.

## 3. `.gitignore` e módulos liberados

A ancoragem liberou exclusivamente:

1. `src/cko/core/runtime/__init__.py`
2. `src/cko/core/runtime/cancellation.py`
3. `src/cko/core/runtime/errors.py`
4. `src/cko/core/runtime/lifecycle.py`
5. `src/cko/core/runtime/models.py`
6. `src/cko/core/runtime/resources.py`
7. `src/cko/core/runtime/runtime.py`
8. `src/cko/core/runtime/validator.py`

Os oito deixaram de ser ignorados. `runtime/.gitkeep` e `runtime/cko.db` continuaram ignorados por `/runtime/`. Arquivos adicionais expostos: nenhum. Nenhum item sensível/local tornou-se candidato.

## 4. Correções documentais

Foram reconciliados o discovery, catálogo da API, mapa, ARCH v1.2, matriz, versões históricas da ARCH, `README.md`, `CHANGELOG.md` e `ROADMAP.md`. O estado vigente é 610 exports preservados + 36 da SPR-017 = 646 únicos e resolvidos. 334/346 e 0.1.0 permanecem apenas como cortes históricos. A matriz inclui SPR-017. Verificação: zero mojibake real e zero links locais quebrados nos documentos modificados.

A CKO-RFC-001 existe no pai em `docs/arquitetura/CKO-RFC-001_PROJECT_WORKSPACE_AUTOMATION_MODULE.md` e está indexada no README, arquitetura e roadmap. Continua Proposta, prioridade Baixa, roadmap futuro e implementação Não autorizada. Não cria nem define SPR-018. A SPR-018 continua não iniciada, sem escopo, termo, especificação ou autorização.

## 5. Commits C01–C10

| ID | Hash | Arquivos | Mensagem |
|---|---|---:|---|
| C01 | `11d8ac96411c1d8ab2b6698e1408e29ea7600b84` | 282 | `chore(core): consolidate foundations through SPR-009A` |
| C02 | `0d3a9c7f4c861f96fd1161b7057ccb0d4beb5fcd` | 17 | `feat(core): consolidate SPR-010 knowledge object foundation` |
| C03 | `5dfe07bfb60e397e8d96048088919c08ff2908cf` | 16 | `feat(core): consolidate SPR-011 document model` |
| C04 | `c0a0cf6e9f5ab0a32e079cb9369ec01f76044301` | 17 | `feat(core): consolidate SPR-012 relationships` |
| C05 | `3d0e6239d1cc18ca10ce89b184b952c5047bf0c4` | 18 | `feat(core): consolidate SPR-013 graph` |
| C06 | `548586aa3fb485f671fd8398ef2bcd2dead6b950` | 16 | `feat(core): consolidate SPR-014 query` |
| C07 | `2b5d3dde604fdd0a87750d32833da9dde8f8a861` | 21 | `feat(core): consolidate SPR-015 index` |
| C08 | `0ebb90954c5e2cb548e1fce1dd78b88d4b00a2c1` | 19 | `feat(core): consolidate SPR-016 corpus` |
| C09 | `daf5040e14fe8d7d29c71d28d2f23a34b39cc7ac` | 30 | `feat(core): consolidate homologated SPR-017 provenance` |
| C10 | `ddb213c0e8438c6f4c41fb5316752d6fca4eee5d` | 29 | `docs(core): reconcile architecture governance and semantic release baseline` |

### C01 — `11d8ac96411c1d8ab2b6698e1408e29ea7600b84`

Mensagem: `chore(core): consolidate foundations through SPR-009A`  
Arquivos (282):

- `.gitignore`
- `CKO_BUILD.cmd`
- `CKO_CLEAN.cmd`
- `CKO_RUNTIME.cmd`
- `CKO_TESTS.cmd`
- `README_SPR_003.md`
- `README_SPR_004.md`
- `SPR005_MANIFEST.json`
- `SPR006A_MANIFEST.json`
- `SPR007B_ADVANCED_ENGINE.cmd`
- `SPR007B_ADVANCED_ENGINE.ps1`
- `SPR008A_IMPLEMENTATION_REPORT.md`
- `SPR008B_IMPLEMENTATION_REPORT.md`
- `SPR008C_IMPLEMENTATION_REPORT.md`
- `SPR008D_IMPLEMENTATION_REPORT.md`
- `SPR008E_IMPLEMENTATION_REPORT.md`
- `SPR008F_IMPLEMENTATION_REPORT.md`
- `SPR008G_IMPLEMENTATION_REPORT.md`
- `SPR008H_IMPLEMENTATION_REPORT.md`
- `SPR008I_IMPLEMENTATION_REPORT.md`
- `SPR008J_IMPLEMENTATION_REPORT.md`
- `SPR008K_IMPLEMENTATION_REPORT.md`
- `SPR008L_IMPLEMENTATION_REPORT.md`
- `SPR008M_IMPLEMENTATION_REPORT.md`
- `SPR008N_IMPLEMENTATION_REPORT.md`
- `SPR008OA_IMPLEMENTATION_REPORT.md`
- `SPR008O_IMPLEMENTATION_REPORT.md`
- `SPR008P_IMPLEMENTATION_REPORT.md`
- `SPR008Q_IMPLEMENTATION_REPORT.md`
- `SPR008R_IMPLEMENTATION_REPORT.md`
- `SPR008S_IMPLEMENTATION_REPORT.md`
- `SPR008T_IMPLEMENTATION_REPORT.md`
- `SPR008U_IMPLEMENTATION_REPORT.md`
- `SPR008V_IMPLEMENTATION_REPORT.md`
- `SPR008W_IMPLEMENTATION_REPORT.md`
- `SPR009A_IMPLEMENTATION_REPORT.md`
- `SPR009_ARCHITECTURE_CERTIFICATION_REPORT.md`
- `SPR009_IMPLEMENTATION_REPORT.md`
- `advanced_engine.py`
- `config/categories.yaml`
- `config/settings.yaml`
- `docs/decisoes/ADR-005A-001_PERSISTENCIA_ADITIVA.md`
- `docs/sprint/CKO-CORE-SPR-005_TERMO_DE_ABERTURA.md`
- `docs/sprint/CKO-CORE-SPR-006A_TERMO_DE_ABERTURA.md`
- `docs/sprint/CKO-SPR-003_TERMO_DE_ABERTURA.md`
- `docs/sprint/CKO-SPR-004_TERMO_DE_ABERTURA.md`
- `docs/sprint/CKO-SPR-005A_TERMO_OFICIAL.md`
- `docs/sprint/SPR004_REPORT.md`
- `docs/sprint/SPR005_REPORT.md`
- `docs/sprint/SPR006A_REPORT.md`
- `migrations/005001_spr005a_persistence.sql`
- `pyproject.toml`
- `reports/SPR007B_ADVANCED_REPORT.md`
- `reports/spr008j_trace/.gitkeep`
- `reports/spr008m_trace/.gitkeep`
- `scripts/INICIALIZAR_BANCO_CANONICO.ps1`
- `scripts/REVERTER_SPR005.ps1`
- `scripts/REVERTER_SPR006A.ps1`
- `scripts/RUN_SPR_003_COMMIT.ps1`
- `scripts/RUN_SPR_003_DRY_RUN.ps1`
- `scripts/RUN_SPR_004_COMMIT.ps1`
- `scripts/RUN_SPR_004_DRY_RUN.ps1`
- `scripts/SPR005A_MIGRAR_E_VALIDAR.ps1`
- `scripts/SPR005A_SQLITE_BACKUP.py`
- `scripts/VALIDAR_SPR005.ps1`
- `scripts/VALIDAR_SPR006A.ps1`
- `src/cko/__init__.py`
- `src/cko/api/__init__.py`
- `src/cko/classifier/__init__.py`
- `src/cko/contracts/__init__.py`
- `src/cko/contracts/repositories.py`
- `src/cko/contracts/scanner.py`
- `src/cko/core/checkpoint/__init__.py`
- `src/cko/core/checkpoint/contracts.py`
- `src/cko/core/checkpoint/engine.py`
- `src/cko/core/checkpoint/errors.py`
- `src/cko/core/checkpoint/models.py`
- `src/cko/core/checkpoint/repository.py`
- `src/cko/core/checkpoint/serializer.py`
- `src/cko/core/checkpoint/validator.py`
- `src/cko/core/composition/__init__.py`
- `src/cko/core/composition/models.py`
- `src/cko/core/composition/root.py`
- `src/cko/core/config/__init__.py`
- `src/cko/core/config/settings.py`
- `src/cko/core/connectors/__init__.py`
- `src/cko/core/connectors/contracts.py`
- `src/cko/core/connectors/errors.py`
- `src/cko/core/connectors/factory.py`
- `src/cko/core/connectors/models.py`
- `src/cko/core/connectors/registry.py`
- `src/cko/core/connectors/validator.py`
- `src/cko/core/contracts/__init__.py`
- `src/cko/core/contracts/base.py`
- `src/cko/core/discovery/__init__.py`
- `src/cko/core/discovery/cancellation.py`
- `src/cko/core/discovery/capability_errors.py`
- `src/cko/core/discovery/capability_models.py`
- `src/cko/core/discovery/capability_negotiation.py`
- `src/cko/core/discovery/capability_validation.py`
- `src/cko/core/discovery/checkpoints.py`
- `src/cko/core/discovery/contracts.py`
- `src/cko/core/discovery/errors.py`
- `src/cko/core/discovery/events.py`
- `src/cko/core/discovery/execution.py`
- `src/cko/core/discovery/execution_errors.py`
- `src/cko/core/discovery/execution_models.py`
- `src/cko/core/discovery/execution_planner.py`
- `src/cko/core/discovery/foundation_errors.py`
- `src/cko/core/discovery/identity_contracts.py`
- `src/cko/core/discovery/identity_errors.py`
- `src/cko/core/discovery/identity_models.py`
- `src/cko/core/discovery/identity_resolution.py`
- `src/cko/core/discovery/mapper.py`
- `src/cko/core/discovery/models.py`
- `src/cko/core/discovery/optimizer.py`
- `src/cko/core/discovery/optimizer_errors.py`
- `src/cko/core/discovery/optimizer_models.py`
- `src/cko/core/discovery/optimizer_rules.py`
- `src/cko/core/discovery/pipeline.py`
- `src/cko/core/discovery/planner.py`
- `src/cko/core/discovery/planner_errors.py`
- `src/cko/core/discovery/planner_models.py`
- `src/cko/core/discovery/policies.py`
- `src/cko/core/discovery/providers.py`
- `src/cko/core/discovery/query_errors.py`
- `src/cko/core/discovery/query_evaluation.py`
- `src/cko/core/discovery/query_evaluation_contracts.py`
- `src/cko/core/discovery/query_evaluation_errors.py`
- `src/cko/core/discovery/query_evaluation_models.py`
- `src/cko/core/discovery/query_index.py`
- `src/cko/core/discovery/query_index_errors.py`
- `src/cko/core/discovery/query_index_models.py`
- `src/cko/core/discovery/query_models.py`
- `src/cko/core/discovery/query_resolution.py`
- `src/cko/core/discovery/query_validation.py`
- `src/cko/core/discovery/service.py`
- `src/cko/core/discovery/session.py`
- `src/cko/core/discovery/statistics.py`
- `src/cko/core/discovery/statistics_errors.py`
- `src/cko/core/discovery/statistics_models.py`
- `src/cko/core/discovery/stream.py`
- `src/cko/core/discovery/streaming_contracts.py`
- `src/cko/core/discovery/streaming_errors.py`
- `src/cko/core/discovery/streaming_models.py`
- `src/cko/core/discovery/streaming_pipeline.py`
- `src/cko/core/discovery/validator.py`
- `src/cko/core/exceptions/__init__.py`
- `src/cko/core/exceptions/errors.py`
- `src/cko/core/execution/__init__.py`
- `src/cko/core/execution/engine.py`
- `src/cko/core/execution/errors.py`
- `src/cko/core/execution/models.py`
- `src/cko/core/execution/operators.py`
- `src/cko/core/execution/pipeline.py`
- `src/cko/core/execution/validator.py`
- `src/cko/core/identity/__init__.py`
- `src/cko/core/identity/identifier.py`
- `src/cko/core/identity/origin.py`
- `src/cko/core/identity/version.py`
- `src/cko/core/inventory/__init__.py`
- `src/cko/core/inventory/builder.py`
- `src/cko/core/inventory/engine.py`
- `src/cko/core/inventory/errors.py`
- `src/cko/core/inventory/models.py`
- `src/cko/core/inventory/service.py`
- `src/cko/core/inventory/validator.py`
- `src/cko/core/logging/__init__.py`
- `src/cko/core/logging/structured.py`
- `src/cko/core/metadata/__init__.py`
- `src/cko/core/metadata/universal.py`
- `src/cko/core/models/__init__.py`
- `src/cko/core/models/asset.py`
- `src/cko/core/models/document.py`
- `src/cko/core/models/event.py`
- `src/cko/core/runtime/__init__.py`
- `src/cko/core/runtime/cancellation.py`
- `src/cko/core/runtime/errors.py`
- `src/cko/core/runtime/lifecycle.py`
- `src/cko/core/runtime/models.py`
- `src/cko/core/runtime/resources.py`
- `src/cko/core/runtime/runtime.py`
- `src/cko/core/runtime/validator.py`
- `src/cko/core/storage/__init__.py`
- `src/cko/core/storage/contracts.py`
- `src/cko/core/storage/errors.py`
- `src/cko/core/storage/factory.py`
- `src/cko/core/storage/filesystem/__init__.py`
- `src/cko/core/storage/filesystem/connector.py`
- `src/cko/core/storage/filesystem/descriptor.py`
- `src/cko/core/storage/filesystem/factory.py`
- `src/cko/core/storage/filesystem/resolver.py`
- `src/cko/core/storage/filesystem/result.py`
- `src/cko/core/storage/filesystem/session.py`
- `src/cko/core/storage/filesystem/storage.py`
- `src/cko/core/storage/filesystem/validator.py`
- `src/cko/core/storage/models.py`
- `src/cko/core/storage/registry.py`
- `src/cko/core/storage/sqlite/__init__.py`
- `src/cko/core/storage/sqlite/connector.py`
- `src/cko/core/storage/sqlite/descriptor.py`
- `src/cko/core/storage/sqlite/factory.py`
- `src/cko/core/storage/sqlite/resolver.py`
- `src/cko/core/storage/sqlite/result.py`
- `src/cko/core/storage/sqlite/session.py`
- `src/cko/core/storage/sqlite/storage.py`
- `src/cko/core/storage/sqlite/validator.py`
- `src/cko/core/storage/validator.py`
- `src/cko/core/uow/__init__.py`
- `src/cko/core/uow/contracts.py`
- `src/cko/core/uow/engine.py`
- `src/cko/core/uow/errors.py`
- `src/cko/core/uow/models.py`
- `src/cko/core/uow/validator.py`
- `src/cko/core/utils/__init__.py`
- `src/cko/core/utils/text.py`
- `src/cko/core/utils/time.py`
- `src/cko/core/workspace/__init__.py`
- `src/cko/core/workspace/build.py`
- `src/cko/core/workspace/cleaner.py`
- `src/cko/core/workspace/cli.py`
- `src/cko/core/workspace/manager.py`
- `src/cko/core/workspace/paths.py`
- `src/cko/core/workspace/validator.py`
- `src/cko/kb/__init__.py`
- `src/cko/kb/database.py`
- `src/cko/metadata/__init__.py`
- `src/cko/metadata/file_metadata.py`
- `src/cko/migrations/0001_initial_schema.sql`
- `src/cko/migrations/__init__.py`
- `src/cko/migrations/runner.py`
- `src/cko/models/__init__.py`
- `src/cko/models/document.py`
- `src/cko/models/job.py`
- `src/cko/organizer/__init__.py`
- `src/cko/persistence/__init__.py`
- `src/cko/persistence/cli.py`
- `src/cko/persistence/database.py`
- `src/cko/persistence/migrations.py`
- `src/cko/repository/__init__.py`
- `src/cko/repository/database.py`
- `src/cko/scanner/__init__.py`
- `src/cko/scanner/inventory.py`
- `src/cko/scanner/scanner.py`
- `src/cko/scanner/watcher.py`
- `src/cko/services/__init__.py`
- `src/cko/services/inventory_service.py`
- `src/cko/utils/__init__.py`
- `src/cko/utils/file_utils.py`
- `src/main.py`
- `tests/fixtures/spr008a_config.toml`
- `tests/fixtures/spr008a_config.yaml`
- `tests/test_architecture_spr005.py`
- `tests/test_canonical_asset_model_spr008b.py`
- `tests/test_checkpoint_foundation_spr008v.py`
- `tests/test_connector_abstraction_spr008r.py`
- `tests/test_core_consolidation_spr009a.py`
- `tests/test_core_sdk_spr008a.py`
- `tests/test_cost_based_planner_spr008m.py`
- `tests/test_discovery_capability_model_spr008h.py`
- `tests/test_discovery_contracts_spr008d.py`
- `tests/test_discovery_identity_resolution_spr008g.py`
- `tests/test_discovery_provider_foundation_spr008e.py`
- `tests/test_discovery_query_evaluation_spr008j.py`
- `tests/test_discovery_query_foundation_spr008i.py`
- `tests/test_discovery_query_index_foundation_spr008k.py`
- `tests/test_discovery_statistics_foundation_spr008l.py`
- `tests/test_discovery_streaming_foundation_spr008f.py`
- `tests/test_execution_engine_spr008p.py`
- `tests/test_execution_planner_spr008o.py`
- `tests/test_file_metadata.py`
- `tests/test_filesystem_storage_connector_spr008t.py`
- `tests/test_inventory_engine_spr008c.py`
- `tests/test_metadata_spr004.py`
- `tests/test_migrations_spr006a.py`
- `tests/test_persistence_spr005a.py`
- `tests/test_query_optimizer_spr008n.py`
- `tests/test_runtime_spr008q.py`
- `tests/test_sqlite_storage_adapter_spr008u.py`
- `tests/test_storage_abstraction_spr008s.py`
- `tests/test_unit_of_work_foundation_spr008w.py`
- `tests/test_workspace_manager.py`

### C02 — `0d3a9c7f4c861f96fd1161b7057ccb0d4beb5fcd`

Mensagem: `feat(core): consolidate SPR-010 knowledge object foundation`  
Arquivos (17):

- `CKO_KNOWLEDGE_OBJECT_API.md`
- `CKO_KNOWLEDGE_OBJECT_ARCHITECTURE.md`
- `CKO_KNOWLEDGE_OBJECT_SERIALIZATION.md`
- `CKO_KNOWLEDGE_OBJECT_VERSIONING.md`
- `SPR010_IMPLEMENTATION_REPORT.md`
- `src/cko/core/knowledge/__init__.py`
- `src/cko/core/knowledge/contracts.py`
- `src/cko/core/knowledge/enums.py`
- `src/cko/core/knowledge/errors.py`
- `src/cko/core/knowledge/factory.py`
- `src/cko/core/knowledge/identity.py`
- `src/cko/core/knowledge/metadata.py`
- `src/cko/core/knowledge/models.py`
- `src/cko/core/knowledge/serializer.py`
- `src/cko/core/knowledge/validator.py`
- `src/cko/core/knowledge/versioning.py`
- `tests/test_knowledge_object_foundation_spr010.py`

### C03 — `5dfe07bfb60e397e8d96048088919c08ff2908cf`

Mensagem: `feat(core): consolidate SPR-011 document model`  
Arquivos (16):

- `CKO_DOCUMENT_API.md`
- `CKO_DOCUMENT_MODEL_ARCHITECTURE.md`
- `CKO_DOCUMENT_MODEL_GUIDE.md`
- `CKO_DOCUMENT_SERIALIZATION.md`
- `SPR011_IMPLEMENTATION_REPORT.md`
- `src/cko/core/documents/__init__.py`
- `src/cko/core/documents/contracts.py`
- `src/cko/core/documents/enums.py`
- `src/cko/core/documents/errors.py`
- `src/cko/core/documents/factory.py`
- `src/cko/core/documents/identity.py`
- `src/cko/core/documents/metadata.py`
- `src/cko/core/documents/models.py`
- `src/cko/core/documents/serializer.py`
- `src/cko/core/documents/validator.py`
- `tests/test_document_canonical_model_spr011.py`

### C04 — `c0a0cf6e9f5ab0a32e079cb9369ec01f76044301`

Mensagem: `feat(core): consolidate SPR-012 relationships`  
Arquivos (17):

- `CKO_RELATIONSHIP_API.md`
- `CKO_RELATIONSHIP_ARCHITECTURE.md`
- `CKO_RELATIONSHIP_MODEL_GUIDE.md`
- `CKO_RELATIONSHIP_SERIALIZATION.md`
- `SPR012_IMPLEMENTATION_REPORT.md`
- `src/cko/core/knowledge/relationships.py`
- `src/cko/core/relationships/__init__.py`
- `src/cko/core/relationships/contracts.py`
- `src/cko/core/relationships/enums.py`
- `src/cko/core/relationships/errors.py`
- `src/cko/core/relationships/factory.py`
- `src/cko/core/relationships/identity.py`
- `src/cko/core/relationships/metadata.py`
- `src/cko/core/relationships/models.py`
- `src/cko/core/relationships/serializer.py`
- `src/cko/core/relationships/validator.py`
- `tests/test_knowledge_relationship_foundation_spr012.py`

### C05 — `3d0e6239d1cc18ca10ce89b184b952c5047bf0c4`

Mensagem: `feat(core): consolidate SPR-013 graph`  
Arquivos (18):

- `CKO_GRAPH_API.md`
- `CKO_GRAPH_ARCHITECTURE.md`
- `CKO_GRAPH_MODEL_GUIDE.md`
- `CKO_GRAPH_NAVIGATION.md`
- `CKO_GRAPH_SERIALIZATION.md`
- `SPR013_IMPLEMENTATION_REPORT.md`
- `src/cko/core/graph/__init__.py`
- `src/cko/core/graph/contracts.py`
- `src/cko/core/graph/enums.py`
- `src/cko/core/graph/errors.py`
- `src/cko/core/graph/factory.py`
- `src/cko/core/graph/identity.py`
- `src/cko/core/graph/metadata.py`
- `src/cko/core/graph/models.py`
- `src/cko/core/graph/navigation.py`
- `src/cko/core/graph/serializer.py`
- `src/cko/core/graph/validator.py`
- `tests/test_knowledge_graph_foundation_spr013.py`

### C06 — `548586aa3fb485f671fd8398ef2bcd2dead6b950`

Mensagem: `feat(core): consolidate SPR-014 query`  
Arquivos (16):

- `CKO_QUERY_API.md`
- `CKO_QUERY_ARCHITECTURE.md`
- `CKO_QUERY_MODEL_GUIDE.md`
- `CKO_QUERY_SERIALIZATION.md`
- `SPR014_IMPLEMENTATION_REPORT.md`
- `src/cko/core/query/__init__.py`
- `src/cko/core/query/contracts.py`
- `src/cko/core/query/enums.py`
- `src/cko/core/query/errors.py`
- `src/cko/core/query/factory.py`
- `src/cko/core/query/identity.py`
- `src/cko/core/query/metadata.py`
- `src/cko/core/query/models.py`
- `src/cko/core/query/serializer.py`
- `src/cko/core/query/validator.py`
- `tests/test_knowledge_query_foundation_spr014.py`

### C07 — `2b5d3dde604fdd0a87750d32833da9dde8f8a861`

Mensagem: `feat(core): consolidate SPR-015 index`  
Arquivos (21):

- `CKO_INDEX_API.md`
- `CKO_INDEX_ARCHITECTURE.md`
- `CKO_INDEX_MODEL_GUIDE.md`
- `CKO_INDEX_OPERATIONS.md`
- `CKO_INDEX_SERIALIZATION.md`
- `SPR015_IMPLEMENTATION_REPORT.md`
- `src/cko/core/graph/indexes.py`
- `src/cko/core/index/__init__.py`
- `src/cko/core/index/builder.py`
- `src/cko/core/index/contracts.py`
- `src/cko/core/index/enums.py`
- `src/cko/core/index/errors.py`
- `src/cko/core/index/factory.py`
- `src/cko/core/index/identity.py`
- `src/cko/core/index/metadata.py`
- `src/cko/core/index/models.py`
- `src/cko/core/index/operations.py`
- `src/cko/core/index/serializer.py`
- `src/cko/core/index/statistics.py`
- `src/cko/core/index/validator.py`
- `tests/test_knowledge_index_foundation_spr015.py`

### C08 — `0ebb90954c5e2cb548e1fce1dd78b88d4b00a2c1`

Mensagem: `feat(core): consolidate SPR-016 corpus`  
Arquivos (19):

- `CKO_CORPUS_API.md`
- `CKO_CORPUS_ARCHITECTURE.md`
- `CKO_CORPUS_MODEL_GUIDE.md`
- `CKO_CORPUS_OPERATIONS.md`
- `CKO_CORPUS_SERIALIZATION.md`
- `SPR016_IMPLEMENTATION_REPORT.md`
- `SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`
- `src/cko/core/corpus/__init__.py`
- `src/cko/core/corpus/builder.py`
- `src/cko/core/corpus/contracts.py`
- `src/cko/core/corpus/enums.py`
- `src/cko/core/corpus/errors.py`
- `src/cko/core/corpus/factory.py`
- `src/cko/core/corpus/identity.py`
- `src/cko/core/corpus/models.py`
- `src/cko/core/corpus/operations.py`
- `src/cko/core/corpus/serializer.py`
- `src/cko/core/corpus/validator.py`
- `tests/test_knowledge_corpus_foundation_spr016.py`

### C09 — `daf5040e14fe8d7d29c71d28d2f23a34b39cc7ac`

Mensagem: `feat(core): consolidate homologated SPR-017 provenance`  
Arquivos (30):

- `CKO_PROVENANCE_STATEMENT_API.md`
- `CKO_PROVENANCE_STATEMENT_ARCHITECTURE.md`
- `CKO_PROVENANCE_STATEMENT_INTEGRATION.md`
- `CKO_PROVENANCE_STATEMENT_MODEL_GUIDE.md`
- `CKO_PROVENANCE_STATEMENT_OPERATIONS.md`
- `CKO_PROVENANCE_STATEMENT_SERIALIZATION.md`
- `SPR017E_NOVA_AUDITORIA_FORMAL.md`
- `SPR017G_VERIFICACAO_FINAL.md`
- `SPR017_HOMOLOGATION_REPORT.md`
- `SPR017_IMPLEMENTATION_REPORT.md`
- `SPR017_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`
- `SPR017_TECHNICAL_SPECIFICATION.md`
- `SPR017_TECHNICAL_SPECIFICATION_AUDIT.md`
- `src/cko/core/__init__.py`
- `src/cko/core/provenance/__init__.py`
- `src/cko/core/provenance/constants.py`
- `src/cko/core/provenance/contracts.py`
- `src/cko/core/provenance/enums.py`
- `src/cko/core/provenance/errors.py`
- `src/cko/core/provenance/factory.py`
- `src/cko/core/provenance/identity.py`
- `src/cko/core/provenance/models.py`
- `src/cko/core/provenance/operations.py`
- `src/cko/core/provenance/references.py`
- `src/cko/core/provenance/relationship_projection.py`
- `src/cko/core/provenance/results.py`
- `src/cko/core/provenance/serializer.py`
- `src/cko/core/provenance/validator.py`
- `src/cko/core/provenance/versioning.py`
- `tests/test_knowledge_provenance_statement_foundation_spr017.py`

### C10 — `ddb213c0e8438c6f4c41fb5316752d6fca4eee5d`

Mensagem: `docs(core): reconcile architecture governance and semantic release baseline`  
Arquivos (29):

- `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md`
- `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.1.md`
- `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md`
- `ARQUITETURA_ATUAL.txt`
- `CHANGELOG.md`
- `CKO_CORE_BASELINE_CONSOLIDATION_REPORT.md`
- `CKO_CORE_V1_ARCHITECTURE_DECISION.md`
- `CKO_CORE_V1_ARCHITECTURE_MAP.md`
- `CKO_CORE_V1_COMPOSITION_ROOT.md`
- `CKO_CORE_V1_DEPENDENCY_MATRIX.md`
- `CKO_CORE_V1_EXCEPTION_CATALOG.md`
- `CKO_CORE_V1_EXCEPTION_HIERARCHY.md`
- `CKO_CORE_V1_GAP_ANALYSIS.md`
- `CKO_CORE_V1_LOGGING_EVENT_CATALOG.md`
- `CKO_CORE_V1_PUBLIC_API_CATALOG.md`
- `CKO_CORE_V1_RELEASE_CERTIFICATION.md`
- `CKO_CORE_V1_SEMANTIC_READINESS_REPORT.md`
- `CKO_CORE_V1_TEST_AND_COVERAGE_REPORT.md`
- `README.md`
- `ROADMAP.md`
- `SPR018_DISCOVERY_AND_SCOPE.md`
- `docs/adr/ADR-001_MONOLITO_MODULAR_INCREMENTAL.md`
- `docs/adr/ADR-002_IDENTIDADE_DOCUMENTAL.md`
- `docs/adr/ADR-003_PRESERVACAO_DO_LEGADO.md`
- `docs/adr/ADR-004_BANCO_CANONICO_SEPARADO.md`
- `docs/adr/INDEX.md`
- `docs/architecture/CKO_CORE_ARQUITETURA_SPR005.md`
- `docs/architecture/CKO_CORE_BASELINE_2026-07-11.md`
- `docs/governance/BASELINE_PREPARATION_REPORT.md`

## 6. Verificações

| Grupo | Verificação | Resultado |
|---|---|---|
| Pré-C01 | ferramenta/configuração | Python 3.13.14; `cko` 1.0.0; `python -m pytest`; `PYTHONPATH=src`; temporários fora do Drive |
| C01 | 30 arquivos de teste | 703 passed; 2 falhas históricas; zero falha nova |
| C02 | Knowledge Object | 29 passed |
| C03 | Document | 30 passed |
| C04 | Relationship | 30 passed |
| C05 | Graph | 14 passed |
| C06 | Query | 19 passed |
| C07 | Index | 25 passed |
| C08 | Corpus | 28 passed |
| C09 | dedicada SPR-017 | 50/50 passed |
| C09 | integração SPR-010–017 | 225/225 passed |
| C09 | regressão completa | 928 passed; 2 falhas históricas; zero regressão nova |
| C09 | API pública | 646 entradas, 646 únicas, 646 resolvidas |
| C09 | partição | 610 anteriores + 36 SPR-017; zero colisão |
| C09 | AC-001–AC-090 | 90/90 PASS |
| C10 | links, números, matriz e estados | aprovado; 0 links quebrados; 0 mojibake real |

C10 foi exclusivamente documental, sem configuração, empacotamento, código ou testes; a regressão completa do gate C09 permaneceu o resultado final aplicável.

## 7. Falhas históricas

1. `tests/test_file_metadata.py::test_collect_metadata` — `collect_metadata()` não aceita `calculate_hash`.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved` — lock de `cko.db` no teardown em Windows.

Ambas precedem a baseline e foram reproduzidas sem alteração. Não ocorreu terceira falha.

## 8. Integridade da SPR-017

| Documento | SHA-256 final |
|---|---|
| `SPR017_TECHNICAL_SPECIFICATION.md` | `D19FA36A85F9BB761A11E65EC32D4D39A9C8BB8DFD290F621101488DB0B4862D` |
| `SPR017_IMPLEMENTATION_REPORT.md` | `6EFF3E326D379CAE109BCE9B06FBC7B9D5F34A985D64378B49F98B57A2FF2EA0` |
| `SPR017_HOMOLOGATION_REPORT.md` | `A7D062962AFD016EED784F17FD8C3A6D766CCB938D8AA83C746665AC3E2C4C13` |

Todos coincidem com a homologação.

## 9. Itens fora

Entradas visíveis não rastreadas:

- `.vscode/extensions.json`
- `.vscode/tasks.json`
- `inventory.txt`
- `src/cko.egg-info/PKG-INFO`
- `src/cko.egg-info/SOURCES.txt`
- `src/cko.egg-info/dependency_links.txt`
- `src/cko.egg-info/top_level.txt`
- `src/main.py.txt`

Também ficaram fora artefatos ignorados de `runtime/` e `logs/`, ZIPs de inventário, `.vscode/settings.json`, relatórios reproduzíveis, cobertura, caches, ambientes, instalações, builds, bancos locais e demais itens excluídos. Nada foi apagado, movido, renomeado ou descartado.

## 10. Pendências

- Duas falhas históricas registradas e não corrigidas.
- Oito entradas visíveis deliberadamente fora.
- Revisão humana local necessária antes de push.
- CKO-RFC-001 não autorizada.
- SPR-018 não iniciada.

## 11. C11, HEAD final e SHA-256 deste relatório

C11 é necessário porque o relatório registra hashes e arquivos de C01–C10 e só pode ser byte-final depois de C10. C11 é exclusivamente documental, mensagem `docs(core): record controlled baseline consolidation`.

O SHA-256 dos bytes finais, o hash C11 e o HEAD final são calculados após a gravação/commit e registrados externamente no fechamento. Inserir no próprio arquivo seu hash integral ou o hash do commit que contém o arquivo criaria autorreferência impossível.

## 12. Estado final e gate

Estado esperado após C11: somente as oito entradas visíveis listadas na seção 9; índice vazio; nenhum push.

- C01–C10 concluídos com staging explícito;
- oito módulos SPR-008Q versionados;
- `src/main.py.txt` fora;
- nenhum sensível/temporário incluído;
- hashes SPR-017 intactos;
- zero regressão nova;
- 646 exports confirmados;
- 90/90 critérios;
- documentação reconciliada;
- RFC não autorizada;
- SPR-018 não iniciada;
- nenhum push.

**Baseline do CKO CORE consolidada localmente e pronta para revisão antes do push.**
