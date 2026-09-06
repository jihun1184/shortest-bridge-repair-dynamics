"""C07-D3E5: frozen verification of a full certificate-aligned D3 witness."""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "c07d3b"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PARENT / "c07a_scripts"))

from finite_window_classification import has_fail  # noqa: E402

from c07d3e1_targeted_search import valid_single_add_repairs  # noqa: E402
from c07d3e2_local_anchor_search import audit_anchor  # noqa: E402
from c07d3e_component_viability import (  # noqa: E402
    certificate_viability,
    component_bridge_exists,
    component_certificates,
    components6,
)


X = frozenset(
    {
        (-3, -1, -1),
        (-1, 0, 0),
        (0, -1, -1),
        (0, -1, 0),
        (0, 2, -1),
    }
)
V1 = (-1, -1, 0)
V2 = (0, 0, 0)


def component_containing(components, point):
    matches = [component for component in components if point in component]
    assert len(matches) == 1
    return matches[0]


def serial_certificate(certificate):
    return tuple(tuple(sorted(component)) for component in certificate)


def background_points_in_box(background, s, t):
    return tuple(
        sorted(
            point
            for point in background
            if all(min(s[a], t[a]) <= point[a] <= max(s[a], t[a]) for a in range(3))
        )
    )


def verify_kill(X, v, certificate):
    before_exists, before = component_bridge_exists(
        X, *certificate, crosscheck=True
    )
    assert before_exists
    viable, after = certificate_viability(
        X, v, certificate, crosscheck=True
    )
    assert not after["resolved"]
    assert after["bridge_evaluated"]
    assert not after["bridge_exists"]
    assert not viable
    before_pair = before["endpoint_pairs"][0]
    after_pair = after["bridge"]["endpoint_pairs"][0]
    before_box = background_points_in_box(X, before_pair["s"], before_pair["t"])
    after_box = background_points_in_box(
        set(X) | {v}, after_pair["s"], after_pair["t"]
    )
    assert set(before_box) == {tuple(before_pair["s"]), tuple(before_pair["t"])}
    assert set(after_box) == {tuple(after_pair["s"]), tuple(after_pair["t"])}
    return {
        "v": v,
        "certificate": serial_certificate(certificate),
        "before": before,
        "after": after,
        "source_cost_assumption_audit": {
            "before_box_background_points": before_box,
            "after_box_background_points": after_box,
            "no_other_preexisting_voxel_in_either_shortest_box": True,
        },
    }


def main():
    assert has_fail(X)
    components = components6(X)
    assert len(components) == 4
    certificates = component_certificates(X)
    assert len(certificates) == 6
    repairs = valid_single_add_repairs(X)
    assert repairs == (V1, V2)
    assert not has_fail(set(X) | {V1})
    assert not has_fail(set(X) | {V2})

    # v1 kills the certificate between (-1,0,0) and (0,2,-1).
    c1 = (
        component_containing(components, (-1, 0, 0)),
        component_containing(components, (0, 2, -1)),
    )
    # v2 kills the certificate between (-3,-1,-1) and (-1,0,0).
    c2 = (
        component_containing(components, (-3, -1, -1)),
        component_containing(components, (-1, 0, 0)),
    )
    kill_v1 = verify_kill(X, V1, c1)
    kill_v2 = verify_kill(X, V2, c2)

    for kill in (kill_v1, kill_v2):
        assert kill["before"]["distance"] == 4
        assert kill["before"]["endpoint_pair_count"] == 1
        assert kill["before"]["endpoint_pairs"][0]["total"] == 12
        assert kill["before"]["endpoint_pairs"][0]["compatible"] == 3
        assert kill["after"]["bridge"]["distance"] == 3
        assert kill["after"]["bridge"]["endpoint_pair_count"] == 1
        assert kill["after"]["bridge"]["endpoint_pairs"][0]["total"] == 1
        assert kill["after"]["bridge"]["endpoint_pairs"][0]["compatible"] == 0

    full_audit = audit_anchor(X, crosscheck=True)
    assert full_audit is not None and full_audit["full_counterexample"]

    # Deletion audit: recompute certificates and valid repairs for every proper
    # nonempty subset; this proves deletion-minimality of this concrete witness
    # under the frozen D3E operational semantics, not absolute global minimality.
    deletion_trials = 0
    smaller_full_counterexamples = []
    ordered = tuple(sorted(X))
    for size in range(1, len(ordered)):
        for subset in itertools.combinations(ordered, size):
            deletion_trials += 1
            Y = frozenset(subset)
            if not has_fail(Y):
                continue
            audit = audit_anchor(Y)
            if audit and audit["full_counterexample"]:
                smaller_full_counterexamples.append(audit)
    assert not smaller_full_counterexamples

    result = {
        "X": tuple(sorted(X)),
        "components": tuple(tuple(sorted(c)) for c in components),
        "genuine_certificate_count": len(certificates),
        "valid_single_add_repairs": repairs,
        "kills": {"v1": kill_v1, "v2": kill_v2},
        "full_counterexample": True,
        "deletion_audit": {
            "proper_nonempty_subsets_checked": deletion_trials,
            "smaller_full_counterexamples": smaller_full_counterexamples,
            "deletion_minimal_for_this_witness": True,
            "absolute_minimality_claimed": False,
        },
        "verdict": {
            "compressed_brute_force_agree": True,
            "resolved_false_for_both_targeted_pairs": True,
            "descendant_endpoint_family_recomputed": True,
            "C07_D3_full_certificate_semantics": "REJECTED",
        },
    }
    output = HERE / "c07d3e5_counterexample_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D3E5 full certificate counterexample: ALL CHECKS PASSED")
    print("valid repairs:", repairs)
    print("v1 certificate bridge: 3/12 -> 0/1; resolved=False")
    print("v2 certificate bridge: 3/12 -> 0/1; resolved=False")
    print("proper nonempty subsets checked:", deletion_trials)
    print("smaller full counterexamples:", len(smaller_full_counterexamples))
    print("JSON:", output)


if __name__ == "__main__":
    main()
