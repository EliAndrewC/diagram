# Feature 461 quickstart: using the landing lane, and testing it

Load this file when: coordinating builders with the lane, building as a builder under it, or checking that it works.

## The coordinator

1. File tasks and queue entries as today (`make task-add`, `make queue-add`), commit them, and (from phase 2) push them DIRECT:
   `scripts/sync-with-main.sh done`. A handout refuses while the clone holds commits main lacks, and prints that command (D13). In
   phase 1 you still run `make land` by hand; hand-ins arrive applied onto your clone's HEAD.
2. Dispatch builders from the queue (`make builder-next`, `make builder-brief`). Repair entries come first in `make builder-next`.
3. The wake-up: `make lane-wait` with `run_in_background: true`. When it returns, read its lines (one per landed batch, or a stop
   that needs you). The Stop guard refuses your stop while the lane has work and no `make lane-wait` runs, printing the command, so
   re-arming is the tooling's; the prompt hook prints any lane line you missed.
4. Never carry, land, push or repair. Every line that needs integration work names a fresh agent for you to dispatch (`plan.md`
   D7's table): a repair entry (a red, a conflict, a push failed twice) goes to a fresh builder through `make builder-next`; an
   arbiter owed (a task red a second time) goes to the `round-arbiter` agent on the bundle the lane's `make arbiter-ask` wrote,
   and its ruling comes back as a repair entry. The lane dead needs only `make lane-start`. `make lane` shows where everything
   stands.

## A builder

1. Build in the pool tree the brief names, run the first tier (`make builder-checks CRATE=...`), no coverage.
2. End with `make builder-done T= F= MSG="<subject>"`. It applies your work onto current `origin/main`, runs the landing's first
   pass, and commits. If it refuses:
   - a conflict with main: resolve the files it names in your tree, then run `make builder-done` again (it resumes);
   - a first-pass refusal (plan review owed, ledger row, audit entry, file size, pointer): run the command it prints, then
     `make builder-done` again.
3. Report and end. The lane lands your commit; if your change makes a batch red, a fresh builder gets a repair entry with the
   gate's output.

## How to test

- **The crates**: `make rust-test CRATE="rust/gate/crates/lane rust/gate/crates/land rust/gate/crates/task rust/gate/crates/tree"`
  and `make rust-test CRATE=rust/guard` (each new refusal fails when its check is deleted).
- **The guard over two trees** (D10): `bash tests/hooks/test-gate-write-hooks.sh` - a commit in the clone during the lane's gate
  is let through, one aimed into the lane's tree is held.
- **End to end, on a scratch world**: the lane crate's integration test builds a clone, a bare `origin` and two pool trees, hands
  in two tasks, runs one batch, and checks: one push, both ticked on `origin/main`, both done refs deleted, one `owed` line. Its
  red variants: a change breaking one crate's test is attributed and ejected with one further run; a red the record cannot place is
  halved within ceil(log2 n) + 1 runs; a conflict with main becomes a repair entry; a green batch whose push fails twice becomes
  one `integrate` repair entry; the tripwire by task fires when a repaired task is red again and stays quiet through a halving.
- **On real work** (phases 2 and 3): hand in two of this feature's own tasks, then read `make lane` and
  `<common>/l7r-lane/lane.jsonl`: the batch's runs, minutes and push; `make task-time SINCE=<the batch's start>` shows the landing's
  Phase lines filed under the lane's tree.
- **The comparison** (phase 5): the D12 script over a like window, each figure beside the night's from `research.md` R3 and
  `baseline-task-time.txt`, with both windows' concurrency: the window chosen by D12's likeness test (trees held and the load band,
  each a GUESS knob), both windows' trees held and median load stated beside each figure where they differ.
