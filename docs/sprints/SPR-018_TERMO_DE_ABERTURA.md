# CKO — SPR-018 — Termo de Abertura

**Processo:** CKO — SPR-018 — Termo de Abertura
**Status:** autorizada, com execução técnica condicionada aos critérios de entrada
**Natureza:** autorização formal de Sprint; documento exclusivamente administrativo e normativo
**Ciclo:** Ciclo Arquitetural II
**Data de abertura:** 03/08/2026
**Onda de execução:** II.5 — Federação de conhecimento
**Gate de destino:** D5 — Homologar a federação delimitada
**Decisão de origem:** ADR-006 — Federated Catalog Authority, aceito
**Especificação de origem:** RFC-002 — Federated Catalog Protocol, sujeita à aprovação como critério de entrada
**Arquitetura de origem:** CKO-ARCH-002 — Ecosystem Evolution Architecture
**Programa:** GOV-002 — Cycle II Execution Program
**Reconciliação de governança:** GOV-003 — ADR Governance Reconciliation
**Baseline protegida:** CKO-BASELINE-2026.07
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos
**Código autorizado por este documento:** nenhum
**Commit autorizado por este documento:** nenhum

> Este Termo cria e autoriza formalmente a SPR-018, primeira Sprint do Ciclo
> Arquitetural II. Sua aprovação autoriza somente a condução governada da Sprint
> e o início de sua etapa de especificação. Não implementa código, não modifica
> baseline, SDK ou API pública, não cria contratos, testes ou implementação e
> não autoriza commit. A execução técnica de cada pacote depende de especificação
> própria, aprovada e auditável, além dos gates aplicáveis.

## Controle normativo e efeito da autorização

As palavras **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **PODE** e **RECOMENDADO**
são normativas.

A autorização desta Sprint NÃO se confunde com autorização irrestrita de código.
Ela estabelece o envelope de governança dentro do qual pacotes futuros poderão
ser especificados, implementados, testados, homologados e auditados. Nenhum
pacote passa à implementação apenas por constar deste Termo.

Cada pacote da SPR-018 DEVE cumprir, nesta ordem, cinco estágios com evidência
própria:

1. especificação;
2. implementação;
3. testes;
4. homologação;
5. auditoria.

É proibido iniciar implementação sem especificação própria previamente aprovada.
É proibido considerar a homologação ou a auditoria de um pacote como implícita na
homologação de outro. Descumprimento material suspende o pacote e todas as
dependências afetadas.

## 1. Contexto

A CKO-BASELINE-2026.07 consolidou o CKO CORE SDK 1.0.0 e sua API pública de 646
exports raiz, únicos e resolvidos. A CKO-ARCH-002 instituiu para o Ciclo
Arquitetural II uma evolução incremental baseada em federação governada,
composição externa, Provenance by Design, Authority Stays at the Source e
preservação do Core.

O GOV-002 converteu essa direção em ondas, precedências e gates. O GOV-003
reconciliou o registro canônico de decisões e estabeleceu que *Federated Catalog
Authority* é o ADR-006 aceito, ainda que seu conteúdo histórico conserve a
designação anterior. O ADR-006 decidiu autoridade, ownership e fronteira do
Catálogo Federado Institucional. A RFC-002 traduziu essa decisão em protocolo
lógico, critérios de implementação futura, testes, homologação e D5.

A SPR-018 é a primeira Sprint derivada integralmente dessa cadeia. Ela se insere
na Onda II.5 e somente poderá produzir execução técnica depois de satisfeitas as
precedências documentais e executivas previstas neste Termo.

## 2. Motivação

A federação de conhecimento exige transformar a decisão arquitetural e o
protocolo lógico em incrementos pequenos, externos ao Core, reversíveis e
auditáveis. Sem uma autorização formal, haveria risco de implementar diretamente
uma RFC ainda não aprovada, confundir contrato lógico do FCP com contrato público
do SDK, antecipar escolhas tecnológicas ou tratar evidência de Sprint como
homologação automática do Gate D5.

Este Termo existe para fixar limites, precedências, responsabilidades de
evidência e condições de parada antes de qualquer execução.

## 3. Objetivo geral

Conduzir, sob autorização formal e controle por pacotes, a implementação externa,
delimitada e reversível do Federated Catalog Protocol especificado pela RFC-002,
produzindo evidências suficientes para submissão ao Gate D5, sem alterar a
CKO-BASELINE-2026.07, o SDK `cko` 1.0.0 ou seus 646 exports públicos.

## 4. Objetivos específicos

1. converter requisitos aprovados da RFC-002 em especificações próprias por
   pacote, sem criar contratos por meio deste Termo;
