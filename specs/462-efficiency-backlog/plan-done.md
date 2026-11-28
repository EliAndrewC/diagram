# 462-efficiency-backlog - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-11-28 -->
### T278 (451 T278's line: the cargo-variant sweep keeps 16 variants a crate and prunes only after 12 idle hours, and the clone's `cover-gate` held 44 GB where a fresh one is 2.65 GB, measured 2026-11-26 (`dev/measurements/2026-11-26/build-levers`); measured again 2026-11-27 after T325 and T515 had landed)

- **Approach**: a measurement, no code changed. The record is `dev/measurements/2026-11-27/t278-variants/results.md`, its scripts and tables beside it (`t278-count.py`, `t278-net.py`, `t278-live.py`, `t278-prune.py`, `t278-build.sh`, `t278-arms.sh`; `t278-count.tsv`, `t278-net.tsv`, `t278-runs.tsv`). Every read of a live cache was by `lstat` alone; every build ran on a copy in the session scratchpad, and the copies were deleted after.
  - **What was measured.** The variants per crate in all 27 `cover-*` directories, and what the sweep (`rust/guard/src/guards/scratch_sweep_hooks/sweep/cargo.rs`, `KEPT = 16`, `L7R_CACHE_IDLE_HOURS` = 12) would take at keep 16, 8, 4, 2 and 1, each at idle cutoffs of 12, 6, 1 and 0 h, gross and net of T515's 48 h prune, measured 2026-11-27 (`t278-count.py`, `t278-net.py`). Then the gate family's coverage build, a hand replica of `cover.rs`'s call (validated: 0 units compiled, 80 fresh, 0.5 s after the warm-up), on a copy of `diagram-backlog-t270/cover-gate` warmed to HEAD, with the rule applied at keep 16, 4 and 2: a warm whole-family build, a warm `-p l7r_gate_claims` alone, and the whole family after a one-line edit of `rust/gate/crates/registry/src/lib.rs`, measured 2026-11-27 (`t278-arms.sh`). Units compiled is the figure to go by: wall time moved from 124 to 202 s across arms that compiled the same 27 units, with the machine at load 14 to 57 on 22 cores, measured 2026-11-27 (`t278-runs.tsv`).
  - **Today, the rule as it stands takes almost nothing.** Keep 16 at 12 h takes 0.02 GB, all of it in the clone's `cover-gate` (17.27 GB, 1,349 entries, largest group 17), and 0.00 GB in every other directory, measured 2026-11-27 (`t278-count.py`). T515's prune did the work: the clone's `cover-gate` went from 44 GB to 17.3 GB, measured 2026-11-26 and 2026-11-27 (`build-levers`, `t278-count.py`).
  - **The levers priced**, measured 2026-11-27 (`t278-net.py`, `t278-arms.sh`):

    | lever | GB taken, all 27 `cover-*` | net of T515 | of which the clone's `cover-gate` | time lost |
    |---|---|---|---|---|
    | keep 16 → 8 | 3.11 | 0.78 | 0.78 | 0 (no live entry within 4 of the cut) |
    | keep 16 → 4 | 11.52 | 5.69 | 3.78 | 0 measured (0 units warm; the same 27 after the edit as at keep 16), but no margin: keep 3 takes a live entry |
    | keep 16 → 2 | 26.40 | 16.68 | 6.48 | 62 units, 297.9 s on the next warm build, and 14 units, 41.9 s on a second `-p` selection, measured 2026-11-27 (`t278-runs.tsv`) |
    | idle 12 h → 0 h, at keep 16 | 0.02 | 0.02 | 0.02 | 0, measured 2026-11-27 (`t278-net.tsv`) |

    The net is an upper bound: `t278-net.py` leaves out T515's newest-of-kind keep.
  - **Why keep 4 has no margin.** `variant_of` groups a crate's library, its build-script compile and its build-script run under one name, so a crate with a build script has 3 live entries in `.fingerprint`, and two `-p` selections that resolve an outside crate differently add a fourth. Keep 3 already takes `.fingerprint/serde_json-864f8b427ec4b3cb`, a live build-script run unit, measured 2026-11-27 (`t278-prune.py ... 3 12 --live`).
  - **The idle cutoff is no lever.** At every keep the take at 12, 6, 1 and 0 h is the same to the hundredth of a GB in every directory, measured 2026-11-27 (`t278-count.tsv`'s `take_k*_h*` columns): the entries past rank 16 are all older than 12 h, so the cutoff never decides what goes and frees 0 GB.
  - **The decision: no lever is adopted here.** Keep 16 stays. Keep 2 loses time, so the GM's rule (time saved outranks disk, 462 T301's restatement of 2026-11-26) rules it out. The idle cutoff frees 0 GB, measured 2026-11-27 (`t278-count.tsv`). Keep 4 lost no time, but only by luck of today's groups: one more live unit in a group (a fourth `-p` resolution, a second build script) and it evicts a live entry. Keep 8 is safe with 4 of margin but frees only 0.78 GB net, measured 2026-11-27 (`t278-net.tsv`). Adopting either changes `cargo.rs` and its suite, which a measurement does not do. Filed as T556: adopt keep 4 only with the group split by unit kind (library, build-script compile, build-script run, as T515's newest-of-kind does), else keep 8.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| no code changed: a measurement, its record and scripts in `dev/measurements/2026-11-27/t278-variants/` | n/a: nothing fixed | n/a: tooling | none | n/a |

### T321 (451 T104's and T304's builders each held the machine at a load of 240 to 400 for over an hour by hand on 2026-11-26, slowing two batch gates and failing a third suite; a reproduction under load had no bounded tool)

- **Approach**: a new command, `make under-load CMD="<command>" COPIES=<n> LOOPS=<n> MAX_MINUTES=<m> [BURNERS=<n>]`, running `l7r-gate rust under-load` (`rust/gate/crates/rustc/src/rustc/under_load.rs` and `under_load/warden.rs`). Built by the task's build half (its handoff, `T321-build.md`); this section is the closing half's.
  - **What it runs.** COPIES copies of CMD at once (`sh -c CMD`, each told `L7R_UNDER_LOAD_COPY` and `_LOOP`, its output to `c<copy>-l<loop>.log`), each LOOPS times one after another, beside BURNERS pure busy loops (default 0). Both kinds of load are offered because the task line names copies, loops and burners, and the hand runs of 2026-11-27 were 10 and 30 concurrent copies of the test itself (461 T58's "6x10" is COPIES=10 LOOPS=6). Label: the easier route, the record silent (tooling).
  - **The bound, two layers.** The caller re-runs its own program as a WARDEN in a process group of its own, its stdin a pipe the caller holds and never writes. The warden spawns a SENTINEL first (`sh -c 'sleep "$0"; kill -s KILL 0'` for the bound plus twice GRACE_S) in a new group G, which every burner and copy then joins; the warden stays outside G. The warden polls every 0.5 s (a GUESS knob) - the 1-minute load, every copy done, the caller's pipe at EOF, the deadline - and at the end shuts a gate (no loop starts after it), sends TERM to G, waits up to GRACE_S (10 s, a GUESS knob) and sends KILL to G, reaping the burners and the sentinel last so G's id is never reused while it can be signalled. The warden alone would not survive a SIGKILL; the sentinel alone gives no early stop and no Phase line. A per-run `timeout` was rejected: `/usr/bin/timeout` here is uutils 0.8.0, and it leaves the group anyway.
  - **What it prints and books.** Red (exit not 0, not cut), cut (exit not 0 with the gate shut, counted apart) and green; up to 10 red logs named; the load at start, peak and end with ISO times; why it ended; the logs' directory (`$TMPDIR/l7r-under-load-<stamp>-<pid>/`, green logs removed). Exit 1 where any run was red. ONE Phase line (`phase.rs` `wrote_with`: `src: rust`, `step: under-load`, make target `under-load`, fields `cmd copies loops burners max_minutes runs red cut load_start load_peak load_end ended group logs`). `columns::category()` gives it no category and `ran::kind()` counts it as no unit-test run, so it adds no false test count; its minutes go to `tests` by a new row of the guard's BUCKETS table (`make under-load`), and the inner `make rust-test` calls' own `build` and `test` lines book as ever. `cli` dispatches it ahead of the run lock, as the pre-warm is, so the copies' own `make rust-test` runs are the same run and overlap rather than queue. Rejected: reusing `(rust, test)` (a false unit-test count) and `src: quick` (a false source).
  - **Caps** (GUESS knobs, `dev/audits/under-load.md`): MAX_MINUTES at most 60 (MAX_MINUTES_CAP), COPIES + BURNERS at most 3 a core (PER_CORE, a GUESS knob, so 66 on this 22-core machine), GRACE_S 10 s (a GUESS knob), so every process of a run is gone by MAX_MINUTES plus 20 s (twice GRACE_S, a GUESS knob).
  - **Moved, unchanged.** `event_log_hooks.rs` stood at 1,000 lines and the BUCKETS row took it to 1,002, past the file-size bar (constitution X clause 13), so the category table (`BUCKETS`, its doc and `bucket_of`, 177 lines) moved to `event_log_hooks/buckets.rs`, re-exported, every old path resolving, observed 2026-11-27, method: the hand-in's first pass refusing the file at 1,002 lines and `wc -l` after the move (826).
  - **The brief's clause.** "Runs ALONE in its batch" was already in `scripts/container/builder-brief.md` (`LOAD=1`; 451 T321; feature 460); nothing rebuilt, and the Makefile help says it again.
  - **Measured 2026-11-27, pool tree `diagram-backlog-t269`, 22 cores.** A real run (`make under-load CMD='make rust-test CRATE=rust/gate/crates/rustc ONLY="rustc::tests::under_load::the_words"' COPIES=2 LOOPS=2 BURNERS=1 MAX_MINUTES=1`): 4 of 4 green in 3.0 s, its four inner `test` Phase lines under make target `under-load` overlapping in pairs, and one `under-load` line. The caller's group SIGKILLed mid-run: the load group of 10 processes empty 0.7 s later, `ended: the caller went away`, 3 runs, 3 cut, measured 2026-11-27 (`setsid make under-load CMD='sleep 60' COPIES=3 LOOPS=2 BURNERS=2 MAX_MINUTES=2`, then `kill -KILL -- -<pgid>`). The warden SIGKILLed with the caller: the group empty 25.9 s after the kills - the sentinel at 6 s plus 2 x 10 s, measured 2026-11-27 (MAX_MINUTES=0.1, `kill -KILL <warden>` and the caller's group).
  - **Red-first**, measured 2026-11-27 (each mutation alone, `make rust-test ONLY=rustc::tests::under_load`, 10 tests): no sentinel kill 9 passed 1 failed; no caller watch 9/1; no TERM 9/1; no KILL 8/2; gate never shut 7/3; the warden in the caller's group 9/1; after, 10 of 10.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the command `make under-load` (`under_load.rs`, `warden.rs`, `phase.rs`, `rustc.rs`, the Makefile) | n/a: a new command, each part pinned by the six red-first mutations above | n/a: tooling | none | n/a |
