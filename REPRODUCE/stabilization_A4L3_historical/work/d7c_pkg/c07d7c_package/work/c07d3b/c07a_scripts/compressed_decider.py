r"""
C-06D.4a -- Production compressed_transition(), implementing
THEOREMS_C06D.md's C-06D.3a/3b LITERALLY, one section at a time.

Deliberately written from scratch (not copy-pasted from
exhaustive_local_windows.py / C-06D.3c) so that the triple-check in
audit_local_transition.py is a genuine independent cross-check, not two
copies of the same bug agreeing with each other.

Only read-only imports from the frozen S2.2 package (has_fail /
edge_cands / vertex_cands / voxel_corners / successors /
gen_all_monotone_paths) -- nothing in that package is modified.

Design note (K-layer masks): B-layer candidates are bounded (<=40,
M(p) union M(q), C-06D.2c+A2). K-layer candidates are NOT p/q-incident,
so they can't be found by scanning M(p) union M(q) -- they are
precomputed ONCE per (K,t) instance as "all masks touching K", which is
O(|K|)-sized and independent of path length/position, matching the
theorem's promise that K-layer occupancy needs no per-step history.
"""
from finite_window_classification import has_fail, BAD_Q2, BAD_Q3, edge_cands, vertex_cands, voxel_corners
from automaton_c06c2 import successors, gen_all_monotone_paths


# ---------------------------------------------------------------------
# Mask geometry primitives (re-derived independently from the raw
# candidate-generation rules -- same ground truth as has_fail, but not
# copy-pasted from the C-06D.3c audit script)
# ---------------------------------------------------------------------

_EDGE_OFFSETS = [
    (0, 0, 0, 'x'), (0, 1, 0, 'x'), (0, 0, 1, 'x'), (0, 1, 1, 'x'),
    (0, 0, 0, 'y'), (1, 0, 0, 'y'), (0, 0, 1, 'y'), (1, 0, 1, 'y'),
    (0, 0, 0, 'z'), (1, 0, 0, 'z'), (0, 1, 0, 'z'), (1, 1, 0, 'z'),
]


def masks_touching(points):
    """All Q2/Q3 masks whose candidate set includes >=1 point of
    `points`. `points` may be K, or any small point set (not
    necessarily a full path history)."""
    out = {}
    edge_anchors = set()
    for (x, y, z) in points:
        for (dx, dy, dz, axis) in _EDGE_OFFSETS:
            edge_anchors.add((x + dx, y + dy, z + dz, axis))
    for e in edge_anchors:
        cand, labels = edge_cands(e)
        out[('Q2', tuple(cand))] = dict(kind='Q2', positions=tuple(cand), labels=tuple(labels))
    vert_anchors = set()
    for v in points:
        vert_anchors |= voxel_corners(v)
    for vtx in vert_anchors:
        cand, labels = vertex_cands(vtx)
        out[('Q3', tuple(cand))] = dict(kind='Q3', positions=tuple(cand), labels=tuple(labels))
    return list(out.values())


def in_box(x, p, t):
    return all(min(p[a], t[a]) <= x[a] <= max(p[a], t[a]) for a in range(3))


def is_active(mask, anchor, t):
    return any(pos != anchor and in_box(pos, anchor, t) for pos in mask['positions'])


def is_disconnected(mask, occ_labels):
    bad_set = BAD_Q2 if mask['kind'] == 'Q2' else BAD_Q3
    return len(occ_labels) >= 2 and occ_labels in bad_set


# ---------------------------------------------------------------------
# sigma_3 representation and update (predecessor-only convention)
# ---------------------------------------------------------------------

def sigma_update(sigma, p, q):
    delta = tuple(q[a] - p[a] for a in range(3))
    shifted = tuple(tuple(u[a] - delta[a] for a in range(3)) for u in sigma)
    neg_delta = tuple(-d for d in delta)
    return (shifted + (neg_delta,))[-3:]


def sigma_points(p, sigma):
    return {tuple(p[a] + u[a] for a in range(3)) for u in sigma}


# ---------------------------------------------------------------------
# K-layer precomputation (once per instance, NOT per step)
# ---------------------------------------------------------------------

def build_K_masks(K):
    """All masks touching K, precomputed once. Independent of path
    length / position -- this is exactly the 'K-only layer' of
    THEOREMS_C06D.md's audit-scope note."""
    return masks_touching(K)


# ---------------------------------------------------------------------
# Phase A: the production compressed transition function
# ---------------------------------------------------------------------

