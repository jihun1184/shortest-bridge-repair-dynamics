"""D7D2-A4: induction map candidates, consolidated in one reproducible
verifier (fixes the reported gap: earlier only the blanket-shift version
was saved here even though the component-aware 52/53 result had already
been found in an interactive session and reported in
D7D2-A4_induction_map_step1.md).

Three maps are defined and tested here, in the order they were actually
tried, so the history stays reproducible from this file alone:

  1. blanket_shift    -- shift every point with x <= -4 by +1.
                          REJECTED: 0/53 (moves unrelated core-touching
                          points that must stay fixed).
  2. component_shift   -- shift only the satellite's current component's
                          points with x < -4 by +1.
                          52/53 (fails when that component contains a
                          "thick" patch, e.g. a multi-point Q2/Q3 repair
                          cluster at one x-value, which a blanket
                          within-component shift also drags along).
  3. thin_tail_contract -- find the maximal STRAIGHT single-file run of
                          the satellite's component (constant y,z,
                          consecutive unit x-steps, exactly one point per
                          x-slice) starting from the satellite itself and
                          extending toward the core; contract by removing
                          the innermost unit of that run and shifting only
                          the satellite-side portion (everything with
                          x <= the removed unit's x) by +1. A thick patch
                          anywhere else in the component is never touched,
                          by construction (the run stops there).
"""

from __future__ import annotations

import sys
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
from c07d3e_component_viability import components6  # noqa: E402
from exact_partition_refinement import build_closure, refine  # noqa: E402

CORE_BOUNDARY_X = -4  # the fixed core has x >= -4; never shift/touch x >= this


def blanket_shift(y7, sat7):
    return frozenset(
        (p[0] + 1, p[1], p[2]) if p[0] <= CORE_BOUNDARY_X else p
        for p in y7
    )


def satellite_component(y7, sat7):
    comps = components6(y7)
    return next(c for c in comps if sat7 in c)


def component_shift(y7, sat7):
    sat_comp7 = satellite_component(y7, sat7)
    return frozenset(
        (p[0] + 1, p[1], p[2]) if (p in sat_comp7 and p[0] < CORE_BOUNDARY_X) else p
        for p in y7
    )


def thin_tail_contract(y7, sat7):
    """Find the maximal straight (constant y,z, unit x-steps, one point
    per x-slice) run of the satellite's component starting at the
    satellite and extending toward the core (increasing x). Remove the
    innermost unit of that run (the one closest to the core / thick
    structure) and shift everything with x <= that unit's x by +1.
    If the satellite itself is not part of any such run of length >= 1,
    falls back to shifting just the satellite point itself.
    """
    sat_comp7 = satellite_component(y7, sat7)
    by_x = {}
    for p in sat_comp7:
        by_x.setdefault(p[0], []).append(p)

    sx, sy, sz = sat7
    x = sx
    run = [sat7]
    while True:
        nxt = x + 1
        pts_here = by_x.get(x, [])
        if len(pts_here) != 1 or pts_here[0] != (x, sy, sz):
            break
        pts_next = by_x.get(nxt, [])
        if len(pts_next) != 1 or pts_next[0] != (nxt, sy, sz):
            break
        run.append((nxt, sy, sz))
        x = nxt
        if nxt >= CORE_BOUNDARY_X:
            break

    # innermost unit of the run = the largest x in `run` that is still < CORE_BOUNDARY_X
    candidates = [p for p in run if p[0] < CORE_BOUNDARY_X]
    if not candidates:
        cut_x = sx  # degenerate: just the satellite itself
    else:
        cut_x = max(p[0] for p in candidates)

    return frozenset(
        (p[0] + 1, p[1], p[2]) if p[0] <= cut_x else p
        for p in y7
    )


