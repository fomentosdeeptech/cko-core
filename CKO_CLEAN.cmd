@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONPATH=%~dp0src"
pushd "%~dp0"
python -m cko.core.workspace.cli clean %*
set "CKO_EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %CKO_EXIT_CODE%
