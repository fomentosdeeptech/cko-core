# SPR-008N — CKO CORE SDK — Canonical Query Optimizer Foundation

## 1. Objetivo

Implementar a fundação canônica do Query Optimizer da Plataforma CKO para
transformar um `QueryPlan` em outro `QueryPlan` logicamente equivalente, de forma
determinística, reproduzível, auditável, reversível e independente de
infraestrutura.

A implementação apenas reescreve o plano lógico. Nenhuma consulta é executada,
nenhuma estratégia física é escolhida e nenhum banco, cache, filesystem,
persistência, API ou serviço externo é utilizado pelo optimizer.

## 2. Arquitetura

O fluxo implementado é:

`QueryPlan` → `OptimizationPipeline` → `OptimizationRule[]` →
`OptimizerValidator` → `OptimizationResult` → `CostBasedPlanner`.

Todo código novo está sob `cko.core.discovery`, portanto dentro do namespace
exclusivo `cko.core`. A solução depende somente da biblioteca padrão e dos
contratos homologados nas SPR-008I a SPR-008M.

O `CostBasedPlanner` da SPR-008M não foi alterado. Ele permanece responsável pela
escolha posterior de estratégia. Nenhum trabalho da SPR-008O foi iniciado.

## 3. Pipeline

`OptimizationPipeline`:

- ordena regras por prioridade crescente e, em empate, por ID;
- executa múltiplas passagens;
- registra toda aplicação e todo descarte;
- encerra ao atingir ponto fixo ou o máximo configurado de iterações;
- usa fingerprints SHA-256 para detectar estados já visitados e impedir loops;
- valida equivalência após cada transformação;
- valida consistência canônica completa no plano final;
- incorpora histórico, relatório e métricas ao resultado imutável.

O limite padrão é de oito iterações. Regras desabilitadas e regras declaradas como
não determinísticas são registradas como ignoradas. O pipeline não executa query,
não consulta estatísticas externas e não escolhe estratégia física.

## 4. Regras

Foram implementadas as dez regras obrigatórias:

1. `PredicateSimplificationRule` — remove grupos AND/OR unários e dupla negação;
2. `BooleanNormalizationRule` — achata grupos associativos e ordena membros
   comutativos;
3. `RedundantFilterRemovalRule` — remove filtros idempotentes duplicados;
4. `DuplicateProjectionRemovalRule` — remove projeções duplicadas;
5. `ProjectionNormalizationRule` — ordena o conjunto projetado canonicamente;
6. `ConstantExpressionRule` — reduz IN/NOT IN unitário a comparação escalar;
7. `SortNormalizationRule` — remove ordenações exatamente duplicadas e renumera
   prioridades;
8. `LimitNormalizationRule` — converte página/tamanho no offset/limit equivalente;
9. `EmptyPredicateRule` — preserva o conjunto vazio como identidade lógica TRUE;
10. `IdentityTransformationRule` — registra explicitamente o ponto fixo.

Todas operam exclusivamente sobre modelos imutáveis. Nenhuma regra altera o ID,
as estimativas, as justificativas preexistentes ou o timestamp do plano.

## 5. Contexto

`OptimizationContext` contém:

- plano original;
- plano atual;
- estatísticas canônicas serializadas;
- índices lógicos canônicos serializados;
- histórico de decisões;
- número de iterações;
- metadados profundamente imutáveis.

O contexto é substituído a cada decisão, sem mutação dos planos de entrada.

`OptimizationResult` retém `original_plan` e `optimized_plan`. O método `revert()`
devolve diretamente o plano original, tornando a otimização reversível sem
reconstrução ou perda de auditoria.

## 6. Métricas

`OptimizationMetrics` registra:

- `duration` lógica determinística (`0.0`);
- iterações;
- regras executadas;
- regras ignoradas;
- convergência;
- score de otimização.

O score representa a redução relativa do tamanho estrutural do plano e não é
usado para escolher estratégia de execução.

## 7. Validação

`OptimizerValidator` verifica:

- tipos e integridade do plano;
- ausência de ciclos na árvore de predicados;
- consistência canônica de filtros, projeções e ordenação;
- preservação de query ID, estimativas e timestamp;
- equivalência estrutural normalizada;
- equivalência de predicados, projeções, ordenação e paginação;
- ausência de perda semântica nas transformações suportadas.

A equivalência normaliza associatividade, comutatividade, idempotência, dupla
negação, membership unitário, prioridades de sort e fronteiras de paginação. Uma
regra que produzir plano não equivalente interrompe a otimização com erro público.

## 8. Logging

Foram implementados os eventos estruturados obrigatórios:

- `optimization_started`;
- `rule_started`;
- `rule_applied`;
- `rule_skipped`;
- `optimization_finished`.

Os eventos são emitidos pelo logging canônico da SDK com contexto ordenado e não
dependem de infraestrutura externa.

## 9. Arquivos criados

- `src/cko/core/discovery/optimizer_errors.py`;
- `src/cko/core/discovery/optimizer_models.py`;
- `src/cko/core/discovery/optimizer_rules.py`;
- `src/cko/core/discovery/optimizer.py`;
- `tests/test_query_optimizer_spr008n.py`;
- `SPR008N_IMPLEMENTATION_REPORT.md`.

## 10. Arquivos alterados

- `src/cko/core/discovery/__init__.py` — exports públicos do optimizer;
- `src/cko/core/__init__.py` — exports públicos da raiz do CORE SDK.

As alterações de API são somente aditivas. Nenhum contrato, nome, assinatura ou
comportamento homologado anteriormente foi removido ou modificado.

