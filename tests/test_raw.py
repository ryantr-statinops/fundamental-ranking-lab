from pathlib import Path

import httpx
import pytest

from fundamental_ranking_lab.pilot_config import CollectionSettings
from fundamental_ranking_lab.providers import SECProvider
from fundamental_ranking_lab.raw import RawStore, SecHTTP, SourceError


def test_retry_after_and_rate_budget_with_no_real_sleep() -> None:
    clock = [0.0]
    waits = []
    calls = []

    def sleep(seconds: float) -> None:
        waits.append(seconds)
        clock[0] += seconds

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return (
            httpx.Response(429, headers={"Retry-After": "10"})
            if len(calls) == 1
            else httpx.Response(200, json={"ok": True})
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        http = SecHTTP(
            "Fixture fixture@example.invalid",
            CollectionSettings(),
            client=client,
            sleep=sleep,
            clock=lambda: clock[0],
            jitter=lambda: 0,
        )
        assert http.get("https://data.sec.gov/test").status_code == 200
        http.get("https://www.sec.gov/test")
    assert waits == [10, 0.5]
    assert len(calls) == 3


@pytest.mark.parametrize("status", [403, 404])
def test_403_disables_source_and_404_does_not_retry(status: int) -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(status)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        http = SecHTTP("Fixture fixture@example.invalid", CollectionSettings(), client=client)
        with pytest.raises(SourceError):
            http.get("https://data.sec.gov/test")
        if status == 403:
            with pytest.raises(SourceError, match="stopped"):
                http.get("https://data.sec.gov/test")
    assert len(calls) == 1


def test_raw_store_checks_missing_corrupt_and_private_headers(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    record = store.put(
        b"original",
        source="fixture",
        url="fixture:test",
        kind="test",
        entity_id="test",
        headers={"Authorization": "secret", "User-Agent": "private", "ETag": "public-tag"},
    )
    assert record.headers == {"etag": "public-tag"}
    assert store.read(record) == b"original"
    target = tmp_path / record.relative_path
    target.write_bytes(b"corrupt")
    with pytest.raises(SourceError, match="checksum"):
        store.read(record)
    target.unlink()
    with pytest.raises(SourceError, match="will not download"):
        store.read(record)


def test_invalid_json_is_not_a_valid_cached_sec_response(tmp_path: Path) -> None:
    from fundamental_ranking_lab.pilot_config import load_roster

    roster = load_roster(Path(__file__).parents[1] / "configs/pilot-roster.csv")
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(200, content=b"<html>error</html>")
        )
    ) as client:
        http = SecHTTP("Fixture fixture@example.invalid", CollectionSettings(), client=client)
        provider = SECProvider(http, RawStore(tmp_path))
        with pytest.raises(SourceError, match="invalid JSON"):
            provider.fetch("https://data.sec.gov/test", roster[0], "companyfacts")
        assert provider.records == []
    assert not list(tmp_path.rglob("*"))


def test_retry_budget_is_finite() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(503)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        http = SecHTTP(
            "Fixture fixture@example.invalid",
            CollectionSettings(),
            client=client,
            sleep=lambda _seconds: None,
            clock=lambda: 100,
            jitter=lambda: 0,
        )
        with pytest.raises(SourceError, match="exhausted"):
            http.get("https://data.sec.gov/test")
    assert len(calls) == 5
