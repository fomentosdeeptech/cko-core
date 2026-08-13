# CKO — RFC-002 — Federated Catalog Protocol

**Processo:** CKO — RFC-002 — Federated Catalog Protocol
**Status:** APPROVED WITH CONDITIONS / HUMAN-RATIFIED / ACTIVE
**Natureza:** especificação técnica exclusivamente documental
**Versão:** 1.0
**Ciclo:** Ciclo Arquitetural II
**Data:** 02/08/2026
**Ratificação humana:** 12/08/2026
**Registro da decisão:** REV-002 — RFC-002 Architectural Decision Review
**Condições vinculantes:** COND-001, COND-002, COND-003, COND-004 e COND-005
**Decisão de origem:** ADR-006 — Federated Catalog Authority, aceito
**Arquitetura de origem:** CKO-ARCH-002 — Ecosystem Evolution Architecture
**Programa:** CKO — GOV-002 — Cycle II Execution Program
**Baseline protegida:** CKO-BASELINE-2026.07
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos
**Implementação:** não autorizada pela aprovação desta RFC
**SPR-018:** OPEN ADMINISTRATIVELY / TECHNICAL IMPLEMENTATION BLOCKED

> Esta RFC especifica o protocolo lógico do Catálogo Federado Institucional
> instituído pelo ADR-006. Não implementa código, não cria contratos no SDK, não
> altera a API pública, não altera a baseline e não autoriza integração, escrita,
> persistência, piloto, publicação operacional ou Sprint.

> **RFC APPROVAL != IMPLEMENTATION AUTHORIZATION.** A decisão
> `APPROVE_WITH_CONDITIONS` foi ratificada humanamente conforme o REV-002. As
> COND-001 a COND-005 são vinculantes nos gates ali definidos e não estão
> automaticamente satisfeitas por esta ratificação. A SPR-018 permanece
> tecnicamente bloqueada até o atendimento de suas demais precedências,
> especificações, auditorias e autorizações por pacote.

## Controle normativo

As palavras **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **PODE** e **RECOMENDADO**
são normativas. Core, Aplicação, Adapter, Provider, Dataset e Corpus Institucional
designam papéis arquiteturais. Os contratos públicos desta RFC pertencem ao
protocolo lógico: não são contratos do SDK, classes, exports, endpoints ou schemas.

## 1. Objetivos do protocolo

O Federated Catalog Protocol (**FCP**) tem por objetivos:

1. permitir descoberta governada sem transferir conteúdo, ownership ou autoridade;
2. estabelecer linguagem comum para observação, registro, verificação, curadoria,
   publicação, consulta e retirada;
3. preservar identidade institucional, identidade na fonte e identidade de versão;
4. tornar autoridade, ownership, stewardship, confiança, acesso, limitações e
   conflitos explícitos;
5. assegurar Provenance da fonte à consulta;
6. separar descoberta, admissão, publicação de metadados e reconhecimento oficial;
7. suportar falha isolada sem converter cache, índice ou projeção em fonte;
8. oferecer contratos lógicos determinísticos, auditáveis e pagináveis;
9. impedir ampliação de acesso pela federação;
10. fornecer critérios para implementação, teste e homologação futuros, inclusive D5.

## 2. Escopo

Esta RFC especifica modelo lógico, entidades, identidades, registros, estados,
ciclo de vida, interfaces, contratos, interações, fluxos de descoberta, publicação,
consulta e Provenance, regras de compatibilidade e critérios futuros de
implementação, teste e homologação.

Abrange registros das classes admitidas pelo ADR-006 quando existência e metadados
puderem ser tratados no perímetro autorizado.

## 3. Não objetivos

Esta RFC NÃO:

- implementa componente nem cria código, pacote, módulo, classe, endpoint ou schema;
- cria contratos, portas ou exports no SDK `cko`;
- altera API, SDK, baseline, build, dependência ou empacotamento;
- escolhe transporte, banco, índice, cache, grafo, serialização ou topologia;
- cria repositório central, data lake, sistema de registro, IAM ou workflow;
- copia ou publica conteúdo original;
- autoriza escrita, correção, movimentação, exclusão ou sincronização em fonte;
- decide retenção, autenticação entre domínios ou persistência canônica;
- declara equivalência, canonicidade, confiança ou oficialidade automaticamente;
- substitui validação humana, autoridade, owner ou steward;
- cria, nomeia, reserva ou autoriza Sprint, piloto ou onda;
- descontinua legado ou promove capacidade ao Core.

## 4. Modelo lógico do Catálogo Federado

### 4.1 Definição e camadas

O Catálogo é uma camada lógica, institucional, governada e auditável de registros e
projeções autorizadas sobre ativos mantidos por fontes autônomas.

```text
fonte governada
  -> Adapter externo (conectividade e evidência técnica)
  -> Provider externo (observação candidata)
  -> Aplicação (composição, política e decisão humana)
  -> FCP (admissão, publicação, consulta e Provenance)
  -> visão autorizada
```

