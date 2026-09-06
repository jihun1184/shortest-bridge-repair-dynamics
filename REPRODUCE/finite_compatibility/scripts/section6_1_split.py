"""
Reproduces manuscript Section 6.1's worked example (Figure 4).

Expected output:
    |M0(chain_3)| = 36
    compatible (True): 9   incompatible (False): 27
    restriction class B ∩ L(q) = {}                : n=27, verdict=False (uniform)
    restriction class B ∩ L(q) = {(-1,-1,-1)}       : n=9,  verdict=True  (uniform)
    => compatibility depth of q is 1 (single decision layer, z=-1)
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from geometry_utils import SEED, shift  # noqa: E402
from stage2_repair_core import pwc_verdict  # noqa: E402

REF_DIR = os.path.join(os.path.dirname(__file__), "..", "reference_results")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")

A = (-3, -2, -2)
B_PT = (-2, -3, -2)
Q = (-2, -2, -2)


def L_of(v, r=1):
    return {(v[0] + dx, v[1] + dy, v[2] + dz)
            for dx in range(-r, r + 1) for dy in range(-r, r + 1) for dz in range(-r, r + 1)}


if __name__ == "__main__":
    chain_L3 = frozenset(set(SEED) | shift(SEED, (0, 0, 1)))
    F_pair = chain_L3 | {A, B_PT}

    M0 = json.load(open(os.path.join(REF_DIR, "chain_L3_base_M0_reference.json")))["M0"]
    M0 = [frozenset(tuple(v) for v in B) for B in M0]
    print(f"|M0(chain_L3)| = {len(M0)}")

    Lq = L_of(Q)
    classes = defaultdict(list)
    for B in M0:
        Z = F_pair.symmetric_difference(B | {Q})
        verdict = pwc_verdict(Z)
        restriction = tuple(sorted(B & Lq))
        classes[restriction].append(verdict)

    n_true = sum(len(v) for v in classes.values() if v and v[0])
    n_false = sum(len(v) for v in classes.values() if v and not v[0])
    if n_true != 9 or n_false != 27 or len(classes) != 2 or any(len(set(v)) != 1 for v in classes.values()):
        raise AssertionError("expected a uniform 9/27 split across exactly two restriction classes")
    print(f"compatible (True): {n_true}   incompatible (False): {n_false}")

    print("\nrestriction classes:")
    summary = {}
    for cls, verdicts in classes.items():
        uniform = len(set(verdicts)) == 1
        print(f"  B ∩ L(q) = {cls}: n={len(verdicts)}, uniform={uniform}, verdict={verdicts[0]}")
        summary[str(cls)] = {"n": len(verdicts), "uniform": uniform, "verdict": verdicts[0]}

    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump({"a": A, "b": B_PT, "q": Q, "n_true": n_true, "n_false": n_false,
               "restriction_classes": summary},
              open(os.path.join(OUT_DIR, "section6_1_split_result.json"), "w"), indent=2)
    print("\nSaved outputs/section6_1_split_result.json")
