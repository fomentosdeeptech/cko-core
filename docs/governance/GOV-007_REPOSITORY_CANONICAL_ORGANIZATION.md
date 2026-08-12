# CKO — GOV-007 — Repository Canonical Organization

**Processo:** CKO — GOV-007 — Repository Canonical Organization
**Título institucional:** Organização Canônica do Repositório CKO
**Status:** oficial
**Versão:** 1.0
**Data:** 03/08/2026
**Natureza:** política documental e organizacional permanente; exclusivamente documental
**Escopo:** patrimônio documental do repositório CKO, com regras específicas para a raiz do CORE e para `docs/`
**Baseline protegida:** `CKO-BASELINE-2026.07`
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos
**Efeito imediato:** normativo e classificatório; sem reorganização física
**Escopo de mudança deste processo:** criação exclusiva deste documento

> Esta GOV estabelece a organização institucional definitiva do repositório.
> Ela não move, renomeia, remove, reclassifica fisicamente nem modifica qualquer
> artefato preexistente. Toda estrutura futura descrita neste documento é um
> destino normativo e dependerá de inventário, plano, autorização, execução
> controlada, validação e homologação próprios.

---

## Sumário executivo

O patrimônio documental do CKO cresceu ao longo do Ciclo Arquitetural I em
diversas superfícies: raiz do CORE, diretórios documentais do CORE, documentação
institucional do projeto e registros de implementação, auditoria e homologação.
Essa distribuição preserva a história real do desenvolvimento, mas não deve ser
reproduzida indefinidamente como modelo de crescimento.

Esta GOV institui uma organização baseada em quatro separações fundamentais:

1. **autoridade:** canônico ou não canônico;
2. **vigência:** ativo, histórico, superseded ou obsoleto;
3. **proveniência:** nativo, legado ou incorporado;
4. **maturidade e custódia:** trabalho, experimental, temporário ou arquivado.

A estrutura canônica futura concentra documentação em `docs/`, mantém na raiz
do CORE apenas documentos de entrada e políticas comunitárias indispensáveis,
preserva registros históricos de forma imutável e separa documentos normativos,
decisórios, executivos, probatórios, modelos e materiais de trabalho. O presente
ato não executa essa estrutura: ele define como uma reorganização futura deverá
ser planejada e controlada.

---

## 1. Objetivo

Instituir o padrão oficial e permanente de organização documental do CKO para:

- oferecer uma localização previsível para cada classe de documento;
- distinguir autoridade, vigência, maturidade e custódia;
- reduzir duplicidade, ambiguidade e referências quebradas;
- preservar integralmente a memória arquitetural e probatória;
- tornar criação, revisão, auditoria, release e baseline verificáveis;
- impedir que conveniência física altere autoridade institucional;
- preparar uma futura reorganização física reversível e homologada.

## 2. Escopo e limites

Esta política rege documentos Markdown e demais artefatos documentais mantidos
no repositório CKO, inclusive documentos institucionais, arquiteturais, de
governança, ADRs, RFCs, Sprints, auditorias, relatórios, catálogos, mapas,
roadmaps, discoveries, READMEs, changelogs e templates.

Este processo NÃO:

- implementa código ou altera comportamento;
- altera SDK, API pública, contratos, testes ou baseline;
- cria Sprint, ADR ou RFC;
- cria commit;
- movimenta, renomeia, remove ou modifica documento preexistente;
- reorganiza diretórios ou corrige referências existentes;
- declara automaticamente como canônico um documento apenas por sua localização;
- autoriza futura reorganização sem os gates da seção 25.

Artefatos de código, configuração, build, runtime e testes são mencionados
somente para delimitar onde a documentação pode residir. Sua organização técnica
continua submetida à arquitetura e à governança competentes.

## 3. Autoridade, precedência e compatibilidade

A GOV-007 é subordinada às autoridades materiais já vigentes e deve ser
interpretada na seguinte ordem:

1. CKO-GOV-001 e `CKO-BASELINE-2026.07`;
2. CKO-ARCH-001 e contratos/evidências homologados do SDK `cko` 1.0.0;
3. CKO-ARCH-002, para a evolução do ecossistema;
4. ADRs aceitos e seu índice reconciliado pelo GOV-003;
5. GOV-002, GOV-003, GOV-005, GOV-006 e esta GOV-007, cada qual em sua matéria;
6. RFCs aprovadas;
7. termos, especificações e entregas de Sprints autorizadas.

Em conflito material, prevalece o instrumento superior ou o documento canônico
competente. Localização, nome de arquivo ou status Git não elevam a autoridade de
um documento. A GOV-007 organiza o patrimônio; não muda decisões técnicas.

## 4. Princípios gerais de organização documental

