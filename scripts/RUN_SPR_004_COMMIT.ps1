$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host ""
Write-Host "CKO-SPR-004 - GRAVACAO NO SQLITE" -ForegroundColor Cyan
Write-Host "Arquivos nao serao movidos, renomeados ou excluidos." -ForegroundColor Yellow
Write-Host "Somente metadados, duplicados e grafo serao gerados." -ForegroundColor Yellow
Write-Host ""

python src/main.py --batch-size 250 --commit
