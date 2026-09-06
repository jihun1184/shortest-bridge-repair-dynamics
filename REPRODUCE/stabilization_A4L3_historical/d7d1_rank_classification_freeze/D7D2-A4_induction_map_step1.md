# D7D2-A4 (step 1) — Induction Map Candidate: 52/53 exact match

## What was tested

For all 53 canonical behavioral classes shared by `Q_6` and `Q_7`, picked
one representative state each, and tested the candidate induction map:

> In the k=7 representative, find the current component containing the
> satellite point. Shift every point of *that component* with `x < -4`
> (i.e. the corridor/satellite portion, excluding anything touching the
> fixed core boundary at `x = -4`) by `+1` in `x`. Leave every other point
> untouched.

First attempt (blanket shift of all points with `x <= -4`, no component
awareness): **0/53** exact matches — wrong, because other, unrelated
bridge/repair actions elsewhere in the same closure also place points in
that x-range, and blanket-shifting moved core-touching points that must
stay fixed.

Refined to a **component-aware** shift (only the satellite's own current
component, and only its part with `x < -4`, strictly excluding the core
boundary itself): **52/53** exact matches.

## The one exception, diagnosed

In the failing case, the satellite's current component in the k=7
representative is not a simple single-file corridor — it contains a
*thickened* cluster of 5 points at a single x-value (`x=-6`:
`(-6,-1,-1),(-6,0,-1),(-6,1,-1),(-6,2,-1),(-6,2,0)`, apparently a
Q2/Q3-repair patch, not a plain line), plus the satellite point itself at
`x=-7`, connected face-to-face with no gap. A uniform "+1 to everything
`x<-4`" shift does not correctly model "remove exactly one corridor unit"
when the corridor has this kind of local thickening — it just moves the
whole thickened block one unit, which does not reproduce the k=6
representative's structure at that same location (the k=6 representative
already has its own analogous thickened block sitting at `x=-6`, i.e. one
unit closer to satellite than a blanket shift predicts).

## Interpretation

This is a strong, specific, and encouraging result: the induction map
candidate is *almost* exactly right (52/53, ~98%), and the one failure
has a clear, mechanical explanation rather than being mysterious. It
suggests the correct A4-L1/L2 statement is not "shift everything past a
fixed x cutoff" but something like:

> **insert exactly one empty x-layer at a *specific, well-defined position
> in the corridor* (rather than translating everything past a threshold)**,

with the right position being determined by where the corridor is
provably "thin" (a single point per x-value, no thickened repair
structure) — likely near the satellite end, since the thickened patch
above is closer to the core end and should be excluded from the insertion
point search.

## Claim boundary

- This is diagnostic evidence for the induction map (A4-L1/L2), not a
  proof. 52/53 on one k=6-vs-k=7 comparison is strong support, not a
  closed argument.
- The exact statement of where to insert the empty layer (thin-segment
  detection, not a fixed coordinate) has not yet been formalized or coded.
- A4-L3 (bisimulation preservation) and the induction step
  `Q_6 ≅ Q_7 ⟹ Q_k ≅ Q_6 ∀k≥6` have not been attempted — this note only
  covers the very first diagnostic step of A4.

## Next step

Refine the map to "insert one empty layer at the thinnest available
corridor cut" (a well-defined, k-independent rule: the corridor's
single-point-per-x-value stretch nearest the satellite, or more precisely
the last x-value before the corridor widens/attaches to a repair patch),
re-test against all 53 classes for k=6 vs k=7, and — if it reaches 53/53 —
extend the same check to k=7 vs k=8 before attempting the formal A4-L1/L2
proofs.
