#requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Core = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$InstallDir = Join-Path $Core "runtime\installations\SPR005"
$CreatedFile = Join-Path $InstallDir "created_files.json"

if (-not (Test-Path -LiteralPath $CreatedFile)) {
    throw "Manifesto de instalação não encontrado. Reversão cancelada."
}

$Answer = Read-Host "Digite REVERTER para remover somente os arquivos intactos da SPR-005"
if ($Answer -cne "REVERTER") {
    throw "Reversão cancelada."
}

$Created = Get-Content -Raw -LiteralPath $CreatedFile | ConvertFrom-Json
$Removed = 0
$Preserved = 0

foreach ($Item in ($Created | Sort-Object { $_.path.Length } -Descending)) {
    $Full = Join-Path $Core $Item.path
    if (Test-Path -LiteralPath $Full -PathType Leaf) {
        $Current = (Get-FileHash -Algorithm SHA256 -LiteralPath $Full).Hash
        if ($Current -eq $Item.sha256) {
            Remove-Item -LiteralPath $Full -Force
            Write-Host "[REMOVIDO] $($Item.path)" -ForegroundColor Green
            $Removed++
        } else {
            Write-Host "[PRESERVADO — ALTERADO APÓS INSTALAÇÃO] $($Item.path)" -ForegroundColor Yellow
            $Preserved++
        }
    }
}

Write-Host ""
Write-Host "Arquivos removidos: $Removed"
Write-Host "Arquivos preservados: $Preserved"
Write-Host "Nenhum arquivo anterior à SPR-005 foi removido."
