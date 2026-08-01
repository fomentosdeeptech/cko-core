# SPR-017E-R — Nova Auditoria Formal da SPR-017

## 1. Identificação, decisão e escopo

- **Data e hora:** 2026-07-30 20:25:11, `America/Sao_Paulo`.
- **Natureza:** recuperação e reconstrução independente de auditoria formal pré-implementação.
- **Repositório canônico:** `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`.
- **Branch:** `main`.
- **Commit:** `e94545919db97a071f08de2c08ce1a5dde06980e`.
- **Arquivo auditado:** `SPR017_TECHNICAL_SPECIFICATION.md`.
- **SHA-256 inicial:** `38E22AB9D9C71F671C7EA2A8E715EF9BD5A57C53122051C5B84EF642941CC2CE`.
- **Modo:** leitura para todo o repositório; única gravação autorizada neste relatório.
- **Decisão formal:** **REPROVADA NA NOVA AUDITORIA FORMAL E DEVOLVIDA PARA CORREÇÃO.**

Esta auditoria não implementa a SPR-017, não executa testes da Sprint, não altera versão, código, testes, catálogo, arquitetura, governança, wheel ou especificação e não autoriza implementação.

## 2. Metodologia e hierarquia de evidência

Foram usados: leitura e busca textual; inspeção de Git; SHA-256; inspeção byte a byte de UTF-8/BOM; contagem de linhas e cabeçalhos; análise estática de `__all__`; importação somente para reflexão pública, com bytecode desabilitado; inspeção de assinaturas/dataclasses; confronto com código e documentos; e recálculo independente, somente em memória, de UUIDv5, NFC, JSON canônico, UTF-8 e SHA-256. Nenhuma suíte de testes foi executada.

A evidência foi hierarquizada assim: contrato público real e reflexão; testes/relatórios homologados anteriores; arquitetura/governança; especificação auditada; afirmações de autorresolução da própria especificação. Uma declaração como “resolvido” na seção 72 não foi aceita sem reprodução.

## 3. Tentativa de recuperação

### 3.1 Locais pesquisados

1. árvore canônica do repositório, inclusive Markdown, texto, JSON, logs visíveis e arquivos não rastreados;
2. histórico Git acessível, por nomes relacionados a `SPR017` e `AUDIT`;
3. área `.codex` acessível dentro do workspace;
4. diretório do anexo `C:\Users\andre\.codex\attachments\b9c717f4-a0e4-4d2a-829e-8580e5f3b616`;
5. buscas por `NF-001` a `NF-008`, “Nova Auditoria Formal”, nome do relatório e SHA-256 atual da especificação.

Não foram acessados diretórios bloqueados, não houve elevação de privilégios e não se presumiu recuperação de conversa desaparecida.

### 3.2 Resultado

**Recuperação parcial.** Foram recuperados integralmente:

- `SPR017_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`, auditoria arquitetural que aprovou a necessidade com ajustes;
- `SPR017_TECHNICAL_SPECIFICATION_AUDIT.md`, auditoria formal anterior com 19 achados;
- a identificação resumida de NF-001 a NF-008 no pedido anexado.

Não foi localizado relatório anterior denominado `SPR017E_NOVA_AUDITORIA_FORMAL.md`, conteúdo completo dos NF-001–NF-008, log correspondente ou versão no histórico Git. As únicas ocorrências dos IDs NF estavam no pedido anexado. Portanto, os 19 achados foram recuperados da auditoria anterior; NF-001–NF-008 e a decisão atual foram reconstruídos e revalidados.

## 4. Materiais consultados

Foram consultados integralmente ou submetidos a inspeção integral mecânica, com leitura focal das cláusulas aplicáveis:

- `SPR017_TECHNICAL_SPECIFICATION.md`;
- `SPR017_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`;
- `SPR017_TECHNICAL_SPECIFICATION_AUDIT.md`;
- `SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`;
- `SPR016_IMPLEMENTATION_REPORT.md` e relatórios SPR-010–SPR-015;
- `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md`;
- `CKO_CORE_V1_ARCHITECTURE_DECISION.md`;
- `CKO_CORE_V1_DEPENDENCY_MATRIX.md`;
- `CKO_CORE_V1_EXCEPTION_HIERARCHY.md`;
- `CKO_CORE_V1_PUBLIC_API_CATALOG.md`;
- documentos Architecture/API/Model/Serialization/Operations disponíveis de Knowledge Object, Document, Relationship, Graph, Query, Index e Corpus;
- `pyproject.toml`;
- fachadas `src/cko/__init__.py`, `src/cko/core/__init__.py` e `__init__.py` das fundações relevantes;
- fontes públicas sob `src/cko/core/knowledge`, `documents`, `relationships`, `graph`, `query`, `index`, `corpus`, `inventory` e `exceptions`;
- contratos e factories necessários para Object, Document, Relationship, Graph, Query, Index, Corpus e Inventory;
- testes existentes apenas como texto; nenhum foi executado.

