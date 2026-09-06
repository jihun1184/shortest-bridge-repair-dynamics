# D7D2-A1 — Contact-Accumulator Automaton: progress note

## What changed

`compressed_decide(K, s, t)` (frozen, C-06D.4a) answers only "does a
compatible bridge exist between s and t". It was shown in this session that
**ρ is not a certificate invariant**: the same (left, right) component pair
can realize different ρ depending on which specific monotone path is
chosen, because a path can incidentally become 6-adjacent to a third
component it wasn't targeting. Confirmed directly: one certificate on the
orbit-15 root has 23 distinct compatible bridge actions realizing both
ρ=2 and ρ=3.

This session built and validated an extension, `contact_automaton.py`,
that decides "does some compatible bridge realize ρ≥4" **without**
enumerating monotone paths, by augmenting the frozen compressed state
`(p, σ)` with a small saturating annotation `A ∈ {None, <other-component
id>, SAT}` tracking how many components beyond the two targeted ones the
path-so-far has touched. `A` is treated as a pure annotation (does not
feed back into the legality check `compressed_transition` already
performs) — this is the Contact-Accumulator Sufficiency Lemma referenced
in conversation. It is **empirically supported, not yet formally proved**.

## Validation performed (all reproducible via `verify_contact_automaton.py`)

1. **Formula check.** ρ = 2 + |{other components 6-adjacent to the new
   path voxels}| was checked against the official `absorption_block`-based
   ρ on every action of every certificate for the 12 known root-layer
   states (6 R*=3 orbits × 2 repairs): **2,656 actions, 0 mismatches.**
2. **Automaton vs brute force.** `contact_automaton`'s SAT/no-SAT decision
   was checked against exhaustive `certificate_bridge_actions` enumeration
   on 18 real roots (12 negative controls with known R*=3, 6 positive
   controls with known R*=4 from the 28 previously-uncomputed roots):
   **18/18 exact agreement.**

This is real empirical validation on real instances, not a proof that the
Contact-Accumulator Sufficiency Lemma holds in general. It should be
treated as strong supporting evidence, not as a closed theorem, until
proved as a corollary of the existing Full Future-Language / Markov-
Sufficiency Theorem.

## What it unlocked: ray extension

Brute-force `certificate_bridge_actions` enumeration hit a combinatorial
wall quickly: on the ray `s=(-k,2,0)`, runtime went 3.2s (k=9) → 24.2s
(k=10) → **did not finish in 280s at k=11**. The `(-k,3,0)` ray hit the
same wall one step earlier (k=9→10: 26.0s → did not finish in 280s).

Using `contact_automaton` instead (root-layer only, both repairs, per k):

```text
ray (-k,2,0): checked k = 6 .. 100, no rho>=4 found, ~18s total at k=100
ray (-k,3,0): checked k = 5 .. 100, no rho>=4 found, ~30s total at k=100
```

Runtime grows roughly linearly in k instead of combinatorially. This is a
genuine computational unlock, not just a faster brute force.

## Claim boundary (do not overstate this)

- This is still a **root-layer-only** result: it shows no action *at the
  root itself* has ρ≥4, for k up to 100 on both rays. It does **not**
  establish `R*(X(s)) ≤ 3` for these larger-k roots — that requires the
  same argument to hold at every state in the full N2-reachable closure,
  which has not been checked here (and full closures are exactly what
  brute force cannot afford at this k).
- The Contact-Accumulator Sufficiency Lemma is empirically validated on 18
  instances + 2,656 actions, not proved as a general theorem.
- No claim of an infinite persistent-rank-3 family is made yet. This is
  strong supporting evidence for one, not the family itself.

## Immediate next steps

1. Extend `contact_automaton` (or a similar contact-tracking DP) from
   root-layer-only to the full reachable closure, so that "no ρ≥4
   anywhere in Reach(X(s))" can be checked for large k the same way
   root-layer was checked here.
2. Attempt the formal proof of the Contact-Accumulator Sufficiency Lemma
   as a corollary of the existing Markov-sufficiency theorem for `(p,σ)`.
3. Only after (1) succeeds for a genuinely unbounded k (or a symbolic
   argument replaces per-k computation) does this become a growing-family
   candidate for D7D2's main theorem.
