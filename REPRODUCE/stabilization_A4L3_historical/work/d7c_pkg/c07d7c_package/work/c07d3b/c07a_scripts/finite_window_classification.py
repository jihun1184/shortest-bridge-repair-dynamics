r"""
S2.0C-06B -- Finite window classification (replaces the length<=9 probe with
a length-independent proof).

Justification for restricting to 4-point windows (direct corollary of
already-PROVEN facts, not a new theorem -- see accompanying handoff note):

  1. has_fail() checks Q2 masks (edge candidates: a 2x2 square of voxels,
     pairwise Chebyshev distance <=1) and Q3 masks (vertex candidates: the
     8 corners of a unit cube, pairwise Chebyshev distance <=1). So ANY two
     voxels that can co-occur in the same Q2/Q3 mask are, by construction,
     Chebyshev-touching (distance <=1).
  2. S2.0C-06A / S2.1's touch-locality theorem (pigeonhole on 3 axes) proves
     two monotone-path points can Chebyshev-touch only if their index-gap
     is <=3.
  3. Combining (1)+(2): if p_j is the point whose addition first creates a
     violation, every other member of that violating mask must touch p_j,
     hence have index in [j-3, j-1]. So the violating mask is a subset of
     {p_{j-3}, p_{j-2}, p_{j-1}, p_j} -- at most 4 points, 3 consecutive
     steps. No separate proof needed for this reduction step.

This script enumerates EVERY possible 3-step monotone window shape (i.e.
every window that could appear starting at any point of any longer monotone
bridge -- since axis/sign commitments from context can only RESTRICT further
choices, never add new window shapes, the unconstrained-from-a-fresh-origin
enumeration below is a superset of every window shape that could occur
in-context) and checks has_fail on each. If none of these finitely many
windows ever fails, self-violation is impossible for monotone bridges of
ANY length -- a real proof, not a probe.
"""
import itertools
import networkx as nx


def disconnected_masks(r):
    G = nx.hypercube_graph(r)
    V = list(G.nodes())
    bad = set()
    for size in range(2, len(V) + 1):
        for S in itertools.combinations(V, size):
            if not nx.is_connected(G.subgraph(S)):
                bad.add(frozenset(S))
    return bad


BAD_Q2 = disconnected_masks(2)
BAD_Q3 = disconnected_masks(3)


def voxel_corners(v):
    x, y, z = v
    return {(x + dx, y + dy, z + dz) for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)}


def vertex_cands(vtx):
    a, b, c = vtx
    cand = [(a + dx, b + dy, c + dz) for dx in (-1, 0) for dy in (-1, 0) for dz in (-1, 0)]
    labels = [(0 if dx == -1 else 1, 0 if dy == -1 else 1, 0 if dz == -1 else 1)
              for dx in (-1, 0) for dy in (-1, 0) for dz in (-1, 0)]
    return cand, labels


def edge_cands(edge):
    a, b, c, axis = edge
    if axis == 'z':
        cand = [(a + dx, b + dy, c) for dx in (-1, 0) for dy in (-1, 0)]
    elif axis == 'y':
        cand = [(a + dx, b, c + dz) for dx in (-1, 0) for dz in (-1, 0)]
    else:
        cand = [(a, b + dy, c + dz) for dy in (-1, 0) for dz in (-1, 0)]
    labels = [(0, 0), (0, 1), (1, 0), (1, 1)]
    return cand, labels


def has_fail(vs):
    edges = set()
    for (x, y, z) in vs:
        for (dx, dy, dz, axis) in [
            (0, 0, 0, 'x'), (0, 1, 0, 'x'), (0, 0, 1, 'x'), (0, 1, 1, 'x'),
            (0, 0, 0, 'y'), (1, 0, 0, 'y'), (0, 0, 1, 'y'), (1, 0, 1, 'y'),
            (0, 0, 0, 'z'), (1, 0, 0, 'z'), (0, 1, 0, 'z'), (1, 1, 0, 'z'),
        ]:
            edges.add((x + dx, y + dy, z + dz, axis))
    for e in edges:
        cand, labels = edge_cands(e)
        S = {l for l, cv in zip(labels, cand) if cv in vs}
        if len(S) >= 2 and frozenset(S) in BAD_Q2:
            return True
    verts = set()
    for v in vs:
        verts |= voxel_corners(v)
    for vtx in verts:
        cand, labels = vertex_cands(vtx)
        S = {l for l, cv in zip(labels, cand) if cv in vs}
        if len(S) >= 2 and frozenset(S) in BAD_Q3:
            return True
    return False


