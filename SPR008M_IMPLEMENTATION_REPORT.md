# SPR-008M — CKO CORE SDK — Cost-Based Query Planner Foundation

## 1. Objetivo

Implementar a fundação canônica do Cost-Based Query Planner da CKO para escolher,
de forma determinística, auditável e reproduzível, uma estratégia lógica para um
`QueryPlan`. A implementação apenas planeja: não otimiza, não reescreve e não
executa consultas.

## 2. Arquitetura

O fluxo implementado respeita a Baseline Arquitetural 1.0:

`QueryPlan` → `LogicalIndex`/`LogicalIndexResolver` → `LogicalStatistics` →
`CostEstimator` → `CostBasedPlanner` → `QueryExecutionPlan`.

Todo código novo está sob `cko.core.discovery`, portanto dentro do namespace
exclusivo `cko.core`. A solução é somente em memória e depende apenas da
biblioteca padrão e dos contratos homologados nas SPR-008I, SPR-008K e SPR-008L.

## 3. Estratégias

Foi criado o enum público `QueryExecutionStrategy` com:

- `FULL_SCAN`;
- `INDEX_SCAN`;
- `COMPOSITE_INDEX_SCAN`;
- `PREFIX_INDEX_SCAN`;
- `ORDERED_INDEX_SCAN`.

Índices hash, compostos, de prefixo e ordenados são convertidos nas estratégias
correspondentes. `FULL_SCAN` é um candidato explícito e controlado pela política.

## 4. Modelos

Foram implementados modelos imutáveis, com `slots`, validação profunda, JSON
determinístico e envelope estrito versionado por `PLANNER_SCHEMA_VERSION = "1.0"`:

- `QueryExecutionPlan`;
- `PlannerDecision`;
- `PlannerPolicy`;
- `PlannerWeights`;
- `PlannerReport`;
- `PlannerMetrics`.

`QueryExecutionPlan` contém `plan_id`, `query_plan`, `execution_strategy`,
`selected_indexes`, custo, linhas, seletividade, confiança, tempo lógico de
planejamento, versão do planner, timestamp, metadados auditáveis e schema.

## 5. Políticas

`PlannerPolicy` controla:

- custo máximo aceitável;
- confiança mínima;
- permissão de full scan;
- permissão de múltiplos índices;
- limite de índices selecionados;
- estratégia padrão de desempate;
- pesos de decisão.

O `PlannerValidator` reaplica essas regras ao plano final e verifica estratégia,
custo, confiança, disponibilidade de índices e coerência do material de auditoria.

## 6. Pesos

`PlannerWeights` define pesos independentes para seletividade, cardinalidade,
custo, cobertura, densidade e confiança. O score é normalizado pela soma dos
pesos; ao menos um peso deve ser positivo.

## 7. Planejamento

`CostBasedPlanner.plan()` recebe exatamente `QueryPlan`, `LogicalStatistics` e
uma coleção de `LogicalIndex`. Todos os insumos são validados antes da análise.

Cada candidato considera obrigatoriamente:

- seletividade e cardinalidade estimadas pelo `CostEstimator` homologado;
- cobertura de filtros;
- cobertura da ordenação;
- cobertura da projeção;
- custo estimado;
- densidade do índice;
- confiança estatística.

O `plan_id` é derivado por SHA-256 dos insumos canônicos, política, versão e
decisão. O tempo lógico registrado é `0.0`, deliberadamente independente da
máquina, e não participa da decisão.

## 8. Decisão

Os candidatos elegíveis são ordenados por:

1. maior score ponderado;
2. preferência explícita da estratégia padrão;
3. menor custo;
4. nome canônico da estratégia;
5. IDs ordenados dos índices.

Não existe aleatoriedade. A ordem de entrada dos índices não altera o resultado.
`PlannerDecision` registra justificativa, estratégias e índices descartados,
confiança, ganho estimado e timestamp.

## 9. Métricas

`PlannerMetrics` registra duração lógica, índices avaliados, estratégias avaliadas,
total de candidatos, candidato escolhido e candidatos descartados. As métricas
ficam incorporadas aos metadados imutáveis do `QueryExecutionPlan`.

## 10. Validação

`PlannerValidator` valida:

- correspondência entre estratégia e índices;
- custo e confiança contra a política;
- limite e disponibilidade dos índices;
- regra de múltiplos índices;
- coerência entre plano, decisão, relatório e métricas.

Também está disponível `is_valid()` para verificação booleana sem ocultar erros no
método estrito `validate()`.

## 11. Logging

Foram adicionados eventos estruturados para:

- `planning_started` — início;
- `analysis_completed` — análise;
- `comparison_completed` — comparação;
- `decision_completed` — decisão;
- `planning_completed` — conclusão.

