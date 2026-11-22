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
### T122 (the full hook run's wall time, the GM's pre-approval of 2026-11-12: a concrete target with a measured saving)

- **Approach**: the full hook run (`make hooks-test HOOKS_ALL=1`) cut by its three bounds together: the idle-tests suite's real-time waits in fractions of a second (the guard's fixture seams `IDLE_WAIT_S` and `IDLE_DEFER_S`, `rust/guard/src/guards/idle_tests_hooks.rs`, honored inside a fixture alone, and `tests/hooks/test-idle-tests-hooks.sh`), the entry-gate suite's fixture answering its units a check at a time (`tests/hooks/test-entry-gate.sh`), and the Makefile's missing-program self-test started beside the suites instead of after them.

   **Decisions** (the GM's pre-approval in `request.md`, "a fifth efficiency round"; FR-002 for every suite case; docs/performance-checklist.md):
   - Why it did not land on 2026-11-12: the idle-tests change alone cut that suite from 35.0 s to about 17 s (observed 2026-11-12, method: T122's first runs, its note in tasks.md), but the full run did not move, because the next suites bounded it - entry-gate, its fixture answering eleven units with one call each where each `record-owed` call rebuilds the tree's owed units - and about 8 s ran outside any suite, the self-test serial after them (observed 2026-11-17, method: the run's own step times, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/runs.txt`). Back-to-back runs on this host also drive the CPU to 94 °C and slow the CPU-bound suites about 1.5 times, which hid the gain (observed 2026-11-17, method: the package temperature and the load logged beside each run, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/runs.txt`).
   - The changes, every case and check kept: entry-gate's fixture answers notes a question at a time, other subjects by kind and the three modal units as one modal-research answer, as a session records them - three calls in place of eleven, the same units answered, its case 4 still proving the gate falls quiet; the self-test's pass, failure and stamp are read after the suites as before, a plain `make hooks-test` still skipping it when unchanged.
   - Before and after, each run started cool: the full run took 43.0, 43.3 and 43.4 s before and 29.4, 28.8 and 29.0 s after (observed 2026-11-17, method: `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/runs.txt`, each run started under 60 °C and a one-minute load under 3, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/full.sh`). Alone, idle-tests went from 34.8 to 17.0 s and entry-gate from 22.8 to 13.5 s (observed 2026-11-17, method: `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/runs.txt`, each run started under 60 °C and a one-minute load under 3, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/full.sh`). Back to back on a hot CPU the run took about 62 s before and 53 to 55 s after (observed 2026-11-17, method: `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/runs.txt`, runs started without waiting to cool), the figure a gate after builds sees.
   - The next bound, recorded and not cut: sync-with-main, with entry-gate and l7r-gate within 4 s of it (observed 2026-11-17, method: the after runs' suite times, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/runs.txt`), so a further cut needs all three; its candidates are sync-with-main's system time, `record-owed`'s fixed cost a call, l7r-gate's real browser and model starts, and `deps --keys` serial before the suites.
   - The checks: `make static` green, `make rust-test` green, `make hooks-test HOOKS_ALL=1` green on 54 suites (observed 2026-11-17, method: those commands, one after another after the last edit).

### T122 Approach (checklist part A)

1. **The goal, in the world.** The full hook run waits only as long as its cases need.
2. **The constraints.** FR-002: every case and check held; the GM's condition, a measured saving.
3. **Where each comes from.** G: the GM's pre-approval; O: the runs T122 recorded (its record removed on landing, in git history).
4. **Do they describe the world here?** Measured on this host cool and hot, measured 2026-11-17 (`/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t122/runs.txt`).
5. **The order.** After T160, which found the run's bound.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The full run a third faster from a cool start.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** Yes, of the hook suites: (1) the time went to idle-tests' real waits, entry-gate's eleven `record-owed` calls and the serial self-test, measured per suite; (2) each change removes work or waiting; (3) the expected saving was the bound's, about a third; (4) the run is bounded by its longest suite, so the next cut needs the three now level; (5) before and after started cool, and hot, the temperature and load stated; (6) no map moved.

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
<!-- plan-archive: T150 to T150 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T151 to T151 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T152 to T208 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T152 to T152 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T156 to T156 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T218 to T157 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T158 (Phase 4 S13, the deletion close: `ask:449-phase4-slices` S13 and Q10, and the Python T222 left with no importer, found 2026-11-19)

- **Approach**: the repository holds no `.py` outside `specs/` except `scripts/gates/codeid.py`, and no Rust starts a Python script except the seven `content_ids` callers that run it by path (seven, measured 2026-11-22 (the reader search below)), under `ask:449-T062-py-id`'s terms (one process a run, never on a plain Bash call or a plain Edit), both until T247 (`ask:449-T158-codeid`): every other tracked `.py` file is deleted, with the Rust that started the claims tools' Python, ruff, `pyproject.toml` and the lockfiles; each file deleted only after a measured search for its readers, and the claims on the deleted units carried by the claims tool. Each figure below is measured 2026-11-22 (method named beside it).

   **Decisions**:
   - **The readers, file by file** (measured 2026-11-22: a scan of every tracked file outside `specs/`, `research/`, `dev/run-log/`, `dev/bypass-log/` and the pools, for each file's path, its repository-relative path, its dotted module and an `import` of its stem - `/tmp/t158/readers.py` - then each hit read; `git grep` of the Rust crates for `include_str!`, `read_to_string`, `Command::new("python3")` and the paths; the hooks and `tests/hooks/`; and a `grep -r` of `/host-l7r-repo/gm-assistant` for `l7r.diagram`, `l7r/diagram`, the script names, `knobs.json` and `work_counts`, which found only comments about the old namespace package). A reader is code that imports, runs or reads the file; a comment citing it as history is not:
     - `l7r/diagram/interactive/**/*.py` (39 files, 3,525 lines, measured 2026-11-22 (the reader search above)): 2 readers - the claims tool's `.py` units (its 43 claims, below) and `rust/gate/crates/registry/src/kinds/tests.rs`, the lockstep test holding the Rust table equal to the Python classes; a lockstep test retires with its Python (`specs/449-rust-codebase/engine-plan.md`), so it went and the table's counts and modal-file test stay. Deleted. The directory itself is NOT deleted: its `assets/` (glossary, modals, choices, siblings: about 3,000 files, measured 2026-11-22 (git ls-files)) is read by the gate's crates, and its two `CLAUDE.md` files are repointed to the Rust.
     - `l7r/diagram/work_counts.py` (38 lines, measured 2026-11-22 (the reader search above)): 0 readers (comments in `rust/mode_a/src/work_counts.rs` and `docs/work-budget-rubric.md` only). Deleted.
     - `l7r/diagram/knobs.json`: 3 readers - `rust/gate/crates/registry/src/conditions.rs` (`KNOBS_FILE`, `knob_table`, `knobs`), `rust/gate/crates/bundle/src/record/bundle/depiction.rs` (the depiction bundle's knobs note) and `rust/phases/src/driver.rs`'s field-stage knob order. KEPT: the task line's "no reader found" did not hold at this tree.
     - `l7r/diagram/__init__.py` (27 lines, measured 2026-11-22 (the reader search above)): 0 readers (`task/src/plan_hold.rs` walks for any `__init__.py` and works with none). Deleted. `l7r/diagram/tools/__init__.py` (8): 0 readers. Deleted.
     - `l7r/diagram/tools/claims.py` (689), `scripts/bundle_door.py` (121), `scripts/record/claims_context.py` (208), `claims_counters.py` (170), `claims_scope.py` (165), `claims_stale.py` (81), `scripts/record/tunables.py` (115): 1 reader, the Rust claims crate, through `core`'s `record::bundle::door::Runner` (`python3 scripts/bundle_door.py`, eleven verbs) - and `seam.rs` asked `claims_read_units` on every `make land` scope split whatever the seam held, so deleting the Python alone would have broken the landing. The Rust's `.py` half went first (below), leaving 0 readers; then deleted.
     - `scripts/gates/codeid.py` (442, `split_ids` with it): 7 readers, each running it for a `.py` file's docstring-blind id or a pair's comparison - `core/src/codeid.rs` (`content_ids`), `tree/src/delta.rs`, `stamp.rs` and `exempt.rs`, `cohort/src/cohort.rs`'s counter-only pairs, `measure/src/preflight.rs`, `task/src/wording.rs`'s `same_pairs` - and `plan/src/plan/engine_edit/tests.rs` and `claims/carry/tests.rs` pin the docstring-blind id. KEPT under the round arbiter's `continue` ruling `ask:449-T158-codeid` (T158 lands with the file kept; the file and its seven Rust callers go together in T247): moving `content_ids` to a blob id was measured 2026-11-22 (`make rust-test` on each crate) to fail two `plan` tests, one `task` test and one `claims` test, and the plan and task crates are 451 T141's builder's, mid-edit at this tree; so the file and every caller go together in T247, filed for after 451 T141 lands, and this task's edit of those callers was undone.
     - `scripts/measure/dead_closure.py` (356 lines, measured 2026-11-22 (the reader search above)): 1 reader, `make dead-closure`, which nothing calls (0 callers in the Makefile, scripts, hooks or crates); the script read `l7r/`, `pool/` and the legacy pool's Python, none left. Deleted with its target. Its rule on Rust code is held by the compiler's `dead_code` lint, refused in `make static`'s `rust lint`, and for a `pub` item nothing calls by `l7r-gate rust dead` (`rust/gate/crates/rustc/src/rustc.rs`'s `dead_public`, tested in `rustc/tests.rs`), the row `dev/rust-tooling.md` carries.
     - `pyproject.toml` (62), `requirements.txt` (13), `requirements-dev.txt` (42), `requirements.in` (4), `requirements-dev.in` (14): readers `scripts/container/setup-dev-env.sh` (the pip install and its two checks, removed), `make quick` and `make static`'s `ruff check` (removed), `checks/documents/docs_mechanism.rs` (reads `pyproject.toml` for a `fail_under` key; an absent file reads as empty, so it holds), `land/src/replay_owing.rs` (copies the file from an OLD commit for the old side; unaffected) and `scripts/land-tooling.sh`'s lint (only on a `.py` file named, so dormant). Deleted. shapely and scipy went with `requirements.txt`: 0 importers (no `.py` is left). The premise the arbiter set (`ask:449-T158-codeid` item 3), measured 2026-11-22 (`grep -n '^import\|^from'` of `scripts/gates/codeid.py`, and `git show HEAD:` of each of the five files grepped for `coverage`): the kept `codeid.py` imports only the standard library at its top (`ast`, `copy`, `hashlib`, `json`, `os`, `pathlib`, `re`, `subprocess`, `sys`), and its one other import, `coverage` inside `--missing` (run by `tree/src/exempt.rs`, a T247 caller), was pinned by none of the five (0 hits each), so deleting them takes nothing it needs; `claims_wait.rs`'s `ruffed` is rechecked in T247, where the last `.py` goes.
     - `l7r-gate cohort fresh-seed`: 0 callers, measured 2026-11-22 (the reader search above), (its one, the make probe, deleted by T230): the verb, `Repo::fresh_seed`, `FRESH_BASE`/`FRESH_SPAN` and their tests deleted.
     - the make-only guard's `ENTRY_SCRIPT` pattern for the deleted `hamletgen/__main__.py`: deleted with its two cases, measured 2026-11-22 (the reader search above) (`make_only_hooks/tests.rs`, `tests/hooks/test-make-only-hooks.sh`).
     - `l7r/diagram/CLAUDE.md`'s `switches.py` row: deleted (no such file).
   - **The claims** (`ask:449-phase4-slices` Q10, `ask:449-T148-claims`): 43 claims sat on `interactive/` units (`choices.py` 10, `classes/_base.py` 18, `conditions.py` 14, `sources.py` 1), every one `NONE` research (plumbing), their code ported by T149 and T144 into the `registry` and `research` gate crates, which the claims walk prunes. `dev/claims-ports.json` maps each unit to its Rust item (`by: 449 T158`), and `make claims-rekey` dropped all 43 as `ask:449-T148-claims` rules for a NONE claim ported into a tooling crate: measured 2026-11-22 (`make claims-rekey`: "0 carried ... 43 dropped"; `dev/claims-index.json` 3,323 rows to 3,280, 0 rows on a `.py` unit, measured 2026-11-22 (a `json` count)). No claim citing research was on a deleted unit, so no new ask.
   - **The Rust's `.py` half** removed with the Python: the claims crate's door and every `.py` branch (`scope.rs` and its `Reader`, `bundle.rs`'s `py_context`, `counters.rs`, `seam.rs` - the land's scope split now owns a finding in a changed `rust/` file and leaves any other, measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/claims`, 156 passed, its `a_landing_answers_for_its_own_findings` holding a changed `rust/` file's DRIFTED as the landing's own and a changed doc's MISLABELED left), `stale.rs`, `triage.rs`, `tunables.rs`, `ports.rs`'s merge-base texts) and `core`'s `record::bundle::door`. The messages that named the deleted Python packages now name where the kinds live (`owed`'s `MODAL_DIRS`: the two `assets/modals/` directories; `bundle`'s check-bundle refusal: the registry's `kinds.rs`), and `Registry::package`, read only by the deleted lockstep test, is gone.
   - **The push's refusal of an unported `.py` claim** (`carry::unported`, T166) can no longer fire: it read the merge base's `.py` units through the deleted Python, and no `.py` unit is left to claim on. Measured before the cut 2026-11-22 (the merge base's `dev/claims-index.json` read with `json`): its 43 `.py::` rows are each mapped under `ports`, none unmatched, so this landing loses no claim the refusal would have held.
   - **The search's one exclusion, `specs/`**, searched apart, measured 2026-11-22 (grep of the 55 `specs/*/measurements*.json` for every deleted name, `ruff`, shapely and scipy): three hits, all records of past runs and none a command `make figures` re-runs against a deleted file - feature 261's `grep` of `greenery.py` at the pre-329 skill path (dead since 329), feature 444's one-off shapely run and feature 449's cProfile note.
   - **Left, and why**: three ruff callers fire only on a `.py` path that is not a deleted file, and the only tracked `.py` files left are `codeid.py` and the frozen `specs/` scripts, which none of the three is handed, so they are dormant, not wrong: `land/src/land/claims_wait.rs`'s `ruffed` (the land crate is 451 T94's and T141's builders'), `scripts/land-tooling.sh`'s lint and `make_only_hooks.rs`'s landing lint (both already silent without ruff), and `ruffed` returns None where ruff fails (its own doc), so a missing ruff leaves a gate-formatted file uncommitted, never a wrong commit. The land crate's `cheap.rs` `stage_seam` and `walk_py` walk `l7r/` for a `.py` `def stage_*` and now always find none, measured 2026-11-22 (`find l7r -name '*.py'` in the working tree: 0): dead, not wrong, in the land crate 451 T94's and T141's builders hold, so named for T247. The constitution's ruff, `pyproject.toml` and `make dead-closure` text is a constitution amendment, not this task's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the deletions and the Rust's `.py` half | the crates' tests (`make rust-test` on each crate touched) | no engine output changes: no generator read any deleted file | none | - |

### T158 Approach (checklist part A)

1. **The goal, in the world.** The repository holds no `.py` outside `specs/` except `scripts/gates/codeid.py`, and no Rust starts a Python script except the seven `content_ids` callers that run it by path (seven, measured 2026-11-22 (the reader search above)), under `ask:449-T062-py-id`'s terms (one process a run, never on a plain Bash call or a plain Edit), both until T247 (`ask:449-T158-codeid`): no lockfile to install, no ruff, and no Rust that starts the claims tools' Python.
2. **The constraints.** FR-001 and FR-001b (Rust only; the Python and its tooling deleted), `ask:449-phase4-slices` S13 and Q10 (claims re-keyed by the tool at the cut), `ask:449-T148-claims` (a NONE claim ported into a tooling crate is dropped), the lockstep rule as T180 restated it (a lockstep test retires with its Python).
3. **Where each comes from.** G: the GM 2026-11-10 ("Yes delete everything except that group, please."); R: the arbiter rulings above; O: the reader search and the claims counts above.
4. **Do they describe the world here?** Measured 2026-11-22 by the reader search (method above): `knobs.json` was found read and kept, the rest found unread once the Rust's `.py` half went.
5. **The order.** After T222 and T230; the claims re-keyed after the `l7r/` Python was deleted and before the claims Python was (the rekey ran with the door still present); the claims and code-id Rust before their Python. T235, T240, T241, T243 and T246 read "lands before T158" and are open at this tree: the landing waits on them, which the session orders.
6. **The exits.** Green: the crates' tests, `make quick`, `make hooks-test` and `make closing-checks T=T158 F=449`; `make claims-report` with no claim on a deleted unit. The exits asserting no `.py` at all and no Rust starting Python are T247's, the deletion close for those two (`ask:449-T158-codeid`). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `git ls-files '*.py'` lists only `specs/` files and `scripts/gates/codeid.py` (kept until T247, `ask:449-T158-codeid`), and `git grep` of `rust/`, `scripts/`, `tests/hooks/` and the Makefile finds no path that runs or reads a deleted file, and no Rust that starts Python but the seven `content_ids` callers of `codeid.py` (seven, measured 2026-11-22 (the reader search above)).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

**Performance work?** No - a deletion; it removes the claims tools' Python start.


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

### T167 (FR-008's remaining debt after T160, and the ruling on the tests that read the live tree)

- **Approach**: the tests still over FR-008's tenth of a second brought under it by the methods T164 and T160 used - shared fixtures built once, fewer git and process calls, a test that does two things split with its name kept on the first part, an injected clock or a poll in place of a sleep - every assertion kept; each tool's one test that reads the live tree declared its end-to-end test by name, as the round arbiter ruled.

   **Decisions** (FR-008; `ask:449-T167-realtree`; the GM's performance rule, docs/performance-checklist.md; constitution XIV):
   - The ruling: a test of a tool's real behavior over the whole repository is that tool's one end-to-end test (the spec's edge case and Story 3), a tool being the check or verb, not the crate. Declared, each doc comment opening with the one marker `FR-008's one end-to-end test (ask:449-T167-realtree):`: tree's stamp self-test, task's research boxes, and checks' research pointers, tooling detector and question size, the ruling's five; checks' file-scale test, which reads the live tree as they do; land's `replay_owing` test, which drives the real `python3` that tool runs, its other tests under the bar; and the markers browser, rustc, research's fetch and ci already carried, made the same words. Eleven in all, one a tool (observed 2026-11-17, method: `grep` of the marker over `rust/`): `rust/browser/src/crop/tests.rs`, `rustc/tests.rs`, `research/src/verbatim/fetch/tests.rs`, `ci/features/tests.rs`, `land/src/replay_owing/tests.rs`, `tree/src/stamp/tests.rs`, `task/src/research_boxes.rs`, and `checks/src/checks/` `research_pointers`, `rust_tooling`, `question_size` and `file_scale`.
   - The guard's `the_r6_corpus_replayed` is an ordinary test, not an end-to-end one: it replays a recorded corpus, not the live tree, and other guard tests drive real `bash` too. Its 239 commands now replay eight at a time through real `bash`, 389 to 66 ms (observed 2026-11-17, method: each test alone, best of three, a fresh TMPDIR, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t167/ws-final.rows`).
   - The count: of 2,400 tests 152 ran over the bar before (observed 2026-11-17, method: each test alone, best of three, a fresh TMPDIR, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t167/ws-final.rows`). Of 2,579 after the splits, the workspace pass left three ordinary tests at 100 ms or more - two claims tests and author's `claim::each_refusal_writes_nothing` (observed 2026-11-17, method: each test alone, best of three, a fresh TMPDIR, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t167/ws-final.rows`). The two claims tests were then brought under it, every claims test under the bar, the highest 94 ms (observed 2026-11-17, method: the same, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t167/claims-final.rows`). Author's `each_refusal_writes_nothing`, which this task did not touch, sits at the line, 99 ms in one pass and 102 ms in the next, load noise (observed 2026-11-17, method: the same, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t167/ws-after.rows` and `ws-final.rows`). The 23 `checks::documents` tests and two rustc tests record no time in the pass: the harness ran them without `CARGO_MANIFEST_DIR`, which they read, and timed with it set the 23 took 2 to 23 ms (observed 2026-11-17, method: the same with the variable set, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t167/ws-final.rows.fail`); none was among the slow tests before. The declared tests run up to 724 ms (observed 2026-11-17, method: each test alone, best of three, a fresh TMPDIR, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t167/ws-final.rows`).
   - The claims tests whose setup ran the bundle and record commands through the Python runner write what those commands leave, and three new tests run the real commands on each fixture and assert the same files, so a change in the recording fails them rather than leaving the others on stale state.
   - Where an assertion stayed but its subject moved, the test still asserts the production value apart: recycling tested every third page with the 25 asserted separately, a test build's shorter timeouts (bundle's slow page, diffrun's one-second wait, browser's crop on the fake Chromium), stand-ins for real programs with one real run kept in each crate.
   - Production changes for speed, each output the same: the checks runner asks the git directory once a run and lists modified and new files in one call, `make claims-carry` reads its target once, the guard's sweep start reports whether it launched in place of a sleep (`0.3 s`, the test's old wait), the landing fetches once.
   - A race fixed (constitution XIV): the scratch-sweep tests failed about once in 50 runs six at a time, a forked child briefly holding a test's open files; they now wait until `/proc` shows no other holder, none failing in 1,920 runs (observed 2026-11-17, method: the two tests six copies at once, the host's load up to 54).
   - Not built: a check refusing a new test over the bar, which the GM's performance rule in `docs/performance-checklist.md` rules out: time is the goal of a performance change and never a gate.
   - The checks: `make static` clean on 31 crates, `make rust-test` clean, `make hooks-test HOOKS_ALL=1` green on 54 suites (observed 2026-11-17, method: those commands, one after another after the last edit).

### T167 Approach (checklist part A)

1. **The goal, in the world.** Every test but a tool's one end-to-end test runs under a tenth of a second.
2. **The constraints.** FR-008; `ask:449-T167-realtree`; the performance rule.
3. **Where each comes from.** R: the ruling; O: the workspace measured before and after.
4. **Do they describe the world here?** Measured over the whole workspace, measured 2026-11-17 (`/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t167/ws-final.rows`).
5. **The order.** After T160.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1` and `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The workspace re-measured with no ordinary test over the bar.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** Yes, of the tests: (1) the time went to setup - git and process calls, real programs, sleeps - measured per test; (2) each change removes work or waits on a condition in place of a clock; (3) the saving is every ordinary test under the bar; (4) the declared tests grow with the repository, held by SC-003's suite total; (5) before and after by T99's method with the load stated; (6) no map moved.


<!-- plan-archive: T168 to T168 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->

<!-- plan-archive: T169 to T169 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->

<!-- plan-archive: T170 to T170 moved to plan-done.md, 2026-11-17 (feature 375 FR-044) -->
<!-- plan-archive: T171 to T171 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
### T175 (the engine's piece 4, the audit's rest, step 1's close; the GM 2026-11-17, request.md: "proceed with the next 2 engine pieces and then we'll measure how well those went")

- **Approach**: the rest of `l7r/diagram/tools/pack_audit/` - onmap, labels, marks_drawn, sun, palette, program_rules, roads, mapmatch, shared, checks, registry and report - ported into `rust/mode_a/src/audit/`, with what they read of the engine (`compound.rs`: `compound_model`'s three distances and `KINDS`, `compound_parts`' three predicates), and `make pack-audit` wired to it (`l7r-gate.sh mode-a pack-audit`); `__main__.py` deleted with its `_invocation.py` row. Every other `pack_audit` module stays for compound.py and tests/test_mode_a_sheets.py under the lockstep rule. Worked by two agents in turn: part A the libraries, part B the wiring and the differential.

   **Decisions** (`ask:449-engine-order` conditions 2, 3 and 5, `ask:449-phase4-slices` Q10, `ask:449-usage-text`, FR-001 to FR-005, FR-008; the GM's words, request.md 2026-11-17):
   - The piece closes step 1 (engine-plan.md step 1's row: the audit held to its verdicts on today's Python-drawn sheets exactly, wired at once). Lockstep (condition 3): the crate's one end-to-end test runs every check's records, all 43 checks' findings and refusals, the whole report and `report.main` in one Python interpreter against the Rust, floats bit for bit, on the six pool sheets, 44 red fixtures, 46 check fixtures and 25 parse fixtures, each check firing on its red fixture and each pool sheet passing its tier's checks; a scratch mutation of a module of each group turned it red (observed 2026-11-18, method: each mutated in a scratch copy restored by `cp`, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/a/mutate/results.txt` and, for `sun.py`, whose first mutation changed nothing, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/a/mutate/results-sun.txt`).
   - Geometry (engine-plan.md: a check's verdict is bound exactly): `sun.py`'s shapely calls are reproduced exactly where they are hulls of convex casters, box overlaps and GEOS's 64-point circle, and only the bed's unshaded area goes through the `geo` crate's union and difference (pinned `=0.32.0`, with `i_overlay` `=4.0.7`). Its largest difference from GEOS over every red fixture's half-hour steps is 1.99e-4 px2 against a nearest margin to a threshold of 25.3 px2, so no verdict can turn on it, and the test asserts the difference stays under the margin (observed 2026-11-18, method: both computed on 882 half-hour steps, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/a/phases.log` line 14; the landed test measures the garden's red fixture's 210 steps).
   - Claims (Q10): the claims on the kept `.py` units stay keyed to them; each Rust copy carries its claim word for word where it describes the Rust, or a claim stating what the Rust unit decides where a memo, a regex range or a figure moved; every other new unit carries its module's NONE; `py.rs`'s module claim is widened to its arithmetic, as two claims rounds asked. `make claims-owed` owes 434 new claims in 25 files one impl-drift round and 11 a triage (observed 2026-11-18, method: `make claims-owed`).
   - The same outputs (FR-002): HEAD's `make pack-audit` against the Rust on each pool sheet, all of them in one call, every fixture sheet where it lies and under its tier with its notes, 17 notes and manifest forms, 12 file refusals and the argument forms, directly and through make - the differential's 207 cases, none differing, every pool case exiting 0 with its full report on both sides (measured 2026-11-18 (`make diff-run CASES=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/b/diff/cases.json VERIFY=1 JOBS=4`, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/b/diff/cases.diff-run/reports/diff-run-verify-20261118T033436Z.json`)). Normalizations: a traceback's frames, and an uncaught `JSONDecodeError` or `UnicodeDecodeError` message compared by its class, under `ask:449-usage-text`'s clause leaving an uncaught traceback's text unbound while the exit and stdout stay bound. The usage line both sides print still names `python3 -m ...pack_audit`: it is bound output, kept as T170 kept its own.
   - The step's page (condition 5, engine-plan.md's page shown to the GM every slice): step 1 draws nothing, and every pool Mode A sheet before step 1 and now is byte-identical, 6 of 6 (observed 2026-11-18, method: each sheet at `9573334eb`, the parent of T168's first commit, the two untracked ones regenerated there, compared with the working tree; `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/b/page/step1-sheets.html`).
   - Defects of HEAD's Python reproduced, not fixed, each refusing nothing: `registry.ft` has no caller and is not ported; three branches cannot run; the On-map error quotes the line break after the bad line; the `county-*` red fixtures carry no tier. Reported to the GM.
   - The piece's measure, by phase: part A's agent took 706k tokens and 88 minutes, part B's 231k tokens and 37 minutes (observed 2026-11-18, method: their usage reports and `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/a/phases.log`, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/b/phases.log`). The end-to-end lockstep takes 7.9 s and every other test at or under 0.056 s (observed 2026-11-18, method: `make test-times CRATE=rust/mode_a`). An edit cycle's `make rust-test CRATE=rust/mode_a` took 13 to 16 s (observed 2026-11-18, method: the phase logs' cycle times). The verify runs took 511.1 s with every side rerun and 203.4 s with the old sides kept (observed 2026-11-18, method: `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/b/phases.log`).
   - The checks: `make static` and `make rust-test` fresh, `make hooks-test HOOKS_ALL=1`, `make quick` and the pointer check green (observed 2026-11-18, method: those commands, one after another after the last edit).

### T175 Approach (checklist part A)

1. **The goal, in the world.** The whole audit runs in Rust, wired, step 1 closed, and the piece's cost measured.
2. **The constraints.** FR-001 to FR-005 and FR-008; `ask:449-engine-order`; Q10; the GM's words.
3. **Where each comes from.** G: the GM's request; R: the rulings; O: the differential, the lockstep, the geometry's measure and the phase logs above.
4. **Do they describe the world here?** Run on this clone's pool sheets and fixtures, measured 2026-11-18 (`/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t175/b/diff/cases.json`).
5. **The order.** After T174; the step's last piece.
6. **The exits.** Green: `make static`, `make rust-test`, `make hooks-test HOOKS_ALL=1`, the claims round and a gated `make land` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The verify run's cases with none differing, the claims round recorded, the phase table in time and tokens.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No - a port, its cost measured for the GM.


<!-- plan-archive: T176 to T175 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T177 to T176 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T177 to T177 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
### T180 (the GM 2026-11-18, request.md: no exactness standard for a port)

- **Approach**: the living guidance amended to the GM's rule - an output may differ from what it replaces so long as everything works: its tests pass, it does its job for its callers, its research claims hold - and, as FR-002 states it, neither an exactness standard: a drawn output passes its checks and holds its research claims, and a ported check still does its job (its red fixtures still fail, what it passed still passes), a check fixed or improved on purpose changing as fixed (restated 2026-11-21 by the plan review of 449's changed blocks, `/tmp/sfr449/verdict.json`, to the GM's 2026-11-18 words: "surely you mean \"the audit checks must pass\" right?!"). The constitution (2.35.0: Principle XIII's "A differing output is not a regression", X's clause 15 widened), its plan, spec and phase templates and the speckit-specify checklist; spec.md's FR-002 (its byte-only ruled cases collapsed into the rule, the three that set a verdict or a behavior kept), its phase-4 paragraph, FR-012 and SC-007; engine-plan.md ("What the same means for any port", condition 3's lockstep restated: a test may show agreement, bytes are not required); the root and three subtree CLAUDE.md files; docs/efficiency-tooling.md, spec-kit-and-reviews.md, diff-run.md (a difference a signal, not a bar) and gm-rulings.md (the GM's words); dev/performance.md; and the review agents' files - spec-fidelity, spec-fidelity-verify, round-arbiter and escalation-check - which launch without CLAUDE.md, so each carries the rule and the GM's words: a reviewer never blocks, narrows or sends back a port for differing bytes, and a requirement demanding byte agreement is itself the finding.

   **Decisions** (the GM's words, request.md 2026-11-18 and 2026-11-17; docs/efficiency-tooling.md, 2026-10-18):
   - Kept, as not a port's exactness standard: reproducibility (the same code and seed give the same map; the cache audit; counters that must not change a map), a lossless split's integrity, a file hash naming its content, and the research rule that a quotation is verbatim; past specs and dated records, history, left as written.
   - Held, not kept exact, as the GM's "everything works" is judged by it: the audit checks pass, a ported check still does its job (its red fixtures fail, what it passed still passes), and a check fixed or improved on purpose changes as fixed (FR-002).
   - The rule is applied from here on: finished tasks' plan sections stay as the records of what they measured, and `rust/mode_a`'s lockstep tests stay until a harmless difference makes one fail, when it is changed to hold the verdicts and claims (engine-plan.md's restated condition 3).
   - The checks: `make hooks-test HOOKS_ALL=1` and the pointer check green (observed 2026-11-18, method: those commands after the last edit, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t180/hooks.log`, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t180/pointers.log`); `make static` red only on T151's port in progress (three uncalled functions in `rust/mode_a/src/labels/`, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t180/static.log`), run again green at the landing with T151's work committed. The sweep's search is `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t180/sweep-grep.txt`, its hits after the amendment `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t180/sweep-grep-after.txt`.

### T180 Approach (checklist part A)

1. **The goal, in the world.** No reviewer, guide or rule holds a port to its bytes; every one holds it to working.
2. **The constraints.** The GM's words; the constitution's own amendment rules.
3. **Where each comes from.** G: the GM's request.
4. **Do they describe the world here?** Read on this clone's living guidance, 2026-11-18 (the sweep's grep, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t180/sweep-grep.txt`).
5. **The order.** Before step 3's review, which it governs.
6. **The exits.** Green: `make static`, `make hooks-test HOOKS_ALL=1`, the plan review, a `make land`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The grep over the changed files showing only the GM's quotes, measurements and the kept reproducibility and integrity lines.
10. **Before moving a constant.** None moved.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No - guidance.


<!-- plan-archive: T181 to T181 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T182 to T176 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T182 to T182 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T183 to T150 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T183 to T183 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T184 to T151 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T184 to T184 moved to plan-done.md, 2026-11-18 (feature 375 FR-044) -->
<!-- plan-archive: T185 to T194 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T185 to T185 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T186 to T182 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T186 to T186 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T187 to T187 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
### T194 (step 3a's last reader and leader gaps, T193's leftover findings and its impl-drift's 2 DRIFTED, 1 MISLABELED and 3 outside the change; the GM 2026-11-18, request.md: "in general we should fix all known bugs in each step before moving on to porting the next step")

- **Approach**: a leader ends on the ink as SVG draws it, in `rust/mode_a/src/labels/placer.rs` (its ink geometry now `placer/ink.rs`, split at the 1,000-line bar), `hand_sheet/read.rs`, `hand_sheet/classify.rs` and `hand_sheet.rs` and the kept `l7r/diagram/labels/placer.py` and `hand_sheet.py` alike. The reader keeps a path as SVG strokes it, and a stroke's band is drawn with its joins, miter limit and dashes. Research page 0242's drawing page is split, its leader topic now research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html. Every log and probe cited below is under `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t194/`, written `t194/` here. The new Rust tests failed on HEAD's code (measured 2026-11-18 (`make rust-test CRATE=rust/mode_a` on a detached worktree of HEAD with the new and changed test files, `t194/red.log`)) and pass on the clone (measured 2026-11-18 (`make rust-test`, `t194/rust-test.log`)).

   **Decisions** (FR-002 and the lockstep rule as T180 restated it, `rust/gate/CLAUDE.md`. Constitution XIV. Research pages 0242 and 0330. The GM's words above):
   - Item 1, the path. `path_points` (both copies) returns each subpath and whether a `Z` closed it. A Bezier is flattened in the fewest equal steps Wang's bound allows, its smooth form reflecting the control point before, and an arc as SVG 1.1 appendix F.6 draws it. The sag is `DISC_SAG_PX` on the sheet (a CONVENTION, 0.05 px, T192's claim "a disc's sampled curve"), divided by the element's largest stretch. Hoshigaoka's rope ring reads as 25 points within 4e-14 px of its radius (observed 2026-11-18, method: `t194/sanity.py`, `t194/sanity.log`).
   - Item 1, beside the curves. A second move was joined to the first by a segment nobody drew (Ubame's rear-yard fence, Ochiba's steam marks), a `Z` drew no closing side (the wells of Ochiba and the two compound sheets), and a path's fill was read on the path alone (Ubame's three dry-garden rakes and Hayakawa's two chevrons, under `<g fill="none">`, read as boxes) (observed 2026-11-18, method: the reader's shapes on HEAD's archive and the clone, `t194/shapesdiff.py`, `t194/shapesdiff.log`). Each subpath is now a shape of its own, a `Z` closes its stroke with a join and no cap, and a path or polyline reads its fill as inherited. A cap, join or limit SVG does not know is ignored and the inherited one stands, as SVG does, where T193 drew an unknown cap butt.
   - Item 1, dashes, measured before choosing. One drawn pool leader ends on a dashed stroke, the sacred tree's, and on the ring as now read it ends on a dash (observed 2026-11-18, method: `t194/survey.py` on HEAD's archive, `t194/survey-head.log`, `t194/sanity.log`). With the dashes drawn no pool caption or leader moves (observed 2026-11-18, method: `t194/reach.py` with and without them, `t194/reach-dash.log`). So they are drawn, as 0242 and 0330 have a leader end at the nearest drawn point and a gap is not drawn: each dash a stroke of its own with the caps, from `stroke-dashoffset`, scaled with the element.
   - Item 2, joins. `stroke-linejoin` and `stroke-miterlimit` are read and inherited, and `join` draws SVG 1.1's corner: a miter, a bevel past the limit, a disc for round. A closed outline is measured round as before, then each corner's miter point is tried, and one that bevels sends it to its whole band (`part_nearest`, `outline_corners`). The whole band alone moved leaders between parallel edges, an equally near point chosen in another order (observed 2026-11-18, method: `t194/variant.py`, `t194/variants-residual.log`). A miter corner a rounding nearer took the Ebisu shrine's leader across a roof edge, cost 2,000 to 3,000 (observed 2026-11-18, method: `t194/reach.py` before the guard, `t194/reachdiff-2.log`), so `CORNER_EPS`, a rounding guard of a billionth of a pixel that decides nothing about the place, keeps the round point there.
   - Item 3, T193's impl-drift. A stroke of no length draws nothing for butt, a disc for round, a level square for square (SVG 2, 13.5.5), and `nearest_ink` answers None where nothing is drawn, `leader_of` then leading to the outline. `ink_nearest` is deleted and `leader_to_ink` measures with `nearest_ink` from the leader's start, so the least half-width (a CONVENTION, 0.5 px, "its drawn sizes") is `drawn_ink`'s alone. "which subjects carry ink" says "drawn with its box". `nearest_points` answers containment first, and on HEAD all 49 leaders `leader_to_ink` met were drawn as scored, on the clone 68 of 68 (observed 2026-11-18, method: `t194/agree.py`, `t194/agree-head.log`, `t194/agree-new.log`).
   - The claims. "which part a leader ends on", "where a leader ends", "when a leader is drawn" and the Python's "leader search" cite 0330, where their sentence now stands, and so do "a tie between parts" and "a stroke's drawn band", which it records as map drawing conventions, and the new "a closed outline's drawn edge", "a stroke's corner" and "a dashed stroke's dashes". The tie order still decides none of 372 exact ties in 89,728 calls (observed 2026-11-18, method: `t194/ties.py`, `t194/ties.log`). Every other pointer to 0242 names a sentence still there (observed 2026-11-18, method: `grep -rn` of the file name, each line read).
   - The record. 0242's leader bullet moved word for word to 0330 with its note, a bullet pointing to 0330 in its place, and 0330 adds the tie order and the drawn corners and dashes. 0242 went from 19,995 to 19,778 bytes and its notes to 8,695, and 0330 is 3,127 with notes of 420 (observed 2026-11-18, method: `wc -c`). The QGIS page's archive record names 0330's notes too. `make record CHECK=1` builds, and `make record-owed` owes quote-check and record-format on 0242 and 0330 alone (observed 2026-11-18, method: `t194/record-check.log`, `t194/record-owed.log`). Its turn and wrap topics are the next split.
   - The Rust tests. `stroke_tests.rs` is new, read from markup through APIs HEAD has: curves (two arcs, a cubic, a smooth quadratic), a path's subpaths, `Z` and inherited fill, joins (mitered, round, an unknown word, a house's corners, a 20 degree V beveled, mitered within a limit of 10, rounded), dashes (plain, one value, offset, square-capped) and two dots, and their edge cases pinned. Each drawn tip stands off the test's own drawing and within 1.05 px of it, each drawn leader the scored one, and all five failed on HEAD with T193's cap test (observed 2026-11-18, method: the tests' markup and `wrong`, `t194/red.log`).
   - The Python, held. `held.json` was re-taken by `held_cases.py` with two sheets more, its 30 earlier answers unchanged: a dashed ring in arcs, a well whose `Z` draws its upper side and two raked curves under a group's `fill="none"`, and a fence whose end lies in a dash gap, a wall bent to a V and a butt dot. HEAD's Python led the rope to 57, inside the ring, the fence to its gap, the V to its round corner at 80.7 and the dot to 192, and the clone to 62, a dash's end, the miter's point at 85.2 and 189 (observed 2026-11-18, method: HEAD's archive placing both sheets, `t194/held-strokes.log`). The placer's `held.json`, re-answered, moved none of 60 (observed 2026-11-18, method: `t194/held-hs-before.json`, `t194/reanswer.log`, `cmp`). Rust and Python place the four pool hand sheets the same (observed 2026-11-18, method: `cmp`, `t194/regen.log`).
   - The reach on the pool: of 190 captions, 5 seats and 8 leaders alone moved, each laid to its change (observed 2026-11-18, method: `t194/reach.py`, `t194/reachdiff-3.log`, `t194/variants-final.log`). Ochiba's well left the undrawn side of its square, by the `Z`. Ubame's rear yard took rank 4 for 14, its phantom segment gone. Hayakawa's RESIDENCE took ring 5 upper left for ring 3 above, its leader to the mitered corner clear where the round one met an obstacle, and then its family privy took ring 0 and the repair re-seated INNER COURT at 2,000 for 1,000 (observed 2026-11-18, method: `t194/why2.py`, `t194/why2-miter.log`, `t194/why-miter.log`). Hayakawa's captions cost 20,500 for 19,500, the other sheets as before, 33 leaders as before, and the 8 leader ends moved 0.0015 to 0.31 px onto the ring or a mitered corner (observed 2026-11-18, method: `t194/reach-head.jsonl`, `t194/reach-new.jsonl`). Each compound well caption left its square's undrawn side, and three leader ends moved 0.1 px (observed 2026-11-18, method: each `.svg` against the mirror's, `t194/county-magistracy-example-svg.diff`, `t194/ochiba-roundtrip-test-svg.diff`).
   - The sheets and audits. All six regenerated by `make map`, each manifest unchanged against HEAD, and `make pack-audit` and `make size-table` exit 0 on them and on the four placed texts, Python and Rust: every pack-audit report is HEAD's and the size tables differ only in the moved leaders' rows (observed 2026-11-18, method: `t194/regen.log`, `t194/checks.sh`, `t194/basechecks.sh`, `t194/checks-diff.log`). The Python seated the four sheets in 20.4 s on HEAD and 25.9 s on the clone, one run each, recorded only (observed 2026-11-18, method: `time`, `t194/reach-head.log`, `t194/reach-final.log`).
   - Found and left, for tasks before step 3b. A filled path's hole is read as a filled part: Hoshigaoka's grove holds one, its caption unmoved. A closed part's dashed outline is measured solid and an unfilled one's inside counts as ink. The audit's path walk keeps an arc by its end point (observed 2026-11-18, method: the grove's 9-point subpath wholly inside its first, `t194/grove.py`, `t194/grove.log`; `_part_nearest` and `path_walk`'s `A` arm read). Their task lines, drafted:
   - Drafted: Step 3a: a filled path's hole - a subpath inside another under its fill rule - is read as a filled part of its own, where SVG leaves it bare (Hoshigaoka's shrine grove holds one, its caption unmoved, T194) - `_path_points` and `read_sheet` in both copies - measured on the pool and fixed with a test red first, before step 3b (the GM 2026-11-18: fix all known bugs in each step).
   - Drafted: Step 3a: a closed part's dashed outline is measured solid and an unfilled closed part's inside counted as on the ink, where SVG draws neither (T194) - `_part_nearest`, `drawn_ink` and `leader_to_ink` in both copies - measured on the pool and fixed with a test red first, before step 3b (the GM 2026-11-18: fix all known bugs in each step).
   - Drafted: Step 2: the audit's path walk keeps an arc by its end point, so the viewBox crop's ink extent misses an arc's bulge (T194) - `path_walk` in `rust/mode_a/src/tagged.rs` and `pack_audit/shared.py` - measured on the pool and fixed with a test red first, before step 3b (the GM 2026-11-18: fix all known bugs in each step).
   - Tooling, fixed with this task: `make decide` and `make task-add` spun without end once 449's plan files neared 1 MB, not on the section's length - fancy_regex's 1,000,000-step limit made a `.flatten()` scan retry its error forever (measured 2026-11-18, `timeout 20 make decide F=449 T=T194` and a scratch `task-add`, scratchpad `lint-spin/`); the plan and task crates' pattern builders now run unlimited and their scans end on an error, each with a test red on the old code; the rest of the class is T185's.
   - The checks: `make static`, `make rust-test` and `make quick`, run one after another after the last edit (measured 2026-11-18 (`make static`, `t194/static.log`), (`make rust-test`, `t194/rust-test.log`), (`make quick`, `t194/quick.log`)).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a path read as SVG strokes it | `a_leader_ends_on_a_path_s_curve_as_the_sheet_draws_it`, `a_path_s_subpaths_are_strokes_of_their_own_a_z_closes_one_and_its_fill_is_inherited`, the held sheet, red without it | n/a (Mode A labels) | none (pages: three wells, Ubame's rear yard, the rope's leader) | n/a |
| joins and dashes drawn | `a_stroke_s_corners_are_joined_as_svg_joins_them`, `a_dash_gap_is_not_ink`, red without it | n/a (Mode A labels) | none (pages: Hayakawa's RESIDENCE, family privy, INNER COURT, seven leader ends) | n/a |
| a dot of no length; one measure for scored and drawn | `a_stroke_of_no_length_ending_flat_draws_nothing`, `a_stroke_s_band_and_a_part_s_drawn_edge`, red without it | n/a (Mode A labels) | none | n/a |

### T194 Approach (checklist part A)

1. **The goal, in the world.** A caption led out to a curved, closed, dashed or cornered stroke is tied to its ink as the sheet draws it, by the leader the placer scored, in the Rust and the kept Python alike, before step 3b, and the leader's rules stand on a research page with room to grow.
2. **The constraints.** FR-002 and the lockstep rule as T180 restated it. Constitution XIV. Research page 0242's drawing page and its split, docs/research-record-rules.md, "A question has a size". The GM's words above.
3. **Where each comes from.** G: the GM's request. R: 0242's leader rule, now 0330's ("it ends at the nearest drawn point - a disc's curve, a stroke's edge, a scattered part"). O: the red and green runs, the probes and the pool measures above.
4. **Do they describe the world here?** Run on this clone's crate, its kept Python and its six pool Mode A sheets (observed 2026-11-18, method: `t194/shapesdiff.py` on all six, `t194/reach.py`, `t194/variant.py`, `t194/agree.py` on the four caption-placing sheets, `t194/checks.sh` on all six).
5. **The order.** After T193. Before step 3b's first port (T152).
6. **The exits.** Green: `make static`, `make rust-test`, `make quick`, the plan review, the claims round and a gated `make land`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The Rust cases red on HEAD's code and green on the clone, every drawn leader the scored one, the moved captions each laid to its change, and every audit exit 0 (`t194/red.log`, `t194/rust-test1.log`, `t194/agree-new.log`, `t194/variants-final.log`, `t194/regen.log`).
10. **Before moving a constant.** n/a: no constant moves. `CORNER_EPS` is a new rounding guard.
11. **Before fitting things into room.** Not a room question.

**Performance work?** No - a defect fixed.


<!-- plan-archive: T195 to T187 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T195 to T195 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
### T197 (T187's checks found these outside their change: citations that do not support their sentences, terms a reader cannot place, pop-ups telling the reader wrong, and claims worded unlike the fine behavior; the GM 2026-11-18, request.md: "in general we should fix all known bugs in each step before moving on to porting the next step")

- **Approach**: the record corrections go through the record's own route, two fresh page sessions per group (write, then check-and-apply, `make page-session`), within the write cap; the claims' wording is restated in place and judged by `impl-drift` through the claims tool. No geometry, no code path and no drawn size moves.
  - **The briefs** (`specs/449-rust-codebase/briefs/t197-g1-write.md`, `t197-g1-checks.md`, `t197-g2-write.md`, `t197-g2-checks.md`), run as one queue so no two sessions share the clone at once. Each write brief assigns four questions by the runner's own count, the cap (measured 2026-11-22 (`l7r-gate brief-load` on each brief: write 4, check 2, write 4, check 3)). G1 is the household pages: 0004's citations, its glossary terms and its drawing page's phrase, `l7r-median-domain`'s citation line with 0030's two notes, and the two retirement-house pop-ups. G2 is the village shrine: 0222's range sentence, its unfootnoted sentence and its ridge tag, 0223's approach fence, and the two depiction rows on 0221's and 0222's drawing pages. The sessions do not commit: the clone holds other builders' uncommitted work.
  - **The median domain's section** is "Hierarchies", not "The Median Domain": the headman sentence stands under it (observed 2026-11-22, method: `grep -n` of `/host-l7r-repo/setting/l7r.md`, the heading at its line 141, the sentence at 151, the next heading at 155).
  - **The claims, restated** (constitution XIV: none is a defect, each a claim the behavior already meets):
    - the well curb's claim moved from the Country shrine section to the magistracy's, beside its wells, with two new GUESS claims for the `well` row's gear share and roof share from 0196's drawing page;
    - a GUESS claim for the sanctuary's 4-20 by 4-12 ft band, a tolerance of ours round the sizes 0222's drawing page draws (observed 2026-11-22, method: reading `docs/building-programs.md`'s Country shrine claims and 0222's drawing page);
    - the bath's tub claim in `rust/mode_a/src/compound/parts.rs` names the end order the code tries, west before east where the yard side faces north or south, north before south where it faces east or west (observed 2026-11-22, method: reading `tubs`, its `ends` array and `Face::along_x`);
    - the county example's storehouse (W) named a DEVIATION in its spec's `research` list: 19 x 16 ft as drawn, against the common 12 x 18 ft and toward Yokota's 18 x 15 ft store (observed 2026-11-22, method: reading the spec's storehouse entry and its `research` list's cited sizes). That list is the spec's own research and no claims-index unit (observed 2026-11-22, method: `grep -c county-magistracy-example dev/claims-index.json`, 0).
  - **The `guest` row**: its source, the guest quarters pop-up's Guesses, took a sentence naming the county example's 40 x 42 ft guest house (observed 2026-11-22, method: reading the pop-up's Guesses and 0091's drawing page), which `modal-form` ruled out under M9 and M13, since the pop-up serves every sheet and Depiction already says "or on some plans for a guest house of its own". Its edits applied, the pop-up and the row stand as they were. 0091's drawing page already records the county plan's guest house, so the record and the row do not disagree.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the record corrections | the record checks each page session ran, recorded with `make record-checked` | n/a (record words) | none | n/a |
| the claims restated | `impl-drift` on the claims bundle, recorded with `make claims-checked` | n/a (claim words) | none | n/a |

### T197 Approach (checklist part A)

1. **The goal, in the world.** A reader of the record finds each sentence supported by what its note quotes and each term glossed, a reader of a pop-up is told the retirement house's recorded size, and every claim says what the code does.
2. **The constraints.** Constitution XII (the record's citation and four-label rules), XIV (a claim the behavior meets is restated, never the code), the write cap of feature 274, the archive-first rule of feature 309, the modal guidelines of `dev/modals.md`.
3. **Where each comes from.** G: the GM's words above. R: 0004, 0028, 0030, 0091, 0196, 0221, 0222, 0223 and the setting's `l7r.md`. O: T187's checks, its plan section in `plan-done.md`.
4. **Do they describe the world here?** Yes: each finding re-read on the page it names before the briefs were written (observed 2026-11-22, method: `grep -o` of each quoted phrase in its file).
5. **The order.** After T187, whose checks found these. The claims round after the page sessions, since their page edits re-owe the claims that cite them.
6. **The exits.** Green: `make record` builds, `make record-owed` names nothing of these pages, `make claims-report` lists no finding of T197's claims. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The four sessions' handoffs, the record checks they recorded, `make record-owed` and `make claims-report` after them.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a
12. **Before any fix.** The pop-ups told a reader the retirement house's size is not recorded where 0028's drawing page records it, and the record's sentences said more than their notes quote: findings the record breaks, fixed in words. The claims are not defects: restated (constitution XIV).

**G2's outcomes** (`specs/449-rust-codebase/briefs/t197-g2-handoff.md`): 0222's opening now gives the Edo halls measured as about 13 ft square (Chikusei's side hall) to about 32 by 35 ft (the Ehime worship hall), its "How big" answer 18 to 35 ft long by 12 to 35 ft deep, the drawing page's band (observed 2026-11-22, method: reading 0222's findings page) - and its "three bays square" sentence narrowed to a village worship hall, and Hie Shrine's rank dated to 1874 from its source. 0223's drawing page labels the unfenced approach a GUESS beside Yasuda Hachiman's one late-Edo fence and a dated absence note. 0221's drawing page labels the kitchen end a doma (accurate) with a kamado on it (accurate, said of row-houses, the kuri a carry-over), the irori left off (a map drawing convention), and glosses `stipple`. Checks recorded: quote-check (0221.drawing three rounds, 0222 two rounds, 0223.drawing), record-format (0221, 0222, 0223), translation-check, source-reader and source-applicability on the three keys, and `make research-claim Q='0221 0222 0223' STATUS=done` (observed 2026-11-22, method: the G2 handoff's CHECKED lines and `make record-owed`).

**Found and fixed?**
- `make quote-verbatim` read a quote's CJK character and a digit with no space between them as a mismatch against a page that has one: `rust/gate/crates/research/src/verbatim.rs`'s `CJK_GAP` now also closes a gap between a CJK character and a digit, red first on its test in `verbatim/tests.rs` (the crate green, 109 tests, observed 2026-11-22, method: the crate's cargo test count in G1's run).
- `make reserve` held a registry key against a session whose clone directory is gone: `rust/gate/crates/record/src/record/reserve.rs`'s `held_elsewhere` skips a row whose clone no longer exists, red first in `reserve/tests.rs` and `apply_edits/tests/rare.rs` (the crate green, 91 tests, observed 2026-11-22, method: the crate's cargo test count in G1's run).
- "Divided-residence retirement" was unglossed on 0004: a sentence on it in the bullet "A retired couple often kept their own meals and purse", from a new note `kotobank-inkyo-5` (source-reader READ), and its glossary term `28220-divided-residence retirement.json`.
- G2's new hall range (13 ft square to 32 by 35 ft, 0222's findings page) left the old "21 to 35 ft on a side" in the pop-ups `sheet/hall-and-dwelling.md` and `sheet/compound-shrine.md`, and the old band in `pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.notes.md`, whose 28 by 32 ft hall stays inside the new 18-35 by 12-35 ft band (observed 2026-11-22, method: `grep -n` of the three files and 0222): restated to the record, the pop-ups through their modal checks.

**Where the deferrals land**: Each deferral lands before T158, Phase 4 S13, the deletion close that ends feature 449 (observed 2026-11-22, method: `grep -n T158 specs/449-rust-codebase/tasks.md`); no next step's port is filed before it, and T244 holds the parked hamlet stages until the GM is consulted.

**Found and left?**
- The retirement-house pop-ups' sizes and the choice pop-up's "beside the farmhouse" rest only on 0028's drawing page (modal-research M14). Not fixed here: moving a finding onto 0028's findings page is a page session of its own, past G1's write cap. Filed as T254; lands before T158.
- 0004's opening "is five people" (the house style's caste rule) and the bullet's "two households" where kotobank-inkyo-2 says separate meals and purse. Not fixed here: G1's quote-check on 0004 ended at its round cap, its third round recorded as dropped (observed 2026-11-22, method: the STOP bookkeeping line of `specs/449-rust-codebase/briefs/t197-g1-handoff.md`), so a rewording owes a check round of its own. Filed as T255; lands before T158.
- The farmhouse pop-up keeps "once they had handed the farm to their heir", the phrase G1.1(a) took off 0004. Not fixed here: modal-research's own EDIT kept it, finding it supported by the pop-up's Entry pages, so it needs a check round of its own. Filed as T256; lands before T158.
- 0030's tsubo-conversion note DIFFERS on `make quote-verbatim` (a '1' and a superscript 2 the page lacks). Not fixed here: outside G1's bundle. Filed as T257; lands before T158.
- The decide guard (`check_bundle_hooks.rs`) refused every G1 record check as 449 T248's, since `l7r-gate plan decided` names any open task without a CLEAR verdict, not the session's started task; each dispatch carried DECIDE_OK. Not fixed here: a guard change outside T197's record and claim words. Filed as T258; lands before T158.
- The hall-and-dwelling pop-up's acolytes are the GM's canon (`setting/l7r.md` line 707, observed 2026-11-22, method: `grep -n -i acolyte`) but no Entry page carries the sentence. Not fixed here: it needs 0229's canon comment to quote it, a page edit past G2's write cap. Filed as T259; lands before T158.
- 0222's absence note and drawing page still word the halls as before the correction, and 0221's `kuri-jawiki` note DIFFERS on `make quote-verbatim`. Not fixed here: outside the blocks G2's checks were given. Filed as T260; lands before T158.
- Hoshigaoka's notes and SVG call the kitchen mark a hearth where 0221's drawing page now says kamado. Not fixed here: a sheet and its re-render, engine work past T197's record words. Filed as T261; lands before T158.
- `set_down_hooks.rs` counts a foreground Agent result's agentId as a running launch, so the Stop hook looped in G2's check session. Not fixed here: a guard change outside T197's record and claim words. Filed as T262; lands before T158.
- The approach pop-up's Guesses tab lacks 0223's new GUESS, and the wood-kami altar pop-up's drawn size and color rest on no drawing page (modal-depiction). Not fixed here: each needs a record line written first. Filed as T263; lands before T158.
- A town's place card leaves out its farmhouses (`place.json`'s town `excludes_farms` true), where 0004's drawing page says a town counts them (impl-drift). Not fixed here: a defect in Mode A's card code and data, past T197's record and claim words. Filed as T264; lands before T158.
- The sanctuary pop-up's Depiction now names the gray strip the front of the plinth, but its Guesses tab has no bullet for the plinth 0222's drawing page calls a GUESS (modal-depiction). Not fixed here: a Guesses bullet re-owes the pop-up's form round, past its cap this task. Filed as T272; lands before T158.

**The claims round** (observed 2026-11-22, method: the impl-drift replies recorded with `make claims-checked`, then `make claims-report`): `impl-drift` on the 14 owed claims, 13 IN-STEP (observed 2026-11-22, method: its reply). The sanctuary band DRIFTED, crediting the reckoned three-bay size, the 4 ft floor and the 20 by 12 ft ceiling to 0222's drawing page (observed 2026-11-22, method: impl-drift's reply), and was restated to credit only the one- and two-bay sizes, then IN-STEP. Its two UNCLAIMED well decisions (0196's drawing page, the depth by the ground and the indoor well's beam pulley) were written as GUESS claims, IN-STEP. The approach-fence row was re-checked IN-STEP now that 0223's drawing page records its GUESS. `make claims-triage` cleared 33 claims with no block moved (observed 2026-11-22, method: its output). `make claims-report` owes 0 (measured 2026-11-22 (make claims-report)).

**Performance work?** No - record and claim words.


<!-- plan-archive: T198 to T198 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T199 to T199 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T200 to T198 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T200 to T200 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T201 to T198 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T201 to T201 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->

<!-- plan-archive: T202 to T198 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T202 to T202 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
### T203 (T202's plan review came back NOT-REVIEWABLE on a heading's `704x its SOUND derived budget` with no label, and T209's on `moved five captions a few pixels`: the figure lint passed both)

- **Approach**: the lint's whole-section rules already read a heading line - `SPLIT_UNIT` and `SPLIT_SENTENCE` cut at a line opening with `#`, and a heading such as `### T05 (183 lines)` is refused today (observed 2026-11-22, method: the count rule's test over that heading, green on the old lint) - so what let T202's heading through was its figure's form: `704x` is a figure to no rule, the unit pattern holding no `x` and item 4's bare-figure pattern refusing a digit run followed by a letter. So `rust/gate/crates/plan/src/plan/lint.rs` reads a multiple written close (`704x`, `100x-4,400x`) as a figure with a unit, everywhere the unit rule reads, the heading among them, and item 4's bare figure takes the `x` too; a rule's multiple (`past 2x`, `more than 2x`, `the 2x rule`, `the 2x raise`) is a limit and no figure, and a spaced `2 x 3` is arithmetic or a size and no multiple. A count spelled as a word (`two` to `twenty`, the tens, `hundred(s)`, `thousand(s)`, `dozen(s)`; never `one`, which names) is read by the count rule where a counted noun follows, as a numeral is, and the count nouns gain `captions`; a threshold's word (`at most ten keys`) stays a limit. Item 4's any-number rule does not take the words: on the first replay they added 45 item-4 findings, nearly all naming ("the three checks", "the two places") (measured 2026-11-22 (T203's replay of `findings` over every task section of `specs/*/plan.md` and `plan-done.md`, old lint against new)). The refusals' words name both forms. Red first: the new tests `a_multiple_needs_a_label_in_a_heading_as_in_the_approach` (T202's heading) and `a_count_spelled_as_a_word_needs_a_label` (T209's sentence) both fail on the old lint (measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/plan` in a detached worktree of HEAD with the new tests copied in: 2 failed, 167 passed)).
- **The replay**: every task section of `specs/*/plan.md` and `plan-done.md` through the old and the new lint gave 1547 and 1760 findings, 213 new and 0 gone, every new one a count spelled as a word and no new multiple (measured 2026-11-22 (a temporary test calling `findings` per `##`/`###` task block in both trees, its rows sorted and compared with `comm`; the rows kept in `/tmp/t203/replay-new-findings.tsv`)). Of the 213 new findings 203 are in closed sections - 65 of 449, 55 of 451, 28 of 405, 17 of 385, 11 of 444, the rest across 374, 417, 418, 420, 422, 423 and 435 - and are reported, not fixed; 10 are in open tasks' sections, reported to their owners and not fixed here, since each label is a measurement only its task's run can give and 449 T158's section is its builder's, mid-edit (measured 2026-11-22 (the same rows, each placed under its block's task and that task's box in its `tasks.md`)):
  - 417 T21 (plan.md:1136), `SC-006's two test landings`;
  - 417 T66 (plan.md:1251 and 1255), `the last three sites` and `a few hundred thousand calls`;
  - 444 T27 (plan.md:576, 579 and 682) and 444 T34 (plan.md:1109), `the two rows` and `the four files' run`;
  - 449 T158 (plan.md:378 and 382), `those two crates`, `its two cases`;
  - 449 T244 (plan.md:909), `three tests in phase_source_hooks/tests.rs`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the multiple and the number words | `lint/tests.rs`'s two new tests | n/a (a gate lint, no map) | none | none |

### T203 Approach (checklist part A)

1. **The goal, in the world.** A plan section reaches its review only once every figure it states - in a heading as in the Approach, written `704x` or spelled `five` - carries its label, so no review round is spent on what the lint exists to catch.
2. **The constraints.** Feature 385 T86 (item 4), feature 430 D5 (a figure with a unit), feature 449 T159 (a count), constitution XIV (a check passing the bad is a defect).
3. **Where each comes from.** O: T202's and T209's NOT-REVIEWABLE plan reviews (`specs/449-rust-codebase/plan-review.json`), and the replay above.
4. **Do they describe the world here?** Yes: the heading was already read and the multiple was the gap (measured 2026-11-22 (the count rule's test on a heading, and the new tests red on the old lint)).
5. **The order.** Before T216 (the session's order); no other task waits on it.
6. **The exits.** Green: the new tests green, the old lint red on them, the replay's findings listed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the forms came from the two reviews' own sentences, and the word list's reach from the replay.
8. **The budget.** One landing.
9. **Done, measured.** The plan crate's tests green but for `engine_edit`'s two, which fail on the other builders' uncommitted edits in this clone (449 T158's deletion close, 451 T141's plan crate) and pass in a worktree of HEAD (measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/plan` in the clone and in a worktree of HEAD)); the replay above.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a
12. **Before any fix.** The finding it breaks: T202's and T209's sections reached review with unlabeled figures the lint passed (a check passing the bad); fixed here, every instance in the plans found by the replay (observed 2026-11-22, method: the replay above over every task section).

**Found and left?** The 10 open-section findings above, each its task's own to label at its `make decide` (not a defect of this task: the lint now refuses each, so none reaches review unlabeled). `engine_edit`'s failing tests (`only_a_docstring_changed_passes_and_a_code_change_waits`, `an_area_hashed_by_its_bytes_always_waits_and_an_unreadable_id_waits`) fail in this clone on the other builders' uncommitted edits and pass at HEAD; not a defect of this task's files, which do not touch `engine_edit`, and theirs to see in their own closing checks.

**Performance work?** no

<!-- plan-archive: T204 to T202 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T204 to T204 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T205 to T205 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T206 to T206 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->

<!-- plan-archive: T208 to T199 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T208 to T208 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->

<!-- plan-archive: T209 to T152 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T209 to T209 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->

<!-- plan-archive: T210 to T156 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T214 to T156 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T214 to T214 moved to plan-done.md, 2026-11-19 (feature 375 FR-044) -->
<!-- plan-archive: T215 to T218 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T215 to T215 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T216 (T212's log, 2026-11-19: a first coverage run after the lockstep deletion seemed to name 5 lines, the next hundreds - observed 2026-11-19, method: T212's `make static` output in its transcript)

- **Approach**: no code change - not a defect (constitution XIV: a defect is a wrong outcome, not a difference). The coverage run named every uncovered line both times; T212's own command showed it only the last three files (measured 2026-11-22 (the replay and transcript below)). Measured three ways:
  - **Lead 1, the replay** - measured 2026-11-22 (T212's 86 timestamped tool calls up to its 18:10:06Z `make static`, read from its transcript `c6fd72d1.../subagents/agent-a9ff219aabc9012c9.jsonl` and run again in a worktree at its parent `443e0f8113`, with T212's own tool, `scripts/gates/l7r-gate.sh rust cover --crate rust/mode_a`):
    - The 18:10:06 tree's first coverage run names 20 files and 668 lines (measured 2026-11-22 (`grep -c` of the replayed run's log, `/tmp/t216x/s1810.log`)).
    - Its `audit/checks.rs` lines (133, 143, 144, 436, 472, 484) and `audit/labels.rs` lines (33-43, 53, 54, 61-64, 106-113, 115, 144, 145) are the ones T212's 18:12:00 run printed.
    - The previous builder's replay was a different state: the final tree with `check_fixtures` unwired, not the 18:10:06 tree.
  - **Why T212 saw 5** - measured 2026-11-22 (its 18:10:06 command, read from the transcript, against the replayed log):
    - The command was `grep -iE "^error|warning:|FAILED|uncovered|dead code|refus|Diff in" static.log | head -40; tail -6 static.log`.
    - The tool prints each file as `<path> - lines no test reaches: ...`, so no pattern matched a file line.
    - `tail -6` showed the last three files alphabetically: `parse/shapes.rs` 61, 86; `pool_sweep.rs` 404; `tagged.rs` 98, 327 (measured 2026-11-22 (`tail -6` of the replayed log beside T212's printed output)). That is exactly the "5 lines" of the task line (measured 2026-11-22 (the same comparison)).
    - T212's 18:12:00 command added `lines no test` to its pattern and saw them all.
    - So the 5-line reading was right for its code only as a tail: the report itself was whole.
  - **Lead 2, a stale report** - measured 2026-11-22 (`cargo llvm-cov report` run directly over a planted `STALE` report file):
    - An empty profile directory exits 1 ("no input files").
    - A profile with no binary exits 1 ("No filenames specified!").
    - Both leave the old file in place, but `cover.rs`'s `missed` reads the report only when the run's code is 0. Either case fails the crate as line 0, never as a stale read.
  - **Lead 3, concurrent runs** - measured 2026-11-22 (the clone's `.git/l7r-events/*.jsonl`, every `make` Pre/Post pair 16:00-18:30Z on 2026-11-19):
    - Only T212's own runs ran, one at a time.
    - Its blocked 18:10:02 `make static` never started.
    - No run overlapped another.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| none (no code changed) | n/a | n/a | none | n/a |

### T216 Approach (checklist part A)

1. **The goal, in the world.** The first coverage run after a deletion names every line the deletion uncovered. It does: the replayed 18:10:06 run names 668 lines (measured 2026-11-22 (`grep -c` of the replayed run's log)).
2. **The constraints.** Constitution XIV, a defect is a wrong outcome, not a difference; new Rust code owes 100% line coverage from its own tests (the root CLAUDE.md).
3. **Where each comes from.** O: the three measurements above; G: XIV as the GM restated it, 2026-11-19.
4. **Do they describe the world here?** Yes. The replay ran T212's own tool on T212's own tree, and the tool's outcome was right.
5. **The order.** After T203 (the session's order); no task waits on it.
6. **The exits.** Green: the replay names what the next run named (measured). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask` (not taken).
7. **The search smell.** None. The cause was a display filter in the session's command, not the tool.
8. **The budget.** One landing, the plan section alone.
9. **Done, measured.** The replayed first run's lines match T212's 18:12:00 lines file for file. T212's 18:10:06 view is reproduced exactly by its own `grep`/`tail -6`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing would change for any reader: not a defect, so the task line is restated here, not the code (constitution XIV).

**Found and left?** None.

**Performance work?** No.


<!-- plan-archive: T217 to T218 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T217 to T217 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T226 to T224 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T226 to T226 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T228 (T225 found it 2026-11-19, T158's builder 2026-11-22: the constitution's passages built on retired tools)

- **Approach**: each passage the task line names is restated in `.specify/memory/constitution.md` to the checks that hold its obligation today, as the record names them. Each is labeled upkeep or versioned by the Governance section's versioning policy. Bump only when a principle's obligation changes, including its enforcement mechanism; a retired command name in a sentence whose obligation stands is upkeep. The amendment follows the speckit-constitution skill's outline by hand: a Sync Impact Report entry, the footer's version and date, and the dependent templates. Its git hooks are not run, since the session commits. The GM's quoted words stay byte for byte. A passage whose tool and rule both went is labeled RETIRED in place, keeping its quotes as the record of what he ruled, as `dev/performance.md` keeps its retired sections.
  - **Upkeep, no version** (the obligation stands, a name retired):
    - VI's coverage-roll sentence, `make roll-audit`;
    - VI's time-as-evidence sentence, `make perf-ab`;
    - the Development Workflow's tooling-hash list, `pyproject`.
  - **Versioned** (the enforcement mechanism changed, the record holding its replacement):
    - VI's performance bookends (`make perf LABEL=`, `make perf-report`, `make perf SCALING=1`) restated to feature 443's work budgets: `make work-budget`, `make budget-sheets`, and the push's `make work-budget-review`. The record is `docs/guards.md`'s retired bookend row, `dev/performance.md`'s RETIRED section, and `l7r/diagram/CLAUDE.md`. The rule that history is never rewritten sits inside that block and stands unchanged.
    - X clauses 1 and 2 (ruff, `pyproject.toml`): no Python is left under `l7r/diagram/`, measured 2026-11-22 (`find -name '*.py'` outside `specs/`: only `scripts/gates/codeid.py`, outside X's scope). The project's lint and format are `make static`'s `rust lint` (clippy, `rust/Cargo.toml`'s `[workspace.lints]` and `clippy.toml`) and `rust format` (rustfmt).
    - X clause 12's held cap: from ruff's `PLR0915` and `check-function-cap.py` to clippy's `too_many_lines` at 100 lines (measured 2026-11-22 (a read of `clippy.toml`)), `#[expect(..., reason = "...")]` its exception. The record is `dev/rust-tooling.md`'s function-cap rows: "one for one, counts lines", feature 444 T17.
    - Technical Standards' Python tooling block and the Development Workflow's Python done checklist: to today's tools and `make done`.
    - XIX's enforcement: from `make dead-closure` to the compiler's `dead_code` lint in `rust lint`, with `l7r-gate rust dead` for an uncalled `pub` item. The record is T158's section.
    - The plan template's X entry: its ruff and `PLR0915` words, restated the same way.
    - escalation-check CUT all four of the versioned items on 2026-11-22 (`/tmp/t228/draft-versioned.md`), as already decided: by the GM's approval of feature 443's design on 2026-10-28, which names each check that ports one for one and the cap counting lines, and by T158's section. The report entry quotes that approval.
  - **Put to the GM through escalation-check** (the obligation would change): VI's one self-scoping command, `make maps` (v1.12.0 and v1.12.1). Today's tools are two commands, `make map MAP=` and the pool sweep `make rust-test CRATE=rust/mode_a`. The clause forbids a second command. The draft is `/tmp/t228/draft-for-gm.md`. escalation-check returned KEEP on 2026-11-22: removing an obligation the GM wrote himself is his decision. It also corrected the draft's context: at the port switch's `rust-only`, `make done` rolls no reference map, so REF_OK has nothing to bypass. So the passage is NOT amended here and goes to the GM as a question. The session recommends retiring the one-command clause, since a wide run costs about 15 s, measured 2026-11-22 (make static's cover step for `rust/mode_a`, 14.8 s). The alternative is a self-scoping target over the Rust sweep. Either answer is a MINOR amendment.
  - **The bump**: MINOR, 2.36.0 to 2.37.0. Enforcement mechanisms changed in three principles (VI, X, XIX), and no principle is removed or lifted from NON-NEGOTIABLE. The precedents are 2.33.0 and 2.34.0: a principle's requirement changes, MINOR.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the passages restated, the version, the template | n/a (governance text, no code) | n/a | none | n/a |

### T228 Approach (checklist part A)

1. **The goal, in the world.** The constitution names only checks that run. A session reading it is sent to no deleted command, and an obligation whose tool went is either restated to today's check or retired by the policy.
2. **The constraints.** The Governance section's versioning policy (GM 2026-09-06: upkeep takes no version). The task line: restate where the record holds the replacement, and escalate where an obligation would change. The GM's quotations stay untouched. No obligation is invented.
3. **Where each comes from.** G: the policy's own words, and the GM's quotes in each passage. O: the records named above, and the tree, measured 2026-11-22 (`ls`, `grep` of the Makefile for each target).
4. **Do they describe the world here?** Yes. None of `make maps`, `make perf`, `make perf-report`, `make perf-ab`, `make roll-audit` or `make dead-closure` is a Makefile target, and `pyproject.toml` and ruff are gone, all measured 2026-11-22 (`grep -n '^<target>:' Makefile`, `ls pyproject.toml`).
5. **The order.** After T158, whose deletion it records. Before T251, which takes the remaining Python-era passages. The `make maps` clause waits on the GM's answer, and whichever amendment he chooses lands after it.
6. **The exits.** Green: every named passage restated or retired, the report entry and footer at 2.37.0, and `make quick` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** No retired name from the task line is left in the principles as a live command, measured by `grep` of the constitution below its report.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session following the text runs a command that does not exist: a wrong outcome of the governance text. No map changes.

**Found and left?**
- VI's `make maps` clause: escalation-check KEEP, a question for the GM (above). Not fixed here: which amendment it takes is the GM's ruling. Filed as T252, which lands before T244.
- The constitution's other Python-era passages still name deleted tools: VI's Python bullet and roll census, X clauses 3, 5, 6 and 10, the quick and gate test forms, and the compliance line. So does the question of whether X keeps a subject. Not fixed here: they are outside the task line's list, and X's subject is a MAJOR question, the GM's. Filed as T251, which lands before T244.

**Performance work?** No.


<!-- plan-archive: T229 to T229 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->

<!-- plan-archive: T230 to T222 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T230 to T230 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T231 to T230 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T231 to T231 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T232 to T231 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T232 to T232 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T233 to T232 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T233 to T233 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->

<!-- plan-archive: T234 to T226 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T234 to T234 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T235 (T226's audit, 2026-11-20: the polder waterward budget prices the marsh drawing the Rust stage never does)

- **Approach**: the stage's derivation, `specs/444-work-budget-program/phases/waterward_polder.derivation.md`, re-derived in place from the Rust stage's contract (feature 444's `t42-brief.md`, stage 4c and drawing item 10). The marsh term is dropped: rounding, waving, the clip to open ground, the keep-out grid and the marsh record. What it prices now is the fringe the stage writes: the dike's face read once, the strips laid from it, each cut along the sluice channels' beds, and the pieces written. Its sizes were measured 2026-11-22 (`make hamlet` on the work budget's eight polder specs, seeds 4/25/39/47 at 10 and 20 households, each roll's SVG read for its dike band, channels and reed pieces, px = ft): the dike's outer face is 120 and 178 points, the two channels hold 6 points (4 reaches), 2 flanks are laid, and the 4 pieces drawn hold 82 and 111 points. The new totals are 2,310 at 10 and 3,206 at 20, exponent 0.48, against the standing 27,296 / 37,653 and the first 17,813 / 24,059. The work-budget agent judged it blind in MODE BUDGET (`waterward_polder.verdict-6.txt`). It was then lowered by `make budget-set ... LOWER=1`, which asks for no GM words. The tool re-pins the stage as `budgeted` and drops its accepted figures, so until the re-acceptance below the push ratchet, which holds accepted stages only, did not hold it. The stage was then counted against the new budget, measured 2026-11-22 (`make work-budget` in the clone, and the per-key counts from `hamlet --budget polder` built with the counters, the mean of seeds 4/25/39/47). In the clone it counts 13,449 at 10 and 17,937 at 20, 5.6x the budget and past the leeway, measured 2026-11-22 (that run). Of that, the fringe's own keys (`test@face`, `test@fringe`, `read@dike`, `write@strip`, `test@flanks`) count 3,359 and 4,692, 1.45x and 1.46x, measured 2026-11-22 (the same run). The rest is `test@bank` and `write@bank`, 10,091 and 13,245, measured 2026-11-22 (the same run): the denser bands of reeds on each channel bank that T240 is adding, uncommitted in the clone and unpriced here. At HEAD, in a detached worktree, the stage counts 3,929 and 5,501 with no bands, 1.70x and 1.72x, measured 2026-11-22 (`hamlet --budget polder` with the counters at bdb111b827): within the 444 FR-022 leeway. The Bounds' 2 strips are T240's tree: at HEAD the strips' written points are 120 and 170, a third strip laid, measured 2026-11-22 (the same HEAD run). If T240's seat change does not land, the figure must rise from 2,310, which `LOWER=1` cannot do. The stage was re-accepted on HEAD's count. The MODE AUDIT bundle was built in a detached worktree at HEAD with the lowered budget re-pinned there, against the newest recorded run (`dev/work-budget/20261120T094844Z-rust-1167cb8e2.json`), whose counts HEAD reproduces. Its verdict, `waterward_polder.audit-3.txt`, is LEEWAY, 1.70x and 1.72x, measured 2026-11-22 (that audit): the excess is the per-flank face scan and the cut at the channel beds. `make budget-accept` then accepted the stage at 3,929 and 5,501, so the push ratchet holds it again and refuses T240's unpriced bands at about 5.6x, measured 2026-11-22 (the clone's run above).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the re-derivation | n/a: a budget record, no code | `waterward_polder.derivation.md` rewritten | none | none |
| the lowering and the re-acceptance | n/a: the budget tools' own tests | `dev/work-budget.json`'s `waterward.polder`, `dev/work-budget-changes.jsonl` (through the tools) | none | none |

### T235 Approach (checklist part A)

1. **The goal, in the world.** The polder waterward stage is held to a budget near the work it does, so a regression of its own size reads as OVER, not WITHIN.
2. **The constraints.** Rubric S7, S8, S10 and S11. 444 FR-022: a budget is an estimate, with LEEWAY up to twice it. A lowering re-pins at no size higher (`budget-set LOWER=1`, ask:444-budget-standard, no GM words).
3. **Where each comes from.** R: 0019, 0027 and 0074 for the strips and their cuts. O: the input sizes measured 2026-11-22 (`make hamlet`, the SVGs read). G: the GM's 2026-10-28 budget standard, as the rubric quotes it.
4. **Do they describe the world here?** Yes. Measured 2026-11-22 (`make hamlet` on the work budget's own polder specs): the rolls are the ones `hamlet --budget polder` counts.
5. **The order.** Before 449 T158. With or after T240's stage work, whose tree the Bounds were measured on; this task does not touch its code.
6. **The exits.** Green: a SOUND verdict, the lowering taken, and the stage counted WITHIN or LEEWAY against the new figure and re-accepted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The stage's committed count against 2,310 / 3,206 is LEEWAY, and it is accepted at 3,929 / 5,501, measured 2026-11-22 (audit-3, `make budget-accept`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on the map changes. The budget record was the defect: it was 8x over the work (measured 2026-11-20 (T226's MODE AUDIT, `waterward_polder.audit-1.txt`)), so a regression could not show.

**Found and left?**

- T240's bank bands. With them the stage counts 5.6x the lowered budget, measured 2026-11-22 (above), and the ratchet now refuses that at T240's push. Not fixed here: the bands are T240's uncommitted stage code, and pricing them (RAISE=1) or making them cheaper is T240's work. Filed as T250; lands before T240.
- Not a defect. The strips are drawn as plain polygons, which departs from 0074's waved, never-ruled marsh edge. That departure is a labeled deliberate deviation, a drawing convention the Rust driver was given (`t42-brief.md` item 10), and the derivation's preamble labels it too. It is drawing work, not this stage's work, and is flagged to the session for its ruling.

**Performance work?** no - a budget record, no code.


<!-- plan-archive: T236 to T234 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T236 to T236 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T238 to T239 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T238 to T238 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T240 (impl-drift on T236 and T239, 2026-11-20: five polder drawing points the claims check could not confirm)

- **Approach**: each point measured on Kuwabata (seed 21, the pool's polder) and a grid polder falling obliquely (seed 5, 30 degrees) by a throwaway test reading the roll in process, `make rust-test CRATE=rust/phases`, measured 2026-11-22 (the driver's manifest carries no geometry). (1) The way out past the waterside reeds: the seat asked its way out again with every strip and the wild pond's fringe grown by the lane's 8 ft as walls - clear on both, before and after (4), measured 2026-11-22 (`Exit::has_exit`); no defect, so the claim at `roll_polder` is restated to 0081's every-way-off-every-marsh and the question is asked of every fresh seed by a new cohort check, `seat_walled_by_reeds` (`check::walled_by_reeds`). (2) The bank band: 98 ft of the feeder and 319 ft of the outfall's drain ran through reeds on Kuwabata (115 and 564 on the oblique polder), measured 2026-11-22 (one-foot samples within the channel's half-width and 3 ft of a reed ring), and nothing drew 0074's denser band; `bank_bands` now lines each bank with a 6 ft band of denser, darker reeds (`Svg::reed_bank`, the `reed-bank` tile), only where the bank's ground is reeds and never on the pond - on Kuwabata 32 and 32 ft along the feeder, 28 and 312 ft along the outfall, measured 2026-11-22 (the band runs' lengths). Rendering: the band and its tile a CONVENTION (0074's own label), its 6 ft the deleted `BANK_FT`. (3) The cohort's check: `polder_checks` gains `seat_on_dike` (a corner of the settlement's ground inside the dike's outer face, or a point of the face inside the ground, past the slack, `SLACK_FT`, a CONVENTION of 1 ft) and `seat_on_canal` (the ring canal's ditches sampled every `CANAL_STEP_FT`, a check's grain of 2 ft, labeled NONE); red first on T239's unfixed roll (the seat handed the plots' edge), which the old check named nothing on. (4) The landward shore: both seats faced the head, their backs up the fall beside the wild pond - Kuwabata's to the north, its reeds on the west, east and south, against 0019's drawn polder (the wild pond at the head's corner, reeds on the west flank and the low foot, the dry landward shore and the village to the east), measured 2026-11-22 (the seat frame's `out`, the fringe's flanks). Ruled on the record: the head holds the wild pond and the foot the outfall's marsh, so the landward shore is a cross flank; that it is the one turned away from the pond is this project's reading, a GUESS (`landward`); the shore is kept over the wind (0072's back to the wind is not weighed against it by either page - the algorithmically easier route, a GUESS), each seat recorded against the map's wind. Kuwabata's settlement now stands east with reeds west and south, as 0019 draws it; the oblique polder's on its north-east flank, away from the pond. 96 fresh cohort seeds (48 grid, 48 dike-pond) all seat and break no rule, measured 2026-11-22 (`make cohort N=48 FIELD=`). (5) The standoff: along the band the dike's outer face stands 2.7 to 24.3 ft inside the seat's ring on Kuwabata and 0 to 22.9 ft on the oblique polder, measured 2026-11-22 (the face's points projected on the frame), so the houses stand 12 to about 36 ft off the face; 0019's "a few steps off the dike" is its own GUESS with no number, so `STANDOFF_FT` is a GUESS and a knob and its claim is restated (at `STANDOFF_FT` and `roll_polder`), not the code.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| (3) the settlement's ground off the dike and the ring canal | `a_settlement_over_the_dike_and_the_ring_canal_is_named`, red first on T239's unfixed roll | `check.rs`'s `ground_on_polder`, `polder_checks` | none: a check | none |
| (4) the seat's back to the landward shore | `the_seat_stands_on_the_landward_shore`, red first (the seat handed no shore); `a_pond_on_the_heads_middle_turns_the_shore_to_the_wind`, the tie, written to the new code | `polder.rs`'s `landward`, `roll_polder`; `driver.rs`'s `Ground::back`, `stage_seat` | Kuwabata's drawing: the settlement east, the east reed strip gone | none |
| (1) the way out asked again past the strips | `a_settlement_over_the_dike_and_the_ring_canal_is_named` (a planted strip named `seat_walled_by_reeds`) | `check.rs`'s `walled_by_reeds` | none: a check | none |
| (2) the denser band on each bank | `a_channel_through_the_reeds_is_lined_on_each_bank`, red first (no band drawn) | `polder.rs`'s `bank_bands`, `roll_polder`; `svg.rs`'s `reed_bank`, `REED_BANK_TILE` | Kuwabata's drawing: four bank bands | none |
| (5) the standoff restated to 0019 | n/a: a claim | `driver.rs`'s `STANDOFF_FT` comment, `polder.rs`'s `roll_polder` comment | none | none |
| `polder.rs` past the 1,000-line bar: its tests split out | n/a: the same tests, moved | `polder/tests.rs` (new), `polder.rs`'s `mod tests;`, `driver/CLAUDE.md`'s index | none | none |

### T240 Approach (checklist part A)

1. **The goal, in the world.** A polder village on its dry landward shore a few steps off the dike, never over the dike or the ring canal, its way out dry past every reed, and each channel through the reeds lined by denser reeds.
2. **The constraints.** R: 0019's drawing page (the landward shore, every other flank holding water back, the village a few steps off the dike - its GUESS); 0074's drawing page (the bank band, a CONVENTION); 0081's drawing page (every way off every marsh's reeds); constitution XIV (a claim the code does not literally match, the behavior fine, is restated).
3. **Where each comes from.** R: the pages above. O: the measurements in the Approach, 2026-11-22.
4. **Do they describe the world here?** Measured on Kuwabata and an oblique grid polder in process, and on 96 fresh cohort seeds, measured 2026-11-22 (`make rust-test CRATE=rust/phases`'s in-process rolls; `make cohort N=48 FIELD=`).
5. **The order.** (3) first, then (4), then (1) and (5) re-measured on the new side, then (2); before T158.
6. **The exits.** Green: the five new tests and the 96 polder cohort seeds clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each point measured once before its change and once after.
8. **The budget.** One landing.
9. **Done, measured.** `make rust-test CRATE=rust/phases` green with the new tests and the crate's lines all covered, and the polder and comb cohorts clean, measured 2026-11-22 (`make rust-test`, `rust cover --crate rust/phases`, `make cohort N=48 FIELD=polder_grid`, `FIELD=mulberry_dike_fishpond`, `N=24`); `make map MAP=pool/hamlets/kuwabata` REGENERATED.
10. **Before moving a constant.** n/a: `STANDOFF_FT` kept, its claim restated; `BANK_FT` new at 6 ft, a CONVENTION (0074's feature 300 width).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** (4) a reader sees Kuwabata's village beside the wild pond at the head and reeds on its east flank, against 0019's drawn east shore; (2) a reader sees no denser band along a channel through the reeds, against 0074; (3) the cohort could not see a settlement over the dike. (1) and (5): nothing a reader sees - restated (constitution XIV).

**Found and left?** None that breaks a finding: south-west of the outfall's straight leg the ground is bare where the west strip ends at the corner's diagonal, so the outfall's west bank carries 28 ft of band against its east bank's 312 ft, measured 2026-11-22 (the band runs' lengths) - T236's strip extent, the foot's reeds reaching the outfall as 0019 draws them; no page puts reeds west of the outfall.

**Performance work?** no

### T241 (impl-drift on T239, 2026-11-20: off_the_dike's bundle held 0019 and 0081 while its claims cite 0027)

The 0081 of that bundle was another unit's page: T239's bundle held several units, and off_the_dike's own claims cite 0019 and 0027 alone (its unit bundled alone, measured 2026-11-22), so 0081 leaving is no loss.

- **Approach**: the claims bundle (`rust/gate/crates/claims/src/claims/bundle.rs`) gathered a unit's questions from its claims' parsed backings alone (`Claim.pointers`), and dropped a backing page that was not a file without a word. A claim's line can cite a page the grammar does not read as its backing: an account's `...; research/questions/<page>: ...`, or a `GUESS: research/questions/<page>: ...`, whose colon makes the page account and the backing a bare GUESS. off_the_dike's two claims cite 0027 both ways. The fix is `cited_pages`: the backing's pointers, then every `research/questions/NNNN-<id>[.drawing].html` the claim's line names (the grammar's own `POINTER` pattern), in order, once. Every one is bundled, and a page that is no question file refuses the bundle, naming the unit, the claim and the page. Each claim's `units.json` pages are its `cited_pages` too, where they were its pointers: `claims-checked` drops a reply's rests on a page not in them (`reply.rs`, "a page it does not cite - dropped"), so a verdict resting on a 0027 block would have lost that rest. Red first: `every_page_a_claim_cites_is_in_its_bundle_or_the_bundle_refuses_naming_it` (`bundle/tests.rs`). At HEAD it failed at its first assertion: the account-cited page was not bundled. Its refusal half names a page the record never had. The replay was measured 2026-11-22 (the builder over every claim of `dev/claims-index.json`, in four bundles of at most 900 keys; each gaining unit then bundled alone and its `questions/` diffed against its `units.json` pages, which are exactly the old page list):
  - 3,274 claims over 2,562 units bundled, and none refused, measured 2026-11-22 (the replay). Six index rows (measured 2026-11-22, the builder's `no such claim(s)` lists) name no current claim and were left out; they are the index's stale rows.
  - 63 units gain 72 pages, measured 2026-11-22 (the replay), for example `polder.rs::off_the_dike` +0027, `waterward.rs::pieces` +0019 +0027, `field/dike.rs::CROWN_FT` and `GAP_HALF_FT` +0027, `audit/sun.rs::NOT_STANDING` +0038 +0103 +0165, `compound.rs::sheet` +0090 +0092 +0242. The list is in the session's report.
  - Over those bundles' claim lines, 0 `research/questions/` mentions miss the pattern, and 0 pages are cited by a bare id, measured 2026-11-22 (a scan of every KEY line of the four MANIFESTs). "Every page" holds for the record as it stands.
  - `make claims-owed`'s set was empty, and `--owed` selected none.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| `cited_pages` in the bundle | the test's first assertion red at HEAD | n/a (tooling, no map) | none | n/a |

### T241 Approach (checklist part A)

1. **The goal, in the world.** An impl-drift check reads every page a claim cites, so a figure is judged against the page it names.
2. **The constraints.** The claims grammar (`grammar.rs`'s `GRAMMAR`) is unchanged. The bundle builder's page list is the only thing changed: T158's builder holds the rest of the claims crate.
3. **Where each comes from.** O: impl-drift on T239 (the task line). O: the replay above.
4. **Do they describe the world here?** Yes. off_the_dike's bundle now holds 0019 and 0027, measured 2026-11-22 (its unit bundled alone).
5. **The order.** Lands before T158 (the task line).
6. **The exits.** Green: the red test passes and the replay refuses nothing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The claims crate's tests are green, 156 passed (the units.json pages assertion red first), measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/claims`). The replay over every claim refuses none, and the 63 units hold their 72 pages, measured 2026-11-22 (the replay).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A bundle missing a cited page lets a check pass unchecked. Nothing on a map changes.

**Found and left?**
- `units.json`'s pages read the backing's pointers alone, so a reply's rests on an account-cited page were dropped: fixed here.
- The research fingerprint and the standing blocks still read the backing's pointers alone (`index.rs` `research_fp`, `standing`, `research_why`). So an edit of an account-cited page, such as 0027 for off_the_dike, moves no claim owed. The 63 units' standing verdicts were also judged without these pages. Not fixed here: the fingerprint is read in `index.rs`, T158's builder's file, and moving it makes all 63 units owed for a re-check round; filed as T249, the 63 units' re-check with it; it lands right after T158 and before the next port step begins: lands before T247.

**Performance work?** No.


<!-- plan-archive: T242 to T242 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->

### T243 (449 T201 found it, 451 T36 re-read it: a pool-sheet stage of Mode A had no change, raise or accept path)

- **Approach**: `budget_change/sheets.rs` built a pool-sheet stage's first budget and its comparison and nothing more. So a placer or compound sheet held past twice its budget refused every engine push (`work_budget_review.rs`'s `hold_sheets`) with no route but a hand edit of a guard file, against 444 FR-022. `make budget-change` now takes a pool-sheet stage for each of the three paths, through the hamlet stage's own rules. The checks the two stages share were cut out of the hamlet path into `budget_change/rules/shared.rs` and are called from both; none is copied:
  - raise: `raise_ready`, `no_raise`, `past_first`;
  - change: `NO_WORDS`, `repoint_refusal`;
  - accept: `audit_refusal`, `over_refusal` with its `Held` figure.
  The split also keeps `rules.rs` under the file-scale bar, at 880 lines, measured 2026-11-22 (`wc -l`). A sentence's list of names is one helper, `rules::and_said`, which `households_said` and the sheet accept's reply both call. Each path:
  - **Raise** (`make budget-set RAISE=1 [SECOND=]` on a pool-sheet derivation): it owes what a hamlet raise owes. The stage must be budgeted, not yet accepted. The derivation must name the work its first missed and carry a SOUND verdict. Its Totals must hold every sheet the stage holds. It must be a raise on the sheets together (`no_raise`, as a hamlet raise is judged at its top size). On each sheet it is capped against that sheet's first figure (`past_first`: a second SOUND past twice it, the GM's words past ten times it). The first raise records `first`, and later raises keep it.
  - **Change** (`make budget-change`, with the GM's WORDS checked by the same hook): the figures `TO="<sheet>=<ops> ..."` names, or a re-pointed SOUND derivation's Totals, or both.
  - **Accept** (`make budget-accept COUNTS="<sheet>=<ops> ..."`): the MODE AUDIT's WITHIN or LEEWAY, or the arbiter's accept, with every sheet counted and held as a hamlet size is. The figures are recorded as `accepted`. The push now holds an accepted sheet to that figure as well (`hold_sheets`), as it holds a hamlet stage at its sizes.
  Red first, each measured 2026-11-22 (`make rust-test CRATE=` of the crate):
  - `a_pool_sheet_stage_is_raised_on_a_sound_re_derivation` failed at HEAD with "`--raise` - a hamlet stage's - is not taken", and its three siblings (the raise's refusals, the change, the accept) failed with it.
  - `an_accepted_sheet_over_its_accepted_figure_is_refused` failed with the hold's hunk taken out.
  - Green: trials 134 passed, measure 204 passed.
  - Closing: clippy's line cap split the paths test into three helpers, its assertions unchanged. Every multi-line assert now binds its value first and asserts on one line. The lines no test reached are closed:
    - the accept of a stage raised with a second SOUND: a new case, accepted on a LEEWAY at 1,300 on beta-sheet, past twice its first of 480 and within ten times it;
    - the unreachable `KeyError` wrapping of `entry_of` dropped, since change and accept route only to a stage that exists;
    - the budget write folded into one loop;
    - the one-sheet reply taken by `and_said`.
    Lint clean and cover green on the trials crate, measured 2026-11-22 (`scripts/gates/l7r-gate.sh rust lint|cover --crate rust/gate/crates/trials`).
  - Found closing: `tests/hooks/test-closing-checks.sh` inherited the caller's CLOSING_TASK and CLOSING_FEATURE from `make closing-checks T= F=`, so its section 6 judged the wrong feature's task, 5 failed. The suite now unsets both. Measured 2026-11-22 (the suite run with CLOSING_FEATURE=449 CLOSING_TASK=T243): 45 passed and 5 failed before the fix, 50 passed and 0 failed after.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the shared rules, the three sheet paths, the accepted hold | the four sheet tests and the hold test red at HEAD | n/a (tooling, no map) | none | n/a |

### T243 Approach (checklist part A)

1. **The goal, in the world.** A pool-sheet stage of Mode A past its budget has the routes a hamlet stage has: a raise on a SOUND re-derivation, a change with the GM's words, and an acceptance. So it is never stuck refusing every engine push.
2. **The constraints.** 444 FR-022: the leeway, the raise without his words on a SOUND re-derivation naming the missed work, and the caps at 2 and 10 times the first. 444 FR-005 and FR-006: the accept. 443 FR-005: a change needs the GM's words. The task line: reuse the hamlet path, write no copy.
3. **Where each comes from.** G: 444 FR-022's words (the GM 2026-11-03, `budget_change.rs`'s header). O: 449 T201's finding, re-read by 451 T36.
4. **Do they describe the world here?** Yes. The real table's three pool-sheet stages (placer 6 sheets, compound 2, pipeline 2, measured 2026-11-22 by a read of `dev/work-budget.json`) are all budgeted, so each path applies to them. No figure of theirs moves in this task.
5. **The order.** Lands before T158 (the task line). After T241.
6. **The exits.** Green: the red tests pass and the hamlet tests are unchanged. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** trials 134 passed and measure 204 passed, measured 2026-11-22 (`make rust-test CRATE=`). The hamlet stage's own tests pass unchanged, so the shared rules keep its refusals' words.
10. **Before moving a constant.** n/a: LEEWAY and RAISE_CAP are read, not moved.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A pool-sheet stage past twice its budget refused every engine push with no route but a hand edit of a guard file, a wrong outcome against 444 FR-022. Nothing on a map changes.

**Found and left?**
- `hold_sheets` held an accepted pool-sheet stage to twice its budget alone, below the accepted figure a hamlet stage is held to; fixed here.
- A pool-sheet stage's lowering (a hamlet stage's `LOWER=1`) is not built, and its counts are taken as given rather than read off `l7r-mode-a caption-counts`. Not a defect: no outcome is wrong without them. A lowering can be made with `make budget-change` and the GM's words, and the push re-counts every sheet itself.

**Performance work?** No.


### T244 (the GM 2026-11-21, docs/gm-rulings.md, its section Stop before homesteads, and talk first: "When you get to the point where you have ported everything else and then we're ready to go back to homesteads, then don't actually proceed. Why don't you go ahead and stop, and then we can talk more after everything else is done before you get started on that.")

- **Approach**: one shared reader, `rust/guard/shared/src/parked.rs` (the stages `rust/parked/src/` holds, read from the tree: homesteads, track, appurtenances, law, ways; a task's stage, its box line opening `phase: <stage>` or a `phase:` line of its block; the resumed record `<git common dir>/parked-resumed.jsonl`; the write and shell predicates; the ruling and the refusal), and four doors over it. (a) The source move and the `lib.rs` line: `rust/guard/src/guards/phase_source_hooks.rs`, its matcher widened to `Write|Edit|MultiEdit`, a parked arm run before the read hold's early returns - a Write, Edit or MultiEdit landing in `rust/phases/src/<stage>(.rs|/...)`, or putting a `mod <stage>` into `rust/phases/src/lib.rs` that the replaced text lacked, and a shell write the tree walk finds there (`mv`, `cp`, `rsync`, a redirect, `sed -i`; a `git mv`'s destination read from its last word, since the walk lands it where git runs), refused unless the stage is resumed. (b) The task-start: `rust/gate/crates/task/src/task_start.rs`'s `parked_stage`, before the performance-first check and before any file is written, so the session is told to stop, never to escape `PERF_LATER_OK`. (c) `GM_RESUMED="<the GM's words>"` is the escape: the gate checks its form (two words, recorded in the guard log as `parked-stage`, the stage then written to `parked-resumed.jsonl`), and the guard holds its words on a shell call - a move, or a `make task-start` - to a message the GM wrote this session (the approval line's test, `feature_approval_hooks::problem`, as `budget_change_hooks` holds `WORDS=`), so a session cannot resume a stage on words of its own; a heredoc body or a quoted argument naming `GM_RESUMED=` is no escape. (d) The set-down: `set_down_hooks`' two pickers and its fallback skip a held stage's task; with only those open, the Stop refusal names the ruling and `make set-down`, and `set_down.rs`'s `parked_stop` takes that set-down with no arbiter ruling and under the usage cap, its row carrying `ruling` and its reply naming it.
- **Which stage tasks are held**: the parked ones, not every 444 `phase:` task. 444's T27 (seat) and T29 (waterward) are stages already in `rust/phases/src/lib.rs`, open but not parked; the GM's words are "go back to homesteads", and `rust/parked/CLAUDE.md` names homesteads, track and appurtenances (with law and ways) as the parked ones. One predicate (`parked::held_task`), read from the tree, so a stage moved back is held no longer.
- **Measured before**, measured 2026-11-22 (a fixture clone `/tmp/t244-measure/c` holding 444's real `spec.md`, `plan.md` and its tasks.md with only T30-T33 and the GM review open, the Stop replayed through `tests/hooks/set-down-hooks.sh`, the set-down through `scripts/gates/l7r-gate.sh set-down 444` under the session's real cap reading): with nothing running the guard named `T30 phase: homesteads ... - performance work first, FR-013: make task-start F=444 T=T30`, with one agent running the free slot named `make task-start F=444 T=T30, then dispatch its builder`, and `make set-down` was refused with `the weekly cap is 100% and the 7-day figure is 64%`, measured 2026-11-22 (the same fixture). With T27 and T29 open too, both named T27 (seat), measured 2026-11-22 (the same fixture, its tasks.md with T27 and T29 open).
- **The replay** measured 2026-11-22 (`/tmp/t244-replay`, a scratch crate on this clone's `l7r_shared`, one process, 8.5 MB peak, 3.4 s): `parked::shell_hits` over the 9,646 Bash calls of T93's `/tmp/t93/replay-cmd.jsonl` (Bash calls only; the corpus holds no Write or Edit) - 0 hits, so 0 changed verdicts; one row names `GM_RESUMED=` (this task's own `make task-add TITLE="..."`), a quoted argument, which `parked::words` reads as no escape after the fix the replay found (it was a hit of `words` before; the guard's verdict on it was unchanged either way, since the row invokes `task-add`, not `task-start`, and moves nothing).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the guard's parked arm | three tests in `phase_source_hooks/tests.rs` (a refused move: `git mv`, Write, Edit; a refused `lib.rs` declaration: Edit, Write, MultiEdit, a shell append; the GM's words resuming and recorded, invented or short words refused) and suite 2 of `test-phase-source-hooks.sh` | n/a: no engine code | none | `GM_RESUMED` |
| task-start | `a_parked_stage_s_task_is_refused_until_the_gm_s_words_resume_it` | n/a | none | `GM_RESUMED` |
| set-down | `only_parked_stages_left_the_stop_is_taken_under_the_cap_naming_the_ruling`, `a_parked_stage_s_task_is_never_the_next_and_only_those_left_name_the_ruling`, suite 9 of `test-set-down-hooks.sh` | n/a | none | `SET_DOWN_OK` |

### T244 Approach (checklist part A)

1. **The goal, in the world.** Once everything else is ported, the session stops before any parked hamlet stage and the GM talks with it first; no door lets a session resume one on its own judgment.
2. **The constraints.** The GM's ruling (docs/gm-rulings.md, 2026-11-21); `rust/parked/CLAUDE.md`; the guard rules of the root CLAUDE.md (match invocations, not mentions; the refusal prints the compliant command; every escape recorded); 451 FR-013 (performance first), whose pickers this joins.
3. **Where each comes from.** G: the GM's words above. O: the measurement before and the replay (above).
4. **Do they describe the world here?** Yes: measured 2026-11-22 (the fixture above) that the Stop guard and the free slot named T30 homesteads and the set-down was refused under the cap - the push into the parked stage the ruling stops.
5. **The order.** After 451 T88 and T102 (the pickers it joins); before any 444 stage task past waterward starts.
6. **The exits.** Green: the pins in the table pass, the replay shows 0 changed verdicts, `make closing-checks T=T244` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The pins green; the replay's 0 hits over 9,646 calls, measured 2026-11-22 (`/tmp/t244-replay` over `/tmp/t93/replay-cmd.jsonl`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; a session would otherwise be pushed into homesteads by the Stop guard and refused its stop by the usage cap, against the GM's ruling.

**Found and left?**
- The tool profile's incremental build linked broken binaries: `make rust-test` failed to link `l7r-rust` (`rust-lld: error: undefined hidden symbol: core::ptr::drop_in_place<serde_json::Value>`) after this task's `l7r_shared` edit, and `make decide`, `make closing-checks` and the review's `make plan-verdict` failed to link `l7r-gate` (an undefined hidden symbol in `libl7r_gate_task`'s `try_fold`) after its task-crate edit - a make target that cannot build valid code, observed 2026-11-22, method: five make runs' logs (`/tmp/t244-red-*.log`, `/tmp/t244-decide.log`, the closing check's `quick.log`, the review's report); clearing the crates' `tool/incremental/` dirs did not cure it, `CARGO_INCREMENTAL=0` built both. Not fixed here: its cause is in the incremental build of the target directory several builders share at once, not in this task's code, and finding it is build-tooling work. Its fix is 451 T142; filed as T246; lands before T158.

**Performance work?** No.


### T246 (T244's builds met a link failure that 451 T142 fixes; filed so the next step waits on it)

- **Approach**: no code here; this task tracked 451 T142, and closes on it. The defect: the tool profile's incremental build linked broken `l7r-gate` and `l7r-rust` binaries (`rust-lld: undefined hidden symbol`), observed 2026-11-22 in T244's five make runs' logs (`/tmp/t244-red-*.log`, `/tmp/t244-decide.log`); `CARGO_INCREMENTAL=0` built both. 451 T142 landed on main as 22607c7f91 ("the gate launcher heals a stale incremental unit on a link failure", 2026-11-22 06:28Z) and was ticked by 451de9cd61 (06:40Z), both in this clone's HEAD, observed 2026-11-22, method: `git merge-base --is-ancestor`. What it does, per 451's `plan-done.md` T142 section: rustc 1.87's incremental release with local ThinLTO can reuse one codegen unit's post-LTO object while the unit defining a symbol it imports is rebuilt under a new `.llvm.` name, so a crate's rlib holds an undefined symbol behind a fresh fingerprint; a `CARGO_INCREMENTAL=0` build is a separate artifact set and leaves the bad rlib for the next incremental build, which is why it came back. `scripts/gates/l7r-gate.sh` now reads each `<crate>-<meta>.<unit>.rcgu.o` the linker names, drops only that crate's incremental session holding the unit and its `.fingerprint/<crate>-<meta>` under cargo's own `.cargo-lock`, says what it dropped, and rebuilds once incrementally; a link error naming no unit rebuilds once with `CARGO_INCREMENTAL=0`; a second failure is refused with the cargo text. Since it landed, measured 2026-11-22 (a grep of the 294 build logs written after 06:40Z, every `/tmp/*.log` and every clone's `.git/closing-checks/*/` log, for `undefined hidden symbol`, the launcher's `stale incremental state` and `rebuilt and linked`, and of the session transcripts' tool results after 06:40Z): the stale unit came back once, in the closing-checks run `20261122T065504Z-458694` (its `static.log` and `quick.log`: `l7r_gate_cohort`'s and `l7r_gate_measure`'s units named), and the launcher's own messages show it healed: "the link failed on stale incremental state ... dropped ..., rebuilding once (feature 451 T142)", then "l7r-gate: rebuilt and linked". No build failed to link since: no log holds "the rebuild after dropping the stale state failed too", and every other transcript hit is the task's own text quoted, not a build. This session's builds on the default incremental profile linked, measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/trials`, `/tmp/t253-green.log`, `/tmp/t250-fix-green.log`, and `make closing-checks T=T253`, `/tmp/t253-cc2.log`, GREEN, with no `CARGO_INCREMENTAL` override). Nothing is built here.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| tracked 451 T142, landed | n/a - no code here; 451 T142's own pin is its stub-cargo test | none | none | n/a |

### T246 Approach (checklist part A)

1. **The goal, in the world.** A make target that builds valid code links it, with the default incremental profile.
2. **The constraints.** Constitution XIII and XIV; the GM 2026-11-18, a step's known bugs fixed before the next step's port.
3. **Where each comes from.** G: the GM's 2026-11-18 words; O: T244's make-run logs, and the build logs since 451 T142 landed.
4. **Do they describe the world here?** Yes: the failure was measured in this clone's shared target directory, and the heal was seen in this clone's closing-checks log.
5. **The order.** After 451 T142 (landed); before T158.
6. **The exits.** Green: 451 T142 landed and default-profile builds link (both met, measured 2026-11-22 above). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** 451 T142 ticked (451de9cd61); since then one stale unit met and healed by the launcher, no build failing to link, and this session's `make rust-test` and `make closing-checks` linked with no `CARGO_INCREMENTAL` override, measured 2026-11-22 (the log grep above).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; a builder's make targets stop failing to link.

**Found and left?** None. The stale unit's coming back once is the condition 451 T142's heal exists for, and it healed; it is not a defect left.

**Performance work?** No.


### T247 (T158's builder, 2026-11-22: a blob id for a `.py` file failed two plan tests, one task test and one claims test, so `scripts/gates/codeid.py` stayed)

`scripts/gates/codeid.py` was the last tracked `.py` file outside `specs/` (measured 2026-11-22, `git ls-files '*.py'` less the clone's uncommitted deletions: it alone). Its one rule the Rust did not have was a `.py` file's docstring-blind id (`ast.dump` of the tree with every bare string statement dropped); a `.rs` file's comment-free id was Rust already (`core`'s `rust_tokens`).

- **Approach**: a `.py` file's id is its blob id everywhere, and `codeid.py` is deleted (`ask:449-T158-codeid`: "move content_ids to the blob id ... restating the pinned tests ... fine under FR-002 as long as the gates still do their job").
  - `core` `codeid.rs`: `content_ids(files, cache)`, a `.rs` file by its comment-free tokens, kept by blob id, any other by its blob id; `gate_tree(root)` in place of `script()`.
  - `tree`: `delta.rs` (the `python` parameter, the scratch blob and `semantically_changed` gone; `semantic()` is `.rs` alone), `stamp.rs` (its self-test rows on `.rs`), `state.rs`, `exempt.rs` (`report`, `missing`, `ranges` gone: no caller, 0 entries, measured 2026-11-22 (a grep of `rust/` and `scripts/`, and `dev/coverage-exempt.json` read)).
  - `cohort.rs`: a pair is counter-only when every modified engine file is the same bytes; the `codeid.py --debug-free-equal` run gone. For a `.rs` file (any file but a `.py`) that mode compared raw bytes already, measured 2026-11-22 (`git show HEAD:scripts/gates/codeid.py`, its `debug_free_bytes` returning the data for a name not ending `.py`), so a `.rs` pair is judged as before.
  - `measure` `preflight.rs`: `same_python` and `raw_areas` gone; `unseen` holds the same bytes and the claims round's records.
  - `claims` `carry.rs`: `touches_engine` is any engine path in the delta, infallible (its `Result` and the stale `case_sensitive_file_extension_comparisons` expectation gone, clippy).
  - `plan` `engine_edit.rs`: `is_engine` alone, so a docstring or comment edit waits under a running review (the GM 2026-10-27's let-through had a `.py` subject alone, and none is left; a `.rs` comment edit always waited).
  - `task` `wording.rs`: `same_pairs` gone, a `.py` comment counted as a change.
  - `land`: `stage_seam` and `walk_py` (the `l7r/**/*.py` seam) gone, `scope_split` handed `&[]`; `claims_wait.rs`'s `ruffed` and `commit_gate_formatting` gone (ruff left with T158).
  - The binary `rust/gate/src/lib.rs`: `content-ids` answered in process, every `"python3"` argument gone; `arbiter` `bundle.rs` follows `cohort::cli`.
  - `core` `record/repo.rs`: `python`, the `python3 -c` seam, deleted with its test lines; no caller outside its tests, measured 2026-11-22 (a grep of `rust/` for `python(`).
  - The tests: the four pinning docstring-blindness restated (`a_docstring_edit_waits_as_a_code_change_does`, the task wording test `a_python_comment_changes_what_runs` red first on the old code, carry's `a_python_change_is_engine_code_as_any_engine_path_s_is`); `checks` `rust_tooling/tests.rs`'s real-tree reader re-pinned to `tests/hooks/test-make-only-hooks.sh` (its `*.rs` find); `land` `cheap/tests.rs` expects an empty seam; `measure` `preflight/tests.rs` loses the python stand-in.
  - The suites: `test-gate-write-hooks.sh` section 3 copies no `codeid.py`; a `.py` docstring and a `.rs` comment are refused, a claims-round record passes (26 passed); `test-engine-freeze-hooks.sh`'s docstring and comment edits wait (32 passed); `test-l7r-gate.1.sh`'s registry docstring owes `diagram` too and its comment case is on a `.rs` file, a `.py` docstring refused; `test-cohort-gate.sh`'s docs commit keeps the landing record and a `.py` docstring moves it (these two red at the first closing check, measured 2026-11-22 (`make closing-checks T=T247 F=449`), green alone after); comments in `test-l7r-gate.1-3.sh`, `test-sync-with-main.sh` and `l7r-gate.sh:155` restated.
  - The docs: the root `CLAUDE.md` route bullet, `docs/session-clones.md`'s route clause, `docs/efficiency-tooling.md`'s `ci verified-done` row, `rust/gate/CLAUDE.md`'s `codeid` row, `dev/rust-tooling.md` row 33, the engine-freeze guard's header; `scripts/` dropped from `plan`'s and `tree`'s `reads` (their tests read the real `codeid.py` alone).
  - The crates' tests: cohort 70, ci 32, measure 205, claims 157, plan 170, task 86, land 91, arbiter 34, the binary 8, all passed, measured 2026-11-22 (`make rust-test CRATE=<dir>` each).
  - The census: `git ls-files '*.py'` lists 62, all 62 deleted in the clone, so 0 are left, measured 2026-11-22 (`git ls-files '*.py'` against `git ls-files --deleted '*.py'`).
  - The engine keys all moved, measured 2026-11-22 (`l7r-gate delta key worktree|HEAD|origin/main` against `/tmp/t247/keys-before.txt`). `origin/main` is the same commit, `451de9cd61`, and holds 38 engine `.py` files: it moved by their ids alone, now blob ids. `HEAD` moved by those 38 and by 451 T141's seven commits, measured 2026-11-22 (`git log --oneline 451de9cd61..HEAD`). The worktree moved by this task's and its neighbors' `.rs` code edits. A tree with no `.py` file keys as before.
- **Decision: comment-blindness is not widened to the `.rs` callers.** The delta's engine test, `touches_engine`, `engine-edit` and the wording pairs treated any `.rs` change as a change before (measured 2026-11-22, the preflight and delta code at HEAD read, and `git show HEAD:<file>` of each caller: `claims/carry.rs`:70 returns `true` for any engine path not ending `.py`, `plan/engine_edit.rs`'s `semantic` takes an id only of bytes written as `edit.py`, and `task/wording.rs`'s pairs are `.py` files alone, its doc line 7), and keep doing so. The alternative was to wire `engine-edit` and the wording check to `rust_tokens`, so a `.rs` comment edit passes them. It costs a new approval, and it loosens two gates over doc comments that hold doctests. It is priced, and not built.
- **The GM-ruled pins restated**, each because its subject was a `.py` file's docstring-blind id and no `.py` file is left (`ask:449-T158-codeid`): the GM 2026-08-26 (a comment or docstring after the stamp is not different code: `test-l7r-gate.1.sh` now pins it on a `.rs` comment, which the stamp's key still strips, and a `.py` docstring refused); the GM 2026-08-28 (a comment-only edit to engine Python is not engine code for the route: the root `CLAUDE.md` and `docs/session-clones.md` restated, every engine path's edit counting); the GM 2026-10-18 (a docstring commit keeps the landing record: `test-cohort-gate.sh` keeps a docs commit's, a `.py` docstring moving it); the GM 2026-10-27 (a docstring edit passes a running review: `engine-edit`, its suite and `docs/guards.md`'s row restated).
- **What the deletion costs.** `.git/semantic-id-cache-2.json`'s `.py` entries are never read again, which is harmless. The `gate-green-*` stamps, the verification state's engine key, the cohort's keys and the work-budget review's kept counts move only for a tree holding `.py` blobs, and none does once T158's deletions are committed. That is accepted under FR-002 (the callers' job held, not their bytes).
- **No Rust starts Python** (`ask:449-T158-codeid` moved this exit here; the round arbiter's ruling `ask:449-T247-python-starts`, 2026-11-22, "continue": "A `python3 -c` or `-m` started from Rust is a Python start", read against SC-005, so T247 deletes every one, with no remainder). Each start, and what went with it:
  - (a) `make replay-owing` (feature 375 SC-001), whose OLD side ran a past commit's own Python by `python3 -c`: `rust/gate/crates/land/src/replay_owing.rs` and its tests deleted, its `pub mod`, its doc line in `land`'s `lib.rs`, its `l7r_gate_owed` dependency and comment in `land`'s `Cargo.toml`, the binary's `replay-owing` dispatch and `pub use`, `claims.rs`'s replay-only `current_at`, `owed_at` and `backfill_at` with `claims/tests.rs`'s `the_land_asks_in_process` trimmed, the Makefile target, `docs/make-targets.html` regenerated (`make docs`, 186 targets, measured 2026-11-22), and `rust/gate/CLAUDE.md`'s `land` row. `specs/375-enforced-wave-process/measurements.json`'s `sc001-replay` command is retired to `<retired: 449 T247 (ask:449-T247-python-starts): ...>`, its values kept as history, by the retire class of `ask:449-T118-retire-375-a1` and 449 T248's form.
  - (b) `research` `tools/memo.rs`'s `python3 -m` in-process arm of `check <name> -- <command>`: `facts_import`, `--facts`, `python()`, `in_process()` and `RAISED` deleted with `tools.rs` reply's `RAISED` branch; `general` is `memo.run(...)`.
  - (c) the guard's `suite_tools/trace.rs` `python_version` (`python3 -c` for `sys.version` in a hook suite's trace key) and the key's `py` field, with its tests.
  - (d) found by this task's census after the ruling, the same class: the make-only guard's `landing_lint` (`python3 -m ruff` on the `.py` files a `make land-tooling` or `make arbiter-fix-done` names, feature 385 T91), with `LANDING`, `LINT_LIMIT`, `Ctx.python` and the `ask_within` import, and its tests (`a_landing_is_linted_before_it_runs`, the `fake` interpreter, the lint rows of `each_refusal_names_what_to_run` and `the_makefile_is_the_trees_the_command_runs_in`). The ask's census missed it because the interpreter traveled through a `Ctx` field, not a literal at the start. Its subject, a `.py` file in a landing, is gone with T158 (0 tracked `.py` files outside `specs/`).
  - (e) the review's round 1 found the same lint in shell, the same class on (d)'s ground: `scripts/land-tooling.sh`'s 385 T91 lint first in the clone (`python3 -m ruff --version`, then `python3 -m ruff check`) deleted, and its 385 T52 `ruff check` of the landed `.py` files in the worktree, the lint step kept as the `LAND_TOOLING_LINT` seam alone (`true` by default), the failure line naming ruff gone; `tests/hooks/test-land-tooling.sh` restated (1c's ruff wording and its T91 case, now "a `.py` file is not linted by default", and 1e, the ruff scope, deleted; 50 passed, measured 2026-11-22); and with its one caller gone, the gate's `ruff-toml` (`core` `logs.rs` `ruff_toml` and `ruff_cli`, their test, the binary's dispatch, `rust/gate/CLAUDE.md`'s `core` row). ruff is installed here (`python3 -m ruff --version` answers 0.15.22, measured 2026-11-22), so the shell lint was live: every landing of a `.py` file started Python.
  - core `record::repo::python`, the `python3 -c` seam, deleted: no caller (above).
  - The census, measured 2026-11-22 after (a)-(d): `git grep -nwE 'python3?' -- 'rust/**.rs'`, less test files (`tests.rs`, `tests/`), `testkit` and `case_tables`, and `//` lines, returns 47 lines, none a start: the guard's patterns and word lists of commands it recognizes (`shared/src/make.rs` `PY`, `shape.rs`, `tree.rs` and `tree/python.rs`, `tree/quoted.rs`, `batching_hooks`, `blocked_fetch_hooks`, `claims_file_hooks`, `make_only_hooks`' `ENTRY_MODULE` pattern and its rewrite note, `phase_source_hooks` and its `search.rs`, `search/filter.rs`), a refusal's text (`gm_tree_hooks`), local names for a `.py` path or a Python-shaped pattern (`claims/ports/flow.rs`, `research/pyre.rs`, `tree/checks.rs`, `trials/.../code.rs`, the binary's `content_ids` test), a fenced code block's language (`bundle/.../depiction.rs`), `pair_hooks`' `python()`, which both callers hand `"bash"` and `l7r-gate.sh`, `memo.rs`'s `preset` argv, which is the memo key's text (the run is `check(root)` in process), and memo's generic `command()` runner, which runs the `argv[0]` its recipe hands it, none of them `python3` (the ruling's (b): no Makefile or script recipe passes a `python3 -m` command, measured by grep), and `rust/parked`'s `cfg(feature = "python")`, a crate with no `Cargo.toml`, never built. The first form, `git grep -nE 'Command::new|"python3?"' -- 'rust/**.rs'` less tests and testkit, names no Python program either. The browser testkit's fake Chromium (`#!/usr/bin/env -S python3`) is a test fake, outside production.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a `.py` file's id its blob id | the four pinned tests failed under a blob id at T158 (its record), and the task wording test red first on the old code | n/a (tooling, no map) | none | n/a |

### T247 Approach (checklist part A)

1. **The goal, in the world.** No Python file is left outside `specs/`, and every gate does its job without one.
2. **The constraints.** FR-001 and SC-005 (an empty census), FR-002 (a caller's job held, not its bytes), `ask:449-T158-codeid`.
3. **Where each comes from.** O: T158's failing tests (the task line). O: the census and the grep of `codeid` above. G: none beyond the ruling.
4. **Do they describe the world here?** Yes. The census is 0, measured 2026-11-22 (above).
5. **The order.** After T158 and T249's claims crate edits. Before the feature's close (SC-005).
6. **The exits.** Green: the crates' tests and `make closing-checks` pass, the census is empty, and no Rust starts Python (the census of the starts above, `ask:449-T247-python-starts`). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The nine crates' tests pass (above), and the four restated suites pass, measured 2026-11-22 (`bash tests/hooks/<suite>.sh`). `git ls-files '*.py'` is empty at the commit. No Rust starts Python: the two greps of the starts above name none, measured 2026-11-22, after (a)-(d); `land`, `claims`, the binary `rust/gate` and `rust/guard` pass their tests, lint, coverage and format check, measured 2026-11-22 (`make rust-test CRATE=<dir>`, `l7r-gate.sh rust lint|cover|format --check --crate <dir>`), and `tests/hooks/test-make-only-hooks.sh` passes, 144 (its three landing-lint cases restated: a landing naming a `.py` file is not refused).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map changes. A docstring-only edit now owes the gate and waits under a review, where it passed before.

**Found and left?**
- The browser testkit's fake Chromium (`rust/browser/src/testkit.rs`, `#!/usr/bin/env -S python3`) is started by the browser crate's own tests, which `make done` runs: not a production start, so outside this exit (the ruling's "production `rust/`"), but a Python start under `make done` at SC-005's close. Not fixed here: it is the browser crate's test fake, outside this task's files and its ruling. Filed as T273; lands before T158, the deletion close.
- `.specify/memory/constitution.md` principle X names `scripts/gates/codeid.py` "until 449 T247 deletes it": T251's uncommitted edit, which says what this task does. Not a defect: the passage is true once this lands.
- `checks`' `every_pointer_in_the_repository_resolves_to_a_fragment` is red on two pointers in other builders' uncommitted text: T249's tasks.md line (`0027-...drawing.html`, an elided file name) and feature 451's plan.md T49 section (`research/contents.json#trades-and-services`'s built page, a quoted command). Not fixed here: both lines are mid-edit in their builders' files, outside this task's. Filed as T249 (its own line, its builder told); lands before T247.

**Performance work?** No.

### T248 (T158's MODE 4 review, 2026-11-22: the .py files under specs/ would fail SC-005's empty-Python census at the feature's close, and no task removes them)

- **Approach**: measured, then ruled by the accepted spec's words (spec-fidelity MODE 4, round 1, 2026-11-22: the record settles it, so no question goes to the GM). The delta is the deletions, one port and the record rewrites below; this builder does not stage, commit or delete under `specs/` (the session's ground rule for its builders), so the execution is the session's, in one landing.
  - **What SC-005 counts, word for word.** SC-005: "When the feature closes, both censuses (FR-001) return nothing, `m:recorded-python-commands`' command returns none, and `make done` and `make figures` run with no Python interpreter. Its one entry here, this feature's own `m:python-start` ... is retired in the closing commit ... the only exemption." FR-001: "Every Python file the repository tracks MUST be replaced by Rust ... THE CENSUS is `git ls-files '*.py'`". The spec review's round 1 added `specs/` to the census on purpose ("CHANGES REQUIRED - the census missed specs/ and pool/"). So SC-005 counts the repository's `.py`, not only the live code's. That is the brief's second branch.
  - **The files.** measured 2026-11-22 (`git ls-files '*.py'`, each checked on disk): 62 tracked at HEAD. 45 of them are deleted in the working tree by the open phase-4 work, which leaves 17. One is `scripts/gates/codeid.py`, which is T247's. The other 16 stand under `specs/449-rust-codebase/derivations/`, measured 2026-11-22 (`git ls-files '*.py'`): 12 in `T198-placer-scripts/` (`chunks`, `formula`, `formula3`, `hybrid`, `inventory`, `params`, `pooled3`, `sim2`, `sim3`, `simulate`, `variants`, `variants2`) and 4 in `T208-compound-scripts/` (`count`, `factors`, `survey`, `tables`), 1,484 lines in all (`wc -l`). They were added on 2026-11-19 by commits 8d2ca5bcb4 (T198) and d968a75fd6 (T208). No tracked `.py` stands anywhere else outside the live code.
  - **What reads each.** measured 2026-11-22 (`git grep` of each directory and each basename over the Makefile, `*.mk`, `rust/`, `scripts/` and every `measurements*.json`; `grep` of the scripts' own imports): nothing runs them. Only the scripts import one another: `inventory` and `simulate` are the base, and `hybrid`, `sim2`, `sim3` and the rest import those. Three things point to them. `plan-done.md:5034` points to T198's directory ("its scripts beside it in `derivations/T198-placer-scripts/`"), and `plan-done.md:5300` points to T208's. `derivations/T198-placer.md` takes every figure from "my own small script". `derivations/T208-compound.md` names `/tmp/t208/count.py`, `factors.py` and `tables.py`, the copies outside the repository. Those figures are the SOUND budgets' working. SC-005's `make figures` re-runs none of them, because no measurement entry names them.
  - **Is there a coded census check?** measured 2026-11-22 (`git grep` of `SC-005`, `census` and `ls-files.*\.py` over `rust/`, `scripts/`, the Makefile and `tasks.md`): no gate check counts the first census. It is the recorded measurement `m:python-census` in `specs/449-rust-codebase/measurements.json` (`git ls-files '*.py' | wc -l` ...), which counts every tracked `.py`, `specs/` included, and that matches FR-001's words. `make inline-census` (`scripts/measure/inline-census.sh`) counts only `scripts/hooks/*.sh` and `tests/hooks/*.sh`, which is phase 1's share, as its help line says. So no check counts the wrong thing, and nothing needs fixing red first.
  - **The same conflict in SC-005's other clauses.** measured 2026-11-22. The second census (`git grep -nE "python3 (-c|-[[:space:]]|-$|<<)" -- Makefile '*.mk' '*.sh'`) returns 73 sites, measured 2026-11-22 (that command run). Nine of them stand in six shell scripts of past features under `specs/`: `131-split-diagram-repo/contracts/split.sh` (2), `255-cheaper-checks-by-tooling/measure/probe.sh` (1), `256-defined-subagents-without-claude-md/measure/dispatch_seeded.sh` (1) and `first_turn.sh` (2), `386-landing-cohort/fresh_cost.sh` (2), and `427-call-volume-refactors/research/us5-test.sh` (1). Of these, only `fresh_cost.sh` has a runner, `m:fresh-block-cost` in `specs/386-landing-cohort/measurements.json`, whose command is not retired. FR-001 puts "the shell scripts under `specs/`" in phase 3, and no open task holds them. `m:recorded-python-commands`' command returns 12 entries in six features' `measurements.json` (306: 2, 308: 1, 374: 2, 385: 1, 444: 4, 449: 2). One of 449's two is `m:python-start`, the exemption. No open task holds the other 11. These are the same question as the 16 files, measured 2026-11-22 (the two commands above): each is a file under `specs/` that SC-005 would count at the close.
  - **The ruling, by group (measured 2026-11-22, the censuses above).** FR-001: "every file it returns is in a phase", and a file under `specs/` has one place, phase 3 if something still runs it, deleted and not ported if nothing does, under the GM's 2026-11-09 words: "I don't think we need to port the past feature harnesses if those are not still used." The parenthetical's naming of a past feature's harness, measurement or prototype describes those files and exempts none; a script computing a derivation's figures is a measurement in that sense, and SC-005's one exemption is `m:python-start`. So: (a) the 16 derivation scripts, which nothing runs, are deleted, not ported, git history keeping them (8d2ca5bcb4, d968a75fd6), with a note at `plan-done.md:5034` and `:5300` naming the commit that deleted them. Precedents, observed 2026-11-22, method: `git log --diff-filter=D -- 'specs/*.py'`: c32fb56b86, 656a119fe3 (T89), cc3f12439c (T130), c9b5e2414b (T210). (b) Of the 6 shell scripts, the 5 that nothing runs are deleted; `specs/386-landing-cohort/fresh_cost.sh`, which `m:fresh-block-cost` still runs, is ported (its two inline Python sites, a subtraction and a summary, become shell arithmetic or an `l7r-gate measure` command), so the entry still re-runs. (c) The 11 recorded commands, each by the retire class's test in FR-001 (a command `make figures` runs that fails today, or that invokes deleted code), measured 2026-11-22 (each file looked up with `git ls-files`): 8 fail today, because they run a `.py` the repository never tracked (`legs.py` x2 in 306, `stages.py` in 308, `<scratchpad>/measure_bank.py` in 385, `skew.py` in 444) or are prose (444's three `python3:` entries), so they are retired to `<retired: ...>` with their values kept; 3 are inline and run today (374's `batch3-open-rows` and `batch4-open-rows`, reading `specs/328-match-the-research/ranking.json`, which exists, and 449's `registered-guards`), so they are rewritten to an equivalent command through make, per FR-001, and re-run. Executed 2026-11-22 as T139's route (`l7r-gate measure spec <feature> <name>`, the form 238, 239, 242, 261, 430 and 432 already take): `scripts/gates/l7r-gate.sh measure spec 374 open-rows` and `... 449 registered-guards`, in `rust/gate/crates/measure/src/measure/spec/counts.rs`, print-only as the one-liners were. Re-run 2026-11-22 (each command, and the Python one-liner before it): "149 open, 96 E3 DRIFTED" and 0, each equal to the Python's today; the recorded 183/132, 179/122 and 44 stand as history, the ranking having moved since and the 44 `-hooks.sh` guards now one Rust dispatcher. `fresh_cost.sh`'s two sites became `awk`: the recorded triples give 57.2, 58.1 and 56.7, its recorded value, measured 2026-11-22 (its median fed the triples of `m:fresh-block-cost`'s method).
  - **Moving instead of deleting** (the "moved" of T248's line): it costs the same, since SC-005 counts tracked files, so a move leaves the repository or it counts; it is not taken.
  - **Restating SC-005 to exclude `specs/`**: not taken. It would reverse the spec review's round 1, which added `specs/` to the census, and the record already rules the files by FR-001's words.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| delete the 16 scripts and 5 shell scripts, port `fresh_cost.sh`, retire 8 commands and rewrite 3, note the two pointers | the two rewritten counts held by `counts/tests.rs` (`the_open_rows_are_those_no_wave_took_and_not_deferred`, `the_registered_guards_are_the_distinct_hook_files_named`); the rest no engine code | `git ls-files '*.py'` less `codeid.py` (T247's) returns nothing | none | a rewritten command that will not run is retired by the class's test, never kept failing |

### T248 Approach (checklist part A)

1. **The goal, in the world.** At the feature's close, SC-005's censuses return nothing under `specs/`: the record keeps its words and values, and git history keeps the deleted scripts.
2. **The constraints.** SC-005; FR-001 (THE CENSUS, the SECOND CENSUS, the `specs/` parenthetical, the recorded-measurement rewrite rule); the root CLAUDE.md's note that the specs are history and keep their words; the brief's rule that neither deletion nor a restatement is this task's to choose.
3. **Where each comes from.** G: the GM's 2026-11-09 words in FR-001 ("I don't think we need to port the past feature harnesses if those are not still used."). R: spec.md SC-005 and FR-001, and the spec review's rounds 1 and 2. O: the measurements above, dated 2026-11-22.
4. **Do they describe the world here?** Yes, measured 2026-11-22 (`git ls-files '*.py'`, the second census's `git grep`, `m:recorded-python-commands`' command run, and each file's runners grepped): 16 `.py` files, 9 inline sites in 6 `.sh` files, and 11 recorded commands under `specs/`, none held by a task.
5. **The order.** Before 449 closes. After T247, which removes `codeid.py`, the 16 files are the census's only remainder, measured 2026-11-22 (`git ls-files '*.py'`, each checked on disk).
6. **The exits.** Green: after the landing, the first census returns only `codeid.py` until T247 lands, the second census returns no site under `specs/`, and `m:recorded-python-commands`' command returns only `m:python-start`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one grep a question, each answering on the first probe.
8. **The budget.** One landing.
9. **Done, measured.** `git ls-files 'specs/*.py'` returns nothing; `git grep -nE "python3 (-c|-[[:space:]]|-$|<<)" -- 'specs/**.sh'` returns nothing; `m:recorded-python-commands`' command returns 1 entry, measured at the landing (those commands run), and `make figures` re-runs `m:fresh-block-cost` and the 3 rewritten entries.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a
12. **Before any fix.** A defect is a wrong outcome (constitution XIV): SC-005 would fail at the close. No map changes; the fix is FR-001's own route for files under `specs/`.

**Found and left?** none outside this task. The second census's 9 sites under `specs/` and the 11 recorded commands (measured 2026-11-22, the commands above) are the same SC-005 failure and are this task's, in (b) and (c) above.

**Performance work?** no


### T249 (449 T241 found it, 2026-11-22: a page a claim cites only in its account was in no claim's research fingerprint)

- **Approach**: the claims index (`rust/gate/crates/claims/src/claims/index.rs`) took a claim's research fingerprint (`research_fp`, in `rows_of`), its standing blocks (`standing`) and its unread check (`research_why`) from its backing's pointers alone. So an edit of a page the claim cites in its account, such as 0027 for `polder.rs::off_the_dike`, owed no claim. All three now read T241's `cited_pages` (`bundle.rs`, made `pub(crate)`, called, not copied): the backing's pages, then each page the claim's line names, once each, in order. The fingerprint of a claim with no account-cited page is unchanged, because its pages come in the same order. The other readers of the same set read it too, so they agree with the index: `report.rs`'s refingerprint test (`research_fp` at the merge base) and its coverage check (an account-cited page naming no question file is reported); `triage.rs`'s triage bundle and its mechanical clear (`clear_page_moves`), whose rows' `pages` would otherwise lack the page and stay owed; `commands.rs`'s pages backfill; and `impl_check.rs`'s question-to-claims map.
  - Red first: `index/tests.rs` `an_edit_of_a_page_a_claim_cites_only_in_its_account_owes_the_claim` builds `off_the_dike`'s claim, backed by one page and citing `0027-polder-dikes.drawing.html` in its account. It records the claim checked, edits 0027, and asks `owed`. With `rows_of` reading the pointers alone it fails (`left: []`, `right: ["rests changed"]`), measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/claims`, the one line reverted). It passes with the fix, 157 passed, measured 2026-11-22 (the same). Lint and cover are clean on the claims crate, measured 2026-11-22 (`l7r-gate.sh rust lint|cover --crate rust/gate/crates/claims`).
  - The real tree: before the fix 15 claims were owed, all other builders' (T197's and the engine's page and code edits), measured 2026-11-22 (`make claims-owed` with the one `rows_of` line reverted). After it, 138 more, measured 2026-11-22 (`make claims-owed`, diffed against that list): 119 `research changed` in 91 units over 36 files, and 19 `triage`. Of the 63 units T241 measured (`/tmp/t241/gains.txt`), 62 are among these 91, and the 63rd, `waterward.rs::face`, is owed a `code triage` now by another builder's edit, measured 2026-11-22 (the two lists compared). The other 29 units gained no page in their bundles, because a sibling claim already backed it, but their own claim's fingerprint grew: for example `driver/plan.rs::KNOBS#the farm water`, a bare `GUESS` naming 0031 in its account, had the empty research fingerprint, measured 2026-11-22 (its index row read).
  - The 19 `triage` claims cleared mechanically: none of the blocks they rest on moved, only the page set grew, measured 2026-11-22 (`make claims-triage`, each row's note then reading feature 432's mechanical clear). That run also cleared `polder.rs::landward`, an owed claim from before the fix, by the same rule. Its other 4 claims (`waterward.rs::face` and `fringe`, `code triage`) are another builder's code edit in progress, not T249's, so they were not dispatched.
  - The re-check: the 119 claims, bundled one file at a time with `make claims-bundle UNITS=` on T249's keys alone, so no other builder's owed claim is swept in (36 bundles, `/tmp/l7r-check/t249-00` to `t249-35`). Each is checked by impl-drift and recorded with `make claims-checked`. `waterward.rs::face#strip at the dike's outer face` is left to the builder whose code edit owes it too.
  - The verdicts, all 119 recorded 2026-11-22 (`make claims-checked`, one reply a bundle): 112 IN-STEP, 5 DRIFTED, 1 MISLABELED, 1 CANNOT-TELL, and 2 UNCLAIMED decisions. Each finding was handled as the claims round's rules say (constitution XIV: a claim the code does not literally match, where the behavior is fine, is restated):
    - `fix: claim` (3): `grounds.rs::well_gear` (the audit leaves the roof's dash unchecked), `driver.rs::BROOK_TAP_RUN` (0054 is silent on a brook's run; it never says a brook wanders) and `field/polder.rs::polder#the feeder` (0019 puts no channel outside the dike; the feeder is the wild water's reach to the inlet) were restated in their `Research:` lines, then re-checked IN-STEP.
    - MISLABELED (1): `grounds.rs::INNERMOST_FT` was relabeled from CONVENTION to `GUESS` on 0220's drawing page, which calls the 12 ft a guess, then re-checked IN-STEP.
    - `fix: code` (2): the magistrate's manor's garrison-emphasis armory and its outer-court granary in `docs/building-programs.md` are known drifts held by 417 T33, which is open and names the armory at an ordinary seat and the granary's court; T265 lands them before T158 (under Found and left, below).
    - CANNOT-TELL (1): `driver/polder.rs::draw_sluices#the board's place` asked whether the ring canal or the outfall's drain meets the channel at the sluice point. Measured on Kuwabata 2026-11-22 (`pool/hamlets/kuwabata/kuwabata.driver.svg`, and `field/polder.rs`'s `ring(RING_FT.0)` and sluice points): neither does. The inlet sluice is at (2328, 2328), where the feeder ends, and the ring canal's corner is at (2334, 2334), 8.5 ft inside it, measured 2026-11-22 (Kuwabata's driver SVG). The outfall sluice is at (2328, 3422), where the outfall's drain starts, and the ring's drain trunk ends at (2334, 3416), also 8.5 ft inside, measured 2026-11-22 (Kuwabata's driver SVG). With that, the re-check found the claim MISLABELED, because the board on the point stands 8.5 ft down the blocked channel from the junction (measured 2026-11-22 (Kuwabata's driver SVG)), which is 0179's own rule. Its `Research:` line was relabeled to cite 0179 with the measurement, then re-checked IN-STEP (`t249-r4`).
    - UNCLAIMED (2): `docs/buildings.md`'s servants' street range, about 15 ft deep, and `sink/pond.rs::lay`'s ring of reeds round the pond each got a claim (`servants' range depth`, a GUESS on 0115's drawing page; `the pond's ring of reeds`, on 0074's drawing page). Both were checked IN-STEP.
    - Outside the change: 0091 against 0115 on where a household's servants live (`found.jsonl` row 139) is filed as T260. Sawada's houses, not backed to the wind against 0031's drawing-page block 61 (row 141), are filed as T261. Bundle 24's merged dike-pond parcel (row 140, 160 by 342 ft, observed 2026-11-22, method: bundle t249-24's checker reading `polder.rs::plots`, against 0022's "about 160 by 320 ft") was read as no defect by its checker, and that row is left open: `make found-close` settles a row only once it "no longer holds".
    - Dropped rests: 00, 06, 12, 15, 17, 18, 29 and 35 each had a verdict resting on blocks of a page its claim does not cite. In each case that was a sibling claim's page, or a context line's page, in the same bundle. It was not a T249 defect: `claims-checked` reads the claim's pages from the bundle's own `units.json`, which `bundle.rs` fills from `cited_pages`, so the two sets are one. The verdicts were recorded and only the foreign rests were dropped. Those 9 claims were re-checked against their own pages alone (`/tmp/l7r-check/t249-r1` and `t249-r2`), and all came back IN-STEP but `draw_sluices`, above.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the cited pages in the index | the test red with `rows_of` reading the pointers, measured 2026-11-22 (`make rust-test`) | n/a (tooling, no map) | none | n/a |
| the re-check | n/a: index rows, through `make claims-checked` | `dev/claims-index.json` and its page store, through the tools | none | n/a |

### T249 Approach (checklist part A)

1. **The goal, in the world.** An edit of any page a claim cites moves that claim owed, so no figure keeps a verdict judged without its page.
2. **The constraints.** The grammar is unchanged. T241's `cited_pages` is the one definition of a claim's pages. T158's and T241's uncommitted edits in the crate are kept. Other builders' owed claims are theirs.
3. **Where each comes from.** O: T241's replay (the task line). O: the owed lists above.
4. **Do they describe the world here?** Yes. Measured 2026-11-22 on this clone's tree (`make claims-owed`, before and after).
5. **The order.** Right after T158, before T247 (the task line).
6. **The exits.** Green: the red test passes, and every claim owed only by the fix is re-checked and recorded. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The claims crate is green, 157 passed, measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/claims`). `make claims-owed` minus the 15 claims owed before the fix is empty, and `make claims-report` lists no open T249 claim.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A check passing unchecked: an edit of an account-cited page re-checked nothing. Nothing on a map changes.

**Found and left?**
- 0091's block 127 puts a household's servants in the shady rear, where 0115 and the sheets put them on the street edge: a reader of 0091 expects a rear servants' range no sheet draws. Not fixed here: a record change, owed a page session. Filed as T260; lands before T158.
- 0031's drawing page says every hamlet keeps its back to the wind, and Sawada's houses, seated by `seat.rs::seat`'s fallback, do not. Not fixed here: a record change, owed a page session. Filed as T261; lands before T158.
- The magistrate's manor in `docs/building-programs.md` draws no armory at a quiet county's seat, where Kaibara and Pingyao both kept one, and it draws the granary in the front office court, where Pingyao kept it behind the offices (bundle t249-00's two `fix: code` drifts, recorded 2026-11-22). Not fixed here: they are the manor's program, which 417 T33 already rewrites (it names the armory at an ordinary seat and the granary's court), and the file holds T197's uncommitted edits. Filed as T265 (with 417 T33); lands before T158.
- A polder's feeder and outfall drain stop 8.5 ft short of the ring canal they join (Kuwabata, measured 2026-11-22): the water may read as broken at each sluice. Not fixed here: it needs a fit-zoom look and a redraw, and the polder's files hold T240's uncommitted edits. Filed as T263; lands before T158.
- `building-programs.md`'s `dwelling band 34-60 by 18-38 ft` is a bare GUESS naming 0221, which `make claims-owed`'s label lint refuses. Not fixed here: T197's page session holds the file's uncommitted edits. Filed as T264; lands before T158.

**Performance work?** No.


### T250 (T235's count, 2026-11-22: T240's bank bands priced by no derivation, the push ratchet refusing the stage at about 5.6x, measured 2026-11-22 (`make work-budget`))

- **Approach**: the bands' work measured where it goes, made cheaper red first with the drawing held, then priced in the stage's derivation. Where it went, measured 2026-11-22 (`hamlet --budget polder` built with the counters, the mean of seeds 4/25/39/47): `test@bank` counted 9,877 at 10 households and 13,029 at 20, against 213 and 217 band points written (`write@bank`). The bands sampled each bank of the feeder and the outfall's drain every 2 ft along its whole course, and asked every sample of every ring of reeds (the strip pieces and the wild pond's fringe, 5 rings), measured 2026-11-22 (the code read, and the per-key run above). The drain runs 1,966 to 2,745 ft to the canvas edge, so a roll took 2,116 samples at 10 and 2,700 to 2,894 at 20, measured 2026-11-22 (a temporary test reading each roll's courses, removed). Most lay past every ring. Each ring test also walked the ring's edges uncounted (rubric S5). The cheaper band in `rust/phases/src/driver/polder.rs`: each bank reach is clipped once to each ring's box (`clip`, Liang-Barsky). A ring whose box the reach meets is walked once for the reach's start's side and its crossings (`crossings`). Each sample in some box is then answered by a cursor along the sorted crossings and by the pond's rim. A sample in no box is out of the reeds and never asked. The samples are the same 2 ft lattice, `t = k/n` on each reach, so the band points are the plain search's, measured 2026-11-22 (`the_clipped_bank_search_equals_the_plain_one`). Before and after, measured 2026-11-22 (`hamlet --budget polder`, counters, the four seeds): `test@bank` went from 9,877 and 13,029 (the ring edges uncounted) to 1,106 and 1,176 (every edge counted). The stage went from 13,449 and 17,937 to 4,677 and 6,084, measured 2026-11-22 (`make work-budget`). Red first: `the_bank_bands_search_only_the_reeds` (counting build) requires at most ten tests per band point on Kuwabata and the eight budget rolls. It failed at 9,864 to 13,748 tests for 207 to 219 points, measured 2026-11-22 (`make counters-inert`, before the change), and passes after it. The drawing is held by `the_bank_bands_hold_their_points`, each roll's bands, points and their weighted sum pinned from T240's code. It is also held by `the_clipped_bank_search_equals_the_plain_one`: Kuwabata and six grid polders at falls of 0, 30, 135, 210, 255 and 300 degrees, each band set equal to the plain search's and none empty. The map: `make map MAP=pool/hamlets/kuwabata` REGENERATED. Its drawn reed-bank paths are 32 and 32 ft on the feeder and 28 and 312 ft on the drain, measured 2026-11-22 (the SVG's paths read): T240's figures. The budget: the derivation (`specs/444-work-budget-program/phases/waterward_polder.derivation.md`) was re-derived in place. It names the bands under `## Work the first derivation missed`, from their input sizes measured 2026-11-22 (a temporary test reading each roll's channels and rings of reeds, no operation count read): 8 bank reaches against 5 rings, 13 pairs meeting, 604 ft of bank in some box, and 213 and 217 band points. It comes to 3,549 at 10 and 4,525 at 20, exponent 0.35. The work-budget agent judged it blind in MODE BUDGET: SOUND (`waterward_polder.verdict-7.txt`). That is 1.54x and 1.41x the first figure, under twice, so no second SOUND is owed, measured 2026-11-22 (verdict-7's arithmetic against `dev/work-budget.json`). The raise did not go in. `make budget-set ... RAISE=1` refuses: "`waterward.polder` is accepted - RAISE=1 raises a budgeted stage, before its acceptance (feature 444 FR-022)". T235 re-accepted the stage at 3,929 and 5,501, measured 2026-11-22 (`dev/work-budget.json`'s `accepted`, read before the raise). A change to an accepted stage is `make budget-change`, which needs the GM's own words, and none in the record name this stage. The figures it would set: `make budget-change PHASE=waterward.polder TO=1 ITEMS_AT_10=3549 ITEMS_AT_20=4525 EXPONENT=0.35 DERIVATION=specs/444-work-budget-program/phases/waterward_polder.derivation.md VERDICT=specs/444-work-budget-program/phases/waterward_polder.verdict-7.txt WORDS="<the GM's words>"`. Neither the Makefile's `budget-change` line nor the tool's `change` takes the figure at 10 households (`budget_change.rs`'s `ITEM_FLAGS`: `change` takes 20, 40 and 80), so even the GM's words cannot set 3,549 at 10 today, observed 2026-11-22, method: the Makefile line and `ITEM_FLAGS` read. Then a MODE AUDIT and `make budget-accept`. Today's count is 1.32x and 1.34x the re-derived figure, measured 2026-11-22 (`make work-budget`). THE RAISE, ON THE ROUND ARBITER'S RULING (`ask:449-T250-raise-accepted`, continue, route (a)): its tooling fix, this task's, lets `make budget-set RAISE=1` take `ARBITER=<trigger>` naming a continue or accept ruling on the same stage in any feature's `arbiter.jsonl`, the stage's acceptance and audit then dropped as LOWER=1 drops them. That reach is the ruling's own `tooling_fix` words: "let RAISE=1 take ARBITER=<trigger> naming a continue or accept ruling in arbiter.jsonl on that same stage, then drop the stage's acceptance and audit as LOWER=1 does (status back to budgeted), with a test that the bare refusal stands without the ruling and that a ruling on another stage does not open it". A ruling opens one raise: a trigger already in the stage's `raised_on` opens nothing (its words: "bound to this stage and these figures", "never a second raise on this ruling") (`raise_opened_by` and `raise_ready`'s `opened` in the `trials` crate's `budget_change/rules.rs` and `rules/shared.rs`). Red first, measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/trials`, `/tmp/t250-fix-red.log`, the opener forced off): `an_arbiters_ruling_opens_an_accepted_stage_to_a_raise` failed on the bare refusal; it passes with the fix, 136 of 136 (`/tmp/t250-once-green.log`), and pins that the bare refusal stands without the ruling, that a ruling on another stage, or a process-fault ruling, opens nothing, and that the same ruling opens no second raise once the stage is accepted again. The stage was then raised: `waterward.polder` budgeted at 3,549 at 10 and 4,525 at 20, exponent 0.35, `raised_on` the ruling, `first` 2,310 and 3,206, measured 2026-11-22 (`dev/work-budget.json` read after `make budget-set ... RAISE=1 ARBITER=ask:449-T250-raise-accepted`). Its MODE AUDIT on this clone's tree, the run `20261122T085144Z-rust-bdb111b827` (`make work-budget WRITE=1`), reads OVER (`waterward_polder.audit-4.txt`): 4,677 at 10 is 2.02x the first figure, past the twice-first cap a raise on one SOUND holds, and 6,084 at 20 is 1.90x, measured 2026-11-22 (the audit's arithmetic on that run). `make budget-accept` refuses it, so the stage stands budgeted, not accepted. The audit names a waste worth more than the 57-operation excess: `waterward::fringe` calls `face` once per flank and each call files every dike corner through `nearest` again (`2 * n`, n 120 at 10, measured 2026-11-22 (the run's `test@fringe`)), though the nearest side does not depend on the flank, so filing once saves 120 to 240, measured 2026-11-22 (audit-4's reading of `test@fringe`). By the ruling, a failing audit is an optimization or a new ask, never a second raise. An earlier round on the same day read UNCOUNTED because the bundle took the newest run file, 2026-11-20's, which a plain `make work-budget` does not replace; that round is not saved as an audit. THE OPTIMIZATION AFTER AUDIT-4 (the ruling's route: optimize, never a second raise): the dike's corners are filed once for all the flanks. `waterward::file` files each corner of the dike ring to the side of the box it stands nearest, a test a corner, and buckets each side's corners in the ring's order (`Filed`); `fringe` files once and every flank's `face` takes the one filing, its own corners read off their side's bucket and its ends' neighbors asked by their filed side, so `face` no longer files and walks the whole ring per flank (`2 * n` each). The faces it writes are the same corners in the same order, so the strips are unchanged. Red first, measured 2026-11-22 (`l7r-gate.sh rust test-counters --crate rust/phases`, `/tmp/t250b/red-kept.log`, before the change): `each_dike_corner_is_filed_once_for_all_the_flanks` adds 60 corners on the head's side, a side no flank faces, and requires `test@face` to grow by 60; it grew by 240, four tests a corner over the west and south flanks, and passes after the change. The drawing is held by `the_waterside_strips_hold_their_points` (`polder/tests.rs`): each roll's flanks, strips, points and their weighted sum on Kuwabata, the eight budget rolls and the six grid polders off the axes, pinned from the code before the change, measured 2026-11-22 (`make rust-test CRATE=rust/phases`, the pin captured red-empty then filled), green after it. `test@face` on seed 4 at 10 went from 3,036 to 2,676, and the stage from 4,677 and 6,084 to 4,317 and 5,550, measured 2026-11-22 (`make work-budget WRITE=1`, the run `20261122T091149Z-rust-bdb111b827`). Audit-4's S5 notes counted in the same pass, in `bank_bands`: each ring's box fold a test a corner; the reach's samples, which were gathered into a list, sorted and deduplicated uncounted, are now the met rings' spans put in order by their starts (a comparison each) and merged in one counted walk, the same samples in the same order; and `crossings`' sort a comparison each. The bands are held by `the_bank_bands_hold_their_points` and `the_clipped_bank_search_equals_the_plain_one`, green after it, measured 2026-11-22 (`make rust-test CRATE=rust/phases` and the counting build). With them the stage counts 4,439 at 10 and 5,701 at 20, 1.92x and 1.78x the first 2,310 and 3,206, under twice, measured 2026-11-22 (`make work-budget WRITE=1`, the run `20261122T091359Z-rust-bdb111b827`). `make map MAP=pool/hamlets/kuwabata` REGENERATED, NOT COMPARED (the mirror's engine is not HEAD's), measured 2026-11-22; the drawing does not move, its strips and its bands pinned equal on Kuwabata by the two pin tests above. The span merge then moved into its own `merged` (clippy's 100-line limit on `bank_bands`), its count unchanged, pinned by `the_met_spans_merge_into_runs_each_sample_once`; the stage re-measured at the same 4,439 and 5,701, measured 2026-11-22 (`make work-budget WRITE=1`, the run `20261122T092024Z-rust-bdb111b827`). Its MODE AUDIT, the work-budget agent on `make work-budget-bundle MODE=audit PHASE=waterward.polder` on this clone's tree (the run `20261122T091359Z-rust-bdb111b827`), reads LEEWAY (`waterward_polder.audit-5.txt`): 1.25x and 1.26x the raised 3,549 and 4,525, under twice the first, the worst roll at 10 (4,452) 168 under the 4,620 cap, the excess in `test@face`'s cuts at each channel bed, which the contract owes, and every loop over a growing set counted, measured 2026-11-22 (the audit's arithmetic on that run). `make budget-accept PHASE=waterward.polder AUDIT=specs/444-work-budget-program/phases/waterward_polder.audit-5.txt` accepted the stage at 4,439 at 10 and 5,701 at 20, measured 2026-11-22 (`dev/work-budget.json` read after it). Audit-5's notes, owing no round: two repeated scans in `pieces` and `difference` (about 290 at 10) and bounded uncounted folds; left, the stage accepted.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the clipped band search | the counter test red at 9,864 to 13,748 tests a roll, measured 2026-11-22 (`make counters-inert`); the pins hold the points | `bank_bands`, `clip`, `crossings`, `close` in `polder.rs`; four tests and `bank_rolls` in `polder/tests.rs` | Kuwabata redrawn, its bands as T240's | none |
| the re-derivation | n/a: a budget record | `waterward_polder.derivation.md` (the bands), `waterward_polder.verdict-7.txt` | none | none |
| the raise and re-acceptance | the opener's test red with the opener forced off, measured 2026-11-22 (`make rust-test`, `/tmp/t250-fix-red.log`), and its once-only check red before it (`/tmp/t250-once-red.log`); the raise set, the accept refused on audit-4's OVER | the `trials` crate's `budget_change/rules.rs` (`raise_opened_by`, `ruled_by`, the opener in `set_budget`), `rules/shared.rs` (`raise_ready`'s `opened`), `sheets.rs` (its call), `rules/tests.rs`; `dev/work-budget.json` and its log through `make budget-set` | none | none: audit-5 LEEWAY, accepted |
| the corners filed once, the bands' loops counted | the counter test red at 240 for 60 corners added, measured 2026-11-22 (`/tmp/t250b/red-kept.log`); the strips and the bands pinned | `Filed`, `file`, `slot`, `face`'s filing and `fringe`'s one call in `waterward.rs`, `face_of` and `each_dike_corner_is_filed_once_for_all_the_flanks` in `waterward/tests.rs`; `bank_bands`' box tally, `merged` and `crossings`' counted sort in `polder.rs`, `the_waterside_strips_hold_their_points` and `the_met_spans_merge_into_runs_each_sample_once` in `polder/tests.rs`; `waterward_polder.audit-5.txt`, `dev/work-budget.json` through `make budget-accept` | Kuwabata redrawn, NOT COMPARED; its strips and bands pinned equal | none |

### T250 Approach (checklist part A)

1. **The goal, in the world.** The denser reeds on each bank are drawn as T240 drew them, at work that follows the reach of bank in the reeds, and the stage's budget prices them.
2. **The constraints.** 0074: the band lines each bank through the reeds and stops at the water. Rubric S5 (count every loop), S9 and S10 (missed work raised on a SOUND re-derivation). The GM's 2026-10-18 rule: speed work may change maps within the research claims.
3. **Where each comes from.** R: 0074's drawing page, cited at `bank_bands`. O: the counts and sizes measured 2026-11-22 (above). G: the GM's 2026-11-03 words, quoted in rubric S10.
4. **Do they describe the world here?** Yes. Measured 2026-11-22 on the rolls `hamlet --budget polder` counts and on Kuwabata, the map T240 drew the bands on.
5. **The order.** After T240's code, which it builds on; lands before T240, both in 449's one landing.
6. **The exits.** Green: the counter test passing with the drawing unchanged (met), a SOUND re-derivation (met), the stage raised (met, on the round arbiter's ruling) and re-accepted (met: audit-4 read OVER at 10 households, the stage was optimized, not raised again, and audit-5 reads LEEWAY, accepted). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The old search sampled the drain's whole 2,000 ft run to find about 600 ft near the reeds, measured 2026-11-22 (the sizes test above). The clip to the rings' boxes removes it. After audit-4: each flank's face filed the whole dike ring again, though a corner's nearest side does not hang on the flank; filing once removes it.
8. **The budget.** One landing.
9. **Done, measured.** `test@bank` 1,228 and 1,327 (every loop counted, the box folds and the span merge among them), `test@face` 2,668 and 3,682, and the stage 4,439 and 5,701, measured 2026-11-22 (`make work-budget WRITE=1`, the run `20261122T091359Z-rust-bdb111b827`, its per-roll counts). The derivation is SOUND at 3,549 and 4,525 (verdict-7), the stage was raised to them, and on audit-5's LEEWAY it is accepted at 4,439 and 5,701, 1.92x and 1.78x the first 2,310 and 3,206, measured 2026-11-22 (`dev/work-budget.json` read after `make budget-accept`).
10. **Before moving a constant.** n/a: `BANK_FT` and `BANK_STEP_FT` unchanged.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on the map changes: the band points equal the plain search's on every pinned roll, and the strips equal the fringe's before its corners were filed once. The defect was the work: a search over the whole drain for a band near the reeds, its edge walks uncounted, and the dike ring filed once per flank.

**Found and left?**

- `make budget-change` cannot set a bounded-n form's figure at 10 households, so the raise above cannot be set at 10 even with the GM's words. Fixed here, through T253, its own task filed from this one's review: `change` takes `--items-at-10` at a form's own sizes, measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/trials`).
- The re-acceptance was this task's own exit, met on audit-5 (Approach, exit 6), not a defect found and left.
- Audit-5's notes: `difference` reads the ring's sense again per bed and piece, and `pieces` scans each piece again for the span `boxed` already holds, about 290 at 10 together, measured 2026-11-22 (audit-5's reading of the run); not a defect: no map moves and no outcome is wrong, the stage accepted under its cap with the waste under half the total, which rubric S10 lets stand.
- `waterward.rs::pieces`' two claims are owed on their pages' change (`make claims-owed`, 2026-11-22: "research changed", and a claims-label on the run past the cut), their code not this task's. Not a defect: checks owed on a page's change, which the claims round runs (449 T249's re-check), not a wrong outcome.

**Performance work?** yes - an engine-speed task (the polder waterward stage's bank bands). 1. Where the work goes: `bank_bands`, every 2 ft sample of each bank's whole course asked of every ring, measured 2026-11-22 (the per-key run). 2. It removes work: a cheap screen (the box clip) before the test, and one crossing walk per met ring in place of a walk per sample. 3. Expected: the bands' tests cut about nine-fold. The stage's time is microseconds, so it is not timed. 4. Growth: the bands now grow with the bank in the reeds, not with the drain's run to the canvas edge (1,106 to 1,176 from 10 to 20 households before their box folds and span merge were counted, 1,228 to 1,327 after, measured 2026-11-22 (`make work-budget WRITE=1`)). 5. Before and after: the counts above, exact. No time was taken: the perf-ab tools are retired. 6. No map moved: the band points are pinned equal to the plain search's. After audit-4, the fringe: `face` filed and walked the whole dike ring per flank; the ring is filed once (`file`), `test@face` on seed 4 at 10 from 3,036 to 2,676, the stage from 4,677 and 6,084 to 4,317 and 5,550, then 4,439 and 5,701 with the bands' three uncounted loops counted, measured 2026-11-22 (`make work-budget WRITE=1`); the strips pinned unchanged.


### T251 (T228 found it 2026-11-22: the constitution's Python-era passages outside T228's task line)

- **Approach**: each passage the task line names is measured for the obligation it states, the tool it names and whether that tool exists, then restated in `.specify/memory/constitution.md` to today's check, labeled RETIRED in place with its quotes kept, or put to the GM, by the Governance section's versioning policy, as T228 did. The GM's quoted words stay byte for byte. The tools named are gone, measured 2026-11-22 (`ls` of `tests/_scope.py`, `tests/rolls.py`, `tests/gate`, `tests/full`, `pool/regressions`, `requirements.in`: none exists; `grep` of the Makefile and `rust/` for `EXHAUSTIVE`, `rolls_map`, `full_or`, `requirements.in`: 0 readers; `grep -rn '#\[ignore' rust`: 0).
  - **Upkeep, no version** (the obligation stands, a name retired): VI's Python bullet (the gate stays `make done`; its parenthetical's type check and pytest dropped); X clause 10 (`pytest.parametrize` -> one test over its variant inputs); X clause 13's `scripts/gates/check-file-scale.py` -> `l7r-gate check file-scale` (`file_scale.rs`, in `make static`, `make quick` and the push's checks, measured 2026-11-22 (a read of `push.rs`'s CHECKS)); Technical Standards' `@pytest.mark.rolls_map` sentence dropped; Governance's compliance line "for Python" -> "for code".
  - **Versioned** (the enforcement mechanism changed, the record holding its replacement, `dev/rust-tooling.md`'s port table under the 443 approval):
    - Principle X keeps its subject, measured 2026-11-22: clauses 1, 2 and 12 bind the Rust since 2.37.0, clause 13's check reads `.rs` and its refusal cites "Principle X clause 13" (`file_scale.rs` lines 1, 24), clause 5's floor is `rust cover`, and the only Python on disk is `scripts/gates/codeid.py` (`find -name '*.py'` outside `.git` and the build tree). So no retirement and no MAJOR question: the heading is "Code Discipline (NON-NEGOTIABLE)" and the scope the Rust crates and the Python left, a clause naming one language's construct binding that language. Clauses 7 and 8 (bare `except:`, `print`) stay the Python's, not extended to the Rust (no obligation invented).
    - X clause 3: the Rust compiler (the types row, "dropped, replaced by the compiler"); clause 5's gate: `rust cover`, `cargo llvm-cov --fail-under-lines 100` over every package under `rust/` (the coverage row), the exemption's reader `l7r-gate coverage-exempt`, its record empty, measured 2026-11-22 (a read of `dev/coverage-exempt.json`).
    - X clause 6: the Cargo workspace. FIXED HERE: `rust/Cargo.lock` was untracked, measured 2026-11-22 (`git -C /diagram ls-files rust/Cargo.lock` empty; `.gitignore` line 2's `*.lock`; no `--locked` in the Makefile, `rust/` or `scripts/`), so a fresh clone resolved each requirement afresh and the pin the clause and Technical Standards state did not hold; `.gitignore` gains `!rust/Cargo.lock`, so the lock is tracked and the session commits it.
    - VI's roll census (feature 217, `tests/rolls.py`): RETIRED in place, the GM's 216 and 217 words the aim; feature 444 FR-020's seeds (amendment 5, the GM 2026-10-31, and 2026-11-07) govern what `make done` rolls, the later and specific approval.
    - The Development Workflow's quick/gate forms (feature 133 T22, 135): items 1 (`tests/_scope.py`'s two forms), 3 (the bad-map corpus) and 7 (the test-roll cache) and the cost paragraph's `EXHAUSTIVE=1` mechanism RETIRED in place; item 2's tooling hash restated to `make static`'s per-crate reuse (449 T93, the change-selected-tests row); item 5's three trees to each crate's own tests, found by walking `rust/`; item 6's sweep to `rust/mode_a`'s tests and FR-020's seeds.
    - The plan template's VI and X entries restated the same way.
    - escalation-check CUT all six items on 2026-11-22 (`/tmp/t251/draft.md`) as already decided by the 443 approval and 444 amendment 5; clause 6's lock a fix the session makes (XIV), not a question. No question for the GM.
  - **The bump**: MINOR, 2.37.0 to 2.38.0, by the policy: enforcement mechanisms changed in VI, X and the Development Workflow; no principle removed or lifted from NON-NEGOTIABLE. Precedents 2.33.0, 2.34.0, 2.37.0.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the passages restated, the version, the template, the lock tracked | n/a (governance text and `.gitignore`, no engine code) | n/a | none | n/a |

### T251 Approach (checklist part A)

1. **The goal, in the world.** The constitution names only checks that run. A session reading it is sent to no deleted tool, test tree or marker; an obligation whose tool went is restated to today's check or labeled RETIRED in place, and Principle X states the subject it binds.
2. **The constraints.** The Governance section's versioning policy (GM 2026-09-06: upkeep takes no version; the GM approves all amendments). The task line: restate, retire by the policy, or put to the GM through escalation-check. The GM's quotations stay untouched. No obligation is invented: clauses 7 and 8 are not extended to Rust.
3. **Where each comes from.** G: the policy's words, the GM's quotes in each passage, the 443 design approval (2026-10-28), 444 amendment 5 and the 2026-11-07 ruling. R: `dev/rust-tooling.md`'s port table (443 FR-011). O: the tree, measured 2026-11-22 (`find`, `ls`, `grep` of the Makefile and `rust/`).
4. **Do they describe the world here?** Yes, measured 2026-11-22 (`find -name '*.py'` outside `.git` and the build tree: only `scripts/gates/codeid.py` and `.rust-ext/`'s generated `__init__.py`; `ls` of `tests/_scope.py`, `tests/rolls.py`, `tests/gate`, `tests/full`, `pool/regressions`, `pyproject.toml`, `requirements.in`: all gone; `grep -rn '#\[ignore' rust`: 0; `git -C /diagram ls-files rust/Cargo.lock`: empty).
5. **The order.** After T228 (2.37.0), on its text. Before T244. Independent of T252 (VI's `make maps` clause, the GM's).
6. **The exits.** Green: every passage of the task line restated, retired or put to the GM, the report entry and footer at 2.38.0, and `make closing-checks` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** No name from the task line is left in the principles as a live tool, measured 2026-11-22 (`grep -n 'pyrefly\|pytest-cov\|requirements.in\|parametrize\|_scope.py\|rolls.py\|rolls_map'` of the constitution below its report: each hit is labeled RETIRED or as the Python's former form).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session following the text looks for a tool, tree or marker that does not exist: a wrong outcome of the governance text. The lock: a fresh clone builds against whatever versions resolve that day, the pin the clause states not held. No map changes.

**Found and left?**
- `rust/Cargo.lock` untracked (above): fixed here.

**Performance work?** No.


### T252 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T252 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T253 (T250's MODE 4 review, 2026-11-22: `make budget-change` cannot set a bounded-n form's figure at 10 households, so the polder waterward raise T250 holds cannot be set even with the GM's words)

- **Approach**: the `change` subcommand takes `--items-at-10` as it takes `--items-at-20`, and the Makefile's `budget-change` line passes `ITEMS_AT_10`. A change now moves item counts only at its stage's own sizes: a form's bounded n (its `sizes`, `waterward.polder`'s 10 and 20) or a stage's 20, 40 and 80. A count at another size is refused, naming the stage's sizes and their flags, since it would sit in the table beside figures nothing reads. The form's sizes are read by one helper, `form_sizes` in `budget_change/rules.rs`, which the accept's reading of them now calls too, so the two agree. The words and re-pointing rules stay the shared ones (`rules/shared.rs`'s `NO_WORDS` and `repoint_refusal`), unchanged. Before the change, measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/trials`, `/tmp/t253-red-kept.log`): the new test `a_forms_change_takes_its_items_at_10` failed with "unrecognized arguments: --items-at-10", exit 2, 134 of 135 passing. After it, measured 2026-11-22 (the same run, `/tmp/t253-green.log`): 135 of 135 pass. On a scratch copy of the real table, measured 2026-11-22 (`l7r-gate budget-change --root <tmp> change waterward.polder 1 --exponent 0.35 --items-at-10 3549 --items-at-20 4525`): the stage read 3,549 at 10 and 4,525 at 20, exponent 0.35, its sizes kept; `--items-at-40` on it was refused naming 10 and 20. The real table was not touched: no budget is changed by this task.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| `change` takes the figure at 10 | `a_forms_change_takes_its_items_at_10` red without it, measured 2026-11-22 (`make rust-test`) | `budget_change.rs` (`ITEM_FLAGS`, `read_args`, `run`), `rules.rs` (`form_sizes`, `change_budget`, `accept_checked`), `rules/tests.rs`, the Makefile's `budget-change` line | none | none |

### T253 Approach (checklist part A)

1. **The goal, in the world.** A bounded-n form's budget can be changed at every size it is budgeted at, with the GM's words, through `make budget-change`.
2. **The constraints.** Feature 443 FR-005 (a later change needs the GM's words, logged with them); 444 D2 (a budget is per thing x the derivation's items at each size); the polder form's sizes 10 and 20 (`ask:444-polder-sizes`).
3. **Where each comes from.** G: the GM's 2026-10-28 approval of 443's design (the words rule); O: T250's MODE 4 review and the `ITEM_FLAGS` read, 2026-11-22.
4. **Do they describe the world here?** Yes: `dev/work-budget.json`'s `waterward.polder` holds `sizes` [10, 20] and `items_at_10`, measured 2026-11-22 (the table read).
5. **The order.** After 449 T243's `budget_change` edits, which it builds on; before T240, so T250's raise can be set.
6. **The exits.** Green: the new test passing and the trials crate green (met, measured 2026-11-22). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** 135 of 135 trials tests pass, measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/trials`); the scratch-table change above sets 3,549 at 10.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map. The defect was a tool that could not record a budget the derivation gives.

**Found and left?** None. Every writer of a stage's items was checked, observed 2026-11-22, method: `budget_change.rs`'s argument specs read: `set` already took the figure at 10; `change` was the one that did not; `sheets` sizes by sheet, not by households.

**Performance work?** No.


### T254, T255, T256, T257, T262, T266, T267, T270, T272 (bundle)

Nine record and pop-up follow-ups that T197's checks found (2026-11-22), worked as one bundle (451 T141): three page-session groups, each write then check-and-apply (`specs/449-rust-codebase/briefs/t254-g{1,2,3}-{write,checks}.md`, each write at or under the four-question cap), and the sheet edit by hand.

- **Approach**: each item is a sentence of the record or a pop-up that says more, or other, than its source or its findings page does; each is restated to the page and its checks re-run on the changed words. Per task:
  - **T254**: 0028's drawing-page bullet "How big was a retirement house, and where did it stand?" moved to 0028's findings page with its six notes and their originals; the drawing page keeps only the map's rule (about 18 by 15 ft, 6 or 12 ft off the farmhouse, each a GUESS), pointing to the findings bullet. Both retirement-house pop-ups already named 0028's findings page in `Entry:`; modal-research found their size sentences resting on it (G1 checks, 2026-11-22).
  - **T255**: 0004's opening says the median household "is five members" (the caste sense of "people"; a grep of all four 0004 files found no other demographic "people", observed 2026-11-22, method: `grep -i people`), and the meals-and-purse bullet now says what `kotobank-inkyo-2` says ("forming several households within one family").
  - **T256**: no page of the record says the farm was handed to the heir (observed 2026-11-22, method: `grep -i 'headship\|家督\|handed\|heir'` over 0004, 0028, 0029); the farmhouse pop-up's clause narrowed to 0004's words (moving out the main form of retirement, a separate building with its own entrance, most often on the house plot). Its modal-form and modal-research rounds came back clean on it.
  - **T257**: the archived page has the "1" (`served.html` reads 「1坪（歩）」; the report's window cut it) and writes the square as `m<sup>2</sup>`, which the checker read as `m2` against the quotation's `m²`. Fixed in the checker: `squeeze` folds a superscript digit to its digit, as NFKC does (`rust/gate/crates/research/src/verbatim.rs`, test `a_superscript_digit_reads_as_the_digit_a_sup_tag_leaves`; the crate green, 109 tests, observed 2026-11-22, method: `make rust-test CRATE=rust/gate/crates/research`). Red first: with the four superscript ranges taken out of `RADICAL`, the same run failed that test alone (108 passed, 1 failed, `verbatim/tests.rs:45`, `left == right`), and passed again with them put back (observed 2026-11-22, method: `make rust-test CRATE=rust/gate/crates/research`, the file restored from a copy and compared with `cmp`). The original restated with the page's space before the first "="; `make quote-verbatim Q=0030` now shows only a reference-marker difference (the page's [5], which no quotation in the record carries).
  - **T262**: 0229's canon comment quotes l7r.md's acolytes sentence (`make canon`, l7r.md:707), and its paragraph states it visibly as the setting's canon; modal-research found the hall-and-dwelling pop-up's acolytes resting on 0229 (its "shrine's land" corrected to "the monk's land", the canon's "the land" being the monk's tax-free plot).
  - **T266**: 0222's absence note restated to the findings page ("No Edo-period village worship hall three bays square was found measured"), its claims about the Himemiya pages and the town survey removed (neither archived, the ledger has them unreadable since 2026-10-02) and its search comment kept; the drawing page's "village sanctuary" wording (lines 4, 7, 8) made the findings page's rural shrine; `kuri-jawiki` restated to the reworded Wikipedia page on 0221's notes, 0221's drawing notes, the registry entry and (G3) 0227's two notes, where the same old wording stood. `make quote-verbatim` on 0221, 0222 and 0227 shows no DIFFERS or NOT-ON-PAGE but reference-marker ones (observed 2026-11-22, method: the G2 and G3 check sessions' runs).
  - **T267**: hoshigaoka's notes (line 74) and its sheet's SVG comment (line 293) say kamado (the cooking stove) for the kitchen end's mark, as 0221's drawing page does; `make map MAP=pool/country-shrines/hoshigaoka-shrine` REGENERATED, rc 0, the built page carrying the words (observed 2026-11-22, method: `grep -c` on the built html).
  - **T270**: the approach pop-up's Guesses carry 0223's "no fence along the approach" GUESS; 0222's drawing page records the wood kami's altar at Ubame (a 16 px square at 3 px = 1 ft, about 5 ft, fill `#C9A57A`, read off `pool/magistracies/ubame-magistracy/ubame-magistracy.svg`) as a map drawing CONVENTION, its size and its color each labeled, with what it costs (the mark reads larger than the one household shrine measured, about 16 in). The bullet names Ubame's wood kami alone, since Hayakawa draws its altars as emblems (modal-depiction's note). modal-depiction found the wood-kami-altar pop-up's drawn size resting on it.
  - **T272**: the sanctuary pop-up's Guesses carry the plinth GUESS ("no page read describes what a village sanctuary stood on"), its modal rounds run.
  - **The size cap**: 0028, 0222 and 0227 each went past 20,000 bytes of prose after their check rounds' EDITs (20,324, 20,016 and, touched, 20,198); each came back under it by shortening its feature-292 sweep comment, the folded sections named by number and topic in place of their slugs (git keeps the slugs), no visible word moved (observed 2026-11-22, method: `make question-sizes`, then `make quick` clean).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the checker's superscript fold (T257) | `verbatim/tests.rs`'s `a_superscript_digit_reads_as_the_digit_a_sup_tag_leaves` | n/a - tooling, no engine code | none | n/a |
| hoshigaoka's words (T267) | the sheet's checks in `make map` and the pool sweep | n/a - a comment and a notes line | hoshigaoka's page rebuilt | n/a |

### T254, T255, T256, T257, T262, T266, T267, T270, T272 Approach (checklist part A)

1. **The goal, in the world.** A reader of the record and the pop-ups finds each statement resting on a page that says it, each quotation matching its page, each drawing choice labeled, and the caste sense of "people" kept.
2. **The constraints.** Constitution XII (citations verbatim, the four labels, archive first), XIV (a defect is a wrong outcome), feature 274's write cap, the 20,000-byte prose cap, `dev/modals.md`, the house style.
3. **Where each comes from.** G: the GM's words in T197's section. R: 0004, 0028, 0030, 0221, 0222, 0223, 0227, 0229, `setting/l7r.md` line 707. O: T197's checks (its plan section above) and this bundle's check rounds (the three handoffs `specs/449-rust-codebase/briefs/t254-g{1,2,3}-handoff.md`).
4. **Do they describe the world here?** Yes: each finding re-read on its page before the briefs were written (observed 2026-11-22, method: `grep -n` of each quoted phrase and `make quote-verbatim` on 0030, 0221, 0222).
5. **The order.** After T197; the claims round after the page sessions, since their edits re-owe the claims citing those pages; all before T158.
6. **The exits.** Green: `make record` builds, `make record-owed` names none of the bundle's units, `make claims-report` holds none of its claims open, `make closing-checks` green for it. Red: what failed recorded and the bundle set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The three handoffs' CHECKED lines, `make record-owed`, `make claims-report`, the closing check.
10. **Before moving a constant.** n/a - no constant moves.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader was told, or could take, what no page says: the pop-ups' sizes and acolytes resting on no Entry page, a farm handed over that no page records, quotations not matching their pages, an unlabeled drawing color, "people" in a demographic count. Each is a finding the record breaks, fixed in words; the checker's fold is a check failing a correct quotation.

**Found and fixed?**
- `make quote-verbatim` failed a correct quotation of a page's superscript (`m²` against `m<sup>2</sup>`): fixed in `verbatim.rs`, above (T257).
- 0227's `kuri-jawiki-3` notes carried the same old Wikipedia wording as 0221's (NOT-ON-PAGE and DIFFERS): fixed here in a third page session (G3), checks clean.
- The retirement-house pop-up and three others' sentences moved by 0028's tightening: G1's modal-research on the 12 pop-ups touched, 6 ACCURACY EDITs applied; the byre and well pop-ups' form EDITs applied.
- 0222's altar bullet first read as a rule for every compound shrine's second altar (modal-depiction): narrowed to Ubame's wood kami, and its color labeled (quote-check's wording point).
- 0222's drawing page said no page describes what a village sanctuary stood on, where 0269 records the Hachiman shrine of Shibasaki's stone base set by masons in 1841, and the sanctuary pop-up now says so (impl-drift's UNCLAIMED note, modal-depiction's note): the plinth sentence and its absence note restated, the plinth still a GUESS for every sanctuary on one example.
- The shrine claims round (observed 2026-11-22, method: impl-drift's replies recorded with `make claims-checked`): the Rust claims 6 IN-STEP; the country-shrine section's 68, 64 IN-STEP, two DRIFTED known to 417 T33 (the genkan tag, the all-earth kitchen), the basin claim's "a village basin" restated to a parish's basin (Nagao's, given by its parishioners, the page not calling Nagao a village shrine), and its three UNCLAIMED decisions written as GUESS claims (the one-roof dwelling end at 46 x 28 ft, the sanctuary's stone plinth, the privy at least 15 ft from a well).
- The one-roof dwelling end claim said 0221's drawing page records the one-roof end at 46 x 28 ft as a guess, where the page sets that size only for a dwelling standing as a house of its own (impl-drift DRIFTED, fix: claim): restated to the two-building guess carried over to the one-roof end, a size no page records (observed 2026-11-22, method: impl-drift on the restated claim, recorded with `make claims-checked`).
- The Size anchors paragraph said "no small kuri measured" where the dwelling band claim and 0221 record one small kuri, a Koshin hall's about 12 x 15 ft (observed 2026-11-22, method: impl-drift's reply on the dwelling band claim, 0221's drawing page): restated to "no village parish temple's kuri measured"; claims-triage sent the three dwelling claims on, and impl-drift found the band and the two-building size IN-STEP (observed 2026-11-22, method: `make claims-triage`, impl-drift, `make claims-checked`).
- The modal-depiction round cap on the six shrine pop-ups: the round arbiter ruled accept on compound-shrine and named four more (hall-and-dwelling, the-monk-s-rooms, sanctuary, shrine-altar), their tabs unchanged since round 6 and the moved 0222 bullets other kinds'; one round on wood-kami-altar alone, on whether its tab calls the wood color the maps' convention (observed 2026-11-22, method: `make arbiter-bundle`, the round-arbiter's ruling in `arbiter.jsonl`, the five answered with `make record-checked REASON=`).

**Where the deferrals land**: Each deferral lands before T244, the stop before the next port step: the parked hamlet stages are the one port left, and T244 holds them until the GM resumes them, so every fix lands before that step starts (the GM 2026-11-18: fix all known bugs in each step before porting the next; observed 2026-11-22, method: `grep -n '^- \[ \]' specs/449-rust-codebase/tasks.md`, no open port task but the parked stages behind T244). Each fix is made in every copy that lives: the record's pages and pop-ups have one copy each, and T285's engine fix is the program table's in `docs/building-programs.md` (the composition rule and knob 4), which the Rust Mode A reads, its one live copy: no tracked Python file holds the rule (observed 2026-11-22, method: `git grep -l -i -E 'burial.{0,40}(yard|apart)' HEAD -- '*.py'`, no file; the same over `rust/*.rs` and `docs/building-programs.md` names only the procedure doc).

**Found and left?**
- The approach pop-up's one, three or seven arches and the sanctuary pop-up's Fortune are the GM's canon stated only on 0220's and 0222's drawing pages, so no Entry page carries them (modal-research M8/M13). Not fixed here: two more findings pages' text, past this bundle's write caps. Filed as T282; lands before T244.
- 0028's and 0229's quote-check findings outside the change: sugiura-1973-fuzoku-7's period and its 'snowy district' heading, matsumoto-dosojin-2's reading of 花見, passages joined without '; ' on four notes, and 0229's opening generalizing one temple's "small house for its monk". Not fixed here: outside the blocks this bundle changed, each a quotation owing its own check round. Filed as T283; lands before T244.
- Five pop-ups' open findings: hamlet/byre's walls and front unasked (modal-form M5), hamlet/well's roof guess with no reckoning beside its count (M11), byre_form--yard_shed's unreconciled 3 m Kinki stable and dug floor (GAPS, observed 2026-11-22, method: modal-research's reply on the pop-up), wood-kami-altar's About silent on why Ubame's Inari shrine keeps it (canon, modal-form P4), shrine-altar's emblem marks recorded on no drawing page. Not fixed here: each needs a research pass or the GM's notes first. Filed as T284; lands before T244.

- The two DRIFTED shrine-dwelling claims known to 417 T33: the dwelling entry tags a plain earth-floored vestibule genkan, where the Edo genkan is an entrance with a shikidai, so the monk's vestibule reads as a formal guests' entrance; and the kitchen is drawn all earth floor, where the kamado stood on the doma "as a rule", so the kitchen reads as having no floored part (impl-drift, fix: code). Not fixed here: sheet drawing changes, past this bundle's record and pop-up words, and 417 T33's own items. Filed as T287 (through 417 T33's own work or there); lands before T244.
- A hill shrine's burial ground can fall in its yard: the composition rule and knob 4 roll yard or apart for every sheet on no map with no hill exception, against 0236 and the section's own claim (impl-drift DRIFTED, outside the change). Not fixed here: an engine change to the shrine's composition rule, past this bundle's record and pop-up words. Filed as T285; lands before T244.

- 0222's two record findings outside the change (quote-check and record-format): the drawing page's wealth-knob bullet states the gifts and the strength stones with no footnote, and leaves its roofing terms unglossed. Not fixed here: sentences this bundle's edits did not touch, each a quotation owing its own search and check round. Filed as T286; lands before T244.
- The wood-kami-altar pop-up's real finish, which no page records (modal-depiction's outside finding on the arbiter's scoped round): fixed here, the round's EDIT making the tab call the wood color a map drawing convention, so no sentence takes it for the altar's real finish, and About already says the altar's look is not recorded; its found.jsonl row settled (`make found-close`, no longer holds).

**Performance work?** No - record, pop-up and sheet words, and one checker fold.

### T258, T268, T269 (bundle)

- **Approach**: three tooling defects in the guards and the gate's found list, each measured first, then red first, then pinned; one
  bundle (451 T141), started by the session as `make task-start F=449 T="T258,T268,T269"`.
  - **T258, decide first judges the check's own task.** Measured 2026-11-22 (`make guard-log GUARD=check-bundle SINCE=2026-11-22
    FULL=1`): 113 record-check dispatches carried `DECIDE_OK` and 32 were refused `decide-first`, the escapes naming another builder's
    task (T197's checks judged on T248's and T250's sections, T265's on the mark's). Cause, read in the code: `check_bundle_hooks`
    asked `l7r-gate plan decided <root>`, whose answer (`plan/task.rs` `decision_refusal`) is the clone's one `active-task` mark's task
    - whichever task started last (the mark named the record bundle's T254 at 11:02Z, three builders running) - or the feature's first
    open task. Fix: `check_bundle_hooks/own.rs` reads the task the check serves, first that says - its own words (the Agent call's
    `description`, else its prompt's first line, the feature the number before the id, else the feature whose start names it, else
    `feature.json`'s), its dispatching builder (`set_down_hooks::builder_brief`, a bundle's every member), its page session's brief
    (`L7R_PAGE_SESSION` looked up in `page-sessions/index.txt`, the task its first line or file name names: `t197-g2-checks.md`) - and
    asks `l7r-gate plan decided <root> <feature> <task>`, the builder-stop guard's question (451 T84). Both differences of that form are
    accepted: a task with no plan section passes (it owes no decision; the one-argument form's `owed` plan-stage fallback was the
    mark's reading), and an unfiled found-and-left deferral refuses too (`make decide` refuses it already, so only a `DEFER_FORM_OK`
    section meets it). A check NOTHING names a task for is never passed silently (FR-003(a); the MODE 4 review, round 1): it falls back
    to the one-argument form, the mark's answer, and where that refuses it is refused with `it names no task it serves - name it in its
    description (<feature> T<n>: ...) or its prompt's first line` before the mark's answer, so its dispatcher names the task and is
    judged on its own section from then on. Every refusal keeps the words `decide first, then check (feature 375 FR-003a)` before the
    gate's answer, which both suites read; `test-checks-hooks.sh`'s four dispatches now name their task (`999 T01: Read ...`).
  - **T268, a foreground Agent result is an end; a bundle's builder counts; a task an open GM question names waits**. Measured 2026-11-22
    (grep of T197 G2's check session's transcript `e4a31b0e-...jsonl`): 27 `toolUseResult`s opening `"status":"completed"`, each with
    its `agentId` after the prompt, 28 ids read as launched and 2 notices, so `running()` was never empty and the Stop hook refused
    `a builder slot is free` four times; over 12 of the clone's transcripts the result's status was `async_launched` 3,387 times and
    `completed` 89 (the same grep). Fix: `set_down_hooks.rs` `events` reads each `"toolUseResult":{` opening and an id inside one that
    opens `"status":"completed"` is `Ended` (no regex spans the prompt). Then the session's note of 2026-11-22, folded in: *'the same
    set_down_hooks count also misses bundle builders. With three builders running (449 T265, your bundle T258/T268/T269, and the record
    bundle T254 to T272), the Stop hook said "1 of 3 builders running (449 T265)" and named T252, which waits on the GM ... Fold that
    into T268, red first, beside the foreground-result fix. And a task whose line waits on the GM (T252, filed for his answer)
    shouldn't be named as the next to start'*. Measured 2026-11-22 (the two live builders' meta files): `449 bundle T258, T268, T269:
    ...` and `449 record bundle: nine ...` - neither matched `^\d{3}\s+T\d+`. Fix: `builder_brief` (pub, the one reader) takes a brief
    opening with its feature number, its tasks the ids before its first colon, else its prompt's first line's (the agent's own
    transcript's first record: `Feature 449, a bundle of nine ...: T254, T255, ...`); `builders` counts one row an agent, its tasks
    joined (`449 T258+T268+T269`), `busy_files` every member's edits. The wait on a GM question is `waits()`'s, so the free slot, the nothing-running
    refusal and `make task-start`'s picker share it: an open question of the feature's `gm-review.jsonl` (`question`, `owed` or `kept`,
    `make gm-review`'s open states) naming the task in its text - T252's kept question ends `(T252)` - its end recorded when the answer
    moves the row on; no prose of the task line is read (T102's D7e: a wait needs a recorded end). The builders' reading and the GM
    wait are `set_down_hooks/builders.rs`, split out because `set_down_hooks.rs` passed the 1,000-line bar (1,005 lines, measured
    2026-11-22 by the closing checks' file-scale; 908 and 113 after).
  - **T269, a found row its checker ruled no defect settles as one.** Measured 2026-11-22 (a read of every `specs/*/found.jsonl`,
    `no defect|not a defect|needs no fix|XIV` over the open rows' findings): 1 of 1,266 open rows of 1,591, 449's row 140 (bundle
    t249-24's merged dike-pond parcel, `so this is no defect and needs no fix`). Fix: `record.rs` `close_rows` takes a `--why` opening
    `not a defect` naming constitution XIV, six words or more, where the row's own finding states the checker's ruling (`no defect`,
    `not a defect`, `needs no fix`) - never the closer's words, a reply quoted in the reason among them (the MODE 4 review, round 1,
    dropped that branch), so 405 D36's rule (a finding that still holds is filed) stands; each refusal prints the form, and a row
    whose finding states no ruling is told to be filed as a task or settled `no longer holds`. The row is
    `settled` with its `why`, as a `no longer holds` row is (no reader of the found list reads `why`: grep of `rust/` 2026-11-22).
  - Found and fixed here: `builder_stop_hooks.rs` `brief_of` read the same `<feature> T<n>` brief, so a bundle's builder stopped unheld
    (451 T84's hold skipped this very bundle); it now reads `builder_brief`, held on the first member, whose section is every member's.
  - Red first, measured 2026-11-22 (each fix disabled in the working tree, the tests run, the fix restored): `rust/guard/shared` 3 failed of 431 (the foreground test, the bundle-builder test with the brief read as one task and no prompt line, the GM-wait test); `rust/guard` 1 failed of 454 (`a_check_is_judged_on_its_own_task_never_the_mark_s`, the guard asking the one-argument form); `test-check-bundle-hooks.sh` 4 failed of 38 (section 5: the decided task, the undecided task's message, the prompt's task, the page brief's task); `rust/gate/crates/record` 1 failed of 92 (the no-defect test, the settlement disabled). Section 5 of the check-bundle suite runs on the clone's real gate: the wrapper sets `L7R_GUARD_TREE` to its own tree, so a stub gate is never reached. Round 2's two changes, red first the same way (2026-11-22): `rust/guard` 1 failed of 454 (`a_check_is_judged_on_its_own_task_never_the_mark_s` at its "names no task" assert, the no-task arm passing silently as before); `rust/gate/crates/record` 1 failed of 92 (the same no-defect test, the quoted-reply branch still in: `close_rows` returned `Ok` where the refusal is owed).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| T258 the check's own task | `own/tests.rs` (words, builder, page session), `check_bundle_hooks/tests.rs` `a_check_is_judged_on_its_own_task_never_the_mark_s`, `test-check-bundle-hooks.sh` section 5 | n/a - no engine code | none | n/a |
| T268 the foreground end | `set_down_hooks/tests.rs` `a_foreground_agent_s_result_is_its_end_and_a_background_launch_still_runs` | n/a | none | n/a |
| T268 a bundle's builder | `a_bundle_s_builder_counts_once_for_all_its_tasks`; `builder_stop_hooks/tests.rs` `a_bundle_s_builder_is_held_on_its_first_member` | n/a | none | n/a |
| T268 the GM wait | `a_task_an_open_gm_question_names_is_never_the_next` | n/a | none | n/a |
| T269 not a defect | `record/tests.rs` `a_finding_ruled_no_defect_is_settled_not_a_defect_naming_its_ruling`; row 140 closed through the built gate | n/a | none | n/a |

### T258, T268, T269 Approach (checklist part A)

1. **The goal, in the world.** No map changes. T258: a record check is held only by the section of the task it serves, so a builder's
   checks need no `DECIDE_OK` while another builder's section is undecided. T268: the Stop hook reads a finished foreground agent as
   finished, counts a bundle's builder as one builder of its tasks, and never names as next a task the GM is asked about. T269: a
   found row its checker ruled no defect is closed as one.
2. **The constraints.** Each task's line; the session's note quoted above (T268); feature 375 FR-003(a) (decide, then check);
   451 T84 (the builder-stop question), T88 (the free slot), T102 (a wait has a recorded end), T141 (the bundle); 405 D36 (a finding
   that still holds is filed, never settled); constitution XIV (a defect is a wrong outcome, not a difference).
3. **Where each comes from.** G: constitution XIV; the session's note. O: the four measurements above, each dated with its method.
   R: none - tooling, no research question.
4. **Do they describe the world here?** Yes: the guard log, the live transcripts and meta files, and the found lists are this clone's,
   read 2026-11-22.
5. **The order.** Each measured first; each test written and run red against the code with its fix disabled; then pinned. All three
   land before 449 T158 (T258's and T268's lines say so; T269 with them).
6. **The exits.** Green: `make closing-checks T=T258,T268,T269 F=449` and the red proofs above. Red: what failed recorded and the task
   set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each reader was found by grep (`plan", "decided`, `BRIEF`, `agentId`, `no longer holds`), and the one
   more reader of the old brief (`builder_stop_hooks`) is fixed here.
8. **The budget.** One landing.
9. **Done, measured.** The tests above green; row 140 closed by `make found-close F=449 ROWS=140 WHY="not a defect ..."`; the T265
   builder's and the record bundle's checks pass with no `DECIDE_OK` (by the case each test replays).
10. **Before moving a constant.** n/a - `BUILDERS` unchanged; a bundle counts once under it.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No reader of a map sees anything differently. The defects are the tools' wrong outcomes: T258 refused 32 checks
    on another task's verdict and sent 113 to the escape; T268's hook refused a turn four times with nothing running and named a task
    waiting on the GM; T269 left a settled finding open with no way to close it.

**Found and left?** none - `builder_stop_hooks`' bundle brief fixed here.

**Performance work?** no.


### T259 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T259 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T260 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T260 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T261 (449 T249's claims re-check, outside its change, 2026-11-22, found.jsonl row 141: 0031's drawing page says every hamlet keeps its back to the wind, while the seat backs Sawada's cluster to the hill, off the wind)

- **Approach**: which is wrong was settled by the record and a search pass, not by the GM. 0031's drawing page's "on every map" is a project decision (its note -8, the round arbiter's ruling on ask:444-T22-windward, which spoke only of ROLLED falls); its first sentence seats a cluster on the higher, drier ground beside its paddy, and 0029's drawing page turns every house to face south. The search pass (research-pass agent, 2026-11-22, archive then web, Japanese and Chinese, on a settlement whose ground falls toward its wind) found one archived survey that sees the case, `sakamoto-tsubaki-1985-omoya-muki` (42 Okinawan villages, 1974-84): on gentle slopes the houses turned south whatever the fall (p.114), at a hill's foot they turned their back to the hill, for the view (p.115); no page read says which way a CLUSTER's back faced when hill and wind lay opposite; China: nothing found. So the code is not against the record: on Sawada's declared fall the wind-facing margins lie on the wet toe, the seat takes the high, dry margin the page's first sentence gives, and the houses still face south by 0029's rule - the cluster's back to the hill is the one unrecorded choice, the algorithmically easier route the record leaves open. What is wrong is the page: it states the rolled case as every hamlet's and is silent on a declared fall into the wind. Not a defect in the code (constitution XIV: no map draws a wrong outcome - nothing reads `Frame.out` or `offwind` but the hem's kept ground, measured 2026-11-22 by grep over rust/, and the shipped Sawada manifest, pool/hamlets/sawada/sawada.json, is the Python seat's, backed to the wind by feature 261's re-seed). The fix is a record correction worked in a page session (`specs/449-rust-codebase/briefs/t261-write.md` then `t261-checks.md`): 0031's drawing page narrows "every map" to the rolled falls, records the declared case - the high margin, the cluster's back to the hill as a GUESS with its absence note, each house still facing south with the survey's p.114 passage at it - and the seat claim is restated to the page's words, no longer attributing 背山面水's "the high side and the windward side one side" to 0031 (no 0031 file carries 背山, grep 2026-11-22; 0071's session note says no page read gives that reading), and `SeatRefused`'s doc ("never seated off the wind", false since T27) restated. The page's words then made one code fix owed (constitution XIV, a wrong outcome): the fallback fired on any empty first ranking, so a crosswind map with its wind-facing margins refused would seat off the wind where the page says rolled falls back it; it now fires only on a fall toward the wind (`seat.rs::seat`). Labeled: the cluster's back to the hill on a declared fall into the wind is a GUESS.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the page and the claim | n/a: no code behavior changes (doc and claim text only); the fallback stays pinned by `driver::tests::a_resting_field_drains_off_the_map` (Sawada seats, `frames[0].offwind`) | n/a | none: no engine behavior changed | n/a |
| the fallback only on a fall toward the wind | `seat::tests::only_a_fall_toward_the_wind_backs_the_hill`, red first (a crosswind fall with its north and west margins refused was seated on its high south margin off the wind, measured 2026-11-22 (`make rust-test CRATE=rust/phases`: 123 passed, 1 failed)), green after (measured 2026-11-22, the same) | 1,000 cohort seeds from 1, 0 refused or broke a rule, measured 2026-11-22 (`make cohort N=1000 SEED=1`, after the fix) | none: Sawada's fall runs into its wind and still seats, pinned by the driver's test | n/a |

### T261 Approach (checklist part A)

1. **The goal, in the world.** A reader of Sawada's map finds its case on 0031's drawing page: the cluster on its high, dry margin with its back to the hill, a labeled guess, each house facing south; no page says every hamlet's back is to the wind.
2. **The constraints.** Constitution XII (search before "guess"; every rendering decision labeled; where the record is silent take the easier route and say which) and XIV (a defect is a wrong outcome, not a difference); 0031's drawing page's "Where does a village's cluster sit?"; 0029's drawing page's south-facing bearing; 0072's windward belt; the arbiter's ruling on ask:444-T22-windward.
3. **Where each comes from.** R: 0031's drawing page and its notes -7 and -8; 0029's drawing page; `sakamoto-tsubaki-1985-omoya-muki` pp.114-115; 0071's session note; 0072. O: the search pass of 2026-11-22; the greps of 2026-11-22 (背山 over 0031's files: none; `offwind` and `Frame.out` readers over rust/). G: none needed (the record decides, GM 2026-10-25).
4. **Do they describe the world here?** Sawada's spec declares `down_deg` 225 into the regional northwest wind, measured 2026-11-22 (read of pool/hamlets/sawada/sawada.spec.json). The driver's test pins its seat off the wind, measured 2026-11-22 (read of `driver/tests.rs`). The rolled falls never take the fallback, measured 2026-11-07 (444 T27's cohort of 1,000 seeds, its commit message).
5. **The order.** The search pass, the page session (write, then check-and-apply), then the seat claim worded to the page as written and its impl-drift re-check, then the fallback's trigger narrowed, red first.
6. **The exits.** Green: the page session's record checks clean and the seat claim IN-STEP. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one bullet and its notes on one page, one claim.
8. **The budget.** One landing.
9. **Done, measured.** `make record-owed` names nothing of 0031 after the check session; the seat claim's impl-drift IN-STEP.
10. **Before moving a constant.** n/a: no constant moves; the claim is restated.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a live map changes: Sawada's seat and the drawn houses are as before (a crosswind map with every wind-facing margin refused is now refused by name, not seated off the wind); what a reader now finds is 0031's drawing page recording the declared case and its guess instead of saying every hamlet backs the wind - not a defect in the code, the page and the claim restated (constitution XIV).

**Found and left?**
- `SeatRefused`'s doc said a settlement is never seated off the wind - fixed here.
- the seat's fallback fired on any empty first ranking, so a rolled crosswind map whose wind-facing margins were all refused would have been seated off the wind, against 0031's drawing page (the rolled falls keep their back to the wind; found by T261's impl-drift, OUTSIDE THE CHANGE) - fixed here: it fires only on a fall toward the wind, and such a map is refused by name.
- an off-the-wind seat keeps its belt's ground behind its back, uphill, where 0072's drawing page puts every belt on the windward side; a reader of Sawada's map would see the dry hem kept off a strip on the hill side, away from the wind. Not fixed here: the belt's ground is drawn in `rust/phases/src/driver.rs`, T240's file, and whether the belt follows the wind or the back on an offwind seat is a record question of 0072's. Filed as T277; lands before T158.

**Performance work?** no


### T263 (449 T249's measurement for `draw_sluices`, 2026-11-22: the polder's feeder and its outfall drain stop 8.5 ft short of the ring canal they join, measured 2026-11-22 (449 T249, Kuwabata's SVG read), nothing drawn across the hop)

- **Approach**: measured first, then a join drawn from each sluice to its ring canal corner, red first on the drawn SVG. THE GAP, measured 2026-11-22 (`/tmp/t263s/gap.py` reading the drawn strokes of each SVG): on Kuwabata (`pool/hamlets/kuwabata/kuwabata.driver.svg`) and six more rolls (`polder_grid` seeds 3, 7, 11 at falls of 90, 45 and 180 degrees, `mulberry_dike_fishpond` seed 21 grid, seed 5 mosaic at 135, seed 21 mosaic, rolled with `make hamlet` into `/tmp/t263m`), the feeder's end and the inlet's point stand 8.49 to 8.50 ft from the head canal's corner, and the outfall drain's start 8.49 to 8.50 ft from the drain trunk's end, on every roll. It is the frame's own geometry: the ring canal lies `RING_FT.0` (6 ft) out from the plots and the sluices `RING_FT.1` (12 ft) out each way, 6 times the square root of 2, and the frame is rigid, measured 2026-11-22 (`RING_FT` and `Frame::at` read). The open ground between the strokes' round caps is 4.74 ft at the inlet (the 3 ft feeder against the 4.5 ft head canal) and 2.99 ft at the outfall (the 5.5 ft drain against the 5.5 ft drain trunk), measured 2026-11-22 (the same script, the strokes' half-widths taken off). The sluice frame covers 1.4 ft of it (the board's 2.8 ft thickness centered on the point, the posts stand 9 ft to each side), so about 3.3 ft and 1.6 ft of the hop show open ground, measured 2026-11-22 (`sluice_frame`'s rectangles read against the hop). The dike's band, drawn after the channels, covers the feeder's last reach across the dike, and the hop lies inside the dike's inner face (`inner_env`), so the band does not cover it, measured 2026-11-22 (the SVG's dike path read: its inner ring's corner is the inlet's point). Kuwabata's crop is 2,025.5 ft wide, about 1.5 to 2 ft a pixel at fit zoom, so the break is a pixel or two at fit and plain when zoomed, measured 2026-11-22 (the SVG's viewBox). THE PAGES: 0179's drawing page puts the board "a few steps down the channel from the junction", and 0060's has the drain's run onward curve "out of the collector's exit, so the junction reads as a turn"; neither, nor 0019, says how the channel is drawn between the sluice and the ring, measured 2026-11-22 (the three drawing pages searched for junction, join and meet). THE FIX, in `rust/phases/src/field/polder.rs`: `joins` lays two reaches as ditches after the ring's trunks, the inlet's point to the head canal's start (`inlet_join`, supply) and the drain trunk's end to the outfall's point (`outfall_join`, drain), each at its trunk's own width at that corner (4.5 ft and 5.5 ft, the widths of `research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html` at those corners, read off the trunks, one source). The feeder and the outfall are not extended, so the sluices' boards keep their directions and the waterside stage's bank bands do not move. The rendering decision is labeled at `joins`: a GUESS, the reach's course and width (0179 silent on them), and 0060's turn for the outfall's join. `draw_sluices`' "the board's place" claim is restated: the board on the point, joined to the junction by a drawn reach, 8.5 ft down the blocked channel from it, measured 2026-11-22 (`/tmp/t263s/gap.py` on the drawn SVGs). The ring-canal check's `RING_CANAL` (`check.rs`) filters by seg and leaves the joins out: they lie inside the dike's inner face, where the dike check already holds the settlement off. Red first: `each_sluice_is_joined_to_its_ring_canal_corner_by_a_drawn_reach` (`polder/tests.rs`) reads the drawn strokes off `Rolled::svg` on Kuwabata and a grid polder falling at 30 degrees and requires a stroke from each sluice's point to its ring corner, the hop's middle inside `inner_env`, and the corner 8.5 ft off, the figure measured 2026-11-22 (`/tmp/t263s/gap.py` on the drawn SVGs). It failed with the joins left out, `(false, true, "8.5")` at the grid polder's inlet (1930.1, 2762.4), measured 2026-11-22 (`make rust-test`, `/tmp/t263m/red.log`, the `extend` line replaced for the run), and passes with them, 123 of 123 in `rust/phases`, measured 2026-11-22 (`make rust-test CRATE=rust/phases FRESH=1`, `/tmp/t263m/green2.log`). THE COUNT, measured 2026-11-22 (`make work-budget`, `/tmp/t263m/wb-before.log` and `wb-after.log`): `waterward.polder` unmoved at 4,439 at 10 and 5,701 at 20, its accepted figures, so no budget rule is owed. `field.polder` from 3,075 and 4,815 to 3,083 and 4,823 (`write@polder_ditch`, two points written twice for each of two joins), 0.7x its 4,651 and 6,584 budget, measured 2026-11-22 (`make work-budget`). `seat.polder`, unbudgeted, from 2,047 and 2,703 to 2,049 and 2,705 (the joins two more lines its way out may not cross), measured 2026-11-22 (`make work-budget`). THE MAP: `make map MAP=pool/hamlets/kuwabata` REGENERATED, NOT COMPARED (the mirror's engine is not HEAD's), measured 2026-11-22; its SVG now draws `M2328,2328 L2334,2334` at 4.5 ft in the supply ink and `M2334,3416 L2328,3422` at 5.5 ft in the drain ink, each sluice's point to its ring corner, measured 2026-11-22 (the SVG's paths read).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the joins drawn | the drawn-stroke test red with the joins left out, measured 2026-11-22 (`make rust-test`, `/tmp/t263m/red.log`) | `joins` and its call in `polder()` in `field/polder.rs`; `draw_sluices`' restated claim in `driver/polder.rs`; `drawn_strokes` and the test in `polder/tests.rs` | Kuwabata redrawn | none |

### T263 Approach (checklist part A)

1. **The goal, in the world.** The water drawn on a polder runs unbroken from the wild pond through the inlet sluice into the ring canal, and from the drain trunk through the outfall sluice onward.
2. **The constraints.** 0019: water crosses the dike only at gated sluices and a ring canal lies at the dike's inside foot. 0179: the board stands a few steps down the blocked channel from the junction. 0060: the drain's run onward reads as a turn out of the collector's exit. The waterward stage's accepted budget (449 T250).
3. **Where each comes from.** R: the 0019, 0179 and 0060 drawing pages, cited at `joins` and `draw_sluices`. O: the gap measured on seven rolls 2026-11-22 (above). G: T263's task line, from 449 T249's report.
4. **Do they describe the world here?** Yes: the gap is the frame's geometry, 8.49 to 8.50 ft on every roll, measured 2026-11-22 (`/tmp/t263s/gap.py` on the drawn SVGs), both archetypes and both dike-pond layouts.
5. **The order.** After 449 T234's sluice frames and T250's bank bands, which it leaves as they stand; in 449's one landing.
6. **The exits.** Green: the drawn-stroke test passing on both rolls, the polder's tests green, the waterward count unmoved. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: two fixed reaches, no search.
8. **The budget.** One landing.
9. **Done, measured.** The drawn-stroke test green on Kuwabata and the grid polder, 123 of 123 in `rust/phases` (`make rust-test CRATE=rust/phases FRESH=1`); Kuwabata's SVG drawing both joins; `waterward.polder` at its accepted 4,439 and 5,701, measured 2026-11-22 (`make work-budget`).
10. **Before moving a constant.** n/a: `RING_FT` unchanged; the joins take the trunks' widths.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader zoomed in on either sluice sees the water stop at the gate and the ring canal start 8.5 ft on, about 3.3 ft and 1.6 ft of open ground showing past the board, measured 2026-11-22 (`/tmp/t263s/gap.py` on the drawn SVGs); after it, the channel runs on through the gate into the ring.

**Found and left?** none.

**Performance work?** no.

### T264 (449 T249's `make claims-owed`, 2026-11-22: the claims-label lint flagged docs/building-programs.md's "dwelling band 34-60 by 18-38 ft" a bare GUESS whose account names 0221)

- **Approach**: a label fix, no code. 0221's drawing page draws the two-building form's dwelling "at the size of the map's farmhouses, 46 by 28 ft" and calls that size "a **guess**" (no village parish temple's kuri measured, the one small kuri, a Koshin hall's, about 12 by 15 ft), measured 2026-11-22 (the page read, its second item). So the claim's `Research:` line is restated from a bare `GUESS: ... (research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html)` to the grammar's `GUESS research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html: the band round the map's 46 x 28 ft farmhouse, the size the page records as a guess; ...`, edited in docs/building-programs.md's own text, the one line. The lint's feet check holds: both figures it reads (28 ft, 15 ft) stand on the page, measured 2026-11-22 (the page read), and `make claims-owed` no longer flags it, measured 2026-11-22. Re-checked by impl-drift on `make claims-bundle UNITS=` (the one key). VERDICT_RESULT.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the claim restated | the claims-label flag, gone at `make claims-owed` | the one `Research:` line in docs/building-programs.md | none (no engine code) | none |

### T264 Approach (checklist part A)

1. **The goal, in the world.** The country shrine's dwelling band says honestly where its guess is recorded: 0221's drawing page.
2. **The constraints.** research/CLAUDE.md's claim grammar and the claims-label lint (`rust/gate/crates/claims/src/claims/labels.rs`): a GUESS whose page records it cites `GUESS <its .drawing.html>`, and every feet figure its account gives stands on that page.
3. **Where each comes from.** R: 0221's drawing page (46 by 28 ft, a GUESS, and 12 by 15 ft, measured 2026-11-22 (the page read)); O: `make claims-owed` 2026-11-22; G: T264's task line.
4. **Do they describe the world here?** Yes: the page read 2026-11-22 records the farmhouse size as a guess, and the band is a tolerance round it.
5. **The order.** After T197's and T265's edits to the same file, which it leaves as they stand.
6. **The exits.** Green: `make claims-owed` without the label flag, impl-drift IN-STEP, `make claims-report` not listing it open. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The flag gone at `make claims-owed` and the claim not open at `make claims-report`, 2026-11-22.
10. **Before moving a constant.** n/a: the band unchanged.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing: not a defect, restate the claim (constitution XIV).

**Found and left?** none.

**Performance work?** no.


### T265 (449 T249's claims re-check, bundle t249-00, 2026-11-22: two DRIFTED claims of the magistrate's manor, `fix: code`, 417 T33's items)

- **Approach**: the county example drew no armory at a quiet seat and stood its granary in the office court beside the hall, its north face level with the hall's (217 to 267 by 92.5 to 119.5 ft, the hall 65.5 to 178.5 by 92.5 to 130.5 ft), measured 2026-11-22 (read from the generated sheet's rects and its `compound.json`). The generator had no garrison-emphasis knob: the four rolled knobs are granary form, main gate form, servants' quarters form and vegetable garden site, and no `armory` stood anywhere in `rust/` or the sheet, measured 2026-11-22 (grep of `rust/` and the spec), so "each roll of the knob" was the program's prose alone: every roll drew no armory, and the granary stood in the office court on every roll.
  - Red first: `gen_tests_parts.rs`'s cart-route test gained an inner-court granary reached from a gate on its own side and refused with the outer gates alone; with `cart_route` walking the outer court alone it failed ("no cart route from a gate to the granary's door"), measured 2026-11-22 (`make rust-test CRATE=rust/mode_a`, 310 passed, 1 failed). `gen_tests_seat.rs` `the_county_example_keeps_an_armory_and_its_granary_behind_the_offices` failed on the old spec ("no armory in the office hall"), measured 2026-11-22 (the same run with the old spec put back, 311 passed, 1 failed).
  - The fix: `ground.rs` walks each building's cart route in its own court, from the gates on that court's side of the divider. The spec: the granary on the inner court's north wall (search start 170 ft, a GUESS, docs/building-programs.md; door on its east face) with a side gate 6 ft wide in the north wall at 232 ft (a GUESS, 0082's drawing page); an armory room 14 x 20 ft at the office hall's west end (its size a GUESS, docs/building-programs.md), the hall 113 to 127 ft (inside its band, `types.json`); the hearing court recentered under the dais (102.5 to 182.5 ft, measured 2026-11-22 (the dais rect on the drawn sheet)) and the two named outer-court grounds beside it re-cut. A new sheet kind `armory` (registry `kinds.rs`, its modal `assets/modals/sheet/armory.md`). The program's knob 4, the walled-enclosure bullet, the manor's research lines and `docs/buildings.md`'s granary entry restated.
  - Room first, measured: a first seat on the inner court's east wall below the guest house needed the compound 42 ft deeper, which put coverage at 26%, under the jin'ya band's 30% (`COVERAGE_BAND`), measured 2026-11-22 (`make pack-audit` on that draw). The north wall's stretch between the house and the shrine held the granary with no growth: coverage 31% and every registered check OK, measured 2026-11-22 (`make pack-audit` on the drawn sheet). The granary now stands 170 to 220 by 3 to 30 ft, north of the office hall (72 to 199 by 92.5 to 130.5 ft), measured 2026-11-22 (the sheet's rects).
  - Green: `make rust-test CRATE=rust/mode_a`, 312 passed, measured 2026-11-22; `make map` REGENERATED clean.
  - The claims re-check (bundles t265-a and t265-b, 2026-11-22) restated what the code does, not the code (constitution XIV): the cart-route claim cites 0082's drawing page for the granary and a GUESS for the stables; the granary's cart gate is split into a cart gate for bulk goods (0082's drawing page) and its place beside the granary (a GUESS); the tax archive's plaster is distinct only from a post-raised granary's slats (an earth-walled kura granary is plastered too, told apart by its label); `docs/buildings.md` gained `Research:` lines for the granary behind the offices (0123) and its own cart gate (a GUESS). The cart walk does not keep off the garden (its courts are passable ground): on the county example it runs between x 220 and 232 ft above y 30 ft, north of the garden's 35.7 ft edge, measured 2026-11-22 (the sheet's `compound.json`), so the words were restated ("need not cross") and the walk left as it is.
  - Firearms (the session's ruling, 2026-11-22): the GM's setting notes say nothing of firearms (grep of /host-l7r-repo/setting/ and gm-assistant's setting/ and cosmology/ for gun, firearm, musket, teppo, arquebus, gunpowder: no match, 2026-11-22), so the map, its pop-ups and its claims name none - Kaibara's gate-range room is a store of arms, the record keeping its gun store as evidence; the session's ruling on how the store is labeled (not a recorded deviation, impl-drift 2026-11-22), stated in `docs/building-programs.md`, the easier route where the setting is silent. The cart-gate check's claim in `ground.rs` restated: any outer-wall gate on the granary's court side satisfies it, the inner court's postern included (impl-drift CANNOT-TELL, 2026-11-22).
  - The `armory` kind's 100th sheet entry moved the registry crate's pinned counts (99 to 100 sheet kinds, 159 to 160 entries): 7 failures, all its own, fixed; `make rust-test CRATE=rust/gate/crates/registry` 23 passed, measured 2026-11-22.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| cart route per court (`ground.rs`) | the inner-court granary refused; pinned by the cart-route test | n/a (a Mode A sheet, no hamlet roll) | county-magistracy-example (ochiba-roundtrip-test's outer granary unchanged, its compose test green) | none |
| the county spec (granary, gate, armory) | no armory, the granary beside the hall; pinned by the county example's test | n/a | county-magistracy-example | none |

### T265 Approach (checklist part A)

1. **The goal, in the world.** A quiet county's magistracy keeps an armory, and its granary stands behind the offices.
2. **The constraints.** 0093 (Kaibara's gate range held a store of arms - the record's gun store; the map, its pop-ups and its claims name no firearm, the session's labeling ruling stated in docs/building-programs.md: the setting's notes say nothing of firearms (grep of /host-l7r-repo/setting/ and gm-assistant's setting/ and cosmology/, 2026-11-22), so the easier route where the record is silent - the session's ruling, 2026-11-22), 0123 (Pingyao: no standing barracks, the armory in the great hall's west end bay, "north of them the county granary"); the program's knobs; the jin'ya coverage band (0116); room first (the GM 2026-10-12).
3. **Where each comes from.** R: 0093, 0123, 0082's drawing page (a cart gate), 0116; G: room first; O: the measurements above.
4. **Do they describe the world here?** The sheet's rects before and after, and `make pack-audit` on each draw, measured 2026-11-22.
5. **The order.** Lands before 449 T158.
6. **The exits.** Green: the new tests green, `make map` clean, `make pack-audit` all OK, the restated claims re-checked IN-STEP. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one seat probed (east wall, refused by coverage), the second fit.
8. **The budget.** One landing.
9. **Done, measured.** The county example's test: an armory room in the hall, the granary's south edge (30 ft) north of the divider (90 ft) and the hall's north face (92.5 ft), measured 2026-11-22 (the drawn sheet's rects and `make rust-test CRATE=rust/mode_a`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** The east-wall seat's room was given first (the compound 42 ft deeper, measured 2026-11-22 (`make compound` on trial specs: 30 ft refused for room, 36 ft seated it but not beside its own gate, 42 ft seated both)); it broke the coverage band, so the north wall's existing room was taken instead.
12. **Before any fix.** A reader sees an armory bay in the office hall and the granary behind the offices, at the rear wall with its own cart gate; both were findings the code broke (0093, 0123).

**Found and left?**
- The granary's seat in the household's inner court is not 0123's reading (Pingyao's stood north of the side-wing offices) and the office reaches it on foot only through the garden's east end; the barracks slid 33 ft north on the east wall into the granary's old seat (753 x 322.5 px against main's 753 x 421.5, measured 2026-11-22 from the two snapshots' svg), leaving about 31 x 31 ft bare in the south-east corner; the shrine's door opens onto the cart apron (building-review 2026-11-22, concluded NEEDS-WORK, E1, E2, Q1). Pinning the barracks back (`near` 125.5) left a 71 x 41 ft perimeter gap where the granary stood instead, measured 2026-11-22 (`make pack-audit` on that draw), so it was put back. The seat is labeled a GUESS in the claims now. Not fixed here: re-siting it is a new seat search across the compound, and the one priced alternative (the east wall) broke the coverage band. Filed as T274; lands before T158.
- size-audit concluded PASS on 14 x 20 ft (its size a GUESS) and set the armory's band, 12-24 x 12-40 ft, observed 2026-11-22, method: size-audit's anchors (Kaibara's eight-mat rooms; a county hall's end bay, an estimate), in `types.json` as an optional item, with two questionables: whether Kaibara's store was one eight-mat room or two, and the hall's back row against Pingyao's full-depth bay. Not fixed here: modal-research held the one-room reading to 0093 and 0097, so each needs a research pass first. Filed as T275; lands before T158.
- The program's audit holds the armory optional (`types.json`) while knob 4 says every seat keeps one: hayakawa-magistracy, ochiba-magistracy, ubame-magistracy and ochiba-roundtrip-test draw none, measured 2026-11-22 (a grep of their svg for the armory kind), so requiring it now turns four sheets red (impl-drift 2026-11-22, `fix: code`). Not fixed here: each is a hand sheet's layout revision with its own review. Filed as T276; lands before T158.
- The notes' stale lines (the barracks unchanged, the band north of the garden open, the archive east of the hall, the hall 113 x 38, the dais centered) restated from the drawn sheet, 2026-11-22: fixed here.

**Performance work?** no.


### T271 (impl-drift on T197's claims, outside its change, 2026-11-22: a town's place card left its drawn farmhouses out of its count, against 0004's drawing page)

- **Approach**: `dwellings_shown` (rust/mode_a/src/place.rs) counts a tier's drawn farmhouses (`houses`) unless the tier excludes farms, and every dwelling-kind building in `buildings` always; place.json's town entry turns `excludes_farms` off, its `houses_noun` from "non-farmhouse dwellings" to "dwellings" and its `population_note` from "Every dwelling of that rest is drawn, and is the number counted above" to "both are counted above". The city, hamlet and village entries are unchanged. The claim "town and city count no farmhouses" is restated as "a town counts its farmhouses, a city none", citing 0004's drawing page's two bullets. Towns in the live pool: none, measured 2026-11-22 (`"scale"` over every pool/**/*.json: five, all `hamlet`); the towns are the legacy pool's three, the held cases' input. Their cards' counts, measured 2026-11-22 (a tally of each manifest's `houses` length and its `buildings` of the ten DWELLING_KINDS, with the town's `default_population` 1,200 outranking each meta's `population`): Hirameki 87 non-farmhouse dwellings before, 166 dwellings after (79 farmhouses + 87); Ubame 82 before, 118 after (36 + 82); Hoshizora 94 before, 136 after (42 + 94); each "population ~1,200" before and after, none declaring households. The cities hold: Minami 520, Tango 583, measured 2026-11-22 (the same tally). The pool hamlets' manifests hold no dwelling-kind building, measured 2026-11-22 (the same tally: 0 in each of five), so a hamlet's count is its `houses` as before.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the town's count | `place::tests::a_town_counts_its_farmhouses_and_a_city_none`, red first on the real place.json (town 2, wanted 4, measured 2026-11-22 (`make rust-test CRATE=rust/mode_a`)), green after (314 passed, measured 2026-11-22 (the same)) | n/a | none: no town or city is in the live pool | n/a |

### T271 Approach (checklist part A)

1. **The goal, in the world.** A town's card counts every dwelling it draws, farmhouses among them; a city's counts its non-farm dwellings only; a hamlet's and a village's their farmhouses.
2. **The constraints.** 0004's drawing page: "A town counts its drawn farmhouses among its dwellings" and "A city counts no farmhouse at all"; its ten dwelling kinds; place.json's other kinds stay as they are.
3. **Where each comes from.** R: research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html; G: the GM's 2026-08-29 ruling that a city's farm fields are not all drawn, as `dwellings_shown`'s comment records it; O: the tally above.
4. **Do they describe the world here?** Yes: the legacy towns draw farmhouses (`houses`: 79, 36, 42) beside their non-farm dwellings, measured 2026-11-22 (the tally above).
5. **The order.** The red test, then the count and place.json, then the claim's impl-drift; before T158.
6. **The exits.** Green: the pin green, `make closing-checks T=T271 F=449` green, the restated claim IN-STEP. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one predicate, one data entry.
8. **The budget.** One landing.
9. **Done, measured.** The pin's town 4 and city 2 on the real place.json; the claim IN-STEP.
10. **Before moving a constant.** n/a: place.json's town flag and words, the claim restated.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of a town's card saw "87 non-farmhouse dwellings" where the sheet draws 166 homes, against 0004's drawing page; it now reads "166 dwellings", and its note no longer says the count is only the non-farm dwellings. Labeled: the "about N households" phrase, gated by the same flag, now follows a town as a hamlet's (a deliberate choice, the algorithmically easier route: 0004's "Where drawn houses and declared households differ, the map's card states both" is general); no legacy town declares households, so no card shows it (measured 2026-11-22, the tally above).

**Found and left?** none

**Performance work?** no


### T273 (449 T247's MODE 4 note, 2026-11-22: the browser crate's test Chromium and the archive crate's stand-in browser server were Python programs the crates' tests started under `make done`, against SC-005's close)

- **Approach**: each Python helper is replaced by its crate's own test binary started again as one test, the self-exec form the guard's `shared` tests already use (`wait/tests.rs`, `tree/tests.rs`): a `#!/bin/sh` launcher written by `install` sets a marker and `exec`s `current_exe()` with `--exact <the stand-in's test> --nocapture -q`; in a plain test run that test sees no marker and returns. No production code changes: both crates still start their browser by path, as they did the Python.
  - What each helper did, measured 2026-11-22 (reading `testkit.rs`'s `FAKE`, `client/tests.rs`'s `SERVE` and every test that starts them, `grep` of the crates' tests for each URL keyword):
    - the fake Chromium, measured 2026-11-22 (its source read, a grep of the crate's tests for `fake_chrome(` and each keyword) (`rust/browser/src/testkit.rs`, `#!/usr/bin/env -S python3 -I -S`): the `DevTools` pipe, NUL-terminated JSON read on fd 3 and written on fd 4, each command answered from a table by method and by keywords in the page's URL (`neterr`, `samedoc`, `noload`, `busy`, `nobody`, `noglyph`, `throw`, `throwplain`, `throwbare`, `big`, `small`, `notready`, `readythrow`, `zoomy`, `stuck`, `novb`, `lateready`, `Fail.me`, `Silent.me`), with a cookie jar, a measure count and a zoom-key count per process; started through `fake_chrome` by 14 tests (their `fake_chrome(` calls) across `cdp`, `chromium`, `page`, `get`, `serve`, `crop`, `lit` and the crate's `tests.rs`. Every keyword has a test that reaches it.
    - the stand-in server, measured 2026-11-22 (its source read and the tests that start it) (`rust/gate/crates/archive/src/client/tests.rs`, `#!/usr/bin/env python3`): `l7r-gate.sh browser serve`'s line protocol, a `{"ready": true}` line, then one JSON line in, one out: `get` writes `body of <url>` to the request's `out` file and answers its status (`slow` 429 then 200) and `<url>#final`, `boom` an error with a call log, `render` an MHTML and text or (`fail`) an error, `junk` a line that is not JSON, `die` an exit before answering, `close` an exit; started by 2 tests (`a_request_and_a_render_through_the_browser_retried_and_spaced`, `a_browser_dropped_while_running_is_closed_then`).
  - The stand-ins: `rust/browser/src/testkit/fake.rs` (`the_fake_chromium`: fd 3 and fd 4 opened as `/dev/fd/3` and `/dev/fd/4`, no `unsafe`; the launch already sends the child's stdout and stderr to `/dev/null`, so the harness's own lines go nowhere) and `client/tests.rs`'s `the_stand_in_server` (stdin read, every op but `get` and `close` answered as a render, the client sending no other; answers on fd 3, the launcher's `3>&1 >/dev/null` keeping the harness's `running 1 test` line off the protocol, which the client reads as its ready line). Each table is the Python's, order kept (`readythrow` before the `throw` case, the `L0` load before `L1`'s, the `{"no": "method"}` message, a null `sessionId` on a browser-level navigation's reply, the 50 ms `lateready` sleep, measured 2026-11-22 (read from the Python's `time.sleep(0.05)`)).
  - Found by the grep of step 3, a third Python start in test code: `rust/gate/crates/land/src/land/alone/tests.rs`'s stub tick, `archive.sh`, ran `python3 -I -c` to cut T1's section out of a plan; now `awk`, the same cut. Fixed here.
  - Green, measured 2026-11-22 (`make rust-test CRATE=` each crate, `l7r-gate.sh rust lint` and `rust cover --crate` each crate, the 12-crate lint red of `make static` being `reviews`' `rows.rs`, 451 T151's, reported apart): browser 32 passed (31 before, the stand-in's entry the 32nd), 1.02 s against 1.00 s before, archive 65 passed (64 before), 0.28 s against 0.19 s; land 87 passed; lint and cover clean on all three, the stand-ins' lines reached by the started copies (`LLVM_PROFILE_FILE`'s `%p` takes each child's profile). Each test alone under FR-008's 0.1 s but the declared real-Chromium test (1.03 s, unchanged), the slowest of the rest 0.086 s, measured 2026-11-22 (`make test-times CRATE=rust/browser`).
  - Red, measured 2026-11-22 (each answer broken once in the working tree, `make rust-test CRATE=`, then restored and diffed equal): the fake's product `FakeChrome/2` failed `cdp::tests::a_command_gets_its_reply...`; its body text `the words of` failed `page::tests::a_page_loads_goes_idle_and_reads_back` and `serve::tests::each_line_is_answered_until_close`; a wrong `ENTRY` (the copy runs no test, answers nothing) failed every test on the fake (7 named in the first lines, `cdp`, `crop`, `lit`, the command line); the stand-in's `#moved` for `#final` failed `a_request_and_a_render_through_the_browser_retried_and_spaced` (left `http://h/page#moved`). A glyph that never grows (`50` for `50 * measured`) stayed green, 32 passed: the grows page asserts only the PNG and the kinds, so its growth steers the zoom loop's lines alone, which the cover run holds - as it was under the Python fake.
  - The grep, measured 2026-11-22 after: `grep -rnE '#!.*python|Command::new\("python' rust --include='*.rs'` (T247's census form, a shebang or a `Command::new`, over every file, tests included) 0 lines (2 before, the two helpers); and a `python3 -c` written into a script a test runs (`put(`, `write_executable`, `executable(`, `script(` on the line) 0 (1 before, land-alone's). The 255 other `python` words in test code, measured 2026-11-22 (`git grep -nwE 'python3?'` of `rust/`'s test files, `//` lines out), are inputs the guards are fed or names in fixtures, never run.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the fake Chromium in Rust | the crate's tests red where its answers move (the red proofs above); pinned by the crate's own tests | n/a (test code, no hamlet roll) | none | none |
| the stand-in server in Rust | the archive client's test red where its answers move; pinned by that test | n/a | none | none |
| land-alone's stub tick in `awk` | its test red where the cut is wrong; pinned by that test | n/a | none | none |

### T273 Approach (checklist part A)

1. **The goal, in the world.** `make done` starts no Python interpreter from a crate's tests: the test helpers that were Python programs are Rust, each test proving what it proved.
2. **The constraints.** SC-005 (`make done` with no Python interpreter), FR-001 (every Python file replaced by Rust), T273's line (every page case kept, the browser crate green, the one real-Chromium test unchanged); constitution XIII (no known regressions).
3. **Where each comes from.** G: SC-005 and FR-001; O: T247's MODE 4 note and the greps above.
4. **Do they describe the world here?** The two helpers read and every test that starts them listed, and the grep of `rust/` test code, measured 2026-11-22.
5. **The order.** Lands before 449 T158.
6. **The exits.** Green: `make rust-test` on the browser, archive and land crates, `make closing-checks T=T273 F=449`, and the grep returning nothing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The two greps above return 0 lines, and the three crates green, lint and cover clean, measured 2026-11-22 (the commands above).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Not a map change: no reader of a map sees anything differently; the defect is SC-005's (a Python start under `make done`).

**Found and left?** none - the third start (land-alone's stub tick) fixed here.

**Performance work?** no.


### T274 (building-review 2026-11-22 on T265's sheet: NEEDS-WORK E1, E2, Q1)

- **Approach**: T265 left the county example's granary in the household's inner court on the north wall (170 to 220 by 3 to 30 ft) with a north cart gate at 232 ft, measured 2026-11-22 (the sheet's svg rects), the office reaching it on foot only through the garden (E1); the barracks slid 33 ft north and left a bare 31 x 31 ft corner (238 to 269 by 168 to 199 ft, E2), measured 2026-11-22 (the sheet's svg rects); the shrine's west door faced the granary's cart apron (Q1) - measured 2026-11-22 from the sheet's svg rects (ft = (svg - 21) / 3, (svg - 45) / 3). The record: 0123's Pingyao (the archived baike page, `make archive-find KEY=pingyao-yamen`) built office buildings behind its war, justice and works offices "and north of them the county granary" - on the office side, the residence behind the great hall; no `0597` exists under research/ (grep, 2026-11-22).
  - Red first: `ground.rs::cart_route` refuses a granary in the household's court; `gen_tests_ground.rs::a_granary_stands_on_the_offices_side_of_the_divider` (an inner granary refused whatever its gates, an office-court granary behind a hall reached) and the county example's own test (granary in the office court) failed on T265's sheet, and `gen_tests_seat.rs::no_court_of_a_pool_sheet_leaves_a_corner_bare` fails on T265's barracks seat (its south-east corner named), measured 2026-11-22 (`make rust-test CRATE=rust/mode_a`: 13 failed, the sheet refused, before the spec moved).
  - Room first, measured and left: the hall drawn 27 to 33 ft forward of the divider with the granary behind it (the envelope 227 to 233 ft deep) drew coverage at 27% (`COVERAGE_BAND`, `make pack-audit`, 2026-11-22); at the 30% floor each foot of depth owes 81 sq ft of building (270 x 0.30), about 1,050 to 1,450 sq ft no program building pays, measured 2026-11-22 (`make pack-audit` on the 227 and 233 ft draws). The clerks' rowhouse 0097 attests at a jin'ya paid it (30%, every check OK, measured 2026-11-22 (`make pack-audit`)) but contradicts the commuting clerks CANON (docs/building-programs.md), so it was withdrawn; the staff-housing knob's recorded value is (a), so a samurai rowhouse would be a choice, not a roll. A jogged divider (a flank court) and a new office kind were priced and left.
  - The fix (the spec): the granary at the head of the office court's east column (217 to 267 by 92.5 to 119.5 ft), its door on its west face, a GUESS recorded on 0123's drawing page through a page session (briefs t274-write.md, t274-checks.md: 0123 seats Pingyao's granary north of the office buildings behind its war, justice and works offices, a seat relative to side-wing offices, and this plan's offices are rooms of one hall on the divider, so nothing on the sheet stands where those offices stood; north of the hall is the household's court, refused; the flank column's head beside the hall's end is the office side's nearest ground), the room priced in docs/building-programs.md; the north gate dropped; the barracks back below it (125.5 to 195.5 ft, measured 2026-11-22 (the sheet's svg rects)) in the south-east corner; the office hall centered in its free ground (58.5 to 185.5 ft) and the hearing court with the outer court's two grounds re-cut 14 ft west under the dais, measured 2026-11-22 (the sheet's svg rects). Q1 resolved by removal; the research pass (2026-11-22) found no source seating a yashikigami before a work yard (NOT ATTESTED).
  - Green, measured 2026-11-22 (the runs' own output): `make rust-test CRATE=rust/mode_a` 315 passed; `make map` REGENERATED; `make pack-audit` coverage 31%, every registered check OK, measured 2026-11-22 (`make pack-audit` on the drawn sheet).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the inner-court granary refused (`ground.rs`) | T265's sheet refused; pinned by the open-ground test | n/a (a Mode A sheet, no hamlet roll) | county-magistracy-example (ochiba-roundtrip-test's outer granary unchanged, its compose test green) | none |
| the county spec (granary, barracks, hall, hearing court) | T265's layout; pinned by the county test and the corner test | n/a | county-magistracy-example | none |

### T274 Approach (checklist part A)

1. **The goal, in the world.** The county seat's granary stands on the office side, reached by the office and by carts without crossing the household; no bare corner; the household's shrine fronts no cart apron.
2. **The constraints.** 0123 (Pingyao's granary north of the office buildings behind its war, justice and works offices); 0090 (two courts, a DEVIATION); 0116 (coverage 30-42%, the record's band, research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.html); the commuting clerks CANON; room first (the GM 2026-10-12).
3. **Where each comes from.** R: 0123, 0090, 0097, 0116, 0218; G: the CANON staffing anchor; O: pack-audit and the svg rects.
4. **Do they describe the world here?** Pingyao is one county's arrangement (its source's limits); the sheet has no side-wing offices, so the seat is a GUESS on 0123's drawing page, not the record's reading.
5. **The order.** The tests red, then the spec, then the claims restated and re-checked, then building-review.
6. **The exits.** Green: the crate green, pack-audit all OK, building-review clearing E1, E2, Q1. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Three seats tried in order (the hall forward 33 ft, then 27 ft with a clerks' rowhouse, then the column head), measured 2026-11-22 (`make pack-audit` on each draw); each failure recorded above.
8. **The budget.** One landing.
9. **Done, measured.** E1, E2 and Q1 judged on the drawn sheet by building-review; the claims judged by impl-drift, observed 2026-11-22, method: their verdicts recorded (`make review-verdict`, `make claims-checked`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** Room given first (227 and 233 ft deep envelopes, measured 2026-11-22 (`make pack-audit` on each draw)), left on the coverage floor's measurement.
12. **Before any fix.** A reader sees the granary at the office court's north-east corner, not in the household's court; the south-east corner holds the barracks; the shrine faces open ground.

**Found and left?**
- The granary at the head of the east column beside the office hall's end, not north of side-wing offices as Pingyao's was (the plan draws none): a GUESS on 0123's drawing page with its room priced (docs/building-programs.md), not a defect once labeled (constitution XIV); a flank court (a jogged divider) or wing offices would be new engine geometry, not filed.

**Performance work?** no

### T275 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T275 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T276 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T276 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T277 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T277 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T278 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T278 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T279 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T279 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T280 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T280 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T281 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T281 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T282 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T282 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T283 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T283 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T284 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T284 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T285 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T285 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T286 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T286 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T287 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T287 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