| the BUCKETS row and the table's move to `buckets.rs` | n/a: a booking, pinned by the guard crate's own tests | n/a: tooling | none | n/a |

### T371 (lever B of 451 T365, `dev/measurements/2026-11-26/tmp-clutter/t365-results.md`: TempDir's sweep lists the whole temp directory)

- **Approach**: `l7r_shared::tempdir::TempDir::new` makes its directory under `<temp dir>/l7r-tmp/` (the new `SUBDIR`) and its
  once-a-process sweep (`sweep_dead`, T370) lists that subdirectory alone (`rust/guard/shared/src/tempdir.rs`). The two runners'
  leak checks, which fail on anything a run leaves in its own `TMPDIR`, pass over an empty `l7r-tmp` and name what is inside one
  as `l7r-tmp/<name>` (`rust/gate/crates/rustc/src/rustc/run.rs`'s `leak_checked`, `tests/hooks/hookrun.sh`'s LEAK line). By T365:
  one listing of `/tmp` 14 to 16 ms (5,443 entries, 21.9 MB directory file), of a directory that never grew 0.06 ms + 0.41 ms each
  1,000 entries, measured 2026-11-26 (a 300-call loop of the real helper, T365's `t365-loop-new.txt`), and the leak pin listed `/tmp`
  once a crate run, 21.6 ms, measured 2026-11-26 (an `LD_PRELOAD` shim counting `opendir` of the temp directory,
  `t365-shim-rust-test.txt`). After: see the performance checklist's item 5.
- **Built here, found beside it**: `tree::command_head` no longer cuts a walk target's `head` at 120 characters. The cut hid a long
  command's end from two guards: `builder_pool_hooks` read no `worktree remove` behind a `git -C <path> ` of 106 characters,
  observed 2026-11-27, method: the failing test's message, its prefix counted with `wc -c`; and `parked::shell_hits` read a
  `git mv`'s destination from `segment`, also cut at 120. Both tests failed once the fixtures' paths grew by `l7r-tmp/`; the parked
  reader now reads `head`, and the context-cap band's message cuts its own copy at 120 as before. A guard now refuses a long command
  it already refused short - no new rule, the same rule at any length.
  One test only measured its fixture's path: `builder_brief::tests::each_kind_s_block_opens_with_its_marker_and_stays_short` counted
  a block naming the fixture's tree, 2,024 characters against its 2,000 cap, observed 2026-11-27, method: the test's failing
  message (`{n}`) in a `FRESH=1` run of `rust/gate/crates/task`; it now counts the block with the fixture's directory read as
  `/diagram/.clones`. Not a defect: the block's length moved only with the fixture's path, which is about 91 characters to a pool
  tree's 37 (`/diagram/.clones/diagram-backlog-t269`), observed 2026-11-27, method: both counted with `wc -c`; the command's code that
  writes a real brief is unchanged.
- **The leak checks pass over an empty `l7r-tmp` only**: every test process that makes a `TempDir` now leaves that one empty
  directory in its run's `TMPDIR`, by design (it is never removed, `SUBDIR`'s comment says why); a run that leaves anything inside
  it still fails, named `l7r-tmp/<name>` (pinned by the leak pin test's `l7r-tmp/l7r-leak-3`). It goes with the run's directory.
- **How it leaves T377, T378 and T379** (their lines in tasks.md): T377's says "the alternative to T371, build one of the two", so
  with this landed it is for the session to withdraw; T378's says "withdraw it when T371 or T377 lands"; T379's says "withdraw it
  when T371 and T372 land", so it stays open while T372 (the hook suites' glob, untouched here) is. This task withdraws none.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the subdirectory and its sweep | `tempdir::tests::its_directories_and_its_sweep_stay_in_one_subdirectory` | n/a (no engine) | none | none |
| the leak pin over it | `rustc::tests::what_a_crate_s_tests_leave_in_their_tmpdir_fails_it_by_name_and_goes` | n/a | none | none |
| the head uncut | `tree::tests::the_walk_judges_a_python_program_run_from_stdin` | n/a | none | none |

### T533 (451 T517's backlog: the landing session's scratchpad held 17.86 GB of 451 tasks landed before T517, observed 2026-11-27, method: `du -s` against `tasks-done.md`)

- **Approach**: a one-off take by hand, no code. The landing session is the coordinating session itself (`CLAUDE_CODE_SESSION_ID=c6fd72d1-ab6c-4736-b723-0697a1f5ca51`, the only scratchpad under `/tmp/claude-1000` past 100K, observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`), so the session ruled that its brief's ban on that scratchpad gives way for this take, done from a computed list rather than a new sweep mode: `--scratch-sweep landed` has no dry form and also takes `/tmp/t<N>`, the clones' `.git/t<N>` and the start marks, and the rule's own fix is T550.
- **The list**: an entry of the scratchpad whose name is `t` then a whole number N (`t51` is never `t515`'s, `leftovers::number`), N ticked `[x]` in 451's `tasks-done.md`.
- **Excluded**: N held by another feature's open start (`open_elsewhere` as built, re-run over the clone's `task-starts.jsonl` and `specs/*/tasks.md`, the numbers 6, 11, 12, 27, 34, 36, 42, 55, 106, 127, 158, in 49 entries, observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`), an entry a live process holds (`/proc/*/cwd` and `fd`, 4 entries, observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`), one holding a registered worktree (none), 451's open numbers (`t537`, 44 entries of 0.37 GB, observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`), the 101 numbers 451 ticks as `Withdrawn: moved to 462` (observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`), every task number of 461 or 462 open or ticked, and every entry without a `t<N>` prefix (597 entries of 2.52 GB, `m14` among them, observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`).
- **Removed** with `rm -rf` over the list, and no guard refused. The list, the wrong removals and the script are `dev/measurements/2026-11-27/t533-scratchpad-take/` (`take.txt`, bytes and name a line, `wrongly-taken.txt`, `measure.py`).
- **Measured**: before 17,965,240,831 bytes in 4,177 entries, after 3,354,947,305 bytes in 1,260 entries, taken 2,917 entries of about 14.61 GB (`t373` 3.50 GB, `t388` 2.99 GB, `t386-bench` 0.99 GB, `t457-clone` 0.91 GB and `t419` 0.77 GB the largest), observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`, just before and after.
- **The 144 wrong removals**: the 461 and 462 numbers were read from the `/diagram` mirror's `tasks.md`, which is behind the session clone's, the mirror's 461 holding no T50-T70 where the clone's lists them open. So 144 entries of 1,385,388 bytes of 461 T50, T53, T54, T56, T58 (22 entries), T59, T60, T61, T62 (68 entries, its `t62-load-*` series and `t62-section.md`), T65, T67, T68 and T69 were taken with 451's same numbers (observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`, `wrongly-taken.txt`). Harmless, the session confirmed: each of those tasks was already handed in and carried, its section, records and tests committed, and no builder was working one. Read from the clone, the list would have held 2,773 entries (observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`). The lesson is T550's: another feature's task numbers are read from the clone that lands, never the mirror.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the landed `t<N>` entries of feature 451 in the session's scratchpad taken once, the exclusions above kept | n/a: a one-off take, no code, before and after measured 2026-11-27 (`du -sb`) | n/a: no code | none | n/a |

### T545 (moved here from 462 FR-004's 451 T537 by the round arbiter's accept, ask:451-T537-plan-review-json, 2026-11-27: 451's plan-review.json stood at 5,074,158 bytes, its live entries a small part, and the tools read it whole every call; observed 2026-11-27, method: `ls -la` of the feature directory)

- **Approach**: `make archive-split` (`l7r-gate plan split`, now `plan/split.rs`) cuts the record after plan-done.md and tasks-done.md are folded: the flat `plan-review.json` keeps its own format and its LIVE entries only, and each closed task's entries go to JSON parts under `archive/plan-review/` beside T537's, named in `archive/index.json` (`parts` and `tasks` under `plan-review.json`) and in `archive/INDEX.md`.
  - **What is live** (decided here): every key but the three maps kept; `blocks` of a block key plan.md holds (`plan_text::blocks`); `tasks` of a task with a section in plan.md or an open box in tasks.md; `block_reviews` rounds naming a live block or a live task. Each closed entry is grouped under its task (a tasks entry by its key, a block by its heading's leading task, a round by its first `tasks` id, else its first block's), groups packed in id order into parts of at most `archive::BOUND` (64 KiB, T537's GUESS knob), a group larger than it alone in its part; each part names every task it holds, its rounds' too. The parts are written before the flat file is rewritten (the plan crate's `pretty`, so the next `plan-verdict` does not reformat it): a failure between leaves an entry in both places, never in neither.
  - **The readers, checked first** (observed 2026-11-27, method: `grep -rn plan-review.json` over `rust/`, each hit read): the writers (`record.rs`, `slim`), the plan gate (`status.rs`, `task.rs`'s `push_held` at HEAD through `judge_held`), `plan-delta`'s bundle, the review-round guard (`review_round_hooks.rs`, its streaming reader), `task_withdraw.rs`, `accept_scope` and the arbiter bundle's `plan_rounds` read live tasks or the latest rounds - the flat file, unchanged. Two read a CLOSED task's verdict and are repointed to `archive::review(read, task)` (the parts the index names for that task, then the flat record): `inside.rs` `built_inside` for a host archived in plan-done.md, and the ledger's `rows.rs` `in_the_record` where the live record has no entry for the task. `left.rs` reads tasks.md, not the record. `feature_report/sources.rs`'s `plan_blocks` reads every committed version of the flat file through `git log -p`, so the split loses it no version. Name-keyed skips extended to the parts: `research_pointers::exempt` and `stale_terms::skipped`.
  - **The merge driver** (`merge.rs`): a map entry the split removed, unchanged on the other side from the base, already stays removed (`whole`); the `block_reviews` rows did not - a pre-split tree carried as OURS kept every base row (pinned red: `a_pre_split_side_resurrects_no_archived_entry`, 1 of 1 failing on the old `rows`). Fixed here: a base row the other side dropped is dropped, as a map entry is. The carry's usual direction (the clone ours, the builder's pre-split tree theirs) was already safe.
  - **The real split of 451** (observed 2026-11-27, method: `make archive-split F=451` in this tree, then the parts and the flat record joined in Python against a copy taken before): the flat record 5,074,158 -> 129,646 bytes, 12 of 788 blocks, 0 of 323 tasks and 15 of 588 rounds live (451 is closed, so the task line's 36/8/42 of before its close no longer hold); 88 parts, every one at most 65,536 bytes but T243's own group (70,116 bytes, alone in its part); parts plus flat equal the original's `blocks` and `tasks` maps key for key and its rounds as a multiset, no entry in two places.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the review's cut, its reader, the two readers repointed, the rows merge, the real split of 451 | n/a: tooling, no map drawn | n/a | none | n/a |

### T278 Approach (checklist part A)

1. **The goal, in the world.** The `cover-*` build directories hold no variant a later coverage build cannot reuse, and the sweep never evicts one a later build would rebuild; the session knows, from measurement, which keep and which idle cutoff do that.
2. **The constraints.** The GM's rule that time saved outranks disk and that nothing a later run would reuse is evicted (462 T301's restatement, 2026-11-26); the task line's order to adopt what loses no time; no live process or live cache touched, every build on a copy; T325 (one feature set per family) and T515 (the stale prune, `L7R_CACHE_STALE_HOURS`) landed first, so the measurement sees the variants that are left after them.
3. **Where each comes from.** G: the GM's words of 2026-11-26 on the disk work, restated in 462 T301's task line and held verbatim in `specs/451-time-retro-and-efficiency/request.md`: time saved outranks disk usage. O: `dev/measurements/2026-11-26/build-levers` (the clone's `cover-gate` that filed the task, measured 2026-11-26 there) and this record, `dev/measurements/2026-11-27/t278-variants/results.md`.
4. **Do they describe the world here?** Yes: the copy used for the builds matched its original's counts row for row, and the hand replica of the gate's coverage call compiled 0 units with 80 fresh after the warm-up, measured 2026-11-27 (`t278-count.py`, `t278-build.sh`).
5. **The order.** After T325 and T515 (both landed 2026-11-26/27, which change how many variants are live); before T556 (the keep change, filed here) and T558 (462 T301's part 2, what else no later run can reuse), which read this record.
6. **The exits.** Green: each lever priced in GB freed and units recompiled, measured 2026-11-27 (`t278-net.tsv`, `t278-runs.tsv`), and a lever adopted only if it lost nothing with margin. Keep 8 qualified (0 units lost, 4 of margin), but adopting it, or keep 4 with the group split, changes `cargo.rs` and its suite, which a measurement does not do, so the adoption is T556's. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing, of this section, the record and its scripts, and T556's line.
9. **Done, measured.** Keep 16 → 8, 4, 2 and the idle cutoff 12 → 0 h each priced at 0.78, 5.69, 16.68 and 0.02 GB net of T515, losing 0, 0 (no margin), 62 units and 297.9 s, and 0 units, measured 2026-11-27 (`t278-net.py`, `t278-arms.sh`).
10. **Before moving a constant.** No constant is moved here: `KEPT` stays 16 and `L7R_CACHE_IDLE_HOURS` 12. Moving `KEPT` is T556's, with the margin this record measured.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing is fixed here, and nothing a reader would see changes: no map moves, and the sweep is left as it is. The one finding with a cost - `variant_of` grouping three unit kinds under one name, so a smaller keep evicts a live build-script unit - is a defect only once the keep is lowered, and it is T556's.

**Found and left?**
- `variant_of` in `rust/guard/src/guards/scratch_sweep_hooks/sweep/cargo.rs` groups a crate's library, build-script compile and build-script run under one name, so at keep 3 the sweep takes a live entry (`.fingerprint/serde_json-864f8b427ec4b3cb`) and at keep 2 the next warm build of the gate family compiles 62 units in 297.9 s, measured 2026-11-27 (`t278-prune.py --live`, `t278-arms.sh`); visible effect: today none at keep 16, but it caps the keep the sweep can safely use at 4 with no margin, holding 5.69 GB net of T515 in place, measured 2026-11-27 (`t278-net.py`). Not fixed here: a measurement changes no source, and the fix (split the group by unit kind, then keep 4; else keep 8) is a change to `cargo.rs` and its suite. Filed as T556; lands before T558.

**Performance work?** no: disk work, ordered by the GM's order for 462 (T549); rebuild time was measured only to make sure no lever costs a later build any time.

### T321 Approach (checklist part A)

1. **The goal, in the world.** A builder that must reproduce a failure under load runs one command that loads the machine as asked and is gone by its bound whatever the builder does - killed, timed out at its context cap or forgotten - and the load's minutes appear in `make task-time`.
2. **The constraints.** The task line (COPIES, LOOPS, MAX_MINUTES, burners, the red count, the load and its start and end, a Phase line, the brief's ALONE clause); the builder-brief's `LOAD=1` rule (451 T321, feature 460); the file-size bar (constitution X clause 13); a guard file edited through `make guard-edit`.
3. **Where each comes from.** G: none beyond the task line as filed. O: the hand loads of 2026-11-26 (240 to 400 for over an hour, 451 T104, T304) and of 2026-11-27 (30 copies on 22 cores, a load of 38 to 86), and the build half's measurements above.
4. **Do they describe the world here?** Yes: the three runs above were made in a pool tree on this machine, a real `make rust-test` among them, measured 2026-11-27 (the runs above).
5. **The order.** After 451 T321's brief clause (landed); before any builder next loads the machine by hand.
6. **The exits.** Green: the module's tests green, the first tier over the build half's crates green, and `l7r-gate.sh rust cover` over `rustc` and `guard/shared` naming no line, each measured at the closing half (`make builder-checks`, the cover run). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The killed-caller run's group empty 0.7 s after the kill and the killed-warden run's 25.9 s after (inside its bound plus 20 s), measured 2026-11-27 (above); the coverage run naming no line.
10. **Before moving a constant.** n/a: MAX_MINUTES_CAP, PER_CORE and GRACE_S are new GUESS knobs, recorded in `dev/audits/under-load.md`.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing is fixed: a new command. No map changes; a builder's load run is bounded where it was not.

**Found and left?**
- A CMD that starts its own process group (`setsid`, `timeout`, a cargo the pre-warm starts) leaves G, and only its own parent ends it; visible effect: such a process can outlive the bound. Not a defect (constitution XIV): an accepted limitation of the design, not filed: a `/proc` sweep by an environment mark was priced and not built, and the checks' own cargo calls stay in the group (`dev/audits/under-load.md`, the module doc; the build half's choice).
- A kill at the bound can cut a rustc mid-write (`prewarm.rs`: 29 of 54); visible effect: one stale link on the next build, which `stale.rs` heals once. Not a defect (constitution XIV): an accepted cost, not filed, the help saying build first.

**Performance work?** no: the task is not a `[perf]` task; it bounds a reproduction's load so that batch gates beside it are not slowed, and makes no step faster itself.


### T371 Approach (checklist part A)

1. **The goal, in the world.** No `TempDir` listing reads `/tmp`'s top level: a process's one sweep reads only the helper's own
   subdirectory, which holds only live and dead helper directories.
2. **The constraints.** The coordinating session's brief for this task: measure before and after on a copy or a fixture, never
   deleting outside one - this deletes nothing anywhere new; the leak pins (449 T101) keep failing a run that leaves anything but
   the two known directories (the shared one, and `l7r-tmp` while empty), by name; the sweep's three-hour and dead-pid rule (the GM
   2026-11-11) unchanged.
3. **Where each comes from.** O: T365's measurement (above). G: 462's request.md (the disk tasks first); the before-and-after on a fixture is the brief's.
   R: none - tooling, no research page.
4. **Do they describe the world here?** Yes: `/tmp` held 5,434 top-level entries, measured 2026-11-27 (`ls -A /tmp | wc -l` at 17:43 EST).
5. **The order.** After T370 (once a process, landed); before T377/T378 (withdrawn by it) and independent of T372.
6. **The exits.** Green: the subdirectory test, the leak pin test and the head pin green, and the shim's count of `/tmp` listings
   by the leak pin at 0. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The shim over `make rust-test CRATE=rust/gate/crates/task FRESH=1`: `l7r-rust`'s listings of `/tmp` 1 before
   (T365) and 0 after.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. The `head` cut is a defect by its outcome: a pool tree removable by hand, and a parked stage
   movable into the phases unrefused, by any command longer than 120 characters.

**Found and left?**
- `tree::command_head` cut every walk target's `head` at 120 characters, so `builder_pool_hooks` and `parked::shell_hits` passed a
  long command they refuse at a short length: fixed here, pinned by the tree test above. observed 2026-11-27, method: `grep -rn
  "\.head\b\|\.segment\b"` over `rust/` for every reader of a target's cut text - `gm_tree_hooks`, `gate_write_hooks` and
  `make_only_hooks` read the program at its start, which no cut reached; `verdict.rs`, `gate_write_hooks` and `make_only_hooks`
  show or key by `segment`, unchanged; `readme_hooks` handles the cut on purpose (its `SEGMENT_KEPT`); `builder_pool_hooks` (the
  verb after `git -C <path>`) and `parked` (the last word) were the two that read past it.
- The helper-form leftovers already at `/tmp`'s top level are no longer swept by any `TempDir`: one, an empty directory
  (`l7r-guard-sweep-sweep-p2301309-0`), observed 2026-11-27, method: `ls -A /tmp` filtered to the helper's `l7r-<tag>-p<pid>-<seq>`
  form. Not a defect: nothing a reader sees and no finding broken, so not filed; T374's wider `/tmp` rule takes it if the GM rules for it.

**Performance work?** Yes (a `[perf]` task, 451 FR-013: the checks' and the builders' loop). Not an engine-speed task.

### T371 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** The one `read_dir` of the temp directory a process's first `TempDir::new` makes (T365, section 1).
2. **Removes work, or only moves it?** Removes it: the listing reads a small directory in place of `/tmp`'s 21.9 MB directory
   file, measured 2026-11-26 (T365, `ls -ld /tmp`).
3. **What do you expect it to save, and why?** By T365's estimate about 40 s a day at the leak pin (2,483 crate runs, one listing
   each) and at most 7 s at `make static`'s self-tests, 14 to 16 ms a listing down to about 0.1 ms, measured 2026-11-26 (T365's
   event-log count and timing loop, `t365-events-totals.txt`, `t365-loop-new.txt`).
4. **How does the work grow with the settlement?** n/a; the listing grows with the subdirectory's live entries, not with `/tmp`'s.
5. **What did the before and after show, and under what conditions?** BEFORE: `l7r-rust` listed `/tmp` once, 5,445 entries read, 21.6
   ms, measured 2026-11-26 (T365's shim over `make rust-test CRATE=rust/gate/crates/task`). AFTER: `l7r-rust` listed `/tmp` 0 times,
   and `/tmp/l7r-tmp` once, 3 entries read, 0.015 ms, with `/tmp` at 5,425 top-level entries and load 4.6 to 5.0, measured 2026-11-27
   (T365's `t365-shim.c` built to the scratchpad, two `FRESH=1` runs of the same crate, the shim watching `/tmp`, then `/tmp/l7r-tmp`).
   Counted listings of `/tmp` a crate run: 1 to 0, measured 2026-11-27 (the same two runs). Nothing was deleted outside a fixture.
6. **Did any map move, and does it still keep the research?** No map is drawn by this code.


### T533 Approach (checklist part A)

1. **The goal, in the world.** The coordinating session's scratchpad no longer holds the landed 451 tasks' scratch worlds that no landing ever took; nothing an open task or a live process uses goes.
2. **The constraints.** T533's line and T517's rule (whole numbers, `open_elsewhere`, live holds, worktrees); the session's ruling of 2026-11-27 (461 and 462 numbers, moved numbers, 451's open ones and unprefixed entries excluded; by hand from a computed list; no new sweep mode).
3. **Where each comes from.** G: the GM's order of 2026-11-27 putting 462's disk tasks first (request.md); R: 451 T517's section, `sweep/leftovers.rs`; O: the measurements above.
4. **Do they describe the world here?** Yes: the real scratchpad listed and sized, the session id read in the shell, the real starts file and task files read, measured 2026-11-27 (`du -sb`, `measure.py`). But the mirror's `tasks.md` of feature 461 was stale, measured 2026-11-27 (`grep` of its task lines against the clone's), the cause of the wrong removals above.
5. **The order.** After 451 T517 (landed); beside T550, which fixes the rule.
6. **The exits.** Green: the take measured before and after. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** 14.61 GB in 2,917 entries taken, 3.35 GB in 1,260 entries left, observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`.
10. **Before moving a constant.** n/a: no constant or knob.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; the host's disk has the taken bytes free (observed 2026-11-27, method: `du -sb` and `ls | wc -l` of the scratchpad and `measure.py`).

**Found and left?**
- The landed-scratchpad rule matches by number alone, so an open or moved task of another feature with no live start loses its scratch when 451's same number lands (observed 2026-11-27, method: the rule's matching re-run read only, `measure.py`: 247 entries of 0.46 GB of moved-to-462 numbers). Not fixed here: a rule change with its red-first test, outside a one-off take. Filed as T550; lands before T301.

