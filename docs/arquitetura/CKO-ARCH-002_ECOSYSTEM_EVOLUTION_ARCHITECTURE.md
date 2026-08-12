# CKO-ARCH-002 — Ecosystem Evolution Architecture

**Processo:** CKO — ARCH-002 — Ecosystem Evolution Architecture
**Status:** oficial
**Natureza:** arquitetura complementar de evolução; exclusivamente documental
**Ciclo:** Ciclo Arquitetural II
**Data:** 02/08/2026
**Baseline protegida:** CKO-BASELINE-2026.07
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos
**Documento precedente:** CKO-ARCH-001 — Arquitetura Canônica da Plataforma CKO
**Evidência de origem:** DSC-001 — Ecosystem Discovery, concluído com **ALTO** potencial de reutilização

> Este documento complementa a CKO-ARCH-001 e não a substitui, corrige ou
> reinterpreta. Ele não constitui Sprint, RFC, ADR, especificação de implementação
> ou autorização para alterar código. Sua função exclusiva é definir a arquitetura
> de evolução do ecossistema no Ciclo Arquitetural II.

## Controle normativo

As palavras **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **PODE** e **RECOMENDADO**
são normativas. As expressões **Core**, **Adapter**, **Provider**, **Aplicação**,
**Dataset** e **Corpus Institucional** designam papéis arquiteturais, não novos
pacotes, produtos, repositórios ou contratos.

Esta arquitetura:

- preserva integralmente a CKO-BASELINE-2026.07;
- preserva o SDK 1.0.0 e seus 646 exports públicos;
- mantém vigentes todas as decisões homologadas pela CKO-ARCH-001;
- não promove qualquer ativo descoberto ao Core;
- não autoriza integração física, migração, movimentação ou classificação de dados;
- não abre, nomeia ou reserva Sprint;
- não cria RFC ou ADR;
- não autoriza descontinuação de legado.

Um item presente no roadmap representa somente direção e ordem arquitetural. Sua
execução futura dependerá dos instrumentos de governança aplicáveis.

## Fontes de autoridade

A interpretação deste documento obedece à seguinte ordem:

1. CKO-GOV-001 e CKO-BASELINE-2026.07;
2. CKO-ARCH-001;
3. contratos e evidências homologados do CKO CORE SDK 1.0.0;
4. CKO-ARCH-002;
5. decisões futuras formalmente aprovadas;
6. especificações e entregas futuras autorizadas.

O DSC-001 fornece evidência de reutilização e oportunidade; não possui autoridade
para alterar a baseline ou declarar ativos como canônicos.

---

## 1. Visão geral do Ciclo Arquitetural II

O Ciclo Arquitetural II transforma o conhecimento obtido no DSC-001 em uma
arquitetura de composição do ecossistema. Seu foco é conectar capacidades já
existentes, preservar suas autoridades de origem e provar reutilização antes de
considerar qualquer promoção ao núcleo compartilhado.

A unidade de evolução deixa de ser a incorporação imediata de módulos ao Core e
passa a ser a **integração governada por fronteiras**:

```text
                    GOVERNANÇA INSTITUCIONAL
          políticas | autoridade | validação humana
                              |
                              v
+------------------------------------------------------------------+
| APLICAÇÕES                                                        |
| CKO | CID | Biblioteca Digital | Governança Drive | Downloads     |
| jornadas, decisões contextuais e composition roots                |
+-------------------------------+----------------------------------+
                                | consomem a API pública preservada
                                v
+------------------------------------------------------------------+
| CKO CORE SDK 1.0.0                                               |
| contratos, modelos e motores neutros — 646 exports preservados    |
+-------------------------------^----------------------------------+
                                | implementam portas / são injetados
+-------------------------------+----------------------------------+
| PROVIDERS E ADAPTERS EXTERNOS                                    |
| capacidades semânticas | filesystem | Drive | bancos | serviços   |
+-------------------------------+----------------------------------+
                                |
                                v
+------------------------------------------------------------------+
| DADOS E CONHECIMENTO                                              |
| datasets operacionais | corpora institucionais | 02_Knowledge     |
+------------------------------------------------------------------+
```

