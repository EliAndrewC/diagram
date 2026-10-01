# Performance: the two shapes this engine keeps growing

**Load this file when:** A gen or a check got slow (or "hangs"), you are about to optimize one, or a GEN_TIME_BUDGETS entry tripped.

Split out of [`../CLAUDE.md`](../l7r/diagram/CLAUDE.md) so it is not in every diagram session's
context. The text is verbatim; the short always-on version of each rule stays in the index.

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
the named gen ALONE (`DIAGRAM_SKIP_RENDER=1 python3 -c "import time,runpy; t=time.process_time();
runpy.run_path('pool/<t>/<m>.gen.py', run_name='__main__'); print(time.process_time()-t)"`). Far
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

Verify an optimization the same way: capture `sorted(gate(M))` for every manifest in `pool/**` before
the change, re-run after, and diff. Anything but "NONE" means the optimization changed behavior.
Run that sweep with `-n auto`-style parallelism or in the background - serial it is ~13 minutes.

### A `GridIndex` box is a COST, so clamp it - on insert AND on query

`GridIndex` allocates a dict entry per 120 px cell of the box it is handed, in both axes. That is
fine for anything on the map and catastrophic for anything that is not: the regression fixture
`city_geometry_within_canvas_fires_on_a_stray_vertex.json` plants a wall vertex at **9,000,000** on a
3,200 px canvas, so the moment `wall` became a SOLID in `OVERLAP_CLASS` and got stroked into quads,
one feature asked for ~5.6 billion cells. The gate ate gigabytes of RAM and the GM had to kill it by
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
  158k feather distances - in Python. The levers below that change what a map draws and are recorded
  in `specs/218-efficient-overlap-checks/research.md` R2 for the GM's decision, not taken.

## Three more shapes, found before the city tier (feature 276, 2026-09-28)

The GM, on the hamlet tests: *"I'm less interested in optimizing specific tests as I am in getting to the root of
these inefficiencies"* - a city has thousands of inhabitants, and a cost that grows with what is already on the map
becomes the whole run there. Every figure below is in `specs/276-engine-hotspots-and-test-scans/measurements.json`.

**A generate-and-test seat search: answer from the free ground.** The dispersed placer walked a 157-offset spiral
per house, built the whole bundle at each offset and ran the full fit test on it; the nucleated placer and every sun
rule scanned every house already standing. On the rescue scenario that was 46,781 full fit tests for ten houses, and
at constant density the cost per seated house grew with the houses already placed. The fix is three indexes and a
pre-screen: the placed houses in an `Indexed` list with a grid of each record's extent (the eave gap, the sun rules
and the yard-sun rule ask it for their reach box); the site's static ground as a raster of SURELY TAKEN cells
(`FreeGround` - the forbidden union shrunk by half a pixel, so a cell is claimed only where every point of it is
refused); and, ahead of the full test, the cheapest exact conjuncts of an order-independent conjunction
(`_seat_refused`, `_bundle_refused`). The bundle is built once per household as a template and moved per seat.
Measured: 2.718 s and 46,781 fit tests -> 0.35 s and 128 on the rescue scenario (dispersed); 29,372 fit tests -> 304
at 240 seeds; per-house cost flat from 60 to 240 seeds on both paths; the same houses seated (five-layout totals
within 2%). **The trap**: the test toy never set the placer's own nucleated switch, so the first profile measured the
path no pool map runs - check which path a scenario exercises before believing its profile.

**A chain of per-piece geometry calls: batch it, and never compute the same result twice.** `close_seams` was ~1 s
per comb field, hundreds of one-polygon shapely calls: `Polygon(ring).buffer(0)` rebuilt per plot in five passes, a
buffer computed twice to keep a piece and again to throw it back, a spatial tree rebuilt whenever any ring changed,
a pocket's grid cutting every cell of its bounding box (a diagonal sliver ~1,400 cells). Shapely 2 takes arrays:
`ring_polygons` builds every plot in two calls, `_despike_many` opens a list at once, a tree query plus
`relate_pattern("T********")` finds only the neighbors whose interiors overlap, `PlotGeoms` keeps its tree and tests
only the rings that changed, and `_plant` cuts only the cells a connected piece of each row reaches. 0.81-0.98 s ->
0.39-0.45 s on seeds 5/11/17, back to back against the unmodified engine. **The trap**: a batched pass that reorders
float work moves a map slightly - here a weld came out with a 0.5 px hairline spur, and the weld guard read only the
deduped ring while the gate reads the ring as recorded. The fix went to the guard (`_weld_apex`), not the batching.

**A test that re-derives what another test already derived: parse or scan once per process.** Four AST tests each
parsed all ~264 engine modules and walked 1-1.5 million nodes; five record tests each rebuilt the same id tables and
re-scanned the record per page or per term. `tests/_engine_ast.py` parses a file once per content (a counter the tests
assert on), the scans take a needle so a file without the keyword is never parsed for them, and the record tests build
their tables once. One scan walked every function's subtree separately, so a body n functions deep was walked n times -
a nested walk is the same shape inside one test. Two record tests each ran a lookbehind-led pattern at every
position of all ~7,900 tracked files; the pattern can only match inside a run of path characters around a `.md`, so it
now runs over those runs alone, once per text for both tests (`md_tokens`), and a multi-word glossary variant is tried
only where its first word starts rather than searched for across the whole record. The five record tests: 17.2 s alone
summed -> 2.55 s together; the four AST tests 2.12 s together against one parse of 1.79 s.

