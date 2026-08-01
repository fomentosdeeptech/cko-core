# ADR-004 — Banco Canônico Separado

## Status

Aceito.

## Decisão

A SPR-006A utilizará `runtime/database/cko_canonical.db`, preservando `runtime/cko.db` e `runtime/database/cko.db`.

## Motivo

Reduzir risco de interferência no legado durante a migração.
