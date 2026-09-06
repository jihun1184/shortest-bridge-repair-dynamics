# D7D2-A2 — Closure-Level Cross-Check Results

## What was done

Per the agreed roadmap, `contact_automaton.py` was cross-checked against
full brute-force `certificate_bridge_actions` enumeration at **every state**
of real N2-reachable closures (not just the root layer), using
`closure_level_crosscheck.py`.

## Results

```text
orbit_15 repair_0:  6,289 states, 3,394 certificates checked, 0 mismatches, max rho = 3
orbit_15 repair_1:  4,914 states, 2,986 certificates checked, 0 mismatches, max rho = 3
orbit_33 repair_0:  1,099 states,   820 certificates checked, 0 mismatches, max rho = 4
```

11,203 states and 7,200 certificates total, across one full R*=3 orbit (both
repairs) and one full R*=4 root (positive control), **zero mismatches**, and
the observed max ρ in each case matches the previously-known R* value
(3, 3, 4 respectively) exactly.

## A bug was found and fixed during this check — reported for transparency

The first run of this cross-check reported 27 "mismatches" in a 200-state
subsample. Investigation traced every one of them to the same cause: at
some certificates, no compatible bridge exists at all (both brute force and
the automaton agreed: zero actions / `flag=None`), but the test harness's
`flag_to_expected_rho_bucket(None)` incorrectly returned an empty set
instead of `{0}`, so a correct "0 == 0" agreement was flagged as a
mismatch. This was a bug in the **test harness's bucket-mapping**, not in
`contact_automaton.py` or the underlying Lemma. After the one-line fix
(`{0}` instead of `set()` for the `None` case), the same 200-state
subsample showed 0/582 and 0/598 mismatches, and the subsequent full runs
above confirm this at full scale. This is recorded here rather than
silently corrected, per the checkpoint's own evidentiary standard.

## Claim boundary

- This validates the Contact-Accumulator Sufficiency Lemma (and the
  threshold-quotient corollary) empirically at **every state of two real
  closures**, not just at roots. Combined with the direct proof in
  `D7D2-A1.2_A1.3_sufficiency_proof.md`, this is strong evidence the
  automaton is exact, not merely a heuristic that happens to agree at
  shallow depth.
- This is still only 2 orbits (3 roots) out of the full family. It is not
  a proof that the automaton is correct for all D7D1 roots — it is a
  regression oracle check on representative small cases, exactly the role
  the user assigned it (A2), not a substitute for A3/A4.
- The next open question (A3) — whether the reachable-state space itself
  can be quotiented/stabilized as the ray parameter k grows — is untouched
  by this note.
