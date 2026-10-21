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

<!-- plan-archive: T36 to T36 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T37 to T37 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T38 to T38 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T39 to T39 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T40 to T40 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T41 to T41 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
## T11 - a web lane's span has no whole-cluster fallback (385 T124)

### T11 Approach (checklist part A)

1. **The goal, in the world.** A web lane runs along the houses it serves and a little past them; no code path lays one along the whole cluster serving none.
2. **The constraints.** 0246's drawing page: a lane runs along the houses it serves, those within 100 ft of its cut (`WEB_REACH_FT`, the page's own GUESS); a stretch joining nothing is not drawn. `web_cuts` (`settlement/_knobs.py`), which places each cut. The gate and the landing cohort.
3. **Where each comes from.** The span along the served houses and the 100 ft: R (0246, the figure a GUESS on that page); the 30 ft pad: R (0246's GUESS "about 30 ft"); `web_cuts`' placement: O.
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of `ways/web.py:504-506` and `settlement/_knobs.py:438-453`): `_extent` falls back to every house when none stands within reach of the cut, but `web_cuts` places every cut either at a gap midpoint at most `reach` past the house that called for it or `reach * 0.5` past it, and both callers pass the same coordinates and the same reach, so that house is always within reach and the fallback never runs; the claim's DRIFTED (385 T106's round) is against code no map executes.
5. **The order.** The fallback removed, the invariant said at the point of change; a unit test that every cut `web_cuts` makes has a house within its reach, and that each cut line spans only those houses plus the pad; the cohort; the claims round on the changed unit; `make land`.
6. **The exits.** (e) conform - the research says a lane spans the houses it serves; the code already does wherever it runs.
7. **The search smell.** None.
8. **The budget.** 20 min with the landing.
9. **Done, measured.** One goal: `_web_cut_lines` holds no whole-cluster fallback, and a test over many coordinate sets finds every cut within reach of a house and every line within the pad of the houses near its cut; the claims round reads the unit's claims IN-STEP; the gate green and the landing cohort refusing no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T11 Decisions

**D16 - no fallback, the invariant named.** `ways/web.py::_web_cut_lines._extent` reads the houses within `WEB_REACH_FT` of the cut and nothing else (the `or along` fallback removed); the comment above it says why none can be missing (`web_cuts` places every cut within reach of the house that called for it). No map changes, since the fallback never ran.

<!-- plan-archive: T42 to T11 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

<!-- plan-archive: T43 to T43 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
## T19 - `law.fouls_fabric` retired: no caller, the live rule is `fouled_segment` (385 T135)

### T19 Approach (checklist part A)

