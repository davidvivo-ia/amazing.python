# ADR 0002 — Modelo de dominio: dataclasses frozen + IntFlag

- Estado: Aceptada
- Fecha: 2026-05-12

## Contexto

El original guarda el laberinto en dos matrices `W(H,V)` y `V(H,V)` de
enteros. `W` codifica orden de visita y `V` codifica con valores 0/1/2/3
qué paredes de cada celda están en pie.

Necesitamos un modelo Python que sea:
- Inmutable (un laberinto no debe mutar después de generarse).
- Eficiente en memoria (mazes 50×50 = 2500 celdas).
- Auto-documentado (no más "qué quería decir `V(I,J)=3`").
- Validable y serializable.

## Opciones consideradas

1. Diccionarios `dict[tuple[int, int], int]`. Flexibles, lentos.
2. Listas anidadas `list[list[int]]` como el original. Familiar, pero
   ofuscado.
3. `pydantic.BaseModel`. Validación gratis, pero overhead innecesario en
   el hot path y poco amigable con `slots`.
4. `numpy` arrays. Tentador para mazes enormes; rompe el espíritu
   "dependencias mínimas".
5. **`dataclass(frozen=True, slots=True)` + `IntFlag`** para las paredes.

## Decisión

Opción 5. El dominio queda:

```python
class Wall(IntFlag):
    NONE = 0
    RIGHT = 1
    BOTTOM = 2

@dataclass(frozen=True, slots=True)
class Cell:
    col: int
    row: int

@dataclass(frozen=True, slots=True)
class Maze:
    width: int
    height: int
    walls: tuple[tuple[Wall, ...], ...]   # walls[col][row]
    entry: Cell
    exit: Cell
```

`tuple` en lugar de `list` para mantener la inmutabilidad real.
`pydantic` solo aparece en `infrastructure.persistence` para el JSON
de récords.

## Consecuencias

- Dominio testeable sin mocks ni I/O.
- `mypy --strict` cómodo, sin `Any`.
- Una pared se consulta con `Wall.RIGHT in maze.wall_at(cell)`, legible
  comparado con `V(I,J) >= 2`.
- La construcción del `Maze` requiere copiar las tuplas → la generación
  usa internamente listas mutables y al final hace `freeze()`.
- Penalización de memoria pequeña (`slots` mitiga).
