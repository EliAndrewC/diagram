# Implementation Plan: A Rust codebase

**Branch**: none - `main`, `SPECIFY_FEATURE=449-rust-codebase` | **Date**: 2026-11-07 | **Spec**: [spec.md](spec.md) (FAITHFUL, round 5)

**Input**: Feature specification from `specs/449-rust-codebase/spec.md`; research in [research.md](research.md).

## Summary

Every Python file the repository tracks, and the Python run inline in its Makefile and shell, is replaced by Rust in four phases
ordered by measured cost: the guards (phase 1), the gate (2), the tooling (3), Mode A and the page writer (4). Each piece's Python runs
until its replacement gives the same verdicts on every case its tests hold, and is deleted in the commit that switches. Phase 1 is
planned here to the task; phases 2-4 to their approach, each planned to the task when it opens (a plan amendment reviewed by
`spec-fidelity`, as every plan here is).

## Technical Context

**Language/Version**: Rust (the toolchain `rust/phases` builds with today, `$HOME/.cargo/bin/cargo`), edition 2021.

**Primary Dependencies**: the standard library first. `serde_json` for the hook protocol's JSON (phase 1), since every guard reads
and writes JSON and a hand-written reader is a defect surface (`rust/phases`' spec reader is deliberately small and reads one shape);
`fancy-regex` for the guards' patterns, 43 of which use lookaround or backreferences (research R8, the amendment of 2026-11-07,
found starting T003). Each further crate is named in its phase's amendment with what it replaces.

**Storage**: files only, as today - the guard log, the transcript (read), the session clone map, `.git/` state.

**Testing**: `cargo test` through make (`make rust-test`), every line and function reached (`rust_checks.py cover`, FR-004); during
phase 1 each guard suite (`tests/hooks/test-<guard>.sh`) drives the Rust guard as its verdict replay (R4).

**Target Platform**: the dev container (Linux), and the CI image for the gate's phases.

**Project Type**: a Cargo workspace: `rust/phases` (the hamlet stages, feature 444) and one crate a phase's tools (phase 1:
`rust/guard`, the binary `l7r-guard`).

**Performance Goals**: the spec's success criteria against the recorded figures - SC-001 (`m:hooks-bash`), SC-002
(`m:done-rust-edit`), SC-003 (`m:suite-cpu`).

**Constraints**: make is the one entry point (FR-005); a guard that cannot run fails open, saying so (research R6); no piece runs as
both Python and Rust (FR-003).

**Scale/Scope**: 872 tracked Python files and 300 inline Python sites in 93 files (`m:python-census`, `m:inline-python-census`);
phase 1 is the 44 registered repository guards (`m:registered-guards`; 26 of them take a Bash call, `m:hooks-bash`) and everything
FR-001 gives it: the 44 files and 6,258 lines of guard shell, the 33 files and
9,053 lines of their Python libraries, the 53 suite files with their four Python helpers (`hookbench.py`, `hookdeps.py`,
`hooktrace.py`, `test_hooks_cases.py`), and the inline Python of `scripts/hooks/` and `tests/hooks/` (34 and 41 sites)
(`m:guard-sources`, `m:inline-python-census`).

**Single-artifact target**: none - this feature draws no map. Phase 4's Mode A sheets are each regenerated and checked as the
artifact of their own task when that phase is planned.

## Performance bookends

Not a generator change through phase 3: no map is rolled, so no `make perf` bookends. Each phase ends with its own measurement against
the spec's figures (FR-010): the phase's `m:` commands re-run and recorded beside the original values in `measurements.json`, the phase
not closed while its success criterion is unmet. Phase 4, which ports Mode A's planner, takes the bookends for the sheets it moves.

## Constitution Check

- **I, II** (viewports, design): N/A - no UI in this repository.
- **III** (pool data conventions): N/A - no generated pool content of a recurring kind; phase 4 regenerates the Mode A sheets, their
  format unchanged.
- **IV, V** (GM source, SOURCE blocks): N/A - no SOURCE block added, moved or touched.
- **VI** (verify before done): PASS - each phase-1 task names its verification: its guard's suite against the Rust guard (every case
  the shell guard passes), `make rust-test` and `cover` green, `make hooks-test` green, and the guard's timing re-run; the phase closes
  on `m:hooks-bash` re-measured (SC-001). No map changes, so no map review is owed.
