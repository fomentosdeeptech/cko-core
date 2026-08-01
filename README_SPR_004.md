# CKO-SPR-004 — Pacote de Implementação

## Onde extrair

Extraia o conteúdo deste pacote dentro de:

`G:\Meu Drive\CKO\CORE`

Permita a mesclagem das pastas e a substituição dos arquivos da sprint.

## Primeira execução obrigatória

No terminal do VS Code:

```powershell
python src/main.py --batch-size 250 --reset-checkpoint
```

Esse comando:

- percorre Downloads e todas as subpastas;
- calcula SHA-256;
- classifica por extensão;
- grava checkpoint;
- não grava no SQLite;
- não move, renomeia ou exclui arquivos.

## Depois da validação

```powershell
python src/main.py --batch-size 250 --commit --reset-checkpoint
```

## Arquivos gerados

- `logs/SPR004.log`
- `logs/spr004_inventory.json`
- `logs/duplicates.json`
- `runtime/database/cko.db`
- `runtime/checkpoints/spr004_checkpoint.json`
- `runtime/graph/document_graph.json`
- `docs/sprint/SPR004_REPORT.md`

## Retomada

Se a execução for interrompida, rode o mesmo comando sem `--reset-checkpoint`.

## Testes

```powershell
pytest
```
