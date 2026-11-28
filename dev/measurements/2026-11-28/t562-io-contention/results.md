# 462 T562: who writes to disk, what the IO contention costs, and the levers priced - measured 2026-11-28

Load this file when: you are weighing a change to how the builders, the tests or the lane touch the disk (a tmpfs, git's
fsync, CARGO_INCREMENTAL, the build cache's size), or asking why the GM's host freezes under the overnight work.

Nothing outside the repository was changed: no mount, no sysctl, no package. Every lever A/B ran on a `git archive` copy in the
scratchpad or in this builder's own pool tree (t270), never on the clone's or the lane's caches. Units: GB = 10^9 bytes, MB =
10^6; "proc-s" = process-seconds (a process in a state for one second).

## The window and the method

- **Window**: 2026-11-28 04:44:28Z to 05:09:37Z (1,500 s; `start.txt`, `end.txt`), four pool trees and the lane busy, load
  about 27-30 on 22 cores at its start.
- **Per-process IO** (`t562-sampler.py`): every 0.5 s, every process's `/proc/<pid>/io` (write_bytes, read_bytes, syscw,
  cancelled_write_bytes), its cmdline, cwd, ancestry and CARGO_TARGET_DIR/TMPDIR at first sight; every 5 s the system series
  (`/proc/pressure/io`, the cgroup's io.pressure, memory.pressure, io.stat, memory.stat, `/proc/fs/jbd2/nvme0n1p3-8/info`,
  `/proc/diskstats`, `/proc/vmstat`, procs_blocked). 10,796 processes seen.
- **Why the per-process figures are LEAVES** (`t562-roots.py`): `/proc/<pid>/io` is INCLUSIVE of reaped children (tested: a
  shell's write_bytes grew by its `dd` child's 20 MiB), and claude (pid 31) reaps every tool call, so a parent's delta mixes in
  its children's whole lifetimes. A process with no child seen has only its own IO: the leaves' sum (16.4 GB written) is a lower
  bound by kind; the rest of the 29.6 GB the cgroup wrote came from processes too short-lived for a 0.5 s sample, threads that
  ended between samples, and deleted files' writeback. `t562-analyze.py`'s exclusive figures (`analysis.json`, `by_*`) are kept
  but are NOT reliable for the claude/cargo/l7r-gate rows for that reason; use `roots.txt`'s LEAVES table.
- **Who waits, and on what** (`t562-dstate.py`, 04:46-05:04Z, 1,080 s): every 0.2 s, each process in state D (uninterruptible:
  IO) with its `wchan` and cwd. tracefs is not mounted, `perf_event_paranoid` is 4 and ptrace is refused, so fsync callers could
  not be traced (`strace` and `perf trace` both refused); `task_delayacct` is off (a sysctl, not changed).
- **Which files** (`census-summary.txt`): `find -newermt <start> ! -newermt <end>` over the cargo targets, `/tmp`, the clones and
  `~/.claude` at 05:10Z - files written in the window and still present.

## (2) The disk and the journal over the window