1. **Autoridade explícita.** Canonicidade decorre de aprovação e registro, não de posição física.
2. **Uma fonte de verdade por matéria.** Duplicatas podem ser preservadas, mas uma única representação deve ser indicada como canônica.
3. **História imutável.** Evidências, decisões e registros encerrados não são reescritos para parecer atuais.
4. **Proveniência preservada.** Origem, autor, data, vínculos e motivo de transição devem permanecer rastreáveis.
5. **Separação de naturezas.** Norma, arquitetura, decisão, proposta, execução, evidência, modelo e rascunho não compartilham autoridade implícita.
6. **Evolução aditiva.** Substituição cria vínculo explícito e preserva o substituído.
7. **Referências estáveis.** Mudanças físicas exigem mapa de redirecionamento e validação de links.
8. **Menor privilégio documental.** Materiais de trabalho não podem assumir força normativa.
9. **Reversibilidade.** Reorganizações devem admitir rollback por manifesto.
10. **Auditabilidade.** Toda transição relevante produz responsável, decisão, data e evidência.
11. **Compatibilidade.** Organização documental não altera contrato técnico nem semântica histórica.
12. **Crescimento controlado.** Novos diretórios e famílias dependem de necessidade comprovada.

## 5. Modelo oficial de classificação documental

### 5.1 Dimensões independentes

As classificações NÃO formam uma única escala. Cada documento DEVE ser descrito,
quando aplicável, por quatro dimensões:

| Dimensão | Pergunta | Valores principais |
|---|---|---|
| Autoridade | Este documento governa sua matéria? | `CANÔNICO` ou não canônico |
| Ciclo de vida | Seu conteúdo ainda rege ou informa o presente? | `ATIVO`, `HISTÓRICO`, `SUPERSEDED`, `OBSOLETO` |
| Proveniência | Ele pertence ao modelo atual de origem? | nativo ou `LEGADO` |
| Maturidade/custódia | Em que estágio e regime de retenção está? | `TRABALHO`, `EXPERIMENTAL`, `TEMPORÁRIO`, `ARQUIVADO` |

Um documento pode, por exemplo, ser `CANÔNICO + ATIVO`, `CANÔNICO + HISTÓRICO +
ARQUIVADO`, ou `LEGADO + SUPERSEDED + ARQUIVADO`. Combinações contraditórias,
como `ATIVO + OBSOLETO`, são proibidas.

### 5.2 Definições oficiais

| Categoria | Significado obrigatório | Efeito |
|---|---|---|
| **CANÔNICO** | Fonte oficial aprovada para uma matéria e versão determinadas. | Deve possuir autoridade, status, versão ou data de corte, proprietário e vínculos normativos claros. |
| **ATIVO** | Documento aplicável ao estado presente ou a processo em curso. | Deve ser revisável, localizável no mapa ativo e ter responsável definido. |
| **HISTÓRICO** | Registro autêntico de estado, decisão, execução ou evidência passada cuja preservação é necessária. | Não rege automaticamente o presente; deve ser preservado sem reescrita substantiva. |
| **LEGADO** | Artefato criado sob convenção, estrutura, tecnologia ou contrato anterior, ainda necessário para compatibilidade, prova ou transição. | Sua existência não implica obsolescência; migração ou retirada exige avaliação de consumidores. |
| **SUPERSEDED** | Documento formalmente substituído por outro documento identificado. | Perde precedência prospectiva, conserva valor histórico e deve apontar o sucessor. |
| **OBSOLETO** | Documento que não descreve mais o sistema, processo ou regra e não deve orientar novas ações. | Deve conter advertência e justificativa; pode ser preservado por evidência. |
| **ARQUIVADO** | Documento retirado da área operacional ativa e colocado sob custódia de preservação. | Permanece pesquisável, íntegro e sujeito a retenção; arquivamento não significa exclusão. |
| **TEMPORÁRIO** | Artefato com finalidade e prazo de retenção limitados, sem autoridade permanente. | Deve indicar responsável, expiração e destinação; vencido, é revisado para descarte governado ou promoção. |
| **TRABALHO** | Rascunho, nota ou material intermediário ainda não aprovado. | Não pode ser citado como norma nem usar status oficial; deve indicar claramente `TRABALHO`. |
| **EXPERIMENTAL** | Documento que explora hipótese, modelo ou organização ainda não adotados. | Deve declarar critérios de avaliação e não pode alterar a baseline ou a organização canônica. |

### 5.3 Documento ativo e documento histórico

Documento **ativo** orienta decisão, operação ou evolução presente. Documento
**histórico** comprova o que foi decidido, executado, observado ou homologado em
um corte anterior. O encerramento de uma Sprint torna seu termo e suas evidências
históricos, mas não os torna irrelevantes; uma política pode continuar ativa por
várias releases; uma arquitetura original pode ser histórica e ainda ser fonte
primária para o contexto de decisões passadas.

### 5.4 Documento canônico e documento de trabalho

Documento **canônico** possui aprovação e autoridade delimitadas. Documento de
**trabalho** serve à elaboração e pode mudar sem processo de substituição. A
promoção de trabalho para canônico exige revisão, metadados, aprovação, destino
oficial e registro no índice aplicável. Copiar um rascunho para diretório
canônico não o promove.

### 5.5 Regras para superseded, obsoleto, legado e arquivado

- `SUPERSEDED` exige identificador e link do sucessor, data e razão.
- `OBSOLETO` exige declaração de não uso e avaliação de preservação.
- `LEGADO` exige descrição da dependência histórica ou do consumidor protegido.
- `ARQUIVADO` exige registro no inventário e verificação de integridade.
- um documento superseded ou obsoleto NÃO DEVE ser apagado quando sustentar
  decisão, auditoria, homologação, baseline, release ou obrigação legal.
