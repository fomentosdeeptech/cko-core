# CKO — ADR-008 — CKO Local Knowledge Finder MVP Architecture

**Date:** 2026-08-16
**Status:** `HUMAN_RATIFIED / ACTIVE`
**Scope:** arquitetura mínima do CKO Local Knowledge Finder MVP
**Authority:** GOV-010 e ratificação humana expressa deste ADR

ADR_STATUS:

HUMAN_RATIFIED / ACTIVE

IMPLEMENTATION_STATUS:

NOT_STARTED / NOT_AUTHORIZED_BY_THIS_ADR

GOV_010_ALIGNMENT:

PASS

AUD_MVP_001_ALIGNMENT:

PASS

## 1. Contexto

A [GOV-010](../governance/GOV-010_CKO_PRODUCT_DIRECTION_AND_LOCAL_KNOWLEDGE_FINDER_MVP.md)
ratificou a direção `LOCAL_FIRST / VALUE_ORIENTED / GOVERNED` e definiu o CKO
Local Knowledge Finder como primeiro MVP. A AUD-MVP-001, executada somente para
leitura, identificou fundações ativas reutilizáveis no CKO Core, componentes
legados adaptáveis e lacunas de extração, busca textual, CLI integrada e
homologação ponta a ponta.

Esta decisão formaliza a arquitetura mínima necessária para uma implementação
futura. Ela não cria pacote, código, banco, fixture ou Sprint e não constitui
autorização de implementação.

## 2. Decisão de isolamento do produto

DISTRIBUTION_NAME:

cko-local-finder

IMPORT_NAMESPACE:

cko_local_finder

EXPECTED_PACKAGE_LOCATION:

packages/cko-local-finder/

ARCHITECTURE_STYLE:

ISOLATED_APPLICATION_PACKAGE_WITH_PORTS_AND_ADAPTERS

CORE_ROLE:

STABLE_DEPENDENCY / NOT MODIFIED

PUBLIC_API_CHANGE_REQUIRED:

NO

O produto será uma distribuição independente que consumirá contratos estáveis
do CKO Core. Regras específicas do Local Knowledge Finder não entrarão no Core,
os 646 exports públicos do SDK 1.0.0 não serão ampliados e nenhum comportamento
público vigente será modificado.

Módulos legados não poderão tornar-se dependências de runtime por importação
direta indiscriminada. Algoritmos selecionados somente poderão ser extraídos ou
adaptados após revisão controlada, testes e registro de proveniência técnica.

## 3. Estrutura lógica mínima

```text
cko_local_finder
├── domain
├── application
├── infrastructure
│   ├── filesystem
│   ├── extractors
│   ├── persistence
│   └── search
└── cli
```

- `domain`: modelos e regras independentes de filesystem, SQLite e CLI;
- `application`: casos de uso, ports e coordenação transacional;
- `infrastructure.filesystem`: descoberta local, confinamento e identidade física;
- `infrastructure.extractors`: extração por formato e normalização mínima;
- `infrastructure.persistence`: schema, migrações e repositórios SQLite;
- `infrastructure.search`: FTS5, filtros, ranking e geração de trechos;
- `cli`: parsing, saída, códigos de retorno e interação com o usuário;
- Core: contratos estáveis, documentos, proveniência, configuração e logging;
- legado: fonte de algoritmos e referência, nunca dependência indiscriminada.

Dependências devem apontar das bordas para os ports da aplicação e para o domínio.
O domínio não importará filesystem, SQLite, CLI, extractors concretos ou Core
infrastructure adapters.

## 4. Fluxo mínimo de ingestão

```text
fonte local autorizada
→ discovery confinado
→ identificação física
→ SHA-256
→ verificação de duplicidade
→ seleção do extractor
→ extração textual
→ normalização mínima
→ metadados
→ classificação simples
→ persistência SQLite
→ indexação FTS
→ proveniência
→ resultado de processamento
```

O processamento de cada arquivo será isolado. Uma falha deverá produzir registro
associado ao arquivo, status explícito e evidência no relatório final, sem
interromper indevidamente os demais itens do lote.

## 5. Fluxo mínimo de busca

