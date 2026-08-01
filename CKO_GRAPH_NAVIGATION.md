# CKO Knowledge Graph Foundation — Navegação

## Serviço

`GraphNavigation` recebe um `CanonicalGraph` validado e fornece leitura estrutural. `GraphNavigator` é um alias público equivalente.

## Operações

| Operação | Resultado |
|---|---|
| `get_node` | nó identificado ou `GraphNavigationError` |
| `get_edges` | todas as arestas ou as incidentes em um nó |
| `neighbors` | nós adjacentes, sem duplicidade |
| `degree` | quantidade de arestas incidentes |
| `incoming` | arestas de entrada conforme a direção homologada |
| `outgoing` | arestas de saída conforme a direção homologada |
| `list_paths` | caminhos simples entre duas identidades |
| `connected_components` | componentes considerando conectividade estrutural |
| `maximum_depth` | maior distância mínima entre nós conectados |
| `width` | maior quantidade de nós em um mesmo nível estrutural |
| `traverse` | registro imutável de visita em largura ou profundidade |
| `statistics` | contagens e métricas derivadas em memória |

## Determinismo

Nós e arestas são ordenados por representação textual de `GraphId`. Empates de caminhos são resolvidos por comprimento e sequência de IDs. O resultado independe da ordem de iteração de dicionários e conjuntos internos.

## Direção

`incoming` e `outgoing` respeitam `RelationshipDirectionType`. Relações bidirecionais e não direcionadas são visíveis nos dois sentidos. Vizinhança, caminhos e componentes medem conexão estrutural e, por isso, consideram incidência em qualquer extremidade.

## Limites

`list_paths` aceita `max_depth` não negativo e enumera apenas caminhos simples, impedindo ciclos na mesma rota. O serviço não calcula relevância, centralidade semântica, inferência ou recomendação.
