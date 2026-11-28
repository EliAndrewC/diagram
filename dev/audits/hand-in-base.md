---
kind: adopted
title: the base a hand-in applies a builder's work onto
for: make builder-done's hand-in (l7r-gate land --hand-in) applies the builder's scratch commit onto HAND_IN_BASE - origin, origin/main after git fetch origin (the default since 461 T22, phase 2, when landings leave the clone), or clone, the clone's HEAD (phase 1, while the session still carries into its clone); read once, by l7r_shared::builder_pool::hand_in_base, for the hand-in, its runner start, the handout's D13 refusal and make builder-trees - a knob set by phase, not measured (461 plan D3, "The base by phase")
measured: 2026-11-27
measurement: none yet - 461 T10 hands in this feature's next task through make builder-done (base clone) and counts the landings refused before a gate over phase 1 against the night of 2026-11-26/27's 19 of 50 (spec, Why)
command: make rust-test CRATE=rust/gate/crates/land ONLY="land::hand_in::tests"
falsifier: in phase 1, a hand-in applied onto the clone's HEAD that a later make land in the clone still meets a carry conflict on (the base was not where work lands); from phase 2, one applied onto origin/main that the lane's batch meets a conflict on
threshold: one such conflict a week (it reopens the knob)
cost: for origin, one git fetch a hand-in (none for clone); the knob read once a hand-in, and by the coordinator's Stop rule and make lane-wait (l7r_shared::lane_wake::origin_base, 461 T56 and T64) - from origin, a waiting hand-in no runner serves holds the stop and is said once by the wait, at most one git for-each-ref a Stop and a 5 s poll with no runner
last-audited: 2026-11-27
cadence-days: 30
covers: HAND_IN_BASE
---

461 T07 (`rust/gate/crates/land/src/land/hand_in.rs`): the hand-in finds its base before it makes the scratch commit, so a
failed fetch refuses with nothing done; any other value of the knob is refused naming both. Weighed in the plan (D3) and not
taken: `origin/main` in phase 1 (it would build on a main without the staged work the tree was handed out on, and D13 would
refuse every handout while a batch stood staged); the lane's tip (work the lane may yet eject).