Suas camadas são:

1. **Fonte:** mantém ativo e identidade qualificada.
2. **Observação:** declaração candidata produzida após leitura autorizada.
3. **Registro:** representação institucional mínima admitida.
4. **Projeção:** visão derivada/filtrada vinculada às entradas e políticas.
5. **Consulta:** resposta contextual para finalidade, instante e perímetro.

Cada camada tem identidade e ciclo próprios. Nenhuma substitui a anterior. O
Catálogo é logicamente uno por aplicar regras comuns, mas não exige centralização.

### 4.2 Invariantes

1. Autoridade e ownership permanecem na fonte e nos órgãos competentes.
2. Registro não substitui ativo, original ou sistema de registro.
3. Descoberta não implica admissão, publicação ou oficialidade.
4. Publicar registro não publica conteúdo.
5. Identidade de origem nunca é reescrita por conveniência.
6. Conflito, ausência, restrição e retirada permanecem explícitos.
7. Provenance acompanha toda transição e transformação relevante.
8. Acesso efetivo é a interseção das políticas aplicáveis.
9. Autorização indeterminável produz falha segura.
10. Confiança é multidimensional e não promove estado automaticamente.
11. Correção gera nova declaração; histórico não é reescrito.
12. Cache, índice, exportação e projeção não adquirem autoridade.
13. Indisponibilidade não torna dado expirado atual.
14. Core permanece neutro e independente das implementações do FCP.

## 5. Entidades do protocolo

| Entidade | Finalidade | Identidade mínima |
|---|---|---|
| `CatalogRecord` | Metadados autorizados de ativo admitido. | `record_id` estável e opaco. |
| `SourceDescriptor` | Fonte, domínio, autoridade e capacidades. | `source_id` e versão. |
| `SourceIdentity` | Identificador local qualificado. | `source_id` + `local_id`. |
| `AssetReference` | Referência sem cópia de conteúdo. | Identidade de origem e revisão. |
| `Observation` | Declaração produzida por Provider. | ID, Provider, fonte e tempo. |
| `RelationshipAssertion` | Alegação de relação. | ID, autor, versão e evidência. |
| `AuthorityAssertion` | Competência sobre decisão. | Autoridade, escopo e vigência. |
| `ResponsibilityAssignment` | Owner, steward ou custódia. | Agente, papel, escopo e vigência. |
| `AccessDescriptor` | Classificação e políticas. | Política, autoridade e versão. |
| `TrustAssessment` | Dimensões de confiança. | Avaliador, contexto e evidência. |
| `ProvenanceStatement` | Entidade, agente, atividade e resultado. | ID append-only e ordenável. |
| `PublicationDecision` | Ato sobre publicação. | Autoridade, escopo e instante. |
| `CatalogTombstone` | Retirada sem simular disponibilidade. | `record_id` e decisão. |
| `QueryContext` | Consulente, finalidade e autorização. | `query_id` e consulente. |
| `QueryResult` | Resposta autorizada. | `query_id`, tempo e fontes. |

### 5.1 Classes e relações

Classes primárias: capacidade pública do Core, Aplicação, Adapter, Provider,
Dataset, Corpus Institucional, documento/objeto/coleção/entidade/relação/evidência,
taxonomia/vocabulário/CMC/política, derivado e legado. A classe define perfil
mínimo, não estado, confiança, visibilidade ou autoridade.

Relações mínimas: `describes`, `sourced_from`, `version_of`, `derived_from`,
`member_of`, `succeeds`, `alias_of`, `equivalent_to`, `conflicts_with`,
`governed_by` e `supersedes_statement`. Equivalência, alias e sucessão são
alegações versionadas, não fusões. Extensão desconhecida não produz efeito de
autorização ou estado.

## 6. Identidades

O FCP separa:

1. identidade institucional, estável, opaca e não reutilizável do registro;
2. identidade qualificada `source_id` + `local_id`, preservada sem reescrita;
3. identidade de versão/revisão do ativo;
4. identidade própria de alegação, decisão, confiança e Provenance.

Regras:

- `record_id` permanece estável após mudança de localização, suspensão e retirada;
- identificador retirado não é reutilizado;
- normalização de `local_id` só existe como derivado;
- mudança de `source_id` produz nova identidade qualificada;
- hash, nome, título, caminho, URL ou conteúdo igual não prova identidade;
- identificador preferencial não apaga aliases;
- identidade provisória é limitada e nunca Oficial/T4;
- identidade sensível usa referência protegida ou pseudônimo governado;
- colisão produz conflito, nunca sobrescrita ou fusão;
- resolução retorna evidência, confiança e autoridade.

Continuidade de revisão depende de atestado da fonte ou autoridade. O protocolo
registra, mas não decide sozinho, se uma mudança cria versão ou novo ativo.

## 7. Registros

