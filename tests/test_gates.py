from fundamental_ranking_lab.gates import assess_groups


def test_group_gates_are_independent_and_require_explicit_approval() -> None:
    coverage = [
        {
            "entity_id": f"entity-{index}",
            "group": "General",
            "membership": "member",
            "actual_snapshot": True,
            "valid_axes": 3,
            "issues": [],
        }
        for index in range(3)
    ]

    gates = assess_groups(coverage, {"General"}, all_have_snapshot=True)

    assert gates[0]["status"] == "pass"
    assert gates[0]["coverage_fraction"] == 1.0
    assert all(gate["status"] == "blocked" for gate in gates[1:])


def test_unresolved_membership_blocks_a_group_even_with_coverage() -> None:
    coverage = [
        {
            "entity_id": f"entity-{index}",
            "group": "General",
            "membership": "member" if index < 3 else "unresolved",
            "actual_snapshot": index < 3,
            "valid_axes": 4,
            "issues": [],
        }
        for index in range(4)
    ]

    general = assess_groups(coverage, {"General"}, all_have_snapshot=False)[0]

    assert general["status"] == "blocked"
    assert general["unresolved_membership"] == 1
