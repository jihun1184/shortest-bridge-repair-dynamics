"""
Reproduces manuscript Table 3, L=4 row: the decision-support
disjointness check for the six exceptional (a,b,q) instances at
chain length 4.

Expected output:
    chain_L4: 6/6 instances checked, 0 leaks
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from stage2_repair_core import candidate_voxels  # noqa: E402

REF_DIR = os.path.join(os.path.dirname(__file__), "..", "reference_results")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def N_of(v, box=3):
    result = set()
    for cell in itertools.product(
        range(v[0] * 2 - box, v[0] * 2 + box + 1),
        range(v[1] * 2 - box, v[1] * 2 + box + 1),
        range(v[2] * 2 - box, v[2] * 2 + box + 1),
    ):
        cv = candidate_voxels(cell)
        if v in cv and len(cv) in (8, 4):
            result.add(cell)
    return result


def check_instance(a, b, q, D_M, label):
    Na, Nb, Nq = N_of(a), N_of(b), N_of(q)
    leak_cells = sorted(h for h in (Na | Nb) - Nq if candidate_voxels(h) & D_M)
    return {"label": label, "a": a, "b": b, "q": q,
            "leak": len(leak_cells) > 0, "leak_cells": leak_cells}


# The six exceptional orbits at L=4 (see MANIFEST.json for provenance of
# these coordinates: independently re-verified against the manuscript's
# six-orbit taxonomy in Section 5).
L4_INSTANCES = {
    "orbit15": ((-3, -2, -2), (-2, -3, -2), (-2, -2, -2)),
    "orbit17": ((-3, -2, -2), (-2, -2, -3), (-2, -2, -2)),
    "orbit21": ((-3, -2, -1), (-2, -3, -1), (-2, -2, -1)),
    "orbit25": ((-3, -2, 0), (-2, -3, 0), (-2, -2, 0)),
    "orbit33": ((-3, -1, -2), (-2, -1, -3), (-2, -1, -2)),
    "orbit45": ((-3, 0, -2), (-2, 0, -3), (-2, 0, -2)),
}

if __name__ == "__main__":
    data = json.load(open(os.path.join(REF_DIR, "chain_L4_base_M0_reference.json")))
    M0 = data.get("M0", data.get("base"))
    D_M = {tuple(v) for B in M0 for v in B}
    print(f"D_M(chain_L4) size: {len(D_M)}")

    results = [check_instance(a, b, q, D_M, label) for label, (a, b, q) in L4_INSTANCES.items()]
    n_leak = sum(r["leak"] for r in results)
    if len(results) != 6 or n_leak != 0:
        raise AssertionError(f"expected 6/6 leak-free instances, got {len(results)} with {n_leak} leaks")
    print(f"chain_L4: {len(results)} instances checked, {n_leak} leaks found")
    for r in results:
        print(" ", r["label"], "leak=", r["leak"])

    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump({"L4": results}, open(os.path.join(OUT_DIR, "disjointness_L4_result.json"), "w"),
               indent=2, default=str)
    print("\nSaved outputs/disjointness_L4_result.json")
