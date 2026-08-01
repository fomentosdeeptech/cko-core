# SPR-008S — Storage Abstraction Foundation

**Produto:** CKO CORE SDK  
**Namespace:** `cko.core.storage`  
**Data de execução:** 21/07/2026  
**Runtime validado:** Python 3.13.14  
**Schema dos contratos:** 1.0  
**Versão da fundação:** 1.0.0  
**Status da implementação:** concluída  
**Status da suíte dedicada:** aprovada  
**Status da regressão cumulativa:** 572 aprovações e 2 falhas legadas

## 1. Arquitetura implementada

A SPR-008S adicionou exclusivamente a camada canônica de abstração de
armazenamento no namespace público `cko.core.storage`. A solução segue Ports and
Adapters, mantém dependências orientadas para o núcleo e separa integralmente os
contratos de qualquer tecnologia ou mecanismo concreto de persistência.

A arquitetura foi organizada nas seguintes responsabilidades:

- porta abstrata `Storage`, implementável apenas por adaptadores futuros;
- modelos canônicos imutáveis, profundamente congelados e versionados;
- localizações e objetos lógicos sem caminhos, URLs ou identificadores de
  infraestrutura;
- `StorageRegistry` por instância, sem singleton ou estado global;
- `StorageFactory` baseada em construtores injetados e sem conhecimento de
  implementações concretas;
- `StorageValidator` para validação isolada e cruzada dos contratos;
- `StorageException` como exceção canônica da fundação;
- integração aditiva com a fachada pública `cko.core`;
- observabilidade estruturada sem configuração de handler ou destino.

O pacote não acessa filesystem, banco de dados, rede, Google Drive, OneDrive,
SharePoint, S3, Azure Blob ou qualquer API externa. Nenhum provider concreto de
armazenamento foi criado.

## 2. Componentes criados

| Componente | Responsabilidade |
|---|---|
| `Storage` | Porta abstrata com descritor e execução lógica por sessão. |
| `StorageDescriptor` | Identidade, metadados, capacidades e versão contratual. |
| `StorageMetadata` | Nome, descrição, versão e rótulos neutros. |
| `StorageCapabilities` | Operações e garantias comportamentais declaradas. |
| `StorageContext` | Correlação, operação, localização e parâmetros lógicos. |
| `StorageSession` | Snapshot imutável e versionado do lifecycle. |
| `StorageSessionState` | Estados `started`, `finished` e `failed`. |
| `StorageResult` | Resultado lógico imutável de uma operação. |
| `StorageLocation` | Namespace e chave lógicos, sem representação física. |
| `StorageObject` | Descritor lógico de objeto, sem conteúdo físico. |
| `StorageOperation` | Enumeração canônica das seis operações de armazenamento. |
| `StorageFactory` | Instancia e valida objetos registrados. |
| `StorageRegistry` | Registra, consulta e enumera providers deterministicamente. |
| `StorageValidator` | Valida todos os contratos requeridos e seus vínculos. |
| `StorageException` | Representa falhas tipadas de contrato e lifecycle. |

Arquivos criados:

- `src/cko/core/storage/__init__.py`;
- `src/cko/core/storage/contracts.py`;
- `src/cko/core/storage/errors.py`;
- `src/cko/core/storage/factory.py`;
- `src/cko/core/storage/models.py`;
- `src/cko/core/storage/registry.py`;
- `src/cko/core/storage/validator.py`;
- `tests/test_storage_abstraction_spr008s.py`;
- `SPR008S_IMPLEMENTATION_REPORT.md`.

Arquivo alterado aditivamente:

- `src/cko/core/__init__.py`, somente para reexportar os novos contratos
  públicos.

## 3. Contratos públicos

O pacote `cko.core.storage` e a fachada `cko.core` expõem:

- `STORAGE_SCHEMA_VERSION`;
- `STORAGE_VERSION`;
- `Storage`;
- `StorageCapabilities`;
- `StorageConstructor`;
- `StorageContext`;
- `StorageDescriptor`;
- `StorageException`;
- `StorageFactory`;
- `StorageLocation`;
- `StorageMetadata`;
- `StorageObject`;
- `StorageOperation`;
- `StorageRegistry`;
- `StorageResult`;
- `StorageSession`;
- `StorageSessionState`;
- `StorageValidator`.

Todos os modelos utilizam `dataclass(frozen=True, slots=True)`, congelam
recursivamente mappings e sequências e rejeitam valores não serializáveis,
números não finitos, estados inválidos e versões desconhecidas. Cada envelope
possui `schema_version` e `model`. Os métodos `to_dict`, `from_dict`, `to_json` e
`from_json` aplicam serialização estrita, round-trip e JSON determinístico com
chaves ordenadas.

O Registry impede duplicidade, consulta pelo identificador e produz snapshots e
enumeração em ordem lexical. Cada instância mantém seu próprio estado. O
construtor injetado fica separado do descritor serializável.

A Factory recebe Registry e Validator por injeção, executa apenas o construtor
registrado, valida a instância contra a porta `Storage` e exige igualdade exata
entre o descritor criado e o descritor registrado. Falhas de construção
preservam a causa original.

O Validator cobre descritores, capacidades, sessões, contextos, operações e
localizações. Também valida instâncias produzidas pela Factory e os vínculos de
identidade e compatibilidade de operação.

## 4. Logging estruturado

| Evento | Emissor |
|---|---|
| `storage_registered` | `StorageRegistry.register` |
| `storage_created` | `StorageFactory.create` |
| `storage_validated` | `StorageValidator` |
| `storage_session_started` | `StorageSession.start` |
| `storage_session_finished` | `StorageSession.finish` |

