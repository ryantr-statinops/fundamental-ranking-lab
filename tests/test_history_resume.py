import json
from pathlib import Path

import httpx
import pytest

from fundamental_ranking_lab.history import ingest
from tests.test_history_ingest import make_config


def test_failed_source_keeps_checkpoint_and_resume_skips_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = make_config(tmp_path)
    with config.open("a") as stream:
        stream.write('mode="live"\n')
    bundle_path = tmp_path / "bundle.json"
    value = json.loads(bundle_path.read_text())
    value.update(
        prototype=False,
        requests=[
            {
                "url": f"https://data.sec.gov/submissions/{name}.json",
                "kind": "submissions",
                "entity_id": name,
                "start": "2007-01-01",
                "end": "2025-12-31",
            }
            for name in ("first", "second")
        ],
    )
    bundle_path.write_text(json.dumps(value))
    monkeypatch.setenv("FRL_SEC_USER_AGENT", "Synthetic Test test@example.invalid")
    monkeypatch.setattr("fundamental_ranking_lab.history.pilot_blockers", lambda c: [])
    called = []
    fail = True

    def get(self: object, url: str, **kwargs: object) -> httpx.Response:
        called.append(url)
        if "second" in url and fail:
            raise RuntimeError("simulated interruption")
        return httpx.Response(200, json={"filings": {"recent": {}}})

    monkeypatch.setattr("httpx.Client.get", get)
    code, first = ingest(config)
    assert code == 1
    assert len(json.loads((first / "checkpoints.json").read_bytes())) == 1
    fail = False
    called.clear()
    code, resumed = ingest(config, resume_run=first.name)
    assert code == 0 and len(called) == 1 and "second" in called[0]
    assert len(json.loads((resumed / "checkpoints.json").read_bytes())) == 2


def test_live_mode_without_pilot_or_contact_does_not_call_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = make_config(tmp_path)
    with config.open("a") as stream:
        stream.write('mode="live"\n')
    monkeypatch.delenv("FRL_SEC_USER_AGENT", raising=False)
    monkeypatch.setattr("httpx.Client.get", lambda *a, **k: pytest.fail("blocked network"))
    code, run = ingest(config)
    blockers = json.loads((run / "blockers.json").read_bytes())
    assert (
        code == 3 and "pilot_gate_missing" in blockers and "sec_contact_not_configured" in blockers
    )