### 7.1 Envelope obrigatório

| Grupo | Elementos mínimos |
|---|---|
| Controle | ID e versão do registro/FCP, criação e observação. |
| Ativo | classe, tipo, finalidade e descrição mínima. |
| Fonte | IDs de fonte/local, revisão e localização lógica protegida. |
| Responsabilidade | autoridade, owner, steward e custódia relevante. |
| Estado | maturidade, publicação, visibilidade, validade e limitação. |
| Acesso | classificação, audiência, políticas e reutilização. |
| Provenance | observação, admissão e última decisão. |
| Confiança | dimensões, T0–T4, evidências e conflitos. |
| Relações | originais, versões, derivados, coleções e alegações. |
| Ciclo de vida | atualização, expiração, retenção e retirada. |

Informação não revelável é omitida ou vira referência protegida; omissão autorizada
não pode parecer inexistência.

### 7.2 Perfis mínimos

- **Core:** símbolo/capacidade pública e versão; nunca implementação.
- **Aplicação:** jornada, superfície, capacidades, owner e dependências públicas.
- **Adapter:** tecnologia, consistência, paginação, limites e falhas.
- **Provider:** capacidades semânticas, versão, escopo, fontes e limitações.
- **Dataset:** finalidade, schema/versão, aquisição, tempo, qualidade e retenção.
- **Corpus:** escopo, inclusão/exclusão, steward, autoridade, taxonomia e curadoria.
- **Derivado:** atividade, entradas, políticas e vínculo às evidências.
- **Legado:** estado, owner, localização, limitações e ausência de promoção.

Alteração em metadado, estado, relação, acesso, confiança ou decisão produz nova
versão ou declaração vinculada. Versões publicadas são imutáveis. Atualização
exige precondição da última versão; conflito falha sem perda. Integridade deve ser
atestável sem algoritmo imposto. Segredos e dados desnecessários não entram no
registro.

## 8. Estados

O protocolo mantém quatro eixos ortogonais:

1. **maturidade:** Localizado, Registrado, Verificado, Curado ou Oficial;
2. **publicação:** Não publicado, Publicado, Suspenso, Retirado ou Rejeitado;
3. **visibilidade:** Público, Institucional, Restrito ou Existência restrita;
4. **confiança:** T0, T1, T2, T3 ou T4.

| Maturidade | Significado | Guarda mínima |
|---|---|---|
| Localizado | Observação não admitida. | Fonte e Provenance. |
| Registrado | Identidade, owner, finalidade, acesso e Provenance aceitos. | Admissão. |
| Verificado | Metadados e fonte validados. | Identidade, integridade e T2. |
| Curado | Revisão semântica concluída. | Steward, validação humana e T3. |
| Oficial | Estado institucional aprovado. | Autoridade, escopo, vigência e T4. |

| Publicação | Efeito |
|---|---|
| Não publicado | Restrito ao inventário/admissão. |
| Publicado | Metadados descobríveis no perímetro. |
| Suspenso | Uso e consulta bloqueados. |
| Retirado | Publicação encerrada; histórico conforme política. |
| Rejeitado | Admissão/publicação negada; decisão preservada quando legítimo. |

| Confiança | Condição | Uso máximo |
|---|---|---|
| T0 | Evidência insuficiente. | Não publicável. |
| T1 | Fonte e Provenance mínimas. | Inventário restrito. |
| T2 | Identidade, integridade e metadados verificados. | Consulta autorizada. |
| T3 | Contexto, qualidade e uso validados. | Uso governado. |
| T4 | Estado/vigência aprovados. | Oficial no escopo declarado. |

Avaliação declara separadamente autoridade, Provenance, identidade, integridade,
qualidade, atualidade, curadoria, direitos e conflitos. O nível não é média nem
autorização. Oficial pode ser Restrito; Público pode não ser Oficial.

## 9. Ciclo de vida

```text
Localizado/T0-T1
  -> Registrado/T1+
  -> Verificado/T2+
  -> Publicado/T2+
  -> Curado/T3 (opcional)
  -> Oficial/T4 (opcional)
```

| Ação | Origem | Destino | Autoridade mínima |
|---|---|---|---|
| Admitir | Localizado | Registrado | owner e autoridades aplicáveis. |
| Verificar | Registrado | Verificado | função autorizada. |
| Curar | Verificado | Curado | steward. |
| Oficializar | Curado/permitido | Oficial | autoridade institucional. |
| Publicar | Verificado+ | Publicado | autoridade de publicação e owner. |
| Restringir | qualquer ativo | visibilidade menor | poder de bloqueio. |
| Suspender | qualquer ativo | Suspenso | autoridade competente. |
| Restaurar | Suspenso | último válido/nova versão | revalidação e autoridade. |
| Retirar | Publicado | Retirado | owner/autoridade. |
| Rejeitar | candidato | Rejeitado | admissão/publicação. |
| Corrigir | qualquer preservado | nova declaração/versão | autoridade competente. |

