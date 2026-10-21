# Plan - feature 405: the engine and record findings moved from 385

Spec: [`spec.md`](spec.md). Tasks: [`tasks.md`](tasks.md). One section per task, written at its start; the approach checklist
is `docs/approach-checklist.md`.

**Lands open**: T01, T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T151, T152, T153, T154

## T12 - `_trim_to_service` walks every end in, never pops a whole segment (385 T126)

### T12 Approach (checklist part A)

1. **The goal, in the world.** A lane that runs on past what it serves ends where it last serves something, not a whole segment short of it: the stretch of its last segment that still comes within reach of a house, a way, the bund or a steading stays drawn.
2. **The constraints.** 0246's drawing page: "a lane end that reaches nothing is pulled back to the last house it serves", with the 60 ft reach to a house or way and 12 ft to a steading's built ground (`WAY_END_REACH_FT`, `end_serves`). `_trim_to_service`'s own claim: "ends trimmed to what serves, 4 ft at a time". The law gate (`lanes_reach_something`) asks the same bar of every end. The gate and the landing cohort.
3. **Where each comes from.** The pull-back to the last house served: R (0246 drawing page, its "Lane ends" section); the 60 ft and 12 ft: R, labeled GUESS on that page; the 4 ft grain: O (the walk's step, `_trim_to_service`).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (a read of `ways/geom.py:546-563`): the first two loops pop a whole vertex while the end does not serve, so on a run whose last segment is long and whose inner part passes within 60 ft of a house, the end jumps back to the previous vertex, past the last point that served; the 4 ft walk below, which does stop at that point, runs only after the pops; the impl-drift round on that task in 385 recorded it DRIFTED.
5. **The order.** The two pop loops removed, so the 4 ft walk (which already drops a vertex once the end is within 4 ft of it) is the one pull-back for every end; the claim's line unchanged; a unit test red without it; the cohort; the claims round on the changed unit; the gate and the landing cohort.
6. **The exits.** (e) conform - the research says pull back to the last house served, and the walk already does; (a) a coarser step to save time was weighed and refused until the cohort shows a cost (the walk is per 4 ft per end, run per lane).
7. **The search smell.** None.
8. **The budget.** 45 min with the landing.
9. **Done, measured.** One goal: `_trim_to_service` on a run whose long last segment passes a house within 60 ft partway ends on that segment within 4 ft of its last serving point (a test red at HEAD); the claims round reads the claim IN-STEP; the gate green and the landing cohort refusing no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T12 Decisions

**D1 - one walk for every end.** `ways/geom.py::_trim_to_service` loses its two vertex-popping loops (`while len(out) > 2 and not serves(...)`); the existing two-pass 4 ft walk pulls each end in along its own last segment, popping a vertex only when the end is within 4 ft of it, so every end stops within 4 ft of the last point that serves. The comment above the walk says so (it no longer explains a two-point-arm special case). The claim "pulled back to the last house served ... 4 ft at a time" stands as it is.

### T12 part B (2026-10-20T12:36Z)

Owed by the round arbiter's ruling on hour:405-engine-findings-from-385@1 (continue), taken while T12 was the active task.

1. **What is refusing?** Nothing in the code: the test, the ways package, the cohort, the gate and the landing cohort were green. The landing refused three times on its route (land-batch takes two tasks or more; the push wants a green gate first; the open tasks wanted a reviewed Lands open line), then on undeclared occasions and the landing cohort.
2. **A3 again.** Unchanged: 0246's pull-back (R), the 4 ft step (O).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "A lane end stops where it last serves, not a segment short" - true by the test and both claims IN-STEP.
7. **The next step is a measurement.** The tick, then `make where-time` for the GM.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - finish T12, then report the breakdown; the ruling's question for the GM goes in the report.


<!-- plan-archive: T30 to T12 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T31 to T12 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
## T32 - only the task being worked holds a landing (the GM, 2026-10-20)

### T32 Approach (checklist part A)

1. **The goal, in the world.** A feature worked one task at a time lands each task when it is done; tasks nobody has started hold nothing, and no line or mark has to be written or reviewed for it.
2. **The constraints.** The GM, 2026-10-20: "I do not want each landing to owe a lands open line ... because that's going to slow things down." Mid-task work stays in the clone (feature 330: "mid-task work is sacred"). The GM-review box is a review after landing. A test red without it.
3. **Where each comes from.** The GM (G); 330 (O); 375 D12 (O).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (T12's landing: refused "feature in progress" on 30 tasks nobody had started; the Lands open line and its review cost ~4 min with the step-back it met).
5. **The order.** `speckit-todo.holding` rewritten; the push's message; the retired pieces (the `**Lands open**:` line read, the tick's "mark the tooling did not put" refusal, task-add's line and mark); the docs at the point of change; the tests.
6. **The exits.** (c) - the active task decides; keeping the line without its review was weighed and refused (the GM: no line at all).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: a push of a feature with open tasks is held only while the clone's active task (`make task-start`) of that feature is open and not named by the landing (`L7R_LAND_TICKS`, set by `make land`); `tests/tooling/` and `tests/hooks/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T32 Decisions

**D4 - the active task holds, nothing else.** `speckit-todo.holding(d)` returns the open box of the clone's active task (`plan_gate.active_task`) when it is this feature's and its id is not in `L7R_LAND_TICKS` (space-separated ids `make land` sets after the task's tick checks pass); no other open box holds - the GM-review box, a carried task and an unstarted task alike. The `**Lands open**:` line is no longer read and task-add no longer writes it or a `[lands-open]` mark; the tick's refusal of a "mark the tooling did not put here" goes with it (no mark is honored or refused - it is text). The push's refusal names the active task and the command that lands it (`make land F=<n> T=<id>`).

### T32 part B (2026-10-20T14:05Z)

Owed by the round arbiter's ruling on hour:405-engine-findings-from-385@2 (continue), taken while T32 was the active task.

1. **What is refusing?** Nothing in the code: tests/tooling (2076), the push suite and hooks-test green. `make land` refused on the hour's step-back, once per task (now printed once).
2. **A3 again.** Unchanged: the GM's "no Lands open line" (G).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: D4 as reviewed, plus a box nested under the active task holding (feature 330's indented rule kept).
6. **The one-sentence test.** "Only the task being worked holds a landing" - true by the suites.
7. **The next step is a measurement.** `make land` on T30-T35.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - land T30-T35 with make land; the repeated line is tidied.

<!-- plan-archive: T33 to T33 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T34 to T34 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T35 to T35 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->

## T14 - `_sweep_dangling_ends` walks every end in, never pops a whole segment (385 T128)

### T14 Approach (checklist part A)

1. **The goal, in the world.** A lane end the finishing sweep pulls back stops where it last serves something - a way, a farmhouse, the bund or a steading - not a whole segment short of it; and a stretch that reaches only the way its own other end stands on is not counted as serving, so the walk leaves no new tail off that way.
2. **The constraints.** 0246's drawing page: a lane end that reaches nothing is pulled back to the last house it serves, with the 60 ft reach to a house or way and 12 ft to a steading's built ground (`end_serves`). The 269 E4 hold: a pull-back stops at another lane's end resting on this one. The house clause (no farmhouse loses its way; the dooryard carry). The law gate (`lanes_reach_something`). The gate and the landing cohort.
3. **Where each comes from.** The pull-back to the last house served: R (0246 drawing page); the 60 ft and 12 ft: R, labeled GUESS on that page; the 4 ft grain: O (the walk's step, as `_trim_to_service`'s since T12); the hold: O (269 E4); the other end's way not counted: O (feature 261, `_trim_to_service`'s `serves`).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (a read of `ways/sweeps.py:703-714`): both loops pop a whole vertex while the end does not serve, so an end whose last segment passes within reach partway lands on the vertex before it, past the last point that served; 385's impl-drift round on T106 recorded it DRIFTED. A walk alone would keep a link whose head stands on a way and whose tail reaches only that same way, as a stub (measured 2026-10-20 (a trace of `end_serves` on the sweep's first unit test: its third lane, emptied at HEAD, kept at 57 ft)); the pop emptied it. `_trim_to_service` answers that case by not counting the way the run's other end stands on.
5. **The order.** The two pop loops replaced by a 4 ft walk that consults the hold before each step; the end's reach asked without the ways the lane's other end stands on; the docstring and claims say both; the unit tests updated in the same edit with a red case for each; the cohort; the claims round on the changed unit; `make land`.
6. **The exits.** (e) conform - the research says pull back to the last house served; (a) a coarser step to save time was weighed and refused until the cohort shows a cost (the walk is per 4 ft per end, run once per lane at the end of the web).
7. **The search smell.** None.
8. **The budget.** 30 min with the landing.
9. **Done, measured.** One goal: `_sweep_dangling_ends` on a lane whose long last segment passes a house within 60 ft partway ends on that segment within 4 ft of its last serving point (a test red at HEAD), and a link standing on a way with nothing at its far end is emptied (a test); the claims round reads the unit's claims IN-STEP; the gate green and the landing cohort refusing no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T14 Decisions

