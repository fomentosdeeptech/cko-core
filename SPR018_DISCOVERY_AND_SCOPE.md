# SPR-018 — Descoberta e delimitação controlada de escopo

## 1. Status deste documento

**CAMINHO C — SPR-018 NÃO DEFINIDA.**

Este documento registra uma descoberta documental. Ele não constitui termo de abertura, especificação técnica aprovada, autorização de implementação ou escolha automática de módulo. O nome “SPR-018” é apenas o identificador sequencial sob investigação; não há nome oficial canônico localizado.

## 2. Precondição atendida

A SPR-017 foi homologada no `SPR017_HOMOLOGATION_REPORT.md`.

- Decisão: **SPR-017 homologada tecnicamente.**
- Relatório de homologação: SHA-256 `A7D062962AFD016EED784F17FD8C3A6D766CCB938D8AA83C746665AC3E2C4C13`.
- Repositório: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`.
- Branch/HEAD: `main` / `e94545919db97a071f08de2c08ce1a5dde06980e`.

## 3. Fontes canônicas consultadas

Foram consultados integralmente, quando existentes e relevantes à evolução:

- `README.md`, `ROADMAP.md` e `CHANGELOG.md`;
- `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md`;
- `CKO_CORE_V1_ARCHITECTURE_DECISION.md`;
- `CKO_CORE_V1_ARCHITECTURE_MAP.md`;
- `CKO_CORE_V1_DEPENDENCY_MATRIX.md`;
- `CKO_CORE_V1_PUBLIC_API_CATALOG.md`;
- índice e ADRs em `docs/adr`, `docs/decisoes` e o relatório em `docs/governance`;
- auditoria e relatório da SPR-016;
- auditorias, especificação, verificação final, relatório de implementação e relatório de homologação da SPR-017;
- contratos e fachada pública efetivos do CORE.

Também foi feita busca mecânica no CORE e no repositório pai por `SPR-018`, `CKO-RFC-001`, `PWAM`, `Project Workspace Automation`, termos de próxima Sprint, backlog e autorização. No repositório pai foram consultados `README.md`, `docs/arquitetura/INDEX.md`, `docs/arquitetura/CKO-RFC-001_PROJECT_WORKSPACE_AUTOMATION_MODULE.md` e `docs/governance/ROADMAP_EXECUTION.md`.

A CKO-RFC-001 existe no repositório pai, está indexada no README, no índice de arquitetura e no roadmap, e declara status **Proposta**, prioridade **Baixa**, horizonte **Roadmap futuro** e implementação **Não autorizada**. Ela não cria, define ou reserva a SPR-018. Não foi localizado índice canônico de Sprints posterior à SPR-017, termo de abertura, especificação ou autorização da SPR-018.

## 4. Estado atual do CORE

- CORE SDK declarado: `1.0.0`.
- Camada semântica implementada no worktree: Knowledge Object, Document, Relationship, Graph, Query, Index, Corpus e Provenance Statement, correspondentes às SPR-010–017.
- API efetiva após a SPR-017: 646 exports raiz, únicos e resolvidos.
- A arquitetura v1.2 é anterior às SPR-010–017 e registra apenas autorização genérica para iniciar a Camada Semântica após a SPR-009A.
- O roadmap raiz termina na Sprint 003 e não governa a sequência atual.
- A documentação transversal ainda contém contagens antigas de 334/346 exports, matriz incompleta e mojibake, divergências já registradas pela SPR-017.
- O worktree permanece deliberadamente sujo e a governança de baseline ainda exige validação humana dos numerosos arquivos não rastreados.

## 5. Resultado da identificação

| Questão | Resultado |
|---|---|
| A SPR-018 existe documentalmente? | Não foi localizada definição canônica suficiente; a CKO-RFC-001 não a define. |
| Nome oficial | Ausente. |
| Objetivo oficial | Ausente. |
| Fundação ou módulo | Não definido. |
| Dependências próprias | Não definidas. |
| Baseline da SPR-018 | Não formalizado; o estado técnico atual é SPR-017 homologada sobre `main`/HEAD indicado. |
| Autorização vigente | Ausente. |
| Especificação técnica | Ausente. |
| Especificação aprovada | Não aplicável; não existe. |
| Implementação autorizada | Não. |
| CKO-RFC-001 / PWAM | Proposta existente no repositório pai; implementação não autorizada; não corresponde à SPR-018. |

Conclusão: a numeração sequencial não fornece escopo. Nenhuma fundação, símbolo, modelo, serviço ou critério de produto pode ser escolhido sem decisão humana e novo gate arquitetural.

## 6. Informação canônica, inferência e lacunas

### 6.1 Informação canônica

1. ARCH-001 v1.2 autoriza genericamente a Camada Semântica após a homologação da SPR-009A, sem enumerar componentes posteriores à SPR-009A.
2. As SPR-010–017 implementaram sucessivamente oito fundações semânticas; cada relatório proíbe antecipar Sprint posterior.
3. ARCH-001 v1.2 mantém no backlog temas P2 de uniformização de eventos, cobertura por módulo, isolamento de temporários e política transversal de configuração e segurança.
4. A SPR-017 registra como dependências documentais externas a reconciliação do catálogo, arquitetura, matriz, versão residual e mojibake.
5. A governança de baseline exige validação humana antes de uma baseline oficial do worktree atual.

### 6.2 Inferências permitidas, mas não decisões

- A homologação da SPR-017 torna tecnicamente possível abrir um gate de descoberta posterior.
- A reconciliação documental/release e o isolamento de temporários são necessidades concretas, porém nenhum documento as nomeia como SPR-018.
- Qualquer nova fundação semântica exigirá primeiro uma auditoria de lacuna semelhante às realizadas para Corpus e Provenance.

### 6.3 Lacunas documentais

- inexistência de roadmap corrente para SPR-018;
- inexistência de backlog canônico nominal para o próximo componente;
- inexistência de termo de abertura, sponsor/autoridade e decisão arquitetural;
- inexistência de nome, problema, fronteiras, dependências e critérios aprovados;
- inexistência de especificação e autorização de implementação;
- documentação transversal desatualizada em relação aos 646 exports;
- baseline Git ainda não formalizada apesar do volume de trabalho não rastreado.

## 7. Alternativas derivadas das fontes

As alternativas abaixo são propostas para decisão; nenhuma é a SPR-018 oficial.

### Alternativa A — Consolidação documental e de release da Camada Semântica

Origem: divergências explícitas da SPR-017 e documentação transversal anterior às SPR-010–017.

Problema candidato: catálogo, ARCH, matriz e documentação de versão não representam a API efetiva de 646 exports e as fundações SPR-010–017.

Dependências: inventário mecânico da API, mapas de dependência, decisões SemVer, preservação dos contratos 1.0.0 e baseline Git validada.

Fronteira: documentação, inventário e certificação; não autoriza alterar comportamento de domínio.

### Alternativa B — Hardening transversal P2 do CORE

Origem: backlog normativo da seção 20 da ARCH-001 v1.2.

Problemas candidatos: uniformização de eventos, cobertura por módulo, isolamento de temporários e política transversal de configuração/segurança.

Dependências: escolha humana de um único problema, análise de impacto sobre contratos homologados e especificação própria. Esses temas não devem ser agrupados automaticamente em uma Sprint ampla.

Fronteira: ainda indefinida; cada tema pode exigir Sprint independente.

### Alternativa C — Nova fundação semântica ainda não identificada

Origem: autorização arquitetural genérica da Camada Semântica.

Problema candidato: somente uma lacuna comprovada por inventário dos contratos SPR-010–017.

Dependências: decisão humana sobre a capacidade de produto pretendida, auditoria pré-implementação read-only, análise de sobreposição e aprovação formal do nome/responsabilidade.

Fronteira: nenhum módulo ou API pode ser proposto antes da auditoria de lacuna.

### Alternativa D — Formalização da baseline e governança do worktree

Origem: `BASELINE_PREPARATION_REPORT.md` e estado Git atual.

Problema candidato: código, testes e documentação permanecem majoritariamente não rastreados sobre um HEAD anterior, reduzindo a rastreabilidade de baselines futuros.

Dependências: decisão humana de inclusão/exclusão, sem commit automático nesta execução.

Fronteira: governança e preparação de baseline; não altera contratos técnicos.

## 8. CKO-RFC-001 e PWAM

A **CKO-RFC-001 — Project Workspace Automation Module (PWAM)** foi localizada em `../docs/arquitetura/CKO-RFC-001_PROJECT_WORKSPACE_AUTOMATION_MODULE.md`, no repositório pai do CORE. Ela está indexada na arquitetura, na governança e no roadmap do repositório pai, mas permanece uma proposta não autorizada. A própria RFC declara que sua presença no roadmap não cria sprint, não reserva numeração e não autoriza implementação.

A CKO-RFC-001 não define a SPR-018, e não foi feita associação entre PWAM e SPR-018. Não foi criado namespace, módulo, requisito, arquitetura ou plano de implementação de PWAM. A existência do `cko.core.workspace` homologado desde a SPR-008OA também exige análise explícita de sobreposição antes de qualquer proposta futura nessa área.

## 9. Fronteiras e impactos preliminares

Enquanto não houver escolha humana:

- nenhuma mudança de API é autorizada;
- nenhum novo export, namespace, modelo, enum, serviço ou exceção é proposto;
- nenhum impacto SemVer é definido;
- contratos SPR-010–017 e os 646 exports permanecem baseline de preservação técnica;
- não há autorização para código, testes, dependências, migrações, build de release ou alteração de documentação normativa existente.

## 10. Riscos

1. escolher escopo pela sequência numérica e criar arquitetura sem autoridade;
2. confundir backlog P2 com prioridade aprovada;
3. transformar divergência documental em mudança de comportamento;
4. duplicar `cko.core.workspace` por meio de PWAM;
5. iniciar nova fundação sem demonstrar lacuna e sobreposição;
6. definir baseline sobre worktree não formalizado;
7. declarar autorização a partir de documento histórico ou genérico.

## 11. Requisitos preliminares do próximo gate

Estes requisitos governam a decisão, não o produto ainda indefinido:

1. selecionar explicitamente uma alternativa ou fornecer outro escopo canônico;
2. nomear autoridade decisora e sponsor;
3. definir problema, objetivo, fronteiras e exclusões;
4. registrar baseline Git/API/documental;
5. realizar auditoria de lacuna e sobreposição;
6. identificar dependências e direção de imports;
7. decidir impacto SemVer e documentação a atualizar;
8. produzir especificação técnica com oráculos verificáveis;
9. submeter a especificação a auditoria formal independente;
10. emitir autorização explícita e separada para implementação.

## 12. Critérios preliminares de aceite do gate de definição

- nome oficial inequívoco;
- problema e responsabilidade exclusiva aprovados;
- ausência de duplicidade com SPR-010–017 e módulos legados;
- baseline e autoridade registradas;
- fronteiras dentro/fora do escopo fechadas;
- dependências e retrocompatibilidade aprovadas;
- critérios técnicos mensuráveis e vetores/oráculos quando aplicáveis;
- especificação aprovada por auditoria independente;
- autorização de implementação textual, vigente e inequívoca.

## 13. Documentação ainda necessária

1. decisão humana de escopo da SPR-018;
2. termo formal de abertura;
3. auditoria arquitetural pré-implementação;
4. especificação técnica;
5. relatório independente de aprovação da especificação;
6. autorização de implementação, caso aprovada;
7. plano de execução somente após os gates anteriores.

## 14. Autorização e recomendação

Situação da autorização: **ausente**.

Próximo gate recomendado: **Gate humano de seleção e autorização de descoberta**, escolhendo uma das alternativas ou fornecendo fonte canônica adicional. Após a escolha, executar auditoria arquitetural read-only e produzir termo de abertura/especificação. Implementação continua proibida.

Nenhuma implementação da SPR-018 foi iniciada nesta execução.

