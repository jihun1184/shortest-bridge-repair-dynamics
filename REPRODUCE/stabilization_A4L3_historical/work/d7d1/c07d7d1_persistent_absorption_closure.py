"""C07-D7D1: full N2-reachable closure for the D7B depth-three family.

The output records exact state/transition counts, current root-component
partition identities, every distinct absorption block with multiplicity,
rho/gamma profiles, R*, and a digest of all generated transitions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
import time
from collections import Counter, deque
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
from c07d3e_component_viability import components6  # noqa: E402
from c07d5_atomic_planning_census import atomic_actions  # noqa: E402


D7B_RESULTS = WORK / "c07d7" / "c07d7b_satellite_depth4_attack_results.json"
RESULT_PATH = HERE / "c07d7d1_persistent_absorption_closure_results.json"


def serial_state(state):
    return tuple(sorted(tuple(point) for point in state))


def encode_partition(partition):
    return tuple(tuple(sorted(block)) for block in partition)


def root_identity_partition(state, root_components):
    current = components6(state)
    blocks = []
    assigned = set()
    for component in current:
        block = tuple(
            index
            for index, root_component in enumerate(root_components)
            if root_component <= component
        )
        if not block:
            raise AssertionError("current component contains no root component")
        if assigned.intersection(block):
            raise AssertionError("root component assigned to multiple descendants")
        assigned.update(block)
        blocks.append(block)
    if assigned != set(range(len(root_components))):
        raise AssertionError("some root component has no descendant")
    return tuple(sorted(blocks))


def absorption_block(before_partition, after_partition):
    merged = []
    for after_block in after_partition:
        contained = tuple(
            before_block
            for before_block in before_partition
            if set(before_block) <= set(after_block)
        )
        if len(contained) >= 2:
            merged.append(tuple(sorted(contained)))
    if len(merged) != 1:
        raise AssertionError(
            f"expected one nontrivial absorption block, got {merged}; "
            f"before={before_partition}, after={after_partition}"
        )
    return merged[0]


def transition_key(before_partition, block, after_partition):
    return json.dumps(
        {
            "before": encode_partition(before_partition),
            "absorbed_current_blocks": encode_partition(block),
            "after": encode_partition(after_partition),
        },
        separators=(",", ":"),
        sort_keys=True,
    )


def audit_root(task):
    orbit_index, repair_index, initial_state, repair = task
    started = time.time()
    initial_state = frozenset(tuple(point) for point in initial_state)
    repair = tuple(repair)
    root = initial_state | {repair}
    if has_fail(root):
        raise AssertionError("N1 successor must be Q2/Q3-valid")
    root_components = components6(root)
    if len(root_components) != 5:
        raise AssertionError(f"expected five root components, got {len(root_components)}")

    queue = deque([(root, 0)])
    seen = {root}
    state_depth_histogram = Counter()
    state_component_histogram = Counter()
    current_partition_histogram = Counter()
    action_rho_histogram = Counter()
    action_gamma_histogram = Counter()
    component_profiles = {}
    partition_transition_histogram = Counter()
    transition_records = []
    max_rho = 0
    max_depth = 0

    while queue:
        state, depth = queue.popleft()
        max_depth = max(max_depth, depth)
        before_components = components6(state)
        before_count = len(before_components)
        before_partition = root_identity_partition(state, root_components)
        state_depth_histogram[depth] += 1
        state_component_histogram[before_count] += 1
        current_partition_histogram[json.dumps(encode_partition(before_partition))] += 1

        actions = atomic_actions(state)
        profile = component_profiles.setdefault(
            before_count,
            {"state_count": 0, "action_count": 0, "max_rho": 0, "rho_histogram": Counter()},
        )
        profile["state_count"] += 1
        for action in actions:
            if set(action["roles"]) != {"N2"}:
                raise AssertionError(
                    f"valid N2-closure state has non-N2-only action: {action['roles']}"
                )
            additions = frozenset(tuple(point) for point in action["additions"])
            successor = state | additions
            if has_fail(successor):
                raise AssertionError("generated N2 successor is invalid")
            after_count = len(components6(successor))
            if not after_count < before_count:
                raise AssertionError("generated N2 action did not contract components")

            after_partition = root_identity_partition(successor, root_components)
            block = absorption_block(before_partition, after_partition)
            rho = len(block)
            gamma = before_count - after_count
            if gamma != rho - 1:
                raise AssertionError("gamma != rho - 1")

            max_rho = max(max_rho, rho)
            action_rho_histogram[rho] += 1
            action_gamma_histogram[gamma] += 1
            profile["action_count"] += 1
            profile["max_rho"] = max(profile["max_rho"], rho)
            profile["rho_histogram"][rho] += 1
            key = transition_key(before_partition, block, after_partition)
            partition_transition_histogram[key] += 1
            transition_records.append(
                json.dumps(
                    {
                        "state": serial_state(state),
                        "additions": serial_state(additions),
                        "before_partition": encode_partition(before_partition),
                        "absorbed_current_blocks": encode_partition(block),
                        "after_partition": encode_partition(after_partition),
                        "rho": rho,
                        "gamma": gamma,
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                )
            )
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, depth + 1))

    digest = hashlib.sha256(
        "\n".join(sorted(transition_records)).encode("utf-8")
    ).hexdigest()
    encoded_profiles = {}
    for count, profile in sorted(component_profiles.items(), reverse=True):
        encoded_profiles[str(count)] = {
            "state_count": profile["state_count"],
            "action_count": profile["action_count"],
            "max_rho": profile["max_rho"],
            "rho_histogram": {
                str(key): value for key, value in sorted(profile["rho_histogram"].items())
            },
        }

    return {
        "root_id": f"orbit_{orbit_index}:repair_{repair_index}",
        "orbit_index": orbit_index,
        "repair_index": repair_index,
        "repair": repair,
        "root_components": tuple(serial_state(component) for component in root_components),
        "root_component_count": len(root_components),
        "reachable_state_count": len(seen),
        "transition_count": len(transition_records),
        "max_reachable_N2_depth": max_depth,
        "R_star": max_rho,
        "persistent_bound_verified": f"rho <= {max_rho}",
        "state_depth_histogram": {
            str(key): value for key, value in sorted(state_depth_histogram.items())
        },
        "state_component_count_histogram": {
            str(key): value for key, value in sorted(state_component_histogram.items(), reverse=True)
        },
        "action_rho_histogram": {
            str(key): value for key, value in sorted(action_rho_histogram.items())
        },
        "action_gamma_histogram": {
            str(key): value for key, value in sorted(action_gamma_histogram.items())
        },
        "component_count_indexed_rank_profile": encoded_profiles,
        "current_partition_identity_histogram": dict(sorted(current_partition_histogram.items())),
        "partition_absorption_transition_histogram": dict(
            sorted(partition_transition_histogram.items())
        ),
        "transition_sha256": digest,
        "elapsed_seconds": round(time.time() - started, 6),
    }


def tasks(limit=None):
    payload = json.loads(D7B_RESULTS.read_text())
    selected = [record for record in payload["tested"] if record["depth"] == 3]
    if len(selected) != 131:
        raise AssertionError(f"expected 131 depth-three states, got {len(selected)}")
    output = []
    for record in selected:
        for repair_index, repair in enumerate(record["valid_N1_repairs"]):
            output.append(
                (
                    record["orbit_index"],
                    repair_index,
                    record["state"],
                    repair,
                )
            )
    if len(output) != 262:
        raise AssertionError(f"expected 262 N1 successors, got {len(output)}")
    return output if limit is None else output[:limit]


def summarize(records, requested_root_count):
    rstar_histogram = Counter(record["R_star"] for record in records)
    total_states = sum(record["reachable_state_count"] for record in records)
    total_transitions = sum(record["transition_count"] for record in records)
    return {
        "checkpoint": "C07-D7D1",
        "status": "EXHAUSTED" if len(records) == 262 else "PARTIAL",
        "scope": "full N2-reachable closures of N1 successors in the 131 D7B depth-three states",
        "requested_root_count": requested_root_count,
        "completed_root_count": len(records),
        "total_reachable_state_instances": total_states,
        "total_transition_instances": total_transitions,
        "R_star_histogram": {
            str(key): value for key, value in sorted(rstar_histogram.items())
        },
        "maximum_R_star": max(rstar_histogram, default=0),
        "roots": sorted(records, key=lambda record: (record["orbit_index"], record["repair_index"])),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    work_items = tasks(args.limit)
    started = time.time()
    records = []
    if args.workers == 1:
        iterator = map(audit_root, work_items)
        pool = None
    else:
        pool = mp.Pool(processes=args.workers)
        iterator = pool.imap_unordered(audit_root, work_items)
    try:
        for index, record in enumerate(iterator, start=1):
            records.append(record)
            checkpoint = summarize(records, len(work_items))
            checkpoint["elapsed_seconds"] = round(time.time() - started, 6)
            RESULT_PATH.write_text(json.dumps(checkpoint, indent=2) + "\n")
            print(
                f"[{index}/{len(work_items)}] {record['root_id']} "
                f"states={record['reachable_state_count']} "
                f"transitions={record['transition_count']} R*={record['R_star']}",
                flush=True,
            )
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    final = summarize(records, len(work_items))
    final["elapsed_seconds"] = round(time.time() - started, 6)
    RESULT_PATH.write_text(json.dumps(final, indent=2) + "\n")
    print(json.dumps({key: value for key, value in final.items() if key != "roots"}, indent=2))


if __name__ == "__main__":
    main()
