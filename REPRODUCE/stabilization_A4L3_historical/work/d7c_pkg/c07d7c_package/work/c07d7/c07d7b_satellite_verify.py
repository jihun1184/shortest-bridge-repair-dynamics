"""Implementation audit for the state-deduplicated D7B depth census."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORK = HERE.parent
for dependency in (
    WORK / "c07d3e",
    WORK / "c07d4",
    WORK / "c07d5",
    WORK / "c07d6b",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

from c07d5_atomic_planning_census import shortest_atomic_plans  # noqa: E402


def main():
    source = HERE / "c07d7b_satellite_depth4_attack_results.json"
    result = json.loads(source.read_text(encoding="utf-8"))
    assert result["stop_rule"]["family_exhausted"]
    assert len(result["tested"]) == 150

    depth2 = [record for record in result["tested"] if record["depth"] == 2]
    depth3 = [record for record in result["tested"] if record["depth"] == 3]
    # Audit every exceptional depth-2 state and boundary representatives of
    # each distance shell among the much larger depth-3 class.
    selected = list(depth2)
    for distance in (2, 3, 4):
        shell = [record for record in depth3 if record["distance_to_X3"] == distance]
        selected.extend((shell[0], shell[-1]))

    audits = []
    seen = set()
    for record in selected:
        state_key = tuple(tuple(point) for point in record["state"])
        if state_key in seen:
            continue
        seen.add(state_key)
        state = frozenset(state_key)
        depth, plans, stats = shortest_atomic_plans(state, max_depth=4)
        assert depth == record["depth"]
        audits.append(
            {
                "second_satellite": record["second_satellite"],
                "census_depth": record["depth"],
                "full_sequence_depth": depth,
                "full_sequence_shortest_plan_count": len(plans),
                "planner_stats": stats,
            }
        )

    output = {
        "audited_state_count": len(audits),
        "all_19_depth2_states_audited": len(depth2) == 19,
        "depth3_shell_boundary_states_audited": 6,
        "all_depths_match": True,
        "audits": audits,
    }
    target = HERE / "c07d7b_satellite_verification.json"
    target.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