Os eventos usam o logging canônico da SDK e não registram infraestrutura externa.

## 12. Arquivos criados

- `src/cko/core/discovery/planner_errors.py`;
- `src/cko/core/discovery/planner_models.py`;
- `src/cko/core/discovery/planner.py`;
- `tests/test_cost_based_planner_spr008m.py`;
- `reports/spr008m_trace/.gitkeep`;
- `SPR008M_IMPLEMENTATION_REPORT.md`.

## 13. Arquivos alterados

- `src/cko/core/discovery/__init__.py` — API pública de Discovery;
- `src/cko/core/__init__.py` — API pública raiz do CORE SDK.

Nenhum contrato homologado foi alterado; apenas novos símbolos foram exportados.

## 14. Testes

A suíte `tests/test_cost_based_planner_spr008m.py` possui 26 testes e cobre:

- modelos, imutabilidade, serialização e schema;
- estratégias, pesos, políticas e métricas;
- decisão, validação, desempate e planejamento;
- full scan e múltiplos índices;
- logging, type hints, docstrings, UTF-8 e PEP-8;
- ausência de dependências de infraestrutura;
- erros e envelopes inválidos.

Resultado isolado: **26 aprovados, 0 falhas**.

## 15. Cobertura

`coverage.py` não está instalado. Foi aplicada a metodologia determinística da
biblioteca padrão com `python -m trace --count --summary --missing`:

| Módulo | Linhas executáveis | Cobertura |
|---|---:|---:|
| `planner.py` | 412 | 94% |
| `planner_errors.py` | 10 | 100% |
| `planner_models.py` | 391 | 91% |

Cobertura agregada aproximada dos módulos novos: **92,6%**. O mínimo de 90% foi
atingido. A execução instrumentada também aprovou os 26 testes.

O Google Drive recusou arquivos `.cover` dentro de `reports/`; a coleta final foi
feita no diretório temporário local autorizado. Trata-se somente de uma limitação
ambiental de emissão do artefato, sem perda dos contadores exibidos pelo `trace`.

## 16. Regressão

Foram executadas conjuntamente as suítes SPR-008A a SPR-008M:

- **336 testes aprovados**;
- **0 falhas funcionais**;
- **0 falhas arquiteturais**;
- **0 falhas legadas**;
- **1 ocorrência ambiental não bloqueante**: criação de bytecode/arquivos
  `.cover` recusada em pastas sincronizadas do Google Drive. Os testes foram
  executados com bytecode desativado e a cobertura foi emitida em diretório
  temporário local.

Resultado final da regressão: **APROVADA**.

## 17. Limitações

- Os custos são estimativas lógicas relativas, não benchmarks de infraestrutura.
- O planner não coleta estatísticas; consome `LogicalStatistics` homologadas.
- O tempo de planejamento é uma métrica lógica determinística (`0.0`) nesta
  fundação, não uma medição de desempenho da máquina.
- Não há execução, otimização, reescrita ou persistência.
- Nenhum trabalho da SPR-008N foi iniciado.

## 18. Compatibilidade

A API pública anterior foi preservada. Os exports foram somente estendidos em
`cko.core.discovery` e `cko.core`. A regressão integral A–M comprova compatibilidade
com CORE-001 e SPR-008A a SPR-008L.

## 19. Respostas obrigatórias

1. O Cost-Based Planner foi implementado? **Sim.**
2. Existe planejamento determinístico? **Sim.**
3. Existe decisão reproduzível? **Sim.**
4. Existe estratégia de execução? **Sim, lógica e não executada.**
5. Existe PlannerPolicy? **Sim.**
6. Existe PlannerWeights? **Sim.**
7. Existe PlannerMetrics? **Sim.**
8. Existe Query Optimizer? **Não.**
9. Existe reescrita de consultas? **Não.**
10. Existe execução da consulta? **Não.**
11. Existe banco? **Não.**
12. Existe filesystem? **Não no código do planner.**
13. Existe persistência? **Não.**
14. A API pública permaneceu compatível? **Sim.**
15. A regressão SPR-008A–008M foi aprovada? **Sim, 336/336 testes.**
16. A cobertura mínima foi atingida? **Sim, aproximadamente 92,6%.**
17. A SPR-008M pode ser homologada? **Sim, tecnicamente recomendada para
    homologação formal.**

## 20. Declaração final

A fundação canônica do Cost-Based Query Planner foi implementada exclusivamente
em `cko.core`, sem infraestrutura e sem execução de consultas. A decisão é
determinística, reproduzível, validada e auditável. A regressão SPR-008A–008M foi
aprovada e a cobertura mínima foi superada. A SPR-008M está pronta para
homologação formal. Nenhum trabalho referente à SPR-008N foi iniciado.
