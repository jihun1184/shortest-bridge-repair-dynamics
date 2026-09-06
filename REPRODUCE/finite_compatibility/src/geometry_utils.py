"""
geometry_utils.py

Small geometry helpers used throughout this package: the 20-cell
vertex/edge neighborhood N(v) of a voxel, pairwise displacement
classification, translation, and the two canonical chain seeds.
"""
from itertools import product


def N(v):
    result = set()
    # dim-0 cells: vertices g=2p with p_i in {v_i, v_i+1}
    for offs in product([0, 1], repeat=3):
        p = tuple(v[i] + offs[i] for i in range(3))
        result.add(tuple(2 * x for x in p))
    # dim-1 cells: for each free axis a, c_a=2*v[a]+1 fixed;
    # other two axes even, 2 choices each
    for a in range(3):
        other_axes = [i for i in range(3) if i != a]
        for offs in product([0, 1], repeat=2):
            g = [0, 0, 0]
            g[a] = 2 * v[a] + 1
            for idx, ax in enumerate(other_axes):
                g[ax] = 2 * (v[ax] + offs[idx])
            result.add(tuple(g))
    return result


def geom_type(u, w):
    d = tuple(u[i] - w[i] for i in range(3))
    cheb = max(abs(x) for x in d)
    if cheb != 1:
        return "OUT_OF_RANGE", d
    zeros = sum(1 for x in d if x == 0)
    if zeros == 2:
        return "face", d
    if zeros == 1:
        return "edge", d
    return "corner", d


def column(px, py, z_lo=-1, z_hi=0):
    return frozenset((px, py, z) for z in range(z_lo, z_hi + 1))


def shift(vs, d):
    return frozenset((x + d[0], y + d[1], z + d[2]) for (x, y, z) in vs)


SEED = frozenset([(-1, -1, -1), (-1, -1, 0), (0, 0, -1), (0, 0, 0)])
SEED2 = frozenset([(-1, 0, -1), (-1, 0, 0), (0, -1, -1), (0, -1, 0)])
