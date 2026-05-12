"""Immutable :class:`Maze` and its mutable :class:`MazeBuilder` counterpart.

The :class:`Maze` is what flows through the application: a frozen
snapshot with bounds, an immutable wall map, and the entry/exit cells.
The :class:`MazeBuilder` is the carving-time scratch space used by
algorithms in :mod:`amazing.application.carve_maze`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from amazing.domain.cell import Cell
from amazing.domain.direction import Direction
from amazing.domain.errors import InvalidDimensions, OutOfBounds, WallBlocksMovement
from amazing.domain.walls import Wall

if TYPE_CHECKING:
    from collections.abc import Iterator


def _validate_dimensions(width: int, height: int) -> None:
    """Reject the same degenerate combinations as the 1978 original.

    The original BASIC line 102 had a logic bug (``AND`` instead of
    ``OR``) that also rejected ``1xN`` corridors. We accept those; the
    only forbidden configuration is the trivial ``1x1`` "maze".
    """
    if width < 1 or height < 1:
        raise InvalidDimensions(width, height)
    if width == 1 and height == 1:
        raise InvalidDimensions(width, height)


@dataclass(frozen=True, slots=True)
class Maze:
    """A fully-carved maze ready for navigation or rendering.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        walls: Walls indexed as ``walls[col][row]``; each cell tracks
            its right and bottom edges.
        entry: Cell on the top row where the player starts. The wall
            above this cell is implicitly open.
        exit: Cell on the bottom row whose bottom wall is open. Reaching
            it ends the game.
    """

    width: int
    height: int
    walls: tuple[tuple[Wall, ...], ...]
    entry: Cell
    exit: Cell

    def __post_init__(self) -> None:
        _validate_dimensions(self.width, self.height)
        if len(self.walls) != self.width:
            raise InvalidDimensions(self.width, self.height)
        for column in self.walls:
            if len(column) != self.height:
                raise InvalidDimensions(self.width, self.height)
        if not self.contains(self.entry) or self.entry.row != 0:
            raise OutOfBounds(self.entry, self.width, self.height)
        if not self.contains(self.exit) or self.exit.row != self.height - 1:
            raise OutOfBounds(self.exit, self.width, self.height)

    # ------------------------------------------------------------- queries
    def contains(self, cell: Cell) -> bool:
        """Return ``True`` when ``cell`` lies inside this maze."""
        return 0 <= cell.col < self.width and 0 <= cell.row < self.height

    def wall_at(self, cell: Cell) -> Wall:
        """Return the walls still standing on ``cell``."""
        if not self.contains(cell):
            raise OutOfBounds(cell, self.width, self.height)
        return self.walls[cell.col][cell.row]

    def can_move(self, source: Cell, direction: Direction) -> bool:
        """Return ``True`` when ``direction`` is unobstructed from ``source``.

        Moving outside the perimeter is forbidden everywhere except
        through the entry (going north from the top row at the entry
        column) and through the exit (going south from the bottom row at
        the exit column).
        """
        if not self.contains(source):
            raise OutOfBounds(source, self.width, self.height)
        target = source.shifted(direction.dcol, direction.drow)
        if not self.contains(target):
            return self._can_exit_perimeter(source, direction)
        return self._wall_between_is_open(source, target, direction)

    def neighbours(self, source: Cell) -> Iterator[tuple[Direction, Cell]]:
        """Yield ``(direction, neighbour)`` for every reachable adjacent cell."""
        for direction in Direction:
            if self.can_move(source, direction):
                target = source.shifted(direction.dcol, direction.drow)
                if self.contains(target):
                    yield direction, target

    def move(self, source: Cell, direction: Direction) -> Cell:
        """Return the destination cell after moving ``direction`` from ``source``.

        Raises :class:`WallBlocksMovement` when the move is blocked.
        """
        if not self.can_move(source, direction):
            raise WallBlocksMovement(source, direction)
        return source.shifted(direction.dcol, direction.drow)

    # -------------------------------------------------------- iteration
    def cells(self) -> Iterator[Cell]:
        """Yield every cell in row-major order."""
        for row in range(self.height):
            for col in range(self.width):
                yield Cell(col, row)

    # ----------------------------------------------------------- helpers
    def _can_exit_perimeter(self, source: Cell, direction: Direction) -> bool:
        if direction is Direction.NORTH:
            return source == self.entry and source.row == 0
        if direction is Direction.SOUTH:
            return source == self.exit and source.row == self.height - 1
        return False

    def _wall_between_is_open(
        self,
        source: Cell,
        target: Cell,
        direction: Direction,
    ) -> bool:
        match direction:
            case Direction.EAST:
                return Wall.RIGHT not in self.walls[source.col][source.row]
            case Direction.WEST:
                return Wall.RIGHT not in self.walls[target.col][target.row]
            case Direction.SOUTH:
                return Wall.BOTTOM not in self.walls[source.col][source.row]
            case Direction.NORTH:
                return Wall.BOTTOM not in self.walls[target.col][target.row]


@dataclass(slots=True)
class MazeBuilder:
    """Mutable scratch space used while carving a maze.

    The builder starts with every wall standing and exposes operations
    to knock walls down. :meth:`build` freezes it into an immutable
    :class:`Maze`.
    """

    width: int
    height: int
    _walls: list[list[Wall]] = field(init=False, repr=False)
    _entry: Cell | None = field(init=False, default=None, repr=False)
    _exit: Cell | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        _validate_dimensions(self.width, self.height)
        self._walls = [[Wall.BOTH for _ in range(self.height)] for _ in range(self.width)]

    # --------------------------------------------------------- mutators
    def set_entry(self, cell: Cell) -> None:
        """Mark ``cell`` (which must lie on the top row) as the maze entry."""
        if not self._contains(cell) or cell.row != 0:
            raise OutOfBounds(cell, self.width, self.height)
        self._entry = cell

    def set_exit(self, cell: Cell) -> None:
        """Mark ``cell`` (which must lie on the bottom row) as the maze exit.

        Knocks down the cell's bottom wall as a side effect.
        """
        if not self._contains(cell) or cell.row != self.height - 1:
            raise OutOfBounds(cell, self.width, self.height)
        self._exit = cell
        self._walls[cell.col][cell.row] &= ~Wall.BOTTOM

    def carve_between(self, a: Cell, b: Cell) -> None:
        """Knock down the wall between two orthogonally adjacent cells."""
        if not self._contains(a) or not self._contains(b):
            offender = a if not self._contains(a) else b
            raise OutOfBounds(offender, self.width, self.height)
        if a.col == b.col + 1 and a.row == b.row:
            self._walls[b.col][b.row] &= ~Wall.RIGHT
        elif b.col == a.col + 1 and a.row == b.row:
            self._walls[a.col][a.row] &= ~Wall.RIGHT
        elif a.row == b.row + 1 and a.col == b.col:
            self._walls[b.col][b.row] &= ~Wall.BOTTOM
        elif b.row == a.row + 1 and a.col == b.col:
            self._walls[a.col][a.row] &= ~Wall.BOTTOM
        else:
            raise ValueError(f"cells {a!r} and {b!r} are not orthogonal neighbours")

    # --------------------------------------------------------- accessors
    def contains(self, cell: Cell) -> bool:
        """Return ``True`` when ``cell`` is inside this builder."""
        return self._contains(cell)

    def wall_at(self, cell: Cell) -> Wall:
        """Return the current walls of ``cell`` mid-carve."""
        if not self._contains(cell):
            raise OutOfBounds(cell, self.width, self.height)
        return self._walls[cell.col][cell.row]

    # ----------------------------------------------------------- freeze
    def build(self) -> Maze:
        """Freeze the builder into an immutable :class:`Maze`.

        Both entry and exit must have been set beforehand. The bottom
        wall of the exit cell is guaranteed to be open at this point.
        """
        if self._entry is None or self._exit is None:
            raise ValueError("entry and exit must be set before building")
        frozen = tuple(tuple(column) for column in self._walls)
        return Maze(
            width=self.width,
            height=self.height,
            walls=frozen,
            entry=self._entry,
            exit=self._exit,
        )

    # ----------------------------------------------------------- private
    def _contains(self, cell: Cell) -> bool:
        return 0 <= cell.col < self.width and 0 <= cell.row < self.height
