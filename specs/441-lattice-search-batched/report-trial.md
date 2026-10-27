# Trial 441 - the web's lattice search: what it found, and what it cost (with feature 440, the tooling it used)

For the GM, laid out as trials 437 and 439 were. Wall clock UTC from commit times, the review agents' reported durations and the
runs' own clocks; `make feature-report F=440` / `F=441` for the split. A WAIT is time spent on a review, a gate or a roll.

## What it found

- The web's router (`route.lattice_search`) is 22% of the web stage under cProfile, but unprofiled it is 0.19 s - 2.7% of the
  40-household roll. Its batched form is a design already withdrawn (feature 278), and A* toward the goal another (feature
  284). Stopped at the measurement: its ceiling is under the quick form's 4% floor (`research/ceilings.md`).
- None of the five searches trial 439 named reaches the floor alone: their ceilings are 2.8%, 2.7%, 1.6%, 1.2% and 1.0% of the
  roll - about 9% together, with overlaps.
- With trials 437 (the shared geometry: 3.5%) and 439 (the seat envelopes: 10.6% for a perfect screen, and its one spike cost
  the roll 17%), the reading is now three trials deep: the roll's time is spread across many stages and hundreds of loops, and
  no one search or layer holds enough of it for an order of magnitude. The candidates for one are now kinds of change that act
  on all the Python at once - a faster interpreter or compiled hot paths, rolls run in parallel - or a redesign of how the
  seating and the web search, measured on the whole roll as 439 learned. Those are the GM's to choose among.

## What it cost

### Feature 440 - the five tooling improvements (22:48:37 to 23:42:20, 54 min)

`make feature-report F=440`: tools 28 min (two landings' gates), thinking 22 min, spec reviews 6 min waited, quick tests 1 min.

| # | step | start | end | took | kind |
|---|---|---|---|---|---|
| 1 | claim, request, spec | 22:48:37 | 22:49:14 | 37 s | work |
| 2 | spec review, round 1 (CHANGES REQUIRED, 4 items) | ~22:49 | ~22:55 | 327 s | WAIT (overlapped: improvements 1-5 begun) |
| 3 | the five built and tested; the calibration measured (one false start: a script without its `__main__` guard, ~2 min) | ~22:50 | 23:06:21 | ~16 min | work, WAIT ~4 min for the timed suites |
| 4 | spec review, round 2 (CHANGES REQUIRED, 3 items); applied; the round cap to the round arbiter (accept) | 23:06:53 | 23:11:45 | 215 s + 36 s | WAIT, work ~1 min |
| 5 | plan review (BLOCKED: the bundle cut FR-006 from a cited range); fixed, the bundler's range bug fixed; round 2 (CLEAR) | ~23:07 | 23:18:38 | 285 s + 77 s | WAIT (overlapped), work ~3 min |
| 6 | the task's preflight (CLEAR), quick, coverage, hook tests, the claims round | 23:18:38 | 23:24:29 | ~6 min | work, WAIT ~2 min (hooks-test) |
| 7 | landing 1: the gate and cohort green, then the merge refused - its feature-complete check did not read the arbiter's accept | 23:24:31 | 23:34:47 | ~10 min | WAIT, wasted |
| 8 | that check fixed and tested; landing 2 | 23:34:47 | 23:42:20 | 345 s + ~2 min | WAIT, work ~2 min |

Work about 25 min, waits about 29 min - 10 of them the landing a check's bug refused at its end.

### Trial 441 (23:42:53 to 23:54, about 11 min)

`make feature-report F=441`: the review 5 min waited, thinking 2 min.

| # | step | start | end | took | kind |
|---|---|---|---|---|---|
| 1 | the clone's sync behind the landing's render-sync, then `make trial ... APPROVED=` (the approval line written; its first commit passed) | 23:42:53 | 23:46:02 | 3.2 min | WAIT ~3 min |
| 2 | measured: `make perf-share` on the kept web profile (under a second), the call tree, the code, the five ceilings | 23:46:02 | ~23:47:20 | ~1.3 min | work |
| 3 | the brief and the evidence; the verdict by its branch | ~23:47:20 | 23:47:41 | ~20 s | work |
| 4 | the one review (FAITHFUL, first round) | ~23:48 | ~23:53:40 | 339 s | WAIT |
| 5 | this report | 23:53:40 | 23:54 | <1 min | work |

Work about 2.5 min, waits about 8.5 min. Against trial 439 (19 min; a review round lost to a verdict that misread its own rule)
and 437 (17 min; three spec rounds before the evidence was fixed), the trial form now took one review, first time, and the
tools 440 added did their part: the approval line on the first commit, the ceiling read in seconds from kept profiles.

## What the times point at

| step | improvement, and what it would save |
|---|---|
| 440 #7 (10 min) | Two gates read one verdict two ways: the review gate took the arbiter's asked accept, the merge's feature-complete check did not - fixed in 440 (`ci/features.spec_accepted` reads it now). The general fix is one reader for "does this spec carry its verdict" that every gate imports, so the next such reading cannot drift; about 10 min each time two readings disagree. |
| 441 #1 (3 min) | `sync-with-main.sh sync-in` waits behind the landing's own background render-sync; a sync that only needs the mirror could skip waiting on render-sync's lock when nothing on main has moved. About 3 min after each landing. |
| 440 #2, #4, #5 (reviews ~15 min of reviewer time, ~6 waited) | Three of the ten review findings were knock-ons of an earlier round's fix (a criterion left behind when its requirement was rewritten); a spec-lint check that each rewritten requirement's criterion was touched in the same edit would catch them before the round. About one round (4 min) a feature. |
| 440 #3 (the false start) | None worth building: a measurement script's guard, written once. |
| 441 #4 (339 s) | The review of a trial whose verdict is "stopped at the measurement" read every profile again to re-derive the figures; for a measurement-only trial the bundle could carry the commands' outputs so the reviewer checks them rather than re-runs them. About 3 min a trial. |
