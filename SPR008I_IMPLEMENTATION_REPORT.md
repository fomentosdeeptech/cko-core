# SPR-008I — CKO CORE SDK — Discovery Query Foundation

## 1. Objetivo

Foi implementado o modelo canônico, imutável, versionado e independente de
infraestrutura para descrição e resolução lógica de consultas do Discovery. A
implementação pertence exclusivamente ao namespace `cko.core` e respeita a
Baseline Arquitetural 1.0, sem criar arquitetura paralela.

## 2. Arquitetura

A fundação foi organizada em quatro módulos coesos sob `cko.core.discovery`:

- `query_errors.py`: hierarquia pública de erros;
- `query_models.py`: modelos, invariantes e serialização versionada;
- `query_validation.py`: validação estrutural e de consistência;
- `query_resolution.py`: resolução para plano lógico neutro e logging.

Não há tradutor, adaptador, provider concreto ou acesso a infraestrutura. A
resolução opera exclusivamente sobre objetos fornecidos em memória e produz
outro objeto canônico imutável.

## 3. Modelos

Foram criados os seguintes modelos e enums públicos:

- `DiscoveryQuery`;
- `QueryFilter` e `QueryOperator`;
- `FilterGroup` e `FilterGroupOperator`;
- `QueryProjection`;
- `QueryOrdering` e `QueryOrderingDirection`;
- `QueryPagination`;
- `QueryPlan`;
- `QUERY_SCHEMA_VERSION`.

Todos os modelos são dataclasses congeladas com slots. Sequências são
normalizadas para tuplas e mapas são copiados e congelados recursivamente. O
schema público da fundação é `1.0`.

## 4. Filtros

`QueryFilter` representa um predicado atômico formado por atributo, operador e
valor canônico. Valores compostos aceitos são congelados recursivamente. Valores
não serializáveis e números não finitos são rejeitados.

`FilterGroup` compõe filtros e outros grupos recursivamente. `AND` e `OR` exigem
ao menos um membro; `NOT` exige exatamente um membro. Os filtros declarados no
nível superior de `DiscoveryQuery` são combinados por `AND` implícito e essa
decisão é registrada nas justificativas do plano.

## 5. Operadores

Foram implementados os 13 operadores obrigatórios:

- `equals`;
- `not_equals`;
- `greater_than`;
- `greater_or_equal`;
- `lower_than`;
- `lower_or_equal`;
- `contains`;
- `starts_with`;
- `ends_with`;
- `in`;
- `not_in`;
- `exists`;
- `not_exists`.

`exists` e `not_exists` não aceitam valor. `in` e `not_in` exigem coleção não
vazia. Operadores textuais exigem texto, e operadores relacionais exigem valor
escalar.

## 6. Resolução

`QueryResolver` valida automaticamente a consulta e produz `QueryPlan`. A
resolução:

1. preserva filtros e grupos booleanos;
2. preserva projeções explícitas;
3. normaliza ordenações por prioridade crescente;
4. normaliza paginação baseada em página para limites de offset;
5. calcula estimativas puramente lógicas;
6. registra justificativas auditáveis;
7. aceita timestamp explícito para reprodução exata do plano.

Não existe tradução para SQL, API, ORM ou linguagem de provider.

## 7. Plano lógico

`QueryPlan` contém:

- identificador da consulta;
- filtros efetivos;
- projeções;
- ordenação;
- paginação normalizada;
- estimativas de quantidade de predicados, grupos e limite superior;
- justificativas;
- timestamp UTC;
- schema versionado.

O plano possui `to_dict`, `to_json`, `from_dict` e `from_json`. A serialização é
determinística, usa JSON ordenado e rejeita envelopes incompletos, desconhecidos
ou com versão incompatível.

## 8. Validação

`QueryValidationEngine` valida:

- tipos de filtros e grupos;
- operadores e formatos de valores;
- projeções duplicadas;
- atributos de ordenação duplicados;
- prioridades de ordenação duplicadas;
- valores de página, tamanho, limite e offset;
- consistência entre página e offset;
- consistência entre tamanho de página e limite;
- consistência entre paginação e os limites declarados na consulta;
- integridade geral do modelo.

Filtros repetidos sobre o mesmo atributo são deliberadamente permitidos, pois
podem expressar intervalos válidos. Duplicidade ambígua é rejeitada nas
projeções e na ordenação.

## 9. Erros públicos

Foi criada e exportada a hierarquia pública:

- `QueryError`;
- `InvalidQueryError`;
- `InvalidFilterError`;
- `InvalidProjectionError`;
- `InvalidOrderingError`;
- `InvalidPaginationError`;
- `QueryValidationError`;
- `QueryResolutionError`.

Todos os erros derivam da hierarquia pública do Discovery. Falhas internas
inesperadas do resolvedor preservam a causa em `QueryResolutionError`.

## 10. Arquivos criados

