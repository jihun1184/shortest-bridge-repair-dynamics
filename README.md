# shortest-bridge-repair-dynamics

**Article:** *Exact Stabilization and Local Decision Structure in Shortest-Bridge Repair Dynamics*

**Authors:** Jihun Bae, Yeonho Bae, Jinglu Hu

This repository is the public mirror of Online Resource 1 accompanying the
article above. It contains the finite data underlying the stabilization
argument, the finite local-decision classification, the supplementary
short-chain examples, and the supplied verification scripts.

The repository separates **verification** from **generation/reproduction**.
The scripts in `VERIFY/` check the published finite tables and classifications
for internal consistency. The publication-facing launchers in `REPRODUCE/`
regenerate the complete Main-Theorem-A closure/quotient, reconstruct the public
local-decision tables from the certified B7 registry, and generate the short-chain
walk families. Historical source lineage is retained separately so the public
wrappers do not silently replace scientific semantics with a new implementation.
The exact boundary of each pipeline is documented in `REPRODUCIBILITY.md`.

## Contents

- `THEORY_NOTE/` — complementary N1/N2 atomic language and finite short-chain
  compatibility theory supporting the supplementary theory note.
- `STABILIZATION_DATA/` — bounded finite objects used by the all-parameter
  stabilization proof: base quotient, representative geometry, connected-
  and isolated-satellite checks, the parametric reachability tree, and the
  complete k = 9 closure summary.
- `LOCAL_DECISION_DATA/` — the complete 117-key residual-signature table,
  the four mixed keys, and aggregate coverage totals for the finite
  interaction domain used in the local decision theorem.
- `FINITE_COMPATIBILITY_DATA/` — finite short-chain tables (chain lengths
  L = 3, 4, 5) and a representative witness supporting the supplementary
  theory note.
- `VERIFY/` — compact consistency-verification scripts for the published finite outputs.
- `REPRODUCE/` — publication-facing reproduction launchers, recovered generation/enumeration source, and source-archive provenance.
- `REPRODUCIBILITY.md` — exact command map, completeness gates, tested anchors, and claim boundaries.
- `requirements.txt` — dependency required by the recovered Main-Theorem-A generator.
- `SHA256SUMS.txt` — checksums for every payload file in this distribution.

Each subdirectory contains its own `README.md` with a more detailed,
directory-specific description of its contents.

## Running the reproduction layer

From the repository root:

```bash
# Complete, fail-closed Main-Theorem-A closure + quotient (k=6 smoke)
python REPRODUCE/reproduce_stabilization.py --k 6 --output build/stabilization

# Certified B7 registry -> public 117-key local-decision tables
python REPRODUCE/reproduce_local_decision.py --output build/local_decision

# Fresh L=3,4,5 walk-family generation and PWC checks
python REPRODUCE/reproduce_finite_compatibility.py --mode smoke --output build/finite_compatibility
```

See `REPRODUCIBILITY.md` before interpreting these commands: Main B retains a
documented deep-history predecessor-archive boundary, and the 76-orbit L=5
compatibility census remains a frozen input rather than a freshly generated
classification.

## Running the verification checks

From the repository root:

```bash
python VERIFY/verify_stabilization.py
python VERIFY/verify_local_decision.py
python VERIFY/verify_finite_compatibility.py
```

Each script prints a JSON summary of its sub-checks and an overall
`"pass": true` on success.

## Integrity

To confirm that no payload file in this distribution has been altered:

```bash
sha256sum -c SHA256SUMS.txt
```

All entries are expected to report `OK`.

## Relationship to Online Resource 1

The repository contains the finite data, verification tools, and publication-facing reproduction layer for the submission supplement.  Release v1.0.2 additionally restores the generation/enumeration source lineage
under `REPRODUCE/` while preserving the published finite outputs and their
verification scripts.

## No external data

No external research dataset was used in this study. All data in this
repository were generated for and are specific to this article.
