# SPR-017 — Auditoria Arquitetural Pré-Implementação

## 1. Identificação da auditoria

- **Auditoria:** SPR-017 — Knowledge Provenance Foundation.
- **Data:** 2026-07-28, fuso `America/Sao_Paulo`.
- **Natureza:** gate arquitetural obrigatório, anterior à especificação e à implementação.
- **Modo:** inspeção em leitura; a criação deste relatório foi a única alteração autorizada no repositório.
- **Baseline declarado:** CORE-001; ARCH-001 v1.2; SPR-008A–W e SPR-008OA; SPR-009/009A; SPR-010–016; CORE SDK público 1.0.0.
- **Resultado único:** **B — APROVADA COM AJUSTES**.
- **Efeito do parecer:** a necessidade de uma fundação independente está confirmada, mas a SPR-017 **não deve ser especificada com o nome contratual e a responsabilidade candidatos sem os ajustes obrigatórios deste relatório**. Incorporados esses ajustes ao termo de especificação, a Sprint pode ser especificada. Nenhuma implementação é autorizada.

## 2. Sumário executivo

Não existe no baseline um contrato público que represente integralmente proveniência. Existe, porém, sobreposição parcial relevante e já homologada:

1. a SPR-010 publica exatamente o símbolo `KnowledgeProvenance`, serializável e contido em `KnowledgeMetadata.provenances`;
2. a SPR-010 também publica `KnowledgeContent.derived_from`, autoria, criação, fonte, referências, identidade, versão e snapshots;
3. a SPR-011 publica `DocumentAuthor`, `DocumentSource`, múltiplas fontes, versões e integridade;
4. a SPR-012 publica tipos `DERIVED_FROM` e `GENERATED_FROM`, endpoints tipados, identidade própria, versão, evidências, digest e serialização determinística;
5. a SPR-013 pode projetar esses relacionamentos como arestas, mas não é autoridade de proveniência;
6. as SPR-015 e SPR-016 registram referências, versões, digests e snapshots estruturais, não origem semântica;
7. a arquitetura legada possui `Origin`, `DiscoveryEvidence`, `IdentityEvidence`, eventos e snapshots de inventário, todos com responsabilidades diferentes e insuficientes.

A lacuna é real: nenhum contrato distingue formalmente **entidade de proveniência, ator responsável, atividade de derivação e declaração/evidência**, nenhum contrato forma uma cadeia canônica de declarações heterogêneas, e nenhum oferece identidade/digest próprios da cadeia como responsabilidade de domínio. A lacuna não cabe legitimamente em Object, Document, Relationship, Graph ou Corpus sem ampliar indevidamente suas responsabilidades.

Entretanto, criar uma nova classe raiz chamada `KnowledgeProvenance` ou repetir campos de fonte, autoria, derivação e evidência produziria colisão pública e duplicidade semântica. Recomenda-se ajustar o nome da fundação para **SPR-017 — Knowledge Provenance Statement Foundation** e sua responsabilidade para:

> Definir a representação canônica, imutável, determinística, versionável e serializável de declarações de proveniência que vinculem referências a entidades de conhecimento, atores responsáveis e atividades declaradas de origem ou derivação, incluindo evidências e encadeamento lógico, sem executar, capturar ou verificar externamente tais atividades.

“Ator” acima é papel conceitual de proveniência; não significa agente de software ou IA. Os nomes de modelos citados neste parecer descrevem papéis arquiteturais mínimos, não uma API pública definitiva.

## 3. Baseline examinado e confirmação

### 3.1 Confirmações diretas

| Item | Evidência direta | Resultado |
|---|---|---|
| Versão pública | `pyproject.toml:1-8`; `src/cko/core/__init__.py:886` | pacote e fachada em `1.0.0` |
| Namespace Corpus | `src/cko/core/corpus/__init__.py:1-40` | 48 entradas únicas em `__all__` |
| Modelos Corpus | `src/cko/core/corpus/identity.py:16-59`; `src/cko/core/corpus/models.py:39-247` | 11 modelos canônicos, frozen/slotted |
| Reexports Corpus | `src/cko/core/__init__.py:923-956` | 42 símbolos do Corpus reexportados na raiz |
| Suíte dedicada SPR-016 | execução de `tests/test_knowledge_corpus_foundation_spr016.py` | **28/28 aprovados** |
| Integração SPR-010–016 | execução dos sete testes dedicados | **175/175 aprovados** |
| Regressão | execução de `tests -q` fora da árvore de trabalho | **880 coletados; 878 aprovados; 2 falhas históricas** |
| Wheel oficial | `runtime/reports/build/cko-1.0.0-py3-none-any.whl` | 416.943 bytes, 265 entradas |
| SHA-256 oficial | `Get-FileHash` sobre o wheel oficial | `32EC3386BFDC1377BF85745F3529FA019AC820158F50E1A480BEA4B03D9A1D51` |
| Conteúdo do wheel | inspeção ZIP direta | 11 módulos Corpus; nenhum teste; nenhum `.pyc`/`.pyo` |
| Correspondência wheel/source | SHA-256 de entradas versus arquivos | `knowledge/metadata.py`, `relationships/models.py`, `corpus/models.py` e `core/__init__.py` idênticos |
| Metadata do wheel | `cko-1.0.0.dist-info/METADATA` | nome `cko`, versão `1.0.0`, Python `>=3.13` |
| API carregada | import isolado do source correspondente ao wheel | CORE 1.0.0; Corpus 1.0.0; raiz com 610 símbolos únicos |

