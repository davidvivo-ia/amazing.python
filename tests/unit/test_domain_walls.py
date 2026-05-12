"""Unit tests for :mod:`amazing.domain.walls`."""

from __future__ import annotations

from amazing.domain import Wall


def test_legacy_integer_compatibility() -> None:
    # The 1978 listing used integers 0..3 with the same bit layout.
    assert int(Wall.NONE) == 0
    assert int(Wall.BOTTOM) == 2
    assert int(Wall.RIGHT) == 1
    assert int(Wall.BOTH) == 3


def test_bitwise_composition() -> None:
    combined = Wall.RIGHT | Wall.BOTTOM
    assert combined is Wall.BOTH
    assert Wall.RIGHT in combined
    assert Wall.BOTTOM in combined


def test_membership_after_clearing() -> None:
    walls = Wall.BOTH & ~Wall.RIGHT
    assert Wall.RIGHT not in walls
    assert Wall.BOTTOM in walls
