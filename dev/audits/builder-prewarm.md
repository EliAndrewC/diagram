---
kind: adopted
title: a pool tree is pre-warmed when it is handed out
for: a builder's first test run in a warm pool tree compiles its own edit alone, because the test builds of the crates others moved since the tree's last handout were built while it read
measured: 2026-11-26
measurement: in the pool tree diagram-backlog-t269 - after a handout whose 14 commits moved three gate crates, the first make rust-test of rust/gate/crates/land took 18.6 s, 7.2 s of it the test build, and the second 0.32 s; with the core crate made to rebuild, the first run's test build took 7.7 s of 25.6 s with no pre-warm and 0.1 s of 9.2 s after a finished one; that pre-warm built 34 crates in 402 s; a real run started in the tree during a pre-warm ended it 9 times of 9; under its first form, which waited for a waiter's mark, two real runs of other trees waited 39.3 s and 25.2 s behind it, and the spare-slot rule replaced it; under the spare rule, one of the two slots taken by hand beside a running pre-warm (flock on the slot's file, held 12 s) cut its build 0.09 s later and it asked the crate again 0.2 s after the slot was let go (no real compile of another tree fell in that span: that case is the test's alone)
command: make rust-test CRATE=rust/gate/crates/rustc (rustc::tests::prewarm); make rust-test CRATE=rust/gate/crates/task (builder_tree::tests); the Phase lines of .git/l7r-events/ whose step is prewarm, beside the build and slot-wait lines of the same tree and hour; a tree's prewarm.log in its git directory; a wait behind a pre-warm is another tree's slot-wait line whose span overlaps a prewarm line's (a slot-wait line names no holder)
falsifier: the first test run after a handout no faster with the pre-warm than without (its build Phase seconds, a handout that moved the same crates, L7R_PREWARM=0 against on), the slot waits of real runs rising with it on (the slot-wait Phase seconds of a day's builders against a day with L7R_PREWARM=0), a slot-wait line longer than a few seconds whose holder was signed pre-warm, or a pre-warm found running past its ceiling
threshold: one handout whose first run's build seconds are no lower with the pre-warm finished, one slot-wait past 10 s behind a pre-warm, or a day's slot-wait seconds higher with it on than off (any reopens it)
cost: the compile itself, on the machine while the builder reads - every moved crate and every crate that builds on one, built whether or not the builder will test it, up to the ceiling (900 s) unless a real run ends it; a build cut short is compiled again; it builds only while a slot is spare, so little beside two busy trees; one flock program a slot at each look and one read of the run record every half second while it runs, and a look can make a real call's own look read held, a poll's wait
last-audited: 2026-11-26
cadence-days: 30
covers: rust/gate/crates/rustc/src/rustc/prewarm.rs
covers: CEILING_S
covers: POLL
---

451 T316 (`rust/gate/crates/rustc/src/rustc/prewarm.rs`, started by `rust/gate/crates/task/src/builder_tree.rs`; the spare
look in `rust/gate/crates/rustc/src/rustc/slot.rs`). The GM, 2026-11-26: "would it make sense to begin compiling immediately
within a work tree builder?" A warm handout (`make builder-tree`) starts, detached, `l7r-gate rust prewarm --since <the commit
of the tree's last handout>`: one `cargo test --no-run` for each crate whose build reads a file the commits since changed, a crate
before the crates that build on it, with the words and environment of a real run's first step, so that run finds the build fresh.

**It holds a slot only while another is spare.** It takes a build slot only where one is free at that instant and a second is
free beside it, and never waits in the slots' queue. While its cargo runs it looks every half second: a real run of the checks
in its tree (a live member of the run lock's record) ends it, and once no slot is spare - a compile of any tree took the last -
it kills its cargo, gives its slot back and builds the crate again when two are free. It reads the slots' own locks, so every
tree's compiles are seen whatever slot code the tree runs. So the next compile to start finds a slot, and the longest one waits
behind a pre-warm is a poll and the time cargo takes to die. With one slot on the machine it builds nothing.

**The knobs are GUESSES.** The ceiling (900 s, `L7R_PREWARM_CEILING`) is the slot's own; the poll (0.5 s) the slot's and the run
lock's. `L7R_PREWARM=0` is no pre-warm.

**What it does not warm.** The lint's build (clippy's artifacts are another build; T318) and a coverage build. A cold tree, whose
whole cache is empty: its handout says so and starts nothing.

**What the gain follows.** What moved. On the handout measured (three small gate crates moved) the first run's test build was 7.2 s of 18.6 s;
with the core crate moved it was 7.7 s without the pre-warm and 0.1 s after it, and the wall time fell from 25.6 s to 9.2 s, most
of that the wrapper's own tool build, which the pre-warm's start also does. The 191 to 531 s first closing-checks runs that
prompted it were coverage builds and lint, which it does not warm.

**The first form waited on a mark and was replaced.** A waiting call left a file the pre-warm read; two runs of trees on the
older slot code, which left none, waited 39.3 s and 25.2 s on a slot while a pre-warm held one (measured 2026-11-26; that they
waited on the pre-warm's slot and not the other is inferred from the spans). The spare rule needs nothing of the other trees.
One real run of nine that ended a pre-warm failed in its tests and passed when run again, unexplained (T329); a second such red
reopens this.

**Not booked by `make task-time` yet.** Its `Phase` lines (step `prewarm`, code 130 where cut short) are booked to no call, so
they are in no builder's compile; a category that shows them by task is T317.

Weighed and not taken: the take-time HEAD as the base (a release brings the tree to HEAD too, so the next handout would see
nothing moved); the pre-warm inside the slots' queue (`slot::around`: it would hold a place a real run wants and write `slot-wait`
lines that are nobody's wait); the run lock joined (a real run would wait on the pre-warm, the opposite of the point); every
crate with no kept result warmed (a builder's tree keeps results only for the crates it tested, so every handout would build the
workspace).
