# SPR-008L — Discovery Query Statistics & Cost Foundation

## 1. Objetivo

Implementar a fundação canônica, imutável e independente de infraestrutura para
estatísticas lógicas, histogramas em memória e estimativas de custo de consultas
Discovery. A implementação prepara o SDK para planejamento futuro baseado em custo,
sem introduzir otimizador ou Cost Based Planner.

## 2. Arquitetura

O fluxo implementado é estritamente aditivo:

`LogicalIndex → StatisticsBuilder → LogicalStatistics → CostEstimator`

Os componentes pertencem exclusivamente ao namespace `cko.core.discovery` e são
reexportados pela fachada `cko.core`. A entrada reutiliza os contratos homologados
`LogicalIndex` (SPR-008K) e `QueryPlan` (SPR-008I), sem alterá-los.

Não há adaptador, I/O, banco, filesystem, persistência, cache externo ou execução de
consulta no novo código.

## 3. Modelos

Foram implementados modelos congelados, versionados e serializáveis:

- `LogicalStatistics`;
- `AttributeStatistics`;
- `Histogram` e `HistogramBucket`;
- `CostEstimate`;
- `StatisticsPolicy`;
- `StatisticsReport`.

Todos usam schema `1.0`, envelope estrito, JSON determinístico, timestamps conscientes
de fuso e congelamento profundo de metadados.

## 4. Histogramas

`HistogramBuilder` constrói histogramas exclusivamente em memória para números,
strings e booleanos. Os buckets possuem identificador contíguo, intervalo, frequência
e frequência cumulativa. Há suporte a políticas `equal_width` e `equal_frequency`,
com limite configurável de buckets e ordenação determinística.

## 5. Estatísticas

As estatísticas incluem total de entradas, chaves distintas, nulos, duplicações,
densidade média, seletividade média, cardinalidade estimada, distribuição lógica,
estatísticas por atributo e referências aos histogramas construídos.

As fórmulas canônicas usadas são:

- densidade média: `chaves_distintas / total_de_entradas`;
- seletividade média: `1 / chaves_distintas`;
- cardinalidade média estimada: `round(total × seletividade)`;
- duplicações: `valores_não_nulos - valores_distintos`.

## 6. Builder

`StatisticsBuilder` recebe apenas um `LogicalIndex`, deriva as distribuições e não
muta a entrada. Quando não é fornecido timestamp explícito, utiliza deterministicamente
o maior timestamp das entradas do índice; para índice vazio utiliza o epoch UTC.

## 7. Validator

`StatisticsValidator` verifica:

- cardinalidade, densidade e seletividade;
- limites da política;
- coerência de nulos, distintos e duplicados por atributo;
- referências de histogramas;
- total de frequências;
- continuidade, ordenação e limite de buckets;
- frequência cumulativa.

## 8. Estimador de custo

`CostEstimator` recebe `QueryPlan` e `LogicalStatistics`. Ele estima seletividade,
linhas e custo lógico relativo sem executar a consulta. São considerados filtros
atômicos, grupos `AND`, `OR` e `NOT`, existência, igualdade, conjuntos, intervalos,
operações de string, projeção, ordenação e paginação.

A confiança reflete a proporção de expressões cobertas por estatísticas de atributo,
respeitando o piso definido na política. `report()` produz um `StatisticsReport`
auditável com as estatísticas e histogramas efetivamente referenciados.

## 9. Políticas

`StatisticsPolicy` define:

- máximo de buckets;
- granularidade;
- política de histograma;
- estratégia de estimativa (`density`, `histogram` ou `hybrid`);
- limites de entradas e confiança mínima.

As configurações são imutáveis, serializáveis e validadas na construção.

## 10. Logging

Foram adicionados eventos estruturados no logger oficial `cko` para:

- início e conclusão da construção;
- construção de histogramas;
- início e conclusão da validação;
- início e conclusão da estimativa;
- conclusão do fluxo.

O prefixo canônico é `discovery.query.statistics.*`.

## 11. Arquivos criados

- `src/cko/core/discovery/statistics_errors.py`;
- `src/cko/core/discovery/statistics_models.py`;
- `src/cko/core/discovery/statistics.py`;
- `tests/test_discovery_statistics_foundation_spr008l.py`;
- `SPR008L_IMPLEMENTATION_REPORT.md`.

## 12. Arquivos alterados

- `src/cko/core/discovery/__init__.py`: exportações públicas aditivas;
- `src/cko/core/__init__.py`: reexportações públicas aditivas.

Nenhum contrato anterior foi removido ou modificado.

## 13. Testes

A suíte exclusiva SPR-008L contém 32 testes e foi aprovada integralmente:

```text
32 passed in 2.37s
```

Ela cobre imutabilidade, serialização, schema, histogramas, buckets, cardinalidade,
seletividade, estatísticas, custo, validação, políticas, logging, type hints,
docstrings, UTF-8, PEP 8 e ausência de infraestrutura proibida.

## 14. Cobertura

`coverage.py` não está instalado no ambiente. Foi aplicada a metodologia determinística
prevista no termo, usando `trace._find_executable_linenos` e contagem de execução da
biblioteca padrão do Python 3.13.

```text
statistics_errors.py:  7/7   = 100.00%
statistics_models.py: 409/444 = 92.12%
statistics.py:        407/443 = 91.87%
TOTAL:                823/894 = 92.06%
```

A cobertura mínima de 90% foi atingida.

## 15. Regressão

Foram executadas conjuntamente as suítes SPR-008A, 008B, 008C, 008D, 008E, 008F,
008G, 008H, 008I, 008J, 008K e 008L:

```text
310 passed in 8.79s
```

Classificação dos resultados:

- falha funcional: nenhuma;
- falha arquitetural: nenhuma;
- falha legada: nenhuma;
- falha ambiental: `coverage.py` indisponível; substituído pela metodologia
  determinística da biblioteca padrão, sem impedir o aceite.

## 16. Limitações

- Histogramas são efêmeros e existem somente em memória.
- As estimativas são lógicas e aproximadas; nenhuma consulta é executada.
- A estratégia configurada estabelece a fundação, sem escolher ou reescrever planos.
- Não há persistência, cache externo, banco, filesystem, API, SQL ou integração de
  infraestrutura.
- Não há Query Optimizer nem Cost Based Planner.

## 17. Compatibilidade

A API pública anterior permaneceu integralmente compatível. As mudanças são apenas
aditivas em `cko.core.discovery` e `cko.core`. A regressão completa demonstra a
preservação dos contratos homologados SPR-008A–008K.

## 18. Respostas obrigatórias

1. A fundação de estatísticas foi implementada? **Sim.**
2. Histogramas foram implementados? **Sim.**
3. Estatísticas são determinísticas? **Sim.**
4. Existe estimativa de seletividade? **Sim.**
5. Existe estimativa de cardinalidade? **Sim.**
6. Existe estimativa de custo? **Sim.**
7. Existe Query Optimizer? **Não.**
8. Existe Cost Based Planner? **Não.**
9. Existe banco? **Não.**
10. Existe filesystem? **Não no escopo implementado.**
11. Existe persistência? **Não.**
12. Existe cache externo? **Não.**
13. API pública permaneceu compatível? **Sim.**
14. Regressão SPR-008A–008L aprovada? **Sim, 310 testes aprovados.**
15. Cobertura mínima atingida? **Sim, 92,06%.**
16. A SPR-008L pode ser homologada? **Sim.**

## 19. Declaração final

A SPR-008L está implementada, validada e apta para homologação formal. O escopo foi
encerrado sem iniciar qualquer trabalho da SPR-008M.
