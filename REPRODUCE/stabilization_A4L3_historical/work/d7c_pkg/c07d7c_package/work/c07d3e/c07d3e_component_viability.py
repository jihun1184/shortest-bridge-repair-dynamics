"""C07-D3E0: genuine N2 component-certificate viability wrapper.

Frozen operational semantics:
  * certificates are unordered pairs of distinct 6-components of X;
  * additions give each old component a unique descendant;
  * Resolved means equality of the two descendants;
  * if unresolved, compatible N2-optimal bridges are tested over every
    endpoint pair attaining min L1 distance between the descendants.

The last bullet is the endpoint quantifier used by S2.1's d6(Ci,Cj)-1
cost audit.  The wrapper records every endpoint decision and can cross-check
the compressed decider against full monotone-order brute force.
"""

from __future__ import annotations

import itertools
import sys
from collections import deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "c07d3b"
sys.path.insert(0, str(PARENT / "c07a_scripts"))

from automaton_c06c2 import brute_force_decide  # noqa: E402
from compressed_decider import compressed_decide  # noqa: E402


Point = tuple[int, int, int]
Component = frozenset[Point]
Certificate = tuple[Component, Component]


def neighbors6(point: Point):
    for axis in range(3):
        for delta in (-1, 1):
            neighbor = list(point)
            neighbor[axis] += delta
            yield tuple(neighbor)


def components6(points) -> tuple[Component, ...]:
    unseen = set(points)
    components = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        component = {seed}
        queue = deque([seed])
        while queue:
            point = queue.popleft()
            for neighbor in neighbors6(point):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        components.append(frozenset(component))
    return tuple(sorted(components, key=lambda c: tuple(sorted(c))))


def component_certificates(points) -> tuple[Certificate, ...]:
    return tuple(itertools.combinations(components6(points), 2))


def descendant(old_component: Component, after_components) -> Component:
    matches = [component for component in after_components if old_component <= component]
    if len(matches) != 1:
        raise AssertionError(
            "addition-only old component must have exactly one descendant: "
            f"old={sorted(old_component)}, matches={list(map(sorted, matches))}"
        )
    return matches[0]


def l1(left: Point, right: Point) -> int:
    return sum(abs(a - b) for a, b in zip(left, right))


def shortest_endpoint_pairs(
    left: Component, right: Component
) -> tuple[int, tuple[tuple[Point, Point], ...]]:
    if not left or not right or left & right:
        raise ValueError("endpoint components must be nonempty and disjoint")
    distance = min(l1(s, t) for s in left for t in right)
    pairs = tuple(
        sorted((s, t) for s in left for t in right if l1(s, t) == distance)
    )
    return distance, pairs


def component_bridge_exists(background, left: Component, right: Component, *, crosscheck=False):
    """Existential compatible bridge over all d6-minimizing endpoint pairs."""
    background = frozenset(background)
    distance, pairs = shortest_endpoint_pairs(left, right)
    records = []
    exists = False
    for s, t in pairs:
        compressed, stats = compressed_decide(background, s, t)
        record = {
            "s": s,
            "t": t,
            "distance": distance,
            "compressed": compressed,
            "compressed_stats": stats,
        }
        if crosscheck:
            brute, total, compatible = brute_force_decide(background, s, t)
            if compressed != brute:
                raise AssertionError(
                    f"compressed/brute mismatch at {(s, t)}: {compressed} != {brute}"
                )
            record.update(brute=brute, total=total, compatible=compatible)
        records.append(record)
        exists |= compressed
    return exists, {
        "distance": distance,
        "new_voxel_cost": distance - 1,
        "endpoint_pairs": records,
        "endpoint_pair_count": len(records),
    }


def certificate_viability(X, v: Point, certificate: Certificate, *, crosscheck=False):
    """Evaluate Resolved OR descendant-component bridge existence."""
    X = frozenset(X)
    before_components = components6(X)
    if certificate not in tuple(itertools.combinations(before_components, 2)):
        raise ValueError("certificate must be a genuine component pair of X")
    after = X | {v}
    after_components = components6(after)
    left_descendant = descendant(certificate[0], after_components)
    right_descendant = descendant(certificate[1], after_components)
    resolved = left_descendant == right_descendant
    result = {
        "v": v,
        "resolved": resolved,
        "left_descendant": tuple(sorted(left_descendant)),
        "right_descendant": tuple(sorted(right_descendant)),
        "bridge_evaluated": not resolved,
    }
    if resolved:
        result.update(bridge_exists=None, bridge=None, viable=True)
        return True, result
    bridge_exists, bridge = component_bridge_exists(
        after, left_descendant, right_descendant, crosscheck=crosscheck
    )
    result.update(bridge_exists=bridge_exists, bridge=bridge, viable=bridge_exists)
    return bridge_exists, result
