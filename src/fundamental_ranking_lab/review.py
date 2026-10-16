"""Bind explicit human review to an independently completed reconciliation artifact."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from fundamental_ranking_lab.manifest import sha256_file
from fundamental_ranking_lab.pilot_config import GROUP_QUOTAS


def validate_review(
    review_path: Path,
    parent: str | None,
    hashes: dict[str, str],
    directory: Path,
    coverage: list[dict[str, Any]],
) -> tuple[set[str], list[dict[str, str]]]:
    def rejected(reason: str) -> tuple[set[str], list[dict[str, str]]]:
        return set(), [{"entity_id": "all", "reason": reason}]

    review = json.loads(review_path.read_text(encoding="utf-8"))
    if not parent or review.get("run_id") != parent or review.get("content_hashes") != hashes:
        return rejected("review_run_or_content_hashes_mismatch")
    if review.get("approved") is not True or not review.get("reviewer"):
        return rejected("explicit_user_review_missing")
    reviewed_at = datetime.fromisoformat(review.get("reviewed_at", ""))
    if reviewed_at.tzinfo is None:
        return rejected("review_timestamp_requires_timezone")
    template_path = directory / "reconciliation.csv"
    if review.get("template_sha256") != sha256_file(template_path):
        return rejected("review_reconciliation_template_mismatch")
    checked_path = review_path.parent / review["checked_csv"]
    if review.get("checked_csv_sha256") != sha256_file(checked_path):
        return rejected("review_checked_csv_checksum_mismatch")
    with template_path.open(encoding="utf-8", newline="") as stream:
        template = list(csv.DictReader(stream))
    with checked_path.open(encoding="utf-8", newline="") as stream:
        checked = list(csv.DictReader(stream))
    if len(checked) != len(template) or not template:
        return rejected("independent_check_row_count_mismatch")
    key_fields = ("entity_id", "cutoff", "kind", "name", "source_ref")
    index = {tuple(row.get(key, "") for key in key_fields): row for row in checked}
    if len(index) != len(checked):
        return rejected("duplicate_independent_check")
    checked_entities, groups = set(), set()
    for row in template:
        key = tuple(row.get(field, "") for field in key_fields)
        check = index.get(key)
        if check is None or row["kind"] not in {"input", "ratio"}:
            return rejected("reconciliation_lacks_actual_snapshot_or_source_check")
        if not check.get("reviewer") or not check.get("reviewed_at"):
            return rejected("independent_check_attribution_missing")
        if check.get("actual", "") != row["actual"]:
            return rejected("independent_check_actual_changed")
        if row["actual"] == "":
            if check.get("status") != "verified_unavailable" or check.get(
                "missing_reason"
            ) != row.get("missing_reason"):
                return rejected("unavailable_ratio_not_reconciled")
        else:
            try:
                actual, expected = Decimal(row["actual"]), Decimal(check["expected"])
                tolerance = Decimal(check["tolerance"])
                allowed = Decimal(row.get("allowed_tolerance") or "0")
                if not all(value.is_finite() for value in (actual, expected, tolerance, allowed)):
                    raise InvalidOperation
                if tolerance < 0 or tolerance > allowed or abs(actual - expected) > tolerance:
                    return rejected("independent_check_material_mismatch")
            except (InvalidOperation, KeyError):
                return rejected("independent_check_numeric_value_invalid")
        checked_entities.add(row["entity_id"])
        groups.add(row["group"])
    if len(checked_entities) < 10 or groups != set(GROUP_QUOTAS):
        return rejected("independent_check_sample_does_not_cover_ten_entities_and_six_groups")
    if any(
        not any(cell["entity_id"] == entity and cell["actual_snapshot"] for cell in coverage)
        for entity in checked_entities
    ):
        return rejected("independent_check_subject_has_no_actual_snapshot")
    approved = set(review.get("approved_groups", []))
    if not approved <= set(GROUP_QUOTAS):
        return rejected("unknown_approved_group")
    return approved, []