As duas falhas reproduzidas são as mesmas documentadas em `SPR016_IMPLEMENTATION_REPORT.md:43-49`: `collect_metadata` não aceita `calculate_hash`, e um handle Windows de `cko.db` permanece aberto no teardown do SPR-005A. Nenhuma falha nova foi observada.

### 3.2 Evidência registrada, não recalculada nesta auditoria

`SPR016_IMPLEMENTATION_REPORT.md:48` registra 98% de linhas, 95% de branches e 97% combinada, com 726 statements, 14 não cobertos, 210 branches e 11 não cobertos/parciais. Não existe em `runtime/reports` um diretório bruto `coverage_spr016` preservado; portanto, os percentuais foram confirmados como evidência homologada no relatório, mas não foram recalculados. O build com exit code zero e a instalação limpa/smoke test também estão registrados em `SPR016_IMPLEMENTATION_REPORT.md:53-57`; esta auditoria não executou novo build, conforme a restrição expressa, e confirmou diretamente o wheel e seu conteúdo.

### 3.3 Divergências documentais

1. `CKO_CORE_V1_PUBLIC_API_CATALOG.md:5-23` ainda declara 334 símbolos na raiz e cobre principalmente A–W. O código atual possui 610 entradas únicas em `cko.core.__all__`. O arquivo contém apenas adendo de Corpus em `CKO_CORE_V1_PUBLIC_API_CATALOG.md:134-138` e não inventaria nominalmente SPR-010–015.
2. `CKO_CORE_V1_PUBLIC_API_CATALOG.md:132` ainda afirma que pacote e `cko.core.__version__` são 0.1.0, enquanto `pyproject.toml:1-8`, `src/cko/core/__init__.py:886` e o wheel oficial confirmam 1.0.0.
3. `CKO_CORE_V1_DEPENDENCY_MATRIX.md:7-20` não possui colunas principais para SPR-010–015; apenas Corpus recebeu adendo em `CKO_CORE_V1_DEPENDENCY_MATRIX.md:66-70`.

Essas divergências não alteram a conclusão sobre o código homologado, mas tornam obrigatória a atualização dos inventários antes do fechamento da especificação SPR-017.

## 4. Metodologia

Foram confrontados:

- namespaces e `__all__` especializados e da fachada `cko.core`;
- modelos, enums, identidades, factories, validators, builders, operações e serializers;
- documentação arquitetural e de API das SPR-010–016;
- relatórios de implementação, certificação, dependências e API pública;
- testes dedicados e de integração;
- arquitetura legada de Identity, Metadata, Models, Inventory e Discovery;
- wheel oficial, seu hash, metadata e conteúdo;
- execução das suítes existentes necessária para confirmar a baseline.

A busca por `cko.core.object`, `cko.core.document` e `cko.core.relationship` foi ajustada aos namespaces efetivos: `cko.core.knowledge`, `cko.core.documents` e `cko.core.relationships`. Não foi inferida equivalência apenas por nomes; cada campo foi avaliado pela validação, serialização, teste e responsabilidade documentada.

## 5. Inventário dos contratos públicos relevantes

| Fundação | Namespace efetivo | Superfície relevante à auditoria | Conclusão |
|---|---|---|---|
| SPR-010 | `cko.core.knowledge` | `KnowledgeProvenance`, `KnowledgeMetadata`, `KnowledgeContent`, `KnowledgeReference`, `KnowledgeObjectIdentity`, `KnowledgeVersion`, `KnowledgeSnapshot`, `KnowledgeRelationship` | maior sobreposição; proveniência local e derivação simples, não fundação completa |
| SPR-011 | `cko.core.documents` | `DocumentAuthor`, `DocumentSource`, `DocumentMetadata`, `DocumentVersion`, `DocumentIntegrity`, `DocumentIdentity` | autoria, múltiplas fontes, ancestral de versão e integridade documental |
| SPR-012 | `cko.core.relationships` | `CanonicalRelationship`, `RelationshipEndpoint`, `RelationshipType`, `RelationshipEvidence`, `RelationshipMetadata`, `RelationshipVersion` | declaração binária genérica com derivação/evidência; não modelo formal de proveniência |
| SPR-013 | `cko.core.graph` | `GraphNode`, `GraphEdge`, `CanonicalGraph`, `GraphPath`, `GraphSnapshot` | projeção de objetos/documentos/relacionamentos homologados |
| SPR-014 | `cko.core.query` | identidade, metadata, intenção e resultados | nenhum contrato de proveniência; apenas intenção de consulta |
| SPR-015 | `cko.core.index` | `IndexReference`, `IndexVersion`, `IndexSnapshot`, digests | projeção indexada e integridade estrutural |
| SPR-016 | `cko.core.corpus` | `CorpusMemberReference`, `CorpusManifest`, `CorpusVersion`, `CorpusSnapshot`, digest | pertencimento e composição; não origem dos membros |
| legado | `cko.core.identity`, `metadata`, `models`, `inventory`, `discovery` | `Origin`, `UniversalMetadata`, documento legado, eventos, inventário, evidências observacionais/de identidade | contratos técnicos/operacionais com outra responsabilidade |

Os símbolos de SPR-010–016 são reexportados seletivamente pela fachada em `src/cko/core/__init__.py:375-447` e `src/cko/core/__init__.py:723-956`. `KnowledgeProvenance` já ocupa o nome raiz em `src/cko/core/__init__.py:396`.

## 6. Matriz de responsabilidades SPR-010 a SPR-016

