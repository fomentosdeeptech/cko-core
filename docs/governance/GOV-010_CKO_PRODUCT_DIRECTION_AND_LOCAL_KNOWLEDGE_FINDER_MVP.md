# CKO — GOV-010 — Product Direction and Local Knowledge Finder MVP

## A. Identificação

| Campo | Valor |
|---|---|
| Identificador | GOV-010 |
| Título | CKO Product Direction and Local Knowledge Finder MVP |
| Data | 16/08/2026 |
| Classe | Direção de produto e definição de MVP |
| Caminho canônico | `docs/governance/GOV-010_CKO_PRODUCT_DIRECTION_AND_LOCAL_KNOWLEDGE_FINDER_MVP.md` |

STATUS:

HUMAN_RATIFIED / ACTIVE

## B. Autoridade humana

O responsável humano pelo projeto ratifica a direção
`LOCAL_FIRST / VALUE_ORIENTED / GOVERNED`, adota o Cenário B — equilíbrio entre
governança e entrega — e estabelece o CKO Local Knowledge Finder como primeiro
MVP. Esta autoridade formaliza direção e critérios, mas não autoriza implementação.

## C. Contexto da EXE-001

A EXE-001 concluiu que o CKO possui fundação arquitetural ampla e validada, mas
ainda carece de uma experiência integrada de produto. Aproximadamente 65% a 75%
do esforço visível corresponde a fundação invisível. Discovery, identidade,
metadados, persistência, query, index, relacionamentos e proveniência já existem
em alguma forma, enquanto extração ativa, busca integrada e interface única são
lacunas centrais. P-018-02 agrega governança federada, porém não é o caminho mais
curto para valor percebido; o primeiro MVP deve operar localmente.

## D. Relação com GOV-009

O GOV-009 estabeleceu `docs/governance/INDEX.md` como autoridade exclusiva de
alocação GOV mantida no CORE e indicou GOV-010 como próximo número disponível.
Esta GOV é criada atomicamente com sua entrada nesse índice e preserva GOV-004
como lacuna histórica não reutilizável.

## E. Direção de produto

PRODUCT_DIRECTION:

LOCAL_FIRST / VALUE_ORIENTED / GOVERNED

CONTINUITY_SCENARIO:

CENÁRIO B — EQUILÍBRIO ENTRE GOVERNANÇA E ENTREGA

A direção prioriza um fluxo local demonstrável, útil e verificável antes de
conectores remotos ou federação. Governança permanece proporcional ao risco e aos
marcos materiais, protegendo fontes, evidências, baseline e API pública.

## F. Definição do CKO

O CKO é uma plataforma destinada a transformar documentos e registros dispersos
em conhecimento identificável, relacionável, pesquisável, rastreável, governado,
vinculado à fonte, à autoridade e à proveniência.

Seu diferencial pretendido é preservar a cadeia:

fonte → identidade → extração → interpretação → relacionamento → consulta →
decisão → evidência

O CKO não se reduz a armazenamento de arquivos, busca textual, banco documental,
RAG, base vetorial, gerenciador de documentos ou catálogo de dados. Esses conceitos
podem compor soluções futuras, mas não definem isoladamente o produto.

## G. Primeira persona

PRIMARY_PERSONA:

André Tozello, profissional responsável pela organização, estruturação, consulta
e recuperação de documentos e conhecimentos relacionados a projetos de inovação.

## H. Problema principal

PRIMARY_PROBLEM:

Localizar rapidamente documentos, versões, duplicidades, informações e evidências
dentro de coleções locais, preservando origem, identidade, integridade e
proveniência.

## I. MVP

MVP_NAME:

CKO Local Knowledge Finder

PRIMARY_USE_CASE:

Processar uma coleção documental local e localizar documentos, versões,
duplicidades, informações e evidências relacionadas a projetos de inovação.

INITIAL_SOURCE:

Pasta local explicitamente selecionada pelo usuário.

O processamento deve ser somente leitura sobre os arquivos-fonte. Todo índice,
banco, manifesto ou relatório produzido é derivado e reconstruível.

## J. Formatos iniciais

O escopo inicial inclui:

1. PDF textual;
2. DOCX;
3. TXT e Markdown como família de texto simples.

CSV poderá ser avaliado posteriormente. OCR e formatos não enumerados não
integram o primeiro MVP.

## K. Fluxo ponta a ponta

