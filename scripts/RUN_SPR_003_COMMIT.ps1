$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host ""
Write-Host "CKO-SPR-003 - GRAVACAO NO SQLITE" -ForegroundColor Cyan
Write-Host "Arquivos nao serao movidos, renomeados ou excluidos." -ForegroundColor Yellow
Write-Host "Somente os metadados serao gravados em runtime\cko.db." -ForegroundColor Yellow
Write-Host ""

python src/main.py inventory --batch-size 200 --commit
