"""Textual TUI for AMAZING — the interactive game shell."""

from __future__ import annotations

import time
from importlib import resources
from typing import ClassVar, Final

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

from amazing.application import PlaySession, SessionStatus
from amazing.domain import Direction, Maze
from amazing.presentation.render import RenderStyle, render_maze

_CSS: Final[str] = (
    resources.files("amazing.assets").joinpath("tui.tcss").read_text(encoding="utf-8")
)


class MazeView(Static):
    """Live ASCII view of the maze that reacts to session changes."""

    moves = reactive(0)

    def __init__(self, session: PlaySession, style: RenderStyle) -> None:
        super().__init__("", id="maze-view")
        self._session = session
        self._style = style
        self._refresh_view()

    def update_view(self) -> None:
        """Re-render the maze from the current session state."""
        self.moves = self._session.moves
        self._refresh_view()

    def _refresh_view(self) -> None:
        text = render_maze(
            self._session.maze,
            style=self._style,
            player=self._session.player,
            trail=self._session.visited,
            show_exit_arrow=True,
        )
        self.update(text)


class StatsPanel(Static):
    """Side panel showing live game statistics."""

    def __init__(self, session: PlaySession) -> None:
        super().__init__("", id="stats")
        self._session = session
        self._started_at = time.monotonic()
        self._refresh_label()

    def refresh_stats(self, frozen_elapsed: float | None = None) -> None:
        """Refresh the rendered text with the latest stats."""
        elapsed = (
            frozen_elapsed if frozen_elapsed is not None else time.monotonic() - self._started_at
        )
        status = self._session.status
        status_label = "JUGANDO" if status is SessionStatus.PLAYING else "¡VICTORIA!"
        self.update(
            f"[b]ESTADO[/b]   {status_label}\n"
            f"[b]PASOS[/b]    {self._session.moves}\n"
            f"[b]TIEMPO[/b]   {elapsed:5.1f}s\n"
            f"[b]ENTRADA[/b]  ({self._session.maze.entry.col}, 0)\n"
            f"[b]SALIDA[/b]   ({self._session.maze.exit.col}, "
            f"{self._session.maze.height - 1})"
        )

    def _refresh_label(self) -> None:
        self.refresh_stats(frozen_elapsed=0.0)


class AmazingApp(App[None]):
    """Top-level Textual app for AMAZING."""

    BINDINGS: ClassVar = [
        Binding("up,k,w", "move('north')", "↑"),
        Binding("down,j,s", "move('south')", "↓"),
        Binding("left,h,a", "move('west')", "←"),
        Binding("right,l,d", "move('east')", "→"),
        Binding("r", "reset", "reiniciar"),
        Binding("t", "cycle_theme", "tema"),
        Binding("q", "quit", "salir"),
        Binding("question_mark", "show_help", "ayuda"),
    ]

    CSS = _CSS

    THEMES: ClassVar[tuple[str, ...]] = ("phosphor", "paper", "amber")

    def __init__(self, maze: Maze, style: RenderStyle = RenderStyle.UNICODE) -> None:
        super().__init__()
        self._maze = maze
        self._style = style
        self._session = PlaySession(maze)
        self._theme_index = 0
        self.title = "AMAZING"
        self.sub_title = "Creative Computing, 1978 → 2026"

    def on_mount(self) -> None:
        """Wire up theme and periodic refresh."""
        self._apply_theme()
        self.set_interval(0.5, self._tick)

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield Header(show_clock=False)
        with Vertical(id="layout"):
            yield MazeView(self._session, self._style)
            yield StatsPanel(self._session)
        yield Footer()

    # ----------------------------------------------------------- actions
    def action_move(self, direction_name: str) -> None:
        """Move the player one step in ``direction_name``."""
        direction = Direction[direction_name.upper()]
        moved = self._session.try_move(direction)
        if moved:
            self.query_one(MazeView).update_view()
            self.query_one(StatsPanel).refresh_stats()
            if self._session.status is SessionStatus.WON:
                self.bell()

    def action_reset(self) -> None:
        """Restart the current maze from its entry."""
        self._session.reset()
        self.query_one(MazeView).update_view()
        self.query_one(StatsPanel).refresh_stats(frozen_elapsed=0.0)

    def action_cycle_theme(self) -> None:
        """Switch to the next visual theme (phosphor → paper → amber)."""
        self._theme_index = (self._theme_index + 1) % len(self.THEMES)
        self._apply_theme()

    def action_show_help(self) -> None:
        """Show a short on-screen help notification."""
        self.notify(
            "Mueve con flechas / wasd / hjkl. R: reiniciar, T: tema, Q: salir.",
            title="AYUDA",
            timeout=4.0,
        )

    # ----------------------------------------------------------- internals
    def _tick(self) -> None:
        if self._session.status is SessionStatus.PLAYING:
            self.query_one(StatsPanel).refresh_stats()

    def _apply_theme(self) -> None:
        theme = self.THEMES[self._theme_index]
        # Theme switching is implemented as a CSS class swap on the screen.
        for value in self.THEMES:
            self.remove_class(f"theme-{value}")
        self.add_class(f"theme-{theme}")
        self.sub_title = f"tema: {theme}"
