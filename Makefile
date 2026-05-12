# AMAZING — atajos de desarrollo.
# Uso: `make`, `make play`, `make print`, `make demo`, `make tests`, `make all`.

.DEFAULT_GOAL := play
.PHONY: install play print demo tests fmt lint types cov clean all

install:        ## sincronizar dependencias con uv
	uv sync --all-extras

play: install   ## lanzar la TUI Textual interactiva
	uv run amazing play

print: install  ## vuelco ASCII fiel al listado de 1978
	uv run amazing print --width 12 --height 8 --seed 42

demo: install   ## demo determinista BFS
	uv run amazing demo --width 12 --height 8 --seed 42

fmt: install
	uv run ruff format .

lint: install
	uv run ruff check .

types: install
	uv run mypy --strict src

cov: install
	uv run pytest

tests: install  ## pasarela completa de calidad
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy --strict src
	uv run pytest

all: tests      ## alias de `make tests`

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
