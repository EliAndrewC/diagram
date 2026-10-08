# Performance: the two shapes this engine keeps growing

**Load this file when:** A gen or a check got slow (or "hangs"), you are about to optimize one, or a GEN_TIME_BUDGETS entry tripped.

The short always-on version of each rule is in the engine index, [`l7r/diagram/CLAUDE.md`](../l7r/diagram/CLAUDE.md);
what a TEST costs is [`test-cost.md`](test-cost.md). The per-feature measurements are in each feature's spec; this file
keeps the doctrine, the shapes to look for, and the levers already withdrawn.

## Maps may change for speed - an optimization is never held to identical output

The GM, 2026-09-30 (feature 297): *"it is perfectly acceptable for maps to change as a result of these optimizations.
They do NOT need to remain identical in output"*, and *"if anything in our project guidelines says that maps can't change
when making optimizations then we should strike it and say the opposite."* Earlier the same: *"It is absolutely not
required that the changes ... result in bite identical output"* (feature 218) and *"I even prefer it if it gets us
performance benefits"* (feature 284).

So a placer, a fill or a scatter may be rebuilt in a faster form that DECIDES differently - a coarser lattice, a
conservative raster of the blocked ground, candidates proposed from a region instead of refused one by one, a different
order of offering - and the maps move. What an optimization is held to is the RULES: every gate rule passes on the
regenerated pool, every household is seated, the forms, kinds and acreage bands hold, and each moved map is reviewed as
any changed map is. Byte-identity is a verification convenience where a change happens to preserve output, never a
requirement and never a reason to reject or withdraw a lever. The one thing that is not coarsened is a CHECK that
VERIFIES a rule (a gate test): loosening it lets defects through, which is a different matter from a placer drawing a
lawful map differently (next sections).

## Time traded for memory, deliberately - read before speeding up a render or the tests (2026-10-04/05)

The containers share a 10 GB cap, and several sessions run gates and renders at once; the GM chose, measured, to give up
some render and test time for memory (session `diagram-performance`: *"we got a huge savings in RAM. And it did add a little
bit to our render time, but in this case that is fine"*). Each trade below is DELIBERATE. Undoing one buys its time back
and costs its memory back - put that cost to the GM, with this table, before taking it.

| trade (where it lives) | memory it buys | time it costs | the record |
|---|---|---|---|
| A picture renders at most 3 tiles at once (`raster.TILE_WORKERS`) | a 20-household render's peak ~970 -> ~540 MB | render 2.2 -> 3.2 s | specs/324-render-memory R2-R3 |
| The stitch child decodes one tile at a time (`raster._PICTURE_CHILD`) | the child 300 -> ~185 MB | none measured | specs/324 R2 |
| The post-landing render step runs at most 4 maps at once (`render_cache.RENDER_JOBS`) | its peak 1.73 -> 1.12 GB, p90 737 -> 434 MB | ~60 -> ~72 s, detached | specs/324 R1-R3 |
| Each tile renders only its part of the map (`raster.tile_doc`) | that render's peak ~540 -> ~370 MB | ~+0.3 s | specs/326-tile-clip R2, R4 |
| 6 test workers, not 10 (`XDIST_WORKERS`, the Makefile note) | a gate's peak ~4.5 -> ~3.1 GB | ~20% of the gate's time on a QUIET machine only; none under the sessions' usual load | the Makefile note at XDIST_WORKERS |

Measured with all three render trades in place (observed 2026-10-04/05, method: a 50 ms process-tree RSS sampler over
`make hamlet ARGS="--name MemTest --seed 4 --households 20 --out <dir>"`): the rendered hamlet peaked ~970 MB before
feature 324 and ~370 MB after feature 326, its render span ~2.2 s -> ~3.5 s. Levers measured and NOT taken, so they are
not re-derived: a finer tile grid (4 x 4 to 7 x 7 saved 10-20 MB more and every one broke the time bound; a grid change also
moves tiling's seam differences, specs/326 R2-R3); clipping whole lines only (byte-identical, ~130 MB instead of ~170 -
the GM chose trimming, which is visually but not byte-identical, specs/326 R4); choosing the worker count from the load
at launch (the GM: the load "can go from very low to very high very quickly", the Makefile note).

If render time is the ask: feature 327 already took the clip's no-memory saving - each line's extent parsed once per picture
(`raster.prepare_doc`), the clip's CPU ~0.9 -> ~0.12 s, the render span 3.55 -> 3.21 s - and found that a faster clip lets the
tiles start together and RAISES the peak unless the renders are capped; `raster.RESVG_SLOTS` (four resvg processes per
process) holds it level (374.6 -> 370.6 MB mean; specs/327-lean-site-fast-clip R3). Raising that cap is a time-for-memory trade
like the rows above. The next no-memory starting point is the stitch's JPEG encode of a 32-megapixel picture. The record site's
build holds its pages as UTF-8 since feature 327 (`site.SiteFiles`, the single page built as bytes): its peak 236 -> 165 MB, its
result 148 -> 84 MB.

## Shape one: a per-candidate scan of geometry that does not change during the scan

**The one performance bug this engine keeps growing, and how to find it.** Every slow gen ever
profiled here has had the same shape: *a per-candidate scan of geometry that does not change during
the scan*. Minami silently became a **45+ minute** grind that way when the paddy-well rule landed
(`_well_ground_clear` rebuilt all 927 drawn basins per candidate seat, ~133k seats). The 2026-08-03
sweep then found four more instances, all in code that looked perfectly reasonable: `on_crop`
re-deriving every plot's bbox per seat, the ground-cover scatters testing every field/block polygon
per scatter POINT, `_near_corridor` walking every corridor segment, `_in_blocked` visiting every
keep-out. Together they were over half of the pool's runtime. The cures, in order of preference:
hoist the invariant out of the loop; add a bbox prefilter (`boxed_polys`/`boxed_hit`); index it
(`PointGrid`, or `Indexed` where the registry is mutated as you go). Never coarsen - see "When a
check is slow, INDEX it" below. The second pass (2026-08-04) found four more of the same shape:
the well memo's own FINGERPRINT (now a `frozen_terrain` scope, which asserts the invariant instead
of guessing it), `_fits` measuring every standing building, the ground-cover keep-outs, and a city
gen testing each candidate against every label on the map.

