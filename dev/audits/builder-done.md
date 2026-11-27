---
kind: adopted
title: a pool tree is handed on as soon as its builder's work is committed
for: a warm pool tree goes to its next task the moment its builder's work is committed, before the carry and the landing, because one command commits the tree, keeps the commit under a ref and releases the tree, and prints the next dispatch ahead of the carry
measured: 2026-11-27
measurement: the three warm pool trees stood idle 336 of 1,440 tree-minutes (23%) from 2026-11-26T17:00Z to 2026-11-27T01:00Z with the queue never short - 170 while the session was in its own turn, 105 while a landing ran, 46 while it was stopped - the session working a builder's end as commit, carry, resolve, check, land and only then the next brief (dev/measurements/2026-11-27/tree-idle/results.md); the command itself is not yet measured over a window
command: the tree-idle table re-measured over a like eight-hour window (tree-idle.py beside the results file); make builder-trees (the done commits not yet carried); make rust-test CRATE=rust/gate/crates/task (builder_done::tests)
falsifier: the tree-idle table re-measured over a like window still showing the warm trees idle 10% or more, or a done commit lost - one the pool's log names whose work the clone's HEAD does not hold and that no ref under refs/l7r/done keeps (make carry deletes the ref at its verified end, an empty pick's too, so a missing ref alone is no loss)
threshold: idle 10% or more of the warm trees' minutes over a like window (a GUESS knob), or one done commit lost
cost: one command at each builder's end, in place of the hand git add and git commit (about ten git calls, and one read of the clone's history since the oldest done commit still waiting); one ref a task under refs/l7r/done until its commit is carried; make builder-trees reading those refs
last-audited: 2026-11-27
cadence-days: 7
covers: rust/gate/crates/task/src/builder_done.rs
---

451 T394 (`rust/gate/crates/task/src/builder_done.rs`). The GM, 2026-11-27, on `make task-time`'s 123.3 blocking minutes for the
second tier: "if our tooling indicates that we have spent over 2 hours blocking on the second tier then that's a HUGE problem,
either with our measurements or with our process, and we should get to the botom of that ASAP". `make builder-done T= F= MSG=`
commits the builder's pool tree, keeps the commit under `refs/l7r/done/<feature>-<task>`, releases the tree and prints the next
dispatch and then `make carry FROM= COMMIT=`; `make builder-trees` lists each done commit the clone's HEAD does not hold.

Weighed and not taken: reading the queue's next task from `specs/<feature>/queue.md` (prose a session edits, which code would
guess at; the command prints a placeholder, and the machine-readable queue is 451 T313's); telling a carried commit by
`git branch --contains` (a carry is a cherry-pick, so never) or by `git cherry` (a patch-id, which a carry that kept both sides of
a conflict changes) - it is told by the author's time and the subject, which a cherry-pick keeps; moving the guard's list of
guard files to `l7r_shared` so the commit's guard-file rule reads it (an edit of the guard's own sources; the command holds a
copy, named as one). Not built by this entry: `make land` carrying what is staged by commit, and the Stop hook's refusal of a
turn's end while a tree is free (451 T313).
