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
`make map` uncached, fastest of three: 8.0 s at load 2.5 -> 6.1 when first taken (observed 2026-09-30, method: `measure.py regen-before`); re-taken back to back with the clone at 6.1 s (`m:before-inashiro-regen-s`).

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
Fixed here: `REFERENCE` carries the gen's pins, and the bookend runs (297-start: 16.1 s total, median 4.2 s, worst 4.5 s; observed 2026-10-01, method: `make perf` in `/tmp/base297`, `dev/perf-log/20261001T040022Z-297-start-base297.json`).

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

## R10. Measuring by the wall clock, and what the first levers bought (observed 2026-10-01)

**cProfile misleads here** (observed 2026-10-01, method: cProfile and the sampler below on the same stage). It charges every Python call, so it over-weights call-heavy code and under-weights the C work
(shapely, numpy, PIL) the regions are made of: a lever that cut calls 30% under cProfile left the homesteads stage's wall time
unchanged. The stage times below are `make map PROFILE=1` best of three (`stagemin.sh` in the session's scratchpad), base
(`/tmp/base297`) and clone back to back; the shares are a wall-clock SAMPLER (a thread reading the main thread's stack every
millisecond, `sys.setswitchinterval(1e-4)` so plain Python is sampled fairly - at the default 5 ms the sample over-weights code
that releases the GIL).

- **The seat's corridor asked first ran the costliest search on every offered seat** (plan C as first written; observed 2026-10-01, method: `make perf-profile SEED=4 STAGE=homesteads` in both trees): the corridor
  search went from 166 distinct searches to 325 (`seat_reaches_tree` 0.48 s profiled against 0.35 s), because the cheap envelope
  test had been refusing most seats before it. Reordered: the field's reach and the water first, the envelope, then the corridor
  once per seat.
- **The regions' cost was shapely's buffers**, not the reads: the woodland region took the hinterland from 0.89 s to 1.16 s
  until every shape was painted with PIL's own primitives (a two-cell margin for PIL's wide-line placement); then 0.75 s.
- **The seat region's flood was PIL's `floodfill`, which is pure Python** (1.1 s profiled over nine fills); replaced by a
  run-length union-find of the free cells (0.09 s). A fill on an image that shares numpy's buffer paints nothing (PIL 12.3).
- **The access tree's lanes drawn first in the web (plan D2) made the web slower** on its own (Inashiro 0.72 -> 1.12 s,
  Kashikawa 0.6 -> 1.44 s, single runs): the web's thirty-odd passes then process the tree's lanes too, and the settle still
  runs its rounds. Reverted until the repairs move to the writes (D3).

## R11. Can the lanes be lawful as they are laid? (observed 2026-10-01, method: scratch taps at each `_pass` of `stage_web` on Inashiro, asking the rules of `law.LAW` of the web as it stood; and a tap at `last_resort`)

