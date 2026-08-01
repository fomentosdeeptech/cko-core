# SPR-008O — CKO CORE SDK — Canonical Execution Planner Foundation

## 1. Objetivo

Implementar a fundação canônica do Execution Planner da Plataforma CKO para
transformar um `QueryExecutionPlan` em um `ExecutionPlan` físico, determinístico,
imutável, serializável e auditável.

A implementação produz somente uma descrição física. Nenhuma consulta é
executada e nenhum banco, filesystem, persistência, rede, thread, API ou
infraestrutura é utilizado pelo código da SPR-008O.

## 2. Arquitetura

O fluxo implementado é:

`QueryExecutionPlan` → `ExecutionContext` → `ExecutionPipeline` → árvore física →
`ExecutionPlanValidator` → `ExecutionPlan`.

O plano incorpora, em metadados profundamente imutáveis, o contexto, o relatório
e as métricas. Todo código novo está sob `cko.core.discovery`, dentro do namespace
exclusivo `cko.core`, e depende somente da biblioteca padrão e dos contratos
homologados nas SPR-008I a SPR-008N.

## 3. Pipeline

`ExecutionPipeline` aceita um `ExecutionContext` ou diretamente um
`QueryExecutionPlan`. O pipeline:

- mapeia a estratégia lógica para o nó de acesso físico correspondente;
- inclui estágios de filtro, projeção, ordenação e limite quando declarados;
- gera IDs SHA-256 a partir do conteúdo canônico e da posição do nó;
- liga cada filho ao ID imutável do pai;
- herda o timestamp do `QueryExecutionPlan`;
- calcula relatório e métricas sem consultar relógio ou estado externo;
- valida o resultado antes de devolvê-lo.

Uma mesma entrada produz igualdade estrutural, JSON idêntico e o mesmo `plan_id`.

## 4. Nós

Foram implementados os dez nós canônicos imutáveis:

1. `ScanNode`;
2. `IndexScanNode`;
3. `CompositeIndexScanNode`;
4. `PrefixScanNode`;
5. `OrderedScanNode`;
6. `FilterNode`;
7. `ProjectionNode`;
8. `SortNode`;
9. `LimitNode`;
10. `RootNode`.

`ExecutionNode` é o modelo abstrato comum e contém `node_id`, `node_type`,
`parent`, `children`, `metadata` e `schema_version`. O campo `parent` contém o ID
do pai, evitando referências reversas cíclicas em modelos imutáveis.

## 5. Árvore

A árvore é unária nesta fundação. Sua ordem externa canônica é:

`Root → Limit → Sort → Projection → Filter → Scan`.

Estágios sem declaração lógica são omitidos. O nó de acesso é sempre folha e
assume uma das cinco formas de scan conforme `QueryExecutionStrategy`. Existe um
único `RootNode`, sem pai, e todos os demais nós são alcançáveis a partir dele.

## 6. Validação

`ExecutionPlanValidator`, também exposto pelo nome compatível
`ExecutionValidator`, verifica:

- tipo e schema do plano;
- raiz única e sem pai;
- filhos canônicos;
- links de pai íntegros;
- IDs únicos;
- ausência de ciclos;
- ausência estrutural de órfãos;
- aridade dos nós físicos;
- existência de um único nó de acesso;
- compatibilidade entre nó de acesso e estratégia;
- metadados obrigatórios;
- coerência da árvore com relatório e métricas.

## 7. Métricas

`ExecutionMetrics` registra:

- `planning_duration` lógica e determinística (`0.0`);
- quantidade de nós criados;
- profundidade máxima;
- score de planejamento, derivado da confiança homologada do plano de entrada;
- metadados de determinismo e rastreabilidade.

## 8. Logging

Foram implementados os eventos estruturados obrigatórios:

- `execution_planning_started`;
- `node_created`;
- `validation_started`;
- `validation_finished`;
- `execution_planning_finished`.

Os eventos usam o logging canônico da SDK e não dependem de infraestrutura.

## 9. Arquivos criados

- `src/cko/core/discovery/execution_errors.py`;
- `src/cko/core/discovery/execution_models.py`;
- `src/cko/core/discovery/execution_planner.py`;
- `tests/test_execution_planner_spr008o.py`;
- `SPR008O_IMPLEMENTATION_REPORT.md`.

## 10. Arquivos alterados

- `src/cko/core/discovery/__init__.py` — exports públicos da SPR-008O;
- `src/cko/core/__init__.py` — exports públicos da raiz do CORE SDK.

As alterações de API são exclusivamente aditivas. Nenhum contrato anterior foi
removido ou modificado.

## 11. Testes

A suíte `tests/test_execution_planner_spr008o.py` contém 18 testes e cobre:

