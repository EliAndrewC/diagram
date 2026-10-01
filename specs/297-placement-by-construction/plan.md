# Implementation Plan: placement by construction

**Branch**: none (main, clone `diagram-performance`) | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md)
**Input**: [spec.md](spec.md), [research.md](research.md), [request.md](request.md)

## Summary

One mechanism and three applications of it, a lane-law keeper, and four small changes. (A) **The region**: a raster of the
ground a thing may not take, painted once from every keep-out the consumer reads (PIL draws rects, circles, polygons and
wide polylines in C), with a summed-area table so "is this box clear" is four array reads - the GM's "drawing a box and then
filling it in". (B) Its uses: the seat region the seating offers from (FR-001), the marsh as array throws read against it, the
village grove's crowns and the woodland search's squares read against it (FR-004). (C) The seat judged once before its
layouts (FR-002). (D) The lane law kept per lane as lanes are written, the access tree's lanes laid with the web, and the
settle reduced to the lanes the keeper names (FR-005). (E) The mats as a direct fill, the page's work overlapped, the hem
prefiltered (FR-003, FR-006, FR-007). (F) The measurement and the record (FR-008). Maps may move anywhere the rules allow
(the GM, 2026-09-30); every lever is held to the gate on the regenerated pool, not to identity.

## Technical Context

**Language/Version**: Python 3.14; numpy 2.5, shapely 2.1, PIL 12.3 (already dependencies - PIL draws the page's picture
and the placement pages). **Testing**: pytest through `make`; the harness (`harness.py`, `counts.py`, `measure.py`), base
`c5a631f9b` in `/tmp/base297`, after back to back, fastest of three, loads recorded; `make cohort N=24` before and after.
**Constraints**: every gate rule on every live map; the 100% floor; files under 1,000 lines.

**The region's cost, measured** (observed 2026-09-30, method: `scratchpad/mask_proto.py`, 300 rects and 60 wide polylines on
a 5,550 px canvas at 2 px cells): painting 0.09 s, 10,000 box queries 0.015 s, but the summed-area table over the WHOLE
canvas 0.40 s - so every region is built over its consumer's own window (the seat band, a marsh's box, a grove's footprint, the
woodland search's window), never the canvas, and at the coarsest cell its rules allow.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `297-start` | `make perf LABEL=297-start` in `/tmp/base297` before the first engine edit |
| after | `297-end` | before the push; `make perf-report AGAINST=297-start` |

## Constitution Check

- **VI**: bookends above; the harness back to back. **X clause 15 (v2.27.0)**: every new keep-out test reads a region built
  once per consumer window; a placer may decide by it and move maps; no gate CHECK is coarsened. **XII**: every task
  `research: rendering`; each moving change is a map drawing convention in the spec's Decisions. **XIII**: the base worktree
  is the baseline, the gate and cohort before and after. **XIV**: anything found is fixed here. **XVI**: every FR as written.

## Design

### A. The region (`settlement/_geom/region.py`, new)

