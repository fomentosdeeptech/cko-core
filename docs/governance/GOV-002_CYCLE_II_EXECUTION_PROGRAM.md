# CKO — GOV-002 — Cycle II Execution Program

**Processo:** CKO — GOV-002 — Cycle II Execution Program
**Status:** oficial
**Natureza:** programa de governança e ordenação executiva; exclusivamente documental
**Ciclo:** Ciclo Arquitetural II
**Data:** 02/08/2026
**Arquitetura de origem:** CKO-ARCH-002 — Ecosystem Evolution Architecture
**Baseline protegida:** CKO-BASELINE-2026.07
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos

> Este documento transforma as ondas II.0–II.7 do CKO-ARCH-002 em um
> programa oficial de execução governada. Ele ordena decisões, evidências e
> autorizações, mas não executa nenhuma onda por si só.

## 1. Objetivo

Instituir o programa executivo do Ciclo Arquitetural II, estabelecendo:

- a ordem oficial e os gates das ondas II.0–II.7;
- critérios de entrada e saída;
- entregáveis e dependências;
- riscos e pontos de decisão;
- paralelismo permitido e precedências obrigatórias;
- a sequência recomendada de futuros ADRs, RFCs e Sprints;
- o roadmap executivo para condução, homologação e escala do ciclo.

O resultado esperado do programa é converter a direção arquitetural do
CKO-ARCH-002 em uma sequência auditável de decisões e entregas, preservando a
baseline e impedindo autorização implícita de implementação.

## 2. Limites e não autorização

Este processo:

- **não cria código**;
- **não cria ADRs**;
- **não cria RFCs**;
- **não cria, abre, nomeia ou reserva Sprints**;
- **não altera a CKO-BASELINE-2026.07**;
- **não modifica o SDK `cko` 1.0.0**;
- **não altera os 646 exports da API pública**;
- **não autoriza escrita**, migração, reorganização ou exclusão em CID,
  Biblioteca Digital, Google Drive, Downloads ou `02_Knowledge`;
- **não promove** Adapter, Provider, aplicação, dataset, corpus ou componente ao
  Core;
- **não descontinua** fluxo, componente ou legado;
- **não substitui** os gates de mudança, segurança, dados, homologação ou
  arquitetura já vigentes.

As referências a ADR, RFC e Sprint neste documento representam apenas
**sequência futura recomendada e critérios de precedência**. Cada artefato
dependerá de abertura e aprovação próprias. A aprovação do GOV-002 autoriza o
programa de governança; não autoriza automaticamente nenhuma implementação.

## 3. Autoridade e precedência

A interpretação e a execução futura do programa obedecem à seguinte ordem:

1. CKO-GOV-001 e CKO-BASELINE-2026.07;
2. CKO-ARCH-001;
3. contratos e evidências homologados do CKO CORE SDK 1.0.0;
4. CKO-ARCH-002;
5. este GOV-002;
6. ADRs futuros aprovados, quando uma decisão material for necessária;
7. RFCs futuros aprovados;
8. Sprints futuras autorizadas e suas evidências de homologação.

Em caso de conflito, o artefato de menor precedência DEVE ser corrigido ou
suspenso. O GOV-002 operacionaliza o CKO-ARCH-002 e NÃO DEVE reinterpretá-lo,
ampliá-lo ou produzir mudança arquitetural implícita.

## 4. Modelo operacional do programa

### 4.1 Estados de uma onda

Cada onda percorre os seguintes estados formais:

1. **Não iniciada:** os critérios de entrada ainda não foram submetidos.
2. **Elegível:** as precedências foram satisfeitas e as evidências de entrada
   estão disponíveis.
3. **Autorizada:** o ponto de decisão aprovou escopo, responsáveis e controles.
4. **Em execução:** apenas os trabalhos expressamente autorizados estão ativos.
5. **Em gate de saída:** entregáveis e evidências estão sob revisão.
6. **Concluída:** todos os critérios de saída foram homologados.
7. **Suspensa:** risco, desvio ou dependência impede continuidade segura.

Nenhuma onda pode passar de **elegível** para **em execução** sem autorização
registrada. Trabalho preparatório não equivale a início da onda.

### 4.2 Gates globais

Todo gate de entrada ou saída DEVE confirmar, no mínimo:

- aderência ao CKO-ARCH-002 e à baseline protegida;
- escopo, owner e autoridades aprovadoras identificados;
- superfícies e dados afetados explicitamente delimitados;
- inexistência de mudança implícita no SDK ou na API pública;
- proveniência e evidências auditáveis;
- segurança, confidencialidade e menor privilégio;
- estratégia de teste proporcional ao trabalho futuro;
- reversibilidade, desligamento e rollback quando aplicáveis;
- riscos abertos com tratamento e responsável;
- decisões pendentes encaminhadas ao instrumento correto.