`CORE-001` nominal continuou não localizado. Os caminhos efetivos relevantes incluem `src/cko/core/knowledge/metadata.py`, `src/cko/core/relationships/factory.py`, `identity.py`, `metadata.py`, `models.py`, `validator.py`, `serializer.py`, `src/cko/core/exceptions/errors.py` e as fachadas citadas.

## 5. Estado inicial do Git

O diretório existe, `git rev-parse --show-toplevel` resolve para ele e não foi usada cópia alternativa.

- branch `main`;
- commit `e94545919db97a071f08de2c08ce1a5dde06980e`;
- 10 entradas rastreadas por `git ls-files`;
- 434 entradas em `git status --porcelain=v1 -uall`;
- 2 rastreadas modificadas preexistentes: `.gitignore` e `pyproject.toml`;
- 432 não rastreadas preexistentes.

Distribuição completa das 432 não rastreadas, por primeiro componente ou arquivo de topo: `.vscode` 2; `config` 2; `docs` 17; `reports` 3; `scripts` 11; `src` 260; `tests` 39; e 98 arquivos de topo/outros, incluindo toda a documentação CKO, relatórios SPR-008–017, comandos, manifests, migration, `advanced_engine.py` e `inventory.txt`. Entre elas já estavam `SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`, `SPR017_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md`, `SPR017_TECHNICAL_SPECIFICATION.md` e `SPR017_TECHNICAL_SPECIFICATION_AUDIT.md`. Nenhuma dessas entradas foi criada ou atribuída a esta execução.

O estado completo é reprodutível pelo comando somente leitura `git status --porcelain=v1 -uall`; as contagens acima são a representação fechada do baseline observado imediatamente antes da gravação.

## 6. Validações mecânicas da especificação

| Validação | Resultado independente |
|---|---|
| SHA-256 | `38E22AB9D9C71F671C7EA2A8E715EF9BD5A57C53122051C5B84EF642941CC2CE` |
| tamanho | 95.208 bytes |
| codificação | UTF-8 estrito, caracteres íntegros |
| BOM | ausente |
| linhas | 1.228 linhas de conteúdo por `Get-Content`; 1.229 segmentos físicos quando o newline terminal é contado |
| seções numeradas | 88, consecutivas de 1 a 88 |
| critérios de aceite | 90, AC-001–AC-090 |
| grupos de testes | 30, T-001–T-030 |
| constantes candidatas | 4 |
| enums candidatos | 7 |
| modelos candidatos | 13 |
| serviços candidatos | 4 |
| exceções candidatas | 8 |
| API candidata | 36 símbolos únicos |
| `cko.core.__all__` | 610 entradas, 610 únicas, 610 resolvidas |
| união de fachadas inspecionadas | 646 nomes únicos; não é a contagem da raiz |
| colisões dos 36 candidatos com a raiz | zero |
| `TBD`, “a definir”, `placeholder`, reticência omissiva | zero marcadores reais |
| código Python/pseudocódigo implementacional | ausente |
| autorização/homologação indevida | não autoriza implementação, mas a seção 55 usa título ambíguo “Sequência autorizada” condicionado pela seção 56 |

A alegação anterior de 1.228 linhas é correta sob a convenção de linhas de conteúdo; o arquivo termina com newline, razão da contagem física 1.229. A busca case-insensitive por `TODO` encontra palavras portuguesas como “Todo”, não marcadores técnicos `TODO` em caixa alta.

## 7. Baseline público real

- `pyproject.toml` e `cko.core.__version__`: `1.0.0`.
- `CKOError`: `cko.core.exceptions.errors.CKOError`, base direta `Exception`.
- `KnowledgeProvenance`: `cko.core.knowledge.metadata.KnowledgeProvenance`, dataclass frozen/slotted, reexportada pela mesma identidade em `cko.core.knowledge` e `cko.core`.
- Assinatura preservada: `(origin, pipeline, generating_process, original_source, timestamp, pipeline_version, source_type=system, schema_version='1.0')`.
- Não existe namespace `cko.core.provenance` implementado.
- A API candidata é aditiva por nomes e não colide, mas ainda não pode ser implementada de modo convergente.

## 8. Matriz dos 19 achados anteriores

Estados permitidos são usados literalmente.

