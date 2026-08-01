SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md
Gate arquitetural: A — APROVADA
Knowledge Corpus constitui uma fundação nova e não duplicada. A SPR-016 pode ser especificada, mas esta auditoria não autoriza sua implementação.
1. Escopo auditado
Foram examinados, em modo exclusivamente read-only:
namespaces públicos e fachada cko.core;
modelos, identidades, factories, builders, validators e serializers;
coleções, snapshots, digests e operações estruturais;
documentação arquitetural e catálogos públicos;
testes dedicados das SPR-010 a SPR-015;
relatórios de implementação;
contratos anteriores potencialmente sobrepostos, especialmente Inventory e Composition Root.
Os namespaces efetivos são:
cko.core.knowledge;
cko.core.documents;
cko.core.relationships;
cko.core.graph;
cko.core.query;
cko.core.index;
aliases publicados em cko.core.
Não existem os namespaces singulares cko.core.object, document ou relationship.
2. Inventário dos contratos públicos relevantes
Fundação	Contratos com possível relação ao corpus	Limite arquitetural
SPR-010	KnowledgeObject, KnowledgeCollection, KnowledgeSnapshot, KnowledgeObjectId, KnowledgeObjectIdentity	Unidade individual de conhecimento; coleção homogênea de objetos completos; snapshot de um único objeto
SPR-011	CanonicalDocument, DocumentCollection, DocumentId, DocumentIdentity	Documento canônico associado a um KnowledgeObject; coleção homogênea
SPR-012	CanonicalRelationship, RelationshipCollection, RelationshipEndpoint, RelationshipId	Relação binária declarada entre duas entidades; não agrega acervo
SPR-013	CanonicalGraph, GraphCollection, GraphSnapshot, GraphNode, GraphEdge, GraphId	Representação relacional composta por objetos/documentos e relações
SPR-014	CanonicalQuery, QueryCollection, QueryResult, QueryId	Intenção de consulta; não delimita nem armazena composição
SPR-015	CanonicalIndex, IndexReference, IndexCollection, IndexSnapshot, IndexId	Projeção indexada por chaves contendo referências mínimas
Fundação anterior	Inventory, InventoryCollection, InventorySnapshot	Inventário de Asset; parcialmente semelhante, mas anterior e incompatível com os agregados SPR-010–015
Composição técnica	CompositionRoot, CoreComposition	Montagem de serviços e infraestrutura; não é composição de conhecimento

A fachada publica essas famílias e seus aliases em [cko/core/__init__.py (line 375)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/__init__.py:375), [cko/core/__init__.py (line 723)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/__init__.py:723), [cko/core/__init__.py (line 780)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/__init__.py:780) e [cko/core/__init__.py (line 888)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/__init__.py:888).
3. Matriz de responsabilidades SPR-010–015
Sprint	Unidade representada	Identidade própria	Composição	Snapshot/digest	Equivalência com Corpus
SPR-010	Unidade de conhecimento	Sim	Conteúdo, metadados, relações locais e contextos	Snapshot de um objeto	Baixa
SPR-011	Documento canônico	Sim	Um KnowledgeObject, representações e versões	Digest serializável, sem snapshot de coleção	Baixa
SPR-012	Relação semântica	Sim	Dois endpoints, evidências e pesos	Digest do modelo	Baixa
SPR-013	Projeção relacional	Sim	Nós de objetos/documentos e arestas de relações	Snapshot e digest de um grafo	Parcial
SPR-014	Intenção de consulta	Sim	Filtros, projeções, paginação e alvos	Digest da consulta	Nenhuma
SPR-015	Projeção indexada	Sim	Chaves e referências a cinco tipos canônicos	Snapshot e digest de um índice	Parcial

