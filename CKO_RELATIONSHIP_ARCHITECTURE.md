# CKO Relationship Architecture

## Status

Documento arquitetural da SPR-012 — Knowledge Relationship Foundation.

- Namespace: `cko.core.relationships`
- Schema: `1.0`
- Versão da fundação: `1.0.0`
- Compatibilidade: Windows 10, Windows 11, PowerShell 5.1, Python 3.13 e UTF-8

## Responsabilidade

A fundação representa significado declarado entre duas entidades canônicas. Ela não representa tabela, documento persistido, aresta física, índice ou estrutura de grafo. O agregado é independente de tecnologia e pode ser composto antes da escolha de qualquer mecanismo de persistência ou processamento.

## Agregado canônico

`CanonicalRelationship` reúne seis componentes obrigatórios:

1. `RelationshipIdentity`: identidade lógica, identidade canônica, namespace e chave semântica.
2. `RelationshipMetadata`: autoria, datas UTC, estado, origem e atributos imutáveis.
3. `RelationshipEndpoint` de origem.
4. `RelationshipEndpoint` de destino.
5. `RelationshipDescriptor`: tipo, direção, restrições, força e descrição.
6. `RelationshipVersion`: versão semântica, estado e linhagem declarada.

Evidências e pesos são coleções opcionais. A criação direta do agregado e da coleção é bloqueada por token interno. `RelationshipFactory` é a fronteira oficial de construção validada.

## Identidade

`RelationshipId` encapsula UUID. A identidade lógica é independente da identidade canônica. A identidade canônica usa UUID v5 sobre o namespace da fundação e a chave semântica determinística:

`source.namespace | source.object_id | target.namespace | target.object_id | type | direction | multiplicity`

Essa chave identifica a declaração sem impor armazenamento. Alterar origem, destino, tipo, direção ou multiplicidade produz outra identidade canônica.

## Endpoints

Um endpoint contém somente:

- UUID lógico do objeto;
- UUID canônico opcional;
- namespace;
- tipo de entidade;
- versão semântica;
- identidade externa opcional.

Não existe referência para Storage, Runtime, Discovery, Checkpoint, Unit of Work, SQLite, filesystem ou Knowledge Graph. Os adaptadores `from_knowledge_object` e `from_document` convertem exclusivamente contratos públicos homologados.

## Direção e restrições

Direção pode ser `directed`, `bidirectional` ou `undirected`. As restrições declaram unicidade, multiplicidade, bidirecionalidade, transitividade, simetria e reflexividade. A fundação valida coerência estrutural, mas não executa inferência, inversão, transitividade ou travessia.

Multiplicidades oficiais:

- `one_to_one`
- `one_to_many`
- `many_to_one`
- `many_to_many`

Simetria exige bidirecionalidade. Auto-relacionamento exige reflexividade declarada. Direção bidirecional ou não direcionada exige a restrição de bidirecionalidade correspondente.

## Evidência e peso

`RelationshipEvidence` registra origem, conteúdo de evidência, algoritmo gerador, confiança, timestamp UTC, autor, pipeline e versão. A evidência é opcional, mas uma instância declarada precisa conter ao menos um detalhe de origem.

`RelationshipWeight` oferece peso, confiança, relevância e probabilidade opcionais no intervalo fechado de zero a um. Esses valores são declarações; a fundação não os interpreta nem os combina.

## Validação

`RelationshipValidator` valida imutabilidade, slots, schema, discriminador, identidade canônica, endpoints, autores, estados, datas, direção, restrições, evidências duplicadas, duplicidade de relacionamentos e compatibilidade de auto-relacionamentos.

Todas as falhas públicas derivam de `CKOError`. Não existe raiz paralela de exceções.

## Limites arquiteturais

A SPR-012 não contém Knowledge Graph, semantic search, ontology, taxonomy engine, inference, embeddings, LLM, persistência, storage, indexação, cache, raciocínio semântico, travessia ou algoritmos de grafo.

O módulo é uma fundação de domínio pronta para futura composição por camadas posteriores, sem antecipar decisões dessas camadas.