| figure | value | source |
|---|---|---|
| disk written (nvme0n1, diskstats) | 32.09 GB (21.4 MB/s); the ext4 lifetime_write_kbytes delta the same | `analysis.json` `disk` |
| the container's cgroup wrote / read (io.stat) | 29.57 GB / 30.32 GB | `cgroup_io` |
| of the reads, page-cache REFAULTS (memory.stat workingset_refault_file) | 29.52 GB - 97% of all reads re-read pages the 10 GiB cap had evicted | `refault_file_GB` |
| direct reclaim scanned | 36.6 GB | `pgscan_direct_GB` |
| memory.current | 8.14-10.73 GB, median 10.1 (the cap 10.74): page cache fills the cap | `memcur_GB_series` |
| dirty pages | 0-1,034 MB, median 329 | `dirty_MB_series` |
| disk time (diskstats weighted ms) | writes 20,240 s, reads 3,805 s: a write waits 5x a read's queue time in total | `disk` |
| device busy (io_ticks) | 577 s of 1,500 (38%) | |
| journal transactions (jbd2 info, delta) | 1,951 in 1,500 s (1.3/s), and **all 1,951 "requested"**: forced by fsync/sync, none by the 5 s timer | `jbd2` |
| average commit time (jbd2's own moving average, read every 5 s - not a single commit's time) | median 38 ms, max 1,975 ms | `commit_us_series` |
| jbd2's other averages (running, blocks, handles a transaction) | did not move (879-881 ms, 208, 2,783-2,788): since-mount means over 299k transactions, NOT window figures - do not quote them as now | |
| IO pressure, the cgroup | full 310.7 s (20.7% of the window), some 355.8 s (23.7%) | `cg_io_psi_*` |
| IO pressure, the host | full 328.7 s (21.9%), some 384.1 s (25.6%); avg10 full median 18.0%, max 67.5% | `host_io_psi_*` |
| memory pressure, the cgroup | full 32.6 s (2.2%) | |
| CPU in iowait | 12.6% | |
| processes blocked | 0-81, median 1 | `blocked_series` |

## (1) Who writes - and (4) small files against bulk

Writes by the leaves (no child seen; `roots.txt`), GB written, of the cgroup's 29.6:

| kind | GB written | processes |
|---|---|---|
| rustc (builds, not coverage) | 10.78 | 520 |
| rustc (coverage builds) | 3.06 | 90 |
| clippy-driver | 1.24 | 127 |
| git | 0.37 | 2,055 |
| tar, cp (the handouts' and carries' copies) | 0.42 | 38 |
| rust-lld | 0.19 | 74 |
| test binaries (coverage) | 0.09 | 30 |
| everything else (the gate binary, the guard, the samplers, python3) | under 0.2 | |

The same leaves by make target, by tree and by kind within target (`t562-leaves.py`, `leaves.txt`; the lane's work is marked by
an ancestor `l7r-gate lane --work`; 13.2 GB of the 29.6 is unlabeled - short-lived processes, ended threads, deleted files):

| make target | GB | | tree | GB |
|---|---|---|---|---|
| builder-checks | 3.10 | | the clone (`diagram-backlog`) | 7.23 |
| no make (the cover runs launched by `l7r-gate.sh` directly, the gate binary) | 2.66 | | t269 | 5.95 |
| carry | 1.94 | | the landing tree | 1.37 |
| static | 1.63 | | the mirror (`diagram`, render-sync) | 0.96 |
| builder-done | 1.24 | | b1 | 0.87 |
| the lane (its runner 0.60, its `make land` 0.57) | 1.17 | | t270, t271 | about 0 (t270 was this measurement's) |
| render-sync | 0.90 | | | |
| map | 0.61 | | | |
| task-add, plan-section, decide (each rebuilding the gate tool after a gate edit) | 1.24 | | | |
| hooks-test | 0.40 | | | |

By kind within target, the largest: rustc in builder-checks 2.58, rustc coverage with no make 2.32, rustc in carry 1.91, rustc in
builder-done 1.11, clippy in static 0.76, rustc coverage in static 0.74. Cargo steps: build and clippy are rustc's and
clippy-driver's rows; the tests' own writes (test binaries) are 0.7 GB.

So **the compiler writes at least 51% of all bytes** (15.1 of 29.6 GB). The files say where (`census-summary.txt`): of 14.56 GB
written and still present, **11.37 GB (78%) is `incremental/`** - 7.78 GB in the build targets, 3.59 GB in the coverage
targets, in 15,571 files; rlibs 1.38 GB, test executables 0.94 GB. The deleted part (32.1 GB on disk against 14.6 GB still
present) is mostly rustc's incremental session directories, which it writes afresh each build and removes, and the tests'
TMPDIRs.

**Small files against bulk**: 12,918 of the 20,042 files (64%) were under 64 KiB, and they held 221.5 MB - 1.5% of the bytes.
The bytes are bulk (incremental object and query files, rlibs, executables). The small files cost journal handles, not bytes:
cargo's fingerprints, `.d` files and build-script outputs were 2,256 files and 3.7 MB of the window.

**The event logs, samplers and the lane's state are negligible**: `.git` of the clone 0.118 GB in 862 files (the git index is
3.84 MB a rewrite, 31,220 entries), `~/.claude` 11 MB, the sampler 0 B. Batching appends would save nothing measurable.

