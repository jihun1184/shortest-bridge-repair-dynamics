r"""
S2.0C-06C.2 -- Finite-state compatible-bridge decision automaton.

Implements the DAG search described in the C-06C.2 handoff:
  state = endpoint p only (C-06C.1: endpoint Markov property, PROVEN)
  successors = up to 3 monotone unit steps toward t
  early ACCEPT = C-06A exact future-escape criterion
    (R(p,t)\{p}) ∩ N_inf^1(K) = empty  =>  every remaining completion is safe
    (this pruning is now fully justified: C-06A [no future K-interaction] +
     C-06B [pure bridge never self-violates])
  transition compatibility = Q2/Q3 has_fail check using ONE representative
    witness path per state (any compatible prefix works, by C-06C.1)
  duplicate endpoints reached again => merge (no re-expansion)

Cross-validated against brute-force enumeration of ALL shortest monotone
paths s -> t for the same (K, s, t).
"""
import itertools
from collections import deque
from finite_window_classification import has_fail, AXES, apply_step


def box_predicts_safe(p, t, K):
    """C-06A criterion: True iff no future (post-p) point on ANY shortest
    monotone completion p->t can Chebyshev-touch K."""
    for k in K:
        ivs = []
        ok = True
        for a in range(3):
            lo, hi = min(p[a], t[a]), max(p[a], t[a])
            klo, khi = k[a] - 1, k[a] + 1
            nlo, nhi = max(lo, klo), min(hi, khi)
            if nlo > nhi:
                ok = False
                break
            ivs.append((nlo, nhi))
        if not ok:
            continue
        # exclude p itself from the overlap region
        # (box \ {p}) ∩ neighborhood(k) != empty ?
        pts_in_overlap_not_p = False
        # enumerate box overlap region (small: each axis range <=3)
        for x in range(ivs[0][0], ivs[0][1] + 1):
            for y in range(ivs[1][0], ivs[1][1] + 1):
                for z in range(ivs[2][0], ivs[2][1] + 1):
                    if (x, y, z) != p:
                        pts_in_overlap_not_p = True
                        break
                if pts_in_overlap_not_p:
                    break
            if pts_in_overlap_not_p:
                break
        if pts_in_overlap_not_p:
            return False  # some k allows a future touch -> NOT safe
    return True  # no k allows any future touch -> safe


def successors(p, t):
    succs = []
    for a in range(3):
        if p[a] != t[a]:
            step = [0, 0, 0]
            step[a] = 1 if t[a] > p[a] else -1
            succs.append(tuple(p[i] + step[i] for i in range(3)))
    return succs


def automaton_decide(K, s, t, collect_stats=False):
    """Returns (exists: bool, stats: dict)."""
    K = frozenset(K)
    stats = dict(states_visited=0, states_merged=0, transitions_checked=0,
                 transitions_rejected=0, escape_accepts=0)

    if has_fail({s} | K):
        return False, stats  # start itself already incompatible

    witness = {s: (s,)}  # p -> representative compatible path tuple
    visited = set([s])
    queue = deque([s])
    stats['states_visited'] += 1

    if s == t:
        return True, stats
    if box_predicts_safe(s, t, K):
        stats['escape_accepts'] += 1
        return True, stats

    while queue:
        p = queue.popleft()
        W = witness[p]
        for q in successors(p, t):
            stats['transitions_checked'] += 1
            new_path = W + (q,)
            if has_fail(set(new_path) | K):
                stats['transitions_rejected'] += 1
                continue  # incompatible transition
            if q == t:
                return True, stats
            if box_predicts_safe(q, t, K):
                stats['escape_accepts'] += 1
                return True, stats
            if q in visited:
                stats['states_merged'] += 1
                continue
            visited.add(q)
            witness[q] = new_path
            queue.append(q)
            stats['states_visited'] += 1

    return False, stats


def gen_all_monotone_paths(s, t):
    """Brute force: all shortest coordinate-wise monotone paths s->t."""
    diffs = [t[a] - s[a] for a in range(3)]
    steps = []
    for a in range(3):
        sign = 1 if diffs[a] > 0 else -1
        for _ in range(abs(diffs[a])):
            steps.append(a)
    paths = []
    seen_orders = set()
    for order in set(itertools.permutations(steps)):
        pt = s
        path = [pt]
        for a in order:
            sign = 1 if diffs[a] > 0 else -1
            step = [0, 0, 0]
            step[a] = sign
            pt = tuple(pt[i] + step[i] for i in range(3))
            path.append(pt)
        paths.append(tuple(path))
    return paths


def brute_force_decide(K, s, t):
    K = frozenset(K)
    paths = gen_all_monotone_paths(s, t)
    total = len(paths)
    compatible = 0
    for path in paths:
        if not has_fail(set(path) | K):
            compatible += 1
    return compatible > 0, total, compatible