PROCESSING_FLOW:

discovery → identidade e hash → extração → metadados → classificação simples →
persistência → índice textual → consulta → resultado com origem e proveniência

O usuário seleciona uma pasta, processa documentos sem alterá-los, visualiza o
inventário, pesquisa por nome e conteúdo, identifica duplicidades, consulta
origem, caminho, tipo, hash e proveniência, reconhece falhas de processamento e
gera relatório resumido.

## L. Interface

INITIAL_INTERFACE:

CLI unificada

Os comandos mínimos são:

- `ingest`: inventariar e processar a pasta selecionada;
- `search`: pesquisar metadados e conteúdo;
- `show`: exibir detalhes, origem, hash e proveniência;
- `duplicates`: identificar conteúdo duplicado por hash;
- `report`: gerar resumo do processamento e de suas falhas.

Interface gráfica e aplicação web ficam fora do primeiro MVP.

## M. Persistência

A persistência inicial será SQLite local com schema versionado. O banco é um
artefato derivado, deve ser reconstruível a partir das fontes e não pode se tornar
autoridade sobre os documentos originais. Mudanças de schema exigirão migração e
compatibilidade explicitamente testadas.

## N. Busca e recuperação

O MVP deve permitir consulta por nome, conteúdo, tipo, categoria, data, projeto
quando disponível, hash e origem. Cada resultado aplicável deve apresentar
caminho, tipo, trecho relacionado, hash e proveniência, sem ocultar falhas ou
incertezas de extração.

## O. Cenário de demonstração

A homologação inicial utilizará corpus sintético de um projeto de inovação,
contendo regulamento, edital ou chamada, proposta, documento técnico, orçamento,
evidência, versão anterior, documento duplicado, documento relacionado e arquivo
deliberadamente não processável.

A demonstração deverá localizar o regulamento aplicável, a versão correta da
proposta, evidência técnica, duplicidade, origem, hash e trecho relacionado. Não
serão necessários dados pessoais, empresariais ou confidenciais.

## P. Critérios de sucesso

MVP_SC_001:

Nenhum arquivo-fonte é modificado.

MVP_SC_002:

Todos os arquivos suportados e válidos são inventariados.

MVP_SC_003:

PDF textual, DOCX, TXT e Markdown possuem extração funcional.

MVP_SC_004:

Falhas de extração são explícitas, rastreáveis e não interrompem indevidamente o
lote.

MVP_SC_005:

Reexecução é idempotente.

MVP_SC_006:

Duplicidades por hash são identificadas.

MVP_SC_007:

Busca por nome, conteúdo, tipo e hash funciona no corpus homologado.

MVP_SC_008:

Resultados apresentam caminho, tipo, trecho, hash e proveniência.

MVP_SC_009:

O banco derivado pode ser reconstruído sem alterar as fontes.

MVP_SC_010:

Existe fluxo ponta a ponta executável em interface única.

MVP_SC_011:

Instalação e execução são reproduzíveis.

MVP_SC_012:

SDK e API pública permanecem protegidos.

## Q. Escopo excluído

Ficam fora do primeiro MVP: interface gráfica, aplicação web, OCR, RAG,
embeddings, banco vetorial, IA generativa, Google Drive, Dropbox, SharePoint,
fontes remotas, conectores externos, multiusuário, IAM corporativo, publicação
oficial de conhecimento, federação, P-018-02, P-018-03, P-018-04, P-018-05,
PWAM, automação autônoma e implantação em produção.

Esses itens somente poderão ser reconsiderados após demonstração do fluxo local
e decisão própria.

## R. Reaproveitamento obrigatório

Antes de implementar, uma auditoria somente leitura deverá examinar o Universal
Content Extractor associado à SPR-007A, scanner, discovery, CLI legada, SQLite,
identidade, metadados, classificação, query, index, relationships, provenance,
relatórios, testes, scripts e componentes históricos.

A auditoria deverá distinguir Core ativo, legado, componente externo,
supersedido, reutilizável, adaptável, descartável e ausente. Nenhum componente
pode ser reconstruído antes da verificação de material reutilizável.

Próxima operação prevista: AUD-MVP-001 — Reusable Components and Legacy
Extraction Audit. A previsão não autoriza sua execução automática.

AUD_MVP_001_AUTHORIZED:

NO — REQUIRES SEPARATE COMMAND

## S. Governança proporcional

