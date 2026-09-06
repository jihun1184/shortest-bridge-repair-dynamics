"""C07-D3E2: exhaustive certificate-aligned search over pure Q2/Q3 anchors."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "c07d3b"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PARENT / "c07a_scripts"))

from finite_window_classification import (  # noqa: E402
    BAD_Q2,
    BAD_Q3,
    edge_cands,
    has_fail,
    vertex_cands,
)

from c07d3e1_targeted_search import valid_single_add_repairs  # noqa: E402
from c07d3e_component_viability import (  # noqa: E402
    certificate_viability,
    component_bridge_exists,
    component_certificates,
    components6,
)


def physical_points(kind, pattern):
    if kind == "Q2":
        positions, labels = edge_cands((0, 0, 0, "z"))
    else:
        positions, labels = vertex_cands((0, 0, 0))
    lookup = dict(zip(labels, positions))
    return frozenset(lookup[label] for label in pattern)


def certificate_kill(X, v, certificate, *, crosscheck=False):
    # Most candidates remain bridgeable after the action.  Test that cheaper
    # rejection first, and evaluate the before-state preservation premise only
    # for an actual after-state full kill.
    viable, after = certificate_viability(
        X, v, certificate, crosscheck=crosscheck
    )
    if after["resolved"] or viable:
        return None
    before_exists, before = component_bridge_exists(
        X, *certificate, crosscheck=crosscheck
    )
    if not before_exists:
        return None
    return {"certificate": tuple(tuple(sorted(c)) for c in certificate), "before": before, "after": after}


def audit_anchor(X, *, crosscheck=False):
    repairs = valid_single_add_repairs(X)
    certificates = component_certificates(X)
    if not repairs or not certificates:
        return None
    action_records = []
    for v in repairs:
        kills = []
        for certificate in certificates:
            kill = certificate_kill(X, v, certificate, crosscheck=crosscheck)
            if kill is not None:
                kills.append(kill)
        action_records.append({"v": v, "kills": kills})
    return {
        "X": tuple(sorted(X)),
        "components": tuple(tuple(sorted(c)) for c in components6(X)),
        "valid_repairs": repairs,
        "certificate_count": len(certificates),
        "actions": action_records,
        "targeted_kill_count": sum(len(record["kills"]) for record in action_records),
        "full_counterexample": all(record["kills"] for record in action_records),
    }


def main():
    cases = []
    targeted = []
    full = []
    seen_X = set()
    for kind, patterns in (("Q2", BAD_Q2), ("Q3", BAD_Q3)):
        for pattern in patterns:
            X = physical_points(kind, pattern)
            if X in seen_X:
                continue
            seen_X.add(X)
            assert has_fail(X)
            audit = audit_anchor(X)
            if audit is None:
                continue
            audit["source_kind"] = kind
            cases.append(audit)
            if audit["targeted_kill_count"]:
                checked = audit_anchor(X, crosscheck=True)
                checked["source_kind"] = kind
                targeted.append(checked)
                if checked["full_counterexample"]:
                    full.append(checked)

    result = {
        "distinct_physical_bad_anchors": len(seen_X),
        "anchors_with_valid_repairs_and_certificates": len(cases),
        "targeted_kill_anchor_count": len(targeted),
        "full_counterexample_count": len(full),
        "targeted_hits": targeted,
        "full_counterexamples": full,
    }
    output = HERE / "c07d3e2_local_anchor_search.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D3E2 pure-anchor search complete")
    print("distinct bad anchors:", len(seen_X))
    print("anchors with valid repairs and certificates:", len(cases))
    print("targeted kill anchors:", len(targeted))
    print("full counterexamples:", len(full))
    print("JSON:", output)


if __name__ == "__main__":
    main()
