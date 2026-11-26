---
kind: adopted
title: make task-progress, the live view of the tasks in flight
for: the session and the GM see, while a task is still in progress, which builders, landings and page sessions are running and where each builder's minutes have gone, by the task time breakdown's own categories
measured: 2026-11-26
measurement: the command run on the session clone's real logs with four builders in flight (2026-11-26, about 20:45Z; `time scripts/gates/l7r-gate.sh measure task-progress --root <the clone>`): 19.2 s of wall time with the tool built, against the 55 s recorded for make task-time SINCE=24h; its four blocks named the four held pool trees' tasks, each builder RUNNING with its context read from its transcript; an earlier run at 20:36:52Z missed the landing then in flight, fixed and pinned by the fixture's landing
command: make task-progress [BACK=<N>h] [AT=<ISO UTC>]; make rust-test CRATE=rust/gate/crates/measure (measure::task_time::progress::tests)
falsifier: nobody runs it - the session still reads a running task's time from make where-time or the raw event log - or what it shows is wrong often enough that it is not trusted (a running builder shown stopped, a landing in flight missed, a block's minutes far from what make task-time books for the task once it lands)
threshold: no run of it in a week of builder batches, or 2 wrong views found in a week (GUESS)
cost: a run when asked, 19.2 s on a day's logs with four builders in flight (measured 2026-11-26); it reads only, runs in no gate and no landing, and holds no lock
last-audited: 2026-11-26
cadence-days: 30
---

451 T293, the GM 2026-11-26: "does their tooling that we have already built allow you to see while a task is in progress where the
time is going? ... I think that we should be able to see that kind of thing". The code is
`rust/gate/crates/measure/src/measure/task_time/progress.rs` with `progress/scene.rs` (who is running) and `progress/render.rs`
(the text); its module doc states the rule and its known gaps. It books nothing of its own: a builder's minutes are
`task_time::book`'s over the lines of that builder's family alone.

Its one knob is `BACK_H`, the hours read back where no held tree is older (2.0, a GUESS; `BACK=` overrides it for a run).

What to check at a re-audit: that the gaps it names in its own output are closed or still named - a resumed builder's later spans
(451 T324, T345), a pool tree's Phase lines naming another task (451 T332), a carry booked to the task that retook the tree (451
T346), a compound command named by its first target (451 T348), a builder's background run it cannot tell dead from live (451
T349) - and that its wall time has not grown past a wait a session will not sit through.