2. manter fonte, conteúdo, identidade, ownership e autoridade institucional em
   seus perímetros de origem;
3. implementar somente componentes externos ao Core e apenas após autorização
   do respectivo pacote;
4. demonstrar descoberta, registro, publicação de metadados, consulta autorizada
   e Provenance nos limites aprovados;
5. aplicar menor privilégio, negativa segura, minimização e ausência de ampliação
   de acesso;
6. demonstrar isolamento de falhas, desligamento e rollback por fonte, Adapter,
   Provider, domínio e Aplicação;
7. verificar mecanicamente a preservação do SDK 1.0.0 e dos 646 exports;
8. produzir matriz requisito–teste–evidência e dossiê auditável para D5;
9. registrar conflitos, lacunas, restrições e decisões diferidas sem resolvê-los
   por conveniência técnica;
10. encerrar cada pacote com especificação, implementação, testes, homologação e
    auditoria individualmente identificáveis.

## 5. Escopo

Integram o escopo autorizado da SPR-018, sempre condicionados às especificações
próprias dos pacotes:

- planejamento, especificação técnica e auditoria pré-implementação dos pacotes;
- implementação do FCP em camada externa ao CKO Core e em ambiente isolado;
- perfis de fonte, mapeamentos e projeções estritamente aprovados para a trilha;
- descoberta e leitura por padrão, sem mutação da fonte;
- registros, identidades, estados e ciclo de vida do protocolo aprovado;
- publicação de metadados distinta de oficialização e de publicação de conteúdo;
- consulta com autorização, menor privilégio, filtragem prévia e negativa segura;
- Provenance ponta a ponta, conflitos explícitos e histórico append-only;
- negociação de versão e capacidades, paginação, falha parcial e idempotência;
- observabilidade sem exposição de conteúdo sensível;
- testes com fixtures isoladas e dados sintéticos ou formalmente autorizados;
- homologação humana por owner, steward e autoridades competentes;
- regressão integral do SDK e verificação mecânica dos 646 exports;
- elaboração e auditoria do dossiê de evidências a ser submetido ao Gate D5.

O escopo efetivo de execução será a interseção entre este Termo, a RFC-002
aprovada, a especificação aprovada do pacote, as autorizações de fonte e os gates
aplicáveis. Em divergência, prevalece o limite mais restritivo.

## 6. Exclusões de escopo

A SPR-018 NÃO autoriza:

- alteração, reabertura, substituição ou promoção da CKO-BASELINE-2026.07;
- modificação de módulo, namespace, dependência, comportamento, versão, build ou
  empacotamento do SDK `cko` 1.0.0;
- criação, remoção, renomeação, depreciação ou reinterpretação de qualquer dos
  646 exports públicos;
- criação ou alteração de contrato público do SDK;
- promoção de capacidade ao Core;
- escolha implícita de transporte, serialização, banco, índice, cache, grafo,
  IAM, topologia ou persistência canônica;
- repositório central, data lake ou centralização física obrigatória;
- escrita, correção, movimentação, exclusão ou sincronização em fonte real;
- cópia ou publicação de conteúdo original por força desta autorização;
- ampliação de acesso, bypass de política ou inferência de existência protegida;
- declaração automática de equivalência, confiança, canonicidade ou oficialidade;
- substituição de validação humana, owner, steward ou autoridade institucional;
- descontinuação de legado, migração irreversível ou operação em produção;
- expansão para a Onda II.6 ou II.7;
- aprovação automática dos gates D0–D5;
- qualquer implementação sem especificação própria aprovada;
- commits por força deste Termo de Abertura.

Tema fora de escopo DEVE ser mantido externo, registrado como decisão diferida
ou encaminhado ao instrumento de governança apropriado.

## 7. Dependências

| Dependência | Condição exigida | Efeito se ausente |
|---|---|---|
| CKO-BASELINE-2026.07 | tag e evidências de baseline disponíveis e íntegras | bloqueia toda execução |
| CKO-ARCH-002 | oficial e vigente | bloqueia enquadramento arquitetural |
| GOV-002 | oficial e vigente | bloqueia ondas, precedências e gates |
| GOV-003 e índice canônico | ADR-006 identificado como decisão aceita | bloqueia rastreabilidade normativa |
| ADR-006 | aceito e aplicável ao perímetro | bloqueia especificação derivada |
| RFC-002 | aprovada em revisão controlada | bloqueia implementação |
| D0–D4 aplicáveis | decisões e evidências aprovadas para a trilha | bloqueia entrada na Onda II.5 |
| Owners, stewards e autoridades | identificados, disponíveis e com poderes registrados | bloqueia fonte ou domínio afetado |
| Autorizações de acesso | finalidade, classificação e menor privilégio aprovados | bloqueia acesso à fonte |
| Perfis e mapeamentos | aprovados por classe e fonte | bloqueia pacote dependente |
| Ambiente e fixtures | isolados, reproduzíveis e autorizados | bloqueia testes e homologação |
| Estratégias de segurança e rollback | aprovadas e ensaiáveis | bloqueia implementação |
| Catálogo da API pública | referência mecânica fixada em 646 exports | bloqueia gate de compatibilidade |