O Ciclo II adota **federação governada**, não centralização física obrigatória.
Metadados, referências e proveniência podem ser integrados sem copiar o conteúdo
original. Aplicações compõem casos de uso; providers apresentam capacidades;
adapters conectam tecnologias; o Core permanece neutro.

## 2. Objetivos estratégicos

São objetivos do Ciclo II:

1. realizar o alto potencial de reutilização identificado pelo DSC-001 sem
   duplicação prematura;
2. integrar CID, Biblioteca Digital, Governança Google Drive, Organização
   Downloads e `02_Knowledge` por contratos e composição externa;
3. separar reutilização de código de reutilização de conhecimento;
4. estabelecer proveniência como requisito transversal de toda incorporação;
5. permitir inventário e consulta federados antes de qualquer consolidação física;
6. preservar autoridades institucionais, confidencialidade e validação humana;
7. reduzir dependências diretas entre produtos e tecnologias concretas;
8. produzir evidências para decisões futuras sem antecipá-las;
9. manter compatibilidade integral com o SDK 1.0.0;
10. evoluir incrementalmente com reversibilidade e gates explícitos.

Não são objetivos: reescrever aplicações, construir um data lake, unificar bancos,
mover acervos, automatizar decisões institucionais, criar novos exports, substituir
interfaces existentes ou declarar todo ativo descoberto como reutilizável.

## 3. Princípios arquiteturais

O Ciclo II herda integralmente os princípios da CKO-ARCH-001 e acrescenta
diretrizes complementares de aplicação:

1. **Baseline First.** Toda evolução parte da baseline publicada e não a modifica
   implicitamente.
2. **Reuse Before Build.** Capacidades existentes devem ser avaliadas antes de
   qualquer construção equivalente.
3. **Composition Before Promotion.** Primeiro reutilizar externamente; somente
   depois avaliar promoção ao SDK.
4. **Federation Before Consolidation.** Inventariar e referenciar antes de copiar,
   migrar ou centralizar.
5. **Provenance by Design.** Origem, transformação, responsabilidade e evidência
   acompanham todo ativo reutilizado.
6. **Authority Stays at the Source.** Integração técnica não transfere autoridade
   institucional ou autoria.
7. **Read Before Write.** A primeira integração de uma superfície deve ser
   somente leitura, salvo decisão posterior formal.
8. **Human-Governed Semantics.** Canonicidade, taxonomia, confidencialidade e
   certificação permanecem decisões humanas autorizadas.
9. **Least Knowledge and Least Privilege.** Cada componente acessa somente os
   dados e metadados necessários ao seu caso de uso.
10. **Deterministic Evidence.** Inventários, mapeamentos e resultados devem ser
    reproduzíveis e auditáveis.
11. **Reversibility.** Toda integração futura deve possuir desligamento, rollback
    e preservação do original.
12. **No Architecture by Copy.** Copiar código ou conteúdo não cria componente
    canônico nem transfere governança.

## 4. Limites do CKO Core

O CKO Core continua sendo o núcleo técnico compartilhado definido pela
CKO-ARCH-001. No Ciclo II, o Core:

- fornece exclusivamente a API pública e os comportamentos homologados do SDK
  1.0.0;
- permanece independente de CID, Biblioteca Digital, Google Drive, Downloads,
  `02_Knowledge` e caminhos físicos;
- não contém credenciais, conteúdo institucional, configuração de cliente,
  taxonomia aplicada, regras operacionais exclusivas ou autoridade decisória;
- não executa movimentações, exclusões ou reclassificações institucionais por
  inferência;
- não recebe novos exports, aliases, namespaces ou contratos por força deste
  documento;
- não absorve providers ou adapters concretos apenas porque foram reutilizados;
- pode ser consumido pelas aplicações e implementado por adapters externos nos
  pontos de extensão já homologados.