| ID / severidade / origem | Descrição e seção corretiva | Evidência atual e confronto com baseline | Estado | Impacto, correção e critério de encerramento |
|---|---|---|---|---|
| F-001 BLOQUEADOR, auditoria técnica | schemas dos 13 modelos; §57 | tabela adicionada, mas tipos, envelopes e construção permanecem ambíguos; `CanonicalValue` contradiz C-02 | PARCIALMENTE RESOLVIDO | bytes e parsers divergem; publicar schemas campo a campo compiláveis e dois parsers independentes convergentes |
| F-002 BLOQUEADOR | token do sujeito/UUID; §60 | payload objeto foi publicado, porém I-01/I-03/I-04 não correspondem ao UUIDv5 recalculado | REGRESSÃO | identidade golden incorreta; corrigir vetores e explicitar ambos os namespaces; reprodução exata |
| F-003 BLOQUEADOR | revisão, SemVer, referência e chave; §61 | revisão n, versão `1.0.(n-1)`, referência completa e chave `ID@revision` estão fechadas | RESOLVIDO | encerrar com fixtures de três revisões e ciclo misto conforme texto |
| F-004 BLOQUEADOR | projeção Relationship; §65 | `from_parts` correto foi adotado, mas payloads de logical/version ID e mapeamento de endpoints/canonical ID não são fechados | PARCIALMENTE RESOLVIDO | relações podem colidir/divergir; publicar todos os nomes UUID e componentes tipados; duas execuções byte-idênticas |
| F-005 ALTO | matriz categoria–atividade–papéis; §59 | matriz total existe, porém usa `supporting`, `responsible`, `other`, ausentes dos enums | PARCIALMENTE RESOLVIDO | validator sem vocabulário único; substituir pelos valores exatos e validar produto cartesiano |
| F-006 ALTO | tempo e qualificadores; §§57/62 | UTC, inteiros e JSON foram fechados; árvore `CanonicalValue` continua contraditória/ambígua | PARCIALMENTE RESOLVIDO | digest e round-trip divergem; definir arrays heterogêneos ou corrigir C-02 e distinguir array/objeto |
| F-007 ALTO | operações; §64 | quatro serviços e alguns métodos têm assinatura; `revise`, `with_*`, `without_*`, `compare` e projection não têm contratos completos | PARCIALMENTE RESOLVIDO | implementações incompatíveis; publicar parâmetros, retornos, pré/pós-condições e erros exatos |
| F-008 ALTO | catálogo/matriz/ARCH; §§45/67/79 | catálogo ainda 334, ARCH 346, matriz só tem adendo Corpus; raiz real 610 | NÃO RESOLVIDO | baseline documental divergente; reconciliar documentos em etapa autorizada antes do freeze e provar igualdade source/catalog/wheel |
| F-009 ALTO | envelopes/payload digest; §63 | discriminadores listados, mas envelopes aninhados não estão fechados e D-01 é irreproduzível | PARCIALMENTE RESOLVIDO | SHA golden não auditável; fornecer JSON sem digest integral e hash correto |
| F-010 MÉDIO | IDs por alvo; §58 | sete tipos e forma do ID estão tabelados | RESOLVIDO | encerrar com sete fixtures e normalização pública idêntica |
| F-011 MÉDIO | documentação futura; §69 | sete documentos têm momento, responsável, conteúdo e conclusão | RESOLVIDO | encerrar por revisão da matriz na futura implementação autorizada |
| F-012 MÉDIO | origem dos 52 mínimos | AC-001–052 foram declarados como mapa, mas a fonte nominal continua não localizada | PARCIALMENTE RESOLVIDO | rastreabilidade histórica incompleta; anexar fonte ou registrar formalmente reconstrução requisito a requisito |
| F-013 MÉDIO | testes sem oráculos; §68 | T-001–T-030 melhoraram, mas muitos são rótulos sem fixtures, exceção e bytes/resultado completos | PARCIALMENTE RESOLVIDO | testes não independentes; completar cada linha com entrada, operação e oráculo determinístico |
| F-014 BAIXO | mojibake README/CHANGELOG | preexistente e fora da autorização desta tarefa | NÃO RESOLVIDO | risco documental baixo; corrigir em tarefa autorizada e validar UTF-8 visual |
| F-015 BAIXO | ARCH com 346 exports | ARCH v1.2 ainda declara 346 contra 610 | NÃO RESOLVIDO | baseline documental falso; atualizar e reconciliar automaticamente |
| F-016 OBSERVAÇÃO | hash anterior | novo SHA-256 foi calculado e corresponde ao informado | RESOLVIDO | repetir antes/depois; cumprido nesta auditoria |
| F-017 OBSERVAÇÃO | 36 sem colisão | scan independente: 36 únicos, zero colisões | RESOLVIDO | repetir imediatamente antes de exportar |
| F-018 OBSERVAÇÃO | namespace UUID correto | namespace recalculado exatamente | RESOLVIDO | preservar golden do namespace; identidade de statements é achado separado |
| F-019 OBSERVAÇÃO | regressão 878/880 | evidência anterior preservada; nenhuma suíte executada aqui | RESOLVIDO | futura implementação deve provar zero falha nova |

Resumo: F-001/F-004/F-005/F-006/F-007/F-009/F-012/F-013 são 8 PARCIALMENTE RESOLVIDOS; F-002 é 1 REGRESSÃO; F-008/F-014/F-015 são 3 NÃO RESOLVIDOS; F-003/F-010/F-011/F-016/F-017/F-018/F-019 são 7 RESOLVIDOS. Total: 19.