AXES = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}


def apply_step(pt, s):
    sign = -1 if s.startswith('-') else 1
    ax = s[-1]
    d = AXES[ax]
    return tuple(pt[k] + sign * d[k] for k in range(3))


def enumerate_windows(n_steps=3):
    """All monotone 3-step direction sequences from a fresh origin: same-axis
    reuse must keep the same sign (monotone constraint), else free."""
    dirs = ['x', '-x', 'y', '-y', 'z', '-z']
    windows = []
    for seq in itertools.product(dirs, repeat=n_steps):
        axis_sign = {}
        ok = True
        for s in seq:
            sign = -1 if s.startswith('-') else 1
            ax = s[-1]
            if ax in axis_sign and axis_sign[ax] != sign:
                ok = False
                break
            axis_sign[ax] = sign
        if not ok:
            continue
        pts = [(0, 0, 0)]
        for s in seq:
            pts.append(apply_step(pts[-1], s))
        windows.append((seq, tuple(pts)))
    return windows


def canonical_form(seq):
    """Symmetry quotient: axis permutation (3! = 6) x per-axis sign flip
    applied consistently across the whole window (2^3 = 8) => group of size
    48. Returns a canonical representative of the window's orbit."""
    best = None
    axes_list = ['x', 'y', 'z']
    for perm in itertools.permutations(axes_list):
        axis_map = dict(zip(axes_list, perm))
        for signs in itertools.product([1, -1], repeat=3):
            sign_map = dict(zip(axes_list, signs))

            def transform(s):
                sign = -1 if s.startswith('-') else 1
                ax = s[-1]
                new_ax = axis_map[ax]
                new_sign = sign * sign_map[ax]
                return ('-' if new_sign == -1 else '') + new_ax

            cand = tuple(transform(s) for s in seq)
            if best is None or cand < best:
                best = cand
    return best


if __name__ == "__main__":
    windows = enumerate_windows(n_steps=3)
    print(f"Total raw monotone 3-step windows (fresh origin, all direction "
          f"combos with per-axis sign consistency): {len(windows)}")

    failures = []
    for seq, pts in windows:
        if has_fail(set(pts)):
            failures.append((seq, pts))

    print(f"Windows with a Q2/Q3 self-violation: {len(failures)}")

    orbits = {}
    for seq, pts in windows:
        c = canonical_form(seq)
        orbits.setdefault(c, []).append(seq)
    print(f"Distinct windows after axis-permutation + sign-flip symmetry "
          f"quotient: {len(orbits)}")

    # cross-check: also brute-force check every 2-point and 3-point sub-prefix
    # of each window (has_fail already scans all subsets present in vs, but
    # we double check no smaller sub-window alone fails, matching length<=9
    # probe's incremental "first failure" semantics)
    subfailures = []
    for seq, pts in windows:
        for k in range(2, len(pts) + 1):
            if has_fail(set(pts[:k])):
                subfailures.append((seq, pts[:k]))
                break
    print(f"Windows where SOME prefix (length 2..4) fails: {len(subfailures)}")

    if not failures and not subfailures:
        print("\nRESULT: 0/%d exhaustively-enumerated windows fail, and 0 "
              "prefixes of any window fail." % len(windows))
        print("Combined with the index-gap<=3 reduction (proven, not "
              "assumed -- see docstring), this closes S2.0C-06B: "
              "pure monotone bridges can NEVER self-violate Q2/Q3, for ANY "
              "path length.")
    else:
        print("\nRESULT: counterexample(s) found -- S2.0C-06B does NOT "
              "close as conjectured. Inspect `failures`/`subfailures` above.")
