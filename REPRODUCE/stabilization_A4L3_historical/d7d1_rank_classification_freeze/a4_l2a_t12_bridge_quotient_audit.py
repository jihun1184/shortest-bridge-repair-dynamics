"""A4-L2a(ii): isolated-satellite bridge-quotient certificate.

This is the expensive audit.  It enumerates the union of the k=9 N2
descendant closures of the 22 formal T12 candidates once, rather than
recomputing a separate recursive closure per class.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
CHECKPOINT_ROOT = HERE.parent
WORK = CHECKPOINT_ROOT / "work" / "d7c_pkg" / "c07d7c_package" / "work"
for dependency in (
    HERE,
    CHECKPOINT_ROOT / "work" / "d7d1",
    WORK / "c07d3e",
    WORK / "c07d5",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

from a4_l1b_formal_geometry_audit import decode_points  # noqa: E402
from a4_l2a_connected_inert_tail_audit import (  # noqa: E402
    class_data,
    formal_candidate,
    labeled_actions,
    root_components,
    stable_encode,
)
from c07d3e_component_viability import components6, shortest_endpoint_pairs  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402
import c07d7d1_persistent_absorption_closure as m  # noqa: E402

SOURCE = HERE / "a4_l1a_signature_table_results.json"
OUTPUT = HERE / "a4_l2a_t12_bridge_quotient_results.json"
BASE_K = 9
COMPARISON_K = 6


def digest_key(value):
    return hashlib.sha256(stable_encode(value).encode("utf-8")).hexdigest()


def satellite_component(state, satellite, components=None):
    components = components if components is not None else components6(state)
    return next(component for component in components if satellite in component)


def enumerate_union_closure(starts, k):
    satellite = (-k, 2, 0)
    root_components_ = root_components(k)
    queue = deque(starts)
    seen = set(starts)
    successors = {}
    component_cache = {}
    invalid_states = []
    endpoint_violations = []
    action_support_violations = []
    started = time.time()

    while queue:
        state = queue.popleft()
        if has_fail(state):
            invalid_states.append(tuple(sorted(state)))
            break
        comps = components6(state)
        component_cache[state] = comps
        sat_comp = satellite_component(state, satellite, comps)
        is_connected_satellite = len(sat_comp) > 1

        if is_connected_satellite:
            for other in comps:
                if other == sat_comp:
                    continue
                _, pairs = shortest_endpoint_pairs(sat_comp, other)
                bad = [(s, t) for s, t in pairs if s[0] < -7]
                if bad:
                    endpoint_violations.append(
                        {
                            "state_size": len(state),
                            "examples": [[list(s), list(t)] for s, t in bad[:5]],
                        }
                    )
                    break

        actions = labeled_actions(state, root_components_)
        successors[state] = actions
        if is_connected_satellite:
            for _, _, additions in actions:
                bad = [point for point in additions if point[0] < -6]
                if bad:
                    action_support_violations.append(
                        {
                            "state_size": len(state),
                            "examples": [list(point) for point in bad[:5]],
                        }
                    )
                    break

        for successor, _, _ in actions:
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)

        if len(seen) % 20000 == 0:
            print(
                f"  closure progress: discovered={len(seen)}, queued={len(queue)}",
                flush=True,
            )

    return {
        "states": tuple(seen),
        "successors": successors,
        "components": component_cache,
        "root_components": root_components_,
        "satellite": satellite,
        "invalid_states": invalid_states,
        "endpoint_violations": endpoint_violations,
        "action_support_violations": action_support_violations,
        "elapsed_seconds": time.time() - started,
    }


def exact_c3(states, successors, component_cache, root_components_):
    keys = {}
    for state in states:
        actions = successors[state]
        keys[state] = (
            len(component_cache[state]),
            max((rho for _, rho, _ in actions), default=0),
            m.root_identity_partition(state, root_components_),
        )
    for _ in range(3):
        previous = keys
        keys = {
            state: (
                previous[state],
                frozenset(
                    (rho, previous[successor])
                    for successor, rho, _ in successors[state]
                ),
            )
            for state in states
        }
    return keys


def classify_actions(state, satellite, actions, component_cache, front_min_x=-5):
    fixed = []
    satellite_actions = []
    for successor, rho, additions in actions:
        comps = component_cache.get(successor)
        if comps is None:
            comps = components6(successor)
        sat_comp = satellite_component(successor, satellite, comps)
        if len(sat_comp) == 1:
            fixed.append((successor, rho, additions))
        else:
            front = frozenset(
                point for point in successor if point[0] >= front_min_x
            )
            satellite_actions.append((successor, rho, additions, front))
    return fixed, satellite_actions


def action_quotients_for_background(background, k, root_components_):
    satellite = (-k, 2, 0)
    state = frozenset(background | {satellite})
    fixed, satellite_actions = classify_actions(
        state, satellite, labeled_actions(state, root_components_), {}
    )
    fixed_keys = frozenset((rho, additions) for _, rho, additions in fixed)
    satellite_fronts = frozenset(
        (rho, front) for _, rho, _, front in satellite_actions
    )
    target_endpoints = target_endpoint_sets(background, satellite)
    return {
        "raw_action_count": len(fixed) + len(satellite_actions),
        "raw_satellite_action_count": len(satellite_actions),
        "fixed_keys": fixed_keys,
        "satellite_fronts": satellite_fronts,
        "target_endpoint_sets": target_endpoints,
    }


def target_endpoint_sets(background, satellite):
    target_endpoints = set()
    for component in components6(background):
        _, pairs = shortest_endpoint_pairs(frozenset((satellite,)), component)
        target_endpoints.add(tuple(sorted(target for _, target in pairs)))
    return frozenset(target_endpoints)


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    templates = {row["template_id"]: row for row in source["templates"]}
    t12_rows = [
        row for row in source["classes"] if row["selected_template_id"] == "T12"
    ]
    connected_digests = {
        row["behavioral_key_sha256"]
        for row in source["classes"]
        if row["selected_template_id"] != "T12"
    }

    starts = []
    row_by_start = {}
    for row in t12_rows:
        template, law_name, length_at = class_data(source, row, templates)
        if law_name != "0":
            raise AssertionError(f"nonzero law in T12 row {row['class_id']}")
        start, satellite, sat_component = formal_candidate(
            row, template, length_at, BASE_K
        )
        if sat_component != frozenset((satellite,)):
            raise AssertionError(f"non-isolated T12 row {row['class_id']}")
        starts.append(start)
        row_by_start[start] = row

    print(f"building union descendant closure from {len(starts)} T12 starts...", flush=True)
    closure = enumerate_union_closure(starts, BASE_K)
    states = closure["states"]
    successors = closure["successors"]
    component_cache = closure["components"]
    satellite = closure["satellite"]
    print(
        f"  closure done: states={len(states)}, edges="
        f"{sum(len(value) for value in successors.values())}, "
        f"elapsed={closure['elapsed_seconds']:.1f}s",
        flush=True,
    )

    keys = exact_c3(
        states, successors, component_cache, closure["root_components"]
    )
    digests = {state: digest_key(key) for state, key in keys.items()}
    frozen_matches = sum(
        digests[start] == row_by_start[start]["behavioral_key_sha256"]
        for start in starts
    )

    isolated_states = []
    connected_states = []
    isolated_layers = Counter()
    fixed_edges = 0
    satellite_edges = 0
    bad_fixed_successor_types = []
    bad_connected_successor_digests = []
    front_to_digests = defaultdict(set)

    for state in states:
        comps = component_cache[state]
        sat_comp = satellite_component(state, satellite, comps)
        if len(sat_comp) == 1:
            isolated_states.append(state)
            isolated_layers[len(comps)] += 1
            fixed, satellite_actions = classify_actions(
                state,
                satellite,
                successors[state],
                component_cache,
                front_min_x=-8,
            )
            fixed_edges += len(fixed)
            satellite_edges += len(satellite_actions)
            for successor, _, _ in fixed:
                successor_sat = satellite_component(
                    successor, satellite, component_cache[successor]
                )
                if len(successor_sat) != 1 or len(component_cache[successor]) >= len(comps):
                    bad_fixed_successor_types.append(len(state))
            for successor, rho, _, front in satellite_actions:
                digest = digests[successor]
                front_to_digests[(rho, front)].add(digest)
                if digest not in connected_digests:
                    bad_connected_successor_digests.append(digest)
        else:
            connected_states.append(state)

    front_nonfunctional = [
        {"rho": key[0], "digest_count": len(values)}
        for key, values in front_to_digests.items()
        if len(values) != 1
    ]

    # The isolated fixed backgrounds are k-independent.  Compare their exact
    # fixed-fixed actions, minimizing target endpoints, and satellite-action
    # active-front quotient between k=6 and k=9.
    root6 = root_components(COMPARISON_K)
    background_mismatches = []
    raw_counts = {
        str(COMPARISON_K): {"all": 0, "satellite": 0},
        str(BASE_K): {"all": 0, "satellite": 0},
    }
    quotient_front_count = 0
    for index, state9 in enumerate(isolated_states, 1):
        background = frozenset(state9 - {satellite})
        q6 = action_quotients_for_background(background, COMPARISON_K, root6)

        # Compatibility with the fixed background depends only on x>=-5.
        # The finer x>=-8 front is used above for the connected-successor
        # lifting quotient; the two roles must not be conflated.
        fixed9, sat9 = classify_actions(
            state9, satellite, successors[state9], component_cache
        )
        q9 = {
            "raw_action_count": len(fixed9) + len(sat9),
            "raw_satellite_action_count": len(sat9),
            "fixed_keys": frozenset((rho, additions) for _, rho, additions in fixed9),
            "satellite_fronts": frozenset((rho, front) for _, rho, _, front in sat9),
            "target_endpoint_sets": target_endpoint_sets(background, satellite),
        }
        for k, quotient in ((COMPARISON_K, q6), (BASE_K, q9)):
            raw_counts[str(k)]["all"] += quotient["raw_action_count"]
            raw_counts[str(k)]["satellite"] += quotient["raw_satellite_action_count"]
        quotient_front_count += len(q9["satellite_fronts"])

        checks = {
            "fixed_actions_equal": q6["fixed_keys"] == q9["fixed_keys"],
            "target_endpoints_equal": (
                q6["target_endpoint_sets"] == q9["target_endpoint_sets"]
            ),
            "satellite_front_quotient_equal": (
                q6["satellite_fronts"] == q9["satellite_fronts"]
            ),
        }
        if not all(checks.values()):
            background_mismatches.append({"index": index, "checks": checks})
        if index % 100 == 0:
            print(f"  compared isolated backgrounds: {index}/{len(isolated_states)}", flush=True)

    isolated_class_layers = Counter()
    for state in isolated_states:
        isolated_class_layers[(len(component_cache[state]), digests[state])] += 1
    distinct_classes_by_layer = Counter(
        component_count for component_count, _ in isolated_class_layers
    )

    failures = {
        "invalid_states": closure["invalid_states"],
        "remote_endpoint_violations": closure["endpoint_violations"],
        "remote_action_support_violations": closure["action_support_violations"],
        "fixed_successor_type_failures": bad_fixed_successor_types,
        "connected_successor_digest_failures": bad_connected_successor_digests,
        "front_nonfunctional": front_nonfunctional,
        "background_quotient_mismatches": background_mismatches,
    }

    result = {
        "scope": (
            "A4-L2a(ii) T12 bridge-quotient finite base certificate at k=9; "
            "closure union plus k=6/k=9 active-front comparison"
        ),
        "claim_boundary": (
            "Supports the parametric bridge-quotient and induction proof. "
            "Does not establish root reachability or all-k exhaustiveness."
        ),
        "base_k": BASE_K,
        "comparison_k": COMPARISON_K,
        "t12_formal_classes": len(t12_rows),
        "frozen_c3_sha_matches": frozen_matches,
        "union_descendant_states": len(states),
        "union_action_edges": sum(len(value) for value in successors.values()),
        "isolated_states": len(isolated_states),
        "connected_states": len(connected_states),
        "isolated_state_component_layers": dict(sorted(isolated_layers.items())),
        "isolated_behavioral_classes_by_component_layer": dict(
            sorted(distinct_classes_by_layer.items())
        ),
        "fixed_fixed_edges": fixed_edges,
        "satellite_absorbing_edges": satellite_edges,
        "raw_action_counts": raw_counts,
        "satellite_active_front_occurrences": quotient_front_count,
        "distinct_rho_front_quotients": len(front_to_digests),
        "compatibility_front_min_x": -5,
        "connected_lift_front_min_x": -8,
        "connected_endpoint_support_min_x": -7,
        "connected_action_support_min_x": -6,
        "failures": failures,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    nonempty_failures = {key: value for key, value in failures.items() if value}
    expected_layers = {2: 1, 3: 7, 4: 13, 5: 1}
    if nonempty_failures:
        raise AssertionError(
            f"A4-L2a(ii) audit failures: {list(nonempty_failures)}; see {OUTPUT}"
        )
    if len(t12_rows) != 22 or frozen_matches != 22:
        raise AssertionError("expected 22 T12 classes and 22 frozen SHA matches")
    if dict(distinct_classes_by_layer) != expected_layers:
        raise AssertionError(
            f"unexpected isolated quotient layers: {dict(distinct_classes_by_layer)}"
        )

    summary = {key: value for key, value in result.items() if key != "failures"}
    summary["failure_counts"] = {key: len(value) for key, value in failures.items()}
    print(json.dumps(summary, indent=2))
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
