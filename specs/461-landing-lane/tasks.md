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

- [ ] T24 Phase 3: the halving - `rust/gate/crates/lane/src/halve.rs` replaces the phase-2 whole-batch ejection: the candidates in hand-in order, the first half run as a batch of its own, a green half pushed at once, a red half halved again, the one left after every other change landed green ejected without a run of its own (`why` `inferred`); a change ejected after its own one-change red run is `why` `red`; no retry of a flake (`LANE_RETRY`, a GUESS knob) (D6 steps 3 and 5; US4; FR-004). Verify: red first in the end-to-end test - with n = 4 and n = 6 and one bad change in each half, the good changes land within ceil(log2 n) + 1 further runs (D6's table); the tripwire by task stays quiet through the n = 6 halving whose bad change is C (two reds in a row that pin no task) and fires when a task left last by one halving is left last again by a later batch's, the lane stopped and the arbiter owed; `make rust-test CRATE=rust/gate/crates/lane`. Lands after T18 and T23.
      research: rendering
- [ ] T25 Phase 3: a carry conflict becomes a repair entry - where the lane's carry of a hand-in onto `origin/main` stops (main moved after the hand-in), the change is ejected as a repair entry (`why` `conflict`, `units` the conflicting files; it pins nothing) and the rest of the batch runs, in `rust/gate/crates/lane/src/` (D7; US5). Verify: red first in the end-to-end test - a hand-in conflicting with a newer main becomes one `conflict` entry and the other change lands; `make rust-test CRATE=rust/gate/crates/lane`. Lands after T15 and T23.
      research: rendering
- [ ] T26 Phase 3: the batch knobs and the open batch's end - D5's knobs recorded beside their rules with their labels (`LANE_MAX`, `LANE_WAIT_S`, `LANE_RETRY`, `LANE_IDLE_S`, `LANE_REPAIR_FIRST`, `HAND_IN_BASE`; the tooling crates are outside `make tunables`, so each beside its rule as 451 D14 did); each batch's size and runs on its `landed` line for trial 458; D14's end of an open batch: a later hand-in of a task the batch landed carried on top, of one it ejected superseding it and that repair entry read as closed (`superseded`), in `rust/gate/crates/lane/src/batch.rs` (D5, D14; FR-004). Verify: red first in the lane crate's tests for both ends of an open batch; `make rust-test CRATE=rust/gate/crates/lane`. Lands after T24. Closes 451 T415 (the lane runs the batch itself in place of the proposed `make land` line): a pointer here on 451 T415's box.
      research: rendering
### Phase 4 - the one route (FR-001, FR-008; D10, D11)

- [ ] T27 Phase 4: the gate-write guard over two trees - the fixture in `rust/guard/src/guards/gate_write_hooks/tests.rs` and `tests/hooks/test-gate-write-hooks.sh`: a commit, an Edit and a `make task-add` in the clone while the lane tree's gate runs let through; the same aimed into the lane's tree held (D10; FR-001). Verify: `bash tests/hooks/test-gate-write-hooks.sh`; `make hooks-test`; `make rust-test CRATE=rust/guard`. Lands after T26. Closes 451 T307 part 1, and with T06 (part 2) and T14 (part 3) the T307 box: a pointer here on 451 T307's box.
      research: rendering
- [ ] T28 Phase 4: 451 T405's option (C) - a test that the lane's gate is not voided by the clone's plan stub, a measurement record's commit, or a fetch log's append in the clone, every landing gated in the lane's tree at its commit (D10; FR-001); its options (A) and (B) not built. Verify: the test in `rust/gate/crates/measure/src/measure/preflight*` or the lane crate's end-to-end test, red first; `make rust-test`. Lands after T26. Closes 451 T405: a pointer here on its box.
      research: rendering
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
- [ ] T40 Phase 1: at hand-in the claims gate's owed-with-no-flight refusal is scoped to the builder's own work - spec-fidelity's MODE 1 exception ruling of 2026-11-27, LEGITIMATE with three bounds that are part of the ruling: (1) an owed claim whose unit's code, claim text or cited research page the hand-in's delta (the working tree against the hand-in base) touches, or a claim it adds or moves, is the builder's, never excused as 'owed at the base too'; (2) with no hand-in base named or none that resolves, every owed claim with no flight refuses as today (delta_base::named's None); (3) only that refusal is scoped - introduced findings (already base-scoped by T34), form problems and carries unchanged, and at a landing (L7R_DELTA_BASE empty) the first pass and the claims round ask every owed claim as before (FR-008) - rust/gate/crates/claims/src/claims/index.rs owed (about line 578, it reads no base today) and scripts/gates/claims-gate.sh; red-first: a claim owed by other staged work quiet at hand-in, one the delta touches refused at hand-in, the first refused at a landing; found by T34's builder; lands before T08
      research: rendering
- [ ] T75 a measurement's hand-in stops the lane at its landing: make builder-brief KIND=measurement says 'no plan section' (rust/gate/crates/task builder_brief), yet make land's tick refuses a task whose section is a stub or unreviewed - the lane's batch 462-2 (462 T278, 0075e5fa37, 2026-11-28T03:2xZ) stopped on 'T278's Approach block leaves part A item(s) 12 unanswered' and '2 block(s) of plan.md changed since their review'; make the two agree - a measurement writes and has reviewed its section before builder-done (as 461 T10's builder did), or the tick takes a measurement's record in place of a section - and say which
      research: rendering
- [ ] T76 the lane reads a first-pass refusal row that names a task's plan section as naming no change: batch 462-2's first pass refused on '### T278 (...)' and 'T278's Approach block' (attempt .git/l7r-lane/attempts/462-2-1.log), yet the runner stopped with the batch open (461 T15's no-change rule) instead of ejecting T278's change as a repair; rust/gate/crates/lane/src/attribute.rs should place a row naming T<n> of feature F on the batch's change for F T<n>, red-first with that row
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
- [ ] T84 make arbiter-ruled files a ruling under the clone's .specify/feature.json feature, not the trigger's: the ruling of red-gate@2026-11-28T03:47:58Z on 461 T74/T63's landing (461's work, SPECIFY_FEATURE=461 in the dispatching shell) was recorded in specs/462-efficiency-backlog/arbiter.jsonl and made 462 T22 - unrelated, waiting - owe a checklist part B; file a red-gate ruling under the feature of the landing that tripped it, red-first
      research: rendering
