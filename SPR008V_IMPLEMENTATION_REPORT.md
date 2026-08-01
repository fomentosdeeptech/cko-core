# SPR-008V — Relatório de Implementação

## 1. Identificação da Sprint

- Sprint: SPR-008V — Checkpoint and Snapshot Foundation
- Produto: CKO CORE SDK
- Namespace canônico: `cko.core.checkpoint`
- Schema público: `1.0`
- Versão pública: `1.0.0`
- Data de validação: 23/07/2026
- Plataforma validada: Windows, Python 3.13 e UTF-8

## 2. Objetivo arquitetural

Foi implementada a fundação canônica de Checkpoints e Snapshots para representar,
serializar, validar, persistir, restaurar, consultar, inspecionar, superseder e
excluir estados lógicos de execução. A fundação permanece neutra em relação a
tecnologia, provider, banco, filesystem e Runtime.

## 3. Arquitetura implementada

A solução segue Ports and Adapters:

- modelos e validações formam o núcleo imutável;
- `CheckpointSerializer`, `CheckpointRepository` e `CheckpointEngine` são portas
  públicas abstratas;
- `DefaultCheckpointSerializer` implementa JSON canônico;
- `StorageCheckpointRepository` adapta exclusivamente a porta pública `Storage`;
- `DefaultCheckpointEngine` coordena lifecycle e delega persistência;
- FilesystemStorage e SQLiteStorage permanecem adapters externos injetados.

Não há singleton, estado global mutável, I/O direto no engine ou configuração de
logging pelo pacote.

## 4. Arquivos criados e alterados

Criados:

- `src/cko/core/checkpoint/__init__.py`
- `src/cko/core/checkpoint/contracts.py`
- `src/cko/core/checkpoint/models.py`
- `src/cko/core/checkpoint/engine.py`
- `src/cko/core/checkpoint/repository.py`
- `src/cko/core/checkpoint/serializer.py`
- `src/cko/core/checkpoint/validator.py`
- `src/cko/core/checkpoint/errors.py`
- `tests/test_checkpoint_foundation_spr008v.py`
- `SPR008V_IMPLEMENTATION_REPORT.md`

Alterado:

- `src/cko/core/__init__.py`, exclusivamente para reexportar a API canônica da
  nova fundação.

## 5. Componentes públicos

A API exporta:

- constantes `CHECKPOINT_SCHEMA_VERSION` e `CHECKPOINT_VERSION`;
- os onze modelos e enums canônicos;
- as três portas abstratas;
- as três implementações padrão;
- `CheckpointValidator`;
- a hierarquia completa de exceções tipadas.

Os mesmos símbolos canônicos foram reexportados pela fachada `cko.core`. Detalhes
auxiliares internos não foram reexportados.

## 6. Modelos e contratos

Foram implementados:

- `CheckpointIdentifier`
- `CheckpointMetadata`
- `CheckpointPayload`
- `CheckpointRecord`
- `CheckpointSnapshot`
- `CheckpointContext`
- `CheckpointResult`
- `CheckpointQuery`
- `CheckpointCollection`
- `CheckpointState`
- `CheckpointOperation`

Todos os modelos de dados usam `@dataclass(frozen=True, slots=True)`, validação na
construção, timestamps UTC, congelamento profundo, envelopes com `model` e
`schema_version`, JSON determinístico, round-trip estrito e rejeição de campos
extras, modelos desconhecidos e versões não homologadas.

## 7. Fluxo de criação

`DefaultCheckpointEngine.create` valida o contexto e a metadata, normaliza o
instante para UTC, cria a identidade lógica, constrói ou aceita um payload
canônico, produz um `CheckpointRecord` em estado `created` e captura um
`CheckpointSnapshot`. Nenhuma operação de Storage é executada na criação.

## 8. Fluxo de persistência

`DefaultCheckpointEngine.store` valida a transição `created -> stored`, produz
um novo record imutável e delega ao repository. O repository:

1. valida o record e eventual versão já existente;
2. serializa o record;
3. constrói a localização lógica;
4. cria `StorageContext` e `StorageSession`;
5. executa `StorageOperation.WRITE`;
6. retorna `CheckpointResult`.

Conflitos de estado são retornados como `checkpoint_conflict`.

## 9. Fluxo de restauração

O repository verifica existência lógica, executa `StorageOperation.READ`, obtém
o envelope Base64, desserializa o JSON canônico e valida identidade, schema,
tamanho e SHA-256. O engine cria uma visão imutável em estado `restored` e um
novo snapshot, sem alterar silenciosamente o registro persistido.

## 10. Integração com Storage

O repository importa somente símbolos públicos de `cko.core.storage`:

- `Storage`
- `StorageContext`
- `StorageLocation`
- `StorageObject`
- `StorageOperation`
- `StorageResult`
- `StorageSession`

O namespace lógico é `checkpoints`. A chave é:

`<namespace>/<subject_id>/<sequence>/<checkpoint_id>.json`

Segmentos vazios, relativos, com separadores ou caracteres de controle são
rejeitados. Nenhuma localização física integra os modelos públicos.

## 11. Integração validada com FilesystemStorage

FilesystemStorage foi exercitado com diretórios temporários isolados em todos os
fluxos: store, restore, list, inspect, supersede, delete, conteúdo binário Base64,
conflito e checkpoint inexistente. O repository não importa o adapter.

## 12. Integração validada com SQLiteStorage

