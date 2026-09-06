"""D7D2-A3.1 v2: fixes the R=2/3/4 single-anchor window's diagnosed flaw.

Diagnosis from v1 (anchor_windowed_quotient.py): windowing by Chebyshev/L1
radius from a SINGLE point (-4,1,0) cut through the middle of the fixed
8-point core itself (whose sub-components span more than radius 3-4 from
that one corner), so core-region content leaked into "interior" and was
wrongly discarded -- producing real but INCONSISTENT compression (up to
~30% of multi-state groups had mismatched successor-signature multisets).

Fix: since core and satellite are separated primarily along x, window by a
fixed x-cutoff instead of a radius from one point:
  W_core  = all points with x >= CORE_X_CUTOFF   (the entire fixed core,
            however many sub-components it has -- untranslated)
  W_sat   = all points with x <= -k + SAT_MARGIN  (near satellite,
            translated by +k so it's k-independent)
  interior = strictly between the two cutoffs (the true empty corridor)
This only discards x-position *within* the interior band, not core
sub-structure.
"""

from __future__ import annotations

import sys
import time
from collections import deque, defaultdict
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
CORE_X_CUTOFF = -4  # entire fixed core has x >= -4
CORE_ANCHOR = (-4, 1, 0)


def corridor_mode(interior_points):
    if not interior_points:
        return "NO_INTERIOR"
    ys = {p[1] for p in interior_points}
    if ys == {1}:
        return "INTERIOR_Y1_ONLY"
    if ys == {2}:
        return "INTERIOR_Y2_ONLY"
    return "INTERIOR_MIXED"


def signature(state, root_components, sat_anchor, margin):
    partition = m.root_identity_partition(state, root_components)
    core_idx = next(i for i, c in enumerate(root_components) if CORE_ANCHOR in c)
    sat_idx = next(i for i, c in enumerate(root_components) if sat_anchor in c)
    core_block = next(b for b in partition if core_idx in b)
    sat_block = next(b for b in partition if sat_idx in b)
    connected = core_block == sat_block

    k = -sat_anchor[0]
    sat_x_cutoff = -k + margin

    w_core = frozenset(p for p in state if p[0] >= CORE_X_CUTOFF)
    w_sat_raw = frozenset(p for p in state if p[0] <= sat_x_cutoff)
    w_sat = frozenset((p[0] + k, p[1], p[2]) for p in w_sat_raw)

    interior = frozenset(
        p for p in state
        if sat_x_cutoff < p[0] < CORE_X_CUTOFF
    )
    mode = corridor_mode(interior)
    return (partition, w_core, w_sat, mode, connected)


def build_and_check(k, y=2, repair=(-1, -1, 0), margins=(2, 3, 4), time_budget=200):
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
    for margin in margins:
        sig_of = {s: signature(s, root_components, sat, margin) for s in all_states}
        distinct = len(set(sig_of.values()))
        groups = defaultdict(list)
        for s in all_states:
            groups[sig_of[s]].append(s)
        inconsistent = 0
        checked_groups = 0
        first_inconsistent_example = None
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
                if first_inconsistent_example is None:
                    first_inconsistent_example = (sig, states_in_group[:2])
        results[margin] = dict(
            states=len(all_states),
            distinct_signatures=distinct,
            compression=1 - distinct / len(all_states),
            groups_with_multiple_states=checked_groups,
            inconsistent_groups=inconsistent,
            first_inconsistent_example=first_inconsistent_example,
        )
    return results, len(all_states), time.time() - t0


if __name__ == "__main__":
    for k in [int(a) for a in sys.argv[1:]] or [6]:
        results, n_states, elapsed = build_and_check(k)
        print(f"=== k={k} ({n_states} states, {elapsed:.1f}s) ===")
        for margin, r in results.items():
            print(
                f"  margin={margin}: distinct={r['distinct_signatures']}/{r['states']} "
                f"compression={r['compression']*100:.1f}% "
                f"multi-state-groups={r['groups_with_multiple_states']} "
                f"inconsistent={r['inconsistent_groups']}"
            )
