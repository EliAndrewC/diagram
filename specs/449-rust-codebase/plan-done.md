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

