# CKO-SPR-003 — Pacote de Implementação

## Instalação

Extraia este pacote dentro de:

`G:\Meu Drive\CKO\CORE`

Permita a mesclagem das pastas. Os arquivos desta sprint substituem `src/main.py` e `src/cko/scanner/watcher.py`.

## Primeira execução obrigatória

No terminal do VS Code:

```powershell
python src/main.py inventory --batch-size 200
```

Esse comando:

- lê os arquivos já existentes em Downloads;
- ignora temporários;
- não calcula hash por padrão;
- não grava no banco;
- não move, renomeia ou exclui nada;
- gera `logs/spr003_dry_run_inventory.json`.

## Após validar o relatório

```powershell
python src/main.py inventory --batch-size 200 --commit
```

Esse comando apenas grava os metadados em `runtime/cko.db`.

## Hash completo

Não execute o hash completo dos quase 3.000 arquivos na primeira rodada. Depois da validação:

```powershell
python src/main.py inventory --batch-size 100 --hash --commit
```

## Monitoramento de novos arquivos

Modo seguro:

```powershell
python src/main.py watch
```

Modo com gravação no banco:

```powershell
python src/main.py watch --commit
```

## Testes

```powershell
pytest
```
