# Research: seat by packing

## R1. Prototype round 1: capacity by packing boxes (observed 2026-10-02, method: `prototype.py observe 40 47,25` - the engine's own seating, with the prediction computed where the exhaustive pass starts and logged beside what the margin seated)

(Observed 2026-10-02, method: as the heading.) The prediction - the households standing plus a greedy pack of the smallest
homestead envelope over the seats the exhaustive pass would offer, on the seat region's raster with every standing box painted
- is 213-305 on every margin of seeds 47 and 25 at 40 households, where the margins seat 15-40:

| seed 47, per margin | seated before the pass | predicted | seated |
|---|---|---|---|
| 16 margins | 11-18 | 220-305 | 15, 18, 20-33, 38, 40 (the 16th) |

**So the free ground is not what fills** (observed 2026-10-02, method: the same run). Within the field's reach the ground holds two hundred-odd homestead boxes; the
placer refuses most seats on it for other reasons. A pack of boxes cannot predict a margin's capacity; whatever limits it is a
rule the placer asks of a seat (R2 measures which). Predicting took 0.41 s over seed 47's sixteen margins (the same run).

## R2. What refuses the placer's offers (observed 2026-10-02, method: a scratch census wrapping each of the placer's questions, the first refusing one per call, through `stage_homesteads` at 40 households, seed 47)

(Observed 2026-10-02, method: as the heading.) Of ~25,000 placer calls over seed 47's sixteen margins, the first refusal:

| phase, first refusal | calls |
|---|---|
| exhaustive pass: no straight corridor from any door to the access tree (`seat_reaches_tree`) | 13,391 |
| exhaustive pass: no garden side's envelope fits | 2,568 |
| exhaustive pass: the part rules, the corridor among them (`access_corridor`) | 2,110 + 2,321 |
| exhaustive pass: a reserved wood-floor seat covered (`covers_a_seat`) | 706 |
| lattice rounds: no corridor / no envelope / part rules | 801 / 687 / 873 |
| seated | 249 (lattice) + the exhaustive pass's |

Per garden side, `access_corridor` refuses 8,570 times in the exhaustive pass and the wood seats 2,507. **The cap on a margin is
reachability**: each house needs a straight corridor from its door to the tree, clear of every homestead, part and wood seat,
and a cluster filling in blocks the lines its later seats would need. The 213-305 boxes of R1 are free ground no corridor reaches.

## R3. Rounds 2 and 3, and a wider corridor search: the search order is not the cap (observed 2026-10-02, method: `prototype.py tree|grow 40 4,...`, and `TARGETS_TRIED` raised by monkeypatch, the reference at 40 households)

(Observed 2026-10-02, method: as the heading.)

- **Round 2, seats beside the tree** (both sides of every leg at 0.55/0.8/1.05 pitches, every half pitch): seed 4 tried all 55
  margins, seating 10-32 each, and was refused. The offers fell on the legs' own strips (the house box refused 9,405 times), past
  the field's reach (5,811) and on neighbors' envelopes (10,722).
