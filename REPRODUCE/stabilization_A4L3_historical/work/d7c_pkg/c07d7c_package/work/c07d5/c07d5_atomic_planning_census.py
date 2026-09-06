"""C07-D5A--D5C: formal atomic planning and 24-witness depth census.

State is the voxel set X.  Primitive actions are identified by their nonempty
addition set, with overlapping role labels:

  A_atom(X) = A_N1^(1)(X) union A_N2(X).

The union is not disjoint: a one-voxel addition may be both an N1 repair and
an N2 shortest compatible bridge.  All certificates and actions are recomputed
after every transition.  Goal means Q2/Q3-valid and one 6-component.
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
D3E = HERE.parent / "c07d3e"
D3B = HERE.parent / "c07d3b"
D4 = HERE.parent / "c07d4"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(D3E))
sys.path.insert(0, str(D4))
sys.path.insert(0, str(D3B / "c07a_scripts"))

from finite_window_classification import has_fail  # noqa: E402

from c07d3e1_targeted_search import valid_single_add_repairs  # noqa: E402
from c07d3e_component_viability import (  # noqa: E402
    component_bridge_exists,
    component_certificates,
    components6,
    descendant,
)
from c07d4_planning_census import certificate_bridge_actions  # noqa: E402


def serial_points(points):
    return tuple(sorted(points))


def goal(state):
    return not has_fail(state) and len(components6(state)) == 1


def atomic_actions(state):
    """Deduplicate by resulting addition set and retain all semantic roles."""
    state = frozenset(state)
    actions = {}

    def record(additions, role, witness=None):
        additions = frozenset(additions)
        if not additions:
            raise AssertionError("atomic actions must add at least one voxel")
        entry = actions.setdefault(
            additions,
            {"additions": serial_points(additions), "roles": set(), "witnesses": []},
        )
        entry["roles"].add(role)
        if witness is not None:
            entry["witnesses"].append(witness)

    for v in valid_single_add_repairs(state):
        record({v}, "N1", {"repair_voxel": v})

    for certificate in component_certificates(state):
        bridge_actions, _ = certificate_bridge_actions(state, certificate)
        for bridge_action in bridge_actions:
            record(
                {tuple(point) for point in bridge_action["additions"]},
                "N2",
                {
                    "certificate": tuple(
                        tuple(sorted(component)) for component in certificate
                    ),
                    "realization_count": len(bridge_action["realizations"]),
                },
            )

    output = []
    for entry in actions.values():
        entry["roles"] = tuple(sorted(entry["roles"]))
        entry["witnesses"].sort(key=lambda witness: json.dumps(witness, sort_keys=True))
        output.append(entry)
    return tuple(sorted(output, key=lambda action: action["additions"]))


def first_action_type(roles):
    roles = set(roles)
    if roles == {"N1", "N2"}:
        return "DUAL_ROLE"
    if roles == {"N1"}:
        return "N1_ONLY"
    if roles == {"N2"}:
        return "N2_ONLY"
    raise AssertionError(f"unexpected roles: {roles}")


def preserves_all_current_N2(state, action):
    """Immediate-obligation-preservation predicate P_preserve."""
    state = frozenset(state)
    successor = state | {tuple(point) for point in action["additions"]}
    after_components = components6(successor)
    records = []
    for certificate in component_certificates(state):
        left = descendant(certificate[0], after_components)
        right = descendant(certificate[1], after_components)
        resolved = left == right
        bridgeable = None
        if not resolved:
            bridgeable, _ = component_bridge_exists(
                successor, left, right, crosscheck=True
            )
        records.append(
            {
                "certificate": tuple(
                    tuple(sorted(component)) for component in certificate
                ),
                "resolved": resolved,
                "bridgeable": bridgeable,
                "viable": resolved or bridgeable,
            }
        )
    return all(record["viable"] for record in records), records


def shortest_atomic_plans(start, max_depth=8):
    """Breadth-first enumeration of distinct addition-set sequences."""
    start = frozenset(start)
    if goal(start):
        return 0, (tuple(),), {"states_expanded": 0, "transitions": 0}

    frontier = ((start, tuple()),)
    states_expanded = 0
    transitions = 0
    for depth in range(1, max_depth + 1):
        next_frontier = []
        goals = {}
        seen_sequences = set()
        for state, schedule in frontier:
            states_expanded += 1
            for action in atomic_actions(state):
                transitions += 1
                additions = tuple(tuple(point) for point in action["additions"])
                action_key = additions
                schedule_key = tuple(step["additions"] for step in schedule) + (action_key,)
                if schedule_key in seen_sequences:
                    continue
                seen_sequences.add(schedule_key)
                successor = frozenset(set(state) | set(additions))
                assert successor != state
                assert not has_fail(successor)
                step = {
                    "additions": additions,
                    "roles": action["roles"],
                    "type": first_action_type(action["roles"]),
                    "successor_component_count": len(components6(successor)),
                }
                next_schedule = schedule + (step,)
                if goal(successor):
                    goals[schedule_key] = next_schedule
                else:
                    next_frontier.append((successor, next_schedule))
        if goals:
            ordered = tuple(goals[key] for key in sorted(goals))
            return depth, ordered, {
                "states_expanded": states_expanded,
                "transitions": transitions,
            }
        frontier = tuple(next_frontier)
        if not frontier:
            return None, tuple(), {
                "states_expanded": states_expanded,
                "transitions": transitions,
            }
    return None, tuple(), {
        "states_expanded": states_expanded,
        "transitions": transitions,
        "depth_cap_reached": True,
    }


def signed_permutations(point):
    for permutation in itertools.permutations(range(3)):
        for signs in itertools.product((-1, 1), repeat=3):
            yield tuple(signs[a] * point[permutation[a]] for a in range(3))


def canonical_isometry_class(points):
    """Canonicalize under translations and the 48 signed axis permutations."""
    points = tuple(points)
    images = []
    for permutation in itertools.permutations(range(3)):
        for signs in itertools.product((-1, 1), repeat=3):
            transformed = [
                tuple(signs[a] * point[permutation[a]] for a in range(3))
                for point in points
            ]
            minima = tuple(min(point[a] for point in transformed) for a in range(3))
            normalized = tuple(
                sorted(
                    tuple(point[a] - minima[a] for a in range(3))
                    for point in transformed
                )
            )
            images.append(normalized)
    return min(images)


def audit_witness(X, index):
    X = frozenset(X)
    actions = atomic_actions(X)
    preserving = []
    action_policy_records = []
    for action in actions:
        allowed, obligations = preserves_all_current_N2(X, action)
        if allowed:
            preserving.append(action)
        action_policy_records.append(
            {
                "additions": action["additions"],
                "roles": action["roles"],
                "preserves_all_current_N2": allowed,
                "obligations": obligations,
            }
        )

    depth, plans, search_stats = shortest_atomic_plans(X)
    first_types = Counter(plan[0]["type"] for plan in plans) if plans else Counter()
    distinct_first_actions = {
        tuple(tuple(point) for point in plan[0]["additions"])
        for plan in plans
    }
    return {
        "index": index,
        "X": serial_points(X),
        "size": len(X),
        "component_count": len(components6(X)),
        "valid_N1_action_count": len(valid_single_add_repairs(X)),
        "atomic_first_action_count": len(actions),
        "immediate_preserving_first_action_count": len(preserving),
        "shortest_plan_depth": depth,
        "shortest_plan_count": len(plans),
        "shortest_distinct_first_action_count": len(distinct_first_actions),
        "shortest_first_action_types": dict(sorted(first_types.items())),
        "shortest_plans": plans,
        "search_stats": search_stats,
        "first_action_policy_audit": action_policy_records,
        "orbit_key": canonical_isometry_class(X),
    }


def main():
    source = D3E / "c07d3e4_pair_lift_search.json"
    d3e4 = json.loads(source.read_text(encoding="utf-8"))
    witnesses = []
    seen = set()
    for record in d3e4["full_counterexamples"]:
        X = frozenset(tuple(point) for point in record["X"])
        if X not in seen:
            seen.add(X)
            witnesses.append(X)
    witnesses.sort(key=serial_points)
    assert len(witnesses) == 24

    audits = [audit_witness(X, index) for index, X in enumerate(witnesses)]

    orbit_members = defaultdict(list)
    for audit in audits:
        orbit_members[tuple(audit["orbit_key"])].append(audit)
    orbit_records = []
    for orbit_index, (key, members) in enumerate(sorted(orbit_members.items())):
        metric_profiles = {
            (
                member["size"],
                member["valid_N1_action_count"],
                member["shortest_plan_depth"],
                member["shortest_plan_count"],
                tuple(member["shortest_first_action_types"].items()),
                member["immediate_preserving_first_action_count"],
            )
            for member in members
        }
        orbit_records.append(
            {
                "orbit": orbit_index,
                "canonical_X": key,
                "member_count": len(members),
                "member_indices": tuple(member["index"] for member in members),
                "metric_profiles": tuple(sorted(metric_profiles)),
            }
        )

    depths = Counter(audit["shortest_plan_depth"] for audit in audits)
    plan_counts = Counter(audit["shortest_plan_count"] for audit in audits)
    assert set(depths) == {2}
    assert all(audit["valid_N1_action_count"] == 2 for audit in audits)
    assert all(audit["atomic_first_action_count"] == 8 for audit in audits)
    assert all(audit["shortest_plan_count"] == 8 for audit in audits)
    assert all(audit["shortest_distinct_first_action_count"] == 2 for audit in audits)
    assert all(
        audit["shortest_first_action_types"] == {"DUAL_ROLE": 8}
        for audit in audits
    )
    assert all(
        audit["immediate_preserving_first_action_count"] == 0
        for audit in audits
    )

    result = {
        "semantics": {
            "state": "finite voxel set X",
            "A_atom": "set union of A_N1^(1)(X) and compatible shortest A_N2(X), deduplicated by addition set",
            "roles_are_nonexclusive": True,
            "transition": "X -> X union additions; recompute certificates and actions",
            "goal": "has_fail(X)=False and number_of_6_components(X)=1",
        },
        "source_full_counterexample_count": len(witnesses),
        "isometry_orbit_count": len(orbit_records),
        "orbits": orbit_records,
        "depth_distribution": dict(sorted(depths.items())),
        "shortest_plan_count_distribution": dict(sorted(plan_counts.items())),
        "all_known_greedy_counterexamples_depth_2": True,
        "all_shortest_first_actions_dual_role": True,
        "all_immediate_preservation_action_sets_empty": True,
        "atomic_goal_unreachable_count": sum(
            audit["shortest_plan_depth"] is None for audit in audits
        ),
        "witnesses": audits,
        "verdict": {
            "D5A_atomic_semantics": "FROZEN",
            "D5B_immediate_obligation_preservation_complete": False,
            "D5C_known_family_max_shortest_depth": 2,
            "macro_primitive_required_by_known_family": False,
            "universal_bounded_depth_claim": "OPEN",
        },
    }
    output = HERE / "c07d5_atomic_planning_census_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D5 atomic planning census: ALL CHECKS PASSED")
    print("full counterexamples:", len(witnesses))
    print("isometry orbits:", len(orbit_records))
    print("depth distribution:", dict(depths))
    print("shortest-plan count distribution:", dict(plan_counts))
    print("all shortest first actions: DUAL_ROLE")
    print("P_preserve allowed first actions: 0 for every witness")
    print("atomic-unreachable witnesses: 0")
    print("JSON:", output)


if __name__ == "__main__":
    main()
