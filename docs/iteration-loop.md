# Iteration-loop efficiency: the measured rationale

*Project reference, split out of [`../CLAUDE.md`](../CLAUDE.md) so it is loaded on demand rather than in every session's context. CLAUDE.md keeps the short always-on version of these rules and points here for the full spec.*

**Load this file when:** you want the evidence behind the loop rules in CLAUDE.md, or you are about to argue with one of them. Every rule here was paid for in measured wall-clock; the incident detail lives here so the rules themselves can stay short.

---

**Iteration-loop efficiency** (profiled with the GM, 2026-07-20): a transcript-timestamp profile of a representative small feature showed **78% of wall time was model turn latency and only 22% tool execution** - tool speed is NOT the bottleneck; the NUMBER of sequential turns is. This holds project-wide (webapp + skills). Standing practice:

- **Batch into fewer, bigger turns.** Group independent recon (greps, file reads, artifact inspections) as parallel tool calls in ONE turn instead of one lookup per turn, and apply a planned multi-edit to a file in one turn rather than edit-per-turn. Only serialize when the next step genuinely depends on the previous result - do not batch past a real decision point, and never skip looking at a result that could change the plan.
- **Docs-only diffs skip the gate.** If everything changed since the last green gate is markdown/docs, do not re-run the gate (`make done`) - it runs once at stop-work for the code that changed. (This redundancy has cost a full gate run before: a re-run after only a docs edit.)
- **Before changing ORDERING or architecture, read the paths and settle the design first.** When a change touches *when* something happens relative to something else - draw order, placement phases, which registry a feature is recorded in, what runs before/after a flush - read every path involved in ONE batched pass and decide the sequence up front. The failure mode is discovering the ordering one gate failure at a time: 2026-07-25 turned a small rule ("no tree drawn on a roof") into four fix-fail-read cycles and ~13 minutes, because each fix revealed the next ordering fact. Those facts were all readable in advance. This is advisory - no hook can detect it - so it is backed up where it bites: the `/diagram` engine now carries a **DRAW ORDER** map in [`.claude/skills/diagram/CLAUDE.md`](../.claude/skills/diagram/CLAUDE.md) plus pointer comments at the registries and the order-sensitive methods themselves, so the rule is in front of you at the moment you would break it. Where you add ordering-critical code elsewhere, do the same: a comment at the point of change beats a rule in a document nobody re-reads.
- **Batching is ENFORCED, not advised** (GM 2026-07-25, [`scripts/batching-hooks.sh`](../scripts/batching-hooks.sh), tested by [`scripts/test-batching-hooks.sh`](../scripts/test-batching-hooks.sh)). When **3 of the last 6 turns** each made a single quick read-only call, a PreToolUse hook BLOCKS the next recon-shaped call and its message carries the whole counter-playbook (batch independent lookups, fold a retry-patch + regen + check into one asserted script, put the action in the same command as the read, never pad with no-ops) so no session rediscovers the strategies. Only quick single reads are ever the blocked call - substantive work (heredocs, `&&`/`;` folds, pytest/make/git-commit runs) always passes, because a 2026-08-09 profile of a patch-grind session found 49 of its 52 blocks landing on patch scripts or already-folded commands, one firing per 14 turns (~9 min of pure block latency) and an induced no-op padding turn. The bar also re-arms higher after each firing (3 doubling toward the window of 6) and decays back to 3 as turns batch, so a reminder stays a reminder instead of a wall. It classifies by measurement, not guesswork: calls in one message arrive milliseconds apart while calls in separate turns are a full round trip apart, and "quick" is the call's actual measured duration. This exists because the doctrine below was written on 2026-07-20 and a profiled feature five days later still batched **zero times in 139 calls** - 104 of which finished in under 2 seconds, doing 29 seconds of work between them at a cost of ~23 minutes of latency. Documentation you have to remember is not a control.

  **Re-tuned 2026-08-08, and the re-tune is the interesting part.** The original counted *consecutive* serial turns and reset to zero on any batched turn or any slow call. A profile of the caption-resize session says that let nearly everything through: **147 of 162 tool round trips (91%) made exactly one call**, costing **22.7 minutes of model latency for 4.0 minutes of tool execution** - and across all of it the hook fired **twice**. The 15 batched turns were scattered through the serial runs, and each one wiped a streak of five that was one turn from tripping. So the counter is now a ROLLING WINDOW - *how many of the last 6 turns were serial and cheap* - with the threshold down to 3; a batched or slow turn is one `0` that ages out instead of an amnesty for everything around it. A block still clears the window, so a genuinely serial chain can never deadlock: worst case one interruption per 3 serial turns, and at 9.2s per round trip a block that turns the next three single calls into one message has already paid for itself. Three implementation traps are recorded in the script and pinned by tests: bash's `${s: -n}` returns the EMPTY string when `n` exceeds the length (so an unguarded trim erased the history on every write and the hook could never fire); on a batched turn the FIRST `posttool` already sees `calls=2`, so the turn's history entry has to be appended at `pretool` or the batch silently overwrites the previous turn's entry; and a **backgrounded** call returns in milliseconds, so the duration test read `make done --run_in_background` as the cheapest possible recon and blocked the one thing these rules most want you to do - `run_in_background: true` is now exempt from both the count and the block. (A backgrounded turn is still a TURN and still ages the window, which is correct: the window asks how much of your RECENT work was one-call recon.)