| Sprint | Autoridade exclusiva | Origem/autoria | Derivação | Cadeia formal | Identidade/digest próprios | Adequação para absorver SPR-017 |
|---|---|---:|---:|---:|---:|---|
| 010 Object | unidade canônica de conhecimento | parcial | `derived_from` e provenance local | não | do objeto/versão/snapshot | não; ampliaria metadado local para domínio transversal |
| 011 Document | unidade documental lógica | parcial forte | apenas ancestral de versão | não | documento/versão/integridade | não; excluiria entidades não documentais |
| 012 Relationship | significado binário declarado | parcial | tipos derivados/gerados | só por composição externa | relação/versão/digest | não integralmente; faltam papéis e semântica de proveniência |
| 013 Graph | projeção relacional em memória | herdada dos payloads | projeta relações | caminhos estruturais | grafo/snapshot/digest | não; torná-lo autoridade viola seu papel de projeção |
| 014 Query | intenção canônica de consulta | metadata de criação | não | não | query/digest | não |
| 015 Index | projeção indexada | metadata de criação | `parent_digest` estrutural | não | índice/versão/snapshot/digest | não |
| 016 Corpus | composição e pertencimento | não | alterações de referências | não | corpus/snapshot/digest | não; origem não é pertencimento |

## 7. Inventário de campos relacionados à proveniência

### 7.1 Knowledge Object

| Contrato/campo | Localização | Semântica confirmada | Limite |
|---|---|---|---|
| `KnowledgeObjectIdentity.origin` | `src/cko/core/knowledge/identity.py:54-63` | texto integrante da identidade descritiva | não referencia entidade/atividade/ator |
| `KnowledgeProvenance.*` | `src/cko/core/knowledge/metadata.py:62-88` | origem, pipeline, processo gerador, fonte original, timestamp, versão do pipeline e tipo de fonte | sem identidade própria, evidência, relações tipadas ou cadeia |
| `KnowledgeMetadata.author/creator/source/provenances` | `src/cko/core/knowledge/metadata.py:119-178` | metadados descritivos e múltiplos registros de proveniência | restritos ao agregado Knowledge Object |
| `KnowledgeReference` | `src/cko/core/knowledge/metadata.py:34-59` | referência textual e `target_object_id` opcional | não declara proveniência |
| `KnowledgeContent.derived_from` | `src/cko/core/knowledge/models.py:26-66` | uma ou várias IDs de Knowledge Object de origem para conteúdo `DERIVED` | um salto, um tipo de entidade, sem atividade/evidência/ator |
| `KnowledgeVersion.parent_version` | `src/cko/core/knowledge/versioning.py:17-61` | ancestralidade de versões do mesmo objeto | sucessão de versão, não derivação semântica |
| `KnowledgeSnapshot` | `src/cko/core/knowledge/models.py:156-181` | estado integral do objeto com hash validado | estado representacional, não cadeia de origem |

### 7.2 Document

| Contrato/campo | Localização | Semântica confirmada | Limite |
|---|---|---|---|
| `DocumentAuthor` | `src/cko/core/documents/metadata.py:35-48` | pessoa/organização/papel descritivos | sem identidade canônica de ator ou declaração de atribuição |
| `DocumentSource` | `src/cko/core/documents/metadata.py:51-70` | tipo, identificador, origem, ID externa e recuperação | fonte documental, não derivação |
| `DocumentMetadata.sources` | `src/cko/core/documents/metadata.py:73-129` | múltiplas fontes e autoria | suficiente para descrição local, não para cadeia transversal |
| `DocumentVersion.parent_version` | `src/cko/core/documents/models.py:84-113` | ancestral de versão documental | não prova origem semântica |
| `DocumentIntegrity` | `src/cko/core/documents/models.py:135-160` | SHA-256, assinatura declarada e estado de integridade | integridade não equivale a proveniência |

### 7.3 Relationship

| Contrato/campo | Localização | Semântica confirmada | Limite |
|---|---|---|---|
| `DERIVED_FROM`, `GENERATED_FROM` | `src/cko/core/relationships/enums.py:6-27` | vocabulário semântico de relações binárias | rótulo não cria modelo de proveniência |
| `RelationshipEndpoint` | `src/cko/core/relationships/identity.py:70-132` | UUID, namespace, tipo, versão, IDs canônica/externa; adaptadores para Object/Document | não distingue entidade, ator e atividade |
| `RelationshipEvidence` | `src/cko/core/relationships/metadata.py:94-121` | fonte, evidência, algoritmo, confiança, timestamp, autor, pipeline e versão | evidência da relação, sem identidade/digest próprio de uma declaração de proveniência |
| `CanonicalRelationship` | `src/cko/core/relationships/models.py:82-111` | relação binária com identidade, metadata, endpoints, descriptor, versão, evidências e pesos | sem restrições de causalidade/proveniência, n-aridade ou papéis formais |
| digest/round-trip | `src/cko/core/relationships/serializer.py:52-84` | integridade determinística de qualquer modelo relacional | não acrescenta semântica de origem |

### 7.4 Graph, Index e Corpus

