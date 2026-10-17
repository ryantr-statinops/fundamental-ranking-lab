from pathlib import Path

from fundamental_ranking_lab.history_sources import discover
from fundamental_ranking_lab.raw import RawStore


def test_sec_indexes_and_filing_headers_are_discovery_only(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    records = [
        store.put(
            b"CIK|Company Name|Form Type|Date Filed|Filename\n"
            b"123|Synthetic|10-K|2009-02-01|edgar/data/123/0000000123-09-000001.txt\n",
            source="fixture",
            url="fixture:index",
            kind="master_index",
            entity_id="catalog",
        ),
        store.put(
            b"<SEC-HEADER>\n<ACCEPTANCE-DATETIME>20090201123000\n"
            b"CENTRAL INDEX KEY: 123\nSTANDARD INDUSTRIAL CLASSIFICATION: TEST [3571]\n"
            b"CONFORMED SUBMISSION TYPE: 10-K\n</SEC-HEADER>",
            source="fixture",
            url="fixture:filing",
            kind="filing_text",
            entity_id="e",
        ),
    ]
    result = discover(records, store)
    assert len(result) == 2
    assert all(r["listing_verified"] is False for r in result)
    assert {r.get("sic") for r in result} == {None, "3571"}
