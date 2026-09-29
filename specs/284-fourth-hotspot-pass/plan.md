# Implementation Plan: the fourth hotspot pass

**Branch**: none (main, clone `diagram-performance`) | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)
**Input**: [spec.md](spec.md), [research.md](research.md), [request.md](request.md)

## Summary

Thirteen requirements in three kinds. (A) Exact changes - the router's one index per route, the page from the structured
blades and marks and one parse of the rest, the board's lazy caption test, the bamboo search outward, the whole-ring
scans and the grove draw's crown test through indexes, the toll's bitmap - each proved by an equality test and by the pool
coming out byte-identical with all of (A) landed and (B) not yet. (B) Moving changes of the kind the GM named - A*, the
coarser lattice, the field search without its blind probe, the carve's rows as arrays (kept only if faster), the board's
coarser candidate lattice - held to 276's FR-006 condition. (C) The measurement and the record.

## Technical Context

**Language/Version**: Python 3.14, shapely 2 and numpy (already dependencies). **Testing**: pytest through `make`; the
harness (`harness.py`, `counts.py`, `measure.py`), before in `/tmp/base284` (`5f15c65bd`), after back to back, fastest of
three, loads recorded. **Constraints**: every gate rule on every live map; the 100% floor; files under 1,000 lines.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `284-start` | total 17.4 s, median 4.1 s, worst 5.4 s (observed 2026-09-28, method: `make perf LABEL=284-start` in `/tmp/base284`, load 5.6 -> 5.1, log copied into the clone) |
| after | `284-end` | before the push; `make perf-report AGAINST=284-start` |

## Constitution Check

- **VI**: bookends above. **X clause 15**: A2, A5, A6, A7 are index-once. **XII**: every task `research: rendering`; the
  moving changes are map drawing conventions recorded in the spec. **XIII**: the base worktree is the baseline, `make
  cohort N=24` before and after. **XIV**: anything found is fixed here. **XVI**: every FR as written.

## Design

### A1. One link index per route (FR-002, `hamletgen/ways/route.py`, `ways/clearance.py`)

`_route` obtains `fabric_index(hard, WEB_HARD_GAP, walls, gap, water, 14.0)` once - the index `_clear_link` asks for every
link of the string-pull, whose memo key (every polygon's identity, length and ends, and every water line) was rebuilt per
link. `clearance.clear_runs` takes an optional prebuilt `index`; `_clear_link_idx(a, b, index)` is `_clear_link` on it. The
pull's search (from each point, the farthest point whose link is clear) is unchanged. **Test**: the drawn paths of the
recorded requests (`tests/fixtures/route_requests_mizuguchi.json`) identical with the index hoisted and A3 not landed.

### A2. The page from structured primitives (FR-006, `settlement/finish.py`, `interactive/page.py`, `interactive/raster.py`)

- `flush_blade_groups` keeps, per output slot it fills, what it wrote from: `("blades", color, kept)` and `("marks", marks)`
  in `self.out_struct[z]`. `finish()` hands `out_struct` to `write_html`.
- `render_page` parses every other classed string ONCE into `(start, end, tag, attrs, extent)` elements (`parse_elements`,
  the regexes `merge_primitives` and `drop_offmap` each ran) and hands that list to `drop_offmap`, `merge_primitives`,
  `marks_region` and `hit_layer`, which take an optional `elems=` and parse only when not given. A structured slot's
  elements are built from its tuples - a blade is a line with its four coordinates, a mark carries its extent - with the
  attrs its string carries, so each pass reads the same elements it read before.
- Why this split and not every producer converted (research R2): the scrub's and the marsh's structured ink, the scrub's marks region
  included, is about 83% of the page's parsing and no other class is over 5%; one parse per string covers the rest.
- **Test**: every pool map's page byte-identical, and a synthetic page (lines, circles, a translucent and an outlined
  shape, a path, a transformed string) byte-identical through both routes.

### A3. The board's lazy caption test (FR-007 first half, `settlement/structures/fixtures/siting.py`)

The final choice is `max(_in_the_open, key=(fits, lab ok, score))` over `_fitting` (the seats at the best caption level)
among `_above_floor`. The seats are sorted stably by `(lab ok, score)` descending and `_sitable` asked in that order; the
first seat at `board_caption_level`'s top level (2) that is not shaded is the answer, and a shaded one at the top level is
kept as the fallback; only when no seat reaches the top level are the rest asked and the old expression applied. Exact:
the stable sort keeps `max`'s first-maximal tie-break. The anchored-handover branch (`_hand`) keeps its full evaluation
(it filters on the best level before its own band). **Test**: the choice with and without laziness over the candidates of
the five pool rolls' boards and synthetic candidate sets with ties.

