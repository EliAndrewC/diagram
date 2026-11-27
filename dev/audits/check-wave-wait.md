---
kind: adopted
title: a check-wave row's wait for its agent
for: a check-wave row that is pending, or returned with no reply, is waited on for at most WAVE_WAIT_S (6 h, a GUESS knob) after its dispatch, so a subagent stop that concerns no live row neither books the return nor rewrites the whole check state (451 T505)
measured: 2026-11-27
measurement: 451 T505 - 14 impl-drift wave rows returned with no reply, 860.7 to 863.6 h old, made every SubagentStop rewrite the 2.6 MB state; a checks-hooks SubagentStop from an agent no row names went from 89.6 to 14.1 ms of CPU median and from 22 of 22 writes to 0 of 22 (20 interleaved runs, a copy of the state)
command: make rust-test CRATE=rust/guard/shared ONLY="checks::handle::hold_writes"
falsifier: a wave agent that returns more than 6 h after its dispatch and whose reply, round or EDIT blocks are lost because its row was no longer waited on
threshold: one such lost return in a month (it reopens the knob)
cost: each SubagentStop's check-hooks call (milliseconds, in make task-time's hook rows)
last-audited: 2026-11-27
cadence-days: 30
covers: WAVE_WAIT_S
---

451 T505 (`rust/guard/shared/src/checks/rounds.rs` `wave_waits`, read by `handle::concerns` and `rounds::pair_wave`): a row past
its wait stays in the state as it was and is no longer booked. The knob is a GUESS chosen by the task's builder within the GM's
go-ahead of 2026-11-27 ("go ahead and do all of the load-bearing ones"), as `HOLD_MAX_S` was for a plan hold (451 T489).
