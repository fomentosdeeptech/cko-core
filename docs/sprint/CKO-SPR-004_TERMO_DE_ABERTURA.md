# CKO-SPR-004 — Inventário Canônico e Base de Conhecimento

## Objetivo

Executar inventário recursivo e seguro do acervo localizado em Downloads, incluindo subpastas, com checkpoint, cálculo de SHA-256, identificação de duplicados e geração inicial do grafo documental.

## Restrições

- nenhum arquivo poderá ser movido;
- nenhum arquivo poderá ser renomeado;
- nenhum arquivo poderá ser excluído;
- o conteúdo dos documentos não será alterado;
- a primeira execução deverá ocorrer em DRY-RUN;
- a gravação no SQLite depende de validação humana.

## Entregáveis

- inventário recursivo;
- checkpoint por lotes;
- banco SQLite;
- relatório de inventário;
- relatório de duplicados;
- grafo documental JSON;
- resumo da sprint;
- testes automatizados.

## Gate

A execução com `--commit` somente poderá ocorrer após revisão do DRY-RUN.
