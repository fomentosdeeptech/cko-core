# SPR-008J — Discovery Query Evaluation Foundation

## 1. Identificação

- Sprint: SPR-008J; componente: CKO CORE SDK, namespace `cko.core`.
- Validação: 2026-07-17; runtime: CPython 3.13.14.
- Baseline: Baseline Arquitetural 1.0 e contratos homologados até SPR-008I.

## 2. Objetivo

Implementada a fundação canônica para avaliar `QueryPlan` sobre subjects em
memória, sem banco, filesystem, rede, provider, repository ou persistência. O
pipeline é: validação, filtros, projeção dos aprovados, ordenação, paginação e
`QueryEvaluationResult` auditável.

## 3. Arquitetura

A implementação foi adicionada ao boundary `cko.core.discovery`. O motor recebe
contratos públicos e estratégias injetáveis. Não há arquitetura paralela nem
tradução para tecnologia de infraestrutura. Resolver, predicados, grupos,
projeção, ordenação, paginação, motor e stream têm responsabilidades separadas.

## 4. Contratos públicos

Publicados `QueryEvaluationSubject`, `AttributeResolver`,
`QueryEvaluationStream`, `AttributeValue` e `MappingQueryEvaluationSubject` em
`cko.core.discovery` e `cko.core`.

## 5. Modelos

Criados modelos congelados e versionados para política, contexto, registro de
predicado, decisão por subject, item projetado e resultado final. Mappings e
sequências são congelados profundamente. JSON é determinístico, UTF-8, sem NaN
e possui envelope estrito de schema/modelo.

## 6. Subject avaliável

`MappingQueryEvaluationSubject` aceita `Mapping[str, object]`, protege a camada
externa com `MappingProxyType` e usa identidade explícita ou `logical_identity`,
`canonical_id` e `id`. Mappings puros são adaptados pelo contrato neutro.

## 7. Resolução de atributos

`DefaultAttributeResolver` resolve caminhos simples e pontuados em mappings e
dataclasses públicas de `cko.core`. Segmentos privados/vazios são bloqueados.
Não há chamada de métodos ou reflexão irrestrita. Ausência usa `exists=False`,
separada de valor existente igual a `None`.

## 8. Semântica dos operadores

- `equals`/`not_equals`: igualdade exata; números `int`/`float` são compatíveis,
  exceto `bool`.
- Quatro operadores relacionais: números compatíveis ou strings.
- `contains`: substring, elemento de sequência ou chave de mapping.
- `starts_with`/`ends_with`: somente strings.
- `in`/`not_in`: pertença exata à coleção canônica.
- `exists`/`not_exists`: presença, independentemente de `None`.

Não ocorre coerção string/número, booleano/inteiro, datetime/string ou
sequência/string. Incompatibilidades seguem a política.

## 9. Grupos lógicos

`FilterGroupEvaluator` avalia `AND`, `OR` e `NOT` recursivamente. `AND` e `OR`
fazem curto-circuito e registram onde ele ocorreu. Predicados visitados são
preservados na auditoria.

## 10. Políticas

`QueryEvaluationPolicy` controla ausência, incompatibilidade, erro, posições de
ausente e `None`, identidade obrigatória, limite e avaliação parcial. Combinações
inseguras são rejeitadas na construção.

## 11. Avaliação

`QueryEvaluationEngine` reutiliza o plano sem mutação, avalia cooperativamente e
produz contagens coerentes. Cada decisão guarda registros, ausências, erros e
justificativas. Duração lógica é a quantidade determinística de predicados
avaliados.

## 12. Projeção

Somente subjects aprovados são projetados. Nomes lógicos são preservados;
ausências aparecem como `None` e em lista explícita; o resultado é imutável.

## 13. Ordenação

Cláusulas são aplicadas por prioridade, ascendente/descendente. Ausente e `None`
têm posições configuráveis, não invertidas pela direção. Tipos incompatíveis
causam erro. Empates usam identidade lógica, sem locale/biblioteca externa.

## 14. Paginação

Offset/limit ou page/page_size normalizados são aplicados após filtragem e
ordenação. O resultado informa total anterior, retornado, offset e limite.

## 15. Execução síncrona

Consome `Iterable`, aplica limite durante o consumo e descarta subjects
rejeitados após criar a auditoria. Aprovados são mantidos apenas enquanto
necessários para projeção, ordenação e paginação.

## 16. Execução assíncrona

Consome `AsyncIterable` diretamente, sem threads/multiprocessing. Aplica a mesma
semântica, política, auditoria e logging. A equivalência foi validada por JSON.

## 17. Avaliação incremental

`DefaultQueryEvaluationStream` oferece fachadas síncrona e assíncrona. Limite e
cancelamento são progressivos; rejeitados não ficam retidos após a avaliação.

## 18. Cancelamento

O `CancellationToken` homologado foi reutilizado e consultado antes de cada
subject. `DiscoveryCancelledError` vira `QueryEvaluationCancelledError` com
causa preservada.

## 19. Logging

Eventos estruturados cobrem início, quantidade recebida, paginação, conclusão,
cancelamento e falha. Conclusões incluem avaliados, correspondentes, rejeitados
e retornados. Conteúdo integral de subjects não é registrado.

## 20. Erros públicos

