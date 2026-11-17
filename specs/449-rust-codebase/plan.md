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
<!-- plan-archive: T83 to T83 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->
<!-- plan-archive: T85 to T85 moved to plan-done.md, 2026-11-16 (feature 375 FR-044) -->
### T122 (the idle-tests suite's waits in fractions of a second, the GM's pre-approval of 2026-11-12)

**Not landed** (its plan review, BLOCKED 2026-11-12): the saving was the suite's alone, not the full hook run's, so it misses the GM's condition ("if you identify concrete targets with significant measured expected savings then go ahead and do them ... Otherwise you can just keep working on the port of the tooling"). The decisions below are the record of what was tried and measured.

- **Approach**: the idle-tests guard's fixture seams `IDLE_WAIT_S` and `IDLE_DEFER_S` take fractions of a second (`seconds_ms` in `rust/guard/src/guards/idle_tests_hooks.rs`, honored only inside a fixture as before), and the suite (`tests/hooks/test-idle-tests-hooks.sh`) waits fractions of a second where it waited whole seconds.

   **Decisions** (the GM's pre-approval in `request.md`, "a fifth efficiency round"; FR-002):
   - Where the suite's time went: the full hook run's longest suite, 35.0 s alone, its cases waiting whole seconds of real time (the timer counts awake time in its own ticks, so a 3-second seam is 3 real seconds), and in a profiled full run its 35.0 s the longest while the run held no pressure on CPU, memory or I/O (stalls of 0.64 s, 17 microseconds and 0.18 s over the run, peak memory 7.75 GB of the 10 GB cap) (observed 2026-11-12, method: the suite under `bash -x` with each line's process and `EPOCHREALTIME`, the main shell's time summed by case and by `check`; `/tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r5/profile.sh`, the cgroup's `memory.current` and the `some` totals of its `cpu`, `memory` and `io` pressure files around `make hooks-test HOOKS_ALL=1`).
   - The change: the seams parse fractions, carried in milliseconds (`seconds_ms`; the real waits stay whole minutes, `minutes_ms`, so a real deferral's message is as before), `wait_awake` folded into `wait_ms`; the suite's tick from 0.2 s to 0.05 s so a fraction stays exact, its waits from 3, 4, 2 and 1 s to 0.3, 0.6, 0.3 and 0.2 s, its two fixed 1.5 s sleeps to 0.8 s and 1.0 s, and its slow runner's 5 s, and the sleep that outlasts it, to 3 s (each a CONVENTION, the fixture's own constant, chosen to keep every case's order of events). Every case and check stays: the suspend case still asks a full wait after the jump (at least 0.35 s, the wait 0.6 s), and the ticker's simulated second a 0.1 s drifts far under the 100 s suspend threshold at the faster tick (the fixture's CONVENTION values, `IDLE_SUSPEND_S=100` in the suite).
   - Measured the same way before and after (SC-007): the suite alone 35.0 s before and 17.3 s, 16.9 s and 17.0 s after, its 34 checks passing each time (observed 2026-11-12, method: `date +%s.%N` around `bash tests/hooks/test-idle-tests-hooks.sh`, at a load of about 3). The full hook run did not move: 52.1 s before, 53.1 s and 54.1 s after, because the other suites slowed inside it, sync-with-main from 28.3 s to 45.5 s and 46.5 s and entry-gate from 24.9 s to 37.6 s and 42.7 s (observed 2026-11-12, method: `/usr/bin/time` around `make hooks-test HOOKS_ALL=1`, its `ran` line). The run is held by something the suites share that the pressure figures do not show, not by its longest suite; the guard wrapper's build lock is not it (it is taken with `-n` and only for a build). So the saving is the suite's own, wherever it runs alone (a change to the idle-tests guard re-runs it alone), and T123's premise, a run bound by its schedule, does not hold.
   - The checks: the guard's tests 555 green and its lines all reached, clippy pedantic clean (the fraction's cast in one function, its saturation a reasoned exception) (observed 2026-11-12, method: `l7r-gate.sh rust test`, `uncovered` and `lint` on the guard).

### T122 Approach (checklist part A)

1. **The goal, in the world.** The idle-tests suite waits only as long as its cases need.
2. **The constraints.** FR-002: every case and check held.
3. **Where each comes from.** G: the GM's pre-approval of 2026-11-12 in `request.md`; O: the profile and the timings above.
4. **Do they describe the world here?** Measured on this clone.
5. **The order.** After T120.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's time above.
10. **Before moving a constant.** The fixture's own tick and waits, none of the guard's real ones.
11. **Before fitting things into room.** Not a room question.

**Performance work?** yes, tooling time, not the generator:
1. **Where does the time go?** Real seconds of waiting the fixture asked for.
2. **Does the change remove work, or only move it?** Removes it: the waits are shorter, the cases the same.
3. **What do you expect it to save, and why?** The suite's waiting, measured above; not the full run's, which another bound holds.
4. **How does the work grow?** With the cases' waits, now fractions.
5. **What did the before and after show, and under what conditions?** Three runs alone and two full runs, on a lightly loaded host.
6. **Did any map move?** No: no engine code changes.

<!-- plan-archive: T123 to T123 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T127 to T91 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->
<!-- plan-archive: T127 to T127 moved to plan-done.md, 2026-11-12 (feature 375 FR-044) -->

<!-- plan-archive: T128 to T128 moved to plan-done.md, 2026-11-16 (feature 375 FR-044) -->
<!-- plan-archive: T135 to T135 moved to plan-done.md, 2026-11-16 (feature 375 FR-044) -->
<!-- plan-archive: T138 to T138 moved to plan-done.md, 2026-11-16 (feature 375 FR-044) -->
### T148 (phase 4's S5, the record's site, `ask:449-phase4-slices`)

- **Approach**: the record site's build and its checks ported into the `research` crate and wired - S1's record library's first production caller: `interactive/record/site.py`, `site_pages.py`, `site_links.py` and `money.py`, `interactive/citations.py` and `glossary_source.py`, `tools/record_asset.py`, `glossary_asset.py`, `footnote_census.py` and `source_tags_contract.py`, and `scripts/gates/memo_check.py` (2,164 lines, observed 2026-11-16, method: `wc -l`), with `record/archive.py`, `blocked.py`, `site_notes.py` and `source_tags.py`, which lost their last importer, deleted - fifteen files; `pipeline/record_build.py` cut to a forwarder for `render_cache.py` (S12), and `interactive/glossary.py` to the `GLOSSARY` and `CASED` that `page.py` (S7) reads.

   **Decisions** (`ask:449-phase4-slices`, `ask:449-T81-slices`, `ask:449-T135-generator`, `ask:449-T148-claims`, `ask:449-usage-text`, `ask:449-T066-json-message`, FR-001, FR-002, FR-003, FR-004, FR-008; T148's note from T144's plan review):
   - The callers: `make record` runs `l7r-gate record site`, `make record CHECK=1` `record check record`, `make glossary` `record glossary [--split]`, `make glossary CHECK=1` `record check glossary`, `make footnote-census` and `make source-tags-contract` their `record` verbs; the push's record and glossary rows run in process where they ran `memo_check.py`, still writing its usage-log row; render-sync's staleness reaches `record site-stale` through the forwarder; the four retired rows leave `_invocation.py`'s operations, and the make-only suite's cases on them move to a recipe still wrapped.
   - `memo_check`'s general form (`<name> --inputs ... [--code ...] [--facts ...] -- <cmd>`) ported beside its two presets, its output, exit, kept pass, memo file's path and shape and usage-log row the Python's, a `python3 -m` command run as the Python ran it in its own process; its key is this program's id with the `--code` files and the project modules they import, where the Python's hashed its interpreter and modules, so a pass the Python kept is missed once after the cut. Its usage line is HEAD's with only the tool's name the port's (`ask:449-T135-generator`).
   - The record check's key is the Python's, no date in it: after the plan review, which held that FR-002's fix exception covers a check that refuses correct work and not one made to refuse more, the date the port first added is out, so a kept pass can outlive an archive row's seven-day pending window as it could in the Python; that behavior is the Python's, and its fix is its own commit after this cut (T163, constitution XIV).
   - The note's two parts: no handler of the slice's Python printed a `KeyError`'s `str(e)` (its one reader, `store.py`, used `e.args[0]`, which `store.rs` matches), and an uncaught exception's line adds Python's repr quotes where a message lacks them, pinned by a test; and live fetch URLs reach the host reading - the blocked-fetch guard, the page, archive and uncited fetches, the ledgers - so the guard's `shared::url_host` ports `urlsplit` exactly (the scheme's case, the leading controls, tab, CR and LF dropped, the bracket and IP checks, the NFKC check, the fallback), matching CPython 3.14.4 on 3,844 URLs, the expected file regenerated from HEAD's own `blocked.host` and the same (observed 2026-11-16, method: `rust/guard/src/shared/url_host/cpython.jsonl` against the port). The guard's cold build went from 23.4 s to 27.0 s with `unicode-normalization` pinned, under the wrapper's limit (observed 2026-11-16, method: one cold build each, before and after).
   - The claims (`ask:449-T148-claims`): `site_pages.py::frame`, a claim of no research on process plumbing whose code moves into a gate crate the claims walk prunes, leaves `dev/claims-index.json`, and the two deleted units leave `dev/claims-deferred.json`; no other claim names either unit and `make claims-owed` owes none after the drop (observed 2026-11-16, method: `grep` of both files and `make claims-owed`).
   - S1's library made faster with no output changed: `linkify`'s markup scan written by hand, the write-up patterns compiled once, an index on `Catalog`; the byte-equal site is the evidence.
   - The same outputs (FR-002), through the shared runner: HEAD's Python against the Rust, the whole real site (4,316 pages, `all.html`, `nav.js`, the assets, the glossary script) byte for byte, 16 fault fixtures on the real record, every glossary, census, contract and check command, flag and refusal including the general form's, the push's two rows over five real record deltas, and render-sync's rebuilt, fresh and rebuilt cycle: the differential's 71 cases, one differing, render-sync's `research/site/.stamp` (measured 2026-11-16 (`make diff-run CASES=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t148/cases.json VERIFY=1`, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t148/cases.diff-run/reports/diff-run-verify-20261117T021539Z.json`)). The stamp hashed the Python modules the build imported, which this cut deletes, so it hashes the building binary, the key Q8 rules for the generator's cache; every page and the rebuilt and fresh verdicts are the same. Normalizations taken: UTC times and the runner's world path (two Python runs differ in them), argparse's and a traceback's text (`ask:449-usage-text`), and the tool's own name in the usage line (`ask:449-T135-generator`). The push's two rows append their usage lines in either order, seen once in an incremental run and not in the verify run: the push runs every row on its own thread at HEAD as it does here (`push.rs`'s `thread::scope`), so the order was HEAD's race too.
   - Timing, recorded and not held: the record check fresh 2.2 s in Rust against 5.0 s in Python, kept 0.06 s against 0.2 s (observed 2026-11-16, method: `/usr/bin/time` of each after the last edit).
   - The census: no `specs/*/measurements*.json` command runs a deleted tool, the three naming `make record` or `make glossary` running targets that stay (observed 2026-11-16, method: `git grep` of each name in command, import, `-m` and path forms). The checks: `make static` clean on 30 crates, `make rust-test` clean, `make hooks-test HOOKS_ALL=1` green on 54 suites, `make quick` clean, the pointer check clean on a clone with the new files added (observed 2026-11-16, method: those commands).

### T148 Approach (checklist part A)

1. **The goal, in the world.** The record site builds and checks in Rust, byte for byte the Python's site, S1's library wired.
2. **The constraints.** FR-001 to FR-004 and FR-008, `ask:449-phase4-slices`, the task's note.
3. **Where each comes from.** R: the rulings; O: the differential, the host's CPython table and the census above.
4. **Do they describe the world here?** Run on copies of this clone's real record, measured 2026-11-16 (`/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t148/cases.json`).
5. **The order.** After S4 (T138).
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and a gated `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The verify run's cases with the stamp the one difference, and the census.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No.


<!-- plan-archive: T149 to T149 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->
### T150 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T150 Approach (checklist part A)

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


### T151 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T151 Approach (checklist part A)

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


### T152 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T152 Approach (checklist part A)

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


### T153 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T153 Approach (checklist part A)

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


### T154 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T154 Approach (checklist part A)

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


### T155 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T155 Approach (checklist part A)

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


### T156 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T156 Approach (checklist part A)

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


### T157 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T157 Approach (checklist part A)

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


### T158 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T158 Approach (checklist part A)

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


<!-- plan-archive: T159 to T159 moved to plan-done.md, 2026-11-16 (feature 375 FR-044) -->
<!-- plan-archive: T160 to T160 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->
### T161 (the GM's second approved proposal, the differentials rerunning only what a fix touched, enforced by tooling; request.md 2026-11-16, the GM 2026-11-11)

- **Approach**: one shared differential runner in the repository, `l7r-gate diff-run <cases file>` (a new gate crate, Rust as all new tooling is under FR-001), which every port task's comparison uses from T147 on in place of a hand-written driver loop: it runs each case on both sides, compares, records, and after a fix reruns only the cases whose key moved.

   **Decisions** (the GM's words in request.md, 2026-11-16 and 2026-11-11; FR-002, whose proof the runner carries; `ask:449-T159-rounds`, which filed it):
   - Why: the differential is the part of a port task's time a script can cut. T145's agent waited on its harness 53.8 min in the background and 10.1 min in the foreground of a 232 min run, and T143's 20.9 min and 9.2 min of a 100 min run (observed 2026-11-16, method: each tool call's and background run's wait in the agents' transcripts, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/agent_time.py`); each of those runs reran every case after each fix, the hand-written drivers keeping no record of what a case had already shown.
   - The shape is the one the hand-written harnesses of T143 to T146 share, so a port's harness moves onto it without losing a case: a world built per side (a setup command run into a fresh directory), the two sides as command templates over that world, each case's steps, the outputs compared (exit, stdout, stderr, every file the case wrote under the world, named extra files such as a server's log), named normalizations (a regex and its replacement, each listed in the report as taken), and one results row a case.
   - Each side of a case is kept on its own key, so a fix to the port reruns what it could change and nothing else: the old side's key is the hash of the case's definition, its normalizations, the content of the inputs it declares and the old side's fingerprint (the files it runs from, the Python tree at its revision), so a fix to the port never moves it and the old side's recorded result stands across every rerun of a task; the new side's key is the same with, in place of the whole binary, the content of the source paths the case declares it exercises (a crate's directory, say), so a fix reruns the new side of the cases whose declared sources it touched. A case that declares no sources keys its new side on the whole new-side fingerprint, as a rebuild then reruns it. Because a declaration can be too narrow, the figures a plan reports come from `--verify`, one run of every case's new side at the end against the kept old sides, which the report names as a verify run; `--only <name>` reruns one case.
   - Noise is the runner's too: `--twice` runs the old side twice and reports what differs between the two runs, the evidence that a normalization covers run-to-run noise and nothing more (T146's harness did this by hand).
   - Enforced by tooling, as the GM's 2026-11-11 words ask: the runner makes the incremental rerun its default; `--all`, which reruns every side of every case, takes a `REASON=` of two words or more and records it in the report and the guard log, as the gate's escapes do (FR-011); and `make decide`'s lint refuses a sentence stating a differential's case count (`cases` beside `differential` or FR-002's `same outputs`) that cites no runner verify report - the path `--verify` writes, which carries `diff-run-verify` in its name, a report of an incremental run not counting - in any feature's plan, so a port whose comparison ran through a hand-written loop cannot reach its review with that figure.
   - Out of scope: what a world needs beyond a setup command (a network namespace, a loopback server, a bare remote) stays the harness's setup script, which the runner runs and keys.

### T161 Approach (checklist part A)

1. **The goal, in the world.** A port's differential reruns after a fix only the cases the fix could change, through one runner every port uses.
2. **The constraints.** The GM's words (request.md, 2026-11-16 and 2026-11-11); FR-002, whose comparison it carries; FR-001 and FR-004 (new tooling in Rust, full line coverage).
3. **Where each comes from.** G: the GM's approval and his enforcement rule; O: the transcript split above; R: the four hand-written harnesses whose shape it takes.
4. **Do they describe the world here?** The shape read from T143's to T146's harnesses, measured 2026-11-16 (`/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/agent_time.py`).
5. **The order.** After T159; before T147, whose differential is its first user.
6. **The exits.** Green: the crate's tests and coverage - among them a case whose input moved rerun and one whose did not kept, a change to one declared source rerunning only the new side of the cases declaring it with every old side kept, `--verify` rerunning every new side, `--all` refused without a reason, and the lint refusing a differential count with no runner report - and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The crate's tests, and T147's runner reports counting, after each fix, the sides it reran and the sides it kept, its figures from a verify run.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No - it saves an agent's waiting on reruns, not the tools' running time.


### T162 (a guard defect T147's port agent met: its own clone refused by the session that launched it)

- **Approach**: the clone-sync guard (`rust/guard/src/guards/clone_sync_hooks.rs`) lets a session through the clone its dispatcher claims; the dispatcher was only `L7R_DISPATCHER`, which a page session's runner sets. A background job Claude Code starts from an interactive session runs as `--fork-session --resume <the parent's transcript>`, the parent stays live and claims the same clone, and nothing named it, so the job's first write was refused as a second live session in the tree. With no `L7R_DISPATCHER`, the guard now reads the session's own process arguments (the sessions json's pid, its `/proc` command line) and takes the session it was forked from as its dispatcher.

   **Decisions** (constitution XIV, a defect fixed where it was found; FR-001's guards ported in phase 1, whose behavior this extends):
   - Found where: T147's agent was refused on its first write into this session's clone, `already occupied by another live session` naming this session's own parent, and wrote through a copy from scratch instead; this session's process runs as `--fork-session --resume <the parent's transcript>`, and the parent's process is live (observed 2026-11-16, method: the sessions json and `/proc` of both processes).
   - Only a fork counts: a session resumed without `--fork-session` is the same conversation continued, not a launched job, and it stays refused beside a live claimant; the resumed argument's leaf, less `.jsonl`, is the parent's id.
   - The exemption is the one a page session already has (the dispatcher's claim alone is let through); every other live claimant still refuses.
   - The checks: the guard's tests green with a test holding a forked session through and an unforked one refused, the test failing with the fix taken out, and the guard's line coverage complete (observed 2026-11-16, method: `make rust-test CRATE=rust/guard`, run with and without the fix, and `l7r-gate.sh rust uncovered --crate rust/guard`).

### T162 Approach (checklist part A)

1. **The goal, in the world.** A background job writes in its launcher's clone without a workaround, and two unrelated live sessions still never share one.
2. **The constraints.** Constitution XIV; the guard's existing claim rule and its dispatcher exemption.
3. **Where each comes from.** O: the refusal T147's agent met and the two processes' arguments.
4. **Do they describe the world here?** Read from this session's own processes, measured 2026-11-16 (`/proc/<pid>/cmdline` of both).
5. **The order.** After T147, which found it; before the next port's agent writes.
6. **The exits.** Green: the guard's tests and coverage, and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The guard's tests, and the next port agent's first write in this clone let through.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No.


<!-- plan-archive: T163 to T148 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->

<!-- plan-archive: T164 to T149 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->
<!-- plan-archive: T164 to T164 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->

<!-- plan-archive: T165 to T165 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->
<!-- plan-archive: T166 to T165 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->
<!-- plan-archive: T166 to T166 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->

### T167 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T167 Approach (checklist part A)

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