Dependência incompleta não pode ser contornada por paralelismo. Pacotes
independentes PODEM avançar em especificação, mas não compartilharão estado,
contrato, dado ou risco ainda não homologado.

## 8. Artefatos de origem

1. tag `CKO-BASELINE-2026.07` e evidências oficiais da baseline;
2. `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md`;
3. `CKO_CORE_V1_PUBLIC_API_CATALOG.md`;
4. `SPR017_HOMOLOGATION_REPORT.md`;
5. `docs/arquitetura/CKO-ARCH-002_ECOSYSTEM_EVOLUTION_ARCHITECTURE.md`;
6. `docs/governance/GOV-002_CYCLE_II_EXECUTION_PROGRAM.md`;
7. `docs/governance/GOV-003_ADR_GOVERNANCE_RECONCILIATION.md`;
8. `docs/adr/INDEX.md`;
9. `docs/adr/ADR-006_FEDERATED_CATALOG_AUTHORITY.md`;
10. `docs/rfc/RFC-002_FEDERATED_CATALOG_PROTOCOL.md`.

Documentos exploratórios anteriores que usem o número SPR-018 não prevalecem
sobre este Termo e não integram sua cadeia autorizadora, salvo incorporação
expressa por especificação futura aprovada.

## 9. Artefatos derivados

A Sprint DEVE produzir, sem que este Termo antecipe seu conteúdo:

- especificação técnica própria de cada pacote;
- auditoria pré-implementação de cada especificação;
- plano e relatório de implementação de cada pacote;
- plano, matriz e relatório de testes de cada pacote;
- relatório de homologação de cada pacote;
- relatório de auditoria pós-implementação de cada pacote;
- matriz consolidada requisito–teste–evidência;
- inventário de componentes e superfícies alteradas;
- relatório de compatibilidade da baseline, SDK e API pública;
- registro de riscos, incidentes, exceções, restrições e decisões diferidas;
- plano e evidência de desligamento e rollback;
- relatório de homologação consolidada da SPR-018;
- relatório de auditoria final da SPR-018;
- dossiê de submissão ao Gate D5;
- termo de encerramento da SPR-018.

Cada artefato derivado DEVE possuir identificador, versão, status, autor ou owner,
data, entradas, evidências e decisão registrada.

## 10. Critérios de entrada

### 10.1 Entrada administrativa da Sprint

- este Termo aprovado pela autoridade competente;
- escopo, exclusões, riscos, premissas e restrições reconhecidos;
- owner da Sprint, arquitetura, governança, segurança, dados e domínios afetados
  identificados;
- baseline, SDK e API pública fixados como superfícies protegidas;
- ausência de autorização de commit decorrente deste documento reconhecida.

### 10.2 Entrada em especificação de pacote

- pacote enquadrado no planejamento preliminar e na Onda II.5;
- requisito rastreado à RFC-002 e ao ADR-006;
- fontes, dados, autoridades e dependências delimitados;
- critérios de aceite, teste, homologação, auditoria e rollback propostos;
- decisões materiais pendentes identificadas e encaminhadas.

### 10.3 Entrada em implementação de pacote

- RFC-002 formalmente aprovada;
- D0–D4 aplicáveis aprovados para a trilha;
- especificação própria do pacote aprovada;
- auditoria pré-implementação concluída sem bloqueio aberto;
- matriz de rastreabilidade e plano de testes aprovados;
- ambiente isolado, fixtures e acessos autorizados;
- owners, stewards, segurança e autoridades competentes de acordo;
- estratégia de desligamento e rollback ensaiável;
- baseline de 646 exports verificada antes da mudança;
- autorização explícita de implementação registrada para o pacote.

## 11. Critérios de saída

A Sprint estará tecnicamente apta à saída quando:

- todos os pacotes admitidos tiverem completado especificação, implementação,
  testes, homologação e auditoria, ou tiverem retirada formal e justificada;
- todos os requisitos implementados estiverem rastreados à RFC-002 aprovada;
- nenhuma decisão material estiver oculta em implementação;
- catálogo, autorização, Provenance, identidade, autoridade e conflitos estiverem
  demonstrados no perímetro aprovado;