### 4.3 Regra de escopo para paralelismo

Os gates podem ser homologados por **trilha delimitada** — CID, Biblioteca
Digital, Google Drive, Downloads, `02_Knowledge` ou fundação transversal — quando
este documento permitir paralelismo. A homologação de uma trilha não declara as
demais concluídas e não permite que uma dependência transversal incompleta seja
contornada.

## 5. Ordem oficial das ondas

| Ordem | Onda | Resultado executivo | Precedência obrigatória |
|---:|---|---|---|
| 1 | II.0 — Preservação | programa protegido por autoridades, escopo e controles confirmados | aprovação do GOV-002 |
| 2 | II.1 — Inventário federado | fontes e restrições caracterizadas em leitura | conclusão de II.0 |
| 3 | II.2 — Contratos e mapeamentos | capacidades mapeadas aos contratos existentes e gaps explícitos | saída aplicável de II.1 |
| 4 | II.3 — Adapters e Providers | composições externas especificadas, seguras e reversíveis | saída aplicável de II.2 e decisões materiais aprovadas |
| 5 | II.4 — Pilotos supervisionados | jornadas read-only/dry-run avaliadas por aplicação | saída aplicável de II.3 e autorização específica de piloto |
| 6 | II.5 — Federação de conhecimento | catálogo e consulta autorizada validados com proveniência | pilotos e controles aplicáveis de II.4 homologados |
| 7 | II.6 — Consolidação de evidências | decisão fundamentada sobre externalidade, evolução ou encerramento | conclusão global de II.4 e II.5 |
| 8 | II.7 — Escala governada | expansão controlada somente de padrões homologados | decisão favorável em II.6 e autorização específica de escala |

A numeração define a ordem de maturidade e de fechamento. Sobreposição controlada
entre trilhas é permitida somente nos termos da seção 8; ela não altera essa
ordem oficial.

## 6. Plano executivo por onda

### 6.1 Onda II.0 — Preservação

**Finalidade.** Fixar o perímetro institucional do ciclo antes de qualquer
trabalho de descoberta ou especificação.

**Critérios de entrada**

- CKO-ARCH-002 oficial e disponível como fonte de direção;
- GOV-002 submetido à governança;
- baseline, SDK e API pública identificados como superfícies protegidas;
- patrocinador, coordenação do programa e autoridades de domínio identificáveis.

**Entregáveis**

- matriz de autoridade e responsabilidade por superfície;
- registro das referências protegidas e critérios de compatibilidade;
- mapa inicial de escopo, exclusões e fontes;
- registro inicial de riscos, dependências e decisões pendentes;
- modelo de evidência e gate aplicável às ondas seguintes.

**Dependências.** CKO-GOV-001, CKO-ARCH-001, CKO-ARCH-002, baseline publicada e
catálogo homologado da API pública.

**Critérios de saída**

- autoridades e owners confirmados;
- escopo e superfícies protegidas homologados;
- inexistência de autorização implícita registrada;
- controles de acesso, evidência e escalonamento definidos;
- decisão **D0** aprovada.

**Riscos dominantes.** Escopo ambíguo, autoridade ausente, uso de evidência
desatualizada e interpretação do programa como autorização técnica.

**Ponto de decisão D0 — Autorizar o início do ciclo.** Aprovar, devolver para
ajuste ou suspender. Sem D0 aprovado, nenhuma outra onda pode iniciar.

### 6.2 Onda II.1 — Inventário federado

**Finalidade.** Caracterizar, em modo somente leitura, CID, Biblioteca Digital,
Google Drive, Downloads e `02_Knowledge`, preservando autoridades e originais.

**Critérios de entrada**

- II.0 concluída;
- fonte, owner, finalidade, perímetro e classificação de acesso definidos para
  cada trilha;
- método de inventário reproduzível e não destrutivo;
- autorização de leitura e política de tratamento de dados aprovadas.

**Entregáveis**

- inventários reproduzíveis por superfície;
- mapa de capacidades, formatos, identidades e sobreposições;
- registro de restrições, confidencialidade, direitos e qualidade conhecida;
- mapa de owners, stewards e fontes de autoridade;
- baseline observacional e relatório de lacunas de evidência.

**Dependências.** Matriz de autoridade de II.0, acesso mínimo aprovado,
disponibilidade das fontes e critérios de proveniência.

**Critérios de saída**