Distribuição original preservada: 4 bloqueadores, 5 altos, 4 médios, 2 baixos e 4 observações.

## 9. Resultado dos 11 grupos obrigatórios

| Grupo | Resultado |
|---|---|
| schemas | FALHA — incompletos/contraditórios |
| identidade | FALHA — golden UUID incorreto e entrada ambígua |
| revisão | APROVADO NO TEXTO |
| matriz semântica | FALHA — valores que não pertencem aos enums |
| canonicalização | FALHA — `CanonicalValue`/C-02 |
| envelopes | FALHA — D-01 irreproduzível |
| operações | FALHA — assinaturas e condições incompletas |
| Relationship | FALHA — IDs/endpoints não fechados |
| catálogo/matriz | FALHA — 334/346 versus 610 e cobertura incompleta |
| docs/mapa | PARCIAL — docs fechadas, fonte dos 52 ausente |
| testes/aceite | FALHA — oráculos incompletos |

Nenhum grupo foi considerado fechado pela mera declaração da seção 72.

## 10. Reconstrução de NF-001 a NF-008

### NF-001 — BLOQUEADOR — Vetores UUIDv5 incorretos

- **Origem:** resumo recuperado e reprodução da §60.
- **Evidência:** namespace recalculado correto: `84c43be6-4bb5-52a8-9582-a2e8b04d797c`. Com JSON objeto canônico, NFC e UTF-8 definidos pela própria especificação, I-01 resulta em `d4e5aadf-9468-59aa-8076-28fe5e91642d`, não `4c385db1-26e6-5227-ae35-b724c54c6865`; I-03 resulta em `579a17ba-956d-57ba-a48d-4f829e30ee50`, não `9af026ef-26c5-5f15-afcd-9f6eb50c1891`; I-04 resulta em `2ac58580-c9ec-5345-8eb0-d95f410cba82`, não `0e61b54c-e1ac-5a59-b463-6cf6de2f7619`.
- **Reprodução:** `uuid5(PROVENANCE_UUID_NAMESPACE, canonical_json.decode('utf-8'))` com chaves ordenadas, separadores mínimos e NFC.
- **Impacto:** implementações conformes produzem IDs diferentes dos golden tests.
- **Correção normativa:** substituir resultados publicados por valores recalculados após fechar sem ambiguidade `business_namespace` e `subject.namespace`, ou publicar outro algoritmo/payload integral e recalcular todos.
- **Encerramento:** duas implementações independentes produzem exatamente os mesmos bytes e UUIDs para I-01–I-04.

### NF-002 — BLOQUEADOR — Identidades da projeção Relationship não fechadas

- **Contrato real:** `RelationshipFactory.from_parts(self, *, identity: RelationshipIdentity, metadata: RelationshipMetadata, source: RelationshipEndpoint, target: RelationshipEndpoint, descriptor: RelationshipDescriptor, version: RelationshipVersion, evidence=(), weights=()) -> CanonicalRelationship`.
- **Evidência:** `RelationshipIdentity` exige `canonical_id == RelationshipId.canonical(namespace, semantic_key)`. Esse método usa o namespace UUID privado da fundação Relationship e o nome `<namespace>:<semantic_key>`. §65 define separadamente um `logical_id` UUIDv5 com “entity token” não definido e um `version_id` “UUIDv5 distinto” sem publicar integralmente namespace e nome. Não especifica `canonical_id`/`external_id` dos endpoints nem o mapeamento exato de `document` para o `entity_type` real (`from_document` usa `canonical_document`).
- **Resultado esperado:** identidade lógica, canônica e de versão reproduzíveis, ligadas por payloads integrais ao statement e aos endpoints.
- **Resultado encontrado:** vários valores conformes ao texto são possíveis; a identidade canônica pode coincidir para statements distintos com os mesmos endpoints/tipo, enquanto a lógica difere.
- **Correção:** publicar JSON/UTF-8/namespace completos de logical/version IDs; declarar semantic key exata; declarar todos os campos de endpoints; explicar unicidade e colisões entre statements/revisões.
- **Encerramento:** fixtures golden completas passam em duas execuções isoladas e satisfazem o validator real.

### NF-003 — BLOQUEADOR — D-01 irreproduzível

- **Evidência:** §63 declara 1.136 bytes e hash `fa164ef4d9b594b39d1e5525deba4a93a58aed7518cc73fceeb8eda8fd36661e`, mas não publica o JSON integral sem digest. D-01 omite ao menos o namespace da entidade e depende de schemas/envelopes aninhados ambíguos.
- **Resultado esperado:** bytes hex integrais e SHA reproduzível.
- **Resultado encontrado:** não existe entrada normativa única; logo tamanho e hash não podem ser confirmados.
- **Correção:** incluir o envelope canônico integral sem digest, seu hex UTF-8, comprimento e SHA-256; declarar ordem/representação de todos os envelopes aninhados.
- **Encerramento:** hash e 1.136 bytes reproduzidos apenas a partir do relatório/especificação, sem decisão adicional.