| Contrato/campo | Localização | Semântica confirmada | Limite |
|---|---|---|---|
| `GraphEdge.relationship` | `src/cko/core/graph/models.py:56-77` | encapsula uma `CanonicalRelationship` sem reproduzi-la | Graph apenas projeta |
| `GraphPath` | `src/cko/core/graph/models.py:80-100` | caminho simples estrutural | não é cadeia de proveniência validada |
| `GraphSnapshot.digest` | `src/cko/core/graph/models.py:199-227` | integridade do estado do grafo | não prova origem |
| `IndexVersion.parent_digest` | `src/cko/core/index/models.py:166-175` | continuidade estrutural do índice | não derivação do conhecimento |
| `IndexSnapshot` | `src/cko/core/index/models.py:316-331` | estado do índice, versão e digest | projeção, não autoridade |
| `CorpusMemberReference` | `src/cko/core/corpus/models.py:51-80` | membro, categoria, versão, namespace, digest e atributos | pertencimento, não fonte |
| `CorpusManifest` | `src/cko/core/corpus/models.py:82-103` | conjunto ordenado de referências | composição apenas |
| `CorpusSnapshot` | `src/cko/core/corpus/models.py:220-241` | cópia estrutural do manifesto e digest | não histórico causal |

## 8. Mapa de sobreposições

| Conceito | Contratos atuais | Sobreposição | Decisão |
|---|---|---|---|
| origem técnica | `Origin`, `KnowledgeObjectIdentity.origin`, `KnowledgeProvenance.origin`, `DocumentSource.origin`, metadata de Relationship | alta nominal, baixa uniformidade | não criar outro texto solto; usar referências/papéis explícitos |
| autoria/atribuição | `KnowledgeMetadata`, `DocumentAuthor`, metadata/evidence de Relationship | dispersa | preservar metadata descritiva; modelar atribuição como declaração separada |
| derivação | `KnowledgeContent.derived_from`, Relationship enums, versões pais | dispersa e semanticamente diferente | distinguir derivação semântica de ancestralidade de versão |
| evidência | `RelationshipEvidence`, `DiscoveryEvidence`, `IdentityEvidence` | nomes iguais, contextos diferentes | não reutilizar como entidade central sem adaptação explícita |
| identidade | IDs específicas por fundação e `CanonicalId` legado | múltiplos espaços de nomes | referências tipadas; não fundir identidades |
| digest | serializers 010–016 e digests estruturais | padrão técnico comum | reutilizar padrão, não significado |
| snapshot | Object, Graph, Index, Corpus, Inventory | estados de domínios distintos | eventual snapshot de proveniência deve copiar apenas declarações/cadeia próprias |
| cadeia | versões pais, graph paths, relações encadeáveis | aparente, não formal | lacuna confirmada |

## 9. Evidências determinantes

| Arquivo e linhas | Símbolo | Responsabilidade observada | Conclusão arquitetural |
|---|---|---|---|
| `src/cko/core/knowledge/metadata.py:62-88` | `KnowledgeProvenance` | registro frozen/slotted de pipeline/origem | contrato parcialmente equivalente e colisão nominal direta |
| `src/cko/core/knowledge/metadata.py:119-178` | `KnowledgeMetadata` | autoria, fonte e várias proveniências | múltiplas origens já são admitidas para Object |
| `src/cko/core/knowledge/models.py:26-66` | `KnowledgeContent` | `derived_from` com várias IDs | derivação simples existente, mas incompleta |
| `src/cko/core/knowledge/__init__.py:10-29`; `src/cko/core/__init__.py:375-413` | exports | publica `KnowledgeProvenance` no subnamespace e raiz | novo símbolo homônimo é proibitivo |
| `src/cko/core/documents/metadata.py:35-95` | Author/Source/Metadata | autoria e múltiplas fontes documentais | não repetir campos; referenciar contratos existentes |
| `src/cko/core/relationships/enums.py:6-27` | `RelationshipType` | derivação e geração declaradas | Relationship sobrepõe a aresta, não o modelo completo |
| `src/cko/core/relationships/models.py:82-111` | `CanonicalRelationship` | identidade, endpoints, versão, evidências | reutilizável como projeção, insuficiente como autoridade |
| `src/cko/core/relationships/metadata.py:94-121` | `RelationshipEvidence` | detalhes de origem da relação | não é evidência de uma cadeia com identidade própria |
| `CKO_RELATIONSHIP_ARCHITECTURE.md:12-14,63-79` | responsabilidade | significado binário geral, sem grafo/execução | especializar toda proveniência aqui violaria a responsabilidade geral |
| `src/cko/core/graph/models.py:30-77,173-227` | nodes/edges/graph/snapshot | encapsula modelos homologados | Graph projeta; não deve tornar-se autoridade |
| `CKO_GRAPH_ARCHITECTURE.md:5-16,43-45` | responsabilidade | projeção relacional em memória | confirma limite documental |
| `src/cko/core/corpus/models.py:51-149,220-241` | reference/manifest/corpus/snapshot | composição, versão e integridade | Corpus não registra origem dos membros |
| `CKO_CORPUS_ARCHITECTURE.md:3-7,29-44` | responsabilidade | autoridade de pertencimento, não resolução/origem | adicionar proveniência violaria exclusividade |
| `src/cko/core/identity/origin.py:9-25` | `Origin` | origem técnica mínima | insuficiente e legado, mas nome colide semanticamente |
| `src/cko/core/inventory/models.py:96-150` | `InventorySnapshot` | visão pontual de inventário | não reutilizável para proveniência |
| `src/cko/core/discovery/models.py:248-263,311-377` | evidence/discovered item | evidência de observação operacional | fora da fundação representacional |
| `src/cko/core/discovery/identity_models.py:119-239` | `IdentityEvidence` | evidência para resolução de identidade | outra finalidade e taxonomia |
| `tests/test_knowledge_object_foundation_spr010.py:34-70,85-125` | fixtures/round-trip | prova serialização da proveniência parcial | contrato homologado não pode ser ignorado |
| `tests/test_knowledge_relationship_foundation_spr012.py:48-96,114-117` | evidence/types/digest | prova derivação genérica e evidência | sobreposição formal confirmada |
| `tests/test_knowledge_graph_foundation_spr013.py:194-200` | snapshot | digest do estado do grafo | integridade, não origem |
| `tests/test_knowledge_corpus_foundation_spr016.py:246-270` | snapshot/serializer | snapshot representacional e round-trip | composição, não proveniência |

