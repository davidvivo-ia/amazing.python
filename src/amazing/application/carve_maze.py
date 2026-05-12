"""Maze carving algorithm.

Provides a modern iterative recursive-backtracker. Produces a perfect
maze (exactly one path between any two cells) with a single entrance on
the top row and a single exit on the bottom row.

The 1978 BASIC original used a hunt-and-kill variant with a row-major
scan that introduced a directional bias. We preserved its *intent* (a
perfect maze with top-edge entry and bottom-edge exit) but used a
standard backtracker for cleaner statistical properties. See
``docs/original_program_analysis.md`` §2.5 for the rationale and
``TODO.md`` for the optional ``--legacy-bias`` mode planned for v1.1.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from amazing.domain import Cell, Direction, MazeBuilder

if TYPE_CHECKING:
    from amazing.application.rng import Rng
    from amazing.domain import Maze


class CarveAlgorithm(StrEnum):
    """Available maze generation strategies."""

    BACKTRACKER = "backtracker"


def carve(
    width: int,
    height: int,
    rng: Rng,
    algorithm: CarveAlgorithm = CarveAlgorithm.BACKTRACKER,
) -> Maze:
    """Generate a perfect maze of ``width × height`` cells.

    Args:
        width: Number of columns.
        height: Number of rows.
        rng: Random source (see :class:`amazing.application.rng.Rng`).
        algorithm: Reserved for future strategies. Currently only
            :attr:`CarveAlgorithm.BACKTRACKER` is implemented.

    Returns:
        A frozen :class:`amazing.domain.Maze`.
    """
    del algorithm  # only one strategy for now; kept in the signature for v1.1
    builder = MazeBuilder(width=width, height=height)
    entry = Cell(col=rng.randrange(0, width), row=0)
    builder.set_entry(entry)

    exit_cell = _carve_with_backtracker(builder, entry, rng)
    builder.set_exit(exit_cell)
    return builder.build()


def _carve_with_backtracker(builder: MazeBuilder, entry: Cell, rng: Rng) -> Cell:
    """Iterative depth-first backtracker.

    Returns the first cell on the bottom row from which the algorithm
    has to backtrack (a natural dead end). Falls back to the last
    visited bottom-row cell when no such dead end exists, guaranteeing
    that every maze has an exit on the bottom edge.
    """
    visited: set[Cell] = {entry}
    stack: list[Cell] = [entry]
    exit_candidate: Cell | None = None
    last_bottom_visit: Cell | None = entry if entry.row == builder.height - 1 else None

    while stack:
        current = stack[-1]
        unvisited: list[tuple[Direction, Cell]] = []
        for direction in Direction:
            neighbour = current.shifted(direction.dcol, direction.drow)
            if builder.contains(neighbour) and neighbour not in visited:
                unvisited.append((direction, neighbour))

        if not unvisited:
            if exit_candidate is None and current.row == builder.height - 1:
                exit_candidate = current
            stack.pop()
            continue

        _, neighbour = rng.choice(unvisited)
        builder.carve_between(current, neighbour)
        visited.add(neighbour)
        if neighbour.row == builder.height - 1:
            last_bottom_visit = neighbour
        stack.append(neighbour)

    if exit_candidate is not None:
        return exit_candidate
    assert last_bottom_visit is not None, "every maze has at least one bottom-row cell"
    return last_bottom_visit
