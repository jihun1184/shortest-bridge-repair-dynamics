"""D7D2-A2: closure-level cross-check of contact_automaton against full
brute-force certificate_bridge_actions enumeration, at EVERY state of a
real N2-reachable closure (not just the root layer).

Usage (from the checkpoint root):
    python3 d7d1_rank_classification_freeze/closure_level_crosscheck.py

Known results reproduced in this session (see D7D2-A2_closure_crosscheck.md):
    orbit_15 repair_0: 6,289 states, 3,394 certs, 0 mismatches, max_rho=3
    orbit_15 repair_1: 4,914 states, 2,986 certs, 0 mismatches, max_rho=3
    orbit_33 repair_0: 1,099 states,   820 certs, 0 mismatches, max_rho=4
"""

import sys, time, json
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKPOINT_ROOT = str(HERE.parent)
sys.path.insert(0, str(HERE))
sys.path.insert(0, CHECKPOINT_ROOT + "/work/d7d1")
sys.path.insert(0, CHECKPOINT_ROOT + "/work/d7c_pkg/c07d7c_package/work/c07d4")
sys.path.insert(0, CHECKPOINT_ROOT + "/work/d7c_pkg/c07d7c_package/work/c07d3e")
sys.path.insert(0, CHECKPOINT_ROOT + "/work/d7c_pkg/c07d7c_package/work/c07d3b/c07a_scripts")

import c07d7d1_persistent_absorption_closure as m
from finite_window_classification import has_fail
from c07d3e_component_viability import components6, component_certificates
from c07d4_planning_census import certificate_bridge_actions
from c07d5_atomic_planning_census import atomic_actions
from contact_automaton import certificate_max_rho_at_least_4

core = frozenset({(-4,1,0),(-3,-1,-1),(-1,-1,-1),(-1,0,-1),(-1,0,0),(0,-1,-1),(0,-1,0),(0,2,-1)})

def flag_to_expected_rho_bucket(flag):
    # returns set of acceptable brute-max-rho values consistent with flag
    if flag is None:
        return {0}  # no compatible path at all -> brute finds zero actions -> brute_max stays 0
    if flag == 'NONE':
        return {2}
    if flag == 'ONE':
        return {3}
    if flag == 'SAT':
        return {4,5}
    return set()

def check_state(state, root_components):
    comps = components6(state)
    before_partition = m.root_identity_partition(state, root_components)
    mismatches = []
    max_rho_here = 0
    n_certs = 0
    for cert in component_certificates(state):
        left, right = cert
        actions, stats = certificate_bridge_actions(state, cert)
        brute_max = 0
        for action in actions:
            additions = frozenset(tuple(p) for p in action['additions'])
            successor = state | additions
            after_partition = m.root_identity_partition(successor, root_components)
            block = m.absorption_block(before_partition, after_partition)
            brute_max = max(brute_max, len(block))
        exists, flag = certificate_max_rho_at_least_4(state, comps, left, right)
        expected = flag_to_expected_rho_bucket(flag)
        n_certs += 1
        max_rho_here = max(max_rho_here, brute_max)
        if brute_max not in expected:
            mismatches.append((cert, brute_max, flag))
    return max_rho_here, n_certs, mismatches

def closure_crosscheck(orbit_index, repair_index, initial_state, repair, limit_states=None):
    initial_state = frozenset(tuple(point) for point in initial_state)
    repair = tuple(repair)
    root = initial_state | {repair}
    assert not has_fail(root)
    root_components = components6(root)
    assert len(root_components) == 5

    queue = deque([root])
    seen = {root}
    total_mismatches = []
    total_certs = 0
    max_rho_overall = 0
    t0 = time.time()
    n_states = 0
    while queue:
        state = queue.popleft()
        n_states += 1
        max_rho_here, n_certs, mismatches = check_state(state, root_components)
        total_certs += n_certs
        max_rho_overall = max(max_rho_overall, max_rho_here)
        total_mismatches.extend(mismatches)
        if mismatches:
            print('MISMATCH at state, count=', len(mismatches))
        actions = atomic_actions(state)
        for action in actions:
            if set(action['roles']) != {'N2'}:
                continue
            additions = frozenset(tuple(p) for p in action['additions'])
            successor = state | additions
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
        if limit_states and n_states >= limit_states:
            break
    elapsed = time.time() - t0
    print(f'orbit_{orbit_index}:repair_{repair_index} states_checked={n_states} certs_checked={total_certs} '
          f'max_rho_overall={max_rho_overall} mismatches={len(total_mismatches)} elapsed={elapsed:.1f}s')
    return total_mismatches

if __name__ == '__main__':
    import sys as _s
    limit = int(_s.argv[1]) if len(_s.argv) > 1 else None
    sat = (-4,3,0)
    state0 = core | {sat}
    for repair in [(-1,-1,0),(0,0,0)]:
        closure_crosscheck(15, 0 if repair==(-1,-1,0) else 1, state0, repair, limit_states=limit)
