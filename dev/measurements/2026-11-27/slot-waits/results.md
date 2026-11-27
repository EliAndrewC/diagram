# The wide build waits left after the small lane (451 T420)

Load this file when: weighing the build slots' count (`L7R_BUILD_SLOTS`), the small lane's width or overflow
(`L7R_BUILD_SLOTS_SMALL`), the pre-warm's slot use, or reading `slot-wait` seconds from the event log.

Measured 2026-11-27, read-only, from the clone's event logs (`/diagram/.clones/diagram-backlog/.git/l7r-events/*.jsonl`, every
feature's, a line written to two logs counted once) and the pool's log, over **2026-11-27T00:20Z (T347 landed) to 03:56:52Z (this
tree's handout for T420), 3.61 h**. Script `waits.py` (run: `python3 -I waits.py > waits.txt`), its output `waits.txt`; the
dependency rebuilds by `dep-run.sh` with this folder's `mem-sample.py` (T347's sampler, plus each rustc's `--crate-name`) and
T347's `windows.py`, their logs `rust_gate*-core-edit.log` and the rustc units each compiled `*.tsv.crates`.

## The finding: the task's premise was a measurement's own waits

T367's record counted 13 `slot-wait` lines, 283.5 s, from 00:20Z to 03:30Z, 279.5 s of them "in later builds of a tree (mostly
`rust/gate/crates/reviews` at 01:49 to 02:00, while a gate ran)". **221.9 s of those were not contention**: the four waits of
55.5, 49.9, 56.4 and 60.0 s are 451 T355's `lint-wait.sh` (`dev/measurements/2026-11-27/lint-memory/lint-wait.sh`), which held both
wide slots of a SCRATCH slot directory with `flock <file> sleep 60` around a `make builder-checks` of `reviews`; its rows `before1`,
`before2`, `negative` and `knob-off` in `lint-memory/lint-wait-rows.txt` carry those very waits (55.498, 49.945, 56.413, 60.033 s).
The event log has no field that tells such a line from a real one, so `make task-time` books them as waiting too (filed: T426).
Of the rest, 54.6 s were waits for the SMALL LANE, not a wide slot.

