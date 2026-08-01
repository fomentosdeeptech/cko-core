# CKO CORE — Relatório de Consolidação da Baseline

**Data do gate:** 2026-07-31  
**Resultado:** **CONSOLIDAÇÃO BLOQUEADA**  
**Única alteração autorizada desta execução:** criação deste relatório.

## 1. Identificação dos repositórios e limites Git

| Escopo | Caminho | Existe | Limite Git | Branch | HEAD |
|---|---|---:|---|---|---|
| Repositório principal CKO | `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO` | sim | não é repositório Git | N/A | N/A |
| CKO CORE | `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE` | sim | raiz Git canônica | `main` | `e94545919db97a071f08de2c08ce1a5dde06980e` |

O HEAD e a branch do CORE coincidem com a baseline informada. Como o diretório pai não possui metadados Git, é possível reconciliar seu conteúdo atual, mas não provar por Git quais arquivos do pai foram adicionados ou alterados, nem atribuir branch/HEAD.

## 2. Estado inicial do Git

Comando de referência: `git status --porcelain=v1 --untracked-files=all`.

- 461 entradas visíveis: 2 modificadas, 459 não rastreadas, 0 adicionadas ao índice, 0 removidas e 0 renomeadas.
- Modificadas: `.gitignore` e `pyproject.toml`.
- Nenhuma alteração estava staged.
- O relatório de homologação registrava 459 entradas no início daquele gate (2 modificadas + 457 não rastreadas). As duas entradas posteriores são `SPR017_HOMOLOGATION_REPORT.md` e `SPR018_DISCOVERY_AND_SCOPE.md`, coerentes com seus timestamps e conteúdo.
- Há ainda 3.357 entradas ignoradas: 3.336 sob `runtime/`, 9 sob `logs/`, 8 módulos em `src/cko/core/runtime/`, 2 ZIPs de inventário na raiz, 1 configuração VS Code e 1 JSON de relatório. Elas não compõem as 461 entradas acima.

## 3. Cadeia documental da SPR-017

| Documento | SHA-256 esperado | SHA-256 encontrado | Resultado |
|---|---|---|---|
| `SPR017_HOMOLOGATION_REPORT.md` | `A7D062962AFD016EED784F17FD8C3A6D766CCB938D8AA83C746665AC3E2C4C13` | igual | confirmado |
| `SPR017_IMPLEMENTATION_REPORT.md` | `6EFF3E326D379CAE109BCE9B06FBC7B9D5F34A985D64378B49F98B57A2FF2EA0` | igual | confirmado |
| `SPR017_TECHNICAL_SPECIFICATION.md` | `D19FA36A85F9BB761A11E65EC32D4D39A9C8BB8DFD290F621101488DB0B4862D` | igual | confirmado |

A homologação não foi reaberta: não foram executados testes, cobertura, vetores, build, instalação, smoke test nem nova auditoria.

## 4. Metodologia

A classificação cruzou estado Git, diffs dos dois arquivos rastreados, conteúdo dos relatórios e auditorias, termos de abertura, testes dedicados, imports/diretórios de produção, documentos de arquitetura/governança e fontes do repositório pai. Nome de arquivo foi usado somente como índice; a atribuição dependeu de conteúdo e fontes correlatas. Itens sem evidência suficiente foram mantidos fora de commits.

## 5. Contagem por categoria — inventário inicial visível

| Categoria | Descrição | Quantidade |
|---|---|---:|
| A | Implementação homologada SPR-017 | 17 |
| B | Documentação SPR-017 | 13 |
| C | SPR-010–016 comprovadas | 124 |
| D | Outras sprints/fundações | 273 |
| E | Documentação transversal CORE | 25 |
| F | Alterações do repositório pai | N/D (CKO pai não é Git) |
| G | Artefatos de teste/build/instalação | 4 |
| H | Temporários/reproduzíveis | 3 |
| I | Preexistentes sem vínculo suficiente | 0 |
| J | Potencialmente indevidos/estranhos | 1 |
| K | Remoções | 0 |
| L | Exigem decisão humana | 1 |

Total das categorias contáveis A–E e G–L: **461**. A categoria F não pode ser quantificada como alteração porque o repositório pai não é Git.

## 6. SPR-017 identificada

Implementação homologada (17): `src/cko/core/__init__.py`, os 15 módulos de `src/cko/core/provenance/` e `tests/test_knowledge_provenance_statement_foundation_spr017.py`.

Documentação (13): os seis `CKO_PROVENANCE_STATEMENT_*.md` e os sete `SPR017*.md` inventariados no Apêndice A. A fachada `src/cko/core/__init__.py` é cumulativa e foi alterada por várias sprints; sua classificação primária como SPR-017 reflete o estado final com 646 exports, e o commit proposto C09 depende de C01–C08.

## 7. Outras sprints e documentação transversal

- SPR-010–016: 124 arquivos, separados por namespace, suíte dedicada, documentação e relatório.
- SPR-003–009A/fundações: 273 arquivos visíveis, incluindo legado preservado, infraestrutura do CORE, Discovery, Execution, Connector, Storage, Filesystem, SQLite, Checkpoint, UoW, scripts, testes e relatórios.
- Documentação transversal: 25 arquivos. `SPR018_DISCOVERY_AND_SCOPE.md` deve ficar fora dos commits porque afirma não ter localizado a CKO-RFC-001, embora a RFC exista atualmente no repositório pai e esteja indexada no README, índice arquitetural e roadmap.
- Repositório pai: quatro fontes correntes foram reconciliadas (`README.md`, `docs/arquitetura/INDEX.md`, `docs/arquitetura/CKO-RFC-001_PROJECT_WORKSPACE_AUTOMATION_MODULE.md` e `docs/governance/ROADMAP_EXECUTION.md`), mas seu histórico de alteração é indeterminável sem Git.

## 8. Artefatos ignorados, temporários e reproduzíveis

O inventário ignorado contém:

