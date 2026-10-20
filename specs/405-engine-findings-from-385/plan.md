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


## T30 - a plan bundle for a feature with no request.md is refused, naming the file (found working T12)

### T30 Approach (checklist part A)

1. **The goal, in the world.** A plan review never runs on a bundle without the GM's words; the session learns at build time, with the fix.
2. **The constraints.** Feature 383 amendment 8: a plan review reads the request verbatim (`request.md`) beside the blocks. The GM's rule: a tool, never a reminder; tips live in error output. A test red without it.
3. **Where each comes from.** 383 (O); the GM (G).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (T12: `make decide F=405 T=T12` built a bundle whose MANIFEST named `request.md`, absent; the spec-fidelity pass returned no verdict, 63 s).
5. **The order.** The refusal in `plan_bundle.build` before anything is written; the test.
6. **The exits.** (c) - refuse at build time; building the request from the spec's quote was weighed and refused (the spec's quote may be trimmed).
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: `make decide` / `make plan-delta` on a feature with no `request.md` exit non-zero naming `specs/<feature>/request.md` and what goes in it; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T30 Decisions

**D2 - no request, no bundle.** `plan_bundle.build` raises `SystemExit` before creating the bundle when `spec_dir/request.md` is missing: "plan bundle: specs/<name>/request.md is missing - write the GM's words there verbatim (the request and every amendment, as the spec's 'The request' quotes them), commit it, and build again".

## T31 - task-add numbers a task from the boxes' own ids (found working T12)

### T31 Approach (checklist part A)

1. **The goal, in the world.** `make task-add` gives a new task the next id of the feature's own tasks, whatever the titles quote.
2. **The constraints.** Feature 385 T64 (D83): the next free id, zero-padded as the feature's ids are. A test red without it.
3. **Where each comes from.** 385 (O).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (405's titles quote "(385 T147)"; `next_id` read every `T<n>` in tasks.md and plan.md and gave T148-T154 where T28-T35 were next).
5. **The order.** `next_id` reads the ids of the boxes and of the plan's `## T<n>` headings only; the test.
6. **The exits.** (e) conform.
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: on a tasks.md whose last box is T31 and whose titles name T147, `next_id` returns T32; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T31 Decisions

**D3 - the boxes' ids.** `task-add.next_id` takes the largest id of `^- \[[ x]\] T<n>` boxes in tasks.md and `^## T<n>` headings in plan.md and plan-done.md, plus one.

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

## T33 - `make land`: one command, every cheap refusal first (landing-analysis.md)

### T33 Approach (checklist part A)

1. **The goal, in the world.** Once a task's checks are recorded, one command lands it: what the landing will refuse is known in seconds and all at once, and the long runs start without the session.
2. **The constraints.** The gated route's conditions: a green gate on this content (`gate-stamp.py --check`), the landing cohort on this engine (`cohort_gate.py check`), the claims gate, the review gate, owed ledger rows, a clean tree; each task's tick refusals (385 T117's `land-batch`). The GM, 2026-10-20: "the landing being the biggest cost is something that we need to do something about". A test red without it.
3. **Where each comes from.** The gates (O); the GM (G).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (T12: six refusals one at a time, `make done` and `make cohort-landing` started by hand after their refusals; the checks themselves 7.5 s, 2.0 s, 0.3 s and 0.02 s).
5. **The order.** `scripts/land.py` from `land-batch.py`; `make land` and `make land-batch` both call it; the tests.
6. **The exits.** (c) - one command; running the gate and the cohort in parallel was weighed and left to a measurement of its own (the memory cap, feature 315).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `make land F= T="<one or more>" NOTE=` prints every cheap refusal together and stops; otherwise runs `make done` when the gate stamp does not cover the content and `make cohort-landing` when the cohort gate would refuse, commits the files the gate regenerated under `pool/`, pushes with `L7R_LAND_TICKS` set and ticks each task; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T33 Decisions

**D5 - one landing command.** `scripts/land.py <feature> "<ids>"` (NOTE from `LAND_NOTE`), one task or more. Pass 1, nothing run: each task's tick refusals but the landed one, uncommitted work, owed ledger rows (`ledger_owed`), the claims gate, the review gate, the holding rule with `L7R_LAND_TICKS` - every failure printed, then exit 2. Pass 2: `gate-stamp.py --check origin/main`; when it refuses, `make done`; when the cohort gate's `check` refuses on an engine delta, `make cohort-landing`; changes the runs leave under `pool/` committed as "regenerated by the landing's gate"; then `sync-with-main.sh done` with `L7R_LAND_TICKS`; then each tick, noted "landed: <note>" (or "landed in batch T1+T2: <note>"). `land-batch.py` keeps its name as a shim to `land.py`.

## T34 - the push asks its cheap questions first (landing-analysis.md)

### T34 Approach (checklist part A)

1. **The goal, in the world.** A plain `sync-with-main.sh done` that will refuse on the holding rule or undeclared occasions says so in seconds, before its slower checks.
2. **The constraints.** The push's checks and their messages unchanged; only their order. A test red without it.
3. **Where each comes from.** The push (O).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (`push_cmd` runs `push_checks.py` and the claims gate, then the fetch, then the holding rule, then `review-gate.sh`).
5. **The order.** The holding rule and `review-gate.sh` moved ahead of `push_checks.py`, the holding rule judged against the fetched main as now; the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a push held by an open active task, or with undeclared occasions, refuses before `push_checks.py` runs; `tests/hooks/test-sync-with-main.sh` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T34 Decisions

**D6 - cheap first.** In `push_cmd`, the fetch, the delta (`ours`), the holding rule and `review-gate.sh` run before `push_checks.py` and `claims-gate.sh`; nothing else moves.

## T35 - render-sync after a landing runs in the background (landing-analysis.md)

### T35 Approach (checklist part A)

1. **The goal, in the world.** A landing returns once its work is on main; main's renders refresh behind it.
2. **The constraints.** The GM browses renders in main (2026-08-12: a stale render cost a round trip), so render-sync still runs after every landing; `render_sync_background` already exists for the prompt hook. A test red without it.
3. **Where each comes from.** The GM (G); the push (O).
4. **Do they describe the world here?** Yes - measured 2026-10-20 (T12's push: 2.5 min, most of it render-sync regenerating four magistracy maps other sessions had changed).
5. **The order.** `done` calls `render_sync_background`; its message says where the render's log is; the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: `sync-with-main.sh done` returns after the push with render-sync started in the background (its lock and log as the prompt hook's); `tests/hooks/test-sync-with-main.sh` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T35 Decisions

**D7 - the render behind the landing.** `sync-with-main.sh done` runs `push_cmd` then `render_sync_background`, printing where the render's progress is logged; `render-sync` itself stays foreground for a hand run.
