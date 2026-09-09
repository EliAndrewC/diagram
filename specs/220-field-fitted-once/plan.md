# Plan - 220 the field fitted once

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I / II / III / IV / V / VII / IX / XI**: N/A - no UI, no pool content, no SOURCE blocks, no
  generated prose; the maps may move (FR-001) and are reviewed (FR-005).
- **VI**: PASS. Bookends `220-start` (taken first, on unmodified code) and `220-end`; the reference
  hamlet re-profiled after each step; `make maps` after the map-changing step; `make verify` (the gate
  with the `settlement-review` beside it) over every hamlet that moved; a from-scratch rendered roll;
  the gate's time recorded. Every generator step is TWO steps - reference, then pool - both as tasks.
- **X**: PASS. `build_comb` becomes two module-level functions with one body (clause 12, feature 146);
  files stay under 1,000 lines (`comb.py` 735, `carve.py` 936 - the index helper lands in
  `banks.py` or a new `waterfields/strokes.py`, not in `carve.py`); the stroke index is an overlap
  check in its efficient form (clause 15) - a per-stroke `PointGrid` of segments, queried with the
  caller's reach; 100% over everything added.
- **XII**: N/A - every task `research: rendering`; no rule about how a place was built changes.
- **XIII**: PASS. Baseline: the committed pool and `220-start`; step 2 byte-identical; step 1 and 3
  judged by the gate and the review.
- **XIV / XV / XVI**: PASS. Spec reviewed before code; review findings fixed in the work.

## Design

**Step 1 - carve and finish (`waterfields/comb.py`).** `carve_comb(...)` returns a `_CombState`
(R, F, channels, threads, plots, a_pts, dpts, drain_bank, brook, envelope, fork, bc, and the inputs
the finish needs) and `finish_comb(state, ...)` runs `close_seams`, the acreage, `_comb_dry_and_beans`
and assembles the dict. `build_comb` = `finish_comb(carve_comb(...))`. `_fit_at_aspect` calls
`carve_comb`, scores on `state.plots` / `state.channels` (the three scorers take a mapping with
`plots` and `channels`; a carved state offers the same two keys), keeps the best state, and returns
it; `fit_field` finishes the best state once. Random state: `R` lives on the state and is consumed
by the finish exactly where the inline finish consumed it.

**Step 2 - the stroke index (`waterfields/banks.py`).** `StrokeIndex(pts, w0, w1, cum, reach)`: the
stroke's segments in a `PointGrid`, each with its index, so `clearance(q)` visits only the segments
whose box is within `reach` of `q` and runs `supply_bank_clearance`'s own arithmetic on them; a query
with no segment within reach returns the "clear" tuple the callers already handle (`gap = 1e9`,
`past = False`). `_SupRow` carries the index; the three callers pass their reach.

**Step 3 - one geometry per plot (`waterfields/seams/`).** A `_Geoms` cache keyed by plot index and
ring identity (rebuilt when `plot["poly"]` is reassigned), a bounds prefilter over plots for the
shared-boundary searches, `STRtree` where the candidate set is the whole plot list. Measured after
step 1 and 2 so only what still costs is touched.

**Verification per task.** `make map PROFILE=1` after each step; `make maps` after step 1 (the pool
moves); the review dispatched with `make verify`; `make perf LABEL=220-end`, `perf-report`; R2-R5.
