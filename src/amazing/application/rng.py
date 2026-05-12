"""Random-number generator protocol used across the application layer.

Concrete implementations live in :mod:`amazing.infrastructure.rng`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class Rng(Protocol):
    """Minimal interface required by the maze-carving algorithms."""

    def randrange(self, start: int, stop: int) -> int:
        """Return a uniform random ``int`` in ``[start, stop)``."""

    def choice[T](self, seq: Sequence[T]) -> T:
        """Return a uniformly chosen element from ``seq``.

        ``seq`` must be non-empty.
        """
