# SPR-008H — CKO CORE SDK — Discovery Capability Model Foundation

## 1. Objetivo

Foi implementado o modelo canônico, imutável, versionado e independente de
infraestrutura para declaração, validação, negociação e resolução de capacidades
do Discovery. A implementação pertence exclusivamente ao namespace `cko.core` e
respeita a Baseline Arquitetural 1.0.

## 2. Arquitetura

A fundação foi organizada em quatro módulos coesos sob
`cko.core.discovery`:

- `capability_models.py`: modelos, invariantes e serialização;
- `capability_errors.py`: hierarquia pública de erros;
- `capability_validation.py`: validação e resolução automática;
- `capability_negotiation.py`: negociação determinística e logging.

Não foi criada arquitetura paralela. Não há adaptador, provider concreto,
scanner, acesso externo ou dependência fora da biblioteca padrão e de
contratos já homologados em `cko.core`.

## 3. Modelos

Foram criados:

- `CapabilityCategory`, enum pública com categorias canônicas;
- `CapabilityRequirementType`, enum com `required`, `optional` e `prohibited`;
- `CapabilityRequirement`, requisito imutável com versão mínima e versões
  incompatíveis;
- `Capability`, declaração imutável com id, nome, descrição, categoria, versão,
  dependências, incompatibilidades, metadados e schema;
- `CapabilitySet`, coleção imutável e ordenada por identidade;
- `CapabilityReport`, relatório auditável de resultados.

Mapas e sequências recebidos são copiados e congelados. Os modelos públicos
centrais usam o schema `1.0`.

## 4. Contratos

`CapabilitySet` oferece união, diferença, interseção e comparação por identidade
e versão semântica. Declarações divergentes para a mesma identidade são rejeitadas
explicitamente. `Capability`, `CapabilityRequirement`, `CapabilitySet` e
`CapabilityReport` possuem `to_dict`, `to_json`, `from_dict` e `from_json` com
envelopes estritos e rejeição de campos desconhecidos, ausentes ou schemas não
suportados.

## 5. Negociação

`CapabilityNegotiationEngine` negocia entre Provider, Pipeline, Executor e
Consumer. O algoritmo:

1. ordena identidades de modo determinístico;
2. aceita somente capacidades declaradas pelos quatro participantes;
3. seleciona a menor versão semântica comum declarada;
4. registra capacidades não comuns como rejeitadas e identifica os papéis
   ausentes;
5. aplica requisitos e validação sobre o conjunto comum;
6. produz `CapabilityReport` auditável.

Com entradas e timestamp idênticos, a serialização do relatório é idêntica.

## 6. Resolução

`CapabilityResolver` recebe o conjunto solicitado e um catálogo de capacidades
disponíveis. Ele expande dependências transitivas em ordem determinística, inclui
dependências opcionais quando válidas e disponíveis, rejeita dependências
obrigatórias ausentes ou incompatíveis e entrega somente um conjunto aprovado
pelo motor de validação.

## 7. Validação

`CapabilityValidationEngine` verifica:

- requisitos obrigatórios ausentes;
- requisitos opcionais;
- capacidades proibidas;
- dependências obrigatórias e opcionais;
- versões mínimas;
- versões explicitamente incompatíveis;
- conflitos declarados entre capacidades.

`validate()` retorna relatório sem mutar as entradas. `ensure_valid()` retorna o
conjunto aceito ou lança o erro público específico.

## 8. Erros públicos

Foi criada a hierarquia pública:

- `CapabilityError`;
- `CapabilityConflictError`;
- `CapabilityDependencyError`;
- `CapabilityValidationError`;
- `CapabilityNegotiationError`;
- `InvalidCapabilityError`.

Todos derivam da hierarquia pública do Discovery.

## 9. Arquivos criados

- `src/cko/core/discovery/capability_errors.py`;
- `src/cko/core/discovery/capability_models.py`;
- `src/cko/core/discovery/capability_validation.py`;
- `src/cko/core/discovery/capability_negotiation.py`;
- `tests/test_discovery_capability_model_spr008h.py`;
- `SPR008H_IMPLEMENTATION_REPORT.md`.

## 10. Arquivos alterados

- `src/cko/core/discovery/__init__.py`: exports exclusivamente aditivos;
- `src/cko/core/__init__.py`: exports exclusivamente aditivos.

