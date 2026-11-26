# Why the guard crate's tests take three times as long under the default temp directory (feature 451 T365, measured 2026-11-26)

Measured in the pool tree `diagram-backlog-t270`, 22 cores, 2026-11-26 17:54 to 18:25 EST (22:54 to 23:25Z), load 3 to 23 (other
builders ran throughout). No source file changed. Every script and raw output named here is in this directory.

## The answer in five lines

- THE CAUSE is `l7r_shared::tempdir::TempDir::new` (`rust/guard/shared/src/tempdir.rs`): every call runs `sweep_dead`, which lists
  the WHOLE temp directory to find dead processes' `l7r-{tag}-p{pid}-{seq}` directories. No schedule, no once-a-process: one full
  listing a call. The guard crate's test binary makes 509 such calls a run.
- ONE LISTING OF `/tmp` COSTS 14 TO 16 ms alone (5,443 entries in a directory file of 21.9 MB) against 0.06 ms in an empty
  directory, and about 160 ms each when 22 test threads list it at once. 509 listings: 9.97 s of the single-threaded run's 9.81 s
  difference, 82 thread-seconds of the parallel run's 3.3 s wall difference.
- THE LIVE HOOKS DO NOT PAY: a PreToolUse or PostToolUse call of the guard binary lists `/tmp` zero times and takes the same time
  under either temp directory (31.6 against 30.5 ms median).
- WHAT DOES PAY, on the standard paths: the test runner's leak pin (one listing a crate run), the hook suites' runner (a shell glob
  of `/tmp` a suite, 16.5 ms), and a few gate self-tests. An ESTIMATE of 1.9 minutes of process time a day, not of anyone's waiting.
- The three-times figure is paid only by a test binary run with `TMPDIR` unset; `make rust-test` gives each crate a new empty
  `TMPDIR` already. Such runs did happen today and are not in the estimate: 29 leftovers show the land crate's test binary running
  under `/tmp` and dying mid-run between 12:46 and 14:07 (section 3); who ran it is not found.

## 1. The cause

### The code

`TempDir::new(tag)` (tempdir.rs lines 34 to 50) calls `sweep_dead(&temp_dir, tag, "/proc", three hours ago)` and then makes its own
directory. `sweep_dead` (lines 168 to 189) is `std::fs::read_dir(parent)` over every entry; for each it builds the name as a
`String` and tests the prefix `l7r-{tag}-p`; only a name that matches goes on to `file_type`, `metadata` and the `/proc/<pid>` probe.
So its cost is the listing itself, and it is the same whether or not anything matches. It runs on EVERY call: not once a process, not
on a schedule, no stamp.

Nothing else scans the temp directory in the test binary:

- `beside_binary` and the tests' guard log (`log.rs` line 222) join a fixed name and list nothing.
- The scratch-sweep guard (`rust/guard/src/guards/scratch_sweep_hooks/`) reads one stamp's age on a prompt and walks `/tmp` only in
  its detached sweep, once a day; its tests sweep fixture trees, not `/tmp`.
- `pair_hooks/review.rs` line 43 writes one file by name.
- THE FIXTURES' OWN SCANS, the task line's second candidate, are ruled out: no `read_dir` of the temp directory is in `rust/guard`
  but `sweep_dead`'s (`grep -rn "read_dir(" rust/guard`, none on `temp_dir`, `/tmp` or `TMPDIR`), and the shim counts the same 509
  listings under either temp directory, one a `TempDir`.

### The counts (in-process, because `strace` is refused here)

`strace` and `perf` cannot run in this container (`ptrace: Operation not permitted`, with `sudo` too; no tracefs). The counts are
from an `LD_PRELOAD` shim, `t365-shim.c`, which counts `opendir` of the temp directory, the `readdir64` calls on it, the wall time
from each `opendir` to its `closedir`, and `statx` of `/proc/<pid>`, one line a process at exit. Rust's `read_dir` goes through the C
library's `opendir`, so the shim sees it.

The guard test binary (`debug/deps/l7r_guard-060b6c99872292e9`, 549 tests), run from `rust/guard`:

