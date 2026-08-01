# SPR-017 — Knowledge Provenance Statement Foundation — Especificação técnica reespecificada

## 1. Identificação

| Campo | Valor normativo |
|---|---|
| Sprint | SPR-017 |
| Nome oficial | **Knowledge Provenance Statement Foundation** |
| Natureza | especificação técnica e arquitetural pré-implementação |
| Data de referência | 2026-07-29, `America/Sao_Paulo` |
| Namespace futuro | `cko.core.provenance` |
| Baseline do SDK | `cko` 1.0.0 |
| Schema inicial proposto | `1.0` |
| Serialização inicial proposta | `1.0` |
| Versão inicial da fundação proposta | `1.0.0` |
| Implementação nesta etapa | **PROIBIDA** |

Este documento usa **DEVE**, **NÃO DEVE**, **PODERÁ**, **OBRIGATÓRIO** e **PROIBIDO** em sentido normativo.

## 2. Status

**REESPECIFICADA E PRONTA PARA NOVA AUDITORIA FORMAL.**

Este status não significa implementação, homologação nem autorização automática para codificação. Nesta etapa não existe namespace, modelo Python, teste executável, alteração de export, incremento de versão ou novo wheel da SPR-017.

## 3. Baseline confirmado

A inspeção direta e os artefatos homologados confirmam:

- CORE-001, ARCH-001 v1.2, SPR-008A–W, SPR-008OA, SPR-009/009A e SPR-010–016 formam o baseline;
- `pyproject.toml` e `cko.core.__version__` declaram `1.0.0`;
- `cko.core.__all__` contém 610 nomes únicos resolvidos;
- `cko.core.corpus.__all__` contém 48 nomes únicos e 42 deles são reexportados por `cko.core`;
- a SPR-016 entrega 11 modelos canônicos frozen/slotted e registra 28/28 testes dedicados e 175/175 testes integrados das SPR-010–016;
- a regressão homologada registra 878/880 testes aprovados, com apenas as duas falhas históricas de `collect_metadata(calculate_hash=True)` e do handle SQLite no teardown Windows;
- a cobertura registrada para a SPR-016 é 98% de linhas e 95% de branches;
- `runtime/reports/build/cko-1.0.0-py3-none-any.whl` possui 416.943 bytes e 265 entradas;
- o SHA-256 recalculado do wheel é `32EC3386BFDC1377BF85745F3529FA019AC820158F50E1A480BEA4B03D9A1D51`;
- o relatório da SPR-016 registra build com exit code zero, instalação limpa e smoke test isolado aprovados.

Os números de cobertura, build e instalação limpa são evidência homologada registrada; o tamanho, hash, versão, API carregada e exports foram novamente confirmados por inspeção nesta especificação. Nenhum novo build foi executado.

## 4. Documentos normativos e evidências

São normativos para a futura implementação:

1. `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md`;
2. `CKO_CORE_V1_ARCHITECTURE_DECISION.md`;
3. `CKO_CORE_V1_DEPENDENCY_MATRIX.md`;
4. `CKO_CORE_V1_EXCEPTION_HIERARCHY.md`;
5. `CKO_CORE_V1_PUBLIC_API_CATALOG.md`, observado o descompasso da seção 45;
6. documentação arquitetural, API, modelo e serialização das SPR-010–016;
7. relatórios de implementação das SPR-010–016;
8. `SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md` e `SPR016_IMPLEMENTATION_REPORT.md`;
9. `SPR017_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md` integralmente;
10. contratos públicos e testes existentes em `src/cko/core` e `tests`.

Em conflito, o código público homologado e seus testes prevalecem sobre catálogo documental desatualizado; esta especificação prevalece para a fronteira exclusiva da SPR-017 após aprovação formal.

## 5. Resultado das auditorias

A auditoria arquitetural pré-implementação aprovou a necessidade com ajustes. A auditoria formal posterior `SPR017E_NOVA_AUDITORIA_FORMAL.md`, SHA-256 `9F69EA938A66E9A82C359B94A326AAD61028DB9F9F4906504A6028DCB23E0085`, reprovou a versão anterior e identificou NF-001–NF-008 e AF-001–AF-004. Esta segunda correção incorpora integralmente essas determinações, preserva a rastreabilidade F-001–F-019 e permanece sujeita a nova auditoria formal independente. Nenhuma auditoria anterior ou esta correção autoriza implementação ou homologação.

## 6. Problema arquitetural

O baseline contém fragmentos legítimos de informação relacionada à proveniência, mas não uma declaração independente que reúna sujeito, fontes heterogêneas, atores, atividade, evidências e antecedentes sob identidade, versão, digest e serialização próprios.

As sobreposições confirmadas são:

| Contrato existente | Informação atual | Limite confirmado |
|---|---|---|
| `KnowledgeProvenance` | origem e pipeline locais de um Knowledge Object | sem identidade própria, sujeito tipado, papéis, evidência ou cadeia |
| `KnowledgeMetadata.provenances` | múltiplos descritores locais | não ordena causalidade nem forma declaração transversal |
| `KnowledgeContent.derived_from` | IDs de Knowledge Objects de origem | um único domínio, sem ator, atividade ou evidência |
| `DocumentAuthor` / `DocumentSource` | autoria e fontes descritivas | metadata documental, não afirmação formal transversal |
| `CanonicalRelationship` | relação binária geral, evidências e digest | não representa declaração n-ária nem atividade com múltiplas entradas |
| Graph | projeção de objetos, documentos e relações | conectividade não equivale a proveniência |
| Index | projeção indexada de referências | organização não equivale a origem |
| Corpus | pertencimento e composição | manifesto não declara origem dos membros |
| versões e snapshots | sucessão ou estado | não provam derivação |
| digests | integridade estrutural | não provam origem, autoria ou verdade |

## 7. Decisão arquitetural

A SPR-017 DEVE criar futuramente uma fundação independente de valores de domínio sob `cko.core.provenance`. Sua autoridade exclusiva será a **declaração de proveniência**. Ela NÃO DEVE especializar, substituir ou ampliar silenciosamente Object, Document, Relationship, Graph, Query, Index, Corpus, Inventory ou contratos legados.

A declaração será n-ária: um sujeito, zero ou mais entidades participantes, zero ou mais atores, no máximo uma atividade declarada, zero ou mais evidências e zero ou mais antecedentes. Os elementos serão referências; nenhum alvo será carregado ou resolvido.

Alternativas rejeitadas:

| Alternativa | Decisão e fundamento |
|---|---|
| ampliar `KnowledgeProvenance` | rejeitada; quebraria contrato 1.0.0 e continuaria local ao Object |
| usar `CanonicalRelationship` como núcleo | rejeitada; relação binária geral perde participantes e cadeia |
| usar Graph como autoridade | rejeitada; Graph é projeção e não admite atores/atividades como nós canônicos |
| usar Corpus como autoridade | rejeitada; pertencimento não representa origem |
| esconder dados em `attributes` | rejeitada; elimina semântica fechada e interoperabilidade |
| criar log/event store | rejeitada; captura operacional está fora do domínio |

## 8. Nome oficial

O nome oficial é **SPR-017 — Knowledge Provenance Statement Foundation**. O agregado será `ProvenanceStatement`. O prefixo `Knowledge` NÃO DEVE ser repetido no nome do agregado, pois o namespace já fornece o contexto e `KnowledgeProvenanceStatement` seria redundante. O termo *Statement* diferencia formalmente a nova afirmação do descritor `KnowledgeProvenance` existente.

## 9. Responsabilidade exclusiva

> Representar declarações canônicas, imutáveis, determinísticas, versionáveis e serializáveis de origem, atribuição e derivação, vinculando entidades, atores responsáveis, atividades declaradas, evidências e encadeamento lógico, sem execução, captura automática ou verificação externa.

A fundação representa que uma afirmação foi estruturada; ela NÃO afirma que a afirmação seja verdadeira.

## 10. Terminologia normativa

| Termo | Definição |
|---|---|
| Provenance Statement | afirmação estruturada e identificada sobre origem, atribuição ou derivação de um sujeito |
| sujeito | elemento cuja proveniência é afirmada; exatamente um por declaração |
| entidade | fonte, entrada, original, contribuição ou suporte referenciado pela afirmação |
| ator | pessoa, organização, sistema ou processo referenciado em papel declarativo |
| atividade | descrição referenciada de ação alegadamente ocorrida; nunca execução |
| evidência declarada | referência que o declarante associa como suporte; não é verificada pela fundação |
| antecedente | referência a outra declaração logicamente anterior ou relacionada na cadeia |
| atribuição | afirmação que associa ator e papel ao sujeito |
| autoria descritiva | metadata local existente; não se torna atribuição formal implicitamente |
| derivação | afirmação causal/transformacional entre sujeito e entidade-fonte |
| sucessão de versão | evolução do mesmo contrato lógico; não implica derivação |
| digest | SHA-256 da representação canônica definida; somente integridade estrutural |
| qualificador | par nome/valor fechado à árvore JSON canônica, sem semântica operacional |

Uma Provenance Statement distingue-se de metadata descritiva, fonte documental, referência genérica, relação semântica, ancestralidade de versão, histórico estrutural, snapshot, log, evento, auditoria, assinatura, certificação, verificação externa e cadeia de custódia física.

## 11. Escopo

Estão dentro do escopo futuro:

- declaração identificada, categoria, sujeito e participantes tipados;
- múltiplas fontes, atores, atividade, evidências, qualificadores e antecedentes;
- versões separadas de schema, serialização, fundação, declaração e alvos;
- UUIDv5, identidade canônica, JSON canônico, SHA-256 e round-trip;
- validação local e validação pura de um conjunto de declarações fornecido pelo chamador;
- comparação e operações imutáveis;
- projeção pura e opcional de casos compatíveis para `CanonicalRelationship`;
- integração somente por APIs públicas homologadas;
- exports, documentação, testes, cobertura, build e validação de wheel.

## 12. Itens fora do escopo

São PROIBIDOS: execução ou captura de atividade; runtime; eventos e logs operacionais; auditoria operacional; Event Store e Event Sourcing; persistência, Storage, Repository, banco, filesystem e cache; rede e acesso a URL; resolução/materialização de referências; ingestão, extração e importação operacionais; workflow, filas e workers; autenticação, autorização, usuários, organizações e tenancy; transações e concorrência; sincronização; assinatura digital operacional; certificação; verificação externa; cadeia de custódia física; monitoramento; Graph/Index/Corpus automáticos; IA, LLM, embeddings, RAG, inferência, ontologias, taxonomias, busca semântica, RDF, OWL, SPARQL, Gremlin e bancos vetoriais.

Também são PROIBIDOS protocolos vazios ou lacunas artificiais que antecipem essas responsabilidades e nomes como `ProvenanceRepository`, `ProvenanceStorage`, `ProvenanceRuntime`, `ProvenanceLoader`, `ProvenanceSession`, `ProvenanceEngine`, `ProvenanceCheckpoint`, `ProvenanceDiscovery`, `ProvenanceManager`, `ProvenanceEventStore`, `ProvenanceWorkflow`, `ProvenanceTracker` e `ProvenanceResolver`.

## 13. Colisão com `KnowledgeProvenance`

`KnowledgeProvenance` é uma dataclass pública frozen/slotted da SPR-010 com `origin`, `pipeline`, `generating_process`, `original_source`, `timestamp`, `pipeline_version`, `source_type` e schema. Ela permanece exportada por `cko.core.knowledge` e `cko.core` com assinatura, comportamento, serialização e discriminador intactos.

Ela não representa integralmente uma Provenance Statement porque não possui identidade própria, sujeito tipado, participantes com papéis, evidências tipadas, versão lógica, digest armazenado ou antecedentes.

Política obrigatória:

1. `KnowledgeProvenance` NÃO DEVE ser removido, renomeado, alterado, convertido em alias nem usado como classe-base;
2. não haverá alias entre `KnowledgeProvenance` e `ProvenanceStatement`;
3. uma adaptação futura, se entregue na SPR-017, será operação pura, explícita e unidirecional, receberá também sujeito e chave semântica e produzirá nova declaração; nunca ocorrerá implicitamente;
4. a adaptação preservará os textos legados como atividade/qualificadores declarados, sem promovê-los a fatos verificados;
5. conversão reversa é rejeitada porque perde sujeito, papéis, cadeia, evidências e identidade;
6. testes de import, assinatura, round-trip, discriminador e comportamento do símbolo antigo são gate de retrocompatibilidade.

## 14. Modelo conceitual

```text
ProvenanceStatement
├── identity: ProvenanceStatementIdentity
├── category: ProvenanceStatementCategory
├── subject: ProvenanceSubjectRef
├── entities: tuple homogênea de ProvenanceEntityRef
├── actors: tuple homogênea de ProvenanceActorRef
├── activity: ProvenanceActivityRef | null
├── evidence: tuple homogênea de ProvenanceEvidenceRef
├── predecessors: tuple homogênea de ProvenanceStatementRef
├── qualifiers: tuple homogênea de ProvenanceQualifier
├── statement_version: ProvenanceStatementVersion
├── declared_at: UTC instant | null
├── schema_version: "1.0"
├── serialization_version: "1.0"
└── digest: lowercase SHA-256
```

O sujeito não carrega o objeto real. Entidades usam um contrato único com papel fechado, evitando classes redundantes por tipo de fonte. Atores usam o termo **Actor**, e não **Agent**, para evitar associação com subsistemas autônomos. A atividade é singular porque cada declaração afirma uma unidade lógica de ocorrência; atividades distintas exigem declarações distintas encadeadas. Evidências são referências declaradas e não payloads, arquivos ou resultados de verificação.

## 15. Modelos públicos candidatos

| Modelo | Campos conceituais e responsabilidade | Classe |
|---|---|---|
| `ProvenanceStatementId` | UUID canônico da declaração | obrigatório |
| `ProvenanceStatementIdentity` | `statement_id`, namespace, chave semântica | obrigatório |
| `ProvenanceQualifier` | nome e valor canônico imutável | obrigatório |
| `ProvenanceSubjectRef` | tipo, namespace, ID, versão e digest opcionais do sujeito | obrigatório |
| `ProvenanceEntityRef` | referência de entidade mais `ProvenanceEntityRole` | obrigatório |
| `ProvenanceActorRef` | referência, tipo de ator e papel | obrigatório |
| `ProvenanceActivityRef` | referência, tipo, rótulo, intervalo UTC opcional e qualificadores | obrigatório |
| `ProvenanceEvidenceRef` | referência, tipo de evidência, digest opcional e qualificadores | obrigatório |
| `ProvenanceStatementRef` | ID, versão lógica e digest da declaração referenciada | obrigatório |
| `ProvenanceStatementVersion` | SemVer lógico, revisão positiva e versão anterior opcional | obrigatório |
| `ProvenanceStatement` | agregado independente e factory-only | obrigatório |
| `ProvenanceStatementComparisonResult` | diferenças estruturais ordenadas entre declarações | obrigatório |
| `ProvenanceChainValidationResult` | IDs validados e antecedentes externos ordenados | obrigatório |

Todos os modelos DEVEM ser dataclasses frozen/slotted, profundamente imutáveis, discriminados, hashable apenas quando todos os seus valores canônicos forem hashable e construídos sem estado global mutável. O agregado `ProvenanceStatement` DEVE ser criado ou reconstruído pela Factory; valores auxiliares podem ter construção direta validada.

## 16. Modelos internos candidatos

Somente os seguintes detalhes internos são autorizados:

- base comum privada para normalização das referências;
- tabela fechada de envelopes e discriminadores;
- tokens privados de construção do agregado;
- tokens de ordenação canônica;
- payload interno de identidade;
- payload interno de digest;
- normalizadores de texto, UUID, SemVer, UTC, SHA-256 e árvore JSON;
- algoritmo privado de detecção de ciclos sobre o conjunto fornecido.

Esses itens NÃO DEVEM aparecer em `__all__`, em `cko.core`, no catálogo público nem como tipo exigido dos consumidores.

## 17. Enums

Todos os enums são fechados, serializados por valor lowercase e rejeitam valores desconhecidos no schema `1.0`.

| Enum | Valores e semântica |
|---|---|
| `ProvenanceStatementCategory` | `origin`, `attribution`, `derivation`, `generation`, `transformation`, `adaptation`, `extraction`, `incorporation`, `source_usage` |
| `ProvenanceTargetType` | `knowledge_object`, `document`, `relationship`, `graph`, `index`, `corpus`, `external_resource` |
| `ProvenanceEntityRole` | `source`, `input`, `original`, `contributing_source`, `supporting_entity` |
| `ProvenanceActorType` | `person`, `organization`, `system`, `process` |
| `ProvenanceActorRole` | `creator`, `author`, `contributor`, `producer`, `responsible_party`, `transformer`, `reviewer`, `publisher` |
| `ProvenanceActivityType` | `generation`, `transformation`, `adaptation`, `extraction`, `incorporation`, `copying`, `other_declared` |
| `ProvenanceEvidenceType` | `documentary`, `record`, `relationship`, `observation`, `assertion` |

