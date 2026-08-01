# CKO-CORE-SPR-006A — Termo de Abertura

## Objetivo

Criar a infraestrutura inicial de banco SQLite canônico, migrações versionadas e controle de schema.

## Escopo

- banco canônico separado;
- migration runner;
- schema versionado;
- tabelas `documents`, `locations` e `schema_version`;
- testes de criação e idempotência.

## Fora do escopo

- importação do inventário;
- CRUD de documentos;
- integração com scanner;
- OCR;
- IA;
- embeddings;
- RAG.
