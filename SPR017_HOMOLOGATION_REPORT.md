# SPR-017 — Relatório de Homologação Técnica Independente

## 1. Decisão formal

**SPR-017 homologada tecnicamente.**

A homologação independente da **SPR-017 — Knowledge Provenance Statement Foundation** foi concluída sem bloqueador técnico concreto, sem correção de código ou testes e sem regressão nova. Todos os 90 critérios de aceite foram aprovados por execução, reflexão, inspeção AST, reprodução algorítmica dos vetores, regressão, cobertura, build e instalação isolada.

## 2. Repositório e baseline

- Repositório canônico: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`.
- Branch inicial e final: `main`.
- HEAD inicial e final: `e94545919db97a071f08de2c08ce1a5dde06980e`.
- Baseline esperado: confirmado exatamente.
- Estado inicial: worktree sujo preexistente, com 459 entradas no `git status --porcelain=v1 --untracked-files=all`: 2 arquivos rastreados modificados (`.gitignore`, `pyproject.toml`) e 457 arquivos não rastreados.
- SHA-256 dos bytes do estado inicial completo: `45D69F3B3A52043F9AE0B087280FB980517037CD77B0EE9ABEAB678953BAD715`.
- Todo o trabalho preexistente foi preservado. Não foram usados `reset`, `clean`, descarte por `checkout` ou equivalentes.

## 3. Integridade documental

| Documento | SHA-256 confirmado |
|---|---|
| `SPR017_TECHNICAL_SPECIFICATION.md` | `D19FA36A85F9BB761A11E65EC32D4D39A9C8BB8DFD290F621101488DB0B4862D` |
| `SPR017G_VERIFICACAO_FINAL.md` | `93D50E88848DC6FC98B53670A381D45D5B52068DC490B3544B1DCFCB8CBE05BB` |
| `SPR017_IMPLEMENTATION_REPORT.md` | `6EFF3E326D379CAE109BCE9B06FBC7B9D5F34A985D64378B49F98B57A2FF2EA0` |

Os três documentos foram lidos integralmente. O hash da especificação foi reconfirmado após testes e inspeções e permaneceu inalterado.

## 4. Metodologia independente

As declarações do relatório de implementação não foram aceitas como evidência única. A verificação combinou:

1. execução das suítes dedicada, integrada e completa;
2. cobertura de linhas e branches medida sobre os 15 módulos reais;
3. reflexão da API, modelos, enums, serviços, exceções e `KnowledgeProvenance`;
4. inspeção AST/imports e busca de dependências, nomes e chamadas proibidos;
5. reprodução direta dos algoritmos UUIDv5, canonicalização, digest e projeção;
6. round-trip estrutural, semântico e byte a byte;
7. build pelo builder oficial com saída fora do repositório;
8. inspeção ZIP/METADATA/RECORD e instalação isolada sem o source no path;
9. comparação da regressão com evidências anteriores à SPR-017.

## 5. Arquivos inspecionados

Foram inspecionados a especificação, os dois relatórios obrigatórios, a suíte dedicada, as suítes SPR-010–017, os contratos públicos relacionados e todos os 15 módulos de `src/cko/core/provenance`: `__init__`, `constants`, `contracts`, `enums`, `errors`, `factory`, `identity`, `models`, `operations`, `references`, `relationship_projection`, `results`, `serializer`, `validator` e `versioning`.

A busca na produção não encontrou valores golden de I-01–I-04, D-01 ou R-01, referências a pytest/testes/ACs, snapshots, builders ou nomes de infraestrutura proibidos.

## 6. API pública e retrocompatibilidade

- `cko.core.provenance.__all__`: 36 entradas, 36 nomes únicos e 36 resolvidos.
- `cko.core.__all__`: 646 entradas, 646 nomes únicos e 646 resolvidos.
- Partição mecânica: 610 nomes legados únicos + 36 nomes novos, interseção nominal zero.
- Famílias novas: 4 constantes, 7 enums, 13 modelos/schemas, 4 serviços e 8 exceções.
- Os sete enums possuem vocabulários fechados; os 13 modelos são frozen, slotted e keyword-only, com envelopes fechados.
- Os quatro serviços são `ProvenanceStatementFactory`, `ProvenanceStatementValidator`, `DeterministicProvenanceSerializer` e `ProvenanceOperations`.
- As oito exceções tipadas e seus códigos determinísticos foram exercitados.
- `KnowledgeProvenance` preservou identidade de classe, módulo, assinatura, frozen/slots, serializer e comportamento público nas fachadas existentes.

## 7. Determinismo, imutabilidade e serialização

- Imutabilidade profunda, ordenação canônica e não mutação pelas operações: aprovadas.
- `CanonicalArray` e `CanonicalObject`: representações internas distintas; tuple pública ambígua rejeitada.
- C-02: `[null,true,false,0,-12]`, aprovado.
- Campos extras, ausentes, duplicados, tipos incorretos, versões futuras e JSON não canônico: rejeitados com códigos esperados.
- NFC/NFD, UTF-8 estrito, UTC com seis dígitos, SemVer, UUID e SHA-256 canônicos: aprovados.
- V-01–V-13: round-trip estrutural, semântico e byte a byte aprovado.
- Revisões 1/2/3: versões `1.0.0`/`1.0.1`/`1.0.2`, mesma identidade e referências anteriores completas.
- Cadeias vazias, simples, múltiplas, parciais e desconectadas: aprovadas; self, conflitos e ciclos: rejeitados.

## 8. Vetores normativos reproduzidos pelo algoritmo real

| Vetor | Resultado independente |
|---|---|
| Namespace UUIDv5 | `84c43be6-4bb5-52a8-9582-a2e8b04d797c` |
| I-01 | `d4e5aadf-9468-59aa-8076-28fe5e91642d` |
| I-02 | versão/digest do alvo não alteraram I-01 |
| I-03 | `579a17ba-956d-57ba-a48d-4f829e30ee50` |
| I-04 | `2ac58580-c9ec-5345-8eb0-d95f410cba82`; NFC/NFD convergentes |
| D-01 sem digest | 1.309 bytes; SHA-256 `dda22685f6674a51030a4c4eacbb0f4cf5991a8d6d61435c5fa0e9bbb50efd6d` |
| D-01 final | 1.385 bytes; round-trip byte a byte aprovado |
| R-01 logical ID | `14662ce7-1def-5fe9-8659-0fc5988074ee` |
| R-01 canonical ID | `488066ef-1ba9-5947-a510-993b0df40914` |
| R-01 version ID | `2c7e0eca-280f-58b4-9846-b5c209eb81b5` |
| R-01 serializer | 2.379 bytes; SHA-256 `8a4d2012d7b997f9dfbe3324ed148c2f4cfdd894a3448564fd215d3cdda3b5be`; validação e round-trip aprovados |

## 9. Testes, critérios e regressão

| Gate | Resultado |
|---|---|
| Suíte dedicada | 30 grupos normativos; 50/50 casos aprovados |
| Integração SPR-010–017 | 225/225 aprovados |
| Relationship Foundation | aprovada dentro da integração e nos vetores R-01 |
| KnowledgeProvenance | contrato, identidade, assinatura e comportamento aprovados |
| Regressão completa | 928 aprovados, 2 falhas históricas, zero falha nova |
| AC-001–AC-090 | 90/90 aprovados |
| Arquitetura/API pública | allowlist, AST, pureza, exports e ausência de colisões aprovados |

Falhas históricas reproduzidas:

1. `tests/test_file_metadata.py::test_collect_metadata`: `collect_metadata()` não aceita o argumento preexistente `calculate_hash=True`.
2. `tests/test_persistence_spr005a.py::Spr005ATests::test_existing_table_is_preserved`: handle SQLite permanece aberto no teardown do Windows.

Ambas constam antes da implementação em `SPR016_IMPLEMENTATION_REPORT.md`, `SPR017_PREIMPLEMENTATION_ARCHITECTURE_AUDIT.md` e `CKO_CORE_V1_TEST_AND_COVERAGE_REPORT.md`; nenhuma envolve `cko.core.provenance`.

## 10. Cobertura

Cobertura medida diretamente em `src/cko/core/provenance`:

- 1.036 statements, zero perdidos;
- 292 branches, zero parciais ou perdidos;
- 100% de linhas;
- 100% de branches.

O arquivo de dados foi gravado fora da unidade sincronizada para evitar o bloqueio SQLite/Google Drive já documentado; os caminhos medidos são os 15 módulos do repositório canônico.

## 11. Build, wheel, instalação e smoke

- Builder oficial: exit code zero, saída isolada fora do repositório.
- Wheel: `cko-1.0.0-py3-none-any.whl`, 440.069 bytes, 280 entradas.
- SHA-256: `A4AEED041D35B227B1BBDF3462B3B819313C4D378A09A74FE6796919807FA698`.
- Conteúdo: 15 módulos provenance; zero testes, cache, `.pyc` ou `.pyo`; METADATA e RECORD presentes.
- O wheel canônico preexistente em `runtime/reports/build` não foi sobrescrito.
- Instalação isolada: aprovada sem dependências e sem alterar o ambiente global.
- Smoke a partir do pacote instalado: 646/646/646 exports, I-01 exato, D-01 com 1.309 bytes/hash exato, envelope final de 1.385 bytes e round-trip aprovado.

## 12. Estado final e controle de mudanças

A única alteração autorizada produzida no repositório durante o Gate 1 é este arquivo, `SPR017_HOMOLOGATION_REPORT.md`. Código, testes, fixtures, configuração, exports, dependências, documentação preexistente, relatório de implementação e especificação não foram alterados.

Nenhum commit, push ou pull request foi criado. Nenhuma correção foi aplicada durante a homologação.

O SHA-256 deste relatório é calculado sobre o arquivo final e registrado externamente no fechamento da execução, conforme o padrão documental vigente que evita autorreferência impossível do hash do arquivo completo.