Criada a hierarquia solicitada derivada de `QueryError`, incluindo base,
subjects/política inválidos, resolução, predicado, grupo, projeção, ordenação,
paginação, cancelamento e limite.

## 21. Arquivos criados

- `src/cko/core/discovery/query_evaluation_errors.py`
- `src/cko/core/discovery/query_evaluation_models.py`
- `src/cko/core/discovery/query_evaluation_contracts.py`
- `src/cko/core/discovery/query_evaluation.py`
- `tests/test_discovery_query_evaluation_spr008j.py`
- `SPR008J_IMPLEMENTATION_REPORT.md`

## 22. Arquivos alterados

- `src/cko/core/discovery/__init__.py`: exports aditivos.
- `src/cko/core/__init__.py`: exports aditivos.

Modelos, erros, validação e resolução da SPR-008I não foram alterados.

## 23. Dependências

Nenhuma dependência de runtime foi adicionada. Apenas biblioteca padrão e
componentes existentes de `cko.core` são usados.

## 24. Testes

A suíte dedicada tem 34 testes cobrindo modelos, congelamento, schema,
desserialização, resolver, 13 operadores, grupos, curto-circuito, políticas,
projeção, ordenação, paginação, limite, cancelamento, sync/async, stream,
logging, inputs, integração e boundaries. Resultado: **34 passed**.

## 25. Cobertura

`coverage.py` não estava instalado. Foi usado `trace` da biblioteca padrão do
Python 3.13 com `--count --missing --summary`. Os `.cover` foram gerados no
temporário gravável da sessão porque o Google Drive recusou esses artefatos.

| Módulo | Executadas | Rastreáveis | Cobertura |
|---|---:|---:|---:|
| `query_evaluation.py` | 529 | 586 | 90,27% |
| `query_evaluation_contracts.py` | 71 | 74 | 95,95% |
| `query_evaluation_errors.py` | 25 | 25 | 100,00% |
| `query_evaluation_models.py` | 333 | 379 | 87,86% |
| **Consolidado** | **958** | **1.064** | **90,04%** |

O mínimo consolidado de 90% foi atingido.

## 26. Regressão

Executadas juntas as suítes SPR-008A, 008B, 008C, 008D, 008E, 008F, 008G,
008H, 008I e 008J. Resultado: **258 passed**, sem falha funcional,
arquitetural ou regressão legada observada.

## 27. Validações adicionais

- Python 3.13.14; AST/imports; UTF-8 sem BOM.
- Máximo de 99 caracteres por linha nos quatro módulos de produção.
- Type hints e docstrings nos contratos públicos.
- Sem imports de infraestrutura, threading ou multiprocessing.
- Sem `TODO`, `NotImplementedError`, placeholders ou funções vazias.

## 28. Limitações deliberadas

- Dataclasses somente quando públicas e pertencentes a `cko.core`.
- Relacionais não aceitam datetime, não homologado pela SPR-008I como valor de
  `QueryFilter`.
- Ordenação global retém apenas aprovados, necessidade lógica determinística.
- Sem avaliação distribuída, provider, cache externo ou persistência.

## 29. Compatibilidade com Sprints anteriores

`QueryPlan`, `QueryFilter`, `FilterGroup`, projeção, ordenação, paginação,
`QueryResolver`, `QueryValidationEngine`, `CancellationToken` e `CanonicalId`
foram reutilizados. Não houve mudança homologada; exports são aditivos. A
regressão 008A–008I passou integralmente.

## 30. Respostas obrigatórias

1. Fundação implementada? **Sim.**
2. `QueryPlan` reutilizado sem alteração? **Sim.**
3. `QueryFilter` reutilizado sem alteração? **Sim.**
4. Filtros funcionais? **Sim.**
5. AND, OR e NOT funcionais? **Sim.**
6. Os 13 operadores funcionais? **Sim.**
7. Ausente distinto de `None`? **Sim.**
8. Incompatibilidades explícitas? **Sim.**
9. Projeções funcionais? **Sim.**
10. Ordenação funcional? **Sim.**
11. Paginação funcional? **Sim.**
12. Desempate determinístico? **Sim, por identidade.**
13. Execução síncrona funcional? **Sim.**
14. Execução assíncrona funcional? **Sim.**
15. Avaliação incremental? **Sim.**
16. `CancellationToken` reutilizado? **Sim.**
17. Subjects imutáveis? **Sim; o motor não os altera.**
18. Tradução SQL? **Não.**
19. Acesso a banco? **Não.**
20. Acesso a filesystem? **Não no código de produção.**
21. Provider concreto? **Não.**
22. Persistência? **Não.**
23. Integração automática com Inventory? **Não.**
24. API compatível? **Sim, com exports aditivos.**
25. Regressão 008A–008J aprovada? **Sim, 258 testes.**
26. Cobertura mínima? **Sim, 90,04%.**
27. Python 3.13? **Sim, CPython 3.13.14.**
28. Pode ser homologada? **Sim, tecnicamente.**

## 31. Declaração final

A SPR-008J está implementada na Baseline 1.0, sem infraestrutura, arquitetura
paralela ou alteração de contratos homologados. Validações funcionais,
arquiteturais, regressão e cobertura foram aprovadas. Está pronta para
homologação formal. Nenhum trabalho da SPR-008K foi iniciado.
