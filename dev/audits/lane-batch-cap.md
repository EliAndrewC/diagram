---
kind: adopted
title: the landing lane's batch cap
for: a batch of the lane holds at most LANE_MAX changes (the oldest waiting hand-in and its feature's run straight after it), so a red batch costs few changes' wait and a smaller set to attribute (461 plan D5, T14)
measured: unmeasured
first-audit: 461 T23's real batch, and trial 458's batch sizes against attempts, read from lane.jsonl
measurement: none yet. The seed: the two-tier threshold's ceiling of "about six tasks" (docs/process-decisions.md); the night of 2026-11-27, smaller batches landed on the first or second attempt after 10:00Z, the 63-task batch took 14 attempts (461 spec, plan D5)
command: make rust-test CRATE=rust/gate/crates/lane ONLY="batch::tests"
falsifier: batches cut at the cap whose next batch waits behind them for more gate minutes than a red attempt of the larger batch would have cost, read from lane.jsonl's run minutes and batch sizes
threshold: over a week of phase 2's landings, the cap reached by more than half the batches with their first attempt green (GUESS: the cap then holds hand-ins back for nothing)
cost: the gate minutes of each extra batch the cap forms (lane.jsonl's run lines, booked by make task-time to the landing's own Phase lines)
last-audited: never
cadence-days: 30
covers: LANE_MAX
---

461 T14 (`rust/gate/crates/lane/src/batch.rs`). LANE_MAX = 6 is the plan's GUESS (D5), with LANE_WAIT_S = 0 (a batch starts as soon as
the lane is idle and a hand-in waits; no constant, since the step forms at once). Weighed in the plan and not taken: Mergify's default
30 s wait (with a gate of minutes, hand-ins gather behind a running batch anyway). Trial 458's verdict resets both.
