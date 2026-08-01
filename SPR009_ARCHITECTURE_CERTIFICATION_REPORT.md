# SPR-009 — Relatório de certificação arquitetural do CKO CORE SDK v1.0

**Data de corte:** 2026-07-25 (America/Sao_Paulo)  
**Modo:** auditoria read-only; nenhum código, teste, contrato, configuração ou banco foi alterado  
**Baseline declarado:** CORE-001, `ARCH-001_CKO_CORE_MASTER_ARCHITECTURE_v1.1.md`, SPR-008A–W e SPR-008OA  
**Parecer:** **CERTIFICADO COM RESSALVAS**

## 1. Resposta executiva

O CKO CORE SDK possui fundações suficientes para iniciar, de forma controlada, a fundação da camada semântica. A implementação real é modular, não apresenta ciclos entre módulos `cko.core`, mantém Runtime e domínio sem dependência de adapters concretos, dispõe de portas Connector/Storage, adapters Filesystem/SQLite, Checkpoint e Unit of Work, e tem 686 testes aprovados. O início deve ser limitado aos modelos e contratos semânticos enquanto as ressalvas P1 abaixo são resolvidas; persistência semântica produtiva, governança e segurança não devem ser declaradas prontas antes disso.

Não há risco P0. O gate não é irrestrito porque a arquitetura normativa está desatualizada em relação às entregas U/V/W, o pacote ainda se identifica como `0.1.0`, a taxonomia de exceções possui seis raízes incompatíveis e não existe composição canônica única para adapters/ports.

## 2. Escopo e metodologia

Foram analisados integralmente `src/cko/core` (150 módulos, 29.411 linhas), `tests` (29 arquivos), `pyproject.toml`, `requirements.txt`, scripts `CKO_*.cmd`, relatórios `SPR008*_IMPLEMENTATION_REPORT.md`, ADRs e ARCH-001 v1.1. Foram usados: parsing AST de todos os módulos; inspeção de `__all__`; grafo de imports e SCC; busca estática; execução serial das suítes; validação de runtime; dois builds; inspeção ZIP/METADATA e SHA-256.

As tentativas de cobertura consolidada com `trace` foram invalidadas: a instrumentação e execuções concorrentes sob `runtime/temp` provocaram falhas de I/O no Google Drive e remoção/bloqueio dos próprios `.cover`. Essas ocorrências não foram contabilizadas como defeitos, pois as mesmas suítes passaram pelo script canônico fora da restrição. A cobertura reportada é a evidência `trace` homologada por Sprint, revalidada por execução funcional normal; não é correto somar seus denominadores como se fossem uma única corrida.

## 3. Ambiente certificado

| Dimensão | Evidência | Resultado |
|---|---|---|
| Windows | execução nativa no workspace `G:\Meu Drive\01 - CKO Platform` | conforme |
| Python | `CKO_RUNTIME.cmd`: 3.13.14 | conforme |
| PowerShell | `CKO_RUNTIME.cmd`: 5.1.26100.8894 | conforme |
| Encoding | validator e leitura de 150 fontes | UTF-8, zero BOM |
| Temporários | `runtime/temp` | conforme em execução canônica serial |
| Namespace | AST sob `src/cko/core` | exclusivo para o SDK novo |
| Dependências | imports de produção | apenas biblioteca padrão; requisitos externos não são usados pelo CORE |

## 4. Inventário consolidado

