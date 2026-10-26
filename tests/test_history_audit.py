import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fundamental_ranking_lab.cli import app
from fundamental_ranking_lab.history import ingest
from fundamental_ranking_lab.history_audit import audit
from tests.test_history_ingest import make_config


def test_end_to_end_audit_is_offline_and_never_approves_fixtures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("httpx.Client.get", lambda *a, **k: pytest.fail("offline network"))
    config = make_config(tmp_path)
    fixture = Path("tests/fixtures/history")
    for name in ("bundle.json", "source.txt"):
        (tmp_path / name).write_bytes((fixture / name).read_bytes())
    # Keep one quarter for this integration test; sample config exercises the full range.
    with config.open("a") as stream:
        stream.write('signal_start="2010-01-01"\nsignal_end="2010-03-31"\n')
    code, first = ingest(config)
    assert code == 3
    code, output = audit(config, first.name)
    assert code == 3
    scope = json.loads((output / "scope.json").read_bytes())
    assert scope["approved"] is False and scope["status"] == "prototype"
    assert "prototype_only" in scope["blockers"]
    _, replay = ingest(config, input_run=first.name)
    _, repeated = audit(config, replay.name)
    a = json.loads((output / "manifest.json").read_bytes())
    b = json.loads((repeated / "manifest.json").read_bytes())
    assert a["content_hashes"] == b["content_hashes"]
    assert len(list(output.glob("*.parquet"))) == 12
    result = CliRunner().invoke(
        app, ["audit-universe", "--config", str(config), "--input-run", first.name]
    )
    assert result.exit_code == 3


def test_cli_rejects_missing_config_and_conflicting_modes() -> None:
    runner = CliRunner()
    assert runner.invoke(app, ["ingest", "--config", "missing.toml"]).exit_code == 2
    assert (
        runner.invoke(
            app,
            ["ingest", "--config", "configs/history.toml", "--input-run", "a", "--resume-run", "b"],
        ).exit_code
        == 2
    )
