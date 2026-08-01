# SPR-008R — Connector Abstraction Foundation

**Produto:** CKO CORE SDK  
**Namespace:** `cko.core.connectors`  
**Data de execução:** 20/07/2026  
**Runtime validado:** Python 3.13.14  
**Schema dos contratos:** 1.0  
**Versão da fundação:** 1.0.0  
**Status da implementação:** concluída  
**Status da suíte dedicada:** aprovada  
**Status da regressão cumulativa:** 486 aprovações e 2 falhas legadas

## 1. Arquitetura implementada

A SPR-008R adicionou exclusivamente a camada canônica de abstração de
conectores no namespace público `cko.core.connectors`. A solução segue Ports and
Adapters, mantém todas as dependências orientadas para o núcleo e não contém
implementações concretas de tecnologias externas.

A arquitetura foi organizada nas seguintes responsabilidades:

- porta abstrata `Connector`, implementável por adaptadores futuros;
- modelos canônicos imutáveis, profundamente congelados e versionados;
- `ConnectorRegistry` por instância, sem singleton ou estado global;
- `ConnectorFactory` baseada em construtores injetados e sem conhecimento de
  implementações concretas;
- `ConnectorValidator` para validação isolada e cruzada dos contratos;
- `ConnectorException` como exceção canônica da fundação;
- integração aditiva com a fachada pública `cko.core`;
- observabilidade estruturada por eventos, sem configuração de destino.

Nenhum componente da SPR acessa filesystem, banco de dados, rede, Google Drive,
OneDrive, SharePoint, S3, Azure Blob, APIs, OCR ou IA. Nenhum conector concreto
foi criado.

## 2. Componentes criados

| Componente | Responsabilidade |
|---|---|
| `Connector` | Porta abstrata com descritor público e execução por sessão. |
| `ConnectorDescriptor` | Identidade estável, metadados, capacidades e versão contratual. |
| `ConnectorMetadata` | Nome, descrição, versão e rótulos neutros. |
| `ConnectorCapabilities` | Operações, funcionalidades e declaração de streaming. |
| `ConnectorContext` | Correlação, operação, parâmetros e metadados lógicos. |
| `ConnectorSession` | Snapshot imutável e versionado do lifecycle da sessão. |
| `ConnectorSessionState` | Estados `started`, `finished` e `failed`. |
| `ConnectorResult` | Resultado lógico imutável, sem payload tecnológico. |
| `ConnectorFactory` | Instancia e valida conectores registrados. |
| `ConnectorRegistry` | Registra, consulta e enumera conectores deterministicamente. |
| `ConnectorValidator` | Valida descritores, capacidades, contextos, sessões e instâncias. |
| `ConnectorException` | Representa falhas tipadas de contrato e lifecycle. |

Arquivos criados:

- `src/cko/core/connectors/__init__.py`;
- `src/cko/core/connectors/contracts.py`;
- `src/cko/core/connectors/errors.py`;
- `src/cko/core/connectors/factory.py`;
- `src/cko/core/connectors/models.py`;
- `src/cko/core/connectors/registry.py`;
- `src/cko/core/connectors/validator.py`;
- `tests/test_connector_abstraction_spr008r.py`;
- `SPR008R_IMPLEMENTATION_REPORT.md`.

Arquivo alterado aditivamente:

- `src/cko/core/__init__.py`, apenas para reexportar os contratos públicos da
  nova fundação.

## 3. Contratos públicos

O pacote `cko.core.connectors` e a fachada `cko.core` expõem:

- `CONNECTOR_SCHEMA_VERSION`;
- `CONNECTOR_VERSION`;
- `Connector`;
- `ConnectorCapabilities`;
- `ConnectorConstructor`;
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

Todos os modelos públicos usam `dataclass(frozen=True, slots=True)`, congelam
recursivamente mappings e sequências e rejeitam valores não serializáveis ou
números não finitos. Cada envelope possui `schema_version` e `model`. Os métodos
`to_dict`, `from_dict`, `to_json` e `from_json` aplicam serialização estrita,
round-trip e JSON determinístico com chaves ordenadas.

O Registry impede identificadores duplicados, consulta por identificador e
produz snapshots e enumeração ordenados lexicalmente pelo identificador. O
Registry é instanciável e injetável, sem estado global.

A Factory recebe Registry e Validator por injeção, executa somente um construtor
sem argumentos previamente registrado, valida a instância contra `Connector` e
exige igualdade exata entre o descritor produzido e o descritor registrado.
Falhas de construção preservam a causa original.

O Validator implementa as validações requeridas de descritor, capacidades,
contexto e sessão. Também valida a instância criada pela Factory e os vínculos
entre operação, identificador de conector e descritor.

## 4. Logging estruturado

Foram implementados e testados os eventos obrigatórios:

| Evento | Emissor |
|---|---|
| `connector_registered` | `ConnectorRegistry.register` |
| `connector_created` | `ConnectorFactory.create` |
| `connector_validated` | `ConnectorValidator` |
| `connector_session_started` | `ConnectorSession.start` |
| `connector_session_finished` | `ConnectorSession.finish` |

Os eventos utilizam o logging canônico do CORE, incluem o campo estruturado
`event` e contexto mínimo de rastreabilidade, sem impor handler ou destino.