| Pacote | Módulos | Linhas | Responsabilidade | Origem | Status |
|---|---:|---:|---|---|---|
| `cko.core` | 1 | 593 | fachada de 334 exports | A–W | estável, ampla |
| `checkpoint` | 8 | 2.666 | snapshots e repository sobre Storage | V | estável |
| `config` | 2 | 112 | configuração do SDK | A | estável, mínima |
| `connectors` | 7 | 1.053 | porta, modelos, registry/factory | R | estável |
| `contracts` | 2 | 82 | ports base | A | estável |
| `discovery` | 53 | 14.845 | discovery, query, índices, estatística, optimizer e planners | D–O | estável, maior domínio |
| `exceptions` | 2 | 46 | raiz histórica `CKOError` | A | parcial |
| `execution` | 7 | 1.115 | operadores e engine lógico | P | estável |
| `identity` | 4 | 138 | ID, origem e semver | A | estável |
| `inventory` | 7 | 878 | inventário em memória | C | estável |
| `logging` | 2 | 62 | JSON logging | A | estável com ressalva |
| `metadata` | 2 | 46 | metadata universal | A | estável |
| `models` | 4 | 829 | ativos, documentos e eventos | B | estável |
| `runtime` | 8 | 1.031 | lifecycle e coordenação do Engine | Q | estável |
| `storage` | 25 | 3.978 | porta e adapters Filesystem/SQLite | S–U | estável |
| `uow` | 6 | 1.122 | transação lógica/compensação | W | estável |
| `utils` | 3 | 33 | tempo e texto | A | interno de suporte |
| `workspace` | 7 | 782 | runtime, limpeza, validação e build | OA | interno |

O inventário nominal e a árvore completa estão em `CKO_CORE_V1_ARCHITECTURE_MAP.md`; a superfície de símbolos está em `CKO_CORE_V1_PUBLIC_API_CATALOG.md`.

## 5. Arquitetura efetivamente implementada

```text
Produto/composition
  ├─ Runtime ─> Execution Engine ─> Execution Plan (Discovery)
  ├─ Discovery ─> Query -> Index/Statistics -> Planner -> Optimizer -> Execution Planner
  ├─ Connector port <─ FilesystemConnector / SQLiteConnector
  ├─ Storage port   <─ FilesystemStorage / SQLiteStorage
  ├─ Checkpoint Engine -> CheckpointRepository -> Storage port
  └─ Unit of Work -> repositories/operations + Storage/Connector/Checkpoint contracts
Workspace/Build é infraestrutura interna lateral, não dependência do Runtime.
```

Não foram encontrados ciclos. Runtime importa Discovery/Execution/logging, nunca Filesystem ou SQLite. Checkpoint importa somente `cko.core.storage`; UoW importa interfaces públicas de checkpoint/connectors/storage. Registries são por instância e retornam snapshots imutáveis. Adapters concretos dependem das portas e stdlib.

## 6. Conformidade com ARCH-001 v1.1

| Requisito/seção | Classe | Evidência no documento | Evidência real | Severidade | Recomendação / atualizar ARCH |
|---|---|---|---|---|---|
| Camadas e direção (5, 21) | CONFORME | regras de dependência | grafo AST, zero ciclos | informativa | manter |
| Ports and Adapters (6) | CONFORME | Connector/Storage | `connectors`, `storage`, adapters | informativa | ampliar para SQLite |
| Namespace/árvore (7, 8) | PARCIALMENTE CONFORME | termina em Filesystem/T | existem `storage.sqlite`, `checkpoint`, `uow` | P1 | atualizar ARCH |
| API raiz (22, 33) | PARCIALMENTE CONFORME | descreve A–T | `cko.core.__all__` tem 334 exports até W | P1 | regenerar catálogo e ARCH |
| Componentes futuros (29) | OBSOLETO | SQLite/persistência/checkpoint/UoW futuros | U/V/W implementados e testados | P1 | reclassificar como homologados |
| Runtime desacoplado (12, 31) | CONFORME | proíbe adapter concreto | `runtime/runtime.py` só importa plan/engine/logging | informativa | manter |
| Versionamento (24) | NÃO CONFORME | objetivo v1.0; componentes 1.0 | `pyproject.toml` e `cko.core.__version__` = 0.1.0 | P1 | decisão formal de release |
| Logging sem sink (19, 23) | PARCIALMENTE CONFORME | app controla handlers | `configure_logging()` limpa handlers do logger escolhido | P2 | documentar efeito ou evitar mutação destrutiva |
| Modelos estritos (24, 31) | PARCIALMENTE CONFORME | versões/campos desconhecidos rejeitados | famílias novas são fortes; famílias B–O variam em schema/serialização | P2 | contrato serializável comum |
| Testes/cobertura (25, 26) | PARCIALMENTE CONFORME | mínimo 90% por entrega | 686/688; 7 módulos individuais <90% | P2 | cobrir módulos listados |

