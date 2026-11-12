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
