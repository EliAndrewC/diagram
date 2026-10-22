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
<!-- plan-archive: T10 to T10 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T10 to T10 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
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

<!-- plan-archive: T103 to T105 moved to plan-done.md, 2026-10-21 (feature 375 FR-044) -->
<!-- plan-archive: T10 to T10 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
<!-- plan-archive: T10 to T10 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
## T107, T26 - a knot's gather where the fence gap would leave it (the GM, 2026-10-21: room first, within the research)

### T107 Approach (checklist part A)

1. **The goal, in the world.** Two households' ways that arrive within 25 ft of each other are walked as one meeting, even where the meeting stands beside a neighbor's garden fence - as paths in a village of abutting lots ran along fences.
2. **The constraints.** 0081's knot (ends within 25 ft joined at one point); 0246's 7 ft from a lane's middle to another household's garden fence (T18); 0081's crop clearance (a lane may touch a plot's boundary, its middle 3 ft off, `WEB_CROP_GAP`); the lane law's needle, fold, hairpin and bend rules; the web kept whole; seeds 1-48 and the pinned rows.
3. **Where each comes from.** 0081's knot: R. 0246's 7 ft: O - the page says "a map drawing convention, not a measured figure". The crop clearance: R (0081). The homestead spacing (`grow_gap`, 18 + 2 ft) and the homestead ground: R-bounded - the spacing pass of 2026-10-22 (`spacing-research.md`) puts the attested clustered-village lot at 90-180 tsubo typical, 300-480 rare; the map's 104 ft homestead (305 tsubo) is above the typical range and inside the rare band, so some widening stays within the research.
4. **Do they describe the world here?** 0081's knot does: seed 24's are two tees 25.0 ft apart on one way. The 7 ft gap does not at a meeting: the gather's diagonal passes 5.7 ft from the neighbor's fence (its tread's edge 4.2 ft off), which no reader of the research would call wrong where lots abut.
5. **The order.** The gather stays where it is in the settle (after the ways are drawn); nothing placed earlier moves.
6. **The exits.** (a) refine the O number - taken, for a gather alone; (b) a knot excused where one lane runs between its two tees - not taken: 0081 says within 25 ft; (c) a new gather form - not needed for seed 24; (d) more room - tried first and measured worse: +5 ft and +10 ft of `grow_gap` (about 335 and 365 tsubo, inside the rare band) newly failed six seeds and refused the reference map (`spacing-research.md`), and the research's typical range gives no reason to go wider still; (e) conform - leaves the knot.
7. **The search smell.** The gather is a search over moved forms against the law; the change narrows one clause of one judge, and runs it only for the knots the convention leaves.
8. **The budget.** 60 min with its landing.
9. **Done, measured.** A gather the 7 ft refuses and the crop clearance admits is taken only after the 7 ft pass (test); seeds 1-48 and the pinned rows 54/54 with T107 alone (measured `dev/cohort-log/20261022T040935Z-*`).
10. **Before moving a constant.** `WEB_FABRIC_GAP` is not moved: `Lawful.fence_gap` defaults to it, and only `settle_knots`' second pass sets `WEB_CROP_GAP`; every other reader (`MIN_WEB_GAP`, `grow_gap`, the seating, every other step's `Lawful`) keeps 7 ft.
11. **Before fitting things into room.** n/a - nothing is fitted; the room was weighed in A6(d): two widths within the research's band, both measured worse.

### T107 part B (2026-10-22T04:13Z)

Owed by cohort@20261022T034941Z (seeds 8, 18, 20, 36, 41, 47 newly failing, `grow_gap` +5 ft) and cohort@20261022T034510Z (seeds 10, 24, 36, 47, T26 in the tree).

1. **What exactly is refusing?** Looked at, by a trace of the gather's judge: seed 24 - every gather of lane 6's foot and lane 16's tee refused, the diagonal for `fabric` (5.7 ft off garden 13, 5.1 ft off its fixture), the re-aim for `needle_joins`, the cut for splitting the web; seed 36 - `needle_loops` and a split web; seed 10 - `connector_hairpins`, `bends`, `needle_loops`; seed 47 - the field way turned down (doubled_tails x12, fabric x228), not the knots step.
2. **A3 again.** The 7 ft gap: O, by 0246's own words. The 25 ft knot: R (0081). The homestead room: above the typical attested lot, inside the rare band.
3. **A4 again.** At seed 24's meeting the gap does not describe the world; the knot does.
4. **Moving something earlier for something later?** Widening the homesteads would have; within the research's band it was measured, and made the cohort worse.
5. **Tuning or changing?** Two widths of `grow_gap` measured (+5, +10), both worse: stopped there (B5), back to A6.
6. **The one-sentence test.** "Why 7 ft?" - a convention, so a meeting the 25 ft rule asks may pass a fence at 0081's crop clearance. "Why not make it bigger?" - it was: two widths within the research's band, both measured worse; the homesteads already stand above the typical attested lot.
7. **The next step is a measurement.** The cohort with T107 alone, then with T26 on it.
8. **Every route measured before offering one?** Yes: +5, +10, the crop clearance on every gather (seed 24 cleared, seed 7 newly knotted - an earlier gather admitted at 3 ft reshaped the web), and the crop clearance only for the knots the 7 ft pass leaves (54/54). No question goes to the GM: the research decides it.
9. **After a ruling:** no ruling.

