# D7D2-A4-L2a(ii) — T12 parametric bridge-quotient persistence

## Status

**PROVED for all 22 T12 isolated-satellite formal families.** Combined
with A4-L2a(i), behavioral persistence is now proved for all 53 formal
families.

This result does not prove that a formal candidate is reachable from its
root for `k>8`, and it does not exclude new behavioral classes elsewhere
in the full closure. A4-L2b and A4-L3 therefore remain open.

## Setup

For every T12 class label `C`, A4-L1b gives

\[
R_C^*(k)=G_C\cup\{s_k\},\qquad s_k=(-k,2,0),
\]

where `G_C subset {x>=-4}` is fixed and `s_k` is an isolated component.
Fixed-fixed N2 actions generate a finite, k-independent family of 737
isolated states `Y_I(k)=I union {s_k}`, where `I` is a fixed background.
Their raw component layers at the lifting base `k=9` contain 517, 191,
28, and 1 states at component counts 2, 3, 4, and 5. Their exact T12
behavioral quotient has respectively `1, 7, 13, 1` classes.

## Parametric Bridge-Quotient Lemma

Let `I subset {x>=-4}` be one of the 737 fixed backgrounds, let `H` be a
6-component of `I`, and consider a shortest monotone bridge from `s_k`
to `H`.

### 1. Target endpoints do not depend on k

For every `t in H`,

\[
d_1(s_k,t)=k+\bigl(t_x+|t_y-2|+|t_z|\bigr).
\]

The additive term `k` is common to every target candidate. Hence the set
of minimizing target endpoints in `H` is independent of `k`.

### 2. Path-word reduction to k=9

Write a shortest monotone path as a word in signed coordinate steps.
Every satellite-to-fixed path uses only `+x` in the x-coordinate and has
at least `k-4` such steps. For `k>=9`, define `D_k` by deleting the first
`k-9` occurrences of `+x` from the word.

The remaining word is a shortest monotone path from `s_9` to the same
target endpoint. After the original path has used those deleted x-steps,
both paths have the same current coordinate and the same remaining word.
Consequently their restrictions to `x>=-8` are identical. Conversely,
prefixing any k=9 path by `k-9` copies of `+x` produces a k-path with the
same `x>=-8` restriction. Thus the set of possible lift fronts
`P intersection {x>=-8}` is k-independent for every `k>=9`.

### 3. Compatibility uses a smaller front

Every Q2/Q3 failure mask has Chebyshev diameter one. A path voxel that
can share such a mask with `I subset {x>=-4}` must lie in `x>=-5`. A
monotone path alone cannot create a Q2/Q3 failure, by the previously
proved finite-window monotone-path theorem implemented in
`finite_window_classification.py`. It follows that bridge compatibility
is determined exactly by `(I union P) intersection {x>=-5}`.

The path reduction preserves this compatibility front, so it preserves
compatible bridge-front existence in both directions. The absorption
label `rho` is also unchanged because the same satellite root block and
the same fixed-component root blocks merge.

The compatibility front and the lift front must not be conflated. An
initial audit found one `(rho, x>=-5 front)` leading to two connected
behavioral classes. Retaining the finer `x>=-8` lift front removes that
ambiguity; the exhaustive base audit finds zero nonfunctional fronts.

### 4. Connected-successor lifting

Let `Z_9` be a normalized k=9 satellite-absorbing successor and `Z_k`
the corresponding successor at `k>=9` with the same lift front. They
agree in `x>=-8`; all differences lie in `x<=-9` and remain in the same
satellite-descendant component.

The exhaustive k=9 base certificate checks every connected state in the
union descendant closure of all 22 T12 candidates. For every such state:

- every minimizing endpoint on the satellite-descendant component lies
  in `x>=-7`;
- every subsequent N2 addition lies in `x>=-6`;
- every state is Q2/Q3-valid.

For any changed point `p` of `Z_k` with `p_x<=-9`, path reduction supplies
a shadow point `q=(-9,p_y,p_z)` in `Z_9`. Against any unchanged component
in `x>=-4`, `q` is no farther than `p`. Since no k=9 minimizing endpoint
lies left of `x=-7`, a changed point cannot become a new minimizing
endpoint after lifting. All minimizing endpoint pairs therefore remain
in the common front and are identical.

The corresponding shortest paths have additions in `x>=-6`. Such an
addition is at least three x-layers from every changed voxel in `x<=-9`,
so no local Q2/Q3 witness can contain both. Compatibility, addition sets,
root partitions, and `rho` labels are consequently identical. Successors
again agree in `x>=-8`, closing induction over descendant depth. Thus the
rho-labeled descendant graphs of `Z_9` and `Z_k` are isomorphic.

Therefore insertion or deletion of the remote `+x` prefix can change raw
bridge paths and raw addition sets, but it does not change the set of
rho-labeled connected behavioral successor classes. This is the required
Parametric Bridge-Quotient Lemma.

## Induction over isolated component count

We now prove persistence simultaneously for all 737 isolated states.

For component count two, there is no fixed-fixed action. Every successor
absorbs the satellite, so its behavioral class is k-independent by the
Bridge-Quotient Lemma and connected-successor lifting.

Assume persistence for isolated states with fewer than `m` components.
For an isolated state with `m` components:

- a fixed-fixed action is geometrically and semantically k-independent,
  leaves the satellite isolated, and strictly lowers component count, so
  its successor class is fixed by induction;
- a satellite-absorbing action has a k-independent rho-labeled connected
  successor-class set by the Bridge-Quotient Lemma.

The component count, maximum outgoing `rho`, and root-identity partition
are preserved under the natural identification `s_9 <-> s_k`. Hence the
complete recursive behavioral key is k-independent. The induction reaches
component count five and covers all 737 isolated states, including the 22
formal T12 candidates.

At k=9, exact three-round keys of those 22 candidates match their frozen
A4-L1a behavioral-key SHA256 values 22/22. A4-L1a/A3.2 already certifies
the same classes at k=6,7,8. Therefore all 22 T12 formal families are
behaviorally persistent for every `k>=6`.

## Finite base certificate and regression

`a4_l2a_t12_bridge_quotient_audit.py` performs one union-closure
enumeration at k=9 and a k=6/k=9 comparison over every isolated fixed
background. Its exact results are:

```text
T12 formal classes                         22
frozen c3 SHA matches                      22/22
union descendant states                   87,517
union N2 action edges                     148,722
isolated intermediate states                 737
connected descendant states               86,780
fixed-fixed edges                           1,024
satellite-absorbing edges                  34,183

raw actions over all isolated backgrounds
  k=6                                      9,279
  k=9                                     35,207

invalid states                                  0
remote endpoint violations                      0
remote action-support violations                0
fixed-successor type failures                   0
connected successor SHA failures                0
nonfunctional x>=-8 lift fronts                 0
k=6/k=9 background quotient mismatches          0
```

The large raw-action increase is real; the theorem concerns the
rho-labeled behavioral successor-class set, not path or action
multiplicity. The finite certificate verifies the bounded hypotheses and
the first unseen level. The universal conclusion comes from path-word
reduction, locality, inert connected-successor lifting, and component-
count induction.

## A4 status after this result

```text
A4-L1a finite certification                    FROZEN
A4-L1b formal all-k geometry                    PROVED
A4-L2a(i) connected persistence                PROVED (31/31)
A4-L2a(ii) isolated T12 persistence             PROVED (22/22)
A4-L2a total behavioral persistence             PROVED (53/53)
A4-L2b parametric reachability                  OPEN
A4-L3 new-class exhaustiveness/all-k quotient   OPEN
```
