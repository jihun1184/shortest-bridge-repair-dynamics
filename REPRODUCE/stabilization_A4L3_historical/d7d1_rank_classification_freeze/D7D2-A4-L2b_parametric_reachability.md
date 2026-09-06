# D7D2-A4-L2b — Parametric reachability of all 53 formal families

## Status

**PROVED.** For every frozen class label `C` and every integer `k>=6`, the
formal A4-L1b candidate `R_C^*(k)` is reachable from the frozen root

\[
X_k=\mathrm{CORE}\cup\{(-1,-1,0)\}\cup\{s_k\},
\qquad s_k=(-k,2,0),
\]

by a finite sequence of compatible N2 shortest-bridge actions.

This closes the existence half only. It does **not** prove that every
reachable state belongs to one of these 53 classes. Therefore A4-L3
exhaustiveness and the all-k equality `Q_k ~= Q_6` remain open.

## 1. Finite reachability skeleton

A target-restricted exact N2 search was run from `X_6` and, independently,
from the first unseen level `X_9`. For each of the 53 formal targets the
search only retains an action if its complete addition set is contained in
that exact target. The resulting schedules have the same depth histogram:

```text
N2 depth 0 :  1 class
N2 depth 1 : 27 classes
N2 depth 2 : 24 classes
N2 depth 3 :  1 class
```

The union of the selected schedules has a particularly small form. There
are 54 nodes — the 53 formal candidates plus one auxiliary connected node
`U(k)` — and exactly 53 directed edges. Hence the witness graph is a rooted
tree with root `C053`, and `R_C053^*(k)=X_k`.

The edges split into four structural types:

```text
root -> fixed-region successor                  16
root -> satellite-absorbing parametric successor 12
non-root fixed addition                          24
auxiliary U -> C006 fixed addition                1
                                                ---
                                                 53
```

Among the 24 non-root fixed edges, 5 have a T12 isolated-satellite parent
and 19 have a connected-satellite parent.

The machine-readable 53-edge table is stored in
`a4_l2b_parametric_reachability_results.json`.

## 2. The 16 root-fixed edges

For these edges both endpoint components and the selected monotone bridge
lie entirely in the fixed region `x>=-4`. The satellite `s_k` is an
additional isolated component lying at `x<=-6` and therefore neither
changes those fixed components nor their mutual d6 distance.

The chosen bridge at `k=6` is a compatible shortest bridge between the
same two fixed components for every `k>=6`. Its addition set is literally
k-independent, and direct substitution into the A4-L1b formulas gives the
corresponding child formal candidate. Thus all 16 root-fixed edges lift
unchanged to every k.

## 3. The 12 root-satellite parametric edges

These are the only edges whose raw addition set grows with k. Each starts
at the singleton satellite component and ends at one of the same three
fixed minimizing endpoints

\[
(-4,1,0),\qquad (-3,-1,-1),\qquad (0,2,-1).
\]

For a fixed target component `H` and `t in H`,

\[
d_1(s_k,t)=k+\bigl(t_x+|t_y-2|+|t_z|\bigr).
\]

The additive `k` is common to all target candidates in `H`. Hence a target
endpoint minimizing at the finite base remains minimizing for every k.

More strongly, each selected path has one explicit word family

\[
w_e(k)=u_e\,(+x)^{k-6}\,v_e,
\]

starting at `s_k`. The 12 finite `(u_e,v_e)` rows are:

| child | fixed endpoint | `u_e` | `v_e` |
|---|---|---|---|
| C015 | `(-3,-1,-1)` | empty | `+x,+x,-y,-y,-y,-z,+x` |
| C016 | `(0,2,-1)` | empty | `+x,+x,+x,+x,+x,-z,+x` |
| C017 | `(0,2,-1)` | empty | `+x,+x,-z,+x,+x,+x,+x` |
| C029 | `(-3,-1,-1)` | `-y` | `+x,+x,-y,-y,-z,+x` |
| C030 | `(-3,-1,-1)` | `-y` | `+x,+x,-y,-z,+x,-y` |
| C031 | `(0,2,-1)` | empty | `+x,+x,+x,+x,-z,+x,+x` |
| C048 | `(-4,1,0)` | empty | `+x,+x,-y` |
| C049 | `(-4,1,0)` | `-y` | `+x,+x` |
| C050 | `(-3,-1,-1)` | empty | `-z,-y,-y,-y,+x,+x,+x` |
| C051 | `(-3,-1,-1)` | `-y,-y,-y,-z` | `+x,+x,+x` |
| C052 | `(-3,-1,-1)` | `-y,-y,-y` | `+x,+x,+x,-z` |
| U | `(-3,-1,-1)` | `-y` | `+x,+x,-z,+x,-y,-y` |

At `k=6` the inserted block is empty. Increasing k shifts the starting
satellite left and inserts exactly the compensating number of `+x` steps,
so the endpoint is fixed and the word remains coordinate-wise monotone and
L1-shortest.

### Compatibility

For every row, the path intersection with the compatibility front
`{x>=-5}` is k-independent. All newly inserted or translated path voxels
lie in `x<=-6`, whereas the fixed root background lies in `x>=-4`.
A Q2/Q3 failure witness has Chebyshev diameter one, and a monotone path by
itself is Q2/Q3-valid by the previously proved finite-window monotone-path
lemma. Therefore the same locality argument used in A4-L2a(ii) applies:
bridge compatibility is determined by the fixed `x>=-5` front. Since the
base path is compatible, every `w_e(k)` is compatible.