## 7. Ports, adapters e contratos

Pontos conformes: ports não importam providers concretos; adapters só conhecem contratos necessários; factories concretas fazem composição local; registries não são globais; engines lógicos não fazem I/O; filesystem/SQLite estão encapsulados; Checkpoint usa a porta Storage; UoW não importa adapters; Runtime não conhece provider concreto.

Ressalvas: `cko.core.storage.sqlite` é adapter dentro do namespace de uma porta, aceitável porém precisa constar da ARCH; UoW referencia tipos públicos de três subsistemas e funciona como coordenador, devendo permanecer fora deles; não existe composition root canônico para montar Runtime + ports + adapters + Checkpoint + UoW, deixando a disciplina de composição a cada produto.

## 8. Modelos, serialização e validators

As famílias Connector, Storage, SQLite e Checkpoint apresentam `frozen=True`, `slots=True`, cópias defensivas, `schema_version`, JSON determinístico, rejeição de extras/versões e round-trip. `SQLiteSession` é deliberadamente mutável para controlar conexão/transação. UoW usa modelos frozen/slots e validação extensa, mas não publica serialização. Modelos B–O usam padrões anteriores: muitos são frozen/slots, porém `schema_version` pode ser constante/envelope em vez de campo e vários não possuem API uniforme `to_dict/from_dict/to_json/from_json`. Não há uma base serializável única; há implementações privadas repetidas.

Foram identificados 17 validators públicos/concretos. Cobrem Checkpoint, Connector, Discovery, planos/optimizer/estatística/index, Execution, Inventory, Runtime, Storage, adapters, UoW e ambiente. Não há validator dedicado para os modelos fundamentais `identity`, `metadata` e `models`; eles validam em `__post_init__`. A sobreposição mais relevante é `DiscoveryValidator` (ABC) versus `DefaultDiscoveryValidator` (implementação), intencional, e validators base mais validators de adapter, também composição deliberada.

## 9. Engines, pipelines e lifecycle

Há consistência em imutabilidade de context/result, validação antes de execução, logging estruturado e estados terminais. Execution Planner produz árvore; Execution Engine executa operadores sem I/O; Runtime coordena Engine/recursos/cancelamento; Checkpoint separa criação explícita de persistência; UoW executa/compensa operações e fecha lifecycle.

Divergências: relógio/ID são injetáveis em Checkpoint/UoW/Identity, mas alguns modelos/planners usam `datetime.now(UTC)` diretamente; Runtime gera IDs por UUID quando ausentes; estratégias de falha variam entre exceção tipada e result envelope; nomes de estado (`completed`, `finished`, `stored`, `committed`) são específicos e não compartilham um protocolo lifecycle. Isso é aceitável por domínio, mas exige guia transversal antes de novos coordenadores.

## 10. Exceções e logging

Foram encontradas 119 classes de exceção e seis raízes independentes (`CKOError`, `ConnectorException`, `StorageException`, `CheckpointException`, `RuntimeErrorBase`, `UnitOfWorkException`), além de famílias `ValueError` de planner/execution/index/statistics. A taxonomia proposta está em `CKO_CORE_V1_EXCEPTION_CATALOG.md`.

Foram encontradas 48 chamadas estruturadas. Há três convenções de nome (`snake_case`, `dot.case`, frases com espaços) e chamadas que não preenchem `extra.event`, especialmente partes antigas de Discovery. Contextos podem registrar paths de workspace/build/cleaning e mensagens de exceção; payloads de Checkpoint não são logados. Catálogo e taxonomia proposta constam de `CKO_CORE_V1_LOGGING_EVENT_CATALOG.md`.

## 11. Testes, cobertura e build