- modelos e dez nós canônicos;
- cinco estratégias de acesso;
- árvore completa e links de pai;
- pipeline e alias `plan`;
- determinismo byte a byte;
- validação positiva e negativa;
- serialização recursiva estrita;
- imutabilidade profunda;
- relatório e métricas;
- logging obrigatório;
- erros e envelopes inválidos;
- exports públicos, type hints e docstrings;
- UTF-8 sem BOM e PEP-8;
- ausência de imports de infraestrutura.

Resultado isolado final: **18 aprovados, 0 falhas**.

## 12. Cobertura

`coverage.py` não está instalado. Foi utilizada a metodologia determinística da
biblioteca padrão com `python -m trace --count --missing --summary`, conforme
autorizado. Os contadores foram emitidos fora do projeto.

| Módulo | Executadas | Executáveis | Cobertura |
|---|---:|---:|---:|
| `execution_errors.py` | 10 | 10 | 100,0% |
| `execution_models.py` | 358 | 381 | 94,0% |
| `execution_planner.py` | 236 | 256 | 92,2% |
| **Agregado** | **604** | **647** | **93,4%** |

O mínimo de 90% foi atingido no agregado e em cada módulo novo.

## 13. Regressão

A matriz canônica CORE-001/SPR-008A a SPR-008O foi executada em conjunto após a
implementação final:

- **379 testes aprovados**;
- **0 falhas funcionais**;
- **0 falhas arquiteturais**;
- **0 falhas ambientais na matriz A–O**;
- **0 falhas legadas na matriz A–O**.

Resultado oficial da regressão solicitada: **APROVADA**.

A pasta `tests` completa também foi executada como verificação adicional. Com o
TEMP padrão, houve **386 aprovações, uma falha legada e quatro erros ambientais**:

- falha legada: handle SQLite aberto impede a remoção de `cko.db` no teardown;
- erros ambientais: o sandbox recusou acesso ao diretório temporário padrão do
  pytest para testes legados de filesystem e migração.

Uma nova tentativa com diretório temporário controlado continuou sujeita às
restrições de escrita herdadas desses testes. Nenhuma dessas ocorrências pertence
à matriz A–O ou importa os módulos da SPR-008O.

## 14. Limitações

- A fundação descreve uma árvore unária; joins e execução paralela não pertencem
  a esta Sprint.
- `SortNode` permanece explícito quando há ordenação, inclusive com acesso
  ordenado, preservando a intenção física auditável desta fundação.
- A duração de planejamento é lógica, não um benchmark dependente de máquina.
- O score usa a confiança homologada do `QueryExecutionPlan`.
- `coverage.py` não está disponível; foi utilizada a biblioteca padrão.
- A suíte legada ampla depende de filesystem e SQLite e encontrou restrições
  ambientais fora do escopo desta Sprint.
- Não existe execução, banco, persistência, cache, rede, API ou infraestrutura no
  Execution Planner.

## 15. Compatibilidade

A API pública permaneceu compatível. Os exports foram somente estendidos em
`cko.core.discovery` e `cko.core`. `QueryPlan`, `OptimizationResult`,
`QueryExecutionPlan`, o Query Optimizer, o Cost-Based Planner e todos os contratos
homologados das SPR-008A a SPR-008N permaneceram inalterados.

A regressão conjunta de 379 testes comprova a compatibilidade requerida.

## 16. Respostas obrigatórias

1. O Execution Planner foi implementado? **Sim.**
2. Existe árvore física? **Sim, imutável, determinística e serializável.**
3. Existem nós canônicos? **Sim, os dez nós obrigatórios.**
4. Existe validação? **Sim, estrutural, de ciclos, raiz, filhos, metadados,
   estratégia e integridade.**
5. Existe pipeline? **Sim, com construção e validação determinísticas.**
6. Existe relatório? **Sim, imutável e incorporado ao plano.**
7. Existe execução da consulta? **Não.**
8. Existe banco? **Não no Execution Planner.**
9. Existe persistência? **Não no Execution Planner.**
10. Existe infraestrutura? **Não no Execution Planner.**
11. A API pública permaneceu compatível? **Sim.**
12. A regressão SPR-008A–008O foi aprovada? **Sim, 379/379 testes.**
13. A cobertura mínima foi atingida? **Sim, 93,4% agregada e acima de 90% por
    módulo.**
14. A SPR-008O pode ser homologada? **Sim, tecnicamente recomendada para
    homologação formal.**

## 17. Declaração final

A fundação canônica do Execution Planner foi implementada exclusivamente dentro
de `cko.core`, sem infraestrutura, sem banco, sem persistência e sem execução de
consultas. O pipeline produz uma árvore física determinística, imutável,
serializável e auditável, com dez nós canônicos, validação estrutural, relatório,
métricas e logging completo.

A suíte isolada foi aprovada em 18/18, a cobertura atingiu 93,4% e a regressão
CORE-001/SPR-008A–008O foi aprovada em 379/379. A SPR-008O está pronta para
homologação formal. Nenhum trabalho referente à SPR-008P foi iniciado.
