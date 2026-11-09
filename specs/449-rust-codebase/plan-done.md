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

<!-- plan-archive: archived 2026-11-08 -->
### T023 Approach (checklist part A)

1. **The goal, in the world.** `conflict-marker-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `conflict-marker-hooks.sh` and `lib/hm_conflict.py`, 2026-11-08):
   - (a) THE GUARD'S HALF OF THE LIBRARY IN-PROCESS: `has_conflict`, `declares_exemption`, `conflicted` and `staged_by` move unchanged, git asked by path, T022's `shlex` shared; the refusal's words are the shell's.
   - (b) `lib/hm_conflict.py` STAYS WHILE ITS OTHER CALLERS DO: the push's `--tracked`, `make audit`'s `--list` and the gate's `--selftest` call it, so it goes when T051 removes each library with its last caller; until then the detector's rule is in two places, the suite's replay and the library's own self-test both holding it.
3. **Where each comes from.** `tests/hooks/test-conflict-marker-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-conflict-marker-hooks.sh` green against `l7r-guard --only conflict-marker-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-conflict-marker-hooks.sh` passes against the Rust guard; `scripts/hooks/conflict-marker-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T024 Approach (checklist part A)

1. **The goal, in the world.** `gate-write-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `gate-write-hooks.sh`, 2026-11-08):
   - (a) THE GUARD IN-PROCESS: its inline Python, and the question `lib/own-make.sh` answered (a make of this target, by program name and cwd), move in, read from `/proc` by pid; a Bash call and an edit start no process while no gate runs. The refusals' words are the shell's.
   - (b) THE TREE CHECK IS A PHASE-2 PIECE: "is this change one the gate sees" is `scripts/gates/preflight.py --tree-check`, which FR-001 places in phase 2 by name ("the gate's scripts under `scripts/gates/`"), and FR-003 keeps it running until its replacement passes. The guard asks it by path, as T018's ruled decision (b) asks its answerers, only while a gate is running; it is the gate's own definition, so a second copy would be two answers to the one question.
3. **Where each comes from.** `tests/hooks/test-gate-write-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-gate-write-hooks.sh` green against `l7r-guard --only gate-write-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-gate-write-hooks.sh` passes against the Rust guard; `scripts/hooks/gate-write-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T025 Approach (checklist part A)

1. **The goal, in the world.** `feature-approval-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `feature-approval-hooks.sh` and `lib/hm_approval.py`, 2026-11-08):
   - (a) THE STAGING CHECK IN-PROCESS: `problem`, `is_new`, `standing`, the approval line and the refusal's words move, on T003's `gm_messages` and T023's `staged_by`, git asked by path.
   - (b) THE PUSH'S CHECK IN-PROCESS TOO: `make speckit-todo`'s reading of a feature at a revision - its status line, its boxes and open GM rows - is read through git and judged in Rust, the same states and the same added-approval rule, so the guard's verdict on a push starts no Python and `lib/hm_approval.py` gains no mode. (`holding` reads the clone's active task, which a past revision's copy never had, so it is empty here, as it was.)
   - (c) THE LIBRARY STAYS FOR ITS OTHER IMPORTERS: `spec-lint.py`, `review_owed.py` and `hm_budget.py` import `lib/hm_approval.py` (`git grep hm_approval`, 2026-11-08), so it goes with its last caller at T051 ("removed with its last caller"); this guard no longer calls it.
   - (d) ONE SUITE CASE'S MEANS, ITS PROPERTY KEPT: case 5 proved the refusal comes from the decider by `sed`-stripping the shell's call and watching the same command pass. With no shell text to strip, the same call goes through another guard's `--only` entry, whose decider this is not, and must pass; the expected verdict is unchanged, as T014's (d) kept its case's property on the Rust constant.
3. **Where each comes from.** `tests/hooks/test-feature-approval-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-feature-approval-hooks.sh` green against `l7r-guard --only feature-approval-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-feature-approval-hooks.sh` passes against the Rust guard; `scripts/hooks/feature-approval-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T026 Approach (checklist part A)

1. **The goal, in the world.** `budget-change-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `budget-change-hooks.sh` and `lib/hm_budget.py`, 2026-11-08):
   - (a) A STRAIGHT PORT: the shell and `lib/hm_budget.py` move, on T003's `gm_messages` and `targets` and T025's `problem`, the words the shell's; `hm_budget.py` is deleted with this guard, its only caller, and `lib/hm_budget_rounds.py`, a different file, stays with `hm_checks.py`.
3. **Where each comes from.** `tests/hooks/test-budget-change-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-budget-change-hooks.sh` green against `l7r-guard --only budget-change-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-budget-change-hooks.sh` passes against the Rust guard; `scripts/hooks/budget-change-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T027 Approach (checklist part A)

1. **The goal, in the world.** `ledger-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `ledger-hooks.sh`, 2026-11-08):
   - (a) THE GUARD'S READING OF THE COMMAND IN-PROCESS: finding the commit and its tree, the row a `make append` will write, what the commit stages, the words of the refusal, and the notice all move, on T022's `shlex`.
   - (b) THE RULES OF A ROW STAY IN THEIR OWN PHASE: FR-001's phase-1 clause, as amended by the round arbiter's ruling on `ask:449-phase1-tools-by-path` (2026-11-08), reads "a Python file elsewhere with callers of its own - the gate, the push, a make target - stays in its own phase, and a guard may run it by path until then, on a rare branch". `ledger_lint.py`, `ledger_owed.py` and `review_cost.py` are under `scripts/reviews/`, not `scripts/hooks/`, and have callers of their own (the gate's static phase, the push, `make ledger-owed`, `make review-cost`), so they are phase 3's. The guard asks them by path only on a command holding a `git commit`, never on the plain Bash or Edit path SC-001 measures.
   - (c) FR-008 HOLDS WITHOUT PYTHON: the decider's unit tests reach the `git commit` branch with those tools' paths stubbed by `sh` scripts; the real tools run only in the suite replay.
3. **Where each comes from.** `tests/hooks/test-ledger-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-ledger-hooks.sh` green against `l7r-guard --only ledger-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-ledger-hooks.sh` passes against the Rust guard; `scripts/hooks/ledger-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T030 Approach (checklist part A)

1. **The goal, in the world.** `archive-first-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `archive-first-hooks.sh` and `lib/hm_archive_first.py`, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE: `held`, `seen_before`, the state files' format and the refusal's words, `lib/hm_archive_first.py` deleted with its only caller.
   - (b) THE ARCHIVE'S URL RULE IN-PROCESS: `sources._cited` is six lines, the guard's own small read (as T025's decision (b)), and moves in, its `html.unescape` the entity forms a cited URL carries. The manifest rule stays one rule, `tests/tooling`'s test holding `archive.py:clean` and `sources._cited` together; the suite's replay holds this copy to the same ids on its fixture archive.
   - (c) ONE SUITE CASE'S MEANS, ITS PROPERTY KEPT: case 3 proved the refusal comes from the decider by `sed`-stripping the shell; as T025's (d), the same call goes through another guard's `--only` entry and must pass, its expected verdict unchanged.
3. **Where each comes from.** `tests/hooks/test-archive-first-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-archive-first-hooks.sh` green against `l7r-guard --only archive-first-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-archive-first-hooks.sh` passes against the Rust guard; `scripts/hooks/archive-first-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T031 Approach (checklist part A)

1. **The goal, in the world.** `claims-file-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `claims-file-hooks.sh`, 2026-11-08):
   - (a) A STRAIGHT PORT: the shell and its inline Python move, every pattern verbatim, the refusal's words the shell's, its closing pointer naming the Rust file where it had one, as T021's did.
   - (b) ONE SUITE CASE'S MEANS, ITS PROPERTY KEPT: the case that proved the refusal comes from the decider by `sed`-stripping the shell goes through another guard's `--only` entry, as T025's (d) and T030's (c), its expected verdict unchanged.
3. **Where each comes from.** `tests/hooks/test-claims-file-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-claims-file-hooks.sh` green against `l7r-guard --only claims-file-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-claims-file-hooks.sh` passes against the Rust guard; `scripts/hooks/claims-file-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T032 Approach (checklist part A)

1. **The goal, in the world.** `readme-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `readme-hooks.sh`, 2026-11-08):
   - (a) A STRAIGHT PORT: the shell and its inline Python move, every pattern verbatim, the refusal's words the shell's, its closing pointer naming the Rust file where it had one, as T021's did.
3. **Where each comes from.** `tests/hooks/test-readme-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-readme-hooks.sh` green against `l7r-guard --only readme-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-readme-hooks.sh` passes against the Rust guard; `scripts/hooks/readme-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T033 Approach (checklist part A)

1. **The goal, in the world.** `download-copy-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `download-copy-hooks.sh`, 2026-11-08):
   - (a) A STRAIGHT PORT: the shell and its inline Python move, every pattern verbatim, the refusal's words the shell's, its closing pointer naming the Rust file where it had one, as T021's did.
3. **Where each comes from.** `tests/hooks/test-download-copy-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-download-copy-hooks.sh` green against `l7r-guard --only download-copy-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-download-copy-hooks.sh` passes against the Rust guard; `scripts/hooks/download-copy-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T046 Approach (checklist part A)

1. **The goal, in the world.** `phase-source-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `phase-source-hooks.sh` and `lib/hm_phase_source.py`, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE: every rule of `decide` and the refusal's words, git asked by path only while a `phase-sources.json` exists, so an ordinary Read or Bash call starts no process; `compgen -G` becomes a small in-process expansion of the same two patterns. The library is removed where its only other readers allow (`git grep hm_phase_source`), else with its last caller at T051.
3. **Where each comes from.** `tests/hooks/test-phase-source-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-phase-source-hooks.sh` green against `l7r-guard --only phase-source-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-phase-source-hooks.sh` passes against the Rust guard; `scripts/hooks/phase-source-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T047 Approach (checklist part A)