### T26 part B (2026-10-22T04:13Z)

Owed by cohort@20261022T034941Z, charged to T26 and T107 together (the in-flight charge built the same night).

1. **What exactly is refusing?** With T107 in the tree (`dev/cohort-log/20261022T041238Z-*`): seed 24 cleared; seed 10 knots that the gather cannot take without a connector hairpin, a bend or a needle loop; seed 36's without a needle loop or a split web; seed 47 refused because the field way's runs are turned down (doubled tails, fabric) - three conflicts, none the fence gap.
2. **A3 again.** 0043's shed a ken off a house wall: R (a GUESS on the page for the ken). The angle rules: R (0081).
3. **A4 again.** The shed rule describes the world; the refusals are downstream, in the ways the moved sheds leave.
4. **Moving something earlier for something later?** Not done: the sheds stay where 0043 puts them.
5. **Tuning or changing?** Neither yet - T26 stays set aside, its shed change kept as a patch; its three remaining conflicts are written into T26's own box, worked in 405.
6. **The one-sentence test.** "Why does a shed move a lane?" - its seat moves the steading's free ground, and the way is walked round it.
7. **The next step is a measurement.** Each remaining seed's gather or field-way refusal traced, as seed 24's was.
8. **Every route measured?** Room measured at two widths within the research's band, both worse (above).
9. **After a ruling:** none.

### T107 Decisions

**D83 - a knot the fence gap leaves is gathered at the crop clearance.** `settle_knots` gathers in two passes: every knot first with the fence gap as it stands (`Lawful.fence_gap = WEB_FABRIC_GAP`, 7 ft, 0246's convention), then the knots left with `Lawful.fence_gap = WEB_CROP_GAP` (3 ft from the join's middle to another household's garden, 0081's "a lane may touch a plot's boundary"). `fouled_segment` takes the gap (`gap`, default `WEB_FABRIC_GAP`); `Lawful.ground_fault` reads `self.fence_gap`. Only the knots step sets it; every other `Lawful` keeps 7 ft. Labeled: the 7 ft stays a map drawing convention; the gather's 3 ft is historically accurate in the sense 0081 gives (a path may run along a fence), applied where the convention and 0081's knot rule collide - R over O. Measured: the crop clearance on every gather knotted seed 7 (an earlier gather admitted at 3 ft reshaped the web), so it is the second pass only. More room was tried first: two widths of `grow_gap` within the research's band (A6(d), `spacing-research.md`), both measured worse.

### T107 Approach (re-answered 2026-10-22T04:25Z)

The Decisions block re-decided only in wording (the research's bound stated as it is); every answer stands as corrected:

1. **The goal, in the world.** Two households' ways that arrive within 25 ft of each other are walked as one meeting, even where the meeting stands beside a neighbor's garden fence - as paths in a village of abutting lots ran along fences.
2. **The constraints.** 0081's knot (ends within 25 ft joined at one point); 0246's 7 ft from a lane's middle to another household's garden fence (T18); 0081's crop clearance (a lane may touch a plot's boundary, its middle 3 ft off, `WEB_CROP_GAP`); the lane law's needle, fold, hairpin and bend rules; the web kept whole; seeds 1-48 and the pinned rows.
3. **Where each comes from.** 0081's knot: R. 0246's 7 ft: O - the page says "a map drawing convention, not a measured figure". The crop clearance: R (0081). The homestead spacing (`grow_gap`, 18 + 2 ft) and the homestead ground: R-bounded - the spacing pass of 2026-10-22 (`spacing-research.md`) puts the attested clustered-village lot at 90-180 tsubo typical, 300-480 rare; the map's 104 ft homestead (305 tsubo) is above the typical range and inside the rare band, so some widening stays within the research.
4. **Do they describe the world here?** 0081's knot does: seed 24's are two tees 25.0 ft apart on one way. The 7 ft gap does not at a meeting: the gather's diagonal passes 5.7 ft from the neighbor's fence (its tread's edge 4.2 ft off), which no reader of the research would call wrong where lots abut.
5. **The order.** The gather stays where it is in the settle (after the ways are drawn); nothing placed earlier moves.
6. **The exits.** (a) refine the O number - taken, for a gather alone; (b) a knot excused where one lane runs between its two tees - not taken: 0081 says within 25 ft; (c) a new gather form - not needed for seed 24; (d) more room - tried first and measured worse: +5 ft and +10 ft of `grow_gap` (about 335 and 365 tsubo, inside the rare band) newly failed six seeds and refused the reference map (`spacing-research.md`), and the research's typical range gives no reason to go wider still; (e) conform - leaves the knot.
7. **The search smell.** The gather is a search over moved forms against the law; the change narrows one clause of one judge, and runs it only for the knots the convention leaves.
8. **The budget.** 60 min with its landing.
9. **Done, measured.** A gather the 7 ft refuses and the crop clearance admits is taken only after the 7 ft pass (test); seeds 1-48 and the pinned rows 54/54 with T107 alone (measured `dev/cohort-log/20261022T040935Z-*`).
10. **Before moving a constant.** `WEB_FABRIC_GAP` is not moved: `Lawful.fence_gap` defaults to it, and only `settle_knots`' second pass sets `WEB_CROP_GAP`; every other reader (`MIN_WEB_GAP`, `grow_gap`, the seating, every other step's `Lawful`) keeps 7 ft.
11. **Before fitting things into room.** n/a - nothing is fitted; the room was weighed in A6(d): two widths within the research's band, both measured worse.

