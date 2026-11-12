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
<!-- plan-archive: T050 to T052 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T011 to T011 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T043 to T043 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T048 to T048 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
### Phase 2 - the gate (Story 2, P2)

**Approach.** The gate's own Python path moves to a Rust binary the Makefile calls: `l7r/diagram/ci/` (the test planner, the
verification state, the stamps), the gate's scripts in `scripts/gates/` and `scripts/measure/`, `_invocation.py`, `switches.py`, and the
inline Python of the Makefile's gate recipes, `sync-with-main.sh`, `land-tooling.sh` and `buildspec/run.sh`. While Python tests remain,
the planner keeps choosing them; the Rust-only route (a Rust-only delta runs the Rust checks and the few text checks over `.rs` files,
no pytest) lands early in this phase, since it is most of SC-002. Planned to the task when the phase opens.

**Planned to the task, 2026-11-08** (phase 1 closed: `dev/phase-1-close.md`). About 18,000 lines (observed 2026-11-08, method: `git ls-files` and `wc -l` over the four areas): `l7r/diagram/ci/` 3,607, `scripts/gates/` 8,503 in 38 files, `scripts/measure/` 6,126 in 34, `_invocation.py` and `switches.py` 612. The order is by measured gain and by what each port stands on: the Rust-only path first, since pytest is most of the one-line edit's gate (`m:done-rust-edit`), then the crate, then leaf first by what imports what (`ask:449-T062-order`): the code id, the delta and the state, the decision and the remote path, then the checks, then the pytest-driven planner, then the close. Each task's decisions are written when it starts, as phase 1's were. Each piece's Python runs until its replacement gives the same verdicts on every case its tests and its suites hold, and is deleted in the commit that switches. FR-001 also places six more here by name: `hm_conflict.py` and `own-make.sh`, in T067 beside the push checks that call the first and `one-gate.sh` that calls the second; and the suites `test-entry-gate`, `test-claims-gate`, `test-cohort-gate` and `test-land-tooling`, in T069 with the gate scripts they test.

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

<!-- plan-archive: T060 to T060 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
### T061 Approach (checklist part A)

1. **The goal, in the world.** One binary the gate's recipes call, as the guards have one.
2. **The constraints.** FR-001, FR-003, FR-004, FR-005.
   **Decisions** (2026-11-08):
   - (a) THE CRATE HOLDS ONLY WHAT SOMETHING CALLS: `rust/gate` starts with its command line and `--version`. The shared facts the plan names (the repository's paths, the run record's format, git in one place) arrive with the first port that reads them, T062: `make static`'s dead-code check refuses a public function nothing calls, and a helper written ahead of its caller is one written against a guess.
   - (b) THE WRAPPER FAILS CLOSED: `scripts/gates/l7r-gate.sh` builds the binary from its own tree when a source is newer and refuses when the build fails. The guards' wrapper fails open and keeps a last good binary, because a broken build must not turn every guard off (plan D7); a gate that cannot build its tool must not pass, and a make recipe can wait on the build where a hook could not. No self-check is run: `--self-check` exists to protect that last good copy, and this has none.
3. **Where each comes from.** `m:guard-sources`' method; plan D5-D7 as they held for the guards.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** As the phase's plan above; each stands on the ones before it.
6. **The exits.** Green: `make static` holds the crate at the coverage floor, the binary built from its own tree, a failed build failing the call. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** A `make` recipe reaches the binary and its coverage is the crate's floor. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T061 part B (2026-11-09T01:17:42Z)

1. **What exactly is refusing?** Two checks of the gate, both on the new files themselves: `test_claims_coverage` read `rust/gate/` as engine code owing research claims, and `check-tool-signals` asked the new wrapper how it records its runs. Neither is a rule about the crate's behavior; each is a roster that did not yet know the crate.
2. **A3 again.** Green: both rules are the repository's own, unchanged.
3. **A4 again.** The claims rule describes the hamlet engine; `rust/gate`, like `rust/guard`, is tooling, so it joins that exclusion. The record rule describes tools that decide; a launcher records through what it launches, as its statement says.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: two rosters, one line each.
6. **The one-sentence test.** "The new tooling crate was told it is tooling." The GM would not ask why.
7. **The next step is a measurement.** `make done` green on hooks-test and test-full, as the round arbiter's ruling on the two reds names.
8. **Before offering routes.** None offered.
9. **After a ruling.** The next step is the one it names: the failing case run directly, the fixes confirmed in the commit, then the gate.

