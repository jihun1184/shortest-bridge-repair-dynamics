"""C07-D3E1: certificate-aligned attack around the D3C destructive anchor.

The remote singleton is enumerated while every counted kill is required to:
  (1) start from a bridge-repairable genuine component certificate,
  (2) remain unresolved after the valid N1c repair, and
  (3) have no compatible bridge over any descendant d6-minimizing endpoints.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "c07d3b"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PARENT / "c07a_scripts"))

from compressed_decider import is_disconnected, masks_touching  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402

from c07d3e_component_viability import (  # noqa: E402
    certificate_viability,
    component_bridge_exists,
    component_certificates,
    components6,
    neighbors6,
)


ANCHOR = frozenset(
    {
        (-2, -1, -1),
        (-1, -2, -1),
        (-1, -1, -1),
        (-1, -1, 0),
    }
)


def occupied_labels(mask, points):
    points = set(points)
    return frozenset(
        label
        for position, label in zip(mask["positions"], mask["labels"])
        if position in points
    )


def bad_mask_records(points):
    points = frozenset(points)
    records = []
    seen = set()
    for mask in masks_touching(points):
        key = (mask["kind"], mask["positions"])
        if key in seen:
            continue
        seen.add(key)
        occupancy = occupied_labels(mask, points)
        if is_disconnected(mask, occupancy):
            records.append((mask, occupancy))
    return records


def valid_single_add_repairs(X):
    universe = sorted(
        {
            position
            for mask, _ in bad_mask_records(X)
            for position in mask["positions"]
            if position not in X
        }
    )
    return tuple(v for v in universe if not has_fail(set(X) | {v}))


def contact_component_count(v, components):
    neighborhood = set(neighbors6(v))
    return sum(bool(neighborhood & set(component)) for component in components)


def audit_fixture(X, *, crosscheck=False):
    certificates = component_certificates(X)
    if len(certificates) != 1:
        return None
    certificate = certificates[0]
    before_exists, before_audit = component_bridge_exists(
        X, *certificate, crosscheck=crosscheck
    )
    if not before_exists:
        return None
    repairs = valid_single_add_repairs(X)
    if not repairs:
        return None
    action_audits = []
    for v in repairs:
        viable, audit = certificate_viability(
            X, v, certificate, crosscheck=crosscheck
        )
        audit["contact_component_count"] = contact_component_count(
            v, components6(X)
        )
        action_audits.append(audit)
    return {
        "X": tuple(sorted(X)),
        "components": tuple(tuple(sorted(c)) for c in components6(X)),
        "certificate_count": 1,
        "before_bridge": before_audit,
        "valid_repairs": repairs,
        "action_audits": action_audits,
        "full_counterexample": all(not audit["viable"] for audit in action_audits),
        "targeted_kill_count": sum(not audit["viable"] for audit in action_audits),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=int, default=4)
    args = parser.parse_args()

    values = range(-args.radius, args.radius + 1)
    fixtures = 0
    bridge_repairable = 0
    targeted = []
    full = []
    for remote in itertools.product(values, repeat=3):
        if remote in ANCHOR:
            continue
        X = ANCHOR | {remote}
        if len(components6(X)) != 2:
            continue
        fixtures += 1
        audit = audit_fixture(X)
        if audit is None:
            continue
        bridge_repairable += 1
        if audit["targeted_kill_count"]:
            # Re-run every reported hit with compressed/full-order cross-check.
            audit = audit_fixture(X, crosscheck=True)
            targeted.append(audit)
            if audit["full_counterexample"]:
                full.append(audit)

    result = {
        "radius": args.radius,
        "anchor": tuple(sorted(ANCHOR)),
        "two_component_fixtures": fixtures,
        "bridge_repairable_with_valid_N1c_action": bridge_repairable,
        "targeted_kill_fixture_count": len(targeted),
        "full_counterexample_count": len(full),
        "targeted_hits": targeted,
        "full_counterexamples": full,
    }
    output = HERE / f"c07d3e1_targeted_search_r{args.radius}.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D3E1 targeted certificate-aligned search complete")
    print("two-component fixtures:", fixtures)
    print("bridge-repairable fixtures with valid repair:", bridge_repairable)
    print("targeted kill fixtures:", len(targeted))
    print("full counterexamples:", len(full))
    print("JSON:", output)


if __name__ == "__main__":
    main()