Qualquer ampliação futura da fronteira do Core exige demonstração de neutralidade,
reutilização transversal, compatibilidade, testes contratuais, versionamento,
documentação, homologação e, quando aplicável, ADR aprovado. Até que esses gates
sejam cumpridos, a capacidade permanece externa.

## 5. Papel dos Adapters

Adapters traduzem entre portas/modelos do ecossistema e tecnologias concretas.
São responsáveis por detalhes como filesystem, Google Drive, bancos, formatos,
APIs, autenticação, paginação, retries e limites operacionais.

Um Adapter DEVE:

- ficar fora do domínio do Core e depender de contratos públicos, nunca de
  detalhes internos;
- encapsular tecnologia, credenciais e configuração;
- declarar capacidades, limitações, modo de falha e consistência;
- preservar identidade da fonte e dados suficientes de proveniência;
- adotar leitura como modo inicial das novas integrações;
- ser substituível e testável por contrato;
- impedir mutação parcial e oferecer idempotência quando houver escrita futura;
- respeitar autorização, confidencialidade, quotas e retenção da fonte.

Um Adapter NÃO DEVE converter conveniência tecnológica em regra de domínio nem
atribuir canonicidade ao que apenas conseguiu ler.

## 6. Papel dos Providers

Providers apresentam capacidades e observações semanticamente compreensíveis às
aplicações e aos contratos de Discovery. Um Provider pode compor um ou mais
Adapters, aplicar mapeamento explícito e declarar quais capacidades oferece.

No Ciclo II:

- Providers são externos e injetados pela aplicação;
- cada Provider possui identidade, versão, escopo, owner e conjunto de
  capacidades declaradas;
- ausência de capacidade é explícita e não deve ser simulada;
- saída de Provider é observação candidata, não ativo canônico automático;
- Discovery não insere automaticamente no Inventory;
- resolução de identidade não substitui catalogação ou validação humana;
- providers concretos não integram a baseline do Core.

Adapter e Provider não são sinônimos: o Adapter resolve conectividade técnica; o
Provider oferece uma capacidade semântica por meio dessa conectividade.

## 7. Papel das Aplicações

As Aplicações são composition roots e proprietárias das jornadas. Compete a elas:

- selecionar e configurar Providers e Adapters;
- compor casos de uso com a API pública do Core;
- aplicar permissões e políticas contextuais aprovadas;
- orquestrar validação humana, tratamento de exceções e rollback;
- apresentar linguagem, UI, CLI e relatórios do produto;
- manter compatibilidade com consumidores e formatos próprios;
- produzir evidências operacionais sem transferir decisões ao SDK.

CKO atua como superfície integradora; CID como aplicação de ingestão e triagem;
Biblioteca Digital como aplicação de preservação e curadoria; Governança e
Downloads como superfícies operacionais com autoridades próprias. Nenhuma dessas
aplicações deve importar detalhes internos de outra ou duplicar capacidades
neutras sem avaliação de reutilização.

## 8. Papel dos Datasets

Dataset é uma coleção de dados delimitada por finalidade, schema, origem e ciclo
de vida operacional. Pode ser transitório, derivado, analítico ou de intercâmbio e
não possui, por si só, autoridade institucional.

Todo Dataset integrado DEVE declarar:

- owner e finalidade legítima;
- schema e versão;
- origem e método de aquisição;
- classificação de acesso e restrições de uso;
- janela temporal, retenção e descarte;
- qualidade conhecida e limitações;
- política de atualização;
- relação com originais e derivações;
- identificador e evidência de proveniência.

Datasets não devem ser confundidos com bancos canônicos, corpora institucionais ou
fontes de verdade. Cópias derivadas permanecem vinculadas à origem.

## 9. Papel dos Corpora Institucionais

Corpus Institucional é uma coleção de conhecimento curada, delimitada e governada,
com finalidade, autoridade, política de inclusão, proveniência e processo de
validação. Diferentemente de um Dataset, seu valor depende também de contexto,
seleção, relações e reconhecimento institucional.

Um Corpus Institucional DEVE possuir:

