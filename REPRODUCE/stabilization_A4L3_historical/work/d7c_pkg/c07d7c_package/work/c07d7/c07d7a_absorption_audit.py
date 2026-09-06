"""C07-D7A: finite Single-Bridge Absorption audit for the D6C witness."""

from __future__ import annotations

import json
import itertools
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

from automaton_c06c2 import gen_all_monotone_paths  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402
from c07d3e_component_viability import (  # noqa: E402
    component_certificates,
    components6,
    descendant,
    neighbors6,
    shortest_endpoint_pairs,
)
from c07d5_atomic_planning_census import atomic_actions, goal  # noqa: E402
from c07d4_planning_census import certificate_bridge_actions  # noqa: E402
from c07d6c_depth3_verify import PLAN, WITNESS  # noqa: E402


N1_CHOICES = (((-1, -1, 0),), ((0, 0, 0),))


def serial(points):
    return tuple(sorted(points))


def component_labels(components):
    distinguished = {
        (-4, 1, 0): "satellite",
        (-3, -1, -1): "left_singleton",
        (0, 2, -1): "right_singleton",
    }
    labels = []
    for component in components:
        hits = [label for point, label in distinguished.items() if point in component]
        labels.append(hits[0] if hits else "central")
    return tuple(labels)


def partition_of_old_components(old_components, after_components):
    groups = {}
    for index, component in enumerate(old_components):
        child = descendant(component, after_components)
        groups.setdefault(child, []).append(index)
    return tuple(sorted((tuple(indices) for indices in groups.values()), key=lambda x: (len(x), x)))


def touched_components(additions, old_components):
    additions = set(additions)
    touched = []
    for index, component in enumerate(old_components):
        if any(neighbor in additions for point in component for neighbor in neighbors6(point)):
            touched.append(index)
    return tuple(touched)


def main():
    successor_audits = []
    for first_additions in N1_CHOICES:
        state1 = WITNESS | frozenset(first_additions)
        assert not goal(state1)
        old_components = components6(state1)
        labels = component_labels(old_components)
        assert len(old_components) == 4
        records = []
        for action in atomic_actions(state1):
            assert action["roles"] == ("N2",)
            additions = frozenset(tuple(point) for point in action["additions"])
            state2 = state1 | additions
            after_components = components6(state2)
            partition = partition_of_old_components(old_components, after_components)
            merged_blocks = tuple(
                tuple(labels[index] for index in block) for block in partition
            )
            records.append(
                {
                    "additions": serial(additions),
                    "addition_count": len(additions),
                    "witness_certificate_count": len(action["witnesses"]),
                    "touched_components": tuple(labels[i] for i in touched_components(additions, old_components)),
                    "old_component_partition": merged_blocks,
                    "largest_absorbed_block": max(map(len, partition)),
                    "successor_component_count": len(after_components),
                    "goal": goal(state2),
                }
            )

        raw_shortest_orderings = 0
        raw_full_absorption = 0
        raw_full_absorption_compatible = 0
        raw_full_absorption_examples = []
        pair_audits = []
        for left_index, right_index in itertools.combinations(range(4), 2):
            certificate = (old_components[left_index], old_components[right_index])
            _, endpoint_pairs = shortest_endpoint_pairs(*certificate)
            pair_raw = 0
            pair_max_absorbed = 0
            for start, end in endpoint_pairs:
                for path in gen_all_monotone_paths(start, end):
                    raw_shortest_orderings += 1
                    pair_raw += 1
                    state2 = state1 | frozenset(path)
                    partition = partition_of_old_components(
                        old_components, components6(state2)
                    )
                    absorbed = max(map(len, partition))
                    pair_max_absorbed = max(pair_max_absorbed, absorbed)
                    if absorbed != 4:
                        continue
                    raw_full_absorption += 1
                    compatible = not has_fail(state2)
                    raw_full_absorption_compatible += int(compatible)
                    if len(raw_full_absorption_examples) < 8:
                        raw_full_absorption_examples.append(
                            {
                                "certificate": tuple(serial(c) for c in certificate),
                                "start": start,
                                "end": end,
                                "path": path,
                                "compatible": compatible,
                            }
                        )
            bridge_actions, bridge_stats = certificate_bridge_actions(
                state1, certificate
            )
            pair_audits.append(
                {
                    "component_pair": (labels[left_index], labels[right_index]),
                    "distance": bridge_stats["distance"],
                    "endpoint_pair_count": bridge_stats["endpoint_pair_count"],
                    "raw_shortest_ordering_count": pair_raw,
                    "compatible_shortest_ordering_count": bridge_stats["compatible_ordering_count"],
                    "distinct_compatible_action_count": len(bridge_actions),
                    "max_old_components_absorbed_by_raw_shortest_ordering": pair_max_absorbed,
                }
            )

        component_histogram = Counter(record["successor_component_count"] for record in records)
        absorption_histogram = Counter(record["largest_absorbed_block"] for record in records)
        touch_histogram = Counter(len(record["touched_components"]) for record in records)
        assert records
        assert all(not record["goal"] for record in records)
        assert max(record["largest_absorbed_block"] for record in records) < 4
        successor_audits.append(
            {
                "first_N1_additions": first_additions,
                "component_labels": labels,
                "components": tuple(serial(component) for component in old_components),
                "N2_action_count": len(records),
                "successor_component_count_histogram": dict(sorted(component_histogram.items())),
                "largest_absorbed_block_histogram": dict(sorted(absorption_histogram.items())),
                "touched_component_count_histogram": dict(sorted(touch_histogram.items())),
                "max_components_absorbed_by_one_N2": max(record["largest_absorbed_block"] for record in records),
                "single_N2_goal_count": sum(record["goal"] for record in records),
                "raw_shortest_ordering_count": raw_shortest_orderings,
                "raw_full_absorption_ordering_count": raw_full_absorption,
                "compatible_full_absorption_ordering_count": raw_full_absorption_compatible,
                "raw_full_absorption_examples": raw_full_absorption_examples,
                "component_pair_audits": pair_audits,
                "actions": records,
            }
        )

    explicit_plan_second = frozenset(PLAN[1])
    first_audit = successor_audits[0]
    planned_record = next(
        record for record in first_audit["actions"]
        if frozenset(tuple(point) for point in record["additions"]) == explicit_plan_second
    )

    result = {
        "witness": serial(WITNESS),
        "finite_obstruction_statement": (
            "For either valid initial N1 action, the successor has four 6-components; "
            "every admissible shortest compatible N2 action merges at most three old "
            "components, hence no N2 successor is Goal."
        ),
        "successors": successor_audits,
        "explicit_depth3_plan_second_action": planned_record,
        "scope": (
            "Finite canonical-state certificate. This audit does not yet prove a "
            "state-independent geometric lemma or identify a unique causal mechanism."
        ),
    }
    output = HERE / "c07d7a_absorption_audit_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D7A absorption audit complete")
    for audit in successor_audits:
        print("first", audit["first_N1_additions"])
        print("N2 actions", audit["N2_action_count"])
        print("component-count histogram", audit["successor_component_count_histogram"])
        print("largest-block histogram", audit["largest_absorbed_block_histogram"])
        print("touch-count histogram", audit["touched_component_count_histogram"])
        print(
            "raw/full/compatible-full orderings",
            audit["raw_shortest_ordering_count"],
            audit["raw_full_absorption_ordering_count"],
            audit["compatible_full_absorption_ordering_count"],
        )


if __name__ == "__main__":
    main()