- falha parcial, suspensão, retirada, desligamento e rollback tiverem evidência;
- fontes, originais e legado permanecerem preservados;
- regressão integral estiver aprovada;
- o SDK permanecer em 1.0.0 e a API permanecer com exatamente 646 exports raiz,
  únicos e resolvidos;
- não houver alteração da CKO-BASELINE-2026.07;
- riscos e incidentes estiverem encerrados, aceitos ou escalados com owner;
- homologação consolidada e auditoria final estiverem concluídas;
- o dossiê D5 estiver completo e formalmente submetido.

A saída técnica da Sprint não equivale à aprovação de D5.

## 12. Critérios de aceite

| Dimensão | Critério obrigatório |
|---|---|
| Governança | cadeia Baseline → ARCH-002 → GOV-002/GOV-003 → ADR-006 → RFC-002 → pacote integralmente rastreável |
| Especificação | cada pacote possui especificação própria aprovada antes da implementação |
| Arquitetura | Core neutro; Aplicação como composition root; Adapter e Provider externos e substituíveis |
| Autoridade | fonte, owner, steward e autoridades preservados; nenhum operador adquire canonicidade |
| Segurança | menor privilégio, interseção de políticas, filtragem prévia e negativa segura comprovados |
| Dados | nenhuma mutação de fonte ou uso de dado não autorizado |
| Provenance | cadeia ponta a ponta auditável; lacunas e conflitos explícitos |
| Resiliência | falha parcial, timeout, retry, paginação, expiração, revogação e isolamento testados conforme especificação |
| Compatibilidade | baseline inalterada, SDK 1.0.0 inalterado e 646/646/646 exports confirmados |
| Reversibilidade | desligamento e rollback por perímetro demonstrados sem afetar original ou legado |
| Qualidade | testes previstos aprovados, sem falha bloqueante ou regressão não aceita |
| Homologação | decisão humana registrada por pacote e no consolidado da Sprint |
| Auditoria | auditoria independente por pacote e auditoria final sem não conformidade material aberta |
| D5 | dossiê completo; decisão permanece reservada às autoridades do gate |

Não conformidade material em qualquer dimensão impede aceite do pacote afetado.

## 13. Riscos

| ID | Risco | Indicador | Tratamento obrigatório |
|---|---|---|---|
| R-018-01 | Termo interpretado como autorização direta de código | implementação sem gate próprio | suspender e exigir especificação/autorização |
| R-018-02 | RFC-002 implementada antes da aprovação | status ainda proposto | bloquear implementação |
| R-018-03 | contrato lógico confundido com API do SDK | novo export, porta ou símbolo público | rejeitar mudança e restaurar compatibilidade |
| R-018-04 | centralização prematura | cópia física ou índice tratado como fonte | retornar à referência federada |
| R-018-05 | ampliação de acesso | consulta revela ativo ou metadado não autorizados | negar com segurança e suspender perímetro |
| R-018-06 | perda de autoridade institucional | decisão automática de canonicidade | devolver decisão ao owner/steward |
| R-018-07 | Provenance incompleta | resultado não rastreável | impedir homologação |
| R-018-08 | falha distribuída contamina fontes | ausência de isolamento | desligar perímetro e executar rollback |
| R-018-09 | pacote combina decisões ou ondas | escopo não isolável | dividir ou retirar pacote |
| R-018-10 | piloto ou protótipo torna-se produção | dependência operacional não homologada | conter, desligar e preservar legado |
| R-018-11 | quebra da baseline/API | versão, comportamento ou contagem divergente | interromper, reverter e auditar |
| R-018-12 | D5 tratado como automático | fechamento sem decisão das autoridades | reabrir gate de governança |
| R-018-13 | dado sensível aparece em log/evidência | conteúdo desnecessário registrado | conter, sanear, notificar e revisar controles |
| R-018-14 | divergência entre fonte e projeção é ocultada | cache/projeção promovido a verdade | invalidar projeção e explicitar conflito |

Risco crítico relativo a baseline, segurança, privacidade, autoridade ou
integridade de dados suspende imediatamente o pacote e suas dependências.

## 14. Premissas

- a tag CKO-BASELINE-2026.07 representa a baseline oficial vigente;
- o SDK protegido permanece `cko` 1.0.0;
- a superfície pública protegida permanece em 646 exports raiz, únicos e
  resolvidos;