### NF-004 — BLOQUEADOR — `CanonicalValue` contraditório e C-02 incompatível

- **Texto aplicável:** §57 define array como “tuple homogênea de `CanonicalValue`”; §62/C-02 exige `[null,true,false,0,-12]`.
- **Interpretação possível:** “homogênea” poderia significar todos os elementos pertencem à união `CanonicalValue`.
- **Interpretação obrigatória pelo uso técnico normal:** homogênea significa mesmo subtipo; C-02 é heterogêneo. Além disso, tuple de valores e tuple de pares também deixa array versus objeto estruturalmente ambíguo.
- **Impacto:** validators, hash, igualdade e round-trip divergem.
- **Correção textual exata exigida:** substituir por “array é tuple ordenada, possivelmente heterogênea, de valores `CanonicalValue`; objeto é um tipo interno distinto de pares chave-string/valor, ordenado por chave e nunca inferido apenas pelo formato da tuple”, ou tornar arrays homogêneos e corrigir C-02.
- **Encerramento:** C-02 aceito ou rejeitado sem contradição e round-trip distingue inequivocamente arrays de objetos.

### NF-005 — ALTO — Vocabulário usado não existe nos enums

- **Evidência:** enum define `supporting_entity`, `responsible_party`, `other_declared`; §59 usa `supporting`, `responsible`, `other`. Esses valores não existem nos sete enums publicados.
- **Impacto:** matriz e testes podem validar tokens diferentes do serializer.
- **Correção:** usar somente os valores completos dos enums em toda regra, exemplo, vetor, aceite e teste; declarar qualquer abreviação como mero rótulo não serializável, preferencialmente removê-la.
- **Encerramento:** extração mecânica de todos os tokens normativos resulta em subconjunto exato dos enums.

### NF-006 — BLOQUEADOR — Schemas dos 13 modelos incompletos

- **Evidência:** §57 não tipa todos os campos, não fecha envelopes aninhados e não define construção keyword-only. Em `ProvenanceStatement`, campos obrigatórios `version` e `digest` aparecem depois de campos com default, impossível na ordem mostrada para dataclass comum sem `kw_only=True` ou reordenação. Resultados omitem tipos/cardinalidades de vários campos.
- **Impacto:** duas implementações podem ter assinaturas, envelopes, igualdade e validações diferentes.
- **Correção:** schema por modelo com ordem, tipo completo, default, cardinalidade, normalizador, invariantes, discriminador, envelope JSON integral, erros e regra de construção compilável.
- **Encerramento:** geração/reflexão de 13 dataclasses coincide exatamente e todos os envelopes têm conjunto de campos único.

### NF-007 — ALTO — Especificação, catálogo e matriz arquitetural divergem

- **Evidência real:** raiz 610; catálogo 334 e ainda afirma `0.1.0`; ARCH v1.2 346; matriz principal não cobre SPR-010–015 e possui apenas adendo SPR-016. A especificação reconhece a defasagem e posterga a correção.
- **Impacto:** não invalida o código 1.0.0, mas impede usar documentos como baseline normativo confiável e impede freeze/release da SPR-017.
- **Correção:** em tarefa autorizada, gerar catálogo/matriz/ARCH a partir da API real, incluir SPR-010–017 e reconciliar source, catálogo e wheel.
- **Encerramento:** contagens, nomes, versões e dependências coincidem automaticamente, com diff vazio.

### NF-008 — ALTO — Operações e oráculos insuficientes

- **Evidência:** §64 fornece assinatura completa apenas para `create/from_parts`; `revise`, família `with_*`/`without_*`, `compare`, cadeia e projection carecem de parâmetros exatos, retornos por caso e tabela de erros. T-001–T-030 frequentemente usam rótulos como “unit”, “matriz” ou “sentinelas”, sem fixture integral, pré-condição, operação e exceção/oráculo exatos.
- **Impacto:** não há teste independente capaz de arbitrar implementações divergentes.
- **Correção:** contrato individual de cada método e caso de teste com requisito, fixture literal, precondição, chamada, resultado/bytes ou exceção/código e critério binário.
- **Encerramento:** nenhuma linha de teste depende de interpretação humana ou de implementação de referência não especificada.

## 11. Achados adicionais