| slot-wait lines, 00:20Z to 03:56:52Z | count | seconds | of 5 s or more |
|---|---|---|---|
| synthetic (T355's scratch slots) | 4 | 221.9 | 4, 221.9 s |
| real, for a wide slot | 3 | 7.1 | 0 |
| real, for the small lane | 13 | 87.4 | 6, 78.3 s |

## (1) Each wide wait

No REAL wide wait reached 5 s. All three, with the build each lay in and what told it wide (the `slot-tell` line before it; the
reason for a later build is read from the `Edit`/`Write` events in its tree since its crate's last build):

| at | wait s | tree | make | build | ran after s | told wide by |
|---|---|---|---|---|---|---|
| 00:28:03 | 1.5 | t270 | builder-checks | lint `guard/shared` | 14.5 | untold: a lint before T355's lane (about 01:53Z) told no pass |
| 01:45:33 | 1.5 | clone | builder-checks | test build `rust/gate` | 13.2 | no edit in the clone since its last build: a carry or landing moved files |
| 03:19:22 | 4.0 | t270 | builder-checks | test build `gate/crates/plan` | 1.5 | the crate's first build after the handout |

None was "after a dependency's edit" by a builder's own `Edit`. The four synthetic waits, read the same way, would have said
"told alone, but waited wide" - their slots were the script's.

## (2) Who held the two wide slots

During the real wide waits (15.1 slot-s, two slots times 7.1 s; every slot-second accounted for, none unseen):

| holder | where | make | slot-s | share |
|---|---|---|---|---|
| lint pass told wide | pool tree | builder-checks | 4.0 | 27% |
| test build told wide | pool tree | builder-checks | 3.9 | 26% |
| pre-warm | pool tree | prewarm | 2.6 | 17% |
| test build told wide | pool tree | rust-test | 1.5 | 10% |
| lint pass | pool tree | rust-lint | 1.5 | 10% |
| lint pass | pool tree | crate-checks | 1.5 | 10% |

No batch gate's coverage build held a slot during a real wide wait. Over the whole window (spans summed, minutes): pre-warm 27.4,
lint passes in pool trees 18.2 (builder-checks 11.2, rust-lint 7.0), the batch gate's coverage builds 7.2 and its lint 6.6, test
builds in pool trees 11.6 and in the clone 3.8; seconds with 0 / 1 / 2 wide holders: 8,983 / 3,523 / 455, never three.

**The holder model** (in `waits.py`'s head): a `build` span told wide (its own wait cut off), a `lint` span (dropped where every
pass took the lane), a `cover-build` span, a `prewarm` span. A `test` span holds none: `make rust-test` and `builder-checks` run
tests side by side (`rustc.rs` `owed_together`, `side.rs`), the executables by `run_in`; only a crate's doc tests take a slot,
which the line does not say. T355's `lint-run.sh` (`L7R_BUILD_SLOTS=0`, 01:40-01:48Z) and `lint-wait.sh` (scratch slots,
01:48:50-02:01:30Z) runs in t270 are left out as holders: they held no real slot. With them in, the model saw three holders at
once for 155 s; without, never.

**The lane's waits** (the real waiting), each held by ONE build told alone in another tree: `guard/shared` 43.7 s of the waits
(alone-told builds of 24.9 and 27.7 s, after edits that included its `lib.rs`), `gate/crates/measure` 17.7 s (18.3 and 20.0 s
builds), `plan` 9.7, `task` 6.1, `land` 4.6, a lint pass of `plan` 1.4. The lane's 169 builds in the window: median 2.8 s,
longest 28.4 s, 27 over 10 s. Two waiters at once only at 01:30:19-20 (0.5 s and 5.0 s).

## (3) The dependency rebuild

This tree, one build at a time, no load generator, the build slot ON (each took a wide slot as a builder's does; neither waited),
load 9.0-9.2 on 22 cores, the container's anonymous memory 0.78-0.84 GiB at the start. A body edit of
`rust/gate/crates/core/src/difflib.rs` (T347's edit: a statement at the head of the first function body), put back after; a warm
run of each crate first, unedited (0.09-0.11 s builds, nothing compiled).

| case | build s | rustc units | crates compiled | anon MiB | rss MiB | rustc at once | linkers |
|---|---|---|---|---|---|---|---|
| A: `make rust-test CRATE=rust/gate` after a `core` edit | 8.17 | 33 | 28: `core`, every gate crate (26), `rust/gate` | 749 | 1651 | 12 | 6 |
| B: `make rust-test CRATE=rust/gate/crates/task` after a `core` edit | 3.70 | 15 | 12: `core`, `task` and the 10 gate crates `task` builds on | 392 | 860 | 4 | 3 |

Both told wide (`slot-tell` code 1). Limits: a body edit only - an interface change would recompile more of each dependent; two
cases, as the brief caps.

## (4) The levers, priced

Per day = the window's figure times 24 / 3.61 = 6.65, on the GUESS that the window's builder load holds all day. T347's budget: sessions
1.4 + two wide holders at 2.0 = 5.4 GiB of a 7 GiB margin (GUESS knobs), the lane's room 1.6. The sampler over the window
(`make sampler-report SINCE=2026-11-27T00:20:00Z`, 1,359 samples to 04:06Z): anonymous memory median 0.79, 95th 1.91, peak 4.20 GiB;
never over the margin; no OOM kill.

| lever | waiting saved, window / day | memory | verdict |
|---|---|---|---|
| a third wide slot | at most 7.1 s / 47 s (every real wide wait) | paper 1.4 + 3 x 2.0 = 7.4 > 7: does not fit; measured peak 4.20 + 2.0 = 6.2 | not filed: nothing to save |
| the batch gate's coverage build taking one slot, not two | 0 | - | moot: it takes ONE already (`cover.rs`, one `around` a group); its 29 builds in the window never overlapped in one tree |
| a lane for one crate plus its changed dependencies | at most 1.5 s / 10 s (the one wide wait after files moved under a build) | case A 0.75 GiB, 12 rustc - a wide build's kind; a second lane beside the first: 1.4 + 4.0 + 1.42 + 0.75 = 7.6 > 7 | not filed |
| the pre-warm yielding its slot before a builder's build | at most 2.6 slot-s, about 1.3 s / 9 s | none | not filed: it already takes a slot only with another spare and yields between crates (T336) |
| **a build told alone takes a FREE wide slot when the lane is held** | **85.7 of 87.4 s / about 570 s** | a build of the class (1.42 GiB at most) in a wide slot's 2.0 room: inside the paper budget | **filed: T425** |
| a lane two wide | about 87 s / 578 s | paper 1.4 + 4.0 + 2 x 1.42 = 8.2 > 7: does not fit; at the body-edit figure (0.64 x 2) 6.7 | not filed: the overflow lever saves as much inside the budget |

**What would reopen the levers not filed:** real wide waits (`slot-wait` lines without a `slot-small` of the same start, and not
on a scratch slot directory once T426 marks those) passing about 5 minutes a day, read with `waits.py` over a new window.
