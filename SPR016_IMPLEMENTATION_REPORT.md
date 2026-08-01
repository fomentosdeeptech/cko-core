# SPR-016 Implementation Report — Knowledge Corpus Foundation

## Identificação e resultado

- Data: 2026-07-28 (America/Sao_Paulo).
- Baseline: CORE-001; ARCH-001 v1.2; SPR-008A–W/OA; SPR-009/009A; SPR-010–015.
- Gate prévio: A — APROVADA, preservado integralmente em `SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`.
- CORE SDK: `1.0.0`, mantido conforme o baseline consolidado.
- Responsabilidade: representação canônica, imutável, determinística, versionável e serializável da composição lógica de um corpus.

## Implementação entregue

Foi criado `cko.core.corpus` com onze módulos: `__init__.py`, `builder.py`, `contracts.py`, `enums.py`, `errors.py`, `factory.py`, `identity.py`, `models.py`, `operations.py`, `serializer.py` e `validator.py`. A única alteração de código fora do namespace foi a adição de reexports em `cko.core.__init__`, sem remover ou substituir símbolos existentes.

Os onze modelos canônicos são `CorpusId`, `CorpusIdentity`, `CorpusVersion`, `CorpusMemberReference`, `CorpusManifest`, `CorpusMetadata`, `KnowledgeCorpus`, `CorpusStatistics`, `CorpusReferenceChange`, `CorpusComparisonResult` e `CorpusSnapshot`. Todos são dataclasses frozen/slotted. `KnowledgeCorpus` exige `CorpusFactory`; mappings são congelados recursivamente.

`CorpusMemberCategory` admite somente Knowledge Object, Canonical Document, Canonical Relationship, Canonical Graph e Canonical Index. Um corpus vazio é válido. Query não possui categoria, é rejeitada por `reference_from_member` e nunca altera manifesto ou digest. Graph e Index são projeções opcionais; Inventory e InventorySnapshot não foram importados, estendidos ou reutilizados.

## Identidade, versionamento e digest

O namespace UUID exclusivo é `0d0ee5a8-e17e-5ae1-b9e4-7801131bf190`. `CorpusId.canonical` usa UUIDv5 sobre namespace e nome normalizados. A identidade independe de caminho, banco, sessão, processo, relógio e infraestrutura.

Há distinção formal entre esquema (`1.0`), API da fundação (`1.0.0`), serialização (`1.0`), versão lógica/revisão (`CorpusVersion`) e versão individual (`member_version`). Operações estruturais retornam novo corpus e incrementam a revisão.

O digest de composição usa SHA-256 sobre JSON canônico contendo esquema, versão de serialização, identidade, versão lógica, manifesto ordenado e metadados estruturais. O próprio digest e timestamps de snapshot são excluídos. `CorpusFactory.from_parts` e `CorpusValidator` recalculam o valor.

## Canonicalização, serialização e operações

`DeterministicCorpusSerializer` usa JSON UTF-8, Unicode preservado, chaves ordenadas, separadores mínimos, números finitos, discriminadores fechados, conjuntos exatos de campos e rejeição de entrada não canônica. Round-trip integral foi validado para todos os modelos.

Foram entregues `add_member`, `remove_member`, `contains_member`, `find_member`, `filter_members`, `compare_corpora` e `corpus_statistics`, além de `CorpusOperations`. Comparações distinguem membros adicionados, removidos, preservados e alterados, com flags próprias para versão e digest. `CorpusBuilder` produz novos agregados sem I/O, resolução ou estado externo. Snapshots são exclusivamente representacionais e estatísticas derivam somente do manifesto.

## Integração SPR-010–015

As referências materializadas usam exclusivamente APIs públicas de `knowledge`, `documents`, `relationships`, `graph` e `index`. `query` é conhecido apenas para rejeitar `CanonicalQuery`. Nenhuma fundação anterior importa `corpus`; não há ciclo nem dependência reversa. Documento e seu Knowledge Object podem coexistir porque categoria e identidade tipada fazem parte da chave de pertencimento.

