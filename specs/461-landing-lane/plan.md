# Implementation Plan: the landing lane - a thin coordinator, builders that hand in ready work, a merge queue of its own

**Branch**: none (main, in the session clone `diagram-backlog`) | **Date**: 2026-11-27 | **Spec**: `specs/461-landing-lane/spec.md`

**Input**: `spec.md` (FAITHFUL at round 5), `request.md` (the GM's words and the sketch he called "very sensible"),
`research.md` (R1 the reuse decision FR-009 asks for, R2 the code as it stands, R3 the baseline), `data-model.md`,
`quickstart.md`, `contracts/lane-cli.md`.

## Summary

The night of 2026-11-27 measured integration, not building, as the bottleneck: the coordinating session carried 93 commits,
ran 50 landing attempts in its own clone (18 landed), resolved 15 conflicts and repaired every red gate in its own turns, its
context growing about 100k tokens an hour (spec, Why). This plan moves integration out of the coordinator in three parts, each
usable on its own:

1. **The hand-in** (US2, FR-002): `make builder-done` applies the builder's work onto current `origin/main` with the carry's own
   merge rules and runs the landing's first pass there, in the builder's tree, before it commits. No coverage.
2. **The lane** (US3, FR-003, FR-005): a detached runner in a worktree of its own takes the hand-ins in order, runs the existing
   `make land` there, pushes, and wakes the coordinator once a batch with one status line.
3. **The red batch** (US4, US5, FR-004): attribution from the gate's own record first, halving only where it names no change; the
   failing change ejected and returned as a repair entry a FRESH builder takes; the rest landed.

Nothing outside is taken whole: every candidate's merge queue is a rule we borrow (R1). The runner reuses this project's own
detached-runner pattern; the wake-up is Claude Code's background command.

## Technical Context

**Language/Version**: Rust (the workspace's pinned toolchain, `rust/Cargo.toml`), bash for the Makefile and `sync-with-main.sh`.

**Primary Dependencies**: the gate's crates - `land` (the landing, `carry.rs`), `task` (`builder_done.rs`, `builder_tree.rs`,
`builder_queue.rs`), `tree` (`state.rs`'s tripwire), `measure` (`preflight.rs`), the guard's `shared::builder_queue`. One new
crate, `rust/gate/crates/lane/`. No outside dependency is added.

**Storage**: files in the clone's git common directory: `l7r-lane/lane.jsonl` (the lane's log), `l7r-lane/attempts/` (one
output file per gate attempt), `l7r-lane/repairs.jsonl` (repair entries), `l7r-lane/read-mark` (the coordinator's place), the
done refs `refs/l7r/done/*` as today and the hand-in's scratch refs `refs/l7r/hand-in/*`. Shapes: `data-model.md`.

**Testing**: each crate's own tests at 100% line coverage (`make rust-test CRATE=...`), red first; the guard's hook suites
(`tests/hooks/test-gate-write-hooks.sh`); an end-to-end test of hand-in, lane batch, red, eject and land on a scratch clone with a
local bare `origin` (the land crate's `carry/tests.rs` already builds such a world).

**Target Platform**: the Linux container the sessions run in.

**Project Type**: the project's own tooling (gate binary, Makefile targets).

**Performance Goals**: the spec's Success measure, over a like window (FR-010) against the night: landed tasks per hour of
builder work at least the night's, read beside task size (FR-007); the cross-blocking row no higher than 32.3 minutes over 130 (measured 2026-11-27 (make task-time, spec-fidelity's re-run))
tasks; total tokens per landed task no higher (FR-006).

**Constraints**: no history rewritten (no `git rebase`, amend, squash or force push: the "rebase" of FR-002 is a new application
of the builder's diff, D3); every change lands through today's gate and push checks (FR-008); the push's lock and route
unchanged (FR-003); a builder runs no coverage (`docs/process-decisions.md`, REVERSED 2026-11-26); no builder is kept past its
report (451 T308).

**Scale/Scope**: one session, three builders (`L7R_BUILDERS` = 3), about 130 tasks a 12-hour window (R3). Several sessions
sharing builders is feature 459, out of scope.

**Single-artifact target**: N/A - no generator change; nothing draws a map. The two-step rule's analogue here is phase 2's: the
lane is proven on one batch of the feature's own tasks before it is the route for every landing (phase 4).

**Performance bookends**: N/A - no engine stage with a work budget is touched (`make work-budget` counts the hamlet stages).
The lane's own costs are the FR-006 and FR-007 measurement (D12), taken before (R3) and after (phase 5).

## Constitution Check

- **I, II**: N/A - no UI in this repository.
- **III, VII, VIII, IX, XI**: N/A - no pool content, no setting prose, no kanji.
- **IV, V**: PASS - no SOURCE block is added or moved; the GM's words stay in `request.md`'s blocks, which this plan quotes and no
  task edits.
- **VI**: PASS - every phase names its verification (each phase's "Verify" line below): the changed crates' tests red first, the
  guard suites for a guard, `make land`'s gate at each landing, the end-to-end scratch-clone test, and for phases 2 and 3 a real
  batch of this feature's own tasks through the lane, its lane log read.
- **X**: PASS, with the file-scale plan of D15: new code owes 100% (the project's CONVENTION) of its lines from its own tests; no function past 100 lines; (100% the project's CONVENTION; file lengths measured 2026-11-27 (wc -l))
  `land.rs` (873 lines), `land/tests.rs` (908) and the shared `builder_queue.rs` (915) gain no more than a dispatch arm, new code
  going to new files; `carry.rs` (661) gains the no-commit form only. Every knob is a named constant or variable with its label
  (`make tunables` does not walk the tooling crates, so each is recorded beside its rule, as 451 D14 did).
- **XII**: N/A - nothing a generator asserts about the world; every task is `research: rendering`. Each tooling decision below is
  labeled (measured / convention / GUESS knob / the easier route).
- **XIII**: PASS - the baseline before the first edit, in a detached worktree (`git worktree add --detach`): `make rust-test
  CRATE="rust/gate/crates/land rust/gate/crates/task rust/gate/crates/tree rust/guard"` and `make hooks-test HOOKS_ALL=1`, its
  counts recorded in phase 1's first task. The process baseline is R3. What each change is held to: its tests, its callers (the
  coordinator's commands, `make task-time`'s readers of the landing's Phase and `end` lines, which the lane's `make land` still
  writes), the guard suites; a different landing log is not a regression.
- **XIV**: PASS - found while reading: the `land` help text and the gate's line still say the changed modules' coverage runs
  (R2), fixed in phase 0; the night's lost causes (attempts overwriting one log) are fixed by the attempt files (D8).
- **XV**: PASS - each phase is usable alone, so a blocked phase does not stop the ones before it.
- **XVI**: PASS, with three readings named for spec-fidelity's plan review: (a) D7 routes US5's "fresh agent dispatched for that
  batch" through the coordinator's dispatch - a repair entry a fresh builder takes, or the round arbiter on the lane's bundle -
  never an agent the lane launches, for every wake whose work is integration (D7's table); (b) D6 keys the red-gate tripwire inside
  the lane by TASK: it fires on a task's second pinned red (a repair's hand-in red again, one task ejected twice) and stays quiet
  only on a halving's own steps, which pin no task; (c) D3 reads
  FR-002's "rebases" as applying the builder's diff onto `origin/main` with the carry's rules, because the project forbids
  `git rebase`. Each is the literal ask under a constraint the GM set; none drops a requirement.
- **XVII**: N/A - no README.
- **XVIII**: PASS - each new refusal (the hand-in's first pass, the handout's unpushed-filing refusal D13, `make land` outside the
  lane tree D11, the Stop rule that keeps the wake-up armed D9) ships with a test that fails when the refusal is deleted, and the gate runs it.
- **XIX**: N/A - nothing placed on a map.

## Design decisions

Each: the decision, why, its label, the alternatives priced.

### D1 - the lane's tree: the existing landing worktree, adopted into the pool as the lane's reserved tree

**Decision.** The lane runs in `<clone>-land`, the persistent worktree `land-alone.sh` lands in today, joined to the builder pool
by `make builder-tree-adopt` under a reserved holder `lane` that no handout takes and the pool's cap (`L7R_BUILDER_POOL`, 4) does
not count. The tree is the tool's: nobody's work lives there, and the lane brings it to `origin/main` at each batch's start
(`land-alone.sh` step 4's rule, kept). Knob `L7R_LANE_TREE` names another tree.

**Why.** The spec leaves it to the plan (b1 or a tree of its own). Three candidates, priced:

| tree | cache for a gate | pool | cost |
|---|---|---|---|
| `<clone>-land`, adopted | its own target directory, 39 GB (measured 2026-11-27 (du)), built by past landings' gates (coverage builds included); its warmth against today's main unmeasured | adopted as is (a rename chills a cache, 0.1 s to 66 s, Makefile's adopt help, measured 2026-11-26) | keeps the cache 451 T525 would have had the sweep take once land-alone retired; that cache is needed by whatever tree gates (sizes in the paragraph below and T525's line) |
| b1 | 16 GB of test builds and lint only: builders run no coverage (two tiers), so a gate's coverage build starts cold there | already a pool tree | takes the fourth pool slot: a fourth builder needs the cap raised (measured 2026-11-27 (du)) |
| a new tree | cold: 14 to 30 minutes for a first full check (`docs/process-decisions.md`, "Two code builders at once") | made by the pool | a third cache on disk (measured 2026-11-26 (docs/process-decisions.md, two builders)) |

The sizes and the tree's existence: `git worktree list` holds `/diagram/.clones/diagram-backlog-land`, and the target directories
under `~/.cache/l7r-cargo-target/` are 39 GB (`-land`), 16 GB (`-b1`) and 104 GB (the clone's own) (observed 2026-11-27, method:
`git worktree list` and `du -sh ~/.cache/l7r-cargo-target/*`). The adopted tree is the easier route: the tree, its cache and the
pool's mechanics all exist. Label: the easier route, a knob.

**The worktree stays, and 451 T525 is answered by it.** 451 T525 has the `-land` worktree removed when land-alone retires, so the
sweep's dead-tree rule takes its cache, `~/.cache/l7r-cargo-target/diagram-backlog-land` (39 GiB, about 10 GiB after T515's prune,
observed 2026-11-27, method: 451 T520's `dev/measurements/2026-11-27/t520-cache-working-set/results.md`, as T525's line cites).
Under this feature the worktree is NOT removed: it stays as the lane's tree, and its cache is the lane's warm cache, built from
then on by the lane's gates. A live tree is not a dead one, so the sweep's rule never takes it. T525's removal is replaced by
this decision, not taken over (the spec's takeover list does not name it); phase 4, which retires land-alone, closes T525 in 451
with a pointer here (D11).
The measurement that could move it: the lane's first gate minutes in phase 2 against b1's, the cache sizes from `make
builder-trees`. The clone's own target directory, where every gate ran until now, stops being a gate's cache once the lane is
the route; whether to drop it is measured then (D11), not assumed.

### D2 - what drives the lane: a detached runner of our own, `l7r-gate lane --work`

**Decision.** A new crate `rust/gate/crates/lane/` and the commands of `contracts/lane-cli.md`. `make lane-start` (and every
hand-in, idempotently) starts ONE detached process per clone - `l7r-gate lane --work`, in a session and process group of its
own, as `make page-session`'s runner starts `page-session --work` - holding `l7r-lane/lane.lock` with `flock` so a second start
is a no-op that says the first's pid. Its loop: wait for a hand-in, form a batch (D5), run it (D6), log every transition (D8),
write the coordinator's status line (D9). It stops after `LANE_IDLE_S` = 3600 s with no hand-in (GUESS knob: a stopped runner
costs one restart at the next hand-in, a running idle one a sleeping process) and on `make lane-stop`. It is restartable: its state
is the refs and its log, never a memory (data-model.md, "Recovery").

**Why.** Each step of the lane is a shell command (`git`, `make land`), and the spec asks for it "driven by tooling rather than
the coordinator's turns" (US3). Label: convention (this project's runner pattern). Alternatives priced (R1): the Workflow tool -
"No direct filesystem or shell access from the workflow itself", so every step would be an agent's turn, and "the run doesn't
continue on its own" when the session is backgrounded; a loop the coordinator starts - its turns, which US3's acceptance forbids
("no coordinator turn between the hand-ins and the push"); Gas Town's Refinery - a standing tmux-hosted agent (US5 rules out a
standing integrator). The stall watchdog (`stall_watchdog_hooks`) learns the runner's argv as it knows the page session's.

### D3 - the hand-in's "rebase": the builder's diff applied onto `origin/main` with the carry's rules, then the first pass, then the commit

**Decision.** `make builder-done` becomes `l7r-gate land --hand-in` (the land crate, `land/hand_in.rs`), which, in the builder's
pool tree:

1. asks today's refusals (`builder_done::unready`, in process: `land` builds on `task`);
2. commits the work as a SCRATCH commit on the tree's base, kept at `refs/l7r/hand-in/<feature>-<task>` (deleted at step 6);
3. `git fetch origin`, detaches the tree at `origin/main` and applies the scratch commit there with `carry.rs`'s rules in a new
   NO-COMMIT form (`git cherry-pick -n`; plan.md by section, tasks.md by box, request.md by dated section, the `.jsonl` records,
   prose by words). Where the carry stops on a conflict, the tree is left with it and the refusal names the files; the builder
   resolves them and runs `make builder-done` again, which sees the scratch ref and resumes at step 4;
4. runs the landing's first pass in its hand-in form (D4) over the tree as it now stands; a refusal prints every reason with its
   fixing command and nothing is committed;
5. commits the tree (parent `origin/main`), keeps it at the done ref, logs the `done` line with `"handed_in": true` (data-model),
   releases the tree, starts the lane if none runs (D2);