- `src/cko/core/discovery/query_errors.py`;
- `src/cko/core/discovery/query_models.py`;
- `src/cko/core/discovery/query_validation.py`;
- `src/cko/core/discovery/query_resolution.py`;
- `tests/test_discovery_query_foundation_spr008i.py`;
- `SPR008I_IMPLEMENTATION_REPORT.md`.

## 11. Arquivos alterados

- `src/cko/core/discovery/__init__.py`: exports exclusivamente aditivos;
- `src/cko/core/__init__.py`: exports exclusivamente aditivos.

Nenhum contrato público homologado foi removido ou alterado.

## 12. Testes

A suíte dedicada possui 39 testes aprovados. Ela valida imutabilidade profunda,
serialização, desserialização estrita, schema, todos os operadores, filtros,
grupos recursivos, projeções, ordenação, paginação, resolução, plano lógico,
logging estruturado, erros, exports, type hints, docstrings, UTF-8 sem BOM,
PEP-8 e ausência de infraestrutura.

Resultado dedicado final, com cache desabilitado: `39 passed in 2.37s`.

## 13. Cobertura

`coverage.py` não está instalado no runtime. Foi usada a ferramenta `trace` da
biblioteca padrão com contagem, resumo e linhas ausentes, executando a suíte
dedicada sobre os quatro módulos novos.

Resultados exatos calculados a partir dos arquivos de contagem:

- `query_errors.py`: 100,00% — 19 de 19 linhas rastreáveis;
- `query_models.py`: 95,73% — 471 de 492 linhas rastreáveis;
- `query_validation.py`: 90,32% — 112 de 124 linhas rastreáveis;
- `query_resolution.py`: 93,02% — 120 de 129 linhas rastreáveis;
- cobertura consolidada: 94,50% — 722 de 764 linhas rastreáveis.

A meta mínima obrigatória de 90% foi atingida em cada módulo e no consolidado.

## 14. Regressão

A regressão obrigatória composta pelas suítes SPR-008A, SPR-008B, SPR-008C,
SPR-008D, SPR-008E, SPR-008F, SPR-008G, SPR-008H e SPR-008I foi aprovada
integralmente.

Resultado final: `224 passed in 4.77s`.

Classificação das ocorrências:

- falha funcional: nenhuma;
- falha arquitetural: nenhuma;
- falha ambiental: a primeira execução dedicada não pôde gravar o cache do
  pytest no volume sincronizado; o cache foi desabilitado nas execuções finais,
  sem impacto nos testes;
- falha legada preexistente: nenhuma observada na regressão obrigatória A–I.

O runtime validado é Python 3.13.14, compatível com o requisito `>=3.13` do
projeto.

## 15. Limitações deliberadas

Não foram implementados SQL, SQLite, banco, ORM, filesystem, scanners,
providers concretos, Google Drive, OneDrive, OCR, IA, Graph, APIs, persistência,
rede ou multiprocessing. As estimativas do plano são lógicas e não representam
cardinalidade obtida de fonte externa.

## 16. Compatibilidade

As APIs públicas das SPR-008A até SPR-008H foram preservadas. Os arquivos
`__init__.py` receberam apenas imports e nomes adicionais. A regressão integral
do recorte homologado confirma a compatibilidade comportamental.

As verificações adicionais confirmaram AST válido, imports públicos, UTF-8 sem
BOM, ausência de placeholder, ausência de `NotImplementedError`, ausência de
funções vazias, ausência de imports de infraestrutura e comprimento máximo de
87 caracteres no código de produção novo.

## 17. Respostas obrigatórias

1. O modelo de consultas foi implementado? **Sim.**
2. As consultas são imutáveis? **Sim, inclusive coleções e mapas aninhados.**
3. Os filtros são determinísticos? **Sim.**
4. Existe resolução automática? **Sim.**
5. Existe plano lógico? **Sim, versionado e auditável.**
6. Existe tradução para SQL? **Não.**
7. Existe acesso ao banco? **Não.**
8. Existe acesso ao filesystem? **Não.**
9. Existem providers concretos? **Não.**
10. Existe persistência? **Não.**
11. A API pública permaneceu compatível? **Sim.**
12. A regressão SPR-008A–008I foi aprovada? **Sim, 224 testes aprovados.**
13. A cobertura mínima foi atingida? **Sim, 94,50% consolidada.**
14. A SPR-008I pode ser homologada? **Sim, tecnicamente, aguardando homologação
    formal.**

## 18. Declaração final

A SPR-008I está implementada conforme a Baseline Arquitetural 1.0,
exclusivamente em `cko.core`, sem arquitetura paralela e sem dependência de
infraestrutura. A implementação, os testes, a cobertura, a regressão e as
verificações estáticas foram aprovados. Nenhum trabalho referente à SPR-008J foi
iniciado. O resultado é tecnicamente homologável e aguarda homologação formal.
