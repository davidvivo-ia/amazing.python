@echo off
rem Arranque rapido de AMAZING en Windows (cmd.exe).
rem
rem Uso:
rem   run            juego TUI interactivo (default)
rem   run print      vuelco ASCII fiel al 1978
rem   run demo       demo determinista BFS
rem   run tests      pasarela completa: ruff + mypy + pytest
rem   run --help     ayuda completa del CLI

setlocal
cd /d "%~dp0"

where uv >nul 2>&1
if errorlevel 1 (
    echo uv no encontrado. Instalalo con:
    echo     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 ^| iex"
    echo (o visita https://docs.astral.sh/uv/ para otras opciones^)
    exit /b 1
)

if not exist ".venv" (
    echo ^>^> primer arranque: instalando dependencias con uv sync...
    uv sync --all-extras || exit /b 1
)

if "%~1"=="" goto play
if /I "%~1"=="tests" goto tests

uv run amazing %*
exit /b %errorlevel%

:play
uv run amazing play
exit /b %errorlevel%

:tests
uv run ruff format --check . || exit /b 1
uv run ruff check . || exit /b 1
uv run mypy --strict src || exit /b 1
uv run pytest
exit /b %errorlevel%
