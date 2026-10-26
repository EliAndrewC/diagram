# 415-gate-incremental-across-tooling - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
## T01 - the run record says what ran, why, and where the time went (FR-002, FR-005)

### T01 Approach (checklist part A)

1. **The goal, in the world.** Anyone reading a gate's run record can tell whether it ran everything, why, how many tests it selected, and how long each phase took - without reconstructing it from a log.
2. **The constraints.** The record is written once per gate run by `LOGRUN`; it must not slow the gate or fail it when a figure is missing.
3. **Where each comes from.** O: the GM's items 2 and 5 (request.md).
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: T26's landing log): the run record held seconds and mode but no reason, no selection count and no phases, and the phase table had to be rebuilt by hand.
5. **The order.** Phase marks first (runstats), then the plan fields, then the record.
6. **The exits.** (a) read the log after each run - not taken, the record is what tools read; (b) the fields - taken.
7. **The search smell.** None.
8. **The budget.** 60 min with its landing.
9. **Done, measured.** Unit tests of `runstats.py phase`/`end` and of the record's new fields (red without); a real gate run's record carries `plan_mode`, `plan_reason`, `selected` and `phases`.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** `runstats.py phase <dir> <name> <seconds>` appends a phase mark; `end` returns them as `phases: {name: seconds}`. The `done` recipe marks the preflight, each of static, format and typecheck, the reference step, the hooks suite and the test phase; the `test` recipe marks `pytest` and `floors` (merge, carry, the reports, save-baseline) inside it. Rendering: none.
- **D2** Every run of the gate's test phase writes this run's plan before pytest starts - the planner's, or, for a run that does not go through the planner (`make test-full` by hand, `INCREMENTAL=0`, `FULL=1`, T05's background refresh), its own with its reason - and the selection plugin writes its `result.json` (mode, reason, selected, collected) as today. `LOGRUN` reads only THIS run's result (stamped with the run's start, so an older file is never read) and adds `plan_mode`, `plan_reason`, `selected` and `collected`; the fields are left out only when no test phase ran (the gate stopped before it). Rendering: none.

<!-- plan-archive: archived 2026-10-24 -->
## T02 - a tooling change no longer runs everything (FR-001)

### T02 Approach (checklist part A)

