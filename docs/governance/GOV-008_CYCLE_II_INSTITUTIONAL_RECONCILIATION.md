# CKO — GOV-008 — Cycle II Institutional Reconciliation

## 1. Identificação

**Processo:** CKO — GOV-008 — Cycle II Institutional Reconciliation
**Título institucional:** Reconciliação Institucional do Ciclo II
**Versão:** 1.1-ratificada
**Data:** 10/08/2026, `America/Sao_Paulo`
**Data da ratificação:** 10/08/2026
**Autoridade da ratificação:** Ratificação humana do responsável institucional pelo projeto CKO
**Escopo da ratificação:** reconciliação institucional e documental do Ciclo II
**Natureza:** proposta de ato institucional e reconciliação documental
**Repositório canônico observado:** `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`
**Branch observada:** `main`
**HEAD local e remoto observado:** `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`
**Baseline protegida:** `CKO-BASELINE-2026.07`, apontando para o mesmo commit
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos
**Predecessores materiais:** CKO-GOV-001, CKO-ARCH-001, CKO-ARCH-002, GOV-002, GOV-003, GOV-005, GOV-006 e GOV-007
**Objeto operacional relacionado:** OPS-004
**Efeito desta emissão:** exclusivamente documental; criação desta proposta, sem migração física ou consolidação Git

## 2. Status

**STATUS: RATIFICADA / OFFICIAL / ACTIVE**

### Registro de ratificação humana

Em 10/08/2026, o responsável institucional pelo projeto CKO ratificou humanamente esta GOV-008, conferindo força institucional às decisões de reconciliação e às decisões D01–D08 registradas neste documento. A ratificação reconhece expressamente ARCH-002, GOV-002, GOV-003, GOV-006 e GOV-007 como `OFFICIAL / ACTIVE`; GOV-005 como `OFFICIAL EVIDENCE / HISTORICAL SNAPSHOT`; e ADR-006 como `ACCEPTED / ACTIVE`, preservada sua identificação histórica interna como ADR-001.

A ratificação **não** aprova RFC-002, **não** libera implementação da SPR-018, **não** libera OPS-005, **não** autoriza migração física, normalização EOL ou alteração da baseline e **não** autoriza consolidação Git automaticamente. Toda execução posterior continua dependente dos instrumentos, gates e changesets independentes definidos nesta GOV-008.

### Registro histórico da proposta

Esta GOV-008 foi originalmente emitida em 10/08/2026 com status `PROPOSTA PARA RATIFICAÇÃO`. Naquele estado, suas deliberações eram propostas completas e internamente coerentes, mas sem força institucional própria. As redações prospectivas e expressões “proposta” preservadas nas seções seguintes documentam fielmente esse estado anterior; desde a ratificação registrada acima, seus resultados e D01–D08 passam a ter força institucional nos limites expressos, sem reescrita silenciosa da proposta original.

## 3. Autoridade

A autoridade material aplicável segue esta ordem:

1. CKO-GOV-001 e a baseline arquitetural/técnica publicada;
2. CKO-ARCH-001 e os contratos e evidências homologados do SDK 1.0.0;
3. CKO-ARCH-002, se ratificada no conjunto documental pós-baseline;
4. ADRs aceitos, com identidade e status administrados pelo índice canônico e GOV-003;
5. programas e atos GOV, cada qual dentro de sua matéria;
6. RFCs aprovadas; RFCs em draft apenas especificam propostas;
7. termos de Sprint, especificações, implementações e homologações dentro de autorizações expressas.

Uma localização, nome, data de modificação, presença no working tree ou autodeclaração de status não cria autoridade. A ratificação desta GOV-008 pode reconhecer e consolidar documentos documentais pós-baseline porque não altera a baseline e porque a autoridade humana ratificadora atua sobre o estado institucional posterior; não pode, contudo, aprovar silenciosamente uma RFC técnica nem autorizar implementação.

## 4. Contexto

A AUD-001 — Working Tree Consolidation Audit registrou que `main`, `origin/main` e a tag `CKO-BASELINE-2026.07` convergem no commit `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`, enquanto o working tree contém documentação institucional do Ciclo II ainda fora do HEAD. A inspeção desta reconciliação confirmou a convergência dos três refs e a presença dos documentos pós-baseline como modificados ou não rastreados.

