# SPR-008W — Relatório de Implementação

## 1. Identificação

- Sprint: SPR-008W — Unit of Work Foundation
- Produto: CKO CORE SDK
- Namespace canônico: `cko.core.uow`
- Schema público: `1.0`
- Versão pública: `1.0.0`
- Data de validação: 23/07/2026
- Plataforma validada: Windows, Python 3.13 e UTF-8

## 2. Objetivo

Foi implementada a fundação canônica de Unit of Work para coordenar operações
lógicas sobre múltiplas instâncias dos ports públicos `CheckpointRepository`,
`Storage` e `Connector`.

A implementação oferece lifecycle validado, commit lógico, rollback
compensatório, rollback automático, proteção contra operações aninhadas,
registro controlado de ports, resultados imutáveis e histórico ordenado. O
coordenador não conhece providers, adapters, banco, filesystem ou Runtime.

## 3. Arquitetura

A solução segue Ports and Adapters:

- `UnitOfWork` é o port público abstrato do coordenador;
- `DefaultUnitOfWork` implementa o lifecycle e a coordenação;
- `UnitOfWorkRepository` registra exclusivamente um dos três ports homologados;
- `UnitOfWorkOperation` associa uma ação lógica a uma compensação opcional;
- `UnitOfWorkValidator` centraliza validações de estado, transição, contexto,
  registros, operações e resultados;
- os modelos públicos são imutáveis e não contêm detalhes físicos;
- exceções tipadas distinguem validação, estado, registro, execução, rollback e
  fechamento.

Nenhum singleton, estado global mutável, ORM, I/O físico ou configuração de
logging foi adicionado.

## 4. Arquivos

Criados:

- `src/cko/core/uow/__init__.py`
- `src/cko/core/uow/contracts.py`
- `src/cko/core/uow/engine.py`
- `src/cko/core/uow/models.py`
- `src/cko/core/uow/validator.py`
- `src/cko/core/uow/errors.py`
- `tests/test_unit_of_work_foundation_spr008w.py`
- `SPR008W_IMPLEMENTATION_REPORT.md`

Alterado:

- `src/cko/core/__init__.py`, somente para reexportar a nova API canônica.

## 5. Contratos públicos

A API de `cko.core.uow` exporta:

- `UnitOfWork`
- `UnitOfWorkContext`
- `UnitOfWorkResult`
- `UnitOfWorkState`
- `UnitOfWorkOperation`
- `UnitOfWorkRepository`
- `DefaultUnitOfWork`
- `UnitOfWorkValidator`
- `UnitOfWorkAction`
- `UnitOfWorkCompensation`
- `RepositoryCollection`
- `UOW_SCHEMA_VERSION`
- `UOW_VERSION`
- a hierarquia completa de exceções tipadas.

Os mesmos símbolos são reexportados pela fachada `cko.core`.

## 6. Componentes

### 6.1 `UnitOfWorkContext`

Mantém `unit_of_work_id`, `correlation_id`, metadata lógica profundamente
congelada e versão de schema. O validator rejeita campos físicos ou sensíveis,
como path, URL, conexão, SQL, credenciais, segredo e token.

### 6.2 `UnitOfWorkRepository`

Associa uma identidade lógica única a uma instância de:

- `CheckpointRepository`;
- `Storage`;
- `Connector`.

O tipo lógico é derivado como `checkpoint_repository`, `storage` ou
`connector`. Instâncias e identificadores duplicados são rejeitados.

### 6.3 `UnitOfWorkOperation`

Representa uma operação por:

- identidade única;
- identidade do port registrado;
- callback de ação;
- callback compensatório opcional;
- metadata lógica imutável.

A ação recebe somente o port público e o contexto da Unit of Work. A
compensação recebe o port público, o valor produzido pela ação e o contexto.

### 6.4 `UnitOfWorkResult`

Registra de forma imutável:

- sucesso;
- estado;
- evento;
- identidade da Unit of Work;
- timestamp UTC;
- identidades opcionais de operação e registro;
- valor lógico;
- erro tipado;
- metadata segura.

### 6.5 `DefaultUnitOfWork`

