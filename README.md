# shortest-bridge-repair-dynamics

**Article:** *Exact Stabilization and Local Decision Structure in Shortest-Bridge Repair Dynamics*

**Authors:** Jihun Bae, Yeonho Bae, Jinglu Hu

This repository is the public mirror of Online Resource 1 accompanying the
article above. It contains the finite data underlying the stabilization
argument, the finite local-decision classification, the supplementary
short-chain examples, and the supplied verification scripts.

The verification scripts in `VERIFY/` are **consistency verifiers for the
finite data provided in this repository**: they check that the included
tables, counts, and classifications are internally consistent with one
another. They are **not** raw-state generators and do not recompute every
underlying object of the article from first principles.

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
- `VERIFY/` — the three consistency-verification scripts described above.
- `SHA256SUMS.txt` — checksums for every payload file in this distribution.

Each subdirectory contains its own `README.md` with a more detailed,
directory-specific description of its contents.

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

This repository mirrors the contents of the `ESM_1.zip` package submitted
as Online Resource 1 for the article. The two are intended to be equivalent
distributions of the same finite data and verification scripts.

## No external data

No external research dataset was used in this study. All data in this
repository were generated for and are specific to this article.
