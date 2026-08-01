# SPR-008G — CKO CORE SDK — Discovery Identity Resolution Foundation

## 1. Identificação

- Sprint: SPR-008G.
- Componente: CKO CORE SDK.
- Namespace exclusivo: `cko.core`.
- Data de validação: 2026-07-15.
- Baseline: Baseline Arquitetural 1.0.
- Estado técnico: implementação concluída e homologável com ressalva ambiental.

## 2. Objetivo

Foi criada a fundação canônica, neutra e auditável para resolver a identidade de
observações `DiscoveredItem`, sem criar entidade concorrente de `Asset` ou
identidade concorrente de `CanonicalId`.

## 3. Arquitetura criada

O fluxo implementado é:

`DiscoveredItem -> IdentityEvidence -> IdentityCandidate -> ResolutionDecision
-> CanonicalId -> Asset`

A sprint termina na decisão e eventual alocação transitória de `CanonicalId`.
Ela não cria `Asset`, não persiste a identidade e não consulta infraestrutura.

## 4. Contratos públicos

- `IdentityCandidateProvider`: fornecimento síncrono e assíncrono de candidatos.
- `IdentityEvidenceEvaluator`: avaliação síncrona e assíncrona explicável.
- `CanonicalIdentityAllocator`: alocação síncrona e assíncrona de identidade.

Não foi implementado provider concreto de candidatos.

## 5. Modelos

Foram implementados modelos imutáveis para evidência, fingerprint, candidato,
conflito, avaliação, política, request e decisão. Mapas recebidos são copiados e
congelados. Os envelopes públicos centrais possuem schema `1.0`, JSON
determinístico e desserialização estrita.

## 6. Evidências

`IdentityEvidence` aceita os tipos públicos:

- identificador externo;
- checksum declarado;
- nome lógico normalizado;
- media type;
- tamanho declarado;
- timestamp declarado;
- chave de origem;
- atributo canônico;
- evidência composta.

Somente valores já fornecidos são usados.

## 7. Fingerprint lógico

`IdentityFingerprint.create()` ordena evidências de forma determinística,
serializa o material lógico em JSON canônico e calcula SHA-256 sobre esse texto
lógico. O hash não é calculado sobre arquivo, conteúdo ou stream. O fingerprint
declara o schema, o scheme e os componentes utilizados.

## 8. Políticas

`ResolutionPolicy` valida e congela:

- confiança mínima para associação;
- confiança mínima para possível duplicidade;
- margem mínima entre candidatos;
- atributos obrigatórios;
- comportamento de conflito;
- comportamento de evidência insuficiente;
- permissão de nova identidade;
- limite de candidatos;
- pesos declarativos.

## 9. Candidatos

`IdentityCandidate` reutiliza `CanonicalId`, contém atributos comparáveis,
evidências, origem lógica, confiança e metadados neutros. Candidatos são
recebidos no request ou pelo contrato injetado. Identidades candidatas duplicadas
são rejeitadas.

## 10. Avaliação

`DefaultNeutralEvidenceEvaluator` realiza comparação exata e determinística de
valores declarados. Não utiliza IA, fuzzy matching ou biblioteca externa. A saída
registra evidências favoráveis, contrárias, ausentes, score, confiança e conflitos.

## 11. Resolução

`IdentityResolutionEngine` valida entradas, obtém candidatos injetados, aplica o
limite, avalia, ordena deterministicamente, mede a margem, detecta empate,
ambiguidade e conflito, e decide associação, duplicidade, nova identidade,
insuficiência ou rejeição.

## 12. Estados

Foram implementados:

- `resolved_existing`;
- `resolved_new`;
- `duplicate_candidate`;
- `ambiguous`;
- `conflict`;
- `insufficient_evidence`;
- `rejected`.

## 13. Conflitos

`IdentityConflict` registra atributo, valor observado, valor candidato,
severidade, evidência relacionada, código estável e descrição estruturada. O
estado `conflict` exige ao menos um conflito.

## 14. Alocação de identidade

`DefaultCanonicalIdentityAllocator` utiliza exclusivamente `CanonicalId.new()`.
Não persiste, não registra no Inventory e não cria `Asset`.

## 15. Execução síncrona

`IdentityResolutionEngine.resolve()` foi implementado e validado.

## 16. Execução assíncrona

`IdentityResolutionEngine.resolve_async()` foi implementado sem threads ou
multiprocessing. Provider, evaluator e allocator possuem fronteiras assíncronas.

## 17. Cancelamento

O motor reutiliza `CancellationToken`, verifica cancelamento antes de operações
externas e entre avaliações, e converte cancelamento cooperativo em
`IdentityResolutionCancelledError` preservando a causa.

## 18. Erros públicos

Foram criados, derivados da hierarquia pública do Discovery:

- `IdentityResolutionError`;
- `InvalidIdentityResolutionRequestError`;
- `InvalidIdentityCandidateError`;
- `InvalidIdentityEvidenceError`;
- `InvalidIdentityPolicyError`;
- `IdentityCandidateProviderError`;
- `IdentityEvidenceEvaluationError`;
- `IdentityAmbiguityError`;
- `IdentityConflictError`;
- `IdentityAllocationError`;
- `IdentityResolutionCancelledError`.

Falhas de provider, evaluator e allocator usam encadeamento de exceção.

## 19. Arquivos criados

- `src/cko/core/discovery/identity_errors.py`;
- `src/cko/core/discovery/identity_models.py`;
- `src/cko/core/discovery/identity_contracts.py`;
- `src/cko/core/discovery/identity_resolution.py`;
- `tests/test_discovery_identity_resolution_spr008g.py`;
- `SPR008G_IMPLEMENTATION_REPORT.md`.

