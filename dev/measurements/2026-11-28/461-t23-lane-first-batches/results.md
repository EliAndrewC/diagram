# The lane's first real batches, 2026-11-28T02:00Z to 06:20Z (461 T23)

Phase 2 went live when T22 landed (tick 02:01:42Z). The questions: what the lane did with each batch (landed or ejected, and
why), how long it took, which stops needed the coordinator by hand, the lane's throughput once phase 3 was on main, the
coordinator's turns spent on landing before and after, and what is left for the lane to do by itself. Also the task line's
three figures: D1 (the lane tree's first gate), D9 (how long a background `make lane-wait` lives), D11 (whether any gate
still builds in the clone's own target directory).

Every figure here was re-derived from the outputs beside this file. Scripts (read-only, `python3 -I`):

| script | reads | output |
|---|---|---|
| `t23-batches.py lane.jsonl` | the lane's log (snapshot `lane.jsonl`, 150 lines, taken 06:31Z; `repairs.jsonl` beside it) | `batches.out` |
| `t23-gates.py <common git dir> 2026-11-27T20:00:00Z` | every `make land` Phase line in `l7r-events/*.jsonl`, joined to the sampler | `gates.out` |
| `t23-wait.py <session transcript> 2026-11-28T02:00:00Z` | the main session's transcript: each background `make lane-wait`, its turn's end, its notice | `wait.out` |
| `t23-coord.py <session transcript> 20:00Z 06:20Z 02:02Z 05:49Z` | the main session's own tool calls, classified (its docstring) | `coord.out` |
| `t23-conc.py <sampler jsonl> <cuts>` | `l7r-events/samples/mem-samples.jsonl`: trees held, `load1` | `conc.out` |
| `git log origin/main` (the tick commits) | who landed what | `ticks.out` |
| `make task-time SINCE=2026-11-28T05:49:00Z` (3 min 21 s) | the task-line verify | `task-time-since-0549.out` |

## The windows and their concurrency (FR-010)

None of these is a like window: FR-010 needs eight hours of builder work, and the after window is 31 minutes. Each figure
below is stated with its window's concurrency. Trees held is the mean of the sampler's `held` count (its samples are evenly
spaced, so the mean is time-weighted). Load is the median `load1` on 22 cores (`conc.out`).

| window | what it is | trees held | load1 median | load1 max |
|---|---|---|---|---|
| W0 2026-11-27T20:00Z to 11-28T02:02Z (6.0 h) | phase 1: every landing by hand in the clone | 3.46 | 14.4 | 91.4 |
| W1 02:02Z to 05:49Z (3.8 h) | phase 2 live; the lane stops on its defects, and the coordinator lands by hand | 2.87 | 19.2 | 606.9 |
| W2 05:49Z to 06:20Z (0.5 h) | phase 3 on main (T24 in the 05:20 bootstrap; T25 ticked by hand at 05:48:36, the runner restarted at 05:49:00) | 3.46 | 31.6 | 61.5 |

## 1. Each batch (`batches.out`)

Run minutes are the sum of the batch's `run` lines. The lane's own `minutes` on its `landed` line restarts at each resume
(462-4: 0.1 there, against 12.9 run minutes and 91.7 wall): a defect, filed below.

| batch | changes (tasks) | wall min | runs (run min) | stops, by cause | resumes | end |
|---|---|---|---|---|---|---|
| 462-1 | 3 (T550, T301, T549) | 47.2 | 1 (21.7) | 2 carry NOT VERIFIED (fixed by T73) | 2 | all 3 ejected `unplaced`, repair r1: `rust/guard cover-run` red (T301's socket test, `SUN_LEN`), placed on no change |
| 461-1 | 1 (T71) | 7.8 | 0 | 2 carry conflicts on `plan.md`/`plan-review.json` (fixed by T74) | 2 | the coordinator landed T71 by hand (tick 03:01:44); the lane then read it as landed |
| 462-2 | 1 (T278) | 12.4 | 4 (2.0) | 3 first-pass refusals on a row naming no change (a measurement's stub section; T75, T76) | 3 | landed by hand from its closing half (tick 03:14:19); attempt 4 refused "T278 is already ticked" and ejected it, repair r2 (T79) |
| 461-2 | 1 (T63) | 42.3 | 2 (4.3) | 2 first-pass refusals (no CLEAR plan review), 3 `lane-stop` by hand | 5 | landed by hand with T74 (tick 03:54:24); then read as landed |
| 462-3 | 6 (T543, T545/T555, T146/T206, T107/T173, T544, T120) | 19.9 | 1 (18.4) | none | 0 | all 6 ejected `unplaced`, repair r3: coverage "lines no test reaches" in `plan/split.rs` and `archive/report.rs`, placed on no change (fixed by T86) |
| 462-4 | 1 (T321, a build half) | 91.7 | 5 (12.9) | 5 first-pass refusals (a build half's stub section; T90), then 5 carry conflicts on `under_load.rs` once T321 had landed by hand (tick 04:56:03) | 10 | ejected `conflict` as integrate repair r4 at 05:49:04, the runner's first act on T25's code; its task had already landed |
| **461-3** | 2 (T81; T93/T86) | 28.5 | 1 (28.5) | none | 0 | **landed by the lane: one run, green, its own push (tick 06:17:14)**. The only `push` event in the log |
| 462-5 | 1 (T545/T555) | (gating at 06:31Z) | | | | not counted |

Who landed what since 02:00Z (`ticks.out` joined to the log's `push` events): the coordinator landed 8 times by hand, 21
tasks: T22 T56 T64 T70 at 02:01 (gated before 02:00), T73 T72, T71, T278, T74 T63, T321, the bootstrap batch of nine (T24 T26
T76 T90 T27 T75 T28 T40 T84) and T25. The lane landed once, 3 tasks. Every hand landing after 02:00Z was for a lane defect
fixed since: T72/T73, T74, T75/T76, T77/T79 (being built), T86, T90, T93 and T25.

The coordinator was needed by hand at 22 starts of the runner (1 start and 21 resumes). The main session ran `make
lane-start` itself 9 times and `make lane-stop` 19 times. The other resumes came from hand-ins (`make builder-done` starts the
runner), and each re-ran the stopped batch into the same refusal: 462-2's attempts 1 to 3 and 462-4's 1 to 5 hold the same
first-pass row. Those repeats came from stops that phase 3 has since removed (T76 places a first-pass row on its change and
ejects it; T90 keeps a build half out of a batch; T77 drops a superseded change). This record files nothing for them.

## 2. Throughput once phase 3 was on main (W2, 05:49Z to 06:20Z)

- Batches ended: 2. 462-4 ended at 05:49:04 by ejecting r4, and 461-3 landed. Landed without a hand: 1 batch of 2 changes (3
  tasks), 1 run, 28.5 minutes from batch start to push, and no stop.
- From hand-in to push: T81 73.6 min (handed in 05:04:02Z, pushed 06:17:36Z), T93/T86 39.3 min (05:38:19Z). Both hand-ins
  were made before 05:49 and waited behind 462-4.
- At 06:31Z, 11 hand-ins were waiting. 462-5 took one change (T545/T555) and left the other 462 hand-ins: by D5, a batch is
  the oldest hand-in plus the same feature's hand-ins straight after it, and the next waiting hand-in was 461's (T77/T79).
  The queue alternates 462, 461, 462 x7, 461, so it forms batches of 1, 1, 6, 1 and 1. It could form 2 batches, if one
  batch could span features. Filed as a lever below.
- Not comparable with W0 or W1 at this length, and n = 1. The figure to read is the one T31 takes over a like window.

## 3. The coordinator's turns on landing (`coord.out`)

A tool call is on the landing side when it runs a hand landing, a carry or hand-in, a lane mend, the session's own push, a
lane wake, or a filing of a lane defect (`t23-coord.py`'s docstring). Calls are classified on their make targets, with quoted
strings and heredoc bodies removed. A model call counts once. Tasks landed are from the tick commits in each window.

| window | model calls on landing (of all) | per hour | tasks landed | per landed task | output tokens on landing | cache-read on landing |
|---|---|---|---|---|---|---|
| W0 phase 1 (6.0 h) | 102 of 408 | 16.9 | 48 (all by hand) | 2.1 | 56.6k | 59.9M |
| W1 phase 2 (3.8 h) | 146 of 330 | 38.6 | 17 (all by hand) | 8.6 | 90.5k | 79.0M |
| W2 phase 3 (0.5 h) | 9 of 23 | 17.4 | 3 (by the lane) | 3.0 | 5.8k | 6.7M |

- The W1 calls by kind: hand-land 28, carry 15, lane-mend 19, own-push 9, wake 70, file-lane 5. So phase 2 cost the
  coordinator more per landed task than phase 1 (8.6 against 2.1), because its lane stopped on a defect at almost every batch.
- The W2 calls by kind: 6 wakes and 3 carry calls. The 3 carry calls are the coordinator handing in r3's five ejected
  changes again by hand (`make builder-done` in their trees, 05:53Z to 06:02Z): a repair entry that ejects several changes
  cannot be handed out (T96).
- Wakes against FR-005's floor of one a landed batch: there were 33 background `make lane-wait` starts and 34 owed lines for 8
  batches. The owed lines by kind: runner not running 13, first pass refused 10, batch ended 4, red and ejected 3, landed 3,
  carry conflict ejected 1. In W2 there are 2 wakes for 2 ended batches, which is the floor.

## 4. What is left for the lane to do by itself (open on origin/main, 06:31Z)

- T96 (a multi-change repair cannot be handed out). Its cost here: r3's five re-hand-ins by the coordinator.
- T95 (the brief for an integrate repair entry). Without it, r4 and any failed-push repair need a brief written by hand.
- T77/T79 (being built, waiting in the lane as bf68e5b8d8). A change superseded by a later hand-in, or one whose task is
  already ticked, still stops or wrongly ejects a batch. 461-1, 461-2, 462-2 and 462-4 all show it.
- T78 (narrowing a halving to its candidates), T87 (withdrawing a misfiled ruling), T91 and T94 (queue-policy readers).
- Phase 4 (T29, T30, T36): `make land` is still allowed in the clone, and the hand landings above used it.

## D1: the lane tree's first gate against b1's (`gates.out`)

b1 ran no gate in the window: its Phase lines are `builder-checks`, `rust-test` and `prewarm` only. So the comparison is the
lane tree (`-land`) against the clone, the tree where every landing gated until now.

| gate | tree | min | cover-build crates compiled | lint crates | load1 median | trees held |
|---|---|---|---|---|---|---|
| 462-1, the lane's first (02:38Z) | `-land` | 15.9 (red) | 302 | 165 | 20.0 | 3 |
| 462-3 (04:02Z) | `-land` | 13.2 (red) | 42 | 78 | 30.3 | 4 |
| 461-3 (05:54Z) | `-land` | 23.1 (green) | 42 | 78 | 29.8 | 4 |
| the clone's gates of 1 to 9 tasks, W0 and W1 (the 9 of 4 min or more) | the clone | 4.1 to 15.1 | 11 to 42 | 18 to 78 | 6.2 to 23.2 | 0 to 4 |

At its first gate, the adopted `-land` cache was cold against that day's main: 302 cover-build crates compiled, against 11 to
42 for every gate after it, in either tree. After that its compile counts match the clone's. The lane's later gates ran 13.2 and 23.1 minutes at
load 30, against the clone's 4.1 to 15.1 minutes at load 6 to 23. Load, batch size and cache are confounded, and n = 3. So D1
stands: the adopted tree's cache warmed after one gate. The figure that would move it is a like window's gate minutes at
like load (T31).

## D9: how long a background `make lane-wait` outlives its turn (`wait.out`)

There were 33 starts, all with `run_in_background`. 32 ended `completed` with a notice, and each notice came when the lane
wrote an owed line. The last one was still running at 06:31Z. Lifetimes from start to notice: median 7.1 min, longest 27.4 min
(05:50:15Z to 06:17:40Z, a 28.5-minute gate). 26 notices came after the turn that started them had ended (the turn's end is
taken as the next main-session message holding text only), the longest 27.1 min after it. No time limit was found up to 27.4
min, so `LANE_WAIT_MAX` is not priced. The bound is only from below: no wait yet has outlived a longer gate.

## D11: does any gate still build in the clone's own target directory?

Yes. Gates ran in the clone until 05:48:13Z: the hand landings (`make land` Phase lines with `clone` the clone: 656 rust
lines, the last at 05:48:13Z) and the hand `l7r-gate.sh rust cover` runs (57 `rust-cover` lines to 05:47:01Z). Its target
directory `~/.cache/l7r-cargo-target/diagram-backlog` (48 GB, `du -sh`, 06:2xZ) also holds the `l7r-gate` binary that
`make lane-wait` runs (`ps`: `.../diagram-backlog/tool/l7r-gate lane wait`), and `builder-checks` ran in the clone 148 times
in W1. Verdict: the directory is not dropped and nothing is deleted. Phase 4 (T29) reopens the question once `make land`
outside the lane's tree is refused.

## The task line's verify: `make task-time` over the lane's batch

`make task-time SINCE=2026-11-28T05:49:00Z` names 461-3's three tasks as landed. But no line of its output names the lane's
tree (`grep -c diagram-backlog-land`: 0). Its landings' side books 20.9 working minutes where the lane's run took 28.5. Its
"Unbooked" line reports "3878 phases tied to no run (282.0 min, not in the minutes)": the lane's gate runs in a detached
runner, outside any session's tool call, so `make task-time` books none of it. The verify fails as written. Filed below.

## Found and filed

- T99 [bugfix]: the lane's `landed` line reports the minutes since the last resume, not the batch's (462-4: 0.1 against 12.9
  run minutes). FR-005's status line and D12's figures read it.
- T100: `make task-time` books none of a lane batch's gate (its Phase lines are tied to no run). T23's verify and T31 need it.
- T101, a lever: one feature a batch (D5, because `make land` takes one `F=`) splits an interleaved queue into batches of one
  (462-5, 06:17Z).
