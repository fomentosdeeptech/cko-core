# CKO Corpus Serialization

`DeterministicCorpusSerializer` suporta todos os onze modelos públicos e garante `deserialize(serialize(value)) == value`.

## Canonicalização

O formato é JSON UTF-8, Unicode preservado, chaves de objetos ordenadas lexicograficamente, separadores `,` e `:` sem espaços e `allow_nan=False`. Cada modelo exige `model` e `schema_version`. O registry de discriminadores e o conjunto exato de campos são fechados; campos ausentes, extras, categorias desconhecidas e versões incompatíveis são rejeitados.

O desserializador reserializa o JSON recebido e exige igualdade textual integral. Assim, whitespace alternativo, outra ordem de chaves ou formas não canônicas são inválidos. UUIDs usam sua forma textual padrão; datas usam ISO-8601 com timezone e são normalizadas para UTC; mappings são ordenados e sequências tornam-se arrays. Campos opcionais são sempre presentes e usam `null` quando ausentes.

## Ordem do manifesto e corpus vazio

O manifesto é normalizado antes da serialização por `CorpusMemberReference.sort_token`; a ordem de entrada não possui semântica. Um manifesto vazio serializa como `"members":[]` e é válido.

## Digests

`KnowledgeCorpus.digest` é SHA-256 sobre os bytes canônicos de `corpus_digest_payload`: `schema_version`, `serialization_version`, `identity`, `corpus_version`, `manifest` e `metadata`. O campo digest é excluído para evitar autorreferência. `CorpusFactory.from_parts` e `CorpusValidator` recalculam e validam o valor.

`DeterministicCorpusSerializer.digest(model)` fornece adicionalmente o SHA-256 do envelope serializado completo de qualquer modelo. Para `KnowledgeCorpus`, esse digest de transporte inclui o campo `digest` e não substitui o digest canônico de composição armazenado na raiz.

## Compatibilidade

Esta implementação aceita apenas esquema `1.0` e serialização `1.0`. Alterações aditivas ou novas categorias exigem versão explícita; não há migração ou upgrade operacional. Pickle, objetos executáveis, endereços de memória, NaN e infinito são proibidos.
