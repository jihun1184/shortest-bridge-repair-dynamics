# D7D2-A4-L1a — Fixed remainder and finite template table

> **Subsequent status:** A4-L1b now proves the formal all-k geometry from
> this frozen table. This does not change the finite scope of the A4-L1a
> certification itself; semantic realization remains open in A4-L2.

## Claim certified here

For each of the 53 exact behavioral keys common to the fully enumerated
closures at `k=6,7,8`, let `R_C(k)` be its canonical minimum-size
representative and let `S_C(k)` be the 6-connected component containing
the satellite `s_k=(-k,2,0)`. Define

\[
G_C(k)=R_C(k)\setminus S_C(k).
\]

Direct coordinate comparison gives

\[
\boxed{G_C(6)=G_C(7)=G_C(8)\quad\text{for all 53 classes }C.}
\]

Thus a fixed remainder `G_C` exists for every computed class. This is an
exact finite certificate, not an inference from equal cardinalities.

## Audit method and result

The audit rebuilt all closures and behavioral keys from source, selected
canonical representatives by `(number of voxels, lexicographic coordinate
list)`, removed the satellite component, and compared the remaining
voxel sets exactly.

```text
k=6:  9,524 states, 53 classes
k=7: 21,963 states, 53 classes
k=8: 45,939 states, 53 classes

fixed-remainder consistent classes: 53/53
fixed-remainder failures:             0
common satellite templates:          18
classes with a common template:      53/53
component reconstruction failures:    0
templates compatible per class:       exactly 1 for every class
```

For every stored witness, the audit also reconstructed the entire
satellite component as the ordinary set union

\[
(s_k+A)\ \cup\
\{a_k+j e_x:0\le j\le\ell_k\}\ \cup\
(e_k+B),
\]

where `a_k=s_k+d`, `e_k=a_k+ell_k e_x`, and `ell_k>=0`. Exact equality
with the original satellite component was checked voxel by voxel.

## The 18 witnessed signatures

Coordinates in `A` are relative to the satellite. Coordinates in `B`
are relative to the closed corridor endpoint. `n` is the number of the
53 classes assigned to the template.

