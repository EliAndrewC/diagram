---
kind: adopted
title: a load run is bounded by its own sentinel
for: a builder reproducing a failure under load holds the machine for a stated time, with a stated number of processes, and never past it - whatever happens to the builder's own call
measured: 2026-11-27
measurement: in the pool tree diagram-backlog-t269 (22 cores) - make under-load CMD='make rust-test CRATE=rust/gate/crates/rustc ONLY="rustc::tests::under_load::the_words"' COPIES=2 LOOPS=2 BURNERS=1 MAX_MINUTES=1: 4 of 4 green in 3.0 s, its four inner test Phase lines overlapping in pairs under make target under-load, and one under-load line; the caller's whole process group SIGKILLed mid-run (3 copies of sleep 60 and 2 burners): the run's group of 10 processes empty 0.7 s later, its Phase line "the caller went away", 3 cut; the warden SIGKILLed with the caller (bound 6 s): the group empty 25.9 s after the kills, by the sentinel at 6 s + 2 x 10 s; the module's red-first mutations (no sentinel kill, no caller watch, no TERM, no KILL, no gate, no own group): each turned one to three of its ten tests red
command: make rust-test CRATE=rust/gate/crates/rustc ONLY="rustc::tests::under_load"; the event log's Phase lines whose step is under-load
falsifier: a load run's processes found alive past MAX_MINUTES plus twice GRACE_S (the sentinel failed); a builder found holding the machine by hand at a load past the cap (the cap too low to reproduce with, so it was bypassed); or a red that needed more than MAX_MINUTES_CAP minutes to show
threshold: one process of a load run's group alive past its bound plus 20 s; one hand load past PER_CORE processes a core since this landed; one reproduction needing more than an hour (any reopens it)
cost: booked to tests by its make target (the guard's table); the machine's cores for the stated minutes, which is what it is for; a rustc cut at the bound (accepted, the help says to build first; stale.rs heals one link)
last-audited: 2026-11-27
cadence-days: 30
covers: rust/gate/crates/rustc/src/rustc/under_load.rs
covers: MAX_MINUTES_CAP
covers: PER_CORE
covers: GRACE_S
---

462 T321 (`rust/gate/crates/rustc/src/rustc/under_load.rs` and `under_load/warden.rs`). Why: 451 T104's and T304's builders held
the machine at a load of 240 to 400 for over an hour by hand on 2026-11-26, slowing two batch gates and failing a third suite.
MAX_MINUTES_CAP (60) is a GUESS: the length those hand loads ran past. PER_CORE (3) is a GUESS: past the 30 copies on 22 cores run
by hand on 2026-11-27 (a load of 38 to 86), short of the loads of 240 to 400. GRACE_S (10) is a GUESS: a cargo run's own shutdown
between the TERM and the KILL. Weighed and not built: a sweep of `/proc` for processes that left the group (a CMD running
`setsid` or `timeout`) by an environment mark - accepted as a limitation, since the checks' own cargo calls stay in the group.
