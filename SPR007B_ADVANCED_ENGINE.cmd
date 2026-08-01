@echo off
chcp 65001 >nul
setlocal enableextensions
set "SCRIPT_DIR=%~dp0"
if not defined SCRIPT_DIR set "SCRIPT_DIR=%CD%"
set "PS1=%SCRIPT_DIR%SPR007B_ADVANCED_ENGINE.ps1"
if not exist "%PS1%" (
    echo [SPR007B] Arquivo PowerShell nao encontrado: %PS1%
    exit /b 1
)
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "EXIT_CODE=%ERRORLEVEL%"
if /I "%SPR007B_SUPPRESS_PAUSE%" NEQ "1" (
    if /I "%CMDCMDLINE%" NEQ "" (
        if /I not "%CMDCMDLINE: /c=%"=="%CMDCMDLINE%" (
            rem no-op
        ) else (
            echo Pressione Enter para sair...
            pause >nul
        )
    )
)
exit /b %EXIT_CODE%