- cobertura e limitações do inventário explicitadas;
- evidências vinculadas à fonte e reproduzíveis;
- nenhuma movimentação, escrita, certificação ou canonicidade inferida;
- fontes, restrições e sobreposições validadas pelos respectivos owners;
- decisão **D1** registrada por trilha e consolidada no fechamento da onda.

**Riscos dominantes.** Exposição indevida, inventário incompleto, identificação
instável, confusão entre pasta e ontologia e oficialização indevida de conteúdo.

**Ponto de decisão D1 — Aceitar a base de evidência.** Aceitar a trilha para
mapeamento, exigir complementação ou excluir a fonte do ciclo.

### 6.3 Onda II.2 — Contratos e mapeamentos

**Finalidade.** Mapear capacidades observadas aos contratos públicos existentes,
sem alterar contratos nem transformar gap em decisão automática.

**Critérios de entrada**

- D1 aprovado para a trilha;
- inventário e limitações disponíveis;
- catálogo dos 646 exports e contratos homologados fixado como referência;
- vocabulário de capacidades e regras de rastreabilidade definidos.

**Entregáveis**

- matriz capacidade–contrato–consumidor;
- mapeamentos de identidade, metadados e proveniência;
- análise de compatibilidade e sobreposição;
- catálogo de gaps, ambiguidades e decisões não tomadas;
- classificação preliminar: consumir, envolver, compor, manter externo ou
  encaminhar para decisão futura.

**Dependências.** Saída aceita de II.1, contratos públicos vigentes e owners dos
domínios envolvidos.

**Critérios de saída**

- todos os mapeamentos rastreiam a evidência de origem;
- gaps estão explícitos e não foram resolvidos por alteração implícita de API;
- direção de dependências permanece compatível com a baseline;
- decisões materiais estão identificadas para eventual ADR futuro;
- decisão **D2** aprovada.

**Riscos dominantes.** Equivalência semântica falsa, acoplamento ao produto,
duplicação de contrato e uso de detalhe interno como API.

**Ponto de decisão D2 — Selecionar o tratamento da capacidade.** Aprovar
composição externa, manter o legado sem integração, solicitar decisão
arquitetural futura ou encerrar o item.

### 6.4 Onda II.3 — Adapters e Providers

**Finalidade.** Especificar composições externas substituíveis para os itens
selecionados em D2. A onda somente poderá produzir implementação quando RFC e
Sprint futuras, próprias e aprovadas, assim o autorizarem.

**Critérios de entrada**

- D2 aprovado para o item;
- fronteiras de Core, Adapter, Provider e Aplicação definidas;
- ADR aplicável aprovado quando houver decisão material não coberta pela
  baseline;
- requisitos de segurança, proveniência, teste, observabilidade e rollback
  disponíveis.

**Entregáveis**

- especificações de portas de composição sem mudança da API pública;
- perfis de Adapter e Provider, capacidades, limites e modos de falha;
- estratégia de configuração, credenciais e menor privilégio;
- plano de testes contratuais, fixtures, dry-run e falha parcial;
- plano de desligamento, rollback e preservação do legado;
- proposta de RFC futura quando necessária.

**Dependências.** II.2, decisões arquiteturais aplicáveis e autoridades técnicas,
de segurança e de dados.

**Critérios de saída**

- composição externa demonstrada no nível de especificação;
- tecnologia, credenciais e regras exclusivas permanecem fora do Core;
- proveniência, segurança, testes e rollback aprovados;
- RFC futura aplicável aprovada antes de qualquer implementação;
- decisão **D3** aprovada.

**Riscos dominantes.** Vazamento de infraestrutura para o domínio, credenciais
indevidas, provider que inventa capacidade, escrita acidental e adapter não
substituível.

**Ponto de decisão D3 — Autorizar preparação de piloto.** Aprovar apenas a
preparação controlada, devolver a especificação ou manter a capacidade externa
sem piloto.

### 6.5 Onda II.4 — Pilotos supervisionados

**Finalidade.** Avaliar jornadas delimitadas em modo read-only ou dry-run,
preservando o fluxo legado e exigindo decisão humana por domínio.

**Critérios de entrada**

- D3 aprovado;
- RFC futura aplicável aprovada;
- Sprint futura específica autorizada;
- ambiente, fixtures, acessos, métricas, limites e responsáveis definidos;
- plano de observação, interrupção e rollback ensaiável;
- autorização independente para qualquer exceção ao modo read-only.

**Entregáveis**

