# Feature 278 - research

## R1. The second measurement (2026-09-28, main `ac01ffe2d`)

**The tests.** `make durations N=30` over everything but `tests/full` (observed 2026-09-28, method: the target, load ~2):
94 s for 5,006 tests. The top of the list is the gate tests reading pool hamlets through the roll cache, cold after
main moved - Sawada's beaded-bund test 31.0 s, Kashikawa's 17.1 s - which is the roll itself (below), not the test.
Then `test_md_tokens_equal_the_whole_text_scan` at 4.6 s (feature 276's own equality test, scanning every tracked text
twice). One failure: `test_every_clickable_class_is_named_somewhere_on_the_committed_page`, red because the page is
gitignored and re-plated only at landing, and main had added the `alder` class.

**A regeneration.** One Inashiro `generate()` with rendering, unprofiled (observed 2026-09-28, method: wrappers timing
`build` and `finish`): 9.6 s - 7.3 s of stages, 2.3 s of finishing (0.8 s the PNG, 1.2 s the page raster). `make map`
on the reference took 19.5 s because it rolls the map twice: once for the gate's reference check, then again uncached
because the cached entry carries no render.

**The stages.** `harness.py` (`harness-before.json`): per pool hamlet the stage seconds (the faster of two unprofiled
rolls; the load was ~9 at the start of this run, so these seconds are read for their order, not their size) and the
mechanism counts (cProfile call counts, load-independent):

| hamlet | roll s | largest stages | builds |
|---|---|---|---|
| Inashiro | 8.1 | field 1.8, windbreak 1.0, crossings 1.0, hinterland 0.9, notice 0.8 | 1 |
| Kashikawa | 13.4 | web 2.6, windbreak 2.2, field 2.0, hinterland 1.2 | 1 |
| Kuwabata | 5.8 | appurtenances 1.7, web 1.2, field 0.7 | 1 |
| Mizuguchi | 6.0 | field 1.0, web 1.0, hinterland 0.7 | 1 |
| Sawada | 27.4 | field 7.6, web 5.9, notice 2.7, windbreak 2.3 | 2 |

**The mechanisms**, from profiles of the hot stages (observed 2026-09-28, method: cProfile callees in a test node):

- The router (`hamletgen/ways/route.py` `_route`) fills `free` for every cell of its box and asks `in_brook_band` of
  every free cell before Dijkstra runs: 358,398 fouled tests and 174,118 band tests on Kashikawa, 1,013,133 and 460,131
  over Sawada's two builds (m:before-kashikawa-cell-fouled, m:before-sawada-cell-fouled). A route that finds its goal
  pops only the cells nearer than it; the rest were evaluated for nothing.
- The straggler doorstep (`hamletgen/ways/serve.py`, the `next(...)` over ring points) calls `fabric_index(...)` once
  per candidate point with the same inputs; the memo hits, but its key walks every polygon: 5,407 key builds on Sawada.
- The footbridge widening (`settlement/city/bridges.py` `_widen_for_confluence`) tests every segment of every other
  watercourse per deck candidate: 62,565 of Inashiro's 63,674 `quad_hits_seg` calls.
- The hamlet well placer (`hamletgen/homesteads/wells.py`) sorts its pool with a key that sorts every house's distance,
  on every pass of its loop: 168 sorts, 3.1 s profiled on Kuwabata.
- Sawada is built twice: `meta.roll_attempt` 2, `roll_after` `farmhouses_reach_a_way`.

**What the first reading called the residue** - the field, the windbreak, the commons and the notice board - was
claimed to be each algorithm's own density on call counts alone. The fidelity review (round 1) held that unmeasured,
and R2 measures it.

## R2. Where the residue stages' seconds go (2026-09-28)

Each stage profiled ALONE (a profiler enabled only inside that stage's function), over Kashikawa and Sawada's two
builds, with the finish profiled the same way (observed 2026-09-28, method: cProfile per stage in a test node, own time
sorted; the profiled seconds are inflated, read for their shares):

- **The field** (21.3 s profiled; observed 2026-09-28, method: the per-stage cProfile): `_pip` 2.18 million calls, 1.91 million of them from the hem pass's `inside_any`
  (`waterfields/carve.py`, point-in-polygon against EVERY plot per drain sample - a per-candidate scan); `_bnd`'s
  `_at_f` 118,836 calls, 1.6 s - a LINEAR walk of a static thread polyline per query, re-projecting every vertex each
  call (`waterfields/frame.py`), a scan of geometry that does not change during the carve; `_quad_in_supply` 261,368 clearance calls, 1.1 s, already bbox-gated per stroke.
- **The windbreak** (12.6 s; observed 2026-09-28, method: the per-stage cProfile): 2.04 million `PointGrid.near` calls - the grove's keep-out families (`hard`, `local`,
  `lane`, `inside`, `too_near`) are separate grids, each asked per candidate, the shape 218 fixed for the scatters
  ("one grid per scatter, not one per family") and never applied to the grove.
