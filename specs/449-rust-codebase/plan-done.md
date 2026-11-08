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

<!-- plan-archive: T002 to T002 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T003 to T003 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T004 to T004 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-07 -->
### T001-T005 - the foundation (phase 1, work breakdown 1-4)

Decisions carried: the workspace of crates by phase (Structure Decision) - a root `rust/Cargo.toml` naming `phases` and
`guard`, `rust_checks.py` running each member and skipping the workspace's own manifest, which builds nothing itself; `serde_json`
added (Complexity Tracking); AMENDED 2026-11-07 starting T003: `fancy-regex` added for the guards' patterns (research R8); the protocol and its merge (D1, D2, contracts/guard-protocol.md); the shared state kept and
the facts asked once (D5, D6); the wrapper keeping the last good binary (D7); the settings switch landed with an empty guard list,
its own cost recorded as phase 1's floor (work breakdown 4).

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

<!-- plan-archive: T002 to T002 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T003 to T003 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T004 to T004 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T005 to T005 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-11-07 -->
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

<!-- plan-archive: T002 to T002 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T003 to T003 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T004 to T004 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T005 to T005 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
