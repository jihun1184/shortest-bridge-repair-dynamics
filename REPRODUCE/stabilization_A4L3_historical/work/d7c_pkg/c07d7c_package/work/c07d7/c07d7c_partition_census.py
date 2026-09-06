"""C07-D7C: absorption-partition census for all 150 admitted D7B states."""

from __future__ import annotations

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

from automaton_c06c2 import gen_all_monotone_paths  # noqa: E402
from finite_window_classification import has_fail  # noqa: E402
from c07d3e_component_viability import components6, descendant, shortest_endpoint_pairs  # noqa: E402
from c07d5_atomic_planning_census import atomic_actions, goal  # noqa: E402


def serial(points):
    return tuple(sorted(points))


def partition(old_components, successor):
    after_components = components6(successor)
    groups = {}
    for index, component in enumerate(old_components):
        child = descendant(component, after_components)
        groups.setdefault(child, []).append(index)
    blocks = tuple(sorted((tuple(indices) for indices in groups.values()), key=lambda block: (block[0], len(block))))
    return blocks


def metrics(blocks, component_count):
    rho = max(map(len, blocks))
    gamma = component_count - len(blocks)
    nontrivial = sum(len(block) > 1 for block in blocks)
    return rho, gamma, nontrivial


def histogram_json(counter):
    return {json.dumps(key, separators=(",", ":")): value for key, value in sorted(counter.items())}


def successor_partition_audit(state, repair):
    successor = state | {tuple(repair)}
    old_components = components6(successor)
    m = len(old_components)
    assert not has_fail(successor)

    compatible_partitions = Counter()
    compatible_rho = Counter()
    compatible_gamma = Counter()
    compatible_nontrivial_blocks = Counter()
    compatible_actions = atomic_actions(successor)
    assert all(action["roles"] == ("N2",) for action in compatible_actions)
    for action in compatible_actions:
        additions = frozenset(tuple(point) for point in action["additions"])
        blocks = partition(old_components, successor | additions)
        rho, gamma, nontrivial = metrics(blocks, m)
        compatible_partitions[blocks] += 1
        compatible_rho[rho] += 1
        compatible_gamma[gamma] += 1
        compatible_nontrivial_blocks[nontrivial] += 1

    raw_partitions = Counter()
    raw_rho = Counter()
    raw_gamma = Counter()
    raw_nontrivial_blocks = Counter()
    raw_orderings = 0
    raw_compatible_orderings = 0
    raw_full_orderings = 0
    raw_full_compatible_orderings = 0
    for left_index, right_index in itertools.combinations(range(m), 2):
        certificate = (old_components[left_index], old_components[right_index])
        _, endpoint_pairs = shortest_endpoint_pairs(*certificate)
        for start, end in endpoint_pairs:
            for path in gen_all_monotone_paths(start, end):
                raw_orderings += 1
                state2 = successor | frozenset(path)
                blocks = partition(old_components, state2)
                rho, gamma, nontrivial = metrics(blocks, m)
                raw_partitions[blocks] += 1
                raw_rho[rho] += 1
                raw_gamma[gamma] += 1
                raw_nontrivial_blocks[nontrivial] += 1
                compatible = not has_fail(state2)
                raw_compatible_orderings += int(compatible)
                full = len(blocks) == 1
                raw_full_orderings += int(full)
                raw_full_compatible_orderings += int(full and compatible)

    compatible_full_actions = sum(
        count for blocks, count in compatible_partitions.items() if len(blocks) == 1
    )
    return {
        "repair": tuple(repair),
        "component_count": m,
        "components": tuple(serial(component) for component in old_components),
        "compatible": {
            "action_count": len(compatible_actions),
            "partition_histogram": histogram_json(compatible_partitions),
            "rho_histogram": dict(sorted(compatible_rho.items())),
            "gamma_histogram": dict(sorted(compatible_gamma.items())),
            "nontrivial_block_count_histogram": dict(sorted(compatible_nontrivial_blocks.items())),
            "min_partition_block_count": min(map(len, compatible_partitions)) if compatible_partitions else None,
            "max_rho": max(compatible_rho) if compatible_rho else None,
            "full_absorption_action_count": compatible_full_actions,
        },
        "raw": {
            "shortest_ordering_count": raw_orderings,
            "compatible_ordering_count": raw_compatible_orderings,
            "partition_histogram": histogram_json(raw_partitions),
            "rho_histogram": dict(sorted(raw_rho.items())),
            "gamma_histogram": dict(sorted(raw_gamma.items())),
            "nontrivial_block_count_histogram": dict(sorted(raw_nontrivial_blocks.items())),
            "min_partition_block_count": min(map(len, raw_partitions)),
            "max_rho": max(raw_rho),
            "full_absorption_ordering_count": raw_full_orderings,
            "compatible_full_absorption_ordering_count": raw_full_compatible_orderings,
        },
    }