- **The hinterland** (9.5 s; observed 2026-09-28, method: the per-stage cProfile): the commons scatter 5.6 s of it - 2.29 million `random.uniform` draws, 241,939 `_sparse`
  tests, 593,218 grid lookups. 218's research R2 priced a vectorized scatter (numpy throws and tests) that keeps the
  density: it moves the map, which the GM has since allowed.
- **The notice board** (10.7 s; observed 2026-09-28, method: the per-stage cProfile): `off_every_bed` measures every way segment per verge candidate (880,459 generator
  steps); `_hard_clear` walks the bounding box of every hard polygon per call and runs `quad_hits_poly` - every vertex
  and edge of each big polygon whose box it meets - 7,569 calls, 3.1 s.
- **The finish** (14.9 s over three finishes; observed 2026-09-28, method: the per-stage cProfile): 4.7 s waiting on the external renderer; the page's `_hits` 1.29 million
  calls; and one of the three finishes is Sawada's discarded first attempt - the driver finishes every attempt, kept or
  not.

## R3. Why Sawada is rolled twice (2026-09-28)

Attempt 1 (observed 2026-09-28, method: `build()` and `unreached_houses()` in a test node, the attempt's map rendered
and cropped): the easternmost farmhouse, at (1271, 1890), is seated in a bare pocket INSIDE the paddy field, north of
the ditch - paddies on three sides, the ditch and the dry plots below it - 226 px from the nearest other house and
237 px from the nearest lane. Its four fixtures (privy, manure, coop, persimmon) found no seat around it. The seat
search ran six rounds. No way can reach the house without crossing crop, so the straggler router fails, the roll
reports `farmhouses_reach_a_way`, and the driver re-rolls with that seat forbidden. The placer took a seat that no way
can reach; only the roll's own self-report, after the whole build, catches it.

## R4. The maps this feature moved (FR-005, and FR-008 when it lands)

**The exact pieces moved nothing** (observed 2026-09-28, method: `make map` of each pool hamlet after A1-A9 and B1, each
manifest compared byte for byte with the committed one): Inashiro, Kashikawa, Kuwabata and Mizuguchi identical.

**Sawada** (B1; observed 2026-09-28, method: the regenerated manifest against the committed one): built ONCE now
(`roll_attempt` 1, `roll_after` empty; before, attempt 2 after `farmhouses_reach_a_way`), 16.0 s to regenerate against
about 31 s. Houses 19 before and after, all plain, nucleated; every farmhouse reaches a way. Paddies 1000 and 1000,
flooded 1 and 1, dry plots 39 and 40, lane records 12 and 13. Read by eye: the same hamlet - the cluster west of the
field, no house inside the paddies.

**The vectorized commons** (B2; observed 2026-09-28, method: every pool map regenerated, each manifest compared with the
post-B1 one, and `commons_marks.py` over the SVGs before and after): the only manifest key that changed on any map is
`ink_classes`, the census of drawn ink - houses, lanes, fields, woodland parcels and every `meta` field identical. The
marks' counts (`commons-marks-before.json`, `commons-marks-after.json`): grass blades within 1.1% on every map and brush
dots within 2.7%, the same throw counts at the same odds landing at different places. Pines moved by up to 6.5%
(Kashikawa 310 -> 291, Sawada 292 -> 311): their code is unchanged - only the random stream they draw from moved, one draw
later than before - and on ~300 marks the sampling spread alone is about the square root, 17 marks or 6%, so the plan's
5% band sits below one standard deviation for this family. Recorded rather than tuned: the expected count is the old one.

**A defect caught by that comparison**: the parcel seat's line index was first built once for the size the scan offers,
but `_ok` is re-asked with a different `half` when the size roll re-tests a seat, and the reach is `pad + half` - so a
re-asked seat was judged at the wrong reach and Kashikawa's and Mizuguchi's woodland parcels moved. The index is now one
per size asked (`_lines_at`), and the parcels are back on their seats byte for byte.


**SC-013's scenarios beyond the pool** (observed 2026-09-28, method: feature 276's harness placement section run in the
base worktree and in the clone): the rescue-rounds scenario seats 16 nucleated and 10 dispersed houses on both, the 10-
and 20-household toys 10 and 20 on both, and every constant-density layout the same count on both paths (five-layout
totals 281, 560 and 1133 nucleated, 191, 365 and 707 dispersed). No shortfall anywhere, new or larger.