- evidências de execução controlada por jornada;
- métricas de qualidade, compatibilidade, cobertura, custo e reutilização;
- comparação com o legado e registro de divergências;
- trilha de proveniência ponta a ponta;
- relatório de incidentes, exceções, feedback humano e rollback;
- recomendação de avançar, repetir, corrigir ou encerrar.

**Dependências.** II.3, ambientes isolados, disponibilidade dos owners e controles
de segurança e dados.

**Critérios de saída**

- critérios de aceite medidos e evidenciados;
- ausência de regressão não aceita ou mutação não autorizada;
- fluxo legado e originais preservados;
- homologação humana do domínio registrada;
- decisão **D4** aprovada para cada piloto.

**Riscos dominantes.** Piloto virar produção, amostra não representativa,
mutação de fonte real, métrica sem baseline e dependência operacional prematura.

**Ponto de decisão D4 — Homologar o piloto.** Homologar para o próximo gate,
repetir com condições, rejeitar ou encerrar com preservação das evidências.

### 6.6 Onda II.5 — Federação de conhecimento

**Finalidade.** Validar catálogo e consulta autorizada de datasets e corpora,
mantendo conteúdo, autoridade e identidade em suas fontes sempre que possível.

**Critérios de entrada**

- D4 aprovado para os pilotos que sustentam a trilha;
- owners, stewards, finalidade, acesso e classificação confirmados;
- identidade, proveniência e distinção entre localizado, curado e oficial
  definidas;
- ADR e RFC futuros aplicáveis aprovados;
- nenhum conteúdo sem direitos ou autoridade suficiente incluído para publicação.

**Entregáveis**

- catálogo federado delimitado e auditável;
- cadeia de proveniência entre fonte, projeção, transformação e consulta;
- matriz de autorização e regras de acesso;
- critérios de inclusão, exclusão, atualização e correção;
- evidência de consulta federada e resolução explícita de conflitos;
- relatório de cobertura, confiança e restrições.

**Dependências.** Pilotos aplicáveis de II.4, governança institucional,
Biblioteca Digital, stewards, autoridades de segurança e fontes participantes.

**Critérios de saída**

- governança e acesso aprovados;
- vínculo com originais e autoridade preservado;
- ausência de centralização física ou canonicidade não autorizada;
- conflitos, lacunas e confiança permanecem explícitos;
- decisão **D5** aprovada.

**Riscos dominantes.** Centralização prematura, perda de contexto, inferência de
canonicidade, vazamento entre domínios e projeção tratada como fonte.

**Ponto de decisão D5 — Homologar a federação delimitada.** Aprovar a evidência
para consolidação, restringir o escopo, exigir correção ou retirar a trilha.

### 6.7 Onda II.6 — Consolidação de evidências

**Finalidade.** Consolidar resultados do ciclo e decidir, com evidência, o que
permanece externo, o que requer evolução formal e o que deve ser encerrado.

**Critérios de entrada**

- todos os pilotos de II.4 encerrados ou formalmente retirados;
- todas as trilhas de II.5 encerradas ou formalmente retiradas;
- métricas, incidentes, divergências, custos e feedback disponíveis;
- pendências e exceções classificadas.

**Entregáveis**

- relatório consolidado de reutilização e compatibilidade;
- matriz de resultados por capacidade e consumidor;
- catálogo de gaps comprovados e riscos residuais;
- recomendação fundamentada: manter externo, ampliar externamente, propor ADR,
  propor RFC adicional, reavaliar ou encerrar;
- registro de lições e condições para eventual escala.

**Dependências.** Fechamento global de II.4 e II.5 e integridade das evidências.

**Critérios de saída**

- conclusões rastreáveis a métricas e evidências homologadas;
- reutilização transversal demonstrada, não presumida;
- ausência de promoção automática ao Core;
- riscos residuais e custo de escala aceitos ou tratados;
- decisão **D6** aprovada.

**Riscos dominantes.** Viés de confirmação, promoção por expectativa, seleção de
métricas favoráveis e descarte de evidência negativa.

**Ponto de decisão D6 — Definir o destino de cada capacidade.** Manter externa,
ampliar sob governança, encaminhar decisão formal, reavaliar ou encerrar. Uma
proposta de promoção ao Core exige processo próprio e não é aprovada por D6.

### 6.8 Onda II.7 — Escala governada

**Finalidade.** Expandir apenas padrões homologados, reversíveis e compatíveis,
com controle contínuo de conformidade.

**Critérios de entrada**

- D6 favorável para o padrão e o escopo propostos;
- ADRs e RFCs futuros aplicáveis aprovados;
- Sprints futuras de escala autorizadas;
- capacidade operacional, suporte, observabilidade, segurança e rollback
  comprovados;