- escopo, finalidade, steward e autoridade aprovadora;
- critérios de inclusão, exclusão e atualização;
- taxonomia e vocabulários aplicáveis;
- política de confidencialidade e acesso;
- vínculo preservado com documentos originais;
- proveniência de itens, relações e transformações;
- estados explícitos de proposta, validação e publicação;
- processo de correção, versionamento e descontinuação.

O modelo homologado de `cko.core.corpus` pode representar estruturas neutras já
suportadas, mas não transforma automaticamente uma coleção em corpus oficial e
não deve ser ampliado por este documento.

## 10. Estratégia de integração do CID

O CID permanece aplicação consumidora do Core e não se torna módulo interno do
SDK. Sua integração ocorrerá por composição de capacidades existentes:

1. inventariar scanners, classificadores, sessões, transações, grafo, busca e
   contratos efetivamente existentes no CID;
2. mapear capacidades equivalentes para contratos públicos homologados, sem
   alterar esses contratos;
3. encapsular filesystem, bancos e serviços do CID em Adapters externos;
4. apresentar descoberta e ingestão por Providers injetados;
5. iniciar com observação e dry-run, preservando o comportamento legado;
6. manter classificação institucional e operações destrutivas sob aprovação
   explícita da aplicação;
7. medir reutilização real por mais de uma aplicação antes de propor promoção.

Não haverá importação reversa do Core para detalhes do CID, cópia indiscriminada
de código nem substituição imediata de seus fluxos históricos.

## 11. Estratégia de integração da Biblioteca Digital

A Biblioteca Digital permanece a superfície de preservação, curadoria,
catalogação e reutilização segura do conhecimento. Sua integração prioriza
metadados, referências, políticas e proveniência, não a movimentação do acervo.

A estratégia é:

1. inventariar corpora, CMC, taxonomias, POPs, inventários e processos de
   homologação sob sua autoridade;
2. expor metadados autorizados por Provider de catálogo;
3. usar Adapters para repositórios e formatos concretos;
4. representar itens e relações somente dentro dos modelos públicos já
   compatíveis;
5. manter originais em suas fontes e resolver acesso sob demanda;
6. distinguir registro localizado, registro curado e registro oficialmente
   validado;
7. preservar steward, direitos, confidencialidade e evidências de decisão.

O Knowledge Graph pode projetar relações autorizadas, mas não substitui CMC,
catálogo, documento original ou autoridade da Biblioteca.

## 12. Estratégia de integração da Governança Google Drive

O Google Drive é infraestrutura e repositório operacional, não domínio, corpus ou
autoridade por si só. A autoridade deriva dos papéis e processos de Governança.

A integração DEVE:

- usar Adapter externo para a API e os identificadores estáveis do Drive;
- começar em modo somente leitura e com menor privilégio;
- registrar arquivo, versão/revisão, localização lógica, owner, permissões
  relevantes, timestamp e checksum quando permitido;
- tratar atalhos, duplicidades, compartilhamentos e movimentos sem inferir nova
  identidade canônica;
- separar metadados técnicos de classificação institucional;
- manter credenciais e IDs de ambiente fora do Core e dos documentos versionados;
- respeitar limites de API, revogação, auditoria e exclusão na fonte;
- exigir autorização independente para qualquer escrita, reorganização ou
  alteração de permissão futura.

O nome ou a pasta no Drive não constituem, isoladamente, prova de canonicidade.

## 13. Estratégia de integração da Organização Downloads

Downloads é uma superfície operacional de chegada, triagem e organização, não
fonte institucional automática. Sua integração segue pipeline supervisionado:

```text
detecção -> inventário -> metadados/hash -> proposta de classificação
         -> revisão humana -> ação autorizada -> evidência/rollback
```

Regras do Ciclo II:

- observar antes de mover;
- preservar caminho e conteúdo originais até ação autorizada;
- separar detecção, classificação e execução física;
- tornar conflitos, duplicidades e baixa confiança visíveis;
- usar Adapter de filesystem e Provider de ingestão externos;
- impedir exclusão, sobrescrita ou oficialização silenciosa;
- registrar proveniência da observação, decisão e eventual ação;
- permitir quarentena lógica, sem presumir diretório físico específico.

