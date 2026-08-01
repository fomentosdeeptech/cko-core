# CKO Knowledge Graph Foundation — Serialização

## Formato canônico

`DeterministicGraphSerializer` produz bytes JSON UTF-8 com chaves ordenadas, separadores compactos, Unicode preservado e `allow_nan=False`. Cada envelope contém exatamente `model`, `schema_version` e os campos declarados pelo modelo.

## Schema fechado

O desserializador rejeita:

- campos ausentes, adicionais ou desconhecidos;
- discriminadores desconhecidos;
- versões de schema não suportadas;
- JSON não canônico, incluindo espaços externos;
- bytes UTF-8 inválidos;
- NaN e infinitos;
- modelos encapsulados que não pertençam às fundações homologadas.

## Modelos encapsulados

Payloads de nós são reconstruídos pelos serializadores oficiais de Knowledge Objects e Canonical Documents. Payloads de arestas são reconstruídos pelo serializador oficial de Canonical Relationships. A reconstrução passa novamente pelas factories e validações homologadas.

## Round-trip

Após desserializar, o serviço serializa novamente o valor e exige igualdade byte a byte com a entrada. Essa verificação torna obrigatória a representação canônica e garante round-trip determinístico.

## Digest

`digest` calcula SHA-256 sobre os bytes canônicos. `GraphSnapshot.digest` é verificado contra a serialização do grafo encapsulado durante a desserialização. Um snapshot adulterado é rejeitado com `GraphSerializationError`.

## Codificação temporal

Instantes são emitidos em ISO-8601 com offset UTC. A desserialização normaliza valores timezone-aware para UTC antes da validação.