- **A `-k` subset is not a pre-gate check, and that is ENFORCED too** (GM 2026-08-08, [`scripts/gate-hooks.sh`](../scripts/gate-hooks.sh), tested by [`scripts/test-gate-hooks.sh`](../scripts/test-gate-hooks.sh)). If the only local pytest run since your last `.py` edit used `-k`, the hook BLOCKS `make done` once and tells you to run the whole file. The rule itself is older - the diagram dev-loop doc has had a section heading saying exactly this since 2026-07-25 - which is the point: a session read it, ran `-k "kura_side or punishment"`, went to the gate, and the gate died on `test_place_punishment_spot_probes_for_a_clear_caption_seat`, a test in the same file on the same function that the filter did not select. A whole-file run costs ~45s; that gate cycle cost 3.9 minutes of idle plus the fix turns. A source edit clears the flag (an earlier run predates the code and cannot vouch for it), a run without `-k` clears it, and `GATE_OK` in the command overrides with a reason. Fourth control of the same kind, for the same reason as the other three.
- **`make done` runs every phase and reports all failures together** (both Makefiles, 2026-07-25). It used to stop at the first failing phase, so a lint slip hid a type error hid a coverage hole and each hidden failure cost another full gate run to discover. Fix everything it lists, then re-run once. When the coverage gate fails it also runs [`scripts/uncovered-in-diff.py`](../scripts/uncovered-in-diff.py), which intersects the coverage miss with `git diff` and prints **the lines you changed that no test reaches**, with their source text - so the retry is a certain fix instead of a hunt through a 5,000-line module.
- **Never re-run a suite the gate just ran, and never run pytest without `-n auto`.** Both Makefiles run `pytest -n auto`; serial pytest is ~7x slower on this box. A green `make done` is the proof that every test in it passed - re-running one of its files "to be sure" buys nothing. Measured cost of getting this wrong (2026-07-25, transcript profile of a 69-minute feature): **13.2 minutes, 19% of the whole feature's wall clock**, spent re-running a regression suite serially that the gate had already run in parallel minutes earlier. It was the single largest time sink in the profile - larger than every real gate run combined.
- **Read derived data from the recorded artifact, not by re-running the generator.** Second-largest sink in that same profile: 7.6 minutes across three runs of an analysis script that re-ran all 17 map generators to compute something the manifests already contained - the same analysis reading the JSON took 0.2s. Regenerate when you need to change what a generator DRAWS; read its output when you need to know what it drew.
- **Iterate on the motivating artifact; run the full test bed exactly once, at the end.** The red/green loop runs against the one artifact (map, fixture, page) that exhibits the defect - a single-artifact rebuild is cheap, so cycles are near-free. The full sweep (the whole test suite / every generated artifact) is reserved for AFTER the motivating artifact is in a good state - but it is MANDATORY then whenever shared code changed, since every downstream artifact depends on it and the sweep is what turns "no other case has this bug" from a hope into a verified claim. Anti-pattern: using the full suite as the FIRST verification of a shared-code change - a failure that would surface in seconds on one artifact surfaces many minutes in. Package-specific gate timings and sweep mechanics live in that skill's dev-loop doc (e.g. [`.claude/skills/diagram/CLAUDE.md`](../.claude/skills/diagram/CLAUDE.md)).
- **Background the final gate - and NEVER poll it** (GM 2026-07-25, now ENFORCED by [`scripts/no-poll-hooks.sh`](../scripts/no-poll-hooks.sh), tested by [`scripts/test-no-poll-hooks.sh`](../scripts/test-no-poll-hooks.sh)). Start the stop-work gate with `run_in_background`, write the docs/commit message while it runs, and act on the COMPLETION NOTIFICATION the harness sends; report done only after it comes back green. Watching a backgrounded command is worse than running it in the foreground, and a transcript profile proved how much worse: **10.9 minutes - 35% of a 31-minute feature - went to polling two gates that had already finished** (they took 97s and 98s; the waits took 351s and 401s). The wait loop used `pgrep -f "make done"`, which **matches its own shell** - the pattern is an argument of the very command line being searched - so its `break` could never fire, and `command sleep` was quietly evading the harness's own foreground-`sleep` block. The hook now refuses all of it at PreToolUse: `pgrep -f`/`pkill -f` on a literal pattern, any loop containing a `sleep`, and the `command sleep` / `/bin/sleep` / `env sleep` bypass forms. A real wait on EXTERNAL state the harness cannot see (a dev-server port, a remote queue) passes by putting `POLL_OK` in the command with a note saying what it waits for. This is the third control of the same kind, for the same reason: the "background the final gate" instruction was already written here, and the session followed it and then blocked on the gate anyway.
- **A review agent is the most expensive thing you wait on - SCOPE it, SPLIT it, launch it EARLY** (GM 2026-08-08). Profiled on the caption-resize session: one `settlement-review` agent, handed two maps with no scope, ran a full audit - **12.3 minutes, 22% of the task's whole wall clock**, with the session idle for 11.4 of them, and two of its five findings were pre-existing defects unrelated to the change. The agents now take **`DELTA: <what changed>`** and review the change, whatever the re-pack moved, and whatever the change made incoherent with its neighbors, naming the sweeps they skipped; `FULL` stays the default for a new or heavily-rewritten artifact. Run **one artifact per agent, in parallel** - the sweeps share no work across artifacts, so bundling them just serializes two audits behind one notification. And launch the moment the artifact is final, before the visual pass and the commit: everything you do while it runs is free, everything after it is added on. This does NOT weaken Principle I - the review still happens, it is just asked the question you actually have.
- **Resolve the session's clone NAME in turn 1, not after the recon** (GM 2026-08-08). The clone-name check is now announced by [`scripts/clone-sync-hooks.sh`](../scripts/clone-sync-hooks.sh) on the FIRST prompt of any session with no claimed clone, because the pretool backstop only speaks at the first EDIT and that is far too late: a session spent 4.7 minutes on recon and planning, discovered only then that its name did not resolve, and the GM's `/rename` became **4.6 minutes of dead wall-clock** instead of something that could have overlapped the analysis. A blocking question you can see coming should be asked while you still have other work to do.
- **Do NOT cut the ritual steps** (regression-fixture freeze, overlap-registry classification, record-the-why docs, the stop-work ritual). GM-confirmed 2026-07-20: they cost ~2 minutes per feature and are why the regression rate stays near zero. The savings come from turn structure, never from skipping guardrails.

