# Relatório de Preparação da Baseline

> **Status do documento — registro histórico:** este relatório representa exclusivamente uma fotografia da fase de preparação, anterior à publicação da baseline. A baseline foi posteriormente consolidada no HEAD `87d3e2ad46dd9820b16b22cbbf62683f2a545305`. Portanto, as observações abaixo não descrevem o estado atual da plataforma; o documento permanece preservado apenas como registro histórico de auditoria.

## Resumo da auditoria

A auditoria foi realizada exclusivamente por inspeção do estado Git do repositório do projeto CKO, sem executar operações de staging, commit, push, merge, checkout ou restore.

### Estado observado

- Repositório Git detectado em: `CORE`
- Arquivos modificados: `.gitignore`, `pyproject.toml`
- Arquivos untracked: vários arquivos de documentação, código, testes, scripts, configurações e artefatos de reports

## Arquivos inspecionados

### Modified

- `.gitignore`
- `pyproject.toml`

### Untracked

A lista abaixo representa os arquivos e diretórios não rastreados no estado atual:

- `.vscode/extensions.json`
- `.vscode/tasks.json`
- `ARQUITETURA_ATUAL.txt`
- `README_SPR_003.md`
- `README_SPR_004.md`
- `SPR005_MANIFEST.json`
- `SPR006A_MANIFEST.json`
- `SPR007B_ADVANCED_ENGINE.cmd`
- `SPR007B_ADVANCED_ENGINE.ps1`
- `advanced_engine.py`
- `config/`
- `docs/`
- `inventory.txt`
- `migrations/`
- `reports/`
- `scripts/`
- `src/`
- `tests/`

## Classificação sugerida para a baseline

### Deve entrar na baseline

- Arquivos de código-fonte principais que representam o produto.
- Arquivos de configuração essenciais ao projeto.
- Documentação oficial relevante para a operação e entendimento do projeto.
- Arquivos de testes que validem a funcionalidade principal.

### Não deve entrar na baseline

- Artefatos temporários ou gerados localmente.
- Arquivos de runtime, logs, reports temporários e caches.
- Configurações locais específicas de ambiente, como `.vscode/`.
- Arquivos de backup, checkpoints temporários e dados operacionais não essenciais.

### Requer validação humana

- `pyproject.toml`, porque houve alteração na estrutura de configuração e pode refletir uma mudança de empacotamento do projeto.
- Arquivos de documentação e scripts que possam ser parte da operação ou do pacote, mas ainda precisam de avaliação para decidir se pertencem à baseline oficial.

## Análise do `pyproject.toml`

O arquivo `pyproject.toml` está marcado como modified porque houve alteração de configuração de empacotamento.

### Diferença observada

As linhas alteradas foram principalmente:

- substituição de sintaxe compacta por sintaxe legível:
  - `name="cko"` passou a ser `name = "cko"`
  - `version="0.1.0"` passou a ser `version = "0.1.0"`
  - `description="Corporate Knowledge Organizer"` passou a ser `description = "Corporate Knowledge Organizer"`
  - `requires-python=">=3.11"` passou a ser `requires-python = ">=3.11"`
- inclusão de seções de build-system e setuptools:
  - `[build-system]`
  - `requires = ["setuptools>=68"]`
  - `build-backend = "setuptools.build_meta"`
  - `[tool.setuptools]`
  - `package-dir = {"" = "src"}`
  - `[tool.setuptools.packages.find]`
  - `where = ["src"]`

### Recomendação

Essa alteração deve permanecer somente se o objetivo for formalizar a instalação e o empacotamento do projeto. Caso a baseline seja destinada a preservar o estado atual do repositório sem introduzir uma mudança estrutural de packaging, essa alteração merece validação humana antes de entrar na baseline oficial.

## Verificação do `.gitignore`

O `.gitignore` está funcionando para alguns padrões esperados.

### Evidência observada

- `.vscode/settings.json` foi identificado como ignorado pelo `git check-ignore`.
- `reports/SPR007B_ADVANCED_REPORT.json` também foi considerado ignorado.

### Pontos de atenção

- O padrão atual não ignora o diretório `.vscode/` inteiro, apenas o arquivo `settings.json`; isso permite que outros arquivos locais, como `extensions.json` e `tasks.json`, continuem aparecendo como untracked.
- A política de ignorar artefatos de reports pode ser refinada conforme a estratégia oficial de baseline.

## Riscos encontrados

- Há um volume grande de arquivos untracked ainda não avaliados para inclusão.
- O estado atual não está suficientemente limpo para uma baseline oficial sem revisão humana.
- O arquivo `pyproject.toml` merece validação antes de ser aceito como parte da baseline.

## Recomendações antes da primeira baseline

1. Revisar manualmente os arquivos untracked para decidir o que é realmente essencial.
2. Confirmar se `pyproject.toml` deve permanecer com a configuração de build-system e setuptools.
3. Garantir que artefatos temporários e locais estejam fora da baseline.
4. Separar claramente documentação oficial, código-fonte e artefatos operacionais.
5. Somente após essa validação humana, criar a primeira baseline oficial.
