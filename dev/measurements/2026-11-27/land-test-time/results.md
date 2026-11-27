# Which of the land crate's tests make a green run take 60 to 100 s (451 T455), 2026-11-27

Measured 2026-11-27 07:38Z to 08:05Z in `diagram-backlog-b1` at HEAD 98b632638d, on the machine's own load (load1 4 to 28 over the
window, 22 cores, the container's 10 GB memory cap with its page cache at the cap). No source changed and no load generator ran. The
only load added was this record's own test runs: 30 direct and 40 through make, 5 to 10 s apart, plus one pass of each test alone.

The test binary is `l7r_gate_land-35df8d33ecfe35d2` in `~/.cache/l7r-cargo-target/diagram-backlog-b1/debug/deps/`, built by
`make rust-test CRATE=rust/gate/crates/land FRESH=1`. It has 173 tests.

| script | what it measures | output |
|---|---|---|
| `phases.py` | every land test phase in the clone's event log (250, 2026-11-20 to 11-27T07:39Z), beside the memory sampler's 10 s samples and, for each phase over 30 s, the other land phases within 10 min of it | `phases.txt` |
| `runs.sh` | the binary run directly 30 times, from the crate's directory with default threads, as cargo runs it, with libtest's per-test times (`-Z unstable-options --report-time --format json`; `RUSTC_BOOTSTRAP=1` unlocks the flag on the stable 1.87 toolchain), and wall, user and sys time from `/usr/bin/time` | `runs.log` |
| `pertest.py` | `runs.sh`'s per-test times read back | `pertest.txt` |
| `procs.sh` | each test run alone (`--exact`, one thread): its git calls, counted by a `git` shim on PATH, and the kernel's pid counter before and after | `procs.tsv` |
| `makeruns.sh` | 40 runs through `make rust-test CRATE=rust/gate/crates/land FRESH=1`, the slow runs' own path (the runner's own `TMPDIR`, environment and pipes), with `watch.sh` running alongside | `makeruns.log` |
| `watch.sh` | a passive watcher: any land test binary from any tree alive past 20 s has its threads and descendant processes dumped from `/proc` | caught none |

strace is not available: the container has no ptrace (`PTRACE_TRACEME: Operation not permitted`, with sudo too, observed
2026-11-27). So the per-test process counts below come from a git shim and a pid counter, not from execve tracing.

## 1. The slow runs against their same-time controls (`phases.txt`)

Each land test phase over 30 s is compared with the other land phases that started within 10 min of it, from any tree. Nine phases ran
over 30 s. The six that T455 names are marked *.

| phase start (UTC) | tree | wall s | controls within 10 min (wall s) | excess over the controls' median, s |
|---|---|---|---|---|
| 11-26 01:11:18 * | t254 | 63.3 | 3.7 | 59.6 |
| 11-26 06:08:12 * | m9 | 79.4 | 6.3, 5.8, 14.0 | 73.1 |
| 11-26 07:00:56 * | m9 | 61.0 | 4.3, 4.4, 1.4, 1.5 | 58.2 |
| 11-26 18:15:13 | t270 | 37.1 | 10.3, 7.4, 8.2, 18.3 | 27.9 |
| 11-27 01:44:43 | b1 | 43.0 | 11.6, 5.1, 3.6, 3.4 | 38.7 |
| 11-27 04:40:06 | t271 | 42.7 | 4.5, 5.2, 9.1, 19.7, 4.5 | 37.6 |
| 11-27 04:55:44 * | b1 | 72.5 | 4.5, 7.3, 21.8, 6.4 | 65.6 |
| 11-27 05:32:02 * | t271 | 101.8 | 23.7 (the clone, 30 s later, load1 77 to 85), 10.5, 7.7, 2.3 | 92.7 |
| 11-27 06:16:46 * | t271 | 64.6 | 2.5, 8.4, 5.0, 5.3, 6.1 | 59.3 |

- **Not load alone.** At 05:32 the clone's land run started 30 s after t271's, at a higher load (load1 77 to 85), and took 23.7 s
  where t271's took 101.8 s. The 06:16 run took 64.6 s at load1 22 to 29, with almost no memory stall: 148 us/s of `mem_full`,
  against a median of 956 us/s for the fast phases. The 07:00 run in m9 came three minutes after runs of 1.4 and 1.5 s in the same tree.
- **The machine signals overlap.** Over the 92 phases with samples, the slow ones ran at a higher median load1 (36 against 14.5) and
  more CPU stall (384k against 116k us/s of `cpu_some`). But fast phases ran at the same values: at 07:34Z, seven phases took 1.0 to
  8.8 s at load1 31 to 35 and `cpu_some` up to 482k us/s. No sampled signal separates the slow runs from the rest.
- **The excess clusters near 30, 60 and 90 s:** 27.9, 37.6 and 38.7, then 58.2, 59.3, 59.6, 65.6 and 73.1, then 92.7. The pattern
  fits a fixed wait of about 30 s, hit one to three times, with load noise on top. That is INFERRED from nine phases and not shown.
  The only 30 s waits in the crate are the two `sleep 30` children of `land::stop::tests` (section 4).
- **When it started.** No land phase ran over 21 s in the 82 phases before 2026-11-26T01:11Z, the first slow run, in the tree
  that built T254 and T255. Since then, 9 of about 170 phases ran over 30 s.

## 2. Load scales every test alike (`runs.log`, `pertest.txt`)

Thirty direct runs, 07:42Z to 07:46Z, load1 7.1 to 28.7. All 30 were green.

