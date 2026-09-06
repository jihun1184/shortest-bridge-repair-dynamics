"""D7D2-A3: quotient/signature discovery over small-k closures.

For each state Y in a ray closure, compute a translation-abstracted
signature that:
  - keeps root-identity partition exactly (which of the 5 original
    components have merged into which current component) -- this is
    k-independent bookkeeping already used throughout D7D1/D7D2,
  - replaces each current component's exact voxel set with a coarse
    shape class: POINT (singleton), LINE_X (a contiguous run of points
    varying only in x -- the expected corridor shape), or an exact
    translation-normalized fingerprint for anything else (expected only
    near the fixed core / satellite, never in the empty corridor).

If the number of DISTINCT signatures stops growing while k grows (and the
raw state count keeps growing), that is direct evidence that most of the
raw-state blowup is just corridor-length bookkeeping, not new qualitative
structure -- i.e. evidence for a finite quotient.

This is exploratory (discovery), not a proof. Correctness of state
generation itself still rests on the already-validated atomic_actions /
has_fail / components6 pipeline (D7D0-D7D2-A2), not on anything new here.
"""

from __future__ import annotations

import sys
import time
from collections import deque, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKPOINT_ROOT = HERE.parent
WORK = CHECKPOINT_ROOT / "work" / "d7c_pkg" / "c07d7c_package" / "work"

for dependency in (
    CHECKPOINT_ROOT / "work" / "d7d1",
    WORK / "c07d3e",
    WORK / "c07d5",
    WORK / "c07d4",
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


def shape_class(component):
    pts = sorted(component)
    if len(pts) == 1:
        return ("POINT",)
    ys = {p[1] for p in pts}
    zs = {p[2] for p in pts}
    xs = sorted(p[0] for p in pts)
    if len(ys) == 1 and len(zs) == 1 and xs == list(range(xs[0], xs[-1] + 1)):
        return ("LINE_X", len(xs))  # length kept SEPARATE, not part of the
        # abstracted signature below -- recorded here for inspection only
    minx = min(p[0] for p in pts)
    miny = min(p[1] for p in pts)
    minz = min(p[2] for p in pts)
    fingerprint = tuple(sorted((p[0] - minx, p[1] - miny, p[2] - minz) for p in pts))
    return ("SHAPE", fingerprint)


def state_signature(state, root_components):
    """k-independent signature: root-identity partition + per-current-
    component shape class, WITHOUT the LINE_X length (corridor length is
    deliberately dropped from the signature -- that's the whole point).
    """
    comps = components6(state)
    partition = m.root_identity_partition(state, root_components)
    entries = []
    for block, comp in zip(partition, comps):
        sc = shape_class(comp)
        if sc[0] == "LINE_X":
            sc = ("LINE_X",)  # drop the length for the abstracted signature
        entries.append((block, sc))
    return (partition, tuple(sorted(entries)))


def build_closure_with_signatures(k, y=2, repair=(-1, -1, 0), time_budget=250):
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
    sig_counter = Counter()
    t0 = time.time()
    n_states = 0
    while queue:
        if time.time() - t0 > time_budget:
            return {
                "k": k, "complete": False, "states_visited": n_states,
                "distinct_signatures": len(sig_counter),
                "top_signatures": sig_counter.most_common(5),
                "elapsed": time.time() - t0,
            }
        state = queue.popleft()
        n_states += 1
        sig = state_signature(state, root_components)
        sig_counter[sig] += 1
        for action in atomic_actions(state):
            if set(action["roles"]) != {"N2"}:
                continue
            additions = frozenset(tuple(p) for p in action["additions"])
            successor = state | additions
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
    return {
        "k": k, "complete": True, "states_visited": n_states,
        "distinct_signatures": len(sig_counter),
        "top_signatures": sig_counter.most_common(5),
        "elapsed": time.time() - t0,
    }


if __name__ == "__main__":
    ks = [int(a) for a in sys.argv[1:]] or [6, 7]
    for k in ks:
        result = build_closure_with_signatures(k)
        print(
            f"k={result['k']} complete={result['complete']} "
            f"states={result['states_visited']} "
            f"distinct_signatures={result['distinct_signatures']} "
            f"elapsed={result['elapsed']:.1f}s",
            flush=True,
        )