**D8 - the sweep walks its ends in.** `ways/sweeps.py::_sweep_dangling_ends` loses its two vertex-popping loops; each end is walked in along its own last segment 4 ft at a time, a vertex dropped only once the end is within 4 ft of it, and the 269 E4 hold still asked before each step (an end whose segment carries another lane's end stops there, as now). The docstring's "gives up its last vertex" becomes the walk, and the claim "lane end reaches something" names the 4 ft grain.

**D9 - the other end's way does not count.** The end's reach is asked of the other lanes' segments less those within `_TOUCH_GAP` of the lane's OTHER end, as `_trim_to_service`'s `serves` does (feature 261), so a link off a way with nothing at its far end is pulled back to nothing and emptied, as the pop did. Claimed on the unit (`GUESS` on 0246, which is silent on a way's own start).

### T14 part B (2026-10-21T03:29Z)

Owed by the round arbiter's ruling on hour:405-engine-findings-from-385@3 (continue), taken while T14 was the active task.

1. **What is refusing?** Nothing in the code: the ways suite (574) and the cohort (16/16) green. The claims round found the unit's rules claimed short (two MISLABELED, three UNCLAIMED); claims added, re-checked.
2. **A3 again.** Unchanged: 0246's pull-back (R), the 4 ft step (O), the hold (R, 0246's one network), the way left not counted (a GUESS reading of 0246, feature 261).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: D8 and D9 as reviewed; claims only.
6. **The one-sentence test.** "A swept lane end stops where it last serves, not a segment short" - true by the tests.
7. **The next step is a measurement.** The claims round, then `make land`.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - the claims round, then `make land`, then T14's breakdown for the GM.

