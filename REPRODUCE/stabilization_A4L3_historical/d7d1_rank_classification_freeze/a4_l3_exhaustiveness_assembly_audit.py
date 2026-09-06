"""A4-L3 finite proof-assembly audit for all-k quotient exhaustiveness.

The universal step is the already-proved A4-L2a(ii) path-word/front
normalization.  This audit checks the finite premises that turn that lemma
into an arbitrary-root-state theorem after A4-L2b supplies reachability:

* C053 is the k=9 root and is one of the 22 T12 starts;
* every T12 start is reachable in the A4-L2b witness tree;
* consequently their union descendant closure is exactly Reach(X_9);
* every exact key in that closure is one of the 53 frozen keys, and all 53
  occur, split as 22 isolated and 31 connected keys.

Run from the checkpoint root.  The closure enumeration is intentionally
fresh and takes several minutes.
"""

from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path

import a4_l2a_t12_bridge_quotient_audit as t12
from anchor_windowed_quotient_v2 import CORE


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "a4_l1a_signature_table_results.json"
REACHABILITY = HERE / "a4_l2b_parametric_reachability_results.json"
OUTPUT = HERE / "a4_l3_exhaustiveness_assembly_results.json"


def digest_key(value):
    return t12.digest_key(value)


def reachable_tree_nodes(edges, root="C053"):
    children = {}
    for edge in edges:
        children.setdefault(edge["source"], []).append(edge["target"])
    seen = {root}
    queue = deque([root])
    while queue:
        node = queue.popleft()
        for child in children.get(node, ()):
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return seen


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    reachability = json.loads(REACHABILITY.read_text(encoding="utf-8"))
    templates = {row["template_id"]: row for row in source["templates"]}
    class_rows = source["classes"]
    row_by_id = {row["class_id"]: row for row in class_rows}
    t12_rows = [row for row in class_rows if row["selected_template_id"] == "T12"]
    connected_rows = [row for row in class_rows if row["selected_template_id"] != "T12"]

    starts = []
    start_by_id = {}
    for row in t12_rows:
        template, law_name, length_at = t12.class_data(source, row, templates)
        if law_name != "0":
            raise AssertionError(f"nonzero T12 law for {row['class_id']}")
        start, satellite, sat_component = t12.formal_candidate(
            row, template, length_at, t12.BASE_K
        )
        if sat_component != frozenset((satellite,)):
            raise AssertionError(f"non-isolated T12 state for {row['class_id']}")
        starts.append(start)
        start_by_id[row["class_id"]] = start

    root = frozenset(CORE | {(-1, -1, 0), (-t12.BASE_K, 2, 0)})
    c053_is_root = start_by_id.get("C053") == root

    tree_nodes = reachable_tree_nodes(reachability["edges"])
    t12_ids = {row["class_id"] for row in t12_rows}
    all_t12_tree_reachable = t12_ids <= tree_nodes

    print(
        f"building k={t12.BASE_K} root closure through {len(starts)} T12 starts...",
        flush=True,
    )
    closure = t12.enumerate_union_closure(starts, t12.BASE_K)
    states = closure["states"]
    successors = closure["successors"]
    components = closure["components"]
    keys = t12.exact_c3(states, successors, components, closure["root_components"])
    digests = {state: digest_key(key) for state, key in keys.items()}
    c4 = {
        state: (
            keys[state],
            frozenset((rho, keys[successor]) for successor, rho, _ in successors[state]),
        )
        for state in states
    }
    c3_class_count = len(set(keys.values()))
    c4_class_count = len(set(c4.values()))

    frozen_all = {row["behavioral_key_sha256"] for row in class_rows}
    frozen_t12 = {row["behavioral_key_sha256"] for row in t12_rows}
    frozen_connected = {row["behavioral_key_sha256"] for row in connected_rows}
    observed_all = set(digests.values())
    observed_isolated = set()
    observed_connected = set()
    type_violations = []
    layer_counts = Counter()
    for state in states:
        sat_component = t12.satellite_component(
            state, closure["satellite"], components[state]
        )
        digest = digests[state]
        if len(sat_component) == 1:
            observed_isolated.add(digest)
            layer_counts[("isolated", len(components[state]))] += 1
            if digest not in frozen_t12:
                type_violations.append(("isolated", digest))
        else:
            observed_connected.add(digest)
            layer_counts[("connected", len(components[state]))] += 1
            if digest not in frozen_connected:
                type_violations.append(("connected", digest))

    # Because C053=root belongs to starts, Reach(X_9) is contained in the
    # union closure.  A4-L2b makes every start reachable, so the reverse
    # containment follows.  These two finite flags certify the premises.
    union_equals_root_closure = c053_is_root and all_t12_tree_reachable

    failures = []
    checks = {
        "class_rows_53": len(class_rows) == 53,
        "t12_rows_22": len(t12_rows) == 22,
        "connected_rows_31": len(connected_rows) == 31,
        "c053_is_k9_root": c053_is_root,
        "all_t12_starts_reachable_in_l2b_tree": all_t12_tree_reachable,
        "l2b_reports_53_k9_targets": reachability["k9_reachable_formal_classes"] == 53,
        "l2b_tree_shape_54_nodes_53_edges": (
            reachability["tree_node_count"] == 54
            and reachability["tree_edge_count"] == 53
        ),
        "l2b_failures_zero": not reachability["failures"],
        "union_equals_root_closure_by_two_inclusions": union_equals_root_closure,
        "c3_to_c4_partition_stable": c3_class_count == c4_class_count,
        "observed_key_set_equals_frozen_53": observed_all == frozen_all,
        "isolated_key_set_equals_frozen_t12_22": observed_isolated == frozen_t12,
        "connected_key_set_equals_frozen_connected_31": (
            observed_connected == frozen_connected
        ),
        "satellite_type_violations_zero": not type_violations,
    }
    failures.extend(name for name, passed in checks.items() if not passed)

    result = {
        "scope": (
            "Finite k=9 proof assembly for A4-L3 exhaustiveness; the all-k "
            "step uses the proved A4-L2a(ii) path-word/front normalization."
        ),
        "base_k": t12.BASE_K,
        "checks": checks,
        "failures": failures,
        "t12_start_count": len(starts),
        "l2b_tree_reachable_node_count": len(tree_nodes),
        "root_closure_state_count": len(states),
        "root_closure_edge_count": sum(len(value) for value in successors.values()),
        "observed_behavioral_key_count": len(observed_all),
        "c3_class_count": c3_class_count,
        "c4_class_count": c4_class_count,
        "observed_isolated_key_count": len(observed_isolated),
        "observed_connected_key_count": len(observed_connected),
        "type_violation_count": len(type_violations),
        "state_layers": {
            f"{kind}_{count}": value
            for (kind, count), value in sorted(layer_counts.items())
        },
        "claim_boundary": (
            "Together with the proved A4-L2a arbitrary isolated-bridge "
            "normalization and A4-L2b reachability, this certifies "
            "Q_k = Q_9 = Q_6 for all k>=6 and hence R*(X_k)=3."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"wrote {OUTPUT}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
