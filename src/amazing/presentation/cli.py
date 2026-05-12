"""Typer-based command-line interface for AMAZING."""

from __future__ import annotations

import sys
import time
from itertools import pairwise
from typing import Annotated

import typer
from rich.console import Console
from rich.text import Text

from amazing import __version__
from amazing.application import (
    PlaySession,
    SessionStatus,
    carve,
    shortest_path,
)
from amazing.domain import (
    AmazingError,
    Cell,
    Direction,
    InvalidDimensions,
    Maze,
)
from amazing.infrastructure import StdlibRng
from amazing.presentation.render import RenderStyle, render_maze

app = typer.Typer(
    name="amazing",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
    help=(
        "AMAZING — a 1978 BASIC maze generator, reborn as a modern Python "
        "TUI game. Use the subcommands below to play, print or demo."
    ),
)

console = Console()
HEADER_LINES = (
    " " * 28 + "AMAZING PROGRAM",
    " " * 15 + "CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY",
)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"amazing {__version__}")
        raise typer.Exit


@app.callback()
def _root(
    _version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Root callback: enables ``--version``."""


# ----------------------------------------------------------------- print
@app.command("print")
def print_command(
    width: Annotated[int, typer.Option("--width", "-W", min=1)] = 10,
    height: Annotated[int, typer.Option("--height", "-H", min=1)] = 6,
    seed: Annotated[int | None, typer.Option("--seed", help="reproducible RNG seed")] = None,
    style: Annotated[
        RenderStyle,
        typer.Option("--style", case_sensitive=False, help="charset"),
    ] = RenderStyle.LEGACY,
) -> None:
    """Generate a maze and print it once to stdout (1978-faithful mode)."""
    maze = _carve_or_exit(width, height, seed)
    for line in HEADER_LINES:
        typer.echo(line)
    typer.echo("")
    typer.echo(render_maze(maze, style=style, show_exit_arrow=True))


# ----------------------------------------------------------------- demo
@app.command("demo")
def demo_command(
    width: Annotated[int, typer.Option("--width", "-W", min=1)] = 10,
    height: Annotated[int, typer.Option("--height", "-H", min=1)] = 6,
    seed: Annotated[int | None, typer.Option("--seed")] = 42,
    style: Annotated[
        RenderStyle,
        typer.Option("--style", case_sensitive=False),
    ] = RenderStyle.LEGACY,
    step_delay: Annotated[
        float,
        typer.Option("--step-delay", min=0.0, help="seconds between steps"),
    ] = 0.0,
) -> None:
    """Generate a maze, solve it with BFS, and print every step."""
    maze = _carve_or_exit(width, height, seed)
    session = PlaySession(maze)
    path = shortest_path(maze)

    for current, nxt in pairwise(path):
        direction = _direction_between(current, nxt)
        session.try_move(direction)
        if step_delay > 0:
            _print_frame(session, style)
            time.sleep(step_delay)
    session.try_move(Direction.SOUTH)  # walk through the exit

    final = render_maze(
        maze,
        style=style,
        player=None,
        trail=session.visited,
        show_exit_arrow=True,
    )
    console.print(Text("DEMO RESUELTA EN " + str(session.moves) + " PASOS", style="bold green"))
    typer.echo(final)


# ----------------------------------------------------------------- play
@app.command("play")
def play_command(
    width: Annotated[int, typer.Option("--width", "-W", min=1)] = 12,
    height: Annotated[int, typer.Option("--height", "-H", min=1)] = 8,
    seed: Annotated[int | None, typer.Option("--seed")] = None,
    style: Annotated[
        RenderStyle,
        typer.Option("--style", case_sensitive=False),
    ] = RenderStyle.UNICODE,
) -> None:
    """Launch the interactive Textual TUI."""
    maze = _carve_or_exit(width, height, seed)
    # Import lazily to avoid loading Textual when running --help or print mode.
    from amazing.presentation.tui import AmazingApp

    app_ = AmazingApp(maze=maze, style=style)
    app_.run()


# ----------------------------------------------------------------- helpers
def _carve_or_exit(width: int, height: int, seed: int | None) -> Maze:
    try:
        return carve(width=width, height=height, rng=StdlibRng(seed))
    except InvalidDimensions as exc:
        console.print(f"[bold red]error:[/bold red] {exc}")
        raise typer.Exit(code=2) from exc
    except AmazingError as exc:  # pragma: no cover - defensive
        console.print(f"[bold red]error:[/bold red] {exc}")
        raise typer.Exit(code=2) from exc


def _direction_between(a: Cell, b: Cell) -> Direction:
    delta = (b.col - a.col, b.row - a.row)
    for direction in Direction:
        if (direction.dcol, direction.drow) == delta:
            return direction
    raise AssertionError(f"non-adjacent cells {a!r} -> {b!r}")


def _print_frame(session: PlaySession, style: RenderStyle) -> None:
    sys.stdout.write("\x1b[2J\x1b[H")  # clear screen + home
    sys.stdout.write(
        render_maze(
            session.maze,
            style=style,
            player=session.player,
            trail=session.visited,
            show_exit_arrow=True,
        )
    )
    sys.stdout.write(f"\nPasos: {session.moves}\n")
    sys.stdout.flush()
    if session.status is SessionStatus.WON:
        sys.stdout.write("¡VICTORIA!\n")
