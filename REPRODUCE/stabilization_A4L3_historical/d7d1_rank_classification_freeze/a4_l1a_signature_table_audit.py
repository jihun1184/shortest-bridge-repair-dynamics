"""A4-L1a finite fixed-remainder certificate and template table audit."""

from __future__ import annotations

import hashlib
import json
import time

from a4_induction_diff import (
    extract_template_witnesses,
    keys_by_state,
    satellite_component,
)
from a4_template_audit import canonical_representatives, jsonable_signature
from exact_partition_refinement import build_closure


def stable_encode(value):
    """Deterministic encoding for nested tuple/frozenset behavioral keys."""
    if isinstance(value, tuple):
        return "(" + ",".join(stable_encode(item) for item in value) + ")"
    if isinstance(value, frozenset):
        return "{" + ",".join(sorted(stable_encode(item) for item in value)) + "}"
    if isinstance(value, int):
        return str(value)
    if value is None:
        return "null"
    raise TypeError(f"unsupported behavioral-key type: {type(value)!r}")


def signature_sort_key(signature):
    d, attachment, patch = signature
    return (d, tuple(sorted(attachment)), tuple(sorted(patch)))


def reconstruct_component(satellite, signature, witness):
    d, attachment, patch = signature
    start = tuple(satellite[i] + d[i] for i in range(3))
    endpoint = witness["endpoint"]
    length = witness["corridor_length"]
    corridor = {
        (start[0] + j, start[1], start[2]) for j in range(length + 1)
    }
    satellite_piece = {
        tuple(satellite[i] + point[i] for i in range(3))
        for point in attachment
    }
    core_piece = {
        tuple(endpoint[i] + point[i] for i in range(3)) for point in patch
    }
    return frozenset(satellite_piece | corridor | core_piece)


