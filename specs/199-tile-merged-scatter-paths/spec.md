# Feature 199 - tile the merged scatter paths

**Status**: DRAFT - round 2 of `spec-fidelity` (constitution XVI). Round 1 returned two items: FR-007's
condition failed on a correct implementation (sub-threshold paths span the map - now scoped to paths
of `TILE_MIN`+ subpaths), and FR-008's 100 ms cap on Inashiro could never fail (now a Kuwabata fixture
capped at 40 ms on the median); its aside on FR-010 overstating R1 is taken.
**Request**: [`request.md`](request.md) - the GM's words verbatim (an analysis asked for, then "run
that feature end to end").
**Research**: [`research.md`](research.md) - the measurements the feature rests on.
**Predecessors**: feature 134 (`merge_primitives`, the page's element-count fix, and R5's refusal of
raster layers); 148 (the merge gathers SEPARATED elements); 153 (outlined shapes refuse to merge);
134 T37-T40 (the hit regions and the scrub's marks region - the fix the GM's request recalls).

## Summary

The GM found Kuwabata's page sluggish next to Inashiro's and asked for an analysis in the spirit of
the earlier fix that replaced "is the mouse over any scrub glyph" with "is it over the scrub's
outline". The analysis (research.md R1) found the cost is not hit-testing at all: `merge_primitives`
folds the scrub scatter into three `<path>` elements of 61,000 to 87,000 subpaths whose bounding box
spans the map, and every hover-driven repaint replays each whole path for every screen tile. Kuwabata
shows it first because a portrait map opens at 2.5x its fitted scale (R2); Kashikawa and Sawada are
worse once zoomed (99-129 ms per pointer move against Inashiro's 20).

The fix is the bounding-box shape the GM described, applied to painting: each merged scatter path is
emitted as one `<path>` per 400 px cell of the map, so Chromium culls whole paths by bounding box per
tile. Measured on a prototype, every pool page falls to the instrument's floor (~17 ms per move) at
every zoom, the picture is unchanged to within anti-aliasing seams (R4), and the page grows by about
780 nodes on 11,218.

## Functional requirements

### The mechanism (FR-001 to FR-004)

- **FR-001** `merge_primitives` emits a bucket of `TILE_MIN` (200) or more members as one `<path>` per
  `TILE` (400) map-px cell instead of one path. A member's cell is that of its ANCHOR: a line's first
  endpoint, a circle's or ellipse's center. The tile paths are written consecutively at the position
  of the bucket's first member, in order of each cell's first appearance among the members; within a
  tile the subpaths keep their original relative order; every tile path carries the same attributes
  the single path would have carried (the shared style, and `fill="none"` for a run of lines). A
  bucket below `TILE_MIN` is written exactly as today.
- **FR-002** Nothing else in the merge changes: which elements join a bucket, the translucent and
  outlined refusals, the `skip` bookkeeping and `_SKIP_CAP` are byte for byte as they are (D4). The
  tiling is a split at EMIT time of a set the merge has already licensed to reorder.
- **FR-003** The SVG and the PNG are untouched (feature 134 FR-010) - the tiling belongs to the HTML
  target alone, as the merge does.
- **FR-004** The picture is unchanged (feature 134 FR-002). By construction: a bucket's members are
  mutually reorderable or they would not be in the bucket (R4). And measured: T05 repeats the
  screenshot comparison of R4 on the implementation over the pool pages and records the pixel counts;
  a count past the seams' order of magnitude (tens of pixels in 1.4 million) fails the task.

### The constants (FR-005)

- **FR-005** `TILE = 400.0` and `TILE_MIN = 200` are module constants in `page.py`, each with the
  measurement that chose it at the point of change (R3: 200 px buys nothing over 400 and triples the
  added nodes; 800 gives some of the gain back; a bucket under 200 members costs nothing to replay).
  They are rendering constants, not knobs: nothing physical is behind them, so per-map variance would
  be variance in nothing a reader can see.

### What is proven, and how (FR-006 to FR-008)

- **FR-006** Unit tests on `merge_primitives`: a bucket over the threshold becomes one path per cell,
  every subpath of a tile is anchored in that tile's cell, the subpath count is conserved, the
  attributes are repeated on every tile, the tiles are in first-appearance order at the first member's
  position; a bucket under the threshold stays one path; a run that mixes tiled and untiled buckets
  leaves the untiled ones as they were.
- **FR-007** A structural guard on the REAL page, in the gate: for the rolled reference hamlet's page,
  every `<path>` carrying `TILE_MIN` or more subpaths is confined to one cell - the anchors of its
  subpaths all fall in the same `TILE` cell. A path under the threshold is exempt, because FR-001
  leaves it as one path and the merge has gathered separated elements since feature 148 (measured by
  the review on the current reference page: 280 merged paths of 2 to 199 subpaths span more than
  400 px). The guard is deterministic and fails the moment the split stops running, whatever the
  machine is doing (D5); the review's measurement is repeated in the test's own docstring.
- **FR-008** The FULL tree's browser test gains the instrument of R1 ON THE PAGE THE GM REPORTED: a
  Kuwabata fixture (the pool's own declaration - seed 21, 16 households, the mulberry-dike fish-pond
  archetype, mosaic ponds, mulberry dikes - generated the way the `inashiro` fixture is), a sweep of
  real pointer moves across the viewport at the opening view, the MEDIAN per-move cost recorded in the
  test's output and capped at 40 ms. R2 measured 57.0 ms before the fix and 17.3 after at that view,
  so the cap sits between them with a 2.3x margin over the tiled page for a loaded FULL run and fails
  the untiled one by 17 ms; the median rather than the mean, so a scheduler stall on one move under
  `-n auto` does not decide the test. The reference hamlet's own sweep (19.5 before, 17.8 after - never
  separable) is recorded beside SC-004's numbers in `test_reference_hamlet_timings`, not capped. Both
  guards together are what "so the regression is gated" means here: FR-007 fails deterministically when
  the split stops running; FR-008 fails on the GM's own symptom on the GM's own page.

