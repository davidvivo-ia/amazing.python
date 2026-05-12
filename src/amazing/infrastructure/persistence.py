"""Persistence of personal-best records under the XDG data directory."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Iterable


class ScoreRecord(BaseModel):
    """One row in the score archive."""

    width: int = Field(ge=1)
    height: int = Field(ge=1)
    seed: int | None = None
    moves: int = Field(ge=0)
    seconds: float = Field(ge=0.0)
    date: datetime


class _Archive(BaseModel):
    """Top-level JSON document persisted under ``$XDG_DATA_HOME``."""

    version: int = 1
    records: list[ScoreRecord] = Field(default_factory=list)


def _default_path() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    root = Path(base) if base else Path.home() / ".local" / "share"
    return root / "amazing" / "scores.json"


class ScoreStore:
    """Tiny JSON-backed personal-best archive.

    All filesystem access is concentrated here so the rest of the app
    can be tested without touching disk.
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path: Path = path if path is not None else _default_path()

    # -------------------------------------------------------------- io
    def load(self) -> list[ScoreRecord]:
        """Load the archive, returning an empty list if no file exists."""
        if not self.path.exists():
            return []
        raw = self.path.read_text(encoding="utf-8")
        archive = _Archive.model_validate_json(raw)
        return list(archive.records)

    def save(self, records: Iterable[ScoreRecord]) -> None:
        """Write ``records`` to disk, creating parents as needed."""
        archive = _Archive(records=list(records))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            archive.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def append(self, record: ScoreRecord) -> list[ScoreRecord]:
        """Append ``record`` to the archive and persist; returns the new list."""
        records = self.load()
        records.append(record)
        self.save(records)
        return records


def now_utc() -> datetime:
    """Return ``datetime.now`` in UTC. Centralised for monkey-patching."""
    return datetime.now(UTC)
