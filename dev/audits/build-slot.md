---
kind: adopted
title: compiling cargo calls take a machine-wide build slot
for: the number of builders at once is not capped by the chance that their compiles and a landing's gate coincide, because at most L7R_BUILD_SLOTS compiling cargo calls of the checks run at once on the machine, whatever tree starts them
measured: 2026-11-26
measurement: the three-builder run's samples joined with the checks' Phase lines (2,602 s, 292 samples, 380 phase lines) - all twelve of the highest memory samples (5.9-6.4 GiB anonymous of the container's 10) and seven of the eight highest rustc counts (39-46) fell where all three trees were in a coverage build at once; the machine ran three compiling steps at once for 1,396 s, two for 509 s, one for 631 s; coverage builds were 57.9 of the window's phase minutes, lint 33.2, test builds 6.2, cargo fmt 1.1; one tree's own closing checks never ran two compiling cargo calls at once (its five at once are coverage runs, tests, not compiles)
command: python3 dev/measurements/2026-11-26/builder-count/slot-coincide.py (the join; a later run's samples as its second argument, and its last line counts the slot waits); make rust-test CRATE=rust/gate/crates/rustc (rustc::tests::slot); make task-time (the category waiting on a build slot beside compile)
falsifier: the slot's waiting minutes exceeding the compile minutes it saves by make task-time (three builders' compile and waiting-on-a-build-slot minutes summed, against the same builders' compile minutes with L7R_BUILD_SLOTS=0), closing checks at three builders no faster with the slot than without, a memory sample past 6.4 GiB anonymous with the slot on, or a cargo call that ran without a slot at the ceiling
threshold: one re-measured three-builder run in which slot waits plus compile exceed the compile minutes of the unslotted run, or one ceiling line (rust-checks: waited ... on a build slot, the ceiling) in a week (either reopens the count; the first also reopens the slot)
cost: a wait where compiles coincide, booked as its own category; one flock program started a slot at each look (every half second while waiting, once where a slot is free); the wrapper's own tool build and a hook suite's guard build take no slot (measured at most 2.6 GiB and 13 rustc where no phase ran)
last-audited: 2026-11-26
cadence-days: 30
covers: rust/gate/crates/rustc/src/rustc/slot.rs
covers: DEFAULT
covers: CEILING_S
covers: POLL
---

451 T284 (`rust/gate/crates/rustc/src/rustc/slot.rs`; the readers' category in
`rust/gate/crates/measure/src/measure/where_time/columns.rs`). The GM, 2026-11-26: "wouldn't it be better to address that with some
synchronization rather than pre-emptively limiting builders just in case?" Each cargo call of `l7r-gate rust` that compiles - a
coverage build, a test build, a `cargo test`, clippy, a stage's `cargo run` - holds the `flock` of one of `L7R_BUILD_SLOTS` files
under `~/.cache/l7r-build-slots/` for its length; a builder's checks and a landing's gate run the same code, so they take the same
slots. A dead holder's slot is free at once (the lock is its open file's); the cargo a holder starts carries
`L7R_BUILD_SLOT_HELD`, so a gate run inside it takes none; `L7R_BUILD_SLOTS=0` is no slot; and a slot that cannot be taken (no
directory, no `flock`, the ceiling passed) is said and the call runs.

**The count is 2, a GUESS knob.** Three compiles at once is the peak the slot is there to stop: load median 42 on 22 cores says
the third added no throughput, and each of the three ran about 15 rustc at the peaks, so two fill the cores. Cargo's own `-j` is
left at a job a core: it bounds one call's rustc, not how many calls coincide. One slot was not measured. The ceiling (900 s) and
the poll (0.5 s) are GUESS knobs too.

**Waiters are not served in arrival order.** Each looks every half second, and a tree that lets a slot go takes one again the
instant its next compile starts, so under sustained load one waiter can wait long, to the ceiling at worst, with no holder hung.
Not measured; the re-measurement's `slot-wait` lines by tree are what would show it (one tree's waits far above the others'),
and a queue (a waiter's ticket file, lowest first) is the fix that was not built.

**What a step's span holds.** A coverage build's slot is taken before its phase's clock starts. A lint's, a test build's and a
test run's phase lines span their wait, and the readers take the `slot-wait` line out first (`PHASE_COLUMNS`' order), so
`make task-time` and `make where-time` book the wait once, as waiting; a script reading raw `Phase` lines subtracts the
`slot-wait` lines of the same tree.

Weighed and not taken: cargo's job limit alone (`-j` or `CARGO_BUILD_JOBS` lowered in every tree: it slows a lone builder for
all of its run to bound a coincidence that held 1,396 of 2,602 s, and bounds rustc, not the linkers and test binaries beside
them); a slot a tree holds for its whole checks run (the coverage runs and tests would queue too, which were not at the peaks);
a daemon or a jobserver shared across trees (a process to keep alive, against a lock a dead holder frees by itself); a slot
around the wrapper's tool build in `scripts/gates/l7r-gate.sh` (shell, no `Phase` line to book its wait by, and not at the
peaks - a candidate once the re-measurement shows it coinciding).