`Region(window, cell)`: a uint8 raster over `window = (x0, y0, x1, y1)` at `cell` px. Painters: `rect(x0,y0,x1,y1, pad)`,
`circle(x, y, r)`, `poly(ring, pad)` (a ring grown by `pad`: painted as the polygon plus its outline at width `2*pad`),
`line(pts, half)` (a polyline of half-width `half`, round joins), `cells(set)` (another raster's taken cells, e.g.
`FreeGround.taken`). Every painter is CONSERVATIVE: it grows the shape by one cell, so a box the region calls clear is clear of
every painted shape (a placer may lose a seat at the margin; it never gains a forbidden one). Queries: `taken(x, y)`,
`taken_many(xs, ys)` (numpy), `box_clear(x0, y0, x1, y1)` (summed-area table, built lazily on the first box query and rebuilt
only when painted after it), `box_clear_many(...)`. Off-window ground is taken. Unit tests: each painter against shapely's
exact geometry on random shapes (no painted shape's point is ever reported clear), the box query against a brute-force sum,
and the off-window rule.

### B1. The seat region (FR-001; `hamletgen/homesteads/region.py`, new; `capacity.py`, `stages.py`)

Built when the seating starts (`_seat_households`, after the exit strip and the field corridor are reserved), over the seat
band's window (the free-seat bounds `free_seats` computes, grown by one bundle pitch), at FreeGround's own 8 px cell: painted
with FreeGround's surely-taken cells, the access tree's segments at the corridor's half-width, the reserved wood-floor seats
and the shared sheds' pockets. On each seated house the house's bundle box and its new corridor are painted (the table is
rebuilt over the window, a few milliseconds at 8 px). A seat is OFFERED - by every round, the front row, the lattice ranks,
the rescue cloud and the exhaustive pass - only where its CORE box (house plus yard, at the smallest house the size ladder
rolls, unturned) is clear in the region. The placer still decides each seat it is offered with all of its rules. Moves maps
(a seat whose core box laps a painted cell's grown margin is no longer offered); held to the gate.

### B2. The marsh as array throws (FR-004; `settlement/land/wet.py`)

`_throw`'s two loops become array throws, as `commons` became `grass_scatter` (feature 278), through the region the marsh
already builds once - its `KeepoutGrid` of every keep-out family and its `RingIndex` of the drawn ground - read for all points
at once (`RingIndex.inside_many`, `KeepoutGrid.hit_many` with the mark's slot extras), the crescent ponds and the pond's ellipse
(grown by the lateral pad, and moved by the blade tip for `blade_up`) as array tests, and the feathered edge's probability
computed for the survivors by `shapely.distance` to the outline, as `grass_scatter` does. The points are drawn as numpy arrays
from a generator seeded off the marsh's own stream. Marks at the same densities; they land at different random places. (The
same region the grass reads - one mechanism for every scatter - rather than a raster: the marsh's keep-outs are already filed
once; what costs is asking them one point at a time in Python, research R3.)

### B3. The village grove's crowns (FR-004; `settlement/homestead_parts/stands.py`, `grove_blocks.py`)

`village_grove` builds a `Region` over the footprint's box from its static keep-outs - the `occ` circles (houses, yards,
gardens, byres, sheds, wells, shrines, torii, ponds, earlier groves, reserved seats), the corridor buffers, the sun boxes and
the east-garden strips, and `GroveBlocks`' hard ground - and the jittered grid's candidates are tested against it as arrays
(`taken_many`), replacing `static_clear` per candidate. What depends on the crowns already placed - the spacing (`Seats.too_near`)
and the clumps' own canopy area - stays per candidate over the survivors only.

### B4. The woodland search's squares (FR-004; `hamletgen/hinterland/parcels.py`)

`open_ground_patches` builds a `Region` over its scan window painted with every keep-out `_ok` reads - the `keep` circles grown
by the candidate's half, the `keep_rects`, the lanes and streams at their reach, the marsh ground, and the crops grown by their
set-back (the sunny-side set-back larger, as `_crop_refuses` measures it: each crop painted as its ring grown by the north
set-back and again offset by the extra southern set-back) - and a candidate square is admitted when `box_clear` holds over the
square, plus the window and frame-area rule `_ok` already applies arithmetically. One region per `half` asked (the size roll
re-asks with another half - the trap 284 recorded). Scoring, spacing and the size roll unchanged.

### C. A seat judged once (FR-002; `settlement/rolling/place.py`, `fit.py`, `access.py`)

In `_place_bundle_nucleated`, before the four garden-side layouts are tested: the field's reach (`within_field_reach`, already
memoized), the house box, and `seat_reaches_tree(s, geom0)` - does `_house_candidates` yield any corridor for this house and
yard (the memo entry `access_corridor` would create, peeked once and kept, so the corridor search continues from it). A seat
failing them builds no layout. A side moved by the one computed move is a different seat and is judged at its own position.
Also: `_bundle_geom`'s template cache keys on the household's seat, so 2,261 of 2,716 layouts were rebuilt (research R2's
profile): the layout is keyed per household, not per offered seat, and the rolls it draws are the household's.

### D. The lane law kept as lanes are laid (FR-005; `hamletgen/ways/keeper.py`, new; `settle.py`, `last_resort.py`, `web.py`; `settlement/water_ways/lanes.py`)

1. **The keeper.** `LaneLaw` holds, per lane, the verdict of each per-lane rule (hooked, kinked, the crossing fault, fouled
   fabric, over fixtures, ends behind, dangling, doorstep) and the joint rules that read a lane with the lanes it meets
   (folded joints, needles, doubled tails, connector hairpins, near misses, width steps). It is told of every write - the
   lane writer (`lane`), `reshape_lane`, `drop_lanes`, and every in-place `pts` assignment in `hamletgen/ways` (the 18 sites,
   routed through one `set_lane_pts`) - and re-judges that lane and the lanes whose ends lie within the joint rules' reach of
   it, at that moment. The network-wide rules (the networks count, fragments, reach, needle loops, way outs) are kept on a
   web version stamp and asked once per version.
