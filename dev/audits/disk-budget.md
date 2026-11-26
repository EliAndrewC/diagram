---
kind: adopted
title: the disk budget and its low-disk trigger
for: the container never fills the host's disk - the build cache held to its budget by evicting idle profiles, the per-clone leftovers swept by age, and an eviction started automatically below a share of free space
measured: 2026-11-25
measurement: the disk at 88% (382G of 461G used, 56G free), the Rust build cache 190 GB against its own 100 GB budget (diagram-backlog 79G, diagram-backlog-land 43G, diagram-research 19G, diagram-backlog-review 18G, a trial worktree 13-14G within minutes), make cache-clean DRY=1 freeing 27 MB; /tmp/claude-1000 17 GB (14.4 GB of it older than 3 days); .git/review-snapshot 1.7 GB in 141 snapshots; after 451 T245 the dry run freed 30.5 GB, and after T245 and T246 the trials ended at 63% free from a 91% peak
command: make disk-audit; make cache-clean DRY=1
falsifier: the eviction's cold rebuilds cost more builder minutes than the full disk it prevents - or it fails its job, the disk falling below its floor anyway
threshold: cold rebuilds after an eviction past 30 builder-minutes a week while free space never fell below 20% without it (GUESS); or free space below FLOOR_GB (15 GB) once with the trigger on
cost: make task-time's build and cover-build Phase minutes of a profile rebuilt cold after an eviction; the trigger's df at each prompt
last-audited: 2026-11-25
cadence-days: 14
covers: BUDGET_GB
covers: FREE_PCT
covers: FLOOR_GB
covers: IDLE_HOURS
covers: TMP_HOURS
covers: SNAPSHOT_DAYS
covers: EVERY
---

451 T245 (`rust/guard/src/guards/scratch_sweep_hooks/`: `disk/audit.rs`, `disk/low.rs`, `sweep/evict.rs`) and T246 (the per-clone
leftovers: task scratch, handoff scratch, review snapshots, the gencache, finished sessions' task outputs). The GM, 2026-11-25:
"we might even want to trigger something automatically if our disk space ever drops below a certain percentage of free space".

Every budget and the 20% trigger (`L7R_DISK_FREE_PCT`) are GUESS knobs, set from the 2026-11-25 measurement. The price, recorded by
T245: a profile taken is a cold rebuild at its tree's next build - one crate's coverage family minutes, the landing tree's whole set
(46 GB) a cold gate. Priced and rejected: a larger budget (each parallel tree adds 13-14 GB), evicting only gone trees (27 MB), and
evicting by tree rather than profile (keeps an idle 25 GB set). The failure it prevents is 2026-11-22's, when every builder's coverage
run failed for want of space.
