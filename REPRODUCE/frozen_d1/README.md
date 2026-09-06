# Certified finite-registry reproduction (Main Theorem B)

## Runnable now

```bash
python3 test_b7_regression.py
```

The on-disk directory name `frozen_d1` is retained as a historical provenance identifier.
This test independently re-asserts, directly against the canonical
`02C20D_B7_FULL_DECISION_RULE.json` shipped in this directory: the scope
(`37,058` classes, `117` buckets, `113`/`4` split, `36,765`/`293` class
split), the predicted totals (`37,018` false / `40` true / `0` mismatch),
the rule-table row count and its `constant_false`/`adjacency_saturation`
split, and zero mismatch across all dynamic-branch source summaries. This
script was executed in this environment; its output is archived in
`run_log_test_b7_regression.txt` (`PASS: B7 full decision-rule integration
37,058/37,058`).

`b7_decision_core.py` contains the pure logic (`l1`,
`frame_adjacency_saturated`, `saturated_pair_exists`) used to build the
rule table; it is imported by `test_b7_regression.py` and is included for
inspection.

## Not independently runnable here

`run_b7_integration.py` regenerates the rule table from the raw upstream
B4/B5/B6 aggregate files (`--b4`, `--b5`, `--b6`, `--b5-source-dir`
arguments). Those raw aggregate files are **not** included in this
Supplement — only their SHA-256 hashes are recorded (in
`EXPECTED` inside the script and in the main handoff's
`CANONICAL_HASHES.md`). Re-running this script would require obtaining
the full B0–B7 research-lineage archive, which is out of scope for a
publication-facing Supplement.

`probe_natural_1_5_counterexample.py` (the script behind main-text
Figure 3's `[1,5]` witness) imports internal modules
(`run_02c15_geometry_instrumentation`, `s2comp02c15_env`,
`c07d3e_component_viability`) that are part of the pre-B0 research
codebase and are not distributed in this handoff or this Supplement. It is
included here for provenance/inspection only, not as a runnable script.
The concrete witness values it produced (`actor`, `target`, `R`, gap
profile `[1,5]`) are recorded directly in `THEOREM.md` /
`RESULT_SUMMARY.md` in the original B6 gate archive and are quoted
verbatim in main-text Figure 3's caption.