def keys_by_state(all_states, successors_of, root_components):
    comp_count, max_rho_at, root_part = {}, {}, {}
    for s in all_states:
        comps = components6(s)
        comp_count[s] = len(comps)
        max_rho_at[s] = max((rho for (_, rho) in successors_of[s]), default=0)
        root_part[s] = m.root_identity_partition(s, root_components)
    c = {s: (comp_count[s], max_rho_at[s], root_part[s]) for s in all_states}
    for _ in range(10):
        prev = dict(c)
        c = {
            s: (c[s], frozenset((rho, prev[t]) for (t, rho) in successors_of[s] if t in prev))
            for s in all_states
        }
        if len({c[s] for s in all_states}) == len({prev[s] for s in all_states}):
            break
    return c


def compare_representatives(k_hi, k_lo, time_budget=150):
    all_hi, succ_hi, rc_hi, sat_hi = build_closure(k_hi, time_budget=time_budget)
    all_lo, succ_lo, rc_lo, sat_lo = build_closure(k_lo, time_budget=time_budget)
    key_hi = keys_by_state(all_hi, succ_hi, rc_hi)
    key_lo = keys_by_state(all_lo, succ_lo, rc_lo)
    rep_hi, rep_lo = {}, {}
    for s in all_hi:
        rep_hi.setdefault(key_hi[s], s)
    for s in all_lo:
        rep_lo.setdefault(key_lo[s], s)
    common = set(rep_hi) & set(rep_lo)

    results = {}
    for name, mapper in (
        ("blanket_shift", blanket_shift),
        ("component_shift", component_shift),
        ("thin_tail_contract", thin_tail_contract),
    ):
        exact = 0
        mismatches = []
        for key in common:
            y_lo = rep_lo[key]
            y_hi = rep_hi[key]
            mapped = mapper(y_hi, sat_hi)
            if mapped == y_lo:
                exact += 1
            else:
                mismatches.append(key)
        results[name] = (exact, len(common), mismatches)
    return results


if __name__ == "__main__":
    import time as _time
    cache = {}

    def get_closure(k):
        if k not in cache:
            print(f"building k={k} closure...", flush=True)
            t0 = _time.time()
            cache[k] = build_closure(k, time_budget=200)
            print(f"  done in {_time.time()-t0:.1f}s, {len(cache[k][0])} states", flush=True)
        return cache[k]

    def compare_cached(k_hi, k_lo):
        all_hi, succ_hi, rc_hi, sat_hi = get_closure(k_hi)
        all_lo, succ_lo, rc_lo, sat_lo = get_closure(k_lo)
        key_hi = keys_by_state(all_hi, succ_hi, rc_hi)
        key_lo = keys_by_state(all_lo, succ_lo, rc_lo)
        rep_hi, rep_lo = {}, {}
        for s in all_hi:
            rep_hi.setdefault(key_hi[s], s)
        for s in all_lo:
            rep_lo.setdefault(key_lo[s], s)
        common = set(rep_hi) & set(rep_lo)
        results = {}
        for name, mapper in (
            ("blanket_shift", blanket_shift),
            ("component_shift", component_shift),
            ("thin_tail_contract", thin_tail_contract),
        ):
            exact = 0
            mismatches = []
            for key in common:
                y_lo = rep_lo[key]
                y_hi = rep_hi[key]
                mapped = mapper(y_hi, sat_hi)
                if mapped == y_lo:
                    exact += 1
                else:
                    mismatches.append(key)
            results[name] = (exact, len(common), mismatches)
        return results

    for k_hi, k_lo in [(7, 6), (8, 7)]:
        print(f"=== k={k_hi} -> k={k_lo} ===", flush=True)
        results = compare_cached(k_hi, k_lo)
        for name, (exact, total, mismatches) in results.items():
            print(f"  {name}: {exact}/{total}", flush=True)