Implementa:

- `begin()`;
- `commit()`;
- `rollback()`;
- `register()`;
- `unregister()`;
- `clear()`;
- `execute()`;
- `status()`;
- `history()`;
- `close()`;
- `__enter__()` e `__exit__()`.

## 7. Estados e transições

Estados canônicos:

- `created`;
- `started`;
- `committed`;
- `rolled_back`;
- `closed`;
- `failed`.

Transições aceitas:

- `created -> started`;
- `created -> closed`;
- `started -> committed`;
- `started -> rolled_back`;
- `started -> failed`;
- `failed -> rolled_back`;
- `failed -> closed`;
- `committed -> closed`;
- `rolled_back -> closed`.

`closed` é terminal. Begin, commit, rollback e close duplicados são rejeitados
com exceções tipadas. Commit e rollback exigem lifecycle compatível.

## 8. Lifecycle

### 8.1 Begin

`begin()` valida o contexto, preserva a identidade original e realiza a
transição única para `started`.

### 8.2 Execute

`execute()` exige estado `started`, registro existente e identidade de operação
única. Operações reentrantes são bloqueadas. Resultados públicos com
`success=False` são tratados como falha.

Uma exceção de ação:

1. registra `uow_failed`;
2. move a Unit of Work para `failed`;
3. inicia rollback automático;
4. preserva exception chaining;
5. retorna ao chamador por exceção tipada.

### 8.3 Commit

`commit()` encerra logicamente a unidade após todas as ações executadas com
sucesso. Nenhuma API de transação física é presumida nos ports existentes.

### 8.4 Rollback

`rollback()` executa compensações em ordem estritamente inversa. Todas as
compensações são tentadas mesmo se uma delas falhar. Falhas agregadas deixam o
estado como `failed` e produzem `UnitOfWorkRollbackError`.

Registros usados por operações pendentes não podem ser removidos nem limpos,
preservando a capacidade de compensação.

### 8.5 Context manager e fechamento

`with DefaultUnitOfWork(...):` inicia automaticamente a Unit of Work. Na saída:

- commit explícito é preservado;
- trabalho ainda iniciado sofre rollback automático;
- exceções do bloco não são suprimidas;
- registros são liberados;
- o estado final é `closed`.

## 9. Atomicidade lógica

Os ports homologados não possuem métodos transacionais comuns. Por isso, a
fundação implementa atomicidade lógica sem inventar contratos físicos:

- ações são coordenadas dentro de um único lifecycle;
- commit confirma o conjunto lógico;
- rollback executa compensações fornecidas pela aplicação;
- compensações usam somente os mesmos ports públicos;
- ordem reversa preserva dependências entre operações;
- falhas de ação provocam rollback automático;
- falhas de compensação são explícitas e auditáveis.

Operações somente de leitura ou naturalmente idempotentes podem omitir
compensação. Operações mutáveis devem fornecer a compensação correspondente.

## 10. Integração

A suíte valida múltiplas instâncias e integração por injeção com:

- `CheckpointRepository`;
- `Storage`;
- `Connector`.

O coordenador somente entrega a instância do port ao callback. Ele não chama
métodos particulares de providers, não inspeciona conexões e não converte
modelos para formatos físicos.

## 11. Isolamento arquitetural

A inspeção AST e textual confirmou ausência de imports ou referências a:

- `FilesystemStorage`;
- `SQLiteStorage`;
- `sqlite3`;
- `pathlib`;
- `Runtime`;
- `cko.core.runtime`;
- adapters de `cko.core.storage.filesystem`;
- adapters de `cko.core.storage.sqlite`.

O código de produção importa apenas contratos públicos homologados e módulos da
biblioteca padrão.

## 12. Logging

Foram implementados os eventos estruturados obrigatórios:

- `uow_created`;
- `uow_started`;
- `uow_registered`;
- `uow_commit`;
- `uow_rollback`;
- `uow_closed`;
- `uow_failed`.

Também é registrado `uow_operation` para cada ação concluída. O contexto contém
somente identidades lógicas, estado, tipo de port, contagens e códigos de erro.
Valores de operação, payloads, paths, URLs, conexões, credenciais e SQL não são
registrados.

