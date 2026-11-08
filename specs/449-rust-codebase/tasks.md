# Tasks - feature 449, a Rust codebase (phase 1: the guards)

Phases 2-4 are planned to the task in their own plan amendments (plan.md, Summary). Every task here is tooling: a map convention with
nothing behind it in physical reality, so each is `research: rendering`.

## Occasions

- none: phase 1 moves the guards that run on Claude Code's tool calls; no map feature, glyph, placement rule or research page changes.

## Tasks

### Setup (plan work breakdown 1)

- [x] T001 The Cargo workspace: `rust/Cargo.toml` with the members `phases` and `guard`, `rust/guard/` created with its `CLAUDE.md` index; `scripts/gates/rust_checks.py` finds and checks every member (`make rust-test`, `make static`'s lint, format, cover and dead over both), each crate's summary printed
      research: rendering

### Foundational (plan work breakdown 2-4; blocks every guard)
      verify: DONE. landed in batch T001+T002+T003+T004+T005: the Rust guard foundation: the workspace, the protocol, the shared library, the wrapper and the settings switch with an empty guard list (4.7 ms a Bash call, m:dispatcher-floor)

- [x] T002 The protocol, `rust/guard/src/protocol.rs` and `main.rs` (contracts/guard-protocol.md): the input parsed once, the answers (allow, refuse, rewrite, notice, stop-block), the merge in the fixed order (plan D2), the exit codes; `l7r-guard <event>`, `l7r-guard --only <guard> <event>` and `l7r-guard --self-check`; with no guard registered every event allows; unit tests of every merge case, each under a tenth of a second
      research: rendering
      verify: DONE. landed in batch T001+T002+T003+T004+T005: the Rust guard foundation: the workspace, the protocol, the shared library, the wrapper and the settings switch with an empty guard list (4.7 ms a Bash call, m:dispatcher-floor)
- [x] T003 The shared library, `rust/guard/src/shared/` (plan D5, D6): the guard log written in `scripts/hooks/lib/guardlog.sh`'s line format (a line read back by `make guard-log` as the shell's is), the escape tokens and their two-word reason rule (`hm_escape.py`), the session's clone and name (`clone-sync-hooks.sh`'s map), the transcript's GM messages, the facts asked once a process and handed to every decider, each read counted in a test
      research: rendering
      verify: DONE. landed in batch T001+T002+T003+T004+T005: the Rust guard foundation: the workspace, the protocol, the shared library, the wrapper and the settings switch with an empty guard list (4.7 ms a Bash call, m:dispatcher-floor)
- [x] T004 The wrapper, `scripts/hooks/l7r-guard.sh` (plan D7): runs the binary built from its own tree, builds it first when its sources are newer, keeps each build that passes `--self-check` as the last good one and runs that one when a build fails to compile or fails its self-check, and only with none ever built lets the call through with a notice and a guard-log line (`outcome=failed-open`); its suite `tests/hooks/test-l7r-guard.sh`: a stale build rebuilt, a broken build falling back to the last good binary, no binary failing open
      research: rendering
      verify: DONE. landed in batch T001+T002+T003+T004+T005: the Rust guard foundation: the workspace, the protocol, the shared library, the wrapper and the settings switch with an empty guard list (4.7 ms a Bash call, m:dispatcher-floor)
- [x] T005 The settings switch landed empty: `.claude/settings.json` calls `scripts/hooks/l7r-guard.sh <event>` once for each event beside the existing guards, its guard list empty, each entry's timeout above the wrapper's build limit (`L7R_GUARD_BUILD_SECS`, 45 s): T004 measured a clone's first build at 5.7 s idle and 19.1 s with every core busy, past the 10 s most entries carry, and a crate-only rebuild at 1.0 s; the wrapper's hot path, empty, at 3.8 ms a call; `m:hooks-bash`'s command re-run with it in place, the dispatcher's own cost recorded as phase 1's floor; landed alone with `make land-tooling` so every session runs it
      research: rendering

### User Story 1 - every tool call answers at once (plan work breakdown 5, 7)