- CKO-ARCH-002, GOV-002 e GOV-003 permanecem oficiais durante a Sprint;
- ADR-006 permanece aceito e canônico conforme o índice e o GOV-003;
- a RFC-002 será submetida à aprovação antes de qualquer implementação;
- D0–D4 aplicáveis e autorizações de fonte existirão antes da execução de II.5;
- ambientes isolados e fixtures autorizadas estarão disponíveis;
- owners, stewards e autoridades participarão dos gates;
- qualquer mudança de premissa material provocará reavaliação formal de escopo.

Premissa não comprovada no gate correspondente passa a ser dependência ou risco;
não pode ser tratada como fato por conveniência.

## 15. Restrições

1. Uma Sprint deve caber em uma onda e em uma RFC aprovada; a SPR-018 permanece
   limitada à Onda II.5 e à RFC-002.
2. Nenhuma implementação ocorrerá sem especificação própria.
3. Cada pacote possuirá especificação, implementação, testes, homologação e
   auditoria próprios.
4. Nenhuma alteração poderá romper a compatibilidade da baseline.
5. O SDK continuará na versão 1.0.0.
6. A API pública continuará com exatamente 646 exports raiz, únicos e resolvidos.
7. Nenhum contrato público será criado ou alterado por este Termo ou por
   conveniência de implementação.
8. Código e integrações permanecerão externos ao Core, salvo decisão formal
   posterior que está fora desta Sprint.
9. Leitura será o padrão; escrita em fonte real está fora do escopo.
10. Segredos, credenciais e conteúdo sensível não integrarão código, fixture,
    log ou evidência.
11. Trabalho paralelo só ocorrerá entre pacotes isolados por contrato, dado,
    risco e autoridade.
12. Nenhum commit é autorizado por este Termo; commits futuros exigirão
    autorização explícita e revisão de escopo.

## 16. Estratégia de implementação

A implementação futura seguirá progressão *specification-first*, por pacotes
pequenos e reversíveis:

1. congelar entrada, interfaces consumidas e evidências da baseline;
2. aprovar a especificação própria e a auditoria pré-implementação do pacote;
3. implementar verticalmente o menor incremento verificável, externo ao Core;
4. usar configuração explícita, injeção de dependências e isolamento por fonte,
   Adapter, Provider, domínio e Aplicação;
5. operar read-only por padrão e falhar fechado quando autorização for
   indeterminada;
6. registrar Provenance sem reproduzir conteúdo sensível;
7. manter chaves de desligamento e caminho de retorno ao legado;
8. impedir dependência do Core em infraestrutura, produto ou fonte;
9. interromper o pacote ao surgir decisão não coberta pelo ADR-006/RFC-002;
10. somente integrar pacotes após testes, homologação e auditoria individuais.

Tecnologia, schema físico, transporte, IAM, persistência e topologia somente
serão escolhidos em especificação própria quando já autorizados por instrumento
competente. Este Termo não realiza nem antecipa essas escolhas.

## 17. Estratégia de testes

Cada pacote terá plano e matriz requisito–teste–evidência próprios. A estratégia
mínima compreenderá:

- testes unitários determinísticos do comportamento especificado;
- testes de contrato lógico e perfis por classe/fonte;
- identidades, estados, transições, versionamento e extensões desconhecidas;
- segurança, menor privilégio, filtragem antes de agregação e negativa segura;
- prevenção de inferência por paginação, contagem, tempo, erro e métricas;
- Provenance, integridade, conflitos, correção append-only e rastreabilidade;
- falha parcial, timeout, retry, backoff, quota, idempotência e concorrência;
- isolamento e desligamento por fonte, Adapter, Provider, domínio e Aplicação;
- testes de integração somente com fixtures isoladas e dados autorizados;
- jornadas read-only/dry-run e ensaio de rollback;
- caracterização do legado e golden files de mapeamento;
- regressão integral canônica do SDK;
- verificação mecânica de 646 entradas, 646 nomes únicos e 646 símbolos
  resolvidos na API raiz;
- comparação do inventário de superfícies antes e depois de cada pacote.

Nenhum teste está autorizado por este Termo a escrever em Drive, Downloads,
`02_Knowledge`, banco, Dataset, Corpus, acervo ou fonte real.

## 18. Estratégia de homologação

A homologação ocorrerá em três níveis:

1. **por pacote:** owner técnico, owner/steward de domínio e autoridades de
   segurança/dados aplicáveis avaliam critérios e evidências;
2. **da Sprint:** arquitetura e governança reconciliam pacotes, regressão,
   compatibilidade, riscos, exceções e rollback;
3. **do Gate D5:** governança, owners, stewards e autoridades afetadas decidem
   homologar, restringir, exigir correção ou retirar a federação delimitada.

