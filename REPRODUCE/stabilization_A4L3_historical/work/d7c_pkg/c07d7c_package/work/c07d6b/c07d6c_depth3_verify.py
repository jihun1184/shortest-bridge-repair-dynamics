"""Independent certificate audit for the C07-D6C exact-depth-3 witness."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
for dependency in (
    HERE,
    HERE.parent / "c07d3e",
    HERE.parent / "c07d4",
    HERE.parent / "c07d5",
    HERE.parent / "c07d3b" / "c07a_scripts",
):
    sys.path.insert(0, str(dependency))

from finite_window_classification import has_fail  # noqa: E402
from c07d3e1_targeted_search import valid_single_add_repairs  # noqa: E402
from c07d3e_component_viability import components6  # noqa: E402
from c07d5_atomic_planning_census import (  # noqa: E402
    atomic_actions,
    goal,
    preserves_all_current_N2,
    shortest_atomic_plans,
)
from c07d6b1_one_voxel_break_search import dual_role_N1_repairs  # noqa: E402


WITNESS = frozenset(
    {
        (-4, 1, 0),
        (-3, -1, -1),
        (-1, -1, -1),
        (-1, 0, -1),
        (-1, 0, 0),
        (0, -1, -1),
        (0, -1, 0),
        (0, 2, -1),
    }
)

PLAN = (
    ((-1, -1, 0),),
    ((-4, -1, -1), (-4, -1, 0), (-4, 0, 0)),
    ((-4, 1, -1), (-3, 1, -1), (-2, 1, -1), (-1, 1, -1), (-1, 2, -1)),
)


def key(action):
    return tuple(tuple(point) for point in action["additions"])


def main():
    assert has_fail(WITNESS)
    assert len(components6(WITNESS)) == 4
    repairs = valid_single_add_repairs(WITNESS)
    assert repairs == ((-1, -1, 0), (0, 0, 0))
    assert dual_role_N1_repairs(WITNESS, repairs) == tuple()

    first_actions = atomic_actions(WITNESS)
    assert len(first_actions) == 2
    assert {key(action) for action in first_actions} == {
        ((-1, -1, 0),),
        ((0, 0, 0),),
    }
    assert all(action["roles"] == ("N1",) for action in first_actions)

    preservation = []
    for action in first_actions:
        allowed, obligations = preserves_all_current_N2(WITNESS, action)
        failed = sum(not obligation["viable"] for obligation in obligations)
        assert not allowed and failed == 1
        preservation.append({"additions": key(action), "failed_obligations": failed})

    one_step_goals = 0
    two_step_sequences = 0
    two_step_goals = 0
    for first in first_actions:
        state1 = WITNESS | frozenset(key(first))
        one_step_goals += int(goal(state1))
        for second in atomic_actions(state1):
            state2 = state1 | frozenset(key(second))
            two_step_sequences += 1
            two_step_goals += int(goal(state2))
    assert one_step_goals == 0
    assert two_step_sequences == 86
    assert two_step_goals == 0

    state = WITNESS
    component_trace = [len(components6(state))]
    role_trace = []
    for additions in PLAN:
        choices = {key(action): action for action in atomic_actions(state)}
        assert additions in choices
        role_trace.append(choices[additions]["roles"])
        state = state | frozenset(additions)
        component_trace.append(len(components6(state)))
    assert not goal(WITNESS)
    assert not goal(WITNESS | frozenset(PLAN[0]))
    assert goal(state)
    assert component_trace == [4, 4, 3, 1]
    assert role_trace == [("N1",), ("N2",), ("N2",)]

    depth, plans, stats = shortest_atomic_plans(WITNESS, max_depth=3)
    assert depth == 3 and len(plans) == 409

    result = {
        "witness": tuple(sorted(WITNESS)),
        "initial_component_count": 4,
        "valid_N1_repairs": repairs,
        "dual_role_N1_repairs": tuple(),
        "initial_atomic_actions": tuple(key(action) for action in first_actions),
        "preservation": preservation,
        "lower_bound": {
            "one_step_goal_count": one_step_goals,
            "two_step_sequence_count": two_step_sequences,
            "two_step_goal_count": two_step_goals,
        },
        "upper_bound": {
            "plan": PLAN,
            "role_trace": role_trace,
            "component_trace": component_trace,
            "final_goal": goal(state),
        },
        "exact_depth": depth,
        "shortest_plan_count": len(plans),
        "planner_stats": stats,
    }
    output = HERE / "c07d6c_depth3_verification.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
