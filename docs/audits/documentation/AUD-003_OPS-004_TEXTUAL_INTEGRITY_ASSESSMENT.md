# CKO — AUD-003 — OPS-004 Textual Integrity Assessment

**Data da avaliação:** 11/08/2026
**Objeto:** `docs/governance/OPS-004_REPOSITORY_CANONICAL_MIGRATION_PLAN.md`
**Natureza:** avaliação documental e errata; nenhuma restauração executada
**Status:** encerrada com recuperação bloqueada
**Modo de tratamento:** MODO B — PRESERVAÇÃO + ERRATA

## A. Estado inicial

- Repositório canônico: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`.
- `HEAD`: `faa51ac6568dc2aa0e11d2333671b1098a1a89fa`.
- Staging inicial: vazio.
- Working tree inicial: já continha alterações e arquivos não rastreados anteriores a esta avaliação, inclusive a própria OPS-004.
- Nenhuma operação Git de staging, commit, push, pull, fetch, reset, clean, checkout, switch ou rebase foi executada.
- A OPS-004 permanecia `PROPOSED / BLOCKED / NON-EXECUTABLE ANALYTICAL PLAN` por autoridade da GOV-008 ratificada.

## B. Hash da OPS-004 atual

- SHA-256: `DFBE147BF42E1956C60D7E2628DD32B3CD1C7C38E310480E81C0F4485FBFF293`.
- Tamanho: 39.774 bytes.
- Timestamp observado no sistema de arquivos: criação e última gravação em 03/08/2026 23:57:50, horário local.

## C. Mapa de corrupção

- Encoding real: UTF-8 válido, sem BOM.
- EOL: 254 ocorrências LF e nenhuma ocorrência CRLF; não houve normalização.
- Caracteres `?`: 829.
- Linhas afetadas: 174 de 255 linhas lógicas observadas (254 quebras LF).
- Caracteres de substituição U+FFFD: zero.
- Bytes NUL: zero.
- Estrutura observada: 22 headings, 59 linhas estruturais `INV-NNN`, 8 linhas D01–D08 e 15 grupos `EXNN`.

Distribuição por região:

| Região | `?` | Linhas afetadas | Intervalo |
|---|---:|---:|---:|
| Preâmbulo | 28 | 7 | 1–12 |
| Seção 1 | 25 | 3 | 14–18 |
| Seção 2 | 38 | 7 | 20–27 |
| Seção 3 | 30 | 11 | 29–42 |
| Seção 4 | 5 | 1 | 46 |
| Seção 5 — inventário | 428 | 62 | 48–112 |
| Seção 6 e subseções | 67 | 28 | 114–158 |
| Seção 7 | 39 | 8 | 160–171 |
| Seção 8 | 27 | 10 | 173–184 |
| Seções 9–10 | 22 | 3 | 188–192 |
| Seções 11–14 | 66 | 18 | 196–220 |
| Seções 15–17 | 54 | 16 | 222–254 |

Exemplos representativos, preservados sem correção: `Sum?rio`, `classifica??o`, `n?o`, `CAN?NICO`, `D01?D08` e separadores de título representados por `?`. A incidência alcança títulos, prosa, tabelas, classificações, decisões, caminhos descritivos e campos de aprovação. A concentração maior está na tabela de inventário, mas a degradação atravessa todo o documento.

O padrão é sistemático e compatível com uma conversão ou gravação lossy anterior que substituiu caracteres não representáveis por `0x3F` (`?`). Essa é hipótese técnica, não atribuição causal: o arquivo já chegou ao estado observado como UTF-8 válido, e não há evidência que identifique com segurança a ferramenta ou etapa responsável. Não há base para afirmar especificamente PowerShell, Windows-1252, exportador ou editor.

## D. Fontes candidatas localizadas

1. OPS-004 local atual, no caminho canônico: conteúdo completo em extensão, porém textualmente corrompido.
2. Objeto sincronizado no Google Drive, ID `14w4bf0LoU5f88QjhS5r-PieDmGyySMbY`: mesmo nome, MIME `text/markdown`, 39.774 bytes, criado e modificado em `2026-08-04T02:57:50.353Z`.
3. Histórico de revisões do objeto no Google Drive: uma única revisão, ID `0B617rv9Mj8Y4ckorcDExbDhoNzRtZ3JkeUo4T0QwQ3A0UWkwPQ`, com 39.774 bytes; não existe revisão anterior.
4. `AUD-001_WORKING_TREE_CONSOLIDATION_AUDIT.md`: referência analítica posterior, sem reprodução integral da OPS-004.
5. `AUD-002_AUD-001_EVIDENCE_INCORPORATION.md`: referência institucional posterior, sem reprodução integral da OPS-004.
6. `GOV-008_CYCLE_II_INSTITUTIONAL_RECONCILIATION.md`: autoridade institucional posterior e descrição de estado/contagens, sem reprodução integral da OPS-004.
7. `CKO_SPR_004_INVENTARIO_CANONICO.zip` e `CKO_SPR_003_INVENTARIO_SEGURO.zip`: listagem interna inspecionada em modo somente leitura; nenhuma entrada correspondente à OPS-004 foi localizada.
8. Histórico Git: nenhuma versão rastreada ou nome correspondente foi localizado; a OPS-004 atual é untracked.
9. Busca local por nome e título na árvore do projeto: nenhuma cópia independente íntegra foi localizada.

## E. Matriz de confiabilidade

| Fonte | Tipo / tamanho | Integridade / `?` | Encoding / EOL | Completude | Proveniência | Classe | Confiabilidade |
|---|---|---|---|---|---|---|---|
| OPS-004 local | Markdown / 39.774 bytes | corrompida / 829 | UTF-8 sem BOM / LF | completa em extensão, não em integridade | caminho canônico e timestamp local | D — CÓPIA CORROMPIDA | alta como evidência do dano; nula para restauração |
| Objeto Google Drive | Markdown / 39.774 bytes | correspondente ao objeto sincronizado corrompido | MIME textual; EOL não regravado | uma única versão disponível | ID e metadados verificáveis | D — CÓPIA CORROMPIDA | alta como proveniência do objeto; nula como fonte anterior |
| Revisão única do Drive | Markdown / 39.774 bytes | sem antecessora | não aplicável à restauração | única | revision ID verificável | D — CÓPIA CORROMPIDA | nula para restauração |
| GOV-008 | Markdown / 32.304 bytes | íntegra como referência | não avaliada como cópia | parcial | autoridade ratificada posterior | E — REFERÊNCIA SEM CONTEÚDO | alta para status; nula para restaurar texto |
| AUD-001 | Markdown / 12.179 bytes | íntegra como referência | não avaliada como cópia | parcial | auditoria posterior | E — REFERÊNCIA SEM CONTEÚDO | alta para achados; nula para restaurar texto |
| AUD-002 | Markdown / 7.801 bytes | íntegra como referência | não avaliada como cópia | parcial | incorporação posterior | E — REFERÊNCIA SEM CONTEÚDO | alta para controles; nula para restaurar texto |
| ZIPs SPR-003/004 | pacotes | sem entrada OPS-004 | não aplicável | ausente | pacotes locais observados | F — INADEQUADA PARA RESTAURAÇÃO | nula |

Nenhuma fonte recebeu classe A, B ou C com conteúdo suficiente para restauração.

## F. Comparação entre fontes

Não foi possível realizar comparação textual restaurativa porque não existe candidata íntegra. O objeto local e o objeto do Drive coincidem em nome, tamanho e instante de criação/modificação do arquivo sincronizado; o Drive conserva somente uma revisão. GOV-008, AUD-001 e AUD-002 confirmam identidade, estado e algumas contagens, mas não contêm os 39.774 bytes nem substituições determinísticas para as 829 posições.

As evidências permitem classificar a diferença esperada como corrupção de caractere, mas não permitem reconstruir cada caractere. Não foi detectada diferença de EOL a tratar. Diferenças editoriais, semânticas, estruturais ou não explicadas entre uma versão íntegra e a corrompida são indetermináveis por ausência da versão íntegra.

## G. Hipótese de origem da corrupção

A corrupção provavelmente antecede a gravação UTF-8 observada e resultou de uma etapa lossy que converteu caracteres não representáveis em `?`. A presença de caracteres Unicode ainda íntegros demonstra que não ocorreu simples destruição uniforme de todo caractere não ASCII. Sem arquivo anterior, log de geração ou revisão remota anterior, a ferramenta, o encoding de origem e o momento exato não podem ser demonstrados.

## H. Gates DOC-R0 a DOC-R6

| Gate | Resultado | Fundamentação |
|---|---|---|
| DOC-R0 | FALHOU | Não existe fonte íntegra com proveniência verificável. |
| DOC-R1 | FALHOU | Não existe fonte íntegra anterior ou equivalente. |
| DOC-R2 | FALHOU | O mecanismo geral é hipotetizável, mas cada diferença material não é explicável deterministicamente. |
| DOC-R3 | FALHOU | Sem fonte íntegra, não se pode excluir alteração semântica não justificada. |
| DOC-R4 | FALHOU | Algumas contagens e decisões são referenciadas, mas não é possível provar identidade integral do documento restaurado. |
| DOC-R5 | FALHOU | Restaurar as 829 posições exigiria inferência linguística proibida. |
| DOC-R6 | SATISFEITO SOMENTE PARA PRESERVAÇÃO | A natureza histórica pode ser preservada mantendo o arquivo intacto; restauração não é autorizável. |

Como os gates são cumulativos, a restauração fiel está bloqueada.

## I. Modo de tratamento escolhido

**MODO B — PRESERVAÇÃO + ERRATA.** A evidência demonstra materialmente o problema, mas não permite restaurar todo o conteúdo com confiança. O original permanece intocado.

## J. Alterações executadas

- Criado somente este artefato de avaliação/errata.
- A OPS-004 não foi modificada.
- Nenhum outro documento, configuração, EOL, inventário ou metadado institucional foi alterado.

## K. Hash final da OPS-004

Não alterada. SHA-256 final esperado e verificado no encerramento: `DFBE147BF42E1956C60D7E2628DD32B3CD1C7C38E310480E81C0F4485FBFF293`.

## L. Diferenças entre versão corrompida e restaurada

Não aplicável: nenhuma versão restaurada foi produzida.

## M. Git status final

O status final deve preservar todas as entradas preexistentes e acrescentar somente este arquivo não rastreado. O staging deve permanecer vazio. A captura final é registrada pela execução operacional de encerramento, sem staging, commit ou push.

## N. Bloqueadores remanescentes

- Ausência de fonte íntegra anterior ou equivalente.
- Ausência de revisão anterior no Google Drive.
- Ausência da OPS-004 nos pacotes e no histórico Git inspecionados.
- Impossibilidade de mapear deterministicamente os 829 caracteres sem inferência.
- Deficiência estrutural já registrada pela GOV-008 permanece fora do escopo desta avaliação.

## O. Próxima ação recomendada

Preservar a OPS-004 e esta errata como evidência. Se surgir fonte externa comprovadamente anterior, submeter nova avaliação DOC-R0–DOC-R6 antes de qualquer alteração. Na ausência dessa fonte, seguir futuramente o processo independente de regeneração estrutural previsto pela GOV-008, sem apresentar a regeneração como restauração histórica.

## P. Veredito

**OPS-004 PRESERVADA — ERRATA NECESSÁRIA**

Após este relatório, a operação deve parar e aguardar autorização humana.