**And a correctness bug the profile found.** `seg_intersect` answered for the infinite LINES through two segments, not
the segments, so the track refused candidate paths on crossings that were not there - 0.966 s of path checks over 176
calls became 0.139 s over 83 once bounded, and 0.011 s with the `PathChecker` index over the same 83. Several maps'
tracks moved (Inashiro's connector now leaves east), each the same hamlet on the same rules. A profile that shows a
check called far more than it should be is sometimes a wrong answer, not a slow one.

## The second pass, and where the returns start to diminish (feature 278, 2026-09-28)

The GM: *"If we run through exactly the same exercise a second time, then I expect we'll turn up even more. Eventually
we'll reach a point where we've optimized as much as can be expected."* The same exercise - every pool hamlet rolled with
each stage timed and each mechanism counted, each heavy stage profiled alone - found nine more per-candidate scans and
one roll done twice. All figures are in `specs/278-second-hotspot-pass/measurements.json`, taken back to back against the
base; the pool's five rolls went from 60.5 s to 35.0 s together.

**The scans, the shape of the first section again.** The router judged its whole search box - up to 90,000 cells - before
Dijkstra ran; now each cell is judged when the search first asks (2-5x fewer cell tests, the same paths). A doorstep search
rebuilt one memoized index's KEY per candidate - a memo whose key walks every polygon is not free (3.6x fewer asks). The
footbridge widening tested every watercourse segment per deck (56x fewer); the wells re-sorted their whole pool on every
pass, including passes that placed nothing (Kuwabata's appurtenances 1.77 s -> 0.09 s); the carve's hem pass asked
point-in-polygon of every plot per sample (81-96x fewer); the notice board measured every way segment and every hard
polygon's box per verge probe; the windbreak asked seven grids per candidate and read a 128 px cell to find neighbors
within 10 px; the page merge walked every extent in a bucket per element (57-66x fewer). **Two traps worth carrying**: an
index keyed by a parameter the caller varies (`_ok` is re-asked with a different `half`) must be one index per value -
the first cut used one and moved a woodland parcel, caught only because the exact pieces are held to byte-identical
manifests; and a harness counter keyed by FILE reads zero once a function moves (`_hits`, now in `extents.py`).

**A roll done twice.** Sawada seated a farmhouse 157 px deep inside its paddy field, where no way can ever be drawn, so the
driver re-rolled it every time - and finished the discarded attempt first. The placer now refuses a seat deeper than any
way's reach inside the web's hard ground (`UnreachableGround`), and the driver finishes only the attempt it keeps. (Since
feature 287 there is no second attempt: the reach is guaranteed where the web settles, and `generate` builds once.)

**Vectorizing is not free.** The commons grass, thrown and tested as numpy arrays, was first SLOWER than the per-point loop
it replaced: building a shapely shape for every keep-out on the map, per call, cost more than 16,000 in-frame points took
in Python. It paid only once the shapes were built for the items near the throws, unioned and PREPARED (a tree query
returning pairs was the slow step), and invalid rings drawn as their even-odd faces instead of their whole box. Exactness
held throughout: points surely in or surely out are decided in arrays, and the band between them by the scalar test.

**What is left, priced - the next pass's levers** (none taken here; the spec's Amendment 1 records why):

| stage | measured after | what is left | the lever, and what it costs |
|---|---|---|---|
| field | 1.075-1.23x per build (Sawada) | the carve's per-row geometry, 4 carves per build on Inashiro and 3 on Kashikawa (the fit's size search) | a closer first guess of the fan's size, or the rows as array operations - both change the field |
| hinterland | 1.20-1.28x | the marsh scatter (the commons' old per-point shape), the bamboo seats' 10,000 samples, the parcels' crop set-backs | the marsh vectorized as the grass was; coarser bamboo sampling - a drawing change |
| notice | 1.19x Inashiro, 1.87x Sawada | the verge probes (9,708 `_fits` calls in Sawada's build, 8,001 in Inashiro's), each through the indexed `_fits` the scoring needs | score first, fit only the probes that could win - changes the seat when two tie |
| windbreak | 1.43x Kashikawa, 1.51x Inashiro | 128,952 candidate points on Kashikawa through Python predicates | the static tests over the jittered grid as arrays, the spacing test sequential - the commons' hybrid applied to the grove |
| finish | - | about 4.7 s profiled over three finishes waiting on the external renderer (PNG and page raster) | fewer or smaller raster tiles; out of this pass's scope (the render path, feature 225's territory) |
| tests | - | the gate's slowest items are pool rolls through a cold roll cache after an engine change | inherent to a change that re-keys the cache; `make quick` is 3,789 tests in ~27 s |

## The third pass: scans that were missed, work done twice, and a lever that bought nothing (feature 281, 2026-09-28)

The GM, after 278: *"each time it seems to be paying out with really big performance gains. So let's do the full thing
again."* The same exercise, with one change to the measuring: every primitive call is traced to the caller that makes it.
All figures are in `specs/281-third-hotspot-pass/measurements.json`; the pool's five rolls went from 32.9 s to 27.6 s
together (1.19x), and the reference hamlet's perf bookend 20.6 s -> 16.5 s. Every pool manifest came out byte-identical.

**Scans the index doctrine missed.** Each was a sibling of code already indexed: the lane clip (`clip_to_clear`) walked
every obstacle edge per 8 ft sample while `clear_runs` beside it asked the fabric index - 535,389 `seg_dist` on Kashikawa
to 11; the notice board walked every way segment per handover sample and every route point per seat; the home-bank join
and the homestead fit walked every brook segment; the caption probe walked every lane segment per seat; the brook toll read
25 mostly empty 20 px cells per ask where a cell a hair wider than the band needs nine. **The shape to look for**: grep a
module for `seg_dist`/`segments_cross` inside `any(`/`min(` generator expressions over a whole registry - that is where the
ones left over from the first two passes were.

