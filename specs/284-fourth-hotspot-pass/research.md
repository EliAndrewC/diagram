# Feature 284 - research

## R1 - The measurement (2026-09-28, main `5f15c65bd`: 281 and 282 landed; first taken at `f52ed6aa8`)

**Method.** `measure.py before`, in the detached worktree `/tmp/base284`: each pool hamlet rolled three times unprofiled
with every stage timed (the fastest kept), once writing its svg and page, once under cProfile (saved to
`/tmp/m284/before`), and once under `sys.monitoring` counting every call beneath each mechanism's entry functions
(281's buckets plus this pass's: `router`, `field`, `notice`, `bamboo`, `page`, `edge_scan`). The load is recorded at each
run's start and end. Every figure is in `measurements.json` as a `before-*` key.

**The roll.** The five pool hamlets take 32.168 s between them (m:before-pool-roll-s, load 3.1 -> 7.8), at `5f15c65bd`. At
`f52ed6aa8`, before main merged feature 282, they took 27.62 s at load 3.7 -> 3.2 (observed 2026-09-28, method: `measure.py
before` in that worktree) - the difference is the threshing yards' mats (R3). By stage, summed over the five: the
field is the largest, then the ways (`stage_web`), the hinterland, the homesteads, the windbreak and the notice board.
Sawada's field alone is 2.939 s (m:before-sawada-stage-field-s) and Kashikawa's ways 1.448 s
(m:before-kashikawa-stage-web-s).

**The profile, by lever** (profiled seconds summed over the five; profiling inflates Python about 2.4 times, so these
rank, they do not predict):

- **The router** (`_route`): Dijkstra's lazy cell tests and heap (`is_free`, `in_band`, the heap: about 5 s), the
  string-pull's link tests (`_clear_link` from `_route`: 2.5 s) and the fabric-index memo KEY rebuilt per link (`_key`,
  3,768 builds, 1 s) though every link of one route asks the same index. The bucket's calls: m:before-kashikawa-b-router-total,
  m:before-sawada-b-router-total. Dijkstra settles every cell nearer the start than the goal; a search toward the goal
  settles a fraction of them and returns a path of the same cost - where two routes cost the same, possibly the other one.
- **The field's size search** (`fit_field`): 13 carves over the four comb fields (Inashiro and Sawada 4 each,
  m:before-inashiro-b-field-carve-comb, m:before-sawada-b-field-carve-comb). A trace of every carve (observed 2026-09-28,
  method: a probe wrapping `carve_comb` and `_fit_at_aspect` on the four rolls) shows the shape: on Inashiro, Kashikawa and
  Sawada the first guess falls short, and the search then carves the LARGEST fan the aspect can draw (feature 145's
  saturation probe, the multiplier at the bracket's top - Inashiro's fall 2727 px against a first guess of 1240) before
  converging on a predicted size. That probe is the costliest carve of the search and lands nowhere near the target; it
  exists for a fan the envelope clamps (cohort seed 47), which the carve after it can detect by its acreage not growing.
  The seam closing (`close_seams`: 5.3 s over four) and the carve's own geometry are the rest.
- **The page writer** (`write_html`: 7.1 s): every classed record string is parsed by regex to cull its off-map ink
  (`drop_offmap`, 1.9 s), parsed again to merge its primitives (`wrap` -> `merge_primitives`, 3.1 s), again for the marks'
  hit regions (`marks_region`, 1.3 s) and again for the widened hit layer. The same text, the same elements, four parses.
- **The notice board** (`place_kosatsuba`): every candidate verge seat is fitted and its caption placed before the seats
  are compared - m:before-inashiro-b-notice-total, m:before-sawada-b-notice-total.
- **The bamboo seats** (`bamboo_seats`): the samples it tests per seat - m:before-kashikawa-b-bamboo-total,
  m:before-mizuguchi-b-bamboo-total.
- **Whole-ring `edge_dist`** (`_crosses_fabric`, `_trim_to_service`, `push_clear_of_fabric`): each walks every edge of every
  fabric polygon per point - m:before-kashikawa-b-edge-scan-total, m:before-kuwabata-b-edge-scan-total.
