# SPR-008F — CKO CORE SDK — Relatório de Implementação

## 1. Identificação

- Sprint: SPR-008F
- Objeto: Discovery Streaming and Batch Foundation
- Workspace: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`
- Namespace exclusivo: `cko.core.discovery`
- Baseline aplicada: Baseline Arquitetural 1.0
- Pré-requisito: SPR-008E homologada com ressalva ambiental
- Data da validação: 14/07/2026
- Runtime disponível: Python 3.12.13
- Runtime requerido pelo projeto: Python 3.13 ou superior
- Modo executado: WRITE CONTROLLED

## 2. Objetivo

Foi implementada exclusivamente a fundação canônica para produção,
transporte e consumo incremental de `DiscoveryBatch`. O fluxo processa um batch
por vez e não materializa em memória o conjunto completo de itens descobertos.

A entrega não cria scanner, provider, producer ou consumer concreto, nem acessa
filesystem, banco, rede, mensageria ou Inventory.

## 3. Arquitetura criada

A evolução permanece dentro de `cko.core.discovery` e foi dividida em cinco
módulos coesos:

1. `streaming_errors.py`: hierarquia pública de erros da SPR-008F;
2. `streaming_models.py`: cursor, política, acknowledgement, estados e métricas;
3. `streaming_contracts.py`: portas síncronas e assíncronas de producer/consumer;
4. `stream.py`: stream canônico, incremental, síncrono e assíncrono;
5. `streaming_pipeline.py`: orquestração neutra producer → stream → consumer.

O vínculo com o Discovery Provider é lógico e explícito por `provider_id`; a
produção é recebida por injeção através das portas públicas. Nenhum provider ou
adaptador de infraestrutura foi implementado.

`DiscoverySession.complete_stream()` foi acrescentado de modo estritamente
aditivo para permitir conclusão da sessão sem fabricar um `DiscoveryResult`
agregado. O método homologado `DiscoverySession.complete()` não foi alterado.

## 4. Contratos públicos

- `BatchProducer`: produção síncrona, fechamento e cancelamento cooperativo;
- `AsyncBatchProducer`: produção, fechamento e cancelamento assíncronos;
- `BatchConsumer`: consumo, fechamento e notificação de falha controlada;
- `AsyncBatchConsumer`: equivalentes assíncronos;
- `BatchProductionContext`: request, session, token, política, cursor e checkpoint;
- `BatchConsumptionContext`: request, session e token;
- `DiscoveryStream`: contrato iterável síncrono e assíncrono, de uso único;
- `StreamingDiscoveryPipeline`: orquestração incremental nos dois modos;
- `StreamingExecution`: saída terminal sem coleção agregada de itens.

## 5. Modelos

Foram criados modelos tipados e imutáveis quando a mutabilidade não pertence ao
ciclo de vida:

- `BatchCursor`;
- `BackpressurePolicy`;
- `BatchAcknowledgement`;
- `StreamMetrics`;
- `DiscoveryStreamState`;
- `BatchAcknowledgementStatus`;
- `ConsumerUnavailableBehavior`;
- `StreamingExecution`.

O `DiscoveryStream` é deliberadamente mutável apenas para controlar estado,
sequência e métricas. Ele conserva identidades e números de sequência já vistos,
mas não conserva o conteúdo dos batches.

## 6. Estados e transições

Estados canônicos:

- `created`;
- `open`;
- `completed`;
- `failed`;
- `cancelled`.

Transições válidas:

- `created → open`;
- `created → failed | cancelled`;
- `open → completed | failed | cancelled`.

Estados terminais não aceitam nova transição. Violações geram
`DiscoveryStreamTransitionError`. O estado `completed` exige que um
`DiscoveryBatch(final=True)` tenha sido observado.

## 7. Batch Cursor

`BatchCursor` possui:

- `schema_version` canônico `1.0`;
- identidade do request;
- identidade da session;
- próxima sequência lógica;
- estado lógico opaco, congelado e validado;
- serialização JSON determinística com chaves ordenadas;
- desserialização estrita, com rejeição de campos e versões desconhecidos.

O cursor rejeita localizações absolutas e chaves de infraestrutura. Não contém
interpretação de token de provider, acesso a filesystem, banco ou persistência.
Na retomada, somente a sequência canônica é avançada; o estado opaco é preservado.

## 8. Backpressure Policy

`BackpressurePolicy` representa:

- quantidade máxima de batches pendentes;
- quantidade máxima de itens por batch;
- limite lógico de memória declarado;
- comportamento de consumidor indisponível: `fail`, `reject` ou `cancel`;
- timeout lógico.

O pipeline sequencial mantém no máximo um batch em processamento. Limite de itens,
timeout e comportamento de indisponibilidade são aplicados. O limite de memória é
declarativo porque o CORE não mede memória de processo nem acessa infraestrutura.

Não foram implementados filas, threads, processos ou mensageria.

## 9. Acknowledgements

`BatchAcknowledgement` associa batch e session e registra:

- status `confirmed`, `rejected`, `partial` ou `failed`;
- itens processados e rejeitados;
- razão controlada quando não confirmado;
- timestamp timezone-aware;
- métricas numéricas imutáveis.

O stream valida identidades e exige que a soma processada/rejeitada corresponda ao
número de itens do batch. Processamento parcial exige contagens positivas em ambos
os resultados.

## 10. Fluxo síncrono

1. A pipeline reutiliza ou cria `DiscoverySession` e `CancellationToken`.
2. A sessão é associada ao `provider_id` e transita para `running`.
3. O producer recebe `BatchProductionContext`.
4. O `DiscoveryStream` abre no primeiro avanço do iterador.
5. Cada batch é validado por identidade, sequência e backpressure.
6. O consumer recebe apenas o batch corrente.
7. O acknowledgement é validado e contabilizado.
8. O cursor lógico avança após confirmação controlada.
9. O batch final encerra o stream deterministicamente.
10. Consumer e producer são fechados; a sessão termina sem resultado agregado.

## 11. Fluxo assíncrono

O fluxo assíncrono preserva a mesma ordem e invariantes, usando diretamente
`AsyncIterator`, `consume_async`, `close_async` e `cancel_async`. Não é criada
ponte de thread, executor de plataforma ou processo auxiliar.

## 12. Cancelamento

O mesmo `CancellationToken` homologado na SPR-008E é transportado aos contextos de
produção e consumo. O token é verificado antes da produção e antes de cada batch.

Quando cancelado:

- o producer é notificado cooperativamente;
- o stream transita para `cancelled`;
- a `DiscoverySession` transita para `cancelled`;
- a causa pública `DiscoveryCancelledError` é preservada;
- os endpoints são fechados deterministicamente.

## 13. Checkpoints

O contrato abstrato `DiscoveryCheckpoint` da SPR-008E é reutilizado sem alteração.
O checkpoint é apenas transportado no `BatchProductionContext` e no resultado da
execução. Sua identidade de sessão e sua relação lógica com o cursor são validadas.

Não existe persistência, serializer, repository ou implementação concreta de
checkpoint.

## 14. Métricas

`StreamMetrics` registra:

- batches produzidos, consumidos e rejeitados;
- itens produzidos, consumidos e rejeitados;
- início e conclusão;
- duração em segundos;
- estado terminal.

Snapshots são imutáveis. A sessão recebe somente os contadores terminais, sem
retenção de `DiscoveryBatch`, `DiscoveredItem` ou `DiscoveryResult` agregado.

## 15. Erros públicos

Todos derivam da hierarquia homologada `DiscoveryError`:

- `InvalidDiscoveryStreamError`;
- `DiscoveryStreamTransitionError`;
- `InvalidBatchSequenceError`;
- `DuplicateBatchError`;
- `InvalidBatchCursorError`;
- `InvalidBatchAcknowledgementError`;
- `BatchProducerError`;
- `BatchConsumerError`;
- `BackpressureViolationError`.

Falhas externas de producer e consumer são encapsuladas com `raise ... from ...`,
preservando a causa original. Falhas secundárias de cancelamento, notificação ou
fechamento não substituem a causa primária e são registradas por logging estruturado.

## 16. Arquivos criados

- `src/cko/core/discovery/streaming_errors.py`;
- `src/cko/core/discovery/streaming_models.py`;
- `src/cko/core/discovery/streaming_contracts.py`;
- `src/cko/core/discovery/stream.py`;
- `src/cko/core/discovery/streaming_pipeline.py`;
- `tests/test_discovery_streaming_foundation_spr008f.py`;
- `SPR008F_IMPLEMENTATION_REPORT.md`.

## 17. Arquivos alterados

- `src/cko/core/discovery/session.py`: método público aditivo
  `complete_stream()`; assinaturas e semântica anteriores preservadas;
- `src/cko/core/discovery/__init__.py`: exportações públicas exclusivamente
  aditivas.

Nenhum outro arquivo funcional foi alterado pela SPR-008F.

## 18. Dependências

### Runtime

- biblioteca padrão do Python;
- contratos e modelos homologados em `cko.core`.

Nenhuma dependência externa de runtime foi adicionada.

### Testes

- `pytest`, já disponível no ambiente de validação.

## 19. Testes

### Suíte específica SPR-008F

- arquivo: `tests/test_discovery_streaming_foundation_spr008f.py`;
- resultado final: **29 testes aprovados, zero falha, zero erro**;
- tempo da execução funcional final: **1,36 s**.

Foram testados estados, transições, iteração síncrona e assíncrona, ordem,
duplicidade, sequência inválida, cursor, versões, campos desconhecidos,
acknowledgements, parcial, cancelamento, falhas, backpressure, métricas, session,
token, checkpoint, API, type hints, docstrings, UTF-8, PEP-8 e proibições.

## 20. Cobertura

`coverage.py` não está instalado. Foi aplicada metodologia determinística da
biblioteca padrão:

1. `trace.Trace(count=1, trace=0)` registrou linhas observadas durante a suíte;
2. `dis.findlinestarts` enumerou linhas executáveis recursivamente em cada code
   object;
3. a interseção foi calculada apenas para os cinco módulos novos e para o método
   aditivo `DiscoverySession.complete_stream()`;
4. arquivos declarativos de exportação não foram usados para elevar o resultado.

Resultado final:

- `stream.py`: 232/237 — 97,89%;
- `streaming_contracts.py`: 92/93 — 98,92%;
- `streaming_errors.py`: 22/22 — 100,00%;
- `streaming_models.py`: 260/284 — 91,55%;
- `streaming_pipeline.py`: 365/428 — 85,28%;
- `DiscoverySession.complete_stream()`: 15/17 — 88,24%;
- total do novo código: **986/1081 — 91,21%**;
- gate mínimo: **90%**;
- resultado: **APROVADO**.

## 21. Regressão

Comando executado com `PYTHONPATH=src` e escrita de bytecode desabilitada:

```text
python -m pytest -p no:cacheprovider
  tests/test_core_sdk_spr008a.py
  tests/test_canonical_asset_model_spr008b.py
  tests/test_inventory_engine_spr008c.py
  tests/test_discovery_contracts_spr008d.py
  tests/test_discovery_provider_foundation_spr008e.py
  tests/test_discovery_streaming_foundation_spr008f.py -q