- **Round 3, seats grown from the houses** (each standing envelope's eight neighbor positions, nearest the center first): seed
  4 again all 55 margins, 10-28 each - the neighbor positions are taken by reserved corridors, wood seats and envelopes.
- **The corridor search widened** (observed 2026-10-02, method: the probe with `TARGETS_TRIED` set; `TARGETS_TRIED` 12 -> 30 / 80, a search breadth, not a rule): the margin that succeeds moves
  (seed 4 rung 3 / 1, seed 39 rung 7 / 4, seed 47 rung 10 / 2) and each call costs more (seed 25 10.9 / 21.8 s against 8.3).
  Whether a margin reaches 40 is near chance: 40 households is about what an unplanned cluster with straight corridors holds.

## R4. Round 4: frontage lanes laid first (observed 2026-10-02, method: `prototype.py` modes `lanes` and `comb` with the front row and lattice rounds disabled, the fallback to the exhaustive pass off, the reference at 40 households, seeds 4 and 47, three margins)

(Observed 2026-10-02, method: as the heading.) Lanes laid as legs of the access tree before the houses, homesteads offered along
them: a spine from the strip's end with lanes across it seated 1-5 a margin until each leg was put to the tree's own test
(`tree.admits`, oriented toward the tree as a corridor is) - the spine is a corner at the strip's end the lane law refuses, so no
lane was laid; lanes as T-junctions along the exit strip seated 2-5 (the strip runs away from the field, past its reach). Every
lane the law admits is reserved ground a house may not stand on; laying a village's streets is a layout of its own (the
village tier's), not a seat order. Withdrawn.

## R5. Round 5: a failing margin's exhaustive pass given up after a dry spell (observed 2026-10-02, method: `prototype.py takes`, each take's offer index logged, then `DRY=400`, the reference at 40 households, four seeds)

(Observed 2026-10-02, method: as the heading.) On a margin that falls short the pass seats its last house by offer 128-1,206 and
offers on to 1,015-1,742; on the margins that succeeded the longest run of offers without a take was 327 (seed 47) and 235 (seed
39). Giving a margin up after 400 dry offers kept every seed's margin and seated count and cut the stage: seed 4 6.2 -> 4.8 s,
25 7.8 -> 6.8, 39 10.1 -> 8.3, 47 50.0 -> 39.9. A heuristic: a margin whose next take lies past 400 dry offers is given up.

## R6. Round 6: the band holds the homestead's whole ground, and a near miss is rescued (observed 2026-10-02, method: `HOMESTEAD_GROUND_FT` set by monkeypatch, `prototype.py rescue` with `RESCUE=3` and `DRY=400`, the reference at 40 households)

(Observed 2026-10-02, method: as the heading.) Seed 47's margins seat 38-39 of 40 and are thrown away. Two levers:

- **The band's ground per household** (observed 2026-10-02, method: the pool's five manifests read for `geom.bbox`). `HOMESTEAD_GROUND_FT = 104` sizes the seat band from the house, yard and row (consts.py);
  it leaves out the household's wood floor (`HOMESTEAD_WOOD_FT2`, 6,000 sq ft at least, within 90 ft of the house), added later.
  The pool's 82 homesteads' envelopes (`geom.bbox`): median 10,521 sq ft, mean 20,366; with the wood floor's least, a homestead's
  ground is sqrt(16,521) = 128.5 ft (median) to sqrt(26,366) = 162.4 ft (mean).
