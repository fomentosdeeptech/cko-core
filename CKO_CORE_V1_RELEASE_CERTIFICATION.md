# CKO CORE SDK 1.0.0 — Certificação de release

**Release:** 1.0.0  
**Sprint:** SPR-009A  
**Data:** 2026-07-25  
**Autoridade técnica:** Arquitetura Principal do CKO  
**Parecer:** CERTIFICADO PARA INÍCIO DA CAMADA SEMÂNTICA

## 1. Escopo certificado

Esta certificação cobre o CKO CORE SDK implementado em `src/cko/core` e o wheel
`cko-1.0.0-py3-none-any.whl`. Ela certifica a eliminação das quatro ressalvas P1
da SPR-009. Não certifica funcionalidade semântica, porque nenhuma foi iniciada.

## 2. Gates de release

| Gate | Critério | Evidência | Estado |
|---|---|---|---|
| ARCH-001 | refletir implementação real | v1.2 com 153 módulos | aprovado |
| versão | todos os pontos em 1.0.0 | manifest, fachada, egg-info, wheel, METADATA | aprovado |
| exceções | raiz canônica única | 120 classes sob `CKOError` | aprovado |
| composição | root oficial único | `cko.core.composition` | aprovado |
| retrocompatibilidade | nenhum export removido | 346 exports únicos | aprovado |
| schemas | nenhuma alteração | diff e regressão | aprovado |
| serialização | nenhuma alteração | regressão | aprovado |
| suíte dedicada | zero falhas | 17 passed | aprovado |
| regressão | nenhuma falha nova | 703 passed, 2 legadas | aprovado |
| runtime | ambiente compatível | 5 checks passed | aprovado |
| build | wheel válido | 187 entradas | aprovado |
| reprodutibilidade | hashes iguais | SHA-256 idêntico | aprovado |
| import do wheel | versão e API disponíveis | import isolado | aprovado |
| escopo semântico | nenhuma implementação | inspeção da árvore | aprovado |

## 3. Artefato certificado

```text
Nome: cko-1.0.0-py3-none-any.whl
Formato: wheel pure Python
Entradas: 187
Módulos CORE: 153
SHA-256: FD19FDDCD0FAC1471ABFF1E758AF89A8B381E3F20237263342A681A33ACF10CB
Metadata-Version: 2.1
Name: cko
Version: 1.0.0
Requires-Python: >=3.13
```

O RECORD foi verificado em 186 entradas com conteúdo, tamanho e SHA-256. A linha
do próprio RECORD permanece sem hash conforme o formato wheel. O ZIP não contém
path absoluto, traversal ou timestamp variável.

## 4. Compatibilidade

- Windows 10: compatível por arquitetura e APIs usadas;
- Windows 11: runtime validado;
- PowerShell 5.1: runtime validado;
- Python 3.13: versão 3.13.14 validada;
- UTF-8: validado;
- API pública: aditiva;
- exceptions: captura histórica preservada;
- Storage, Runtime, Discovery, Execution, Checkpoint e UoW: comportamento
  funcional preservado;
- schemas e serializações: preservados.

## 5. Falhas legadas verificadas

As duas falhas conhecidas foram novamente reproduzidas:

| Falha | Origem | Classificação |
|---|---|---|
| `collect_metadata` rejeita `calculate_hash` | legado anterior ao CORE SDK novo | não regressão |
| teardown não remove `cko.db` aberto no Windows | persistência SPR-005A | não regressão |

Elas não foram ocultadas, alteradas ou reclassificadas. Nenhuma falha nova foi
observada.

## 6. Respostas obrigatórias

**Todas as ressalvas P1 foram eliminadas?**  
Sim.

**O CORE SDK encontra-se oficialmente certificado como versão 1.0.0?**  
Sim.

**A arquitetura normativa representa fielmente a implementação?**  
Sim. ARCH-001 v1.2 representa os 153 módulos, dependências e componentes reais.

**Existe Composition Root oficial?**  
Sim. `CompositionRoot.compose` e `compose_core` são as entradas oficiais.

**Existe hierarquia única de exceções?**  
Sim. Todas as exceções declaradas por `cko.core` derivam de `CKOError`.

**O SDK encontra-se apto para iniciar a Camada Semântica?**  
Sim, após a homologação formal da SPR-009A.

## 7. Condição de encerramento

A implementação, regressão, runtime, build, wheel, versão, composição e
documentação estão concluídos. A execução da Sprint deve ser interrompida após a
emissão deste parecer e permanecer aguardando homologação formal.

## 8. Parecer final

CERTIFICADO PARA INÍCIO DA CAMADA SEMÂNTICA