1. **The goal, in the world.** A landing after a tooling change runs the tests its change reaches, plus the tests that read the changed tooling - not the whole suite.
2. **The constraints.** Never miss a test a change can break: the gate's machinery, the test run's configuration and the pinned lockfiles still plan `full`; the planner's other fallbacks are unchanged (spec FR-001).
3. **Where each comes from.** O: the GM's item 1; spec rounds 1-2 (the lockfiles ADDED; the word `scripts` read loosely; `gate-stamp.py` incremental).
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: the gate's planner asked offline on T26's baseline): T26's two engine files reached 143 of 11,890 baseline tests; the gate ran 10,376 because `scripts/` had moved the tooling hash.
5. **The order.** A planner hash of the gate's configuration beside the tooling hash; the `scripts/` readers; the plan; the tooling-test reuse on an incremental plan; tests.
6. **The exits.** (a) take `scripts/` out of `tooling_hash` - not taken: that hash decides when the tooling tests rerun, which stays; (b) a second hash for the planner - taken.
7. **The search smell.** None: one static scan of the test sources per plan.
8. **The budget.** 120 min with its landing.
9. **Done, measured.** SC-001's fixture cases (red without); `make test-file FILE=tests/tooling/ci/` green; T26's case re-asked of the planner plans incremental.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D3** `state.gate_config_hash(root)`: a content hash over `l7r/diagram/ci/`, `l7r/diagram/pipeline/`, `l7r/diagram/switches.py`, `l7r/diagram/_invocation.py`, `tests/conftest.py`, `tests/_scope.py`, the pinned lockfiles (`requirements.txt`, `requirements-dev.txt`, `requirements-ci.txt`), `pyproject.toml`'s `[tool.pytest*]` and `[tool.coverage*]` tables, and the Makefile's TEST CONFIGURATION - the recipes of `test` and `test-full` and every variable definition they reference, closed over the variables those reference, with each `##` help comment stripped. `incremental.manifest` records it as `gate_config` and the `scripts/` tree's blob ids as `scripts`; `plan` plans `full` when `gate_config` moved (a baseline without the key counts as moved, once) and no longer on `tooling` alone. Every non-lockfile path it names is already in today's `state.TOOLING_PATHS` (`l7r/diagram/ci`, `l7r/diagram/pipeline`, `l7r/diagram/switches.py`, `l7r/diagram/_invocation.py`, `tests/conftest.py`, `tests/_scope.py`, observed 2026-10-24, method: `state.py:172` read), so it adds no reason to run everything beyond the lockfiles the spec marks ADDED. Rendering: none.
- **D4** Where `scripts` moved and `gate_config` did not, the plan adds to its changed test modules every test module under `tests/tooling/` and `tests/hooks/`, and every other test module whose source - or the source of a module under `tests/` it imports, transitively - contains the substring `scripts` (spec FR-001 read loosely; a substring, so `tests._scripts` and `"scripts"` both match - spec round 3's aside), and carries `reuse_tooling: true`; `_test_deps.gate_full` becomes `gate_reuses`, true on a full plan or one carrying `reuse_tooling`, so the tooling tests whose recorded reads are unchanged are deselected as on a full plan, and `incremental carry` copies their baseline coverage in before the floors on such a plan too (the merge drops a selected test's old contexts, so without the carry a reused test's coverage would be lost). Rendering: none.

<!-- plan-archive: archived 2026-10-24 -->
## T03 - the landing waits only on what can refuse it (FR-003, FR-004)

### T03 Approach (checklist part A)

1. **The goal, in the world.** A landing returns once its work is on main, having waited only on the checks that can refuse it.
2. **The constraints.** The fixed seeds and pinned rows still refuse a regressed seed beside the gate; the fresh block's record still reaches `make cohort-seeds`; an uncovered added line still refuses the landing.
3. **Where each comes from.** O: the GM's items 3 and 4.
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: T26's landing log): the cohort finished 1.4 min after the gate; `cover-changed` took 48 s before the gate started.
5. **The order.** The cohort split (fixed beside the gate, fresh after the push); `cover-changed` beside the gate with a stop; the cohort gate's record shape.
6. **The exits.** (a) drop the fresh block - not taken, its trend is read; (b) after the push - taken.
7. **The search smell.** None.
8. **The budget.** 90 min with its landing.
9. **Done, measured.** Unit tests: the fresh block started after a push and not before; a failing `cover-changed` stops the gate and refuses; `cohort_gate.check` takes a landing record with no fresh block. A landing's log shows both.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** `make cohort-landing` rolls `N=48 FRESH=0` beside the gate; after a successful push, `land.py` starts `make cohort N=0 FRESH=48` detached (its own process group, its log under the git directory), one at a time (a lock file: a later landing's fresh block WAITS for the running one, never skipped), and the landing returns; its record is committed by the cohort as today and goes out with the next push. `cohort_gate.check` asks the landing record for the fixed seeds and pinned rows only (`landing_shaped(..., need_fresh=False)`). Rendering: none.
- **D6** `land.py` starts `cover_changed.py` beside `make done` (both in their own process groups); when it exits non-zero the gate's group is stopped (as `make land-stop` does) and the landing refused with its lines; `cheap_refusals` no longer runs it. Rendering: none.

<!-- plan-archive: archived 2026-10-24 -->
## T04 - the gate's costs, measured (FR-007)

### T04 Approach (checklist part A)

1. **The goal, in the world.** The cutoff and the refresh rule rest on what a gate run costs here, not on a guess.
2. **The constraints.** Real landings' records (T01's fields), at least three incremental and two full; the host's load at each end is recorded beside each (runstats), and a reading under heavy load is said so.
3. **Where each comes from.** O: the GM's item 6 ("first measure the fixed cost and the per-test cost on a few real landings").
4. **Do they describe the world here?** To be measured - this task is the measurement.
5. **The order.** Collect T01-T03's own landings' records and any other session's; fit seconds = fixed + per-test x selected for the test phase, the other phases read directly; and the merged baseline's drift: after the incremental runs, one full run's baseline compared with the merged one (contexts gained or lost).
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** 45 min, mostly waiting on landings.
9. **Done, measured.** `research.md` holds the table of runs, the fit, and the drift count, each figure labeled with its date and method.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Approach (re-answered 2026-10-24T17:08Z)

