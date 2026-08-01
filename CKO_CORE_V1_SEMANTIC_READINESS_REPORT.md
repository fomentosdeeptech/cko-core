# CKO CORE v1 — Prontidão para a fase semântica

## Ordem recomendada e gates

| Ordem | Capacidade | Dependências existentes | Ausentes | Risco | Entrada | Conclusão |
|---:|---|---|---|---|---|---|
| 1 | Knowledge Object Foundation | `CanonicalId`, Asset, metadata, provenance básica, Storage/UoW | contrato de versão semântica, taxonomia de erros | médio | ressalvas P1 normativas decididas | modelo imutável/versionado, validação e round-trip |
| 2 | Document Canonical Model | `CanonicalDocument`, `DocumentAsset`, locations | seções/blocos, mídia, extração/provenance granular | médio | Knowledge Object estável | modelo canônico sem dependência de parser/provider |
| 3 | Knowledge Provenance | Origin, events, Checkpoint, logging | audit trail imutável e actor identity | alto | IDs/versões definidos | cadeia verificável source→transform→knowledge |
| 4 | Knowledge Versioning | SemanticVersion, Checkpoint, UoW | política de migração/merge | médio | provenance disponível | evolução, conflito, rollback e compatibilidade testados |
| 5 | Taxonomy and Ontology | policies/capabilities/query models | modelos conceituais e governança de termos | alto | object/document estáveis | versionamento, validação e aprovação humana |
| 6 | Knowledge Governance | logging, validators, lifecycle | security, audit trail, policy engine | alto | identity/security disponíveis | decisões auditáveis e políticas aplicadas |
| 7 | Knowledge Graph | IDs, relações de Asset, Storage, query/planner | modelo de nós/arestas e adapter graph | alto | ontology/versioning estáveis | contratos neutros + adapter testado |
| 8 | Semantic Index | logical index/statistics/planner | embedding/vector contracts e atualização incremental | alto | document/object/provenance estáveis | índice reproduzível, versionado e descartável |
| 9 | Semantic Search | Query/Optimizer/Planner/Execution | operadores semânticos, ranking e adapter de índice | alto | semantic index homologado | relevância, filtros, explain e regressão |
| 10 | Knowledge Consolidation | identity resolution, UoW, Checkpoint | merge policy, lineage e human review | alto | graph/provenance/governance | consolidação reversível e auditável |
| 11 | Knowledge Reasoning | execution/runtime/policies | lógica de inferência, explicabilidade | alto | graph + ontology + governance | inferências versionadas, explicáveis e canceláveis |
| 12 | Incorporação de Núcleos | Discovery/Inventory/Storage/Checkpoint/UoW | adapters reais, security e governança | alto | pipeline semântico completo | ingestão idempotente, rastreável e homologada |

## Parecer por capacidade

- **Prontas para desenho imediato:** Knowledge Object Foundation e Document Canonical Model, após a Sprint de consolidação normativa.
- **Prontas apenas como contratos:** Provenance e Versioning.
- **Não prontas para implementação produtiva:** Governance, Graph, Index, Search, Consolidation, Reasoning e incorporação de Núcleos, pois dependem de decisões ainda ausentes.

## Riscos de sequência

Começar pelo graph ou semantic index antes do objeto/documento/provenance cristaliza detalhes de tecnologia nos contratos. Começar por reasoning antes de governance impede explicar e auditar inferências. Incorporar Núcleos antes de security/audit trail expõe conteúdo sem controles institucionais. A sequência acima preserva a direção Ports and Adapters já demonstrada pelo CORE.
