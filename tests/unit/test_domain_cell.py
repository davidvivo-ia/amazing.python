"""Unit tests for :mod:`amazing.domain.cell`."""

from __future__ import annotations

import pytest

from amazing.domain import Cell


def test_cell_is_immutable() -> None:
    cell = Cell(3, 5)
    with pytest.raises(AttributeError):
        cell.col = 10  # type: ignore[misc]


def test_shifted_returns_offset_cell() -> None:
    assert Cell(2, 3).shifted(1, -1) == Cell(3, 2)


def test_shifted_does_not_clamp_to_zero() -> None:
    assert Cell(0, 0).shifted(-1, -1) == Cell(-1, -1)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (Cell(0, 0), Cell(0, 0), 0),
        (Cell(0, 0), Cell(3, 4), 7),
        (Cell(5, 5), Cell(2, 8), 6),
    ],
)
def test_manhattan_distance(a: Cell, b: Cell, expected: int) -> None:
    assert a.manhattan_to(b) == expected
    assert b.manhattan_to(a) == expected


def test_cell_is_hashable() -> None:
    seen = {Cell(1, 2), Cell(1, 2), Cell(2, 1)}
    assert len(seen) == 2
