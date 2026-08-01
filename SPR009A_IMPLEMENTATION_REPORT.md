# SPR-009A — Relatório de implementação

**Sprint:** SPR-009A — CORE SDK v1.0 — Consolidação pós-certificação  
**Data:** 2026-07-25  
**Escopo:** eliminação das quatro ressalvas P1 da SPR-009  
**Resultado técnico:** concluído

## 1. Resumo executivo

A SPR-009A consolidou o CKO CORE SDK como release `1.0.0` sem introduzir
funcionalidade de negócio. Foram eliminadas as quatro ressalvas P1:

1. ARCH-001 foi atualizada para v1.2 e alinhada aos 153 módulos reais.
2. Distribuição, fachada, egg-info, wheel e METADATA foram alinhados em `1.0.0`.
3. Todas as 120 exceções declaradas pelo CORE convergem em `CKOError`.
4. `cko.core.composition` tornou-se o Composition Root oficial.

Nenhum Knowledge Object, modelo semântico ou camada semântica foi criado.

## 2. Alterações de produção

### 2.1 Versionamento

| Ponto oficial | Antes | Depois |
|---|---:|---:|
| `pyproject.toml` | `0.1.0` | `1.0.0` |
| `cko.core.__version__` | `0.1.0` | `1.0.0` |
| `src/cko.egg-info/PKG-INFO` | `0.1.0` | `1.0.0` |
| wheel | `cko-0.1.0-py3-none-any.whl` | `cko-1.0.0-py3-none-any.whl` |
| wheel METADATA | `Version: 0.1.0` | `Version: 1.0.0` |

O Summary e `Requires-Python` do egg-info também foram alinhados ao
`pyproject.toml`: `CKO CORE SDK canonical foundation` e `>=3.13`.

### 2.2 Exceções

Foi adicionada `CompositionError`. As raízes históricas Connector, Storage,
Checkpoint, Runtime e Unit of Work passaram a herdar de `CKOError`. As famílias
Logical Index, Statistics, Planner, Optimizer, Execution Planner e Execution
Engine passaram a usar herança múltipla `CKOError, ValueError`.

Não houve alteração de nomes, construtores, atributos, códigos, mensagens ou
exports existentes. O comportamento de captura como `ValueError` foi preservado.

### 2.3 Composition Root

Foram criados:

```text
src/cko/core/composition/__init__.py
src/cko/core/composition/models.py
src/cko/core/composition/root.py
```

O root compõe:

```text
Logging
Workspace e Build
16 Validators
ConnectorRegistry e ConnectorFactory
StorageRegistry e StorageFactory
DiscoveryProviderRegistry, Resolver e Factory
Filesystem Connector e Storage
SQLite Connector e Storage
DiscoveryService
CostBasedPlanner e OptimizationPipeline
Execution Planner e ExecutionEngine
StorageCheckpointRepository e DefaultCheckpointEngine
DefaultUnitOfWork
Runtime
```

O container `CoreComposition` é frozen/slots. Mappings de adapters e validators
são read-only. Runtime e Unit of Work novos são obtidos por métodos do próprio
container, eliminando repetição de composição manual em módulos consumidores.

### 2.4 Fachada pública

`cko.core.__all__` passou de 334 para 346 símbolos, todos únicos e resolvidos.
Foram adicionados somente a hierarquia fundamental de exceções e os símbolos do
Composition Root. Nenhum export anterior foi removido.

## 3. Arquivos alterados

```text
pyproject.toml
src/cko.egg-info/PKG-INFO
src/cko/core/__init__.py
src/cko/core/exceptions/errors.py
src/cko/core/exceptions/__init__.py
src/cko/core/connectors/errors.py
src/cko/core/storage/errors.py
src/cko/core/checkpoint/errors.py
src/cko/core/uow/errors.py
src/cko/core/runtime/errors.py
src/cko/core/execution/errors.py
src/cko/core/discovery/query_index_errors.py
src/cko/core/discovery/statistics_errors.py
src/cko/core/discovery/planner_errors.py
src/cko/core/discovery/optimizer_errors.py
src/cko/core/discovery/execution_errors.py
```

## 4. Arquivos criados

