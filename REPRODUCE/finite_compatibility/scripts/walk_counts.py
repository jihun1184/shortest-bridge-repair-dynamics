"""Reproduce Table 1 and verify the walk characterization for L=3,4,5.

The four column states are the four (x,y) positions in {-1,0}^2.
At each successive z layer a walk may stay put or move across one face;
the diagonal jump is forbidden.  Hence there are 4*3^(L-1) walks.

L=3 is independently enumerated through its minimal size.  For L=4,
all candidate repairs of size <4 are exhaustively rejected, after which
the walk family is generated and compared exactly with the frozen M0.
For L=5 the generated walk family is likewise compared exactly with the
frozen M0.  Every generated repair is rechecked with the PWC oracle.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from geometry_utils import SEED, shift  # noqa: E402
from repair_enumeration_core import universe_for  # noqa: E402
from stage2_repair_core import pwc_verdict  # noqa: E402

REF_DIR = os.path.join(os.path.dirname(__file__), "..", "reference_results")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
COLUMN_STATES = ((-1, -1), (-1, 0), (0, -1), (0, 0))


def chain(length):
    obj = set(SEED)
    for k in range(1, length - 1):
        obj |= shift(SEED, (0, 0, k))
    return frozenset(obj)


def canonical(repair):
    return tuple(sorted(tuple(v) for v in repair))


def load_reference(length):
    path = os.path.join(REF_DIR, f"chain_L{length}_base_M0_reference.json")
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    rows = data.get("M0", data.get("base"))
    if rows is None:
        raise KeyError(f"{path} contains neither 'M0' nor legacy 'base'")
    return {canonical(row) for row in rows}


def walk_family(length):
    repairs = set()
    for states in itertools.product(COLUMN_STATES, repeat=length):
        diagonal_jump = any(
            states[i][0] != states[i + 1][0]
            and states[i][1] != states[i + 1][1]
            for i in range(length - 1)
        )
        if not diagonal_jump:
            repairs.add(canonical(
                (states[i][0], states[i][1], i - 1) for i in range(length)
            ))
    return repairs


def exhaustive_winners_through(length, max_size):
    initial = chain(length)
    universe, _ = universe_for(initial)
    winners = []
    first_size = None
    for size in range(max_size + 1):
        current = []
        for combo in itertools.combinations(sorted(universe), size):
            if pwc_verdict(initial.symmetric_difference(combo)):
                current.append(canonical(combo))
        if current:
            first_size, winners = size, current
            break
    return len(universe), first_size, set(winners)


def verify_generated(length):
    initial = chain(length)
    generated = walk_family(length)
    frozen = load_reference(length)
    expected = 4 * 3 ** (length - 1)
    oracle_pass = sum(
        pwc_verdict(initial.symmetric_difference(repair)) for repair in generated
    )
    if len(generated) != expected:
        raise AssertionError(f"L={length}: generated {len(generated)}, expected {expected}")
    if generated != frozen:
        raise AssertionError(
            f"L={length}: generated/frozen mismatch "
            f"({len(generated-frozen)} extra, {len(frozen-generated)} missing)"
        )
    if oracle_pass != expected:
        raise AssertionError(f"L={length}: only {oracle_pass}/{expected} pass PWC")
    return generated, oracle_pass


if __name__ == "__main__":
    results = []

    u3, m3, exhaustive3 = exhaustive_winners_through(3, 3)
    generated3, pass3 = verify_generated(3)
    if m3 != 3 or exhaustive3 != generated3:
        raise AssertionError("L=3 exhaustive M0 does not equal the walk family")
    print(f"L=3: |U|={u3}, m0=3, |M0|={len(generated3)}, "
          f"fresh exhaustive equality=PASS, PWC={pass3}/{len(generated3)}")
    results.append({"L": 3, "universe_size": u3, "m0": 3,
                    "M0_size": len(generated3), "reference_equality": True,
                    "pwc_pass": pass3, "method": "fresh_exhaustive"})

    u4, smaller4, _ = exhaustive_winners_through(4, 3)
    if smaller4 is not None:
        raise AssertionError(f"L=4 unexpectedly has a repair of size {smaller4}")
    generated4, pass4 = verify_generated(4)
    print(f"L=4: |U|={u4}, sizes<4 exhaustive exclusion=PASS, m0=4, "
          f"|M0|={len(generated4)}, reference equality=PASS, "
          f"PWC={pass4}/{len(generated4)}")
    results.append({"L": 4, "universe_size": u4, "m0": 4,
                    "M0_size": len(generated4), "reference_equality": True,
                    "pwc_pass": pass4,
                    "method": "lower_sizes_exhaustive_plus_walk_generation"})

    generated5, pass5 = verify_generated(5)
    print(f"L=5: m0=5 (walk characterization), |M0|={len(generated5)}, "
          f"reference equality=PASS, PWC={pass5}/{len(generated5)}")
    results.append({"L": 5, "m0": 5, "M0_size": len(generated5),
                    "reference_equality": True, "pwc_pass": pass5,
                    "method": "walk_generation_plus_frozen_exact_equality"})

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "walk_counts_result.json"), "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print("Saved outputs/walk_counts_result.json")
