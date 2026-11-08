# 449-rust-codebase - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-11-07 -->
### T002 Approach (checklist part A)

1. **The goal, in the world.** one process answers a hook event by Claude Code's protocol, its guard list empty.
2. **The constraints.** FR-007 (one process), contracts/guard-protocol.md (every answer kind and the merge), FR-008 (each test under a tenth of a second).
3. **Where each comes from.** research R3 (the protocol measured from today's guards), plan D1-D2.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T001.
6. **The exits.** Green: every merge case tested, `--self-check` answering, coverage full. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** an event with no guard allows in under a millisecond of its own work; the merge's cases pass.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-07 -->
### T003 Approach (checklist part A)

1. **The goal, in the world.** the facts every guard reads - the guard log, the escapes, the session's clone and name, the GM's messages - read once and written as today.
2. **The constraints.** FR-002 (the same verdicts), plan D5-D6 (the shared state kept; a fact asked once a process, its count pinned
   in a test - the practice FR-006 names for the import graph and the semantic ids, applied to the guards' reads); the shell-shape
   library (`hm_shape.py`'s heredoc and quote stripping, which the escape rule rests on) ported here with `fancy-regex` (research R8).
3. **Where each comes from.** research R5 (the shared state), R7 (the design fixes).
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T002.
6. **The exits.** Green: a guard-log line written by Rust read back by `make guard-log` as the shell's is; each read counted once a process in a test. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** the library's tests green, its reads counted. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten to the port in the same commit and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-07 -->
### T004 Approach (checklist part A)

1. **The goal, in the world.** a guard's build reaches every session, a broken build never turning every guard off.
2. **The constraints.** plan D7, FR-002 (each guard's verdict as today), FR-003 (never both). FR-005's clause on the replacements' binaries is the make-only guard's, carried by T028.
3. **Where each comes from.** research R6 (main's copy runs); plan D7 (the last good binary kept); FR-002 against `m:python-dead-fails-open`: a guard whose Python cannot start fails open today - repo-safety lets a force push to main through - so the wrapper failing open only with no good binary ever built gives no verdict weaker than today's, and falls back where today nothing does.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T002. The wrapper takes no guard's place in this task: T005 puts it in the settings beside the shell guards with an empty guard list, and each guard task moves one decider in and removes that guard's shell script and settings entry in the same landing, so a guard never runs in both (FR-003).
6. **The exits.** Green: its suite: a stale build rebuilt; a failed build - one that does not compile, or one that compiles and fails `l7r-guard --self-check` (D7's test of a good build) - running the last good binary; none ever built failing open with its line. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** the wrapper's suite green.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-07 -->
### T005 Approach (checklist part A)

1. **The goal, in the world.** every session calls the dispatcher once an event, beside the guards it does not yet hold.
2. **The constraints.** FR-003 (no guard runs twice), FR-010 (measured).
3. **Where each comes from.** plan work breakdown 4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T004; landed alone with `make land-tooling`.
6. **The exits.** Green: the settings call it for every event; `make hooks-test` green; its floor timed. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** `m:hooks-bash`'s command re-run with it in place, the floor recorded.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T001-T005 - the foundation (phase 1, work breakdown 1-4)

Decisions carried: the workspace of crates by phase (Structure Decision) - a root `rust/Cargo.toml` naming `phases` and
`guard`, `rust_checks.py` running each member and skipping the workspace's own manifest, which builds nothing itself; `serde_json`
added (Complexity Tracking); AMENDED 2026-11-07 starting T003: `fancy-regex` added for the guards' patterns (research R8); the protocol and its merge (D1, D2, contracts/guard-protocol.md); the shared state kept and
the facts asked once (D5, D6); the wrapper keeping the last good binary (D7); the settings switch landed with an empty guard list,
its own cost recorded as phase 1's floor (work breakdown 4).

### T001 Approach (checklist part A)

1. **The goal, in the world.** the Rust tools build and are checked as one workspace, the guard crate beside the hamlet stages.
2. **The constraints.** FR-004 (every line and function covered), FR-005 (make the one entry point).
3. **Where each comes from.** the plan's Structure Decision; `rust_checks.py`'s crate discovery.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** First: every later task builds in it.
6. **The exits.** Green: `make rust-test`, `make static` clean over both members, each crate's summary printed. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** both crates' tests, lint, format, cover and dead clean through make.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.
<!-- plan-archive: archived 2026-11-08 -->
### T007 Approach (checklist part A)

1. **The goal, in the world.** `gate-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `gate-hooks.sh`, 2026-11-08):
   - (a) ITS LIBRARY, PORTED WITH IT: the guard asks `scripts/hooks/lib/hm_make.py` three times on every Bash call - the make targets a command invokes, the quick-and-done combination, and `classify`'s verdict - so unlike T006's rare-branch tools it cannot stay Python. `targets`, `combine` and `classify`'s verdict through `bare-pytest` (its earlier arms - an escaped guard edit, a foreign makefile, an engine entry point - decide that a command is not one) move to `rust/guard/src/shared/make.rs`, each pattern verbatim; the rest of `hm_make.py` (the pytest and wrapped-module rewrites, the guard-write arms) moves with the guards that read it, `make-only-hooks` (T028) and `guard-file-hooks` (T029).
   - (b) THE COMMAND READ AS JSON (constitution XIV): the shell read the command with a greedy `sed` to the payload's last quote, so a ` -k ` in a later field (an Agent-free Bash payload carries `description`) could arm the subset flag; the decider reads `tool_input.command`. Named in the commit and the phase's record (FR-002), and the suite gains the case: a Bash payload whose `description` carries ` -k ` arms no subset flag, a `make done` after it passes.
   - (c) `status` (`gate-hooks.sh status`, printing the subset flag by hand) is PORTED: `l7r-guard --only gate-hooks status` prints the same `subset_pending=` line on stdout, a plain-text answer the protocol passes through as it is; the shim's `status` mode reaches it, so the suite and a person call it as they did (the T007 preflight of 2026-11-08 ruled dropping it NOT LEGITIMATE).
3. **Where each comes from.** `tests/hooks/test-gate-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-gate-hooks.sh` green against `l7r-guard --only gate-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-gate-hooks.sh` passes against the Rust guard; `scripts/hooks/gate-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T008 Approach (checklist part A)

1. **The goal, in the world.** `measure-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `measure-hooks.sh`, 2026-11-08):
   - (a) WHAT IT ASKS: the sanitized command (`hm_shape.py sanitize`, the quote and heredoc stripping T003 ported) is read in-process; the last full gate (an inline Python scan of `dev/run-log/*/*.json`) is read in-process over the same records; `scripts/measure/gatecost.py done full`, asked only on the first expensive measurement of a streak for its reminder's median, stays the measure tool's (asked by path, as T006's decision (a)) until phase 3 ports it.
   - (b) THE `git commit` RESET KEPT AS THE SHELL READ IT: the shell's greedy `sed` read - from the payload's last `"command"` key to its last quote - is used only for the `git commit` reset, so a later field naming `git commit` resets the streak. The decider reads the same span of the input as serialized in its own key order (`serde_json`'s `preserve_order`), so the verdict is the shell's (FR-002); the T008 preflight of 2026-11-08 ruled reading the command alone NOT LEGITIMATE, since it makes the guard stricter and constitution XIV's exception is only for a guard that refuses correct work. T007's (b) stands: there the greedy read refused correct work.
   - (c) `status` is ported, printing the same `measurements_since_reset=N budget=B` line (T007's (c)).
3. **Where each comes from.** `tests/hooks/test-measure-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-measure-hooks.sh` green against `l7r-guard --only measure-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-measure-hooks.sh` passes against the Rust guard; `scripts/hooks/measure-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T009 Approach (checklist part A)

1. **The goal, in the world.** `no-poll-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `no-poll-hooks.sh`, 2026-11-08):
   - (a) ITS LIBRARY, PORTED WITH IT (as T007's (a)): the guard asks `scripts/hooks/lib/hm_shape.py` up to eight times on a Bash call - the sanitized command, a sleep inside a loop, the file-watching wait and its proof of life, the self-matching process pattern and its bracketing (with `own-make.sh`'s scoping of a make wait), the 90-minute ceiling, and the periodic report with its cron. Those functions move to `rust/guard/src/shared/wait.rs`, each pattern verbatim; the rest of `hm_shape.py` (`executing_backticks` and its patterns) moves with the guard that reads it.
   - (b) THE CRON'S MINUTE IN LOCAL TIME, AS THE PYTHON READ IT: the periodic-report refusal names a cron at the current minute of the local hour (`time.localtime().tm_min`); the decider asks `date +%M` for it - a process started only on that branch, a backgrounded periodic report, as T006's decision (a) asks its tools - so the minute is the local one in any zone (the T009 preflight of 2026-11-08 ruled a UTC minute NOT LEGITIMATE).
   - (c) A PROCESS PATTERN FROM THE COMMAND, MATCHED BY THE RUST DIALECT: `self_matching` compiles the `pgrep -f` pattern a command carries and asks whether it matches the command; the Python compiled it with `re`, the decider with `fancy-regex`, which reads Python's syntax (research R8). The decider skips a pattern `fancy-regex` cannot compile, as the Python skipped one `re` could not; a pattern one dialect compiles and the other does not is found only by the suite's replay (FR-002), the proof this decision rests on.
3. **Where each comes from.** `tests/hooks/test-no-poll-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-no-poll-hooks.sh` green against `l7r-guard --only no-poll-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-no-poll-hooks.sh` passes against the Rust guard; `scripts/hooks/no-poll-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T010 Approach (checklist part A)

1. **The goal, in the world.** `main-tree-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `main-tree-hooks.sh`, 2026-11-08):
   - (a) ITS LIBRARY, PORTED WITH IT (as T007's (a)): the verdict is `scripts/hooks/lib/hm_tree.py`'s `judge` - the effective directory walked through the command's own cds, variables and subshells, every write classified by where it lands, every rewrite re-judged - with its `explain` text and its log context. The whole module moves to `rust/guard/src/shared/tree.rs`, each pattern verbatim, since `gm-tree-hooks` reads it too and takes it from there in its own task.
   - (b) THE CLONE FROM THE SESSION'S FACTS: the shell asked `clone-sync-hooks.sh resolve` (a bash and a Python start) for the session's clone when a write would land in main; the decider reads T003's session facts, the same resolver ported (the claim map, the transcript's last `/rename`, the sessions json).
   - (c) THE MIRROR FROM THE WORK TREE: `git rev-parse --show-toplevel` in the hook's directory, cut at `/.clones/`, becomes the walk up to the nearest `.git` (T006's `find_root`), the same answer with no process.
   - (d) THE MESSAGES NAME THE RUST GUARD: the refusal and the rewrite's context name `scripts/hooks/main-tree-hooks.sh`, which this task deletes; they name `rust/guard/src/guards/main_tree_hooks.rs` instead, as T006's decide-first refusal did. No verdict changes.
3. **Where each comes from.** `tests/hooks/test-main-tree-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-main-tree-hooks.sh` green against `l7r-guard --only main-tree-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-main-tree-hooks.sh` passes against the Rust guard; `scripts/hooks/main-tree-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T012 Approach (checklist part A)

1. **The goal, in the world.** `event-log-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `event-log-hooks.sh`, 2026-11-08):
   - (a) THE HOOK HALF OF ITS TOOL, PORTED WITH IT: the guard is a wrapper round `scripts/measure/event_log.py hook`, a Python start on every hook event of every tool call. The hook half - the line (`line`, its verdict reading and categories), the log's path (`clone_root`, `common_git_dir`, `feature_of`, `log_path`) and the append - moves to the decider, each pattern verbatim and the line's fields and order the same, so `make feature-report` reads it as it did. The tool's other half, `from-transcript` (a command, not a hook), stays Python until phase 3 ports the measure tools.
   - (b) THE REVERSAL WIRE: on an Edit, the test whether it puts back text an earlier Edit of the file replaced (`hm_arbiter.reversal`, three lines over the log) runs in-process; recording the trigger (`hm_arbiter.trip`, the arbiter's owed record) is asked of `hm_arbiter.py` by path, only when a reversal is found (as T006's (a)), until the arbiter's own port.
   - (c) THE EVENT FROM THE PAYLOAD: the line's `ev` is the payload's `hook_event_name`, as the Python read it; `l7r-guard --only` given no event name takes it from there too, so the suite's `"$HOOK"` (called with no mode) replays unchanged.
   - (d) THE EDIT'S DIGESTS: `digest` is SHA-1's first 12 hex digits; a SHA-1 of a few lines sits beside T006's SHA-256 in `shared`, rather than a crate.
3. **Where each comes from.** `tests/hooks/test-event-log-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-event-log-hooks.sh` green against `l7r-guard --only event-log-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-event-log-hooks.sh` passes against the Rust guard; `scripts/hooks/event-log-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T013 Approach (checklist part A)

1. **The goal, in the world.** `clone-sync-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `clone-sync-hooks.sh`, 2026-11-08):
   - (a) THE TOOLS IT ASKS STAY THEIRS (as T006's (a)): git, `sync-with-main.sh sync-in`, `lib/own-make.sh`, `gates/gate_lock.py held`, `lib/clone_local_settings.py`, `lib/solo.py`, `measure/usage_log.py record` and `reviews/layout_carry.sh` are asked by path in the clone or the tree, as the shell asked them, until their own ports.
   - (b) THE SESSION'S FACTS IN-PROCESS: the guard's inline Python - each field of the input, the session's canonical clone (the transcript's last `/rename`, else the sessions json) and whether another session in the claim map is live (its sessions-json pid and `/proc/<pid>/cmdline`) - reads T003's session facts and `/proc`, the same answers with no process; the make targets of the behind-main notice are `shared::make::targets` (`hookmatch.py targets`, the same function).
   - (c) `resolve` KEPT IN THE SHELL, ITS CODE UNCHANGED, NOT A GUARD: four shell guards and `lib/guardlog.sh` call `clone-sync-hooks.sh resolve` for the session's clone, so the script stays as that one mode, its claim-map read and `canonical_clone` as they were, until T051 deletes the callers. Its guard modes, `prompt` and `pretool`, leave the settings in this task (FR-003). NOT through `l7r-guard` (tried 2026-11-08): the wrapper's no-binary path calls `guard_log`, which calls `resolve`, an unbounded recursion that exhausted the host's processes on the wrapper suite's no-binary case; and a suite that moves HOME would start a cargo build from nothing on every firing.
   - (d) THE PROMPT'S LINES ON STDOUT, AS THE SHELL PRINTED THEM: the prompt mode's lines are the decider's plain-stdout answer (`Answer::Print`), byte for byte, so the suite's prompt cases - which match the text on stdout - pass with their expectations unedited (FR-002).
3. **Where each comes from.** `tests/hooks/test-clone-sync-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-clone-sync-hooks.sh` green against `l7r-guard --only clone-sync-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-clone-sync-hooks.sh` passes against the Rust guard; the script's guard modes (`prompt`, `pretool`) and both their settings entries are gone in the commit that registers the decider, the script kept only as decision (c)'s resolve entry until T051.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T014 Approach (checklist part A)

1. **The goal, in the world.** `idle-tests-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `idle-tests-hooks.sh`, 2026-11-08):
   - (a) EVERY MODE PORTED, THE TIMER AS ITS OWN ENTRY: `stop`, `prompt`, `timer` and `stagger` all move. A hook event is the guard; the detached wait and the printed stagger are the binary's `--idle-tests timer|stagger`, the wait started as the shell started it (`setsid nohup <the binary> ...`, the log and the state file as they were), so nothing of the shell remains. The GM's disable of 2026-09-06 carries over as one constant, arming off, every other mode live.
   - (b) THE TOOLS IT ASKS STAY THEIRS (as T006's (a)): git (`rev-parse --short`, `status`), `setsid`, `nohup`, `kill`, `pgrep` and the run itself are asked by path. The lock is the `flock` tool on the lock file's descriptor, handed to it as stdin: the crate's toolchain (1.87) has no `File::try_lock`, and a lock taken this way belongs to the open file the timer holds, as the shell's fd 9 did.
   - (c) THE PYTHON AND THE SMALL TOOLS IN-PROCESS: each `field`, `state_of`, the JSON the state and the records are written as, `cksum` (the POSIX CRC, the same values, so every session keeps its stagger), `ls -t`, the clone's top found by walking up for `.git`. The JSON's keys and values are the same; its key order and indentation are not held, because each reader takes it by key.
   - (d) THE SUITE'S ENTRY AND ITS ONE READ OF THE SOURCE: `$HOOK stagger <name>` reaches `--idle-tests` through the shim. The case "the shipped default IS disabled" grepped the shell's `DEF_ARM=0`; it reads the Rust constant instead - the same property, in the file that now holds it, every other expectation unedited.
3. **Where each comes from.** `tests/hooks/test-idle-tests-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-idle-tests-hooks.sh` green against `l7r-guard --only idle-tests-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-idle-tests-hooks.sh` passes against the Rust guard; `scripts/hooks/idle-tests-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T015 Approach (checklist part A)

1. **The goal, in the world.** `agent-stall-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `agent-stall-hooks.sh`, 2026-11-08):
   - (a) EVERY MODE PORTED: `prompt` is the guard; `check`, `watch`, `pending` and `ack` are the binary's `--agent-stall`, the Python scan in-process, one read of each transcript's last line as it was.
   - (b) THE SCRIPT STAYS AS A FORWARDER UNTIL T051, A TOOL A SESSION RUNS BY HAND: this guard's own report and `engine-freeze-hooks`'s refusal both print the exact command `scripts/hooks/agent-stall-hooks.sh ack <dir> <id>`, and a session runs `watch` under a Monitor. So the path keeps working: it runs `l7r-guard.sh --agent-stall "$@"` and holds nothing else. No guard and no library calls it, so it is outside the hazard T013 found in `resolve`. Its hook mode leaves the settings in this task (FR-003).
   - (c) THE WATCH LOOP'S TEST: `watch` loops until it is killed, as it did; a count of ticks from the environment ends it for a unit test, the shell's other seams kept (`AGENT_STALE_S`, `AGENT_RECENT_S`, `AGENT_TICK_S`).
3. **Where each comes from.** `tests/hooks/test-agent-stall-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-agent-stall-hooks.sh` green against `l7r-guard --only agent-stall-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-agent-stall-hooks.sh` passes against the Rust guard; the script's logic and its settings entry are gone in the commit that registers the decider, the script kept only as decision (b)'s forwarder until T051.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T016 Approach (checklist part A)

1. **The goal, in the world.** `stall-watchdog-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `stall-watchdog-hooks.sh`, 2026-11-08):
   - (a) THE SHELL AND THE PASS BOTH MOVE: `prompt` is the guard; `run` (the loop) and `once` are the binary's `--stall-watchdog`; `lib/stall_watchdog.py`, the pass, is ported with them (`stall_watchdog_hooks/pass.rs`) because T052's census holds no `.py` under `scripts/hooks/` at the phase's close (FR-001, phase 1). Each loop pass still starts a fresh process, through the wrapper, so an update to what a stall is reaches a loop already running, as it did. The one tool still asked by path is `finished-run-hooks.sh live`, a shell guard until T017, which moves it.
   - (b) SMALL TOOLS: `kill -0` becomes the `/proc/<pid>` check the other guards read; the loop's one-instance lock is T014's `flock` on the open file, moved to `shared::tool`, and its descriptor is closed for children by default, the fix the shell needed by hand; the sleep is in-process, so no child can outlive the loop holding the lock.
   - (c) A GUARD THAT STARTS A DAEMON MUST NOT DO IT FROM THE SELF-CHECK: every build's `--self-check` runs each guard on a sample `UserPromptSubmit` under a throwaway HOME, which the shell never faced. The guard does nothing when `L7R_SELF_CHECK` is set, which `main.rs`'s sandbox sets, and the loop ends if its state directory disappears, so a loop started under a suite's moved HOME does not run for ever; the real state directory is never removed.
   - (d) THE LOOP'S TEST: a count of passes from the environment ends `run` for a unit test (as T015's (c)), `STALL_PERIOD` and `STALL_STATE_DIR` kept.
3. **Where each comes from.** `tests/hooks/test-stall-watchdog-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-stall-watchdog-hooks.sh` green against `l7r-guard --only stall-watchdog-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-stall-watchdog-hooks.sh` passes against the Rust guard; `scripts/hooks/stall-watchdog-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T017 Approach (checklist part A)

1. **The goal, in the world.** `finished-run-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `finished-run-hooks.sh`, 2026-11-08):
   - (a) EVERY MODE AND ALL ITS PYTHON PORTED: `prompt` and `stop` are the guard; `check`, `seen`, `live`, `judge` and `stale` are the binary's `--finished-run`. The inline Python (the `/proc` walks, `files_named`, the waiter census) moves in-process with its rules unchanged, every process fact read from `/proc`, never by a pattern over this hook's own command line. T016's watchdog pass now asks `live` in-process.
   - (b) THE SCRIPT STAYS AS A FORWARDER UNTIL T051: `scripts/reviews/review_prereq.py` (phase 3) runs `finished-run-hooks.sh live <clone>`, so the path keeps answering, running `l7r-guard.sh --finished-run "$@"` and holding nothing else, as T015's (b). No guard and no library calls it, so it is outside the hazard T013 found in `resolve`. Its hook modes leave the settings in this task (FR-003).
   - (c) THE TOOLS IT ASKS STAY THEIRS: `lib/writer-alive.sh` is asked by path for each waiter's file, a shell helper no-poll's message names and the loop itself runs, until T051.
   - (d) ONE SMALL RESTATEMENT: `os.access(path, X_OK)` is the file's execute bits, which no test or suite case tells apart for the session's own files; `sort -n | tail -1` over the run log is the newest by modification time, then by path.
3. **Where each comes from.** `tests/hooks/test-finished-run-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-finished-run-hooks.sh` green against `l7r-guard --only finished-run-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-finished-run-hooks.sh` passes against the Rust guard; the script's logic and its settings entries are gone in the commit that registers the decider, the script kept only as decision (b)'s forwarder until T051.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T018 Approach (checklist part A)

1. **The goal, in the world.** `engine-freeze-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `engine-freeze-hooks.sh` and `lib/hm_engine_freeze.py`, 2026-11-08):
   - (a) THE GUARD AND ITS CHEAP HALF IN RUST: the live reviews (each agent's meta file and transcript tail, the stall ack), the live rolls (`/proc`, by cwd) and the refusal's words move in-process; the library is deleted, as T052's census requires.
   - (b) THE TWO QUESTIONS WHOSE ANSWERS ARE PHASE 2 ARE ASKED, LAST: FR-001 places by name "`l7r/diagram/ci/`, the gate's scripts under `scripts/gates/` and `scripts/measure/`" in phase 2. "Is this path engine" is `l7r/diagram/ci/delta.py`'s one list, and "does this edit change only docstrings" is `scripts/gates/gate-stamp.py`'s AST identity, so both answerers are phase-2 pieces and stay Python until that phase; FR-003 keeps a piece's Python running until its replacement passes. The guard asks them as T006's decision (a) asks its phase-3 tools: "The guard itself is one process (FR-007); the tools are what it consults, as git is." The glue that loads the two (`_is_engine`, `docstring_only`) leaves `scripts/hooks/`, which FR-001 puts in phase 1, for `scripts/gates/engine_edit.py`, beside the file it calls, unchanged, and goes when phase 2 ports its answerers. It is asked only when a review or a roll is live, so an ordinary edit starts no Python (the shell started two on every engine edit). The verdict is the same: refused only when the edit is an engine edit, not a docstring alone, and something is live.
   - (c) `REVIEW_AGENTS` is read directly from `pair_hooks`, no more parsing its source.
3. **Where each comes from.** `tests/hooks/test-engine-freeze-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-engine-freeze-hooks.sh` green against `l7r-guard --only engine-freeze-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-engine-freeze-hooks.sh` passes against the Rust guard; `scripts/hooks/engine-freeze-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T019 Approach (checklist part A)

1. **The goal, in the world.** `gm-tree-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `gm-tree-hooks.sh` and `lib/hm_gm_tree.py`, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE: the decider is `offending`, on T010's `shared::tree` (`hm_tree.py`'s `classify` and `walk`, the same functions), `lib/hm_gm_tree.py` deleted; `GM_TREE_ROOT` stays the seam.
   - (b) NOTHING ELSE CHANGES: the literal `gm-assistant` pre-check, the escape on a Bash call only, and the words, as they were.
3. **Where each comes from.** `tests/hooks/test-gm-tree-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-gm-tree-hooks.sh` green against `l7r-guard --only gm-tree-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-gm-tree-hooks.sh` passes against the Rust guard; `scripts/hooks/gm-tree-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T020 Approach (checklist part A)

1. **The goal, in the world.** `batching-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `batching-hooks.sh`, 2026-11-08):
   - (a) THE WHOLE GUARD, ITS STATE FILE UNCHANGED: `pretool`, `posttool` and the hand-run `status` move; the state line keeps its format and its path, so a session running across the switch keeps its window. The tests on the raw payload text become tests on the event's own JSON text, the same substrings of the same fields.
   - (b) THE NOTICE'S LOG LINE IS WRITTEN IN-LINE: the shell wrote it in the background because `guard_log` started Python; in the crate it is one file write.
   - (c) A SUITE'S `--only` MATCHES BY EVENT ALONE: the guard's tools are those its settings entry named, `Read|Grep|Glob|Bash`, so the session's verdicts are unchanged; but a suite drove the shell directly, where no matcher applied, and this suite's Edit case reaches the guard on that footing. `--only <guard>` is the suite's entry (D4), so it now ignores the tool matcher, as running the shell by hand did; the expectations stay unedited.
3. **Where each comes from.** `tests/hooks/test-batching-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-batching-hooks.sh` green against `l7r-guard --only batching-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-batching-hooks.sh` passes against the Rust guard; `scripts/hooks/batching-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T021 Approach (checklist part A)

1. **The goal, in the world.** `no-branch-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `no-branch-hooks.sh`, 2026-11-08):
   - (a) A STRAIGHT PORT: the same literal spellings of branch creation, the `/host-l7r-repo` pass and the escape, checked in the shell's order; the refusal's words are the shell's, its closing pointer naming the Rust file as T010's decision (d) did.
3. **Where each comes from.** `tests/hooks/test-no-branch-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-no-branch-hooks.sh` green against `l7r-guard --only no-branch-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-no-branch-hooks.sh` passes against the Rust guard; `scripts/hooks/no-branch-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T022 Approach (checklist part A)

1. **The goal, in the world.** `discard-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `discard-hooks.sh`, 2026-11-08):
   - (a) A STRAIGHT PORT, ITS PARSER IN-PROCESS: the inline Python (the command split on `&&`, `||`, `;`, `|`, `shlex` with comments, each git checkout or restore's paths, the merge-resolution exception, `git status --porcelain` per path) moves unchanged, git asked by path with its 5-second limit (`ask_within`); the refusal's words are the shell's, its closing pointer naming the Rust file as T021's did.
3. **Where each comes from.** `tests/hooks/test-discard-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-discard-hooks.sh` green against `l7r-guard --only discard-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-discard-hooks.sh` passes against the Rust guard; `scripts/hooks/discard-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