O Ciclo I permanece encerrado e protegido. O Ciclo II foi descrito por uma cadeia documental coerente em intenção — arquitetura complementar, programa por ondas, reconciliação de ADRs, decisão de catálogo, RFC proposta, Sprint condicionada, auditoria, dossiê e política organizacional — mas essa cadeia não foi consolidada no repositório e vários documentos atribuíram a si próprios estados como “oficial”, “vigente” ou “aceito”. Esta GOV-008 separa conteúdo tecnicamente coerente de autoridade institucional demonstrada.

## 5. Problema

Há cinco problemas institucionais simultâneos:

1. documentos pós-baseline apresentam força declarada superior à evidência externa disponível;
2. ADR-006 possui identidade canônica externa incompatível com a identificação histórica interna ADR-001;
3. RFC-002 continua em draft, embora a SPR-018 tenha sido administrativamente aberta sobre uma cadeia condicionada à sua aprovação;
4. OPS-004 declara totais que sua estrutura atual não permite reproduzir;
5. o working tree mistura documentos institucionais, configurações locais, cópias de código e metadados gerados.

Sem reconciliação, uma futura consolidação Git poderia parecer ratificar por acidente documentos, números ou autorizações ainda não decididos.

## 6. Escopo

Esta proposta:

- reconstrói autoridade, vigência, proveniência e maturidade dos documentos do Ciclo II;
- propõe status inequívocos para ARCH-002, GOV-002, GOV-003, GOV-005, GOV-006, GOV-007, ADR-006, RFC-002, SPR-018 e OPS-004;
- delibera D01–D08 para ratificação humana;
- define políticas de autoridade, proveniência, maturidade, retenção, logs e EOL;
- classifica os artefatos não institucionais indicados;
- define requisitos para regenerar a OPS-004 e gates futuros.

## 7. Fora de escopo

Não são autorizados por esta GOV-008: alteração de código, runtime, banco, testes, SDK, API, dados ou baseline; migração, movimento, renomeação ou exclusão de arquivos; deduplicação; OPS-005; implementação da RFC-002 ou SPR-018; alteração de tag ou histórico; staging, commit, push, pull, reset, clean; normalização de EOL; alteração de releases, backups, checkpoints, pacotes ou logs.

## 8. Baseline protegida

`CKO-BASELINE-2026.07` é imutável. O tag, o commit apontado, o corpus histórico e sua proveniência não podem ser alterados para absorver retroativamente o Ciclo II. Compatibilidade futura deve ser aditiva e externa à baseline. Nenhum alias, redirecionamento, índice ou reorganização pode mudar bytes protegidos ou falsear a localização histórica. Nesta execução, a baseline foi somente inspecionada.

## 9. Cadeia institucional