## The 5% threshold: a whole-process speedup is never "only N seconds" (GM 2026-08-16)

Stated while deciding feature 026 (the cache-backed gate): **a >=5% wall-clock speedup to a whole
process - a gate run, a sweep, a full generation pass - is always above the threshold of caring,
even when the absolute saving is a handful of seconds.** 10 s off a 180 s gate is more than 5% and
matters; 30 s off is a sixth of the whole run and is extremely significant. The reasoning is the
same one at the top of this file: iteration cost compounds, because the gate runs many times a day.

The distinction that keeps this from licensing micro-optimization: it applies to END-TO-END
processes, not individual functions. A 5% win inside one function is usually below the threshold -
unless that function effectively IS the process (the `main` of a scripted run), in which case it
is the process and the rule applies. When weighing a perf change to a loop, compute the
percentage, not just the seconds, and never argue "it's only N seconds" against a >=5%
whole-process win.
## The 2026-08-16 profile: the cut-bank fix, and where the time goes now

First full transcript profile taken AFTER the 2026-08 performance refactors (pool-regen fan-out,
cache-backed gate, batched crop inspection, batching hooks), on a representative small engine fix
(the cut-bank scrub margin): **14m33s prompt-to-verified-in-main**, breaking down as **60% LLM
turn latency (520s), 28% idle waiting on background work (249s), 12% foreground tool execution
(102s)**. Compare 2026-07-20's 78%/22% split on much larger absolute tool time: both halves
shrank. The findings that set the next round of rules:

- **The gate was NEVER on the critical path.** It ran 177s and finished 92s BEFORE the
  settlement-review DELTA agent (350s) - the critical path was diagnosis -> design ->
  implementation -> the REVIEW tail (84s past the green gate) -> wrap-up (57s). Speeding the gate
  further buys nothing on this task shape; launching the review earlier and making it cheaper buys
  the tail. Hence the sharpened review-launch rule (diagram CLAUDE.md, "Invoking a review agent")
  and `tools/scatter_audit.py` (feature 108), which converts the review's ~21-tool-use hand parse into
  one seconds-fast script.
- **Seven long reasoning turns were 273s of the 520s LLM time**, and the largest (75s) partly
  re-derived a recorded open decision. Hence the open-decision-sketch convention (diagram
  CLAUDE.md, "An OPEN DECISION carries an implementation sketch").
- **A 38s foreground pool-regen sweep bought nothing** - the rule, with its render claim VERIFIED
  against the render model rather than assumed: foreground-regenerate only the MOTIVATING map (a
  session needs its render for its own crop inspection); run the whole affected test file; do NOT
  run a pre-gate `pipeline/regen.py pool/*/*.gen.py` sweep. The gate verifies the pool itself
  (`DIAGRAM_SKIP_RENDER` + gencache), and `sync-with-main.sh` render-sync REGENERATES main's
  renders from main's own committed tip (RENDER MODEL, GM 2026-07-22) - so clone-side renders of
  non-motivating maps feed nothing at all.
- **Projected floor for tasks of this shape: ~12 minutes** - roughly 8 minutes of genuinely serial
  reasoning and implementation with the review tail fully overlapped. The next profile taken after
  these rules land compares against that number.

## The 2026-08-16 profile #2: the fan-toe pond fix (45.7 min), and the cohort fan-out it bought

Second post-refactor profile, on a GM-reported map defect (a field pond spilling across its plot).
**45.7 minutes** prompt-to-synced, attributed with every second in exactly one bucket: **44% LLM
generation (1206s over 148 responses), 40% idle waiting on background work (1087s), 9% unit tests
(235s), 6% hamlet generation (178s), 1% git/sync/lint/crops**. The review agents cost nothing -
launched early, they finished inside the cohort's shadow, which is the launch-early rule paying off.

Why a "simple" fix ran long, and what each finding bought:

- **The two 24-seed cohort rolls were 17.3 min of the 45.7, ~11 min of it critical-path idle.** The
  cohort is the verification step of every placement-rule change, and `python3 -m l7r.diagram.hamletgen --batch`
  was still SERIAL - `regen.py` and `cohort_audit.py` had been fanned out in the 2026-08-15 round
  and this CLI was simply missed. Fixed the same day: **526s -> 71s (7.4x)**. Two lessons past the
  fix itself. First, when a perf round parallelizes a class of work, census every entry point into
  that class - the one nobody profiles is the one that stays serial. Second, **the verdict-identity
  check has to control for what else moved**: the parallel run differed from the serial baseline on
  3 of 24 maps, which looks damning until you notice the baseline predated a mid-task merge of
  another session's engine round (whose own notes predicted exactly that `field_ringed` marginal
  flip). Re-rolling only the three differing seeds serially on the CURRENT code proved the match in
  ~45s. Diff against the same code, not against an older log.
- **A second iteration (~8 min) because the first fix used the check's PREDICATE but not its full
  INPUT SET.** Placement fitted the pond against its host plot; the check scans every plot ring plus
  the drain hem, and a comb fan's rings overlap at the fan/grid seams. The existing "placement and
  its check must read the SAME manifest source" rule covers the data source; this sharpens it to the
  EXTENT of that source. The cohort caught it, which is the argument for cohorts over single maps.
- **~4-5 min (~10%) lost to three failed heredoc patch scripts**, all quoting slips in
  Python-that-rewrites-Python, none of them wrong anchors. Hence the "edit with `Edit`" rule in
  CLAUDE.md - it batches into one turn just as well and cannot fail this way.
- **The mid-task merge conflict was cheap** (~4.5 min including a second gate and regenerating four
  maps, ~1 min of it the actual resolution). Concurrent sessions colliding is inherent; nothing here
  suggests a process change.
