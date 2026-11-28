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
<!-- plan-archive: T10 to T43 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
<!-- plan-archive: T11 to T22 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->

### T23 (phase 2's measurement on real work: the lane's first batches, 2026-11-28T02:00Z to 06:20Z; D1, D9, D11)

- **Approach**: nothing changes. Read-only scripts under `dev/measurements/2026-11-28/461-t23-lane-first-batches/` read the lane's log (its snapshot `lane.jsonl`), every `make land` Phase line, the sampler, the main session's transcript and origin/main's ticks; their outputs are beside them and are read in `results.md`. Concurrency (FR-010): W0 20:00Z-02:02Z trees held 3.46, load1 median 14.4; W1 02:02Z-05:49Z 2.87, 19.2; W2 05:49Z-06:20Z 3.46, 31.6, on 22 cores, measured 2026-11-28 (t23-conc.py). None is a like window, W2 being 31 minutes long, measured 2026-11-28 (t23-conc.py). (1) Of 8 batches only 461-3 (T81, T93/T86) landed by the lane, in 1 green run of 28.5 min with its own push, measured 2026-11-28 (t23-batches.py). 462-1 and 462-3 ejected every change `unplaced` (r1, r3); 462-2 and 462-4 ejected T278 and T321 after each had landed by hand (r2, r4); 461-1 and 461-2 were landed by hand and read back, measured 2026-11-28 (t23-batches.py). The coordinator landed 8 times by hand, 21 tasks, each for a lane defect since fixed, and the runner needed 22 starts, 21 of them resumes, measured 2026-11-28 (ticks.out and t23-batches.py). (2) In W2 1 batch of 2 changes and 3 tasks landed without a hand, its hand-ins waiting 73.6 and 39.3 min to the push, measured 2026-11-28 (lane.jsonl and make lane); 462-5 took one change of a queue alternating features (D5). (3) The coordinator's model calls on landing per landed task were W0 2.1 (102 of 408 calls, 48 tasks by hand), W1 8.6 (146 of 330, 17 by hand) and W2 3.0 (9 of 23, 3 by the lane: 6 wakes and r3's re-hand-ins by hand), measured 2026-11-28 (t23-coord.py). (4) Still the lane's to do by itself: T96, T95, T77/T79 (in the lane), T78, then phase 4. D1: b1 ran no gate; the lane tree's first gate took 15.9 min and compiled 302 cover-build crates against 11 to 42 for every later gate in either tree, measured 2026-11-28 (t23-gates.py); the later lane gates took 13.2 and 23.1 min at load 30 against the clone's 4.1 to 15.1 min at load 6 to 23, measured 2026-11-28 (t23-gates.py); D1 stands, the cache warm after one gate. D9: 32 waits all completed on a lane line, the longest 27.4 min and 27.1 past its turn, measured 2026-11-28 (t23-wait.py): no limit found, so `LANE_WAIT_MAX` is not priced. D11: gates built in the clone until 05:48:13Z and its target directory holds the `l7r-gate` that `make lane-wait` runs, measured 2026-11-28 (t23-gates.py and ps), so it is kept and T29 reopens it. The task line's verify, `make task-time` showing the lane tree's Phase lines, fails: T100.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the read | n/a: nothing changed | n/a | n/a | n/a |

### T23 Approach (checklist part A)

1. **The goal, in the world.** The record says, with figures and the concurrency they were taken under, what the lane did with its first real batches, what it cost the coordinator, and D1, D9 and D11's answers, so phase 3's follow-ups and T31 start from measured figures.
2. **The constraints.** US3, US4, SC-002, SC-003; FR-005 (one wake a landed batch); FR-010 (each figure with its concurrency); D1, D5, D9, D11; the brief's four things.
3. **Where each comes from.** O: the lane's `lane.jsonl` and `repairs.jsonl`, the event log's Phase lines, the sampler, the session's transcript, the tick commits (each script's output beside it). G: the plan's phase 2 measurement line.
4. **Do they describe the world here?** Yes, they are this clone's own logs over the window. The figures are re-derived by re-running the scripts over the snapshot (`batches.out`) or over the live files up to the window's end (the others).
5. **The order.** After T22 put phase 2 live and T24/T25 put phase 3 on main; before T31 (the like-window measurement) and phase 4 (T29, which D11 hands to).
6. **The exits.** Green: the record's figures re-derived from its outputs. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one read of each source.
8. **The budget.** One landing.
9. **Done, measured.** `python3 -I dev/measurements/2026-11-28/461-t23-lane-first-batches/t23-batches.py dev/measurements/2026-11-28/461-t23-lane-first-batches/lane.jsonl | diff - dev/measurements/2026-11-28/461-t23-lane-first-batches/batches.out` is empty, and each table of `results.md` matches its output file.
10. **Before moving a constant.** n/a: `LANE_WAIT_MAX` stays unpriced (D9, no limit found up to 27.4 min, measured 2026-11-28 (t23-wait.py)), and `LANE_MAX` and D5's one-feature rule are unmoved (T101 prices the latter).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing: no code changes; not a defect.

**Found and left?**
- The lane's `landed` line reports the minutes since the last resume (462-4: 0.1 against 12.9 run minutes, measured 2026-11-28 (t23-batches.py)), so FR-005's status line under-reports a resumed batch's time. Not fixed here: a measurement changes no source. Filed as T99; lands before T31.
- `make task-time` books none of a lane batch's gate (no line names the lane's tree; 461-3's 28.5-minute run shows as 20.9 working minutes, and the Unbooked line holds 3878 phases tied to no run), so the landings' side reads short. Not fixed here: a measurement changes no source. Filed as T100; lands before T31.
- One feature a batch (D5) splits an interleaved queue into batches of one (462-5), a throughput lever with no wrong outcome. Not fixed here: a lever to price, not a defect. Filed as T101; lands before T31.

**Performance work?** yes: a measurement of where the landing's time goes (451 FR-013: the landings, measured), no engine-speed change.

### T24 (D6 step 3 and 5, its table; US4, FR-004: phase 3's halving in place of phase 2's whole-batch ejection - the real batch 462-1, 2026-11-28, ejected all three of T550, T301 and T549 as `unplaced`)

