"""C07-D4A--D4C: coordinated planning census for the canonical D3E witness."""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
D3E = HERE.parent / "c07d3e"
D3B = HERE.parent / "c07d3b"
sys.path.insert(0, str(D3E))
sys.path.insert(0, str(D3B / "c07a_scripts"))

from automaton_c06c2 import gen_all_monotone_paths  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402

from c07d3e1_targeted_search import valid_single_add_repairs  # noqa: E402
from c07d3e5_counterexample_verify import V1, V2, X  # noqa: E402
from c07d3e_component_viability import (  # noqa: E402
    component_bridge_exists,
    component_certificates,
    components6,
    descendant,
    shortest_endpoint_pairs,
)


def serial_component(component):
    return tuple(sorted(component))


def serial_certificate(certificate):
    return tuple(serial_component(component) for component in certificate)


def stable_bridge_audit(bridge):
    """Strip traversal-order counters; retain deterministic decision evidence."""
    if bridge is None:
        return None
    endpoint_pairs = []
    for record in bridge["endpoint_pairs"]:
        stable = {
            "s": record["s"],
            "t": record["t"],
            "distance": record["distance"],
            "compressed": record["compressed"],
        }
        for key in ("brute", "total", "compatible"):
            if key in record:
                stable[key] = record[key]
        endpoint_pairs.append(stable)
    return {
        "distance": bridge["distance"],
        "new_voxel_cost": bridge["new_voxel_cost"],
        "endpoint_pair_count": bridge["endpoint_pair_count"],
        "endpoint_pairs": endpoint_pairs,
    }


def certificate_bridge_actions(state, certificate):
    """All distinct compatible d6-optimal addition sets for one certificate."""
    state = frozenset(state)
    distance, endpoint_pairs = shortest_endpoint_pairs(*certificate)
    by_additions = {}
    ordering_count = 0
    compatible_ordering_count = 0
    for s, t in endpoint_pairs:
        for path in gen_all_monotone_paths(s, t):
            ordering_count += 1
            successor = state | set(path)
            if has_fail(successor):
                continue
            compatible_ordering_count += 1
            additions = frozenset(set(path) - set(state))
            by_additions.setdefault(
                additions,
                {"additions": tuple(sorted(additions)), "realizations": []},
            )["realizations"].append({"s": s, "t": t, "path": path})
    actions = []
    for action in by_additions.values():
        action["realizations"].sort(
            key=lambda realization: (
                realization["s"], realization["t"], realization["path"]
            )
        )
        actions.append(action)
    return tuple(sorted(actions, key=lambda action: action["additions"])), {
        "distance": distance,
        "endpoint_pair_count": len(endpoint_pairs),
        "ordering_count": ordering_count,
        "compatible_ordering_count": compatible_ordering_count,
        "distinct_action_count": len(by_additions),
    }


def state_audit(state, *, enumerate_actions=False):
    state = frozenset(state)
    components = components6(state)
    certificate_records = []
    for certificate in component_certificates(state):
        exists, bridge = component_bridge_exists(state, *certificate, crosscheck=True)
        record = {
            "certificate": serial_certificate(certificate),
            "bridge_exists": exists,
            "bridge": stable_bridge_audit(bridge),
        }
        if enumerate_actions:
            actions, action_stats = certificate_bridge_actions(state, certificate)
            assert bool(actions) == exists
            record.update(actions=actions, action_stats=action_stats)
        certificate_records.append(record)
    return {
        "state": tuple(sorted(state)),
        "size": len(state),
        "has_fail": has_fail(state),
        "components": tuple(serial_component(component) for component in components),
        "component_count": len(components),
        "certificate_count": len(certificate_records),
        "bridgeable_certificate_count": sum(
            record["bridge_exists"] for record in certificate_records
        ),
        "all_certificates_bridgeable": all(
            record["bridge_exists"] for record in certificate_records
        ),
        "valid_N1c_single_add_repairs": valid_single_add_repairs(state),
        "certificates": certificate_records,
    }