- `runtime/reports/`: 1.824 entradas;
- `runtime/temp/`: 1.498 entradas;
- `runtime/installations/`: 5;
- `runtime/database/`: 5;
- `runtime/checkpoints/`: 1;
- `runtime/graph/`: 1;
- `runtime/.gitkeep`: 1;
- `runtime/cko.db`: 1;
- `logs/`: 9;
- `CKO_SPR_003_INVENTARIO_SEGURO.zip` e `CKO_SPR_004_INVENTARIO_CANONICO.zip`;
- `.vscode/settings.json`;
- `reports/SPR007B_ADVANCED_REPORT.json`.

Esses artefatos permanecem fora dos commits propostos. Não foram apagados. Os quatro arquivos `src/cko.egg-info/*` visíveis também são metadata reproduzível e ficam fora.

Exceção crítica: a regra `runtime/` do `.gitignore` não está ancorada e oculta indevidamente oito módulos de produção documentados pela SPR-008Q:

1. `src/cko/core/runtime/__init__.py`
2. `src/cko/core/runtime/cancellation.py`
3. `src/cko/core/runtime/errors.py`
4. `src/cko/core/runtime/lifecycle.py`
5. `src/cko/core/runtime/models.py`
6. `src/cko/core/runtime/resources.py`
7. `src/cko/core/runtime/runtime.py`
8. `src/cko/core/runtime/validator.py`

Eles devem integrar C01, depois de uma correção deliberada da política de ignore em gate separado. Isso é bloqueio objetivo porque um commit convencional omitiria produção homologada.

## 9. Itens fora dos commits e decisões humanas

Permanecem fora: `.vscode/extensions.json`, `.vscode/tasks.json`, `.vscode/settings.json`, `inventory.txt`, `src/cko.egg-info/*`, `src/main.py.txt`, `SPR018_DISCOVERY_AND_SCOPE.md`, todos os artefatos ignorados listados na seção 8 e, provisoriamente, `.gitignore`.

Decisões necessárias:

1. aprovar correção ancorada do ignore operacional (por exemplo, `/runtime/`) sem ocultar `src/cko/core/runtime/`;
2. decidir a destinação de `src/main.py.txt`, duplicata textual de um entrypoint sem vínculo canônico suficiente;
3. autorizar ou rejeitar as mudanças de governança em `.gitignore`;
4. corrigir/reemitir ou excluir da baseline `SPR018_DISCOVERY_AND_SCOPE.md`, pois sua conclusão sobre ausência da RFC está desatualizada;
5. decidir se o repositório pai deve receber Git próprio ou outro mecanismo de proveniência;
6. aprovar formalmente o plano C01–C10 antes de qualquer staging.

## 10. Divergências documentais

| Fonte | Encontrado | Esperado atual | Impacto | Ação recomendada |
|---|---|---|---|---|
| `CKO_CORE_V1_PUBLIC_API_CATALOG.md` | 334 exports; pacote 0.1.0 | 646 exports; 1.0.0 | catálogo factual obsoleto | atualizar em atividade documental |
| `CKO_CORE_V1_ARCHITECTURE_MAP.md` | 334 exports | 646 | mapa não cobre camada semântica completa | atualizar |
| `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md` | 346 exports | 646 | arquitetura normativa anterior às SPR-010–017 | publicar revisão controlada |
| `CKO_CORE_V1_DEPENDENCY_MATRIX.md` | adendo até SPR-016; sem Provenance Statement | incluir SPR-017 | matriz incompleta | adicionar dependências SPR-017 |
| `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md` e v1.1 | distribuição 0.1.0 | histórico claramente marcado; corrente 1.0.0 | risco de leitura como vigente | manter como histórico e reforçar índice |
| `README.md`, `CHANGELOG.md`, `ROADMAP.md` do CORE | mojibake; roadmap só SPR-001–003; changelog v2.0 genérico | estado até SPR-017 / SDK 1.0.0 | navegação e governança desatualizadas | reconciliar após baseline |
| `SPR018_DISCOVERY_AND_SCOPE.md` | RFC-001 “não encontrada” | RFC existe no pai e está indexada | conclusão de discovery desatualizada | não consolidar antes de revisão |

O estado técnico de 646 exports é evidenciado pelos relatórios de implementação/homologação SPR-017; não foi reexecutado.

## 11. CKO-RFC-001 — PWAM

Localização: `CKO/docs/arquitetura/CKO-RFC-001_PROJECT_WORKSPACE_AUTOMATION_MODULE.md`. Status expresso: **Proposta**, prioridade **Baixa**, horizonte **Roadmap futuro**, implementação **Não autorizada**, versão documental 0.1. Há referências no README pai, índice arquitetural e roadmap. A RFC define PWAM como capacidade de aplicação, proíbe ampliação implícita do CORE e exige rito próprio para promoção de contratos. Não há documento posterior localizado que autorize implementação. PWAM não é SPR-018 e não foi implementado.

## 12. Plano de consolidação Git — não executar neste gate

| ID | Conteúdo exato | Mensagem proposta | Dependência |
|---|---|---|---|
| C01 | todas as linhas do Apêndice A marcadas C01 + os oito módulos SPR-008Q da seção 8 | `chore(core): consolidate foundations through SPR-009A` | decisões 1 e 3 |
| C02 | linhas C02 | `feat(core): consolidate SPR-010 knowledge object foundation` | C01 |
| C03 | linhas C03 | `feat(core): consolidate SPR-011 document model` | C02 |
| C04 | linhas C04 | `feat(core): consolidate SPR-012 relationships` | C03 |
| C05 | linhas C05 | `feat(core): consolidate SPR-013 graph` | C04 |
| C06 | linhas C06 | `feat(core): consolidate SPR-014 query` | C05 |
| C07 | linhas C07 | `feat(core): consolidate SPR-015 index` | C06 |
| C08 | linhas C08 | `feat(core): consolidate SPR-016 corpus` | C07 |
| C09 | linhas C09 | `feat(core): consolidate homologated SPR-017 provenance` | C08 |
| C10 | linhas C10 + este relatório após aprovação | `docs(core): consolidate architecture and baseline governance` | C09; divergências resolvidas ou registradas |

Não é seguro formar um único commit: há trabalhos de múltiplas sprints, arquivo cumulativo de fachada, produção ocultada por ignore, documentação divergente e itens locais/estranhos. O Apêndice A é a delimitação exata: nenhum glob é autorização de inclusão.