## 10. Análise de Knowledge Object e Document

### 10.1 Knowledge Object

SPR-010 é a principal colisão. Sua documentação afirma expressamente que múltiplas proveniências e referências permitem múltiplas origens (`CKO_KNOWLEDGE_OBJECT_ARCHITECTURE.md:9-14`). O código implementa isso de forma imutável, validada e serializável. Portanto, não é correto declarar que a baseline não possui proveniência.

O contrato, entretanto, é um **descritor local de produção do Knowledge Object**. Todos os seus campos centrais são strings ou timestamp; ele não possui ID canônica, versão da declaração, referência tipada ao objeto resultante, referência tipada à fonte, ator, atividade, evidência ou ligações para declarações anteriores. `KnowledgeMetadata.provenances` permite várias ocorrências, mas não impõe unicidade, ordem causal ou encadeamento. `DeterministicKnowledgeSerializer.digest` pode calcular o hash de qualquer modelo, mas o digest não é parte da identidade/semântica de `KnowledgeProvenance`.

`KnowledgeContent.derived_from` permite múltiplos objetos-fonte e satisfaz parcialmente derivação, mas só para `KnowledgeObjectId` e sem qualificação do processo. Não representa Document, Relationship, Graph, Index ou Corpus como entidades envolvidas; não registra ator, atividade ou evidência. Deve permanecer como atalho local compatível, não ser promovido à autoridade transversal.

### 10.2 Document

SPR-011 distingue corretamente autoria, fontes, versão e integridade. `DocumentMetadata.sources` permite múltiplas fontes; `DocumentAuthor` admite identificador, organização e papel. Esses valores continuam válidos como metadata descritiva do documento.

Eles não modelam uma declaração causal: não há sujeito/objeto de proveniência explícitos, tipo de derivação, atividade, encadeamento ou evidência. `parent_version` significa apenas ancestralidade da versão do mesmo documento. `DocumentIntegrity` e checksums detectam correspondência/integridade, sem provar quem produziu o conteúdo ou de onde ele derivou.

Conclusão: Object e Document devem ser **referenciáveis** pela nova fundação; não devem recebê-la por expansão indiscriminada de seus metadados.

## 11. Análise de Knowledge Relationship

`CanonicalRelationship` é o contrato existente mais próximo de uma aresta de proveniência. Ele já oferece:

- direção, origem e destino;
- tipos `DERIVED_FROM`, `DERIVED_INTO`, `GENERATED_FROM` e `GENERATED_INTO`;
- identidade lógica e canônica;
- endpoints com namespace, tipo e versão;
- metadata e autoria da declaração;
- evidências e pesos;
- versionamento, digest e round-trip determinístico.

Mesmo assim, ele representa **significado binário geral** entre duas entidades. Não distingue papéis de entidade, ator e atividade; não valida causalidade temporal; não vincula várias entradas e saídas a uma mesma atividade; não dá identidade a uma cadeia; e seus tipos de evidência são evidências da relação genérica. Uma coleção ou grafo pode encadear relações, mas não há contrato que declare que o caminho é uma cadeia de proveniência válida.

Logo, Knowledge Provenance não deve ser simples alias, subclasse ou novo label de Relationship. A fundação independente pode **projetar** declarações binárias compatíveis em `CanonicalRelationship` ou referenciá-las como evidência, desde que a especificação defina direção e perda de informação. Relationship continua autoridade da relação semântica geral; Provenance torna-se autoridade da declaração causal/atributiva com papéis formais.

## 12. Análise de Knowledge Graph

`GraphNode` aceita somente `KnowledgeObject` ou `CanonicalDocument`; `GraphEdge` aceita `CanonicalRelationship`. Essa composição está em `src/cko/core/graph/models.py:30-77`. O grafo não possui nós próprios para ator ou atividade de proveniência e não contém declaração de proveniência distinta.

`GraphPath` prova conectividade estrutural, não validade causal. Um caminho pode misturar `references`, `contains`, `contradicts` e `derived_from`; nada o transforma automaticamente em lineage. Tornar Graph autoridade de proveniência violaria `CKO_GRAPH_ARCHITECTURE.md:5-16`, que o define como projeção das conexões entre objetos homologados sem reprodução de campos.

Conclusão: Graph pode projetar uma cadeia definida pela SPR-017 no futuro, mas não a substitui e não deve ser dependência interna obrigatória da fundação.

## 13. Análise de Knowledge Corpus

`CorpusMemberReference` declara identidade tipada, namespace, versão e digest do membro. `CorpusManifest` declara pertencimento. `KnowledgeCorpus` declara identidade, versão da composição, metadata e digest. `CorpusSnapshot` congela esse estado.

Nenhum desses contratos registra quem criou um membro, qual fonte o originou, qual atividade o derivou ou quais membros precederam causalmente outro. `attributes` é extensão estrutural arbitrária, não contrato formal de proveniência. Usá-lo para ocultar proveniência impediria validação e interoperabilidade canônicas.

