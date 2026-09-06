"""C07-D6B1: one-background-voxel attack with no dual-role N1 action.

Predeclared family:
  X = X0 union {b}, where b lies in the coordinate bounding box of X0
  expanded by 2 in every direction.  Isometric duplicates are quotiented.

Only states with a valid N1 single-add repair and empty
A_N1^(1)(X) intersect A_N2(X) proceed to atomic planning.
"""

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
from c07d3e_component_viability import components6, neighbors6  # noqa: E402
from c07d5_atomic_planning_census import (  # noqa: E402
    atomic_actions,
    canonical_isometry_class,
    preserves_all_current_N2,
    shortest_atomic_plans,
)


def serial(points):
    return tuple(sorted(points))


def dual_role_N1_repairs(state, repairs):
    components = components6(state)
    output = []
    for v in repairs:
        neighborhood = set(neighbors6(v))
        touched = [component for component in components if neighborhood & set(component)]
        if len(touched) >= 2:
            output.append(v)
    return tuple(output)


def immediate_preserving_action_count(state):
    count = 0
    for action in atomic_actions(state):
        allowed, _ = preserves_all_current_N2(state, action)
        count += allowed
    return count


def macro2_recovery(state):
    """Broader-policy probe: union two current atomic action sets, then atomic plan."""
    actions = atomic_actions(state)
    recoveries = []
    for left, right in itertools.combinations(actions, 2):
        additions = frozenset(
            {tuple(point) for point in left["additions"]}
            | {tuple(point) for point in right["additions"]}
        )
        successor = frozenset(set(state) | set(additions))
        if has_fail(successor):
            continue
        if len(components6(successor)) == 1:
            recoveries.append(
                {"macro_additions": serial(additions), "atomic_continuation_depth": 0}
            )
            continue
        depth, plans, _ = shortest_atomic_plans(
            successor, max_depth=len(components6(successor)) + 1
        )
        if depth is not None:
            recoveries.append(
                {
                    "macro_additions": serial(additions),
                    "atomic_continuation_depth": depth,
                    "continuation_plan_count": len(plans),
                }
            )
    recoveries.sort(key=lambda record: (record["atomic_continuation_depth"], record["macro_additions"]))
    return tuple(recoveries)


def main():
    minima = tuple(min(point[a] for point in X0) - 2 for a in range(3))
    maxima = tuple(max(point[a] for point in X0) + 2 for a in range(3))
    window = tuple(
        itertools.product(
            *(range(minima[a], maxima[a] + 1) for a in range(3))
        )
    )

    raw_states = []
    by_orbit = {}
    for extra in window:
        if extra in X0:
            continue
        state = frozenset(set(X0) | {extra})
        raw_states.append(state)
        key = canonical_isometry_class(state)
        by_orbit.setdefault(key, state)

    defective = 0
    with_repairs = 0
    no_dual = 0
    audits = []
    for orbit_index, (orbit_key, state) in enumerate(sorted(by_orbit.items())):
        if not has_fail(state):
            continue
        defective += 1
        repairs = valid_single_add_repairs(state)
        if not repairs:
            continue
        with_repairs += 1
        dual = dual_role_N1_repairs(state, repairs)
        if dual:
            continue
        no_dual += 1
        actions = atomic_actions(state)
        depth_cap = len(components6(state)) + 1
        depth, plans, search_stats = shortest_atomic_plans(state, max_depth=depth_cap)
        preserving_count = immediate_preserving_action_count(state)
        first_types = Counter(plan[0]["type"] for plan in plans) if plans else Counter()
        audit = {
            "orbit_index": orbit_index,
            "orbit_key": orbit_key,
            "representative": serial(state),
            "extra_relative_to_X0_representation": tuple(sorted(set(state) - set(X0))),
            "component_count": len(components6(state)),
            "valid_N1_repairs": repairs,
            "dual_role_N1_repairs": dual,
            "atomic_first_action_count": len(actions),
            "immediate_preserving_first_action_count": preserving_count,
            "shortest_atomic_depth": depth,
            "shortest_plan_count": len(plans),
            "shortest_first_types": dict(sorted(first_types.items())),
            "search_stats": search_stats,
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
    broader_recoverable = [
        audit for audit in unreachable if audit.get("macro2_recoveries")
    ]

    result = {
        "family": {
            "base_X0": serial(X0),
            "box_min": minima,
            "box_max": maxima,
            "window_point_count": len(window),
            "raw_one_voxel_extensions": len(raw_states),
            "isometry_quotient_states": len(by_orbit),
            "constraint": "valid N1 single-add repair exists and no such repair is dual-role N1/N2",
        },
        "defective_orbits": defective,
        "orbits_with_valid_N1_repairs": with_repairs,
        "no_dual_role_orbits": no_dual,
        "depth_distribution": {
            ("UNREACHABLE" if key is None else str(key)): value
            for key, value in sorted(depth_distribution.items(), key=lambda item: (item[0] is None, item[0] or 0))
        },
        "depth_ge_3_count": len(depth_ge_3),
        "atomic_unreachable_count": len(unreachable),
        "macro2_recoverable_atomic_unreachable_count": len(broader_recoverable),
        "depth_ge_3_hits": depth_ge_3,
        "atomic_unreachable_hits": unreachable,
        "audits": audits,
        "stop_rule": {
            "depth_ge_3": bool(depth_ge_3),
            "atomic_unreachable": bool(unreachable),
            "family_exhausted": True,
        },
    }
    output = HERE / "c07d6b1_one_voxel_break_search_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D6B1 one-voxel no-dual search complete")
    print("raw / quotient states:", len(raw_states), len(by_orbit))
    print("defective / valid-repair / no-dual orbits:", defective, with_repairs, no_dual)
    print("depth distribution:", result["depth_distribution"])
    print("depth>=3:", len(depth_ge_3))
    print("atomic unreachable:", len(unreachable))
    print("macro2-recoverable unreachable:", len(broader_recoverable))
    print("JSON:", output)


if __name__ == "__main__":
    main()