Decisões sobre valores avaliados:

- `subject`, `output` e `derived` NÃO integram `ProvenanceEntityRole`: o sujeito já representa o resultado e duplicá-lo criaria conflito;
- `custodian_logical` NÃO integra papéis iniciais: sua semântica aproxima cadeia de custódia, fora do escopo;
- `other_declared` existe apenas para atividade representacional cuja categoria principal continua fechada; exige rótulo e qualificador de vocabulário. Não permite responsabilidade operacional oculta;
- `external_resource` admite referência lógica externa sem rede ou resolução;
- valor desconhecido exige nova versão de schema; não há fallback silencioso.

## 18. Referências tipadas

As seis referências públicas são distintas para impedir troca acidental de papéis. Não haverá referência genérica pública.

Campos comuns: `target_type` quando aplicável, `namespace` textual NFC não vazio, `target_id` textual canônico não vazio, `target_version` SemVer opcional, `target_digest` SHA-256 lowercase opcional e schema. IDs dos alvos CORE DEVEM usar o UUID textual canônico publicado pelo alvo; `external_resource` DEVE usar identificador absoluto estável, mas a fundação NÃO DEVE acessá-lo.

Regras adicionais:

- `ProvenanceSubjectRef` e `ProvenanceEntityRef` aceitam os sete tipos de alvo;
- `ProvenanceActorRef` usa `actor_type`, namespace e ID próprios, sem criar usuário ou organização;
- `ProvenanceActivityRef` usa identidade declarativa, tipo, rótulo opcional, `started_at`/`ended_at` opcionais e qualificadores; quando ambos existem, fim não antecede início;
- `ProvenanceEvidenceRef` usa identidade declarativa e tipo; seu digest descreve o alvo declarado, não a declaração;
- `ProvenanceStatementRef` aceita somente `ProvenanceStatementId`, versão e digest, sem `target_type`;
- igualdade e hashing usam todos os campos normalizados;
- referências não materializam, validam existência, consultam ou abrem o alvo;
- versões ou digests desconhecidos são representados por `null`, não por texto vazio.

## 19. Categorias

| Categoria | Invariantes adicionais |
|---|---|
| `origin` | ao menos uma entidade `source` ou `original`; atividade opcional |
| `attribution` | ao menos um ator; papéis de entidade são opcionais; atividade opcional |
| `derivation` | ao menos uma entidade `source`, `input`, `original` ou `contributing_source`; atividade opcional |
| `generation` | atividade obrigatória; fontes opcionais |
| `transformation` | atividade obrigatória e ao menos uma fonte/entrada/original |
| `adaptation` | atividade obrigatória e ao menos uma fonte/entrada/original |
| `extraction` | atividade obrigatória e ao menos uma fonte/entrada/original |
| `incorporation` | atividade obrigatória e ao menos uma fonte/entrada/contribuição |
| `source_usage` | ao menos uma entidade `source` ou `contributing_source`; atividade opcional |

Uma declaração trata um único sujeito. Múltiplas fontes são representadas por várias entidades na mesma declaração. Resultados adicionais exigem declarações próprias, compartilhando a mesma atividade referenciada quando apropriado.

## 20. Papéis

Papéis são afirmações, não permissões, propriedades ou autenticação. `author` e `creator` são distintos: autor responde pela autoria intelectual declarada; creator responde pela criação declarada do artefato. `producer` indica produção, `transformer` participação na transformação, `responsible_party` responsabilidade declarada, `reviewer` revisão e `publisher` publicação. Nenhum papel prova identidade ou ação.

Cada par `(actor identity, role)` e `(entity identity, role)` é único. A mesma referência PODERÁ aparecer com papéis semanticamente distintos. Papéis incompatíveis com a categoria são rejeitados: `attribution` aceita todos os papéis; `transformation` exige ao menos um ator `transformer` ou `responsible_party` somente quando atores forem informados; nenhuma categoria obriga ator além de `attribution`.

## 21. Invariantes

1. Todo modelo público é frozen e slotted.
2. Sequências tornam-se tuplas; qualificadores tornam-se tuplas ordenadas; mappings são profundamente congelados.
3. Schema e discriminador pertencem à allowlist fechada.
4. O sujeito é obrigatório e único.
5. A identidade canônica corresponde exatamente ao payload de identidade.
6. O namespace UUID da fundação é exclusivo e constante.
7. Categoria e enums são válidos.
8. Textos são NFC, sem espaços periféricos e não vazios quando obrigatórios.
9. Instantes têm timezone e são normalizados para UTC.
10. Versões seguem SemVer canônico; revisão é inteira positiva.
11. SHA-256 possui 64 caracteres hexadecimais lowercase.
12. Coleções não contêm duplicatas pelos tokens definidos na seção 25.
13. Coleções são armazenadas na ordem canônica, independentemente da ordem de entrada.
14. Sujeito não pode reaparecer como entidade com a mesma identidade tipada.
15. A declaração não referencia a si própria como antecedente nem como versão anterior.
16. A validação de conjunto rejeita ciclos entre declarações fornecidas.
17. Antecedentes externos ao conjunto são fronteiras válidas e explicitamente relatadas.
18. Regras específicas da categoria são satisfeitas.
19. Atividade é única e compatível com a categoria.
20. Intervalo temporal declarado é coerente; não há validação causal contra relógio externo.
21. Valores de qualificador limitam-se a `null`, booleano, inteiro, texto, arrays e objetos textuais; floats, bytes, datetime embutido, NaN e infinito são proibidos.
22. Nomes de qualificadores são únicos dentro do mesmo proprietário.
23. Versão anterior, quando presente, usa o mesmo statement ID, revisão menor e digest diferente.
24. Mudança semântica exige incremento de revisão e digest diferente.
25. Mudança de categoria ou sujeito exige nova identidade.
26. O digest armazenado coincide com o payload canônico sem o próprio digest.
27. Round-trip preserva igualdade e bytes canônicos.
28. Campos desconhecidos, duplicados, ausentes ou de tipo incorreto são rejeitados.
29. Nenhuma operação realiza I/O, resolução, captura ou mutação.
30. Nenhum import privado ou dependência reversa é permitido.
31. `KnowledgeProvenance` e contratos existentes permanecem intactos.

As invariantes 1–15 e 18–23 aplicam-se na construção e desserialização; 16–17 na validação explícita de cadeia; 24–25 na criação de revisão e comparação; 26–28 na serialização/desserialização; todas as invariantes de pureza aplicam-se a qualquer operação.

## 22. Identidade

`ProvenanceStatementIdentity` contém namespace de negócio, chave semântica normalizada e `ProvenanceStatementId`. A chave semântica é fornecida pelo chamador e identifica a linhagem da afirmação; não é caminho, timestamp nem chave de banco.

O nome UUIDv5 é a representação JSON canônica do array conceitual:

`provenance_statement`, namespace de negócio, chave semântica, categoria e token canônico do sujeito.

O ID resultante é estável para a mesma linhagem, categoria e sujeito. Entidades, atores, atividade, evidências, qualificadores, antecedentes, `declared_at`, versões e digest são excluídos do nome UUID para permitir revisões da mesma afirmação. Mudar sujeito ou categoria muda a natureza da afirmação e DEVE gerar identidade nova. Mudar participantes ou conteúdo mantém a identidade e DEVE incrementar a versão/revisão.

Não há UUIDv4, aleatoriedade, relógio, path, contador global ou estado externo na identidade canônica.

## 23. Namespace UUID

O namespace recomendado e reservado é:

`84c43be6-4bb5-52a8-9582-a2e8b04d797c`

Ele foi obtido deterministicamente por UUIDv5, usando o namespace padrão URL e o nome NFC exato `urn:cko:core:knowledge-provenance-statement-foundation`. O valor não aparece nos namespaces existentes inspecionados. A implementação DEVE publicar `PROVENANCE_UUID_NAMESPACE`, testar a reprodução do valor e registrar a derivação. Alterá-lo após publicação é quebra de identidade e exige novo schema/contrato, nunca simples patch.

## 24. Versionamento

| Dimensão | Campo/constante | Inicial | Regra |
|---|---|---:|---|
| schema | `PROVENANCE_SCHEMA_VERSION` | `1.0` | muda quando forma/semântica do modelo fechado muda |
| serialização | `PROVENANCE_SERIALIZATION_VERSION` | `1.0` | muda quando bytes canônicos mudam |
| fundação | `PROVENANCE_VERSION` | `1.0.0` | SemVer da API do namespace |
| declaração | `ProvenanceStatementVersion.version` | `1.0.0` | SemVer lógico da linhagem |
| revisão | `ProvenanceStatementVersion.revision` | `1` | incrementa exatamente em um a cada revisão |
| alvo | `target_version` | opcional | versão publicada pelo alvo; não inferida |
| SDK | `cko.core.__version__` | `1.0.0` atual | não alterada nesta etapa |

Schema/serialização futuros são rejeitados. Schema anterior só será aceito se houver decoder explicitamente mantido no mesmo contrato; não há migração operacional. Uma nova revisão referencia a anterior por `ProvenanceStatementRef`, com mesmo ID, versão anterior e digest anterior. O antecedente causal permanece em `predecessors`, separado da versão anterior.

## 25. Canonicalização

O formato canônico DEVE usar:

- UTF-8 estrito, sem BOM, `ensure_ascii=False`;
- Unicode NFC antes de validar ou ordenar;
- chaves de objetos em ordem lexicográfica por code point;
- separadores `,` e `:` sem whitespace;
- UUID em lowercase com hífens;
- enum pelo valor lowercase;
- SemVer canônico sem prefixo `v`;
- UTC ISO-8601 com microssegundos normalizados e sufixo `Z`;
- SHA-256 lowercase;
- todos os campos declarados presentes; opcionais ausentes representados por `null`;
- arrays somente para coleções ordenadas;
- rejeição de floats e números não inteiros em qualificadores;
- rejeição de chave duplicada já no parser JSON;
- rejeição de campo desconhecido, valor vazio proibido e duplicidade semântica.

Tokens de ordenação:

| Coleção | Token, na ordem |
|---|---|
| entidades | papel, tipo do alvo, namespace, ID, versão ou vazio, digest ou vazio |
| atores | papel, tipo de ator, namespace, ID, versão ou vazio, digest ou vazio |
| evidências | tipo, namespace, ID, versão ou vazio, digest ou vazio |
| antecedentes | statement ID, versão, digest |
| qualificadores | nome, representação JSON canônica do valor |

Reordenação de entrada não muda bytes, identidade ou digest. Alteração de papel, referência, evidência, atividade, qualificador, antecedente, versão ou instante declarado muda a representação e o digest.

## 26. Digest

O algoritmo é SHA-256 sobre bytes UTF-8 do payload canônico da declaração. O payload inclui: schema, serialização, identidade, categoria, sujeito, entidades, atores, atividade, evidências, antecedentes, qualificadores, versão da declaração e `declared_at`. Exclui somente o campo `digest` para impedir autorreferência.

O statement ID participa do digest, mas o digest não participa do statement ID. Digests dos alvos e antecedentes participam quando declarados. O digest é texto lowercase de 64 hexadecimais. `verify_digest` usa comparação segura e retorna `bool`; `require_valid_digest` retorna `None` ou lança `ProvenanceDigestError`.

O digest comprova somente integridade/igualdade estrutural. Ele NÃO comprova autoria, origem, causalidade, veracidade, autenticidade externa, assinatura, certificação nem cadeia de custódia.

## 27. Serialização e desserialização

`DeterministicProvenanceSerializer` será o único serializer oficial. Cada envelope contém exatamente `model`, `schema_version`, `serialization_version` e os campos fechados do discriminador. Discriminadores serão nomes snake_case derivados dos modelos, sem import dinâmico.

Desserialização obrigatória:

1. aceita somente bytes UTF-8 estritos;
2. detecta chaves JSON duplicadas;
3. exige raiz objeto e allowlist de discriminador;
4. valida conjunto exato de campos e versões;
5. reconstrói enums, UUID, UTC, SemVer, referências e valores congelados;
6. reconstrói o agregado pela Factory;
7. recalcula e valida identidade e digest;
8. serializa novamente e exige igualdade byte a byte com a entrada.

JSON semanticamente equivalente, mas não canônico, é rejeitado. Não haverá leitura/escrita de arquivo, pickle, import dinâmico, adaptador, URL, stream ou migration hook.

## 28. Round-trip

Para todo modelo aceito, a desserialização da serialização DEVE resultar em valor igual, com mesmo hash quando aplicável, identidade, papéis, ordem canônica, versões, digest e bytes. O round-trip cobre cada modelo público e o agregado. A serialização após desserialização DEVE ser byte a byte idêntica.

## 29. Operações puras

`ProvenanceOperations` exporá operações estáticas; todas recebem valores e devolvem novo valor ou resultado, sem modificar entradas.

| Operação conceitual | Resultado e regras |
|---|---|
| `create` via Factory | declaração revisão 1 validada, identidade e digest calculados |
| `revise` | nova declaração, mesma identidade, revisão +1 e referência à versão anterior |
| `with_actor` / `without_actor` | nova revisão; rejeita duplicidade/ausência |
| `with_entity` / `without_entity` | nova revisão; revalida categoria |
| `with_evidence` / `without_evidence` | nova revisão |
| `with_predecessor` / `without_predecessor` | nova revisão; rejeita self e duplicidade |
| `compare` | `ProvenanceStatementComparisonResult` ordenado |
| `validate_chain_in_supplied_set` | valida todo o conjunto fornecido e retorna fronteiras externas |
| `verify_digest` | valida SHA-256 sem I/O |
| `project_relationships` | tupla de `CanonicalRelationship` somente nos casos permitidos da seção 32 |

Todas são determinísticas; canonicalização e serialização são lineares no tamanho do valor, ordenações custam `O(n log n)`, comparação é linear após canonicalização e validação de cadeia é `O(V+E)` sobre o conjunto fornecido. Qualquer alteração semântica produz revisão e digest novos. Operação que removeria requisito da categoria falha sem criar valor.

Builder é **rejeitado na versão inicial**: a Factory e as operações imutáveis cobrem composição sem introduzir estado intermediário público. `canonicalize`, `serialize` e `deserialize` pertencem ao serializer e não serão duplicados como funções raiz.

## 30. Decisão sobre snapshot

**NÃO ADOTAR SNAPSHOT.**

`ProvenanceStatement` já é imutável, versionada, digerida, serializável e encadeável. Um `ProvenanceStatementSnapshot` duplicaria estado sem responsabilidade distinta e incentivaria leitura temporal ou persistência fora do escopo. Estado histórico é representado por versões anteriores explicitamente referenciadas; cadeia causal é representada por `predecessors`. Snapshots de Object, Graph, Index, Corpus e Inventory NÃO DEVEM ser reutilizados.

## 31. Encadeamento

- `predecessors` é uma tupla canonicamente ordenada de zero ou mais `ProvenanceStatementRef`;
- cadeia vazia é válida e representa raiz ou declaração independente;
- múltiplos antecedentes são válidos;
- duplicidade pelo statement ID é proibida, mesmo com versão/digest diferentes;
- autorreferência é rejeitada localmente;
- validação local não resolve antecedentes;
- `validate_chain_in_supplied_set` examina integralmente apenas as declarações fornecidas pelo chamador;
- ciclo entre declarações fornecidas é rejeitado com `ProvenanceChainError`;
- antecedente ausente do conjunto é fronteira externa válida e aparece no resultado, não é resolvido;
- referência encontrada DEVE coincidir em ID, versão e digest;
- não existe ID de cadeia separado: a identidade está em cada declaração e na estrutura de referências;
- não há limite arbitrário de profundidade; o conjunto fornecido define a fronteira finita da validação.

Encadeamento causal e versão anterior são grafos distintos e NÃO DEVEM compartilhar campo.

## 32. Evidências e projeção para Relationship

Evidência é sempre declarada. `ProvenanceEvidenceRef` identifica o suporte alegado, seu tipo, versão/digest opcionais e qualificadores. A fundação não lê o suporte, recalcula seu digest, verifica assinatura nem decide confiança. Evidência e source são distintas: uma entidade participa da afirmação; uma evidência sustenta a afirmação.

Projeção opcional para `CanonicalRelationship`:

- permitida para categorias não `attribution` quando sujeito e cada entidade forem endpoints aceitos pela Relationship Foundation;
- gera uma relação por entidade-fonte, orientada **entidade → sujeito**;
- mapeia derivação/geração para tipos homologados quando houver correspondência exata; demais categorias usam somente tipo público semanticamente compatível, nunca `related_to` como fallback silencioso;
- múltiplas fontes geram múltiplas relações correlacionadas pelo statement ID em metadata estrutural;
- atores, atividade, evidências, antecedentes e parte dos qualificadores não cabem integralmente e a perda DEVE ser documentada no resultado/guia;
- atribuição não é projetada, pois atores não são endpoints homologados de Graph;
- projeção não é reversível, não participa do ID/digest da declaração e não altera Relationship;
- projeção é operação explícita, pura e nunca automática.

## 33. Integração com Object

`ProvenanceSubjectRef` e `ProvenanceEntityRef` aceitam `KnowledgeObjectId`, namespace, versão e digest declarados, sem carregar `KnowledgeObject`. `KnowledgeProvenance`, `KnowledgeMetadata.provenances` e `KnowledgeContent.derived_from` permanecem metadata/atalho local.

Uma adaptação explícita de `KnowledgeProvenance` exige sujeito e chave semântica. Não haverá geração automática de statements a partir de metadata nem sincronização reversa. `KnowledgeContent.derived_from` não será considerado prova suficiente e não será alterado.

## 34. Integração com Document

Document é referenciável como sujeito ou entidade por identidade pública. `DocumentAuthor` e `DocumentSource` permanecem metadata descritiva. Criar uma atribuição formal exige chamada explícita à Factory/operação de adaptação e referência de ator; nenhum autor é promovido automaticamente. Múltiplas fontes documentais podem originar entidades distintas, preservando seus identificadores, mas não são copiadas implicitamente.

## 35. Integração com Relationship

Relationship permanece autoridade de significado binário geral. Provenance Statement permanece autoridade da afirmação n-ária. A SPR-017 poderá importar somente símbolos públicos de `cko.core.relationships` para a projeção explícita da seção 32. Não haverá subclasse, alias, campo novo, dependência reversa ou reconstrução integral a partir de relação.

## 36. Integração com Graph

Graph permanece projeção. Não participa de identidade ou digest, não armazena semântica completa e não é atualizado automaticamente. Como Graph aceita nós Object/Document e arestas Relationship, somente projeções compatíveis da seção 32 podem ser compostas externamente em Graph. A SPR-017 NÃO DEVE importar Graph para seu núcleo nem executar travessia.

## 37. Integração com Query

Query permanece intenção de consulta, fora do núcleo. Uma query NÃO é ator, atividade, evidência ou entidade de proveniência por conveniência. `ProvenanceTargetType` não inclui Query. A SPR-017 não importa `cko.core.query`.

## 38. Integração com Index

Index permanece projeção. É permitido referir um Index existente como sujeito ou entidade porque ele possui identidade pública, mas a SPR-017 não o lê nem o atualiza. A categoria fechada atual de `IndexReference` não será ampliada para Provenance Statement nesta Sprint; indexação futura exigirá autorização própria. Index não participa de identidade/digest da declaração.

## 39. Integração com Corpus

Corpus é referenciável como sujeito ou entidade por `CorpusId`, versão e digest. Isso permite afirmar proveniência sobre uma composição sem tornar Corpus autoridade de origem. Manifesto, versão e digest de Corpus não provam origem. `CorpusMemberCategory` não será ampliado; statements não serão incorporados automaticamente e Corpus não resolverá declarações.

## 40. Arquitetura de dependências

| Fundação | Direção permitida | Contratos públicos reutilizados | Projeção permitida | Dependência proibida / mitigação |
|---|---|---|---|---|
| SPR-010 Object | Provenance → API pública de identidade, somente em adaptador | `KnowledgeObjectId`; precedente de serializer | nenhuma automática | Object → Provenance proibida; referências desacopladas |
| SPR-011 Document | Provenance → API pública de identidade, somente em adaptador | `DocumentId` | nenhuma automática | Document → Provenance proibida |
| SPR-012 Relationship | Provenance → API pública, módulo de projeção | `CanonicalRelationship`, endpoint, factory, enum | explícita e com perda | Relationship → Provenance proibida |
| SPR-013 Graph | nenhuma dependência de produção | nenhum no núcleo | composição externa de relações projetadas | imports de Graph proibidos |
| SPR-014 Query | nenhuma | nenhum | nenhuma | Query fora do target enum |
| SPR-015 Index | nenhuma dependência de produção | IDs somente como texto canônico | nenhuma automática | alteração de Index proibida |
| SPR-016 Corpus | Provenance → `CorpusId` apenas em adaptador público | identidade/versão/digest declarados | nenhuma automática | Corpus → Provenance proibida |
| SPR-017 Provenance | internas relativas + stdlib + `cko.core.exceptions` | próprios contratos | operações puras | nenhum runtime/infra/import privado |

O núcleo de modelos e serializer DEVE trabalhar com referências próprias, evitando imports das fundações 010–016. Adaptadores públicos e projeção ficam em módulos periféricos do mesmo namespace. Essa divisão elimina ciclos e permite serialização independente.

## 41. API pública candidata

Todos os nomes obrigatórios DEVEM estar em `cko.core.provenance.__all__`. Como o padrão homologado reexporta fundações semânticas, eles DEVEM também ser reexportados por `cko.core` após auditoria automática de colisões. Nenhum nome genérico como `Reference`, `Actor`, `Activity`, `Evidence`, `Version`, `Factory` ou `Serializer` será publicado.

| Família | Símbolos obrigatórios |
|---|---|
| constantes | `PROVENANCE_SCHEMA_VERSION`, `PROVENANCE_SERIALIZATION_VERSION`, `PROVENANCE_UUID_NAMESPACE`, `PROVENANCE_VERSION` |
| enums | os sete enums da seção 17 |
| identidade/modelos | os treze modelos da seção 15 |
| serviços | `ProvenanceStatementFactory`, `ProvenanceStatementValidator`, `DeterministicProvenanceSerializer`, `ProvenanceOperations` |
| erros | `ProvenanceError`, `ProvenanceValidationError`, `ProvenanceSerializationError`, `ProvenanceFactoryError`, `ProvenanceIdentityError`, `ProvenanceVersionError`, `ProvenanceDigestError`, `ProvenanceChainError` |

Protocolos públicos de serializer/validator/factory são **opcionais e rejeitados para a primeira implementação**, pois não existe consumidor público que os exija. Helpers, payloads, sort tokens, adaptadores internos e funções duplicadas são internos.

## 42. Inventário e classificação de símbolos

| Símbolo/grupo | Namespace | Estabilidade futura | Raiz | Colisão | Classificação/justificativa |
|---|---|---|---|---|---|
| constantes `PROVENANCE_*` | provenance | estável | sim | nenhuma encontrada | público obrigatório; versões/UUID observáveis |
| enums `Provenance*` | provenance | estável | sim | nenhuma encontrada | público obrigatório; vocabulário fechado |
| `ProvenanceStatementId/Identity` | provenance | estável | sim | nenhuma | público obrigatório; identidade reproduzível |
| referências tipadas | provenance | estável | sim | nenhuma | público obrigatório; impedem troca de papel |
| `ProvenanceQualifier` | provenance | estável | sim | nenhuma | público obrigatório; extensão estruturada controlada |
| `ProvenanceStatementVersion` | provenance | estável | sim | nenhuma | público obrigatório; separa versão lógica |
| `ProvenanceStatement` | provenance | estável | sim | não colide com `KnowledgeProvenance` | público obrigatório; agregado |
| resultados de comparação/cadeia | provenance | estável | sim | nenhuma | público obrigatório; retorno tipado |
| Factory/Validator/Serializer/Operations | provenance | estável | sim | nomes prefixados | público obrigatório; fronteiras oficiais |
| oito exceções | provenance | estável | sim | nenhuma encontrada | público obrigatório; granularidade alinhada ao CORE |
| protocolos | provenance | não publicados | não | — | rejeitados inicialmente |
| builder e snapshot | — | — | não | — | rejeitados por redundância |
| helpers/aliases | interno | interno | não | — | não exportar |

O inventário final DEVE ser gerado do código implementado. Esta especificação não presume o total final de símbolos na raiz.

## 43. Exceções

| Exceção | Base | Condição e informação preservada | Visibilidade |
|---|---|---|---|
| `ProvenanceError` | `CKOError` | raiz com código, modelo, campo e detalhes seguros | pública |
| `ProvenanceValidationError` | `ProvenanceError`, `ValueError` | categoria, sujeito, referência, ator, atividade, evidência, papel, duplicidade ou campo inválido | pública |
| `ProvenanceSerializationError` | `ProvenanceError` | UTF-8/JSON/envelope/campo/discriminador/schema não canônico | pública |
| `ProvenanceFactoryError` | `ProvenanceError` | construção direta ou composição inválida | pública |
| `ProvenanceIdentityError` | `ProvenanceValidationError` | UUID, namespace, chave ou recomputação divergente | pública |
| `ProvenanceVersionError` | `ProvenanceValidationError` | SemVer, revisão, versão anterior ou compatibilidade inválida | pública |
| `ProvenanceDigestError` | `ProvenanceValidationError` | formato ou recomputação SHA-256 divergente | pública |
| `ProvenanceChainError` | `ProvenanceValidationError` | self, ciclo, referência conflitante ou conjunto duplicado | pública |

Não haverá exceções separadas para cada enum ou papel: `ProvenanceValidationError` com campo/código comunica esses casos. Campo desconhecido pertence à serialização. Referência malformada pertence à validação; digest malformado usa `ProvenanceDigestError`.

## 44. Retrocompatibilidade

1. Nenhum símbolo 1.0.0 será removido ou substituído.
2. Assinaturas e discriminadores existentes serão capturados antes/depois da implementação.
3. `KnowledgeProvenance`, `KnowledgeMetadata.provenances`, `KnowledgeContent.derived_from`, autoria/fontes de Document e enums/aliases de Relationship serão testados sem alteração.
4. Imports das SPR-010–016 pela raiz e subnamespaces permanecerão válidos.
5. Os 610 exports únicos observados formam baseline mínimo de preservação, não total futuro contratado.
6. A nova API será estritamente aditiva e prefixada.
7. Schemas e serializers antigos não receberão campos da SPR-017.
8. Nenhuma migração ou adaptação implícita será executada.

## 45. Correção futura do catálogo público

`CKO_CORE_V1_PUBLIC_API_CATALOG.md` declara 334 símbolos e versão 0.1.0, enquanto a API real inspecionada possui 610 símbolos únicos e versão 1.0.0. `CKO_CORE_V1_DEPENDENCY_MATRIX.md` também não inventaria nominalmente as SPR-010–015 em sua matriz principal.

A futura implementação DEVE, antes do freeze/homologação:

1. extrair `cko.core.__all__` e cada `__all__` por execução isolada;
2. verificar nomes únicos, resolvidos, aliases e origem de cada símbolo;
3. preservar nominalmente todos os exports do baseline;
4. atualizar versão de pacote/fachada efetivamente autorizada;
5. inventariar nominalmente SPR-010–017 e aliases;
6. atualizar a matriz principal com dependências SPR-010–017;
7. comparar catálogo gerado, source e wheel instalado;
8. registrar o total efetivo apurado, sem estimativa baseada nesta proposta.

O catálogo NÃO foi corrigido nesta etapa por restrição expressa do escopo.

## 46. Plano de testes

A suíte dedicada `tests/test_knowledge_provenance_statement_foundation_spr017.py` DEVE cobrir:

- construção válida de todos os modelos, frozen/slots, igualdade e hashing;
- UUIDv5 e namespace exclusivo; reprodução e não colisão;
- todas as categorias, tipos e papéis; valores desconhecidos;
- sujeito, referências heterogêneas, múltiplas fontes, atores e atividade;
- evidências versus digest e autoria versus atribuição;
- derivações heterogêneas versus versão/snapshot;
- qualificadores, deep freeze, NFC, UTC e rejeição de floats ambíguos;
- regras por categoria, duplicidade, self e papéis incompatíveis;
- cadeia vazia, simples, múltipla, externa, conflitante e cíclica;
- versão de schema, serialização, fundação, declaração e alvos;
- revisão válida/inválida e versão anterior separada de predecessor;
- canonicalização, ordenação, digest, adulteração e reordenação não semântica;
- serialização/desserialização de cada discriminador, round-trip e bytes idênticos;
- rejeição de UTF-8, JSON, chaves duplicadas, campos ausentes/desconhecidos, tipos, enums, versões, UUIDs e hashes inválidos;
- todas as operações puras e garantia de não mutação;
- comparação determinística e resultado ordenado;
- projeção Relationship permitida, recusada, n-ária e perda semântica;
- integração pública 010–016 e ausência de imports privados/reversos;
- `KnowledgeProvenance` e demais contratos antigos intactos;
- ausência de I/O, rede, runtime, persistence, storage, repository, Graph update, Index update e Corpus update;
- exports do subnamespace/raiz, catálogo atualizado e inexistência de colisões;
- regressão, build, wheel, instalação limpa, imports e SHA-256.

Execuções obrigatórias: suíte dedicada; conjunto SPR-010–017; regressão integral; cobertura; auditoria AST/import; build oficial; inspeção ZIP/RECORD/METADATA; instalação em ambiente limpo; smoke test isolado; hash SHA-256.

## 47. Validações arquiteturais automatizadas

Gates futuros:

1. AST confirma apenas stdlib, `cko.core.exceptions` e APIs públicas permitidas.
2. Grafo de imports não contém SCC nem dependência reversa.
3. busca por módulos proibidos retorna zero import no namespace.
4. monkeypatch de `open`, sockets, filesystem, subprocess e clientes externos confirma que operações não os chamam.
5. inspeção pública confirma namespace isolado e ausência de helpers em `__all__`.
6. snapshots, builders, inventory extensions e nomes proibidos estão ausentes.
7. `KnowledgeProvenance` mantém identidade de classe, assinatura e serializer.
8. Relationship é apenas saída explícita de projeção; Graph/Index/Corpus não são atualizados.
9. Query não aparece no enum de alvo e Inventory não é importado.
10. digest é descrito/testado somente como integridade.
11. autoria/atribuição e derivação/versionamento possuem testes negativos.
12. catálogo gerado coincide com source e wheel.

## 48. Cobertura

Mínimo obrigatório: **95% de linhas** em `cko.core.provenance` e **90% de branches**. Meta de engenharia: 95% de branches, coerente com a SPR-016. O gate de 90% reconhece ramificações defensivas legítimas sem autorizar testes artificiais; toda branch crítica de identidade, digest, schema, cadeia, categoria, serialização e fronteira arquitetural DEVE ser exercitada independentemente do percentual global.

A regressão não pode introduzir falha nova. As duas falhas históricas só podem ser aceitas se reproduzidas e demonstradas fora do namespace.

## 49. Documentação futura

| Documento | Conteúdo mínimo obrigatório |
|---|---|
| `SPR017_IMPLEMENTATION_REPORT.md` | arquivos, API efetiva, testes, cobertura, regressão, build, wheel, hash, desvios e status |
| `CKO_PROVENANCE_STATEMENT_ARCHITECTURE.md` | responsabilidade, modelo, invariantes, dependências, exclusões e decisões |
| `CKO_PROVENANCE_STATEMENT_API.md` | símbolos, campos, construção, erros, exports e estabilidade |
| `CKO_PROVENANCE_STATEMENT_MODEL_GUIDE.md` | categorias, papéis, referências, autoria, derivação, evidência e exemplos estruturais sem I/O |
| `CKO_PROVENANCE_STATEMENT_SERIALIZATION.md` | envelopes, NFC, JSON canônico, versões, digest, rejeições e round-trip |
| `CKO_PROVENANCE_STATEMENT_OPERATIONS.md` | operações puras, pré/pós-condições, complexidade, versão e digest |
| `CKO_PROVENANCE_STATEMENT_INTEGRATION.md` | matriz 010–017, adapters, projeção Relationship e perdas |

Documentos gerais serão alterados apenas para registrar fundação, dependências, exports, catálogo, versão autorizada, artefato e SHA-256. Documentação homologada não será reescrita sem necessidade e a auditoria pré-implementação permanecerá imutável.

## 50. Build e wheel

Após implementação e autorização de versão:

1. executar suítes e gates de cobertura antes do build;
2. executar `CKO_BUILD.cmd` e exigir exit code zero;
3. localizar exatamente o wheel da versão autorizada;
4. inspecionar ZIP, paths, timestamps, `METADATA`, `WHEEL` e `RECORD`;
5. confirmar todos os módulos `cko/core/provenance/*.py` esperados;
6. confirmar ausência de testes, caches, `.pyc/.pyo`, temporários e arquivos indevidos;
7. comparar exports de source e wheel;
8. instalar em ambiente limpo sem source no path;
9. executar imports isolados e smoke de identidade, digest e round-trip;
10. calcular SHA-256, tamanho e contagem de entradas;
11. registrar evidências no relatório.

Nenhum novo wheel é produzido por esta especificação.

## 51. Versionamento semântico do SDK

Adicionar uma API pública estável e inteiramente nova, preservando a API 1.0.0, caracteriza incremento **minor** segundo SemVer. Portanto, o impacto esperado é 1.1.0, condicionado à confirmação da política e à autorização formal na implementação. A versão da fundação inicia em 1.0.0, independentemente da versão do SDK. Esta especificação NÃO altera `pyproject.toml`, `cko.core.__version__`, metadata ou nome do wheel.

## 52. Riscos e mitigação

| Risco | Impacto | Mitigação normativa |
|---|---|---|
| colisão com `KnowledgeProvenance` | crítico | nomes distintos, teste de assinatura/export e sem alias |
| chave semântica mal governada | identidades distintas para mesma intenção | documentação, NFC e escopo de namespace; igualdade não é inferida |
| confundir declaração com verdade | confiança indevida | linguagem explícita, evidence declarada e zero verificação |
| ciclos parciais fora do conjunto | cadeia global não demonstrada | resultado informa fronteiras; nenhuma alegação de validação global |
| proliferação de enums | incompatibilidade futura | valores mínimos fechados e evolução por schema |
| perda na projeção binária | semântica incompleta | projeção opcional, não reversível e perda documentada |
| catálogo desatualizado | quebra invisível | inventário automatizado obrigatório antes do freeze |
| API raiz extensa | colisão cognitiva | nomes prefixados e auditoria de todos os 610 símbolos baseline |
| branch coverage defensiva | falsa segurança | gates críticos explícitos além do percentual |
| timestamp declarado | interpretação operacional | opcional, incluído no digest, nunca capturado automaticamente |

## 53. Limitações

- A fundação não comprova existência, identidade real, autoria, origem ou causalidade.
- Validação de cadeia cobre somente o conjunto finito recebido.
- Referências externas permanecem opacas.
- Não há consulta, travessia, merge, resolução de conflito ou sincronização.
- Projeção para Relationship perde semântica e não é reversível.
- Metadata antiga e statements podem contradizer-se; a fundação preserva ambas como declarações, sem escolher verdade.
- Não há snapshot, builder, persistência, migração ou upgrade operacional.

## 54. Critérios de aceite da futura implementação

1. Fundação independente implementada em `cko.core.provenance`.
2. Responsabilidade exclusiva preservada.
3. Nenhuma responsabilidade proibida introduzida.
4. Nome oficial e terminologia adotados.
5. `KnowledgeProvenance` preservado integralmente.
6. Todos os contratos públicos do baseline preservados.
7. Modelos públicos frozen/slotted e profundamente imutáveis.
8. Agregado construído somente pela Factory.
9. Declaração canônica possui identidade própria.
10. Sujeito tipado é obrigatório e único.
11. Múltiplas fontes são suportadas.
12. Atores são somente declarativos.
13. Atividade é somente declarativa e singular.
14. Evidências são declaradas e não verificadas.
15. Categorias e papéis fechados estão implementados.
16. Regras específicas por categoria são aplicadas.
17. Referências não carregam nem resolvem alvos.
18. Encadeamento vazio, simples e múltiplo funciona.
19. Autorreferência é rejeitada.
20. Ciclos no conjunto fornecido são rejeitados.
21. Fronteiras externas são relatadas sem resolução.
22. Autoria descritiva permanece separada de atribuição.
23. Derivação permanece separada de sucessão de versão.
24. Evidência permanece separada de digest.
25. Digest é descrito somente como integridade.
26. UUIDv5 usa o namespace registrado.
27. Namespace UUID é reproduzível e não colide.
28. Mudança de sujeito/categoria gera nova identidade.
29. Revisão semântica mantém identidade e incrementa revisão.
30. Schema, serialização, fundação, declaração, alvo e SDK são versões distintas.
31. Canonicalização NFC/UTF-8 é determinística.
32. JSON fechado e canônico é implementado.
33. Campos desconhecidos e chaves duplicadas são rejeitados.
34. Round-trip integral e byte a byte é aprovado.
35. SHA-256 é reproduzível e validado.
36. Reordenação não semântica preserva digest.
37. Alteração semântica muda digest.
38. Operações são puras e não mutam entradas.
39. Snapshot não é introduzido.
40. Builder não é introduzido na API inicial.
41. Relationship é somente projeção explícita opcional.
42. Perda da projeção é testada e documentada.
43. Graph permanece apenas projeção e não é atualizado.
44. Index permanece apenas projeção e não é atualizado.
45. Corpus não se torna autoridade nem é atualizado.
46. Query permanece fora do núcleo.
47. Inventory não é estendido.
48. Integração usa somente contratos públicos.
49. Nenhum import privado existe.
50. Nenhuma dependência reversa ou ciclo existe.
51. Nenhum I/O, rede, runtime, storage, repository ou persistence existe.
52. API pública corresponde ao inventário aprovado.
53. Todos os novos nomes são livres de colisão real.
54. Exports do namespace e raiz são coerentes.
55. Catálogo público é corrigido a partir da API efetiva.
56. Matriz de dependências principal é atualizada.
57. Versão SemVer do SDK é autorizada e aplicada consistentemente.
58. Suíte dedicada é integralmente aprovada.
59. Integração SPR-010–017 é integralmente aprovada.
60. Regressão integral não possui falha nova.
61. Cobertura atinge 95% de linhas e 90% de branches.
62. Branches críticas são testadas independentemente do percentual.
63. Auditorias arquiteturais automatizadas são aprovadas.
64. Build oficial termina com exit code zero.
65. Wheel contém módulos esperados e nenhum arquivo indevido.
66. Instalação limpa e smoke test isolado são aprovados.
67. SHA-256, tamanho e conteúdo do wheel são registrados.
68. Documentação futura mínima está completa.
69. Nenhum schema antigo é alterado.
70. Nenhuma migração automática é criada.
71. As duas falhas históricas, se presentes, são reproduzidas sem regressão nova.
72. Nenhuma Sprint posterior é antecipada.

## 55. Sequência futura condicionada, sem autorização atual

Esta sequência só inicia após autorização formal:

1. congelar a especificação aprovada e registrar baseline Git/API;
2. corrigir catálogo e matriz documental a partir da API real, preservando exports;
3. criar namespace isolado, contratos, enums, erros e modelos auxiliares;
4. implementar identidade/UUID, Factory e invariantes;
5. implementar canonicalização, digest e serializer estrito;
6. implementar operações puras, cadeia e comparação;
7. implementar adaptadores explícitos e projeção Relationship;
8. publicar exports após auditoria de colisão;
9. criar documentação e suíte dedicada;
10. executar integração, regressão, cobertura e auditorias arquiteturais;
11. aplicar versão SemVer somente com autorização;
12. executar build, inspeção, instalação limpa, smoke e SHA-256;
13. emitir relatório e interromper para homologação formal.

Nenhuma etapa autoriza iniciar Sprint posterior.

## 56. Hierarquia normativa interna

As seções 57–92 fecham os schemas, payloads, operações, fixtures, critérios e testes referidos nas seções anteriores. Elas integram esta especificação integral e prevalecem sobre formulação anterior menos específica. Não há decisão pendente.

## 57. Schemas fechados dos 13 modelos

Convenções comuns: todos os modelos são públicos, `dataclass(frozen=True, slots=True, kw_only=True)`, fortemente tipados e profundamente imutáveis. Todos contêm `schema_version: str = "1.0"` e `serialization_version: str = "1.0"`; outro valor é rejeitado. `None` é o único ausente. Igualdade e hash usam todos os campos; somente `ProvenanceStatementId` tem `order=True`. Tuplas são copiadas, normalizadas e ordenadas quando semanticamente não ordenadas. Não há `dict` livre, atributo dinâmico ou extensão de schema. O token privado `InitVar` que restringe a construção de `ProvenanceStatement` não é campo público, não participa de igualdade/hash/digest e não aparece no envelope.

| Modelo / módulo | Responsabilidade exclusiva | Campos exatos, cardinalidade e defaults | Identidade, digest, envelope e erros |
|---|---|---|---|
| `ProvenanceStatementId` / `identity.py` | ID estável | `value: UUID` obrigatório | UUIDv5/variante RFC 4122; participa de igualdade, hash, digest e envelope; IdentityError |
| `ProvenanceStatementIdentity` / `identity.py` | vincular ID à linhagem | `statement_id`; `business_namespace: str`; `lineage_key: str` | textos NFC/trimmed/não vazios; ID recomputável; todos entram no digest/envelope |
| `ProvenanceQualifier` / `models.py` | par declarativo fechado | `name: str`; `value: CanonicalValue` | nome único por proprietário; valor da seção 62; integral no digest |
| `ProvenanceSubjectRef` / `references.py` | único sujeito | `target_type: ProvenanceTargetType`; `namespace: str`; `target_id: str`; `target_canonical_id: str|None=None`; `target_external_id: str|None=None`; `target_version: str|None=None`; `target_digest: str|None=None`; versões comuns | somente `target_type`, `namespace` e `target_id` entram no statement ID; todos os campos entram no envelope e digest |
| `ProvenanceEntityRef` / `references.py` | entidade participante | `target_type: ProvenanceTargetType`; `namespace: str`; `target_id: str`; `role: ProvenanceEntityRole`; `target_canonical_id: str|None=None`; `target_external_id: str|None=None`; `target_version: str|None=None`; `target_digest: str|None=None`; versões comuns | sujeito idêntico proibido; duplicidade integral proibida; todos os campos entram no envelope e digest |
| `ProvenanceActorRef` / `references.py` | ator declarado | `actor_type`; `namespace`; `actor_id`; `role`; `actor_version: str|None=None`; `actor_digest: str|None=None` | opaco; identidade+papel únicos; todos digeridos |
| `ProvenanceActivityRef` / `references.py` | atividade declarada singular | `activity_type`; `namespace`; `activity_id`; `label: str|None=None`; `started_at: datetime|None=None`; `ended_at: datetime|None=None`; `qualifiers=()` | fim ≥ início; `other_declared` exige label e qualifier `vocabulary`; todos digeridos |
| `ProvenanceEvidenceRef` / `references.py` | suporte alegado | `evidence_type`; `namespace`; `evidence_id`; `evidence_version: str|None=None`; `evidence_digest: str|None=None`; `qualifiers=()` | nunca resolvido; duplicidade integral proibida; todos digeridos |
| `ProvenanceStatementRef` / `references.py` | nó referenciado completo | `statement_id`; `revision: int`; `statement_version: str`; `digest: str` | nenhum opcional; revisão positiva; SemVer/digest válidos; chave ID@revisão |
| `ProvenanceStatementVersion` / `versioning.py` | estado ordinal | `statement_version: str="1.0.0"`; `revision: int=1`; `previous_revision: ProvenanceStatementRef|None=None` | raiz exige nulo; revisão n exige ref n−1, mesmo ID e digest diferente; VersionError |
| `ProvenanceStatement` / `models.py` | agregado | `identity: ProvenanceStatementIdentity`; `category: ProvenanceStatementCategory`; `subject: ProvenanceSubjectRef`; `version: ProvenanceStatementVersion`; `digest: str`; `entities: tuple de ProvenanceEntityRef=()`; `actors: tuple de ProvenanceActorRef=()`; `activity: ProvenanceActivityRef|None=None`; `evidence: tuple de ProvenanceEvidenceRef=()`; `predecessors: tuple de ProvenanceStatementRef=()`; `qualifiers: tuple de ProvenanceQualifier=()`; `declared_at: datetime|None=None`; `foundation_version: str="1.0.0"`; versões comuns | ordem compilável e keyword-only; factory-only; digest excluído apenas do payload de cálculo; todo o restante participa |
| `ProvenanceStatementComparisonResult` / `results.py` | diferença estrutural | `same_identity: bool`; `left_node_key`; `right_node_key`; `same_digest: bool`; `changed_fields: tuple homogênea de str` | paths JSON únicos/ordenados; serializável/hashable |
| `ProvenanceChainValidationResult` / `results.py` | validação finita aprovada | `node_keys`; `root_keys`; `external_predecessors`; `components`; `edge_count: int` | tuplas ordenadas; múltiplas raízes/componentes válidos; nunca representa resultado inválido |

`CanonicalValue` é a união interna fechada `None | bool | int | str | CanonicalArray | CanonicalObject`. `CanonicalArray` é tipo privado com `values: tuple de CanonicalValue`; representa sequência ordenada, profundamente imutável e possivelmente heterogênea. `CanonicalObject` é tipo privado distinto com `entries: tuple ordenada de pares (str, CanonicalValue)`, ordenado pela chave NFC. Array e objeto nunca são inferidos exclusivamente da estrutura de uma tuple. Entrada JSON array normaliza para `CanonicalArray`; entrada JSON object normaliza para `CanonicalObject`; tuple pública ambígua é rejeitada. Ambos têm igualdade/hash estruturais com o discriminador do tipo. Tipos proibidos incluem float, Decimal, bytes, bytearray, datetime, list/dict retidos sem normalização, set, frozenset e objeto arbitrário. `bool` é tratado antes de `int`; inteiros ficam entre −9007199254740991 e 9007199254740991. Texto e chaves usam NFC; duas chaves que colidam após NFC são rejeitadas. `None` serializa como `null`. C-02 é o `CanonicalArray((None,True,False,0,-12))` válido e serializa exatamente `[null,true,false,0,-12]`.

## 58. Normalização dos IDs de alvo

| `target_type` | representação de `target_id` |
|---|---|
| `knowledge_object` | UUID canônico de `KnowledgeObjectId.value` |
| `document` | UUID canônico de `DocumentId.value` |
| `relationship` | UUID canônico de `RelationshipId.value` |
| `graph` | UUID canônico de `GraphId.value` |
| `index` | UUID canônico de `IndexId.value` |
| `corpus` | UUID canônico de `CorpusId.value` |
| `external_resource` | URI absoluta NFC preservada, sem acesso de rede |

UUID usa lowercase e hífens. Namespace e string usam NFC, trim de bordas, não vazio e nenhum controle. `target_version` é SemVer opcional; `target_digest` é SHA-256 lowercase opcional. Ausência é `null`, nunca string vazia.

## 59. Matriz total categoria–atividade–papéis

| Categoria | entidades permitidas e mínimo | atividade permitida e cardinalidade | atores permitidos e mínimo |
|---|---|---|---|
| `origin` | source/original/supporting_entity; ≥1 source/original | generation/copying/other_declared; 0..1 | creator/producer/responsible_party/publisher; ≥0 |
| `attribution` | supporting_entity; ≥0 | other_declared; 0..1 | creator/author/contributor/responsible_party/reviewer/publisher; ≥1 |
| `derivation` | source/input/original/contributing_source/supporting_entity; ≥1 dos quatro primeiros | transformation/adaptation/extraction/incorporation/copying/other_declared; 0..1 | contributor/producer/responsible_party/transformer; ≥0 |
| `generation` | source/input/contributing_source/supporting_entity; ≥0 | generation; exatamente 1 | creator/producer/responsible_party; ≥0 |
| `transformation` | source/input/original/contributing_source; ≥1 | transformation; exatamente 1 | contributor/producer/responsible_party/transformer; ≥0 |
| `adaptation` | source/input/original/contributing_source; ≥1 | adaptation; exatamente 1 | author/contributor/responsible_party/transformer; ≥0 |
| `extraction` | source/input/original; ≥1 | extraction; exatamente 1 | contributor/producer/responsible_party/transformer; ≥0 |
| `incorporation` | source/input/contributing_source; ≥1 | incorporation; exatamente 1 | contributor/producer/responsible_party/transformer; ≥0 |
| `source_usage` | source/contributing_source/supporting_entity; ≥1 source/contributing_source | copying/other_declared; 0..1 | author/contributor/responsible_party/publisher; ≥0 |

Combinação fora da linha é `ProvenanceValidationError`. O par identidade normalizada+papel é único; a mesma identidade pode exercer papéis distintos permitidos. `author` é autoria intelectual; `creator` é criação do artefato. Nenhum papel prova ação ou identidade. Os rótulos abreviados `supporting`, `responsible` e `other` não pertencem aos enums, não são serializáveis e são recusados pelas validações.