- limites, indicadores e condição de interrupção definidos.

**Entregáveis**

- plano de expansão incremental por domínio e consumidor;
- evidências de conformidade contínua;
- indicadores operacionais, de reutilização e de risco;
- registro de exceções, incidentes, correções e reversões;
- revisão periódica de arquitetura e governança;
- recomendação de continuidade, contenção ou encerramento do ciclo.

**Dependências.** II.6, autorizações específicas e capacidade operacional
homologada.

**Critérios de saída**

- expansão dentro dos limites aprovados;
- indicadores e auditoria disponíveis durante todo o período;
- compatibilidade da baseline e dos 646 exports confirmada;
- exceções resolvidas ou aceitas formalmente;
- decisão **D7** registrada e encerramento executivo do Ciclo II aprovado.

**Riscos dominantes.** Escala antes de maturidade, erosão de fronteiras,
dependência irreversível, crescimento de privilégios e exceções permanentes.

**Ponto de decisão D7 — Continuar, conter ou encerrar.** Autorizar nova expansão
delimitada, congelar o alcance, reverter uma trilha ou encerrar o Ciclo II.

## 7. Dependências transversais

| Dependência | Ondas afetadas | Regra de controle |
|---|---|---|
| Baseline e catálogo da API pública | II.0–II.7 | referência imutável durante o programa; mudança exige processo independente |
| Autoridade e ownership | II.0–II.7 | nenhuma trilha sem owner e aprovador identificados |
| Segurança e menor privilégio | II.1–II.7 | acesso concedido por finalidade e revogável |
| Proveniência | II.1–II.7 | evidência acompanha observação, transformação, decisão e publicação |
| Identidade entre fontes | II.2–II.7 | conflitos permanecem explícitos até decisão formal |
| Testes e ambientes isolados | II.3–II.7 | nenhuma validação em acervo permanente sem autorização específica |
| Legado e rollback | II.3–II.7 | substituição não ocorre antes de equivalência e homologação |
| Governança de datasets e corpora | II.1, II.4–II.7 | catálogo técnico não transfere autoridade institucional |
| Disponibilidade de stewards e validadores | II.1, II.4–II.7 | decisão sem validação humana aplicável não atravessa gate |
| ADR/RFC/Sprint futuros | conforme a seção 9 | cada instrumento deve estar aprovado antes da atividade que governa |

## 8. Paralelismo e precedência

### 8.1 Ondas e trilhas que podem operar em paralelo

| Combinação | Paralelismo permitido | Condição |
|---|---|---|
| II.1 por superfície | total entre CID, Biblioteca, Drive, Downloads e `02_Knowledge` | II.0 concluída e acessos independentes aprovados |
| II.1 e II.2 | sobreposição progressiva por trilha | D1 da trilha aprovado; fechamento global de II.2 aguarda II.1 global |
| II.2 e II.3 | sobreposição progressiva por item | D2 do item e decisões materiais aplicáveis aprovados |
| II.3 por Adapter/Provider | paralelismo entre composições independentes | contratos compartilhados estabilizados e owners definidos |
| II.4 por aplicação | paralelismo entre pilotos isolados | ambientes, fontes e autoridades não compartilharem risco não controlado |
| II.4 e II.5 | sobreposição limitada | somente a trilha federada sustentada por D4 aprovado; outros pilotos podem continuar |
| II.5 por domínio autorizado | paralelismo entre catálogos/consultas delimitados | identidade, acesso e proveniência transversais compatíveis |
| II.7 por padrão homologado | expansão incremental paralela | D6 favorável e capacidade de contenção independente por trilha |

### 8.2 Conclusões prévias obrigatórias

- II.0 DEVE terminar antes de qualquer inventário.
- Uma trilha de II.1 DEVE obter D1 antes de entrar em II.2.
- Um item de II.2 DEVE obter D2 antes de entrar em II.3.
- Uma composição de II.3 DEVE obter D3, RFC aplicável e autorização futura antes
  de qualquer piloto em II.4.
- Uma trilha de II.5 exige D4 dos pilotos que a sustentam.
- II.6 não pode iniciar seu fechamento enquanto houver piloto ou federação em
  execução sem encerramento ou retirada formal.
- II.7 não pode iniciar para um padrão sem D6 favorável e autorizações próprias.

Dependências compartilhadas impedem paralelismo quando sua falha puder contaminar
mais de uma trilha. Nesses casos, a coordenação do programa DEVE serializar o
trabalho ou estabelecer isolamento comprovado.

## 9. Sequência recomendada de ADRs, RFCs e futuras Sprints