def compressed_transition(K, K_masks, t, p, sigma, q):
    """
    Given a non-DEAD compressed state (p, sigma) and a next voxel q,
    return either ('DEAD', stats) or ((q, sigma_next), stats).

    Implements THEOREMS_C06D.md C-06D.3a case-by-case:
      - F (frozen at p): ignored -- already harmless (C-06D.1), and
        by C-06D.2d can never become active again, so no check needed.
      - B (active at p, incident to p or q): occupancy reconstructed
        from K + {p,q} + sigma_points -- checked for newly-frozen +
        disconnected.
      - K-layer (active at p, from precomputed K_masks, not already
        counted as B): occupancy is exactly K ∩ M (proved in
        THEOREMS_C06D.md's audit-scope note) -- checked the same way.
    """
    sigma_next = sigma_update(sigma, p, q)
    bridge_pts = {p, q} | sigma_points(p, sigma)

    seen_keys = set()
    b_touched = 0  # ALL masks incident to p or q (theorem's M(p)∪M(q) superset)
    b_active = 0   # actual B-layer count: active at p AND touching L (theorem's |B|)
    k_checked = 0
    dead = False

    # --- B-layer: masks incident to p or q ---
    for anchor in (p, q):
        for m in masks_touching({anchor}):
            key = (m['kind'], m['positions'])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            b_touched += 1
            if not is_active(m, p, t):
                continue  # frozen at p already -- ignore (non-DEAD hypothesis)
            b_active += 1
            if is_active(m, q, t):
                continue  # still active at q -- not a verdict point yet
            occ = frozenset(l for l, c in zip(m['labels'], m['positions'])
                             if c in K or c in bridge_pts)
            if is_disconnected(m, occ):
                dead = True
                break
        if dead:
            break

    # --- K-layer: precomputed masks touching K only ---
    if not dead:
        for m in K_masks:
            key = (m['kind'], m['positions'])
            if key in seen_keys:
                continue  # already covered as a B-layer mask
            seen_keys.add(key)
            k_checked += 1
            if not is_active(m, p, t):
                continue
            if is_active(m, q, t):
                continue
            occ = frozenset(l for l, c in zip(m['labels'], m['positions']) if c in K)
            if is_disconnected(m, occ):
                dead = True
                break

    stats = dict(B_touched=b_touched, B_active=b_active, K_checked=k_checked)
    if dead:
        return 'DEAD', stats
    return (q, sigma_next), stats


def initial_state(K, K_masks, s, t):
    """Compressed state for the empty prefix (P = [s])."""
    sigma0 = ()
    # A mask is frozen at s or active; sigma is empty (no predecessors).
    # Check DEAD directly: any mask (incident to s, or K-layer) that's
    # frozen at s and already disconnected using only K ∪ {s}.
    dead = False
    seen = set()
    for m in masks_touching({s}) + K_masks:
        key = (m['kind'], m['positions'])
        if key in seen:
            continue
        seen.add(key)
        if is_active(m, s, t):
            continue
        occ = frozenset(l for l, c in zip(m['labels'], m['positions'])
                         if c in K or c == s)
        if is_disconnected(m, occ):
            dead = True
            break
    if dead:
        return 'DEAD'
    return (s, sigma0)


# ---------------------------------------------------------------------
# Phase B: memoized compressed decision procedure
# ---------------------------------------------------------------------

def compressed_decide(K, s, t):
    """DEAD | (p, sigma_3) - only. No other state. Memoizes on
    (p, sigma) exactly as C-06D.3b licenses (Full Future-Language /
    Markov-Sufficiency Theorem)."""
    K = frozenset(K)
    K_masks = build_K_masks(K)
    stats = dict(
        states_generated=0,       # every non-DEAD outcome produced (may repeat)
        states_expanded=0,        # unique (p,sigma) keys actually recursed into (memo misses) -- this is the metric to compare against the N_sigma*V bound
        memo_hits=0,
        initial_dead_rejects=0,   # DEAD detected before any transition (the whole-instance start)
        dead_successor_transitions=0,  # DEAD detected as the outcome of a transition during search
        terminal_accepts=0, transition_calls=0,
        max_branching=0, B_touched=0, B_active_max=0, K_masks_precomputed=0,
    )
    memo = {}

    init = initial_state(K, K_masks, s, t)
    stats['states_generated'] += 1
    stats['K_masks_precomputed'] = len(K_masks)
    if init == 'DEAD':
        stats['initial_dead_rejects'] += 1
        return False, stats

    def rec(p, sigma):
        key = (p, sigma)
        if key in memo:
            stats['memo_hits'] += 1
            return memo[key]
        stats['states_expanded'] += 1
        if p == t:
            memo[key] = True
            stats['terminal_accepts'] += 1
            return True
        succs = successors(p, t)
        stats['max_branching'] = max(stats['max_branching'], len(succs))
        result = False
        for q in succs:
            stats['transition_calls'] += 1
            outcome, tstats = compressed_transition(K, K_masks, t, p, sigma, q)
            stats['B_touched'] += tstats['B_touched']
            stats['B_active_max'] = max(stats['B_active_max'], tstats['B_active'])
            if outcome == 'DEAD':
                stats['dead_successor_transitions'] += 1
                continue
            new_p, new_sigma = outcome
            stats['states_generated'] += 1
            if rec(new_p, new_sigma):
                result = True
                break
        memo[key] = result
        return result

    p0, sigma0 = init
    decision = rec(p0, sigma0)
    return decision, stats