- **VII, VIII, IX** (generation, voice, setting): N/A - no content generated or written in-world.
- **X** (discipline): PASS, read for Rust as the crate holds it today - clippy `-D warnings` with pedantic, rustfmt, every line and
  function covered (FR-004), red-green for each guard (the suite case fails against an empty Rust guard before its decider lands),
  functions under 100 lines (clippy's `too_many_lines`), files under ~1,000 lines split into module folders with a `CLAUDE.md` index.
  No overlap check is added. The Python that remains during the port keeps clause 10's rules until it is deleted.
- **XI** (kanji triangle): N/A - no kanji.
- **XII** (historical grounding): N/A through phase 3 - nothing asserts about the world; phase 4's port of Mode A holds every sheet
  to its checks and its research claims (FR-002), the claims carried to the Rust code that keeps them.
- **XIII** (no known regressions): PASS - FR-002's verdict replay is the regression test of each piece; the gate's seeds and suites
  run on every phase's landing.
- **XIV** (fix defects where found): PASS - FR-002's exception: a guard that refuses correct work is fixed in its port, its case's
  verdict changed in the same commit and named (two such were found 2026-11-07: the make-only guard read a `grep` pattern naming
  `pytest` as a pytest run; the guard-file guard read a scratch file's text naming `x-hooks.sh` as a guard write).
- **XV, XVI** (behavioral; literal reading): PASS - the plan does what the spec says; the one exception (XIV) is the spec's own.

## Phases

### Phase 1 - the guards (Story 1, P1)

**Approach.** One binary, `l7r-guard`, replaces the 44 registered repository guards (`m:registered-guards`). `.claude/settings.json` calls it once for each hook event
(`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `SubagentStart`, `PostToolUseFailure`) through the wrapper
of research R6, instead of one shell per guard. It reads the input once and runs, in a fixed order, the deciders of the guards whose
matcher takes the tool, then merges their answers by `contracts/guard-protocol.md`: every refusal reported together, rewrites applied
in order, notices joined.

**Decisions.**
- D1 - ONE PROCESS (R1, R2): every check in-process; a decider is a pure function of the parsed input and the facts it asks for.
- D2 - A FIXED ORDER: the guards' order in today's settings, so the merged answer is the same each time; a rewrite is seen by the
  deciders after it.
- D3 - GUARD BY GUARD (FR-003): the dispatcher lands first with no guard in it; each guard then moves in its own commit, which removes
  its shell entry from the settings in the same commit that adds its Rust decider, after its suite passes against the Rust guard.
  No guard is ever both.
- D4 - THE SUITE IS THE REPLAY (R4): `tests/hooks/test-<guard>.sh` runs with `HOOK` pointed at `l7r-guard --only <guard>`;
  every case must pass before the switch. The Rust decider's own unit tests are written beside it, under a tenth of a second each
  (FR-008), from the suite's cases.
- D5 - SHARED STATE KEPT (R5): the guard log's line format, the escape tokens and their reason rule, the transcript and clone-map
  reads, ported first as the library every decider uses.
- D6 - ASK ONCE (R2, FR-006): a fact several deciders need - the clone, the session's name, the transcript's GM messages, a `git`
  answer - is read once per process and handed to every decider; the work-budget practice of pinning counts is used for these reads.
- D7 - THE BINARY FROM ITS OWN TREE, THE LAST GOOD ONE KEPT (R6): the wrapper runs the binary built from the tree it is in, building
  it when its sources are newer, and keeps a copy of each build that passed its own self-check (`l7r-guard --self-check`: every
  guard's decider answers a fixed input); a failed build runs the last good binary, so a broken build leaves the previous guards
  standing rather than none. Only with no good binary ever built does the call go through, with a notice and a guard-log line - the
  outcome Claude Code gives a crashing hook today: its hooks documentation makes exit 2 the only blocking exit, any other failure a
  non-blocking error shown and passed. A guard's change cannot reach main unbuilt: `make land-tooling` runs `make hooks-test`, which
  builds and replays it.

**Order of the guards**: by measured cost first (R2): `pair-hooks`, `gate-hooks`, `measure-hooks`, `no-poll-hooks`,
`main-tree-hooks`, `record-edit-hooks`, then the rest in settings order. The two guards that refuse correct work (Constitution Check
XIV) are fixed as they move.

**Work breakdown** (each line becomes tasks in `tasks.md`):
1. The Cargo workspace: `rust/guard` beside `rust/phases`, `make rust-test`/`lint`/`cover` over both.
2. The protocol (contracts/guard-protocol.md): input parse, the three answers, the merge, exit codes - with the dispatcher and no guard.
3. The shared library (D5): guard log, escapes, transcript and clone-map reads, the facts read once (D6).
4. The wrapper and the settings switch (D7), landed with an empty guard list - its timing is the floor.
5. One task a guard, in the order above: its decider, its unit tests, its suite replayed, its shell and settings entry removed.
6. The libraries left unused deleted (`scripts/hooks/lib/hm_*.py` as each last caller moves).
7. The suites' own Python (FR-001: "each `tests/` file with the piece it tests", and `tests/hooks/`'s inline sites in phase 1): the
   41 inline sites in `tests/hooks/*.sh` replaced as each guard's suite is replayed (a JSON input built by `l7r-guard`'s test helper
   or by plain shell, a field read by the binary), and the four Python helpers ported to the guard crate - `hookdeps.py` (which suites
   a change makes stale) and `hooktrace.py` (which guards a session ran) as `l7r-guard deps` and `l7r-guard trace`, `hookbench.py` as
   `l7r-guard bench`, `test_hooks_cases.py`'s cases as the guard crate's tests.
8. The close: `m:hooks-bash` and `m:pair-hooks-suite` re-run (SC-001, US1-3), and phase 1's share of BOTH censuses (FR-001: every
   `.py` under `scripts/hooks/` and `tests/hooks/`, every inline site in those two trees) returns nothing; recorded.

<!-- plan-archive: T001 to T005 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T049 to T049 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
### T050-T052 - the suites' tooling and the close (phase 1, work breakdown 6-8)

Decisions carried, none new: the four `tests/hooks/` Python helpers ported as `l7r-guard` subcommands and crate tests (work
breakdown 7); the unused libraries deleted with their last caller (work breakdown 6); the close on SC-001 and phase 1's share of both
censuses empty (work breakdown 8, FR-010).

<!-- plan-archive: T001 to T001 moved to plan-done.md, 2026-11-07 (feature 375 FR-044) -->
<!-- plan-archive: T006 to T049 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
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
### T028 Approach (checklist part A)

1. **The goal, in the world.** `make-only-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-005 (the guard covers the replacements' binaries as it covers the Python and cargo today), FR-008 (each unit test under a tenth of a second).
3. **Where each comes from.** `tests/hooks/test-make-only-hooks.sh`, the guard's own suite; plan D3-D4. The constitution XIV fix named in its commit and in the phase's record (FR-002).
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-make-only-hooks.sh` green against `l7r-guard --only make-only-hooks`, with new cases for FR-005 - a direct Bash run of a replacement's binary (`l7r-guard`, `hamlet`, from the cargo target directory or by path) refused with the make target that runs it, as a bare `cargo run` is today - `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-make-only-hooks.sh` passes against the Rust guard; `scripts/hooks/make-only-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T029 Approach (checklist part A)

1. **The goal, in the world.** `guard-file-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
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

### T036 Approach (checklist part A)

1. **The goal, in the world.** `house-style-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
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

### T044 Approach (checklist part A)

1. **The goal, in the world.** `escalation-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
3. **Where each comes from.** `tests/hooks/test-escalation-hooks.sh`, the guard's own suite; plan D3-D4.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After T005; in the plan's order (the measured cost first, research R2), independent of the other guards.
6. **The exits.** Green: `tests/hooks/test-escalation-hooks.sh` green against `l7r-guard --only escalation-hooks`, `make rust-test` and `cover` green, `make hooks-test` green. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** every case of `test-escalation-hooks.sh` passes against the Rust guard; `scripts/hooks/escalation-hooks.sh` and its settings entry are gone in the commit that registers the decider.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T045 Approach (checklist part A)

1. **The goal, in the world.** `review-round-hooks`'s verdicts given by the Rust guard, its shell gone.
2. **The constraints.** FR-002 (every suite case's verdict the same, XIV's fix named), FR-003 (never both), FR-008 (each unit test under a tenth of a second).
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
### T050 Approach (checklist part A)

1. **The goal, in the world.** the suites' own tooling - which suites a change makes stale, which guards a session ran, the bench, the shared cases - in Rust.
2. **The constraints.** FR-001 (phase 1's `tests/hooks/` Python), FR-008.
3. **Where each comes from.** plan work breakdown 7; `m:guard-sources` (the four helpers).
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After the guard tasks that use them.
6. **The exits.** Green: `make hooks-test` keyed by `l7r-guard deps`, its results unchanged; the four `.py` files deleted. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** no `.py` under `tests/hooks/`. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten to the port in the same commit and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T051 Approach (checklist part A)

1. **The goal, in the world.** no guard library outlives its last caller.
2. **The constraints.** FR-001, FR-003.
3. **Where each comes from.** plan work breakdown 6.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** After every guard task.
6. **The exits.** Green: `make audit` and `make guard-log` reading the Rust lines unchanged; no `.py` under `scripts/hooks/`. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
9. **Done, measured.** no `.py` and no inline Python under `scripts/hooks/`. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten to the port in the same commit and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T052 Approach (checklist part A)

1. **The goal, in the world.** phase 1 closed on its measured outcome.
2. **The constraints.** SC-001, FR-010, FR-001 (phase 1's share of both censuses).
3. **Where each comes from.** plan work breakdown 8; `m:hooks-bash`, `m:pair-hooks-suite`.
4. **Do they describe the world here?** Tooling: the guards on Claude Code's tool calls; no researched value moves.
5. **The order.** Last.
6. **The exits.** Green: the figures re-run and recorded beside their first values, SC-001 met, both censuses' phase-1 share empty. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing (`make land-tooling`): no work budget, nothing rolled.
   **Carried into phase 1's record:** the one suite case whose expected verdict changed, `test-wakeup-hooks.sh`'s input that is not JSON, by the round arbiter's ruling `ask:449-T038-garbage` (FR-002).
9. **Done, measured.** SC-001 met: the guards before a Bash call decide it in under a tenth of today's slowest guard's time. The phase's measurements recorded in `dev/` as well as beside their first values (FR-010), and the record naming the two constitution XIV fixes (FR-002).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### Phase 2 - the gate (Story 2, P2)

**Approach.** The gate's own Python path moves to a Rust binary the Makefile calls: `l7r/diagram/ci/` (the test planner, the
verification state, the stamps), the gate's scripts in `scripts/gates/` and `scripts/measure/`, `_invocation.py`, `switches.py`, and the
inline Python of the Makefile's gate recipes, `sync-with-main.sh`, `land-tooling.sh` and `buildspec/run.sh`. While Python tests remain,
the planner keeps choosing them; the Rust-only route (a Rust-only delta runs the Rust checks and the few text checks over `.rs` files,
no pytest) lands early in this phase, since it is most of SC-002. Planned to the task when the phase opens.

### Phase 3 - the tooling (Story 3, P3)

**Approach.** The rest of `scripts/` (record, reviews, pages, measure), `l7r/diagram/tools/`, `pipeline/`, the small engine helpers,
every `.py` file under `specs/` and the inline Python of the shell scripts under `specs/`, every recorded measurement that runs Python
(FR-001's rewrite rule), the inline Python of the Makefile's other recipes (every recipe phase 2 does not take), and
`.specify/scripts/bash/`'s inline Python. One crate a family of tools; each tool's tests rewritten as Rust tests, its one end-to-end test kept. Planned to the task
when it opens.

### Phase 4 - Mode A and the page writer (Story 4, P4)

**Approach.** Mode A's planner (`compound*`, `labels/`, `buildings/`, `dwellings.py`, `well_gear.py`), the Mode A sheets' generators
under `pool/`, `interactive/`; then the containers' Python (`Dockerfile.ci`, `setup-dev-env.sh`, the four lockfile pairs, `pyproject.toml`'s
tables) and `l7r/diagram/__init__.py` last. Every sheet regenerated and held to its checks and research claims, the performance
bookends taken. The close is SC-005: both censuses empty, `make done` and `make figures` with no Python interpreter.

## Project Structure

### Documentation (this feature)

```text
specs/449-rust-codebase/
├── spec.md, request.md, measurements.json
├── plan.md              # this file
├── research.md          # R1-R7
├── data-model.md        # the piece, the decider, the answer, the verdict replay
├── contracts/
│   └── guard-protocol.md
├── quickstart.md        # how to run, test and time phase 1
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
rust/
├── Cargo.toml            # the workspace (phase 1)
├── phases/               # the hamlet stages (feature 444), unchanged
└── guard/                # phase 1: the l7r-guard binary
    ├── CLAUDE.md         # the index
    └── src/
        ├── main.rs       # the event's input in, the merged answer out
        ├── protocol.rs   # parse, answers, merge (contracts/guard-protocol.md)
        ├── shared/       # guard log, escapes, transcript, clone map, facts read once
        └── guards/       # one module a guard, in the fixed order
scripts/hooks/l7r-guard.sh   # the wrapper (D7)
tests/hooks/                 # the suites, the verdict replay through phase 1
```

**Structure Decision**: a workspace of crates by phase, so a guard's edit rebuilds the guard crate and not the hamlet stages
(feature 444 T43's build measurements apply).

## Complexity Tracking

| Choice | Why | Simpler alternative rejected because |
|---|---|---|
| `serde_json`, the first external crate | every guard reads and writes the hook protocol's JSON | a hand-written reader for an open-ended input shape is a defect surface; `rust/phases`' reader reads one fixed spec |
| `fancy-regex`, the second crate (research R8) | 43 of the guards' patterns use lookaround or backreferences (`m:guard-regex-features`), which the `regex` crate lacks; `fancy-regex` reads them verbatim, and each guard's suite replay proves its verdicts unchanged (FR-002, D4) | a hand-written parser for each pattern would re-prove every verdict case by case; kept only for a pattern a profile shows hot, in its guard's task |
| the last good binary kept, failing open only with none (D7) | one binary is every guard, so a failed build must not turn them all off; Claude Code's own rule passes a crashing hook (exit 2 alone blocks) | failing closed would lock the GM's session out of every tool call on a build error, with no recovery from inside it; failing open on every failed build would turn every guard off at once |
