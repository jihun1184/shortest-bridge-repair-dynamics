# Reproduction and source lineage

This directory contains the publication-facing reproduction launchers and the
recovered research-lineage source from which they are derived. The compact
`VERIFY/` scripts remain separate consistency checks.

## Publication-facing entry points

```bash
python REPRODUCE/reproduce_stabilization.py --k 6 --output build/stabilization
python REPRODUCE/reproduce_local_decision.py --output build/local_decision
python REPRODUCE/reproduce_finite_compatibility.py --mode smoke --output build/finite_compatibility
```

The exact scientific boundary of each command is documented in
`../REPRODUCIBILITY.md`.

## Stabilization historical source

`stabilization_A4L3_historical/` is the exact extracted A4-L3 checkpoint
(source archive SHA-256
`33f551d1f7384ee90cda61db212c92909d0088f20c573784608298a9e78849ec`).
It contains the N2 closure machinery, exact behavioral partition refinement,
and A4-L1/L2/L3 audit code and finite inputs.

The archived `exact_partition_refinement.py` has two publication-facing hazards:
its historical `__main__` block has a two-vs-three return-value unpack mismatch,
and `build_closure()` silently stops when its wall-clock budget expires.
`reproduce_stabilization.py` imports the historical scientific primitives but
uses a fail-closed BFS launcher: the queue must empty before refinement begins.
No partial closure is accepted.

The older `stabilization_wrapper/` is retained for provenance but the safe
publication command is `reproduce_stabilization.py`.

## Finite compatibility

`finite_compatibility/` is the retained publication-era reproduction package.
Its own README records which results are independently reconstructed and which
are checked against frozen references. `reproduce_finite_compatibility.py`
provides a fast generated-family smoke mode and a launcher for the full retained
script suite.

## Frozen-D1 decision layer

`frozen_d1/` contains the standalone B7 decision regression and integration
source supplied with the supplement. `reproduce_local_decision.py` regenerates
the public tables from the certified integrated B7 record.

`provenance/RECOVERED_GENERATION_CODE_20260906.zip` preserves the recovered
02C9 -> 02C18 -> 02C19 -> 02C20A/B/C/D -> B7 source lineage as a byte-identical
provenance archive. It is kept nested rather than expanded so that the public
release remains Windows-path-safe. A complete raw D1 rebuild still requires
the exact large predecessor archives listed in
`provenance/SOURCE_ARCHIVE_SHA256SUMS.txt`; those archives are not silently
replaced by a new implementation.

## Verification versus regeneration

- `REPRODUCE/`: creates regenerated artifacts within the documented boundary.
- `VERIFY/`: checks the published finite artifacts for internal consistency.

Neither layer enlarges the mathematical scope of either main theorem.
