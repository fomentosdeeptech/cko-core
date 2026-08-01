# CKO CORE v1 — Matriz de dependências

## Matriz de pacotes

`X` significa import direto encontrado por AST. `—` significa nenhum import direto. Imports relativos internos ao próprio pacote não são repetidos.

| Consumidor ↓ / Provedor → | found. | models | discovery | execution | runtime | connectors | storage | checkpoint | logging | workspace |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| foundation (`config/contracts/identity/metadata/models`) | X | X | — | — | — | — | — | — | — | — |
| inventory | X | X | — | — | — | — | — | — | X | — |
| discovery | X | X | X | — | — | — | — | — | X | — |
| execution | — | — | X | X | — | — | — | — | X | — |
| runtime | — | — | X | X | X | — | — | — | X | — |
| connectors | — | — | — | — | — | X | — | — | X | — |
| storage port | — | — | — | — | — | X | X | — | X | — |
| filesystem/sqlite adapters | — | — | — | — | — | X | X | — | X | — |
| checkpoint | — | — | — | — | — | — | X | X | logging stdlib | — |
| uow | — | — | — | — | — | X | X | X | X | — |
| workspace | — | — | — | — | — | — | — | — | X | X |

## Arestas efetivas agregadas

| Aresta | Imports | Avaliação |
|---|---:|---|
| checkpoint → storage | 2 | conforme: somente port pública |
| connectors → logging | 4 | conforme |
| discovery → contracts/identity/models/metadata/utils/logging/exceptions | 53 | conforme à fundação |
| execution → discovery/logging | 8 | conforme: consome plano |
| inventory → exceptions/identity/models/logging | 12 | conforme |
| runtime → discovery/execution/logging | 4 | conforme |
| storage → connectors/logging | 18 | conforme; adapters compartilham ports |
| uow → checkpoint/connectors/storage/logging | 4 | conforme ao coordenador W |
| workspace → logging | 1 | conforme |

## Ciclos e inversões

- **Ciclos de módulos:** nenhum SCC com mais de um módulo.
- **Domínio → filesystem/SQLite:** nenhum.
- **Runtime → adapter/provider concreto:** nenhum.
- **Port → implementação:** nenhum em `connectors/contracts.py` ou `storage/contracts.py`.
- **Adapter → adapter:** não encontrado; Filesystem e SQLite não se importam.
- **Checkpoint → adapter:** nenhum; `checkpoint/repository.py` importa `cko.core.storage`.
- **UoW → adapter:** nenhum; imports somente de pacotes públicos.

## Dependências externas

O CORE de produção importa somente biblioteca padrão: `abc`, `argparse`, `base64`, `binascii`, `collections`, `contextvars`, `csv`, `dataclasses`, `datetime`, `enum`, `functools`, `hashlib`, `inspect`, `io`, `json`, `locale`, `logging`, `math`, `os`, `pathlib`, `re`, `shutil`, `sqlite3`, `subprocess`, `sys`, `tempfile`, `time`, `tomllib`, `types`, `typing`, `urllib`, `uuid`, `zipfile`.

`requirements.txt` declara pytest, typer, rich, pydantic, networkx, fastapi, uvicorn, python-dotenv e pyyaml, mas nenhum é importado por `src/cko/core`. Isso não é dependência oculta do CORE; é uma lista de ambiente mais ampla e não refletida como `project.dependencies` no wheel.

## Ocorrências classificadas

| ID | Ocorrência | Severidade | Evidência | Tratamento |
|---|---|---|---|---|
| DEP-01 | ARCH não conhece U/V/W | P1 | ARCH seções 27/29 versus árvore real | atualizar documento |
| DEP-02 | UoW coordena três domínios públicos | informativa | `uow/contracts.py`, `uow/engine.py` | manter; impedir imports concretos futuros |
| DEP-03 | adapters estão sob pacote `storage` | informativa | `storage/filesystem`, `storage/sqlite` | decisão aceita; documentar SQLite |
| DEP-04 | workspace compartilha `runtime/temp` | P2 | scripts `CKO_TESTS.cmd` e testes de workspace | isolamento/lock por execução |
| DEP-05 | wheel inclui legado além do CORE | P2 | 184 entries, 150 CORE | documentar distribuição ou separar artefato futuro |
| DEP-06 | requirements amplos não viram METADATA | P3 | `requirements.txt` versus wheel METADATA | definir política de dependências do pacote |

## Regras certificadas

Permitido: foundation → stdlib; domain → foundation; execution → plan; runtime → execution; adapters → ports; composition externa → todos. Proibido para próximas Sprints: foundation/domain/runtime → adapter; port → tecnologia; adapter → adapter; registries globais; workspace como dependência de domínio.

## Adendo SPR-016 — direção de dependência do Corpus

`cko.core.corpus` depende somente da biblioteca padrão, da hierarquia pública `cko.core.exceptions` e, na conversão tipada de agregados, das APIs públicas de `cko.core.knowledge`, `cko.core.documents`, `cko.core.relationships`, `cko.core.graph`, `cko.core.query` e `cko.core.index`. Query é importada exclusivamente para rejeição explícita como membro. Nenhum desses seis namespaces importa `corpus`; a auditoria AST confirmou ausência de ciclos, imports privados e dependências reversas.

Corpus não importa Inventory, Runtime, Storage, Repository, Checkpoint, Discovery, filesystem, banco de dados ou rede. Graph e Index permanecem projeções opcionais declaradas como membros, nunca autoridades implícitas do manifesto.

## Adendo SPR-017 — direção de dependência de Provenance Statement

`cko.core.provenance` depende da biblioteca padrão, da hierarquia pública `cko.core.exceptions` e, exclusivamente para a projeção explícita de relacionamentos, da API pública `cko.core.relationships`. Os demais imports são internos ao próprio namespace.

Provenance não importa Corpus, Graph, Query, Index, Document, Knowledge Object, Inventory, Discovery, Runtime, Storage, adapters, banco de dados ou rede. Nenhum namespace anterior importa `provenance`; a integração ocorre pela fachada raiz, preservando a direção de dependências e os 610 exports anteriores.
