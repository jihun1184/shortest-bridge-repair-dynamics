"""A4-L2a(i): connected-satellite inert-tail audit.

This is a finite hypothesis audit for the structural lifting proof in
D7D2-A4-L2a_connected_inert_tail_persistence.md.  It does NOT enumerate a
new root closure.  It starts from the 31 non-T12 formal candidates at k=8,
enumerates only their descendant N2 closures, verifies that the moving
left tail is semantically inert there, and independently checks the frozen
c3 behavioral-key SHA at the first unseen level k=9.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

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

from a4_l1b_formal_geometry_audit import (  # noqa: E402
    CORE,
    REPAIR,
    build_satellite,
    decode_points,
    infer_law,
)
from c07d3e_component_viability import components6, shortest_endpoint_pairs  # noqa: E402
from c07d5_atomic_planning_census import atomic_actions  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402
import c07d7d1_persistent_absorption_closure as m  # noqa: E402

SOURCE = HERE / "a4_l1a_signature_table_results.json"
OUTPUT = HERE / "a4_l2a_connected_inert_tail_results.json"


def stable_encode(value):
    if isinstance(value, tuple):
        return "(" + ",".join(stable_encode(item) for item in value) + ")"
    if isinstance(value, frozenset):
        return "{" + ",".join(sorted(stable_encode(item) for item in value)) + "}"
    if isinstance(value, int):
        return str(value)
    if value is None:
        return "null"
    raise TypeError(type(value))


def class_data(source, row, templates):
    template = templates[row["selected_template_id"]]
    lengths = {
        str(k): row["selected_template_witnesses"][str(k)]["corridor_length"]
        for k in (6, 7, 8)
    }
    law_name, length_at, _ = infer_law(lengths)
    return template, law_name, length_at


def formal_candidate(row, template, length_at, k):
    satellite, _, _, sat_component = build_satellite(template, k, length_at(k))
    return decode_points(row["fixed_remainder"]) | sat_component, satellite, sat_component


def root_components(k):
    satellite = (-k, 2, 0)
    return components6(frozenset(CORE | {satellite, REPAIR}))


def labeled_actions(state, root_components_):
    before = m.root_identity_partition(state, root_components_)
    out = []
    for action in atomic_actions(state):
        if set(action["roles"]) != {"N2"}:
            raise AssertionError(f"non-N2 action in frozen descendant semantics: {action['roles']}")
        additions = frozenset(tuple(point) for point in action["additions"])
        successor = state | additions
        after = m.root_identity_partition(successor, root_components_)
        rho = len(m.absorption_block(before, after))
        out.append((successor, rho, additions))
    return out


def descendant_inert_audit(start, satellite, active_x_min, root_components_):
    stack = [start]
    seen = {start}
    edge_count = 0
    failures = []
    while stack:
        state = stack.pop()
        if has_fail(state):
            failures.append({"type": "state_has_fail", "state_size": len(state)})
            break
        comps = components6(state)
        sat_comp = next(component for component in comps if satellite in component)
        for other in comps:
            if other == sat_comp:
                continue
            _, pairs = shortest_endpoint_pairs(sat_comp, other)
            bad = [(s, t) for s, t in pairs if s[0] < active_x_min]
            if bad:
                failures.append(
                    {
                        "type": "remote_shortest_endpoint",
                        "state_size": len(state),
                        "active_x_min": active_x_min,
                        "examples": [[list(s), list(t)] for s, t in bad[:5]],
                    }
                )
                break
        if failures:
            break
        for successor, _, additions in labeled_actions(state, root_components_):
            edge_count += 1
            if additions and min(point[0] for point in additions) < active_x_min:
                failures.append(
                    {
                        "type": "remote_action_support",
                        "state_size": len(state),
                        "active_x_min": active_x_min,
                        "min_addition_x": min(point[0] for point in additions),
                    }
                )
                break
            if successor not in seen:
                seen.add(successor)
                stack.append(successor)
        if failures:
            break
    return len(seen), edge_count, failures


def c3_key(start, k):
    rc = root_components(k)
    action_cache = {}
    c0_cache = {}
    memo = {}

    def actions(state):
        if state not in action_cache:
            action_cache[state] = [
                (successor, rho)
                for successor, rho, _ in labeled_actions(state, rc)
            ]
        return action_cache[state]

    def c0(state):
        if state not in c0_cache:
            acts = actions(state)
            c0_cache[state] = (
                len(components6(state)),
                max((rho for _, rho in acts), default=0),
                m.root_identity_partition(state, rc),
            )
        return c0_cache[state]

    def refine(state, round_index):
        key = (state, round_index)
        if key in memo:
            return memo[key]
        if round_index == 0:
            value = c0(state)
        else:
            value = (
                refine(state, round_index - 1),
                frozenset(
                    (rho, refine(successor, round_index - 1))
                    for successor, rho in actions(state)
                ),
            )
        memo[key] = value
        return value

    value = refine(start, 3)
    digest = hashlib.sha256(stable_encode(value).encode("utf-8")).hexdigest()
    return digest, len(action_cache), sum(len(v) for v in action_cache.values())


def main(regression_k_max=100):
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    templates = {row["template_id"]: row for row in source["templates"]}
    connected_rows = []
    failures = []
    total_descendant_states = 0
    total_action_edges = 0
    k9_matches = 0

    for row in source["classes"]:
        template, law_name, length_at = class_data(source, row, templates)
        if law_name == "0":
            continue
        connected_rows.append(row)
        active_x_min = -6 if law_name == "k-6" else -5

        start8, sat8, component8 = formal_candidate(row, template, length_at, 8)
        if has_fail(start8):
            failures.append({"class_id": row["class_id"], "type": "k8_candidate_has_fail"})
            continue

        # Geometry needed by the lifting proof: the active core-side part is
        # fixed, while every symmetric-difference voxel stays at least three
        # x-layers to its left.
        active8 = frozenset(p for p in component8 if p[0] >= active_x_min)
        geom_failures = []
        for k in range(8, regression_k_max + 1):
            _, _, component_k = formal_candidate(row, template, length_at, k)
            active_k = frozenset(p for p in component_k if p[0] >= active_x_min)
            if active_k != active8:
                geom_failures.append({"k": k, "type": "active_front_changed"})
                break
            diff = component8 ^ component_k
            if diff and max(p[0] for p in diff) > active_x_min - 3:
                geom_failures.append(
                    {
                        "k": k,
                        "type": "tail_not_remote",
                        "max_difference_x": max(p[0] for p in diff),
                    }
                )
                break
        if geom_failures:
            failures.append({"class_id": row["class_id"], "geometry": geom_failures})
            continue

        n_states, n_edges, inert_failures = descendant_inert_audit(
            start8, sat8, active_x_min, root_components(8)
        )
        total_descendant_states += n_states
        total_action_edges += n_edges
        if inert_failures:
            failures.append({"class_id": row["class_id"], "inert": inert_failures})

        start9, _, _ = formal_candidate(row, template, length_at, 9)
        digest9, states9, edges9 = c3_key(start9, 9)
        sha_match = digest9 == row["behavioral_key_sha256"]
        k9_matches += int(sha_match)
        if not sha_match:
            failures.append(
                {
                    "class_id": row["class_id"],
                    "type": "k9_behavioral_key_mismatch",
                    "expected": row["behavioral_key_sha256"],
                    "actual": digest9,
                }
            )

    result = {
        "scope": "A4-L2a(i) connected-satellite classes only; T12 isolated-satellite classes excluded",
        "claim_boundary": (
            "Finite hypotheses plus a structural inert-tail lifting proof establish behavioral "
            "persistence for the 31 non-T12 formal families. This does not prove the 22 T12 "
            "families, root reachability, or all-k exhaustiveness."
        ),
        "connected_class_count": len(connected_rows),
        "excluded_t12_class_count": len(source["classes"]) - len(connected_rows),
        "base_k": 8,
        "geometry_regression_k_range": [8, regression_k_max],
        "descendant_states_audited": total_descendant_states,
        "action_edges_audited": total_action_edges,
        "k9_frozen_key_matches": k9_matches,
        "failures": failures,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        raise AssertionError(f"A4-L2a connected audit failures: {len(failures)}")
    if len(connected_rows) != 31 or k9_matches != 31:
        raise AssertionError("expected exactly 31 connected classes and 31 k=9 key matches")
    print(json.dumps(result, indent=2))
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