def all_state_check(k_hi, k_lo, time_budget=200):
    """Step 3+4 of the agreed roadmap: check thin_tail_contract on EVERY
    state of k_hi's closure (not just representatives), verifying:
      (a) the contracted state is a valid state of k_lo's closure,
      (b) it lands in the SAME exact behavioral class,
      (c) every rho-labeled transition of Y maps to a rho-labeled
          transition of pi(Y) into the class of pi(Y'), for each
          Y --rho--> Y' in k_hi's closure.
    """
    all_hi, succ_hi, rc_hi, sat_hi = build_closure(k_hi, time_budget=time_budget)
    all_lo, succ_lo, rc_lo, sat_lo = build_closure(k_lo, time_budget=time_budget)
    key_hi = keys_by_state(all_hi, succ_hi, rc_hi)
    key_lo = keys_by_state(all_lo, succ_lo, rc_lo)
    lo_state_set = set(all_lo)

    not_in_lo = 0
    class_mismatch = 0
    transition_mismatch = 0
    checked = 0
    for y in all_hi:
        py = thin_tail_contract(y, sat_hi)
        checked += 1
        if py not in lo_state_set:
            not_in_lo += 1
            continue
        if key_hi[y] != key_lo[py]:
            class_mismatch += 1
            continue
        # transition check: for each (y', rho) successor of y, pi(y') should
        # be a successor of py with the same rho (existence check, not
        # full multiset -- consistent with the labeled-set criterion)
        py_succ_labels = {(rho, key_lo[t]) for (t, rho) in succ_lo[py] if t in key_lo}
        for (yprime, rho) in succ_hi[y]:
            if yprime not in key_hi:
                continue
            needed = (rho, key_hi[yprime])
            if needed not in py_succ_labels:
                transition_mismatch += 1
                break
    return dict(
        checked=checked,
        not_in_lo=not_in_lo,
        class_mismatch=class_mismatch,
        transition_mismatch=transition_mismatch,
    )


def diagnose_failures(k_hi, k_lo, time_budget=200):
    """A4.2: per-class breakdown of thin_tail_contract landing failures,
    and a direct check of whether 'lands in k_lo closure' is itself a
    class invariant (same class, some good, some bad states)."""
    all_hi, succ_hi, rc_hi, sat_hi = build_closure(k_hi, time_budget=time_budget)
    all_lo, succ_lo, rc_lo, sat_lo = build_closure(k_lo, time_budget=time_budget)
    key_hi = keys_by_state(all_hi, succ_hi, rc_hi)
    key_lo = keys_by_state(all_lo, succ_lo, rc_lo)
    lo_state_set = set(all_lo)

    by_class_good = {}
    by_class_bad = {}
    for y in all_hi:
        py = thin_tail_contract(y, sat_hi)
        cls = key_hi[y]
        landed = py in lo_state_set
        if landed:
            by_class_good.setdefault(cls, []).append(y)
        else:
            by_class_bad.setdefault(cls, []).append(y)

    all_classes = set(by_class_good) | set(by_class_bad)
    mixed_classes = [c for c in all_classes if c in by_class_good and c in by_class_bad]
    only_bad_classes = [c for c in all_classes if c not in by_class_good]
    only_good_classes = [c for c in all_classes if c not in by_class_bad]

    return dict(
        n_classes_total=len(all_classes),
        n_mixed=len(mixed_classes),
        n_only_bad=len(only_bad_classes),
        n_only_good=len(only_good_classes),
        mixed_classes=mixed_classes,
        by_class_good=by_class_good,
        by_class_bad=by_class_bad,
        sat_hi=sat_hi,
    )


