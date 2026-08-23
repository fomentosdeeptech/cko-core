# CKO — REV-008 — Revisão da Recuperação do Piloto do Local Knowledge Finder

Data: 2026-08-22

Identificador: `REV-008`

Componente avaliado: CKO Local Knowledge Finder

Versão: `0.1.0`

Commit do hotfix: `d49bcc0fbe93e9f59580e5dec62b0cf02beb795f`

Escopo: recuperação, reingestão e validação funcional do `PILOT-001`

Classificação: evidência de piloto local controlado

Status: `RECOVERED / FUNCTIONALLY VALIDATED / READY_FOR_CONTROLLED_CONTINUATION`

## 1. Estado canônico e escopo

A inspeção somente leitura encontrou a família de revisões até `REV-007`, sem caminho ou alocação concorrente para `REV-008`. Esta revisão consolida exclusivamente evidências agregadas já confirmadas. Nenhum documento real ou banco do piloto foi acessado, e a raiz é descrita apenas como pasta local controlada do piloto em unidade sincronizada.

O hotfix `FIX-PILOT-001` está concluído e publicado no commit acima, filho de `a0b45f30b0536ea36e326d0f1b6a481d9016460f`, com a mensagem `fix(local-finder): preserve indexing after partial extraction failure`. A reconciliação da causa raiz está corrigida. A validação totalizou 182 testes: 179 aprovados e 3 ignorados, todos preexistentes e relacionados à permissão de symlink no Windows. Não houve impacto na API pública, breaking change ou migração de schema.

## 2. Histórico do incidente

1. A ingestão inicial persistiu parcialmente os resultados.
2. Foram identificados 38 documentos únicos.
3. Uma exceção interrompeu o processamento após 15 extrações persistidas.
4. Nesse estado parcial, 14 extrações eram bem-sucedidas.
5. O índice FTS5 permaneceu vazio.
6. As buscas retornaram zero resultados.
7. O diagnóstico localizou uma composição inadequada entre a conclusão integral da extração e o início da indexação.
8. O hotfix foi desenvolvido, validado e publicado.
9. O hotfix foi instalado de modo controlado.
10. A reingestão real terminou com código de saída `0`.
11. O índice e a pesquisa foram recuperados e validados.

## 3. Causa raiz

O pipeline persistia cada extração em transação própria, mas só iniciava a indexação depois do retorno integral do lote de extração. Uma exceção inesperada tardia interrompia o lote e impedia a chamada de indexação, embora sucessos anteriores já estivessem persistidos.

## 4. Correção aplicada

Os sucessos anteriores passaram a ser indexados antes da propagação da falha inesperada. A falha permanece visível ao operador, com código de saída diferente de zero para falha interna e mensagem externa sanitizada. Não houve migração de schema nem alteração da API pública. A reingestão posterior continua idempotente.

## 5. Resultado da recuperação

| Métrica | Resultado |
|---|---:|
| Localizações descobertas | 40 |
| Documentos únicos | 38 |
| Extrações bem-sucedidas | 34 |
| Documentos sem texto extraível | 4 |
| Falhas recuperáveis | 0 |
| Documentos indexados | 34 |
| Grupos de duplicatas | 2 |
| Localizações duplicadas | 4 |
| Problemas atuais | 0 |
| Problemas históricos não resolvidos | 0 |

Os quatro registros `NO_TEXT` são documentos descobertos sem texto extraível pelo conjunto atual de extratores; não são falhas recuperáveis.

## 6. Validações funcionais

| Validação | Estado | Código de saída |
|---|---|---:|
| Pesquisa textual com resultados reais | `PASS` | 0 |
| Proveniência de documento indexado | `PASS` | 0 |
| Relatório de duplicatas | `PASS` | 0 |
| Relatório de falhas | `PASS` | 0 |
| Relatório de ingestão | `PASS` | 0 |

Os documentos-fonte não foram modificados. Não houve autorização nem observação de mutação do corpus.

## 7. Limitações observadas

- Quatro documentos não apresentaram texto extraível pelo conjunto atual de extratores.
- A ausência de OCR é uma hipótese possível para ampliar cobertura futura, sem evidência para afirmar que esses quatro documentos são digitalizações.
- Alguns PDFs malformados ou não estritamente conformes emitiram avisos.
- A operação atual depende de linha de comando, instalação e configuração técnicas.
- Não há fluxo gráfico para seleção de pasta nem apresentação amigável de progresso, falhas e relatórios.
- Uma política explícita para bancos, backups e atualização do índice ainda deve ser definida.

Essas limitações não são classificadas como defeitos confirmados além da evidência disponível.

## 8. Decisão de recuperação

```text
PILOT_RECOVERY_DECISION:
RECOVERED / FUNCTIONALLY VALIDATED / READY_FOR_CONTROLLED_CONTINUATION
```

A decisão confirma a recuperação funcional do piloto local controlado. Ela não libera produção ampla, operação multiusuário ou expansão automática do corpus.

## 9. Próxima recomendação

```text
NEXT_RECOMMENDED_WORK:
SPR-020 — CKO Local Knowledge Finder Desktop Interface
```

O plano recomendado é [SPR-020 — CKO Local Knowledge Finder Desktop Interface](../sprints/SPR-020_CKO_LOCAL_KNOWLEDGE_FINDER_DESKTOP_INTERFACE_PLAN.md). Sua implementação depende de autorização arquitetural e operacional posterior.
