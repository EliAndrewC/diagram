# Tasks - feature 461, the landing lane

Ticked tasks are archived in `tasks-done.md` (feature 449 T142): `make tick` moves each ticked task there with its lines; this file holds the open ones.

**Input**: `plan.md` (CLEAR at round 3: D1-D15 and its phases 0 to 5), `spec.md` (US1-US5, FR-001 to FR-010), `data-model.md`,
`contracts/lane-cli.md`, `quickstart.md`, `research.md` (R1-R3).

Every task is tooling, so every task is `research: rendering`. Each task is one plan phase item, sized for one builder (at most three
jobs, `scripts/container/builder-brief.md`), and leaves the session a working route when it lands (plan, "The phases - each usable
on its own"). Each line names its files, its D-numbers, its Verify (the plan's) and its order. A task whose files include a HELD
file (`rust/guard/src/**` but its tests, `scripts/hooks/*.sh`, the root `Makefile`) says so; its builder runs `make guard-edit
FILE=<file> WHY="<reason>"` for each before the first edit. Each new refusal's test is written first and seen red, then the check
deleted and the test seen red again (constitution XVIII). New code owes 100% line coverage from its own tests (plan, X). American
spellings, hyphens only.

**Ready now** (nothing blocks them): T01, T03, T04, T05. T02 is ready once T01 lands. Every other phase-1 task waits on T05, the
baseline taken before the first code edit (plan, XIII).

**The 451 parts this feature takes over** (spec, "Taken over from feature 451"), each carried by the task named: T302 part 1 (T03
confirms it), T302 part 4 (T30), T307 part 2 (T06), T307 part 3 (T14), T307 part 1 and the T307 box (T27), T308 (T16), T405 (T28),
T415 (T26). Not taken over but answered: 451 T525, its removal replaced by D1, carried by T30. Their 451 boxes were closed at the move
of 2026-11-27 (feature 462, FR-003), each pointing to the task here that carries it; T302's parts 2 and 3 moved to feature 462 as
`451 T302`.

## Occasions

- none: tooling only - the gate's land, task, tree and new lane crates, the guard's shared queue and its gate-write, pool-idle,
  stall-watchdog and clone-sync guards, the Makefile and `scripts/`; no map feature, sheet, glyph, placement rule or research page
  changes.

## Dependencies

Phase 0 (T01-T04) changes nothing for the session. Phase 1 (T05-T10) is the hand-in: T05 first, then T06 and T07 side by side, T08
after both, T09 after T07, T10 after T08. Phase 2 (T11-T23) is the lane: T11, then T12 and T13, T14 after both, then T15-T22 as each
line says, T23 the phase's real batch last. Phase 3 (T24-T26) after T23. Phase 4 (T27-T30) after phase 3 is in use. Phase 5 (T31)
over the first like window after phase 3 is the route.

## Implementation strategy

Land phase by phase: each phase is a working route on its own (constitution XV), so a blocked phase stops none before it. Phase 1
alone already moves the night's refusals before a gate onto the builder with the context; phase 2 takes integration out of the
coordinator (US1, US3); phase 3 the whole red path (US4, US5); phase 4 makes the lane the one route; phase 5 measures it.

## Tasks

### Phase 0 - the record (no engine code; plan, "The phases")

### Phase 1 - the hand-in (US2, FR-002; D3, D4, D14)

### Phase 2 - the lane (US3, FR-003, FR-005; D1, D2, D5, D6 steps 1, 2 and 4, D7, D8, D9, D13, D14)

- [ ] T23 Phase 2's measurement on real work: a real batch of this feature's own tasks handed in and landed through the lane, its `lane.jsonl` and `make lane` read; measured and recorded under `dev/measurements/`: the lane tree's first gate minutes against b1's (D1), how long a background `make lane-wait` outlives the turn that started it (D9; `LANE_WAIT_MAX` priced only if a time limit is found), whether any gate still builds in the clone's own target directory and, if none, that directory dropped (D11; plan, "What retires"). Verify: the recorded figures re-derived from their command outputs; `make task-time SINCE=<the batch's start>` shows the landing's Phase lines under the lane's tree. Lands after T14-T22.
      research: rendering
### Phase 3 - the whole red path (US4, US5, FR-004; D5, D6 steps 3 and 5, D7, D14)

- [ ] T25 Phase 3: a carry conflict becomes a repair entry - where the lane's carry of a hand-in onto `origin/main` stops (main moved after the hand-in), the change is ejected as a repair entry (`why` `conflict`, `units` the conflicting files; it pins nothing) and the rest of the batch runs, in `rust/gate/crates/lane/src/` (D7; US5). Verify: red first in the end-to-end test - a hand-in conflicting with a newer main becomes one `conflict` entry and the other change lands; `make rust-test CRATE=rust/gate/crates/lane`. Lands after T15 and T23.
      research: rendering
### Phase 4 - the one route (FR-001, FR-008; D10, D11)

- [ ] T29 Phase 4: the one route - `make land` refused outside the lane's tree, naming `make lane-start`, escape `LAND_HERE_OK="<reason>"` recorded (for the lane's own failure); and `make land` refuses an unclean tree, naming each file, in `rust/gate/crates/land/src/land.rs`'s dispatch arm and a new module beside it (D11; 451 T302 part 4; FR-008). Verify: red first in the land crate's tests - a landing refused in the clone with its command, the escape recorded, an unclean tree refused naming its files, each check deleted and its test seen red (XVIII); `make rust-test CRATE=rust/gate/crates/land`. Lands after T26 (after the lane has carried a like window's landings, phase 3 in use); lands before T30.
      research: rendering
- [ ] T30 Phase 4: land-alone retired - `rust/gate/crates/land/src/land/alone.rs` and `land-alone.sh` steps 1 to 6 (among them step 2, the task's own sections committed apart, and step 3, the attribution of uncommitted files by the event log) removed; step 7 moved to `scripts/take-tip.sh` and run by `scripts/sync-with-main.sh`'s `sync-in` where `git pull` would stop on a dirty sectioned file; `land/writers.rs` STAYS; the `-land` worktree NOT removed (it is the lane's tree, D1); the lane's next batch green (D11; plan, "What retires"). Verify: the land crate's tests; `make hooks-test`; `sync-in` taking a tip over a dirty sectioned file in a scratch clone; the lane's next batch green. Lands after T29. Closes 451 T302 part 4 (T302's box stays open in 451 for parts 2 and 3) and 451 T525 (its removal of the `-land` worktree replaced by D1: the worktree stays as the lane's, its cache the lane's warm cache): a pointer here on each box.
      research: rendering
### Phase 5 - the after-measurement (FR-006, FR-007, FR-010; D12, D13)

- [ ] T31 Phase 5: the after-measurement - over the first like window after phase 3 is the route, chosen by D12's likeness test (eight hours or more of builder work, trees held and median load within their GUESS bands), D12's script run and every figure of its table beside the night's, both windows' trees held and median load stated beside each figure where they differ (FR-010), each per-task figure beside task size (FR-007), total tokens per landed task by kind and actor (FR-006); D13's waits reported apart, the queue entries that waited on another task's landing named; then `make feature-report F=461 WRITE=1` (D12, D13; the Success measure). Verify: the figures re-derived from their recorded command outputs; the GM reads the comparison. Lands after T26 and a like window after it.
      research: rendering
- [ ] T35 Phase 5: settle the number of builders (L7R_BUILDERS, a GUESS at 3) by measurement once the lane takes integration off the coordinator (the GM 2026-11-27, his sixteenth process-reviewer message in specs/449-rust-codebase/port-talk-gm-goal.md: 'this reflects a huge impact to our throughput where we don't want to wait until later'): over like windows (FR-010: trees held and load stated) run 3 and 4 builders, each window long enough for its own landings, and compare landed tasks per hour of wall clock and per tree-hour, total tokens per landed task by model (451 T532), the cross-blocking row and the lane's queue wait, CPU stall and memory peak (make sampler-report rows by trees held); the night's figures as the starting point (observed 2026-11-27, method: make sampler-report 02:00Z to 15:00Z - four trees held about 420 min and three about 220, memory peak 59% and 31% of 10 GiB, median load 14.3 and 12.5 on 22 cores, CPU stall 1.04 s and 0.69 s a sample, integration the bottleneck so throughput not comparable); the knob set by the result with its dev/audits/ entry (measurement, falsifier, cadence) - lands after T23 (the lane running), beside T31
      research: rendering
- [ ] T36 Phase 4: make review-tree's bundle reads land-alone's attribution - scripts/gates/review-tree.sh:109 takes the PYLIB of scripts/land-alone.sh (step 3, the attribution of uncommitted files by the event log) and runs its split; T30 retires step 3, after which make review-tree dies 'scripts/land-alone.sh holds no PYLIB to read the attribution from' (found by 461 T03's grep, dev/measurements/2026-11-27/461-t03-land-alone-callers/output.txt). Move the split where review-tree.sh reads it, or give review-tree its own rule, before T30 removes it. Verify: make review-tree over a scratch bundle after the PYLIB leaves land-alone.sh; make hooks-test. Lands before T30.
      research: rendering
- [ ] T77 an open batch keeps a change a later hand-in superseded: 462 T278's closing half handed in cf6a3887ee over the stopped batch 462-2 that held 0075e5fa37, and the resume ran 462-2 again with 0075e5fa37 (attempt 2, the same first-pass refusal, 2026-11-28T03:4xZ) - so a stopped batch can never clear by the fix that answers it; the resume should drop a superseded change from its batch and form the next batch with the hand-in that superseded it (rust/gate/crates/lane, runner/run.rs's resume and log::state's superseded), red-first with that case
      research: rendering
- [ ] T79 a batch change whose task is already ticked on main is ejected as a red, not read as landed: batch 462-2 held 462 T278's first hand-in (0075e5fa37) while T278 landed by hand from its closing half (cf6a3887ee); attempt 4's first pass refused 'T278 is already ticked' and the lane ejected it as repair r2 (why red, 2026-11-28T04:0xZ, .git/l7r-lane/attempts/462-2-4.log) - an open repair with nothing to repair, offered first to every free builder; read a change whose tasks origin/main ticks as landed (log::state, the runner's step), and let an entry whose tasks all landed close - red-first
      research: rendering
- [ ] T81 US6 (FR-011) part 1, the policy and its one reader: the builders' scheduling policy as one record the GM's words set (its file, its form - feature lines 'all', 'floor N', 'share' and class lines for performance and [bugfix] - and its default when absent), read by one function in l7r_shared::builder_queue that ranks the READY work every handout path asks for; the class membership as FR-011 states it (performance as 451 FR-013 settled it; a [bugfix] tag given by make task-add BUGFIX=1 or on the line); the rules FR-011 replaces made forms of it (performance first, T313's unlisted performance tasks, the caller's own queue, the name-order fallback, a queue's #! order=queue below the classes, repairs ranked by their task's class and feature) - red-first with the 2026-11-28 case (462 disk tasks handed builders while 461 phase 3 tasks stood ready)
      research: rendering
- [ ] T82 US6 (FR-011) part 2, every handout path reads the one policy and a departure is refused: make builder-next, make builder-done's next dispatch, make queue's pick, make builder-brief, the pool-idle Stop guard, the set-down Stop hook's start-the-next (set_down_hooks next_performance_in) and make task-start single and bundle (US6's 17-file search) ask part 1's reader, none keeping a rule of its own; make builder-brief and the Stop guard refuse a departure naming the policy's pick, escape SCHED_OK with its ground (the pick cannot be worked yet for a reason the tool cannot see) recorded; lands after part 1
      research: rendering
- [ ] T83 US6 (FR-011) measured, SC-007: replay the pool's log of 2026-11-28 under a policy giving 461 every builder it can use - every handout path names a ready 461 task wherever one stood ready and a performance or [bugfix] task of any feature ahead of both - and, over the first like window after parts 1 and 2 land, count free trees given to work the policy ranks below a ready one, the escapes with their grounds beside the figure
      research: rendering
- [ ] T86 the lane places a coverage red by crate, not by the file it names: batch 462-3's gate went red on 'lines no test reaches' in rust/gate/crates/plan/src/plan/split.rs (+ split/tests.rs) and rust/guard/shared/src/speckit/archive/report.rs (+ report/tests.rs) - files only 462 T545/T555's change (1505e57eeb) adds or touches - yet attribute.rs read the cover-run lines by crate, several changes touched each crate, and the whole batch of six changes (T543, T545/T555, T146/T206, T107/T173, T120, T544) was ejected as repair r3 (2026-11-28T04:4xZ, .git/l7r-lane/attempts/462-3-1.log); place a 'lines no test reaches' line on the one change whose delta touches that FILE, red-first with that log
      research: rendering
- [ ] T78 D6 step 2's narrowing: a red unit naming several changes halves over those candidates alone, the others riding with the first half (rust/gate/crates/lane/src/attribute.rs, halve.rs, runner/run.rs); T24 halves over every change that ran, correct but up to a run or so slower; needs a rider pin rule written first (a lone candidate red beside riders is no one-change run)
      research: rendering
- [ ] T93 T76/T26's done commit (refs/l7r/done/461-T76, 1a729b9a7a) predates T63: its new test in rust/gate/crates/lane/src/batch/tests.rs (an_open_batch_s_end_lands_...) builds World with no all field, which HEAD's l7r_shared::lane_log::World requires since T63, so the lane crate's tests fail to compile once it is carried and the batch gate goes red - add all: &all to that literal at its carry, research: rendering
      research: rendering
- [ ] T80 gate-write: a make target that writes a tracked spec file aimed into a gated tree is let through - task-withdraw, queue-add, gm-reviewed beside task-add (held since 461 T27); rust/guard/src/guards/gate_write_hooks.rs MAKE_WRITE; measure each one's writes against preflight --tree-check first (make append is unseen on purpose, 405 T41); observed 2026-11-27 by reading MAKE_WRITE against the Makefile
      research: rendering
- [ ] T87 no command withdraws a misfiled arbiter ruling's part-B owing: red-gate@2026-11-28T03:47:58Z (461's landing) charged 462 T22 a part B in the clone's common .git/approach-owed.json (row {462-efficiency-backlog, T22, part B, 2026-11-28T03:51:25Z}) and its ruling row sits in specs/462-efficiency-backlog/arbiter.jsonl (55c7bd6da6); make tick refuses 462 T22 until a part B is written or the row is dropped by hand - add a withdraw verb (rust/gate/crates/plan/src/plan/approach.rs owed_entries/owe_all, a make target, its reason recorded) and use it for this row
      research: rendering
- [ ] T96 a repair entry ejecting several changes cannot be handed out: make builder-brief REPAIR=r3 (462 batch 462-3's six ejected changes, 2026-11-28T05:3xZ) applied the first done commit onto the tree uncommitted, then refused the next ('the handout could not build on refs/l7r/done/462-T545 ... 13 staged path(s) stand uncommitted') and gave the tree back - builder_tree's build_on takes one done commit; apply a repair's changes in order onto the tree (each committed scratch, or the carry's own stacking), or hand each innocent change back to the lane apart; red-first with a two-change entry
      research: rendering
- [ ] T95 make builder-brief and make builder-next take a repair entry of kind integrate (why push, T19; why conflict, T25): builder_queue/repairs.rs passes every integrate entry over as 'no kind make builder-brief takes yet: brief its builder by hand', so each conflict or failed-push repair costs the coordinator a hand brief, where D7 hands it to a fresh builder with the entry's attempt file; rust/guard/shared/src/builder_queue/repairs.rs, rust/gate/crates/task/src/builder_brief.rs
      research: rendering
