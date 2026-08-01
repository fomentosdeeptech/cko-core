# CKO Document Canonical Model — Serialização

## Contrato

`DeterministicDocumentSerializer` é o serializer oficial do namespace `cko.core.documents`. Sua saída é um documento JSON em bytes UTF-8, com ordenação estável de chaves e separadores canônicos.

Cada envelope contém obrigatoriamente `schema_version` e `model`. O campo `model` é o discriminador fechado do tipo. A versão inicial do schema documental é `1.0`.

## Canonicalização

A codificação usa as seguintes regras:

- UTF-8 sem escape obrigatório de caracteres Unicode;
- chaves em ordem lexicográfica;
- separadores sem espaços;
- instantes ISO-8601 normalizados para UTC;
- UUIDs em representação textual canônica;
- enums por seus valores oficiais;
- tuplas como arrays JSON;
- mapeamentos com chaves textuais ordenadas;
- ausência de NaN e infinito.

O serializer valida o modelo antes da codificação. Um payload decodificado é novamente serializado e precisa produzir exatamente o texto recebido. Espaços adicionais, ordem alternativa de chaves e outras formas JSON semanticamente equivalentes são rejeitados por não serem canônicos.

## Schema fechado

Cada discriminador possui conjunto exato de campos. Campo ausente, campo desconhecido, discriminador desconhecido e versão de schema não suportada geram `DocumentSerializationError`.

Modelos aninhados também usam envelopes completos. `KnowledgeObject` e `KnowledgeObjectId` são delegados ao `DeterministicKnowledgeSerializer` homologado. Essa delegação preserva integralmente o schema da Knowledge Object Foundation.

## Round-trip

O round-trip obrigatório obedece à identidade:

`deserialize(serialize(modelo)) == modelo`

A reconstrução de `CanonicalDocument` e `DocumentCollection` passa por `DocumentFactory`. Portanto, desserialização não contorna a fronteira obrigatória de criação nem o `DocumentValidator`.

## Digest

`digest` calcula SHA-256 sobre os bytes JSON canônicos. O resultado é estável para o mesmo valor documental e inclui schema, discriminadores e todos os campos serializados.

O digest de serialização não substitui `DocumentIntegrity`. O primeiro protege a representação canônica do modelo; o segundo descreve a integridade lógica e física declarada do documento.

## Falhas

São recusados:

- bytes que não formam UTF-8 válido;
- JSON inválido;
- constantes numéricas não finitas;
- raiz que não seja objeto;
- arrays onde um objeto é exigido;
- objetos onde um array é exigido;
- envelopes com campos desconhecidos ou ausentes;
- schema diferente de `1.0`;
- discriminador ausente, incorreto ou desconhecido;
- enum, UUID, hash, data ou modelo aninhado inválido;
- JSON válido que não esteja na forma canônica.