def audit(ks=(6, 7, 8), time_budget=200):
    representatives = {}
    satellites = {}
    closure_sizes = {}
    for k in ks:
        started = time.time()
        states, successors, root_components, satellite = build_closure(
            k, time_budget=time_budget
        )
        keys = keys_by_state(states, successors, root_components)
        representatives[k] = canonical_representatives(states, keys)
        satellites[k] = satellite
        closure_sizes[k] = len(states)
        print(
            f"k={k}: {len(states)} states, {len(representatives[k])} classes "
            f"({time.time() - started:.1f}s)",
            flush=True,
        )

    common_keys = set.intersection(*(set(representatives[k]) for k in ks))
    ordered_keys = sorted(common_keys, key=stable_encode)
    class_ids = {key: f"C{index:03d}" for index, key in enumerate(ordered_keys, 1)}

    fixed_remainder_failures = []
    reconstruction_failures = []
    class_work = []
    all_common_signatures = set()

    for key in ordered_keys:
        cid = class_ids[key]
        components = {
            k: satellite_component(representatives[k][key], satellites[k]) for k in ks
        }
        remainders = {
            k: frozenset(representatives[k][key] - components[k]) for k in ks
        }
        remainder_equal = len(set(remainders.values())) == 1
        if not remainder_equal:
            fixed_remainder_failures.append(cid)

        witness_maps = {
            k: extract_template_witnesses(representatives[k][key], satellites[k])
            for k in ks
        }
        common_signatures = set.intersection(
            *(set(witness_maps[k]) for k in ks)
        )
        all_common_signatures.update(common_signatures)

        reconstruction_ok = True
        for k in ks:
            for signature in common_signatures:
                for witness in witness_maps[k][signature]:
                    if reconstruct_component(satellites[k], signature, witness) != components[k]:
                        reconstruction_ok = False
                        reconstruction_failures.append(
                            {
                                "class_id": cid,
                                "k": k,
                                "signature": jsonable_signature(signature),
                            }
                        )

        encoded_key = stable_encode(key).encode("utf-8")
        class_work.append(
            {
                "class_id": cid,
                "behavioral_key_sha256": hashlib.sha256(encoded_key).hexdigest(),
                "representative_sizes": {str(k): len(representatives[k][key]) for k in ks},
                "fixed_remainder_equal": remainder_equal,
                "fixed_remainder": [list(p) for p in sorted(remainders[ks[0]])]
                if remainder_equal
                else {str(k): [list(p) for p in sorted(remainders[k])] for k in ks},
                "common_signatures": common_signatures,
                "witness_maps": witness_maps,
                "reconstruction_ok": reconstruction_ok,
            }
        )

    ordered_signatures = sorted(all_common_signatures, key=signature_sort_key)
    template_ids = {
        signature: f"T{index:02d}" for index, signature in enumerate(ordered_signatures, 1)
    }
    templates = []
    for signature in ordered_signatures:
        members = [
            row["class_id"] for row in class_work if signature in row["common_signatures"]
        ]
        templates.append(
            {
                "template_id": template_ids[signature],
                **jsonable_signature(signature),
                "compatible_class_ids": members,
            }
        )

    classes = []
    for row in class_work:
        common = sorted(row.pop("common_signatures"), key=signature_sort_key)
        witness_maps = row.pop("witness_maps")
        selected = common[0]
        selected_id = template_ids[selected]
        per_k = {}
        for k in ks:
            witness = min(
                witness_maps[k][selected],
                key=lambda item: (
                    item["corridor_length"], item["start"], item["endpoint"]
                ),
            )
            per_k[str(k)] = {
                "satellite": list(satellites[k]),
                "corridor_start": list(witness["start"]),
                "corridor_endpoint": list(witness["endpoint"]),
                "corridor_length": witness["corridor_length"],
            }
        classes.append(
            {
                **row,
                "compatible_template_ids": [template_ids[sig] for sig in common],
                "selected_template_id": selected_id,
                "selected_template_witnesses": per_k,
            }
        )

    return {
        "scope": "finite certification on canonical representatives for k=6,7,8",
        "claim_boundary": (
            "Does not establish reachability or behavioral-class membership for k>8."
        ),
        "ks": list(ks),
        "closure_sizes": closure_sizes,
        "common_behavioral_classes": len(common_keys),
        "fixed_remainder_consistent_classes": len(common_keys)
        - len(fixed_remainder_failures),
        "fixed_remainder_failures": fixed_remainder_failures,
        "witnessed_template_count": len(templates),
        "classes_with_common_template": sum(
            bool(row["compatible_template_ids"]) for row in classes
        ),
        "component_reconstruction_failures": reconstruction_failures,
        "templates": templates,
        "classes": classes,
    }


if __name__ == "__main__":
    result = audit()
    if result["common_behavioral_classes"] != 53:
        raise AssertionError(
            f"expected 53 common classes, got {result['common_behavioral_classes']}"
        )
    if result["fixed_remainder_failures"]:
        raise AssertionError(
            f"fixed-remainder failures: {result['fixed_remainder_failures']}"
        )
    if result["witnessed_template_count"] != 18:
        raise AssertionError(
            f"expected 18 templates, got {result['witnessed_template_count']}"
        )
    if result["classes_with_common_template"] != 53:
        raise AssertionError(
            "not every behavioral class has a common satellite template"
        )
    if result["component_reconstruction_failures"]:
        raise AssertionError(
            "one or more template witnesses failed exact reconstruction"
        )
    output = __file__.replace(
        "a4_l1a_signature_table_audit.py", "a4_l1a_signature_table_results.json"
    )
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    summary_keys = (
        "scope",
        "closure_sizes",
        "common_behavioral_classes",
        "fixed_remainder_consistent_classes",
        "fixed_remainder_failures",
        "witnessed_template_count",
        "classes_with_common_template",
        "component_reconstruction_failures",
        "claim_boundary",
    )
    print(json.dumps({key: result[key] for key in summary_keys}, indent=2))
    print(f"wrote {output}")