Retrocesso não reescreve história. Expiração ou deriva exige revalidação ou
suspensão. Retirada deve alcançar projeções, caches e índices no prazo de política.

## 10. Interfaces lógicas

Estas interfaces representam responsabilidades do protocolo, não interfaces de
programação do Core:

| Interface | Responsabilidade | Operador esperado |
|---|---|---|
| `SourceCapability` | Declarar identidade, versão, capacidades, limites e saúde. | Adapter/Provider. |
| `Discovery` | Produzir observações candidatas paginadas. | Provider com Adapter. |
| `Admission` | Validar envelope e registrar admissão. | Aplicação governada. |
| `IdentityResolution` | Registrar candidatos, alegações e conflitos. | Componente externo autorizado. |
| `Verification` | Validar metadados, fonte, integridade e evidência. | Função autorizada. |
| `Curation` | Registrar revisão semântica do steward. | Aplicação sob stewardship. |
| `Publication` | Publicar, restringir, suspender, restaurar ou retirar. | Aplicação sob autoridade. |
| `CatalogQuery` | Consultar visão autorizada e contextual. | Aplicação consumidora. |
| `ProvenanceTrace` | Recuperar cadeia autorizada. | Aplicação/auditoria. |
| `Conformance` | Declarar versão, capacidades e conformidade. | Todo participante. |

Cada interface DEVE declarar versão, capacidades, classes aceitas, limites, modo
de falha e política de consistência. Capacidade ausente é explícita, não simulada.

## 11. Contratos públicos do protocolo

### 11.1 Envelope de operação

Toda operação recebe identificador e correlação, versão do FCP, capacidades,
agentes técnico/humano, finalidade, audiência, autorização, instante/prazo, escopo,
políticas, paginação, precondição de versão quando aplicável e modo read-only.

Toda resposta declara correlação, resultado, versão/capacidades usadas, instante e
validade, cobertura, fontes consultadas/omitidas/indisponíveis de modo seguro,
política aplicada, dados ou erros autorizados, Provenance e continuação.

Resultados normativos: `success`, `partial`, `denied`, `unavailable`,
`conflict` e `invalid`.

### 11.2 Operações

| Operação | Entrada principal | Saída | Efeito |
|---|---|---|---|
| `DescribeCapabilities` | contexto e versão | fontes, classes, operações e limites | nenhum |
| `Discover` | fonte, escopo, filtro e página | observações e cobertura | somente observação |
| `SubmitForAdmission` | observação, registro candidato e evidências | aceitar, rejeitar ou complementar | registro não publicado |
| `GetRecord` | ID, versão e contexto | visão autorizada ou negativa segura | nenhum |
| `ResolveIdentity` | identidades e contexto | candidatos, conflitos e confiança | não funde |
| `VerifyRecord` | registro, versão e evidências | declaração/versão ou falha | pode alcançar T2 |
| `CurateRecord` | registro, parecer e evidências | decisão do steward | pode alcançar T3 |
| `DecidePublication` | registro, audiência, vigência e aprovações | decisão de publicação | publica metadados |
| `DeclareOfficial` | registro, escopo e decisão | declaração Oficial/T4 | não publica conteúdo |
| `RestrictRecord` | registro, motivo e política | visibilidade menor | nunca amplia |
| `SuspendRecord` | registro, risco e autoridade | suspensão auditável | bloqueia uso |
| `WithdrawRecord` | registro, motivo e retenção | tombstone/referência | encerra publicação |
| `QueryCatalog` | contexto, expressão, projeção e página | resultado autorizado | somente leitura |
| `TraceProvenance` | entidade, profundidade e contexto | subgrafo autorizado | não revela protegidos |
| `Revalidate` | registro, fonte e política | confirmar, corrigir, suspender ou conflitar | não corrige fonte |

### 11.3 Semântica operacional

Observação e consulta são repetíveis sem efeito material. Operações decisórias
exigem chave de idempotência e precondição de versão. Timeout deixa resultado
desconhecido até consulta segura; não autoriza repetição cega.

Paginação usa continuação opaca e escopo estável. Ordenação, facetas e contagens
consideram somente o universo autorizado. Resultado parcial declara cobertura e
validade sem revelar ativos restritos.

Entrada inválida, conflito, negação, indisponibilidade e expiração são distintos
para auditoria. A resposta externa minimiza informação. Quando existência for
protegida, “não encontrado” e “não autorizado” são indistinguíveis.

## 12. Interação entre papéis arquiteturais

### 12.1 Core

Fornece somente contratos, modelos e comportamentos já homologados. Não implementa
autoridade do Catálogo, não conhece fontes e não recebe contrato por esta RFC.

### 12.2 Aplicações

São composition roots: selecionam componentes externos, formam `QueryContext`,
aplicam políticas, orquestram validação humana e registram decisões. Não reduzem
políticas da fonte nem delegam oficialização a algoritmo.

