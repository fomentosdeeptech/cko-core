# SPR-008T — Filesystem Storage Connector

**Produto:** CKO CORE SDK  
**Namespace:** `cko.core.storage.filesystem`  
**Data de execução:** 21/07/2026  
**Runtime validado:** Python 3.13.14  
**Schema do adaptador:** 1.0  
**Versão do adaptador:** 1.0.0  
**Status da implementação:** concluída  
**Status da suíte dedicada:** aprovada  
**Status da regressão cumulativa:** 601 aprovações e 2 falhas legadas

## 1. Arquitetura implementada

A SPR-008T implementou o primeiro adaptador concreto do CORE SDK no namespace
`cko.core.storage.filesystem`. A solução segue Ports and Adapters e depende dos
contratos públicos homologados de `cko.core.connectors` e `cko.core.storage`, sem
dependência direta do Runtime e sem alteração dos contratos das SPR-008R e
SPR-008S.

O adaptador possui duas superfícies integradas:

- `FilesystemStorage` implementa a porta pública `Storage` e recebe somente
  `StorageSession` em sua operação contratual;
- `FilesystemConnector` implementa a porta pública `Connector`, traduz uma
  `ConnectorSession` em `FilesystemSession` e delega a execução ao Storage;
- `FilesystemSession` mantém os modelos públicos `ConnectorSession` e
  `StorageSession` vinculados por identificador, correlação e lifecycle;
- `FilesystemResult` mantém `ConnectorResult` e `StorageResult` vinculados e
  serializáveis;
- `FilesystemLocationResolver` é a fronteira exclusiva entre
  `StorageLocation` e o caminho físico confinado à raiz configurada;
- `FilesystemStorageFactory` compõe as implementações concretas através de
  `ConnectorRegistry`, `ConnectorFactory`, `StorageRegistry` e `StorageFactory`;
- `FilesystemStorageValidator` delega a validação contratual aos validators
  públicos das fundações R e S.

As seis operações canônicas de `StorageOperation` são preservadas sem mudança.
As operações físicas `create`, `copy` e `move`, que não existem no enum da
SPR-008S, são expostas pelo Connector e representadas por `StorageOperation.WRITE`
com o discriminador serializável `filesystem_operation` no `StorageContext`.
Essa tradução é local ao adaptador e não modifica o contrato canônico.

## 2. Componentes criados

| Componente | Responsabilidade |
|---|---|
| `FilesystemStorage` | Implementa create, read, write, delete, exists, list, copy, move e metadata no filesystem. |
| `FilesystemConnector` | Expõe as nove operações pela porta pública Connector. |
| `FilesystemDescriptor` | Agrupa descritores públicos de Storage e Connector. |
| `FilesystemSession` | Vincula e serializa as sessões públicas equivalentes. |
| `FilesystemResult` | Vincula e serializa os resultados públicos equivalentes. |
| `FilesystemLocationResolver` | Resolve localizações lógicas sob uma raiz física confinada. |
| `FilesystemStorageFactory` | Compõe Storage e Connector pelas factories públicas. |
| `FilesystemStorageValidator` | Valida raiz, descritores, sessões e resultados. |

Arquivos de produção criados:

- `src/cko/core/storage/filesystem/__init__.py`;
- `src/cko/core/storage/filesystem/connector.py`;
- `src/cko/core/storage/filesystem/descriptor.py`;
- `src/cko/core/storage/filesystem/factory.py`;
- `src/cko/core/storage/filesystem/resolver.py`;
- `src/cko/core/storage/filesystem/result.py`;
- `src/cko/core/storage/filesystem/session.py`;
- `src/cko/core/storage/filesystem/storage.py`;
- `src/cko/core/storage/filesystem/validator.py`.

Arquivos adicionais criados:

- `tests/test_filesystem_storage_connector_spr008t.py`;
- `SPR008T_IMPLEMENTATION_REPORT.md`.

Nenhum arquivo das fundações `cko.core.connectors` e `cko.core.storage` foi
alterado. Nenhum componente legado ou Runtime foi alterado.