| ID | Título/data/tipo | Predecessor → sucessor | Autoridade, proveniência e dependências | Declarado / demonstrável | Resultado proposto após ratificação |
|---|---|---|---|---|---|
| CKO-GOV-001 | Baseline Arquitetural 1.0; 12/07/2026; ato institucional | Discoveries + CKO-ARCH-001 → toda evolução | Corpus institucional predecessor; baseline e governança | VIGENTE / demonstrado por ato externo ao CORE | OFFICIAL / ACTIVE, preservado |
| CKO-ARCH-001 | Arquitetura Canônica; Ciclo I; arquitetura | Discoveries → CKO-ARCH-002 | Integra a baseline; depende de GOV-001 | OFICIAL / demonstrado por GOV-001 | OFFICIAL / ACTIVE, preservado |
| ARCH-002 | Ecosystem Evolution; 02/08/2026; arquitetura complementar | GOV-001/ARCH-001 → GOV-002 | Nativo pós-baseline; depende da preservação do Ciclo I | oficial / conteúdo coerente, autoridade externa ainda não consolidada | OFFICIAL / ACTIVE por ratificação humana desta GOV-008 |
| GOV-002 | Cycle II Execution Program; 02/08/2026; programa | ARCH-002 → ADR/RFC/Sprints por ondas | Nativo pós-baseline; depende de ARCH-002 | oficial / programa coerente, ainda fora do HEAD | OFFICIAL / ACTIVE por ratificação humana |
| GOV-003 | ADR Governance Reconciliation; 02/08/2026; governança | índice/ADRs históricos → ADR-006/INDEX | Nativo pós-baseline; preserva conteúdo histórico | oficial / reconciliação coerente, ainda fora do HEAD | OFFICIAL / ACTIVE por ratificação humana |
| ADR-006 | Federated Catalog Authority; 02/08/2026; ADR | ARCH-002 + GOV-002 + GOV-003 → RFC-002 | Arquivo pós-baseline; identidade administrada pelo índice | “ADR-001”, aceito / mérito coerente; número interno divergente | ACCEPTED / ACTIVE como ADR-006, com identidade histórica preservada |
| RFC-002 | Federated Catalog Protocol; 02/08/2026; RFC | ADR-006 → eventual especificação aprovada | Nativa pós-baseline; `1.0-draft` | proposta para aprovação / draft inequívoco | PROPOSED / DRAFT; não aprovada |
| SPR-018 | Termo de Abertura; 03/08/2026; Sprint | GOV-002 + ADR-006 + RFC-002 aprovada + D0–D4 → D5 | Nativo pós-baseline; depende de gates e especificações por pacote | autorizada com execução condicionada / planejamento possível, implementação bloqueada | OPEN administrativamente / TECHNICAL IMPLEMENTATION BLOCKED |
| GOV-005 | Auditoria Histórica de Esforço; 03/08/2026; auditoria | corpus histórico → GOV-006/GOV-007 | Raiz do CORE; evidência analítica, não norma arquitetural | sem campo Status explícito / auditoria concluída e limitada | OFFICIAL EVIDENCE / HISTORICAL SNAPSHOT; não norma material |
| GOV-006 | Project Dossier; 03/08/2026; dossiê | GOV-005 + cadeia anterior → GOV-007/GOV-008 | Nativo pós-baseline; fotografia institucional | vigente / síntese coerente, ainda não consolidada | OFFICIAL / ACTIVE como dossiê de corte, por ratificação humana |
| GOV-007 | Repository Canonical Organization; 03/08/2026; política | GOV-006 + GOV-003 → OPS-004 | Nativa pós-baseline; normativa sem execução | oficial / conteúdo compatível; força ainda não consolidada | OFFICIAL / ACTIVE por ratificação humana |
| OPS-004 | Repository Canonical Migration Plan; 03/08/2026; plano analítico | GOV-007 → nova OPS-004; depois, talvez OPS-005 | Pós-baseline; inventário não estruturalmente íntegro | plano proposto / totais não reproduzíveis | NON-EXECUTABLE ANALYTICAL PLAN / SUPERSEDED somente após substituto aceito |
| GOV-008 | Esta reconciliação; 10/08/2026; GOV ratificada | AUD-001 + cadeia acima → ratificação humana | Nativa do working tree; ratificada pelo responsável institucional | proposta original seguida de ratificação humana em 10/08/2026 | RATIFICADA / OFFICIAL / ACTIVE |

Não foi localizada cópia da AUD-001 nem relatório material equivalente no corpus pesquisado. Seus resultados são tratados como premissa fornecida pela ordem desta etapa e foram corroborados, quando possível, por inspeção Git; a ausência do artefato local permanece pendência documental anterior à consolidação Git. Sua futura incorporação deverá preservar origem, data, contexto, resultados, relação com a GOV-008 e proveniência verificável. Nenhuma AUD-001 foi inventada ou reconstruída nesta execução.

## 10. Reconciliação ARCH-002

ARCH-002 complementa, sem substituir, GOV-001/ARCH-001; preserva baseline, SDK e API; separa arquitetura de implementação; adota federação, autoridade na fonte, leitura antes de escrita e reversibilidade. Não foi encontrado conflito material com o Ciclo I. **Proposta:** ratificar como `OFFICIAL / ACTIVE`, exclusivamente arquitetural e documental. A ratificação não aprova RFC, Sprint, código ou migração.

## 11. Reconciliação GOV-002

GOV-002 converte ARCH-002 em programa de ondas II.0–II.7 e gates D0–D7, mantendo ADR → RFC → Sprint e decisões humanas. **Proposta:** `OFFICIAL / ACTIVE`. Seus gates são controles, não evidência de que foram satisfeitos. As D01–D08 desta GOV-008 são decisões sobre organização documental e não substituem D0–D7 do programa.