Downloads pode alimentar datasets de triagem e candidatos a corpora, mas não
certifica conteúdo.

## 14. Estratégia para o corpus `02_Knowledge`

`02_Knowledge` será tratado como **portfólio de coleções candidatas**, não como um
corpus único automaticamente canônico. A estrutura física atual permanece
preservada.

A estratégia possui cinco estágios arquiteturais:

1. **Inventário read-only:** identificar coleções, owners, formatos, volumes,
   acessos e restrições sem mover ou editar arquivos.
2. **Delimitação:** propor fronteiras de datasets e corpora por finalidade e
   autoridade, sem homologá-las automaticamente.
3. **Mapeamento:** associar metadados e identidades aos modelos públicos
   compatíveis, preservando referências às fontes.
4. **Curadoria:** submeter inclusão, taxonomia, confidencialidade e canonicidade à
   governança e aos stewards responsáveis.
5. **Federação:** disponibilizar catálogo e consulta autorizada por Providers e
   Adapters, mantendo o conteúdo em sua localização governada sempre que possível.

Pastas, nomes e hierarquia física são evidências contextuais, não ontologia
oficial. Conteúdo pessoal, confidencial, duplicado, temporário ou sem direitos
claros permanece excluído de reutilização até decisão expressa.

## 15. Política de reutilização de código

A reutilização de código segue a ordem preferencial:

1. consumir a API pública do Core;
2. reutilizar uma biblioteca ou componente no repositório de origem;
3. envolver legado com Adapter;
4. compor capacidade por Provider;
5. extrair componente externo compartilhado;
6. somente então avaliar promoção ao SDK.

Toda reutilização DEVE verificar licença/autoria, dependências, segurança,
manutenção, cobertura, consumidores, compatibilidade e owner. Copiar e colar é
excepcional, deve preservar atribuição e não equivale a promoção arquitetural.

Promoção futura ao Core somente poderá ocorrer quando a capacidade for neutra,
coesa, comprovadamente transversal, livre de infraestrutura concreta, coberta por
contratos e testes, documentada, versionada e homologada. Este documento não
declara nenhum candidato promovido.

## 16. Política de reutilização de conhecimento

Reutilizar conhecimento significa permitir descoberta e uso autorizado com
contexto suficiente, não replicar conteúdo indiscriminadamente.

Antes da reutilização devem ser conhecidos:

- autoria, fonte, steward e autoridade;
- finalidade original e finalidade pretendida;
- direitos, licença, consentimento e confidencialidade;
- versão, temporalidade, validade e qualidade;
- contexto, taxonomia e limitações;
- transformações e derivações;
- necessidade de validação humana.

Conhecimento derivado não substitui a fonte. Resumos, embeddings, índices, grafos
e respostas assistidas permanecem projeções vinculadas às evidências originais.
Conteúdo sem proveniência suficiente pode ser inventariado como não confiável, mas
não deve ser publicado como conhecimento institucional.

## 17. Política de Provenance

Provenance é obrigatória em toda fronteira de ingestão, transformação, decisão e
publicação. A fundação homologada de `cko.core.provenance` deve ser usada dentro de
seus contratos atuais, sem alteração de API.

Cada registro de proveniência DEVE permitir determinar:

- qual entidade ou conteúdo foi observado;
- de qual fonte, localização e versão se originou;
- qual agente humano ou técnico atuou;
- qual atividade foi realizada e quando;
- quais entradas, parâmetros e políticas foram aplicados;
- qual resultado ou derivação foi produzido;
- quais evidências sustentam a relação;
- qual estado de validação e confiança foi atribuído;
- qual regra de acesso protege o registro.

Registros devem ser imutáveis ou append-only, ordenáveis, serializáveis e
auditáveis. Correções produzem nova declaração vinculada; não apagam a história.
Ausência de proveniência, falha de resolução ou conflito devem permanecer
explícitos. Dados sensíveis não devem ser copiados para a proveniência quando uma
referência protegida for suficiente.

