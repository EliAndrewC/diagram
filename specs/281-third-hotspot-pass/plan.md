# Implementation Plan: the third hotspot pass

**Branch**: none (main, clone `diagram-inashiro`) | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)
**Input**: [spec.md](spec.md), [research.md](research.md), [request.md](request.md)

## Summary

Eleven requirements in three kinds. (A) The exact removals - the clip through the fabric index, the ring indexes shared
by content, the toll's grid, the notice board's two indexes, the watercourse indexes, the caption probe's lane index, the
carve's vertex memo and the windbreak gap fill's memory: each index PRUNES and the existing exact test DECIDES
(`dev/performance.md`), each proved by an equality test against the old form, and the pool comes out byte-identical with
all of (A) landed and (B) not yet (SC-011). (B) The two moving changes - the carve's shared-edge walk and the vectorized
marsh - held to feature 276's FR-006 condition in full. (C) The measurement and the record.

## Technical Context

**Language/Version**: Python 3.14, shapely 2 and numpy (already dependencies).
**Primary Dependencies**: none new.
**Testing**: pytest through `make`; `measure.py before` recorded the base in the clone at `c13a6ebe6`; `measure.py after`
runs a detached worktree of it (`/tmp/base281`) and the clone back to back.
**Constraints**: every gate rule on every live map; the 100% coverage floor; files under 1,000 lines.
**Single-artifact target**: each piece is proved on its unit tests and on the pool's byte-identity (A) or the moved maps (B).

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `281-start` | total 20.6 s, median 5.2 s, worst 5.8 s (observed 2026-09-28, method: `make perf LABEL=281-start` in `/tmp/base281`, log copied into the clone) |
| after | `281-end` | taken before the push; `make perf-report AGAINST=281-start` |

## Constitution Check

- **VI (performance)**: bookends above.
- **X clause 15 (index once, ask per candidate)**: A1 and A3 to A6 are this clause - the index built before the loop.
- **XII (research)**: every task is `research: rendering`; no physical claim changes. B1 and B2 change where a plot edge's
  threshold lands in the last floating-point bits and where random marsh marks land at the same density.
- **XIII (no regressions)**: the base worktree is the baseline; `make cohort N=24` before and after.
- **XIV (fix where found)**: anything found on the way is fixed in this work.
- **XVI (the literal thing)**: every FR as written; no exceptions.

## Design

### A1. The clip through the fabric index (FR-001, `hamletgen/ways/clearance.py`)

