# SPR-008U — SQLite Storage Adapter

**Produto:** CKO CORE SDK  
**Namespace:** `cko.core.storage.sqlite`  
**Data de execução:** 23/07/2026  
**Runtime validado:** Python 3.13.14  
**Schema do adaptador:** 1.0  
**Versão do adaptador:** 1.0.0  
**Status da implementação:** concluída  
**Status da suíte dedicada:** aprovada  
**Status da cobertura:** aprovada, 92,63% ponderados  
**Status da regressão cumulativa:** 629 aprovações e 2 falhas legadas  

## 1. Arquitetura implementada

A SPR-008U implementou o primeiro adaptador concreto de persistência estruturada
do CORE SDK no namespace `cko.core.storage.sqlite`. A solução segue Ports and
Adapters e depende exclusivamente dos contratos públicos homologados de
`cko.core.connectors` e `cko.core.storage`, sem dependência direta do Runtime e
sem alteração dos contratos das SPR-008R, SPR-008S e SPR-008T.

O adaptador possui duas superfícies integradas:

- `SQLiteStorage` implementa a porta pública `Storage` e recebe somente
  `StorageSession` na operação contratual;
- `SQLiteConnector` implementa a porta pública `Connector`, traduz uma
  `ConnectorSession` em `SQLiteSession` e delega a execução ao Storage;
- `SQLiteSession` vincula os modelos públicos `ConnectorSession` e
  `StorageSession` e controla uma transação SQLite isolada;
- `SQLiteResult` vincula `ConnectorResult` e `StorageResult`;
- `SQLiteLocationResolver` mantém a fronteira entre o caminho físico do banco e
  as localizações lógicas representadas por `StorageLocation`;
- `SQLiteStorageFactory` compõe as implementações concretas pelas registries e
  factories públicas;
- `SQLiteStorageValidator` delega a validação contratual aos validators públicos
  das fundações R e S.

As seis operações canônicas de `StorageOperation` foram preservadas. As
operações `create`, `copy` e `move`, ausentes no enum homologado, são expostas
pelo Connector e representadas por `StorageOperation.WRITE` com o discriminador
serializável `sqlite_operation` em `StorageContext`. Essa tradução é interna ao
adaptador e não modifica o contrato público.

Cada execução isolada abre uma conexão, inicia transação, executa a operação,
realiza commit ou rollback e fecha a conexão. Transações explícitas usam
`SQLiteSession` como context manager e uma conexão exclusiva mantida em
`ContextVar`, impedindo compartilhamento implícito entre sessões.

## 2. Componentes criados

| Componente | Responsabilidade |
|---|---|
| `SQLiteStorage` | Implementa as nove operações, conexões, transações e persistência estruturada. |
| `SQLiteConnector` | Expõe o adaptador pela porta pública Connector. |
| `SQLiteDescriptor` | Agrupa descritores públicos de Storage e Connector. |
| `SQLiteSession` | Vincula sessões públicas e controla commit e rollback. |
| `SQLiteResult` | Vincula e serializa resultados públicos equivalentes. |
| `SQLiteLocationResolver` | Resolve o banco físico e valida localizações lógicas. |
| `SQLiteStorageFactory` | Compõe Storage e Connector pelas factories públicas. |
| `SQLiteStorageValidator` | Valida banco, descritores, sessões e resultados. |

Arquivos de produção criados:

- `src/cko/core/storage/sqlite/__init__.py`;
- `src/cko/core/storage/sqlite/connector.py`;
- `src/cko/core/storage/sqlite/descriptor.py`;
- `src/cko/core/storage/sqlite/factory.py`;
- `src/cko/core/storage/sqlite/resolver.py`;
- `src/cko/core/storage/sqlite/result.py`;
- `src/cko/core/storage/sqlite/session.py`;
- `src/cko/core/storage/sqlite/storage.py`;
- `src/cko/core/storage/sqlite/validator.py`.

Arquivos adicionais criados:

- `tests/test_sqlite_storage_adapter_spr008u.py`;
- `SPR008U_IMPLEMENTATION_REPORT.md`.

Nenhum arquivo das fundações `cko.core.connectors` e `cko.core.storage` foi
alterado. Nenhum componente legado, Runtime ou adaptador filesystem foi
alterado.

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

Toda entrada operacional é fornecida por `StorageContext`, `StorageLocation` e
`StorageSession`. Toda saída operacional é fornecida por `StorageObject` e
`StorageResult`. A integração genérica recebe `ConnectorSession` e retorna
`ConnectorResult`.

## 4. Funcionalidades implementadas

