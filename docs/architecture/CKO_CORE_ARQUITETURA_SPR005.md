# CKO CORE — Arquitetura da SPR-005

## Objetivo

Adicionar fronteiras arquiteturais mínimas à implementação existente.

## Estrutura resultante

```text
src/cko
├── scanner
├── classifier
├── organizer
├── metadata
├── kb
├── utils
├── contracts
├── models
├── services
└── api
```

## Limites

- `contracts`: interfaces independentes de implementação;
- `models`: identidades e estruturas centrais;
- `services`: orquestração futura;
- `api`: fronteira futura de integração.

A sprint não altera o comportamento operacional do scanner.
