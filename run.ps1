# Arranque rápido de AMAZING en Windows (PowerShell).
#
# Uso:
#   .\run.ps1                # juego TUI interactivo
#   .\run.ps1 print          # vuelco ASCII fiel al 1978
#   .\run.ps1 demo           # demo determinista BFS
#   .\run.ps1 tests          # pasarela completa: ruff + mypy + pytest
#   .\run.ps1 --help         # ayuda completa del CLI

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv no encontrado. Instálalo con:"
    Write-Host '    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
    Write-Host "(o visita https://docs.astral.sh/uv/ para otras opciones)"
    exit 1
}

if (-not (Test-Path -Path '.venv' -PathType Container)) {
    Write-Host '>> primer arranque: instalando dependencias con uv sync...'
    uv sync --all-extras
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$first = if ($Args.Count -gt 0) { $Args[0] } else { 'play' }

switch ($first) {
    'tests' {
        uv run ruff format --check .
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        uv run ruff check .
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        uv run mypy --strict src
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        uv run pytest
        exit $LASTEXITCODE
    }
    default {
        if ($Args.Count -eq 0) {
            uv run amazing play
        } else {
            uv run amazing @Args
        }
        exit $LASTEXITCODE
    }
}