## 12. Reconciliação GOV-003

GOV-003 preserva a série de ADRs, torna o índice fonte administrativa e cria a reconciliação externa de ADR-006 sem reescrever o artefato aceito. **Proposta:** `OFFICIAL / ACTIVE`. Seu alcance é identificação e ciclo de vida documental; o mérito do ADR-006 depende de ratificação humana explícita nesta cadeia.

## 13. Reconciliação ADR-006

Adota-se a alternativa **A combinada com mecanismo institucional C**: preservar integralmente o conteúdo histórico, inclusive título e metadados internos “ADR-001”, e manter reconciliação externa pelo GOV-003, `docs/adr/INDEX.md` e esta GOV-008. Não se executará correção editorial no ADR, porque trocar seu identificador interno após aceitação alteraria a evidência de produção e faria parecer que nasceu como ADR-006. Referências prospectivas devem usar `ADR-006`; referências históricas podem registrar “produzido como ADR-001”. **Proposta:** `ACCEPTED / ACTIVE` como ADR-006 após ratificação. Nenhuma implementação decorre dessa aceitação.

## 14. Reconciliação RFC-002

RFC-002 é `1.0-draft`, declara “proposta para aprovação” e exclui implementação. **Decisão:** permanece `PROPOSED / DRAFT`. Esta GOV-008 não avalia nem concede aprovação arquitetural de seu protocolo. Aprovação futura exige revisão técnica própria, autoridade identificada e registro controlado. A mera existência de ADR-006 ou SPR-018 não supre esse gate.

## 15. Reconciliação SPR-018

A abertura administrativa é compatível com planejamento e especificação, mas o próprio Termo condiciona implementação à aprovação da RFC-002, D0–D4 aplicáveis, especificação e auditoria por pacote, ambientes e acessos autorizados, testes, rollback e autorização expressa. **Decisão:** `OPEN ADMINISTRATIVELY / TECHNICAL IMPLEMENTATION BLOCKED`. Nenhum código, teste com fonte real, commit ou pacote técnico está autorizado. Se RFC-002 for rejeitada, a Sprint deve ser replanejada, suspensa ou encerrada por ato próprio.

## 16. Reconciliação GOV-005

GOV-005 é uma auditoria histórica analítica, não um ato normativo material. O prefixo GOV é aceitável como série institucional porque formaliza método, limites e evidência para governança; ele não deve ser interpretado como aprovação de suas estimativas. Seu local canônico futuro, conforme GOV-007, é `docs/audits/` — preferencialmente `docs/audits/documentation/` ou família de auditoria institucional que o índice futuro definir — e não a raiz. O arquivo não será movido nesta etapa. **Proposta:** `OFFICIAL EVIDENCE / HISTORICAL SNAPSHOT`, predecessor factual do dossiê GOV-006 e insumo organizacional de GOV-007.

## 17. Reconciliação GOV-006

GOV-006 é dossiê executivo de corte, derivado da cadeia e da GOV-005. Distingue fatos, inferências e estimativas e reconhece que documentos pós-tag não integram automaticamente a baseline. **Proposta:** `OFFICIAL / ACTIVE` como porta de entrada institucional referente ao corte de 03/08/2026, sem substituir fontes especializadas. Declarações de status sobre o Ciclo II passam a ser lidas segundo esta GOV-008 após ratificação.

## 18. Reconciliação GOV-007

GOV-007 é coerente com predecessores, preserva a baseline e a proveniência, separa norma de execução e define gates R0–R9. A árvore é destino normativo, não estado realizado. D01–D08 fortalecem seus limites e não criam incompatibilidade material. **Proposta:** ratificar como `OFFICIAL / ACTIVE`, com a ressalva vinculante de que sua taxonomia é refinada pela D03 desta GOV-008 e nenhuma reorganização ou OPS-005 fica autorizada.

## 19. Reconciliação OPS-004