## (3) What the stall costs: who waits, and on what

`dstate.json`, 1,080 s: on average 1.98 processes were in D state (max 80). Of the 9,398 D samples the top-200 table places
(of 10,548), by wait channel and place:

| | proc-s | share |
|---|---|---|
| **journal waits** (`do_get_write_access`, `wait_transaction_locked`, `ext4_orphan_add/del`, `jbd2_log_wait_commit`, `__lock_buffer`) | 848 | 45% |
| page or buffer waits (`folio_wait_bit_common`, `__wait_on_buffer`: a read, or an fsync waiting on writeback - the channel does not tell them apart) | 736 | 39% |
| ... of it in the tests' TMPDIRs (mostly git: likelier fsync's writeback than reads) | 449 | 24% |
| ... of it elsewhere (the trees' builds: the refault reads' floor) | 287 | 15% |
| the device queue full (`blk_mq_get_tag`) | 250 | 13% |
| **git processes, all places** | 1,373 | 73% |
| **anything in the tests' TMPDIRs** (`/tmp/l7r-tmp/l7r-rust-tests-*`: the lane, task, guard, shared, pages suites' fixture repos) | 1,265 | 67% |
| ... of it journal waits | 667 | 35% |
| the clone and the pool trees | 409 | 22% |

The git processes in the tests' TMPDIRs (1,956 sampled; `init` 223, `push` 65, `cherry-pick` 61, `maintenance` 27, `commit` 21)
wrote only 0.06 GB. **The waiting is the tests' fixture git, not their bytes.** Who REQUESTS the forced commits is not measured
here (no tracing): git's default fsync can force them (the 40-fixture loop forced 26-32 commits by default against 2-3 with
`core.fsync=none`, `git-fsync-ab.tsv`), and an fsync forces a commit of every pending metadata change on the partition, which
every other writer then waits on. But commits ran at about 1.3/s whatever the fixtures did: per 5 s slice, 6.4 commits in the 258
slices with no fixture git sampled against 10.1 in the 30 with one (correlation 0.17; all git 0.18), and the suites' A/B forced
as many commits with `core.fsync=none` as without (`suite-ab.tsv`'s `jbd2_requested`). So fixture git is where the time is lost
and one source of forced commits; whether it is the main one is T563's trial and the host-side trace below.

The gate's phases over the window beside the cgroup's IO pressure (`phases.txt`; avg10 full sampled at each phase's start,
middle and end): `land suite` 67 runs, 1,077 s, at 30.7% mean; `builder-checks test` 12 runs, 210 s, at 34.3%; `land static`
564 s at 27.7%; `rust-cover cover-build` 429 s at 21.5%; `builder-checks build` 207 s at 19.7%. The test phases - the fixture-heavy
ones - ran at the highest pressure.

`make task-time SINCE=2026-11-28T04:44:28Z UNTIL=2026-11-28T05:09:37Z` (`task-time.txt`): 130.7 working minutes on the tasks' side,
compile 11.6 and tests 9.5 of them. Its top row, python3 43.2 min, is this measurement's own two samplers (reading `/proc`, one
process each for the window): not builder work.

## (5) The levers, priced in time