- “deprecated” pode ser usado em contratos técnicos, mas documentos adotam as
  categorias desta GOV; quando necessário, deve ser mapeado para estado e prazo.

## 6. Metadados documentais obrigatórios

Todo novo documento institucional, arquitetural, de governança, ADR, RFC,
Sprint, auditoria ou relatório DEVE declarar, no corpo inicial ou em front
matter equivalente:

- identificador e título;
- status e classificação;
- versão ou data de corte;
- data e fuso quando o horário for relevante;
- proprietário institucional ou mantenedor;
- escopo e natureza;
- documentos de autoridade e artefatos relacionados;
- baseline/release afetada ou declaração de não afetação;
- substitui/substituído por, quando aplicável;
- prazo de revisão ou evento de revisão;
- nível de confidencialidade, quando aplicável.

Relatórios gerados automaticamente devem registrar ferramenta, versão, entradas
e procedimento de reprodução. Segredos, credenciais, dados pessoais indevidos e
caminhos privados não devem ser incorporados como metadados.

## 7. Estrutura canônica definitiva de `docs/`

A estrutura normativa para crescimento e futura reorganização é:

```text
docs/
├── README.md
├── INDEX.md
├── institutional/
│   ├── architecture/
│   ├── governance/
│   ├── policies/
│   ├── roadmaps/
│   └── glossaries/
├── architecture/
│   ├── core/
│   ├── ecosystem/
│   ├── discoveries/
│   ├── maps/
│   └── catalogs/
├── governance/
├── adr/
│   └── INDEX.md
├── rfc/
│   └── INDEX.md
├── sprints/
│   └── INDEX.md
├── audits/
│   ├── architecture/
│   ├── documentation/
│   ├── implementation/
│   └── release/
├── reports/
│   ├── implementation/
│   ├── homologation/
│   ├── certification/
│   ├── discovery/
│   └── metrics/
├── guides/
├── reference/
├── templates/
│   ├── governance/
│   ├── adr/
│   ├── rfc/
│   ├── sprint/
│   ├── audit/
│   └── report/
├── archive/
│   ├── architecture/
│   ├── governance/
│   ├── adr/
│   ├── rfc/
│   ├── sprints/
│   ├── audits/
│   └── reports/
└── work/
    ├── drafts/
    ├── experimental/
    └── temporary/
```

Esta árvore é **recomendada como destino final**, não como comando de criação.
Diretórios vazios não devem ser criados apenas para reproduzir o desenho.
`docs/README.md` explica navegação e regras; `docs/INDEX.md` oferece o mapa
institucional e aponta os índices especializados.

## 8. Estrutura definitiva dos documentos da raiz do CORE

A raiz do CORE deve permanecer uma superfície de entrada mínima. Em seu estado
futuro, documentos mantidos na raiz limitam-se a:

- `README.md` — entrada principal e navegação;
- `CHANGELOG.md` — evolução publicada;
- `ROADMAP.md` — direção pública vigente, se adotado como roadmap raiz;
- `CONTRIBUTING.md` — contribuição;
- `SECURITY.md` — política de segurança;
- `CODE_OF_CONDUCT.md` — conduta;
- arquivos exigidos por licenciamento ou ferramentas, quando aplicável.

Arquiteturas detalhadas, relatórios de implementação, especificações, termos de
Sprint, inventários e auditorias não devem nascer na raiz. Os documentos hoje
existentes na raiz permanecem intocados até a reorganização futura. Arquivos
técnicos como `pyproject.toml`, manifests e scripts não são documentos desta
taxonomia e seguem a governança técnica competente.

## 9. Organização por família documental

### 9.1 Documentos institucionais

Atos que definem identidade, autoridade, baseline institucional, políticas
transversais, glossários e roadmaps de plataforma residem em
`docs/institutional/`. Subdiretórios separam arquitetura institucional,
governança institucional, políticas, roadmaps e vocabulário. A duplicação de
atos entre o repositório do projeto e o CORE deve ser resolvida por referência,
não por cópias divergentes.

### 9.2 Documentos arquiteturais

Arquiteturas de produto, Core, ecossistema, discoveries, mapas e catálogos
residem em `docs/architecture/`. Arquitetura normativa não se mistura com
auditoria arquitetural ou relatório de implementação. Documentos mestres devem
declarar quais versões são vigentes e quais cortes são históricos.

### 9.3 Documentos de governança

GOVs específicas do repositório ou do CORE residem em `docs/governance/`.
Políticas permanentes de plataforma podem residir em
`docs/institutional/governance/`, conforme sua autoridade. Cada GOV possui
identificador imutável, objetivo, autoridade, compatibilidade, riscos e
declaração de efeito. Lacunas de numeração são registradas, nunca preenchidas
retroativamente por conveniência.

### 9.4 ADRs

ADRs residem em `docs/adr/` e são governados pelo GOV-003. O `INDEX.md` é o
registro canônico de identificadores, títulos, status, sucessões e links. ADR
aceito não é reescrito para incorporar decisão nova; correções editoriais devem
ser claramente separadas, e mudança material exige novo ADR. Variantes como
`decisoes/` devem ser reconciliadas somente no plano futuro aprovado.

### 9.5 RFCs

