# SPR-008D — CKO CORE SDK — Relatório de Implementação

## 1. Identificação

- Sprint: SPR-008D
- Objeto: Discovery Contracts
- Workspace: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`
- Baseline aplicada: Baseline Arquitetural 1.0
- Fundações homologadas: SPR-008A, SPR-008B e SPR-008C
- Data da validação: 14/07/2026
- Modo executado: WRITE CONTROLLED

## 2. Objetivo

Foi implementada a fronteira pública, abstrata e independente de infraestrutura
do futuro Discovery Engine. O novo namespace recebe solicitações canônicas,
representa fontes e capacidades, transporta observações com evidência e
proveniência, valida resultados, publica eventos e permite o mapeamento explícito
de um `DiscoveredItem` para o `Asset` homologado.

Nenhum mecanismo concreto de descoberta foi implementado.

## 3. Arquitetura implementada

O namespace `cko.core.discovery` foi dividido em nove módulos coesos:

1. `models.py`: modelos imutáveis e serialização versionada;
2. `contracts.py`: portas públicas implementáveis por adaptadores externos;
3. `policies.py`: invariantes neutras de políticas e capacidades;
4. `validator.py`: validação canônica das fronteiras;
5. `mapper.py`: mapeamento controlado para o `Asset` existente;
6. `events.py`: nomes estáveis e fábrica de `CanonicalEvent`;
7. `service.py`: orquestração sem infraestrutura;
8. `errors.py`: hierarquia pública derivada de `CKOError`;
9. `__init__.py`: API pública estável do namespace.

O fluxo implementado é:

`DiscoverySource -> DiscoveryProvider -> DiscoveryResult -> DiscoveredItem ->`
`DiscoveryAssetMapper -> Asset`

O `InventoryService` permanece fora do Discovery e recebe o `Asset` somente por
uma chamada explícita de um consumidor.

## 4. Contratos criados

- `DiscoverySource`: identidade estável e capacidades declarativas;
- `DiscoveryProvider`: execução lógica de uma solicitação;
- `DiscoveryAssetMapper`: transformação de observação validada em `Asset`;
- `DiscoveryEventPublisher`: publicação desacoplada de `CanonicalEvent`;
- `DiscoveryValidator`: validação de fonte, solicitação, item e resultado;
- `DiscoveryService`: orquestração de provider, validação, eventos e mapper.

Os contratos são `Protocol` verificáveis em runtime e não possuem implementação
de scanner, conector, transporte, parser ou persistência.

## 5. Modelos criados

- `DiscoverySourceId`;
- `DiscoveryRequest`;
- `DiscoveryScope`;
- `DiscoveryPolicy`;
- `DiscoveryCapability`;
- `DiscoveryStatus`;
- `DiscoveryWarning`;
- `DiscoveryErrorRecord`;
- `DiscoveryEvidence`;
- `DiscoveredItem`;
- `DiscoveryMetrics`;
- `DiscoveryResult`;
- `DiscoveryBatch`;
- `DiscoveryContext`.

Os modelos de dados usam `dataclass(frozen=True, slots=True)`. Mapas e sequências
de extensão são copiados e congelados, inclusive os metadados aninhados de uma
observação.

## 6. Fluxo de Discovery

1. O consumidor constrói `DiscoveryRequest` com fonte, escopo lógico, contexto,
   política, correlação e capacidades requeridas.
2. `DiscoveryService` valida fonte e solicitação.
3. O serviço publica `discovery.started`.
4. Um `DiscoveryProvider` externo produz um `DiscoveryResult` completo.
5. O serviço valida identidade, proveniência, correlação, métricas e estado.
6. O serviço publica eventos de itens, batches e conclusão.
7. O resultado retorna ao consumidor sem persistência ou mutação externa.

Falhas do provider são encapsuladas em `DiscoveryProviderError`, preservando a
causa, e geram `discovery.failed`.

## 7. Integração com Asset

`DefaultDiscoveryAssetMapper` exige que a identidade canônica já esteja validada
em `DiscoveredItem.canonical_id`. Ele cria o `Asset` homologado pela SPR-008B,
reutiliza `UniversalMetadata`, preserva proveniência técnica mínima e não cria
classificação institucional.

Quando a identidade canônica não está disponível, o mapper rejeita a operação
com `DiscoveryMappingError`. Nenhuma entidade concorrente de `Asset` existe.

## 8. Integração com Inventory

O Discovery não importa nem chama `Inventory`, `InventoryItem` ou
`InventoryService`. `DiscoveryService.map_assets()` retorna somente uma tupla de
`Asset`. O registro posterior em um inventário é uma decisão explícita do
consumidor, fora da transação de Discovery.

Assim, o fluxo `DiscoveredItem -> Asset -> Inventory` está preparado, mas a
inserção automática é arquiteturalmente impossível dentro do novo namespace.

## 9. Eventos

Foram definidos os nomes estáveis:

- `discovery.started`;
- `discovery.item.observed`;
- `discovery.item.rejected`;
- `discovery.batch.completed`;
- `discovery.completed`;
- `discovery.failed`;
- `discovery.cancelled`.

A fábrica reutiliza `CanonicalEvent`, `CanonicalId` e `Origin`. O serviço recebe
`Clock` e `DiscoveryEventPublisher` por injeção. Nenhum handler ou transporte é
configurado pelo núcleo.

## 10. Erros públicos

A hierarquia estável derivada de `CKOError` contém:

- `DiscoveryError`;
- `InvalidDiscoveryRequestError`;
- `InvalidDiscoverySourceError`;
- `InvalidDiscoveredItemError`;
- `UnsupportedDiscoveryCapabilityError`;
- `DiscoveryProviderError`;
- `DiscoveryMappingError`;
- `DiscoveryValidationError`.

Exceções genéricas de adaptadores não atravessam o serviço como contrato público.

## 11. Arquivos criados

- `src/cko/core/discovery/__init__.py`;
- `src/cko/core/discovery/contracts.py`;
- `src/cko/core/discovery/errors.py`;
- `src/cko/core/discovery/events.py`;
- `src/cko/core/discovery/mapper.py`;
- `src/cko/core/discovery/models.py`;
- `src/cko/core/discovery/policies.py`;
- `src/cko/core/discovery/service.py`;
- `src/cko/core/discovery/validator.py`;
- `tests/test_discovery_contracts_spr008d.py`;
- `SPR008D_IMPLEMENTATION_REPORT.md`.

## 12. Arquivos atualizados

- `src/cko/core/__init__.py`: exposição seletiva dos principais modelos de
  Discovery na fachada do SDK.

Nenhum módulo legado, documento de Baseline, Governança, Discovery institucional,
banco, Release ou Checkpoint foi alterado.

## 13. Dependências

### Runtime

- biblioteca padrão do Python;
- `cko.core.contracts.Clock`;
- `cko.core.identity`;
- `cko.core.metadata.UniversalMetadata`;
- `cko.core.models.Asset` e `CanonicalEvent`;
- `cko.core.exceptions.CKOError`;
- `cko.core.logging`.

Não foi adicionada dependência externa ao runtime.

### Testes

- `pytest`, já disponível no ambiente de validação.

## 14. Testes executados

### Suíte SPR-008D

- comando: `python -m pytest -p no:cacheprovider`
  `tests/test_discovery_contracts_spr008d.py -q`;
- resultado: **27 testes aprovados**;
- cobertura funcional: fontes, solicitações, capacidades, políticas, contexto,
  itens, evidências, warnings, erros, métricas, batches, estados, serialização,
  desserialização, versões e campos desconhecidos, validação, mapper, serviço,
  eventos, falha controlada e proibições de infraestrutura.

### Regressão SPR-008A + SPR-008B + SPR-008C + SPR-008D

- comando: `python -m pytest -p no:cacheprovider` com as quatro suítes
  homologadas;
- resultado: **71 testes aprovados, sem falhas**.

### Suíte completa do repositório

- resultado: **76 aprovados, 3 falhas e 7 erros**;
- causa: o sandbox negou enumeração/limpeza de `%TEMP%` e abertura de SQLite em
  diretórios temporários usados exclusivamente por testes legados;
- impacto na SPR-008D: nenhum. As 71 validações homologadas e os 27 testes do
  novo namespace foram aprovados.

## 15. Cobertura

Como `coverage.py` não está instalado, a cobertura foi medida com o tracer da
biblioteca padrão, limitado aos nove módulos de `cko.core.discovery`.

- linhas executáveis: **840**;
- linhas observadas: **773**;
- cobertura: **92,02%**;
- mínimo exigido: **90%**;
- resultado: **aprovado**.

## 16. Validações adicionais

- nove módulos lidos como UTF-8 e analisados por AST;
- zero imports de `os`, `pathlib`, `sqlite3`, `watchdog`, `requests`, `urllib`,
  OCR, parsing, Graph, embeddings, RAG, LLM ou SDK externo;
- zero caminhos absolutos embutidos;
- políticas rejeitam padrões que representem caminhos absolutos;
- zero `TODO`, placeholder, `NotImplemented` ou pseudocódigo;
- zero linhas acima de 88 caracteres no novo namespace;
- API pública documentada e com type hints;
- JSON determinístico, com enums por valor e datas ISO 8601 com fuso;
- campos desconhecidos e versões não suportadas são rejeitados.

## 17. Limitações deliberadas

1. Não existe scanner ou conector concreto.
2. Não existe leitura de filesystem, Drive, conteúdo, OCR ou parser.
3. Não existe persistência, SQLite ou registro automático no Inventory.
4. Não existe classificação, Graph, embeddings, RAG ou IA.
5. O mapper só cria um `Asset` quando `canonical_id` já foi validado.
6. O ambiente disponível executa Python 3.12.13; o projeto exige Python 3.13 ou
   superior. A implementação usa APIs estáveis compatíveis, mas a execução nativa
   em 3.13 permanece pendente.

## 18. Compatibilidade com SPR-008A

Foram reutilizados `CanonicalId`, `Clock`, `CanonicalEvent`, `Origin`,
`CKOError` e logging estruturado. Nenhuma configuração de handler, ambiente ou
infraestrutura foi adicionada. A evolução é estritamente aditiva.

## 19. Compatibilidade com SPR-008B

O mapper produz diretamente o `Asset` canônico e reutiliza
`UniversalMetadata`. `DiscoveredItem` é uma observação de proveniência e não uma
segunda entidade de ativo. Não houve alteração nos modelos homologados.

## 20. Compatibilidade com SPR-008C

O Discovery não conhece o agregado `Inventory`. A fronteira entrega `Asset` ao
consumidor, que pode usar explicitamente `InventoryService.register()` em outra
camada. Nenhum `InventoryItem` foi duplicado e nenhum estado do inventário é
mutado durante Discovery.

## 21. Próximos passos

1. Reexecutar as 71 validações homologadas em Python 3.13.
2. Homologar formalmente a API pública de `cko.core.discovery`.
3. Implementar providers e fontes concretas apenas em Sprint autorizada e fora
   do núcleo canônico.
4. Definir contratos de checkpoint/cancelamento operacional em Sprint própria,
   preservando as capacidades declarativas criadas nesta entrega.
5. Conectar explicitamente o resultado mapeado ao `InventoryService` somente na
   futura camada de aplicação autorizada.

## 22. Respostas obrigatórias

1. **Os contratos públicos de Discovery foram implementados?** Sim.
2. **Existe scanner concreto?** Não.
3. **Existe acesso ao filesystem?** Não.
4. **Existe acesso a banco?** Não.
5. **Existe dependência externa no runtime?** Não.
6. **O Discovery cria entidades concorrentes de `Asset`?** Não.
7. **O Discovery insere automaticamente itens no Inventory?** Não.
8. **O fluxo `DiscoveredItem -> Asset -> Inventory` está preparado?** Sim. O
   mapper produz `Asset`; o registro no Inventory permanece explícito e externo.
9. **Os modelos possuem serialização versionada?** Sim, com schema 1.0,
   round-trip validado, JSON determinístico e rejeição de versões/campos
   desconhecidos.
10. **Os eventos e erros públicos estão estáveis?** Sim.
11. **A regressão das SPRs anteriores foi aprovada?** Sim. As suítes homologadas
    SPR-008A/B/C/D totalizaram 71 testes aprovados.
12. **A SPR-008D pode ser homologada?** Sim, com as ressalvas ambientais de
    execução nativa em Python 3.13 e da suíte legada dependente de `%TEMP%`.

## 23. Declaração final

**SPR-008D CONCLUÍDA COM RESSALVAS**

As ressalvas são exclusivamente ambientais. A implementação funcional da
SPR-008D, sua regressão homologada, a cobertura mínima e as proibições
arquiteturais foram aprovadas.

### Resumo executivo

O CKO CORE SDK passa a possuir uma fronteira pública completa para Discovery,
com modelos imutáveis e versionados, contratos substituíveis, validação de
proveniência, eventos estáveis, erros de domínio, orquestração desacoplada e
mapeamento explícito para o `Asset` canônico. A entrega não antecipa scanner,
infraestrutura, persistência, classificação ou integração automática com o
Inventory, preservando integralmente as responsabilidades das SPRs homologadas.
