"""Command-line entry point for the research lab."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from fundamental_ranking_lab.doctor import diagnostics

app = typer.Typer(no_args_is_help=True, help="Tools for reproducible ranking research.")


@app.command("doctor")
def doctor_command(
    config: Annotated[
        Path | None, typer.Option("--config", help="TOML config to validate.")
    ] = None,
) -> None:
    """Check Python, installed dependencies, and optionally a TOML config."""
    ok, checks, _ = diagnostics(config)
    for check in checks:
        typer.echo(check)
    if not ok:
        raise typer.Exit(code=1)


@app.command("version", hidden=True)
def version_command() -> None:
    """Keep the CLI as a command group so commands use explicit subcommands."""
