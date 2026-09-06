import itertools, json
from pcm_check import build_complex, border_of
from stage2_repair_core import candidate_voxels, failure_type_at, RANK, pwc_verdict

def defect_set(Y):
    Y = frozenset(Y)
    if not Y: return {}
    _, cells = build_complex(Y)
    d = border_of(cells, RANK)
    return {g: failure_type_at(g, d) for g in d if failure_type_at(g, d) is not None}

def universe_for(Y):
    d = defect_set(Y)
    u = set()
    for h in d: u |= candidate_voxels(h)
    return sorted(u), d

def brute_min_repair(Y, universe, max_size):
    Y = frozenset(Y)
    for size in range(0, max_size + 1):
        winners = []
        for combo in itertools.combinations(universe, size):
            Z = Y.symmetric_difference(combo)
            if pwc_verdict(Z):
                winners.append(frozenset(combo))
        if winners:
            return size, winners
    return None, []

def analyze_case(F0, R):
    F0 = frozenset(F0); R = frozenset(R)
    d0 = defect_set(F0)
    results = {}
    for w in R:
        others = R - {w}
        Y_w = F0.symmetric_difference(others)
        G_w = defect_set(Y_w)
        W = {h for h in d0 if h in G_w and w in candidate_voxels(h)}
        W_safe = {h for h in W if not any(u in candidate_voxels(h) for u in others)}
        results[w] = dict(W=sorted(W), W_safe=sorted(W_safe),
                           W_size=len(W), W_safe_size=len(W_safe),
                           FAILURE=(len(W) > 0 and len(W_safe) == 0))
    return results

if __name__ == "__main__":
    # Fixture: the SEED block used throughout the manuscript's chain family
    F0_fixture = frozenset([(-1,-1,-1),(-1,-1,0),(0,0,-1),(0,0,0)])
    universe, d0 = universe_for(F0_fixture)
    m0, M0 = brute_min_repair(F0_fixture, universe, max_size=3)
    print(f"FIXTURE: m0={m0}, |M0|={len(M0)}")
    any_failure = False
    for R in M0:
        res = analyze_case(F0_fixture, R)
        for w, r in res.items():
            print(f"  R={sorted(R)} w={w}: |W|={r['W_size']} |W_safe|={r['W_safe_size']} FAILURE={r['FAILURE']}")
            if r['FAILURE']:
                any_failure = True
    print(f"FIXTURE regression: any safe-witness failure? {any_failure}")
