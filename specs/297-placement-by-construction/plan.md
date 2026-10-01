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
band's window (the free-seat bounds `free_seats` computes, grown by one bundle pitch), at FreeGround's own 8 px cell. It is
TWO rasters, both kept current as what stands changes:

- **Buildable**: painted with FreeGround's surely-taken cells, the access tree's segments at the corridor's half-width, the
  reserved wood-floor seats and the shared sheds' pockets, and each seated homestead's bundle box as it is seated.
- **Reachable**: the buildable raster's free cells CONNECTED to the access tree - a flood fill (PIL `ImageDraw.floodfill` on a
  copy) seeded from the free cells the tree's segments touch, redone when the tree gains a corridor or a homestead is seated.
  It is the cautious reach: a door outside it has no way to the tree through free ground at all, so no corridor can be found
  for it; a door inside it may still find none, which the placer's exact test (C) decides.

A seat is OFFERED - by every round: the front row, the lattice ranks, the rescue cloud and the exhaustive pass - only where
(a) at least one garden side's ENVELOPE (the side's own bundle box at the SMALLEST house the size ladder rolls, from the
household-independent layout template at turn 0) is clear in the buildable raster, and (b) the door ground (the yard's box at
that size) touches the reachable raster. The offering is computed for a round's whole candidate list at once
(`box_clear_many`, `taken_many`), not per candidate. The placer still decides each seat it is offered with all of its rules.
Moves maps (a seat whose envelope laps a grown margin is no longer offered; a seat at a larger house may still be refused by
the placer, as now); held to the gate.

### B2. The marsh as array throws (FR-004; `settlement/land/wet.py`)

`_throw`'s two loops become array throws, as `commons` became `grass_scatter` (feature 278), against ONE region: the marsh's
`KeepoutGrid`, which already files every keep-out family once, gains the two it lacked - the crescent ponds and the pond's
ellipse, filed as rings (the ellipse as its 32-gon) with the lateral pad and the blade tip as slot extras - and the drawn ground's
`RingIndex`. All points are read at once (`RingIndex.inside_many`, `KeepoutGrid.hit_many`), and the feathered edge's probability
is computed for the survivors by `shapely.distance` to the outline, as `grass_scatter` does. No keep-out is asked per point or
in turn. The points are drawn as numpy arrays from a generator seeded off the marsh's own stream. Marks at the same densities;
they land at different random places.

### B3. The village grove's crowns (FR-004; `settlement/homestead_parts/stands.py`, `grove_blocks.py`)

