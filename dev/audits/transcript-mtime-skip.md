---
kind: adopted
title: the time reports skip a transcript last written before their window
for: make task-time, make where-time and the task progress view read each transcript once and none that cannot hold a row of their window, printing the same report
measured: 2026-11-28
measurement: 462 T544: make task-time over 2026-11-27 02:00Z-14:29Z read 4,585,082,516 bytes of 7,138 files before and 1,626,899,295 bytes of 2,722 after (T536's read-count shim, every path); the report byte-identical on that window and on 2026-11-27T00:00Z-11-28T00:00Z, three before-and-after pairs each; system time 4.5-6.7 s to 1.8-3.8 s a call, wall time not resolved at load 6 to 78 on 22 cores
command: make rust-test CRATE=rust/gate/crates/measure ONLY=transcripts_tests
falsifier: a report that differs with the skip off (SLACK_S raised past the window) on the same window - a row of the window in a transcript written before it
threshold: one such difference (it reopens the slack)
cost: one metadata call a transcript (microseconds, in make task-time's tool rows)
last-audited: 2026-11-28
cadence-days: 30
covers: SLACK_S
---

462 T544 (`rust/gate/crates/measure/src/measure/where_time/columns.rs`, `read_subagents`): every row of a transcript is written at or
after its own time, so a file last modified before the window's start less SLACK_S holds no usage row of the window, and a run of the
window has its `Bash` call, its notice and any `TaskStop` of it written at or after its start. SLACK_S, an hour, is a GUESS knob far past
the seconds between a call's transcript row and its hook line. A skipped file's agent or session is still entered with no calls, so
every map keeps its keys.
