# M1: how many builders at once (2026-11-25 12:00 UTC to 2026-11-26 06:10 UTC)

Script: m1-concurrency.py beside this file (`python3 m1-concurrency.py [-v]`; read-only). Sources: the session transcript
(Agent dispatches, launch results, task notifications) and the guard's event log (`.git/l7r-events/*.jsonl`: Phase spans,
tool calls by agent, SubagentStop token counts, this session's landings). A builder's life runs from its launch to its last
tool call. Every figure below is reproduced by the tables after the summary.

## Summary by concurrency

| builders at once | builders (code) | median min, launch to last tool call | code builders: min per 10k output tokens (to first stop) | wall min at exactly n | builder-min per wall hour (era) | builder-built tasks landed per wall hour (era) |
|---|---|---|---|---|---|---|
| 1 | 17 (16) | 24 | 3.2 (2.8) | 469 | 54 | 1.71 (8 in 281 min) |
| 2 | 28 (22) | 33 | 6.4 (3.5): 2.02x (1.25x) | 407 | 85 | 2.02 (21 in 625 min) |
| 3 | 7 (2) | 16 | 9.7 (7.4), two builders | 43 | 111 (3 and 4 together) | 2.44 (7 in 172 min; 3 and 4 together) |
| 4 | 3 (0) | 6 | - | 9 | | |

Like-for-like spans (same suite or crate, against its own median at one builder): hook suites 1.67x at 2; rust lint 2.3x at 2;
rust test and coverage runs 1.27x at 2. A whole closing-checks run in a builder worktree: a tree's FIRST run 142 s (13 runs at
2), a LATER run 62 s at 1 builder (8 runs) and 76 s at 2 (18 runs) - 1.23x; the session clone alone 48 s. At 3 or more builders
the spans come from three trees (t258, t262, t263) and ONE whole closing-checks run (264 s, a first run, at 4).

## Reading

