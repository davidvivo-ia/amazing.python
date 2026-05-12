"""Unit tests for :mod:`amazing.domain.maze`."""

from __future__ import annotations

import pytest

from amazing.domain import (
    Cell,
    Direction,
    InvalidDimensions,
    Maze,
    MazeBuilder,
    OutOfBounds,
    Wall,
    WallBlocksMovement,
)


def _open_corridor(width: int, height: int) -> Maze:
    """Build a maze where every internal wall is knocked down (open box)."""
    builder = MazeBuilder(width, height)
    for col in range(width):
        for row in range(height):
            if col + 1 < width:
                builder.carve_between(Cell(col, row), Cell(col + 1, row))
            if row + 1 < height:
                builder.carve_between(Cell(col, row), Cell(col, row + 1))
    builder.set_entry(Cell(0, 0))
    builder.set_exit(Cell(width - 1, height - 1))
    return builder.build()


# ---------------------------------------------------------------- validation
@pytest.mark.parametrize(
    ("width", "height"),
    [(0, 5), (5, 0), (-1, 3), (1, 1)],
)
def test_invalid_dimensions_rejected(width: int, height: int) -> None:
    with pytest.raises(InvalidDimensions):
        MazeBuilder(width, height)


@pytest.mark.parametrize(("width", "height"), [(1, 5), (5, 1)])
def test_one_by_n_corridors_are_allowed(width: int, height: int) -> None:
    # The original BASIC line 102 rejected these because of an AND/OR bug.
    builder = MazeBuilder(width, height)
    for col in range(width):
        for row in range(height):
            if col + 1 < width:
                builder.carve_between(Cell(col, row), Cell(col + 1, row))
            if row + 1 < height:
                builder.carve_between(Cell(col, row), Cell(col, row + 1))
    builder.set_entry(Cell(0, 0))
    builder.set_exit(Cell(width - 1, height - 1))
    maze = builder.build()
    assert maze.width == width
    assert maze.height == height


# ---------------------------------------------------------------- builder
def test_set_entry_outside_top_row_is_rejected() -> None:
    builder = MazeBuilder(3, 3)
    with pytest.raises(OutOfBounds):
        builder.set_entry(Cell(1, 1))


def test_set_exit_outside_bottom_row_is_rejected() -> None:
    builder = MazeBuilder(3, 3)
    with pytest.raises(OutOfBounds):
        builder.set_exit(Cell(1, 1))


def test_build_requires_entry_and_exit() -> None:
    builder = MazeBuilder(3, 3)
    with pytest.raises(ValueError, match="entry and exit"):
        builder.build()


def test_carve_between_rejects_non_neighbours() -> None:
    builder = MazeBuilder(3, 3)
    with pytest.raises(ValueError, match="orthogonal"):
        builder.carve_between(Cell(0, 0), Cell(2, 2))


def test_carve_between_rejects_out_of_bounds() -> None:
    builder = MazeBuilder(3, 3)
    with pytest.raises(OutOfBounds):
        builder.carve_between(Cell(0, 0), Cell(-1, 0))


def test_exit_bottom_wall_is_open_after_build() -> None:
    maze = _open_corridor(3, 3)
    assert Wall.BOTTOM not in maze.wall_at(maze.exit)


# ---------------------------------------------------------------- movement
def test_movement_through_open_corridor() -> None:
    maze = _open_corridor(3, 3)
    assert maze.move(Cell(0, 0), Direction.EAST) == Cell(1, 0)
    assert maze.move(Cell(1, 1), Direction.NORTH) == Cell(1, 0)


def test_movement_blocked_by_wall() -> None:
    builder = MazeBuilder(3, 3)
    builder.set_entry(Cell(0, 0))
    builder.set_exit(Cell(0, 2))
    maze = builder.build()
    with pytest.raises(WallBlocksMovement):
        maze.move(Cell(1, 1), Direction.EAST)


def test_exit_through_perimeter_only_at_exit_cell() -> None:
    maze = _open_corridor(3, 3)
    # Going south from the exit cell is allowed (off the bottom edge).
    assert maze.can_move(maze.exit, Direction.SOUTH) is True
    # Going south from any other bottom-row cell is blocked.
    blocked = Cell((maze.exit.col + 1) % maze.width, maze.height - 1)
    assert maze.can_move(blocked, Direction.SOUTH) is False


def test_can_move_out_of_bounds_raises() -> None:
    maze = _open_corridor(3, 3)
    with pytest.raises(OutOfBounds):
        maze.can_move(Cell(99, 99), Direction.NORTH)


def test_wall_at_out_of_bounds_raises() -> None:
    maze = _open_corridor(3, 3)
    with pytest.raises(OutOfBounds):
        maze.wall_at(Cell(99, 0))


def test_neighbours_yields_only_open_directions() -> None:
    builder = MazeBuilder(3, 3)
    builder.carve_between(Cell(0, 0), Cell(1, 0))
    builder.set_entry(Cell(0, 0))
    builder.set_exit(Cell(0, 2))
    maze = builder.build()
    neighbours = dict(maze.neighbours(Cell(0, 0)))
    assert neighbours == {Direction.EAST: Cell(1, 0)}


def test_cells_iterates_in_row_major_order() -> None:
    maze = _open_corridor(2, 2)
    assert list(maze.cells()) == [Cell(0, 0), Cell(1, 0), Cell(0, 1), Cell(1, 1)]


# ---------------------------------------------------------------- frozen
def test_maze_is_hashable_and_frozen() -> None:
    maze = _open_corridor(2, 2)
    with pytest.raises(AttributeError):
        maze.width = 99  # type: ignore[misc]
    assert hash(maze) == hash(maze)
