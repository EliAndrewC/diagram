# Feature 461 research: what the landing lane reuses, what the code holds today, and the baseline

Load this file when: weighing a design decision of `plan.md` (each D<n> there cites the R<n> here), or re-reading the reuse
decision FR-009 asks for.

Sources: public pages only; nothing from this repository went into a search or a URL. Each web quotation is marked with how it
was read. Two reading paths: (raw) fetched with `curl -sL` from the raw file on 2026-11-27 and the passage found by `grep -n`, so
it is the page's own text; (tool) returned by one read-only web agent through WebFetch on 2026-11-27, whose summarizing model
may have lightly normalized it, the same caveat `specs/449-rust-codebase/port-talk-orchestrator-research.md` carries.

## R1 - the reuse decision (FR-009), part by part

FR-009 asks, before any part is built, whether it can be taken from something that exists. The candidates are Gas Town's
Refinery, bors-ng, GitHub's merge queue (with Mergify, Trunk and Zuul as the same family), and Claude Code's own primitives
(background agents, the Workflow tool, worktrees, Monitor, background commands). TAKE means the code or tool is adopted, BORROW
means its rule is reimplemented in the existing Rust, and NOT means it is not used, with the reason.

### What each candidate is

- **Gas Town (Go, MIT).** README (raw, line 96): "When polecats complete work via `gt done`, the Refinery batches merge requests,
  runs verification gates, and merges to main using a Bors-style bisecting queue. Failed MRs are isolated and either fixed inline
  or re-dispatched." README (raw, lines 653-661): "3. Runs verification gates on the merged stack 4. If green: all MRs in batch
  merge to main 5. If red: bisects to isolate the failing MR, merges the good ones". `docs/design/architecture.md` (raw, lines
  208-235): "The refinery processes MRs through a batch-then-bisect merge queue (Bors-style). This is a core capability, not a
  pluggable strategy." Its phase table there marks the bisection unbuilt: "| 2: Batch-then-bisect | gt-i2vm | Bors-style batching
  with binary bisect | Blocked by Phase 1 |" and "| 3: Pre-verification | gt-lu84 | Polecats run tests before MR submission |
  Blocked by Phase 2 |", and "Gates (test command, lint, etc.) are pluggable. The batching strategy is core."
  `docs/concepts/polecat-lifecycle.md` (raw, lines 74-78): "The Refinery owns the merge queue. ... Work exists in the MQ, not in
  the polecat - If rebase fails, Refinery creates a conflict-resolution task"; and (raw, line 229) "If conflict: create task for
  available polecat". The Refinery is an agent role: the README (tool) says tmux is "Required for `gt up` and the tmux-backed roles
  (Mayor, Witnesses, Refineries, polecats)", with Beads (`bd`) and Dolt as its work store. The docs read say nothing of what
  happens to an MR that fails its tests after bisection beyond "isolated and either fixed inline or re-dispatched".
- **bors-ng (Elixir, a GitHub App).** README (tool): "**Deprecation notice**: Though I'll still merge bug fixes if they're
  provided, new features will not be accepted." On failure bors "splits the batch into two batches, and pushes those to the
  queue", and a one-PR batch "gets kicked back to the creator so they can fix it". Docs (tool): `max_batch_size` - "batches will
  never have more than `max_batch_size` pull requests in them"; `timeout_sec`.
- **GitHub's merge queue.** Docs (tool): minimum and maximum group size and a wait time that "allows smaller groups to merge if
  there are no more PRs queued within your specified time limit"; on a failed group "the merge queue automatically removes pull
  request #1 from the merge queue" and rebuilds the rest - remove and retest, not bisection; it needs pull requests and Actions'
  `merge_group` event.
- **Zuul** (tool): "A gating system should always test each change applied to the tip of the branch exactly as it is going to be
  merged." and "if one fails, then changes that were expecting it to succeed are re-tested without the failed change."
  **Mergify** (tool): `batch_size`, and `batch_max_wait_time`, default "30 seconds".
