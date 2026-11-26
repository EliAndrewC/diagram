---
kind: adopted
title: parallel builder count
for: two code builders run at once, each in a reused (warm) worktree, and three or four at once only for batches that compile nothing, so the coordinating session waits less on a queue of builders without the builders slowing each other or the container running out of memory
measured: 2026-11-26
measurement: builder-built tasks landed per wall hour 1.71 with one builder (8 in 281 min) and 2.02 with two (21 in 625 min), 2.44 with three and four together on mostly comment and doc work (7 in 172 min); per-builder pace at two between level and 1.6x; a later closing-checks run 62 s at one and 76 s at two (1.23x), a tree's first run 142 s; 21 of 22 code builders at two ran in a cold tree against 1 of 16 at one; container memory limit 10 GiB with no swap, memory.peak 10.73 GB at some time in 30 h, no OOM kill, the peak during 3-4 at once not recorded
command: python3 dev/measurements/2026-11-26/builder-count/m1-concurrency.py -v (reads the dispatching session's transcript under ~/.claude/projects/ and the tree's l7r-events; the 2026-11-26 figures are kept in m1-results.md beside it, since a transcript does not outlive its container)
falsifier: two at once lands no more per wall hour than one, or a planned run at three lands more than two within the pace and memory margins
threshold: down to one - over the next 20 code tasks at two in warm trees, landed per wall hour at or under 1.71, or a later closing-checks run over 1.5x its one-builder median; up to three - six or more compile tasks at three landing more per wall hour than at two, pace per 10k output tokens within 15% of two's, anonymous memory peak at or under 7 GiB; the 7 GiB margin is a GUESS knob
cost: make task-time's builder and closing-checks rows by concurrency; a cold worktree's first build (13-14 GB and 142 s of closing checks)
last-audited: 2026-11-26
cadence-days: 14
---

PROVISIONAL - a working default for the GM to confirm at the talk, not closed under the pre-approval of 2026-11-25 (its memory
condition is unmeasured; the three-or-four rule is the session's addition). Recorded (`docs/process-decisions.md`, "Two code builders at once, in
reused worktrees; three or four only for work that compiles nothing"). The rule is in `scripts/container/builder-brief.md`'s SIZING
paragraph; no guard enforces it.

Not measured, and owed before the count is certified: peak memory at each count (a sampler at dispatch), and one builder in a
fresh worktree against one in a warm tree. The audit re-runs the command over the builders dispatched since 2026-11-26.
