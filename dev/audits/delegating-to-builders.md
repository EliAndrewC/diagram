---
kind: adopted
title: delegating code tasks to builders at all
for: the coordinating session keeps its own context small and dispatches each code task to a builder, so the coordinator's every turn does not re-read the build
measured: unmeasured
first-audit: agenda item 12's three-way comparison (specs/449-rust-codebase/port-talk-agenda.md): minutes (blocking and total) and tokens per landed task for (a) builders capped at 300k with handoffs, (b) builders let grow, (c) no builders, the coordinator building in its own context; plus the handoff's own overhead - writing the handoff, the brief, the coordinator's reading of the report
measurement: never measured as a choice; the context it runs in, 2026-11-25 over 24 hours (`make where-time` F=449 and F=451): agents used 2,147 agent-minutes, builders and coordinators 1,692 of them (79%); the coordinating session waited 385 min on agents
command: make where-time (the share); make task-time (the per-task minutes the comparison needs)
falsifier: arm (c), no builders, lands a task in no more blocking minutes and no more tokens than arm (a), the coordinator's re-read context counted
threshold: arm (c)'s blocking minutes per landed task at or below arm (a)'s, and its tokens at most 1.1x arm (a)'s (GUESS)
cost: make task-time's builder rows and the coordinator's waits on agents (make where-time)
last-audited: never
cadence-days: 7
---

The GM, 2026-11-25: "we should make sure to measure whether the complexity of the handoffs actually saves time and/or tokens
relative to either letting the builders grow or not using them in the first place". Arm (a) against (b) has a first measurement
(`builders-context-cap.md`); arm (c) has none, and its cost lands on the coordinator's own context, re-read every turn.

It is never audited, so `make audits` lists it first until the three-way comparison runs.