| run | listings of the temp directory | entries read | time inside the listings, summed over threads | `/proc/<pid>` probes |
|---|---|---|---|---|
| `TMPDIR` unset (`/tmp`), 22 threads | 509 | 2,774,691 (5,451 a listing) | 82.2 s (161 ms a listing) | 25 |
| `TMPDIR` unset, `--test-threads=1` | 509 | 2,772,215 | 9.97 s (19.6 ms a listing) | 25 |
| `TMPDIR` a new empty directory, 22 threads | 509 | 10,600 (21 a listing) | 0.10 s (0.2 ms a listing) | 25 |

(`t365-shim-testbin-*.txt`. The 25 probes are the same in both: tests of other code, not the sweep, which found no name to probe.)

### The wall times

Five runs each, alternating, `/usr/bin/time` (`t365-bin-times.txt`; the empty directory is `/tmp/t365-tmp/e`, the same filesystem):

| | wall s (five runs) | median | user s | sys s |
|---|---|---|---|---|
| `TMPDIR` unset | 5.34, 5.30, 5.76, 5.30, 5.70 | 5.34 | 8.7 to 9.2 | 14.8 to 15.9 |
| new empty `TMPDIR` | 2.08, 2.08, 2.11, 2.14, 1.95 | 2.08 | 9.3 to 9.5 | 8.3 to 8.6 |
| `TMPDIR` unset, one thread | 24.85 | | 8.05 | 14.83 |
| new empty `TMPDIR`, one thread | 15.04 | | 7.57 | 5.87 |

THE ARITHMETIC CLOSES. One thread: 24.85 - 15.04 = 9.81 s of difference, and the shim's 509 listings took 9.97 s. Parallel: the
difference is 3.26 s of wall and about 7 s of system time; the listings summed to 82 thread-seconds, about 3.7 s on each of 22
threads. No one test accounts for it because every test that makes a `TempDir` pays one listing.

