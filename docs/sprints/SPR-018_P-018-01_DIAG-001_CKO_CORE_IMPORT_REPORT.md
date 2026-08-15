# CKO — SPR-018 — P-018-01 DIAG-001 CKO.CORE Import Report

**Data:** 2026-08-13  
**Operação:** DIAG-001 — diagnóstico controlado do import de `cko.core` sob CPython 3.13  
**Veredito:** `DIAG-001 COMPLETE — P1-R17 REPLAY CAN BE REAUTHORIZED`

## A. Estado Git inicial

- Branch: `main`
- `HEAD`: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- `origin/main` local: `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- `origin/main` remoto (`git ls-remote`): `45d3bf87f9f01b663971b0dd6fa306aa207ab679`
- Baseline `CKO-BASELINE-2026.07^{}`: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
- Staging: vazio.
- Os arquivos não rastreados preexistentes foram preservados integralmente.

## B. Ambiente

- Executável exclusivo: `C:\Users\ANDRÉ\AppData\Local\CKO\cko-py313-validation\Scripts\python.exe`
- Runtime: CPython `3.13.15`, x64, Windows.
- O pacote `cko` não está instalado no venv (`pip show cko`: não encontrado). Para importar o source layout sem instalar ou alterar dependências, os processos diagnósticos receberam `PYTHONPATH=<repositório>\src` somente no ambiente do processo.
- Todos os processos foram executados com `-B`, impedindo escrita de bytecode.
- Nenhum pacote, runtime, venv, `PATH`, código, teste, requisito ou metadado de packaging foi alterado.

## C. Grafo imediato de imports

`src/cko/__init__.py` é vazio. `src/cko/core/__init__.py` importa e reexporta diretamente 21 subpacotes:

```text
cko.core
├── exceptions
├── config
├── identity
├── metadata
├── discovery
├── models
├── execution
├── runtime
├── connectors
├── storage
├── checkpoint
├── uow
├── composition
├── knowledge
├── documents
├── relationships
├── graph
├── query
├── index
├── corpus
└── provenance
```

O ramo mais largo é `discovery` (53 arquivos Python). `composition` amplia o grafo ao importar, entre outros, `inventory`, `workspace`, `storage.filesystem` e `storage.sqlite`. Assim, um único `import cko.core` carrega praticamente toda a superfície pública do Core.

## D. Efeitos em import-time encontrados

A análise AST dos 21 ramos diretos encontrou somente inicializações puras no nível de módulo: compilação de expressões regulares, criação de `frozenset`/`set`, constantes `UUID`, sentinelas `object`, `TypeVar` e obtenção de loggers (`get_logger`/`logging.getLogger`).

Há imports de módulos capazes de I/O (`pathlib`, `os`, `sqlite3`, filesystem storage e workspace), porém não foi encontrada execução de leitura/escrita de arquivos, abertura de SQLite, rede, subprocesso, thread, multiprocessing, lock, `sleep`, descoberta de plugins, migração ou scanning de recursos durante o import. Também não foi observado ciclo de import que impedisse conclusão.

## E. Tempos medidos

Cada medição ocorreu em processo Python independente, com limite de 30 s.

| Alvo | Tempos internos (s) | Tempos de parede (s) | Resultado |
|---|---:|---:|---|
| `import cko` | 0,006167; 0,009778; 0,007773 | 0,083850; 0,079756; 0,079294 | `IMPORT_OK` em 3/3 |
| `import cko.core` | 2,647260; 2,376552; 2,287312 | 2,789691; 2,513854; 2,401444 | `IMPORT_OK` em 3/3 |

Uma execução inicial adicional de `cko.core` terminou em 2,279122 s internos e 2,433690 s de parede. A execução instrumentada com `faulthandler` terminou em 2,252694 s.

## F. Resultado de `python -X importtime`

- `cko`: custo cumulativo observado de aproximadamente 7,8 ms no módulo.
- `cko.core`: custo cumulativo observado de 2.287.302 µs na terceira repetição.
- Maiores ramos cumulativos na terceira repetição: `cko.core.discovery` 577.553 µs; `cko.core.composition` 346.088 µs; `cko.core.composition.root` 228.683 µs; `cko.core.config` 164.212 µs; `cko.core.index` 118.298 µs; `cko.core.provenance` 113.253 µs.
- Maior custo próprio de módulo observado: `cko.core.index.models`, 30.605 µs. Em seguida: `cko.core.checkpoint.models`, 29.290 µs; `cko.core.models.asset`, 26.546 µs; `cko.core.discovery.execution_models`, 24.307 µs.
- Último módulo confirmado na árvore capturada antes da conclusão: `cko.core.provenance`, seguido da conclusão de `cko.core`.
- Não houve ponto de interrupção: todas as árvores terminaram com sucesso.

## G. Diagnóstico progressivo

O timeout não foi reproduzido. Portanto, a condição definida para decompor cada import direto em novos testes de timeout não ocorreu. A análise estática individual dos 21 ramos foi concluída; executar `import cko.core.<ramo>` em Python acionaria primeiro o mesmo `cko.core.__init__` e não reduziria mecanicamente o caminho já bem-sucedido.

## H. Stack diagnostic

`faulthandler.dump_traceback_later(1, repeat=True)` capturou duas stacks enquanto o import ainda progredia:

1. Aos 1 s: `importlib._bootstrap_external.get_data/get_code`, chamado por `cko.core.storage.factory` linha 9, via `cko.core.storage.__init__` e `cko.core.__init__` linha 296.
2. Aos 2 s: criação/carregamento de módulo em `importlib`, chamado por `cko.core.index.__init__` linha 23, via `cko.core.__init__` linha 888.

O processo concluiu em 2,252694 s. As stacks mostram leitura sequencial de módulos no filesystem, não espera em lock, rede, SQLite, thread ou subprocesso.

## I. Comparação entre runtimes

Não executada. Outro runtime não era necessário para localizar a causa operacional, e nenhum runtime adicional foi instalado ou configurado. Esta operação não constitui validação P1-R17.

## J. Causa provável

**Classificação:** `EXECUTOR_TIMEOUT_ARTIFACT`.

A evidência atual não reproduz o comportamento de 30 s: cinco imports completos de `cko.core` (quatro temporizados e um com stack dump) terminaram entre 2,25 s e 2,65 s internos. O import é relativamente amplo e realiza muitas leituras de pequenos módulos a partir de um workspace no Google Drive, mas permanece muito abaixo do limite. A stack confirma progresso normal em `importlib`. Logo, o timeout anterior foi provavelmente imposto/observado pelo executor da ENV-002C ou por latência transitória do ambiente, e não por deadlock ou defeito mecânico demonstrado no código.

`FILESYSTEM_OR_GOOGLE_DRIVE_LATENCY` é fator contribuinte plausível para a duração de aproximadamente 2,3 s, mas não explica, com a evidência atual, um bloqueio de 30 s.

## K. Relação causal com P-018-01

Busca mecânica em `src/cko/core` não encontrou referência a `external/fcp`, `tests/fcp` ou import de `external`. O grafo imediato e transitivo observado parte exclusivamente do Core. Os artefatos P-018-01 são externos/não rastreados e não são importados por `cko.core`.

`P_018_01_CAUSAL_RELATION: NO`

## L. Impacto sobre P1-R17

O bloqueio ambiental específico da ENV-002C não foi reproduzido. Há evidência suficiente para reautorizar um novo replay controlado de P1-R17, em operação separada, preservando o mesmo runtime e explicitando o source layout (`PYTHONPATH=src`) ou usando o artefato instalado previsto pelo replay. Este relatório não executou o replay.

## M. Recomendação técnica

1. Reautorizar P1-R17 em operação separada, com captura de stdout/stderr e limite explícito de pelo menos 30 s.
2. Registrar `sys.executable`, `sys.path`, `cko.__file__`, início/fim monotônicos e código de saída antes de interpretar timeout como deadlock.
3. Manter `faulthandler.dump_traceback_later` disponível no replay caso o processo ultrapasse 10 s.
4. Não alterar código, dependências ou ambiente com base neste diagnóstico.

## N. SHA-256 do relatório

`CANONICAL_SHA256: 6a53401201d8136f80cf5442a08e2a1ddd7edeaacfc450c4ae8db8475680405d`

Convenção verificável: SHA-256 UTF-8 do conteúdo completo deste arquivo com o valor hexadecimal acima substituído literalmente por `<SHA256>` e finais de linha LF. Essa convenção evita a impossibilidade matemática prática de um arquivo conter o próprio digest final sem normalização.

## O. Estado final do repositório

- Branch e SHAs permanecem iguais ao preflight.
- Staging permanece vazio.
- Nenhum arquivo preexistente foi modificado.
- Único arquivo criado por DIAG-001: `docs/sprints/SPR-018_P-018-01_DIAG-001_CKO_CORE_IMPORT_REPORT.md`.
- Todos os arquivos não rastreados preexistentes foram preservados.

## Resultados obrigatórios

`CKO_ROOT_IMPORT: IMPORT_OK`  
`CKO_CORE_IMPORT: IMPORT_OK`  
`CKO_CORE_IMPORT_DURATION: 2.252694–2.647260 s internos; 2.401444–2.789691 s de parede nas três repetições formais`  
`LAST_CONFIRMED_IMPORT: cko.core.provenance; depois cko.core concluiu`  
`SLOWEST_IMPORT: cko.core.discovery (577.553 µs cumulativos); cko.core.index.models (30.605 µs próprios)`  
`IMPORT_TIMEOUT_REPRODUCED: NO`  
`STACK_CAPTURED: YES`  
`ROOT_CAUSE_CLASSIFICATION: EXECUTOR_TIMEOUT_ARTIFACT`  
`P_018_01_CAUSAL_RELATION: NO`  
`PROJECT_CODE_CHANGE_REQUIRED: NO`  
`DEPENDENCY_CHANGE_REQUIRED: NO`  
`ENVIRONMENT_CHANGE_REQUIRED: NO`  
`P1_R17_REPLAY_RECOMMENDED: YES`  
`P_018_02_AUTHORIZED: NO`

## Veredito

`DIAG-001 COMPLETE — P1-R17 REPLAY CAN BE REAUTHORIZED`
