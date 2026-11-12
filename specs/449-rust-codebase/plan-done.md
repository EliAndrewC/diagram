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

<!-- plan-archive: archived 2026-11-09 -->
### T066 Approach (checklist part A)

1. **The goal, in the world.** What refuses a plan or a spec, and the question `engine_freeze_hooks` asks, are Rust.
2. **The constraints.** FR-001, FR-002, FR-003; `ask:449-T052-round3` for `engine_edit.py`.
   **Decisions** (the round arbiter's `ask:449-T066-scope`, its five conditions):
   - ONE LANDING: `plan_gate.py`, `plan_sections.py`, `plan_seen.py`, `plan_lint.py`, `plan_bundle.py`, `approach_gate.py`'s `owed`, `ruled` and `owe`, `spec-lint.py`, `spec_figures.py`, `wording_only` and `engine_edit.py` become `l7r-gate plan <verb>` (`rust/gate/src/plan/`) and `l7r-gate check spec-lint`, and every Python body is deleted in that landing (condition 1). The Makefile, `plan-gate.sh`, `check-bundle-hooks.sh`, `push_checks.py`, `push_check_times.py` and the guards `pair_hooks`, `review_round_hooks` and `engine_freeze_hooks` switch with it; `git grep -nE "(plan_gate|approach_gate|plan_bundle|plan_lint|spec_figures|plan_seen|engine_edit|plan_sections)\.py|spec-lint\.py" -- Makefile '*.mk' '*.sh' 'buildspec/*' 'scripts/*.py' 'l7r/*.py' 'rust/*.rs' .claude/settings.json` then names no invocation (comments naming where a port came from aside).
   - THE VERDICTS ARE THE PYTHON'S: over every spec of the repository, at the commit before the deletion (observed 2026-11-09, method: each run both ways in a scratch clone, stdout, stderr, exit status and every bundle file compared): the spec lint on all 367 specs, no mismatch; `task_sections` and `blocks` on 325 plan files, no mismatch; `owed` on 281 specs, no mismatch; `decide` on 120 sampled task sections, bundles included, no mismatch; `delta` on 281 specs, no mismatch.
   - THE FOUR WHO STAY PYTHON (condition 5, FR-001): `make task-start` moves to `scripts/task_start.py` beside `plan_hold.py` and `phase_sources.py` (which read `speckit-todo` and `work_budget_bundle`), and `wording.refusal` stays (it reads `codeid.py`'s `semantic_bytes`): phase 3. The cohort's approach trigger moves into `cohort_known.py` (T068), and asks the verb `plan approach owe-in-flight`. `scripts/plan_door.py` is the Python callers' forwarder, deleted with its last caller.
   - CONDITION 2, ONE WRITER PER STATE FILE: `task_start.py` writes `active-task`, `.specify/feature.json`, `task-starts.jsonl` and `phase-sources.json`; `plan_hold.py` writes nothing. No ported verb writes any of those (`approach.rs` and `task.rs` read them). `approach-owed.json`, `plan-review.json` and `plan-seen/` are written only by the Rust verbs.
   - CONDITION 3, NO PYTHON ON A PLAIN CALL: `task_start.py` runs on `make task-start`, `wording.refusal` and the door on `make tick` and `make land`, the door on `hm_arbiter.py ruled`, on `claims_carry.py` at a landing, and on `hm_planhold.py`, which `record_edit_gate.rs` starts only while a plan review's hold is live; the cohort trigger on `make cohort`. None runs on a plain Bash call, a plain Edit or a `make done` whose change holds no file they read (`git grep -nE "plan_door|task_start|wording\.|phase_sources|plan_hold" -- Makefile '*.mk' '*.sh' 'buildspec/*' .claude/settings.json 'rust/guard/*.rs' 'scripts/*.py'`).
   - CONDITION 4, NO DOOR IN A LOOP: each caller asks once per run; the one loop, `hm_planhold.held` over the live holds, asks a plan's sections and blocks once, by the door's cache on the plan's text.
   - WHAT THE TESTS REPLAY: every case of `test_plan_gate.py`, `test_plan_blocks.py`, `test_plan_lint.py`, `test_plan_arbiter_accept.py`, `test_plan_bundle_request.py`, `test_approach_gate.py` and `test_spec_lint.py` is in `rust/gate/src/plan/*/tests.rs` or `checks/spec_lint/tests.rs` before those files are deleted, but these: the cases that drive `tick-task.py`, `task_start.py`, `hm_arbiter.py` and `wording.refusal` stay in Python against the door (`tests/tooling/test_plan_door.py`); the cohort's in `test_cohort_approach.py`; the `make figures` cases in `test_make_figures.py`; `test_there_is_one_definition_of_a_figure` has nothing to compare (the one definition is `spec_figures.rs`, and `review_prereq.py` asks it through `check spec-lint --figure-pattern`). One message differs, by the ruled case `ask:449-T066-json-message` in FR-002: a `measurements.json` that is not JSON quotes serde's parse error inside the parentheses where Python quoted its own; the verdict, exit status, location and fixed words are the Python's.
   - A DEFECT FIXED ON THE WAY (constitution XIV): the wrapper took its tree from a path holding `..` wrongly; a hook reaching it through its own `../gates` failed to build and read as "no refusal". `l7r-gate.sh` normalizes such a path. No suite case's expected verdict changed with it.
3. **Where each comes from.** `specs/*/plan.md` as the corpus.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the phase's plan above; each stands on the ones before it.
6. **The exits.** Green: over every spec and plan in the repository the verdicts equal the Python's, `decide` over a sample of 120 task sections (each builds a bundle and asks the claims triage, minutes apiece). Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** The differential over every spec and plan, `decide` on its sample: no mismatch. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-09 -->
### T067 Approach (checklist part A)

1. **The goal, in the world.** The landing's refusals are Rust, with `scripts/hooks/lib/hm_conflict.py` (`push_checks.py`, its make target) and `scripts/hooks/lib/own-make.sh` (`one-gate.sh`), each held to FR-002 before it goes.
2. **The constraints.** FR-001, FR-002.
   **Moved** (`ask:449-T067-scope`): the carried item of `ask:T063-browser-raw` goes to T071 with `preflight.unseen`, its remaining caller; `engine_edit.docstring_only` was ported at T066 with the same verdict.
   **Decisions** (the round arbiter's `ask:449-T067-scope`):
   - ONE LANDING: `gate_lock.py` and `own-make.sh` become `l7r-gate lock` and `l7r-gate own-make` (`rust/gate/src/lock.rs`), `hm_conflict.py` `l7r-gate check conflict` (`checks/conflict.rs`, over the guard's one detector), `rust_checks.py` `l7r-gate rust` (`rustc.rs`), `push_gates.py` and `push_checks.py` `l7r-gate push-gate` and `push-checks` (`push.rs`), and every Python body is deleted in that landing. `git grep -nE "(gate_lock|push_gates|push_checks|rust_checks|hm_conflict)\.py|own-make\.sh" -- Makefile '*.mk' '*.sh' 'buildspec/*' 'scripts/*.py' 'l7r/*.py' .claude/settings.json` names no invocation: its two lines are a docstring in `l7r/diagram/ci/pool_readers.py` and a past feature's `specs/430-faster-landings/time-push-gates.sh`.
   - `push_checks.py`'S ROWS, SETTLED (the ruling's clause): all 29 rows are the table `CHECKS` in `push.rs`, each a `Tool::Gate` row asking the port or a `Tool::Py` row running the file by path, and each `Tool::Py` row's file is placed by FR-001 (`check-duplicate-defs.py`, `check-function-cap.py`, `check-entry-headings.py`, `check-partial-citations.py`: `ask:449-T065-scope`; `memo_check.py`, `close_check.py`: this ruling; `make-docs.py`, `ledger_owed.py`, `downloads.py`, `speckit-todo.py`, `money_candidates.py`, `gm_review.py`: phase 3, the rest of `scripts/`). No row's placement is left open; a row may still run only when the change holds what it reads, by its `needs`.
   - THE T065 CLAUSE ON `close_check.py` AND `memo_check.py`: `git grep -nE "close_check|memo_check" -- Makefile '*.sh' 'scripts/*.py' 'rust/*.rs'` shows them run by the push's table, by `make record CHECK=1` and `make glossary CHECK=1`, and imported by `tick-task.py` and `gm_review.py` at a close. `git grep -n "push-checks" -- Makefile` returns nothing, and `git grep -n "l7r-gate.sh\" push-checks" -- '*.sh'` returns one line, `scripts/sync-with-main.sh`'s `done` step, the push, and the Makefile calls that script only for `backup` and `render-sync` (`git grep -n "sync-with-main.sh" -- Makefile`); so `make done` reaches neither file, nor does any guard (`git grep -nE "close_check|memo_check" -- 'rust/guard/*'` returns nothing), and no plain Bash call, plain Edit or `make done` starts them and no trigger needed narrowing.
   - THE VERDICTS ARE THE PYTHON'S (observed 2026-11-09, method: a scratch clone at the commit before the deletion, each command run through the Python and through the binary, exit status and output compared; a one-shot, the Python being gone): the conflict check's `--selftest` and `--tracked` on a clean tree and on one holding two conflicted files; `push-gate skip` for `claims`, `entry`, `cohort` and an unknown gate at merge bases 1, 3, 8, 20, 60 and 150 commits back, and for a pass stored by the Python and read by the Rust; `lock held` and `acquire` on an empty directory and on a dead owner; the 29 names of `push-checks --list`. `own-make` beside the old `own-make.sh` on no run, a `make done` in the tree, a `make map` in another tree, a target with arguments, a process whose name only looks like make and no arguments: 9 cases, none differ, and `lock/tests.rs` replays its rule that only a make of this target in this tree counts. Of the other 31 (3 of the conflict check, 24 of the skip, 1 of a stored pass, 3 of the lock; the 29 names are a separate comparison), 6 differ, all one case: an unknown gate's usage text names the new command, exit status 2 both ways, which FR-002 does not hold (a usage line names its own program). The first run found two real differences, both fixed before this count: a `./` before a file name when the root was `.`, and a stored pass's key missing git's final newline, so a pass stored before the switch would not have held.
   - WHAT THE TESTS REPLAY: every case of `test_gate_lock.py` and `test_push_gates.py` is in `lock/tests.rs` and `push/tests.rs`; of `test_push_checks.py`, the runner's first-refusal, the kept self-test, the make-page and money rows, the retained checks' delta predicates and the Makefile asks-first case are in `push/tests.rs`, and the file is deleted. NOT REPLAYED, each with its reason: `real_tree/test_content_cache.py` (the whole tree's conflicts the same with the cache on and off) and the `L7R_CACHE_OFF` half of `test_content_cache.py`, because the Rust conflict check keeps no cache to compare (it reads every file on several threads); `real_tree/test_push_checks.py` (each check in one process gives what it gives alone), because no row runs in the runner's process any more, each is a child with its own exit status. `test_rust_tooling.py`'s 12 cases, which run the real cargo, keep driving `l7r-gate rust` as a black box for now, under the spec's Assumptions clause, verbatim: "Each piece's Python tests are rewritten as Rust tests when the piece is ported; during a phase, a Python test may drive a Rust binary black-box only until that piece's Rust tests replace it." The clause's limit is the phase, so T070, the close of phase 2, replaces the file and deletes it (its row in `tasks.md`), under FR-008 ("A tool's tests MUST each take under a tenth of a second, but its one end-to-end test against the real command"): `l7r-gate rust` is one tool, so ONE Rust end-to-end test runs its subcommands against the real cargo on a fixture crate with a breach of each kind, and every other case is a `World` seam test with a fake cargo. Until then the 12 cases, which were the Python tool's own, pass against the binary, and they are FR-002's hold on `l7r-gate rust`.
   - THE CALLERS' SHARE: `cover_changed.py` (T071) asks `l7r-gate rust uncovered`; `hm_approval.py` loses the halves only `push_checks.py` called.
   - DEFECTS FIXED ON THE WAY (constitution XIV): the port's `dead` searched once per name with a Unicode `\b` over each whole crate and ran four hours and ten minutes on the guard crate before it was killed (observed 2026-11-09, method: the process's elapsed time from `ps`); it now counts the text's words in one pass, and took 11 s with its rebuild (observed 2026-11-09, method: `time` around `l7r-gate rust dead`). A test's fake script could fail with "Text file busy" when another test forked while it was open for writing; `write_executable` writes it through a child process in both crates.
   - THE WATCHDOG (the GM 2026-11-09, "I thought we had tooling to prevent a stuck command from blocking us from doing work for that amount of time"): a stall is a silent session, and a session answering the GM over a stuck background `make` is not silent. Each pass of `stall_watchdog_hooks` now also tells a session, once per make, about a `make` in its clone past `STALL_LONG_RUN` (default 1,800 s, CONVENTION and a knob: at most 1,300 s in 1,051 of the 1,052 gate runs recorded for October and November 2026, observed 2026-11-09 from `dev/run-log/`). It reports and kills nothing.
3. **Where each comes from.** the landings recorded under `dev/run-log/`.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the phase's plan above; each stands on the ones before it.
6. **The exits.** Green: each suite's verdicts unchanged; the done line below met. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `git ls-files 'scripts/gates/*.py'` returns only the files FR-001 names as owed by T068 (`check-run-plausible.py`, `check-tool-signals.py`, `cohort_gate.py`, `room_table.py`), T071 (`preflight.py`, `cover_changed.py`, `refresh_baseline.py`, `pool-readers.py`), phase 3 (`close_check.py`, `memo_check.py`, `plan_hold.py`, `phase_sources.py`, `wording.py`, `check-partial-citations.py`) or phase 4 (`codeid.py`, `check-entry-headings.py`, `check-duplicate-defs.py`, `check-function-cap.py`), and neither of `scripts/hooks/lib/hm_conflict.py` and `scripts/hooks/lib/own-make.sh` is tracked (`ask:449-T067-scope`). Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-09 -->
### T068 Approach (checklist part A)

1. **The goal, in the world.** What things cost is measured by Rust.
2. **The constraints.** FR-001, FR-002, FR-008.
   **Decisions** (the round arbiter's `ask:449-T068-scope`; this task is its first slice, in the ruling's words "gate checks and cohort", whose list named `cohort_seeds`; the ruling's last slice takes only the four tools it adds there and `model_trial`):
   - ONE LANDING: `cohort_gate.py`, `cohort_known.py`, `room_table.py` and `cohort_seeds.py` become `l7r-gate cohort` (`rust/gate/src/cohort.rs`, `cohort/`), `check-run-plausible.py` and `check-tool-signals.py` become `l7r-gate check run-plausible` and `tool-signals`, and every Python body goes in that landing. `git grep -nE "(cohort_gate|cohort_known|room_table|cohort_seeds|check-run-plausible|check-tool-signals)\.py" -- Makefile '*.mk' '*.sh' 'scripts/*.py' 'l7r/*.py' 'rust/*.rs' .claude/settings.json 'tests/*.py' 'tests/*.sh' 'specs/*.py' 'specs/*.sh'` names no invocation: its remaining lines are the ported modules' first comments saying where each came from and one comment in `tests/tooling/test_switches.py`; the Makefile, `cohort-gate.sh`, `review-gate.sh`, `land.py`, `cover_changed.py`, `arbiter_bundle.py` and `probe.py` ask the gate, once a run each. `make cohort-seeds`, which the docs name and the Makefile had lost, is a target again.
   - WHAT STAYS PYTHON, AND WHY IT IS NO DOOR IN A LOOP: `codeid.py` (phase 4, `ask:449-T062-py-id`) gained `--debug-free-equal`, which a run starts at most once, with every commit pair that run must ask in that one invocation (`round:spec-fidelity|plan:449-rust-codebase#T068@3`; `Repo::prime` gathers them before any is asked, nothing kept per pair between runs, and a test holds the count at one with several differing records), beside the id-miss process of `ask:449-T062-py-id`; never on a plain Bash call or a plain Edit, and a failure fails the gate with no substitute answer, because counter blocks are read off the Python AST; a changed `.rs` compares by bytes as before. `ratchet.py` (slice 2) keeps the pinned baselines, read off its text by `run_plausible::baseline` until that slice ports it. `fresh_tally.py` (slice 3) carries its own three-line reading of a record's fresh seeds, so it starts no process per record.
   - THE VERDICTS ARE THE PYTHON'S (observed 2026-11-09, method: a scratch clone at the commit before the deletion, each command run through the Python there and through the final binary on the same tree, exit status and output compared): `check`, `needs-baseline`, `counter-only`, `rust-owed` and `fresh-seed` at HEAD and at 1, 5, 40 and 200 commits back and at a reference that does not resolve; `cohort_known` over every record; `cohort_seeds` over every record; the room table; `check-run-plausible` on three targets, six durations and two modes, on four `MAKEFLAGS`, and with `--reuse`; `check-tool-signals`. 59 cases, 0 differ, re-run after the one-process change on the commands it touches. Two more cases, an unknown verb and a missing argument, differ only in the usage line naming the new command, exit status 2 both ways. A first version of the port read a `USAGE_LOG_TOOL` constant as a call where the Python read only a file holding the words `usage_log`; that was corrected before this count. It showed a gap the Python had missed, `conflict-markers` recording runs no registry row named, and that is fixed in the tree, not in the check: `conflict.rs` carries the words and the registry its row.
   - WHAT THE TESTS REPLAY: every case of `test_cohort_gate.py`, `test_cohort_known.py`, `test_cohort_approach.py`, the three `cohort_seeds` cases of `test_measure_reports.py` and `test_run_plausible.py`'s cases is in `cohort/tests.rs` and `run_plausible/tests.rs`, the floor reading the real `ratchet.py` and the replay of every recorded green `done` through it among them, with a stand-in Python, because an engine key's docstring and counter rules are `codeid.py`'s and `delta`'s and are tested there. `test-check-tool-signals.sh` stays the end-to-end suite and drives the binary. NOT REPLAYED, with its reason: `test_it_runs_as_a_script` (the wrapper is what runs). THE SAME CODE, TESTED WHERE IT LIVES: the docstring and comment cases of `test_cohort_gate.py`, `test_cohort_known.py` and `test_a_commit_is_on_mains_engine_when_no_engine_file_differs` are the engine key's rules, and `Repo::engine_key` is one call of `delta::engine_key` and `delta::engine_key_worktree` in `rust/gate/src/delta.rs`; `l7r/diagram/ci/delta.py` is the Python door to those same functions, and `tests/tooling/ci/test_delta.py` runs them over the real `codeid.py` (`test_the_key_is_blind_to_comments_docstrings_and_formatting`), so the port's key is the code those tests run.
   - THE CENSUS: `git grep -nE "cohort_gate|cohort_known|room_table|cohort_seeds|check-run-plausible|check-tool-signals" -- 'specs/*/measurements*.json'` returned one command, rewritten to `l7r-gate cohort seeds --record` in this commit (`m:375-a8-cohort-seeds`).
3. **Where each comes from.** `m:measure-sources`, to be taken when this task starts.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the phase's plan above; each stands on the ones before it.
6. **The exits.** Green: the slice's six files gone, each verdict the Python's by the one-shot differential below. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `git ls-files` names none of the slice's six files; `make hooks-test` and `make static` run them through the port. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-09 -->
### T74 Approach (checklist part A)

1. **The goal, in the world.** A past feature's Python that nothing runs is gone, not ported: the GM, 2026-11-09, "I don't think we need to port the past feature harnesses if those are not still used."
2. **The constraints.** FR-001's words on `specs/`: a file something still runs is ported like any other, and one nothing runs is deleted and not ported.
3. **Where each comes from.** `git ls-files 'specs/*.py'`, the Makefile and code outside `specs/`, every `specs/*/measurements*.json` command.
4. **Do they describe the world here?** Tooling: no researched value moves, and no recorded figure is touched.
5. **The order.** The census, then the deletion, one landing.
6. **The exits.** Green: the gate's own checks pass with the files gone. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** Each deleted path, its feature directory with its path inside it, and its name in the same feature's `.py`, `.sh`, `.mk`, `.yml` or `.json`, are searched across every tracked file but the records named below, and the only hits left are in the named files of the quoted list.
   **Decisions** (FR-001, the GM 2026-11-09):
   - THE TEST OF "STILL USED": something still runs a file under `specs/` when its path, or its feature directory with its path inside that directory, or (in the same feature) its name in a `.py`, `.sh`, `.mk`, `.yml` or `.json`, appears in any tracked file, of any feature and any extension, outside the records named here: `spec.md`, `plan.md`, `plan-done.md`, `tasks.md`, `research.md`, `data-model.md`, `quickstart.md`, `request.md`, `*.jsonl`, the `contracts/`, `checklists/`, `briefs/` and `audit/` of a feature, `dev/run-log`, `bypass-log`, `perf-log`, `cohort-log`, `review-ledger`, `research/`, whatever under `pool/` is not a `.py`, and the recorded command corpus `tests/hooks/fixtures/` (`ask:449-T052-inline-census`: a string fed to a guard as input is no run). A hit keeps the file, but for these named records, which quote a file as history: each feature's `plan-review.json`, `specs/303-research-organization/migration.md`, `specs/312-uncited-source-catalog/prep.md`, `specs/447-semantic-index/research/*`, `specs/286-hand-sheet-labels-placed/sc002.json` and `specs/288-sources-ledger-and-page-cache/measurement/result.json`. `tests/tooling/fixtures/brief_load/` holds briefs `scripts/pages/brief_load.py` parses as text (`test_brief_load.py`), never executed.
   - THE ROUTES THAT NEVER SPELL A PATH (observed 2026-11-09, method: `git grep` over the Makefile, `*.mk`, shell, `scripts/`, `rust/`, `l7r/`, `tests/`, `pool/*.py` and `.specify/scripts` for `specs/*`, `specs/[`, a `glob`, `rglob` or `find` over `specs`): each walks feature directories for their `spec.md`, `tasks.md` or records; none collects or runs a `.py` under `specs/`, and `testpaths` holds pytest to `tests/`.
   - THE CENSUS (observed 2026-11-09, method: that test, over `git ls-files`, 6,469 files searched, a one-shot script): 222 files; 138 deleted, 16670 lines; 84 kept, each ported or ruled on at its own task in phase 3, or deleted there if it no longer runs. The first version of this census named no file in a measurement's other fields or in a shell script and was corrected: 14 files came back, then 2 a kept file names across features.
   - NOT TOUCHED: every `spec.md`, `plan.md`, `tasks.md` and `measurements.json`, whose prose may still name a deleted file as history (`specs/*` keep their words; git keeps the file).
   - WHY NO PROSE IS REWRITTEN: a spec is a record of what was done, and a deleted harness's name in one is true of its time, as `docs/session-clones.md` holds for every moved path.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-09 -->
### T75 Approach (checklist part A)

1. **The goal, in the world.** What things cost is measured by Rust.
2. **The constraints.** FR-001, FR-002, FR-008; the slice and its files as the round arbiter's `ask:449-T068-scope` names them.
   **Decisions** (the round arbiter's `ask:449-T068-scope`; the second slice, figures and probes):
   - ONE LANDING: `figures.py`, `probe.py`, `ratchet.py`, `gatecost.py` and `gate_costs.py` become `l7r-gate measure` (`rust/gate/src/measure.rs`, `measure/`). `git grep -nE "(figures|probe|ratchet|gatecost|gate_costs)\.py" -- Makefile '*.mk' '*.sh' 'scripts/*.py' 'l7r/*.py' 'rust/*.rs' .claude/settings.json 'tests/*.py' 'tests/*.sh' 'specs/*.py' 'specs/*.sh'` names no invocation of them: its other lines are other features' files whose names end the same (`fr005_probe.py`, `collect_probe.py`, a scratch `probe.py` in a hook suite's corpus) and the ported modules' first comments. The Makefile's three call sites and inline `class_count` ask the gate; the guard `measure_hooks` asks it for the median it prints. `git grep -nE "(figures|probe|ratchet|gatecost|gate_costs)\.py" -- 'specs/*/measurements*.json'` names none of them as a command.
   - THE TABLE MOVES: `RATCHETS` becomes data, `dev/ratchets.json`, with every pinned baseline and its written reason verbatim; the check `run-plausible` reads the same row. A new target is a row, as it was.
   - THE CALIBRATION LOOP IS RE-PINNED, BECAUSE IT IS A DIFFERENT LOOP: the floor-net-of-load loop was Python's; in Rust the same arithmetic is about 100 times faster, so it runs 300,000,000 iterations, chosen to take the Python loop's time, and `calibration_s` is 0.116 s with its date, method and load in the table's `calibration_reason` (observed 2026-11-09, method: `l7r-gate measure ratchet --calibrate 6`, best of 3 runs). This is the loop's own constant moving with its code, not a ratchet baseline; the ceiling and the baseline the GM pinned are unchanged (`dev/ratchets.json`). The loop runs only for a `quick` at or over its ceiling, as before.
   - THE VERDICTS ARE THE PYTHON'S (observed 2026-11-09, method: each command run over the real repository through the Python and through the binary, exit status and output compared, a one-shot, the Python being gone): `gatecost` on four targets, three scopes and three classes and bare, its `--count` beside the Python's `class_count`, `gate-costs` plain and with `--since`, `ratchet` on eighteen argument shapes, `figures` on a missing spec. 63 cases, 6 differ, 3 ruled and 3 by a path. The ruled case is FR-002's `ask:449-T75-gatecost-class`: the Python's third positional reached `cwd`, so a named class left the median empty; in the Rust it is the class (2 cases, the usage line a third). The other three differ only in naming `dev/ratchets.json` for the moved baseline. `probe` and the `figures` commands that re-run measurements are held by their tests: a probe rolls 96 seeds and a full `figures` runs every recorded command, neither of which a differential should repeat.
   - THE RULING'S LIMIT: a class median over its ceiling is printed and does not refuse, tested; `make done` never reached one in Python, and the standing rule of 2026-10-26 is that timings gate nothing new.
   - WHAT THE TESTS REPLAY: every case of `test_ratchets.py`, `test_gate_costs.py`, `test_figures_deleted_engine.py`, `test_make_figures.py` and `test_probe.py` is in `measure/*/tests.rs`, the Makefile recipe cases among them.
3. **Where each comes from.** The Python tools of this slice, each compared with its port.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the ruling's slices; each stands on the ones before it.
6. **The exits.** Green: each tool's verdicts the Python's, by a differential over the repository run on the final port, and the slice's files gone. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `git ls-files` names none of the slice's files. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.


<!-- plan-archive: archived 2026-11-09 -->
### T76 Approach (checklist part A)

1. **The goal, in the world.** What things cost is measured by Rust.
2. **The constraints.** FR-001, FR-002, FR-008; the slice and its files as the round arbiter's `ask:449-T068-scope` names them.
   **Decisions** (the round arbiter's `ask:449-T76-scope`; the third slice, reduced by that ruling):
   - ONE LANDING: `runstats.py`, `guard-log.py`, `review_yield.py`, `wave_report.py`, `subagent_cache.py` and `fresh_tally.py` become `l7r-gate measure` (`rust/gate/src/measure/`). `git grep -nE "(runstats|guard-log|review_yield|wave_report|subagent_cache|fresh_tally)\.py" -- Makefile '*.mk' '*.sh' 'scripts/*.py' 'l7r/*.py' 'rust/*.rs' .claude/settings.json 'tests/*.py' 'tests/*.sh' 'specs/*.py' 'specs/*.sh' 'specs/*/measurements*.json' docs .claude/agents` names no invocation: its remaining lines are the ported modules' first comments and comments in `uncovered_marks.py`.
   - WHAT MOVES, BY THE RULING: `event_log.py`, `feature_report.py`, `turn_time.py`, `fix_yield.py`, `task_phases.py` and `where_time.py` go to phase 3 with their importers (FR-001). `tool_yield.py` goes with them, the ruling's own condition: `fix_yield.py` still imports it. The phase-2 close lists them, `tool_yield.py` the seventh, as expected remainders carrying the T065 clause. The Makefile's recipes reach those seven only from `make fix-yield`, `make tool-yield`, `make where-time` and `make feature-report`, none of them on `make done`, a plain Bash call or a plain Edit (`git grep -nE "event_log|feature_report|turn_time|fix_yield|task_phases|where_time|tool_yield|arbiter_bundle|ledger_owed|earlier_rounds|stepback_bundle" -- Makefile .claude/settings.json 'scripts/*.sh' 'rust/guard/*.rs' 'rust/gate/*.rs'`: the importers run under `make arbiter-*`, `make ledger-owed`, a check bundle and the step-back, and the guard `event_log_hooks` holds its own Rust copy of what it writes), and no deferred module writes a file a tool ported here writes.
   - THE VERDICTS ARE THE PYTHON'S (observed 2026-11-09, method: each command run over the real repository through the Python and through the binary, exit status and output compared, a one-shot, the Python being gone): `guard-log` five ways over the live log, `review-yield` two windows, `fresh-tally` two, `wave-report`, `subagent-cache` two ways, `runstats`'s phase file, its usage and its `end` with no start. 15 cases, 7 differ, all of three kinds: a usage line names the new command; `guard-log` lists firings of the same second in file order where the Python's `glob` gave the file system's; and `fresh-tally` lists causes tied on a count in name order where the Python's order came from iterating a set, which changes from run to run.
   - WHAT THE TESTS REPLAY: every case of `test_guard_log_listing.py`, `test_fresh_tally.py`, `test_subagent_cache.py` and `test_wave_report.py`, the `runstats` cases of `test_runstats.py` and the `review_yield` cases of `test_measure_reports.py` are in `measure/*/tests.rs`, but `test_subagent_cache.py`'s `shared_text` and `contract_part` cases. `git grep -nE "subagent_cache|contract_shared|contract_part|shared_text" -- 'scripts/*' 'tests/*' 'l7r/*' 'rust/*' Makefile` at the commit before the deletion, which sees an import as well as a path, finds their only caller outside `subagent_cache.py` and its own test to be `tests/tooling/test_bundle_shared_text.py`; both function bodies, `shared_text` and `contract_part` with `contract_shared` and their `_lines`, move into that test file with their use, and the file drives them as before (observed 2026-11-09, method: that grep). `test_runstats.py` keeps the cases of `tests/_gate_failures.py`, which stays Python with pytest, and of the Makefile's wiring.
3. **Where each comes from.** The Python tools of this slice, each compared with its port.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the ruling's slices; each stands on the ones before it.
6. **The exits.** Green: each tool's verdicts the Python's, by a differential over the repository run on the final port, and the slice's files gone. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `git ls-files` names none of the slice's files. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.


<!-- plan-archive: archived 2026-11-10 -->
### T069 Approach (checklist part A)

1. **The goal, in the world.** No inline Python in the gate's own path, or in the suites of the gate's scripts: `test-entry-gate`, `test-claims-gate`, `test-cohort-gate` and `test-land-tooling`.
2. **The constraints.** FR-001's second census.
   **Decisions** (the inline Python of the gate's own path):
   - THE VERBS: `l7r-gate log run` (the Makefile's `LOGRUN`), `log bypass` (`LOGBYPASS`), `log gate-bypass` (the bypass heredocs of `claims-gate.sh`, `cohort-gate.sh` and `entry-gate.sh`), `log land-tooling` and `ruff-toml` (`land-tooling.sh`), `json-field` (`review-gate.sh` and `sync-with-main.sh`), in `rust/gate/src/logs.rs`.
   - THE XDIST PROBE KEEPS ITS FORK (`ask:449-T069-xdist`): the Makefile's `python3 -c "import xdist"` chose a serial pytest when the plugin was absent; `python3 -m pip show -q pytest-xdist` asks the same question with no inline Python, and the serial arm stays. It starts Python, on the recipe line that then starts pytest, and goes with that line in phase 4; the phase-2 close names it by its own search, the census's pattern not matching `-m`. Until then it carries the T065 clause as far as the line allows: it runs only when that pytest line runs, never at Makefile parse time, on a plain Bash call or on a plain Edit, and not on a `make done` that stops at "already verified". It does run on every other `make done`, as the import probe did: `done`'s phase loop always calls `test-full`, whose recipe also starts `python3 -m l7r.diagram.ci incremental` and pytest (read from the Makefile, 2026-11-09), so the clause's last limb, a `make done` picking no Python test, cannot be held on this line until T071 and phase 4.
   - THE SUITES: `test-cohort-gate.sh`, `test-land-tooling.sh`, and `test-claims-gate.sh`'s index edit use `jq` (already installed by `setup-dev-env.sh` and already used by the hook suites), `test-entry-gate.sh`'s edit a literal shell replacement.
   - WHAT STAYS, EACH NAMED: `make audit`'s four recipes are not gate recipes and go in phase 3 (the one reading `CLASSES` in phase 4 with `check-entry-headings.py`). `buildspec/run.sh` goes with the deletion T73 waits on. `test-claims-gate.sh`'s fixture over `claims.py` and `test-entry-gate.sh`'s `answer_all` over `record_owed.py` call the modules phase 3 ports, and go with them (`ask:449-T069-suites`).
   - JSON TEXT: a record's bytes are the Python's, numbers included: `logs.rs`'s `dumps` writes `json.dumps`'s form (non-ASCII escaped as `\\uXXXX`, its separators and indent) and a float as `repr` writes it (`5e-05`, `1e+16`), each form pinned by a test. No exception.
3. **Where each comes from.** `m:inline-python-census`.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the phase's plan above; each stands on the ones before it.
6. **The exits.** Green: the census's phase-2 share holds only what **What stays** names. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** The census's phase-2 share returns only the sites named in **What stays** above (the Makefile's four `make audit` recipes, `buildspec/run.sh` until T73's removal, and the two fixtures of `ask:449-T069-suites`): `git grep -nE "python3 (-c|-[[:space:]]|-$|<<)" -- Makefile 'scripts/gates/*.sh' scripts/sync-with-main.sh scripts/land-tooling.sh buildspec/run.sh tests/hooks/test-entry-gate.sh tests/hooks/test-claims-gate.sh tests/hooks/test-cohort-gate.sh tests/hooks/test-land-tooling.sh` prints only those sites. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-10 -->
### T071 Approach (checklist part A)

1. **The goal, in the world.** The gate's first phase and its tree check are decided by Rust; what can only be read from pytest stays behind one door until pytest goes.
2. **The constraints.** FR-001, FR-002, FR-006; the Assumptions clause on a Python test driving a Rust binary.
   **Carried from T063 through T067** (`ask:T063-browser-raw`, `ask:449-T067-scope`): an area on the repository root takes the `diagram` area's exclusions, so a docstring edit in `tests/full/interactive/page_browser/*.py` is called not byte-hashed by `preflight.unseen` while the browser key moves. T071 ports it with the same verdict under FR-002 by default; any correction goes through its own case, named in the commit and the phase's record.
   **Decisions** (the round arbiter's `ask:449-T071-scope`; T071 is `preflight.py`):
   - THE PHASE AND THE TREE CHECK ARE RUST: `l7r-gate preflight` (`rust/gate/src/preflight.rs`): the derived files, the record and its pointers, the quick tier, the stray-probe refusal, the snapshot, the check, what the gate itself rolled and the gate-write guard's question. The Makefile's four calls and `gate_write_hooks.rs` call it.
   - ONE NAMED DOOR, `scripts/gates/preflight.py`, kept at its path and cut to what reads pytest: `--cover`, the changed lines' coverage, asked only by `make preflight`. `make done` passes `--no-coverage`, as the Python's `make done` already did (feature 405 T47, D25: the step's cost on every gate, and the gate's own coverage floor judges the same lines), so no `make done` starts it. It goes in phase 4 with pytest.
   - THE TWO-VERSION QUESTION IS `codeid.py`'s (FR-001's one Python library), a new verb `--same-program` beside `--debug-free-equal`: whether a `.py` file's two versions differ only where the gate does not look, asked at most once a run, in one batch, and only when a `.py` file outside the byte-hashed areas changed. So it starts Python only with a gate running and such a file changed, or on the tree check of a `make done` whose tree moved one.
   - THE CLAIMS CALL (`ask:449-T067-scope`) STAYS WHERE IT WAS: `hamlet_path`'s import of `l7r.diagram.tools.claims` is inside the door's `--cover`, reached only by `make preflight` when the coverage step found gaps, so it is Python by path until phase 3 as ruled and never runs on a `make done`.
   - THE T063 CARRIED CASE (`ask:T063-browser-raw`) IS UNCHANGED: `raw_areas` asks the stamp's `--raw-match` the same question the Python did, so a `tests/full/interactive/page_browser/*.py` docstring edit is called as before.
   - THE DOOR'S JSON: `--cover`'s answer is new, between the two halves; each line the phase prints is the Python's.
   - WHAT THE TESTS REPLAY: `test_preflight.py`'s cases of the phase and the tree are in `preflight/tests.rs`; those of the door stay in it, with a new one for `--cover` and one for `--same-program`.
   - THE VERDICTS ARE THE PYTHON'S (observed 2026-11-10, method: the tree snapshot, the tree check against both tools' snapshots, the guard's `--would-write` on eleven kinds of path each unchanged, changed and deleted, a docstring edit, a code edit, a moved tree and an unreadable HEAD, through the last commit's Python and the binary on the real repository, exit status and output compared, a one-shot: 43 cases, 0 differences).
3. **Where each comes from.** the baseline under `<git dir>/gate-baseline/`; coverage.py's data as it stands.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** Leaf first by what imports what (`ask:449-T062-order`), each stands on the ones before it; callers reach the binary once a process or in a batch, never one spawn a file (FR-006, SC-002).
6. **The exits.** Green: every phase and tree case gives the Python's verdict, and `preflight.py` is cut to the door. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** The differential over the real repository (the tree snapshot, the tree check and the guard's question) shows no mismatch, and `scripts/gates/preflight.py` holds only `--cover` and what it calls. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-10 -->
### T73 Approach (checklist part A)

1. **The goal, in the world.** Nothing in the repository runs a test on AWS, and a gated push lands on a green local `make done`: the GM, 2026-11-09, "Let's delete rather than port our tooling which runs our tests remotely on AWS."
2. **The constraints.** FR-001, as amended for the deletion; FR-002 for what stays: the route (DIRECT or GATED) and a gated push's conditions, which were the remote-off path's. The remote has been off since 2026-09-05 (`dev/switches.json`), so the behavior of a push does not change.
   **Decisions** (FR-001a, the GM 2026-11-09):
   - WHAT GOES, IN ONE LANDING: `buildspec/`, `Dockerfile.ci`, `dev/ci.md`, `requirements-ci.in`, `requirements-ci.txt`, and under `rust/gate/src/ci/` the modules `aws`, `cachepolicy`, `decision`, `dispatch`, `door`, `imagecheck`, `main`, `runlog` and `real_tree` with their tests; the make targets `ci-off`, `ci-on`, `ci-check`, `ci-merge`, `ci-measure`, `ci-image` and `commit-permitted`, the `REMOTE_OK` macro, `audit`'s remote spend and the `bypass-audit` branch for a build; the `remote` axis of `dev/switches.json`; the aws CLI's install, `boto3` and `CODEBUILD_BUILD_ID`'s branches. The tracked files themselves are deleted by the GM's own command, because a built-in safety check refused the session's and said only a person may approve it; the task's done line holds until that has run and the Rust modules were out of the build before it.
   - WHAT STAYS, ON THE PATH IT ALREADY TOOK (FR-002): the remote has been off since 2026-09-05, so a gated push has been the old LOCAL-GATED path. `l7r-gate ci status --route` gives DIRECT or GATED; `l7r-gate ci gated-check` (`rust/gate/src/ci/gated.rs`, `make gated-check`) gives what `ci-merge` gave with the remote off: the merge conflict first, then feature-complete, green-local-since-edit and a green local `make done` on the engine content the merge lands, every condition printed even after one fails, a push only when all hold. `sync-with-main.sh` then does the locked pull and push it did on SKIP-VERIFIED. Four differences follow from the deletion and hold no verdict: the route word `GATED-LOCAL` is now `GATED`; the `remote-enabled`, `route-is-gated` and `breaker-not-tripped` rows, and the `.git/ci-verdict` file, are gone, because each answered a question about the remote or about a caller that now asks only on GATED; the refusal names `merged-engine-green` where it named `remote-enabled`; and `make ci-status` keeps its name, because a guard's corpus and every refusal name it, but it is local.
   - WHAT THE TESTS REPLAY: `gated/tests.rs` holds the route, the three conditions' refusals and the merge conflict, and `switches/tests.rs` and `config/tests.rs` keep their cases on the axes that remain. `test-sync-with-main.sh`'s gated cases are the local path: a pass lands, a refusal keeps the work, an unknown route word refuses, and the cohort's and port switch's cases run on the GATED route. NOT REPLAYED, each because the behavior is deleted: the dispatch sequence, the AWS adapter, the parked build, the mailbox, the verified-record lookup, the run log's remote entries and spend, the image check, the bucket lifecycle and the tests of the `CODEBUILD_BUILD_ID` branches.
   - THE CENSUS: `git grep -nE "ci-(check|merge|measure|image|on|off)\b|buildspec|Dockerfile\.ci" -- 'specs/*/measurements*.json'` returns two lines, a recorded census row and a recorded T064 comparison, neither a command `make figures` runs against the files deleted here (observed 2026-11-09, method: that grep, each row read).
3. **Where each comes from.** `rust/gate/src/ci/`, `buildspec/`, `Dockerfile.ci`, `scripts/sync-with-main.sh`.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** The push's use first (a local route and gated check), then the targets, the Rust, the files, the docs, all in one landing.
6. **The exits.** Green: a gated push still refuses without a green local `make done` on the merged engine content, and the census below is empty. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `git ls-files buildspec Dockerfile.ci dev/ci.md` returns nothing; `git grep -nE "ci-(check|merge|measure|image|on|off)\b|CodeBuild|buildspecOverride" -- Makefile 'scripts/*.sh' 'scripts/*.py' 'rust/*.rs' 'l7r/*.py'` names no invocation; `make hooks-test HOOKS_ALL=1` green with `test-sync-with-main`'s gated cases on the local path.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.


<!-- plan-archive: T74 to T74 moved to plan-done.md, 2026-11-09 (feature 375 FR-044) -->

<!-- plan-archive: T75 to T75 moved to plan-done.md, 2026-11-09 (feature 375 FR-044) -->
<!-- plan-archive: T76 to T76 moved to plan-done.md, 2026-11-09 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-10 -->
### T77 Approach (checklist part A)

1. **The goal, in the world.** What things cost is measured by Rust.
2. **The constraints.** FR-001, FR-002, FR-008; the slice and its files as the round arbiter's `ask:449-T068-scope` names them.
   **Decisions** (the round arbiter's `ask:449-T77-scope` and `ask:449-T77-replays`; the last slice):
   - ONE LANDING: `maps_moved.py`, `work_budget_rust.py`, `popup_rounds.py`, `push_check_times.py` and `model_trial.py` become `l7r-gate measure maps-moved | work-budget | popup-rounds | push-check-times | model-trial` (`rust/gate/src/measure/`). `git grep -nE "(maps_moved|work_budget_rust|popup_rounds|push_check_times|model_trial)\.py" -- Makefile '*.mk' '*.sh' 'scripts/*.py' 'l7r/*.py' .claude/settings.json 'specs/*.py' 'specs/*.sh' 'specs/*/measurements*.json'` names no invocation once the Makefile and the three figure files are rewritten, and `docs/spec-kit-and-reviews.md`'s `model_trial.py` step and `rust/phases/src/driver/CLAUDE.md`'s pointer are rewritten with them; a bare-name import search (`(import|from) +(maps_moved|work_budget_rust|popup_rounds|push_check_times|model_trial)`, `spec_from_file_location`, `sys.path`) finds only `tests/tooling/test_maps_moved.py` and `tests/tooling/test_model_trial.py`, which go with them.
   - THE DELETION WAITS ON THE GM (as T73's does): the built-in safety check refused the removal of the five tools and those two tests, observed 2026-11-09, and leaves it to a person, so this task stays open until the GM runs it. The ports land first; no recipe, hook or figure runs the Python meanwhile, and the two tests that import those tools stay, and pass, until the same removal.
   - WHAT MOVES, BY THE RULINGS: `replay_owing.py` and `depiction_replay.py` import `modal_owed`, `modal_triage` and `claims`, which stay Python until phase 3, so they go to phase 3 with them; the other deferred tools are in FR-001 and T070's row.
   - THE FOLD (`ask:449-T77-replays`, FR-003): `model_trial.py`'s `usage` read `agent_census.fold_usage`; `model_trial.rs` holds a Rust `fold_usage` and `agent_census.py`'s phase-3 port calls that one. No piece runs both.
   - THE VERDICTS ARE THE PYTHON'S (observed 2026-11-09, method: each command run over the real repository through the Python and through the binary, exit status and output compared, a one-shot): `maps-moved` three ways, `popup-rounds` on the clone by name, with `--json` and with a zoned `--since`, its usage and its `--record` over the tracked snapshots (byte for byte, and equal to the tracked file), `model-trial catalog` three ways, 15 cases and 0 differences; `model-trial usage` on 40 real transcripts picked by a seeded shuffle, 0 differences, the fold's differential the ruling asks; `prepare` on a real run through both, its prompt, recorded reply, meta and output and its agent files identical; `make work-budget`'s table identical.
   - DELIBERATE DIFFERENCES: `run` starts each session in its own process group, not its own session: the only difference is the controlling terminal, which a backgrounded `claude -p` does not use, and the standard library offers no safe way to start a session. A bad `--since` to `popup-rounds` exits 1 with empty stdout, as the Python's uncaught `ValueError` does, with one line on stderr naming the value where the Python printed a traceback (`ask:449-T77-bad-since`). WHICH values parse stays the Python's, and the local-time conversion with them (observed 2026-11-09, method: 13,876 generated `--since` forms, every date, separator, time and zone form the parser takes and the malformed ones around them, through `datetime.fromisoformat(...).timestamp()` and the binary, a one-shot: the Python accepts 2,677, the epoch equal on each; on the other 11,199 both exit 1 with empty stdout; 0 differences). `run-all`'s progress times read the local zone, as the Python's did.
   - `push_check_times` (FR-002 ruled case, `ask:449-T77-scope`): the Python's table listed commands of a shell line T067 removed, so the same-output test cannot hold. The Rust rows are the Rust push's own `CHECKS` table plus the one-process run, so a row the push adds is timed. Its proof is the re-run figure `m:push-checks-rust`.
   - WHAT THE TESTS REPLAY: every case of `test_maps_moved.py` and `test_model_trial.py` is in `measure/*/tests.rs`.
3. **Where each comes from.** The Python tools of this slice, each compared with its port.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the ruling's slices; each stands on the ones before it.
6. **The exits.** Green: each tool's verdicts the Python's, by a differential over the repository run on the final port, and the slice's files gone. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `git ls-files` names none of the slice's files. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-10 -->
### T78 Approach (checklist part A)

1. **The goal, in the world.** A change to this repository no longer waits on the Python unit tests, the planner that selected them, the coverage floor over Python or the static checks whose only subject is Python source.
2. **The constraints.** FR-001b, FR-002 for every tool that stays, the guards' suites under `tests/hooks/`.
   **Decisions** (the GM's words, FR-001b):
   - WHAT STAYS UNDER `tests/`, by subject, what outlives the Python: `test_mode_a_sheets.py` (the sweep of the hand-drawn sheets), `test_agent_models.py`, `test_agent_sync.py`, `test_claude_md_quotes.py`, `test_one_root_claude_md.py`, `tooling/test_docs_match_the_mechanism.py`, `test_citation_rule_inventory.py`, `test_task_research_boxes.py`, `test_settlement_review_contract.py`, `test_operations_registry.py`; what those and pytest load: `conftest.py`, `__init__.py`, `_scope.py`, `_gate_failures.py`, `_heap.py`, `_sheets.py`; and everything that is not Python (`tests/hooks/`, `tests/fixtures/`). Of the live-pool search's matches, read by hand (observed 2026-11-10, method: every `test_*` function naming the pool by path, `ast`-walked over the tracked tests: 70 functions in 32 files), only `test_mode_a_sheets.py` sweeps the live maps; the rest exercise Python code on fixtures.
   - THE PLANNER AND THE FLOOR GO WITH THE TESTS (`ask:449-T071-scope` placed them in the commit that removes pytest; the GM's approval moves that here): `l7r/diagram/ci/selection.py`, `gate_plugin.py`, `incremental.py`, `pool_readers.py`, `gate_config.py`'s two readers, `scripts/gates/pool-readers.py`, `cover_changed.py`, `refresh_baseline.py`, and `scripts/gates/preflight.py`, whose only remaining half was `--cover`, with no tests to run. The kept suite runs whole, with no selection and no coverage.
   - PYTHON-ONLY STATIC CHECKS GO: `check-function-cap.py`, `check-duplicate-defs.py`, `ruff format`, `pyrefly`, and `check stale-dirs`. The `.py` arm of `check file-scale`'s line bar goes, as the list told to the GM named it; its `.rs` bar and its per-directory file count stay, their subject not being Python. `ruff check` stays, narrowed to outright errors (`E9`, `F63`, `F7`, `F82`), the only automatic check left on the Python still being edited as ports land.
   - THE OLD TESTS STAY READABLE: the commit before the removal is tagged `python-tests-before-removal`; a port reads the cases it used to replay from there. New Rust code still owes 100% line coverage from its own tests (`rust cover`, FR-004).
   - THE COST, told to the GM before the approval: a regression in Python that is still running and being edited before its port is caught only by the kept checks, the guards' suites, the differentials of its port, or use. Priced against keeping the tests: observed 2026-11-10, method: the last green `make done` record, pytest 135 s of 212 s, beside static checks that bound the saving at roughly 0 to 50 s on the last four green runs before static speeds up.
3. **Where each comes from.** The GM's words in FR-001b; the census above.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves, and the sweep of the hand-drawn sheets stays.
5. **The order.** Tag; delete the tests and the Python-only tooling in one commit with the Makefile, `land.py`, the guards and the crates edited to stop reading them.
6. **The exits.** Green: `make done`, `make quick`, `make land` and `make hooks-test` run with only the kept tests. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `git ls-files 'tests/*.py'` holds only the kept files; no recipe names the deleted tools; `make done` green and its time recorded against `m:done-rust-edit`.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-10 -->
### T070 Approach (checklist part A)

1. **The goal, in the world.** Phase 2 closed on its measured outcome.
2. **The constraints.** SC-002, FR-010.
   **Decisions** (the close of phase 2; `ask:449-T071-scope`, FR-001b):
   - SC-002 AS MEASURED: `m:done-rust-edit-phase2`, 22.0 s against the 15.1 s owed: not met, recorded with its shares in `dev/phase-2-close.md`, the line unmoved and re-measured at the phase-3 close. The round arbiter's `ask:449-T071-scope` (`arbiter.jsonl`) rules this case: "phase 2 closes without a new ask: dev/ records the figure and the shares, states SC-002 NOT MET at phase 2 by that named share ... and leaves SC-002's line unmoved; it is re-measured at the phase-3 close". The planner it named is gone (FR-001b), so the shares are the kept pytest's two runs, the preflight's Python tools and the seeds.
   - AN UNCHANGED TREE RUNS NO TEST: the preflight stands aside on a verified tree, so `make done`'s "already verified" path starts no test (SC-002's second half), `m:done-unchanged-after`.
   - THE TIME FLOOR: a `make done` reuses each crate's unchanged checks, so it is judged at the incremental floor, 5 s (`ABSOLUTE_MIN` in `run_plausible.rs`, a setting), in place of the floor of 10% of the pinned ratchet baseline (40 s, a setting of `dev/ratchets.json`): `m:done-rust-edit-phase2` did every check its delta owed in 22.0 s of wall time, and the old floor refused such a run.
   - FR-008'S ONE END-TO-END TEST: `test_rust_tooling.py` was deleted by FR-001b; FR-008's test against the real command is `rustc/tests.rs`'s `the_real_cargo_tests_a_real_crate`, the real cargo over the fixture crate.
   - THE CENSUSES: the `.py` census's phase-2 share is `git ls-files 'scripts/gates/*.py' 'scripts/measure/*.py' 'l7r/diagram/ci/*' l7r/diagram/switches.py scripts/hooks/lib/hm_conflict.py` (observed 2026-11-10, one-shot): it lists only files `dev/phase-2-close.md` names with their phase, and neither of the last two exists. The second census returns the four `make audit` recipes and the two fixtures of `ask:449-T069-suites`. The `ask:449-T069-xdist` probe is gone with the planner's recipe: `git grep -c 'pip show' -- Makefile` printed 'nothing' (observed 2026-11-10, one-shot).
3. **Where each comes from.** `m:done-rust-edit`.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the phase's plan above; each stands on the ones before it.
6. **The exits.** Green: the figures re-run and recorded beside their first values, SC-002's result stated (met, or not met by its named shares as `ask:449-T071-scope` rules), and the censuses' phase-2 share holding only the expected remainders named in `dev/phase-2-close.md`. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** SC-002's measurement and both censuses, recorded in `dev/`. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** No constant's value moves; the Time Floor decision changes which existing floor applies to `make done`.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: archived 2026-11-10 -->
### T79 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T79 Approach (checklist part A)

1. **The goal, in the world.** The phase-3 tools no Python still imports are Rust, each giving the Python's output.
2. **The constraints.** FR-001, FR-002, FR-003, FR-001b; `ask:449-T77-replays` (one Rust fold).
   **Decisions** (T79 is the phase-3 tools no Python still imports):
   - WHAT IS HERE: `canon.py`, `money_conversions.py`, `found.py`, `stale_terms.py`, `money_candidates.py`, `fragment_move.py` and `agent_census.py` become `l7r-gate record` verbs (`rust/gate/src/record/`), with `rust/gate/src/difflib.rs` the one port of `SequenceMatcher` (autojunk off).
   - WHAT MOVES TO ITS CALLER, the T76 shape, so one implementation runs (FR-003), by the search `git grep -lE "^\s*(import|from) +<name>\b"` over `scripts/`, `l7r/`, `tests/` (observed 2026-11-10, one-shot): `ledger_lint`, `review_cost`, `moves` and `brief_load` to T81 with `hm_checks`, `ledger_owed`, `modal_owed`, `review_owed` and `page_session_runner`; `pager` to T82 with `claims`; `task_phases`, `turn_time`, `tool_yield`, `work_budget_view` and `work_budget_bundle` to T83 with `feature_report`, `stepback_bundle`, `fix_yield`, `land.py` and `speckit-todo.py`. `size_table.py` and `open_questions.py` import the engine's Mode A code and `CLASSES` and go in phase 4 (`ask:449-T79-moves`). `agent_sync.py` stays with its kept test, `test_agent_sync.py`, and goes in T83 with that test's Rust port. THE SEARCH (closed by `ask:449-T79-moves`, observed 2026-11-10, one-shots): an `ast` walk of every tracked `.py` (341 files: `ast.Import` and `ast.ImportFrom`, the last dotted part and each imported name) finds no importer of the seven tools; a word-bounded `git grep` of the seven names over the Makefile, `.sh` files and `rust/`, read by hand, finds the ordinary word "found" and the JSON key `canon`. `specs/251-tiered-subagent-checks/measure/seeded.py` and `run_seeded.sh` are deleted, not ported (`ask:449-T79-moves`, the GM's 2026-11-09 rule): a whole-tree `git grep` of `seeded.py` and `run_seeded` finds only `docs/spec-kit-and-reviews.md:109` as a live direction, historic text under `specs/251`, `255`, `256`, `294`, `383` and `449`, and `specs/256`'s `dispatch_seeded.sh` header; and `seeded.py`'s by-path load names `scripts/_agent_census.py`, which no tracked file is, so it cannot run today. `size_table.py` and `open_questions.py` carry the T065 clause until phase 4 and the phase-3 close names them.
   - THE VERDICTS ARE THE PYTHON'S (observed 2026-11-10, method: each command through the Python and the binary on the real repository, exit and output compared, a one-shot): `canon`, `money-conversions` and `found` 12 cases, `stale-terms` 13 over the eight newest specs, `money-candidates` 5 over the record's 1,439 amounts, `stale-dirs` 8 (kept review-round snapshots against their feature directories and two git-history pairs, against the Python functions the guard called), 0 differences; `fragment-move` 12 on real moves of 41, 21 and 7 files in scratch copies, `agent-census` 11, whose one difference is the `command` lines `--record` writes, which name the verb. HTML entities are CPython's whole table and its numeric rules (`record/html5_entities.tsv`, generated from `html.entities.html5`), so `html.unescape`'s answers hold for any fragment.
   - THE GUARD: `review_round_hooks` asks `l7r-gate record stale-dirs` in place of its inline Python.
   - THE PYTHON STAYS UNTIL THE GM APPROVES ITS REMOVAL: the safety check reserves that to a person (the request is in the session); no recipe, hook or figure runs these files meanwhile.
3. **Where each comes from.** The Python tools of this slice, each compared with its port.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** Before T80 to T83, whose tools import these or are imported by them.
6. **The exits.** Green: each verb's differential below shows no mismatch, the recipes and the guard run only the verbs. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differentials below; `git grep -nE "\b(<the seven>)\.py\b" -- Makefile '*.mk' '*.sh' .claude/settings.json 'specs/*/measurements*.json' 'rust/*.rs'` names no invocation (observed 2026-11-10, one-shot: its lines are one list of paths in `research_pointers.rs` and comments), the commands in `specs/251`'s measurements rewritten to the verb, every figure's command so rewritten in the porting commit (FR-001). `docs/spec-kit-and-reviews.md:109` is rewritten in the removal commit to name `scripts/gates/l7r-gate.sh measure model-trial` in place of `seeded.py`, so no document directs the deleted file.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-10 -->
### T80 (the first slice of the archive, `ask:449-T80-order`)

- **Approach**: the three tools ported with the decisions below.

   **Decisions** (the first slice, `ask:449-T80-order`: `access_tags`, `downloads`, `check-partial-citations`):
   - WHAT IS HERE: `l7r-gate record access-tags`, `l7r-gate record downloads`, `l7r-gate check partial-citations` (`rust/gate/src/record/`, `rust/gate/src/checks/`), the push's and the Makefile's rows and recipes moved to the verbs. `partial-citations` keeps its delta gate, only the files it reads named anew.
   - THE CALLERS (an `ast` walk of every tracked `.py` for imports, and `importlib`/by-path strings, 2026-11-10, one-shot): `archive_ops.py` (`resolve_matches`) and `uncited.py` (`retire_cited`) import `access_tags`; both reach the Rust through its command, `access-tags entry-keys` and `access-tags set`, so one implementation decides. `check_bundle.py` and `memo_check.py`'s dynamic imports name neither module.
   - NO PYTHON FOR THE LOCK: `downloads add` used `reserve-prefix.py` for `mirror_of` and `Lock` alone, and neither has a verb a subprocess could use; both are ported in-process, the lock through `flock(1)` on the same `<mirror>/.specify/download-ids.lock` (T014's decision, `File::try_lock` being past this toolchain), so the Python and Rust callers still exclude each other. `ingest` runs `archive_ops.py inbox` by path, as the Python did, until step 3.
   - THE DATE IS THE PYTHON'S: `date.today()` is the local date; `today` asks `date(1)`, not the UTC clock.
   - THE VERDICTS ARE THE PYTHON'S (observed 2026-11-10, method: each command through the Python and the binary on the real repository and two scratch clones, exit, stdout, stderr and every written file compared, a one-shot): 249 comparisons, 0 differences. Argparse usage text (exit 2) and a Python traceback's text are not compared. Argparse's usage text and a traceback's text are not compared: not outputs FR-002 binds (`ask:449-usage-text`).

### T80 Approach (checklist part A)

1. **The goal, in the world.** The access tags, the download list and the partial-citation check are decided by Rust.
2. **The constraints.** FR-001, FR-002, FR-003; the round arbiter's `ask:449-T80-order`.
3. **Where each comes from.** The Python tools of this slice, each compared with its port.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** Before T81, as `ask:449-T80-order` orders the archive.
6. **The exits.** Green: the differential in the decisions shows no mismatch, and the recipes, the push and the callers named run only the verbs. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The decisions' differential; `git grep -nE "(access_tags|downloads|check-partial-citations)\.py" -- Makefile '*.mk' '*.sh' .claude/settings.json 'specs/*/measurements*.json' 'rust/*.rs'` names no invocation.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-10 -->
### T81 (the first record leaves, `ask:449-T81-slices`)

- **Approach**: three leaves ported with the decisions below; everything else the old T81 named is T85-T89.

   **Decisions** (`ask:449-T81-slices`):
   - `hm_record.py` becomes `l7r-gate record edit-route` and `record fragments`; `hm_house.py` becomes `record americanize`, reaching the guard's own correction; `moves.py` becomes `record moved-only`, reaching `checks/moves.rs`. One implementation of each.
   - Python callers reach them through `scripts/record_door.py`, one process a run (FR-006): `review_owed` asks every new folder at once, `entry_owed` every hit, `apply_edits` and `claims_reply` every text, `check_bundle` from memory.
   - The old Python files are removed with T84's approval, not here.
   - `edit-route` compared on the real tree, Python `main()` against the verb, exit, stdout and stderr, a traceback's text not bound (`ask:449-usage-text`): 566 payloads, every rule of the router and malformed input among them, 0 differ (observed 2026-11-10, method: a one-shot harness sampling fragment text from the questions, the registry and the glossary with a fixed seed). `scripts/record_door.py` goes with its last Python caller (`ask:449-T81-hm-record`).
   - Differential, both on the real tree: `moved-only` 15 cases, 0 differ; `fragments` 204 payloads and 2,356 listings, 0 differ; `americanize` 5,114 paragraphs and 495 seeded, 0 differ after the fix for `\s` on U+001C-U+001F around a dash (observed 2026-11-10, method: each Python against its verb, exit, stdout and stderr compared). A whole-file `americanize` run was killed unfinished and compared nothing, so the paragraph run is the evidence.

### T81 Approach (checklist part A)

1. **The goal, in the world.** What a record edit routes to, a question's fragments, the house spelling and the moved-only check are decided by Rust.
2. **The constraints.** FR-001, FR-002, FR-003, FR-006; `ask:449-T81-slices`.
3. **Where each comes from.** The Python tools of this slice, each compared with its port.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** First of the old T81's slices; T85 follows.
6. **The exits.** Green: the decisions' differential shows no mismatch and `make land` is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The decisions' differential; `git grep -nE "(hm_record|hm_house|moves)\.py" -- Makefile '*.mk' '*.sh'` names no invocation.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-10 -->
### T86 (the arbiter and checks state, `ask:449-T86-door`)

- **Approach**: the five modules and three guards ported as one cut, with T011, T043 and T048, on the ruled door.

   **Decisions** (`ask:449-T86-door`, FR-001, FR-002, FR-003, FR-006):
   - The core is `l7r_guard::shared::checks`; the guards `check-bundle`, `checks` and `record-edit` call it directly, and `l7r-gate arbiter`, `checks-close` and `checks-door` are the commands. No guard starts Python on a plain Bash call or a plain Edit.
   - Writers found outside the five, by `git grep -nE 'checks-open\.json|arbiter-owed\.json|modal-batches\.json|arbiter\.jsonl|arbiter-[a-z]+\.json|gm-rulings|arbiter_owed|checks-open' -- '*.py' '*.sh' 'Makefile' '*.mk' '*.rs'`, `specs/` included: `record_owed.py`'s `keep_batches` writes `modal-batches.json` and moves to a door verb; `rust/gate/src/state.rs`'s `second_red_gate` writes `arbiter-owed.json` and moves to the shared lock and atomic rename. A search by name cannot see a path taken from the `state_path` verb, so its callers were read as well: `arbiter_bundle.py`, `modal_bundle.py`, `earlier_rounds.py` and `check_bundle.py` only read it, their writes going to a bundle's own directory. Under `specs/` no Python or shell file names any of those files or the `state_path` verb, and two features' `measurements.json` name `checks-open.json` only as the source a figure was read from (374 and 375, three entries; their commands are `make feature-report` and `measure popup-rounds`, which read it) (observed 2026-11-10, method: the search above over `specs/**/*.py`, `specs/**/*.sh` and `specs/*/*measurements*.json`, and each hit read). So one implementation writes.
   - `scripts/checks_door.py` is one process a run, reopened if the environment it reads changes mid-run, because `land.py` exports `SPECIFY_FEATURE`. It holds no logic. The door's verbs beyond the ruling's list, each a read or write the callers already made: `rulings`, `_round_no`, `PAGE_CHECKS`, `notes_of_manifest`, `subjects_of_manifest`, `fix_hold`, `keep_batches`.
   - `l7r-gate arbiter` still runs Python by path on rare branches that are later tasks' ports and the T065 clause: `record_owed.answer`, `gm_review.question`, `checkpoint.close_checkpoint`, `review_prereq.py content-key`, `claims.py accept`. None writes `checks-open.json` or an arbiter file directly: an `ast` import closure from each, listing every file naming a state file and every write on those lines, found none, the writes reaching the state through door verbs only (observed 2026-11-10, method: `t86-closure.py` in the session's scratchpad). It reads line by line and cannot see a by-path run outside the import graph.
   - Differential against the Python at commit 9c77004cf, on the real tree with writes on scratch copies, exit, stdout and stderr compared: door reads 9,265, door after an environment change 6, door writes 21 (`trip` 10, `record_answer` 7, `keep_batches` 4, covering what `checks_door/tests.rs`, `arbiter/tests.rs`, `rounds/tests.rs` and the Rust hook suites hold; no kept Python test uses those verbs), guards `check-bundle` 30, `checks` 16, `record-edit` 17, arbiter commands 92, `check-closed` 5, the accept seam's failure path 2 and its success path 1, on sparse clones where the engine imports, the store record, `arbiter-owed.json`, `checks-open.json` and the new `arbiter.jsonl` row compared too; 9,455 in all, 0 differ (observed 2026-11-10, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t86-diff.py`). It found one difference, fixed: a failed `trip` through the door returned false where the Python raised; the door now answers an error and the guards keep the quiet false. No lock is held across the seam: `record_ruling` calls `accept_answers` with none held and `pop_owed` takes the owed lock afterwards. Three normalizations: the merged hook reply is compared as parsed JSON, the hook protocol's order being its keys'; a library's error text inside `refused - ...` is not compared; and where the Python's stderr holds a traceback, only the traceback itself is unbound (`ask:449-usage-text`): what either side wrote before the `Traceback (most recent call last):` line is compared, with exit status and stdout. One case of the 9,455 reached that, with no text before its traceback (observed 2026-11-10, method: the same harness, re-run with that comparison and a count).
   - Reads that open the state files themselves today stand, Rust keeping the files' shape: `gm_review`, `set-down`, `budget_change`, `claims_carry`, `fix_yield`, `tool_yield`, `popup_rounds.rs`, `plan/record.rs`.
   - The Rust keeps the Python's hand-written words, including refusal tags naming the old file, as the earlier guard ports did (FR-002).
   - The five `.py` files, the three guards' `.sh` and the dangling link `tests/hooks/record-edit-gate.sh`, which nothing runs (`git grep -n record-edit-gate` names only its own suite, which needs no such link, and `make hooks-test HOOKS_ALL=1` is green without it), are deleted in the cut (the GM's standing approval of 2026-11-10; `ask:449-T86-door`).

### T86 Approach (checklist part A)

1. **The goal, in the world.** The state of the record checks and the arbiter is decided and written by Rust alone.
2. **The constraints.** FR-001, FR-002, FR-003, FR-006; `ask:449-hm-checks-route`, `ask:449-T86-door`.
3. **Where each comes from.** The Python compared with its port.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** After T81; T87-T89 and T83 then port their callers off the door.
6. **The exits.** Green: the differential above shows no difference, the census no import of the five, and `make land` is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential; `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t86-census.py` walks all of `git ls-files '*.py'`, `specs/` included, with `ast`, searches shell and Makefile, and reads `specs/*/measurements*.json`'s commands: no import, by-path load or run of the five (observed 2026-11-10: 324 Python files, 84 under `specs/`; two comment lines in suites); `.claude/settings.json` names no removed guard.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-10 -->
### T011 Approach (checklist part A)

1. **The goal, in the world.** `record-edit-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
3. **Where each comes from.** `tests/hooks/test-record-edit-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-record-edit-hooks.sh` green against `l7r-guard --only record-edit-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-record-edit-hooks.sh` passes against the Rust guard; `scripts/hooks/record-edit-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T012 to T012 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T013 to T013 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T014 to T014 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T015 to T015 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T016 to T016 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T017 to T017 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T018 to T018 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T019 to T019 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T020 to T020 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T021 to T021 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T022 to T022 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T023 to T023 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T024 to T024 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T025 to T025 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T026 to T026 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T027 to T027 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T028 to T028 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T029 to T029 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-10 -->
### T043 Approach (checklist part A)

1. **The goal, in the world.** `check-bundle-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
3. **Where each comes from.** `tests/hooks/test-check-bundle-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-check-bundle-hooks.sh` green against `l7r-guard --only check-bundle-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-check-bundle-hooks.sh` passes against the Rust guard; `scripts/hooks/check-bundle-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T044 to T044 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T045 to T045 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-10 -->
### T048 Approach (checklist part A)

1. **The goal, in the world.** `checks-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
3. **Where each comes from.** `tests/hooks/test-checks-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-checks-hooks.sh` green against `l7r-guard --only checks-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-checks-hooks.sh` passes against the Rust guard; `scripts/hooks/checks-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

<!-- plan-archive: T006 to T049 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T050 to T052 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T052 to T052 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-10 -->
### T84 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T84 Approach (checklist part A)

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

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: archived 2026-11-11 -->
### T87 (the owed core, `ask:449-T87-entry-owed`)

- **Approach**: `record_owed`, `record_units`, `modal_owed`, `translation_owed` and `modal_triage` ported as one cut, with `pull-queue.sh`'s jq merge as a verb; `entry_owed.py` moved to phase 4 by the ruling.

   **Decisions** (`ask:449-T87-entry-owed`, FR-001, FR-002, FR-003, FR-006):
   - The Rust is `rust/gate/src/record/{owed,owed/answers,units,modals,translation,triage,merge_answers,repo,args}.rs`, reached as `l7r-gate record record-owed|record-units|modal-owed|translation-owed|modal-triage|merge-answers`; the Makefile recipes and `scripts/gates/entry-gate.sh` run the binary, and `rust/gate/src/arbiter.rs` calls the answer function directly instead of running `record_owed.py`.
   - Python callers reach the port through one door, `scripts/owed_door.py` (namespaces `ro`, `ru`, `mo`, `mt`, as the callers named the modules), one process a run, no logic: `bundle_owed`, `check_bundle` (its in-process `translation_owed` now runs as the command `make translation-owed` runs), `claims`, `claims_triage`, `modal_bundle`, `apply_edits`, `arbiter_bundle`, `depiction_replay`, `replay_owing` (its snippets on the current tree; `_OLD_MODALS` still imports the historic `modal_owed` from a worktree at an old commit, which is that commit's file, not this one), `entry_owed` and `tests/hooks/test-entry-gate.sh`. The door is deleted with its last caller and named at the phase-3 close if present.
   - `fingerprint` and `quotation_key` are door verbs keyed on root, rev and sources, the working tree uncached; `apply_edits` takes both from one call. No caller mutates or holds a `Record` (the census below reads every attribute taken from the five).
   - `entry_owed.py`, under the T065 clause: the Rust starts it only when the entry-drift family is asked for and the base has commits, and then when a file it reads changed against the base, untracked files included, or the engine is missing. The files it reads were measured two ways over a real run on a worktree whose question page 0059, named by 19 classes' `Entry:`, was edited (observed 2026-11-10, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/entry_reads.py`, Python's `sys.addaudithook` `open` and `subprocess.Popen` events, and `bash /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/inotify_run.sh`, `inotifywait -m -r -e open` over the whole worktree, which also sees the door's Rust processes). The audit hook saw it open only files under `l7r/diagram/interactive/`, `l7r/diagram/__init__.py`, the edited question page and the four scripts it loads, and start only git, `owed-door` and `record fragments`. The watch saw those processes open as well the question pages, the write-ups under `research/sources/`, `research/*.json` and `research/to-download.*`, and the gate's own sources and wrapper, which build the binary answering its doors, and nothing else under the tree. So `ENTRY_READS` in `owed.rs` is `l7r/diagram/interactive/`, `l7r/diagram/__init__.py`, `research/`, `entry_owed.py`, `record_cache.py`, `record_door.py`, `owed_door.py`, `scripts/gates/l7r-gate.sh` and `rust/gate/`, every file the watch saw opened lying within it. A change that broke what it reads fails as the Python's did, and a change holding none of those files does not start it, as the clause says; only then is an engine failing to import not seen. A test pins each case: a registry edit, an untracked file in the closure, a record data file, and a file it never reads. It reaches `read_page`, `kinds_in` and `modal_file` through the door.
   - `quote_verbatim` and `style_prepass` are started as one `python3 -c` a run, only for notes files whose parse is not already in `translation-pairs.json`. `apply_edits.reply_of` is not the T86 door's `_reply_of` (it unescapes and reads a transcript differently), so it goes by command. `kinds_in` is built on `pylex.rs`'s lexer (`pylex::kinds`, grouping parentheses unwrapped, checked against `ast`), not a second reader.
   - `.git/record-checks/*.json` has one writer: `record merge-answers` replaces the jq merge and `cp` at `pull-queue.sh`, its output JSON-equal to jq's, key collisions included, written by atomic rename; the store's other writes are `owed/answers.rs`.
   - Caching, decided on the Rust's own measurement (`ask:449-T81-slices`). The Rust keeps parses by their text in memory for one process and reads the translation cache once a run. Without that cache a fresh `record-owed` took 7.5 s and with it 2.6 s (observed 2026-11-10, method: the port agent's timing of `record record-owed` on the real tree, before and after the cache). A disk cache would carry the warm parse to a fresh process: through the door, one process asking each family twice, the record family took 0.89 s cold and 0.28 s warm, translation 0.45 s, entry-drift 0.17 s and modal 0.18 s both times (observed 2026-11-10, method: `time.time()` around `ro.units(root, families=(f,))` through `scripts/owed_door.py`, each family twice in one process). So a disk cache could save at most the record family's cold-to-warm gap a call. No hook runs it on a tool call: its callers are `make record-owed`, the push's `entry-gate.sh` and the bundle builders, a few calls a landing (observed 2026-11-10, method: `git grep` for `record-owed` and `ro.units` over `rust/guard`, `scripts/hooks`, `scripts/gates`, the Makefile and `.claude/settings.json`). That gap is under the bar a disk cache's invalidation would cost to keep right, so none is ported, and `record_cache.py`'s is not. Beside the Python, on this clone's tree at d43e55542, `record_owed.py` took 1.85 to 1.89 s with its disk cache warm and `record record-owed` 2.69 to 3.46 s, their outputs byte-identical (observed 2026-11-10, method: `/usr/bin/time`, three runs each, after a warm build); of a shimmed run's time, git took 1.17 s over 49 calls and Python 0.32 s over two (observed 2026-11-10, method: PATH shims timing each `git` and `python3` call). A profiler could not be run in this container (`perf_event_paranoid` 4 on a read-only `/proc/sys`, and no `ptrace`).
   - Cases changed: the arbiter's Rust tests take a test double in place of a fake `record_owed.py`, and the message they expect reads "record-owed said" for "python3 said".
   - The Rust keeps the Python's hand-written words (FR-002); argparse's generated usage text and traceback text are unbound (`ask:449-usage-text`).
   - Differential against the Python at 7efe2ab04, the Rust at d43e55542, on two shared side clones, exit, stdout, stderr and written state compared: commands 26, usage errors 11 (every argparse-generated one), answers 23, the entry-drift seam 7 (success through a stub included), `merge-answers` against jq 12, the door 8 cases making about 5,800 verb calls over every verb, write verbs with state compared; 87 in all, 0 differ (observed 2026-11-10, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/harness/diff.py`). Two cases reached a traceback (one answers, one seam). Normalizations: paths; `utc` and bypass-log file names; the caches (`translation-pairs.json`, `l7r-cache/`) not compared; traceback text and argparse usage text (`ask:449-usage-text`); the bypass-log `commit`, the two sides sitting on different HEADs; a slug with no colon has no `subject` on either side.
   - `record_cache.py`, which the task line had deleted here, stays: `scripts/gates/memo_check.py`, `scripts/record/claims.py` and `scripts/record/entry_owed.py` still import it (observed 2026-11-10, method: `git grep -n record_cache -- ':!specs'`); it goes with the last of them.
   - The five `.py` files are deleted in the cut (the GM's standing approval of 2026-11-10). The docs naming their paths now name the Rust: `dev/modals.md` and the three modal agent files generated from it, `docs/research-doctrine.md`, `scripts/CLAUDE.md`, and comments in `entry-gate.sh`, `pull-queue.sh` and `bundle_owed.py`. `specs/375-enforced-wave-process/measurements.json`'s `375-a3-record-tooling-before` command named `record_owed.py`: it is rewritten to `make record-owed` (FR-001; its other commands are later tasks' ports), and re-run, the re-run kept beside the 2026-10-11 figure as its own dated field, since that figure was a baseline at 374's HEAD whose base cannot be rebuilt (2.66, 2.79 and 2.79 s, observed 2026-11-10, method: `date +%s.%N` around `make record-owed`, three runs, on this clone at 82cacf0b2).

### T87 Approach (checklist part A)

1. **The goal, in the world.** What the record checks owe, and what they answered, is decided by Rust alone.
2. **The constraints.** FR-001, FR-002, FR-003, FR-006; `ask:449-T81-slices`, `ask:449-T86-door`, `ask:449-T87-entry-owed`, `ask:449-usage-text`.
3. **Where each comes from.** The Python compared with its port.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** After T86; `entry_owed` and the archive cluster follow in phase 4 (T85).
6. **The exits.** Green: the differential above shows no difference, the census no import or run of the five, and `make land` is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential; `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/census.py` walks all of `git ls-files '*.py'`, `specs/` included, with `ast`, and at d43e55542 finds the five imported only by each other; `git grep` over shell, Makefile, `*.mk`, Rust, JSON, TOML and `.claude/settings.json` finds no run of them by path outside the Rust's own provenance comments, a Rust test's fixture files and recorded history under `specs/` (observed 2026-11-10, both run by the session at that commit). `make rust-test` (gate 684 after the review's fixes, observed 2026-11-10; guard 499 as the port agent ran it), `make static` with the new Rust at 100% line coverage, `make test-full` and `make hooks-test HOOKS_ALL=1` green, seen run by the port agent; the hook suites' first run failed only `l7r-guard.sh`'s two `--version` cases on a cold 54.9 s build, and the rerun with the build warm was green (observed 2026-11-10, method: `make hooks-test HOOKS_ALL=1`, run twice by the port agent).
10. **Before moving a constant.** None moved; `rust/gate/src/push/tests.rs` reads the Rust's constants.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-11 -->
### T88 (the bundles, `ask:449-T88-bundles`)

- **Approach**: `bundle_owed`, `check_bundle`, `modal_bundle`, `earlier_rounds`, `arbiter_bundle` and `depiction_replay` ported as one cut; what they reach of unported Python goes through one runner, `scripts/bundle_door.py`, by the ruling.

   **Decisions** (`ask:449-T88-bundles`, `ask:449-T77-replays`, FR-001, FR-002, FR-003, FR-006, `ask:449-usage-text`):
   - The Rust is `rust/gate/src/record/bundle.rs` and `record/bundle/{check,parts,keys,owed,modal,depiction,earlier,door}.rs`, `rust/gate/src/arbiter/bundle.rs` and `arbiter/bundle/{marks,sections,reviews}.rs`, and `rust/gate/src/measure/depiction_replay.rs`, reached as `l7r-gate record check-bundle`, `record modal-bundle` (its `--prepass` too), `arbiter bundle` (its `--check-ask` too) and `measure depiction-replay`; the Makefile's `notes`, `check-bundle`, `modal-bundle`, `modal-prepass`, `arbiter-bundle` and `arbiter-ask` recipes run the binary. `args.rs` gains positionals and `nargs="*"` lists, as argparse reads them.
   - The runner, `scripts/bundle_door.py`, is started on a run's first verb and never before, one process a run, one JSON line each way; each verb calls one existing Python function: `run` (the in-process helpers `record_prepass`, `quote_verbatim`, `style_prepass`, `source_pages`, as `check_bundle._run_in_process` ran them, feature 383 D6 kept in one process, FR-006), `passages`, `save_cached` (`residue_pages`' save, `CachedPages` and its cache-only fetcher kept in Python - `source_pages.save` with `sources.CachedPages`, the fetcher being `check_bundle`'s `NotCached` stub, a constant answer, moved into `bundle_door.py` and gone with that verb in T85; the URLs it is handed are picked in Rust, as `residue_pages` picked them), `claims_rows` and `load_index` (`arbiter_bundle.claims_section`'s, to Rust in T82), `knobs` and `knob_table` (modal-depiction bundles only, phase 4's). Its replies have a descriptor of their own (fd 1 is pointed at stderr), so nothing a helper prints can reach the channel - the one bound: anything `save_cached`, `passages`, `claims_rows` or the knobs printed, which reached the bundle command's stdout in process, now reaches its stderr, and none printed on the differential's real data; a helper's argparse names its program `check_bundle.py`, as it did in process. A verb's failure is the traceback the Python raised, printed after what the run printed, exit 1.
   - `modal_bundle.glyph_crop` stays a by-command Playwright start (`python3 -c` of the Python's own script, kept as the tracked `scripts/record/glyph_crop.py`, which `depiction.rs` embeds with `include_str!`, so the first FR-001 census, over `git ls-files '*.py'`, counts it; the second searches the Makefile and shell and cannot see a Rust `python3 -c`, so it is named at the phase-3 close as an expected remainder, and T85 removes it before the feature closes), only on `make modal-bundle FOR=modal-depiction` with a pool page drawing the kind, under the T065 clause; it moves onto the CDP crate in T85.
   - `apply_edits` reaches `modal_bundle.research_held` and `sources` reaches `check_bundle.url_of` through `scripts/owed_door.py` (`mb.research_held`, `cb.url_of`), the same Rust functions the bundles call. `translation-owed`, which `check_bundle` ran as a process since T87, is called in the bundle's own process. `verdict_of` and the event log's path are the guard crate's (`event_log_hooks`, the log path now public there, one implementation); `feature_report.reversals` is ported into `arbiter/bundle/sections.rs`, for T83 to take; `bundle_owed.reason_ok` calls the guard's escape rule (`shared::escape::enough`) in place of `hm_escape.py`'s, the rule the guards already apply.
   - No start of the runner or the crop is conditional on a changed file, and none is reached by a guard, a plain Edit or `make done` (observed 2026-11-10, method: `git grep` for the four make targets and the binary's verbs over `rust/guard`, `scripts/hooks`, `scripts/gates`, `tests/hooks` and the Makefile's `done` and `quick` recipes), so no read set is measured for them.
   - A defect of the Python fixed, the one case changed, a ruled FR-002 case (`ask:449-T88-check-order-escape`, the round arbiter, 2026-11-11): `modal_bundle.bundle` rebound `held` (to the research-held wording) and `first` (to the last candidate's first words) before writing `check-order-escape:`, so a modal-research bundle let through by CHECK_ORDER_OK recorded a page's first words as the reason, and a form bundle with research-held wording wrote the line when nothing held it; the port writes the reason given, only where the order held the bundle. No reader parses the line (observed 2026-11-10, method: `git grep check-order-escape`).
   - A defect of T87's door fixed: `owed_door.Modal` copied the JSON's `entry_files` and `drawing_files` lists into the instance under the methods' names, so every `m.entry_files()` raised TypeError and `make modal-bundle` and `make modal-prepass` failed on every modal since T87 landed (observed 2026-11-10, method: the differential's first modal case, the Python's traceback); fixed in the door, which the Python side of the differential runs (N7).
   - `check_bundle.refresh`, which no caller runs (observed 2026-11-10, method: `git grep "refresh("` over `scripts/`), is not ported: no Python calls it and nothing runs it by name (observed 2026-11-11, method: `git grep -n -w refresh` over the Makefile, `*.sh`, `*.mk` and `.claude/settings.json`, every hit another tool's, and the old `check_bundle.py` naming it only at its own `def`).
   - The MANIFEST text `check_bundle_hooks.rs` and `owed/answers.rs` parse is the Python's, byte for byte (the differential compares every bundle file); its origin column still names `scripts/record/modal_bundle.py` for the prepass, the candidates and the no-crop note, as the Python wrote it.
   - Coverage: the bundles' tests run on the testkit's scratch record with a stub runner and a stub crop (`cfg(test)`), and a default OUT goes under the test's temp directory. The new Rust has 100% of its lines reached and is `clippy::pedantic` clean (observed 2026-11-11, method: the port agent's `make static`, its cover run clean on all three crates).
   - Differential against the Python at 00a123467, the Rust at 39dfd7fbe (its modal group re-run at 008c60641 with the pool's generated pages copied in, so the crop runs on both sides), on two scratch clones of the real tree, exit, stdout, stderr and every file a run writes compared (the bundle directories, the sources-consulted ledger's new lines, the record `--record` writes): check-bundle 48 cases, modal-bundle 36, arbiter-bundle 40, depiction-replay 6 and the doors 5 (every runner verb against its Python function on three questions, `research_held` over 78 pop-ups and `url_of` over every write-up), 135 in all, 2 differing, both the `check-order-escape:` fix above (one case, its bundle carried into the next case's compared state), 0 reaching a traceback and 7 an argparse usage error (observed 2026-11-10 and 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t88/diff.py`). Normalizations: N1 paths; N2 a ledger line's stamps; N3 `glyph.png` by its presence, its kinds compared in `glyph.txt`; N4 traceback text; N5 argparse's generated usage text (`ask:449-usage-text`); N6 the replay's `until`, each side's own commit; N7 the door's Modal fix on the Python side.
   - The census at the cut: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t88/census.py` finds the six imported only by each other, `apply_edits` and `sources` now through the door, and the Rust reaching Python only through the runner's seven verbs (`run`, `passages`, `save_cached`, `claims_rows`, `load_index`, `knobs`, `knob_table`; `bundle_door.py`'s `VERBS`) and the crop (observed 2026-11-10, method: that script over `git ls-files '*.py'`, `specs/` included, and `git grep` for `ask("`, `helper("` and `Command::new("python3")` over the new Rust).
   - The docs naming the six now name the Rust: `docs/guards.md`, `docs/research-doctrine.md`'s citation-rule inventory (its test green), `docs/research-record-rules.md`, `dev/rust-tooling.md`, `scripts/CLAUDE.md`, `rust/gate/CLAUDE.md` and `archive.py`'s comment. The three recorded commands that named a ported file (found by `git grep -nE '(bundle_owed|check_bundle|modal_bundle|earlier_rounds|arbiter_bundle|depiction_replay)(\.py)?' -- 'specs/*/measurements*.json'` and each hit read: `375-a3-record-tooling-before` and `375-a6-about-only-replay` in feature 375's, `design-fixes` in this feature's) are rewritten to the port and re-run, each re-run kept beside its old figure as its own dated field: `375-a6-about-only-replay` runs `scripts/gates/l7r-gate.sh measure depiction-replay`, and its re-run finds the 2026-10-12 figures exactly, 221 edits, 213 owed under amendment 1, 170 under amendment 6 and 43 About-only (observed 2026-11-11, method: the rewritten command without `--record`). `375-a3-record-tooling-before` runs `make check-bundle` and `make modal-bundle`, re-run at 2.31, 2.37 and 2.35 s for Q=0190 with no quotes and 7.58, 7.67 and 7.69 s for the notice-board's depiction bundle, its crop's browser included (observed 2026-11-11, method: `date +%s.%N` around each make, three runs, on this clone's own delta, NOT_OWED_OK and CHECK_ORDER_OK given). 449's `design-fixes` runs `make check-bundle Q=0086 FOR=record-format`, re-run at 2.18, 2.12 and 2.16 s (observed 2026-11-11, method: as for 375-a3). On one tree the Python and the Rust took 4.04, 2.19 and 2.21 s against 4.01, 2.10 and 2.07 s for Q=0086, 2.44, 2.39 and 2.41 s against 2.29, 2.36 and 2.35 s for Q=0190, 7.81, 7.77 and 7.65 s against 7.58, 7.53 and 7.57 s for the depiction bundle and 3.21, 3.20 and 3.21 s against 2.70, 2.67 and 2.69 s for the replay (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t88/timing.py`, `time.perf_counter` around each process, three runs each, on the differential's two scratch clones).

### T88 Approach (checklist part A)

1. **The goal, in the world.** A check's bundle, a pop-up's bundle and the round arbiter's bundle are built by Rust.
2. **The constraints.** FR-001, FR-002, FR-003, FR-006; `ask:449-T88-bundles`, `ask:449-T77-replays`, `ask:449-T81-slices`, `ask:449-usage-text`.
3. **Where each comes from.** The Python compared with its port.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** After T87; T82 takes `claims_section`'s verbs off the runner, T83 `reversals` and the event log, T85 the helpers, `passages`, `save_cached` and the crop.
6. **The exits.** Green: the differential above shows no difference but the named fix, the census no import of the six outside themselves, and `make land` is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential and the census above; `make rust-test` (gate 742, guard 500), `make static` with the new Rust at 100% line coverage and `clippy::pedantic` clean, `make hooks-test HOOKS_ALL=1` (53 suites) and the citation-rule inventory's test green, seen run by the port agent (observed 2026-11-11, method: those make targets).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-11 -->
### T89 (the reviews, `ask:449-T89-reviews`)

- **Approach**: `review_owed`, `review_prereq` and `checkpoint` ported with `scripts/hooks/lib/hm_approval.py` (its `_state_at` the guard's `feature_approval_hooks::at_rev`, reused); `stepback_bundle` moved to T83 and reaches the port through one door until then, by the ruling. T89 amends the spec (`ask:449-T89-reviews`), so it is not straight under FR-001c and keeps its review.

   **Decisions** (`ask:449-T89-reviews`, `ask:449-T81-slices`, `ask:449-T051-lib-route`, FR-001, FR-002, FR-003, FR-006, `ask:449-usage-text`):
   - The Rust is `rust/gate/src/reviews.rs` and `reviews/{owed,owed/declared,glyph,prereq,checkpoint,door}.rs`, reached as `l7r-gate reviews owed`, `reviews prereq <command>`, `reviews checkpoint <verb>` and `reviews-door`; the Makefile's `verify`, `step-back`, `step-back-off`, `step-back-on`, `review-accept`, `review-paired-gate` and `review-verdict` recipes and `review-gate.sh` run the binary. The round arbiter's checkpoint close and a unit's content key (`arbiter.rs`) are in-process calls, no longer a `python3 -c` and a by-path `review_prereq.py`.
   - The pair guard asks the port BY COMMAND (`l7r-gate reviews ...` from its tree, as it already asked `l7r-gate plan decided`), not in-process: the gate crate depends on the guard crate, not the reverse, and the port needs the gate's `checks::moves::moved_only`, the bundle runner and the record's git helpers. One implementation either way. The guard's `python` interpreter field went with its last use, and its `!script.is_file()` early returns (the glyph hour and the prerequisites, for a clone without the Python) went with the scripts: no suite case ran without them, the suite copying the real `scripts/` tree. The suite's two SC-004 trace greps now look for `reviews owed`.
   - The doors: `scripts/reviews_door.py` (`l7r-gate reviews-door`) holds exactly the three verbs the ruling names for `stepback_bundle.py`, `gitdir`, `git` and `checkpoint_state`, and leaves with T83. `tick-task.py`'s `checkpoint.hold` and `review_snapshot.py`'s `owed(landing=True)` and its Unit fields reach the port through two verbs on T86's `checks_door.py`, `review_hold` and `review_owed` (its units as attribute objects with the fields the snapshot reads), since they outlive T83; both carry the T065 clause and are named at the phase-3 close. `pool_map_names`, which the ruling listed for `review_snapshot.py`, is read by no Python caller left (`review_prereq named` was its one reader, now Rust), so it has no verb.
   - `gencache.is_current` is one verb on `scripts/bundle_door.py`, started from the `--clone`'s own `scripts/` (so a fixture clone's stub cache answers, as the Python imported the clone's) and only when `reviews prereq check` asks about a map with a generator; it leaves with `l7r/diagram/pipeline/` in T90.
   - `speckit-todo.py --state DIR` is asked by command once a run (cached per directory), run from `/` so no tool-usage row is written: the Python asked it in-process and recorded nothing, and the row is the landing's holding check's. `record_cache.RevReader` is not ported: the base's pool trees are one `ls-tree` and one `cat-file --batch` of the files asked, and the new folders' tracked files one `git ls-files` for the run (the Python ran one a folder).
   - The figure pattern is asked of `l7r-gate check spec-lint --figure-pattern` by command, as the Python asked it, Python's `\w` read as `\w\p{N}`: the first build read it in-process, and the differential named the spec-lint usage row the Python's command wrote on every `check` case; dropping that row would be an output change needing its own FR-002 case, so the command is kept.
   - The state files keep one writer each: `glyph-clock.json` (`owed`'s batch and reopening, `checkpoint`'s open and close), `glyph-landing` (also unlinked by `sync-with-main.sh`, the same act as `--landing-mark off`), `review-verdicts/`, `review-dispositions/`, `checkpoint-admitted` and `dev/step-back.json`, each in the shape the Python wrote (`json.dumps(indent=1)`, Python's float form).
   - No start of Python is conditional on a changed file: `speckit-todo.py` runs when a feature is named, `bundle_door.py` when `prereq check` asks, so no read set is measured. `specs/240-verified-before-reviewed/measure/fr005_probe.py` is deleted unported under the ruling; its seven `measurements.json` entries keep their values, their commands retired in `make figures`' own form for a figure not re-run: `ask:449-T79-moves` retired no `measurements.json` entry and left no convention to copy (`git log -S seeded.py -- specs/251-tiered-subagent-checks/measurements.json` finds no commit), and `rust/gate/src/measure/figures.rs`' `refused` lists a command holding a `<placeholder>` as not re-measured and never runs it, so each command now reads `<retired: the FR-005 probe, deleted unported by feature 449 T89 (ask:449-T89-reviews) - the value is history, not re-run>`, which `make figures` does not run and `m:recorded-python-commands`' pattern, needing `python3` before a `.py`, does not count.
   - Coverage: the reviews' tests run on scratch repositories with the tools the port asks by command stubbed (`speckit-todo.py`, the gate wrapper, the finished-run probe, the bundle runner, the engine key); `misaligned` takes the exported feature as an argument so no test sets the environment. `owed.rs` is split into `owed/declared.rs` under the file-scale bar. The new Rust has 100% of its lines reached and is `clippy::pedantic` clean (observed 2026-11-11, method: `make static`, its cover run clean on all three crates).
   - Differential: the Python against the Rust (the Python scripts at b696c0fcc, the binary built at 3e2a43bc3) on two scratch clones of the real tree under a `.clones/` directory beside a copy of the real pool (so main's mirror copy is read), each case set up identically on both, exit, stdout, stderr and every file a run writes compared: `reviews owed` 99 cases, `reviews checkpoint` 33 and `reviews prereq` 46, 178 in all, 0 differing, 3 reaching a traceback (stderr compared before it) and 10 an argparse usage error (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t89/diff.py`). Every seam's success path ran in it: `speckit-todo.py --state` on this feature's real history (the reopening walk through `at_rev`), `is_current` through `bundle_door.py` into the real generation cache, the figure pattern's command, the gate stamp and the finished-run probe. The doors and the repointed callers: each door verb against the Python function it replaces (`gitdir`, `gitdir` with no repository, `git`, a refused `git`, `checkpoint_state`, `review_hold`, `review_owed`) on six setups, 42 comparisons, 0 differing (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t89/diff2.py`), and `review_snapshot.py` (4 cases), `stepback_bundle.py` (3) and `tick-task.py`'s hold (3) before (b696c0fcc) and after (3e2a43bc3), 10 cases, 1 differing only in the step-back's `time.md` minutes, which run to each run's own clock (N7), and 0 on the run before at 21602d025 (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t89/diff2.py`). Normalizations: N1 the copy's path; N2 an epoch time inside the run's window and today's UTC stamps (a batch's, a mark's, the switch's `utc`, a trigger's); N3 the not-due refusal's `in <n> s`; N4 Python's bytecode caches unwritten (`PYTHONDONTWRITEBYTECODE=1`); N5 traceback text; N6 argparse's generated usage text (`ask:449-usage-text`); N7 the step-back window's end, each run's own clock; N8 the copies' `rust/` removed so their wrapper runs the one binary. The Python and the Rust took 66.2 s against 53.1 s over the owed cases, 16.9 s against 14.7 s over the checkpoint's and 22.8 s against 19.7 s over the prerequisites' (observed 2026-11-11, method: the harness's `time.time` around each process, the wrapper's start included).
   - The census at the cut: an `ast` walk of `git ls-files '*.py'`, `specs/` included, finds the four and `hm_approval.py` imported by nothing but `fix_yield.py`'s `stepback_bundle` (T83's, ruled), and named only in docstrings; `git grep` over the Makefile, `*.mk`, `*.sh`, the Rust, `.claude/settings.json` and the agent files finds no run of them, only the Rust's provenance comments; the Rust reaches Python only through `speckit-todo.py --state` and the runner's `is_current` (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t89/census.py` and that search). No `specs/*/measurements*.json` command names the four (observed 2026-11-11, method: `git grep` of their names there, every hit the seven `fr005_probe.py` sources).

### T89 Approach (checklist part A)

1. **The goal, in the world.** What a delta owes the review checks, a dispatch's prerequisites, the verdict record and the hourly checkpoint are decided by Rust.
2. **The constraints.** FR-001, FR-002, FR-003, FR-006; `ask:449-T89-reviews`, `ask:449-T81-slices`, `ask:449-T051-lib-route`, `ask:449-usage-text`.
3. **Where each comes from.** The Python compared with its port.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** After T88; T83 takes `stepback_bundle.py` and `reviews_door.py`, T90 the `is_current` verb.
6. **The exits.** Green: the differential shows no difference, the census no import of the four outside the doors, and `make land` is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential and the census above; `make rust-test` (gate 782, guard 500), `make static` with the new Rust at 100% line coverage and `clippy::pedantic` clean, `make hooks-test HOOKS_ALL=1` (53 suites green) and the citation-rule inventory's test (2 passed), seen run by the port agent (observed 2026-11-11, method: those make targets).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-11 -->
### T82 (the claims, `ask:449-T82-claims`)

- **Approach**: `scripts/record/claims.py` and its satellites (`claims_{accept,carry,cli,context,counters,flight,labels,owed,reply,scope,stale,triage}.py`), `tunables.py`, `pager.py` and `l7r/diagram/tools/claims_rust.py`, with the grammar, the section reader and `doc_units` of `l7r/diagram/tools/claims.py`, ported to `l7r-gate claims`, `l7r-gate tunables` and `l7r-gate claims-door`; the `.py` half (a `.py` unit's fingerprint is CPython's `ast.dump`) stays Python behind verbs of `scripts/bundle_door.py`, by the ruling. T82 amends the spec (`ask:449-T82-claims`), so it is not straight under FR-001c and keeps its review.

   **Decisions** (`ask:449-T82-claims`, `ask:449-T88-bundles`, `ask:449-T069-suites`, `ask:449-T062-py-id`, FR-001, FR-002, FR-003, FR-006, `ask:449-usage-text`):
   - The Rust is `rust/gate/src/claims.rs` and `claims/{grammar,units,scope,index,reply,triage,bundle,report,carry,commands,flight,labels,seam,tunables,pager,door}.rs`, reached as `l7r-gate claims [--root DIR] <command>` (the Makefile's thirteen `claims-*` recipes and `scripts/gates/claims-gate.sh`), `l7r-gate tunables` (`make tunables`) and `l7r-gate claims-door` (`scripts/claims_door.py`). The round arbiter's accept (`arbiter.rs`) and the plan's triage hint (`plan.rs`) call the port in process, no longer `python3 scripts/record/claims.py` by path; the arbiter bundle's claims section reads the rows and the index in Rust, so `bundle_door.py`'s `claims_rows` and `load_index` are gone, and the arbiter bundle's functions that only handed the runner on to it lost that argument.
   - The `.py` half: `tools/claims.py` gains `py_units` (the Python half of `all_units`, lifted out, `all_units` calling it, so the Python's own output is unchanged) and `unit_json`; the runner's new verbs each call one existing Python function and print JSON, never a syntax tree: `claims_py_units`, `claims_module_units` (`claims_triage.section_words`' `.py` history), `claims_context_source` (`context_source`'s Python branch, moved to `claims_context.py_source`), `claims_callees`, `claims_direct`, `claims_chase`, `claims_counter_only` (`claims_counters.counter_only_json`, the unit rebuilt as the reader holds it), `claims_stale`, `claims_scope_units`, `claims_read_units`, `tunables_unstated`, and the one write verb `gm_review_add_row` (`gm_review.add_row`: `claims_carry`'s `gm-review.jsonl` append and `ensure_box` together, Python their one writer until T91 ports `scripts/gm_review.py`). Each leaves the runner with the Python it reads (phase 4) or with T91.
   - When Python starts: `claims_py_units` only when its answer, kept under the clone's common git directory (`l7r-cache/claims-py-units.json`, at most four answers, written by atomic rename), is keyed differently - the key is the reader's code (`tools/claims.py`, `bundle_door.py`), the flags, and every `.py` under `l7r/diagram/` by path and bytes, and a tree with none asks nothing. The read set behind the key: a real run of the verb on the clone opened 117 files of the repository, every one a `.py` under `l7r/diagram/` (or its bytecode), `tools/claims.py` or `bundle_door.py`, none outside the key, and the directory listings of the walk, whose file list the key holds (observed 2026-11-11, method: `sys.addaudithook` and `inotifywait -m -r -e open` over `l7r/` and `scripts/` around the same run, `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t82/readset.py`). A run that asks the runner took 1.2 s and one that reads the kept answer 0.13 s for `claims triage-owed` on the clone (observed 2026-11-11, method: a timed build of the port printing the read's wall time, two runs). `claims_stale` only when the delta since the merge base changes a `.py` under `l7r/` (the Python parsed on every `make claims-owed`); `claims_counter_only` only for a `.py` unit owed a code triage with a merge base (a `.rs` unit is answered false without asking: the Python's `ast.parse` of Rust source fails and it returned false, and a section is line-keyed, refused before any parse); the context verbs only on a bundle of a `.py` unit or a `--with` `.py` reference; `claims_module_units` only on a claimed dictionary's section triage; the scope verbs only through the door from `land.py`; `tunables_unstated` only on `--inline` over the map code's `.py` files; `gm_review_add_row` only on recording a known drift. `claims-checked` and `claims-triaged` read a reply through `apply_edits.reply_of` by command (T87's seam). `touches_engine` asks `codeid.py` by path for the `.py` engine files the delta changes (`ask:449-T062-py-id`), as the Python did.
   - Python that stays Python reaches the port through `scripts/claims_door.py` (`current`, `owed`, `load_index`, `load_store`, `backfill_sections`, `scope_split`, `git_diff`, `file_left`, `flight_live`, and the four constants by a verb): `land.py` (its by-path runs of `claims.py` now `l7r-gate.sh claims`; `claims_scope` and `claims_flight` through the door), `replay_owing.py` (its inline claims code uses the door where the scripts tree has one and an older commit's own `claims.py` otherwise) and `impl_check.py`. No caller hands back a mutated object: `backfill_sections` returns new copies, which `replay_owing` writes.
   - `tests/hooks/test-claims-gate.sh`'s fixture over `claims.py` (`ask:449-T069-suites`) now records its verdicts as a check's reply is recorded: `l7r-gate claims bundle --owed`, then `record` of an IN-STEP line per key, a case of its own.
   - The Python's failures on a malformed record are kept: a merge base's index or a `gm-review.jsonl` row that is no object, a flight mark's `at` that `float` cannot read, a live row with no verdict at the report's or the gate's reading (`v["verdict"]`) each fail the command, exit 1, as the Python's traceback did; a value printed is `str()` of it (`py_str`).
   - The report goes through the pager on a terminal it overflows (`LINES`, then `stty size`, then 24; `$PAGER` else `less -FRSX`; `NO_PAGER`), as `pager.py` did; a pipe gets it whole. The base tree is written to `base.tar` and extracted with `tar`, as `tarfile` did; temporary directories are named per process and call, so the crate's parallel tests do not share one.
   - Coverage: the tests run on a scratch repository (`claims/tests.rs`' fixture) with a stub runner answering from files the test writes, a stub `apply_edits` and a stub `codeid.py`; a test of the archive's failure takes the git program as an argument. The new Rust has 100% of its lines reached and is `clippy::pedantic` clean (observed 2026-11-11, method: `make static`, its cover run clean on all three crates, and `make rust-test CRATE=rust/gate`, 842 tests).
   - Differential: the Python at d6fcc51a8 against the Rust at 3f0e5cca3, each case set up identically twice at one path on a sparse copy of the real tree (`l7r/`, `rust/`, `docs/`, the questions, `specs/`, the claims records, origin/main set to effd80cb6), exit, stdout, stderr and every file a run writes compared (the index, the snapshots, the bundles, the triage skips, the carry record, `tasks.md`, `gm-review.jsonl`, `found.jsonl`, the flight marks, the kept page blobs): 40 cases, 110 runs - the real tree's every command, five edit scenarios (a constant, a counter block, a unit's body, a page, a section; blocks removed), the claims switch at `clean` with a known drift and a carry, a moved unit, the backfills, a stale figure, no origin, the gate suite's fixture tree, every usage refusal - 0 differing, 8 reaching a traceback (stderr compared before it) and 12 an argparse usage error (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t82/diff.py`). The doors and the callers: each `claims_door.py` verb against the Python function it replaces on the real tree and on the edits, `impl_check.report` over four research-record features, `land._in_flight` and `replay_owing`'s inline claims code (owed and migrate, three trees) before and after, 32 comparisons, 0 differing (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t82/diff2.py`). The Python took 187.6 s and the Rust 124.4 s over the 110 runs, each from a cold copy (observed 2026-11-11, method: the harness's `time.time` around each process); warm on the clone, best of six alternated, `claims owed` 0.34 s against 0.21 s, `report` 0.26 s against 0.12 s, `triage-owed` 0.27 s against 0.11 s and `gate` 1.33 s against 0.52 s (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t82/timing.py`). No case differed, so no FR-002 change is made; the normalizations: N1 a flight mark's `at`, N2 a UTC stamp, N3 stderr from `Traceback (most recent call last):` on, N4 argparse's generated usage text (`ask:449-usage-text`; exit 2 and empty stdout held), N5 Python's bytecode caches unwritten, N6 the Python's `coverage` imports the reader of the tree it reads (`engine(root)`), so the hand-made fixture tree is given one. N7: `--help`, which argparse answers with its help and exit 0, the port refuses with exit 2 - unbound by `ask:449-usage-text`, no kept suite holding it, and not a case the differential ran. A defect of the Python kept, not fixed, for a ruling if one is wanted: a live index row with no verdict (a claim the index never held, named by a triage) makes the report's and the gate's reading raise `KeyError` (`open_findings`, `classify`), at `clean` the gate failing outright; the port fails the same way. The kept answers' key does not hold the interpreter's version, so an upgrade that changed `ast.dump` would be read from the kept answer until a `.py` file changed, the gap the Python's pickled parses had.
   - The census at the cut: an `ast` walk of the 313 files `git ls-files '*.py'` lists, `specs/` included, finds the ported files imported or loaded only by `scripts/bundle_door.py`'s verbs (`claims_context`, `claims_counters`, `claims_stale`, `claims_scope`, `tunables`, `tools.claims`), named elsewhere only in docstrings, with `replay_owing`'s inline code importing an older commit's own `claims.py` (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t82/census.py`). `git grep` over the Makefile, `*.mk`, `*.sh`, the Rust, `.claude/settings.json` and the agent files finds no run of them but the Rust's provenance comments, and the Rust reaches Python only through the runner's twelve claims verbs, `apply_edits.reply_of` and `codeid.py` by command (observed 2026-11-11, method: that search and `git grep` for `ask("` over `rust/gate/src/claims`).
   - The docs repointed: `docs/guards.md` (the claims gate's row and the counter clear), `dev/rust-tooling.md`, `l7r/diagram/tools/CLAUDE.md`, `scripts/CLAUDE.md`, `rust/gate/CLAUDE.md`; `docs/research-doctrine.md`'s citation-rule inventory names no T82 file (its test green, observed 2026-11-11, method: `make test-file FILE=tests/test_citation_rule_inventory.py`, 2 passed); no agent file or `dev/modals.md` names one.
   - Recorded measurements: no `specs/*/measurements*.json` command runs or names a T82 file; four name a claims make target or `claims-gate.sh` in prose or shell (`375-a3-record-tooling-after`, `375-a8-claims-cold`, `375-a8-claims-after`, `claims-gate-push` of feature 383), and none is rewritten (observed 2026-11-11, method: `python3 /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t82/mcensus.py`).
   - Expected for deletion after review (the GM's standing approval of 2026-11-10): `scripts/record/claims.py`, `claims_accept.py`, `claims_carry.py`, `claims_cli.py`, `claims_flight.py`, `claims_labels.py`, `claims_owed.py`, `claims_reply.py`, `claims_triage.py`, `pager.py` and `l7r/diagram/tools/claims_rust.py`, deleted in the cut. Staying, by the ruling: `l7r/diagram/tools/claims.py` (the `.py` half; its grammar, section reader and `doc_units` still serve its own `module_units` until phase 4), `claims_context.py`, `claims_counters.py`, `claims_stale.py`, `claims_scope.py` and `tunables.py` (their syntax-tree halves behind the runner's verbs; `tunables.py`'s list and `claims_scope.py`'s `split`/`file_left` are Rust and their Python copies go with the files in phase 4), each named at the phase-3 close as an expected remainder carrying the T065 clause, with `scripts/claims_door.py` and `scripts/gm_review.py` (T91). The removal of `claims_rust.py` takes with it what only the deleted Python reached: `tools/claims.py`'s `all_units` (its one importer), `coverage` and `PROCEDURES`, and `tunables.py`'s `.rs` branch (`inline`, `RUST_NUMBER`, `unstated_rust`, `render_inline`) and `main`, which the Rust `make tunables` replaced and which imported the deleted `claims.py`; `Memo` and `_NoMemo` stay, `py_units` taking them. `dev/rust-tooling.md`'s research-claims row drops its `claims_rust.py` key; its placement-stages row stays, the file's "Proven on the fixture" table naming it and its key a test name rather than a path, so no check reads it as a missing file. The runner's verbs reach none of the removed names (observed 2026-11-11, method: `grep` of `scripts/bundle_door.py` for each, and an import of both files), and `make rust-tooling` is green.

### T82 Approach (checklist part A)

1. **The goal, in the world.** What the research claims owe, their bundles, triage, report, push verdict and carry are decided by Rust; only a `.py` unit's syntax tree is read by Python.
2. **The constraints.** FR-001, FR-002, FR-003, FR-006; `ask:449-T82-claims`, `ask:449-T88-bundles`, `ask:449-T069-suites`, `ask:449-T062-py-id`, `ask:449-usage-text`.
3. **Where each comes from.** The Python compared with its port.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** After T89; T83 takes `land.py` and `replay_owing.py` off the door, T91 `gm_review.py` off the runner, phase 4 the `.py` half.
6. **The exits.** Green: the differential shows no difference, the census no import of a ported file outside the doors, and `make land` is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential and the census above; `make rust-test CRATE=rust/gate` (842 passed), `make static` with the new Rust at 100% line coverage and `clippy::pedantic` clean, `make hooks-test HOOKS_ALL=1` (53 suites green) and the citation-rule inventory's test (2 passed), seen run by the port agent (observed 2026-11-11, method: those make targets).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: archived 2026-11-11 -->
### T92 (the gate crate split, the GM 2026-11-11, `request.md` "the Rust iteration loop", FR-011)

- **Approach**: the gate crate (74,199 lines, one crate) is split into fifteen crates under `rust/gate/crates/<dir>` (packages `l7r_gate_<dir>`) and the binary `l7r_gate` at `rust/gate`, which only dispatches. T92 is not a port: no Python is replaced, so it is not straight under FR-001c and keeps its review.

   **Decisions** (FR-011, FR-002, FR-003, SC-006, `ask:449-T92-messages`):
   - The baseline, from the session's own runs: touching one source file made `make rust-test CRATE=rust/gate` take 68 s (about 50 s compiling, 16 s the 842 tests), touching only a test file 21 s (6 s compiling), nothing changed 21 s (observed 2026-11-11, method: `make rust-test CRATE=rust/gate` after `touch` of one file, wall time).
   - The crates, sized in lines of code and tests (observed 2026-11-11, method: `wc -l` over each crate's `src`): `core` 2,795 (the shared helpers under their old module names, `codeid`, `difflib`, `logs`, the record's `repo`/`args`/`units`/bundle helpers and runner, the door loop, and the `testkit` feature the other crates' tests build on), `tree` 3,924 (stamp, delta, state, hashing, exempt, lock, the ratchets, `checks::needs`), `downloads` 3,305, `checks` 6,111, `plan` 7,070, `cohort` 4,286 (cohort, push, rustc), `owed` 5,325, `bundle` 7,416 (the check bundles, the round marks, `owed-door`), `claims` 9,506, `reviews` 4,520, `trials` 4,318, `measure` 5,394 (with `preflight`), `arbiter` 5,366 (with `checks-door`), `ci` 1,535, `record` 3,051, the binary 238. They form a DAG with no cycle; `rust/gate/CLAUDE.md` has a row a crate and what each builds on.
   - Each moved file keeps its module path: a crate's `lib.rs` re-exports, under the old names, what it reads of the crates below it (`pub mod record { pub use l7r_gate_owed::record::*; pub mod bundle; }`), so `crate::record::owed::...` and `super::py_repr` resolve unchanged. Items another crate names became `pub`, with `#[must_use]`, `# Errors` and `# Panics` written on each (clippy pedantic); three targeted `#[expect]`s with reasons (`implicit_hasher` on `owed::read_at`, `must_use_candidate` on the fixtures' `git` and `commit`), no blanket allow.
   - The one edge inverted through the binary: `plan` -> `claims::cli` (`decide` and `delta`'s triage hint). `plan::cli` takes the claims tool as a `&dyn Fn(&[String]) -> Reply` the binary hands in, plan's tests a stub; the output is the same `claims::cli`'s. Every other edge is a plain dependency or an item moved down (the shared helpers to `core`; `needs`, the ratchets and `top` to `tree`; the round marks to `bundle`; the door loop to `core`; `checks::needs` now answers its exit code, the cli's reply unchanged).
   - One crate, not the two the design drew, for the claims (`claims_base` under `claims`): the lower half's tests build on the upper's command line (`bundle/tests.rs`, `report/tests.rs` through `carry::key_of`) and fixtures, so a split owed moving tests across for little: the claims' dependents are `arbiter`, `ci` and the binary.
   - Tests: 870, the 842 kept, each with the module it tests, and 28 new for lines another crate's tests had reached (core's `kit_tests.rs` and its helpers' own tests, and more across tree, cohort, claims, downloads, plan, reviews, trials, owed and ci (both sides of the route's make check); `rustc`'s two nested-crate tests; the binary's push-gate path test split from `push/tests.rs`, which names the claims' and the modals' paths the push's crate cannot see) (observed 2026-11-11, method: the 16 `make rust-test CRATE=` runs' `test result` counts). `claims::read_paths` is a plain `pub fn`.
   - Coverage: every gate crate at 100% of its own lines by its own tests but `ci/gated.rs` 196-197, which only a run under make reaches (the baseline had them unreached outside make too) (observed 2026-11-11, method: `l7r-gate rust uncovered --crate` over the sixteen, and `make static`). Measured before the move, by running each proposed crate's tests alone in a scratch clone, 302 lines were reached only by another crate's tests; each is now reached by its own.
   - `l7r-gate rust` learned the crates (`crates/cohort/src/rustc.rs`): a verdict key follows path dependencies transitively, and a path belongs to the crate whose directory holds it most nearly (`rust/gate` holds `crates/*`: by prefix alone a nested crate's own files had fallen out of its key, and its checks would never have run again); `uncovered` leaves a nested crate's lines to it; `dead` counts a gate crate's calls over `rust/gate/**`; the gate's crates share one coverage build (`cover-gate`, its shared dependencies built once), a run clearing only its own `lib<name>-` and every other test binary (llvm-cov's report reads each binary in the build, and another crate's carried this crate's code with none of the run's counts).
   - The paths: the checks that read the gate's own files by path name them where they now are (`tree`'s `checks::needs` partial-citations set, `research_pointers`' fixture and refusal lists, `tool_signals`' entry scripts and its scan of `rust/gate`, `scripts/measure/tool_yield.py`'s `ENTRY_SCRIPTS`, the guard's `html_text` include of the entity table); the 118 `rust/gate/src/` mentions outside `specs/` point at the crates, but the guards' three "moved from `rust/gate/src/...`" history comments, `dev/rust-tooling.md`'s `rust/gate/src/ci/aws.rs` (a file gone before T92) and two tests' scratch-repository fixture paths. The Rust's own output text naming `rust/gate/src/` was the five `push.rs` selftest messages, corrected under `ask:449-T92-messages`: file-scale and research-pointers (`fix rust/gate/crates/checks/src/checks/`), downloads (`rust/gate/crates/downloads/src/record/downloads/check.rs`), spec-lint (`rust/gate/crates/checks/src/checks/spec_lint.rs`), gate-stamp (`rust/gate/crates/tree/src/stamp.rs`); a grep of the split tree finds no other.
   - Behavior: 102 invocations of every subcommand (usage errors, the self-tests, the checks over the tree, the plan, claims, record, reviews and arbiter reads, the four doors) of the pre-split binary and the split one, each on the same fixture clone of the pre-split commit reset between cases, compared on exit, stdout, stderr and what each leaves in the tree: one differs, `check research-pointers`, whose fixture list now names the crates' paths, so on the pre-split tree it reads the moved files' fixtures as unexempted; two runs of the pre-split binary differ in none (observed 2026-11-11, method: the scratchpad's `t92/behave.py`).
   - After (observed 2026-11-11, method: `make rust-test CRATE=<crate>` after `touch` of one file, wall time): a claims source file 15.5 s for the claims crate, then 11.8 s for its dependent `arbiter` (9.7 s of it arbiter's tests), 2.4 s `ci`, 3.4 s the binary, a claims test file 3.5 s, an owed source file 34.6 s, a core source file 49 s, then 5.4 s the binary over every crate above it, nothing changed 1.5 s for claims, 0.3 s the binary, about 26 s for all sixteen one after another. Of a core edit's 49 s, 40 s is the wrapper rebuilding the release `l7r-gate` before it runs the tests and 1.3 s the test build and tests, of a claims edit's 9.4 s and 3.4 s, of an owed edit's 27.6 s and 3.1 s (observed 2026-11-11, method: `scripts/gates/l7r-gate.sh --version` timed after the `touch`, then the `make rust-test`). The release rebuild of the edited crate and what depends on it is now most of a crate's loop: the next fruit (T93).
   - Memory: a cold build of every gate crate's tests (`make rust-test CRATE=rust/gate` into an empty target directory) took 112 s and its rustc processes peaked at 3,791 MB together, 1,139 MB the largest one, under the 10 GB cap, so no `jobs` cap is set (observed 2026-11-11, method: `/proc` sampled every 0.5 s).

### T92 Approach (checklist part A)

1. **The goal, in the world.** An edit of the gate's Rust recompiles one crate and what depends on it.
2. **The constraints.** FR-011, FR-002 (every output byte for byte, `ask:449-T92-messages` for the five messages), FR-003 (every line of a crate reached by its own tests, clippy pedantic).
3. **Where each comes from.** G: the GM 2026-11-11 (`request.md`); O: the baseline and after figures above.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** Before T93 (the fast loop by default) and T94 (the landing's hook suites).
6. **The exits.** Green: the behavior check shows only the ruled path difference, every crate's tests pass and cover its lines, `make static` is green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The behavior check, the 870 tests, the coverage and the timings above; `make static`'s Rust steps (lint, format, cover, dead on 18 crates) green, its spec lint naming four findings in `spec.md` lines 185 and 193 (SC-006's `68 s` and three `m:` figures, not T92's text); `make rust-tooling`, the citation-rule inventory's test (2 passed) and `make hooks-test HOOKS_ALL=1` (53 suites) green (observed 2026-11-11, method: those make targets).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** Yes, of the build, not the engine: it removes work (an edit compiles a crate and its dependents, not 74,199 lines); no engine call count moves.


<!-- plan-archive: archived 2026-11-11 -->
### T94 (the landing's slow hook suites, FR-011)

- **Approach**: the two slowest suites of the T82 landing's `make done` read, measured alone and changed only where they did work `make done` need not repeat.

   **Decisions** (FR-011, SC-006):
   - The guard suite (`tests/hooks/test-l7r-guard.sh`) took 86.5 s in that landing (observed 2026-11-11, method: `make done`'s hooks-test line, `ran l7r-guard.sh 86.5s`). Its real-build case copied `rust/` into a scratch directory and built the guard crate there; cargo keys a build on the package's path as well as its sources, so the copy recompiled the whole crate on every run, the comment's "cp -p keeps the times, so cargo finds nothing to do" being wrong. It now runs the clone's own wrapper on the clone's own tree into the wrapper's own target, the one `make done`'s hook calls build (`make hooks-test` runs `scripts/hooks/l7r-guard.sh trace` and `deps`, and that wrapper rebuilds the release guard binary there when the guard's sources changed), so a changed guard crate is built once in a landing, not twice; it no longer deletes the kept binary to force a build, the build, self-check and keep paths being cases 1-6's on the fake cargo, and judges that the kept binary answers.
   - The same case's last check ran `sleep 30 | ( timeout 10 ... )`: a pipeline waits for its `sleep`, so the suite slept 30 s on every run, and the right side ran in a subshell, so its `ok`/`bad` never reached the suite's counts. It now feeds stdin from a process substitution, which the shell does not wait for, and judges in the suite's own shell, so the case counts (30 cases became 31).
   - Together: the suite runs in 1.5 s, both runs, the real-build case in 0.2 s (observed 2026-11-11, method: `bash tests/hooks/test-l7r-guard.sh` timed twice with `date +%s.%N`, the suite's own `real build through the wrapper` line). A change to the guard crate still pays its one real build there, which is the case's purpose.
   - The sync-with-main suite took 83.7 s in the T82 landing and 94.3 s in T92's hook run, but 19.3 s alone (observed 2026-11-11, method: `bash tests/hooks/test-sync-with-main.sh` timed alone, and a `bash -x` trace with `PS4` carrying `EPOCHREALTIME` summed by command, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/speed/trace.py`). The trace shows its parts already run in parallel under one `wait`, and none builds a crate; its time in a landing is CPU shared with the parallel coverage and counters builds. It is left as it is; how `make done` schedules its phases is the measured question after T93.
   - Every suite, not only the two slowest (SC-006 covers all of them): with the tree's build warm from the T92 landing's `make done`, one `make hooks-test HOOKS_ALL=1` run of all 53 suites wrote no build output under any cargo target directory and made no new one; the only file written was the guard suite's kept `l7r-guard.good`, re-kept with nothing compiled (observed 2026-11-11, method: `bash /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/speed/buildcensus.sh`, which lists every file under `~/.cache/l7r-cargo-target/` newer than a marker made before the run, excluding `incremental/`, and diffs the target directories before and after). The suites that build at all reach cargo only through the wrappers `scripts/hooks/l7r-guard.sh` and `scripts/gates/l7r-gate.sh`, and through `tests/hooks/guard-shim.sh` and `tests/hooks/guard-cases.sh`, which set the clone's own target (found by `git grep -nE 'cargo|CARGO_TARGET_DIR|L7R_GATE_TARGET|L7R_GUARD_TARGET' -- tests/hooks`); the guard suite's real-build case was the one second target.

### T94 Approach (checklist part A)

1. **The goal, in the world.** A landing's hook suites spend their time on what they check, not on rebuilding or sleeping.
2. **The constraints.** FR-011 and SC-006; the guard suite's real-build case keeps proving the wrapper against the real crate.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the landing's hooks-test line and the timings above.
4. **Do they describe the world here?** Measured on this clone, alone and inside `make done`.
5. **The order.** After T92; T93 follows.
6. **The exits.** Green: the guard suite green in about a second and its new case counted, the hook suites green, `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The guard suite's two timed runs above; `make hooks-test HOOKS_ALL=1` green on 53 suites (observed 2026-11-11, method: that command on the T92 tree, which carries this change).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.

<!-- plan-archive: archived 2026-11-11 -->
### T93 (the fast Rust loop by default and enforced, the GM 2026-11-11, `request.md` "the Rust iteration loop", FR-011)

- **Approach**: the Rust checks get their own crate and binary, and every check of a crate reuses its last green result while what it depends on stands. T93 is not a port: no Python is replaced, so it is not straight under FR-001c and keeps its review.

   **Decisions** (FR-011, FR-002, FR-004, SC-006):
   - The before, from T92's after-figures: of a core edit's 49 s under `make rust-test CRATE=`, 40 s was the wrapper rebuilding the release `l7r-gate` before any test ran, of a claims edit's 15.5 s 9.4 s, of an owed edit's 34.6 s 27.6 s, and `test` never reused a result, nor any check of a named crate (observed 2026-11-11, method: T92's `make rust-test CRATE=<crate>` after a `touch`, as T92's section in plan-done.md records). Measured again on a scratch clone, the full binary's release rebuild after touching one crate's `lib.rs` took 48.3 s for core, 30.7 s tree, 30.6 s plan, 8.8 s claims and 1.3-13 s for the others, and a prototype of the runner over core and tree alone rebuilt in 0.0 s after a claims, owed, plan, cohort or arbiter touch, 5.1 s after tree's and 8.0 s after core's (observed 2026-11-11, method: `scripts/gates/l7r-gate.sh --version` and the prototype's release build timed after each touch, `scratchpad/t93/wrap.json`, `proto.json`).
   - The runner is its own crate, `rust/gate/crates/rustc` (package `l7r_gate_rustc`, over core and tree only), with its own binary `l7r-rust`: `l7r-gate.sh rust <cmd>` builds and runs it, stale only over `crates/{core,tree,rustc}`, `rust/guard` and the workspace's manifests. The full binary still dispatches `rust` to the same code. The wrapper's staleness scan had left out `rust/guard`, which both binaries build on, so a guard edit left `l7r-gate` stale: it now scans it, and touches the binary after a build, so a newer file cargo ignores asks no build on every call.
   - The key: a crate's test, cover, lint and dead run again only when its key moves - its sources, the crates it builds from by path (followed against every crate, also when crates are named), the workspace's manifests, and what its tests read of the tree at run time, which its `Cargo.toml` declares (`[package.metadata.l7r] reads`, `"."` the whole tree, every other crate's files too). Declared: checks, cohort, plan, tree and the gate binary `"."`, ci `scripts/`, guard `tests/hooks/`, `Makefile` and `scripts/`, rustc its fixture crate. Before T93 every crate's cover and counting run were keyed on the whole tree, so a spec's edit ran all eighteen. A crate whose sources name the tree (`CARGO_MANIFEST_DIR`, `top()`, `toplevel()`) and declare nothing is refused with the fix named. The checks crate's own file-scale test proved the whole-tree reading on the way: it failed on `rustc.rs` at 1,105 lines, a file in another crate, so `"."` covers the other crates' files and `rustc.rs` was split (`rustc/kept.rs`).
   - The second key, for `test` and `test-counters` when the first moved: the crate's test binaries (`cargo test --no-run --message-format=json`) and every input but its Rust sources. A binary that already passed runs nothing, and the counting build shares the plain one's verdict where its binary is the same, which is every crate but core (its `testkit`) and phases (its `counters`) (observed 2026-11-11, method: the executables' sha256 compared with and without `--all-features` on a scratch clone, `scratchpad/t93/determinism.json`, and `make done`'s counters-inert running only those two of nineteen).
   - A content id is git's blob id whether the file is edited, staged or committed (`git hash-object --stdin-paths` for what differs from the index), and the last eight green keys are kept: the first version hashed an edited file's bytes and read the index's blob id once committed, so a commit ran every crate it touched once more, and an edit taken back ran again.
   - The escape: every crate fresh is `FRESH=1 REASON="..."` on `make rust-test`, `make static` or `make counters-inert`, through `LOGESCAPE` and `guard_log` (refused without a reason of two words), or `make done FULL=1`, which sets the same `L7R_RUST_FRESH` (`done: export L7R_RUST_FRESH := $(if $(FULL),1,)`) and runs `bypass-audit` before any check: that recipe asks for a reason at a terminal, cancels on an empty answer, refuses a run with no terminal or with `REF_WHY` set from a backgrounded call, and records the reason given, or the refusal, with `l7r-gate log bypass` (`LOGBYPASS`), so it too states a reason and is recorded. Those are the only two: `FULL` on `make rust-test`, `make static` or `make counters-inert`, and `INCREMENTAL=0` anywhere, no longer turn reuse off, and the idle run's `make done INCREMENTAL=0` keeps reuse for the Rust checks (`make idle-tests`' help says "the whole gate, never FULL"). No new guard: a repeated `make rust-test` or `make static` with nothing changed now runs no test.
   - Output: the `l7r-gate rust` verbs answer byte for byte as before but where a kept result stands - `rust-checks: <cmd> unchanged on <crate> - its last green result stands` now also for `test`, for a named crate, and on a second-key hit - and the new refusal of an undeclared reader.
   - After (observed 2026-11-11, method: `make rust-test CRATE=<crate>` wall time after `touch` of one file and after a one-line comment added at its top, then the file restored with git, `scratchpad/t93/after.py`): a claims source file touched 0.2 s, edited 13.9 s (the test binary rebuilt, the same binary, no test run), restored 0.1 s, owed 0.2 s, 8.4 s and 0.1 s, core 5.1 s (the runner's rebuild), 10.0 s, 5.1 s, against T92's 15.5 s, 34.6 s and 49 s. Nothing changed: `make rust-test` over all nineteen crates 0.4 s, no test, and `make static` 3.3 s, no coverage run, 32.2 s when the full binary was stale from the core edit (observed 2026-11-11, method: the same script, twice each). `make done` green in 64 s, counters-inert 53 s of it running core's and phases' counting tests, then `make done` with nothing changed 1.6 s, already verified (observed 2026-11-11, method: two `make done` back to back, `dev/run-log` records `20261111T160942814774-3907071.json` and `20261111T160944685917-3907429.json`).

### T93 Approach (checklist part A)

1. **The goal, in the world.** An edit of one crate and `make rust-test` or `make static` costs the build of what changed and the tests whose binary changed, nothing more, and no session can drift back to the slow run without saying why.
2. **The constraints.** FR-011, SC-006, FR-002 (every output byte for byte but the kept lines and the new refusal, named above), FR-004 (every line of the new crate reached by its own tests, clippy pedantic).
3. **Where each comes from.** G: the GM 2026-11-11 (`request.md`); O: the figures above.
4. **Do they describe the world here?** Tooling; no researched value moves.
5. **The order.** After T92 and T94.
6. **The exits.** Green: the after-figures above, `make static`, `make hooks-test HOOKS_ALL=1` and `make done` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The after-figures above, `make static` green (lint, format, cover, dead on 19 crates), `make hooks-test HOOKS_ALL=1` green on 53 suites, `make done` green, and `FRESH=1` refused without a reason and logged with one (observed 2026-11-11, method: those make targets).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.


<!-- plan-archive: T94 to T94 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-11 -->
### T95 (the full l7r-gate release binary rebuilt after any gate crate edit, FR-012)

- **Approach**: the three tool binaries (`l7r-gate`, `l7r-rust`, `l7r-guard`) build in a named cargo profile, `[profile.tool]` in `rust/Cargo.toml`, which inherits release and turns incremental compilation on, and `[profile.release]` is left as cargo's default because the hamlet engine's `cargo run --release` (Makefile `HAMLET_RUN`, `rustc.rs`) builds it.

   **Decisions** (FR-012, SC-007):
   - Cargo's release profile compiles without incremental compilation, so a one-line edit to any gate crate rebuilt the whole release binary, 38-45 s after a comment in core, 21-23 s in tree, 15-17 s in plan, 8.0-8.6 s in claims and 19-21 s in owed (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t95/bench.py` in a scratch clone, the binary built through a copy of `scripts/gates/l7r-gate.sh` after a one-line comment and after its revert, two samples each, `results.jsonl` beside it).
   - Under the tool profile the same rebuilds took 1.9-2.1 s in core, 2.0 s in tree, 1.4 s in plan, 1.1 s in claims and 1.5 s in owed (observed 2026-11-11, method: the same bench, the same edits), and a one-token code edit gave the same band, 1.3-2.6 s (observed 2026-11-11, method: the same bench, a code token changed in place of the comment).
   - Rejected, each measured on the same bench (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t95/bench.py` and `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t95/summary.py`): `codegen-units = 256` equals incremental's own default and bought nothing, opt-level 1 saved 0.3-0.5 s a rebuild but slowed the heavy verbs by 30-60%, `lto = "off"` bought nothing and slowed the tool by 15-40%, and the dev profile rebuilt more slowly (2.7-6.0 s) and compiled the guard twice. The `rust-lld` linker saved about 0.4 s more (observed 2026-11-11, method: the same bench, its option f2 linking with `rust-lld`) but needs both wrappers' `RUSTFLAGS` kept identical and a linker installed, so it is left out of this landing.
   - The tool runs no slower and says the same: the 8 verbs `check spec-lint`, `record record-owed`, `claims owed`, `tunables --inline`, `file-scale`, `conflict`, `research-pointers` and `delta key` gave byte-identical stdout, stderr and exit codes, with spec-lint 1.07-1.12 s before and 1.04-1.21 s after and record-owed 2.78-3.06 s before and 2.86-2.94 s after (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t95/verbs_ab.py`, three alternated runs each against a copy of the release `l7r-gate` taken before the change, outputs hashed).
   - The guard shares the build: `scripts/hooks/l7r-guard.sh` builds `--profile tool`, its self-check and kept copy read `tool/l7r-guard`, and `tests/hooks/test-l7r-guard.sh`'s fake cargo refuses a build without `--profile tool`, so a wrapper drifting back to release goes red. `make_only_hooks` matches the binaries by name, so its code is unchanged, and one case each in `tests/hooks/test-make-only-hooks.sh` and `make_only_hooks/tests.rs` pins a `tool/l7r-gate` path.
   - The guard answers the same and no slower: over four hook inputs (a `git status`, a bare `cargo build` it refuses, a `Read` and an `Edit`) the release and tool builds of `l7r-guard` gave identical stdout and exit codes, with a median of 29.9 ms for release and 26.4 ms for tool and a p90 of 46.1 ms and 45.1 ms (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t95/guardlat.py`, 15 alternated rounds of the four inputs through copies of both binaries, the event and guard logs sent to scratch directories).
   - `l7r-guard bench` compares verdicts, not times, and runs the current guard in its own process, so its release-built baseline is no comparison across profiles.
   - Left in release on purpose: the hamlet engine's run, and `bench.rs`'s baseline build, which builds the guard as it stood at an older commit whose manifest may not define the profile, into its own worktree's target.
   - Its costs: the `tool/` directory is 485 MB per clone target against release's 141 MB, and a cold tool build took 34.1 s, `l7r-rust` 0.36 s after it (observed 2026-11-11, method: `du -sh` on the target and `/usr/bin/time` on the wrapper). `rust/Cargo.toml` is in every crate's kept-result key, so the first `make rust-test` after landing reruns every crate once, 88.0 s here (observed 2026-11-11, method: `make rust-test` timed once after the change).
   - What it leaves: `make static` after a fresh comment in core took 103.3 s and in claims 64.8 s, and 6.5 s and 4.7 s after the revert (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t95/static_runs.sh`, one timed run each). The gate rebuild is about 2 s of that (observed 2026-11-11, method: the tool-profile bench above), the rest being the lint, coverage and dead-code runs T93's key reruns for the edited crate and every crate built on it, which is T96's measurement.

### T95 Approach (checklist part A)

1. **The goal, in the world.** A gate crate edit costs a couple of seconds of tool rebuild before any make target that runs the tool.
2. **The constraints.** FR-012 and SC-007: every output and verdict the tool gives today held, the hamlet engine's release build untouched.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the bench and the verb comparison above.
4. **Do they describe the world here?** Measured on a scratch clone of this tree and then on this clone.
5. **The order.** First of T95-T99, since T96 touches the same profile settings.
6. **The exits.** Green: the guard suite, `make rust-test` and `make static` green on the change, the verbs identical, `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The rebuild figures above, and `bash tests/hooks/test-l7r-guard.sh` 31 passed in 1.8 s with all 19 crates of `make rust-test` green (observed 2026-11-11, method: those commands on this clone after the change).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling build time, not the generator, so the checklist's generator tools do not apply:
1. **Where does the time go?** The release profile's non-incremental compile of the whole tool binary after any gate crate edit, measured by crate above.
2. **Does the change remove work, or only move it?** Removes it: incremental compilation keeps the unchanged code's compiled parts instead of compiling them again.
3. **What do you expect it to save, and why?** Most of each rebuild, since a one-line edit touches a small part of the binary, which the bench confirmed.
4. **How does the work grow?** With the edited crate's size rather than the whole binary's, so it no longer grows with every crate ported.
5. **What did the before and after show, and under what conditions?** The bench's two samples per crate and option, edits and reverts alternated on a throttled host, and the verb and guard comparisons above, alternated, read as evidence.
6. **Did any map move?** No: no engine code changes and the hamlet engine's release build is untouched.


<!-- plan-archive: archived 2026-11-11 -->
### T96 (a test binary rebuilt after a one-line edit, FR-012)

- **Approach**: every cargo build links with `rust-lld`, the linker the toolchain ships, through one repository-root `.cargo/config.toml`, and the dev profile (which the test profile inherits) keeps line tables only for debug info.

   **Decisions** (FR-012, SC-007):
   - Where a one-line edit's test rebuild went: a comment in `claims/src/lib.rs` rebuilt in 3.8 s and 3.9 s, the claims library 1.5 s, the test harness 1.6 s and GNU ld's link 1.2-1.4 s, and the GM's 13.9 s was that rebuild after a core edit and its revert, which cargo's timestamp check rebuilds through core, tree, owed and plan (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t96/bench.py` running `make rust-test CRATE=rust/gate/crates/claims` in a scratch clone, compile and link timed by a `RUSTC_WRAPPER` and a `cc` shim, two samples each).
   - GNU ld linked each gate crate's test binary one at a time, 27-61 s of `make static` after a core edit, and rust-lld linked them in 3.7-4.1 s (observed 2026-11-11, method: the same bench, option b against base).
   - Line-tables-only debug info cut the link to 17 s alone and the coverage tests to 37 s (observed 2026-11-11, method: the same bench, option a), and halved the build output.
   - One config file for every build, so no build's flags differ from another's that shares its target: cargo reads `.cargo/config.toml` from its working directory upward, so `scripts/gates/l7r-gate.sh`, `scripts/hooks/l7r-guard.sh` and `rustc.rs` (every cargo call, cover's `show-env`, build, tests and report included) now run cargo from the tree's root, and make's recipes and `HAMLET_RUN` already do. `cargo llvm-cov show-env` folds the config's flags into the RUSTFLAGS it prints, so the coverage build keeps lld, its test binaries reporting `Linker: LLD 20.1.1`.
   - No toolchain is pinned, so the config names the 1.87.0 `gcc-ld` directory and a moved toolchain is caught with its fix: `scripts/hooks/lib/lld-path.sh` makes `l7r-gate.sh` refuse and `l7r-guard.sh` keep its last good binary, each naming the `-B` path to set, and `make rust-test` fails `the_configured_rust_lld_is_the_active_toolchain_s`.
   - `.cargo/config.toml` joins the kept-result key's workspace files in `kept.rs`, and `rustc/Cargo.toml` declares `.cargo/` in its reads, so a config change reruns every crate rather than leaving stale results standing.
   - The release and tool profiles do not inherit dev's debug setting, so the hamlet engine's code generation is unchanged by it, and its release build relinks once with lld.
   - Rejected or left: opt-level 0 for our crates (option c) bought less than a and b, and instrumenting only our own crates for coverage (option e, 20 s a run) is T100's, as are the `"."` reads and the dead-code key (observed 2026-11-11, method: the same bench, options c and e).
   - After the change: `make rust-test CRATE=rust/gate/crates/claims` after a comment edit took 1.1 s and 0.9 s and after its revert 0.2 s and 0.2 s, the claims test binary went from 136 MB to 48 MB, and this clone's target directory from 41 GB to 6.0 GB (observed 2026-11-11, method: those makes timed twice on this clone, `ls -l` on the binary and `du -sh` on the target).
   - `make static` after a core comment edit took 74.9 s, 81.8 s and 75 s against T95's 103.3 s, and after a claims comment edit 55.8 s and 56.6 s against 64.8 s (observed 2026-11-11, method: `make static` timed on this clone after each edit), most of what is left being the coverage tests, which is T100's.
   - The same verdicts: `make rust-test` green on 19 crates, claims' and core's coverage reports identical to before once build hashes are stripped, `bash tests/hooks/test-l7r-guard.sh` 37 of 37, and the 8 `l7r-gate` verbs identical from the before and after binaries over one tree (observed 2026-11-11, method: those commands on this clone, the reports diffed by `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t96/lcovdiff.py`).

### T96 Approach (checklist part A)

1. **The goal, in the world.** A one-line edit to a gate crate costs about a second of test rebuild, and links stop dominating `make static`.
2. **The constraints.** FR-012 and SC-007: every coverage figure, lint finding and tool output held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the bench and the after-figures above.
4. **Do they describe the world here?** Measured on a scratch clone, then on this clone.
5. **The order.** After T95, before T101-T103 and T97-T100.
6. **The exits.** Green: `make rust-test`, `make static`, the guard suite and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The after-figures above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling build time, not the generator:
1. **Where does the time go?** In the link (GNU ld, one binary at a time) and the debug info it writes, measured above.
2. **Does the change remove work, or only move it?** Removes it: a faster linker and less debug info to write and link.
3. **What do you expect it to save, and why?** Most of each link, which the bench showed before building.
4. **How does the work grow?** With the number of test binaries linked, now each about a third of the size.
5. **What did the before and after show, and under what conditions?** Two samples per option on a throttled host, read as evidence, with a noisy spread noted (an earlier pair of core runs took 178-194 s, observed 2026-11-11, method: `make static` timed on this clone after a core edit).
6. **Did any map move?** No: no engine code changes.


<!-- plan-archive: archived 2026-11-11 -->
### T103 (session scratch under /tmp/claude-1000 swept, FR-013)

- **Approach**: a new guard, `scratch-sweep-hooks` (`rust/guard/src/guards/scratch_sweep_hooks.rs`, what it removes in `sweep.rs`), starts at most one detached sweep a day from UserPromptSubmit, and `make scratch-sweep [DRY=1]` runs one on demand.

   **Decisions** (FR-013, SC-008):
   - Nothing removed a session's scratch: `/tmp/claude-1000` reached 38 GB and one session's scratch 20 GB (observed 2026-11-11, method: the GM's laptop session's `du`, and `du -sh` on this session's directory).
   - What goes: a session directory `/tmp/claude-<uid>/<slug>/<session id>/` when its transcript `~/.claude/projects/<slug>/<id>.jsonl` and everything inside it have been unchanged three days (a subagent writing into its session's scratch moves no line of the session's own transcript, so both are read), one with no transcript when nothing inside changed in three days, and a loose top-level entry when nothing inside it changed in three days.
   - What stays, always: the prompting session's directory, every session Claude Code records as running in `~/.claude/sessions/<pid>.json` while that pid still runs and started when the record says (its `procStart` against `/proc/<pid>/stat`'s 22nd field, so a reused pid keeps nothing), with no session directory judged at all where that registry cannot be read, any entry a live process holds as its cwd, its binary or an open file (read from `/proc`, and nothing is removed where `/proc` cannot be read), any tree with a directory the sweep cannot read, and anything through a symlink: a link is never followed or descended, so a link inside a removed tree is deleted as itself, its target untouched, and a link standing at the root or among a project's sessions is left. The uid is the process's own, and the root, the projects directory, the state directory, the threshold (`SCRATCH_SWEEP_DAYS`) and the clock are seams the tests set.
   - Once a day, one at a time: the hook reads only the stamp's age and starts the sweep with `setsid -f`, which takes a lock, checks the stamp again and writes it before walking, so a sweep that dies is not retried every prompt and a second session finds the lock held or the stamp fresh. The hook added 0.15 ms to a usual prompt and 1.3 ms on the day's one start, against 5.40 ms for the process alone (observed 2026-11-11, method: the median of 20 runs of each on a fixture tree, never the real stamp).
   - Every removal and the day's total go to the guard log with its size.
   - The dry run on this machine would remove 110 entries, 11.0 MB, the large trees already cleared by the GM's laptop session (observed 2026-11-11, method: `make scratch-sweep DRY=1`).
   - Left as it is: a project directory left empty is kept.

### T103 Approach (checklist part A)

1. **The goal, in the world.** A finished session's scratch does not outlive it by more than a few days.
2. **The constraints.** FR-013: never a live session's, never anything outside the root.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the sizes and the dry run above.
4. **Do they describe the world here?** The dry run was read on this machine.
5. **The order.** After T96, beside T101; T102 extends it to the cargo cache.
6. **The exits.** Green: the guard crate's tests, `make static` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make rust-test CRATE=rust/guard` 504 passed with the sweep's tests, and the dry run above (observed 2026-11-11, method: those commands on this clone).
10. **Before moving a constant.** The three days and the one day are new constants, chosen as GUESS knobs (`SCRATCH_SWEEP_DAYS`), long enough that a session paused over a weekend keeps its scratch.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: archived 2026-11-11 -->
### T102 (the cargo target cache stops growing, FR-013)

- **Approach**: T103's daily sweep also prunes `~/.cache/l7r-cargo-target` (`rust/guard/src/guards/scratch_sweep_hooks/sweep/cargo.rs`), under the same lock, stamp, live-process check, log and `make scratch-sweep [DRY=1]`.

   **Decisions** (FR-013, SC-008):
   - The leak: every tree that builds gets its own `~/.cache/l7r-cargo-target/<tree name>/` and nothing removed one, 54 GB in 56 directories, and inside one clone's `debug/` cargo kept 3,407 `l7r_fixture` incremental directories and 5,069 compiled files, about 5.6 GB (observed 2026-11-11, method: `du -sh` on each directory, `ls | grep -c l7r_fixture` and `du -ch` on that clone's `debug/incremental` and `debug/deps`).
   - Its source is gone: those were `l7r_fixture_broken_<n>` crates, built from a fresh path each run by a Python test deleted with the Python suite on 2026-11-10, the newest of them dated 2026-11-09, and the one Rust test that builds the fixture crate does so into its own scratch target, which T101 now removes (observed 2026-11-11, method: a build's `.d` file and `.fingerprint` names in `diagram-research`'s target, `ls -lt` on them, and `git grep` for `fixture_broken` finding nothing in the tree).
   - Cargo makes a new variant of a crate (a new `-<hash>` in `deps/`, `incremental/`, `.fingerprint/`, `build/`) only when its path or its flags change, never on a source edit, so variants pile up only from moved paths and changed flags. A crate's live variants are its test, lint and all-features builds, at most three, so each crate's variants in a store beyond its newest four go once idle three days; one wrongly taken costs only its rebuild.
   - A build directory named for no live tree, neither the mirror nor any directory under `/diagram/.clones`, goes whole once nothing in it changed in three days; the mirror's and every clone's are never removed whole, the guard hook running the mirror's kept binary; where the clones directory cannot be read, none is removed whole. Anything a live process holds is kept, as in T103.
   - The dry run on this machine would remove 449 entries, 2,409.6 MB, of a 34 GB cache: six stale build directories whole (a top-level `debug/` and `release/` from an older layout, `base`, `pyseat`, `wt-old`, `llvm-cov-target`) and old variants inside the rest, among them the `l7r_fixture` and `l7r_phases` variants of `diagram-backlog-tooling` (observed 2026-11-11, method: `make scratch-sweep DRY=1` and `du -sh ~/.cache/l7r-cargo-target`). This session's scratch clones' builds (`t101clone`, `t103clone`), changed today, go three days after their last build.
   - Tested on a fixture: the mirror's and a clone's build directories kept whole however old, a gone scratch clone's removed and a fresh one's kept, six old variants of one crate losing their oldest two, five fresh ones losing none, a nested coverage target's store found, a store below the depth limit and a symlink left, an entry whose age cannot be read kept, and nothing removed whole where the clones cannot be listed (`make rust-test CRATE=rust/guard`, 516 passed, observed 2026-11-11, method: that command on this clone).

### T102 Approach (checklist part A)

1. **The goal, in the world.** The build cache holds what live trees build with, and no more than a few days of anything else.
2. **The constraints.** FR-013 and SC-008; the guard's kept binary and a live clone's build are never removed whole.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the sizes, the counts and the dry run above.
4. **Do they describe the world here?** The dry run was read on this machine.
5. **The order.** After T101 and T103, whose sweep it extends.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The dry run above.
10. **Before moving a constant.** Four variants and three days are new constants, GUESS knobs: four above the three live variants a crate has, three days as T103's.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: T103 to T103 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-11 -->
### T97 (make done's counters-inert phase, FR-012)

- **Approach**: `l7r-gate rust test-counters` (`rust/gate/crates/rustc/src/rustc.rs`) runs a crate's counting build only where the crate has a `counters` feature, and passes over the rest by name.

   **Decisions** (FR-012, SC-007):
   - Where the time went: the phase took 113 s in T102's landing's `make done` and 59 s in T101's (observed 2026-11-11, method: the `phases` field of the run records `dev/run-log/2026-11/20261111T220512696061-2826777.json` and `20261111T215633488253-2744162.json`). It ran `cargo test --all-features` on every crate whose key moved, and an edit of the guard crate, which every gate crate builds on, moves all 19; the arbiter crate's tests alone took 8-11 s of it (observed 2026-11-11, method: the landings' `test-counters on rust/gate/crates/arbiter` lines).
   - Only `rust/phases` has a `counters` feature; core's one feature, `testkit`, is on in its own test build already (`#[cfg(any(test, feature = "testkit"))]`), every other crate has none, and no crate builds on `rust/phases` (observed 2026-11-11, method: each `Cargo.toml`'s `[features]` read, and `grep -l phases` over every manifest). So for 18 of the 19 crates the counting build was the default test build run a second time, and `make static`'s `cover` runs those same tests in the same `make done`. The phase's purpose, that the counters change no result, has only `rust/phases` to prove it on, which it still does.
   - After: `make counters-inert FRESH=1` with every crate run fresh took 4.96 s, 18 crates passed over and `rust/phases` 93 passed (observed 2026-11-11, method: `/usr/bin/time` on that command on this clone).
   - The same command after (SC-007): the landing that carried T97 ran its `make done` counters-inert phase in 1 s, against 113 s and 59 s in the two landings before it (observed 2026-11-11, method: the `phases` field of `dev/run-log/2026-11/20261111T221159134216-2861346.json`).
   - The same verdicts: every test a skipped crate's counting build ran is run by `cover` in the same `make done`, and `rust/phases`' counting run is unchanged. The rustc crate's tests give a crate a `counters` feature where they run the counting build, and assert the pass-over line for one without (`make rust-test CRATE=rust/gate/crates/rustc`, 27 passed, observed 2026-11-11, method: that command on this clone).

### T97 Approach (checklist part A)

1. **The goal, in the world.** `make done` proves the counters inert where there are counters, and nowhere else.
2. **The constraints.** FR-012 and SC-007: every verdict held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the run records and the timing above.
4. **Do they describe the world here?** Measured on this clone.
5. **The order.** After T101-T103.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The forced-fresh timing above (observed 2026-11-11, method: `/usr/bin/time make counters-inert FRESH=1`), and the next landing's `counters-inert` phase.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** In counting builds identical to the default ones, rerun for every crate a shared edit moves.
2. **Does the change remove work, or only move it?** Removes it: 18 duplicate test runs a landing.
3. **What do you expect it to save, and why?** Nearly the whole phase, since 18 of its 19 crates were duplicates.
4. **How does the work grow?** With the crates that have counters, one today, not with every crate ported.
5. **What did the before and after show, and under what conditions?** One landing's phase each before and one forced-fresh run after, on a throttled host, read as evidence.
6. **Did any map move?** No: no engine code changes.


<!-- plan-archive: archived 2026-11-11 -->
### T100 (make static's lint, coverage and dead-code reruns after a fresh gate crate edit, FR-012)

- **Approach**: three changes to `l7r-gate rust` (`rust/gate/crates/rustc/src/rustc.rs`, `rustc/kept.rs`) and the crates' declared reads.

   **Decisions** (FR-012, SC-007):
   - Coverage instruments the workspace's own crates only: `show-env`'s RUSTFLAGS instrumented every crate the build compiles, `fancy-regex` and `serde` too, though the report counts only the workspace's lines, and the checks crate's tests, which scan the tree with regexes, took 23 s under coverage against 0.6 s plain (observed 2026-11-11, method: T96's bench, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t100/../t96/bench.py`). `workspace_only` moves the three coverage flags out of RUSTFLAGS into a `RUSTC_WORKSPACE_WRAPPER` script, which cargo calls for the workspace's crates alone, the rest of RUSTFLAGS (rust-lld, T96) left to every crate; the script is rewritten only when its text changes. The coverage is the same: claims' 7,640 lines and core's 3,654 all hit before and after with identical `uncovered` reports, one loop's hit count in core's `units.rs` moving with the live tree it reads, 121 to 110, hit both times (observed 2026-11-11, method: `l7r-gate.sh rust uncovered` for each crate with `L7R_RUST_FRESH=1` before and after, the lcov reports compared line by line on the crate's own files by `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t100/lcovcmp.py`).
   - The declared reads narrowed to what the tests read: plan, cohort, tree and the gate binary declared `"."`, so any edit anywhere, a spec or a doc, ran their lint-free checks again; a full run of each test binary under the hook suites' read shim (LD_PRELOAD) recorded what they open of the tree, plan the approach checklist and three scripts, cohort the Makefile and one script, tree `dev/ratchets.json` and two scripts, the binary only `development-secrets.ini`, beside `.git`, which is git's own lookup (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t100/trace_reads.sh`). Each now declares those, whole directories where a script was read (`scripts/`) and the plan template its comment names; checks, whose file-scale and pointer checks read 36,499 files of the tree, keeps `"."`.
   - The dead check is keyed on its whole family: it counts a `pub fn`'s callers across every crate of the family (all of `rust/gate/`), but its key held only the crate and what it builds from, so a dependent dropping the last call left its kept green result standing. Its key is every file of the family; a test moves low's dead key with the binary's file and a sibling's, and not with a file outside the family.
   - Measured the same way before and after (SC-007): the tree without these changes in a scratch clone and this clone, each after `make rust-test` and a green `make static`, each edit a one-line comment unique to the run (a repeated text is answered from the kept results), `make static` timed after each: core 68.7 s before and 54.0 s after, claims 44.5 s and 25.3 s, a docs file 34.2 s and 13.5 s, each revert 3.7-5.7 s both ways, the coverage tests after a core edit 36.2 s and 16.6 s, and after the docs edit five crates' coverage ran before and one after (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t100/static_runs_before.sh` then `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t100/static_runs.sh`, back to back, `date +%s.%N` around each `make static` and the logs' `cover build` and `cover tests` lines summed).
   - What is left: a core edit still builds every gate crate's coverage binary one crate after another, 17 builds and 14.6 s of the 54.0 s (observed 2026-11-11, method: the same logs); building them together is a change to how the coverage run shares its build, filed apart if it is taken up.

### T100 Approach (checklist part A)

1. **The goal, in the world.** An edit costs `make static` the checks it can change, and coverage measures only the workspace.
2. **The constraints.** FR-012 and SC-007: every coverage figure and verdict held; a kept result never stands over an input that moved.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the traces and the timings above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of its committed tree.
5. **The order.** After T96, whose bench found the coverage cost.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The before-and-after timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Coverage instrumenting third-party crates, whole-tree reads rerunning five crates on any edit, and the coverage builds of a core edit's dependents.
2. **Does the change remove work, or only move it?** Removes it: uninstrumented dependencies, and checks no longer rerun when nothing they read moved.
3. **What do you expect it to save, and why?** Most of the coverage test time, and most of a non-Rust edit's reruns.
4. **How does the work grow?** With what an edit reaches, no longer with every crate that declared the whole tree.
5. **What did the before and after show, and under what conditions?** One back-to-back run each on a throttled host, read as evidence.
6. **Did any map move?** No: no engine code changes.


<!-- plan-archive: archived 2026-11-11 -->
### T98 (the hook suites run in parallel, FR-012)

- **Approach**: the batching suite moves its guard's clock by a file instead of sleeping, and the rest is measured and left.

   **Decisions** (FR-012, SC-007):
   - Each slow suite timed alone against its time in a full run tells its own cost from contention: sync-with-main 25.6 s alone, entry-gate 18.4 s, idle-tests 34.9 s, batching 29.3 s, land-tooling 8.9 s (observed 2026-11-11, method: `bash tests/hooks/<suite>` timed alone with `date +%s.%N`), against 62.7 s, 47.6 s, 36.3 s, 31.5 s and 17.3 s in a full `make hooks-test HOOKS_ALL=1` of the tree without this change (observed 2026-11-11, method: that run's `hooks-test: ran` line in a scratch clone). So batching and idle-tests cost their own time and sync-with-main and entry-gate mostly contention.
   - Batching's time was sleeps: 0.75 s before each simulated turn and 2.1 s inside a slow one, to move the wall clock the guard reads (observed 2026-11-11, method: the suite's `sleep` lines, 14 of them). The guard now takes its time from a file named by `BATCH_CLOCK`, honored only beside a fixture's own `BATCH_STATE_DIR`, so a session's hook never reads it (`rust/guard/src/guards/batching_hooks.rs`, a unit test of the file, its absence and a session without a state directory), and the suite moves it with `tick`, one clock a case since the cases run in parallel parts (a shared one moved every part's time, and two cases failed). Its one real wait, for the guard log's notice record, polls instead of sleeping. The suite took 1.4 s three times, all 56 checks passing (observed 2026-11-11, method: `bash tests/hooks/test-batching-hooks.sh` timed thrice).
   - Idle-tests is left: its time is real timer processes it exists to test, polled at a tenth of a second, and its timings have flaked before when tightened (observed 2026-11-11, method: a `bash -x` trace with `EPOCHREALTIME` in `PS4`, summed by line, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t98idle.trace`).
   - Tried and dropped: starting the suites longest-first by each one's last time made the full run slower, 74.8 s and 77.0 s, sync-with-main 67.5 s and 69.5 s, since the heaviest suites then contend with each other (observed 2026-11-11, method: two `make hooks-test HOOKS_ALL=1` runs with the queue sorted, reverted).
   - The same command before and after (SC-007): a full `make hooks-test HOOKS_ALL=1` took 71.2 s on the tree without this change and 63.8 s with it, all 54 suites green, sync-with-main 62.7 s and 56.5 s its longest (observed 2026-11-11, method: `date +%s.%N` around each, the scratch clone then this clone). What is left is sync-with-main's own time, measured alone above, and the contention around it.

### T98 Approach (checklist part A)

1. **The goal, in the world.** A full hook-suite run costs what its suites check, not their sleeps.
2. **The constraints.** FR-012 and SC-007: every suite's verdicts held; a session's hook never reads a test clock.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the timings above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of its committed tree.
5. **The order.** After T100.
6. **The exits.** Green: `make hooks-test HOOKS_ALL=1`, `make static` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The before and after runs above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** In one suite's sleeps, and in contention around the longest suite.
2. **Does the change remove work, or only move it?** Removes it: the batching suite's sleeping, the suite measured above.
3. **What do you expect it to save, and why?** The batching suite's whole sleep, and some wall time where it overlapped the others.
4. **How does the work grow?** With the suite's cases, no longer with sleeps between them.
5. **What did the before and after show, and under what conditions?** One run each, and three of the suite, on a throttled host, read as evidence.
6. **Did any map move?** No: no engine code changes.


<!-- plan-archive: archived 2026-11-11 -->
### T104 (a spec round's arbiter bundle read every subagent transcript whole, found under T99, FR-012)

- **Approach**: `first_prompt` (`rust/gate/crates/arbiter/src/arbiter/bundle/reviews.rs`) reads a transcript's first line only, through a buffered reader, where it read the whole file to take that line.

   **Decisions** (FR-012, SC-007):
   - Where T99's time went: one of the arbiter crate's 32 tests took 7.64 s of its 8-11 s, the next 0.42 s (observed 2026-11-11, method: the crate's test binary run once per test with `--exact`, timed by `date +%s.%N`), and within it one call, the bundle of `round:spec-fidelity|500-f#1@3`, took 7.62 s (observed 2026-11-11, method: a temporary timer around each bundle call in that test, reverted).
   - That call lists every subagent transcript on the machine to find the spec review's rounds, and `first_prompt` read each whole for its first line: 8,696 files, 8.0 GB (observed 2026-11-11, method: `ls ~/.claude/projects/*/*/subagents/agent-*.jsonl | wc -l` and `du -sch` over them). A real spec round's bundle paid the same.
   - After: the same test took 0.30 s and the whole crate's tests 1.09 s (observed 2026-11-11, method: the same per-test run, and `make rust-test CRATE=rust/gate/crates/arbiter`'s `finished in`).
   - The same output: the first line is what was parsed before, and a path that cannot be opened, a directory (whose read now fails at the first line rather than the open), an empty file and a first line that is not JSON each still give an empty prompt; the crate's 32 tests pass unchanged.
   - Left to T99: six tests still take 0.14-0.43 s against FR-008's 0.1 s, each computing the record's owed list one to four times, about 25 `git` calls and 0.1 s a computation (observed 2026-11-11, method: `git` and `python3` wrapped by timing scripts ahead on `PATH` for one test, 140 `git` and 8 `python3` calls).

### T104 Approach (checklist part A)

1. **The goal, in the world.** A spec round's bundle reads what it needs of each transcript and no more.
2. **The constraints.** FR-012 and SC-007: the bundle says what it said.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the timings above.
4. **Do they describe the world here?** Measured on this machine's transcripts.
5. **The order.** Found under T99, landed before it.
6. **The exits.** Green: `make static` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The after-figures above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Reading every transcript whole, 8.0 GB, to take one line of each (observed 2026-11-11, method: `du -sch` over them).
2. **Does the change remove work, or only move it?** Removes it: one line read a file.
3. **What do you expect it to save, and why?** Nearly the whole call, its reads falling from gigabytes to the first lines.
4. **How does the work grow?** With the number of transcripts, no longer with their length.
5. **What did the before and after show, and under what conditions?** One timed run each of the same test, on a throttled host, read as evidence.
6. **Did any map move?** No: no engine code changes.

<!-- plan-archive: archived 2026-11-12 -->
### T105 (a core edit's coverage builds made together, FR-012)

- **Approach**: `l7r-gate rust cover` (`rust/gate/crates/rustc/src/rustc.rs`) asks every crate's kept result first and builds the coverage binaries the rest owe in one cargo call a family (`build_together`), and each crate's own run keeps the builds it finds.

   **Decisions** (FR-012, SC-007):
   - Each crate's coverage run built its instrumented test binary alone, one crate after another in the family's one build directory, which cargo locks, so a core edit's 17 builds ran in a row on a machine of 22 cores (observed 2026-11-11, method: `make static` logs' `cover build` lines, and `nproc`). The crates owed are now built first in one `cargo test --no-run --lib -p <each>` a family, which compiles them side by side, in the same environment a crate's own run uses (`cover_env`, factored out); a failed build there is left to the crate's own run to report.
   - Each crate's run kept less than it could: it deleted every copy of its own library before building, which then compiled the crate again each run, and every other crate's test binary after, which the next crate built again. It now deletes only the copies of its own library the build did not just write, the build's JSON naming each artifact (an older one beside it carries lines of older source the report reads as unreached, measured 2026-11-07, the reason the deletion was there), and moves the other crates' binaries aside while its tests and report run (the report reads every binary in the build, T92) and puts them back after (`cover_built`).
   - The coverage is the same: claims' 7,640 lines and core's 3,654 all hit with every hit count and the `uncovered` report identical to T100's (observed 2026-11-11, method: `l7r-gate.sh rust uncovered` for each crate with `L7R_RUST_FRESH=1`, the lcov reports compared line by line on the crate's own files by `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t105/../t100/lcovcmp.py`; neither crate's sources moved since).
   - Measured the same way before and after (SC-007): a scratch clone of main without the change and this clone, each after `make rust-test` and a green `make static`, each edit a one-line comment unique to the run, back to back: `make static` after a core edit 65.0 s before and 57.2 s after, after a claims edit 26.0 s and 24.8 s, each revert 4.2-5.9 s both ways, the per-crate builds after the core edit 23.5 s before and 6.0 s after, the together build about 10 s of the rest (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t105/runs_before.sh` then `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t105/runs_after.sh`, `date +%s.%N` around each `make static`, the logs' `cover build` lines summed, the machine shared with other sessions at a load of 7-15). The together build now prints its own line.
   - What is left: the coverage tests themselves, 17.2 s of the core edit's run, still one crate after another (observed 2026-11-11, method: the same logs' `cover tests` lines).
   - The tests: a family's owed crates go to one cargo call naming each package, a family of one to none (`tests/cover.rs`), and the clearing test keeps a library the build wrote, removes one it did not, and finds another crate's binary put back. The coverage-step tests moved to `rustc/tests/cover.rs`, the tests file at the 1,000-line bar.

### T105 Approach (checklist part A)

1. **The goal, in the world.** A core edit's coverage builds use the machine's cores, and a crate's run rebuilds nothing it already has.
2. **The constraints.** FR-012 and SC-007: every coverage figure held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the timings and the coverage comparison above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of main.
5. **The order.** First of T105-T107.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The before and after timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Serial coverage builds, each rebuilding the crate's own library.
2. **Does the change remove work, or only move it?** Both: the rebuilds of a crate's own library go, and the builds left run side by side.
3. **What do you expect it to save, and why?** Most of the per-crate build time, cores being idle.
4. **How does the work grow?** With the slowest crate's build, no longer with the sum of all of them.
5. **What did the before and after show, and under what conditions?** One back-to-back run each on a shared, loaded host, read as evidence.
6. **Did any map move?** No: no engine code changes.


<!-- plan-archive: archived 2026-11-12 -->
### T107 (the record's owed list's git calls, FR-012)

- **Approach**: one computation of the record's owed list asks git for its revisions, its delta and its trees once, in a `Delta` (`rust/gate/crates/owed/src/record/delta.rs`) it makes and hands its four families (record, translation, entry-drift, modal), where each asked again.

   **Decisions** (FR-012, SC-007):
   - The cost: one computation on the arbiter's fixture made 24 `git` calls and took 519-599 ms under a timing wrapper, and `record-owed` with no flags made 47, computing its units twice (observed 2026-11-11, method: `git` wrapped by a timing script ahead on `PATH`, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t107/measure.sh`). The 35 a computation earlier counted the arbiter's own `git log` beside it.
   - `Delta` asks once for the revisions (the merge base first, HEAD and origin/main only where it is empty, each family's own fallback kept: the plain merge base, entry-drift's base, translation's base with none), one `diff --name-status --no-renames` over entry-drift's paths and one untracked listing, each family filtering them to its own paths, and one `ls-tree` a revision, all three families' blobs read in one `cat-file --batch`. Where a family's paths hold a deleted and an added file at once (a possible rename) or an unusual status, its own narrow diff runs instead, so its answer is exact. It is passed explicitly, made by one computation, no cache outliving it. `listing()` reuses its units rather than computing them again, and `unanswered_of`, with no caller left, is removed; the old entry points stay as thin wrappers for their other callers.
   - The same outputs: `make record-owed`, and `record-owed` (no flags, `--unanswered`, `--slugs`, `--between`), `modal-owed` and `translation-owed` on the fixture, stdout, stderr and exit codes byte-identical before and after, and the same verbs from the old and new binaries on a real record delta (the clone set back before commit 4a12ccfed, a listing of 1,075 bytes of owed units) identical too (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t107/realdiff.sh`, the old binary built from a second clone at e05e28023). `delta/tests.rs` holds each shared diff to the narrow one it replaces, the rename case included.
   - Measured the same way before and after (SC-007): one computation on the fixture 24 `git` calls and 519-599 ms before, 9 and 208-257 ms after (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t107/measure.sh`). `make record-owed` on this tree, an empty delta, 7.7 s (cold), 3.9 s and 2.9 s before, 3.4 s, 1.9 s and 1.6 s after, its `git` calls 44 and 14, their time 1.63 s and 0.41 s (observed 2026-11-11, method: the old and new binaries built side by side and run alternately, three each). The arbiter's real owed-list test 147 ms before and 126 ms after (observed 2026-11-11, method: best of six alone with `--exact`).
   - What is left: on the real tree every question page's base is read (one `cat-file`, about 180 ms) even on an empty delta, and `moved_only`'s whole-tree `ls-tree` is its own (observed 2026-11-11, method: the same wrapper on `make record-owed`).

### T107 Approach (checklist part A)

1. **The goal, in the world.** The record's owed list costs one read of git's state, wherever it is asked.
2. **The constraints.** FR-012 and SC-007: every output byte-identical.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the call counts, the timings and the output diffs above.
4. **Do they describe the world here?** Measured on a scratch clone of this tree and on a real record delta.
5. **The order.** After T105.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The call counts and timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** In `git` processes, each family asking the same questions.
2. **Does the change remove work, or only move it?** Removes it: 15 of 24 calls a computation on the fixture, 30 of 44 on the tree.
3. **What do you expect it to save, and why?** Most of the computation's git time, which was most of its time.
4. **How does the work grow?** With one read a computation, no longer with the families.
5. **What did the before and after show, and under what conditions?** Alternated runs of the old and new binaries on a loaded host, read as evidence.
6. **Did any map move?** No: no engine code changes.


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

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

<!-- plan-archive: archived 2026-11-12 -->
### T106 (the sync-with-main hook suite's own time, FR-012)

- **Approach**: the suite (`tests/hooks/test-sync-with-main.sh`) builds its fixture topology once and copies it a case, its id cache filled once, and waits for a lock instead of sleeping; the script under test, most of the time, is named as what is left.

   **Decisions** (FR-012, SC-007):
   - Where its time went: a serial run of its 32 cases took 154 s, 112 s of it the script under test (36 `push` runs of about 2 s, each about 1 s in `l7r-gate push-checks`, which starts about 17 processes, six of them Rust self-tests run on every push, plus 11 `done` and 15 `sync-in`), 23.1 s in `topology()`, which copied `scripts/` into a fresh seed repository, committed, pushed and cloned twice for each case, 8.9 s in `stamp_hooks`, each fresh clone's first id of every `scripts/` file, and two fixed `sleep 0.3` (observed 2026-11-11, method: each case run alone under `bash -x` with `EPOCHREALTIME`, the function and the line in `PS4`, the gaps summed by function, the script under test traced through `SHELLOPTS=xtrace` and `BASH_XTRACEFD=7`, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t106drv.sh`).
   - `template_build` makes the topology once before the parts run, and `topology()` copies it with `cp -a` (about 0.03 s against 0.25 s, observed 2026-11-11, method: the T106 agent timing each in a scratch clone) and points both origins at the copy's own `github.git`. The template's clone runs the stamp once, so each copy's id cache is filled, and the stamps that run wrote are deleted, so each case starts as it did. The two sleeps wait for the lock to be held (`lock_held`). Every case and every assertion stays, 138 checks passing (observed 2026-11-11, method: the suite run alone).
   - Measured the same way before and after (SC-007): the suite before and after run alternately on this clone, 23.4 s and 24.5 s before, 19.1 s and 19.5 s after, at loads of 4.8-6.4 (observed 2026-11-11, method: `bash tests/hooks/test-sync-with-main.sh` timed with `date +%s.%N`, the old suite a copy of HEAD's beside it, removed after). In the serial traced run `topology` fell from 23.1 s to 2.4 s and `stamp_hooks` from 8.9 s to 2.2 s (observed 2026-11-11, method: the trace above, after).
   - What is left: the script under test, about four fifths of the suite. Each fixture push reruns `push-checks`' Rust self-tests whether or not anything changed, about 0.4 s a push (observed 2026-11-11, method: the trace above), which a skip like the Python checks' would save, and that is the gate's push code (`rust/gate/crates/cohort/src/push.rs`), not the suite (observed 2026-11-11, method: the trace above). The suite's `WEIGHT` table, from 2026-10-17, is left to re-time on a quiet machine.

### T106 Approach (checklist part A)

1. **The goal, in the world.** The suite's own fixtures cost little beside the script it tests.
2. **The constraints.** FR-012 and SC-007: every case and assertion held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the trace and the timings above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of it.
5. **The order.** After T105 and T107.
6. **The exits.** Green: `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The alternated timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** In the script under test, then the fixtures built a case.
2. **Does the change remove work, or only move it?** Removes it: the fixture built once, not 32 times.
3. **What do you expect it to save, and why?** The fixture's time, measured above.
4. **How does the work grow?** With the cases' own runs, no longer with a fixture each.
5. **What did the before and after show, and under what conditions?** Two alternated runs each on a shared host, read as evidence.
6. **Did any map move?** No: no engine code changes.


<!-- plan-archive: T107 to T107 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-12 -->
### T109 (push-checks' Rust self-tests kept per binary, FR-012)

- **Approach**: `l7r-gate push-checks` (`rust/gate/crates/cohort/src/push.rs`) keeps a passed Rust self-test as it already keeps a Python one, against the version of `scripts/` and, for a Rust one, the gate binary as a file (`binary_id`), so the six run again only when the binary is rebuilt or the scripts move.

   **Decisions** (FR-012, SC-007):
   - Where the time went: the six Rust self-tests (file-scale, research-pointers, downloads, spec-lint, conflict, gate-stamp) ran on every push, 0.02-0.08 s each and 0.28 s of a 3.7 s push at a load of 0.5, while a Python self-test was already kept per version of `scripts/` (observed 2026-11-11, method: `l7r-gate measure push-check-times`).
   - What a Rust self-test depends on: five test the binary on fixtures written in code, and gate-stamp's hashes `.py` files through the tree's `codeid.py`, so the key is the `scripts/` version (the one a Python self-test is kept against) and the binary (observed 2026-11-11, method: each `selftest` function read).
   - The binary is keyed by its file, its path, inode, size and modification time to the nanosecond, which a rebuild writes anew (cargo writes a new file, and the wrapper touches it), rather than by its content, whose hash took 33 ms for the 15.6 MB binary, about a ninth of what keeping saves (observed 2026-11-11, method: `sha256sum` timed on `tool/l7r-gate`). A rebuild with the same bytes runs the self-tests once more, the safe direction. The binary is this process's own (`current_exe`), the one the wrapper's `$BIN` runs the rows on. A binary whose file cannot be read keeps nothing, and a failed self-test is never kept, as before.
   - The sync-with-main suite copies a template a case (T106), so its fixture clones started with nothing kept and most cases push once: the template's clone runs `push-checks` once, as a real clone has after its first push, so each copy keeps the self-tests (they are kept against the real tree's `scripts/` and binary, which every case runs).
   - Measured the same way before and after (SC-007): `push-checks` on this clone from the before tree (main without the change) and this one, alternated five times each after a warm run, 8.41-8.53 s before and 8.00-8.20 s after, and on this clone with the six kept or cleared, 3.56-3.69 s against 4.10-4.11 s at a load of about 5 (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t109/push_ab.sh 5`, and the keep file's six entries removed before each unkept run). The sync-with-main suite alone, alternated twice each, 15.8 s and 17.7 s before and 15.4 s and 15.1 s after at loads of 2.9-5.1, its parts running side by side, which spreads the 36 pushes' saving (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t109/suite_ab.sh`), all 138 checks passing.
   - The test: `a_passed_rust_self_test_is_kept_until_the_binary_or_the_scripts_change` - kept on a second push, run again when the binary's file is rewritten, when `scripts/` moves, with the cache off, and every time when the binary cannot be read.
   - What is left: `money-candidates` is 2.2 s of a real 3.7 s push at a load of 0.5, the push's largest row (observed 2026-11-11, method: `l7r-gate measure push-check-times`), a candidate for the GM.

### T109 Approach (checklist part A)

1. **The goal, in the world.** A push runs a Rust self-test only when the binary or the scripts it reads changed.
2. **The constraints.** FR-012 and SC-007: every self-test still run on any change that could break it, every verdict held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the timings above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of main.
5. **The order.** Before T108.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The alternated timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Six self-test processes a push.
2. **Does the change remove work, or only move it?** Removes it: the self-tests run once a binary.
3. **What do you expect it to save, and why?** Their time on every push, as the decisions above measure it.
4. **How does the work grow?** With rebuilds, no longer with pushes.
5. **What did the before and after show, and under what conditions?** Alternated runs on a shared host, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
### T108 (a core edit's coverage tests side by side, FR-012)

- **Approach**: `l7r-gate rust cover` (the coverage code moved to `rust/gate/crates/rustc/src/rustc/cover.rs`) builds a family's owed crates in one cargo call whose JSON names each crate's test binary, then runs every crate's tests and report in a report directory of its own, five crates at a time on this machine (`uncovered_each`).

   **Decisions** (FR-012, SC-007):
   - Where the time went after T105: each crate's coverage run built again (0.3-1.0 s each, 6.0 s in all), ran its tests through `cargo test`, which holds the family build directory's lock, and its report, one crate after another, the tests 17.2 s of a core edit's run and the checks crate 8.9 s of it (observed 2026-11-11, method: the `cover build` and `cover tests` lines of T105's `make static` logs).
   - Why they could not overlap: `cargo llvm-cov report` reads every test binary and every profile in its build directory, so each crate's run moved the other crates' binaries aside and cleared the last profiles (T92, T105). Each crate now gets a report directory of its own, holding a hard link to its test binary alone and the profiles its tests write, and the runs share nothing. Its tests run straight from the binary, as `cargo test` runs them: from the crate's directory, with `CARGO`, `CARGO_MANIFEST_DIR` and `CARGO_PKG_NAME` set, quietly, `CARGO` being the one cargo variable a test reads at run time (observed 2026-11-11, method: a search of the Rust sources for `env::var("CARGO`). The together build's JSON names each test binary (`json-render-diagnostics`, the compiler's errors still readable), so the per-crate builds go too, and the deletion of a crate's stale libraries and the moves aside go with them, a report directory holding nothing stale. A failed build of several crates is asked again a crate at a time, so the failure is the crate's that has it. `show-env` is asked once a family.
   - The same coverage: a report from such a directory against the old path's, for core, claims and checks, the lines each leaves unreached identical, and the functions never called identical for claims and checks. For core, they differ only in four closures of the guard's `sweep_dead`, outside core's own files, which the floor reads. Whether a test reaches them depends on what the temp directory holds at that moment. Every crate's own files are 100% covered both ways (observed 2026-11-11, method: `l7r-gate.sh rust uncovered` with `L7R_RUST_FRESH=1` on each crate in both trees, the lcov's zero `DA` and `FNDA` entries compared with the tree's path and the build hashes removed, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t108/zeros2.py`). Two runs of the old path already differ in hit counts, so the zero set is the bar, not identical bytes (observed 2026-11-11, method: the old path run twice on core, `cmp`).
   - How many at once: every owed crate at once took this 22-core machine's load to 31 and failed two crates' timing tests, the depiction bundle's 300 ms test crop timeout (a Python start) and the downloads lock test's branch (observed 2026-11-11, method: the after run's `make static` log, and the downloads crate alone three times clean). So the runs go a quarter of the cores at a time (`side_by_side`, 5 here). At five at a time the depiction test's 300 ms still failed in one of two core-edit passes, the same two tests at a load of 13.8, and passed in the other (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t108/runs.sh` twice with the timeout at main's 300 ms, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t108/keep300b-edit-core.log`), so its crop timeout is 1 s, under its slow page's 5 s sleep (a CONVENTION, the test's own constant, observed 2026-11-11, method: the logs above), which costs the slow page's test about 0.7 s more in a crate whose tests take 5-6 s beside the others (observed 2026-11-11, method: the runs' `cover tests bundle` lines). Starting the slowest crate first was tried and taken out: the checks crate already started in the first five, and the step stayed 15.0-16.4 s, bound by its tests, 8.9 s alone and 15-16 s beside four others (observed 2026-11-11, method: the runs' `cover tests` lines).
   - Measured the same way before and after (SC-007): a scratch clone of main (T109 in) and this clone, each after `make rust-test` and a green `make static`, each edit a one-line comment unique to the run, back to back. `make static` after a core edit took 49.7 s, 51.0 s, 52.0 s and 51.0 s before (four passes) and 40.2 s after with this code, and 36.7 s and 43.9 s in a pass that also ordered the crates slowest first (observed 2026-11-11, method: the runs below). After a claims edit it took 26.7-34.7 s before and 23.4 s and 25.0 s after, at loads of 5-13 (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t108/runs.sh <tree> <label>`, `date +%s.%N` around each `make static`). In the after run, the core edit's build of 17 crates took 4.1-7.8 s, against 11.8 s of builds before, and the tests and reports 15.0-16.4 s against 16.4 s of tests alone before, the reports then untimed (observed 2026-11-11, method: the same logs' `cover` lines).
   - The tests: the floor reads a report directory holding the crate's binary alone, gone after the run, the tests run from the crate's directory with cargo's variables, quietly, their profiles in that directory (`the_floor_reads_the_lines_from_the_crate_s_own_report_directory`). A family's builds go together, and a failed one is asked again crate by crate (`tests/cover.rs`). Every cargo call still runs from the tree's root.
   - What is left: the checks crate's tests are the step's floor, and two coverage runs on one clone at once still share its report directories, as they shared its build directory before.

### T108 Approach (checklist part A)

1. **The goal, in the world.** A core edit's coverage tests use the machine's cores, each crate's report reading its own run alone.
2. **The constraints.** FR-012 and SC-007: every crate's coverage verdict held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the timings and the report comparison above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of main.
5. **The order.** After T109.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The before and after timings above.
10. **Before moving a constant.** The depiction test's crop timeout, a test constant, raised for the load the change brings, as the decisions say.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Serial coverage runs, each building again and holding the build's lock.
2. **Does the change remove work, or only move it?** Both: the per-crate builds go, and the runs overlap.
3. **What do you expect it to save, and why?** The per-crate builds, and the tests' time beyond the slowest crate's.
4. **How does the work grow?** With the slowest crate's tests and the rest's over five at a time, no longer with the sum of all of them.
5. **What did the before and after show, and under what conditions?** Back-to-back passes on a shared, loaded host, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
### T99 (the arbiter crate's tests against FR-008's bar, FR-012)

- **Approach**: the cut of the transcript scan landed as T104; here the arbiter's bundle tests are given what they do not test - the record's owed list and the machine's transcripts - through two seams of the test build alone, and the one real computation of the owed list is its own test, under the round arbiter's ruling `ask:set-down-449-efficiency-round-2`, which reads: "(a) finish T99 by building the owed list once per test binary (a shared computed fixture, or a pre-built record or fixed git reader fed to the six tests), so each of the six arbiter tests runs under FR-008's [bar] with every output and verdict unchanged; if one cannot reach the bar without changing what the arbiter does at its git boundary, land T99 with its measured cut and name that test as remainder in the report rather than spend rounds on it."

   **Decisions** (FR-012, FR-008, SC-007):
   - Before: after T104 six tests took 0.14-0.43 s, `the_capped_round_cause` 0.43 s, `asks_reversals_red_gates_and_reviews` 0.30 s, `a_round_trigger_and_its_rounds` 0.26 s, `the_rare_paths_of_the_arbiters_bundle` 0.21 s, `a_batch_and_the_command_line` 0.15 s, `the_sections_rare_paths` 0.14 s, and the crate's tests 1.09 s (observed 2026-11-11, method: the test binary run once per test with `--exact` and `make rust-test CRATE=rust/gate/crates/arbiter`'s `finished in`). Each computed the record's owed list one to four times, about 35 `git` calls and 0.1 s a computation on a fixture repository it changes between them, so a shared computed fixture cannot serve them (observed 2026-11-11, method: `git` and `python3` wrapped by timing scripts ahead on `PATH`, 140 `git` and 8 `python3` calls for the slowest).
   - The fixed reader the ruling names: the one place the arbiter computes the owed list, a capped round's cause (`bundle/sections.rs`), now asks `owed_units`, which in the test build alone returns what a test gave it on its own thread (`GIVEN`, `#[cfg(test)]`, so the binary's build has no seam), else `record::owed::unanswered`. The five bundle tests that do not test the owed list give it an empty one, and the capped round's cause gives it an empty list and, for its unreadable-list case, an error, the owed crate's own tests testing the computation. The same for the spec rounds' transcripts (`bundle/reviews.rs`, `TRANSCRIPTS`): `asks_reversals_red_gates_and_reviews` reads an empty fixture folder, not the machine's 8,696 transcripts (observed 2026-11-11, method: `ls ~/.claude/projects/*/*/subagents/agent-*.jsonl | wc -l`), of which it tested only that the folder was there.
   - The real computation stays tested once: `the_capped_round_cause_reads_the_record_s_owed_list` computes the owed list on the fixture and finds `quote-check:0094#k` in the cause, the arbiter's own git boundary, which a given list would not test; it is the named remainder, 0.143 s, one computation and the fixture's repository (observed 2026-11-11, method: best of three runs of that test alone).
   - `asks_reversals_red_gates_and_reviews` held two concerns, an ask's bundle and the reversals, red gates and review rounds, and took 0.123 s run alone (observed 2026-11-11, method: best of three runs with `--exact`), so it is two tests, `an_ask_s_bundle_and_a_busy_out` and `reversals_red_gates_and_reviews`, each with its own fixture.
   - After, by the same method as before: every one of the crate's 34 tests runs under 0.1 s alone but the named remainder, the slowest of the rest 0.097 s, the two split tests 0.084 s and 0.086 s, `a_round_trigger_and_its_rounds` 0.081 s, and the crate's tests took 0.18 s together, every test passing (observed 2026-11-11, method: each test run alone with `--exact`, best of three, and `make rust-test CRATE=rust/gate/crates/arbiter`'s `finished in`).

### T99 Approach (checklist part A)

1. **The goal, in the world.** The arbiter crate's tests cost well under a second, each under FR-008's bar alone but the one real computation of the owed list.
2. **The constraints.** FR-008 and FR-012, under the round arbiter's ruling.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the timings and the call counts above; the ruling `ask:set-down-449-efficiency-round-2`.
4. **Do they describe the world here?** Measured on this clone.
5. **The order.** After T104, which carries the cut, and before the set-down.
6. **The exits.** Green: `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The per-test times above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** One transcript scan, now cut, and repeated `git` reads of the record's owed list.
2. **Does the change remove work, or only move it?** T104 removed the scan; the rest is named, not moved.
3. **What do you expect it to save, and why?** The crate's tests' time, measured above.
4. **How does the work grow?** With the owed list's families and the computations a test makes.
5. **What did the before and after show, and under what conditions?** Each test run alone with `--exact`, before once and after best of three, on a throttled host, read as evidence.
6. **Did any map move?** No: no engine code changes.


<!-- plan-archive: T100 to T100 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
### T101 (every temporary directory a check or test makes is removed, FR-013)

- **Approach**: one temporary-directory type, `TempDir` in `l7r_guard::shared::tempdir`, whose `Drop` removes it, held by every test helper and production site that made a directory under the temp directory; and the runners themselves fail a crate or a hook suite that leaves anything behind.

   **Decisions** (FR-013, SC-008):
   - The leak: the GM's laptop found about 329,000 leftover `l7r-gate-check-*` and `l7r-guard-*` directories in `/tmp`, roughly 126 GB, back to early October (observed 2026-11-11, method: the laptop session's count and `du`, relayed in `request.md`). Nearly all came from one test helper, `l7r_gate_core::checks::scratch(tag)`, which about 300 tests call and which removed nothing; about 90 other test helpers, about 25 guard test sites and a few production paths (the stamp selftest, preflight, the probe, the cohort counter, the claims `temp_dir`, the hook bench, the guard's `--self-check`) made their own and removed them on success at most (observed 2026-11-11, method: a read-only `git grep` inventory of every `temp_dir()`, `mktemp` and `mkdtemp` under `rust/`, `scripts/` and `tests/`).
   - `TempDir` (`new(tag)`, `path()`, `Deref<Target = Path>`, `AsRef<Path>`, `keep()`), with `Held<T>` for a helper that returns a path inside the directory, and `beside_binary(name)` for the few things one test process shares (a log directory, a fixture template, the tests' bundle root): `<temp dir>/l7r-test-scratch/<name>`, emptied when a process first asks, which under `make rust-test` is inside the run's own temp directory, so the runner removes it on exit with that directory, and both runners' leak checks (`rustc.rs`, and `hookrun.sh`, whose suites run the guard's test binary) pass over that one name only because each removes it next (a test makes it beside two leaks and finds only the two named). No crate panics with `abort`, so `Drop` runs on a return, a `?` and a test's panic, which a unit test proves inside `catch_unwind`. The guard's `--self-check` drops its directory before `process::exit`, which skips destructors.
   - Tests no longer write into the real `/tmp/l7r-check`; the production bundle root, whose bundles review agents read later, is unchanged, as are `delta.rs`'s `Scratch` and `PromptFile`, which already removed themselves.
   - THE PIN, in the tooling rather than in anyone's memory: `rustc.rs` runs each crate's `test`, `test-counters`, `test-no-counters` and `cover` with `TMPDIR` set to a fresh directory of that run (`/tmp/l7r-rust-tests-<crate>-*`) and fails the crate on anything left in it, naming each entry and the fix, then removes the directory, so a test killed by SIGKILL, whose `Drop` never ran, leaves nothing past the run either. `tests/hooks/hookrun.sh` does the same for each hook suite with a `LEAK:` line. The directory sits under `/tmp`, not the target, because guards that recognize a test fixture by its `/tmp/` path broke otherwise.
   - The pin bites: before the sites moved, core went red with "left 29 entries", and with one `scratch("git-text")` given `.keep()` after, core went red naming it, and with `$GUARD_LOG_ROOT` taken out of the discard suite's trap, that suite went red with `LEAK:` (observed 2026-11-11, method: `make rust-test CRATE=rust/gate/crates/core` and `bash tests/hooks/hookrun.sh` on the scratch clone, logs `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t101-pin-red.log` and `t101-pin-red2.log`).
   - The shell suites the pin caught: the discard and pair suites each set a second `trap ... EXIT` that replaced their first, no-poll made a stderr file per part it never removed, `parts.sh` now removes its work directory on an exit, an interrupt or a TERM, its trap appended to the suite's own EXIT trap and the suite's put back after, each part's directory made inside it, and an interrupt or a TERM stops the parts first, so a suite run alone and stopped leaves nothing (a new suite, `tests/hooks/test-parts.sh`, ends a parted suite with TERM and finds nothing left, the suite ending 143 and its own trap run, and went red against the old `parts.sh`), `test-gate-hooks.sh`'s trap covers its per-case directories, `sync-with-main.sh` removes `gdir` on an interrupt, and `collect_cost.py` uses `TemporaryDirectory`.
   - Measured: a full `make rust-test FRESH=1` and `make hooks-test HOOKS_ALL=1` left no `l7r-*` or `tmp.*` entry newer than a marker made before them, and nothing in `/tmp/l7r-check` changed (observed 2026-11-11, method: `find /tmp -maxdepth 1 -newer` the marker on the scratch clone).
   - INT and TERM remove a process's directories too (`rust/guard/src/shared/tempdir/signals.rs`): a process ended by a signal it does not catch never runs a `Drop`, so the first `TempDir` of a process catches INT and TERM, its handler only writing the signal's number to a pipe, which a handler may do, and a thread on that pipe removes every `TempDir` the process still holds and exits as the signal would (128 + its number); a signal the process was started ignoring, a background job's INT, stays ignored. It is the crate's one use of `unsafe`, `pipe(2)`, `write(2)` and `signal(2)` from the C library std already links, each with its SAFETY note. A test runs itself as a child that makes a `TempDir` and a kept one, sends it TERM and then INT (INT only where the test itself was not started ignoring it), and finds the child ended 143 and 130, its held directory gone and its kept one there; with the registration knocked out it went red (observed 2026-11-11, method: `make rust-test CRATE=rust/guard` with `signals::hold` commented out, then restored).
   - Only a SIGKILL, which no process can catch, leaves a process's directories, and the next of its kind removes them: `TempDir` names its directory `l7r-{tag}-p{pid}-{seq}`, and every `TempDir::new` first removes each directory of that form and tag in its parent whose pid has no `/proc` entry and which has not changed in three hours, the GM's "don't touch dirs younger than a few hours (a running gate may own them)", since a killed process's children can still be working in its directory. `tests/hooks/hookrun.sh` names its suite directory `l7r-hooks-suite-<guard>-p<pid>.*`, removes those of a gone pid unchanged in three hours before each run, and on an INT or a TERM stops the suite and exits through its EXIT trap. Only the new form is matched, the tag and both numbers exactly, so the directories the checks left before T101 (`l7r-{tag}-{pid}-{seq}`, no `p`) are never touched, being the GM's laptop session's to delete; a pid reused by a live process keeps its directory, the safe way to be wrong; and every process sharing this `/tmp` is in this container's one pid namespace. A unit test sweeps a fixture of a gone pid's old and young directories, a live pid's, another tag's, the old form's and malformed names, and `tests/hooks/test-parts.sh` runs `hookrun.sh` beside a gone run's old and young directories, a live run's and an old-form one, and stops one with TERM, two of its cases red against T101's earlier `hookrun.sh`.
   - Left: a SIGKILLed process's directories last until the next of its kind runs three hours on.
   - Carried onto T96 and T103: `rustc.rs`'s cargo call keeps T96's run from the tree's root with T101's `TMPDIR`, and T103's sweep tests hold their fixture in a `TempDir`, `make rust-test CRATE=rust/guard` 511 passed under the pin (observed 2026-11-11, method: that command on this clone).

### T101 Approach (checklist part A)

1. **The goal, in the world.** A check or a test leaves nothing in the temp directory, and the runners refuse one that does.
2. **The constraints.** FR-013 and SC-008; the check bundles review agents read stay where they are.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the inventory and the measurement above.
4. **Do they describe the world here?** Measured on a scratch clone of this tree, then merged here.
5. **The order.** After T96 and T103; T102 next.
6. **The exits.** Green: `make static`, `make rust-test` and `make hooks-test HOOKS_ALL=1` green with the pin on, `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The marker measurement above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** no.


<!-- plan-archive: T102 to T102 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->

<!-- plan-archive: T104 to T99 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->

<!-- plan-archive: T105 to T105 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->
<!-- plan-archive: T106 to T106 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T109 to T109 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T108 to T108 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

### T110 (rustfmt kept per crate, FR-012)

- **Approach**: `l7r-gate rust format --check` keeps each crate's green result as lint and coverage already do, keyed on what rustfmt reads (`Reads::Own` in `rust/gate/crates/rustc/src/rustc/kept.rs`).

   **Decisions** (FR-012, SC-007):
   - The cost: the format check kept nothing (`kept_reads` named no reads for it), so every `make static` ran rustfmt over all 19 crates, 2.1 s of a core edit's 29.1 s on a quiet machine (observed 2026-11-11, method: each line of `make static` timestamped after a one-line comment edit of core).
   - The key: the crate's own files, the workspace's manifests and toolchain files (`WORKSPACE`, as every key) and rustfmt's configuration under its usual names (none tracked today), with the compiler's version, but not the crates it builds from, which rustfmt does not read. A crate's files are those its directory holds most nearly, so the binary's key stands over its nested crates' edits.
   - Only a check's green result is kept. `make format`, which rewrites files, keeps nothing, because its key was read before the rewrite, and keeping it would mark the unformatted text green. A rewrite's own run still skips a crate whose key stands, since that text was checked clean.
   - Measured the same way before and after (SC-007): `rust format --check` over every crate 2.32 s, then 0.16 s and 0.17 s with nothing changed, 0.78 s after a one-line core edit (core alone run) and 0.66 s after its revert (observed 2026-11-11, method: `date +%s.%N` around `l7r-gate.sh rust format --check`, the first run keeping nothing, at a load of about 1). `make static` with nothing changed 1.36-1.39 s, three runs (observed 2026-11-11, method: the same, at a load of about 2).
   - The tests: the format key stands over a dependency's edit and moves with the crate's own file, rustfmt's configuration and `Cargo.lock` (`a_nested_crate_owns_its_files_and_a_dependency_s_dependency_moves_the_key`), and a check is kept and a rewrite is not (`a_format_check_is_kept_and_a_rewrite_is_not`). The kept-result tests moved to `rustc/tests/kept.rs`, the tests file over the 1,000-line bar.

### T110 Approach (checklist part A)

1. **The goal, in the world.** rustfmt runs only on a crate whose files changed.
2. **The constraints.** FR-012 and SC-007: every format verdict held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the timings above.
4. **Do they describe the world here?** Measured on this clone.
5. **The order.** First of T110-T116.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** rustfmt over every crate on every run.
2. **Does the change remove work, or only move it?** Removes it: an unchanged crate is not formatted again.
3. **What do you expect it to save, and why?** The format step's time on every crate that did not change, measured above.
4. **How does the work grow?** With the crates edited, no longer with all of them.
5. **What did the before and after show, and under what conditions?** One run each on a quiet host, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
### T111 (a coverage pass records the crate's test result, FR-012)

- **Approach**: when `l7r-gate rust cover` passes a crate whose `cargo test` is its unit tests alone, it keeps the crate's `test` key as green too (`Verdict::keep_tests`, `unit_tests_only` in `rust/gate/crates/rustc/src/rustc/kept.rs`), so `make rust-test` after `make static` runs no test the coverage run already ran.

   **Decisions** (FR-012, SC-007):
   - Why a coverage pass answers for the tests: the coverage run builds the crate's library tests (`cargo test --no-run --lib`) with the coverage flags and runs every one of them. Its build differs from the plain one only by the instrumentation and `cfg(coverage)`, and no code in `rust/` reads `cfg(coverage)` (observed 2026-11-11, method: a search of the Rust sources for `cfg(coverage)` and `cfg(not(coverage))`). So the tests that pass instrumented pass plain.
   - Where it does not: `cargo test` also builds and runs a crate's binaries, integration tests, examples, benches and doctests, which the coverage run does not. A crate holding any of them (`src/main.rs`, `src/bin`, `tests`, `examples`, `benches`, a `[[bin]]`-style table in its manifest, or a doc comment with a code block, fenced or indented: rustdoc runs an indented block too, and a doc line indented four spaces past its marker's own starts one after an empty doc line or opening a doc comment, while inside a paragraph it continues the paragraph, as markdown reads it) keeps no test result from a coverage pass. That leaves out `rust/guard`, `rust/gate`, `rust/phases` and `rust/gate/crates/rustc`, the four with a binary, and none has the others (observed 2026-11-11, method: each crate's directory listed, and its sources searched for a fenced doc comment and, by the rule above, an indented block; the indented doc lines in `claims` and `downloads` continue a paragraph).
   - Only the test key is kept, the one `make rust-test` asks first. Asking the second key, over the plain test binaries, would build them, the cost this saves. The key is the same one `make rust-test` computes, from the same inputs the coverage run read, so any change since moves it.
   - Measured the same way before and after (SC-007): on a scratch clone of main (T110 in) and this clone, after a one-line core edit and a green `make static`, `make rust-test` took 18.3 s before, 11 crates' results standing, and 4.2 s after, 18 standing, and after the edit's revert 0.4 s and 0.3 s, all 19 standing (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t111/ab.sh <tree> <label>`, `date +%s.%N` around `make rust-test`, at loads of 9-13).
   - The tests: which crates' `cargo test` is their unit tests alone (`a_crate_whose_unit_tests_are_its_whole_cargo_test`), and a coverage pass keeps the tests of such a crate and not of one with a binary (`a_coverage_pass_keeps_the_tests_of_a_crate_with_unit_tests_alone`).

### T111 Approach (checklist part A)

1. **The goal, in the world.** A crate's tests run once after an edit, whichever of the two checks asks first.
2. **The constraints.** FR-012 and SC-007: every test verdict held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the search and the timings above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of main.
5. **The order.** After T110.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Each owed crate's tests run twice, plain and under coverage.
2. **Does the change remove work, or only move it?** Removes it: the plain run is not repeated where the coverage run answered.
3. **What do you expect it to save, and why?** The plain test runs of the crates the coverage run covered, measured above.
4. **How does the work grow?** With the crates with a binary, no longer with every owed crate.
5. **What did the before and after show, and under what conditions?** One run each on a loaded host, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
### T112 (comment-insensitive keys, FR-012)

- **Approach**: a crate's lint, test and coverage keys read each Rust file by its code, its text without its plain comments (`code_text`, `rust/gate/crates/rustc/src/rustc/kept/code.rs`; `code_ids` and `verdict_key_with` in `kept.rs`), so a comment-only edit moves none of them.

   **Decisions** (FR-012, SC-007):
   - The cost: a one-line comment added to core moved every gate crate's keys and re-ran 29.1 s of `make static` on a quiet machine, no verdict depending on it (observed 2026-11-11, method: each line of `make static` timestamped after such an edit).
   - What a comment cannot change: clippy's verdict, the tests' and the coverage floor's. What stays in the code: doc comments (`///`, `//!`, `/** */`, `/*! */`), which clippy lints and rustdoc runs, and every line but one a removed comment left empty, so blank lines, which a lint can read, still move a key. Clippy's `too_many_lines` counts no comment line (observed 2026-11-11, method: a scratch crate's function of 98 code lines and 10 comment lines drew no warning under `-W clippy::too_many_lines`, one of 102 code lines did). Nothing in `rust/` uses `line!()`, includes a `.rs` file or reads its own source undeclared (observed 2026-11-11, method: a search for `line!()`, `include_str!` of a `.rs` and `include!`; the undeclared reader is refused already, T93).
   - What keeps the whole text: rustfmt, which formats comments, and the dead check, which counts a word in a comment as a use (T100's family key), and any file a crate's tests declare they read, whose comments they may read. The checks crate declares the whole tree (`reads = ["."]`), so its tests' keys still move with any comment, its coverage 10.4 s of the comment edit's run below (observed 2026-11-11, method: that run's `cover tests checks` line). That is T116's subject, and keeping it here holds its verdict.
   - The code is read by a small lexer that takes a string, raw string, byte string, char literal or lifetime as such (a `//` inside a literal is no comment) and nests block comments as Rust does. Each file is read from the work tree once a run, its id `code:` and the sha of its code. The keys of every crate move once, at the first run after this lands.
   - Measured the same way before and after (SC-007): on a scratch clone of main (T111 in) and this clone, each after `make rust-test` and a green `make static`, `make static` after a one-line comment edit of core took 37.5 s before and 17.5 s after, 10.4 s of it the checks crate's coverage, after its revert 11.0 s and 3.3 s, and with nothing changed 1.5-1.6 s and 1.7-1.8 s, at loads of 11-19 (observed 2026-11-11, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t112/ab.sh <tree> <label>`, `date +%s.%N` around each `make static`). After the edit, lint, format and coverage kept 18 of 19 crates (observed 2026-11-11, method: the run's `unchanged` lines counted).
   - The tests: the lexer's cases (`kept/code/tests.rs`), and a comment-only edit moving no lint, test or coverage key while moving format's and dead's and a declared read's (`a_comment_only_edit_moves_no_lint_test_or_coverage_key`).

### T112 Approach (checklist part A)

1. **The goal, in the world.** A comment-only edit re-runs only the checks that read comments.
2. **The constraints.** FR-012 and SC-007: every verdict held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the experiment, the searches and the timings above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of main.
5. **The order.** After T111.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Every check of every crate built on an edited file, though the edit was a comment.
2. **Does the change remove work, or only move it?** Removes it: the checks a comment cannot change do not run.
3. **What do you expect it to save, and why?** A comment edit's lint, test and coverage reruns, measured above.
4. **How does the work grow?** With code edits, no longer with comment edits.
5. **What did the before and after show, and under what conditions?** One back-to-back run each on a loaded host, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
### T113 (the dependents' lint keyed on a crate's public interface, FR-012)

- **Approach**: a crate's lint key reads each crate it builds from by that crate's interface: its code (T112) with the bodies of the functions no other crate can see into taken out (`interface_text` beside `code_text` in `rust/gate/crates/rustc/src/rustc/kept/code.rs`). The crate's own files, and every other check's key, stay as they are. This is the one change of T110-T116 that is not exact, so its design is reviewed before any code (the GM 2026-11-11, `request.md`).

   **Decisions** (FR-012, SC-007):
   - The cost: after a core edit the 16 crates built on core re-linted for 8.5 s of clippy's 10.6 s, core alone 1.4 s (observed 2026-11-11, method: `l7r-gate.sh rust lint --crate rust/gate/crates/core` timed after a one-line edit of core, then `l7r-gate.sh rust lint` for the rest, on a quiet machine).
   - Why another crate's body cannot move a dependent's lint: clippy and rustc lint the crate being checked, its own code, in a check build that does not generate code, so another crate's function body is never linted or monomorphized there. What a dependent's lint reads of a dependency is its items: signatures, types, traits and impls, attributes (`#[must_use]`, `#[deprecated]`), constants and statics with their values, macros, and its docs.
   - What is taken out: the body of a `fn` (free, in an `impl` or a trait's default) that is not `const` or `async`, whose signature holds no `impl` (a returned `impl Trait`'s auto traits follow from the body), and whose body holds no `impl` block or `macro_rules!` (an impl or an exported macro inside a body is seen crate-wide). The body is replaced by `{}`. Everything else stays as T112's code: doc comments, attributes, every item outside a body, a `macro_rules!` whole (its `fn`s are not read as functions). A file the lexer cannot read to its end (an unclosed brace or literal) keeps its whole code.
   - What it is not: exact. A lint in a dependent that reads a dependency's body through the compiler (a nursery or restriction lint, none enabled 2026-11-11: the workspace denies `all` and `pedantic` and names `too_many_lines` and `allow_attributes_without_reason`) would go unrun after a body-only edit, and so would a body change the rules above misread as private. Both fail open: the lint stays unrun on every run until the dependent's own files or the dependency's interface move. The alternatives priced: an interface from `syn`'s full parser (`syn` 3 is in `Cargo.lock` only as `serde_derive`'s, built without `full`; adding it changes a shared dependency's build and fails closed on syntax it cannot parse), or rustc's `.rmeta`, which moves with any line shift (spans), so it saves little.
   - Where it applies: the lint key alone, and only for the files of the crates a crate builds from. The crate's own files are read by their code (T112), so its own lint still runs on any code edit. Tests, coverage, format and dead keep their keys, since a body change does change what a dependent's tests do.
   - What it saves, expected: on an edit of core that changes only function bodies, the 16 dependents' lint, 8.5 s (observed 2026-11-11, method: as above). An edit of a signature, a type or a constant moves the interface and runs them as now.
   - A lint key reads no declared test read: a crate's `[package.metadata.l7r] reads` names what its tests read at run time, and a lint runs no test. T112 applied it to every key, so the checks crate (`reads = ["."]`) still re-linted on any edit anywhere. Its tests' and coverage keys keep it. A declared read only ever chose a `.rs` file's full id over its code id in a lint key, never added an input to it. What a lint build reads at compile time beyond the crate's code is its build script, a procedural macro it uses, and the files it includes: no workspace crate has a build script, `[build-dependencies]` or `proc-macro = true`, and no Rust file includes a `.rs` file (observed 2026-11-12, method: `grep -rln` over every `Cargo.toml` under `rust/` for `proc-macro`, `proc_macro` and `[build-dependencies]`, `find rust -name build.rs` (one hit, `rust/phases/src/field/build.rs`, a module, the crate's root holding none), and `grep -rn` for `include_str!`, `include_bytes!` and `include!` over every `.rs`). So no dependency of the rule is a procedural macro or a build dependency, whose bodies would run in the dependent's build.
   - Found and fixed: the files a crate's sources include sit outside its directory where they are another crate's (`guard` includes the record crate's `html5_entities.tsv`, the checks crate `guard`'s `house_style_words.tsv`), and no key of the including crate read them, so a kept test result stood over a changed table (observed 2026-11-12, method: the include census above against `inputs`). A test or coverage key now reads every file its Rust files include (`included`, read in the same pass as the code ids); a lint, format or dead key does not, since an included data file changes none of them.
   - Measured the same way before and after (SC-007): on a scratch clone of main (T112 in) and this clone, each after `make rust-test` and a green `make static`, `make static` after a body-only edit of core (`write_executable`'s draft name, unique a run) took 37.5 s before, lint keeping 2 of 19 crates, and 30.1 s after, keeping 17, and after its revert 3.5 s and 4.2 s, at loads of 15-22 (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t113/ab.sh <tree> <label>`, `date +%s.%N` around each `make static`, the `lint unchanged` lines counted). The two the after run re-linted were core and the checks crate, the second by the declared read above. With that fixed, `l7r-gate.sh rust lint` after such an edit took 1.95 s, keeping 18 (observed 2026-11-12, method: `date +%s.%N` around the command), against 10.6 s for the lint step of a core edit before (observed 2026-11-11, method: the timestamped `make static`).
   - The tests: the interface's cases (a body taken out, each kept case, a `macro_rules!`, an unclosed file, a brace inside a char or string), and a body-only edit of a dependency moving no lint key of its dependent while moving its test and coverage keys and its own lint key, and a signature edit moving the dependent's lint key; a declared read moving no lint key; an included file moving the test and coverage keys and not the lint key (`a_test_key_reads_what_the_crate_s_sources_include`).

### T113 Approach (checklist part A)

1. **The goal, in the world.** A body-only edit of a shared crate re-lints that crate alone.
2. **The constraints.** FR-012 and SC-007, with the GM's acceptance that this one is not exact and its design reviewed first.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the lint split above.
4. **Do they describe the world here?** Measured on this clone.
5. **The order.** After T112, whose lexer it reuses.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** A body-only core edit's `make static`, before and after.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Clippy over every crate built on an edited one.
2. **Does the change remove work, or only move it?** Removes it: a dependent whose view of the edit is unchanged is not re-linted.
3. **What do you expect it to save, and why?** The dependents' lint on a body-only edit, as the decisions measure it for core.
4. **How does the work grow?** With interface edits, no longer with every edit of a shared crate.
5. **What did the before and after show, and under what conditions?** One back-to-back run each on a heavily loaded host, and the lint step alone after the fix, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
### T114 (the push's money-candidates check, FR-012)

- **Approach**: `record money-candidates` (`rust/gate/crates/record/src/record/money.rs`) scans the record's question pages side by side, dealt round the machine's cores and put back in page order, where it scanned them one after another.

   **Decisions** (FR-012, SC-007):
   - Where the time went: the check scans every one of the record's 1,652 question pages (18 MB) with its regular expressions, one page after another on one core, 2.07-2.19 s alone and 2.46 s of a 3.68 s push (observed 2026-11-11 and 2026-11-12, method: `l7r-gate measure push-check-times`, and `date +%s.%N` around `l7r-gate.sh record money-candidates --check` three times, `ls research/questions | wc -l`, `du -sh`). Each page's scan (`scan`) reads that page, and its notes page's base, alone.
   - Side by side rather than skipped: a skip keyed on what the check reads (the pages, the conversion table, the backfill list, the binary) would hold its verdict too, but would still cost the full scan after any record edit, the pushes that carry them. Running the pages side by side removes the time on every push, and changes nothing the check computes.
   - The same output: the pages are dealt round the cores (page i to core i mod the core count, so long runs of heavy pages are shared) and their amounts put back in page order before the stable sort that orders the listing, so it sees the same sequence as before. `money-candidates` with `--all --context`, with `--check` and with nothing gave byte-identical stdout, stderr and exit before and after (observed 2026-11-12, method: each run before and after the change into a file, `cmp`).
   - Measured the same way before and after (SC-007): `money-candidates --check` alone 2.08-2.19 s before and 0.37-0.81 s after, at loads of 7-9 (observed 2026-11-12, method: `date +%s.%N` around it, three runs before and five after). In the push's timing, the row 2.46 s before and 0.79 s after, the whole push in one process 3.68 s and 2.28 s (observed 2026-11-11 and 2026-11-12, method: `l7r-gate measure push-check-times`, at loads of 6.5 and 6.8).
   - The tests: the record crate's money tests, which run `amounts` over fixture pages, unchanged and green, and every line of the change covered.

### T114 Approach (checklist part A)

1. **The goal, in the world.** The push's money check costs a fraction of a second.
2. **The constraints.** FR-012 and SC-007: its output byte-identical.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the timings and the output comparison above.
4. **Do they describe the world here?** Measured on this clone.
5. **The order.** After T113.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** The pages' regular expressions, one page after another.
2. **Does the change remove work, or only move it?** Moves it onto idle cores: the same scans, side by side.
3. **What do you expect it to save, and why?** Most of the scan's time, the cores being idle during a push.
4. **How does the work grow?** With the record's pages over the cores.
5. **What did the before and after show, and under what conditions?** A few runs each on a loaded host, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
### T115 (the full hook run's two longest suites, FR-012)

- **Approach**: the work under the two suites goes side by side: the record's pages parsed across the cores before `Record::of` reads them (`warm` in `rust/gate/crates/core/src/record/units.rs`), which each record gate of the entry-gate suite runs twice, and the push's checks run at once, their output shown in the table's order (`run_checks` in `rust/gate/crates/cohort/src/push.rs`), which each of the sync-with-main suite's pushes runs.

   **Decisions** (FR-012, SC-007):
   - Where the entry-gate suite's time went: a clone of the tree and five runs of the record gate, each about 2 s, its `record-owed --unanswered` 1.45-1.51 s with nothing changed and 1.70-1.85 s with one page edited, parsing every one of the record's 1,652 pages on one core, and two runs of its answer step, 3.9 s (observed 2026-11-12, method: the suite under `bash -x` with `EPOCHREALTIME` in `PS4`, the gaps summed by line, and `date +%s.%N` around `record-owed`). The parses are kept by text, so the merge base and the tree share them; the table was locked while a page parsed, so the lock is now taken only to look up and to keep, and every page is parsed into it side by side before the record is read in order, which reads the same parses in the same order.
   - Where a push's time went: `push-checks` was 0.82 s of a fixture push's 1.33 s, its rows one process after another, each reading the clone and writing nothing another row reads (the two memo presets and the ledger check each keep a file of their own, by an atomic rename) (observed 2026-11-12, method: T106's trace driver on one direct push, and each row's writes read in its script). The rows now start at once; then, in the table's order, each row's output is shown and the first refusal ends the run with the shell's line as before. A row after a refusal ran, but shows nothing and keeps nothing (a self-test after it is not kept), and a row's stdout is shown before its stderr, where they could interleave.
   - The same outputs: `record-owed` with no flags, `--unanswered` and `--slugs`, on an empty delta and with a page edited, byte-identical between the old binary and the new on this clone (observed 2026-11-12, method: each run into a file from both trees' binaries against this clone, `cmp`). The sync-with-main suite's 138 checks and the entry-gate suite's 13 pass.
   - Measured the same way before and after (SC-007), on a scratch clone of main (T114 in) and this clone. `record-owed --unanswered` with a page edited took 1.71-1.74 s before and 1.21-1.23 s after (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t115/ab.sh`, the two trees alternated, `date +%s.%N` around each, at loads of 4-8). `push-checks` on this clone took 6.6-6.7 s before and 5.0-5.3 s after, five runs each (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t115/ab.sh`, the two trees alternated, `date +%s.%N` around each, at loads of 4-8). The sync-with-main suite alone took 10.3 s and 11.0 s before, 9.2 s and 9.7 s after (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t115/ab.sh`, the two trees alternated, `date +%s.%N` around each, at loads of 4-8). The entry-gate suite alone took 17.8 s and 19.3 s before, 17.9 s and 13.4 s after (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t115/ab.sh`, the two trees alternated, `date +%s.%N` around each, at loads of 4-8). Inside the full hook run (`make hooks-test HOOKS_ALL=1`), sync-with-main took 51.9 s and 52.9 s before, 49.1 s and 48.5 s after, and entry-gate 47.8 s and 47.0 s before, 43.0 s and 44.3 s after (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t115/ab.sh`, the two trees alternated, `date +%s.%N` around each, at loads of 4-8).
   - What did not move: the full hook run itself, 64.8 s and 64.4 s before, 64.6 s and 64.2 s after (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t115/ab.sh`, the two trees alternated). It runs eight suites at a time and is not bound by the cores: 762% of 22 cores' 2,200%, its kernel time 243 s against 223 s of user time, and twelve suites at a time took 72.8 s, sixteen 76.3 s, against 64.1 s at eight (observed 2026-11-12, method: `/usr/bin/time` around `make hooks-test HOOKS_ALL=1` with `HOOKS_JOBS` 12, 16 and 8). The sync-with-main suite alone spent 38 s of user and 38 s of kernel time across its parts, the entry-gate suite 14 s and 6 s (observed 2026-11-12, method: `/usr/bin/time` around each). So the run waits on something the suites share in the kernel, which their wall time does not show; it is left measured, a candidate for the GM, not changed here. The wrapper `l7r-gate.sh` costs 18 ms a call with the binary's start, 4 ms of it its staleness walk, so it is not it (observed 2026-11-12, method: twenty no-op calls timed).
   - The tests: a refusal's shell line is the run's verdict and a self-test after it keeps nothing (`the_runner_stops_at_the_first_refusal_with_the_shell_s_line`); the record's units unchanged in every core and owed test; the two suites green.

### T115 Approach (checklist part A)

1. **The goal, in the world.** The two longest hook suites, and what they run on every push, take less time.
2. **The constraints.** FR-012 and SC-007: every output and verdict held.
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the traces, the timings and the output comparison above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of main.
5. **The order.** After T114.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The timings above.
10. **Before moving a constant.** None moved; eight suites at a time kept, measured above.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** The record's pages parsed on one core, and a push's checks one after another.
2. **Does the change remove work, or only move it?** Moves it onto idle cores: the same parses and checks, side by side.
3. **What do you expect it to save, and why?** The suites' and a push's waiting, measured above; not the full run's, which is bound elsewhere.
4. **How does the work grow?** With the record's pages and the push's rows over the cores.
5. **What did the before and after show, and under what conditions?** Alternated runs on a loaded host, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
### T116 (the checks crate's coverage tests, FR-012)

- **Approach**: the one whole-tree test that made the checks crate's coverage run slow, `every_pointer_in_the_repository_resolves_to_a_fragment`, is left out of the coverage build (`#[cfg(not(coverage))]`) and runs in the plain test run, which `make rust-test` owes the crate after every coverage pass; a fixture test reaches the one line only it reached.

   **Decisions** (FR-012, SC-007):
   - Where the time went: one test of the crate's 98 took 8.25 s under the coverage build and 0.27 s plain, every other at most 0.46 s, the whole instrumented run 7.5 s (observed 2026-11-12, method: each test run alone with `--exact` from the coverage build's test binary and from the plain one, `date +%s.%N` around each). It checks every pointer in the whole repository, the regular expressions it runs on every file instrumented as generic code instantiated in this crate (T100 instruments the workspace's crates, and a dependency's generic code compiled into one of them is theirs).
   - Why it can leave the coverage build: it checks the tree, not the code, every line it reaches but one reached by the crate's fixture tests, and that one, the sort of the alternation's names, reached only with two names or more, which the real tree alone gave (observed 2026-11-12, method: `l7r-gate.sh rust uncovered` with the test ignored). `alternation` now takes a `Vec`, so it has one instantiation, and `the_alternation_puts_a_longer_name_first` reaches it. The crate's coverage is 100% without the whole-tree test (observed 2026-11-12, method: the same, after).
   - Why it still runs: the plain `make rust-test` runs it, and T111 keeps no test result from a coverage pass for a crate that reads `cfg(coverage)`, so the plain run stays owed after every coverage pass. The workspace declares the cfg (`[workspace.lints.rust] unexpected_cfgs`, `check-cfg = ["cfg(coverage)"]`), which `cargo llvm-cov` sets, so the lint does not refuse it.
   - The crate's declared reads stay the whole tree (`reads = ["."]`): its tests read the tree (the pointers, the file sizes, the record's pages), so any edit still re-runs its tests and coverage, now about 1.5 s, the coverage run 0.7 s (observed 2026-11-12, method: the coverage run's `cover tests checks` line). A narrower list would have to name every path those tests read.
   - Measured the same way before and after (SC-007), a scratch clone of main (T115 in) and this clone back to back (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t108/runs.sh <tree> <label>` and `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t113/ts.sh <tree> <label>`, `date +%s.%N` around each `make static`). After a one-line comment edit of core, `make static` took 18.2 s before and 9.9 s after, the checks crate's coverage 10.7 s and 0.9 s, at loads of 13 and 23 (observed 2026-11-12, method: as above). After one of claims, 16.8 s and 7.0 s (observed 2026-11-12, method: as above). After a body-only code edit of core, 30.3 s and 23.5 s, its coverage tests and reports 15.8 s and 7.7 s, the checks crate's 15.6 s and 3.3 s, at loads of 19 (observed 2026-11-12, method: as above).

### T116 Approach (checklist part A)

1. **The goal, in the world.** The checks crate's coverage no longer sets the floor of a core edit's coverage step.
2. **The constraints.** FR-012 and SC-007: every verdict held, the crate's coverage whole (the floor's rule).
3. **Where each comes from.** G: the GM's words of 2026-11-11 in `request.md`; O: the per-test timings and the coverage runs above.
4. **Do they describe the world here?** Measured on this clone and a scratch clone of main.
5. **The order.** Last of T110-T116.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The timings above.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** One whole-tree test under the coverage build's instrumentation.
2. **Does the change remove work, or only move it?** Removes it from the coverage run: the test runs once, plain.
3. **What do you expect it to save, and why?** The test's instrumented time, less its plain time, measured above.
4. **How does the work grow?** With the tree, in the plain run alone.
5. **What did the before and after show, and under what conditions?** Back-to-back runs on a loaded host, read as evidence.
6. **Did any map move?** No: no engine code changes.
<!-- plan-archive: archived 2026-11-12 -->
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

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T84 to T84 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
### T121 (T83's fifth slice, the landing, `ask:449-T83-scope`)

- **Approach**: `land.py` with `work_budget_view.py` and `replay_owing.py` ported with no door into a new gate crate `land` (`l7r-gate land`, `l7r-gate replay-owing`), `make audit`'s three sections that do not read `CLASSES` into `measure` (`l7r-gate measure audit runs|guards|claims`), `make land`, `make land-batch`, `make land-stop` and `make replay-owing` repointed, and the three `.py` deleted in the same cut, which lands through the Rust land.

   **Decisions** (`ask:449-T83-scope`, `ask:449-usage-text`, FR-001, FR-002, FR-003):
   - Its own crate: no existing gate crate builds on the ledger, the claims and the holding box together without the arbiter, which builds on most of the others. The ruling's three in-process asks (`reviews ledger-owed`, `speckit-todo --holding`, the claims' commands with their scope split and checks in flight) each call the function their command runs (`inproc.rs`). The gate's other subcommands (the stamp, `coverage-exempt stale`, `arbiter gate-held`, `cohort counter-only|port|check|rust-owed`), the three `*-gate.sh`, `make`, `sync-with-main.sh`, `make-docs.py` and `ruff` stay commands, as the Python ran them.
   - `tick-task.py` stays Python (T85's) and is run by path: one flag added, `--land-check`, so the first pass asks it of every task in one process, as `land.py`'s import asked `tick` and `refusal` in one. Its rows also say whether `boxes_refusal` finds a research box open (`box_open`), and the Rust land makes `land.py`'s `_box_flag` choice itself from that: `--boxes` on a task's tick under `BOXES=1` where its box is open. The reading of the boxes stays `tick-task.py`'s one `boxes_refusal` (FR-003), asked in the process the first pass already starts (FR-006), where a flag doing the choice inside `tick-task.py` moved the land's logic into Python (the plan review's block, 2026-11-12). The Python asked just before each tick, the Rust in the first pass: nothing between them writes `tasks.md` but the landing's own ticks, each of its own task.
   - The engine-path question the land asked `codeid.py` is the cohort crate's identical regex, `is_landing_engine`, asked in process.
   - Not ported, as dead: `land.py`'s `file_left` branch, which no caller set, and the `start_cover` branches, `None` since the Python tests were deleted (feature 449 FR-001b) (observed 2026-11-12, method: `git grep` of each name). The claims door's verbs only `land.py` asks (`scope_split`, `file_left`, `flight_live`, `CLAIMS_FEATURE_DIR`) and `seam::file_left` stay through this commit, which the Python lands, and leave in T124, which the Rust land lands.
   - `GATE_MACHINERY`, the paths that decide how a landing and its gate run: `scripts/land.py` replaced by `rust/gate/crates/land/`, the landing's code at its new home, so a change to the land still runs the tooling tests.
   - A defect the differential found and fixed: the land's TERM handler was replaced by the guard's own the first time an in-process call made a `TempDir`, so a stopped landing exited 143 with its gate still running. The land registers its stop step on the guard's one handler (`l7r_guard::shared::tempdir::before_exit`), pinned in the guard's signal test and the land's child-process test.
   - Kept for byte parity: the usage text naming `land.py`, `-h` exiting 2, an INT cleaning only the scratch and exiting 130 as the Python's `KeyboardInterrupt` did. `make land-stop` finds an `l7r-gate land` process, the land now being the binary.
   - The landing commit, as the ruling has it: the last the Python `land.py` lands and the one that deletes it. The commit deletes `land.py` and points `make land` at `l7r-gate land` (the switch collapsed), so the landing runs HEAD's `land.py` as it stood before the commit, saved outside the tree and run with its own path set to `scripts/land.py` (`make land ... LAND_RUN="python3 <the saved copy's runner>"`), so every file it loads by its own directory (`tick-task.py`, `claims_door.py`, `codeid.py`, the gates, `hooks/lib`) resolves as it did. The door verbs it asks mid-run stay in this commit (above). `work_budget_view.py`, deleted with it, is loaded only at an engine landing, after the push, and the land's engine paths include the Rust crates, so the landing (2026-11-12) pushed and ticked T121 and then raised there, its one loss the work budget's summary lines after the push (observed 2026-11-12, method: the landing's log, `ModuleNotFoundError: No module named 'work_budget_view'` after `land: T121 landed and ticked`).
   - The same outputs (FR-002), the Python always HEAD's. The verdict replay: every `(make land)` tick commit on the first parent since 2026-11-09 (50 landings, T066-T120), each from its tick's parent in a shared clone against a local bare origin, `make` and the push stubbed and recorded, in three modes (the real stamp; the stamp refusing once then passing, on the six newest; every escape set, through to the ticks and the push), 104 runs, 0 differing, `make done` asked in 66, ticks committed in 52, the push asked in 52 (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/replay.py`). The commands: 53 cases of `make land`, `land-batch` and `land-stop` (every argument and refusal, the six escapes good and bad, `BOXES`, a closing tick refused and reverted, push results 0, 3, 1 and a failing revert, engine, Rust, machinery and scripts deltas, the budget and Rust-gate branches, a stop idle and against a running landing), 1 differing, `push-failed`, whose revert shows a bypass record modified rather than deleted because the tick fell in the same second as an earlier record, records being named by the second (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/diff_land.py`). `make replay-owing` 14 cases (waves 106, 108 and 111, the `TRIAGE=1` commits, later commits, the argument and failure forms), 0 differing (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/diff_replay.py`). The audit 50 cases, 0 differing (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/diff_audit.py`). Failure parity: commits after T87 fail on both sides of the replay (their own `modal_owed.py` gone), and every broken-input case of the audit fails on both. Normalizations: tracebacks from `Traceback` on, argparse's usage text, the bypass records' file names, `utc` and `commit` and the same-second add-or-modify, the live machine's `JOBS` and memory figures, commit ids in a revert message.
   - Timing: the verdict replay 430 s Python against 281 s Rust (observed 2026-11-12, method: the harnesses in `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/`). The commands 1,429 s against 1,491 s, mostly two 20-minute claims waits a side (observed 2026-11-12, method: the harnesses in `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/`). The audit 4.9 s against 3.2 s (observed 2026-11-12, method: the harnesses in `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/`).
   - The recorded measurement: only `specs/375-enforced-wave-process/measurements.json`'s `sc001-replay` names one of the three, through `make replay-owing`, which stays. `make figures` lists it NOT RE-MEASURED before and after the cut, its command written as prose make cannot parse (observed 2026-11-12, method: `make figures SPEC=specs/375-enforced-wave-process`); the 14 replay cases above are its proof of sameness.
   - The census at the cut: provenance comments, `rust/gate/CLAUDE.md`, `scripts/CLAUDE.md` and `docs/guards.md` repointed (observed 2026-11-12, method: `git grep` of the three names and `LAND_DRIVER` outside `specs/` and `dev/`). The checks: the port's `make static` and `make rust-test` green on 20 crates (`land` 51 tests, `measure` 130, `claims` 62, `cohort` 52, the guard 555), `make hooks-test HOOKS_ALL=1` green on 54 suites, the pointer check clean (observed 2026-11-12, method: those commands).

### T121 Approach (checklist part A)

1. **The goal, in the world.** `make land` is Rust, the replay and the audit sections with it, the three `.py` gone.
2. **The constraints.** FR-001, FR-002 and FR-003, the ruling `ask:449-T83-scope`.
3. **Where each comes from.** G: the GM's words in `request.md` and the standing approval to delete ported Python; R: the rulings; O: the replay, the differentials and the census above.
4. **Do they describe the world here?** Replayed over this clone's own recorded landings, every one since 2026-11-09 (measured 2026-11-12 (`/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/replay.py`)).
5. **The order.** After T120, the slice the ruling put last.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and its own `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The verdict replay's 104 runs with no difference, the differentials' one explained difference, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No.


### T117 (T83's first slice, the review ledger's tools, `ask:449-T83-scope`)

- **Approach**: `ledger_lint.py`, `review_cost.py` and `ledger_owed.py` ported with no door: the lint and a review's cost in the guard crate (`rust/guard/src/shared/ledger.rs`, `ledger/cost.rs`), the commands and the owed rows in the gate's `reviews` crate (`reviews/ledger.rs`: `reviews ledger-lint`, `ledger-rows`, `review-cost`; `reviews/ledger_passes.rs` and its `settle`, `rows`, `trace`: `reviews ledger-owed`, `ledger-passes`), every caller repointed and the three `.py` deleted in the same cut.

   **Decisions** (`ask:449-T83-scope`, `ask:449-T76-scope`, `ask:449-usage-text`, FR-001, FR-002, FR-003):
   - The lint and the cost live in the guard crate: the guard's `checks/passes.rs` already held a copy of `review_cost`'s arithmetic and `ledger_lint.CHECKS`, and the guard cannot build on the gate, which builds on the guard. One implementation (FR-003) puts them in the guard, as T89 reused the guard's `at_rev`; `passes.rs` now reads the shared code. `ledger_hooks` and `escalation_hooks` ask the lint and the cost in-process, where they ran Python by path, and `ledger_hooks` runs `reviews ledger-owed` by command through the gate's wrapper (the repository's own first, else the tree's). Two leaves moved into the guard with them, since the guard cannot reach `core`: `iso.rs` (Python's `datetime.fromisoformat`) and `py_text::repr`, `core` re-exporting both so its callers are unchanged.
   - The callers: the Makefile's `ledger-owed` and `review-cost` recipes, `sync-with-main.sh`, `land-tooling.sh` (the defaults inside its `LAND_TOOLING_PLAN_ROWS` and `LAND_TOOLING_LEDGER` overrides, the suites' contract kept), `land.py` (Python until T121, running the command by subprocess), `page_session_runner.py`, `push.rs`'s `ledger-owed` row (now a gate row), and the Python importers, each now running the command: `coord.py` (`ledger-lint` on a scratch file, `review-cost --last`), `review_census.py` (`ledger-rows`) and `feature_report.py` (`ledger-passes`, until T119 ports it).
   - Two corrections toward the Python in the guard, which no differential case reaches: a pass's cost in the pass log is computed as `review_cost.py` computed it (integer microseconds, Python's `int()`), where the guard's copy could round a half-second tie or an odd token count differently, and `event_log_hooks::verdict_of` reads a reply's first line with Python's `strip()` and `splitlines()`.
   - The same outputs (FR-002): the Python (from a `git archive` of HEAD) against the Rust on the same inputs, each case set up identically at one path, its file times pinned, exit, stdout, stderr, every file of the work repository and the usage-log line compared: 149 cases, `ledger-owed` 69, the lint 9, the cost 71, over the real ledger, the real pass log of 2,950 lines, about 40 real agents' transcripts and scratch fixtures for every flag and branch, 0 differing, 33 reaching a traceback and 6 an argparse usage error (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s1/diff.py`). The repointed importers before and after, `coord.py`, the census, `feature_report`'s passes on the real log and the page runner's rows: 21 cases, 0 differing (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s1/diff2.py`). Normalizations: N1 stderr from `Traceback` on, N2 argparse's usage text (`ask:449-usage-text`), N3 the usage line's `utc`, N4 no bytecode. One real difference found and fixed: a relative `--transcripts` was joined to the working directory, which moved the path the kept-cost file stores. Divergences no case reaches: `--help` exits 2 (T82's N7), Python's `\w` and `\b` on a character like `²`, a pass's `segment` read as ASCII digits, a log line holding NaN or a lone surrogate skipped where Python kept it, glob characters in an agent id, and which undecodable page raises first.
   - Timing: the Python 29.1 s and the Rust 20.9 s over the first harness's 149 runs, process time alone (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s1/diff.py`).
   - The census at the cut: a `git grep` of the three names over the Makefile, `*.mk`, `*.sh`, `*.py`, `*.rs`, `.claude/` and `tests/`, untracked files included, finds provenance comments and docstrings, and one error text kept byte for byte, `_review_cost: no transcript ...`; no `specs/*/measurements*.json` command runs them (observed 2026-11-12, method: that search). `turn_time.py` is still Python, `scripts/measure/turn_time.py`, 120 lines, its one importer `stepback_bundle.py`, so it ports in T120 (observed 2026-11-12, method: `git ls-files` and `git grep`).
   - The coverage and the checks: every new line reached by its crate's tests and the crates `clippy::pedantic` clean, `make static` clean on 19 crates, `make rust-test` green (the guard 536 tests, `reviews` 62), `make hooks-test HOOKS_ALL=1` green on all 54 suites (observed 2026-11-12, method: those commands).
   - A cost to note: a `git commit` now starts the gate's wrapper in the ledger guard, which builds the binary first if a gate source is newer, inside the hook.

### T117 Approach (checklist part A)

1. **The goal, in the world.** The review ledger's tools are Rust, one implementation, and no Python of theirs is left.
2. **The constraints.** FR-001, FR-002 and FR-003, the ruling `ask:449-T83-scope`.
3. **Where each comes from.** G: the GM's words in `request.md` and the standing approval to delete ported Python; R: the ruling; O: the differential and the census above.
4. **Do they describe the world here?** Run on this clone's real ledger, pass log and transcripts.
5. **The order.** First of T83's five slices.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential's 170 cases with no difference, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T118 (T83's second slice, `speckit-todo.py`, `ask:449-T83-scope`)

- **Approach**: `scripts/speckit-todo.py` ported with no door: its rules (the state, the vocabulary, `**Affects**:` and `**Owed at**:`, `closed_by_status`, `holding`, the active task, the GM-review rows) in the guard crate (`rust/guard/src/shared/speckit.rs`), its command line and report in the gate's `cohort` crate (`cohort/src/speckit_todo.rs`, `speckit_todo/report.rs`, `speckit_todo/work_budget_view.rs`) as `l7r-gate speckit-todo`, its Rust callers calling the rules in-process, every other caller repointed and the `.py` deleted in the same cut.

   **Decisions** (`ask:449-T83-scope`, `ask:449-usage-text`, FR-001, FR-002, FR-003):
   - The rules live in the guard crate: two guards read them (`set_down_hooks`, `feature_approval_hooks`) and the guard cannot build on the gate, T117's reason. The command line lives in `cohort`, the narrowest crate the binary builds on that holds the push. In-process now: `ci/features.rs` (`holding`; its unused `python` parameter and `ask` gone), `reviews/glyph.rs` (`state`; its run by command and cache gone), `set_down_hooks` (`closed_by_status`; its `Ctx` gone) and `feature_approval_hooks` (its copies of `CLOSING`, `STATUS` and `BOX` read from the shared module, its own `at_rev` rule kept as it was, deliberately different). The push's "speckit-todo check" row is a gate row (`speckit-todo --root {root} --check`), keeping the row runner, its refusal text, its kept key and its usage line, as T117's `ledger-owed` row did.
   - By command now: the Makefile's `speckit-todo` recipe (its `##` text unchanged), `sync-with-main.sh`'s three calls (an error still failing closed), `land.py`'s holding line (Python until T121), and the Python importers `close_check.py`, `plan_hold.py`, `research_claims.py` and `tick-task.py`, each through one new flag, `--each-state DIR...` (one state a line, `""` for a directory it cannot read, no usage line, as their imports recorded none), so each runs one process for all its directories. Test stubs of `speckit-todo.py` in `core/ci/fixtures.rs`, `reviews/tests.rs` and `set_down_hooks/tests.rs` gave way to real `.git/active-task` files and status lines.
   - The usage log: the command records as `usage_log.exited` did (`passed` or `refused`, in the working directory's repository, none on an argparse error or a traceback). The in-process calls record nothing, where `features.rs` and `set_down_hooks` left a `speckit-todo` line through their runs by command, the line a by-product of the process, not of a check.
   - `work_budget_view.py`'s `lines()` and `moved()` are ported for the report (`speckit_todo/work_budget_view.rs`), while the `.py` stays for `land.py`, its other importer, which the ruling ports in T121: two copies for one slice, each file's comment naming the other, the `.py` deleted with `land.py` in T121.
   - The same outputs (FR-002): the Python (HEAD's whole `scripts/` from `git archive`) against the Rust, each case set up identically at one path, exit, stdout, stderr, every file and the usage line compared. Over the real tree (`--root` this clone and `/diagram`, every report flag), every real feature's `--state`, `--closed-by-status` and `--holding`, about 170 scratch trees covering every branch (status forms, CRLF and invalid bytes, boxes, Affects and Owed-at forms, a broken vocabulary five ways, the 444 view ten ways, the holding rule over 14 marks and 2 environments, clones in both layouts), argparse's prefix and `=` forms: 1,302 cases, 1 differing, `-h` exiting 2 against Python's 0, the divergence T82 (N7) and T117 accepted, 32 reaching a traceback and 6 an argparse usage error (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s2/diff.py`). The repointed importers before and after (`plan_hold.holder`, `tick-task.waits_or_marks`, `research_claims.settled_features`, `close_check.push_reasons`, `write_grandfathered`, `land.py`'s holding line): 797 cases, 0 differing (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s2/diff2.py`). Normalizations: N1 stderr from `Traceback` on, N2 argparse's usage text, N3 the usage line's `utc`. Divergences no case reaches: `isdigit()` on non-ASCII digits in an `F=` number, Python's JSON taking `NaN`, a vocabulary alias given as a number or `tags` not an object, and a lone `--`.
   - A broken `.specify/affects.json` fails where the Python raised (the plan review of T118, round 2): the Python's `feature(d)` read the vocabulary of `d`'s grandparent, so `--state` and every importer's state raised on it. `state(d)` reads it too and returns its error (an absent file still reads as none, as the Python's did), `state_given_vocabulary` serving the one caller that handed a vocabulary in. `--state` exits 1 with the error on stderr. `--each-state` prints `error: <why>` on the line of a directory it cannot read and exits 1, and with `--root` reads that vocabulary once, a broken one printing nothing and exiting 1. The importers that let the old import raise (`close_check.py`, `plan_hold.py`, `tick-task.py`) raise on the nonzero exit (`check=True`), and `research_claims.py`, which caught it, keeps its old handling: a broken vocabulary retires nothing, an `error:` line is skipped. `reviews/glyph.rs` read a failed run by command as `""` (not closed), and reads the in-process error the same way. `holding` and `closed_by_status` never read the vocabulary, in the Python either. Pinned by a guard test (`a_broken_vocabulary_above_the_directory_fails_its_state`) and the cohort's cases, and in the differential: 15 commands over three broken vocabularies (not JSON, a tag without its stage, bad bytes), and 58 importer cases, both sides failing (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s2/diff.py` and `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s2/diff2.py`, re-run). The differential's counts on the final binary: 1,317 command cases, 1 differing (`-h`), 41 reaching a traceback, and 855 importer cases, 0 differing, a raise compared as a raise and not by its type (N4: the import raised the reader's error, the command's caller raises `CalledProcessError`) (observed 2026-11-12, method: the same harnesses).
   - Timing: the Python 65.6 s and the Rust 31.5 s over the 1,317 cases, process time through the wrapper, and the importers 2.5 s before and 0.6 s after (observed 2026-11-12, method: the harnesses above).
   - The census at the cut: no caller left over the Makefile, `*.mk`, `*.sh`, `*.py`, `*.rs`, `*.json`, `*.md`, `.claude/`, `tests/`, `docs/`, `scripts/` and `rust/`, untracked files included, only provenance comments, docstrings and `dev/phase-1-close.md`'s history; `specs/375-enforced-wave-process/measurements.json`'s `375-a1-speckit-todo-clones` recorded a prose timing of the Python's `in_clones` in two modes, a comparison no make command reaches (the port keeps only the chosen mode), so its command is retired and its values kept as history (`ask:449-T118-retire-375-a1`, on the `ask:449-T79-moves` and `ask:449-T89-reviews` pattern), which `make figures` does not run (observed 2026-11-12, method: that `git grep`, and `make figures` after the retirement).
   - The checks: `make static` clean on 19 crates, `make rust-test` green (the guard 548 tests, `cohort` 50, `ci` 30, `reviews` 62), `make hooks-test HOOKS_ALL=1` green on 54 suites, the pointer check clean (observed 2026-11-12, method: those commands).

### T118 Approach (checklist part A)

1. **The goal, in the world.** `speckit-todo` is Rust, its Rust callers asking it in-process, no Python of it left.
2. **The constraints.** FR-001, FR-002 and FR-003, the ruling `ask:449-T83-scope`.
3. **Where each comes from.** G: the GM's words in `request.md` and the standing approval to delete ported Python; R: the ruling; O: the differential and the census above.
4. **Do they describe the world here?** Run on this clone's real `specs/` and its sibling clones.
5. **The order.** After T117.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential's 2,172 cases, one accepted difference, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T119 (T83's third slice, the measure chain, `ask:449-T83-scope`)

- **Approach**: `event_log.py`, `task_phases.py`, `feature_report.py` and `where_time.py` ported with no door: the event-log reader beside its writer in the guard (`rust/guard/src/guards/event_log_hooks/read.rs`: `read_jsonl`, `from_transcript`, `reversals`), the report, the task phases and the time split in the gate's `measure` crate (`measure/events.rs`, `task_phases.rs`, `feature_report.rs` with `sources.rs` and `tables.rs`, `where_time.rs`, `event_log.rs`) as `l7r-gate measure feature-report`, `where-time` and `event-log hook|from-transcript`, the callers repointed and the four `.py`, with the unported harness `specs/385-approach-checklist/where_time.py`, deleted in the same cut.

   **Decisions** (`ask:449-T83-scope`, `ask:449-usage-text`, FR-001, FR-002, FR-003):
   - One event-log reader, as the ruling asks: the reader lives in the guard beside the writer, reusing its `line`, `typed_prompt`, `verdict_of`, `log_path` and `common_git_dir`, since the guard cannot build on the gate; the arbiter's bundle, which held its own `read_jsonl` and `reversals`, now calls these. `py_str` and `value_repr` moved into the guard's `pyjson`, `core` re-exporting them.
   - The report reads the review passes in-process (`ledger_passes::passes`), where T117's interim ran `reviews ledger-passes` by command; the command stays for its other readers.
   - Both of `event_log.py`'s verbs are ported (`hook` and `from-transcript`), though nothing runs them, so no command vanishes unannounced. `hook` writes through a new guard function, `record`, the hook's own path: a hook payload that is no JSON object now writes no line, as the Python's raised and its hook wrote none, where the guard's writer had written one.
   - The callers: the Makefile's `feature-report` and `where-time` recipes (their `##` text and `F=` checks unchanged). No inline `python3 -c` recipe of the Makefile calls these modules, so none goes with this slice.
   - `specs/385-approach-checklist/where_time.py`, which imported `feature_report`, is deleted unported as a past harness under the GM's 2026-11-09 rule: nothing in the Makefile, `scripts/`, `rust/`, `.claude/` or any `specs/*/measurements*.json` command ran it (observed 2026-11-12, method: `git grep` over those).
   - Failure parity: wherever the Python raised the Rust fails too, pinned by 40 differential cases with both sides failing (a log line that is no object, an event without `ev`, an unparseable time, a bad `ms`, a `tasks.md`, `spec.md` or `plan.md` not UTF-8, a run-log record that is a list, bad task-start rows, a pass log not UTF-8, a spec "directory" that is a file under `--write`) (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s3/diff.py`).
   - The same outputs (FR-002): the Python (HEAD's, copied) against the Rust, exit, stdout, stderr and every file written compared, over 15 real features (with SINCE and UNTIL windows, transcript forms and `--write`), `where-time` on 6 features with `--since` and `--by-tick`, `from-transcript` on real session and subagent transcripts, HEAD's Makefile against this clone's (`make feature-report F=374` among them) and scratch trees for every branch: 182 cases, 0 differing, 40 reaching a traceback and 8 a usage error (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s3/diff.py`), and the same 182 re-run after the deletion, 0 differing (observed 2026-11-12, method: the same harness against the copies). Normalizations: N1 stderr from `Traceback` on, N2 usage text (`ask:449-usage-text`), N3 the line `This report took X s`, N4 the order of `where-time` rows that tie on their sort key (tasks never started, or started in one batch in the same second), which the Python left to its string hash, different from run to run (two `PYTHONHASHSEED` values gave two orders), where the Rust keeps the order first booked, N5 the hook's own time in a written line, N6 the Makefile's path in make's own error line. Divergences no case reaches: non-ASCII digits in an `int` or `float`, `NaN` in JSON, unhashable or mixed-type event fields, a list-valued `t` on a lone event, which agent wins when one tool id is in two subagents' transcripts (Python's set order), non-UTF-8 output from git (both fail, at different points), and `-h` exiting 2.
   - Timing: the Python 347.3 s and the Rust 244.9 s over the final run before the cut, process time with the wrapper (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s3/diff.py`).
   - The recorded measurements: `specs/374-...`'s `sc003-375-first-three-tasks` and `sc004-375-dispatches-per-row` and `specs/375-...`'s `sc005-one-task` run `make feature-report` commands the cut leaves as they are, the differential matching them; `sc005-372`, `cascade-threshold` and `sc006-replay` run `make feature-report F=372 TRANSCRIPT=<a transcript no longer on disk>`, failing alike before and after; `event-hook-cost`'s command has run nothing since T012 and only its method names `event_log.py` (observed 2026-11-12, method: `git grep` of the four names over every `specs/*/measurements*.json`). None runs a deleted script, so FR-001's rewrite is not owed by this cut.
   - The census at the cut: provenance comments in the Rust, `dev/phase-2-close.md`, `docs/guards.md` and measurement prose alone (observed 2026-11-12, method: `git grep` of the four names). The checks: `make static` clean on 19 crates, `make rust-test` green (`measure` 96 tests, the guard 556), `make hooks-test HOOKS_ALL=1` green on 54 suites, the pointer check and `ruff check scripts` clean, no file over the bar (observed 2026-11-12, method: those commands).

### T119 Approach (checklist part A)

1. **The goal, in the world.** The measure chain is Rust, one event-log reader, no Python of it left.
2. **The constraints.** FR-001, FR-002 and FR-003, the ruling `ask:449-T83-scope`.
3. **Where each comes from.** G: the GM's words in `request.md` and the standing approval to delete ported Python; R: the ruling; O: the differential and the census above.
4. **Do they describe the world here?** Run on this clone's real event logs, features and transcripts.
5. **The order.** After T118.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential's 182 cases, twice, with no difference, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T120 (T83's fourth slice, the step-back and the yields, `ask:449-T83-scope`)

- **Approach**: `stepback_bundle.py`, `turn_time.py`, `fix_yield.py` and `tool_yield.py` ported with no door into the gate's `measure` crate (`measure/stepback_bundle.rs` with `words.rs`, `fix_yield.rs`, `tool_yield.rs` with `records.rs`, `turn_time.rs`: `l7r-gate measure step-back`, `fix-yield`, `tool-yield`, `turn-time`), the tool inventory made one implementation in `core` (`core/src/measure/tool_inventory.rs`), `reviews_door.py` and its Rust side (`reviews-door`) removed, the callers repointed and the five `.py` deleted in the same cut.

   **Decisions** (`ask:449-T83-scope`, `ask:449-T89-reviews`, `ask:449-usage-text`, FR-001, FR-002, FR-003):
   - The step-back lives in `measure`, beside `fix_yield`, which it needs and `reviews` cannot build on; it calls `reviews`' `git`, `gitdir` and `checkpoint::state` in-process, which is what retires the door's three verbs (`ask:449-T89-reviews`). It writes the bundle's files in the Python's order, so a failure part-way leaves the same files. `reviews_door.py`, `reviews/door.rs` and the `reviews-door` dispatch go with it: nothing else used them (observed 2026-11-12, method: `git grep` of `reviews_door` and `reviews-door`).
   - The tool inventory: `checks/tool_signals.rs` did not run `tool_yield.py` by command, as the ruling supposed, but held its own copy of the inventory since T068 (`hook_guards`, `recipe`, `reached`, `check_paths`, the registry reader). One implementation now, in `core`, which both `checks` and `measure` build on, `tool_signals.rs` reading it in-process and its copy removed. With it `check tool-signals` fails (exit 1, `check-tool-signals: <error>`) on a missing or broken settings file, Makefile or registry, or a gate script not UTF-8, where T068's copy read them leniently and the original `check-tool-signals.py` failed through its import of `tool_yield`: a return toward the Python, pinned by a test, the check passing on the real tree.
   - `turn_time` stays a command with no make recipe, as the Python had none, T119's rule that no command vanishes unannounced. `tool-yield`'s default `--root` is the tree the command runs in, where the Python's was its own script's tree, the same under `make tool-yield`, which always passes `--root`. `fix_yield` asks a fix's commit by `git rev-parse --verify --quiet <sha>^{commit}` where the Python ran `git cat-file -e`, the same question through the one git reader.
   - The callers: the Makefile's `fix-yield`, `tool-yield` and both `step-back` forms. No inline `python3 -c` recipe of the Makefile calls these modules.
   - The recorded measurement: `specs/375-enforced-wave-process/measurements.json`'s `375-a7-turn-time` ran `python3 scripts/measure/turn_time.py` on a session transcript no longer on disk, failing before and after the cut, so its command is retired and its values kept as history (`ask:449-T120-retire-375-a7`), which `make figures` does not run (observed 2026-11-12, method: `make figures SPEC=specs/375-enforced-wave-process`).
   - The same outputs (FR-002): the Python (HEAD's, reaching the door through a frozen copy of the binary that still held it) against the Rust built after the deletion and a green `make static`, in a frozen world (a scratch home holding the guard log and transcripts, snapshot usage and event logs), each case set up identically, exit, stdout, stderr and every file written compared: 219 cases, 0 differing, 68 reaching a traceback and 10 a usage error (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s4/diff.py`). The step-back 60 (13 real windows of this clone's features, 6 replays of real transcripts, 31 scratch cases for every branch, the argument and refusal forms), the tool yield 76 (every `--kind`, 31 broken scratch trees both sides fail on), the fix yield 44 (every real feature with a ruled fix and scratch fixes), the turn time 33 (11 real transcripts and every `--record` path), and 10 Makefile forms. Failure parity: every case where the Python raised (a bad time, a message that is no object, a zero-duration call's `KeyError`, an output path that is a file, a `tasks.md` not UTF-8, a broken settings file or registry, a bypass record that is a list, an unreadable arbiter file) fails in the Rust too (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s4/diff.py`). A rerun of 103 cases, 0 differing, and a replay of the Rust alone hours later against the kept Python outcomes, 1 differing, a step-back with no `--since` on a repository with no checkpoint, whose window starts at each run's own clock (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s4/run3.log` and `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s4/replay2.log`). Normalizations: N1 stderr from `Traceback` on, N2 argparse's usage text, N3 the clock in a case with no `--until` (T89's N7, extended to the start a missing checkpoint leaves to the clock), N4 no bytecode, N5 the `utc` of make's own usage line, N6 the new Makefile's path in make's error line, N7 the scratch fixtures' `.git` internals, and in the replay alone N8, `tool-yield`'s "uses (7 d)" column, counted back from each run's clock. Not run: `make step-back` with no `TRIGGER`, which writes a real bundle's name; its two halves ran apart. Divergences no case reaches: Python's Unicode `isalnum` in the trigger's escape, glob characters in a session id or `F=`, `NaN` or a lone surrogate in JSON, an integer past 64 bits, `-h` exiting 2, a lone `--`, a registry `kind` that is not text.
   - Timing: the Python 529.9 s and the Rust 502.3 s over the cases, most of it the wrapper's start and reading 78,660 guard-log files a tool-yield case (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s4/diff.py`).
   - The census at the cut: provenance comments, the Rust module names, `rust/gate/CLAUDE.md`, `dev/rust-tooling.md`, `dev/phase-2-close.md`'s history and `round-arbiter.md`'s mention of `make fix-yield`, a target that stays (observed 2026-11-12, method: `git grep --untracked` of the six names). The checks: `make static` clean on 19 crates, `make rust-test` green (`measure` 125 tests, `checks` 99, `reviews` 61, the guard 555), `make hooks-test HOOKS_ALL=1` green on 54 suites, the pointer check clean (observed 2026-11-12, method: those commands). One flake seen once under `make static`'s side-by-side cover run, `ledger_passes::settle::tests::a_kept_cost_is_served_while_its_transcript_stands` (it expected the kept cost and got a fresh one), passing on every later run, in code this slice did not change (observed 2026-11-12, method: the port's `make static` and `make rust-test` runs).

### T120 Approach (checklist part A)

1. **The goal, in the world.** The step-back and the yield tools are Rust, one tool inventory, the reviews door gone.
2. **The constraints.** FR-001, FR-002 and FR-003, the rulings `ask:449-T83-scope` and `ask:449-T89-reviews`.
3. **Where each comes from.** G: the GM's words in `request.md` and the standing approval to delete ported Python; R: the rulings; O: the differential and the census above.
4. **Do they describe the world here?** Run on this clone's real windows, transcripts, features and logs.
5. **The order.** After T119.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential's 219 cases with no difference, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T124 (T121's follow-up: the claims-door verbs only `land.py` asked, `ask:449-T83-scope`)

- **Approach**: the claims door's `scope_split`, `file_left`, `flight_live` and `CLAIMS_FEATURE_DIR` (Rust `door.rs` and `scripts/claims_door.py`) and `seam::file_left` with its constant removed, with their tests, the port's patch for them kept from T121's landing commit (`/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t83s5/landing-commit.patch`). They stayed through T121's commit so the Python `land.py` could land its own deletion, as the ruling has it, and leave once the Rust land is `make land`.

### T124 Approach (checklist part A)

1. **The goal, in the world.** No door verb is left that nothing asks.
2. **The constraints.** FR-001 and FR-003, the ruling `ask:449-T83-scope`.
3. **Where each comes from.** R: the ruling and T121's plan review; O: the census.
4. **Do they describe the world here?** A `git grep` of each verb's name after T121 landed: outside the land crate, which asks `scope_split` and `flight_live` in process, only provenance comments and the door's tests that each verb is refused (observed 2026-11-12, method: `git grep -n` of the four names over `scripts` and `rust`).
5. **The order.** After T121's landing, which pushed 2026-11-12.
6. **The exits.** Green: `make static`, `make rust-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The census naming the verbs only in provenance comments.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No.

<!-- plan-archive: archived 2026-11-12 -->
### T125 (the full hook run ends on its longest suite started late, the GM's pre-approval of 2026-11-12)

- **Approach**: `make hooks-test` hands its suites to its eight slots longest first, by each suite's seconds the last time it ran (`tests/hooks/hookrun.sh` keeps them beside its stamp, `.git/hooks-test/<suite>.s`, pass or fail), a suite never timed first; and the engine-freeze suite's two roll fixtures wait for the roll to show in `/proc` instead of a fixed sleep.

   **Decisions** (the GM's pre-approval in `request.md`: "if you identify concrete targets with significant measured expected savings then go ahead and do them", and his priority "After you finish the current in-progress task(s) you should prioritize the performance bits of the tests and landing"; FR-002):
   - Where a landing's time goes: T124's landing took about 75 s, its gate's full hook run about 54 s of it (observed 2026-11-12, method: the landing's log and its commits' times). The full run is not held by the CPU: 22 processors, no quota and no throttling, about 5 in use (observed 2026-11-12, method: `nproc`, `/sys/fs/cgroup/cpu.max` and `cpu.stat`). Sampling every process of the run every 50 ms with the suite each sat under, the run ended at 55.7 s on idle-tests, 36.1 s long and started 19.6 s in, the eight slots having taken the roster in its order first (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/sample.py`).
   - The order, A/B'd alternated three runs a side: idle-tests alone moved first 51.4, 50.9 and 51.6 s against the roster's 53.0, 62.7 and 63.0 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/ab.txt`). Every suite longest first by its last seconds 49.9, 51.9 and 53.4 s against idle-tests first 42.1, 52.2 and 52.0 s, the same within the spread, so the general rule lands rather than one suite named (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/abC.sh`). The change as landed against HEAD's Makefile: 51.0, 51.6 and 54.9 s against 52.4, 62.5 and 63.3 s, a mean of 52.5 s against 59.4 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/ab125.sh`). T98 measured longest first slower on an earlier roster (its section in `plan-done.md`); the measurement above, on today's, supersedes it.
   - Not done, measured: a split suite's parts above two beside other suites (`PARTS_MAX`, kept at two since the 10 GB memory cap was hit on 2026-10-17) gained nothing, 52.8 s at four and 53.4 s at eight against 50.9 s at two (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/pm.txt`), the run then ending on entry-gate, which is not split.
   - The flake the reordering showed: in one longest-first run the engine-freeze suite's Rust-gate roll was not yet in `/proc` after its fixed 0.5 s, so three cases failed (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/c-C1.log`); its two roll fixtures now wait for the roll by name, a 5 s bound (CONVENTION, the fixture's own constant), so the case tests a roll that is running, and the other-tree case no longer passes because no roll was seen yet.
   - Kept as it was: every suite, its cases and its checks; the stamps; the eight slots (`HOOKS_JOBS`); `PARTS_MAX`. A suite's kept seconds is a hint to the order alone, and a missing or stale one only moves a suite in the queue.

### T125 Approach (checklist part A)

1. **The goal, in the world.** A full hook run, the longest phase of a tooling landing's gate, ends sooner.
2. **The constraints.** FR-002, the GM's pre-approval and priority.
3. **Where each comes from.** G: the GM's words in `request.md`; O: the sampled run and the A/Bs above.
4. **Do they describe the world here?** Measured on this clone's own full hook runs (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/ab125.sh`).
5. **The order.** After T124.
6. **The exits.** Green: `make hooks-test HOOKS_ALL=1` green and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The A/B against HEAD above, a mean of 52.5 s against 59.4 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/ab125.sh`).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** Yes, below.

### T125 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In the full hook run, the last suite to finish: idle-tests, started 19.6 s in by roster order (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/sample.py`).
2. **Removes work, or only moves it?** Moves it: the same suites, run in an order that starts the longest first.
3. **What do you expect it to save, and why?** The late start of the longest suite, about 8 s of a run whose longest suite is about 36 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/ab.txt`).
4. **How does the work grow with the settlement?** Not a settlement stage: it grows with the longest suite, not the roster.
5. **What did the before and after show, and under what conditions?** Alternated three runs a side on the shared host: a mean of 52.5 s against 59.4 s, spread 51.0-54.9 s against 52.4-63.3 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/ab125.sh`).
6. **Did any map move, and does it still keep the research?** No map: tooling only.
<!-- plan-archive: archived 2026-11-12 -->
### T126 (the gate wrapper's cost on every call, the GM's pre-approval of 2026-11-12)

- **Approach**: `scripts/gates/l7r-gate.sh`, which every `make` recipe and hook suite calls to run the gate's binary, reads the account's home from `/etc/passwd` in its own shell (`getent` kept as the fallback) and asks whether the binary is stale with one `find -newer ... -quit` over the same sources, where it ran `getent`, `id` and `cut` and walked every source path in a bash glob on every call.

   **Decisions** (the GM's pre-approval in `request.md`: "if you identify concrete targets with significant measured expected savings then go ahead and do them", and his priority on the tests' and the landing's time; FR-002):
   - Where the time goes: after T125 the full hook run ends on sync-with-main, the suite with the most CPU, 53 CPU-seconds alone of about 178 over every suite (observed 2026-11-12, method: each suite alone under GNU `time`, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/cpu.sh`). Sampling its processes every 50 ms, the bash of `l7r-gate.sh` itself ran in about 100 samples against 30 for the binary it starts (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/sample2.py`). A call cost 22 to 25 ms through the wrapper against 5 to 6 ms for the binary alone (observed 2026-11-12, method: thirty calls of `json-field` each way). Of it, `getent passwd "$(id -u)" | cut` 4.7 ms and the glob walk of the 835 paths under `rust/gate` and `rust/guard` 5.0 ms, against 0.3 ms for `/etc/passwd` read in the shell and 3.5 ms for one `find` (observed 2026-11-12, method: fifty calls of each in one bash, `EPOCHREALTIME`).
   - The change: a call 10.5 ms (observed 2026-11-12, method: thirty calls of `json-field` through the new wrapper). The full hook run, HEAD's wrapper and the new one swapped in place, alternated three runs a side, HEAD first: HEAD 42.4, 52.0 and 51.9 s, the new wrapper 44.7, 47.1 and 47.0 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/abwrap.sh`, `wrap.txt`). Again with the new wrapper first: the new wrapper 46.1, 47.1 and 47.5 s, HEAD 52.8, 53.0 and 56.8 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/abwrap2.sh`, `wrap2.txt`). Over all twelve runs a mean of 46.6 s against 51.5 s, five of the six pairs favoring the new wrapper by 5 to 9 s and HEAD's first run of the first sequence (42.4 s) the one faster than every new run (observed 2026-11-12, method: the two records above).
   - The same answer (FR-002): `find -newer` is strictly newer, as `-nt` against an existing binary was; it also sees dot files, which the glob skipped, so it can only ask for a build the glob would not, never skip one. A source touched still rebuilds the binary (observed 2026-11-12, method: `touch rust/gate/crates/core/Cargo.toml`, then a call, the binary's time moved). The home is the same account's: the line of `/etc/passwd` whose uid is the shell's `UID`, `getent` asked where none is.
   - Not changed: the guards' wrapper `l7r-guard.sh`, whose walk of `rust/guard` costs 1.6 ms (observed 2026-11-12, method: fifty walks in one bash), too little to move a run.

### T126 Approach (checklist part A)

1. **The goal, in the world.** Every call of the gate's tools costs less, and the full hook run with it.
2. **The constraints.** FR-002, the GM's pre-approval and priority.
3. **Where each comes from.** G: the GM's words in `request.md`; O: the profile and the A/Bs above.
4. **Do they describe the world here?** Measured on this clone's own full hook runs (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/abwrap2.sh`).
5. **The order.** After T125.
6. **The exits.** Green: `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The A/Bs above, a mean of 46.6 s against 51.5 s over all twelve runs (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/wrap2.txt`).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** Yes, below.

### T126 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In the wrapper around every gate tool call: three processes for the home and a bash walk of 835 paths (observed 2026-11-12, method: the fifty-call timings above).
2. **Removes work, or only moves it?** Removes it: three processes fewer a call, and the walk in C where it was in bash.
3. **What do you expect it to save, and why?** About 12 ms a call, many hundreds of calls a full hook run, the run contended for its processors (observed 2026-11-12, method: the timings above).
4. **How does the work grow with the settlement?** Not a settlement stage: with the number of gate calls.
5. **What did the before and after show, and under what conditions?** Two alternated A/Bs on the shared host, three runs a side each, a mean of 46.6 s against 51.5 s over all twelve runs (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r6/wrap.txt` and `wrap2.txt` there).
6. **Did any map move, and does it still keep the research?** No map: tooling only.
<!-- plan-archive: archived 2026-11-12 -->
### T123 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T123 Approach (checklist part A)

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

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T124 to T83 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T125 to T125 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T126 to T126 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-12 -->
### T91 (the GM-review queue, filed by `ask:449-T82-claims`)

- **Approach**: `scripts/gm_review.py` ported whole, no door, into the gate's `reviews` crate (`reviews/gm_review.rs` with `listing.rs` and `py.rs`: `l7r-gate gm-review <verb>`), every caller repointed and the `.py` deleted in the same cut; `bundle_door.py`'s `gm_review_add_row` verb leaves with it, as the ruling has it.

   **Decisions** (`ask:449-T82-claims` Q2, `ask:449-usage-text`, FR-001, FR-002, FR-003):
   - Where it lives: `reviews`, which builds on `core` alone; `arbiter` already builds on it, and `claims` takes it as a path dependency, which makes no cycle. After the cut `gm_review.rs` is the one writer of `specs/<f>/gm-review.jsonl` and of the GM's box in `tasks.md`, as the ruling requires (observed 2026-11-12, method: `git grep` of both file names over `*.py`, `*.sh` and `*.rs`, the only other writers four hook-suite fixtures writing test data).
   - The callers: the Makefile's five gm-review recipes run `l7r-gate gm-review`. The arbiter asks `question` in process for a `for_gm` ruling and a declined fix, where it ran inline Python, and its fake fixture goes. The push row `gm-questions` runs `gm-review owed-check` as a gate command, as T117 and T118 did for their rows. `make claims-known`'s carry calls `add_row` in process, and the door verb with its stub branch goes.
   - The command is top-level, `l7r-gate gm-review`, not under `reviews`, to keep the recipes and the push row short. The usage text keeps naming `gm_review.py` byte for byte.
   - `close_check.py` stays Python (phase 3, held by no task): on the one branch where the GM's box is a feature's last open box, `reviewed` runs it by path from `L7R_GATE_TREE` under the T065 clause, with a new `--reasons-json DIR SPECS` mode that writes no usage-log line, as the Python's import recorded none (the T118 `--each-state` precedent). Its own port is T127, filed for it (phase 3 by FR-001, held by no task until this review), and this by-path run goes when it lands.
   - Two refusals outside gm-review's own commands name the Rust where they named Python. The arbiter's when its question fails reads `gm-review said: <why>`, where it was `python3 said: <traceback>`, and its two Rust tests that held `python3 said` (HEAD's `arbiter/tests.rs`, lines 607 and 619) expect the new words (observed 2026-11-12, method: `git grep -n "python3 said" HEAD` and the same over the working tree): a changed case on T87's ruled precedent `T87-arbiter-test-message` (LEGITIMATE, in `plan-review.json`: "the message names the source of a failure, and the python3 subprocess it named no longer exists once the ruled port runs the answer in Rust ... The words are the Rust arbiter's own, not the Python's hand-written words FR-002 binds"), where T87 made the same change to `record-owed said`. claims-known's on a write failure reads `gm-review: <why>`, where it was the runner's traceback; the failure returns through the same `?` of the same function to the same caller as the door's error did, so its exit status is unchanged (observed 2026-11-12, method: HEAD's `claims/carry.rs` against the working tree's, the `reader.ask(...)?` and `add_row(...).map_err(...)?` lines).
   - The same outputs (FR-002): HEAD's Python (from `git archive`) against the Rust through the wrapper, each case set up identically, exit, stdout, stderr and every file written compared: 1,272 cases over the real queues of all 47 features as stored and with every row reopened, 328's ranking and a variant with rows held behind others, scratch features for every trigger, fix, kind and refusal, ten `COLUMNS` widths, and broken inputs both sides fail on, 59 reaching a traceback on both sides (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t91/diff.py`). The closing branch compared end to end: refused, and passed with the box ticked. 8 differ, every one a row value no writer produces: 7 rows holding `NaN`, which Python reads and serde skips, and 1 integer past 64 bits, which comes back as `1e+20` (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t91/results.json`). The in-process callers: 55 cases, 0 differing, the arbiter's `fix declined` and `ask` with a `for_gm` ruling over 9 queue states against HEAD's `question` as the old arbiter ran it, and claims-known against the bytes HEAD's door verb wrote (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t91/diff2.py`). Normalizations: stderr from `Traceback` on, the times the run stamps, a JSON decode error's wording, `PYTHONHASHSEED=0` on the Python side. Divergences no case reaches: non-ASCII digits in F or ROW, `½`, row numbers past 128 bits, a width under 1, a real terminal's width, git output not UTF-8, Python's hash order between two unknown row kinds.
   - Timing: the cases took 42.4 s of process time in Python against 19.9 s in Rust, and `make gm-review` 0.052 s against 0.024 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t91/diff.py`).
   - The census at the cut: provenance comments and one guard test whose name contains `gm_review`; no `specs/*/measurements*.json` command runs the file; `docs/guards.md` pointed at a test that does not exist, repointed to the Rust tests (observed 2026-11-12, method: `git grep gm_review` over the Makefile, `*.mk`, `*.sh`, `*.py`, `*.rs`, `.claude/`, `tests/` and `docs`). The checks: `make static` clean on 20 crates, `make rust-test` green (`reviews` 88 tests, `claims` 62, `arbiter` 34, `cohort` 52, the guard 555), `make hooks-test HOOKS_ALL=1` green on 54 suites, the pointer check and ruff clean (observed 2026-11-12, method: those commands).

<!-- plan-archive: archived 2026-11-12 -->
### T91 Approach (checklist part A)

1. **The goal, in the world.** The GM-review queue is Rust, one writer of its files, the door verb gone.
2. **The constraints.** FR-001, FR-002 and FR-003, the ruling `ask:449-T82-claims`.
3. **Where each comes from.** G: the GM's words in `request.md` and the standing approval to delete ported Python; R: the ruling; O: the differential and the census above.
4. **Do they describe the world here?** Run on the real queues of all 47 features with one, measured 2026-11-12 (`/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t91/diff.py`).
5. **The order.** After T126.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential's 1,272 cases with 8 explained differences, the callers' 55 with none, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No.


<!-- plan-archive: T92 to T92 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: T93 to T93 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->

<!-- plan-archive: T95 to T95 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: T96 to T96 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: T97 to T97 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: T98 to T98 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: T99 to T110 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T111 to T111 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T112 to T112 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T113 to T113 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T114 to T114 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T115 to T115 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T116 to T116 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T121 to T83 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-12 -->
### T127 (the closing check, filed by T91's plan review)

- **Approach**: `scripts/gates/close_check.py` ported whole, no door: its reasons in the gate's `reviews` crate (`reviews/closing.rs`), its command line and push form in `cohort` (`cohort/close_check.rs`: `l7r-gate close-check`), every caller repointed and the `.py` deleted in the same cut; gm-review's by-path run of it (T91) goes with it.

   **Decisions** (FR-001, FR-002, FR-003, `ask:449-T067-scope`'s T065 clause, `ask:449-usage-text`):
   - Where it lives: the reasons in `reviews`, which builds on `core` alone, so gm-review asks them in process and `cohort` builds on `reviews` without a cycle (`core`, the other crate both could build on, rebuilds every gate crate on an edit, T92). `open_fixes` and `fix_hold` move from `arbiter` to `reviews`, which the closing check reads and `reviews` cannot build on `arbiter` for; `arbiter` re-exports them. The command and its push form in `cohort`, which already builds on `plan` (`touched_features`, made public) and `tree` (the usage log), and reads a feature's state in process.
   - The callers: gm-review's last-box close asks `closing::reasons` in process, where T91 ran the file by path. The push row `closing` runs `close-check --push origin/main...HEAD` as a gate command, its refusal text, its `CLOSE_OK` skip and its guard-log entry as before. `tick-task.py`, which stays Python (`ask:449-T89-reviews`), runs `l7r-gate.sh close-check --reasons-json <spec dir> <root>/specs` by command where it imported the module, one process where it asked once, a failure raising as the import's did (T118's N4).
   - The seam that stays Python: the closing check asks `impl_check.missing()` of a research-record feature, and `impl_check.py` stays Python (phase 3, its own later port), so the Rust runs `impl_check.py --missing-json DIR...` by path under the T065 clause, one process a run over the directories not grandfathered and none when there are none, recording no usage line. The new mode prints as JSON only what `missing()` returned. Its stderr is captured: on a failure it is carried inside the error, so a traceback reads where it read before; on success the command line and `tick-task.py` pass it through, and gm-review's in-process close drops it, as the old by-path run did.
   - Every form is ported, `--carries` and `--write-grandfathered` included (T119's rule that no command vanishes unannounced); `--reasons-json` stays, now serving `tick-task.py`, with no usage line (the T118 `--each-state` precedent). A run records `passed` or `refused`, a usage error's exit 2 counting as refused, a raise nothing; the usage text is the Python's byte for byte. A `measurements.json` is read as Python's `json` reads it, `NaN` and `Infinity` counting as values.
   - The same outputs (FR-002): HEAD's `scripts/` (from `git archive`) and the binary built from HEAD against the working scripts and the new binary, each case set up identically, exit, stdout, stderr and every file written compared, 1,645 cases with 2 differing (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t127/diff.py`, its `results-*.json`). Every real feature directory in both forms with the real and an empty grandfathered list, 1,469 cases, none differing; the push over real commit ranges, 22, none; `tick-task.py`'s last tick end to end, 9, none; gm-review's last box, 8, none; scratch inputs for every branch, refusal and raise, 117, 2 differing; and an `impl_check` group, a stand-in that warns, owes or raises and the real one, through all five forms, 20, none (observed 2026-11-12, method: the same harness). The 2 scratch differences are a directory named `٣-x`, whose non-ASCII digit Python's `int()` reads and the Rust refuses, the divergence T91 and T118 met (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t127/results-scratch.json`). Normalizations: stderr from the first `Traceback` on, the usage line's `utc`, each side's scratch tree path. Divergences no case reaches: a lone surrogate, nesting past 128 or `1e400` in a `measurements.json`, a directory name not UTF-8.
   - Timing: the real directories 328.6 s of process time in Python against 245.2 s in Rust, the push 68.6 s against 55.8 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t127/diff.py`).
   - The census at the cut: provenance comments, `dev/review-ledger.md` and the specs' history; no `specs/*/measurements*.json` command runs or names the file; `docs/guards.md`'s two rows repointed, one of which named a test file that no longer exists (observed 2026-11-12, method: `git grep close_check`). The checks: `make static` clean on 20 crates, `make rust-test` green (`reviews` 95 tests, `cohort` 58, `arbiter` 34, `plan` 118, the guard 555), `make hooks-test HOOKS_ALL=1` green on 54 suites, `check tool-signals`, ruff and the pointer check clean (observed 2026-11-12, method: those commands).

<!-- plan-archive: archived 2026-11-12 -->
### T127 Approach (checklist part A)

1. **The goal, in the world.** The closing check is Rust, gm-review asks it in process, nothing runs the `.py`.
2. **The constraints.** FR-001, FR-002 and FR-003, the T065 clause for the one seam left to Python.
3. **Where each comes from.** G: the standing approval to delete ported Python; R: T91's plan review and the rulings; O: the differential and the census above.
4. **Do they describe the world here?** Run on every real feature directory in this clone, measured 2026-11-12 (`/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t127/diff.py`).
5. **The order.** After T91, whose by-path run it retires.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential's 1,645 cases with its 2 explained differences, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No.

<!-- plan-archive: archived 2026-11-12 -->
### T90 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T90 Approach (checklist part A)

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

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T91 to T82 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->
<!-- plan-archive: T91 to T91 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-12 -->
### T130 (the deletion and retire classes of `ask:449-phase3-remainder`)

- **Approach**: the files nothing runs deleted unported, and every recorded measurement command that runs a script and fails today or invokes deleted code retired with its values kept and its script deleted, as the ruling's Q4 and Q5 have it.

   **Decisions** (`ask:449-phase3-remainder` Q4 and Q5, FR-001, the GM 2026-11-09: "I don't think we need to port the past feature harnesses if those are not still used."):
   - The deletion class, 48 files, 6,160 lines: the census's 44 dead files under `specs/`, `l7r/diagram/tools/caption_decl.py` and `hit_share.py`, `scripts/measure/uncovered-in-diff.py` and `uncovered_marks.py`; and 63 shell scripts under `specs/` (257 lines) that run only those files. Each confirmed at HEAD before deletion: every hit of its path, and of its path within its feature, over the Makefile, `*.mk`, `*.sh`, `*.py`, `*.rs`, `.claude/` and every `specs/*/measurements*.json` was a file deleted with it, the specs' history or a false match on a shared name (observed 2026-11-12, method: `git grep -n -F -e <path> -e <feature-relative path>` per file, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t130/results.tsv`).
   - The retire class: each recorded `command` that `make figures` runs, that runs a script or a Python test (`python3 <file>`, `python3 -c`, `make spec-harness`, `make test-file`, `make -C .claude/skills/diagram ...`), and that fails today or invokes deleted code, is rewritten to `<retired: ask:449-phase3-remainder, <why>>` with its values kept, and the script it ran is deleted unported with any harness or counts file only it ran: 27 files, 2,950 lines, 4,367 entries across 18 features (the hotspot passes 278, 281, 284 and 297 hold 4,271 of them, sharing ten commands), each command run once in a scratch clone with a 90 s bound and its failure recorded (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t130/results.tsv`). 387's four placeholder commands are retired; 276's `measure_before_five.py` failed (its base commit is no object in any clone) and joins; 340's `harness.py` joins, as the ruling names. `m:recorded-python-commands` falls from 4,398 commands in 22 files to 48 in 13 (observed 2026-11-12, method: the measurement's own command before and after).
   - The class read as the commands that run a file: the ruling's test names "a command make figures runs that fails ... or that imports or invokes deleted code", and its consequence, "its file is deleted unported, together with any harness or counts.py that only it runs", is a command that runs a file; the question it answered (Q4) named the harnesses `make figures` starts. About 70 failing commands that run no file are reported and not retired: greps of paths under the old skill directory (35, in 261), greps and `ls` whose text moved or whose renders a fresh clone lacks (the maps' SVGs are not tracked, so they pass in a working clone), prose with shell syntax, 375's three `make feature-report ... TRANSCRIPT=` on transcripts no longer on disk, and one prose entry in this feature's own file (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t130/results.tsv`). Retiring them is not what the ruling's class deletes; a stale grep is the measurement's own record, not a Python port's remainder.
   - Kept: the working measurement scripts T139 ports (238 `inventory_shares`, 239 `change_size`, 242 `inventory_census` and `note_census`, 261's five, 430 `full_reasons`, 432 `triage_price`), 335's `harness.py` (phase 4, T140), and `tooling_reuse_time.py`, whose three 383 commands pass today (rc 0), for T140's commit (observed 2026-11-12, method: each run once in the scratch clone). Shell scripts under `specs/` that run no dead file stay, listed in the record.
   - `make figures` over the touched features before and after: failed-run lines from 68 to 35, retired and placeholder lines from 2 to 32, no moved count and no out-of-band timing either side (observed 2026-11-12, method: `l7r-gate measure figures` in a shared scratch clone, `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t130/figures-before.log` and `figures-after.log`). The live pointers to deleted files fixed (`docs/iteration-loop.md`, the `pyproject.toml` comment, `scripts/record/sources.py`'s docstring, `l7r/diagram/tools/CLAUDE.md`, `scripts/CLAUDE.md`); history in `specs/` prose, `dev/phase-2-close.md`, pool notes and test fixtures left as written. The checks: `make static`, `make hooks-test` (3 suites run, green) and the pointer check clean (observed 2026-11-12, method: those commands).
   - The landing is GATED: two of the deleted files are under `l7r/` (`tools/caption_decl.py`, `hit_share.py`).

### T130 Approach (checklist part A)

1. **The goal, in the world.** No file nothing runs, and no recorded command that runs a broken script, left for a port.
2. **The constraints.** FR-001, `ask:449-phase3-remainder` Q4 and Q5, the GM's 2026-11-09 words.
3. **Where each comes from.** G: the GM's words; R: the ruling; O: the census and each command's run.
4. **Do they describe the world here?** Each file and command tested at this clone's HEAD, measured 2026-11-12 (`/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t130/results.tsv`).
5. **The order.** After T129, before the phase-3 ports, so they port only what runs.
6. **The exits.** Green: `make static`, `make hooks-test` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `m:recorded-python-commands` at 48, and `make figures`' failed runs from 68 to 35.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No.


<!-- plan-archive: archived 2026-11-12 -->
### T134 (the work budget's tools no task held, `ask:449-phase3-remainder`)

- **Approach**: `scripts/reviews/work_budget_bundle.py` and `scripts/budget_change.py` ported whole, no door, into the gate's `trials` crate beside `measure work-budget` (`measure/work_budget_bundle.rs` with `derivation.rs`, `code.rs` and `pyast/`; `measure/budget_change.rs` with `rules.rs`: `l7r-gate work-budget-bundle`, `l7r-gate budget-change`), every caller repointed and both `.py` deleted in the same cut.

   **Decisions** (`ask:449-phase3-remainder`, `ask:449-usage-text`, FR-001, FR-002, FR-003):
   - Where it lives: `trials`, beside `measure work-budget`, so `budget-change` reads `sizes` in process where the Python imported it. One writer of each file, unchanged: `measure work-budget --write` writes `dev/work-budget.md` and the run files, `budget-change` writes `dev/work-budget.json` and `dev/work-budget-changes.jsonl`, and `cohort`'s view only reads (observed 2026-11-12, method: each tool's writes read from its code).
   - The callers: the Makefile's `work-budget-bundle`, `budget-set`, `budget-change`, `budget-accept` and `budget-program` run the gate commands with their arguments as they were. `phase_sources.py`, which stays Python until T131, runs `work-budget-bundle --sources PHASE --root R` once by command where it imported the module, a JSON list of the stage's paths on stdout, a failure raising as the import's did. The flag is `--sources`, not `--old-code`, which made `--o` ambiguous with `--out` under argparse's prefix rule (observed 2026-11-12, method: the differential, both names tried). Neither Python tool recorded a usage line, so neither command does.
   - The audit reads the engine's Python with a parser in Rust (`pyast`): MODE BUDGET reads today's code names from the 110 `.py` files under `l7r/`, and the audit follows calls from older runs' keys in `labels/*.py`, the bundle's `code/` list ordered as `ast.walk`'s breadth-first walk orders it, so the parse needs CPython's tree shape and each call's depth, which the guard's `pylex` (no indentation, no numbers) cannot give. It is not `ask:449-T82-claims`' refused route (b): that route would have stored a Rust `ast.dump` as the `.py` units' fingerprints in `dev/claims-index.json`, which must equal CPython's byte for byte; `pyast` stores nothing, only reads structure within a run, and goes with the last Python it reads, the engine's, in phase 4. Checked against CPython's `ast` on 1,038 files (the standard library, the repository's `.py` and 197 snippets, 55 of them syntax errors): definitions, scope names, imports and calls in walk order, none differing (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t134/pyast/`).
   - Non-finite figures: what Python's `float()` takes for a figure (`inf`, `nan`, `1e999`, any case and sign) is taken, written into `dev/work-budget.json` and its log as `json.dumps` wrote it (`Infinity`, `-Infinity`, `NaN`), and read back where a value stands as `json.loads` read it, carried through `serde_json` as a marker string. The older reader `measure work-budget` (T77) reads that table with plain `serde_json` and would report it unreadable if a non-finite figure were ever written, as it would have under the Python writer.
   - The audit's seven 444 arbiter fixes, whose named Python tests are deleted with the file, are held by named Rust tests (`sink-round-9`, `T16-field-audit-5` and `-6`, `T02-water-round-6`, `T02-field-round-8`, `budget-standard`, `polder-sizes`), the arbiter's log left as written.
   - The same outputs (FR-002): HEAD's Python against the Rust, each case set up identically, exit, stdout, stderr and every file written compared: MODE BUDGET on all 49 derivations and MODE AUDIT on every stage with and without the funnel budget, 103 cases, none differing; `budget-change`, every verb, refusal and status on copies of the real table, log, runs, 444's derivations, verdicts and arbiter log, with every figure spelling and a table holding non-finite figures, 471, none; the bundle on scratch trees, every form refusal and audit reading and each raise, 192, none; `phase_sources.sources` before and after on real and scratch trees, 129, none, 10 raising on both sides (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t134/harness.py`, its `results-*.json`). Normalizations: stderr where both sides exit nonzero and the Python's is a traceback or an argparse usage error (`ask:449-usage-text`, `ask:449-T77-bad-since`), exit and stdout still compared, 124 cases (the bundle 44 tracebacks and 5 usage errors, `budget-change` 48 and 27, the real tree none). Divergences no case reaches: `-h` exiting 2, non-ASCII digits, a glob character in a stage name, serde's float reading without round-trip.
   - Timing: the real tree 27.4 s of process time in Python against 8.0 s in Rust, `budget-change` 20.7 s against 7.2 s (observed 2026-11-12, method: `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t134/harness.py`).
   - The census at the cut: provenance comments and history (specs, 444's arbiter log, `dev/review-ledger.md`); no `specs/*/measurements*.json` command runs or names either file, at HEAD or after the cut, so FR-001's rewrite of a recorded command owes nothing here (observed 2026-11-12, method: `git grep -n -E "work_budget_bundle|budget_change" HEAD -- 'specs/*/measurements*.json'` and the same over the working tree, no hit either side); nor does anything else run them (observed 2026-11-12, method: `git grep -E "work_budget_bundle|budget_change\.py"` over the Makefile, `*.mk`, `*.sh`, `*.py`, `*.rs`, `.claude/`, `tests/`, `docs` and `dev`), and nothing imports `budget_change` as a module, at HEAD or after the cut (observed 2026-11-12, method: `git grep -E "import +budget_change|import_module\(.budget_change"` and the `from ... import` form over `*.py`, `*.rs`, `*.sh` and the Makefile, at HEAD and on the working tree). The checks: `make static` clean on 20 crates (`trials` at 100% line coverage), `make rust-test` green (`trials` 104 tests, the guard 556), `make hooks-test HOOKS_ALL=1` green on 54 suites, `check rust-tooling`, ruff and the pointer check clean (observed 2026-11-12, method: those commands).

### T134 Approach (checklist part A)

1. **The goal, in the world.** The work budget's bundle and its changes are Rust, one writer of each file.
2. **The constraints.** FR-001, FR-002 and FR-003, `ask:449-phase3-remainder`, feature 443's budgets and the budget-change guard they serve.
3. **Where each comes from.** G: the standing approval to delete ported Python; R: the rulings; O: the differential and the census above.
4. **Do they describe the world here?** Run on every derivation and stage this clone's record holds, measured 2026-11-12 (`/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/t134/harness.py`).
5. **The order.** After T130, before the task gate (T131), whose `phase_sources` it serves.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The differential's 895 cases and the parser's 1,038 files with none differing, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No.


