# 451 T347: the small lane in the built tool - the wait before and after, the telling's cost, one real-tree negative

Measured 2026-11-26, 22:35-23:00 UTC, in the pool tree `diagram-backlog-t269`, one run at a time, load 1.9 to 24.7 on 22 cores.
The script is `lane-wait.sh` beside this file: T315's body edit of one file (a statement with a new value at the head of its
first function body), two holders `flock <slot file> sleep 60` on both wide slots (nothing compiling, no load generator), then
`make rust-test CRATE=rust/gate/crates/reviews`, the run's `Phase` lines read from the event log; the file is put back by
`git checkout`. The slot files were a SCRATCH directory's (`L7R_BUILD_SLOT_DIR`), so no other tree's build was held and no
other tree's holder is in a figure: the mechanism is the same, the directory alone differs.

| run | tool | holders | telling (`slot-tell`) | wide wait (`slot-wait`) | lane (`slot-small`) | build span s | make wall s |
|---|---|---|---|---|---|---|---|
| before1 | before the change | 2 x 60 s | - | 59.98 s | - | 62.15 | 63.9 |
| before2 | before the change | 2 x 60 s | - | 59.97 s | - | 62.42 | 64.5 |
| knob-off | built, `L7R_BUILD_SLOTS_SMALL=0` | 2 x 60 s | none asked | 60.00 s | - | 62.16 | 63.9 |
| held1 | built | 2 x 60 s | alone, 5 ms | none | 1 ms | 2.24 | 3.99 |
| held2 | built | 2 x 60 s | alone, 6 ms | none | 1 ms | 2.24 | 7.13 |
| held3 | built | 2 x 60 s | alone, 6 ms | none | 2 ms | 2.15 | 3.88 |
| negative (body edit of `rust/gate/crates/core/src/difflib.rs`) | built | 2 x 60 s | NOT alone, 6 ms | 56.43 s | - | 60.69 | 65.7 |
| after-negative-1 (`difflib.rs` put back: its time moved) | built | none | NOT alone, 5 ms | none (slots free) | - | 4.10 | 9.0 |
| after-negative-2 | built | none | alone, 6 ms | none | 2 ms | 2.19 | 3.9 |

The build span holds its wait; the wall holds the launcher, the telling, the build and the 1.3 s test run (held2's 7.1 s: the
launcher rebuilt nothing; not looked into, one run).

**The telling's cost: 4 to 7 ms** over the sixteen tellings of `reviews` on the real tree, read from the event log's
`slot-tell` lines (6, 6, 6, 5, 5, 5, 6, 4, 6, 5, 6, 6, 6, 5, 6, 7 ms; the stamps are whole milliseconds; the table's rows are
nine of them, the others the runs that found the defect below and one run of `lane-wait.sh` as it is kept here). `reviews`
builds from three crates (`core`, `pool`, `guard/shared`); its key text is about 220 lines (222 counted before the fix below).

**The first run after the tool is rebuilt was told wrongly wide, found here and fixed.** Before the fix the first TWO runs
after each rebuild of `l7r-rust` were wide: the files a Rust file compiles in were read by a pattern whose path could span
lines, `core/src/build.rs` names the macros in strings, and the kept code views (a line a file) gave that "path" back cut at
its first line - so the key read fresh and the key read from the kept views differed (the two key texts differed in that one
entry). With the pattern held to one line (`kept.rs`, `INCLUDE`) the run after the first wide build is told alone
(`fixed-establish` wide, `fixed-second` alone).

## Two builds at once, and a real build queued in the lane (the closing half, 2026-11-26, 23:10-23:13 UTC)

The script is `lane-pair.sh` beside this file; the slot files a scratch directory's again, both wide slots held by
`flock <slot file> sleep 30`, load 14.3 to 16.5 on 22 cores. Seconds are from the two runs' start, read from the `Phase` lines.

| run | what ran | telling | wide wait | lane wait (`slot-wait`, then `slot-small`) | build span s | started at s |
|---|---|---|---|---|---|---|
| pair1, `plan` | body edits of `reviews` (`census.rs`) and `plan` (`status.rs`), `make rust-test` of each started together, `plan` into a target directory of its own (`CARGO_TARGET_DIR`), both keys warm | alone, 5 ms | none | none, 2 ms | 8.62 | +0.32 |
| pair1, `reviews` | the same run's other build | alone, 6 ms | none | none, 1 ms | 2.84 | +11.64 |
| lane1, `reviews` | one body-edit run, the LANE's own file held too (`flock small-0 sleep 10`) beside the two wide holders | alone, 6 ms | none | 10.05 s (`slot-wait` code 0, no crate), then `slot-small` code 0 of 10.05 s | 12.41 | +0.36 |

**Two runs of one tree never meet in the lane.** pair1's `reviews` run waited for `plan`'s whole run (its log: `rust-checks:
waiting 0 s for ~/.cache/l7r-cargo-target/diagram-backlog-t269, held by ... the run make rust-test CRATE=rust/gate/crates/plan`):
a run joins the run lock in its tree's own target directory as well as the one `CARGO_TARGET_DIR` names (`runlock.rs`,
`dirs_of`), so a second target directory does not let two runs of a tree build at once. Neither waited for a wide slot, 30 s
held, and each took the lane. So the lane queues builds of two TREES only, and a builder's tree is held to this one: lane1
shows that queue with one real build behind a held lane - a `slot-wait` line of the lane's wait, then the `slot-small` line of
the same span, then the build, and no wide wait.

NOT measured: the lane under real load beside two compiling wide holders (the memory falsifier is the audit's, read by
`make sampler-report`); two real small builds of two trees queued on the lane, each compiling (one tree cannot start them, as
above: a real build behind a `flock` holder, and fixtures, only); `make task-time`'s `waiting on a build
slot` minutes after a day with the lane (before: 1.0 minutes, 0.7 blocking, over the 24 h to 2026-11-26 21:19 UTC, twelve
`slot-wait` lines). The day after is 451 T380's to read.
