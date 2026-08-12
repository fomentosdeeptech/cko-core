# CKO — AUD-004 — Repository Consumers, Dependencies & References Audit

**STATUS:** AUDIT / NON-EXECUTABLE
**Data:** 11/08/2026 — America/Sao_Paulo
**Escopo:** análise somente-leitura; nenhuma migração, OPS-005 ou REL-001 autorizada.

## A. Estado inicial

O repositório estava na branch `main`, com uma alteração rastreada e artefatos não rastreados preexistentes. Eles foram preservados. Nenhuma operação Git mutável foi executada.

## B. HEAD/baseline

| Referência | Commit |
|---|---|
| HEAD | `faa51ac6568dc2aa0e11d2333671b1098a1a89fa` |
| origin/main local | `faa51ac6568dc2aa0e11d2333671b1098a1a89fa` |
| origin/main remoto (`ls-remote`) | `faa51ac6568dc2aa0e11d2333671b1098a1a89fa` |
| tag `CKO-BASELINE-2026.07` | `faa51ac6568dc2aa0e11d2333671b1098a1a89fa` |

## C. Integridade da OPS-004R

- Markdown SHA-256: `6385AE31F238110E5FF0A38DD74A6F10074CD37FE31F7BB70DCD5AF61D8AD101` — confirmado.
- CSV SHA-256: `EA7A1B734CC26E59E5E66348B37F98B0C890950DBE43301B5098BEA8DB591067` — confirmado.
- Registros: 174; KEEP 52; MOVE 100; HOLD 18; IGNORE_GENERATED 4; decisão humana YES 122 — confirmado.
- Duplicatas exatas: 2 grupos / 6 arquivos — confirmado pela fonte OPS-004R.

## D. Universo efetivamente pesquisado

Foi enumerado todo o repositório, exceto `.git/`. Entraram `docs/`, `src/`, `scripts/`, `tests/`, `config/`, `migrations/`, `prompts/`, `reports/`, `logs/`, `templates/`, `.vscode/`, raiz e runtime em modo somente-leitura. Binários foram enumerados, mas não interpretados como texto.

## E. Número de arquivos pesquisados

- Arquivos regulares enumerados: **4090**.
- Arquivos textuais decodificados e pesquisados: **499**.
- Objetos do inventário: **174/174**.

## F. Metodologia