Each guard task, in the order below (the measured cost first, research R2, then the settings' order): the guard's decider in `rust/guard/src/guards/<guard>.rs` with its unit tests; its suite `tests/hooks/test-<guard>.sh` run with `HOOK` pointed at `l7r-guard --only <guard>` until every case passes (a case whose verdict changes is a constitution XIV fix, named in the commit - FR-002), the suite's own inline Python replaced in the same task (plan work breakdown 7); then, in ONE commit, the decider registered, `scripts/hooks/<guard>.sh` deleted and its `.claude/settings.json` entry removed (FR-003), landed with `make land-tooling`.
      verify: DONE. landed in batch T001+T002+T003+T004+T005: the Rust guard foundation: the workspace, the protocol, the shared library, the wrapper and the settings switch with an empty guard list (4.7 ms a Bash call, m:dispatcher-floor)

- [x] T006 [US1] `pair-hooks`: its decider `rust/guard/src/guards/pair_hooks.rs`, its suite `tests/hooks/test-pair-hooks.sh` replayed against `l7r-guard --only pair-hooks`, then `scripts/hooks/pair-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: pair-hooks is Rust: its suite's 100 cases green against l7r-guard, the shell deleted; a Bash ls 200 ms -> 6.8 ms (m:pair-hooks-ported)
- [x] T007 [US1] `gate-hooks`: its decider `rust/guard/src/guards/gate_hooks.rs`, its suite `tests/hooks/test-gate-hooks.sh` replayed against `l7r-guard --only gate-hooks`, then `scripts/hooks/gate-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: gate-hooks is Rust: 45 of 45 suite cases green against l7r-guard, the shell deleted; a Bash ls 111.6 ms -> the dispatcher's 5.5 ms (m:gate-hooks-ported)
- [x] T008 [US1] `measure-hooks`: its decider `rust/guard/src/guards/measure_hooks.rs`, its suite `tests/hooks/test-measure-hooks.sh` replayed against `l7r-guard --only measure-hooks`, then `scripts/hooks/measure-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: measure-hooks is Rust: 48 of 48 suite cases green against l7r-guard, the shell deleted; a Bash ls 74.0 ms -> the dispatcher's 7.3 ms (m:measure-hooks-ported)
- [x] T009 [US1] `no-poll-hooks`: its decider `rust/guard/src/guards/no_poll_hooks.rs`, its suite `tests/hooks/test-no-poll-hooks.sh` replayed against `l7r-guard --only no-poll-hooks`, then `scripts/hooks/no-poll-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: no-poll is Rust: 115 of 115 suite cases green against l7r-guard, the shell deleted; a Bash ls 57.4 ms -> the dispatcher's 8.4 ms (m:no-poll-hooks-ported)
- [x] T010 [US1] `main-tree-hooks`: its decider `rust/guard/src/guards/main_tree_hooks.rs`, its suite `tests/hooks/test-main-tree-hooks.sh` replayed against `l7r-guard --only main-tree-hooks`, then `scripts/hooks/main-tree-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: main-tree is Rust: 87 of 87 suite cases green against l7r-guard, the shell deleted; a Bash ls 60.7 ms -> the dispatcher's 10.5 ms (m:main-tree-hooks-ported)
- [ ] T011 [US1] `record-edit-hooks`: its decider `rust/guard/src/guards/record_edit_hooks.rs`, its suite `tests/hooks/test-record-edit-hooks.sh` replayed against `l7r-guard --only record-edit-hooks`, then `scripts/hooks/record-edit-hooks.sh` and its settings entry removed
      research: rendering
- [x] T012 [US1] `event-log-hooks`: its decider `rust/guard/src/guards/event_log_hooks.rs`, its suite `tests/hooks/test-event-log-hooks.sh` replayed against `l7r-guard --only event-log-hooks`, then `scripts/hooks/event-log-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: the event log is Rust: 18 of 18 suite cases green, its lines byte-identical to the Python's; a Bash ls 32.9 ms -> the dispatcher's 12.4 ms (m:event-log-hooks-ported)
- [x] T013 [US1] `clone-sync-hooks`: its decider `rust/guard/src/guards/clone_sync_hooks.rs`, its suite `tests/hooks/test-clone-sync-hooks.sh` replayed against `l7r-guard --only clone-sync-hooks`, then `scripts/hooks/clone-sync-hooks.sh` and its settings entry removed - its solo skip (`scripts/hooks/lib/solo.py`, feature 444 T36) carried into the decider
      research: rendering
      verify: DONE. landed: clone-sync is Rust; resolve stays shell until T051
- [x] T014 [US1] `idle-tests-hooks`: its decider `rust/guard/src/guards/idle_tests_hooks.rs`, its suite `tests/hooks/test-idle-tests-hooks.sh` replayed against `l7r-guard --only idle-tests-hooks`, then `scripts/hooks/idle-tests-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: idle-tests is Rust
- [x] T015 [US1] `agent-stall-hooks`: its decider `rust/guard/src/guards/agent_stall_hooks.rs`, its suite `tests/hooks/test-agent-stall-hooks.sh` replayed against `l7r-guard --only agent-stall-hooks`, then `scripts/hooks/agent-stall-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: agent-stall is Rust
- [x] T016 [US1] `stall-watchdog-hooks`: its decider `rust/guard/src/guards/stall_watchdog_hooks.rs`, its suite `tests/hooks/test-stall-watchdog-hooks.sh` replayed against `l7r-guard --only stall-watchdog-hooks`, then `scripts/hooks/stall-watchdog-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: stall-watchdog is Rust
- [x] T017 [US1] `finished-run-hooks`: its decider `rust/guard/src/guards/finished_run_hooks.rs`, its suite `tests/hooks/test-finished-run-hooks.sh` replayed against `l7r-guard --only finished-run-hooks`, then `scripts/hooks/finished-run-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: finished-run is Rust
- [x] T018 [US1] `engine-freeze-hooks`: its decider `rust/guard/src/guards/engine_freeze_hooks.rs`, its suite `tests/hooks/test-engine-freeze-hooks.sh` replayed against `l7r-guard --only engine-freeze-hooks`, then `scripts/hooks/engine-freeze-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: engine-freeze is Rust
- [x] T019 [US1] `gm-tree-hooks`: its decider `rust/guard/src/guards/gm_tree_hooks.rs`, its suite `tests/hooks/test-gm-tree-hooks.sh` replayed against `l7r-guard --only gm-tree-hooks`, then `scripts/hooks/gm-tree-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: gm-tree is Rust
- [x] T020 [US1] `batching-hooks`: its decider `rust/guard/src/guards/batching_hooks.rs`, its suite `tests/hooks/test-batching-hooks.sh` replayed against `l7r-guard --only batching-hooks`, then `scripts/hooks/batching-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: batching is Rust
- [x] T021 [US1] `no-branch-hooks`: its decider `rust/guard/src/guards/no_branch_hooks.rs`, its suite `tests/hooks/test-no-branch-hooks.sh` replayed against `l7r-guard --only no-branch-hooks`, then `scripts/hooks/no-branch-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: no-branch is Rust
- [x] T022 [US1] `discard-hooks`: its decider `rust/guard/src/guards/discard_hooks.rs`, its suite `tests/hooks/test-discard-hooks.sh` replayed against `l7r-guard --only discard-hooks`, then `scripts/hooks/discard-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: discard is Rust
- [x] T023 [US1] `conflict-marker-hooks`: its decider `rust/guard/src/guards/conflict_marker_hooks.rs`, its suite `tests/hooks/test-conflict-marker-hooks.sh` replayed against `l7r-guard --only conflict-marker-hooks`, then `scripts/hooks/conflict-marker-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: conflict-marker is Rust
- [x] T024 [US1] `gate-write-hooks`: its decider `rust/guard/src/guards/gate_write_hooks.rs`, its suite `tests/hooks/test-gate-write-hooks.sh` replayed against `l7r-guard --only gate-write-hooks`, then `scripts/hooks/gate-write-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: gate-write is Rust
- [x] T025 [US1] `feature-approval-hooks`: its decider `rust/guard/src/guards/feature_approval_hooks.rs`, its suite `tests/hooks/test-feature-approval-hooks.sh` replayed against `l7r-guard --only feature-approval-hooks`, then `scripts/hooks/feature-approval-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: feature-approval is Rust
- [x] T026 [US1] `budget-change-hooks`: its decider `rust/guard/src/guards/budget_change_hooks.rs`, its suite `tests/hooks/test-budget-change-hooks.sh` replayed against `l7r-guard --only budget-change-hooks`, then `scripts/hooks/budget-change-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: budget-change is Rust
- [x] T027 [US1] `ledger-hooks`: its decider `rust/guard/src/guards/ledger_hooks.rs`, its suite `tests/hooks/test-ledger-hooks.sh` replayed against `l7r-guard --only ledger-hooks`, then `scripts/hooks/ledger-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: ledger is Rust
- [ ] T028 [US1] `make-only-hooks`: its decider `rust/guard/src/guards/make_only_hooks.rs`, its suite `tests/hooks/test-make-only-hooks.sh` replayed against `l7r-guard --only make-only-hooks`, then `scripts/hooks/make-only-hooks.sh` and its settings entry removed - with the constitution XIV fix: a `grep` whose pattern names `pytest` is not a pytest run (found 2026-11-07); and FR-005's clause: a direct Bash run of a replacement's binary (`l7r-guard`, `hamlet`) refused with the make target that runs it, as a bare `cargo run` is today
      research: rendering
- [ ] T029 [US1] `guard-file-hooks`: its decider `rust/guard/src/guards/guard_file_hooks.rs`, its suite `tests/hooks/test-guard-file-hooks.sh` replayed against `l7r-guard --only guard-file-hooks`, then `scripts/hooks/guard-file-hooks.sh` and its settings entry removed - with the constitution XIV fix: a scratch file whose text names a guard (`x-hooks.sh`) is not a guard write (found 2026-11-07)
      research: rendering
- [x] T030 [US1] `archive-first-hooks`: its decider `rust/guard/src/guards/archive_first_hooks.rs`, its suite `tests/hooks/test-archive-first-hooks.sh` replayed against `l7r-guard --only archive-first-hooks`, then `scripts/hooks/archive-first-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: archive-first is Rust
- [x] T031 [US1] `claims-file-hooks`: its decider `rust/guard/src/guards/claims_file_hooks.rs`, its suite `tests/hooks/test-claims-file-hooks.sh` replayed against `l7r-guard --only claims-file-hooks`, then `scripts/hooks/claims-file-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T031+T032+T033: claims-file, readme and download-copy are Rust
- [x] T032 [US1] `readme-hooks`: its decider `rust/guard/src/guards/readme_hooks.rs`, its suite `tests/hooks/test-readme-hooks.sh` replayed against `l7r-guard --only readme-hooks`, then `scripts/hooks/readme-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T031+T032+T033: claims-file, readme and download-copy are Rust
- [x] T033 [US1] `download-copy-hooks`: its decider `rust/guard/src/guards/download_copy_hooks.rs`, its suite `tests/hooks/test-download-copy-hooks.sh` replayed against `l7r-guard --only download-copy-hooks`, then `scripts/hooks/download-copy-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T031+T032+T033: claims-file, readme and download-copy are Rust
- [ ] T034 [US1] `repo-safety-hooks`: its decider `rust/guard/src/guards/repo_safety_hooks.rs`, its suite `tests/hooks/test-repo-safety-hooks.sh` replayed against `l7r-guard --only repo-safety-hooks`, then `scripts/hooks/repo-safety-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T035 [US1] `shell-check-hooks`: its decider `rust/guard/src/guards/shell_check_hooks.rs`, its suite `tests/hooks/test-shell-check-hooks.sh` replayed against `l7r-guard --only shell-check-hooks`, then `scripts/hooks/shell-check-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T036 [US1] `house-style-hooks`: its decider `rust/guard/src/guards/house_style_hooks.rs`, its suite `tests/hooks/test-house-style-hooks.sh` replayed against `l7r-guard --only house-style-hooks`, then `scripts/hooks/house-style-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T037 [US1] `source-block-hooks`: its decider `rust/guard/src/guards/source_block_hooks.rs`, its suite `tests/hooks/test-source-block-hooks.sh` replayed against `l7r-guard --only source-block-hooks`, then `scripts/hooks/source-block-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T038 [US1] `wakeup-hooks`: its decider `rust/guard/src/guards/wakeup_hooks.rs`, its suite `tests/hooks/test-wakeup-hooks.sh` replayed against `l7r-guard --only wakeup-hooks`, then `scripts/hooks/wakeup-hooks.sh` and its settings entry removed
      research: rendering
- [x] T039 [US1] `blocked-fetch-hooks`: its decider `rust/guard/src/guards/blocked_fetch_hooks.rs`, its suite `tests/hooks/test-blocked-fetch-hooks.sh` replayed against `l7r-guard --only blocked-fetch-hooks`, then `scripts/hooks/blocked-fetch-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T039+T049: blocked-fetch and set-down are Rust
- [ ] T040 [US1] `workflow-hooks`: its decider `rust/guard/src/guards/workflow_hooks.rs`, its suite `tests/hooks/test-workflow-hooks.sh` replayed against `l7r-guard --only workflow-hooks`, then `scripts/hooks/workflow-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T041 [US1] `agent-model-hooks`: its decider `rust/guard/src/guards/agent_model_hooks.rs`, its suite `tests/hooks/test-agent-model-hooks.sh` replayed against `l7r-guard --only agent-model-hooks`, then `scripts/hooks/agent-model-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T042 [US1] `agent-prefix-hooks`: its decider `rust/guard/src/guards/agent_prefix_hooks.rs`, its suite `tests/hooks/test-agent-prefix-hooks.sh` replayed against `l7r-guard --only agent-prefix-hooks`, then `scripts/hooks/agent-prefix-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T043 [US1] `check-bundle-hooks`: its decider `rust/guard/src/guards/check_bundle_hooks.rs`, its suite `tests/hooks/test-check-bundle-hooks.sh` replayed against `l7r-guard --only check-bundle-hooks`, then `scripts/hooks/check-bundle-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T044 [US1] `escalation-hooks`: its decider `rust/guard/src/guards/escalation_hooks.rs`, its suite `tests/hooks/test-escalation-hooks.sh` replayed against `l7r-guard --only escalation-hooks`, then `scripts/hooks/escalation-hooks.sh` and its settings entry removed
      research: rendering
- [ ] T045 [US1] `review-round-hooks`: its decider `rust/guard/src/guards/review_round_hooks.rs`, its suite `tests/hooks/test-review-round-hooks.sh` replayed against `l7r-guard --only review-round-hooks`, then `scripts/hooks/review-round-hooks.sh` and its settings entry removed
      research: rendering
- [x] T046 [US1] `phase-source-hooks`: its decider `rust/guard/src/guards/phase_source_hooks.rs`, its suite `tests/hooks/test-phase-source-hooks.sh` replayed against `l7r-guard --only phase-source-hooks`, then `scripts/hooks/phase-source-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: phase-source is Rust
- [x] T047 [US1] `new-file-hooks`: its decider `rust/guard/src/guards/new_file_hooks.rs`, its suite `tests/hooks/test-new-file-hooks.sh` replayed against `l7r-guard --only new-file-hooks`, then `scripts/hooks/new-file-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: new-file is Rust
- [ ] T048 [US1] `checks-hooks`: its decider `rust/guard/src/guards/checks_hooks.rs`, its suite `tests/hooks/test-checks-hooks.sh` replayed against `l7r-guard --only checks-hooks`, then `scripts/hooks/checks-hooks.sh` and its settings entry removed
      research: rendering
- [x] T049 [US1] `set-down-hooks`: its decider `rust/guard/src/guards/set_down_hooks.rs`, its suite `tests/hooks/test-set-down-hooks.sh` replayed against `l7r-guard --only set-down-hooks`, then `scripts/hooks/set-down-hooks.sh` and its settings entry removed
      research: rendering

### User Story 1 - the suites' tooling and the close (plan work breakdown 6-8)
      verify: DONE. landed in batch T039+T049: blocked-fetch and set-down are Rust

- [ ] T050 [US1] The four Python helpers under `tests/hooks/` ported to the guard crate: `hookdeps.py` as `l7r-guard deps` (which suites a change makes stale, keyed on the Rust sources), `hooktrace.py` as `l7r-guard trace`, `hookbench.py` as `l7r-guard bench`, `test_hooks_cases.py`'s cases as the crate's tests; the `hooks-test` recipe calling them; the Python deleted
      research: rendering
- [ ] T051 [US1] The guard libraries left unused deleted: each `scripts/hooks/lib/*.py`, `guardlog.sh` and `agent-model-rule.txt` reader removed with its last caller; `make audit` and `make guard-log` read the Rust guard's lines unchanged
      research: rendering
- [ ] T052 [US1] The close (SC-001, US1 scenarios 1-3, FR-010): `m:hooks-bash` and `m:pair-hooks-suite` re-run and recorded beside their first values in `measurements.json`; phase 1's share of BOTH censuses - every `.py` and every inline site under `scripts/hooks/` and `tests/hooks/` - returns nothing (`m:python-census`, `m:inline-python-census` re-run); SC-001 met or the phase not closed
      research: rendering

## Dependencies

T001 -> T002 -> T003 -> T004 -> T005 -> the guard tasks (each depends on T002-T005, not on another guard) -> T050, T051 -> T052. A guard task whose decider needs a shared fact the library lacks extends T003's library in the same task.

## Parallel opportunities

The 44 guard tasks are independent of one another once T005 has landed: each touches its own decider, suite and settings entry. They land one at a time (each its own `make land-tooling`), since the settings file is shared.

## Implementation strategy

MVP: T001-T005 and the first guard, `pair-hooks` (T006): the dispatcher in every session with the slowest guard moved, its suite green, the call timed. Then the guards in order, each landed as it passes, so the session speeds up guard by guard.