def old_certificate_viability_after_macro(X, additions):
    after = frozenset(set(X) | set(additions))
    after_components = components6(after)
    records = []
    for certificate in component_certificates(X):
        left = descendant(certificate[0], after_components)
        right = descendant(certificate[1], after_components)
        resolved = left == right
        bridge_exists = None
        bridge = None
        if not resolved:
            bridge_exists, bridge = component_bridge_exists(
                after, left, right, crosscheck=True
            )
        records.append(
            {
                "certificate": serial_certificate(certificate),
                "resolved": resolved,
                "left_descendant": serial_component(left),
                "right_descendant": serial_component(right),
                "bridge_exists": bridge_exists,
                "viable": resolved or bridge_exists,
                "bridge": stable_bridge_audit(bridge),
            }
        )
    return records


def n2_first_bfs(start):
    """Enumerate all reachable compatible shortest-bridge states to connectivity."""
    start = frozenset(start)
    queue = deque([(start, tuple())])
    best_depth = {start: 0}
    first_successors = {}
    goals = []
    transitions = 0
    while queue:
        state, schedule = queue.popleft()
        components = components6(state)
        if len(components) == 1 and not has_fail(state):
            goals.append({"state": tuple(sorted(state)), "schedule": schedule})
            continue
        for certificate in component_certificates(state):
            actions, _ = certificate_bridge_actions(state, certificate)
            for action in actions:
                additions = frozenset(tuple(point) for point in action["additions"])
                successor = frozenset(set(state) | set(additions))
                assert not has_fail(successor)
                assert len(components6(successor)) < len(components)
                transitions += 1
                step = {
                    "certificate": serial_certificate(certificate),
                    "additions": tuple(sorted(additions)),
                    "successor_component_count": len(components6(successor)),
                }
                next_schedule = schedule + (step,)
                if not schedule:
                    first_successors.setdefault(
                        successor,
                        {
                            "state": tuple(sorted(successor)),
                            "first_steps": [],
                            "has_fail": has_fail(successor),
                            "valid_N1c_single_add_repairs": valid_single_add_repairs(successor),
                            "v1_globally_safe_addition": not has_fail(set(successor) | {V1}),
                            "v2_globally_safe_addition": not has_fail(set(successor) | {V2}),
                        },
                    )["first_steps"].append(step)
                depth = len(next_schedule)
                if depth < best_depth.get(successor, 10**9):
                    best_depth[successor] = depth
                    queue.append((successor, next_schedule))
    minimum = min((len(goal["schedule"]) for goal in goals), default=None)
    shortest_goals = [goal for goal in goals if len(goal["schedule"]) == minimum]
    return {
        "reachable_state_count": len(best_depth),
        "transition_realizations_examined": transitions,
        "first_successor_count": len(first_successors),
        "first_successors": tuple(first_successors.values()),
        "connected_goal_count": len(goals),
        "minimum_bridge_action_depth": minimum,
        "shortest_connected_schedules": shortest_goals,
    }