## 18. Política de Testes

Esta arquitetura não cria nem executa testes. Para integrações futuras, a política
obrigatória será:

1. testes de caracterização do comportamento legado antes de mudança;
2. testes unitários de mapeamento e invariantes;
3. testes contratuais por porta, Adapter e Provider;
4. testes de conformidade com os modelos e serializadores públicos;
5. testes de integração com fixtures isoladas, nunca com acervo permanente;
6. testes de permissões, confidencialidade e menor privilégio;
7. testes de idempotência, repetição, paginação, retry e falha parcial;
8. testes de proveniência e rastreabilidade ponta a ponta;
9. golden files ou snapshots determinísticos para mapeamentos;
10. execução paralela, dry-run e comparação antes de substituição;
11. testes de rollback e desligamento;
12. regressão integral do SDK e verificação mecânica dos 646 exports.

Testes de integração não podem escrever em Drive, Downloads, `02_Knowledge`,
bancos ou corpora reais sem fixture, autorização e isolamento explícitos.

## 19. Estratégia para evolução incremental

O padrão de evolução do Ciclo II é Strangler Fig orientado por evidência:

```text
inventariar
    -> caracterizar
    -> mapear contratos existentes
    -> envolver com Adapter
    -> expor por Provider
    -> operar read-only/dry-run
    -> executar em paralelo
    -> homologar por aplicação
    -> medir reutilização
    -> decidir manter externo ou propor evolução formal
```

Cada incremento futuro DEVE ter escopo único, consumidores identificados,
fronteiras de dados, compatibilidade, observabilidade, critérios de aceite,
rollback e autoridade. Integrações podem ser desligadas sem retirar o legado.

Não haverá big bang, migração irreversível, dependência direta entre aplicações,
centralização obrigatória ou promoção ao Core baseada apenas em expectativa.

## 20. Roadmap arquitetural do Ciclo II

O roadmap abaixo define ondas e gates arquiteturais. Não define Sprints, datas,
equipes, commits ou autorização de implementação.

| Onda | Finalidade arquitetural | Evidência de saída | Gate para avançar |
|---|---|---|---|
| II.0 — Preservação | Fixar referências da baseline, owners, fronteiras e superfícies protegidas | matriz de autoridade e compatibilidade | baseline e escopo confirmados |
| II.1 — Inventário federado | Caracterizar CID, Biblioteca, Drive, Downloads e `02_Knowledge` em leitura | inventários reproduzíveis e mapa de sobreposição | fontes e restrições validadas |
| II.2 — Contratos e mapeamentos | Mapear capacidades aos 646 exports e portas existentes | matriz de contratos, gaps e decisões não tomadas | zero alteração implícita de API |
| II.3 — Adapters e Providers | Definir composições externas substituíveis | especificações contratuais e estratégia de teste | segurança, proveniência e rollback aprovados |
| II.4 — Pilotos supervisionados | Validar jornadas read-only/dry-run por aplicação | métricas de qualidade, compatibilidade e reutilização | homologação humana por domínio |
| II.5 — Federação de conhecimento | Integrar catálogo, corpora e consultas autorizadas | catálogo federado e cadeia de proveniência | governança e acesso aprovados |
| II.6 — Consolidação de evidências | Avaliar o que permanece externo e o que merece proposta formal | relatório de reutilização e gaps comprovados | decisão arquitetural futura, se necessária |
| II.7 — Escala governada | Expandir apenas padrões homologados e reversíveis | conformidade contínua e indicadores operacionais | revisão periódica de arquitetura |

A Onda II.3 não autoriza a criação de adapters/providers; a Onda II.4 não abre
pilotos; e a Onda II.6 não cria ADRs. Cada ação dependerá de autorização própria.

---

## 21. Justificativa das seções

