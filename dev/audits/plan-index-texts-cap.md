---
kind: adopted
title: the plan index's kept texts cap
for: the plan digest index's kept texts (451 T465) stay bounded: written texts prune the directory to TEXTS_CAP (4 MiB, a GUESS knob), the least recently read dropped first, so the store cannot grow without limit
measured: 2026-11-27
measurement: 451 T478: the live store held 108 files, 1.3 MB on 2026-11-27; a prune scan over 432 files (5.0 MB) took 1.5 ms median, a read's mtime touch 4.9 us (a Python stand-in, not the Rust prune)
command: make rust-test CRATE=rust/gate/crates/plan ONLY=plan::history
falsifier: a landing's plan calls fetching dropped texts back from git often enough to cost more than the disk they free (the cap too small), or the directory past the cap
threshold: one such case in a month's use (it reopens the knob)
cost: a directory scan at each write (milliseconds, in make task-time's tool rows)
last-audited: 2026-11-27
cadence-days: 30
covers: TEXTS_CAP
---

451 T478 and T473 (`rust/gate/crates/plan/src/plan/history/index.rs`): a store a tool writes and nothing pruned, bounded where it is written. The knob is a GUESS chosen by the
task's builder within the GM's go-ahead of 2026-11-27 ("go ahead and do all of the load-bearing ones").
