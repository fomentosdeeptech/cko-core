#requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Core = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:PYTHONPATH = Join-Path $Core "src"

$Code = @"
from pathlib import Path
from cko.repository.database import initialize_canonical_database, canonical_database_path

core = Path(r'$Core')
applied = initialize_canonical_database(core)
print('Banco:', canonical_database_path(core))
print('Migrações aplicadas:', applied if applied else 'nenhuma; schema já estava atualizado')
"@

python -c $Code
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao inicializar o banco canônico."
}
