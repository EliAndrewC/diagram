# Feature 297 - research

## R1. Where Inashiro's regeneration goes (observed 2026-09-30, session "Diagram performance")

Method: `make map GEN="--no-cache pool/hamlets/inashiro/inashiro.gen.py" PROFILE=1`, four runs, with scratch phase marks
(`_phase.mark()` deltas to stderr) around `generate`, `Settlement.finish` and `render_page`, and spans inside the threaded
renders; the marks were reverted after. Load 1.8-4.0 on 22 cores (observed 2026-09-30, method: the marks above). Regeneration 7.0-8.5 s (child, as REGENERATED reports it).

| part | seconds |
|---|---|
| stages (`build`) | 4.9-6.2 (field 1.25-1.4, homesteads 1.07-1.13, hinterland 1.0-1.6, web 0.82-0.87, windbreak 0.17-0.21, notice 0.12, track 0.11, woodland 0.07-0.09, appurtenances 0.06) |
| finish: beads, tree stands, blade groups | 0.113 |
| finish: labels, splices, svg write, ink census | 0.024 |
| page: drop_offmap 0.029, wrap 0.145, hit regions 0.115, svg join 0.005 | 0.294 |
| page: picture (resvg zoom 2 in 2x2 tiles 0.691 + JPEG child 0.488) and id map (recolor 0.051 + resvg 0.251) in two threads | 1.197 |
| page: explanations + json blob | 0.207 |
| PNG (resvg at the map's PNG width, a background thread joined at the end) | 0.462, hidden |
| json write, promote | 0.04 |
| child start, imports, cache store | ~0.35 |

The harness (`measure.py before`, base `c5a631f9b`, render off as the gate's policy requires; load recorded per key in
`measurements.json`) gives Inashiro's stages as 5.640 s summed, the fastest of three, and the pool's five rolls 26.705 s (`m:before-pool-roll-s`; a first run at load 1.2 read 4.281 s and 25.181 s - the keys hold the second, at load 6.4 -> 2.0, after the harness's callee names were corrected).
`make map` uncached, fastest of three: 8.0 s (`m:before-inashiro-regen-s`, load 2.5 -> 6.1).

## R2. The homestead seating's funnel (observed 2026-09-30)

Method: the manifest's own `meta.seat_search` counters, cProfile of the homesteads stage (`make perf-profile SEED=4
STAGE=homesteads` with the gen's full spec), and scratch counters in `access_corridor` (`r2-access-counters.patch`, reverted).

- 734 seats offered to `try_place` (254 by the lattice rounds, 480 by the exhaustive pass, which seated 7 of them).
- 902 parts tests (`_parts_fit`), behind 2,716 garden-side layouts built (`_bundle_geom`, four per seat).
- 477 corridor searches (`access_corridor`): 36 found a corridor; **348 found no candidate at all** (no door's strip to a tree
  target clears the house and the standing ground), 93 had candidates every one of which was refused, 4 candidates refused by
  the tree judge. The no-candidate verdict depends on the house's box and yard, the access tree and the standing ground - not on
  the garden side or the fixtures - and is asked after all four layouts are built.
- Cost shares (observed 2026-09-30, method: cProfile of the stage, relative only): the corridor search 42% of the stage, the layouts 34%, the threshing-yard mats 12%
  (15 yards), `seg_dist` 215k calls.

## R3. The hinterland's lookups (observed 2026-09-30, cProfile of the stage)

- Grass (`commons` -> `grass_scatter`) is already thrown and tested as arrays (feature 278) - region-then-fill in all but name.
- The marsh's `_throw` is per point in Python: 198,162 `random.uniform` draws on Inashiro, 19,408 `_sparse` tests.
- The village grove offers 15,605 candidate crowns to `static_clear` and asks `too_near` 28,980 times (6,267 crowns drawn).
- The open-ground search asks `_ok` 4,473 times, behind 10,819 crop-edge `edge_within` probes.
- `PointGrid.near` (indexes.py:264) 102,164 calls in the stage under cProfile (273,450 over the roll); the harness's whole-stage bucket counts it as `m:before-inashiro-b-hinterland-stage-pointgrid-near`.

## R4. The web (observed 2026-09-30)

`settle_the_web` is 73% of the stage under cProfile (observed 2026-09-30, method: `make perf-profile SEED=4 STAGE=web`); on Inashiro 12 of 15 houses are unreached when the settle starts (their
access corridors were reserved at seating and are drawn by `settle_reach`), the settle runs 4 rounds with 22 lane edits and
the last resort drops 1 lane (`meta.web_settle`). The last resort's re-sweeps (`lanes_breaking`, 4 calls) and `unsettled` are
39% of the stage profiled. Pool: rounds 3-6, changed 5-27, dropped 0-1.

## R5. The drain-bank hem (observed 2026-09-30)

12,195 `drain_bank_clearance` calls (`m:before-inashiro-b-hem-drain-bank-clearance`) = every vertex of every plot over three carves, each against every drain segment; ~0.07 s
real (observed 2026-09-30, method: cProfile's 0.184 s cumulative over its ~2.5x overhead). Not the field's cost (the three carves and `close_seams` are), but asked where no corner can be near the drain.

## R6. Why each seat offer fails (observed 2026-09-30, method: scratch counters at each refusal in `_place_bundle_nucleated` and `_parts_fit`, reverted)

Of Inashiro's 734 offers: 176 refused at the house's own box (`_house_box_refused`), 288 with every garden side's envelope
blocked (after the four layouts were built), 255 with at least one side reaching the part rules and every side failing, 15
seated. The part rules' refusals by rule, counted per side: the wood floor's seats covered (`wood.covers_a_seat`) 361, no corridor
to the access tree 441 (166 distinct searches - the four sides of a seat share one house and one yard, 558 of 558 seats measured,
so the corridor memo answers the other three), the sun rules 40, the field's reach 24, other rules 5. So 464 of the 734 offers are
refused by ground occupancy alone (the house box and the envelope) and most of the rest by the wood seats and the corridor -
each a question about WHERE the seat is, not about the homestead's parts.

## R7. What the settle's rounds change (observed 2026-09-30, method: scratch print of each step's change count per round, reverted)

- Inashiro: round 1 - `settle_reach` 15 (the access tree's lanes, judged lawful at seating, drawn only now), a squared crossing,
  a deferral, 2 network edits; round 2 - one end; round 3 - one shape, one network edit; round 4 - nothing. The rounds went still,
  but `unsettled` still named `dangling_ends`, so the last resort ran and dropped one ordinary lane.
- Sawada (the web stage ran twice in one regeneration): `settle_reach` 17 and 19 in round 1, then 1-3 edits a round (ends,
  fragments, `prune_the_tree`, widths) for 3 and 5 rounds.
- Kashikawa: 4 edits in round 1, one in round 2, still at round 3.

So almost all of the settle's edits are the access tree's lanes, which were lawful when the seating admitted them, plus a
handful of repairs to lanes laid earlier in the stage; yet every round asks all sixteen steps of the whole web, and the exit
asks the whole lane law again (`unsettled`), and a still round with one rule broken runs the whole last resort.

## R8. `make perf` failed on main, and the defect beneath it (observed 2026-10-01, method: `make perf` and `make hamlet` in `/tmp/base297`)

`make perf LABEL=297-start` raised `WebRefused` ("lanes 1 (skeleton) still break a rule of the lane law; the web still breaks
bends") on its first seed. The tool's `REFERENCE` spec says it is "Inashiro's own spec", but it had kept the unpinned spec after the
GM pinned Inashiro nucleated with its shrine (feature 291); its last green run (293-end, `cfd76e764`) predates feature 287's landing.
Fixed here: `REFERENCE` carries the gen's pins, and the bookend runs (297-start: 16.1 s total, median 4.2 s, worst 4.5 s).

The defect beneath it stands on main: the UNPINNED Inashiro spec at seed 4 is refused - by the web (`WebRefused`, bends on a
skeleton lane) through the perf tool, and at the wells (`OverlapRefused`: a well recorded on a house) through `make hamlet` (whose
spec differs by the CLI's defaults). The cohort's own seeds pass (30/30, `cohort-base.log`). Both refusals are in code this feature
rebuilds (the lane law, D; the seating, B1/C); each is re-rolled after its lever lands, and fixed here if it still refuses
(constitution XIV).

## R9. The layout template keyed per household - withdrawn (observed 2026-10-01, method: `make quick` with the key changed)

Plan C's second half keyed `_bundle_geom`'s template on the household (the k-th seated) instead of the seat each round offers it,
so a household's layout would be built once rather than per offer (2,261 builds for 734 offers on Inashiro). It broke the seating:
`test_a_seating_draws_a_well_at_every_pocket_it_laid` (seed 3) seated 9 of 10 households and refused its site, and a row of
seats at one pitch lost its fourth. The yard's area is a lognormal roll seeded by the seat's position (`_yard_area_ft2`), so
the per-seat rolls offered a household a different yard size at every seat - the seating's only way to fit a large-yard
household into a tight spot. Keyed once per household, a large-yard household had no seat. Withdrawn by measurement; the seat's
own questions (the first half of C) stand and do not depend on it.
