# CKO Knowledge Graph Foundation — API Pública

## Namespace

A API oficial reside em `cko.core.graph` e é reexportada por `cko.core`.

## Constantes e contratos

- `GRAPH_SCHEMA_VERSION`: versão `1.0` do schema fechado.
- `GRAPH_VERSION`: versão `1.0.0` da fundação.
- `GraphModel`: comportamento comum dos modelos.
- `GraphSerializer`: protocolo de serialização, desserialização e digest.
- `GraphValidatorContract`: protocolo de validação.

## Modelos

- Identidade: `GraphId`, `GraphIdentity`.
- Metadados: `GraphMetadata`, `GraphDescriptor`.
- Estrutura: `GraphNode`, `GraphEdge`, `GraphPath`, `GraphTraversal`.
- Agregados: `CanonicalGraph`, `GraphCollection`, `GraphSnapshot`.
- Leitura: `GraphQuery`, `GraphResult`, `GraphStatistics`.

## Enums

- `GraphStatus`
- `GraphTraversalMode`
- `GraphNodeType`
- `GraphEdgeType`
- `GraphSnapshotType`
- `GraphConsistency`

## Serviços

`GraphFactory` cria nós, arestas, grafos, coleções, caminhos, travessias, snapshots, estatísticas, consultas e resultados. `GraphValidator` valida modelos e referências cruzadas. `DeterministicGraphSerializer` implementa JSON canônico. `GraphNavigation` realiza navegação estrutural. `GraphIndexes` constrói índices imutáveis e executa filtros determinísticos.

## Índices

`GraphIndexes.build` deriva índices de identidade, namespace, tipo, autor, categoria, status e versão. `lookup` retorna IDs ordenados. `execute` aplica interseção entre dimensões e paginação por `GraphQuery`.

## Exceções

`GraphError`, `GraphValidationError`, `GraphSerializationError`, `GraphFactoryError`, `GraphIdentityError`, `GraphNavigationError` e `GraphIndexError` derivam de `CKOError`. `to_dict` fornece código, mensagem, modelo e detalhes seguros.