Homologação será explícita, humana, registrada e baseada em evidência. Aprovação
de teste não substitui homologação; homologação da Sprint não substitui D5; D5
não promove capacidade ao Core.

## 19. Estratégia de rollback

O rollback será definido e ensaiado por pacote, com os seguintes controles
mínimos:

- desligamento independente por fonte, Adapter, Provider, domínio e Aplicação;
- remoção da composição externa sem alteração do Core;
- invalidação segura de projeções e caches sem afetar a fonte;
- revogação de credenciais, acessos e publicação de metadados;
- restauração do fluxo legado e preservação dos originais;
- retenção controlada das evidências de auditoria e decisão;
- confirmação posterior de baseline, SDK 1.0.0 e 646 exports;
- registro de causa, alcance, responsável, horário, evidência e resultado.

Rollback não apagará história nem converterá projeção em fonte. Se uma alteração
atingir superfície protegida, a resposta obrigatória será interromper, reverter,
revalidar a baseline e submeter o incidente à governança.

## 20. Critérios para encerramento da Sprint

A SPR-018 será encerrada somente quando:

- o inventário final de pacotes estiver congelado;
- cada pacote estiver completo nos cinco estágios ou formalmente retirado;
- entregáveis, versões, owners e decisões estiverem registrados;
- critérios de saída e aceite estiverem reconciliados;
- não houver não conformidade material aberta;
- baseline, SDK e API pública estiverem formalmente confirmados como inalterados;
- riscos residuais e decisões diferidas possuírem owner e destino;
- relatório de homologação e auditoria final estiverem aprovados;
- dossiê D5 tiver sido submetido e sua decisão registrada;
- resultado da Sprint estiver classificado como homologado, homologado com
  restrições, devolvido para correção ou retirado;
- Termo de Encerramento tiver sido aprovado.

Uma decisão D5 de correção ou retirada não autoriza maquiar o resultado. A Sprint
pode ser encerrada administrativamente com resultado não homologado desde que
evidências, causas, restrições e destino estejam preservados. Somente decisão D5
favorável, eventualmente com restrições expressas, habilita a transição prevista
no GOV-002.

## 21. Entregáveis previstos

| ID | Entregável | Gate principal |
|---|---|---|
| E-018-01 | Termo de Abertura oficial | abertura administrativa |
| E-018-02 | registro consolidado de dependências, riscos e autoridades | entrada |
| E-018-03 | conjunto de especificações próprias dos pacotes | pré-implementação |
| E-018-04 | auditorias pré-implementação | pré-implementação |
| E-018-05 | implementações externas delimitadas | execução condicionada |
| E-018-06 | suítes, matrizes e relatórios de testes | qualidade |
| E-018-07 | homologações e auditorias por pacote | aceite por pacote |
| E-018-08 | evidência de rollback e desligamento | reversibilidade |
| E-018-09 | relatório de compatibilidade 1.0.0/646/baseline | preservação |
| E-018-10 | matriz consolidada requisito–teste–evidência | homologação da Sprint |
| E-018-11 | relatório de homologação consolidada | saída técnica |
| E-018-12 | auditoria final independente | saída técnica |
| E-018-13 | dossiê de submissão ao D5 | Gate D5 |
| E-018-14 | Termo de Encerramento | encerramento administrativo |

O item E-018-05 não é produzido nem autorizado tecnicamente pela aprovação
isolada deste Termo; depende dos critérios de entrada e autorizações por pacote.

## 22. Relação com as ondas do GOV-002

A SPR-018 pertence exclusivamente à **Onda II.5 — Federação de conhecimento**.
Ela não executa nem declara concluídas outras ondas.

| Onda | Relação com a SPR-018 |
|---|---|
| II.0 — Preservação | fornece baseline, autoridades, escopo e controles; precedência obrigatória |
| II.1 — Inventário federado | fornece fontes, restrições, owners e evidência aceita em D1 |
| II.2 — Contratos e mapeamentos | fornece mapeamentos, gaps e decisão D2 sem alterar API |
| II.3 — Adapters e Providers | fornece composições externas especificadas e decisão D3 |
| II.4 — Pilotos supervisionados | fornece pilotos aplicáveis homologados em D4 |
| II.5 — Federação de conhecimento | onda de execução da SPR-018; produz evidência para D5 |
| II.6 — Consolidação de evidências | consumidora futura do resultado D5; não autorizada nesta Sprint |
| II.7 — Escala governada | fora de escopo; depende de decisões posteriores |

Se qualquer precedente aplicável estiver ausente, a SPR-018 permanece aberta em
estado administrativo ou em especificação, sem iniciar o pacote técnico afetado.

## 23. Relação com o Gate D5