```text
consulta
→ parser de filtros
→ SQLite FTS5
→ filtros de metadados
→ ranking determinístico
→ geração de trecho
→ associação com origem, hash e proveniência
→ apresentação do resultado
```

O resultado deverá conservar critérios suficientes para reprodução da consulta e
apresentar origem, caminho, tipo, hash, trecho e proveniência quando aplicáveis.

## 6. Interface inicial

A primeira interface será uma CLI unificada com cinco casos de uso:

- `ingest`: descobrir e processar uma fonte local autorizada;
- `search`: pesquisar conteúdo e metadados;
- `show`: apresentar um registro e sua rastreabilidade;
- `duplicates`: listar conteúdos fisicamente idênticos e suas localizações;
- `report`: resumir inventário, processamento, falhas e estado do índice.

A CLI conterá somente parsing, apresentação e códigos de retorno. Regras de
negócio e acesso a infraestrutura permanecerão atrás dos casos de uso e ports.

## 7. Persistência e busca textual

PERSISTENCE_ENGINE:

SQLite

TEXT_SEARCH_ENGINE:

SQLite FTS5

DATABASE_CLASS:

LOCAL_DERIVED_REBUILDABLE_ARTIFACT

SOURCE_OF_TRUTH:

ORIGINAL_LOCAL_DOCUMENTS

MIGRATION_POLICY:

VERSIONED / IDEMPOTENT / TESTED

DATABASE_COMMIT_POLICY:

NOT TRACKED IN GIT

O banco e o índice serão derivados e integralmente reconstruíveis a partir dos
documentos originais. O schema terá versão explícita, migrações idempotentes e
testes de aplicação, rollback e reconstrução.

A implementação futura deverá verificar a disponibilidade do FTS5 antes de criar
ou abrir o banco do produto. Runtime sem FTS5 deverá falhar com diagnóstico claro.
Não haverá fallback de busca textual desenvolvido para o primeiro MVP.

## 8. Formatos e dependências de extração

Os formatos iniciais autorizados são PDF textual, DOCX, TXT e Markdown.

PDF_EXTRACTION_DEPENDENCY:

pypdf

DOCX_EXTRACTION_DEPENDENCY:

python-docx

TXT_MARKDOWN_READER:

Python standard library

OCR, PDF exclusivamente baseado em imagem, planilhas, apresentações, e-mails,
páginas web, fontes remotas e armazenamento em nuvem ficam fora desta arquitetura
inicial.

## 9. Políticas de filesystem

SYMLINK_POLICY:

DO_NOT_FOLLOW_BY_DEFAULT

HIDDEN_FILE_POLICY:

IGNORE_BY_DEFAULT

ROOT_CONFINEMENT:

REQUIRED

PATH_NORMALIZATION:

REQUIRED

SOURCE_MUTATION:

PROHIBITED

UNREADABLE_FILE_POLICY:

REGISTER_ERROR_AND_CONTINUE

UNSUPPORTED_FORMAT_POLICY:

SKIP_WITH_EXPLICIT_STATUS

A implementação futura não poderá mover, renomear, excluir ou modificar
documentos de origem. Toda localização resolvida deverá permanecer confinada à
raiz explicitamente selecionada, salvo decisão futura específica.

## 10. Identidade, localização, versão e duplicidade

O SHA-256 representa a identidade física do conteúdo. Arquivos byte a byte
idênticos serão reconhecidos como duplicados, preservando-se todas as localizações
conhecidas.

O modelo deverá distinguir:

- identidade física: digest dos bytes observados;
- registro lógico: entidade administrativa do produto;
- localização: caminho observado sob a fonte autorizada;
- versão: relação lógica entre estados de um documento;
- conteúdo extraído: representação textual derivada;
- proveniência: cadeia entre fonte, atividade de extração e derivado.

Duplicidade física não implica automaticamente equivalência semântica, versão ou
autoridade documental.

## 11. Codificação e limites

DEFAULT_TEXT_ENCODING:

UTF-8

TEXT_ENCODING_FALLBACK:

UTF-8-SIG, depois diagnóstico explícito

MAX_FILE_SIZE_DEFAULT:

50 MiB

MAX_EXTRACTED_TEXT_DEFAULT:

