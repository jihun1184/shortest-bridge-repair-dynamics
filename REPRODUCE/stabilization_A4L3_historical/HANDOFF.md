# HANDOFF — C07-D7D0/D7D1/D7D2 research checkpoint

**Freeze point:** end of D7D2-A4-L3. The all-`k` 53-class quotient and
`R*(X_k)=3` are proved for every `k>=6`. Read this file first in the next
session; it summarizes the completed proof chain and the remaining
manuscript-integration work without requiring any A4 re-derivation.

## 0. How to use this package

Everything is inside `C07D7D0_D7D1_A4L3_Checkpoint/`. All scripts are
in `d7d1_rank_classification_freeze/` and are meant to be run from the
checkpoint root, e.g.:
```bash
cd C07D7D0_D7D1_A4L3_Checkpoint
python3 d7d1_rank_classification_freeze/verify_shortcut.py
python3 d7d1_rank_classification_freeze/verify_contact_automaton.py
```
Every `SHA256SUMS.txt` (top-level and inside the freeze folder) has been
verified against a **fresh unzip** at every checkpoint in this session —
not just the working copy. If you re-verify, do it the same way (unzip
somewhere new, `sha256sum -c`, rerun a script) rather than trusting the
in-place copy.

## 1. What is PROVED (solid, don't re-derive)

- **D7D0**: the atomic potential `Φ(X) = |Comp_6(X)| + 1[has_fail(X)]`
  strictly decreases on every frozen atomic transition ⟹ every finite
  initial state's atomic-reachable graph is a finite DAG. Regression:
  986 D7B states, 140,329 transitions, 0 violations. Independently
  re-verified in this session (cube suite rerun from source, exact
  match).
- **D7D1 persistent-rank classification: 262/262 roots EXHAUSTED**
  (full closure census is only 234/262 PARTIAL — **keep these two
  separate**, never say "D7D1 EXHAUSTED" alone). 12 roots R*=3
  (orbits 15,79,89,197,206,207), 250 roots R*=4. The 28 previously-open
  roots were resolved via a root-layer shortcut proof (not full closure):
  every root already realizes ρ=4 in its own first N2 layer, and since
  N2 strictly drops component count below 5, no descendant state can
  exceed ρ=4 either. Proved, not just computed.
- **Contact-Accumulator Sufficiency Lemma + threshold-quotient
  exactness** (D7D2-A1.2/A1.3): proved directly from the actual
  `compressed_transition`/`successors` code (the referenced
  `THEOREMS_C06D.md` does not exist anywhere in this package — checked).
  `contact_automaton.py` decides "does some bridge realize ρ≥4" without
  enumerating monotone paths.
- **Full-closure cross-validation** (D7D2-A2): `contact_automaton`
  matches brute-force `certificate_bridge_actions` exactly at **every
  state** of 3 full real closures (orbit_15 both repairs: 11,203 states,
  7,200 certs; orbit_33 repair_0 positive control: 1,099 states, 820
  certs). 0 mismatches.
- **Ray extension** (D7D2-A1 continued): using `contact_automaton`,
  root-layer ρ≥4 checked out to k=100 on both `(-k,2,0)` and `(-k,3,0)`
  rays — none found. (Root-layer only; not a full-closure claim for
  k>8.)
- **Exact behavioral bisimulation quotient stabilizes** (D7D2-A3.2):
  full closures at k=6 (9,524 states), k=7 (21,963), k=8 (45,939) all
  reduce to **exactly 53 canonical behavioral classes**, with identical
  round-history `[35,51,53,53]`, and the canonical class **keys**
  (not just counts) are set-identical pairwise across all three k
  (symmetric difference = 0 every time). All 53 classes have
  `max_rho ∈ {0,2,3}`.
- **A4.3B cut-equivalence templates (finite certification):** canonical
  representatives are 53/53 satellite-component consistent across
  k=6,7,8, with 18 witnessed signatures and 0 inconsistencies.
- **A4-L1a fixed remainder (finite certification):** removing the
  satellite component leaves exactly the same voxel set at k=6,7,8 for
  all 53 classes. The audit assigns every class to exactly one common
  signature and reconstructs all 159 satellite components exactly.
