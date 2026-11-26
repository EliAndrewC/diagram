---
kind: adopted
title: a pool tree is pre-warmed when it is handed out
for: a builder's first test run in a warm pool tree compiles its own edit alone, because the test builds of the crates others moved since the tree's last handout were built while it read
measured: 2026-11-26
measurement: in the pool tree diagram-backlog-t269 - after a handout whose 14 commits moved three gate crates, the first make rust-test of rust/gate/crates/land took 18.6 s, 7.2 s of it the test build, and the second 0.32 s; with the core crate made to rebuild, the first run's test build took 7.7 s of 25.6 s with no pre-warm and 0.1 s of 9.2 s after a finished one; that pre-warm built 34 crates in 402 s; a real run started in the tree during a pre-warm ended it 9 times of 9; under its first form, which waited for a waiter's mark, two real runs of other trees waited 39.3 s and 25.2 s behind it, and the spare-slot rule replaced it; under the spare rule, one of the two slots taken by hand beside a running pre-warm (flock on the slot's file, held 12 s) cut its build 0.09 s later and it asked the crate again 0.2 s after the slot was let go (no real compile of another tree fell in that span: that case is the test's alone); THAT CUT WAS REMOVED by 451 T336 - a test build killed past rustc's front end left the crate's finished incremental session written into and the next build of the crate failed to link (rust-lld: undefined hidden symbol) until its incremental directories were removed: on rust/guard in the pool tree diagram-backlog-t270, 29 of 54 tries with a build cut failed so (SIGTERM 16 of 31, SIGKILL 7 of 10, SIGINT 6 of 13) and 0 of 20 left to finish (dev/measurements/2026-11-26/prewarm-link/); of the 160 crates pre-warmed that day (every prewarm Phase line, code 0) the median took 2.0 s, nine in ten under 13.0 s, the longest 82.7 s (rust/mode_a) - what a real run can now wait for the rest of
command: make rust-test CRATE=rust/gate/crates/rustc (rustc::tests::prewarm); make rust-test CRATE=rust/gate/crates/task (builder_tree::tests); the Phase lines of .git/l7r-events/ whose step is prewarm, beside the build and slot-wait lines of the same tree and hour; a tree's prewarm.log in its git directory; a wait behind a pre-warm is another tree's slot-wait line whose span overlaps a prewarm line's (a slot-wait line names no holder)
falsifier: a test build that fails to link (rust-lld: undefined hidden symbol; a link-heal Phase line) in a tree whose only earlier builds were its pre-warm's and real runs left to finish - the pre-warm still breaks a session; a real run's wait behind a pre-warm finishing its crate past the bound below (another tree's slot-wait Phase line overlapping a prewarm line, or a tree's own build line beginning inside one: the wait on cargo's build-directory lock); the first test run after a handout no faster with the pre-warm than without (its build Phase seconds, a handout that moved the same crates, L7R_PREWARM=0 against on); the slot waits of real runs rising with it on (a day's slot-wait Phase seconds against a day with L7R_PREWARM=0); or a pre-warm found starting a crate past its ceiling
threshold: one link failure after a pre-warm with no build killed in that tree; one real run's wait past 90 s behind a pre-warm's crate (GUESS, a knob: just past the longest crate pre-warmed on 2026-11-26, 82.7 s - a longer wait is more than one crate's rest), or more than one in ten such waits past 13 s (GUESS: that day's ninth decile); one handout whose first run's build seconds are no lower with the pre-warm finished; or a day's slot-wait seconds higher with it on than off (any reopens it)
cost: the compile itself, on the machine while the builder reads - every moved crate and every crate that builds on one, built whether or not the builder will test it, up to the ceiling (900 s) unless a real run ends it; ACCEPTED with 451 T336 (the builder's choice on the measurement, the brief's direction): a real run started in its tree waits on cargo's build-directory lock, and a compile of another tree can wait in the slots' queue, for the REST OF ONE CRATE (median crate 2.0 s, nine in ten under 13.0 s, longest 82.7 s), where the first form's promise was a poll - the alternatives priced: cut and then drop the crate's incremental directories (a 22 to 44 s rebuild of rust/guard from nothing against its 11 s incremental build, more than the pre-warm buys), give the slot back but keep compiling (a third compile at once, the memory peak the slots exist to stop), heal only (every cut still costs a from-nothing rebuild, and 29 of 54 cuts needed one), CARGO_INCREMENTAL=0 for the pre-warm (never breaks a session, 0 of 20, but it is another artifact set: 36.2 s to build and the real build after it still compiled 12.2 s against 0.08 s fresh); it starts a crate only while a slot is spare, so little beside two busy trees; one flock program a slot at each look and one read of the run record every half second while it runs, and a look can make a real call's own look read held, a poll's wait
last-audited: 2026-11-26
cadence-days: 30
covers: rust/gate/crates/rustc/src/rustc/prewarm.rs
covers: CEILING_S
covers: POLL
covers: rust/gate/crates/rustc/src/rustc/stale.rs
covers: LOCK_S
---

