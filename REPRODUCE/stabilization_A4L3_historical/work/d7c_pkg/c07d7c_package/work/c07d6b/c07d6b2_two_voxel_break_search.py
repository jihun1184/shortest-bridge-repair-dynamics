"""C07-D6B2: exact two-background-voxel extensions in an expanded-by-1 box."""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
D3E = HERE.parent / "c07d3e"
D3B = HERE.parent / "c07d3b"
D4 = HERE.parent / "c07d4"
D5 = HERE.parent / "c07d5"
for dependency in (HERE, D3E, D4, D5, D3B / "c07a_scripts"):
    sys.path.insert(0, str(dependency))

from finite_window_classification import has_fail  # noqa: E402

from c07d3e1_targeted_search import valid_single_add_repairs  # noqa: E402
from c07d3e5_counterexample_verify import X as X0  # noqa: E402
from c07d3e_component_viability import components6  # noqa: E402
from c07d5_atomic_planning_census import (  # noqa: E402
    atomic_actions,
    canonical_isometry_class,
    preserves_all_current_N2,
    shortest_atomic_plans,
)
from c07d6b1_one_voxel_break_search import (  # noqa: E402
    dual_role_N1_repairs,
    macro2_recovery,
)


def serial(points):
    return tuple(sorted(points))


def main():
    minima = tuple(min(point[a] for point in X0) - 1 for a in range(3))
    maxima = tuple(max(point[a] for point in X0) + 1 for a in range(3))
    window = tuple(
        point
        for point in itertools.product(
            *(range(minima[a], maxima[a] + 1) for a in range(3))
        )
        if point not in X0
    )

    raw_count = 0
    defective_count = 0
    valid_repair_count = 0
    no_dual_raw_count = 0
    representatives = {}
    for extras in itertools.combinations(window, 2):
        raw_count += 1
        state = frozenset(set(X0) | set(extras))
        if not has_fail(state):
            continue
        defective_count += 1
        repairs = valid_single_add_repairs(state)
        if not repairs:
            continue
        valid_repair_count += 1
        if dual_role_N1_repairs(state, repairs):
            continue
        no_dual_raw_count += 1
        key = canonical_isometry_class(state)
        representatives.setdefault(key, (state, extras, repairs))

    audits = []
    for orbit_index, (orbit_key, (state, extras, repairs)) in enumerate(
        sorted(representatives.items())
    ):
        actions = atomic_actions(state)
        depth, plans, stats = shortest_atomic_plans(
            state, max_depth=len(components6(state)) + 1
        )
        preserving = 0
        for action in actions:
            allowed, _ = preserves_all_current_N2(state, action)
            preserving += allowed
        first_types = Counter(plan[0]["type"] for plan in plans) if plans else Counter()
        audit = {
            "orbit_index": orbit_index,
            "orbit_key": orbit_key,
            "representative": serial(state),
            "extras": tuple(sorted(extras)),
            "component_count": len(components6(state)),
            "valid_N1_repairs": repairs,
            "dual_role_N1_repairs": (),
            "atomic_first_action_count": len(actions),
            "immediate_preserving_first_action_count": preserving,
            "shortest_atomic_depth": depth,
            "shortest_plan_count": len(plans),
            "shortest_first_types": dict(sorted(first_types.items())),
            "search_stats": stats,
            "shortest_plans": plans,
        }
        if depth is None:
            audit["macro2_recoveries"] = macro2_recovery(state)
        audits.append(audit)

    depth_distribution = Counter(audit["shortest_atomic_depth"] for audit in audits)
    depth_ge_3 = [
        audit for audit in audits
        if audit["shortest_atomic_depth"] is not None
        and audit["shortest_atomic_depth"] >= 3
    ]
    unreachable = [audit for audit in audits if audit["shortest_atomic_depth"] is None]
    broader = [audit for audit in unreachable if audit.get("macro2_recoveries")]
    no_dual_greedy_failures = [
        audit for audit in audits
        if audit["immediate_preserving_first_action_count"] == 0
    ]

    result = {
        "family": {
            "base_X0": serial(X0),
            "box_min": minima,
            "box_max": maxima,
            "available_extra_points": len(window),
            "raw_two_voxel_extensions": raw_count,
            "constraint": "valid N1 single-add repair exists and no such repair is dual-role N1/N2",
        },
        "defective_raw_states": defective_count,
        "raw_states_with_valid_N1_repairs": valid_repair_count,
        "no_dual_role_raw_states": no_dual_raw_count,
        "no_dual_role_isometry_orbits": len(representatives),
        "no_dual_role_greedy_failure_orbits": len(no_dual_greedy_failures),
        "depth_distribution": {
            ("UNREACHABLE" if key is None else str(key)): value
            for key, value in sorted(depth_distribution.items(), key=lambda item: (item[0] is None, item[0] or 0))
        },
        "depth_ge_3_count": len(depth_ge_3),
        "atomic_unreachable_count": len(unreachable),
        "macro2_recoverable_atomic_unreachable_count": len(broader),
        "depth_ge_3_hits": depth_ge_3,
        "atomic_unreachable_hits": unreachable,
        "audits": audits,
        "stop_rule": {
            "depth_ge_3": bool(depth_ge_3),
            "atomic_unreachable": bool(unreachable),
            "family_exhausted": True,
        },
    }
    output = HERE / "c07d6b2_two_voxel_break_search_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D6B2 two-voxel no-dual search complete")
    print("raw / defective / valid-repair:", raw_count, defective_count, valid_repair_count)
    print("no-dual raw / orbits:", no_dual_raw_count, len(representatives))
    print("no-dual greedy-failure orbits:", len(no_dual_greedy_failures))
    print("depth distribution:", result["depth_distribution"])
    print("depth>=3:", len(depth_ge_3))
    print("atomic unreachable:", len(unreachable))
    print("macro2-recoverable unreachable:", len(broader))
    print("JSON:", output)


if __name__ == "__main__":
    main()
