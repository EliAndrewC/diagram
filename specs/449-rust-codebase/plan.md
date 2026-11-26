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
<!-- plan-archive: T162 to T160 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
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
<!-- plan-archive: T194 to T187 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T162 to T194 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T203 to T209 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T216 to T212 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
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
<!-- plan-archive: T235 to T226 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T240 to T239 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T241 to T239 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
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


<!-- plan-archive: T244 to T244 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T246 to T142 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
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


<!-- plan-archive: T249 to T241 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T250 to T240 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T251 to T228 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T252 to T228 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T259 to T277 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->

<!-- plan-archive: T261 to T249 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T263 to T249 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T264 to T249 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
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


<!-- plan-archive: T271 to T197 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T273 to T247 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T274 to T265 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T275 to T288 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->






<!-- plan-archive: T260 to T287 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
### T158, T197, T203, T216, T228, T235, T240, T241, T243, T244, T246, T247, T248, T249, T250, T251, T253, T254, T255, T256, T257, T258, T261, T262, T263, T264, T265, T266, T267, T268, T269, T270, T271, T272, T273, T274 part B (2026-11-22T13:33Z)

One answer for every task the red-gate@2026-11-22T13:29:06Z tripwire charged (the round arbiter ruled accept, 2026-11-22): the two red gates were one hooks-test failure settled before the second run, then a format slip in a test this session added to the plan crate, nothing in any of these tasks' own work.

