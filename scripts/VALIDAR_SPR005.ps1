#requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Core = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$InstallDir = Join-Path $Core "runtime\installations\SPR005"

$Required = @(
    "src\cko\contracts\__init__.py",
    "src\cko\contracts\scanner.py",
    "src\cko\contracts\repositories.py",
    "src\cko\models\__init__.py",
    "src\cko\models\document.py",
    "src\cko\models\job.py",
    "src\cko\services\__init__.py",
    "src\cko\api\__init__.py",
    "docs\architecture\CKO_CORE_BASELINE_2026-07-11.md",
    "docs\sprint\SPR005_REPORT.md",
    "tests\test_architecture_spr005.py"
)

$Missing = @()
foreach ($Relative in $Required) {
    if (Test-Path -LiteralPath (Join-Path $Core $Relative)) {
        Write-Host "[OK] $Relative" -ForegroundColor Green
    } else {
        Write-Host "[AUSENTE] $Relative" -ForegroundColor Red
        $Missing += $Relative
    }
}

$ProtectedFile = Join-Path $InstallDir "protected_before.json"
if (-not (Test-Path -LiteralPath $ProtectedFile)) {
    $Missing += "runtime\installations\SPR005\protected_before.json"
} else {
    $Protected = Get-Content -Raw -LiteralPath $ProtectedFile | ConvertFrom-Json
    foreach ($Item in $Protected) {
        $Full = Join-Path $Core $Item.path
        if (-not (Test-Path -LiteralPath $Full)) {
            Write-Host "[PROTEGIDO AUSENTE] $($Item.path)" -ForegroundColor Red
            $Missing += $Item.path
        } else {
            $Current = (Get-FileHash -Algorithm SHA256 -LiteralPath $Full).Hash
            if ($Current -ne $Item.sha256) {
                Write-Host "[PROTEGIDO ALTERADO] $($Item.path)" -ForegroundColor Red
                $Missing += $Item.path
            } else {
                Write-Host "[PRESERVADO] $($Item.path)" -ForegroundColor Yellow
            }
        }
    }
}

if ($Missing.Count -gt 0) {
    throw "SPR-005 não validada. Pendências encontradas: $($Missing.Count)"
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "              SPR-005 VALIDADA" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host "Nenhum arquivo protegido foi alterado."
Write-Host "Nenhum banco foi alterado."
Write-Host "Nenhum scanner foi executado."