### 9.1 Regra de precedência dos instrumentos

```text
evidência da onda
    -> decisão material pendente?
       -> sim: ADR futuro aprovado
       -> não: baseline vigente permanece suficiente
    -> RFC futura aprovada para a mudança delimitada
    -> Sprint futura autorizada para executar parte da RFC
    -> homologação e evidência retornam ao gate da onda
```

Um ADR decide **por que e qual direção material** adotar. Uma RFC especifica
**como uma mudança delimitada deverá funcionar**. Uma Sprint executa **uma parte
autorizada e verificável**. Nenhum instrumento substitui o anterior e nenhum
documento deve ser criado apenas para cumprir formalidade.

### 9.2 Sequência recomendada de futuros ADRs

ADRs somente serão propostos quando a baseline não resolver uma decisão material.
Se necessários, a ordem recomendada é:

1. autoridade, ownership e fronteira do catálogo federado;
2. identidade entre fontes e política de reconciliação de duplicidades;
3. autorização e isolamento entre domínios de confidencialidade;
4. escrita ou sincronização bidirecional com fontes externas;
5. persistência ou índice canônico, apenas se a federação provar necessidade;
6. retenção, exclusão e tratamento de dados em datasets, corpora e proveniência;
7. promoção de capacidade comprovadamente transversal ao Core;
8. descontinuação de legado após equivalência e reversibilidade comprovadas.

Os itens 4–8 não são pré-requisitos universais: devem permanecer inexistentes
enquanto a necessidade não for comprovada. Em especial, decisão sobre promoção
ou descontinuação somente pode decorrer das evidências de II.6.

### 9.3 Sequência recomendada de futuras RFCs

Sem criar ou numerar RFCs neste processo, a sequência temática recomendada é:

1. protocolo de inventário federado e evidência read-only, se automação for
   necessária;
2. mapeamentos e perfis contratuais por capacidade;
3. composição externa de Adapters e Providers por superfície;
4. jornada e controles de cada piloto supervisionado;
5. catálogo federado, autorização de consulta e proveniência ponta a ponta;
6. observabilidade, conformidade e expansão governada;
7. transição, promoção ou descontinuação, somente após decisão formal aplicável.

Cada RFC futura DEVE ter escopo único, contratos consumidos, superfícies
protegidas, segurança, compatibilidade, testes, evidências, rollback e gate de
homologação. RFCs independentes podem avançar em paralelo quando não
compartilharem decisão, contrato ou risco bloqueante.

### 9.4 Sequência recomendada de futuras Sprints

Sem criar, nomear, numerar ou reservar Sprints, recomenda-se que a execução
futura siga lotes pequenos nesta ordem:

1. preparação de controles e evidências da onda autorizada;
2. inventário read-only por fonte;
3. mapeamento contratual por capacidade;
4. especificação e testes contratuais da composição externa;
5. Adapter/Provider externo em ambiente isolado, quando autorizado;
6. piloto read-only/dry-run por jornada;
7. federação delimitada de catálogo e consulta;
8. consolidação de métricas, incidentes e decisões;
9. expansão incremental de um padrão homologado;
10. endurecimento, conformidade contínua e encerramento.

Uma Sprint futura DEVE caber em uma onda e em uma RFC aprovada; não pode ocultar
decisão arquitetural, combinar escrita com descoberta inicial, alterar a API por
conveniência nem declarar uma onda concluída sem o respectivo gate.

### 9.5 Mapeamento entre ondas e instrumentos futuros

| Onda | ADR futuro | RFC futura | Sprint futura |
|---|---|---|---|
| II.0 | normalmente não aplicável | normalmente não aplicável | não aplicável até autorização posterior |
| II.1 | apenas se houver decisão de autoridade/dados não coberta | protocolo de inventário, se houver automação | inventários isolados por fonte |
| II.2 | identidade, fronteira ou contrato material, se necessário | mapeamentos e perfis contratuais | lotes de mapeamento e validação |
| II.3 | decisão material pendente antes da especificação | composição de Adapter/Provider | implementação externa e testes, se autorizados |
| II.4 | somente para exceção material não decidida | jornada e controles do piloto | um piloto delimitado por jornada |
| II.5 | autoridade, acesso, identidade ou persistência, se necessário | catálogo, consulta e proveniência | federação delimitada por domínio |
| II.6 | promoção/descontinuação apenas como recomendação posterior | avaliação ou transição após decisão | consolidação de evidências; nenhuma promoção automática |
| II.7 | decisões adicionais somente se a escala mudar arquitetura | expansão, operação e conformidade | incrementos reversíveis por padrão homologado |

## 10. Riscos do programa

