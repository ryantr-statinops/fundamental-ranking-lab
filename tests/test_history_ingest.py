import json
from pathlib import Path

import pytest

from fundamental_ranking_lab.history import ingest
from fundamental_ranking_lab.manifest import canonical_sha256
from fundamental_ranking_lab.raw import SourceError


def make_config(tmp_path: Path) -> Path:
    bundle = {
        "mapping_version": "fixture-v1",
        "mapping": [],
        "mapping_sha256": canonical_sha256([]),
    }
    (tmp_path / "bundle.json").write_text(json.dumps(bundle))
    config = tmp_path / "history.toml"
    config.write_text(
        f'[paths]\ndata_dir="{tmp_path.as_posix()}/data"\n'
        f'artifact_dir="{tmp_path.as_posix()}/artifacts"\n'
        f'[history]\nbundle_path="{tmp_path.as_posix()}/bundle.json"\n'
    )
    return config


def test_ingest_replay_and_resume_are_immutable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("httpx.Client.get", lambda *a, **k: pytest.fail("offline network"))
    config = make_config(tmp_path)
    code, first = ingest(config)
    assert code == 3
    _, replay = ingest(config, input_run=first.name)
    _, resumed = ingest(config, resume_run=first.name)
    assert first != replay != resumed
    assert (first / "bundle.json").read_bytes() == (replay / "bundle.json").read_bytes()
    (first / "bundle.json").write_text("{}")
    with pytest.raises(SourceError):
        ingest(config, input_run=first.name)


def test_mutually_exclusive_replay_resume(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        ingest(make_config(tmp_path), "one", "two")


def test_pinned_raw_corruption_never_falls_back_to_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = make_config(tmp_path)
    fixture = Path("tests/fixtures/history")
    for name in ("bundle.json", "source.txt"):
        (tmp_path / name).write_bytes((fixture / name).read_bytes())
    _, run = ingest(config)
    record = json.loads((run / "raw_index.json").read_bytes())[0]
    raw = tmp_path / "data" / "raw" / record["relative_path"]
    monkeypatch.setattr("httpx.Client.get", lambda *a, **k: pytest.fail("offline network"))
    raw.write_bytes(b"corrupt")
    with pytest.raises(SourceError):
        ingest(config, input_run=run.name)
    raw.unlink()
    with pytest.raises(SourceError):
        ingest(config, input_run=run.name)
