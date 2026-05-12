"""BFS solver used by the ``--demo`` mode and as a property-test oracle."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from amazing.domain import Cell, Direction

if TYPE_CHECKING:
    from amazing.domain import Maze


def shortest_path(maze: Maze) -> list[Cell]:
    """Return the shortest cell-by-cell path from entry to exit.

    The returned list always starts at :attr:`Maze.entry` and ends at
    :attr:`Maze.exit`. In a perfect maze (which is what
    :func:`amazing.application.carve_maze.carve` produces) the BFS path
    is also the only path.

    Raises:
        RuntimeError: if no path exists. This should never happen for a
            maze produced by our carver; the check is defensive.
    """
    start = maze.entry
    goal = maze.exit
    previous: dict[Cell, Cell] = {}
    queue: deque[Cell] = deque([start])
    visited: set[Cell] = {start}

    while queue:
        current = queue.popleft()
        if current == goal:
            return _reconstruct(previous, start, goal)
        for direction in Direction:
            if not maze.can_move(current, direction):
                continue
            neighbour = current.shifted(direction.dcol, direction.drow)
            if not maze.contains(neighbour) or neighbour in visited:
                continue
            visited.add(neighbour)
            previous[neighbour] = current
            queue.append(neighbour)

    raise RuntimeError("maze is disconnected — entry cannot reach exit")


def _reconstruct(previous: dict[Cell, Cell], start: Cell, goal: Cell) -> list[Cell]:
    path = [goal]
    cursor = goal
    while cursor != start:
        cursor = previous[cursor]
        path.append(cursor)
    path.reverse()
    return path
