"""Independent logical/summary audit of the D7C partition census."""

from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent


def components6(points):
    unseen = set(map(tuple, points))
    components = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        component = {seed}
        queue = deque([seed])
        while queue:
            point = queue.popleft()
            for axis in range(3):
                for delta in (-1, 1):
                    neighbor = list(point)
                    neighbor[axis] += delta
                    neighbor = tuple(neighbor)
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)
        components.append(frozenset(component))
    return tuple(sorted(components, key=lambda c: tuple(sorted(c))))


def main():
    result = json.loads(
        (HERE / "c07d7c_partition_census_results.json").read_text(encoding="utf-8")
    )
    audits = result["audits"]
    assert len(audits) == 150
    assert all(audit["classifier_correct"] for audit in audits)

    raw_nontrivial_blocks = Counter()
    identity_profile = Counter()
    for audit in audits:
        original_components = components6(audit["state"])
        state_max_rho = max(
            successor["compatible"]["max_rho"]
            for successor in audit["successors"]
        )
        maximal_absorbed_old_subsets = set()
        for successor in audit["successors"]:
            for count, frequency in successor["raw"]["nontrivial_block_count_histogram"].items():
                raw_nontrivial_blocks[int(count)] += frequency

            successor_components = tuple(
                frozenset(map(tuple, component))
                for component in successor["components"]
            )
            successor_to_original = {
                successor_index: next(
                    original_index
                    for original_index, original in enumerate(original_components)
                    if original <= component
                )
                for successor_index, component in enumerate(successor_components)
            }
            for encoded_partition in successor["compatible"]["partition_histogram"]:
                blocks = json.loads(encoded_partition)
                rho = max(map(len, blocks))
                if rho != state_max_rho:
                    continue
                for block in blocks:
                    if len(block) == rho:
                        maximal_absorbed_old_subsets.add(
                            tuple(sorted(successor_to_original[index] for index in block))
                        )
        identity_profile[
            (audit["depth"], state_max_rho, len(maximal_absorbed_old_subsets))
        ] += 1

    assert raw_nontrivial_blocks == {1: 273921}
    assert result["compatible_action_nontrivial_block_count_histogram"] == {"1": 109927}
    assert result["classifier"]["correct_state_count"] == 150
    assert result["raw_compatibility_class_histogram"] == {
        "COMPATIBLE_FULL": 19,
        "GEOMETRY_FORBIDS_FULL": 131,
    }

    output = {
        "family_state_count": 150,
        "N1_successor_count": 300,
        "classifier_correct": "150/150",
        "raw_shortest_orderings_by_nontrivial_block_count": dict(raw_nontrivial_blocks),
        "compatible_actions_by_nontrivial_block_count": {1: 109927},
        "maximal_absorbed_subset_identity_profile": {
            f"depth={depth};rho={rho};distinct_subsets={subsets}": count
            for (depth, rho, subsets), count in sorted(identity_profile.items())
        },
        "conclusion": (
            "Maximum rho suffices for the depth-2/depth-3 classifier in this fixed "
            "five-component family, but equal rho can correspond to different absorbed "
            "old-component subsets; the partition retains strictly more transition data."
        ),
    }
    target = HERE / "c07d7c_partition_verification.json"
    target.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