Nenhum contrato público homologado foi removido ou alterado.

## 11. Testes

A suíte dedicada possui 35 testes aprovados. Ela valida imutabilidade profunda,
serialização, desserialização estrita, schema, álgebra de conjuntos, comparação,
requisitos, versões, dependências transitivas, conflitos, negociação, resolução,
logging, exports públicos, type hints, docstrings, UTF-8 sem BOM, PEP-8 e ausência
de infraestrutura.

Resultado dedicado final: `35 passed in 1.73s`.

## 12. Cobertura

`coverage.py` não está instalado no runtime. Foi usada a ferramenta `trace` da
biblioteca padrão com contagem, resumo e linhas ausentes, executando a suíte
dedicada sobre os quatro módulos novos.

Resultado final:

- `capability_errors.py`: 100% de 15 linhas rastreáveis;
- `capability_models.py`: 91% de 502 linhas rastreáveis;
- `capability_negotiation.py`: 96% de 108 linhas rastreáveis;
- `capability_validation.py`: 90% de 180 linhas rastreáveis;
- cobertura ponderada pelos totais informados: aproximadamente 91,6%.

A meta mínima de 90% foi atingida. Os percentuais unitários são arredondados pela
ferramenta padrão.

## 13. Regressão

A regressão obrigatória composta pelas suítes SPR-008A, SPR-008B, SPR-008C,
SPR-008D, SPR-008E, SPR-008F, SPR-008G e SPR-008H foi aprovada integralmente.

Resultado final: `185 passed in 4.36s`.

Classificação das ocorrências:

- falha funcional: nenhuma;
- falha arquitetural: nenhuma;
- falha ambiental: runtime disponível em Python 3.12.13, abaixo do Python 3.13
  declarado pelo projeto;
- falha legada preexistente: nenhuma observada na regressão obrigatória A–H.

## 14. Limitações deliberadas

Não foram implementados scanners, providers concretos, filesystem, banco,
SQLite, OCR, IA, Graph, Google Drive, OneDrive, APIs, persistência, rede,
threads ou multiprocessing. A fundação opera somente sobre declarações já
fornecidas em memória.

## 15. Compatibilidade

As APIs públicas das SPR-008A até SPR-008G foram preservadas. Os dois arquivos
`__init__.py` receberam apenas imports e nomes adicionais. A regressão integral
do recorte homologado confirma a compatibilidade comportamental.

As validações adicionais confirmaram AST válido, imports públicos, UTF-8 sem BOM,
ausência de placeholder, ausência de `NotImplementedError`, ausência de funções
vazias, ausência de imports de infraestrutura e comprimento máximo de 99
caracteres. `pycodestyle` não está instalado; a verificação PEP-8 foi realizada
por suíte automatizada, AST e inspeção determinística de fonte.

## 16. Respostas obrigatórias

1. O modelo de capacidades foi implementado? **Sim.**
2. As capacidades são imutáveis? **Sim, inclusive metadados e sequências.**
3. Existe negociação determinística? **Sim.**
4. Existe resolução automática? **Sim.**
5. Dependências são validadas? **Sim.**
6. Conflitos são detectados? **Sim.**
7. Há dependência de infraestrutura? **Não.**
8. Há acesso ao filesystem? **Não.**
9. Há acesso a banco? **Não.**
10. Há providers concretos? **Não.**
11. Há persistência? **Não.**
12. A API pública permaneceu compatível? **Sim.**
13. A regressão SPR-008A–008H foi aprovada? **Sim, 185 testes aprovados.**
14. A cobertura mínima foi atingida? **Sim, aproximadamente 91,6%.**
15. A SPR-008H pode ser homologada? **Sim, com ressalva ambiental.**

## 17. Declaração final

A SPR-008H está implementada conforme a Baseline Arquitetural 1.0, exclusivamente
em `cko.core`, sem arquitetura paralela, sem infraestrutura e sem iniciar qualquer
trabalho da SPR-008I. A implementação, os testes, a cobertura, a regressão e as
verificações estáticas foram aprovados. O resultado é tecnicamente homologável
com ressalva ambiental referente ao runtime Python 3.12.13 disponível, enquanto o
projeto declara compatibilidade Python 3.13. Aguarda-se homologação formal.