Adicionar diretamente atores, atividades e cadeias ao Corpus quebraria sua responsabilidade exclusiva de composição (`CKO_CORPUS_ARCHITECTURE.md:3-13`). Um corpus poderá futuramente conter uma declaração de proveniência como membro somente se a evolução do conjunto fechado de categorias for autorizada em Sprint própria; isso não faz parte da SPR-017 e não deve ser antecipado.

## 14. Versões, snapshots e digests

### 14.1 Versões

`KnowledgeVersion`, `DocumentVersion` e `RelationshipVersion` usam `parent_version`; `IndexVersion` usa `parent_digest`; `CorpusVersion` usa versão/revisão. Esses contratos descrevem sucessão dentro de um mesmo domínio. Uma nova versão pode não derivar semanticamente de outra fonte, e uma derivação pode gerar uma entidade de tipo diferente sem relação de versão. Portanto, versionamento não substitui proveniência.

### 14.2 Snapshots

Knowledge, Graph, Index, Corpus e Inventory possuem snapshots. Todos capturam estado de seu agregado ou coleção. Nenhum registra, por responsabilidade própria, uma declaração causal completa. Um eventual snapshot de proveniência deverá ser exclusivamente representacional e conter apenas declarações/cadeia da nova fundação; não deve ser confundido com backup, checkpoint, log ou histórico persistente.

### 14.3 Digests

Os serializers de SPR-010–016 calculam SHA-256 sobre JSON determinístico: `knowledge/serializer.py:43-64`, `documents/serializer.py:53-82`, `relationships/serializer.py:52-84`, `graph/serializer.py:54-81`, `query/serializer.py:57-89`, `index/serializer.py:47-60` e `corpus/serializer.py:52-79`.

Esses digests provam igualdade/integridade da representação fornecida. Eles não comprovam que a fonte declarada existe, que a autoria é verdadeira, que a atividade ocorreu ou que a cadeia é externamente autêntica. Uma declaração SPR-017 pode ter digest próprio para integridade estrutural, mantendo essa limitação explícita.

## 15. Arquitetura legada

### 15.1 `Origin`

`src/cko/core/identity/origin.py:1-25` define `Origin(system, captured_at, reference)` como origem técnica mínima. Ele não tem identidade, versão, serializer próprio, sujeito, ator, atividade, evidência ou cadeia. Deve permanecer compatível com eventos/documento legado; não deve ser promovido a raiz da nova fundação.

### 15.2 Documento e evento legados

`src/cko/core/models/document.py:14-58` usa `Origin` no documento legado e associa documento/localização a inventário. `src/cko/core/models/event.py:12-25` representa fato técnico publicável. Ambos pertencem ao baseline pré-SPR-010 e não cobrem proveniência canônica transversal. `CanonicalEvent` é evento operacional, expressamente fora da nova responsabilidade.

### 15.3 Discovery e identidade

`DiscoveryEvidence` sustenta uma observação (`src/cko/core/discovery/models.py:248-263`); `DiscoveredItem` registra source, referência externa, método, correlação, adapter e evidências (`src/cko/core/discovery/models.py:311-377`). `IdentityEvidence` sustenta resolução de identidade (`src/cko/core/discovery/identity_models.py:119-239`). São contratos operacionais ou de decisão de identidade. Reutilizá-los como proveniência criaria dependência reversa e confundiria captura com representação.

### 15.4 Inventory

`InventorySnapshot` é uma visão imutável de uma revisão e coleção (`src/cko/core/inventory/models.py:96-150`). Não contém fonte, atividade, ator ou derivação. Inventory responde ao que foi inventariado, não à origem causal do conhecimento. Não deve ser estendido ou reutilizado.

## 16. Contratos reutilizáveis

Reutilização aqui significa **referenciar ou compor contratos públicos**, não copiá-los nem alterar sua responsabilidade:

1. IDs públicos de Knowledge Object, Document, Relationship, Graph, Index e Corpus, por meio de referência tipada que preserve namespace e versão.
2. `KnowledgeReference` e `RelationshipEndpoint` como precedentes de desenho; o segundo pode servir em projeções binárias, mas não como representação única de ator/atividade.
3. `CanonicalRelationship` como projeção opcional de uma declaração binária de derivação, nunca como aggregate authority da cadeia.
4. `DocumentAuthor` e os campos `author/creator` como fontes de adaptação para atribuições declaradas, sem elevá-los automaticamente a identidades verificadas.
5. padrões de dataclass frozen/slotted, deep-freeze, validação de instantes UTC, UUIDv5, schema/version e JSON canônico das fundações homologadas.
6. hierarquia pública `CKOError` e convenções de erros serializáveis.
7. serializers/digests existentes para calcular a integridade das entidades referenciadas, deixando claro que esses digests não provam origem.

## 17. Contratos não reutilizáveis como núcleo

| Contrato | Motivo |
|---|---|
| `KnowledgeProvenance` | descritor local rígido de pipeline; nome já ocupado; ausência de identidade, papéis, evidência e cadeia |
| `KnowledgeContent.derived_from` | restrito a Knowledge Object, sem atividade/ator/evidência |
| `CanonicalRelationship` | binário e semanticamente geral; não expressa atividade com múltiplas entradas/saídas nem cadeia validada |
| `CanonicalGraph`/`GraphPath` | projeção e conectividade, não autoridade causal |
| `CorpusManifest`/`CorpusMemberReference` | pertencimento e composição, não origem |
| snapshots de Object/Graph/Index/Corpus/Inventory | estados de outros agregados |
| `Origin` | origem técnica mínima legada |
| `DiscoveryEvidence`/`DiscoveredItem` | observação e captura operacional |
| `IdentityEvidence` | resolução de identidade, não proveniência |
| `CanonicalEvent` | fato técnico operacional |
| metadata `attributes` genéricos | não oferecem semântica, validação ou interoperabilidade formal |