OPS-004 fica classificada como **PLANO ANALÍTICO NÃO EXECUTÁVEL**. Ela declara 281 artefatos, 147 migrações, 134 permanências e 106 bloqueados, mas o arquivo observado possui 254 linhas físicas e apenas 59 linhas estruturais que começam como registros `INV-NNN` detectáveis; portanto não materializa um registro estrutural por cada um dos 281 artefatos. As contagens 281/147/134/106 não são reproduzíveis a partir da tabela presente. Os grupos de duplicatas e órfãos são evidências analíticas úteis, não base executiva. Nenhuma migração pode usar esse inventário. O plano permanece preservado e só se torna `SUPERSEDED / HISTORICAL` quando uma versão regenerada for aceita; até lá, é `PROPOSED / BLOCKED / NON-EXECUTABLE`.

## 20. Decisão D01 — Baseline

**Decisão proposta:** a baseline é imutável. Não mover, renomear, editar ou regenerar conteúdo do tag. Compatibilidade futura usará índice, alias ou mapa externo, aditivo, versionado e reversível, sem modificar os bytes históricos. Qualquer mecanismo deve distinguir caminho histórico de caminho corrente, validar links e oferecer rollback. Estado: **DECIDIDA PARA RATIFICAÇÃO; execução não autorizada**.

## 21. Decisão D02 — Duplicatas

**Decisão proposta:** fonte canônica é eleita por matéria com estes critérios objetivos, nesta ordem: autoridade formal; status aprovado; pertencimento ao corpus corrente; identidade/versão; completude; proveniência; integridade/hash; manutenção e referências. Cópias em release, backup, checkpoint ou pacote são `RELEASE EVIDENCE` ou `HISTORICAL COPY` e permanecem intactas. Duplicata operacional corrente deve apontar para a fonte canônica; divergência semântica impede deduplicação. Hash igual prova identidade de bytes, não autoridade. Nenhuma exclusão automática é permitida.

## 22. Decisão D03 — Documentos superseded, obsoletos e legados

**Taxonomia definitiva proposta:**

| Estado | Regra |
|---|---|
| ACTIVE | rege o presente dentro do escopo declarado |
| SUPERSEDED | possui sucessor identificado e perdeu precedência prospectiva; continua preservado |
| OBSOLETE | contexto/premissa cessou e não deve orientar novas ações; exige ato, justificativa e avaliação de consumidores |
| HISTORICAL | prova um corte, decisão ou execução passada; não implica inaplicabilidade do conteúdo em seu contexto |
| ARCHIVED | estado de custódia fora do fluxo ativo; não equivale a exclusão nem determina vigência |

`ARCHIVED` é dimensão de custódia e pode coexistir com `HISTORICAL`, `SUPERSEDED` ou `OBSOLETE`. `LEGACY` é dimensão de proveniência/compatibilidade, não estado terminal. Nenhuma classificação retroativa será aplicada sem sucessor ou justificativa demonstrável, registro institucional, preservação e análise de consumidores.

## 23. Decisão D04 — RFCs

**Decisão proposta:** RFC-002 permanece `PROPOSED / DRAFT`. RFC proposta não é norma aprovada, e Sprint aberta não é aprovação implícita. Nenhuma implementação, contrato, persistência, piloto ou alteração de SDK decorrente da RFC-002 é autorizada.

## 24. Decisão D05 — Releases, backups, checkpoints e pacotes

**Decisão proposta:** `INSTITUTIONAL HOLD`. Antes de movimento, remoção ou deduplicação são obrigatórios inventário completo, hash, proveniência, classificação, owner, política de retenção, consumidores, integridade do pacote e rollback comprovado. Cópias internas continuam como evidência mesmo quando duplicam fonte corrente.

## 25. Decisão D06 — Logs

**Decisão proposta:** `INSTITUTIONAL HOLD`. Antes de qualquer ação, identificar produtores e consumidores, referências por código/scripts/testes/documentação, função operacional e probatória, sensibilidade, dados pessoais/segredos, autoridade, owner, retenção, rotação, acesso, integridade e descarte. Logs idênticos por hash não podem ser eliminados sem verificar contexto e cadeia de custódia.

## 26. Decisão D07 — Fonte de verdade documental

**Decisão proposta:** uma fonte de verdade por matéria, registrada em índice. Classes obrigatórias:

- `CANONICAL AUTHORITY`: documento aprovado que governa matéria e versão;
- `HISTORICAL COPY`: cópia autêntica de um corte passado;
- `RELEASE EVIDENCE`: conteúdo preservado dentro de release/pacote para reprodução;
- `GENERATED COPY`: saída reproduzível de ferramenta, subordinada à entrada e ao método;
- `WORKING COPY`: material corrente sem autoridade até aprovação.

Documentos institucionais no diretório pai governam matérias de plataforma quando assim instituídos; documentos em `CORE/docs` governam matérias do CORE conforme índice e autoridade; relatórios provam fatos e não criam norma; pacotes preservam evidência; cópias auxiliares não prevalecem. Caminho sozinho nunca decide canonicidade.

## 27. Decisão D08 — SPR-018

**Decisão proposta:** SPR-018 permanece aberta administrativamente. Planejamento e documentação são permitidos. `IMPLEMENTAÇÃO TÉCNICA = BLOQUEADA` até RFC-002 aprovada, D0–D4 aplicáveis satisfeitos, especificação técnica própria aprovada, auditoria prévia sem bloqueios, autorizações de fonte/ambiente, testes e rollback aprovados e autorização expressa por pacote. Esta decisão não aprova D5.

## 28. Política de autoridade documental

Autoridade deriva de matéria, instrumento, aprovação, versão e registro; não de pasta, filename, status Git ou texto autorreferente. Todo documento novo deve declarar owner, autoridade aprovadora, status, escopo, baseline afetada, predecessores e sucessores. Índices administram identidade e navegação, mas não alteram silenciosamente mérito histórico.

## 29. Política de proveniência

Preservar conteúdo original, autoria, data, caminho histórico, hashes quando aplicáveis, cadeia de incorporação e ato que alterou status ou localização. Correções históricas usam errata ou reconciliação externa. Transformações e cópias devem registrar fonte, ferramenta/método, data, responsável e relação com o original.

## 30. Política de maturidade

Maturidade deve ser independente de autoridade e vigência. Estados mínimos: `WORKING`, `PROPOSED/DRAFT`, `REVIEWED`, `APPROVED/ACCEPTED`, e `CLOSED` quando aplicável. `OFFICIAL` identifica autoridade; `ACTIVE` identifica vigência; `BLOCKED` identifica impedimento; nenhum deles substitui maturidade. Aprovação humana deve ser registrável e não inferida.

## 31. Política de documentos históricos

Documento histórico é preservado como prova do seu corte, mesmo que contenha nomenclatura ou status hoje reconciliado. Não deve ser atualizado para parecer contemporâneo. Relações predecessor/sucessor e erratas são externas e bidirecionais. Exclusão física exige política específica e nunca decorre apenas de `SUPERSEDED`, `OBSOLETE` ou `ARCHIVED`.

## 32. Política para releases, backups e checkpoints

Aplica-se HOLD até existir inventário verificável, hashes, manifesto, proveniência, classificação de retenção, owner, consumidores e restauração ensaiada. Conteúdo interno de pacote não será movido nem reescrito. A fonte corrente pode ser canônica sem invalidar a cópia probatória.

## 33. Política para logs

Logs devem ter produtor, consumidores, finalidade, classificação de acesso, retenção, rotação, integridade, owner e regra de descarte documentados. Logs probatórios exigem cadeia de custódia; logs com segredos ou dados pessoais exigem controle de acesso e tratamento específico. Movimento futuro requer atualização validada de todos os consumidores.

## 34. Política EOL futura

Recomenda-se operação independente para criar `.gitattributes`, após inventário EOL e aprovação. Política candidata:

```gitattributes
* text=auto
*.md text eol=lf
*.py text eol=lf
*.json text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
*.ps1 text eol=crlf
*.cmd text eol=crlf
*.bat text eol=crlf
*.zip binary
*.whl binary
*.db binary
*.docx binary
```

A lista final depende de inventário de formatos e consumidores. `core.autocrlf=true` foi observado, `.gitattributes` está ausente e o corpus apresenta EOL misto. Não normalizar agora. Consolidação documental, normalização EOL e reorganização física devem ocorrer em changesets e revisões separados, cada um com fotografia anterior, diff limitado, validação e rollback.

## 35. Classificação de artefatos locais/gerados

