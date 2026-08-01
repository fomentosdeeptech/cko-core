# CKO — SPR-005A — Termo Oficial

**Título:** Núcleo Persistente SQLite  
**Dependência:** SPR-004 homologada e concluída  
**Natureza:** instalação aditiva, versionada e reversível  

## Objetivo

Implantar a infraestrutura persistente da Base de Conhecimento Inteligente sem alterar os módulos homologados anteriormente.

## Escopo

- camada `cko.persistence`;
- migração versionada 5001;
- tabelas de documentos, entidades, relações e eventos;
- índices estruturais;
- testes prévios à instalação;
- checkpoint, backup e rollback;
- validação pós-instalação.
