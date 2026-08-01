# CKO Knowledge Query Foundation — Serialização

## Formato canônico

A serialização oficial é JSON codificado em UTF-8. As chaves são ordenadas lexicograficamente, separadores não contêm espaços, caracteres Unicode não são convertidos para escapes ASCII e números não finitos são proibidos.

Cada envelope contém exatamente `schema_version`, `model` e os campos declarados pelo modelo. Campos ausentes, adicionais ou desconhecidos são rejeitados. Discriminadores e versões desconhecidos também são rejeitados.

## Determinismo

O mesmo modelo imutável produz a mesma sequência de bytes. Mapeamentos são ordenados antes da codificação. Tuplas são codificadas como arrays JSON. Enums são codificados pelos valores públicos. UUIDs são codificados em forma textual canônica.

## Instantes e UTC

Campos temporais estruturais usam ISO 8601 com offset UTC. Instantes recebidos com outro offset são normalizados para UTC durante a criação. Instantes dentro de valores abertos de restrição ou metadados usam um marcador escalar fechado para preservar o tipo durante o round-trip.

## Valores declarativos

Valores de `QueryConstraint`, atributos, métricas e metadados aceitam somente valores imutáveis suportados: nulo, booleano, inteiro, float finito, texto, UUID, datetime consciente de fuso, enum, modelo de query, sequência e mapeamento textual. Outros tipos são rejeitados.

## Round-trip

Após a leitura, o modelo passa pela factory e pelo validador. Em seguida, ele é serializado novamente. Os bytes resultantes devem corresponder exatamente ao texto recebido. Espaços adicionais, ordem não canônica de chaves e representações alternativas são rejeitados.

## SHA-256

`digest` calcula SHA-256 diretamente sobre os bytes JSON canônicos e retorna 64 caracteres hexadecimais minúsculos. O digest identifica a representação, não executa consulta e não constitui mecanismo de persistência.

## Modelos integrados

Itens de `QueryResult` são envelopes públicos completos de `KnowledgeObject`, `CanonicalDocument`, `CanonicalRelationship` ou `CanonicalGraph`. A restauração é delegada exclusivamente aos serializadores públicos homologados de cada fundação.

## Rejeições obrigatórias

O serializador rejeita JSON inválido, UTF-8 inválido, NaN, infinitos, campos desconhecidos, discriminadores desconhecidos, versões de schema não suportadas, envelopes não canônicos, modelos integrados não homologados e inconsistências entre totais e estatísticas.