### Documentation (FR-009)

- **FR-009** `interactive/CLAUDE.md`'s `merge_primitives` row records the tiling and its why; the
  point of change in `page.py` carries the R1 measurement in one paragraph; `research.md` here holds
  the numbers; the pool pages regenerate on landing through the render fingerprint (feature 187), so
  no page is hand-edited.

### What this feature does not do (FR-010 to FR-012)

- **FR-010** It does not touch the hit regions, the widened hit copies, the lifted sluice layer, the
  clip, `page.js` or `page.css`. R1 measured each of them: the clip, the JS and the CSS carry nothing,
  and the hit layer's 20 ms (58.7 -> 38.8 with it removed) is the same repaint at one remove - the
  widened ditch copies put a map-spanning class under the pointer - which the tiling makes cheap; it
  measures at the floor once the paths are tiled, so the layer stays as the GM tuned it.
- **FR-011** It does not take the scatter marks out of hit-testing (`pointer-events: none`). Measured:
  it halves nothing the GM sees, and it would change which feature takes the pointer where a blade
  crosses a lane (D3).
- **FR-012** It does not rasterize anything. Feature 134 R5's refusal stands; the 16x zoom stays vector.

## Success criteria

- **SC-001** Kuwabata's page at its opening view costs no more per pointer move than Inashiro's, on
  the same machine in the same run (R2 prototype: 17.3 against 17.8 ms). Recorded in T05.
- **SC-002** Every live pool page costs under 25 ms per move at the whole-map, opening, 2x and 4x
  views on the analysis machine (prototype: 16.6 to 18.8 ms). Recorded in T05, not gated (D5).
- **SC-003** The page's node count grows by under 10% on every pool page (prototype: +7% on Kuwabata).
- **SC-004** `make done` green; `make page-check` green; the Kuwabata page opened and hovered by
  the session at the opening view before the push.
- **SC-005** With the tiling reverted (FR-001 off) and nothing else changed, BOTH FR-007 and FR-008
  fail - shown once during T03/T04, the way a guard is proven to fire (constitution XVIII).

## Decisions Recorded

- **D1 - the cell is 400 map px.** Measured at 200, 400 and 800 (R3). Rendering constant, no physical
  meaning, recorded at the point of change.
- **D2 - only a bucket of 200 or more members is tiled.** A small merged path costs nothing to
  replay; tiling it multiplies elements for nothing. The threshold is on the bucket because that is
  where the merge decides what becomes a path.
- **D3 - the marks stay in hit-testing.** `pointer-events: none` on the scrub's marks was measured and
  declined: hit-test 1.33 -> 0.14 ms, move cost 58.7 -> 58.9 ms, and it would let a lane or a house
  take the pointer through a blade drawn over it, which is a change in behavior the GM did not ask for.
- **D4 - split at emit time, not a cell in the bucket key.** Same output; a cell in the key multiplies
  the open buckets and with them the `skip` bookkeeping every element does against every open bucket,
  and the `_SKIP_CAP` blockings. The refusals that keep the picture honest are untouched.
- **D5 - two guards: a structural one on the reference page, a timing one on Kuwabata.** The first
  draft capped the timing on the reference hamlet at 100 ms, and the review showed the cap could never
  fail: Inashiro was never the slow page (19.5 ms before the fix), so a full reversion would have
  passed with 4x to spare. The GM accepted "so the regression is gated", and a gate that cannot fail
  is not one. So the timing runs on Kuwabata's opening view, where before and after are 57 and 17 ms,
  capped at 40 on the median. Feature 145's lesson (two fixed waits in this file flaked under a loaded
  FULL run) is met by the margin and the median, not by loosening the cap past the regression.
- **D6 - a subpath that straddles a cell border belongs to its anchor's cell.** The tile's bounding
  box then reaches a stroke's length past the cell, which costs nothing - culling is by box, and a
  box a few px larger than the cell culls the same.
- **D7 - the GM's "bounding box" reading was right and the earlier fix's was too.** Feature 134 T40's
  marks region changed where the pointer is CAUGHT; this changes what a repaint COSTS. Both were
  needed and neither replaces the other.