Under 22 threads a listing costs eight times what it costs alone (161 against 19.6 ms in this debug build). The listings contend:
each test also makes and removes a directory in the same parent between listings. Which lock it is (the directory's inode lock, or
the overlay filesystem's cache of a merged directory, dropped at every change) is NOT measured; no tracing tool runs here.

### The cost as a function

One `TempDir::new`, timed alone in a loop of 300, release build, the real helper with a tag that matches nothing
(`t365-loop-main.rs`, a scratch crate outside the tree with a path dependency on `rust/guard/shared`; `t365-loop-new.txt`,
`t365-loop-bloat.txt`):

| the temp directory | entries | size of the directory file | median ms a call |
|---|---|---|---|
| new, empty | 0 | 4 KB | 0.06 |
| new, 1,000 files | 1,000 | 61 KB | 0.43 |
| new, 5,400 files | 5,400 | 295 KB | 2.19 |
| new, 20,000 files | 20,000 | 1.1 MB | 8.16 |
| new, 80,000 files | 80,000 | 4.6 MB | 32.3 |
| 330,000 files made, all removed | 0 | 20.4 MB | 2.4 to 2.7 |
| 330,000 files made, all but 5,400 removed | 5,400 | 20.4 MB | 6.8 to 8.7 |
| `/tmp` | 5,443 | 21.9 MB | 13.4 to 16.0 |

- In a directory that never grew: **0.06 ms + 0.41 ms for each 1,000 entries**, linear from 1,000 to 80,000.
- `/tmp` is not that directory. It once held about 329,000 entries (tempdir.rs's header), and a directory file never shrinks: it
  is 21.9 MB for 5,443 entries. A listing reads all of it. The synthetic copy of that history costs 2.5 ms with nothing in it and
  7 to 9 ms with 5,400 entries left scattered through it; the real `/tmp` costs 13.4 to 16.0 ms, about **2.7 ms for each 1,000
  entries**, six and a half times the clean rate. The gap between the synthetic copy and the real one (7 to 9 against 13 to 16 ms)
  is not explained: `/tmp` is the root of the container's overlay mount, the copy a directory inside it.
- A bare `read_dir(/tmp)` with no `TempDir` is 14.2 to 14.7 ms: the listing is the whole cost of the call.
- WHAT FOLLOWS FOR A CLEAN-UP: removing every entry from `/tmp` would leave a listing at about 2.5 ms, not 0.06 ms, by the
  synthetic copy. Only a directory that never grew is cheap.

## 2. Who else pays

### The live hooks: nothing

One real call as the settings make it, `/diagram/scripts/hooks/l7r-hook <event>` with `CLAUDE_PROJECT_DIR=/diagram`, the mirror's
kept binary, a JSON event on stdin naming this tree as its `cwd` and the session `t365-measure-0000`:

- Under the shim: PreToolUse Bash (`true`), PostToolUse Bash, PreToolUse Edit (one line of `docs/usage.md`) and UserPromptSubmit each
  list the temp directory **0 times**.
- Timed, 20 runs each, alternating, after a warm-up (`t365-time.py`, `t365-hook-times.txt`), load 2.8 to 2.9:

| the call | `/tmp`: median, 90th centile ms | empty `TMPDIR`: median, 90th centile ms |
|---|---|---|
| PreToolUse, Bash `true` | 31.6, 41.3 | 30.5, 38.1 |
| PostToolUse, Bash `true` | 20.8, 24.5 | 20.5, 22.2 |
| PreToolUse, Edit of `docs/usage.md` | 342.2, 362.0 | 346.4, 365.6 |

The differences (1.1, 0.3 and -4.2 ms) are inside the spread. Two guards do call `TempDir::new` in production code, each at most once
an event and only on their own matcher: `ledger_hooks.rs` line 213 (a Bash command appending a ledger row) and `gate_write_hooks.rs`
line 267 (an edit of a file the gate reads); neither fired on these events. Their bound is in the estimate below.

FOUND BESIDE IT: a PreToolUse hook on an Edit takes 342 ms where one on a Bash call takes 32 ms. The temp directory is not the
reason (same under both). Filed as T373. It is ONE made-up event - one file, a session id that resolves to no session - so the day's
figure is a PROJECTION, not a measurement: if every one of the day's 470 Edit and Write calls cost that, 2.7 minutes, more than
everything the temp directory costs.

### The gate tool

- `scripts/gates/l7r-gate.sh builder-tree list` (what `make builder-trees` runs): 0 listings; 946 ms median (90th centile 1,008)
  under `/tmp`, 949 (1,023) under an empty `TMPDIR`, load 14 to 23 (`t365-gate-times.txt`). `make switches`, `speckit-todo`,
  `claims-owed`, `ledger-owed`, `sampler`, `tunables` and `research-backlog`: 0 listings each (`t365-make-listings.txt`).
- A gate call that does pay: `l7r-gate.sh check file-scale --selftest` (the first step of `make static`) makes two `TempDir`s: 2
  listings, **76.4 ms median (81.9) under `/tmp` against 36.6 (38.2)** under an empty `TMPDIR`, 20 ms a listing at load 13 to 14.
- `make static`'s other steps before its coverage step (`file-scale .`, `question-size --all`, `claims coverage --rust`, `rust lint`,
  `rust format --check`): 0 listings. The gate's production callers of the helper are `checks::scratch` (the checks' self-tests,
  `claims accept`, `claims carry`), `rustc.rs`'s `leak_checked` and `times.rs`.
- THE LEAK PIN (`rust/gate/crates/rustc/src/rustc.rs` line 212, also the coverage and side runs): one `TempDir::new` under `/tmp` a
  crate's test run, to make the run's own `TMPDIR`. One listing a run; the tests inside then list only their own small directory.
  MEASURED through `make rust-test CRATE=rust/gate/crates/task` under the shim: `l7r-rust` listed `/tmp` once, 21.6 ms, and the
  crate's test binary not at all (`t365-shim-rust-test.txt`). The coverage runs' one listing is read from the code (`cover.rs` line
  370), not measured.

### The hook suites

`tests/hooks/hookrun.sh` gives each suite its own `TMPDIR` (a `mktemp -d` under `/tmp`), so the guard calls inside a suite list a
small directory. But the runner itself, line 95, globs `/tmp/l7r-hooks-suite-*-p[0-9]*.*` before every suite to remove a killed
runner's leftovers, and a shell glob reads the whole directory: 200 globs in one bash took 3.30 s under `/tmp` and 0.00 s under an
empty directory, **16.5 ms a suite** (`t365-glob.txt`). Under the shim that loop is one `opendir` of `/tmp` by bash, 20.8 ms
(`t365-shim-glob.txt`). The runner itself was not run (a job writes its suite's stamp); the loop is its lines 95 to 99 as written.
One job is one `Phase` line of `step: suite` (the Makefile's line 378 writes one for each job's span), so the day's count of those
lines is the count of globs.

### The day's cost: an ESTIMATE

From the clone's event log (`/diagram/.clones/diagram-backlog/.git/l7r-events/*.jsonl`, lines stamped 2026-11-26T00:00Z to
22:56Z, read before these measurements added to it; 28,147 lines, 8 session ids; `t365-events.py`, `t365-events-totals.txt`). This
is ONE clone's log; other clones' work is not in it.