## 13. Testes dedicados

Comando final:

`python -m pytest -p no:cacheprovider
--basetemp=runtime\temp\pytest_spr008w
tests\test_unit_of_work_foundation_spr008w.py -q`

Resultado:

- 26 testes aprovados;
- 0 falhas;
- duração final: 0,86 segundo.

A suíte cobre:

- begin, commit, rollback e close;
- rollback automático em ação com exceção;
- rollback automático pelo context manager;
- commit explícito no context manager;
- compensação reversa;
- falha de compensação com tentativa best-effort;
- múltiplos CheckpointRepository, Storage e Connector;
- registro, remoção, limpeza e duplicidade;
- proteção de registros com operações pendentes;
- operação duplicada;
- operação aninhada;
- todos os estados e transições;
- fechamento e ações posteriores ao fechamento;
- validação de contexto, resultados e metadata;
- resultados públicos malsucedidos;
- exception chaining;
- logging estruturado;
- AST, UTF-8 e imports proibidos;
- limite de linha compatível com PEP 8.

## 14. Cobertura

A cobertura foi medida com `trace`, da biblioteca padrão, sem adicionar
dependências:

| Módulo | Linhas executáveis | Cobertura |
|---|---:|---:|
| `__init__.py` | 7 | 100% |
| `contracts.py` | 38 | 100% |
| `engine.py` | 333 | 100% |
| `errors.py` | 58 | 100% |
| `models.py` | 153 | 100% |
| `validator.py` | 99 | 100% |
| **Total ponderado** | **688** | **100%** |

O resultado supera a cobertura mínima obrigatória de 90%.

## 15. Regressão

Comando oficial:

`python -m pytest -p no:cacheprovider
--basetemp=runtime\temp\pytest_spr008u_regression tests -q`

Resultado final:

- 686 testes aprovados;
- 2 falhas;
- nenhuma falha nova;
- duração final: 14,70 segundos.

As duas falhas são exatamente as exceções legadas homologadas:

1. `collect_metadata()` não aceita o argumento legado `calculate_hash`;
2. o arquivo SQLite legado `cko.db` permanece aberto durante teardown no
   Windows.

Uma execução preliminar com um novo `basetemp` dentro do Google Drive foi
descartada porque o filesystem sincronizado bloqueou a criação de bancos SQLite
e artefatos temporários. A execução oficial reutilizou o diretório de regressão
homologado e reproduziu o baseline esperado.

## 16. Compatibilidade

A implementação foi validada com:

- Python 3.13;
- Windows;
- UTF-8;
- PowerShell 5.1 para os comandos de validação;
- PEP 8, incluindo limite de 79 caracteres;
- biblioteca padrão e contratos já presentes no SDK.

Não foram adicionadas dependências, ORM, framework, driver, cloud SDK ou pacote
de cobertura.

## 17. Observações técnicas

- A Unit of Work é de uso único; após commit, rollback ou close, não é reaberta.
- Atomicidade física permanece responsabilidade de cada adapter quando existir
  suporte próprio. A fundação não altera nem amplia contratos homologados.
- Atomicidade entre tecnologias heterogêneas é obtida por compensação lógica,
  não por protocolo distribuído ou conhecimento de provider.
- O histórico é retornado como tupla imutável e preserva a ordem dos eventos.
- Metadata de modelos é profundamente congelada.
- Timestamps públicos são normalizados para UTC.
- IDs de operações são únicos dentro de uma Unit of Work.
- Falhas de compensação não impedem a tentativa das compensações restantes.

## 18. Contratos homologados e limite da Sprint

Nenhum contrato público anterior foi alterado. A mudança é exclusivamente
aditiva sob `cko.core.uow`, com reexports na fachada `cko.core`.

ARCH-001 não foi atualizado. Nenhuma Sprint posterior foi iniciada. Não foram
implementados cache, scheduler, transação distribuída, novos adapters,
persistência direta, integração com Runtime ou mudanças fora do escopo da
SPR-008W.
