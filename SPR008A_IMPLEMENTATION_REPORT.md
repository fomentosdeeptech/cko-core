# SPR-008A — CKO CORE SDK — Relatório de Implementação

## Identificação

- Sprint: SPR-008A
- Objeto: fundação do núcleo canônico do CKO CORE SDK
- Workspace: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`
- Baseline aplicada: Baseline Arquitetural 1.0
- Arquitetura de referência: CKO-ARCH-001
- Data da validação: 14/07/2026
- Runtime de homologação técnica: Python 3.13.14

## Arquitetura implementada

A implementação cria o namespace aditivo `cko.core` como núcleo compartilhado,
neutro de produto e independente de adaptadores concretos. A direção das
dependências permanece voltada para contratos, identidade, modelos e metadados
do núcleo, de acordo com Ports and Adapters e com o monólito modular incremental
definido pela Baseline 1.0.

Nenhum módulo legado foi movido ou removido. Nenhuma alteração foi realizada em
Governança, Discoveries, banco canônico, Releases ou Checkpoints.

```text
src/cko/core
├── contracts
├── models
├── identity
├── metadata
├── exceptions
├── logging
├── config
└── utils
```

## Módulos criados

### Contracts

Contratos estruturais tipados para `Repository`, `Clock`, `EventPublisher`,
`Plugin` e `Identifiable`. Os contratos não selecionam banco, transporte,
framework ou aplicação consumidora.

### Canonical Models

Modelos imutáveis para `CanonicalDocument`, `DocumentLocation`, `InventoryItem`
e `CanonicalEvent`, com validação de consistência, datas com fuso e metadados
defensivamente imutáveis.

### Identity

Implementação de `CanonicalId` baseada em UUID, `SemanticVersion` com leitura e
ordenação de precedência semântica e `Origin` para origem técnica rastreável.

### Metadata

`UniversalMetadata` representa atributos universais sem incorporar taxonomia,
classificação ou regra de produto.

### Exceptions

Hierarquia pública iniciada em `CKOError`, com especializações para contrato,
modelo, identidade, metadados e configuração.

### Logging

Infraestrutura JSON baseada em `logging`, com timestamp UTC, nível, logger,
mensagem, evento, contexto e exceção. A configuração é idempotente por namespace.

### Configuration

`SDKConfig` e `load_config` carregam TOML ou JSON e aplicam sobrescritas por
variáveis `CKO_*`. A implementação usa somente a biblioteca padrão e aceita
extensões escalares controladas.

### Utilities

Utilitários puros para horário UTC, validação de datas com fuso e normalização de
texto não vazio.

## Arquivos criados

### SDK

- `src/cko/core/__init__.py`
- `src/cko/core/contracts/__init__.py`
- `src/cko/core/contracts/base.py`
- `src/cko/core/models/__init__.py`
- `src/cko/core/models/document.py`
- `src/cko/core/models/event.py`
- `src/cko/core/identity/__init__.py`
- `src/cko/core/identity/identifier.py`
- `src/cko/core/identity/version.py`
- `src/cko/core/identity/origin.py`
- `src/cko/core/metadata/__init__.py`
- `src/cko/core/metadata/universal.py`
- `src/cko/core/exceptions/__init__.py`
- `src/cko/core/exceptions/errors.py`
- `src/cko/core/logging/__init__.py`
- `src/cko/core/logging/structured.py`
- `src/cko/core/config/__init__.py`
- `src/cko/core/config/settings.py`
- `src/cko/core/utils/__init__.py`
- `src/cko/core/utils/text.py`
- `src/cko/core/utils/time.py`

### Testes e evidências

- `tests/test_core_sdk_spr008a.py`
- `tests/fixtures/spr008a_config.toml`
- `tests/fixtures/spr008a_config.yaml`
- `SPR008A_IMPLEMENTATION_REPORT.md`

## Arquivo atualizado

- `pyproject.toml`: descrição do SDK e requisito `requires-python = ">=3.13"`.

## Testes executados

Comando principal:

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests\test_core_sdk_spr008a.py -q -p no:cacheprovider
```

Resultado no Python 3.13.14:

```text
9 passed in 0.81s
```

Os testes validam:

- importação dos oito pacotes públicos;
- construção e consistência dos modelos canônicos;
- identidade UUID e precedência de versão semântica;
- contratos estruturais verificáveis em runtime;
- configuração TOML e sobrescrita por ambiente;
- rejeição de formato de configuração não suportado;
- emissão de logging JSON;
- datas UTC com fuso explícito.

Uma execução adicional da suíte legada completa coletou os testes existentes.
Foram aprovados 14 testes; testes antigos dependentes de escrita no diretório
temporário do Windows não puderam concluir porque o sandbox negou acesso. As
falhas observadas foram exclusivamente `PermissionError` e impossibilidade de
abrir bancos SQLite temporários dos testes legados. Nenhum banco canônico foi
aberto ou alterado.

## Cobertura

A cobertura do novo namespace foi medida no Python 3.13 com o módulo `trace` da
biblioteca padrão e linhas executáveis identificadas pelo próprio módulo:

```text
331/390 instruções executáveis — 84,9%
```

O percentual cobre somente `src/cko/core` e a suíte da SPR-008A. Não mistura
código legado no denominador.

## Validações adicionais

- análise sintática: 22 arquivos Python aprovados;
- codificação: arquivos Python em UTF-8 sem BOM;
- PEP-8: nenhuma linha do SDK acima de 88 caracteres após revisão;
- marcadores incompletos: nenhum encontrado;
- componentes excluídos: nenhuma implementação ou importação de OCR, Discovery,
  RAG, embeddings, SQLite, IA, Graph, parsing ou indexação;
- dependências: nenhum import externo no runtime de `cko.core`.

## Limitações deliberadas

- a Sprint entrega fundação e contratos; não fornece adaptadores concretos;
- `Repository` inicia com a fronteira mínima de leitura, sem política de
  persistência ou transação;
- logging é configurável pelo consumidor e não cria arquivo ou serviço externo;
- configuração não interpreta YAML, evitando dependência de runtime;
- não há funcionalidade de negócio, automação operacional ou migração;
- a execução integral dos testes legados permanece condicionada à liberação de
  escrita no diretório temporário do ambiente de teste.

## Próximos passos

1. Homologar formalmente os contratos públicos desta fundação.
2. Manter novos motores dependentes de `cko.core`, nunca de adaptadores concretos.
3. Criar testes contratuais por adaptador nas Sprints que os introduzirem.
4. Expandir contratos somente dentro do escopo aprovado de cada Sprint.
5. Reexecutar a suíte legada completa em ambiente com temporário gravável.

## Respostas de validação

1. **Todos os módulos foram criados?** Sim. Os oito pacotes solicitados estão
   presentes e importáveis.
2. **A estrutura segue a Baseline?** Sim. É aditiva, modular, SDK First,
   independente de infraestrutura e preserva o legado.
3. **Existem dependências externas?** Não no runtime do novo SDK. `pytest` é
   usado apenas nos testes e `setuptools` permanece como backend de build.
4. **O SDK está pronto para receber os próximos motores?** Sim, por contratos,
   modelos, identidade, metadados, erros, observabilidade, configuração e
   utilitários estáveis.
5. **A SPR-008A pode ser homologada?** Sim. Os critérios funcionais da Sprint
   foram atendidos e validados no Python 3.13.14.

## Declaração

**SPR-008A CONCLUÍDA**

