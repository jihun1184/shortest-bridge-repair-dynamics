"""C07-D6B3: overlap extensions with no dual-role and P_preserve empty.

Seeds are the three no-dual D6B2 orbit representatives.  Add exactly one
voxel from the canonical X0 bounding box expanded by 2, quotient by lattice
isometry, then admit only states satisfying:

  has_fail(X), A_N1^(1)(X) nonempty, no dual-role N1 repair,
  and zero P_preserve-allowed actions across all A_atom(X).

The first exact depth >=3 state terminates planning and receives a complete
two-step-impossibility certificate.  A bounded miss is SEARCH_UNRESOLVED,
not atomic-unreachable.
"""

from __future__ import annotations

import itertools
import json
import sys
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
from c07d3e_component_viability import (  # noqa: E402
    component_bridge_exists,
    component_certificates,
    components6,
    descendant,
)
from c07d5_atomic_planning_census import (  # noqa: E402
    atomic_actions,
    canonical_isometry_class,
    goal,
    preserves_all_current_N2,
    shortest_atomic_plans,
)
from c07d6b1_one_voxel_break_search import dual_role_N1_repairs  # noqa: E402


def serial(points):
    return tuple(sorted(points))


def preservation_audit(state, actions):
    records = []
    for action in actions:
        allowed, obligations = preserves_all_current_N2(state, action)
        records.append(
            {
                "additions": action["additions"],
                "roles": action["roles"],
                "allowed": allowed,
                "obligations": obligations,
            }
        )
    return tuple(records)


def preserves_all_current_N2_fast(state, action):
    """Compressed-only prefilter; strict crosscheck follows after admission."""
    state = frozenset(state)
    successor = state | {tuple(point) for point in action["additions"]}
    after_components = components6(successor)
    for certificate in component_certificates(state):
        left = descendant(certificate[0], after_components)
        right = descendant(certificate[1], after_components)
        if left == right:
            continue
        bridgeable, _ = component_bridge_exists(
            successor, left, right, crosscheck=False
        )
        if not bridgeable:
            return False
    return True


def two_step_impossibility_certificate(state):
    """Enumerate all length-one and length-two atomic action sequences."""
    first_records = []
    one_step_goals = 0
    two_step_sequences = 0
    two_step_goals = 0
    for first in atomic_actions(state):
        delta1 = frozenset(tuple(point) for point in first["additions"])
        state1 = frozenset(set(state) | set(delta1))
        first_goal = goal(state1)
        one_step_goals += first_goal
        second_records = []
        if not first_goal:
            for second in atomic_actions(state1):
                delta2 = frozenset(tuple(point) for point in second["additions"])
                state2 = frozenset(set(state1) | set(delta2))
                reaches_goal = goal(state2)
                two_step_sequences += 1
                two_step_goals += reaches_goal
                second_records.append(
                    {
                        "additions": serial(delta2),
                        "roles": second["roles"],
                        "goal": reaches_goal,
                        "component_count": len(components6(state2)),
                    }
                )
        first_records.append(
            {
                "additions": serial(delta1),
                "roles": first["roles"],
                "goal": first_goal,
                "component_count": len(components6(state1)),
                "second_actions": tuple(second_records),
            }
        )
    return {
        "first_action_count": len(first_records),
        "one_step_goal_count": one_step_goals,
        "two_step_sequence_count": two_step_sequences,
        "two_step_goal_count": two_step_goals,
        "all_depth_lt_3_fail": one_step_goals == 0 and two_step_goals == 0,
        "first_actions": tuple(first_records),
    }


