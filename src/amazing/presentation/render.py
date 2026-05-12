"""ASCII / Unicode rendering of a maze.

The legacy style reproduces the 1978 listing character for character
(``.``, ``--``, ``:``, ``I``). The Unicode style uses box-drawing
glyphs for a nicer modern look. Both can decorate the maze with the
player position and visited trail used by the TUI and demo modes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from amazing.domain import Cell, Wall

if TYPE_CHECKING:
    from amazing.domain import Maze


class RenderStyle(StrEnum):
    """Character set used by :func:`render_maze`."""

    LEGACY = "legacy"
    UNICODE = "unicode"


@dataclass(frozen=True, slots=True)
class _Charset:
    top_corner: str
    bot_corner: str
    horiz: str
    vert: str
    gap_h: str
    gap_v: str
    player: str
    trail: str
    entry_mark: str
    exit_mark: str
    closing_bot_corner: str


_LEGACY = _Charset(
    top_corner=".",
    bot_corner=":",
    horiz="--",
    vert="I",
    gap_h="  ",
    gap_v=" ",
    player="*",
    trail="·",
    entry_mark="v",
    exit_mark="^",
    closing_bot_corner=".",
)

_UNICODE = _Charset(
    top_corner="+",
    bot_corner="+",
    horiz="──",
    vert="│",
    gap_h="  ",
    gap_v=" ",
    player="◉",
    trail="·",
    entry_mark="▼",
    exit_mark="▲",
    closing_bot_corner="+",
)


def render_maze(
    maze: Maze,
    *,
    style: RenderStyle = RenderStyle.LEGACY,
    player: Cell | None = None,
    trail: frozenset[Cell] = frozenset(),
    show_exit_arrow: bool = False,
) -> str:
    """Return the maze rendered as a multi-line string.

    Args:
        maze: Maze to render.
        style: Character set to use.
        player: If given, the cell is marked with the player glyph.
        trail: Cells previously visited that should be marked as a fading
            trail. ``player`` overrides ``trail`` on a per-cell basis.
        show_exit_arrow: Append a small arrow pointing at the exit below
            the maze.

    Returns:
        A string with embedded newlines, ready to ``print`` or write to
        a Textual widget.
    """
    charset = _LEGACY if style is RenderStyle.LEGACY else _UNICODE
    lines: list[str] = [_render_top(maze, charset)]

    for row in range(maze.height):
        lines.append(_render_row_sides(maze, row, charset, player, trail))
        lines.append(_render_row_bottom(maze, row, charset))

    if show_exit_arrow:
        lines.append(_render_exit_arrow(maze, charset))

    return "\n".join(lines)


# --------------------------------------------------------------- internals
def _render_top(maze: Maze, charset: _Charset) -> str:
    pieces: list[str] = []
    for col in range(maze.width):
        pieces.append(charset.top_corner)
        pieces.append(charset.gap_h if col == maze.entry.col else charset.horiz)
    pieces.append(charset.top_corner)
    return "".join(pieces)


def _render_row_sides(
    maze: Maze,
    row: int,
    charset: _Charset,
    player: Cell | None,
    trail: frozenset[Cell],
) -> str:
    pieces: list[str] = [charset.vert]
    for col in range(maze.width):
        cell = Cell(col, row)
        if player is not None and cell == player:
            pieces.append(f" {charset.player}")
        elif cell in trail:
            pieces.append(f" {charset.trail}")
        else:
            pieces.append("  ")
        walls = maze.wall_at(cell)
        pieces.append(charset.vert if Wall.RIGHT in walls else charset.gap_v)
    return "".join(pieces)


def _render_row_bottom(maze: Maze, row: int, charset: _Charset) -> str:
    pieces: list[str] = []
    for col in range(maze.width):
        pieces.append(charset.bot_corner)
        walls = maze.wall_at(Cell(col, row))
        pieces.append(charset.horiz if Wall.BOTTOM in walls else charset.gap_h)
    pieces.append(charset.closing_bot_corner)
    return "".join(pieces)


def _render_exit_arrow(maze: Maze, charset: _Charset) -> str:
    column_position = 1 + maze.exit.col * 3 + 1  # under the gap of the exit cell
    return " " * column_position + charset.exit_mark