**The SECOND shape, found once the first was exhausted (2026-08-08): the same scan run again over
ground that has not changed.** Minami's dwelling `top_up` evaluated **511,519 candidate positions**
- effectively its whole runtime - and **64.6% of them were RE-visits of a seat an earlier pass had
already refused at the same tightness**, because the caller sweeps each caste's regions three times
over and again in `fill_exactly`, always on the same fixed 5x6 px lattice. `settlement.SeatMemo`
remembers refusals across calls: **21.0s -> 14.5s, and every manifest byte-identical**, because a
refusal only turns into a placement if an obstacle DISAPPEARS and nothing in a top-up phase removes
one. Three things about it are worth carrying to the next instance of this shape:

- **The memo ASSERTS the invariant instead of assuming it** (`sync()`), the same discipline
  `frozen_terrain` applies to the well memo. A registry that is rebound, truncated, or changed by
  anything but an append clears the memo - so a future gen that frees ground loses the SPEEDUP, not
  a hundred houses. That failure direction is the whole design.
- **Byte-identity is the oracle here, and it is a stronger one than the brief expected.** A memo
  that only skips work is output-preserving by construction, so any drift in a manifest is a
  soundness bug and not a judgment call - which is why this needed no `settlement-review` pass.
- **Measure the re-visit share PER GEN before wiring it in.** The same memo was fitted to Nagahara
  and Tango and made both SLOWER (9.56 -> 10.29s, 9.71 -> 10.19s): their re-visit shares are 3.1%
  and 0.0%, so every candidate paid the probe and almost none saved a test. Minami is the outlier
  because the Fox eight-temple doctrine leaves its packs unable to seat anything and its merchant
  target unmeetable. Below roughly a third re-visits, this is a pessimization.

Two levers deliberately NOT taken, so they are not re-derived: an `ok()`-level memo (that test is
pad-independent, so it is re-run once per pass) would spare 33,810 of the remaining 181,085
evaluations, but they are the CHEAPEST ones - and capping the unmeetable caste targets, which the
memo has already made nearly free. Both were measured, both are worth well under a second.