## 60. Identidade e token canônico do sujeito

Tipos aceitos são exatamente os sete da seção 58. O token canônico do sujeito é o JSON canônico do objeto fechado `{"namespace":"<namespace>","target_id":"<id>","target_type":"<enum>"}`. Não contém versão nem digest do alvo: atualizar a revisão externa preserva a identidade lógica; trocar ID lógico a altera.

O nome UUIDv5 exato é o JSON canônico, sem newline, do objeto:

`{"business_namespace":"<namespace>","category":"<categoria>","kind":"provenance_statement_identity","lineage_key":"<linhagem>","subject":<objeto-token>}`

`statement_id = UUIDv5(84c43be6-4bb5-52a8-9582-a2e8b04d797c, identity_name)`, com `identity_name` Unicode NFC codificado em UTF-8. Nenhum componente é nulo/vazio. Entidades, atores, atividade, evidências, antecedentes, qualificadores, instante, revisão, versões e digests são excluídos. Relógio, aleatoriedade, ordem de entrada, path e estado externo são proibidos.

| Vetor | entrada | resultado |
|---|---|---|
| I-01 | business_namespace `cko`; subject.namespace `cko`; linhagem `lineage-001`; derivation; Document `123e4567-e89b-12d3-a456-426614174000` | `d4e5aadf-9468-59aa-8076-28fe5e91642d` |
| I-02 | I-01 com qualquer target version/digest | mesmo UUID |
| I-03 | I-01 com categoria origin | `579a17ba-956d-57ba-a48d-4f829e30ee50` |
| I-04 | business_namespace `acervo`; subject.namespace `acervo`; linhagem NFC `café`; attribution; external URI `https://example.org/café` | `2ac58580-c9ec-5345-8eb0-d95f410cba82`; NFD converge |

O namespace é UUID versão 5, variante RFC 4122, derivado por UUIDv5(namespace URL, nome NFC `urn:cko:core:knowledge-provenance-statement-foundation`). É público, exclusivo e imutável. Mudá-lo é quebra de identidade major. O vetor de reprodução resulta em `84c43be6-4bb5-52a8-9582-a2e8b04d797c`.

## 61. Revisão, versões, referência anterior e chave dos nós

| Camada | inicial/regra | identidade | digest | serialização |
|---|---|---:|---:|---:|
| schema | `1.0`; muda forma/semântica fechada | não | sim | sim; desconhecida rejeitada |
| serialização | `1.0`; muda bytes | não | sim | sim; desconhecida rejeitada |
| fundação | SemVer `1.0.0`; muda API | não | sim | sim |
| declaração | `1.0.(revision−1)` no schema 1.0 | não | sim | sim |
| revisão | inteiro, inicia 1, incrementa exatamente 1 | não | sim | sim |
| alvo | SemVer opcional declarado | não | se presente | sim/null |
| SDK | 1.0.0 atual; futuro minor condicionado | não | não | fora do payload |

Assim, revisões 1, 2 e 3 usam versões 1.0.0, 1.0.1 e 1.0.2. `previous_revision` contém mesmo ID, revisão n−1, versão correspondente e digest anterior diferente. Raiz tem `None`. Alterar categoria, sujeito, business namespace ou linhagem cria outra identidade; revisar sem mudança declarativa é proibido.

A chave de nó é `<statement-id-lowercase>@<revision-decimal>`. Versão/digest validam a referência, mas não compõem a chave. Duas entradas com mesma chave e digest são duplicata; com digest diferente são conflito; ambas lançam `ProvenanceChainError`.

Há arestas causais do nó para `predecessors` e aresta de sucessão para `previous_revision`; os campos nunca se substituem. Predecessor com o mesmo statement ID em qualquer revisão é autorreferência proibida. Raízes, múltiplas raízes, múltiplos antecedentes, componentes desconectados e fronteiras externas são válidos. A validação examina integralmente somente o conjunto fornecido, rejeita ciclos diretos/indiretos detectáveis, inclusive combinações entre revisões/identidades, e relata referências ausentes como fronteiras sem resolvê-las. O nome obrigatório da operação é `validate_chain_in_supplied_set`.

## 62. Canonicalização completa e JSON canônico

| Tipo | regra normativa |
|---|---|
| codificação | UTF-8 estrito, sem BOM ou newline final; surrogates proibidos |
| Unicode | NFC antes de validar, comparar, ordenar ou serializar |
| strings de ID | trim de bordas, não vazias, sem controles |
| strings de valor | whitespace preservado; NFC |
| null/bool | `null`, `true`, `false` |
| inteiros | base 10, sem `+`; faixa −9007199254740991..9007199254740991; bool excluído |
| float/Decimal | proibidos, incluindo NaN, infinidades e zero negativo |
| data/hora | somente campos tipados; UTC `YYYY-MM-DDTHH:MM:SS.ffffffZ`, sempre seis dígitos; naive/precisão maior recusadas |
| UUID/enum/SemVer/SHA | formas canônicas lowercase; SemVer sem `v`; SHA com 64 chars |
| list/tuple | array; ordem semântica preservada; coleções set-like ordenadas antes |
| set/frozenset | proibidos como entrada |
| map | chaves string NFC únicas, ordenadas por code point; colisão pós-NFC é duplicata |
| opcionais | campo sempre presente como `null` |
| unknown/duplicate | rejeitados, inclusive chave duplicada pelo parser |

Chaves de objeto são lexicográficas por code point. Separadores são `,` e `:` sem whitespace. Unicode imprimível e `/` não são escapados. Aspas/barra usam escapes JSON; backspace/tab/LF/form feed/CR usam `\b`, `\t`, `\n`, `\f`, `\r`; outros controles usam `\u00xx` lowercase. JSON semanticamente equivalente mas não canônico é recusado por `from_json`.

| Vetor | entrada | saída/oráculo |
|---|---|---|
| C-01 | objeto b=1, a=`é` NFD | `{"a":"é","b":1}`; hex UTF-8 `7b2261223a22c3a9222c2262223a317d` |
| C-02 | null, bools, 0, −12 | `[null,true,false,0,-12]` |
| C-03 | instante | `2026-07-29T12:34:56.000007Z` |
| C-04 | texto com LF e aspas | `"linha\n\"x\""` |
| C-05 | chaves `é` NFC e NFD | `ProvenanceValidationError` por duplicidade pós-NFC |

## 63. Digest, envelopes e round-trip

SHA-256 incide nos bytes UTF-8 do envelope canônico `provenance_statement` com todos os campos, inclusive identidade, versões, foundation version e `declared_at`, excluindo somente `digest`. Resultado é hexadecimal lowercase sem prefixo. Digest ausente existe apenas durante construção interna. `verify_digest` usa comparação constante e retorna bool; `require_valid_digest` retorna `None` ou lança `ProvenanceDigestError`.

Todo envelope contém exatamente `model`, `schema_version`, `serialization_version` e os campos da seção 57. Discriminadores exatos: `provenance_statement_id`, `provenance_statement_identity`, `provenance_qualifier`, `provenance_subject_ref`, `provenance_entity_ref`, `provenance_actor_ref`, `provenance_activity_ref`, `provenance_evidence_ref`, `provenance_statement_ref`, `provenance_statement_version`, `provenance_statement`, `provenance_statement_comparison_result`, `provenance_chain_validation_result`. O agregado inclui `foundation_version`. Transporte inclui digest; payload de digest não.

Campo ausente/desconhecido, chave duplicada, tipo, discriminador, schema ou versão futura inválidos geram SerializationError; ID/revisão/digest divergentes usam erro específico. Não há fallback ou migração. `to_dict/from_dict` garantem round-trip estrutural e semântico; `to_json/from_json` exigem também bytes idênticos. Igualdade, hash, identidade, ordem, versão e digest são preservados.

Vetor D-01: I-01, revision 1, derivation, sem atores/atividade/evidências/antecedentes/qualificadores/instante, uma entidade source Document `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa`, IDs canônicos/externos, versões e digests de alvo nulos. O envelope integral, hex e regra de reprodução estão na seção 89. O envelope sem digest tem **1.309 bytes** e SHA-256 lowercase `dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d`; o envelope final tem 1.385 bytes. Mudar o role altera bytes e digest.

Digest é integridade, não identidade, assinatura, prova, confiança, verdade ou verificação externa.

## 64. Operações e serviços fechados

| Serviço | assinaturas conceituais completas | retorno/erros |
|---|---|---|
| Factory | `create(*, business_namespace: str, lineage_key: str, category: ProvenanceStatementCategory, subject: ProvenanceSubjectRef, entities: Iterable[ProvenanceEntityRef]=(), actors: Iterable[ProvenanceActorRef]=(), activity: ProvenanceActivityRef|None=None, evidence: Iterable[ProvenanceEvidenceRef]=(), predecessors: Iterable[ProvenanceStatementRef]=(), qualifiers: Iterable[ProvenanceQualifier]=(), declared_at: datetime|None=None) -> ProvenanceStatement`; `from_parts(*, identity: ProvenanceStatementIdentity, category: ProvenanceStatementCategory, subject: ProvenanceSubjectRef, version: ProvenanceStatementVersion, digest: str, entities: Iterable[ProvenanceEntityRef]=(), actors: Iterable[ProvenanceActorRef]=(), activity: ProvenanceActivityRef|None=None, evidence: Iterable[ProvenanceEvidenceRef]=(), predecessors: Iterable[ProvenanceStatementRef]=(), qualifiers: Iterable[ProvenanceQualifier]=(), declared_at: datetime|None=None, foundation_version: str="1.0.0") -> ProvenanceStatement` | `create` produz revisão 1/1.0.0; `from_parts` recalcula ID e digest e exige igualdade; códigos `PF001`, `PV001`–`PV009`, `PI001`, `PD001` |
| Validator | `validate(*, value: ProvenanceModel) -> None`; `validate_chain_in_supplied_set(*, statements: Iterable[ProvenanceStatement]) -> ProvenanceChainValidationResult` | sucesso retorna `None` ou resultado finito; falha usa `PV` ou `PC` específico |
| Serializer | `to_dict(*, value: ProvenanceModel) -> dict[str,CanonicalJSON]`; `from_dict(*, payload: Mapping[str,object]) -> ProvenanceModel`; `to_json(*, value: ProvenanceModel) -> bytes`; `from_json(*, payload: bytes) -> ProvenanceModel`; `canonical_bytes(*, value: ProvenanceModel, include_digest: bool=True) -> bytes`; `digest(*, statement: ProvenanceStatement) -> str` | retorno canônico exato; códigos `PS001`–`PS007` e `PD001` |
| Operations | assinaturas individuais abaixo | valores novos/resultados; nunca muta entrada |

Assinaturas de `ProvenanceOperations`: `revise(*, statement, entities, actors, activity, evidence, predecessors, qualifiers, declared_at) -> ProvenanceStatement`; `with_actor(*, statement, actor, declared_at)`, `without_actor(*, statement, actor, declared_at)`, `with_entity(*, statement, entity, declared_at)`, `without_entity(*, statement, entity, declared_at)`, `with_evidence(*, statement, evidence_ref, declared_at)`, `without_evidence(*, statement, evidence_ref, declared_at)`, `with_predecessor(*, statement, predecessor, declared_at)`, `without_predecessor(*, statement, predecessor, declared_at)`, `with_qualifier(*, statement, qualifier, declared_at)`, `without_qualifier(*, statement, qualifier, declared_at)`, `with_activity(*, statement, activity, declared_at)` e `without_activity(*, statement, declared_at)` retornam `ProvenanceStatement`; `compare(*, left, right) -> ProvenanceStatementComparisonResult`; `verify_digest(*, statement) -> bool`; `require_valid_digest(*, statement) -> None`; `validate_chain_in_supplied_set(*, statements) -> ProvenanceChainValidationResult`; `project_relationships(*, statement) -> tuple de CanonicalRelationship`. Todos os parâmetros após `*` são keyword-only e tipados pelos modelos homônimos; `declared_at` aceita `datetime|None` e é sempre explícito.

`revise` exige ao menos uma diferença entre os sete conteúdos recebidos e o valor anterior, mantém identidade/categoria/sujeito, cria `previous_revision` integral, incrementa revisão em um, mapeia versão para `1.0.(revision-1)` e recalcula digest. Cada `with_` rejeita duplicata com `PV004`; cada `without_` rejeita ausência com `PV008`; todos delegam semanticamente a `revise`, reordenam coleções, revalidam a matriz e não alteram a entrada. `compare` exige schema/serialização iguais, usa os paths raiz `/activity`, `/actors`, `/category`, `/declared_at`, `/entities`, `/evidence`, `/identity`, `/predecessors`, `/qualifiers`, `/subject`, `/version`, ordena os paths e inclui somente campos cujos envelopes diferem. O conjunto vazio de cadeia retorna `node_keys=()`, `root_keys=()`, `external_predecessors=()`, `components=()`, `edge_count=0`. Todas as operações são stateless, determinísticas, livres de I/O, relógio implícito, aleatoriedade, estado global e dependências proibidas.

As oito exceções permanecem públicas: `ProvenanceError(CKOError)` raiz; ValidationError também ValueError; SerializationError; FactoryError; IdentityError; VersionError; DigestError; ChainError. Códigos fechados: `PV001` tipo; `PV002` texto vazio/controle; `PV003` enum; `PV004` duplicata; `PV005` matriz/invariante; `PV006` tempo; `PV007` número/CanonicalValue; `PV008` membro ausente; `PV009` campo extra; `PS001` UTF-8/JSON; `PS002` chave JSON duplicada; `PS003` discriminador; `PS004` campo ausente/extra; `PS005` versão de schema/serialização; `PS006` JSON não canônico; `PS007` round-trip; `PF001` construção direta/estado inválido; `PI001` UUID/payload divergente; `PR001` SemVer/revisão; `PR002` referência anterior; `PD001` formato/recomputação de digest; `PC001` autorreferência; `PC002` nó duplicado/conflitante; `PC003` referência encontrada divergente; `PC004` ciclo. Mensagem mínima é `<código>:<modelo>:<campo>:<detalhe>`.

## 65. Projeção determinística para Relationship

`project_relationships(*, statement)` usa exclusivamente APIs públicas de `cko.core.relationships` e stdlib. É elegível quando categoria não é `attribution`; sujeito e todas as entidades são `knowledge_object` ou `document`; `target_id` e `target_canonical_id` são UUIDs; `target_version` e `declared_at` existem. `target_external_id` pode ser texto ou `null`; `target_digest` é preservado em metadata, pois `RelationshipEndpoint` não possui digest. `attribution` ou categoria válida sem entidades retorna tupla vazia. Qualquer outro target, canonical ID ausente, versão ausente ou instante ausente lança `ProvenanceValidationError` código `PV005`, campo `relationship_projection_not_representable`.

Produz uma relação por entidade, na ordem canônica, orientada entidade source → sujeito target. Origin/generation usam `GENERATED_INTO`; derivation/transformation/adaptation/extraction/incorporation/source_usage usam `DERIVED_INTO`.

Mapeamento fechado de cada target permitido: `knowledge_object` gera `RelationshipEndpoint(object_id=UUID(target_id), namespace=namespace, entity_type="knowledge_object", version=target_version, canonical_id=UUID(target_canonical_id), external_id=target_external_id)`; `document` gera os mesmos campos, mas `entity_type="canonical_document"`, valor exigido pelo adapter público real. Não há terceiro tipo permitido. Source usa a entidade; target usa o sujeito.

Direction é `DIRECTED` com roles `provenance_entity`/`provenance_subject`; constraint é `unique=True`, `multiplicity="many_to_one"` e demais flags `False`; strength é `UNKNOWN`. O `semantic_key` é exatamente `source.namespace|source.object_id|target.namespace|target.object_id|relationship_type|directed|many_to_one`, construído por `RelationshipValidator.build_semantic_key`. O namespace de `RelationshipIdentity` é `cko.core.provenance.projection`. `canonical_id` é UUIDv5 no namespace privado real Relationship `a899f825-bd53-4e68-b9d2-1e2597f2fc75`, com nome `<namespace>:<semantic_key>`, exatamente o resultado de `RelationshipId.canonical`. Identidades canônicas iguais para endpoints/tipo iguais representam coalescência semântica deliberada da Relationship Foundation, não colisão de statements; `logical_id` distingue integralmente statement, revisão e entidade.