- **The brook toll**: after 281's 3 x 3 grid, still 590,253 cell lookups on Kashikawa (m:before-kashikawa-b-toll-dict-get).

- **Four more slow stages with no lever yet** (the GM's general instruction takes them in, FR-011; a fifth, the threshing
  yards' mats, arrived with the re-base - R3), each bucket counted
  apart since buckets nest exclusively: the windbreak's fill and its draw (m:before-kashikawa-b-grove-total,
  m:before-kashikawa-b-grove-draw-total - the draw's crown test walks every nearby and every drawn crown per crown, 713,438
  comparisons over the pool in the profile), the seam closing (m:before-sawada-b-seams-total - shapely unions and buffers
  in `_absorb` and `_plant`, already batched by 276), the commons' scatter (m:before-kashikawa-b-commons-total) and the
  finish's blade flush (m:before-sawada-b-flush-total - every blade formatted to a path, which the page then re-parses).

**What the GM allowed** (request.md): a lane taking the other of two equally short routes, plot boundaries shifting within
the field's acreage tolerance (`fit_field`'s `tolerance`), a tied board seat resolving the other way, bamboo clumps sitting a little differently -
and in general any change of that nature that makes a map significantly faster. Not a change to what a settlement is,
and not a broken rule.

## R2 - Where the page's parsing goes, by class (2026-09-28)

**Method** (observed 2026-09-28, method: a probe timing the page's `wrap`, `drop_offmap` and `marks_region` per call and
attributing each to its string's feature class, over one full generate of Kashikawa and one of Sawada): 1.597 s of parsing
in all. The scrub and rough grazing took 41.4% (10,971 elements, 4.2 million characters), the marsh 18.5% - the two classes
whose ink is the deferred blade and mark buckets the finish flattens (`_blade_groups`, `_mark_groups`). The page's own
`marks_region` - the scrub's hit region, drawn from the scrub's marks (`HIT_FROM_MARKS` holds only the scrub) - took
another 23.2% (a probe attributing by string identity missed it, since that pass reads the marks by list; the review's
re-measurement placed it, observed 2026-09-28, method: a probe timing `marks_region` itself). No other class took more than 5.0%: the
bunds 5.0%, the paddies 3.0%, the windbreak 1.9%, the bund beans 1.3%, every other class under 1%, together about 17%. So the two
structured classes hold about 83% of the page's parsing in all (41.4 + 18.5 + 23.2), and carrying the structures the
engine already makes to the page reaches that, and what is left is spread
thin over every other producer - which one parse per string covers without rewriting each producer's drawing code.

## R3 - The threshing yards, after main merged feature 282 (2026-09-28)

Main merged feature 282 (the threshing yard's mats and racks) while this work was specified, and every pool manifest moved,
so the base was re-taken at `5f15c65bd`. The homesteads stage went from 0.357 s to 1.806 s on Inashiro (m:before-inashiro-stage-homesteads-s), 0.496 s to
2.313 s on Kashikawa (m:before-kashikawa-stage-homesteads-s) and 0.497 s to 1.859 s on Sawada
(m:before-sawada-stage-homesteads-s) - the first figure each from the `f52ed6aa8` run (observed 2026-09-28, method:
`measure.py before` in that worktree). Kashikawa's mats bucket counts 14288475 calls (m:before-kashikawa-b-mats-total). The profile names it (observed 2026-09-28, method: R1's saved profiles in `/tmp/m284/before`): `mat_cells` took 16 profiled
seconds over the 54 yards of Inashiro, Kashikawa and Sawada (5.01 + 6.21 + 4.82), about 4 million `hypot` calls of its own
(987,053 `edge_dist` calls from `yards.py`, one `seg_dist` per edge of the quad) - it tests every quarter-foot grid point of the yard against the floor's outline (point in
polygon, then the distance to each edge), and it counts, for every lattice at every offset, the seated mats one by one in
Python; `_lay_by_hand` then tests each mat's outline against every laid and every upcoming mat's (`_quad_gap`, 34,070 calls, the same profiles).
Both are static geometry asked per candidate: the grid's test can be decided in arrays (surely inside the inset floor,
surely outside it, the scalar test in the band between), the lattice counts are sums of shifted slices of one boolean
array, and two quads farther apart than the clearance need no `_quad_gap`. The mats come out the same.