RFCs residem em `docs/rfc/`. Cada RFC declara status, proprietário, dependências,
escopo, alternativas, segurança, compatibilidade e decisão associada. RFC
proposta não equivale a aprovação, Sprint ou autorização de implementação. O
índice registra proposta, revisão, aprovação, rejeição, retirada ou supersessão.

### 9.6 Sprints

Termos, especificações e encerramentos de Sprint residem em `docs/sprints/`,
preferencialmente agrupados por identificador quando houver múltiplos artefatos:

```text
docs/sprints/SPR-017/
├── SPR-017_OPENING.md
├── SPR-017_TECHNICAL_SPECIFICATION.md
├── SPR-017_AUDIT.md
├── SPR-017_IMPLEMENTATION_REPORT.md
└── SPR-017_HOMOLOGATION_REPORT.md
```

O exemplo define função, não nomes retroativos. Sprints encerradas tornam-se
históricas, permanecendo na família para rastreabilidade; arquivamento físico só
ocorre quando não prejudicar navegação, links ou baseline.

### 9.7 Auditorias

Auditorias residem em `docs/audits/` por objeto: arquitetura, documentação,
implementação ou release. Toda auditoria declara escopo, universo, método,
evidências, achados, severidade, limitações, responsável e conclusão. Auditoria
não modifica o objeto auditado durante a mesma etapa e não se confunde com
homologação.

### 9.8 Relatórios

Relatórios residem em `docs/reports/` por finalidade: implementação,
homologação, certificação, discovery ou métricas. Um relatório descreve fatos e
evidências; não cria decisão arquitetural implícita. Relatórios reproduzíveis
devem vincular entradas e comandos, preservando dados brutos quando necessários.

### 9.9 Templates

Templates residem exclusivamente em `docs/templates/` por família. Devem conter
marcadores explícitos, versão, mantenedor e instruções, sem identificadores reais
reservados. Alteração material de template não altera retroativamente documentos
já emitidos.

### 9.10 Documentos históricos

O diretório `docs/archive/` guarda material retirado da navegação ativa quando a
preservação fora de sua família melhorar a operação sem romper rastreabilidade.
Arquivamento deve manter a família original, um índice, o hash anterior e o mapa
origem-destino. Documentos históricos frequentemente consultados podem permanecer
na família ativa com status histórico; `HISTÓRICO` não obriga movimentação.

### 9.11 Trabalho, experimental e temporário

Materiais ainda não oficiais residem em `docs/work/`. Nenhum arquivo dessa área
pode ser dependência normativa de código, release ou baseline. O diretório deve
ser revisado em toda Sprint e não pode se tornar arquivo permanente informal.

## 10. Convenção oficial para nomes de diretórios

Novos diretórios documentais DEVEM:

- usar inglês técnico estável, minúsculas e `kebab-case` quando houver mais de uma palavra;
- evitar espaços, acentos, datas e números ordinais sem função taxonômica;
- representar uma família ou domínio, não um status transitório informal;
- usar plural para coleções (`sprints`, `audits`, `reports`, `templates`) e nomes
  consagrados no singular quando já institucionalizados (`governance`, `architecture`, `reference`);
- não duplicar sinônimos, como `sprint/` e `sprints/`, ou idiomas paralelos;
- não ser criado antes de existir conteúdo aprovado para ele.

Exceções de legado permanecem válidas até migração controlada.

## 11. Convenção oficial para nomes de arquivos

### 11.1 Regras gerais

- extensão preferencial: `.md` para documentos textuais versionáveis;
- caracteres: `A-Z`, `0-9`, hífen e sublinhado conforme os padrões abaixo;
- identificadores institucionais permanecem em maiúsculas;
- palavras do título usam `UPPER_SNAKE_CASE` após o identificador;
- não usar espaços, acentos, `FINAL`, `NOVO`, `OK`, `DEF`, `COPIA` ou versões ambíguas;
- datas, quando necessárias, usam ISO `YYYY-MM-DD`;
- versão no nome só é usada quando múltiplas versões precisam coexistir; a
  preferência é versão nos metadados e histórico Git;
- nome não deve conter status que possa mudar, salvo snapshots históricos.

### 11.2 Padrões por família

| Família | Padrão | Exemplo |
|---|---|---|
| Governança | `GOV-NNN_TITULO.md` | `GOV-007_REPOSITORY_CANONICAL_ORGANIZATION.md` |
| Arquitetura institucional | `CKO-ARCH-NNN_TITULO.md` | `CKO-ARCH-002_ECOSYSTEM_EVOLUTION_ARCHITECTURE.md` |
| Arquitetura do Core | `ARCH-NNN_TITULO.md` | `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md` |
| ADR | `ADR-NNN_TITULO.md` | `ADR-006_FEDERATED_CATALOG_AUTHORITY.md` |
| RFC | `RFC-NNN_TITULO.md` | `RFC-002_FEDERATED_CATALOG_PROTOCOL.md` |
| Sprint | `SPR-NNN_TIPO.md` | `SPR-018_OPENING.md` |
| Auditoria | `AUD-NNN_ESCOPO_YYYY-MM-DD.md` | `AUD-003_DOCUMENTATION_2026-10-01.md` |
| Relatório | `RPT-NNN_TIPO_ESCOPO.md` | `RPT-012_HOMOLOGATION_SPR-018.md` |
| Template | `TEMPLATE_FAMILIA.md` | `TEMPLATE_ADR.md` |