- **The rescue**: a margin left at most three short is searched again before the ladder moves on - the seat grid at a sixth of
  a pitch (the pass's is a third) and the corridor search over 40 tree points (12 in the pass); a search breadth, no rule.

| homesteads s (margins) at 40 hh | seed 4 | seed 25 | seed 39 | seed 47 |
|---|---|---|---|---|
| the engine (104) | 6.2 (2) | 7.8 (3) | 10.1 (4) | 50.0 (16) |
| 104 + rescue + dry | 4.8 (2) | 6.8 (3) | 8.3 (4) | 30.5 (12) |
| 128 + rescue + dry | 3.8 (1) | 1.7 (1) | 10.6 (5) | 7.4 (3) |
| 140 + rescue + dry | 3.0 (1) | 3.0 (1) | 2.0 (1) | 5.9 (2) |
| 162 + rescue + dry | 2.9 (1) | 3.7 (1) | 2.0 (1) | 17.1 (3) |

Four seeds do not separate a figure from luck (which margin fills is near chance at the edge of capacity); a twelve-seed sweep
follows (R7).

## R7. The band's figure swept, and its rim (observed 2026-10-02, method: `rim.py` - the probe with `HOMESTEAD_GROUND_FT` set and, for `rim`, the shared sheds' pockets laid farthest from the band's middle - the reference at 40 households, run as four or six processes at once, so the seconds are a loaded machine's)

(Observed 2026-10-02, method: as the heading.) Twelve seeds (1-13 but 4) at 40 households, margins seated before every household
stood: the engine (104) seated on the first margin on 1 seed of 12 (2.9-118 s, seed 7 crashed - see R8); 128 with the rescue on
4; 140 with the rescue on 7; **162 with the rescue on 11** (2.2-5.5 s). 162 ALONE (no rescue, no dry cap), sixteen seeds (1-13,
25, 39, 47): fifteen on the first or second margin in 1.9-6.1 s, seed 47 on the seventh in 23.5 s; at 15 households the four
reference seeds 0.5-1.0 s against 1.0-1.3 s at 104, at 20 households 1.0-1.4 s against 1.0-5.7 s. Seeds 1-32 at 162 (but 4,
25): 20 on the first margin, 8 on the second, 1 on the third, 1 on the fourth; seed 28 is refused by the field (`FieldRefused`,
52 acres). The shared sheds laid at the band's rim instead of spread: no better (seeds 3 and 7 worse, 24 better) - withdrawn;
the round-3 seats grown from the houses at 162: worse on three of four seeds - withdrawn.

## R8. A crash the scaling leg found (observed 2026-10-02, method: the R7 sweep at 104, seed 7, 40 households; the traceback)

(Observed 2026-10-02, method: as the heading.) `waterfields/partition.region_rings` read `.exterior` of every part of the
planted region; the difference that makes it (`planted_region`) left a sliver LineString where the water's edge ran along the
envelope's, and the fit raised `AttributeError`. A line plants nothing: only the region's polygons are rings now
(`tests/waterfields/test_partition.py::test_a_sliver_line_in_the_region_is_not_a_ring`). Constitution XIV.

## R10. The overlap census, calibrated (observed 2026-10-02, method: a scratch census - `sys.monitoring` on the geometry primitives, each comparison charged to the nearest named function outside `settlement/_geom/`, its calls counted from its first comparison - over the five pool hamlets' specs and the reference at 40 households, seed 4)

(Observed 2026-10-02, method: as the heading.) Comparisons per call of the checks a roll runs: nine over 5,000 -
`ways/touch._clear_of_fabric` 111,700 (one call, the web), `ways/dry_exit._blocked_cells` 101,229 (the track),
`cluster.seat_cluster` 30,604 (the seat), `city/bridges.bridges` 16,190, `homestead_parts/groves._belt_ranks` 15,005,
`fields/comb._comb_record_field` 12,263, `ways/street.street_span` 6,394, `city/bridges.channel_footbridges` 5,485,
`water/polder.dike_gaps_at_channels` 5,048; the next below at 3,859 (`ways/serve._lay_web_lane`), the bulk under 1,500. The flag
is set at the knee, 5,000.

## R9. The rescue and the dry cap on top of the band's figure (observed 2026-10-02, method: `rim.py` with `HOMESTEAD_GROUND_FT=162`, `MODE=base` against `MODE=rescue RESCUE=3 DRY=400`, sixteen seeds (1-13, 25, 39, 47) at 40 households, two processes at once)

(Observed 2026-10-02, method: as the heading.) Summed homesteads seconds: 92.7 (the figure alone) -> 72.2 (with both). Every seed
seated all 40; the rescue saved a margin on seeds 6 (2 -> 1), 25 (2 -> 1) and 47 (7 -> 3; 37.0 -> 22.8 s); no seed slower
beyond 0.15 s. **GO: both are built** (plan D2).

## R11. The band's figure in the engine: the canvas kept, and what it buys (observed 2026-10-02, method: the clone's engine with `HOMESTEAD_GROUND_FT = 162` and the dry cap and rescue (plan D1, D2); `make cohort N=24`, `make maps SCOPE=all`; the 40-household probe `rim.py MODE=base` over sixteen seeds)

(Observed 2026-10-02, method: as the heading.) With 162 also sizing the canvas's room for the seat (`seat_room`), every canvas grew
and every field was re-fitted: the cohort fell from 30/30 (the base, `/tmp/base306`) to 27/30 - seed 18 seated 8-13 of 15 on
all sixteen margins, seed 19's dispersed farms lost their channels (`farm_without_its_channel` x10), the linear pinned seed 903
was refused by the web - and Sawada was refused (`WebRefused`, its field way's doubled tail). With the canvas's room sized as
before (`plan.SEAT_ROOM_GROUND_FT = 104`) and the band at 162: the cohort 29/30 (seed 903 still refused - lane 2, the skeleton,
`bends`), the pool clean, and at 40 households fifteen of sixteen seeds seat on the FIRST margin (seed 47 3.6 s, from 50.0 on
the base engine; seed 12 the outlier, eleven margins, 31.9 s), 94.9 s summed over the sixteen.

## R12. The seating's band apart from the margin's (observed 2026-10-02, method: the clone's engine; `make cohort N=24`, `make map` per pool gen, `make test-file FILE=tests/hamletgen`, the 40-household probe over sixteen seeds)

(Observed 2026-10-02, method: as the heading.) R11's variant - the band at 162 for everything but the canvas's room - leaves a
band longer than the canvas holds with its windward belt: `test_the_canvas_holds_the_seat_and_its_belt_on_the_windward_side`
failed for every wind (the belt's room is a band-depth and more upwind of the band's fringe, so a 162 band needs a 162 room),
and growing the room (R11's first form) re-fitted every field. Isolated: the canvas grown with the band left at 104 made 40
households WORSE (seed 39: 42 margins, 216 s) - the win is the seating's spread, not the room. So the seating's band is its own
figure (`consts.SEATING_GROUND_FT = 162`, `_seat_households`' lattice and seat bound), and the margin, the canvas and the belt keep
`HOMESTEAD_GROUND_FT`'s 104 - every canvas, field and margin as the base drew it. At 40 households: 11 of 16 seeds on the first
margin, the worst 14.1 s, 84.2 s summed (the base engine about 449 s over the same seeds, R7's sweep and the spec's Context);
the cohort 30/30; the pool: Inashiro refused by the web (an access lane, `needle_joins`) and Sawada failing the pool test of two
ways side by side past a pitch - each sent to its root cause (R13).

## R13. The nine flagged checks indexed, and the census after (observed 2026-10-02, method: three background agents in worktrees, each check against its old scan kept as the oracle, `make maps SCOPE=all` with the pool manifests compared; then `make census` on the clone's engine)

(Observed 2026-10-02, method: as the heading.) Every fix exact - byte-identical pool manifests, an equivalence test with the old
scan as its oracle, red when the index drops a candidate:

| check (observed 2026-10-02, method: the agents' alternated runs) | comparisons a call, before -> after | its own time, before -> after |
|---|---|---|
| `ways/touch._clear_of_fabric` | 111,700 -> 69 | 103-128 ms -> 3.0-3.5 ms |
| `ways/dry_exit._blocked_cells` | 101,229 -> 5,485 (the exact deciding tests left) | 1.4-2.8 s -> 0.07-0.09 s; Sawada's seat stage 1.1-1.9 -> 0.09-0.12 s |
| `cluster.seat_cluster` | 30,604 -> 572 | 2.0 s -> 0.13-0.18 s (mostly the raster above) |
| `city/bridges.bridges` | 16,190 -> 8 | 0.061 -> 0.027 s |
| `homestead_parts/groves._belt_ranks` | 15,005 -> 1,196 | 0.071 -> 0.047 s |
| `fields/comb._comb_record_field` | 12,263 -> 174 | 0.122 -> 0.065 s |
| `ways/street.street_span` | 6,394 -> ~472 | 15.6 -> 2.0 ms (a `PointGrid` was slower; boxes of 16 segments) |
| `city/bridges.channel_footbridges` | 5,485 -> 6 | 0.206 -> 0.054 s |
| `water/polder.dike_gaps_at_channels` | 5,048 -> 51 | 2-3 -> ~1 ms |

The census on the clone's engine afterwards (the pool and the reference at 40, shapely's predicates counted): **no check over
5,000**; the largest 2,624 (`ways/street.joints_along`), 2,137 (`_blocked_cells`), 1,989 (`web.tidy_lane_ends`).

## R14. The pool's two regressions under the seating's band, at their causes (observed 2026-10-02, method: a background agent in its own worktree; `make map` per gen, `make test-file FILE=tests/hamletgen/test_pool_261.py`, `make maps SCOPE=all`, `make cohort N=24`)

(Observed 2026-10-02, method: as the heading.) **Inashiro** (`WebRefused`, an access lane's `needle_joins`): the seating judged the
tree with corridors hung from the exit strip at one point; the web's touch pass later moved the connector's start 2.6 ft along the
strip, and `tree.lanes_of` moved each corridor end onto that start - turning a 355 ft leg a third of a degree, so a second corridor
hung from it met it at 19.95 degrees where the seating had judged 20.26: a needle no settle may cut (both tree lanes). Fixed:
`lanes_of` leaves a corridor end already on the connector's tread where the seating judged it. **Sawada** (two ways side by side
past a pitch): an ordinary join lane ran 105 ft within 30 ft of the exit strip and was the only way to one farmhouse, whose own
reserved corridor was never drawn because the stray lane reached the house first; `settle_shadows` keeps a shadowing lane the
network needs. Fixed: `tree.left_to_the_tree` lets it drop such a lane where the houses it leaves unreached have reserved
corridors, which the settle then draws. Two tests in `tests/hamletgen/ways/test_tree.py`. With both, and the row street's inside
corner rounded (the earlier seed-903 fix, `homesteads/rows.py`): the pool clean, `test_pool_261.py` 31/31, the cohort 30/30.