| ID | Risco | Sinal de alerta | Resposta obrigatória | Gate principal |
|---|---|---|---|---|
| R1 | alteração implícita da baseline/API | novo contrato, export ou comportamento não autorizado | suspender trilha e encaminhar ao processo formal | todos |
| R2 | programa tratado como autorização de código | trabalho técnico sem RFC/Sprint aplicável | interromper e registrar desvio | D0–D3 |
| R3 | autoridade institucional perdida | fonte técnica decide canonicidade | devolver decisão ao owner/steward | D1, D5 |
| R4 | acesso ou exposição indevida | privilégio excessivo ou dado fora do escopo | revogar acesso, conter e avaliar incidente | D1–D7 |
| R5 | centralização prematura | cópia física sem necessidade comprovada | voltar à referência/federação | D4, D5 |
| R6 | equivalência semântica falsa | mapeamento sem validação do domínio | rejeitar mapeamento e preservar gap | D2 |
| R7 | piloto torna-se produção | dependência operacional sem homologação | conter, desligar e restaurar fluxo legado | D4 |
| R8 | proveniência incompleta | resultado não rastreável à fonte/atividade | impedir homologação | D1–D7 |
| R9 | promoção por expectativa | proposta sem mais de um consumidor e evidência | manter externo e coletar evidência | D6 |
| R10 | paralelismo contamina trilhas | recurso, dado ou contrato compartilhado instável | serializar ou isolar antes de continuar | D1–D5 |
| R11 | legado sem rollback | substituição antes de equivalência | bloquear avanço e recompor reversibilidade | D3–D7 |
| R12 | escala excede capacidade de governança | exceções e incidentes crescentes | conter alcance ou reverter trilha | D7 |

Risco crítico sem resposta aceita suspende a trilha. Risco que afete baseline,
segurança, autoridade institucional ou integridade de dados suspende também as
trilhas dependentes até decisão formal.

## 11. Pontos de decisão e autoridades

| Decisão | Pergunta executiva | Evidência mínima | Resultado possível |
|---|---|---|---|
| D0 | O ciclo pode iniciar sob controles suficientes? | matriz de autoridade, escopo e proteções | autorizar, ajustar ou suspender |
| D1 | O inventário é confiável e autorizado? | cobertura, limitações, proveniência e validação do owner | aceitar, complementar ou excluir |
| D2 | Como tratar cada capacidade? | matriz contratual, compatibilidade e gaps | compor, manter, decidir formalmente ou encerrar |
| D3 | A composição está pronta para preparação de piloto? | especificação, segurança, testes e rollback | avançar, corrigir ou não pilotar |
| D4 | O piloto foi satisfatório e seguro? | métricas, comparação, incidentes e homologação humana | homologar, repetir ou rejeitar |
| D5 | A federação delimitada preserva acesso e autoridade? | catálogo, proveniência, autorização e conflitos | homologar, restringir, corrigir ou retirar |
| D6 | Qual é o destino baseado em evidência? | consolidação de reutilização, custos, gaps e riscos | manter, ampliar, propor decisão, reavaliar ou encerrar |
| D7 | A escala deve continuar? | conformidade, indicadores, incidentes e capacidade de rollback | continuar, conter, reverter ou encerrar |

A autoridade final de cada decisão cabe à governança competente, com participação
dos owners técnicos e institucionais afetados. Segurança, dados, Biblioteca e
stewards mantêm poder de bloqueio dentro de suas competências. A coordenação do
programa consolida evidências, mas não substitui essas autoridades.

## 12. Roadmap executivo do Ciclo II

O roadmap é orientado por gates, não por datas. Datas, capacidade, equipes e
Sprints somente serão definidas em autorizações futuras.

| Horizonte executivo | Ondas | Objetivo de gestão | Marco de saída |
|---|---|---|---|
| H0 — Instituir e proteger | II.0 | confirmar autoridade, perímetro e controles | D0 aprovado |
| H1 — Conhecer e mapear | II.1–II.2 | produzir evidência federada e compatibilidade contratual | D1/D2 consolidados |
| H2 — Especificar e provar | II.3–II.4 | preparar composições externas e validar pilotos supervisionados | D3/D4 consolidados |
| H3 — Federar conhecimento | II.5 | validar catálogo, acesso e proveniência sem centralização obrigatória | D5 aprovado |
| H4 — Decidir com evidência | II.6 | decidir externalidade, evolução ou encerramento | D6 aprovado |
| H5 — Escalar e encerrar | II.7 | expandir padrões homologados e revisar continuamente | D7 e encerramento do ciclo |