O payload do `logical_id` é o objeto fechado `{"entity":{"namespace":namespace,"role":role,"target_id":target_id,"target_type":target_type},"kind":"relationship_projection_logical","relationship_type":relationship_type,"revision":revision,"statement_id":statement_id}`; UUIDv5 usa `PROVENANCE_UUID_NAMESPACE`. O payload do `version_id` é `{"kind":"relationship_projection_version","logical_id":logical_id,"revision":revision,"statement_digest":digest,"statement_version":statement_version}` no mesmo namespace. Alterar statement, revisão ou entidade muda logical ID; alterar conteúdo/digest/versão muda version ID; alterar apenas versão/digest de endpoint não muda canonical ID porque o validator real define semântica pelos endpoints lógicos/tipo/direção/multiplicidade.

Metadata: created/modified=`declared_at`; created_by=`provenance:<statement-id>`; ACTIVE; source=`cko.core.provenance`; attributes fechados e ordenados `category`, `entity_role`, `statement_digest`, `statement_id`, `statement_revision`. Version: `version_id` calculado, SemVer da declaração, mesmo instante/autor/status, `parent_version=null`. Descriptor label/description são `null`; evidence/weights são vazios. A construção obrigatória usa a assinatura real `RelationshipFactory.from_parts(*, identity, metadata, source, target, descriptor, version, evidence=(), weights=()) -> CanonicalRelationship`; `create` é proibida porque usa relógio e UUIDv4.

Preserva sujeito, entidade, direção, categoria mapeada, statement ID/revision/digest e instante. Perde atores, atividade detalhada, evidências, antecedentes, qualificadores e visão n-ária conjunta. Não é reversível, autoridade, automática ou parte do digest/ID da declaração. Duas execuções isoladas devem produzir bytes Relationship idênticos. Graph apenas compõe externamente essas relações.

## 66. Integração e dependências

| Fundação | direção/import permitido | preservado/perdido | decisão |
|---|---|---|---|
| Object | Provenance→adapter público de ID; KnowledgeProvenance somente leitura | ID/version/digest; objeto não carregado | sem reversa; contrato antigo intacto |
| Document | Provenance→ID público | referência; metadata não copiada | autoria não promovida |
| Relationship | Provenance→módulo periférico público | seção 65 | projeção com perda; não autoridade |
| Graph | nenhum import nuclear | relação projetada externamente | projeção, não autoridade |
| Query | nenhum | nada | fora do núcleo/target enum |
| Index | referência própria textual | ID/version/digest | não lê/atualiza |
| Corpus | referência própria textual | ID/version/digest | não autoridade/membro automático |
| Inventory | nenhum | nada | não alvo, import ou extensão |

Módulos candidatos: constants, enums, errors, contracts, identity, references, versioning, models, results, factory, validator, serializer, operations, relationship_projection e init. O núcleo depende apenas de stdlib e `cko.core.exceptions.CKOError`. Adaptadores usam IDs públicos; projection usa apenas os símbolos públicos descritos. São proibidos imports privados, reversos, ciclos, Runtime, Storage, Repository, banco, filesystem, rede, Discovery, Query, Inventory, acoplamento obrigatório a Graph/Index/Corpus, confiança, assinatura, políticas e Sprints posteriores.

## 67. API pública e compatibilidade

O inventário permanece 4 constantes + 7 enums + 13 modelos + 4 serviços + 8 exceções = **36 símbolos únicos**. Nenhum foi adicionado, removido ou reclassificado. Todos entram em `cko.core.provenance.__all__` e, após scan, em `cko.core`. Helpers são internos. Os 610 exports baseline, assinaturas, modelos, envelopes, digests, IDs, exceções, testes, fachadas, instalação e wheel devem permanecer. A futura mudança é aditiva.

Recomendação condicionada: SDK 1.0.0→1.1.0 MINOR. Após autorização, sincronizar pyproject, `cko.core.__version__`, egg-info/metadata, catálogo, CHANGELOG e wheel. Nada disso muda nesta tarefa.

## 68. Plano de testes com oráculos

| ID | requisito/nível/tipo | entrada | resultado, exceção e oráculo |
|---|---|---|---|
| T-001 | schemas/unit | mínimos/máximos 13 modelos | campos/defaults/frozen/slots/hash §57 |
| T-002 | tipagem/unit | bool como int, coleções mutáveis | ValidationError; §§57/62 |
| T-003 | matriz/unit | produto categoria×atividade×papéis | somente células §59 |
| T-004 | duplicidade/property | permutações | bytes/digest iguais; duplicata rejeitada |
| T-005 | identidade/golden | I-01–I-04 | UUID exato §60 |
| T-006 | revisão/unit | três revisões | mesmo ID; 1/2/3; versões/digests §61 |
| T-007 | namespace/golden | nome publicado | UUID exato §60 |
| T-008 | Unicode/unit | NFC/NFD/surrogate | convergência/rejeição §62 |
| T-009 | JSON/golden | C-01–C-05 | bytes/erros exatos §62 |
| T-010 | números/unit | limites/float/Decimal/NaN/infinito/−0 | domínio fechado §62 |
| T-011 | tempo/unit | offsets/naive/fração | UTC seis dígitos ou ValidationError |
| T-012 | digest/golden | D-01/adulterações | 1.309 bytes; `dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d`; false/DigestError §63/89 |
| T-013 | round-trip/unit | 13 discriminadores | estrutural/semântico/bytes §63 |
| T-014 | envelope/fuzz | unknown/missing/duplicate/future | SerializationError §63 |
| T-015 | refs/integration | sete target types | normalização §58, zero resolução |
| T-016 | evidência/unit | cinco tipos/duplicatas | opaca; sem I/O |
| T-017 | autoria/atribuição | metadata+statement | nenhuma promoção automática |
| T-018 | derivação/versão | parent/relação/statement | nenhuma inferência cruzada |
| T-019 | self/unit | mesmo ID em revisões | ChainError §61 |
| T-020 | ciclos/unit | direto/indireto/misto | ChainError no conjunto §61 |
| T-021 | parciais/unit | ausentes/raízes/componentes | resultado ordenado §61 |
| T-022 | projection/integration | elegíveis/attribution | relações exatas/vazio §65 |
| T-023 | projection/golden | duas execuções isoladas | bytes iguais; zero clock/UUID4 |
| T-024 | Graph/integration | relações projetadas | composição externa; sem import |
| T-025 | Index/Corpus/Inventory | sentinelas | zero update/autoridade/extensão |
| T-026 | Query/architecture | AST | zero import/target |
| T-027 | dependências/architecture | AST/SCC | allowlist; zero reversa/privado/ciclo |
| T-028 | API/compat | reflexão before/after | 610 preservados +36; zero colisão |
| T-029 | regressão/system | suíte integral | zero falha nova; duas históricas isoladas |
| T-030 | release/system | build/wheel/install/smoke | exit 0, conteúdo/export/hash coerentes |

Mínimos futuros: 95% linhas, 90% branches; meta 95% branches. Toda branch crítica de ID, schema, parser, digest, cadeia e projection é obrigatória. Nenhum teste é criado ou executado nesta reespecificação.

## 69. Documentação futura fechada

| Documento | momento/responsável lógico | conteúdo mínimo e conclusão |
|---|---|---|
| `SPR017_IMPLEMENTATION_REPORT.md` | pós-implementação/responsável Sprint | arquivos/API/testes/cobertura/build/wheel/hash/desvios; evidência reproduzível |
| Architecture | freeze/arquitetura | responsabilidade/modelo/dependências/riscos; coincide com código |
| API | freeze API/domínio | 36 símbolos/assinaturas/erros/exports; reflexão coincide |
| Model Guide | modelos/domínio | categorias/papéis/refs/casos; matriz completa |
| Serialization | serializer/domínio+serialização | envelopes/vectors/digest/round-trip; golden tests coincidem |
| Operations | operações/domínio | pré/pós/erros/complexidade/pureza; testes coincidem |
| Integration | integrações/arquitetura | matriz 010–017/projection/perdas; AST e testes coincidem |

Os nomes dos seis guias são exatamente os definidos na seção 49. Dependem de especificação aprovada e implementação autorizada; não são criados agora.

## 70. Riscos e limitações remanescentes

Catálogo e ARCH estão preexistente e documentalmente defasados; alvos podem ficar indisponíveis; ciclos externos são invisíveis; projection perde semântica; evidência pode ser mal interpretada; duas falhas históricas persistem. Mitigações: inventário automatizado antes do freeze, referências versionadas/digeridas, limites explícitos, golden vectors e regressão. Sem implementação não há cobertura/wheel novo. CORE-001 nominal e a fonte dos 52 mínimos não foram localizados; AC-001–052 abaixo constituem o mapa explícito 52→90.

## 71. Critérios de aceite verificáveis

Os 72 critérios anteriores são preservados e fechados abaixo; 18 critérios adicionais cobrem bloqueadores/altos. Para todos, a evidência deve constar do relatório futuro e o resultado necessário é aprovação sem divergência.

| ID | requisito/seção | evidência/teste |
|---|---|---|
| AC-001 | namespace independente §40/66 | import isolado |
| AC-002 | responsabilidade §9 | AST/review |
| AC-003 | exclusões §12 | guards/AST |
| AC-004 | nome §8 | API/docs |
| AC-005 | KnowledgeProvenance intacto §13 | identidade/signature/serializer |
| AC-006 | baseline §3/44 | diff/reflexão |
| AC-007 | frozen/slots §57 | T-001/002 |
| AC-008 | Factory exclusiva §64 | direct construction falha |
| AC-009 | identidade própria §60 | T-005 |
| AC-010 | sujeito único §57/58 | T-003/015 |
| AC-011 | múltiplas fontes §14 | unit |
| AC-012 | atores declarativos §20 | unit |
| AC-013 | atividade singular §14 | unit |
| AC-014 | evidência não verificada §32 | T-016 |
| AC-015 | enums fechados §17 | enum matrix |
| AC-016 | categorias §59 | T-003 |
| AC-017 | refs opacas §58 | I/O guards |
| AC-018 | cadeia básica §31/61 | T-021 |
| AC-019 | self rejeitado §61 | T-019 |
| AC-020 | ciclos rejeitados §61 | T-020 |
| AC-021 | fronteiras relatadas §61 | T-021 |
| AC-022 | autoria/atribuição §33 | T-017 |
| AC-023 | derivação/versão §34/61 | T-018 |
| AC-024 | evidência/digest §32/63 | T-016 |
| AC-025 | digest só integridade §63 | negative docs/test |
| AC-026 | UUIDv5 exato §60 | T-005/007 |
| AC-027 | namespace reproduzível §60 | golden/search |
| AC-028 | sujeito/categoria mudam ID §60 | property |
| AC-029 | revisão mantém ID §61 | T-006 |
| AC-030 | sete versões distintas §61 | unit |
| AC-031 | NFC/UTF-8 §62 | T-008 |
| AC-032 | JSON fechado §62/63 | T-009/014 |
| AC-033 | unknown/duplicate recusados §63 | T-014 |
| AC-034 | round-trip integral §63 | T-013 |
| AC-035 | SHA reproduzível §63 | T-012 |
| AC-036 | reordenação preserva digest §62 | T-004 |
| AC-037 | mutação muda digest §63 | T-012 |
| AC-038 | operações puras §64 | guards/property |
| AC-039 | sem snapshot §30 | API/AST |
| AC-040 | sem builder §29 | API/AST |
| AC-041 | Relationship só projection §65 | T-022 |
| AC-042 | perda explícita §65 | T-022 |
| AC-043 | Graph projeção §66 | T-024 |
| AC-044 | Index não atualizado §66 | T-025 |
| AC-045 | Corpus não autoridade §66 | T-025 |
| AC-046 | Query fora §66 | T-026 |
| AC-047 | Inventory intacto §66 | T-025 |
| AC-048 | APIs públicas §66 | AST |
| AC-049 | zero privado §66 | AST |
| AC-050 | zero reversa/ciclo §66 | SCC |
| AC-051 | zero infraestrutura §12/66 | guards |
| AC-052 | API 36 §41/67 | reflexão |
| AC-053 | zero colisão §67 | scan 610 |
| AC-054 | exports coerentes §67 | all |
| AC-055 | catálogo=source futuro §45 | generated diff |
| AC-056 | matriz futura atualizada §45 | doc audit |
| AC-057 | SemVer autorizado §67 | metadata |
| AC-058 | suíte dedicada §68 | test report |
| AC-059 | integração 010–017 §68 | T-015–026 |
| AC-060 | zero regressão nova §68 | T-029 |
| AC-061 | cobertura mínima §68 | coverage |
| AC-062 | branches críticas §68 | branch map |
| AC-063 | gates arquiteturais §47 | AST/SCC report |
| AC-064 | build exit 0 §50 | log |
| AC-065 | wheel íntegro §50 | ZIP/RECORD |
| AC-066 | install/smoke isolados §50 | clean env log |
| AC-067 | hash/tamanho registrados §50 | report |
| AC-068 | sete docs §69 | doc matrix |
| AC-069 | schemas antigos intactos §44 | diff/golden |
| AC-070 | zero migração §13/44 | AST/API |
| AC-071 | falhas históricas isoladas §3/70 | regression |
| AC-072 | zero Sprint posterior §12 | scope audit |
| AC-073 | 13 schemas exatos §57 | reflection schema |
| AC-074 | token sujeito exato §60 | I-01–I-04 |
| AC-075 | target version/digest fora do ID §60 | I-02 |
| AC-076 | referência anterior completa §61 | T-006 |
| AC-077 | chave ID@revision §61 | chain fixtures |
| AC-078 | garantia parcial limitada §61 | T-020/021 |
| AC-079 | matriz semântica total §59 | product matrix |
| AC-080 | tempo seis dígitos §62 | T-011 |
| AC-081 | números fechados §62 | T-010 |
| AC-082 | envelopes por discriminator §63 | T-013/014 |
| AC-083 | payload digest fixo §63 | D-01 |
| AC-084 | verify/require distintos §63/64 | unit |
| AC-085 | projection usa from_parts §65 | spy/AST |
| AC-086 | zero clock/UUID4 §65 | guard/golden |
| AC-087 | projection byte-idêntica §65 | T-023 |
| AC-088 | sete IDs de alvo §58 | T-015 |
| AC-089 | docs com dono/momento/critério §69 | review |
| AC-090 | API/catalog/source/wheel reconciliados §67 | release gate |

Quantidade normativa: **90 critérios**.

## 72. Rastreabilidade dos 19 achados

| ID/severidade | problema | decisão/seções | verificação |
|---|---|---|---|
| F-001/B | schemas | 13 schemas fechados §57 | AC-073/T-001/013 |
| F-002/B | token sujeito | payload/vectors §60 | AC-074/075 |
| F-003/B | revisão/chave | §61 | AC-076–078 |
| F-004/B | Relationship | from_parts/UUIDv5 §65 | AC-085–087 |
| F-005/A | matriz | §59 | AC-079/T-003 |
| F-006/A | tempo/qualifiers | §§57/62 | AC-080/081 |
| F-007/A | operações | §64 | AC-038/084 |
| F-008/A | catálogo/matriz | §§45/67 | AC-055/056/090 |
| F-009/A | envelopes/payload | §63 | AC-082/083 |
| F-010/M | IDs alvo | §58 | AC-088 |
| F-011/M | docs | §69 | AC-089 |
| F-012/M | origem 52 | AC-001–052 §71 | trace review |
| F-013/M | oráculos | §§60/62/63/68 | golden tests |
| F-014/Baixo | mojibake preexistente | §70; sem alteração autorizada | UTF-8 visual futuro |
| F-015/Baixo | ARCH 346 | §70; correção futura | AC-090 |
| F-016/Obs | hash anterior | §87 | hash final |
| F-017/Obs | 36 sem colisão | §67 | pre-export scan |
| F-018/Obs | UUID correto | §60 | T-007 |
| F-019/Obs | 878/880 | §70 | T-029 |

Os 11 grupos fechados são: schemas; identidade; revisão; matriz; canonicalização; envelopes; operações; Relationship; catálogo/matriz; docs/mapa; testes/aceite. Todos possuem decisão, contrato e verificação acima.

## 73. Autoria, atribuição e papéis de fronteira

Autoria documental permanece em metadata; atribuição intelectual exige statement attribution com ator author. Criador, responsible party, custódia, publicação, aprovação, transformação, extração e classificação são papéis distintos. Custódia física fica fora; reviewer representa revisão declarada; publisher publicação; transformer transformação. Nenhuma metadata é duplicada ou promovida automaticamente.

## 74. Derivação, versionamento e relações de domínio

Nova versão não é derivação; derivação não é nova versão; revisão não pode mudar o fato estrutural sem novo digest; predecessor não substitui Relationship; relação documental/Knowledge Object não se torna proveniência sem statement explícito. `previous_revision`, `predecessors`, `parent_version`, `derived_from` e Relationship são contratos diferentes.

