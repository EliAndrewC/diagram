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

**The residue** - each already indexed, its cost the number of samples its drawing takes:

- The comb carve: 3-4 carves per build (the power-law fit, feature 220), each mostly `_sector_body_rows` - 12,244
  `edge` and 2,373 `in_supply` calls per build on Inashiro, no scan among them.
- The windbreak: 60,307 (Inashiro) to 128,952 (Kashikawa) `too_near` tests over its jittered grid, each a grid lookup.
- The commons scatter: 35,960 to 164,042 `_sparse` tests.
- The notice board: every verge point every `12 px` along every route, both sides, each through the indexed `_fits` -
  8,001 to 21,311 `_fits` calls per roll.