## 3. Contratos utilizados

Contratos públicos de `cko.core.connectors` utilizados:

- `Connector`;
- `ConnectorCapabilities`;
- `ConnectorContext`;
- `ConnectorDescriptor`;
- `ConnectorException`;
- `ConnectorFactory`;
- `ConnectorMetadata`;
- `ConnectorRegistry`;
- `ConnectorResult`;
- `ConnectorSession`;
- `ConnectorSessionState`;
- `ConnectorValidator`.

Contratos públicos de `cko.core.storage` utilizados:

- `Storage`;
- `StorageCapabilities`;
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

Toda entrada lógica é representada por contexto, localização e sessão públicos.
Toda saída é representada por `StorageObject`, `StorageResult` e
`ConnectorResult`. Caminhos físicos e bytes não são adicionados aos contratos
canônicos.

## 4. Funcionalidades implementadas

| Operação | Comportamento técnico |
|---|---|
| `create` | Cria arquivo vazio, arquivo inicializado ou diretório. |
| `read` | Lê arquivo e retorna conteúdo Base64; texto é opcional e usa encoding explícito. |
| `write` | Grava texto serializável ou conteúdo Base64. |
| `delete` | Exclui arquivo, diretório vazio ou árvore quando `recursive` é verdadeiro. |
| `exists` | Retorna existência em metadata e o objeto quando presente. |
| `list` | Enumera direta ou recursivamente em ordem lexical determinística. |
| `copy` | Copia arquivo ou diretório para outro `StorageLocation`. |
| `move` | Move arquivo ou diretório para outro `StorageLocation`. |
| `metadata` | Retorna tamanho, SHA-256, tipo de objeto e modificação em UTC. |

Os resultados de falhas operacionais são `StorageResult` e `ConnectorResult`
tipados, com mensagem ou errors conforme os invariantes dos contratos públicos.

## 5. Logging estruturado

Foram implementados e testados os eventos obrigatórios:

| Evento | Emissão |
|---|---|
| `filesystem_open` | Abertura validada da raiz pelo Storage. |
| `filesystem_read` | Conclusão de leitura, inclusive resultado de falha. |
| `filesystem_write` | Conclusão de criação ou escrita. |
| `filesystem_delete` | Conclusão de exclusão. |
| `filesystem_copy` | Conclusão de cópia. |
| `filesystem_move` | Conclusão de movimentação. |
| `filesystem_list` | Conclusão de enumeração. |

Os eventos usam o logging estruturado canônico, incluem `event` e `context` e
não configuram handler ou destino.

## 6. Testes

Comando da suíte dedicada:

```powershell
python -m pytest -p no:cacheprovider `
  --basetemp=runtime\temp\pytest_spr008t `
  tests\test_filesystem_storage_connector_spr008t.py -q
```

Resultado:

```text
29 passed in 7.71s
```

A suíte dedicada validou:

- criação de arquivos e diretórios;
- leitura e escrita UTF-8;
- leitura e escrita binária em Base64;
- exclusão simples e recursiva;
- cópia e movimentação de arquivos e diretórios;
- enumeração direta e recursiva determinística;
- existência e metadados com SHA-256;
- confinamento de localização e rejeição de traversal;
- tratamento tipado de arquivos ausentes e parâmetros inválidos;
- serialização determinística e round-trip de descriptor, session e result;
- integração completa com Connector;
- integração completa com Storage;
- composição pelas registries e factories públicas;
- emissão dos sete eventos estruturados obrigatórios;
- ausência de dependência direta de Runtime;
- AST válido, UTF-8 e limite PEP-8 de 88 caracteres.

## 7. Cobertura

A cobertura foi medida com `trace`, da biblioteca padrão, sobre a suíte
dedicada.