6. deletes the scratch ref and prints the next dispatch (the queue's, as today) and `handed in to the lane` in place of today's
   `make land` line.

**The base by phase** (`HAND_IN_BASE`, a knob): in phase 1 the coordinator still carries into its clone, so the clone's HEAD is
where work lands and is ahead of `origin/main` for the length of every staged batch; the hand-in applies onto the clone's HEAD
then (`clone`). From phase 2, when landings leave the clone, it is `origin/main` (`origin`) and D13 starts with it. Applying onto
`origin/main` in phase 1 would build on a main without the staged work the tree was handed out on, and D13 in phase 1 would
refuse every handout while a batch stood staged.

**The no-commit form's own verified end.** `carry.rs`'s verified end asks "nothing staged" (its doc, R2), which a no-commit apply
contradicts by design; the form ends verified on nothing in progress, nothing unmerged and each non-spec file of the scratch
commit present in the working tree. To confirm in phase 1's first task, with a test.

**Why.** FR-002 asks for the rebase, the first pass, then the commit, in that order, and for a refusal to name its fix. Label: the
literal order, under the no-rewrite rule. Which main, from phase 2: `origin/main` after a fetch, the "current main" of FR-002 and Zuul's "tip of
the branch exactly as it is going to be merged" (R1). Alternatives priced: `git rebase` (forbidden: rewrites history); a `git
stash` and pop (loses the carry's merge rules, which resolved most of the night's 15 conflicts); the lane's tip as the base (a
hand-in would build on work the lane may yet eject); the clone's HEAD (today's, holding the coordinator's unpushed filings, D13).
Cost moved to the builder: one fetch, one carry and the first pass - the push's table alone took 7.01 to 14.27 s (R2) - and its
conflict turns, which were the coordinator's (FR-006 counts them where they land).

### D4 - the first pass at hand-in: what a builder can answer is asked; what is the lane's is not

**Decision.** `cheap_refusals` takes a mode. In the hand-in mode it reads the delta as the working tree against `origin/main` (measured 2026-11-27 (reading the code))
(`git diff --name-only origin/main`, not `origin/main...HEAD`), writes its records into the tree uncommitted, so step 5 commits
them with the work, and asks:

| asked at hand-in (the builder's to answer) | not asked at hand-in (the lane's, asked again when it lands) |
|---|---|
| each task's tick check, `landed=false` (plan review owed, audit entry, ledger row, the GM's words), the phase checklist, open claims, the named files (451 T294) | another writer's changes (`writer_refusal`): the tree is the builder's own |
| the stale coverage-exempt entry; the ledger rows owed | the mark's hold (`ready.rs`): another task's start is the lane's ordering |
| `review-gate.sh`, `plan-gate.sh`, `entry-gate.sh` | the red-gate tripwire (`arbiter gate-held`): a process stop, never a builder's |
| `claims-gate.sh`, with an owed claim with no check in flight a refusal naming the bundle to dispatch | a claims round in flight: the lane's landing waits on it, as today (`claims_wait.rs`); whether `claims::flight_live`, which `in_flight` asks of the tree's root, sees a round dispatched from a builder's tree when asked from the lane's is to confirm in phase 1's first task |
| the push's table (`push-checks --every`): file size, pointers, spec lint, make-targets page | the gate's stamp rows (they need the gate) |

No coverage runs (FR-002; the first pass holds none, R2). **Why.** The night's 19 refusals before a gate were plan review owed 6,
audit entry 5, tripwire 4, ledger row 3, unclear 2 (spec): all but the tripwire are in the left column. Label: measured (the
night's refusal kinds), the split by who can answer. Alternative priced: the whole first pass unchanged in the builder's tree -
refused there by `writer_refusal` and the hold for reasons no builder can cure.

### D5 - when the lane starts a batch, and what it holds (FR-004, 451 T415)

**Decision.** The lane starts a batch as soon as it is idle and a hand-in waits, after `LANE_WAIT_S` = 0 s (a GUESS knob). A batch
is the oldest waiting hand-in plus the waiting hand-ins of the same feature that come straight after it in hand-in order (FR-003's
"in order"): the run ends at the first waiting hand-in of another feature, or at one D14 holds behind an open batch, or at
`LANE_MAX` = 6 changes (a GUESS knob), whichever comes first. A same-feature hand-in that comes after another feature's is NOT
pulled forward: it waits for its own turn, so no hand-in lands ahead of an older one it was not batched with. One feature a batch,
because `make land` takes one `F=`. A repair's hand-in is ordered by its own hand-in time. This replaces T415's printed `make land`
line: the lane runs it. Label: the literal order, the cut at a held hand-in the easier route.

**Why.** The spec seeds the knob from trial 458's finding, and trial 458 has none yet (not read before 2026-11-28; its spec says
the pipeline ran rolling, so the gate ran "when a few tasks stood staged"). So both are GUESS knobs, seeded: 6 is the two-tier
threshold's ceiling of "about six tasks" (`docs/process-decisions.md`), and an immediate start is the trial's "stronger
version" (a continuous gate whose batch is whatever arrived while the last ran), which a lane of its own makes free. Mergify's (Mergify's documented default, CONVENTION)
default 30 s wait was priced: with a gate of minutes, hand-ins gather behind a running batch anyway. The night's reading - smaller
batches landed on the first or second try after 10:00Z, the 63-task batch took 14 attempts - argues for the cap. Trial 458's
verdict resets both; the lane log gives it the batch sizes it asks for.

### D6 - a red batch: attribute, else halve; eject; land the rest (US4)

**Decision.**

1. **Each attempt's output is its own file** (`l7r-lane/attempts/<batch>-<n>.log`), never overwritten.
2. **Attribution from the gate's own record**: the red `test`, `lint`, `cover-build`, `cover-run` and `build` Phase lines in the
   attempt's span name their `crates` (R2); a red hook suite is named in the attempt's output (`test-<name>-hooks.sh`); a red
   first-pass row names its file. Each red unit maps to the batch changes whose delta touches it: a crate by its directory, a suite
   by its own file and its guard's sources (`rust/guard/src/guards/<name>_hooks*`), a row by its file. One candidate: it is
   ejected and the rest runs again. Several: the halving runs over those candidates only, the others riding with the first half.
   None (a red the record does not place: a test that fails only beside other crates' tests): the halving runs over the batch.
3. **The halving, landing as it goes.** The candidates in hand-in order; the first half runs as a batch of its own. A green half
   is pushed at once: it was gated exactly as it lands, on the main it lands on (Zuul's rule, R1). A red half is halved again. When
   every change but one has landed green, the one left is ejected without a run of its own: everything else in the red batch is
   on main, so the red belonged to it alone or to its meeting with them, and its repair builder's hand-in re-tests it on that main.
4. **The tripwire inside the lane, keyed by TASK.** Inside the lane the tripwire still fires on repeated reds on the same work, and
   stays quiet only on a halving's own steps. A red counts against a task only when the lane PINS it there: the task is ejected
   red-attributed (`why` `red`), ejected after its own one-change red run in a halving (`why` `red`: that run's red is its alone),
   left last after a halving (`inferred`), or ejected with its whole batch in phase 2 (`unplaced`). A red half of two changes or
   more pins on nobody, so the red runs in a row of one halving count nothing until a change is ejected; each batch ejects a task at
   most once. The lane
   fires the tripwire at the moment of a task's SECOND pin, read from the earlier `eject` lines of `lane.jsonl` for that task, any
   batch (a repair's hand-in carries the task's id, so its red is the same task's): a repair's hand-in red again, or one task
   ejected from two batches. It then files no second repair: the batch stops, `make arbiter-ask SUBJECT=lane-<task>` is run by the
   lane with the two attempt files as its `FILES`, and the coordinator is owed one line (D7's table). A conflict ejection
   (`conflict`) is not a red and pins nothing. Each lane attempt runs `make land` with `L7R_LANE_BATCH` = the batch's id. The
   variable alone stands nothing down: `tree/state.rs`'s `second_red_gate` leaves a run to the lane's rule above only when the run
   is in the lane's tree (`L7R_LANE_TREE`) AND its batch id names a batch open in `lane.jsonl` (a `batch` line with no `landed` or
   `stop` after it), or the run was started by the runner holding `l7r-lane/lane.lock` (its pid the lock's holder or a child of
   it). A run outside the lane meets `second_red_gate` exactly as today, the variable set or not, so a by-hand `make land` with
   `L7R_LANE_BATCH` exported is no unrecorded escape (FR-008); the recorded escapes stay the arbiter's, as today. Label: the
   reviewer's reading of the tripwire (repeated reds on the same work), the pin rule the easier route. The tripwire keyed by change
   set was priced and dropped: a halving runs smaller subsets, the rest after an ejection is a new set, and a repair's hand-in has a
   new sha, so a set never comes back and the tripwire could never fire in the lane.
5. **No retry of a flake** (`LANE_RETRY` = 0, GUESS knob; Gas Town's `retry_flaky_tests` priced): a flake costs one halving step.

Runs after the batch's first red run, one bad change, the last survivors' gate counted (FR-008: nothing pushes ungated):

| n | where the bad change is | runs (sets run) | US4's bound ceil(log2 n) + 1 |
|---|---|---|---|
| any | attributed by the record | 1 (the rest) | - |
| 4 | first half [A B] | 3: [A B] red, [A] green, [C D] green; B ejected | 3 |
| 4 | second half [C D] | 2: [A B] green, [C] green; D ejected (or [C] red: C ejected, [D] green, 3) | 3 |
| 6 | first half [A B C] | 4: [A B C] red, [A] green, [B] green, [D E F] green; C ejected | 4 |
| 6 | second half [D E F] | 3 or 4: [A B C] green, [D] green, [E] green, F ejected; or [E] red, [F] green | 4 |

**Why.** US4 and FR-004, literally: "first by the gate's own report ... by bisection only where that names none". Label: borrowed
rule (bors, Gas Town, R1); the attribution map is the easier route. A re-run of a subset costs less than a whole gate because a
crate's kept result is reused where its key did not move (`rust/gate/CLAUDE.md`); each run's minutes go on the lane log, so the
cost is measured, not assumed. Alternatives priced: GitHub's remove-and-retest of the one failing PR (needs attribution, which is
step 2); a separate run of each change (n runs where halving needs about log2 n); the tripwire unchanged (the second step of any
halving would stop the lane), or an `ARBITER_OK` on every lane run (an escape on every run teaches every run to escape).

**By phase.** Attribution (step 2) and the tripwire by task (step 4) come in phase 2, with the lane itself: in phase 2 an
attributed red ejects its change and runs the rest, and a red the record cannot place ejects the WHOLE batch as one repair entry
naming every change (so no batch is formed again from the same hand-ins, and each of its tasks takes one pin). A repair whose
hand-in is red again pins its task a second time and fires the tripwire, so the tripwire is live from phase 2. The halving (step 3)
comes in phase 3 and replaces that whole-batch ejection.

### D7 - the repair: a queue entry a fresh builder takes (US4, US5)

**Decision.** An ejected change becomes a repair entry in `l7r-lane/repairs.jsonl`: its task, kind `fix`, the ejected done
commit, why (the attempt file, the red units, or the carry's conflict), and its batch. `make queue` and `make builder-next` read
these entries before `queue.txt`'s (`builder_queue/repairs.rs`, a new module of the shared queue), so the next free tree goes to
a repair first (`LANE_REPAIR_FIRST` = 1, a knob). The repair's `make builder-brief` carries the task's plan section, the ejected
commit and the attempt file's path (T308's rule: what a successor needs is durable when a builder ends). Its handout applies the
ejected commit onto `origin/main` without committing (D3's no-commit carry), so the fix is made on top; its hand-in SUPERSEDES the
ejected done ref. A conflict the lane's carry cannot merge (main moved after the hand-in) is a repair entry too, "conflict-
resolution task" in Gas Town's words (R1).

**Why.** US4: "The repair goes to a FRESH builder given the gate's output; no builder is kept past its report"; US5: "never a
standing integrator, never the coordinator's context". The coordinator dispatches the entry as any other, so its context gets one
queue line, not the conflict or the gate output. Label: borrowed rule (`assign_back`, R1); XVI reading (a) named for spec-fidelity.
Alternative priced: the lane launching a fresh headless agent itself through `page-session`'s launcher - a second launcher the
Agent guards never see (`agent_prefix_hooks` fires on Agent calls), its tokens booked to nothing (451 T513), and an unattended
permission surface; what would reopen it: repairs that queue behind builder work for longer than a builder's dispatch.
Where the repair entries live: a file in the common git directory, not `queue.txt` in the clone, so the lane never writes in the
coordinator's tree (FR-001's purpose) - the easier route.

**Every wake whose work is integration, and who does it.** The coordinator's act on any lane line is a dispatch or a command, never
the integration itself; the work goes to a fresh agent the coordinator dispatches for that batch:

| the line D9 wakes the coordinator with | the coordinator's one act | who does the work |
|---|---|---|
| a batch landed | reads it | nobody: done |
| a repair entry (red attributed, left last, a whole batch unplaced, a carry conflict) | `make builder-next`, `make builder-brief`, dispatch | a fresh builder, given the entry's attempt file or conflict |
| a green batch whose push failed twice (Risks, "Two writers of main") | as above | a fresh builder on a repair entry of kind `integrate`, `why` `push`, naming every change of the set and the push's output: it applies them onto current `origin/main` with the carry's rules, resolves what stopped the push, and hands in once, superseding them |
| the round arbiter owed (D6 step 4: a task's second pinned red) | dispatches the `round-arbiter` agent on the bundle the lane's `make arbiter-ask` wrote | the round arbiter rules; what its ruling asks of the work (continue with a fix, or a process fault to repair) is a repair entry the lane files once `make arbiter-ruled` records the ruling (the stopped batch waits on it), `why` `arbiter`, taken by a fresh builder; the coordinator carries the ruling's id, never the gate output |
| a US5 conflict the carry cannot merge | as for a repair entry | a fresh builder (the conflict entry above) |
| the runner dead | `make lane-start` | the runner, from its log (data-model.md, "Recovery") |

So the coordinator's context takes one line and one dispatch a wake, never a conflict, a gate's output or a push's. Label: the
reviewer's rule (a fresh agent for each integration wake), the routes the easier ones (the queue the builders already take).

### D8 - the lane's states and its log

**Decision.** States are computed, never typed, from the done refs, the hand-in scratch refs, `origin/main` and the lane's log,
as the queue's are (`builder_queue.rs`): a hand-in is `waiting`, `in batch <b>`, `landed`, `ejected -> repair <r>` or
`superseded`; a batch is `forming`, `carrying`, `gating <n>`, `halving`, `pushing`, `landed`, `stopped`. One JSON line a
transition in `l7r-lane/lane.jsonl` (shapes: `data-model.md`). The done ref of a landed change is deleted by the lane after its
push; "carried" (`builder_done::uncarried`) is asked against `origin/main` instead of the clone's HEAD once the lane is the route,
so `make builder-trees` lists what waits on the lane.

**Why.** The night's causes were "partly inferred: several attempts overwrote one log" (spec). Label: convention (the pool's log
and the queue's computed states). Alternative priced: a state file the runner rewrites (lost or stale on a crash, which a log
replayed is not).

### D9 - the coordinator's wake-up: one background command, one status line a batch (FR-005)

**Decision.** `make lane-wait`, run by the coordinator with `run_in_background: true`, blocks until the lane writes a line owed
to the coordinator past its read mark - a batch landed, a repair entry (a push failed twice among them), a US5 stop, an arbiter
owed, the runner dead - prints those lines and moves the mark; who does each one's work is D7's table, never the coordinator; the session's next prompt carries the notification. A landed batch's line is one line: `lane: 461 (an example line, its figures a GUESS)
batch 7 landed T12 T14 (2 runs, 11.4 min); T13 ejected -> repair r3 (rust/gate/crates/land test)`. It has no ceiling of its own,
so it wakes the session only for what FR-005 lists. `make lane` prints the same status on demand.

**The re-arm is the tooling's, not a remembered step.** The pool-idle Stop guard (`rust/guard/src/guards/pool_idle_hooks.rs`)
gains a rule: the main session's stop is refused while the lane holds a waiting hand-in or an open batch and no `make lane-wait`
of this clone runs, its message the exact command to start with `run_in_background: true`; it ships with its suite case and its
quiet case (XVIII). The prompt hook, which already runs `sync-in` each turn, prints any unread lane lines, so a wake-up command
killed early loses nothing.

**Why.** FR-005: "once per landed batch with a short status, and otherwise only for US5's cases". Label: TAKE (R1, the platform's
background command). Unknown, so measured in phase 2: how long a background command outlives the turn that started it; if the
platform ends it at a time limit, the Stop rule and the prompt hook above catch it, and a ceiling (`LANE_WAIT_MAX`, GUESS) would
be priced then as a wake FR-005 does not list, under XVI. Cost: each wake re-reads the coordinator's context (540k to 966k tokens (measured 2026-11-27 (the transcript's usage fields))
a call on the night, the spec's Why), one per batch, the floor the spec sets. Monitor priced: a wake per output line, a watch at (Claude Code's documented limits, CONVENTION)
most 30 minutes.

### D10 - FR-001's gate-write guard and 451 T405's tree check, by construction plus a fixture

**Decision.** Once landings run only in the lane tree (D11), no gate runs in the coordinator's clone, so FR-001 holds by where
gates run. The guard's reach is already right (451 T307 part 1, T406, T430: a write is held by the tree it lands in); this
feature adds the fixture that pins it for two trees - a commit, an Edit and a `make task-add` in the clone while the lane tree's
gate runs are let through, and the same aimed into the lane tree are held - in `gate_write_hooks/tests.rs` and the suite. T405
closes by its own option (C), "every landing gated in the landing worktree at its commit, the clone free to write": a test that
the lane's gate is not voided by the clone's plan stub, a measurement record's commit, or a fetch log's append in the clone. Its
options (A) and (B) are not built: neither is needed when nothing but the landing writes in the gated tree.

**Why.** Label: measured (T405's priced table, 451 plan). The lane's own writes during its gate: none - the runner waits on
`make land` and the landing's own records are already excused or committed by the landing.

### D11 - what retires, and when (451 T302 parts 1 and 4)

**Decision.** In phase 0, T302 part 1 is confirmed by reading: `alone_owed` is asked only by `make land`, and `land-alone.sh` is
run only by `alone.rs` (a `grep` over `rust/`, `scripts/` and the Makefile, recorded). In phase 4, after the lane has carried a
like window's landings (phase 3 in use): `make land` outside the lane tree is refused, naming `make lane-start`, escape
`LAND_HERE_OK="<reason>"` (recorded, for the lane's own failure); the dirty-clone route is retired - `alone.rs` and
`land-alone.sh`'s steps 1 to 6, among them its step 2 (the task's own sections committed apart) and step 3 (the attribution of
uncommitted files by the event log, the part T302 part 4 names) - and `make land` refuses an unclean tree, naming each file (T302
part 4). `land/writers.rs` STAYS: it is 451 T242's refusal of another writer's changes and the put-back of a tick whose commit
failed (its doc), which every landing, the lane's included, still needs (FR-008). The landing worktree itself is not dropped with
land-alone: D1 adopts it as the lane's tree, it stays as the lane's, and its cache is the lane's warm cache, so 451 T525's removal
of it (and the sweep taking its cache) is replaced; phase 4 closes T525 with a pointer to D1. KEPT from `land-alone.sh`: its step 7, the clone taking a tip with its uncommitted work kept piece by piece,
moved to `scripts/take-tip.sh` and run by `sync-in` where `git pull` would stop on a dirty sectioned file, because the
coordinator's clone still takes main after every lane push. The clone's own target directory is dropped only once phase 2's
measurement shows no gate builds in it (D1). `make carry` stays for a hand carry; `make land-tooling` is unchanged (out of scope).

**Why.** T302 part 4 retires land-alone; read whole, its step 7 is the one piece the clone still needs (`sync-in` is a plain
`git pull --no-rebase`, R2). Label:
the easier route. Retiring before the lane has carried real landings would leave no route at all.

### D12 - the measurement (FR-006, FR-007, FR-010)

**Decision.** One measurement script under `dev/measurements/<date>/landing-lane/`, of the kind `tree-idle.py` is, reads the same
sources over both windows:

| figure | source | night (R3) |
|---|---|---|
| tasks landed, builder hours, landed per builder hour | `make task-time` header; pool log's held spans | 130 tasks; tree hours from the busy shares 93/98/83% (measured 2026-11-27 (tree-idle.py)) |
| cross-blocking row (US1) | `make task-time` tasks' side | 32.3 min over 130 tasks (measured 2026-11-27 (make task-time)) |
| landings' side blocking | `make task-time` | 569.1 of 772.5 min (measured 2026-11-27 (make task-time)) |
| landings refused before a gate (US2) | lane log (after); update note (before) | 19 of 50 |
| tokens per landed task, by kind and actor (FR-006) | every transcript in the window summed by actor (builders, repair builders, review agents, the coordinator), over tasks landed; the per-task T512 booking a cross-check only | coordinator 0.58M output / 616M cache read; booked to tasks 6,179k output / 1,147M cache read (04:30Z on) (measured 2026-11-27 (the transcripts)) |
| task size beside each per-task figure (FR-007) | T512's test and non-test lines, median and total | from the kept table |
| concurrency (FR-010) | trees held time-weighted from the pool log; the machine's load: the median of the sampler's `load` field over the window, against the cores (`make sampler-report`'s load column) | three trees, 93/98/83% busy (measured 2026-11-27 (tree-idle.py)); the night's load median read in phase 0 |

A window is LIKE when it holds eight hours or more of builder work, its time-weighted trees held is within 0.5 of the night's
(a GUESS knob), and its median load is within the LOAD BAND of the night's median, which phase 0 reads from the sampler's file
(FR-010: trees held AND the machine's load). The load band is a ratio: the window's median load between 0.75 and 1.25 times the
night's (a GUESS knob, `LIKE_LOAD_BAND`, recorded beside the rule as the other knobs are). A window that misses either band is not
like: the script prints both concurrencies beside every figure, and where the loads differ (outside the band, or a like window's
loads not equal), both windows' median loads are stated beside each figure as well as both trees held, so no figure is read bare. **Why.** FR-006 counts a cost "where it
lands", and 451 T513 showed the coordinator's calls are booked to no task, so only window totals over every actor can count it.
T512's fill starts at 04:30Z, so the token comparison is over 04:30Z to 14:29Z of the night, said with the figure. The script is
written and run over the night IN PHASE 0, while the night's transcripts are on disk, so the before figure exists in the form the
after figure will take; the coordinator's 0.58M / 616M (02:00Z to 15:00Z, another agent's read) is a cross-check, not the
baseline. Label:
measured sources; the likeness bands, trees held and load, each a GUESS. Alternative priced: a new `make lane-report` target (a report crate for a one-off
comparison; it reopens if the process reviewer, the next feature, wants it standing).

### D13 - the coordinator's own commits go out before a builder builds on them

**Decision.** `make builder-tree` refuses a handout while the clone's HEAD holds commits `origin/main` lacks, printing
`scripts/sync-with-main.sh done` (the DIRECT route for spec-only commits: a locked fast-forward push, no gate). The handout base
is then `origin/main` and the clone's HEAD alike.

**Why.** A builder fills a plan stub `make task-add` wrote; if that stub is only in the clone's unpushed commit, the hand-in's
apply onto `origin/main` (D3) meets a section main lacks. Pushing the coordinator's filings DIRECT waits on no gate (US1: "nothing
it writes waits on a gate"). Label: the easier route. Alternative priced: the hand-in applying onto `origin/main` plus the clone's
unpushed commits (it would carry the coordinator's commits into the builder's done commit, landing them under another task's
name). The coordinator's own code changes go to a builder; it does not push engine code from its clone. In force from phase 2
(D3's base by phase).

**A premise this moves.** The coverage reversal of 2026-11-26 rests on builders going on "from the clone's HEAD, which already
holds the carried work" (`docs/process-decisions.md`). Under the lane, staged work sits in the lane, not the clone: a closing half
still builds on its first half (D14), but a queue entry with `waits=T<n>` on ANOTHER task waits until T<n> lands (the queue reads
"neither ticked nor carried", `builder_queue.rs`, and carried now means landed). That wait is a tree idle on a landing - the
cross-blocking row - and is the reversal's own reopening measurement ("repairs after a gate hold builders back"); phase 5 reports
it apart, the entries that waited named. Label: measured where it lands; not built around before it is seen.

### D14 - done refs, successors and repairs

**Decision.** A task's next handout (a closing half, a repair) no longer waits for its earlier done commit to be carried
(`handout_waits`): the handout applies that commit onto the base without committing, so the successor builds on it, and the
successor's hand-in supersedes the earlier ref (the lane logs `superseded`). One ref a task, so the rule where the earlier commit
sits in an OPEN batch: a batch reads its changes' shas when it forms (its `batch` line), so a later hand-in moving the ref changes
no batch; the later hand-in waits until that batch ends - if it landed the earlier commit, the later one is carried on top (its
earlier half already on main, the carry's empty hunks skipped as today); if it ejected it, the later one supersedes and the
ejected one's repair entry closes as superseded (`data-model.md`). **Why.** Under the lane "carried" means landed, which
may be a batch away; a closing half held for it would idle a tree. Label: the easier route (D3's no-commit carry reused).

### D15 - where the code lives

**Decision.** `rust/gate/crates/lane/` (builds on `land`, `task`, `core`): `lane.rs` (the command line), `runner.rs` (the loop),
`batch.rs` (D5), `attribute.rs` and `halve.rs` (D6), `log.rs` (D8), `wake.rs` (D9), `repairs.rs` (D7's writer). `land/hand_in.rs`
(D3, D4) with its tests in `land/hand_in/tests.rs`; `carry.rs` gains the no-commit form; `land.rs` gains the `--hand-in` arm only.
The shared queue reads repairs in `builder_queue/repairs.rs`. `rust/gate/CLAUDE.md` gets the crate's row; the Makefile the targets
`lane-start`, `lane`, `lane-wait`, `lane-stop`, and `builder-done` pointed at the hand-in.

## The phases - each usable on its own

The session lands by hand today; each phase leaves it a working route.

**Phase 0 - the record (no engine code).** R3's baseline kept (`baseline-task-time.txt`), D12's script written and run over the
night (the token totals by actor while the transcripts exist), the load median read from `make sampler-report` over the night
(the sampler's file holds 4,647 samples stamped 02:00Z to 14:59Z of 2026-11-27, observed 2026-11-27, method: `grep -c` over
`l7r-events/samples/mem-samples.jsonl` in the common git directory), T302 part 1 confirmed by reading (D11), the stale coverage words fixed in the Makefile's `land`
help and `long_runs.rs`'s line. Verify: the record's commands re-run; `make quick`. Usable: nothing changes for the session.

**Phase 1 - the hand-in (US2, FR-002; D3, D4, D14).** `make builder-done` applies the work onto the clone's HEAD (`HAND_IN_BASE`
= `clone`, D3) and runs the first pass before it commits. The coordinator still runs `make land` by hand, but every hand-in
arrives on what it lands on, with its conflicts and its bookkeeping answered by the builder. Verify: red first - a hand-in whose plan review is owed, whose ledger row is owed, or that conflicts with
main is refused with its command, in the land crate's scratch-clone tests; a fixture shows no coverage runs; one real hand-in of
this feature's next task. Measured: landings refused before a gate, against the night's 19 of 50.

**Phase 2 - the lane (US3, FR-003, FR-005; D1, D2, D6 steps 1, 2 and 4, D7, D8, D9, D13).** The runner, the adopted tree,
batches of hand-ins run through `make land` there, the one status line, the Stop rule that keeps `make lane-wait` armed;
`HAND_IN_BASE` = `origin` and D13 switched on. A red batch: an attributed change is ejected as a repair entry and the rest runs
again; a red the record cannot place ejects the whole batch as one repair entry (D6, "By phase"), so no batch re-forms from the
same hand-ins and each of its tasks takes one pin (D6 step 4). The coordinator dispatches repair entries like any other
and repairs nothing itself, so US1 holds from here (D7's table, a push failed twice included). Verify: the end-to-end test (two
hand-ins, one batch, one push, the refs deleted, the status line; an attributed red ejects one change and lands the other); red
first, the tripwire by task reached: that ejected task's repair handed in red again in a later batch stops the lane, files no
second repair and owes the round arbiter (its `make arbiter-ask` bundle written, one owed line), and a green batch whose push
fails twice files one `integrate` repair entry; red first, the stand-down's reach: a by-hand `make land` in the clone carrying
`L7R_LANE_BATCH` (outside the lane's tree, its batch id open or not) is still stopped on its second red by `second_red_gate`, and
a run in the lane's tree with a batch id `lane.jsonl` holds no open batch for is stopped too (in `tree/state.rs`'s tests and the
lane crate's end-to-end test); a real batch of this feature's tasks;
measured: the lane tree's first gate minutes (D1), a background command's lifetime (D9).

**Phase 3 - the whole red path (US4, US5, FR-004; D5, D6 step 3, D7's conflict entries, 451 T415).** The halving in place of the
whole-batch ejection, a carry conflict as a repair entry, the batch knobs. Verify: red first - a batch whose red the record
cannot place lands its good changes in at most ceil(log2 n) + 1 further runs (n = 4 and 6, D6's table); a carry conflict becomes a
repair entry; the tripwire by task, both ways: it stays quiet through the n = 6 halving of D6's table whose bad change is C (the
batch's first red run and then the red half [A B C], two reds in a row that pin no task, before C is ejected), and it fires when a task left last by one halving is left last
again by a later batch's halving (one task ejected twice), the lane stopped and the round arbiter owed.

**Phase 4 - the one route (FR-001, FR-008; D10, D11, 451 T302 part 4, T307, T405).** The guard fixture over two trees, T405's
option (C) test, `make land` refused outside the lane tree, the dirty-clone route retired, step 7 kept as `take-tip.sh`, the
`-land` worktree kept as the lane's tree with its cache (D1), the taken-over 451 tasks closed in 451 with a pointer here, and 451
T525 closed with a pointer to D1 (its removal replaced: the worktree stays as the lane's). Verify: the guard suite; `make hooks-test`; a landing refused in the clone
with its command; the lane's next batch green.

**Phase 5 - the after-measurement (FR-006, FR-007, FR-010; D12).** Over the first like window after phase 3 is the route, chosen by
D12's likeness test: the first span of eight hours or more of builder work whose trees held is within 0.5 of the night's AND whose
median load is within the load band of the night's (both GUESS knobs, D12). Every figure of D12's table beside the night's, with
both windows' trees held and median load stated beside each figure where they differ. Verify: the figures re-derived from their recorded command
outputs; the GM reads the comparison.

## What retires (451 T302 part 4) and when

| what | when | why then |
|---|---|---|
| `make builder-done`'s `make land` line and `make carry` as the usual route | phase 2 | the lane takes them |
| T415's proposed `make land` line | phase 3 | the lane runs the batch itself (D5) |
| `alone.rs`, `land-alone.sh` steps 1-6 (its attribution of uncommitted files, step 3, among them) | phase 4 | a clean-tree landing in the lane's tree is the only route |
| `make land` in a session clone | phase 4 | refused, `LAND_HERE_OK` for a broken lane |
| NOT retired: the `-land` worktree and its cache (451 T525's removal replaced) | stays | it is the lane's tree and the lane's warm cache (D1); phase 4 closes T525 with a pointer |
| the clone's own target directory | after phase 2's measurement | only if no gate builds there |

## The 451 parts this feature takes over

T302 parts 1 and 4 (D11), T307 parts 1-3 (part 1's guard built, its fixture D10; part 2's push table already in the first pass,
kept in both forms D4; part 3's one gate for several ready tasks is the lane's batch D5), T308's two-tier split (D3, D4: the fast
tier stays the builder's, the full gate the lane's; its "repaired by whoever is cheapest" replaced by D7, its builder coverage
replaced by none), T405 (D10), T415 (D5). Each is closed in 451 with a pointer here when this feature's tasks are written.
Not taken over but answered: 451 T525 (the `-land` worktree's removal when land-alone retires) is replaced by D1 - the worktree
stays as the lane's tree, its cache the lane's - and phase 4 closes it with a pointer.

## Risks

- **Two writers of main.** The lane's pushes and the coordinator's DIRECT pushes meet under the one lock; a `tasks.md` the
  coordinator filed into while the lane ticked can make the push's pull conflict, and the push then reverts its ticks (today's
  behavior). The lane fetches, brings its tree to the new main and runs the batch again once; a second failure files the set as
  one repair entry of kind `integrate` (`why` `push`, D7's table), whose line wakes the coordinator to dispatch a fresh builder for
  it; the coordinator does not push, carry or resolve it. Measured in phase 2 by the lane log.
- **The hand-in moves cost onto builders** (fetch, apply, first pass, conflict turns). FR-006 and FR-007 judge it; if builder
  minutes a task rise past what the coordinator saved, phase 5 says so.
- **A wrong attribution** ejects a good change: its repair builder's hand-in then passes at once, costing one builder dispatch;
  counted on the lane log as a repair whose hand-in changed nothing.
- **A wake that needs judgment** goes to a fresh agent the coordinator dispatches for that batch (D7's table: a repair builder, or
  the round arbiter on the lane's bundle); the coordinator's turns hold its line and its dispatch only.

## Found and left

- The Makefile's `land` help and `long_runs.rs`'s gate line say the changed modules' coverage runs beside the gate, which
  `long_runs.rs`'s own doc says is gone. Visible effect: a reader is told a check runs that does not. Fixed in phase 0.

## Project Structure

```text
specs/461-landing-lane/
├── spec.md, request.md
├── plan.md                 # this file
├── research.md             # R1 reuse, R2 code, R3 baseline
├── baseline-task-time.txt  # R3's recorded command output
├── data-model.md           # the lane's entries, batches, states, log line
├── quickstart.md           # the coordinator's and a builder's use, and how to test
└── contracts/lane-cli.md   # the commands and their exits

rust/gate/crates/lane/src/{lib.rs, lane.rs, runner.rs, batch.rs, attribute.rs, halve.rs, log.rs, wake.rs, repairs.rs}
rust/gate/crates/land/src/land/{hand_in.rs, hand_in/tests.rs, carry.rs (no-commit form), cheap.rs (the mode)}
rust/gate/crates/task/src/{builder_done.rs (uncarried against origin/main), builder_tree.rs (D13, D14)}
rust/gate/crates/tree/src/state.rs (a lane run left to the lane's tripwire by task, D6 step 4)
rust/guard/shared/src/builder_queue/repairs.rs; rust/guard/src/guards/gate_write_hooks/tests.rs (D10)
scripts/take-tip.sh (land-alone.sh step 7); Makefile (lane targets, builder-done)
```

**Structure Decision**: one new gate crate for the lane, the hand-in in the land crate (it builds on `task`), no new outside
dependency.

## Complexity Tracking

No Constitution Check violation; the three XVI readings above go to spec-fidelity's plan review.

## Knobs this plan takes (the record could not settle them)

| knob | value | label |
|---|---|---|
| `L7R_LANE_TREE` | `<clone>-land`, adopted | the easier route (D1) |
| `LANE_MAX` | 6 | GUESS, seeded from the two-tier ceiling; trial 458 resets it (D5) |
| `LANE_WAIT_S` | 0 | GUESS (D5) |
| `LANE_RETRY` | 0 | GUESS (D6) |
| `LANE_IDLE_S` | 3600 | GUESS (D2) |
| `HAND_IN_BASE` | `clone` in phase 1, `origin` from phase 2 | the easier route by phase (D3) |
| `LANE_WAIT_MAX` | none (no ceiling) | priced only if phase 2 measures a time limit on background commands (D9) |
| `LANE_REPAIR_FIRST` | 1 | GUESS (D7) |
| like-window band | trees held within 0.5 | GUESS (D12) |
| `LIKE_LOAD_BAND` | median load 0.75 to 1.25 times the night's | GUESS (D12) |

D9's Stop rule (the main session's stop refused while the lane holds a waiting hand-in or an open batch and no `make lane-wait` of this clone runs) lives in the guard's `pool_idle_hooks.rs`, with a case in its suite.

### T01 (D12's token figure, taken while the night's transcripts are on disk)

- **Approach**: A single measurement script, `dev/measurements/2026-11-27/461-t01-night-tokens/night-tokens.py`, of the same
  kind as `tree-idle.py`. It reads the coordinator's transcript and every subagent transcript under it, workflow agents
  included. It counts each call once, keyed by message id. It sums four kinds: output, fresh input, cache read and cache write.
  The advisor's own calls go in separate columns.
  - **Actors.** Builders, repair builders, review agents, the coordinator and page sessions.
  - **Booking.** A builder books to the feature and task in its `BUILDER-BRIEF` marker. An agent a builder dispatched books
    through its `parentAgentId` chain. Any other agent books to a task only where its description names exactly one feature
    and task. The coordinator books to no task.
  - **The task list.** The script takes a `make task-time` output and reads the window's landed tasks, with their test and
    non-test lines, from its T512 table.
  - **Two windows.** The headline is 04:30Z to 14:29Z (D12, T512's fill). The brief also asked for the spec's whole window,
    02:00Z to 14:29Z, so the script was run over that too.
  - **The 04:30Z figure.** In this window 120 tasks landed, and window totals per landed task are 44.5k output, 0.14k fresh
    input, 11.21M cache read and 172k cache write, of which builders account for 33.6k output and 7.08M cache read, review
    agents 7.2k and 0.18M, and the coordinator 3.6k and 3.95M (observed 2026-11-27, method: `night-tokens.py` over the
    transcripts, `output-0430-1429.txt`).
  - **The coordinator's share.** The coordinator carries 35.2% of the window's cache read and 8.2% of its output
    (observed 2026-11-27, method: that output's totals divided).
  - **No repair builders or page sessions.** None ran in either window (observed 2026-11-27, method: the script's
    classification, with its builder audit list printed).
  - **The record.** It is `results.md`, alongside both windows' outputs, the per-call extract `calls-0200-1429.tsv.gz` (no content,
    so the record re-derives once the transcripts are gone) and the kept cut of the 04:30Z `make task-time` run.
  - **The directory.** It follows the brief (`461-t01-night-tokens/`), not T01's line (`landing-lane/`). T02 extends this
    script where it is.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: a measurement, no engine or tooling code | - | - | - | - |

### T01 Approach (checklist part A)

1. **The goal, in the world.** Feature 461's before figure for FR-006 exists in the form phase 5's after figure will take.
   That form is tokens per landed task by actor and kind, as window totals over every actor, with the per-task booking beside
   it. It also has to exist while the night's transcripts are still on disk.
2. **The constraints.** FR-006 (a cost is counted where it lands), FR-007 (task size beside each per-task figure), D12 (one
   script, a window over every actor, T512 as a cross-check only, 04:30Z on) and R3 (the night's window and its 130 tasks).
3. **Where each comes from.** R: plan D12 and research R3. O: 451 T513's finding that most coordinator calls book to no task,
   and T512's fill starting at 04:30Z. G: none beyond the spec's.
4. **Do they describe the world here?** Yes, with checks.
   - Duplicate records of one message id carry identical usage, measured 2026-11-27 (every in-window record compared).
   - The top-level usage leaves out the advisor's iterations, measured 2026-11-27 (sample calls' iterations summed).
   - The coordinator's count agrees with the update note within 1.5%, at 1,016 calls, 0.589M output and 624.7M cache read
     over 02:00Z to 15:00Z, measured 2026-11-27 (the same dedupe over that span).
5. **The order.** Before T02, which extends this script with D12's other figures, and before any phase 1 edit.
6. **The exits.** Green: the outputs are written and the reconciliation holds for every actor (booked to a landed task, plus
   booked to a task not landed, plus unbooked, equals the total). Red: what failed is recorded and the task set down. A claim
   that it cannot be done is ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Both windows' outputs are kept, and the totals re-derive from the extract with `results.md`'s `zcat |
   awk` line to within one call. The one-call difference is a message whose records fall on both sides of 04:30:00 (observed
   2026-11-27, method: that line run).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing to fix. A measurement changes no behavior.

**Found and left?** none. The per-task T512 booking is higher than this script's figure, at 5.62M output against 4.71M over
the same 120 tasks (observed 2026-11-27, method: the outputs' cross-check sections), a gap from T512's design, not a defect:
it adds the coordinator's booked calls and counts a builder's calls from before the window. It is stated in `results.md` as
a limit.

**Performance work?** Yes, as a `[perf]` measurement (451 FR-013). It measures where the tokens go, but it changes no
engine speed, so the performance checklist does not apply.



### T01 part B (2026-11-27T18:07Z)

1. **What exactly is refusing?** The landing gate's `hooks-test`: an unreviewed guard message, gate-write-hooks refuse (key
   07af561d8fed9177), rendered by 451 T530's new test case. The same rule both times: the two reds at 18:02:27Z and 18:03:02Z
   came 35 seconds apart on one fault (the round arbiter's ruling, red-gate@2026-11-27T18:03:02Z).
2. **A3 again, for that rule.** O: the gate's own output, read; the rule is the guard-message check (451 T170), every rendered
   message held to a recorded verdict.
3. **A4 again.** Yes: the message was new, and unreviewed - the rule describes the case.
4. **Is the next fix moving something placed earlier to suit something placed later?** No: the fix was the message's wording and
   its review, not T01's measurement.
5. **Tuning or changing?** Neither: one wording change at message-check's BREVITY finding, then ten renderings checked PASS.
6. **The one-sentence test.** "A new guard message is reviewed before it lands" - the GM would not ask why.
7. **The next step is a measurement.** `make hooks-test` over every suite with the new wording, green, before the next landing.
8. **Before offering routes.** None offered: the arbiter ruled `continue`.
9. **After a ruling.** The next step is the one it names: land once more with the shortened wording in place, and read any red
   before starting another landing; 461 T01 and T05 not queued behind an unread red.

<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T03 (D11: 451 T302 part 1, confirmed by reading before phase 4 retires land-alone)

- **Approach**: nothing changes; a grep over `rust/`, `scripts/` and the Makefile, kept as `dev/measurements/2026-11-27/461-t03-land-alone-callers/callers.sh`, its output `output.txt` beside it and read in `results.md` (read 2026-11-27 at f412c319b7, method: that script). `alone_owed` is asked once, in `Land::land`; `land-alone.sh` is run once, by `alone.rs`'s `SCRIPT`; `Land::land` is reached only by `make land` and `make land-batch` (the same command), the other arms of `land::cli` (`--carry`, `--stop`, `--unfinished`) returning before it; a builder lands nothing (`make builder-done` commits its tree, the session carries it). So only a session's own clone lands alone: T302 part 1 is closed, a pointer written on 451 T302's box, which stays open for parts 2 and 3 (part 4 is T30).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the read | n/a: nothing changed | n/a | n/a | n/a |

### T03 Approach (checklist part A)

1. **The goal, in the world.** The record says, with its command, that land-alone runs only from a session's own clone, so T30 retires it knowing every caller.
2. **The constraints.** D11; 451 T302 part 1; FR-008 (`land/writers.rs` stays, untouched here).
3. **Where each comes from.** G: the GM's confirmation of 2026-11-26 that every session has its own clone, quoted on 451 T302's line; O: the grep, `output.txt`.
4. **Do they describe the world here?** Yes: the grep was run over this tree at f412c319b7.
5. **The order.** Phase 0, before T30 (which retires what the grep found).
6. **The exits.** Green: the recorded grep re-run gives the same lines. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one grep, one read of `land::cli`.
8. **The budget.** One landing.
9. **Done, measured.** `bash dev/measurements/2026-11-27/461-t03-land-alone-callers/callers.sh | diff - dev/measurements/2026-11-27/461-t03-land-alone-callers/output.txt` is empty.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing: no code changes; not a defect.

**Found and left?**
- `scripts/gates/review-tree.sh` lines 109-110 read `land-alone.sh`'s `PYLIB` (its step 3, the attribution) and run its `split`; once T30 removes step 3, `make review-tree` dies "holds no PYLIB" - a review bundle that cannot be built. Not fixed here: it moves code T30 is about to retire, and where the split should live is that task's choice, not a read's. Filed as T36; lands before T30.

**Performance work?** no.

### T03 part B (2026-11-27T19:13Z)

1. **What exactly is refusing?** The batch gate's `static`, red twice in a row on two causes (the round arbiter's ruling,
   red-gate@2026-11-27T19:10:08Z): first coverage gaps in 461 T07's `hand_in.rs` and 451 T526's line; second one failure of the
   rustc crate's `drain::a_late_reader_with_no_holder_is_waited_for_not_cut` (451 T364's) under the coverage run.
2. **A3 again, for that rule.** O: the gate's output, read; the rule is the crate coverage bar and the crate's own tests.
3. **A4 again.** The coverage bar describes the case; the drain test's failure is in no file the batch touched - re-run only because
   the batch changed `core`, which the rustc crate builds on.
4. **Is the next fix moving something placed earlier to suit something placed later?** No: coverage repairs added tests; the flake
   is filed apart.
5. **Tuning or changing?** Neither: two repairs by builders in their own trees, the batch's coverage run clean before the gate.
6. **The one-sentence test.** "New code is covered by its own tests; a test that fails once on good work is filed" - no question.
7. **The next step is a measurement.** The next gate as the batch stands; the drain test run 5 of 5 alone at load 14 to 15 passed
   (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/rustc ONLY=` five times).
8. **Before offering routes.** None offered: the arbiter ruled `continue`.
9. **After a ruling.** The step it names: run the next gate; if the drain test goes red again, fix it before a third run; the observed
   failure filed as a 451 task with its hypothesis either way.

<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T08 to T08 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T09 to T09 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T10 (phase 1's measurement on real work, US2 and SC-002: the hand-in in use since T43 landed)

- **Approach**: A measurement script, `dev/measurements/2026-11-27/461-t10-phase1/phase1.py`, reuses T02's `night-figures.py`
  for the landings, the pool replay and the load, so the after figures count as the night's did. Its record is that
  directory's `results.md`; nothing in the engine or the tooling changed.
  - **Windows.** 19:57:00Z (T08 and T43 landed, 19:56:47Z) to 23:03:20Z (before this task's take), 3.11 h, and 21:06:47Z (T44
    landed) to 23:03:20Z beside it (observed 2026-11-27, method: the event log's `make land` end rows and the pool log).
  - **Hand-ins.** 27 pool `done` rows, all `"handed_in": true`, all run by a builder and none by the coordinator, on 22 tasks or
    bundles; 21:06Z on, 22 on 18 (observed 2026-11-27, method: `phase1.py figures` over the kept extracts,
    `output-1957-2303.txt` and `output-2106-2303.txt`, each done row joined to the builder-done call that wrote it).
  - **Refused at hand-in.** Of 34 builder calls, 7 handed nothing in, on 7 of 23 tasks. 4 were conflicts and 3 first-pass
    refusals: a ledger row, a feature-close report, and a plan review owed. Each named its fixing command or its paths. 3 of 4
    conflicts were resolved by the builder that met them, the fourth by a fresh closing half from a handoff, and none by the
    coordinator. No hand-in ran a coverage step (observed 2026-11-27, method: the same outputs; the outcomes and reasons from
    the calls' own tool results in the subagent transcripts, found by call id, a second source the logs cannot give).
  - **What the logs cannot show.** The event log's foreground tool rows carry no exit code, and the pool log writes nothing on
    a refused or conflicted hand-in. So the logs show that a call handed nothing in, never why, and never a conflict resolved.
  - **Landings refused before a gate.** 0 of 7 attempts (5 landed, 2 gates red) over 19:57Z on, and 0 of 4 over 21:06Z on,
    against the night's 17 of 39. Trees held were 2.94 and 3.02 against 3.19, and the median load 9.4 and 10.3 against 14.1
    on 22 cores (observed 2026-11-27, method: `night-figures.py`'s `landings()` and replay through `phase1.py`, the night's
    from T02's record). The window is not LIKE the night, 3.11 h long with its load below 10.6, and seven attempts agree with
    US2's "well under" without establishing it: at an 11% rate, none in seven comes 44% of the time (observed 2026-11-27,
    method: 0.89^7, the likeness rule of `night-figures.py`).
  - **The one real hand-in.** This task's own, a measurement's under T44's rule. Its outcome is in the builder's report, since
    the record it commits cannot hold it.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: a measurement, no engine or tooling code | - | - | - | - |

### T10 Approach (checklist part A)

1. **The goal, in the world.** Phase 1's after figures (hand-ins, refusals at hand-in and their causes, conflicts a builder
   resolved, landings refused before a gate) recorded with their concurrency, re-derivable from kept extracts.
2. **The constraints.** US2 and SC-002; FR-010 (every figure beside its concurrency); T02's counting rule for landings.
3. **Where each comes from.** R: the spec's US2, SC-002 and FR-010; T02's record. O: this task's runs.
4. **Do they describe the world here?** Measured on the pool log, the event log, the sampler and the transcripts over the
   windows above (observed 2026-11-27, method: `phase1.py`; live and kept runs agree but for the transcript outcomes).
5. **The order.** After T08, T43 and T44 landed; before T31, which reads the like window.
6. **The exits.** Green: the record written and its counts re-derived from its outputs. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the logs' gaps are named, and the transcripts fill them as a labeled second source.
8. **The budget.** One landing.
9. **Done, measured.** `results.md` with the outputs it cites, the figures re-derived by the commands it lists.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing: a measurement, no fix.

**Found and left?**
- The likeness test's trees held counts the lane's own worktree, adopted `lane` at 21:08:09Z and never released, as a held
  builder tree: 3.55 against 2.94 over 19:57Z on, and the sampler's `held` lists `lane` in 215 of 1,065 samples (observed
  2026-11-27, method: `phase1.py` with and without the lane tree, and each sample's `held` against the replay). T31's like
  window would read about one tree high. Not fixed here: a measurement changes no tooling. Filed as T59; lands before T31.
- A build half's hand-in is refused for the feature-close ask, which only its closing half can answer: 451 T537's build half at
  22:06:03Z (observed 2026-11-27, method: that call's tool result). T44 puts off a build half's plan asks by its kind, but not
  this one. Not fixed here: a measurement changes no tooling. Filed as T60; lands before T31.

**Performance work?** yes - a measurement of where the landings' and the hand-ins' time and refusals go (451 FR-013: a
measurement task counts).

### T11 (D2, D8, D15: phase 2's first task, the lane crate and its log, which T12-T22 build on)

- **Approach**: a new crate `rust/gate/crates/lane/` (`l7r_gate_lane`, on `core`, `task` and the guard's `shared`; `land` joins
  with the runner, T12, which runs `make land`): `lane.rs` the command line of `contracts/lane-cli.md`, of which T11 builds
  `status` (`make lane`, `l7r-gate lane status`), read only - no fetch, nothing created, an empty lane exit 0; `start`, `wait`,
  `stop` and `--work` are refused with the usage until T12 and the wake-up build them. `log.rs`: one JSON line a transition in
  `l7r-lane/lane.jsonl` of the git common directory, only data-model.md's ten events, each line one `write_all` with its newline,
  a torn or foreign line skipped on reading; and the COMPUTED states. A HAND-IN is a pool-log `done` line with `"handed_in": true`,
  one a commit (a bundle's tasks share one; the live log's `451 T528,T529` is one), enumerated from the pool log rather than the
  refs, because the refs alone cannot show `landed` (the lane deletes the ref after its push) or `superseded` (one ref a task),
  and kept while still the lane's: a done ref names its commit, or a lane-log line does. Its state is the first of data-model.md's
  order that holds; `landed` is `task`'s carried rule asked of `origin/main` - `builder_done::held_by(clone, rev, commits)`, a new
  public door over the same author's-time-and-subject reading `uncarried` asks of HEAD (one rule, `keys_since`, shared), so the
  rule is not written twice - or a `landed` line listing it, which still holds once the object is pruned. A BATCH's state comes
  from its own lines through one function, `state_of`, so T12 and T14 can move the mapping in one place. The binary's dispatch
  (`src/lib.rs`, a `here()` helper shared with `land`, `claim` and `make-docs` to keep `cli` under clippy's `too_many_lines` lint), the
  Makefile's `lane` target, `docs/make-targets.html` regenerated, and the crate's row in `rust/gate/CLAUDE.md`.
- **The data model's silences, each read the easier way** (labeled in `log.rs`'s doc beside the mapping): (1) `forming` has no
  event before the `batch` line (D5's cut takes no time at `LANE_WAIT_S` = 0), so a batch in the log is `carrying` from its
  `batch` line - a deliberate deviation from data-model.md's list, T14 adding the event if it adds a wait; (2) `stopped` is a
  `stop` line naming the batch (the arbiter owed, D6 step 4), and a killed runner writes no line, so its batch is resumed as
  Recovery says, not stopped; (3) the hand-in scratch refs mark a hand-in not yet made and add no state; (4) every batch line
  carries `batch` (data-model.md's `run` example does); (5) a commit is named whole or by a prefix of seven or more (a run's `set`
  holds short shas). "Repairs open" are the `eject` lines' `repair` ids no hand-in's `repair_of` answers; `repairs.jsonl`'s reader
  is D7's writer's task, not this one.
- Red first (2026-11-27, `make rust-test CRATE=rust/gate ONLY=tests::the_lane_is_a_subcommand` on the old dispatch): 0 passed, 1
  failed - `l7r-gate: no subcommand lane`, exit 2 against 0. Green: the lane crate 11 of 11, task 151 of 151 (the new
  `held_by_asks_the_carried_rule_of_any_rev`), the binary 10 of 10, `checks`' `guard_deps` 8 of 8; `make builder-checks
  CRATE="rust/gate/crates/lane rust/gate/crates/task rust/gate"` clean. Live (2026-11-27, `make lane` in this tree over the
  clone's real pool log): `0 hand-in(s) on the lane` - every phase-1 hand-in's ref was deleted by its carry, so none is listed as
  waiting - and no `l7r-lane/` created.

### T11 Approach (checklist part A)

1. **The goal, in the world.** `make lane` tells the coordinator, from any tree of the clone, what waits on the lane, the open
   batch and its state, the last landed batch and the repairs open, from records a crash cannot leave stale; the later phase-2
   tasks write the log this reads.
2. **The constraints.** D2 (the crate and its commands), D8 (states computed, never typed, a JSON line for each transition), D15 (where
   the code lives), data-model.md (the events, the hand-in's and the batch's states and their order), contracts/lane-cli.md
   (`make lane` prints, exit 0), rust/gate/CLAUDE.md (a crate's wiring, its testkit dev-dependencies, every line covered by its own tests).
3. **Where each comes from.** R: plan.md D2, D8, D15; data-model.md; contracts/lane-cli.md. O: the live pool log's `done` lines
   (`"handed_in": true`, `detail` `<feature> <tasks>`, a bundle one commit), read 2026-11-27.
4. **Do they describe the world here?** Yes: the done refs are `refs/l7r/done/<feature key>-<task>` and the pool log is
   `builder-pool.log` in the common directory (read from `builder_done.rs` and the live log, 2026-11-27); the live `make lane`
   lists none of the carried phase-1 hand-ins.
5. **The order.** After T08 (the hand-in writes `"handed_in": true`); before T12-T22, which build on this crate.
6. **The exits.** Green: the lane crate's tests over each state of data-model.md and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one pass over the data model's states, the gaps above labeled.
8. **The budget.** One landing.
9. **Done, measured.** The tests above green, `make lane` run live with no hand-in misread.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: new code, no defect fixed.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: T12 to T11 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T14 (D5, D6 step 1, D8, D14: phase 2's batch, the runner's step and resume that T12 left as stand-ins; lands after T12 and T13)

- **Approach**: `rust/gate/crates/lane/src/batch.rs` (new, with `batch/tests.rs`) forms the batch; `runner/run.rs` (new, with
  `run/tests.rs`) runs it as the step and resume T12's `work_cli` calls; `runner.rs`'s spawn strips the caller's environment and
  runs the lane tree's own wrapper (T12's "For T14"). Built in two halves (2026-11-27); the build half's handoff is
  `<clone git dir>/l7r-handoffs/T14-build.md`. `dev/audits/lane-batch-cap.md` covers `LANE_MAX`; the lane crate's row in
  `rust/gate/CLAUDE.md` names the modules.
- **Decision 1 - D5's formation, literally.** `form(&World, LANE_MAX)` takes the `waiting` hand-ins in hand-in order, starts at
  the oldest, and takes the run of its feature straight after it, cut at the first hand-in of another feature, at one D14 holds,
  or at `LANE_MAX` changes. D14's open-batch half: a hand-in is held while an open batch carries another hand-in of its feature
  sharing one of its tasks; where the OLDEST waiting hand-in is held, no batch forms (none jumps ahead of it). `next_id` is
  `<feature>-<n>`, n one past the feature's highest `batch` line. A batch reads its changes' full shas once, on its `batch` line, so
  a later hand-in moves no batch. Label: the literal order (D5); the cut at a held hand-in the easier route (D5's own label).
- **Decision 2 - `LANE_MAX` = 6.** GUESS knob, beside its constant and in `dev/audits/lane-batch-cap.md` (seed: the two-tier
  threshold's "about six tasks", `docs/process-decisions.md`; trial 458's verdict resets it). `LANE_WAIT_S` = 0 has no constant: the
  step forms as soon as no batch is open. Label: GUESS.
- **Decision 3 - the run's four steps** (`run_batch`): (1) the lane's tree brought to `origin/main` by T13's `builder_tree::cli(["lane"])`,
  and the changes `origin/main` already holds dropped (a resume after the push lands with no run); (2) each remaining change carried
  by `make carry COMMIT=<sha>` in the lane's tree, oldest first, one `carry` line - the lane carries the batch's OWN shas, since
  `make land`'s `carry_done` reads the done refs live; (3) `make land F=<feature> T="<tasks>" NOTE="<subjects; ...> - landed by the
  lane, batch <b>"` there, its stdout and stderr the attempt's own file `l7r-lane/attempts/<b>-<n>.log`, n continuing from the
  batch's `run` lines (D6 step 1, never overwritten), one `run` line and a `push` line where it pushed; (4) each done ref deleted
  only where it still names the batch's sha (`update-ref -d <ref> <sha>`: a later hand-in keeps its ref; the linked tree's carry
  keeps the refs, 451 T404), then the `landed` line and ONE `owed` line, `lane: batch <b> landed - <feature> <tasks> (<k>
  change(s), <r> run(s), <m> minutes)`, which T20 prints. A carry that stops, or a landing that ends red or refused, writes its line
  (a red one also ONE `owed` line naming the attempt file) and returns an error: the runner stops with `error: ...` and the batch
  stays OPEN, so nothing re-runs each poll and the next `make lane-start` resumes it as attempt n+1. A make that cannot start counts
  as exit -1 on the same path. Label: the easier route (D6 step 1's green path; T15, phase 3 and T19 replace the red, the carry's
  and the push's branches).
- **Decision 4 - a non-zero exit is read against `origin/main`.** GNU make ends 2 for any failed recipe, so the landing's own exit 3
  (pushed, other sessions' edits merged) reaches the runner as 2, never 3 (observed 2026-11-27, a scratch Makefile under GNU Make
  4.4.1: a recipe's `exit 3` printed `Error 3` and make ended 2). On any exit but 0 the runner fetches `origin main` in the
  lane's tree and asks `held_by(tree, "refs/remotes/origin/main", <the batch's shas>)`: every change there is a push (a `push` line
  with the observed code), and the batch goes on to step 4; otherwise it is the red branch. The push's own code is not separable from
  make land's today (T19's). Label: the easier route (main's content is the truth, as Recovery already asks it).
- **Decision 5 - the stripped environment.** `run::STRIPPED`, removed from both the runner's spawn (`spawn_command`) and each
  `make` the run starts: T12's five (`MSG`, `GUARD`, `T`, `F`, `L7R_GATE_TREE`) and make's own `MAKEFLAGS`, `MAKEOVERRIDES`,
  `MFLAGS`, `MAKELEVEL`, because a runner a hand-in started inherits `make builder-done T= F= MSG=`'s environment and a variable on
  that make's command line reaches a grandchild make through `MAKEFLAGS`. Observed 2026-11-27, method: a scratch Makefile under GNU
  Make 4.4.1 (`make -f outer.mk T=T14 F=461`, its recipe running `sh -c "$(MAKE) -f inner.mk show"`): the grandchild printed
  `T=[T14] F=[461]`, and `env -u MAKEFLAGS -u MAKEOVERRIDES -u MFLAGS -u MAKELEVEL` left its child an empty `MAKEFLAGS`. Label:
  convention (GNU make's own variable passing, observed).
- **Decision 6 - the lane tree's own wrapper.** `runner_exe(common, fallback)` returns the registry's lane tree's
  `scripts/gates/l7r-gate.sh` when the lane's tree and that file exist, else `fallback` (`current_exe()`: phase 1, a scratch
  repository); both `lane start` and `on_hand_in` use it. The wrapper `exec`s `<target>/tool/l7r-gate lane --work <common>`, so the
  stall watchdog's `runs_lane` still matches. Label: the easier route (T12's "For T14"). Its rebuild may outlast `START_WAIT_S`:
  filed as T51 (Found and left).
- **Decision 7 - `NOTE=` on make's command line.** The Makefile's `land: export LAND_NOTE = $(NOTE)` overwrites an inherited
  `LAND_NOTE`, so the run passes `NOTE=` as a make argument; it reaches the binary as `LAND_NOTE`, as contracts/lane-cli.md names
  it. `SPECIFY_FEATURE`, `SPECIFY_FEATURE_DIRECTORY` and `L7R_LANE_BATCH` go in the environment. Label: convention (the Makefile's
  own route for the variable).
- **Decision 8 - `L7R_LAND_ALONE=1` and `SYNC_BACKUP=off`, as `land-alone.sh` sets them** for its own landing in this same `-land`
  worktree (its line 572). Their non-test readers (found by grep, 2026-11-27): `land/alone.rs`'s `INNER` (the tree is not sent to
  land alone again - it is the landing); `core/build.rs`'s `LANDING` (a claims answer from a mixed build owed again, right for a
  clean lane tree); `sync-with-main.sh` line 564 (no backup push from a worktree that is no clone). Both kept. Label: convention
  (`land-alone.sh`'s own settings for the same tree).
- **The flake the build half saw.** `runner::tests::a_second_start_is_a_no_op_naming_the_first_s_pid_and_stop_now_ends_it` failed
  once in the build half's first `make builder-checks` (its last `stop NOW` found a runner). Measured 2026-11-27, `make rust-test
  CRATE=rust/gate/crates/lane ONLY="runner"` ten times in a row at load 16-27 on 22 cores: 2 red of 10 - that test once (its last
  `stop NOW` reading `stopped at once` for the runner killed before) and `the_work_command_holds_the_lock_..._leaves_quietly` once
  (`held` true after `work_cli` returned). The cause: a `flock` lock belongs to the open file description, so a close frees it only
  once every copy is closed, and the test binary's other threads fork `git`, `make` and `sh` all the while, each child holding a
  copy of every descriptor until its `exec` - so the probe's own lock (`held` takes it for an instant where it is free) and the ended
  runner's lock outlived their close. Fixed in `runner.rs`: `free` (the probe) and `release` (the runner's end) let the lock go by
  `flock -u` before the close, which frees it whatever copies exist; `held`'s doc no longer says it is let go as the file closes. The
  wrong outcome fixed: `make lane-stop` or `make lane-start` reading a runner that has ended (a stop naming a dead pid, a start
  saying `already runs`) where the caller is a threaded process. Red first in
  `runner::tests::a_probe_and_an_ended_runner_leave_no_lock_behind_a_copy_of_their_descriptor`, which keeps a `try_clone` of the
  descriptor alive across the probe and across the release: on the old code 0 passed, 1 failed (at the probe's assertion); with only
  the probe fixed, 0 passed, 1 failed (at the release's); after both, 1 of 1, and `ONLY="runner"` 23 of 23. After the fix,
  the same `ONLY="runner"` run thirty times in a row at load 22-52 on 22 cores: 30 green of 30 (0 red, against 2 of 10 before).
  Label: convention (`flock(1)`'s `-u`; the lock's ownership by the open file description is `flock(2)`'s).
- **Two things the build half changed beside its own modules.** T12's test
  `the_work_command_sees_a_real_hand_in_and_resumes_an_open_batch_of_the_log` now expects, with no lane's tree in the pool, the
  resume to fail: the runner exits 1 with `stop why "error: lane: batch 461-1: builder-tree lane: ..."` and the batch stays open
  (T12's stand-in resume had succeeded). `log::names` became `pub(crate)` for `batch.rs`.
- **Phase 1's base.** A phase-1 hand-in's base is the clone's HEAD, so carried onto `origin/main` it may conflict; by design until
  T22, since in phase 1 the runner starts only by `make lane-start` (T12's Decision 6), and a conflict ends the step on the carry's
  seam above.
- Red first (2026-11-27, the build half): `batch::tests` against stubs, 0 passed, 3 failed; after, 3 of 3. `runner::run::tests`
  against stubs, 0 passed, 6 failed; after, 6 of 6; the exit-3-as-2 test under the old `code == 0 || code == 3` rule, 6 passed, 1
  failed; after, 7 of 7. `runner::tests::the_runner_runs_the_lane_tree_s_own_wrapper_...` with `runner_exe` returning the fallback
  and no stripping, 0 passed, 1 failed; after, 1 of 1. The lane crate 36 of 36, the land crate 219 of 219. Not run red: nothing
  against a real lane tree or a real `make land` (the end-to-end test's `make land` is a stand-in recipe in the scratch clone's
  Makefile that ticks and pushes); T23 is the real batch.

### T14 Approach (checklist part A)

1. **The goal, in the world.** A runner that, with no batch open, forms D5's batch from the waiting hand-ins, lands it in the
   lane's own tree with one gate run, each attempt's output kept, the landed done refs deleted and one status line owed; a killed
   or red batch left open and resumed as the next attempt.
2. **The constraints.** D5 (the formation and `LANE_MAX`), D6 step 1 (the attempt files), D8 (a JSON line a transition, the done
   refs deleted after the push), D14 (shas read once; a later hand-in waits), FR-003 ("in order"), US3, data-model.md ("Recovery"),
   contracts/lane-cli.md (`LAND_NOTE`, `L7R_LANE_BATCH`), T12's "For T14".
3. **Where each comes from.** R: plan.md D5, D6, D8, D14; data-model.md; contracts/lane-cli.md; T12's plan section; the Makefile's
   `land` recipe; `land-alone.sh` line 572. O: the red-first counts above; GNU make's documented `MAKEFLAGS` and exit 2.
4. **Do they describe the world here?** Yes for the scratch world: the end-to-end test builds a clone, a bare `origin` and two pool
   trees, hands in two changes, and sees one batch, one push, both ticked, both done refs deleted, one `owed` line. Not yet for the
   real clone's lane tree: T23 measures that.
5. **The order.** After T12 (the runner) and T13 (the lane's tree); before T15 (the red's attribution), T19 (the push), T20 (the
   wake-up), T22 (the base flipped) and T23 (the real batch); T52 before T22.
6. **The exits.** Green: the lane crate's tests, the end-to-end batch among them, and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Two: the exit-3-as-2 reading (Decision 4), found by reading make's exit rule after the first green, fixed
   red-first; and the lock's flake, 2 red in 10, traced to a descriptor copy and fixed red-first (above).
8. **The budget.** One landing.
9. **Done, measured.** The tests above green, 2026-11-27; the runner's tests' flake, 2 red of 10 before the lock fix, and the runs
   after it, above.
10. **Before moving a constant.** n/a: `LANE_MAX` is new, labeled GUESS and audited.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** One defect fixed: a probe or an ended runner leaving the lock held behind a copy of its descriptor, so a
   threaded caller read a runner that had ended (the flake above: 2 red runs in 10). The rest is new code.

**Found and left?**

- In the lane's tree `make land`'s `carry_done` reads the done refs live, so a task whose ref a later hand-in moved after the
  batch's `batch` line is carried again at the new sha on top: a hand-in lands inside a batch that never named it, against D14.
  Not fixed here: `make land`'s carry is the land crate's, and the stand-in `make land` of the end-to-end test carries nothing, so
  the fix needs its own red test there. Filed as T52; lands before T22.
- The runner's start waits `START_WAIT_S` for the lock while the lane tree's wrapper may first rebuild that tree's `l7r-gate`, so a
  start can report `holds no lock` while the runner comes up after the build. Not fixed here: the rebuild is unmeasured. Filed as
  T51; lands before T22.
- `make lane` shows an earlier hand-in of a task in an OPEN batch as `superseded`, not `in batch <b>`, once a later hand-in of the
  task exists (`log::state`, T11's order), though the batch's `batch` line names and lands the earlier sha (D14): the lane's view
  misstates what a batch carries (D8's states). Not fixed here: `log::state` is T11's reading and the batch's formation does not
  depend on it. Filed as T53; lands before T20.

**Performance work?** no


### T15 (phase 2's red path: a red batch attributed from the gate's own record, its changes ejected as repair entries, the rest run again)

- **Approach**: `rust/gate/crates/lane/src/attribute.rs` (new, pure) reads a red attempt's units - its span's red `test`, `lint`, `cover-build`, `cover-run` and `build` Phase lines in the lane's tree, ONE UNIT A LINE over every crate it names; `HOOK TESTS FAILED:` lines and the first pass's `Every refusal:` rows of the attempt file - and maps each to the change whose delta touches it (D6 step 2). `repairs.rs` (new) is the one writer of `l7r-lane/repairs.jsonl`. `runner/run.rs`'s `run_batch` loops: a red attempt writes its `run` line's `red`, an `attribute` line, each entry BEFORE its `eject` lines, one `owed` line an entry, and runs the rest again on the tree brought to `origin/main` anew (D6 "By phase", D7). `wake::dead` (T20) narrowed: only the runner's own `"stopped": true` line tells a death. Measured 2026-11-27: the two readings the handoff left open, by reading the code and a test of each (below); every `Phase` line of the clone's `l7r-events/*.jsonl` counted by step and crate count (a Python count): 947 of 2,723 `cover-build` lines named 2 to 28 crates, every other step's line one.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **Several candidates in phase 2 are UNPLACED** - any red unit naming no change or more than one, or no unit read at all, ejects the batch as one entry (`why` `unplaced`). Label: the algorithmically easier route; D6 halves over candidates, phase 3's (T24 replaces `attribute()`).
2. **A crate is its directory; its dependents are not counted** (`dir/` matched with the slash). A change to `core` that reddens `lane`'s tests is unplaced; phase 3's halving places it. Label: D6's literal "a crate by its directory".
3. **A Phase line is one unit over all the crates it names**: the unit names every change under ANY of the line's crates, each of them read, however many - only its printed form is cut (`<dir> <dir> <dir> (+<k> more) <step>`, the first 3 shown, `NAMED` a GUESS knob of the owed line's length, no rule's). Label: deliberate deviation from the build half's unit a crate, a defect fixed here: a red `cover-build` is one compile of a family, so read a crate at a time it placed and ejected an innocent change under another crate of the family as `red`. Pinned by `attribute::tests::a_red_line_naming_several_crates_is_one_unit_over_all_of_them`.
4. **A suite maps** to a delta path whose file name is the guard file, `tests/hooks/test-<stem>.*`, and for a `*-hooks` stem `rust/guard/src/guards/<snake>*` and `rust/guard/shared/src/guards/<snake>*`. Label: D6's map; the shared crate the easier reading of "its guard's sources".
5. **A first-pass row maps** by a delta path its text contains, or by its leading task list (`T13, T14: ...`). Label: D6 "a row by its file"; the task head the first pass's own form.
6. **A non-zero exit not on `origin/main` is a red, except two that eject nothing.** Exit -1 (`make` could not start, or was killed): no failing change to name, and ejecting on no evidence would eject innocent ones. And a FIRST-PASS REFUSAL WITH A ROW NAMING NO CHANGE of the batch - a hold, a lock, an owed round of no task of it (`attribute::refusal`, `Refusal::Unnamed`): it blocks the whole batch and would refuse every repair too. Each stops the runner with the batch open, its `owed` line carrying `"stopped": true` (`lane: batch <b>: make land's first pass refused at attempt <n>, a row naming no change of the batch (<those rows>) - the runner stopped, the batch open, nothing ejected: <attempt>`), and the next `make lane-start` resumes it, as T14 did. Where such a row stands beside a row naming a change, the stop holds too: nothing lands while the hold stands, and the named change is ejected on the resume once it clears. A refusal whose every row names a change of the batch ejects what the rows name and runs the rest again: a row naming one change places it (`red`, Decision 5); a row naming several - `T13, T14: ...`, two hand-ins - ejects every change the rows name as ONE entry (`unplaced`, the rows its units), not the whole batch. Label: the GM's "ejects the failing change. The rest of the batch lands" read literally - a row naming a change names the failing one, a row naming none names no failing change; fixed on the plan review's rounds 1 (the build half ejected the whole batch for a refusal naming nothing, NOT LEGITIMATE) and 2 (round 1's stop also took a row naming two changes, NOT LEGITIMATE). Pinned red first by `runner::run::tests::a_first_pass_refusal_naming_no_change_ejects_nothing_and_one_naming_a_task_ejects_its_change` and `a_first_pass_row_naming_two_changes_ejects_both_and_the_rest_lands` (two changes of three ejected as one entry, the third lands; a named row beside a lock stops).
7. **A kill between filing an entry and its `eject` lines resumes as a new attempt.** The resume runs what the log has not ejected (`runner::remaining`); an entry of the same batch and the same set is filed once (`repairs::file` returns its id). Label: the algorithmically easier route (no repair of a half-written ejection). What it costs: the entry's `ejected` may list a change the resume then lands, or re-ejects under a second entry. So AN ENTRY IS A CHANGE'S REPAIR ONLY WHERE AN `eject` LINE NAMES IT - data-model.md, "A repair entry", states it for T16's queue (`log::repairs_open`, and the repair's changes the `eject` lines' `change`s). Priced: finishing the interrupted ejection at resume (the entry's unejected changes ejected before the next attempt) - a second writer of `eject` lines for a window of two appends; not taken. Pinned by `runner::run::tests::a_kill_between_a_repair_entry_and_its_eject_lines_resumes_what_the_log_has_not_ejected`. Chosen by the closing half, 2026-11-27, as the brief named it.
8. **T20's Decision 6 revisited: only the runner's own `"stopped": true` line tells a death** (`wake::STOPPED`), not any `owed` line of the open batch. WHY: T20 wrote the rule for T14's red stand-in, which owed one line and stopped; since T15 an ejection owes its line and the runner goes on, so a runner killed in the next attempt left an open batch no line said - the coordinator never woken. Red first: `wake::tests::an_ejection_s_line_tells_no_death_so_a_runner_killed_after_it_is_said` failed on T20's rule (the wait returned the sentinel line, no death line). T20's own test kept, its line now the real exit -1 form. A stopped carry writes no `owed` line, so the wait's death line says it, once.
9. **The attribution's record is found where the gate's writer files it** (the handoff's check 1): a check's `Phase` line carries no task and no feature (`rustc/phase.rs`, `append_row_with(root, None, ...)`), so `event_log_hooks/filed.rs`'s chain reaches the pool's holder - `builder_pool::read` drops the lane's tree - and then `feature_of`: `L7R_FEATURE_DIRECTORY` (stripped by the runner), then the runner's `SPECIFY_FEATURE`, which `make land` exports again as the same spec (`land.rs`). Pinned by `runner::run::tests::a_check_s_phase_line_in_the_lane_s_tree_is_filed_where_the_attribution_reads_it` (the real writer, a stale `feature.json` naming another feature). No lane-tree `Phase` line exists yet to observe - none in the clone's logs, observed 2026-11-27, method: the same Python count of every log's `Phase` lines by `clone` (the lane has run no real batch); T23's real batch measures it.
10. **One `owed` line a repair entry**, naming the entry, its units and the attempt file. Label: the algorithmically easier route, FR-005's wake for a red batch - each entry is a dispatch the coordinator owes (D7: a fresh builder by `make builder-next`); the `owed` lines of one attempt are written together, so one `make lane-wait` returns them as one wake.
11. **The suite and row readers read the attempt file** (the handoff's check 2): `long_runs.rs`'s `run_gate` and `loud` spawn `make done` and `make hooks-test` with inherited stdout and stderr, `make done` prints `HOOK TESTS FAILED:` in its foreground loop (the static phases' log is printed after), `LAND_RUN` has no pipe, and the runner points `make land`'s stdout and stderr at the attempt file. The `--src hooks` Phase lines stay the fallback, not built.

### T15 Approach (checklist part A)

1. **The goal, in the world.** A red batch in the lane costs the coordinator one line a repair: the change the gate's record names leaves the batch as a repair entry for a fresh builder, the rest lands without a human.
2. **The constraints.** FR-005 (one wake an event), D6 step 2 and "By phase", D7 (repairs by fresh builders), D14 (an ejected change's ref kept), data-model.md's repair entry and log lines.
3. **Where each comes from.** R: plan.md D6, D7, D14; data-model.md. O: the crate counts above, the code read for checks 1 and 2.
4. **Do they describe the world here?** The crate count and the two readings, each pinned by a test; the real lane tree's lines are T23's.
5. **The order.** After T14, T20, T53 (merged `log::state`: `in batch` before `superseded`, a `landed` line listing a change as ejected reads ejected, both tested in `log::tests`); before T16 (reads the entries by Decision 7's rule), T18, T19.
6. **The exits.** Green: the lane crate's tests and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The lane crate's tests all green, 69 of 69, measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/lane`); the red-first counts in the report.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Three wrong outcomes fixed: an innocent change ejected by a family `cover-build` red (Decision 3); a whole batch ejected for a first-pass refusal no change caused (Decision 6); a runner killed after an ejection never said to the coordinator (Decision 8). And one test reached again: `step` over an open batch returns `Ok(false)` and writes nothing, now with a hand-in waiting (red with the guard removed).

**Found and left?** none

**Performance work?** no


### T16 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T16 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T17 to T17 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T18 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T18 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T19 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T19 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T20 (D9, FR-005: phase 2's coordinator wake-up, the lines T14's runner owes printed once; lands after T14)

- **Approach**: `rust/guard/shared/src/lane_wake.rs` (new, with `lane_wake/tests.rs`) is the read mark; `rust/gate/crates/lane/src/wake.rs`
  (new, with `wake/tests.rs`) is `l7r-gate lane wait`, the verb `["wait"]` in `lane.rs` and the Makefile's `lane-wait` (its help
  line names the knobs; `docs/make-targets.html` regenerated); the prompt hook `clone_sync_hooks.rs` `prompt()` prints the unread
  lines. `log.rs`'s `DIR`/`FILE` now point at `lane_wake`'s; `runner::knob` became `pub(crate)`. `dev/audits/lane-wake.md` covers
  `WAIT_POLL_S`, `DEAD_GRACE_S` and `LOCK_S`; the lane crate's row in `rust/gate/CLAUDE.md` names `wake.rs`. Built in two halves
  (2026-11-27); the build half's handoff is `<clone git dir>/l7r-handoffs/T20-build.md`.
- **Decision 1 - one mark reader, in `l7r_shared::lane_wake`.** `take_unread(common)` returns the `line` of every `owed` event past
  `l7r-lane/read-mark` (a byte offset into `lane.jsonl`) and moves the mark past the last COMPLETE line (a torn tail is read again
  once whole), under `read-mark.lock` by flock, let go by `flock -u` before the close (T14's reason: a forked child holds a copy of
  the descriptor), the mark written by a rename; a mark past the log's end or no number reads from 0; with no log nothing is taken
  and nothing created; a lock not got within `LOCK_S` takes nothing (the holder is showing the lines). `unread(common)` is a
  lock-free length-against-mark test, so a poll with nothing new spawns no flock. Both `make lane-wait` and the prompt hook call it,
  so one rule says what is unread. Why here: the guard depends only on `l7r_shared` (the checks' `guard_deps`), and a hook shelling
  out to the gate binary would pay a launcher start each prompt. Label: the easier route.
- **Decision 2 - whichever reader comes first moves the mark, the hook included.** A hook that printed without moving it would have
  each re-armed wait print at once what the prompt already showed: a wake FR-005 does not list. The read, the take and the move are
  serialized by the mark's lock, so a line is shown once, by the prompt or by the wait, never both. Label: the easier route of D9's
  "prints any unread lane lines, so a wake-up command killed early loses nothing".
- **Decision 3 - the runner-dead line is written by the wait.** A killed runner writes nothing, and a runner stopped on an error
  (T14's stopped carry or refused landing) writes `stop` but owes nothing, so a wait reading only `owed` lines would block for ever
  over a stranded batch. Rule (`wake::dead`): no runner holds the lane's lock, the log's LAST batch is open, and no `owed` line with
  `why: "runner"` since the last `start` line (said once a death); held `LANE_DEAD_GRACE_S` continuously (reset whenever the runner
  is seen or nothing is stranded), so a runner a hand-in is starting is not called dead. The wait then appends ONE `owed` line
  `{"batch", "why": "runner", "line"}` naming the batch, its changes, the runner's last stop (or `killed`) and `make lane-start`,
  and loops, so it prints that line through the mark like any other. Quiet with no open batch: an `idle` end, `make lane-stop` after
  a landing, and phase 1's waiting hand-ins with no runner (landed by hand). Label: the easier route (a stranded batch is the one
  case in which no other line will come).
- **Decision 4 - the prompt hook prints before `solo::alone`'s return.** `prompt()` extends its lines with
  `take_unread(<clone>/.git)` after the feature.json notice and before the only-session return, because a coordinator whose
  builders are subagents IS the only session, and the return would otherwise drop the lane's lines for exactly the session they
  are owed to. This changes the hook's rendering: an unread lane line now appears among its prompt lines. Label: the easier route.
- **Decision 5 - the wiring and the knobs.** The verb takes no flags, its knobs from the environment, because the stall watchdog's
  `waits_on_lane` (T12) matches exactly `<dir>/l7r-gate lane wait` (confirmed live below). `wait_cli` exits 0 with each line
  printed, 2 on a knob that is no number, 1 on a dead line it cannot write. `WAIT_POLL_S` 5 s (the runner's own `POLL_S`),
  `DEAD_GRACE_S` 30 s (past `START_WAIT_S` and a short rebuild, T51), `LOCK_S` 5 s: all GUESS, each beside its constant and in
  `dev/audits/lane-wake.md`. No ceiling (D9's `LANE_WAIT_MAX`: none). Label: GUESS for the numbers; convention (the watchdog's
  argv) for the flagless verb.
- **Decision 6 - one red run wakes once: the runner's own line for the batch tells the death.** With T14's red stand-in a red run
  writes its ONE `owed` line (`... - the runner stopped, the batch open; ...: <attempt file>`), THEN the runner stops with `error:`
  and leaves the batch open. Under Decision 3 alone the coordinator's re-armed wait would see no runner over that open batch and,
  `DEAD_GRACE_S` after the re-arm, write and print a runner-dead line for the same batch: a second wake for one red, one FR-005 does
  not list (540k-966k tokens a wake, measured 2026-11-27 (the transcript's usage fields), as D9 records). So `wake::dead` counts any
  `owed` line naming the open batch since the last `start` - a `why: "runner"` line or the runner's own - as having told it. Nothing
  is lost: that red line already says the runner stopped; a runner started again (a new `start`) and killed is a new death, said.
  The rule can go with T15, whose red path no longer stops the runner. Label: the easier route. The build half's handoff had
  accepted the double wake until T15; the plan review (round 3, 2026-11-27) ruled that NOT LEGITIMATE under FR-005, so it is fixed
  here.
- **Not here.** T47 (the watchdog's long-run exemption of `make lane-wait`, `pass.rs`) and T21 (the Stop rule that keeps the wait
  armed) are their own tasks. T21's "the lane holds a waiting hand-in or an open batch" reading is not exposed by this task: the
  guard cannot reach the lane crate, so T21 needs its own reading in `l7r_shared` (as `lane_wake` is).
- Red first (2026-11-27, the build half): `l7r_shared` `lane_wake::tests` against stubs (`unread` false, `take_unread` empty), 1
  passed, 4 failed; after, 5 of 5. The lane crate's `wake::tests` against a stub `wait` returning no lines, 0 passed, 6 failed;
  after, 6 of 6 (a seventh, the command sleeping on the real clock until a thread writes the line, added after for `wait_cli`'s real
  sleep, written green). Decision 6 (2026-11-27, the closing half): `wake::tests::a_red_run_s_own_line_tells_the_death_so_one_red_wakes_once`
  under the old `dead`, 6 passed, 1 failed; after, 7 of 7. The guard's `clone_sync_hooks::tests::an_unread_lane_line_is_printed_once_and_marked` without the hook's
  line, 0 passed, 1 failed (left "", right the line); after, 1 of 1, the module 33 of 33. `tests/hooks/test-clone-sync-hooks.sh`
  68 ok with its two new cases (an unread line printed on the prompt, then not again); not run red (the Rust test is the red one).
  Live (2026-11-27, a scratch repository whose Makefile calls this tree's `scripts/gates/l7r-gate.sh lane wait`):
  `/proc/<pid>/cmdline` read `.../tool/l7r-gate|lane|wait|`, an appended owed line ended it printing `lane: live line`, exit 0,
  `read-mark` 42 = the log's 42 bytes, observed 2026-11-27, method: that live run. Nothing run against the real clone's lane (it has no `l7r-lane/`).

### T20 Approach (checklist part A)

1. **The goal, in the world.** A coordinator that runs `make lane-wait` in the background is woken once for each line the lane owes
   it - a landed batch's status, a repair, an arbiter owed, a stranded batch's dead runner - and never twice for one line, whether
   the wait or its next prompt shows it first; a wait killed early loses nothing.
2. **The constraints.** D9 (one background command, the mark, no ceiling, the prompt hook's unread lines), FR-005 ("once per landed
   batch with a short status, and otherwise only for US5's cases"), D8 (the log a JSON line a transition), T12's `waits_on_lane`
   argv, T14's owed line and its red stand-in, data-model.md ("The log line").
3. **Where each comes from.** G: FR-005's words. R: plan.md D8, D9; data-model.md; T12's and T14's plan sections; the build half's
   handoff. O: the red-first counts and the live run above.
4. **Do they describe the world here?** Yes for a scratch repository: the live run's real `l7r-gate lane wait` was matched by its
   argv and ended by an appended line, the mark at the log's end. Not yet for the real clone's lane, which has no `l7r-lane/`:
   T23 runs the real batch.
5. **The order.** After T14 (the owed lines) and T53; with T47 (the watchdog exemption); before T15 (which may drop Decision 6's red-line rule), T21 (the Stop rule), T22 (the base
   flipped, with T56) and T23.
6. **The exits.** Green: the changed crates' tests and `make builder-checks` clean, the clone-sync suite green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One: the runner dead has no writer (Decision 3), found by reading T14's stop path; and the double wake it
   left over a red, fixed red-first (Decision 6).
8. **The budget.** One landing.
9. **Done, measured.** The tests above green, 2026-11-27; the first tier green again at the closing half.
10. **Before moving a constant.** n/a: `WAIT_POLL_S`, `DEAD_GRACE_S` and `LOCK_S` are new, labeled GUESS and audited.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** New code; one wrong outcome of the build half fixed in it: a red run woke the coordinator twice (Decision 6).

**Found and left?**

- A WAITING hand-in that no runner serves (from phase 2's base, a runner start that failed past `START_WAIT_S`, T51's rebuild) is
  not called dead by `wake::dead`, which reads only an open batch, so the coordinator's wait - which T21's Stop rule keeps armed -
  blocks with nothing ever coming. Not fixed here: in phase 1 such hand-ins are landed by hand and must stay quiet, and the base
  flips in T22. Filed as T56; lands before T23 (with T22).

**Performance work?** no


### T21 (D9, FR-005: the Stop rule that keeps the coordinator's `make lane-wait` armed; lands after T20)

- **Approach**: `rust/guard/src/guards/pool_idle_hooks.rs` gains a second rule beside the free-tree rule (`judge_lane`,
  `lane_refusal`, `Lane`), the lane's state read in `l7r_shared::lane_wake::holds` (`rust/guard/shared/src/lane_wake.rs`, its
  tests in `lane_wake/holds_tests.rs`), because the guard cannot reach the lane crate (T20's "Not here"). Tests:
  `pool_idle_hooks/tests.rs` (three new) and `tests/hooks/test-pool-idle-hooks.sh` (ten new cases).
- **Decision 1 - what the lane holds, read in `l7r_shared`, parallel to the lane crate's `log.rs`.** `holds(common)` says, in a few
  words, the lane's first open batch (a batch whose last state-moving line - `MOVES`, `state_of`'s events - is neither `landed` nor
  `stop`, its lines routed as `batches` routes them, so a batch resumed after a `stop` is open again), else its first waiting
  hand-in; none where the lane has no log. The waiting reading follows `log::state` with no batch open (in-batch cannot hold):
  the pool log's `handed_in` done lines, a commit's first, still the lane's (a done ref or a lane line names it), not landed by a
  `landed` line, not ejected (the last line naming it an `eject`, or a `landed` line listing it ejected), not superseded. "Landed"
  by `origin/main` (`held_by`) is not asked: a git walk a Stop hook would pay each turn; cost, a hand-in landed on `origin/main` by
  hand while its done ref still stands reads as waiting, which `make carry` (the ref deleted at its end) does not leave. Label: the
  easier route; the duplication is filed as T63 (one reading, `log.rs`'s pure readers moved to `l7r_shared` and re-exported).
- **Decision 2 - a waiting hand-in counts only while the runner lives.** A deliberate deviation from D9's literal "a waiting
  hand-in", for phase 1: until T22 flips `HAND_IN_BASE` no hand-in starts the runner (T12 Decision 6), the coordinator lands each by
  hand, and a wait over it could never wake (`wake::dead` is quiet there on purpose, T20 Decision 3) - so the rule would refuse
  every stop after a hand-in and arm a wait with nothing coming. The runner's lock (`lane.lock`, `RUNNER_LOCK`) is probed as
  `runner::held` probes it (`flock -n`, let go by `flock -u`). No second reading of the knob is made. From T22's base a waiting
  hand-in no runner serves (T56's case) holds no stop: Not fixed here: the base and its one reading are T22's. Filed as T64; lands
  with T22 and T56.
- **Decision 3 - "a `make lane-wait` of this clone runs": its `make` or the wait itself, any process of the clone.** A `/proc`
  process whose argv is `l7r-gate lane wait` (T12's `waits_on_lane`) or a `make` whose one target is `lane-wait` past its flags,
  a valued flag's value and `VAR=` words (`pass::lane_wait_make`, shared with T47), its working directory in the clone. The make
  counts from its start, while `l7r-gate.sh` may still build the binary (T54: 2 to 112 s, measured 2026-11-27 (T54's scratch-clone rebuilds)), so a stop in that gap is not refused.
  Any process of the clone, not only the session's own (as T12's `lane_works` asks): the plan's Scale is one session a clone,
  several sessions feature 459's, and a Stop hook has no registry pid to walk from. On the reviewer's note that T20's Decisions 2
  and 4 assume one session: not found in `plan-review.json` or the ledger; the same assumption is taken here, as D9's "of this
  clone" words it. `/proc` is `POOL_IDLE_PROC` in a suite. Label: the easier route.
- **Decision 4 - one block, and an escape of its own.** Where both rules hold, the free tree's block and the lane's are said in ONE
  Stop block (each refused stop is a wake, 540k-966k tokens, D9). `POOL_IDLE_OK` waives the tree rule only: a turn that keeps a
  tree free for the GM still owes its wait; the lane rule's escape is a line starting `LANE_WAIT_OK: <reason>`, checked first and
  recorded (rule `LANE_WAIT_OK`; a bare one `LANE_WAIT_OK-no-reason`; a held stop `lane-unwatched`). The block names the exact
  command, `make -C <clone> lane-wait`, with `run_in_background: true`. NEW GUARD MESSAGES: the lane block and the bare-escape block
  (the session runs their check). The escape parser is shared by both rules (`reason`). Label: convention (`POOL_IDLE_OK`'s form).
- Red first (2026-11-27): `l7r_shared` `lane_wake::holds_tests` against a stub `holds` returning none, 0 passed, 2 failed; after,
  `lane_wake` 7 of 7. The guard's `pool_idle_hooks::tests` against stub `judge_lane`/`lane_refusal` (quiet, none), 6 passed, 3
  failed; after, 9 of 9. `tests/hooks/test-pool-idle-hooks.sh` with `judge_lane` returning quiet at its top (the rule deleted), 37
  passed, 5 failed; restored, 42 of 42. `make builder-checks CRATE="rust/guard rust/guard/shared"`: 636 and 617 tests, lint and
  format clean, observed 2026-11-27, method: that run's log.

### T21 Approach (checklist part A)

1. **The goal, in the world.** A coordinator cannot end its turn while the lane holds work whose line will come and nothing would
   wake it; told the one command, it starts `make lane-wait` in the background and is woken once by the line. Phase 1's hand-ins,
   landed by hand, hold nothing.
2. **The constraints.** D9 (the Stop rule, its message the exact command with `run_in_background: true`, its suite case and quiet
   case, XVIII), FR-005 (no wake it does not list), D8 (the states computed from the logs), T12 Decision 6 (no runner before T22's
   base), T20's mark and Decision 3, the plan's Scale (one session a clone).
3. **Where each comes from.** G: FR-005's words. R: plan.md D8, D9; data-model.md; T12's and T20's sections. O: the red-first
   counts above.
4. **Do they describe the world here?** On fixtures: a scratch repository with done refs and the pool and lane logs, a fake
   `/proc`. Not on the real clone's lane, which has no `l7r-lane/`: T23 runs the real batch.
5. **The order.** After T20 (the wait it arms); with T47; before T22 (with T64 and T56) and T23.
6. **The exits.** Green: the changed crates' tests, `make builder-checks`, the pool-idle suite. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One: the literal rule refuses every stop in phase 1 (Decision 2), found by reading T12 Decision 6 and
   `wake::dead`.
8. **The budget.** One landing.
9. **Done, measured.** The tests above green, 2026-11-27.
10. **Before moving a constant.** n/a: no constant moved; `RUNNER_LOCK` mirrors `runner::LOCK`.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** New rule: without it a coordinator ends its turn over an open batch with no wait armed and is woken by
   nothing until the GM prompts it.

**Found and left?**

- The lane's states read twice, in `log.rs` and `lane_wake` (Decision 1): a later change to either drifts the Stop rule.
  Not fixed here: the lane crate is outside this task's crates. Filed as T63; lands before T26.
- From T22's base a waiting hand-in no runner serves holds no stop (Decision 2). Not fixed here: the base's one reading is T22's.
  Filed as T64; lands before T23 (with T22 and T56).

**Performance work?** no

### T22 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T22 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T23 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T23 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T24 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T24 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T25 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T25 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T26 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T26 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T27 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T27 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T28 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T28 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T29 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T29 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T30 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T30 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T31 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T31 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T32 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T32 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

### T33 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T33 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T35 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T35 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

<!-- plan-archive: T34 to T06 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T37 to T34 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T38 (T34's builder, 2026-11-27: the first pass's in-process claims calls never see the hand-in base; T40 built here)

- **Approach**: built in pool tree `diagram-backlog-t271` on main's 13ca98165b. The in-process claims calls take the base as an argument,
  and at a hand-in the owed-with-no-flight refusal is scoped to the builder's own claims.
  - **The door** (`land` `cheap.rs` `Land::claims`): every in-process claims call (the rekey, the carry, the known drifts, the report)
    goes through it. It now passes `--delta-base=<base>`: the hand-in base at hand-in, an empty value at a landing.
  - **The flag** (`claims` `claims.rs` `split_top`): a new top-level `--delta-base=`, `=` form only, so an empty value counts as a
    value. Given, it runs the command inside `l7r_gate_core::delta_base::with`.
  - **The reader** (`core` `delta_base.rs`): `with` exists in every build now, not only in test builds. A base given on the thread
    wins over the process's `L7R_DELTA_BASE`, and an empty one given reads as no base. So a stray export never narrows an in-process
    call at a landing. `with` restores the outer base after it. A test build still reads no process variable.
  - **The sites that did not read the base**, now reading `delta_base::named` through `carry::delta_paths` (the working tree
    against the base, plus untracked files; else the merge base, as before):
    - `carry.rs` `touches_engine`, which picks the carry's target. From the merge base, another task's staged engine code sent a
      builder's carries into its own feature rather than 405.
    - `report.rs` `delta_form_problems`.
  - **The task line's pointer, made precise**: report.rs 91 is `delta_form_problems`. The claims gate's child process calls it, not
    the in-process `report`. That `report()` reads no base, and `open_claims_refusal` already scopes it by `delta_names()`, which
    reads the hand-in base. At hand-in, `origin/main...HEAD` named every staged batch's files and none of the builder's uncommitted
    ones, so a form problem the builder wrote passed and another task's refused (observed 2026-11-27, method: reading `gate_cmd` and
    the fixture below). Fixed here.
  - **T40, the owed claims at hand-in** (new `claims/hand_in.rs`, called by `carry.rs` `classified`): applies spec-fidelity's MODE 1
    ruling of 2026-11-27 (LEGITIMATE, three bounds). It applies only where `delta_base::named` gives a base, never on `mb`'s merge-base
    fallback. Each owed (key, why) is compared with the base tree that `classified` already extracts (its rows by `index::rows_of`).
    - A claim counts as the landing's only if the base holds a row under the same key that matches the row now on everything an owed
      reason reads: code, normalized claim text, research fingerprint (cited pages, followed), the unit's constant reads, its
      siblings and its index row. For a DRAWN reason, the Mode A engine must match too.
    - Anything else is the builder's, including a claim with no base row (added or moved). This is bound 1. Where in doubt, it refuses.
    - The landing's claims go to the pre-existing warnings as `owed below the hand-in base, the landing's to ask (461 T40; <why>): <key>`.
      The line never contains `owed (`, which `claims_wait::claims_cure` and the first pass's `lane_s` read as the builder's to cure.
    - `owed()` itself, `owed_keys` (`ports::Before`), introduced findings, form problems and carries are unchanged (bound 3). A
      landing gives an empty base, so it asks every owed claim. A base that names no commit gives None, so nothing is scoped (bound 2).
    - A scoped pass is never stored for the landing to skip on: `push-gate pass claims` stores none while a judged path is
      uncommitted, and at a phase-1 hand-in every path the gate judges is (observed 2026-11-27, method: reading `cohort`
      `push.rs` `record_pass`).
  - Built here: T40 - the hand-in's owed-with-no-flight refusal scoped to the claims the builder's delta touches, adds or moves (`claims/hand_in.rs`, `carry.rs` `classified`).
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=<crate> ONLY=<module>` with each line below broken in turn and
    restored, by `t38-mutate.py` in the scratchpad):

    | line broken | crate, ONLY | passed, failed | red |
    |---|---|---|---|
    | `classified` not scoping at a hand-in | claims, `claims::hand_in` | 2, 1 | at_a_hand_in_only_the_claims_its_work_touches_are_refused_owed |
    | the flag parsed but not given | claims, same | 2, 1 | the same |
    | `touches_engine` reading the merge base only | claims, same | 2, 1 | at_a_hand_in_the_engine_and_the_form_problems_are_the_work_s |
    | `delta_form_problems` reading `origin/main...HEAD` | claims, same | 2, 1 | the same |
    | `Land::claims` giving an empty base at hand-in | land, `land::cheap::tests::hand_in` | 6, 1 | the_checks_that_read_their_own_delta_are_handed_the_hand_in_base |
    | `with` not restoring the outer base | core, `delta_base` | 0, 1 | a_named_commit_is_the_base_and_anything_else_is_none |

    - The fixtures commit another task's staged batch above `origin/main` (`Thing.m`'s code changed, so its claim is owed), make that
      commit the base, and leave the work uncommitted (`reach`'s code changed).
    - At hand-in only `reach` is refused owed, and `Thing.m` is said as the landing's. With no base, an empty one or `no-such-rev`,
      both are refused.
    - Two assertions also hold on the old code, which refused everything, so they were not run red: bound 1's test (the work touches
      `Thing.m` again and adds `helper`'s claim, and all three are refused) and the landing leg.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the hand-in base given to the in-process claims calls, and the owed claims scoped to the work at hand-in | n/a - no map | n/a | none | n/a |

### T38 Approach (checklist part A)

1. **The goal, in the world.** At hand-in the claims checks judge the builder's own work. The in-process carry, the known drifts and
   the form problems read the hand-in base, and an owed claim refuses only where the work touches, adds or moves it.
2. **The constraints.** FR-002 (a builder's tree meets the refusals the builder can cure), FR-008 (a landing asks every owed claim),
   D3, D4, T34's reader, and spec-fidelity's MODE 1 ruling of 2026-11-27 with its three bounds. Constitution XIII: with no base given,
   every call reads as before.
3. **Where each comes from.** G: the GM's request behind FR-002 (spec.md). R: the ruling's bounds (T40's line), T34's section. O: the
   red-first table.
4. **Do they describe the world here?** Yes: each fixture stands as a phase-1 hand-in tree does, with a staged commit above origin/main
   as the base and the work uncommitted on it.
5. **The order.** After T34, before T08, which wires the hand-in mode into `hand_in.rs`.
6. **The exits.** Green: the tests and `make builder-checks` of core, claims and land. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The red-first table above. `make builder-checks CRATE="rust/gate/crates/core rust/gate/crates/claims
   rust/gate/crates/land"` green, 2026-11-27 (core 86, claims 206, land 192 tests). Core is checked because `delta_base.rs` changed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Only a hand-in that names a base changes. It refuses fewer owed claims (other staged work's) and its own form
   problems in place of other tasks'. With no base, or an empty one as at every landing and push, nothing changes.

**Found and left?** none. The push table's other delta-scoped rows are T37's.

**Performance work?** no. The scoping costs one `rows_of` over the base tree, and only at a hand-in with something owed. It was not
timed: the base tree was already extracted, and the fixtures' gate calls stay inside the crate's test time.


### T36 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T36 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T40 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T40 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

<!-- plan-archive: T41 to T37 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T42 to T34 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T43 to T08 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T44 to T43 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T45 to T13 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T46 (T13's found-and-left: the builder-tree help lines said nothing of the lane)

- **Approach**: three `##` help lines of the root Makefile (through `make guard-edit FILE=Makefile`, a guard file) restated to
  what the code does now, read 2026-11-27 in `rust/gate/crates/task/src/builder_tree.rs` and T13's, T49's and T50's sections:
  `builder-tree-adopt` - the lane's tree (`L7R_LANE_TREE`, else `<clone>-land`) joins as the lane's, held by the reserved holder
  `lane`, no handout takes it, the cap does not count it, a `T=` or a second lane refused; the runner's `l7r-gate builder-tree
  lane` (no make target) brings it to `origin/main` at each batch's start and makes it again at its path, its cache kept, when it
  is gone from disk (T13, T50); `builder-tree-drop` - takes the lane's tree too, refused while the lane's runner lives (`make
  lane-stop` first) or a batch of its log is open (`make lane-start` runs it to its landing or its stop) (T49); `builder-trees` -
  lists the lane's tree, held by `lane`, apart from the cap (T13, the list header's `, and the lane's tree`). `make docs`
  regenerated `docs/make-targets.html` (224 targets, 0 undocumented). No code changed. Red first: none applies - no test pins
  these help lines' words (grep of `tests/` and `rust/` for the three target names, 2026-11-27: only the builder-pool guard's
  REMOVE message and the crate's own stdout, both unchanged).

### T46 Approach (checklist part A)

1. **The goal, in the world.** A reader of `make help` or `docs/make-targets.html` adopting `<clone>-land` is told it becomes the
   lane's tree, how the lane brings it to `origin/main` and re-makes it, and how it is dropped.
2. **The constraints.** T13 (the lane holder, the cap, the reserved word, `builder-tree lane`), T49 (the lane's drop), T50 (the
   re-make), T12's hold on the Makefile (landed before this).
3. **Where each comes from.** R: tasks.md T46's line, T13's, T49's and T50's plan sections; O: `builder_tree.rs`, read 2026-11-27.
4. **Do they describe the world here?** Yes: each clause matches a message the crate's lane tests pin (`builder_tree/tests/lane.rs`).
5. **The order.** After T12, T13, T49 and T50; before T22.
6. **The exits.** Green: `make docs` writes the page with 0 undocumented. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the three targets found by one grep of the Makefile.
8. **The budget.** One landing.
9. **Done, measured.** `make help` and `docs/make-targets.html` carry the lane's adoption, `builder-tree lane`, the re-make and the
   lane's drop.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of the help lines is told the lane's rules; nothing else changes.

**Found and left?** none

**Performance work?** no

### T47 (D9, FR-005: the watchdog's long-run warning passes over the coordinator's own `make lane-wait`; lands with T20, before T22)

- **Approach**: `rust/guard/src/guards/stall_watchdog_hooks/pass.rs`: `long_run` takes `waits` and drops a `make lane-wait` from its
  candidates where it holds; `long_run_line` asks T12's `lane_works(p, clone, pid)` for it; `LongRun` keeps the make's argv (from
  its `cmdline`'s NUL-split words); `lane_wait_make(argv)` is the matcher, shared with T21's Stop rule. Tests in `pass/tests.rs`.
- **Decision 1 - exempt the one make, not the check.** Only a `make` whose one target is `lane-wait` (past its flags, a valued
  flag's value - `-C <clone>`, T21's command - and `VAR=` words) is passed over, and only while `lane_works` holds: the clone's
  runner live and the wait the session's own. A long `make static` beside the wait is still told (skipping the whole check while a
  wait runs would hide it for as long as a wait is armed, which in phase 2 is nearly always), and with the runner gone the wait is
  a long make like any other: then nothing will end it but a dead-runner line or the GM, and `LONG_RUN`'s 30 minutes (CONVENTION, a knob) is a fair moment to say so.
  Why: the wait runs as long as a batch by design (D9), and each warning past `LONG_RUN` (1800 s, CONVENTION, a knob) types a nudge into the session -
  a wake FR-005 does not list (540k-966k tokens a wake, measured 2026-11-27 (the transcript's usage fields), D9). Label: the easier route (T12's predicate reused).
- Red first (2026-11-27): `pass::tests::a_long_make_lane_wait_is_not_told_while_the_session_s_lane_works` on the old `long_run`,
  0 passed, 1 failed (the wait warned); after, the module's 23 of 23 with it and
  `a_make_lane_wait_is_its_one_target_past_flags_and_assignments`. `tests/hooks/test-stall-watchdog-hooks.sh` 29 of 29, unchanged
  (the Rust test is the red one). No guard message changed.

### T47 Approach (checklist part A)

1. **The goal, in the world.** The coordinator's backgrounded `make lane-wait` over a long batch types no watchdog nudge into its
   pane, while any other make that runs too long is still told.
2. **The constraints.** D9 (the wait, no ceiling), FR-005, T12's `lane_works` (narrowed at its plan review to the session's own
   wait and a live runner), the long-run warning's purpose (the GM 2026-11-09).
3. **Where each comes from.** G: FR-005's words, the GM's long-run words. R: plan.md D9; T12's and T20's sections. O: the red-first
   counts.
4. **Do they describe the world here?** On a fake `/proc`; the live argv of `make lane-wait` (`make lane-wait`, its child
   `l7r-gate lane wait`) read from the Makefile's recipe and T20's live run.
5. **The order.** With T20 and T21; before T22.
6. **The exits.** Green: the module's tests, `make builder-checks`, the stall-watchdog suite. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The tests above green, 2026-11-27.
10. **Before moving a constant.** n/a: `LONG_RUN` is unchanged.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A defect fixed before it is live: a long batch's wait would have been told as a stuck make, a wake FR-005
   does not list and a nudge that invites killing the wait.

**Found and left?** none

**Performance work?** no

### T49 (T45's found-and-left: the drop of the lane's tree was a dead end)

- **Approach**: `drop_tree` (`rust/gate/crates/task/src/builder_tree.rs`) takes the lane's tree itself: a tree held by
  `builder_pool::LANE` is asked `lane_busy` in place of the held refusal - refused while the lane's runner lives
  (`l7r-lane/lane.lock` held, probed by `flock -n` as the lane's `runner::held`; the refusal names `make lane-stop`) or while a
  batch of `l7r-lane/lane.jsonl` is open (the refusal names the batch and `make lane-start`, which runs it to its landing or its
  stop); otherwise removed as any free tree is - REASON owed, the worktree, its cache and its registry line gone, a `drop` line
  logged - and adoptable again. THE LOG'S READING mirrors the lane's own grouping, not T17's one-batch question (`lane/src/log.rs`,
  `batches` and `state_of`, read 2026-11-27): a batch's lines are those naming it after its `batch` line (a later `batch` line of
  the same id a new batch), `landed` or `stop` naming it ends it, `carry`/`eject`/`run`/`attribute`/`push` reopen it, and a line
  naming no batch - the runner's own `stop` (`runner.rs`, `{pid, why}`), whose batch is resumed at the next start - or a torn line
  changes nothing. Read here, as `tree`'s `state::lane_run` reads it (461 T17), because the lane crate builds on `task`; a third
  reader of the log beside the lane and T17 (kept private here rather than making `tree`'s helpers public, which asks a different
  question - one named batch - and would put a second crate in this task). Every builder tree's rules are as they were: the
  not-free branch and its message unchanged. No guard-rendered message changed: the builder-pool guard's REMOVE message (T45)
  already names `make builder-tree-drop TREE=<path>`, which now works for the lane's tree.
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/task ONLY="builder_tree::tests::lane"` on the old code): 3 passed,
  1 failed - `the_lane_s_tree_goes_by_the_drop_once_no_runner_lives_and_no_batch_is_open` answered `is held by lane - make
  builder-tree-release T=lane first`. Green: `builder_tree::tests` 13 of 13; `make builder-checks CRATE="rust/gate/crates/task"`
  clean, the crate 157 of 157. The test covers the REASON, the lock held (refused) and present but free (passes), a batch open
  beside a runner's batch-less `stop`, a batch-keyed `stop` and a torn line (refused, the tree and registry kept), a batch landed,
  reopened by a `run` and landed again (drops, tree and cache gone, the registry's `lane` line gone), and a re-adoption then a
  drop of the tree gone from disk.

### T49 Approach (checklist part A)

1. **The goal, in the world.** A session retiring `<clone>-land` runs `make builder-tree-drop TREE=<it> REASON=` once the lane is
   idle, and is told what to stop first while it is not, with no `BUILDER_TREE_OK` escape.
2. **The constraints.** D1 (the lane's tree and its holder), T13 (`lane` reserved: no release frees it), T45 (the REMOVE message
   names the drop), T17 (the log and lock read without depending on the lane crate), the brief: refused while the runner lives or a
   batch is open, every builder tree's rules kept.
3. **Where each comes from.** R: tasks.md T49's line, T45's found-and-left item; O: `drop_tree`'s held check, the lane's
   `log::batches`/`state_of` and `runner::held`/`stop`, read 2026-11-27.
4. **Do they describe the world here?** Yes: the red test shows the old drop refused the lane's tree with the release T13 refuses.
5. **The order.** After T13, T17 and T45; before T22.
6. **The exits.** Green: the lane test and `make builder-checks` above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one caller of the held refusal (`drop_tree`), read.
8. **The budget.** One landing.
9. **Done, measured.** The lane drop test green; in use, `make builder-tree-drop TREE=/diagram/.clones/diagram-backlog-land
   REASON=...` with no runner and no open batch removes it.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session retiring the lane's tree is no longer left only the guard's escape; nothing else a reader sees
    changes.

**Found and left?**
- The lane's tree gone from disk mid-batch is still a dead end: `builder-tree lane`'s gone-from-disk refusal names the drop, which
  is refused while the runner lives (it made the call) and, after `make lane-stop`, while its batch stays open (resumed at the next
  start, which calls `lane` again). Not fixed here: the task's words refuse the drop while a batch is open, and the route a gone
  tree needs is a decision of its own. Filed as T50; lands before T22.

**Performance work?** no


### T50 (T49's found-and-left: the lane's tree gone from disk mid-batch was a dead end)

- **Approach**: the task line's first route, a re-made worktree at the registry's path. `lane_start`
  (`rust/gate/crates/task/src/builder_tree.rs`), finding the registry's lane tree gone from disk, runs `git worktree prune` (a
  hand `rm -rf` leaves git's record of the path, and the add would refuse it) and `git worktree add -q --detach <path> <the
  clone's HEAD>` from the clone, logs a `remake` line, says `was gone from disk: made again there, its build cache kept` on
  stderr, and falls through to the fetch, reset, clean and detach at `origin/main` as before. WHY THIS ROUTE, not the drop: the
  drop's route was the loop itself - refused while the runner lives (the runner made the call) and, after `make lane-stop`, while
  the batch stays open (resumed at the next start, which calls `lane` again); a `stop` of the open batch written from here, the
  brief's example, would put a second writer of `l7r-lane/lane.jsonl` in the `task` crate beside the lane's own (T14 is building
  the batch run there) and still leave drop-then-adopt, whose adoption needs a worktree at the path that only a hand `git worktree
  add` (refused, 451 T285) would make. The re-make loses nothing: `lane` already throws away whatever the tree held (step 4's
  `reset --hard`, `clean -fdq`, detach), a resumed batch carries onto it from `origin/main` as every batch does, and the build
  cache lives beside the tree by its name (`builder_pool::cache`, `<cache root>/<tree name>`, read 2026-11-27), so D1's reason for
  never making the lane's tree - a new tree starts cold - does not hold for one made again at the same path: its cache is warm
  where it survived. T13's "refused, never made" stands for a lane tree never adopted; only the gone-from-disk case changes.
  Where git cannot make it there (something stands at the path), the refusal names that and the `git worktree add` that says what,
  and no longer the drop: the next batch start makes it once the path is clear. No lane-crate edit; the drop (T49) is unchanged.
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/task ONLY="builder_tree::tests::lane"` on the old code): 4 passed,
  1 failed - `a_lane_tree_gone_from_disk_is_made_again_at_its_path_and_its_cache_kept` answered `is gone from disk - make
  builder-tree-drop ...`, code 2. Green: the same run 5 of 5; `make builder-checks CRATE="rust/gate/crates/task"` clean, the crate 158 of 158. The test: a
  batch open, the tree removed with no prune, `lane` re-makes it at `origin/main` with the cache's `debug/` kept, the registry's
  lane line kept and a `remake` line logged; then a file at the path, refused naming what is in the way and not the drop. The old
  gone-from-disk assertion of T13's adoption test moved into it.

### T50 Approach (checklist part A)

1. **The goal, in the world.** A lane whose tree vanished mid-batch carries on at its next batch start, warm where the cache
   survived, with no hand step and no escape.
2. **The constraints.** D1 (the lane's tree, its cache kept, step 4's rule), T13 (`lane` at a batch's start), T49 (the drop refused
   while the runner lives or a batch is open), 451 T285 (no hand `git worktree add`), the brief: lane-crate edits narrow (none made).
3. **Where each comes from.** R: tasks.md T50's line, T49's found-and-left item; O: `lane_start`, `drop_tree`, `make_cold` and
   `builder_pool::cache`, read 2026-11-27.
4. **Do they describe the world here?** Yes: the red test shows the old `lane` refused a gone tree with the drop T49 refuses.
5. **The order.** After T13 and T49; before T22.
6. **The exits.** Green: the lane tests and `make builder-checks` above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one gone-from-disk branch for the lane's tree (`lane_start`), read; the builders' own (`take`'s note
   naming the drop) is a free tree's, which the drop takes, and is left as it is.
8. **The budget.** One landing.
9. **Done, measured.** The lane test green; in use, a `rm -rf` of `<clone>-land` mid-batch is followed by a `remake` line in the
   pool's log at the next batch start and the batch's landing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session whose lane tree vanished is no longer sent round the drop's refusals; nothing else a reader sees
    changes.

**Found and left?** none

**Performance work?** no

### T51 (T14's start through the lane tree's launcher could say "holds no lock" of a runner still building; filed at T14's build half)

- **Approach**: `rust/gate/crates/lane/src/runner.rs`: `start` runs `prebuild(exe)` before the spawn - where `exe` is the launcher
  (file name `l7r-gate.sh`, `LAUNCHER`, which `runner_exe` returns for the lane's tree), it is run once in the foreground as
  `L7R_GATE_PRINT_FRESH=1 <exe>`, with the spawn's environment (`run::STRIPPED` removed) and without `L7R_GATE_STALE_OK` or
  `L7R_GATE_NO_BUILD` (either would make it build nothing), and waited for whole; a non-zero exit returns code 1 with cargo's stderr
  and spawns nothing; any other `exe` (the caller's binary, `runner_exe`'s fallback) builds nothing. The spawned launcher then finds
  the binary fresh and `exec`s at once, so `START_WAIT_S` (unchanged, a GUESS knob) covers the spawn to the lock alone - its doc comment and
  `dev/audits/lane-runner.md` say so. `start`'s signature and both callers (`lane.rs`, `on_hand_in`) are unchanged; the tests are a
  module of their own (`runner/start_tests.rs`), away from T14's closing half's edits of `runner/tests.rs`.
- **Measured** (method for each figure below: a `git clone --shared` of the lane tree at its commit efc35ccc4f in the scratchpad, a
  copy of the lane tree's `tool/` build cache as `L7R_GATE_TARGET`, `/usr/bin/time` over `L7R_GATE_PRINT_FRESH=1
  scripts/gates/l7r-gate.sh`, under a load average of 27 to 46 on 22 cores, measured 2026-11-27 (uptime)):
  - at its own commit with every source's time new, as a tree made again by T50 is, a whole-workspace rebuild of 101.75 s, measured 2026-11-27 (the scratch timing), not the same-commit cost.
  - Again at once, 0.05 s, measured 2026-11-27 (the scratch timing): fresh, no build.
  - efc35cc to e343e50, a day's move of 401 files under `rust/`, 112.08 s, measured 2026-11-27 (the scratch timing).
  - Across single landed commits, 15.02 s to 6174b208b5 (12 files), measured 2026-11-27 (the scratch timing).
  - 2.25 s to 950b1ccd56 (10 files) and 2.24 s to e343e5021e (2 files), measured 2026-11-27 (the scratch timing).
  - A touched file with no change 1.09 s, measured 2026-11-27 (the scratch timing).
  - A comment added to the core crate 4.92 s, measured 2026-11-27 (the scratch timing).
  - So every move past the smallest outlasts `START_WAIT_S`.
- **Decision 1 - prebuild, not a wait on the spawned child.** The brief offered both. Waiting while the detached child lives would
  need a new ceiling knob and would hide a failed build: the child's standard streams are `/dev/null` (T12's measured reason), so
  the start could say only "it exited 1". The prebuild's stderr reaches the caller with the command that rebuilds it alone, and
  the wait is the build's own end. Its cost: a source moved between the prebuild and the spawn (a reset in that instant) reopens
  the `START_WAIT_S` window, which only the runner resets, and it resets after it holds the lock. Label: the algorithmically easier route,
  the record silent (tooling, no research question).
- **Decision 2 - the start's callers wait out the build in the foreground.** `make lane-start` and, from T22's base, a hand-in's
  `on_hand_in` now block for the rebuild (up to the 112 s measured 2026-11-27, the scratch timing) where before they returned at `START_WAIT_S` with a false failure; for
  `make builder-done` that sits near a builder's 2-minute tool timeout. Dormant until T22 (Decision 6 of T12). Not fixed here: a
  background start or a prebuild at the lane tree's reset is a design choice for the hand-in path, outside the start path this
  brief scopes. Filed as T54; lands before T22.
- Red first, measured 2026-11-27 (make rust-test): `runner::start_tests` against the old `start`, 0 passed, 2 failed - the stale launcher's start returned
  "lane: started `.../gates/l7r-gate.sh lane --work ...`, but it holds no lock after 0.3 s" (the bug's own words; measured 2026-11-27 (make rust-test), a 0.6 s fake
  build against a 0.3 s wait), and the failing build's start returned 0 (the runner came up regardless). After, measured 2026-11-27 (make rust-test): 2 of 2, the lane
  crate 38 of 38, and `make builder-checks CRATE="rust/gate/crates/lane"` clean (test, lint, format).

### T51 Approach (checklist part A)

1. **The goal, in the world.** `make lane-start` (and a hand-in's start) says "started" of a runner that comes up after the lane
   tree's rebuild, and says why when that build fails, never "holds no lock" of a healthy runner.
2. **The constraints.** T12's start (the lock the truth, the runner detached with `/dev/null` streams, `START_WAIT_S`), T14's
   runner program (the lane tree's `scripts/gates/l7r-gate.sh`, `run::STRIPPED`), the launcher's `L7R_GATE_PRINT_FRESH`, the
   crate's own-tests coverage (rust/gate/CLAUDE.md), the brief's scope (the start path in runner.rs).
3. **Where each comes from.** R: plan.md T12 and T14, tasks.md T51, `scripts/gates/l7r-gate.sh`. O: the rebuild timings above
   (2026-11-27).
4. **Do they describe the world here?** Yes: the timings ran the lane tree's own commit and build cache through the real launcher;
   the tests drive `start` through `setsid` with a launcher stand-in that builds and takes the lock as the runner does.
5. **The order.** After T14's build half (the launcher as the runner's program); before T22 (the base flipped, which makes every
   hand-in start the runner); beside T14's closing half, whose edits are in `runner/tests.rs` and `run.rs`.
6. **The exits.** Green: the tests above and the lane crate whole. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one branch before the spawn.
8. **The budget.** One landing.
9. **Done, measured.** `runner::start_tests` 2 of 2 after 0 of 2 on the old code, the lane crate 38 of 38, measured 2026-11-27 (make rust-test).
10. **Before moving a constant.** n/a: `START_WAIT_S` keeps its value (a GUESS), its doc saying what it now covers.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes: a lane start that reported a false failure (and a hand-in's start line saying so) now
    reports the runner it started, or the build's error.

**Found and left?**

- A hand-in's start (`on_hand_in`) now waits in `make builder-done`'s foreground for the lane tree's rebuild, up to the 112 s
  measured 2026-11-27 (the scratch timing), near a builder's 2-minute tool timeout (Decision 2). Not fixed here: the hand-in path's design (a background start, or
  a prebuild at the lane tree's reset) is outside this start-path fix and dormant until T22. Filed as T54; lands before T22.

**Performance work?** no
### T52 (T14's build half, its decision 1: `make land`'s carry of the done refs read live carried a later hand-in into a lane batch)

- **Approach**: `carry_done` (`rust/gate/crates/land/src/land/carry_done.rs`) still reads the done refs live
  (`builder_done::to_carry`), but under `L7R_LANE_BATCH` (read through the landing's `Rooted`, so a test's own environment) it keeps
  only the commits whose sha starts with a change the batch's `batch` line in `l7r-lane/lane.jsonl` (the git common directory)
  names - the lane writes full shas, a short one matches too - and says the rest on one line, `land: lane batch <b>: left <n> done
  commit(s) its batch line does not name, for a later batch (461 T52, D14): <shas>`, their refs kept for the lane's next batch. The
  line is the LAST `batch` line naming the batch (a later `batch` line of the same id a new batch, as T49's reading and the lane's
  `log::batches` take it); a torn line is skipped, as the lane skips it. A `landed` line of the batch after it ends it: a by-hand
  `make land` with a done batch's id exported carries as before, never leaving its tasks' commits uncarried (round 2, the
  advisor's probe of "a landing outside the lane is unchanged"); a `stop` naming the batch ends nothing, since the lane resumes it
  - so T17's `"landed" | "stop"` rule is not copied, which would reopen the unbounded window on a resumed batch. Read in the land crate, not through the lane crate (which
  builds on `task`), as `tree`'s `state::batch_open` (461 T17) reads it - a fourth small reader of the log, kept private rather than
  making T17's helper public, which answers another question (open or not) and would put a second crate in this task. Of the
  brief's two fixes ("carries nothing" or "only the batch line's shas") the second: it holds D14 whether or not the lane carried
  first, and leaves `make land`'s carry the one that verifies a batch's commit is in HEAD. A batch no line names, or one a `landed` line
  ended (the variable exported by hand, no log), is no lane batch and carries as before; a landing outside the lane is unchanged (the variable unset,
  `batch_named` None before any read).
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/land ONLY="land::carry_done::tests"` on the old code): 5 passed,
  1 failed - `a_lane_batch_carries_only_the_commits_its_batch_line_names` carried both T1's named commit and T2's unnamed one
  (`notes/later.txt` in HEAD). Green: `land::carry_done::tests` 6 of 6; `make builder-checks CRATE="rust/gate/crates/land"` clean, the crate 221 of 221. The tests cover a short named sha carried beside an
  unnamed one left (its ref kept, the line said), a log holding another batch's line and a torn line, a batch whose every waiting
  commit is named (nothing said), and a batch no line names (both carried, nothing said). Round 2 (2026-11-27, the same
  command with the `landed` arm made a no-op): 5 passed, 1 failed - `a_batch_no_line_names_carries_as_before`'s landed batch
  carried only the named commit; after, 6 of 6, the batch line followed by a `stop` of it still filtering.

### T52 Approach (checklist part A)

1. **The goal, in the world.** A lane batch's landing lands exactly the hand-ins its `batch` line named; a task's later hand-in
   waits for the next batch with its done ref, whatever window a resumed batch spans.
2. **The constraints.** D14 (a batch takes its changes' shas when it forms; a later hand-in changes no open batch), D5 (the
   batch's changes), data-model.md's batch and log line, T17's rule (the log read in the land crate without the lane crate), the
   brief: a landing outside the lane unchanged; the land crate only (T14's closing half works in the lane crate).
3. **Where each comes from.** R: tasks.md T52's line, data-model.md ("A batch takes its changes' shas when it forms"), T14's
   build-half handoff decision 1; O: `carry_done` and `to_carry` read 2026-11-27, the red test.
4. **Do they describe the world here?** Yes: the red test shows the old landing carrying an unnamed done commit under the
   variable.
5. **The order.** After T14's build half; before T22 (as the task's line says).
6. **The exits.** Green: the carry_done tests and `make builder-checks CRATE="rust/gate/crates/land"`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: `carry_done` is `to_carry`'s one caller in the land crate; the lane's `runner/run.rs` sets
   `L7R_LANE_BATCH` and writes the `batch` line before `make land`, read 2026-11-27.
8. **The budget.** One landing.
9. **Done, measured.** The red test green; in use, the lane's first real batch (T23) with a later hand-in of a batched task left
   waiting, its `left` line in the attempt file.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A later hand-in landed under a batch that never named it, against D14: its gate run and NOTE are the
    batch's, and the lane's ref deletion keeps its ref, so the lane would carry it again as an empty pick in the next batch.

**Found and left?** none.

**Performance work?** no.


### T53 (found by 461 T14's build half: `make lane` misstates an open batch's change as superseded)

- **Approach**: `rust/gate/crates/lane/src/log.rs`, `log::state`: `in batch <b>` - an open batch's `batch` line names the sha and
  no `eject` is the last log line naming it - is asked right after `landed` and before `superseded`; `superseded`, `ejected` and
  `waiting` follow in their old order. The batch's commit is the one the lane lands (T52 carries only what the batch line names,
  D14), so the batch's own change reads `in batch`, and the later hand-in of its task stays `waiting` (data-model.md's prose: "That
  later hand-in is `waiting` until the batch ends"). An ejected change of an open batch, or a stopped batch's, is not in the batch,
  so with a later hand-in it reads `superseded` as before (the data model's "superseding it if the batch ejected it"). Moving
  `in batch` ahead of `superseded` departs from data-model.md's numbered list, which its own paragraph on a batch contradicts: a
  deliberate deviation, labeled in the module doc. Callers: `make lane`'s listing (`lane.rs`, which now shows the batch's change)
  and `batch::form`'s `waiting` filter (unchanged: an in-batch or superseded hand-in was never batched).
- Red first (2026-11-27, `make rust-test CRATE=rust/gate/crates/lane ONLY="log::tests"` on the old code): 7 passed, 1 failed -
  `an_open_batch_s_change_is_in_batch_though_a_later_hand_in_of_its_task_exists`, `Superseded` against `InBatch("461-4")`. Green:
  `make builder-checks CRATE="rust/gate/crates/lane"` clean, the crate 50 of 50; the test also pins the later hand-in `waiting`,
  and the earlier `superseded` once its batch ejects it or stops.
- **Test only, the coordinator's addition**: the session's pre-gate coverage named `runner.rs`'s `on_lane(common)` (its
  `.map(|h| h.commit)`, line 504) reached by no test; a new module `runner/on_lane_tests.rs` writes a pool log `handed_in` line
  and a done ref in a scratch git common directory and asserts `on_lane` returns that commit, and not a hand-in no ref or lane
  line names (2026-11-27, `make rust-test CRATE=rust/gate/crates/lane ONLY=runner::on_lane_tests`: 1 of 1). Not red first: no
  code changed, a coverage gap.

### T53 Approach (checklist part A)

1. **The goal, in the world.** `make lane` shows the change an open batch is landing as `in batch <b>`, and a later hand-in of
   its task as `waiting`, so the coordinator reads what the batch carries.
2. **The constraints.** D8 (states computed), D14 (a batch takes its shas when it forms; a later hand-in moves no open batch),
   data-model.md ("A hand-in"'s order, "A batch"'s paragraph on the later hand-in), T11's order, T52's carry; the brief: log.rs
   and its tests only (T15 edits runner/run.rs elsewhere).
3. **Where each comes from.** R: tasks.md T53's line, data-model.md, plan sections T11 and T52; O: the red test.
4. **Do they describe the world here?** Yes: the red test reproduces the misstatement on the old code; `log::state`'s callers
   read 2026-11-27 (`lane.rs`, `batch.rs`), none relying on a batch's change reading `superseded`.
5. **The order.** After T11, T14's build half and T52; before T20.
6. **The exits.** Green: the log tests and `make builder-checks CRATE="rust/gate/crates/lane"`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: `log::state` and its callers in `lane.rs` and `batch.rs`, read 2026-11-27 (`grep -n log::state`).
8. **The budget.** One landing.
9. **Done, measured.** The red test green; in use, `make lane` over the first lane batch with a later hand-in of a batched task.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The coordinator reading `make lane` sees the batch's change as superseded and no change `in batch`,
    against what the batch lands (D8's states misstated).

**Found and left?** none.

**Performance work?** no.

### T54 (T51's Decision 2: a hand-in's runner start waits in `make builder-done`'s foreground for the lane tree's rebuild; filed at T51)

- **Approach**: `rust/gate/crates/lane/src/runner/run.rs`: `run_batch`, right after `builder-tree lane` brings the lane's tree to
  `origin/main` and before the changes to carry are read, runs T51's `prebuild` on the tree's own `scripts/gates/l7r-gate.sh` where
  that file exists (the run tests' worlds have none), its result ignored. The hand-in path (`on_hand_in`, `start`) is unchanged.
- **When a start can find the lane tree stale** (read from the code, 2026-11-27): the launcher's staleness is `find -newer` over the
  sources (`scripts/gates/l7r-gate.sh`'s `stale`). Two writers move the lane tree's sources. The runner's `run_batch` resets it, then
  carries (`make carry`, whose launcher builds) and lands (`make land`, whose `LAND_RUN` builds again after the carries).
  `scripts/land-alone.sh`'s reset step resets the same tree (`<clone>-land`), and its landing step runs `make land` there, which builds. So after
  either writer the binary is fresh, and the 2.2-112 s T51 measured (measured 2026-11-27, T51's scratch timing) reaches a start only
  where a reset was followed by no `make`:
  1. a batch whose every change `origin/main` already holds (`todo` empty: a resumed batch whose push went out, the Recovery case),
     T50's re-made tree included - the whole move since the last build, up to the 112 s of a day's move and 102 s for a re-made tree, measured
     2026-11-27 (T51's scratch timing). CLOSED HERE.
  2. a runner killed between the reset and the build - the rest of that build. Accepted (below).
  3. a stopped carry - the carried files' rebuild, up to the 15.02 s T51 measured for a 12-file commit (measured 2026-11-27, T51's scratch timing), but where the conflict is in
     a file the gate builds from, a failed build and no runner at all (Found and left, T55).
- **Decision 1 - the build at the reset (route B), not a background start (route A).** Priced 2026-11-27, by reading:
  - Route A, the prebuild inside a detached child of the hand-in. It needs a new detached path in `start` and its tests. Its
    failure must reach the coordinator as an `owed` line (data-model.md's event; T20's `make lane-wait` prints only `owed` lines).
    The hand-in would lose its `started (pid N)` line, and T51 Decision 1's reason (a build failure the caller sees) would come back
    as a deferred line. It covers cases 1-3's waits, but not case 3's failure.
  - Route B: a call after the reset, in the lane crate. In the common batch (a carry follows) it adds no build: it makes, earlier, the
    build `make carry`'s launcher would make, and the carry's moved files are rebuilt by `make land` as before. It closes case 1,
    the only unbounded case on a live runner. Cases 2 and 3 are left.
  - Chosen: B, the cheaper. It is sound for the hand-in's wait: the residual waits are bounded by one carry's files or one killed
    build. No log line is written, so nothing is added to data-model.md's events.
  - Label: the algorithmically easier route, the record silent (tooling, no research question).
- **Decision 2 - a failed build at the reset stops no batch.** Where a carry follows, `make carry`'s own launcher fails on the same
  build and the carry's error (the `carry` line, the runner's `error:`) says so, as before. Where none follows, the next start's
  prebuild (T51) says why to its caller. Making it an error here would add a third route to the same report.
- **Accepted limitation (case 2)**: a runner killed between the reset and its build leaves the next start the rest of that build in
  the foreground, up to the 112 s above under the same load (measured 2026-11-27, T51's scratch timing). Its cost: one hand-in's wait, near the 2-minute tool timeout, after a
  `make lane-stop NOW=1` or a crash in that instant. Alternatives priced: route A covers it at the cost above. Chosen by: this
  builder, under T54's brief, which asks for the cheaper sound route.
- Red first, measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/lane ONLY="runner::run::tests"`): the new test
  `a_reset_with_nothing_to_carry_leaves_the_lane_tree_s_launcher_built_so_the_next_start_builds_nothing` against the old
  `run_batch`, 7 passed, 1 failed (`left: None`, `right: Some("built <origin sha>")`: no build after the reset). After, measured
  2026-11-27 (`make builder-checks CRATE="rust/gate/crates/lane"`): the lane crate 40 of 40, lint and format clean. The test commits
  a stand-in launcher (it builds where the tree's HEAD moved since its last build, its marks in the git common directory, out of
  the reset's `clean`) and moves `origin/main` past a landed batch. It then resumes a batch `origin/main` already holds: one build
  at the new HEAD, and T51's `prebuild` after it builds nothing. Then, with the build failing, a further batch still lands.

### T54 Approach (checklist part A)

1. **The goal, in the world.** A hand-in's runner start from T22's base finds the lane tree's `l7r-gate` built, so `make
   builder-done` does not wait out a rebuild near a builder's tool timeout.
2. **The constraints.** T51's start (its prebuild and its error words), T12's start and lock, T14's batch run (`run_batch`, steps
   1-4), T50's re-made tree, data-model.md's events (none added), the crate's own-tests coverage (rust/gate/CLAUDE.md).
3. **Where each comes from.** R: plan.md T51, T12, T14; tasks.md T54; `scripts/gates/l7r-gate.sh` (`stale`), `scripts/land-alone.sh`
   (its reset and landing steps). O: T51's rebuild timings (2026-11-27).
4. **Do they describe the world here?** The staleness cases are read from the code above. The timings are T51's, on the lane
   tree's own commit and build cache. The test drives `step` and `resume` against a real bare `origin` and the pool's lane tree.
5. **The order.** After T51 and T14; before T22, which makes every hand-in start the runner.
6. **The exits.** Green: the new test, and the lane crate whole. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one call after the reset.
8. **The budget.** One landing.
9. **Done, measured.** The new test red then green, the lane crate 40 of 40, measured 2026-11-27 (make rust-test, make builder-checks).
10. **Before moving a constant.** n/a: `START_WAIT_S` is unchanged.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. A hand-in after a batch that carried nothing now starts its runner at once, where it waited
    out the whole move since the last build.

**Found and left?**

- A stopped carry leaves its cherry-pick in progress in the lane's tree (`rust/gate/crates/land/src/land/carry.rs`: "the stop leaves
  the pick in progress"). Where the conflict is in a file the gate builds from, the next start's prebuild (T51) fails on the
  conflict markers and starts no runner. Only the runner's resume resets that tree, so from T22's base every hand-in says "could
  not be built" and the open batch is never resumed. Found by reading, not run. Not fixed here: it is the start's handling of an
  open batch's tree, outside the build-at-reset this brief prices, and route B does not reach it. Filed as T55; lands before T22.

**Performance work?** no - it removes a foreground wait that does not yet happen (dormant until T22's base), and it times nothing.


### T55 (T54's Found and left: a stopped carry's conflict in the lane's tree fails every later start's build, and only the runner's resume resets that tree; filed at T54)

- **Approach**: `rust/gate/crates/lane/src/runner.rs`: `start`, after its lock check (no runner lives) and before T51's `prebuild`,
  asks `stopped_carry`: the registry's lane tree has `CHERRY_PICK_HEAD` (`git -C <tree> rev-parse -q --verify`, which a linked
  tree answers for itself) AND the lane's log's last batch is open with its last `carry` line's code not 0. Where both hold,
  `reset_stopped` makes the resume's own call, `builder-tree lane` (`l7r_gate_task::builder_tree::cli`, as `run_batch` calls it),
  which fetches and brings the tree to `origin/main` (`reset --hard`, `clean -fdq`, `checkout --detach`), and says so in a stdout line
  before the start's own. A reset that fails is the reply's stderr and the start goes on, so the build's own words follow it. The
  rest of `start` moves unchanged into `start_built`. `start`'s signature and its callers (`lane.rs`, `on_hand_in`) are unchanged;
  `run.rs` is not touched (T15's).
- **Decision 1 - the reset first, not the prebuild skipped.** Read 2026-11-27 in `scripts/gates/l7r-gate.sh`: the launcher builds
  where stale in both modes (the `elif stale` branch runs whether or not `L7R_GATE_PRINT_FRESH` is set), and it never falls back to
  the binary it has. So a skipped prebuild only moves the failed build into the detached child, whose streams are `/dev/null`, and the
  start says "holds no lock". Spawning with `L7R_GATE_STALE_OK` instead would leave that variable in the runner's environment, and
  through it in every `make carry` and `make land` the runner runs. `run::STRIPPED` (run.rs, T15's file) does not remove it. The
  reset is what the resume does at once anyway (`run_batch`'s first step), so it removes nothing the runner needs. Label: the
  algorithmically easier route, the record silent (tooling, no research question).
- **Decision 2 - both halves of the condition.** `state_of` reads any `carry` line as gating, so the code is asked of the line. The
  log half matters because `scripts/land-alone.sh` shares the lane's tree: a pick in progress there with no stopped carry open is
  not the lane's to discard, and is left alone (pinned by a test).
- **After the reset** the runner starts, resumes the batch and carries again. A conflict with `origin/main` still there stops the
  carry again, and the runner stops with the batch open as before. That repeat is T25's (phase 3: a carry conflict becomes a repair
  entry), not a deadlock: each start makes one more attempt and says why it stopped.
- Red first, measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/lane ONLY="runner::start_tests"`), the three new tests
  against the old `start`: 3 passed, 2 failed. The stopped carry's start returned the deadlock's own words, "lane: the runner's
  program could not be built (exit 1), so no runner started ... error: this file contains an unclosed delimiter". The failing reset
  said nothing of the reset. The test world is a real one: a bare `origin`, a clone, and the lane's tree in the pool's registry with
  a hand-in's `rust/x.rs` cherry-picked onto a moved `origin/main` and stopped in conflict. The lane's log holds `batch`, `carry` (code
  2) and the runner's `stop`. A stand-in launcher fails on conflict markers under `rust/` in both modes, as cargo would. After,
  measured 2026-11-27 (`make builder-checks CRATE="rust/gate/crates/lane"`): the lane crate 43 of 43 (40 before), lint and format
  clean.

### T55 Approach (checklist part A)

1. **The goal, in the world.** After a batch's carry stops in a file the gate builds from, the next `make lane-start` (or, from
   T22's base, a hand-in's start) starts a runner that resumes the open batch, where every start had failed to build.
2. **The constraints.** T51's start (its lock check first, its prebuild and its words), T54's build at the reset, T14's batch run and
   Recovery (the resume brings the tree to `origin/main`), T13's `builder-tree lane`, `land`'s carry ("the stop leaves the pick in
   progress"), `land-alone.sh`'s shared use of the tree, the crate's own-tests coverage (rust/gate/CLAUDE.md), the brief's scope (the
   start path in runner.rs; T15 edits run.rs).
3. **Where each comes from.** R: plan.md T51, T54, T14, T13; tasks.md T55; `scripts/gates/l7r-gate.sh` (`stale`, both modes),
   `rust/gate/crates/land/src/land/carry.rs`, `rust/gate/crates/task/src/builder_tree.rs` (`lane_start`). O: the red and green runs
   above (2026-11-27).
4. **Do they describe the world here?** Yes: the tests drive `start` through `runner_exe` and `setsid` against a real conflicted
   cherry-pick in a registered lane tree, a bare origin, and the real `builder-tree lane`.
5. **The order.** After T51 and T54; before T22, which makes every hand-in start the runner; beside T15 (run.rs, untouched here).
6. **The exits.** Green: the three new tests and the lane crate whole. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one check and one call before the build.
8. **The budget.** One landing.
9. **Done, measured.** `runner::start_tests`: 3 of 5 on the old code, 5 of 5 after; the lane crate 43 of 43, measured 2026-11-27 (make rust-test, make builder-checks).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. A start after a stopped carry now resets the lane's tree and starts the runner, where it
    failed on the conflict markers and no batch was ever resumed.

**Found and left?** none - the resumed batch stopping again on the same conflict is T25's planned work (phase 3), not a defect left here.

**Performance work?** no
### T56 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T56 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T57 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T57 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T58 (T51's stale-launcher start test red 2 of 30 under load, "holds no lock after 0.3 s", measured 2026-11-27 (T15's build half, 3x10 at once), filed there)

- **Approach**: the defect is the TEST's own bound, not the runner's start; `rust/gate/crates/lane/src/runner/start_tests.rs` alone
  changes, `runner.rs` not at all. The tests' starts take `WAIT_S` (3.0 s, a GUESS knob of the test module with its measured why) in
  place of 0.3 s and the stopped-carry tests' 2.0 s (each a GUESS of T51's and T55's), and the fake launcher's build is 3.5 s, so the build still outlasts the start's
  wait, as the lane tree's rebuild outlasts `START_WAIT_S`, and in its runner mode it sleeps 0.5 s before the lock, a loaded
  machine's slow spawn pinned. A lock seen ends the wait at once, so the longer bound costs a green run nothing; the build costs
  the one test 3.5 s, measured 2026-11-27 (make rust-test).
- **Measured** (method for each figure: the lane test binary run whole-crate, ten at once, under `uptime`'s load on 22 cores, the
  start's wait timed by a scratch `eprintln!` in `start_built`, removed after, 2026-11-27):
  - Before, 0 red of 30 at load 15-47, then 2 red of 60 at load 31-86, measured 2026-11-27 (the lane binary 6x10): this test 1 ("holds no lock after 0.3 s", 0.623 s with no lock) and one other, below.
  - Spawn to lock over the 419 starts that came up: median 0.066 s, 99th percentile 0.471 s, longest 0.749 s, measured 2026-11-27 (the timed wait), and at `START_WAIT_S` (5.0 s) not one of 300 real starts failed, measured 2026-11-27 (the timed wait).
  - The runner's own take against the probe (a scratch test: `work_cli` run 20 times beside a thread calling `held()` every 20 ms, the binary 3x10 at once, load 17-35): 0 quiet leaves of 600 takes, measured 2026-11-27 (the scratch race test, removed after), so `TAKE_S` (1.0 s) is not lost to `free()`'s brief lock.
- **Decision 1 - fix the test, not the start; no wait read against the child's state.** The task line offered the child's state.
  The measurements above show no production start failing: `START_WAIT_S` holds 6.7 times the longest spawn to lock at load 86,
  and the runner's take never lost to the probe. A wait on the child would add a ceiling knob and was priced and declined by T51
  (Decision 1) for hiding a failed build; with no wrong outcome in the start (constitution XIV) the test's bound is the defect.
  Label: the algorithmically easier route, the record silent (tooling, no research question).
- Red first, measured 2026-11-27 (make rust-test): the fake's spawn slowed 0.5 s against the old 0.3 s bound, 10 of 10 red, "holds
  no lock after 0.3 s". After, measured 2026-11-27 (make rust-test): `runner::start_tests` 5 of 5; the start without its prebuild
  still red ("holds no lock after 3 s", measured 2026-11-27 (make rust-test)), so the test still tells T51's fix, and the lane binary 6x10 at once at load 19-61, 0 red of 60, measured 2026-11-27 (the lane binary 6x10).

### T58 Approach (checklist part A)

1. **The goal, in the world.** The lane crate's start tests are green at load, and stay red against a start that skips its build.
2. **The constraints.** T51's start (the prebuild, `START_WAIT_S`), T14's lock probe (`free`, `TAKE_S`), the brief's scope
   (runner.rs's start path and start_tests.rs; T15's closing half edits `runner/run.rs`), the crate's own-tests coverage.
3. **Where each comes from.** R: tasks.md T58, plan.md T51 and T14. O: the load runs above (2026-11-27).
4. **Do they describe the world here?** Yes: the runs used the crate's own test binary, whole, ten at once on the shared machine
   at the loads named.
5. **The order.** After T51 and T55 (their tests); before T23.
6. **The exits.** Green: the 6x10 run at load clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one constant and the fake's timings.
8. **The budget.** One landing.
9. **Done, measured.** 10 of 10 red before, 0 of 60 red after at load, measured 2026-11-27 (the lane binary 6x10).
10. **Before moving a constant.** `START_WAIT_S` unmoved; the tests' 0.3 s and 2.0 s were no claim's, now `WAIT_S` (a GUESS with its measured margin).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes: a red batch gate's false red from this test is gone; the start itself behaves as before.

**Found and left?**

- A start or a stop can name a dead runner's pid: `holder` reads the lock file while it is held, and a new runner holds the lock before `work_cli`'s `set_len(0)` and pid write, so the file still names the last killed runner; `runner::tests::a_runner_deaf_to_term_...` red 1 of 60 (pid 884049, the killed runner, against 887300), and a stop would signal that dead pid's group. Not fixed here: the race is in `work_cli` and `holder` and its test in `runner/tests.rs`, outside this brief's start path, and T15's closing half edits beside it. Filed as T62; lands before T23.

**Performance work?** no

### T62 (T58's found-and-left: a lane start or stop could name a dead runner's pid, `runner::tests::a_runner_deaf_to_term_...` red 1 of 60 at load 31-86, measured 2026-11-27 (T58's lane binary 6x10))

- **Approach**: `rust/gate/crates/lane/src/runner.rs`'s `holder()` names the pid read from the lock file only where that process holds the lock itself (`holds`: one of `/proc/<pid>/fd` is the lock file by device and inode, and its `/proc/<pid>/fdinfo/<fd>` lists a `FLOCK` lock - the kernel lists a lock only on the open file holding it, observed 2026-11-27 (a shell holding `flock` on fd 9 beside a second open of the same file: the lock line on the first alone)); `stop` in the window, the lock held and no holder named, signals nothing and says so. Its tests in `runner/tests.rs`. With it, three lines the session's pre-gate coverage named (2026-11-27 about 23:40Z), tests only: `work_cli`'s real `sleep` (a new test, the idle a minute and a stop request ending it, since with the 0.05 s idle a slow first step outlasts the idle and the loop never sleeps), `wake/tests.rs`'s `n == 50` guard (one line, `assert!(n < 50)`, so the guard no right answer reaches runs no unrun line and a regression is still a red, not a hang on the fake clock), and `rustc/run.rs` line 205 - covered in `tested`'s instance of the generic `leak_checked`, but its instances for `side::run_built` and `cover::run_job` were never called with an entry inside `l7r-tmp/` (the lcov's `FNDA:0` on both, observed 2026-11-27 (the cover run's `lcov-rustc.info`)), so `tests/side.rs`'s and the cover world's leaks gain one there.
- **Decision 1 - the reader proves the pid, the writer's order unchanged.** The task offered writing the pid before the lock is seen held: a runner cannot write before it wins the lock without overwriting a live runner's pid when it loses, and the cited red went through the tests' shell stand-ins (`flock` then `echo $$`), which a `work_cli` reorder would not reach. So `holder()` refuses a pid not holding the lock - a dead pid, a zombie (descriptors closed) or a reused pid all hold none - rather than "a live child of" anything (the runner is in a session of its own, nobody's child). No retry knob: in the window `holder()` is `None`, which a start already polls through (`start_built`'s wait) and a stop already said before (the empty file after `set_len(0)`); a stop now says the lock is held and asks again. Label: the algorithmically easier route, the record silent (tooling, no research question).
- **Decision 2 - Linux `/proc` read for the proof.** The lane runs only in the Linux container; the stall watchdog already reads `/proc` for the runner. Label: convention (the watchdog's own reading).
- Red first, measured 2026-11-27 (make rust-test): `runner::tests::a_pid_is_named_only_where_its_process_holds_the_lock_itself` - the lock held in process, the file naming a dead pid (a reaped child's), then a live pid holding no lock, then this process's own - 0 passed, 1 failed on the old code (`holder` returned the dead pid); after, `runner` and `wake` 48 of 48. The lane test binary whole, 6x10 at once at load 10-53 on 22 cores: 0 red of 60, measured 2026-11-27 (the lane binary 6x10).

### T62 Approach (checklist part A)

1. **The goal, in the world.** A lane start or stop names, and a `NOW=1` stop signals, only the process that holds the runner's lock - never a killed runner's pid or whatever reused it.
2. **The constraints.** T12 Decision 1 (the lock is the truth, the pid secondary) and Decision 9 (`TAKE_S`); T58's start bound; the crate's own-tests coverage; the brief's three named lines.
3. **Where each comes from.** R: tasks.md T62, plan.md T12, T14, T58. O: T58's 6x10 red; the fdinfo observation and the lcov above (2026-11-27).
4. **Do they describe the world here?** Yes: the red test forces the window in the crate's own test binary on this machine; the fdinfo lock line was observed on this kernel.
5. **The order.** After T58; before T22 and T23.
6. **The exits.** Green: the red test green, the lane binary 6x10 at load clean, and the cover run over `lane` and `rustc` naming no line. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one reader and its proof.
8. **The budget.** One landing.
9. **Done, measured.** 0 passed, 1 failed before; green after; 0 red of 60 at load 10-53, measured 2026-11-27 (the lane binary 6x10).
10. **Before moving a constant.** n/a: no constant moved or added.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes: a stop in the start's window says the lock is held and signals nothing, where it signalled the last runner's pid's group.

**Found and left?** none

**Performance work?** no


### T59 (phase 1: the likeness test counts the lane's tree as a builder's; found by T10's measurement)

- **Approach**: in pool tree `diagram-backlog-t271`, bundled with T60.
  - **Measured** (observed 2026-11-27, method: `night-figures.py`'s `concurrency` and `load_figures` over 19:57:00Z-23:03:20Z, the pool
    log from T10's kept extract and the live samples, a probe script in the scratchpad): trees held 3.55, the sampler's held mean 3.18 over
    1,065 samples, on the old script - the pool log's `adopt` of `/diagram/.clones/diagram-backlog-land` with detail `lane` (21:08:09Z, never
    released) replayed as a hold, and `len(held)` counting `lane`.
  - **The script** (`dev/measurements/2026-11-27/461-t01-night-tokens/night-figures.py`): `LANE = 'lane'`, the guard's
    `shared::builder_pool::LANE`; `held_spans` treats an `adopt` of `lane` as no hold and as the end of one (a tree adopted for the lane
    is no builder's from then), unless `lane=True` asks for it; `concurrency` passes that through; `sample_rows` counts `held` without
    `lane`. `phase1.py` (T10's) drops its own `-land` suffix filter and asks `concurrency(..., lane=True)` for its "with it" figure, so
    T10's outputs re-derive. After: trees held 2.94, the sampler's mean 2.98 (same method); T10's two kept figures runs, `phase1.py figures`
    over 19:57Z and 21:06:47Z with `--kept`, byte for byte their recorded outputs; T02's night, `figures` 04:30Z-14:29Z with `--kept`, its
    output and `ref-0430-1429.json` unchanged (no lane then); `like` over 19:57Z-23:03:20Z reads trees held 2.94 (observed 2026-11-27,
    method: those commands, diffed against the recorded files).
  - **The sampler** (`rust/gate/crates/measure/src/measure/sampler.rs`'s `sample`): already reads `shared::builder_pool::read`, which
    leaves the lane out since T13 (landed 20:52Z). The 215 samples naming `lane` (21:08:12Z to 21:43:55Z) came from pid 3387947, started
    09:44:04Z, before T13, which ran until its `L7R_SAMPLE_MAX_H` ended at 21:44:05Z; the sampler started 21:52:53Z lists no `lane`
    (observed 2026-11-27, method: `sampler.log` and each sample's `held` in `mem-samples.jsonl`). So no code change: the sampler test's
    fixture now holds a lane tree, and `a_sample_reads_the_cgroup_and_proc_and_leaves_out_what_its_file_does_not_give` pins `held`
    without it. Not red first: the code it pins was right from T13; the red is the script's, above.
  - **Decision: the lane told by its holder, not its path.** `lane` is the registry's reserved word (T13) and the pool log's adopt detail;
    the `-land` suffix is a naming habit. Label: the algorithmically easier route, one word shared with the guard.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: a measurement script and a test fixture | - | - | - | - |

### T59 Approach (checklist part A)

1. **The goal, in the world.** The likeness test's trees held, and its sampler cross-check, count builders' trees only, so T31's like window
   is judged against the night's 3.19 on the same footing.
2. **The constraints.** Plan D12 (the likeness test), FR-010 (every figure beside its concurrency), T13 (the lane's reserved holder), T10's
   record kept re-derivable.
3. **Where each comes from.** R: plan D12, T13's section; O: the runs above (2026-11-27).
4. **Do they describe the world here?** Yes: the live pool log, the live samples and T10's kept extracts.
5. **The order.** After T10; before T31, which reads the like window.
6. **The exits.** Green: 2.94 and 2.98 from the script, T10's outputs re-derived. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The sampler's half was a stale process, not code: named above and filed.
8. **The budget.** One landing.
9. **Done, measured.** The probe's figures 2.94 and 2.98; `make builder-checks CRATE="rust/gate/crates/measure"` green (observed 2026-11-27,
   method: those commands).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** T31's like window would read about 0.6 tree high against the night's 3.19, its band 0.5 (GUESS, plan D12),
   enough to pass or fail a window wrongly (observed 2026-11-27, method: the probe above): fixed here.

**Found and left?**
- The memory sampler runs the code it started with for its whole `L7R_SAMPLE_MAX_H` (12 h), so a change to what it reads reaches its
  samples only at its next start: 215 samples listed `lane` after T13 had left it out (observed 2026-11-27, method: `sampler.log` against
  T13's landing). Not fixed here: a restart-on-rebuild is a mechanism of its own, past this fix's size. Filed as T61; lands before T31.

**Performance work?** yes - a measurement script of where the builders' concurrency goes (451 FR-013: a measurement task counts).


### T60 (phase 1: a build half's hand-in refused for the feature-close ask; found by T10's measurement)

- **Approach**: in pool tree `diagram-backlog-t271`, bundled with T59.
  - **What refused, measured** (observed 2026-11-27, method: T10's record, `dev/measurements/2026-11-27/461-t10-phase1/output-1957-2303.txt`,
    the call's own tool result): 451 T537's build half at 22:06:03Z, "this tick would close the feature, and: 451 has no report.md ... review
    passes with no ledger row" - the closing check `tick::checks`' `close_owed` joins to the last task's refusal where the tasks asked are the
    feature's last open boxes (451 T307 part 2). Its closing half answered both and handed in on the same tree at 22:44:14Z.
  - **The change** (`rust/gate/crates/task/src/tick/refusal.rs`, `Section`; `tick.rs`, `checks`; `land/hand_in.rs`, `section_of`): T44's
    `Later` splits in two - `Closing`, a build half's hand-in, puts off the section's two asks and the close (`close_owed` not asked);
    `Later`, a measurement's, puts off the section's two asks alone, its close still asked. A fix's or a closing half's hand-in
    (`Owed`), `make tick`, `l7r-gate tick --land-check` and the landing (`Pass::Landing`, always `Owed`) ask everything. The first
    pass's own ledger-row row (`land/cheap.rs`, a pass with no row) is not the close's and stands at every kind.
  - **Decision: the close put off for a build half alone, not for a measurement.** The close's reasons (a report, the close's ledger
    rows, the implementation check) are the closing half's work, and a closing half always follows a build half; nothing follows a
    measurement, so its builder answers its feature's close at hand-in, as before (the plan review's round 1, BLOCKED on the
    measurement limb, SC-002: a hand-in submitted once it is ready to land). This narrows the task line's "a build half and a
    measurement" to the half the reason covers. Label: the algorithmically easier route that cannot loosen the landing.
  - **The docs**: `refusal.rs`'s `Section` doc, `checks`' doc, `hand_in.rs`'s step 6 and `section_of`, and `scripts/container/builder-brief.md`'s
    THE BUILDER HANDS IN ITSELF (the close put off with the two asks, the landing asking all three).
  - **Red first** (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/task ONLY="tick::tests"` and `CRATE=rust/gate/crates/land
    ONLY="land::hand_in::tests"` with the new assertions on the old code): task 13 passed, 1 failed
    (`the_last_tick_closes_only_past_the_closing_check_and_the_archive_is_recorded`, its new `Section::Later` assertion); land 27 passed, 1
    failed (`a_build_half_of_the_feature_s_last_task_hands_in_with_its_close_still_to_come`, at the hand-in: the landing's half of it, the
    close still asked of `Pass::Landing`, passed on the old code, as it must, and so do the fix's and the measurement's hand-ins still
    refused, added after round 1). After: `make builder-checks CRATE="rust/gate/crates/task rust/gate/crates/land"`: task 160 passed,
    land 223, lint and format clean (`rust/gate/crates/measure` 307 for T59).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the hand-in's close put off | n/a - no map | n/a | none | n/a |

### T60 Approach (checklist part A)

1. **The goal, in the world.** A build half hands its own work in when its task is the feature's last open box; the closing half, a
   measurement's own hand-in and the landing still owe the close.
2. **The constraints.** US2 (a refusal a builder can answer is answered by the builder that has the context), T44's mode and its rule that the
   landing asks everything, FR-002 (no coverage at hand-in).
3. **Where each comes from.** R: US2 (spec.md), T44's section; O: T10's record (2026-11-27).
4. **Do they describe the world here?** Yes: the refusal is the real call's, and the tests run the real first pass through the hand-in.
5. **The order.** After T44 and T10; before T31.
6. **The exits.** Green: the task and land crates' tests and `make builder-checks`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/task rust/gate/crates/land"` green (observed 2026-11-27, method:
   that command, its log's tail).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A build half of a feature's last task refused at hand-in for work only its closing half does, 38 minutes and a second
   builder's run (451 T537, observed 2026-11-27, method: T10's record): fixed here.

**Found and left?** none.

**Performance work?** yes - it makes the builders' loop faster (451 FR-013): a build half of a feature's last task hands in without
waiting on its closing half.


### T61 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T61 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T63 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T63 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T64 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T64 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

