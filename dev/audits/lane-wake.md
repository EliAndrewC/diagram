---
kind: adopted
title: the coordinator's wake-up, make lane-wait, and its dead-runner grace
for: the coordinator ends its turn on one backgrounded make lane-wait and is woken only for a line the lane owes it (a landed batch, a repair entry, an arbiter owed) or a runner dead over an open batch - FR-005's wakes and no others (461 plan D9, T20)
measured: unmeasured
first-audit: 461 T23 reads the lane's log over a real batch - how long after an owed line the wait exited (LANE_WAIT_POLL_S), and whether a runner a hand-in was starting was ever called dead (LANE_DEAD_GRACE_S)
measurement: none yet of the knobs. Live on a scratch repository, 2026-11-27: make lane-wait run in the background read `<target>/tool/l7r-gate lane wait` from /proc/<pid>/cmdline (the stall watchdog's waits_on_lane argv), an owed line appended to the scratch lane log ended it within a poll, printing that line, exit 0, the read mark at the log's end
command: make rust-test CRATE=rust/gate/crates/lane ONLY="wake"
falsifier: a dead-runner line written for a runner that was only starting (the grace too short), or an owed line that waited more than a minute to wake the coordinator (the poll too long)
threshold: either, once in a week of phase 2's landings (GUESS)
cost: one sleeping process a coordinator while it waits; each poll stats the lane's log and probes the runner's lock (one flock), reading the log only while no runner holds it
last-audited: never
cadence-days: 30
covers: WAIT_POLL_S
covers: DEAD_GRACE_S
covers: LOCK_S
---

461 T20 (`rust/gate/crates/lane/src/wake.rs`, `rust/guard/shared/src/lane_wake.rs`). WAIT_POLL_S = 5 s is the runner's own POLL_S,
the same bound on how long a line waits against gates of minutes. DEAD_GRACE_S = 30 s is past a start's START_WAIT_S (5 s) and a
short rebuild of the lane tree's l7r-gate (461 T51), short against a gate's minutes: a stranded batch is told within half a minute,
a starting runner is not called dead. LOCK_S = 5 s is how long a reader of the read mark waits for another holding its lock (a
read of milliseconds) before leaving the lines to that reader, which is showing them. Weighed in the plan (D9) and not taken: the
Monitor tool (a wake per output line, a watch of at most 30 minutes); a ceiling of the wait's own (LANE_WAIT_MAX, priced in T23
only if the platform ends a background command at a time limit).