- **A4-L1b formal all-k geometry:** the 53 frozen class data obey exactly
  three corridor laws: `ell=k-4` (30 classes), `ell=0` (22 T12 classes),
  and `ell=k-6` (C050/T14). The 18/18 template connectivity conditions
  and fixed-remainder separation give a proof that every formal
  `R_C^*(k)` is well-defined for all k>=6 and has the declared satellite
  component. It agrees with the certified canonical representative at
  k=6,7,8. This is geometry only, not semantic realization.
- **A4-L2a(i) connected-satellite behavioral persistence:** PROVED for all
  31 non-T12 formal families.  A k=8 finite base audit covers 2,869
  descendant states and 4,035 N2 action edges with zero remote-endpoint or
  remote-action-support violations.  The structural inert-tail lifting
  lemma then gives a rho-labeled descendant-graph isomorphism for every
  k>=8.  Combined with the already-certified k=6,7,8 equality, these 31
  classes persist for all k>=6.  Independent first-unseen-level check:
  31/31 frozen c3 behavioral-key SHA matches at k=9.
- **A4-L2a(ii) isolated T12 behavioral persistence:** PROVED for all 22
  T12 families. Path-word reduction deletes the first k-9 remote +x
  steps, preserving the finite lift front; a k=9 base certificate covers
  87,517 states and 148,722 edges. Component-count induction over the 737
  isolated intermediate states gives all-k persistence. Exact first-
  unseen-level check: 22/22 frozen c3 SHA matches.
- **A4-L2a total:** behavioral persistence is proved for all **53/53**
  formal families. This is not a reachability or exhaustiveness result.
- **A4-L2b parametric reachability:** PROVED for all **53/53** formal
  families. The witness system is a 54-node / 53-edge rooted tree (53
  formal representatives plus one auxiliary connected family): 16
  root-fixed edges, 12 root-satellite parametric bridge families, 24
  non-root fixed edges, and 1 auxiliary fixed edge. The 12 moving bridges
  have explicit words `u (+x)^(k-6) v`; all target endpoints stay
  d6-minimizing and the x>=-5 compatibility front is fixed. Exact
  target-restricted reconstruction gives 53/53 reachability at k=9, and
  the closed-form edge audit has 0 failures in 5,035 edge/k cases for
  k=6,...,100.
- **A4-L3 persistence:** combining A4-L2a and A4-L2b proves every
  frozen behavioral key is actually realized for every k>=6, hence
  `Q_6 subseteq Q_k`. In particular the all-k lower bound `R*(X_k)>=3`
  is proved.
- **A4-L3 exhaustiveness and quotient equality:** PROVED. `C053=X_9` is
  one of the 22 T12 starts used by the A4-L2a(ii) union closure, while
  A4-L2b proves all 22 starts reachable. Hence that 87,517-state,
  148,722-edge union closure is exactly `Reach(X_9)`. A strengthened
  audit finds exactly the frozen 53 keys: 22 isolated T12 keys and 31
  connected keys, with `c_3 -> c_4` partition stability. The arbitrary
  path-word/front normalization already proved in A4-L2a(ii) maps every
  reachable all-`k` behavioral key to this `k=9` base. Therefore
  `Q_k isomorphic to Q_6` and `R*(X_k)=3` for every `k>=6`.

## 2. Historical negative result retained for scope clarity

- A concrete **total** state-level map `Reach(X_{k+1}) → Reach(X_k)` was
  attempted (`thin_tail_contract`) and works perfectly at the
  representative level (53/53 on two independent pairs, 7→6 and 8→7,
  same rule) but is **not total**: 12.5% of raw k=7 states don't land in
  k=6's closure under this map. This was diagnosed (D7D2-A4.2) and is
  **not a counterexample** — landing success is not a class invariant
  (0 "only-bad" classes, 5 "mixed" classes account for all 2,738
  failures). A4-L3 does not repair or assume this map. It uses an
  existential, history-dependent behavioral normalization to `k=9`.

## 3. Next starting point

A4-L1a/L1b/L2a/L2b/L3 are closed. Do **not** redo the quotient induction.
The next task is to integrate the theorem chain into the main manuscript:
state the all-`k` quotient theorem, isolate the finite certificates from
the universal locality arguments, and propagate `R*(X_k)=3` to the
surrounding classification statement. Any broader claim outside this
specific ray family remains separate.