- **Approach**: `rust/gate/crates/lane/src/halve.rs` (new, pure, over the changes' indices) answers which set a red batch runs next and what each result means; `runner/run.rs`'s `run_batch` keeps ONE loop - a `Run` (the changes left, those landed, the halving under way) whose `next_set` asks the halving (its ejections made on the way, through `file_groups`, the tripwire's check included) or else takes every change left, each set then carried, gated and pushed by the existing `carry`, `land`, `Pushed` and `PushFailed` arms. A first red the record cannot place (`Verdict::Unplaced`: no unit read, a unit naming no change, or a unit - a Phase line or a first-pass row - naming several) writes its `attribute` line (`how` `none`, every change that ran) and starts the halving; a red inside the halving is recorded, not read again. The ejection code (`integrate`, `eject`, `file_groups`, `trip`) moved to `runner/run/eject.rs`: `run.rs` reached 1,001 lines, measured 2026-11-27 (`wc -l`, the file-scale bar's check). Measured 2026-11-27: red first, `make rust-test CRATE=rust/gate/crates/lane ONLY="runner::run::tests::halving runner::run::tests::a_red_the_record_cannot_place"` on the old code: 0 passed, 4 failed (each batch ejected whole as `unplaced` after one run: `["T01 T02 T03 T04"]`); after, the crate 99 of 99 and `make builder-checks CRATE="rust/gate/crates/lane"` clean. The runs counted by the end-to-end tests (after the batch's first red run, against ceil(log2 n) + 1): n = 4, bad B: 3 ([A B] red, [A], [C D]; B `inferred`); bad D: 2; bad C: 3 (C `red`, [D]); n = 6, bad C: 4 ([A B C] red, [A], [B], [D E F]; C `inferred`); bad F: 3 - D6's table row by row. The pure test drives every single bad change of n = 1 to 8 within the bound.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **The first half is the first `len / 2`** of a set (`[A B C]` runs `[A]`, then `[B]`). Label: D6's table, literal (its 4-run row for n = 6, bad C).
2. **A second half whose first half ran green inside a red parent is red without a run** and is halved in turn; one whose first half ran red is untested and runs. Label: D6's table, literal.
3. **The rest runs as one**: untested sets standing together at the front run as one set (after a `red` ejection, the ejected change's untested sibling and the untested other half). Label: D6 step 2's "it is ejected and the rest runs again"; WHY: without it n = 4 with A bad took 4 runs and n = 6 with B bad took 5, past US4's bound, observed 2026-11-27, method: the rules traced by hand without the merge (the bound held since by `halve::tests::every_single_bad_change_of_n_1_to_8_is_found_within_the_bound`).
4. **The inferred single is ejected only once everything else has landed or been ejected** (`why` `inferred`, its repair's `attempt` the red run its inference rests on, so the tripwire's ask names that file). Two such singles (two bad changes; the plan says "the one left") are each ejected `inferred`, in hand-in order, at the end. Label: D6's "the one left after every other change landed green"; the two-singles case the easier route.
5. **A one-change batch red the record cannot place is ejected `red` with no further run**: its first run was its own. Label: data-model.md's pin rule ("ejected after its own one-change red run is `red`").
6. **The halving runs over every change that ran, not D6 step 2's candidates alone** (a red unit naming several changes is still `Unplaced`). Label: the algorithmically easier route, correct and at most a run or so slower; a lone candidate run red beside riders is no one-change run, so the narrowing needs a rider pin rule first. Not fixed here: the narrowing is a new rule needing its own pin reading. Filed as T78; lands before T27.
7. **A first-pass refusal is read as any red unit** (round 1's objection 7a and 7c). A row naming several changes (`T13, T14: ...`) is `Unplaced` and HALVED over every change that ran, as Decision 6 halves - each halved set's run takes the first pass again, so a named change refused wherever it runs is ejected `red` after its own one-change run and the innocent ones land; T15 Decision 6's one `unplaced` entry over the named changes (a phase-2 ruling, made before any halving) is retired, and the narrowing to the named changes joins T78. A row naming ONE change is placed (`red`), D6's one-candidate path. A row naming NO change of the batch (a hold, a lock, an owed round of no task of it) still stops the runner with the batch open, nothing ejected, as T15's plan review round 1 ruled: it is no change's fault, and a halving would meet the same refusal in every half and eject every change one by one, the innocent ejection that ruling refused; the next `make lane-start` resumes the batch once the hold clears. Label: D6 step 2 read literally for the first two, the T15 ruling kept for the third with its reason. Pinned by `runner::run::tests::a_first_pass_row_naming_two_changes_is_halved_each_ejected_alone_and_the_rest_lands` (T01 and T02 each refused wherever it runs: both ejected `red`, two entries, T03 landed, measured 2026-11-27 (`make builder-checks`, the crate 99 of 99)) and, unchanged, `a_first_pass_refusal_naming_no_change_ejects_nothing_and_one_naming_a_task_ejects_its_change`.
8. **`LANE_RETRY` = 0 is handed into the halving** (`Halving::new(.., retry)`): a red set runs again that many times before it is read red; tested at 1 (a flake then lands whole) and at 0 (the flake costs an innocent change's `inferred` ejection, the cost D6 step 5 accepts). Label: GUESS knob, D6 step 5.
9. **A halving's green set whose push fails** runs again once (the halving asks the same set again, its result not recorded); a second failure is the batch's `integrate` entry over that set, as T19 ruled, and the changes the halving had not yet run stay unlanded and unejected - `waiting` for the next batch (`log::state`). Label: the easier route.
10. **A runner killed mid-halving resumes what is left as one attempt** (`runner::remaining`), so the halving starts again from that red. Label: the easier route; no halving state is kept in the log.
11. **No `attribute` line inside a halving**: each set's own `run` line names its red units; the halving's ejections are their own repair entries, `units` the red run's units. Label: the easier route; data-model.md's `attribute` row ("a red is read") is the first red's.

### T24 Approach (checklist part A)

1. **The goal, in the world.** A batch whose red the gate's record cannot place lands its good changes and ejects only the bad one, within ceil(log2 n) + 1 further runs, instead of ejecting the whole batch as 462-1 did.
2. **The constraints.** D6 steps 3 to 5 and its table; US4; FR-004; FR-008 (nothing pushes ungated: every landed set was gated as it lands); T18's pin rules (a red half of two or more pins nobody); T19's push-failure path.
3. **Where each comes from.** R: plan.md D6, data-model.md, tasks.md T24's line. O: the red-first counts and the run counts above.
4. **Do they describe the world here?** The stand-in landing of the end-to-end tests is red exactly when its set holds the bad task, by a Phase line naming a crate no change touches (the record cannot place it), measured 2026-11-27 (`make rust-test`, the halving's end-to-end tests); a real batch's halving is the lane's use once it lands.
5. **The order.** After T18 and T23; before T25, T26 and T29.
6. **The exits.** Green: the lane crate's tests and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The lane crate 99 of 99, 2026-11-27 (`make builder-checks CRATE="rust/gate/crates/lane"`); the red-first counts above.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome fixed: a red the record cannot place ejected every change of the batch (462-1's three), so good changes waited on repairs they did not need. The test `a_red_the_record_cannot_place_ejects_the_whole_batch_as_one_repair_entry_and_forms_no_batch_again` pinned that phase-2 outcome and is rewritten as `a_red_the_record_cannot_place_is_halved_and_each_change_red_alone_is_ejected_after_its_own_run`.

**Found and left?**
- D6 step 2's narrowing to the candidates (Decisions 6 and 7): the halving runs over the whole set, at most a run or so more where a unit (a Phase line or a first-pass row) names several changes. Not fixed here: a new rule, its rider pin reading unwritten. Filed as T78; lands before T27.

**Performance work?** no

### T25 (phase 3: a carry conflict becomes a repair entry - the lane stopped twice on carry conflicts on 2026-11-28, batch 461-1 at 461 T71 and batch 462-1 at T549's ledger, each needing the coordinator by hand; REBUILT 2026-11-28 on T24's halving, the first build 54f0c0b43f having conflicted with T24's rewrite of run.rs)

- **Approach**: `rust/gate/crates/lane/src/runner/run.rs` and `run/eject.rs`. `carry()` now returns the changes it carried. Where one change's `make carry COMMIT=` stops with unmerged paths (`git diff --name-only --diff-filter=U` in the lane's tree), the tree is put back where that carry found it - `git cherry-pick --abort`, then `git reset -q --hard <the HEAD read before that carry>` - BEFORE any line is written, and `conflicted()` (new, in `eject.rs` beside the other ejections) files the change as ONE repair entry (kind `integrate`, `why` `conflict`, `units` the conflicting files, `ejected` its sha, `attempt` the carry's own stdout and stderr kept as `l7r-lane/attempts/<batch>-carry-<sha10>.log`), then its `eject` line (`why` `conflict`) and one `owed` line (`lane: batch <b>'s carry of <sha> stopped in conflict - <feature> <tasks> ejected as repair <r> (integrate, conflict: <files>) - make builder-next hands it to a fresh builder; the rest of the batch goes on: <file>`); the next change is carried. A change's carry that fails with NO unmerged path is ejected the same way, `why` `carry`, `units` the carry's own `carry:` and `land:` lines (Decision 4, round 2); only a carry on the lane's own tree - exit -1, or the carry's `carry: refused - nothing carried` (`CARRY_REFUSED`) - still stops the runner. The set's one `carry` line follows, code 0, its `conflict` every ejected change's files. In `run_batch` (T24's `Run` loop) the attempt's `todo` is rebound to the carried survivors, so `land`, the red's `eject`, the halving's `record` and a failed push's `integrate` never see an ejected change; where a carry ejected any, the new `Run::conflicted` drops those changes from `left` and ENDS a halving under way (Decision 8); where nothing was carried the loop goes on to the next set before `runs += 1`, so a set whose every carry conflicts runs no landing. `spec_of` (moved out of `land`, unchanged) names the entry's feature. Docs made true in the same change: run.rs's and eject.rs's module docs, `repairs.rs`'s `kind`, data-model.md's `conflict` and `carry` rows, rust/gate/CLAUDE.md's lane row. Measured 2026-11-28 (`make rust-test CRATE=rust/gate/crates/lane ONLY="runner::run::tests"`): red first, 6 of 32 failed on the old code - five by behavior (the newer-main conflict, the all-conflict batch, the same-batch conflict, the conflict inside a halving and a carry failing with no conflicting path each stopped the runner with the batch open: `step` returned `Err`), one by its error's wording only (a carry refused on the lane's own tree, now said so); after, 32 of 32. The tests moved to `run/tests/conflict.rs` (tests.rs was at 902 lines, measured 2026-11-28 (`wc -l`)), the stand-in `make carry` given a `carry-fails-<sha>` file, a `carry-refused` file and a `clash-<sha>` count (that commit's carries after that many stop in conflict) in `tests.rs`'s `CARRY_LINES`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **Kind `integrate`, `why` `conflict`, `units` the conflicting files, pinning nothing.** Label: D7's table and data-model.md's `conflict` row, a labeled departure from D7's Decision paragraph, which gives every ejected change kind `fix`: a carry's repair is a rebase onto the new `origin/main`, not a fix of the change's code, the same kind T19 gave a set whose push failed twice; `tripwire::PINS` already leaves `conflict` out, pinned by `a_change_conflicting_with_an_earlier_one_of_its_batch_is_ejected_and_the_earlier_lands` (`tripwire::pins` empty after the ejection).
2. **The tree put back to the HEAD read before the carry, not by `cherry-pick --abort` alone, and before any line.** The real `make carry` resolves some paths by rule before it stops, so `--abort` alone is not trusted; and the reset comes first so a runner killed mid-ejection leaves no conflict markers - T55's start-time reset fires only after a `carry` line with a code not 0, which this path never writes. Label: the algorithmically easier route (one reset, no new state for T55's check to read).
3. **The set's `carry` line keeps code 0, its `conflict` the ejected changes' files.** Code not 0 still means a stop with the batch open (T55's `stopped_carry`, the batch states). Label: the easier route; data-model.md's `carry` row amended to say both.
4. **A carry that stops with NO unmerged path ejects its change, `why` `carry`, unless the stop is the lane's own tree's** (round 2, the plan review's 4b: each `make carry COMMIT=` carries one named change, so a carry that ran and failed is evidence on it, and a stop re-stops every later start on it). The lane's own, kept as a stop with the batch open and nothing ejected: exit -1 (a `make` that could not start or was killed) and the carry's `carry: refused - nothing carried; <tree> holds unfinished work`, which `land/carry.rs` prints before it picks anything (read 2026-11-28, method: every `Ok(2)` and `stopped` exit of `carry()` in `rust/gate/crates/land/src/land/carry.rs` - the refusal of unfinished work the one exit made before the change is touched; the others, a commit not located, a pick that refused to start, a continue that failed and an end not verified, are taken as the change's). Label: T15's Decision 6 rule read for the carry (a stop only where no change is named); the `why` `carry` is new beside `conflict` (data-model.md amended), pins nothing (`tripwire::PINS`), and no reader keys on `why` (`builder_queue`, `lane_log`, read 2026-11-28 by `grep`). Pinned by `a_carry_of_one_change_that_fails_with_no_conflicting_path_ejects_it_and_the_other_lands` and `a_carry_refused_on_the_lane_s_own_tree_leaves_the_batch_open`.
5. **The carry's output kept as `attempts/<batch>-carry-<sha10>.log`, the entry's `attempt`.** The `eject` line carries no `attempt` (only the tripwire's hold line does; `tripwire::pins` reads it there first). A resume that conflicts on the same change again overwrites that file, where gate attempts are never overwritten: acceptable, the same carry's output. Label: GUESS, a reading aid for the fresh builder; data-model.md names `attempt` as an attempt file.
6. **A conflict with an earlier change of the same batch is ejected the same way** (the later change, the earlier landing): the owed line says `stopped in conflict`, not `with origin/main`, since the lane's tree then holds both. Label: the task line's rule read for every carry stop that names a change (Decision 4); pinned by `a_change_conflicting_with_an_earlier_one_of_its_batch_is_ejected_and_the_earlier_lands`.
7. **One `owed` line a conflict entry, the batch's end line after.** Label: T15's Decision 10 (one line a repair entry), the same wake rule.
8. **A conflict inside a halving's set ENDS the halving; the batch's rest runs as one** (new in the rebuild: T24's halving landed after the first build). The halving asked for a set that no longer runs as asked; recording the survivors' result as the set's would misread it (a green survivor would mark the sibling red by inference), and recording nothing loops for ever - `Halving::advance` answers an unrecorded `Run` unchanged, and its set's ejected change is no longer carried. So `Run::conflicted` sets `halving` to none: the survivors carried in this attempt land or go red as a plain attempt (a red unplaced starts a fresh halving over them, a placed one ejects), and the changes left run as one after. Costs at most the halving's lost knowledge, a few runs, on a rare event (a halving's subset conflicts only where `origin/main` moved mid-batch or a change was built on another of its batch). Label: the algorithmically easier route, the plan silent; the alternative priced - dropping the ejected index from the halving's sets and recording on the survivors - needs a new `Halving` API and re-proving US4's bound (`halve::tests`' every-bad-subset sweep). Pinned by `a_conflict_in_a_halving_s_set_ends_the_halving_and_the_rest_runs_as_one` (three changes, T03 red unplaced, T02's carry conflicting from its second carry: T01 pushed by the halving, T02 ejected `conflict`, T03 run alone and ejected `red`, the lane's tree clean).

### T25 Approach (checklist part A)

1. **The goal, in the world.** A hand-in whose carry conflicts with a newer `origin/main` costs the coordinator one line - a repair entry for a fresh builder - and the rest of the batch lands without him; the lane never stops on a change's carry, in conflict or not, in a plain attempt or in a halving - only on its own tree's.
2. **The constraints.** D7's table (a carry conflict: one `integrate` entry, `why` `conflict`, for a fresh builder, the batch's other changes going on), data-model.md's repair entry and `carry` row, T15's ejection order (entry before `eject`), T55's start-time reset, T19's `integrate` entry, T24's halving (D6 step 3, US4), FR-005 (one wake an event).
3. **Where each comes from.** R: plan.md D7, D6; data-model.md; tasks.md T25. O: the red and green runs above; the coordinator's two hand-resolved stops of 2026-11-28 (the brief).
4. **Do they describe the world here?** Yes: the tests run the real `run_batch` on a scratch world - a bare origin moved by another commit of the same file after the hand-in, a stand-in `make carry` that is a bare `git cherry-pick` left in conflict (or made to conflict at a chosen carry by a `clash-<sha>` count, to fail by a `carry-fails-<sha>` file, or to refuse the tree as the real one does by a `carry-refused` file), the lane's tree in the pool's registry. A real conflict in the lane is T23's to observe.
5. **The order.** After T15, T19, T55 and T24 (landed 2026-11-28; this rebuild sits on its `Run` struct); beside T77/T79 (resume and the state readers, untouched: `runner::remaining` already drops every `eject` line's change, `why` `conflict` too).
6. **The exits.** Green: the lane crate's tests and `make builder-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `runner::run::tests` 32 of 32 and the lane crate's builder checks clean, 2026-11-28.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome fixed: a carry conflict stopped the runner with the batch open, every later start re-stopping on it (T55's note), so a batch's innocent changes waited on the coordinator's hand.

**Found and left?**

- The queue offers an `integrate` entry as `no kind make builder-brief takes yet: brief its builder by hand` (`rust/guard/shared/src/builder_queue/repairs.rs`), as it does T19's push entries, so each conflict repair costs the coordinator a hand brief where D7 hands it to a fresh builder. Not fixed here: another crate and command (the queue and `make builder-brief`), the first build filed it as T85, which never reached main. Filed as T95; lands before T29.

**Performance work?** no


### T28 (451 T405, taken over: the gate's tree check voided a gate for the clone's writes it never read; option (C), plan D10)

- **Approach**: in pool tree `diagram-backlog-t269` on main's 674dae31f3. A test only: option (C) holds by construction once every
  landing is gated in the lane's tree (D11; the lane runs `make land` with the lane's tree as its working directory, `lane` `run.rs`).
  - **Where it is** (`rust/gate/crates/measure/src/preflight/tests.rs`, `the_clone_s_writes_never_void_the_lane_tree_s_gate`; the
    task line's `measure/src/measure/preflight*` is `measure/src/preflight/`): a clone with a linked worktree added `--detach`, as
    `builder-tree lane` adds the lane's; the gate's tree snapshot taken in the lane tree (`--tree-snap`, as `make done` starts) and the
    green-gate stamp's `diagram` key read there. Then the clone's writes T405 measured: `make task-add`'s plan stub appended
    (`specs/<f>/plan.md`, uncommitted), a measurement record committed (`dev/measurements/...`, the clone's HEAD moved), the fetch
    log appended (`research/source-attempts.jsonl`), and an engine file edited (`l7r/diagram/a.py`, for the stamp). The lane's
    `--tree-check` stays 0 and silent, and its stamp key unchanged. The same writes in the lane tree: `GATE NOT GREEN` naming each of
    the four paths, and the key moved - the void T405 measured where the gate runs in the tree being written, so options (A) (a moved
    path outside every stamp area unseen) and (B) (the landing committing the append-only logs first) are not built: nothing but the
    landing writes in the lane's tree (D10).
  - **Red first: the behavior already holds, so a pin and its evidence** (observed 2026-11-27, method: `make rust-test
    CRATE=rust/gate/crates/measure ONLY="preflight::tests"`): the clone's writes aimed at the gated tree instead (the phase-1 route,
    a landing gated in the clone it writes in) - 19 passed, 1 failed, this test, at its first assertion: exit 1 naming
    `dev/measurements/2026-11-27/x/results.md`, `l7r/diagram/a.py`, `research/source-attempts.jsonl` and `specs/461-x/plan.md`;
    restored, 20 passed, 0 failed.
  - Not touched: `rust/guard`'s gate-write guard (T27's, D10's fixture over two trees) and `make land`'s one route (T29).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the lane tree's gate pinned unvoided by the clone's writes | n/a - no map | n/a | none | n/a |

### T28 Approach (checklist part A)

1. **The goal, in the world.** The coordinator writes freely in its clone - a filed task, a measurement record, a fetch - while the
   lane gates a batch, and no such write costs the batch its green gate.
2. **The constraints.** FR-001, D10 (option (C) only), D11, 451 T405's priced options; constitution XIII (the tree check itself
   unchanged: a write in the gated tree still voids it).
3. **Where each comes from.** G: FR-001's request (spec.md); R: D10, 451 T405's box and T307's priced table; O: the test above.
4. **Do they describe the world here?** Yes: a linked worktree added `--detach` off the clone shares its object store and refs and
   has its own HEAD and index, as the lane's tree does.
5. **The order.** After T26 (the task line); beside T27, before T29.
6. **The exits.** Green: the measure crate's tests and `make builder-checks`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The red-first above; `make builder-checks CRATE="rust/gate/crates/claims rust/gate/crates/measure"` green: tests, lint and format clean on both, the claims crate 211 passed, 0 failed (observed 2026-11-27, method: that command, its log).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** none - a pin; the tree check and the stamp unchanged.

**Found and left?** none.

**Performance work?** no.


### T29 (plan D11 phase 4: the one route - `make land` refused outside the lane's tree, its escape recorded; FR-001, FR-003, FR-008)

- **Approach**: a new module `rust/gate/crates/land/src/land/route.rs` (D15: the land crate) asked in `land.rs`'s `main` - the dispatch arm `make land` and `make land-batch` reach through `LAND_RUN`, after its usage, NOTE and spec checks and before `Land::landing`, so a refusal writes the landing's `end` line (`refused(2)`) and nothing of the landing runs (no carry, no first pass). The rule (`route::rule`): the tree is the lane's when the pool's registry (`l7r_shared::builder_pool::read_all` of the root's common git directory) holds an entry held by `lane` whose canonical path is the root's - the same reading as `tree/src/state.rs`'s `lane_run`. Neither `L7R_LANE_BATCH` nor `L7R_LAND_ALONE` lets a landing through: both are plain exports, so either would be an unrecorded escape (pinned by a test). Elsewhere, `LAND_HERE_OK="<reason>"` is read first, held to the reason floor (`escape::enough`), and recorded either way to the guard log as `land-here` (`escaped`/`land-here-ok`, `blocked`/`LAND_HERE_OK-no-reason`); with none, the landing is refused, recorded `blocked`/`outside-the-lane`, its message naming the lane's tree (or `make builder-tree-adopt TREE=<clone>-land` where none is adopted), `make builder-done T=<task> F=<feature>`, `make lane-start` and the escape's whole command. The Makefile's `land` and `land-batch` help and `docs/guards.md` carry the rule. The callers, observed 2026-11-28, method: a `grep` for `make land`, `l7r-gate land` and `gate.sh land` over the Makefile, `scripts/`, `rust/` and `tests/hooks/`: the lane's runner runs `make land` in the lane's tree (`lane/src/runner/run.rs` step 3) - passes; `scripts/land-alone.sh` step 6 runs it in `${LAND_ALONE_TREE:-<clone>-land}`, which is the registry's lane entry (`/diagram/.clones/diagram-backlog-land`, read from `builder-pool.json` 2026-11-28) - passes, so land-alone keeps working until T30; `scripts/sync-with-main.sh` and `land-tooling.sh` run no `make land` (one message names it: T98); `tests/hooks/test-disk-floor.sh` stops at the floor before `LAND_RUN`. The lane's runner tests run a fake Makefile, untouched.

| case | before | after |
|---|---|---|
| `make land` in the clone | lands (route test: `Ok(0)`, ticked) | refused, exit 2, its `end` written, no stub called |
| in the lane's tree | lands | lands, nothing recorded |
| `LAND_HERE_OK` with a reason | - | lands as before (a dirty clone still alone), `escaped` recorded once (the inner land-alone run is in the lane's tree, so it records nothing) |
| `LAND_HERE_OK=x` | - | refused, `blocked` recorded |
| an unclean lane tree | refused by the first pass, naming each change (`writers.rs`, 451 T242) | the same |

### T29 Approach (checklist part A)

1. **The goal, in the world.** Every landing is the lane's: the coordinator's `make land` in its clone stops with the route named, and the one recorded exception is a landing by hand when the lane itself cannot land.
2. **The constraints.** FR-001 (no gate in the coordinator's tree), FR-003 (the lane runs the existing `make land` in its own worktree), FR-008 (nothing of the checks dropped: the refusal comes before them, the escape runs them all); D10, D11 (phase 4), D15; the brief's "keep land-alone working until T30".
3. **Where each comes from.** G: the GM's lane (FR-003, the spec's words); R: plan D11's phase-4 decision; O: the registry and caller reads of 2026-11-28 above.
4. **Do they describe the world here?** Yes: the lane's tree is in the registry under `lane` and is the tree land-alone uses, measured 2026-11-28 (a read of the clone's `builder-pool.json` beside `land-alone.sh`'s `WT=`); the lane's runner has landed batches there, measured 2026-11-28 (the brief's account of the 05:2xZ bootstrap).
5. **The order.** After T26 (phase 3 in use, the lane carrying landings); before T30, which retires land-alone.
6. **The exits.** Green: the land crate's tests, the route's red-first tests green and each check deleted seen red. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none - a tooling rule, no research question.
8. **The budget.** One landing.
9. **Done, measured.** `make rust-test CRATE=rust/gate/crates/land`: 235 passed; red first, the route's main test `Ok(0)` (landed outside the lane) on the old dispatch; each of the five checks (the lane match, the escape read, the reason floor, the escape's record, main's return on refusal) deleted in turn turns a route test red (1 or 2 failed each), measured 2026-11-28.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a
12. **Before any fix.** A session that runs `make land` in its clone is refused with the route instead of gating and pushing from the clone; the lane's landings are unchanged.

The task line's second refusal, "`make land` refuses an unclean tree, naming each file", read against the brief's "keep land-alone working until then": in the lane's tree (and land-alone's, both `L7R_LAND_ALONE`) an unclean tree is already refused by the first pass, naming each change (`writers.rs`, 451 T242; pinned by `writers/tests.rs`'s `the_first_pass_names_the_changes_and_an_open_handoff_naming_the_clone`). In the clone a dirty tree is land-alone's own trigger (`alone_owed`), so refusing it there now would retire land-alone a task early; the clone's unclean refusal arrives with T30's removal of `alone.rs`, when a dirty clone under `LAND_HERE_OK` meets the same writers' refusal. Label: the easier route, the brief's order kept; the coordinating session told.

**Found and left?**
- The notices that still send the coordinator to `make land` in its clone - the batch-landing order notice at `make decide` (`static_runs_hooks/order.rs`), the holding box's lines (`shared/src/speckit.rs`), `sync-with-main.sh`'s push message, `builder-brief.md`'s phase-1 step: a session that follows one is now refused. Not fixed here: guard messages in another crate, beyond this task's one job. Filed as T98; lands before T30.

**Performance work?** no

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
<!-- plan-archive: T38 to T34 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
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


<!-- plan-archive: T38 to T40 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
### T68 (the plan review bundle read "451 T274's D3 (...), D13 (...), D5 (...)" in 461 T61's section as 451's plan-level D3 and dropped D13 and D5: found by T61's blocks review, 2026-11-27)

- **Approach**: the plan review bundle's citation reader, moved out of `rust/gate/crates/plan/src/plan/bundle.rs` (1,028 lines with this work, past the file-scale bar, measured 2026-11-27 (`scripts/gates/l7r-gate.sh check file-scale .`)) into `bundle/cited.rs`, its test into `bundle/cited/tests.rs`; four changes. (a) A decision a run names after a task's possessive, `<feature> T<n>'s D<k>`, or `T<n>'s D<k>` with no number (this feature's task), is read from that task's section of that feature's plans (plan.md, then plan-done.md and its archive parts, `plans_of`), the new `in_task`, under `<!-- feature 451 T274 -->`; a task with no section, or a section without the id, is a NOT FOUND line saying which, never the feature's plan-level decision of that name. A requirement a task names stays the spec's ("444 T20's FR-043"). A clause after the run naming the run's own feature cuts nothing from it ("451 T274's D3, D13 and D5 from 451's plan-done.md"). `section.rs` no longer drops a task's possessive in a labeled section (451 T467 dropped it, there being no reader of a task's section then). (b) A run's id may carry a parenthetical gloss naming no id, `D3 (the pid file names the sampler), D13 (...)`, so the run goes on past it. (c) `DECISION` reads a heading decision, `### D7 - title` - 48 plans write decisions so, 461's every one (measured 2026-11-27, `grep -cE "^#{2,4} D[0-9]+" specs/*/plan.md`) - and a block's own decisions are read in a section's indented form too (`  - **D1. ...`, `SECTION_DECISION`), in the block and in its task's whole section in plan.md, so a section's bare D1 is its own and not the plan's, an Approach block's too. (d) A bare id found nowhere is a NOT FOUND line, where it was dropped without a word. Red first: `plan::bundle::tests::a_decision_named_with_another_feature_s_task_is_that_task_s` failed on the old code, 1 of 31 `plan::bundle::tests` (the bundle carried 451's `THEIRS PLAN THREE` and nothing for D13, D5, D7 or D9), 2026-11-27; after, 247 of 247 of the plan crate's tests pass, the one pinned header changed (`433 T01's D3b` now `<!-- feature 433 T01 -->`). On the real plan, `make decide F=461 T=T61` built a bundle carrying 451 T274's D3, D13 and D5 from 451's plan-done.md, 2026-11-27. Round 1 of the review BLOCKED on decision 2 (the unnumbered form left as it was); it is now read by decision 1's rule, pinned by `plan::bundle::cited::tests::a_task_s_run_keeps_its_clause_and_an_unnumbered_task_is_this_feature_s`, and two pins of 451 T467 moved with it (an unlabeled section's `T31's D3` and `T31's D11` now NOT FOUND for T31's section, no longer the plan's).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| n/a: gate tooling, no map drawn | - | - | none | - |

**Decisions** (each labeled):

1. **A task's decision is its section's, whatever the feature**: `461 T61's D2` is read from 461's T61 section too, not 461's plan-level D2. Label: the brief's rule ("a decision named after `<feature> T<n>'s` is that feature's plan's"), read as the task's section of it, since 451's plan-level D3 was the wrong text the review found.
2. **An unnumbered `T<n>'s D<k>` is this feature's task's**, read by decision 1's rule in a labeled and an unlabeled section alike, a NOT FOUND line where the section or the id is missing. Label: decision 1's rule; the review's round 1.
3. **A gloss holding an id ends the run**: `D3 (see D7), D5` is read as before, so an id inside a gloss is never taken as the qualified feature's. Label: design decision.

### T68 Approach (checklist part A)

1. **The goal, in the world.** A plan reviewer reads, in `spec-cited.md`, the text of every decision a section names, from the place its name points at, and a NOT FOUND line for any it cannot find.
2. **The constraints.** T68's line in tasks.md; the brief's rule for `<feature> T<n>'s`; 451 T46's and T48's "never dropped without a word"; 451 T438's and T467's labeled-section rules.
3. **Where each comes from.** O: T61's blocks review (the bundle /tmp/l7r-check/plan-461-landing-lane-blocks-T61-fd4d36b2/spec-cited.md) and T65's empty one (/tmp/l7r-check/plan-461-landing-lane-blocks-T65-88fbf292/spec-cited.md); the red test above.
4. **Do they describe the world here?** Yes: the rebuilt T61 bundle carries 451 T274's D3, D13 and D5, measured 2026-11-27 (`make decide F=461 T=T61`, its spec-cited.md read); 461's plan writes its decisions as headings, which no bundle had carried.
5. **The order.** After T61's review; before T31.
6. **The exits.** Green: `make builder-checks CRATE="rust/gate/crates/plan"` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The plan crate's 247 tests pass and `make builder-checks CRATE="rust/gate/crates/plan"` is clean, measured 2026-11-27 (that run's own lines).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reviewer judged T61's D2 against 451's plan-level D3 "A background run's end" in place of T274's "The sampler names itself", and never saw D13 or D5; T65's reviewer saw no D7.

**Found and left?**
- 461 T65's bundle was empty for three citations: plan D7 (a heading decision, fixed here), "T16's Decision 3" and data-model.md's repair entry, forms that are no FR, SC or D id; observed 2026-11-27, method: T65's blocks read against its spec-cited.md. Not fixed here: a reader of other forms and of other spec files is another mechanism. Filed as T69; lands before T31.

**Performance work?** no

<!-- plan-archive: T63 to T21 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->

### T75 (the lane's batch 462-2 stopped at 462 T278's tick: a measurement hands in with its stub section, which the landing refuses)

- **Approach**: a measurement writes its plan section and has it reviewed before it hands in, and its hand-in asks the section as a
  fix's does - one rule for every kind's landing. Chosen over the tick taking the record in place of a section, which would need the
  landing to learn a task's kind after its tree is released, waive the plan gate's and the Approach block's asks every other task
  owes, and tick a task whose decisions no review read. `rust/gate/crates/task/src/builder_brief.rs`: the measurement's STOP POINT
  orders the record, the levers filed, then the plan section (the record's figures its Approach), `make decide` and the plan review;
  its HAND IN line waits on "the record written and review CLEAR". `rust/gate/crates/land/src/land/hand_in.rs`: `section_of` returns
  `Owed` for a measurement (it was `Later`, the asks put off), the record still asked beside it, its refusal restated ("beside its
  plan section"); `Section::Later` in `rust/gate/crates/task/src/tick/refusal.rs` is set by nothing after that and is removed, its
  doc comments and the ones in `tick.rs` and `land/cheap.rs` restated; `scripts/container/builder-brief.md`'s THE FOUR KINDS and
  hand-in paragraphs say so, with the why. What a section costs: over the review ledger's 2,017 plan-review (MODE 4) rows a pass's
  median is 123 s and its 90th percentile 266 s, spent in the reviewer's context, measured 2026-11-27 (a grep of
  `dev/review-ledger.md`'s MODE 4 rows and their time column, sorted); 461 T10's measurement builder took one round, 72 s, CLEAR,
  measured 2026-11-27 (its row in `dev/review-ledger.md`). Red-first, measured 2026-11-27 (`make rust-test ONLY=` on the old code):
  the brief's block test 0 passed 1 failed (`rust/gate/crates/task`), the hand-in's two tests 0 passed 2 failed
  (`rust/gate/crates/land`: a measurement's stub section was not refused at hand-in).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the brief's text | `each_kind_s_block_opens_with_its_marker_and_stays_short` pins the new STOP POINT and HAND IN lines and the 2,000-character cap | n/a: no map | none | n/a |
| the hand-in | `a_fix_a_closing_half_a_measurement_and_an_unbriefed_tree_still_owe_the_section_at_hand_in`, `a_measurement_hands_in_its_record_beside_its_section` | n/a | none | n/a |

### T75 Approach (checklist part A)

1. **The goal, in the world.** A measurement's hand-in reaches the lane with a section its tick passes, so no batch stops at a measurement's tick and no closing half is sent to write one.
2. **The constraints.** FR-002 (the hand-in runs the landing's first pass), US2 ("A refusal a builder can answer is answered by the builder that has the context"), 461 T44 (the record asked of a measurement), the brief's 2,000-character cap.
3. **Where each comes from.** G: US2's words; R: `scripts/container/builder-brief.md` ("the landing asks all three whatever the kind"); O: 462 T278's stop (tasks.md T75's line), the ledger's figures above.
4. **Do they describe the world here?** Yes: the stop was observed on the lane's batch 462-2, and the red tests show a measurement's stub section passing the hand-in on the old code.
5. **The order.** Lands with T27 (one hand-in); a measurement briefed after it is told to write its section.
6. **The exits.** Green: the tests named above pass and `make builder-checks` over task, land and guard is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: `grep Section::Later` over `rust/` found the hand-in's one setter and the tick's tests.
8. **The budget.** One landing.
9. **Done, measured.** The tests above green; the measurement block's length stays under 2,000 characters in its test.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** What breaks today: the lane's batch stops at a measurement's tick (462 T278, 2026-11-28) and a closing half is spent on its section; after it the stub is refused at the hand-in, where the measurement's builder answers it.

**Found and left?** none

**Performance work?** no


<!-- plan-archive: T76 to T76 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
### T77 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T77 Approach (checklist part A)

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


### T79 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T79 Approach (checklist part A)

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


<!-- plan-archive: T81 to T81 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
### T82 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T82 Approach (checklist part A)

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


### T83 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T83 Approach (checklist part A)

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


<!-- plan-archive: T84 to T22 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
<!-- plan-archive: T86 to T86 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
### T90 (a build half's hand-in formed a batch and stopped the lane: 462 T321's build half 06520f6b3f formed batch 462-4 alone, its tick refused the plan section its closing half writes, the refusal named no change, and the runner stopped with every later batch behind it, 2026-11-28, `.git/l7r-lane/attempts/462-4-1.log` to `-3.log`)

- **Approach**: `rust/guard/shared/src/lane_log.rs` (the lane's computed states, 461 T63, which `lane`'s `log.rs` re-exports and `batch.rs`'s `form` and the Stop rule read) marks each hand-in `build_half` and gives such a hand-in, where it is neither landed, in an open batch, superseded nor ejected, the state `OnClosingHalf` ("waiting on its closing half") in place of `waiting`. `form` batches only `waiting` hand-ins, so a build half forms no batch and is no oldest hand-in for a later one to be cut behind; its closing half's hand-in, a later hand-in of its task, supersedes it (D14's handout half, T09: the closing half's commit holds both halves' work) and is batched as any other.
- **Decision 1 - a build half told by its brief's `kind`, read from the pool's log.** `kinds()` walks the pool's log once: a tree's `brief` line with a `kind` is kept per tree and holder (`detail`), dropped at the tree's next `take`, `make` or `adopt`; a `done` line takes the kind kept for its tree and holder. This is the reading `task`'s `builder_done::kind_of` makes for the hand-in's milder mode (461 T44). Why it and not the other two clues the brief named: the done line carries no kind (adding one would leave 462 T321's and 461 T36's build halves, already on the log, unmarked, and the lane would still batch them), and a handoff named in the commit is the builder's own words, where the brief's kind is written by `make builder-brief` and never by the builder (T44's reason). Observed 2026-11-28, method: the clone's `builder-pool.log`, lines 1010-1011 and 1086-1087 - both live build halves have a `brief` line with `"kind": "build-half"` before their done line, and 462 T321's closing half (line 1095) `closing-half`. Label: the easier route (no writer changes, no migration).
- **Decision 2 - its place in the order: last, before `waiting`.** `landed`, `in batch`, `superseded` and `ejected` are still asked first: a batch formed before T90 still carries what its `batch` line names (T53's rule), an ejected build half still waits on its repair, and a superseded one rides inside its closing half's commit. Only what would have read `waiting` reads `waiting on its closing half`. Label: the easier route.
- **Decision 3 - a new state, not a filter in `form`.** In `l7r_shared::lane_log` so `make lane` shows it by name (`lane.rs` lists every state but landed and superseded) and the Stop rule's `waiting_unasked` no longer counts it - the lane has nothing to do for it until its closing half hands in. Label: the easier route (one rule in one place, T63's reason).
- The `HandIn` struct gains one field; the five test literals (observed 2026-11-28, method: `grep -rn "HandIn {" rust`) (lane_log, lane's batch, tripwire and wake tests) name it `false`; 461 T76/T26's and T24/T25's done commits construct no `HandIn` literal and touch none of these hunks (`git show refs/l7r/done/461-T76` etc., read 2026-11-28): the new batch test sits after the `formed` helper, away from T76's append at the file's end.
- Red first (2026-11-28): `batch::tests::a_build_half_s_hand_in_waits_on_its_closing_half_and_forms_no_batch`, 461 T36's build half's shape as the pool's log wrote it, on the old code - 3 passed, 1 failed: `left: ["c736496d82221e0a6d0452b5998882dc04f42c7f"]`, `right: ["dddddddddd4444444444444444444444444444444"]` (the build half formed the batch alone, 462-4's shape). After: `ONLY="batch::tests"` 4 of 4, `ONLY="lane_log::tests"` 8 of 8 with the new `a_build_half_s_hand_in_waits_on_its_closing_half` (the kind's reading per tree, holder and hold; the state's order; the closing half superseding; the Stop rule's waiting). Not run red: the lane_log test (the variant did not exist).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the lane's hand-in state | n/a: tooling, no map | n/a | none | n/a |

### T90 Approach (checklist part A)

1. **The goal, in the world.** A build half's hand-in waits on the lane, in no batch, and holds no later batch behind it; its closing half's hand-in supersedes it and lands both halves in one batch.
2. **The constraints.** 461 D5 (the batch of `waiting` hand-ins), D14 (a later hand-in of a task supersedes; the closing half builds on the build half's commit, T09), T44 (the kind read from the brief, never from the builder), T63 (the states in one place).
3. **Where each comes from.** O: batch 462-4's attempts and the lane's log (2026-11-28); O: the pool's log lines above; R: `builder_done.rs`'s `kind_of`.
4. **Do they describe the world here?** Yes, measured 2026-11-28 (the clone's `builder-pool.log` read for 461 T36's take, brief and done lines): the red test is that build half's own shape, its sha the live one.
5. **The order.** Before T23 (the lane runs every landing); after T63.
6. **The exits.** Green: the red test green and the crates whole at `make builder-checks`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make rust-test CRATE=rust/gate/crates/lane ONLY="batch::tests"`: 4 of 4; `make lane` lists 461 T36's build half `waiting on its closing half` once landed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A build half batched alone stops the lane with every later batch behind it - a wrong outcome (constitution XIV), not a difference.

**Found and left?**
- 461 T76/T26's done commit (1a729b9a7a) predates T63: its new batch test builds `World` without `all`, so the lane crate's tests fail to compile once it is carried and the batch gate goes red. Not fixed here: the test is in T76's commit, not on HEAD, and editing it here would conflict with its carry. Filed as T93; lands before T23.

**Performance work?** no

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T93 to T63 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
### T78 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T78 Approach (checklist part A)

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

### T80 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T80 Approach (checklist part A)

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

### T87 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T87 Approach (checklist part A)

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




### T96 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T96 Approach (checklist part A)

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

### T95 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T95 Approach (checklist part A)

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

### T91 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T91 Approach (checklist part A)

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


### T94 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T94 Approach (checklist part A)

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


### T104 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T104 Approach (checklist part A)

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


### T107 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T107 Approach (checklist part A)

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


### T109 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T109 Approach (checklist part A)

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


### T110 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T110 Approach (checklist part A)

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

### T97 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T97 Approach (checklist part A)

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


### T98 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T98 Approach (checklist part A)

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

### T99 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T99 Approach (checklist part A)

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


### T100 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T100 Approach (checklist part A)

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


### T101 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T101 Approach (checklist part A)

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