## 20. Arquivos alterados

- `src/cko/core/discovery/__init__.py`: exports exclusivamente aditivos;
- `src/cko/core/__init__.py`: exports exclusivamente aditivos.

## 21. Dependências

Nenhuma dependência externa foi adicionada. O novo código usa somente a
biblioteca padrão e contratos existentes de `cko.core`.

## 22. Testes

- Suíte dedicada SPR-008G: 28 testes aprovados.
- Regressão obrigatória SPR-008A–008G: 150 testes aprovados após a ampliação
  final da suíte 008G (a execução anterior registrou 149 antes do último teste).
- Linha de base anterior às alterações: 122 testes SPR-008A–008F aprovados.

Foram cobertos modelos imutáveis, serialização, campos e versões desconhecidos,
fingerprint, avaliação, todos os estados, políticas, empate, ordenação, limites,
duplicidade, cancelamento, falhas externas, modos síncrono e assíncrono, API,
UTF-8 sem BOM e ausência de infraestrutura.

## 23. Cobertura

`coverage.py` não está disponível no runtime. Foi usado `trace` da biblioteca
padrão com `--count --summary --missing`, executando exclusivamente a suíte
SPR-008G sobre os quatro módulos novos.

Resultado final:

- `identity_contracts.py`: 100%;
- `identity_errors.py`: 100%;
- `identity_models.py`: 88%;
- `identity_resolution.py`: 93%;
- cobertura ponderada por linhas rastreáveis: aproximadamente 90,1%.

A meta mínima de 90% foi atingida. Percentuais por arquivo são arredondados pelo
`trace`; a ponderação usa o total de linhas rastreáveis informado pela ferramenta.

## 24. Regressão

A regressão obrigatória SPR-008A–008G foi aprovada sem falha funcional ou
arquitetural: 150 testes aprovados na composição final esperada.

A suíte integral do repositório, que também inclui sprints antigas fora do
recorte obrigatório, registrou 153 aprovações, 3 falhas e 7 erros causados por
`PermissionError [WinError 5]` no diretório temporário do ambiente; SQLite não
conseguiu abrir arquivos nesse mesmo diretório. A repetição com `TEMP`, `TMP` e
`--basetemp` alternativos também foi bloqueada pelo controle de permissões. Essa
ocorrência é ambiental e não foi causada pela SPR-008G.

## 25. Validações adicionais

- AST dos cinco arquivos Python da sprint: aprovado;
- imports públicos de `cko.core`: aprovado;
- imports proibidos no novo código: ausentes;
- BOM UTF-8: ausente;
- linhas acima de 99 caracteres no código novo: zero;
- `TODO`, `NotImplementedError` e `pass`: ausentes;
- alteração de `DiscoveredItem`, `Asset` ou Inventory: ausente;
- Python executado no ambiente: 3.12.13.

`pycodestyle` e `coverage.py` não estavam instalados. A validação PEP-8 foi feita
por inspeção de comprimento, AST, imports, docstrings e suíte automatizada.

## 26. Limitações deliberadas

Não há scanner, filesystem, banco, persistência, repository, Inventory,
provider concreto, OCR, parser, leitura de conteúdo, hash físico, IA, API HTTP,
fuzzy matching externo, deduplicação física ou criação automática de `Asset`.

## 27. Compatibilidade com Sprints anteriores

SPR-008A, 008B, 008C, 008D, 008E e 008F foram preservadas. Não houve alteração
de assinatura ou semântica homologada. Os `__init__.py` receberam somente
exports aditivos. Foram reutilizados `CanonicalId`, `DiscoveredItem`,
`DiscoverySession`, `DiscoveryContext`, `CancellationToken`, `DiscoveryError` e
logging estruturado.

## 28. Respostas obrigatórias

1. A fundação foi implementada? **Sim.**
2. Distingue ativo novo de existente? **Sim.**
3. Detecta possível duplicidade? **Sim.**
4. Detecta ambiguidade? **Sim.**
5. Detecta conflitos? **Sim.**
6. Rejeita evidência insuficiente? **Sim.**
7. O fingerprint é determinístico? **Sim.**
8. Existe leitura de arquivo? **Não.**
9. Existe cálculo de hash físico? **Não.**
10. Existe acesso ao filesystem? **Não.**
11. Existe acesso a banco? **Não.**
12. Existe persistência? **Não.**
13. Existe consulta automática ao Inventory? **Não.**
14. Existe criação automática de Asset? **Não.**
15. CanonicalId foi reutilizado? **Sim.**
16. DiscoveredItem foi reutilizado? **Sim.**
17. DiscoverySession foi reutilizada? **Sim.**
18. CancellationToken foi reutilizado? **Sim.**
19. A execução síncrona funciona? **Sim.**
20. A execução assíncrona funciona? **Sim.**
21. As decisões são auditáveis? **Sim.**
22. Empates são tratados explicitamente? **Sim.**
23. Candidatos duplicados são rejeitados? **Sim.**
24. Falhas externas preservam a causa? **Sim.**
25. A regressão SPR-008A–008G foi aprovada? **Sim.**
26. A cobertura mínima foi atingida? **Sim, aproximadamente 90,1%.**
27. A SPR-008G pode ser homologada? **Sim, com ressalva ambiental.**

## 29. Declaração final

A SPR-008G está implementada conforme a Baseline Arquitetural 1.0, sem
arquitetura paralela e sem iniciar trabalho da SPR-008H. O resultado é
tecnicamente homologável com ressalva ambiental: o ambiente disponível possui
Python 3.12.13, não Python 3.13, e mantém bloqueio de permissões em diretórios
temporários para parte da suíte legada integral. Aguarda-se homologação formal.