## T36 - the claims gate refuses only what the change made (A)

### T36 Approach (checklist part A)

1. **The goal, in the world.** A task that touches a function lands once its own claims are right; a finding on that function's older code is filed as a task of the feature, as the GM's found-work rule asks, instead of refusing the landing.
2. **The constraints.** The GM, 2026-10-19: "we should keep findings on code a task didn't change as new tasks in 385" (carried to 405 as its FR-002). The claims gate's FR-010 (a finding the delta introduced refuses). 385 FR-013's carry (`claims_carry`), which already files a page edit's findings on unchanged code. impl-drift judges; the gate only counts.
3. **Where each comes from.** The found-work rule: G. FR-010 and FR-013: O (features 316, 385).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14's claims round, `landing-analysis-2.md`): three findings on code T14 never changed (the dooryard carry's fallback, the restore-whole rule, the grove band) were refused as introduced because the unit's code changed, and cost a third impl-drift round.
5. **The order.** The bundle marks changed lines; the MANIFEST says when to tag; the reply parser and the index keep the tag; `classify` carries a tagged finding whose claim is unchanged from the base (or an UNCLAIMED one); `make land` runs the carry in its first pass; tests for each.
6. **The exits.** (c) - the agent says which findings rest on the change, because only it reads what a finding rests on; a mechanical rule by claim text was weighed and refused (a code change can make an unchanged claim false, which is the gate's whole job).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: a reply whose DRIFTED and UNCLAIMED findings on an unchanged claim carry `[outside the change]` leaves the claims gate with carried findings, not introduced ones, and `make land` files them as one open task; an untagged one, or a tagged one on a claim the delta reworded, is still introduced (tests).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T36 Decisions

**D10 - the agent tags, the gate carries.** `claims.bundle` shows each unit's source with the lines the delta changed (against the merge base with origin/main) marked `+`, and the MANIFEST asks that a non-IN-STEP verdict or UNCLAIMED line resting on no marked line, and not on a claim the delta added or reworded, begin its note `[outside the change]`. `record` keeps `outside: true` on the row. `classify` carries such a row when it is UNCLAIMED or its claim text matches the merge base's row; otherwise it is classified as before. `land.py`'s first pass runs `claims.py carry --feature <n>` before the claims gate and commits what it files.

## T37 - a new unit with only the inherited NONE is named first (B)

### T37 Approach (checklist part A)

1. **The goal, in the world.** A new helper that decides something about the place gets its own claim before the first check, so the check does not spend a round saying so.
2. **The constraints.** Feature 316's claims grammar: a unit with no `Research:` line inherits its module's; a `NONE` claim says the unit decides nothing physical.
3. **Where each comes from.** O (feature 316).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14's first impl-drift round): `_walk_in`, new, inherited `lane sweep plumbing - NONE` and was judged MISLABELED with two UNCLAIMED decisions.
5. **The order.** The notice in `claims.py owed` (and the bundle command), a test.
6. **The exits.** (b) - a notice, not a refusal: a new helper may truly be plumbing, and a refusal on correct work teaches bypassing.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: `make claims-owed` on a delta adding a function whose only claim is inherited `NONE` prints a line naming it and what to write (a test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T37 Decisions

**D11 - named, not refused.** `claims.py owed` (behind `make claims-owed` and `make claims-bundle OWED=1`) prints, for each owed key whose status is `new`, whose unit is `inherited` and whose claim is `NONE`: "<uid> is new and carries only its module's NONE - if it decides anything about the place, give it its own `Research:` line before the check".

## T38 - the step-back clock keeps the wait on the GM (C)

### T38 Approach (checklist part A)

1. **The goal, in the world.** The hourly step-back comes due after an hour of the session's work, never because the session waited overnight for the GM.
2. **The constraints.** 383's hour (`CHECKPOINT_S`); 385's GM-wait rule (a Stop to the GM's next prompt is not the session's time); 397's idle rule.
3. **Where each comes from.** O (features 383, 385, 397).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of 405's event log, rows 662-671): after the Stop at 14:11Z two `SubagentStop` events (14:14Z, 15:05Z) reset the GM wait, so the 12 hours to the GM's prompt counted as idle gaps, each charged its first 20 min, and the hour came due after about 17 minutes of work.
5. **The order.** `gm_waits` and `idle` hold a Stop through `SubagentStop`; a test built on that event sequence, red before.
6. **The exits.** (e) conform - the rule already says a wait on the GM is not the session's time.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: the event sequence Stop, SubagentStop, SubagentStop, the GM's prompt counts as one GM wait and no idle gap, and the hour does not come due on it (a test red at HEAD).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T38 Decisions

**D12 - only the session's own act ends a wait.** In `checkpoint.gm_waits` a `SubagentStop` no longer clears an open Stop (a `PreToolUse` or a non-GM prompt still does); in `checkpoint.idle` a gap after a Stop stays the wait's through `SubagentStop`, so the same span is never counted as both.

## T39 - a claims-bundle pass is traced to the active task's feature (D)

### T39 Approach (checklist part A)

1. **The goal, in the world.** A claims round's agent passes get their ledger rows from the landing's own write, with no prompt wording needed.
2. **The constraints.** 371's ledger rows (every pass has one); 395's rule that a feature's write takes only passes traced to it.
3. **Where each comes from.** O (features 371, 395).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14's landing): `make land` refused once on three impl-drift passes whose prompts named only `/tmp/l7r-check/claims-owed/`, which `belongs` could not trace to 405.
5. **The order.** `belongs` traces a subject naming a claims bundle (`claims-owed`, `claims-triage`) to the clone's active task's feature; a test.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: with 405's task active, a pass whose subject names `/tmp/l7r-check/claims-owed/MANIFEST.md` belongs to 405 and not to another feature (a test red at HEAD).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T39 Decisions

**D13 - the active task owns the claims bundles.** `ledger_owed.belongs(p, num, ...)` is also true when the subject names `l7r-check/claims-owed` or `l7r-check/claims-triage` and the repository's active task (`plan_gate.active_task`) is feature `num`'s.

## T40 - the preflight judges a changed function's every line (F)

### T40 Approach (checklist part A)

1. **The goal, in the world.** A coverage gap the gate's 100% floor will refuse is found in the preflight's two minutes, not after the gate's five.
2. **The constraints.** The 100% floor (feature 174); the preflight's coverage step (375 FR-004), which today asks only the changed lines and, on the hamlet path, defers to the gate's rolls.
3. **Where each comes from.** O (features 174, 375).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14's first landing and the gate baseline's `coverage.db`): `sweeps.py:738`, unchanged, lost its only unit test when T14 reworked it; the preflight passed, the gate failed 5.7 min in, and the baseline shows only `test_sweeps.py` tests ever reached that line, no roll.
5. **The order.** `changed_lines` widened to each changed function's span; for an on-path gap, the line mapped to the baseline's copy of the file (its blob in the baseline manifest) and the baseline's contexts read: reached there only by tests the quick tier runs (or by none) - the preflight refuses it; tests.
6. **The exits.** (c) - the baseline is the last green gate's evidence of what the rolls reach; a line the delta changed has no baseline line and keeps today's rule (the gate judges).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: a fixture where an unchanged line inside a changed function is uncovered by the quick run and reached at the baseline only by a quick-tier test makes the preflight refuse it; the same line reached at the baseline by a gate-tier test is only printed (tests).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T40 Decisions

**D14 - a changed function, and the baseline's word on the rest.** `preflight.changed_lines` returns, for each changed engine file, the changed lines plus every line of each function or method enclosing one (by `ast` spans). In `coverage_step`, an on-path gap whose line maps (`difflib`, equal blocks) to a line of the baseline's copy of the file is refused when the baseline's `coverage.db` holds no context for that line from a test outside the quick run (a test id under `tests/gate`, `tests/full`, `tests/tier_*`, `tests/tooling`, a test the quick run did not run, or a fixture context); with no baseline, today's rule.

## T41 - the gate runs beside the claims round (E)

### T41 Approach (checklist part A)

1. **The goal, in the world.** The gate and the landing cohort can start as soon as the code is final and run while the claims round settles the claims, so the landing waits for whichever is longer, not for both.
2. **The constraints.** The gate's tree check (375 FR-004: a run that saw half of one change vouches for neither); the gate-write guard (385 FR-010); the stamp's semantic id (features 133, 385 T57: a docstring or comment edit is not a change the gate exercised; the `page` and `browser` areas hash bytes).
3. **Where each comes from.** O (features 133, 375, 385).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (T14): the claims round's edits were docstring claims and records, none of which the gate exercises, yet the guard refused the records and the docstring edits voided a running gate (5 min of machine time, killed).
5. **The order.** One predicate, "a move the gate does not see": a `.py` change whose semantic id is unchanged and that is in no byte-hashed area, or a path among the claims round's records; the tree check passes such moves (HEAD may move by commits holding only them); the gate-write guard passes the claims round's targets and a commit, add, Edit or Write whose changes are all such moves; tests.
6. **The exits.** (c) - the stamp's own semantic id decides, so the gate's tree check and its stamp cannot disagree; widening to any file was weighed and refused.
7. **The search smell.** None.
8. **The budget.** 60 min.
9. **Done, measured.** One goal: with a gate of this tree running, `make claims-checked`, a commit of a docstring-only engine edit with the claims index, and an Edit of a claim docstring pass the guard, and the tree check reads that run as unmoved; a code-token edit, or a record outside the list, still refuses and still voids it (tests).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T41 Decisions

**D15 - a move the gate does not see.** `preflight.unseen(root, path, old, new)`: a `.py` file outside the `page`/`browser` areas whose `gate-stamp.semantic_bytes` are equal, or a path in the claims round's records (`dev/claims-index.json`, `dev/claims-pages.json`, `dev/review-ledger.md`, and the ACTIVE feature's `found.jsonl`, `arbiter.jsonl`, `claims-carried.jsonl` and `tasks.md` - the last the claims carry's box (385 FR-013); no feature's `plan.md`, which the gate's spec-lint reads). The tree snapshot keeps every differing file's blob; the check compares the before and after trees across a HEAD move and calls the run moved only when a path that differs is not unseen. The gate-write guard lets `make claims-checked`, `claims-triaged` and `append` through, and a `git add`/`git commit`, Edit or Write when every resulting change is unseen (an Edit's result is computed from its old and new strings).

### T36 part B (2026-10-21T04:41Z)

Owed by the round arbiter's ruling on hour:405-engine-findings-from-385@4 (continue), taken while T36 was the active task.

1. **What is refusing?** Nothing in the code: tests/tooling (2085) and hooks-test green. `make land` refused once, on the hour's step-back.
2. **A3 again.** Unchanged: the found-work rule (G), FR-010 and FR-013 (O).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: D10-D15 as reviewed.
6. **The one-sentence test.** "A finding outside the change is filed, not refused" - true by the tests.
7. **The next step is a measurement.** `make land` on T36-T41, then T11 measured against T14.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - land T36-T41, then T11; WEB_REACH_FT's source asked first.
