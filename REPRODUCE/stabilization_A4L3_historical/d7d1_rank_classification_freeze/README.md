# D7D1 Rank Classification Freeze — addendum

This folder is an addendum to the C07-D7D0/D7D1 partial checkpoint. It must
stay inside the checkpoint tree (as a sibling of `work/` and `outputs/`)
because `verify_shortcut.py` imports the frozen dependency package from
`../work/d7c_pkg` and the D7D1 task list from `../work/d7d1`.

## Files

- `S2.0C-07_D7D1_rank_classification_freeze.md` — main report; states the
  precise claim boundary (`full closure census: PARTIAL` vs
  `persistent-rank classification: EXHAUSTED`).
- `shortcut_theorem.md` — the root-layer shortcut proof that gives
  `R*(Y) = 4` for the 28 remaining roots without a full closure.
- `shallow_check_per_root.json` — per-root root-layer rho histograms for the
  28 roots (raw data behind the shortcut).
- `d7d1_final_rank_census.json` — merged 262-root census (234 full-closure
  results + 28 shortcut results), with per-root method tagging and the
  6/125/0 state-level breakdown.
- `verify_shortcut.py` — standalone script; recomputes the root-layer
  enumeration from the frozen source (not from any cached table) and asserts
  the exact histogram and root count. Run:

  ```bash
  python3 d7d1_rank_classification_freeze/verify_shortcut.py
  ```

  from the checkpoint root.

- `SHA256SUMS.txt` — manifest for this folder's own files.
- `D7D2-A4.3B_cut_equivalence_results.md` — the revised cut-equivalence
  definition, exact `53/53` result for k=6,7,8, and all-k claim boundary.
- `a4_template_audit.py` / `a4_template_audit_results.json` — executable
  A4.3B audit and its machine-readable output.
- `D7D2-A4-L1a_fixed_remainder_and_template_table.md` — finite
  fixed-remainder result, explicit 18-template table, and separated
  geometric/semantic proof obligations.
- `a4_l1a_signature_table_audit.py` /
  `a4_l1a_signature_table_results.json` — executable 53-class remainder
  and reconstruction audit, with exact class/template assignments.
- `D7D2-A4-L1b_formal_parametric_geometry.md` — the proved all-k formal
  geometry theorem with the three corridor laws and semantic boundary.
- `a4_l1b_formal_geometry_audit.py` /
  `a4_l1b_formal_geometry_results.json` — closure-free symbolic checks and
  k=6,...,100 regression (5,035 class/k cases).
- `D7D2-A4-L2a_connected_inert_tail_persistence.md` — structural inert-tail
  lifting proof for the 31 non-T12 connected-satellite formal families.
- `a4_l2a_connected_inert_tail_audit.py` /
  `a4_l2a_connected_inert_tail_results.json` — k=8 descendant-semantic
  hypothesis audit (2,869 states / 4,035 action edges) plus 31/31 frozen
  behavioral-key SHA matches at the first unseen level k=9.
- `D7D2-A4-L2a_T12_bridge_quotient_persistence.md` — path-reduction,
  connected-successor lifting, and component-count induction proof for
  the 22 isolated T12 families.
- `a4_l2a_t12_bridge_quotient_audit.py` /
  `a4_l2a_t12_bridge_quotient_results.json` — k=9 union-closure base
  certificate (87,517 states / 148,722 edges), 22/22 frozen-key matches,
  and k=6/k=9 quotient-front comparison over 737 isolated backgrounds.
- `D7D2-A4-L2b_parametric_reachability.md` — 54-node / 53-edge
  parametric reachability-tree proof for all 53 formal families.
- `a4_l2b_parametric_reachability_audit.py` /
  `a4_l2b_parametric_reachability_results.json` — exact target-restricted
  reconstruction at k=6 and k=9 plus 5,035 closed-form edge/k witness
  checks over k=6,...,100.

## One-line status to carry forward

```text
D7D1 full N2-reachable closure census      234/262   PARTIAL
D7D1 persistent-rank classification        262/262   EXHAUSTED
```

Do not compress these two lines into a single "D7D1 EXHAUSTED" statement.