- **Projected shape after the fan-out: ~28-30 min for this task, ~20 of it model latency.** Past
  that point the remaining cost is reasoning and the verification rituals, which is where it should
  be.


## The `make quick` profile (GM 2026-08-26): where 30 s went, and where 23 s still goes

Measured on the 22-core container, scope locked, 3,675 tests in the quick set.

| component | before | after | how |
|---|---|---|---|
| ruff check --fix + ruff format + mypy (warm cache) | 0.33 s | 0.33 s | already negligible |
| pytest collection (every worker collects the whole suite; not imports - 0.29 s of imports, the rest is pytest walking ~3,700 tests: parametrization + fixture resolution, spread evenly ~0.6 s per test directory) | 5.4 s | 5.4 s | the floor; no single directory to cut |
| worker spawn | ~0.3 s | ~0.3 s | negligible (-n 0 costs the same as -n 22) |
| test execution, ideal (270 CPU-s / 22 workers) | 12.3 s | 11.3 s | - |
| scheduling tail (critical path + `--dist load` imbalance) | ~12 s | ~5 s | the 9.0 s critical-path test was a full-gate **coverage carrier** - it exists to execute 33 deep statements under coverage, and quick runs `--no-cov`, so it proved nothing there; `coverage_only` marker, 4 tests deselected (29.3 -> 24.6 s). Then `--dist worksteal` in place of `load`, which hands each worker a fixed slice and leaves the last worker running ~5 s alone (27.5 -> 22.0 s wall) |
| **`make quick` wall** | **~30 s** | **~23 s** | |