<!-- plan-archive: T91 to T91 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
## T113 - the room table (the GM's third process fix, 2026-10-21; the arbiter's tooling_fix on ask:set-down-T26)

### T113 Approach (checklist part A)

1. **The goal, in the world.** When a map fails to fit, the session weighing more room sees each spacing knob's research ceiling and whether widening it grows the band the seats are dealt over, so a room probe measures room and not packing, and farms stay within the attested lot sizes rather than "a mile apart".
2. **The constraints.** The GM's three fixes of 2026-10-21 (amendment 8); the arbiter's tooling_fix (each row says whether the band grows with its knob); the ceilings of `spacing-research.md`; a tooling fix lands with its test (feature 379).
3. **Where each comes from.** The GM's words (amendment 8) and the arbiter's ruling: R for the process. The ceilings: R where attested (the 1698 register, Buck, Ushijima), and "unresearched - research question owed" where the pass was SILENT (neighbor spacing).
4. **Do they describe the world here?** Yes: the +5/+10 ft probes of 2026-10-22 widened `grow_gap` in a fixed seating band, which is exactly what the band column names.
5. **The order.** Printed where the session meets the question: part B's prompt from a cohort fit failure (`approach_gate.cohort`), and an arbiter ask naming a knot, a refusal or room (`arbiter_bundle.bundle`).
6. **The exits.** (a) a table in a doc the checklist points to - not taken: remembering to read it is the failure; (b) printed only on fit failures - taken; (c) printed on every part B - not taken: noise on a row or water rule; (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 30 min with its landing.
9. **Done, measured.** A fit failure's part B prints the table, a row-rule failure's does not; an ask naming a knot carries it, one about wording does not (two tests, each red without the wiring).
10. **Before moving a constant.** No constant moves: the table only states the knobs.
11. **Before fitting things into room.** n/a - this is the tool that asks it.

<!-- plan-archive: T93 to T93 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->

<!-- plan-archive: T115 to T91 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->

<!-- plan-archive: T116 to T115 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->

## T117 - the door release's words (T115's round 4)

### T117 Approach (checklist part A)

1. **The goal, in the world.** A field way that starts beside a house it serves can leave that house; its claim says where the release holds as the code tests it.
2. **The constraints.** 0246's no house corner on the tread (§113, kept by `house_hit`); the router's release of a house within `GABLE_MARGIN_FT` + `FIELD_ROUTE_GAP_FT` (13 ft) of a route's start (`mine()`), a GUESS.
3. **Where each comes from.** The tread rule: R. The 13 ft release: U - the claim already labels it a bare GUESS.
4. **Do they describe the world here?** `mine()` frees the house when the start stands within 13 ft of any of its walls (`edge_dist`), not only its front; the claim says "at its door". The door side is not the release's business: the route only needs to leave the wall it starts beside, and the law still keeps every house corner off the tread, so a start beside a gable or the back is let out the same way and the tread rule holds.
5. **The order.** Nothing moves.
6. **The exits.** (a) the claim drops "at its door" for "beside any wall" - taken; (b) test the front wall - not taken: a house record's door side is not what the release needs, and it would wall a route the law already admits, for no map defect; (c) record on 0246 - n/a (a bare GUESS); (d) more room - n/a; (e) conform - n/a.
7. **The search smell.** None.
8. **The budget.** 10 min with its landing.
9. **Done, measured.** The claim re-checked IN-STEP; a docstring only.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.

### T117 Decisions

**D88 - the release beside any wall.** `field_router`'s claim "its own house at its door" says a route starting within 13 ft of any wall of a house is not walled by it (`mine()`'s `edge_dist`), a bare GUESS, the law keeping 0246's no house corner on the tread. No code changes.