O Gate D5 responde se a federação delimitada preserva acesso e autoridade. A
SPR-018 deve produzir, para essa decisão:

- catálogo delimitado e auditável;
- autorização aplicada em tempo de consulta;
- Provenance ponta a ponta;
- vínculo preservado com originais, identidades e autoridades;
- conflitos, lacunas, confiança, parcialidade e validade explícitos;
- separação entre publicação de metadados e oficialização;
- evidência de menor privilégio, negativa segura e revogação;
- evidência de ausência de centralização ou canonicidade não autorizada;
- aprovações e restrições de owners, stewards, governança e autoridades;
- confirmação de baseline, SDK 1.0.0 e 646 exports inalterados.

A SPR-018 prepara e submete o dossiê; não decide D5. A autoridade do gate pode
homologar, restringir, exigir correção ou retirar a trilha. Não conformidade
material impede homologação. D5 nunca promove capacidade ao Core.

## 24. Compatibilidade obrigatória

| Superfície protegida | Obrigação da SPR-018 | Evidência mínima |
|---|---|---|
| CKO-BASELINE-2026.07 | não alterar, reabrir, substituir ou promover elemento | diff de superfícies, tag de referência e auditoria final |
| SDK `cko` 1.0.0 | não modificar módulo, namespace, dependência, comportamento, versão, build ou empacotamento | metadata, build reproduzível e regressão canônica |
| API pública | preservar exatamente 646 exports raiz, únicos e resolvidos, sem mudança semântica | inventário mecânico 646/646/646 antes e depois |
| Core | permanecer neutro e sem dependência de Aplicação, Adapter, Provider ou fonte | análise de dependências e inventário de arquivos |
| Contratos homologados | consumir somente contratos vigentes, sem criação ou alteração implícita | matriz capacidade–contrato–consumidor |
| Legado e originais | preservar comportamento, identidade, autoridade e retorno | caracterização, golden files e ensaio de rollback |

Compatibilidade é condição de entrada, aceite, saída e encerramento. Divergência
em qualquer superfície protegida suspende o pacote, exige rollback e impede D5.

## 25. Justificativa de cada seção

| Seção | Justificativa |
|---|---|
| Controle normativo | delimita o efeito jurídico-operacional da abertura e impede autorização implícita de código |
| 1. Contexto | estabelece a cadeia de autoridade e o estado protegido do sistema |
| 2. Motivação | registra o problema de governança que justifica a Sprint |
| 3. Objetivo geral | define resultado único, perímetro e invariantes |
| 4. Objetivos específicos | converte o objetivo em resultados verificáveis |
| 5. Escopo | delimita o trabalho potencialmente autorizável por pacote |
| 6. Exclusões | impede expansão, decisões ocultas e impacto na baseline |
| 7. Dependências | transforma precedências do GOV-002 em bloqueios operacionais |
| 8. Artefatos de origem | assegura proveniência normativa e resolve precedência documental |
| 9. Artefatos derivados | fixa a cadeia mínima de evidências da Sprint |
| 10. Critérios de entrada | separa abertura, especificação e implementação |
| 11. Critérios de saída | define prontidão técnica sem usurpar D5 |
| 12. Critérios de aceite | torna qualidade, segurança e governança objetivamente verificáveis |
| 13. Riscos | antecipa falhas dominantes e respectivas respostas |
| 14. Premissas | explicita condições assumidas e impede que incerteza vire decisão |
| 15. Restrições | congela limites não negociáveis da autorização |
| 16. Estratégia de implementação | estabelece execução incremental, externa e reversível |
| 17. Estratégia de testes | define prova proporcional para protocolo, segurança e compatibilidade |
| 18. Estratégia de homologação | separa teste, aceite humano, Sprint e decisão D5 |
| 19. Estratégia de rollback | preserva legado, fontes e reversibilidade por perímetro |
| 20. Encerramento | evita encerramento sem evidência ou ocultação de resultado negativo |
| 21. Entregáveis | torna o resultado material inventariável e auditável |
| 22. Ondas do GOV-002 | fixa a Sprint em II.5 e preserva precedências D0–D4 |
| 23. Gate D5 | define o dossiê e mantém a decisão na autoridade competente |
| 24. Compatibilidade | protege baseline, SDK 1.0.0 e 646 exports em todos os gates |
| 26. RFC-002 | demonstra derivação técnica sem transformar a RFC em código implícito |
| 27. Pacotes | oferece planejamento inicial sem dispensar especificações próprias |
| 28. Declaração final | consolida a autorização e seus limites formais |

## 26. Relação entre a SPR-018 e a RFC-002