| after the pass | what the lane law finds broken |
|---|---|
| cut (the stage's start: the connector and the field spur) | one network short, 1 dangling end, 15 houses unreached |
| skeleton | one network short, 1 dangling end, 15 unreached |
| join-orphans | one network short, **2** dangling ends, 15 unreached |
| bridge-breaks | one network short, 1 dangling end, 12 unreached |
| touch | one network short, 1 dangling end, 12 unreached |
| bridge-breaks, join-orphans, smooth | 12 unreached |
| touch (the last construction pass) | 1 dangling end, 12 unreached |
| settle (its start) | 1 dangling end, 12 unreached |

Two findings:

- **The web is unlawful mid-construction by design.** It is in pieces until the touch passes join it, and ends dangle and are
  joined from pass to pass (2, then 1, then 0, then 1). A lane judged at its own write would be refused or reshaped before the
  pass that completes it ran. So plan D3-D4 as written (every lane lawful at its write, no repair after the web) cannot be built
  on the web's passes as they are; it would mean re-designing every construction pass to lay only complete, joined lanes.
  Asking the law at every pass boundary instead costs more than the settle it would replace (the whole law asked ten times).
- **What the settle actually mends on Inashiro is two things**: the 12 farmhouses whose access corridors (judged lawful at
  seating) are drawn only by the settle, and one dangling two-point skeleton lane. Yet it spent four rounds of all sixteen steps,
  the whole law re-asked at the exit, and the last resort (which dropped that lane): 0.5 s of the stage's 0.72 s (observed 2026-10-01, method: the R10 sampler on `stage_web`). The lane
  dangled through every round because `settle_dangling` never dropped a lane its trim could not shorten - though its docstring
  said "a lane the law still calls dangling after its trim goes whole". Fixed; the last resort no longer runs on Inashiro.

What was built in its place: the law's pure verdicts kept per lane (`ways/keeper.py`), a later round running only the repairs
for the rules still broken (`STEP_RULES`, `steps_for`), the exit reusing the last answer when nothing changed, and the
`settle_dangling` fix. Inashiro's web stage 0.72 -> 0.41 s, Sawada's about even (0.46 / 0.50) (observed 2026-10-01, method: `make map PROFILE=1` single runs and `stagemin.sh` best of three, R10).

## R12. The targeted settle rounds, measured and withdrawn (observed 2026-10-01, method: `stagemin.sh` best of three, the same engine but the settle loop, back to back, load 3.2-3.8)

| web stage (observed 2026-10-01, method: `stagemin.sh`) | full rounds (every step every round, the law asked once at the exit) | targeted (the law asked after each round, only its rules' steps run) |
|---|---|---|
| Inashiro | 0.40 s | 0.45 s |
| Sawada | 0.51 s | 0.60 s |
| Kashikawa | 1.22 s | 1.14 s |

Asking the whole law after every round costs more than the steps it lets a round skip: on Sawada the law bucket's calls rose
from 456,889 to 1,521,541 (observed 2026-10-01, method: `measure.py after` on the targeted engine, since re-run on the final engine whose figure the `after-` key holds). Withdrawn: the settle runs its rounds
as before. What made Inashiro's web faster is the keeper (`keeper.kept`) and the `settle_dangling` fix that stops the last resort
from running there (R11), both kept.

## R13. The pool and the cohort after the levers (observed 2026-10-01)

Each pool map's houses, field acreage, lanes (count and length), wells, grove crowns and marshes are the same as the base's on all
five maps (method: the manifests of `/tmp/base297` HEAD against the clone's regenerated pool). What moved is the threshing yards'
mats (the fill) and the scatter's marks (the marsh's array throws and the regions' margins). `make cohort N=24`: 30/30 passed the
whole gate, as the base's (`cohort-base.log`) - and again on the final engine after B3's grove (`cohort-after.log`).

## R14. Plan D2-D4 built as specified, and measured (observed 2026-10-01, method: scratch harnesses run as test nodes over the five pool maps and cohort seeds 1-24, `build` through `stage_web`, the same session and load 1.4-2.1)

First built at the PASS boundary (the review of Amendment 1 round 2 rightly said this is not D3 as written; the per-write build
follows): **D2**, the access tree's lanes drawn before the skeleton; **D3**, every lane-and-joint
repair (`settle_husks`, `square_every_crossing`, `settle_shapes`, `settle_ends` with the dangling trim, `settle_joins`,
`settle_needles`, `settle_defer`, `settle_widths`) applied at each pass boundary of `stage_web` - the write unit at which the passes
hand the web on - and once more after the last pass; **D4**, no settle rounds and no last resort: the tree's owed lanes drawn
again where a repair cut one, then the whole law asked ONCE, and any break counted as a refusal (`WebRefused`), dangling ends in
the class judged at the end as the review asked.

| (observed 2026-10-01, method: the R14 harnesses) | the shipping settle | D2-D4 as built |
|---|---|---|
| webs refused (of the 23 that draw one; 6 dispersed draw none) | 0 | **10** - Inashiro and Sawada among them (needle joins 2-8, doubled tails 1-4, networks, fragments, dangling ends, one house unreached) |
| the web stage, summed over the 29 specs | 14.30 s | 19.73 s |

Without any repair (D4 alone, the tree's lanes drawn last) 20 of the 23 webs end broken - needle joins, doubled tails, width steps,
needle loops, oblique crossings, fragments: per-lane and joint rules, not only the network-wide ones. With the repairs at each
pass, the repairs themselves lay new breaks the next pass does not see (a needle cut opens a tail; a tree lane drawn first is met by
the next pass's lanes as a needle). Withdrawn under the plan's own rule - both slower and failing the gate - and the settle stays.

**D3 AT THE WRITE, as plan D3 states it** (observed 2026-10-01, method: the same harnesses, the hook on every lane write -
`lane`, `reshape_lane`, `reink_lane` (which the in-place `pts` edits call) and `drop_lanes` - running ALL THIRTEEN repairs of the
settle (`square_every_crossing`, `settle_shapes`, `settle_way_outs`, `settle_ends`, `settle_street_ends`, `settle_shadows`,
`settle_joins`, `settle_needles`, `settle_defer`, `settle_network`, `settle_fragments`, `prune_the_tree`, `settle_widths`, with the
husks) to a fixpoint after each write, a repair's own writes folded into that fixpoint; the tree's lanes first (D2); dangling ends
left to the end; no settle - the law asked once): **21 of the 29 specs end broken or unreached and one raises** (Sawada: an
`IndexError` - a repair at the write took a lane out from under the pass that was iterating the lanes); 1 web clean (the six
dispersed draw none). Unreached houses return on eleven maps: the network and fragment repairs and `prune_the_tree`, asked of a web
still being built, take away lanes - the tree's among them - that a later pass would have joined to. The web stage summed 15.29 s
against the shipping settle's 14.30 s (120 to 136 writes and 266 to 784 repair-step runs a web). Withdrawn under the plan's rule:
it fails the gate.

## R15. The seat region with the seated homesteads painted, measured (observed 2026-10-01, method: a scratch toggle painting each seated homestead's box into the buildable raster; the five pool maps and cohort seeds 1-24 built through `stage_homesteads`, back to back)

| (observed 2026-10-01, method: R15's toggle) | homesteads not painted (as built) | every seated homestead's box painted |
|---|---|---|
| households seated | 442 of 442, none refused | 442 of 442, none refused |
| placer calls | 4,712 | 4,054 |
| the homesteads stage, summed | 51.31 s | 56.01 s |

Painted (observed 2026-10-01, method: R15's toggle), the region offers fewer seats the placer then refuses, but repainting the raster and rebuilding its table after every
house costs more than those calls (9% slower). Not painted, under the plan's rule. (The first cut of the region seated no one on
Inashiro for a different reason - FreeGround's cells painted grown on an offset grid over-refused the static ground - and that was
fixed by painting them exactly on FreeGround's own grid; the spec's "painted, Inashiro seated no one" misattributed it.)

**D3 at the write AS PLAN D1-D4 STATE IT** (observed 2026-10-01, the review's round 3; method: the same harness, the hook firing
only at the OUTERMOST write - `drop_lanes` re-inks lanes inside its own loop, and mending there raised the first build's
`IndexError`, a harness bug, fixed - running the lane-and-joint repairs (`square_every_crossing`, `settle_shapes`, `settle_ends`,
`settle_street_ends`, `settle_shadows`, `settle_joins`, `settle_needles`, `settle_defer`, `settle_widths`, the husks) to a fixpoint
after each write; the NETWORK-WIDE repairs (`settle_way_outs`, `settle_network`, `settle_fragments`, `prune_the_tree`) held to the
end with the tree's owed lanes, as D1 and D4 state; dangling ends judged at the end; no rounds, no last resort, the law asked once):
**16 of 22 webs ended broken or with houses unreached, 2 raised, 4 clean** (the six dispersed and one with no web draw none), and the
web stage summed **24.59 s against 14.30 s** (1.72x slower). The two that raise are the construction passes themselves: they walk
the lane list by index (`for i, ln in enumerate(lanes)` with edits behind them) while a repair at the write drops lanes from under
them - not a harness bug, and making it go away means re-writing those passes, an overhaul. Withdrawn under the plan's rule: slower,
and failing the gate after the one fixable failure (the harness's nested hook) was fixed.

## R16. The grove decided by its regions alone (observed 2026-10-01, method: `stagemin.sh` best of three on Inashiro, a detached worktree of HEAD (the prefilter form) and the clone back to back; the pool's crowns read from the regenerated manifests)

Plan B3 as the plan review asked: three regions by family (the hard edges, the lanes, the local obstacles) and NO exact family
asked in turn - `taken_by` says which family holds a clump's ground, and that decides drop or re-seat.

| (observed 2026-10-01, method: `stagemin.sh`) | the prefilter form (exact families where the region reads taken) | the regions alone |
|---|---|---|
| Inashiro's hinterland, windbreak | 0.87 s, 0.16 s | 0.83 s, 0.14 s |
| grove crowns: Inashiro, Kuwabata, Sawada | 661, 632, 693 | 569, 522, 598 (-14% to -17%) |

Faster by about 0.06 s a map (observed 2026-10-01, method: the table's runs), and the belts and copses lose a sixth of their crowns: the two-cell margin of every keep-out refuses
the clumps that stood at its edge. Kept if the gate holds every grove rule on the moved pool (the belt deep and whole, the copse's
stocking, a household's reserved wood share); withdrawn by its own measurement if not. **Withdrawn**: the gate failed woods W25
(`test_the_belt_leaves_a_reserved_seat_free_and_the_copse_plants_it`, `test_a_reserved_seat_moved_round_another_groves_crown_is_asked_its_reach_again`)
- the margin round the belt's crowns covered a household's reserved seat the seating had proved clear, and the copse dropped it.
The fix is to ask the exact families for a reserved seat only (below).

**The regions alone for every ordinary clump, the exact families for a reserved seat** (observed 2026-10-01, the plan review's
round 4; method: `stagemin.sh` best of three on Inashiro, the prefilter worktree and the clone back to back, load 0.8 -> 1.0): the
gate's two W25 failures were both reserved seats, so the reserved seat and its re-seat are asked of the exact families
(`GroveBlocks.exact_taken_by`) and every other clump reads the regions alone (`taken_by`). Inashiro's hinterland 0.84 s and
windbreak 0.16 s in both forms - no faster, and no slower; the pool's crowns 624, 586 and 659 on Inashiro, Kuwabata and Sawada
(661, 632, 693 in the prefilter form). Kept as the plan states B3: the gate held every grove rule on the moved pool (green, 2026-10-01).

## R17. The hinterland's remaining 43,856 lookups (observed 2026-10-01, the GM: "Why do we still hvae 43,856 hinerland lookups? That still seems really high, doesn't it?"; method: the callers of `PointGrid.near` in `/tmp/m297/after/inashiro.prof`, and R10's sampler on `stage_hinterland`)

What they are: ~26,000 are the village grove's crown spacing (`Seats.too_near`: each candidate crown against the crowns already
planted - a question about the crowns placed so far, which no region painted beforehand can answer); ~13,000 the windbreak belt
measuring its own band's edge (`belt.py`); ~4,000 the commons' brush dots (`cover._sparse`); ~2,000 the woodland search's field
height. What they cost (observed 2026-10-01, method: R10's sampler): all of `PointGrid.near` is 3.7% of the stage's wall time, about 0.03 s of 0.86 s - each is an array read of
a few microseconds. The stage's time is elsewhere: the grass scatter 23% (its throws and their strings), the village grove 24%, the
woodland search's region 22%, the marsh 9%.

Tried: the woodland search reading ONE region per pair of set-backs by its square's box (as plan B4 first wrote it) instead of one
region per size by its center (observed 2026-10-01, method: `stagemin.sh`) - the stage 0.82 -> 0.81 s, and two tests failed (the square's corners stricter than the center's
reach moved a parcel off the brook line its lot follows, and a parcel past its size band). Not kept.