1. **The goal, in the world.** `new-file-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `new-file-hooks.sh` and `lib/hm_new_file.py`, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE, IN-PROCESS: every rule of `verdict`, `assigned`, `resolved` and `_top`, and the refusal's words. `lib/hm_new_file.py`'s only caller is the guard, so it is removed with the shell.
   - (b) NO TOOL IS ASKED BY PATH. `reserve-prefix.py` has callers of its own (the `make reserve` target, `apply_edits.py`, `downloads.py`, `uncited.py`) and stays for its phase, but what the guard took from it is small and is really the guard's own logic under the arbiter's line: the ledger read (`reserved`), `mirror_of`, and how deep each kind's directory sits. Those move in-process; the suite still reserves through the real `reserve-prefix.py`, so a change to the ledger's form or the directories fails the replay.
   - (c) A ledger row's prefix is read as the integer `reserve-prefix.py` writes; the Python's `int()` would also have taken a numeric string, a form nothing writes. A row of another form holds nothing, where the Python crashed and passed the call.
3. **Where each comes from.** `tests/hooks/test-new-file-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-new-file-hooks.sh` green against `l7r-guard --only new-file-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-new-file-hooks.sh` passes against the Rust guard; `scripts/hooks/new-file-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T039 Approach (checklist part A)

1. **The goal, in the world.** `blocked-fetch-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `blocked-fetch-hooks.sh`, `lib/hm_fetch.py`, `scripts/record/attempts.py` and `l7r/diagram/interactive/record/blocked.py`, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE: what is a fetch, which URLs it names, the heredoc rule, `clone_of`, `archived`, the block verdict and the refusal's words are Rust. `lib/hm_fetch.py`'s only caller is the guard, so it is removed with the shell.
   - (b) THE BLOCK VERDICT IS READ IN-PROCESS. `record/blocked.py` has callers of its own and stays for its phase; what the guard takes from it - load `research/blocked-domains.json` from the guard's own tree, a host, domain-or-subdomain - is small and is the guard's own logic under the arbiter's line. A list that cannot be trusted (an entry with no approval, malformed JSON) made the Python raise and the call pass, and still passes; the suite runs against the real list.
   - (c) THE ATTEMPTS LOG IS ASKED BY PATH, ONCE A FETCH. `attempts.py` has its own callers (`make source-outcome`, the record's routes) and its report pulls in the filter's verdict and the URL's normal form, so it stays in phase 3 and the guard runs it by path under FR-001's clause. It is a rare branch: reached only once a call IS a fetch, not blocked, in a clone, naming a URL - never on a plain Bash call or a plain Edit. A new subcommand, `seen`, does each URL's report and write in one process, where the two existing subcommands would have taken one each per URL. The ask is bounded (CONVENTION, labeled at the constant, under the 15 s the settings entry gave the shell); a failed ask gives no context and passes, as the Python's crash did. T052's record lists it.
   - (d) ENTITIES IN A URL: `archived` is keyed on the URL after `html.unescape`, every named and numeric entity. The decoding comes back from the same `attempts.py seen` ask as the report (a `plain` beside each URL's `lines`), so no entity is dropped and no process is added; it moves into Rust with `attempts.py`, in phase 3 (round 1's NOT LEGITIMATE on a six-entity table; T052's record lists it with the ask).
   - (e) THE SHELL'S LITERAL PRE-FILTER GOES. It existed to keep Python off commands that cannot be a fetch; the two patterns run in-process on every Bash call, so a command that merely contains `archive` or `reserve` no longer starts anything.
3. **Where each comes from.** `tests/hooks/test-blocked-fetch-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-blocked-fetch-hooks.sh` green against `l7r-guard --only blocked-fetch-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-blocked-fetch-hooks.sh` passes against the Rust guard; `scripts/hooks/blocked-fetch-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T049 Approach (checklist part A)

1. **The goal, in the world.** `set-down-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `set-down-hooks.sh`, `lib/hm_setdown.py` and `test-set-down-hooks.sh`, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE: the verdict, the launch, notification and stop patterns, the refusal's words and the fail-open on a read error are Rust. `lib/hm_setdown.py`'s only caller is the guard, so it is removed with the shell.
   - (b) ONE TOOL STAYS BY PATH, ASKED LAST: `speckit-todo.py --closed-by-status` has its own callers (the push, the make targets) and stays for its phase, run by path under FR-001's clause. The rare branch is rarer than the Python's: a Stop event, open boxes, nothing running, no set-down, so only a turn about to be refused starts it. Every outcome before it lets the turn end or refuses identically, so moving it last changes no verdict. T052's record lists it.
   - (c) THE ROOT: the shell's `clone-sync-hooks.sh resolve` is the session's own `clone_dir()` (T013's port of that resolve); `SET_DOWN_ROOT` and the fall-back to the work tree `cwd` stands in are kept.
   - (d) THE TRANSCRIPT IS STREAMED A LINE AT A TIME, as the Python did since 2026-10-26, and never through the session's whole-file read, which would bring back the memory growth that fix removed.
3. **Where each comes from.** `tests/hooks/test-set-down-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-set-down-hooks.sh` green against `l7r-guard --only set-down-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-set-down-hooks.sh` passes against the Rust guard; `scripts/hooks/set-down-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T006-T049 - one task a guard (phase 1, work breakdown 5, 7)