### 12.3 Adapters

Encapsulam tecnologia, autenticação, paginação, retry, quota e falhas. Preservam
identidade/evidência técnica e operam read-only por padrão. Não atribuem significado
ou canonicidade ao que leem.

### 12.4 Providers

Expõem capacidades semânticas e observações candidatas, declarando identidade,
versão, escopo, owner, fontes, cobertura e limitações. Sua saída não entra
automaticamente no Catálogo.

### 12.5 Datasets e Corpora

Dataset mantém finalidade, schema, origem e ciclo operacional; não adquire
autoridade institucional por catalogação. Corpus é coleção curada e governada e
exige steward, autoridade, política de inclusão/exclusão, taxonomia, validação,
Provenance e vínculo com originais. O Catálogo descreve o Corpus; não o constitui.

| Ato | Core | Aplicação | Adapter | Provider | Autoridade/owner/steward |
|---|---|---|---|---|---|
| Ler fonte | não | orquestra | executa | solicita | autoriza |
| Observar | não | recebe | evidencia | produz | valida escopo |
| Admitir | não | orquestra | não | não | decide |
| Verificar/curar | capacidades existentes | registra | apoia | apoia | atesta/decide |
| Publicar metadados | não | executa | não | não | aprova |
| Declarar Oficial | não | registra | não | não | decide |
| Consultar | API existente se aplicável | compõe | acessa | consulta | limita |
| Alterar fonte | não autorizado | não autorizado | não autorizado | não autorizado | processo próprio |

## 13. Fluxos de descoberta

### 13.1 Pré-condições e fluxo

Descoberta exige fonte, owner, finalidade, perímetro, classificação, autorização
de leitura, método reproduzível e política de Provenance.

1. Aplicação cria envelope read-only.
2. Provider declara capacidade e seleciona Adapter.
3. Adapter autentica com menor privilégio e registra versão/cobertura.
4. Adapter lê metadados autorizados sem alterar a fonte.
5. Provider cria `Observation`, preservando valores de origem.
6. Mapeamento gera Provenance de agente, atividade, política, entrada e resultado.
7. Aplicação recebe observações paginadas e cobertura explícita.
8. Observações permanecem Localizadas e Não publicadas até admissão separada.

Falha parcial produz `partial`, declara cobertura e impede interpretar ausência
como inexistência. Retry respeita idempotência, quota e consistência. Credencial
insuficiente não pode ser contornada.

Discovery NÃO move, corrige, classifica institucionalmente, deduplica de forma
destrutiva, admite automaticamente, publica, oficializa ou amplia acesso.

## 14. Fluxos de publicação

### 14.1 Admissão

Uma observação somente vira Registrada com:

1. escopo e finalidade legítima;
2. autoridade da fonte, owner e steward/função equivalente;
3. identidades suficientes e conflitos explícitos;
4. classe e vínculos com originais/derivados;
5. Provenance mínima verificável;
6. direitos, licença, consentimento e tratamento aplicáveis;
7. classificação, audiência e regra de consulta;
8. versão, temporalidade, atualização, retenção e retirada;
9. qualidade, limitações e confiança;
10. aprovações das autoridades aplicáveis.

### 14.2 Publicar registro

1. Vínculo com fonte e evidência são verificados.
2. Registro alcança no mínimo Verificado/T2.
3. Owner e steward aprovam metadados, finalidade e limitações.
4. Segurança, privacidade, dados e fonte exercem bloqueios.
5. Autoridade define audiência, escopo, vigência e política.
6. `DecidePublication` cria decisão append-only.
7. Somente a projeção mínima autorizada torna-se descobrível.
8. Projeções recebem decisão e prazo de revalidação.

Publicação de conhecimento institucional exige ainda curadoria, validação humana,
direitos, vínculo com originais, política de inclusão/exclusão e decisão Oficial/T4.
O ato não publica conteúdo e vale apenas no escopo e período declarados.

Incidente, expiração, revogação, Provenance quebrada ou conflito crítico exige
restrição, suspensão ou retirada. A decisão alcança projeções e consultas futuras;
histórico segue retenção, privacidade e autoridade.

## 15. Fluxos de consulta

Toda consulta começa com consulente autenticado, finalidade, audiência, escopo,
atributos de autorização, política e instante. Autenticação e concessão são externas.

1. Aplicação valida `QueryContext`.
2. Plano lógico determina candidatos sem revelá-los.
3. Calcula-se a interseção das políticas institucional, fonte, ativo, Aplicação e
   consulente.
4. Filtros de existência/metadados antecedem contagem, faceta e recuperação.
5. Providers/Adapters consultam somente fontes autorizadas.
6. Resultados são relacionados explicitamente, nunca fundidos destrutivamente.
7. Resposta apresenta fonte, versão, estado, confiança, limitações e Provenance.
8. Cobertura, conflito e indisponibilidade aparecem sem inferência indevida.
9. Consulta é auditada proporcionalmente ao risco.