| Execução válida | Resultado |
|---|---|
| regressão `CKO_TESTS.cmd -q` | 686 passed, 2 failed, 0 skipped, 30,99 s |
| SPR-008T | 29 passed, 4,31 s |
| SPR-008U | 28 passed, 3,46 s |
| SPR-008V | 31 passed, 3,45 s |
| SPR-008W | 26 passed, 1,14 s |
| runtime | todos os 5 checks aprovados |
| build 1/2 | 184 entradas; SHA-256 idêntico |

Falhas legadas confirmadas sem alteração: `collect_metadata()` rejeita `calculate_hash`; o teste de persistência deixa `cko.db` aberto no teardown Windows. A cobertura por entrega supera 90%, mas sete módulos individuais estão abaixo de 90%; detalhes em `CKO_CORE_V1_TEST_AND_COVERAGE_REPORT.md`.

O wheel `cko-0.1.0-py3-none-any.whl` é válido, contém os 150 módulos CORE, 184 entradas, paths seguros e timestamp ZIP fixo `1980-01-01`. Dois builds produziram SHA-256 `A03F566116013678A9D2B53FC11F3BF21AA7772A37B58CB758E24565A143AFE5`. O wheel inclui também namespaces legados `cko.*`, coerente com preservação, porém confirma que o artefato não é exclusivamente CORE.

## 12. Qualidade estática

Todos os 150 arquivos possuem AST válido, UTF-8 sem BOM, zero tabs e nenhuma linha acima de 100 caracteres; há 84 linhas acima de 88. Não há TODO/FIXME em produção. `NotImplementedError` aparece apenas em ports/ABCs ou métodos abstratos de modelos. Um `pass` em `workspace/manager.py:90` ignora falha de remoção de diretório vazio, deliberadamente best-effort. `print` existe apenas na CLI JSON. Não há singleton/registry global. UUID/relógio possuem defaults não injetados em pontos listados no gap report.

## 13. Riscos e roadmap de correção

| Prioridade | Achado | Impacto |
|---|---|---|
| P0 | nenhum | — |
| P1 | ARCH-001 termina em T e contradiz U/V/W | governança e decisões futuras baseadas em mapa obsoleto |
| P1 | versão distribuída 0.1.0 versus certificação v1.0 | incompatibilidade de release/consumidor |
| P1 | seis raízes de exceção + famílias ValueError | tratamento uniforme e observabilidade difíceis |
| P1 | ausência de composition root/política de DI | produtos podem compor adapters/lifecycle de modos divergentes |
| P2 | sete módulos com cobertura individual <90% | ramos de validação/serialização insuficientemente exercitados |
| P2 | taxonomia de eventos inconsistente e paths em contexto | correlação e exposição operacional |
| P2 | serialização/schema não uniformes entre famílias | evolução e migração sem contrato transversal |
| P2 | scripts compartilham `runtime/temp` | execuções paralelas interferem entre si |
| P3 | 84 linhas >88 e API raiz de 334 nomes | manutenção/descoberta da API |
| P3 | relógio/UUID default não injetados em alguns modelos | determinismo de testes e replay |

Sequência recomendada: (1) Sprint de consolidação normativa/release sem breaking changes; (2) taxonomia comum de erros/eventos e guia de lifecycle; (3) composition root/config/security/audit mínimos; (4) reforço de cobertura/serialização; (5) iniciar Knowledge Object Foundation.

## 14. Gate e declaração final

**CERTIFICADO COM RESSALVAS.** O SDK é robusto o bastante para iniciar modelos e contratos da camada semântica, mas a certificação não autoriza declarar `v1.0` publicado nem iniciar persistência/governança sem resolver as quatro ressalvas P1. Não foi iniciada SPR-010.

Checklist: escopo completo; baseline confrontado; inventário/API/dependências/exceções/logging catalogados; regressão e falhas legadas reproduzidas; cobertura limitada explicitada; build repetível confirmado; riscos priorizados; prontidão semântica avaliada; nenhum código ou contrato alterado.
