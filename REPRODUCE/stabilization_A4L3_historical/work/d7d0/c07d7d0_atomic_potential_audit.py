"""C07-D7D0: frozen atomic-potential implementation regression.

This is deliberately an implementation audit, not the symbolic proof.
It stops at the first violation and writes a machine-readable counterexample.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / "d7c_pkg" / "c07d7c_package"
WORK = PACKAGE / "work"
for dependency in (
    WORK / "c07d3e",
    WORK / "c07d4",
    WORK / "c07d5",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

from finite_window_classification import has_fail  # noqa: E402
from c07d3e1_targeted_search import (  # noqa: E402
    bad_mask_records,
    valid_single_add_repairs,
)
from c07d3e_component_viability import components6, neighbors6  # noqa: E402
from c07d5_atomic_planning_census import atomic_actions  # noqa: E402


COUNTEREXAMPLE_PATH = HERE / "c07d7d0_atomic_potential_counterexample.json"
D7B_RESULTS = WORK / "c07d7" / "c07d7b_satellite_depth4_attack_results.json"


def serial(points):
    return tuple(sorted(tuple(point) for point in points))


def phi(state):
    return len(components6(state)) + int(has_fail(state))


def fail(reason, state, action=None, successor=None, extra=None):
    payload = {
        "status": "COUNTEREXAMPLE",
        "reason": reason,
        "state": serial(state),
        "state_has_fail": has_fail(state),
        "state_component_count": len(components6(state)),
        "state_phi": phi(state),
        "action": action,
        "successor": None if successor is None else serial(successor),
        "successor_has_fail": None if successor is None else has_fail(successor),
        "successor_component_count": (
            None if successor is None else len(components6(successor))
        ),
        "successor_phi": None if successor is None else phi(successor),
        "extra": extra,
    }
    COUNTEREXAMPLE_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    raise AssertionError(f"{reason}; preserved at {COUNTEREXAMPLE_PATH}")


def audit_state(state, suite, counters):
    state = frozenset(tuple(point) for point in state)
    counters["states_audited"] += 1
    counters[f"states_{'defective' if has_fail(state) else 'valid'}"] += 1

    repairs = set(valid_single_add_repairs(state))
    if not has_fail(state) and repairs:
        fail("valid state unexpectedly has N1 repairs", state, extra=serial(repairs))

    if has_fail(state):
        bad_records = bad_mask_records(state)
        for repair in repairs:
            contact_count = sum(neighbor in state for neighbor in neighbors6(repair))
            if contact_count == 0:
                fail(
                    "N1 repair has no 6-neighbor in current state",
                    state,
                    extra={"repair": repair, "bad_mask_count": len(bad_records)},
                )
            counters["n1_repair_contact_checks"] += 1

    for action in atomic_actions(state):
        counters["transitions_audited"] += 1
        for role in action["roles"]:
            counters[f"role_occurrences_{role}"] += 1
        additions = frozenset(tuple(point) for point in action["additions"])
        successor = state | additions
        if not additions or successor == state:
            fail("atomic action is not a strict nonempty addition", state, action)
        if has_fail(successor):
            fail("atomic action produced Q2/Q3-invalid successor", state, action, successor)

        before_components = len(components6(state))
        after_components = len(components6(successor))
        if "N2" in action["roles"] and not after_components < before_components:
            fail("N2 action did not strictly contract 6-components", state, action, successor)
        if "N1" in action["roles"] and after_components > before_components:
            fail("N1 action increased 6-component count", state, action, successor)
        if not phi(successor) < phi(state):
            fail("Phi did not strictly decrease", state, action, successor)

        counters[f"phi_drop_{phi(state) - phi(successor)}"] += 1
        counters[f"suite_transitions_{suite}"] += 1


def cube_states():
    cube = tuple(itertools.product((0, 1), repeat=3))
    for size in range(1, len(cube) + 1):
        for subset in itertools.combinations(cube, size):
            yield frozenset(subset)


def d7b_states():
    payload = json.loads(D7B_RESULTS.read_text())
    seen = set()
    for record in payload["tested"]:
        state = frozenset(tuple(point) for point in record["state"])
        if state not in seen:
            seen.add(state)
            yield "d7b_initial", state
        for repair in record["valid_N1_repairs"]:
            successor = state | {tuple(repair)}
            if successor not in seen:
                seen.add(successor)
                yield "d7b_n1_successor", successor
        current = state
        for step in record["first_shortest_plan"]:
            current = current | {tuple(point) for point in step["additions"]}
            if current not in seen:
                seen.add(current)
                yield "d7b_recorded_plan_state", current


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--suite", choices=("cube", "d7b", "all"), default="all"
    )
    args = parser.parse_args()
    result_path = HERE / f"c07d7d0_atomic_potential_audit_{args.suite}_results.json"
    if COUNTEREXAMPLE_PATH.exists():
        COUNTEREXAMPLE_PATH.unlink()

    counters = Counter()
    suite_state_counts = Counter()
    if args.suite in ("cube", "all"):
        for state in cube_states():
            suite_state_counts["cube_nonempty_subsets"] += 1
            audit_state(state, "cube", counters)
    if args.suite in ("d7b", "all"):
        for suite, state in d7b_states():
            suite_state_counts[suite] += 1
            audit_state(state, suite, counters)

    result = {
        "checkpoint": "C07-D7D0",
        "status": "PASS",
        "scope": {
            "cube": "all 255 nonempty subsets of {0,1}^3",
            "d7b": (
                "all declared 150 initial states, their distinct N1 successors, "
                "and all states on each recorded first shortest plan"
            ),
        },
        "stop_rule": "first violation writes counterexample JSON and aborts",
        "suite_state_counts": dict(sorted(suite_state_counts.items())),
        "counters": dict(sorted(counters.items())),
        "counterexample_file_created": COUNTEREXAMPLE_PATH.exists(),
    }
    result_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