GOVERNANCE_MODEL:

RISK_BASED / MILESTONE_ORIENTED / AUTOMATION_FIRST

Continuam obrigatórios integridade Git, baseline, segurança, proteção de dados,
API pública, testes de comportamento, não mutação das fontes, proveniência,
dependências, releases, breaking changes, migrações e controles sobre dados reais.

Hashes, manifestos, fingerprint da API, imports, staging fechado, whitespace,
instalação e matriz requisito–teste–evidência devem ser automatizados ou
consolidados. Alterações de baixo risco e sem efeito semântico não exigem cadeias
repetitivas de relatórios. Decisão humana é exigida por marco material.

## T. Publicação do P-018-01

P_018_01_SOURCE_CONSOLIDATION:

PUBLISHED_TO_CANONICAL_GIT_REMOTE

CKO_FCP_PACKAGE_REGISTRY_PUBLICATION:

NOT EXECUTED / NOT AUTHORIZED

O código-fonte do P-018-01 foi publicado no Git remoto canônico. Sua distribuição
não foi publicada no PyPI ou em outro registry.

## U. Estado dos pacotes

P_018_01_STATUS:

IMPLEMENTED / VALIDATED / CONSOLIDATED

P_018_02_RECOMMENDATION:

DEFER_PENDING_MVP

P_018_02_AUTHORIZED:

NO

P_018_03_STATUS:

BLOCKED / NOT AUTHORIZED

P_018_04_STATUS:

BLOCKED / NOT AUTHORIZED

P_018_05_STATUS:

BLOCKED / NOT AUTHORIZED

## V. Roadmap em horizontes

### Horizonte 0 — Direção e reaproveitamento

Consolidar GOV-010, auditar componentes existentes e definir arquitetura mínima.
Não implementar antes da auditoria.

### Horizonte 1 — Primeiro valor visível

Entregar CLI unificada, inventário pesquisável, busca por metadados,
duplicidades, relatório e corpus sintético.

### Horizonte 2 — MVP operacional

Entregar extração mínima, índice textual persistido, busca por conteúdo, trechos,
proveniência, instalação, testes ponta a ponta e rollback do banco derivado.

### Horizonte 3 — Piloto controlado

Usar somente dados autorizados, aplicar segurança local e hardening, coletar
feedback e métricas e decidir separadamente sobre interface.

### Horizonte 4 — Federação

Somente após o MVP local, reconsiderar P-018-02 e definir fonte piloto,
autoridade, IAM, trust, retenção, redaction e resposta a incidentes.

## W. Riscos

| Risco | Controle |
|---|---|
| Reconstruir componentes existentes | AUD-MVP-001 somente leitura antes da arquitetura e implementação |
| Alterar fontes durante ingestão | processamento somente leitura e critérios de não mutação |
| Confundir banco derivado com fonte | reconstrução comprovada e proveniência explícita |
| Expandir prematuramente para federação | P-018-02 diferido até demonstração do MVP |
| Ocultar falhas de extração | erro explícito, rastreável e isolado por arquivo |
| Romper SDK ou API pública | gates automatizados de versão, contagem, fingerprint e comportamento |
| Usar dados sensíveis cedo demais | homologação inicial com corpus sintético |
| Transformar governança em atraso | controles proporcionais ao risco e decisões por marco material |

## X. Decisões futuras

Exigem decisão separada: autorização e escopo da AUD-MVP-001; arquitetura mínima;
plano de implementação; Sprint ou pacote executivo; corpus homologado definitivo;
política de instalação; interface posterior; uso de dados reais; piloto controlado;
e eventual reconsideração da federação e do P-018-02.

## Y. Proibições

Esta GOV não implementa código, cria Sprint, executa AUD-MVP-001, modifica GOV-009
ou GOV-002, altera README ou ROADMAP, publica pacote, inicia federação, usa fontes
remotas, autoriza implantação em produção ou concede autoridade aos pacotes
P-018-02 a P-018-05.

MVP_IMPLEMENTATION_AUTHORIZED:

NO

## Z. Veredito

Fica ratificada a direção `LOCAL_FIRST / VALUE_ORIENTED / GOVERNED` e definido o
CKO Local Knowledge Finder como primeiro MVP do CKO. A implementação e a
AUD-MVP-001 permanecem dependentes de comandos separados. P-018-02 permanece
diferido e não autorizado.