## 11. Testes

A suíte `tests/test_query_optimizer_spr008n.py` contém 25 testes e cobre:

- as dez regras canônicas;
- prioridade e metadata das regras;
- pipeline, ponto fixo e múltiplas iterações;
- limite de iterações e não convergência;
- prevenção de loop de dois estados;
- equivalência e validação final;
- reversibilidade;
- serialização estrita e imutabilidade profunda;
- context, result, report e metrics;
- logging completo;
- falhas explícitas e schemas inválidos;
- exports públicos, type hints e docstrings;
- UTF-8 sem BOM e PEP-8 (linhas até 99 caracteres);
- ausência de imports de infraestrutura.

Resultado isolado final: **25 aprovados, 0 falhas**.

## 12. Cobertura

`coverage.py` não está instalado. Foi utilizada a metodologia determinística da
biblioteca padrão com `python -m trace --count --missing`, conforme autorizado no
briefing. Os contadores foram emitidos fora do Google Drive para evitar a recusa
ambiental de arquivos `.cover`.

| Módulo | Executadas | Executáveis | Cobertura |
|---|---:|---:|---:|
| `optimizer.py` | 271 | 293 | 92,5% |
| `optimizer_errors.py` | 10 | 10 | 100,0% |
| `optimizer_models.py` | 285 | 312 | 91,3% |
| `optimizer_rules.py` | 245 | 249 | 98,4% |
| **Agregado** | **811** | **864** | **93,9%** |

Todos os módulos novos superam individualmente 90%. O mínimo requerido foi
atingido.

## 13. Regressão

A matriz canônica CORE-001/SPR-008A a SPR-008N foi executada conjuntamente:

- **361 testes aprovados**;
- **0 falhas funcionais**;
- **0 falhas arquiteturais**;
- **0 falhas ambientais na matriz A–N**;
- **0 falhas legadas na matriz A–N**.

Resultado oficial da regressão solicitada: **APROVADA**.

Também foi executada, como verificação adicional, a pasta `tests` completa. Após
resolver as permissões do diretório temporário, o resultado foi **370 aprovados e
2 falhas legadas fora da matriz A–N**:

- `tests/test_file_metadata.py`: contrato legado chama `collect_metadata` com o
  argumento inexistente `calculate_hash`;
- `tests/test_persistence_spr005a.py`: um handle SQLite legado permanece aberto e
  impede a remoção de `cko.db` durante o teardown no Windows.

Essas falhas são preexistentes, pertencem a contratos anteriores à série SPR-008
e não têm relação de importação, execução ou estado com a SPR-008N. Nenhuma delas
foi ocultada ou alterada nesta Sprint.

## 14. Limitações

- A equivalência é provada para o conjunto canônico de transformações desta
  fundação, não para reescritas arbitrárias fornecidas por terceiros.
- O score mede redução estrutural e não custo físico.
- A duração é lógica e determinística, não benchmark da máquina.
- Estatísticas e índices são contexto auditável; as regras atuais não os usam para
  selecionar estratégia.
- `coverage.py` não está disponível; foi usada a biblioteca padrão.
- O Google Drive e o TEMP padrão apresentaram restrições de gravação durante a
  regressão ampla; a matriz A–N não depende dessas gravações e foi aprovada.
- Não existe execução, banco, persistência, cache, API ou infraestrutura no código
  do optimizer.

## 15. Compatibilidade

A API pública permaneceu compatível. Os exports foram apenas estendidos em
`cko.core.discovery` e `cko.core`. O `QueryPlan`, o Cost-Based Planner e todos os
contratos homologados das SPR-008A a SPR-008M permaneceram inalterados.

A regressão conjunta de 361 testes comprova compatibilidade com CORE-001 e
SPR-008A a SPR-008M.

## 16. Respostas obrigatórias

1. O Query Optimizer foi implementado? **Sim.**
2. Existe pipeline de otimização? **Sim.**
3. Existem regras canônicas? **Sim, as dez regras obrigatórias.**
4. Existe convergência? **Sim, por ponto fixo.**
5. Existe controle de iterações? **Sim, com limite configurável e padrão oito.**
6. Existe validação? **Sim, estrutural, semântica, de integridade e de ciclos.**
7. Existe relatório? **Sim, serializável, imutável e incorporado ao resultado.**
8. Existe execução da consulta? **Não.**
9. Existe banco? **Não no optimizer.**
10. Existe persistência? **Não no optimizer.**
11. Existe infraestrutura? **Não no optimizer.**
12. A API pública permaneceu compatível? **Sim.**
13. A regressão SPR-008A–008N foi aprovada? **Sim, 361/361 testes.**
14. A cobertura mínima foi atingida? **Sim, 93,9% agregada e >90% por módulo.**
15. A SPR-008N pode ser homologada? **Sim, tecnicamente recomendada para
    homologação formal.**

## 17. Declaração final

A fundação canônica do Query Optimizer foi implementada exclusivamente dentro de
`cko.core`, sem infraestrutura, sem banco, sem persistência e sem execução de
consultas. O pipeline é determinístico, reproduzível, auditável, reversível,
convergente e protegido contra loops. As dez regras obrigatórias foram
implementadas com validação semântica, logging e serialização estrita.

A suíte isolada foi aprovada em 25/25, a cobertura atingiu 93,9% e a regressão
CORE-001/SPR-008A–008N foi aprovada em 361/361. A SPR-008N está pronta para
homologação formal. Nenhum trabalho referente à SPR-008O foi iniciado.