| Artefato | Classificação proposta | Fundamentação e ação futura |
|---|---|---|
| `.vscode/extensions.json` | KEEP / LOCAL | recomenda extensões úteis; decidir política de compartilhamento da equipe antes de versionar |
| `.vscode/tasks.json` | REVIEW / LOCAL | tarefas úteis, mas dependem de PowerShell, Python e script local; validar portabilidade e segurança |
| `inventory.txt` | ACCIDENTAL / REVIEW | contém código Python completo com mojibake sob extensão `.txt`; comparar com implementação canônica antes de decidir retenção |
| `src/cko.egg-info/*` | GENERATED / CANDIDATE_IGNORE | metadados típicos de build/editable install; confirmar que não sustentam release antes de ignorar/remover em etapa própria |
| `src/main.py.txt` | ACCIDENTAL / REVIEW | cópia mínima de entry point sob extensão `.txt`; comparar com entry point canônico e consumidores |

Nenhum item é excluído, movido, ignorado ou versionado por esta decisão.

## 36. Gates para regeneração da OPS-004

A nova versão deve cumprir todos os gates:

1. corpus e regras de inclusão/exclusão fechados;
2. um registro estrutural por artefato, sem linhas implícitas ou omitidas;
3. identificador único, caminho de origem e destino proposto;
4. ação, autoridade, vigência, proveniência e maturidade explícitas;
5. bloqueador, hash aplicável, consumidor e dependências;
6. D01–D08 relacionada e justificativa;
7. rollback e validações por registro/lote;
8. schema versionado em formato processável, acompanhado de visão humana;
9. validação automática de unicidade, caminhos, enums e referências;
10. totais calculados da mesma fonte, com invariantes `total = migrar + permanecer + outras ações explicitadas` e categorias multidimensionais não somadas como se fossem exclusivas;
11. relatório de reprodução com ferramenta, versão, comando, entradas e hash do inventário;
12. revisão humana de autoridade, retenção, colisões e bloqueios.

Até a satisfação e aceitação desses gates, OPS-004 não pode fundamentar OPS-005.

## 37. Gates para futura consolidação Git

Antes de qualquer staging ou commit futuro:

- ratificação humana registrada da GOV-008;
- AUD-001 incorporada ou vinculada com proveniência verificável;
- lista fechada dos documentos do Ciclo II autorizados para consolidação;
- revisão individual de conteúdo, encoding, links e metadados;
- status proposto reconciliado nos índices, sem reescrever históricos;
- separação dos artefatos locais/gerados;
- confirmação de que RFC-002 segue draft e SPR-018 bloqueada;
- ausência de migração física e de normalização EOL no changeset;
- diff e `git status` revisados por humano;
- plano de commit e mensagem aprovados.

Esta GOV-008 não autoriza `git add`, `commit` ou `push`.

## 38. Gates para OPS-005

OPS-005 permanece bloqueada até: GOV-008 ratificada; D01–D08 ratificadas; GOV-007 efetivamente vigente; OPS-004 regenerada e aceita; inventário/hashes/consumidores completos; políticas de retenção e logs aprovadas; colisões resolvidas; branch, manifesto e rollback ensaiados; piloto delimitado; ausência de fechamento simultâneo de release/baseline; autorização executiva própria; auditoria e homologação independentes definidas. Satisfazer esses gates permite avaliar a abertura de OPS-005, não a executa automaticamente.

## 39. Riscos

| Risco | Consequência |
|---|---|
| Ratificação por autodeclaração | falsa autoridade institucional |
| Confundir baseline com estado posterior | história e reprodução comprometidas |
| Tratar RFC/Sprint como autorização de código | implementação sem gate arquitetural |
| Executar OPS-004 incompleta | perda, colisões e links quebrados |
| Reescrever ADR-006 | proveniência histórica falseada |
| Deduplicar pacotes | evidência de release destruída |
| Misturar EOL, conteúdo e movimento | diff não auditável |
| Versionar artefatos locais/gerados sem decisão | ruído, dependência acidental e falsa canonicidade |
| Ausência local da AUD-001 | cadeia probatória incompleta |

## 40. Controles

