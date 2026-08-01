# SPR-011 — Document Canonical Model — Relatório de Implementação

## Status

Implementação funcional concluída em 26 de julho de 2026 e pronta para homologação técnica da SPR-011, com duas falhas herdadas da regressão geral registradas na seção de testes.

## Escopo entregue

Foi criado exclusivamente o namespace `cko.core.documents`, composto por `__init__.py`, `contracts.py`, `errors.py`, `enums.py`, `factory.py`, `identity.py`, `metadata.py`, `models.py`, `serializer.py` e `validator.py`.

O único módulo público preexistente alterado foi `cko/core/__init__.py`, para exportação da nova API. O `CanonicalDocument` legado foi preservado; o novo agregado é exposto no topo como `DocumentCanonicalModel`.

## Modelos entregues

- `DocumentId`;
- `DocumentIdentity`;
- `DocumentMetadata`;
- `DocumentDescriptor`;
- `DocumentContentDescriptor`;
- `DocumentLanguage`;
- `DocumentAuthor`;
- `DocumentSource`;
- `DocumentRepresentation`;
- `DocumentVersion`;
- `DocumentStatistics`;
- `DocumentIntegrity`;
- `DocumentRights`;
- `CanonicalDocument`;
- `DocumentCollection`.

Todos são dataclasses congeladas e slotted, possuem schema `1.0`, discriminador estável, normalização UTC, estruturas internas imutáveis e serialização determinística.

## Integração com Knowledge Objects

`DocumentFactory` usa exclusivamente `KnowledgeObjectFactory` e modelos públicos da Knowledge Object Foundation. Cada documento contém um `KnowledgeObject` do tipo `COMPOSITE`, compartilha identidade lógica, namespace e versão e permanece validável pelo contrato homologado. Nenhum contrato público de Knowledge Objects foi modificado.

## Serialização

Foi entregue JSON determinístico UTF-8, com chaves ordenadas, separadores canônicos, rejeição de NaN e infinito, schema fechado, campos desconhecidos proibidos, discriminador obrigatório, digest SHA-256 e round-trip obrigatório.

## Validação

O validador cobre identidade, schemas, discriminadores, datas, UTC, idiomas, hashes, integridade, estatísticas, versões, duplicidades, campos obrigatórios, consistência com Knowledge Object, consistência de checksum e tamanhos.

## Testes dedicados

Arquivo: `tests/test_document_canonical_model_spr011.py`.

Resultado final: 30 testes aprovados.

Cobertura do namespace, incluindo branches: 97%, acima do mínimo de 95%.

O conjunto valida modelos imutáveis, todos os formatos oficiais, Factory exclusiva, deep freeze, identidade em quatro dimensões, especialização de Knowledge Object, serialização determinística, round-trip, JSON estrito, integridade e caminhos defensivos.

## Regressão completa

A execução com raiz temporária local nova alcançou todos os testes: 762 aprovados e 2 falhas fora do SPR-011.

Falhas herdadas identificadas:

1. `tests/test_file_metadata.py::test_collect_metadata`: o teste chama `collect_metadata` com `calculate_hash`, parâmetro ausente no contrato atualmente implementado em módulo anterior.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`: o teardown tenta remover `cko.db` ainda aberto por código legado de persistência.

Nenhuma falha foi registrada em `cko.core.documents`, Knowledge Object Foundation ou na nova API pública. Os dois módulos em falha estão fora do escopo autorizado e não foram alterados.

## Build oficial

`CKO_BUILD.cmd` foi executado com sucesso.

Artefato: `runtime/reports/build/cko-1.0.0-py3-none-any.whl`.

O wheel contém 209 arquivos e inclui o namespace documental.

## Compatibilidade

- Windows 10 e Windows 11;
- PowerShell 5.1;
- Python 3.13;
- UTF-8;
- Knowledge Object Foundation SPR-010;
- hierarquia consolidada de exceções do CORE.

## Itens deliberadamente não implementados

Não foram implementados IA, LLM, embeddings, Knowledge Graph, Semantic Search, ontologia, taxonomia, inferência, persistência, repositórios, Storage, indexação, cache, extração, OCR, parser ou lógica específica de formatos.

## Encerramento

A SPR-011 encerra-se no modelo documental canônico. Nenhuma Sprint posterior foi iniciada. A implementação aguarda homologação formal.