```text
T01 d=(0,-3,-1) A={(0,-3,-1),(0,-3,0),(0,-2,0),(0,-1,0),(0,0,0)}
    B={(1,0,0)}                                                        n=5
T02 d=(0,-3,-1) A={(0,-3,-1),(0,-3,0),(0,-2,0),(0,-1,0),(0,0,0)}
    B={(1,0,0),(2,0,0),(3,0,0),(3,0,1),(3,1,0),(3,1,1),(3,2,0),
       (3,3,0),(4,0,0),(4,0,1),(4,3,0)}                               n=1
T03 d=(0,-3,-1) A={(0,-3,-1),(0,-3,0),(0,-2,0),(0,-1,0),(0,0,0)}
    B={(1,0,0),(2,0,0),(3,0,0),(3,0,1),(3,1,0),(3,1,1),(4,0,0),
       (4,0,1)}                                                        n=2
T04 d=(0,-3,0)  A={(0,-3,0),(0,-2,0),(0,-1,0),(0,0,0)}
    B={(1,0,-1),(1,0,0)}                                              n=3
T05 d=(0,-1,0)  A={(0,-1,0),(0,0,0)} B={}                             n=5
T06 d=(0,-1,0)  A={(0,-1,0),(0,0,0)}
    B={(0,-2,-1),(0,-2,0),(0,-1,0),(1,-2,-1)}                         n=2
T07 d=(0,-1,0)  A={(0,-1,0),(0,0,0)}
    B={(0,-2,-1),(0,-2,0),(0,-1,0),(1,-2,-1),(2,-2,-1),(3,-2,-1),
       (3,-2,0),(3,-1,-1),(3,-1,0),(3,0,-1),(3,1,-1),(4,-2,-1),
       (4,-2,0),(4,1,-1)}                                             n=1
T08 d=(0,-1,0)  A={(0,-1,0),(0,0,0)}
    B={(0,-2,-1),(0,-2,0),(0,-1,0),(1,-2,-1),(2,-2,-1),(3,-2,-1),
       (3,-2,0),(3,-1,-1),(3,-1,0),(4,-2,-1),(4,-2,0)}                n=1
T09 d=(0,-1,0)  A={(0,-1,0),(0,0,0)}
    B={(0,-1,-1),(0,-1,0),(1,-2,-1),(1,-1,-1)}                        n=1
T10 d=(0,-1,0)  A={(0,-1,0),(0,0,0)}
    B={(0,0,-1),(1,-2,-1),(1,-1,-1),(1,0,-1),(1,1,-1),(2,1,-1),
       (3,1,-1),(4,1,-1)}                                             n=1
T11 d=(0,-1,0)  A={(0,-1,0),(0,0,0)}
    B={(0,0,-1),(1,0,-1),(2,0,-1),(3,-2,-1),(3,-2,0),(3,-1,-1),
       (3,-1,0),(3,0,-1),(3,1,-1),(4,-2,-1),(4,-2,0),(4,1,-1)}       n=1
T12 d=(0,0,0)   A={(0,0,0)} B={}                                      n=22
T13 d=(0,0,0)   A={(0,0,0)}
    B={(0,-3,-1),(0,-3,0),(0,-2,0),(0,-1,0),(1,-3,-1)}                n=1
T14 d=(0,0,0)   A={(0,0,0)}
    B={(0,-3,-1),(0,-2,-1),(0,-1,-1),(0,0,-1),(1,-3,-1),(2,-3,-1),
       (3,-3,-1)}                                                      n=1
T15 d=(0,0,0)   A={(0,0,0)} B={(0,-1,0)}                              n=2
T16 d=(0,0,0)   A={(0,0,0)}
    B={(0,-1,0),(0,0,-1),(1,0,-1),(2,0,-1),(3,0,-1),(4,0,-1)}        n=2
T17 d=(0,0,0)   A={(0,0,0)}
    B={(0,-1,0),(1,0,0),(2,0,-1),(2,0,0),(3,0,-1),(4,0,-1)}          n=1
T18 d=(0,0,0)   A={(0,0,0)}
    B={(0,-1,0),(1,0,0),(2,0,0),(3,0,-1),(3,0,0),(4,0,-1)}           n=1
```

The class IDs, deterministic behavioral-key SHA256 values, exact fixed
remainders, unique template assignments, and the k-specific corridor
start/endpoint/length witnesses are stored in
`a4_l1a_signature_table_results.json`.

## A4-L1 proof skeleton and claim boundary

### A4-L1a — Fixed remainder

The displayed equality of `G_C(k)` is **CERTIFIED for k=6,7,8**. An
all-k theorem still requires a construction or inductive invariant; the
finite audit alone does not quantify over `k>8`.

### A4-L1b — Geometric parametric family

For a table entry `sigma=(d,A,B)`, define `a_k=s_k+d`, choose a
nonnegative integer `ell_sigma(k)`, put

\[
L_\sigma(k)=\{a_k+j e_x:0\le j\le\ell_\sigma(k)\},
\qquad e_k=a_k+\ell_\sigma(k)e_x,
\]

and define the formal satellite geometry

\[
S_\sigma(k)=(s_k+A)\cup L_\sigma(k)\cup(e_k+B).
\]

The audit certifies that this formula reconstructs all 159 computed
class/k satellite components. It defines voxel sets for other k, but by
itself does not prove that those sets are reachable from `X_k` or belong
to behavioral class `C`.

### A4-L1c — Degenerate corridor convention

The corridor is a closed lattice segment with `ell_sigma(k)>=0`.
Therefore `ell_sigma(k)=0` is valid and gives `L_sigma(k)={a_k}`.
Attachment, corridor, and patch may overlap; every displayed combination
is ordinary set union, not disjoint union. This convention absorbs the
k=6 endpoint/elbow coincidence found in A4.3B.

### Remaining semantic obligation

Reachability and class membership for the formal representatives at
`k>8` are **OPEN**. They belong to the transition-semantic step A4-L2,
not to the finite geometric certification above. A4-L3 must then prove
both persistence and exhaustiveness before any all-k quotient claim.

## Reproduction

From the checkpoint root, run:

```bash
python d7d1_rank_classification_freeze/a4_l1a_signature_table_audit.py
```

The script writes `a4_l1a_signature_table_results.json`.