`village_grove` builds a `Region` over the footprint's box from its static keep-outs - the `occ` circles (houses, yards,
gardens, byres, sheds, wells, shrines, torii, ponds, earlier groves, reserved seats), the corridor buffers, the sun boxes and
the east-garden strips, and `GroveBlocks`' hard ground - and the jittered grid's candidates are tested against it as arrays
(`taken_many`), replacing `static_clear` per candidate - and `static_clear` itself is backed by the same region, so every path
that asks it (the jittered grid, the windbreak's gap fill, the re-seat) reads the region. What depends on the crowns already placed - the spacing (`Seats.too_near`)
and the clumps' own canopy area - stays per candidate over the survivors only.

### B4. The woodland search's squares (FR-004; `hamletgen/hinterland/parcels.py`)

`open_ground_patches` builds a `Region` over its scan window painted with every keep-out `_ok` reads - the `keep` circles grown
by the candidate's half, the `keep_rects`, the lanes and streams at their reach, the marsh ground, and the crops grown by their
set-back (the sunny-side set-back larger, as `_crop_refuses` measures it: each crop painted as its ring grown by the north
set-back and again offset by the extra southern set-back) - and a candidate square is admitted when `box_clear` holds over the
square, plus the window and frame-area rule `_ok` already applies arithmetically. One region per `half` asked (the size roll
re-asks with another half - the trap 284 recorded). Scoring, spacing and the size roll unchanged.

### C. A seat judged once (FR-002; `settlement/rolling/place.py`, `fit.py`, `access.py`, `bundle.py`)

In `_place_bundle_nucleated`, before any garden-side layout is built (`_bundle_geom` is not called), the seat's own questions
are asked once: the field's reach (`within_field_reach`), the water (`lot.watered`: the house's position and whether the household
keeps a well), the house box, and `seat_reaches_tree(s, core)` - does `_house_candidates` yield any corridor for this house and
yard, where `core` is the house-and-yard geometry (`_core_geom`: the two rects of the household's layout template, moved and turned
by the seat's rake, and the turn - the fields `doors_of` and the corridor search read) computed without the full layout. The memo
entry `access_corridor` would create is the one peeked, so the corridor search continues from it. A seat failing them builds no
layout; the four layouts of a seat that passes share the answers. A side moved by the one computed move is a different seat and
is judged at its own position. Also (WITHDRAWN, R9): `_bundle_geom`'s template cache keys on the household's seat, so 2,261 of 2,716 layouts were
rebuilt (research R2's profile); keyed per household instead, a large-yard household lost the per-seat yard rolls that let it fit a
tight seat, and seed 3 seated 9 of 10. The template stays keyed on the seat offered.

### D. The lane law kept as lanes are laid (FR-005; `hamletgen/ways/keeper.py`, new; `settle.py`, `last_resort.py`, `web.py`; `settlement/water_ways/lanes.py`)

1. **The keeper.** `LaneLaw` holds, per lane, the verdict of each per-lane rule (hooked, kinked, the crossing fault, fouled
   fabric, over fixtures, ends behind, dangling, doorstep) and the joint rules that read a lane with the lanes it meets
   (folded joints, needles, doubled tails, connector hairpins, near misses, width steps). It is told of every write - the lane
   writer (`lane`), `reshape_lane`, `drop_lanes`, and every in-place `pts` assignment in `hamletgen/ways` (the 18 sites, routed
   through one `set_lane_pts`) - and judges that lane and the lanes whose ends lie within the joint rules' reach of it, at that
   moment. The network-wide rules (the networks count, fragments, reach, needle loops, way outs) cannot be asked of a web still
   being built - every web is in pieces while it is laid - so they are kept on a web version stamp and asked once, at the end.
2. **The access tree's lanes are laid with the web.** `settle_reach`'s tree lanes (15-19 per map, research R7) are drawn at the
   start of `stage_web`, before the skeleton - they were admitted lawful at seating (`tree.admits`) - so the web's own lanes are
   laid around them.
3. **Every repair moves to the write.** Each rule's repair - the step of today's settle that mends it (`square_every_crossing`,
   `settle_shapes`, `settle_ends`, `settle_joins`, `settle_needles`, `settle_widths`, `settle_defer`, `settle_fragments`,
   `prune_the_tree`, `settle_way_outs`, `settle_dangling`, `settle_shadows`, `settle_street_ends`) - is applied by the write hook
   to the lane the keeper names under it, at the moment that lane is written; what that repair writes is itself judged at its
   write, so a repair's own consequence is mended where it lands, never in a later round. A lane no repair can make lawful is not
   laid (or is taken back at its write) - the last resort's drop, made where the lane is laid, never a tree lane.
4. **No settle after the web.** The round loop (`settle_the_web`'s rounds), `unsettled`'s whole-law re-ask and the last resort's
   passes are retired. When `stage_web` ends it reads the keeper - the per-lane and joint verdicts it holds and the network-wide
   rules asked once - and raises `WebRefused` (or `refuse_unreached`) naming any break; nothing is repaired and no lane is dropped
   there. `meta.web_settle` records what the writes repaired (counts per rule) and that no round ran. A map the engine cannot lay
   lawfully this way is a finding to fix in the writer, and a mechanism that cannot be made to work is withdrawn by a spec
   amendment through review, never kept as an exception.

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
measured after each (D3 and D4 land together - with the rounds retired, every repair must already be at its write); then F. A lever that makes its stage slower, or cannot pass the gate on the moved pool after its
failures are fixed, is recorded with the measurement and withdrawn (spec amendment), as 284's were.

## Decisions (for the plan review)

| Decision | Class | Why |
|---|---|---|
| Painters grow every shape by one cell (conservative region) | map drawing convention | a region may lose a seat or a glyph at a margin, never admit a forbidden one - the rules hold by construction |
| Regions are built per consumer window, never the canvas | map drawing convention (a cost decision) | the summed-area table over the canvas costs 0.40 s (measured above) |
| The seat region offers where a garden side's envelope at the smallest house is clear and the door ground is reachable | map drawing convention | the smallest house keeps every seat any household could take; reach is the cautious one (free ground connected to the tree) and the placer's corridor search still decides |
| ~~Every repair is applied at the write; a lane no repair makes lawful is not laid~~ - built at the write and at the pass boundary and withdrawn (R14: fails the gate both ways) | map drawing convention (the same lane law) | FR-005, Amendment 1 |
| The marsh's marks land at different random places at the same densities | map drawing convention | array throws draw a different stream, as the grass did in 278 |
| ~~The access tree's lanes are drawn first in the web~~ - withdrawn (R10, R14: slower, alone and with D3-D4) | map drawing convention | R7, Amendment 1 |

## Amendment 1 (2026-10-01): the designs as built, by measurement (spec Amendment 1; research R9-R11)

- **A.** The region paints with PIL's own primitives and a two-cell margin (`GROW = 2.0`); shapely buffers were most of a region's
  cost. `fill_many` paints many shapely geometries by kind. The property test (no painted point read clear) holds at cells 2-8.
- **B1.** Built as planned with two measured changes: the static ground on FreeGround's own grid, its surely-taken cells painted
  exactly (grown on an offset grid they over-refused - Inashiro seated no one); the seated homesteads NOT painted (R15: painted, every household still seated but the stage 9% slower); the reach is the free cells' 4-connected components meeting the tree's strip
  (a run-length union-find - PIL's flood fill is Python), its summed-area table kept with it. A side's envelope is tested shrunk by
  a cell (the placer samples nine points).
- **B2.** Through the marsh's `KeepoutGrid` read as one painted region (`KeepoutGrid.taken_many`), the crescents and the pond's
  ellipse filed into it; the grass reads the same.
- **B3.** `GroveBlocks.region()` paints the fill's seven static families once; `static_clear` reads it first and asks the families
  only where it is taken. The regions-alone form built and withdrawn (R16: fails woods W25 at the gate).
- **B4.** `open_ground_region`, one per size, at 3 px (at 8 px the margin moved a parcel off its brook line).
- **C.** The field's reach and the water before any layout; the corridor once per seat after the envelope (R10); the per-household
  template withdrawn (R9).
- **D.** D1 as `keeper.kept` (pure verdicts per lane geometry); D2-D4 built three ways and withdrawn under this plan's rule (R14: as
  D1-D4 state it, the network-wide repairs at the end and the hook at the outermost write - 16 of 22 webs broken or unreached, two
  raising from the passes' own index walks, 1.72x slower); targeted rounds built and withdrawn (R12); the measured fix kept (R11):
  `settle_dangling` drops what its trim cannot mend, so the last resort no longer runs on Inashiro.
- **E3.** `hem_rings_to_bank` (every plot at once) for the comb; the single-ring hem scalar.