**Work done twice.** A fabric-index memo miss rebuilt the ring index of every polygon it filed - 376 distinct polygons
built 5,932 times on Kashikawa - so ring indexes are now shared by CONTENT (the ring's points are the key). The carve asked
each bund vertex once per plot sharing it (four), and walked each shared plot edge once per plot (two). And the windbreak's
gap fill re-offered a gap that seated nothing the same 165 candidate points every round for up to six rounds - though a gap
that seats nothing cannot seat anything later, because every test it faces is static except the spacing test, whose
refusals only grow.

**Measuring where work moves.** A count credited to a primitive's direct caller reads zero once an index moves the call
under a new method - a criterion "passed" on work that merely moved. The harness now counts every call made beneath each
mechanism's entry functions with `sys.monitoring` (the builders included), and records each bucket's TOTAL beside its
named count: a named count that falls while the total does not is a finding, not a pass.

**A lever priced by 278 that bought nothing.** The marsh scatter, thrown and tested as arrays in 278's grass form, cut its
scalar keep-out tests 359x - and its hinterland stage did not get faster (Kuwabata's got slower): on small marshes, building
the shapely shapes of the keep-outs near each mark kind's throws costs what the scalar tests did. It was withdrawn. **Price
a vectorization by the stage's wall time, fastest of three, not by the calls it removes** - the profile favors it, since
profiling inflates Python calls and not C. Its one lasting find was a defect: a pond bank's keep-out thinned to every 16th
point cut the bank's corners, fixed by using the whole ring.

**Two traps worth carrying.** A cache keyed by a list's LENGTH (the precedent `_water_obstacles` uses) served a stale index
when a caller replaced the streams with a different list of the same length - the gate's feature-261 test caught it; the
stream index now holds the objects it was built from and compares them by identity. And a single back-to-back reading is
not a measurement on this host: one base re-run read Kashikawa at 13.2 s against 8.9-9.0 s in every other reading.

**What is left, priced** (profiled seconds over the five maps, `/tmp/m281/after`; profiling inflates Python ~2.4x):

| where | profiled | what it is | the lever, and what it costs |
|---|---|---|---|
| the router (`_route`) | 7.9 s | Dijkstra over lazily judged cells, `_clear_link` per shortcut | a coarser lattice, or A* toward the goal - both change which of two equal paths is drawn |
| field fit and seams | ~9 s | the carve's per-row geometry and shapely buffers/unions in `close_seams` | the rows as array operations; fewer carves by a closer first guess - both change the field |
| the page writer | ~4 s | regex parsing of the element text (`merge_primitives`, `drop_offmap`) | emit the page's elements from the records instead of re-parsing the svg - a rewrite of the page path |
| `edge_dist` over whole rings | ~1.5 s | `_crosses_fabric`, `ways/geom.py`'s service trims, the comb's `_dry` | the fourth batch of the missed-scan shape: a `RingIndex` per ring; exact, about 0.6 s real |
| the brook toll | 590,253 lookups on Kashikawa | 9 cells per ask, most empty | a bitmap of cells near the band - exact, small |
| the finish | ~1.5 s | the blade buckets' flush | out of this pass's scope (feature 223's) |

## The fourth pass: the exact levers kept, the moving ones measured faster and withdrawn on the rules (feature 284, 2026-09-28)

The GM, on 281's priced residue: *"look at what is slow and then be willing to let things of that nature change if those
changes would allow it to be significantly faster."* The pool's five rolls went from 35.15 s on main (as merged, with feature
269) to 26.72 s back to back (1.32x), and every pool map came out main's map but for one bamboo thicket on two maps (the 16 ft seat lattice). All figures are in
`specs/284-fourth-hotspot-pass/measurements.json` and its research record.

**What paid, all exact:** the threshing yards' mats in arrays (feature 282 had made the homesteads stage 3.7-5.1 times slower;
the same mats), the page reading the blade slots' structures instead of re-parsing their strings, the notice board sampling
its verge band before the rest (the roadside rule throws the rest away whenever the band holds a seat), the bamboo walked
outward from its target, the whole-ring `edge_dist` scans asked through indexes, one link index per route, the brook toll's
near-cell set (and one exact lever withdrawn for costing more than it saved: a crown grid per grove clump, whose few crowns are
cheaper to walk than to file) - and a stranding re-roll resuming from a copy of the first roll taken before the seats, the stages before
them being the same on every attempt (a re-roll 1.1-1.7 s faster; the resume went with the re-roll in feature 287, below).

**The moving levers, and how to judge one.** A* in the router and the field's size search without its blind probe each move
maps, and the moved maps re-roll more often. Judged by the pool and cohort seeds 1-24 rolled whole against the run-to-run
spread measured IN THE SAME RUN (the shipping engine rolled twice, interleaved by map with the lever's pass;
`specs/284-fourth-hotspot-pass/combined/`), they were 4.8% faster together against a 0.6% spread - and the gate then failed
on five rules over the moved POOL maps (a bund stepped twice, woodland parcels in a ruled row, a copse off its house's bank,
brook legs on a screen axis, a seat off the wind), with the pool itself no faster. The field search's lever was
withdrawn on the rules; A*, measured again alone once that was out, was not faster than the run-to-run spread, and went too. **Three lessons:** run the
gate on the moved pool before calling a moving lever kept - a cohort comparison measures reach and time, not the pool's
seed tests; never judge one lever with another in that has since changed (each was first withdrawn on a run under the other);
and a lever's own stage can halve while the rolls get slower. The coarser router lattice, the carve's rows in arrays and the
board's 24 px lattice lost on those terms too (they strand, run slower, or break the entrance rule).

**A defect the moved maps found.** The junction pass deleted a connector the web could not join as debris, and the reach
check then read the network that was left and passed: cohort seed 15 shipped with no way off the map. The connector is now
never dropped there. A check that reads "whatever is left" passes when the thing it should have failed on is deleted first.

**What is left** (profiled on Sawada and Kashikawa after the pass; research R7): no lever of the allowed kind remains that
makes any of these significantly faster.

| where | cost | why nothing was taken |
|---|---|---|
| the seam closing (`close_seams`) | ~2.5 profiled s on Sawada | ~800 shapely welds of ~1.2 ms each, already ranked in one array call and read from a shared tree; no scan left, and the shapes are the rule |
| the first-roll strandings (CLOSED by feature 287: no roll re-rolls - see its section below) | 2 of 29 rolls pay a re-roll (the resume cuts it to the stages from the seats on) | a seat-time reach test was tried three times before and failed - reachability depends on fabric that does not exist when seats are chosen |
| the commons, the blade flush, the grove fill | 0.2-0.6 s each | sums of indexed lookups; each an index already |
| `seg_dist` over ~25 callers | 312,391 calls on Sawada, none above 0.09 s | an index per caller buys under a tenth of a second each |

## Guarantees instead of re-rolls and finished-map tests (feature 287, 2026-09-29)

Feature 284's two moving levers broke five finished-map rules on the pool, and the GM asked for every such rule to be
*"guaranteed by the placement algorithm rather than just happening to work on particular seeds"*. What that did to the
cost of a roll and of a gate (the full record: `specs/287-placer-guarantees/research.md` R5-R10):

- **A map is built once.** `generate` used to re-roll a map that stranded a farmhouse, with that ground forbidden, up to
  four times, and keep the least bad. Before the feature 8 of the 53 maps of the pool and cohort 1-48 re-rolled (11 extra
  builds; observed 2026-09-29, method: `specs/287-placer-guarantees/p0/harness.py`, research R5). The seating now reserves
  a corridor from every door to the exit strip against the fabric still to be laid (M3), the web's last pass
  (`ways/settle.py`) draws the corridor for any house its lanes do not reach, and the loop, its snapshot-and-resume and
  its choice between attempts are deleted. The acceptance sweep counts one build per roll (research R9). Eighteen
  earlier seat-time reach tests failed because they ran before the neighbors' fabric existed; a RESERVATION against
  that fabric is what made the seat-time answer possible.
- **The web settles itself, and says how hard it worked.** `settle_the_web` repairs only by cutting ordinary lanes or
  drawing reserved corridors, so it terminates; the pool's manifests record 2-3 rounds and 3-15 lanes changed
  (`meta.web_settle`; observed 2026-09-29, method: the five committed manifests at bf705bee3). Its wall-clock seconds
  are kept OUT of the manifest, which otherwise rewrote every pool map on each regeneration with nothing moved.
- **One registry of what stands, indexed once.** Every footprint is recorded through one grid index (120 px cells,
  `overlap/registry.py`), filed once as recorded and asked per candidate (constitution X clause 15); the overlap matrix
  that one test used to read after the fact is now asked by every placer before it places.
- **What the gate stopped paying.** 84 test functions retired with their rules guaranteed by placer unit tests: 228.6 s
  of test time per full gate, 216.45 s of it ONE unit test - a board under one wide canopy, where the strict siter proved
  every shaded seat by a full least-cost search before the terminal. Rebuilt as a timing probe that scene took 305.5 s
  before and 4.6 s after the siting was indexed and ordered open seats first, the same seat (observed 2026-09-29,
  method: a direct call in the clone and in a detached worktree, research R8). The finished-map tests themselves cost
  10.4 s together: **a finished-map test's cost is the roll it reads, and that roll is shared**, so retiring one frees
  little unless it was the only reader of its map.
- **What the guarantees cost a roll, and the part of it that was work done twice** (the feature's last perf pass,
  2026-09-30). The guarantees made the reference bookend about a third slower than main; profiled per stage, most of the
  rise was the shapes of this file, in the code the feature added. The same route asked again on each of the straggler
  pass's four passes (seed 47: 144 routes, 47 distinct - `ways/serve.py` remembers them, and each candidate's clear runs,
  for the pass); the coarse-grain top-up's 558 reserve plots each walking every ditch segment (`WetLines`) and every
  paddy ring re-boxed and re-built per plot (`BoxedRings`); the ways' ground test asked of 1,317 corridor lines of which
  it refused one, before the fixtures and beds that refuse most of them (`access.lawful_leg`, asked last); the copse's
  brook barriers walked per clump (`BankNear`, 381,637 crossing tests); the same 683-ring union of the worked ground
  taken three times in one seating, once per view of the manifest (`memo_ground`, now kept per manifest). Every lever
  prunes or remembers; the old test decides (`tests/settlement/test_exact_pieces_287.py`), and the pool and cohort 1-20
  came out byte-identical. The bookend went from 35.0 / 34.6 s to 29.3 / 29.0 s, against main's 25.9 / 25.5 (observed
  2026-09-30, method: `make perf LABEL=adhoc` alternated over detached worktrees of the feature's head and of main, load
  4.6-6.4). **What is left is the guarantees' own work**: the exhaustive seat pass offers hundreds of seats
  for the last few households (seed 4: 523 offered, 9 taken) and each pays four bundle layouts and a corridor search;
  the one exact refusal found ahead of the layouts is the house's own box on the grounds that only grow with a box
  (`_house_box_refused`: the canvas margin, a reserved corridor, two placed homesteads - about a third of the offers,
  0.1 s a seed; only `seat_search`'s counts moved). Offering the full-pitch lattice first would cut the pass's offers
  from 523 / 282 / 378 to 71 / 66 / 87 on seeds 4 / 25 / 47, but the clusters it seats spread 12-27% further from their
  seat and up to 28% taller - a change of form, not of speed, and not taken (observed 2026-09-30, method: the reference
  spec's seating in the clone, the grid reordered, against the unmodified engine).
- **The bookends**: `287-start` total 20.9 s, median 5.2 s, worst 5.8 s (observed 2026-09-29, method: `make perf
  LABEL=287-start` before any engine change, load 1.3); `287-end` 25.7 s against origin/main's 24.0 s on the same host
  (observed 2026-09-30, method: `make perf LABEL=287-end` at load 3.5 and two runs alternated with a worktree at
  80af74aef - `reference-snapshot-main` in the spec's measurements.json). Against main the guarantees cost about +9.4 s
  gross over the four seeds (homesteads, web, hinterland, field) and 287's exact speedups give back about 8.2 s (the
  straggler route memo, seed 39's web -4.4 s; the board siting, notice -0.5 to -0.95 s on three seeds; the windbreak,
  -1.1 s in all), a net +1.7 s (+7%). perf-audit: band 1 consistent, band 2 justified (2026-09-30); band 3 owes the GM.
- **The seat pass's cheaper refusals first**: the wood check and the three sun rules are asked before the corridor search
  in `_parts_fit` - they refuse 510 / 177 / 230 of the offers on seeds 4 / 25 / 47 for about 0.05 s, only refuse, and read
  nothing the search writes, so every manifest stays byte-identical; the corridor searches on seed 4 fell 1,122 -> 612
  and homesteads 6.03 -> 5.11 s over the four seeds (`refusals-before-corridor` in the spec's measurements.json).
- **Measured and declined - the straggler footpaths dropped**: -3.0 s (-11.2%, all in the web), but every map's lanes
  move (380 -> 347 lanes, -4.9% length) and it exposed a settle gap (cohort 14's doubled tail on the connector), now
  closed by the settle's exit check; reverted as the GM's call (`straggler-footpaths-off`).
- **The straggler footpaths dropped, on the GM's call** (2026-09-30: *"Yes, go ahead and drop the straggler footpath
  logic."*): the pass is deleted, not disabled - `_serve_stragglers` with its route memo and its four passes, the
  home-bank re-serve (`_link_home_bank`, `excursion_lanes`, the brook-crossing index it alone read) and the helpers only
  they used - because the access tree now guarantees reach by construction (the corridor reserved at seating, drawn by
  the settle for any house left unreached, refused by `last_resort` otherwise). The reference snapshot went from 28.27 s
  to 24.30 s, -14.0%, all in the web (observed 2026-09-30, method: `make perf LABEL=adhoc` alternated with a detached
  worktree at 7174f9d54, three valid rounds at load 7-15 after a cold first round; the host was never under 4). Lanes
  over the pool and cohort 1-20 fell 380 -> 347 and 4.9% shorter, 22 of 25 maps moving, the same figures the
  scratch-off measured; the acceptance sweep held R13's bar and better (plain 53/53 clean, the cohort-34 belt reading
  gone; probes 52/52 produced maps clean plus plan D2's cohort-18 refusal), and `make cohort N=60` passed 60/60
  (`straggler-footpaths-dropped`).

## Memory: the spike is C buffers, not Python objects, and it lands where nothing reads it (feature 208, 2026-09-07)

The GM asked why a full gate costs 6.8 GiB and whether each of the eight workers really needs most of a
gigabyte. Measured with a per-test RSS sampler (a thread at 20 ms), a cgroup sampler, tracemalloc on one
file and a per-stage wrapper (`specs/208-the-raster-is-a-render/research.md` R1):

- A worker is 111 MB after import, and a whole hamlet roll - all 18 placement stages - takes it only to
  121. The engine's own geometry is cheap.
- The spike was the PAGE's raster picture: PIL decoding resvg's 18.6-megapixel PNG (70 MB of RGBA) and
  libwebp encoding it lossless (a further 240 MB of working memory) - 146 -> 598 -> 173 MB in 7.3 s, on
  EVERY roll, including the scratch page the roll driver writes into a temp directory and deletes. About
  thirty times a gate, for pages nothing reads. Tracemalloc saw 93 MB of Python objects at an 870 MB peak:
  the rest was C memory the interpreter's allocator never returns, which is also why a worker then RESTED
  at 250 MB.
- Two gates at once reached the container's 8 GiB cap (3,455 reclaim events).

Two rules came out of it. **A render is made on the render condition, never on the roll** - the page's
raster now shares the PNG's `render and not DIAGRAM_SKIP_RENDER`, so a test roll writes the vector-only
page: 9.2 s and 598 MB became 1.6 s and 153 MB. **Large C buffers are made in a child process** - the
picture's decode and encode run in a PIL-only child (`raster.webp_lossless`), so the worker never holds
them and there is nothing for the allocator to keep: the parent rests at 125 MB after a rendered page,
and `malloc_trim` (which the GM had authorized if the child alone did not do it) was not needed. The
instruments live in the session scratchpad and are cheap to rebuild: sample `/proc/self/statm` from a
thread inside a pytest plugin loaded through `PYTEST_ADDOPTS`, and read the peak per test - `ru_maxrss`
sees the peak but cannot say which test, and before/after readings cannot see inside one.

**The second look (feature 210, the same day).** With the raster gone the GM asked what a worker's
resting 200-250 MB was made of, and whether the "rolled manifests it holds" could be loaded and purged.
A heap census (RSS split from `/proc/self/status`, glibc `mallinfo2` through ctypes, a `gc` type
histogram, every module-level container in the engine with `__slots__` descended, the objects reachable
from each) found no manifest held at all - the fixtures release their rolls and the FULL run's shared
pickles were 0.7 MB - but `hamletgen/clearance.py`'s `_MEMO` holding 46 MB of a finished roll's geometry
(keyed by object identity, so it could never serve a later roll, yet kept for the process's life), glibc
keeping 14-68 MB freed, and the rest pymalloc arenas left fragmented by rolls. Three rules from it:
**a per-roll memo is cleared when the roll ends** (`driver.roll_scope()`, which every stage-running
loop enters - a static test walks the engine's AST for loops whose body calls a stage, because the
feature's spec review found one such loop outside the scope four rounds running); **`malloc_trim(0)`
when a roll ends** (`_memory.trim_heap`); and **the roll itself runs in a child** where it can -
`rollcache.hamlet()` first, the gate fixtures' rolls, a subprocess in `gate_obtain`'s shape so its
coverage still lands. Measured on one roll-heavy file: the worker rested at 90 MB instead of 242, with
3 MB retained instead of 41 and no memo at all. And the GM's file-cache question: the 2-3 GiB `file` in
`memory.stat` is the kernel's page cache (git packs, pool renders and pages, `.pyc`, coverage data), clean
and reclaimable, not tmpfs - nothing here is in RAM by mistake, and a kill is decided by `anon`.

**The third pass (feature 213, the same week): the rolls themselves were the count, not the size.** A
census of one gate found 37 real rolls of 14 distinct specs - the same spec rolled by four workers at once,
the cohort seeds rolled under two cache subjects, Inashiro rolled seven times by four mechanisms - against a
packing record that had measured 11 a week earlier. The memory work of 208 and 210 had made each roll cheap
to the worker; 213 made the gate roll each hamlet ONCE (one subject per spec, a lock so the first wave waits,
every roll in a child) and put a census gate on it so the number cannot drift back unnoticed. The six
levers from the 5.5 GiB breakdown are its FRs: no test renders (a suite-wide default, a `renders` marker for
the tests of rendering), the child roll-out finished, the pool sweep's child profiled, the worker count
measured, the rolling tests collected first and their concurrency capped. Numbers: `specs/213` research R4.

## Where a pool hamlet's time goes, end to end (audit, session `diagram-performance`, 2026-09-10)

The GM asked, after features 218-221, whether more low-hanging fruit remained. The stage profile
answers only for the stage loop, so each pool gen was timed end to end (`make map GEN="--no-cache ..."`,
one at a time, load average 0.5 on 22 cores) with phase marks around everything outside the stages, in a
detached scratch worktree. **The stage loop is under half of a regen.** Seconds, one run each:

| phase | inashiro | kashikawa | kuwabata | mizuguchi | sawada | mean |
|---|---|---|---|---|---|---|
| engine stages (`build`) | 6.9 | 10.4 | 16.6 | 6.3 | 14.4 | 10.9 |
| page picture: resvg `--zoom 3` + lossless WebP | 7.8 | 7.1 | 6.5 | 6.9 | 6.4 | 6.9 |
| PNG render: resvg 2600 px | 2.1 | 3.0 | 2.7 | 2.0 | 2.4 | 2.5 |
| page text: `drop_offmap` | 0.7 | 1.0 | 0.8 | 0.6 | 1.1 | 0.8 |
| page text: `wrap` (merge + hit copies) | 0.5 | 0.3 | 0.3 | 0.4 | 0.3 | 0.3 |
| page: explanations + json blob | 0.3 | 0.3 | 0.4 | 0.3 | 0.3 | 0.3 |
| page: id map (resvg zoom 1) | 0.3 | 0.2 | 0.3 | 0.3 | 0.2 | 0.3 |
| page: hit regions | 0.1 | 0.1 | 0.0 | 0.1 | 0.1 | 0.1 |
| svg/json write + ink census | 0.1 | 0.2 | 0.1 | 0.1 | 0.2 | 0.1 |
| child interpreter + engine imports | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 |
| `gencache.store` | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |
| **regen total (child)** | **19.3** | **23.0** | **27.9** | **17.3** | **25.6** | **22.6** |

`make map` adds ~0.6 s (the reference HIT check, the pool index) and 9 s more when the reference must
first roll on a MISS. Stages, the same runs:

| stage | inashiro | kashikawa | kuwabata | mizuguchi | sawada | mean |
|---|---|---|---|---|---|---|
| hinterland | 1.3 | 2.4 | **10.0** | 1.7 | 3.7 | 3.8 |
| field | 1.8 | 2.4 | 0.7 | 1.1 | 3.7 | 2.0 |
| homesteads | 1.0 | 1.3 | 2.6 | 0.8 | 1.0 | 1.3 |
| track | 0.8 | 0.9 | 1.1 | 1.0 | 0.9 | 0.9 |
| appurtenances | 0.2 | 1.3 | 1.1 | 0.2 | 1.2 | 0.8 |
| web | 0.2 | 0.7 | 0.4 | 0.4 | 2.1 | 0.8 |
| notice | 0.3 | 0.6 | 0.5 | 0.3 | 1.0 | 0.5 |
| windbreak | 0.7 | 0.2 | 0.2 | 0.5 | 0.4 | 0.4 |
| crossings | 0.3 | 0.4 | 0.0 | 0.3 | 0.4 | 0.3 |

**The picture, split.** `raster.picture` is resvg rendering the page's SVG at 3 px per map px (Inashiro
5103 x 5136 = 26 Mpx, 2.1-3.6 s) and then a child decoding the PNG and encoding it as LOSSLESS WebP
(2.9-5.2 s). Measured on Inashiro's picture alone: PIL decode 0.41 s; lossless WebP `method=0` 4.12 s for
3.87 MB; lossy WebP q90 0.93 s for 2.32 MB; PNG level 1 1.15 s for 8.3 MB; JPEG q90 0.20 s. The lossless
encode is the single most expensive step of the whole generation, on every map, and it is a rendering
decision (feature 200) - lossy at q90+ is a question for the GM, not a substitution.

**The SVG is 13-16 MB and 89% of it is one glyph.** Inashiro's file holds 268,156 `<line>` elements
(14.6 MB of 16.4) - the bucketed grass blades of the commons scrub (`land/cover.py`, `#A7A860`) and the
marsh reeds (`land/wet.py`, `#6E9377`) - beside 18k circles, 2k polygons and 235 paths. Every consumer
pays for them: resvg parses them three times per gen (the PNG, the picture, the id map), and
`drop_offmap` walks them all to discard the ~90% that lie outside the viewBox (specs/200 R2). Measured
with resvg on Inashiro's SVG: 2600 px render 2.13 s as shipped, 1.17 s with each blade group merged into
ONE `<path d="M..L..M..L..">` (9.4 MB), 0.89 s with the blades removed; the zoom-3 render 3.81 / 2.86 /
2.43 s. So merging the blade lines into one path per group saves ~1 s per resvg pass with no change to
the ink (the page's `merge_primitives` already does this merge for the browser - it would move upstream
into the writer), and NOT EMITTING the off-map blades at all - the writer knows the viewBox only at crop
time, but the scrub could be clipped to the frame's content box plus a margin when it is scattered, or
culled in `finish` before the SVG is written - would take the file to ~3 MB and every downstream pass
with it.

**Inside the stages (cProfile of the gen child, +100-170%; relative shares only).** Both maps' hot
spots are constitution X clause 15's shape again - a candidate tested against every edge of everything:

- **Kuwabata's hinterland, 87% of the stage**: `title_pocket` -> `Settlement._blank_label_spot` ->
  `_box_clear`, 4,027 candidate boxes each tested against every edge of every obstacle polygon and line
  by `segments_cross` - 16.4 million segment pairs, 34 million `ccw`. A dike-pond hamlet's obstacle
  list is every pond and every ditch. `_rect_hits` two files away already bbox-prefilters each polygon and
  each edge; `_box_clear` has no prefilter at all, and the scan tries every 24 px box top-to-bottom until
  one clears. A per-polygon bbox reject plus a coarse occupancy grid of the obstacles, built once per
  `_title_obstacles` call, would take the ~8.7 real seconds to well under one. The same scan runs again in
  `title()` at the label phase.
- **Sawada's hinterland, 52% of the stage**: `bamboo_seats` -> `_fits` (15 samples per candidate) ->
  `bamboo_blocked`, which tests each sample against every segment of every lane and every polygon by
  `seg_dist` - 2.2 million distances for 9,796 samples. A `KeepoutGrid` of the rects, lanes, polys and
  pond (the windbreak's shape from feature 218) asked once per sample is the fix.
- **`place_wells` (appurtenances, 1.1-1.3 s on three maps)**: the minimax sort key calls `_worst_after`
  70k times - `pool.sort(key=...)` evaluates the tuple's `_worst_after(c)` TWICE per candidate and the
  inner `min` over `placed` for every needy house each time; a precomputed nearest-standing-well distance
  per house and one `_worst_after` per candidate is the same answer at a fraction of the calls.
- **`stage_web` on Sawada (2.1 s)**: `_serve_stragglers` -> `_route` x135 -> `clearance.fouled` 647k
  queries. The router's lattice is 10 ft cells over a box padded to 0.75 x span; most of its cost is
  marking cells that the string-pulled path never visits. A lazy (on-demand) `fouled` per popped cell
  rather than a whole-lattice pre-mark, or a coarser first pass, is the lever; measure before choosing.
- **`stage_notice` on Sawada (1.0 s)**: `place_kosatsuba` probes every verge spot along every lane with
  `edge_within` (640k calls) - the same shape, a `RingIndex` per lane bed built once.
- **`commons` scatter (`land/cover.py`, 3-3.5 s profiled, ~1 s real per map)**: 1-1.3 million
  `random.uniform` draws, most refused by `_sparse`. It is already indexed (feature 218); what is left is
  the draw count itself, and the off-map share of it (see the SVG note above) - a scatter clipped to the
  content box draws fewer points AND writes fewer lines.
- **`stage_field` (1-3.7 s)**: `carve_comb` / `close_seams` / `banks.clearance`, as profiled in feature
  220; nothing new found here.

**The page's text passes run on every TEST roll too.** A gate roll (render=False) still pays
`drop_offmap` + `wrap` + explanations, ~1.6 s per roll, for a page no test opens (feature 208 took the
raster out of test rolls; the vector page stayed). Small now that the gate rolls only the shipped
five on a cold cache, but it is a cost without a reader.

**Levers, ranked by seconds per regen for the effort** (each is a rendering or engine change and owes its
own feature; a knob or a visual change is the GM's call):

1. Lossless -> lossy WebP for the page picture, or `RASTER_R` 3 -> 2 (2.25x fewer pixels): -3 to -4 s
   per map (GM decision: it is what the reader sees below the switch scale).
2. Run the three renders concurrently - the PNG (resvg 2600), the picture (resvg zoom 3 + WebP) and the
   id map are independent subprocesses today run in sequence: -2 to -3 s of wall per map at zero
   change to any output.
3. Bucketed blades as ONE path per group in the writer, and the off-map scatter never emitted: -1 s per
   resvg pass (three passes), -0.5 s of `drop_offmap`, and a 13-16 MB SVG becomes ~3 MB.
4. `_box_clear` with a bbox prefilter and an occupancy grid: -8 s on Kuwabata, -0.5 to -2 s elsewhere,
   and the `title()` rescan with it.
5. `bamboo_blocked` on a `KeepoutGrid`: -3 s on Sawada, -1 s typical.
6. `place_wells` minimax key computed once per candidate: -0.5 to -1 s on three maps.
7. `place_kosatsuba` and `_route` indexed: -0.5 to -1.5 s where they bite.

**Two defects met on the way (no engine change made in this audit; both owe a feature).** `make map
... PROFILE=1` prints NOTHING since feature 213 moved the roll into a child: the stage profile goes to the
child's stderr, which `rollcache._in_child` captures and discards on success - so the GM's own instrument
for "where the roll spent its time" (feature 151) has been silent for two days. Forward the child's
stderr, or carry the timings in the pickled payload. And cProfile cannot run inside a gen child: the
dependency recorder holds `sys.monitoring.PROFILER_ID`, so `cProfile.Profile().enable()` raises "Another
profiling tool is already active" - `make perf-profile` avoids it only because it profiles a stage in
the driver's own process. py-spy 0.4.2 does not recognize Python 3.14 either, so a sampling profile is not
available on this host today. The scratch method that worked: a detached worktree, a `_phase.mark()`
helper printing deltas to stderr at each boundary, the child's stderr forwarded, and the recorder moved to
tool id 3 while cProfile is on.

**What feature 222 took off it (2026-09-11, the GM's four picks from the ranked list - specs/222):** regen per
pool hamlet 17-28 s -> 11-19 s. The title-pocket scan on a `BoxObstacles` index (Kuwabata's hinterland 10.0 ->
1.6 s, verdicts identical); the blade buckets written as the page's tiled paths straight from their coordinates
(`merge_lines` - calling `merge_primitives` on the written lines first cost 1.9 s of the stage, the parse-back
trap; SVG 16.4 -> 9.4 MB, each resvg pass ~1 s faster); the page picture a JPEG (the encode child 2.9-5.2 s ->
0.5-0.8; reversible in three lines in `raster.py`); the PNG render threaded under the page's own work, its join
0.00 s. Found on the way and fixed: `_title_obstacles` carried a duplicate block since feature 137 that made the
cover fallback dead, and `make map PROFILE=1` had printed nothing since 213. What is left is the list above
minus those four: the bamboo seat scan, the wells key, the router, `drop_offmap` (or not emitting the off-map
scatter), and `RASTER_R`.

## The homesteads stage, counted (2026-09-12, session `diagram-performance`, at the GM's request)

The GM, looking at the placement-stages page: *"at the point where we lay out the homesteads, the map is mostly
empty ... We should be able to draw a series of line segments separating the farm field from the place where we
are laying out our homesteads. And then the only thing that we need to do is make sure that the homesteads are on
the correct side of the line and that they do not overlap with each other."* The stage costs 1.0 / 2.3 / 2.3 s
real on Inashiro / Kuwabata / Sawada (15 / 16 / 19 houses). cProfile of the gen child, counts PER HOUSE:

| per house | inashiro | kuwabata | sawada |
|---|---|---|---|
| candidate seats proposed (`try_place`) | 3 | 10 | 2 |
| positions tested (`_fits_any_side`) | 419 | 1,686 | 363 |
| rectangles tested (`_rect_blocked`) | 1,090 | 2,755 | 848 |
| chord side tests (`chain_violated`) | 7,778 | 13,075 | 6,424 |
| hard-ground scans (`_hard_clear`, bbox over every hard polygon) | 1,234 | 2,090 | 1,006 |
| rotated-corner gap tests against standing houses (`poly_gap`) | 396 | 802 | 283 |
| segment distances (`seg_dist`, whole gen) | 73,000 | 66,000 | 99,000 |
| point-in-polygon (whole gen) | 29,000 | 23,000 | 25,000 |

What a rectangle is tested against: `block_polys` (EVERY dry hem plot, appended by `comb.py`, plus the pond's
box, plus Kuwabata's dike-pond mosaic), the field's chords (feature 140 - five points per rect, so the chords are
already what the GM describes, but built from the PADDY outline only), the water courses (2-3, bbox-pruned), and
the hard ground (`_hard_clear`: every dry plot AGAIN, every marsh, and every field-ditch segment as its own quad -
29 + 114 + 2 polygons on Inashiro, by bbox per rect). Then the standing houses by rotated-corner gap, the sun
corridors, the treads, and `_wall_on_the_bund` (the chords again, per corner). So the hem is compared against
twice per rectangle and the ditches inside the paddy once, for a rectangle that the chords already keep off the
paddy.

Why so many positions: `_place_bundle_nucleated` spirals through up to 181 offsets (15 rings x 12) from each
proposed seat, running the FULL battery at every offset, and 24 of Inashiro's 39 proposed seats fail every
offset - 181 full tests each for nothing. Kuwabata proposes 157 seats for 16 houses.

What the stage actually has to establish: the house side of the cultivated ground (chords from the paddy AND
the hem, which would retire the plot-by-plot and ditch-by-ditch scans), clear of the few things outside it (the
marsh, the pond, the stream and the feeder), clear of the bundles already standing (their boxes, and the eave
gap only for the nearest), and the yards' and gardens' sun. Cheapest test first - the house center against the
chords and the placed boxes - would also dispose of most of the spiral's offsets in microseconds.

## The site boundary: the ground asked once, the guesses counted (feature 226, 2026-09-12)

The answer to the section above. `hamletgen/homesteads/boundary.py` computes the ground a homestead may stand on
ONCE per roll: the paddy's facing chains (feature 140's, asked by side), one `unary_union` outline with holes of
everything else - the hem plots, the hard ground grown by `_hard_clear`'s 2 px tilt allowance, the marshes, the dry
plots, the keep-out ellipses as 24-gons, and the reed-marsh toe asked of `toe_band()` before it is drawn (registered
as hard ground, so the byres, sheds and wells refuse it too) - asked by containment, and the water courses and
registered corridors as segments at the clearance their old tests applied (a segment the cultivated ground covers is
dropped: 86-119 -> 0-7 per map). `_site_blocks_rect` asks nine points per rectangle. Seats are proposed FROM it: the
front row walks the chains at the bundle pitch; the cloud keeps its draw but dedupes to a 0.8-pitch lattice; every
seat is pre-tested (the smallest house's box against the boundary and the placed boxes) before the placer is asked;
the spiral is six rings, with three fifteen-ring rescue rounds only while the quota is short. `meta.seat_search`
counts every guess. The pads and point sets of every retired test are kept (spec 226 D2).

| per house (pool, first roll) | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| candidate seats (pre-tested) | 4.3 | 4.8 | 7.0 | 2.5 | 1.6 |
| placer calls | 1.5 | 1.4 | 1.8 | 1.1 | 1.3 |
| positions the fit test saw | 55 | 62 | 105 | 28 | 46 |
| rectangles judged | 194 | 220 | 387 | 113 | 163 |
| boundary: chords / rings (vertices) / water + corridor segments | 7 / 3 (667) / 5 + 3 | 10 / 3 (654) / 5 + 3 | 7 / 1 + 1 hole (230) / 0 | 8 / 3 (627) / 5 + 3 | 7 / 3 (657) / 5 + 3 |

Against the table above: 419 / 1,686 positions per house on Inashiro / Kuwabata, and 157 proposals for Kuwabata's
16 houses, are 55 / 105 positions and 112 pre-tested candidates (28 placer calls). The rings are OUTLINES of a few
hundred vertices, not "a few segments" - the chords, water and corridors are 13-22 per map; the review of the
feature asked that the record say so. The stage: 1.0 / 1.3 / 2.3 / 0.8 / 1.0 s after feature 225 -> see specs/226
research R2 for the after (0.2-0.6 s on the first measurement).

Three things the cohort taught, each a shape to remember:

- **A lattice needs a fresh phase per retry.** `generate` re-rolled a stranded map with that ground forbidden (until
  feature 287, which removed the re-roll); the old
  random cloud explored new pockets by itself, the lattice kept the same survivors and re-seated the same pocket. The
  draw is salted by the count of forbidden seats.
- **A new hard member cuts capacity somewhere.** The toe band took cohort seed 25 from 20 households to 14; the
  rescue rounds widen further and drop the lattice dedupe (a rescue spends guesses on purpose).
- **Judge a re-roll on every count it can lose.** The accept rule kept a retry that stranded fewer houses but SEATED
  fewer (14 -> 13); and the cohort audit reported strands but not shortfalls. Both fixed; probe `roll_placed` per
  attempt when a seed looks odd.


## Where a gate's RAM goes (profile, session `diagram-performance`, 2026-09-13, at the GM's request)

The GM asked how much RAM `make done`'s tests use and how it breaks down - our tests, third-party libraries,
the standard library, our engine code being imported. Three instruments, all in the session scratchpad and
cheap to rebuild, and all three see the REAL gate rather than a model of it:

- **a process-tree sampler**: every 0.4 s, `Pss`, `Rss` and `Anonymous` from `smaps_rollup` for every process
  under the `make`, plus the cgroup's `memory.current` and `anon`/`file`. PSS divides shared pages among the
  processes mapping them, so the sum over the tree is an honest total a concurrent gate cannot inflate;
- **an import hook** in a `sitecustomize.py` on `PYTHONPATH` (active only with `MEMPROF_DIR` set), which wraps
  every loader found on `sys.meta_path` so each `exec_module` is bracketed by `statm` and `smaps_rollup`
  readings. A module's cost is EXCLUSIVE - its children's deltas subtracted - and is classed by its file:
  stdlib, site-packages, `l7r/`, `tests/`; a stdlib module also records which class pulled it in;
- **a pytest plugin** (discovered through a `pytest11` entry point in a `dist-info` beside it, so a child
  pytest without the path simply loads nothing - the `-p memprof` form failed the fifteen `tests/tooling`
  tests that spawn a gate of their own) sampling `statm` at 20 ms for a per-test peak, with RSS marks at
  plugin load, session start, collection end and session end.

**The whole gate, full test phase, browser package running (before the fix below).** Peak sum-PSS
**3,210 MiB**, 54 s in, during the test phase; every other phase is small - `pyrefly` 164 MiB, the reference
roll ~120, the hooks-test fan-out ~110 in total, `ruff` 20, and after pytest the coverage combine, the report
and the hamlet floor under 40. The container went from 5.5 GiB to 8.7 of its 10 GiB cap, +2,962 MiB of `anon`,
which is the sum-PSS figure seen from outside. At the peak:

| process class | MiB | share | count |
|---|---|---|---|
| the ten gate workers | 1,268 | 40% | 10, median 124 MiB PSS each; life peaks median 123, max 235 |
| Playwright drivers (node) | 751 | 23% | **8**, ~95 MiB each |
| Chromium | 445 | 14% | 40 processes, five per browser |
| sub-gates spawned by `tests/tooling` | 682 | 21% | 8 controllers + 12 two-worker gates alive at once (30 over the run, ~1.2 s each, ~33 MiB a controller) |
| everything else | 64 | 2% | the real controller, the ci helpers, make |

**The defect: eight browsers for a rule that said one.** The browser package's `xdist_group("chromium")` was a
`pytestmark` in its conftest.py, and pytest reads module marks only from the TEST module - a conftest is on
no test's node chain - so under `loadgroup` the 21 tests spread over 8 workers and each worker's
session-scoped `browser` fixture launched its own driver and Chromium: **1.2 GiB, 37% of the peak**. The
Makefile and the conftest had both stated the one-Chromium rule (GM 2026-09-12) and nothing measured it. A
collection hook in the conftest was tried first and did NOT work under `make page-check`: a conftest named
on the command line is an initial conftest, registered before xdist's `WorkerInteractor`, and pluggy calls
the later registration first, so xdist had already read the marks (measured: 21 of 777 node ids already
carried `@chromium` when the hook ran). The mark lives in each test module's own `pytestmark` now, beside
`renders`, and `tests/test_markers.py` asserts it from the AST - on every module in the package, and that the
conftest carries none. Measured after: ONE driver (141 MiB) and ONE Chromium (139 MiB over five processes);
`make page-check` peaks at **968 MiB against 2,090**; the gate's test phase (`make test-full`, the package
running) at **2,125 MiB against 3,210**. The module-level `playwright.sync_api` import moved into the
fixture at the same time, so the nine workers that never run the group stop paying for it: a worker's
imports fell from 93.1 to 81.7 MiB.

**What one gate worker is made of** (median over the ten, exclusive import cost as RSS; every worker is
its own copy - 25 of its 1,268 MiB were file-backed pages, the rest anonymous heap - so the import column is
paid ten times over):

| | MiB | of imports | what |
|---|---|---|---|
| interpreter at startup | 9.2 | - | |
| third-party | 31.8 | 34% | numpy 7.6, pytest 6.4, playwright 5.3 (+ greenlet 1.6; both gone from nine workers now), PIL 3.0, shapely 2.9, coverage 2.5, pygments 1.1, execnet 0.7 |
| our tests | 26.3 | 28% | `tests/tools` 7.3, `tests/tooling` 6.4, `tests/settlement` 4.2, `tests/hamletgen` 2.4 - 275 modules |
| stdlib | 22.6 | 24% | 18.4 of it pulled in by third-party code, 2.8 by the interpreter and pytest's bootstrap, 0.7 by tests, 0.7 by the engine; hashlib with OpenSSL 4.4, asyncio 1.5, sqlite3 1.0, ssl 0.8, xml 0.7 |
| our engine | 11.2 | 12% | 227 modules: settlement 3.6, interactive 2.0, hamletgen 1.8, ci 1.0, waterfields 0.8, tools 0.8 |
| other | 1.2 | 1% | |
| **imports in all** | **93.1** | | RSS 45 when the plugin loads, 48 at session start |
| collection | +10 | | 3,894 items: RSS 108 at collection end |
| the run itself | +41 | | RSS 149 at session end, median retained growth 45; run peak median 152 |

The run-time growth is mostly coverage's per-context bookkeeping and pytest's own: against an untraced run of
the same tree (`make test-file FILE=tests`, the quick-scope form, 3,055 items), a traced worker is +6 MiB at
collection end and +14 at session end - roughly 150 MiB across ten workers, and the engine's import column is
+1.7 MiB under tracing. The test with the largest spike is the lit-screenshot test: the three `test_page_lit`
browser tests each rise 180-200 MiB over their start in the one worker that runs them (numpy decoding the id
map and PIL the screenshot), which is why that worker peaks at ~300 MiB against ~150 for the others; the
largest outside the browser are the two pinned-knob rolling tests at 65-70 MiB.

**What this says about the three categories the GM named.** Our own code is the SMALL part of a worker: the
engine is 11 MiB and the tests 26, against 55 for third-party code and the stdlib it drags in. Where the gate's
RAM actually goes is in COPIES and PROCESSES - ten workers each importing everything (feature 237's finding,
still true), browsers launched per worker (fixed here), and the tooling tests' real sub-gates (a cost of
testing the gate machinery with the gate machinery, 0.7 GiB at the peak; left as is, stated).