- The gain from two at once is between none and 1.6x, and this data cannot narrow it: 1.18x by tasks landed per wall hour (a
  baseline of 8 landings, 5 of that era's 13 builders spent on one task, T243), 0.99x by pace to the last tool call (2 / 2.02),
  1.6x by pace to the first stop (2 / 1.25). Trial 1's "44 min side by side against 88 one after the other" assumed a builder
  alone would also take 44.
- Each code builder at 2 was slower by more than the 15% bar on every measure (1.25x to 2.02x). Most of it is the fresh
  worktree, not the second builder: a tree's first closing-checks run costs 142 s against 62-76 s later, while a later run at 2
  is 1.23x a later run at 1. 21 of the 22 code builders at 2 ran in a new worktree; 1 of the 16 at 1 did.
- Three and four at once were not tested on comparable work: 52 wall minutes, 8 of 10 builders comment or doc edits (451 T250's
  batches, the agenda writes), both code builders at 3 on a different model (fable-5-2; every builder at 1 ran opus-5-5).
- Builder-minutes per wall hour is occupancy, not output; landed per hour in the last era is 7 landings.

## Memory and load

- The container's memory limit is 10 GiB (cgroup `memory.max` 10737418240), not the 15 GB `free -g` shows; it has no swap
  (`memory.swap.max` 0), so past the limit comes reclaim and then an out-of-memory kill.
- `memory.peak` 10725941248: the cgroup has touched its limit at some time in its 30 h. That figure includes page cache and
  has no timestamp, so peak memory during the 3- and 4-at-once runs was NOT recorded. `memory.events`: oom 0, oom_kill 0.
- At the reading (two measurers running): anon 1.36 GB, file cache 7.6 GB. Pressure totals since start: memory some 264 s, full
  190 s; CPU some 5,229 s. 22 cores, load 5.9. `dmesg` is not readable in the container.
- The sampler that would record it (every 10 s, timestamped; started by the tooling that dispatches a builder):
  `while sleep 10; do echo "$(date -u +%FT%TZ) anon=$(awk '/^anon /{print $2}' /sys/fs/cgroup/memory.stat) cur=$(cat /sys/fs/cgroup/memory.current) mem_some_us=$(grep some /sys/fs/cgroup/memory.pressure | cut -d= -f5) load=$(cut -d' ' -f1 /proc/loadavg)"; done >> "$(git rev-parse --git-common-dir)/l7r-events/mem-samples.log"`

## Frictions by count (agenda item 1's trial notes)

- 1: none from parallelism; the cost was the queue (385 min of 24 h waiting on agents run one at a time).
- 2 (trials 1-5, thirteen tasks): the started-task mark shared through .git; guards reading the session clone, not the
  worktree; a cold build cache per tree (first build 2-2.5 min, cold coverage about 9 min, 13-14 GB, disk to 91%); task numbers
  collided twice; every carry-over conflicted on plan-review.json; reviewers recorded verdicts from the wrong tree; one
  closing-checks test flaked side by side; two gitignored map renders missing in a fresh tree. Fixed since: 451 T245-T247,
  T252-T257.
- 3 and 4: the agenda records none - no trial note was written for the 2026-11-26 runs. The follow-ups filed that night (451
  T266-T273) name two: parallel builders' shared scratch, and claims-checked in a worktree.

## Not measured

Peak memory at any count; 3 and 4 builders on compile work; one builder alone in a fresh worktree against one in a warm tree
(the control that separates the cold cache from contention); the load of the other session on the machine (a1bf10b9).

## Recommended standard

Two code builders at once, in worktrees that are reused or share a build cache (the cold tree is the larger measured cost);
three or four only for batches that compile nothing (comment and doc edits). No count is certified on memory: until the sampler
has run, the margin is unproven; proposed margin, anon peak at or under 7 GiB of the 10 GiB limit with oom_kill at 0.
Falsifiers: (a) down to 1 if, over the next 20 code tasks at 2 in warm trees, builder-built tasks landed per wall hour is at or
under 1.71 or a later closing-checks run exceeds 1.5x its 1-builder median; (b) up to 3 if a planned run of 6 or more compile
tasks at 3 lands more per wall hour than at 2, with pace per 10k output tokens within 15% of the pace at 2 and anon peak at
or under 7 GiB.

## Every builder dispatch since 2026-11-25T12:00 (UTC)

| start | tree | task | kind | min to first stop | min to last tool call | tokens k | builders at start | avg builders | stops |
|---|---|---|---|---|---|---|---|---|---|
| 11-25T12:12 | db | T230 | code | 11 | 11 | 167 | 1 | 1.00 | 1 |
| 11-25T12:23 | db | T238 | code | 5 | 5 | 126 | 1 | 1.00 | 1 |
| 11-25T12:28 | db | T240 | code | 14 | 28 | 251 | 1 | 1.00 | 6 |
| 11-25T12:59 | db | T237 | code | 17 | 17 | 209 | 1 | 1.00 | 1 |
| 11-25T13:18 | db | T241 | code | 12 | 12 | 234 | 1 | 1.00 | 1 |
| 11-25T13:32 | db | T226 | code | 21 | 23 | 261 | 1 | 1.00 | 2 |
| 11-25T14:06 | db | T243 | code | 26 | 26 | 310 | 1 | 1.00 | 1 |
| 11-25T14:32 | db | T243 | code | 35 | 35 | 280 | 1 | 1.00 | 1 |
| 11-25T15:08 | db | T243 | code | 26 | 26 | 234 | 1 | 1.00 | 1 |
| 11-25T15:34 | db | T243 | code | 33 | 35 | 289 | 1 | 1.00 | 2 |
| 11-25T16:10 | db | T243 | code | 12 | 12 | 141 | 1 | 1.00 | 1 |
| 11-25T16:25 | db | T244 | code | 18 | 24 | 261 | 1 | 1.00 | 4 |
| 11-25T16:52 | db-t228 | T228 | code | 44 | 44 | 192 | 1 | 2.00 | 1 |
| 11-25T16:53 | db-t234 | T234 | code | 44 | 44 | 281 | 2 | 1.99 | 1 |
| 11-25T17:46 | db-t235 | T235 | code | 26 | 53 | 240 | 1 | 1.92 | 4 |
| 11-25T17:46 | db-t242 | T242 | code | 17 | 41 | 227 | 2 | 2.00 | 3 |
| 11-25T18:31 | db-t245 | T245 | code | 33 | 54 | 280 | 2 | 1.92 | 3 |
| 11-25T18:44 | db-t231 | T231 | code | 24 | 45 | 232 | 2 | 1.93 | 2 |
| 11-25T19:38 | db-t227 | T227 | code | 32 | 64 | 279 | 1 | 1.83 | 3 |
| 11-25T19:38 | db-t229 | T229 | code | 34 | 53 | 202 | 2 | 2.00 | 5 |
| 11-25T20:42 | db-t232 | T232 | code | 62 | 62 | 309 | 1 | 1.70 | 1 |
| 11-25T20:56 | db-t247 | T247 | code | 10 | 27 | 144 | 2 | 2.00 | 2 |
| 11-25T21:27 | db-t246 | T246 | code | 26 | 39 | 309 | 2 | 1.85 | 4 |
| 11-25T21:45 | db-t232 | T232 | code | 4 | 5 | 125 | 2 | 2.00 | 2 |
| 11-25T21:55 | db-t233 | T233 | code | 22 | 34 | 238 | 2 | 1.76 | 3 |
| 11-25T22:07 | db-t246 | T246 | code | 1 | 14 | 84 | 2 | 2.00 | 4 |
| 11-25T22:44 | db-t248 | T248 | code | 20 | 40 | 201 | 1 | 1.78 | 4 |
| 11-25T22:44 | db-t249 | T249 | code | 32 | 32 | 189 | 2 | 2.00 | 1 |
| 11-25T23:32 | db | T252 | code | 10 | 10 | 122 | 1 | 1.00 | 1 |
| 11-25T23:44 | db | T253 | code | 31 | 31 | 270 | 1 | 1.00 | 1 |
| 11-26T00:47 | db-t254 | T254 | code | 36 | 39 | 313 | 1 | 1.89 | 2 |
| 11-26T00:47 | db-t256 | T256 | code | 22 | 32 | 249 | 2 | 2.00 | 3 |
| 11-26T01:23 | db-t254 | T254 | code | 18 | 35 | 215 | 2 | 1.06 | 4 |
| 11-26T02:12 | db | T259 | code | 37 | 37 | 311 | 1 | 1.29 | 1 |
| 11-26T02:38 | db-t417 | T417 | code | 29 | 29 | 231 | 2 | 1.98 | 1 |
| 11-26T02:50 | db | T259 | code | 25 | 25 | 188 | 2 | 1.68 | 1 |
| 11-26T03:17 | db-t258 | T258 | code | 23 | 42 | 193 | 1 | 2.40 | 3 |
| 11-26T03:28 | db-talkrec | - | comment/doc | 3 | 4 | 57 | 2 | 3.82 | 2 |
| 11-26T03:28 | db-decide | - | comment/doc | 9 | 9 | 107 | 3 | 3.37 | 2 |
| 11-26T03:28 | db-t261 | T261 | code | 13 | 13 | 118 | 4 | 2.95 | 1 |
| 11-26T03:39 | db-decide | - | comment/doc | 0 | 0 | 59 | 3 | 3.00 | 1 |
| 11-26T03:43 | db-t439 | T439 | comment/doc | 17 | 17 | 147 | 2 | 2.91 | 1 |
| 11-26T03:43 | db-t262 | T262 | code | 23 | 28 | 148 | 3 | 2.17 | 2 |
| 11-26T04:23 | db-t251 | T251 | comment/doc | 39 | 41 | 165 | 1 | 2.76 | 2 |
| 11-26T04:23 | db-t250 | T250 | comment/doc | 15 | 16 | 149 | 2 | 2.99 | 2 |
| 11-26T04:23 | db-t263 | T263 | code | 27 | 43 | 140 | 3 | 2.72 | 2 |
| 11-26T04:39 | db-t250 | T250 | comment/doc | 6 | 6 | 106 | 3 | 3.98 | 1 |
| 11-26T04:40 | db-t250b | T250 | comment/doc | 10 | 10 | 130 | 4 | 3.53 | 1 |
| 11-26T05:05 | db-t251 | T251 | comment/doc | 10 | 10 | 125 | 2 | 1.13 | 2 |
| 11-26T05:15 | db-t250 | T250 | comment/doc | 7 | 7 | 129 | 1 | 1.98 | 2 |
| 11-26T05:16 | db-t250c | T250 | comment/doc | 9 | 9 | 132 | 2 | 1.94 | 2 |
| 11-26T05:23 | db-t250 | T250 | comment/doc | 10 | 10 | 133 | 2 | 1.93 | 1 |
| 11-26T05:25 | db-t250c | T250 | comment/doc | 7 | 7 | 122 | 2 | 2.00 | 1 |
| 11-26T05:32 | db-t250c | T250 | comment/doc | 15 | 15 | 146 | 2 | 1.93 | 1 |
| 11-26T05:34 | db-t250 | T250 | comment/doc | 15 | 15 | 173 | 2 | 1.85 | 2 |
| 11-26T05:55 | db-t250 | T250 | comment/doc | 14 | 14 | 128 | 1 | 1.00 | 1 |

## Code builders only: minutes per 10k OUTPUT tokens (a size-normalized pace: cumulative tok.out from the SubagentStop lines; subagent_tokens is the final context size and saturates at the cap)

| n | code builders with tok.out | median output tokens k | median min per 10k output tokens, to last tool call | to first stop | vs n=1 | worktree builders among them |
|---|---|---|---|---|---|---|
| 1 | 16 | 68 | 3.2 | 2.8 | 1.00x | 1 |
| 2 | 22 | 63 | 6.4 | 3.5 | 2.02x | 21 |
| 3 | 2 | 27 | 9.7 | 7.4 | 3.07x | 2 |

## Code builders: foreground minutes inside make targets, per builder (the event log's PostToolUse ms by agent; a backgrounded run is not in it)

| n | builders | models | rust-test | closing-checks | quick | crate-checks + rust-lint | decide + plan-verdict | all make targets | all tool time | builder min |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 16 | opus-5-5 16 | 1.2 | 0.0 | 0.1 | 0.5 | 0.2 | 3.9 | 4.6 | 23 |
| 2 | 22 | opus-5-5 20, fable-5-2 2 | 2.8 | 0.0 | 0.0 | 0.7 | 0.4 | 6.2 | 11.3 | 38 |
| 3 | 2 | fable-5-2 2 | 2.6 | 0.0 | 0.1 | 0.0 | 0.0 | 3.5 | 8.8 | 28 |

## Builders by concurrency (avg builders over its life, rounded)

| n | builders | of them code | median min to first stop | median min | mean min | mean tokens k | tokens k per builder-min | wall min with exactly n running |
|---|---|---|---|---|---|---|---|---|
| 1 | 18 | 16 | 17 | 23 | 22 | 219 | 10.0 | 483 |
| 2 | 28 | 22 | 23 | 33 | 32 | 203 | 6.3 | 407 |
| 3 | 7 | 2 | 15 | 16 | 20 | 126 | 6.3 | 43 |
| 4 | 3 | 0 | 6 | 6 | 7 | 98 | 14.9 | 9 |

## The same span at each load: duration / that span's own median at load 1 (time-weighted mean over keys)

A key is (source, step, suite name or crate). Spans under 1 s, cached and failed ones are dropped; a key needs 3 spans at load 1.

| spans | load measured as | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|---|
| hook suites (no build cache) | builders running at t0 | 1.00x (median key 1.00x; 2443 spans, 58 keys, 385 min) | 1.67x (median key 1.54x; 2023 spans, 58 keys, 544 min) | 7.46x (median key 6.46x; 37 spans, 14 keys, 55 min) | - |
| hook suites (no build cache) | trees with an overlapping span | 1.00x (median key 1.00x; 3143 spans, 61 keys, 540 min) | 2.06x (median key 1.81x; 1420 spans, 60 keys, 439 min) | 10.68x (median key 8.41x; 10 spans, 5 keys, 27 min) | - |
| rust build + cover-build (cold in a new worktree) | builders running at t0 | 1.00x (median key 1.00x; 299 spans, 27 keys, 100 min) | 3.16x (median key 1.83x; 226 spans, 22 keys, 195 min) | 2.84x (median key 3.10x; 13 spans, 5 keys, 10 min) | - |
| rust build + cover-build (cold in a new worktree) | trees with an overlapping span | 1.00x (median key 1.00x; 395 spans, 31 keys, 157 min) | 2.67x (median key 1.89x; 163 spans, 24 keys, 156 min) | - | - |
| rust lint | builders running at t0 | 1.00x (median key 1.00x; 579 spans, 33 keys, 58 min) | 2.27x (median key 1.75x; 631 spans, 33 keys, 127 min) | 4.93x (median key 2.14x; 22 spans, 11 keys, 11 min) | 5.35x (median key 4.80x; 16 spans, 8 keys, 5 min) |
| rust lint | trees with an overlapping span | 1.00x (median key 1.00x; 911 spans, 34 keys, 104 min) | 2.07x (median key 1.79x; 371 spans, 34 keys, 97 min) | - | - |
| rust test + cover-run | builders running at t0 | 1.00x (median key 1.00x; 805 spans, 38 keys, 76 min) | 1.27x (median key 1.24x; 501 spans, 36 keys, 59 min) | 1.75x (median key 1.80x; 8 spans, 4 keys, 3 min) | - |
| rust test + cover-run | trees with an overlapping span | 1.00x (median key 1.00x; 936 spans, 39 keys, 83 min) | 1.62x (median key 1.73x; 403 spans, 36 keys, 57 min) | - | - |
| make quick, whole | builders running at t0 | 1.00x (median key 1.00x; 133 spans, 1 keys, 16 min) | 1.54x (median key 1.54x; 65 spans, 1 keys, 28 min) | 25.78x (median key 25.78x; 10 spans, 1 keys, 17 min) | 33.40x (median key 33.40x; 3 spans, 1 keys, 5 min) |
| make quick, whole | trees with an overlapping span | 1.00x (median key 1.00x; 149 spans, 1 keys, 31 min) | 1.67x (median key 1.67x; 57 spans, 1 keys, 25 min) | 33.30x (median key 33.30x; 5 spans, 1 keys, 10 min) | - |

## A whole closing-checks run (40+ hook suites in one tree), by what ran beside it

| beside it | runs | median wall s | mean wall s | vs alone | median suite-seconds (sum of its suites) | vs alone |
|---|---|---|---|---|---|---|

### The same runs in builder worktrees, a tree's FIRST whole run apart from its later ones

| run | builders at midpoint | runs | trees | median wall s | min - max |
|---|---|---|---|---|---|
| first in its tree | 1 | 1 | 1 | 145 | 145 - 145 |
| first in its tree | 2 | 13 | 13 | 142 | 56 - 343 |
| first in its tree | 4 | 1 | 1 | 264 | 264 - 264 |
| later | 1 | 8 | 5 | 62 | 40 - 175 |
| later | 2 | 18 | 9 | 76 | 48 - 198 |
| the session clone, any | 1 | 13 | 1 | 48 | 33 - 176 |

Spans at 3 or more builders, by tree: hooks diagram-backlog-t251 1 spans; hooks diagram-backlog-t258 24 spans; hooks diagram-backlog-t262 32 spans; hooks diagram-backlog-t263 54 spans; quick quick diagram-backlog-decide 3 spans; quick quick diagram-backlog-t250 2 spans; quick quick diagram-backlog-t250b 1 spans; quick quick diagram-backlog-t251 1 spans; quick quick diagram-backlog-t258 2 spans; quick quick diagram-backlog-t262 1 spans; quick quick diagram-backlog-t263 1 spans; quick quick diagram-backlog-t439 1 spans; quick quick diagram-backlog-talkrec 1 spans; rust build diagram-backlog-t261 2 spans; rust build diagram-backlog-t262 2 spans; rust build diagram-backlog-t263 3 spans; rust cover-build diagram-backlog-t251 3 spans; rust cover-build diagram-backlog-t258 6 spans; rust cover-build diagram-backlog-t263 1 spans; rust cover-run diagram-backlog-t258 27 spans; rust format diagram-backlog-t263 4 spans; rust lint diagram-backlog-t251 34 spans; rust lint diagram-backlog-t258 5 spans; rust lint diagram-backlog-t262 3 spans; rust lint diagram-backlog-t263 33 spans; rust test diagram-backlog-t261 1 spans; rust test diagram-backlog-t262 1 spans; rust test diagram-backlog-t263 2 spans
| other full runs overlapping: 0 | 48 | 88 | 105 | 1.00x | 547 | 1.00x |
| other full runs overlapping: 1 | 6 | 120 | 117 | 1.36x | 696 | 1.27x |
| builders at its midpoint, all trees: 1 | 22 | 49 | 79 | 1.00x | 335 | 1.00x |
| builders at its midpoint, all trees: 2 | 31 | 123 | 120 | 2.53x | 753 | 2.25x |
| builders at its midpoint, all trees: 4 | 1 | 264 | 264 | 5.43x | 1914 | 5.72x |
| builders at its midpoint, the session clone only: 1 | 13 | 48 | 73 | 1.00x | 328 | 1.00x |
| builders at its midpoint, builder worktrees only: 1 | 9 | 79 | 88 | 1.00x | 534 | 1.00x |
| builders at its midpoint, builder worktrees only: 2 | 31 | 123 | 120 | 1.56x | 753 | 1.41x |
| builders at its midpoint, builder worktrees only: 4 | 1 | 264 | 264 | 3.35x | 1914 | 3.59x |

## Throughput by era (an era opens when the builder count first reaches a new level; landing and merge gaps stay inside)

| era | window (UTC) | wall min | builders | builder-min | builder-min per wall hour | % wall at 0 / 1 / 2 / 3+ builders | tokens M | builder-built tasks landed (distinct) of all this session landed | landed per wall hour | builder-min per landed task |
|---|---|---|---|---|---|---|---|---|---|---|
| one at a time | 11-25T12:12 - 11-25T16:53 | 281 | 13 | 254 | 54 | 10 / 90 / 0 / 0 | 3.0 | 8 of 8 | 1.71 | 32 |
| two at a time | 11-25T16:53 - 11-26T03:17 | 625 | 23 | 889 | 85 | 15 / 28 / 57 / 0 | 5.2 | 21 of 21 | 2.02 | 42 |
| three and four at a time | 11-26T03:17 - 11-26T06:09 | 172 | 20 | 317 | 111 | 10 / 30 / 30 / 30 | 2.6 | 7 of 7 | 2.44 | 45 |

wall minutes by exact builder count: 1: 483, 2: 407, 3: 43, 4: 9