### 12.1 Caminho crítico

```text
GOV-002 aprovado
  -> II.0 / D0
  -> II.1 / D1
  -> II.2 / D2
  -> II.3 / D3
  -> II.4 / D4
  -> II.5 / D5
  -> II.6 / D6
  -> II.7 / D7
  -> encerramento executivo do Ciclo II
```

### 12.2 Indicadores executivos mínimos

O acompanhamento futuro DEVE reportar por onda e por trilha:

- estado, owner, gate atual e decisão pendente;
- entregáveis previstos, aceitos e rejeitados;
- cobertura e limitações das evidências;
- riscos críticos, incidentes e exceções;
- aderência à baseline, SDK e API pública;
- percentual de operações read-only/dry-run quando aplicável;
- proveniência completa e validações humanas pendentes;
- reutilização por consumidor, divergência do legado e capacidade de rollback;
- decisões de continuar, conter, reverter ou encerrar.

Percentuais isolados não autorizam avanço. A conclusão depende da aceitação
qualitativa e formal dos critérios de saída.

## 13. Critérios de conclusão do programa

O Ciclo II somente poderá ser declarado concluído quando:

- todas as ondas estiverem concluídas ou formalmente encerradas sem execução;
- D0–D7 estiverem registrados com autoridade e evidência;
- riscos críticos estiverem encerrados, aceitos ou transferidos formalmente;
- exceções e trilhas retiradas estiverem documentadas;
- legado, originais, autoridade e proveniência estiverem preservados;
- compatibilidade com a CKO-BASELINE-2026.07, SDK 1.0.0 e 646 exports estiver
  confirmada;
- qualquer evolução material tiver seguido ADR, RFC e Sprint próprios quando
  aplicáveis;
- nenhuma promoção, escrita, centralização ou descontinuação tiver ocorrido por
  inferência deste documento;
- a governança tiver aprovado o relatório executivo de encerramento.

O encerramento pode recomendar novo ciclo, manutenção operacional ou nenhuma
ação adicional. Não cria automaticamente qualquer desses trabalhos.

## 14. Justificativa do programa

O CKO-ARCH-002 definiu a direção correta para evolução do ecossistema, mas seu
roadmap arquitetural deliberadamente não definiu execução. O GOV-002 preenche
essa lacuna sem invadir arquitetura ou implementação: converte cada onda em um
conjunto verificável de entradas, entregáveis, saídas, riscos e decisões.

A estrutura adotada é necessária porque:

1. **protege a baseline:** nenhum avanço depende de alteração implícita do Core;
2. **faz evidência preceder decisão:** inventário e mapeamento antecedem desenho,
   piloto, federação e escala;
3. **preserva autoridade:** owners e stewards participam dos gates aplicáveis;
4. **permite paralelismo seguro:** trilhas independentes avançam sem eliminar
   precedências;
5. **separa instrumentos:** ADR decide, RFC especifica e Sprint executa;
6. **mantém reversibilidade:** pilotos e escala exigem isolamento, legado e
   rollback;
7. **impede promoção prematura:** somente II.6 pode produzir evidência para uma
   proposta futura, nunca uma promoção automática;
8. **torna o ciclo governável:** D0–D7 oferecem marcos executivos claros para
   continuar, corrigir, conter, reverter ou encerrar.

## 15. Declaração final

Fica instituído o CKO — GOV-002 — Cycle II Execution Program como programa oficial
de governança das ondas II.0–II.7 do CKO-ARCH-002.

Sua vigência preserva integralmente a CKO-BASELINE-2026.07, o CKO CORE SDK 1.0.0
e os 646 exports públicos. O programa não cria código, ADR, RFC ou Sprint; não
altera baseline, SDK ou API; e não autoriza implementação, escrita, promoção,
migração ou descontinuação.

Toda execução futura dependerá dos gates e instrumentos próprios definidos neste
documento e nas autoridades de maior precedência.

## Referências

- [CKO-ARCH-002 — Ecosystem Evolution Architecture](../arquitetura/CKO-ARCH-002_ECOSYSTEM_EVOLUTION_ARCHITECTURE.md)
- [CKO-GOV-001 — Baseline Arquitetural 1.0](../../../docs/governance/CKO-GOV-001_BASELINE_ARQUITETURAL_1.0.md)
- [CKO-ARCH-001 — Arquitetura Canônica](../../../docs/arquitetura/CKO-ARCH-001_ARQUITETURA_CANONICA.md)
- [Índice Mestre da Governança](../../../docs/governance/GOVERNANCE_INDEX.md)
- [Índice de ADRs](../adr/INDEX.md)