**Performance work?** no


### T545 Approach (checklist part A)

1. **The goal, in the world.** A session that opens 451's plan-review.json meets its live entries (129,646 bytes, observed 2026-11-27, method: `ls -la` after the split), and a closed task's verdict is one part away through `index.json`; every tool reads what it read before.
2. **The constraints.** 462 FR-004 and SC-002; T545's line; T537's layout (`archive.rs`, the index, the note); the record's writers, merge driver and gate unchanged in format.
3. **Where each comes from.** G: the GM's words of 2026-11-27 (462 request.md); R: the round arbiter's accept, ask:451-T537-plan-review-json; O: the readers' census and the real split above.
4. **Do they describe the world here?** Yes: measured on 451's own record in this tree, 2026-11-27 (the split, then the join against the copy).
5. **The order.** After 462 T548 (the real split of plan-done.md and tasks-done.md); inside the same `make archive-split` run as T555, after its plan.md move, so the live blocks are the closed plan.md's.
6. **The exits.** Green: the new tests green, `make builder-checks` green over the six changed crates, the join equal. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The flat record 129,646 bytes (observed 2026-11-27, method: `ls -la` after the split), parts plus flat equal to the original, `built_inside` and `in_the_record` answering from a part (their tests).
10. **Before moving a constant.** n/a: `BOUND` is T537's, unmoved.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing a map shows. The rows merge: a carry from a pre-split tree would have brought back archived rounds, which the review-round guard counts.

