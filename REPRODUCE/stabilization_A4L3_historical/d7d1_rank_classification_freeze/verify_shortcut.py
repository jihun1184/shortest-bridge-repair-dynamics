"""Reproduce the root-layer shortcut result for the 28 previously-uncomputed
C07-D7D1 roots (14 D7B depth-three orbits: 302, 316, 318, 320, 322, 329, 331,
333, 335, 337, 342, 344, 345, 347).

This does NOT run the full N2-reachable closure. It only enumerates the N2
actions available at the root state itself (depth 0) and checks:

    (a) every root already realizes an action with rho = 4;
    (b) no root-layer action exceeds rho = 4;
    (c) combined with the already-proved D7D0 component-monotonicity lemma,
        this is sufficient to conclude R*(root) = 4 exactly, without
        enumerating any descendant state.

Run from anywhere; paths are resolved relative to this file's location,
which must remain inside the C07D7D0_D7D1_Partial_Checkpoint tree (it
imports the frozen dependency package under work/d7c_pkg and the D7D1
closure module under work/d7d1).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKPOINT_ROOT = HERE.parent
PACKAGE = CHECKPOINT_ROOT / "work" / "d7c_pkg" / "c07d7c_package"
WORK = PACKAGE / "work"

for dependency in (
    CHECKPOINT_ROOT / "work" / "d7d1",
    WORK / "c07d3e",
    WORK / "c07d4",
    WORK / "c07d5",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

import c07d7d1_persistent_absorption_closure as m  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402
from c07d3e_component_viability import components6  # noqa: E402
from c07d5_atomic_planning_census import atomic_actions  # noqa: E402

MISSING_ORBITS = {302, 316, 318, 320, 322, 329, 331, 333, 335, 337, 342, 344, 345, 347}

EXPECTED_ROOT_COUNT = 28
EXPECTED_HIST = {2: 9058, 3: 10822, 4: 5648}
EXPECTED_TOTAL_N2 = 25528


def main() -> None:
    items = m.tasks()
    targets = [t for t in items if t[0] in MISSING_ORBITS]
    assert len(targets) == EXPECTED_ROOT_COUNT, len(targets)
    assert {t[0] for t in targets} == MISSING_ORBITS

    agg_hist: dict[int, int] = {}
    total_n2 = 0
    per_root = []

    for orbit_index, repair_index, initial_state, repair in targets:
        root = frozenset(tuple(p) for p in initial_state) | {tuple(repair)}
        assert not has_fail(root), "N1 successor must be Q2/Q3-valid"
        root_components = components6(root)
        assert len(root_components) == 5, "root must have five components"

        before_partition = m.root_identity_partition(root, root_components)
        actions = atomic_actions(root)

        root_hist: dict[int, int] = {}
        max_rho = 0
        n2_count = 0
        for action in actions:
            assert set(action["roles"]) == {"N2"}, "root-layer action must be N2-only"
            additions = frozenset(tuple(p) for p in action["additions"])
            successor = root | additions
            assert not has_fail(successor), "generated N2 successor must be valid"
            after_count = len(components6(successor))
            assert after_count < 5, "N2 action must strictly contract components"

            after_partition = m.root_identity_partition(successor, root_components)
            block = m.absorption_block(before_partition, after_partition)
            rho = len(block)
            assert rho <= 5, "rho cannot exceed root component count"

            root_hist[rho] = root_hist.get(rho, 0) + 1
            agg_hist[rho] = agg_hist.get(rho, 0) + 1
            max_rho = max(max_rho, rho)
            n2_count += 1
            total_n2 += 1

        assert max_rho == 4, f"root {orbit_index}:{repair_index} did not realize rho=4"
        per_root.append(
            {
                "root_id": f"orbit_{orbit_index}:repair_{repair_index}",
                "orbit_index": orbit_index,
                "repair_index": repair_index,
                "root_layer_N2_action_count": n2_count,
                "root_layer_rho_histogram": {str(k): v for k, v in sorted(root_hist.items())},
                "root_layer_max_rho": max_rho,
            }
        )

    assert agg_hist == EXPECTED_HIST, agg_hist
    assert total_n2 == EXPECTED_TOTAL_N2, total_n2
    assert all(r["root_layer_max_rho"] == 4 for r in per_root)

    summary = {
        "status": "PASS",
        "claim": (
            "For all 28 remaining C07-D7D1 roots, R* = 4 exactly, proved from "
            "root-layer rho=4 realization plus the D7D0 component-monotonicity "
            "lemma. No full N2-reachable closure was computed."
        ),
        "root_count": len(per_root),
        "aggregate_root_layer_rho_histogram": {str(k): v for k, v in sorted(agg_hist.items())},
        "aggregate_root_layer_N2_action_count": total_n2,
        "all_roots_R_star_4_by_shortcut": True,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