SQLiteStorage foi exercitado com bancos temporários isolados e fechamento
explícito após cada teste. Os mesmos fluxos e resultados obtidos com
FilesystemStorage foram validados sem qualquer import direto do adapter pelo
repository.

## 13. Serialização e integridade

O serializer usa UTF-8, chaves ordenadas, separadores compactos,
`ensure_ascii=False` e `allow_nan=False`. Bytes usam envelope Base64 explícito.
O tamanho e o SHA-256 do payload são calculados sobre sua representação JSON
canônica. Snapshots usam SHA-256 da representação canônica completa do record.
Corrupção, JSON não canônico, Base64 inválido e divergência de identidade são
detectados.

## 14. Lifecycle e transições

Transições homologadas:

- `created -> stored`
- `created -> failed`
- `stored -> restored`
- `stored -> superseded`
- `stored -> failed`
- `restored -> superseded`
- `restored -> failed`

`superseded` e `failed` são terminais. A supersessão exige sucessor distinto, do
mesmo namespace e subject, com sequência superior e
`parent_checkpoint_id` apontando para o checkpoint anterior. Não há exclusão
automática ou em cascata.

## 15. Logging

Foram emitidos os eventos:

- `checkpoint_created`
- `checkpoint_validated`
- `checkpoint_serialized`
- `checkpoint_stored`
- `checkpoint_restored`
- `checkpoint_listed`
- `checkpoint_inspected`
- `checkpoint_superseded`
- `checkpoint_deleted`
- `checkpoint_integrity_failed`
- `checkpoint_operation_failed`

Os contextos contêm somente identidade lógica, estado, operação, contagens e
códigos de erro. Payloads, conteúdo binário, credenciais, paths, URLs, conexões e
SQL não são registrados. O pacote não configura handler ou destino.

## 16. Testes

Suíte dedicada:

- comando: `python -m pytest -p no:cacheprovider
  --basetemp=runtime\temp\pytest_spr008v
  tests\test_checkpoint_foundation_spr008v.py -q`
- resultado final: `31 passed`
- duração da execução final dedicada com medição: 5,89 segundos

A suíte cobre modelos, imutabilidade, congelamento profundo, UTC, envelopes
estritos, JSON determinístico, Base64, digests, corrupção, lifecycle, queries,
ordenação, limit, adapters reais, injeção, logging, AST, UTF-8, imports e
exception chaining.

## 17. Cobertura

Como `coverage.py` não está instalado e nenhuma dependência externa poderia ser
adicionada, a medição foi realizada com `trace`, da biblioteca padrão do Python.

| Módulo | Executadas | Não executadas | Executáveis | Cobertura |
|---|---:|---:|---:|---:|
| contracts.py | 51 | 0 | 51 | 100,00% |
| engine.py | 207 | 13 | 220 | 94,09% |
| errors.py | 60 | 0 | 60 | 100,00% |
| models.py | 804 | 44 | 848 | 94,81% |
| repository.py | 355 | 33 | 388 | 91,49% |
| serializer.py | 65 | 9 | 74 | 87,84% |
| validator.py | 173 | 8 | 181 | 95,58% |
| **Total ponderado** | **1.715** | **107** | **1.822** | **94,13%** |

O total ponderado supera a cobertura mínima obrigatória de 90%.

## 18. Regressão

Comando final:

`python -m pytest -p no:cacheprovider
--basetemp=runtime\temp\pytest_spr008u_regression tests -q`

Resultado:

- 660 testes aprovados;
- 2 falhas;
- nenhuma falha nova.

As duas falhas são exatamente as exceções legadas autorizadas:

1. `collect_metadata()` não aceita o argumento legado `calculate_hash`;
2. o banco SQLite legado `cko.db` permanece aberto durante teardown no Windows.

Uma execução preliminar sem `--basetemp` foi descartada por falta de permissão na
pasta global `pytest-of-andre`; a execução oficial acima usou isolamento dentro
do workspace.

## 19. Compatibilidade

A implementação usa Python 3.13, biblioteca padrão, UTF-8, paths lógicos com `/`
somente no contrato Storage e arquivos temporários isolados nos testes. O código
não depende de recursos exclusivos de shell e permanece compatível com Windows
10, Windows 11 e PowerShell 5.1.

## 20. Dependências

Nenhuma dependência de produção ou teste foi adicionada. Não há ORM, framework,
driver externo, cloud SDK ou pacote de cobertura. A implementação usa apenas a
biblioteca padrão e contratos já homologados do CKO CORE SDK.

## 21. Riscos e observações

- Providers de Storage precisam declarar READ, WRITE, LIST, DELETE e EXISTS.
- A listagem restaura e valida cada record encontrado no namespace dedicado,
  priorizando integridade e neutralidade sobre otimizações específicas.
- O repository rejeita conteúdo inválido em vez de omitir silenciosamente um
  checkpoint corrompido.
- A medição de cobertura usa critérios de linhas executáveis do módulo `trace`,
  documentados na tabela.

## 22. Contratos homologados

Nenhum contrato público homologado foi alterado. A mudança foi exclusivamente
aditiva, com novos símbolos no namespace `cko.core.checkpoint` e reexports
canônicos na fachada `cko.core`.

## 23. Limite da Sprint

Nenhuma Sprint posterior foi iniciada. ARCH-001 não foi atualizado. Não foram
implementados plugins, Unit of Work, cache, Knowledge Graph, scheduler,
concorrência física, cloud adapters ou persistência direta do Runtime.