**Found and left?**
- Fixed here: the rows merge kept a base row one side dropped (above), observed 2026-11-27, method: the new test over both orders of the two sides.

**Performance work?** yes: it bounds what a reader of 451's review record reads (5,074,158 to 129,646 bytes flat, observed 2026-11-27, method: `ls -la` after the split), which the GM tied to builders' context use; no engine-speed work.

<!-- plan-archive: archived 2026-11-28 -->
### T555 (observed 2026-11-27, method: `ls -la` of specs/451-time-retro-and-efficiency/ after 462 T548: report.md 1,496,878 bytes and plan.md 267,986 stood whole past the 64 KiB part the split keeps)

- **Approach**: `make archive-split` cuts the report too (`archive::report`, new), and first moves a CLOSED feature's finished plan.md sections to plan-done.md, so the fold takes them.
  - **Why plan.md held sections** (observed 2026-11-27, method: `make plan-archive F=451` on a copy, 0 moved, then each remaining section's heading and `l7r-gate plan decided` read): 19 tasks' sections stood, every task ticked. Two causes. (1) 18 of them carry `part B (2026-11-27T07:20Z ... 09:53Z)` blocks, appended by the red-gate tripwire's arbiter rulings to every task of that batch after the task's review and never reviewed, so the archive's test (`task_current` at plan.md, or `section_clear` of the whole section) found no current CLEAR and the archive moves only a CLEAR section (13 of them say so at `l7r-gate plan decided`; five pass it by its other route, `owed_for`). (2) T18's heading, `### T18 (FR-011: T="T1,T2" read as one task ...)`, named T1 and T2 as its example: the archive took every id a heading names (`TASK_ID`), and T1 and T2 are no ticked tasks, so the section never moved - a defect, fixed here: a heading's tasks are its leading ids (`plan_text::leading_tasks`), every named id only for a heading that opens with none (375's `### Wave 1 (T01)`). Measured: with the fix alone, `make plan-archive F=451` on a copy moved T18 and nothing else (observed 2026-11-27, method: a copy of HEAD's 451 directory in a fresh repository).
  - **The closed move** (decided here): where tasks.md holds no open box and a task is ticked, `make archive-split` - and it alone - moves every section whose tasks are all ticked, its verdict unasked (`task::archive(dir, when, closed)`): no review reads a closed feature's section again. The tick's archive keeps its CLEAR rule, so a feature's last tick never archives an unreviewed section.
  - **The report's cut** (decided here): `report.md` is cut at its `## ` sections; a section past `INLINE` (16 KiB, a GUESS knob: 451's ran 83 to 24,344 bytes but for its tables) moves to `report/NN-<slug>-K.md` parts, each at most `BOUND`, cut between table rows - every table of the section (451's critical path holds eight), a part opening with the section's heading and, inside a table, its header and separator; a task's rows (the first cell) stay together up to half of `BOUND`, longer runs (451's decision-log skeleton held runs of 120 KB) cut between rows. `report.md` becomes the index: its title, a marker line, a note opening "Load this file when:" with its WHY, the small sections inline and each moved one's heading with its parts, bytes and row range. `make feature-report WRITE=1` writes through the same `report::write`, split only where the feature has `archive/` (as T537's fold), so an unsplit feature's report is as before and the close's check (`closing.rs`, `report.md` stands) holds.
  - **The real split of 451** (observed 2026-11-27, method: `make archive-split F=451` in this tree, its outputs compared with copies taken before): plan.md 267,986 -> 28,573 bytes (19 sections moved, T18 T312 T313 T341 T364 T365 T369 T373 T403 T404 T406 T409 T413 T419 T420 T424 T425 T427 T428); `make plan-section F=451` of those 19 printed every line it printed before (0 missing), now from plan-done.md, where each task's earlier-archived sections print beside them (253,729 -> 314,480 bytes); report.md 1,496,878 -> 27,636 bytes and 29 parts, the largest 65,435 bytes, every table row of the original in a part.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the closed move and the heading-ids fix, the report's cut and its writer, the real split of 451 | n/a: tooling, no map drawn | n/a | none | n/a |

### T555 Approach (checklist part A)