`success` exige fontes obrigatórias; `partial` indica cobertura incompleta;
`denied` minimiza a negativa; `unavailable` indica resposta/autorização
indeterminável; `conflict` impede resposta unívoca; `invalid` rejeita envelope.

Consulta não concede conteúdo ou reutilização. Cache/exportação é derivado com
owner, validade, Provenance, política e revogação próprios, nunca fonte de verdade.

## 16. Fluxos de Provenance

Provenance é obrigatória para observação, mapeamento, admissão/rejeição, identidade,
verificação/confiança, curadoria, validação humana, publicação/oficialização,
restrição/suspensão/restauração/retirada, projeção, consulta e correção.

Cada declaração permite determinar entidade, fonte, localização lógica, versão,
agentes, atividade, instante, finalidade, entradas, parâmetros, políticas,
transformações, resultado, evidências, estado, autoridade e acesso.

```text
ativo na fonte
  <- observação <- mapeamento <- registro admitido
  <- verificação/curadoria <- decisão de publicação
  <- projeção autorizada <- resposta de consulta
```

Cada seta é identificável. A cadeia pode ser distribuída, mas é navegável no
perímetro autorizado e explicita lacunas. Digest não substitui contexto ou
autoridade. Declarações são imutáveis/append-only; correção usa
`supersedes_statement`. Dados sensíveis são minimizados e o trace aplica as
mesmas políticas da consulta principal.

## 17. Regras de compatibilidade

### 17.1 Superfícies protegidas

| Superfície | Regra |
|---|---|
| CKO-BASELINE-2026.07 | Nenhuma alteração, reabertura ou promoção. |
| SDK `cko` 1.0.0 | Nenhum módulo, dependência, comportamento ou empacotamento novo. |
| API pública | 646 exports preservados; nenhum símbolo criado, removido, renomeado, depreciado ou reinterpretado. |
| Core | Neutro, com dependências orientadas para dentro. |
| Fontes e legado | Originais, comportamento e autoridade preservados. |
| Provenance | Fundação homologada consumida somente pelos contratos atuais. |

### 17.2 Versionamento e evolução

O FCP usa versão lógica `major.minor`, distinta das versões do registro e ativo:

- **minor:** extensão opcional e compatível;
- **major:** mudança de significado, remoção, nova obrigação ou efeito de estado;
- revisão documental: correção sem efeito semântico.

Campos opcionais, relações sem efeito automático, classes negociadas e diagnósticos
preserváveis são compatíveis em minor. Participantes ignoram com segurança ou
preservam extensões desconhecidas, sem inferir autorização, publicação, identidade
ou oficialidade. Novo estado, transição, operação obrigatória ou semântica de
acesso exige major e governança.

Participantes negociam versão e capacidades antes de operar. A operação usa apenas
a interseção compatível; capacidade obrigatória ausente falha explicitamente.
Degradação só é aceita quando preserva segurança, Provenance e semântica.

Serialização futura deve preservar tipos, identidade, temporalidade, referências,
ordenação necessária e valores desconhecidos. Esta RFC não escolhe formato
canônico nem algoritmo de digest.

## 18. Critérios para futura implementação

Nenhuma implementação inicia por força desta RFC. Proposta futura só estará apta
quando demonstrar:

1. D1 e D2 aplicáveis aprovados, escopo e necessidade evidenciados;
2. D3 aplicável e Sprint própria antes de código executável;
3. fronteiras de Core, Aplicação, Adapter e Provider preservadas;
4. zero alteração implícita em SDK, API e baseline;
5. tecnologia, credenciais, configuração e fontes fora do Core;
6. perfis de registro/mapeamento por classe e fonte aprovados;
7. identidade, conflito, concorrência e idempotência especificados;
8. autorização em consulta, minimização e negativa segura;
9. read-only por padrão e nenhuma escrita na fonte;
10. Provenance ponta a ponta, append-only e protegida;
11. falha parcial, timeout, retry, paginação, expiração e revogação;
12. observabilidade sem vazamento de conteúdo sensível;
13. isolamento por fonte, Provider, Adapter, domínio e Aplicação;
14. desligamento, rollback e preservação do legado;
15. fixtures isoladas e dados sintéticos/autorizados;
16. owners, stewards e autoridades aprovadoras;
17. análise de ameaça, privacidade, direitos, licença e retenção;
18. plano de compatibilidade e migração do FCP;
19. SLOs e prazos de revogação aprovados por instrumento próprio;
20. nenhuma escolha pendente de persistência ou IAM tratada como implícita.

Persistência, índice físico, autorização entre domínios, escrita bidirecional,
retenção ou promoção ao Core exigem instrumento próprio quando ultrapassarem as
autoridades aprovadas.

## 19. Critérios de teste

### 19.1 Contrato e modelo

