"""Cardinal directions for maze movement."""

from __future__ import annotations

from enum import Enum


class Direction(Enum):
    """Cardinal direction with its grid delta and a short label.

    The deltas use ``(dcol, drow)`` convention: rows grow downward, so
    ``SOUTH`` increments ``row``.
    """

    NORTH = (0, -1)
    SOUTH = (0, 1)
    WEST = (-1, 0)
    EAST = (1, 0)

    @property
    def dcol(self) -> int:
        """Return the column delta."""
        return self.value[0]

    @property
    def drow(self) -> int:
        """Return the row delta."""
        return self.value[1]

    @property
    def opposite(self) -> Direction:
        """Return the direction pointing the opposite way."""
        match self:
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.SOUTH:
                return Direction.NORTH
            case Direction.WEST:
                return Direction.EAST
            case Direction.EAST:
                return Direction.WEST
