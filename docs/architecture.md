# Arquitectura

## Visión de conjunto

```
┌───────────────────────────────────────────────────────────────┐
│                       presentation                            │
│   ┌──────────┐    ┌────────────┐    ┌─────────────────────┐   │
│   │  cli.py  │    │   tui.py   │    │  render.py (ASCII)  │   │
│   │ (typer)  │    │ (textual)  │    │                     │   │
│   └────┬─────┘    └──────┬─────┘    └──────────┬──────────┘   │
└────────┼────────────────┼─────────────────────┼───────────────┘
         │                │                     │
         ▼                ▼                     │
┌───────────────────────────────────────────────┼───────────────┐
│                       application             │               │
│   ┌─────────────────────┐    ┌────────────────┴───────────┐   │
│   │ carve_maze.py       │    │ play_session.py            │   │
│   │ (genera laberinto)  │    │ (estado de partida)        │   │
│   └──────────┬──────────┘    └────────────┬───────────────┘   │
└──────────────┼───────────────────────────┬┼───────────────────┘
               │                           ││
               ▼                           ▼▼
┌───────────────────────────────────────────────────────────────┐
│                         domain                                │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│   │  cell.py │  │ walls.py │  │ maze.py  │  │ direction.py │  │
│   │          │  │ (IntFlag)│  │(inmutab.)│  │              │  │
│   └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└───────────────────────────────────────────────────────────────┘
                              ▲
                              │ implementa interfaces de
                              │
┌───────────────────────────────────────────────────────────────┐
│                       infrastructure                          │
│   ┌──────────┐    ┌────────────────────┐                      │
│   │  rng.py  │    │   persistence.py   │                      │
│   │(Protocol)│    │ (JSON XDG savegame)│                      │
│   └──────────┘    └────────────────────┘                      │
└───────────────────────────────────────────────────────────────┘
```

## Reglas de dependencia

- `domain` no depende de nada salvo de la biblioteca estándar.
- `application` depende de `domain` y de interfaces (`Protocol`)
  declaradas en `domain` o en `application` mismo.
- `infrastructure` implementa esas interfaces y depende de `domain`.
- `presentation` orquesta `application` y `infrastructure`, y puede
  tocar `domain` solo para leer.

## Flujo de una partida

1. `cli.py` parsea argumentos (`--width`, `--height`, `--seed`,
   `--demo`, `--unicode`, `--legacy-bias`).
2. Construye un `RandomNumberGenerator` (de `infrastructure.rng`) con
   la semilla suministrada o aleatoria.
3. Llama a `carve_maze.carve(width, height, rng, legacy_bias=False)`,
   que delega en el algoritmo apropiado del `domain` y devuelve un
   `Maze` inmutable.
4. Si modo `--demo`: ejecuta `play_session.run_demo(maze, rng)` que
   reproduce un BFS desde la entrada hasta la salida imprimiendo cada
   paso. Útil para grabar y para los tests E2E.
5. Si modo interactivo: lanza `tui.AmazingApp(maze).run()`, que mete
   al jugador en el laberinto y le deja moverse con flechas.
6. Al ganar (o al pulsar `q`), `play_session` decide si guardar
   estadísticas a `~/.local/share/amazing/scores.json`.

## Inversión de dependencias

`application` recibe siempre el `Rng` (Protocol) por inyección, nunca
importa `random` directamente. Esto permite:

- Tests deterministas con un RNG falso que devuelve secuencias fijas.
- Tests de propiedad con `hypothesis` que barren miles de semillas.
- Un futuro modo "RNG criptográfico" sin tocar dominio.

## Errores

Tres excepciones del dominio (`src/amazing/domain/errors.py`):

- `InvalidDimensions(width, height)`: dimensiones no válidas.
- `OutOfBounds(cell, maze)`: un consumidor pidió una celda fuera del
  laberinto.
- `WallBlocksMovement(from_cell, direction)`: el jugador intentó
  cruzar una pared.

`presentation` las captura y las traduce a mensajes amigables en
español.

## Persistencia

Una única tabla JSON con récords personales por dimensión. Path XDG:
`$XDG_DATA_HOME/amazing/scores.json` o, por defecto,
`~/.local/share/amazing/scores.json`. Schema:

```json
{
  "version": 1,
  "records": [
    {"width": 10, "height": 10, "seed": 42, "moves": 31, "seconds": 12.4, "date": "2026-05-12T18:33:21Z"}
  ]
}
```

Validado con `pydantic` v2 al cargar/guardar.