| ID | Severidade | Evidência e impacto | Correção / encerramento |
|---|---|---|---|
| AF-001 | ALTO | I-01/I-03 dizem apenas “namespace `cko`”, embora o payload possua `business_namespace` e `subject.namespace`; I-04 tem a mesma dupla dimensão. O vetor não fecha a própria entrada. | publicar cada campo separadamente; golden reproduzível sem inferência |
| AF-002 | ALTO | projeção não define `entity_type`, `canonical_id` e `external_id` exatos por target; adapter Document real usa `canonical_document`, não o token `document` da SPR-017 | tabela endpoint campo a campo por target; valor aceito pelo baseline e bytes golden |
| AF-003 | MÉDIO | ordem/defaults de `ProvenanceStatement` não é uma assinatura de dataclass compilável comum e `kw_only` não foi adotado | declarar `kw_only=True` e assinatura ou reordenar campos; reflexão futura deve coincidir |
| AF-004 | OBSERVAÇÃO | 1.228 linhas de conteúdo versus 1.229 segmentos quando newline terminal conta | declarar convenção de contagem; sem impacto semântico |

Totais dos achados atuais independentes (NF + AF): **5 BLOQUEADORES, 5 ALTOS, 1 MÉDIO, 0 BAIXOS, 1 OBSERVAÇÃO; total 12**. AF-001/AF-002 detalham lacunas distintas das divergências de resultado de NF-001/NF-002; não alteram o gate já bloqueado.

## 12. Schemas dos 13 modelos

Todos deveriam ser frozen/slotted, profundamente imutáveis, tipados, com igualdade/hash, schema/serialização `1.0`, discriminador fechado, rejeição de extras e round-trip. O estado abaixo considera o contrato inteiro, não apenas a existência de uma linha na tabela.

| Modelo | Campos/finalidade resumidos | Obrigatoriedade, identidade/digest/envelope | Estado |
|---|---|---|---|
| ProvenanceStatementId | `value: UUID` | obrigatório; UUIDv5; envelope próprio | AMBÍGUO — golden incorreto |
| ProvenanceStatementIdentity | statement_id, business_namespace, lineage_key | obrigatórios; recomputável; todos no digest | CONTRADITÓRIO — ID publicado diverge |
| ProvenanceQualifier | name, CanonicalValue | obrigatórios; nome único; valor no digest | CONTRADITÓRIO — valor/array/objeto |
| ProvenanceSubjectRef | target_type, namespace, target_id, version?, digest? | sujeito único; versão/digest fora do ID, dentro do digest | AMBÍGUO — tipos/envelope não integrais |
| ProvenanceEntityRef | campos do sujeito + role | 0..n; ordenado; extras recusados | AMBÍGUO — schema por herança textual |
| ProvenanceActorRef | actor_type, namespace, actor_id, role, version?, digest? | 0..n; identidade+papel único | AMBÍGUO — tipos/envelope omitidos |
| ProvenanceActivityRef | type, namespace, id, label?, intervalo?, qualifiers | 0..1; intervalo e `other_declared` | AMBÍGUO — shorthand enum e envelope |
| ProvenanceEvidenceRef | type, namespace, id, version?, digest?, qualifiers | 0..n; opaca | AMBÍGUO — cardinalidade/tipos de qualifiers |
| ProvenanceStatementRef | id, revision, version, digest | todos obrigatórios; chave ID@revision | COMPLETO no nível conceitual |
| ProvenanceStatementVersion | version, revision, previous? | raiz/revisão fechadas; digest anterior | COMPLETO no nível conceitual |
| ProvenanceStatement | identidade, categoria, participantes, versão, instante, digest, foundation | factory-only; tudo menos próprio digest participa | CONTRADITÓRIO — ordem/defaults e envelope D-01 |
| ProvenanceStatementComparisonResult | flags, node keys, changed_fields | resultado ordenado | INCOMPLETO — tipos/envelope/validações faltam |
| ProvenanceChainValidationResult | node/root/external/component keys, edge_count | resultado válido ordenado | INCOMPLETO — tipos/cardinalidades/envelope faltam |

Resultado: 2 conceitualmente completos, 6 ambíguos, 3 contraditórios e 2 incompletos; **zero schema integralmente pronto para implementação isolada**, pois até os dois conceitualmente completos dependem do envelope comum ainda incompleto.

## 13. Enums

Os sete enums e seus valores declarados são pertinentes e fechados. Porém, a matriz normativa usa três aliases inexistentes (`supporting`, `responsible`, `other`). Resultado: **definições dos enums completas; uso normativo inconsistente e não aprovável**.

## 14. Identidade, namespace e vetores normativos

### 14.1 Namespace

- nome NFC: `urn:cko:core:knowledge-provenance-statement-foundation`;
- UTF-8 hex: `75726e3a636b6f3a636f72653a6b6e6f776c656467652d70726f76656e616e63652d73746174656d656e742d666f756e646174696f6e`;
- transformação: UUIDv5(namespace URL, nome);
- declarado/recalculado: `84c43be6-4bb5-52a8-9582-a2e8b04d797c` / igual;
- situação: CORRETO.

### 14.2 I-01/I-02

Assumindo, de forma explícita, ambos os namespaces como `cko`, bytes canônicos:

`{"business_namespace":"cko","category":"derivation","kind":"provenance_statement_identity","lineage_key":"lineage-001","subject":{"namespace":"cko","target_id":"123e4567-e89b-12d3-a456-426614174000","target_type":"document"}}`

Hex:

`7b22627573696e6573735f6e616d657370616365223a22636b6f222c2263617465676f7279223a2264657269766174696f6e222c226b696e64223a2270726f76656e616e63655f73746174656d656e745f6964656e74697479222c226c696e656167655f6b6579223a226c696e656167652d303031222c227375626a656374223a7b226e616d657370616365223a22636b6f222c227461726765745f6964223a2231323365343536372d653839622d313264332d613435362d343236363134313734303030222c227461726765745f74797065223a22646f63756d656e74227d7d`

Declarado `4c385db1-26e6-5227-ae35-b724c54c6865`; recalculado `d4e5aadf-9468-59aa-8076-28fe5e91642d`; **DIVERGENTE**. I-02 preserva o recalculado quando somente target version/digest mudam.

### 14.3 I-03

Mesma entrada, categoria `origin`. Hex difere no token de categoria; declarado `9af026ef-26c5-5f15-afcd-9f6eb50c1891`; recalculado `579a17ba-956d-57ba-a48d-4f829e30ee50`; **DIVERGENTE**.

### 14.4 I-04

NFC convergiu `cafe\u0301` para `café` no lineage e URI. Bytes:

`{"business_namespace":"acervo","category":"attribution","kind":"provenance_statement_identity","lineage_key":"café","subject":{"namespace":"acervo","target_id":"https://example.org/café","target_type":"external_resource"}}`

Declarado `0e61b54c-e1ac-5a59-b463-6cf6de2f7619`; recalculado `2ac58580-c9ec-5345-8eb0-d95f410cba82`; **DIVERGENTE**.

## 15. Canonicalização, JSON e C-02

Regras de NFC, UTF-8, chaves, escapes, inteiros seguros, rejeição de float/Decimal, UTC de seis dígitos e ausência de BOM estão suficientemente claras isoladamente. Vetores reproduzidos:

| Vetor | bytes canônicos / hex | Resultado |
|---|---|---|
| C-01 | `{"a":"é","b":1}` / `7b2261223a22c3a9222c2262223a317d` | correto |
| C-02 | `[null,true,false,0,-12]` / `5b6e756c6c2c747275652c66616c73652c302c2d31325d` | bytes corretos, schema contraditório |
| C-03 | `2026-07-29T12:34:56.000007Z` / `323032362d30372d32395431323a33343a35362e3030303030375a` | correto como token textual |
| C-04 | `"linha\n\"x\""` / `226c696e68615c6e5c22785c2222` | correto |
| C-05 | colisão NFC entre chaves | erro normativo correto, sem bytes válidos |

Conclusão C-02: há **contradição normativa material**, não compatibilidade demonstrável.

## 16. Digest, serialização e round-trip

O algoritmo conceitual — SHA-256 lowercase do envelope UTF-8 sem o próprio digest — é adequado. Contudo, o payload não é reconstruível por causa de NF-003/NF-004/NF-006. Logo:

- D-01: **NÃO REPRODUZÍVEL**;
- serialização: discriminadores enumerados, envelopes incompletos;
- round-trip estrutural/semântico/byte a byte: objetivo correto, oráculo ausente para vários modelos;
- identidade, revisão, versão, referência anterior, assinatura e prova estão conceitualmente separadas; digest continua corretamente limitado a integridade.

## 17. Versão, evidência, cadeia, ciclos e snapshot

- camadas schema/serialização/fundação/declaração/revisão/alvo/SDK estão separadas;
- revisão n referencia n−1 por ID, versão e digest; predecessor causal é distinto;
- evidências são referências declaradas, opacas e não verificadas;
- raízes, múltiplos antecedentes, cadeias parciais e componentes desconectados são admitidos;
- self e ciclos detectáveis no conjunto fornecido são rejeitados;
- a garantia é corretamente limitada ao conjunto fornecido;
- decisão **NÃO ADOTAR snapshot** é coerente;
- operações são declaradas puras, sem I/O, rede, filesystem, banco, relógio implícito ou aleatoriedade, mas faltam contratos executáveis completos.

## 18. Relationship e integrações

A projeção é explicitamente lossy, não reversível e não autoridade; isso está correto. A direção entidade→sujeito, `DERIVED_INTO`/`GENERATED_INTO`, `DIRECTED`, `many_to_one`, strength UNKNOWN e uso obrigatório de `from_parts` também são compatíveis com o baseline.

Falham o fechamento dos IDs e endpoints descrito em NF-002/AF-002. A projeção não pode ser aprovada até que logical ID, canonical ID, semantic key, version ID e todos os campos de ambos endpoints tenham entrada e bytes golden.

Integrações restantes:

