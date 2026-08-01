# SPR-008P — CKO CORE SDK — Canonical Execution Engine Foundation

## 1. Objetivo

Implementar a fundação canônica do Execution Engine para interpretar um
`ExecutionPlan` físico homologado na SPR-008O, validar sua integridade, percorrer
sua árvore em pré-ordem determinística, coordenar operadores lógicos e produzir um
`ExecutionResult` imutável.

O escopo foi mantido estritamente em memória. Nenhum banco, filesystem,
persistência, cache, conector, rede, thread, async, execução paralela ou regra de
negócio foi introduzido no Engine.

## 2. Arquitetura

O fluxo implementado é:

`ExecutionPlan` → `ExecutionEngine` → `ExecutionContext` →
`ExecutionEngineValidator` → `ExecutionPipeline` → operadores canônicos →
`ExecutionResult`.

O novo pacote público é `cko.core.execution`. Essa fronteira preserva os nomes
homologados `ExecutionContext`, `ExecutionPipeline`, `ExecutionMetrics` e
`ExecutionValidator` da SPR-008O em `cko.core.discovery` e na raiz `cko.core`.
Aliases explícitos do Engine foram adicionados na raiz: `EngineExecutionContext`,
`EngineExecutionPipeline` e `EngineExecutionMetrics`.

## 3. Engine

`ExecutionEngine`:

- recebe um `ExecutionPlan`;
- cria um identificador SHA-256 determinístico a partir do JSON canônico do plano;
- cria e valida o contexto;
- aplica as transições `CREATED → READY → RUNNING → COMPLETED`;
- delega a travessia ao pipeline;
- produz resultado e métricas imutáveis;
- registra sucesso ou falha de forma estruturada.

Para o mesmo plano e os mesmos metadados de entrada, o resultado, o JSON, a ordem
dos nós, as métricas lógicas e o `execution_id` são idênticos.

## 4. Pipeline

`ExecutionPipeline` percorre a árvore em pré-ordem, respeitando a ordem imutável da
tupla `children`. Cada objeto de nó é visitado no máximo uma vez. O pipeline:

- exige contexto em estado `RUNNING`;
- controla a `execution_stack`;
- detecta ciclo e reutilização indevida de objeto;
- resolve o operador pelo `ExecutionNodeType`;
- separa nós executados e ignorados;
- acumula warnings;
- calcula profundidade máxima;
- sempre restaura a pilha ao encerrar um nó, inclusive em falha.

## 5. Operadores

Foi criado o contrato abstrato `ExecutionOperator` e dez implementações canônicas:

1. `ScanOperator`;
2. `FilterOperator`;
3. `ProjectionOperator`;
4. `SortOperator`;
5. `LimitOperator`;
6. `IndexScanOperator`;
7. `CompositeIndexScanOperator`;
8. `PrefixScanOperator`;
9. `OrderedScanOperator`;
10. `RootOperator`.

O registro retornado por `canonical_operators()` é imutável e cobre os dez valores
de `ExecutionNodeType`. Os operadores apenas confirmam o contrato lógico do nó e
retornam `OperatorResult`; não acessam dados ou infraestrutura.

## 6. Estados

`ExecutionState` contém exatamente:

- `CREATED`;
- `READY`;
- `RUNNING`;
- `COMPLETED`;
- `FAILED`;
- `CANCELLED`.

As transições são explícitas e estados terminais não podem ser reabertos. Falhas
ocorridas após a criação do contexto levam ao estado `FAILED` antes do logging.

## 7. Validação

`ExecutionEngineValidator`, também exposto como `ExecutionValidator` dentro de
`cko.core.execution`, valida:

- o contrato físico completo por meio do `ExecutionPlanValidator` homologado;
- raiz, filhos, IDs, links de pai, aridade, estratégia e metadados do plano;
- ausência de ciclos e reutilização de objetos;
- estado inicial, pilha, metadados e estatísticas do contexto;
- chaves, tipos, propriedade e cobertura do registro de operadores;
- existência de operador compatível para todo nó alcançável.

## 8. Métricas

`ExecutionMetrics` é imutável e contém:

- `duration`, fixada em `0.0` como duração lógica determinística;
- `nodes_executed`;
- `maximum_depth`;
- `warnings`;
- `metadata` profundamente imutável.

As métricas identificam explicitamente `duration_kind=logical`, a versão do Engine
e o caráter determinístico da execução.

## 9. Logging

Foram implementados e testados os eventos estruturados obrigatórios:

- `execution_started`;
- `node_execution_started`;
- `node_execution_finished`;
- `execution_finished`;
- `execution_failed`.

Os eventos usam o logging canônico do SDK e incluem `execution_id`, `plan_id`,
identidade e tipo do nó quando aplicável.

## 10. Arquivos criados

- `src/cko/core/execution/__init__.py`;
- `src/cko/core/execution/engine.py`;
- `src/cko/core/execution/errors.py`;
- `src/cko/core/execution/models.py`;
- `src/cko/core/execution/operators.py`;
- `src/cko/core/execution/pipeline.py`;
- `src/cko/core/execution/validator.py`;
- `tests/test_execution_engine_spr008p.py`;
- `SPR008P_IMPLEMENTATION_REPORT.md`.

## 11. Arquivos alterados

- `src/cko/core/__init__.py` — exports aditivos e aliases explícitos do Engine.

Nenhum arquivo ou contrato homologado da SPR-008O/OA foi modificado.

## 12. Testes

A suíte `tests/test_execution_engine_spr008p.py` contém 22 testes e cobre:

- engine e determinismo;
- pipeline e pré-ordem;
- cinco estratégias de acesso físico;
- dez operadores canônicos e operadores customizados;
- seis estados e transições;
- contexto, pilha, metadados e estatísticas;
- resultado imutável e serialização estrita;
- validação positiva e negativa;
- skips, warnings e falhas de operador;
- logging de início, nós, término e falha;
- API pública e preservação dos nomes do Planner;
- type hints, docstrings, UTF-8 sem BOM, AST e PEP-8 de 99 colunas;
- ausência de imports de infraestrutura, filesystem, rede, threads e async.

Resultado isolado final: **22 aprovados, 0 falhas**.

## 13. Cobertura

`coverage.py` não está instalado. Foi usada a metodologia determinística da
biblioteca padrão, já homologada nas SPR-008O/OA:
`python -m trace --count --missing --summary`.

| Módulo | Executadas | Executáveis | Cobertura |
|---|---:|---:|---:|
| `__init__.py` | 8 | 8 | 100,0% |
| `engine.py` | 97 | 100 | 97,0% |
| `errors.py` | 12 | 12 | 100,0% |
| `models.py` | 267 | 280 | 95,4% |
| `operators.py` | 134 | 134 | 100,0% |
| `pipeline.py` | 94 | 100 | 94,0% |
| `validator.py` | 94 | 105 | 89,5% |
| **Agregado** | **706** | **739** | **95,5%** |

O mínimo agregado de 90% foi superado.

## 14. Regressão

A matriz oficial CORE-001 + SPR-008A até SPR-008P, incluindo SPR-008OA, foi
executada fora da restrição ambiental de escrita do sandbox:

- **419 testes aprovados**;
- **0 falhas funcionais**;
- **0 falhas arquiteturais**;
- **0 falhas ambientais na execução oficial**;
- **0 falhas legadas dentro da matriz oficial**.

Uma primeira execução no sandbox aprovou 403 testes e encontrou 12
`PermissionError` exclusivamente nos testes OA que gravam temporários sob o Google
Drive. A repetição idêntica fora da restrição aprovou todos os testes, classificando
essas ocorrências como ambientais e resolvidas.

A suíte ampliada `CKO_TESTS.cmd -q` também foi executada:

- 429 testes aprovados;
- duas falhas legadas fora da matriz oficial.

Falhas legadas preservadas:

1. `test_file_metadata.py::test_collect_metadata`: o teste chama o argumento
   antigo `calculate_hash`, ausente na implementação legada importada;
2. `test_persistence_spr005a.py::test_existing_table_is_preserved`: um handle
   SQLite legado aberto impede a remoção de `cko.db` no teardown do Windows.

As duas ocorrências já estavam registradas na SPR-008OA, não importam
`cko.core.execution` e não foram alteradas para preservar os contratos homologados
e a proibição de modificar filesystem/persistência nesta Sprint.

Resultado oficial da regressão solicitada: **APROVADA**.

## 15. Limitações

- A execução é lógica e coordenativa; operadores não materializam registros.
- A duração é uma métrica lógica determinística, não um benchmark de relógio.
- A árvore física atual é unária conforme a fundação homologada na SPR-008O.
- Não há cancelamento externo concorrente; `CANCELLED` existe no modelo de estado,
  sem introduzir threads ou async.
- Não há joins, graph, banco, filesystem, persistência, cache, rede, conectores ou
  execução paralela.
- As duas falhas da suíte legada ampliada permanecem fora do escopo.

## 16. Compatibilidade

A API pública permaneceu compatível. Todos os exports foram aditivos. Na raiz
`cko.core`, os símbolos homologados do Planner continuam apontando para
`cko.core.discovery.execution_models` e `execution_planner`. Os modelos homônimos
do Engine são acessíveis pelo pacote `cko.core.execution` e pelos aliases explícitos
`EngineExecutionContext`, `EngineExecutionPipeline` e
`EngineExecutionMetrics`.

A regressão oficial de 419 testes comprova a compatibilidade requerida.

## 17. Respostas obrigatórias

1. O Execution Engine foi implementado? **Sim.**
2. Existe pipeline de execução? **Sim, síncrono e determinístico.**
3. Existem operadores canônicos? **Sim, os dez operadores obrigatórios.**
4. Existe controle de estados? **Sim, com seis estados e transições validadas.**
5. Existe validação? **Sim, de plano, árvore, ciclos, contexto, estados,
   metadados, integridade e operadores.**
6. Existe ExecutionResult? **Sim, imutável, versionado e serializável.**
7. Existe execução determinística? **Sim, em pré-ordem e sem aleatoriedade.**
8. Existe banco? **Não no Execution Engine.**
9. Existe persistência? **Não no Execution Engine.**
10. Existe infraestrutura? **Não no Execution Engine.**
11. Existe execução paralela? **Não.**
12. A API pública permaneceu compatível? **Sim, com alterações apenas aditivas.**
13. A regressão SPR-008A–008P foi aprovada? **Sim, 419/419 testes.**
14. A cobertura mínima foi atingida? **Sim, 95,5% agregada.**
15. A SPR-008P pode ser homologada? **Sim, tecnicamente recomendada para
    homologação formal.**

## 18. Declaração final

A fundação canônica do Execution Engine foi implementada exclusivamente dentro do
namespace `cko.core`. O Engine valida e percorre o `ExecutionPlan` em pré-ordem
determinística, coordena dez operadores lógicos sem infraestrutura, controla o
ciclo de estados, impede ciclos, registra todos os eventos obrigatórios e produz
um `ExecutionResult` imutável e serializável.

A suíte isolada foi aprovada em 22/22, a cobertura agregada atingiu 95,5% e a
regressão oficial CORE-001/SPR-008A–008P foi aprovada em 419/419. A SPR-008P está
pronta para homologação formal. Nenhum trabalho referente à SPR-008Q foi iniciado.