| lever | measured | verdict |
|---|---|---|
| **A. git `core.fsync=none` for the tests' fixture repos** (env `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsync GIT_CONFIG_VALUE_0=none` beside the runners' TMPDIR) | A 40-fixture loop (init, add, commit, branch, update-ref, commit, status; `git-fsync-ab.tsv`, ABAB): at load 14, 5.57 s default against 1.77 s, journal forced commits 6 against 2; at load 17, 1.39/1.18 s against 1.32/1.13 s (forced commits 26-32 against 2-3). Whole suites (`suite-ab.tsv`, `make rust-test`, `L7R_RUST_FRESH=1`, ABAB; `tests_s` is the LAST test binary's "finished in", the wall is the whole command): shared at load 23-25, tests 8.12 / 10.49 s default against 4.95 / 3.43 s, wall 10.77 / 11.85 s against 6.74 / 16.87 s; guard at load 25-29, tests 2.35 / 5.86 s against 2.11 / 2.80 s, wall 3.35 / 6.81 against 3.04 / 3.86 s; lane and task at load 6-14, no difference. Two rounds each, and one fsync-none wall the slowest of all: a signal, not a figure. | **The likeliest lever.** Repository-level, a few env lines. The upper bound on its share: the tests' fixture git is 67% of the IO-wait time and half of that is journal waits; the test phases are 1,442 phase-seconds of the 25 minutes (land suite 1,077, builder-checks test 210, hooks-test 155). If the suites halve under pressure, as shared did, that is about 12 phase-minutes per 25-minute busy window. Every other writer gains from the fewer forced commits too. Filed as **T563** for a trial at load. |
| **B. A tmpfs for the tests' TMPDIRs** (`/tmp/l7r-tmp`; `rust/guard/shared/src/tempdir.rs` honors `TMPDIR`) | Live size (`tmpdu.tsv`, every 2 s for 4 minutes while the guard, shared and lane suites ran here beside the other trees' work): peak 17.6 MB, 1,458 files. Not trialled: `/dev/shm` (63 MB) is `noexec`, and the suites exec stub scripts in their TMPDIR (`/dev/shm/t562/x`: Permission denied); a new tmpfs is a mount. | **Host-level, for the GM.** It fits: one tree's three suites peaked at 17.6 MB; five trees' suites at once at about five times that, under 0.1 GB, is an ESTIMATE (not sampled at the window's load) against the 10 GiB cap. It would remove both the fixtures' fsyncs (a no-op on tmpfs) and their create/unlink journaling (`ext4_orphan_*` 5.3% of the waits). The config: a docker `--tmpfs /tmp/l7r-tmp:rw,exec,size=1g,mode=1777` (or a tmpfs mounted there), nothing else changed. Lever A gets most of it without a mount. |
| **C. The GM's question: a tmpfs for only cargo's small, much-written files** | Live bytes across ALL target trees: fingerprints 16.5 MB (45,650 files), `.d` files 63.9 MB (11,166), build-script `out/` 58.0 MB - about 0.14 GB, 1.3% of the cap. Written in the window: 3.7 MB and 2,256 files of the 20,042 touched (11%). | **It fits, and removes no forced commit; host-level, for the GM, not recommended.** The journal's transactions were all forced (1,951 of 1,951), so their number follows the fsync rate rather than how many files are touched - Cargo does not feed it: a cold 96 s build of the phases and guard crates into a scratch target forced 0.42 commits a second against 0.57 in the minute before and 0.56 after (`t562-cargo-commits.sh`, `cargo-commits2.tsv`; a 6.8 s build of phases alone, 0.59 against 0.65 and 0.40, `cargo-commits.tsv`). The bytes and files are small too: 11% of the files touched, 0.03% of the bytes. Its time is unmeasured (a mount) and expected small: not recommended. Cargo has no setting to put fingerprints outside the target directory (only symlinks per profile directory, lost at a reboot). The much-written cargo files are `incremental/`, and those are the bulk, not small: next row. |
| **D. A tmpfs for the incremental directories or a whole target** | Live `incremental/` (`du`, 05:20Z): 118 GB across the targets - the clone 31.5, t269 18.8, t270 18.9, t271 17.6, the landing tree 14.5, b1 14.3; one pool tree's build incremental alone 10.2 GB. | **Does not fit.** tmpfs pages are charged to the same 10 GiB cgroup, which page cache already fills (median 10.1 GB), so even a few GB of tmpfs would evict more page cache and raise the refault reads (97% of reads already). |
| **E. `CARGO_INCREMENTAL=0` for coverage builds** (`incr-ab.tsv`, `incr-ab2.tsv`: `l7r-gate.sh rust cover --crate rust/phases` on a `git archive` copy, a scratch target a setting) | Cold: 60.5 s, 0.36 GB written, 1,848 files (default) against 64.8 s, 0.16 GB, 232 files. Warm after a one-line edit, ABAB: 10.1 / 8.8 / 12.2 s default against 28.9 / 21.6 / 34.1 s (load 11-23). | **Rejected.** It saves 0.2 GB a cold build, under 10 s of disk time at the window's rate, and costs 13-22 s on every warm rebuild. The coverage targets' incremental is 3.59 GB of the window's writes, but it is what makes a repair's rebuild fast. |
| **F. Batched appends, fewer small files of our own** | The event logs, lane state, samplers and `.git` state: 0.13 GB and about 1,000 files in the window. | **Rejected**: under 0.5% of the bytes. |
| **G. The page-cache thrash** (29.5 GB of refault reads in 25 minutes) | The 10 GiB cap counts page cache; six target trees of 14-48 GB each are the working set. Page or buffer waits outside the tests' TMPDIRs are 15% of the IO-wait time (the floor); all page or buffer waits 39% (the ceiling, since some are fsync's writeback waits). | **Host-level, for the GM**: a larger memory cap for the container (page cache would hold more of the trees' rlibs) is the direct lever. In the repository, T520 priced shrinking the per-tree working set (`dev/measurements/2026-11-27/t520-cache-working-set/results.md`). |

## For the GM (host-level, not done here)

1. **What was measured of the freeze**: every journal commit in the window was forced (1,951 in 25 minutes, none by the
   timer), the journal's moving-average commit time reached 1,975 ms, and journal waits were 45% of the container's IO waits.
   Git processes were 73% of the IO-wait time and the tests' throwaway fixture repos 67%; git's default fsync can force
   commits, but who requests most of them is NOT measured here (no tracing in the container). Lever A (filed, T563) is the
   repository's side. To name the fsync callers on the host, where tracing works:
   `sudo perf trace -s -e fsync,fdatasync,msync -a -- sleep 60` or
   `sudo bpftrace -e 'tracepoint:syscalls:sys_enter_fsync,tracepoint:syscalls:sys_enter_fdatasync { @[comm] = count(); }'`.
2. **A tmpfs for `/tmp/l7r-tmp`** (lever B): under 0.1 GB, removes the fixtures' journaling outright.
   **Your question, a tmpfs for cargo's small files** (lever C): it fits (0.14 GB live: fingerprints, `.d` files, build-script
   outputs, across every target), but those files are 0.03% of the bytes written and a cold cargo build forced no more journal
   commits than the machine's background rate; the much-written cargo files are `incremental/`, which is bulk (118 GB live) and cannot fit. The tiny-file churn
   that does fit and does wait on the journal is the tests' TMPDIRs: item 2.
3. **The memory cap** (lever G): reads are 97% refaults of the build cache under the 10 GiB cap.
4. **ext4 options** (`commit=`, `data=writeback`, `barrier`) were not priced: they trade durability on the host's one partition
   for every file on it; the trace in item 1 says first whether the forced commits come from a source the repository controls.

## Reproduce

    S=<scratch>; python3 -I t562-sampler.py $S/run 1500 &; python3 -I t562-dstate.py $S/run/dstate.json 1080 &
    python3 -I t562-analyze.py $S/run/samples.json > analysis.json; python3 -I t562-roots.py $S/run/samples.json > roots.txt
    python3 -I t562-leaves.py $S/run/samples.json > leaves.txt
    bash t562-git-fsync-ab.sh $S/gitab git-fsync-ab.tsv 40 3
    bash t562-suite-ab.sh <a pool tree you hold> rust/guard/shared suite-ab.tsv 2
    bash t562-incr-ab.sh $S/incr $PWD/incr-ab.tsv          # rust/phases on a git archive of HEAD
    bash t562-tmpdu.sh $PWD/tmpdu.tsv 240

The raw sample file (27 MB) and the file census (3.4 MB) stayed in the scratchpad.
