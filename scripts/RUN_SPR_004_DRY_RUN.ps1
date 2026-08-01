$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host ""
Write-Host "CKO-SPR-004 - INVENTARIO RECURSIVO SEGURO" -ForegroundColor Cyan
Write-Host "Modo: DRY-RUN" -ForegroundColor Yellow
Write-Host "Nenhum arquivo sera movido, renomeado ou excluido." -ForegroundColor Yellow
Write-Host ""

python src/main.py --batch-size 250
