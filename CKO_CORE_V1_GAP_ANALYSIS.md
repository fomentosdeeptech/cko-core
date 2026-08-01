# CKO CORE v1 — Gap analysis

## Matriz de lacunas

| ID | Lacuna | Evidência | Classe | Prioridade | Ação recomendada |
|---|---|---|---|---|---|
| GAP-01 | ARCH v1.1 desatualizada | seções 8/27/29/33 param em T; `src/cko/core/storage/sqlite`, `checkpoint`, `uow` existem | governança | P1 | revisão normativa pós-SPR-009 |
| GAP-02 | versão não consolidada | `pyproject.toml` e `src/cko/core/__init__.py` = 0.1.0; componentes = 1.0.0 | release | P1 | decisão SemVer e wheel v1.0 |
| GAP-03 | múltiplas raízes de erro | 119 classes em seis raízes e famílias ValueError | contrato | P1 | taxonomia comum aditiva |
| GAP-04 | sem composition root | factories locais, mas nenhum módulo monta Runtime/Storage/Connector/Checkpoint/UoW | composição | P1 | composition root explícito |
| GAP-05 | schemas/serialização heterogêneos | modelos B–O divergem de R–W | compatibilidade | P2 | protocolo serializável/versionado |
| GAP-06 | logging heterogêneo | snake_case, dot.case e frases; 48 chamadas | observabilidade | P2 | taxonomia e redaction policy |
| GAP-07 | cobertura pontual <90% | sete módulos nos relatórios homologados | testes | P2 | testes de ramos |
| GAP-08 | temporário compartilhado | scripts usam `runtime/temp/pytest`; concorrência da auditoria interferiu | workspace | P2 | IDs exclusivos/lock de execução |
| GAP-09 | API raiz muito ampla | 334 exports em `cko.core.__all__` | API | P3 | manter compatibilidade e promover imports por pacote |
| GAP-10 | defaults de relógio/UUID | `identity/identifier.py`, Checkpoint, UoW, modelos de query/planner | determinismo | P3 | protocolos Clock/IdFactory consistentes |
| GAP-11 | configuração mínima | `config/settings.py` lê ambiente/TOML/YAML, sem schema transversal de componentes | operação | P2 | configuration foundation versionada |
| GAP-12 | segurança/auditoria não transversal | não há identity/authorization/audit trail institucional | governança | P1 antes de produção | contratos mínimos antes de conhecimento sensível |

## Componentes candidatos antes da camada semântica

| Componente | Classificação | Evidência e limite |
|---|---|---|
| Cache foundation | PODE SER POSTERGADO | performance ainda não demonstrada como requisito |
| Event bus | RECOMENDADO | existe `EventPublisher`, mas não bus; útil para provenance/audit |
| Plugin framework | PODE SER POSTERGADO | `Plugin` base existe; providers/registries já dão extensão controlada |
| Scheduler | NÃO NECESSÁRIO AO CORE | nenhum lifecycle atual exige agendamento |
| Policy engine | RECOMENDADO | policies locais existem; governança semântica futura requer unificação |
| Identity and security | OBRIGATÓRIO ANTES DA CAMADA SEMÂNTICA produtiva | `CanonicalId` não é identidade/autorização de usuário/tenant |
| Audit trail | OBRIGATÓRIO ANTES DA CAMADA SEMÂNTICA produtiva | logging não é trilha imutável de governança |
| Configuration foundation | OBRIGATÓRIO ANTES DA CAMADA SEMÂNTICA produtiva | configuração atual é mínima e não compõe subsistemas |
| DI composition root | OBRIGATÓRIO ANTES DA CAMADA SEMÂNTICA persistida | adapters são corretamente injetáveis, mas montagem não é canônica |
| Migration framework | RECOMENDADO | legado possui migrations; CORE Storage/Checkpoint não têm versão de migração transversal |
| Health diagnostics | RECOMENDADO | workspace valida ambiente, não saúde dos adapters/runtime |
| Telemetry | PODE SER POSTERGADO | métricas locais existem; falta exporter/correlation transversal |
| Transaction abstraction | JÁ ATENDIDO | UoW + SQLite session cobrem fundação; sem transação distribuída |
| Graph infrastructure | PODE SER POSTERGADO | deve seguir Knowledge Object/Document Model, não precedê-los |
| Exception/event taxonomy | OBRIGATÓRIO ANTES DA CAMADA SEMÂNTICA | evita nova proliferação na próxima família de domínio |

“Obrigatório antes” distingue início de modelagem de entrada produtiva: Knowledge Object Foundation pode começar após a consolidação normativa; segurança, audit trail e composição são gates para dados semânticos reais.