```

Resultado final: **122 testes aprovados, zero falha, zero erro, 2,58 s**.

Classificação:

- falha funcional causada pela SPR-008F: nenhuma;
- falha arquitetural: nenhuma;
- falha ambiental: Python 3.13 ausente; `coverage.py` ausente;
- falha legada preexistente nas suítes obrigatórias: nenhuma observada.

Uma tentativa de `compileall` encontrou bloqueio ambiental para escrita em
diretórios `__pycache__` existentes no Google Drive. Isso não afetou importação,
execução ou análise sintática. A validação foi concluída sem escrita de bytecode.

## 22. Validações adicionais

- API pública importada com sucesso;
- módulos e funções possuem docstrings;
- funções públicas e internas possuem type hints completos;
- zero linha acima de 88 caracteres nos cinco módulos novos;
- todos os arquivos novos lidos como UTF-8 e analisados por AST;
- zero `TODO`, `NotImplementedError` ou ellipsis de placeholder;
- zero import de `os`, `pathlib`, `sqlite3`, `requests`, `urllib`, Google,
  OneDrive, `threading`, `multiprocessing` ou OpenAI nos módulos novos;
- zero scanner, provider, producer ou consumer concreto de produção;
- logging estruturado aplicado a batches, transições e falhas secundárias;
- cursor rejeita campos, versões, tipos e localizações inválidos;
- API anterior permaneceu importável e coberta pela regressão.

## 23. Limitações deliberadas

1. Não existe scanner ou provider concreto.
2. Não existe producer ou consumer concreto de produção.
3. Não existe persistência de cursor, checkpoint ou sessão.
4. Não existe integração automática com Inventory.
5. Não existe medição real de memória; o limite é declaração lógica neutra.
6. Não existe espera ativa quando o consumidor está indisponível; a política
   escolhe falhar, rejeitar ou cancelar sem filas e sem threads.
7. O stream mantém conjuntos de identidades e sequências vistas para rejeitar
   duplicidade, mas nunca retém os conteúdos dos batches.
8. A execução nativa em Python 3.13 permanece pendente por indisponibilidade do
   runtime, mantendo a ressalva ambiental herdada.

## 24. Compatibilidade com as Sprints anteriores

### SPR-008A

`CanonicalId`, `Clock`, logging e erros fundamentais foram reutilizados.

### SPR-008B

`Asset` e identidade canônica não foram alterados nem duplicados.

### SPR-008C

Inventory não é importado, acessado ou atualizado.

### SPR-008D

`DiscoveryBatch`, `DiscoveryRequest`, `DiscoveredItem` e demais modelos foram
reutilizados sem mudança de assinatura ou semântica.

### SPR-008E

`DiscoverySession`, `CancellationToken` e `DiscoveryCheckpoint` foram reutilizados.
A única evolução funcional anterior foi o método aditivo `complete_stream()` para
conclusão sem agregação. Registry, Factory, Resolver, Executor e Pipeline 008E não
tiveram contratos alterados.

## 25. Respostas obrigatórias

1. **A fundação de streaming foi implementada?** Sim.
2. **O processamento incremental está funcional?** Sim, um batch por vez.
3. **A execução síncrona está funcional?** Sim.
4. **A execução assíncrona está funcional?** Sim.
5. **O Batch Cursor é neutro e versionado?** Sim, schema `1.0`.
6. **Existe persistência de cursor?** Não.
7. **Existe persistência de checkpoint?** Não.
8. **Existe scanner concreto?** Não.
9. **Existe provider concreto?** Não.
10. **Existe acesso ao filesystem?** Não.
11. **Existe acesso a banco?** Não.
12. **Existe integração com Google Drive?** Não.
13. **Existe dependência externa no runtime?** Não.
14. **Existe integração automática com Inventory?** Não.
15. **O CancellationToken da SPR-008E foi reutilizado?** Sim.
16. **A DiscoverySession da SPR-008E foi reutilizada?** Sim.
17. **O DiscoveryBatch da SPR-008D foi reutilizado?** Sim.
18. **A política de backpressure está funcional?** Sim.
19. **As sequências duplicadas são rejeitadas?** Sim.
20. **As falhas de producer e consumer são controladas?** Sim, com causa preservada.
21. **A regressão SPR-008A–008F foi aprovada?** Sim, 122 testes aprovados.
22. **A cobertura mínima foi atingida?** Sim, 91,21%.
23. **A SPR-008F pode ser homologada?** Sim, com ressalva exclusivamente ambiental
    pela ausência de Python 3.13 no runtime disponível.

## 26. Declaração final

**SPR-008F CONCLUÍDA E APTA À HOMOLOGAÇÃO, COM RESSALVA AMBIENTAL**

A Discovery Streaming and Batch Foundation está funcional, incremental,
determinística e integralmente contida no namespace `cko.core`. Os fluxos síncrono
e assíncrono, cursor versionado, acknowledgements, backpressure, cancelamento,
checkpoints abstratos, métricas e erros públicos foram implementados e validados.

Não existe scanner, provider concreto, infraestrutura, persistência, filesystem,
banco, Google Drive, Inventory automático ou dependência externa de runtime.

Nenhum trabalho da SPR-008G foi iniciado. A entrega aguarda homologação formal.