**And trust the A/B, not the profile's seconds.** cProfile charges its per-call overhead to
whatever has the most calls, which is exactly these tight inner loops - it valued the ground-cover
grid at 3-4s where the A/B measured 1.1s, and the well fingerprint at ~8s where the A/B measured
6.4s. Use the profile to find WHERE the time is; use `git stash` and two timed runs to find out
whether you actually saved any.

**If a gen ever "hangs", suspect that shape FIRST and profile before bisecting.** A timeout-based
bisect probe cannot distinguish "broken" from "slow", and one burned an hour here concluding an
innocent commit was the regression.

**And beware the CACHE you add to fix it** - two of the three staleness bugs in this file's history
came from the cure, not the disease (see `Indexed`, `_wgc_cache` and the comment in `_fits`). A
cache key built from lengths, record counts or object identity is a GUESS about content; `placed`
gets rebound to a filtered copy, and a field's `plot_polys` gets replaced with a same-length list,
and both guesses were wrong within a day. Prefer a registry that versions itself (`Indexed`), and
make sure the key is cheaper than the scan it guards - one fingerprint here cost more than the scan
it replaced.

Since 2026-08-03 the sweep ENFORCES a per-gen CPU budget (`GEN_TIME_BUDGETS` in
`tests/test_villages.py`) so the next silent 45-minute-class regression fails loudly by name instead of
being waited out; `DIAGRAM_ALLOW_SLOW_GENS=1` overrides once you are certain perf is fine, and a
legitimately-outgrown map gets a bigger budget entry WITH its reason. **Budgets are calibrated
against the GATE, not a solo run** - under `pytest -n auto` a gen's own CPU time inflates 2-4x
through cache contention, which is why each entry is ~4x its recorded solo measurement.

**A GEN'S CPU TIME INFLATES 2-4x INSIDE THE GATE, so budgets are calibrated against the GATE, never
a solo run** (`tests/test_villages.py` says this at the table; both halves of it were found the same day,
independently, by two sessions whose gates were slowing each other down). `process_time` is immune
to WAITING for a core but not to needing more cycles for the same work, and `-n auto` runs 22
workers here. Measured pairs, solo vs under-gate: hoshizora **12.4s / 35.7s**, kuwabata **16.8s /
36.4s**, enokida **19.9s / 31.9s**, kikuta **10.9s / 36.2s**, minami **~54s / 154.8s**. Which map
trips therefore depends on what else is on the box, so **diagnose before touching anything**: re-run
the named gen ALONE (`make map GEN=pool/<tier>/<map>/<map>.gen.py PROFILE=1` with nothing else running). Far
under budget alone means contention, not a regression.

The resolution, and one dead end worth not re-walking:

- **What the guard does now:** each entry is ~4x its SOLO measurement (~1.5x its worst observed
  under-gate time), which still nets the class of bug this exists for - the motivating regression
  ran ~250x over budget, not 20% over. An optimization pass the guard's first run prompted (the
  `on_crop` bbox hoist, ground-cover prefilters, a well-siting `PointGrid`) roughly halved every
  heavy gen, so the budgets sit on faster code too.
- **Do NOT try to auto-calibrate** by timing a proxy workload in the worker and scaling by the
  inflation it reports. The proxy has to stall the way a gen does and no cheap loop does: a tight
  arithmetic loop is L1-resident (1.56x under a controlled 20-way load, but 1.0x during a real
  sweep in which minami inflated 2.9x), while a DRAM-striding walk is already latency-bound and does
  not inflate at all (0.95x). A point sample after the gen cannot represent contention during it
  either. Tried and reverted 2026-08-03.
- **The override must not silence the guard's own self-test.** `DIAGRAM_ALLOW_SLOW_GENS=1` is
  documented for whole-sweep use, and it used to silence the budget for
  `test_slow_gen_budget_fires_and_the_override_silences_it` as well - so the one test proving the
  guard has teeth failed exactly when a session followed the advice, making the escape hatch a
  guaranteed red gate. The test now clears the variable for itself. Any future env-driven escape
  hatch needs the same treatment.