<!-- plan-archive: T062 to T062 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
### T063 Approach (checklist part A)

1. **The goal, in the world.** What a change owes and what the gate saw are answered by one implementation.
2. **The constraints.** FR-001, FR-002, FR-003 (one writer, one cut), FR-006 (one spawn a process or a batch).
   **Decisions** (the round arbiter's `ask:449-T063-slices`: three slices, each landing whole with its own decisions, differential and review):
   - (slice 1, 2026-11-09) THE CONTENT ID MOVES, UNPORTED: `content_id`, `git_blob_id`, the kept cache and `_git_dir` move from `gate-stamp.py` into `codeid.py`, which `ask:449-T062-py-id` already places in phase 4, as the one Python library for callers ported later; `gate-stamp.py` keeps thin functions that delegate, so no caller changes and no answer can. `m:t063-slice1`: every area's key and every id equal before and after.
   - Slice 2, below, lists every remaining Python caller of `content_id`, `_area_files` and `AREAS` and which implementation answers each, and deletes `gate-stamp.py`. Slice 3, `state.py`, `runlog.py`, `gate_config.py` and `coverage_exempt.py`, is T72, so that this task's two slices land and tick as one.
   - (slice 2, 2026-11-09) THE COMMAND AND THE DELTA ARE THE RUST GATE'S: `gate-stamp.py` becomes `l7r-gate stamp` (`rust/gate/src/stamp.rs`) and `delta.py`'s list, delta and key become `l7r-gate delta` (`rust/gate/src/delta.rs`); `__main__`'s `cov-scope` and `engine-key`, the Makefile, the push and `make land` switch in that commit and `gate-stamp.py` is deleted. A stamp kept before the switch still verifies: `m:t063-slice2`, every area's key equal, every area's file list equal.
   - WHAT IS LEFT OF `delta.py` IS A CLIENT, not a second implementation: no list, no git call, no hash, only the `Delta` type `decision.py` takes and calls to the binary, once a process or in a batch (item 5), until T064 ports `decision.py` and `dispatch.py` and T071 `incremental.py`. A caller with many paths passes them all at once (`engine_paths`), so no caller spawns per file (FR-006).
   - EVERY REMAINING CALLER AND WHAT ANSWERS IT, from `git grep -n 'gate-stamp' -- . ':!dev/bypass-log' ':!dev/run-log' ':!dev/review-ledger.md' ':!dev/cohort-log'` over every tracked file (the code rows below; prose elsewhere is reworded or is history), and `git grep -nE 'compute_delta|coverage_scope|engine_key|is_engine|ci\.delta|ci import .*delta' -- '*.py' '*.sh' '*.mk' Makefile`, run before the switch: the Makefile's stamp and key recipes, `land.py`, `push_checks.py`, `push_check_times.py`, `review_prereq.py`, `model_trial.py`, `rust/guard`'s `pair_hooks`: `l7r-gate stamp` by the command line; `state.py` `current_hash` and `incremental.py`'s area listing: the binary, once a process (`stamp --key diagram`, `stamp --list diagram`); `incremental.py`, `claims_carry.py`, and the `specs/` harnesses `415` and `430` `replay_plans.py`: `engine_paths`, one batch; `engine_edit.py`: the binary, once a process, only when a review or roll is live, and on `codeid.py` only until its own port in T066 (FR-001 makes it phase 2, so this is no license to stay on the library past that phase); `preflight.py`, `engine_edit.py` for the byte-hashed areas: `stamp --raw-match`, one batch; `state.py`, `dispatch.py`, `__main__.py` `status --route`, `cohort_known.py`: `delta.py`'s client; `decision.py`: the `Delta` type alone; `claims_carry.py`, `record_cache.py` `content_id` and `preflight.py`, `engine_edit.py`, `wording.py` `semantic_bytes`: `codeid.py`, the library slice 1 placed. `specs/131-split-diagram-repo/contracts/split.sh` names the file's pre-329 path in a finished one-off migration, which does not run again.
   - THE CONTENT ID STAYS IN `codeid.py` for those callers, the ruling's second route, chosen because they hold bytes that are no file on disk (a blob, an edit not yet applied) and a call to the binary per id would spawn per file. The differential the ruling names ran on every file of every area: `m:t063-slice2`, 8,885 files (observed 2026-11-09, method: exact comparison), no mismatch.
   - MEMBERSHIP OF A BYTE-HASHED AREA IS PORTED UNCHANGED (FR-002): by pattern, a batch on stdin (`stamp --raw-match`), and an area on the repository root takes `diagram`'s exclusions as `_area_exclusions` gave it. What that leaves, a browser test's docstring edit reading as unseen though the browser key moves on it, goes to the round arbiter (`ask:T063-browser-raw`), not into this slice.
   - THE DIFFERENTIAL: `m:t063-slice2` also holds the engine key over every 4th of the last 200 commits, the worktree key, the delta at seven bases and `is_engine` over every tracked path, and `--raw-match` over the working tree's 26,663 tracked paths after the delete with 7 synthetic paths a pattern must answer for that are on no disk (`is_engine`'s 26,664 is the same index one file earlier, `gate-stamp.py` still in it), all equal to the Python loaded from a detached worktree of the commit before.