- Object/Document: referências públicas opacas; autoria não promovida; correto;
- Graph: composição externa; correto;
- Index/Corpus: não atualizados e não autoridades; correto;
- Query: isolada e fora do target enum; correto;
- Inventory: não estendido/importado; correto;
- dependências: núcleo stdlib + `cko.core.exceptions.CKOError`; imports privados/reversos/ciclos e infraestrutura proibidos; correto como direção normativa;
- retrocompatibilidade: `KnowledgeProvenance` preservada e API candidata nominalmente aditiva.

## 19. Critérios de aceite e plano de testes

Os 90 critérios estão numerados e rastreados, mas vários aceitam apenas a existência futura de relatório/diff/teste, não publicam dados suficientes para verificação independente. Os 30 grupos melhoram a cobertura temática, porém não satisfazem uniformemente requisito, entrada literal, precondição, operação, resultado, exceção, oráculo e critério binário.

Lacunas principais: golden UUID errado; D-01 sem fixture; C-02 contraditório; schemas sem envelope; projection sem IDs/endpoints completos; operações sem assinatura; “matriz”, “sentinelas”, “AST” e “duas execuções” sem fixture/resultado integral. NF-008 permanece ALTO.

## 20. Catálogo, matriz e arquitetura

As divergências são documentais em relação ao baseline 1.0.0 já implementado, mas materiais para esta especificação porque ela as cita como normas e exige reconciliação futura. Elas não autorizam alteração nesta tarefa. Antes de qualquer freeze/implementação/release autorizados, catálogo 334, ARCH 346, versão 0.1.0 residual e matriz incompleta precisam coincidir com os 610 exports e as fundações SPR-010–017.

## 21. Riscos remanescentes

1. IDs incompatíveis entre produtores;
2. digests e bytes não interoperáveis;
3. colisão ou dissociação entre IDs lógico/canônico/de versão de Relationship;
4. parsers diferentes para arrays/objetos e enums abreviados;
5. assinaturas de dataclass/serviços incompatíveis;
6. testes que confirmam a própria implementação em vez do contrato;
7. documentação normativa divergente do source;
8. falsa percepção de aprovação por a especificação declarar seus próprios achados resolvidos.

## 22. Gate formal

Os critérios de aprovação não são atendidos: existem 5 bloqueadores e 5 altos atuais; achados anteriores não estão todos resolvidos; NF-001–NF-008 não foram resolvidos; há contradição material; vetores de identidade e digest falham; projection não coincide completamente com contratos reais; schemas não estão completos; enums são usados inconsistentemente; e testes não têm todos os oráculos determinísticos.

**Estado final permitido escolhido:** **REPROVADA NA NOVA AUDITORIA FORMAL E DEVOLVIDA PARA CORREÇÃO.**

Não há autorização de implementação.

## 23. Estado final do Git e controles de escopo

Esta seção deve ser lida com o fechamento mecânico final registrado após a gravação:

- mudança causada por esta execução: criação de `SPR017E_NOVA_AUDITORIA_FORMAL.md`;
- todas as 434 entradas iniciais permanecem preexistentes e não atribuídas à auditoria;
- nenhuma outra criação, substituição, renomeação, movimentação ou alteração foi realizada;
- nenhum código foi implementado;
- nenhum teste da SPR-017 foi criado ou executado;
- nenhuma versão foi alterada;
- nenhum wheel foi gerado;
- nenhuma Sprint posterior foi iniciada;
- implementação não foi autorizada.

O SHA-256 final da especificação deve permanecer `38E22AB9D9C71F671C7EA2A8E715EF9BD5A57C53122051C5B84EF642941CC2CE`. O SHA-256, linhas e estado final deste relatório são calculados após esta gravação e apresentados no fechamento da execução; não integram o próprio conteúdo para evitar autorreferência de hash.

## 24. Limitações

Não há implementação SPR-017 a testar. Não foram executados testes, build, instalação ou wheel. CORE-001 e a fonte histórica nominal dos 52 critérios não foram localizados. O relatório perdido completo de SPR-017E não foi recuperado; NF-001–NF-008 foram reconstruídos a partir do resumo e revalidados diretamente. Tais limitações não impedem o gate porque as contradições textuais e os vetores reproduzidos já são bloqueadores.

## 25. Conclusão

A arquitetura independente, a preservação de `KnowledgeProvenance`, a separação de responsabilidades, o namespace UUID e grande parte do modelo conceitual são sólidos. A reespecificação melhorou revisão, cadeia, canonicalização básica, matriz temática e testes, mas ainda não permite que implementações independentes produzam os mesmos IDs, envelopes, digests e relações. A SPR-017 deve retornar à correção normativa e ser submetida a nova auditoria antes de qualquer solicitação posterior de implementação.

Nova auditoria formal da SPR-017 concluída e gravada: especificação reprovada e devolvida para correção, sem autorização de implementação.
