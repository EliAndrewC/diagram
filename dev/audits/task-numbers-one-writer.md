---
kind: adopted
title: task numbers handed out by one writer
for: two builders in two worktrees filing tasks on one feature never take the same T-number
measured: 2026-11-25
measurement: the parallel trials 2-5: builders in two worktrees each ran make task-add and filed T247, then T248, twice, renumbered by hand; on HEAD's numbering the new test's second worktree filed T10, the first's id
command: make rust-test CRATE=rust/gate/crates/task (task_add::tests::two_worktrees_never_take_one_id); a duplicate's census: grep -ho '^- \[.\] T[0-9]*' specs/<feature>/tasks.md specs/<feature>/tasks-done.md | sort | uniq -d
falsifier: a T-number filed twice again, or the reservation's lock making a filing wait
threshold: one duplicate id, or a filing waiting past 5 s on the lock (GUESS)
cost: make task-add's run (its lock and the reads of main's files; seconds)
last-audited: 2026-11-25
cadence-days: 30
---

451 T255 (`rust/gate/crates/task/src/task_add.rs`): the id is one past the highest of this tree's files, the same files on `main`
and `origin/main` as last fetched, and the reservation file `<git common dir>/task-ids.txt`, written under the filing lock (451
T84) before the box goes in. A filing that `make quick` withdraws gives its id back.
