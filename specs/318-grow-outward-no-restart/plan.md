# Implementation Plan: Grow outward, never restart

**Branch**: none (main, in the clone) | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

## Summary

The nucleated seating stops throwing seated houses away: one margin is seated, its cluster grows outward until every household
stands, and nothing refuses a seat for its distance from the field. The take-back machinery goes (the margin ladder's take-back,
the rescue, feature 317's withheld re-seat and early stop, the 12:1 refusal, the passage re-lay), the 700 ft field reach goes
with every use, and the growth tries the seat nearer the field first among seats otherwise equal. Amendments 2 and 3: neighbors stand a lane's
threading gap apart, no path is searched while a household is seated, and the ways are laid in the gaps once every house stands.

## Performance bookends (constitution VI)

`make perf LABEL=318-start` at main before the first engine edit, `LABEL=318-end` on the engine as it lands, alternated.
Expected: no thrown-away seating on seed 47 at 40 households (feature 317 R10: 8.2 s against main's 4.0 at 317's landing).

## Decisions

**D1 - No take-back (FR-001, FR-004, FR-005).** `stages.seat_every_household` seats the chosen margin once. The ladder is kept
only for a margin that seats NO house - `_seat_households` returns before seating any (no lawful exit bearing, no lawful field
corridor) - and only then is the next margin tried; with no house standing nothing is taken back. A margin that seats some but
not all is refused (`SiteRefused`, naming the households seated and the margin). Removed: `capacity.rescue_the_margin` and its
constants, `stages.seat_the_margin`, `_passage_withheld`, `passage.passages_spent` and growth's early stop before the widest
level, the 12:1 refusal (`drawn_in_band` asked as a refusal; the declared shape still recorded, `declare_cluster_shape`).

**D2 - The growth keeps widening (FR-002).** `growth.grow_the_margin` queues and offers seats with no radius test: the
`d <= bound` filter on queued seats and the `> bound` refusal of a settled seat go. Where `GROW_LEVELS` runs dry the growth keeps
widening: further levels at 16 directions with rings stepping out by half the least distance each, until a level queues no new
seat on the canvas (every ring point off it or already seen) - the termination. AMENDED with D4 (research R1): the table is one
level, every direction and ring of the old three offered at once. The old radius stays only where it sizes
something else (the exit strip's length, the front row's reach on the other forms, the seat lattice's band).

**D3 - The field reach removed (FR-003, SC-002).** `fit.FIELD_REACH_FT` and `within_field_reach` deleted, with their four
calls (`growth.seat_refused`, `place._place_bundle_nucleated`, `capacity.free_seats`, `fit._parts_fit`'s reach memo). The
growth's seat region window (`region.seat_window`), the free-ground grid's box (`boundary.free_ground_bounds`) and
`capacity.free_seats`' search box are the canvas; their docstrings already say the box bounds the cost, never the answer -
the grid's cost on the whole canvas measured at the bookends. `site_boundary.window` records the canvas box `(x0, y0, x1, y1)` - sized from the map's own extent, FR-003's words - and the
placement-stages plate draws it as a box (no radius, no reach);
the placement-stages legend and the tests pinning 700 updated. `ways/law.py`'s own `FIELD_REACH_FT` (a way reaching the field)
untouched.

**D4 - Nearer the field, all else being equal (FR-003a, SC-002a), AMENDED TWICE: first on measurement (research R1), then by
the GM (Amendments 2 and 3).** The growth's levels are main's again (`GROW_LEVELS` = 8 directions, then 12, then 16; main's
breadth, the GM: "the tie-break thing for the real speedup"), and its heap key is main's distance from the margin's seat center,
taken in RINGS `TIE_RING_FT` (20 ft, a GUESS: about the parting between neighbors' houses) wide, with the distance to the field's
facing chains (`field_distance`) breaking ties within a ring, then the exact distance, then the insertion order. One growth
step offers its seats within about a ring, so the preference fires among the seats a step offers and never pulls the growth
past a nearer ring. Unit tests pin both halves (SC-002a): a farther ring is never tried first, and within one ring the nearer
the field is; the seating counts the seats the tie-break reordered (`seat_search.tie_reordered`), read on the cohort and the pool.

WITHDRAWN: one level of sixteen directions at rings 1.0, 1.5 and 2.0, the nearest the field first (the first amendment). It
kept the cluster near the field (research R1) but tried and refused near-field seats hemmed in by the field (seed 4: 281 seats
offered against main's 80), +11.9% on the bookends; the GM ruled the preference "not a hard requirement; merely an 'all else
being equal, try this first'". Measured in the scratch prototype (observed 2026-10-03, method: per-stage process time on nine
nucleated seeds): the tie-break alone 9.96 s against main's 9.85.

**D5 - The passage recheck without the re-lay (FR-001).** `passage.recheck_passages` keeps only its first arm: a household
reached across a yard whose drawn layout finds a straight or round-the-gable corridor on the finished seating is given it and
its passage ended, in place. `relay`, the stored layouts (`_passage_seats`' layouts, `_tight_of["layouts"]`) and
`meta.passage_unfit` go.

**D6 - The quarter-built figure reported (FR-007).** Page 0032's rule binds villages, not hamlets ("A hamlet is rightly loose
and is not held to it"), and no hamlet code enforces it; the seating records it for every nucleated map
(`meta.built_share`: the area of houses, yards, gardens and homestead groves inside the houses' outline - the convex hull of the
homestead boxes - over the outline's area), refusing nothing.

**D7 - The record (FR-008).** 0029's drawing page (amended by D14): nearer the field, all else being equal; no distance from the field is a limit (the GM's ruling, canon). 0032's: the 700 ft is no limit (its back-row sentence
kept as what the drawn villages showed), and the maps report the built share. 0081's: a passage the finished map makes
unnecessary (its drawn layout given a way of its own) is ended in place; no re-lay. 0004 already states the rule. Every claim
citing the reach goes with its code; claims of changed units re-checked by impl-drift.

**D8 - Occasions.** placement-changed: farmhouse on the pool's nucleated maps (Inashiro, Kuwabata, Sawada) - the seating's
order, limits and gap change; village lane - the ways are laid in the gaps (D12).

**D9 - The threading gap (FR-011).** `growth.grow_gap` is `MIN_WEB_GAP` (the web's own figure for two steadings a lane threads:
`WEB_FABRIC_GAP` off each garden fence and the tread) plus the 2 ft parting the growth already left - 20 ft between footprints,
against 16 before. A corridor's line keeps `ACCESS_HALF_FT` (7 ft) off each homestead, so the gap leaves a 6 ft band its line can
run in. Pairwise exemption: a tight seat (feature 317) is placed at `TIGHT_GAP_PX` from the one neighbor it is reached across and
keeps `grow_gap` from every other footprint (`keeps_its_distance` asked against the others).

**D10 - Lane ground, the cheap check (FR-012, FR-013).** `SeatRegion` gains a second raster, LANE GROUND: the buildable raster
with every seated homestead's box painted grown by `ACCESS_HALF_FT`, flooded from the exit strip and the field's corridor (and
from the window's edge where the canvas goes on, as today). `SeatRegion.opens(geom)`: does the homestead's yard, grown by the
half-width and a cell, touch a reached cell - a summed-area lookup. One predicate, two askers: an ordinary seat is admitted only
where it holds (`place._place_bundle_nucleated`, in place of `seat_reaches_tree`; `fit._parts_fit`, in place of
`access_corridor`), and a tight seat is refused where it holds (`passage.landlocked`, in place of the straight or round-the-gable
corridor test). The raster is rebuilt only when a house is seated (`sync`), as the reach raster is.

**D11 - No per-seat path search (FR-013).** During the seating no corridor is searched, judged or reserved per household:
`fit._parts_fit` no longer calls `access_corridor`, the placer no longer calls `seat_reaches_tree`, and `reserve_way` reserves
nothing for an ordinary household (a passage household's walk is still barred, feature 317). The exit strip and the field's
corridor are reserved as today (`start_tree`, `reserve_field_corridor`). `access_corridor`, `_house_candidates` and
`routed_corridors` stay for the passage recheck after the ways are laid (FR-001) and for anything a village roll asks.

**D12 - The ways laid in the gaps (FR-014), a new module `settlement/rolling/gap_ways.py`, called at the end of
`seat_every_household`, after the last house stands and before `recheck_passages` and `reserve_the_seating`.** Built from the
scratch prototype (research R4):
1. One raster of lane ground over the cluster's box and a margin (cell `GAP_CELL` 5 px: the 6 ft band always holds a cell
   center; 4 px cost 0.3 s more a map, 6 px left a house unreached on seed 4): the homestead boxes counted per cell grown by the
   half-width, the wood seats by the lane gap, the free-ground raster's surely-taken cells, its uncertain cells asked exactly
   (`site_samples_clear`). Indexed once, asked per cell (constitution X).
2. One shortest-path flood from every cell on the exit strip and the field's corridor, 8-neighbor, no diagonal cutting a
   blocked corner, each step costed up by the blocked cells around it so a way keeps to the middle of its gap; stopped 400 px
   past the last house's ring.
3. Houses in order of their ring's flood distance (nearest the way out first). For each: a small search from its dooryard doors
   over its own homestead's open ground (off its house, beds, outbuildings and fixtures by the corridor's own leg tests, and off
   every other homestead by the layers) to the flood's cells; up to `GAP_TRIES` (6) distinct exits, each traced back along the
   flood to the way out - or stopped where it comes within `JOIN_FT` (25 ft, under the shadow rule's 30 ft, `WEB_SHADOW_FT`) of
   a way already laid and the leg onto it is clear, joining it there at a T; pulled taut (`route.taut`, at most `GAP_LEGS` 12
   legs) and admitted by the corridor's own predicate (`access.admitted`: its legs, then the whole tree's lane law); the first
   admitted is reserved (`access.reserve`) and recorded as the house's corridor, exactly as the seating recorded one before, so
   the web, `reserve_the_seating` and the claims read it unchanged.
4. A household none of its exits gives an admitted way: D13.

**D13 - The pinch: reached across a neighbor's yard (FR-014).** A household the gap pass cannot reach is recorded reached across
the nearest household whose way was laid (`reached_across`, `passage` with `kind: "pinch"`), the walk from its dooryard to that
neighbor's threshing yard not drawn - feature 317's passage record, so the web, `unreached_houses` and the modal read it as they
read a passage. Canon: the GM, "it's okay for people to cut through neighbors' yards in a pinch"; the adjoining-land condition of
an ordinary passage (3 ft) does not bind it. Measured to be rare (prototype: 0-1 a map at 5 px with retries); every pinch is
counted in `meta.pinch_passages`.

**D14 - The record and the claims (FR-008).** 0081's drawing page: neighbors a lane's threading gap apart; no way searched while a
household is seated; the ways laid in the gaps once every house stands (the record's own reading, a GUESS, with Smith 1899 as
the nearest support for houses first and paths worn after - added to the question page only if `source-reader` confirms the
passage); the pinch. 0029's: nearer the field all else being equal. `Research:` claims of every changed unit re-checked by
impl-drift (`make claims-owed`).

## Verification

Unit tests for D1-D6 and D9-D13 (SC-007's gap between every two homesteads but a tight pair; SC-008's no-search test: the
homesteads stage calls no `access_corridor` or `routed_corridors` before the gap pass; the gap pass on a constructed row of
homesteads; the pinch on a constructed pocket) (the no-take-back test SC-001 counts houses during the seating; SC-002a's order; SC-003's constructed
refusal); `make done`; the cohort (`make cohort N=24`) and the pool against main; seed 18 and the 40-household bookend seeds on
their first margin (SC-002); the bookends (FR-010) with the spread (farthest house from the first and from the field, built
share) in research.md.

## Constitution Check

XII: every decision labeled (D2-D4 canon, the GM's rulings; D6 calibration reported). XIII/XIV: cohort and pool against main.
XVI: the literal request - every take-back removed, the reach removed with every use.