Controles obrigatórios: ratificação humana; baseline read-only; índices canônicos; reconciliação externa de históricos; inventário estruturado; hash e manifesto; revisão por matéria; least privilege; HOLD para pacotes/logs; mudanças em changesets separados; `git status` antes/depois; nenhum staging automático; gates de parada; auditoria e homologação independentes.

## 41. Matriz de rastreabilidade

| Achado/decisão | Fonte principal | Controle/resultado nesta GOV-008 |
|---|---|---|
| Baseline imutável | GOV-001, AUD-001 informada, refs Git | seções 8 e 20 |
| Arquitetura do Ciclo II | ARCH-002 | seções 10 e 18 |
| Ondas e gates | GOV-002 | seções 11, 27 e 38 |
| Identidade ADR-006 | GOV-003, ADR INDEX, ADR-006 | seções 12 e 13 |
| RFC em draft | RFC-002 | seções 14 e 23 |
| Sprint condicionada | SPR-018 | seções 15 e 27 |
| Natureza da GOV-005 | GOV-005 e GOV-006 | seção 16 |
| Organização normativa | GOV-007 | seções 18, 22 e 26 |
| Inventário não reproduzível | OPS-004 e inspeção estrutural | seções 19 e 36 |
| Duplicatas/pacotes | OPS-004 | seções 21, 24 e 32 |
| Logs | OPS-004 | seções 25 e 33 |
| EOL misto | AUD-001 informada e configuração Git | seção 34 |
| Artefatos não institucionais | working tree e conteúdo observado | seção 35 |

## 42. Decisões finais

Ratificadas humanamente em 10/08/2026:

1. preservar integralmente `CKO-BASELINE-2026.07`;
2. ratificar ARCH-002, GOV-002, GOV-003, GOV-006 e GOV-007 como `OFFICIAL / ACTIVE`;
3. reconhecer GOV-005 como `OFFICIAL EVIDENCE / HISTORICAL SNAPSHOT`;
4. reconhecer ADR-006 como `ACCEPTED / ACTIVE`, preservando a identidade interna histórica;
5. manter RFC-002 `PROPOSED / DRAFT`;
6. manter SPR-018 aberta administrativamente e tecnicamente bloqueada;
7. classificar OPS-004 como plano analítico não executável;
8. adotar D01–D08 e os gates definidos neste documento;
9. manter OPS-005 bloqueada;
10. não modificar qualquer documento existente antes da ratificação.

## 43. Próximas etapas

1. obter e vincular o artefato íntegro da AUD-001, com proveniência verificável;
2. atualizar índices e metadados mínimos em changeset documental próprio, preservando históricos;
3. regenerar OPS-004 em formato estruturalmente verificável;
4. deliberar separadamente sobre RFC-002;
5. classificar os artefatos locais/gerados em revisão própria;
6. planejar política `.gitattributes` em changeset independente;
7. somente então avaliar os gates para consolidação Git e, posteriormente, a abertura de OPS-005.

Nenhuma próxima etapa é executada por esta GOV-008.

## 44. Critério de encerramento

O critério institucional de ratificação foi satisfeito em 10/08/2026 por decisão humana explícita do responsável institucional pelo projeto CKO. D01–D08 estão ratificadas; os documentos relacionados possuem os status definidos nesta GOV-008; a baseline permanece protegida; RFC-002 não foi aprovada; SPR-018 permanece tecnicamente bloqueada; OPS-004 não autoriza migração; OPS-005 permanece bloqueada; e consolidação Git não foi autorizada automaticamente.

O processo de reconciliação institucional GOV-008 está encerrado de forma controlada com status `RATIFICADA / OFFICIAL / ACTIVE`. Permanecem abertas, como trabalhos futuros independentes e não autorizados por este encerramento, a incorporação probatória da AUD-001, a regeneração da OPS-004, as atualizações de índices/metadados, a decisão sobre RFC-002, a política EOL, o tratamento de artefatos locais e qualquer eventual consolidação Git.

---

**Declaração de não execução:** esta emissão não moveu, renomeou, excluiu ou alterou documentos preexistentes; não modificou código, runtime, banco, SDK, API, testes, baseline, tag ou release; não executou OPS-005, RFC-002 ou SPR-018; não normalizou EOL; e não realizou staging, commit, push, pull, reset ou clean.
