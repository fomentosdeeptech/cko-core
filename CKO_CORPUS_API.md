# CKO Knowledge Corpus Public API

O namespace estável é `cko.core.corpus`. Os nomes públicos não colidem com os aliases homologados e os principais contratos também são reexportados por `cko.core`.

## Constantes e identidade

- `CORPUS_SCHEMA_VERSION`, `CORPUS_SERIALIZATION_VERSION`, `CORPUS_VERSION`, `CORPUS_UUID_NAMESPACE`.
- `CorpusId`: `new`, `parse` e derivação UUIDv5 `canonical`.
- `CorpusIdentity`: identidade estável por namespace e nome.
- `CorpusVersion`: versão semântica lógica e revisão não negativa.

## Modelos

- `CorpusMemberCategory`, `CorpusMemberReference`, `CorpusManifest` e `CorpusMetadata`.
- `KnowledgeCorpus`, `CorpusSnapshot` e `CorpusStatistics`.
- `CorpusReferenceChange` e `CorpusComparisonResult`.

## Construção, validação e serialização

- `CorpusFactory`: `create_reference`, `reference_from_member`, `create_manifest`, `create_corpus`, `from_parts` e `create_snapshot`.
- `CorpusBuilder`: `from_corpus`, `add`, `add_reference`, `remove_reference` e `build`.
- `CorpusValidator` e `DeterministicCorpusSerializer`.
- Protocolos: `CorpusSerializer`, `CorpusValidatorContract`, `CorpusFactoryContract` e `CorpusBuilderContract`.

## Operações puras

`add_member`, `remove_member`, `contains_member`, `find_member`, `filter_members`, `compare_corpora` e `corpus_statistics`. `CorpusOperations` oferece a mesma superfície em uma fachada agrupada. `canonical_corpus_digest`, `corpus_digest_payload` e `reference_from_member` são utilitários determinísticos públicos.

## Exceções

Todas derivam de `CKOError`: `CorpusError`, `CorpusValidationError`, `CorpusIdentityError`, `CorpusReferenceError`, `CorpusCategoryError`, `DuplicateCorpusMemberError`, `CorpusManifestError`, `CorpusVersionError`, `CorpusDigestError`, `CorpusSerializationError`, `CorpusFactoryError` e `CorpusOperationError`. Cada erro possui `code`, `model`, `details` imutáveis e `to_dict()`.

## Inventário

O `__all__` do namespace é a fonte canônica do inventário. Somente contratos estáveis são publicados; `_FACTORY_TOKEN` e helpers de parsing permanecem internos. A versão pública do SDK permanece `1.0.0`, coerente com a política observada nas fundações SPR-010–015 do CORE 1.0 consolidado.