| who | count on the day | each | process time a day |
|---|---|---|---|
| hook calls (15,463 events, 15,759 guard processes; 7,073 PreToolUse, 6,880 PostToolUse) | 15,759 | 0 ms (0 listings) | 0 s |
| hook suites run (`Phase` lines of `src: hooks`, `step: suite`) | 4,051 | 16.5 ms (one glob) | 67 s |
| crate test and coverage runs (`step: test` 1,154 + `step: cover-run` 1,329), the leak pin | 2,483 | 16 ms (one listing) | 40 s |
| `make static` runs' `file-scale --selftest` (closing-checks 77 + land about 50 + quick 56 Bash calls, an upper count) | at most 183 | 40 ms (two listings) | at most 7 s |
| guards that make a `TempDir` (ledger, gate-write): bounded by the 470 Edit and Write calls | at most 470 | 16 ms | at most 8 s |
| a test binary run by hand with `TMPDIR` unset | not logged | 3.3 s for the guard crate | not counted |

**About 114 s measured (67 + 40 + 7), at most 122 s with the bound: 1.9 to 2.0 minutes of process time a day.** This is an estimate:
the per-call figures are today's, alone or at load 13; the suites and the crate runs go several at once, so a listing can cost more
than 16 ms where they contend (161 ms at 22 at once) and the wall time anyone waits is less than the sum. The 1,421 Bash calls that
named a make target are not multiplied by anything: the targets sampled list nothing.

## 3. What is in /tmp

Snapshot of the top level at 2026-11-26T22:56Z (`find /tmp -maxdepth 1`), sizes by `du -sk` of each entry 30 minutes later (18 s to
walk). Read-only. `t365-census.py`; whole tables in `t365-census-all.txt` (402 prefixes), `t365-census-by-count.txt`,
`t365-census-by-bytes.txt`, `t365-census-l7r.txt`, `t365-du-top20.txt`.

**5,442 entries, 11.7 GB.** By age: 6 under 3 hours, 106 from 3 to 24 hours, 330 from 1 to 3 days, 1,355 from 3 to 7 days, 2,208
from 7 to 30 days, 1,437 over 30 days. So 5,000 of 5,442 are older than three days, and 112 are of the last day.

By size, the largest (the 20 largest single entries are in `t365-du-top20.txt`):

| entry or prefix | count | MB | oldest to newest | writer | its own clean-up |
|---|---|---|---|---|---|
| `claude-1000/` | 1 | 6,787 | | Claude Code: each session's scratch and task outputs | the scratch sweep: a session idle 3 days, a task output idle 24 h |
| `l7r-check/` | 1 (1,905 inside; 804 older than 3 days, 17 of the last 3 hours) | 1,027 | | the gate's bundles and verdicts (`rust/gate/src/lib.rs`, `plan.rs`, `record/bundle.rs`, `record/sources.rs`), a fixed path | none |
| `l7r-pass/` | 1 | 566 | 11-26 | the `research-pass` agent's scratch (named in `.claude/agents/research-pass.md`) | none |
| `probe309/`, `rh/`, `c1/`, `s453/`, `431s1/`, `s403/` and the rest of the sessions' and builders' hand scratch (`s*`, `c*`, `b*`, `p*`, `fb*`, `lf*`: every name no row here lists) | 2,525 | 2,984 | 10-10 to 11-26 | sessions and builders, by hand | none: the sweep's `/tmp` rule takes only `t<N>...` and `tmp.*` |
| `l7r-dl/` | 1 | 200 | 11-24 | the same agent file names it | none |
| `guardlog-fixtures*` | 828 | 78 | 10-07 to 11-08 | INFERRED from the name and dates (the shell hook suites before the leak pin); no file of `tests/`, `rust/` or `scripts/` names it now | none; no writer left |

