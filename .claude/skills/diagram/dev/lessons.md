# Method lessons from the diagram work - things not to repeat

**Load this when a fix is not working and you are about to try another one.** Split out of
`future-work/` on 2026-08-24: that file is a backlog of work TO DO, and these are not tasks. They
are records of attempts that failed, claims that turned out to be wrong, and the shapes those
failures take - which is exactly the material the project's own rules say to keep ("record a fix that
FAILED, at the point of change"; "when stuck, the next step is a MEASUREMENT, not another speculative
edit").

Read the whole file once. It is short, and the value is in recognizing the SHAPE of a failure you are
currently inside, which an index cannot give you.

---

## 3. Author-loop pace: log of what ran long (keep appending)
- 021 resize re-lay (2026-08-10): ~4h of migrate-grind. Root cause: literalness (see #1),
  plus one avoidable class - bulk text-shifters that touched non-coordinate numbers. Any
  future bulk transform must be coordinate-aware (pairs/boxes only) and verified by
  `grep -E '\* -|court_every=[0-9]{3}'` before regen.
- Regen+gate cycle is ~10s for the whole capital; the cost is the NUMBER of author cycles,
  never the generator. Batch many fixes per cycle; measure with the check's own data
  (locators, tools/why_placed.py) instead of guessing coordinates - every hand-guessed seat this
  feature landed on something.

### Two dead ends, both implemented, measured and reverted

Neither is a reason not to try again - both got most of the way - but each broke something specific.

1. **`_share` - partition a scrap among the basins along it by NEAREST BASIN.** Took Inashiro 23 -> 7
   and visibly removed the staircase, and it is the right idea in the abstract: each basin takes the
   ground in front of its own bund, so its wall moves outward across its whole frontage. Measured
   failure: `_absorb` refuses 960 of 2,685 welds against 5 of 370 without it, leaving 16,767 px2 of
   bare ground inside the command area against 1,760, and **492 of those refusals had NO ADJACENT
   BASIN AT ALL** - `_absorb` ranks the basins whose bund forms part of a scrap, so a piece touching
   only its siblings has nothing to rank. Guarding the stranding (abandon the partition when a piece
   reaches no basin; fold recovery ground into the neighbouring piece) took bare ground to ~4,900 px2
   and refusals to 281, but then the partition switches itself off exactly where the ground is
   awkward, which is exactly where the staircase is. It is also fragile against GEOS: three separate
   `TopologyException` sites in one afternoon, including inside `_absorb`'s ranking loop.
   **`_seam_cuts` is the same insight applied one stage earlier, at a tenth of the machinery** - the
   pitch, not the partition - which is why it worked.
2. **Dropping a step's vertices from every ring that carries them.** Looks partition-preserving and
   is not: the two rings either side of a wall have DIFFERENT neighbouring vertices, so the chords
   they close over differ, and Inashiro rings 460 and 592 lost 400 px2 and gained 259 - the
   difference being bare floor. `_unjog` trades the corner as a POLYGON instead, which conserves
   ground by construction whatever the two rings look like.

Two smaller levers were measured as dead and are recorded at the point of change in `seams.py`:
letting the basin on the OTHER side of a wall attempt the repair (one step in four maps, 70% of the
regeneration), and re-offering a partition piece no basin would take.

## OBSERVATION 2026-08-19: two DIFFERENT failure shapes, and conflating them costs the second lesson

Across two sessions this day produced five retractions and roughly a dozen engine defects. It is tempting
to write them up as one pattern. They are TWO, and the waterfields session corrected me when I collapsed
them - the correction is the useful part, so it is recorded rather than smoothed away.

**SHAPE 1 - the instrument cannot discriminate.** A measurement whose INPUT cannot contain the failure it
names. `cluster_shape` fed a pass that never ran (honored on 1 of 48 seeds). The honesty guard compared a
drawn aspect against a mechanism parameter, then compared it on the PAGE's axes so a diagonal band read as
1.22 instead of 3.83. The woodland scan vetted a square while the gate measured a rotated bbox. The
way-vs-water tests never received `M["streams"]`. `dry_plot_furrows_vary` compared zero pairs. The paddy
floor gates AREA while the defect is WIDTH. The gen-time budgets described solo CPU while measuring
parallel-run CPU. Four branches were "covered" only by a warm gen cache. And my own count of 1,329 tint
candidates was seven call sites of a shared predicate.
**Remedy: a second measurement that has to disagree** - a detached-worktree baseline, a control assertion
that the setup produces the thing being tested, an independent reviewer looking at the drawing.

**SHAPE 2 - the instrument is fine and the ATTRIBUTION is wrong.** The waterfields session measured a real
ripple correctly and assigned it to the wrong cause, because the baseline was an older HEAD and a peer's
lane-web feature had landed inside the window. The number was right; the story about what produced it was
not.
**Remedy is different and does not follow from the first: NAME THE COMMIT a measurement is taken against.**
No amount of instrument-sharpening prevents this one - a session doing shape-1 discipline perfectly still
gets it wrong this way, which is exactly what happened.

Keep them apart in any future write-up. "Check your instruments" does not cover shape 2, and a session
that has internalised only shape 1 will still misattribute a correct number.

## 2026-08-19: the caption seat search, seven attempts - what worked, and THREE CLAIMS OF MINE THAT WERE WRONG

Gate 0617 caught caption-on-tread notches on cohort seeds 1, 7, 14, 33, 36. **All five are now clear
(38/48 -> 43/48, zero new failures).** Getting there took seven attempts, and the reason it took seven -
two of them measuring code that was never applied - is the useful part. Three claims of mine in this
section were wrong; they are corrected below rather than edited away, in the order I made them.

**WRONG CLAIM 1: "all five failing boards are TILTED".** They are not. `linear_tilt` **CLAMPS** past 45
degrees rather than folding - its own docstring says so at length and warns it must never be confused with
`label_tilt`, which folds. So boards at rot 51.6, 128.9 and -83.3 all return tilt **0.0** and take the
UNTILTED branch. I read `rot`, inferred the branch, and spent two attempts improving a code path those
seeds never execute. **rot is not tilt past the clamp.**

**WRONG CLAIM 2: "the outward walk is a no-op".** It was measured against a tree an auto-sync had reverted
mid-experiment, so the measurement was of the old code. Applied properly to the UNTILTED branch it fixes
three of the five seeds. A measurement taken against an uncommitted edit is worth nothing; commit first,
then measure - which is now how this session does it.

**WHAT ACTUALLY LANDED - and read WRONG CLAIM 3 below before trusting items 3 and 4 of this list.**
They are described here as verified. Two of them were not in the tree when that was written.

1. **The scorer reads the lane's tread EDGE**, which is what gate 0617 reads. It read the CENTERLINE -
   `street_runs` returns polylines with no widths - so it was optimistic by half a lane width (~2.5-3 px)
   and every "best" seat was best by a measure the rule does not use. The placer-and-check-read-one-source
   rule, broken in code written to enforce it.
2. **The untilted search walks outward** (four directions x six distances to 60 px) instead of sampling
   four fixed points, the way `clear_label_seat` rings out for verge-hugging features and for the same
   documented reason: such a feature sits at the busiest node, so its surroundings are the most crowded
   ground on the map.
3. **`label_above` CONSTRAINS the search instead of replacing it.** Its caller sets it from
   `label_seat_clear` - a two-seat verdict about STRUCTURES that knows nothing about lanes - so reading it
   as "place exactly here" skipped the lane search entirely on the boards that set it.
4. **Structures and ways are ONE search.** Every candidate is filtered by the engine's own
   `label_seat_clear`/`label_blockers` and then scored on lane clearance, with the flag kept only as the
   fallback when nothing clears the structures. Honoring the two constraints in separate places is what
   left seats with 22-61 ft of clearance unused.

**WRONG CLAIM 3, and it is the one that cost the most: TWO OF THE FOUR "VERIFIED" CHANGES WERE NEVER IN
THE TREE.** Items 3 and 4 above were written up as landed and verified. They were not. `git log` shows
`136e0398` -> `9805d654` with neither commit in between, and the working file still read
`_lx, _ly = max(_cands, key=_box_clearance)` - the unconstrained line both items claim to have replaced.
Both patch scripts printed success and the `git commit` appeared to run. So the cohort runs that produced
"seeds 14 and 36 still notch after all four changes" were measuring **two changes, not four**, and the
conclusion drawn from them - that the design did not work and my model of the code path must be wrong -
was false. The design was right; the code was absent.

This is the same family as WRONG CLAIM 2 one section up (a measurement against a reverted tree), which
means the lesson did not take the first time. It has now: **after an edit, confirm the string is in the
file, the commit exists, AND the diffstat names the file.** All three. A script's success message and a
clean `git commit` are each, separately, worth nothing.

**WHAT THE INSTRUMENTATION FOUND (one run, and it was decisive).** The previous entry's next step was
right - stop pulling levers, log the actual candidate list. For seed 14: 24 candidates, 3 clearing the
structure filter, the best of those with **7.8 ft** of lane clearance - and the caption drawn at a seat
with **-1.2 ft**. The good seat was being found and then discarded. That is item 3's diagnosis exactly,
which is what pointed at the code being missing rather than the model being wrong.

**THE ROOT CAUSE IS UPSTREAM OF EVERYTHING ABOVE.** `place_kosatsuba` computes `lab` by testing
`label_seat_clear` at the DEFAULT distance only - `y +/- h/2 + 11` - and passes that verdict on as
`label_above`. So a board whose below-seat is blocked at 11 px and perfectly clear at 35 px gets flagged
"above", and the flag then forced the caption to the far side. The premise the flag encodes ("below is
unusable") is a narrower claim than the one it is read as. The fix is not to weaken the flag but to stop
computing it from a question that cannot see the answer: **`kosatsuba` now asks the structure question
itself, of every candidate in its outward walk, and `place_kosatsuba` no longer passes `label_above` at
all.** `lab` is still used, one line up, to prefer a BOARD POSITION where some caption seat exists -
a different question, and a good one.

**`label_above` STAYS A HARD CONSTRAINT for anyone who sets it.** The first version of this fix made the
flag advisory, and `test_kosatsuba_records_a_blocking_struct` caught it immediately (507.1 > 500) - the
test calls `kosatsuba` directly and pins the flag's contract, which exists for the gate-adjacent case its
docstring describes, where the caller knows something the manifest does not. That test was right and the
change was too broad: an external caller's knowledge is not a hint. So the flag now NARROWS the candidate
pool rather than naming a point, and the lane score still chooses within the allowed side.

**RESULT: 43/48, all five caption notches cleared, zero new failures against baseline.** Seeds 14 and 36
are FIXED - the entry above saying they "remain" and are "not understood" was measuring absent code.

## 2026-08-20: THE INSTRUMENT-DISCRIMINATION FAMILY - five instances, three sessions, one day

Named by the Inashiro session, and recorded here because it is now clearly the dominant failure mode
across this whole effort - more costly than any individual bug any of the three sessions fixed. **The
failure is never in the measuring. It is in the step immediately after, where an accurately-observed
narrow fact is promoted into a broad claim it does not establish.** Every instance passed review at the
time because the underlying number was correct.

| # | the true observation | the unsupported promotion | what it cost |
|---|---|---|---|
| 1 | 7 call sites of `pointed_ring` | "1,329 tint candidates" | a wrong ledger entry, caught by a peer; real figures 2 of 706 entering, 10 shapes judged |
| 2 | a cohort run measured 41/48 | "the unified seat search does not help" | two attempts spent looking for geometric causes; the code was never in the tree |
| 3 | three of 48 seeds are crescent-rolled and fail | "it is a crescent defect" | p ~ 0.04 treated as decisive; a sixth fix attempt against dead code |
| 4 | 60-120 ft of clearance to FABRIC beside each stranded house | "the ground is wide open" | attempt ten; the open ground was flooded paddy, which the measurement did not count |
| 5 | "not in my tree, I have not touched `waterfields/` all session" | "those items are unclaimed" | three sessions nearly rewrote `carve.py` twice |

Instance 5 is the one worth dwelling on, because it is the only one that is not a measurement at all -
it is a **coordination** instance, which shows the family is about inference rather than instruments.
A peer's report about its own working directory is a true statement with a narrow scope; "unclaimed" is
a statement about three sessions. I had better evidence to hand (my own earlier message assigning those
items) and overrode it with the weaker source. Also note instance 4's mirror, recorded in 2b: an
erosion test that says the dry ground stays connected, but counts only crop - so it answers about mud,
not about where a way can run.

**THE REMEDIES, both cheap, and each would have caught a different subset:**

1. **Name the commit a measurement was taken against.** Catches 2 (and the architecture session's own
   retraction, which baselined against a HEAD older than the lane-web feature). A measurement whose
   tip is not stated is not a measurement yet.
2. **Ask what fraction of the POPULATION looks like the signal, before calling it one.** Catches 3 and
   4. The base rate is the check, and it is one line.
3. **For coordination specifically: "not in my tree" and "unclaimed" are different sentences.** A peer
   cannot see the other peers. Only the session that ASSIGNED an item knows who owns it, so ownership
   questions go to the assignment record, never to a third party's working directory.

**A SIXTH INSTANCE, AND IT IS A DIFFERENT KIND OF CLAIM: the SET RELATION.** The five above are all
"measured the wrong quantity". This one is "asserted a relation instead of constructing it", and it
belongs in the same family because it fails the same way - the reasoning is valid, the object it is
about is not what you think it is.

Ranking board positions by caption feasibility, I probed a NEAR RING of 8 seats rather than all 48,
and justified it: the full candidate set is a SUPERSET of the ring, so ring-feasible implies
search-feasible, which is the one-way guarantee a PREFERENCE needs. The argument is sound. **My ring
was not a subset** - it used 45-degree diagonals while the search's annulus runs
30/60/120/150/210/240/300/330 - so a board could be ranked sitable on a seat the search never offers.
Seed 14 did not move, and the cohort read 42/48 twice running for two entirely different reasons.
Rebuilt as exactly the twelve zero-standoff members of the real candidate list, seed 14 passes.

So the discipline has two halves, pointed at two kinds of claim:

- **Measure what the RULE measures** - not a near-enough quantity wearing the same name.
- **CONSTRUCT the subset; do not assert it.** Where an optimization rests on set containment, build
  the smaller set FROM the larger one in code, so the relation cannot quietly stop being true when
  someone edits the larger one.

**And one that generalizes past this project: validate an instrument on inputs whose answer you already
know, BEFORE you point it at the unknown.** The `seat_cluster` edge-turn metric written the same day
snapped to the nearest envelope vertex, so a square anchored mid-edge reported 180 degrees where the
truth is 0 - it would have reported a corner on every map in the cohort and "confirmed" the hypothesis
it was built to test. Three known shapes (square mid-edge 0, square spanning a corner 90, square
half-lap 180) caught it in one run. **An instrument that cannot fail its own sanity case is not
evidence, and a hypothesis confirmed by an untested instrument is worse than no result** - it ends the
investigation.

## 2026-08-27/28 (feature 133 T92): a gate that "hangs" is a serial roll ladder; and how the harness fights a long gate

**The shape.** The first unlocked `make done` in two days sat 25 minutes with ONE xdist worker at
100% and seven idle. Not a hang: `test_a_rolled_cohort_passes_the_whole_gate` rolled four seeds
SERIALLY (a coverage reason that only matters under the coverage floors), each seed with the driver's
re-roll ladder (up to five rolls of ~80 s when a farmhouse is stranded), while the rest of the suite
finished. Per-test durations (`make durations MARK=rolls_map N=40`) named it in one run - 1,329 s
against the next-slowest at 101 s. Reach for `durations` BEFORE bisecting seeds: the seed hunt
(24 seeds at 90 s each) burned 20 minutes to learn only that rolls take 65-101 s.

**What could not be measured.** `py-spy dump` cannot attach in this container - ptrace is refused
even as root - so a hot worker's stack is not available; /proc gives nothing useful for Python.
The measurement that works is the per-test duration table, or a per-seed roll with a wall clock.

**How the harness fights a long gate (measured, three ways).** (1) A foreground Bash call is
capped at 10 minutes whatever `timeout` is passed - the command is killed and its make with it,
so nothing is stamped. (2) A background Bash task running `make done` was killed by the harness
within seconds, twice (status "killed", no output), while the same session's 20-minute bisect and
22-minute durations runs in background survived - the difference is not understood; do not rely on
a background `make done` surviving. (3) What works: launch the gate fully detached -
`setsid nohup bash -c '... make done > gate.log 2>&1; echo EXIT=$? >> gate.log' &` - and watch
the log with a Monitor for the verdict lines. The run-log/verification stamp is written by make
at the end, so a killed wrapper leaves NO record: an empty record after a "run" means the run
never finished, not that it was green.

**The fix that was in scope.** The GM's ruling (T92): the gate must TERMINATE; failures become
expected failures for a separate session. So the cohort test rolls 4-wide at the gate (serial only
under `L7R_COV_FLOORS=1`, which the Makefile now exports under COV_FLOORS) and judges against a
pinned expected-failure set with `baseline_verdict`'s rule (outside the set = regression, clean
pinned seed = stale pin).

## 2026-08-28 (feature 137 T03): the lock hid that T31/T32 broke the tier - 18/24 to 2/24 in two tasks

The reference-hamlet period's lane passes (T31 `_touch_junctions`, T32 `_smooth_web`) made Inashiro
right and the TIER wrong: a 24-seed cohort passed 18 at the lock and 2 after T32, with
`houses_clear_of_lanes` on 13 seeds and `features_do_not_overlap` on 10. The doctrine written into
T31 - "a junction link crosses nothing, but it may brush a fence" at a 4 ft footprints-only
margin - was tuned on the one map, where every refused link was 29 ft long beside a garden; on the
tier those brushes are lanes inside a house's 40 ft clearance and over garden rects the matrix sizes
6 ft wide. Two lessons. (1) A pass tuned on one map is a hypothesis until the cohort has run - the
lock's accepted cost ("found at unlock") was two days of building on a broken web. (2) A margin
the GATE will not accept is not a margin the generator may use, whatever the picture on one map
says; the fix that works is to hold every link to the web's own fabric margin and route the
detour, never to relax the brush. The bisect that found this needed a CLEAN scratch clone: the
first attempt measured one tree four times because a copied-in instrumented file blocked every
checkout silently.


## 2026-08-28 (feature 134 T50): a REPAIR that cannot satisfy the CHECK it exists to satisfy, and a router whose lattice narrows every corridor

Three lane-web defects, all latent for a long time. The threshing-yard roll (T49) did not create any of
them - it moved geometry until each showed. That is the shape worth remembering: a placement change is a
FUZZER for every rule that was tuned on one arrangement of the same map.

**1. The repair's threshold and the check's threshold were different numbers, and nobody compared them.**
`lanes_bend_like_paths` fails ANY turn past 140 degrees. `_smooth_web`'s hairpin repair would only cut an
arm under `_ARM_FT` (40 ft). So the band between them - a hairpin whose arm is 40 ft or longer - was drawn,
failed, and could not be repaired by any pass. Tripwire seed 47 sat in that band with a 62 ft arm. Nothing
warned, because a check firing looks the same whether the repair declined or the repair was never able.
**Whenever you write a repair for a check, state both thresholds in one place and ask what lives between
them.** The fix was not to raise the cap: the cap was standing in for "do not destroy a lane doing real
work", so that got MEASURED instead (no farmhouse loses its way; the tip left behind still reaches
something by the check's own figures), and the cap became a bound on how much of the picture one cut may
change.

**2. A rule asked ONCE, at creation, by passes that all mutate afterwards.** `draw_web_lane` refuses to
draw a lane under `_WEB_MIN_FT` (30 ft), and then a trim, a hairpin cut and `_stop_at_network` each shorten
lanes with nothing re-asking. A 20.5 ft fragment shipped. **A validity rule enforced at construction is not
enforced at all in a pipeline that keeps editing the object** - it needs a sweep at the end, over what
actually ships.

**3. THE ROUTER'S PLANNING CLEARANCE IS NOT THE CLEARANCE YOU PASSED IT.** `_route` plans on a lattice and
uses `gap + cell * 0.71`, inflating by half a cell's diagonal so that "this cell is free" means every point
in it is clear. That is load-bearing and correct. But it is charged against the CORRIDOR, and it is
invisible at the call site: `gap=_TOUCH_GAP` (4 ft) with `cell=6.0` really demands **8.26 ft**, and
`gap=WEB_FABRIC_GAP` (7) with `cell=10.0` demands **14.1 ft**. Seed 27's only way out was a corridor about
7 ft wide, so both rungs reported NO ROUTE for a journey that plainly existed - and the caller's error
message says the piece could not be joined, never that it was the lattice that could not see the gap.
**When a router says no, check its effective clearance before believing the geometry.** At `cell=3.0` the
same 4 ft standard costs 6.13 ft and the ways round opened.

**And a candidate generator that only ever aims at the NEAREST point of a way writes off the whole way when
that point is the walled one.** Nine points further along seed 27's same lane were reachable. Sampling
along the way was the other half of the fix.

**How each was found: by MEASUREMENT on the map's own manifest, not by reading the code harder.** A grid
search over `wip/tw27.json`'s footprints, run at each rung's effective clearance, answered "is there a
corridor, and how wide" in one turn - after two turns of reasoning about the code had produced only
plausible guesses. When a placer or router refuses, probe the geometry it was given.

## Two test-cost levers that were measured and do NOT work (feature 158, 2026-08-29)

Both are the obvious next thing to reach for, and both are recorded here so the next session spends
the measurement once rather than the implementation twice.

**Shrinking a test's `plan.envelope` does not shrink its fan.** The 39-second
`test_the_fit_gives_a_saturated_best_aspect_the_full_search_it_was_denied` looked like the textbook
case for the GM's own *"reducing the size of the test fixture settlement"*. Taking the shared test
envelope from a 600 px square down through 400, 300, 200 and 150 leaves the drawn fan at **1,985
plots and an acreage error of 0.891 at every one of them**. The envelope is not what clamps a
saturated fan - the CANVAS is, and the canvas is derived from the household count (`canvas_for`,
`plan.py`). What actually costs the seconds is the PLOT COUNT, set by `plot_across` and `row_step`;
coarsening those from 46/(26,30) to 138/(78,90) took the fan to 257 plots and the test to about a
quarter of its time, with the branch under test and both assertions unchanged.

**`COVERAGE_CORE=sysmon` is SLOWER here than the C tracer.** Python 3.14 with coverage 7.15 and
line-only coverage (no `branch = true`) is precisely the configuration `sys.monitoring` was built
for, and the tracer looked like half the gate's cost. Measured on the same tree and the same
selection: **ctrace 16.2 s wall / 1 m 30 s CPU against sysmon 20.1 s / 1 m 59 s**, with the coverage
tables byte-identical. The premise was wrong too - the "coverage doubles the gate" reading came from
a baseline whose roll cache was cold; on a warm tree the tracer's share is small.


## A directory-prune tuple keyed on NAMES is a trap for any new top-level tree (feature 161, 2026-08-30)

`render_cache.engine_fingerprint()` and `gencache.engine_files()` both walk the skill directory and
decide what counts as ENGINE SOURCE by pruning directories BY NAME:

```python
dirnames[:] = sorted(d for d in dirnames if d not in ("pool", "wip", "tests", "__pycache__") ...)
```

Feature 161 added a second pool tree, `legacy-hand-authored-pool/`. It is not the string `pool`, so
without being added to both tuples its 18 frozen generators would have been collected as engine
modules and folded into every map's cache key. What that costs, in order of how long it takes to
notice: every live map's stamp goes stale at once, so the next render-sync regenerates the whole
pool for nothing; and thereafter any edit to a frozen exhibit invalidates every live map's cache -
precisely backwards, since the freeze exists so those files cost nothing. **Nothing would have gone
red.** Both outcomes look exactly like a cache working normally, and the synthetic skill dir in
`tests/pipeline/test_render_cache.py` cannot see a tree it does not build.

The fix is to prune `poolmaps.TREES` rather than a literal, so the list has one home. The general
shape: **when you add a top-level directory, grep for tuples of directory names before anything
else** - they are invisible to every test that builds its own fixture tree.

Note the companion trap points the OTHER WAY. `ci/delta.py`'s `_ENGINE_DIRS` also names `pool/`,
and there the legacy tree had to be ADDED, because that list answers a different question: not "is
this engine source" (a map generator is not) but "does a change here owe the paid gate". Two lists,
same literal, opposite corrections.

## "The record already covers it" is worth checking against what the check can actually SEE (feature 161)

`tests/test_villages.py`'s stale-render sweep ends in `assert checked` and its message says *"no
LIVE hamlet render to check"*. That message had not described the test's behavior since the
2026-08-16 freeze committed the exhibits' renders: a live map's `.svg`/`.png` are gitignored and
absent from a clean checkout, so **every render it actually checks is a FROZEN exhibit** - measured
2026-08-30, 8 of 8. Splitting the trees while it still walked the live pool alone would have taken
`checked` to zero and turned the assertion red.

Two things worth carrying forward. First, the assertion is the only reason this surfaced loudly; had
it merely `continue`d over an empty list, the split would have silently retired a guard against
exactly the kind of staleness it exists to catch, which is the "a check that never runs looks
exactly like a check that passes" failure in its purest form. Second, **the code and its own message
disagreed, and only counting the files on disk said which one was true** - reading the test would
have confirmed the wrong belief.

## A git worktree's `.git` is a FILE, and the baseline procedure lives in one (feature 161)

Principle XIII mandates taking the regression baseline in a detached worktree. In a worktree `.git`
is a file containing a `gitdir:` line, so any code doing `root / ".git" / name` raises
`NotADirectoryError` there. `scripts/gate-stamp.py` did exactly that and crashed once per area
during this feature's own baseline - the gate ran and passed, only the recording failed, and it
failed noisily-but-non-fatally, which is the shape that gets scrolled past in a long log.

`git rev-parse --git-common-dir` is the answer, in both a checkout and a worktree. Worth knowing
that the file-not-directory case was already half-handled in that same module (`_cache_path` guarded
`.is_dir()` and quietly gave up), which is why only one of the two paths crashed: **a guard applied
at one call site and not its sibling reads as "handled" until the other one runs.**