`clip_to_clear`'s closure is replaced by `fabric_index(obstacles, margin, (), 0.0, lines, line_margin).fouled`. The closure
tested each line (`seg_dist < line_margin`), then each obstacle (`point_in_poly` or the minimum edge `seg_dist` `< margin`),
which is `fouled_brute(q, obstacles, margin, lines=lines, line_margin=line_margin)` term for term - and `FabricIndex.fouled`
equals `fouled_brute` (feature 138's oracle test, `tests/hamletgen/test_clearance.py`). **Test**: `clip_to_clear` against
a copy of the old function in the test, over clips recorded from a Kashikawa roll and over synthetic obstacles (a
concave ring, a line, a sample exactly on an edge's margin) - equal outputs; the pool byte-identical (SC-011).

### A2. Ring indexes shared by content (FR-002, `hamletgen/clearance.py`)

A module store `_RINGS: dict[tuple[Pt, ...], RingIndex]` keyed by the ring's points as a tuple of float pairs - the
content, so a ring with the same points gets the same index and a changed ring cannot get an old one. `FabricIndex`
asks it for every polygon; `clearance.reset()`, which clears `_MEMO` when every roll ends (`driver.roll_scope`,
feature 210), clears it too. The store is bounded like
`_MEMO`: past `_RINGS_MAX` (4,096) entries it is cleared whole. **Test**: two fabric indexes over overlapping polygon
sets build each distinct ring once (a spy on `RingIndex`); a ring mutated in place between two asks gets a new index; and
`fouled` equal to `fouled_brute` as before.

### A3. The toll's grid sized to the band (FR-003, `hamletgen/ways/route.py`)

`set_crossing` files the course's 5 ft samples in cells of `max(20.0, radius)` and records the cell; `in_brook_band`
reads the 3 x 3 cells around the point (k = 1: a sample within `radius` of the point lies at most one cell away when the
cell is at least the radius) and applies the same `math.dist(p, q) <= r`. **Test**: `in_brook_band` against the old
25-cell form over a grid of points round a synthetic course, including points exactly at the radius; the pool
byte-identical.

### A4. The notice board's indexes (FR-004, `settlement/structures/fixtures/_helpers.py`, `siting.py`, `hamletgen/frame.py`)

- `outermost_join(track, others, step)` builds `seg_reach_index([(o, 0.0) for o in others], KOSATSUBA_HANDOVER_PX + 1e-6)`
  once and asks each sample the segments whose widened box holds it, deciding `seg_dist <= KOSATSUBA_HANDOVER_PX` as
  before (the 1e-6 keeps a point at exactly the reach inside the widened box, so the closed test sees it).
- `RouteReach(routes)` files every route's points in a `PointGrid` tagged by route; `missed(x, y, near)` counts the
  routes with no point within `near` (`math.hypot(q[0] - x, q[1] - y) <= near`, the same expression). `routes_missed`
  becomes `RouteReach(routes).missed(...)` for its one-shot callers (`tools/notes_census.py`); `place_kosatsuba` and
  `hamletgen/frame.py` build one per candidate loop. **Test**: both against the old forms over the routes and ways of a
  Sawada roll and over synthetic cases (a route passing exactly at `near`; an empty route list); the pool byte-identical.

### A5. The watercourse indexes (FR-005, `hamletgen/ways/sweeps.py`, `settlement/rolling/fit.py`)

- `_link_home_bank`: the brook's segments filed once in a `PointGrid` by their boxes; a route segment's crossing test
  asks the segments whose box meets its own (two segments whose boxes do not meet cannot cross), `segments_cross`
  deciding; the `home` parity counts crossings of `(c, mid)` over the segments its box meets - every segment it can cross.
- `_rect_on_stream`: each stream segment's box, widened by `hw`, is compared with the box of the rect's five points and
  four edges before `seg_dist` or `segments_cross` runs - a segment whose widened box misses theirs is farther than `hw`
  from every point and crosses no edge.

**Test**: both against copies of the old forms over a Kashikawa roll's routes and seats, and synthetic touching cases;
the pool byte-identical.

### A6. The caption probe's lane index (FR-006, `settlement/structures/captions.py`, `siting.py`)

`label_seat_clear` takes `lanes=`, an index built by a new `lane_seat_index()` (every lane segment filed by its raw box
with its `half`, and the largest half recorded); without it, it builds one per call. A probe asks `near(cx, cy, maxhalf +
boxhalf)` and decides each returned segment with the same `seg_dist(...) < half + boxhalf`. The two callers that probe
many seats against unchanging lanes (`place_kosatsuba`'s caption levels, `clear_label_seat`'s rings) build it once, as they
already build `boxes` once. **Test**: the probe with and without the index over seats round a Kashikawa roll's lanes; the
pool byte-identical.

### A7. The carve's vertex memo (FR-007, first half, `waterfields/carve.py`)

In `_carve_sector`, after `rspan` is set live, the plots are laid through `edge_m(fv, j, n)`, which remembers
`edge(fv, j, n)` keyed on `(fv, j, n)`; the `f_hi` probe keeps calling `edge` itself, before the wander is live, so its
vertices never enter the memo. `edge` reads only its arguments, the frame, the threads, `rspan` (fixed from here on) and
`sup_idx` (fixed) - no random draw - so a remembered vertex is the vertex. **Test**: a sector laid with and without the memo
gives the same plots; the pool byte-identical.

### A8. The windbreak gap fill's memory (FR-008, `settlement/homestead_parts/stands.py`, `grove_blocks.py`)

- A gap is identified by its two clumps' exact coordinates `(pa, pb)`. When a gap takes no seat in a round it is recorded
  in `_barren`; a later round skips a recorded gap. Exact: every test a candidate faces is static (the outline, `within`,
  the hard ground, the local keep-outs, the lanes, `_near`) except `near_seats.too_near`, and `near_seats` only grows, so a
  point refused in one round is refused in every later one - a gap that seated nothing seats nothing again.
- `GroveBlocks.static_clear(x, y)` - `not (hard or local or lane)` - remembered per point, as `inside` already is; the gap
  fill asks it in place of the three calls (the grid loop and the re-seat keep theirs: they tell `hard` from `local` apart).

**Test**: the gap fill on a synthetic belt with a hard-refused gap and a gap that fills in round two - the clumps equal the
old loop's (a copy in the test), and the refused gap is offered once; the pool byte-identical.

### B1. The shared plot edge walked once (FR-007, second half, `waterfields/carve.py`)

`_quad_in_supply` remembers, per carve, each edge's verdict under the unordered pair of its endpoints, walking it from the
lesser endpoint (tuple order) to the greater, so both plots sharing an edge read one walk. The walk's samples are the old
walk's reversed for one of the two plots - equal but for rounding - so a plot within rounding of the bank's threshold may
flip. Held to SC-011's moving condition; the Decisions row is in the spec. **Test**: the verdict of a shared edge is the
same read from either plot; a quad test against the old function over a carve's plots, allowing only rounding-threshold
cases.

### B2. The vectorized marsh (FR-009, `settlement/land/wet.py`)

`marsh_scatter(...)` beside `grass_scatter` (278): the tint throws and the tuft throws as numpy arrays from a generator
seeded off the marsh's own seeded stream; the tests `_sparse` ran, point for point - the predicted frame, the outline
(`RingIndex.inside_many`), the keep-outs (`KeepoutGrid.hit_many` with the four slot pads the mark's pad selects), the
crescent ponds, the pond's ellipse with the lateral pad and, for a tuft, the blade top, then the feather (dropped where
`u > (ed / feather) ** drop`). The tint's radius, the glint's 12% and the tufts' four blades are rolled from the same
generator. **Test**: a compliance test like the grass's - no mark's keep-out test fails, rounding-aware; the density per
1,000 sq ft within the old scatter's across seeds; Kuwabata's shore still reeded (feature 150's fringe figures).

### C. Measure and record (FR-011, SC-001, SC-011, SC-012)

`measure.py after` - the base worktree then the clone, back to back - writes `base-rerun-*` and `after-*`. The order of
landing makes SC-011 checkable: A1 to A8 land, the pool regenerates, and `git diff --quiet` over the pool manifests against
`c13a6ebe6` must hold (the committed pool at the base: SC-011's reference); then B1 and B2 land and the pool regenerates
under 276's FR-006 condition - `make done`, the rescue-rounds scenario and toys, the forms, the moved maps' research
entries, `make cohort N=24` against the base's. `dev/performance.md` gets the third pass's section and residue table.

## Verification per piece

| piece | unit test | map proof |
|---|---|---|
| A1-A8 | equality against the old form, in the test | the pool byte-identical against `c13a6ebe6` before B lands |
| B1 | shared-edge symmetry; quad verdicts equal but for rounding | 276's FR-006 condition |
| B2 | compliance and density | 276's FR-006 condition |

## Complexity Tracking

None: every piece is an index, a memo or 278's array form applied to one more scatter.
