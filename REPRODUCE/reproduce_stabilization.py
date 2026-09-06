#!/usr/bin/env python3
"""Deterministically regenerate the reachable N2 closure and exact behavioral quotient.

This publication-facing launcher uses the recovered historical implementation for
all scientific primitives, but replaces its unsafe wall-clock truncation behavior:
a time limit is a *failure condition*, never a request to return a partial closure.

Examples
--------
    python REPRODUCE/reproduce_stabilization.py --k 6 --output build/stabilization
    python REPRODUCE/reproduce_stabilization.py --k 6 7 8 --max-seconds 0

``--max-seconds 0`` means no internal wall-clock limit.  If a positive limit is
reached, the program exits nonzero and does not run quotient refinement.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = (
    ROOT
    / "REPRODUCE"
    / "stabilization_A4L3_historical"
    / "d7d1_rank_classification_freeze"
    / "exact_partition_refinement.py"
)

EXPECTED_STATES = {6: 9524, 7: 21963, 8: 45939, 9: 87517}
EXPECTED_HISTORY = {6: [35, 51, 53, 53], 7: [35, 51, 53, 53], 8: [35, 51, 53, 53]}
EXPECTED_CLASSES = {6: 53, 7: 53, 8: 53, 9: 53}
EXPECTED_EDGES = {9: 148722}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_historical_module():
    sys.path.insert(0, str(HISTORICAL.parent))
    spec = importlib.util.spec_from_file_location("cgta_exact_partition_refinement", HISTORICAL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import recovered historical module: {HISTORICAL}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_complete_closure(mod, k: int, max_seconds: float):
    """Historical closure semantics with a fail-closed completeness gate."""
    sat = (-k, 2, 0)
    state0 = mod.CORE | {sat}
    root = state0 | {(-1, -1, 0)}
    if mod.has_fail(root):
        raise AssertionError("invalid root")
    root_components = mod.components6(root)
    if len(root_components) != 5:
        raise AssertionError("expected 5 root components")

    queue = deque([root])
    seen = {root}
    all_states = []
    successors_of = {}
    t0 = time.monotonic()

    while queue:
        if max_seconds > 0 and time.monotonic() - t0 > max_seconds:
            raise TimeoutError(
                "completeness gate: time limit reached before BFS queue emptied "
                f"(k={k}, processed={len(all_states)}, seen={len(seen)}, queued={len(queue)}). "
                "No partial closure was accepted."
            )
        state = queue.popleft()
        all_states.append(state)
        before_partition = mod.m.root_identity_partition(state, root_components)
        succs = []
        for action in mod.atomic_actions(state):
            if set(action["roles"]) != {"N2"}:
                continue
            additions = frozenset(tuple(p) for p in action["additions"])
            successor = state | additions
            after_partition = mod.m.root_identity_partition(successor, root_components)
            rho = len(mod.m.absorption_block(before_partition, after_partition))
            succs.append((successor, rho))
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
        successors_of[state] = succs

    if len(all_states) != len(seen) or queue:
        raise AssertionError("BFS completeness invariant failed")
    return all_states, successors_of, root_components


def check_expected(k: int, summary: dict) -> dict:
    checks = {}
    if k in EXPECTED_STATES:
        checks["state_count"] = summary["states"] == EXPECTED_STATES[k]
    if k in EXPECTED_CLASSES:
        checks["class_count"] = summary["final_exact_classes"] == EXPECTED_CLASSES[k]
    if k in EXPECTED_HISTORY:
        checks["refinement_history"] = summary["rounds_history"] == EXPECTED_HISTORY[k]
    if k in EXPECTED_EDGES:
        checks["edge_count"] = summary["n2_edges"] == EXPECTED_EDGES[k]
    checks["all"] = all(checks.values())
    return checks


def run_one(mod, k: int, max_seconds: float) -> dict:
    t0 = time.monotonic()
    states, successors, root_components = build_complete_closure(mod, k, max_seconds)
    closure_seconds = time.monotonic() - t0

    t1 = time.monotonic()
    class_id_of, history, stable_keys = mod.refine(states, successors, root_components)
    refinement_seconds = time.monotonic() - t1

    summary = {
        "k": k,
        "states": len(states),
        "n2_edges": sum(len(v) for v in successors.values()),
        "rounds_history": history,
        "final_exact_classes": len(stable_keys),
        "closure_complete": True,
        "closure_seconds": closure_seconds,
        "refinement_seconds": refinement_seconds,
        "total_seconds": time.monotonic() - t0,
    }
    summary["reference_checks"] = check_expected(k, summary)
    if not summary["reference_checks"]["all"]:
        raise AssertionError(f"frozen-reference mismatch for k={k}: {summary['reference_checks']}")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", nargs="+", type=int, required=True, help="ray-family parameter(s)")
    ap.add_argument(
        "--max-seconds",
        type=float,
        default=0.0,
        help="fail if a closure is not complete within this many seconds; 0 disables the limit",
    )
    ap.add_argument("--output", type=Path, default=Path("build/stabilization"))
    args = ap.parse_args()

    mod = load_historical_module()
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for k in args.k:
        print(f"[stabilization] k={k}: complete BFS + exact refinement", flush=True)
        result = run_one(mod, k, args.max_seconds)
        results.append(result)
        print(
            f"  states={result['states']} edges={result['n2_edges']} "
            f"history={result['rounds_history']} classes={result['final_exact_classes']}",
            flush=True,
        )

    payload = {
        "pipeline": "publication-safe complete N2 closure + exact behavioral refinement",
        "historical_source": str(HISTORICAL.relative_to(ROOT)),
        "historical_source_sha256": sha256(HISTORICAL),
        "python": platform.python_version(),
        "results": results,
    }
    out = args.output / "stabilization_reproduction.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