def main():
    source = HERE / "c07d7b_satellite_depth4_attack_results.json"
    d7b = json.loads(source.read_text(encoding="utf-8"))
    assert len(d7b["tested"]) == 150 and d7b["stop_rule"]["family_exhausted"]

    audits = []
    for index, record in enumerate(d7b["tested"]):
        state = frozenset(tuple(point) for point in record["state"])
        assert len(record["valid_N1_repairs"]) == 2
        assert record["first_shortest_plan"][0]["type"] == "N1_ONLY"
        successors = tuple(
            successor_partition_audit(state, tuple(repair))
            for repair in record["valid_N1_repairs"]
        )
        compatible_full = any(
            successor["compatible"]["full_absorption_action_count"] > 0
            for successor in successors
        )
        raw_full = any(
            successor["raw"]["full_absorption_ordering_count"] > 0
            for successor in successors
        )
        audit = {
            "index": index,
            "state": serial(state),
            "depth": record["depth"],
            "second_satellite": tuple(record["second_satellite"]),
            "successors": successors,
            "some_raw_full_absorption": raw_full,
            "some_compatible_full_absorption": compatible_full,
            "classifier_prediction": 2 if compatible_full else 3,
            "classifier_correct": (record["depth"] == 2) == compatible_full,
            "raw_compatibility_class": (
                "COMPATIBLE_FULL" if compatible_full else
                "COMPATIBILITY_DELETES_ALL_FULL" if raw_full else
                "GEOMETRY_FORBIDS_FULL"
            ),
        }
        audits.append(audit)
        if (index + 1) % 10 == 0:
            print("audited", index + 1, flush=True)

    class_histogram = Counter(audit["raw_compatibility_class"] for audit in audits)
    depth_class = Counter((audit["depth"], audit["raw_compatibility_class"]) for audit in audits)
    max_rho_by_state = Counter(
        (
            audit["depth"],
            max(successor["compatible"]["max_rho"] for successor in audit["successors"]),
        )
        for audit in audits
    )
    nontrivial_block_observations = Counter()
    for audit in audits:
        for successor in audit["successors"]:
            for count, frequency in successor["compatible"]["nontrivial_block_count_histogram"].items():
                nontrivial_block_observations[int(count)] += frequency

    result = {
        "semantics": {
            "absorption_partition": "old components grouped by equality of descendants after an addition-only action",
            "rho": "maximum block size",
            "gamma": "old component count minus partition block count",
        },
        "family_state_count": len(audits),
        "N1_successor_count": sum(len(audit["successors"]) for audit in audits),
        "all_initial_actions_N1_only": True,
        "all_states_have_exactly_two_N1_successors": True,
        "classifier": {
            "statement": "depth=2 iff some N1 successor has a compatible full-absorption N2 action",
            "correct_state_count": sum(audit["classifier_correct"] for audit in audits),
            "incorrect_state_count": sum(not audit["classifier_correct"] for audit in audits),
        },
        "raw_compatibility_class_histogram": dict(sorted(class_histogram.items())),
        "depth_by_raw_compatibility_class": {
            f"depth={depth};{classification}": count
            for (depth, classification), count in sorted(depth_class.items())
        },
        "depth_by_max_compatible_rho": {
            f"depth={depth};rho={rho}": count
            for (depth, rho), count in sorted(max_rho_by_state.items())
        },
        "compatible_action_nontrivial_block_count_histogram": dict(sorted(nontrivial_block_observations.items())),
        "audits": audits,
        "claim_boundary": (
            "Exact finite-family classifier. No universal depth theorem or persistent "
            "absorption bound is inferred."
        ),
    }
    output = HERE / "c07d7c_partition_census_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("C07-D7C complete")
    print("classifier", result["classifier"])
    print("raw/compatibility", result["raw_compatibility_class_histogram"])
    print("depth/rho", result["depth_by_max_compatible_rho"])
    print("nontrivial blocks", result["compatible_action_nontrivial_block_count_histogram"])


if __name__ == "__main__":
    main()
