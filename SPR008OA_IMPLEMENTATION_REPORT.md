# SPR-008OA — CKO CORE SDK — Development Workspace & Build Infrastructure

## 1. Objetivo

Implementar a infraestrutura canônica de desenvolvimento local do CKO CORE SDK
para criação e localização do workspace, isolamento de artefatos temporários,
limpeza segura, build, testes, validação ambiental e logging auditável.

A implementação é exclusivamente interna. Nenhuma API pública, contrato
funcional, regra de negócio ou arquitetura homologada do CORE foi alterada.

## 2. Escopo implementado

Foi criado o pacote interno `cko.core.workspace`, sem reexportação por
`cko.core`, com os seguintes componentes:

- `RuntimePaths`: centralização imutável de todos os caminhos operacionais;
- `WorkspaceManager`: localização, criação, consulta, validação de permissões e
  acesso à limpeza;
- `TemporaryFileManager`: descoberta e remoção segura de artefatos temporários;
- `WorkspaceCleaner`: operações completas, isoladas e em modo dry-run;
- `EnvironmentValidator`: validação de Python, PowerShell, permissões, UTF-8 e
  espaço disponível;
- builder determinístico de wheel sem dependências externas;
- CLI interna baseada somente na biblioteca padrão.

## 3. Estrutura canônica do runtime

A árvore abaixo é criada automaticamente e de forma idempotente:

```text
runtime/
├── temp/
├── cache/
├── traces/
├── logs/
├── reports/
├── database/
└── snapshots/
```

Os caminhos são derivados de uma única configuração `RuntimePaths`. O projeto
pode ser localizado por um `pyproject.toml` ancestral ou por
`CKO_WORKSPACE_ROOT`.

## 4. Segurança e preservação

Toda remoção exige que o alvo resolvido:

- esteja estritamente abaixo da raiz do workspace;
- não seja a própria raiz;
- não escape da raiz por link simbólico;
- não seja nem esteja abaixo de um diretório permanente.

São protegidos, tanto na árvore canônica quanto nas equivalentes legadas da
raiz, `database`, `reports`, `snapshots` e `logs`.

A limpeza reconhece:

- `__pycache__`;
- `.pytest_cache`;
- `.cover`;
- arquivos `*.pyc` e `*.pyo`;
- conteúdo de `runtime/temp`, `runtime/cache` e `runtime/traces`;
- diretórios legados `temp`, `trace`, `.pytest_tmp`, `pytest_tmp`,
  `*_pytest_tmp` e `*_test_temp`.

Após qualquer limpeza, a árvore canônica é recriada, caso necessário.

## 5. Operações de limpeza

Foram implementadas as operações obrigatórias:

- `clean()`;
- `clean_temp()`;
- `clean_cache()`;
- `clean_trace()`;
- `clean_python_cache()`;
- `dry_run()`.

Cada operação retorna um `CleanResult` imutável com operação, candidatos,
itens removidos e indicação de dry-run.

## 6. Scripts de linha de comando

Foram criados e executados:

- `CKO_CLEAN.cmd` — limpeza completa, com suporte a `--dry-run`;
- `CKO_TESTS.cmd` — inicialização e pytest com cache desabilitado e temporários
  isolados em `runtime/temp/pytest`;
- `CKO_BUILD.cmd` — build determinístico de wheel em
  `runtime/reports/build`;
- `CKO_RUNTIME.cmd` — criação da árvore e validação completa do ambiente.

Todos usam `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src`,
preservam o código de saída e são compatíveis com `cmd.exe`, Windows 10/11 e
PowerShell 5.1.

O build não depende de `coverage.py`, `ruff`, `build` ou do backend
`setuptools.build_meta`. Os fontes Python são lidos em UTF-8, compilados em
memória para validação sintática e empacotados em um wheel puro com timestamps,
ordem e `RECORD` determinísticos.

Resultado do build real:

- artefato: `runtime/reports/build/cko-0.1.0-py3-none-any.whl`;
- conteúdo: 123 entradas;
- código de saída: 0.

## 7. Validação ambiental

`CKO_RUNTIME.cmd` foi executado no ambiente alvo e aprovou todos os requisitos:

| Verificação | Valor | Resultado |
|---|---|---|
| Python | 3.13.14 | Aprovado |
| PowerShell | 5.1.26100.8875 | Aprovado |
| Permissões | criar, gravar, ler e remover em `runtime/temp` | Aprovado |
| Encoding | UTF-8 | Aprovado |
| Espaço disponível | superior a 100 MiB | Aprovado |

O probe de permissão grava e relê o texto UTF-8 `CKO UTF-8: validação`, remove o
arquivo e não deixa resíduos.

## 8. Logging

Foram implementados e testados os eventos obrigatórios:

- `workspace_created`;
- `workspace_cleaned`;
- `cache_removed`;
- `trace_removed`;
- `validation_completed`.