def extract_template_family(y, sat, core_boundary=CORE_BOUNDARY_X):
    """Return an elbow-aware, k-independent satellite template.

    The old A4.3 cut forced the corridor to use the satellite's own
    ``(y, z)`` line.  That convention fails when the component follows a
    fixed path inside the satellite's initial x-slice and then enters a
    long straight line on another ``(y, z)`` line.  Here that whole initial
    slice is treated as the fixed attachment, and the longest admissible
    run toward the core from any of its points is selected.

    The signature deliberately omits corridor length.  It records instead
    (i) the corridor-line offset from the satellite, (ii) the local
    satellite-side attachment, and (iii) the core-side patch anchored at
    the corridor endpoint.  These are the fixed pieces in the intended
    ``A_C union corridor_C(k) union B_C`` decomposition.
    """
    sat_comp = satellite_component(y, sat)
    by_x = {}
    for p in sat_comp:
        by_x.setdefault(p[0], []).append(p)

    sx, sy, sz = sat
    starts = [p for p in sat_comp if p[0] == sx]

    candidates = []
    for start in starts:
        _, line_y, line_z = start
        run = [start]
        x = sx
        while x < core_boundary:
            nxt = x + 1
            expected = (nxt, line_y, line_z)
            pts_next = by_x.get(nxt, [])
            if expected not in pts_next:
                break
            run.append(expected)
            x = nxt
            # A multi-point slice is the core-side endpoint of the thin
            # corridor, not a slice before it.  Include the line point as
            # the endpoint and stop there.
            if len(pts_next) != 1:
                break
        candidates.append((len(run), x, start, tuple(run)))

    # Prefer the longest corridor.  The remaining fields make ties stable
    # and independent of set/dictionary iteration order.
    _, end_x, start, corridor = max(
        candidates,
        key=lambda item: (item[0], item[1], tuple(-v for v in item[2])),
    )
    return _template_signature_for_cut(sat_comp, sat, start, end_x, corridor)


def _template_signature_for_cut(sat_comp, sat, start, end_x, corridor):
    """Encode one admissible cut; corridor length is intentionally absent."""
    sx, sy, sz = sat
    _, line_y, line_z = start
    corridor_set = frozenset(corridor)

    # When the corridor starts on another line, the initial slice is the
    # fixed satellite-side elbow.  When it starts at the satellite itself,
    # other points in that slice belong to the core-side patch.  Keeping
    # both admissible cuts (see extract_template_families) handles the
    # zero-length boundary degeneration without privileging a convention.
    if start == sat:
        attachment_pts = frozenset((sat,))
    else:
        attachment_pts = frozenset(p for p in sat_comp if p[0] <= sx)
    attachment_shape = frozenset(
        (p[0] - sx, p[1] - sy, p[2] - sz) for p in attachment_pts
    )

    patch_pts = frozenset(
        p for p in sat_comp if p not in corridor_set and p not in attachment_pts
    )
    patch_shape = frozenset(
        (p[0] - end_x, p[1] - line_y, p[2] - line_z) for p in patch_pts
    )

    line_offset = (start[0] - sx, line_y - sy, line_z - sz)
    return (line_offset, attachment_shape, patch_shape)


def extract_template_families(y, sat, core_boundary=CORE_BOUNDARY_X):
    """Return the cut-equivalence class of all admissible A4.3 templates.

    A representative can have more than one legitimate straight-corridor
    cut, especially when a corridor has length zero at k=6 and its elbow
    shares the satellite's x-slice.  Equality of one arbitrarily selected
    cut is therefore too strong.  The intrinsic comparison is whether the
    admissible-signature sets for corresponding representatives intersect.
    """
    return frozenset(extract_template_witnesses(y, sat, core_boundary))


def extract_template_witnesses(y, sat, core_boundary=CORE_BOUNDARY_X):
    """Map every admissible signature to its closed-corridor witnesses.

    Each witness records the actual start, endpoint, and nonnegative
    corridor length.  These data let an audit reconstruct the complete
    satellite component by ordinary set union and explicitly include the
    zero-length boundary case.
    """
    sat_comp = satellite_component(y, sat)
    by_x = {}
    for p in sat_comp:
        by_x.setdefault(p[0], []).append(p)

    sx = sat[0]
    witnesses = {}
    for start in (p for p in sat_comp if p[0] == sx):
        _, line_y, line_z = start
        run = [start]
        x = sx
        while x < core_boundary:
            nxt = x + 1
            expected = (nxt, line_y, line_z)
            pts_next = by_x.get(nxt, [])
            if expected not in pts_next:
                break
            run.append(expected)
            x = nxt
            if len(pts_next) != 1:
                break
        signature = _template_signature_for_cut(
            sat_comp, sat, start, x, tuple(run)
        )
        witnesses.setdefault(signature, []).append(
            {
                "start": start,
                "endpoint": (x, line_y, line_z),
                "corridor_length": x - sx,
                "corridor": tuple(run),
            }
        )
    return witnesses