Decisions carried, none new: guard by guard, the shell and its settings entry removed in the commit that registers the decider
(D3, FR-003); the suite as the verdict replay, its inline Python replaced in the same task (D4, work breakdown 7); the order, the
measured cost first (research R2); the two constitution XIV fixes on `make-only-hooks` and `guard-file-hooks` (FR-002's exception).

### T006 Approach (checklist part A)

1. **The goal, in the world.** `pair-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-007 (one guard process a tool call), FR-008 (each unit test under a tenth of a second), FR-006 (a fact computed once, and only where it is used).
   **Decisions** (found reading `pair-hooks.sh`, 2026-11-07):
   - (a) THE TOOLS IT ASKS STAY THEIRS UNTIL THEIR PHASE: on its two rare branches - a gate invocation and a review agent's dispatch - and at Stop, the guard asks eight questions that phase 3's tooling answers (`scripts/reviews/checkpoint.py due`, `scripts/gates/plan_gate.py decided`, `scripts/reviews/review_prereq.py named|check`, `scripts/reviews/review_owed.py`, `scripts/gates/gate-stamp.py --fresh`, `make engine-key`, `scripts/hooks/lib/hm_arbiter.py`'s round check, `scripts/hooks/lib/hm_dropped.py stop`). The Rust decider asks them as it does today, by path in the session's clone, until each tool's port (phase 3) answers in-process. The guard itself is one process (FR-007); the tools are what it consults, as git is. A plain Bash call, the case `m:hooks-bash` measures, reaches none of them and starts no process.
   - (b) THE ENGINE KEY ASKED ONLY WHERE IT IS READ (FR-006): today every call computes it - a `find` over `l7r/` and `pool/`, and `make engine-key` when the cached key is older - and only the two rare branches read it. The decider computes it on those branches alone; every verdict is unchanged, since no other branch reads it.
   - (c) THE GUARD'S OWN STATE IN-PROCESS: its inline Python (the pairing state, the review rounds, the dispatch record, the bypass log, `read_field`) becomes Rust over the same files and formats.
   - (d) THE SUITE'S `"$HOOK" pretool|stop` runs `l7r-guard --only pair-hooks PreToolUse|Stop` through a shim, `tests/hooks/guard-shim.sh <guard>` (shared by every guard task): the suite's cases unchanged (D4).
3. **Where each comes from.** `tests/hooks/test-pair-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-pair-hooks.sh` green against `l7r-guard --only pair-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-pair-hooks.sh` passes against the Rust guard; `scripts/hooks/pair-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T007 to T007 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T008 to T008 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T009 to T009 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T010 to T010 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T034 Approach (checklist part A)

1. **The goal, in the world.** `repo-safety-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `repo-safety-hooks.sh`, its case table in `tests/hooks/test_hooks_cases.py` and its firing-log test, 2026-11-08):
   - (a) THE GUARD MOVES WHOLE, IN-PROCESS: its inline Python, every pattern verbatim, and the three refusals' words. It has no library and asks no tool. The heredoc blanking is `shared::shape::strip_heredocs`, whose pattern is this guard's; the quoted-string blanking is the guard's own, because it writes the word ` QUOTED ` the command-position anchor consumes (feature 178).
   - (b) THE ESCAPE IS DECIDED FIRST, as in the shell: a bare `HOST_GIT_OK` is refused before any rule is read, and a reasoned one lifts only the mount rule, never the force push or the rewrite.
   - (c) THE CASE RUNNER finds a ported guard by its link: `test_hooks_cases.py` runs `tests/hooks/<guard>-hooks.sh` where that link exists, else the shell, so the table replays unchanged. `test_guard_firing_log.py`'s named list of guards that record an escape drops this one, because that test scans shell permit sites and this guard has no shell; the guarantee it held moves to `repo_safety_hooks/tests.rs`'s `an_escape_is_recorded_with_its_reason`, in the same commit, which goes red if the escaped branch writes no firing record.
3. **Where each comes from.** `tests/hooks/test-repo-safety-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-repo-safety-hooks.sh` green against `l7r-guard --only repo-safety-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-repo-safety-hooks.sh` passes against the Rust guard; `scripts/hooks/repo-safety-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T038 Approach (checklist part A)

1. **The goal, in the world.** `wakeup-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `wakeup-hooks.sh` and its suite, 2026-11-08):
   - (a) THE GUARD MOVES WHOLE, IN-PROCESS: both layers, the transcript read a line at a time behind the same literal pre-filter, the split rule (the call fails closed on an unreadable transcript, the turn end open), the refusals' words. It has no library and asks no tool.
   - (b) AN INPUT THAT IS NOT JSON IS NOTHING TO JUDGE, AS FOR EVERY OTHER GUARD (T012), BY THE ROUND ARBITER'S RULING OF 2026-11-08, `ask:449-T038-garbage`: no settings entry of its own, no list and no `--only` branch for it; the call layer runs in the one whole-binary process for a `ScheduleWakeup` call, so FR-007 holds. The suite case keeps its input and its expected verdict becomes a pass, named in the commit and in phase 1's record, citing the ruling; FR-002 names the case. Decision (a) is untouched: a real call whose transcript cannot be read still refuses.
   - (c) `tests/tooling/test_hook_deps.py` used this guard as its example of a shell guard; the example becomes `record-edit-hooks.sh`, the last to be ported (T011, after T048). `hookdeps.py` itself is T050's.
3. **Where each comes from.** `tests/hooks/test-wakeup-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-wakeup-hooks.sh` green against `l7r-guard --only wakeup-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-wakeup-hooks.sh` passes against the Rust guard; `scripts/hooks/wakeup-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T039 to T039 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T041 Approach (checklist part A)

1. **The goal, in the world.** `agent-model-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `agent-model-hooks.sh`, `lib/agent-model-rule.txt` and the suite, 2026-11-08):
   - (a) THE GUARD MOVES WHOLE, IN-PROCESS, its refusal and its three recorded permits with it. The root's `clone-sync-hooks.sh resolve` is the session's `clone_dir()` (T013's port); git is asked only when a dispatch names no model and the clone does not resolve.
   - (b) THE RULE STAYS STATED ONCE: `lib/agent-model-rule.txt` had the shell as its only reader, so it moves beside the decider (`rust/guard/src/guards/agent_model_rule.txt`) and is compiled in. The suite still holds the root `CLAUDE.md` to its two clauses.
   - (c) AN UNKNOWN MODE STAYS AN ERROR: `--only <guard> <event>` exits 1 on an event no guard of the binary takes, so the suite's case stands unchanged (round 1's NOT LEGITIMATE on restating it).
3. **Where each comes from.** `tests/hooks/test-agent-model-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-agent-model-hooks.sh` green against `l7r-guard --only agent-model-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-agent-model-hooks.sh` passes against the Rust guard; `scripts/hooks/agent-model-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T040 Approach (checklist part A)

1. **The goal, in the world.** `workflow-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `workflow-hooks.sh`, `lib/hm_workflow.py`, the suite and `tests/test_agent_models.py`, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE, IN-PROCESS: the script scan, the wave's argument checks, each unit through every `PreToolUse` hook an Agent call meets (an entry with no matcher among them), the refusals' words. `lib/hm_workflow.py`'s callers are the guard, `agent-prefix` (T042, landing together) and `tests/test_agent_models.py`, which now reads `WAVE_JOBS` from the Rust source; it is removed with the shell.
   - (b) ONE ASK STAYS BY PATH UNTIL T048: `hm_checks.drop_run`, on a refused wave alone, never a plain call. `hm_checks` is under `scripts/hooks/lib/` and T048 ports it in this same phase, when this call becomes an in-process one.
   - (c) THE HOOK'S TIME: the shell's entry named no limit of its own, and the Rust guards' one entry had 60 s (observed 2026-11-08, method: read from `.claude/settings.json`). A wave's units run inside that one entry now, and one unit through the four Agent hooks took 463 ms (`m:wave-unit-hooks`), so the entry's limit is raised to 600 s, ten times the headroom (a knob, `m:wave-unit-hooks` its basis), against a wave whose units and verify steps outrun the 60 s under load. It is a limit, not a cost: nothing waits unless a guard hangs.
   - (d) A RUN WITH NO `tool_use_id` hashes its input as the guard's JSON writes it, where the Python's sorted-key form differed. The hash is only the run's own label for its units.
3. **Where each comes from.** `tests/hooks/test-workflow-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-workflow-hooks.sh` green against `l7r-guard --only workflow-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-workflow-hooks.sh` passes against the Rust guard; `scripts/hooks/workflow-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T041 to T041 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T042 Approach (checklist part A)

1. **The goal, in the world.** `agent-prefix-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `agent-prefix-hooks.sh`, `lib/hm_agent_prefix.py` and the suite, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE, IN-PROCESS: the line-run comparison in characters as Python counted them (`splitlines`' every boundary, not only newlines), the store's form, the wave window, both escapes, every refusal's words, the headless pass. `lib/hm_agent_prefix.py`'s only caller is the guard, so it is removed with the shell. git is asked once a dispatch for the store's directory, as the shell did.
   - (b) `WAVE_JOBS` IS READ FROM `workflow_hooks.rs` (T040, landing together), where the shell started Python to ask `hm_workflow`.
3. **Where each comes from.** `tests/hooks/test-agent-prefix-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-agent-prefix-hooks.sh` green against `l7r-guard --only agent-prefix-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-agent-prefix-hooks.sh` passes against the Rust guard; `scripts/hooks/agent-prefix-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T037 Approach (checklist part A)

1. **The goal, in the world.** `source-block-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `source-block-hooks.sh`, `lib/hm_escape.py`'s `escape-reason` and the case table, 2026-11-08):
   - (a) THE GUARD MOVES WHOLE, IN-PROCESS: its inline Python, the block pattern verbatim, both containment tests against the file on disk, the refusals' words. It has no library and asks no tool; the reason's rule is `shared::escape`'s.
   - (b) THE ESCAPE IS READ FROM THE WRITTEN TEXT, as the shell's was: the token anywhere in `new_string` plus `content` takes the escape branch before the file is read, and a reason short of the floor refuses there, whether or not the file holds a block.
3. **Where each comes from.** `tests/hooks/test-source-block-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-source-block-hooks.sh` green against `l7r-guard --only source-block-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-source-block-hooks.sh` passes against the Rust guard; `scripts/hooks/source-block-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T038 to T038 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T040 to T040 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T042 to T042 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T035 Approach (checklist part A)

1. **The goal, in the world.** `shell-check-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `shell-check-hooks.sh`, `lib/hm_shell.py`, `hm_shape.executing_backticks` and the case table, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE, IN-PROCESS: the word walk, the four rules in order, the rewrite and its conditions, the refusals' words. `lib/hm_shell.py`'s only caller is the guard, so it is removed with the shell, and its `--selftest` assertions move into the guard's unit tests (the suite's first line, which ran it, goes). The corpus replay still drives the hook.
   - (b) THE PARSE STAYS `bash -O extglob -n`, A CHILD OF THE ONE GUARD PROCESS: bash is the parser being asked about, and a second parser in Rust would be a guess at its grammar, the thing the rule exists to avoid. It is not a guard's own process (FR-007) and not a Python ask; `m:shell-check-parse` is its cost.
   - (c) `executing_backticks` JOINS `shared::shape`, because `hm_make`'s recipe-comment half (T028) asks the same question; the Python copy in `hm_shape.py` stays for its other callers until T051.
   - (d) THIS GUARD RUNS LAST, SO NO GUARD READS ITS REWRITE: every other guard judges the command as written, as each shell guard did, and the rewrite reaches only Claude Code. `guards()` keeps `shell-check-hooks` the final entry and `lib.rs`'s order test pins it; a guard ported later is inserted before it.
3. **Where each comes from.** `tests/hooks/test-shell-check-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-shell-check-hooks.sh` green against `l7r-guard --only shell-check-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-shell-check-hooks.sh` passes against the Rust guard; `scripts/hooks/shell-check-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T036 Approach (checklist part A)

1. **The goal, in the world.** `house-style-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `house-style-hooks.sh`, `lib/hm_house.py`, its callers and the suite, 2026-11-08):
   - (a) THE GUARD AND ITS DECISION MOVE, IN-PROCESS: `report`, `plan`, `held_ranges`, `outside_heredocs`, the corrections, the three verdicts and every message. `write_targets` is `shared::tree::walk`, the port of the walk it asked.
   - (b) `lib/hm_house.py` STAYS UNTIL ITS OTHER CALLERS ARE PORTED OR T051: `plan_gate.py`, `apply_edits.py`, `claims_reply.py` and `hm_arbiter.py` ask its `americanize`, and `check-house-style-delta.py` and `hookbench.py` its table. The guard no longer imports it.
   - (c) THE WORD TABLE IS DATA, `rust/guard/src/guards/house_style_words.tsv`, generated from `hm_house.py`'s table: typed into a tracked source file it would be corrected on the way in, the reason that module's own comment gives. `test_house_style_delta.py`'s reading of the table holds the two equal. Both the guard's and `check-house-style-delta.py`'s exempt names gain the data file.
   - (d) THE CRASH WARNING GOES: the shell told the session when its Python decision could not run. A compiled decision has no import to fail, and a guard that does not run is the wrapper's own notice (T004).
   - (e) THE SUITE'S IMPORT-STUB CASE keeps its assertion, that the guard still acts on a command with `hm_house.py` broken, now by driving the link with the module broken in a copy of the tree. Its verdict does not change.
   - (f) THIS GUARD'S REWRITES: it runs before `shell-check` (T035 decision (d)), so `shell-check` judges the corrected text, whose words differ only in spelling or dash; shell-check's four rules read neither.
3. **Where each comes from.** `tests/hooks/test-house-style-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-house-style-hooks.sh` green against `l7r-guard --only house-style-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-house-style-hooks.sh` passes against the Rust guard; `scripts/hooks/house-style-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T037 to T037 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T044 Approach (checklist part A)

1. **The goal, in the world.** `escalation-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `escalation-hooks.sh`, `lib/hm_gm_question.py` and the suite, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE, IN-PROCESS: arming and disarming, the once-per rules, the question and offer patterns, reading the transcript from its end, the kept-question naming, every message. `lib/hm_gm_question.py`'s only caller is the guard, so it is removed with the shell.
   - (b) ONE TOOL STAYS BY PATH: `scripts/reviews/ledger_lint.py`, with callers of its own, asked for the row count when a review arms and for "every finding disposed" at a turn's end with a review armed. Both are rare branches, a review agent's dispatch or a turn it leaves armed, never a plain Bash call or Edit. T052's record lists it.
   - (c) `state`, `arm` AND `disarm` ARE A COMMAND LINE OF THE BINARY, `--escalation`, like the other guards' non-hook modes; the seams still refuse a path outside a fixture.
   - (d) `clone_of` WALKS UP FOR `.git` IN-PROCESS, the answer `git rev-parse --show-toplevel` gives, so no process starts on an Agent call or a Stop.
3. **Where each comes from.** `tests/hooks/test-escalation-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-escalation-hooks.sh` green against `l7r-guard --only escalation-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-escalation-hooks.sh` passes against the Rust guard; `scripts/hooks/escalation-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T045 Approach (checklist part A)

1. **The goal, in the world.** `review-round-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `review-round-hooks.sh`, `lib/hm_review_round.py`, its Python test and the suite, 2026-11-08):
   - (a) THE GUARD AND ITS LIBRARY BOTH MOVE, IN-PROCESS: the mode reading, the verdict reading, the snapshot, the preamble, the round and pass state, both caps and every refusal. `lib/hm_review_round.py` is removed with the shell; `tests/tooling/test_plan_round_cap.py`, the one Python test that imported it, moves: `plan_rounds` and the third-round rule to the guard's unit tests, the real arbiter round trip to a new case of the suite.
   - (b) THREE RECORD TOOLS STAY BY PATH, each on a `spec-fidelity` dispatch alone: `hm_arbiter.py` (rulings, closed and continues, and a trip with its refusal; T051's), `plan_gate.active_task` on a MODE 4 dispatch, and `stale_terms.py` on a later round. Each has callers of its own. None runs on a plain Bash call or an Edit. T052's record lists them.
   - (c) THE DIFF IS `difflib.unified_diff`, PORTED EXACTLY, not another diff tool (round 1's NOT LEGITIMATE on `diff -u`, whose edits differ): `SequenceMatcher` with its default autojunk, the opcode grouping and the headers, in `shared::difflib`. `difflib_cases.json`, 76 cases generated from CPython's own `difflib`, pins it byte for byte in a unit test.
   - (d) `state` AND THE SUITE'S `verdict-of` ARE A COMMAND LINE OF THE BINARY, `--review-round`; `verdict-of` replaces the suite's import of the deleted module, its case and verdict unchanged.
3. **Where each comes from.** `tests/hooks/test-review-round-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-review-round-hooks.sh` green against `l7r-guard --only review-round-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-review-round-hooks.sh` passes against the Rust guard; `scripts/hooks/review-round-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T046 to T046 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T047 to T047 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T028 Approach (checklist part A)

1. **The goal, in the world.** `make-only-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-005 (the guard covers the replacements' binaries as it covers the Python and cargo today), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `make-only-hooks.sh`, `lib/hm_make.py`, the suite and its callers, 2026-11-08):
   - (a) THE GUARD AND ITS DECIDING MOVE, IN-PROCESS: `classify`, `doubled_var`, the targeted-pytest and entry-point rewrites (the Makefile parsed at hook time), every refusal's words. `lib/hm_make.py` itself stays for `hookmatch.py`, `guard-file-hooks.sh` (T029) and `test_guard_corpus.py`, until T051. `test_guard_firing_log.py`'s named list of guards that record an escape drops this one, because that test scans shell permit sites; `make_only_hooks/tests.rs`'s `an_escape_is_recorded_with_its_reason`, in the same commit, goes red if the escaped branch writes no firing record.
   - (b) THE XIV FIX THE TASK NAMES: a `grep` whose pattern names `pytest` is not a pytest run. `strip_quotes` keeps a string after `-c ` (a Python program), so `grep -c "a|pytest" f` left `|pytest` at a command position, and an unquoted `\|` read as a pipe. `shared::make::pytest_view` blanks the quoted pattern of a searcher's `-c` and drops an escaped pipe; `gate`'s `bare_pytest` reads the same view. New suite cases pin both, and the expected verdict changes from refused to pass, named in the commit and in phase 1's record.
   - (c) FR-005's CLAUSE: a direct Bash run of a replacement's binary (`l7r-guard`, `hamlet`, by any path) is refused with the make target that runs it, a new verdict `bare-binary` beside `bare-cargo`; the wrapper `scripts/hooks/l7r-guard.sh` is not the binary and passes. New suite cases pin it.
   - (d) `ruff` STAYS BY PATH on a `make land-tooling` or `arbiter-fix-done` naming a `.py` file: a Python tool the landing's own lint is defined by, a rare branch. T052's record lists it.
3. **Where each comes from.** `tests/hooks/test-make-only-hooks.sh`, the guard's own suite; plan D3-D4. The constitution XIV fix named in its commit and in the phase's record (FR-002).
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-make-only-hooks.sh` green against `l7r-guard --only make-only-hooks`, with new cases for FR-005 - a direct Bash run of a replacement's binary (`l7r-guard`, `hamlet`, from the cargo target directory or by path) refused with the make target that runs it, as a bare `cargo run` is today - `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-make-only-hooks.sh` passes against the Rust guard; `scripts/hooks/make-only-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T029 Approach (checklist part A)

1. **The goal, in the world.** `guard-file-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
   **Decisions** (found reading `guard-file-hooks.sh`, `lib/hm_guard_permit.py`, the suite and the guard log of 2026-11-07, 2026-11-08):
   - (a) THE GUARD MOVES WHOLE, IN-PROCESS: the Read reminders, the recipe-comment refusal (its detector ported from `hm_make.recipe_comment_hazards`, over `shared::shape::executing_backticks`), the held-file list, the marker and permit rules, every message. git is asked only for a held file or a `/Makefile` path.
   - (b) `hm_guard_permit.py` STAYS FOR ITS `grant`, which the Makefile's `guard-edit` runs; the guard reads the permit store itself, the same file and the same hour. T051 owes the file.
   - (c) THE XIV FIX THE TASK NAMES: a scratch file whose text names a guard is not a guard write. The guard log of 2026-11-07 holds it: `cat >> $S/switch_probe.py <<'EOF'` with `(root / "scripts" / "x-hooks.sh").write_text(...)` in the body was refused, by the shell-route rule in `make_only_hooks` (T028), whose Python-write patterns read the raw command. The patterns no longer read a body only when the whole call is one storing `cat` or `tee`: nothing before it but `NAME=value` assignments of plain values whose name is one letter or lowercase, so none can be `PATH`, an `LD_*` loader variable or any other name the shell or a loader reads (round 4's finding: `PATH=<dir>` changes what `cat` runs; the logged case's `S=` is one letter), nothing on the heredoc's own line but the storing target - `cat`'s one redirect or each of `tee`'s file arguments, each a word of plain path characters and `$NAME` expansions (`$S/...` stays allowed: the logged case uses it), so no process substitution, command substitution or backquote anywhere on that line - nothing after the terminator as bash reads it (with `<<-` a tab-indented delimiter ends the body; a line equal to the delimiter inside the body ends it there, and what follows is not stored), and a QUOTED delimiter (single, double or backslash: with an unquoted one the shell runs a substitution in the body, measured 2026-11-08 by the round 3 review). Then no command in the call can run what was stored. Every other form - piped, chained on the opener, followed by anything, a body handed to an interpreter, and `> Makefile` on the stored file's own redirect - stays a guard write. New cases in `test-make-only-hooks.sh`, the suite that exercises the rule, pin both directions (the opener-line `&&`, a run through a glob, an unquoted delimiter with a substitution, and `cat > >(bash)` and `tee >(bash)` among the refused), and the expected verdict changes from refused to pass for that one form alone, named in the commit and in phase 1's record.
3. **Where each comes from.** `tests/hooks/test-guard-file-hooks.sh`, the guard's own suite; plan D3-D4. The constitution XIV fix named in its commit and in the phase's record (FR-002).
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-guard-file-hooks.sh` green against `l7r-guard --only guard-file-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-guard-file-hooks.sh` passes against the Rust guard; `scripts/hooks/guard-file-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T030 to T030 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T031 to T031 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T032 to T032 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T033 to T033 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T034 to T034 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T035 to T035 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T036 to T036 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T053 Approach (checklist part A)

1. **The goal, in the world.** No plain Bash call and no plain Edit starts Python for the guards the round arbiter moved to phase 3.
2. **The constraints.** FR-001's phase-3 clause (the ruling `ask:449-hm-checks-route`), FR-002 (every suite case of `test-record-edit-hooks.sh` keeps its verdict), FR-007 (one process on such a call).
   **Decisions** (found reading `record-edit-hooks.sh`, `lib/hm_checks.py`'s `edit` mode, `lib/hm_record.py` and `.claude/settings.json`, 2026-11-08):
   - (a) `record-edit` IS THE ONE THAT STARTS PYTHON ON A PLAIN CALL: both its settings entries, on every Edit, Write and Bash call. `check-bundle` runs on an Agent call alone, and `checks-hooks.sh after` greps its state in shell and starts Python only with a plan review's snapshot taken; both named in the ruling.
   - (a2) A SNAPSHOT OUTLIVED ITS HOLD (found reading the live state, 2026-11-08: eight entries of `plan_snaps` from reviews long returned, in a 899,438-byte state file, so `checks-hooks.sh after`'s test of the key started Python on every Bash call): a snapshot is taken before a write and popped by that call's `after`, so a call another guard refuses never pops its own. `hm_planhold.restore` now also drops every snapshot naming no hold still open, a snapshot having no use without its hold; the key goes when nothing is left, as it did. The same run of a held call also purges a hold whose dispatch never launched, past `PENDING_S`, which `refusal` already ignores, so no verdict moves; a running hold past `HOLD_MAX_S` stands, refusing until `PLAN_EDIT_OK` (the round arbiter, `ask:449-T053-round3`).
   - (b) THE TEST MOVES TO RUST, THE DECIDING STAYS: `record-edit-gate` runs `record-edit-hooks.sh`, unchanged, when the call can concern it. A Bash call can when a plan review holds text (a non-empty `plan_holds` in the state, the test `hm_checks._handle` makes: the key itself stays, empty, after every hold, so its presence says nothing; any command can rewrite held text), or it names `apply-edits`, or runs `make done` by `hm_checks`' own pattern. An Edit or Write can when its file is one `hm_checks.subject_of_path` freezes or `hm_record.page_dir_for` re-aims, or, while a plan review holds text, is a `specs/*/plan.md`: an Edit of any other file cannot change held text. Any other call starts nothing. The state is found as `hm_checks.state_path` finds it, a `.git` file (a worktree) resolved through its gitdir and `commondir`; with no repository there is no state, so no hold, as the Python's `state_path` returning None gives. The shell guard's reply becomes this binary's answers.
3. **Where each comes from.** `tests/hooks/test-record-edit-hooks.sh`, the guard's own suite; the ruling's step 1.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** Before T050-T052; the phase's close measures it.
6. **The exits.** Green: `test-record-edit-hooks.sh` green and `test-record-edit-gate.sh` green (the same cases driven through the gate, the no-repository reply beside the shell guard's, and a `python3` sentinel on the PATH that a plain call does not start and a `make done` call does), `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** A plain Bash call and a plain Edit start no Python for this guard, observed by the sentinel in `test-record-edit-gate.sh`; `m:record-edit-gate` the time beside the shell's.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T051 Approach (checklist part A)

1. **The goal, in the world.** no guard library outlives its last caller.
2. **The constraints.** FR-001, FR-003.
   **Decisions** (the round arbiter's ruling `ask:449-T051-lib-route`, route 2; found reading each library's code-level callers, 2026-11-08):
   - (a) GROUP A IS PORTED, ITS PYTHON DELETED: `hm_dropped.py` is `pair_hooks/dropped.rs` (`l7r-guard dropped drop`, the Stop check in process); `solo.py` and `clone_local_settings.py` are `clone_sync_hooks/solo.rs` and `settings.rs`, in process where they were asked by path on a prompt; `hm_guard_permit.py`'s `grant` is `l7r-guard permit grant` (`check` and `root-makefile` had only the shell guard as a caller). `hookmatch.py` is deleted: `hm_shape.py` and `hm_escape.py` name it only in their docstrings (the ruling's condition, checked), it imported them, and its one code caller, the Makefile's escape log, asks `hm_escape.py reason-ok`. `hm_make.py` is deleted with it, its one importer: `make_only_hooks` holds its logic. Nothing retained imports either.
   - (b) THE TESTS GO WITH THEM: `test_solo.py`, `test_clone_local_settings.py`, `test_guard_corpus.py`'s make-only rows (97, through `classify`, `targeted_pytest` and `wrapped`) and `test_makefile_recipe_comments.py`'s detector and repository scans are crate tests. The no-poll rows stay in `test_guard_corpus.py`, through the retained `hm_shape.py`. T050's ceiling on how many guards reach `hm_make.py` goes with that file; the ones on files that remain stand.
   - (c) NONE OF THE RETAINED FILES STARTS PYTHON ON A PLAIN CALL (the ruling's step 3, each by the branch that starts it): `guardlog.sh` from `l7r-guard.sh` is sourced only after `exec "$GOOD"`, so only when no good binary has ever been built. `usage_log.py` is asked by `clone_sync_hooks` only in the branch that has just merged main into the clone, on a prompt. `hm_house.py` is named in `rust/guard` only by the exemption pattern and a test, never started. `own-make.sh` and `writer-alive.sh` hold no Python; each is shell the guards write into a wait or, for `writer-alive.sh`, run on a Stop's live-run check. `check-bundle-hooks.sh` reaches `hm_escape.py` on an Agent call alone. `hm_approval.py`, `hm_conflict.py`, `hm_tree.py` and `hm_shape.py` have no guard caller.
   - (d) THE PHASE OF EACH, COUNTED THROUGH THE LIBRARIES THAT CALL IT (FR-001): phase 2, `hm_conflict.py` (`push_checks.py`, `push_check_times.py`, its make target) and `own-make.sh` (`one-gate.sh`); phase 3, `usage_log.py`, `hm_approval.py` (`review_owed.py`), `hm_house.py` (`apply_edits.py`, `claims_reply.py`, `hm_arbiter.py`), `hm_escape.py` (`record_owed.py`, `escape_log.py`), `hm_tree.py` (`hm_house.py`), `hm_shape.py` (`hm_tree.py`, `hm_escape.py`), `guardlog.sh` (`escape_log.py`, `check-bundle-hooks.sh`) and `writer-alive.sh` (`hm_shape.py`). T052's census reports them by phase.
3. **Where each comes from.** plan work breakdown 6.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After every guard task.
6. **The exits.** Green: `make audit` and `make guard-log` reading the Rust lines unchanged; no `.py` under `scripts/hooks/` but those FR-001 places in a later phase by name. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** no `.py` and no inline Python under `scripts/hooks/` but those FR-001 places in a later phase by name. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten to the port in the same commit and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T053 to T053 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T054 Approach (checklist part A)

1. **The goal, in the world.** SC-001: the guards before a Bash call decide it in under a tenth of the slowest guard's time at the start of the feature, on `m:hooks-bash`'s own sample; what it costs on real commands is measured and recorded beside it.
2. **The constraints.** SC-001, FR-002 (every suite case keeps its verdict), FR-007.
   **Decisions** (measured 2026-11-08, method: the guards timed in sequence on a plain `ls`, then the whole dispatch by the median of 40 spawns, `m:t054-plain-bash`):
   - (a) WHERE THE TIME WENT (observed 2026-11-08, method: each guard timed in sequence on `ls`, the median of 20 runs, one-off, the breakdown not kept in the entry): 35.8 ms a call by the whole dispatch, of which 28.3 ms inside the binary: compiling patterns the command could not match (`repo-safety` 8.9, `house-style` 2.5, `readme` 2.2, `pair` 2.2, `new-file` 1.8) and one `bash -n` (`shell-check` 3.0). `make-only` was the same on a `make` command, 10.9 ms (observed 2026-11-08, method: the same sequence on `make test-file`).
   - (b) A FAST EXIT ONLY WHERE THE RULES CANNOT FIRE, EACH SAYING WHY: `repo-safety`, every pattern names `git` and a word of its rule (`push` with a force flag, `rebase`, `--squash`, `--amend`, or the mount's path); `make-only`, its file, duplicate-variable and guard-write patterns each need what they name; `readme`, every pattern names a README, case-insensitively; `pair`'s gate test needs the word `make`; `new-file`'s targets need a redirect or `tee`; `record-edit-gate`'s `make done` pattern needs `done`, and its hold test becomes a scan, the state file being large; `house-style`, no word of its table and no forbidden dash anywhere in the input; `shell-check`, a command of plain words alone (no quote, separator, bracket, redirect or newline) that does not begin with a reserved word has nothing `bash -n` can reject and no rule can fire. Each exit comes after the guard's escape handling where one exists, so an escape token is still seen.
   - (c) NOT THE WRAPPER: it costs 5 to 6 ms (observed 2026-11-08, method: the median of 40 spawns of the wrapper against the bare binary, `--version`) and stays; the target is met without replacing the launcher that keeps a broken build from turning every guard off (plan D7).
   - (d) WHAT THE FIGURE DOES AND DOES NOT SAY (`m:t054-plain-bash`, observed 2026-11-08): `m:hooks-bash`'s sample, `ls`, is 15.4 ms, under SC-001's 17.5 (`m:t054-plain-bash`). One quoted `git` command is 19.0 ms (`m:t054-plain-bash`). Over 400 real commands sampled from this project's transcripts the median is 23.0 ms, the 90th percentile 109 ms and 7.2 percent are under 17.5 ms (`m:t054-plain-bash`); the tail is `ledger-hooks` starting `ledger_lint.py`, 200 to 260 ms (`m:t054-plain-bash`), on commit-shaped commands, a by-path ask FR-001 leaves until phase 3. Whether SC-001 is met on its own instrument or owes the rest is the round arbiter's (`ask:449-T054-sc001`).
3. **Where each comes from.** `m:hooks-bash`, `m:t054-plain-bash`.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** Before T052, whose close reads this figure.
6. **The exits.** Green: every guard's suite and the case tables unchanged, `make rust-test` and `cover` green, `m:t054-plain-bash`'s `ls` under 17.5 ms, its other figures recorded beside it, as the arbiter's ruling on `ask:449-T054-sc001` holds. Red: what failed recorded, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `m:t054-plain-bash`.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T050-T052 - the suites' tooling and the close (phase 1, work breakdown 6-8)

Decisions carried, none new: the four `tests/hooks/` Python helpers ported as `l7r-guard` subcommands and crate tests (work
breakdown 7); the unused libraries deleted with their last caller (work breakdown 6); the close on SC-001 and phase 1's share of both
censuses empty (work breakdown 8, FR-010).

<!-- plan-archive: T001 to T001 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T006 to T049 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
### T050 Approach (checklist part A)

1. **The goal, in the world.** the suites' own tooling - which suites a change makes stale, which guards a session ran, the bench, the shared cases - in Rust.
2. **The constraints.** FR-001 (phase 1's `tests/hooks/` Python), FR-008.
   **Decisions** (found reading the four files, their tests and the `hooks-test` recipe, 2026-11-08):
   - (a) A LEXER FOR THREE PYTHON FACTS, NOT A PARSER CRATE: `hookdeps.py` asked `ast` for docstring lines, imports and string constants, each decided by tokens and logical lines; `pylex` reads them, adds no crate (the plan's one crate stands), and was held to the Python's own answers before the Python went (`m:t050-deps-differential`: 57 suites, 291 Python test files, 8 traces, no mismatch). The differential's one side is deleted by this task, so it cannot be re-run; what holds the port afterward is `suite_tools`' tests over fixture trees and the real one.
   - (b) THE NAME INDEX KEEPS ITS DICT SEMANTICS: three forwarders under `scripts/hooks/` share a basename with their suite's link under `tests/hooks/`, so "every basename is unique" is no longer true; a name keeps its first place and its last path, as the dict did, which the differential found.
   - (c) A TRACE KEPT BEFORE THE PORT STANDS, AND THE ONE PYTHON PROCESS LEFT: a directory's entries are written as `json.dumps` wrote them and the blob id and three git calls are `record_cache.content_ids`'s, in Rust, so no suite re-runs for the port alone. `py` stays the interpreter's `sys.version`: a trace is a suite's reads under one interpreter, and which interpreter runs the suites is a fact only that interpreter can state, so it is one `python3` process a `fresh` or `stamp` call, never a hook's. It goes with the last Python a suite runs, at phase 3's end, when the key has nothing to say; T052's record lists it among the by-path asks, since neither census can see a spawn from the binary. Phase 4 removes the installed Python, so it must be gone by then, and a `fresh` would otherwise find no interpreter.
   - (d) `bench` TAKES ANY GUARD: FR-007 of feature 239 refused a guard with no importable decision so the cost of spawning stayed visible; every guard this binary holds now decides in process, so that refusal has nothing left to refuse among them. `check-bundle`, `checks` and `record-edit`, the three in phase 3 (FR-001), are not in the binary; `bench` refuses each by name, saying it is not in this binary and is not spawned (run, 2026-11-08: `make hookbench GUARD=checks`, and the same for the other two), so the cost of spawning stays visible for exactly the guards it can still apply to. `--against REF` builds the guard from that ref (or, before the port, runs its shell) one spawn a command, and says which: the Python's in-process baseline read `scripts/hm_house.py`, a path gone since the 2026-10-08 move, so that branch had been dead.
   - (e) THE CASE TABLES ARE CRATE TESTS, THEIR SUITES STAY: `case_tables.rs` holds the four guards' cases, generated from `test_hooks_cases.py` with each case's comment above it, and each runs through `--only <guard> PreToolUse`, the suite's own entry. `make hooks-test` requires a companion per guard, so the four suites stay, calling `tests/hooks/guard-cases.sh` (`cargo test` of the named tests). A failing replay lists every wrong case, as the Python's did.
   - (f) THE TESTS OF THE PYTHON MOVE WITH IT: `test_hook_deps.py` and `test_hookbench.py` are deleted, their rules now `suite_tools`' unit tests over fixture trees and, for the rules about this repository, the real one: transitivity, comment-and-docstring stripping, the whole-tree pair, the helper census, and each ceiling and floor on how many guards reach a helper. The one bound not carried is `test_hooks_cases.py`'s own ceiling, the file being deleted. `test_file_log.py` keeps the C recorder's own tests; its `hooktrace` and `hookdeps` cases moved.
   - (g) THE ONE MEASUREMENT COMMAND NAMING A DELETED FILE IS NOW A MAKE TARGET, RE-RUN: searched with the JSON `command` field of every `specs/*/measurements*.json` for the six file names this task deletes (the four helpers, `test_hook_deps.py` and `test_hookbench.py`; 2026-11-08), one hit, `375-a3-hooks-test-after` (a one-off script when it was measured). `make hooks-deps-window FROM=eb64e2ba3 N=10` is that analysis through make (`l7r-guard deps --window`); the entry's command names it and its value is the re-run, the 2026-10-11 figures kept beside it as what was measured then.
3. **Where each comes from.** plan work breakdown 7; `m:guard-sources` (the four helpers); `m:t050-deps-differential`.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After the guard tasks that use them.
6. **The exits.** Green: `make hooks-test` keyed by `l7r-guard deps`, its results unchanged, the keys and traces equal to the Python's first (`m:t050-deps-differential`); the four `.py` files deleted. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** no `.py` under `tests/hooks/`. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten to the port in the same commit and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T051 to T051 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T054 to T054 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-08 -->
### T052 Approach (checklist part A)

1. **The goal, in the world.** phase 1 closed on its measured outcome.
2. **The constraints.** SC-001, FR-010, FR-001 (phase 1's share of both censuses).
   **Decisions** (the round arbiter's rulings `ask:449-T054-sc001` and `ask:449-T052-inline-census`; 2026-11-08):
   - (a) SC-001 IS STATED AS MET ON ITS INSTRUMENT ALONE: `dev/phase-1-close.md` carries the ruling's wording, the real-command distribution and the commit branch, whose asks are T027's (`ledger_owed.py`, `ledger_lint.py`), a third branch beside T044's two, on a real `git commit` only (`m:t054-plain-bash`).
   - (b) THE SECOND CENSUS IS A COMMAND: `make inline-census` (`m:inline-census-sites`) lists every remaining site under one of the ruling's three groups and fails on any site outside them. The guard-input group is by exact line, so a real run in those suites still counts. `test-record-edit-gate.sh`, checked as the ruling asked, tests the phase-1 gate, so its one site was converted, and it is not among the suites that move.
   - (c) `resolve` MOVES BESIDE ITS ONLY CALLER: `scripts/hooks/lib/clone-resolve.sh`, the `clone-sync-hooks.sh` wrapper retired, as FR-009 gives the `*-hooks.sh` wrappers to Story 1.
   - (d) THE 111 CONVERTED SITES (`m:inline-census-sites`: 168 at T052's start, 57 now): `jq`, literal JSON, `sed` and `awk`, each suite still green; `BEHIND_TEST_TARGETS`' drift test moved to the crate beside its list; the two fake rolls in `test-engine-freeze-hooks.sh`, a real run of Python, are a process that looks like one (`exec -a`). `jq` joins the three install lists the suites run under: `setup-dev-env.sh`, `Dockerfile.ci` and `buildspec/run.sh`'s stock-image bootstrap, since `make done` runs them in CI as on the laptop (the custom image rebuilds with `make ci-image` when remote runs next come on). FR-009 keeps the containers in this feature only for the Python they run and install; `jq` is what removing inline Python from the suites needs where they run, so it joins those lists rather than opening a port of them.
3. **Where each comes from.** plan work breakdown 8; `m:hooks-bash`, `m:pair-hooks-suite`.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** Last.
6. **The exits.** Green: the figures re-run and recorded beside their first values, SC-001 met on its instrument (`ask:449-T054-sc001`), both censuses' phase-1 share empty but for what FR-001 names: the first by `git ls-files 'scripts/hooks/*.py' 'tests/hooks/*.py'` (`m:phase-1-python-share`: 13 files under `scripts/hooks/lib/`, each placed later by name, none under `tests/hooks/`, beside `m:python-census`'s first 872; by use, the search recorded there found one guards-only module outside them, `scripts/gates/engine_edit.py`, a wrapper over phase-2 code that goes with it, and a test of the firing log outside `tests/hooks/`, `tests/tooling/test_guard_firing_log.py`, which goes with `guardlog.sh`, in phase 3), the second by `make inline-census` (`m:inline-census-sites`). Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
   **Carried into phase 1's record:** the one suite case whose expected verdict changed, `test-wakeup-hooks.sh`'s input that is not JSON, by the round arbiter's ruling `ask:449-T038-garbage` (FR-002).
9. **Done, measured.** SC-001 met on its instrument (`ask:449-T054-sc001`): the guards before a Bash call decide it in under a tenth of today's slowest guard's time. The phase's measurements recorded in `dev/` as well as beside their first values (FR-010), and the record naming the two constitution XIV fixes (FR-002): `make-only` T028 and `guard-file` T029, each of which added new suite cases and changed no earlier case's expected verdict (their suites' `git show`, 2026-11-08), so the wakeup case stays the one changed verdict.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T060 Approach (checklist part A)

1. **The goal, in the world.** A one-line Rust edit's `make done` runs only what that edit can change (SC-002's largest share: `m:done-rust-edit`, 14 s of pytest over the 11 modules that plan selected, of 30.2 s).
2. **The constraints.** FR-001, FR-002, SC-002; Story 2 scenario 1 and 3.
   **Decisions** (measured 2026-11-08, `m:t060-done-rust-edit`):
   - (a) THE GATE GOT SLOWER AND THE FIGURE SAYS WHY: a one-line edit of `rust/phases`, on a fresh full baseline, is 60 s by wall clock against `m:done-rust-edit`'s 30.2 s, `static` 40 s against 13: phase 1's `rust/guard` is a crate as large as the hamlet stages, and the gate lints, covers and lists every crate on every edit.
   - (b) A CRATE'S UNCHANGED CHECKS REUSE THEIR LAST GREEN RESULT (the same edit afterward: 38 s, `static` 15 s, `m:t060-done-rust-edit`): `rust_checks.py` keeps, per crate and per check, an id of what that check depends on, and reuses a green result while it is the same. `lint`, `dead` and `format --check` depend on the crate, the workspace's manifests and the compiler; `cover` and `test-counters` also on the repository outside the other crates, since a crate's tests read the Makefile and fixtures under `tests/hooks/`, less the append-only records every run writes (`dev/run-log/`, `dev/bypass-log/`, `dev/perf-log/`, `dev/idle-log/`). A failure is never kept. `make done INCREMENTAL=0` and `FULL=1` run everything and keep what they find. No verdict can move: each check is a function of the inputs the id covers, a crate this one builds from by path among them (neither crate has one today).
   - (c) THE PYTHON TESTS ARE NOT NARROWED HERE: 7 of the 14 modules a Rust edit selects read real Rust source, and running only those saves about 3 s of today's 17 (observed 2026-11-08, method: `make test-file` of the 7). What that saves does not justify a hand-written roster of them; they go as the checks they test are ported.
   - (d) SC-002's FIGURE IS T070's: this task's exit is the reuse in place and the gate's time measured, recorded beside the first value. Preflight (6 s, `m:t060-done-rust-edit`'s run record) and the pytest step go with T062 to T067.
3. **Where each comes from.** `m:done-rust-edit`; the reference run's phase table.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the phase's plan above; each stands on the ones before it.
6. **The exits.** Green: an edit of one crate runs no check of the other, `m:t060-done-rust-edit` recorded beside `m:done-rust-edit`, the defect scenarios caught by the same rule; SC-002 itself is T070's exit. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `make done` on a one-line Rust edit, timed against `m:done-rust-edit`,. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T062 Approach (checklist part A)

1. **The goal, in the world.** The Rust gate computes a file's id: a `.rs` file's by `rust_tokens`, through the blob-keyed cache in one format with atomic writes, and a kept stamp still verifies. A `.py` file's id stays Python's own `ast.dump`, asked of `codeid.py` by path, one process a run with all the misses in it, its failure failing the gate and no substitute written (`ask:449-T062-py-id`); `codeid.py`'s `.rs` branch stays for its Python callers, held equal to `rust_tokens` by a differential test while both exist.
2. **The constraints.** FR-001, FR-002, FR-003, FR-006; the round arbiter's `ask:449-T062-order`.
   **Decisions** (2026-11-08; `m:t062-content-ids`, 1,112 files with no mismatch, 567 of them against the real cache's own ids):
   - (a) THE RUST GATE'S ID: `rust/gate/src/codeid.rs` ports `rust_tokens` and `git_blob_id`, and reads and writes the same `semantic-id-cache-2.json`, written whole and renamed in with what another writer added merged in; `gate-stamp.py`'s own write now does the same, so neither side loses the other's entries.
   - (b) ONE SHARED `sha1`/`sha256`: the crate depends on `rust/guard` by path for them, rather than copying them. `rust_checks.py` therefore reads a crate's coverage for its own files only, since a path dependency's sources otherwise enter the report, and T060's id already counts a crate built from another by path.
   - (c) NOTHING SWITCHES YET: T063 is the first Rust caller. `l7r-gate content-ids` is the surface, and until then `tests/tooling/test_codeid_rust.py` holds the two `.rs` branches equal.
3. **Where each comes from.** `m:ci-sources`, to be taken when this task starts; the real `semantic-id-cache` and the recorded engine keys.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** Leaf first by what imports what (`ask:449-T062-order`), each stands on the ones before it; callers reach the binary once a process or in a batch, never one spawn a file (FR-006, SC-002).
6. **The exits.** Green: every tracked `.rs` file's id equals the Python's, the recorded keys still verify, the Rust gate's callers switched in one commit, `codeid.py` placed in phase 4 by FR-001. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** The differential over every engine file and the kept keys: no mismatch. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T062 part B (2026-11-09T01:35:27Z)

1. **What exactly is refusing?** The red-gate tripwire of T061's two reds, attributed here because T062 was the active task when it was ruled. T062's own work has not refused: the differential is clean.
2. **A3 again.** Green: `m:t062-content-ids`.
3. **A4 again.** The rule is the process's, and it fired on T061's reds, ruled and landed.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "The two reds were T061's and are fixed." No question follows.
7. **The next step is a measurement.** T062's plan review, then its gate.
8. **Before offering routes.** None offered.
9. **After a ruling.** The ruling's step was T061's gate, run and green.

<!-- plan-archive: archived 2026-11-08 -->
### T72 Approach (checklist part A)

1. **The goal, in the world.** What the gate last verified is written by one implementation.
2. **The constraints.** FR-001, FR-002, FR-003 (one writer, one cut), FR-006 (one spawn a process or a batch, ids read from the kept cache and Python asked only for its misses). Slice 3 of the round arbiter's `ask:449-T063-slices`, moved out of T063 so that its first two slices could land and tick as a task.
   **Decisions**:
   - THE STATE AND THE HASHES ARE THE RUST GATE'S: `state.py`'s writer, reader, tooling hash and `already_verified` become `l7r-gate state` (`rust/gate/src/state.rs`), `gate_config.config_hash` becomes `l7r-gate config-hash` (`hashing.rs`), and `coverage_exempt.py` becomes `l7r-gate coverage-exempt` (`exempt.rs`) and is deleted; the Makefile's `$(STATE)`, `verified-done`, `tooling-green` and the coverage recipes, and `__main__`'s subcommands for them, switch in that commit. `m:t72-state`: the record, the tooling hash and the config hash equal the Python's on this tree, so a recorded tooling hash still reads.
   - WHAT IS LEFT OF `state.py` IS A CLIENT, as `delta.py` is: the `VerificationState` type, two constants `decision.py` and `dispatch.py` take, and calls to the binary once a process, until T064 ports them.
   - THE TWO HASHES STAY EQUAL TO THE PYTHON'S, over Python's `ast.dump`: changing their form would re-run the tooling tests once for nothing, and FR-002 asks for the same outputs. Their input is the concatenated dumps, which no per-file id can rebuild, so what is kept is the dump itself, by blob, under `<git dir>/semantic-dumps/`, and `codeid.py --semantic` is asked once a run only for the blobs it lacks (FR-001's cache misses, FR-006): an unchanged tree starts no Python. A form unused for a week is dropped.
   - `runlog.py` MOVES TO T064 AND `scripts_readers`/`tooling_modules` TO T071: every caller of each is in that task, so porting them there needs no client at all (FR-003, one cut). `tasks.md` says so on all three boxes.
   - THE COVERAGE RECORD (`ask:449-T72-coverage-exempt`, the round arbiter): the reach branch, `import_graph`, `_top_names`, `reached_from_kept` and `seeded` are dropped; `load` refuses an entry naming no stages, with a test; `report` asks coverage.py through `codeid.py --missing`, one process with every live entry, only when one exists, and its failure fails the gate. Nothing else imports the dropped functions: `git grep -nE 'seeded|import_graph|_top_names|reached_from_kept'` over the code, and `specs/448-engine-coverage-relax/*.py` holds no import of `coverage_exempt`. Cases retired with them: `test_a_whole_engine_entry_goes_stale_only_when_its_file_is_gone`, `test_a_whole_engine_entry_is_live_while_only_slated_code_reaches_it_and_stale_once_kept_code_does`, `test_seeded_takes_each_unaccepted_stages_own_python_with_every_stage_it_serves`. Every other case of `test_coverage_exempt.py`, `test_state.py` and `test_gate_config.py` replays in the Rust tests or against the binary.
3. **Where each comes from.** the state files as they stand; `m:ci-sources`.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** After T063, whose `l7r-gate stamp` and `l7r-gate delta` it stands on; callers reach the binary once a process or in a batch, never one spawn a file (FR-006, SC-002).
6. **The exits.** Green: the verification state written before the switch still reads; no state file has two writers at any commit. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `make done` reuses a last green result across the switch. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-08 -->
### T064 Approach (checklist part A)

1. **The goal, in the world.** The conditions on a remote run, the make-only refusal in-process and the switches in Rust.
2. **The constraints.** FR-001, FR-002; constitution on money (a paid dispatch is not run to test this).
   **Decisions** (the round arbiter's `ask:449-T064-slices`):
   - ONE LANDING: `config.py`, `switches.py`, `decision.py`, `door.py`, `features.py`, `imagecheck.py`, `cachepolicy.py`, `runlog.py` and `dispatch.py` become `l7r-gate ci`, `switches` and `lifecycle` (`rust/gate/src/ci/`), and are deleted with their Python tests; `ci/__main__.py` keeps only `incremental` until T071. The Makefile's recipes switch in that commit. `m:t064-remote`: on the commit before the switch the route, the whole status, the spend report, the door, the switches and the idle flag equal the Python's.
   - `_invocation.py` MOVES TO PHASE 4 with its last Python caller: FR-001's amendment cites the ruling. `via_make.rs` is the same check for `l7r-gate`'s own binaries: each runtime decides for its own process and neither calls the other (FR-003, FR-005); `ci/via_make/tests.rs` holds a tree with `l7r-gate` between make and the process, and `tests/tooling/test_invocation_under_gate.py` the Python's side.
   - THE AWS BOUNDARY IS A TRAIT WITH THE `aws` CLI BEHIND IT (`buildspec/run.sh` already uses it; `setup-dev-env.sh` installs it). The adapter is tested through a fake `aws` on the path, CLI-shaped JSON at the process boundary (`ci/aws/tests.rs`). **The live adapter is unproven**, no paid run may prove it, and the first paid run after remote is turned on is its proof (`dev/rust-tooling.md`).
   - THE ONE REGISTRY OF OPERATIONS STAYS IN `_invocation.py`, read by the gate as text (`dispatch::operations`), until phase 4; `spec-verdict` and `--holding` stay in `hm_arbiter.py` and `speckit-todo.py`, asked by path once a process, until phase 3.
   - WHAT THE TESTS REPLAY, from a listing of `def test` in each deleted file at the commit before: every case of `test_dispatch.py`, `test_decision.py`, `test_door.py`, `test_features.py`, `test_imagecheck.py`, `test_cachepolicy.py`, `test_runlog.py`, `test_config.py`, `test_measure_route.py`, `test_cache.py` and `tests/test_switches.py` is a Rust test under `rust/gate/src/ci/` or goes as follows. Those that read the real tree (the buildspecs, `run.sh`, `Dockerfile.ci`, the Makefile, the example secrets) are `ci/real_tree.rs`. `test_only_a_BUILD_can_write_the_freshness_state_a_build_restores`, which read the dispatcher's source, is now behavior: `a_check_dispatches_one_parked_build_and_records_it` asserts no `put_object` under `cache`. `test_the_module_documents_the_state_that_is_now_TRUE` reads `cachepolicy.rs`'s own text. The three of `test_features.py` that exercise the verdict rather than the feature check (`test_a_spec_the_round_arbiter_accepted_at_its_cap_is_faithful`, `test_a_spec_ruled_on_an_asked_round_is_faithful`, `test_the_merge_and_the_review_gate_read_one_verdict`) are `tests/tooling/test_spec_verdict.py`, against `hm_arbiter.py spec-verdict`, and go with `hm_arbiter.py` in phase 3; that the gate's reader takes its verdict from there is `the_merge_and_the_review_gate_read_one_verdict` in `ci/features/tests.rs`, the real Python on the real script, the piece's one end-to-end test (FR-008). `test_a_rule_is_addressed_by_id_and_a_missing_one_is_loud` is `a_rule_is_addressed_by_id_and_a_missing_one_is_loud` in `cachepolicy.rs`, the function ported with `l7r-gate lifecycle <id>` as its caller. `test_env_var_alone_opens_nothing` is `an_environment_variable_alone_opens_nothing` in `ci/door/tests.rs`. `tests/tooling/test_switches.py` stays: its six cases (`test_make_uses_six_workers_on_a_shared_box_and_every_core_on_codebuild`, `test_make_remote_targets_refuse_when_remote_is_off`, `test_make_switch_targets_require_a_reason_and_commit`, `test_make_done_short_circuits_on_an_unchanged_gate_key`, `test_quick_collects_only_the_quick_tree`, `test_the_directory_decides_when_a_test_runs`) drive the real Makefile through make, so they test recipes, and port with those recipes in T069.
3. **Where each comes from.** `dev/ci.md`; `dev/switches.json`.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** Leaf first by what imports what (`ask:449-T062-order`), each stands on the ones before it; callers reach the binary once a process or in a batch, never one spawn a file (FR-006, SC-002).
6. **The exits.** Green: their suites' verdicts unchanged, no remote run spent to prove it. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** The dispatcher's tests against a stubbed AWS. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-09 -->
### T065 Approach (checklist part A)

1. **The goal, in the world.** The checks the gate runs over text are Rust.
2. **The constraints.** FR-001, FR-002, FR-008.
   **Decisions** (the round arbiter's `ask:449-T065-scope`):
   - SIX CHECKS, ONE LANDING: `check-file-scale.py`, `check-stale-dirs.py`, `check-question-size.py`, `check-rust-tooling.py`, `check-research-pointers.py` and `check-house-style-delta.py` become `l7r-gate check <name>` (`rust/gate/src/checks/`) and are deleted with their Python tests; the Makefile, `preflight.py`, `push_checks.py` and `push_check_times.py` switch in that commit, and they are every caller: `git grep -nE "check-(file-scale|stale-dirs|question-size|rust-tooling|research-pointers|house-style-delta)\.py" -- Makefile '*.mk' '*.sh' 'buildspec/*' 'scripts/*.py' 'l7r/*.py' 'rust/*.rs' .claude/settings.json` then names no invocation (what remains is a Rust check's own header comment and its table of fixture files). Over a scratch clone of the repository with sixty commits of delta, each of the twelve invocations gives the Python's stdout, stderr and exit status (observed 2026-11-09, method: each run both ways in that clone and its three streams compared, a comparison no command can repeat once the Python is deleted).
   - THE FOUR THAT OUTLAST PHASE 2 are FR-001's. THE PREDICATE IS PER CHECK AND IS ITS READ SET, read off its source and the modules it imports: `check-duplicate-defs.py`, the `.py` under `l7r/`, `tests/`, `pool/` and `legacy-hand-authored-pool/` (its `SCAN_ROOTS`); `check-function-cap.py`, the `.py` under `l7r/`, `tests/`, `scripts/` and `pool/` (its `TREES`) and `pyproject.toml`; `check-partial-citations.py`, `research/partial-confirmations.jsonl`, `research/source-access.json`, `research/to-download.md`, `research/sources/010-works-cited/`, `research/archive/`, `research/questions/*.notes.html` and `access_tags.py` and `downloads.py`; `check-entry-headings.py`, `research/questions/`, the modal texts under `l7r/diagram/interactive/assets/modals/` from which a class's `Entry:` is parsed, and the `.py` under `l7r/diagram/interactive/` (what `classes` and `sources` import); each also its own script. `l7r-gate check needs <check>` exits 0 when the change since the merge base holds a file of that set, or when there is no base to compare with. Who starts them, from `git grep -nE "check-(duplicate-defs|function-cap|partial-citations|entry-headings)" -- Makefile '*.sh' 'scripts/*.py' 'buildspec/*' 'l7r/*.py' .claude/settings.json 'rust/*.rs'` (and `l7r/*.py` holds only a comment naming one): the four `make quick`/`make static` recipe lines and the `delta:` rows of `push_checks.py`, all of which ask first; the two others run none on a change: `Makefile` line 404 (`make audit`'s listing, importing only `SILENT`) on request, and `push_check_times.py` (the timing tool, on request, which T068 ports); `preflight.py` calls none of the four. `a_rust_only_change_starts_none_of_the_python_checks` (Rust, both directions and each read kind), `test_the_four_checks_still_in_python_do_not_start_on_a_rust_only_change` (a `.notes.html` starts the two that read it and neither that reads only Python; a `.py` under `l7r/` outside `interactive/` starts only the two that read it) and `test_every_makefile_line_starting_a_retained_python_check_asks_first` hold it.
   - THE POINTER CHECK SCANS BY OCCURRENCE: the Python's patterns run at every position of a line in `fancy-regex` ran past five minutes on the tree and was stopped (observed 2026-11-09, method: the wall clock on the first version); the port anchors each at an occurrence of `research/` or of a page name and reads the files on several threads with no cache: 0.3 s on the tree against the Python's 0.41 s on its content cache and 5.5 s without it, and the two agree over 32,000 repository lines, 534 chunks, no mismatch (both observed 2026-11-09, method: repeated runs and a line-by-line differential in a scratch repository).
   - THE WORD TABLE IS COMPILED IN (`include_str!` of `house_style_words.tsv`), so `test_a_moved_table_fails_loudly_rather_than_matching_nothing` has nothing left to test (a moved table does not compile), and `test_the_word_list_is_the_hook_s_own` is true by construction: the check (`rust/gate/src/checks/house_style_delta.rs`) and the guard (`rust/guard/src/guards/house_style_hooks.rs`) `include_str!` the one file. `test_the_rust_guards_word_table_is_the_decisions` is kept, in `tests/tooling/test_house_words.py`, until `hm_house.py` goes.
   - WHAT THE TESTS REPLAY: every case of `test_file_scale.py`, `test_house_style_delta.py`, `test_question_size.py`, `test_research_pointers.py`, `test_check_rust_tooling.py` and `test_stale_dirs.py` is in `rust/gate/src/checks/*/tests.rs` before those files are deleted, but these: the two named above; `test_the_file_cap_is_found_a_reader`, whose subject (a Python script reading `.py` by lines) is gone; what it guarded, that the detector finds a real reader of source, is replayed by `the_detector_finds_a_real_reader_on_the_real_tree`, which names a surviving reader, `check-function-cap.py`, and which goes red if the detector goes blind, and by `a_reader_of_each_kind_with_no_row_fails_and_a_row_clears_it` on a planted reader of each kind; `fragment_move.py`'s self-test, moved to `tests/tooling/test_fragment_move.py`. Elsewhere `test_content_cache.py`'s pointer case and the pointer half of `real_tree/test_content_cache.py` go: those compare a content cache's answers with and without it, and the compiled check has none. FR-006's three design fixes are the import graph kept per process, semantic file ids from the kept cache and a fixture built once; the pointer check's cache is none of them, and leaving it out costs nothing (the timing above), and the stale-dirs row of `test_push_checks.py`'s in-process cases (the compiled check is no `runpy` run).
   - THE MEASUREMENT CENSUS, over the files this task ports or deletes: `git grep -nE "check-(file-scale|stale-dirs|question-size|rust-tooling|research-pointers|house-style-delta)|check-<name>|test_(file_scale|house_style_delta|question_size|research_pointers|check_rust_tooling|stale_dirs)" -- 'specs/*/measurements*.json'` returns nothing. A differential against a deleted Python cannot be re-run after the deletion, so this task's are dated one-shot observations above, and no entry of `measurements.json` needs Python.
3. **Where each comes from.** `m:gates-sources`, to be taken when this task starts.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the phase's plan above; each stands on the ones before it.
6. **The exits.** Green: each check's findings over the repository equal the Python's before it is deleted. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** Each check's differential over the repository: no mismatch. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