```text
src/cko/core/composition/__init__.py
src/cko/core/composition/models.py
src/cko/core/composition/root.py
tests/test_core_consolidation_spr009a.py
SPR009A_IMPLEMENTATION_REPORT.md
CKO_CORE_V1_EXCEPTION_HIERARCHY.md
CKO_CORE_V1_COMPOSITION_ROOT.md
ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md
CKO_CORE_V1_RELEASE_CERTIFICATION.md
```

## 5. Restrições verificadas

| Restrição | Resultado |
|---|---|
| não alterar Storage | atendida; somente ancestralidade do erro |
| não alterar Runtime | atendida; somente ancestralidade do erro |
| não alterar Discovery | atendida; somente raízes de erros P1 |
| não alterar Execution | atendida; somente raiz de erro P1 |
| não alterar Checkpoint | atendida; somente ancestralidade do erro |
| não alterar UoW além da integração | atendida; engine e contratos intactos |
| não alterar serialização | atendida |
| não alterar schemas | atendida |
| não iniciar semântica | atendida |
| preservar API pública | atendida, mudança aditiva |

## 6. Testes dedicados

Comando executado:

```powershell
python -m pytest -p no:cacheprovider --basetemp=runtime\temp\pytest_spr009a tests\test_core_consolidation_spr009a.py -q
```

Resultado:

```text
17 passed in 2.82s
```

Cobertura comportamental da suíte:

- versão em manifest, fachada e egg-info;
- introspecção de todas as exceções declaradas;
- compatibilidade `ValueError`;
- composição real de Filesystem e SQLite;
- 16 validators e cinco UoW repositories;
- fresh Runtime e Unit of Work;
- mappings read-only;
- erro de storage de checkpoint não registrado;
- build, nome, METADATA e módulos do wheel;
- exports da fachada pública.

## 7. Regressão completa

Comando oficial:

```powershell
CKO_TESTS.cmd -q
```

Resultado:

```text
703 passed, 2 failed in 34.19s
```

As duas falhas são exatamente as falhas legadas registradas na SPR-009:

1. `tests/test_file_metadata.py::test_collect_metadata`: a API legada não
   aceita `calculate_hash`.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`:
   `cko.db` permanece aberto durante o teardown no Windows.

Não houve nova falha, skip ou regressão.

## 8. Runtime oficial

`CKO_RUNTIME.cmd` aprovou:

| Check | Evidência |
|---|---|
| Python | 3.13.14 |
| PowerShell | 5.1.26100.8894 |
| permissions | write/delete probe aprovado |
| encoding | UTF-8 |
| disk space | 135.130.963.968 bytes livres |

## 9. Build e wheel

`CKO_BUILD.cmd` gerou:

```text
runtime/reports/build/cko-1.0.0-py3-none-any.whl
```

Validação independente:

| Item | Resultado |
|---|---|
| entradas ZIP | 187 |
| módulos CORE | 153 |
| RECORD com hash | 186 entradas conferidas |
| ZIP CRC | íntegro |
| paths absolutos ou traversal | zero |
| timestamps | todos `1980-01-01 00:00:00` |
| METADATA Version | `1.0.0` |
| Requires-Python | `>=3.13` |
| import isolado do wheel | aprovado |
| Composition Root no wheel | aprovado |
| exceção canônica no wheel | aprovada |

Dois builds em diretórios independentes produziram:

```text
FD19FDDCD0FAC1471ABFF1E758AF89A8B381E3F20237263342A681A33ACF10CB
```

Uma tentativa dentro do sandbox não obteve permissão de escrita/lock do SQLite
e do wheel no Google Drive. As mesmas operações, executadas no ambiente oficial
fora do sandbox, passaram. A ocorrência é restrição do executor, não defeito do
SDK.

## 10. Documentação

Foram produzidos todos os cinco documentos requeridos. A ARCH v1.2 inclui
Filesystem, SQLite, Checkpoint, Unit of Work, Workspace, Build, Runtime,
Execution Engine, Execution Planner, dependências, ports, adapters, registries,
factories, validators, modelos públicos, fluxos, matrizes, responsabilidades,
roadmap, histórico e homologação.

## 11. Conclusão

As quatro ressalvas P1 foram eliminadas. O CORE SDK está tecnicamente consolidado
como `1.0.0`, sem funcionalidade nova e sem regressão nova.