1. **What exactly is refusing?** `make done`'s static phase, `rust-checks: format FAILED on rust/gate/crates/plan`: one test, `a_bundle_approach_block_covers_every_task_its_heading_lists` in `rust/gate/crates/plan/src/plan/lint/tests.rs`, written past rustfmt's width, observed 2026-11-22 (the verify gate's log). The earlier red, hooks-test at 900bf1ad55, did not recur.
2. **A3 again, for that rule.** O: rustfmt's own check, the gate's; nothing of the research or the GM's words.
3. **A4 again.** Yes: the line was over width; the gate's format step rewrote it (46af955365).
4. **Is the next fix moving something placed earlier to suit something placed later?** No: a formatting rewrite of one test.
5. **Tuning or changing?** Neither: no tuning; one rewrite.
6. **The one-sentence test.** "A test was reformatted to rustfmt's width" - no question to answer first.
7. **The next step is a measurement.** `make static`, then `make verify` on the rewritten tree: the format check green.
8. **Before offering routes.** No routes: nothing to choose.
9. **After a ruling.** The ruling (accept) names the next step, `make done` under `make verify` again, and that is the step taken.

<!-- plan-archive: T289 to T300 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T292 to T303 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T302 to T311 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T312 to T326 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T317 to T327 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T328 to T340 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T330 to T333 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T341 to T350 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T342 to T349 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T351 to T368 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T358 to T370 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T371 to T385 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T374 (withdrawn: moved to 452 T007 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T007 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T374 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T007 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T007 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T007 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T007 from 449 T374; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T007's.

**Found and left?** none - the task moved whole to 452 T007.

**Performance work?** no.


<!-- plan-archive: T375 to T402 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T399 to T403 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
### T380 (withdrawn: moved to 452 T015 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T015 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T380 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T015 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T015 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T015 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T015 from 449 T380; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T015's.

**Found and left?** none - the task moved whole to 452 T015.

**Performance work?** no.


<!-- plan-archive: T383 to T391 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T386 (withdrawn: moved to 452 T001 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T001 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T386 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T001 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T001 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T001 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T001 from 449 T386; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T001's.

**Found and left?** none - the task moved whole to 452 T001.

**Performance work?** no.


### T387 (withdrawn: moved to 452 T002 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T002 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T387 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T002 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T002 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T002 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T002 from 449 T387; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T002's.

**Found and left?** none - the task moved whole to 452 T002.

**Performance work?** no.


### T389 (withdrawn: moved to 452 T003 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T003 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T389 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T003 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T003 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T003 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T003 from 449 T389; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T003's.

**Found and left?** none - the task moved whole to 452 T003.

**Performance work?** no.


### T390 (withdrawn: moved to 452 T008 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T008 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T390 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T008 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T008 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T008 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T008 from 449 T390; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T008's.

**Found and left?** none - the task moved whole to 452 T008.

**Performance work?** no.


### T393 (withdrawn: moved to 452 T009 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T009 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T393 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T009 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T009 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T009 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T009 from 449 T393; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T009's.

**Found and left?** none - the task moved whole to 452 T009.

**Performance work?** no.


### T396 (withdrawn: moved to 452 T010 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T010 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T396 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T010 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T010 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T010 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T010 from 449 T396; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T010's.

**Found and left?** none - the task moved whole to 452 T010.

**Performance work?** no.


### T404 (withdrawn: moved to 452 T004 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T004 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T404 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T004 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T004 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T004 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T004 from 449 T404; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T004's.

**Found and left?** none - the task moved whole to 452 T004.

**Performance work?** no.


### T405 (withdrawn: moved to 452 T005 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T005 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T405 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T005 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T005 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T005 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T005 from 449 T405; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T005's.

**Found and left?** none - the task moved whole to 452 T005.

**Performance work?** no.


### T406 (withdrawn: moved to 452 T016 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T016 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T406 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T016 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T016 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T016 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T016 from 449 T406; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T016's.

**Found and left?** none - the task moved whole to 452 T016.

**Performance work?** no.


### T408 (withdrawn: moved to 452 T006 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T006 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T408 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T006 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T006 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T006 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T006 from 449 T408; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T006's.

**Found and left?** none - the task moved whole to 452 T006.

**Performance work?** no.


### T410 (withdrawn: moved to 452 T017 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T017 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T410 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T017 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T017 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T017 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T017 from 449 T410; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T017's.

**Found and left?** none - the task moved whole to 452 T017.

**Performance work?** no.


### T411 (withdrawn: moved to 452 T011 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T011 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T411 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T011 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T011 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T011 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T011 from 449 T411; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T011's.

**Found and left?** none - the task moved whole to 452 T011.

**Performance work?** no.


### T412 (withdrawn: moved to 452 T012 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T012 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T412 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T012 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T012 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T012 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T012 from 449 T412; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T012's.

**Found and left?** none - the task moved whole to 452 T012.

**Performance work?** no.


### T413 (withdrawn: moved to 452 T013 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T013 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T413 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T013 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T013 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T013 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T013 from 449 T413; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T013's.

**Found and left?** none - the task moved whole to 452 T013.

**Performance work?** no.


### T414 (withdrawn: moved to 452 T014 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md))

- **Approach**: none in 449 - the task moved to 452 T014 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md), with its full text and evidence; its plan is 452's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| withdrawn | n/a: nothing built in 449 | n/a | none | n/a |

### T414 Approach (checklist part A)

1. **The goal, in the world.** n/a in 449: the task moved to 452 T014 unbuilt (the GM 2026-11-24, specs/452-building-plan-followups/request.md); 452 T014 states it.
2. **The constraints.** The GM's request of 2026-11-24 (specs/452-building-plan-followups/request.md).
3. **Where each comes from.** G: the GM 2026-11-24, "can we move all 17 of those into their own separate feature?"
4. **Do they describe the world here?** n/a: no map changes in 449.
5. **The order.** Withdrawn before T158, so 449 closes on its port.
6. **The exits.** Green: the line ticked withdrawn and 452 T014 filed. Red: n/a.
7. **The search smell.** None.
8. **The budget.** None of its own.
9. **Done, measured.** 452's tasks.md carries T014 from 449 T414; `make speckit-todo` no longer counts it open on 449.
10. **Before moving a constant.** n/a: no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a: nothing fixed in 449; the fix is 452 T014's.

**Found and left?** none - the task moved whole to 452 T014.

**Performance work?** no.


<!-- plan-archive: T415 to T415 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T416 to T416 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
### T417 (found by 449 T415, spec-fidelity 2026-11-24: the live seat stage kept a clustered village's belt ground on every settlement form, so the pool's two row hamlets, Kashikawa and Mizuguchi, were seated with a belt's ground kept, where 0031's drawing page has a row or a scattered settlement draw a grove at each farm and no village belt; split by the GM 2026-11-25 - the groves are T438; observed 2026-11-24, method: T415's spec-fidelity read of the seat stage against 0031's drawing page)

- **Approach**: the seat stage reads the settlement form. One predicate, `plan::keeps_belt` (a `nucleated` form, or a form the table does not name, keeps the belt; `linear` and `dispersed` do not), is read once in `stage_seat` (the comb's and the polder's seat alike) into `SeatIn::belt`, and the seat hands it on to every frame (`Frame::belt`), so every reader of the settlement's ground - the dry hem, the placeholder drawn, the map checks `dry_on_settlement`, `seat_on_dike` and `seat_on_canal` - sees the same ground. Where the belt is off: `margins::ranked` asks no belt's room (no `belt_off` refusal, no score against it) and stands no band off a windward field for one (the hill-backed `lead`); `settlement_ground` is the band alone, from the margin to its back, with no belt swept and no strip behind it; `seat_room` keeps no `BELT_REACH`, so the canvas is smaller. Measured 2026-11-25 with a throwaway sweep mode of the hamlet binary run through `make cohort` (T426's 41,000 rolls: 20,000 cohort combs from 10,000,000, 300,000,000, 555,555,000, 777,000,000 and 941,239,000; 6,000 polders, 1,000 of each form from 10,000,000, 300,000,000 and 555,555,000; seeds 1 to 1,500 at T426's ten size and fall pairs), one line a roll - its form, canvas, refusal, broken checks, band share on the paddy, the nearest dry plot to the band and the seat's center - before = HEAD, after = the code as built; the sweep mode is removed.
  - **Before and after, over the 41,000 rolls** (20,744 clustered, 12,269 scattered, 7,987 row), measured 2026-11-25 (the sweep):

    | | refused | a map check broken | bands on the paddy (worst share) | canvas, mean side (row / scattered) | seats moved | nearest dry plot to the band moved |
    |---|---|---|---|---|---|---|
    | before, measured 2026-11-25 (the sweep) | 0 | 0 | 6,790 (3.69 percent) | 5,562 / 5,572 ft | - | - |
    | after, measured 2026-11-25 (the sweep) | 0 | 0 | 6,790 (3.69 percent) | 5,280 / 5,291 ft | 1,018 (405 row, 613 scattered), all declared falls into the wind (725 at 225 degrees, 268 at 200, 21 at 270, 4 at 180), each 145 to 147 ft nearer its field | 3,449 rolls (1,375 row, 2,074 scattered), a median 40 ft nearer, the most 215 ft |

  - **The clustered villages are untouched**: all 20,744 clustered rolls' lines are identical before and after (canvas, seat, hem, checks), measured 2026-11-25 (the sweep).
  - **The seats that moved** are the hill-backed seats of a row or a scattered settlement on a declared fall into the wind: before, the band stood the belt's far edge (146 ft, `BELT_BAND`'s GUESS) further off a windward field for a belt the settlement never draws, measured 2026-11-25 (the sweep); now it stands at the standoff, as every other seat does. No other seat moved once the canvas's shift is taken out: no margin had been refused for a belt's room alone on these rolls, measured 2026-11-25 (the sweep, each seat's center less half the canvas's change).
  - **The pool**, measured 2026-11-25 (`make map` on each, before and after, the records and the renders compared): Kashikawa (seed 3, row) and Mizuguchi (seed 23, row) regenerated in the foreground: the canvas 6,450 to 6,250 ft and 5,050 to 4,750 ft, the seat on the same margin at the same place on its field, the settlement's ground the band alone (Kashikawa's strip behind it 146 ft shorter; Mizuguchi's belt wrapped round the band's windward end gone), the dry hem as before - neither's hem stood in the strip, measured 2026-11-25 (the renders compared). Crops: `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/kashikawa-before-after.png`, `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/mizuguchi-before-after.png`. Inashiro (pinned nucleated), Sawada and Kuwabata roll clustered and do not move.
  - **The work budget**: `make work-budget` is identical to HEAD's on every stage (seat 20,809 / 29,141 / 42,701 / 68,507 ops, hem 7,541 / 11,760 / 18,465 / 30,411), measured 2026-11-25 (HEAD's in a detached worktree): the budget's reference hamlet pins `nucleated`, so no stage moves and no step is owed; the row and scattered path is not in the budget's counts (it does less work - no `belt_off`, no swept ground).
  - `make seeds`: the pool empty, 600 fresh seeds of the three forms, 0 failed, measured 2026-11-25.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the seat reads the form: no belt's room, ground or reach for a row or a scattered settlement | red first: `driver::tests::a_row_or_a_scattered_hamlet_keeps_no_clustered_village_s_belt` failed on HEAD's code ("linear: the ground reaches 392.7 ft out, its band's back 246.7"), green after, measured 2026-11-25 (`make rust-test CRATE=rust/phases`); `seat::tests` pin the belt-off margin kept and no band stood off for a belt; `plan` tests pin the smaller room | n/a: no repair step deleted; the 41,000 rolls above, 0 refused before and after | Kashikawa and Mizuguchi (`.driver.json`, `.driver.svg`, gitignored renders) | n/a |