Os exemplos não criam nem reservam identificadores.

## 12. Convenção oficial para numeração

- cada família numerada possui sequência própria, crescente e imutável;
- o índice da família é a autoridade de alocação;
- identificadores usam três dígitos (`001`), salvo convenção histórica
  formalmente preservada;
- um número emitido não é reutilizado, mesmo após rejeição, retirada ou erro;
- lacunas são registradas com razão conhecida ou como “não localizado”;
- sufixos (`A`, `B`, `A-001`) só são admitidos quando definidos por política
  específica e não devem nascer para evitar um novo identificador;
- renumerar documentos históricos é proibido sem ato de reconciliação;
- reserva de número expira se a política da família assim determinar, mas o
  registro da reserva permanece auditável;
- o GOV-003 prevalece para ADRs.

## 13. Criação de novos documentos

Um novo documento somente deve ser criado quando:

1. houver finalidade não atendida por documento existente;
2. a família, autoridade e proprietário estiverem identificados;
3. o template aplicável tiver sido usado ou a exceção justificada;
4. não houver duplicação de fonte canônica;
5. identificador tiver sido alocado pelo índice competente;
6. baseline, arquitetura, API e contratos afetados forem declarados;
7. critérios de revisão e ciclo de vida estiverem definidos;
8. referências e confidencialidade tiverem sido verificadas;
9. aprovação aplicável tiver sido obtida.

Notas efêmeras e saídas intermediárias devem permanecer fora das famílias
canônicas e possuir prazo de retenção.

## 14. Alteração de documentos existentes

Alterações são classificadas como:

- **editorial:** ortografia, formatação ou link, sem mudança de sentido;
- **compatível:** esclarece ou amplia sem contrariar a decisão vigente;
- **material:** muda regra, autoridade, fronteira, contrato, status ou decisão.

Alterações editoriais e compatíveis exigem revisão proporcional e registro no
histórico. Alteração material em documento canônico exige instrumento de decisão
aplicável, nova versão ou documento sucessor. Evidência histórica encerrada não
deve ser atualizada para refletir o presente; uma errata vinculada é preferível.

## 15. Arquivamento e preservação histórica

### 15.1 Critérios para arquivamento

Um documento pode ser arquivado quando:

- não participa mais do fluxo ativo;
- sua retenção é obrigatória ou útil;
- autoridade e sucessor estão claros;
- referências de entrada foram inventariadas;
- hash, origem, destino e metadados foram registrados;
- a movimentação não rompe baseline, release, automação ou obrigação legal.

### 15.2 Critérios para preservação histórica

Preservação é obrigatória para:

- documentos de baseline e release;
- ADRs e RFCs com decisão registrada;
- termos, especificações, auditorias e homologações de Sprint;
- relatórios que sustentam aceite, certificação ou métricas publicadas;
- documentos citados por artefato canônico;
- registros necessários à reconstrução de decisão, compatibilidade ou autoria;
- material sujeito a retenção legal, contratual ou de segurança.

Preservação deve manter conteúdo, metadados, hash, relações e legibilidade. A
conversão de formato exige conservar o original ou comprovar equivalência.

## 16. Descontinuação documental

Descontinuação é o processo governado pelo qual um documento deixa de ser
mantido ou utilizado. Ela exige:

1. inventário de consumidores e referências;
2. classificação final (`SUPERSEDED`, `OBSOLETO` ou `ARQUIVADO`);
3. sucessor ou justificativa de ausência;
4. avaliação histórica, legal, contratual e de baseline;
5. aviso e janela de transição quando houver consumidores;
6. aprovação do proprietário e da governança competente;
7. registro no índice e validação de links.

Exclusão física é último recurso e não é autorizada por esta GOV. Documentos
canônicos, evidências de baseline e registros decisórios não podem ser excluídos
por simples obsolescência operacional.

## 17. Mapa documental institucional recomendado

| Necessidade | Fonte recomendada | Índice de navegação |
|---|---|---|
| Estado institucional | `docs/institutional/` | `docs/INDEX.md` |
| Arquitetura vigente e histórica | `docs/architecture/` | `docs/architecture/INDEX.md` quando necessário |
| Atos de governança | `docs/governance/` | `docs/INDEX.md` e índice mestre institucional |
| Decisões arquiteturais | `docs/adr/` | `docs/adr/INDEX.md` |
| Propostas técnicas | `docs/rfc/` | `docs/rfc/INDEX.md` |
| Execução por Sprint | `docs/sprints/` | `docs/sprints/INDEX.md` |
| Evidência de auditoria | `docs/audits/` | índice por objeto |
| Evidência e resultados | `docs/reports/` | índice por finalidade |
| Modelos | `docs/templates/` | README da família |
| Consulta histórica arquivada | `docs/archive/` | `docs/archive/INDEX.md` |
| Elaboração não oficial | `docs/work/` | inventário com responsável e expiração |

O mapa deve registrar para cada documento: identificador, título, caminho,
classificações, status, versão/data, proprietário, baseline relacionada,
antecessor, sucessor e hash quando exigido.

## 18. Política oficial para reorganizações futuras

