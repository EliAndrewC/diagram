# Feature 281 - research

## R1 - The measurement (2026-09-28, main `c13a6ebe6`: 278 and 261 landed, 279's woodland crowns merged)

**Method.** `measure.py before`: the harness (`harness.py`, via `make spec-harness`) rolls each pool hamlet twice
unprofiled with every stage timed (the faster roll kept), once more writing its svg and page, and once under cProfile
writing the page too, saving the profile; `counts.py` reads the profiles and credits each generator expression to the
function that encloses it, so a count survives line moves. Every figure is in `measurements.json` as a `before-*` key.

**The roll.** The five pool hamlets take 32.902 s between them (m:before-pool-roll-s), against 60.1 s before feature 278. (A first
run at `2a61d1488`, before 279's crowns merged, gave every count here unchanged and 33.8 s - observed 2026-09-28,
method: `measure.py before` at that commit.)
By stage, summed over the five: the field is the largest, then the ways (`stage_web`), the windbreak, the hinterland, the
notice board, the homesteads and the track. A full generate writing the svg and the interactive page costs about the same
as the roll alone (Inashiro 5.859 s against 5.893 s, m:before-inashiro-full-s, m:before-inashiro-roll-s), so the
finish is not where the time goes. The pixel render is a separate step outside the roll (feature 278 priced it and left it).

**The profile** (profiled seconds summed over the five, `/tmp/m281/before/*.prof`; profiling inflates Python-level work
about 2.4 times, so these rank, they do not predict). The self-time leaders are the distance primitives: `seg_dist` 5.8
million calls, `seg_closest` beneath it, `min`/`max`/`hypot` around them. Traced to their callers:

