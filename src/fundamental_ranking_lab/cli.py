"""Command-line entry point for the research lab."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from fundamental_ranking_lab.doctor import diagnostics

app = typer.Typer(no_args_is_help=True, help="Tools for reproducible ranking research.")


@app.command("ingest")
def ingest_command(
    config: Annotated[Path, typer.Option("--config")],
    input_run: Annotated[str | None, typer.Option("--input-run")] = None,
    resume_run: Annotated[str | None, typer.Option("--resume-run")] = None,
) -> None:
    """Collect historical evidence or replay pinned inputs offline."""
    from fundamental_ranking_lab.history import ingest

    _history_command(lambda: ingest(config, input_run, resume_run))


def _history_command(action: Callable[[], tuple[int, Path]]) -> None:
    from fundamental_ranking_lab.raw import SourceError

    try:
        code, destination = action()
    except (ValueError, FileNotFoundError):
        typer.echo("Invalid history configuration or missing input.", err=True)
        raise typer.Exit(code=2) from None
    except (OSError, SourceError):
        typer.echo("History IO or pinned source failure.", err=True)
        raise typer.Exit(code=1) from None
    typer.echo(f"History run: {destination}; exit code: {code}")
    raise typer.Exit(code=code)


@app.command("audit-universe")
def audit_universe_command(
    config: Annotated[Path, typer.Option("--config")],
    input_run: Annotated[str, typer.Option("--input-run")],
) -> None:
    """Audit pinned historical inputs offline."""
    from fundamental_ranking_lab.history_audit import audit

    _history_command(lambda: audit(config, input_run))


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


@app.command("pilot")
def pilot_command(
    config: Annotated[Path, typer.Option("--config", help="Validated pilot TOML configuration.")],
    input_run: Annotated[
        str | None, typer.Option("--input-run", help="Replay a pinned run offline.")
    ] = None,
) -> None:
    """Collect the pilot or replay raw inputs; publish a feasibility report and gate status."""
    from pydantic import ValidationError

    from fundamental_ranking_lab.pilot import run_pilot

    try:
        code, destination = run_pilot(config, input_run)
    except (ValidationError, ValueError, FileNotFoundError) as exc:
        typer.echo(f"Invalid pilot configuration: {type(exc).__name__}", err=True)
        raise typer.Exit(code=2) from None
    except OSError as exc:
        typer.echo(f"Pilot IO failure: {type(exc).__name__}", err=True)
        raise typer.Exit(code=1) from None
    typer.echo(f"Pilot run: {destination}")
    typer.echo(f"Exit code: {code}; see manifest.json, feasibility.md and blockers_final.json.")
    raise typer.Exit(code=code)


@app.command("rank")
def rank_command(
    input_run: Annotated[
        Path,
        typer.Option("--input-run", help="Path to pilot run directory with ratios.parquet."),
    ],
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Target output directory for ranking tables."),
    ] = None,
) -> None:
    """Compute cross-sectional percentile scores, industry ranks, and top-100 candidates."""
    from fundamental_ranking_lab.ranking import run_ranking

    try:
        code, destination = run_ranking(input_run, output_dir)
    except FileNotFoundError as exc:
        typer.echo(f"Ranking input failure: {exc}", err=True)
        raise typer.Exit(code=2) from None
    except Exception as exc:
        typer.echo(f"Ranking failure: {type(exc).__name__}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Ranking output generated at: {destination}")
    raise typer.Exit(code=code)


@app.command("portfolio")
def portfolio_command(
    input_ranking: Annotated[
        Path,
        typer.Option("--input-ranking", help="Path to ranking output directory."),
    ],
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Target output directory for portfolio tables."),
    ] = None,
) -> None:
    """Construct portfolio target weights with industry tilt and water-filling caps."""
    from fundamental_ranking_lab.portfolio import run_portfolio_construction

    try:
        code, destination = run_portfolio_construction(input_ranking, output_dir)
    except FileNotFoundError as exc:
        typer.echo(f"Portfolio input failure: {exc}", err=True)
        raise typer.Exit(code=2) from None
    except Exception as exc:
        typer.echo(f"Portfolio failure: {type(exc).__name__}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Portfolio output generated at: {destination}")
    raise typer.Exit(code=code)


@app.command("evaluate")
def evaluate_command(
    input_ranking: Annotated[
        Path,
        typer.Option("--input-ranking", help="Path to ranking output directory."),
    ],
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Target output directory for evaluation tables."),
    ] = None,
) -> None:
    """Evaluate hypotheses Q1, Q2, and Q3 with Newey-West and Benjamini-Hochberg tests."""
    from fundamental_ranking_lab.evaluation import run_evaluation

    try:
        code, destination = run_evaluation(input_ranking, output_dir)
    except FileNotFoundError as exc:
        typer.echo(f"Evaluation input failure: {exc}", err=True)
        raise typer.Exit(code=2) from None
    except Exception as exc:
        typer.echo(f"Evaluation failure: {type(exc).__name__}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Evaluation output generated at: {destination}")
    raise typer.Exit(code=code)


@app.command("quarterly")
def quarterly_command(
    cutoff: Annotated[str, typer.Option("--cutoff", help="Quarter-end cutoff date (YYYY-MM-DD).")],
    phase: Annotated[
        str,
        typer.Option("--phase", help="Phase to execute: 'signal' or 'reconcile'."),
    ] = "signal",
    input_run: Annotated[
        Path | None,
        typer.Option("--input-run", help="Parent signal run directory for reconcile phase."),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Optional target output directory."),
    ] = None,
) -> None:
    """Execute quarterly research operations (signal generation or morning reconcile)."""
    from fundamental_ranking_lab.quarterly import run_quarterly_reconcile, run_quarterly_signal

    try:
        if phase == "signal":
            code, destination = run_quarterly_signal(cutoff, Path("configs/pilot.toml"), output_dir)
        elif phase == "reconcile":
            if input_run is None:
                typer.echo("--input-run is required for reconcile phase", err=True)
                raise typer.Exit(code=2)
            code, destination = run_quarterly_reconcile(
                input_run, open_prices={}, output_root=output_dir
            )
        else:
            typer.echo(f"Unknown phase: {phase}. Must be 'signal' or 'reconcile'.", err=True)
            raise typer.Exit(code=2)
    except Exception as exc:
        typer.echo(f"Quarterly operation failure: {type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Quarterly {phase} output generated at: {destination}")
    raise typer.Exit(code=code)


@app.command("replay")
def replay_command(
    input_run: Annotated[
        Path,
        typer.Option("--input-run", help="Path to pinned run directory to replay offline."),
    ],
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Target replay output directory."),
    ] = None,
) -> None:
    """Replay a pinned run strictly offline with SHA-256 checksum verification."""
    from fundamental_ranking_lab.quarterly import run_offline_replay

    try:
        code, destination = run_offline_replay(input_run, output_dir)
    except Exception as exc:
        typer.echo(f"Replay failure: {type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Replayed run successfully at: {destination}")
    raise typer.Exit(code=code)
