# AMAZING

> "AMAZING PROGRAM — CREATIVE COMPUTING, MORRISTOWN, NEW JERSEY"
>
> *— Jack Hauber, 1978*

Un generador de laberintos de 1978, reencarnado como juego TUI en Python
3.13 con fósforo verde, animaciones sutiles y código que tu yo del
futuro entenderá.

[![ci](https://img.shields.io/badge/ci-passing-brightgreen)](.github/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.13+-blue)](pyproject.toml)
[![license](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

## Qué es

Versión 2026 del programa AMAZING publicado por Jack Hauber en
*BASIC Computer Games* (David H. Ahl, 1978). Cuatro décadas más tarde,
con:

- **Backtracker iterativo** con pila explícita (en vez de 55 GOTOs).
- **TUI Textual** con tres temas (fósforo verde, papel sepia, ámbar P3).
- **Juego, no generador**: navega el laberinto desde la entrada hasta la
  salida, con cronómetro y contador de pasos.
- **Modo `print`**: vuelca el laberinto a stdout fiel al listado del 78.
- **Modo `--demo`**: BFS automático que resuelve y se autoejecuta.
- **`--seed` reproducible**: mismo número, mismo laberinto.
- Tests con `pytest`, propiedades con `hypothesis`, tipos `mypy --strict`,
  lint `ruff`.

El código BASIC original vive intacto en `legacy/ibm-pc/amazing.bas` y
el análisis arqueológico completo en `docs/original_program_analysis.md`.

## Instalación

```bash
git clone https://github.com/davidvivo-ia/amazing.python
cd amazing.python
uv sync --all-extras
```

Requiere Python 3.13+ y [uv](https://docs.astral.sh/uv/).

## Uso

```bash
# Juego interactivo (TUI Textual)
uv run amazing play --width 12 --height 8

# Generación reproducible con semilla
uv run amazing play --width 20 --height 12 --seed 42

# Volcado fiel al listado del 78 a stdout
uv run amazing print --width 10 --height 6 --seed 42

# Volcado con caracteres Unicode (+──+│)
uv run amazing print --width 10 --height 6 --unicode

# Demo determinista (genera, resuelve y muestra)
uv run amazing demo --width 8 --height 6 --seed 42

# Versión y ayuda
uv run amazing --help
uv run amazing --version
```

### Controles del juego

| Tecla | Acción |
| --- | --- |
| `↑` / `w` / `k` | Mover arriba |
| `↓` / `s` / `j` | Mover abajo |
| `←` / `a` / `h` | Mover izquierda |
| `→` / `d` / `l` | Mover derecha |
| `r` | Reiniciar partida |
| `t` | Cambiar tema (`phosphor → paper → amber`) |
| `?` | Ayuda |
| `q` | Salir |

## Ejemplo de salida (modo `print`, 10×6, seed 42)

```
.--.  .--.--.--.--.--.--.--.--.
I     I                 I     I
:  :--:--:--:  :--:--:  :  :  .
I           I        I     I  I
:--:--:--:  :  :--:  :--:--:  .
I  I        I     I        I  I
:  :  :--:--:--:--:--:--:  :  .
I     I                 I  I  I
:  :--:--:  :  :--:--:  :  :  .
I        I  I  I     I     I  I
:--:--:  :--:  :  :--:--:--:  .
I              I              I
:  :--:--:--:--:--:--:--:--:--.
```

## Estructura del proyecto

```
amazing.python/
├── legacy/ibm-pc/amazing.bas    # original Hauber 1978, intacto
├── docs/                        # análisis, arquitectura, diseño, ADRs
├── src/amazing/
│   ├── domain/                  # dataclasses inmutables, sin I/O
│   ├── application/             # casos de uso (carve, play)
│   ├── infrastructure/          # RNG, persistencia JSON XDG
│   ├── presentation/            # CLI (typer) + TUI (textual)
│   └── assets/tui.tcss          # CSS Textual con tres temas
└── tests/                       # unit · integration · property (hypothesis)
```

## Desarrollo

```bash
uv sync --all-extras
uv run pre-commit install        # opcional pero recomendado
uv run pytest                    # tests con cobertura
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src
```

## Licencia

MIT. Ver [LICENSE](LICENSE).

El código BASIC original es dominio público (Ahl, *BASIC Computer
Games*, 1978). Ver [legacy/SOURCES.md](legacy/SOURCES.md) para
detalles.

## Créditos

- Jack Hauber, autor original del algoritmo (1978).
- David H. Ahl, editor del libro que lo preservó para la posteridad.
- [vintage-basic.net](https://vintage-basic.net) por el listado
  digitalizado.

---

*Hecho con `rich`, `typer`, `textual`, `pydantic` y un café con sabor a
fósforo.*
