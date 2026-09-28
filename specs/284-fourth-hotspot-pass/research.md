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

**Method** (observed 2026-09-28, method: `b2/harness.py` - the five pool hamlets and cohort seeds 1-24 rolled at each cell
with `route.ROUTE_CELL` set, the driver's own `unreached_houses` wrapped so every attempt's count is kept, twelve forked
workers, load 5-19; the rows are `b2/results.json`). Unreached houses summed over every attempt, re-rolls included:

| cell (px) | unreached, all attempts | maps worse than the 10 px lattice | roll seconds, summed (loaded, indicative) |
|---|---|---|---|
| 10 (the base) | 8 | - | 334.6 |
| 12 | 20 | cohort 03 (0 -> 1 then 2, and the map KEPT one stranded house), 08 (0 -> 2 then 8, kept 2), 23 (0 -> 2) | 295.4 |
| 14 | 15 | cohort 08 (0 -> 7), Mizuguchi (0 -> 1) | 219.5 |
| 16 | 13 | cohort 08 (0 -> 2 then 5, kept 2), 10 (0 -> 1) | 215.9 |
| 18 | 13 | cohort 03 (0 -> 1 then 7, kept 1) | 197.4 |

The first cell tried, 12, already strands houses the base did not - two of them through the driver's re-roll into the
finished map - so by the plan's rule the largest cell before it is taken, and that is the base's 10: **B2 is withdrawn**.
The summed seconds fall with the cell, but most of the fall is the maps that happened not to re-roll (a re-roll is a whole
second build); the router itself is under half a second of a roll (`_route`, 26 calls, 0.47 profiled s on Sawada). Which
maps strand moves chaotically with the cell, which is why the rule counts per map and seed rather than in total.

**What this measurement names instead.** Eight of the base's 29 rolls strand a house on the first attempt and pay a whole
second build to fix it - the costliest single thing in the table, and not a lattice question. Recorded for the fourth
pass's section of `dev/performance.md`.

## R5 - The carve's rows as arrays (B4, 2026-09-28)

**Method** (observed 2026-09-28, method: `b4/harness.py` - one build of Sawada records every `_edge_in_supply` and
`_clear_supply` call; an array form answers the same edge calls, each edge's 3 px samples against a stroke's segments in one
numpy array, and both are timed fastest of three over the recorded calls; load 18.5; `b4/results.json`). After B3 the
carve is a small part of Sawada's field stage: `_carve_sector` 0.43 of the field's 3.83 profiled seconds, the body rows 0.35,
while the seam closing is 2.5 (observed 2026-09-28, method: a cProfile of one build of Sawada).

| part | calls | scalar | arrays |
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

- **The seam closing** (`close_seams`, 2.5 profiled s on Sawada, 1.4 on Kashikawa): 822 pocket welds on Sawada at about
  1.2 ms each (`_absorb`, 0.97 s), the remainder `_plant` 0.35, `_unjog` 0.29, `_shed_necks` 0.22. A weld is a handful of
  shapely unions, buffers and a simplify on the one pocket and its ranked neighbors, already ranked in one array call and
  read from a shared tree (feature 276); there is no scan left to index, and the shapes are the rule. No lever taken.
- **The commons** (`commons`, 0.43 s on Sawada): the grass scatter, 0.37, already clipped to a predicted frame (feature 224).
  No lever taken.
- **The blade flush** (`flush_blade_groups`, 0.23 s on Sawada, 0.43 on Kashikawa): the merge of each blade group's lines
  (`merge_lines`, 0.09 s). No lever taken.
- **The grove fill** (`village_grove`, 0.57 s on Sawada): its tests are the grove blocks' indexed lookups (`near`, `inside`,
  `hard`, each under 0.1 s), with the crown seat test on its grid since A6. No lever taken.
- **The geometry primitives**: `seg_dist` is called 312,391 times on Sawada (0.54 profiled s), from about 25 callers, none
  above 0.09 s. An index per caller would each buy under a tenth of a second.

## R8 - A re-roll resumed at the seats (2026-09-28)

