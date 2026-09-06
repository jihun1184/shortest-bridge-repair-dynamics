"""D7D2-A3.2: exact behavioral partition refinement (bisimulation) on a
real finite closure.

c_0(Y) = (component_count, max_rho_at_Y, root_identity_partition)
c_{n+1}(Y) = (c_n(Y), frozenset{(rho(a), c_n(Y')) : Y --a--> Y'})

Since every N2 action strictly decreases component count (D7D0), this
closure's transition graph is a DAG with depth <=4, so refinement is
guaranteed to stabilize in a few rounds (process states in order of
decreasing component count / topological order for one-pass exactness per
round, or just iterate to a fixed point -- both are done here for
robustness).

Output: the number of classes each round, and, once stable, a cross-tab
against the v2 anchor-windowed signature to see whether the exact
behavioral classes refine (subdivide) the geometric signature or align
with it -- this tells us exactly what extra state the geometric signature
is missing.
"""

from __future__ import annotations

import sys
import time
from collections import deque, defaultdict, Counter
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

from anchor_windowed_quotient_v2 import CORE, signature as anchor_signature  # noqa: E402


def build_closure(k, y=2, repair=(-1, -1, 0), time_budget=200):
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
    return all_states, successors_of, root_components, sat


def refine(all_states, successors_of, root_components, max_rounds=10):
    comp_count = {}
    max_rho_at = {}
    root_part = {}
    for s in all_states:
        comps = components6(s)
        comp_count[s] = len(comps)
        max_rho_at[s] = max((rho for (_, rho) in successors_of[s]), default=0)
        root_part[s] = m.root_identity_partition(s, root_components)

    c = {s: (comp_count[s], max_rho_at[s], root_part[s]) for s in all_states}
    history = []
    for round_idx in range(max_rounds):
        classes = {}
        for s in all_states:
            key = c[s]
            classes.setdefault(key, len(classes))
        n_classes = len(classes)
        history.append(n_classes)
        c_next = {}
        for s in all_states:
            label = frozenset((rho, c[t]) for (t, rho) in successors_of[s] if t in c)
            c_next[s] = (c[s], label)
        new_classes = {}
        for s in all_states:
            new_classes.setdefault(c_next[s], len(new_classes))
        if len(new_classes) == n_classes:
            c = c_next
            history.append(len(new_classes))
            break
        c = c_next
    final_classes = {}
    class_id_of = {}
    for s in all_states:
        key = c[s]
        if key not in final_classes:
            final_classes[key] = len(final_classes)
        class_id_of[s] = final_classes[key]
    return class_id_of, history, set(final_classes.keys())


if __name__ == "__main__":
    for k in [int(a) for a in sys.argv[1:]] or [6]:
        all_states, successors_of, root_components, sat = build_closure(k)
        t0 = time.time()
        class_id_of, history = refine(all_states, successors_of, root_components)
        n_final = len(set(class_id_of.values()))
        print(f"k={k}: states={len(all_states)} rounds_history={history} "
              f"final_exact_classes={n_final} elapsed={time.time()-t0:.1f}s")

        # cross-tab against anchor signature (margin=1)
        anchor_sig_of = {s: anchor_signature(s, root_components, sat, 1) for s in all_states}
        crosstab = defaultdict(set)
        for s in all_states:
            crosstab[anchor_sig_of[s]].add(class_id_of[s])
        splits = {sig: classes for sig, classes in crosstab.items() if len(classes) > 1}
        print(f"  anchor-signature groups that split into >1 exact class: {len(splits)} "
              f"(out of {len(crosstab)} anchor-signature groups)")
