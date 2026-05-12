# CLAUDE.md

## Misión

Tomar un programa de los años 80 (BASIC ZX Spectrum, Amstrad CPC, Sega
Mega Drive/Genesis, Commodore 64, MSX, Apple II, IBM PC, etc.) y
reconstruirlo como obra de software de 2026: juego completo, jugable,
empaquetado, testeado, documentado y con diseño visual cuidado.

Preservas la lógica funcional y el "alma" del original. Reimaginas todo
lo demás.

No es traducción línea a línea. Es reinterpretación con criterio de
ingeniero senior y sensibilidad de diseñador.

## Obtención del código original (FASE -1)

Antes de cualquier otra cosa, comprueba si `legacy/` contiene código
fuente.

### Caso A: `legacy/` ya tiene código
Procede directamente a la Fase 0.

### Caso B: `legacy/` está vacío o solo contiene una nota del usuario
La nota indicará el juego o tipo de programa que quiero recrear (ej.
"Manic Miner", "Jet Set Willy", "un juego de aventura conversacional tipo
Adventure", "un Frogger", "un Wizard's Castle"). Búscalo tú.

Tu trabajo es **encontrar código fuente real de los años 80** del
programa pedido, o de uno equivalente del mismo género y plataforma, y
copiarlo a `legacy/` antes de empezar.

**Plataformas objetivo, en orden de preferencia:**

1. **ZX Spectrum** (Sinclair BASIC, Z80 assembly). Mucho código preservado
   en formato `.tap`, `.tzx`, `.bas` y listados de revistas.
2. **Amstrad CPC** (Locomotive BASIC, Z80). Listados de revistas como
   *Amstrad Acción*, *Amstrad User*.
3. **Commodore 64** (CBM BASIC v2, 6502). Enorme archivo público.
4. **MSX** (MSX BASIC, Z80). Listados japoneses y europeos.
5. **Apple II** (Applesoft BASIC, Integer BASIC, 6502).
6. **IBM PC** (GW-BASIC, BASICA, Turbo Pascal, C). Listados de *Creative
   Computing*, *BYTE*, *Compute!*.
7. **Sega Mega Drive / Genesis** (68000 assembly, C con SGDK). Más
   complicado: no hay BASIC nativo, pero hay homebrews de los 90 y
   disassemblies de juegos comerciales.
8. **Atari 800 / ST**, **BBC Micro**, **Dragon 32**, **TI-99/4A** si
   procede.

**Fuentes recomendadas para buscar código:**

- World of Spectrum (`worldofspectrum.org`) — archivo masivo de software
  ZX, incluyendo listados originales escaneados de revistas.
- CPCWiki y CPC-POWER (`cpcwiki.eu`, `cpc-power.com`) — Amstrad CPC.
- archive.org — colecciones de revistas escaneadas: *Microhobby*,
  *MicroMania*, *Input*, *Your Sinclair*, *Crash*, *Amstrad Acción*,
  *Amiga Power*, *Compute!*, *Creative Computing*, *BYTE*, *Dr. Dobb's
  Journal*.
- GitHub: busca `site:github.com <nombre del juego> basic spectrum` o
  `site:github.com <género> zx spectrum source`.
- atariarchives.org, vintage-basic.net, classic-basic-games (Ahl's
  "BASIC Computer Games" y "More BASIC Computer Games" de los 70-80,
  perfectamente conservados y dominio funcional).
- SourceForge, archivos académicos viejos.
- Sega Retro y Plutiedev para Mega Drive.

**Procedimiento de búsqueda:**

1. Identifica el juego o género solicitado.
2. Usa `web_search` y `web_fetch` para localizar listados originales.
3. Prioriza código fuente real de la época (BASIC listados, ensamblador,
   Pascal). Evita ports modernos en Python/JavaScript: arruinan el
   ejercicio arqueológico.
4. Si encuentras varias versiones (Spectrum, Amstrad, C64), descárgalas
   todas a `legacy/` en subcarpetas por plataforma.
5. Si el juego pedido no existe o no encuentras fuentes, busca un
   equivalente del mismo género de la misma época.
6. Documenta en `legacy/SOURCES.md` la procedencia exacta.

**Si tras búsqueda razonable no encuentras nada utilizable:**

Como último recurso, usa uno de los clásicos de dominio público
indiscutible del libro *BASIC Computer Games* (David Ahl, 1978) o *More
BASIC Computer Games* (1979). Están todos en `vintage-basic.net` con
listados limpios. Documenta la sustitución como [LICENCIA CREATIVA] en
`CHANGELOG.md`.

Commit tras esta fase: `chore: import legacy source code from <fuente>`.

## Modo de operación: AUTÓNOMO

Trabajas sin pedir permiso. No haces preguntas de clarificación. No
esperas validación humana entre fases. Tomas decisiones, las documentas
en ADRs y sigues.

Cuando dudes entre dos opciones razonables, eliges la que más respete
estas prioridades, en este orden:

1. Que el juego funcione end-to-end y sea jugable.
2. Que el código sea idiomático Python 2026 y pase calidad estricta.
3. Que la presentación sea memorable visualmente.
4. Que la fidelidad al original sea reconocible en mecánicas y espíritu.
5. Que la arquitectura sea limpia y extensible.

Si encuentras un bug en el original: arréglalo y documéntalo en
`docs/original_program_analysis.md` bajo "Bugs corregidos".

Si el original tiene ambigüedades: resuélvelas con el criterio más
generoso para el jugador moderno y documéntalo como [LICENCIA CREATIVA]
en `CHANGELOG.md`.

Si te falta una pieza de información: asume lo más probable, marca
[SUPUESTO: ...] en el código o en docs, y sigue.

NO PARAS hasta que:

- `uv sync` funcione sin errores.
- `ruff check` esté limpio.
- `ruff format --check` esté limpio.
- `mypy --strict src` pase sin errores.
- `pytest` pase todos los tests con cobertura >=80% en `domain/`.
- El juego sea ejecutable con `uv run <paquete>` y jugable de principio a
  fin.
- Exista un modo `--demo` determinista que complete una partida sin
  intervención humana.
- README, CHANGELOG y los tres documentos de `docs/` estén escritos.

## Stack obligatorio

- Python 3.13+ (PEP 695 generics, type params modernos).
- Gestión: `uv` + `pyproject.toml` (PEP 621), `src/` layout.
- Modelos: `pydantic` v2 para fronteras IO/config; `dataclass(frozen=True,
  slots=True)` para dominio puro.
- CLI: `typer` con `rich` integrado.
- TUI (default si no hay razón fuerte para gráfico): `textual` con CSS
  propio en `src/<paquete>/assets/`.
- Logging: `structlog` con render bonito en dev, JSON en prod.
- Tests: `pytest` + `hypothesis` para propiedades.
- Calidad: `ruff` (lint+format), `mypy --strict`, `pre-commit`.
- CI: GitHub Actions con matriz Python 3.13 y 3.14.

## Reglas de código innegociables

- `mypy --strict` pasa siempre antes de marcar tarea hecha.
- `ruff check` y `ruff format` limpios.
- Type hints completos. Nombres expresivos en inglés.
- Comentarios en español solo donde aclaren intención no obvia.
- Funciones <40 líneas salvo justificación documentada.
- Cero globales mutables.
- `match/case` donde aclare.
- Modelos de dominio inmutables (`frozen=True, slots=True`).
- IO aislado en `infrastructure/`. Dominio puro, testeable sin mocks.
- RNG inyectado, nunca `random.random()` global.

## Marcadores de confianza

- `[DATO]`: verificado en el código original.
- `[INFERENCIA]`: deducido con alta confianza del contexto.
- `[SUPUESTO]`: asumido, podría estar equivocado.
- `[LICENCIA CREATIVA]`: decisión de diseño 2026 que se aparta del
  original conscientemente.

## Idioma

- Código, identificadores, mensajes de log y commits: inglés.
- Mensajes al usuario final del juego: español.
- Documentación (`docs/`, README, CHANGELOG): español.

## Filosofía final

Mejor entregar un juego completo, jugable y bonito con 3 [SUPUESTO]
documentados, que no entregar nada por miedo a equivocarse.