4. Sobreposições encontradas
4.1 Coleções homogêneas
As coleções existentes apenas agrupam instâncias completas de um único tipo:
KnowledgeCollection.objects: [knowledge/models.py (line 135)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/knowledge/models.py:135);
DocumentCollection.documents: [documents/models.py (line 218)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/documents/models.py:218);
RelationshipCollection.relationships: [relationships/models.py (line 114)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/relationships/models.py:114);
GraphCollection.graphs: [graph/models.py (line 230)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/graph/models.py:230);
IndexCollection.indexes: [index/models.py (line 243)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/index/models.py:243).
Elas não possuem, em conjunto, identidade canônica de coleção, versão de composição, referências heterogêneas nem digest integral da composição.
4.2 InventorySnapshot
É o contrato parcialmente equivalente mais próximo. Ele possui:
inventory_id;
nome;
revisão;
coleção imutável;
serialização determinística.
Evidência: [inventory/models.py (line 96)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/inventory/models.py:96).
A equivalência termina aí:
aceita exclusivamente InventoryItem contendo Asset;
não aceita diretamente KnowledgeObject, CanonicalDocument, CanonicalRelationship, CanonicalGraph ou CanonicalIndex;
incorpora os ativos completos, em vez de declarar composição por referências;
não possui digest da composição;
representa inventário de ativos, não acervo semântico;
estendê-lo para os contratos SPR-010–015 misturaria a taxonomia legada de Asset com a camada semântica homologada.
Logo, é precedente arquitetural reutilizável como referência conceitual, mas não como fundação a ser ampliada.
5. Análise específica de KnowledgeGraph
CanonicalGraph contém identidade, metadados, descritor, nós e arestas [graph/models.py (line 172)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/graph/models.py:172).
Não funciona como agregador raiz do conhecimento porque:
GraphNode aceita somente KnowledgeObject ou CanonicalDocument [graph/models.py (line 30)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/graph/models.py:30);
relacionamentos só aparecem como arestas;
índices, consultas e outros grafos não podem ser membros;
todo relacionamento precisa resolver para nós presentes no mesmo grafo [graph/validator.py (line 42)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/graph/validator.py:42);
a finalidade documentada é representar conexões, não pertencimento ao acervo;
nós incorporam agregados completos, em vez de referências mínimas.
GraphSnapshot captura um único CanonicalGraph e seu digest [graph/models.py (line 199)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/graph/models.py:199). Esse digest prova a integridade do grafo, não da totalidade de um corpus.
Conclusão: o grafo é uma projeção relacional do corpus. Torná-lo corpus violaria sua responsabilidade original.
6. Análise específica de KnowledgeIndex
A documentação é explícita: o índice é uma camada de organização por referências e “não é conhecimento”; também nunca armazena a entidade indexada completa [CKO_INDEX_ARCHITECTURE.md (line 5)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/CKO_INDEX_ARCHITECTURE.md:5).
IndexReference possui namespace, ID canônico, tipo, versão, discriminador e checksum opcional [index/models.py (line 86)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/index/models.py:86). Entretanto:
cada índice depende de uma IndexDefinition;
membros existem subordinados a chaves;
o conjunto é limitado aos alvos declarados pela definição;
os alvos são objetos, documentos, relações, grafos e consultas — não outros índices;
ausência em um índice não significa ausência no acervo;
diferentes índices podem cobrir subconjuntos diferentes do mesmo corpus.
O digest de CanonicalIndex cobre definição, versão e entradas ordenadas [index/factory.py (line 66)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/index/factory.py:66). IndexSnapshot registra somente a origem e integridade de um índice [index/models.py (line 316)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/index/models.py:316).
Conclusão: KnowledgeIndex é exclusivamente uma projeção indexada. Usá-lo como manifesto de corpus seria abuso do contrato.
7. Snapshots e digests
Contrato	Unidade capturada	Digest integral de corpus?
KnowledgeSnapshot	Um KnowledgeObject completo	Não
GraphSnapshot	Um CanonicalGraph completo	Não
IndexSnapshot	Estado de um CanonicalIndex	Não
InventorySnapshot	Uma revisão de ativos	Não possui digest
Checkpoint snapshots	Estado operacional/persistente	Fora do domínio e explicitamente proibido

Os serializers das seis fundações usam JSON canônico e SHA-256, mas cada serializer possui envelope fechado para sua própria família. Exemplos: [knowledge/serializer.py (line 35)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/knowledge/serializer.py:35), [graph/serializer.py (line 43)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/graph/serializer.py:43) e [index/serializer.py (line 45)](G:/Meu Drive/01 - CKO Platform/01_Projects/CKO/CORE/src/cko/core/index/serializer.py:45).
Nenhum calcula digest sobre uma composição heterogênea integral do conhecimento.
8. Contratos reutilizáveis
Podem ser reutilizados pela especificação da SPR-016:
identidades canônicas dos membros: KnowledgeObjectId, DocumentId, RelationshipId, GraphId e IndexId;
versões e IDs canônicos publicados por cada agregado;
discriminadores públicos dos modelos;
padrão de dataclasses congeladas e com slots;
padrão de factory obrigatória, validator e serializer determinístico;
algoritmos conceituais de canonicalização e SHA-256;
IndexReference como referência de desenho para uma referência mínima, sem reutilizá-lo literalmente como referência universal;
InventorySnapshot como precedente de identidade, nome e revisão de um conjunto lógico.
9. Contratos que não devem ser reutilizados como Corpus
KnowledgeCollection: aceita somente objetos completos.
DocumentCollection: aceita somente documentos completos.
RelationshipCollection: aceita somente relações completas.
GraphCollection: coleção de grafos, sem identidade ou digest da coleção.
QueryCollection: coleção de intenções de consulta.
IndexCollection: coleção de índices, não manifesto dos itens indexados.
GraphNode: apenas objeto/documento e com payload embutido.
RelationshipEndpoint: semântica específica de relação binária.
IndexReference: depende de IndexTarget e não admite CanonicalIndex.
InventorySnapshot: trabalha com Asset, não com os agregados semânticos homologados.
CompositionRoot: compõe serviços e infraestrutura, não conhecimento.
10. Colisões e riscos
Risco	Avaliação	Restrição recomendada
Confundir corpus com grafo	Alto	Declarar Graph como projeção opcional do corpus
Confundir corpus com índice	Alto	Declarar Index como projeção derivada e não autoridade de pertencimento
Colisão com KnowledgeCollection	Média	Manter o nome distinto KnowledgeCorpus; não criar KnowledgeCorpusCollection sem necessidade comprovada
Colisão de Snapshot	Média	Usar nomes explícitos, como CorpusSnapshot, se o contrato for realmente necessário
Reutilizar UUID namespace existente	Alto	Reservar namespace UUID próprio para Corpus
Misturar versão do corpus com versões dos membros	Alto	Separar corpus_version/revisão da versão referenciada de cada membro
Digest ambíguo	Alto	Definir digest sobre referências canônicas ordenadas e tipadas, não sobre projeções ou timestamps
Duplicidade entre documento e seu KnowledgeObject associado	Alto	Especificar se ambos podem pertencer e como são distinguidos
Dependência circular	Alto	Corpus deve depender das identidades públicas; Graph e Index não devem passar a depender de Corpus na mesma fundação
Alias na fachada raiz	Baixo	Auditar cko.core.__all__ e publicar nomes sem substituir aliases homologados

