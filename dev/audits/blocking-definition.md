---
kind: adopted
title: what counts as blocking time
for: the task time breakdown books a minute as blocking only when something else waits on it before it can start, so the talk weighs each kind of work by what it actually holds up
measured: 2026-11-25
measurement: two readings tried and rejected the same day - a session's own idle waits summed booked a headless page session's turns as blocking, 949 min, half the working time, and could exceed the clock; the project's wall clock with nothing working anywhere hid research a decision truly waits on whenever unrelated work ran elsewhere
command: make task-time
falsifier: a sample of tasks read by hand where the booked blocking disagrees with what actually waited
threshold: more than about one task in ten disagreeing (the GM: "it doesn't have to be 100% exact")
cost: the Blocks: line in every dispatch brief and L7R_BLOCKS on a make run (words, no minutes); make task-time's own run
last-audited: 2026-11-25
cadence-days: 30
---

Decided by the GM, 2026-11-25, recorded in full in `docs/process-decisions.md` ("What counts as blocking time"): "a minute should
count as blocking. When something else is waiting on it to be done before it can be started". Blocking is a dependency: the data
carries a `Blocks: <feature> T<n>` or `Blocks: none` line in a dispatch and an `L7R_BLOCKS` variable on a make run, and stated
defaults decide where none is given (a builder's foreground command blocks its task; a background run only from when its task waits
on it; a page session or research pass blocks nothing unless its brief names a task).

The audit is a hand reading: pick ten landed tasks from `make task-time`, read their transcripts for what actually waited, and count
the disagreements.