**The bookend.** `284-start` was first taken at `f52ed6aa8` (17.4 s, before 282's mats merged) and re-taken at the base
`5f15c65bd`: total 23.3 s, median 5.6 s, worst 7.1 s (observed 2026-09-28, method: `make perf LABEL=284-start` in
`/tmp/base284`, load 6.7). The re-taken one is the bookend `284-end` is judged against.

## R4 - The coarser router lattice (B2, 2026-09-28)

**Method** (observed 2026-09-28, method: `b2/harness.py` on the engine that ships - the router in cost order, the base's
field search, the re-roll resume and the connector fix; a first run made with A* and the probe lever still in was set aside
at the reviews of Amendment 1, because the router itself decides which maps strand. The five pool hamlets, the 10- and
20-household toys and cohort seeds 1-24, each rolled at each cell with `route.ROUTE_CELL` set and the driver's own
`unreached_houses` wrapped so every attempt's count is kept; a coarser cell declined, for the run, the boxes the 10 px lattice
declined (the change went with the withdrawal, since it made the sweeps' own 14 px lattice decline boxes it used to route).
Twelve forked workers; the rows are `b2/results.json`):

| cell (px) | unreached, all attempts | rolls re-rolled | stranded in the kept map | maps worse than 10 px (every attempt) | roll seconds, summed (loaded; observed 2026-09-28, method: `b2/harness.py`) |
|---|---|---|---|---|---|
| 10 (today's) | 5 | 2 | 0 | - | 220.9 |
| 12 | 8 | 4 | 0 | cohort 08 [2, 0], Sawada [1, 0] | 235.6 |
| 14 | 12 | 4 | 7 | cohort 08 [7, 0], 19, 21, Mizuguchi | 231.4 |
| 16 | 13 | 5 | 1 | cohort 10, 19, 21 [1, 3], Sawada | 289.9 |
| 18 | 16 | 5 | 0 | cohort 01, 10, 18 [11, 0], 19, 21 | 388.2 |

The first cell tried, 12, strands houses the 10 px lattice does not (two maps, each healed by a re-roll; observed 2026-09-28, method: the table's harness), so by the plan's
rule the largest cell before it is today's 10: **B2 is withdrawn**. The rolls are not faster at any coarser cell either:
the router is a small share of a roll, and every extra stranding is a whole second build of the stages from the seats on.
The rescue-rounds scenario is a homestead-seat scenario with no ways in it, so the lattice does not reach it.

## R5 - The carve's rows as arrays (B4, 2026-09-28)

**Method** (observed 2026-09-28, method: `b4/harness.py` - one build of Sawada records every `_edge_in_supply` and
`_clear_supply` call; an array form answers the same edge calls, each edge's 3 px samples against a stroke's segments in one
numpy array, and both are timed fastest of three over the recorded calls; load 18.5; `b4/results.json`). After B3 the
carve is a small part of Sawada's field stage: `_carve_sector` 0.43 of the field's 3.83 profiled seconds, the body rows 0.35,
while the seam closing is 2.5 (observed 2026-09-28, method: a cProfile of one build of Sawada).

| part | calls | scalar | arrays (observed 2026-09-28, method: `b4/harness.py`) |
|---|---|---|---|
| the plot tests' edge walk (`_edge_in_supply`) | 3,310 | 0.086 s | 0.312 s, the same 3,310 verdicts |
| the vertices' pushes (`_clear_supply`) | 3,490 | 0.024 s | not built: the scalar total is under the arrays' overhead on the walk above |

A row holds a handful of columns and an edge a dozen samples, so numpy's per-call cost is paid on arrays too small to
repay it: the array walk is 3.6 times slower. **B4 is withdrawn** under the plan's own rule (kept only if faster). No part
was left scalar for being impossible to put in arrays; the vertices were not built because the whole of their scalar cost
is smaller than the loss already measured on the larger part.

## R7 - The other slow stages, re-profiled (T15, 2026-09-28)

**Method** (observed 2026-09-28, method: `t15/harness.py`, one cProfile of a build and finish of Sawada and one of
Kashikawa, after A1-A8, B1 and B3). What is left is spread thin:

- **The seam closing** (`close_seams`, 2.5 profiled s on Sawada, 1.4 on Kashikawa; observed 2026-09-28, method: the profile above): 822 pocket welds on Sawada at about
  1.2 ms each (`_absorb`, 0.97 s), the remainder `_plant` 0.35, `_unjog` 0.29, `_shed_necks` 0.22. A weld is a handful of
  shapely unions, buffers and a simplify on the one pocket and its ranked neighbors, already ranked in one array call and
  read from a shared tree (feature 276); there is no scan left to index, and the shapes are the rule. No lever taken.
- **The commons** (`commons`, 0.43 s on Sawada): the grass scatter, 0.37, already clipped to a predicted frame (feature 224).
  No lever taken.
- **The blade flush** (`flush_blade_groups`, 0.23 s on Sawada, 0.43 on Kashikawa): the merge of each blade group's lines
  (`merge_lines`, 0.09 s). No lever taken.
- **The grove fill** (`village_grove`, 0.57 s on Sawada): its tests are the grove blocks' indexed lookups (`near`, `inside`,
  `hard`, each under 0.1 s), with the crown seat test on its grid since A6. No lever taken.
- **The page's other parsing** (observed 2026-09-28, method: `parse/harness.py`, each page pass timed inside one finish of
  Kashikawa and of Sawada, fastest of three, load 12.5; `parse/results.json`): with the blade slots read from their structures,
  the passes that re-read a string the page already read - the off-map cull (`drop_offmap`) and the hit copies - take 0.051 s
  and 0.059 s together; the merge (`merge_primitives`, 0.170 and 0.178 s) is work on the elements, not a second parse. One
  shared parse could at most remove the first two - about 1% of a roll, a ceiling since the load inflates it.
- **The grove draw's crown grid, withdrawn** (observed 2026-09-28, method: `measure.py after-main`, main as merged against
  the clone back to back): with it the windbreak stage was 0.55 -> 0.60 s on Kashikawa, 0.60 -> 0.65 on Mizuguchi and 0.68 ->
  0.76 on Sawada - a grid filed per clump costs more than walking the clump's few nearby crowns. Main's 269 had already put
  its own crown index where the crowns are many (the rank), so the draw goes back to its two scans.
- **The grove draw** (`_draw_grove`; observed 2026-09-28, method: `grove/harness.py`, each call timed inside one build,
  fastest of three, load 3.6; `grove/results.json`): 0.128 s of Kashikawa's 4.46 s build and 0.092 s of Sawada's 4.71 s,
  its crown seat test 0.022 and 0.017 s of that. At 2-3% of a build, no change to it - a coarser crown lattice included,
  which could at most remove the draw - makes a roll significantly faster.
- **The seam closing, priced for a moving lever** (the same run): `close_seams` 0.890 s of Kashikawa's build and 1.628 s of
  Sawada's, the welds (`_absorb`) 0.317 and 0.681 s. Every shapely step in the whole build together - `buffer` 0.281 and
  0.352 s, `simplify` 0.041 and 0.084 s, `union` 0.028 and 0.054 s - is under half of it; the rest is the pass's own
  ladder of repairs, each the fix for a rule: a strip left between two basins is a doubled bund
  (`tests/waterfields/test_seams.py::test_a_thin_strip_between_two_basins_is_absorbed_not_left_as_a_doubled_bund`), a weld
  that points a basin is refused (`...::test_absorb_leaves_the_scrap_bare_when_every_weld_would_make_a_real_needle`), a
  crossing ring is refused (`...::test_a_repaired_crossing_ring_is_refused_when_its_raw_ring_is_a_needle`), and the
  shipped hamlets carry no basin tapering to a point (`tests/gate/test_paddy_fabric.py`). The moving levers priced: weld
  fewer pockets (leaves doubled bunds - the first rule), or drop the weld's tidying `simplify` (at most 0.041-0.084 s, 1-2%
  of a build, and it would record rings with more vertices for nothing). Neither makes a roll significantly faster within
  the rules.