1. **The goal, in the world.** 451's report.md and plan.md open at under 30 KB each, a reader sent to one part by an index, and no finished section left in a closed plan.md.
2. **The constraints.** 462 FR-004 and SC-002; T555's line; T537's layout and `BOUND`; the close's check that `report.md` stands.
3. **Where each comes from.** G: the GM's words of 2026-11-27 (462 request.md); O: the plan-archive run on a copy and the report's sections measured, 2026-11-27.
4. **Do they describe the world here?** Yes: measured 2026-11-27 (`make archive-split F=451` on 451's own files in this tree, the split above).
5. **The order.** After 462 T548; in one `make archive-split` run before T545's review cut.
6. **The exits.** Green: the new tests green (the heading test and the closed split red on the old code, 2 of 3 failing), `make builder-checks` green, the real split's figures above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** plan.md 28,573 and report.md 27,636 bytes, every report part at most 65,536, nothing lost (observed 2026-11-27, method: `ls -la` after the split and the joins above).
10. **Before moving a constant.** n/a: `INLINE` is new, a GUESS knob.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing a map shows. The heading-ids defect kept a finished section in plan.md, where `make plan-delta` and every plan reader read it (observed 2026-11-27, method: the 19 remaining sections' headings read against `TASK_ID` and `leading_tasks`, T18 the one instance).

**Found and left?**
- Fixed here: the archive's heading ids (cause 2 above), observed 2026-11-27, method: each of the 19 remaining sections' headings read against `TASK_ID` and `leading_tasks`; T18 the only heading naming ids it does not lead with.

**Performance work?** yes: it bounds what a reader of 451's report and plan reads (1,496,878 to 27,636 and 267,986 to 28,573 bytes, observed 2026-11-27, method: `ls -la` after the split); no engine-speed work.


<!-- plan-archive: archived 2026-11-28 -->
### T543 (make plan-delta read 451's plan-done.md eleven times a call and plan-review.json twice: 451 T536's read counter, dev/measurements/2026-11-27/t536-record-readers/results.md)

- **Approach**: every reader on `plan delta`'s path reads through one module, `rust/gate/crates/plan/src/plan/once.rs`: inside
  `once::held`, which the `plan delta` arm of `plan.rs` alone enters, a file is read from disk once and served from memory after, and
  the review record is parsed once (`once::record`); outside it each read goes to disk as before, so decide, tick and record, which
  write the records between their reads, see no change. Routed: `plan_delta`'s plan.md, `status::delta_keys` (plan.md, the record,
  plan-done, tasks.md, tasks-done) and the earlier-text check's plan-done (`status.rs`, the eleven-fold read: one a changed block),
  `lint.rs` (`tasks_without_approach`, `findings`' request.md), `lint/deferral.rs` (`boxes`), `lint/task_line.rs`, and `bundle.rs`'s
  `read`, `plans_of` and `review_of` (its `cited` and `section` children read through `bundle::read`). The archive's own reader
  (`l7r_shared::speckit::archive::text`, T545's tree) is untouched: `once` hands it a caching reader closure.
  FOUND MEASURING, and the wall time's larger part (observed 2026-11-28, method: the read shim and spawn logger on the copy): each `History::block` looked the clone's common git directory up again,
  `git rev-parse --path-format=absolute --git-common-dir`, 413 processes in one `plan delta 451`; a History now looks it up once
  (`history.rs`, `git_dir`). Measured 2026-11-28 on a `git clone --shared` copy of this tree (451 split under `archive/`, 461 flat;
  method: T536's `LD_PRELOAD` read shim, an `LD_PRELOAD` `posix_spawn` logger, 7 interleaved runs a side, load average 11 to 23):

| `plan delta` | plan-done | plan-review.json | plan.md | tasks-done | index.json | processes | wall median | label |
|---|---|---|---|---|---|---|---|---|
| 451 before | 40,579,308 (11x) | 10,148,316 (2x) | 1,339,930 (5x) | 1,823,772 (3x) | 801,879 (13x) | 422 | 2,644 ms | observed 2026-11-28, method: the read shim and spawn logger on the copy |
| 451 after | 3,689,028 (1x) | 5,074,158 (1x) | 267,986 (1x) | 1,823,772 (3x) | 123,366 (2x) | 11 | 1,802 ms | observed 2026-11-28, method: the read shim and spawn logger on the copy |
| 461 before | 2,248,496 (8x) | 853,370 (2x) | 705,585 (5x) | 284,060 (5x) | - | 24 | 1,263 ms | observed 2026-11-28, method: the read shim and spawn logger on the copy |
| 461 after | 281,062 (1x) | 426,685 (1x) | 141,117 (1x) | 170,436 (3x) | - | 11 | 1,207 ms | observed 2026-11-28, method: the read shim and spawn logger on the copy |

  Through `once` every file is now read once (the trace of its disk reads, one line a path); the repeats left (observed 2026-11-28, method: the read shim and spawn logger on the copy) are the spec lint's
  beside it (`rust/gate/src/lib.rs` `linted_plan`, the checks crate: tasks-done and tasks.md twice more, 451's spec.md 16 times) -
  outside this crate, filed as T560 with the claims hint's 0.6 s. Unchanged (observed 2026-11-28, method: the read shim and spawn logger on the copy), checked on the same copy: stdout, exit code and every
  file of the bundle (`diff -r`, 8 files) for 451 and 461, the "no block owed" reply of 449 and 450, the no-directory refusal, and a
  lint refusal (a made-up GM quote added to 461's plan.md).
  RED FIRST: `once/tests.rs` `plan_delta_reads_each_file_once_flat_and_split` with the readers routed and nothing held failed with
  tasks.md 7, request.md 6, tasks-done.md 6, plan.md 5, plan-done.md 3, archive/index.json 3, plan-review.json 2 reads (flat case);
  held, 1 each, flat and split. `history/tests.rs` `a_history_looks_its_git_directory_up_once`: 6 lookups for five blocks before, 1 after.

### T543 Approach (checklist part A)

1. **The goal, in the world.** `make plan-delta` reads each record once a call and starts no process a block, so a builder's plan
   review is dispatched sooner (9.2 s median over 142 real calls, observed 2026-11-27, method: the event logs' PostToolUse ms, T536).
2. **The constraints.** 462 FR-004 (the record readers); every block, verdict and bundle the command writes stays the same; T545 owns
   the archive code and plan-review.json's split, so the shared archive reader is not edited.
3. **Where each comes from.** O: T536's measurement; O: this task's copy runs (the table above); G: the brief's "every block, verdict
   and bundle it writes must stay the same".
4. **Do they describe the world here?** measured 2026-11-28 (the read shim on a copy) on today's tree (451 split by T548) and on 461's current plan, the live feature.
5. **The order.** After 462 T548 (the split it measures on); before or beside T545 (plan-review.json's split: its reader of the record
   in this crate becomes `once::record`'s one line).
6. **The exits.** Green: the two red-first tests pass and the shim shows one read of each record through the plan crate. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** The table above (observed 2026-11-28, method: the read shim and spawn logger on the copy): 451 2,644 -> 1,802 ms, plan-done 11x -> 1x, plan-review.json 2x -> 1x, 422 -> 11 processes.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a
12. **Before any fix.** nothing a reader sees differently: the bundle and reply are byte for byte the same; the command is faster.

**Found and left?**
- The 413 `git rev-parse` processes of a `plan delta 451` call, observed 2026-11-28, method: the spawn logger over one call, every
  process listed (about 0.8 s of its 2.6 s, the wall medians before and after): fixed here (`history.rs`).
- The claims hint (`triage_hint` -> `claims triage-owed`, 0.6 s a call, observed 2026-11-28, method: the command timed alone, n=3) and the spec lint's repeated reads beside plan-delta (451's
  spec.md 16 times, tasks-done three): Not fixed here: outside the plan crate (the claims and checks crates), not plan-delta's own
  read path. Filed as T560; lands before T547 (decide's repeats, whose call runs the same lint and hint).

**Performance work?** yes - a `[perf]` task (451 FR-013): it makes the gate's `make plan-delta` faster; not an engine-speed task.


<!-- plan-archive: archived 2026-11-28 -->
### T550 (T533's one-off take: the landed-scratchpad rule matches a `t<N>` entry by number alone and protects only another feature's open START, observed 2026-11-27, method: the rule's matching re-run read only over the session scratchpad, 462 T533's `measure.py`)

- **Approach**: `sweep/leftovers.rs`'s `open_elsewhere` now holds a number while ANY other feature has an OPEN box of it (`- [ ] T50`, an older feature's `- [ ] **T007**`, at any indent; `open_box`) in its `tasks.md` or `tasks-done.md`, started or not, read from `specs/` beside the git directory holding `task-starts.jsonl` - `make land` passes the landing clone's `git rev-parse --git-common-dir`, so the clone that lands, never the `/diagram` mirror (T533's cause: the mirror's 461 `tasks.md` lacked T50-T69). A start of another feature whose `tasks.md` cannot be read still holds its number (T517's conservative branch, kept); a start whose task is open is now held by its box. A feature is matched by its leading number, so `F=462` and `462-efficiency-backlog` are one. Name, signature, `why` strings and callers unchanged (`sweep.rs`'s doc line restated).
- **Which, and why - by number, open boxes only**: an entry's contents and owner do not name its feature: a builder's scratch is named `t<N>-` (451 T271) with no feature and every entry has the one uid. The pool log's take/release windows DO attribute some: the scratchpad's `t22-*` (00:11-00:25Z on 11-28, `ls` shows the container's EST) fall inside 461 T22's window (00:02-00:26Z), observed 2026-11-27, method: `stat` of the scratchpad's entries against `grep` of `.git/builder-pool.log` (the T550 plan review's note caught the zone). But not all: the coordinating session's own `t<N>-` scratch falls in no window, nor does any entry from before the pool's log began (2026-11-26), an mtime is a last write and not a creation, and two features' same number can run at once. So keying by window is a second mechanism over the log, with its own misattribution to price, not this fix: by number here, the window lever filed as T553. The brief's "open or ticked" was priced and not taken: over the clone's specs (28 features with an open box), holding ticked boxes too would hold all 70 of 461's numbers and 94 of 462's 113, the take all but gone (T517's growth back), while open boxes only hold 184 of 451's 537, 56 of 461's 70 and 14 of 462's 113, observed 2026-11-27, method: `scratchpad/t550-measure2.py` over `specs/*/tasks*.md` (5,975 of 7,287 box lines carry a plain id; the bold-id form of features before 130 parsed too; the rest are id-less boxes such as `GM review`). A ticked box needs no hold: its own landing took its scratch since T517. Each case the brief names is covered: an unstarted open task of another feature is held by its box; a `Withdrawn: moved to 462` line is ticked and holds nothing itself, but the moved task keeps its id open in 462 (462 tasks.md's preamble), so it is held at every other feature's landing and taken at 462's own; a builder's `t<N>-` scratch of another feature is held while that task is open. Chosen by the T550 builder; cost: a landed number another feature holds open keeps its scratch until that box closes or the session ends.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| another feature's open box holds its number, started or not, an old bold id too; a ticked box or a moved-to-us line does not; by number or full name | red first: `every_open_number_of_another_feature_holds_whether_started_or_not` (`sweep/leftovers/tests.rs`; 1 failed, 5 passed on the old code: `left: [] right: [7, 22, 50]`) | n/a: tooling | none | n/a |
| T517's rows kept: a start open elsewhere held, ticked not, an unstarted start with no open box (its fixture's T172) not, unreadable held | `another_feature_s_start_holds_the_number_while_its_task_is_open_whatever_its_age` unchanged and green; `disk/tests.rs`'s landing test green | n/a: tooling | none | n/a |

### T550 Approach (checklist part A)

1. **The goal, in the world.** A landing takes its own tasks' scratch in the session's scratchpad and never another feature's work in flight, whether that task was started, never started or moved under the same number.
2. **The constraints.** T550's line (key to the feature or exclude another feature's open and moved numbers, started or not; read the landing clone, never the mirror); T517's rule (whole numbers, live holds, worktrees, the unreadable branch); T533's lesson.
3. **Where each comes from.** R: T517's and T533's sections, 462 `tasks.md`'s preamble (moved boxes keep their 451 ids); O: the measurements above.
4. **Do they describe the world here?** Yes: the clone's real specs counted (`t550-measure2.py`), the Makefile's `--scratch-sweep landed` call read (the clone's `--git-common-dir`), the pool log and scratchpad read, 2026-11-27.
5. **The order.** After T517 and T533 (landed); before T301 (it edits `sweep/tmp.rs`; no overlap); T553 after it.
6. **The exits.** Green: the red-first test green, `make builder-checks CRATE=rust/guard` (637 passed) and `tests/hooks/test-disk-floor.sh` (16 passed). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The take's held numbers on the clone's specs: 451 184 of 537, 461 56 of 70, 462 14 of 113, observed 2026-11-27, method: `scratchpad/t550-measure2.py`.
10. **Before moving a constant.** n/a: no constant or knob.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; another feature's open work is no longer deleted at a landing of the same number.

**Found and left?**
- A scratch entry carries no feature, so an entry whose number another feature holds open is kept past its own landing (461: 56 of 70 numbers), observed 2026-11-27, method: `scratchpad/t550-measure2.py`. Not fixed here: naming scratch by feature changes `make builder-brief`'s block and every builder's habit, a mechanism of its own. Filed as T553; lands before T301 (no dependency either way).

**Performance work?** no


<!-- plan-archive: archived 2026-11-28 -->
### T562 (the GM's host freezes and IO pressure stood high at 2026-11-28T04:38Z with four pool trees and the lane busy, as T562's line records: measure who writes and price the levers)

- **Approach**: a MEASUREMENT; no source file changes. The record is `dev/measurements/2026-11-28/t562-io-contention/results.md`,
  its window 04:44:28Z-05:09:37Z at load about 30, measured 2026-11-28 (uptime at the window's start). Its method: per-process
  `/proc/<pid>/io` every 0.5 s, D-state wait channels every 0.2 s, the jbd2, diskstats and cgroup series every 5 s and a
  `find -newermt` census, measured 2026-11-28 (`t562-sampler.py`, `t562-dstate.py`). The levers were A/B'd ABAB on a `git archive`
  copy or this builder's own tree.
  - The disk wrote 32.1 GB and read 30.8 GB in 25 minutes, 97% of the reads page-cache refaults under the 10 GiB cap, measured 2026-11-28 (diskstats, cgroup memory.stat deltas).
  - rustc writes at least 51% of the bytes and `incremental/` holds 78% of the bytes still present, measured 2026-11-28 (`t562-leaves.py`, `census-summary.txt`).
  - All 1,951 journal commits were forced, none by the timer, and the journal's moving-average commit time reached 1,975 ms, measured 2026-11-28 (jbd2 info deltas).
  - Journal waits are 45% of the IO-wait time and git in the tests' fixture TMPDIRs 67% of it while writing 0.06 GB, measured 2026-11-28 (`t562-dstate.py` by wait channel and cwd).
  - Who requests most forced commits is not measured, measured 2026-11-28 (no tracefs, ptrace refused): the fixtures are one source (a 40-fixture loop forced 26-32 commits by default against 2-3 with `core.fsync=none`, measured 2026-11-28 (`t562-git-fsync-ab.sh`)), and the commit rate barely followed them (6.4 against 10.1 a 5 s slice without and with fixture git sampled, measured 2026-11-28 (`samples.json`)).
  - Lever A, git `core.fsync=none` for the tests: the shared suite's tests 9.3 s to 4.2 s mean at load 23-25, measured 2026-11-28 (`t562-suite-ab.sh`, two rounds, noisy), no change below load 14, measured 2026-11-28 (the same) - filed as T563 for a trial at load.
  - Lever B, a tmpfs for the tests' TMPDIRs (peak 17.6 MB live, measured 2026-11-28 (`t562-tmpdu.sh`)), and lever G, a larger memory cap: host-level, for the GM.
  - Lever C, the GM's question, a tmpfs for cargo's small files: 0.14 GB live across every target, measured 2026-11-28 (`du`), so it fits, and those files took 3.7 MB and 2,256 of the 20,042 files written in the window, measured 2026-11-28 (`census-summary.txt`); a cold 96 s cargo build of the phases and guard crates, which writes those files, forced 0.42 commits a second against 0.57 in the minute before and after it, measured 2026-11-28 (`t562-cargo-commits.sh`, `cargo-commits2.tsv`), so moving them would remove no forced commit; its time saved is unmeasured (a mount, which the brief leaves to the GM) and expected small: listed for the GM beside B and G as his question's answer, not recommended.
  - Lever D, a tmpfs for incremental: 118 GB live, measured 2026-11-28 (`du`), so it does not fit: rejected.
  - Lever E, `CARGO_INCREMENTAL=0` for coverage: 0.2 GB less a cold build and 13-22 s more a warm rebuild, measured 2026-11-28 (`t562-incr-ab.sh`): rejected.
  - Lever F, batched appends: under 0.5% of the bytes, measured 2026-11-28 (`census-summary.txt`): rejected.
  - **The attribution's limit**, observed 2026-11-28, method: a shell's `/proc/self/io` before and after a 20 MiB `dd` child:
    the counters include reaped children, so the per-kind figures are LEAVES (processes with no child seen), a lower bound -
    16.4 of the cgroup's 29.6 GB written; the bytes by path come from the file census instead.
  - **What could not be measured here**: the fsync callers by name (no tracefs, `perf_event_paranoid` 4, ptrace refused) and
    per-process IO delay (`task_delayacct` off): the record gives the GM the host-side `perf trace` and `bpftrace` commands.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the five things measured and written up; levers A/B'd on scratch copies and this builder's own tree | n/a: a measurement, no source changed | n/a: tooling | none | n/a |

### T562 Approach (checklist part A)

1. **The goal, in the world.** The session and the GM know who writes to the disk, what the IO stall costs the builders, and which lever buys back the most time, with the host-level ones named for the GM.
2. **The constraints.** T562's line; the brief's limits (no source change, no mount, sysctl or anything outside the repository, no lever measured on the clone's or the lane's live caches, at most 4 copies at once); the GM's measure of 2026-11-28, *"if looking into it speeds up your overnight work then it might be helpful"* (request.md), time saved, and his question of the same day on a tmpfs for cargo's much-written files (request.md, 2026-11-28).
3. **Where each comes from.** G: the GM's two messages of 2026-11-28, relayed in the brief. R: `rust/guard/shared/src/tempdir.rs` (the tests' TMPDIR root honors `TMPDIR`), `rust/Cargo.toml`'s profiles, `scripts/gates/l7r-gate.sh`, T520's record. O: the window's samples and the A/Bs above.
4. **Do they describe the world here?** Yes: the window was 25 minutes of the real overnight work at load about 30, read from `/proc` and the cgroup, measured 2026-11-28 (`t562-sampler.py`, uptime). The A/Bs ran real gate commands on a `git archive` copy of HEAD or this tree.
5. **The order.** After T520 (the cache's working set). Before T563, whose trial sits on lever A's figures.
6. **The exits.** Green: the record with the five things and every lever priced. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Three probes were redone. The first attribution subtracted a reaped child's window share where its parent takes the child's whole lifetime, putting 26 GB on claude, measured 2026-11-28 (`t562-analyze.py`), and the leaves are the fix. The first coverage A/B's "cold" removed `cover-*` under a `CARGO_TARGET_DIR` override that the cover build uses directly, so its cold row is the prime run. The lever A/Bs after the window ran at load 6-29, measured 2026-11-28 (each `.tsv` row's load column), mostly below the window's IO pressure, so lever A's wall figures are a signal for T563's trial, not its price.
8. **The budget.** One landing.
9. **Done, measured.** `results.md`'s tables answer (1)-(5), observed 2026-11-28, method: the scripts named beside each.
10. **Before moving a constant.** n/a: no constant moved.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; no defect is fixed in a measurement. The lever found is filed below.

**Found and left?**
- The tests' fixture git repos run with git's default fsync, which can force journal commits every writer on the partition waits on (a 40-fixture loop forced 26-32 commits by default against 2-3 with `core.fsync=none`), and git in `/tmp/l7r-tmp` is 67% of the container's IO-wait time, observed 2026-11-28, method: `t562-dstate.py`'s wait channels by cwd and `t562-git-fsync-ab.sh`; whether the fixtures are the main requester of the forced commits is not measured (no tracing); not a defect (constitution XIV): slower tests, no wrong outcome - a speed lever, filed as T563 for its trial at load.

**Performance work?** yes, a `[perf]` measurement (451 FR-013): it measures where the builders' time goes to IO and prices the levers. It is no engine-speed task, so the checklist below is answered for the record only.

### T562 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** IO waits: journal waits 45%, page or buffer waits 39%, a full device queue 13% of the D-state time, measured 2026-11-28 (`t562-dstate.py`), and the test phases ran at the highest IO pressure (`builder-checks test` 34.3%, `land suite` 30.7% mean), measured 2026-11-28 (`phases.txt`).
2. **Removes work, or only moves it?** Lever A removes work (fsyncs nobody needs on throwaway repos); the tmpfs levers move it, and only lever B's fits.
3. **What do you expect it to save, and why?** Lever A: up to about 12 phase-minutes per 25-minute busy window if fixture-heavy suites halve under pressure as shared did, measured 2026-11-28 (`phases.txt`: the test phases' 1,442 s - land suite 1,077, builder-checks test 210, hooks-test 155 - halved), an upper bound that T563's trial prices.
4. **How does the work grow with the settlement?** n/a: not engine work.
5. **What did the before and after show, and under what conditions?** `suite-ab.tsv`, `git-fsync-ab.tsv`, `incr-ab*.tsv`, each row with its load.
6. **Did any map move, and does it still keep the research?** n/a: no source changed.


<!-- plan-archive: archived 2026-11-28 -->
### T146 (the guard launcher's tool-profile build and `make rust-test`'s dev-profile test builds failed their links on stale incremental units, `rust-lld: undefined hidden symbol` - l7r_shared's units under l7r-rust twice on 2026-11-22, l7r_gate_archive's lib test on 2026-11-19 - with no heal reaching either; filed from 451 beside T142's launcher heal)

- **Approach**: no new code: both halves were built after this task was filed, and this section records what heals each and why the two are not one code.
  - **`make rust-test`'s test builds: healed by `stale.rs` (451 T336, landed 2026-11-26).** Every test build `rust-test` asks reaches `stale::built`: the binary key's build (`kept.rs`'s `binary_key`, `--message-format=json`, its link error in its JSON) leaves `verdict.built` false when it fails, so `answer`'s loop asks `stepped`, whose `--no-run` build is `stale::built` with `phase::JSON` (`json-render-diagnostics`: rustc's diagnostics rendered on stderr, where `healed` reads them), for `test` and `test-counters` alike; observed 2026-11-27, method: read `rustc.rs` `answer` and `stepped`, `kept.rs` `binary_key` and its caller, `phase.rs` `JSON`. Cost: a mixed session's first red build is asked once more before the heal (the binary key's, then `stepped`'s), one failing link of seconds.
  - **The guard launcher's build: healed by `scripts/hooks/l7r-guard.sh` itself (451 T449, landed 2026-11-27).** On a link failure it drops tool/deps, tool/.fingerprint and tool/incremental of `l7r_guard` and `l7r_shared` - every path crate the guard builds on (`rust/guard/Cargo.toml` names `l7r_shared` alone) - under cargo's lock, rebuilds once inside its ceiling, and says so; once a source change (`guard.healed`). Its drop is wider than `stale.rs`'s (the rlibs too) on T449's own measurement: a bad rlib with a fresh fingerprint, healed only once deps and fingerprints were set aside.
  - **Why not one healing code** (the brief: "one healing code, reached from each - or say why one cannot"). The heal in Rust is `stale::healed_under`, reached from both builds the gate's tool runs (this task and T206). The launchers cannot reach it: `l7r-guard.sh` and `l7r-gate.sh` (451 T142) each build the binary that would hold it, in the tool profile whose `l7r_shared` is what fails to link, so the healer would be broken by what it heals; and the guard's hooks must not wait on the gate's tool, which the launcher would have to build first (`check guard-deps` keeps the two apart). A guard-binary subcommand on the last good binary was priced: a new command and a guard edit, a builder of its own, for a rule each launcher already holds - not taken, not filed: no wrong outcome is left (constitution XIV).
  - **The record**: `stale.rs`'s header (it said the guard's launcher and the coverage build "do not yet"; now it names the one heal, the builds reaching it and why the launchers heal apart).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a red test build of `make rust-test` on `undefined hidden symbol` drops the named crates' sessions and fingerprints and builds once more | pinned by `a_link_on_a_mixed_session_drops_the_named_crates_sessions_and_builds_once_more` (451 T336) | n/a: tooling | none | n/a |
| the guard launcher's link failure drops the state of `l7r_guard` and `l7r_shared`, rebuilds once, and is stamped failed only when the rebuild fails too | pinned by `tests/hooks/test-l7r-guard.sh` case 6f (451 T449) | n/a: tooling | none | n/a |

### T146 Approach (checklist part A)

1. **The goal, in the world.** No test build of `make rust-test` and no build of the guard by its launcher stays red on a stale incremental unit its code did not cause: each heals once and says so.
2. **The constraints.** T146's line in tasks.md; the brief: one healing code reached from each, or why one cannot; red first on a stub cargo; the first tier only.
3. **Where each comes from.** O: the failures of 2026-11-19 and 2026-11-22 the line names; T336's measurement (`dev/measurements/2026-11-26/prewarm-link/`) and T449's (its comment in `l7r-guard.sh`).
4. **Do they describe the world here?** Yes: both heals are in this tree's HEAD and their tests pass (item 9).
5. **The order.** After 451 T336 and T449, which built it; beside T206, which reaches the same heal from the coverage build.
6. **The exits.** Green: `make builder-checks CRATE="rust/gate/crates/rustc"` and `tests/hooks/test-l7r-guard.sh`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing (with T206).
9. **Done, measured.** RED FIRST, measured 2026-11-27 (method: `stale::built`'s heal replaced by the first build's answer, `make rust-test CRATE=rust/gate/crates/rustc ONLY="rustc::tests::stale"`): 1 passed, 2 failed - one build asked against two, and exit 101 against 0; restored, 3 passed. The guard launcher: `bash tests/hooks/test-l7r-guard.sh` 119 passed, 0 failed, measured 2026-11-27 (its case 6f the forced link failure on a stub cargo: two builds, the two crates' state dropped and the rest kept, a second failure stamped failed after no third build).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Not a defect of a map. The wrong outcome: a build red on right code until directories were removed by hand; fixed by 451 T336 and T449, none left.

**Found and left?** none.

**Performance work?** yes: it keeps the checks and the builders' loop from stopping on a stale link (451 FR-013); not an engine-speed task, so `docs/performance-checklist.md` does not apply.


<!-- plan-archive: archived 2026-11-28 -->
### T206 (the coverage build's link failed on stale `l7r_shared` incremental units, `rust-lld: undefined hidden symbol`, and no retry reached it: observed 2026-11-23, `make crate-checks` on `rust/guard/shared`, healed only by deleting the `l7r_shared-*` directories under the family's `cover-guard/target/debug/incremental` by hand)

- **Approach**: the coverage build reaches the test build's heal (`stale.rs`, 451 T336), one code.
  - **`stale.rs`**: `healed` becomes a wrapper over `healed_under(world, target, manifests, ...)`, which reads the linker's units under the target directory it is given (the coverage build's is its family's own, `cover_dir/target`, not the tree's) and writes its `link-heal` `Phase` line over every crate the build was asked for. `SIGN` is shared with `cover.rs`. The rule, the wording and `LOCK_S` are unchanged.
  - **`cover.rs`'s `build`**: where the family's group build fails with `undefined hidden symbol`, `healed_under` is asked over the build's `CARGO_TARGET_DIR`, its second build the same cargo call with the same arguments and environment, under the build slot already held and inside the `cover-build` line's span (that line carries the healed build's code and count); a heal that linked is said on stderr, as `stale::built` says it. ONCE A FAMILY: where the healed build fails too, the crate-by-crate builds that follow are told not to heal, so cargo writing the crate's sessions anew in them cannot start a heal a crate (pinned: item 9).
  - **The record**: the `rustc` row of `rust/gate/CLAUDE.md`, the headers of `stale.rs` and `cover.rs`'s `build`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a coverage group build red on `undefined hidden symbol` drops the named sessions and fingerprints in the family's directory and builds once more, a `link-heal` line written | pinned by `a_coverage_build_s_link_on_a_mixed_session_is_healed_once` | n/a: tooling | none | n/a |
| a healed coverage build that fails again heals nothing more in its crate-by-crate builds | pinned by the same test (its builds and `link-heal` lines counted, item 9) | n/a: tooling | none | n/a |

### T206 Approach (checklist part A)

1. **The goal, in the world.** `make crate-checks` and the gate's coverage step never stay red on a stale incremental unit: the coverage build heals once, as the test build does, and says so.
2. **The constraints.** T206's line in tasks.md; the brief: the one heal of `stale.rs`, reached from the cover build; red first on a stub cargo; the first tier only.
3. **Where each comes from.** O: the failure of 2026-11-23 the line names; T336's measurement of the heal's scope (`dev/measurements/2026-11-26/prewarm-link/`).
4. **Do they describe the world here?** Yes: the coverage build's directory is `cover-<family>/target` under the tree's target (`cover_dir`), the one the 2026-11-23 failure named, and its diagnostics are rendered on stderr (`json-render-diagnostics`), where `healed_under` reads them.
5. **The order.** After 451 T336; beside T146.
6. **The exits.** Green: `make builder-checks CRATE="rust/gate/crates/rustc"`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing (with T146).
9. **Done, measured.** RED FIRST, measured 2026-11-27 (method: the new test on HEAD's `cover.rs`, `make rust-test CRATE=rust/gate/crates/rustc ONLY="rustc::tests::cover"`): 2 passed, 1 failed - 4 builds asked (the group and three crates, no heal) against 2; with the heal, 3 passed; with the once-a-family guard removed, 1 failed, 8 builds against 5. NOT run live: the heal on a really broken coverage cache (as 451 T362 for the test build).
10. **Before moving a constant.** n/a: `LOCK_S` reused as it stands.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Not a defect of a map. The wrong outcome fixed: a coverage step red on right code until directories were removed by hand.

**Found and left?** none.

**Performance work?** yes: it keeps the checks from stopping on a stale link (451 FR-013); not an engine-speed task, so `docs/performance-checklist.md` does not apply.


<!-- plan-archive: archived 2026-11-28 -->
### T107 (the bundle crate's `the_rare_paths_of_a_depiction_bundle` returned -1 where 0 was expected under load near 30, 2026-11-21 at 451 T102's landing; its -1 is the tests' 150 ms crop bound outlasted by the fake crop's `sh` start, measured 2026-11-27 (the bundle binary 30 at once))

- **Approach**: the defect is the TESTS' crop bound, not the bundle: `rust/gate/crates/bundle/src/record/bundle/depiction.rs`'s
  `#[cfg(test)] CROP_TIMEOUT` goes from 150 ms to 30 s (a GUESS knob with its measured why beside it), a ceiling no green run waits
  out - the fake crop of a page that is not slow ends in milliseconds and the 1 ms poll ends the wait at once - while the `slow`
  page keeps its own 20 ms (`crop_timeout`), so the timeout test's time is unchanged. The production `CROP_TIMEOUT` (180 s, observed 2026-11-27, method: read
  `depiction.rs`) and `glyph_crop` are untouched. `depiction/tests.rs`: each success assertion says `run.err` (on the assertion's own line), so a
  future -1 names its cause where this one was thrown away (`let (code, _)`).
- **Measured** (method for each figure: the bundle crate's test binary run whole, 30 or 20 at once, under `uptime`'s load on 22
  cores, its failures' messages counted, 2026-11-27):
  - What -1 is: `subprocess.TimeoutExpired: the crop of well timed out after 180 seconds` (the message names the production
    bound; the test's is 150 ms) - 17 red of 90 at load 18-333, 18 failures, all three crop tests (the rare paths 5, the crop 5,
    the cannot-crop 8), measured 2026-11-27 (the bundle binary 30x3). Not a signal and not the browser: the tests' crop is a `sh`
    script, never `l7r-browser`.
  - After: 0 red of 80 at load 437-469, measured 2026-11-27 (the bundle binary 20x4). At 30 at once a third round hit the
    container's `pids.max` (2048): `failed to spawn thread`, EAGAIN, across the crate's tests, one in the rare-paths test, at load
    259-606, measured 2026-11-27 (the bundle binary 30x3, its second run) - the machine's limit under the measurement's own load,
    no test's defect.
- **Decision 1 - fix the tests' bound, not the bundle.** No production crop failed: the -1 came from the test-only 150 ms bound (observed 2026-11-27, method: read `depiction.rs`),
  which the history beside it set at "many times a start under load" twice (449 T108, T160) and load outran both times. A bound
  that only a hung crop reaches stops that race for good; the slow page keeps its own 20 ms (observed 2026-11-27, method: read `depiction.rs`), so FR-008's tenth
  of a second is not spent. So the rare paths are pinned with no load sensitivity the task line names: a crop that ends at all passes, however slow its start, and only one that never ends meets the ceiling, measured 2026-11-27 (the slowed fake crop and the 20x4 run). Label: the algorithmically easier route, the record silent (tooling, no research question).
- **Decision 2 - fixed here, the merge-base test's stale-page case.** The same load run turned up
  `the_candidates_at_the_merge_base_and_the_geometry` red 1 of 90 at load 12-340 (the first run after the bound's fix): it writes `g.svg` a statement after `g.html` and
  expects "not stale" from `stale_page`'s one-second tolerance, which a slow second statement crossed. The drawing's time is now
  set to the page's plus one second (the tolerance's edge), not left to the clock.
- Red first, measured 2026-11-27 (make rust-test, ONLY the depiction module): the fake crop slowed 0.3 s for every page that is not
  `slow` or `nocrop` (a scratch edit, removed after) against the old 150 ms bound, 8 passed and 2 failed with
  `subprocess.TimeoutExpired` (`the_rare_paths_of_a_depiction_bundle` and `a_depiction_bundle_with_its_crop`), and against 30 s 10 of 10 passed, measured 2026-11-27 (make rust-test).

### T107 Approach (checklist part A)

1. **The goal, in the world.** The depiction bundle's tests are green at any load, and the crop's timeout is still proved by the
   slow page's own test.
2. **The constraints.** 449 T167's 20 ms slow-page bound, FR-008's tenth of a second a test and the production `CROP_TIMEOUT`
   (180 s), observed 2026-11-27, method: read `depiction.rs` and its history comments, with the crate's own-tests coverage and an
   assertion's message on its own line (451 T343).
3. **Where each comes from.** R: tasks.md T107, the history comments beside `CROP_TIMEOUT` (449 T108, T160, T167). O: the load
   runs above (2026-11-27).
4. **Do they describe the world here?** Yes: the runs used the crate's own test binary, whole, 20 or 30 at once on the shared
   machine at the loads named, and the cause was read from the failures' own messages, measured 2026-11-27 (the bundle binary 30x3
   and 20x4).
5. **The order.** Any; it touches only the bundle crate's depiction module.
6. **The exits.** Green: the 20x4 run at load clean. Red: what failed recorded and the task set down, a claim that it cannot be
   done ruled through `make arbiter-ask`.
7. **The search smell.** None: one test constant and one fixture's time.
8. **The budget.** One landing.
9. **Done, measured.** 17 of 90 red before at load 18-333, 0 of 80 after at load 437-469, measured 2026-11-27 (the bundle binary
   30x3 and 20x4).
10. **Before moving a constant.** The test-only `CROP_TIMEOUT` was no claim's; now 30 s, a GUESS with its measured why. The
    production 180 s unmoved (observed 2026-11-27, method: `git diff`).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes: a red batch gate's false red from these tests is gone; the bundle behaves as before.

**Found and left?**

- `the_candidates_at_the_merge_base_and_the_geometry`'s stale-page case read the clock (Decision 2): fixed here.
- The container's `pids.max` of 2048 failed thread spawns at 30 test binaries at once and load 606, measured 2026-11-27 (the
  bundle binary 30x3, `/sys/fs/cgroup/pids.max`): not a defect - the measurement's own load, no test's wrong outcome.

**Performance work?** no

<!-- plan-archive: archived 2026-11-28 -->
### T173 (tests/hooks/test-finished-run-hooks.sh section 6's five refusal cases failed twice chained after the rust/guard crate builds at load ~15, 2026-11-23 (451 T171's finisher), the cause the fixture's 12 s life, which one slow Stop call outlasts, measured 2026-11-27 (the suite with its first Stop slowed))

- **Approach**: the defect is the SUITE's fixture, not the guard: every live run the suite starts was `make sleeper`, `sleep 12`,
  so all the checks of a section had to finish inside 12 s of its start (observed 2026-11-27, method: read the suite).
  `tests/hooks/test-finished-run-hooks.sh` alone changes: the fixture sleeps `RUN_S` (600 s, a GUESS knob beside its measured why),
  a ceiling no green run waits out since every section ends its runs itself, in section 6, 6b (the sleeper and 6d's `p2`, while
  `p1`'s 3 s, the transition 6d waits for, is kept, observed 2026-11-27, method: read the suite), 6e's nested and sibling clones,
  and so in 6c, 6g, 6f, 9, 10 and 11, which run the same Makefile. `endruns <clone>` (new) ends a clone's live makes and their
  direct children (`pkill -P`, then `kill`) where each section killed only the make, which left its `sleep` to run out; `endone`
  does it for 6f's one run, and the EXIT trap runs `endruns` over the three fixture clones, so a red run leaves no `RUN_S` sleeper
  behind.
- **Measured**:
  - THE CAUSE: the first Stop call on the live clone slowed 13 s (a scratch wrapper hook sleeping once before the real one, a
    marker directory saying it had) - on HEAD's text 79 passed and 5 failed, exactly section 6's five refusal cases ("stop refuses
    a turn that would close over a live run", "...and says so", "...and what to do about it", "a token in a command cannot escape
    a Stop hook", "the refusal is recorded with its own rule"), the run gone before they asked and nothing else red, measured
    2026-11-27 (the first-Stop-slowed suite on HEAD's text). The line's shape: the five together, and green alone.
  - What can slow a call that much: a stale guard binary (a guard source touched) makes the suite's first call rebuild it, and
    the wrapper waits up to 45 s (`L7R_GUARD_BUILD_SECS`) on that build, observed 2026-11-27, method: read
    `scripts/hooks/l7r-guard.sh`. It did NOT reproduce the line's failure here: one stale-binary run put its 15.2 s rebuild in
    section 1's first call and left section 6 green, measured 2026-11-27 (each call timed by a scratch wrapper, load 189). The
    2026-11-23 runs' logs are gone, so which call waited then is not measured, and the fix does not depend on it: any one Stop
    call past the fixture's 12 s fails the five, measured 2026-11-27 (the first-Stop-slowed suite on HEAD's text).
  - Unslowed under load: 20 of 20 green at load 52-71, measured 2026-11-27 (the suite 10 at once, 2 rounds) - a wait of 12 s is
    rare, as the line's "passed alone" says.
  - A shared state file: none - the said-once record (`<git dir>/l7r-said/`) and the told marker are in the suite's own temp
    clone, a stale waiter is scoped by the per-run `NEVER` token, observed 2026-11-27, method: read `once::file`,
    `common_git_dir` and the suite.
- **Decision 1 - the fixture outlives the slow call; no hook change.** The guard's refusal is right whenever the run is live, and
  the test's 12 s was the bound, measured 2026-11-27 (the first-Stop-slowed suite on both texts). A longer fixture costs a green
  run nothing (each section ends its runs); the price is a sleeper that a killed suite would leave, which the EXIT trap and
  `endruns`' child kill answer. Priced and declined: a fresh guard binary before the suite (the rebuild wait is one possible slow
  call of several - load is another - and the suite is run by `make hooks-test` after the builds anyway). Label: the
  algorithmically easier route, the record silent (tooling, no research question).
- Red first: on HEAD's text the first Stop slowed 13 s fails the five (79 passed, 5 failed), and on the fixed text the same run
  passes 84 of 84, measured 2026-11-27 (the first-Stop-slowed suite on both texts). Unslowed, 20 of 20 green at load 25-29 and
  alone 84 of 84 in 8.0 s, with no `sleep 600` left after any run, measured 2026-11-27 (the suite 10x2, alone, and `pgrep` after
  each).

### T173 Approach (checklist part A)

1. **The goal, in the world.** The finished-run suite's refusal cases hold however slow a hook call is, and still fail a guard
   that lets a live run through.
2. **The constraints.** 451 T115's `settle` (a state that never comes fails, its SETTLE_S 30 s, observed 2026-11-27, method: read
   the suite), the per-run `NEVER` token (no cleanup reaches another clone's suite), and the guard's hook suite run as
   `make hooks-test` runs it.
3. **Where each comes from.** R: tasks.md T173, 451 T115's and T171's sections. O: the runs above (2026-11-27).
4. **Do they describe the world here?** Yes: the suite was run whole through its own shim, alone, 10 at once, and with its first
   Stop slowed, on the shared machine at the loads named, measured 2026-11-27 (the runs above).
5. **The order.** Any; it touches the suite alone.
6. **The exits.** Green: the first-Stop-slowed suite green on the fixed text and the 10-at-once runs clean. Red: what failed
   recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one fixture's length and its cleanup.
8. **The budget.** One landing.
9. **Done, measured.** The first Stop slowed 13 s: 5 red (section 6's five) before, 84 of 84 after, measured 2026-11-27 (the
   first-Stop-slowed suite on both texts).
10. **Before moving a constant.** The fixture's 12 s was no claim's, observed 2026-11-27, method: read the suite; now `RUN_S`,
    600 s, a GUESS with its measured why.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes: a false red of the hook suites at a landing is gone; the guard behaves as before.

**Found and left?** none

**Performance work?** no

<!-- plan-archive: archived 2026-11-28 -->
### T544 (make task-time took 61 s median over 31 real calls and 260 s a call on a copy, reading about 5.0 GB, observed 2026-11-27, method: 451 T536's record, dev/measurements/2026-11-27/t536-record-readers/results.md)

- **Approach**: what it re-reads, measured first: `make task-time` read 4,585,082,516 bytes of 7,138 files (observed 2026-11-28, method: T536's read-count shim over the 2026-11-27 02:00Z-14:29Z window, every path, each file's bytes against its size). Almost nothing is RE-read, 6,999 files once (observed 2026-11-28, method: T536's read-count shim over the 2026-11-27 02:00Z-14:29Z window). The re-reads are each main transcript twice, 857 MB for 429 MB (observed 2026-11-28, method: T536's read-count shim over the 2026-11-27 02:00Z-14:29Z window), since `columns::enqueued` and `columns::read_subagents` each read every `<sid>.jsonl`, and the pool log and `task-starts.jsonl` about 10 and 8 times, 2.3 MB together (observed 2026-11-28, method: T536's read-count shim over the 2026-11-27 02:00Z-14:29Z window), filed as T559. The bytes are the subagent transcripts read once, 3.58 GB, 4,460 files of them (2.57 GB) last written before the report's read-back start (observed 2026-11-28, method: T536's read-count shim over the 2026-11-27 02:00Z-14:29Z window, each file's mtime). So the fix is both: (1) `enqueued`'s rows read in `read_subagents`' one pass (`enqueue_rows`, the map `Subagents::enqueued`; `enqueued` removed, its three callers - task-time, where-time, the task progress view - reading the field), and (2) a transcript whose mtime is before the window's start less `SLACK_S` (an hour, a GUESS knob) is not read: every row it holds was written before it, so its usage rows are outside the window, and a run of the window has its `Bash` call, its notice and any `TaskStop` written at or after its start (the call seconds before its hook line); its agent or session is still entered with no calls (`tokens.read(path, "")`), so every map keeps its keys. An unbounded window (`stopped`, where-time with no readable `since`) skips nothing. After, 1,626,899,295 bytes of 2,722 files, transcripts 4.44 GB to 1.48 GB (observed 2026-11-28, method: T536's read-count shim over the 2026-11-27 02:00Z-14:29Z window). The output is byte-identical before and after on both windows, three pairs each, 1,131,096 and 1,830,443 bytes (observed 2026-11-28, method: `cmp` of each pair's outputs over 02:00Z-14:29Z and 2026-11-27T00:00Z-11-28T00:00Z), and the before binary is stable run to run (observed 2026-11-28, method: `cmp` of its first and third). Wall time on the night window is not resolved by the machine's noise, before median 106.3 s and after 115.6 s over eight alternated runs each at load 6 to 78 on 22 cores (observed 2026-11-28, method: `/usr/bin/time`, one binary's user time ranging 62 to 180 s). System time fell in every pair, 4.5-6.7 s to 1.8-3.8 s (observed 2026-11-28, method: `/usr/bin/time`). The quietest pair, at load 6-7, ran 85.0 s before and 64.0 s after (observed 2026-11-28, method: `/usr/bin/time`). The read phase was about 120 s of a 201 s run before, rchar flat from 123 s, so the rest is compute, T559's (observed 2026-11-28, method: `/proc/<pid>/io` rchar every 2 s).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| one pass and the mtime skip | `transcripts_tests.rs`: s.jsonl read 2 and the old subagent 1 on the old code, 1 and 0 after | n/a, no block | none: no map is drawn | n/a |

### T544 Approach (checklist part A)

1. **The goal, in the world.** `make task-time` reads each transcript once and none that cannot hold a row of its window, printing the same report.
2. **The constraints.** 462 FR-004 (read each record once); every figure the report prints stays the same (the brief).
3. **Where each comes from.** O: the shim's counts above, the A/B diff of outputs; G: the brief's "every figure it prints must stay the same".
4. **Do they describe the world here?** Measured on the live logs and transcripts at fixed past windows (an ISO SINCE and UNTIL), before and after binaries alternated, outputs diffed run by run.
5. **The order.** Red test first (the read counter `READS`, test-only), then the one pass, then the skip.
6. **The exits.** Green: the read-once test passes, the outputs identical, the bytes down. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** Bytes read a call 4.59 GB to 1.63 GB on the night window, the report identical (observed 2026-11-28, method: T536's read-count shim over the 2026-11-27 02:00Z-14:29Z window).
10. **Before moving a constant.** n/a: `SLACK_S` is new, a GUESS knob with its reasoning beside it.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A report reader sees nothing different: every figure is identical (diffed); the change is its time.

**Found and left?**
- Not fixed here: the report spends about 75 s of its 201 s after its last read, rchar flat at 4.58 GB from 123 s (observed 2026-11-28, method: `/proc/<pid>/io` rchar every 2 s), and re-reads the pool log and `task-starts.jsonl`, 2.3 MB (observed 2026-11-28, method: T536's read-count shim over the 2026-11-27 02:00Z-14:29Z window); neither is a transcript re-read, and the compute wants its own profile. Filed as T559; it orders no other open task.

**Performance work?** yes - a `[perf]` task (451 FR-013): it makes `make task-time`, `make where-time` and the task progress view read less.


<!-- plan-archive: T533 to T545 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->
