# SPR-008K — Discovery Query Index Foundation

## 1. Objetivo

Implementar a fundação canônica de indexação lógica do Discovery no namespace
`cko.core`, integralmente em memória, desacoplada de banco de dados, filesystem,
cache externo, providers concretos e persistência.

## 2. Arquitetura

O fluxo implementado é:

`Discovery Assets → LogicalIndexBuilder → LogicalIndex →
LogicalIndexResolver / QueryIndexPlanner → Query Evaluation Engine`

A fundação consome o `QueryPlan` homologado na SPR-008I e preservado pela
SPR-008J. Nenhum contrato anterior foi modificado. As exportações públicas nos
arquivos `__init__.py` são exclusivamente aditivas.

## 3. Modelos

Foram implementados modelos versionados, congelados e serializáveis:

- `LogicalIndex`;
- `LogicalIndexEntry`;
- `LogicalIndexStatistics`;
- `LogicalIndexPolicy`;
- `DiscardedLogicalIndex`;
- `LogicalIndexReport`;
- `QueryIndexPlan`.

Os modelos usam `dataclass(frozen=True, slots=True)`, normalização profunda de
sequências e mappings, timestamps UTC e envelopes JSON estritos com
`schema_version` e `model`. O schema da Sprint é `1.0`.

## 4. Índices

O enum público `IndexStrategy` contém `HASH`, `ORDERED`, `PREFIX` e
`COMPOSITE`. O índice registra identificador, nome, atributos indexados,
estratégia, cardinalidade lógica, estatísticas e entradas imutáveis.

## 5. Construção

`LogicalIndexBuilder` recebe somente objetos já existentes em memória. A
identidade é resolvida deterministicamente por `logical_identity`, `identity`
ou `id`. Atributos pontuados são suportados em mappings e objetos. Entradas são
ordenadas por identidade e chave canônica, tornando o resultado independente
da ordem da fonte.

As duplicidades obedecem a `DuplicateBehavior`: `REJECT`, `KEEP_FIRST` ou
`KEEP_LAST`. A política também limita a cardinalidade.

## 6. Validação

`LogicalIndexValidator` valida:

- tipo e contrato do índice;
- limite de cardinalidade;
- duplicidade de identidades;
- presença dos atributos indexados;
- correspondência entre chave e atributos;
- coerência das estatísticas e distribuição;
- estratégia e cardinalidade já protegidas pelos modelos.

O método `validate` retorna o mesmo índice quando aprovado e `is_valid` oferece
uma consulta booleana sem alterar estado.

## 7. Resolução

`LogicalIndexResolver` avalia compatibilidade entre operadores, ordenações,
atributos e estratégias. O ranking é estável e auditável: compatibilidade,
cobertura, custo lógico e identificador do índice formam o desempate
determinístico. O resultado é um `LogicalIndexReport` versionado.

## 8. Planejamento

`QueryIndexPlanner` recebe um `QueryPlan` e índices disponíveis. Produz um
`QueryIndexPlan` com índice selecionado, atributos atendidos, custo lógico,
justificativas, relatório de resolução e timestamp. Quando nenhum índice é
compatível, o plano representa explicitamente uma varredura lógica completa.

## 9. Políticas

`LogicalIndexPolicy` é imutável e contém limite de índices, limite de
cardinalidade, comportamento para duplicidades, estratégia padrão e regras de
seleção. Valores inválidos são recusados na construção.

## 10. Logging

Eventos estruturados foram adicionados para construção, validação, seleção,
planejamento e conclusão. Os registros usam o logger canônico `cko` e os campos
`event` e `context`.

## 11. Arquivos criados

- `src/cko/core/discovery/query_index_errors.py`;
- `src/cko/core/discovery/query_index_models.py`;
- `src/cko/core/discovery/query_index.py`;
- `tests/test_discovery_query_index_foundation_spr008k.py`;
- `SPR008K_IMPLEMENTATION_REPORT.md`.

## 12. Arquivos alterados

- `src/cko/core/discovery/__init__.py` — exportações aditivas;
- `src/cko/core/__init__.py` — exportações aditivas.

## 13. Testes

A suíte específica da SPR-008K possui 20 testes e foi aprovada:

`20 passed in 2.64s`

Ela valida modelos imutáveis, imutabilidade profunda, serialização estrita,
schema, construção, entradas, estatísticas, estratégias, duplicidades,
cardinalidade, validação, seleção, desempate, planejamento, resolução, política,
logging, API pública, type hints, docstrings, UTF-8 sem BOM, linhas PEP-8 e
ausência de infraestrutura proibida.

## 14. Cobertura

`coverage.py` não está instalado no ambiente. Foi aplicada metodologia
determinística com o módulo `trace` da biblioteca padrão, conforme autorizado
pelo briefing:

- `query_index.py`: 331/353 linhas executáveis — 93,77%;
- `query_index_errors.py`: 13/13 — 100%;
- `query_index_models.py`: 388/430 — 90,23%;
- total da SPR-008K: 732/796 — **91,96%**.

A cobertura mínima de 90% foi atingida.

## 15. Regressão

A execução conjunta obrigatória SPR-008A–SPR-008K foi aprovada:

`278 passed in 5.15s`

Classificação dos resultados:

- falha funcional: nenhuma;
- falha arquitetural: nenhuma;
- falha ambiental: `coverage.py` ausente; diretório sincronizado recusou os
  arquivos transitórios do primeiro `trace`, contornado por diretório temporário;
- falha legada: nenhuma.

## 16. Limitações deliberadas

Não foram implementados SQL, SQLite, banco de dados, ORM, filesystem, providers,
cache externo, Redis, Elastic, Lucene, FAISS, Graph, APIs, OCR, IA ou
persistência. A fundação não executa a consulta nem cria índices físicos; ela
constrói, valida, resolve e planeja índices lógicos em memória.

## 17. Compatibilidade

As Sprints SPR-008A–SPR-008J permaneceram compatíveis. Nenhum contrato homologado
foi alterado. Todo código novo pertence a `cko.core.discovery`, dentro do
namespace obrigatório `cko.core`.

## 18. Respostas obrigatórias

1. A fundação de índices foi implementada? **Sim.**
2. Os índices são imutáveis? **Sim.**
3. Existe construção determinística? **Sim.**
4. Existe seleção automática? **Sim.**
5. Existe planejamento de utilização? **Sim.**
6. Existe resolução automática? **Sim.**
7. Existe acesso ao banco? **Não.**
8. Existe acesso ao filesystem? **Não no código de produção da SPR-008K.**
9. Existe cache externo? **Não.**
10. Existe persistência? **Não.**
11. Existe provider concreto? **Não.**
12. A API pública permaneceu compatível? **Sim.**
13. A regressão SPR-008A–008K foi aprovada? **Sim, 278 testes aprovados.**
14. A cobertura mínima foi atingida? **Sim, 91,96%.**
15. A SPR-008K pode ser homologada? **Sim, tecnicamente recomendada para
    homologação formal.**

## 19. Declaração final

A SPR-008K foi concluída exclusivamente no escopo autorizado. A fundação de
índices lógicos é imutável, determinística, auditável, versionada, testada e
independente de infraestrutura. Nenhum trabalho da SPR-008L foi iniciado. O
resultado está pronto para homologação formal.
