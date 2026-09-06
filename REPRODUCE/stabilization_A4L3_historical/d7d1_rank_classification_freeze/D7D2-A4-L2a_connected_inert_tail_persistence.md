# D7D2-A4-L2a(i) — Connected-satellite inert-tail persistence

## Status

**PROVED for the 31 non-T12 formal families.**

This note closes only the connected-satellite part of A4-L2a.  The 22
T12 families, in which the satellite remains an isolated component, are
still open.  A4-L2b root reachability and A4-L3 new-class exhaustiveness
are also still open.

## Setup

A4-L1b gives a formal family `R_C^*(k)` for every class label and every
`k>=6`.  Exactly 31 classes are non-T12: 30 have corridor law
`ell_C(k)=k-4`, and C050/T14 has `ell_C(k)=k-6`.  Their satellite is
already joined to a fixed core-facing component.

Use `k0=8` as the lifting base.  For a `k-4` class put `b_C=-5`; for
C050/T14 put `b_C=-6`.  Write `S_C(k)` for the satellite component and

```
F_C = {p in S_C(8) : p_x >= b_C}.
```

From the explicit A4-L1b formulas, for every `k>=8`:

1. `S_C(k) ∩ {x>=b_C} = F_C`;
2. every point of the symmetric difference `S_C(k) triangle S_C(8)` has
   x-coordinate at most `b_C-3`.

For the `k-4` families this is because the whole core-side corridor from
`x=-5` through the fixed endpoint `x=-4` is already present at `k=8`,
while the translated attachment and any newly inserted corridor voxels
are at `x<=-8`.  For C050/T14 the fixed endpoint is `x=-6` and the
`k=8`/`k>8` difference is at `x<=-9`.

## Finite base certificate at k=8

Starting independently from each of the 31 formal candidates
`R_C^*(8)`, `a4_l2a_connected_inert_tail_audit.py` enumerates its entire
N2 descendant closure.  Across the 31 closures it checks 2,869 distinct
(descendant-within-class-start) states and 4,035 N2 action edges.

For every audited state:

- the state is Q2/Q3-valid (`has_fail=False`);
- every generated action is N2-only;
- for every still-distinct component paired with the satellite-descendant
  component, every d6-minimizing endpoint on the satellite side lies in
  `x>=b_C`;
- every N2 addition lies in `x>=b_C`.

There are zero failures.

## Inert-tail lifting lemma

Fix one of the 31 classes and a state `Y` in the audited descendant
closure of `R_C^*(8)`.  Define `Psi_k(Y)` by replacing the original
satellite component `S_C(8)` by `S_C(k)` and leaving every later N2
addition unchanged.

We prove by induction over descendant depth that, for all `k>=8`,
`Psi_k` is a rho-labeled transition-graph isomorphism from the descendant
closure of `R_C^*(8)` to that of `R_C^*(k)`.

### Components and root labels

All non-satellite starting voxels lie at `x>=-4`, and the finite base
audit shows that every later addition lies in `x>=b_C`.  The moving tail
is connected to the same fixed front `F_C` and cannot contact another
component through the remote symmetric-difference region.  Hence current
components correspond one-for-one under `Psi_k`.  Under the natural
identification of the moving singleton root identity `s_8` with `s_k`,
the root-identity partition is unchanged.

### Shortest endpoint pairs

Pairs not involving the satellite-descendant component are literally
unchanged geometrically.  For a pair that does involve it, the base audit
certifies that every minimizing satellite-side endpoint lies in the fixed
front `x>=b_C`.

The only satellite-component points changed when `k` grows are either:

- translated attachment points, whose x-coordinate moves strictly farther
  left while y,z stay fixed; or
- newly inserted leftward corridor points, each farther from every
  fixed-region point than a corridor point with the same y,z already
  present at `k=8`.

Thus a non-minimizing remote point at `k=8` cannot become a new minimizing
endpoint at larger `k`, while all old minimizing endpoints remain.
Therefore the complete set of d6-minimizing endpoint pairs is identical.

### N2 actions and compatibility

Because the minimizing endpoint pairs are identical, the same monotone
shortest paths are considered.  Every such path stays in `x>=b_C`, where
`Y` and `Psi_k(Y)` agree, so its addition set is identical.

The Q2/Q3 validity predicate is local: every failure witness is contained
in voxels that pairwise Chebyshev-touch.  The changing tail lies at least
three x-layers to the left of the active action region.  It therefore
cannot participate in a failure witness created by an active-region
bridge.  The only local patterns that change inside the remote tail are a
translated copy of the fixed attachment/corridor-start pattern and extra
straight-corridor interior; these are the same valid local patterns
already present at the base.  Hence a candidate bridge is compatible for
`Y` iff it is compatible for `Psi_k(Y)`.

So the N2 addition sets correspond exactly.

### rho labels and induction

The corresponding action merges the same current root-identity blocks,
so its absorption size `rho` is unchanged.  Also

```
Psi_k(Y union A) = Psi_k(Y) union A
```

for the common addition set `A`.  The successor is therefore the image of
the base successor, and the induction closes.

Consequently the full rho-labeled descendant semantics of the formal
candidate is independent of `k` for every `k>=8`.  Since A4-L1a/A3.2
already certify that the same frozen behavioral class is realized by the
formal representative at `k=6,7,8`, behavioral persistence holds for all
`k>=6` for these 31 classes.

## Independent first-unseen-level regression

As a check on the proof rather than its basis, the audit computes the
exact three-round behavioral key `c_3` directly from each formal
`R_C^*(9)` descendant semantics and compares its deterministic SHA256 to
the frozen A4-L1a class key.

Result: **31/31 exact SHA matches at k=9.**

## Remaining A4-L2a problem: the 22 T12 classes

The T12 families are genuinely different: `R_C^*(k)=G_C union {s_k}`
with an isolated moving satellite.  Their raw descendant closures can grow
with `k`, even though the exact behavioral key appears stable.

There is, however, an important simplification.  For a fixed component
`H subset {x>=-4}` and `t in H`,

```
d1(s_k,t) = k + (t_x + |t_y-2| + |t_z|).
```

Therefore the set of d6-minimizing target endpoints in `H` is independent
of `k`.  Moreover, the prefix of a shortest monotone bridge lying at
`x<=-6` cannot Chebyshev-touch the fixed background at `x>=-4`; bridge
compatibility can only depend on a bounded core-side suffix plus the
self-valid monotone-path geometry.

The next target is therefore a **parametric bridge-quotient lemma** for
these isolated-satellite actions: show that inserting additional remote
+x steps changes raw bridge realizations but not the set of rho-labeled
behavioral successor classes.  Fixed-fixed actions are already
k-independent and simply descend to lower-component-count T12 classes, so
this lemma can be combined with induction on component count.

## Claim boundary

Closed here:

- A4-L2a(i), 31 connected-satellite classes: **PROVED**.

Still open:

- A4-L2a(ii), 22 T12 isolated-satellite classes;
- A4-L2b parametric root reachability;
- A4-L3 persistence + no-new-class exhaustiveness;
- `Q_k ~= Q_6` for all `k>=6` and the all-k persistent-rank conclusion.
