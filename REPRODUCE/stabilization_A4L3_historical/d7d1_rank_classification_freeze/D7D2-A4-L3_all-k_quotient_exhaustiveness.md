# D7D2-A4-L3 — All-k quotient exhaustiveness

## Theorem

For every integer `k>=6`, the exact rho-labeled behavioral quotient of
the N2-reachable closure of `X_k` has the same 53 canonical keys as at
`k=6`. Under the natural identification of the five root-component
identities,

\[
Q_k \cong Q_6,\qquad |Q_k|=53.
\]

Consequently,

\[
R^*(X_k)=3\qquad(k\ge 6).
\]

The proof is at behavioral-key level. It does not assert a total raw-state
contraction `Reach(X_k) -> Reach(X_9)`.

## 1. The finite base is the full `k=9` root closure

Let `T_9` be the set of the 22 formal T12 states at `k=9`, and let
`Desc(T_9)` denote their union descendant closure.

The formal state `C053` is exactly `X_9`, and `C053 in T_9`. Therefore

\[
\operatorname{Reach}(X_9)\subseteq \operatorname{Desc}(T_9).
\]

A4-L2b proves that every one of the 22 T12 formal states is reachable
from `X_9`. Descendants of reachable states are reachable, so

\[
\operatorname{Desc}(T_9)\subseteq \operatorname{Reach}(X_9).
\]

Hence the union closure already enumerated for A4-L2a(ii) is not merely a
collection of local test closures:

\[
\boxed{\operatorname{Desc}(T_9)=\operatorname{Reach}(X_9).}
\]

The strengthened finite audit reconstructs this closure from source. It
contains 87,517 states and 148,722 N2 action edges. Exact refinement is
stable from `c_3` to `c_4`. Its key set contains exactly 53 elements and
equals the frozen 53-key set. More specifically, the 737 states in which
the satellite remains isolated realize exactly the 22 frozen T12 keys,
whereas the 86,780 connected-satellite states realize exactly the other
31 frozen keys.

Thus

\[
Q_9=Q_6.
\]

## 2. Arbitrary-State Front Normalization Lemma

For every `k>=9` and every `Y in Reach(X_k)`, there exists a state
`N_k(Y) in Reach(X_9)` with the same exact rho-labeled behavioral key.

### Case 1: the satellite is still isolated

Choose a reachability history from `X_k` to `Y`. If the satellite root
component is still isolated at `Y`, no earlier action in the history can
have absorbed it, because N2 transitions only merge components. Every
earlier action is therefore fixed-fixed. The state has the form

\[
Y=I\cup\{s_k\},
\]

where `I subset {x>=-4}` is one of the 737 fixed backgrounds. The same
fixed-fixed action history produces `I union {s_9}` from `X_9`.

A4-L2a(ii)'s component-count induction proves that the complete recursive
behavioral key of `I union {s_k}` is independent of `k`. Set

\[
N_k(Y)=I\cup\{s_9\}.
\]

### Case 2: the satellite has been absorbed

In the chosen history, take the first satellite-absorbing action. Its
parent is `I union {s_k}` for one of the same 737 backgrounds. Write its
shortest monotone bridge as a signed coordinate word `w`.

Delete the first `k-9` occurrences of `+x`. A4-L2a(ii)'s path-word
reduction produces a compatible shortest bridge from `s_9` to the same
fixed endpoint, with the same absorption label and the same lift front
in `x>=-8`. Let `Z_k` and `Z_9` be the corresponding connected
successors.

The connected-successor lifting part of A4-L2a(ii) gives a rho-labeled
transition-graph isomorphism between the full descendant closures of
`Z_k` and `Z_9`. Applying that isomorphism to the remaining suffix of the
chosen history yields a state `N_k(Y)` below `Z_9` with exactly the same
behavioral key as `Y`.

Both cases give

\[
Q_k\subseteq Q_9\qquad(k\ge9).
\]

The normalization is existential and may depend on a chosen reachability
history. This is sufficient for quotient exhaustiveness and avoids the
known failure of a total geometric thin-tail contraction on raw states.

## 3. Quotient equality and rank

D7D2-A3.2 gives `Q_6=Q_7=Q_8`. Section 1 gives `Q_9=Q_6`, and Section 2
gives `Q_k subseteq Q_9` for every `k>=9`. A4-L2a together with A4-L2b
already proves persistence of every frozen key, namely

\[
Q_6\subseteq Q_k\qquad(k\ge6).
\]

Combining the inclusions proves `Q_k=Q_6` for all `k>=6`.

Every frozen class has outgoing absorption size in `{0,2,3}`, so
exhaustiveness gives `R^*(X_k)<=3`. A4-L2b makes a frozen rho-3 witness
reachable for every `k>=6`, giving the reverse inequality. Therefore
`R^*(X_k)=3`.

## 4. Reproducible certificate

Run from the checkpoint root:

```bash
python d7d1_rank_classification_freeze/a4_l3_exhaustiveness_assembly_audit.py
```

The audit verifies the two closure inclusions' finite premises, rebuilds
the complete `k=9` closure, checks `c_3 -> c_4` partition stability, and
compares all observed keys with the frozen 22+31 split. The universal
step is the proved path-word reduction and connected-descendant lifting
in `D7D2-A4-L2a_T12_bridge_quotient_persistence.md`.

## ELI5 intuition

Imagine a toy city joined to a distant satellite by roads. Moving the
satellite farther left only adds boring straight road far away from the
city. Before the satellite joins the city, we can erase the extra early
straight steps and obtain the `k=9` route. After it joins, every later
choice happens near the unchanged city-facing end, so the same choices
remain available. Every far-away construction therefore has a `k=9`
version with the same future behavior, even though there need not be one
single geometric eraser that works on every raw voxel set.