For the 11 class children, direct substitution of the row into the frozen
A4-L1b `(G_C,d_C,A_C,B_C,ell_C)` formula gives exactly `R_C^*(k)`. The
remaining row defines the auxiliary family

\[
U(k)=X_k\cup w_U(k).
\]

Thus all 12 satellite-absorbing root edges exist for every `k>=6`.

## 4. The 24 non-root fixed edges

Every one of these edges has a k-independent bridge path and a
k-independent addition set. The target/source identity

\[
R_D^*(k)=R_C^*(k)\cup A_{C\to D}
\]

is a direct finite algebraic check of the A4-L1b formulas: the two families
have the same moving remote part, and differ only by the displayed fixed
addition.

There are two cases.

### 4.1 Five T12-parent edges

The satellite stays isolated in the parent. These actions join two fixed
components. A4-L2a(ii) already proved that fixed-fixed actions are
geometrically and semantically k-independent. Hence the same exact bridge
exists for every k.

### 4.2 Nineteen connected-parent edges

A4-L2a(i)'s inert-tail lifting lemma proved more than equality of class
keys: for every connected formal family, the complete set of minimizing
endpoint pairs and the exact N2 addition sets in the fixed front are
preserved under tail extension. Each selected tree edge is one such fixed
addition. Therefore it lifts unchanged to every larger k and lands on the
exact child formal candidate by the preceding source/target identity.

The finitely certified levels `k=6,7,8` are already reachable by their
closure provenance; the lifting statement supplies every later level.

## 5. The auxiliary edge `U -> C006`

The auxiliary state has three components. Its satellite-descendant
component contains the fixed point `(-3,1,-1)`. The selected bridge is

```text
(-3,1,-1)
(-3,2,-1)
(-2,2,-1)
(-1,2,-1)
( 0,2,-1)
```

ending at the fixed singleton component `(0,2,-1)`. The three interior
voxels are the k-independent addition set.

The only k-dependent points of `U(k)` move or extend farther to the left.
They therefore cannot beat the fixed minimizing endpoint `(-3,1,-1)` in
L1 distance to `(0,2,-1)`. The same path stays shortest for every k. Its
successor is exactly `R_C006^*(k)`, which is Q2/Q3-valid by A4-L2a(i), so
the action is compatible for all k.

## 6. Tree induction

`C053` is the root itself. Every other node of the 54-node skeleton has a
unique parent, and Sections 2--5 prove that the corresponding tree edge is
an admissible N2 action for every k in its stated range. Induction on tree
depth therefore gives

\[
X_k\leadsto R_C^*(k)
\qquad\text{for every class }C\text{ and every }k\ge6.
\]

This proves A4-L2b. `square`

## 7. Exact audit and regression

`a4_l2b_parametric_reachability_audit.py` independently reconstructs the
witness tree at `k=6` and `k=9` from the frozen operational semantics. It
then recovers one exact certificate/path realization for every tree edge,
infers the 12 `(+x)^(k-6)` path families, and checks the closed-form
witnesses over `k=6,...,100` without rebuilding any full closure.

Exact results:

```text
formal classes reachable at k=6                 53/53
formal classes reachable at k=9                 53/53
reachability-tree nodes                            54
reachability-tree edges                            53
root-fixed edges                                   16
root-satellite parametric edges                    12
non-root fixed edges                               24
auxiliary fixed edge                                1
root-satellite fixed x>=-5 fronts                 12/12
regression edge/k witness cases                  5,035
failures                                             0
```

For every regression case the script directly checks:

- exact source-plus-addition equality with the declared child;
- a genuine pair of distinct source components;
- d6-minimizing endpoints;
- monotone L1-shortest path length;
- exact path addition set;
- strict component contraction;
- Q2/Q3 validity of the successor.

The finite `k<=100` sweep is a regression on the structural proof, not the
basis of the universal statement.

## 8. Consequences and remaining boundary

Combining A4-L2a and A4-L2b now proves the **persistence half** of A4-L3:
for every `k>=6`, every one of the 53 frozen behavioral keys is realized
by an actually reachable state. Equivalently, under the frozen key
identification,

\[
Q_6\subseteq Q_k.
\]

Hence the all-k lower bound `R^*(X_k)>=3` also follows from the already
known rho-3 frozen class.

What remains open is only the reverse inclusion / no-new-class statement

\[
Q_k\subseteq Q_6.
\]

Until that exhaustiveness step is proved, neither `Q_k ~= Q_6` nor the
all-k upper bound `R^*(X_k)<=3` may be claimed.

Current A4 status:

```text
A4-L1a finite template certification             FROZEN
A4-L1b formal all-k geometry                     PROVED
A4-L2a behavioral persistence                    PROVED (53/53)
A4-L2b parametric reachability                    PROVED (53/53)
A4-L3 persistence / Q6 subset Qk                 PROVED
A4-L3 exhaustiveness / Qk subset Q6              OPEN
all-k quotient equality                          OPEN
all-k R*(X_k) <= 3                               OPEN
```
