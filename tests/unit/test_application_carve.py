"""Unit tests for :mod:`amazing.application.carve_maze`."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pytest

from amazing.application import carve, shortest_path
from amazing.application.rng import Rng
from amazing.domain import Cell, Direction
from amazing.infrastructure import StdlibRng

if TYPE_CHECKING:
    from collections.abc import Sequence


class _FixedRng:
    """A trivial RNG that always returns the first option."""

    def randrange(self, start: int, _stop: int) -> int:
        return start

    def choice[T](self, seq: Sequence[T]) -> T:
        return seq[0]


def test_rng_protocol_is_satisfied_by_stub() -> None:
    assert isinstance(_FixedRng(), Rng)


@pytest.mark.parametrize("seed", [0, 1, 42, 999, 12345])
def test_carved_maze_is_connected(seed: int) -> None:
    maze = carve(width=8, height=6, rng=StdlibRng(seed))
    assert maze.entry.row == 0
    assert maze.exit.row == maze.height - 1
    path = shortest_path(maze)
    assert path[0] == maze.entry
    assert path[-1] == maze.exit


@pytest.mark.parametrize("seed", [0, 1, 42, 999])
def test_carved_maze_visits_every_cell(seed: int) -> None:
    # In a perfect maze, BFS from entry must reach every cell.
    maze = carve(width=7, height=5, rng=StdlibRng(seed))
    reached: set[Cell] = {maze.entry}
    frontier = [maze.entry]
    while frontier:
        cell = frontier.pop()
        for direction in Direction:
            if not maze.can_move(cell, direction):
                continue
            neighbour = cell.shifted(direction.dcol, direction.drow)
            if maze.contains(neighbour) and neighbour not in reached:
                reached.add(neighbour)
                frontier.append(neighbour)
    assert len(reached) == maze.width * maze.height


def test_seed_is_deterministic() -> None:
    a = carve(width=10, height=8, rng=StdlibRng(2026))
    b = carve(width=10, height=8, rng=StdlibRng(2026))
    assert a == b


def test_different_seeds_produce_different_mazes() -> None:
    a = carve(width=10, height=8, rng=StdlibRng(1))
    b = carve(width=10, height=8, rng=StdlibRng(2))
    assert a != b


def test_one_by_n_corridor_carves_successfully() -> None:
    maze = carve(width=1, height=6, rng=StdlibRng(7))
    assert maze.entry == Cell(0, 0)
    assert maze.exit == Cell(0, 5)
    # In a 1-wide corridor every internal horizontal wall must be open.
    for row in range(maze.height - 1):
        assert maze.can_move(Cell(0, row), Direction.SOUTH)


def test_n_by_one_corridor_carves_successfully() -> None:
    maze = carve(width=6, height=1, rng=StdlibRng(7))
    assert maze.entry.row == 0
    assert maze.exit.row == 0
    for col in range(maze.width - 1):
        assert maze.can_move(Cell(col, 0), Direction.EAST)


def test_fixed_rng_path() -> None:
    # The fixed RNG always picks first option => deterministic shape.
    maze = carve(width=3, height=3, rng=_FixedRng())
    assert maze.entry == Cell(0, 0)
    # Exit must still lie on the bottom row.
    assert maze.exit.row == 2


def test_rng_can_be_passed_as_stdlib_random_wrapper() -> None:
    rng = random.Random(0)
    wrapper = StdlibRng.from_random(rng)
    maze = carve(width=4, height=4, rng=wrapper)
    assert maze.width == 4
