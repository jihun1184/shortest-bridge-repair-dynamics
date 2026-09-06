"""D7D2-A3.1: anchor-windowed behavioral quotient discovery.

Signature q_R(Y) = (root_identity_partition,
                     W_core^R(Y)  -- raw points within L1<=R of the fixed
                                     core anchor (-4,1,0), untranslated,
                     W_sat^R(Y)   -- points within L1<=R of the satellite
                                     anchor (-k,y,0), translated by (+k,0,0)
                                     so it is comparable across k,
                     corridor_mode -- classification of the y-value pattern
                                      of points strictly outside BOTH
                                      windows (the abstracted "bend
                                      location" signal, exact position
                                      discarded),
                     connected_flag -- whether the core anchor's current
                                       component already equals the
                                       satellite anchor's current
                                       component)

This deliberately does NOT collapse the whole component to one
fingerprint (that was tried in quotient_discovery.py and rejected: 0%
compression, because bend position leaked into the global fingerprint).
Here the corridor's exact bend position is discarded and only its
*phase* (inside core window / inside sat window / interior-only-y1 /
interior-only-y2 / interior-mixed) is kept.
"""

from __future__ import annotations

import sys
import time
from collections import deque, Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKPOINT_ROOT = HERE.parent
WORK = CHECKPOINT_ROOT / "work" / "d7c_pkg" / "c07d7c_package" / "work"

for dependency in (
    CHECKPOINT_ROOT / "work" / "d7d1",
    WORK / "c07d3e",
    WORK / "c07d5",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

import c07d7d1_persistent_absorption_closure as m  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402
from c07d3e_component_viability import components6  # noqa: E402
from c07d5_atomic_planning_census import atomic_actions  # noqa: E402

CORE = frozenset(
    {
        (-4, 1, 0), (-3, -1, -1), (-1, -1, -1), (-1, 0, -1),
        (-1, 0, 0), (0, -1, -1), (0, -1, 0), (0, 2, -1),
    }
)
CORE_ANCHOR = (-4, 1, 0)


def l1(p, q):
    return sum(abs(a - b) for a, b in zip(p, q))


def corridor_mode(interior_points):
    if not interior_points:
        return "NO_INTERIOR"
    ys = {p[1] for p in interior_points}
    if ys == {1}:
        return "INTERIOR_Y1_ONLY"
    if ys == {2}:
        return "INTERIOR_Y2_ONLY"
    return "INTERIOR_MIXED"


def signature(state, root_components, sat_anchor, R):
    comps = components6(state)
    partition = m.root_identity_partition(state, root_components)

    core_idx = next(i for i, c in enumerate(root_components) if CORE_ANCHOR in c)
    sat_idx = next(i for i, c in enumerate(root_components) if sat_anchor in c)
    core_block = next(b for b in partition if core_idx in b)
    sat_block = next(b for b in partition if sat_idx in b)
    connected = core_block == sat_block

    k = -sat_anchor[0]
    w_core = frozenset(p for p in state if l1(p, CORE_ANCHOR) <= R)
    w_sat_raw = frozenset(p for p in state if l1(p, sat_anchor) <= R)
    w_sat = frozenset((p[0] + k, p[1], p[2]) for p in w_sat_raw)

    interior = frozenset(
        p for p in state
        if l1(p, CORE_ANCHOR) > R and l1(p, sat_anchor) > R
    )
    mode = corridor_mode(interior)

    return (partition, w_core, w_sat, mode, connected)


def build_and_check(k, y=2, repair=(-1, -1, 0), radii=(2, 3, 4), time_budget=200):
    sat = (-k, y, 0)
    state0 = CORE | {sat}
    root = state0 | {repair}
    if has_fail(root):
        raise AssertionError("invalid root")
    root_components = components6(root)
    if len(root_components) != 5:
        raise AssertionError(f"expected 5 components, got {len(root_components)}")

    queue = deque([root])
    seen = {root}
    all_states = []
    successors_of = {}
    t0 = time.time()
    while queue:
        if time.time() - t0 > time_budget:
            break
        state = queue.popleft()
        all_states.append(state)
        succs = []
        for action in atomic_actions(state):
            if set(action["roles"]) != {"N2"}:
                continue
            additions = frozenset(tuple(p) for p in action["additions"])
            successor = state | additions
            succs.append(successor)
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
        successors_of[state] = succs

    results = {}
    for R in radii:
        sig_of = {s: signature(s, root_components, sat, R) for s in all_states}
        distinct = len(set(sig_of.values()))
        # successor-signature-multiset consistency check, grouped by signature
        groups = defaultdict(list)
        for s in all_states:
            groups[sig_of[s]].append(s)
        inconsistent = 0
        checked_groups = 0
        for sig, states_in_group in groups.items():
            if len(states_in_group) < 2:
                continue
            checked_groups += 1
            multisets = []
            for s in states_in_group:
                succ_sigs = tuple(sorted(
                    (sig_of[t] for t in successors_of[s] if t in sig_of),
                    key=repr,
                ))
                multisets.append(succ_sigs)
            if len(set(multisets)) > 1:
                inconsistent += 1
        results[R] = dict(
            states=len(all_states),
            distinct_signatures=distinct,
            compression=1 - distinct / len(all_states),
            groups_with_multiple_states=checked_groups,
            inconsistent_groups=inconsistent,
        )
    return results, len(all_states), time.time() - t0


if __name__ == "__main__":
    for k in [int(a) for a in sys.argv[1:]] or [6]:
        results, n_states, elapsed = build_and_check(k)
        print(f"=== k={k} ({n_states} states, {elapsed:.1f}s) ===")
        for R, r in results.items():
            print(
                f"  R={R}: distinct={r['distinct_signatures']}/{r['states']} "
                f"compression={r['compression']*100:.1f}% "
                f"multi-state-groups={r['groups_with_multiple_states']} "
                f"inconsistent={r['inconsistent_groups']}"
            )
