---
kind: adopted
title: a started-task mark per task, read per tree
for: builders in several worktrees start their own tasks without moving each other's mark, and a push is held by another tree's started task only where it carries that task's edits
measured: 2026-11-25
measurement: the parallel trials 2-5 (eleven tasks, two builders at a time, each in its own worktree): the one shared mark refused a landing while the other task was started, worked around by moving the mark by hand for each landing; trial 1: a second make task-start overwrote the first's mark
command: make rust-test CRATE=rust/guard/shared (speckit::marks::tests::each_tree_keeps_its_own_mark and the holding test); bash tests/hooks/test-sync-with-main.sh
falsifier: a mark moved by hand again in a parallel batch, or a push let through that carried another started task's unfinished edits
threshold: one hand move of a mark in a batch, or one such push (either reopens it)
cost: the push's and make land's hold check (seconds, in make task-time's land rows)
last-audited: 2026-11-25
cadence-days: 30
---

451 T254 (`rust/guard/shared/src/speckit/marks.rs`, `speckit/touch.rs`): `make task-start` writes
`<git common dir>/task-marks/<feature>/<task>.json`; this tree's own open started task holds its push whatever it carries (feature
405 T32's D4 kept); another tree's holds only by the edits the push carries (451 T101's rule, its prefix fault - the clone's path
alone, so a worktree builder's edits were never seen - fixed on the way). Approved by the GM's words of 2026-11-25 ("sounds good,
please start with that"), one of four fixes before three parallel builders.
