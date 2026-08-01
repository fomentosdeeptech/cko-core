#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$CoreRoot,
    [Parameter(Mandatory=$true)][string]$DatabasePath,
    [Parameter(Mandatory=$true)][string]$CheckpointRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$migrations = Join-Path $CoreRoot "migrations"
$env:PYTHONPATH = Join-Path $CoreRoot "src"

if (Test-Path -LiteralPath $DatabasePath) {
    $safeBackupDir = Join-Path $CheckpointRoot "database"
    if (-not (Test-Path -LiteralPath $safeBackupDir)) {
        New-Item -ItemType Directory -Path $safeBackupDir -Force | Out-Null
    }

    $safeBackup = Join-Path $safeBackupDir "cko_sqlite_backup_before_migration.db"

    python (Join-Path $CoreRoot "scripts\SPR005A_SQLITE_BACKUP.py") `
        --source $DatabasePath `
        --destination $safeBackup

    if ($LASTEXITCODE -ne 0) {
        throw "Falha no backup transacional do SQLite."
    }
}

python -m cko.persistence.cli `
    --database $DatabasePath `
    --migrations $migrations `
    migrate

if ($LASTEXITCODE -ne 0) {
    throw "Falha ao aplicar a migração."
}

python -m cko.persistence.cli `
    --database $DatabasePath `
    --migrations $migrations `
    validate

if ($LASTEXITCODE -ne 0) {
    throw "Falha na validação estrutural."
}
