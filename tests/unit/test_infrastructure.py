"""Unit tests for the infrastructure layer."""

from __future__ import annotations

import random
from datetime import UTC, datetime
from pathlib import Path

import pytest

from amazing.application.rng import Rng
from amazing.infrastructure import ScoreRecord, ScoreStore, StdlibRng


# --------------------------------------------------------------------- RNG
def test_stdlib_rng_implements_protocol() -> None:
    assert isinstance(StdlibRng(0), Rng)


def test_stdlib_rng_is_seeded() -> None:
    a = StdlibRng(123)
    b = StdlibRng(123)
    assert [a.randrange(0, 1000) for _ in range(20)] == [b.randrange(0, 1000) for _ in range(20)]


def test_stdlib_rng_from_random_reuses_instance() -> None:
    src = random.Random(7)
    expected = src.randrange(0, 100)
    src = random.Random(7)  # reset to consume first value through our wrapper
    wrapper = StdlibRng.from_random(src)
    assert wrapper.randrange(0, 100) == expected


def test_stdlib_rng_choice() -> None:
    rng = StdlibRng(0)
    seq = (10, 20, 30, 40)
    assert rng.choice(seq) in seq


# --------------------------------------------------------------- persistence
def test_score_store_returns_empty_when_no_file(tmp_path: Path) -> None:
    store = ScoreStore(tmp_path / "scores.json")
    assert store.load() == []


def test_score_store_roundtrip(tmp_path: Path) -> None:
    store = ScoreStore(tmp_path / "scores.json")
    record = ScoreRecord(
        width=10,
        height=8,
        seed=42,
        moves=31,
        seconds=12.4,
        date=datetime(2026, 5, 12, 18, 33, 21, tzinfo=UTC),
    )
    store.save([record])
    loaded = store.load()
    assert loaded == [record]


def test_score_store_append(tmp_path: Path) -> None:
    store = ScoreStore(tmp_path / "scores.json")
    first = ScoreRecord(
        width=5,
        height=5,
        moves=10,
        seconds=4.0,
        date=datetime(2026, 1, 1, tzinfo=UTC),
    )
    second = ScoreRecord(
        width=5,
        height=5,
        moves=8,
        seconds=3.2,
        date=datetime(2026, 2, 1, tzinfo=UTC),
    )
    store.append(first)
    records = store.append(second)
    assert records == [first, second]
    assert store.load() == [first, second]


def test_score_record_rejects_invalid_dimensions() -> None:
    with pytest.raises(ValueError, match="greater than or equal"):
        ScoreRecord(
            width=0,
            height=5,
            moves=10,
            seconds=4.0,
            date=datetime(2026, 1, 1, tzinfo=UTC),
        )
