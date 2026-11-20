# 449-rust-codebase - the ticked tasks, archived by `make tick` (feature 449 T142; the open ones are in tasks.md)

- [x] T001 The Cargo workspace: `rust/Cargo.toml` with the members `phases` and `guard`, `rust/guard/` created with its `CLAUDE.md` index; `scripts/gates/rust_checks.py` finds and checks every member (`make rust-test`, `make static`'s lint, format, cover and dead over both), each crate's summary printed
      research: rendering
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
- [x] T011 [US1] `record-edit-hooks`: its decider `rust/guard/src/guards/record_edit_hooks.rs`, its suite `tests/hooks/test-record-edit-hooks.sh` replayed against `l7r-guard --only record-edit-hooks`, then `scripts/hooks/record-edit-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T86+T011+T043+T048+T84: the arbiter and checks state in Rust, three guards with it, and the first ported Python removed
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
- [x] T043 [US1] `check-bundle-hooks`: its decider `rust/guard/src/guards/check_bundle_hooks.rs`, its suite `tests/hooks/test-check-bundle-hooks.sh` replayed against `l7r-guard --only check-bundle-hooks`, then `scripts/hooks/check-bundle-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T86+T011+T043+T048+T84: the arbiter and checks state in Rust, three guards with it, and the first ported Python removed
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
- [x] T048 [US1] `checks-hooks`: its decider `rust/guard/src/guards/checks_hooks.rs`, its suite `tests/hooks/test-checks-hooks.sh` replayed against `l7r-guard --only checks-hooks`, then `scripts/hooks/checks-hooks.sh` and its settings entry removed
      research: rendering
      verify: DONE. landed in batch T86+T011+T043+T048+T84: the arbiter and checks state in Rust, three guards with it, and the first ported Python removed
- [x] T049 [US1] `set-down-hooks`: its decider `rust/guard/src/guards/set_down_hooks.rs`, its suite `tests/hooks/test-set-down-hooks.sh` replayed against `l7r-guard --only set-down-hooks`, then `scripts/hooks/set-down-hooks.sh` and its settings entry removed
      research: rendering
- [x] T050 [US1] The four Python helpers under `tests/hooks/` ported to the guard crate: `hookdeps.py` as `l7r-guard deps` (which suites a change makes stale, keyed on the Rust sources), `hooktrace.py` as `l7r-guard trace`, `hookbench.py` as `l7r-guard bench`, `test_hooks_cases.py`'s cases as the crate's tests; the `hooks-test` recipe calling them; the Python deleted
      research: rendering
      verify: DONE. landed: the suites' tooling in Rust
- [x] T051 [US1] The guard libraries left unused deleted: each `scripts/hooks/lib/*.py`, `guardlog.sh` and `agent-model-rule.txt` reader removed with its last caller; `make audit` and `make guard-log` read the Rust guard's lines unchanged
      research: rendering
      verify: DONE. landed: the unused guard libraries; the rest placed by FR-001
- [x] T052 [US1] The close (SC-001, US1 scenarios 1-3, FR-010): `m:hooks-bash` and `m:pair-hooks-suite` re-run and recorded beside their first values in `measurements.json`; phase 1's share of BOTH censuses - every `.py` and every inline site under `scripts/hooks/` and `tests/hooks/` - returns nothing (`m:python-census`, `m:inline-python-census` re-run); SC-001 met or the phase not closed
      research: rendering
- [x] T053 [US1] The plain-call gate for the guards moved to phase 3: `record-edit-gate` in `rust/guard` answers a Bash call or an Edit that cannot concern `record-edit-hooks.sh` with no process, and runs the shell guard for one that can; its two settings entries gone (the round arbiter, `ask:449-hm-checks-route`, step 1)
      research: rendering
      verify: DONE. landed: the plain-call gate; three stale-state defects fixed
- [x] T054 [US1] SC-001 on a plain Bash call: each guard whose rules cannot match a command answers it before compiling their patterns or starting `bash -n`; `m:t054-plain-bash` under `m:hooks-bash`'s tenth of the slowest guard
      research: rendering
      verify: DONE. landed: fast exits; SC-001 met on its instrument
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
- [x] T070 [US2] The close of phase 2 (the expected remainders of `scripts/measure/`, by phase: `work_budget_view.py`, `replay_owing.py`, `depiction_replay.py` and the deferred T76 modules in phase 3; `uncovered-in-diff.py`, `uncovered_marks.py`, `tooling_reuse_time.py`, `collect_cost.py`, `collect_probe.py` and `dead_closure.py` in phase 4; `agent_census.py`'s port in phase 3 calls `measure/model_trial.rs`'s `fold_usage` and deletes the Python fold, so no second Rust fold is written, `ask:449-T77-replays`; the inline sites `test-claims-gate.sh`'s fixture over `claims.py` and `test-entry-gate.sh`'s `answer_all` over `record_owed.py`, and `make audit`'s four recipes, three in phase 3 and the one reading `CLASSES` in phase 4, `ask:449-T069-suites`; the gate recipe's `python3 -m pip show -q pytest-xdist` probe, phase 4 with the pytest line it serves, `ask:449-T069-xdist`; and, phase 4, deleted and not ported in the commit that removes pytest, `selection.py`, `gate_plugin.py`, `incremental.py`, `gate_config.py`'s two readers, `pool_readers.py`, `pool-readers.py`, `cover_changed.py`, `refresh_baseline.py`, `__main__.py`, `delta.py` and `state.py`, an unchanged or comment-only tree's `make done` starting none of them, and SC-002's run stating the planner's and pytest's shares as `m:` figures, `ask:449-T071-scope`): `m:done-rust-edit`, an unchanged tree's `make done`, both censuses' phase-2 share, `tests/tooling/test_rust_tooling.py` replaced by one Rust end-to-end test against the real cargo and `World` seam tests for the rest (FR-008), and deleted (the Assumptions clause's limit, `ask:449-T067-scope`), the phase's record in `dev/`
      research: rendering
      verify: DONE. landed: phase 2 closed; SC-002's one-line edit recorded not met at 22.0 s, an unchanged tree runs no test
- [x] T071 [US2] `scripts/gates/preflight.py`: its checks with a lasting subject, its pytest-reading checks behind one named door until phase 4 (`ask:449-T071-scope`; the planner set goes in phase 4, deleted and not ported)
      research: rendering
      verify: DONE. landed in batch T071+T73+T77: the gate's first phase is Rust, the AWS path and the ported measure tools are gone
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
- [x] T85 Phase 4, the archive cluster with `interactive/record` (`ask:449-T81-slices`, moved by its test, each carrying the T065 clause and named at the phase-3 close): `quote_verbatim`, `sources`, `attempts`, `source_pages`, `reserve-prefix`, `apply_edits`, `uncited`, `uncited_imports`, `archive_ops`, `archive`, `entry_owed`, `record_prepass`, `style_prepass` (`ask:449-T88-bundles`); Rust `downloads`' by-path run of `reserve-prefix.py` ends here
      research: rendering
      verify: DONE. folded into the phase-4 slices by ask:449-phase4-slices (the round arbiter, 2026-11-15): its files go to S2 (T145), S3a (T146), S3b (T147) and S6 (T149), its interactive/record to S1 (T144) and S5 (T148); its stale 'downloads runs reserve-prefix' corrected there (downloads runs archive_ops.py inbox, S3b)
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
- [x] T90 Phase 3, the engine's pipeline package (`l7r/diagram/pipeline/`, phase 3 by FR-001, filed by `ask:449-T89-reviews`); `bundle_door.py`'s `is_current` verb leaves when it lands
      research: rendering
      verify: DONE. closed as moved, nothing ported: ask:449-T90-scope (the round arbiter, 2026-11-12) moved l7r/diagram/pipeline/ to phase 4, its own task T128; FR-001 amended
- [x] T91 Phase 3, the GM-review queue (`scripts/gm_review.py`, phase 3, filed by `ask:449-T82-claims`); `bundle_door.py`'s gm-review write verb leaves when it lands
      research: rendering
      verify: DONE. landed: gm_review.py ported to Rust (l7r-gate gm-review): 1,272 differential cases, 8 explained (row values no writer produces), the in-process callers 55 with none; make static, rust-test and hooks-test green
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
- [x] T122 The idle-tests suite's waits in milliseconds: its fixture waits 1 to 4 s of real time a case (the timer counts awake time in real ticks), 35.0 s alone and the full hook run's longest suite, about 20 s of it waits; a model of the run's eight slots puts the run at 28 s with the suite at 15 s, against 44 s as run (2026-11-12, /tmp/claude-1000/-diagram/d2dc8c63-4103-4cf9-bc83-e73a2fae792a/scratchpad/r5/profile.sh and the schedule model) (the GM 2026-11-12, pre-approved: "if you identify concrete targets with significant measured expected savings then go ahead and do them")
      research: rendering
      note: not landed - its plan review (BLOCKED, 2026-11-12) held it to the GM's condition: the suite alone fell from 35.0 s to about 17 s, but the full hook run did not move (52.1 s against 53.1 s and 54.1 s), so no significant saving in the loop he is speeding up; the change is kept as a patch until the run's real bound is found
      verify: DONE. landed: the full hook run a third faster from a cool start; static, rust-test and hooks-test green
- [x] T123 The hook suites started longest first, from each suite's last time: the eight slots take the roster in its order, the longest suite 34th, the model 44 s as run against 35 s longest first (2026-11-12); T98 measured longest first slower (74.8 s and 77 s against 63.8 s), so it lands only on a fresh A/B (the GM 2026-11-12, pre-approved: "if you identify concrete targets with significant measured expected savings then go ahead and do them")
      research: rendering
      note: not built - T122's full hook runs (53.1 s and 54.1 s against 52.1 s) showed the run is held by something its suites share, not by its schedule, so the model's saving does not hold and the GM's condition (a significant measured expected saving) is not met; to be closed or rescoped once that bound is found
      verify: DONE. done by T125, which landed it measured: hook suites started longest first by each suite's last time, the full hook run a mean of 52.5 s against 59.4 s (2026-11-12)
- [x] T124 The claims-door verbs only land.py asked (scope_split, file_left, flight_live, CLAIMS_FEATURE_DIR) and seam::file_left removed, with claims_door.py's forwarders: kept through T121's landing commit so the Python land.py could land its own deletion (ask:449-T83-scope), landed by the Rust land after it (T121's plan review, 2026-11-12)
      research: rendering
      verify: DONE. landed: the four claims-door verbs only land.py asked removed; whole-tree census clean, make static and rust-test green; the Rust land's first landing
- [x] T125 The hook suites started longest first by each suite's last time: the full hook run (every gate's and landing's longest phase) ends on idle-tests, 36 s started 19.6 s in by roster order; idle-tests first measured 51.3 s mean against 59.6 s, longest first by last time 52.4 s (2026-11-12, scratchpad/r6) (the GM 2026-11-12, pre-approved: "if you identify concrete targets with significant measured expected savings then go ahead and do them")
      research: rendering
      verify: DONE. landed: hook suites started longest first: full hook run mean 52.5 s against 59.4 s, three alternated runs a side; the engine-freeze roll race fixed, eight runs green
- [x] T126 The gate wrapper's per-call cost cut: scripts/gates/l7r-gate.sh looked up its home with getent, id and cut (about 4.4 ms) and walked 835 source paths in bash (about 5 ms) on every call, about 22 ms against the binary's 5 ms; read in the shell and one find, 10.5 ms a call, the full hook run a mean of 46.6 s against 51.5 s over two alternated A/Bs, twelve runs (2026-11-12, scratchpad/r6/wrap.txt and wrap2.txt) (the GM 2026-11-12, pre-approved: "if you identify concrete targets with significant measured expected savings then go ahead and do them")
      research: rendering
      verify: DONE. landed: the gate wrapper's per-call cost cut (22 ms to 10.5 ms): the full hook run a mean of 46.6 s against 51.5 s over twelve alternated runs
- [x] T127 Phase 3, the closing check (scripts/gates/close_check.py, phase 3 by FR-001, held by no task until T91's plan review, 2026-11-12); the gm-review port runs it by path from L7R_GATE_TREE on the one branch where the GM's box is a feature's last open box (T91), which goes when it lands
      research: rendering
      verify: DONE. landed: close_check.py ported to Rust (l7r-gate close-check): 1,645 differential cases, 2 explained; make static, rust-test and hooks-test green
- [x] T128 Phase 4, the engine's pipeline package (l7r/diagram/pipeline/: gencache, regen, rollcache, poolmaps, pool_index, render_cache, record_build, with codeid.py going with its last Python caller), moved from phase 3 by ask:449-T90-scope beside the Mode A generators it runs; make map, make pool-index and make render-sync are planned as a whole here, and bundle_door.py's is_current verb leaves when it lands
      research: rendering
      verify: DONE. folded into the phase-4 slices by ask:449-phase4-slices: record_build to S5 (T148), poolmaps to S11 (T156), gencache, regen, pool_index and render_cache to S12 (T157), rollcache, pipeline/codeid and _census deleted unported there (Q8)
- [x] T129 Phase 3, the hook libraries no task held (phase-3 census, 2026-11-12): scripts/hooks/lib/usage_log.py (85; the Makefile's  starts Python on every make), hm_escape.py (157) and hm_shape.py (594), onto the guard's shared::escape and shared::shape; hm_tree.py (520), which nothing runs, deleted
      research: rendering
      verify: DONE. landed: the hook libraries ported (usage_log, hm_escape, hm_shape; hm_tree deleted): 7,854 differential cases, none differing; make static, rust-test and hooks-test green
- [x] T130 Phase 3, the deletion and retire classes (ask:449-phase3-remainder) Q4/Q5: the 44 specs/ files nothing runs and the specs shell scripts that only run them, l7r/diagram/tools/caption_decl.py and hit_share.py, uncovered-in-diff.py and uncovered_marks.py, deleted unported; every make figures command that fails today or invokes deleted code retired to <retired: ...> with its values kept as history and its file deleted (fr005_probe / ask:449-T79-moves), 387's four placeholder commands retired, 276's measure_before_five run once to place it, 340's harness.py in the class
      research: rendering
      verify: DONE. landed: 138 files nothing runs deleted and broken script commands retired (ask:449-phase3-remainder Q4/Q5): m:recorded-python-commands 4,398 to 48
- [x] T131 Phase 3, the task gate and its last caller (ask:449-phase3-remainder) Q2 task A: scripts/tick-task.py with task_start, plan_hold, phase_sources and wording (ask:449-T066-scope) and tests/test_task_research_boxes.py in one cut, plan_door.py deleted in it; usage_log.py with it only if nothing else runs it
      research: rendering
      verify: DONE. landed: the task gate and tick-task.py ported to Rust (l7r-gate tick, task-start, phase-read): 305 differential cases, none differing; make static, rust-test and hooks-test green
- [x] T132 Phase 3, the review snapshot and the implementation check (ask:449-phase3-remainder) Q2 task B: scripts/reviews/review_snapshot.py and scripts/record/impl_check.py, checks_door.py and claims_door.py deleted with them (each file's imports put to the ask:449-T81-slices test first)
      research: rendering
      verify: DONE. landed: review_snapshot.py and impl_check.py ported, the last Python doors deleted: 829 differential cases, 11 explained; make static, rust-test and hooks-test green
- [x] T133 Phase 3, the six document and agent-file tests as Rust tests (ask:449-phase3-remainder) Q3: test_agent_models, test_citation_rule_inventory, test_claude_md_quotes, test_one_root_claude_md, test_settlement_review_contract, tooling/test_docs_match_the_mechanism (583 lines)
      research: rendering
      verify: DONE. landed: the six document and agent-file tests ported to Rust tests: 51 mutations failing both sides; make static, rust-test and hooks-test green
- [x] T134 Phase 3, the work budget's tools no task held (phase-3 census, 2026-11-12): scripts/measure/work_budget_bundle.py and budget_change.py (1,136 lines), before the task gate (phase_sources imports work_budget_bundle)
      research: rendering
      verify: DONE. landed: the work budget's tools ported to Rust (work-budget-bundle, budget-change): 895 differential cases, none differing; make static, rust-test and hooks-test green
- [x] T135 Phase 3, the authoring tools no task held (phase-3 census, 2026-11-12): claim-feature.py (also run by .specify's create-new-feature.sh), trial-start.py, trial-review.py, task-add.py, set-down.py, make-docs.py (run by the push and the land), patch.py (about 1,160 lines)
      research: rendering
      verify: DONE. landed: the authoring tools ported to Rust (claim, trials, patch, make-docs, task-add, set-down): 344 tool cases, 1 ruled difference, 27 make cases with none; make static, rust-test and hooks-test green
- [x] T136 Phase 3, the review census and the agent sync no task held (phase-3 census, 2026-11-12): scripts/reviews/review_census.py and agent_sync.py with tests/test_agent_sync.py (216 lines)
      research: rendering
      verify: DONE. landed: the review census and the agent sync ported to Rust (reviews census, agent-sync): 163 differential cases, 3 explained; 12 mutations failing both sides; make static, rust-test and hooks-test green
- [x] T137 Phase 3, the page sessions' tools no task held (phase-3 census, 2026-11-12; routed to T81 and T83, which closed without them): page_session_runner.py, brief_load.py, escape_log.py, coord.py, research_claims.py (1,080 lines)
      research: rendering
      verify: DONE. landed: the page sessions' tools ported to Rust (pages crate): 1,727 differential cases, 1 ruled difference; make static, rust-test and hooks-test green
- [x] T138 Phase 3, the research search no task held (phase-3 census, 2026-11-12): research_search.py and semantic_index.py (520 lines), after T85 (both import archive in process)
      research: rendering
      verify: DONE. landed: phase 4 S4, the research search: 174 differential cases none differing (verify run), vectors bit-identical; make static, rust-test and hooks-test green
- [x] T139 Phase 3, the past features' measurement scripts still run and working (ask:449-phase3-remainder) Q4: 238 inventory_shares, 239 change_size, 242 inventory_census and note_census, 261's five working scripts, 430 full_reasons, 432 triage_price, ported as make figures re-runs them
      research: rendering
      verify: DONE. landed: the past features' measurement scripts ported (l7r-gate measure spec): 574 differential cases, none differing; 29 recorded commands rewritten and re-run; note_census retired
- [x] T140 Phase 4, the tools that reach Mode A or interactive/ (ask:449-phase3-remainder) Q1: building_programs, footnote_census, glossary_asset, notes_census, the pack_audit package, picture_diff, record_asset, source_tags_contract and scripts/gates/memo_check.py (each under the T065 clause, named at the phase-3 close), page_lit onto T85's one browser crate, tools/__init__.py, _census.py and work_counts.py with their last importer, 335's harness.py; and the pytest infrastructure's removal commit with the last kept pytest test (test_mode_a_sheets): conftest.py, the two __init__.py, _scope.py, _gate_failures.py, _heap.py, _memory.py, tooling_reuse_time.py (its three 383 commands retired)
      research: rendering
      verify: DONE. folded into the phase-4 slices by ask:449-phase4-slices: S5 (T148), S7 (T150), S9b (T153), S10a (T154), S10b (T155) and S11 (T156), the pytest infrastructure's removal in S11; its tooling_reuse_time.py already deleted by T133
- [x] T141 The review-round guard's Python hop removed: review_round_hooks.rs starts python3 on an inline snippet that only runs l7r-gate.sh plan door active-task and parses its JSON, on each spec-fidelity dispatch; the guard runs the gate command itself (found by T131's plan review, 2026-11-12)
      research: rendering
      verify: DONE. landed: the review-round guard asks the gate for the active task itself, no python3 snippet; guard tests (556) and hook suites green
- [x] T142 Ticked tasks archived out of tasks.md into tasks-done.md, as ticked tasks' plan sections already go to plan-done.md, and every reader of a feature's tasks reading both (the next free task number, the spec-kit state, the closing check, the tick's already-ticked and landed checks, the research boxes, the feature report): 449's tasks.md holds 131 ticked tasks of 137, about 63 KB read whole by every session and agent that opens it (the GM 2026-11-15: "please do that, because I imagine that will make our long-running featuers with tons of tasks much more token efficient")
      research: rendering
      verify: DONE. landed: ticked tasks archived to tasks-done.md, every reader reading both: 1,001 outputs with none differing; 449's tasks.md 63,691 to 6,040 bytes; make static, rust-test and hooks-test green
- [x] T143 Phase 3, the shell libraries' inline Python (ask:449-phase4-slices) Q12: scripts/hooks/lib/guardlog.sh and clone-resolve.sh (sourced by five *-gate.sh, l7r-guard.sh and sync-with-main.sh on every run) and .specify/scripts/bash/common.sh's four sites, onto the Rust; before S1
      research: rendering
      verify: DONE. landed: the shell libraries' inline Python replaced (guardlog.sh, common.sh; clone-resolve.sh deleted): 2,558 differential cases, none differing; make static, rust-test and hooks-test green
- [x] T144 Phase 4 S1, the record's core (ask:449-phase4-slices): interactive/record's split, assemble, absence, contents, fragments, notes, originals, passages, questions, confusables, xref, store, site_notes, source_tags, blocked, archive and __init__, with interactive/sources.py and content.py (2,721 lines), extending core::record; its own task, since S2-S12 import it
      research: rendering
      verify: DONE. landed: phase 4 S1, the record's core as a Rust library: 378,360 recorded calls replayed, none differing; make static, rust-test and hooks-test green
- [x] T145 Phase 4 S2, T81's cut together (ask:449-phase4-slices), ask:449-T80-order: scripts/record/sources, attempts, reserve-prefix, quote_verbatim, source_pages, record_prepass, style_prepass, apply_edits (3,075 lines); retires owed/answers.rs REPLY_OF, owed/translation.rs READER and parser_key, bundle_door's run, passages and save_cached verbs, blocked_fetch_hooks.rs's by-path run
      research: rendering
      verify: DONE. landed: phase 4 S2, T81's record tools in Rust: 1,261 differential cases with two ruled differences, the write paths 204; make static, rust-test and hooks-test green
- [x] T146 Phase 4 S3a, the one browser crate (ask:449-phase4-slices) Q4: scripts/record/archive.py and glyph_crop.py over CDP (995 lines), the crate page_lit later uses; retires depiction.rs's include_str! and python3 run and the Playwright install in setup-dev-env.sh; before S3b (ask:449-T80-order's condition met by S1)
      research: rendering
      verify: DONE. landed: phase 4 S3a, the one browser crate: 109 differential cases with one explained difference, 36 crops identical, a kept end-to-end case; make static, rust-test and hooks-test green
- [x] T147 Phase 4 S3b, the uncited cluster (ask:449-phase4-slices): scripts/record/uncited, uncited_imports, archive_ops (1,623 lines); retires downloads.rs's by-path run of archive_ops.py inbox
      research: rendering
      verify: DONE. landed: phase 4 S3b, the uncited cluster: 128 differential cases none differing (verify run), make static, rust-test and hooks-test green
- [x] T148 Phase 4 S5, the record's site (ask:449-phase4-slices): record/site, site_pages, site_links, money, citations, glossary, glossary_source, tools/record_asset, glossary_asset, footnote_census, source_tags_contract, scripts/gates/memo_check.py, pipeline/record_build (2,164 lines); retires push.rs's memo_check and record-build runs
      research: rendering
      note: owed from T144's plan review (2026-11-16), where S1's library has no caller: wiring a caller that printed a KeyError's str(e) keeps its quotes; and research::host's tabs and missing NFKC, against urlsplit, need their own decision once live fetch URLs reach it beside the blocked-domain list
      verify: DONE. landed: phase 4 S5, the record's site: the real site byte for byte, 71 differential cases with the stamp the one ruled difference; make static, rust-test, hooks-test and quick green
- [x] T149 Phase 4 S6, the registries and their readers (ask:449-phase4-slices) Q5: interactive/classes/*, compound_kinds/*, conditions, choices, entry_owed, check-entry-headings, open_questions (2,225 lines), the modal prose moved verbatim to one Markdown file per class and kind (the FR-002 ruled case, an old-to-new id map); owed_door, record_door and record_cache deleted (756)
      research: rendering
      verify: DONE. landed: phase 4 S6, the registries: 45 differential cases none differing, the modal id map empty; make static, rust-test, hooks-test and quick green
- [x] T150 Phase 4 S7, the map page writer (ask:449-phase4-slices) Q13: interactive/page, place, raster, extents, notes, tags, sheet, dwellings, picture_diff, page_lit onto S3a's crate, the image crate for PIL and numpy (2,912 lines); interactive/__init__ deleted; what page.py writes today, the Mode A sheets' pages
      research: rendering
      verify: DONE. landed: step 2: the page writer and its diagnostics in Rust, 135 differential cases none differing, 497 claims checked
- [x] T151 Phase 4 S8, labels (ask:449-phase4-slices) Q7: labels/* and work_counts (2,397 lines), shapely onto the geo crate, FR-002 binding what is written
      research: rendering
      verify: DONE. landed in batch T151+T181: step 3a: the labels in Rust and the shrine drawn by Rust, its checks as before, 310 claims checked; and T180's measure reworded to the GM's must-pass sense
- [x] T152 phase: compound - the Mode A compound generator rebuilt in Rust from its SOUND derivation (T208), never ported (the GM 2026-10-30 and 2026-11-19; T199): the two generated compound sheets (county-magistracy-example, ochiba-roundtrip-test) drawn by Rust from their programs, each passing its checks (make pack-audit, the census, the size table) and holding docs/buildings.md's composition rules and the research claims they rest on, captions placed by T202's caption_place, its counters within twice each sheet's budget; the old Python (compound*.py, compound_parts.py, compound_model.py, well_gear.py, labels/*.py - and compound* moved here from T156) and its lockstep tests deleted in the landing, the generators' .gen.py wiring kept; the side-by-side page of every pool sheet before and after published for the GM (engine-plan.md)
      research: rendering
      phase: compound
      derivation: specs/449-rust-codebase/derivations/T208-compound.md
      old-code: l7r/diagram/compound.py l7r/diagram/compound_example.py l7r/diagram/compound_model.py l7r/diagram/compound_parts.py l7r/diagram/compound_view.py l7r/diagram/well_gear.py l7r/diagram/labels/*.py
      verify: DONE. landed: the compound generator rebuilt from its derivation; the old Python deleted
- [x] T153 Phase 4 S9b, pack_audit's leaves (ask:449-phase4-slices): tagged, parse, grids, onmap, labels, marks_drawn, size_marks, sun, palette (1,586 lines)
      research: rendering
      verify: DONE. done by T170 (tagged, parse), T174 (grids, size_marks) and T175 (onmap, labels, marks_drawn, sun, palette), which landed them measured: each ported into rust/mode_a and held to its Python by the lockstep, make pack-audit's 207 differential cases none differing
- [x] T154 Phase 4 S10a, pack_audit's core (ask:449-phase4-slices): checks, shared, program_rules, roads, mapmatch (2,142 lines)
      research: rendering
      verify: DONE. done by T175, which landed it measured: checks, shared, program_rules, roads and mapmatch ported into rust/mode_a/src/audit and held to their Python by the lockstep, make pack-audit's 207 differential cases none differing
- [x] T155 Phase 4 S10b, pack_audit's registry (ask:449-phase4-slices): __init__, registry, report, __main__, notes_census, size_table, building_programs (1,123 lines); make pack-audit, notes-census, size-table and building-programs Rust
      research: rendering
      verify: DONE. done by T168 (building_programs), T170 (notes_census), T174 (size_table) and T175 (__init__, registry, report, __main__ deleted), which landed them measured: make pack-audit, notes-census, size-table and building-programs run the Rust, each held by its differential with none differing
- [x] T156 Phase 4 S11, the Mode A top and pytest's exit (ask:449-phase4-slices) Q6, Q9 - split by its scoping of 2026-11-19 into four landings: T210 (dead measurement tooling), T211 (the Rust pool sweep), T212 (the Python audit and its lockstep retired), T213 (pytest's exit); compound* went to T152, resvg is a library since T150, and the six .gen.py's one Rust sheet driver with a spec file per map is folded into T157, whose pipeline finds maps by their .gen.py; T156 is ticked when T210-T213 are
      research: rendering
      verify: DONE. landed in batch T156+T214: T156 done through T210-T213; T214 done by T213
- [x] T159 The pre-review count check: make decide refuses a count (lines, cases, files ...) whose sentence carries no label, the plan review's commonest unreviewable return (request.md 2026-11-16)
      research: rendering
      verify: DONE. landed: make decide refuses an unlabeled count; plan crate tests green, coverage complete; ask:449-T159-rounds
- [x] T160 Compile and test speed, the GM's third approved proposal (request.md 2026-11-16), ordered last: first measure where compile and test time goes across a port task, then take any target with a significant measured saving
      research: rendering
      verify: DONE. landed: compile and test speed: the checks runner side by side with kept views, the slowest and flaky tests fixed; static, rust-test and hooks-test green
- [x] T161 The differential runner, the GM's second approved proposal (request.md 2026-11-16) enforced by tooling (the GM 2026-11-11, 'our tooling must enforce this'): one shared runner in the repository that keys each case by the inputs and code it runs and reruns after a fix only the cases whose key moved, the port briefs from T147 on using it
      research: rendering
      verify: DONE. landed: the shared differential runner and its lint; 16 real cases rerun 32/0/6/16 sides across a first, a no-change, a one-file and a verify run
- [x] T162 The clone-sync guard's launcher exemption for a forked background session: a session started with --fork-session --resume <parent> treats that parent as its dispatcher, as L7R_DISPATCHER does for a page session (found by T147's port agent, refused in its own clone)
      research: rendering
      verify: DONE. landed: the clone-sync guard's forked-session dispatcher; guard tests green, coverage complete, the test failing without the fix
- [x] T163 The record check's kept pass keys today's UTC date, so a pass cannot be replayed after an archive row's seven-day pending window ends (a defect T148 found in the Python's check and, holding FR-002 in the port, left for its own commit; constitution XIV)
      research: rendering
      verify: DONE. landed: the record check's kept pass keys the date; research tests green, the test failing without the fix; make static clean
- [x] T164 Three defects T149 found, each fixed (constitution XIV): the entry-headings check never covered the 99 Mode A kinds; diffrun's a_bare_world_compares_everything_under_it fails under load; eleven owed-crate tests run over FR-008's tenth of a second
      research: rendering
      verify: DONE. landed: three defects T149 found, each fixed: entry-headings over both registries with old lines byte-kept, a flaky diffrun test, the owed crate's slow tests under FR-008
- [x] T165 The claims tooling over Rust engine units before the engine ports (the GM 2026-11-17: port the claims tools before the map engine): the stale-figure check (claims_stale, a changed constant's old figure on a drawing page) and the counter-only clear (claims_counters) made to work on Rust units as they work on Python's, and the rest - context, fingerprints, carry, tunables - confirmed on a Rust unit end to end
      research: rendering
      verify: DONE. landed: the claims tools over Rust units: stale figures and counter-only clears firing on real rust/phases changes, the Python cases unchanged
- [x] T166 The claims tooling's two gaps T165 found before the engine ports: a claim carried from a deleted .py unit onto its Rust port (carry matches by code fingerprint, which a .py and a .rs unit never share; 367 .py claims), and a Rust unit's fingerprint holding the constants it reads as a Python unit's does (111 of 398 claimed Rust functions), migrated without re-owing unchanged code
      research: rendering
      verify: DONE. landed: claims carry across a port and a Rust fingerprint holding its read constants; the migration owing nothing, a ported claim checked IN-STEP
- [x] T167 FR-008's remaining debt after T160: 151 tests over a tenth of a second (scratchpad t160/ws-after.rows), and the ruling on the real-tree tests (checks' research pointers, tooling detector and question size; task's research boxes; research's site cases; the guard's r6 corpus) that are not declared a tool's one end-to-end test
      research: rendering
      verify: DONE. landed: FR-008's debt: every ordinary test under a tenth of a second, eleven end-to-end tests declared; static, rust-test and hooks-test green
- [x] T168 The engine pilot, piece 1 of step 1 (the GM 2026-11-17, request.md: a pilot measured by phase, then a second piece): building_programs.py and the buildings.types registry it reads, ported into a new engine crate and wired (make building-programs), the Python command deleted, types.py held in lockstep for the generators; its wall time and tokens reported by phase
      research: rendering
      verify: DONE. landed: the engine pilot, piece 1: building_programs and the building types in rust/mode_a, wired; 76 differential cases none differing; 80 claims IN-STEP
- [x] T169 The engine pilot's no-brainer process fixes (the GM 2026-11-17, pre-approved): the differential's worlds sparse (T168's first run 307 s against 50 s), the claims form checked by make static before landing, the plan review's bundle carrying every arbiter ruling a block cites, and a per-test timer for FR-008
      research: rendering
      verify: DONE. landed: the pilot's process fixes: sparse worlds for iterating with whole-world verifies, the claims form at make static, rulings in the plan bundle, make test-times
- [x] T170 The engine pilot, piece 2 of step 1 (the GM 2026-11-17, request.md: a second real piece, measured after the pilot's fixes): notes_census.py wired (make notes-census) with what it reads - pack_audit's parse.py and tagged.py (the plan's SVG parse, ten research claims) and interactive/sheet.py's SVG reader - ported into rust/mode_a, the Python they serve held in lockstep; its wall time and tokens reported by phase
      research: rendering
      verify: DONE. landed: the engine pilot's second piece: notes_census, the sheet parse and the sheet reader in rust/mode_a, 105 differential cases none differing, 176 claims IN-STEP
- [x] T171 The notes census's entrance-board line and its freshness test (constitution XIV; found by T170): since feature 444 cut the tool's entrance-board branch, an entrance-seated notice board's census line reads a 250-ft farmhouse count, which feature 261 does not judge a board by - fix the line (the ways-out count ported onto the manifest, or the line left out for an entrance seat, the easier route named); restore the freshness test feature 444 dropped on a wrong label (feature 193 kept notes-census for it); regenerate the four hamlets' notes ROUTES (round arbiter, ask:set-down-449-pilot, 2026-11-17; the GM's to choose): (a) the ways-out count ported onto the manifest - keeps the fact in the four hamlets' notes; the count's Rust is `rust/parked/src/law/routes.rs`'s `departure_routes` over the manifest's `lanes` and `houses`, engine-side work; or (b) the line left out for an entrance-seated board - simpler, drops the fact.
      research: rendering
      verify: DONE. landed in batch T171+T177+T182: step 1's defects: the stale notes, the pack audit's ports, the round-trip's rooms at their measured sizes
- [x] T172 The claims walk's Rust items read raw strings (constitution XIV; found by T170's claims round): the splitter's item end takes a raw string literal's inner quote for its close, so a static after one is swallowed into the unit before it and gets no key of its own - raw and byte-raw literals read to their own close, the units the fix reshapes re-checked
      research: rendering
      verify: DONE. landed: the claims walk reads raw strings to their own close; 50 claims IN-STEP
- [x] T173 make diff-run JOBS=n: a run's cases side by side, each in its own world (the GM 2026-11-17, request.md: no-brainer process fixes from the pilot; T170's verify run took 392.6 s, its cases' own commands 11.6 s of it, the rest a whole world built and removed for each of 210 sides one after another) - opt-in, results and the report's order unchanged
      research: rendering
      verify: DONE. landed: make diff-run JOBS=n: T170's verify 375.8 s serial, 151.5 s at JOBS=4, reports equal
- [x] T174 The engine's piece 3 (the GM 2026-11-17, request.md: the next two pieces, measured): make size-table wired to Rust - scripts/reviews/size_table.py with what it reads, pack_audit's size_marks.py and grids.py and labels/hand_sheet.py's start_tags, ported into rust/mode_a, the Python they serve held in lockstep; its wall time and tokens reported by phase
      research: rendering
      verify: DONE. landed: the engine's piece 3: make size-table in Rust, 113 differential cases none differing, 138 claims IN-STEP
- [x] T175 The engine's piece 4 (the GM 2026-11-17, request.md: the next two pieces, measured): the rest of the audit - pack_audit's onmap, labels, marks_drawn, sun, palette, program_rules, roads, mapmatch, shared, checks, registry, report and its command, with compound_parts' three predicates and compound_model's constants they read - ported into rust/mode_a and make pack-audit wired to it; the Python the generators and tests still import held in lockstep; step 1 closed; its wall time and tokens reported by phase
      research: rendering
      verify: DONE. landed: the engine's piece 4: the whole audit in Rust, make pack-audit wired, 207 differential cases none differing, step 1 closed
- [x] T176 The audit's placement rules labeled (constitution XII, found by T175's claims round): the Rust units of the audit are keyed one by one where the Python's walk keyed only a unit with its own claim, and about 40 of them carry a rule under their module's NONE - floating_doors, occluded_foreground, arch_on_approach, hall_at_an_end, sanctuary_on_axis, shrine_tree, well_clear_of_arch, privies_by_zone, fire_water_distribution, lodging_entrances, HIERARCHY, TUB_KINDS, end_meets, gate_feeds_its_road, the sun's wall and tree heights, the palette's colors and more (make claims-report): each given the page that attests it, CONVENTION, GUESS or UNRESEARCHED, a research pass where a placement question has none; the Python copies' claims to match
      research: rendering
      verify: DONE. landed: the audit's placement rules labeled, claims text only, no code changed; 148 claims checked, their departures from the pages filed as T177
- [x] T177 Six audit rules brought to their pages (constitution XIV; found by T175's and T176's claims rounds, DRIFTED): the notice board casts no shadow though 0190 measures it 10-11 ft high; a road refused when wider than its gate though 0088 draws the road at a compound's gate at its own width; arch_on_approach refuses a first arch 0220 lets move inward; gate_widths' fix text gives a width outside 0093's bands; no_precinct_enclosure's message calls a sanctuary fence a donation where 0223 draws none; lodging_entrances passes one door per joined block where 0097 and 0106 give each dwelling its own - each fixed in both the Python and the Rust copy, the pool sheets' verdicts measured before and after
      research: rendering
      verify: DONE. landed in batch T171+T177+T182: step 1's defects: the stale notes, the pack audit's ports, the round-trip's rooms at their measured sizes
- [x] T178 The lockstep's Python half kept (the GM 2026-11-18, request.md: the efficiency fixes): rust/mode_a's one end-to-end test runs the Python's readings of every sheet and fixture each time, 7.9 s, so an edit cycle took 15 s in T175; its Python half's output kept by a key over everything it reads (the Python sources, the sheets, fixtures, manifests, types.json and the dump script), rerun only when the key moves
      research: rendering
      verify: DONE. landed in batch T178+T179: the lockstep's Python half kept and diff-run's whole worlds reused, measured before and after
- [x] T179 make diff-run's whole worlds reused (the GM 2026-11-18, request.md: the efficiency fixes): a verify run builds and removes a whole checkout for every case side; each worker's whole world made once a run per side and reset between cases to the revision's tree, held equal to a fresh world by a test
      research: rendering
      verify: DONE. landed in batch T178+T179: the lockstep's Python half kept and diff-run's whole worlds reused, measured before and after
- [x] T180 No exactness standard for a port (the GM 2026-11-18, request.md: "amend our project guidelines and speckit constitution and whatever else we need to update to clarify this and remove any references to things needing to be bitwise identical or anything like that as an exactness standard"): a port's outputs may differ from what they replace so long as everything works - its tests pass, it does its job, its research claims hold - the audit checks' verdicts the one measure kept exact; the constitution, spec.md's FR-002 and its ruled cases, engine-plan.md, docs/, dev/ guides and the CLAUDE.md files amended, every bitwise or byte-for-byte exactness standard removed
      research: rendering
      verify: DONE. landed: no exactness standard for a port: the constitution, FR-002, the engine plan, the guides and the review agents amended to the GM's rule
- [x] T181 T180's kept measure reworded to the GM's sense (the GM 2026-11-18, request.md: "surely you mean the audit checks must pass"): a drawn output must pass its checks and hold its research claims; a ported check must still do its job - its red fixtures still fail, its good sheets still pass, a check fixed on purpose changing as fixed - never "verdicts kept exact" as a standard; wherever T180 wrote it
      research: rendering
      verify: DONE. landed in batch T151+T181: step 3a: the labels in Rust and the shrine drawn by Rust, its checks as before, 310 claims checked; and T180's measure reworded to the GM's must-pass sense
- [x] T182 Step 1's known defects fixed before step 3b (the GM 2026-11-18, request.md: "fix all known bugs in each step before moving on"), in the Rust and the kept Python alike: the sheet reader pairs kinds by index, so a '>' in CDATA before a tag-like run shifts later kinds and a name outside [A-Za-z] overruns the start tags (T174); a single-quoted data-kind reads untagged (T174); the tokenizer refuses a sheet ElementTree accepts (T174); gap_tag never enforces the kura fire gap's floor (T175); the ink's path_points drops relative path commands (T175); the On-map error quotes the line break after the bad line (T175); the county red fixtures carry no tier (T175); privies_by_zone checks one of a residence's two privies (T176); registry.ft and three unreachable branches removed (T175); the claims round's open items on the audit (T176's second round: the shoe-stone door, no tub inside a building or roofed court, a tub off a well, the kura roles, a road's ending, the well-or-basin of 0222 against 0196); with T171 and T177 the step's other two
      research: rendering
      verify: DONE. landed in batch T171+T177+T182: step 1's defects: the stale notes, the pack audit's ports, the round-trip's rooms at their measured sizes
- [x] T183 Step 2's known defects fixed before step 3b (the GM 2026-11-18, request.md): hit_copies copies an element's id into a d attribute, a path getting two (T150); size_sentence multiplies a households value given as text (T150); a refused render leaves an empty page (T150); the TIFF modes and oversize ICO the diagnostics refuse, read and shrunk as PIL did where the image crate allows (T150)
      research: rendering
      verify: DONE. landed: step 2's four known defects fixed, each with a test that failed before
- [x] T184 Step 3a's known defects fixed before step 3b (the GM 2026-11-18, request.md), in the Rust and the kept Python alike: a leader's block touching a line subject that bends back divides by zero; a one-point line subject raises; a tag starting with '_' raises; a prefixed caption text element raises; a zero-size caption loops forever in the Python; a non-finite coordinate refused in other words than the Python's (T151 part A); and T151's claims round: the association gap asked only of the first ring where the claim gives it every leaderless ring; an area taller than ELONGATED times its width turned 90 degrees where 0242 keeps an area's caption level; docs/buildings.md's caption prose against 0242 on when a leader is drawn; obstacles' names_group fallback, the block, stepped, wall and face constants, a leader's end trim, a turned subject's angle and a stranded multi-line caption's wrap each given its own claim or class; caption_clears_ways' way cost judged with ObstacleIndex in its bundle
      research: rendering
      verify: DONE. landed: step 3a's listed defects fixed in both copies, each code fix with a test red before
- [x] T185 The regex scans that loop forever past their step limit (constitution XIV; found by T151 part B): a pattern with a word boundary on a long line makes the regex library give up past its step limit and return the same error without advancing, so a scan loop that retries never ends - T151 fixed it in the house-style delta check (make quick hung on a 157 KB one-line file); the same skipping of a regex's error stands at other call sites under rust/ (152 by T151's recorded search), the edit guard house_style_hooks.rs among them - each made to end on the error, with a test proving it fires; the same class hung `make task-add` and `make decide` once 449's plan files neared 1 MB (fancy_regex's 1,000,000-step limit, a `.flatten()` scan retrying its error forever) - fixed in the plan and task crates with T194, tests red on the old code; the rest of the class (276 `.flatten()` scans in 115 files, core's `record::units::re`, `checks::re`, `measure::tool_inventory::re` and about 45 guard patterns, six of which already err at the limit on 449's plan files) is this task's (2026-11-18, scratchpad lint-spin/)
      research: rendering
      verify: DONE. landed: no regex scan spins past the step limit: one unlimited constructor, scans ending on an error, eight quadratic patterns rewritten, a tree-wide guard; tests red on HEAD
- [x] T186 make claims-bundle's UNITS run through the shell (constitution XIV; found by T182's claims round): the recipe passes "" inside double quotes, so a claim key with a backtick (docs/building-programs.md's 'the required item is `well`') is executed as a command and the bundle refused - every make target that hands a claim key, a reason or other free text to a recipe passes it so the shell never reads it (an environment variable, as the escape reasons do), with a test of a key holding a backtick, a dollar sign and a quote
      research: rendering
      verify: DONE. landed: free text reaches make's recipes through the environment; a hostile-value suite test red on the old Makefile; the suites and the hooks stamp hold the Makefile
- [x] T187 Step 1's third claims round's findings, fixed before step 3b (the GM 2026-11-18, request.md: "fix all known bugs in each step"): lodging_entrances lets an undivided barracks or long-house pass as 0097's common room, which 0097 gives the servants' quarters alone; the well curb sized 3 to 4 ft where 0196 gives about 4; the well-and-basin rule's label (0222 and 0196 now answer it); the basin's plan size and roof unclaimed; a doorless building's tub falling back to its end faces where 0100 puts the bath's on its yard side; the basin by the innermost arch (0222); the late-Edo fence along an approach (0223) unruled; the hilltop shrine's well (0196); the sanctuary band past its attested widths; the county example's claims impl-drift found drifted on 2026-11-18 (the hearing court drawn 80 x 26 against its page's 80 x 32; the servants' row claim's 76 ft against the 60 ft drawn; storehouse (W) at 16 x 19 against the page's ~12 x 18 and Yokota's pair; the divider gate's 'narrower than the main gate' rule against a gate rolled at 6 ft; the residence's massing, room order and veranda faces fixed where the pages make each a seeded knob), its stale comments (the gatehouse 18 x 12, the stables door's side, the servants' row's 76 ft), the gate-range roll drawing no range building, the vegetable garden size claim citing its page 0109, and the record's two disagreements it found (building-programs.md's divider width UNRESEARCHED against its claim's GUESS; 0104 §102 calling the service-side well accurate against 0105 §204's GUESS); the corridor's two ends leading to the house's door and privies, and its dotted edge drawn where it does not lie on a room wall (the round-trip's corridor glyph reviews); the size audits' measured rooms (the Matsue 10-mat zashiki and 8-mat next room, the Yokota house's rooms, JAANUS's 6-12-mat main room; their findings files hold the passages) quoted onto 0091 by a record session, so the room pop-ups may name them (the modal-research round of 2026-11-18 found no page carrying them, and they were recast as the plan's guess); the in-house corridor's drawing convention (a lighter strip with a dotted edge) recorded on 0091's drawing page, with what a samurai house's inner corridor looked like if a search finds it (the modal-depiction round of 2026-11-18); 0004's drawing page §13 saying a map's population is its DECLARED households times five, as §25's example and the code have it, and size_sentence's population claim naming the map's own population as the second override (T183's impl-drift, 2026-11-18); 0242's drawing page glossing who Yoeli is in 'Yoeli's scheme' (record-format, 2026-11-18); the room bands on the kinds' pages enforced for generated plans (since ask:449-T182-room-scope no check holds them - the registry's size_bands reads types.json alone); the guest room given a band of its own (45 x 25 ft on Ochiba, unbanded and not faulted; ask:449-T182-room-layout); the placer's choices the round-trip's glyph reviews questioned - the kitchen joining the house at the formal end, away from the family's, the storehouses' backs before the reception's garden face, and the guests' privy reached through the lord's quarters; and for a record session, 0220's innermost-arch label and 0222's hall size against the program band
      research: rendering
      research: rendering
      verify: DONE. landed: step 1's leftovers triaged under XIV: 2 defects fixed, 28 restated, 3 dropped; the record checks' real findings fixed
- [x] T188 Step 3a's two placer gaps T184 found, fixed before step 3b (the GM 2026-11-18, request.md: fix all known bugs in each step), in the Rust and the kept Python: the one-text placer keeps a wrap when no wrap clears, where 0242 has a caption go back to one line (it shows on the shrine's 'sanctuary of Bishamon'); a prefixed caption text element, once fixed, written back as plain text, so a sheet binding SVG only to a prefix loses its namespace (T184's report); and T184's claims round (2026-11-18), each in both copies: an area caption levels the inside seat of a single turned rect, where 0242 sets a turned feature's caption at its own angle and keeps level only an area with no direction of its own; names_group and GROUP_WORDS match substrings ('magistrate' names the gate group, any 'estate' the samurai estates), where 0243 means whole words and gives the estates to the samurai caption alone; ring 1's exemption from the association test given a test it can pass, or recorded on 0242's drawing page as a DEVIATION with T184's measurement (13 ring-1 captions to 0); WAY_NOTCH's unit stated (2 sheet units is 2/3 ft on a hand sheet); Sheet.one's ground rule citing 0242, not CONVENTION; a beside seat's angle turned a half turn when it would read upside down (0242 §46, §53), if the placer does not already; the ground's-name break keeping an inside seat that covers a building over a free seat (0242 §35); and seat's two unclaimed rules (the break, the placing order) claimed
      research: rendering
      verify: DONE. landed: the rest of step 3a's known placer defects fixed in both copies, each with a test red before
- [x] T189 Step 3a's turned-caption edge cases T188's last claims round found, fixed before step 3b (the GM 2026-11-18, request.md: fix all known bugs in each step), in both copies: a turned rectangular holder (a turned garden with its lantern) named level off its upright box when its caption is beside it, and a lone turned block likewise (subjects' single-block branch), where 0242 seats a turned feature's caption at its own angle off its turned edge; squared() claimed citing 0242's angle rule, not NONE, and the area-caption claim naming the unequal ellipse it turns; whether a turned non-rectangular outline (an L-shaped house) and a single turned block among parts have a direction of their own, settled from 0242 (or recorded on its drawing page) and the code made to match
      research: rendering
      verify: DONE. landed: step 3a's turned-caption edge cases fixed in both copies, each with a test red before
- [x] T190 Step 3a: an L-shaped (all-square-cornered, turned) member of a scatter seated beside off its raw outline rather than its turned box (_framed, as the lone-shape branch is), if the seater does not already measure a Point subject off its turned edge (0242 §26), in both copies with a test red first; the turned-angle claim listing scatter members, and squared's 'outline of square corners' claim citing 0242's drawing-page convention bullet rather than calling the page silent, and 'a lone block's beside box' likewise; 0242's drawing page recording the turned holder's beside box (the box of all it holds, in the holder's frame) beside the lone block's placer.py _score's docstring giving T188's ring-1 measurement as 0242 §20 does (13 captions to none, 12 more leader lines, for the test as a whole) (T189's impl-drift, 2026-11-18); before step 3b (the GM 2026-11-18: fix all known bugs in each step)
      research: rendering
      verify: DONE. landed: step 3a's last citations and the scatter member's seat measured unchanged
- [x] T191 Step 3a: a leader to a lone turned L-shaped outline ends at its turned box's nearest point, not the L's own ink - 42 to 80 of 256 ring-9 seats more than 1.5 px off the ink past the leader's 1 px trim in T190's 30/120/200-degree probe - where 0242 ties a leader to the nearest point of the feature; fixed in both copies with a test red first, before step 3b (the GM 2026-11-18: fix all known bugs in each step); and 0242's drawing page recording that an ellipse of unequal radii has a direction of its own, as its convention bullet records the square-cornered outline (T190's impl-drift); and the same bullet saying an outline holding the others with no direction of its own (a corner off square) is seated level
      research: rendering
      verify: DONE. landed: a leader to a lone turned L-shape ends on the shape, in both copies, with a test red before
- [x] T192 Step 3a: a leader to a disc (circle or ellipse) ends on its drawn box, which the reader keeps as its outline, not on the drawn curve - 3 pool leaders end 1.75 to 4.45 px off it (Hayakawa's old pines and striking posts, Ubame's fire-water tubs); and a subject of several parts scores its leader to its box while the hand sheet draws it to the parts' ink - 2 of 33 pool leaders (Hayakawa's striking posts and weapon rack, tips 3.85 and 1.36 px apart, the drawn leader scoring the same, free); fixed in both copies with a test red first, before step 3b (the GM 2026-11-18: fix all known bugs in each step); and subjects' choice of which subjects carry their own outline as `ink` (today a lone shape alone) claimed in both copies (T191's impl-drift: UNCLAIMED)
      research: rendering
      verify: DONE. landed: a leader ends on a disc's curve and on several parts' ink, in both copies, tests red before
- [x] T193 Step 3a: a leader led past a stroke's end ends on a round cap the sheet may not draw, stroke-linecap unread by the reader, so past a thick stroke's flat end it stops up to its half-width short of the ink - nearest_ink and leader_to_ink in both copies, no pool leader so ended (T192's probe) - fixed with a test red first, before step 3b (the GM 2026-11-18: fix all known bugs in each step); and which part a leader ends on: nearest_ink and _nearest_ink choose a part by its stroke's line, an outline winning a tie and the wider stroke a stroke tie, where 0242's drawing page records 'the drawn feature's nearest point - ... a stroke's edge' - either end at the nearest drawn edge or record the line rule and tie order on the page (it is at its 20,000-byte prose cap, so that is the split 'A question has a size' describes), the claims made to match (T192's impl-drift: 4 DRIFTED)
      research: rendering
      verify: DONE. landed: a leader ends on the drawn band and the nearest drawn edge, in both copies, tests red before
- [x] T194 Step 3a's reader gaps T193 found, fixed before step 3b (the GM 2026-11-18: fix all known bugs in each step), in both copies with tests red first: a path's curves kept only by their end points and its dashes ignored (Hoshigaoka's sacred-tree rope, a circle in two arcs, read as a 10 px line doubled back); stroke-linejoin unread, a stroke's bends and a stroked outline's corners measured round where the sheet draws a miter (up to 1.86 px short at a 9 px wall's right angle); then 0242's drawing page recording the leader's tie order (an outline before a stroke drawn along it, the wider of two strokes), which needs the page split along its topics first - it is at its 20,000-byte prose cap (docs/research-record-rules.md, 'A question has a size'); and from T193's impl-drift: stroke_band giving a zero-length stroke a disc whatever its cap, where a butt one draws nothing (code or claim); ink_nearest's claim moved to 'which part a leader ends on'; leader_to_ink's 0.5 px least half-width taken from drawn_ink, not written twice; 'which subjects carry ink' saying 'drawn with its box'; and whether nearest_ink scores a block inside a closed part as leader_to_ink draws it (inside counted as on the ink) - measured, and made to agree if not
      research: rendering
      verify: DONE. landed: the reader's curves, subpaths, joins and dashes in both copies, tests red before; 0242 split into 0330; the plan lint's spin fixed
- [x] T195 Step 3a's last reader gaps T194 found, fixed before step 3b (the GM 2026-11-18: fix all known bugs in each step), in both copies with tests red first: a filled path's hole read as a filled part (Hoshigaoka's grove, one subpath inside another); an unfilled closed part's inside counted as ink; the audit's path walk keeping an arc by its end point, so the viewBox crop misses an arc's bulge; and 0242's drawing page, 222 bytes under its cap after T194's split, split again along its angle and wrap topics; and 0242's place rule ('beyond that the caption is tied to its feature by a thin leader line') linking 0330, where that clause's grounds now sit (quote-check, 2026-11-18); and from T194's impl-drift: subjects' 'which subjects carry ink' citing 0330's drawing page, not 0242, in both copies. Dropped 2026-11-19, the GM's question on the sub-pixel tail answered by root CLAUDE.md's 'a GUESS, UNRESEARCHED or CONVENTION value ... is a goal and a knob, never a target to defend' (escalation-check REWRITE): a dashed closed outline measured solid and a square-capped zero-length stroke in a turned group, which move no caption and contradict no research finding; from here a drift that moves no caption and contradicts no research finding is fixed by restating the claim, not the geometry; and the way weight (T187's impl-drift, CANNOT-TELL): WEIGHT_WAY 500 against WEIGHT_OBSTACLE 1000 lets a seat covering one building beat a seat crossing three ways, against 0242's 'a house or any other building ... is never covered while any other choice exists' - measured first (does any pool caption take a building-covering seat where a seat crossing only ways stands?), the scoring made to rule a building out while any other seat exists if it does, and the 500 recorded on 0242's drawing page as a calibration
      research: rendering
      verify: DONE. landed: step 3a's last gaps triaged under XIV: the path walk's curves fixed in both copies, the rest measured and restated
- [x] T196 A defect is a wrong outcome, not a difference (the GM 2026-11-19, request.md: "don't spent a lot of time 'fixing' things which are not actually wrong like things which are different than you expected but still work perfectly well and are in line with our research and produce maps which look fine"): the constitution's fix-as-we-go principle defines a defect - a map that reads wrong, a research finding contradicted, a check that passes the bad or refuses the good, a tool that crashes, hangs or answers wrongly - and says a difference from expectation, from the Python, from a convention's own wording or a gap no reader sees is not one; a claim the code does not literally match where the behavior is fine is fixed by restating the claim; impl-drift's verdicts name which fix (the claim or the code) and the visible effect; spec-fidelity rules leaving a difference within, not a narrowing; a found-and-left item is filed only with its visible effect or the finding it breaks; the plan template's Approach asks what a reader of the map would see differently; root CLAUDE.md, docs/gm-rulings.md and the review agents carry it
      research: rendering
      verify: DONE. landed: a defect is a wrong outcome, not a difference: the constitution, the review agents, the claims recorder and the templates
- [x] T198 The step-3a caption placer measured against a work budget derived from first principles, before step 3b (the GM 2026-11-19, request.md: "if the 3a step is horribly inefficient then we might need to rip it out and restart  tomake it not terrible"): the Rust placer (rust/mode_a/src/labels/) counted - seats tried, obstacle queries, leader tests, per caption and per sheet - on the six pool sheets, its wall time beside the kept Python's; a budget derived on paper as feature 443/444 derive one (.specify/templates/derivation.md, judged SOUND by the work-budget agent); within the budget it stays, far over it (the derivation says how far) it is rebuilt from that derivation as phase tasks with the phase-source guard on, the GM told either way
      research: rendering
      verify: DONE. landed: the step-3a placer counted: 704x its SOUND derived budget; rebuilt from the derivation as phase tasks
- [x] T199 Feature 449's engine plan carries the GM's 2026-10-30 rule (specs/444-work-budget-program/request.md: "we are not trying to re-implement the same algorithms"), which the 2026-11-17 plan dropped: engine-plan.md, spec.md and plan.md say step 3b (the Mode A model: buildings, compound - T152) is rebuilt from a derivation as phase tasks, the phase-source guard refusing a read of the old Python while each runs, and step 4's pipeline stays a port only after a check that none of its modules does far more work than needed; the lockstep tests holding a Rust module to the Python's answers are retired as that Python is deleted, the module's tests then pinning research-backed behavior; the GM's words of 2026-11-19 quoted (request.md)
      research: rendering
      verify: DONE. landed: the GM's rebuild-not-port rule written into engine-plan.md and spec.md
- [x] T200 make work-budget-bundle MODE=budget refuses a derivation for naming today's code on plain English words: T198's placer derivation was refused for 'research' and 'write' (the code-name list holds common words, so a derivation written in ordinary prose cannot pass) - a check refusing good work, a defect under constitution XIV; the name match restricted to identifiers a derivation could only have learned from the code (snake_case or CamelCase names, function and module names), with a test red on the old check (2026-11-19)
      research: rendering
      verify: DONE. landed: the work-budget bundle refuses code-shaped names, not plain words
- [x] T201 The derivation template and make work-budget-bundle take a Mode A stage, for the step-3a placer's rebuild (T198: 704x its SOUND budget): the template's checks are the hamlet stages' - Totals at 20/40/80 households, every figure in ft, the scopes 'per item / over the run / once', each Indexes bullet a grid in ft - so T198-placer.md (Totals per pool sheet, px on a 3 px = 1 ft sheet, per-query scopes) is refused for its form, not its substance; the template gains a Mode A form (sizes the six pool sheets, px with the sheet's scale, per-query scopes) and budget-set takes per-sheet figures, with tests that the T198 derivation bundles and a hamlet derivation still refused for the same gaps (2026-11-19)
      research: rendering
      verify: DONE. landed: the derivation template takes a Mode A stage; the placer budgeted per pool sheet
- [x] T202 phase: placer - the hand sheets' caption placer rebuilt in Rust from its SOUND derivation (specs/449-rust-codebase/derivations/T198-placer.md, budgeted per pool sheet by T201), never from today's code (the GM, 2026-10-30 and 2026-11-19, engine-plan.md 'Rebuilt from a derivation, not ported'; T198: today's placer 704x its budget): a new placer module under rust/mode_a/src/ written from the derivation and 0242/0330's drawing pages, wired into l7r-mode-a hand-sheet for the four hand sheets, its counters behind mode_a's counters feature reading within twice each sheet's budget (make budget-sheets), each hand sheet passing its checks (make pack-audit, the census) and holding 0242's and 0330's rules (a caption on its feature where it fits, else beside it, never covering a building while any other choice exists, a leader past twice the gap, wraps and angles as the pages state); the old Rust placer and its lockstep tests against the Python deleted in the same landing; the Python labels package kept only for compound.py's two generated sheets until step 3b rebuilds them
      research: rendering
      phase: placer
      derivation: specs/449-rust-codebase/derivations/T198-placer.md
      old-code: l7r/diagram/labels/*.py rust/mode_a/src/labels/placer.rs rust/mode_a/src/labels/placer/*.rs rust/mode_a/src/labels/obstacles.rs rust/mode_a/src/labels/obstacles/*.rs rust/mode_a/src/labels/geom.rs rust/mode_a/src/labels/geom/*.rs rust/mode_a/src/labels/layout.rs rust/mode_a/src/labels/standard.rs rust/mode_a/src/labels/hand_sheet.rs rust/mode_a/src/labels/hand_sheet/seat.rs rust/mode_a/src/labels/hand_sheet/tests.rs rust/mode_a/src/labels/hand_sheet/*_tests.rs rust/mode_a/src/labels/hand_sheet/held.json rust/mode_a/src/labels/hand_sheet/held_cases.py
      verify: DONE. landed: the caption placer rebuilt from its derivation: 1.1x-1.9x its budget, the old placer and its lockstep deleted
- [x] T204 phase_source_hooks lets a search print the old code: during T202 a grep over rust/mode_a/src printed lines of the guarded labels/hand_sheet.rs and labels/placer.rs (the guard refuses a read aimed at a guarded file or its directory, not a recursive search of a parent that matches inside one) - a check passing the bad (constitution XIV); a Grep, or a shell grep/rg/ag/find -exec, whose path holds a guarded file is refused unless it excludes the guarded files, the refusal naming the exclusion that makes it compliant; tests red on the old guard (2026-11-19) Also (T202's deletion step): the guard refuses the `make phase-read FILE=<guarded>` it prescribes when the command also holds a read verb (a pipe into tail), and a `git diff --stat` over the guarded directory; and its refusal names a derivation that does not exist (`specs/449-rust-codebase/phases/placer_greenfield.derivation.md`, where T202's is `derivations/T198-placer.md`) - the message reads the task block for its derivation, or names none.
      research: rendering
      verify: DONE. landed: the phase-source guard refuses every route to the old code
- [x] T205 make hooks-test's slowest suites trimmed (the GM 2026-11-12, request.md: "you should prioritize the performance bits of the tests and landing"): 52 suites ~12 min serial, entry-gate.sh 104 s, l7r-gate.sh 83 s, sync-with-main.sh 75 s, pair-hooks.sh 31 s (observed 2026-11-19, method: hooks-test's own per-suite timing line); each slow suite profiled for its repeated setup (git inits, guard rebuilds, full gate runs per case) and cut where a case can share a fixture, every case kept, the saving measured before and after
      research: rendering
      verify: DONE. landed: the hook suites build their binaries once: about 20% faster
- [x] T206 A claims re-check owes only the claims a change can bear on, measured first (the GM 2026-11-12: "if you identify concrete targets with significant measured expected savings then go ahead"): T202's three impl-drift rounds re-judged 259, 55 and 21 claims, most IN-STEP and unchanged in their cited code and blocks; first measure, over feature 449's claims rounds, how many re-owed claims had neither their unit's code nor their cited blocks changed since their last IN-STEP; if that share is large, narrow claims-owed to claims whose unit or cited block changed (every claim citing a changed file or block still owed), with tests that a claim citing a changed block is still owed (2026-11-19)
      research: rendering
      verify: DONE. landed: claims re-checks measured: 7% waste, none from claims-owed; no change
- [x] T207 The idle time in make where-time (the GM 2026-11-19: "And that's sooooo much idle time!  Is that time where nothing was happening?!"): it was not real. A test's empty payload wrote session-less blank lines into the event log (367 of them, 11-08 to 11-19), which where-time read as a second session, and the gaps between them were 379 "idle" minutes (and inflated the model column); fixed: the event-log writer refuses a payload naming no hook event, the reader skips such lines, and SINCE keeps the task active when the window opens. The 11-17 gap was the GM away after the session's final report, not a stall (the untyped agent-finished event at 18:51 was Claude Code's away summary), and 11-16's was the weekly usage limit; no watchdog change.
      research: rendering
      verify: DONE. landed: where-time's idle minutes were blank event-log lines; fixed at the writer and the reader
- [x] T208 The Mode A compound generator's derivation, blind to its code (the GM 2026-10-30 and 2026-11-19, engine-plan.md 'Rebuilt from a derivation, not ported'): an efficient generator of the two generated compound sheets (pool/magistracies/county-magistracy-example, ochiba-roundtrip-test) written from docs/buildings.md's composition rules, docs/building-programs.md and the research pages they cite (0090, 0091, 0115, 0116 and the parts' pages), never from compound*.py, compound_parts.py, compound_model.py, well_gear.py or labels/*.py; its contract (what a program declares, what the sheet must hold - the court spine, perimeter-first placement, ranks, the parts by their rules, captions by the T202 placer), its operation count per sheet in the pool-sheet form (T201), judged SOUND by the work-budget agent, the budget set by make budget-set; before T152
      research: rendering
      verify: DONE. landed: the compound generator's blind derivation, SOUND; budget set
- [x] T209 The caption placer's nearness test measures to the outer edge of a feature's outline stroke while it seats a caption at the usual gap from the feature's fill box, so every place directly above, below or beside a stroked building is refused by about 1 px and the caption falls to a diagonal seat (found by T152 on county-magistracy-example's storehouses, 2026-11-19) - contrary to 0242's ranked places, a research finding the code breaks (constitution XIV); fixed in rust/mode_a/src/caption_place with a test red first; the fix moves 38 captions on the four hand sheets (12 Hayakawa, 9 Ochiba, 14 Ubame, 3 Hoshigaoka - T152's measurement), each sheet looked at after and its checks green; before T156
      research: rendering
      verify: DONE. landed: captions seated off the drawn edge; leaders kept off other buildings
- [x] T210 T156a - dead measurement tooling (T156's first landing, no engine code): scripts/measure/collect_cost.py, collect_probe.py and make collect-cost deleted; tests/test_operations_registry.py deleted unported (ask:449-phase4-slices Q9); specs/335-*/harness.py and make spec-harness retired (its caption_moves is dead since T152; a port would have to be rebuilt per engine-plan.md, retiring is the easier route the record leaves open), make figures listing its 7 measurements as not re-measured
      research: rendering
      verify: DONE. landed: dead measurement tooling retired; T156 split
- [x] T211 T156b - the Rust pool sweep (T156's second landing): every pool sheet through its tier's checks, the red fixtures on the Rust verdicts, the size table's coverage, the on-map declaration and maps_recording, the declared tiers, the round-trip's corridor - written fresh as Rust tests (hand sheets read from their svg, generated sheets composed in process from their spec); census/pool_check's calls moved out of the lockstep test; tests/test_mode_a_sheets.py and tests/_sheets.py deleted (its staleness check missed Rust generator edits - a defect retired with it); suite_tools/deps/tests.rs re-pointed
      research: rendering
      verify: DONE. landed: the pool sweep is Rust; the Python sweep deleted
- [x] T212 T156c - the Python audit and its lockstep retired (T156's third landing; no open task owned it - T153-T155 kept the Python for its Python importers): l7r/diagram/tools/pack_audit/*.py (4,790 lines), interactive/sheet.py's reader half and buildings/types.py deleted once nothing imports them, rust/mode_a/src/parse/lockstep*.rs (2,009 lines) and the types lockstep deleted (engine-plan.md: lockstep tests retire with their Python), the claims re-keyed by claims carry or the rebuilt outcome (Q10), mode_a's Cargo.toml test reads trimmed; and the three red fixtures no registry row names (tests/fixtures/hayakawa-layout-red.svg, hoshigaoka-walled-red.svg, ubame-tub-straddle-red.svg - found by T211, 2026-11-19) wired to the check each was drawn for, or deleted if none
      research: rendering
      verify: DONE. landed: the Python audit and its lockstep retired; no claim stranded
- [x] T213 T156d - pytest's exit (T156's fourth landing): tests/conftest.py, tests/__init__.py, tests/tooling/__init__.py, tests/_scope.py, _gate_failures.py, _heap.py and l7r/diagram/_memory.py deleted; pytest removed from make quick, test, test-full, test-file, durations, soak and done; pyproject's pytest block and stale entries removed; the Rust that names pytest files (tree hashing and state, land long_runs, suite_tools deps, make_only_hooks' pytest branch, measure gate_costs) and tests/CLAUDE.md, l7r/diagram/CLAUDE.md updated
      research: rendering
      verify: DONE. landed: pytest's exit
- [x] T214 Done by T213 (2026-11-19): the make-only guard's pytest branch, the one that refused a mention, was deleted with pytest; rust/guard/src/guards/make_only_hooks/tests.rs::a_pytest_command_or_mention_is_left_alone pins that a mention passes. make_only_hooks refuses a mention of pytest as an invocation: T156's scoping (2026-11-19) was refused a read-only python3 -I -c whose string literal held the word pytest - a check refusing good work (constitution XIV); the guard matches an invocation, not a word in a quoted string, with a test red on the old guard
      research: rendering
      verify: DONE. landed in batch T156+T214: T156 done through T210-T213; T214 done by T213
- [x] T218 T157a - the pipeline's tooling fixes (T157's first landing, no engine code): make scatter-bases (runs a deleted script) removed and fix-check.md and glyph-check.md re-pointed; cache-audit dropped from .PHONY and dev/cache.md; sync-with-main.sh's unused RENDER_CACHE_MOD and the dead roll store's seed_roll_cache retired (.gencache/rolls, 6.0 GB, never written since 2026-11-07); T215 (make map's default GEN) and T217 (perf-gate and cov-file named but gone) folded in; and the open question whether an edit to a tracked hand-sheet svg lands DIRECT with no pool sweep (tree/delta.rs counts only .gen.py and .json under pool/ as engine) measured and fixed if so (found by T157's scoping, 2026-11-19)
      research: rendering
      verify: DONE. landed: the pipeline's tooling fixes; a hand-sheet svg edit is engine
- [x] T219 T157b derivation - the pipeline's map walk and generation key, derived blind to l7r/diagram/pipeline/ (engine-plan.md: a scan growing faster than its input is rebuilt, never ported; T157's scoping found gencache's key re-reading and hashing every engine file - 51 .py and 1,186 Rust sources - for every map, and the walk keying a map on its .gen.py so pool/index.html lists 6 of the pool's 30 maps): one walk over each folder's contents (a .spec.json hamlet, a .compound.json sheet, a tracked hand-sheet svg in a declared tier, a legacy .json exhibit, anything else reported), one key per map (the binary's id once per run, the spec's bytes, the reads the engine reports), judged SOUND by the work-budget agent, the budget set (2026-11-19)
      research: rendering
      verify: DONE. landed: the pipeline derivation and budget
- [x] T220 T157c - phase: the pool walk and the index (T157's second landing): the walk rebuilt from T157b's derivation in a crate the gate and mode_a both use, its consumers moved onto it in the same landing (reviews prereq, snapshot and owed, measure probe, trials model_trial, review-gate.sh, mode_a pool_sweep), pool/index.html written by Rust from it listing every map of both trees (the hamlets and the frozen exhibits included); pool_index.py and its css and json deleted with render_cache.py, which imports it, in T222 (T220, 2026-11-19: deleting them first breaks render-sync on main); and the pipeline stage's counters added to the work-budget review's counted set (T224 left `pipeline` printed UNCOUNTED until its code exists), dev/work-budget.json's row saying so until then
      research: rendering
      phase: pipeline
      derivation: specs/449-rust-codebase/derivations/T219-pipeline.md
      old-code: l7r/diagram/pipeline/*.py l7r/diagram/pipeline/pool_index.css l7r/diagram/pipeline/pool_index_text.json
      verify: DONE. landed: the pool walk and the index, rebuilt from T219's derivation
- [x] T221 T157d - phase: one sheet driver and the generation cache (T157's third landing): make map MAP=<folder|spec> runs any pool map (hamlets too) through one Rust driver with the key from T157b's derivation and the cache's publish semantics (atomic, meta last); the six .gen.py, sheet.py, regen.py, gencache.py, rollcache.py and _census.py deleted (raster's census hook and the Python class name in the Rust errors with them), bundle_door's is_current replaced by the Rust cache asked in process, tree/delta.rs and make_only_hooks' .gen.py patterns updated; and the engine's reported reads include the files it looked for and did not find (T219's derivation, 2026-11-19: the Mode A page writer records only files that exist, so a looked-for file created later - a modal text - leaves its sheet cached and stale), a test red first; and a read first reported on a miss is hashed before the engine runs, or held by the racy-file rule against the engine's start, so a file changed while the engine read it is never recorded with a digest of content the entry was not built from (T219's second judgment, 2026-11-19)
      research: rendering
      phase: pipeline
      derivation: specs/449-rust-codebase/derivations/T219-pipeline.md
      old-code: l7r/diagram/pipeline/*.py l7r/diagram/pipeline/pool_index.css l7r/diagram/pipeline/pool_index_text.json
      verify: DONE. landed: one Rust driver and the generation cache, rebuilt from T219's derivation
- [x] T223 Make targets that pass by running nothing, and a notes edit that skips the sweep (found by T218, 2026-11-19): names in the Makefile's .PHONY with no rule answer 'Nothing to be done' and exit 0 - perf-review (run by sync-with-main.sh on every push, so the push's perf review checks nothing), cohort-landing (called by make land when the port switch is not rust-only), perf, perf-report, maps, explain, why-placed and the perf-explain/confirm/audit/signoff/review/profile family that .claude/agents/perf-audit.md names - each a check passing the bad (constitution XIV): wired to the tool that does the job now, or removed with its callers and the agent file updated; gate_write_hooks' dead guard on a running make cache-audit removed; and a hand sheet's .notes.md, which the pool sweep reads (its census), counted as engine for the land route so a notes-only edit runs the sweep; tests red first
      research: rendering
      verify: DONE. landed: no make target passes by running nothing; pool notes are engine
- [x] T224 The push's work-budget review checks nothing (found by T223, 2026-11-19): make work-budget-review prints 'suspended ... T42' and exits 0 while six stages are accepted (water_frame, field, sink, hem, waterward, waterward.polder) and the placer and compound budgets are set - the push and make land both call it, so no accepted stage is held to its budget at the push (a check passing the bad, constitution XIV); it holds each accepted stage, the hamlets' and the Mode A stages' (pool-sheet budgets, T201), to its figure with the leeway feature 443/444 set, red first on a stage over budget; and the green-gate stamp's diagram area (tree/src/stamp.rs) covers pool .json, .svg and .notes.md, so make land runs make done for a pool-only change instead of the push refusing it; lands before T220 (T223's plan review, 2026-11-19)
      research: rendering
      verify: DONE. landed: the work-budget review holds each accepted stage; the stamp covers the pool
- [x] T225 Stale command names left in guards, gate messages and docs (found by T223, 2026-11-19): pair_hooks' make maps, measure_hooks' make perf reminder and make test-full, the work-budget bundle's make perf-fanout refusal, the cohort note's make rust-gate, stale rows in l7r/diagram/tools/CLAUDE.md and docs/efficiency-tooling.md, and the constitution's and .specify templates' pytest and perf names (an amendment) - each a tip naming a command that does not run; re-pointed at the command that does the job, or removed, the suites updated; and the guard-file refusals for dev/work-budget.json name make budget-change (its one writer) where they name make guard-edit, which refuses that file (found by T227, 2026-11-19); lands before T221 (T227's plan review, 2026-11-19: a refusal must name the command that does the job)
      research: rendering
      verify: DONE. landed: every instruction to run a make target names one that runs
- [x] T227 A guard file edited by a shell heredoc without the guard firing (found by T220, 2026-11-19): scripts/gates/review-gate.sh and tests/hooks/test-review-gate.sh were rewritten through a Bash heredoc and the guard-file edit guard did not refuse it (both carried GUARD_EDIT_OK markers, so nothing wrong landed, but an edit with no permit would have gone through the same way) - the guard's matching of shell writes to guarded files measured and widened to the heredoc and redirect forms, red first; lands before T221 begins (T220's plan review, 2026-11-19)
      research: rendering
      verify: DONE. landed: every shell write of a held guard file is refused