## Shape one, found again in the lane router (feature 138, 2026-08-28)

The GM asked why a 16-household polder cost ~100 s when *"even with an n squared or an n cubed
algorithm, I wouldn't expect that to matter"*, and the profile agreed with the GM: not NP-hard, not
the field bisection the budget file blamed, but shape one - `ways._route` built its free lattice by
calling `clear_runs` once per cell (165,611 calls on seed 19), and each call re-derived every
polygon's bounds from its vertices and then measured the sample against every edge of every polygon
that survived (36 million `seg_dist`, 106 million `max`). `path_violations` compared every pair of
water crossings for the deck-length rule - on a polder whose parallel ditches give a connector
hundreds of crossings, 170 million `hypot`. Three other stages had the same disease at smaller size:
`fixture_clear_of_water` walked every watercourse segment for each of 17,407 notice-board probes;
`_clear_link` / `_clear_touch` rebuilt their prefilter 4,969 times on identical fabric.

The fix is the doctrine below applied literally: `hamletgen/clearance.py` files every polygon and line
by grid cell once (memoized on the inputs' identity while the same lists are passed around; entries
spanning more than 256 cells are tested by bounds rather than filed), `_route` derives its whole
lattice from one index, `pairs_within` buckets crossings by cells of the deck length, and
`_geom/water_index.py` files the watercourses once per settlement. All of it returns the SAME
verdicts - a superset of candidates measured with the same predicate - so every gate roll and every
live pool map came out byte-identical (the feature's sweep). Measured solo: the seed-19 polder
110 -> ~30 s, the reference hamlet 37 -> ~21 s. What remains is spread over `stage_homesteads`
(the bundle fit's `point_in_poly` on large polygons), `stage_hinterland` (scatter samples against
the commons outline) and, on comb hamlets, `fit_field`'s seven `build_comb` rounds - each a few
seconds, none of them the router's shape, and the solver is left alone because a different
convergence draws a different map.

## When a check is slow, INDEX it - do not coarsen it

The gate's cost is dominated by a handful of checks that ask a local question with a global scan.
Profile before guessing (`cProfile` around the retired `check_village.gate` on `tango.json`, the worst case - kept because the SHAPE of the finding outlived the battery):
2026-07-25 found `city_fan_heads_quilted` testing ~3,000 canal-side samples against EVERY plot
polygon and ditch (14M `seg_dist` calls, ~58% of a 17s city gate) and `structures_clear_of_dry_plots`
testing every structure against every dry plot (3.5M `segments_cross` calls). Both were fixed with
`GridIndex` (a uniform-grid spatial index in `l7r/diagram/overlap/matrix.py`): insert each feature
under the cells its influence bbox touches, query the cell, then run the SAME exact test on the few
candidates. Result: Tango 17.3s -> 2.9s, whole-pool gate 34.1s -> 11.8s, `make done` ~2min -> 77s,
with **byte-identical verdicts on all 695 manifests** (pool + regression corpus).

The rule that matters FOR A CHECK THAT VERIFIES A RULE (a gate test - not a placer; a placer may decide
differently and move maps, see "Maps may change for speed" above): **the index prunes, it never decides.** It is always
tempting to make a slow check cheap by making it coarser - testing a bounding polygon instead of the real features, sampling
fewer points, raising a tolerance. That trades correctness for speed and the loss is invisible until
a real defect slips through. Indexing costs ~15 lines and changes no verdict, so there is no reason
to reach for coarsening first. (Concretely: `structures_clear_of_trees` must test the recorded
CROWNS, not the stand outline, because placement drops crowns individually - an outline test would
fire on trees that were deliberately never drawn.)

Verify a check's optimization the same way: its verdicts on every input it judges before the change and after,
diffed. Anything but "none" means the optimization changed behavior.

### A `GridIndex` box is a COST, so clamp it - on insert AND on query

`GridIndex` allocates a dict entry per 120 px cell of the box it is handed, in both axes. That is
fine for anything on the map and catastrophic for anything that is not: a (since retired) negative fixture
planted a wall vertex at **9,000,000** on a
3,200 px canvas, so the moment `wall` became a SOLID in `OVERLAP_CLASS` and got stroked into quads,
so one feature asked for ~5.6 billion cells. The gate ate gigabytes of RAM and the GM had to kill it by
hand (2026-07-26). **Negative fixtures contain deliberately insane geometry - any new code that
consumes raw manifest coordinates will meet it.**

Two rules, and the second is the one that is easy to half-do:

1. **Clamp the index box to the canvas** (`meta.W`/`meta.H`, generously - a couple of canvases of
   slack). Clamping only shrinks, and a polygon's on-canvas part is always inside the clamped box, so
   no real overlap can be lost. Geometry wholly off the canvas is skipped; that is
   `city_geometry_within_canvas`'s business, not the overlap matrix's.
2. **Clamp the QUERY box too.** `near_rect` walks the cells of the box it is *given*. Clamping only
   the insert leaves the query iterating exactly the same billions of cells - which is precisely the
   half-fix that shipped first here and looked plausible for a whole turn.

`test_matrix_survives_geometry_far_off_the_canvas` is the guard, timed rather
than structural on purpose: the failure mode is unbounded work, and the correct-vs-broken margin is
a fraction of a second against effectively forever.

## The three bands, and who answers for an increase (feature 129, 2026-08-25)

The GM's matrix, evaluated on BOTH measurements and PER ENVIRONMENT (local against local history,
CodeBuild against CodeBuild - a cross-environment pair is REFUSED, never displayed):

    band            TOTAL          ANY SEED     what it takes
    (band 1's line is PER ENVIRONMENT since feature 179: 0.0% local, 2.0% codebuild - see
     perf_bands.BAND1_PCT, where the 5-of-6 noise measurement that bought the floor is recorded)
    1  explain      over the line  over the line         `make perf-explain WHY=... CONTROL=<key>|UNVERIFIED="..."` (yours) + `make perf-confirm ... AS=perf-audit` (the subagent's)
    2  audit        > 5%           > 10%        `make perf-audit VERDICT=justified NECESSARY= COMMENSURATE= NO_WAY_AROUND= AS=perf-audit`
    3  GM sign-off  > 10%          > 20%        `make perf-signoff WHY=...` - the GM, at a terminal, before the push

`make perf-report` / `make done` PRINT the band and the stages that grew (FR-009b); `make perf-review`
- run by `sync-with-main.sh` at the push - ENFORCES it. Records are one file per event in
`dev/perf-log/`, bound to the end snapshot's commit and exact percentages: a stale one is refused by
name, a negative or inconclusive verdict never counts.

**Why the subagent's commands prompt instead of checking.** Measured 2026-08-25: a subagent's shell
carries the SAME `CLAUDE_CODE_SESSION_ID`, `CLAUDE_PID` and parent as the main session's - nothing
distinguishes them. So `perf-confirm`/`perf-audit` print the GM's words ("if you are the main
session, you should not continue") and decline without `AS=perf-audit`; the declaration is
recorded, and what a self-grant costs is a false analysis written into a tracked file.

**Evidence is tiered, and tier 1 is free.** Every snapshot already carries a per-stage breakdown;
the report prints which stage grew and by how much, and that answers most band-1 and band-2
questions. When it cannot say WHICH FUNCTION, `make perf-profile SEED=n STAGE=s` runs cProfile on
that one stage of that one seed - measured at +225% on the real generation workload (27.4 s -> 89.0 s
on seed 4), which is why it is triggered, never always-on. The derived top-25 table (kilobytes) is
committed; the raw `.prof` stays in the gitignored `dev/perf-raw/` and goes to the profile-archive
repository `EliAndrewC/mapgen-perflogs` (the default; `PERF_ARCHIVE=` empty disables it), pushed with the
CodeBuild PAT through `scripts/git-askpass-token.sh`; a failed push degrades to a message.

**If the harness does not know the `perf-audit` agent type** (it loads `.claude/agents/` from
`/diagram` at session start, so a session that predates the file - or runs before it lands on main -
gets "Agent type 'perf-audit' not found"): launch a `general-purpose` agent and tell it to read and
follow `.claude/agents/perf-audit.md` as the `perf-audit` role. That is how feature 129's own
confirmation was produced on 2026-08-25. The record still says `declared: perf-audit`.

## The same shape, a third time: the ring itself (feature 145, 2026-08-28)

The rule at the top of this file - a per-candidate scan of geometry that does not change during the
scan - had been applied to WHICH polygons a lookup tests (the boxed prefilters, `PointGrid`,
`FabricIndex`) and not to the polygon once chosen: `point_in_poly` and `edge_dist` still walked every
edge of a 40-60-vertex outline for every one of ~135k scatter throws, and `FabricIndex.fouled`
walked every edge of the field envelope (a `big` entry, tested on every lookup) for each of 1.2M
router cells. That was 60% of the reference's hinterland stage and 70% of seed 25's whole roll. The
answer is `RingIndex` (`settlement/_geom/indexes.py`): the ring's own edges in a grid, so inside and
distance-to-edge touch only the edges near the point, with verdicts identical to the linear scan.
When you find a `point_in_poly(...)` or `edge_dist(...)` inside a loop over candidates, that is the
next one. Measured: seed 25's web 35.6 -> ~4 s; the cohort's four-seed total 128 -> 48 s.

A solver has the same shape in a different coat: `fit_field` carved the whole comb nine times per
aspect to bisect a multiplier whose first carve already predicted the answer, and kept carving at
aspects where the fan had saturated. Predict from the curve's own shape (acres ~ k^2), probe the
bracket's end once to detect saturation, and stop when the bracket is narrower than a plot row.
Seed 47's field: 39 carves -> 8.

## The third shape: the index that exists, beside the scan that does not use it (feature 218, 2026-09-08)

The GM asked whether a 7.3 s windbreak stage was *"doing some kind of overlap check every time we
place an individual tree"*, and proposed the fix in one sentence: *"Start by drawing the outline of
where the Windbreak Forest is going to be, and then we lay down all of the trees within that
outline"*. The profile agreed. `village_grove` tested each of 37,490 candidate clump positions against
every edge of every crop polygon and every watercourse segment, linearly, in pure Python - 7.19
million `seg_dist` calls, 77% of the stage, to keep 150 clumps - while `field_polys` was already an
`Indexed` registry with a spatial index the farmhouse placer queried, and `boxed_rings` /
`boxed_seg_hit` had answered exactly these questions for the ground-cover scatters since feature 145.
The marsh scatter was the same shape one level down: its watercourse test HAD a pre-boxed grid
(`wat_b`) and bypassed it for every mark carrying a mound pad - which is every tint circle and every
reed tuft - so `_watercourse_segs` was rebuilt, taper split and all, 20,964 times per roll (73% of the
hinterland stage). Shape one was cured in the scatters in 2026-08; the cure sat beside the code that
still had the disease.

What changed, and what each bought on the reference hamlet's seed 4 (real seconds, `make map
PROFILE=1`; the maps byte-identical after every step):

| stage | before | after | what |
|---|---|---|---|
| `stage_windbreak` | 7.27 | 0.50 | `GroveBlocks` (`homestead_parts/grove_blocks.py`): every keep-out of one grove fill indexed once; `Seats` files the clumps as they land |
| `stage_hinterland` | 8.09 | 2.60 | the marsh's watercourse grid per pad (the `mnd_g` treatment the crests already had) |
| | 2.60 | 2.42 | the scatters' urban halo indexed; the strip and trunk tests' `Footing` built once per pass; the parcel scan's crops boxed |
| | 2.42 | 1.27 | `KeepoutGrid`: EVERY keep-out of a scatter in ONE grid, one cell read per point instead of ten; `_crop_refuses` from a ring index; the crescent-pond registry read once |

**Rules learned, beyond "index it":**

- **An index that is built and not asked is the same as no index.** The marsh's grid was correct
  and unused on the hot path. When a `near=` or `idx=` parameter exists, grep every caller for the
  one that passes `None`.
- **One grid per scatter, not one per family.** Ten indexed families cost ten `near` calls and ten
  wrapper calls per point, most returning an empty cell - 1.33 million `near` calls on 134,877
  points. `KeepoutGrid` files rings, segments, rects and circles together, tagged, and a point loops
  once over what its cell holds. A family whose pad varies per query (a glyph's lean, a mark's mound
  pad) files its base and a slot, and the query passes the extras.
- **Exactness was kept here because it happened to be free - it is not a requirement.** Every conversion
  above kept the linear scan's own expression as the deciding test - down to the association of a float
  sum (`w / 2 + (2.0 + pad)`, not `(w / 2 + 2.0) + pad`) - and the pool regenerated byte-identical after
  each. The GM relaxed the requirement mid-feature (*"It is absolutely not required that the changes ...
  result in bite identical output"*) and later ruled it out as a constraint altogether (feature 297,
  "Maps may change for speed" above): a faster form that moves maps within the rules is preferred to an
  exact one that is slower.
- **What is left is the algorithm, not a scan.** After the conversions the hinterland's 1.27 s is
  the commons scatter's own work per throw - 866k `random.uniform` draws, a million outline tests,
  158k feather distances - in Python. The levers that change what a map draws are recorded
  in `specs/218-efficient-overlap-checks/research.md` R2 for the GM's decision, not taken.

## Shapes the later passes found - what to look for next (features 276-314)

Each line is a rule a pass paid to learn; the pass's numbers are in its spec.

- **A generate-and-test seat search: answer from the free ground** - index what is placed, raster the static ground as
  SURELY TAKEN cells, and put the cheapest exact conjuncts of an order-independent conjunction ahead of the full test.
  Check which path a scenario exercises before believing its profile (the test toy ran a path no pool map runs) (276).
- **Batch per-piece geometry; never compute the same result twice.** Shapely 2 takes arrays. A batched pass that
  reorders float work can move a map by a hairline; fix the guard that misreads it, not the batching (276).
- **A test that re-derives what another derived: parse or scan once per process** (`tests/_engine_ast.py`), and a nested
  walk is the same shape inside one test (276).
- **A check called far more than it should be is sometimes a wrong answer, not a slow one** (`seg_intersect` answered for
  the infinite lines through two segments) (276).
- **A memo whose key walks every polygon is not free; an index keyed by a parameter the caller varies is one index per
  value; a harness counter keyed by FILE reads zero once a function moves** (278).
- **Grep a module for `seg_dist` / `segments_cross` inside `any(` / `min(` over a whole registry** - that is where the scans
  the index doctrine missed were, each a sibling of indexed code (281). Share an index by CONTENT, not identity, when the
  same ring is filed again and again (281).
- **Count the calls made BENEATH a mechanism's entry, and record the bucket's total beside the named count**: a named count
  that falls while the total does not is work that merely moved (281).
- **Price a vectorization by the stage's wall time, fastest of three, not by the calls it removes** - profiling inflates
  Python calls and not C, so the profile favors it (278, 281). Building the shapes is often what it costs.
- **Measure by the wall clock, sampled fairly**: a thread reading the main thread's stack every millisecond with
  `sys.setswitchinterval(1e-4)` - at the default 5 ms it over-weights whatever releases the GIL (297).
- **A region's cost is its painting.** Paint with PIL's own primitives, not shapely buffers; PIL's `floodfill` is pure
  Python (a run-length union-find labels the same components ~10x faster); and a fill on an image that shares numpy's
  buffer (`Image.fromarray`) silently paints nothing (297).
- **Order questions cheapest-first, never "position first"; ask the route (the dearest question) last** (297, 308).
  Settle a seat when it is OFFERED, not when it is queued (308).
- **Pruning that the rules would have refused anyway saves only what the refused candidates cost** (297); **an index is not
  free - measure it against the scan** (304); **when a search's success is near chance, the lever is the capacity it searches
  in, not the order it searches** (306).
- **A moving lever is kept only after the gate passes on the moved POOL** - a cohort comparison measures reach and time, not
  the pool's seed tests; never judge one lever with another in that has since changed; a lever's own stage can halve while
  the rolls get slower (284). A check that reads "whatever is left" passes when the thing it should fail on was deleted
  first (284).
- **A finished-map test's cost is the roll it reads, and that roll is shared**: retiring one frees little unless it was the
  roll's only reader (287). Keep wall-clock seconds OUT of a manifest, or every regeneration rewrites every map (287).
- **The live instruments**: the perf bookend rolls the reference at 10 / 20 / 40 households (`perf_snapshot.SCALING_SIZES`)
  and bands each size against its own history, so a slowdown that shows only at a village's size cannot land green (304);
  `make census` counts comparisons per call of every check the pool's rolls run and flags one over 5,000 (306).

## Memory: what the gate's RAM is, and the rules it left (features 208, 210, 2026-09-13 profile)

- **A render is made on the render condition, never on the roll**: a test roll writes the vector-only page (208).
- **Large C buffers are made in a child process** (the picture's decode and encode), so the worker never holds memory the
  allocator will not return (208).
- **A per-roll memo is cleared when the roll ends** (`driver.roll_scope()`, which every stage-running loop enters - a static
  test walks the engine's AST for loops that call a stage outside it), **`malloc_trim(0)` when a roll ends**
  (`_memory.trim_heap`), and **the roll itself runs in a child** where it can (210).
- **A kill is decided by `anon`**; the cgroup's `file` is the kernel's reclaimable page cache, not memory held by mistake (210).
- **An `xdist_group` mark in a `conftest.py` applies to nothing** - pytest reads module marks only from the test module - so
  the one-Chromium rule lives in each browser test module's own `pytestmark`, and `tests/test_markers.py` asserts it from
  the AST. A third-party import only some workers need goes inside the fixture (2026-09-13).
- **Our own code is the small part of a worker**; the RAM is in COPIES and PROCESSES - every worker imports everything, and
  the tooling tests' real sub-gates (2026-09-13). The time-for-memory trades are the table at the top of this file.

## Levers measured and withdrawn - do not re-try

Each was built, measured and taken out (or priced and declined); the spec named holds the numbers.

- `SeatMemo` on a map whose re-visit share is under about a third; an `ok()`-level memo; capping the unmeetable caste
  targets - above.
- Auto-calibrating `GEN_TIME_BUDGETS` from a proxy workload - above.
- The marsh scatter thrown and tested as arrays (`specs/281-third-hotspot-pass`).
- A crown grid per grove clump (`specs/284-fourth-hotspot-pass`).
- A* in the router; the field's size search without its blind probe; a coarser router lattice; the carve's rows in arrays;
  the notice board's 24 px lattice - they strand, run slower, or break a rule (`specs/284-fourth-hotspot-pass`).
- The full-pitch lattice offered first in the exhaustive seat pass - a change of form, not of speed
  (`specs/287-placer-guarantees`).
- Each keep-out buffered with shapely before painting a region (`specs/297-placement-by-construction`); a line-of-sight reach
  region, priced and not built (same).
- The access tree's targets from a ring; the exhaustive pass pruned three ways - the region re-asked per house, homesteads
  painted, a straight-corridor precheck (`specs/304-homesteads-at-scale`).
- Capacity predicted by packing boxes; seats proposed beside the tree, grown from the houses, or along planned frontage lanes;
  a wider corridor search alone; the shared sheds at the band's rim; the canvas grown with the seating band
  (`specs/306-seat-by-packing`).
- Straight grown paths only; an exact grown seat with no computed move (`specs/308-grow-the-cluster`).
- The route searched off the household's own beds and fixtures (it broke the lane law once the web drew it); the map's grid
  for the route; the house and its yard asked before the layout; a heavier weight on the search's aim; seats with a straight
  run to the tree offered first; the pre-check at the settle's first position only (`specs/314-seat-before-settle`).
- A finer render tile grid; clipping whole lines only; the worker count chosen from the load at launch - the memory table
  above (`specs/324-render-memory`, `specs/326-tile-clip`).
- **Laying the lanes before the houses** - DECLINED by the GM (2026-10-02): lanes are trodden by villagers walking between
  homesteads already built, and it was tried before and made the seating harder ([`placement.md`](placement.md)). Do not
  offer it as a performance lever again.
