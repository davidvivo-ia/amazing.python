"""Immutable cell coordinate inside a maze."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cell:
    """A position within a maze grid, indexed from zero.

    ``col`` runs along the horizontal axis (width / ``H`` in the
    original BASIC), ``row`` runs along the vertical axis (length /
    ``V``). Both are non-negative.
    """

    col: int
    row: int

    def shifted(self, dc: int, dr: int) -> Cell:
        """Return a new cell offset by ``(dc, dr)`` without bounds check."""
        return Cell(self.col + dc, self.row + dr)

    def manhattan_to(self, other: Cell) -> int:
        """Return the Manhattan distance to ``other``."""
        return abs(self.col - other.col) + abs(self.row - other.row)
