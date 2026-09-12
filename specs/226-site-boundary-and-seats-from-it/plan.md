# Plan - 226 the site boundary, and the seats proposed from it

Spec: [`spec.md`](spec.md). Engine code (`hamletgen/homesteads/stages.py`, `seats.py`, `settlement/rolling/fit.py`,
`place.py`, `_geom/primitives.py` if a helper is needed); GATED route.

## Constitution Check

VI: Inashiro first, then the pool, the cohort, the review. X clause 15: the boundary is the index built once;
the per-candidate work is a few segments. X clause 5: the boundary builder, the pre-test and the bounded spiral
have unit tests. XII: D1-D5. XVI: reviewed first. Principle XII's research: rendering, no physical claim - the
rules' numbers are unchanged, only where they are held.

## Order

1. FR-001 the boundary (shapely union + buffer + simplify, `facing_chains`), recorded; a test on a toy field.
2. FR-002 the fit test on the boundary path; `make map` Inashiro; the counts.
3. FR-003 the proposals from the chains, the pre-test, the spiral bound; the counts in the manifest.
4. The pool; the cohort; R2; `make done`; the review; land.