Amdahl's reading of what is left (23 s): 5.4 s collection is fixed and evenly spread; 11.3 s is
the parallel ideal of 250 CPU-seconds of real tests; ~5 s is the remaining tail (the longest
single tests are now 4.3 s: a site-justice proposal, a city-frame check, a comb-grain roll). The
only lever left worth more than a second is the CPU itself: the two biggest files are
`test_regressions.py` (the corpus replay, 33 s CPU after the carriers left) and
`check_village/test_driver_and_fixtures.py` (32 s CPU - "every solid struct is gated off every
hazard", ~3 s per parameter because each runs a targeted gate on a whole fixture). Halving those
would save ~3 s of wall. Not taken: a 23 s quick is at the point where a model turn costs more than
the test run, so the next gain is fewer turns, not a faster gate.

Also enforced from the same day: `make quick` and `make done` never share a command
(`gate-hooks.sh`) - `quick` is a subset of the 70 s locked `done`, and chaining them was 1.5 min of
duplicated tests in one 11-minute task.


## Tier relevance (GM 2026-08-26, feature 133 T17) - and the idea kept for later

While scope is locked to the reference hamlet, tests that exercise town/city/capital-only features
prove nothing about the map on the sheet. Every test carries a `tiers(...)` marker naming the tiers
it is relevant to (untagged = all); the suite runs with `--tier hamlet` under the lock and deselects
the rest - 731 tests on the day it landed, quick 22 -> 19.5 s wall (the remaining floor is
collection, 5.4 s, and the untagged city-fixture gate tests that test shared checks). The first
tagging pass was SCRIPTED from the tier names each test's body mentions, written into the source as
ordinary decorators so it is reviewable and correctable by hand; hamlet and village share the
homestead engine, so a test naming either stays in.

**Built the same day, off the shelf (T28):** the GM's long-run idea - *"based on what code changed,
we would be able to detect ... in an automated way"* - is `pytest-testmon`, adopted in `make quick`
on 2026-08-26 with `--testmon-forceselect` (plain `--testmon` stops selecting whenever `-m` is used).
It records, per test, the code the test executed, and selects only tests whose executed code
changed. Measured: nothing changed -> "no tests ran" in 3.3 s; a one-line engine edit -> 10 tests in
6.7 s; one test function edited -> 1 test in 3.6 s; the first run in a fresh clone pays ~3 s to
build `.testmondata` (gitignored, per clone). Limits, stated: data files are not tracked, so a test
that reads a fixture or manifest re-runs only when its CODE changes - which is why the gate never
selects; and `make quick ALL=1` runs every quick test on demand. The tier tags stay: they answer a
different question (relevance to the map on the sheet) and compose with it.


## The "collection" floor is not collection (measured 2026-08-26, after the GM asked for a quick-tests folder)

The GM: *"could we not move the quick tests into their own folder, and then the pytest command
which invokes the quick tests searches only that folder? ... save us, like, five seconds."* Measured
with a per-file collect timer and a session profile - the earlier "5.4 s collection" figure was
wrong about WHAT it was:

| piece | measured |
|---|---|
| collecting all 91 files, one process (`--collect-only`, `-n 0`) | **1.0 s** of item creation (2.1 s wall with pytest's 0.8 s startup) |
| a zero-test session, 1 worker | 2.1 s |
| a zero-test session, 4 workers | 2.7 s |
| a zero-test session, 22 workers | 5.7 s |
| interpreter exit after importing the engine | negligible (0.6 s total process, 0.55 of it import) |
| plugin autoload disabled | no change (only xdist and cov are installed) |

So the floor is **~2 s of pytest startup + ~0.17 s per xdist worker** - each of the 22 workers is an
interpreter that bootstraps over execnet, imports the engine (0.55 s) and collects the whole suite
(1 s CPU) under 22-way contention, and the master waits for the slowest. Collection proper is 1 s of
that and it happens in parallel. A quick-tests folder would skip the ~20% of items the tier and
marker deselection already drops: **~0.2-0.4 s**, not 5. And fewer workers cut the fixed cost but
cost more in execution (240 CPU-s / W): the optimum is more workers than we have cores. Not done.
What WOULD move the floor is a persistent test runner (workers that stay warm between runs) - a
different tool, noted, not pursued.


## The quick-test audit (GM 2026-08-26, feature 133 T19-T21) - every test above 0.3 s, and the call made on it

The principles applied, in the order they were learned today (constitution v2.8.0 "a test's cost is a cost"):

1. **Fixture size**: the smallest field, canvas or grid that shows the property (a 1- or 2-fan comb, not 5; a 600 px near-ring grid, not 1,000).
2. **Products become axes; sweeps become documented subsets** with the full form under `EXHAUSTIVE=1` and the last exhaustive green in the docstring.
3. **Proofs of tooling** (a cache is faithful, a roster is complete, a whole-tree scan) prove nothing about a map: `EXHAUSTIVE`/gate only.
4. **Tier relevance**: a test, a corpus fixture or a pool sweep tagged for other tiers does not run under the lock.
5. **A test helper's brute-force loop gets the same index the engine got** (bbox prefilters, targeted gates: ask the gate ONE question with `only=`, not 189).
6. **Wall, not CPU, is the goal**: 22 workers make 26 CPU-s of independent tests ~1.2 s of wall; the floor is ~6 s of pytest/xdist overhead plus the longest single test.

Day's arc, `make quick` under the hamlet tier: **30 s -> 14.2 s wall**; pytest 29 -> 11.3 s; per-test total 270 -> 100 s; tests over 1 s: 59 -> 18.

**Changed on the audit (T21)**, beyond T19/T20: the two hazard-matrix axes and the gap-ratchet and label-registry tests ask the gate one targeted question each instead of running all 189 checks (principle 5); seven comb tests build 2-fan combs (1); the near-ring tests use a 600 px grid (1); the rolls_map-marker guard and the waterfields census, both whole-tree source scans, moved to EXHAUSTIVE (3).

**Kept, with the reason - these are the judgment calls for the GM to overrule:**

| test | cost | why it is kept as is |
|---|---|---|
| the regression corpus (251 hamlet/village fixtures) | 24 CPU-s, ~1.2 s wall | every saved bad map still trips its check - the GM's own doctrine; 251 independent tests parallelize completely, so it costs ~1 s of wall; the true fix is change-based selection (run a fixture only when its check's segment changed since the last green run), recorded above as the long-run idea |
| `test_switches` make-driven refusals (12 targets + 4) | ~5 CPU-s | they run the REAL Makefile in a fixture and prove each refusal; ~0.2 s per `make` is process cost (Makefile parse + the switch read); a cheaper fixture would test a copy of the logic, not the logic |
| `test_a_foreign_parallel_coverage_file_reaches_the_report` | 1.3 s | spawns a real coverage subprocess to prove a real merge path |
| the ci tests (git repos in tmp) | 0.3-0.6 s each | each builds a real git repo with subprocess git; the behavior under test is git's |
| supply-banks (2.0 s), hem-is-cropland (1.6 s), intake-snaps (1.2 s), cascade sources (1.2 s) | building 2-3 combs each | each property needs a drawn comb with a stream/hem/second fan; already at 2 fans; the rest is `close_seams`, which profiled as evenly spread geometry, not a hot loop |
| the hinterland scatters (1.35, 1.1, 0.8 s) | a 1000 px scatter each | the scatter density is the property; a smaller canvas would test a sparser sheet - kept at the size the doctrine draws |

**Not done, deliberately**: shrinking the corpus by sampling (every fixture is a distinct bad map, there is no redundancy to remove), and any change to what the engine draws.


## Where `make quick` stood at the end of 2026-08-26 (hamlet lock, 8 workers)

**7.5 s wall** (three runs: 7.56, 7.46, 7.70), pytest 6.2 s, 1,972 tests + 360 deferred to the gate;
the gate's exhaustive test phase 2,502 tests in 26.7 s. Composition of the 7.5 s:

| piece | s |
|---|---|
| pytest + xdist with zero tests (startup, 8 spawns, 8 collections, teardown) | 3.6 |
| the tests themselves: 17.9 CPU-s at 8-wide | ~2.3 |
| ruff check + format + mypy | 0.36 |
| make, the switch reads, the state write, the run-log | ~1.2 |

The day: 33 s -> 7.5 s. What moved it, largest first: the check tests asking the gate one
TARGETED question instead of running all 189 checks (1,430 sites; per-test work 30 -> 17 s); the
scope lock deferring the map-rolling tests; the tier tags; the corpus and the tooling tests
leaving quick for the gate; `worksteal`; the coverage carriers; a second collection hidden in a
closing message; the fixture sizes. The floor now is pytest's own overhead (48%); the tests are
the smallest third.


## The test tree, since 2026-08-26 (feature 133 T29)

`tests/` IS the quick suite. Everything that is not quick lives in a tree of its own and is not
even collected by `make quick`:

| tree | holds | collected by |
|---|---|---|
| `tests/` (with its packages) | the unit forms, relevant to the lane tiers or to every tier | quick and the gate |
| `tests/tier_town/`, `tests/tier_city/` | tests tagged for other tiers only (232 + 451 functions), mirrored package paths | the gate; quick once the scope lock moves to that tier |
| `tests/gate/` | the bad-map corpus, the coverage carriers, the map-rolling tests | the gate only |
| `tests/tooling/` | tests that RUN the make/ci/pipeline tooling (+ the whole ci package) | the gate; quick only when the tooling changed (`ci tooling-fresh`) |

Moved tests import their helpers from the source module; a fixture they take comes through the
tree's `conftest.py` (a parameter name is a use pytest sees and ruff does not). The tier and
tooling MARKERS stay on the moved tests as the exact filter; the trees are the collection scope.
Measured: the zero-test floor on the quick tree 3.5 -> 3.1 s; `make quick ALL=1` (everything quick
runs) 8.7 -> ~7.0 s wall for 1,971 tests; with testmon, an unchanged tree answers in ~3.5 s and a
one-file edit in ~4-7 s. `dmypy run` replaces one-shot mypy in quick (~0.25 -> ~0.1 s after the
first run; one-shot on CodeBuild).


## DECLINED, by the GM (2026-08-26): a persistent test runner

**What was asked:** whether warm worker processes (a per-clone daemon that has imported the engine
and collected the suite, forking workers per run) would remove the ~3 s pytest/xdist floor.

**What was measured** (a fork-server prototype, eight children, the quick tree): forked from a warm
base 11.9 / 13.9 s; the same eight started cold 14.9 s; `make quick ALL=1` with xdist and
work-stealing 7.0 s. The warmth itself is worth ~1 s of wall (interpreter start + engine import,
paid in parallel); pytest's own startup and the per-process COLLECTION cannot be forked away,
because pytest cannot reuse a collected session across processes; and a runner without xdist's
balancing loses 5-7 s to static slicing.

**What it would cost:** a bespoke runner (warm workers + work-stealing + a pre-collected session)
that must be per clone (each session's warm state is that clone's code), local only (never on
CodeBuild), and must die with the Claude session that spawned it - the failure mode being dozens of
orphaned interpreters accumulating over months of sessions in one container.

**The decision:** not built. ~1 s per run does not buy that lifecycle risk. The GM: *"I agree with
that finding."* Reopen only if the per-run count makes a second matter AND pytest grows a way to
reuse collection across processes.