5,000,000 caracteres por documento

LIMIT_OVERRIDE:

EXPLICIT CONFIGURATION ONLY

Limites serão avaliados antes da extração ou persistência. Arquivos e conteúdos
que os excederem não serão truncados silenciosamente: receberão status explícito
e diagnóstico rastreável.

## 12. Proveniência mínima

Cada conteúdo indexado deverá manter, no mínimo:

- caminho de origem;
- SHA-256;
- tamanho;
- data observada;
- tipo de arquivo;
- extractor e versão;
- resultado da extração;
- status de processamento;
- relação entre arquivo original e conteúdo derivado.

Os contratos estáveis de `cko.core.documents` e `cko.core.provenance` serão usados
por mapeamento mínimo e controlado. Modelos do produto não serão adicionados ao
Core e o banco derivado não se tornará fonte de verdade sobre os originais.

## 13. Reutilização controlada

A implementação futura poderá reutilizar diretamente ou adaptar componentes
ativos identificados pela AUD-MVP-001, especialmente confinamento de caminhos,
SQLite, documentos, proveniência, configuração e logging.

Algoritmos legados de hashing, metadados e duplicidade poderão ser extraídos de
forma controlada, sem transformar seus módulos de origem em dependências de
runtime. `scanner/watcher.py`, `utils/file_utils.py` e placeholders sem
implementação têm descarte recomendado para este produto.

O Universal Content Extractor/SPR-007A permanece apenas referência histórica
enquanto seu código não estiver disponível no repositório canônico e submetido a
auditoria própria.

## 14. Estratégia mínima de testes futuros

A futura implementação deverá incluir:

1. testes unitários por extractor;
2. arquivos válidos, vazios, grandes, corrompidos e não suportados;
3. testes de SHA-256 e duplicidade;
4. confinamento de caminhos, arquivos ocultos e symlinks;
5. migrações SQLite versionadas e idempotentes;
6. disponibilidade e comportamento do FTS5;
7. ranking determinístico e geração de trechos;
8. idempotência da ingestão;
9. reconstrução integral do banco;
10. continuidade do lote após falha isolada;
11. testes dos cinco comandos da CLI;
12. corpus sintético sem dados pessoais ou documentos reais;
13. gate de preservação do SDK 1.0.0;
14. gate das contagens públicas `646 / 646 / 646`;
15. gate do fingerprint público
    `d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`.

## 15. Consequências

### Positivas

- entrega local isolada de mudanças no Core;
- banco e índice reconstruíveis;
- separação verificável entre fonte e derivado;
- reaproveitamento seletivo da fundação existente;
- caminho curto para valor sem antecipar federação;
- API pública do SDK protegida.

### Custos e riscos

- nova distribuição e ciclo de release independentes;
- duas dependências externas de extração;
- necessidade de verificar FTS5 no runtime;
- mapeamento explícito para documentos e proveniência do Core;
- coexistência temporária com componentes legados que não devem ser importados.

## 16. Itens adiados

Ficam fora do escopo inicial: GUI, OCR, embeddings, RAG, modelos generativos,
busca semântica, fontes remotas, sincronização em nuvem, federação, monitoramento
contínuo de diretórios, agentes autônomos, alteração da API pública e P-018-02.

## 17. Autorizações e proibições

Este ADR permite que um plano de implementação ou uma Sprint sejam preparados
posteriormente mediante mandato separado. Não autoriza criar código, pacote,
diretórios de implementação, dependências instaladas, banco, fixtures, migrações
ou Sprint nesta operação.

MVP_IMPLEMENTATION_AUTHORIZED:

NO — REQUIRES SEPARATE COMMAND

P_018_02_AUTHORIZED:

NO

## 18. Veredito

Fica ratificada a arquitetura
`ISOLATED_APPLICATION_PACKAGE_WITH_PORTS_AND_ADAPTERS` para a distribuição
`cko-local-finder`, com namespace `cko_local_finder`, persistência SQLite, busca
SQLite FTS5 e extração inicial de PDF textual, DOCX, TXT e Markdown. O Core
permanece dependência estável e não modificada. A implementação não foi iniciada
nem autorizada por este ADR.