R4's table showed the costliest thing in a roll that is not a stage: eight of the 29 base rolls strand a house on the
first attempt and pay a whole second build. The avoid list a re-roll carries is first read at `stage_homesteads` (the seat
loops, `homesteads/seats.py` `_seat_allowed` and `rolling/place.py`); the five stages before it - the water frame, the
field, the sink, the seat and the waterward fringe - read nothing that differs between attempts. So the first roll keeps a
deep copy of the settlement and plan as they stand before the seats, and each re-roll starts from a fresh copy of that
(`driver.resume`), rather than running the field again. An exact change: the same map, sooner.

**Method** (observed 2026-09-28, method: `reroll/harness.py` - on Kashikawa and cohort seeds 1, 5, 17, 18 and 19, the maps
R4 found re-rolling at the 10 px lattice, the re-roll made both ways and each finished to a scratch svg and page; load
4.8; `reroll/results.json`):

| map | re-roll built from scratch | re-roll resumed | first roll without / with the snapshot | manifest, svg, page |
|---|---|---|---|---|
| Kashikawa | 5.08 s | 3.39 s | 4.98 / 4.80 s | identical |
| cohort 01 | 3.50 s | 2.18 s | 3.43 / 3.29 s | identical |
| cohort 05 | 4.23 s | 2.73 s | 3.88 / 3.93 s | identical |
| cohort 17 | 3.80 s | 2.67 s | 3.81 / 3.97 s | identical |
| cohort 18 | 3.67 s | 2.42 s | 4.16 / 4.29 s | identical |
| cohort 19 | 2.94 s | 1.75 s | 2.65 / 2.81 s | identical |

A resumed re-roll is 1.1 to 1.7 s faster (about a third); the snapshot's copy costs the first roll no more than its own
run-to-run spread (single runs each, so within noise either way).

## R6 - What the moving levers did to the maps (2026-09-28)

**The field search without its blind probe (FR-004), withdrawn.** It cut the field bucket's calls 2.1x on Inashiro and 3.0x
on Sawada and the field stage from 1.51 to 1.06 s and from 2.89 to 2.21 s (measure.py after, back to back). But the fields it
lands, within the same tolerance, are other fields, and the maps they move re-roll more often. Over the pool and cohort
seeds 1-24, each rolled with the base's `_fit_at_aspect` swapped in and with the lever, everything else the clone's
(observed 2026-09-28, method: `b3cmp/harness.py`, twelve forked workers; `b3cmp/results.json`):

| | the base's search | without the blind probe |
|---|---|---|
| households seated | 442 | 442 |
| rolls that re-rolled | 4 | 6 |
| summed roll seconds (loaded, both halves under the same load) | 180.6 | 190.7 |
| household bamboo stands | 141 | 120 |
| connectors drawn | 29 | 29 |

Kashikawa was one of the maps it moved into a re-roll: with the base's search its first roll strands none, with either
router (`strand/harness.py`). The lever was slower in all, so it was withdrawn and the base's search restored, with this
measurement at the point of change in `hamletgen/water/fit.py`.

**A defect the moved maps found: a connector deleted as debris.** Cohort seed 15, rolled with the lever, came out with
no connector at all - its 4,004 px track out to the map edge planned, threaded, drawn, and then deleted by the junction
pass (`_touch_junctions`), which drops a piece the web cannot join when it serves no house of its own. The connector is the
one way that must not go (`trim_lane_stubs` has always exempted it), and with it gone the reach check read the network that
was left and passed: the roll reported OK on a hamlet with no way off the map. Fixed: the pass never drops the connector
(`tests/hamletgen/ways/test_geom.py::test_touch_junctions_never_drops_the_connector`); one test of the pass had counted the
deletion as its expected result (`test_touch.py`, the end-meets-end case) and now asserts the join it meant. With the fix
every one of the 58 rolls above draws its connector.

**The other moving levers.** A* (FR-001) moved Mizuguchi's lanes and nothing else on it; the bamboo seat lattice (FR-008's
fallback) moved Mizuguchi's thicket; neither changes what a house, a paddy or a way is. The pool's before and after for each
moved map is below, from `pool_compare.py`.
