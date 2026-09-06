"""
Reproduces the consistency check underlying manuscript Lemma 3 (Bridge
Lemma) / Lemma 4 (Column Intersection Lemma) applied to the chain_5
classification.

Expected output:
    12 orbits with a nontrivial dependency window checked
    12 PASS / 0 FAIL
"""
import json
import os

REF_DIR = os.path.join(os.path.dirname(__file__), "..", "reference_results")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")

# chain_5 spans z = -1 .. 3; exact_window entries are labeled c0..c4 -> z = i-1
LABEL_TO_Z = {f"c{i}": i - 1 for i in range(5)}

if __name__ == "__main__":
    rows = json.load(open(os.path.join(REF_DIR, "chain_L5_orbit_audit_reference.json")))

    results = []
    n_checked = n_pass = n_fail = 0

    for row in rows:
        exact_window = row.get("exact_window", [])
        if not exact_window:
            continue  # depth-0 orbit: nothing for the Bridge Lemma to constrain

        window_zs = [LABEL_TO_Z[c] for c in exact_window]
        wz_min, wz_max = min(window_zs), max(window_zs)

        exceptional_qs = [(eval(q_str), cnt) for q_str, cnt in row.get("compat_counts", {}).items()
                           if cnt < 324]
        if not exceptional_qs:
            continue

        n_checked += 1
        orbit_ok = True
        for q, _cnt in exceptional_qs:
            qz = q[2]
            fits = (wz_min >= qz - 1) and (wz_max <= qz + 1)
            orbit_ok = orbit_ok and fits

        n_pass += orbit_ok
        n_fail += (not orbit_ok)
        results.append({"orbit_id": row["orbit_id"], "status": "PASS" if orbit_ok else "FAIL"})

    print(f"Orbits with nontrivial dependency window checked: {n_checked}")
    if (n_checked, n_pass, n_fail) != (12, 12, 0):
        raise AssertionError(f"expected 12/12 PASS and 0 FAIL, got {n_checked}/{n_pass}/{n_fail}")
    print(f"  PASS: {n_pass}")
    print(f"  FAIL: {n_fail}")

    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump({"n_checked": n_checked, "n_pass": n_pass, "n_fail": n_fail, "results": results},
               open(os.path.join(OUT_DIR, "bridge_lemma_result.json"), "w"), indent=2)
    print("\nSaved outputs/bridge_lemma_result.json")