## 75. Evidências e limites epistêmicos

Evidências são referências declaradas com tipo, namespace, ID, versão/digest e qualifiers. A fundação não acessa arquivo/rede, verifica assinatura/autenticidade, calcula confiança, interpreta conteúdo, executa política, declara verdade ou converte digest em prova.

## 76. Decisão final sobre snapshot

**NÃO ADOTAR.** O agregado já é imutável/versionado/digerido. Alvos ficam por referência; versão/digest apoiam reprodutibilidade, mas mutação/indisponibilidade externa limita reconstrução. Copiar estado externo violaria responsabilidade declarativa.

## 77. Pureza e complexidade

Criação/revisão/composição/comparação/digest/serializer/projection não têm efeito colateral. Canonicalização é linear; ordenações O(n log n); comparação linear após canonicalização; cadeia O(V+E). Nenhuma complexidade autoriza limite arbitrário oculto.

## 78. Validações arquiteturais futuras

AST allowlist; SCC; busca de módulos proibidos; guards de open/socket/subprocess/clock/UUID4; frozen/slots; all; identidade de classe/signature/serializer de KnowledgeProvenance; duas projections isoladas; catálogo source/wheel; clean install; regressão.

## 79. Estado documental do baseline

README/CHANGELOG contêm mojibake preexistente e ARCH/catalog têm contagens antigas. São fatos observados, não autorização de correção nesta tarefa. Código/reflexão prevalecem para 610 exports. A futura implementação deve reconciliar documentos antes do freeze, sem remover exports.

## 80. Semantic Versioning futuro

MINOR 1.0.0→1.1.0 é recomendação condicionada por API aditiva pública. Não há quebra autorizada. Arquivos futuros listados na seção 67 só mudam após gate e autorização.

## 81. Gates de release futuros

Suíte dedicada; integração 010–017; regressão; cobertura; arquitetura; build exit 0; inspeção ZIP/RECORD/METADATA; comparação source/wheel; instalação limpa; smoke isolado; SHA-256/tamanho/entradas; relatório. Nenhum gate é executado agora.

## 82. Sequência futura condicionada

Após nova auditoria, gate aprovado e autorização: congelar especificação/baseline; modelos/ID; canonicalização/envelopes/digest; operações/cadeia; projection; exports; testes/docs; regressão/cobertura; catálogo/matriz/ARCH/SemVer autorizados; build/wheel/install/hash; relatório; parar para homologação. Nenhuma Sprint posterior é iniciada.

## 83. Contagens finais da proposta

Constantes 4; enums 7; modelos 13; serviços 4; exceções 8; total 36. Modelos internos exportados: zero. Critérios: 90; grupos de testes: 30. Dos achados atuais, 5 bloqueadores, 4 altos e 1 médio foram corrigidos na especificação; o alto NF-007 e as divergências F-008/F-014/F-015 foram isolados como dependências documentais externas não alteráveis nesta tarefa; AF-004 foi corrigido pela convenção da seção 88.

## 84. Proibições finais

Não implementar nesta tarefa; não criar teste; não alterar versão/wheel/runtime/código/catalog/docs baseline; não declarar homologação; não autorizar codificação; não iniciar Sprint posterior; não prometer aciclicidade global; não tratar Relationship/Graph/Index/Corpus como autoridade.

## 85. Aptidão

Os schemas, token do sujeito, revisão/chave, projection, matriz, canonicalização, operações, envelopes e oráculos estão fechados. Desenvolvedores independentes podem produzir os mesmos IDs, bytes, digests e resultados sem nova decisão arquitetural.

## 86. Estado permitido

**REESPECIFICADA E PRONTA PARA NOVA AUDITORIA FORMAL.** Implementação continua dependente de nova auditoria, aprovação do gate e autorização posterior do CKO Architect.

## 87. Integridade desta reespecificação

O SHA-256 inicial confirmado desta execução é `38E22AB9D9C71F671C7EA2A8E715EF9BD5A57C53122051C5B84EF642941CC2CE`. O novo SHA-256, linhas, seções e UTF-8 são registrados no fechamento mecânico no chat, sem autorreferência no conteúdo e sem editar outro arquivo.

## 88. Convenção de contagem de linhas

“Linhas de conteúdo” é a quantidade retornada pela leitura textual, sem criar uma linha adicional para o newline terminal. “Segmentos físicos” conta o segmento vazio posterior ao newline terminal. O fechamento informa linhas de conteúdo; o arquivo deve terminar com exatamente um newline LF.

## 89. Vetores integrais de identidade e digest

Todos os JSON desta seção são uma única linha, sem newline, com chaves ordenadas, separadores mínimos, NFC e UTF-8 sem BOM. O algoritmo UUID é UUIDv5 com namespace `84c43be6-4bb5-52a8-9582-a2e8b04d797c` e nome igual ao JSON Unicode decodificado.

I-01 entrada por campo: `business_namespace="cko"`; `category="derivation"`; `kind="provenance_statement_identity"`; `lineage_key="lineage-001"`; `subject.namespace="cko"`; `subject.target_id="123e4567-e89b-12d3-a456-426614174000"`; `subject.target_type="document"`. JSON integral:

`{"business_namespace":"cko","category":"derivation","kind":"provenance_statement_identity","lineage_key":"lineage-001","subject":{"namespace":"cko","target_id":"123e4567-e89b-12d3-a456-426614174000","target_type":"document"}}`

Hex UTF-8 integral: `7b22627573696e6573735f6e616d657370616365223a22636b6f222c2263617465676f7279223a2264657269766174696f6e222c226b696e64223a2270726f76656e616e63655f73746174656d656e745f6964656e74697479222c226c696e656167655f6b6579223a226c696e656167652d303031222c227375626a656374223a7b226e616d657370616365223a22636b6f222c227461726765745f6964223a2231323365343536372d653839622d313264332d613435362d343236363134313734303030222c227461726765745f74797065223a22646f63756d656e74227d7d`. Resultado: `d4e5aadf-9468-59aa-8076-28fe5e91642d`. Propriedade: separa business namespace de subject namespace e exclui target version/digest.

I-02 usa todos os campos de I-01 e acrescenta ao objeto de domínio `subject.target_version="9.9.9"` e `subject.target_digest="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"`. Esses campos não entram no payload de identidade; JSON, hex e resultado permanecem exatamente os de I-01. Propriedade: versão e digest do alvo não mudam o statement ID.

I-03 troca somente `category` por `origin`. JSON integral:

`{"business_namespace":"cko","category":"origin","kind":"provenance_statement_identity","lineage_key":"lineage-001","subject":{"namespace":"cko","target_id":"123e4567-e89b-12d3-a456-426614174000","target_type":"document"}}`

Hex UTF-8 integral: `7b22627573696e6573735f6e616d657370616365223a22636b6f222c2263617465676f7279223a226f726967696e222c226b696e64223a2270726f76656e616e63655f73746174656d656e745f6964656e74697479222c226c696e656167655f6b6579223a226c696e656167652d303031222c227375626a656374223a7b226e616d657370616365223a22636b6f222c227461726765745f6964223a2231323365343536372d653839622d313264332d613435362d343236363134313734303030222c227461726765745f74797065223a22646f63756d656e74227d7d`. Resultado: `579a17ba-956d-57ba-a48d-4f829e30ee50`. Propriedade: categoria muda identidade.

I-04 entrada: business namespace `acervo`; subject namespace `acervo`; lineage `café`; category `attribution`; target type `external_resource`; target ID `https://example.org/café`. NFD é normalizado antes do payload. JSON integral:

`{"business_namespace":"acervo","category":"attribution","kind":"provenance_statement_identity","lineage_key":"café","subject":{"namespace":"acervo","target_id":"https://example.org/café","target_type":"external_resource"}}`

Hex UTF-8 integral: `7b22627573696e6573735f6e616d657370616365223a2261636572766f222c2263617465676f7279223a226174747269627574696f6e222c226b696e64223a2270726f76656e616e63655f73746174656d656e745f6964656e74697479222c226c696e656167655f6b6579223a22636166c3a9222c227375626a656374223a7b226e616d657370616365223a2261636572766f222c227461726765745f6964223a2268747470733a2f2f6578616d706c652e6f72672f636166c3a9222c227461726765745f74797065223a2265787465726e616c5f7265736f75726365227d7d`. Resultado: `2ac58580-c9ec-5345-8eb0-d95f410cba82`. Propriedade: NFC/NFD convergem.

D-01 envelope canônico integral sem `digest`:

`{"activity":null,"actors":[],"category":"derivation","declared_at":null,"entities":[{"model":"provenance_entity_ref","namespace":"cko","role":"source","schema_version":"1.0","serialization_version":"1.0","target_canonical_id":null,"target_digest":null,"target_external_id":null,"target_id":"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa","target_type":"document","target_version":null}],"evidence":[],"foundation_version":"1.0.0","identity":{"business_namespace":"cko","lineage_key":"lineage-001","model":"provenance_statement_identity","schema_version":"1.0","serialization_version":"1.0","statement_id":{"model":"provenance_statement_id","schema_version":"1.0","serialization_version":"1.0","value":"d4e5aadf-9468-59aa-8076-28fe5e91642d"}},"model":"provenance_statement","predecessors":[],"qualifiers":[],"schema_version":"1.0","serialization_version":"1.0","subject":{"model":"provenance_subject_ref","namespace":"cko","schema_version":"1.0","serialization_version":"1.0","target_canonical_id":null,"target_digest":null,"target_external_id":null,"target_id":"123e4567-e89b-12d3-a456-426614174000","target_type":"document","target_version":null},"version":{"model":"provenance_statement_version","previous_revision":null,"revision":1,"schema_version":"1.0","serialization_version":"1.0","statement_version":"1.0.0"}}`

Em D-01 e em todo envelope `1.0`, campos opcionais estão presentes e usam `null`; nenhuma omissão condicional é permitida.

Hex UTF-8 integral de D-01 sem digest: `7b226163746976697479223a6e756c6c2c226163746f7273223a5b5d2c2263617465676f7279223a2264657269766174696f6e222c226465636c617265645f6174223a6e756c6c2c22656e746974696573223a5b7b226d6f64656c223a2270726f76656e616e63655f656e746974795f726566222c226e616d657370616365223a22636b6f222c22726f6c65223a22736f75726365222c22736368656d615f76657273696f6e223a22312e30222c2273657269616c697a6174696f6e5f76657273696f6e223a22312e30222c227461726765745f63616e6f6e6963616c5f6964223a6e756c6c2c227461726765745f646967657374223a6e756c6c2c227461726765745f65787465726e616c5f6964223a6e756c6c2c227461726765745f6964223a2261616161616161612d616161612d346161612d386161612d616161616161616161616161222c227461726765745f74797065223a22646f63756d656e74222c227461726765745f76657273696f6e223a6e756c6c7d5d2c2265766964656e6365223a5b5d2c22666f756e646174696f6e5f76657273696f6e223a22312e302e30222c226964656e74697479223a7b22627573696e6573735f6e616d657370616365223a22636b6f222c226c696e656167655f6b6579223a226c696e656167652d303031222c226d6f64656c223a2270726f76656e616e63655f73746174656d656e745f6964656e74697479222c22736368656d615f76657273696f6e223a22312e30222c2273657269616c697a6174696f6e5f76657273696f6e223a22312e30222c2273746174656d656e745f6964223a7b226d6f64656c223a2270726f76656e616e63655f73746174656d656e745f6964222c22736368656d615f76657273696f6e223a22312e30222c2273657269616c697a6174696f6e5f76657273696f6e223a22312e30222c2276616c7565223a2264346535616164662d393436382d353961612d383037362d323866653565393136343264227d7d2c226d6f64656c223a2270726f76656e616e63655f73746174656d656e74222c227072656465636573736f7273223a5b5d2c227175616c696669657273223a5b5d2c22736368656d615f76657273696f6e223a22312e30222c2273657269616c697a6174696f6e5f76657273696f6e223a22312e30222c227375626a656374223a7b226d6f64656c223a2270726f76656e616e63655f7375626a6563745f726566222c226e616d657370616365223a22636b6f222c22736368656d615f76657273696f6e223a22312e30222c2273657269616c697a6174696f6e5f76657273696f6e223a22312e30222c227461726765745f63616e6f6e6963616c5f6964223a6e756c6c2c227461726765745f646967657374223a6e756c6c2c227461726765745f65787465726e616c5f6964223a6e756c6c2c227461726765745f6964223a2231323365343536372d653839622d313264332d613435362d343236363134313734303030222c227461726765745f74797065223a22646f63756d656e74222c227461726765745f76657273696f6e223a6e756c6c7d2c2276657273696f6e223a7b226d6f64656c223a2270726f76656e616e63655f73746174656d656e745f76657273696f6e222c2270726576696f75735f7265766973696f6e223a6e756c6c2c227265766973696f6e223a312c22736368656d615f76657273696f6e223a22312e30222c2273657269616c697a6174696f6e5f76657273696f6e223a22312e30222c2273746174656d656e745f76657273696f6e223a22312e302e30227d7d`.

Quantidade: 1.309 bytes. SHA-256 lowercase: `dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d`. O envelope final é o mesmo objeto com a chave lexicograficamente posicionada `"digest":"dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d"` entre `declared_at` e `entities`; possui 1.385 bytes. Reprodução: decodificar o hex, confirmar igualdade com o JSON UTF-8, confirmar comprimento, aplicar SHA-256, inserir o digest, serializar novamente e exigir round-trip byte a byte.

## 90. Fixtures integrais dos 13 modelos

Cada modelo rejeita campos extras, exige discriminador e versões, serializa todos os campos definidos na seção 57 e participa integralmente de igualdade/hash. Finalidade, base `object`, `frozen=True`, `slots=True`, `kw_only=True`, ordem de campos, tipos, defaults, normalização, invariantes, identidade, versão, revisão, digest, envelope, serialização, desserialização e códigos são os seguintes:

| Modelo | ordem dos campos públicos; obrigatoriedade/default | invariantes, identidade/digest e código |
|---|---|---|
| ProvenanceStatementId | `value: UUID`; `schema_version="1.0"`; `serialization_version="1.0"` | UUID versão 5/variante RFC; valor é identidade e entra no digest; `PI001` |
| ProvenanceStatementIdentity | `statement_id`; `business_namespace: str`; `lineage_key: str`; versões comuns | textos NFC/trim/não vazios; ID recomputado no agregado; todos entram no digest; `PI001`/`PV002` |
| ProvenanceQualifier | `name: str`; `value: CanonicalValue`; versões comuns | nome NFC/trim/não vazio; nome único no proprietário; valor normalizado; ambos no digest; `PV002`/`PV004`/`PV007` |
| ProvenanceSubjectRef | `target_type`; `namespace`; `target_id`; `target_canonical_id=None`; `target_external_id=None`; `target_version=None`; `target_digest=None`; versões comuns | tipos/IDs da seção 58; só primeiros três no ID, todos no digest; `PV001`–`PV003`/`PV005` |
| ProvenanceEntityRef | `target_type`; `namespace`; `target_id`; `role`; `target_canonical_id=None`; `target_external_id=None`; `target_version=None`; `target_digest=None`; versões comuns | identidade+papel única; não repete sujeito; todos no digest; `PV003`–`PV005` |
| ProvenanceActorRef | `actor_type`; `namespace`; `actor_id`; `role`; `actor_version=None`; `actor_digest=None`; versões comuns | identidade+papel única; textos NFC; todos no digest; `PV003`/`PV004` |
| ProvenanceActivityRef | `activity_type`; `namespace`; `activity_id`; `label=None`; `started_at=None`; `ended_at=None`; `qualifiers=()`; versões comuns | fim não precede início; `other_declared` exige label e qualifier `vocabulary`; tudo no digest; `PV005`/`PV006` |
| ProvenanceEvidenceRef | `evidence_type`; `namespace`; `evidence_id`; `evidence_version=None`; `evidence_digest=None`; `qualifiers=()`; versões comuns | referência opaca, integralmente única; tudo no digest; `PV003`/`PV004` |
| ProvenanceStatementRef | `statement_id`; `revision: int`; `statement_version: str`; `digest: str`; versões comuns | revisão positiva, versão `1.0.(n-1)`, SHA válido; chave ID@revision; `PR001`/`PD001` |
| ProvenanceStatementVersion | `statement_version`; `revision`; `previous_revision=None`; versões comuns | raiz 1/1.0.0/nulo; n exige n−1 integral; validada contra agregado; tudo no digest; `PR001`/`PR002` |
| ProvenanceStatement | ordem integral da seção 57; factories somente | matriz, ID, revisão e digest recalculados; próprio digest é o único campo fora do payload; `PF001` e erros específicos |
| ProvenanceStatementComparisonResult | `same_identity: bool`; `left_node_key: str`; `right_node_key: str`; `same_digest: bool`; `changed_fields: tuple de str=()`; `schema_version: str="1.0"`; `serialization_version: str="1.0"` | keys/paths NFC, únicos e ordenados; resultado não possui digest próprio; `PV001`/`PV004` |
| ProvenanceChainValidationResult | `node_keys: tuple de str=()`; `root_keys: tuple de str=()`; `external_predecessors: tuple de str=()`; `components: tuple de tuples de str=()`; `edge_count: int=0`; `schema_version: str="1.0"`; `serialization_version: str="1.0"` | coleções únicas/ordenadas, componentes ordenados, edge_count não negativo; só representa sucesso; `PV004`/`PV007` |