451 T316 (`rust/gate/crates/rustc/src/rustc/prewarm.rs`, started by `rust/gate/crates/task/src/builder_tree.rs`; the spare
look in `rust/gate/crates/rustc/src/rustc/slot.rs`). The GM, 2026-11-26: "would it make sense to begin compiling immediately
within a work tree builder?" A warm handout (`make builder-tree`) starts, detached, `l7r-gate rust prewarm --since <the commit
of the tree's last handout>`: one `cargo test --no-run` for each crate whose build reads a file the commits since changed, a crate
before the crates that build on it, with the words and environment of a real run's first step, so that run finds the build fresh.

**It starts a crate only while a slot is spare, and never cuts one in flight (451 T336).** It takes a build slot only where one
is free at that instant and a second is free beside it, and never waits in the slots' queue. BEFORE each crate it looks: a real
run of the checks in its tree (a live member of the run lock's record) ends it, and so does its ceiling; with no slot spare it
starts nothing and looks again every half second until two are free. A crate's build once started runs to its end, its slot held
until then, whatever starts beside it: the first form killed its cargo the moment a real run started or the last slot was taken,
and a rustc killed past its front end can leave the crate's finished incremental session written into, so that every later link
of the crate fails until its incremental directories are removed (the measurement above; that the working session's files are
hard links of the finished one's is inferred, not read in rustc). Its cargo is a process group of its own, so a signal to the
pre-warm's group does not reach it either. Each crate's line in `prewarm.log` says the seconds it ran on after the moment the
first form would have cut it. It reads the slots' own locks, so every tree's compiles are seen whatever slot code the tree runs.
With one slot on the machine it builds nothing. Do not bring the kill back to shorten the wait: the gate's test build heals this
link error once (`rust/gate/crates/rustc/src/rustc/stale.rs`, a `link-heal` Phase line), at the price of the crate compiled from
nothing.

**The knobs are GUESSES.** The ceiling (900 s, `L7R_PREWARM_CEILING`) is the slot's own, and is looked at between crates; the poll (0.5 s) the slot's and the run
lock's. `L7R_PREWARM=0` is no pre-warm.

**The heal's knob is a GUESS.** `LOCK_S` (120 s, `stale.rs`): how long a healing test build waits for cargo's lock of the build
directory before it drops anything - past the longest crate pre-warmed on 2026-11-26, 82.7 s, which a pre-warm finishing its
crate in the tree can hold the lock for. Its falsifier is this entry's: a `link-heal` line after a pre-warm with no killed build.

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

**Not booked by `make task-time` yet.** Its `Phase` lines (step `prewarm`, cargo's own code; 130 on the lines of 2026-11-26 the first form cut short) are booked to no call, so
they are in no builder's compile; a category that shows them by task is T317.

Weighed and not taken: the take-time HEAD as the base (a release brings the tree to HEAD too, so the next handout would see
nothing moved); the pre-warm inside the slots' queue (`slot::around`: it would hold a place a real run wants and write `slot-wait`
lines that are nobody's wait); the run lock joined (a real run would wait on the pre-warm, the opposite of the point); every
crate with no kept result warmed (a builder's tree keeps results only for the crates it tested, so every handout would build the
workspace).