By count:

| prefix | count | oldest to newest | live or dead | writer | its own clean-up |
|---|---|---|---|---|---|
| `l7r-*` in all | 1,217 | 1,138 of them 11-11 16:09 to 16:11 | | | |
| `l7r-*` not of the helper's form: mostly `l7r-<tag>-<pid>-<seq>[-<name>]`, the form before 449 T101 (`gate-check-*`, `guard-checks-*`, `gate-reviews-*`) | 1,187 | 1,138 of them 11-11 | every pid checked dead (394 names carry one) | the checks' tests of one afternoon, before `TempDir` | none, by decision: `sweep_dead` takes only the `-p<pid>-` form ("the GM's laptop session's to delete") |
| `l7r-gate-ci-stop-handler-p<pid>-<seq>` | 29 | 11-26 12:46 to 14:07 | every pid dead | `gate-ci-{tag}` (`rust/gate/crates/core/src/ci/fixtures.rs` line 41), a stop-handler test | `sweep_dead`, at the next `TempDir` of that tag after 3 hours: none since |
| `l7r-guard-sweep-sweep-p2301309-0` | 1 | 11-25 16:55 | dead | a scratch-sweep test (`scratch_sweep_hooks/tests.rs` line 179) | the same |
| `guardlog-fixtures*` | 828 | 10-07 to 11-08 | | as above | none |
| `plan-verdict-*.json` | 194 | 10-13 to 11-26 | | INFERRED from the name: sessions writing a verdict file for `make plan-verdict` | none |
| `tmp*` that is not `tmp.` (Python's `tempfile`) | 159 | 10-10 to 11-21 | | the Python tools, deleted since | none (the sweep's rule is `tmp.`) |
| `rollchild*` 116, `pymp-*` 53 | 169 | 10-10 to 11-04 | | INFERRED: the Python engine, deleted (`pymp-` is Python's multiprocessing; nothing in the tree names `rollchild`) | none |
| `l7r-rust-tests-*` (the test runner's `TMPDIR`s), `l7r-hooks-suite-*` (the suites') | 0 | | | `leak_checked`, `hookrun.sh` | each removed by its runner; a killed runner's by the next run |
| `tmp.*` (`mktemp -d`) | 52 | 11-26 12:58 to 13:25 | | shell | the sweep, idle 24 h |
| `t<N>...` | 2 | 11-20 | | builders | the sweep, idle 24 h, and `make land` |

- OF THE PID-NAMED ENTRIES: 30 of the helper's form, all of dead processes and none of a live one at the snapshot; 394 of the old
  form whose pid the name gives, all dead.
- THE 29 STOP-HANDLER LEFTOVERS say more than a leak: their sequence numbers run 71 to 99, so each was about the 70th to 100th
  `TempDir` of a process whose temp directory was `/tmp` - the land crate's whole test binary (125 tests;
  `rust/gate/crates/land/src/land/stop/tests.rs` line 117 is the one `scratch("stop-handler")`), outside the leak pin, ended before
  that test dropped its directory; three of them (pids 656574, 656578, 656579) within nine seconds of each other. The test run alone
  under a private `TMPDIR` leaves nothing (two runs). Their times fall partly inside `land` and coverage phases of the clone and its
  trees and partly inside none the event log holds; WHO ran the binary under `/tmp` is not found (T376).
- THE WRITERS THAT STILL LEAK are few: the stop-handler test (29 in 81 minutes today, each 8 bytes in a directory), hand scratch by
  sessions and builders under names the sweep's rule does not know, `plan-verdict-*.json`, and the fixed-name `l7r-check/`.
  Everything else is history: 1,138 entries of 2026-11-11, 828 `guardlog-fixtures`, 328 of the deleted Python.
- The leak pins work: `make rust-test` and the hook suites leave nothing new at the top level.

## 4. The levers, priced

Per-day figures are section 2's estimate. "Reuse" answers the GM's disk principle: would it delete anything a later run could have
used.