- perfis mínimos por classe;
- estabilidade e não reutilização de identidades;
- transições válidas e rejeição das inválidas;
- ortogonalidade entre maturidade, publicação, visibilidade e confiança;
- histórico append-only e conflito otimista;
- negociação de versão/capacidade e extensões desconhecidas;
- serialização/desserialização semanticamente equivalentes.

### 19.2 Segurança e privacidade

- menor privilégio e interseção de políticas;
- filtragem antes de contagem, faceta, ordenação e erro;
- indistinguibilidade de inexistência e existência não revelável;
- prevenção de inferência por paginação, tempo, métricas e mensagens;
- revogação, expiração, suspensão e retirada em projeções/caches;
- ausência de segredo/conteúdo desnecessário em registro, log e Provenance;
- falha segura quando autorização não puder ser determinada.

### 19.3 Federação e resiliência

- falha parcial por fonte e cobertura explícita;
- timeout, retry, backoff, quota, paginação e continuação;
- idempotência e recuperação de resultado desconhecido;
- cache indisponível/expirado nunca promovido a fonte;
- isolamento/desligamento por fonte, Adapter, Provider, domínio e Aplicação;
- concorrência sem sobrescrita e determinismo com fixtures fixas.

### 19.4 Provenance e compatibilidade

- rastreabilidade ponta a ponta e correção por declaração vinculada;
- detecção explícita de lacuna/conflito e filtragem do subgrafo;
- integridade, ordenação, correlação e atribuição de agentes;
- caracterização do legado e golden files de mapeamento;
- testes contratuais por interface, Adapter e Provider;
- integração apenas com fixtures isoladas;
- execução read-only/dry-run, rollback e desligamento;
- regressão integral do SDK e verificação mecânica dos 646 exports.

Nenhum teste pode escrever em Drive, Downloads, `02_Knowledge`, banco, Dataset,
Corpus ou acervo real por autorização desta RFC.

## 20. Critérios de homologação

### 20.1 Homologação documental

Esta RFC pode ser aprovada quando:

- estiver coerente com ADR-006, ARCH-002, GOV-002, GOV-003 e baseline;
- cobrir todos os elementos técnicos exigidos;
- separar contrato lógico do FCP e API do SDK;
- não autorizar implementação, Sprint, escrita ou persistência;
- for revisada por arquitetura, governança, segurança, dados e domínios afetados;
- registrar pendências como dependências, não decisões ocultas.

Aprovação documental torna a RFC referência, mas não torna onda, piloto ou
implementação Autorizada ou Em execução.

### 20.2 Homologação futura de implementação

Exige:

1. matriz requisito–teste–evidência;
2. compatibilidade da baseline, SDK 1.0.0 e 646 exports;
3. perfis de fonte e contratos externos aprovados;
4. evidência read-only e ausência de mutação;
5. Provenance completa e auditável;
6. testes de segurança, privacidade, resiliência, contrato e regressão;
7. owners, stewards e autoridades identificados;
8. limites, riscos, incidentes, exceções e cobertura;
9. suspensão, retirada, desligamento e rollback ensaiados;
10. homologação humana e decisões D3/D4 aplicáveis.

### 20.3 Gate D5

A federação delimitada somente satisfaz D5 quando:

- catálogo, autorização e Provenance ponta a ponta estiverem demonstrados;
- vínculo com originais, identidade e autoridade estiver preservado;
- consultas aplicarem menor privilégio e negativa segura;
- conflitos, lacunas, confiança, parcialidade e validade estiverem explícitos;
- não houver centralização ou canonicidade não autorizada;
- publicação e oficialização forem atos distintos e rastreáveis;
- revogação alcançar projeções/caches no prazo aprovado;
- governança, owners, stewards, segurança e autoridades aprovarem a evidência ou
  registrarem restrições.

Não conformidade material impede homologação. D5 pode homologar, restringir,
exigir correção ou retirar a trilha; nunca promove capacidade ao Core.

## 21. Segurança, privacidade e falhas

- Política da fonte é piso e não pode ser relaxada.
- Existência, metadados, contagens e Provenance podem ter classificações distintas.
- Acesso ao registro não implica acesso ao ativo.
- Falha do Catálogo não autoriza bypass ou consulta direta.
- Logs registram decisão/correlação sem dados desnecessários.
- Incidente crítico pode suspender fonte, Adapter, Provider, domínio ou Aplicação
  sem afetar original ou trilhas isoladas.
- Segurança, privacidade, fonte e Corpus mantêm poder de bloqueio.

## 22. Dependências e decisões diferidas

### 22.1 Dependências normativas

- CKO-GOV-001 e CKO-BASELINE-2026.07;
- CKO-ARCH-001 e contratos homologados do SDK `cko` 1.0.0;
- CKO-ARCH-002;
- GOV-002;
- ADR-006, conforme registro canônico reconciliado pelo GOV-003;
- autoridades, owners e stewards das fontes e domínios.

