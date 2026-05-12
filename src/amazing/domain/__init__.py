"""Pure domain layer for AMAZING.

Contains immutable value objects and entities that model a maze. No I/O,
no randomness, no presentation. Everything here is trivially testable
and the lifeblood of the rest of the codebase.
"""

from amazing.domain.cell import Cell
from amazing.domain.direction import Direction
from amazing.domain.errors import (
    AmazingError,
    InvalidDimensions,
    OutOfBounds,
    WallBlocksMovement,
)
from amazing.domain.maze import Maze, MazeBuilder
from amazing.domain.walls import Wall

__all__ = [
    "AmazingError",
    "Cell",
    "Direction",
    "InvalidDimensions",
    "Maze",
    "MazeBuilder",
    "OutOfBounds",
    "Wall",
    "WallBlocksMovement",
]