- **Claude Code's Workflow tool** (tool, https://code.claude.com/docs/en/workflows): "No direct filesystem or shell access from
  the workflow itself | Agents read, write, and run commands. The script coordinates the agents"; "No mid-run user input"; "If you
  background your session or exit Claude Code while a workflow run is in progress, the run doesn't continue on its own."
- **Background subagents and commands** (tool, sub-agents and tools-reference pages): "A background subagent's results reach
  Claude as a completion notification in a later turn."; a background command started with `run_in_background` "keeps running
  after a final response, until it exits, is stopped, or reaches its time limit" (the limit is not stated). **Monitor**: "Runs a
  command in the background and feeds each output line back to Claude"; "Every watch Claude starts has a deadline: 5 minutes by
  default, at most 30 minutes". **Worktree isolation**: "By default, the copy branches from your default branch rather than the
  parent session's `HEAD`." (observed 2026-11-27, method: the vendors' documented defaults, read by the planner)

### The decision, part by part

| part of the lane | decision | the passage that decides it |
|---|---|---|
| the carry (hand-ins onto main in order) | NOT any outside code; KEEP our own `carry.rs` (451 T300, T399, T419 merge rules) | every candidate rebases or merges with git alone; ours already merges plan.md by section and tasks.md by box, where 8 of the night's 15 hand conflicts fell (`port-talk-orchestrator-update.md`). Gas Town's "Rebase A..D as a stack on main" is the same step with fewer rules |
| the gate | NOT outside code; KEEP `make land`'s gate (FR-008) | Gas Town: "Gates (test command, lint, etc.) are pluggable" - the gate is ours in any design |
| the batch rule | BORROW from GitHub and Mergify: a maximum size and a wait, as knobs | "allows smaller groups to merge if there are no more PRs queued within your specified time limit" (GitHub, tool) |
| test what is merged | BORROW from Zuul | "test each change applied to the tip of the branch exactly as it is going to be merged" (tool) - each lane run gates exactly the set it pushes, on the main it pushes to |
| attribute-or-bisect | BORROW bors's and Gas Town's halving, after our own attribution | "splits the batch into two batches" (bors, tool); "Binary bisect → test B (midpoint)" (Gas Town, raw). TAKE is impossible: bors is a deprecated GitHub App ("new features will not be accepted"), and Gas Town's bisection is "Blocked by Phase 1" in its own table - there is no code to take |
| eject and re-dispatch | BORROW Gas Town's `assign_back` and bors's "kicked back to the creator", with our twist: the creator has ended, so a FRESH builder (451 T308, the GM) | "If conflict: create task for available polecat" (raw) - a new task for whichever worker is free, not the original |
| the lane's runner | NOT the Workflow tool; NOT a Gas Town agent role; KEEP the detached-runner pattern of `make page-session` (`rust/gate/crates/pages/src/runner.rs`) | Workflow: "No direct filesystem or shell access from the workflow itself" and "the run doesn't continue on its own" (tool) - every lane step is a shell command, so each would be an agent's turn (tokens, FR-006), and the lane would stop when the session is backgrounded. Gas Town's Refinery is a tmux-hosted Claude session: a standing integrator, which the spec rules out (US5) and current practice dropped (Cursor, A4 of the 449 note) |
| the coordinator's wake-up | TAKE Claude Code's background command: `make lane-wait` run with `run_in_background`, which wakes the session once when it exits | "A background subagent's results reach Claude as a completion notification in a later turn" and the command form's "keeps running ... until it exits" (tool). NOT Monitor as the main route: it wakes per output line and a watch dies at "at most 30 minutes" (tool). Its lifetime is unmeasured: plan phase 2 measures it (D9) |
| the lane's tree | KEEP our worktrees and the builder pool; NOT `isolation: worktree` | the tool's worktree "branches from your default branch rather than the parent session's HEAD" (tool) and is "auto-cleaned", so its build cache is cold each time; a cold tree's first checks took 14-30 minutes (`docs/process-decisions.md`, "Two code builders at once") |
| integration judgment (US5) | BORROW Gas Town's "creates a conflict-resolution task": the queue gets a repair entry a fresh builder takes | as above; plan D7 prices a headless agent the lane launches itself | (observed 2026-11-27, method: the vendors' documented limits, read by the planner)

