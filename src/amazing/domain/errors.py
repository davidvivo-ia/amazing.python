"""Domain exceptions for AMAZING.

All errors raised by the pure domain inherit from :class:`AmazingError`
so the presentation layer can translate them to friendly user messages
with a single ``except`` clause.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amazing.domain.cell import Cell
    from amazing.domain.direction import Direction


class AmazingError(Exception):
    """Base class for all domain errors."""


class InvalidDimensions(AmazingError):
    """Raised when a maze is requested with non-positive or trivial dims."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        super().__init__(
            f"invalid maze dimensions: width={width}, height={height}; "
            "both must be >= 1 and not both equal to 1"
        )


class OutOfBounds(AmazingError):
    """Raised when a caller accesses a cell outside the maze."""

    def __init__(self, cell: Cell, width: int, height: int) -> None:
        self.cell = cell
        self.width = width
        self.height = height
        super().__init__(f"cell {cell!r} is out of bounds for a {width}x{height} maze")


class WallBlocksMovement(AmazingError):
    """Raised when a player tries to move through a standing wall."""

    def __init__(self, source: Cell, direction: Direction) -> None:
        self.source = source
        self.direction = direction
        super().__init__(f"a wall blocks movement {direction.name} from {source!r}")