## 18. Colisões e riscos

| Risco | Severidade | Evidência | Tratamento obrigatório |
|---|---:|---|---|
| colisão do nome `KnowledgeProvenance` | crítica | exportado em `knowledge` e raiz | nome distinto para o novo aggregate; preservar compatibilidade 1.0.0 |
| duas enumerações `RelationshipType` | alta | knowledge e relationships; alias raiz já necessário | não criar terceira enum homônima; vocabulário de proveniência próprio e mapeado |
| confundir fonte com endpoint `source` | alta | Document, Metadata e Relationship usam `source` com sentidos diferentes | glossário normativo e referências tipadas |
| duplicar autoria | alta | Object, Document e Relationship têm author/creator | atribuição como declaração; metadata permanece descritiva |
| confundir versão com derivação | alta | vários `parent_version`/`parent_digest` | regra explícita de não equivalência |
| confundir digest com prova de origem | alta | todos os serializers produzem SHA-256 | denominar integridade estrutural, não autenticidade |
| transformar Graph em autoridade | alta | Graph encapsula Relationship | dependência opcional/projeção externa, nunca raiz |
| esconder proveniência em `attributes` | média | mappings extensíveis em várias fundações | campos/papéis canônicos fechados na nova fundação |
| dependência reversa com Discovery/Runtime | crítica | evidências operacionais semelhantes | nova fundação de domínio não importa subsistemas operacionais |
| inventário público desatualizado | alta | catálogo 334 versus API real 610 | atualizar catálogo/matriz antes do freeze da especificação |
| referências heterogêneas | alta | IDs e versões próprios por fundação | referência discriminada e namespace explícito |
| ordem de cadeias e ciclos | alta | GraphPath não impõe causalidade | regras estruturais determinísticas e política explícita de ciclos |
| veracidade externa implícita | alta | hashes/assinaturas declaradas existentes | separar declaração, integridade e verificação externa |

## 19. Lacunas confirmadas

O baseline não possui contrato que, simultaneamente:

1. identifique uma declaração de proveniência como entidade canônica própria;
2. referencie de forma tipada o elemento produzido/atribuído e uma ou várias fontes;
3. diferencie entidade, ator responsável e atividade declarada;
4. represente origem, atribuição, transformação, adaptação, extração, geração ou importação como tipos canônicos de proveniência;
5. represente derivações entre tipos diferentes de membros;
6. agrupe múltiplas entradas e saídas sob a mesma atividade declarada;
7. encadeie declarações e valide a estrutura da cadeia;
8. associe evidências à declaração sem confundi-las com prova externa;
9. possua identidade, versão, digest e serialização próprios da declaração/cadeia;
10. diferencie formalmente proveniência de relação semântica, metadata, versão, snapshot, auditoria, persistência e cadeia de custódia física.

## 20. Fronteiras recomendadas

### 20.1 Dentro da fundação

Papéis conceituais mínimos, sem fixar nomes definitivos de API:

- identidade e versão da declaração de proveniência;
- referência tipada à entidade descrita e a suas fontes;
- referência declarada ao ator responsável;
- referência/descrição da atividade de origem ou derivação;
- vocabulário fechado de natureza da declaração, incluindo origem, atribuição e derivação;
- suporte a múltiplas fontes e múltiplas declarações encadeadas;
- evidências declaradas e qualificadores estruturais;
- identidade e digest determinísticos da declaração e, se adotado, da cadeia;
- serialização canônica e round-trip fechado;
- comparação e validação estrutural;
- snapshot exclusivamente representacional da cadeia/declarations.

Ator, atividade e entidade pertencem ao escopo como **papéis declarativos**, não como processos executáveis. Autoria deve poder ser expressa como atribuição de proveniência, mas os campos descritivos de Object/Document permanecem separados e compatíveis.

### 20.2 Fora da fundação

- execução de atividades;
- captura automática, ingestão, extração ou importação;
- Discovery, monitoramento, rastreadores e observabilidade;
- eventos operacionais, logs, auditoria operacional e event stores;
- persistência, repositórios, storage, checkpoints, banco, filesystem e rede;
- resolução física de fontes;
- verificação externa de autoria, verdade, existência ou causalidade;
- assinatura digital operacional, certificação e serviços de confiança;
- autenticação, autorização, controle de acesso e workflow;
- cadeia de custódia física;
- IA, LLM, embeddings, inferência, ontologias, taxonomias, busca semântica e RAG;
- geração ou execução obrigatória de Graph, Index, Query ou Corpus;
- agentes de software, plugins ou serviços externos.

## 21. Respostas às questões arquiteturais

