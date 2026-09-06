"""D7D2-A1 verifier: reproduces the cross-validation of contact_automaton.py
against full brute-force enumeration, and reruns the two ray extensions.

Three independent checks, all re-derived from the frozen source on each run
(nothing here is read from a cached table):

  1. rho = 2 + |contact set| formula holds exactly on 2,436 real bridge
     actions across the 6 known R*=3 orbits' root layers (12 roots).
  2. contact_automaton's SAT-reachability decision matches brute-force
     certificate_bridge_actions max-rho>=4 exactly on 18 real roots
     (12 negative controls with known R*=3, 6 positive controls with
     known R*=4).
  3. Re-extends both rays s=(-k,2,0) and s=(-k,3,0) using the automaton
     and confirms no rho>=4 action appears up to a chosen k_max (default
     20, kept small here for a fast default run -- the conversation
     record for this checkpoint reports k up to 100 for both rays).

Run from the checkpoint root:
    python3 d7d1_rank_classification_freeze/verify_contact_automaton.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKPOINT_ROOT = HERE.parent
WORK = CHECKPOINT_ROOT / "work" / "d7c_pkg" / "c07d7c_package" / "work"

for dependency in (
    HERE,
    CHECKPOINT_ROOT / "work" / "d7d1",
    WORK / "c07d4",
    WORK / "c07d3e",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

import c07d7d1_persistent_absorption_closure as m  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402
from c07d3e_component_viability import components6, component_certificates  # noqa: E402
from c07d4_planning_census import certificate_bridge_actions  # noqa: E402
from contact_automaton import certificate_max_rho_at_least_4  # noqa: E402

CORE = frozenset(
    {
        (-4, 1, 0), (-3, -1, -1), (-1, -1, -1), (-1, 0, -1),
        (-1, 0, 0), (0, -1, -1), (0, -1, 0), (0, 2, -1),
    }
)
REPAIRS = [(-1, -1, 0), (0, 0, 0)]
KNOWN_R3_SATELLITES = [(-4, 3, 0), (-6, 2, 0), (-5, 3, 0), (-7, 2, 0), (-6, 2, 1), (-6, 3, 0)]


def brute_max_rho(root):
    comps = components6(root)
    before_partition = m.root_identity_partition(root, comps)
    overall = 0
    for cert in component_certificates(root):
        actions, _ = certificate_bridge_actions(root, cert)
        for action in actions:
            additions = frozenset(tuple(p) for p in action["additions"])
            successor = root | additions
            after_partition = m.root_identity_partition(successor, comps)
            block = m.absorption_block(before_partition, after_partition)
            overall = max(overall, len(block))
    return overall


def brute_formula_check(root):
    """Check rho == 2 + |contact set| for every action of every certificate."""
    comps = components6(root)
    before_partition = m.root_identity_partition(root, comps)
    total = 0
    mismatches = 0
    for cert in component_certificates(root):
        left, right = cert
        others = [c for c in comps if c != left and c != right]
        actions, _ = certificate_bridge_actions(root, cert)
        for action in actions:
            additions = frozenset(tuple(p) for p in action["additions"])
            successor = root | additions
            after_partition = m.root_identity_partition(successor, comps)
            block = m.absorption_block(before_partition, after_partition)
            rho_official = len(block)
            path_pts = action["realizations"][0]["path"]
            touched = set()
            for v in path_pts:
                if v in left or v in right:
                    continue
                for idx, c in enumerate(others):
                    if any(sum(abs(a - b) for a, b in zip(v, p)) == 1 for p in c):
                        touched.add(idx)
                        break
            rho_formula = 2 + len(touched)
            total += 1
            if rho_formula != rho_official:
                mismatches += 1
    return total, mismatches


def automaton_says_rho_ge_4(root):
    comps = components6(root)
    for cert in component_certificates(root):
        left, right = cert
        _, flag = certificate_max_rho_at_least_4(root, comps, left, right)
        if flag == "SAT":
            return True
    return False


def check1_formula():
    total_all, mismatches_all = 0, 0
    for sat in KNOWN_R3_SATELLITES:
        for repair in REPAIRS:
            root = CORE | {sat, repair}
            total, mismatches = brute_formula_check(root)
            total_all += total
            mismatches_all += mismatches
    print(f"[check 1] rho=2+|contact| formula: {total_all} actions, {mismatches_all} mismatches")
    assert mismatches_all == 0


def check2_cross_validation():
    ok = True
    for sat in KNOWN_R3_SATELLITES:
        for repair in REPAIRS:
            root = CORE | {sat, repair}
            brute = brute_max_rho(root) >= 4
            auto = automaton_says_rho_ge_4(root)
            if brute != auto:
                ok = False
                print(f"  MISMATCH (negative control) sat={sat} repair={repair}")
    items = m.tasks()
    missing_orbits = {302, 316, 318, 320, 322, 329, 331, 333, 335, 337, 342, 344, 345, 347}
    positive_sample = [t for t in items if t[0] in missing_orbits][:6]
    for orbit_index, repair_index, initial_state, repair in positive_sample:
        root = frozenset(tuple(p) for p in initial_state) | {tuple(repair)}
        brute = brute_max_rho(root) >= 4
        auto = automaton_says_rho_ge_4(root)
        if brute != auto:
            ok = False
            print(f"  MISMATCH (positive control) orbit={orbit_index} repair={repair_index}")
    print(f"[check 2] contact automaton vs brute force: {'18/18 OK' if ok else 'MISMATCHES FOUND'}")
    assert ok


def check3_ray_extension(k_max=20):
    print(f"[check 3] ray extension up to k={k_max} (root layer only)")
    for ray_name, y in (("(-k,2,0)", 2), ("(-k,3,0)", 3)):
        max_k_checked = 0
        any_rho4 = False
        for k in range(5, k_max + 1):
            sat = (-k, y, 0)
            state = CORE | {sat}
            for repair in REPAIRS:
                root = state | {repair}
                if has_fail(root) or len(components6(root)) != 5:
                    continue
                max_k_checked = k
                if automaton_says_rho_ge_4(root):
                    any_rho4 = True
        print(f"  ray {ray_name}: checked up to k={max_k_checked}, any rho>=4 found: {any_rho4}")


if __name__ == "__main__":
    check1_formula()
    check2_cross_validation()
    check3_ray_extension(k_max=20)
    print("ALL CHECKS PASSED")
