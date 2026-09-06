import time
from itertools import product, combinations
from pcm_check import (
    voxel_to_cell, dim, is_face, closure, build_complex,
    strictly_comparable, theta_prime, is_surface, is_pwc, border_of,
    connected_components,
)

RANK = 3
_pwc_verdict_cache = {}

def candidate_voxels(cell):
    opts = []
    for c in cell:
        if c % 2 == 1:
            opts.append([(c - 1) // 2])
        else:
            opts.append([c // 2 - 1, c // 2])
    return set(product(*opts))


def cofaces_of_dim(h, target_dim):
    assert dim(h) == 0, "cofaces_of_dim is only implemented for vertex h"
    n = len(h)
    result = set()
    for axes in combinations(range(n), target_dim):
        for signs in product([-1, 1], repeat=target_dim):
            x = list(h)
            for axis, sign in zip(axes, signs):
                x[axis] = h[axis] + sign
            result.add(tuple(x))
    return result


def geometric_cofaces_12(h):
    return cofaces_of_dim(h, 1) | cofaces_of_dim(h, 2)


# ---------------------------------------------------------------------
# is_pwc / LocalOK oracle wrappers. `pwc_verdict` is cached by
# frozenset(voxels) -- correctness-neutral (same voxel set always maps
# to the same verdict), purely a performance fix for repeated X0
# lookups. NOT used to short-circuit or share logic between the
# direct and certified paths for Z, which remain independently
# computed as before.
# ---------------------------------------------------------------------

def pwc_verdict(voxels):
    key = frozenset(voxels)
    if key in _pwc_verdict_cache:
        return _pwc_verdict_cache[key]
    _, all_cells = build_complex(voxels)
    verdict, _details = is_pwc(all_cells, RANK)
    _pwc_verdict_cache[key] = verdict
    return verdict


def local_ok(h, delta):
    if h not in delta:
        return True
    return is_surface(theta_prime(delta, h), RANK - 2)


def failure_type_at(h, delta):
    if h not in delta:
        return None
    nb = theta_prime(delta, h)
    if not is_surface(nb, RANK - 2):
        comps = connected_components(nb)
        if len(comps) > 1:
            return "theta_disconnected"
        return "theta_not_surface_recursive"
    return None


# ---------------------------------------------------------------------
# Defect witness record (built from Y = X0 xor D, the broken state)
# ---------------------------------------------------------------------

class DefectWitness:
    def __init__(self, h, Y_voxels):
        self.h = h
        self.dimension = dim(h)
        _, all_cells = build_complex(Y_voxels)
        self.all_cells = all_cells
        self.delta = border_of(all_cells, RANK)
        self.failure_type = failure_type_at(h, self.delta)
        self.theta = theta_prime(self.delta, h)
        self.theta_components = connected_components(self.theta) if self.theta else []

    def restricted_universe(self):
        u = set(candidate_voxels(self.h))
        for x in self.theta:
            u |= candidate_voxels(x)
        return u

    def full_universe(self):
        u = set(candidate_voxels(self.h))
        for x in geometric_cofaces_12(self.h):
            u |= candidate_voxels(x)
        return u


# ---------------------------------------------------------------------
# Repair problem: explicit X0 / D / Y / R / Z state model
# ---------------------------------------------------------------------

def sym_diff(a, b):
    return set(a).symmetric_difference(set(b))


class RepairProblem:
    def __init__(self, X0_voxels, D_voxels):
        self.X0 = set(X0_voxels)
        verdict = pwc_verdict(self.X0)
        assert verdict, "RepairProblem precondition PWC(X0) failed -- not a valid baseline"
        self.D = set(D_voxels)
        self.Y = sym_diff(self.X0, self.D)

    def witness_at(self, h):
        return DefectWitness(h, self.Y)

    def apply_repair(self, R_voxels):
        R = set(R_voxels)
        Z = sym_diff(self.Y, R)
        E_total = sym_diff(self.D, R)   # == X0 xor Z
        return Z, E_total


def A_E(batch_voxels):
    s = set()
    for v in batch_voxels:
        s |= closure(voxel_to_cell(v))
    return s


def certification_pass(X0_voxels, Z_voxels, E_total_voxels):
    verdict_x0 = pwc_verdict(X0_voxels)
    assert verdict_x0, "certification_pass precondition PWC(X0) failed"
    _, all_cells_z = build_complex(Z_voxels)
    delta_z = border_of(all_cells_z, RANK)
    ae = A_E(E_total_voxels)
    domain = all_cells_z & ae
    return all(local_ok(h, delta_z) for h in domain)


def target_local_ok(h, Z_voxels):
    _, all_cells = build_complex(Z_voxels)
    delta = border_of(all_cells, RANK)
    return local_ok(h, delta)


def infer_action(v, base_voxels):
    return "remove" if v in base_voxels else "add"


# ---------------------------------------------------------------------
# Search: cardinality-ordered brute force over R subseteq universe.
# Tracks direct (ground-truth) and certified (theorem-based) verdicts
# independently, WITHIN the searched universe and size bound only --
# field names say so explicitly.
# ---------------------------------------------------------------------

def search_minimal_repair(problem: RepairProblem, witness: DefectWitness, universe, max_size=3):
    t_start = time.time()
    universe = sorted(universe)
    h = witness.h
    restricted = witness.restricted_universe()

    record = {
        "witness": h,
        "universe_size": len(universe),
        "max_size_searched": max_size,
        "batches_examined": 0,
        "min_target_local_size": None,
        "min_target_local_batch": None,
        "min_direct_pwc_size_within_universe": None,
        "min_direct_pwc_batch_within_universe": None,
        "min_certified_pwc_size_within_universe": None,
        "min_certified_pwc_batch_within_universe": None,
        "oracle_disagreements": 0,
        "min_certified_used_voxel_outside_restricted_universe": None,
        "total_edit_size_from_certified_base": None,
        "elapsed_seconds": None,
    }

    for size in range(0, max_size + 1):
        for combo in combinations(universe, size):
            record["batches_examined"] += 1
            Z, E_total = problem.apply_repair(combo)
            if not Z:
                continue

            tgt_ok = target_local_ok(h, Z)
            if tgt_ok and record["min_target_local_size"] is None:
                record["min_target_local_size"] = size
                record["min_target_local_batch"] = combo

            direct_ok = pwc_verdict(Z)
            certified_ok = certification_pass(problem.X0, Z, E_total)
            if direct_ok != certified_ok:
                record["oracle_disagreements"] += 1

            if direct_ok and record["min_direct_pwc_size_within_universe"] is None:
                record["min_direct_pwc_size_within_universe"] = size
                record["min_direct_pwc_batch_within_universe"] = combo

            if certified_ok and record["min_certified_pwc_size_within_universe"] is None:
                record["min_certified_pwc_size_within_universe"] = size
                record["min_certified_pwc_batch_within_universe"] = combo
                record["min_certified_used_voxel_outside_restricted_universe"] = any(
                    v not in restricted for v in combo
                )
                record["total_edit_size_from_certified_base"] = len(E_total)

        if record["min_certified_pwc_size_within_universe"] is not None:
            break

    record["elapsed_seconds"] = round(time.time() - t_start, 3)
    return record


def classify_divergence(record):
    tgt = record["min_target_local_size"]
    cert = record["min_certified_pwc_size_within_universe"]
    return {
        "finite_size_divergence": (tgt is not None and cert is not None and tgt != cert),
        "feasibility_divergence_within_universe_and_bound": (tgt is not None and cert is None),
        "oracle_divergence": (record["oracle_disagreements"] > 0),
    }
