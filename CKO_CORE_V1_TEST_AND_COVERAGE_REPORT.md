# CKO CORE v1 — Relatório de testes e cobertura

## Ambiente

Windows nativo; Python 3.13.14; PowerShell 5.1.26100.8894; UTF-8; `PYTHONDONTWRITEBYTECODE=1`; `PYTHONPATH=src`; temporários canônicos em `runtime/temp`. `coverage.py` não está instalado (`No module named coverage`); nenhuma dependência foi instalada.

## Execuções válidas

| Comando | Escopo | Resultado | Duração |
|---|---|---|---:|
| `cmd /c CKO_TESTS.cmd -q` | regressão integral | 686 passed, 2 failed, 0 skipped | 30,99 s |
| `cmd /c CKO_TESTS.cmd tests\test_filesystem_storage_connector_spr008t.py -q` | T | 29 passed | 4,31 s |
| `cmd /c CKO_TESTS.cmd tests\test_sqlite_storage_adapter_spr008u.py -q` | U | 28 passed | 3,46 s |
| `cmd /c CKO_TESTS.cmd tests\test_checkpoint_foundation_spr008v.py -q` | V | 31 passed | 3,45 s |
| `cmd /c CKO_TESTS.cmd tests\test_unit_of_work_foundation_spr008w.py -q` | W | 26 passed | 1,14 s |
| `cmd /c CKO_RUNTIME.cmd` | ambiente | 5/5 checks | 2,7 s |
| `cmd /c CKO_CLEAN.cmd --dry-run` | limpeza segura | 36 candidatos, nada removido | 24,8 s |

As suítes A–S e OA integram as 686 aprovações da regressão. A soma de funções de teste por busca textual é menor que 688 porque parametrização gera casos adicionais; a contagem oficial é a coletada pelo pytest.

## Falhas legadas verificadas

1. `tests/test_file_metadata.py::test_collect_metadata`: `collect_metadata(sample, calculate_hash=True)` resulta em `TypeError` porque `src/cko/metadata/file_metadata.py` não aceita o argumento. Estado: **idêntica e não resolvida**.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`: `tempfile.TemporaryDirectory.cleanup()` recebe `WinError 32` para `cko.db`, mantido aberto pelo código legado. Estado: **idêntica e não resolvida**.

Nenhuma falha nova foi encontrada na execução canônica. As duas ocorrências são fora de `cko.core` e já constavam da ARCH v1.1 e dos relatórios R–W.

## Execuções inválidas e diagnóstico

Tentativas de rodar `trace` sobre toda a suíte e de executar validação/workspace em paralelo com tests causaram falhas de escrita SQLite/Filesystem e perda dos `.cover` sob `runtime/temp`. Execuções diretas no sandbox também receberam `WinError 5` em arquivos do Google Drive. As mesmas suítes passaram serialmente pelo `CKO_TESTS.cmd`; portanto essas ocorrências são limitações ambientais/metodológicas, não regressões. Elas evidenciam, porém, que o workspace não suporta duas execuções usando o mesmo `runtime/temp` — risco P2.

## Cobertura disponível

As medições abaixo foram produzidas com `trace` da stdlib nos relatórios homologados de cada Sprint e suas suítes dedicadas. Elas são comparáveis dentro de cada entrega, mas não podem ser somadas em um percentual global porque possuem denominadores, escopos e momentos diferentes.

| Entrega/família | Cobertura registrada |
|---|---:|
| Inventory C | 99,37% |
| Provider E | 91,68% |
| Capability H | ≈91,6% |
| Query I | 94,50% |
| Evaluation J | 90,04% |
| Index K | 91,96% |
| Statistics L | 92,06% |
| Planner M | ≈92,6% |
| Optimizer N | 93,9% |
| Execution Planner O | 93,4% |
| Connector R | 96% |
| Storage S | 96% |
| Filesystem T | 92,85% |
| SQLite U | 92,63% |
| Checkpoint V | 94,13% |
| UoW W | 100% |

**Cobertura consolidada agregada:** indisponível de modo metodologicamente válido no ambiente atual. Declarar uma média desses percentuais seria incorreto. A evidência disponível demonstra >90% por entrega, não >90% por cada módulo nem por todo o wheel. Esta limitação é uma ressalva P2 do gate.

## Módulos abaixo de 90%

| Módulo | Evidência | Cobertura |
|---|---|---:|
| `discovery/query_evaluation_models.py` | SPR008J | 87,86% |
| `workspace/manager.py` | SPR008OA | 88,7% |
| `execution/validator.py` | SPR008P | 89,5% |
| `runtime/validator.py` | SPR008Q | 89,1% |
| `storage/filesystem/session.py` | SPR008T | 87% |
| `storage/sqlite/session.py` | SPR008U | 86,74% |
| `checkpoint/serializer.py` | SPR008V | 87,84% |

Os caminhos críticos mais relevantes não totalmente exercitados são ramos de sessão/rollback/erro, versões/inputs inválidos de modelos de evaluation, validação de execução/runtime e falhas de serialização de Checkpoint. APIs públicas UoW tiveram 100% na metodologia da Sprint.

## Build e repetibilidade

`CKO_BUILD.cmd` foi executado duas vezes. Ambas geraram `runtime/reports/build/cko-0.1.0-py3-none-any.whl`, 184 entradas, incluindo 150 módulos CORE. SHA-256 nas duas execuções: `A03F566116013678A9D2B53FC11F3BF21AA7772A37B58CB758E24565A143AFE5`. Todos os timestamps ZIP são `1980-01-01 00:00:00`; não há path absoluto ou `..`. METADATA: pacote `cko`, versão `0.1.0`, Python `>=3.13`, sem dependências declaradas.

## Conclusão

A regressão funcional é estável com duas falhas legadas conhecidas. Cobertura por entrega é forte, mas o gate mantém ressalva porque sete módulos ficam abaixo de 90% e não existe corrida agregada confiável. Recomenda-se adicionar uma configuração de cobertura canônica e isolamento por execução, sem instalar ferramenta durante esta Sprint.
