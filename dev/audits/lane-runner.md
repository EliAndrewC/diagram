---
kind: adopted
title: the landing lane's detached runner and its idle stop
for: make lane-start (and, from phase 2's base, every hand-in) starts one detached l7r-gate lane --work a clone, held by flock on l7r-lane/lane.lock; it polls every LANE_POLL_S, ends LANE_IDLE_S after the last new hand-in it saw, and a start waits START_WAIT_S for it, a stop STOP_WAIT_S (461 plan D2, T12)
measured: 2026-11-27
measurement: none yet of the knobs - 461 T23 reads the lane's log over a real batch of this feature's tasks (how often a hand-in finds the runner stopped and restarts it, against how long a runner sits idle). Live on a scratch repository, 2026-11-27: a start read through a pipe returned at once with the runner's pid (its pid, process group and session one number); a second start named it; LANE_IDLE_S=3 ended it with a stop line `idle` within one poll; make lane-stop and NOW=1 each ended one with its line; an open batch in the log was named `resume <batch>` on the next start's line
command: make rust-test CRATE=rust/gate/crates/lane ONLY="runner::tests"
falsifier: a hand-in that waits on a stopped runner more than once a day (the idle stop too short), or a runner idle more than half the hours it runs (too long); a start or stop that times out on a healthy runner
threshold: either, over a week of phase 2's landings (GUESS)
cost: one sleeping process a clone while the lane has had a hand-in in the last hour; each poll reads the pool's log, the done refs and the lane's log (no fetch); a restart (under a second) at the first hand-in after an idle stop
last-audited: 2026-11-27
cadence-days: 30
covers: LANE_IDLE_S
covers: LANE_POLL_S
covers: POLL_S
covers: START_WAIT_S
covers: STOP_WAIT_S
covers: TAKE_S
---

461 T12 (`rust/gate/crates/lane/src/runner.rs`). LANE_IDLE_S = 3600 is the plan's GUESS (D2): a stopped runner costs one restart
at the next hand-in, a running idle one a sleeping process. The idle clock runs from the newest hand-in the runner saw (or a
batch it ran), never from "nothing waiting", so a runner over a hand-in it cannot yet batch (before T14) still idles out. POLL_S
= 5 s bounds how long a hand-in waits to be seen, against gates of minutes. START_WAIT_S = 5 s and STOP_WAIT_S = 10 s are bounds on
a wait for a lock to change hands. Weighed in the plan (D2) and not taken: the Workflow tool and a loop of the coordinator's turns
(each step a turn); Gas Town's Refinery (a standing agent).
