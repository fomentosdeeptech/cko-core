# CKO-SPR-003 — Inventário Seguro e Knowledge Base Inicial

## Objetivo

Inventariar com segurança o acervo existente na pasta Downloads, estimado em quase 3.000 arquivos, sem mover, renomear ou excluir documentos.

## Princípios obrigatórios

- execução inicial em DRY-RUN;
- processamento em lotes;
- arquivos temporários ignorados;
- banco SQLite separado do acervo;
- nenhuma movimentação física nesta sprint;
- relatório JSON para auditoria;
- gravação definitiva somente após validação humana.

## Entregáveis

- inventário em lotes;
- coleta de metadados;
- hash SHA-256 opcional;
- banco SQLite em `runtime/cko.db`;
- relatório de DRY-RUN em `logs/spr003_dry_run_inventory.json`;
- monitor de novos arquivos;
- testes mínimos.

## Gate

A gravação no SQLite somente poderá ocorrer depois da revisão do relatório de DRY-RUN.
