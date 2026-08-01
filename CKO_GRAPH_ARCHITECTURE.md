# CKO Knowledge Graph Foundation — Arquitetura

## Escopo

`cko.core.graph` é a representação canônica, imutável e integralmente em memória das conexões entre objetos homologados. O namespace não possui adaptador de armazenamento, dependência de banco de dados, cache, runtime, descoberta, mecanismo semântico ou componente de inteligência.

## Dependências permitidas

O módulo depende apenas de APIs públicas de:

- `cko.core.knowledge`, para `KnowledgeObject`;
- `cko.core.documents`, para `CanonicalDocument`;
- `cko.core.relationships`, para `CanonicalRelationship` e seus endpoints;
- `cko.core.exceptions`, para a raiz `CKOError`.

`GraphNode` contém uma referência a um único agregado homologado. `GraphEdge` contém uma referência a um único relacionamento canônico. Nenhum campo do objeto, documento ou relacionamento é reproduzido no grafo.

## Camadas internas

| Arquivo | Responsabilidade |
|---|---|
| `contracts.py` | schema, normalização, deep freeze, protocolos e envelope fechado |
| `identity.py` | `GraphId` e `GraphIdentity` |
| `metadata.py` | metadados UTC e atributos imutáveis |
| `models.py` | nós, arestas, caminhos, travessias, snapshots, estatísticas e agregados |
| `factory.py` | fronteira validada de criação |
| `validator.py` | invariantes de schema, unicidade e referências cruzadas |
| `serializer.py` | JSON UTF-8 canônico e SHA-256 |
| `navigation.py` | operações estruturais determinísticas |
| `indexes.py` | índices derivados somente em memória |

## Invariantes

- Todos os modelos públicos são dataclasses `frozen=True` e `slots=True`.
- Datas são normalizadas para UTC.
- Atributos arbitrários são congelados recursivamente.
- IDs de nós e arestas são derivados deterministicamente das identidades encapsuladas.
- Identidades de nós, arestas, payloads e relacionamentos são únicas.
- Todo endpoint de relacionamento deve resolver para um nó presente no mesmo grafo.
- Grafos vazios são válidos e produzem estatísticas zeradas.
- `CanonicalGraph` e `GraphCollection` só podem ser construídos por `GraphFactory`.

## Independência tecnológica

O grafo é um valor de domínio. Navegação, índices e estatísticas são projeções efêmeras calculadas sobre tuplas imutáveis. Nenhum estado é escrito fora da memória do processo.