| Operação | Comportamento técnico |
|---|---|
| `create` | Insere um objeto estruturado e rejeita localização já existente. |
| `read` | Lê e desserializa deterministicamente JSON ou conteúdo Base64. |
| `write` | Executa upsert atômico do objeto estruturado. |
| `delete` | Remove exatamente um objeto lógico. |
| `exists` | Retorna a existência em metadata do `StorageResult`. |
| `list` | Lista namespace ou prefixo em ordem lexical determinística. |
| `metadata` | Retorna tamanho, SHA-256, timestamps UTC e metadata do objeto. |
| `copy` | Copia um objeto e seus dados em uma única transação. |
| `move` | Copia e remove a origem atomicamente na mesma transação. |

Também foram implementados:

- criação automática do banco e do schema técnico quando o arquivo não existe;
- detecção tipada de banco corrompido;
- conexão exclusiva por operação ou sessão explícita;
- context manager em `SQLiteStorage` e `SQLiteSession`;
- transações automáticas e explícitas;
- commit e rollback;
- rollback automático após resultado operacional com falha;
- isolamento entre sessões por conexão e contexto;
- timeout e `busy_timeout` configuráveis;
- `foreign_keys` habilitado por conexão;
- prepared statements com binding para todos os valores operacionais;
- serialização JSON determinística com UTF-8, chaves ordenadas, separadores
  canônicos, rejeição de NaN e ausência de coerção arbitrária;
- armazenamento binário por envelope Base64 serializável;
- digest SHA-256 calculado sobre o payload canônico;
- erros operacionais convertidos em `StorageResult` ou `ConnectorResult`
  tipados;
- erros de construção, validação e banco convertidos em `StorageException`.

O schema físico usa chave primária composta por namespace e chave lógica. O
schema não adiciona regras de negócio e armazena somente payload, tamanho,
digest, metadata e timestamps técnicos.

## 5. Logging estruturado

Foram implementados e testados todos os eventos obrigatórios:

| Evento | Emissão |
|---|---|
| `sqlite_open` | Abertura de conexão SQLite. |
| `sqlite_close` | Fechamento de conexão ou adapter context. |
| `sqlite_begin` | Início de transação automática ou explícita. |
| `sqlite_commit` | Commit de transação bem-sucedida. |
| `sqlite_rollback` | Rollback explícito, automático ou de fechamento. |
| `sqlite_read` | Conclusão de leitura. |
| `sqlite_write` | Conclusão de create, write, copy ou move. |
| `sqlite_delete` | Conclusão de exclusão. |
| `sqlite_list` | Conclusão de listagem. |
| `sqlite_exists` | Conclusão de verificação de existência. |
| `sqlite_metadata` | Conclusão de leitura de metadata. |

Os eventos usam o logging estruturado canônico, incluem `event` e `context` e
não configuram handler ou destino.

## 6. Testes

Comando da suíte dedicada:

```powershell
python -m pytest -p no:cacheprovider `
  --basetemp=runtime\temp\pytest_spr008u_clean `
  tests\test_sqlite_storage_adapter_spr008u.py -q
```

Resultado:

```text
28 passed in 3.32s
```

A suíte dedicada validou:

- criação, leitura, escrita, exclusão e existência;
- listagem determinística por namespace e prefixo;
- metadata, tamanho e SHA-256;
- copy e move atômicos;
- criação de banco inexistente;
- detecção de banco corrompido;
- serialização determinística e envelopes estritos;
- conteúdo estruturado UTF-8 e binário Base64;
- transações explícitas e automáticas;
- commit automático e rollback manual;
- rollback integral após falha em transação;
- prepared statements com chave hostil à injeção;
- isolamento entre conexões e sessões;
- concorrência lógica simulada entre dois adapters;
- integração com Connector e Storage;
- composição por ConnectorRegistry e StorageRegistry;
- composição por ConnectorFactory e StorageFactory;
- factory e validator concretos;
- logging estruturado dos onze eventos obrigatórios;
- context managers e fechamento seguro;
- tratamento de erros e parâmetros incompatíveis;
- ausência de ORM, dependência externa e dependência direta de Runtime;
- AST válido, UTF-8 e limite PEP-8 de 88 caracteres.

## 7. Cobertura

A cobertura foi medida com `trace`, da biblioteca padrão, sobre a suíte
dedicada:

```powershell
python -m trace --count --missing --summary `
  --coverdir runtime\reports\coverage_spr008u `
  --module pytest -p no:cacheprovider `
  --basetemp=runtime\temp\pytest_spr008u_coverage `
  tests\test_sqlite_storage_adapter_spr008u.py -q
```

