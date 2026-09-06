# D7D2-A4-L1b — Formal parametric representative geometry

## Status and scope

**PROVED:** the frozen finite data define, for every one of the 53 class
labels and every integer `k>=6`, a formal candidate voxel set whose
satellite part is connected and is exactly the component containing the
satellite. The candidates agree exactly with the certified canonical
representatives at `k=6,7,8`.

**NOT CLAIMED:** reachability from `X_k` or membership in the indicated
behavioral class for `k>8`. In this note, “representative” always means
**formal candidate representative** outside the three enumerated
closures.

## Frozen data and the three corridor laws

For a class label `C`, A4-L1a supplies a fixed remainder `G_C` and a
unique common signature

\[
\sigma_C=(d_C,A_C,B_C).
\]

Comparison of the stored corridor witnesses gives exactly three laws:

\[
\ell_C(k)=
\begin{cases}
k-4, & 30\text{ classes},\\
0, & 22\text{ classes, all assigned to T12},\\
k-6, & 1\text{ class, C050/T14}.
\end{cases}
\]

For the first family the endpoint x-coordinate is always `-4`. For
C050/T14 it is always `-6`. The T12 satellite component is the isolated
satellite itself.

Put

\[
s_k=(-k,2,0),\qquad a_C(k)=s_k+d_C,
\]

\[
L_C(k)=\{a_C(k)+j e_x:0\le j\le\ell_C(k)\},
\qquad e_C(k)=a_C(k)+\ell_C(k)e_x,
\]

and define

\[
S_C^*(k)=(s_k+A_C)\cup L_C(k)\cup(e_C(k)+B_C),
\]

\[
R_C^*(k)=G_C\cup S_C^*(k).
\]

All unions are ordinary set unions. In particular, endpoints and local
pieces may overlap. Since `ell_C(k)>=0`, `L_C(k)` is a closed lattice
segment and the zero-length case is `L_C(k)={a_C(k)}`.

## Theorem

**Formal Parametric Representative Geometry.** For each of the 53 frozen
class labels `C`, the preceding formulas determine a finite voxel set
`R_C^*(k)` for every integer `k>=6`. Its satellite part `S_C^*(k)` is
6-connected, contains `s_k`, and is exactly the 6-connected component of
`R_C^*(k)` containing `s_k`. Moreover,

\[
R_C^*(k)=R_C(k)\qquad(k=6,7,8),
\]

where the right-hand side is the certified canonical representative in
the enumerated closure.

### Proof

**1. Nonnegative corridor length.** The three displayed laws give
`ell_C(k)>=0` for every `k>=6`. Hence every closed segment `L_C(k)` is
well-defined, including the C050/T14 degeneration `ell_C(6)=0`.

**2. Connectivity.** Direct inspection of the complete 18-row frozen
table certifies, for every signature,

\[
0,d_C\in A_C,\qquad A_C\text{ is 6-connected},
\qquad \{0\}\cup B_C\text{ is 6-connected}.
\]

Thus `s_k+A_C` contains both the satellite and the corridor start. The
closed corridor joins that start to `e_C(k)`, and `e_C(k)+B_C` is joined
to the corridor at its endpoint. Their ordinary union is therefore
6-connected and contains `s_k`.

**3. Separation from the fixed remainder.** The frozen A4-L1a table,
checked exhaustively by the A4-L1b audit, has every point of every `G_C`
at x-coordinate at least `-4`. Let

\[
H_C(k)=\{p\in S_C^*(k):p_x\ge-5\}.
\]

For the `k-4` family, the endpoint and endpoint patch are fixed at the
core side, while the only corridor points in `x>=-5` are the fixed final
two positions. For T12, `H_C(k)` is empty for all `k>=6`. For C050/T14,
the endpoint and patch are fixed at `x=-6` relative geometry, and every
point reaching `x>=-5` belongs to that fixed patch. Consequently,

\[
H_C(k)=H_C(6)\qquad(k\ge6).
\]

At `k=6`, A4-L1a certifies that `S_C^*(6)` is exactly the satellite
component of `G_C union S_C^*(6)`, so `H_C(6)` neither overlaps nor is
6-adjacent to `G_C`. Every point of `S_C^*(k)\setminus H_C(k)` has
x-coordinate at most `-6`, whereas every point of `G_C` has x-coordinate
at least `-4`; such points cannot overlap or be 6-adjacent. Hence no
satellite-component leak into `G_C` is possible for any `k>=6`.
Together with Step 2, this proves that `S_C^*(k)` is exactly the component
of `R_C^*(k)` containing `s_k`.

**4. Agreement at the certified k values.** The inferred laws reproduce
the stored length triples `(2,3,4)`, `(0,0,0)`, or `(0,1,2)` at
`k=6,7,8`. A4-L1a already certified exact reconstruction of each of the
159 satellite components from its selected signature and witness, and
exact equality of the corresponding fixed remainders. Therefore
`R_C^*(k)=R_C(k)` for `k=6,7,8`. This completes the proof. `square`

## Root containment corollary

Let the frozen root be

\[
X_k=\mathrm{CORE}\cup\{(-1,-1,0)\}\cup\{s_k\}.
\]

Then `X_k` is a subset of `R_C^*(k)` for every class label and every
`k>=6`. The fixed root voxels occur in the k-independent core-facing
pieces already certified at `k=6`, and `s_k` belongs to the attachment.
Increasing `k` changes only the leftward corridor/attachment position and
does not remove a fixed root voxel. This makes the frozen root-component
labels well-defined on every formal candidate, but it does not imply
reachability.

## Independent regression

`a4_l1b_formal_geometry_audit.py` reads only the frozen A4-L1a table; it
does not rebuild a closure. It checks:

- all four local connectivity hypotheses on all 18 templates;
- the `30/22/1` corridor-law split and the C050/T14 exception;
- `G_C subset {x>=-4}` for all 53 classes;
- exact component separation, root containment, endpoint laws, and
  fixed core-facing geometry for every class and every `k=6,...,100`.

Result: 5,035 class/k cases, zero overlap, disconnect, component-leak,
root-subset, endpoint, or boundary-stability failures. This regression
checks the proof; it is not the reason the universal statement holds.

## Next semantic obligations

- **A4-L2a — Behavioral persistence:** prove that the frozen descendant
  transition structure from each formal candidate realizes the same
  behavioral key for every `k>=6`, without assuming root reachability.
- **A4-L2b — Parametric reachability:** construct an N2 action sequence
  `X_k -> R_C^*(k)` for every class and every `k>=6`.
- **A4-L3 — Quotient conclusion:** combine persistence with a separate
  exhaustiveness argument excluding new behavioral classes.

Until these steps are complete, neither `Q_k ~= Q_6` nor the all-k
persistent-rank conclusion follows from A4-L1b alone.