Nenhuma reorganização física pode ser executada como “limpeza” informal. Toda
reorganização deve ser tratada como migração documental controlada e obedecer a:

- escopo fechado e inventário congelado;
- nenhuma alteração simultânea de conteúdo e localização, salvo correção
  indispensável explicitamente aprovada;
- manifesto origem-destino por arquivo;
- preservação de histórico Git na medida tecnicamente verificável;
- atualização atômica ou faseada de links conforme plano;
- validação automatizada e amostragem humana;
- rollback testado;
- relatório de execução e homologação independente;
- ausência de alteração em código, SDK, API, contratos, testes e baseline, salvo
  autorização distinta e explícita — que não pode ser inferida da reorganização.

Reorganizações amplas devem ocorrer fora do fechamento de release ou baseline e
não podem coexistir com mudanças funcionais no mesmo conjunto de revisão.

## 19. Plano oficial para futura reorganização física

### Fase 0 — autorização

- aprovar escopo, responsáveis, janela, critérios de sucesso e rollback;
- confirmar que a baseline publicada será somente referência, não objeto mutável;
- abrir instrumento próprio sem reutilizar esta GOV como autorização executiva.

### Fase 1 — inventário imutável

- enumerar documentos, caminhos, tamanhos, hashes, status Git e referências;
- identificar arquivos versionados, não versionados, duplicados e externos;
- registrar fotografia assinada ou homologada.

### Fase 2 — classificação humana assistida

- atribuir família e dimensões da seção 5;
- identificar fonte canônica, duplicatas, sucessões, lacunas e conflitos;
- exigir validação humana para autoridade, confidencialidade e descarte.

### Fase 3 — mapa de migração

- produzir tabela origem-destino, ação proposta, justificativa e risco;
- separar movimentos seguros, decisões pendentes e itens bloqueados;
- simular colisões de nomes e links, sem alterar arquivos.

### Fase 4 — piloto reversível

- selecionar conjunto pequeno, não crítico e fora da baseline;
- executar em branch dedicada, com manifesto e rollback;
- validar links, índices, build documental e histórico observável.

### Fase 5 — execução por lotes

- migrar uma família por vez;
- proibir alterações funcionais concorrentes no lote;
- revisar diff, referências, hashes e inventário após cada lote.

### Fase 6 — reconciliação

- atualizar índices e mapas;
- registrar exceções e documentos mantidos no local legado;
- comparar inventários inicial e final, justificando toda diferença.

### Fase 7 — homologação e encerramento

- auditoria independente do plano;
- teste de restauração;
- relatório de execução, riscos residuais e aprovação;
- somente após homologação, declarar a estrutura física como canônica.

## 20. Critérios e gates para execução da reorganização

A execução futura somente pode começar quando todos os gates forem satisfeitos:

| Gate | Critério obrigatório |
|---|---|
| R0 — Autoridade | aprovação formal, proprietário e escopo definidos |
| R1 — Inventário | 100% dos alvos com caminho, hash e status registrados |
| R2 — Classificação | fonte canônica e destino proposto aprovados por humanos |
| R3 — Referências | links, índices, scripts e consumidores inventariados |
| R4 — Segurança | segredos, dados pessoais, permissões e retenção avaliados |
| R5 — Reversibilidade | backup/branch, manifesto e rollback verificados |
| R6 — Piloto | lote piloto aprovado sem perda ou ambiguidade |
| R7 — Execução | diff limitado a movimentos e atualizações autorizadas |
| R8 — Validação | links, inventário, hashes e build documental aprovados |
| R9 — Homologação | relatório independente e aceite institucional emitidos |

Falha em qualquer gate suspende o processo. Automação pode inventariar, comparar
e validar, mas não decidir canonicidade, descarte ou autoridade.

## 21. Política de auditoria documental contínua

### 21.1 Auditoria ao encerramento de cada Sprint

Escopo mínimo:

- completude do termo, especificação, relatório e homologação aplicáveis;
- status e links atualizados;
- rastreabilidade entre requisito, implementação, teste, auditoria e aceite;
- ausência de rascunhos indevidamente citados;
- classificação de temporários e pendências;
- confirmação de que a Sprint não alterou arquitetura ou contrato sem decisão.

Evidência: checklist assinado no relatório de encerramento ou auditoria vinculada.

### 21.2 Auditoria antes de cada Release

Escopo mínimo:

- changelog, notas de release, compatibilidade e migração;
- documentação da API e versão do SDK;
- ADRs/RFCs/Sprints incorporados;
- links, índices e documentos superseded;
- inventário de artefatos e hashes de distribuição;
- segurança, licença, reprodução e rollback.

### 21.3 Auditoria antes de cada Baseline

Escopo mínimo:

- definição exata do corpus que integra a baseline;
- autoridade e status de todos os documentos normativos;
- convergência entre arquitetura, código, API, testes e evidências;
- ausência de documentos de trabalho no corpus;
- árvore limpa ou exceções formalmente registradas;
- tag/identificador, hashes, relatório de execução e recuperação testada.

### 21.4 Auditoria trimestral do repositório

Deve revisar crescimento, duplicatas, links quebrados, diretórios paralelos,
metadados ausentes, documentos sem proprietário, temporários vencidos,
classificações inconsistentes, referências externas e aderência à árvore
canônica. O resultado produz plano de correção, não reorganização automática.