| Módulo | Statements | Cobertura |
|---|---:|---:|
| `filesystem.__init__` | 10 | 100% |
| `filesystem.connector` | 53 | 94% |
| `filesystem.descriptor` | 101 | 95% |
| `filesystem.factory` | 53 | 96% |
| `filesystem.resolver` | 51 | 94% |
| `filesystem.result` | 83 | 90% |
| `filesystem.session` | 119 | 87% |
| `filesystem.storage` | 261 | 94% |
| `filesystem.validator` | 53 | 94% |
| **Total ponderado** | **784** | **92,85%** |

O resultado supera a cobertura mínima requerida de 90% para o novo pacote.

## 8. Regressão

Comando da regressão cumulativa:

```powershell
python -m pytest -p no:cacheprovider `
  --basetemp=runtime\temp\pytest_spr008t_regression tests -q
```

Resultado:

```text
601 passed, 2 failed in 21.67s
```

As duas falhas são legadas, foram registradas anteriormente nas SPR-008R e
SPR-008S e não foram introduzidas pela SPR-008T:

1. `tests/test_file_metadata.py::test_collect_metadata`: o teste fornece o
   argumento legado `calculate_hash`, ausente no contrato atual de
   `collect_metadata`.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`:
   o teste mantém `cko.db` aberto no Windows e o teardown não consegue remover
   o arquivo, retornando `WinError 32`.

Nenhuma dessas falhas importa ou exercita `cko.core.storage.filesystem`. A
regressão aprovou os 29 testes da SPR-008T e todos os 572 testes que já eram
aprovados no baseline da SPR-008S. Componentes legados não foram alterados para
ocultar ocorrências fora do escopo.

## 9. Compatibilidade

- Python 3.13: validado em Python 3.13.14;
- UTF-8: validado no código, testes, conteúdo e serialização;
- PEP-8: validado pelo limite de 88 caracteres;
- biblioteca padrão no código de produção: atendido;
- dependências externas novas: nenhuma;
- contratos públicos R e S: preservados sem modificação;
- Runtime: nenhuma dependência direta;
- estado global: não introduzido;
- serialização: schema 1.0 estrito e JSON determinístico;
- logging: estruturado, sem destino imposto;
- plataformas: operações baseadas em `pathlib`, `shutil`, `hashlib` e Base64
  da biblioteca padrão.

## 10. Observações técnicas

O adaptador mantém o caminho físico exclusivamente no resolver e na
implementação concreta. `StorageLocation`, `StorageObject`, sessões e resultados
continuam lógicos e serializáveis. A resolução normaliza o caminho, rejeita
componentes absolutos e `..` e confirma que o destino permanece descendente da
raiz configurada.

Conteúdo binário não é inserido como `bytes` em mappings canônicos. Escritas
recebem `content_base64` e leituras retornam `content_base64`, mantendo
compatibilidade com o congelamento e a serialização estrita das fundações.

A enumeração ordena caminhos lexicalmente. Identificadores de objetos derivam
deterministicamente de namespace e chave. Digests usam SHA-256 e timestamps de
filesystem são normalizados para UTC.

`FilesystemStorageFactory` registra construtores sem argumentos por closure nas
registries instanciáveis e solicita a criação às factories públicas. Isso
exercita a composição prevista nas fundações e não introduz singleton.

A execução dos testes de filesystem precisou ocorrer fora do sandbox porque o
processo sandboxed não possuía permissão para criar arquivos no workspace do
Google Drive. A execução aprovada fora do sandbox confirmou os resultados
funcionais e de cobertura.

## 11. Conclusão

A SPR-008T foi implementada integralmente no namespace
`cko.core.storage.filesystem`. Os oito componentes solicitados foram criados, as
nove operações foram implementadas com biblioteca padrão, os contratos públicos
de Connector e Storage foram preservados e os sete eventos obrigatórios foram
emitidos.

A suíte dedicada aprovou 29 testes e atingiu 92,85% de cobertura ponderada. A
regressão cumulativa aprovou 601 testes e confirmou somente as duas falhas
legadas já conhecidas e independentes do adaptador. A implementação é compatível
com Python 3.13, UTF-8, PEP-8 e biblioteca padrão. Nenhuma Sprint posterior foi
iniciada.