- Wall time was 1.92 to 12.30 s: 1.9 to 2.6 s at load1 7 to 13, and 3.0 to 12.3 s at load1 13 to 29.
- **Processor seconds are not constant.** user+sys went from 27 s (the quiet runs) to 53 s (run 25, load1 21 to 28). Most of it was
  system time: 17.5 s rising to 34.3 s. The binary's parallelism fell from 14 cores to 4 to 5: CPU seconds per wall second were 14.1 in
  run 1 and 4.3 in run 25. In the slowest runs, the tests summed 163 to 217 s of test time against 53 s of processor time, so most of a
  test's time under load is spent off the processor.
- **No test stands out.** The slowest three runs (23, 25, 30) against the fast half: each test's time grew by a median of 5.1x and at
  most 7.5x, over the 143 tests with a fast median above 5 ms. The order of the slowest tests did not change: the `alone` tests, which
  run the real `scripts/land-alone.sh`, lead in both. No test passed 10 s in any run, and the longest single time was 9.36 s.

| test (the five slowest) | fast-half median s | slowest-three mean s |
|---|---|---|
| `land::alone::tests::takeback::a_file_the_task_edited_and_put_back_is_not_its_own` | 1.728 | 8.114 |
| `land::alone::tests::the_script_refuses_its_own_uncommitted_files_and_moves_nothing_on_a_conflict` | 1.484 | 7.822 |
| `land::alone::tests::takeback::an_append_only_log_appended_on_both_sides_keeps_both` | 1.494 | 7.679 |
| `land::alone::tests::takeback::a_replace_all_edit_put_back_is_not_its_own` | 1.225 | 6.092 |
| `land::alone::tests::the_script_lands_the_clone_s_head_alone_and_the_clone_takes_the_tip` | 1.124 | 5.984 |

Load explains the 5 to 25 s tail of the land phases, and it stretches every test about alike. It does not reach 60 to 100 s at the
loads the slow runs had: at load1 21 to 29, this record's runs took 3.0 to 12.3 s.

## 3. Processes per test (`procs.tsv`)

Each test was run alone, at load1 4 to 11.

- **Totals:** 4,394 git calls through the PATH shim, which misses any git called by absolute path. The pid counter rose by 9,347
  (processes and threads, other sessions' included). The idle baseline was 381 in 10 s, or about 1,100 over the pass's 29 s.
- **Serial time:** 29.3 s of wall, 9.0 s user and 19.8 s system. System time dominates, as it does in section 2.
- **The most git calls:** `land::carry::tests::a_done_commit_is_carried_by_its_ref_after_its_tree_went_to_the_next_task` (137),
  `land::tests::bundle::a_three_task_bundle_starts_closes_decides_and_lands_as_one` (128) and
  `land::carry_done::tests::done_commits_are_carried_oldest_first_and_a_held_one_is_left` (107).
- **The longest alone:** the `alone` tests, 0.6 to 1.15 s each, with 54 to 76 git calls and 208 to 276 pids. They run the shell
  script, its `python3 -I` blocks and a worktree.

No test's alone time exceeds 1.2 s. None waits on a lock or a slot when run alone: every alone time is within 2x of its own processor
seconds.

## 4. Not reproduced, and what is left

- **Not reproduced.** None of the 70 runs came near the slow runs: 30 direct ones at load1 7 to 29 (at most 12.30 s), and 40 through
  make at load1 6 to 13 (2.61 to 9.26 s, median 2.88 s). The make runs were the slow runs' own path. `watch.sh` caught no land test
  binary from any tree alive past 20 s while it ran.
- **A lead, not shown.** `land::stop::tests` starts the crate's only 30 s children. In `a_running_landing_is_sent_term`, the test ends
  with `let _ = child.wait()` on a `sleep 30` that it has sent TERM to. Nothing asserts how the child ended, so a TERM that did not end
  it would add 30 s to a green run. In `term_stops_every_held_group_and_exits_143`, the child copy of the test binary sleeps 30 s
  after its note. That case is bounded by the parent's three 400 x 25 ms polls and would fail red, not run long. Reading the code, no
  way was found for either to wait 30 s green. A fixed 30 s wait, and the excess near 30, 60 and 90 s, is a hypothesis.
- **Searched and ruled out by reading** (the land crate, `scripts/land-alone.sh`, `scripts/gates/closing-checks.sh`, the core
  test fixtures and `l7r_shared::tempdir`; no 30 or 60 s wait was found apart from the `stop` tests' sleeps):
  - The pid limit: `pids.events` shows `max 0`, a peak of 1,659 of 2,048.
  - A CPU quota: `cpu.max` is `max`, and `cpu.stat` shows 0 throttled periods.
  - Memory reclaim failure: `memory.events` shows `max 0` and `oom 0`. The page cache does churn at the cap: 7.5 GB of file pages,
    0.5 GB of them dirty, and 353M working-set refaults by 2026-11-27.
  - The commit retry (`writers.rs`, `COMMIT_TRIES`): it sleeps through the fixture's clock, which does not advance real time.
  - The claims wait: 400 ms through the fixture's clock.
  - `land-alone.sh`'s `flock -n`: non-blocking, and in the fixture's own git directory.
  - The `sleep 20` cohort stubs (`long_runs/tests.rs:123`, `phase/tests.rs:371`): each is in its own process group, which TERM ends,
    with no pipe to drain.
  - `TempDir`'s once-a-process sweep of the temp directory: under make, the runner gives each run its own empty `TMPDIR`.
- **The verdict.** The slow runs cannot be explained by load alone. Every test's time scales about 5x with load, and processor seconds
  roughly double rather than staying flat. That accounts for 5 to 25 s. Each of the six named runs carries a further 58 to 93 s over a
  same-time control, inside the binary: libtest's own `finished in` matches the phase, as T445 found. It was not reproduced in 70 runs,
  and no single test is named. Catching the next one alive is filed as T463.

Filed from this tree: T463, the next slow land run caught alive.