3. **Where each comes from.** the state files as they stand; `m:ci-sources`.
4. **Do they describe the world here?** Tooling: the gate; no researched value moves.
5. **The order.** Leaf first by what imports what (`ask:449-T062-order`), each stands on the ones before it; callers reach the binary once a process or in a batch, never one spawn a file (FR-006, SC-002).
6. **The exits.** Green: a stamp kept before the switch still reads; the routes and keys over recorded deltas equal the Python's; no state file has two writers at any commit. Red: what failed recorded, the task set down, a process stop to `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Its landing: no work budget, nothing rolled.
9. **Done, measured.** `make done` reuses a last green result across the switch, and the differential over recorded deltas shows no mismatch. Every `specs/*/measurements*.json` command that runs a file this task ports or deletes is rewritten in the same commit, to the port where it names a ported file and to an equivalent make command where it is inline or prose, and re-run as its proof (FR-001).
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

### T063 part B (2026-11-09T02:57Z)

1. **What exactly is refusing?** One test, `test_no_kept_file_names_a_deleted_package`, on two path strings in the new `rust/gate/src/delta/tests.rs`. It names the file, not the string, so the first fix missed the second.
2. **A3 again.** Green: the rule is the repository's own, unchanged (feature 444 FR-024).
3. **A4 again.** The rule describes kept files naming the deleted hamlet engine; the two strings were example paths in a classifier's test, ported from `test_delta.py`, so they take live examples of the same kinds: an engine `.py` under `l7r/` and a file under `tests/`.
4. **Moving something placed earlier to suit something later?** No.
5. **Tuning or changing?** Neither: two test strings.
6. **The one-sentence test.** "A new test named a package that no longer exists." The GM would not ask why.
7. **The next step is a measurement.** The failing test run directly, then one full gate, as the round arbiter's ruling names; the same test red on another string sweeps every kept file for the six names in one pass.
8. **Before offering routes.** None offered.
9. **After a ruling.** The next step is the one it names: `git grep` over `rust/gate/src` for the six names, the test run directly, then the gate.

<!-- plan-archive: T064 to T064 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->
<!-- plan-archive: T065 to T065 moved to plan-done.md, 2026-11-09 (feature 375 FR-044) -->
<!-- plan-archive: T066 to T066 moved to plan-done.md, 2026-11-09 (feature 375 FR-044) -->
<!-- plan-archive: T067 to T067 moved to plan-done.md, 2026-11-09 (feature 375 FR-044) -->
<!-- plan-archive: T068 to T068 moved to plan-done.md, 2026-11-09 (feature 375 FR-044) -->
<!-- plan-archive: T069 to T069 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T071 to T071 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T070 to T070 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
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

<!-- plan-archive: T72 to T72 moved to plan-done.md, 2026-11-08 (feature 375 FR-044) -->

<!-- plan-archive: T73 to T73 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T77 to T77 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->

<!-- plan-archive: T78 to T78 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->

<!-- plan-archive: T79 to T79 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T80 to T80 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T81 to T81 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T82 to T82 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
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
### T85 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T85 Approach (checklist part A)

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


<!-- plan-archive: T86 to T86 moved to plan-done.md, 2026-11-10 (feature 375 FR-044) -->
<!-- plan-archive: T87 to T87 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: T88 to T88 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
<!-- plan-archive: T89 to T89 moved to plan-done.md, 2026-11-11 (feature 375 FR-044) -->
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

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


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

### T121 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T121 Approach (checklist part A)

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

