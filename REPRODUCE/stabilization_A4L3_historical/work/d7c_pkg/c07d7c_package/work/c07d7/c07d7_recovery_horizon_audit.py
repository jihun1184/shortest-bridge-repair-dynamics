"""Separate obligation-recovery horizon from residual goal depth at D6C."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORK = HERE.parent
for dependency in (
    WORK / "c07d3e",
    WORK / "c07d4",
    WORK / "c07d5",
    WORK / "c07d6b",
    WORK / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

from c07d3e_component_viability import (  # noqa: E402
    component_bridge_exists,
    component_certificates,
    components6,
    descendant,
)
from c07d5_atomic_planning_census import atomic_actions, goal, shortest_atomic_plans  # noqa: E402
from c07d6c_depth3_verify import PLAN, WITNESS  # noqa: E402


N1_CHOICES = (((-1, -1, 0),), ((0, 0, 0),))


def original_obligation_audit(original, successor, *, crosscheck=True):
    after_components = components6(successor)
    records = []
    for certificate in component_certificates(original):
        left = descendant(certificate[0], after_components)
        right = descendant(certificate[1], after_components)
        resolved = left == right
        bridgeable = None
        if not resolved:
            bridgeable, _ = component_bridge_exists(
                successor, left, right, crosscheck=crosscheck
            )
        records.append(
            {
                "resolved": resolved,
                "bridgeable": bridgeable,
                "viable": resolved or bridgeable,
            }
        )
    return records


def main():
    audits = []
    for first in N1_CHOICES:
        state1 = WITNESS | frozenset(first)
        immediate = original_obligation_audit(WITNESS, state1)
        assert sum(record["viable"] for record in immediate) == 5
        restoring = []
        for action in atomic_actions(state1):
            additions = tuple(tuple(point) for point in action["additions"])
            state2 = state1 | frozenset(additions)
            obligations = original_obligation_audit(WITNESS, state2)
            if all(record["viable"] for record in obligations):
                restoring.append(additions)
        assert restoring
        residual_depth, plans, stats = shortest_atomic_plans(state1, max_depth=3)
        assert residual_depth == 2
        audits.append(
            {
                "first_N1": first,
                "original_certificate_count": len(immediate),
                "viable_immediately_after_N1": sum(record["viable"] for record in immediate),
                "one_action_continuations": len(atomic_actions(state1)),
                "one_action_original_obligation_restorations": len(restoring),
                "obligation_recovery_horizon": 1,
                "residual_goal_depth": residual_depth,
                "residual_shortest_plan_count": len(plans),
                "residual_planner_stats": stats,
                "first_restoring_action": restoring[0],
            }
        )

    state = WITNESS | frozenset(PLAN[0]) | frozenset(PLAN[1])
    explicit = original_obligation_audit(WITNESS, state)
    assert all(record["viable"] for record in explicit)
    assert not goal(state)

    result = {
        "definitions": {
            "obligation_recovery_horizon": (
                "Minimum number of subsequent frozen atomic actions after a fixed "
                "initial N1 action until every genuine N2 certificate of the original "
                "state is viable between its current descendants."
            ),
            "residual_goal_depth": (
                "Minimum number of subsequent frozen atomic actions after the fixed "
                "initial N1 action until Goal."
            ),
        },
        "audits": audits,
        "explicit_D6C_plan_after_second_action": {
            "all_original_obligations_viable": True,
            "goal": False,
        },
        "conclusion": (
            "For both initial N1 choices, obligation recovery horizon is one but "
            "residual goal depth is two. D6C therefore proves two-step residual goal "
            "planning, not a two-step delay in recovering the lost original obligation."
        ),
    }
    output = HERE / "c07d7_recovery_horizon_audit_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
