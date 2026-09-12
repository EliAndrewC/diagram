# Performance: the two shapes this engine keeps growing

**Load this file when:** A gen or a check got slow (or "hangs"), you are about to optimize one, or a GEN_TIME_BUDGETS entry tripped.

Split out of [`../CLAUDE.md`](../CLAUDE.md) so it is not in every diagram session's
context. The text is verbatim; the short always-on version of each rule stays in the index.

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

The rule that matters: **the index prunes, it never decides.** It is always tempting to make a slow
check cheap by making it coarser - testing a bounding polygon instead of the real features, sampling
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
    1  explain      over the line  over the line         `make perf-explain WHY=...` (yours) + `make perf-confirm ... AS=perf-audit` (the subagent's)
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
- **Exactness is cheap to keep and worth keeping.** Every conversion above kept the linear scan's
  own expression as the deciding test - down to the association of a float sum (`w / 2 + (2.0 +
  pad)`, not `(w / 2 + 2.0) + pad`) - and the pool regenerated byte-identical after each, which is
  the strongest verification this engine has. The GM relaxed the requirement mid-feature (*"It is
  absolutely not required that the changes ... result in bite identical output"*); it was kept because
  it was free.
- **What is left is the algorithm, not a scan.** After the conversions the hinterland's 1.27 s is
  the commons scatter's own work per throw - 866k `random.uniform` draws, a million outline tests,
  158k feather distances - in Python. The levers below that change what a map draws and are recorded
  in `specs/218-efficient-overlap-checks/research.md` R2 for the GM's decision, not taken.

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
