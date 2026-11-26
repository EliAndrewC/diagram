---
kind: adopted
title: builder worktrees come from a standing warm pool
for: a builder's first closing checks run on a warm build cache, because no session can make a builder's worktree by hand or remove a pool tree or its cache
measured: 2026-11-26
measurement: the day's parallel builders - 21 of 22 code builders at two ran in a fresh worktree whose first closing checks took 14-30 minutes against about a minute warm, and the coordinating session removed each worktree and its cache after the landing; the rename test - a pool tree renamed with its cache moved rebuilt every workspace crate (tool build 0.11 s to 66.5 s, the guard's test build 0.08 s to 41.7 s, the same again moved back), so the three trees of the day were adopted under their own names
command: make builder-trees (who holds each tree, each cache's size); make rust-test CRATE=rust/gate/crates/task (builder_tree::tests); bash tests/hooks/test-builder-pool-hooks.sh; make task-time (a builder's first closing-checks minutes)
falsifier: a builder's first closing checks in a pool tree taking more than five minutes with no cold tree announced, a pool tree or cache found removed with no drop on .git/builder-pool.log, or the guard refusing a correct command (make guard-log GUARD=builder-pool)
threshold: one cold first run in a tree the pool called warm, one unlogged removal, or two refusals of correct work in a week (any reopens it)
cost: about 9 GB of build cache a pool tree (four at the cap, L7R_BUILDER_POOL, a GUESS), which the cache's budget never evicts (about 40 GB at the cap outside the 100 GB budget's reach); one walk of the command on a Bash call naming worktree or rm
last-audited: 2026-11-26
cadence-days: 30
covers: rust/guard/src/guards/builder_pool_hooks.rs
covers: CAP
---

451 T285 (`rust/gate/crates/task/src/builder_tree.rs`, `rust/guard/shared/src/builder_pool.rs`,
`rust/guard/src/guards/builder_pool_hooks.rs`). The GM, 2026-11-26: "we should make it so that whatever tooling we use to create
worktrees automatically enforces and performs the correct behavior without the opportunity for this kind of mistake in the future".
`make builder-tree T=<task>` hands out a free tree of the clone's pool, brought to the clone's HEAD and held by the task, and
makes one more (cold, said so, its guard built) only when none is free and the pool is under its cap; `make land` frees a landed
task's tree with its cache in place; `make builder-tree-drop TREE= REASON=` is the one removal. The guard refuses the hand forms.
Weighed and not taken: renaming the three existing trees to `-b1` to `-b3` (the rename chills the cache, measured above); making a
cold tree when a free one is held by uncommitted work (the cold tree is the failure, so the handout refuses and names the paths);
exempting the landing's and the review's trees by name (a hand command could take the name - they are exempt because their
scripts' git calls are not tool calls). The cache's budget (`sweep/evict.rs`) skips a pool tree's build directory, since a free pool
tree is idle by its ranking and would be emptied first; a tree whose holding tasks are all ticked is freed at the next handout.