## API pública

`cko.core.corpus.__all__` contém 48 símbolos únicos. A fachada `cko.core` reexporta 42 símbolos não ambíguos, sem duplicatas em seu `__all__`: quatro constantes, onze modelos, categoria fechada, factory, builder, validator, serializer, operações, utilitários de digest/referência e exceções. Protocolos, `CorpusModel` e `corpus_digest_payload` permanecem no namespace especializado. O inventário nominal está em `CKO_CORPUS_API.md`.

## Testes, arquitetura e cobertura

- Suíte dedicada: **28/28 aprovados**.
- Integração SPR-010–016: **175/175 aprovados**.
- Regressão oficial: **880 coletados; 878 aprovados; 2 falhas históricas; 0 falhas novas**.
- Falha histórica 1: `collect_metadata` não aceita `calculate_hash`.
- Falha histórica 2: handle Windows de `cko.db` permanece aberto no teardown do SPR-005A.
- Cobertura: **98% de linhas**, **95% de branches**, **97% combinada**; 726 statements, 14 não cobertos, 210 branches e 11 não cobertos/parciais.
- Auditoria automatizada: 11 módulos compilados; 48/48 símbolos públicos únicos; 42 reexports raiz; zero duplicatas raiz; zero imports proibidos; zero imports reversos.

A suíte cobre corpus vazio e heterogêneo, identidade, UUID, imutabilidade, slots, hashing, manifesto, ordem, duplicidades, operações puras, comparação, estatísticas, snapshots, versões, digest, serializer fechado, round-trip, rejeições, integrações SPR-010–015, Query excluída, ausência de I/O, dependências proibidas, ciclos e exports.

## Build e wheel

`CKO_BUILD.cmd` terminou com exit code zero. Artefato: `runtime/reports/build/cko-1.0.0-py3-none-any.whl`, **416.943 bytes**, **265 entradas**, SHA-256 **`32EC3386BFDC1377BF85745F3529FA019AC820158F50E1A480BEA4B03D9A1D51`**.

O wheel contém os onze módulos `cko/core/corpus/*.py`, nenhum teste e nenhum `.pyc`/`.pyo`. A primeira tentativa de instalação foi bloqueada pelo diretório temporário global do sandbox; a repetição autorizada fora do sandbox instalou `cko-1.0.0` com sucesso. Smoke test isolado com `python -I` confirmou CORE `1.0.0`, Corpus `1.0.0`, 48 símbolos, criação/digest e alias raiz `KnowledgeCorpus`.

## Arquivos e preservação

Criados: os onze módulos do namespace; `tests/test_knowledge_corpus_foundation_spr016.py`; `SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`; este relatório; `CKO_CORPUS_ARCHITECTURE.md`; `CKO_CORPUS_API.md`; `CKO_CORPUS_MODEL_GUIDE.md`; `CKO_CORPUS_SERIALIZATION.md`; `CKO_CORPUS_OPERATIONS.md`.

Modificados: `src/cko/core/__init__.py`, `CKO_CORE_V1_PUBLIC_API_CATALOG.md` e `CKO_CORE_V1_DEPENDENCY_MATRIX.md`. As alterações preexistentes em `.gitignore`, `pyproject.toml` e os numerosos arquivos não rastreados foram preservadas. Nenhum commit, push ou PR foi realizado.

## Riscos, limitações e exclusões

As duas falhas legadas permanecem fora do escopo. Categorias futuras exigem evolução explícita do schema. Não há resolução de referências ou verificação de existência física. A fundação não contém Runtime, persistência, Storage, Repository, Unit of Work, Checkpoint, Discovery, cache, filesystem, banco, rede, serviços, IA, LLM, embeddings, busca, inferência, ontologia, RAG, agentes, execução de Query, atualização de Index, geração de Graph, merge, sincronização ou migração.

Nenhuma Sprint posterior foi iniciada.

**SPR-016 concluída e pronta para auditoria e homologação formal.**
