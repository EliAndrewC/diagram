# The builders' queue (feature 451, before the port resumes)

The order tasks are handed to pool trees, written down so it is not kept in a session's head (451 T313 will read a queue like
this one). The GM's ordering, 2026-11-26: *"putting the ones most likely to give us better measurements at the front of the
line, followed by the ones most likely to increase our task throughput"*. A task is taken from the top whose files do not
overlap a task in flight; `files` is the expected crates or files, a guess until the builder reports.

## In flight (2026-11-26)

- T304 (two parts: the carry test under load, the index lock) - files: `rust/gate/crates/land` tests, the guards' git spawn.
- T316 the pool tree pre-warmed at handout - files: `rust/gate/crates/task` (`builder_tree.rs`), `rust/gate/crates/rustc`.
- T298 the task time breakdown's window table, second tier apart, booking faults, SINCE=last - files: `rust/gate/crates/measure`.

## 1. Better measurements

1. T298 - in flight. Everything below is judged by its report.
2. T315 what a single-crate rebuild spends its seconds on (compile, link, run) - a MEASUREMENT, wants a quiet machine: run it
   alone, between batches. files: none.
3. T301 part 1 only: why one target directory holds 20-29 hashes of a crate (are builds recompiled that need not be) - a
   measurement first. files: `rust/gate/crates/rustc` if a cause is found. Its other parts wait (the GM: disk work begins after
   the parallelization talk).
4. T293 a live view of the tasks in flight (`make task-progress`). files: `rust/gate/crates/measure` - after T298 lands.
5. T274 the memory and load sampler as tooling, started with the builders. files: `rust/gate/crates/task` or a script - after T316.

## 2. Throughput

6. T316 - in flight.
7. T308 the second review round's mechanical causes removed at `make decide`, and the review's wait put to use; the tooling's
   one-tier order nudge retired. files: `rust/gate/crates/plan`, `rust/guard` static-runs order.
8. T313 the tooling keeps the pool full (this queue read by a check at a builder's end and at Stop). files: `rust/guard` Stop
   hook, a new reader - after T297.
9. T297 the overlap of two tasks' files named at handout. files: `rust/gate/crates/task` (`builder_tree.rs`) - after T316.
10. T307 what a landing waits on that it need not (the gate-write guard holding other trees' commits; every push check in the
    first pass; several finished tasks in one gate run by default). files: `rust/guard` gate-write, `rust/gate/crates/land`.
11. T300 shared registry files one entry a line; the carry regenerating the make-targets page. files: `docs/guards.md`,
    `rust/*/CLAUDE.md`, the Makefile - RUN ALONE in its batch: it rewrites the files every other task appends to.
12. T314 the state-sync suite under load; T304's remainder (the suite stamps trees overwrite). files: `tests/hooks`, `rust/guard`.

## 3. Correctness and hygiene (no throughput at stake; before the port all the same)

13. T302 every writer has one tree and a landing needs a clean clone - four steps, a builder each, in order.
14. T310 the event log books a pool builder's check dispatch to no task; `make builder-tree` writes the start row and mark.
15. T306 the program spellings the tree guards still miss. T275 the state paths joined onto `.git` (measure each in a worktree).
16. T312, T311, T143 tests that read or write the machine's live state. T288 the per-task plan bundle. T296 pool follow-ups.
17. T286 (mostly moot with the pool), T294 (its unstaged-file part superseded by T302), T299 (the Stop hook's statistic case).
18. T278 and T301's other parts (disk) - after the parallelization talk, by the GM's word.

## Landed from this queue

T303, T305 (the pre-round); T309, T289; T104 and T159 staged for the next gate.