## 5. Testes executados

### 5.1 Suíte dedicada

Comando:

```powershell
python -m pytest -p no:cacheprovider tests\test_connector_abstraction_spr008r.py -q
```

Resultado:

```text
40 passed in 2.61s
```

A suíte dedicada validou:

- API pública e constantes de versão;
- abstração efetiva de `Connector`;
- imutabilidade superficial e profunda;
- isolamento contra mutação dos inputs;
- serialização determinística e round-trip de todos os modelos;
- rejeição de campos, versões, tipos e JSON inválidos;
- invariantes de contexto, sessão e resultado;
- transições terminais imutáveis de sessão;
- registro, consulta, duplicidade e enumeração determinística;
- criação genérica e validação contratual pela Factory;
- preservação da causa em falhas de construção;
- emissão dos cinco eventos estruturados obrigatórios;
- ausência de imports e chamadas proibidos no pacote.

### 5.2 Validações estáticas

Foram aprovados:

- parsing AST dos oito arquivos de código e teste envolvidos;
- leitura UTF-8;
- limite PEP-8 de 88 caracteres por linha;
- type hints nas superfícies públicas;
- docstrings nos módulos, classes e métodos públicos;
- importação pela fachada `cko.core`;
- ausência de dependências externas adicionadas.

## 6. Cobertura

A cobertura foi medida com `trace`, da biblioteca padrão, sobre a suíte dedicada.

| Módulo | Statements | Cobertura |
|---|---:|---:|
| `connectors.__init__` | 8 | 100% |
| `connectors.contracts` | 12 | 100% |
| `connectors.errors` | 33 | 100% |
| `connectors.factory` | 41 | 97% |
| `connectors.models` | 457 | 95% |
| `connectors.registry` | 78 | 100% |
| `connectors.validator` | 105 | 93% |
| **Total ponderado** | **734** | **96%** |

O resultado supera a cobertura mínima requerida de 90% para o novo código.

## 7. Regressão

A regressão cumulativa foi executada sobre todo o diretório `tests` em pasta
temporária local dedicada, após tentativas em temporários do workspace terem sido
afetadas por permissões do Google Drive e do sandbox.

Resultado final da execução integral:

```text
486 passed, 2 failed in 7.89s
```

As duas falhas são legadas e não foram introduzidas pela SPR-008R:

1. `tests/test_file_metadata.py::test_collect_metadata`: o teste chama
   `collect_metadata(sample, calculate_hash=True)`, mas o contrato legado atual
   não possui esse parâmetro.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`:
   o teste deixa `cko.db` aberto e o teardown do Windows não consegue remover o
   arquivo, retornando `WinError 32`.

Essas falhas não importam nem exercitam `cko.core.connectors`; os componentes
legados relacionados não foram alterados porque isso violaria o escopo expresso
da SPR-008R. Os demais 486 testes cumulativos, incluindo toda a suíte dedicada,
foram aprovados.

## 8. Compatibilidade

- Python 3.13: validado em Python 3.13.14;
- UTF-8: validado;
- biblioteca padrão no código de produção: atendido;
- dependências externas novas: nenhuma;
- API pública anterior: preservada por exportação exclusivamente aditiva;
- estado global: não introduzido;
- serialização: schema 1.0 estrito e versionado;
- implementação concreta: nenhuma;
- filesystem, banco, rede, cloud, API, OCR e IA no pacote: ausentes.

## 9. Observações técnicas

O Registry armazena internamente o descritor serializável separado do construtor
injetado. O construtor é mecanismo de composição e não integra nenhum modelo
serializado. Essa separação mantém os modelos puros e permite que aplicações
futuras componham adaptadores sem o CORE conhecer tecnologias concretas.

O lifecycle de sessão não utiliza mutabilidade. `ConnectorSession.start` cria o
snapshot inicial e `ConnectorSession.finish` retorna um novo snapshot terminal.
Estados terminais não podem ser reabertos.

Os timestamps são fornecidos pelo consumidor e normalizados para UTC. O núcleo
não escolhe relógio, não introduz nondeterminismo implícito e permanece compatível
com testes e futuras injeções de `Clock`.

A enumeração do Registry, as coleções de capacidades e os JSONs produzidos são
determinísticos. Nenhuma ordem de registro altera o resultado enumerado.

Nenhuma Sprint posterior foi iniciada e nenhum componente fora do escopo foi
modificado para corrigir ocorrências legadas identificadas pela regressão.

## 10. Conclusão

A infraestrutura canônica de abstração de conectores da SPR-008R foi
implementada integralmente no namespace `cko.core.connectors`, com contratos
públicos tipados, documentados, imutáveis, serializáveis e versionados. Registry,
Factory e Validator atendem aos requisitos funcionais e arquiteturais. Os cinco
eventos estruturados obrigatórios foram implementados. A suíte dedicada foi
aprovada com 40 testes e 96% de cobertura ponderada.

A regressão cumulativa aprovou 486 testes e identificou duas ocorrências legadas
independentes da SPR-008R. Elas foram registradas sem alteração dos componentes
afetados, preservando rigorosamente a fronteira desta Sprint.