1. **The goal, in the world.** No lane's tread lies on or within 7 ft of another household's yard or garden, and an own way keeps off its own beds (0246 §16); the code that holds it is the code that runs.
2. **The constraints.** 0246's drawing page (no tread on another household's yard or bed; 7 ft off another's garden; its way leaves its dooryard round its own beds and fixtures); `settle.fouled_segment` and `theirs`, the web's foul test; the overlap matrix (`forbidden_segment`), which forbids a lane on any yard or garden, its own household's too.
3. **Where each comes from.** R (0246) and O (features 287, 385).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a grep of `l7r/`, `pool/`, `scripts/`): `law.fouls_fabric` has no caller; its only reader is its own unit test. The `LAW` registry's docstring says it is reached through `breaks_mid_run`, which calls only `breaks_through`. So the finding (an `own` caller dropping its own garden) is against code no map executes; the live test, `fouled_segment`, exempts a steading at a lane's end from the fence clearance (`theirs`) but still refuses a tread on its own beds through the matrix ("its own household's too").
5. **The order.** `fouls_fabric` and its test removed; the three docstrings that name it (`LAW`'s, `fouled_segment`'s, `fabric.house_hit`'s) brought to what runs; the claims round on the changed units; `make land`.
6. **The exits.** (e) conform - the research is held by the code that runs; the dead copy that drifted is removed rather than mended.
7. **The search smell.** None.
8. **The budget.** 20 min with the landing.
9. **Done, measured.** One goal: `fouls_fabric` is gone from the engine and the tests, nothing names it as live, `make done` is green (no coverage lost on live code) and the claims round reads the changed units IN-STEP; no map changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T19 Decisions

**D20 - the dead copy retired.** `ways/law.py::fouls_fabric` and `test_a_lane_fouls_a_house_or_a_neighbors_plot_but_not_its_own` are deleted; its three claims leave the index with it (the same rules are claimed at `settle.fouled_segment` and `settle.theirs`). The `LAW` docstring names `deck_seats` alone as asked of one candidate way; `fouled_segment`'s docstring names `theirs` for the yard and garden test; `house_hit`'s names `fouled_segment` as the web's reader. No map changes.

<!-- plan-archive: T48 to T48 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

## T13 - a street's dangling end is cut no further than the last farm it serves (385 T127)

### T13 Approach (checklist part A)

1. **The goal, in the world.** A row's street runs on to the last farm it serves, a farm with no door path of its own included; only the stretch past every farm and every joint is cut away.
2. **The constraints.** 0246's drawing page (a street pulled back to the last house it serves; an end reaching nothing is pulled back); `street.trim_streets`, which already keeps a street to each served farm's point (`serve.street_anchors`, feature 385 T97, D125); `settle_street_ends`, the settle's repair of a street end the lane law calls dangling.
3. **Where each comes from.** R (0246, the pull-back a GUESS on that page) and O (features 291, 293, 385).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of `settle.py` and `web.py`): the web's trim passes `street_anchors(s)` as joints, but `settle_street_ends` cuts a dangling street end back to other lanes' ends alone, so a farm the street reaches without a door path, beyond the last such end, is cut off its street (impl-drift DRIFTED, 385 T106's round).
5. **The order.** `settle_street_ends` counts each `street_anchors` point as a joint beside the other lanes' ends, as the trim does; a unit test of a street whose last served farm stands past its last lane joint; the gate and the landing cohort beside it; the claims round; `make land`.
6. **The exits.** (e) conform - the research says pull back to the last house served; the trim already does.
7. **The search smell.** None.
8. **The budget.** 25 min with the landing.
9. **Done, measured.** One goal: a dangling street end is cut to the outermost of its lane joints and its served farms' points (test); the claims round reads `settle_street_ends` IN-STEP; the gate green and the landing cohort refusing no seed against main.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T13 Decisions

**D22 - the settle anchors as the trim does.** `settle.settle_street_ends` passes `serve.street_anchors(s)` with the other lanes' ends to `street.end_to_its_joint` (each anchor stands on its own street, within the touch), so a dangling end is cut back no further than the last farm the street serves; its claim names the anchors.

<!-- plan-archive: T50 to T50 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T51 to T51 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T47 to T47 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

<!-- plan-archive: T49 to T13 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

<!-- plan-archive: T52 to T49 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

<!-- plan-archive: T53 to T53 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->

## T17, T16, T27 - the lane-end, run-on and farm-fixture claims brought to the research (385 T133, T131, T147)

### T17 Approach (checklist part A)

1. **The goal, in the world.** Every claim on the lane-end rules says what the code does and labels it as 0246 does.
2. **The constraints.** 0246's drawing page, read 2026-10-21: "a lane end that reaches nothing is pulled back to the last house it serves. No page we read says how far a lane ran past its last house, so the rule is a GUESS"; an end reaches a farmhouse within 60 ft (or 12 ft of its built ground) and another way within 60 ft; back lanes bring every farmhouse within 100 ft of one. 0014 sets the field's join.
3. **Where each comes from.** R (0246, 0014).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (a read of each site): `_pull_back`'s comment says the walk "ends the lane at the homestead"; `WAY_END_REACH_FT`'s docstring names the field among its 60 ft reaches (the field's is `law.FIELD_REACH_FT`, T22's); `_lay_skeleton`'s claim floors the span "at one bundle pitch (100 ft) each way" where the code floors each half-extent at half a pitch (50 ft); `sweeps._SERVE_FT`'s 100 ft claims no page though 0246 gives it; thirteen claims state the pull-back plainly where the page calls it a GUESS.
5. **The order.** Each wording put right where it stands; the thirteen pull-back claims labeled GUESS; the claims round on every changed claim.
6. **The exits.** (e) conform - the words to the code and the labels to the page; no behavior changes.
7. **The search smell.** None.
8. **The budget.** 30 min for the three tasks with one landing.
9. **Done, measured.** One goal: the claims round reads every changed claim IN-STEP; no code token changes (the gate's semantic key unchanged).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T17 Approach (re-answered 2026-10-21T12:56Z)

1. **The goal, in the world.** As before: every claim says what the code does, labeled as its page labels it.
2. **The constraints.** As before, and 0033's drawing page (a row street "runs on off the map as the road into it") and 0081's (lanes along the hem of dry fields; the spur stops at the hem's edge), which the round read.
3. **Where each comes from.** R (0246, 0033, 0014, 0081).
4. **Do they describe the world here?** Yes - the round, 2026-10-21 (impl-drift, 27 claims): where a claim's page disagrees with the CODE, the code's drift is a task of its own; where it disagrees with the label, the label follows the page.
5. **The order.** The street and `_pull_back` claims left as they were (their drift is the code's - T54, T55); the others labeled GUESS; `_SERVE_FT` cited plainly; `_lay_skeleton`'s arm claim split into the plain 7 ft clip and the GUESS pull-back; the claims round.
6. **The exits.** (e) conform - words and labels; the code's drift carried (T54, T55).
7. **The search smell.** None.
8. **The budget.** With the batch.
9. **Done, measured.** The claims round reads every changed claim IN-STEP; the street and `_pull_back` drift filed as T54 and T55.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T17 Decisions

**D29 - the lane-end words.** `_pull_back`'s comment ends the lane "at the last homestead it serves"; `WAY_END_REACH_FT` names a farmhouse and another way (the field's reach is `law.FIELD_REACH_FT`); `_lay_skeleton`'s span floor reads half a pitch (50 ft) each way, a pitch across; the pull-back claims of `_trim_to_service`, `settle_dangling`, `_sweep_dangling_ends`, `_walk_in`, `served_arm`, `tidy_lane_ends`, `_pull_back`'s trim floor and `_lay_skeleton`'s arm trim (split from its 7 ft clip, which 0246 states plainly) are labeled GUESS, as 0246 labels the rule; `_SERVE_FT`'s 100 ft cites 0246 plainly (the page states it). The round found three street claims and two `_pull_back` claims drifting from their pages in the CODE (0033: a street runs on off the map; 0246: an end at the dooryard): those claims stay as they were and the code's drift is carried to T54 and T55.

<!-- plan-archive: T16 to T16 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T16 to T16 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T16 to T16 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T58 to T58 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T57 to T53 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
## T81, T80, T82, T20, T08, T10 - one block reading, the join's width, the walk off a way, three claims (batch 6's rounds; 385's)

### T81 Approach (checklist part A)

1. **The goal, in the world.** The decide guard and `make plan-delta` read a plan block the same way.
2. **The constraints.** `plan_gate.block_status` (plan-delta), which forgives a typo-scale change from a block's reviewed text (375 FR-005(b)); `_section_clear`, the decide guard's reading of the active task's section.
3. **Where each comes from.** O (features 375, 405).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (batch 6: with T79's blocks appended under T77's, plan-delta owed nothing while `_section_clear` read T77 Decisions' digest as changed and refused T74's claims check, escaped with DECIDE_OK).
5. **The order.** `_section_clear` takes the plan's history and forgives a typo-scale change from the reviewed text as `block_status` does; a test.
6. **The exits.** (c) - one reading.
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** A moved blank line passes both, a real change neither (test).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T81 Decisions

**D57 - one reading of a block.** `_section_clear(review, section, history)`: a CLEAR block passes at its digest or at a typo-scale change from its recorded or historical text (`typo_only`); `decision_refusal` passes `History(plan)`.

<!-- plan-archive: T80 to T80 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T80 to T82 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T82 to T20 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T20 to T20 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T20 to T08 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T44 to T44 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T10 Approach (checklist part A)

1. **The goal, in the world.** The track out's last resort and drawn channels are claimed as they stand against 0084.
2. **The constraints.** 0084 (a path may cross a farm ditch on a plank).
3. **Where each comes from.** R (0084).
4. **Do they describe the world here?** Yes - measured 2026-10-21 (385 T120's finding: `connector_dry_exit` never crosses a drawn channel, unclaimed).
5. **The order.** The claim: a DEVIATION from 0084 - the fill lays no plank, so it keeps to the ground between the channels, and a gateway with no such way is refused (`NoDryExit`).
6. **The exits.** (a) claim as a DEVIATION - 0084 permits a plank and does not require one; laying planks from the fill was weighed and refused here (the last resort runs where no bearing is dry; a refused gateway is re-seated, feature 287 W23).
7. **The search smell.** None.
8. **The budget.** 40 min for the batch with its landing.
9. **Done, measured.** The claims round reads it IN-STEP.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T10 Decisions

**D62 - withdrawn; T10 stays open.** 0084 §116 draws a timber deck as wide as the way where a way crosses a ditch, so the research expects the track out to cross a drawn channel on a deck, which the fill refuses; no claim may call that a departure the page does not record (the claims round). T10 is re-scoped to the deck crossing - a code task - and is not landed with this batch.

<!-- plan-archive: T60 to T17 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T54 to T83 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T83 to T84 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T84 to T85 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T85 to T87 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T87 to T90 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T90 to T90 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T90 to T23 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T23 part B (2026-10-21T17:46Z)

Owed by the cohort (cohort@20261021T172647Z: seeds 12, 21, 22, 24, 38 and 901 newly failing), taken while T23 was the last task started - the work that resisted was T18's, whose part B answers it.

1. **What is refusing?** The cohort, on T18's record owner before the owner reached `Lawful` (T18 part B); nothing of T23's - its claim names a fallback and changes no code.
2. **A3 again.** Unchanged: 0014 and 0246.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither for T23.
6. **The one-sentence test.** "A spur's tip that cannot be carried on is pulled back and the field reached another way" - as claimed, read IN-STEP.
7. **The next step is a measurement.** The landing: seeds 1-48 and the pinned rows passed 54/54 on T18's fix.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** No ruling.

<!-- plan-archive: T95 to T95 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T95 to T96 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T96 to T97 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T97 to T100 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T100 to T97 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T100 to T100 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T26 Approach (checklist part A)

1. **The goal, in the world.** A farm's wood shed stands a ken off a wall of its steading - the house's or the kura's - never forward into the dooryard, its first seat turned per household as the coop's is.
2. **The constraints.** 0043 (GUESS there): the shed behind or beside the house, never the front yard, a ken off the wall (about 9.5 ft with the wall gap); the coop's seats turned by the household's roll (feature 328).
3. **Where each comes from.** R (0043) and O (the coop's roll).
4. **Do they describe the world here?** Yes - T34's rounds: `shed_off_a_wall` clears only the house by the ken while `against_a_wall` accepts the kura (a seat 3.5 ft off the kura); `in_front` refuses only a shed wholly past the front wall; the first seat unrolled; `against_a_wall`'s 1.5 ft tolerance lets a shed stand ~11 ft out, unclaimed. The kura's side (0040) is split to T104.
5. **The order.** `shed_off_a_wall`: clear of EVERY wall of the steading by the gap and the ken; no part forward of the front wall (`forward_of_front`); against a wall at no tolerance (the seats stand exactly a ken out); `_wood_shed` turns its seat list by the household's roll (`u`, as the coop's); claims; tests; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 60 min for the batch with its landing.
9. **Done, measured.** A seat 3.5 ft off the kura, one half forward of the front wall and one 11 ft out are refused (tests); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T26 Decisions

**D78 - a ken off every wall, never forward.** `shed_off_a_wall(seat, walls, g, px)`: `clears(seat, walls, g + ken)` (every wall, the kura's too), `against_a_wall(seat, walls[:1], g + ken, tol=0.0)` (exactly a ken off the HOUSE - 0043's "a short step off the house"; the claims round: a shed a ken off the kura alone had passed - and the wall places offered off the house's walls only), and `not forward_of_front(seat, hh)` (no part past the front wall, `seat_y + d/2 > hh`). The seats are not turned by the household's roll here: tried, it moved Sawada's farms into a knot the gap keeps from gathering (measured 2026-10-21), so the roll is filed as T106. The kura's side stays as drawn (north) - T104 owns 0040's west for a scattered farm.

<!-- plan-archive: T103 to T103 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T103 to T103 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T26 Approach (re-answered 2026-10-21T19:13Z)

1. **The goal, in the world.** A farm's wood shed stands a short step off a wall of its house, clear of its kura by as much, never forward into the dooryard, its first seat turned per household as the coop's is.
2. **The constraints.** 0043 (GUESS there): the shed behind or beside the house, never the front yard, a ken off a house wall (about 9.5 ft with the wall gap - the ken the page's GUESS, the gap its DEVIATION).
3. **Where each comes from.** R (0043) and O (the coop's roll).
4. **Do they describe the world here?** Yes - T34's rounds, and batch 11's round: a ken off the kura alone had passed, where the page says off the house.
5. **The order.** `shed_off_a_wall`: against a HOUSE wall at exactly the gap and a ken, clear of every steading wall by as much, no part forward of the front wall; wall places offered off the house's walls only; the seats turned by the household's roll; claims; tests; seeds 1-48.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** With batch 11.
9. **Done, measured.** A seat 3.5 ft off the kura, a ken off the kura alone, one half forward of the front wall and one 1.4 ft past the ken are refused (tests); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T26 Approach (re-answered 2026-10-21T19:24Z)

1. **The goal, in the world.** A farm's wood shed stands a short step off a wall of its house, clear of its kura by as much, never forward into the dooryard.
2. **The constraints.** 0043 (GUESS there): the shed behind or beside the house, never the front yard, a ken off a house wall (about 9.5 ft with the wall gap - the ken the page's GUESS, the gap its DEVIATION).
3. **Where each comes from.** R (0043).
4. **Do they describe the world here?** Yes - T34's rounds and batch 11's round; and measured 2026-10-21: turning the seats by the household's roll moved Sawada's farms into a knot two households' ways cannot gather without passing 2.7 ft from a neighbor's yard.
5. **The order.** `shed_off_a_wall`: against a HOUSE wall at exactly the gap and a ken, clear of every steading wall by as much, no part forward of the front wall; wall places off the house's walls only; the seat roll filed as T106; claims; tests; seeds 1-48 and the pool.
6. **The exits.** (e) conform; the roll filed (T106).
7. **The search smell.** None - one measured roll of Sawada with and without the seat roll.
8. **The budget.** With batch 11.
9. **Done, measured.** A seat 3.5 ft off the kura, a ken off the kura alone, one half forward of the front wall and one 1.4 ft past the ken are refused (tests); Sawada's pool tests pass without the roll (measured); seeds 1-48 and the pinned rows pass.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T103 part B (2026-10-21T19:30Z)

Owed by the cohort (cohort@20261021T192759Z: seeds 10, 24, 36 and 47 newly failing), taken while T103 was the last task started - the work that resisted was T26's.

1. **What is refusing?** The cohort, on T26's wood-shed rule (D78): the new seats moved farms so two households' ways ended within 25 ft of one another, and the knots step's every gather was refused - passing within 0246's 7 ft of a neighbor's garden (T18) or splitting the web; with the seat roll the cohort passed and Sawada failed the same way. Nothing of T103's - a claim.
2. **A3 again.** Unchanged for T103.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** T26's engine change is set down (the shed code and the pool restored to main's) and T107 filed for the knots-versus-gap conflict, which T26 and T106 wait on; T103 lands alone.
6. **The one-sentence test.** "A nub shorter than the ink's touch is not drawn" - claimed, read IN-STEP.
7. **The next step is a measurement.** `make land` for T103: its gate on main's engine.
8. **Every route measured before offering one?** Two T26 routes measured (with and without the roll); both expose the conflict, so neither is offered.
9. **After a ruling: the step it names?** No ruling.

<!-- plan-archive: T105 to T105 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
### T105 Decisions

**D80 - the mend and the footpath claimed.** No code change: the joint moved back a vertex claimed UNRESEARCHED, beside 0081's zigzag rule it serves; `settle_ends`' unwidthed lane claimed as 0081's 3 ft footpath.
