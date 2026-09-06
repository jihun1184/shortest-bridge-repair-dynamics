"""Verify the frozen C07-D7D1 partial checkpoint without regenerating closures."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT = HERE / "c07d7d1_persistent_absorption_closure_results.json"
SUMMARY = HERE / "c07d7d1_partial_verification.json"


def main():
    payload = json.loads(RESULT.read_text())
    roots = payload["roots"]
    assert payload["status"] == "PARTIAL"
    assert payload["requested_root_count"] == 262
    assert payload["completed_root_count"] == len(roots) == 234
    assert sum(root["reachable_state_count"] for root in roots) == 11_987_299
    assert sum(root["transition_count"] for root in roots) == 20_255_841
    assert Counter(root["R_star"] for root in roots) == Counter({4: 222, 3: 12})
    assert all(root["max_reachable_N2_depth"] == 4 for root in roots)
    assert all(len(root["transition_sha256"]) == 64 for root in roots)

    by_orbit = defaultdict(list)
    for root in roots:
        by_orbit[root["orbit_index"]].append(root)
    assert len(by_orbit) == 117
    assert all(len(pair) == 2 for pair in by_orbit.values())
    assert all(len({root["R_star"] for root in pair}) == 1 for pair in by_orbit.values())

    r3_orbits = tuple(sorted(index for index, pair in by_orbit.items() if pair[0]["R_star"] == 3))
    assert r3_orbits == (15, 79, 89, 197, 206, 207)

    largest = max(roots, key=lambda root: root["reachable_state_count"])
    assert largest["root_id"] == "orbit_298:repair_0"
    assert largest["reachable_state_count"] == 693_229
    assert largest["transition_count"] == 1_172_112

    summary = {
        "checkpoint": "C07-D7D1 partial verification",
        "status": "PASS",
        "completed_roots": 234,
        "completed_D7B_states": 117,
        "uncomputed_roots": 28,
        "uncomputed_D7B_states": 14,
        "reachable_state_instances": 11_987_299,
        "transition_instances": 20_255_841,
        "R_star_histogram": {"3": 12, "4": 222},
        "persistent_R3_orbits": r3_orbits,
        "largest_completed_root": {
            "root_id": largest["root_id"],
            "reachable_states": largest["reachable_state_count"],
            "transitions": largest["transition_count"],
        },
    }
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
