# ADR-005A-001 — Persistência aditiva

**Status:** Aceita  
**Data:** 2026-07-12  

A SPR-005A cria o namespace `cko.persistence` e preserva o módulo `cko.kb` homologado anteriormente.

As tabelas recebem prefixo `cko_kb_`, reduzindo risco de colisão.

A migração é registrada como versão 5001.
