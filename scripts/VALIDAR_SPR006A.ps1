#requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Core = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

$Required = @(
    "src\cko\migrations\__init__.py",
    "src\cko\migrations\0001_initial_schema.sql",
    "src\cko\migrations\runner.py",
    "src\cko\repository\__init__.py",
    "src\cko\repository\database.py",
    "scripts\INICIALIZAR_BANCO_CANONICO.ps1",
    "tests\test_migrations_spr006a.py",
    "docs\sprint\CKO-CORE-SPR-006A_TERMO_DE_ABERTURA.md",
    "docs\sprint\SPR006A_REPORT.md"
)

$Missing = @()

foreach ($Relative in $Required) {

    if (Test-Path -LiteralPath (Join-Path $Core $Relative)) {
        Write-Host "[OK] $Relative" -ForegroundColor Green
    }
    else {
        Write-Host "[AUSENTE] $Relative" -ForegroundColor Red
        $Missing += $Relative
    }

}

$Protected = @(
    "src\main.py",
    "src\cko\scanner",
    "src\cko\metadata",
    "src\cko\kb",
    "logs\spr004_inventory.json",
    "runtime\checkpoints\spr004_checkpoint.json",
    "runtime\database\cko.db"
)

foreach ($Relative in $Protected) {

    if (Test-Path -LiteralPath (Join-Path $Core $Relative)) {
        Write-Host "[PRESERVADO] $Relative" -ForegroundColor Yellow
    }
    else {
        Write-Host "[NÃO LOCALIZADO] $Relative" -ForegroundColor DarkYellow
    }

}

if ($Missing.Count -gt 0) {
    throw "SPR-006A não validada. Arquivos ausentes: $($Missing.Count)"
}

Write-Host ""
Write-Host "Executando testes específicos da SPR-006A..." -ForegroundColor Cyan

Push-Location $Core

try {

    #
    # Garante que o pacote "cko" seja encontrado
    #
    $env:PYTHONPATH = Join-Path $Core "src"

    #
    # Evita PermissionError no diretório TEMP do Windows
    #
    $PytestTemp = Join-Path $Core "runtime\pytest_tmp"

    if (-not (Test-Path -LiteralPath $PytestTemp)) {
        New-Item -ItemType Directory -Path $PytestTemp -Force | Out-Null
    }

    python -m pytest `
        --basetemp "$PytestTemp" `
        tests\test_migrations_spr006a.py `
        -q

    if ($LASTEXITCODE -ne 0) {
        throw "Os testes da SPR-006A falharam."
    }

}
finally {

    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

    Pop-Location

}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "             SPR-006A VALIDADA" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host "Nenhum scanner foi executado."
Write-Host "Nenhum inventário foi importado."
Write-Host "Nenhum banco legado foi alterado."
Write-Host ""
Write-Host "Todos os testes da SPR-006A passaram com sucesso." -ForegroundColor Green