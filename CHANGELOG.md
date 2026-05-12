# Changelog

Todas las notas siguen [Keep a Changelog](https://keepachangelog.com/) y el
proyecto sigue [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-05-12

### Preservado del original

- **Cabecera** "AMAZING PROGRAM / CREATIVE COMPUTING, MORRISTOWN, NEW
  JERSEY", reproducida tanto en el modo `print` como en la portada de la
  TUI.
- **Algoritmo conceptual**: laberinto rectangular perfecto, con una sola
  entrada en el borde superior (columna aleatoria) y una sola salida en
  el borde inferior.
- **Estilo de render ASCII**: caracteres `.`, `:`, `-`, `I`, `  ` y la
  geometría de 3 columnas de terminal por celda, idéntica al listado
  de 1978. Disponible con `--style legacy` (por defecto en `amazing
  print`).
- **Sin tiempo, sin enemigos, sin vidas**: el original era un puzzle
  contemplativo y mantenemos ese espíritu. Cronómetro y contador de
  pasos son meramente informativos.

### Modernizado

- Reescritura completa en Python 3.13 con `dataclass(frozen, slots)`,
  `IntFlag` para las paredes, `Protocol` para el RNG, `match/case` donde
  aclara, type hints estrictos (`mypy --strict`).
- Arquitectura por capas: `domain` puro · `application` con casos de uso
  · `infrastructure` con RNG y persistencia · `presentation` con CLI y
  TUI. Cero `import textual` desde dominio.
- 55 `GOTO`s del original sustituidos por un solo bucle while con pila
  explícita.
- Gestión con `uv` + `pyproject.toml`; lint con `ruff`; tests con
  `pytest` + `hypothesis`; pre-commit y CI configurados.

### Añadido

- **TUI con Textual** (modo `amazing play`) con tres temas (fósforo
  verde por defecto, papel sepia y ámbar P3) intercambiables con `t`.
- **Modo `--seed`** para laberintos reproducibles.
- **Modo `amazing demo`** que genera, resuelve con BFS y renderiza el
  recorrido. Útil para grabar GIFs y como prueba E2E determinista.
- **Modo `amazing print --style unicode`** con caracteres de box-drawing
  (`+──+│`) para terminales modernas.
- **Persistencia de récords personales** en JSON bajo XDG
  (`~/.local/share/amazing/scores.json`), validada con pydantic.
- **Marcador del jugador** (`*` / `◉`) y **estela de visitados** (`·`)
  en los renders interactivos.
- **Flecha que apunta a la salida** debajo del laberinto en modo
  `print` y `demo`.

### Licencias creativas tomadas

- Sustituido el algoritmo *hunt-and-kill* con escaneo del original por
  un **recursive-backtracker iterativo**. Ambos producen un laberinto
  perfecto del mismo tamaño con entrada arriba y salida abajo; el nuevo
  tiene mejores propiedades estadísticas (menos sesgo direccional). La
  documentación arqueológica en `docs/original_program_analysis.md` §2.5
  cubre la justificación. El modo `--legacy-bias` queda planeado para
  v1.1 en `TODO.md`.
- **Ganar requiere "salir" caminando hacia el sur a través del hueco**,
  no simplemente pisar la última celda. Decidimos que ese segundo
  movimiento le da al final una sensación de cierre que el listado
  original (que sólo imprimía un laberinto estático) nunca tuvo.
- **El archivo `c.bas` mencionado por el usuario no existe** en el repo
  GReaperEx/bcg. Sustituido por `amazing.bas` del mismo repositorio,
  coherente con el nombre del directorio del proyecto (`amazing.python`).
  Sustitución documentada en `legacy/SOURCES.md`.
- **Mensajes al usuario en español** (cabeceras de juego, mensajes de
  error, panel de estadísticas) frente al inglés del original. La CLI y
  los logs siguen en inglés.

### Bugs corregidos

- **BUG-1 — validación de dimensiones**: la línea 102 del original
  rechaza erróneamente `1×N` y `N×1` (un único corredor recto). Hauber
  quería rechazar sólo `1×1`. Aceptamos los corredores y testeamos el
  caso explícitamente.
- **BUG-3 — re-entrada infinita en grids 1×N**: como `1×N` no llegaba
  a la lógica del original, la trampa nunca disparó. Aquí sí se podía:
  añadimos un fallback explícito en el carver que abre la salida bajo
  la última celda del corredor si la generación normal no creó ninguna.
- **BUG-2 — sesgo direccional del scan**: no es un bug funcional, pero
  el nuevo algoritmo lo elimina por construcción. El modo legacy queda
  documentado para una versión futura.

### Documentación

- `docs/original_program_analysis.md` (encuadre + arqueología).
- `docs/architecture.md` (diagrama de capas y reglas de dependencia).
- `docs/design.md` (sistema de diseño, paleta, tipografía, accesibilidad).
- `docs/adr/0001..0004` (decisiones de presentación, dominio, RNG y
  estética).
- `docs/postmortem.md` (qué se ganó, qué se perdió).

### Verificación

- 86 tests `pytest` (unidad, integración y propiedad con `hypothesis`).
- `ruff check`, `ruff format --check`, `mypy --strict` limpios.
- CI con GitHub Actions sobre Python 3.13.
- Cobertura ≥80% en `domain/`, `application/` y `infrastructure/`.