### 22.2 Dependências futuras condicionais

- perfis de mapeamento por classe/fonte;
- autorização e isolamento entre domínios;
- retenção, exclusão e dados pessoais;
- SLOs, validade, revogação e disponibilidade;
- transporte, serialização, persistência, índice e topologia;
- contratos externos de Adapter/Provider e jornadas;
- ambientes, fixtures e observabilidade;
- operação em escala e conformidade contínua.

Essas dependências não são resolvidas nem autorizadas aqui. Persistência/índice
físico só podem ser avaliados se a federação demonstrar necessidade.

## 23. Justificativa técnica

Separar fonte, observação, registro, projeção e consulta impede confundir
conectividade com autoridade ou agregação com consolidação. Estados ortogonais
impedem tratar “público”, “verificado” e “oficial” como sinônimos. Identidades em
camadas preservam origem sem bloquear relações entre fontes. Provenance append-only
torna transformação e decisão auditáveis.

Negociação de capacidades, respostas parciais, idempotência, concorrência otimista
e negativas seguras permitem federação resiliente sem escolher tecnologia. O nível
de abstração é testável e suficiente para D5, sem antecipar schema, transporte,
persistência, IAM ou implantação.

## 24. Impactos arquiteturais

### 24.1 Imediatos

- semântica técnica comum para o Catálogo Federado;
- decisões de identidade, estado, publicação e consulta testáveis;
- fronteiras e responsabilidades explícitas;
- referência para RFCs futuras de mapeamento, composição e piloto;
- tradução do ADR-006 em critérios verificáveis para D5.

Os impactos são exclusivamente documentais. Não há mudança em código, runtime,
dados, contratos do SDK, API, build, dependências, banco, baseline ou operação.

### 24.2 Futuros condicionais

Com autorização própria, poderão existir implementações externas, Adapters,
Providers, composition roots, projeções, políticas e suítes de conformidade. Tudo
permanece externo ao Core até decisão formal e preserva os 646 exports.

| Risco | Controle |
|---|---|
| Centralização prematura | Federação lógica e persistência diferida. |
| Oficialização indevida | Estados e atos separados. |
| Perda de autoridade | Atribuição e bloqueios por competência. |
| Fusão incorreta | Alegações versionadas e conflitos explícitos. |
| Vazamento | Interseção de políticas, filtro prévio e negativa segura. |
| Deriva | Validade, revalidação, Provenance e suspensão. |
| Acoplamento ao Core | Interfaces externas e API congelada. |
| Falha distribuída | Resultado parcial, cobertura e isolamento. |

## 25. Conformidade da própria RFC

Esta RFC é compatível por construção: deriva do ADR-006; observa a numeração
canônica do GOV-003; aplica ARCH-002 e GOV-002; preserva baseline, SDK e API;
especifica comportamento lógico sem implementação; mantém fontes, originais,
legado, autoridade, ownership e stewardship; e não cria Sprint ou código.

## 26. Declaração final

Fica especificado o FCP como protocolo lógico, governado e auditável para
descoberta, registro, publicação, consulta e Provenance de ativos distribuídos.
Preserva identidades e autoridades nas fontes, mantém Core neutro, usa Aplicações
como composition roots, Adapters para conectividade e Providers para observações.

Registros são referências e evidências autorizadas; não substituem ativos nem
publicam conteúdo. Datasets não ganham autoridade por catalogação. Corpora exigem
stewardship, validação e autoridade. Nenhuma transição decorre de descoberta ou
score automático.

Esta RFC não implementa código, não cria contratos no SDK, não altera API pública,
baseline ou versão, não cria Sprint e não autoriza escrita, centralização,
persistência, piloto, promoção ou descontinuação. Execução futura depende dos
instrumentos e gates do GOV-002 e das autoridades aplicáveis.

## Referências

- [ADR-006 — Federated Catalog Authority](../adr/ADR-006_FEDERATED_CATALOG_AUTHORITY.md)
- [Índice canônico de ADRs](../adr/INDEX.md)
- [GOV-003 — ADR Governance Reconciliation](../governance/GOV-003_ADR_GOVERNANCE_RECONCILIATION.md)
- [CKO-ARCH-002 — Ecosystem Evolution Architecture](../arquitetura/CKO-ARCH-002_ECOSYSTEM_EVOLUTION_ARCHITECTURE.md)
- [GOV-002 — Cycle II Execution Program](../governance/GOV-002_CYCLE_II_EXECUTION_PROGRAM.md)
- [ARCH-001 — CKO CORE SDK](../../ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md)
- [CKO-ARCH-001 — Arquitetura Canônica](../../../docs/arquitetura/CKO-ARCH-001_ARQUITETURA_CANONICA.md)
- [CKO-GOV-001 — Baseline Arquitetural 1.0](../../../docs/governance/CKO-GOV-001_BASELINE_ARQUITETURAL_1.0.md)
