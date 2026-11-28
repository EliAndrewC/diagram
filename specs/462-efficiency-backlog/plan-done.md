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


