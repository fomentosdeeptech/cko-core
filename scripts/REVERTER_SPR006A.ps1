#requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Core = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$InstallDir = Join-Path $Core "runtime\installations\SPR006A"
$CreatedFile = Join-Path $InstallDir "created_files.json"

if (-not (Test-Path -LiteralPath $CreatedFile)) {
    throw "Manifesto da SPR-006A não encontrado."
}

$Answer = Read-Host "Digite REVERTER para remover arquivos intactos da SPR-006A"
if ($Answer.Trim().ToUpper() -ne "REVERTER") {
    throw "Reversão cancelada."
}

$Created = Get-Content -Raw -LiteralPath $CreatedFile | ConvertFrom-Json
foreach ($Item in ($Created | Sort-Object { $_.path.Length } -Descending)) {
    $Full = Join-Path $Core $Item.path
    if (Test-Path -LiteralPath $Full -PathType Leaf) {
        $Current = (Get-FileHash -Algorithm SHA256 -LiteralPath $Full).Hash
        if ($Current -eq $Item.sha256) {
            Remove-Item -LiteralPath $Full -Force
            Write-Host "[REMOVIDO] $($Item.path)" -ForegroundColor Green
        } else {
            Write-Host "[PRESERVADO — ALTERADO] $($Item.path)" -ForegroundColor Yellow
        }
    }
}

$CanonicalDb = Join-Path $Core "runtime\database\cko_canonical.db"
if (Test-Path -LiteralPath $CanonicalDb) {
    Write-Host "[NÃO REMOVIDO] $CanonicalDb" -ForegroundColor Yellow
    Write-Host "O banco canônico deve ser removido manualmente apenas após confirmação." -ForegroundColor Yellow
}
