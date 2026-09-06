"""
Reproduces manuscript Table 3, L=3 and L=5 rows: the decision-support
disjointness check.

Expected output:
    chain_L3: 3/3 instances checked, 0 leaks
    chain_L5: 12/12 instances checked, 0 leaks
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
    """Cells h (vertex or edge cells) with v in candidate_voxels(h)."""
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


def D_M_from(ref_file):
    M0 = json.load(open(ref_file))["M0"]
    return {tuple(v) for B in M0 for v in B}


if __name__ == "__main__":
    results = {}

    D_M_L5 = D_M_from(os.path.join(REF_DIR, "chain_L5_base_M0_reference.json"))
    rows = json.load(open(os.path.join(REF_DIR, "chain_L5_orbit_audit_reference.json")))
    L5_results = []
    for row in rows:
        a, b = (tuple(x) for x in row["canonical_pair"])
        for q_str, cnt in row.get("compat_counts", {}).items():
            if cnt < 324:
                L5_results.append(check_instance(a, b, eval(q_str), D_M_L5, row["orbit_id"]))
    n_leak = sum(r["leak"] for r in L5_results)
    print(f"chain_L5: {len(L5_results)} instances checked, {n_leak} leaks found")
    results["L5"] = L5_results

    D_M_L3 = D_M_from(os.path.join(REF_DIR, "chain_L3_base_M0_reference.json"))
    L3_pairs = {
        "section6_1_depth1": ((-3, -2, -2), (-2, -3, -2), (-2, -2, -2)),
        "depth2_instance": ((-3, -2, -1), (-2, -3, -1), (-2, -2, -1)),
        "depth3_instance": ((-3, -2, 0), (-2, -3, 0), (-2, -2, 0)),
    }
    L3_results = [check_instance(a, b, q, D_M_L3, tag) for tag, (a, b, q) in L3_pairs.items()]
    n_leak_l3 = sum(r["leak"] for r in L3_results)
    if len(L5_results) != 12 or n_leak != 0 or len(L3_results) != 3 or n_leak_l3 != 0:
        raise AssertionError("expected L5 12/12 and L3 3/3 leak-free instances")
    print(f"chain_L3: {len(L3_results)} instances checked, {n_leak_l3} leaks found")
    for r in L3_results:
        print(" ", r["label"], "leak=", r["leak"])
    results["L3"] = L3_results

    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(results, open(os.path.join(OUT_DIR, "disjointness_L3_L5_result.json"), "w"),
              indent=2, default=str)
    print("\nSaved outputs/disjointness_L3_L5_result.json")
