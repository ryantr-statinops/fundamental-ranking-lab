"""Provider boundaries: SEC filing archives and explicitly configured daily prices."""

from __future__ import annotations

import json
import re
import time
from datetime import date, timedelta
from typing import Any

from fundamental_ranking_lab.pilot_config import RosterEntry
from fundamental_ranking_lab.raw import RawRecord, RawStore, SecHTTP, SourceError, encode_json


class SECProvider:
    def __init__(self, http: SecHTTP, store: RawStore) -> None:
        self.http, self.store = http, store
        self.records: list[RawRecord] = []
        self.issues: list[dict[str, str]] = []

    def fetch(
        self,
        url: str,
        entry: RosterEntry,
        kind: str,
        accession: str | None = None,
        *,
        expect_json: bool = True,
    ) -> bytes:
        cached = self.store.get_cached(url)
        if cached is not None:
            record, content = cached
            if expect_json:
                try:
                    json.loads(content)
                except (ValueError, UnicodeDecodeError):
                    cached = None
            if cached is not None:
                self.records.append(record)
                return content
        response = self.http.get(url)
        if expect_json:
            try:
                json.loads(response.content)
            except (ValueError, UnicodeDecodeError):
                raise SourceError("SEC returned an invalid JSON payload") from None
        self.records.append(
            self.store.put(
                response.content,
                source="sec",
                url=url,
                entity_id=entry.entity_id,
                kind=kind,
                accession=accession,
                headers=dict(response.headers),
            )
        )
        return response.content

    def collect(self, entry: RosterEntry, years: tuple[int, ...]) -> None:
        submissions = json.loads(
            self.fetch(
                f"https://data.sec.gov/submissions/CIK{entry.cik}.json", entry, "submissions"
            )
        )
        try:
            self.fetch(
                f"https://data.sec.gov/api/xbrl/companyfacts/CIK{entry.cik}.json",
                entry,
                "companyfacts",
            )
        except SourceError as exc:
            if "404" not in str(exc):
                raise
            # Companyfacts is a discovery aid; original filing archives can still be audited.
            self.issues.append({"entity_id": entry.entity_id, "reason": "companyfacts_not_found"})
        pages = [submissions.get("filings", {}).get("recent", {})]
        for historical in submissions.get("filings", {}).get("files", []):
            name = historical.get("name", "")
            if not re.fullmatch(r"CIK\d+-submissions-\d+\.json", name):
                raise SourceError("unexpected SEC submissions history filename")
            if any(
                str(year - 4) <= str(historical.get("filingTo", ""))[:4]
                and str(historical.get("filingFrom", ""))[:4] <= str(year)
                for year in years
            ):
                pages.append(
                    json.loads(
                        self.fetch(
                            f"https://data.sec.gov/submissions/{name}", entry, "submissions_history"
                        )
                    )
                )
        selected: dict[str, dict[str, Any]] = {}
        for page in pages:
            for row in submission_rows(page):
                filed = str(row.get("filingDate", ""))
                if row.get("form") not in {"10-K", "10-Q", "10-K/A", "10-Q/A"}:
                    continue
                if (
                    any(year - 4 <= int(filed[:4]) <= year for year in years)
                    and filed[:10] <= f"{max(years)}-12-31"
                ):
                    selected[str(row["accessionNumber"])] = row
        for accession, row in sorted(selected.items()):
            if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession):
                raise SourceError("unexpected SEC accession")
            directory = accession.replace("-", "")
            base = f"https://www.sec.gov/Archives/edgar/data/{int(entry.cik)}/{directory}"
            self.fetch(
                f"{base}/{accession}.txt", entry, "filing_text", accession, expect_json=False
            )
            index = json.loads(self.fetch(f"{base}/index.json", entry, "filing_index", accession))
            primary = str(row.get("primaryDocument", ""))
            candidates = [primary] if primary else []
            for item in index.get("directory", {}).get("item", []):
                name = item.get("name", "")
                if (
                    name.endswith(".xml")
                    and not re.search(r"_(cal|def|lab|pre)\.xml$", name)
                    and name not in {"FilingSummary.xml", "MetaLinks.xml"}
                ):
                    candidates.append(name)
            for name in dict.fromkeys(candidates):
                if not name or "/" in name or "\\" in name or ".." in name:
                    raise SourceError("unexpected filing document filename")
                self.fetch(f"{base}/{name}", entry, "filing_document", accession, expect_json=False)


def submission_rows(page: dict[str, Any]) -> list[dict[str, Any]]:
    accessions = page.get("accessionNumber", [])
    return [
        {
            key: values[index]
            for key, values in page.items()
            if isinstance(values, list) and len(values) > index
        }
        for index in range(len(accessions))
    ]


class YFinanceProvider:
    def __init__(self, store: RawStore, requests_per_second: float = 2) -> None:
        self.store = store
        self.interval = 1 / requests_per_second
        self.last_request: float | None = None

    def collect(self, entry: RosterEntry, symbol: str, cutoff: date) -> RawRecord:
        url = f"yfinance:{symbol}:{cutoff}"
        cached = self.store.get_cached(url)
        if cached is not None:
            return cached[0]
        import yfinance as yf  # type: ignore[import-untyped]

        if self.last_request is not None:
            time.sleep(max(0, self.interval - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        ticker = yf.Ticker(symbol)
        history = ticker.history(
            start=(cutoff - timedelta(days=75)).isoformat(),
            end=(cutoff + timedelta(days=1)).isoformat(),
            interval="1d",
            auto_adjust=False,
            back_adjust=False,
            actions=True,
            repair=False,
            raise_errors=True,
            timeout=30,
        )
        if history.empty:
            raise SourceError("yfinance returned no daily observations")
        rows = []
        for timestamp, row in history.iterrows():
            rows.append(
                {
                    "date": str(timestamp)[:10],
                    **{
                        str(column): None if value != value else float(value)
                        for column, value in row.items()
                    },
                }
            )
        payload = {
            "symbol": symbol,
            "cutoff": cutoff.isoformat(),
            "rows": rows,
            "currency": ticker.history_metadata.get("currency"),
            "convention": "provider_unadjusted_ohlcv_auto_adjust_false_no_repair",
            "limitation": (
                "provider history may incorporate historical split adjustments; "
                "verify against filing/event evidence"
            ),
        }
        return self.store.put(
            encode_json(payload),
            source="yfinance",
            url=url,
            kind="prices",
            entity_id=entry.entity_id,
        )
