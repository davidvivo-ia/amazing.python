"""Unit tests for :class:`amazing.application.PlaySession`."""

from __future__ import annotations

from amazing.application import PlaySession, SessionStatus, carve, shortest_path
from amazing.domain import Cell, Direction
from amazing.infrastructure import StdlibRng


def test_initial_state() -> None:
    maze = carve(width=5, height=5, rng=StdlibRng(0))
    session = PlaySession(maze)
    assert session.player == maze.entry
    assert session.moves == 0
    assert session.status is SessionStatus.PLAYING
    assert maze.entry in session.visited


def test_blocked_move_returns_false_and_does_not_advance() -> None:
    maze = carve(width=4, height=4, rng=StdlibRng(0))
    session = PlaySession(maze)
    # Find at least one blocked direction from the entry.
    blocked: Direction | None = None
    for direction in Direction:
        if not maze.can_move(maze.entry, direction):
            blocked = direction
            break
    assert blocked is not None, "the entry should have at least one wall"
    assert session.try_move(blocked) is False
    assert session.moves == 0


def test_following_shortest_path_wins() -> None:
    maze = carve(width=6, height=5, rng=StdlibRng(123))
    path = shortest_path(maze)
    session = PlaySession(maze)
    for current, nxt in zip(path, path[1:], strict=False):
        direction = _direction_between(current, nxt)
        assert session.try_move(direction) is True
    # Final step: south through the exit.
    assert session.player == maze.exit
    assert session.try_move(Direction.SOUTH) is True
    assert session.status is SessionStatus.WON
    assert session.moves == len(path)


def test_cannot_move_after_winning() -> None:
    maze = carve(width=4, height=4, rng=StdlibRng(0))
    path = shortest_path(maze)
    session = PlaySession(maze)
    for current, nxt in zip(path, path[1:], strict=False):
        session.try_move(_direction_between(current, nxt))
    session.try_move(Direction.SOUTH)  # win
    assert session.try_move(Direction.NORTH) is False


def test_reset_restores_initial_state() -> None:
    maze = carve(width=4, height=4, rng=StdlibRng(0))
    session = PlaySession(maze)
    for direction in Direction:
        session.try_move(direction)
    session.reset()
    assert session.player == maze.entry
    assert session.moves == 0
    assert session.status is SessionStatus.PLAYING


def test_snapshot_is_immutable_view() -> None:
    maze = carve(width=3, height=3, rng=StdlibRng(0))
    session = PlaySession(maze)
    snap = session.snapshot()
    for direction in Direction:
        if session.try_move(direction):
            break
    # Old snapshot should not change after moves.
    assert snap.moves == 0
    assert snap.player == maze.entry


def _direction_between(a: Cell, b: Cell) -> Direction:
    delta = (b.col - a.col, b.row - a.row)
    for direction in Direction:
        if (direction.dcol, direction.drow) == delta:
            return direction
    raise AssertionError(f"non-adjacent cells {a!r} -> {b!r}")