11. Respostas às questões arquiteturais
Existe contrato público equivalente?
Não.

Existe contrato parcialmente equivalente?
Sim: InventorySnapshot, CanonicalGraph/GraphSnapshot, CanonicalIndex/IndexSnapshot e as coleções homogêneas. Nenhum cobre a responsabilidade integral.

KnowledgeGraph funciona como agregador raiz?
Não. Ele agrega somente a projeção relacional e exige fechamento dos endpoints no próprio grafo.

KnowledgeIndex representa a totalidade do conhecimento?
Não. Representa somente uma projeção indexada segundo definição, campos e chaves.

Algum Snapshot, Manifest, Registry, Collection, Catalog, Bundle, Set ou Context ocupa a responsabilidade?
Não integralmente. InventorySnapshot é o caso parcial mais próximo. Registries e Composition Root são técnicos; contexts são locais; collections são homogêneas.

Knowledge Corpus produziria duplicidade conceitual?
Não, desde que seja a autoridade explícita de pertencimento por referências e não replique Graph, Index ou Inventory.

A lacuna pode ser resolvida numa fundação existente?
Não legitimamente. A ampliação quebraria a responsabilidade única de Graph, Index, Inventory ou Knowledge Object.

Há riscos de colisão?
Sim, principalmente em identidade, versões, digest, snapshots, documento versus objeto associado e aliases públicos. São controláveis na especificação.

Quais contratos podem ser reutilizados?
IDs canônicos dos componentes, versões, discriminadores e padrões de imutabilidade, factory, validação, serialização e digest.

Quais não podem ser reutilizados?
Coleções homogêneas, Graph como raiz, Index como manifesto, IndexReference como referência universal, RelationshipEndpoint, Inventory e Composition Root.

12. Lacuna confirmada
O baseline não possui contrato que simultaneamente:
identifique canonicamente um conjunto lógico de conhecimento;
declare pertencimento heterogêneo por referências;
permita múltiplos conjuntos independentes;
versione a composição;
produza snapshot da composição;
calcule digest da composição integral;
diferencie autoridade de pertencimento de suas projeções Graph e Index.
Essa é uma lacuna arquitetural real.
13. Decisão e recomendação final
Resultado: A — APROVADA.
Knowledge Corpus constitui fundação nova e não duplicada. A SPR-016 pode ser especificada.
Não há ajuste obrigatório de nome ou mudança da responsabilidade candidata antes da especificação. A especificação, porém, deve preservar estes guardrails:
composição heterogênea por referências canônicas;
autoridade explícita de pertencimento;
identidade, versão e digest próprios;
ordenação canônica independente da ordem de entrada;
Graph e Index tratados como membros/projeções, nunca como totalidade implícita;
nenhuma extensão de Inventory;
nenhuma dependência de Runtime, persistência, Storage, Repository, Discovery, Checkpoint ou demais elementos proibidos.
Nenhum teste foi executado, pois isso poderia criar caches ou artefatos e violar o modo read-only. As evidências de testes foram inspecionadas estaticamente nos arquivos dedicados e nos relatórios homologados.
Confirmação de integridade: nenhum arquivo foi criado, editado, removido ou renomeado por esta auditoria. O arquivo físico SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md não foi criado devido à proibição expressa de alterar documentação. O worktree já possuía alterações e numerosos arquivos não rastreados anteriores à auditoria; esse estado permaneceu inalterado.