| Seção | Justificativa arquitetural |
|---|---|
| 1. Visão geral | Converte o resultado do DSC-001 em modelo de federação e composição sem alterar a baseline. |
| 2. Objetivos | Define resultados estratégicos e impede que integração seja confundida com centralização ou reescrita. |
| 3. Princípios | Torna explícitas as regras que protegem autoridade, reversibilidade e reutilização responsável. |
| 4. Limites do Core | Evita erosão da fronteira do SDK e protege os 646 exports. |
| 5. Adapters | Isola tecnologias concretas e mantém dependências orientadas ao núcleo. |
| 6. Providers | Separa conectividade técnica de capacidade semântica e preserva Discovery como observação. |
| 7. Aplicações | Mantém jornadas, composição e decisões contextuais fora do SDK. |
| 8. Datasets | Evita tratar dados operacionais como fonte institucional automática. |
| 9. Corpora | Formaliza a diferença entre coleção técnica e conhecimento institucional governado. |
| 10. CID | Aproveita a superfície técnica madura identificada no ecossistema sem acoplá-la ao Core. |
| 11. Biblioteca Digital | Preserva sua autoridade de curadoria e prioriza integração por catálogo e referência. |
| 12. Governança Drive | Trata Drive como infraestrutura, com menor privilégio e sem canonicidade por localização. |
| 13. Downloads | Mantém detecção, classificação e execução física separadas e supervisionadas. |
| 14. `02_Knowledge` | Protege um acervo heterogêneo contra oficialização ou migração indiscriminada. |
| 15. Reutilização de código | Estabelece composição antes de extração e gates antes de promoção ao SDK. |
| 16. Reutilização de conhecimento | Protege contexto, direitos, confidencialidade e vínculo com a fonte. |
| 17. Provenance | Dá rastreabilidade transversal às integrações e reutiliza a fundação homologada. |
| 18. Testes | Define evidências mínimas para evolução futura sem executar trabalho de implementação agora. |
| 19. Evolução incremental | Aplica Strangler Fig com read-only, paralelismo, rollback e decisão baseada em evidência. |
| 20. Roadmap | Ordena o Ciclo II por gates sem criar Sprint ou autorização implícita. |

## 22. Impactos arquiteturais

### 22.1 Impactos imediatos

Os impactos imediatos são exclusivamente documentais:

- instituição do Ciclo Arquitetural II como camada complementar de evolução;
- definição de papéis para Adapters, Providers, Aplicações, Datasets e Corpora;
- definição de estratégias de integração sem execução;
- estabelecimento de gates e evidências para decisões futuras.

Não há impacto imediato em código, runtime, dados, builds, dependências, contratos,
API, empacotamento, bancos ou processos operacionais.

### 22.2 Impactos futuros condicionais

Se autorizados por processos posteriores, os impactos poderão incluir Adapters e
Providers externos, composition roots nas aplicações, catálogos federados,
políticas operacionais e suítes de conformidade. Tais impactos deverão permanecer
fora do Core até eventual promoção formal e não são aprovados por este documento.

### 22.3 Riscos controlados

- **Acoplamento ao produto:** controlado por portas, Adapters e composição.
- **Cópia indiscriminada:** controlada pela política de reutilização.
- **Perda de autoridade:** controlada por governança e Provenance.
- **Centralização prematura:** controlada por federação antes de consolidação.
- **Operação destrutiva:** controlada por read-only, dry-run, aprovação e rollback.
- **Quebra da API:** controlada pelo congelamento dos 646 exports e regressão.
- **Oficialização indevida:** controlada pela separação entre observação,
  curadoria e validação.

## 23. Compatibilidade com a baseline

| Superfície protegida | Compatibilidade do ARCH-002 |
|---|---|
| CKO-ARCH-001 | Complementa a arquitetura canônica; mantém monólito modular, Ports and Adapters, SDK compartilhado e produtos consumidores. |
| CKO-BASELINE-2026.07 | Não altera, reabre ou substitui decisão homologada. |
| SDK 1.0.0 | Não modifica módulo, dependência, comportamento ou empacotamento. |
| API pública | Preserva exatamente os 646 exports; não cria, remove, renomeia ou deprecia símbolo. |
| Direção de dependências | Aplicações e infraestrutura dependem do núcleo; o núcleo não depende delas. |
| Governança | Mantém CMC, taxonomia, canonicidade, confidencialidade e validação sob autoridade institucional. |
| Persistência e fontes | Mantém tecnologias concretas e repositórios atrás de Adapters. |
| Legado | Preserva comportamento, originais, formatos e caminhos de reversão. |
| Provenance | Reutiliza a fundação homologada sem ampliar seus contratos. |
| Testes | Mantém os gates vigentes e exige regressão dos 646 exports para trabalho futuro. |
| Versionamento | Nenhum impacto SemVer; o SDK permanece 1.0.0. |