| where | what it does per ask | why that is a scan | measured |
|---|---|---|---|
| `clip_to_clear`'s `fouled` (the lane arms, the field spur, the track's threading) | every obstacle polygon's every edge, every line | its through-lane sibling `clear_runs` asks `FabricIndex` (feature 138); the clip never did | seg_dist from it: m:before-kashikawa-clip-seg-dist, m:before-kuwabata-clip-seg-dist |
| `FabricIndex.__init__` on a memo miss | builds a `RingIndex` for every polygon | the same polygons are rebuilt per miss: on Kashikawa 376 distinct polygons, 5,932 builds (observed 2026-09-28, method: a probe wrapping `fabric_index` on one Kashikawa roll) | m:before-kashikawa-ring-index-builds, m:before-sawada-ring-index-builds |
| `in_brook_band` (the router's toll) | up to 25 grid cells of 20 px, each a dict lookup, around the point | the band's radius is 30 px (`FORD_HALF`); a cell the radius wide answers from 9 | m:before-kashikawa-brook-band-tests, m:before-sawada-brook-band-tests |
| `outermost_join` (the notice board's handover) | every other way's every segment, per 5 ft sample of the connector | a static set of segments | m:before-sawada-handover-seg-dist |
| `routes_missed` (the notice board's departure count) | every route's every point, per candidate seat | static routes | m:before-sawada-routes-missed-dist, m:before-inashiro-routes-missed-dist |
| `_link_home_bank` (feature 261's home-bank join) | every brook segment per route segment | a static course | m:before-kashikawa-home-bank-cross |
| `_rect_on_stream` (the homestead fit) | every stream segment per rect, no box prefilter | a static course | m:before-sawada-stream-rect-seg-dist |
| `label_seat_clear` (caption seats) | every lane segment per probe | the lanes do not change during a caption pass | m:before-kashikawa-caption-lane-seg-dist |
| the carve's `edge(fv, j, n)` | a bund vertex, pushed off the supply banks | each vertex is shared by up to four plots and computed for each | m:before-sawada-carve-edge |
| `_quad_in_supply` | each plot edge walked at 3 px against the supply banks | a shared edge is walked by both its plots | m:before-sawada-supply-clearance |

And two stages whose remaining cost is per-candidate Python work over an index that is already there:

- **The windbreak** (`village_grove`): 278 filed its keep-outs in one grid; what remains is the scalar tests themselves -
  the outline, the hard ground, the local keep-outs, the lanes - asked of every grid point and of every re-seat ring
  (40 positions round each blocked point), and above all of the GAP FILL, which offers each gap between two seated
  clumps 5 fractions x 33 depths in every round, for up to six rounds. Counted by caller: of Sawada's 253704 outline
  tests (m:before-sawada-grove-inside) 519 come from the re-seat (m:before-sawada-grove-inside-reseat), and the grid holds
  at most 3,276 points (observed 2026-09-28, method: the profile's `_hjit` calls from the grove, two per point) - so
  nearly all come from the gap fill. Every one of those tests but the spacing one is STATIC - the ground does not change during the fill -
  and the spacing test's refusals only grow as clumps land. So a gap that took nothing in a round takes nothing later:
  re-offering it is the whole of the repeat cost, and remembering that is exact, where 278's priced lever (the static
  tests as array operations) would only have made the repeats cheaper.
- **The marsh scatter** (`marsh`): per point, the commons' old shape (m:before-kuwabata-marsh-sparse,
  m:before-sawada-marsh-sparse). 278 priced it: "the marsh vectorized as the grass was".

**What is not a scan.** The router's own search (Dijkstra over lazily judged cells, 278), the field fit's size search
(already predictive: m:before-sawada-carve-comb carves), the seam closing's pocket absorption, the page's merge (indexed
by 278; its remaining cost is regex parsing of the element text) and the finish's blade grouping. These go to the
after-profile's residue with their levers priced (FR-011).

**The tests.** `make durations` (observed 2026-09-28, method: `make durations`, one run): the quick tree is 4,062 tests in 27.8 s wall; its slowest test is
3.8 s and no one test is its critical path, so no test-side lever is taken - the gate's cost is the pool rolls, which the
engine levers reduce.

## R2 - The pool after the exact pieces, and after the moving ones (2026-09-28)

**The exact pieces (A1-A8), SC-011's first half.** The committed pool at `c13a6ebe6` was first confirmed to regenerate
byte-identically in the base worktree (observed 2026-09-28, method: `make maps SCOPE=all` in `/tmp/base281`, then
`git status` over `pool/` - clean). With A1-A8 landed and B1-B2 not, `make maps SCOPE=all` in the clone left
`git diff c13a6ebe6 -- .claude/skills/diagram/pool` empty: every live pool manifest, svg and page byte-identical.

**The moving pieces (B1, B2), each map's houses, paddies and ways before and after** (observed 2026-09-28, method:
`pool_compare.py`, the manifests at `c13a6ebe6` against the regenerated ones, and a key-by-key diff of each manifest).
With both landed, the ONLY key that changed on any of the five maps was `ink_classes.marsh`, the count of marsh marks
inked (Inashiro 2278 -> 2254, Kashikawa 2559 -> 2476, Kuwabata 802 -> 767, Mizuguchi 1772 -> 1826, Sawada 4140 -> 4096):
the houses (15, 20, 16, 12, 19), their kinds, the form, every field and plot record, every way and its length, and the
marsh outlines were identical. So B1's shared-edge walk moved no plot on any pool map - no plot edge sits within rounding
of the bank's threshold there - and B2 moved only where the marsh's random marks land.

**B2 WITHDRAWN: the vectorized marsh bought no time** (observed 2026-09-28, method: each stage timed over three rolls per
map, the fastest kept, the base worktree then the clone). The hinterland stage, where the marsh runs, came out 0.596 ->
0.614 s on Inashiro, 0.926 -> 0.942 on Kashikawa, 0.380 -> 0.443 on Kuwabata, 0.536 -> 0.555 on Mizuguchi and 0.790 ->
0.762 on Sawada - flat, and slower on Kuwabata. The profile says why: the scalar keep-out tests fell 359x on Sawada and
671x on Kuwabata, but the array form builds the shapely shapes of every keep-out near a kind's throws (`KeepoutGrid.
_trees_for`, once per mark kind per marsh), and on these small marshes that costs what the scalar tests did - on
Kuwabata, with its many fish-pond banks, more (the profiled `_trees_for` 0.15 -> 0.47 s). A change that moves every map's
marks and buys nothing is not the exercise, so the marsh is back to its scalar throws (spec Amendment 1). With B2 out
and the bank fix below in, the whole pool regenerated byte-identical against `c13a6ebe6` - Kuwabata included, whose drawn
reeds never stood in a cut bank corner - so this feature, as landed, moves no pool map.

**A defect the moved throws exposed, fixed where found.** An existing test - reeds keep off a fish pond's bank - failed:
one tuft based at (699.0, 497.2), inside the drawn bank's corner. The keep-out and its array form agree there; the marsh
tested each bank thinned to every 16th point (feature 139: "16 points hold its shape for a keep-out"), and the thinned
ring cuts each corner of a rectangular bank with a chord 7.45 px from that point (observed 2026-09-28, method: the
distance from the point to the chord between the thinned ring's 56th and 63rd points), beyond a tuft's 7 px pad. The old
throws had simply never landed in the sliver. The thinning was a cost choice made while every bank was walked per point;
the keep-out grid indexes each ring now, so the whole bank is used and the reeds keep off the corners too. It stays with B2 withdrawn: the defect is in the keep-out, not the throws.

**Beyond the pool** (observed 2026-09-28, method: feature 276's harness `_homesteads` section run in the base worktree and
in the clone): the rescue-rounds scenario seats 16 nucleated and 10 dispersed houses on both, the 10- and 20-household
toys 10 and 20 on both, and every constant-density layout the same count (five-layout totals 281, 560 and 1133 nucleated,
191, 365 and 707 dispersed). No shortfall anywhere, new or larger.
