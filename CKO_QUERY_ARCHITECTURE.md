# CKO Knowledge Query Foundation — Arquitetura

## Estado arquitetural

A Knowledge Query Foundation define a representação canônica de intenção de consulta do CKO. O namespace oficial é `cko.core.query`. A fundação é imutável, versionada, determinística, independente de infraestrutura e não contém mecanismo de execução.

## Limites

O módulo representa modelos, contratos, filtros, expressões, critérios, ordenação, projeção, paginação, resultados e estatísticas lógicas. O módulo não executa consultas, não traduz consultas, não acessa armazenamento, não indexa conteúdo e não realiza ranqueamento.

As dependências de domínio são limitadas aos modelos públicos homologados:

- `KnowledgeObject`, da SPR-010;
- `CanonicalDocument`, da SPR-011;
- `CanonicalRelationship`, da SPR-012;
- `CanonicalGraph`, da SPR-013.

Esses modelos podem compor `QueryResult`. Nenhuma API interna dessas fundações é utilizada.

## Organização do namespace

| Arquivo | Responsabilidade |
|---|---|
| `contracts.py` | Modelo-base, normalização, deep freeze, UTC, primitivas e protocolos |
| `errors.py` | Hierarquia de exceções derivada de `CKOError` |
| `enums.py` | Vocabulário enumerado oficial |
| `factory.py` | Fronteira obrigatória de criação dos agregados |
| `identity.py` | Identidade lógica e canônica |
| `metadata.py` | Metadados imutáveis da intenção |
| `models.py` | Modelos declarativos e agregados |
| `serializer.py` | JSON UTF-8 fechado, determinístico e SHA-256 |
| `validator.py` | Validação estrutural, semântica e de duplicidades |
| `__init__.py` | API pública do namespace |

## Invariantes

Todos os modelos são `dataclass(frozen=True, slots=True)`, possuem `schema_version` e discriminador estável. Datas são normalizadas para UTC. Sequências mutáveis são convertidas em tuplas. Mapeamentos são ordenados e protegidos por `MappingProxyType`. Números não finitos são rejeitados.

`CanonicalQuery`, `QueryResult` e `QueryCollection` somente podem ser materializados pela `QueryFactory`. A desserialização também atravessa a factory e o validador.

## Estrutura lógica

`QueryConstraint` representa uma comparação. `QueryFilter` vincula a comparação a uma dimensão oficial. `QueryExpression` compõe filtros e expressões com AND, OR e NOT. `QueryDescriptor` reúne alvos, escopo, consistência, filtros, expressão, ordenação, projeção e paginação. `CanonicalQuery` acrescenta identidade e metadados à intenção.

`QueryResult` é um envelope declarativo de resultado fornecido por uma camada externa futura. Ele não produz nem transforma itens. Totais, tempo lógico, estatísticas, avisos e metadados são validados por consistência estrutural.

## Independência tecnológica

Não existem imports de Storage, Runtime, SQLite, Filesystem, mecanismos de busca, SQL, bancos de grafos, bancos vetoriais, IA, embeddings ou LLM. Os nomes e valores do modelo não expõem construções específicas dessas tecnologias.

## Compatibilidade pública

O namespace `cko.core` já publicava `QueryFilter`, `QueryOperator`, `QueryOrdering`, `QueryPagination` e `QueryProjection` da Discovery Foundation. Esses símbolos foram preservados sem alteração. A raiz publica os novos tipos conflitantes como `CanonicalQueryFilter`, `CanonicalQueryOperator`, `CanonicalQueryOrdering`, `CanonicalQueryPagination` e `CanonicalQueryProjection`. A API integral e nominal da SPR-014 permanece disponível em `cko.core.query`.
