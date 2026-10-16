import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fundamental_ranking_lab.cli import app
from fundamental_ranking_lab.filings import Fact
from fundamental_ranking_lab.manifest import (
    RunManifest,
    canonical_sha256,
    sha256_file,
    write_manifest,
)
from fundamental_ranking_lab.pilot import (
    CellEvidence,
    ClassEvidence,
    _market_data,
    cutoffs,
    run_pilot,
)
from fundamental_ranking_lab.pilot_config import load_pilot_config, load_roster
from fundamental_ranking_lab.raw import RawStore, SecHTTP, encode_json


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    root = Path(__file__).parents[1]
    config = tmp_path / "pilot.toml"
    config.write_text(
        '[paths]\ndata_dir = "'
        + (tmp_path / "data").as_posix()
        + '"\nartifact_dir = "'
        + (tmp_path / "artifacts").as_posix()
        + '"\n[pilot]\nroster_path = "'
        + (root / "configs/pilot-roster.csv").as_posix()
        + '"\n',
        encoding="utf-8",
    )
    return config


def test_blocked_pilot_and_offline_replay_keep_all_cells(config_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("FRL_SEC_USER_AGENT", raising=False)

    def no_network(*args, **kwargs):
        raise AssertionError("offline execution attempted network")

    monkeypatch.setattr(SecHTTP, "get", no_network)
    code, original = run_pilot(config_path)
    replay_code, replay = run_pilot(config_path, original.name)
    assert code == replay_code == 3
    cells = json.loads((original / "coverage.json").read_text())
    assert len(cells) == 160 and not any(cell["actual_snapshot"] for cell in cells)
    assert all(
        gate["status"] == "blocked"
        for gate in json.loads((original / "group_gates.json").read_text())
    )
    first = RunManifest.model_validate_json((original / "manifest.json").read_text())
    second = RunManifest.model_validate_json((replay / "manifest.json").read_text())
    assert first.content_hashes == second.content_hashes
    assert second.parent_run == original.name
    assert first.status == "blocked"
    assert first.code_sha256 and len(first.code_sha256) == 64
    assert (original / "feasibility.html").exists()
    assert (original / "reconciliation.csv").exists()


def test_pinned_original_filing_replays_and_missing_raw_never_downloads(
    config_path: Path, monkeypatch
) -> None:
    config = load_pilot_config(config_path)
    roster = load_roster(config.pilot.roster_path)
    store = RawStore(config.paths.data_dir / "raw")
    header = store.put(
        (
            b"<ACCEPTANCE-DATETIME>20251101120000\nFILED AS OF DATE: 20251101\n"
            b"CONFORMED SUBMISSION TYPE: 10-Q"
        ),
        source="fixture",
        url="fixture:header",
        kind="filing_text",
        entity_id=roster[0].entity_id,
        accession="fixture",
    )
    content = (
        (Path(__file__).parent / "fixtures/pilot/as-filed.xml")
        .read_bytes()
        .replace(b"0000000001", roster[0].cik.encode())
    )
    document = store.put(
        content,
        source="fixture",
        url="fixture:document",
        kind="filing_document",
        entity_id=roster[0].entity_id,
        accession="fixture",
    )
    parent = config.paths.artifact_dir / "fixture-parent"
    parent.mkdir(parents=True)
    index = parent / "raw_index.json"
    index.write_bytes(
        encode_json([header.model_dump(mode="json"), document.model_dump(mode="json")])
    )
    write_manifest(
        RunManifest(
            run_id=parent.name,
            created_at_utc=datetime.now(UTC),
            command="fixture",
            config_sha256=config.research_fingerprint(),
            code_revision="fixture",
            input_artifacts={
                "roster": sha256_file(config.pilot.roster_path),
                "evidence": canonical_sha256({}),
            },
            output_artifacts={"raw_index.json": sha256_file(index)},
        ),
        parent / "manifest.json",
    )
    monkeypatch.setattr(SecHTTP, "get", lambda *args, **kwargs: pytest.fail("network called"))
    code, first = run_pilot(config_path, parent.name)
    replay_code, second = run_pilot(config_path, first.name)
    assert code == replay_code == 3
    first_manifest = json.loads((first / "manifest.json").read_text())
    second_manifest = json.loads((second / "manifest.json").read_text())
    assert first_manifest["content_hashes"] == second_manifest["content_hashes"]
    (store.root / document.relative_path).unlink()
    failure_code, failure = run_pilot(config_path, first.name)
    assert failure_code == 1
    assert json.loads((failure / "manifest.json").read_text())["status"] == "failed"


def test_cutoffs_and_invalid_cli_configuration(tmp_path: Path) -> None:
    values = cutoffs((2012, 2018, 2022, 2025))
    assert [value.date().isoformat() for value in values] == [
        "2012-12-31",
        "2018-12-31",
        "2022-12-30",
        "2025-12-31",
    ]
    assert all(value.hour == 16 and value.astimezone(UTC).hour == 21 for value in values)
    invalid = tmp_path / "bad.toml"
    invalid.write_text("[pilot]\nroster_path='none'\nunknown=true\n")
    assert CliRunner().invoke(app, ["pilot", "--config", str(invalid)]).exit_code == 2


def test_multiple_common_classes_use_distinct_prices_and_missing_class_blocks_cap(
    tmp_path: Path,
) -> None:
    import exchange_calendars as xcals

    cutoff = datetime(2025, 12, 31, 16, tzinfo=__import__("zoneinfo").ZoneInfo("America/New_York"))
    sessions = xcals.get_calendar("XNYS").sessions_in_range("2025-12-01", "2025-12-31")[-20:]
    store = RawStore(tmp_path)
    entry = load_roster(Path(__file__).parents[1] / "configs/pilot-roster.csv")[0]
    records, facts, classes = [], [], []
    for symbol, shares, price in [("AAA", 30, 10), ("BBB", 70, 20)]:
        records.append(
            store.put(
                encode_json(
                    {
                        "symbol": symbol,
                        "currency": "USD",
                        "cutoff": "2025-12-31",
                        "rows": [
                            {"date": day.date().isoformat(), "Close": price, "Volume": 1_000_000}
                            for day in sessions
                        ],
                    }
                ),
                source="fixture",
                url="fixture:prices",
                kind="prices",
                entity_id=entry.entity_id,
            )
        )
        facts.append(
            Fact(
                entity_id=entry.entity_id,
                accession="fixture",
                taxonomy="dei",
                tag="EntityCommonStockSharesOutstanding",
                context_id=symbol,
                period_end=date(2025, 9, 30),
                unit="shares",
                value_text=str(shares),
                value=Decimal(shares),
                filed_date=date(2025, 10, 30),
                publication_precision="date_only",
                raw_sha256="a" * 64,
                form="10-Q",
            )
        )
        classes.append(
            ClassEvidence(
                security_id=symbol,
                symbol=symbol,
                shares_raw_sha256="a" * 64,
                shares_context_id=symbol,
            )
        )
    evidence = CellEvidence(
        identity_verified=True,
        price_convention_verified=True,
        all_common_classes_verified=True,
        classes=tuple(classes),
    )
    cap, market = _market_data(entry, cutoff, evidence, facts, records, store)
    assert cap.value == 1700 and market["selected_security_id"] == "BBB"
    missing, _ = _market_data(entry, cutoff, evidence, facts, records[:1], store)
    assert missing.value is None and missing.reason == "missing_twenty_price_sessions"
