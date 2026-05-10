"""AMAZING — a Python port of the 1978 BASIC maze generator.

Original: David H. Ahl, *BASIC Computer Games* (Creative Computing, 1978),
preserved at https://github.com/GReaperEx/bcg/blob/master/amazing.bas

The original is a tangle of line numbers, GOTOs, and ON ... GOTO dispatch
tables. This port keeps the same behaviour (a rectangular maze with a single
entrance on the top edge and a single exit on the bottom edge) but rewrites
it with modern Python idioms: type hints, dataclasses, an IntFlag for wall
state, a clean iterative recursive-backtracker, argparse, and a seeded RNG
for reproducible mazes.
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass, field
from enum import IntFlag
from typing import Iterator


class Wall(IntFlag):
    """Walls still standing on a cell's right and bottom edges.

    Each cell only tracks two of its four walls; the other two belong to its
    neighbours. The outer border is implicit.
    """

    NONE = 0
    RIGHT = 1
    BOTTOM = 2
    BOTH = RIGHT | BOTTOM


@dataclass(frozen=True)
class Cell:
    col: int
    row: int

    def shifted(self, dc: int, dr: int) -> "Cell":
        return Cell(self.col + dc, self.row + dr)


@dataclass
class Maze:
    width: int
    height: int
    rng: random.Random = field(default_factory=random.Random)
    walls: list[list[Wall]] = field(init=False)
    _visited: list[list[bool]] = field(init=False, repr=False)
    entry_col: int = field(init=False)
    exit_col: int = field(init=False)

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise ValueError("width and height must be >= 1")
        if self.width == 1 and self.height == 1:
            raise ValueError("meaningless dimensions — try larger numbers")
        self.walls = [[Wall.BOTH] * self.height for _ in range(self.width)]
        self._visited = [[False] * self.height for _ in range(self.width)]
        self.entry_col = self.rng.randrange(self.width)
        self.exit_col = -1

    # -------------------------------------------------------------- carving
    def carve(self) -> None:
        """Generate the maze with an iterative depth-first backtracker."""
        start = Cell(self.entry_col, 0)
        self._visited[start.col][start.row] = True
        stack: list[Cell] = [start]

        while stack:
            cell = stack[-1]
            options = list(self._unvisited_neighbours(cell))
            if not options:
                # Punch the exit the first time we backtrack from the bottom row,
                # mirroring the original program's behaviour.
                if self.exit_col < 0 and cell.row == self.height - 1:
                    self.exit_col = cell.col
                    self.walls[cell.col][cell.row] &= ~Wall.BOTTOM
                stack.pop()
                continue
            nxt = self.rng.choice(options)
            self._knock_down_wall(cell, nxt)
            self._visited[nxt.col][nxt.row] = True
            stack.append(nxt)

        if self.exit_col < 0:
            # Degenerate case (e.g. height == 1): exit beneath the last cell.
            self.exit_col = self.width - 1
            self.walls[self.exit_col][self.height - 1] &= ~Wall.BOTTOM

    def _unvisited_neighbours(self, cell: Cell) -> Iterator[Cell]:
        for dc, dr in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            n = cell.shifted(dc, dr)
            if 0 <= n.col < self.width and 0 <= n.row < self.height:
                if not self._visited[n.col][n.row]:
                    yield n

    def _knock_down_wall(self, a: Cell, b: Cell) -> None:
        if b.col == a.col + 1:        # b is to the right of a
            self.walls[a.col][a.row] &= ~Wall.RIGHT
        elif b.col == a.col - 1:      # b is to the left of a
            self.walls[b.col][b.row] &= ~Wall.RIGHT
        elif b.row == a.row + 1:      # b is below a
            self.walls[a.col][a.row] &= ~Wall.BOTTOM
        elif b.row == a.row - 1:      # b is above a
            self.walls[b.col][b.row] &= ~Wall.BOTTOM

    # -------------------------------------------------------------- render
    def render(self, *, unicode: bool = False) -> str:
        """Return the maze as a printable multi-line string.

        The ASCII layout reproduces the original BASIC output character for
        character. The Unicode variant uses box-drawing characters for a
        nicer modern look.
        """
        if unicode:
            top_corner = bot_corner = "+"
            horiz, vert, gap_h, gap_v = "──", "│", "  ", " "
        else:
            top_corner, bot_corner = ".", ":"
            horiz, vert, gap_h, gap_v = "--", "I", "  ", " "

        lines: list[str] = []

        # Top edge with the entry gap.
        top = "".join(
            top_corner + (gap_h if c == self.entry_col else horiz)
            for c in range(self.width)
        ) + top_corner
        lines.append(top)

        for r in range(self.height):
            # Vertical walls within the row (left border is always solid).
            side = vert
            for c in range(self.width):
                side += "  "
                side += vert if self.walls[c][r] & Wall.RIGHT else gap_v
            lines.append(side)

            # Horizontal walls below the row.
            below = "".join(
                bot_corner
                + (horiz if self.walls[c][r] & Wall.BOTTOM else gap_h)
                for c in range(self.width)
            )
            # Closing corner — "." in classic mode to mirror the original.
            below += "." if not unicode else bot_corner
            lines.append(below)

        return "\n".join(lines)


# ------------------------------------------------------------------------ CLI
def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="amazing",
        description="Generate a random rectangular maze (Ahl 1978, in Python).",
    )
    p.add_argument("-W", "--width", type=int, help="maze width (columns)")
    p.add_argument("-H", "--height", type=int, help="maze height (rows)")
    p.add_argument("--seed", type=int, help="seed for reproducible output")
    p.add_argument(
        "--unicode",
        action="store_true",
        help="render with Unicode box-drawing characters",
    )
    return p.parse_args(argv)


def _prompt_dimensions() -> tuple[int, int]:
    while True:
        try:
            raw = input("What are your width and length? ")
        except EOFError:
            sys.exit(0)
        parts = raw.replace(",", " ").split()
        try:
            w, h = int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            print("Please enter two positive integers, e.g. '10 10'.")
            continue
        if w < 1 or h < 1 or (w == 1 and h == 1):
            print("Meaningless dimensions.  Try again.")
            continue
        return w, h


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.width is None or args.height is None:
        print(" " * 28 + "AMAZING PROGRAM")
        print(" " * 15 + "CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY")
        print("\n\n")
        width, height = _prompt_dimensions()
    else:
        width, height = args.width, args.height

    try:
        maze = Maze(width, height, rng=random.Random(args.seed))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    maze.carve()
    print()
    print(maze.render(unicode=args.unicode))
    return 0


if __name__ == "__main__":
    sys.exit(main())