Nothing is TAKEN whole except the platform's background command. Gas Town is the closest design and was read first, as the GM
asked; what it would give us - batch, bisect, assign back - is the rule, and its own docs say the bisection is not yet built.

## R2 - what the code does today (read 2026-11-27 in this clone at 7af15e21ab)

- **`make land`** (`rust/gate/crates/land/src/land.rs`, 873 lines): unfinished-work refusal, then `carry_done` (the done commits
  HEAD lacks, through `carry.rs`), then the land-alone choice (`alone.rs`: a dirty clone sends the landing to
  `scripts/land-alone.sh`, 585 lines, which runs it whole in `<clone>-land`, a persistent worktree with its own target directory,
  and then has the clone take the tip, step 7, a piece-by-piece merge of plan.md, tasks.md, plan-review.json and the ledger), the
  first pass (`cheap.rs`), the gate (`long_runs.rs`: the green-gate stamp names the gates owed, `make done` runs in its own process
  group, its output to the landing's stdout, no file of its own), the claims wait, the ticks and ONE `sync-with-main.sh done`.
  The Makefile recipe adds the scratch sweep, `state-sync.sh push` and `builder-tree landed` around it, so a driver should run the
  `make land` target, not the binary.
- **The first pass writes and commits.** `cheap_refusals` commits the ledger rows, the make-targets page, the claims' moved rows,
  the carries it files and the escape records (`records_on_the_way`), refuses another writer's changes in the tree
  (`writer_refusal`), asks the mark's hold, the in-progress rule, the red-gate tripwire, four gate scripts and the push's table
  (`push-checks --every`, 7.01 to 14.27 s, measured 2026-11-27 in 451 T307 part 2's section). It reads the delta as
  `origin/main...HEAD`. So it cannot run unchanged in a builder's uncommitted tree: plan D3 splits it.
- **No coverage runs in the first pass.** `long_runs.rs`'s doc: "The changed modules' coverage check that once ran beside the gate
  is gone since the Python tests were deleted". Two printed lines still claim one: the Makefile's `land` help ("the changed
  modules' coverage among them") and `gates_and_cohort`'s "(the changed modules' coverage beside it)". A wrong message, fixed in
  phase 1 (plan, Found and left).
- **`make builder-done`** (`rust/gate/crates/task/src/builder_done.rs`): refuses an unfinished operation, unmerged path, markers,
  nothing to commit, a guard file with no `GUARD=`, or the task's earlier done commit not yet carried; commits the tree whole at the
  base it was handed out at (the clone's HEAD), keeps the commit at `refs/l7r/done/<feature>-<task>`, logs a `done` line, releases
  the tree, prints the next dispatch and the `make land` to run. "Carried" is defined against the CLONE's HEAD (`uncarried`: by
  author time and subject), and `handout_waits` refuses a task's next handout until its commit is there. The crate direction is
  `land` builds on `task` (`rust/gate/CLAUDE.md`), so the task crate cannot call the first pass in process.
- **The carry in a linked worktree keeps the done ref** (451 T404), because the clone still waits for it.
- **The gate-write guard** (`rust/guard/src/guards/gate_write_hooks.rs`) already holds a write by the tree it lands in, wherever
  the session stands (451 T307 part 1, T406, T430, all ticked). FR-001's guard half is built; what remains is a fixture over the
  lane's two trees (plan D10).
- **The tree check** (`rust/gate/crates/measure/src/preflight.rs`, `tree()` and `seen_moves`) voids a gate for any tracked file
  that moved and is not one of 4 records, 5 active-feature files or a new cohort log (451 T405's line). Its option (C) - every
  landing gated in a tree of its own, the clone free to write - is what the lane is.
- **The red-gate tripwire** (`rust/gate/crates/tree/src/state.rs`, `second_red_gate`): a second FAILED `make done` in a row in one
  tree's git directory writes a `red-gate` trigger, and `make done` and the first pass's `arbiter gate-held` hold every later gate
  until the round arbiter rules. A bisection is red runs in a row by design: plan D6.
- **The queue** (`rust/guard/shared/src/builder_queue.rs`, 915 lines; `rust/gate/crates/task/src/builder_queue.rs`, 438): one file
  `specs/<feature>/queue.txt` in the clone, states computed never typed (landed, built, in flight, waiting, ready), kinds `fix`,
  `measurement`, `build-half`, `closing-half`; `make queue-add` refuses outside the clone.
- **The rust checks' Phase lines** carry `crates` and a code (`rust/gate/crates/rustc/src/rustc/phase.rs`), so a red `test`,
  `lint` or `cover-run` line in an attempt's span names its crates in the event log; a red hook suite is named in `make done`'s
  summary output only.
- **The detached runner** (`rust/gate/crates/pages/src/runner.rs`): `page-session` starts itself again as `page-session --work` in
  a session of its own; the stall watchdog knows the queue by that argv.
- **`sync-with-main.sh`**: `sync-in` is `git pull --no-rebase origin main` in the clone (a dirty clone's overlapping file stops
  it); `done` is the locked push (`flock .clones/.sync.lock`), DIRECT or GATED by the delta. (observed 2026-11-27, method: the planner's read of the code and the event log's Phase lines)

## R3 - the baseline (FR-006, FR-007, FR-010), measured before any edit

All from the night of 2026-11-27, the spec's comparison window.

- `make task-time SINCE=2026-11-27T02:00:00Z UNTIL=2026-11-27T14:29:00Z`, run 2026-11-27 in this clone at 7af15e21ab (93.4 s wall), its header, window
  tables and T512 table kept as `specs/461-landing-lane/baseline-task-time.txt`: 130 tasks landed; the tasks' side
  143.2 blocking minutes, of which the cross-blocking row 32.3; the landings' side 772.5 minutes, 569.1 blocking; working at once
  "three or more" 603.2 of the window's minutes (observed 2026-11-27, method: that run's header and its two window tables).
- Tokens booked to the 130 landed tasks in that run's T512 table: output 6,179.1k, fresh input 17.1k, cache read 1,146,882.8k,
  cache write 24,819.3k (observed 2026-11-27, method: the table's four token columns summed with `awk` over its 130 rows). Two
  limits, both stated wherever the figure is used: T512's transcripts were filled from 2026-11-27T04:30Z only (its line), so tokens
  compare over 04:30Z to 14:29Z, not the whole window; and 451 T513 measured 2,808 of 2,910 session calls booked to no task, so the
  coordinator's tokens are missing from the per-task sums. FR-006's figure is therefore a WINDOW TOTAL by actor divided by tasks
  landed (plan D12), with the coordinator's from `port-talk-orchestrator-update.md`: 0.58M output, 616M cache read over 1,007 calls.
- Concurrency (FR-010): the pool trees busy 93%, 98% and 83% of 02:00Z to 14:29Z (the spec's Why, the session's `tree-idle.py`
  run about 14:40Z); 451 T401 owns the re-measure tool. The machine's load: `make sampler-report` over the window, read by phase
  0's task (not read here).
- Token booking caveat measured: the sums above are per-task bookings, so they are a cross-check on the window totals, never the
  FR-006 figure itself.
- Integration, from the update note: 50 landing attempts, 18 landed, 19 refused before a gate, 10 gates red; 15 of 93 carries
  conflicted.
