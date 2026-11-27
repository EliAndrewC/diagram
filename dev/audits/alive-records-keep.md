---
kind: adopted
title: the slow test runs' live records kept
for: the live-state records a test program past 30 s writes (451 T463) stay bounded: each write keeps the newest KEEP (50, a GUESS knob, at most about 3.1 MiB at the 64 KiB cap) in the event-log directory's alive/
measured: 2026-11-27
measurement: 451 T473: alive/ held 1 file, 8 KB on 2026-11-27; the record of a slow run is read only when one is investigated
command: make rust-test CRATE=rust/gate/crates/rustc ONLY=rustc::tests::alive
falsifier: a slow run's record pruned before anyone read it (more than 50 slow runs between two investigations)
threshold: one such case in a month's use (it reopens the knob)
cost: a directory scan at each write (milliseconds, in make task-time's tool rows)
last-audited: 2026-11-27
cadence-days: 30
covers: KEEP
---

451 T478 and T473 (`rust/gate/crates/rustc/src/rustc/alive.rs`): a store a tool writes and nothing pruned, bounded where it is written. The knob is a GUESS chosen by the
task's builder within the GM's go-ahead of 2026-11-27 ("go ahead and do all of the load-bearing ones").