Verificações mínimas antes de qualquer commit futuro: reemitir status completo incluindo ignorados; confirmar que os oito módulos Runtime ficaram visíveis; revisar staging por ID; confirmar ausência dos itens FORA; verificar imports/exports e testes proporcionais ao commit. Após C09: executar a regressão canônica e verificar os 646 exports somente em gate autorizado. Após C10: recalcular hashes documentais e confirmar links/contagens.

## 13. Avaliação da proposta SPR-018

“SPR-018 — Consolidação Arquitetural, Documental e de Release da Camada Semântica” resolve lacunas reais (646 exports versus 334/346, matriz sem SPR-017, índices/roadmap/changelog residuais) e é compatível com a arquitetura se permanecer estritamente documental/release, sem mudar contratos. As dependências não estão satisfeitas enquanto a baseline Git estiver bloqueada.

Recomendação principal: tratar primeiro a formação controlada da baseline como gate próprio. Depois, abrir termo de atividade de release/documentação; só chamá-la de SPR-018 mediante decisão humana explícita. Se receber número de sprint, exige termo de abertura, especificação documental, critérios e auditoria de lacunas. Não conflita tecnicamente com a RFC-001 porque PWAM é aplicação futura não autorizada, mas a distinção deve constar formalmente. A descoberta atual registra “CAMINHO C — SPR-018 NÃO DEFINIDA” e está factual/documentalmente desatualizada quanto à existência da RFC no pai.

Próximo gate recomendado: **gate humano de desbloqueio da baseline**, limitado às seis decisões da seção 9; depois, execução controlada C01–C10. Não implementar SPR-018 nem PWAM.

## 14. Parecer

**CONSOLIDAÇÃO BLOQUEADA.**

Bloqueios objetivos:

- regra `runtime/` oculta oito módulos de produção SPR-008Q;
- `.gitignore` exige decisão/correção antes da baseline;
- `src/main.py.txt` tem origem não comprovada;
- `SPR018_DISCOVERY_AND_SCOPE.md` diverge do estado documental atual do pai;
- o repositório pai não oferece histórico Git para provar suas alterações;
- staging ainda não foi autorizado e os grupos dependem das decisões acima.

Nenhuma alteração preexistente precisa ser descartada.

## 15. Estado final e integridade da execução

Após a criação deste relatório, o estado esperado é 462 entradas visíveis: 2 modificadas e 460 não rastreadas, sendo este relatório a única entrada nova desta execução. Nenhum arquivo existente foi alterado; código, testes e documentação homologada permaneceram intactos. Não houve `git add`, commit, push, pull request, reset, clean, restore, checkout, stash, rebase, merge ou cherry-pick. SPR-018 e PWAM não foram implementados.

O SHA-256 dos bytes finais deste relatório é calculado depois de sua gravação e registrado externamente no fechamento do gate. Esse é o padrão documental vigente, pois inserir o hash integral dentro do próprio arquivo criaria autorreferência impossível.

## Apêndice A — inventário completo das 461 alterações visíveis no estado inicial

Legenda: ` M` = rastreado modificado; `??` = não rastreado; `FORA` = não incluir em commit.

