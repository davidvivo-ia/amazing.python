"""Game state for an interactive maze run.

A :class:`PlaySession` tracks the player's current cell, the trail of
visited cells, the move count, and whether the game is still in
progress or has ended with a victory. It is intentionally **not**
inmutable: it is mutated by the presentation layer in response to
player input. The pure rules (which moves are legal) live in
:class:`amazing.domain.Maze`; this module only owns the *bookkeeping*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from amazing.domain import Cell, Direction, Maze, WallBlocksMovement


class SessionStatus(Enum):
    """Lifecycle state of a play session."""

    READY = "ready"
    PLAYING = "playing"
    WON = "won"


@dataclass(frozen=True, slots=True)
class GameState:
    """Read-only snapshot of a session at a given instant."""

    player: Cell
    visited: frozenset[Cell]
    moves: int
    status: SessionStatus


@dataclass(slots=True)
class PlaySession:
    """Mutable container that drives one game over a frozen maze."""

    maze: Maze
    _player: Cell = field(init=False)
    _visited: set[Cell] = field(init=False, default_factory=set)
    _moves: int = field(init=False, default=0)
    _status: SessionStatus = field(init=False, default=SessionStatus.READY)

    def __post_init__(self) -> None:
        self._player = self.maze.entry
        self._visited = {self.maze.entry}
        self._status = SessionStatus.PLAYING

    # ----------------------------------------------------------- queries
    @property
    def player(self) -> Cell:
        """Return the player's current cell."""
        return self._player

    @property
    def moves(self) -> int:
        """Return the number of successful moves so far."""
        return self._moves

    @property
    def status(self) -> SessionStatus:
        """Return the lifecycle status of the session."""
        return self._status

    @property
    def visited(self) -> frozenset[Cell]:
        """Return an immutable view of the cells visited so far."""
        return frozenset(self._visited)

    def snapshot(self) -> GameState:
        """Return an immutable snapshot suitable for rendering."""
        return GameState(
            player=self._player,
            visited=frozenset(self._visited),
            moves=self._moves,
            status=self._status,
        )

    # ----------------------------------------------------------- actions
    def try_move(self, direction: Direction) -> bool:
        """Attempt to move ``direction``.

        Returns ``True`` when the move succeeded and ``False`` when a
        wall blocked it. Walking south through the exit cell completes
        the game (``status`` becomes :class:`SessionStatus.WON`).
        """
        if self._status is SessionStatus.WON:
            return False
        try:
            destination = self.maze.move(self._player, direction)
        except WallBlocksMovement:
            return False

        if not self.maze.contains(destination):
            if direction is Direction.SOUTH and self._player == self.maze.exit:
                self._moves += 1
                self._status = SessionStatus.WON
                return True
            return False

        self._player = destination
        self._visited.add(destination)
        self._moves += 1
        if destination == self.maze.exit:
            # Reaching the exit cell itself doesn't win until the player
            # explicitly walks south through the opening. This is a
            # [LICENCIA CREATIVA] choice: the legacy program just printed
            # a static maze; we wanted the satisfying "step out".
            pass
        return True

    def reset(self) -> None:
        """Restart the session at the entry cell, preserving the maze."""
        self._player = self.maze.entry
        self._visited = {self.maze.entry}
        self._moves = 0
        self._status = SessionStatus.PLAYING
