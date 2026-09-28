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
sampling is added. **Test**: the
seat against the old scan over synthetic obstacle sets and the pool maps' bamboo.

### A5. Whole-ring scans through indexes (FR-009)

- `_crosses_fabric` (`ways/fabric.py`): a polygon whose box, widened by `gap`, misses the run's box is skipped; within a
  polygon, a run segment whose box widened by `gap` misses the polygon edge's box is skipped - a crossing needs the boxes to
  meet and `seg_dist < gap` needs them within `gap`.
- `_trim_to_service`'s field and steading tests and `push_clear_of_fabric` (`ways/geom.py`): `edge_dist` against a polygon
  becomes `RingIndex(poly).edge_within(x, y, limit)` (the ring store's shared indexes, 281) with the closed/strict bound
  each test uses.
- The comb's `_dry` (`settlement/fields/comb.py`): the water lines filed once in `seg_reach_index` with their `half`; a bead
  asks the segments whose widened box holds it, `seg_dist >= half` deciding.
**Test**: each against a copy of its old form over synthetic inputs, including points exactly at the bound.

### A6. The grove draw's crown test through an index (FR-011, `homestead_parts/groves.py`, `shrines_wells/woods.py`)

`_crown_seat_clear(x, y, r, crowns)` walked every nearby and every drawn crown per crown - 713,438 comparisons over the
pool. A `CrownGrid` files crowns by position in cells of twice the largest crown radius (a crown within `max(r, r_other)` of
the point lies in the 3 x 3 cells round it); `drawn` is filed as crowns land. The same `>=` decides. **Test**: equality over
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
  strided slices of `ok`; the offsets reaching the best count so far are then walked in the old `(i0, j0)` order with the old
  `_off_center` tie-break, so the lattice chosen is the old one.
- `_lay_by_hand`: a neighbor quad whose box is farther than `need` from the mat's box is skipped before `_quad_gap`.
- **Test**: `mat_cells` against a copy of the old function over the pool's yards (their `w, h, poly, keep_out, salt` recorded)
  and synthetic ones (a rack, a small yard, a quarter-turned floor) - identical lists.

### B1. A* (FR-001, `hamletgen/ways/route.py`)

The heap holds `(g + h, g, ix, iy)` with `h = hypot(ix - gx, iy - gy) * cell`; the stale-entry check compares `g`. The
start/goal presets, the corner rule and the toll are unchanged. **Test**: over the recorded requests, on the same lattice
every A* cost no more than Dijkstra's (a copy in the test), every drawn link clear, the new router's drawn path (A* and the
chosen cell together) at most `5%` longer than the old router's, and a request with no path still returns [].

### B2. The coarser lattice (FR-003)

The callers' cells (`cell=` at each `_route` call, default 10) raised to 12 and to 14 in turn; for each, the pool, the
rescue-rounds scenario, the toys and `make cohort N=24` rolled and the unreached houses counted. The largest cell with none
more than the base's is taken; the counts at every cell tried are recorded (research R2).

### B3. The field search without its blind probe (FR-004, `hamletgen/water/fit.py`)

After a first carve short of the target, the next carve is at `_predict_k`'s size, not the bracket's top. The probe to the
top is taken when a carve's acreage grows less than `SATURATION_GROWTH` times the previous for a larger `k` (the fan not
growing with its size - the clamped envelope of cohort seed 47), so a saturating aspect is still found and still cut short.
**Test**: `_fit_at_aspect` over a stubbed `carve_comb` whose acreage saturates probes the top and stops; over one that grows
as `k ** 2` it never carves the top; the pool's fields within tolerance.

### B4. The carve's rows as arrays (FR-005, `waterfields/sector_rows.py`)

Each body row's vertices for all its columns at once: the two thread bounds per row (already per row), the column
interpolation, the wobble and drift as numpy over the columns, then the supply push per vertex (scalar, through the memo)
and the quad tests. Kept only if Sawada's field stage, fastest of three, is faster with it than without; otherwise
withdrawn with the measurement (research R2).

### B5. The board's coarser candidate lattice (FR-007 second half)

Samples along a route every `24` px instead of `12`, for hamlets and villages - kept only if the notice stage, fastest of
three, is faster with it than without (FR-007). **Test**: the board's rules (verge, beds, water, fit, caption) hold on every
pool map, via the gate.

### C. Measure and record (FR-012, SC-001 to SC-011)

The four named stages (FR-011): the grove draw is A6; the grove fill, the seam closing, the commons and the flush are
re-profiled once A lands, and each gets its lever. Then the after-profile is read under the same rule: anything slow that a
change of the allowed kind makes significantly faster is taken in this feature; only what cannot be is left, each with its
measurement (FR-012). The landing order: A lands, the pool regenerates byte-identical against `5f15c65bd` (confirmed first to regenerate
itself in `/tmp/base284`); then B, under 276's FR-006 condition. `measure.py after`, `make perf LABEL=284-end`,
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