### 21.5 Auditoria anual do patrimônio documental

Deve avaliar valor histórico, autenticidade, legibilidade, retenção, riscos de
formato, confidencialidade, sucessões, cobertura de índices, recuperação e
continuidade institucional. Inclui amostra de restauração e comparação de hashes
dos conjuntos protegidos. Toda proposta de descarte exige decisão separada.

### 21.6 Independência e registro

Quem produz um conjunto pode executar autocheck, mas homologação material deve
ter revisão independente proporcional ao risco. Achados possuem responsável,
severidade, prazo, estado e evidência de fechamento. Auditorias nunca silenciam
divergências para adequar a história ao modelo desejado.

## 22. Checklist obrigatório ao encerramento de toda Sprint

- [ ] Objetivo, escopo e critérios de aceite estão encerrados ou justificados.
- [ ] Termo, especificação, auditoria, implementação e homologação aplicáveis estão vinculados.
- [ ] Status e data de corte são coerentes.
- [ ] ADR/RFC exigido foi aprovado antes da mudança material.
- [ ] Arquitetura, API pública, contratos e baseline afetados foram declarados.
- [ ] Documentos novos seguem família, nome, número e metadados oficiais.
- [ ] Links internos e referências normativas foram verificados.
- [ ] Rascunhos, experimentos e temporários possuem destinação e prazo.
- [ ] Evidências e hashes necessários foram preservados.
- [ ] Documentos superseded apontam sucessores.
- [ ] Nenhum histórico foi reescrito indevidamente.
- [ ] Índices aplicáveis refletem o estado encerrado.
- [ ] Riscos e pendências possuem responsável.
- [ ] A árvore Git e as exceções não versionadas foram registradas.

## 23. Checklist obrigatório antes de toda Release

- [ ] Escopo exato da release e commits integrantes estão identificados.
- [ ] Changelog e notas de release convergem com o conteúdo.
- [ ] Versão do SDK e catálogo da API estão coerentes.
- [ ] Compatibilidade, migração, depreciação e rollback estão documentados.
- [ ] ADRs, RFCs e Sprints incorporados possuem status válido.
- [ ] Testes, auditorias, certificações e homologações estão vinculados.
- [ ] Documentação de uso, segurança e operação está atualizada.
- [ ] Índices e links foram validados.
- [ ] Artefatos de distribuição possuem hashes reproduzíveis.
- [ ] Segredos, temporários e dados indevidos estão ausentes.
- [ ] Documentos históricos e superseded foram preservados.
- [ ] Exceções foram aprovadas e possuem prazo.

## 24. Checklist obrigatório antes de toda Baseline

- [ ] A autoridade que institui a baseline está identificada.
- [ ] O corpus documental e técnico está enumerado sem ambiguidade.
- [ ] Arquitetura, governança, ADRs, RFCs e evidências convergem.
- [ ] SDK, API pública, contratos, testes e comportamento estão caracterizados.
- [ ] Todos os documentos do corpus são canônicos ou evidências explicitamente aceitas.
- [ ] Nenhum documento `TRABALHO`, `EXPERIMENTAL` ou `TEMPORÁRIO` integra o corpus normativo.
- [ ] Estados `SUPERSEDED`, `OBSOLETO`, `LEGADO` e `ARQUIVADO` estão explícitos.
- [ ] Links, índices, nomes, números e metadados foram auditados.
- [ ] Inventário, hashes, tag proposta e procedimento de recuperação estão disponíveis.
- [ ] Regressão, build e verificações documentais foram executados conforme o plano.
- [ ] Estado Git e itens não versionados foram registrados e decididos.
- [ ] Riscos residuais e divergências estão declarados.
- [ ] Relatório de baseline e homologação independente estão aprovados.

## 25. Política de critérios periódicos e indicadores

As auditorias devem acompanhar, no mínimo:

- documentos por família e classificação;
- percentual com metadados mínimos;
- documentos sem proprietário ou revisão;
- links quebrados e referências externas indisponíveis;
- duplicatas exatas e candidatas semânticas;
- temporários vencidos;
- documentos superseded sem sucessor;
- lacunas e colisões de numeração;
- divergências entre índices e filesystem;
- tempo para localizar a fonte canônica;
- achados abertos por severidade e idade.

Metas devem ser aprovadas separadamente. Métrica não autoriza exclusão nem
reclassificação automática.

## 26. Riscos e controles

| Risco | Impacto | Controle obrigatório |
|---|---|---|
| Perda de história em “limpeza” | decisões e evidências irrecuperáveis | preservação, manifesto, hash e rollback |
| Fonte canônica ambígua | decisões conflitantes | índice, autoridade e vínculo de supersessão |
| Links quebrados após movimento | perda de rastreabilidade | inventário de referências e validador antes/depois |
| Renomeação massiva mistura mudanças | revisão impraticável | lotes por família e diff exclusivo |
| Status inferido pela pasta | falsa autoridade | metadados e registro canônico |
| Duplicatas divergentes | uso da versão errada | fonte única e aliases/referências controlados |
| Automação decide descarte | perda ou violação institucional | validação humana obrigatória |
| Arquivo vira depósito | crescimento sem governança | retenção, índice e auditoria anual |
| Temporários permanentes | ruído e risco de dados | proprietário, expiração e auditoria trimestral |
| Mudança física afeta baseline | quebra de reprodução | baseline imutável e migração fora de seu corpus |
| Convenções retroativas apagam contexto | história artificial | exceções legadas documentadas |
| Dados sensíveis em documentos | exposição | classificação, revisão e menor privilégio |