1. **The goal, in the world.** The cutoff and the refresh rule rest on what a gate run costs here, not on a guess.
2. **The constraints.** Real landings' records (T01's fields): at least three planned incremental and two full, with the host's load at each end recorded beside each (runstats) and a reading under heavy load said so. T01-T05's own landings change `ci/` and plan full; the incremental samples come from later landings, this session's or another's.
3. **Where each comes from.** O: the GM's item 6 ("first measure the fixed cost and the per-test cost on a few real landings").
4. **Do they describe the world here?** To be measured. Read 2026-10-24 (method: `incremental.py`'s docstring, spec D1 of feature 207): the baseline is the LAST FULL RUN, never a merged result - each incremental run selects everything changed since it, so the selection GROWS between full runs; that growth, not drift, is what a refresh resets.
5. **The order.** Collect the records; fit the test phase's seconds = fixed + per-test x selected; read the other phases directly; and measure the growth: the selected count of each incremental run against the number of landings since its baseline.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** 45 min, mostly waiting on landings.
9. **Done, measured.** `research.md` holds the table of runs, the fit and the growth, each figure labeled with its date and method.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D7** The measurement is `scripts/measure/gate_costs.py`, reading `dev/run-log/` (T01's fields): the table of runs, the least-squares fit of the test phase's seconds on the selected count, and the selection's growth since each run's baseline (the selected count against the landings since the last full run). Rendering: none.

<!-- plan-archive: archived 2026-10-24 -->
## T05 - a landing runs what its change reaches (FR-006)

### T05 Approach (checklist part A)

1. **The goal, in the world.** However much a change reaches, the landing runs that and no more; the baseline stays accurate without a landing paying for it.
2. **The constraints.** T04's numbers; one background refresh at a time; never on a landing's path; the gate outside a landing keeps today's fraction (spec US1 scenario 4 names landings).
3. **Where each comes from.** O: the GM's item 6; M: T04's fit and drift.
4. **Do they describe the world here?** Decided on T04's numbers (this block is re-answered then).
5. **The order.** The landing's gate passes `INCR_NO_CUTOFF=1`; the refresh rule from T04's drift; the refresh started after the push.
6. **The exits.** Decided with T04's numbers.
7. **The search smell.** None.
8. **The budget.** 90 min with its landing.
9. **Done, measured.** Unit tests: a landing plan over the fraction stays incremental; the refresh starts when the rule says, never twice at once; SC-004.
10. **Before moving a constant.** `FULL_FRACTION` stays for the gate outside landings; its dropping at landings rests on T04.
11. **Before fitting things into room.** n/a.

### T05 Approach (re-answered 2026-10-24T18:39Z)

1. **The goal, in the world.** However much a change reaches, the landing runs that and no more; the baseline stays accurate without a landing paying for it.
2. **The constraints.** R2's numbers; one background refresh at a time; never on a landing's path; the gate outside a landing keeps today's fraction (spec US1 scenario 4 names landings); the box's shared 10 GB memory cap (the refresh is a gate's worth of workers beside the session's own work).
3. **Where each comes from.** O: the GM's item 6; M: `research.md` R2 (67 s fixed + 12.7 ms per selected test; the selection 1,492 -> 2,657 over three runs since a full one).
4. **Do they describe the world here?** Yes, measured 2026-10-24 (`make gate-costs`, R2): a landing's incremental test phase costs at most about what a full one does (158 s at 60%, 188 s at 80%, 197 s full), so the cutoff saves a landing nothing; the growth is what costs, a landing paying for every change since the last full run.
5. **The order.** The landing's gate without the cutoff; the refresh after the push, in a detached worktree; its baseline copied into the clone, the coverage paths rewritten.
6. **The exits.** (a) refresh in the clone itself - not taken: the session's next edit moves the tree under it and voids the run, and its gate lock would hold the next landing; (b) refresh after every incremental landing - not taken: a full run each time spends ~200 s of the box for a selection of a few hundred tests; (c) the 25% rule in a worktree - taken.
7. **The search smell.** None.
8. **The budget.** 120 min with its landing.
9. **Done, measured.** Unit tests: a landing's plan over the fraction stays incremental; the refresh starts at 25% and not under it, never two at once; its baseline lands in the clone with the paths rewritten and not over a newer one. SC-004.
10. **Before moving a constant.** `FULL_FRACTION` stays for the gate outside landings; the landing passes `INCR_NO_CUTOFF=1`; the refresh's 25% is R2's.
11. **Before fitting things into room.** n/a.

### T05 part B (2026-10-24T19:08Z)

Owed by the round arbiter's ruling on red-gate@2026-10-24T19:05:23Z (continue).

1. **What exactly is refusing?** Two red landing gates, two causes in this feature's own tests: a T03 test started the real `cover_changed.py`, whose nested coverage run overwrote the gate's coverage data (817 failed); and three planner tests inherited `INCR_NO_CUTOFF=1`, which T05's landing exported to its whole gate (3 failed).
2. **A3 again.** O: the GM's item 6 and request amendment 1; nothing in the constraints moved.
3. **A4 again.** The decisions describe the world; the slips were in how the tests were isolated from the gate running them.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Changing: the flag becomes a make variable (`NO_CUTOFF=1`) the test recipe hands to the planner's call alone, never an environment the tests inherit; the T03 test starts a stand-in check; the planner tests clear the variable as a backstop.
6. **The one-sentence test.** "Why did the landing go red?" - its own new tests reached the gate that ran them.
7. **The next step is a measurement.** One `make land` for T05, the three planner tests green and nothing new failing (the ruling's "what").
8. **Every route measured?** n/a - no route is in question.
9. **After a ruling:** the arbiter's continue, recorded in `arbiter.jsonl`.

### T05 part B (2026-10-24T19:22Z)

Owed by the round arbiter's ruling on red-gate@2026-10-24T19:17:09Z (continue).

1. **What exactly is refusing?** The 18:59Z and 19:17Z gates share one cause, read correctly only the second time: T03 made `make land` run `cover_changed.py` beside the gate in the same tree, and its coverage data, with no `COVERAGE_FILE` of its own, landed where the gate's workers wrote theirs ("no such table: context"). T03 landed on the direct route, so the two first met at T05's gated landing. The 19:05Z gate's cause (the inherited `INCR_NO_CUTOFF`) was separate and is fixed.
2. **A3 again.** O: the GM's item 4 (FR-004) still puts `cover-changed` beside the gate; nothing in the constraints moved.
3. **A4 again.** The decision describes the world; the check and the gate needed separate coverage data.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Changing: `cover_changed.py` writes its coverage data in its own temporary directory (`COVERAGE_FILE`); and the arbiter's tooling fix - a delta touching `land.py`, `scripts/gates/`, the Makefile or `l7r/diagram/ci/` lands through a gate, never the direct route (`land.GATE_MACHINERY`).
6. **The one-sentence test.** "Why did the gate lose its coverage tables?" - the check beside it wrote its own coverage data into the same files.
7. **The next step is a measurement.** One `make land` for T05, counted green only on the ruling's three conditions: no INTERNALERROR and no failed test; the three planner tests green by name; `cover_changed.py` run beside the gate with real work, its data in its own directory, no stray `.coverage*` in the clone root after.
8. **Every route measured?** n/a.
9. **After a ruling:** the arbiter's continue and its tooling fix, recorded in `arbiter.jsonl`.

### T05 Decisions

- **D8** On R2's numbers (spec FR-006, amended): `make land`'s gate runs with `INCR_NO_CUTOFF=1`, which `incremental.plan` reads to skip the `FULL_FRACTION` check (the gate outside a landing keeps it). After a successful push whose gate ran incremental and selected at least `REFRESH_FRACTION` (0.25) of its baseline, `land.py` starts `scripts/gates/refresh_baseline.py` detached: under a lock, it adds a detached worktree at the pushed commit, runs `make done INCR_FORCE="refresh: <n> of <N> baseline tests selected"` there (a fresh worktree has no verification to short-circuit on), and when it is green copies the worktree's `gate-baseline/` into the clone's - each coverage file path rewritten from the worktree's root to the clone's - unless the clone's baseline was saved after the refresh started; it removes the worktree, and copies the run record into the clone's `dev/run-log/`, committed path by path. Rendering: none.

<!-- plan-archive: archived 2026-10-26 -->
## T06 - measured end to end (SC-006)

### T06 Approach (checklist part A)

1. **The goal, in the world.** The GM sees what a landing costs now, against T26's 8.8 minutes.
2. **The constraints.** A real engine landing after a tooling change, its phases from T01's record.
3. **Where each comes from.** O: the GM's item 1 ("the gate measured on the next real landing").
4. **Do they describe the world here?** To be measured.
5. **The order.** After T05.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** `research.md` holds the landing's table beside T26's.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T06 Decisions

- **D9** The landing measured is the first whose own change does not move `gate_config`, whose baseline already carries the `gate_config` key, and which has a `scripts/` change since its baseline - confirmed by `plan_mode: incremental` in its run record (405's next task where it meets this; T01-T05's own landings change `ci/` and run everything). Rendering: none.
<!-- plan-archive: archived 2026-10-26 -->
## T08 - a hook suite keeps the gate incremental

### T08 Approach (checklist part A)

1. **The goal, in the world.** A change to a `tests/hooks/*.sh` suite, which no pytest module runs, no longer makes a landing's
   gate run all ~10,000 tests, so T06 can be measured on a landing that carries one.
2. **The constraints.** The planner selects every test that can read a changed file; nothing it would catch today is missed.
3. **Where each comes from.** O: 405 T106/T138's two full-planned landing gates on 2026-10-25 (`tests/hooks/test-no-poll-hooks.sh`).
4. **Do they describe the world here?** Yes: feature 430 T02 (landed 7d1ced680, 2026-10-26) made a non-module file below
   `tests/<dir>/` select its readers (`incremental.tree_file_readers`) instead of planning full; a hook suite is one.
5. **The order.** After 430 T02; before T07.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 15 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** `test_a_hook_suite_keeps_the_gate_incremental` plans incremental on today's planner and fails on the
   planner before 7d1ced680.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T08 Decisions

- **D10** No planner change of this feature's own: 430 T02's reader rule already covers the hooks tree, so T08 adds the test that
  pins the case it was filed for. Rendering: none.

