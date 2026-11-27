---
kind: adopted
title: the prune of stale builds inside a live build directory
for: inside every live build directory (the clone's, the pool trees', the mirror's), a crate's build unread for STALE_HOURS (48 h, a GUESS knob, `L7R_CACHE_STALE_HOURS`) before its profile's last use is taken by the cache sweep, the eviction and `make cache-clean`, never one a live cargo holds; the knob is floored at FLOOR (25 h), past the day a `relatime` atime can lag a read (451 T515)
measured: 2026-11-27
measurement: 451 T515 - the build cache at 246.8 GB against its 100 GB budget, the low-disk eviction freeing 0.0 GB because every profile was a live tree's rebuilt each landing or a pool tree's; on the real cache, by stat alone, a 30 h knob would take 111.6 GB, 48 h 85.0 GB (83.3 GB by the built rule), 72 h 76.5 GB; a warm build timed on a pruned copy of one crate's profile
command: make rust-test CRATE=rust/guard ONLY="scratch_sweep_hooks"
falsifier: a warm tree's next build recompiling a crate the prune took, its test or lint build slower than before the prune
threshold: one landing's gate or one builder's first build slowed by more than a minute by a pruned crate in a month (it reopens the knob)
cost: the sweep's stat walk of each build directory (seconds, in make task-time's hook rows), and any rebuild a wrong prune causes (the falsifier)
last-audited: 2026-11-27
cadence-days: 30
covers: STALE_HOURS
covers: FLOOR
---

451 T515 (`rust/guard/src/guards/scratch_sweep_hooks/sweep/prune.rs`, `disk.rs`): the GM, 2026-11-27, on the disk at 82% - "we
are reusing builder worktrees ... a lot of the cleanup that we are relying on never actually happens". A reused tree is never idle,
so the eviction's whole-profile rule (451 T158, T245) never took anything from it; this prunes inside it. The 48 h default is the
builder's GUESS within the GM's 2026-11-26 words, "we definitely don't want to clean things up if it is going to cost us time
later": two days of no read is well past any build a warm tree repeats. Idle pool-tree profiles past the budget are left for 451
T518, which prices their rebuild first; a landed task's scratch worlds under a session's scratchpad are 451 T517.
