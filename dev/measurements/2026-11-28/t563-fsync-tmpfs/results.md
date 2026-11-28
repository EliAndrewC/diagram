# 462 T563: git's fsyncs off (lever A) against a tmpfs TMPDIR (lever B), at load

Measured 2026-11-28, 12:00-12:40 UTC, in the pool tree `diagram-backlog-t271`, by `t563-driver.sh` (the windows) over
`t563-trial.sh` (one run of four suites). The suites: the built test binaries of `rust/guard/shared`, `rust/guard`,
`rust/gate/crates/lane` and `rust/gate/crates/task` from one `make rust-test` build. Each got `side.rs`'s environment and a
fresh TMPDIR under `/tmp/l7r-tmp`.

- **The arms.** default; A, `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsync GIT_CONFIG_VALUE_0=none`; B, TMPDIR a 256 MiB tmpfs
  mounted in `unshare -Urm`, the tests run as uid 1000 in a nested `unshare --map-user=1000 --map-group=1000 -U`
  (`t563-ns-probe.sh`: the read-only refusal kept, exec and git work); AB, both.
- **The load.** One arm a window: `make under-load` with COPIES=4 LOOPS=2 and no burners, the other sessions' load beside it.
  The order ran default, A, B, AB, AB, B, A, default. Each window had an ambient 45 s slice before it with no trial running.
  The 1-minute load at the windows' starts was 30-60 and peaked about 84; IO pressure (`some avg10`) was 0.4-69 (`windows.tsv`).

| arm | window wall s (two windows) | suites' summed mean s (16 runs each) | shared | guard | lane | task | red runs | forced commits/s in window |
|---|---|---|---|---|---|---|---|---|
| default | 142.6, 101.0 | 56.8 | 18.4 | 15.0 | 13.2 | 10.2 | 2 (task, the lane-drop test) | 0.83, 0.93 |
| A | 98.5, 124.8 | 52.2 | 15.0 | 14.2 | 11.6 | 11.4 | 0 | 1.12, 1.22 |
| B | 63.3, 78.8 | 33.8 | 11.1 | 8.0 | 10.1 | 4.6 | 32 (every shared and guard run) | 0.96, 1.00 |
| AB | 81.4, 84.4 | 39.2 | 12.1 | 10.2 | 11.4 | 5.6 | 32 (the same) | 1.03, 1.01 |

The ambient slices ran 0.96-3.55 forced commits a second, as high as the windows or higher.

## Findings

- **The journal.** The trial did not raise the forced-commit rate: every commit was forced, but the windows ran at 0.83-1.22 a
  second against 0.96-3.55 ambient. At this load the fixture git in these suites is not what drives the journal, and neither
  lever measurably lowered the rate. T562's 40-fixture loop (26-32 forced against 2-3) holds for a loop alone, not for these
  suites among the other sessions' writes.
- **Wall time.** B saved about 40% of the summed suite time and A about 8%. Under B, A added nothing (AB 39.2 s against B's
  33.8 s, within the noise), as expected: a tmpfs fsync is free.
- **B's costs, each priced.**
  - Two tests fail on every B run because they read the filesystem as the disk gives it:
    `session::tests::the_name_sources_read_as_the_python_read_them` (shared) and
    `scratch_sweep_hooks::disk::audit::tests::the_audit_names_every_place_...` (guard).
  - The leak pin (`leak_checked`, `left.rs`, `hookrun.sh`) reads TMPDIR from outside the mount namespace, so it would always
    find the tmpfs's directory empty. Its check would have to run inside the namespace.
  - It needs unprivileged user namespaces, which a host can disable. It needs a fallback where `unshare` fails.
  - The tmpfs peaked at 4.9 MB a suite (guard's), about 20 MB at four copies, inside the 10 GiB cap.
  - Together that is a new mechanism, two builders by the brief rules, not this `fix`.
- **What was built.** A: `tests_tmp` (`rust/gate/crates/rustc/src/rustc/run.rs`), the one place every test runner sets its TMPDIR,
  now also sets git's `core.fsync=none`. Its callers are `cargo_call`, `side.rs`, `cover.rs` and `times.rs`. B is filed.
- **Not trialled.** The hooks suites (`tests/hooks/hookrun.sh` sets their TMPDIR) and the landing's suite as a whole.
- **Found.** The task crate's
  `builder_tree::tests::lane::the_lane_s_tree_goes_by_the_drop_once_no_runner_lives_and_no_batch_is_open` failed 2 of 16 default
  runs at load (`lane.rs:309` and `:326`; `default-task-red.log`). It is a flake under load, filed.
