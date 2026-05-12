"""Hypothesis property tests: the carver must always produce a perfect maze."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from amazing.application import carve, shortest_path
from amazing.domain import Cell, Direction
from amazing.infrastructure import StdlibRng


def _is_perfect(maze: object) -> bool:  # local import only to keep deps tight
    from amazing.domain import Maze

    assert isinstance(maze, Maze)
    # BFS counts edges and verifies a unique tree structure.
    reached: set[Cell] = {maze.entry}
    edges = 0
    frontier = [maze.entry]
    while frontier:
        cell = frontier.pop()
        for direction in Direction:
            if not maze.can_move(cell, direction):
                continue
            neighbour = cell.shifted(direction.dcol, direction.drow)
            if not maze.contains(neighbour):
                continue
            if neighbour not in reached:
                reached.add(neighbour)
                edges += 1
                frontier.append(neighbour)
    cells = maze.width * maze.height
    return len(reached) == cells and edges == cells - 1


@given(
    width=st.integers(min_value=2, max_value=12),
    height=st.integers(min_value=2, max_value=12),
    seed=st.integers(min_value=0, max_value=10_000),
)
@settings(max_examples=80, deadline=None)
def test_carver_always_produces_a_perfect_maze(width: int, height: int, seed: int) -> None:
    maze = carve(width=width, height=height, rng=StdlibRng(seed))
    assert _is_perfect(maze)
    path = shortest_path(maze)
    assert path[0] == maze.entry
    assert path[-1] == maze.exit


@given(
    seed=st.integers(min_value=0, max_value=10_000),
)
@settings(max_examples=40, deadline=None)
def test_seed_determinism(seed: int) -> None:
    a = carve(width=7, height=5, rng=StdlibRng(seed))
    b = carve(width=7, height=5, rng=StdlibRng(seed))
    assert a == b