- **The geometry primitives**: `seg_dist` is called 312,391 times on Sawada (0.54 profiled s), from about 25 callers, none
  above 0.09 s. An index per caller would each buy under a tenth of a second.

## R8 - A re-roll resumed at the seats (2026-09-28)

The costliest thing in a roll that is not a stage: a roll that strands a house on its first attempt pays a whole second
build - two of the 29 rolls of R4 at 10 px on the engine that ships, and six of 29 with the moving levers R6 measured
(observed 2026-09-28, method: `b2/harness.py` and `combined/harness.py`). The avoid list a re-roll carries is first read at `stage_homesteads` (the seat
loops, `homesteads/seats.py` `_seat_allowed` and `rolling/place.py`); the five stages before it - the water frame, the
field, the sink, the seat and the waterward fringe - read nothing that differs between attempts. So the first roll keeps a
deep copy of the settlement and plan as they stand before the seats, and each re-roll starts from a fresh copy of that
(`driver.resume`), rather than running the field again. An exact change: the same map, sooner.

**Method** (observed 2026-09-28, method: `reroll/harness.py` - on Kashikawa and cohort seeds 1, 5, 17, 18 and 19, the six
maps that re-roll with the moving levers in (R6's combined run), the re-roll made both ways and each finished to a scratch svg and page; load
4.8; `reroll/results.json`):

| map | re-roll built from scratch | re-roll resumed | first roll without / with the snapshot | manifest, svg, page (observed 2026-09-28, method: `reroll/harness.py`) |
|---|---|---|---|---|
| Kashikawa | 5.08 s | 3.39 s | 4.98 / 4.80 s | identical |
| cohort 01 | 3.50 s | 2.18 s | 3.43 / 3.29 s | identical |
| cohort 05 | 4.23 s | 2.73 s | 3.88 / 3.93 s | identical |
| cohort 17 | 3.80 s | 2.67 s | 3.81 / 3.97 s | identical |
| cohort 18 | 3.67 s | 2.42 s | 4.16 / 4.29 s | identical |
| cohort 19 | 2.94 s | 1.75 s | 2.65 / 2.81 s | identical |

A resumed re-roll is 1.1 to 1.7 s faster (about a third; observed 2026-09-28, method: the table's harness); the snapshot's copy costs the first roll no more than its own
run-to-run spread (single runs each, so within noise either way).

## R6 - What the moving levers did to the maps (2026-09-28)

Each moving lever is judged by the pool and cohort seeds 1-24 rolled whole - summed roll seconds, first-roll strandings,
re-rolls - never by its own stage's calls; and by the run-to-run spread, measured in the same run: the shipping engine is
rolled twice, interleaved by map with the lever's pass, twelve forked workers, so the load drifts over all passes alike.
A lever is kept when it is faster in all by more than that spread with every rule holding. The first runs of FR-001 and
FR-004 were each made with the other lever in, and with a router box decline that no longer ships; the reviews of
Amendment 1 set them aside. The runs below were made with every other lever as it then stood (FR-004 in for the A* run);
both were then withdrawn on the rules (below), so the engine that ships is the "levers off" column.

**The field search without its blind probe (FR-004)** (observed 2026-09-28, method: `b3cmp/harness.py`, the router in cost
order; `b3cmp/results.json`): the shipping search 383.9 s and 388.3 s in its two passes, the lever 367.1 s - about 19 s
(5%) faster than their mean, against a spread of 4.3 s (1%). It re-rolls five maps against two. Its own stage:
Inashiro's field 1.51 to 1.06 s, Sawada's 2.89 to 2.21 s (measure.py after, the interim run).

**A* in the router (FR-001), with FR-004 in** (observed 2026-09-28, method: `astarcmp/harness.py`, `astar.txt` the lever's
search; `astarcmp/results.json`): the cost-order search 211.5 s and 212.7 s, A* 207.1 s - 5.1 s (2.4%) faster than their
mean, against a spread of 1.2 s (0.6%); 8 houses unreached over every attempt against 6, six re-rolls against five, every
map healed by its re-roll.

**Both together, against both off** (observed 2026-09-28, method: `combined/harness.py`; `combined/results.json`):

| | the levers off (the base's router and search - the engine that ships) | levers on, pass 1 | levers on, pass 2 |
|---|---|---|---|
| summed roll seconds (loaded) | 344.75 | 327.27 | 329.37 |
| houses unreached, every attempt | 5 | 8 | 8 |
| rolls that re-rolled | 2 | 6 | 6 |
| households seated, connectors drawn, failing rolls | 442, 29, 0 | 442, 29, 0 | 442, 29, 0 |
| household bamboo strips | 140 | 120 | 120 |

16.4 s (4.8%) faster in all, against a spread of 2.1 s (observed 2026-09-28, method: the table's harness). **The household bamboo falls 14%** - fewer on 13 maps, more on 3:
presence is rolled per farmstead from its position (a labeled GUESS at 60%, `HOUSEHOLD_BAMBOO_PREVALENCE`) and a strip is
dropped where the farmstead has no room, so the moved houses leave fewer rolled-present farmsteads room. The cohort's rolls
broke no rule the runs check and no household lost its seat - but the regenerated pool failed five gate rules (below).

**The coarser lattice (FR-003)**: R4 - it strands at 12 px on this engine too (observed 2026-09-28, method: `b2/harness.py`).

**Both withdrawn, on the rules.** With both kept, the pool regenerated (Inashiro, Kashikawa and Sawada moved; Kashikawa
re-rolled; every household seated, every connector drawn, every field within its tolerance), and the gate failed on the
moved maps (observed 2026-09-28, method: `make done`, its FULL test phase over the shipped pool):
`test_a_bund_does_not_build_a_flight_of_steps` (a plot ring stepped twice), and in `tests/hamletgen/test_pool_261.py` three
woodland parcels in a ruled row on Kashikawa, a copse clump off its house's bank on Inashiro, and a brook leg within 1.6
degrees of a screen axis on Kashikawa and on Sawada; `test_pool_wind.py` found Sawada's seat no longer backed onto the
regional northwest. Each is a rule the gate proves on the shipped maps rather than one its placer guarantees, so a map moved
for any reason can meet it; these two levers met five. The GM allowed map changes for speed within the rules only, and the
pool itself was no faster with them (23.76 s against 23.89 s without, each measure.py after back to back): **FR-001 and
FR-004 are withdrawn**, the base's router order and field search restored, each with this at its point of change. With them
out, the pool is main's map by map but for the bamboo thicket (FR-008's coarser sampling, below), and the gate's pool rules
pass.

**The pool, against main as merged (`7c0c94f94`)** (observed 2026-09-28, method: `make maps SCOPE=all`, each manifest compared
with `git show` of main's): Inashiro, Kuwabata and Sawada are main's maps byte for byte. On Kashikawa and Mizuguchi the
houses, paddies, dry plots, ways and every household bamboo strip are main's, and the one bamboo thicket seats on the 16 ft
lattice where the 8 ft one seated it: its center 18.1 ft from main's on Kashikawa and 24.5 ft on Mizuguchi - the nearest
fitting seat on the coarser lattice, the same keep-outs and reach. Every map is a single roll.

**What those five failures say about the placers.** None is a defect the levers made: each is a property of a FINISHED map
that no single placer owns (the constitution's third kind of rule), and the cohort seeds the levers moved did not meet them
- the pool maps did. They are recorded here, not fixed under this feature, because nothing ships that breaks them: fixing
them means making five placers guarantee what the gate now observes, a change of what each placer is for.

**A defect the moved maps found: a connector deleted as debris** (observed 2026-09-28, method: `c15/harness.py`, spies on
the connector's routing, threading and `drop_lanes`). Cohort seed 15, rolled with FR-004 under A*, came out with no connector
at all - its 4,004 px track out to the map edge planned, threaded, drawn, and then deleted by the junction pass
(`_touch_junctions`), which drops a piece the web cannot join when it serves no house of its own. The connector is the one
way that must not go (`trim_lane_stubs` has always exempted it), and with it gone the reach check read the network that was
left and passed: the roll reported OK on a hamlet with no way off the map. Fixed: the pass never drops the connector
(`tests/hamletgen/ways/test_geom.py::test_touch_junctions_never_drops_the_connector`); one test of the pass had counted the
deletion as its expected result (`test_touch.py`, the end-meets-end case) and now asserts the join it meant. Every roll of
the three runs above - 87 rolls each - draws its connector.

