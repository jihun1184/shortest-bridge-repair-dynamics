"""C07-D7B: targeted second-satellite attack for exact atomic depth four."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter
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

from finite_window_classification import has_fail  # noqa: E402
from c07d3e1_targeted_search import valid_single_add_repairs  # noqa: E402
from c07d3e_component_viability import components6, neighbors6  # noqa: E402
from c07d5_atomic_planning_census import (  # noqa: E402
    atomic_actions,
    canonical_isometry_class,
    first_action_type,
    goal,
)
from c07d6b1_one_voxel_break_search import dual_role_N1_repairs  # noqa: E402
from c07d6b3_overlap_attack import preserves_all_current_N2_fast  # noqa: E402
from c07d6c_depth3_verify import WITNESS as X3  # noqa: E402


DISTANCE_CAP = 4


def serial(points):
    return tuple(sorted(points))


def isolated(point, state):
    return point not in state and not any(neighbor in state for neighbor in neighbors6(point))


def schedule_digest(schedules):
    payload = json.dumps(sorted(schedules), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def exact_sequence_audit(start, max_depth=4):
    """Exhaustive schedule-tree search with per-depth counts and digests."""
    start = frozenset(start)
    frontier = ((start, tuple()),)
    depth_audits = []
    for depth in range(1, max_depth + 1):
        next_frontier = []
        schedules = []
        goals = []
        transitions = 0
        for state, schedule in frontier:
            for action in atomic_actions(state):
                transitions += 1
                additions = tuple(tuple(point) for point in action["additions"])
                successor = state | frozenset(additions)
                step = {
                    "additions": additions,
                    "roles": action["roles"],
                    "type": first_action_type(action["roles"]),
                    "successor_component_count": len(components6(successor)),
                }
                next_schedule = schedule + (step,)
                schedule_key = tuple(item["additions"] for item in next_schedule)
                schedules.append(schedule_key)
                if goal(successor):
                    goals.append(next_schedule)
                else:
                    next_frontier.append((successor, next_schedule))
        depth_audits.append(
            {
                "depth": depth,
                "frontier_state_schedule_count": len(frontier),
                "transition_count": transitions,
                "distinct_schedule_count": len(set(schedules)),
                "schedule_sha256": schedule_digest(tuple(set(schedules))),
                "goal_schedule_count": len(goals),
            }
        )
        if goals:
            return depth, tuple(goals), tuple(depth_audits)
        frontier = tuple(next_frontier)
        if not frontier:
            return None, tuple(), tuple(depth_audits)
    return None, tuple(), tuple(depth_audits)


def fast_plan_search(start, max_depth=4):
    """State-deduplicated BFS used only to locate a decisive witness."""
    start = frozenset(start)
    frontier = {start: tuple()}
    visited = {start}
    audits = []
    for depth in range(1, max_depth + 1):
        next_frontier = {}
        transitions = 0
        for state, schedule in frontier.items():
            for action in atomic_actions(state):
                transitions += 1
                additions = tuple(tuple(point) for point in action["additions"])
                successor = state | frozenset(additions)
                step = {
                    "additions": additions,
                    "roles": action["roles"],
                    "type": first_action_type(action["roles"]),
                    "successor_component_count": len(components6(successor)),
                }
                next_schedule = schedule + (step,)
                if goal(successor):
                    audits.append(
                        {
                            "depth": depth,
                            "frontier_state_count": len(frontier),
                            "transition_count_until_first_goal": transitions,
                        }
                    )
                    return depth, next_schedule, tuple(audits)
                if successor not in visited:
                    visited.add(successor)
                    next_frontier.setdefault(successor, next_schedule)
        audits.append(
            {
                "depth": depth,
                "frontier_state_count": len(frontier),
                "transition_count": transitions,
                "new_state_count": len(next_frontier),
                "goal_count": 0,
            }
        )
        frontier = next_frontier
        if not frontier:
            return None, None, tuple(audits)
    return None, None, tuple(audits)


def main():
    minima = tuple(min(point[a] for point in X3) - 3 for a in range(3))
    maxima = tuple(max(point[a] for point in X3) + 3 for a in range(3))
    window = tuple(itertools.product(*(range(minima[a], maxima[a] + 1) for a in range(3))))

    # Start with nearby isolated satellites: their finite shortest-path action
    # closures are much smaller and therefore give the sharpest first attack.
    raw = []
    for point in window:
        if not isolated(point, X3):
            continue
        distance = min(sum(abs(point[a] - old[a]) for a in range(3)) for old in X3)
        if distance > DISTANCE_CAP:
            continue
        raw.append((distance, point))
    raw.sort(key=lambda item: (item[0], item[1]))

    representatives = {}
    for distance, point in raw:
        state = X3 | {point}
        key = canonical_isometry_class(state)
        representatives.setdefault(key, (state, point, distance))

    counters = {
        "raw_isolated_candidates": len(raw),
        "quotient_candidates": len(representatives),
        "five_component": 0,
        "defective": 0,
        "valid_N1": 0,
        "no_dual": 0,
        "preservation_empty": 0,
        "planned": 0,
    }
    tested = []
    decisive = None
    for orbit_index, (_, (state, point, distance)) in enumerate(representatives.items()):
        if len(components6(state)) != 5:
            continue
        counters["five_component"] += 1
        if not has_fail(state):
            continue
        counters["defective"] += 1
        repairs = valid_single_add_repairs(state)
        if not repairs:
            continue
        counters["valid_N1"] += 1
        dual = dual_role_N1_repairs(state, repairs)
        if dual:
            continue
        counters["no_dual"] += 1
        actions = atomic_actions(state)
        if any(preserves_all_current_N2_fast(state, action) for action in actions):
            continue
        counters["preservation_empty"] += 1

        depth, first_plan, fast_audits = fast_plan_search(state, max_depth=4)
        counters["planned"] += 1
        plans = tuple()
        depth_audits = fast_audits
        if depth == 4:
            exact_depth, plans, depth_audits = exact_sequence_audit(
                state, max_depth=4
            )
            assert exact_depth == depth and plans
            first_plan = plans[0]
        record = {
            "orbit_index": orbit_index,
            "second_satellite": point,
            "distance_to_X3": distance,
            "state": serial(state),
            "valid_N1_repairs": repairs,
            "initial_atomic_action_count": len(actions),
            "depth": depth,
            "shortest_goal_schedule_count": len(plans) if depth == 4 else None,
            "first_shortest_plan": first_plan,
            "depth_audits": depth_audits,
            "audit_mode": "full-sequence" if depth == 4 else "state-deduplicated BFS",
            "classification": (
                "DEPTH4" if depth == 4 else
                "DEPTH3" if depth == 3 else
                "DEPTH2" if depth == 2 else
                "SEARCH_UNRESOLVED"
            ),
        }
        tested.append(record)
        print("tested", counters["planned"], "satellite", point, "depth", depth)
        if depth == 4:
            decisive = record
            break

    result = {
        "family": {
            "base": "D6C exact-depth-3 witness X3",
            "box_min": minima,
            "box_max": maxima,
            "distance_cap_to_X3": DISTANCE_CAP,
            "required_second_satellite_isolated": True,
            "required_component_count": 5,
            "admission": "has_fail; A_N1 nonempty; no dual role; all-atomic P_preserve empty",
        },
        "counters": counters,
        "tested_depth_histogram": dict(sorted(Counter(record["depth"] for record in tested).items())),
        "tested_distance_histogram": dict(sorted(Counter(record["distance_to_X3"] for record in tested).items())),
        "tested": tested,
        "decisive_depth4_hit": decisive,
        "stop_rule": {
            "depth4_hit": decisive is not None,
            "family_exhausted": decisive is None and counters["planned"] == counters["preservation_empty"],
            "atomic_unreachable_claimed": False,
        },
    }
    output = HERE / "c07d7b_satellite_depth4_attack_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D7B complete", counters)
    print("depth4 hit", decisive is not None)


if __name__ == "__main__":
    main()
