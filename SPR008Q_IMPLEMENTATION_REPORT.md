# SPR-008Q — CKO CORE SDK — Canonical Runtime Foundation

## 1. Objetivo

Implementar a fundação canônica do Runtime do CKO CORE SDK para coordenar, em
memória, o ciclo de vida de uma execução física homologada. O Runtime recebe um
`ExecutionPlan`, prepara contexto e sessão, controla estados e recursos lógicos,
coordena o `ExecutionEngine` da SPR-008P e produz métricas e relatório.

O Runtime não executa operadores, não acessa dados e não introduz banco,
filesystem, persistência, cache externo, rede, conectores, threads ou async.

## 2. Arquitetura

O fluxo implementado é:

`ExecutionPlan` → `Runtime` → `ExecutionEngine` → `ExecutionResult`.

O pacote público novo é `cko.core.runtime`, integralmente dentro do namespace
autorizado. O Runtime usa composição para coordenar o `ExecutionEngine`; a execução
dos operadores permanece responsabilidade exclusiva do Engine homologado.

Os componentes são independentes de infraestrutura externa e trocam apenas
objetos em memória, modelos imutáveis de saída e snapshots serializáveis.

## 3. Runtime

`Runtime` implementa:

- criação de identidade de runtime e sessão;
- vinculação e inicialização de um `ExecutionPlan`;
- preparação, início, finalização, pausa lógica, retomada e cancelamento;
- coordenação síncrona do `ExecutionEngine`;
- controle de estado, métricas e recursos lógicos;
- retenção do `ExecutionResult` produzido pelo Engine;
- geração de sessão e relatório por snapshot;
- emissão dos eventos estruturados obrigatórios.

Os métodos `start()` e `execute()` são equivalentes. Uma instância coordena um
único ciclo terminal, evitando a reabertura de execuções concluídas, falhas ou
canceladas.

## 4. Sessão

`RuntimeSession` contém:

- `session_id`;
- referência lógica `runtime` por `runtime_id`;
- snapshot de `RuntimeContext`;
- snapshot de `RuntimeMetrics`;
- metadata profundamente imutável.

A sessão possui serialização JSON determinística, versionada, sem dependência de
persistência. O snapshot impede que alterações posteriores no Runtime modifiquem
retroativamente um relatório já emitido.

## 5. Ciclo de vida

`RuntimeState` contém exatamente os oito estados obrigatórios:

- `CREATED`;
- `INITIALIZED`;
- `READY`;
- `RUNNING`;
- `PAUSED`;
- `COMPLETED`;
- `FAILED`;
- `CANCELLED`.

`LifecycleController` mantém o grafo explícito de transições. Estados terminais
não podem ser reabertos. A pausa e a retomada são pontos cooperativos lógicos; não
há concorrência, thread ou tarefa assíncrona.

## 6. Recursos

`ResourceRegistry` registra somente recursos lógicos representados por valores
serializáveis em memória. O registro:

- normaliza e valida nomes;
- impede duplicidade;
- congela mappings e sequências profundamente;
- rejeita objetos externos ou não serializáveis;
- oferece consulta, remoção, snapshot imutável e liberação total.

Nenhum handle, arquivo, conexão, socket ou recurso externo é adquirido.

## 7. Cancelamento

`CancellationToken` implementa cancelamento cooperativo, síncrono e idempotente.
O primeiro pedido registra a razão normalizada; pedidos posteriores não alteram o
estado. `throw_if_cancelled()` materializa `RuntimeCancellationError` no próximo
ponto cooperativo.

O Runtime pode ser cancelado desde `CREATED` até `PAUSED`, atualiza métricas,
finaliza a duração e emite relatório válido sem iniciar o Engine.

## 8. Validação

`RuntimeValidator` valida:

- estrutura e identidade do contexto;
- vínculo entre sessão e runtime;
- tipos e valores de estado;
- transições pelo `LifecycleController`;
- métricas da sessão;
- igualdade entre snapshot da sessão e contexto corrente;
- consistência entre contexto e `ResourceRegistry`;
- consistência entre estatísticas e métricas;
- integridade agregada por `validate_integrity()` e `is_valid()`.

Erros foram separados por domínio: modelo, lifecycle, validação, cancelamento e
registro de recursos.

## 9. Logging

Foram implementados e testados os eventos estruturados obrigatórios:

- `core.runtime.runtime_created`;
- `core.runtime.runtime_initialized`;
- `core.runtime.runtime_started`;
- `core.runtime.runtime_finished`;
- `core.runtime.runtime_cancelled`.

Os eventos usam o logging canônico do SDK e incluem as identidades e o estado
relevantes, sem gravar arquivos.

## 10. Arquivos criados

- `src/cko/core/runtime/__init__.py`;
- `src/cko/core/runtime/cancellation.py`;
- `src/cko/core/runtime/errors.py`;
- `src/cko/core/runtime/lifecycle.py`;
- `src/cko/core/runtime/models.py`;
- `src/cko/core/runtime/resources.py`;
- `src/cko/core/runtime/runtime.py`;
- `src/cko/core/runtime/validator.py`;
- `tests/test_runtime_spr008q.py`;
- `SPR008Q_IMPLEMENTATION_REPORT.md`.

## 11. Arquivos alterados

- `src/cko/core/__init__.py` — exports públicos exclusivamente aditivos.

O `CancellationToken` homologado de Discovery foi preservado na raiz. O token do
Runtime é exposto na raiz pelo alias inequívoco `RuntimeCancellationToken` e pelo
nome `CancellationToken` dentro de `cko.core.runtime`.

Nenhum módulo homologado das SPRs anteriores foi modificado.

## 12. Testes

A suíte `tests/test_runtime_spr008q.py` contém 17 testes e cobre:

- Runtime e coordenação do Engine;
- contexto e sessão;
- oito estados e transições válidas/inválidas;
- cancelamento cooperativo e idempotência;
- métricas e contadores terminais;
- recursos lógicos e rejeição de objetos externos;
- relatório, snapshots e serialização UTF-8;
- falha do Engine e transição para `FAILED`;
- cinco eventos obrigatórios de logging;
- validação individual e integridade agregada;
- preservação da API pública anterior;
- type hints, docstrings, UTF-8 sem BOM e PEP-8 de 99 colunas;
- ausência de imports de banco, filesystem, rede, threads e async.

Resultado isolado final: **17 aprovados, 0 falhas**.

## 13. Cobertura

`coverage.py` não está instalado. Foi usada a metodologia determinística da
biblioteca padrão homologada nas SPRs anteriores:
`python -m trace --count --missing --summary`.

| Módulo | Executadas | Executáveis | Cobertura |
|---|---:|---:|---:|
| `__init__.py` | 9 | 9 | 100,0% |
| `cancellation.py` | 33 | 33 | 100,0% |
| `errors.py` | 14 | 14 | 100,0% |
| `lifecycle.py` | 54 | 54 | 100,0% |
| `models.py` | 248 | 268 | 92,5% |
| `resources.py` | 59 | 60 | 98,3% |
| `runtime.py` | 206 | 211 | 97,6% |
| `validator.py` | 57 | 64 | 89,1% |
| **Agregado** | **680** | **713** | **95,4%** |

O mínimo agregado de 90% foi superado.

## 14. Regressão

A matriz oficial CORE-001 + SPR-008A até SPR-008Q, incluindo SPR-008OA, foi
executada com 438 casos:

- **438 testes aprovados**;
- **0 falhas funcionais**;
- **0 falhas arquiteturais**;
- **0 falhas ambientais na execução oficial fora do sandbox**;
- **0 falhas legadas dentro da matriz oficial**.