### T417 Approach (checklist part A)

1. **The goal, in the world.** A row or a scattered hamlet is seated and drawn with no clustered village's shelter belt: no ground kept for one behind or round its houses, no band stood off its field for one, no canvas widened for one; a clustered village keeps all three as before.
2. **The constraints.** 0031's drawing page ("Where farms carry their own groves, no village shelter belt is drawn"); 0072's drawing page for the clustered village's belt, unchanged; constitution XIV (a wrong outcome fixed); the GM's split of 2026-11-25 (the groves are T438).
3. **Where each comes from.** R: research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html; G: the GM's split of 2026-11-25, recorded at T438 in tasks.md; O: the sweep and the pool regenerations above.
4. **Do they describe the world here?** Yes: 0031 rules by form, and the plan's `settlement_form` knob is that form (half clustered, three in ten scattered, two in ten rows, 0031's shares); the pool's two row hamlets roll `linear`, measured 2026-11-25 (their records).
5. **The order.** After T415 (which found it); before T438 (the groves, with the homesteads stage) and T158.
6. **The exits.** Green: no row or scattered roll keeps belt ground, every clustered roll unchanged, no roll refused or breaking a check over the 41,000. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the research switch is deferred (no research pass); 0031 states the rule, and the one choice it is silent on is labeled UNRESEARCHED below.
8. **The budget.** One landing.
9. **Done, measured.** The sweep's after row above: 0 refused, 0 checks broken, clustered lines identical, no belt ground on 20,256 row and scattered rolls, measured 2026-11-25 (the sweep) (the test pins it on a constructed row and scattered spec).
10. **Before moving a constant.** No constant moves: `BELT_REACH`, `BELT_BAND` and `BELT_FAR_FT` keep their figures and now apply to a clustered village alone; their claims restated to say so (`seat_room`, `settlement_ground`'s back strip, `ranked`'s belt claims).
11. **Before fitting things into room.** The canvas shrinks by the belt's reach for a row or a scattered settlement; measured that no roll is refused for it (0 of 20,256, the sweep), so no room is owed back.
12. **Before any fix.** A reader of a row or a scattered hamlet's map sees the settlement's dashed ground as the band alone - no strip a belt's depth behind it, no wrap round its windward end - and, on a fall into the wind, the band 146 ft (`BELT_BAND`'s GUESS) nearer its field, measured 2026-11-25 (the sweep); the dry hem may stand up to the band's back (40 ft nearer on the median roll that moved, measured 2026-11-25 (the sweep)). It breaks 0031's drawing page's rule no longer.
    - **Decision (a): how much ground a row's or a scattered farm's own grove keeps past the band - none (UNRESEARCHED, the algorithmically easier route).** The record does not say how deep behind a farm its own grove stands; the band is sized by the homestead ground (`HOMESTEAD_GROUND_FT`), which T438 draws the groves in. Labeled UNRESEARCHED in the claim at `settlement_ground`; a knob for T438 if its groves need more.
    - **Decision (b): a form the table does not name keeps the belt.** `keeps_belt` names the two forms 0031 rules out; any other (a hand-written spec's typo, the empty string) keeps the stage's behavior before this task. The easier route, and no spec in the pool names another.
    - **Decision (c): `BACK_DEPTHS` (2.6 band depths, "the cluster and its belt") is left alone**: the live driver hands the seat no dry plots (`plots: Vec::new()`, the hem laid after it), so the back's share is never read; it acts on nothing here.

**Found and left?** none

**Performance work?** no


<!-- plan-archive: T418 to T416 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T418 to T418 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T420 to T420 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
### T425 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T425 Approach (checklist part A)

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
12. **Before any fix.** No map changes: T425 is page work only. Its untrue sentences were findings against the research record (the 2026-11-24 wording audit), each written true in page sessions P1-P13 with their record checks and cascades; the code-labeled guesses whose page was silent (P13 items e and f, P14) went to `make research-backlog` under 451 T236 (the GM, 2026-11-25), not fixed here because a guess the page does not record is not a wrong map.

**Found and left?** - Not fixed here: 0057's and 0031's sentences that 449 T432 left behind the code (found 2026-11-25 by T432's claims round). Filed as T436; lands before T158.

**Performance work?** no


<!-- plan-archive: T426 to T426 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T427 to T427 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
### T428 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T428 Approach (checklist part A)

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
12. **Before any fix.** No map changes: the search (page session P12) found the record holding what the code draws - 0006's drawing page has each plot a rectangle square to the canal where it stands, tapering at a bend - so the bend taper (PINCH_SHARE, 449 T423) stands, and the comment naming a GM ruling the GM never made is gone from rust/phases/src/field/dry.rs. Not a defect in the drawing; the claim was restated (constitution XIV).

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T429 to T429 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T430 to T427 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T430 to T430 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T431 to T427 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T431 to T431 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T433 to T433 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T434 to T433 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T434 to T434 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T435 to T434 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T435 to T435 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->

### T436 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T436 Approach (checklist part A)

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
12. **Before any fix.** No map changes: T436 is page wording only (page session P15, 2026-11-25) - 0057 and 0031 restated to what 449 T432 draws; its cascade restated three toe.rs claim comments (no code) and three pop-ups (hamlet/marsh, choice/cluster_position--high_margin, choice/settlement_form--nucleated) whose words the new pages contradicted.

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T437 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T437 Approach (checklist part A)

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


### T438 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T438 Approach (checklist part A)

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


### T439 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T439 Approach (checklist part A)

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

