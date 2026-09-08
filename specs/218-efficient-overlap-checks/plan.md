# Plan - 218 efficient overlap checks

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I / II**: N/A - no UI in this repository.
- **III / IV / V / VII / IX / XI**: N/A - no pool content, no SOURCE blocks, no generated prose; the
  maps must NOT change (FR-003).
- **VI. Verify Before Reporting Done**: PASS. Bookends `218-start` (taken on unmodified code before
  anything changed) and `218-end`; the reference hamlet re-profiled per stage (FR-004 a); every live
  pool map regenerated and diffed byte-identical (`make maps`, then `git status` on `pool/` -
  reference settlement first, then the pool, both as tasks); `make done` green with the two floors;
  no settlement-review is owed because no map moves (a map that moves is a defect under FR-003, not a
  review candidate). The gate's time recorded beside its predecessor (FR-004 c).
- **X. Python Discipline**: PASS. Two closures (`_hard_blocked`, `_lane_blocked`, `_local_blocked`
  and the seat-proximity tests in `village_grove`; `_sparse`'s watercourse branch in `marsh`) become
  calls on a module-level index object tested with plain lists (clause 4 red-green, feature 146's
  lifting doctrine); files stay under 1,000 lines (`stands.py` 545, `wet.py` 525); 100% coverage
  over everything added. The feature ADDS clause 15 to this principle (FR-005).
- **XII. Historical Grounding**: N/A - every task is `research: rendering`; nothing about how a
  place was built changes, and the maps are byte-identical.
- **XIII. No Known Regressions**: PASS. Baseline is the committed pool and the `218-start` bookend;
  byte-identity is stronger than any per-seed comparison.
- **XIV. Fix Defects Where You Find Them**: PASS. The census (FR-002) converts every per-candidate
  scan in the two stages that measurably costs time; those that cost nothing are LISTED with their
  share (spec D5) - a deliberate, recorded decision, not a deferral.
- **XV / XVI**: PASS. The spec is reviewed by `spec-fidelity` before implementation (T01); the field
  stage's exclusion is the GM's own, quoted.
- **XVII / XVIII**: N/A - no README, no guard.

## Design

**The shape of the fix, once.** Every conversion here is the engine's PREFILTER pattern
(`_geom/indexes.py`): the index PRUNES the candidate list, the caller's exact test still DECIDES, so
the verdict equals the linear scan's and the pool regenerates byte-identical. Nothing is coarsened.

**Windbreak (`settlement/homestead_parts/stands.py`).** A module-level `GroveBlocks` built once
per `village_grove` call from plain data - the crop rings with their pad, the dry plots with
theirs, the dike outlines, the watercourse polylines with their half-widths plus the clump's radius,
the corridor polylines with their buffers, the occupancy circles (and the other grove's clumps as a
separate circle set, because `_reseat` tells them apart), the open sun-corridor rectangles, and the
grove's own outline as a `RingIndex`:

- `hard(x, y)` - crops (`boxed_ring_hit` with the crop pad), dry plots (its pad), dikes (inside only),
  water (`boxed_seg_hit`) - the four terms of `_hard_blocked` in the same order.
- `lane(x, y)` - `boxed_seg_hit` over the corridors.
- `local(x, y)` - circles from a `PointGrid` of `(cx, cy, r, box)` items with the same strict
  squared-distance test, then the open rectangles (sun south, garden east, west sun-lane) from one
  grid of `(x0, y0, x1, y1, box)` items with the same strict inequalities.
- `displaced(x, y)` - the other-grove circles alone (the sparse re-seat rule).
- `inside(x, y)` / `rim_within(x, y, limit)` - the outline, via `RingIndex.inside` and
  `edge_within(limit + 1e-9)` then `<= limit` (the original is `edge_dist <= clump`; the epsilon
  keeps the closed inequality exact).
- `Seats` - an incremental `PointGrid` of the clumps seated so far, with `too_near(x, y, r)` for the
  two proximity tests (`_reseat`'s `step * 0.55` against the rounded clumps, the gap fill's
  `clump * 0.5` against the unrounded seats - two instances, one per list, so each test reads the
  list it read before).

The closures stay as one-line delegates (feature 146: ONE body) or are replaced at their call sites.
The grid walk's `point_in_poly(jx, jy, poly)` and the gap fill's become `inside`.

**Hinterland (`settlement/land/wet.py`).** `marsh` builds `wat_g`, one pre-boxed watercourse grid
per distinct pad it will ask for (`{0.0: wat_b} | {p: boxed_grid(boxed_segs(self._watercourse_segs(2.0
+ p))) for p in _pads}`), and `_sparse` passes `near=wat_g[0.0 if role == "pond_fringe" else
mound_pad].near` - the same `boxed_seg_hit` the pond fringe already takes. `_on_watercourse`'s linear
branch remains for its per-corner callers (bamboo, fixtures, woods, the yard context) and is no longer
reached per scatter point. Then the stage is re-profiled and the census (research R2) decides what
else in it is converted: `parcels._clear_gap` (every crop per candidate square) and anything else
the profile shows above noise.

**Doctrine.** Constitution Principle X clause 15 (MINOR, 2.24.0, log entry at the top); root
`CLAUDE.md` bullet after the lifted-closure bullet; skill `CLAUDE.md` Performance bullets; the third
shape in `dev/performance.md` (an index that exists beside the scan that does not use it - this
feature's two cases); the plan template's Constitution Check under X gains the question.

**Tests.** `tests/settlement/test_homestead_parts.py` gains a synthetic-layout equivalence test
(`GroveBlocks` verdicts == the linear expressions, for every keep-out class); `tests/settlement/test_geom.py`
covers any new helper in `_geom/indexes.py`; `tests/settlement/test_wet_ground.py` gains a test that
`_watercourse_segs` is called a bounded number of times by one `marsh` (a counting monkeypatch), which
fails on the old code.

## Verification per task

`make quick` while iterating on the reference hamlet (`make map`), then `make maps` for the tier and a
`git status` diff of `pool/`, then one detached `make done`; `make perf LABEL=218-end` and
`make perf-report AGAINST=218-start` before the push; the timings into research R3/R4.