2. **The access tree's lanes are laid with the web.** `settle_reach`'s tree lanes (15-19 per map, research R7) are drawn at the
   start of `stage_web`, before the skeleton - they were admitted lawful at seating (`tree.admits`) - so the web's own lanes are
   laid around them rather than repaired against them afterward.
3. **The settle asks the keeper.** Each repair step runs only on the lanes the keeper names under its rule (a step whose rule
   names none does nothing and asks nothing), the round loop ends when the keeper names nothing, `unsettled` reads the keeper,
   and the last resort's `lanes_breaking` reads the keeper. `WebRefused` is unchanged in meaning: raised when the keeper still
   names a rule only the tree could mend.
4. **The writers lay lawfully.** Where a step of `stage_web` writes a lane the keeper then names (measured per rule over the
   pool and cohort), the repair that step's rule needs is applied by that writer at the write - so the settle has nothing left to
   do on a well-formed web. Target: no repair round on any pool map (SC-005); a rule that still needs a round on some map is
   recorded with its measurement in `dev/performance.md` (FR-008).

### E1. The mats as a fill (FR-003; `settlement/homestead_parts/yards.py`)

The lattice is computed rather than searched: for each gap in `MAT_GAPS_FT` the columns and rows that fit the floor shrunk by
`MAT_EDGE_CLEAR_FT` (the floor grid already computed by `floor_grid`) are counted directly and the lattice centered; the first
gap whose centered lattice meets the third-of-cover floor is taken (else the one that seats most), then the hand-laid nudge and
thinning as now. Every mat rule holds (its four corners inside the floor by the clearance, off the rack).

### E2. The page's work overlapped (FR-006; `interactive/page.py`)

`render_page` starts the picture and the id map on its two-thread pool as soon as the wrapped SVG is joined, then computes the
hit regions, the explanations, the place card and the JSON blob while they render, and joins them last. The hit layer is
spliced into the SVG text the picture does not read (the picture reads `without_text(svg)`; the id map reads class groups) -
the regions are inserted after the raster inputs are taken. Timed with the R1 marks.

### E3. The hem prefiltered (FR-007; `waterfields/banks.py`)

`hem_to_bank` takes the collector's box grown by its widest bank need (half the wider drawn width plus `BANK_MARGIN`) and the
fall's reach; a vertex outside it is clear without a measure (its gap cannot be under the need, or it is past the collector's
span), the rest measured by `drain_bank_clearance` as now.

### F. Measurement and record (FR-008, SC-001..SC-010)

`measure.py after` (the base then the clone, back to back), `measure.py regen-after` beside a fresh `regen-before`; the R1 phase
marks re-applied as a scratch patch for SC-006's page timing and reverted; `dev/performance.md` gains the section FR-008 owes.

## Order of work

A first (with its tests); then C and E1-E3 (small, independent); then B1, B2, B3, B4, each measured on Inashiro as it lands
(`make map ... PROFILE=1`, fastest of three) and the gate's map tests run on the moved pool; then D in its four steps,
measured after each; then F. A lever that makes its stage slower, or cannot pass the gate on the moved pool after its
failures are fixed, is recorded with the measurement and withdrawn (spec amendment), as 284's were.

## Decisions (for the plan review)

| Decision | Class | Why |
|---|---|---|
| Painters grow every shape by one cell (conservative region) | map drawing convention | a region may lose a seat or a glyph at a margin, never admit a forbidden one - the rules hold by construction |
| Regions are built per consumer window, never the canvas | map drawing convention (a cost decision) | the summed-area table over the canvas costs 0.40 s (measured above) |
| The seat region offers by the CORE box at the smallest house | map drawing convention | the core (house and yard) is common to all four layouts (R6); the smallest house keeps every seat any household could take |
| The marsh's marks land at different random places at the same densities | map drawing convention | array throws draw a different stream, as the grass did in 278 |
| The access tree's lanes are drawn first in the web | map drawing convention | they were admitted lawful at seating; drawing them last made the settle draw 15-19 lanes and repair around them (R7) |