1. **Existe contrato público equivalente?** Não, não integralmente.
2. **Existe contrato parcialmente equivalente?** Sim: sobretudo `KnowledgeProvenance`, além de Source, Evidence e relações derivativas.
3. **A proveniência está dispersa?** Sim, entre Object, Document, Relationship e contratos legados.
4. **Relationship contempla proveniência integralmente?** Não; contempla relação binária genérica e evidência da relação.
5. **Graph funciona como grafo de proveniência?** Não; pode projetar relações rotuladas, sem autoridade ou papéis formais.
6. **Corpus registra origem dos membros?** Não; registra pertencimento, versão e digest.
7. **Metadados são suficientes?** Não; são locais, descritivos e sem cadeia/identidade causal.
8. **Versões e snapshots substituem a fundação?** Não; representam sucessão e estado.
9. **Digests comprovam origem?** Não; comprovam integridade/igualdade estrutural da representação.
10. **Manifest/Registry/History/Lineage/Attribution/Source/Origin/Evidence já ocupam a responsabilidade?** Existem contratos parciais com esses sentidos, mas nenhum ocupa o domínio integral.
11. **A criação produziria duplicidade?** Sim, se repetir `KnowledgeProvenance`, source/author/derived_from/evidence sem estratégia de compatibilidade; não, se adotar a fronteira ajustada.
12. **A lacuna cabe em fundação existente?** Não sem quebrar a responsabilidade única ou excluir entidades heterogêneas.
13. **Independente ou especialização de Relationship?** Fundação independente, com projeção/mapeamento opcional para Relationship; não subclasse nem alias.
14. **Entidades mínimas?** Declaração identificada, referências a entidades, ator declarativo, atividade declarativa, natureza/qualificação, evidência e encadeamento. São papéis, não nomes finais de classes.
15. **Atores, atividades e entidades pertencem?** Sim, como papéis representacionais; não como execução.
16. **Autoria e proveniência juntas?** Autoria descritiva permanece em metadata; atribuição autoral pode ser uma declaração de proveniência referenciada, sem duplicar o contrato documental.
17. **Cadeia de custódia física pertence?** Não.
18. **Eventos operacionais, logs e auditoria pertencem?** Não.
19. **Há colisões?** Sim: nomes, `source`, tipos de relação, IDs, versões, digests, snapshots e envelopes.
20. **Quais contratos podem ser reutilizados?** IDs/referências públicas, padrões de serializer/validator/error, Relationship como projeção e contratos de autoria/fonte como adaptáveis.
21. **Quais não podem ser núcleo?** `KnowledgeProvenance` atual, `CanonicalRelationship`, Graph, Corpus, Inventory, Discovery/Identity evidence, Origin e snapshots de outros domínios.
22. **A SPR-017 pode ser especificada?** **Não na formulação candidata inalterada; sim após incorporar os ajustes obrigatórios deste parecer.**

## 22. Decisão arquitetural fundamentada

### B — APROVADA COM AJUSTES

A fundação é necessária porque a baseline não possui declaração/cadeia transversal de proveniência com papéis formais, identidade e serialização próprias. O resultado não pode ser A porque existe sobreposição pública substancial e colisão nominal direta com `KnowledgeProvenance`. Não é C porque a dispersão é conciliável sem romper as fundações: cada contrato atual pode manter sua responsabilidade, enquanto a nova fundação torna-se autoridade exclusiva da declaração causal/atributiva. Não é D porque nenhum contrato atual cobre integralmente a lacuna.

### Nome recomendado

**SPR-017 — Knowledge Provenance Statement Foundation**.

O acréscimo “Statement” diferencia a nova autoridade transversal do descritor `KnowledgeProvenance` homologado na SPR-010. A especificação pode avaliar outra denominação equivalente, desde que não colida na API pública e preserve essa distinção.

### Responsabilidade recomendada

> Definir a representação canônica, imutável, determinística, versionável e serializável de declarações de proveniência que vinculem referências a entidades de conhecimento, atores responsáveis e atividades declaradas de origem ou derivação, incluindo evidências e encadeamento lógico, sem executar, capturar ou verificar externamente tais atividades.

### Ajustes obrigatórios antes da especificação

1. preservar `KnowledgeProvenance` e todos os contratos 1.0.0 existentes; definir política explícita de compatibilidade, adaptação e depreciação futura, sem quebra silenciosa;
2. escolher nome de aggregate e discriminadores que não colidam com `KnowledgeProvenance` nem com `Origin`, `RelationshipEvidence`, `IdentityEvidence` ou `CanonicalEvent`;
3. publicar glossário normativo para entity/source/actor/activity/statement/evidence/derivation/version/digest/snapshot;
4. definir referência heterogênea sem copiar identidades das fundações existentes;
5. separar autoria descritiva de atribuição de proveniência;
6. separar derivação semântica de `parent_version`, `parent_digest` e mudança estrutural;
7. definir relação de composição/projeção com `CanonicalRelationship` e Graph, incluindo direção e perda de informação;
8. definir política estrutural para múltiplas fontes, encadeamento, ordem, duplicidade e ciclos;
9. limitar digest a integridade da representação e evidência a declaração, sem promessa de verificação externa;
10. atualizar `CKO_CORE_V1_PUBLIC_API_CATALOG.md` e `CKO_CORE_V1_DEPENDENCY_MATRIX.md` para a baseline real antes do freeze da especificação;
11. manter dependências direcionadas da nova fundação apenas para contratos públicos de domínio e base; nenhuma dependência de subsistemas operacionais;
12. fixar expressamente todas as exclusões da seção 20.2.

## 23. Recomendação final

A SPR-017 é arquiteturalmente necessária, mas deve nascer como fundação de **declarações de proveniência**, não como repetição do registro `KnowledgeProvenance`, como especialização nominal de Relationship, como grafo, como manifesto de Corpus ou como log de eventos.

O CKO Architect pode autorizar a fase de especificação somente após aceitar os doze ajustes acima. Essa autorização futura não homologará a Sprint nem autorizará implementação. Nesta auditoria não foi criado namespace, modelo, enum, factory, builder, operação, serializer ou teste; nenhuma Sprint posterior foi iniciada.

