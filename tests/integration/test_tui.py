"""End-to-end tests for the Textual TUI using ``App.run_test``."""

from __future__ import annotations

import pytest

from amazing.application import SessionStatus, carve, shortest_path
from amazing.domain import Cell, Direction
from amazing.infrastructure import StdlibRng
from amazing.presentation.tui import AmazingApp


def _direction_between(a: Cell, b: Cell) -> Direction:
    delta = (b.col - a.col, b.row - a.row)
    for direction in Direction:
        if (direction.dcol, direction.drow) == delta:
            return direction
    raise AssertionError("non-adjacent")


_KEY_FOR: dict[Direction, str] = {
    Direction.NORTH: "up",
    Direction.SOUTH: "down",
    Direction.WEST: "left",
    Direction.EAST: "right",
}


@pytest.mark.asyncio
async def test_app_walks_the_shortest_path_and_wins() -> None:
    maze = carve(width=4, height=4, rng=StdlibRng(0))
    path = shortest_path(maze)
    app = AmazingApp(maze=maze)
    async with app.run_test() as pilot:
        for current, nxt in zip(path, path[1:], strict=False):
            await pilot.press(_KEY_FOR[_direction_between(current, nxt)])
        await pilot.press(_KEY_FOR[Direction.SOUTH])  # walk through the exit
        # pylint: disable=protected-access
        assert app._session.status is SessionStatus.WON


@pytest.mark.asyncio
async def test_app_reset_action_returns_to_entry() -> None:
    maze = carve(width=5, height=5, rng=StdlibRng(1))
    app = AmazingApp(maze=maze)
    async with app.run_test() as pilot:
        await pilot.press("right")
        await pilot.press("down")
        await pilot.press("r")
        assert app._session.player == maze.entry
        assert app._session.moves == 0


@pytest.mark.asyncio
async def test_theme_cycle_does_not_crash() -> None:
    maze = carve(width=4, height=4, rng=StdlibRng(2))
    app = AmazingApp(maze=maze)
    async with app.run_test() as pilot:
        for _ in range(4):
            await pilot.press("t")
