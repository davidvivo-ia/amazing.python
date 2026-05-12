"""Unit tests for :mod:`amazing.presentation.render`."""

from __future__ import annotations

import pytest

from amazing.application import carve
from amazing.domain import Cell
from amazing.infrastructure import StdlibRng
from amazing.presentation.render import RenderStyle, render_maze


@pytest.mark.parametrize("style", list(RenderStyle))
def test_render_starts_with_top_border(style: RenderStyle) -> None:
    maze = carve(width=5, height=3, rng=StdlibRng(0))
    lines = render_maze(maze, style=style).splitlines()
    # Top border is 1 char + 3 chars per cell + closing corner; legacy
    # uses "." and unicode uses "+" but length is the same.
    assert len(lines[0]) == 1 + maze.width * 3
    if style is RenderStyle.LEGACY:
        assert lines[0].startswith(".")
        assert lines[0].endswith(".")
    else:
        assert lines[0].startswith("+")
        assert lines[0].endswith("+")


def test_render_includes_player_marker() -> None:
    maze = carve(width=4, height=4, rng=StdlibRng(1))
    out = render_maze(maze, player=Cell(0, 0))
    assert "*" in out


def test_render_includes_trail_marker() -> None:
    maze = carve(width=4, height=4, rng=StdlibRng(1))
    out = render_maze(maze, trail=frozenset({Cell(0, 0), Cell(1, 0)}))
    assert "·" in out


def test_render_player_overrides_trail() -> None:
    maze = carve(width=3, height=3, rng=StdlibRng(0))
    out = render_maze(
        maze,
        player=Cell(0, 0),
        trail=frozenset({Cell(0, 0)}),  # same cell as player
    )
    # The player glyph appears, the trail glyph does not need to.
    assert "*" in out


def test_render_exit_arrow_appended() -> None:
    maze = carve(width=4, height=3, rng=StdlibRng(0))
    out = render_maze(maze, show_exit_arrow=True)
    assert out.splitlines()[-1].lstrip().startswith(("^", "▲"))


def test_render_total_lines() -> None:
    maze = carve(width=4, height=3, rng=StdlibRng(0))
    out = render_maze(maze)
    # 1 top + 2 per row = 1 + 2*height
    assert len(out.splitlines()) == 1 + 2 * maze.height
