"""SEC historical discovery parsers; filing presence never proves exchange listing."""

from __future__ import annotations

import json
import re
from typing import Any

from fundamental_ranking_lab.providers import submission_rows
from fundamental_ranking_lab.raw import RawRecord, RawStore, SourceError


def discover(records: list[RawRecord], store: RawStore) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for record in records:
        if record.kind not in {"master_index", "submissions", "submissions_history", "filing_text"}:
            continue
        payload = store.read(record)
        rows: list[dict[str, Any]] = []
        if record.kind == "master_index":
            for line in payload.decode("utf-8").splitlines():
                parts = line.split("|")
                if len(parts) != 5 or not parts[0].isdigit():
                    continue
                cik, company, form, filed, filename = parts
                if not re.fullmatch(r"edgar/data/\d+/[\d-]+\.txt", filename):
                    raise SourceError("invalid SEC master index filing path")
                rows.append(
                    {
                        "cik": cik.zfill(10),
                        "company": company,
                        "form": form,
                        "filing_date": filed,
                        "filing_path": filename,
                    }
                )
        elif record.kind in {"submissions", "submissions_history"}:
            value = json.loads(payload)
            page = (
                value.get("filings", {}).get("recent", {})
                if record.kind == "submissions"
                else value
            )
            rows.extend(submission_rows(page))
        else:
            text = payload.decode("utf-8", errors="replace")
            header = text.split("</SEC-HEADER>", 1)[0]
            row: dict[str, Any] = {}
            patterns = {
                "accepted_at_text": r"<ACCEPTANCE-DATETIME>(\d{14})",
                "cik": r"CENTRAL INDEX KEY:\s*(\d+)",
                "sic": r"STANDARD INDUSTRIAL CLASSIFICATION:[^\n]*\[(\d{4})\]",
                "form": r"CONFORMED SUBMISSION TYPE:\s*([^\r\n]+)",
                "period_end_text": r"CONFORMED PERIOD OF REPORT:\s*(\d{8})",
            }
            for name, pattern in patterns.items():
                match = re.search(pattern, header)
                if match:
                    row[name] = match[1].strip()
            if row:
                rows.append(row)
        output.extend(
            {
                **row,
                "entity_id": record.entity_id,
                "raw_sha256": record.sha256,
                "source_kind": record.kind,
                "listing_verified": False,
            }
            for row in rows
        )
    # Duplicate discoveries from indexes/submissions remain traceable to each source.
    return sorted(output, key=lambda row: json.dumps(row, sort_keys=True))
