"""D7D2-A4-L2b: finite reachability skeleton + structural witness audit.

This script does two expensive-but-small exact tasks only at k=6 and k=9:
  * reconstruct a target-restricted N2 path to every one of the 53 formal
    representatives;
  * extract one exact shortest-monotone realization for every edge of the
    resulting 54-node reachability tree (53 classes + one auxiliary node U).

It then checks the closed-form lifted witnesses on k=6..100 without
enumerating the full root closure or all bridge actions at those k values.
The universal all-k statement is proved in the accompanying theorem note;
the finite k-range is a regression on the proof hypotheses, not its basis.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CHECKPOINT_ROOT = HERE.parent
WORK = CHECKPOINT_ROOT / "work" / "d7c_pkg" / "c07d7c_package" / "work"
for dependency in (
    CHECKPOINT_ROOT / "work" / "d7d1",
    WORK / "c07d3e",
    WORK / "c07d4",
    WORK / "c07d5",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))
sys.path.insert(0, str(HERE))

from a4_l1b_formal_geometry_audit import (  # noqa: E402
    REPAIR,
    build_satellite,
    decode_points,
    infer_law,
)
from anchor_windowed_quotient_v2 import CORE  # noqa: E402
from c07d3e_component_viability import (  # noqa: E402
    component_certificates,
    components6,
    l1,
    shortest_endpoint_pairs,
)
from c07d4_planning_census import certificate_bridge_actions  # noqa: E402
from c07d5_atomic_planning_census import atomic_actions  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402

SOURCE = HERE / "a4_l1a_signature_table_results.json"
OUTPUT = HERE / "a4_l2b_parametric_reachability_results.json"

STEP_OF = {
    (1, 0, 0): "+x",
    (-1, 0, 0): "-x",
    (0, 1, 0): "+y",
    (0, -1, 0): "-y",
    (0, 0, 1): "+z",
    (0, 0, -1): "-z",
}
DELTA_OF = {value: key for key, value in STEP_OF.items()}

source_payload = json.loads(SOURCE.read_text(encoding="utf-8"))
TEMPLATES = {row["template_id"]: row for row in source_payload["templates"]}
CLASS_ROWS = {row["class_id"]: row for row in source_payload["classes"]}
CLASS_IDS = tuple(sorted(CLASS_ROWS))


def formal_state(class_id: str, k: int) -> frozenset[tuple[int, int, int]]:
    row = CLASS_ROWS[class_id]
    template = TEMPLATES[row["selected_template_id"]]
    lengths = {
        str(j): row["selected_template_witnesses"][str(j)]["corridor_length"]
        for j in (6, 7, 8)
    }
    _, length_at, _ = infer_law(lengths)
    _, _, _, satellite_component = build_satellite(template, k, length_at(k))
    return frozenset(decode_points(row["fixed_remainder"]) | satellite_component)


def root_state(k: int):
    return frozenset(CORE | {(-k, 2, 0), REPAIR})


def path_word(path):
    output = []
    for left, right in zip(path, path[1:]):
        delta = tuple(right[i] - left[i] for i in range(3))
        if delta not in STEP_OF:
            raise AssertionError(f"non-6-neighbor path step: {left}->{right}")
        output.append(STEP_OF[delta])
    return tuple(output)


def generate_path(start, word):
    current = tuple(start)
    rows = [current]
    for step in word:
        delta = DELTA_OF[step]
        current = tuple(current[i] + delta[i] for i in range(3))
        rows.append(current)
    return tuple(rows)


def serialized_points(points):
    return [list(p) for p in sorted(points)]


ACTION_CACHE = {}
CERT_ACTION_CACHE = {}


def actions(state):
    state = frozenset(state)
    if state not in ACTION_CACHE:
        ACTION_CACHE[state] = atomic_actions(state)
    return ACTION_CACHE[state]


def restricted_path(target, k, max_depth=4):
    """BFS using only N2 additions contained in the exact target."""
    root = root_state(k)
    if not root <= target:
        raise AssertionError("root is not a subset of target")
    if root == target:
        return tuple()
    queue = deque([(root, tuple())])
    seen = {root}
    while queue:
        state, schedule = queue.popleft()
        if len(schedule) >= max_depth:
            continue
        for action in actions(state):
            if set(action["roles"]) != {"N2"}:
                continue
            addition = frozenset(tuple(p) for p in action["additions"])
            if not addition <= target:
                continue
            successor = state | addition
            if successor == target:
                return schedule + (addition,)
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, schedule + (addition,)))
    raise AssertionError(f"target not reached at k={k}, size={len(target)}")


def build_paths(k):
    targets = {cid: formal_state(cid, k) for cid in CLASS_IDS}
    paths = {cid: restricted_path(targets[cid], k) for cid in CLASS_IDS}
    return targets, paths


def state_sequence(k, schedule):
    rows = [root_state(k)]
    state = rows[0]
    for addition in schedule:
        state = state | addition
        rows.append(state)
    return tuple(rows)


def discover_tree(k, targets, paths):
    reverse = {state: cid for cid, state in targets.items()}
    root = root_state(k)
    unknown_states = set()
    transition_records = []
    for cid in CLASS_IDS:
        seq = state_sequence(k, paths[cid])
        for left, right in zip(seq, seq[1:]):
            if left not in reverse:
                unknown_states.add(left)
            if right not in reverse:
                unknown_states.add(right)
            transition_records.append((left, right, frozenset(right - left)))
    unknown_states.discard(root)
    if len(unknown_states) != 1:
        raise AssertionError(f"expected one auxiliary state, got {len(unknown_states)}")
    auxiliary = next(iter(unknown_states))

    def node_name(state):
        if state in reverse:
            return reverse[state]
        if state == auxiliary:
            return "U"
        raise AssertionError("unexpected unnamed state in skeleton")

    # Every formal class except the root gets its incoming final edge from its
    # chosen exact schedule. U gets the unique edge entering the auxiliary state.
    edges = {}
    for cid in CLASS_IDS:
        if cid == "C053":
            continue
        seq = state_sequence(k, paths[cid])
        left, right = seq[-2], seq[-1]
        key = (node_name(left), cid)
        edges[key] = {
            "source_state": left,
            "target_state": right,
            "additions": frozenset(right - left),
        }
    entering_u = [
        (left, right, add)
        for left, right, add in transition_records
        if right == auxiliary
    ]
    unique_entering_u = {
        (left, right, add) for left, right, add in entering_u
    }
    if len(unique_entering_u) != 1:
        raise AssertionError(f"expected unique root->U edge, got {len(unique_entering_u)}")
    left, right, add = next(iter(unique_entering_u))
    if node_name(left) != "C053":
        raise AssertionError("auxiliary node is not a root child")
    edges[("C053", "U")] = {
        "source_state": left,
        "target_state": right,
        "additions": add,
    }
    if len(edges) != 53:
        raise AssertionError(f"expected 53 tree edges, got {len(edges)}")
    return auxiliary, edges


def exact_realization(state, addition):
    """Recover one exact N2 realization already known to atomic_actions."""
    chosen = None
    for action in actions(state):
        if frozenset(tuple(p) for p in action["additions"]) == addition:
            if "N2" not in action["roles"]:
                continue
            chosen = action
            break
    if chosen is None:
        raise AssertionError("chosen addition is not an atomic N2 action")
    n2_witnesses = [w for w in chosen["witnesses"] if "certificate" in w]
    if not n2_witnesses:
        raise AssertionError("N2 action has no certificate witness")
    certificate = tuple(frozenset(tuple(p) for p in comp) for comp in n2_witnesses[0]["certificate"])
    cache_key = (state, certificate)
    if cache_key not in CERT_ACTION_CACHE:
        CERT_ACTION_CACHE[cache_key] = certificate_bridge_actions(state, certificate)[0]
    for action in CERT_ACTION_CACHE[cache_key]:
        if frozenset(tuple(p) for p in action["additions"]) == addition:
            realization = action["realizations"][0]
            return certificate, {
                "s": tuple(realization["s"]),
                "t": tuple(realization["t"]),
                "path": tuple(tuple(p) for p in realization["path"]),
            }
    raise AssertionError("could not recover selected bridge realization")


def infer_insertion(word6, word9):
    extra = len(word9) - len(word6)
    if extra != 3:
        raise AssertionError(f"expected k=9 to add 3 steps, got {extra}")
    matches = []
    for index in range(len(word6) + 1):
        if word9 == word6[:index] + ("+x",) * 3 + word6[index:]:
            matches.append(index)
    if not matches:
        raise AssertionError(f"cannot infer +x insertion: {word6} -> {word9}")
    return matches[0]


def classify_edge(source_name, source9, target9, add6, add9):
    sat = (-9, 2, 0)
    if source_name == "C053":
        before_sat = next(c for c in components6(source9) if sat in c)
        after_sat = next(c for c in components6(target9) if sat in c)
        return "root_satellite" if len(after_sat) > len(before_sat) else "root_fixed"
    if source_name == "U":
        if add6 != add9:
            raise AssertionError("auxiliary edge unexpectedly varies with k")
        return "aux_fixed"
    if add6 != add9:
        raise AssertionError("nonroot edge unexpectedly varies with k")
    return "nonroot_fixed"


def edge_node_state(name, k, auxiliary_state):
    if name == "U":
        return auxiliary_state
    return formal_state(name, k)


def main(k_regression_max=100):
    # Exact base schedule reconstruction at a certified level and the first
    # unseen lifting level used by A4-L2a(ii).
    targets6, paths6 = build_paths(6)
    targets9, paths9 = build_paths(9)
    aux6, edges6 = discover_tree(6, targets6, paths6)
    aux9, edges9 = discover_tree(9, targets9, paths9)
    if set(edges6) != set(edges9):
        raise AssertionError("k=6 and k=9 skeleton edge sets differ")

    depth_hist_6 = Counter(len(paths6[cid]) for cid in CLASS_IDS)
    depth_hist_9 = Counter(len(paths9[cid]) for cid in CLASS_IDS)
    if depth_hist_6 != depth_hist_9:
        raise AssertionError("reachability-depth histogram changed at k=9")
    if depth_hist_9 != Counter({1: 27, 2: 24, 3: 1, 0: 1}):
        raise AssertionError(f"unexpected depth histogram: {depth_hist_9}")

    edge_records = []
    edge_data = {}
    kind_counts = Counter()
    # Recover exact bridge realizations at k=6 and k=9 and infer the finite
    # parametric word for the 12 satellite-absorbing root edges.
    for key in sorted(edges9):
        source_name, target_name = key
        e6, e9 = edges6[key], edges9[key]
        cert6, realization6 = exact_realization(e6["source_state"], e6["additions"])
        cert9, realization9 = exact_realization(e9["source_state"], e9["additions"])
        word6 = path_word(realization6["path"])
        word9 = path_word(realization9["path"])
        kind = classify_edge(
            source_name,
            e9["source_state"],
            e9["target_state"],
            e6["additions"],
            e9["additions"],
        )
        kind_counts[kind] += 1
        record = {
            "source": source_name,
            "target": target_name,
            "kind": kind,
            "k6_addition_size": len(e6["additions"]),
            "k9_addition_size": len(e9["additions"]),
            "k6_s": list(realization6["s"]),
            "k6_t": list(realization6["t"]),
            "k6_word": list(word6),
        }
        data = {
            "kind": kind,
            "source": source_name,
            "target": target_name,
            "realization6": realization6,
            "realization9": realization9,
            "word6": word6,
        }
        if kind == "root_satellite":
            if realization6["t"] != realization9["t"]:
                raise AssertionError("root-satellite target endpoint changed")
            insertion = infer_insertion(word6, word9)
            data["insertion_index"] = insertion
            record["variable_x_insertion_index"] = insertion
            record["fixed_target_endpoint"] = list(realization6["t"])
        else:
            if realization6["path"] != realization9["path"]:
                raise AssertionError(
                    f"fixed edge realization changed: {source_name}->{target_name}"
                )
        edge_records.append(record)
        edge_data[key] = data

    expected_kinds = {
        "root_fixed": 16,
        "root_satellite": 12,
        "nonroot_fixed": 24,
        "aux_fixed": 1,
    }
    if dict(kind_counts) != expected_kinds:
        raise AssertionError(f"edge-kind counts {dict(kind_counts)} != {expected_kinds}")

    # Define U(k) by lifting its root-satellite bridge word. This is the only
    # non-class node in the finite tree.
    root_to_u = edge_data[("C053", "U")]

    def auxiliary_at(k):
        w6 = root_to_u["word6"]
        idx = root_to_u["insertion_index"]
        word = w6[:idx] + ("+x",) * (k - 6) + w6[idx:]
        path = generate_path((-k, 2, 0), word)
        return root_state(k) | frozenset(path)

    failures = []
    total_edge_k_cases = 0
    root_sat_fronts = defaultdict(set)
    for k in range(6, k_regression_max + 1):
        aux = auxiliary_at(k)
        node_states = {cid: formal_state(cid, k) for cid in CLASS_IDS}
        node_states["U"] = aux
        if node_states["C053"] != root_state(k):
            failures.append({"k": k, "root_class_not_exact_root": True})

        for key in sorted(edge_data):
            data = edge_data[key]
            source_state = node_states[data["source"]]
            target_state = node_states[data["target"]]
            if not source_state < target_state:
                failures.append({"k": k, "edge": list(key), "source_not_strict_subset": True})
                continue
            addition = frozenset(target_state - source_state)

            if data["kind"] == "root_satellite":
                w6 = data["word6"]
                idx = data["insertion_index"]
                word = w6[:idx] + ("+x",) * (k - 6) + w6[idx:]
                path = generate_path((-k, 2, 0), word)
                root_sat_fronts[key].add(
                    tuple(p for p in path if p[0] >= -5)
                )
            else:
                path = data["realization6"]["path"]

            s, t = path[0], path[-1]
            path_set = frozenset(path)
            comps = components6(source_state)
            containing_s = [c for c in comps if s in c]
            containing_t = [c for c in comps if t in c]
            checks = {
                "path_additions_exact": frozenset(path_set - source_state) == addition,
                "start_component_unique": len(containing_s) == 1,
                "target_component_unique": len(containing_t) == 1,
                "endpoints_distinct_components": bool(containing_s and containing_t)
                and containing_s[0] != containing_t[0],
                "path_length_l1": len(path) - 1 == l1(s, t),
                "target_valid": not has_fail(target_state),
                "component_count_contracts": len(components6(target_state)) < len(comps),
            }
            if containing_s and containing_t and containing_s[0] != containing_t[0]:
                _, pairs = shortest_endpoint_pairs(containing_s[0], containing_t[0])
                checks["endpoint_pair_minimizing"] = (s, t) in pairs or (t, s) in pairs
            else:
                checks["endpoint_pair_minimizing"] = False
            if not all(checks.values()):
                failures.append({"k": k, "edge": list(key), "checks": checks})
            total_edge_k_cases += 1

    # The 12 parametric root paths must have one fixed compatibility front;
    # only their remote x<=-6 portion may grow.
    nonconstant_fronts = {
        f"{src}->{dst}": len(fronts)
        for (src, dst), fronts in root_sat_fronts.items()
        if len(fronts) != 1
    }
    if nonconstant_fronts:
        failures.append({"root_satellite_nonconstant_x_ge_minus_5_fronts": nonconstant_fronts})

    result = {
        "scope": (
            "A4-L2b reachability witness skeleton; exact k=6/k=9 reconstruction plus "
            "closed-form witness regression. Full closure is not enumerated."
        ),
        "claim_boundary": (
            "Proves reachability of the 53 formal A4-L1b families. Does not prove "
            "A4-L3 exhaustiveness or Q_k ~= Q_6 for all k."
        ),
        "class_count": len(CLASS_IDS),
        "tree_node_count": 54,
        "tree_edge_count": len(edge_data),
        "auxiliary_node_count": 1,
        "edge_kind_counts": dict(kind_counts),
        "depth_histogram_k6": {str(k): v for k, v in sorted(depth_hist_6.items())},
        "depth_histogram_k9": {str(k): v for k, v in sorted(depth_hist_9.items())},
        "k6_reachable_formal_classes": sum(1 for p in paths6.values() if p is not None),
        "k9_reachable_formal_classes": sum(1 for p in paths9.values() if p is not None),
        "root_satellite_path_family_count": kind_counts["root_satellite"],
        "root_satellite_fixed_compatibility_front_count": sum(
            len(fronts) == 1 for fronts in root_sat_fronts.values()
        ),
        "regression_k_range": [6, k_regression_max],
        "regression_edge_k_cases": total_edge_k_cases,
        "failures": failures,
        "edges": edge_records,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        raise AssertionError(f"A4-L2b audit failures: {len(failures)}; see {OUTPUT}")
    print(json.dumps({
        "class_count": result["class_count"],
        "tree_node_count": result["tree_node_count"],
        "tree_edge_count": result["tree_edge_count"],
        "edge_kind_counts": result["edge_kind_counts"],
        "depth_histogram_k6": result["depth_histogram_k6"],
        "depth_histogram_k9": result["depth_histogram_k9"],
        "k6_reachable_formal_classes": result["k6_reachable_formal_classes"],
        "k9_reachable_formal_classes": result["k9_reachable_formal_classes"],
        "root_satellite_fixed_compatibility_front_count": result["root_satellite_fixed_compatibility_front_count"],
        "regression_k_range": result["regression_k_range"],
        "regression_edge_k_cases": result["regression_edge_k_cases"],
        "failures": result["failures"],
        "claim_boundary": result["claim_boundary"],
    }, indent=2))
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