A RFC-002 é a especificação lógica de origem da SPR-018; a Sprint é o instrumento
de execução delimitada de parte verificável dessa RFC. A relação é de derivação,
não de substituição:

| RFC-002 | SPR-018 |
|---|---|
| define modelo lógico, entidades, estados, operações e invariantes | planeja incrementos externos que implementem somente o conteúdo aprovado |
| define contratos públicos do protocolo lógico | não os converte automaticamente em contratos do SDK |
| estabelece critérios futuros de implementação | transforma-os em gates por pacote |
| estabelece critérios de teste | exige matriz e evidência própria por pacote |
| estabelece critérios de homologação e D5 | prepara dossiê, sem aprovar o gate |
| não escolhe tecnologia, persistência, IAM ou topologia | somente poderá escolher o mínimo autorizado em especificação própria |
| não autoriza Sprint ou implementação | passa a ser executável apenas após aprovação e em conjunto com este Termo |

Todo requisito de pacote DEVE apontar para seção e versão aprovadas da RFC-002.
Lacuna, ambiguidade ou mudança semântica retorna à RFC, ADR ou governança; não
será resolvida silenciosamente em código. Se a RFC-002 não for aprovada, a
SPR-018 não entra em implementação.

## 27. Planejamento preliminar dos pacotes da Sprint

O planejamento abaixo é preliminar, não cria contrato nem autoriza implementação.
Cada pacote somente ingressa em execução após especificação própria, auditoria
prévia e autorização expressa.

| Pacote | Finalidade preliminar | Dependências principais | Evidência de saída |
|---|---|---|---|
| P-018-01 — Fundação externa do protocolo | materializar, fora do Core, modelo lógico, identidades, registros, estados, ciclo de vida e negociação aprovados | RFC-002 aprovada; D1–D3 aplicáveis; perfis aprovados | conformidade de modelo, identidade, transições e versão |
| P-018-02 — Autoridade, publicação e consulta | aplicar ownership, stewardship, admissão, publicação de metadados, autorização, consulta e negativa segura | P-018-01; matriz de autoridade; políticas aprovadas | autorização, separação de atos e ausência de ampliação de acesso |
| P-018-03 — Federação e resiliência | compor projeções aprovadas por Adapter/Provider externo com paginação, falha parcial, idempotência e isolamento | P-018-01/02; D3/D4; ambientes e fontes autorizados | federação delimitada read-only, parcialidade explícita e desligamento |
| P-018-04 — Provenance e conflitos | demonstrar cadeia ponta a ponta, correção append-only, lacunas, conflitos, validade, revogação e vínculo com originais | P-018-01/02/03; perfis e políticas aprovados | trace auditável e conflitos não ocultos |
| P-018-05 — Conformidade e dossiê D5 | executar regressão, rollback, homologação integrada, auditoria final e consolidar evidências | P-018-01 a 04 homologados e auditados | matriz requisito–teste–evidência, compatibilidade e dossiê D5 |

Para **cada** P-018-01 a P-018-05 são obrigatórios e separadamente
identificáveis:

1. especificação do pacote;
2. implementação do pacote;
3. testes do pacote;
4. homologação do pacote;
5. auditoria do pacote.

P-018-05 também terá implementação: implementação dos mecanismos executáveis de
conformidade, coleta reproduzível e empacotamento controlado das evidências
especificadas. A decisão humana de homologação e a auditoria permanecem separadas
desses mecanismos.

Os pacotes não representam cronograma fechado. Podem ser divididos, retirados ou
reordenados por decisão formal, desde que permaneçam na Onda II.5, dentro da
RFC-002 aprovada e sem relaxar precedências, compatibilidade ou os cinco estágios.

## 28. Declaração final de abertura

Fica formalmente criada e autorizada a **CKO — SPR-018**, primeira Sprint do
Ciclo Arquitetural II, para condução governada do escopo definido neste Termo.

Esta autorização permite iniciar planejamento e especificação. Nenhuma
implementação ocorrerá sem especificação própria, auditoria pré-implementação,
critérios de entrada satisfeitos e autorização expressa do pacote. Cada pacote
deverá possuir especificação, implementação, testes, homologação e auditoria.

A CKO-BASELINE-2026.07 permanece integralmente protegida. O CKO CORE SDK
permanece na versão 1.0.0. A API pública permanece com exatamente 646 exports
raiz, únicos e resolvidos. Nenhuma alteração poderá romper essa compatibilidade.

Este ato não cria código, contrato, teste, implementação ou commit. Qualquer
commit dependerá de autorização posterior e explícita. A Sprint produzirá
evidências para o Gate D5, cuja decisão permanece reservada à governança, owners,
stewards e autoridades competentes.