1. Enumeração recursiva determinística, exclusão exclusiva de `.git/` e dos próprios artefatos AUD-004 durante a coleta.
2. Leitura textual por extensão elegível, rejeitando NUL; tentativa de UTF-8, CP-1252 e Latin-1 somente para análise.
3. Busca case-insensitive por caminho atual com `/` e `\`, filename completo e identificadores GOV/ADR/RFC/SPR/OPS/AUD/ARCH.
4. Caminho completo = `PATH_REFERENCE/HIGH`; filename isolado = `FILENAME_REFERENCE/MEDIUM`; identificador inequívoco = `IDENTIFIER_REFERENCE/MEDIUM`.
5. Autorreferências, ocorrências no inventário/plano OPS-004R, duplicação caminho+filename e identificadores ambíguos foram rejeitados como falsos positivos.
6. Somente HIGH/MEDIUM fundamentam resultados. Ausência após cobertura completa é `NO_VERIFIED_*`, não `UNKNOWN`.
7. Dependência de fonte técnica/configuracional é `OPERATIONAL_DEPENDENCY`; demais referências confirmadas são `DOCUMENTARY_DEPENDENCY`. Não houve inferência por mera semelhança nominal.

## G. Objetos auditados

**174/174**, com exatamente um registro por `INVENTORY_ID` no CSV de resultados.

## H. Resultado dos 100 MOVE

| Risco | Quantidade |
|---|---:|
| LOW_REFERENCE_RISK | 0 |
| MEDIUM_REFERENCE_RISK | 33 |
| HIGH_REFERENCE_RISK | 67 |
| BLOCKED_UNKNOWN | 0 |

Nenhum MOVE é autorizado. A classificação mede apenas risco de referência detectável no estado observado.

## I. Resultado dos 18 HOLD

Os **18** HOLD foram auditados sem mudança de estado. Configurações locais, OPS-004 histórica, pacotes, artefatos locais e logs permanecem sujeitos a decisão humana. Logs foram examinados apenas quanto a consumidores, referências, função aparente, valor probatório e impacto operacional; nenhuma política de retenção foi definida.

## J. Consumidores encontrados

Objetos com consumidor HIGH/MEDIUM: **172**.

## K. NO_VERIFIED_CONSUMER

Objetos sem consumidor verificável após a varredura: **2**.

## L. Consumidores ainda UNKNOWN

**0**. A enumeração do universo foi completa; arquivos binários não foram promovidos artificialmente a texto, e essa limitação está declarada.

## M. Dependências comprovadas

Objetos com ao menos uma dependência documental ou operacional comprovada: **172**.

## N. NO_VERIFIED_DEPENDENCY

Objetos sem dependência verificável: **2**.

## O. Dependências ainda UNKNOWN

**0** sob a metodologia declarada.

## P. REFERENCES_IN

Relações confirmadas de entrada: **2993**.

## Q. REFERENCES_OUT

Relações confirmadas de saída entre fontes inventariadas e alvos: **2925**. Fontes fora dos 174 aparecem na matriz, mas não recebem registro de objeto.

## R. Referências por path

Referências confirmadas por caminho ou filename: **960**.

## S. Referências por identificador

Referências inequívocas por identificador: **2033**. Elas não implicam dependência física de caminho.

## T. Falsos positivos rejeitados

- Referências candidatas avaliadas: **6816**.
- Referências confirmadas: **2993**.
- Candidatas rejeitadas/colapsadas: **3823**.

Principais causas: autorreferência, inventário/plano tautológico, sobreposição caminho+filename e identificador compartilhado por vários objetos.

## U. Classificação de risco

Para MOVE: HIGH quando existe consumidor operacional ou cinco ou mais referências de path; MEDIUM quando existe referência confirmada; LOW quando não existe referência HIGH/MEDIUM; BLOCKED_UNKNOWN somente se a cobertura for tecnicamente insuficiente.

## V. Artefatos criados

1. `docs/audits/documentation/AUD-004_REPOSITORY_CONSUMERS_DEPENDENCIES.csv`
2. `docs/audits/documentation/AUD-004_REFERENCE_MATRIX.csv`
3. `docs/audits/documentation/AUD-004_REPOSITORY_CONSUMERS_DEPENDENCIES_AUDIT.md`

## W. SHA-256

Os hashes finais são calculados externamente após o fechamento deste relatório para evitar autorreferência. Depois desse cálculo, os três artefatos não devem ser alterados.

## X. Gates A4-R0 a A4-R16

| Gate | Estado | Evidência |
|---|---|---|
| A4-R0 | SATISFEITO | hashes e invariantes OPS-004R confirmados |
| A4-R1 | SATISFEITO | 174 registros de entrada |
| A4-R2 | SATISFEITO | repositório enumerado read-only; `.git/` excluído |
| A4-R3 | SATISFEITO | critérios de consumidores documentados |
| A4-R4 | SATISFEITO | classes de dependência documentadas |
| A4-R5 | SATISFEITO | referências de entrada por matriz |
| A4-R6 | SATISFEITO | referências de saída por matriz |
| A4-R7 | SATISFEITO | 100 MOVE auditados |
| A4-R8 | SATISFEITO | 18 HOLD auditados |
| A4-R9 | SATISFEITO | 174 resultados produzidos |
| A4-R10 | SATISFEITO | IDs N:N sequenciais e consistentes |
| A4-R11 | SATISFEITO | falsos positivos contabilizados |
| A4-R12 | SATISFEITO | risco classificado |
| A4-R13 | SATISFEITO | UNKNOWN separado de NO_VERIFIED_* |
| A4-R14 | PENDENTE DE VERIFICAÇÃO FINAL | comparar status inicial/final |
| A4-R15 | SATISFEITO | Git somente read-only |
| A4-R16 | PENDENTE DE VERIFICAÇÃO FINAL | validar UTF-8, U+FFFD e NUL |

## Y. Git status final

Deve preservar o estado inicial e acrescentar exclusivamente os três artefatos AUD-004. A comprovação é feita externamente após o hash final.

## Z. Bloqueadores

Não há bloqueador técnico para concluir a produção de evidência. Permanecem bloqueadores institucionais para migração: revisão humana dos 122 registros, aceitação de destinos, política de retenção/custódia e homologação independente.

## AA. Impacto sobre ND-002

ND-002 recebe evidência estruturada para os 174 objetos e deixa de depender de `UNKNOWN` generalizado. Ela não é encerrada automaticamente: referências MEDIUM, riscos HIGH e decisões humanas continuam exigindo aceite.

## AB. Próxima ação recomendada

Revisão humana da matriz, começando pelos MOVE `HIGH_REFERENCE_RISK` e pelos 18 HOLD; validar referências MEDIUM e somente depois deliberar sobre atualização da OPS-004R em operação separada. Não abrir OPS-005 nem REL-001.

## AC. Veredito

**AUD-004 CONCLUÍDA PARCIALMENTE — REVISÃO HUMANA NECESSÁRIA**
