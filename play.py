#!/usr/bin/env python3
"""Arranque rápido de AMAZING como un solo programa Python.

Uso:
    python play.py              # juego TUI interactivo (default)
    python play.py print        # vuelco ASCII fiel al listado de 1978
    python play.py demo         # demo determinista (BFS)
    python play.py tests        # pasarela completa de calidad
    python play.py --help       # ayuda del CLI

El script funciona aunque no tengas las dependencias instaladas: detecta
el entorno (uv preferido, pip como respaldo) y se instala solo la primera
vez. En Linux, macOS y Windows, idéntico.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_PYTHON = (3, 13)


def _die(message: str, code: int = 1) -> int:
    sys.stderr.write(message.rstrip() + "\n")
    return code


def _check_python_version() -> None:
    if sys.version_info < MIN_PYTHON:
        need = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
        have = f"{sys.version_info.major}.{sys.version_info.minor}"
        sys.stderr.write(
            f"AMAZING necesita Python {need}+ (tu intérprete es {have}).\n"
            "Si tienes 'uv' instalado, ejecuta `./run` (Linux/macOS) o\n"
            "`run.ps1` / `run.bat` (Windows): uv descarga Python 3.13 solo.\n"
        )
        raise SystemExit(1)


def _have_package() -> bool:
    try:
        import amazing  # noqa: F401
    except ImportError:
        return False
    return True


def _run_amazing_inprocess(args: list[str]) -> int:
    from amazing.presentation.cli import app

    sys.argv = ["amazing", *args]
    try:
        app()
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else 0
    return 0


def _bootstrap_with_uv(args: list[str]) -> int:
    venv = ROOT / ".venv"
    if not venv.exists():
        print(">> primer arranque: instalando dependencias con `uv sync`...")
        subprocess.check_call(["uv", "sync", "--all-extras"], cwd=ROOT)
    if args and args[0] == "tests":
        return _run_tests_with_uv()
    return subprocess.call(["uv", "run", "amazing", *args], cwd=ROOT)


def _run_tests_with_uv() -> int:
    steps = (
        ["ruff", "format", "--check", "."],
        ["ruff", "check", "."],
        ["mypy", "--strict", "src"],
        ["pytest"],
    )
    for step in steps:
        code = subprocess.call(["uv", "run", *step], cwd=ROOT)
        if code != 0:
            return code
    return 0


def _bootstrap_with_pip(args: list[str]) -> int:
    print(">> primer arranque: instalando AMAZING en el intérprete actual con `pip`...")
    pip_args = [sys.executable, "-m", "pip", "install", "-e", ".[dev]"]
    code = subprocess.call(pip_args, cwd=ROOT)
    if code != 0:
        return _die("Fallo al instalar con pip. Mira el mensaje de arriba o usa `uv` (más fiable).")
    if not _have_package():
        return _die("La instalación con pip terminó pero `amazing` sigue sin importarse.")
    if args and args[0] == "tests":
        return _run_tests_inprocess()
    return _run_amazing_inprocess(args)


def _run_tests_inprocess() -> int:
    import pytest

    return int(pytest.main(["-q"]))


def _install_hint() -> int:
    sys.stderr.write(
        "\n"
        "AMAZING no encuentra ni `uv` ni `pip` utilizables.\n"
        "\n"
        "Instala una de estas opciones:\n"
        "\n"
        "  1) uv (recomendado: maneja Python y dependencias):\n"
        "     Linux/macOS:  curl -LsSf https://astral.sh/uv/install.sh | sh\n"
        '     Windows:      powershell -c "irm https://astral.sh/uv/install.ps1 | iex"\n'
        "\n"
        f"  2) pip (si ya tienes Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+):\n"
        f"     {sys.executable} -m ensurepip\n"
        "\n"
        "Luego vuelve a ejecutar:  python play.py\n"
    )
    return 2


def main(argv: list[str] | None = None) -> int:
    _check_python_version()
    os.chdir(ROOT)
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        args = ["play"]

    if _have_package():
        if args[0] == "tests":
            return _run_tests_inprocess()
        return _run_amazing_inprocess(args)

    if shutil.which("uv"):
        return _bootstrap_with_uv(args)

    if shutil.which("pip") or _python_has_pip():
        return _bootstrap_with_pip(args)

    return _install_hint()


def _python_has_pip() -> bool:
    try:
        import pip  # noqa: F401
    except ImportError:
        return False
    return True


if __name__ == "__main__":
    sys.exit(main())
