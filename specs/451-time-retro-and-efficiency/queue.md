# The builders' queue (feature 451, before the port resumes)

**THE ORDER NOW LIVES IN `queue.txt`** (451 T313, T395, 2026-11-27): one entry a line, read by `make queue` (each state computed),
`make builder-next`, `make builder-done` and the pool-idle Stop guard. This file is kept for its reasoning - the GM's ordering, the
rules learned - and is no longer the list a session edits.

The order tasks are handed to pool trees, written down so it is not kept in a session's head (451 T313 will read a queue like
this one). The GM's ordering, 2026-11-26: *"putting the ones most likely to give us better measurements at the front of the
line, followed by the ones most likely to increase our task throughput"*. A task is taken from the top whose files do not
overlap a task in flight; `files` is the expected crates or files, a guess until the builder reports.

## In flight (2026-11-26, 20:10 UTC)

- T308 (one part: why plan reviews take a second round; the mechanical causes refused at `make decide`) - files:
  `rust/gate/crates/plan`, `rust/guard` static-runs order.
- T299 with T282's detector part (the Stop hook's question detector's false positives; moved to the front on the GM's word,
  2026-11-26: "I would prefer not to see these messages about false positives") - files: `rust/guard` escalation hooks.
- T315 where a test run's seconds go (a measurement) - files: none expected.

RULES learned running it: a task that must LOAD the machine (reproducing a failure under load) runs ALONE in its batch and
under 451 T321's bounded helper once that exists - two such tasks on 2026-11-26 held the load at 240 to 400 for over an hour
each, slowed three batch gates and froze the host's desktop (feature 460). A NEW MECHANISM is two builders from the start: one
measures, builds and tests and writes a handoff; a second writes the plan section, takes the review and reports (three of
three such tasks reached the context cap before closing: T285, T298, T316).

## 1. Better measurements

1. T298 - LANDED. Everything below is judged by its report.
2. T315 what a single-crate rebuild spends its seconds on (compile, link, run) - a MEASUREMENT, wants a quiet machine: run it
   alone, between batches. files: none.
3. T301 part 1 only: why one target directory holds 20-29 hashes of a crate (are builds recompiled that need not be) - a
   measurement first. files: `rust/gate/crates/rustc` if a cause is found. Its other parts wait (the GM: disk work begins after
   the parallelization talk).
4. T293 a live view of the tasks in flight (`make task-progress`). files: `rust/gate/crates/measure` - after T298 lands.
5. T274 the memory and load sampler as tooling, started with the builders. files: `rust/gate/crates/task` or a script - after T316.

## 2. Throughput

6. T316 - LANDED (it buys the first run's test build, about 7 s; not the lint or the coverage builds).
6a. T325 one feature set for a family's test and coverage builds (the one place compile time is spent twice: 17 of 75
    compiler runs after a core change) - files: `rust/gate/crates/rustc`.
6b. T321 the bounded load helper - before any further load-reproduction task (T314, T329).
6c. T334 a builder is dispatched through the tooling, which writes the standing part of its brief and checks its shape -
    four briefs broke the sizing rule on 2026-11-26 with nothing refusing. A mechanism: two builders. files: `rust/guard`
    (a dispatch check), `rust/gate/crates/task`, `scripts/container/builder-brief.md`.
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

T303, T305 (the pre-round); T309, T289; T104, T159; T298, T316. Carried and landed with their tasks still open: T304 (two
parts; its remainder is in group 2), T301 part 1 (its finding: nothing is rebuilt needlessly; the one duplication is 451 T325).
