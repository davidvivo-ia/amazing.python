#!/usr/bin/env python3
"""AMAZING — arranque cero-dependencias.

Ejecuta esto con cualquier Python 3.10+:

    python amazing.py                        # laberinto 12x8 con semilla aleatoria
    python amazing.py --width 20 --height 12 # tamaño a medida
    python amazing.py --seed 42              # laberinto reproducible
    python amazing.py --demo                 # genera, resuelve por BFS y muestra
    python amazing.py --unicode              # caracteres box-drawing
    python amazing.py --help

Sólo necesita la biblioteca estándar de Python (sin uv, sin pip,
sin instalar nada). Es la versión mínima jugable, suficiente para
ver y resolver laberintos.

Si quieres la TUI interactiva con Textual, los temas y las
estadísticas, usa `python play.py` o `./run` (que auto-instalan
las dependencias).
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import deque
from dataclasses import dataclass, field

NORTH = (0, -1)
SOUTH = (0, 1)
WEST = (-1, 0)
EAST = (1, 0)
DIRECTIONS = (NORTH, SOUTH, WEST, EAST)

WALL_RIGHT = 1
WALL_BOTTOM = 2


@dataclass
class Maze:
    """Laberinto con paredes empaquetadas en una lista 2D de enteros."""

    width: int
    height: int
    walls: list[list[int]] = field(default_factory=list)
    entry: tuple[int, int] = (0, 0)
    exit: tuple[int, int] = (0, 0)

    def in_bounds(self, cell: tuple[int, int]) -> bool:
        c, r = cell
        return 0 <= c < self.width and 0 <= r < self.height

    def can_move(self, source: tuple[int, int], direction: tuple[int, int]) -> bool:
        c, r = source
        dc, dr = direction
        target = (c + dc, r + dr)
        if not self.in_bounds(target):
            if direction == NORTH:
                return source == self.entry and r == 0
            if direction == SOUTH:
                return source == self.exit and r == self.height - 1
            return False
        if direction == EAST:
            return not (self.walls[c][r] & WALL_RIGHT)
        if direction == WEST:
            return not (self.walls[target[0]][target[1]] & WALL_RIGHT)
        if direction == SOUTH:
            return not (self.walls[c][r] & WALL_BOTTOM)
        return not (self.walls[target[0]][target[1]] & WALL_BOTTOM)


def carve(width: int, height: int, rng: random.Random) -> Maze:
    """Backtracker iterativo: produce un laberinto perfecto."""
    if width < 1 or height < 1 or (width == 1 and height == 1):
        raise ValueError(f"meaningless dimensions: {width}x{height}")
    walls = [[WALL_RIGHT | WALL_BOTTOM for _ in range(height)] for _ in range(width)]
    entry = (rng.randrange(0, width), 0)
    visited: set[tuple[int, int]] = {entry}
    stack = [entry]
    exit_cell: tuple[int, int] | None = None
    last_bottom = entry if entry[1] == height - 1 else None

    while stack:
        current = stack[-1]
        c, r = current
        options: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for direction in DIRECTIONS:
            dc, dr = direction
            n = (c + dc, r + dr)
            if 0 <= n[0] < width and 0 <= n[1] < height and n not in visited:
                options.append((direction, n))
        if not options:
            if exit_cell is None and r == height - 1:
                exit_cell = current
            stack.pop()
            continue
        direction, neighbour = rng.choice(options)
        _knock_down(walls, current, neighbour, direction)
        visited.add(neighbour)
        if neighbour[1] == height - 1:
            last_bottom = neighbour
        stack.append(neighbour)

    if exit_cell is None:
        assert last_bottom is not None
        exit_cell = last_bottom
    walls[exit_cell[0]][exit_cell[1]] &= ~WALL_BOTTOM
    return Maze(width=width, height=height, walls=walls, entry=entry, exit=exit_cell)


def _knock_down(
    walls: list[list[int]],
    a: tuple[int, int],
    b: tuple[int, int],
    direction: tuple[int, int],
) -> None:
    ac, ar = a
    bc, br = b
    if direction == EAST:
        walls[ac][ar] &= ~WALL_RIGHT
    elif direction == WEST:
        walls[bc][br] &= ~WALL_RIGHT
    elif direction == SOUTH:
        walls[ac][ar] &= ~WALL_BOTTOM
    else:  # NORTH
        walls[bc][br] &= ~WALL_BOTTOM


def shortest_path(maze: Maze) -> list[tuple[int, int]]:
    """BFS desde la entrada hasta la salida."""
    previous: dict[tuple[int, int], tuple[int, int]] = {}
    queue: deque[tuple[int, int]] = deque([maze.entry])
    visited: set[tuple[int, int]] = {maze.entry}
    while queue:
        current = queue.popleft()
        if current == maze.exit:
            break
        for direction in DIRECTIONS:
            if not maze.can_move(current, direction):
                continue
            target = (current[0] + direction[0], current[1] + direction[1])
            if not maze.in_bounds(target) or target in visited:
                continue
            visited.add(target)
            previous[target] = current
            queue.append(target)
    path = [maze.exit]
    while path[-1] != maze.entry:
        path.append(previous[path[-1]])
    path.reverse()
    return path


def render(
    maze: Maze,
    *,
    unicode_style: bool = False,
    trail: set[tuple[int, int]] | None = None,
) -> str:
    """Render ASCII estilo 1978 o Unicode."""
    if unicode_style:
        top_corner = bot_corner = closing = "+"
        horiz, vert, trail_glyph, exit_glyph = "──", "│", "·", "▲"
    else:
        top_corner = "."
        bot_corner = ":"
        closing = "."
        horiz, vert, trail_glyph, exit_glyph = "--", "I", "·", "^"

    trail = trail or set()
    lines: list[str] = []

    top_parts: list[str] = []
    for c in range(maze.width):
        top_parts.append(top_corner)
        top_parts.append("  " if c == maze.entry[0] else horiz)
    top_parts.append(top_corner)
    lines.append("".join(top_parts))

    for r in range(maze.height):
        side: list[str] = [vert]
        for c in range(maze.width):
            side.append(f" {trail_glyph}" if (c, r) in trail else "  ")
            side.append(vert if maze.walls[c][r] & WALL_RIGHT else " ")
        lines.append("".join(side))

        bot: list[str] = []
        for c in range(maze.width):
            bot.append(bot_corner)
            bot.append(horiz if maze.walls[c][r] & WALL_BOTTOM else "  ")
        bot.append(closing)
        lines.append("".join(bot))

    lines.append(" " * (1 + maze.exit[0] * 3 + 1) + exit_glyph)
    return "\n".join(lines)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="amazing.py",
        description=(
            "AMAZING — generador de laberintos (1978 Ahl / 2026 Python). Versión cero-dependencias."
        ),
    )
    p.add_argument("--width", "-W", type=int, default=12)
    p.add_argument("--height", "-H", type=int, default=8)
    p.add_argument("--seed", type=int, default=None, help="semilla reproducible")
    p.add_argument("--demo", action="store_true", help="resuelve con BFS y muestra el rastro")
    p.add_argument("--unicode", action="store_true", help="caracteres box-drawing")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        maze = carve(args.width, args.height, random.Random(args.seed))
    except ValueError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    print(" " * 28 + "AMAZING PROGRAM")
    print(" " * 15 + "CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY")
    print()
    trail: set[tuple[int, int]] | None = None
    if args.demo:
        trail = set(shortest_path(maze))
        print(f"Resuelto en {len(trail) - 1} pasos (seed={args.seed}).")
        print()
    print(render(maze, unicode_style=args.unicode, trail=trail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
