"""Infrastructure layer: adapters and side-effecting machinery."""

from amazing.infrastructure.persistence import ScoreRecord, ScoreStore
from amazing.infrastructure.rng import StdlibRng

__all__ = ["ScoreRecord", "ScoreStore", "StdlibRng"]
