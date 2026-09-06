"""
Reproduces manuscript Table 2 (chain_5 compatibility-depth histogram,
76 orbits / 528 pairs) and Corollary 7 (sharpness: max depth = 3).

Expected output:
    total: 76 orbits, 528 pairs
    depth 0: 64 orbits, 468 pairs
    depth 1:  6 orbits,  40 pairs
    depth 2:  2 orbits,   8 pairs
    depth 3:  4 orbits,  12 pairs
    max depth observed: 3  (sharpness of Theorem 5's bound)
"""
import json
import os
from collections import Counter

REF_DIR = os.path.join(os.path.dirname(__file__), "..", "reference_results")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")

if __name__ == "__main__":
    rows = json.load(open(os.path.join(REF_DIR, "chain_L5_orbit_audit_reference.json")))

    orbit_hist = Counter(r["compatibility_depth"] for r in rows)
    pair_hist = Counter()
    for r in rows:
        pair_hist[r["compatibility_depth"]] += r["orbit_size"]

    n_orbits = len(rows)
    n_pairs = sum(r["orbit_size"] for r in rows)
    max_depth = max(orbit_hist)

    expected_orbits = {0: 64, 1: 6, 2: 2, 3: 4}
    expected_pairs = {0: 468, 1: 40, 2: 8, 3: 12}
    if (n_orbits, n_pairs, dict(orbit_hist), dict(pair_hist), max_depth) != (
        76, 528, expected_orbits, expected_pairs, 3
    ):
        raise AssertionError("depth histogram does not match the frozen expected result")

    print(f"total orbits: {n_orbits}  total pairs: {n_pairs}")
    for d in sorted(orbit_hist):
        print(f"  depth {d}: {orbit_hist[d]:3d} orbits, {pair_hist[d]:4d} pairs")
    print(f"max depth observed: {max_depth}")

    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump({
        "n_orbits": n_orbits, "n_pairs": n_pairs,
        "orbit_histogram": dict(sorted(orbit_hist.items())),
        "pair_histogram": dict(sorted(pair_hist.items())),
        "max_depth": max_depth,
        "method": "stored_plus_reaggregated_from_raw_per_orbit_records",
    }, open(os.path.join(OUT_DIR, "depth_histogram_result.json"), "w"), indent=2)
    print("\nSaved outputs/depth_histogram_result.json")
