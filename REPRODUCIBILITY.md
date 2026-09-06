# Reproducibility map

This repository deliberately distinguishes **generation/reproduction** from
**verification**.

```text
REPRODUCE/ : scientific definitions or certified finite records -> regenerated artifacts
VERIFY/    : published artifacts -> consistency checks
```

The distinction matters because the three computational components have
different reproducibility boundaries.

## 1. Main Theorem A: reachable closure and behavioral quotient

Publication launcher:

```bash
python REPRODUCE/reproduce_stabilization.py --k 6 --output build/stabilization
```

For each requested `k`, the launcher starts from the recovered historical
ray-family root, enumerates the complete reachable N2 closure, and then runs the
exact recursive behavioral refinement. The scientific primitives are imported
from the frozen A4-L3 source tree; they are not reimplemented in a second code
base.

A positive `--max-seconds` is a **fail-closed completeness gate**. If the BFS
queue is still nonempty when the limit is reached, the program exits nonzero
and does not refine or accept a partial closure. `--max-seconds 0` disables the
internal wall-clock limit.

Frozen reference anchors are checked automatically when available:

| k | reachable states | stable classes | refinement history |
|---:|---:|---:|---|
| 6 | 9,524 | 53 | 35, 51, 53, 53 |
| 7 | 21,963 | 53 | 35, 51, 53, 53 |
| 8 | 45,939 | 53 | 35, 51, 53, 53 |
| 9 | 87,517 | 53 | archived k=9 assembly |

For `k=9`, the publication data also require 148,722 N2 edges; the launcher
checks this count when a complete k=9 run finishes.

### Audit performed for release v1.0.2

A clean k=6 run regenerated 9,524 states, 18,824 N2 edges, refinement history
`[35, 51, 53, 53]`, and 53 classes. A deliberate k=7 timeout negative control
was also run; it exited nonzero with the BFS queue nonempty and explicitly
reported that no partial closure was accepted.

The larger k=7/8/9 runs are supported by the same complete-closure launcher but
are computationally heavier and were not re-executed as part of this packaging
audit.

## 2. Main Theorem B: finite local-decision classification

Publication launcher:

```bash
python REPRODUCE/reproduce_local_decision.py --output build/local_decision
```

The shipped self-contained layer starts from the certified integrated B7 record
and deterministically regenerates:

```text
117 residual-signature keys
  -> 113 constant-false keys + 4 adjacency-saturation keys
  -> 36,765 constant-branch classes + 293 dynamic-branch classes
  -> 37,018 geometry-false + 40 geometry-true
```

The generated CSV/JSON files are compared semantically with
`LOCAL_DECISION_DATA/` and the script exits nonzero on any mismatch.

**Boundary:** this is a certified-registry-to-publication-table reproduction,
not a first-principles reconstruction of the 37,058-class D1 census from the
ten historical source roots. The deep-history raw rebuild requires the exact
predecessor archives whose SHA-256 identifiers are recorded in
`REPRODUCE/provenance/SOURCE_ARCHIVE_SHA256SUMS.txt`. Historical integration source is preserved byte-for-byte in
`REPRODUCE/provenance/RECOVERED_GENERATION_CODE_20260906.zip`; it is intentionally
kept as a nested provenance archive to avoid Windows path-length failures in the
publication release.

## 3. Supplementary finite compatibility

Fast generated-family smoke test:

```bash
python REPRODUCE/reproduce_finite_compatibility.py --mode smoke \
  --output build/finite_compatibility
```

This freshly generates the walk families and reruns the PWC oracle for every
member:

```text
L=3:  36/36
L=4: 108/108
L=5: 324/324
```

Each generated family must exactly equal the archived M0 family.

The slower retained upstream package can be run with:

```bash
python REPRODUCE/reproduce_finite_compatibility.py --mode full \
  --output build/finite_compatibility_full
```

**Boundary:** the 76-orbit / 528-pair L=5 classification is a frozen input in
the recovered publication-era package. Full mode re-aggregates and audits that
classification; it does not independently regenerate the 76 symmetry classes
from first principles. The repository therefore does not claim otherwise.

## 4. Consistency verification

After or independently of reproduction, run:

```bash
python VERIFY/verify_stabilization.py
python VERIFY/verify_local_decision.py
python VERIFY/verify_finite_compatibility.py
```

All three scripts must print an overall `"pass": true`.

## 5. Environment

The hardened publication launchers were tested with Python 3.13.5 and
NetworkX 3.6.1. Install the declared dependency with:

```bash
python -m pip install -r requirements.txt
```

The finite-compatibility and local-decision launchers themselves use only the
Python standard library.

## 6. Claim discipline

The repository supports the computational premises stated in the article but
does not enlarge their mathematical scope. In particular, it does not assert a
transfer theorem beyond the parametric ray family, a decision rule outside the
frozen finite interaction domain, or a first-principles rebuild where only a
certified finite intermediate is distributed.
