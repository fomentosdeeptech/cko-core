# CKO Knowledge Graph Foundation — Guia de Modelos

## Identidade do grafo

`GraphId.new` cria UUID v4 lógico. `GraphId.canonical` deriva UUID v5 estável. `GraphIdentity` associa ID lógico, ID canônico, namespace, nome e versão semântica.

## Nós

`GraphFactory.create_node` aceita exclusivamente `KnowledgeObject` ou `CanonicalDocument`. O tipo é inferido e registrado em `GraphNodeType`. O ID canônico deriva do namespace, tipo e ID lógico do payload. O payload permanece a única fonte dos seus metadados.

## Arestas

`GraphFactory.create_edge` aceita exclusivamente `CanonicalRelationship`. O ID deriva do namespace e ID lógico do relacionamento. Origem, destino, direção, tipo e demais informações permanecem no relacionamento encapsulado.

## Grafo

`GraphFactory.create` recebe namespace, nome, autor, nós e arestas. Valores homologados podem ser fornecidos diretamente e são adaptados para `GraphNode` e `GraphEdge`. A factory cria identidade, metadados, descritor e executa validação completa.

`GraphFactory.from_parts` é a fronteira para reconstrução de um agregado completo, usada pelo serializador. Ela não ignora validação.

## Caminhos e travessias

`GraphPath` mantém uma sequência de nós e a sequência de arestas que conecta cada par consecutivo. O caminho é simples e exige `len(edge_ids) == len(node_ids) - 1`. `GraphTraversal` registra início, modo, ordem de visita, arestas percorridas e caminhos estruturais.

## Snapshots

`GraphSnapshot` contém UUID, grafo imutável, instante UTC, SHA-256, tipo e versão semântica. A factory calcula o digest a partir do JSON canônico do grafo.

## Estatísticas

`GraphStatistics` contém quantidade de nós, quantidade de arestas, densidade, grau médio, componentes, profundidade e largura. Para zero nós, todas as métricas são zero. Para menos de dois nós, a densidade é zero.

## Consultas e resultados

`GraphQuery` filtra por IDs, namespaces, tipos, autores, categorias, status e versões, com limite e deslocamento. `GraphResult` contém a página de nós, arestas induzidas e totais. Esses modelos não introduzem mecanismo de descoberta ou persistência.
