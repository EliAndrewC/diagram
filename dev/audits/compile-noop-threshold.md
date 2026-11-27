---
kind: adopted
title: a compile line under 1.0 s is counted a no-op check in make task-time's counts
for: a task's compile count says how many of its compiler invocations did work, so the GM can read a count beside its lines and minutes without cargo's no-op checks (a crate found fresh) swelling it
measured: 2026-11-27
measurement: each (step, crates) pair's fastest, p10 and median span over the 451 event log's Phase lines, pairs with 10 or more lines - a no-op floor of 0.03 to 0.15 s for build, cover-build and lint, 0.5 s for prewarm (its span polled in 0.5 s steps), and a single crate's real rebuild past 1 s (p10 of rust/guard/shared's builds 1.51 s, of rust/gate/crates/measure's 1.27 s); T417's 40 compiles of 2026-11-27, 39 of them 1.0 s or more, the one under it a 0.1 s build of rust/guard/shared in make builder-checks
command: make task-time SINCE=2026-11-27T03:30:00Z UNTIL=2026-11-27T12:00:00Z (T417's counted lines listed under its tables); make rust-test CRATE=rust/gate/crates/measure ONLY="measure::where_time::columns::ran"
falsifier: a compile line the writer marks as compiling (its `compiled` count above 0, once the writer writes one) whose span is under 1.0 s, or one marked 0 whose span is 1.0 s or more
threshold: one such line in ten of a day's compile lines (the writer's field and the span disagreeing) reopens the knob, or retires it for the field
cost: a cargo call that rebuilt one small crate in under a second is miscounted a no-op, and a slow no-op (a cold filesystem, a held cargo lock) is counted as work; the minutes are untouched
last-audited: 2026-11-27
cadence-days: 30
covers: rust/gate/crates/measure/src/measure/where_time/columns/ran.rs
covers: NOOP_BELOW_S
---

451 T522 (`rust/gate/crates/measure/src/measure/where_time/columns/ran.rs`). The GM, 2026-11-27, on T417's 19 compiles and 28
test runs: "I would have expected the number of compiler runs to actually be strictly higher than the number of test runs". A
`Phase` line says nothing of what cargo did, so the reader tells a no-op by the span alone, a GUESS knob. The exact answer is the
writer's (`rustc/kept.rs` already reads cargo's `--message-format=json`, whose `compiler-artifact` messages carry `fresh`; a lint's
clippy names each `Checking` crate), filed as its own task; the reader takes a line's `compiled` count first where it carries one.

451 T528 (2026-11-27): the writer now writes it. Each `build`, `cover-build`, `lint` and `prewarm` line carries `compiled` (the
crates cargo's `--message-format=json-render-diagnostics` names built afresh, `rustc/phase.rs`), left out where cargo exited
non-zero or named no artifact; the reader takes it first, so this knob decides only the lines written before T528 and those
without the field. The falsifier is now readable: on the first 11 lines with the field (`diagram-backlog-t271`, 2026-11-27) the
field and the span agreed on all 11 (one of 0 at 0.08 s; ten of 1 to 4 at 1.16 to 15.21 s).