| ID | Git | Cat. | Origem/atividade | Natureza | Evidência | Ação | Commit | Caminho |
|---:|:---:|:---:|---|---|---|---|:---:|---|
| 001 | ` M` | L | atividade de baseline; decisão humana | governança Git | diff Git + BASELINE_PREPARATION_REPORT.md | não consolidar antes de corrigir/decidir | FORA | `.gitignore` |
| 002 | ` M` | D | SPR-008A/009A | configuração/manifesto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `pyproject.toml` |
| 003 | `??` | H | ambiente local/reproduzível | configuração/manifesto | BASELINE_PREPARATION_REPORT.md e natureza local | manter fora | FORA | `.vscode/extensions.json` |
| 004 | `??` | H | ambiente local/reproduzível | configuração/manifesto | BASELINE_PREPARATION_REPORT.md e natureza local | manter fora | FORA | `.vscode/tasks.json` |
| 005 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md` |
| 006 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.1.md` |
| 007 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.2.md` |
| 008 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `ARQUITETURA_ATUAL.txt` |
| 009 | `??` | D | SPR-008OA | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `CKO_BUILD.cmd` |
| 010 | `??` | D | SPR-008OA | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `CKO_CLEAN.cmd` |
| 011 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_ARCHITECTURE_DECISION.md` |
| 012 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_ARCHITECTURE_MAP.md` |
| 013 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_COMPOSITION_ROOT.md` |
| 014 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_DEPENDENCY_MATRIX.md` |
| 015 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_EXCEPTION_CATALOG.md` |
| 016 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_EXCEPTION_HIERARCHY.md` |
| 017 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_GAP_ANALYSIS.md` |
| 018 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_LOGGING_EVENT_CATALOG.md` |
| 019 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_PUBLIC_API_CATALOG.md` |
| 020 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_RELEASE_CERTIFICATION.md` |
| 021 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_SEMANTIC_READINESS_REPORT.md` |
| 022 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `CKO_CORE_V1_TEST_AND_COVERAGE_REPORT.md` |
| 023 | `??` | C | SPR-016 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `CKO_CORPUS_API.md` |
| 024 | `??` | C | SPR-016 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `CKO_CORPUS_ARCHITECTURE.md` |
| 025 | `??` | C | SPR-016 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `CKO_CORPUS_MODEL_GUIDE.md` |
| 026 | `??` | C | SPR-016 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `CKO_CORPUS_OPERATIONS.md` |
| 027 | `??` | C | SPR-016 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `CKO_CORPUS_SERIALIZATION.md` |
| 028 | `??` | C | SPR-011 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `CKO_DOCUMENT_API.md` |
| 029 | `??` | C | SPR-011 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `CKO_DOCUMENT_MODEL_ARCHITECTURE.md` |
| 030 | `??` | C | SPR-011 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `CKO_DOCUMENT_MODEL_GUIDE.md` |
| 031 | `??` | C | SPR-011 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `CKO_DOCUMENT_SERIALIZATION.md` |
| 032 | `??` | C | SPR-013 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `CKO_GRAPH_API.md` |
| 033 | `??` | C | SPR-013 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `CKO_GRAPH_ARCHITECTURE.md` |
| 034 | `??` | C | SPR-013 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `CKO_GRAPH_MODEL_GUIDE.md` |
| 035 | `??` | C | SPR-013 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `CKO_GRAPH_NAVIGATION.md` |
| 036 | `??` | C | SPR-013 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `CKO_GRAPH_SERIALIZATION.md` |
| 037 | `??` | C | SPR-015 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `CKO_INDEX_API.md` |
| 038 | `??` | C | SPR-015 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `CKO_INDEX_ARCHITECTURE.md` |
| 039 | `??` | C | SPR-015 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `CKO_INDEX_MODEL_GUIDE.md` |
| 040 | `??` | C | SPR-015 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `CKO_INDEX_OPERATIONS.md` |
| 041 | `??` | C | SPR-015 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `CKO_INDEX_SERIALIZATION.md` |
| 042 | `??` | C | SPR-010 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `CKO_KNOWLEDGE_OBJECT_API.md` |
| 043 | `??` | C | SPR-010 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `CKO_KNOWLEDGE_OBJECT_ARCHITECTURE.md` |
| 044 | `??` | C | SPR-010 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `CKO_KNOWLEDGE_OBJECT_SERIALIZATION.md` |
| 045 | `??` | C | SPR-010 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `CKO_KNOWLEDGE_OBJECT_VERSIONING.md` |
| 046 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `CKO_PROVENANCE_STATEMENT_API.md` |
| 047 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `CKO_PROVENANCE_STATEMENT_ARCHITECTURE.md` |
| 048 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `CKO_PROVENANCE_STATEMENT_INTEGRATION.md` |
| 049 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `CKO_PROVENANCE_STATEMENT_MODEL_GUIDE.md` |
| 050 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `CKO_PROVENANCE_STATEMENT_OPERATIONS.md` |
| 051 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `CKO_PROVENANCE_STATEMENT_SERIALIZATION.md` |
| 052 | `??` | C | SPR-014 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `CKO_QUERY_API.md` |
| 053 | `??` | C | SPR-014 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `CKO_QUERY_ARCHITECTURE.md` |
| 054 | `??` | C | SPR-014 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `CKO_QUERY_MODEL_GUIDE.md` |
| 055 | `??` | C | SPR-014 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `CKO_QUERY_SERIALIZATION.md` |
| 056 | `??` | C | SPR-012 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `CKO_RELATIONSHIP_API.md` |
| 057 | `??` | C | SPR-012 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `CKO_RELATIONSHIP_ARCHITECTURE.md` |
| 058 | `??` | C | SPR-012 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `CKO_RELATIONSHIP_MODEL_GUIDE.md` |
| 059 | `??` | C | SPR-012 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `CKO_RELATIONSHIP_SERIALIZATION.md` |
| 060 | `??` | D | SPR-008OA | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `CKO_RUNTIME.cmd` |
| 061 | `??` | D | SPR-008OA | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `CKO_TESTS.cmd` |
| 062 | `??` | D | SPR-003–009A/fundação | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `README_SPR_003.md` |
| 063 | `??` | D | SPR-003–009A/fundação | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `README_SPR_004.md` |
| 064 | `??` | D | SPR-005 | configuração/manifesto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR005_MANIFEST.json` |
| 065 | `??` | D | SPR-006A | configuração/manifesto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR006A_MANIFEST.json` |
| 066 | `??` | D | SPR-007B | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR007B_ADVANCED_ENGINE.cmd` |
| 067 | `??` | D | SPR-007B | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR007B_ADVANCED_ENGINE.ps1` |
| 068 | `??` | D | SPR-008A | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008A_IMPLEMENTATION_REPORT.md` |
| 069 | `??` | D | SPR-008B | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008B_IMPLEMENTATION_REPORT.md` |
| 070 | `??` | D | SPR-008C | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008C_IMPLEMENTATION_REPORT.md` |
| 071 | `??` | D | SPR-008D | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008D_IMPLEMENTATION_REPORT.md` |
| 072 | `??` | D | SPR-008E | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008E_IMPLEMENTATION_REPORT.md` |
| 073 | `??` | D | SPR-008F | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008F_IMPLEMENTATION_REPORT.md` |
| 074 | `??` | D | SPR-008G | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008G_IMPLEMENTATION_REPORT.md` |
| 075 | `??` | D | SPR-008H | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008H_IMPLEMENTATION_REPORT.md` |
| 076 | `??` | D | SPR-008I | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008I_IMPLEMENTATION_REPORT.md` |
| 077 | `??` | D | SPR-008J | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008J_IMPLEMENTATION_REPORT.md` |
| 078 | `??` | D | SPR-008K | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008K_IMPLEMENTATION_REPORT.md` |
| 079 | `??` | D | SPR-008L | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008L_IMPLEMENTATION_REPORT.md` |
| 080 | `??` | D | SPR-008M | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008M_IMPLEMENTATION_REPORT.md` |
| 081 | `??` | D | SPR-008N | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008N_IMPLEMENTATION_REPORT.md` |
| 082 | `??` | D | SPR-008OA | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008OA_IMPLEMENTATION_REPORT.md` |
| 083 | `??` | D | SPR-008O | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008O_IMPLEMENTATION_REPORT.md` |
| 084 | `??` | D | SPR-008P | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008P_IMPLEMENTATION_REPORT.md` |
| 085 | `??` | D | SPR-008Q | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008Q_IMPLEMENTATION_REPORT.md` |
| 086 | `??` | D | SPR-008R | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008R_IMPLEMENTATION_REPORT.md` |
| 087 | `??` | D | SPR-008S | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008S_IMPLEMENTATION_REPORT.md` |
| 088 | `??` | D | SPR-008T | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008T_IMPLEMENTATION_REPORT.md` |
| 089 | `??` | D | SPR-008U | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008U_IMPLEMENTATION_REPORT.md` |
| 090 | `??` | D | SPR-008V | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008V_IMPLEMENTATION_REPORT.md` |
| 091 | `??` | D | SPR-008W | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR008W_IMPLEMENTATION_REPORT.md` |
| 092 | `??` | D | SPR-009A | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR009A_IMPLEMENTATION_REPORT.md` |
| 093 | `??` | D | SPR-009 | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR009_ARCHITECTURE_CERTIFICATION_REPORT.md` |
| 094 | `??` | D | SPR-009 | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `SPR009_IMPLEMENTATION_REPORT.md` |
| 095 | `??` | C | SPR-010 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `SPR010_IMPLEMENTATION_REPORT.md` |
| 096 | `??` | C | SPR-011 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `SPR011_IMPLEMENTATION_REPORT.md` |
| 097 | `??` | C | SPR-012 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `SPR012_IMPLEMENTATION_REPORT.md` |
| 098 | `??` | C | SPR-013 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `SPR013_IMPLEMENTATION_REPORT.md` |
| 099 | `??` | C | SPR-014 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `SPR014_IMPLEMENTATION_REPORT.md` |
| 100 | `??` | C | SPR-015 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `SPR015_IMPLEMENTATION_REPORT.md` |
| 101 | `??` | C | SPR-016 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `SPR016_IMPLEMENTATION_REPORT.md` |
| 102 | `??` | C | SPR-016 | documentação/texto | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `SPR016_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md` |
| 103 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `SPR017E_NOVA_AUDITORIA_FORMAL.md` |
| 104 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `SPR017G_VERIFICACAO_FINAL.md` |
| 105 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `SPR017_HOMOLOGATION_REPORT.md` |
| 106 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `SPR017_IMPLEMENTATION_REPORT.md` |
| 107 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `SPR017_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md` |
| 108 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `SPR017_TECHNICAL_SPECIFICATION.md` |
| 109 | `??` | B | SPR-017 | documentação/texto | cadeia documental e conteúdo SPR-017 | incluir com SPR-017 | C09 | `SPR017_TECHNICAL_SPECIFICATION_AUDIT.md` |
| 110 | `??` | E | SPR-018 | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | FORA | `SPR018_DISCOVERY_AND_SCOPE.md` |
| 111 | `??` | D | SPR-003–009A/fundação | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `advanced_engine.py` |
| 112 | `??` | D | SPR-003–009A/legado | configuração/manifesto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `config/categories.yaml` |
| 113 | `??` | D | SPR-003–009A/legado | configuração/manifesto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `config/settings.yaml` |
| 114 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `docs/adr/ADR-001_MONOLITO_MODULAR_INCREMENTAL.md` |
| 115 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `docs/adr/ADR-002_IDENTIDADE_DOCUMENTAL.md` |
| 116 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `docs/adr/ADR-003_PRESERVACAO_DO_LEGADO.md` |
| 117 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `docs/adr/ADR-004_BANCO_CANONICO_SEPARADO.md` |
| 118 | `??` | E | SPR-015 | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `docs/adr/INDEX.md` |
| 119 | `??` | E | SPR-005 | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `docs/architecture/CKO_CORE_ARQUITETURA_SPR005.md` |
| 120 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `docs/architecture/CKO_CORE_BASELINE_2026-07-11.md` |
| 121 | `??` | D | SPR-003–009A/legado | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/decisoes/ADR-005A-001_PERSISTENCIA_ADITIVA.md` |
| 122 | `??` | E | documentação transversal | documentação/texto | conteúdo arquitetural/governança transversal | reconciliar; incluir salvo discovery | C10 | `docs/governance/BASELINE_PREPARATION_REPORT.md` |
| 123 | `??` | D | SPR-003–009A/legado | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/sprint/CKO-CORE-SPR-005_TERMO_DE_ABERTURA.md` |
| 124 | `??` | D | SPR-003–009A/legado | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/sprint/CKO-CORE-SPR-006A_TERMO_DE_ABERTURA.md` |
| 125 | `??` | D | SPR-003–009A/legado | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/sprint/CKO-SPR-003_TERMO_DE_ABERTURA.md` |
| 126 | `??` | D | SPR-003–009A/legado | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/sprint/CKO-SPR-004_TERMO_DE_ABERTURA.md` |
| 127 | `??` | D | SPR-003–009A/legado | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/sprint/CKO-SPR-005A_TERMO_OFICIAL.md` |
| 128 | `??` | D | SPR-004 | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/sprint/SPR004_REPORT.md` |
| 129 | `??` | D | SPR-005 | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/sprint/SPR005_REPORT.md` |
| 130 | `??` | D | SPR-06A | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `docs/sprint/SPR006A_REPORT.md` |
| 131 | `??` | H | ambiente local/reproduzível | documentação/texto | BASELINE_PREPARATION_REPORT.md e natureza local | manter fora | FORA | `inventory.txt` |
| 132 | `??` | D | SPR-05A | migração SQL | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `migrations/005001_spr005a_persistence.sql` |
| 133 | `??` | D | SPR-07B | documentação/texto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `reports/SPR007B_ADVANCED_REPORT.md` |
| 134 | `??` | D | SPR-08J | arquivo de projeto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `reports/spr008j_trace/.gitkeep` |
| 135 | `??` | D | SPR-08M | arquivo de projeto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `reports/spr008m_trace/.gitkeep` |
| 136 | `??` | D | SPR-003–009A/legado | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/INICIALIZAR_BANCO_CANONICO.ps1` |
| 137 | `??` | D | SPR-005 | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/REVERTER_SPR005.ps1` |
| 138 | `??` | D | SPR-06A | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/REVERTER_SPR006A.ps1` |
| 139 | `??` | D | SPR-003–009A/legado | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/RUN_SPR_003_COMMIT.ps1` |
| 140 | `??` | D | SPR-003–009A/legado | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/RUN_SPR_003_DRY_RUN.ps1` |
| 141 | `??` | D | SPR-003–009A/legado | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/RUN_SPR_004_COMMIT.ps1` |
| 142 | `??` | D | SPR-003–009A/legado | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/RUN_SPR_004_DRY_RUN.ps1` |
| 143 | `??` | D | SPR-05A | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/SPR005A_MIGRAR_E_VALIDAR.ps1` |
| 144 | `??` | D | SPR-05A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/SPR005A_SQLITE_BACKUP.py` |
| 145 | `??` | D | SPR-005 | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/VALIDAR_SPR005.ps1` |
| 146 | `??` | D | SPR-06A | script operacional | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `scripts/VALIDAR_SPR006A.ps1` |
| 147 | `??` | G | build/packaging reproduzível | arquivo de projeto | metadados gerados por setuptools | não versionar; regenerável | FORA | `src/cko.egg-info/PKG-INFO` |
| 148 | `??` | G | build/packaging reproduzível | documentação/texto | metadados gerados por setuptools | não versionar; regenerável | FORA | `src/cko.egg-info/SOURCES.txt` |
| 149 | `??` | G | build/packaging reproduzível | documentação/texto | metadados gerados por setuptools | não versionar; regenerável | FORA | `src/cko.egg-info/dependency_links.txt` |
| 150 | `??` | G | build/packaging reproduzível | documentação/texto | metadados gerados por setuptools | não versionar; regenerável | FORA | `src/cko.egg-info/top_level.txt` |
| 151 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/__init__.py` |
| 152 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/api/__init__.py` |
| 153 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/classifier/__init__.py` |
| 154 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/contracts/__init__.py` |
| 155 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/contracts/repositories.py` |
| 156 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/contracts/scanner.py` |
| 157 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/__init__.py` |
| 158 | `??` | D | SPR-008V | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/checkpoint/__init__.py` |
| 159 | `??` | D | SPR-008V | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/checkpoint/contracts.py` |
| 160 | `??` | D | SPR-008V | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/checkpoint/engine.py` |
| 161 | `??` | D | SPR-008V | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/checkpoint/errors.py` |
| 162 | `??` | D | SPR-008V | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/checkpoint/models.py` |
| 163 | `??` | D | SPR-008V | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/checkpoint/repository.py` |
| 164 | `??` | D | SPR-008V | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/checkpoint/serializer.py` |
| 165 | `??` | D | SPR-008V | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/checkpoint/validator.py` |
| 166 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/composition/__init__.py` |
| 167 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/composition/models.py` |
| 168 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/composition/root.py` |
| 169 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/config/__init__.py` |
| 170 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/config/settings.py` |
| 171 | `??` | D | SPR-008R | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/connectors/__init__.py` |
| 172 | `??` | D | SPR-008R | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/connectors/contracts.py` |
| 173 | `??` | D | SPR-008R | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/connectors/errors.py` |
| 174 | `??` | D | SPR-008R | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/connectors/factory.py` |
| 175 | `??` | D | SPR-008R | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/connectors/models.py` |
| 176 | `??` | D | SPR-008R | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/connectors/registry.py` |
| 177 | `??` | D | SPR-008R | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/connectors/validator.py` |
| 178 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/contracts/__init__.py` |
| 179 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/contracts/base.py` |
| 180 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/__init__.py` |
| 181 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/builder.py` |
| 182 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/contracts.py` |
| 183 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/enums.py` |
| 184 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/errors.py` |
| 185 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/factory.py` |
| 186 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/identity.py` |
| 187 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/models.py` |
| 188 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/operations.py` |
| 189 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/serializer.py` |
| 190 | `??` | C | SPR-016 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `src/cko/core/corpus/validator.py` |
| 191 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/__init__.py` |
| 192 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/cancellation.py` |
| 193 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/capability_errors.py` |
| 194 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/capability_models.py` |
| 195 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/capability_negotiation.py` |
| 196 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/capability_validation.py` |
| 197 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/checkpoints.py` |
| 198 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/contracts.py` |
| 199 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/errors.py` |
| 200 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/events.py` |
| 201 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/execution.py` |
| 202 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/execution_errors.py` |
| 203 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/execution_models.py` |
| 204 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/execution_planner.py` |
| 205 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/foundation_errors.py` |
| 206 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/identity_contracts.py` |
| 207 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/identity_errors.py` |
| 208 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/identity_models.py` |
| 209 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/identity_resolution.py` |
| 210 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/mapper.py` |
| 211 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/models.py` |
| 212 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/optimizer.py` |
| 213 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/optimizer_errors.py` |
| 214 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/optimizer_models.py` |
| 215 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/optimizer_rules.py` |
| 216 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/pipeline.py` |
| 217 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/planner.py` |
| 218 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/planner_errors.py` |
| 219 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/planner_models.py` |
| 220 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/policies.py` |
| 221 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/providers.py` |
| 222 | `??` | D | SPR-008I | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_errors.py` |
| 223 | `??` | D | SPR-008J | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_evaluation.py` |
| 224 | `??` | D | SPR-008J | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_evaluation_contracts.py` |
| 225 | `??` | D | SPR-008J | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_evaluation_errors.py` |
| 226 | `??` | D | SPR-008J | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_evaluation_models.py` |
| 227 | `??` | D | SPR-008K | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_index.py` |
| 228 | `??` | D | SPR-008K | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_index_errors.py` |
| 229 | `??` | D | SPR-008K | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_index_models.py` |
| 230 | `??` | D | SPR-008I | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_models.py` |
| 231 | `??` | D | SPR-008I | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_resolution.py` |
| 232 | `??` | D | SPR-008I | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/query_validation.py` |
| 233 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/service.py` |
| 234 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/session.py` |
| 235 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/statistics.py` |
| 236 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/statistics_errors.py` |
| 237 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/statistics_models.py` |
| 238 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/stream.py` |
| 239 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/streaming_contracts.py` |
| 240 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/streaming_errors.py` |
| 241 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/streaming_models.py` |
| 242 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/streaming_pipeline.py` |
| 243 | `??` | D | SPR-008D–O | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/discovery/validator.py` |
| 244 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/__init__.py` |
| 245 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/contracts.py` |
| 246 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/enums.py` |
| 247 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/errors.py` |
| 248 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/factory.py` |
| 249 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/identity.py` |
| 250 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/metadata.py` |
| 251 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/models.py` |
| 252 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/serializer.py` |
| 253 | `??` | C | SPR-011 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `src/cko/core/documents/validator.py` |
| 254 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/exceptions/__init__.py` |
| 255 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/exceptions/errors.py` |
| 256 | `??` | D | SPR-008P | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/execution/__init__.py` |
| 257 | `??` | D | SPR-008P | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/execution/engine.py` |
| 258 | `??` | D | SPR-008P | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/execution/errors.py` |
| 259 | `??` | D | SPR-008P | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/execution/models.py` |
| 260 | `??` | D | SPR-008P | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/execution/operators.py` |
| 261 | `??` | D | SPR-008P | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/execution/pipeline.py` |
| 262 | `??` | D | SPR-008P | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/execution/validator.py` |
| 263 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/__init__.py` |
| 264 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/contracts.py` |
| 265 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/enums.py` |
| 266 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/errors.py` |
| 267 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/factory.py` |
| 268 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/identity.py` |
| 269 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/graph/indexes.py` |
| 270 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/metadata.py` |
| 271 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/models.py` |
| 272 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/navigation.py` |
| 273 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/serializer.py` |
| 274 | `??` | C | SPR-013 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `src/cko/core/graph/validator.py` |
| 275 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/identity/__init__.py` |
| 276 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/identity/identifier.py` |
| 277 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/identity/origin.py` |
| 278 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/identity/version.py` |
| 279 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/__init__.py` |
| 280 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/builder.py` |
| 281 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/contracts.py` |
| 282 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/enums.py` |
| 283 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/errors.py` |
| 284 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/factory.py` |
| 285 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/identity.py` |
| 286 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/metadata.py` |
| 287 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/models.py` |
| 288 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/operations.py` |
| 289 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/serializer.py` |
| 290 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/statistics.py` |
| 291 | `??` | C | SPR-015 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `src/cko/core/index/validator.py` |
| 292 | `??` | D | SPR-008C | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/inventory/__init__.py` |
| 293 | `??` | D | SPR-008C | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/inventory/builder.py` |
| 294 | `??` | D | SPR-008C | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/inventory/engine.py` |
| 295 | `??` | D | SPR-008C | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/inventory/errors.py` |
| 296 | `??` | D | SPR-008C | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/inventory/models.py` |
| 297 | `??` | D | SPR-008C | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/inventory/service.py` |
| 298 | `??` | D | SPR-008C | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/inventory/validator.py` |
| 299 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/__init__.py` |
| 300 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/contracts.py` |
| 301 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/enums.py` |
| 302 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/errors.py` |
| 303 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/factory.py` |
| 304 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/identity.py` |
| 305 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/metadata.py` |
| 306 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/models.py` |
| 307 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/knowledge/relationships.py` |
| 308 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/serializer.py` |
| 309 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/validator.py` |
| 310 | `??` | C | SPR-010 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `src/cko/core/knowledge/versioning.py` |
| 311 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/logging/__init__.py` |
| 312 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/logging/structured.py` |
| 313 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/metadata/__init__.py` |
| 314 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/metadata/universal.py` |
| 315 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/models/__init__.py` |
| 316 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/models/asset.py` |
| 317 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/models/document.py` |
| 318 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/models/event.py` |
| 319 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/__init__.py` |
| 320 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/constants.py` |
| 321 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/contracts.py` |
| 322 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/enums.py` |
| 323 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/errors.py` |
| 324 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/factory.py` |
| 325 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/identity.py` |
| 326 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/models.py` |
| 327 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/operations.py` |
| 328 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/references.py` |
| 329 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/relationship_projection.py` |
| 330 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/results.py` |
| 331 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/serializer.py` |
| 332 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/validator.py` |
| 333 | `??` | A | SPR-017 | produção Python | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `src/cko/core/provenance/versioning.py` |
| 334 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/__init__.py` |
| 335 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/contracts.py` |
| 336 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/enums.py` |
| 337 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/errors.py` |
| 338 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/factory.py` |
| 339 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/identity.py` |
| 340 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/metadata.py` |
| 341 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/models.py` |
| 342 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/serializer.py` |
| 343 | `??` | C | SPR-014 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `src/cko/core/query/validator.py` |
| 344 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/__init__.py` |
| 345 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/contracts.py` |
| 346 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/enums.py` |
| 347 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/errors.py` |
| 348 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/factory.py` |
| 349 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/identity.py` |
| 350 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/metadata.py` |
| 351 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/models.py` |
| 352 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/serializer.py` |
| 353 | `??` | C | SPR-012 | produção Python | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `src/cko/core/relationships/validator.py` |
| 354 | `??` | D | SPR-008S | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/__init__.py` |
| 355 | `??` | D | SPR-008S | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/contracts.py` |
| 356 | `??` | D | SPR-008S | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/errors.py` |
| 357 | `??` | D | SPR-008S | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/factory.py` |
| 358 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/__init__.py` |
| 359 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/connector.py` |
| 360 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/descriptor.py` |
| 361 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/factory.py` |
| 362 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/resolver.py` |
| 363 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/result.py` |
| 364 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/session.py` |
| 365 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/storage.py` |
| 366 | `??` | D | SPR-008T | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/filesystem/validator.py` |
| 367 | `??` | D | SPR-008S | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/models.py` |
| 368 | `??` | D | SPR-008S | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/registry.py` |
| 369 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/__init__.py` |
| 370 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/connector.py` |
| 371 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/descriptor.py` |
| 372 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/factory.py` |
| 373 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/resolver.py` |
| 374 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/result.py` |
| 375 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/session.py` |
| 376 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/storage.py` |
| 377 | `??` | D | SPR-008U | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/sqlite/validator.py` |
| 378 | `??` | D | SPR-008S | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/storage/validator.py` |
| 379 | `??` | D | SPR-008W | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/uow/__init__.py` |
| 380 | `??` | D | SPR-008W | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/uow/contracts.py` |
| 381 | `??` | D | SPR-008W | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/uow/engine.py` |
| 382 | `??` | D | SPR-008W | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/uow/errors.py` |
| 383 | `??` | D | SPR-008W | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/uow/models.py` |
| 384 | `??` | D | SPR-008W | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/uow/validator.py` |
| 385 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/utils/__init__.py` |
| 386 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/utils/text.py` |
| 387 | `??` | D | SPR-008A–009A | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/utils/time.py` |
| 388 | `??` | D | SPR-008OA | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/workspace/__init__.py` |
| 389 | `??` | D | SPR-008OA | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/workspace/build.py` |
| 390 | `??` | D | SPR-008OA | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/workspace/cleaner.py` |
| 391 | `??` | D | SPR-008OA | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/workspace/cli.py` |
| 392 | `??` | D | SPR-008OA | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/workspace/manager.py` |
| 393 | `??` | D | SPR-008OA | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/workspace/paths.py` |
| 394 | `??` | D | SPR-008OA | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/core/workspace/validator.py` |
| 395 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/kb/__init__.py` |
| 396 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/kb/database.py` |
| 397 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/metadata/__init__.py` |
| 398 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/metadata/file_metadata.py` |
| 399 | `??` | D | SPR-003–009A/legado | migração SQL | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/migrations/0001_initial_schema.sql` |
| 400 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/migrations/__init__.py` |
| 401 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/migrations/runner.py` |
| 402 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/models/__init__.py` |
| 403 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/models/document.py` |
| 404 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/models/job.py` |
| 405 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/organizer/__init__.py` |
| 406 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/persistence/__init__.py` |
| 407 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/persistence/cli.py` |
| 408 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/persistence/database.py` |
| 409 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/persistence/migrations.py` |
| 410 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/repository/__init__.py` |
| 411 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/repository/database.py` |
| 412 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/scanner/__init__.py` |
| 413 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/scanner/inventory.py` |
| 414 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/scanner/scanner.py` |
| 415 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/scanner/watcher.py` |
| 416 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/services/__init__.py` |
| 417 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/services/inventory_service.py` |
| 418 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/utils/__init__.py` |
| 419 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/cko/utils/file_utils.py` |
| 420 | `??` | D | SPR-003–009A/legado | produção Python | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `src/main.py` |
| 421 | `??` | J | ORIGEM NÃO COMPROVADA | documentação/texto | sem referência canônica suficiente | manter fora; decidir | FORA | `src/main.py.txt` |
| 422 | `??` | D | SPR-008A | configuração/manifesto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/fixtures/spr008a_config.toml` |
| 423 | `??` | D | SPR-008A | configuração/manifesto | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/fixtures/spr008a_config.yaml` |
| 424 | `??` | D | SPR-005 | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_architecture_spr005.py` |
| 425 | `??` | D | SPR-008B | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_canonical_asset_model_spr008b.py` |
| 426 | `??` | D | SPR-008V | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_checkpoint_foundation_spr008v.py` |
| 427 | `??` | D | SPR-008R | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_connector_abstraction_spr008r.py` |
| 428 | `??` | D | SPR-009A | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_core_consolidation_spr009a.py` |
| 429 | `??` | D | SPR-008A | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_core_sdk_spr008a.py` |
| 430 | `??` | D | SPR-008M | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_cost_based_planner_spr008m.py` |
| 431 | `??` | D | SPR-008H | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_capability_model_spr008h.py` |
| 432 | `??` | D | SPR-008D | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_contracts_spr008d.py` |
| 433 | `??` | D | SPR-008G | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_identity_resolution_spr008g.py` |
| 434 | `??` | D | SPR-008E | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_provider_foundation_spr008e.py` |
| 435 | `??` | D | SPR-008J | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_query_evaluation_spr008j.py` |
| 436 | `??` | D | SPR-008I | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_query_foundation_spr008i.py` |
| 437 | `??` | D | SPR-008K | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_query_index_foundation_spr008k.py` |
| 438 | `??` | D | SPR-008L | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_statistics_foundation_spr008l.py` |
| 439 | `??` | D | SPR-008F | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_discovery_streaming_foundation_spr008f.py` |
| 440 | `??` | C | SPR-011 | teste | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C03 | `tests/test_document_canonical_model_spr011.py` |
| 441 | `??` | D | SPR-008P | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_execution_engine_spr008p.py` |
| 442 | `??` | D | SPR-008O | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_execution_planner_spr008o.py` |
| 443 | `??` | D | SPR-003–009A/fundação | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_file_metadata.py` |
| 444 | `??` | D | SPR-008T | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_filesystem_storage_connector_spr008t.py` |
| 445 | `??` | D | SPR-008C | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_inventory_engine_spr008c.py` |
| 446 | `??` | C | SPR-016 | teste | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C08 | `tests/test_knowledge_corpus_foundation_spr016.py` |
| 447 | `??` | C | SPR-013 | teste | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C05 | `tests/test_knowledge_graph_foundation_spr013.py` |
| 448 | `??` | C | SPR-015 | teste | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C07 | `tests/test_knowledge_index_foundation_spr015.py` |
| 449 | `??` | C | SPR-010 | teste | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C02 | `tests/test_knowledge_object_foundation_spr010.py` |
| 450 | `??` | A | SPR-017 | teste | SPR017_IMPLEMENTATION_REPORT.md §2 e homologação | incluir após dependências | C09 | `tests/test_knowledge_provenance_statement_foundation_spr017.py` |
| 451 | `??` | C | SPR-014 | teste | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C06 | `tests/test_knowledge_query_foundation_spr014.py` |
| 452 | `??` | C | SPR-012 | teste | relatórios, suítes dedicadas e documentação SPR-010–016 | incluir por sprint | C04 | `tests/test_knowledge_relationship_foundation_spr012.py` |
| 453 | `??` | D | SPR-004 | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_metadata_spr004.py` |
| 454 | `??` | D | SPR-006A | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_migrations_spr006a.py` |
| 455 | `??` | D | SPR-005A | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_persistence_spr005a.py` |
| 456 | `??` | D | SPR-008N | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_query_optimizer_spr008n.py` |
| 457 | `??` | D | SPR-008Q | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_runtime_spr008q.py` |
| 458 | `??` | D | SPR-008U | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_sqlite_storage_adapter_spr008u.py` |
| 459 | `??` | D | SPR-008S | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_storage_abstraction_spr008s.py` |
| 460 | `??` | D | SPR-008W | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_unit_of_work_foundation_spr008w.py` |
| 461 | `??` | D | SPR-003–009A/fundação | teste | relatórios/termos/testes SPR-003–009A e conteúdo/imports | incluir em fundação histórica | C01 | `tests/test_workspace_manager.py` |
