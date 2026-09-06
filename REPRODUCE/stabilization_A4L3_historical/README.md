# C07-D7D0 / D7D1 / D7D2-A4-L3 all-k quotient checkpoint

## Frozen status

```text
D7D0 strict atomic potential                     PROVED
D7D0 finite exact closure per finite state       PROVED
D7D0 implementation regression                  PASSED
D7D1 full-closure census                        234 / 262  PARTIAL
D7D1 persistent-rank classification             262 / 262  EXHAUSTED
D7D2 exact quotients at k=6,7,8                  53 / 53 / 53
D7D2 A4.3B satellite templates                   53 / 53  CERTIFIED (k=6,7,8)
D7D2 A4-L1a fixed remainder                      53 / 53  CERTIFIED (k=6,7,8)
D7D2 A4-L1b formal all-k geometry                PROVED
D7D2 A4-L2a(i) connected behavioral persistence   31 / 31  PROVED
D7D2 A4-L2a(ii) T12 isolated persistence          22 / 22  PROVED
D7D2 A4-L2a total behavioral persistence           53 / 53  PROVED
D7D2 A4-L2b parametric reachability             53 / 53  PROVED
D7D2 A4-L3 persistence / Q6 subset Qk             PROVED
D7D2 A4-L3 exhaustiveness / Qk subset Q6           PROVED
D7D2 all-k quotient / Qk isomorphic to Q6          PROVED
D7D2 all-k persistent rank / R*(Xk)=3              PROVED
```

## Quick verification

```bash
python work/d7d0/c07d7d0_atomic_potential_audit.py --suite cube
python work/d7d1/c07d7d1_partial_verify.py
python d7d1_rank_classification_freeze/a4_l1b_formal_geometry_audit.py
python d7d1_rank_classification_freeze/a4_l2a_connected_inert_tail_audit.py
python d7d1_rank_classification_freeze/a4_l2a_t12_bridge_quotient_audit.py
python d7d1_rank_classification_freeze/a4_l2b_parametric_reachability_audit.py
python d7d1_rank_classification_freeze/a4_l3_exhaustiveness_assembly_audit.py
sha256sum -c SHA256SUMS.txt
```

The D7D0 D7B regression regenerates 140,329 actions and may take several
minutes:

```bash
python work/d7d0/c07d7d0_atomic_potential_audit.py --suite d7b
```

The 234-root full-closure JSON remains a partial census. The separate
persistent-rank classification is exhausted for all 262 roots by the
root-layer shortcut proof; do not conflate these statuses. A4-L3 is now
closed: the 53-class quotient and `R*(X_k)=3` hold for every `k>=6`.

## Main files

- `outputs/S2.0C-07_D7D0_atomic_potential_finite_closure_audit.md`
- `outputs/S2.0C-07_D7D1_partial_persistent_absorption_checkpoint.md`
- `work/d7d0/`: potential regression and results
- `work/d7d1/`: closure generator, 234-root checkpoint, and verifier
- `work/d7c_pkg/`: frozen integrated source dependencies
- `HANDOFF.md`: current claim boundary and next semantic task
- `d7d1_rank_classification_freeze/D7D2-A4-L1b_formal_parametric_geometry.md`
- `d7d1_rank_classification_freeze/a4_l1b_formal_geometry_audit.py`
- `d7d1_rank_classification_freeze/D7D2-A4-L2a_connected_inert_tail_persistence.md`
- `d7d1_rank_classification_freeze/a4_l2a_connected_inert_tail_audit.py`
- `d7d1_rank_classification_freeze/D7D2-A4-L2a_T12_bridge_quotient_persistence.md`
- `d7d1_rank_classification_freeze/a4_l2a_t12_bridge_quotient_audit.py`

- `d7d1_rank_classification_freeze/D7D2-A4-L2b_parametric_reachability.md`
- `d7d1_rank_classification_freeze/a4_l2b_parametric_reachability_audit.py`
- `d7d1_rank_classification_freeze/a4_l2b_parametric_reachability_results.json`
- `d7d1_rank_classification_freeze/D7D2-A4-L3_all-k_quotient_exhaustiveness.md`
- `d7d1_rank_classification_freeze/a4_l3_exhaustiveness_assembly_audit.py`
- `d7d1_rank_classification_freeze/a4_l3_exhaustiveness_assembly_results.json`
