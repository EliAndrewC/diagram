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
- [x] T028 [US1] `make-only-hooks`: its decider `rust/guard/src/guards/make_only_hooks.rs`, its suite `tests/hooks/test-make-only-hooks.sh` replayed against `l7r-guard --only make-only-hooks`, then `scripts/hooks/make-only-hooks.sh` and its settings entry removed - with the constitution XIV fix: a `grep` whose pattern names `pytest` is not a pytest run (found 2026-11-07); and FR-005's clause: a direct Bash run of a replacement's binary (`l7r-guard`, `hamlet`) refused with the make target that runs it, as a bare `cargo run` is today
      research: rendering
      verify: DONE. landed: make-only is Rust
- [x] T029 [US1] `guard-file-hooks`: its decider `rust/guard/src/guards/guard_file_hooks.rs`, its suite `tests/hooks/test-guard-file-hooks.sh` replayed against `l7r-guard --only guard-file-hooks`, then `scripts/hooks/guard-file-hooks.sh` and its settings entry removed - with the constitution XIV fix: a scratch file whose text names a guard (`x-hooks.sh`) is not a guard write (found 2026-11-07)
      research: rendering
      verify: DONE. landed: guard-file is Rust
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
- [x] T034 [US1] `repo-safety-hooks`: its decider `rust/guard/src/guards/repo_safety_hooks.rs`, its suite `tests/hooks/test-repo-safety-hooks.sh` replayed against `l7r-guard --only repo-safety-hooks`, then `scripts/hooks/repo-safety-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T034+T038+T041: repo-safety, wakeup and agent-model are Rust
- [x] T035 [US1] `shell-check-hooks`: its decider `rust/guard/src/guards/shell_check_hooks.rs`, its suite `tests/hooks/test-shell-check-hooks.sh` replayed against `l7r-guard --only shell-check-hooks`, then `scripts/hooks/shell-check-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: shell-check is Rust
- [x] T036 [US1] `house-style-hooks`: its decider `rust/guard/src/guards/house_style_hooks.rs`, its suite `tests/hooks/test-house-style-hooks.sh` replayed against `l7r-guard --only house-style-hooks`, then `scripts/hooks/house-style-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: house-style is Rust
- [x] T037 [US1] `source-block-hooks`: its decider `rust/guard/src/guards/source_block_hooks.rs`, its suite `tests/hooks/test-source-block-hooks.sh` replayed against `l7r-guard --only source-block-hooks`, then `scripts/hooks/source-block-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: source-block is Rust
- [x] T038 [US1] `wakeup-hooks`: its decider `rust/guard/src/guards/wakeup_hooks.rs`, its suite `tests/hooks/test-wakeup-hooks.sh` replayed against `l7r-guard --only wakeup-hooks`, then `scripts/hooks/wakeup-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T034+T038+T041: repo-safety, wakeup and agent-model are Rust
- [x] T039 [US1] `blocked-fetch-hooks`: its decider `rust/guard/src/guards/blocked_fetch_hooks.rs`, its suite `tests/hooks/test-blocked-fetch-hooks.sh` replayed against `l7r-guard --only blocked-fetch-hooks`, then `scripts/hooks/blocked-fetch-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T039+T049: blocked-fetch and set-down are Rust
- [x] T040 [US1] `workflow-hooks`: its decider `rust/guard/src/guards/workflow_hooks.rs`, its suite `tests/hooks/test-workflow-hooks.sh` replayed against `l7r-guard --only workflow-hooks`, then `scripts/hooks/workflow-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T040+T042: agent-prefix and workflow are Rust
- [x] T041 [US1] `agent-model-hooks`: its decider `rust/guard/src/guards/agent_model_hooks.rs`, its suite `tests/hooks/test-agent-model-hooks.sh` replayed against `l7r-guard --only agent-model-hooks`, then `scripts/hooks/agent-model-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T034+T038+T041: repo-safety, wakeup and agent-model are Rust
- [x] T042 [US1] `agent-prefix-hooks`: its decider `rust/guard/src/guards/agent_prefix_hooks.rs`, its suite `tests/hooks/test-agent-prefix-hooks.sh` replayed against `l7r-guard --only agent-prefix-hooks`, then `scripts/hooks/agent-prefix-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T040+T042: agent-prefix and workflow are Rust
- [x] T044 [US1] `escalation-hooks`: its decider `rust/guard/src/guards/escalation_hooks.rs`, its suite `tests/hooks/test-escalation-hooks.sh` replayed against `l7r-guard --only escalation-hooks`, then `scripts/hooks/escalation-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: escalation is Rust
- [x] T045 [US1] `review-round-hooks`: its decider `rust/guard/src/guards/review_round_hooks.rs`, its suite `tests/hooks/test-review-round-hooks.sh` replayed against `l7r-guard --only review-round-hooks`, then `scripts/hooks/review-round-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: review-round is Rust
- [x] T046 [US1] `phase-source-hooks`: its decider `rust/guard/src/guards/phase_source_hooks.rs`, its suite `tests/hooks/test-phase-source-hooks.sh` replayed against `l7r-guard --only phase-source-hooks`, then `scripts/hooks/phase-source-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: phase-source is Rust
- [x] T047 [US1] `new-file-hooks`: its decider `rust/guard/src/guards/new_file_hooks.rs`, its suite `tests/hooks/test-new-file-hooks.sh` replayed against `l7r-guard --only new-file-hooks`, then `scripts/hooks/new-file-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed: new-file is Rust
- [x] T049 [US1] `set-down-hooks`: its decider `rust/guard/src/guards/set_down_hooks.rs`, its suite `tests/hooks/test-set-down-hooks.sh` replayed against `l7r-guard --only set-down-hooks`, then `scripts/hooks/set-down-hooks.sh` and its settings entry removed
      research: rendering

### User Story 1 - the suites' tooling and the close (plan work breakdown 6-8)

- [x] T053 [US1] The plain-call gate for the guards moved to phase 3: `record-edit-gate` in `rust/guard` answers a Bash call or an Edit that cannot concern `record-edit-hooks.sh` with no process, and runs the shell guard for one that can; its two settings entries gone (the round arbiter, `ask:449-hm-checks-route`, step 1)
      research: rendering
      verify: DONE. landed: the plain-call gate; three stale-state defects fixed

- [x] T050 [US1] The four Python helpers under `tests/hooks/` ported to the guard crate: `hookdeps.py` as `l7r-guard deps` (which suites a change makes stale, keyed on the Rust sources), `hooktrace.py` as `l7r-guard trace`, `hookbench.py` as `l7r-guard bench`, `test_hooks_cases.py`'s cases as the crate's tests; the `hooks-test` recipe calling them; the Python deleted
      research: rendering
      verify: DONE. landed: the suites' tooling in Rust
- [x] T051 [US1] The guard libraries left unused deleted: each `scripts/hooks/lib/*.py`, `guardlog.sh` and `agent-model-rule.txt` reader removed with its last caller; `make audit` and `make guard-log` read the Rust guard's lines unchanged
      research: rendering
      verify: DONE. landed: the unused guard libraries; the rest placed by FR-001
- [x] T054 [US1] SC-001 on a plain Bash call: each guard whose rules cannot match a command answers it before compiling their patterns or starting `bash -n`; `m:t054-plain-bash` under `m:hooks-bash`'s tenth of the slowest guard
      research: rendering
      verify: DONE. landed: fast exits; SC-001 met on its instrument

- [x] T052 [US1] The close (SC-001, US1 scenarios 1-3, FR-010): `m:hooks-bash` and `m:pair-hooks-suite` re-run and recorded beside their first values in `measurements.json`; phase 1's share of BOTH censuses - every `.py` and every inline site under `scripts/hooks/` and `tests/hooks/` - returns nothing (`m:python-census`, `m:inline-python-census` re-run); SC-001 met or the phase not closed
      research: rendering

### User Story 2 - the gate is Rust (phase 2, opened 2026-11-08 by a plan amendment)

- [x] T060 [US2] The Rust-only route: a delta touching only `.rs` files and the Rust manifests runs the Rust checks and the few text checks over `.rs`, and no pytest
      research: rendering
      verify: DONE. landed: a crate's unchanged checks reuse their last green result

- [x] T061 [US2] `rust/gate`: the crate and its binary `l7r-gate`, called from the Makefile, with the shared facts the ports below read (the repository's paths, the run record's format, git in one place)
      research: rendering
      verify: DONE. landed: the gate crate

- [x] T062 [US2] `gate-stamp.py`'s content id and `codeid.py`'s `.rs` id and blob-keyed cache in Rust, read by the engine key, the push stamp and the roll cache, held to the Python's byte for byte on the real records; a `.py` id stays `codeid.py`'s, asked once a run for the misses (`ask:449-T062-py-id`)
      research: rendering
      verify: DONE. landed: the code ids in Rust

- [x] T063 [US2] `l7r/diagram/ci/` the delta and the stamps: `delta.py`, the rest of `scripts/gates/gate-stamp.py` and `__main__.py`'s subcommands for them (slices 1 and 2 of `ask:449-T063-slices`; the state is T72)
      research: rendering
      verify: DONE. landed: the stamps and delta ported to rust/gate; m:t063-slice2 shows area keys, lists, 8,885 content ids, 50 engine keys, 7 deltas, the engine list over 26,664 paths and raw-match over 26,670 equal to the Python; static, tooling tests and 56 hook suites green

- [x] T064 [US2] `l7r/diagram/ci/` the decision and the remote path: `decision.py`, `dispatch.py`, `cachepolicy.py`, `door.py`, `features.py`, `imagecheck.py`, `config.py`, `switches.py`, and `runlog.py` (moved from T72: its callers are these) (`_invocation.py` moves to phase 4 with its last Python caller, `ask:449-T064-slices`)
      research: rendering
      verify: DONE. landed: the remote path ported to rust/gate/src/ci; m:t064-remote shows route, status, spend, door, switches, idle and lifecycle equal to the Python's; the AWS adapter is tested through a fake aws and unproven until the first paid run; static, tooling tests and hook suites green

- [x] T065 [US2] `scripts/gates/` the text checks: `check-file-scale.py`, `check-stale-dirs.py`, `check-question-size.py`, `check-rust-tooling.py`, `check-research-pointers.py` and `check-house-style-delta.py`, each check's verdicts held to the Python's over the repository (the other `check-*.py`: `ask:449-T065-scope`, FR-001)
      research: rendering
      verify: DONE. landed: the six text checks are Rust (l7r-gate check); the four that outlast phase 2 ask check needs first

- [x] T066 [US2] `scripts/gates/` the plan and spec gates: `plan_gate.py`, `plan_sections.py`, `approach_gate.py`, `plan_bundle.py`, `spec-lint.py`, with `engine_edit.py` beside the code it wraps, and what they import (`plan_lint.py`, `plan_seen.py`, `spec_figures.py`, `wording_only`); `task-start` and the cohort's trigger stay in Python with what they read (`ask:449-T066-scope`, FR-001)
      research: rendering
      verify: DONE. landed: the plan and spec gates are Rust (l7r-gate plan, check spec-lint); what stays Python reaches them through scripts/plan_door.py

- [x] T067 [US2] `scripts/gates/` the landing's own: `gate_lock.py`, `rust_checks.py`, `push_gates.py`, `push_checks.py`, with `scripts/hooks/lib/hm_conflict.py` and `own-make.sh`; `cohort_gate.py` and `room_table.py` go to T068, `preflight.py`, `cover_changed.py`, `refresh_baseline.py` and `pool-readers.py` to T071, `close_check.py` and `memo_check.py` to phase 3 (`ask:449-T067-scope`, FR-001)
      research: rendering
      verify: DONE. landed: the gate lock, own-make, the conflict check, the Rust crates' checks and the push's checks are Rust; the watchdog tells a session about a long make

- [x] T068 [US2] The gate checks and the cohort, the first of `scripts/measure/`'s four slices (`ask:449-T068-scope`): `cohort_gate.py`, `cohort_known.py`, `room_table.py`, `cohort_seeds.py`, `check-run-plausible.py` and `check-tool-signals.py` (`ask:449-T065-scope`, `ask:449-T067-scope`); the figures and probes, the logs and reports, and the rest are the tasks after it, `collect_cost.py` and `collect_probe.py` left to phase 4
      research: rendering
      verify: DONE. landed: the first slice of scripts/measure/: the cohort, the room table, the run floor and the tool-signals check are Rust

- [x] T069 [US2] The inline Python of the phase: the Makefile's gate recipes, `scripts/gates/*.sh`, `sync-with-main.sh`, `land-tooling.sh`; the suites FR-001 moved here (`test-entry-gate`, `test-claims-gate`, `test-cohort-gate`, `test-land-tooling`) with them
      research: rendering
      verify: DONE. landed: the gate's inline Python is Rust verbs; T77's ports land with it, T77 and T73 open until the GM's removal

- [x] T071 [US2] `scripts/gates/preflight.py`: its checks with a lasting subject, its pytest-reading checks behind one named door until phase 4 (`ask:449-T071-scope`; the planner set goes in phase 4, deleted and not ported)
      research: rendering
      verify: DONE. landed in batch T071+T73+T77: the gate's first phase is Rust, the AWS path and the ported measure tools are gone

- [x] T070 [US2] The close of phase 2 (the expected remainders of `scripts/measure/`, by phase: `work_budget_view.py`, `replay_owing.py`, `depiction_replay.py` and the deferred T76 modules in phase 3; `uncovered-in-diff.py`, `uncovered_marks.py`, `tooling_reuse_time.py`, `collect_cost.py`, `collect_probe.py` and `dead_closure.py` in phase 4; `agent_census.py`'s port in phase 3 calls `measure/model_trial.rs`'s `fold_usage` and deletes the Python fold, so no second Rust fold is written, `ask:449-T77-replays`; the inline sites `test-claims-gate.sh`'s fixture over `claims.py` and `test-entry-gate.sh`'s `answer_all` over `record_owed.py`, and `make audit`'s four recipes, three in phase 3 and the one reading `CLASSES` in phase 4, `ask:449-T069-suites`; the gate recipe's `python3 -m pip show -q pytest-xdist` probe, phase 4 with the pytest line it serves, `ask:449-T069-xdist`; and, phase 4, deleted and not ported in the commit that removes pytest, `selection.py`, `gate_plugin.py`, `incremental.py`, `gate_config.py`'s two readers, `pool_readers.py`, `pool-readers.py`, `cover_changed.py`, `refresh_baseline.py`, `__main__.py`, `delta.py` and `state.py`, an unchanged or comment-only tree's `make done` starting none of them, and SC-002's run stating the planner's and pytest's shares as `m:` figures, `ask:449-T071-scope`): `m:done-rust-edit`, an unchanged tree's `make done`, both censuses' phase-2 share, `tests/tooling/test_rust_tooling.py` replaced by one Rust end-to-end test against the real cargo and `World` seam tests for the rest (FR-008), and deleted (the Assumptions clause's limit, `ask:449-T067-scope`), the phase's record in `dev/`
      research: rendering

### Phase 3 (moved by the round arbiter's ruling `ask:449-hm-checks-route`, 2026-11-08; ported in one cut with their Python callers, FR-001)
      verify: DONE. landed: phase 2 closed; SC-002's one-line edit recorded not met at 22.0 s, an unchanged tree runs no test

- [x] T011 [US1] `record-edit-hooks`: its decider `rust/guard/src/guards/record_edit_hooks.rs`, its suite `tests/hooks/test-record-edit-hooks.sh` replayed against `l7r-guard --only record-edit-hooks`, then `scripts/hooks/record-edit-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T86+T011+T043+T048+T84: the arbiter and checks state in Rust, three guards with it, and the first ported Python removed
- [x] T043 [US1] `check-bundle-hooks`: its decider `rust/guard/src/guards/check_bundle_hooks.rs`, its suite `tests/hooks/test-check-bundle-hooks.sh` replayed against `l7r-guard --only check-bundle-hooks`, then `scripts/hooks/check-bundle-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T86+T011+T043+T048+T84: the arbiter and checks state in Rust, three guards with it, and the first ported Python removed
- [x] T048 [US1] `checks-hooks`: its decider `rust/guard/src/guards/checks_hooks.rs`, its suite `tests/hooks/test-checks-hooks.sh` replayed against `l7r-guard --only checks-hooks`, then `scripts/hooks/checks-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T86+T011+T043+T048+T84: the arbiter and checks state in Rust, three guards with it, and the first ported Python removed

## Dependencies

T001 -> T002 -> T003 -> T004 -> T005 -> the guard tasks (each depends on T002-T005, not on another guard) -> T050, T051 -> T052. A guard task whose decider needs a shared fact the library lacks extends T003's library in the same task.

## Parallel opportunities

The 44 guard tasks are independent of one another once T005 has landed: each touches its own decider, suite and settings entry. They land one at a time (each its own `make land-tooling`), since the settings file is shared.

## Implementation strategy

MVP: T001-T005 and the first guard, `pair-hooks` (T006): the dispatcher in every session with the slowest guard moved, its suite green, the call timed. Then the guards in order, each landed as it passes, so the session speeds up guard by guard.
- [x] T72 [US2] `l7r/diagram/ci/` the state: `state.py`, `gate_config.py`'s `config_hash`, `coverage_exempt.py` and `__main__.py`'s subcommands for them, the verification state readable across the switch (slice 3 of `ask:449-T063-slices`; `runlog.py` goes with its callers in T064, and `scripts_readers` and `tooling_modules` with `incremental.py` in T071)
      research: rendering
      verify: DONE. landed: the state, the tooling and config hashes and the coverage record ported to rust/gate; m:t72-state shows both hashes equal to the Python's, the second call from kept forms; static, tooling tests and hook suites green
- [x] T73 The remote test path deleted, not ported (FR-001a): `buildspec/`, `Dockerfile.ci`, the `ci-*` targets, the `remote` switch, the dispatcher and AWS adapter; the route and the gated push local
      research: rendering
      verify: DONE. landed in batch T071+T73+T77: the gate's first phase is Rust, the AWS path and the ported measure tools are gone
- [x] T74 Past feature harnesses nothing runs deleted, not ported (FR-001): 138 Python files under `specs/`
      research: rendering
      verify: DONE. landed: 138 past-feature harness files nothing runs deleted; the done-line census shows no hit outside the named records
- [x] T75 `scripts/measure/`, the second slice (`ask:449-T068-scope`): the figures and probes, `figures.py`, `probe.py`, `ratchet.py`, `gatecost.py`, `gate_costs.py`
      research: rendering
      verify: DONE. landed: the figures, the probe, the ratchets and the gate's costs are Rust; reopen.py restored
- [x] T76 `scripts/measure/`, the third slice (`ask:449-T068-scope`): the logs and reports, `runstats.py`, `guard-log.py`, `review_yield.py`, `wave_report.py`, `subagent_cache.py`, `fresh_tally.py`, with `tool_yield.py` if no Python caller remains; `event_log.py`, `feature_report.py`, `turn_time.py`, `fix_yield.py`, `task_phases.py` and `where_time.py` are phase 3's (`ask:449-T76-scope`)
      research: rendering
      verify: DONE. landed: run stats, the guard log and the small reports are Rust
- [x] T77 `scripts/measure/`, the last slice (`ask:449-T068-scope`, `ask:449-T77-scope`, `ask:449-T77-replays`): `maps_moved.py`, `work_budget_rust.py`, `model_trial.py`, `popup_rounds.py`, `push_check_times.py`
      research: rendering
      verify: DONE. landed in batch T071+T73+T77: the gate's first phase is Rust, the AWS path and the ported measure tools are gone
- [x] T78 The Python unit tests, the planner and the Python-only static checks deleted (FR-001b)
      research: rendering
      verify: DONE. landed: the Python unit tests, the planner, the floor and the Python-only checks are deleted (FR-001b)
- [x] T79 Phase 3, the standalone tools with no Python caller: `canon.py`, `money_conversions.py`, `found.py`, `stale_terms.py`, `money_candidates.py`, `fragment_move.py`, `agent_census.py`
      research: rendering
      verify: DONE. landed: the phase-3 tools no Python imports are Rust; their Python stays until the GM approves its removal (T84)
- [x] T80 Phase 3, the archive's first slice (`ask:449-T80-order`): `access_tags.py`, `downloads.py`, `check-partial-citations.py`; `uncited.py`, `uncited_imports.py`, `archive_ops.py` and `archive.py` follow T81 in its order
      research: rendering
      verify: DONE. landed: access-tags, downloads and partial-citations are Rust; their Python stays until the GM approves its removal
- [x] T81 Phase 3, the record's first leaves (`ask:449-T81-slices`): `hm_record` as `record edit-route` and `record fragments`, `hm_house` as `record americanize`, `moves` as `record moved-only`, Python's callers through `scripts/record_door.py`; the rest of the old T81 is T85-T89 and `quote_verbatim.py` moves to phase 4
      research: rendering
      verify: DONE. landed: the first record leaves in Rust: edit-route, fragments, americanize, moved-only
- [x] T82 Phase 3, claims: claims.py and its satellites
      research: rendering
      verify: DONE. landed: the claims tools in Rust; the .py half behind bundle_door.py, claims_door.py for the Python that stays (ask:449-T82-claims); the plan's .py-half bullet still names all_units, removed in the cut
- [x] T83 Phase 3, measure and events: event_log, feature_report, ledger_owed, where_time, stepback_bundle, fix_yield, replay_owing's ruling, the three make audit recipes, land.py and speckit-todo.py
      research: rendering
      verify: DONE. all five slices landed: T117 (the ledger's tools), T118 (speckit-todo), T119 (the measure chain), T120 (the step-back and the yields), T121 (land.py, work_budget_view.py, replay_owing.py, three audit sections), with T124 removing the door verbs only land.py asked
- [x] T84 The first removal under the GM's standing approval (the GM, 2026-11-10: "Yes please delete Python files once their Rust ports land."): the ported `canon.py`, `money_conversions.py`, `found.py`, `stale_terms.py`, `money_candidates.py`, `fragment_move.py`, `agent_census.py`, `access_tags.py`, `downloads.py`, `check-partial-citations.py`, `moves.py`, `hm_record.py`, `hm_house.py` and specs/251's `seeded.py` and `run_seeded.sh`, the docs renamed to their verbs; each later task removes its own ported files at its landing
      research: rendering
      verify: DONE. landed in batch T86+T011+T043+T048+T84: the arbiter and checks state in Rust, three guards with it, and the first ported Python removed
- [ ] T85 Phase 4, the archive cluster with `interactive/record` (`ask:449-T81-slices`, moved by its test, each carrying the T065 clause and named at the phase-3 close): `quote_verbatim`, `sources`, `attempts`, `source_pages`, `reserve-prefix`, `apply_edits`, `uncited`, `uncited_imports`, `archive_ops`, `archive`, `entry_owed`, `record_prepass`, `style_prepass` (`ask:449-T88-bundles`); Rust `downloads`' by-path run of `reserve-prefix.py` ends here
      research: rendering
- [x] T86 Phase 3, the arbiter and checks state, with T011, T043 and T048: hm_arbiter, hm_checks, hm_fixloop, hm_planhold, hm_budget_rounds, one owner of checks-open.json, arbiter-owed.json and modal-batches.json
      research: rendering
      verify: DONE. landed in batch T86+T011+T043+T048+T84: the arbiter and checks state in Rust, three guards with it, and the first ported Python removed
- [x] T87 Phase 3, the owed core (`entry_owed.py` moved to T85's phase by `ask:449-T87-entry-owed`): record_owed, record_units, modal_owed, translation_owed, modal_triage, and `pull-queue.sh`'s merge as a verb; `record_cache.py` stays for its other importers (`memo_check.py`, `claims.py`, `entry_owed.py`) and goes with the last of them with its last Python caller (`ask:449-T81-slices`)
      research: rendering
      verify: DONE. landed: the owed core in Rust: record_owed, record_units, modal_owed, translation_owed, modal_triage and the pull-queue merge; entry_owed to phase 4 by ask:449-T87-entry-owed
- [x] T88 Phase 3, the bundles: bundle_owed, check_bundle, modal_bundle, earlier_rounds, arbiter_bundle, depiction_replay onto the Rust modal_owed (`ask:449-T88-bundles`: one Python runner, `scripts/bundle_door.py`, for what they reach of unported Python)
      research: rendering
      verify: DONE. landed: the bundles in Rust: bundle_owed, check_bundle, modal_bundle, earlier_rounds, arbiter_bundle, depiction_replay; one Python runner for what they reach of unported Python (ask:449-T88-bundles)
- [x] T89 Phase 3, the reviews (`ask:449-T89-reviews`): review_owed, review_prereq, checkpoint, with hm_approval.py; stepback_bundle moves to T83
      research: rendering
      verify: DONE. landed: the reviews in Rust: review_owed, review_prereq, checkpoint, hm_approval; stepback_bundle to T83; specs/240's probe retired (ask:449-T89-reviews)
- [ ] T90 Phase 3, the engine's pipeline package (`l7r/diagram/pipeline/`, phase 3 by FR-001, filed by `ask:449-T89-reviews`); `bundle_door.py`'s `is_current` verb leaves when it lands
      research: rendering
- [ ] T91 Phase 3, the GM-review queue (`scripts/gm_review.py`, phase 3, filed by `ask:449-T82-claims`); `bundle_door.py`'s gm-review write verb leaves when it lands
      research: rendering
- [x] T92 Split the gate crate (74,199 lines) into crates so an edit recompiles one, the binary a thin crate over them (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the gate crate split into 15 crates and a dispatching binary (FR-011); the plan cites FR-003 for the coverage rule, which is FR-004, and its path counts name no command (both noted by the review, not changed after it)
- [x] T93 The fast Rust loop by default and enforced: make rust-test and make static run only the crates whose test binary changed since their last green run, the passed result reused; the whole run an escape with a reason (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the Rust runner's own binary, reuse keyed on sources, declared reads and the test binary, FRESH=1 REASON= as the logged escape; the first-key bullet's 1,105 lines is unlabeled (review aside)
- [x] T94 The landing's slow hook suites reuse what make done already built: the guard suite's real build and the sync-with-main suite (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the guard suite reuses the wrapper's build and no longer sleeps 30 s (86.5 s -> 1.4 s); every suite measured to build nothing on a warm tree; built-once on a changed guard crate is reasoned, not measured
- [x] T95 The full l7r-gate release binary rebuilt after any gate crate edit (48 s after core): a lighter or incremental release build for the tool, measured (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the tool binaries build in an incremental profile: l7r-gate rebuilds in 1-2 s after a crate edit, from 8-45 s
- [x] T96 A test binary rebuilt after a one-line edit (13.9 s claims): the gate crates' test profile and the linker, measured (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: every build links with rust-lld and dev keeps line tables only: a claims test rebuild 13.9 s to 1 s, make static after a core edit 103 s to 75 s
- [x] T97 make done's counters-inert phase (53 s of 57 s): the counting builds of core and phases rerun less, measured (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the counting build runs only on a crate with a counters feature: counters-inert 59-113 s to about 5 s
- [x] T98 The hook suites in parallel (about 95 s): the slowest few profiled and made cheaper (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the batching suite moves its guard's clock by a file: 29.3 s to 1.4 s, a full hook run 71.2 to 63.8 s
- [x] T99 The arbiter crate's slow tests (100-300 ms each against FR-008's tenth of a second): made fast (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: every arbiter test under 0.1 s alone but the one real owed-list computation (0.143 s, the named remainder); the crate's tests 8-11 s to 0.18 s
- [x] T100 make static after a fresh gate crate edit (103.3 s core, 64.8 s claims after a comment, 2026-11-11): the lint, coverage and dead-code reruns for the edited crate and every crate built on it, measured and cut (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: make static after an edit: core 68.7 to 54.0 s, claims 44.5 to 25.3 s, a docs file 34.2 to 13.5 s, coverage unchanged
- [x] T101 Every l7r-gate-* and l7r-guard-* temp directory a check or test makes is removed on exit, failure and panic included, and a test pins it: ~329,000 left in /tmp since early October, ~126 GB (Eli via the laptop session, 2026-11-11)
      research: rendering
      verify: DONE. landed: every temp directory a check or test makes is removed on exit, failure, panic, INT and TERM, and the Rust and hook-suite runners fail one that leaves any
- [x] T102 The cargo build cache stops growing: the rustc real-target test builds its fixture crate into its own removed target (3,407 l7r_fixture incremental dirs and 5,069 deps files, ~5.6 GB, in diagram-backlog's debug/), and a sweep removes incremental sessions and deps files unused for days and the target dirs of trees that no longer exist under ~/.cache/l7r-cargo-target (54 GB, 56 dirs) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the daily sweep prunes the cargo target cache: a gone tree's build directory whole, each crate's variants beyond its newest four, once idle three days
- [x] T103 Session scratch under /tmp/claude-1000 swept: a session's scratchpad and task outputs removed once its transcript has been idle for days, never a live session's (38 GB, 20 GB in one session's scratch clones) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: a finished session's scratch under /tmp/claude-<uid> is swept once a day by a detached guard, never a running session's
- [x] T104 A spec round's arbiter bundle read every subagent transcript whole for its first line (8,696 files, 8.0 GB): one bundle 7.6 s, the arbiter crate's tests 8-11 s; read the first line only (found under T99, 2026-11-11)
      research: rendering
      verify: DONE. landed: a spec round's arbiter bundle reads each transcript's first line only: 7.6 s to 0.3 s, the arbiter crate's tests 8-11 s to 1.1 s
- [x] T105 A core edit's coverage builds made together: make static builds each gate crate's coverage binary one after another, 17 builds and 14.6 s of 54.0 s after a core edit (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: a family's owed coverage binaries built together: make static after a core edit 65.0 to 57.2 s
- [x] T106 The sync-with-main hook suite's own time: 25.6 s alone, 56.5 s amid the others, the full hook run's critical path (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the sync-with-main suite's fixture built once and copied a case: 23.4-24.5 s to 19.1-19.5 s
- [x] T107 The record's owed list's git calls: about 35 a computation, 0.1 s on a fixture and more on the tree, wherever it runs (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the record's owed list reads git's state once a computation: 24 git calls to 9 on the fixture, make record-owed 44 to 14
- [x] T108 A core edit's coverage tests side by side: each crate's coverage tests and report run one after another in the family's one build, 17.2 s of make static's 57.2 s after a core edit, one crate 8.9 s of it (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: a core edit's coverage tests side by side: make static after a core edit 49.7-52.0 s to 40.2 s
- [x] T109 push-checks' Rust self-tests kept per binary: the six run on every push whether or not the binary changed, 0.28 s of a 3.7 s push at load 0.5, about 0.4 s under the sync-with-main suite's load (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: push-checks' Rust self-tests kept per binary: a push 8.41-8.53 s to 8.00-8.20 s
- [x] T110 rustfmt kept per crate: `rust format --check` keeps nothing, all 19 crates re-checked on every make static, 2.1 s of a core edit's 29 s and of an idle run's 4.6 s (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: rustfmt's check kept per crate: 2.3 s to 0.16 s idle, 0.78 s after a core edit
- [x] T111 A coverage pass records the crate's test result: make rust-test then make static run every owed crate's tests twice, plain and under coverage, and no code depends on cfg(coverage) (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: a coverage pass records the test result: rust-test after a core edit's static 18.3 s to 4.2 s
- [x] T112 Comment-insensitive keys: a comment-only Rust edit moves every kept key it reaches, a core comment rerunning 29 s of make static that no check's verdict depends on (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: comment-insensitive keys: make static after a core comment edit 37.5 s to 17.5 s
- [x] T113 The dependents' lint keyed on a crate's public interface: after a core edit the 16 crates built on it re-lint for 8.5 s of clippy's 10.6 s, though their lint changes only with core's interface; not exact, its design reviewed first (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the dependents' lint keyed on the interface: a body-only core edit's lint step 10.8 s to 1.9 s
- [x] T114 The push's money-candidates check: 2.46 s of a 3.68 s push, the whole record scanned on every push whatever it changed (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the money check's pages side by side: its push row 2.46 s to 0.79 s
- [x] T115 The full hook run's two longest suites: sync-with-main 54.4 s and entry-gate 50.4 s of its 64.8 s (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the two longest suites: record-owed 1.72 s to 1.22 s, push-checks 6.6 s to 5.1 s; the full hook run bound elsewhere
- [x] T116 The checks crate's coverage tests: 8.9 s alone and 15-16 s beside the others, the floor of a core edit's coverage step, rerun on any edit anywhere since its tests declare the whole tree (2026-11-11) (the GM 2026-11-11)
      research: rendering
      verify: DONE. landed: the checks crate's coverage 10.7 s to 0.9 s; a body-only core edit's static 30.3 s to 23.5 s
- [x] T117 T83's first slice (`ask:449-T83-scope`): the review ledger's tools, `ledger_owed.py`, `ledger_lint.py` and `review_cost.py`
      research: rendering
      verify: DONE. landed: T83 slice 1: the review ledger's tools in Rust, 170 differential cases with no difference
- [x] T118 T83's second slice (`ask:449-T83-scope`): `speckit-todo.py`, its Rust callers calling it in-process
      research: rendering
      verify: DONE. landed: T83 slice 2: speckit-todo in Rust, 2,172 differential cases, one accepted difference
- [x] T119 T83's third slice (`ask:449-T83-scope`): the measure chain, `event_log.py`, `task_phases.py`, `feature_report.py`, `where_time.py`
      research: rendering
      verify: DONE. landed: T83 slice 3: the measure chain in Rust, 182 differential cases twice with no difference
- [x] T120 T83's fourth slice (`ask:449-T83-scope`): `stepback_bundle.py` with `turn_time.py`, `fix_yield.py` and `tool_yield.py`; `reviews_door.py`'s three verbs go
      research: rendering
      verify: DONE. landed: T83 slice 4: the step-back and the yields in Rust, 219 differential cases with no difference
- [x] T121 T83's fifth slice (`ask:449-T83-scope`): `land.py` with `work_budget_view.py` and replay_owing's OLD side, last, proved by a verdict replay over recorded landings
      research: rendering
      verify: DONE. landed: land.py ported to Rust (l7r-gate land), proved by a 104-run verdict replay over 50 recorded landings and three differentials; make static, rust-test and hooks-test green
- [ ] T122 The idle-tests suite's waits in milliseconds: its fixture waits 1 to 4 s of real time a case (the timer counts awake time in real ticks), 35.0 s alone and the full hook run's longest suite, about 20 s of it waits; a model of the run's eight slots puts the run at 28 s with the suite at 15 s, against 44 s as run (2026-11-12, /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r5/profile.sh and the schedule model) (the GM 2026-11-12, pre-approved: "if you identify concrete targets with significant measured expected savings then go ahead and do them")
      research: rendering
      note: not landed - its plan review (BLOCKED, 2026-11-12) held it to the GM's condition: the suite alone fell from 35.0 s to about 17 s, but the full hook run did not move (52.1 s against 53.1 s and 54.1 s), so no significant saving in the loop he is speeding up; the change is kept as a patch until the run's real bound is found
- [ ] T123 The hook suites started longest first, from each suite's last time: the eight slots take the roster in its order, the longest suite 34th, the model 44 s as run against 35 s longest first (2026-11-12); T98 measured longest first slower (74.8 s and 77 s against 63.8 s), so it lands only on a fresh A/B (the GM 2026-11-12, pre-approved: "if you identify concrete targets with significant measured expected savings then go ahead and do them")
      research: rendering
      note: not built - T122's full hook runs (53.1 s and 54.1 s against 52.1 s) showed the run is held by something its suites share, not by its schedule, so the model's saving does not hold and the GM's condition (a significant measured expected saving) is not met; to be closed or rescoped once that bound is found
- [x] T124 The claims-door verbs only land.py asked (scope_split, file_left, flight_live, CLAIMS_FEATURE_DIR) and seam::file_left removed, with claims_door.py's forwarders: kept through T121's landing commit so the Python land.py could land its own deletion (ask:449-T83-scope), landed by the Rust land after it (T121's plan review, 2026-11-12)
      research: rendering
      verify: DONE. landed: the four claims-door verbs only land.py asked removed; whole-tree census clean, make static and rust-test green; the Rust land's first landing
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
