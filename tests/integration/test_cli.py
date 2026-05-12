"""Integration tests for the Typer-based CLI."""

from __future__ import annotations

from typer.testing import CliRunner

from amazing.presentation.cli import app

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "amazing" in result.stdout.lower()


def test_print_command_renders_a_maze() -> None:
    result = runner.invoke(
        app,
        ["print", "--width", "8", "--height", "6", "--seed", "42"],
    )
    assert result.exit_code == 0
    assert "AMAZING PROGRAM" in result.stdout
    assert "CREATIVE COMPUTING" in result.stdout
    # Maze body: top border has 1 + 3*8 chars and includes "."
    assert ".--" in result.stdout or ".  " in result.stdout


def test_print_command_unicode_style() -> None:
    result = runner.invoke(
        app,
        ["print", "--width", "6", "--height", "4", "--seed", "1", "--style", "unicode"],
    )
    assert result.exit_code == 0
    assert "+" in result.stdout
    assert "─" in result.stdout


def test_print_command_rejects_1x1() -> None:
    result = runner.invoke(app, ["print", "--width", "1", "--height", "1"])
    assert result.exit_code == 2
    assert "invalid maze dimensions" in (result.stdout + result.stderr)


def test_demo_command_completes() -> None:
    result = runner.invoke(
        app,
        ["demo", "--width", "8", "--height", "6", "--seed", "42"],
    )
    assert result.exit_code == 0
    assert "DEMO RESUELTA" in result.stdout


def test_demo_command_is_deterministic_for_same_seed() -> None:
    args = ["demo", "--width", "8", "--height", "6", "--seed", "42"]
    a = runner.invoke(app, args)
    b = runner.invoke(app, args)
    assert a.exit_code == b.exit_code == 0
    assert a.stdout == b.stdout
