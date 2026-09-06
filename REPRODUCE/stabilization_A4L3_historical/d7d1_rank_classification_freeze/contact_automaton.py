"""D7D2-A1 prototype: (p, sigma, A) contact-accumulator product automaton.

Extends the frozen compressed_decider.compressed_transition (legality only,
UNCHANGED, not re-implemented or re-derived) with a small saturating
annotation A that tracks how many *other* (non-endpoint) components the
path-so-far has become 6-adjacent to, saturating at 2 ("SAT") since rho >= 4
requires at least two extra contacts beyond the two endpoint components
that are always merged by construction.

A in {None, <other-component index>, 'SAT'}.

This module answers, for one certificate (left, right) and background K:
    does there exist a Q2/Q3-compatible monotone path s->t that touches
    >= 2 other components (equivalently: some resulting bridge action has
    rho >= 4)?
without generating a single full path or enumerating monotone orderings
(no gen_all_monotone_paths call anywhere in this module).

Correctness of this module is NOT assumed. It is cross-validated against
full brute-force enumeration (certificate_bridge_actions) in
verify_contact_automaton.py in this same folder, on real D7D1 roots,
before being trusted for anything beyond this checkpoint.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKPOINT_ROOT = HERE.parent
PACKAGE = CHECKPOINT_ROOT / "work" / "d7c_pkg" / "c07d7c_package"
WORK = PACKAGE / "work"

for dependency in (
    WORK / "c07d3e",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

from compressed_decider import build_K_masks, compressed_transition, initial_state  # noqa: E402
from automaton_c06c2 import successors  # noqa: E402
from c07d3e_component_viability import shortest_endpoint_pairs  # noqa: E402


def touched_ids(q, other_components):
    ids = set()
    for idx, comp in enumerate(other_components):
        for p in comp:
            if sum(abs(a - b) for a, b in zip(q, p)) == 1:
                ids.add(idx)
                break
    return ids


def promote(A, touched):
    if A == "SAT":
        return "SAT"
    if len(touched) >= 2:
        return "SAT"
    if len(touched) == 1:
        c = next(iter(touched))
        if A is None or A == c:
            return c if A is None else A
        return "SAT"
    return A


def contact_decide(K, other_components, s, t):
    """Level-by-level (rank = L1(p,t), strictly decreasing each step, so
    this is a DAG with no cycles) forward DP over (p, sigma) merging the
    SET of distinct A-annotations reachable at each compressed state
    before any of that level's states are expanded.

    Returns (exists_path, flag) where flag in {None, 'NONE', 'ONE', 'SAT'}:
      None  -> no compatible path exists at all
      'NONE'-> compatible paths exist but none touches any extra component
      'ONE' -> some compatible path touches exactly one extra component
      'SAT' -> some compatible path touches >= 2 extra components
               (equivalently: some action has rho >= 4)
    """
    K = frozenset(K)
    K_masks = build_K_masks(K)

    init = initial_state(K, K_masks, s, t)
    if init == "DEAD":
        return False, None

    p0, sigma0 = init
    A0 = promote(None, touched_ids(p0, other_components))

    frontier = {(p0, sigma0): {A0}}
    best_at_t = set()

    while frontier:
        next_frontier = {}
        for (p, sigma), A_set in frontier.items():
            if p == t:
                best_at_t |= A_set
                continue
            for q in successors(p, t):
                outcome, _ = compressed_transition(K, K_masks, t, p, sigma, q)
                if outcome == "DEAD":
                    continue
                new_p, new_sigma = outcome
                touched = touched_ids(q, other_components)
                new_A_set = {promote(A, touched) for A in A_set}
                key = (new_p, new_sigma)
                if key in next_frontier:
                    next_frontier[key] |= new_A_set
                else:
                    next_frontier[key] = set(new_A_set)
        frontier = next_frontier

    if not best_at_t:
        return False, None
    if "SAT" in best_at_t:
        return True, "SAT"
    if any(a is not None for a in best_at_t):
        return True, "ONE"
    return True, "NONE"


def certificate_max_rho_at_least_4(root_state, comps, left, right):
    """High-level entry point: given the two endpoint components of a
    certificate (as frozensets of points, matching components6 output),
    decide whether some compatible bridge action has rho >= 4, without
    enumerating monotone paths.
    """
    other_components = [c for c in comps if c != left and c != right]
    distance, pairs = shortest_endpoint_pairs(left, right)
    K = frozenset(root_state)
    overall_exists = False
    overall_flag = None
    for s, t in pairs:
        exists, flag = contact_decide(K, other_components, s, t)
        if exists:
            overall_exists = True
            if flag == "SAT":
                overall_flag = "SAT"
            elif flag == "ONE" and overall_flag != "SAT":
                overall_flag = "ONE"
            elif overall_flag is None:
                overall_flag = flag
    return overall_exists, overall_flag
