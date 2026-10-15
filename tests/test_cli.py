from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fundamental_ranking_lab.cli import app


def test_doctor_reads_config_without_network(sample_config_path: Path) -> None:
    result = CliRunner().invoke(app, ["doctor", "--config", str(sample_config_path)])
    assert "OK config:" in result.output
    assert "research fingerprint" in result.output


def test_doctor_reports_invalid_config(tmp_path: Path) -> None:
    invalid = tmp_path / "bad.toml"
    invalid.write_text("[research]\nunknown = true\n", encoding="utf-8")
    result = CliRunner().invoke(app, ["doctor", "--config", str(invalid)])
    assert result.exit_code == 1
    assert "FAIL config:" in result.output
