"""D7D2-A4.3B: reproduce and audit elbow-aware template consistency."""

from __future__ import annotations

import json
import time

from a4_induction_diff import extract_template_families, keys_by_state
from exact_partition_refinement import build_closure


def canonical_representatives(states, keys):
    grouped = {}
    for state in states:
        grouped.setdefault(keys[state], []).append(state)
    return {
        key: min(group, key=lambda state: (len(state), sorted(state)))
        for key, group in grouped.items()
    }


def jsonable_signature(signature):
    line_offset, attachment, patch = signature
    return {
        "line_offset": list(line_offset),
        "attachment_shape": [list(p) for p in sorted(attachment)],
        "patch_shape": [list(p) for p in sorted(patch)],
    }


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

    common = set.intersection(*(set(representatives[k]) for k in ks))
    inconsistent = []
    witnessed_family_signatures = set()
    for key in common:
        signature_sets = {
            k: extract_template_families(representatives[k][key], satellites[k])
            for k in ks
        }
        common_signatures = set.intersection(*(set(signature_sets[k]) for k in ks))
        witnessed_family_signatures.update(common_signatures)
        if not common_signatures:
            inconsistent.append(
                {
                    "combined_size": sum(len(representatives[k][key]) for k in ks),
                    "representatives": {
                        str(k): [list(p) for p in sorted(representatives[k][key])]
                        for k in ks
                    },
                    "signature_sets": {
                        str(k): [
                            jsonable_signature(signature)
                            for signature in sorted(signature_sets[k], key=str)
                        ]
                        for k in ks
                    },
                }
            )

    inconsistent.sort(
        key=lambda row: (row["combined_size"], str(row["signature_sets"]))
    )
    return {
        "method": "set-valued cut-equivalence; elbow-aware straight corridors; endpoint-anchored patch",
        "ks": list(ks),
        "closure_sizes": closure_sizes,
        "common_classes": len(common),
        "consistent_classes": len(common) - len(inconsistent),
        "inconsistent_classes": len(inconsistent),
        "distinct_witnessed_signatures": len(witnessed_family_signatures),
        "inconsistent_details": inconsistent,
    }


if __name__ == "__main__":
    result = audit()
    output = __file__.replace("a4_template_audit.py", "a4_template_audit_results.json")
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "inconsistent_details"}, indent=2))
    print(f"wrote {output}")