## 4. File guide

- `S2.0C-07_D7D1_rank_classification_freeze.md` — D7D1 census + claim
  boundary.
- `D7D2-A1_progress_note.md`, `D7D2-A1.2_A1.3_sufficiency_proof.md`,
  `D7D2-A2_closure_crosscheck.md` — contact automaton, its proof, and
  full-closure validation.
- `D7D2-A3_A3.1_quotient_discovery.md` — rejected global-fingerprint and
  single-anchor-radius quotient attempts (useful negative results, don't
  retry these approaches).
- `D7D2-A3.2_exact_quotient_stabilization.md` — the 53-class exact
  bisimulation result.
- `D7D2-A4_induction_map_step1.md`, `D7D2-A4.1_thin_tail_contraction_results.md`,
  `D7D2-A4.2_diagnose_total_map_failure.md`,
  `D7D2-A4.3_template_extraction_results.md`,
  `D7D2-A4.3B_cut_equivalence_results.md` — the induction-map and
  template search in order.
- `a4_template_audit.py`, `a4_template_audit_results.json` — reproducible
  53/53 A4.3B audit and its machine-readable result.
- `D7D2-A4-L1a_fixed_remainder_and_template_table.md`,
  `a4_l1a_signature_table_audit.py`,
  `a4_l1a_signature_table_results.json` — finite fixed-remainder
  certificate, the 18-row table, exact class assignments, and witnesses.
- `D7D2-A4-L1b_formal_parametric_geometry.md`,
  `a4_l1b_formal_geometry_audit.py`,
  `a4_l1b_formal_geometry_results.json` — all-k formal geometry proof and
  its closure-free 5,035-case regression.
- `D7D2-A4-L2a_connected_inert_tail_persistence.md`,
  `a4_l2a_connected_inert_tail_audit.py`,
  `a4_l2a_connected_inert_tail_results.json` — proved 31-class connected
  persistence, finite k=8 descendant hypotheses, and k=9 key regression.
- `D7D2-A4-L2a_T12_bridge_quotient_persistence.md`,
  `a4_l2a_t12_bridge_quotient_audit.py`,
  `a4_l2a_t12_bridge_quotient_results.json` — proved 22-class T12
  persistence, k=9 union-closure certificate, and k=6/k=9 quotient check.
- `D7D2-A4-L2b_parametric_reachability.md`,
  `a4_l2b_parametric_reachability_audit.py`,
  `a4_l2b_parametric_reachability_results.json` — all-k 53/53
  reachability theorem and finite witness skeleton.
- `D7D2-A4-L3_all-k_quotient_exhaustiveness.md`,
  `a4_l3_exhaustiveness_assembly_audit.py`,
  `a4_l3_exhaustiveness_assembly_results.json`,
  `D7D2-A4-L3_five-reviewer_check.md` — arbitrary-state front
  normalization, exact `k=9` root-closure identification, all-k quotient
  equality, and `R*(X_k)=3`.
- `smallest_inconsistent.json` — historical pre-A4.3B cut-convention
  diagnostic; it is consistent under the current extractor.
- `contact_automaton.py`, `exact_partition_refinement.py`,
  `anchor_windowed_quotient_v2.py` (kept for reference; v1 rejected),
  `a4_induction_diff.py` — all executable, all reproducible from a fresh
  unzip (verified this session).

## 5. One process note for the next session

Several real bugs were caught and fixed *during* this line of work
(an inverted interior-band inequality that silently deleted state
information; a reproducibility gap where a reported 52/53 result wasn't
actually saved in the checkpointed script). Both were caught by direct
inspection of a concrete example that looked suspicious, not by
re-deriving from first principles. The former A4.3B diagnostic above
follows the same pattern — trust concrete small examples over aggregate stats
when something doesn't add up.

The first T12 quotient attempt also exposed a real boundary issue:
`x>=-5` is sufficient for bridge compatibility but not for uniquely
determining the connected successor class (one front mapped to two
classes). The final proof keeps separate `x>=-5` compatibility and
`x>=-8` lifting fronts. Do not collapse these two roles.