| lever | saves a call | saves a day | risks | deletes anything reusable |
|---|---|---|---|---|
| A. `sweep_dead` once a process (all tags in the one listing), not once a `TempDir` | 508 of 509 listings in the guard test binary: 5.3 s to about 2.1 s by hand; 20 ms of `file-scale --selftest`'s 40 | about 4 s (the self-test); the by-hand runs, uncounted | a leftover of another tag goes at the next process of ANY tag (the same dead-pid and three-hour test) | no: a dead process's `-p<pid>-` directory is reused by nothing |
| B. the helper's directories under one subdirectory (`<temp>/l7r-tmp/`), so no sweep lists the rest of `/tmp` | 14 to 16 ms to about 0.1 ms a `TempDir::new` | 40 s (the leak pin) + 7 s; makes A unnecessary for time | tests and guards that know a path by its shape (four guard tests fail when `TMPDIR` sits under a session's scratchpad); the leak pin's check of what a run left; the old-form leftovers stay where they are | no |
| C. the hook suites' leftover glob once a `make hooks-test` run, or their directories under one subdirectory | 16.5 ms a suite | 67 s, the largest | a killed runner's leftovers wait for the next full run | no |
| D. the scratch sweep's `/tmp` rule widened from `t<N>...` and `tmp.*` to every top-level entry of this uid idle past a threshold, named caches excepted | at most 11 to 13 ms a listing (16 down to the 2.5 ms floor), and only where B and C are not built | at most 90 s, 0 s beside B and C; frees up to 4.9 GB (everything outside `claude-1000/`) | removing what a session still means to read; a decision about disk, the GM's | yes unless excepted: `l7r-check/` (bundles and verdicts read by later steps, 17 written in the last 3 hours), `l7r-dl/`, `l7r-pass/` |
| E1. the sweep at most once an interval, by a stamp file every process reads | A's 508 listings and each process's first too: 14 to 16 ms to one `stat` | 40 s (the leak pin) + 7 s, as B, with no path moved; nothing for the suites' glob | where the stamp lives; two processes sweeping at once; a dead process's directory living an interval longer | no |
| E2. the sweep detached | the caller's 14 to 16 ms, less a process started a call | nothing beyond E1; the listings still run and still contend | a process a `TempDir`, unless stamped too, which is E1 | no |
| F. a `TMPDIR` for each pool tree | everything above for a builder's own runs | at most B + C together | four guard tests fail under a `TMPDIR` whose path the guards read as scratch; a place the scratch sweep does not know | no |

Filed, each its own task of feature 451: A is T370, B is T371, C is T372, D is T374; and the three things found beside them - the
Edit hook's 342 ms (T373), the four guard tests that fail under a scratchpad `TMPDIR` (T375), the stop-handler test's leftovers
(T376). E1 is T377 (the alternative to B: build one of the two), and E2 (T378) and F (T379) are filed as priced and dominated, to be withdrawn
when the others land. A, with either B or E1, and C together take the whole estimate.

## What these measurements changed outside this directory

- NOTHING was removed from `/tmp` by hand, and the helper's sweep removed nothing: the `-p<pid>-` names in `/tmp` were the same 30
  before and after (the timing loop's tag matches nothing; the guard tests' tags matched no leftover).
- THE DAY'S SCRATCH SWEEP RAN, started by this measurement. The one UserPromptSubmit call made under the shim (23:03:17Z) found
  the sweep's stamp more than a day old and started it, as the next real prompt of any session would have: 92 removals, 0.5 MB - 87
  finished task outputs idle past 24 hours and 5 finished sessions' scratch directories, all under `/tmp/claude-1000/`, none at
  `/tmp`'s top level (`t365-sweep-side-effect.txt`, every path in `t365-sweep-removed-paths.txt`). Its guard-log records went to the
  measurement's own `GUARD_LOG_DIR`, not the real guard log; those two files are their only copy.
- THE EVENT LOG gained 130 lines of session `t365-measure-0000` in `451-time-retro-and-efficiency.jsonl` (the timed hook calls).
- `make static` was started under the shim to count its listings and STOPPED when it reached its coverage step, which the first tier
  does not run: about four minutes of load on the machine, nothing left behind.
- Four tests of the guard crate fail when `TMPDIR` is a directory under a session's scratchpad
  (`/tmp/claude-1000/<slug>/<session>/scratchpad/...`) and pass under `/tmp` and `/tmp/t365-tmp/e`: the first three timings were
  taken that way and discarded. Filed.