Conclusão de compatibilidade: **compatível por construção**, pois toda evolução
descrita ocorre por composição externa e toda mudança material permanece sujeita
a decisão e autorização posteriores.

## 24. Recomendações para futuros ADRs

Este documento não cria ADRs. Recomenda-se avaliar ADR somente quando uma decisão
material concreta não puder ser resolvida pela baseline vigente. Temas candidatos:

1. fronteira e ownership de um catálogo federado institucional;
2. modelo de identidade entre fontes e política de reconciliação de duplicidades;
3. política de escrita e sincronização bidirecional com Google Drive;
4. critérios formais de promoção de um componente comprovadamente transversal ao
   Core;
5. política institucional de retenção, exclusão e direito ao esquecimento em
   datasets, corpora e Provenance;
6. modelo de autorização para consulta federada entre domínios de confidencialidade;
7. escolha de persistência ou índice canônico, caso a federação demonstre essa
   necessidade;
8. política de descontinuação de um fluxo legado após equivalência comprovada.

Um futuro ADR DEVE registrar contexto, decisão material, alternativas,
consequências, impacto sobre a baseline, segurança, migração, compatibilidade,
rollback, autoridade e evidências. Lacunas de implementação, escolha de biblioteca
local ou mera documentação operacional não devem gerar ADR automaticamente.

## 25. Critérios de conformidade do Ciclo II

Uma iniciativa futura somente estará conforme esta arquitetura quando demonstrar:

- aderência explícita à CKO-ARCH-001 e à CKO-BASELINE-2026.07;
- zero alteração não autorizada nos 646 exports;
- fronteiras claras entre Core, Adapter, Provider e Aplicação;
- owner, finalidade, acesso e proveniência de datasets/corpora;
- validação humana para decisões institucionais;
- read-only ou justificativa formal para escrita;
- testes proporcionais, observabilidade e rollback;
- preservação do legado e dos originais;
- ausência de Sprint, RFC, ADR ou implementação implícita.

## 26. Declaração final

O Ciclo Arquitetural II estabelece uma arquitetura de evolução por reutilização,
federação governada e composição externa. CID, Biblioteca Digital, Governança
Google Drive, Organização Downloads e `02_Knowledge` passam a possuir estratégias
arquiteturais explícitas de integração, sem alteração de suas autoridades e sem
incorporação automática ao CKO Core.

A CKO-BASELINE-2026.07 permanece integralmente preservada. O CKO CORE SDK
permanece na versão 1.0.0, com 646 exports públicos únicos e resolvidos. Nenhum
código, contrato público, RFC, ADR ou Sprint é criado ou autorizado por esta
arquitetura.

## Referências

- `../../../docs/arquitetura/CKO-ARCH-001_ARQUITETURA_CANONICA.md`
- `../../../docs/arquitetura/discovery/DISCOVERY-ECOSYSTEM-001.md`
- `../../../docs/arquitetura/discovery/DISCOVERY-ECOSYSTEM-002.md`
- `../../../docs/governance/CKO-GOV-001_BASELINE_ARQUITETURAL_1.0.md`
- `../../ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md`
- `../../CKO_CORE_V1_ARCHITECTURE_MAP.md`
- `../../CKO_CORE_V1_PUBLIC_API_CATALOG.md`
- `../../CKO_CORE_V1_RELEASE_CERTIFICATION.md`
- DSC-001 — Ecosystem Discovery (conclusões comunicadas ao processo ARCH-002)