| Módulo | Statements | Cobertos | Cobertura |
|---|---:|---:|---:|
| `sqlite.__init__` | 10 | 10 | 100,00% |
| `sqlite.connector` | 55 | 51 | 92,73% |
| `sqlite.descriptor` | 101 | 94 | 93,07% |
| `sqlite.factory` | 59 | 57 | 96,61% |
| `sqlite.resolver` | 29 | 29 | 100,00% |
| `sqlite.result` | 80 | 74 | 92,50% |
| `sqlite.session` | 181 | 157 | 86,74% |
| `sqlite.storage` | 542 | 506 | 93,36% |
| `sqlite.validator` | 55 | 52 | 94,55% |
| **Total ponderado** | **1.112** | **1.030** | **92,63%** |

O resultado supera a cobertura mínima requerida de 90% para o novo pacote.

## 8. Regressão

Comando da regressão cumulativa:

```powershell
python -m pytest -p no:cacheprovider `
  --basetemp=runtime\temp\pytest_spr008u_regression tests -q
```

Resultado:

```text
629 passed, 2 failed in 11.77s
```

As duas falhas são legadas e constam expressamente no relatório homologado da
SPR-008T:

1. `tests/test_file_metadata.py::test_collect_metadata`: o teste fornece o
   argumento legado `calculate_hash`, ausente no contrato atual de
   `collect_metadata`;
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`:
   o teste mantém `cko.db` aberto no Windows e o teardown não consegue remover
   o arquivo, retornando `WinError 32`.

A SPR-008T registrou 601 aprovações e as mesmas 2 falhas legadas. A regressão da
SPR-008U registrou 629 aprovações e as mesmas 2 falhas, correspondendo
exatamente aos 28 novos testes aprovados. Nenhuma nova falha foi introduzida.
Os módulos envolvidos nas duas falhas não importam nem exercitam
`cko.core.storage.sqlite` e não foram alterados para ocultar ocorrências fora do
escopo.

## 9. Compatibilidade

- Python 3.13: validado em Python 3.13.14;
- UTF-8: validado no código, testes, valores e serialização;
- PEP-8: validado pelo limite de 88 caracteres;
- biblioteca padrão no código de produção: atendido;
- persistência: exclusivamente `sqlite3`;
- ORM: nenhum;
- dependências externas novas: nenhuma;
- contratos públicos R e S: preservados sem modificação;
- adaptador filesystem T: preservado sem modificação;
- Runtime: nenhuma dependência direta;
- estado global: não introduzido;
- registries: composição por instância;
- serialização: schema 1.0 estrito e JSON determinístico;
- logging: estruturado e sem destino imposto;
- SQL: valores operacionais vinculados por prepared statements.

## 10. Observações técnicas

O arquivo físico do banco permanece encapsulado por
`SQLiteLocationResolver`. Localização lógica, objetos, sessões e resultados
continuam independentes de tecnologia e serializáveis pelos contratos públicos.

O payload persistido usa envelope explícito `json` ou `bytes`. Valores JSON são
normalizados recursivamente para primitivas, mappings e sequências. Conteúdo
binário é normalizado para Base64. O digest SHA-256 e o tamanho são derivados do
payload UTF-8 canônico, garantindo repetibilidade.

As operações isoladas usam uma transação por execução. O context manager de
`SQLiteSession` mantém uma conexão exclusiva e permite executar múltiplas
`StorageSession` do mesmo provider na mesma transação. Qualquer falha marca a
transação e força rollback ao sair do contexto.

`ContextVar` isola a transação ativa por contexto de execução sem criar
singleton ou estado global. Uma segunda instância do adapter usa conexão
independente e não observa escrita ainda não confirmada.

`create`, `copy` e `move` usam inserção sem sobrescrita implícita. `write` usa
upsert atômico. `move` executa inserção do destino e remoção da origem na mesma
transação. A listagem usa ordenação lexical no banco e escaping dos caracteres
especiais de `LIKE`.

O código de produção importa somente módulos do CORE SDK e da biblioteca
padrão. Nenhum arquivo de requisitos ou configuração de dependências foi
alterado.

A execução dos testes SQLite precisou ocorrer fora do sandbox porque o processo
sandboxed não possuía permissão para criar e bloquear arquivos de banco nos
diretórios temporários. A execução aprovada fora do sandbox confirmou a suíte,
a cobertura e a regressão.

## 11. Conclusão

A SPR-008U foi implementada integralmente no namespace
`cko.core.storage.sqlite`. Os oito componentes solicitados foram criados, as
nove operações foram implementadas com `sqlite3`, o gerenciamento seguro de
conexões e transações foi incorporado e os contratos públicos de Connector e
Storage foram preservados.

A suíte dedicada aprovou 28 testes e atingiu 92,63% de cobertura ponderada. A
regressão cumulativa aprovou 629 testes e manteve somente as duas falhas legadas
já homologadas, sem nova regressão. A implementação é compatível com Python
3.13, UTF-8, PEP-8 e biblioteca padrão. Nenhuma Sprint posterior foi iniciada.