## 27. Impactos arquiteturais

### 27.1 Impactos imediatos

Os impactos imediatos são exclusivamente documentais:

- cria linguagem comum para autoridade e ciclo de vida;
- define destino canônico para novos documentos;
- institui auditorias e checklists;
- estabelece gates para eventual reorganização.

Não há impacto imediato em código, módulos, namespaces, dependências, SDK, API,
contratos, testes, persistência, runtime ou baseline.

### 27.2 Impactos futuros condicionais

Uma reorganização aprovada poderá melhorar descoberta, onboarding, validação de
links, automação documental e composição de releases. Poderá exigir atualização
de referências, índices e pipelines documentais, sempre sem mudança semântica.
Qualquer efeito técnico material exige instrumento próprio e não decorre desta GOV.

### 27.3 Compatibilidade arquitetural

A organização proposta preserva Domain First, Ports and Adapters, dependências
para dentro, governança soberana, evidência antes de automação, preservação do
legado, evolução incremental e autoridade na fonte. A separação documental entre
Core, ecossistema, governança, decisões e evidências reflete as fronteiras já
instituídas sem criar componentes técnicos.

## 28. Compatibilidade com a documentação vigente

| Instrumento | Compatibilidade da GOV-007 |
|---|---|
| CKO-GOV-001 | preserva Baseline Arquitetural 1.0, autoridade institucional, evolução incremental, versionamento e critérios formais de mudança |
| GOV-002 | não executa ondas II.0–II.7, não atravessa gates D0–D7 e não autoriza ADR, RFC, Sprint ou implementação |
| GOV-003 | adota inventário, índice, identificador imutável, estados explícitos e preservação de ADRs; o GOV-003 prevalece nessa família |
| GOV-005 | preserva auditoria, método, limitações, métricas e evidências como patrimônio histórico; não reestima esforço |
| GOV-006 | operacionaliza o mapa documental e a distinção entre baseline publicada, estado presente e registros históricos, sem substituir o dossiê |
| CKO-ARCH-001 | mantém monólito modular, Core compartilhado, infraestrutura substituível, aplicações consumidoras, legado e governança |
| CKO-ARCH-002 | mantém federação governada, composição externa, Provenance by Design, autoridade na fonte e evolução reversível |
| `CKO-BASELINE-2026.07` | trata a baseline como publicada e imutável; a GOV-007 é posterior e não altera seu corpus, tag, SDK 1.0.0 ou 646 exports |

## 29. Exceções e divergências

Uma exceção à estrutura deve registrar: regra excepcionada, justificativa,
responsável, risco, prazo, compensação e autoridade aprovadora. Exceção não cria
precedente automático. Divergências atuais, inclusive diretórios sinônimos,
documentos na raiz, nomes históricos e artefatos fora da árvore recomendada, são
estado observado a ser inventariado; esta GOV não os corrige nem os condena
retroativamente.

## 30. Critérios de conformidade

Um documento novo está conforme quando possui família correta, nome e número
válidos, metadados mínimos, autoridade/status explícitos, referências íntegras,
proprietário, classificação, compatibilidade e registro no índice aplicável.

Um repositório está documentalmente conforme quando é possível identificar, sem
ambiguidade, a fonte canônica de cada matéria; reconstruir decisões e baselines;
distinguir ativo de histórico e oficial de trabalho; auditar temporários,
sucessões e exceções; e restaurar o patrimônio protegido.

## 31. Declaração final

A GOV-007 institui o padrão de organização documental do CKO e passa a orientar
todo novo documento e todo planejamento de reorganização. A árvore proposta é
normativa como destino, mas não representa estado físico já executado.

Este processo criou somente
`docs/governance/GOV-007_REPOSITORY_CANONICAL_ORGANIZATION.md`. Nenhum arquivo
preexistente foi movido, renomeado, removido ou modificado; nenhum código, SDK,
API pública, contrato, teste, comportamento ou baseline foi alterado; nenhuma
Sprint, ADR, RFC ou commit foi criado.

## Referências institucionais

- `../../../docs/governance/CKO-GOV-001_BASELINE_ARQUITETURAL_1.0.md`
- `../../../docs/arquitetura/CKO-ARCH-001_ARQUITETURA_CANONICA.md`
- `../arquitetura/CKO-ARCH-002_ECOSYSTEM_EVOLUTION_ARCHITECTURE.md`
- `GOV-002_CYCLE_II_EXECUTION_PROGRAM.md`
- `GOV-003_ADR_GOVERNANCE_RECONCILIATION.md`
- `../../GOV-005_PROJECT_EFFORT_AUDIT.md`
- `GOV-006_PROJECT_DOSSIER.md`
- `../adr/INDEX.md`
- `../../ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md`
- `../../CKO_CORE_BASELINE_EXECUTION_REPORT.md`
