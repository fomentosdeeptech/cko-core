# CKO Knowledge Query Foundation — API Pública

## Versões

| Símbolo | Valor |
|---|---|
| `QUERY_SCHEMA_VERSION` | `1.0` |
| `QUERY_VERSION` | `1.0.0` |

## Modelos

| Modelo | Responsabilidade |
|---|---|
| `QueryId` | Identificador UUID lógico ou canônico |
| `QueryIdentity` | Identidade, namespace, nome e versão semântica |
| `QueryMetadata` | Autoria, estado, tags, atributos e instantes UTC |
| `QueryConstraint` | Operador comparativo e valores declarados |
| `QueryFilter` | Dimensão oficial associada a uma restrição |
| `QueryExpression` | Composição lógica AND, OR ou NOT |
| `QueryOrdering` | Campo, direção e prioridade |
| `QueryProjection` | Campos e inclusão de identidade e metadados |
| `QueryPagination` | Limite, deslocamento e cursor lógico |
| `QueryDescriptor` | Critérios completos da intenção |
| `CanonicalQuery` | Agregado canônico de consulta |
| `QueryStatistics` | Totais, tempo lógico e métricas declaradas |
| `QueryResult` | Envelope de itens, totais, estatísticas e avisos |
| `QueryCollection` | Coleção canônica de consultas únicas |

## Enums oficiais

`QueryOperator` contém `EQUAL`, `NOT_EQUAL`, `GREATER_THAN`, `LESS_THAN`, `GREATER_OR_EQUAL`, `LESS_OR_EQUAL`, `CONTAINS`, `STARTS_WITH`, `ENDS_WITH`, `IN`, `BETWEEN`, `AND`, `OR` e `NOT`.

`QueryStatus` contém `DRAFT`, `READY`, `COMPLETED`, `PARTIAL`, `EMPTY` e `FAILED`.

`QueryDirection` contém `ASCENDING` e `DESCENDING`.

`QueryScope` contém `CURRENT_NAMESPACE`, `DESCENDANT_NAMESPACES` e `GLOBAL`.

`QueryTarget` contém `KNOWLEDGE_OBJECT`, `CANONICAL_DOCUMENT`, `CANONICAL_RELATIONSHIP` e `CANONICAL_GRAPH`.

`QueryConsistency` contém `DECLARED`, `CONSISTENT` e `SNAPSHOT`.

## QueryFactory

| Método | Retorno |
|---|---|
| `create_constraint` | `QueryConstraint` |
| `create_filter` | `QueryFilter` |
| `create_expression` | `QueryExpression` |
| `create_ordering` | `QueryOrdering` |
| `create_projection` | `QueryProjection` |
| `create_pagination` | `QueryPagination` |
| `create_descriptor` | `QueryDescriptor` |
| `create` | `CanonicalQuery` |
| `from_parts` | `CanonicalQuery` |
| `create_statistics` | `QueryStatistics` |
| `create_result` | `QueryResult` |
| `result_from_parts` | `QueryResult` |
| `create_collection` | `QueryCollection` |

## Serializador

`DeterministicQuerySerializer.serialize` retorna bytes UTF-8 canônicos. `deserialize` aceita bytes UTF-8 ou texto canônico e restaura o modelo original. `digest` retorna o SHA-256 hexadecimal em minúsculas. `from_dict` restaura um envelope fechado já decodificado.

## Validador

`QueryValidator.validate` aceita somente modelos canônicos dataclass, frozen e slotted. A validação abrange schema, discriminador, estado, operadores, paginação, ordenação, duplicidades, composição lógica, alvos e itens homologados.

## Exceções

| Exceção | Uso |
|---|---|
| `QueryError` | Base pública da fundação |
| `QueryValidationError` | Violação estrutural ou semântica |
| `QuerySerializationError` | Violação do envelope ou JSON canônico |
| `QueryFactoryError` | Violação da fronteira de criação |
| `QueryIdentityError` | Identidade inválida ou inconsistente |

Todas derivam direta ou indiretamente de `CKOError`.

## Exportação na raiz

Os símbolos sem colisão são exportados em `cko.core`. Os cinco símbolos conflitantes usam aliases `CanonicalQueryFilter`, `CanonicalQueryOperator`, `CanonicalQueryOrdering`, `CanonicalQueryPagination` e `CanonicalQueryProjection`. A escolha preserva integralmente os contratos públicos anteriores.