### A4. The bamboo search outward (FR-008, `hamletgen/hinterland/bamboo.py`)

The positions of the old scan, each with its distance to the target and its scan index, sorted by `(distance, index)`; the
first that fits is the answer - the old scan kept the nearest, the first met on a tie. Both scales as before. This takes the
table's "bamboo sampled more coarsely" by removing the same wasted tests exactly; if SC-006's floor is not met, the coarser
sampling is added AFTER T09, as a moving change in the B phase under SC-011's moving condition (B6). **Test**: the
seat against the old scan over synthetic obstacle sets and the pool maps' bamboo.

### A5. Whole-ring scans through indexes (FR-009)

- `_crosses_fabric` (`ways/fabric.py`): a polygon whose box, widened by `gap`, misses the run's box is skipped; within a
  polygon, a run segment whose box widened by `gap` misses the polygon edge's box is skipped - a crossing needs the boxes to
  meet and `seg_dist < gap` needs them within `gap`.
- `_trim_to_service`'s field and steading tests and `push_clear_of_fabric` (`ways/geom.py`): `edge_dist` against a polygon
  becomes `RingIndex(poly).edge_within(x, y, limit)` (the ring store's shared indexes, 281) with the closed/strict bound
  each test uses - `edge_within` answers strictly-under, so a `<=` test (`_trim_to_service`'s `end_serves`) asks it at the
  limit plus a hair and re-applies `<=` to the distance it returns.
- The comb's `_dry` (`settlement/fields/comb.py`): the water lines filed once in `seg_reach_index` with their `half`; a bead
  asks the segments whose widened box holds it, `seg_dist >= half` deciding.
**Test**: each against a copy of its old form over synthetic inputs, including points exactly at the bound.

### A6. The grove draw's crown test through an index (FR-011, `homestead_parts/groves.py`, `shrines_wells/woods.py`)

`_crown_seat_clear(x, y, r, crowns)` walked every nearby and every drawn crown per crown - 713,438 comparisons over the
pool. A `CrownGrid` files crowns by position in cells of twice the largest crown radius (a crown within `max(r, r_other)` of
the point lies in the 3 x 3 cells round it); `drawn` is filed as crowns land. The cell is fixed before filing at twice the largest crown radius the draw can make, so it
covers every query radius too. The same `>=` decides. **Test**: equality over
synthetic crown sets; the pool byte-identical.

### A7. The toll's bitmap (FR-010, `hamletgen/ways/route.py`)

`set_crossing` also records the set of cells whose 3 x 3 neighborhood holds a sample; `in_brook_band` returns False at once
for a point whose cell is not in it (the old 9 lookups would all have come back empty). **Test**: 281's toll equality test,
extended.

### A8. The yards' mats in arrays (FR-011, `settlement/homestead_parts/yards.py`)

- `inside` (the quarter-foot grid's floor test): numpy over the whole grid - the signed distance of every point to every edge
  of the convex floor quad; surely in where every one clears `clear` by a margin, surely out where one falls short by it,
  and the scalar `point_in_poly and edge_dist >= clear` asked in the band between. `spot` / `ok` then as arrays too.
- The lattice search: for each gap and each `(nc, nr)`, the seated count at every offset `(i0, j0)` is the sum of `nc * nr`
  strided slices of `ok`; the offsets reaching the GLOBAL best count over every `(nc, nr)` are then walked in the old `(nc, nr, i0, j0)` order
  with the old `_off_center` tie-break and strict-improvement rule, so the lattice chosen is the old first-maximal one.
- `_lay_by_hand`: a neighbor quad whose box is farther than `need` from the mat's box is skipped before `_quad_gap`.
- **Test**: `mat_cells` against a copy of the old function over the pool's yards (their `w, h, poly, keep_out, salt` recorded)
  and synthetic ones (a rack, a small yard, a quarter-turned floor) - identical lists.

### B1. A* (FR-001, `hamletgen/ways/route.py`)

The heap holds `(g + h, g, ix, iy)` with `h = hypot(ix - gx, iy - gy) * cell`; the stale-entry check compares `g`. The
start/goal presets, the corner rule and the toll are unchanged. **Test**: over the recorded requests, on the same lattice
every A* cost no more than Dijkstra's (a copy in the test), every drawn link clear, the new router's drawn path (A* and the
chosen cell together) at most `5%` longer than the old router's, and a request with no path still returns [].

### B2. The coarser lattice (FR-003)

Only the call sites at the default 10 ft lattice are raised; the deliberately fine lattices stay (the cells of 5.0 and 6.0,
`_FINE_CELL` 3.0, and `sweeps`' `min(10, gap / 6)`). The cell steps 12, 14, 16, 18 toward `MIN_WEB_GAP` and stops at the
first cell that strands a house; the largest cell before it is taken. At each cell the pool, the rescue-rounds scenario,
the toys and `make cohort N=24` are rolled and the unreached houses counted PER MAP AND PER SEED against the base's (no new
or larger shortfall anywhere, SC-011), a stranding the driver's re-roll hid counted too (`meta.roll_attempt` and
`meta.roll_after` say a map was re-rolled after a stranded farmhouse). The counts at every cell tried are recorded (research
R4).

### B3. The field search without its blind probe (FR-004, `hamletgen/water/fit.py`)

After a first carve short of the target, the next carve is at `_predict_k`'s size, not the bracket's top. The probe to the
top is taken when a carve's acreage grows less than `SATURATION_GROWTH` times the previous for a larger `k` (the fan not
growing with its size - the clamped envelope of cohort seed 47), so a saturating aspect is still found and still cut short.
`SATURATION_GROWTH` carries its reason beside it: a fan scales about as `k ** 2`, so a larger `k` whose acreage grows less
than linearly in `k` is being clamped.
**Test**: `_fit_at_aspect` over a stubbed `carve_comb` whose acreage saturates probes the top and stops; over one that grows
as `k ** 2` it never carves the top; the pool's fields within tolerance.

### B4. The carve's rows as arrays (FR-005, `waterfields/sector_rows.py`, `waterfields/carve.py`)

All three parts FR-005 names, as numpy over a row's columns (the body) and over a quad batch (the tests):
- the vertices: the two thread bounds per row, the column interpolation, the wobble and the drift;
- their pushes off the supply banks: `_clear_supply` as an array function - each stroke's segments against every vertex at
  once (a stroke is tens of segments, so a points x segments distance array is small), the nearest segment, the bank's
  half-width from the stroke's taper, the push along the normal, repeated for the vertices still inside a bank, at most the
  scalar loop's six rounds, with the scalar tie-break for a point on a centerline;
- the plot tests: `spills` (each corner's fall against the drain's at its `u`), `above` (the canal line) and `in_supply`
  (each edge's 3 px samples against the strokes) over the row's quads at once.
The quads that pass are appended in the scalar order, with the same random draws. Kept only if Sawada's field stage, fastest
of three, is faster with it than the scalar rows; otherwise withdrawn and the measurement recorded (research R5). A part
that cannot be put in arrays is brought to review as an exception with its measurement, not left scalar silently.

### B5. The board's coarser candidate lattice (FR-007 second half)

Samples along a route every `24` px instead of `12`, for hamlets and villages (the only tiers that roll; the frozen legacy
town is never regenerated), in both lattices that seat the board - `place_kosatsuba`'s and `stage_notice`'s re-seat lattice
(`hamletgen/frame.py`) - kept only if the notice stage, fastest of
three, is faster with it than without (FR-007). **Test**: the board's rules (verge, beds, water, fit, caption) hold on every
pool map, via the gate.

### B6. The bamboo's coarser sampling, only if A4 misses SC-006's floor (FR-008)

A moving change, after T09: the scan's step raised, the same keep-outs and reach; its Decisions row is in the spec.

### C. Measure and record (FR-012, SC-001 to SC-011)

The five named stages (FR-011): the grove draw is A6 and the yards' mats A8; the grove fill, the seam closing, the commons and the flush are
re-profiled once A lands, and each gets its lever. Then the after-profile is read under the same rule: anything slow that a
change of the allowed kind makes significantly faster is taken in this feature; only what cannot be is left, each with its
measurement (FR-012). The landing order: A lands, and the pool - the hamlets AND the magistracy pages, which go through `render_page` - regenerates
byte-identical against the clone's HEAD just before the first A commit (`A_BASE`), itself regenerated in a detached worktree
first; main merged 283 after `5f15c65bd` and moved the magistracy sheets, so `5f15c65bd` is not the reference for T09 (it
stays the TIMING base). A main merge during A re-takes `A_BASE` the same way. Then B, under 276's FR-006 condition, each
moved map's houses, paddies and ways before and after recorded in the research record (research R6) - the "research entry"
SC-011 asks for. `measure.py after`, `make perf LABEL=284-end`,
`dev/performance.md`'s fourth-pass section.

## Verification per piece

| piece | unit test | map proof |
|---|---|---|
| A1-A7 | equality against the old form | the pool byte-identical before B |
| B1 | cost, clearance, length bound over recorded requests | 276's FR-006 condition |
| B2 | the unreached-house counts per cell | the cohort, the toys, the pool |
| B3 | stubbed saturating and growing fans | fields within tolerance |
| B4 | the plots within tolerance | kept only if faster |
| B5 | the gate's board rules | the pool |

## Complexity Tracking

A2 changes three page modules' signatures (an optional `elems=`); every existing caller passes nothing and parses as today.

## Amendment 1 (2026-09-28): what was built, after the measurements

The spec's Amendment 1 records the why; this is how each piece landed.

| piece | outcome | where |
|---|---|---|
| A1-A8 | built as designed; the pool byte-identical against `A_BASE` before B (T09) | as designed above |
| A6 (the grove draw's crown grid) | built, exact, and WITHDRAWN: slower than main's two scans after main's 269 reworked the draw (the windbreak 8-12% slower on three pool hamlets); main's own `CrownIndex` in `_geom` serves the rank | `settlement/homestead_parts/groves.py` |
| A2's "one parse of the rest" | not built: the passes that re-read a string cost 0.051 s and 0.059 s a map together, a ceiling of about 1% of a roll (research R7) | - |
| A3 | built as `board_choice`, the caption level asked lazily in ranking order | `settlement/structures/fixtures/siting.py` |
| B1 (A*) | built, measured over the pool and cohort against a same-run spread (research R6): 2.4% faster in all against 0.6% with B3 in; measured again alone on the merged engine, B3 out: 5.0 s under the shipping mean against an 8.9 s spread - WITHDRAWN on that; the search is Dijkstra in the base's heap order, the base's recorded-request equality test restored | `hamletgen/ways/route.py` (`lattice_search`) |
| B2 (the coarser lattice) | measured at 12-18 px on the engine that ships, the toys added (research R4), WITHDRAWN: `ROUTE_CELL` stays 10; the run's coarser cells declined what 10 px declined, and that change went with the withdrawal (it made the sweeps' own 14 px lattice decline boxes it routed) | `hamletgen/ways/route.py` |
| B3 (the blind probe) | built, measured over the pool and cohort against a same-run spread (research R6): 5% faster in all against 1% - WITHDRAWN on the rules (its moved maps failed five gate rules, two from stages only it reaches); the base's search restored with the reason at the point of change | `hamletgen/water/fit.py` |
| B4 (rows as arrays) | the edge walk built in a probe and timed (research R5), WITHDRAWN: 3.6 times slower | `b4/harness.py` |
| B5 (the board's 24 px lattice) | built, WITHDRAWN: it broke the entrance-board rule's test; in its place the verge band is sampled first (`VERGE_FIRST`), exact, tested against whole-band sampling | `settlement/structures/fixtures/siting.py` |
| B6 (the bamboo's coarser sampling) | TAKEN, since A4 missed SC-006 on Mizuguchi: `BAMBOO_SEAT_STEP_FT = 16` | `hamletgen/hinterland/bamboo.py` |
| FR-014 (new) | a re-roll resumes at the seats: `resume_at` (found by name, so a timed stage still resumes), `build(..., snapshot=)`, `resume`; tested on stand-in stages and byte-identical on six re-rolling maps (research R8) | `hamletgen/driver.py` |
| FR-009, one more scan | `push_clear_of_fabric` asks only the polygons whose widened box holds the point; tested against the old walk | `hamletgen/ways/geom.py` |
| the connector defect | `_touch_junctions` never drops the connector; its test and the corrected end-meets-end test | `hamletgen/ways/touch.py` |
| A2, A5's tests | the synthetic page byte-identical through both routes; the comb's bead test against its whole scan | `tests/settlement/test_exact_pieces_284.py` |
| C | `measure.py after` and `after-main` (research R1's keys, and main as merged); the pool regenerated: main's maps but for the bamboo thicket on Kashikawa and Mizuguchi (research R6) | `measurements.json` |
