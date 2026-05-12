"""Unit tests for :mod:`amazing.domain.direction`."""

from __future__ import annotations

import pytest

from amazing.domain import Direction


@pytest.mark.parametrize(
    ("direction", "dcol", "drow"),
    [
        (Direction.NORTH, 0, -1),
        (Direction.SOUTH, 0, 1),
        (Direction.WEST, -1, 0),
        (Direction.EAST, 1, 0),
    ],
)
def test_deltas(direction: Direction, dcol: int, drow: int) -> None:
    assert direction.dcol == dcol
    assert direction.drow == drow


@pytest.mark.parametrize(
    ("direction", "opposite"),
    [
        (Direction.NORTH, Direction.SOUTH),
        (Direction.SOUTH, Direction.NORTH),
        (Direction.EAST, Direction.WEST),
        (Direction.WEST, Direction.EAST),
    ],
)
def test_opposite_is_symmetric(direction: Direction, opposite: Direction) -> None:
    assert direction.opposite is opposite
    assert opposite.opposite is direction
