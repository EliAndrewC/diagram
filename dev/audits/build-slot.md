---
kind: adopted
title: compiling cargo calls take a machine-wide build slot
for: the number of builders at once is not capped by the chance that their compiles and a landing's gate coincide, because at most L7R_BUILD_SLOTS compiling cargo calls of the checks run at once on the machine, whatever tree starts them
measured: 2026-11-26
measurement: the three-builder run's samples joined with the checks' Phase lines (2,602 s, 292 samples, 380 phase lines) - all twelve of the highest memory samples (5.9-6.4 GiB anonymous of the container's 10) and seven of the eight highest rustc counts (39-46) fell where all three trees were in a coverage build at once; the machine ran three compiling steps at once for 1,396 s, two for 509 s, one for 631 s; coverage builds were 57.9 of the window's phase minutes, lint 33.2, test builds 6.2, cargo fmt 1.1; one tree's own closing checks never ran two compiling cargo calls at once (its five at once are coverage runs, tests, not compiles); for the small lane (451 T347), dev/measurements/2026-11-26/small-build-memory/results.md (a test build of one crate alone 0.19-0.64 GiB anonymous after a body edit, 1.42 GiB at the most, two rustc at once, sampled from /proc every 20 ms) and lane-results.md beside it (both wide slots held by flock for 60 s: a body-edit test build of rust/gate/crates/reviews waited 59.98 and 59.97 s before the lane and 1-2 ms in it, three runs; the telling 4-7 ms); for the lint in the lane (451 T355), dev/measurements/2026-11-27/lint-memory/results.md (a clippy pass of one crate alone 0.08-0.37 GiB anonymous after a body edit, 0.66 GiB at the most, one to three clippy-driver at once and no link, sampled the same way by pass; both wide slots held by flock for 60 s: the lint of rust/gate/crates/reviews in make builder-checks waited 55.5 and 49.9 s before and 1-2 ms for the lane after, three runs; the telling 5-10 ms a pass)
command: python3 dev/measurements/2026-11-26/builder-count/slot-coincide.py (the join; a later run's samples as its second argument, and its last line counts the slot waits); make rust-test CRATE=rust/gate/crates/rustc (rustc::tests::slot); make task-time (the category waiting on a build slot beside compile); for the small lane, OUT=<a scratch directory> dev/measurements/2026-11-26/small-build-memory/lane-wait.sh <label> (its slot-tell, slot-wait and slot-small lines; lane-pair.sh <label> lane beside it for one real build queued behind a held lane - two runs of one tree take turns on the run lock and never meet in the lane) and make rust-test CRATE=rust/gate/crates/rustc (rustc::tests::alone); for the lint, OUT=<a scratch directory> dev/measurements/2026-11-27/lint-memory/lint-wait.sh <label> (make builder-checks' slot lines) and rustc::tests::lint
falsifier: the slot's waiting minutes exceeding the compile minutes it saves by make task-time (three builders' compile and waiting-on-a-build-slot minutes summed, against the same builders' compile minutes with L7R_BUILD_SLOTS=0), closing checks at three builders no faster with the slot than without, a memory sample past 6.4 GiB anonymous with the slot on, or a cargo call that ran without a slot at the ceiling; for the small lane (451 T347, its section below): an OOM kill or anonymous memory over the 7 GiB margin with a slot-small build running, a slot-small build seen with more than two rustc (a lint pass: more clippy-driver than the crate has targets, three at the most in this workspace), or lane waits past the wide waits the lane saved
threshold: one re-measured three-builder run in which slot waits plus compile exceed the compile minutes of the unslotted run, or one ceiling line (rust-checks: waited ... on a build slot, the ceiling) in a week (either reopens the count; the first also reopens the slot); for the small lane, one OOM kill or one sample over 7 GiB anonymous while a slot-small build runs, or one slot-small build seen with more than two rustc - for a lint pass, more clippy-driver than its crate's targets, three at the most (either reopens the telling and the lane's width of one), or a day whose slot-wait lines followed by a slot-small line sum past the sum of the twelve slot-wait lines of 2026-11-26, the wide waits the lane was built to remove (both sums read from the event log's Phase lines; 451 T380 reads the first day: reopens the width)
cost: a wait where compiles coincide, booked as its own category; one flock program started a slot at each look (every half second while waiting, once where a slot is free); the wrapper's own tool build and a hook suite's guard build take no slot (measured at most 2.6 GiB and 13 rustc where no phase ran)
last-audited: 2026-11-26
cadence-days: 30
covers: rust/gate/crates/rustc/src/rustc/slot.rs
covers: DEFAULT
covers: CEILING_S
covers: POLL
covers: SMALL_DEFAULT
covers: rust/gate/crates/rustc/src/rustc/kept/alone.rs
covers: rust/gate/crates/rustc/src/rustc/lint.rs
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

## The small lane (451 T347)

A builder's test build of one crate waited its turn behind coverage builds: four runs of `rust/gate/crates/reviews` after a body
edit waited 57.3, 18.2, 2.5 and 34.9 s for a wide slot for compiles of 2.3 to 4.0 s. Measured 2026-11-26
(`dev/measurements/2026-11-26/small-build-memory/results.md`): a test build that compiles ONE crate alone, its dependencies
fresh, is 0.19-0.64 GiB anonymous after a body edit and 1.42 GiB at the most (every source of `rust/mode_a`), two rustc at
once; a wide slot's own kind of build is 2.0 GiB a tree at three at once and a dozen rustc.

**A lane one wide, not a skip.** A build told to be of that class (below) takes one of `L7R_BUILD_SLOTS_SMALL` places - files
`small-<i>` beside the `slot-<i>` - and never a wide slot, so it waits only behind another of its kind. The width is 1, a GUESS
knob (`SMALL_DEFAULT`): the budget is 1.4 GiB of sessions and two wide builds at 2.0 against a 7 GiB margin (itself a GUESS
knob, `L7R_MEM_MARGIN_GIB`), which leaves 1.6 - one build at the class's ceiling, not two (2.8). A lane also bounds a WRONG
telling, as no slot at all would not: at the worst three large builds at once, 3 x 2.0 + 1.4 = 7.4 GiB of the container's 10.
`L7R_BUILD_SLOTS_SMALL=0` is no lane (such a build takes a wide slot, as before the lane); with no wide slots
(`L7R_BUILD_SLOTS=0`, a run under a holder) there is no lane either.

**The telling** (`rust/gate/crates/rustc/src/rustc/kept/alone.rs`), asked once a crate a run beside the binary key's build:
a KEY - the content ids of every file of the crates it builds from by path and of the files those compile in, the workspace's
manifests, lockfile and `.cargo/config.toml`, its own `Cargo.toml`, the compiler, the build's words and the `RUSTFLAGS` and
`CARGO_ENCODED_RUSTFLAGS` it inherits; not its own sources - kept in the target directory the build writes
(`<target>/l7r-alone/<crate>-<check>`), TOGETHER WITH the times: every such file older than the key's file, whose time is the
start of the build that kept it. Content alone is not enough: cargo judges a path crate by its files' times (a dependency's
file put back by `git checkout` at its committed content recompiled it, the record's run `w`). The same answer stands at both
slotted calls of a test run: the binary key's build (`kept.rs`) and a red build's second asking (`stepped`, through
`stale.rs`); a heal's second build is a wide one. A build told alone that fails leaves its key (no dependency moved), so the
run after a red build is told alone again; a wide build keeps its key only where it passes. Not told, so wide: the first build
in a target directory, a fresh run (`FRESH=1`), a run outside a repository, `test-no-counters`, the pre-warm's builds, the
doctests' `cargo test --doc`, `make test-times`.

**What is counted.** `slot-tell`: one `Phase` line a telling, its span the telling's cost, its code 0 where the build was told
alone and 1 where not. `slot-small`: one line a build that took the lane, its span its wait for the lane, its code 1 where it
ran without (no `flock`, the ceiling). A wait in the lane is a `slot-wait` line like a wide wait - so `make task-time` books it
as `waiting on a build slot` - and is told from one by the `slot-small` line of the same span and tree that follows it. The
readers book `slot-tell` and `slot-small` to no category.

**Measured in the built tool, 2026-11-26** (pool tree `diagram-backlog-t269`, a scratch slot directory through
`L7R_BUILD_SLOT_DIR` so no other tree's builds were held; both wide slots held by `flock <slot file> sleep 60`, nothing
compiling; a body edit of `rust/gate/crates/reviews/src/reviews/census.rs`, then `make rust-test
CRATE=rust/gate/crates/reviews`): with the lane off (the tool before the change, twice, and `L7R_BUILD_SLOTS_SMALL=0` after it) the build waited 59.98, 59.97
and 60.00 s for a wide slot and the run took 63.9, 64.5 and 63.9 s; with the lane, three runs waited on no wide slot and 1 to 2
ms for the lane and took 3.99, 7.13 and 3.88 s. The telling cost 4 to 7 ms a crate (sixteen tellings; `reviews` builds from
three crates, about 220 key lines). One negative on the real graph: a body edit of `rust/gate/crates/core/src/difflib.rs` was NOT
told alone (`slot-tell` code 1) and waited 56.4 s for a wide slot; the file put back by `git checkout` (its time moved, its
content as committed) was not told alone either, and the run after that wide build was. The record:
`dev/measurements/2026-11-26/small-build-memory/lane-results.md`.

**Falsifier** (any one reopens the lane or its telling): an OOM kill, or a sample of anonymous memory over the 7 GiB margin,
with a `slot-small` build running (`make sampler-report` over the window of the `slot-small` lines); a `slot-small` build seen
with more than two rustc at once, or a lint pass with more `clippy-driver` than its crate has targets - its library, its
tests, a binary: three at the most in this workspace, counted 2026-11-27 (a wrong telling); lane waits (`slot-small` spans) summing past the wide waits the lane saved
in a `make task-time` window (the lane too narrow: widen it only with the wide holders measured under 2.0 GiB each).

**The lint in the lane (451 T355, `rust/gate/crates/rustc/src/rustc/lint.rs`).** Until 2026-11-27 every clippy pass took a wide
slot whatever it compiled. Measured that day (`dev/measurements/2026-11-27/lint-memory/results.md`, T347's sampler with
`clippy-driver` counted and each pass read from the live `cargo clippy`'s words): a pass that compiles one crate alone is 0.08
to 0.37 GiB anonymous after a body edit (1 to 8 s) and 0.66 GiB at the most (every source of `rust/mode_a`, 17 s), one to three
`clippy-driver` at once - the library, then its tests and its binary - and no link: under the test build's class at every
point, so it takes the SAME lane under the same budget, in a test build's place and never beside one (the lane is one wide).
The telling is the test build's kind and not the test build's own: after a dependency's body edit and a green test build, whose
key then stood, the lint compiled the dependency again (clippy's check units have their own fingerprints), and the `--lib` pass
compiled the dependencies again straight after the `--all-targets` pass had. So EACH PASS keeps a key of its own, named by its
words (`<crate>-lint--all-targets`, `...--all-targets--all-features`, `...--lib`) and holding them with `-D warnings`, and is
told alone only by what that pass last built; a pass told alone leaves its key, red or green, and a wide pass keeps its key
only where it passes. A fresh run's lint is told like any other (cargo's fingerprints know nothing of `FRESH=1`); outside a
repository nothing is told. Its `slot-tell` and `slot-small` lines are the test build's steps, told from them by the span they
lie in: the crate's `lint` line, where a test build's lie in its `build` line. In the built tool, both wide slots held for 60 s,
`make builder-checks CRATE=rust/gate/crates/reviews` after a body edit: the lint waited 55.5 and 49.9 s before (the runs 65.8
and 63.9 s) and 1 to 2 ms for the lane after, three runs (8.9, 7.7 and 7.9 s); a telling costs 5 to 10 ms a pass; a body edit
of `core` with one of `reviews` was told wide at both passes, wide again once the file was put back, and alone on the run after.
Still wide: the first lint of a crate in a target directory - so a builder's first after a handout, since the pre-warm runs no
lint (451 T367) - and the lint after a dependency's edit, a put-back or a red wide pass.

**Owed, 451 T380:** `make task-time`'s `waiting on a build slot` minutes over the first 24 h with the lane live, against
the 1.0 minutes (0.7 blocking) of the 24 h to 2026-11-26 21:19 UTC, with the day's `slot-tell` and `slot-small` counts; and
why that minute is under the sum of the day's twelve `slot-wait` lines. Also not measured: two compiling small builds of two
trees queued on the lane (one tree's two runs take turns on the run lock first; `lane-results.md`).

Weighed and not taken: no slot at all for the class (no ceiling on a wrong telling); cargo's `--unit-graph` or build plan
(unstable flags the pinned toolchain refuses); reading cargo's fingerprints (an internal format); the verdict key itself (one
hash, which also holds what the tests read at run time).