def main():
    X1 = X | {V1}
    X2 = X | {V2}
    X12 = X | {V1, V2}

    initial = state_audit(X, enumerate_actions=True)
    after_v1 = state_audit(X1)
    after_v2 = state_audit(X2)
    simultaneous = state_audit(X12)

    assert initial["valid_N1c_single_add_repairs"] == (V1, V2)
    assert not after_v1["has_fail"] and not after_v2["has_fail"]
    assert after_v1["valid_N1c_single_add_repairs"] == ()
    assert after_v2["valid_N1c_single_add_repairs"] == ()
    assert not simultaneous["has_fail"]
    assert simultaneous["all_certificates_bridgeable"]

    ordered = {
        "v1_then_v2": {
            "first_is_N1c_repair": V1 in initial["valid_N1c_single_add_repairs"],
            "second_is_recomputed_N1c_repair": V2 in after_v1["valid_N1c_single_add_repairs"],
            "second_is_globally_safe_addition": not has_fail(X12),
            "final_state": simultaneous,
        },
        "v2_then_v1": {
            "first_is_N1c_repair": V2 in initial["valid_N1c_single_add_repairs"],
            "second_is_recomputed_N1c_repair": V1 in after_v2["valid_N1c_single_add_repairs"],
            "second_is_globally_safe_addition": not has_fail(X12),
            "final_state": simultaneous,
        },
    }
    assert not ordered["v1_then_v2"]["second_is_recomputed_N1c_repair"]
    assert not ordered["v2_then_v1"]["second_is_recomputed_N1c_repair"]

    macro_old_obligations = old_certificate_viability_after_macro(X, {V1, V2})
    assert all(record["viable"] for record in macro_old_obligations)

    n2_first = n2_first_bfs(X)
    assert n2_first["first_successor_count"] > 0
    assert n2_first["connected_goal_count"] > 0
    assert all(
        successor["valid_N1c_single_add_repairs"] == ()
        for successor in n2_first["first_successors"]
    )

    # Determine which first bridge choices themselves admit a continuation.
    completable_first_successors = 0
    dual_role_completable = 0
    threatened_certificate_first_dead_ends = 0
    for successor in n2_first["first_successors"]:
        state = frozenset(tuple(point) for point in successor["state"])
        continuation = n2_first_bfs(state)
        first_additions = {
            tuple(point) for point in successor["first_steps"][0]["additions"]
        }
        dual_role = first_additions in ({V1}, {V2})
        successor["remaining_certificate_bridgeability"] = tuple(
            component_bridge_exists(state, *certificate, crosscheck=True)[0]
            for certificate in component_certificates(state)
        )
        successor["completion_exists"] = continuation["connected_goal_count"] > 0
        successor["minimum_additional_bridge_depth"] = continuation[
            "minimum_bridge_action_depth"
        ]
        successor["dual_role_N1_and_N2_first_action"] = dual_role
        if successor["completion_exists"]:
            completable_first_successors += 1
            dual_role_completable += dual_role
        elif len(first_additions) == 3:
            threatened_certificate_first_dead_ends += 1
    assert completable_first_successors == 2
    assert dual_role_completable == 2
    assert threatened_certificate_first_dead_ends == 6

    post_pair_macro = n2_first_bfs(X12)
    assert post_pair_macro["minimum_bridge_action_depth"] == 1

    result = {
        "D4A": {
            "initial": initial,
            "after_v1": after_v1,
            "after_v2": after_v2,
            "simultaneous_pair_macro": simultaneous,
            "old_certificate_viability_after_pair_macro": macro_old_obligations,
            "ordered_N1": ordered,
        },
        "D4B": {
            **n2_first,
            "completable_first_successor_count": completable_first_successors,
            "dual_role_completable_first_successor_count": dual_role_completable,
            "three_voxel_first_bridge_dead_end_count": threatened_certificate_first_dead_ends,
            "post_pair_macro_N2_completion": post_pair_macro,
        },
        "D4C": {
            "PAIR_MACRO": True,
            "ORDERED_N1": False,
            "N2_FIRST_broad_definition": True,
            "N2_FIRST_threatened_certificate_first": False,
            "DUAL_ROLE_N1_N2_THEN_N2": True,
            "DEEPER_PLANNING": False,
            "classification_note": (
                "The proposed labels are not mutually exclusive. PAIR_MACRO solves "
                "the immediate N1 selection obstruction. A two-step bridge schedule "
                "also reaches connectivity, but its only completable first actions are "
                "v1 or v2 acting dually as an N1 repair and a one-voxel N2 bridge; "
                "bridging either threatened D3E certificate first is a dead end."
            ),
        },
    }
    output = HERE / "c07d4_planning_census_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D4 coordinated planning census: ALL CHECKS PASSED")
    print("X12 fail/components/bridgeable certs:", simultaneous["has_fail"], simultaneous["component_count"], f"{simultaneous['bridgeable_certificate_count']}/{simultaneous['certificate_count']}")
    print("ordered N1 second-step admissible:", False, False)
    print("initial bridgeable certificates:", f"{initial['bridgeable_certificate_count']}/{initial['certificate_count']}")
    print("N2-first successor states:", n2_first["first_successor_count"])
    print("N2-first connected goals/min depth:", n2_first["connected_goal_count"], n2_first["minimum_bridge_action_depth"])
    print("completable/dead-end first bridges:", completable_first_successors, threatened_certificate_first_dead_ends)
    print("post-pair-macro N2 completion depth:", post_pair_macro["minimum_bridge_action_depth"])
    print("classification: PAIR_MACRO + DUAL_ROLE_N1_N2_THEN_N2; ORDERED_N1=False")
    print("JSON:", output)


if __name__ == "__main__":
    main()