def main():
    source = HERE / "c07d6b2_two_voxel_break_search_results.json"
    d6b2 = json.loads(source.read_text(encoding="utf-8"))
    seeds = tuple(
        frozenset(tuple(point) for point in audit["representative"])
        for audit in d6b2["audits"]
    )
    assert len(seeds) == 3

    minima = tuple(min(point[a] for point in X0) - 2 for a in range(3))
    maxima = tuple(max(point[a] for point in X0) + 2 for a in range(3))
    window = tuple(
        itertools.product(
            *(range(minima[a], maxima[a] + 1) for a in range(3))
        )
    )

    raw_count = 0
    representatives = {}
    for seed_index, seed in enumerate(seeds):
        for extra in window:
            if extra in seed:
                continue
            raw_count += 1
            state = frozenset(set(seed) | {extra})
            key = canonical_isometry_class(state)
            representatives.setdefault(key, (state, seed_index, extra))

    defective = 0
    with_repairs = 0
    no_dual = 0
    no_dual_N1_preserve_empty = 0
    admitted = []
    for orbit_index, (orbit_key, (state, seed_index, extra)) in enumerate(
        sorted(representatives.items())
    ):
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
        # Necessary-condition short circuit: full P_preserve-empty implies
        # that every N1 action already fails preservation.  Most states are
        # rejected here without constructing their much larger N2 action set.
        n1_policy = []
        for v in repairs:
            n1_action = {"additions": (v,), "roles": ("N1",)}
            allowed = preserves_all_current_N2_fast(state, n1_action)
            n1_policy.append(
                {
                    "additions": (v,),
                    "roles": ("N1",),
                    "allowed": allowed,
                }
            )
        if any(record["allowed"] for record in n1_policy):
            continue
        no_dual_N1_preserve_empty += 1
        actions = atomic_actions(state)
        if any(preserves_all_current_N2_fast(state, action) for action in actions):
            continue
        # Only states surviving the compressed prefilter pay for the frozen
        # compressed/full-ordering crosscheck.  This is the authoritative audit.
        policy = preservation_audit(state, actions)
        assert not any(record["allowed"] for record in policy)
        assert all(not goal(frozenset(set(state) | set(map(tuple, action["additions"])))) for action in actions)
        admitted.append(
            {
                "orbit_index": orbit_index,
                "orbit_key": orbit_key,
                "representative": serial(state),
                "seed_index": seed_index,
                "extra": extra,
                "component_count": len(components6(state)),
                "valid_N1_repairs": repairs,
                "dual_role_N1_repairs": dual,
                "atomic_first_action_count": len(actions),
                "preservation_audit": policy,
            }
        )

    tested = []
    decisive = None
    for candidate in admitted:
        state = frozenset(tuple(point) for point in candidate["representative"])
        depth, plans, stats = shortest_atomic_plans(
            state, max_depth=len(components6(state)) + 2
        )
        audit = dict(candidate)
        audit.update(
            shortest_atomic_depth=depth,
            shortest_plan_count=len(plans),
            shortest_plans=plans,
            search_stats=stats,
            planning_class=(
                "SEARCH_UNRESOLVED" if depth is None
                else "DEPTH2" if depth == 2
                else "DEPTH3PLUS" if depth >= 3
                else "DEPTH1"
            ),
        )
        tested.append(audit)
        if depth is not None and depth >= 3:
            certificate = two_step_impossibility_certificate(state)
            assert certificate["all_depth_lt_3_fail"]
            assert plans and len(plans[0]) == depth
            audit["two_step_impossibility_certificate"] = certificate
            decisive = audit
            break

    result = {
        "family": {
            "seed_orbits": len(seeds),
            "seed_source": "D6B2 no-dual orbit representatives",
            "box_min": minima,
            "box_max": maxima,
            "window_point_count": len(window),
            "raw_seed_extensions": raw_count,
            "isometry_quotient_states": len(representatives),
            "admission": "has_fail; A_N1 nonempty; no dual-role N1; P_preserve allows no A_atom action",
        },
        "defective_orbits": defective,
        "orbits_with_valid_N1_repairs": with_repairs,
        "no_dual_role_orbits": no_dual,
        "no_dual_and_N1_preserve_empty_orbits": no_dual_N1_preserve_empty,
        "admitted_no_dual_preserve_empty_orbits": len(admitted),
        "planner_tested_before_stop": len(tested),
        "untested_after_stop": len(admitted) - len(tested),
        "tested": tested,
        "decisive_depth_ge_3_hit": decisive,
        "stop_rule": {
            "depth_ge_3": decisive is not None,
            "atomic_unreachable": False,
            "search_unresolved_count": sum(
                audit["planning_class"] == "SEARCH_UNRESOLVED" for audit in tested
            ),
            "family_exhausted": decisive is None and len(tested) == len(admitted),
        },
        "semantic_note": (
            "Under frozen A_N1^(1), every N1 action makes has_fail false; "
            "N1->N1 schedules are therefore outside the current action semantics."
        ),
    }
    output = HERE / "c07d6b3_overlap_attack_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D6B3 overlap attack complete")
    print("raw / quotient:", raw_count, len(representatives))
    print("defective / valid-repair / no-dual:", defective, with_repairs, no_dual)
    print("no-dual & N1-preserve-empty:", no_dual_N1_preserve_empty)
    print("admitted no-dual & preserve-empty:", len(admitted))
    print("tested / untested:", len(tested), len(admitted) - len(tested))
    print("depth>=3 decisive hit:", decisive is not None)
    if decisive is not None:
        print("hit depth / plans:", decisive["shortest_atomic_depth"], decisive["shortest_plan_count"])
    print("stop rule:", result["stop_rule"])
    print("JSON:", output)


if __name__ == "__main__":
    main()