A primeira execução dentro do sandbox aprovou 426 testes e apresentou 12
`PermissionError` exclusivamente em testes homologados de Workspace que criam
temporários. A repetição da matriz idêntica fora da restrição aprovou 438/438,
classificando as 12 ocorrências como ambientais e resolvidas.

A suíte ampliada `CKO_TESTS.cmd -q` também foi executada:

- 446 testes aprovados;
- duas falhas legadas fora da matriz oficial.

Falhas legadas preservadas:

1. `test_file_metadata.py::test_collect_metadata`: o teste usa o argumento legado
   `calculate_hash`, ausente na assinatura atual da implementação legada;
2. `test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`:
   um handle SQLite legado aberto impede a remoção de `cko.db` no teardown do
   Windows.

As duas ocorrências são as mesmas registradas na SPR-008P, não importam
`cko.core.runtime` e não foram alteradas para preservar contratos homologados e o
limite de escopo da SPR-008Q.

Resultado oficial: **regressão aprovada**.

## 15. Limitações

- Cada instância de `Runtime` coordena um único ciclo terminal.
- Pausa, retomada e cancelamento são cooperativos; sem threads ou async, não há
  interrupção concorrente durante uma chamada síncrona já em andamento.
- `runtime_duration` mede tempo monotônico de coordenação, não benchmark do Engine.
- Recursos são descritores lógicos serializáveis, não handles externos.
- O Runtime não materializa dados e não executa operadores.
- Não há banco, filesystem, persistência, cache externo, Redis, Elastic, Lucene,
  FAISS, graph, network, conectores ou regras de negócio.
- As duas falhas da suíte legada ampliada permanecem fora do escopo oficial.

## 16. Compatibilidade

A API pública permaneceu compatível. Todas as alterações são aditivas e os
contratos homologados de CORE-001 e SPR-008A–008P/OA permanecem inalterados.

Em particular, `cko.core.CancellationToken` continua apontando para o contrato de
Discovery. O novo token é `cko.core.runtime.CancellationToken` e
`cko.core.RuntimeCancellationToken`. A regressão oficial de 438 testes comprova a
compatibilidade requerida.

## 17. Respostas obrigatórias

1. O Runtime foi implementado? **Sim.**
2. Existe RuntimeContext? **Sim.**
3. Existe RuntimeSession? **Sim.**
4. Existe LifecycleController? **Sim.**
5. Existe CancellationToken? **Sim, cooperativo, síncrono e idempotente.**
6. Existe ResourceRegistry? **Sim, exclusivamente para recursos lógicos.**
7. Existe RuntimeValidator? **Sim.**
8. Existe RuntimeReport? **Sim, versionado e serializável.**
9. Existe RuntimeMetrics? **Sim.**
10. Existe infraestrutura? **Não há infraestrutura externa no Runtime.**
11. Existe banco? **Não no Runtime.**
12. Existe persistência? **Não no Runtime.**
13. A API pública permaneceu compatível? **Sim, com alterações apenas aditivas.**
14. A regressão SPR-008A–008Q foi aprovada? **Sim, 438/438 na matriz oficial.**
15. A cobertura mínima foi atingida? **Sim, 95,4% agregada.**
16. A SPR-008Q pode ser homologada? **Sim, tecnicamente recomendada para
    homologação formal.**

## 18. Declaração final

A fundação canônica do Runtime foi implementada exclusivamente no namespace
`cko.core`. Ela coordena contexto, sessão, lifecycle, recursos lógicos,
cancelamento, métricas, validação, logging interno e o `ExecutionEngine` sem
executar operadores nem acessar infraestrutura.

A suíte isolada foi aprovada em 17/17, a cobertura agregada atingiu 95,4% e a
regressão oficial CORE-001/SPR-008A–008Q foi aprovada em 438/438. A SPR-008Q está
pronta para homologação formal. Nenhum trabalho referente à SPR-008R foi iniciado.
