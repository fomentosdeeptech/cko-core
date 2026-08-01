# CKO Relationship Serialization

## Contrato

`DeterministicRelationshipSerializer` implementa serialização JSON canônica para todos os modelos de `cko.core.relationships`.

- codificação UTF-8;
- chaves em ordem lexicográfica;
- separadores compactos;
- `ensure_ascii=False`;
- `allow_nan=False`;
- schema fechado;
- discriminador obrigatório;
- schema version obrigatório;
- round-trip byte a byte obrigatório.

## Envelope

Todo modelo serializado contém `schema_version` e `model`. Os demais campos são definidos de forma fechada para cada discriminador. Campos ausentes, adicionais ou desconhecidos causam `RelationshipSerializationError`.

O schema homologado é `1.0`. Payload com outro schema é rejeitado antes da criação do modelo.

## Valores canônicos

- UUID é texto no formato canônico.
- Enum é seu valor textual oficial.
- `datetime` é ISO-8601 com timezone e normalizado para UTC.
- Tupla é array JSON.
- Mapping imutável é objeto JSON com chaves ordenadas.
- Nulo, booleano, inteiro, float finito e texto mantêm seus tipos JSON.

NaN e infinitos positivos ou negativos são rejeitados na construção, serialização e leitura.

## Determinismo

Para um mesmo modelo válido, `serialize` sempre produz os mesmos bytes. `digest` calcula SHA-256 sobre esses bytes canônicos. O digest representa o envelope completo e não cria identidade de armazenamento.

## Round-trip estrito

`deserialize` realiza quatro etapas:

1. decodifica bytes como UTF-8 estrito;
2. interpreta JSON sem constantes numéricas não finitas;
3. aplica schema fechado e recria modelos validados;
4. serializa novamente e compara o texto byte a byte.

JSON semanticamente equivalente, mas não canônico, é rejeitado. Isso inclui espaços adicionais, outra ordem de chaves e representações numéricas não estáveis.

## Discriminadores

Discriminadores homologados:

- `relationship_id`
- `relationship_identity`
- `relationship_endpoint`
- `relationship_metadata`
- `relationship_direction`
- `relationship_constraint`
- `relationship_evidence`
- `relationship_weight`
- `relationship_version`
- `relationship_descriptor`
- `canonical_relationship`
- `relationship_collection`
- `relationship_query`
- `relationship_result`

## Segurança de schema

O desserializador não importa classes indicadas pelo payload, não executa código e não aceita extensões abertas. O discriminador é resolvido por tabela fechada no código. Agregados desserializados passam novamente pela `RelationshipFactory` e pelo `RelationshipValidator`.