Os eventos utilizam o logging canônico do CORE, incluem o campo estruturado
`event` e contexto mínimo de rastreabilidade, sem impor destino de log.

## 5. Testes executados

### 5.1 Suíte dedicada

Comando:

```powershell
python -m pytest -p no:cacheprovider `
  tests\test_storage_abstraction_spr008s.py -q
```

Resultado:

```text
86 passed in 2.62s
```

A suíte validou:

- API pública e constantes de versão;
- abstração efetiva da porta `Storage`;
- imutabilidade superficial e profunda;
- isolamento contra mutação dos inputs;
- serialização determinística e round-trip de todos os modelos;
- rejeição estrita de campos, versões, tipos e JSON inválidos;
- invariantes de metadados, capacidades, localização, objeto, contexto, sessão
  e resultado;
- transições terminais imutáveis de sessão;
- registro, consulta, duplicidade, isolamento e enumeração determinística;
- criação genérica e validação contratual pela Factory;
- preservação da causa em falhas de construção;
- validação de descritores, capacidades, sessões, contextos, operações e
  localizações;
- emissão dos cinco eventos estruturados obrigatórios;
- ausência de imports e chamadas de I/O ou tecnologias externas.

### 5.2 Validações estáticas

Foram aprovados:

- parsing AST dos arquivos da implementação, integração pública e teste;
- leitura UTF-8;
- limite PEP-8 de 88 caracteres por linha;
- type hints nas superfícies públicas;
- docstrings nos módulos, classes e métodos públicos;
- importação pelo pacote e pela fachada `cko.core`;
- inspeção AST contra I/O e dependências proibidas;
- ausência de dependências externas adicionadas.

## 6. Cobertura

A cobertura foi medida com `trace`, da biblioteca padrão, sobre a suíte
dedicada.

| Módulo | Statements | Cobertura |
|---|---:|---:|
| `storage.contracts` | 12 | 100% |
| `storage.errors` | 35 | 100% |
| `storage.factory` | 41 | 97% |
| `storage.models` | 556 | 95% |
| `storage.registry` | 76 | 100% |
| `storage.validator` | 126 | 94% |
| **Total ponderado** | **846** | **96%** |

O resultado supera a cobertura mínima requerida de 90% para o novo código.

## 7. Regressão

A regressão integral foi executada em raiz temporária local gravável para evitar
as restrições de escrita do Google Drive e as ACLs inválidas do diretório
temporário padrão do Windows.

Resultado válido:

```text
572 passed, 2 failed in 8.73s
```

As duas falhas são legadas, já registradas na SPR-008R, e não foram introduzidas
pela SPR-008S:

1. `tests/test_file_metadata.py::test_collect_metadata`: o teste fornece o
   argumento legado `calculate_hash`, ausente no contrato atual de
   `collect_metadata`.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`:
   o teste mantém `cko.db` aberto e o teardown do Windows não consegue excluir o
   arquivo, resultando em `WinError 32`.

Nenhuma das falhas importa ou exercita `cko.core.storage`. Os 572 testes
aprovados incluem integralmente os 86 testes da SPR-008S. Componentes legados não
foram alterados, preservando a fronteira da Sprint.

## 8. Compatibilidade

- Python 3.13: validado em Python 3.13.14;
- UTF-8: validado;
- PEP-8: validado pelo limite de 88 caracteres;
- biblioteca padrão no código de produção: atendido;
- dependências externas novas: nenhuma;
- API pública anterior: preservada por alteração exclusivamente aditiva;
- estado global: não introduzido;
- serialização: schema 1.0 estrito e versionado;
- provider concreto: nenhum;
- filesystem, banco, rede e serviços cloud no pacote: ausentes.

## 9. Observações técnicas

`StorageLocation` usa somente `namespace`, `key` e atributos lógicos. O contrato
não admite semântica de caminho, URL, bucket, container, tabela ou vendor. A
tradução para endereços físicos pertence exclusivamente a adaptadores futuros.

`StorageObject` descreve identidade, localização, tamanho, digest e metadados.
Ele não transporta bytes nem abre recursos. O resultado permanece canônico,
serializável e independente da forma concreta de armazenamento.

O lifecycle não utiliza mutabilidade. `StorageSession.start` cria o snapshot
inicial e `StorageSession.finish` retorna um novo snapshot terminal. Estados
terminais não podem ser reabertos. Timestamps são fornecidos pelo consumidor e
normalizados para UTC, sem relógio implícito.

As capacidades usam `StorageOperation`, eliminando operações textuais livres.
Ordenações de operações, registros, mappings e JSON são determinísticas.

O pacote não importa `os`, `pathlib`, `sqlite3`, módulos de rede ou SDKs cloud e
não chama `open`. Essa restrição é verificada automaticamente pela suíte por
inspeção AST.

Nenhuma Sprint posterior foi iniciada e nenhum componente fora do escopo foi
alterado para corrigir ocorrências legadas.

## 10. Conclusão

A infraestrutura canônica de abstração de armazenamento da SPR-008S foi
implementada integralmente em `cko.core.storage`, com contratos públicos
tipados, documentados, imutáveis, serializáveis e versionados. Registry, Factory
e Validator atendem aos requisitos funcionais e arquiteturais. Os cinco eventos
estruturados obrigatórios foram implementados.

A suíte dedicada aprovou 86 testes e atingiu 96% de cobertura ponderada. A
regressão cumulativa aprovou 572 testes e confirmou somente duas falhas legadas,
independentes da nova fundação. A implementação está compatível com Python 3.13,
UTF-8, PEP-8 e biblioteca padrão, sem qualquer implementação concreta ou acesso
a armazenamento externo.