O builder também registra `build_completed`. Todos os eventos usam o logging
estruturado existente e incluem contexto auditável.

## 9. Testes da SPR-008OA

Foi criado `tests/test_workspace_manager.py` com 18 testes cobrindo:

- criação e idempotência da árvore;
- centralização e descoberta de caminhos;
- validação de permissões e UTF-8;
- limpeza completa e operações isoladas;
- dry-run sem modificação;
- contenção dos alvos e proteção de dados permanentes;
- preservação de database, reports, snapshots e logs;
- logging obrigatório;
- validação positiva e negativa do ambiente;
- CLI de inicialização, validação, limpeza e build;
- execução e isolamento dos scripts `.cmd`;
- build de wheel válido e determinístico;
- docstrings, type hints, UTF-8 sem BOM, AST e limite PEP-8 de 99 colunas.

Resultado isolado final: **18 aprovados, 0 falhas**.

## 10. Cobertura

`coverage.py` não está instalado. Foi aplicada a metodologia homologada na
SPR-008O com `python -m trace --count --missing --summary` da biblioteca padrão.

| Módulo | Executadas | Executáveis | Cobertura |
|---|---:|---:|---:|
| `__init__.py` | 6 | 6 | 100,0% |
| `build.py` | 83 | 83 | 100,0% |
| `cleaner.py` | 166 | 173 | 96,0% |
| `cli.py` | 64 | 65 | 98,5% |
| `manager.py` | 63 | 71 | 88,7% |
| `paths.py` | 69 | 71 | 97,2% |
| `validator.py` | 98 | 103 | 95,1% |
| **Agregado** | **549** | **572** | **96,0%** |

A cobertura agregada supera o mínimo obrigatório de 90%.

## 11. Regressão oficial

A matriz oficial CORE-001 + SPR-008A até SPR-008O + SPR-008OA foi executada com
temporários isolados em `runtime/temp/pytest_regression`:

- **399 testes aprovados**;
- **0 falhas**;
- **0 erros**;
- tempo: 15,86 s.

Resultado oficial: **REGRESSÃO APROVADA**.

## 12. Verificação ampliada da suíte

Como verificação adicional, `CKO_TESTS.cmd -q` executou todos os testes presentes
em `tests`, inclusive legados fora da matriz oficial:

- 407 testes aprovados;
- duas falhas legadas fora do escopo da SPR-008OA.

Falhas observadas:

1. `tests/test_file_metadata.py::test_collect_metadata`: o teste legado fornece
   o argumento `calculate_hash`, inexistente na implementação antiga que ele
   importa;
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`:
   um handle SQLite legado permanece aberto e o Windows impede a exclusão de
   `cko.db` no teardown.

A segunda ocorrência já estava documentada no relatório homologado da
SPR-008O. Nenhuma das duas falhas importa `cko.core.workspace`. Elas não foram
alteradas, pois uma correção exigiria modificar API ou persistência, ações
expressamente proibidas nesta Sprint.

## 13. Arquivos criados

- `src/cko/core/workspace/__init__.py`;
- `src/cko/core/workspace/paths.py`;
- `src/cko/core/workspace/manager.py`;
- `src/cko/core/workspace/cleaner.py`;
- `src/cko/core/workspace/validator.py`;
- `src/cko/core/workspace/build.py`;
- `src/cko/core/workspace/cli.py`;
- `tests/test_workspace_manager.py`;
- `CKO_CLEAN.cmd`;
- `CKO_TESTS.cmd`;
- `CKO_BUILD.cmd`;
- `CKO_RUNTIME.cmd`;
- `SPR008OA_IMPLEMENTATION_REPORT.md`.

## 14. Arquivos funcionais preservados

Não foram alterados:

- Discovery;
- Query Optimizer;
- Planner e Cost-Based Planner;
- Execution Planner;
- Execution Engine;
- banco e persistência;
- regras de negócio;
- exports e APIs públicas do CORE.

## 15. Compatibilidade

A implementação usa somente recursos disponíveis no Python 3.13 e na
biblioteca padrão. Os scripts evitam sintaxe exclusiva de PowerShell moderno e
operam por `cmd.exe`, mantendo compatibilidade com Windows 10, Windows 11 e
PowerShell 5.1. Todos os arquivos de texto novos estão em UTF-8 sem BOM.

## 16. Declaração final

A infraestrutura canônica de desenvolvimento, runtime, testes, limpeza, build,
validação e logging da SPR-008OA foi implementada e verificada. A suíte isolada
foi aprovada em 18/18, a cobertura agregada atingiu 96,0%, o ambiente alvo foi
integralmente validado, o wheel foi gerado com sucesso e a regressão oficial foi
aprovada em 399/399.

A SPR-008OA está pronta para homologação formal. Nenhum trabalho referente à
SPR-008P foi iniciado.
