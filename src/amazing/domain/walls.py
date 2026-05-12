"""Wall encoding for a single maze cell.

A cell only tracks its right and bottom walls. The other two are owned
by its neighbours; the outer perimeter is implicit. This mirrors how the
1978 BASIC original encoded walls in its ``V(I,J)`` matrix with values
``0/1/2/3``, but expressed as an explicit bit flag for legibility.
"""

from __future__ import annotations

from enum import IntFlag


class Wall(IntFlag):
    """Standing walls on a cell's right and bottom edges.

    Members combine bitwise: ``Wall.RIGHT | Wall.BOTTOM == Wall.BOTH``.
    The legacy program used integers ``0..3`` for the same encoding;
    this class is bit-compatible (RIGHT=1, BOTTOM=2) for easy
    cross-reading against the original listing.
    """

    NONE = 0
    RIGHT = 1
    BOTTOM = 2
    BOTH = RIGHT | BOTTOM
