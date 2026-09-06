# Reproducibility package

Code and frozen reference data for the numeric claims in *Bounded
Compatibility Depth in Local Repairs of P-Well-Composed Voxel Sets*
(submitted to the SIAM Journal on Imaging Sciences).

The package uses Python 3.9 or newer and only the standard library.

## Quick start

From the package root, run:

```bash
cd scripts
python depth_histogram.py
python bridge_lemma.py
python disjointness_L3_L5.py
python disjointness_L4.py
python section6_1_split.py
python walk_counts.py
```

Each script prints a summary, raises an error if its expected invariants
fail, and writes a JSON result to `outputs/`. The `outputs/` directory is
created at runtime and is intentionally absent from the distributed ZIP.

## Fresh and stored computations

- `depth_histogram.py` re-aggregates the frozen per-orbit L=5 audit.
- `bridge_lemma.py` rechecks the dependency windows in that frozen audit.
- `disjointness_L3_L5.py` and `disjointness_L4.py` recompute the stated
  decision-support disjointness tests from the frozen baseline repairs.
- `section6_1_split.py` recomputes the 27/9 compatibility split from the
  frozen L=3 baseline repairs.
- `walk_counts.py` freshly enumerates L=3, exhaustively excludes repairs
  of size below four for L=4, generates the walk families for L=3,4,5,
  compares them exactly with the frozen M0 sets, and rechecks every
  generated repair with the PWC oracle.

The strength of these checks differs by length. For L=3, minimality and
the complete M0 family are independently recovered by exhaustive search.
For L=4, exhaustive rejection of all smaller repairs establishes m0=4,
while completeness of the 108-member size-4 family uses the manuscript's
walk characterization and exact equality with the frozen M0. For L=5,
minimality and completeness likewise rely on that characterization and
the frozen reference; the script verifies exact set equality and PWC
validity of all 324 members, but does not independently re-enumerate all
smaller and size-5 candidates. Thus reference equality is an executable
consistency check, not an independent proof of frozen-reference
completeness for L=4 or L=5.

The 76-orbit L=5 classification and the selection of its 12 nontrivial
instances are also frozen inputs rather than a freshly regenerated
classification. The observed maximum depth 3 supplies a witness attaining
the conditional theorem's bound; these scripts do not prove the theorem.

The finite-family checks for L=3,4,5 are not evidence that the
decision-support hypothesis holds for arbitrary L. They establish only
the finite cases described in the manuscript.

## Expected results

| Script | Expected result |
| --- | --- |
| `depth_histogram.py` | 76 orbits / 528 pairs; depths 64,6,2,4; maximum 3 |
| `bridge_lemma.py` | 12 PASS / 0 FAIL |
| `disjointness_L3_L5.py` | L3: 3/3 and L5: 12/12, no leaks |
| `disjointness_L4.py` | L4: 6/6, no leaks |
| `section6_1_split.py` | 27 False / 9 True; both classes uniform |
| `walk_counts.py` | L3=36, L4=108, L5=324; exact reference equality |

## Package layout

```text
reproducibility_package/
  README.md
  CONTENTS.txt
  LICENSE
  requirements.txt
  MANIFEST.json
  src/
  scripts/
  reference_results/
```

`MANIFEST.json` records the SHA-256 digest and byte size of every
distributed file except itself. Regenerate it after any edit with:

```bash
python scripts/generate_manifest.py
```

The eight files in `reference_results/` are frozen inputs or archived
copies of freshly reproduced results. Their provenance is stated in
`CONTENTS.txt`.
