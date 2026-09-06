# Root-Layer Shortcut Theorem for the Remaining 28 D7D1 Roots

## Statement

Let \(Y\) be any of the 28 N1-successor roots belonging to the 14 previously
uncomputed D7B depth-three orbits
(302, 316, 318, 320, 322, 329, 331, 333, 335, 337, 342, 344, 345, 347).
Then

\[
\boxed{R^*(Y) = 4}
\]

without enumerating the full N2-reachable closure of \(Y\).

## Ingredients

1. **Component monotonicity of N2 actions** (already established, D7D0
   Lemma D7D0.2): every \(\Delta\in A_{N2}(Z)\) strictly decreases
   \(|\operatorname{Comp}_6(Z)|\).

2. **Rank is bounded by current component count.** By construction,
   \(\rho_Z(\Delta)\) is the size of the absorption block, i.e. the number of
   root-identity partition blocks of \(Z\) merged by \(\Delta\). A partition of
   the root's five identities into blocks assigned to \(Z\)'s current
   components can merge at most \(|\operatorname{Comp}_6(Z)|\) blocks in one
   action, so
   \[
   \rho_Z(\Delta) \le |\operatorname{Comp}_6(Z)|.
   \]

3. **Root-layer realization.** Every root \(Y\) has
   \(|\operatorname{Comp}_6(Y)| = 5\) by the frozen D7B/D7D1 construction.
   Direct enumeration of \(A_{N2}(Y)\) — i.e. only the actions available at
   \(Y\) itself, not the full descendant closure — found at least one action
   with \(\rho_Y(\Delta) = 4\) for **all 28** roots.

## Proof that \(R^*(Y) = 4\)

- **Lower bound.** The root-layer enumeration exhibits an action with
  \(\rho = 4\) at \(Y\) itself, so \(R^*(Y) \ge 4\).
- **Upper bound.** For any \(Z \in \mathrm{Reach}_{N2}(Y)\) with \(Z \ne Y\),
  \(Z\) was reached by at least one N2 action from \(Y\), so by ingredient 1,
  \(|\operatorname{Comp}_6(Z)| \le 4\). By ingredient 2, every action available
  at such a \(Z\) has \(\rho_Z(\Delta) \le |\operatorname{Comp}_6(Z)| \le 4\).
  Combined with the root layer itself (\(\rho_Y(\Delta)\le 4\), confirmed by
  direct enumeration — no root-layer action exceeded 4), every reachable state
  in the entire closure has all actions bounded by 4. Hence \(R^*(Y) \le 4\).

Therefore \(R^*(Y) = 4\) exactly, established from:

- the already-proved D7D0 component-monotonicity lemma (no new assumption),
- a partition-counting bound on \(\rho\) (structural, not empirical),
- one shallow (depth-0) enumeration per root, not the full closure.

## What this does **not** establish

- It does not produce the full voxel-state closure size, transition count, or
  SHA-256 digest for these 28 roots. Those quantities remain uncomputed and
  are **not** claimed here.
- It does not change the classification of any of the 234 already-completed
  roots.
- It is specific to roots with exactly 5 initial components; it is not a
  general \(m\)-component argument and does not by itself yield a growing
  family (that is the explicit target of D7D2).

## Independent re-verification performed in this session

The root-layer enumeration was executed directly against the frozen D7D0/D7D1
source (`atomic_actions`, `components6`, `has_fail`, and
`root_identity_partition` from `c07d7d1_persistent_absorption_closure.py`),
not against any cached or hand-computed table. Result:

```text
roots checked                         28
aggregate root-layer N2 actions       25,528
rho histogram                         {2: 9058, 3: 10822, 4: 5648}
roots with root-layer max_rho < 4      0
roots with root-layer max_rho == 4    28
```

This matches the counts reported in conversation and is reproduced by
`verify_shortcut.py` in this package.
