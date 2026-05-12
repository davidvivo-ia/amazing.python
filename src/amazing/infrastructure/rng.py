"""Concrete implementations of :class:`amazing.application.rng.Rng`."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(slots=True)
class StdlibRng:
    """Wrapper around :class:`random.Random` that fits :class:`Rng`."""

    seed: int | None = None
    _impl: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._impl = random.Random(self.seed)

    @classmethod
    def from_random(cls, source: random.Random) -> StdlibRng:
        """Wrap an existing :class:`random.Random` instance."""
        instance = cls.__new__(cls)
        # We bypass ``__init__`` so the caller-provided generator stays untouched.
        object.__setattr__(instance, "seed", None)
        object.__setattr__(instance, "_impl", source)
        return instance

    def randrange(self, start: int, stop: int) -> int:
        """Return a uniform random ``int`` in ``[start, stop)``."""
        return self._impl.randrange(start, stop)

    def choice[T](self, seq: Sequence[T]) -> T:
        """Return a uniformly chosen element from ``seq``."""
        return self._impl.choice(seq)
