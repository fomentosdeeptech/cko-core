#requires -Version 5.1
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-JsonLine {
    param(
        [Parameter(Mandatory=$true)] [string]$Level,
        [Parameter(Mandatory=$true)] [string]$Event,
        [Parameter(Mandatory=$true)] [string]$Message,
        [Parameter(Mandatory=$false)] [hashtable]$Context = @{}
    )

    $payload = [ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        level = $Level
        event = $Event
        message = $Message
        context = $Context
    }

    $line = $payload | ConvertTo-Json -Compress -Depth 10
    Add-Content -LiteralPath $script:BootstrapLog -Value $line -Encoding UTF8
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory=$true)] [string]$Command,
        [Parameter(Mandatory=$false)] [string[]]$Arguments = @()
    )

    try {
        $output = & $Command @Arguments 2>&1
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            throw "Command failed with exit code $exitCode"
        }
        return $output
    }
    catch {
        throw
    }
}

$script:BootstrapLog = $null
$script:ExitCode = 0

try {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    if ([string]::IsNullOrWhiteSpace($scriptDir)) {
        $scriptDir = (Get-Location).Path
    }
    $root = [System.IO.Path]::GetFullPath((Join-Path $scriptDir "."))
    $runtimeDir = Join-Path $root "runtime"
    $databaseDir = Join-Path $runtimeDir "database"
    $logsDir = Join-Path $root "logs"
    $reportsDir = Join-Path $root "reports"
    $canonicalDatabase = Join-Path $databaseDir "cko_canonical.db"
    $bootstrapLog = Join-Path $logsDir "SPR007B_BOOTSTRAP.log"
    $script:BootstrapLog = $bootstrapLog

    if (-not (Test-Path -LiteralPath $bootstrapLog)) {
        Set-Content -LiteralPath $bootstrapLog -Value "" -Encoding UTF8
    }

    Write-JsonLine -Level "INFO" -Event "bootstrap.start" -Message "Iniciando bootstrap SPR-007B" -Context @{root=$root}

    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
    New-Item -ItemType Directory -Path $databaseDir -Force | Out-Null
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null

    foreach ($path in @($runtimeDir, $databaseDir, $logsDir, $reportsDir)) {
        $testFile = Join-Path $path ".write_test"
        Set-Content -LiteralPath $testFile -Value "ok" -Encoding UTF8
        Remove-Item -LiteralPath $testFile -Force -ErrorAction SilentlyContinue
    }

    if (-not (Test-Path -LiteralPath $canonicalDatabase -PathType Leaf)) {
        throw "Banco canônico não encontrado: $canonicalDatabase"
    }

    $pythonCandidates = @(
        "python3.13.exe",
        "py.exe",
        "python.exe"
    )

    $pythonCommand = $null
    foreach ($candidate in $pythonCandidates) {
        if ($candidate -eq "py.exe") {
            if (Get-Command py.exe -ErrorAction SilentlyContinue) {
                $pythonCommand = "py"
                break
            }
            continue
        }
        $resolved = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($resolved) {
            $pythonCommand = $candidate
            break
        }
    }

    if (-not $pythonCommand) {
        throw "Python 3.13 não encontrado"
    }

    if ($pythonCommand -eq "py") {
        $versionOutput = & py -3.13 --version 2>&1
        $script:ExitCode = $LASTEXITCODE
        if ($script:ExitCode -ne 0) {
            throw "Falha ao validar o Python 3.13"
        }
        $pythonVersion = ($versionOutput | Select-Object -First 1)
    }
    else {
        $versionOutput = & $pythonCommand --version 2>&1
        $script:ExitCode = $LASTEXITCODE
        if ($script:ExitCode -ne 0) {
            throw "Falha ao validar o Python 3.13"
        }
        $pythonVersion = ($versionOutput | Select-Object -First 1)
    }

    if ($pythonVersion -notmatch '3\.13') {
        throw "Versão do Python incompatível: $pythonVersion"
    }

    $advancedEngine = Join-Path $root "advanced_engine.py"
    if (-not (Test-Path -LiteralPath $advancedEngine -PathType Leaf)) {
        throw "advanced_engine.py não encontrado"
    }

    if (-not (Test-Path -LiteralPath (Join-Path $root "runtime") -PathType Container)) {
        throw "Diretório runtime ausente"
    }

    if (-not (Test-Path -LiteralPath (Join-Path $root "logs") -PathType Container)) {
        throw "Diretório logs ausente"
    }

    if (-not (Test-Path -LiteralPath (Join-Path $root "reports") -PathType Container)) {
        throw "Diretório reports ausente"
    }

    $pythonArg = @()
    if ($pythonCommand -eq "py") {
        $pythonArg = @('-3.13', $advancedEngine, '--project-root', $root)
    }
    else {
        $pythonArg = @($advancedEngine, '--project-root', $root)
    }

    $bootstrapLogDir = Split-Path -Parent $bootstrapLog
    New-Item -ItemType Directory -Path $bootstrapLogDir -Force | Out-Null
    if (-not (Test-Path -LiteralPath $bootstrapLog)) {
        Set-Content -LiteralPath $bootstrapLog -Value "" -Encoding UTF8
    }

    if ($pythonCommand -eq "py") {
        & py -3.13 $advancedEngine --project-root $root
    }
    else {
        & $pythonCommand $advancedEngine --project-root $root
    }
    $script:ExitCode = $LASTEXITCODE

    if ($script:ExitCode -ne 0) {
        throw "advanced_engine.py terminou com falha"
    }

    Write-JsonLine -Level "INFO" -Event "bootstrap.success" -Message "Bootstrap concluído com sucesso" -Context @{root=$root; pythonVersion=$pythonVersion}
    Write-Host "[SPR007B] Bootstrap concluído com sucesso." -ForegroundColor Green
}
catch {
    $script:ExitCode = 1
    Write-JsonLine -Level "ERROR" -Event "bootstrap.failed" -Message $_.Exception.Message -Context @{root=$root}
    Write-Host "[SPR007B] Erro: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    if ($env:SPR007B_SUPPRESS_PAUSE -ne "1") {
        if ($Host.Name -eq 'ConsoleHost') {
            Write-Host "Pressione Enter para sair..."
            Read-Host | Out-Null
        }
    }
}

exit $script:ExitCode
