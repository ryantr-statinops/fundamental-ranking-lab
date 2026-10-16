"""Feasibility gates with explicit coverage denominators and independent group decisions."""

from typing import Any

from fundamental_ranking_lab.pilot_config import GROUP_QUOTAS


def assess_groups(
    coverage: list[dict[str, Any]],
    approved_groups: set[str],
    *,
    all_have_snapshot: bool,
) -> list[dict[str, Any]]:
    gates = []
    for group in GROUP_QUOTAS:
        cells = [cell for cell in coverage if cell["group"] == group]
        members = [cell for cell in cells if cell["membership"] == "member"]
        actual_entities = {cell["entity_id"] for cell in cells if cell["actual_snapshot"]}
        covered = sum(cell["actual_snapshot"] and cell["valid_axes"] >= 3 for cell in members)
        data_ok = len(actual_entities) >= 3 and bool(members) and covered / len(members) >= 0.5
        identity_complete = bool(cells) and all(
            cell["membership"] != "unresolved" for cell in cells
        )
        mismatch = any(cell["issues"] for cell in cells)
        ready = data_ok and identity_complete and not mismatch
        if ready and group in approved_groups:
            status = "pass"
        elif ready:
            status = "pending_review"
        else:
            status = "blocked"
        gates.append(
            {
                "group": group,
                "status": status,
                "actual_entities": len(actual_entities),
                "member_snapshots": len(members),
                "covered_member_snapshots": covered,
                "unresolved_membership": sum(cell["membership"] == "unresolved" for cell in cells),
                "coverage_fraction": covered / len(members) if members else None,
                "all_roster_entities_have_a_snapshot": all_have_snapshot,
                "unresolved_fact_or_period_mismatch": mismatch,
                "semantics_and_reconciliation_approved": group in approved_groups,
            }
        )
    return gates
