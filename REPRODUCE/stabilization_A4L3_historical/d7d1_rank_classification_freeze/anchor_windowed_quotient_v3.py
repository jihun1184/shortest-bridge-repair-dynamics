"""D7D2-A3.1 v3: labeled-successor-SET consistency (not multiset).

Same signature q_R as v2 (x-cutoff windows, corrected interior condition).
Only the consistency criterion changes: instead of comparing the sorted
MULTISET of successor signatures (which penalizes two states for merely
having a different NUMBER of actions leading to the same abstract class),
compare the SET of (rho(action), successor_signature) pairs -- what matters
for reachability/R* is which (rho, next-class) pairs are reachable at all,
not how many syntactically-distinct bridge actions realize each one.
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

from anchor_windowed_quotient_v2 import CORE, CORE_ANCHOR, signature  # noqa: E402


def build_and_check(k, y=2, repair=(-1, -1, 0), margins=(0, 1), time_budget=200):
    sat = (-k, y, 0)
    state0 = CORE | {sat}
    root = state0 | {repair}
    if has_fail(root):
        raise AssertionError("invalid root")
    root_components = components6(root)
    if len(root_components) != 5:
        raise AssertionError("expected 5 components")

    queue = deque([root])
    seen = {root}
    all_states = []
    # store (successor, rho) pairs per state
    successors_of = {}
    t0 = time.time()
    while queue:
        if time.time() - t0 > time_budget:
            break
        state = queue.popleft()
        all_states.append(state)
        before_partition = m.root_identity_partition(state, root_components)
        succs = []
        for action in atomic_actions(state):
            if set(action["roles"]) != {"N2"}:
                continue
            additions = frozenset(tuple(p) for p in action["additions"])
            successor = state | additions
            after_partition = m.root_identity_partition(successor, root_components)
            block = m.absorption_block(before_partition, after_partition)
            rho = len(block)
            succs.append((successor, rho))
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

        inconsistent_multiset = 0
        inconsistent_labeled_set = 0
        checked_groups = 0
        for sig, states_in_group in groups.items():
            if len(states_in_group) < 2:
                continue
            checked_groups += 1
            multisets = []
            labeled_sets = []
            for s in states_in_group:
                pairs = [(rho, sig_of[t]) for (t, rho) in successors_of[s] if t in sig_of]
                multisets.append(tuple(sorted(pairs, key=repr)))
                labeled_sets.append(frozenset(pairs))
            if len(set(multisets)) > 1:
                inconsistent_multiset += 1
            if len(set(labeled_sets)) > 1:
                inconsistent_labeled_set += 1

        results[margin] = dict(
            states=len(all_states),
            distinct_signatures=distinct,
            compression=1 - distinct / len(all_states),
            groups_with_multiple_states=checked_groups,
            inconsistent_multiset=inconsistent_multiset,
            inconsistent_labeled_set=inconsistent_labeled_set,
        )
    return results, len(all_states), time.time() - t0


if __name__ == "__main__":
    for k in [int(a) for a in sys.argv[1:]] or [7]:
        results, n_states, elapsed = build_and_check(k)
        print(f"=== k={k} ({n_states} states, {elapsed:.1f}s) ===")
        for margin, r in results.items():
            print(
                f"  margin={margin}: distinct={r['distinct_signatures']}/{r['states']} "
                f"compression={r['compression']*100:.1f}% "
                f"multi-groups={r['groups_with_multiple_states']} "
                f"inconsistent(multiset)={r['inconsistent_multiset']} "
                f"inconsistent(labeled-set)={r['inconsistent_labeled_set']}"
            )