Vetores integrais mínimos V-01–V-13 são os JSON canônicos a seguir; `from_json(to_json(V-n)) == V-n`, hashes são iguais e os bytes reserializados são idênticos:

1. V-01 `{"model":"provenance_statement_id","schema_version":"1.0","serialization_version":"1.0","value":"d4e5aadf-9468-59aa-8076-28fe5e91642d"}`.
2. V-02 `{"business_namespace":"cko","lineage_key":"lineage-001","model":"provenance_statement_identity","schema_version":"1.0","serialization_version":"1.0","statement_id":{"model":"provenance_statement_id","schema_version":"1.0","serialization_version":"1.0","value":"d4e5aadf-9468-59aa-8076-28fe5e91642d"}}`.
3. V-03 `{"model":"provenance_qualifier","name":"sample","schema_version":"1.0","serialization_version":"1.0","value":[null,true,false,0,-12]}`.
4. V-04 `{"model":"provenance_subject_ref","namespace":"cko","schema_version":"1.0","serialization_version":"1.0","target_canonical_id":null,"target_digest":null,"target_external_id":null,"target_id":"123e4567-e89b-12d3-a456-426614174000","target_type":"document","target_version":null}`.
5. V-05 `{"model":"provenance_entity_ref","namespace":"cko","role":"source","schema_version":"1.0","serialization_version":"1.0","target_canonical_id":null,"target_digest":null,"target_external_id":null,"target_id":"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa","target_type":"document","target_version":null}`.
6. V-06 `{"actor_digest":null,"actor_id":"actor-1","actor_type":"person","actor_version":null,"model":"provenance_actor_ref","namespace":"cko","role":"author","schema_version":"1.0","serialization_version":"1.0"}`.
7. V-07 `{"activity_id":"activity-1","activity_type":"other_declared","ended_at":null,"label":"declared","model":"provenance_activity_ref","namespace":"cko","qualifiers":[{"model":"provenance_qualifier","name":"vocabulary","schema_version":"1.0","serialization_version":"1.0","value":"cko"}],"schema_version":"1.0","serialization_version":"1.0","started_at":null}`.
8. V-08 `{"evidence_digest":null,"evidence_id":"evidence-1","evidence_type":"assertion","evidence_version":null,"model":"provenance_evidence_ref","namespace":"cko","qualifiers":[],"schema_version":"1.0","serialization_version":"1.0"}`.
9. V-09 `{"digest":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","model":"provenance_statement_ref","revision":1,"schema_version":"1.0","serialization_version":"1.0","statement_id":{"model":"provenance_statement_id","schema_version":"1.0","serialization_version":"1.0","value":"11111111-1111-5111-8111-111111111111"},"statement_version":"1.0.0"}`.
10. V-10 `{"model":"provenance_statement_version","previous_revision":null,"revision":1,"schema_version":"1.0","serialization_version":"1.0","statement_version":"1.0.0"}`.
11. V-11 é o envelope final D-01 da seção 89.
12. V-12 `{"changed_fields":["/entities"],"left_node_key":"11111111-1111-5111-8111-111111111111@1","model":"provenance_statement_comparison_result","right_node_key":"11111111-1111-5111-8111-111111111111@2","same_digest":false,"same_identity":true,"schema_version":"1.0","serialization_version":"1.0"}`.
13. V-13 `{"components":[["11111111-1111-5111-8111-111111111111@1"]],"edge_count":0,"external_predecessors":[],"model":"provenance_chain_validation_result","node_keys":["11111111-1111-5111-8111-111111111111@1"],"root_keys":["11111111-1111-5111-8111-111111111111@1"],"schema_version":"1.0","serialization_version":"1.0"}`.

Negativos comuns: trocar `model` gera `PS003`; retirar/adicionar campo gera `PS004`; schema/serialização `2.0` gera `PS005`; whitespace fora de string ou ordem não canônica gera `PS006`; chave repetida gera `PS002`; JSON array versus objeto sempre reconstrói tipos internos distintos; colisão NFC gera `PV004`.

## 91. Fixtures de revisão, cadeia e Relationship

Use `A=11111111-1111-5111-8111-111111111111`, `B=22222222-2222-5222-8222-222222222222`, `C=33333333-3333-5333-8333-333333333333`; digests `a×64`, `b×64`, `c×64`, `d×64`, `e×64`, `f×64` significam literalmente 64 repetições lowercase. A1 é raiz `A@1/1.0.0/a×64`; A2 é `A@2/1.0.1/b×64` com previous A1; A3 é `A@3/1.0.2/c×64` com previous A2. Oráculos: A1/A2/A3 são válidos, mesma identidade e chaves distintas; previous de A2 com digest `f×64` lança `PC003`; previous de A2 apontando A2 lança `PC001`; B1 predecessor B1 lança `PC001`; B1→C1 e C1→B1 lança `PC004`; A2→A1 por revisão, A1→B1 causal e B1→A2 causal lança `PC004`; conjunto `{B1}` com predecessor C1 ausente é válido e relata `C@1`; `{A1,B1}` sem arestas produz duas raízes e dois componentes; `{A1,A2,A3}` produz raiz A1, um componente e duas arestas. Essas fixtures cobrem raiz, segunda/terceira revisão, anterior inválida, digest anterior incorreto, autorreferência, ciclo de duas declarações, ciclo misto, cadeia parcial e componentes desconectados.

Golden R-01 usa statement I-01 revisão 1/1.0.0, digest `d1ab797ea20cca608daf65553fa55081a07021e93e0d1f68aea9ef5570183ee9`, declared_at `2026-07-29T12:34:56.000007Z`, entity Document logical `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa`, canonical `bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb`, subject Document logical `123e4567-e89b-12d3-a456-426614174000`, canonical `cccccccc-cccc-4ccc-8ccc-cccccccccccc`, ambos namespace `cko`, versão `1.0.0`, external ID nulo. O logical payload integral é `{"entity":{"namespace":"cko","role":"source","target_id":"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa","target_type":"document"},"kind":"relationship_projection_logical","relationship_type":"derived_into","revision":1,"statement_id":"d4e5aadf-9468-59aa-8076-28fe5e91642d"}` e produz `14662ce7-1def-5fe9-8659-0fc5988074ee`. Semantic key é `cko|aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa|cko|123e4567-e89b-12d3-a456-426614174000|derived_into|directed|many_to_one`; canonical ID é `488066ef-1ba9-5947-a510-993b0df40914`. Version payload integral é `{"kind":"relationship_projection_version","logical_id":"14662ce7-1def-5fe9-8659-0fc5988074ee","revision":1,"statement_digest":"d1ab797ea20cca608daf65553fa55081a07021e93e0d1f68aea9ef5570183ee9","statement_version":"1.0.0"}` e produz `2c7e0eca-280f-58b4-9846-b5c209eb81b5`.

O JSON Relationship golden completo é o envelope canônico produzido pelo serializer público real com: identity `{logical_id=14662ce7-1def-5fe9-8659-0fc5988074ee,canonical_id=488066ef-1ba9-5947-a510-993b0df40914,namespace=cko.core.provenance.projection,semantic_key acima}`; source/target exatamente os endpoints R-01 com `entity_type=canonical_document`; direction/constraint/descriptor exatamente a seção 65; metadata com os cinco attributes fechados; version ID acima; evidence/weights vazios. Sua serialização pública real possui exatamente 2.379 bytes e SHA-256 `8a4d2012d7b997f9dfbe3324ed148c2f4cfdd894a3448564fd215d3cdda3b5be`. Duas execuções isoladas devem produzir esse comprimento, hash e todos os valores; o objeto deve passar `RelationshipValidator.validate` e round-trip no `DeterministicRelationshipSerializer`.

## 92. Fechamento de aceite, testes e rastreabilidade

Para cada AC-001–AC-090 da seção 71, o objeto verificável é o requisito literal da segunda coluna; a entrada/fixture e operação são a seção indicada e o T-n indicado na terceira coluna; o resultado exato é o oráculo literal de T-n e das seções 89–91; o critério binário é igualdade integral do resultado ou recebimento da exceção/código exatos; a evidência exigida é registro de entrada, chamada, retorno/exceção e bytes/hash quando existentes. Critério sem T-n explícito usa: API/assinatura/reflexão → T-001/T-028; AST/import/dependência → T-027; pureza/I-O → T-002/T-027; catálogo/release → T-028/T-030; documentação → diff literal dos nomes/contagens requeridos. Assim, nenhum AC aceita ausência de erro, declaração de conformidade, relatório futuro vazio, matriz genérica, sentinela não definida ou implementação de referência não especificada.

Cada grupo T-001–T-030 da seção 68 tem precondição fixa de schema/serialização `1.0`, chamada exatamente ao método das seções 64–65 e aprovação binária por igualdade ou código. Fixtures e oráculos fechados: T-001 usa V-01–V-13 e reflexão exata; T-002 usa bool em revisão, list retida e construção direta → `PV001`/`PF001`; T-003 usa o produto literal da seção 59 → aceita somente células; T-004 usa permutações e duplicata V-05 → mesmos bytes ou `PV004`; T-005 usa I-01–I-04; T-006 usa A1–A3; T-007 reproduz o namespace; T-008 usa `café` NFC/NFD e surrogate → convergência/`PV007`; T-009 usa C-01–C-05; T-010 usa limites ±9007199254740991 e limite±1/float/Decimal → aceita limites e `PV007`; T-011 usa C-03, offset/naive → C-03 ou `PV006`; T-012 usa D-01 → 1.309 bytes, SHA-256 `dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d`, adulteração false/`PD001`; T-013 usa V-01–V-13 → igualdade e bytes; T-014 aplica missing/extra/duplicate/2.0 → `PS002`/`PS004`/`PS005`; T-015 usa sete linhas da seção 58 → forma exata e zero I/O; T-016 usa cinco evidence types e duplicata V-08 → opaco/`PV004`; T-017 usa V-06 attribution → nenhuma promoção; T-018 usa A1/A2 e entidade → nenhuma inferência cruzada; T-019 usa self fixture → `PC001`; T-020 usa ciclos fixtures → `PC004`; T-021 usa parcial/desconectado → resultados literais; T-022 usa R-01/attribution → R-01 ou vazio; T-023 executa R-01 duas vezes → 2.379 bytes/hash exato; T-024 recebe R-01 externamente → nenhum import Graph; T-025 inspeciona AST e estado Index/Corpus/Inventory → zero chamada/mutação; T-026 inspeciona imports/enum → zero Query; T-027 usa allowlist stdlib/exceptions/relationships periférico e SCC → diff vazio; T-028 compara lista literal dos 610 com baseline+36 → 610 preservados, 36 novos únicos, zero colisão; T-029 executa somente após implementação autorizada → zero falha nova e duas históricas isoladas; T-030 executa somente após release autorizada → exit zero e source/wheel/API idênticos. Nesta correção T-029/T-030 são contratos, não execuções.

| Achado | seção/alteração | vetor/AC/T | situação após correção |
|---|---|---|---|
| NF-001 | 60/89 UUIDs recalculados | I-01–I-04; AC-026/074/075; T-005 | CORRIGIDO NA ESPECIFICAÇÃO |
| NF-002 | 65/91 três identidades Relationship | R-01; AC-085–087; T-022/023 | CORRIGIDO NA ESPECIFICAÇÃO |
| NF-003 | 63/89 D-01 integral | D-01; AC-035/083; T-012 | CORRIGIDO NA ESPECIFICAÇÃO |
| NF-004 | 57/62 CanonicalValue distinto | C-02/V-03; AC-031/032; T-008–010 | CORRIGIDO NA ESPECIFICAÇÃO |
| NF-005 | 17/59 aliases removidos | matriz; AC-015/079; T-003 | CORRIGIDO NA ESPECIFICAÇÃO |
| NF-006 | 57/90 treze schemas | V-01–V-13; AC-073/082; T-001/013 | CORRIGIDO NA ESPECIFICAÇÃO |
| NF-007 | 45/67/79 baseline 610 e dependência externa | AC-055/056/090; T-028/030 | DEPENDÊNCIA EXTERNA NÃO ALTERÁVEL NESTA TAREFA |
| NF-008 | 64/68/71/92 operações e oráculos | AC-001–090; T-001–030 | CORRIGIDO NA ESPECIFICAÇÃO |
| AF-001 | 60/89 namespaces separados | I-01–I-04; AC-074; T-005 | CORRIGIDO NA ESPECIFICAÇÃO |
| AF-002 | 65/91 endpoints completos | R-01; AC-085–087; T-022/023 | CORRIGIDO NA ESPECIFICAÇÃO |
| AF-003 | 57/90 kw_only e ordem | V-11; AC-073; T-001 | CORRIGIDO NA ESPECIFICAÇÃO |
| AF-004 | 87/93 convenção de linhas | verificação final; AC-006; T-028 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-001 | 57/90 schemas | V-01–V-13; AC-073; T-001/013 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-002 | 60/89 token/UUID | I-01–I-04; AC-074/075; T-005 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-003 | 61/91 revisão | A1–A3; AC-076–078; T-006/019–021 | PRESERVADO COMO RESOLVIDO |
| F-004 | 65/91 Relationship | R-01; AC-085–087; T-022/023 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-005 | 59 matriz | matriz; AC-079; T-003 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-006 | 57/62 CanonicalValue/tempo | C-02/C-03; AC-080/081; T-008–011 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-007 | 64 operações | fixtures 91; AC-038/084; T-004/006 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-008 | 45/79 documentos 334/346 versus 610 | AC-055/056/090; T-028/030 | DEPENDÊNCIA EXTERNA NÃO ALTERÁVEL NESTA TAREFA |
| F-009 | 63/89 envelopes/digest | D-01; AC-082/083; T-012–014 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-010 | 58 IDs alvo | V-04/V-05; AC-088; T-015 | PRESERVADO COMO RESOLVIDO |
| F-011 | 69 documentos futuros | AC-089; T-030 | PRESERVADO COMO RESOLVIDO |
| F-012 | 71/92 mapa 52→90 reconstruído | AC-001–052; T associados | CORRIGIDO NA ESPECIFICAÇÃO |
| F-013 | 68/92 oráculos | fixtures 89–91; AC-001–090; T-001–030 | CORRIGIDO NA ESPECIFICAÇÃO |
| F-014 | README/CHANGELOG mojibake | AC-090; tarefa externa | DEPENDÊNCIA EXTERNA NÃO ALTERÁVEL NESTA TAREFA |
| F-015 | ARCH 346 versus 610 | AC-090; T-028/030 | DEPENDÊNCIA EXTERNA NÃO ALTERÁVEL NESTA TAREFA |
| F-016 | 87/93 hash | hash final | PRESERVADO COMO RESOLVIDO |
| F-017 | 41/67 API 36 sem colisão | AC-052/053; T-028 | PRESERVADO COMO RESOLVIDO |
| F-018 | 23/60 namespace UUID | I-namespace; AC-027; T-007 | PRESERVADO COMO RESOLVIDO |
| F-019 | 3/70 regressão 878/880 | AC-060/071; T-029 | PRESERVADO COMO RESOLVIDO |

Catálogo com 334 nomes, ARCH com 346, versão documental residual 0.1.0, matriz incompleta e mojibake são dependências externas. Não foram corrigidos nem declarados resolvidos; deverão ser reconciliados em tarefa própria autorizada antes de freeze ou release. A coerência interna desta especificação usa o baseline factual `cko.core.__all__`: 610 entradas, 610 nomes únicos e 610 resolvidos.

## 93. Conclusão e confirmações finais

A arquitetura independente aprovada foi preservada. `KnowledgeProvenance` permanece integralmente intacto. Nenhum código, teste, versão, wheel, runtime, catálogo, documentação baseline ou Sprint posterior é autorizado por este documento.

Segunda correção integral da especificação SPR-017 concluída e gravada, sem implementação e sujeita a nova auditoria formal independente.
