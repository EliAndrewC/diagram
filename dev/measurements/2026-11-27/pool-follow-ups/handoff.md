# 451 T296 build half - handoff (2026-11-27)

Tree: /diagram/.clones/diagram-backlog-t271. NOTHING BUILT, nothing staged or committed; the tree is clean. All four
follow-ups were judged against what has landed since 451 T285: none still pays. The closing half's job is to close the box
with the evidence below (a plan section saying so); there is no code to review.

## (a) Seed a new pool tree's build cache from a free warm one - NOT BUILT: it does not pay

Measured once, 2026-11-27 01:10-01:18 UTC, in diagram-backlog-t271 (the brief's crates): `make builder-checks
CRATE="rust/gate/crates/task rust/gate/crates/land"` with `L7R_RUST_FRESH=1 L7R_GATE_TARGET=<dir> CARGO_TARGET_DIR=<dir>`
(both are needed: `L7R_GATE_TARGET` places only the tool binary; `l7r-rust` takes the cargo target from `CARGO_TARGET_DIR`,
`rustc.rs` `target_override`), each arm into a scratch target dir in the scratchpad, removed afterward.

- COLD (empty target): 260.1 s wall, green; the target came to 1.9 GB (so every build landed in the scratch dir, nothing
  in t271's own cache). Load average 6.3 at the start, 13.9 at the end.
- SEEDED from another tree's cache (diagram-backlog-t270's `debug/` and `tool/`, excluding `incremental/` and
  `.cargo-lock`, with no run records, locks, `cover-*` or `*.good`): copy 11.9 s, 3.3 GB; then 176.0 s wall, green; the target
  grew to 4.2 GB (0.9 GB rebuilt). Load 12.0 at the start, 24.6 at the end. Total 187.9 s, which saves 72 s measured against
  cold. The land crate's test run took 64.4 s in this arm against 2.4 s in the cold one. If that 62 s was noise, the saving is
  up to about 135 s; its cause was not established (load alone does not explain a 27x slowdown).
- A HAZARD OF SEEDING `tool/`: `l7r-gate.sh` rebuilds a tool binary only when the sources are newer than it, so a seed of `tool/`
  can run the donor's `l7r-rust`, built from a held tree's uncommitted sources. Neither run's log shows whether the tool was
  rebuilt (the build is `--quiet`). Any seed would have to leave `tool/` out, which shrinks the saving further.
- Logs: `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t296-cold.log` and `t296-seed.log` beside it
  (the scratchpad; the target dirs are removed).
- Why only that much: the workspace crates rebuild anyway (T285's own measurement, plan-done.md under "### T285": a tree
  moved to a new path rebuilt every workspace crate, 66.5 s and 41.7 s, while the registry crates were kept, because cargo's
  fingerprints hold the workspace's absolute path). Only the registry crates' share is saved.
- Fidelity: the simulation built t271's sources at t271's path against t270's artifacts, and the 0.9 GB growth shows the workspace
  crates rebuilt as they would in a new tree. `make_cold` already builds the guard into `tool/`, so an empty target is slightly
  pessimistic for the cold arm.
- HOW OFTEN: `builder-pool.log` (in /diagram/.clones/diagram-backlog/.git/), over the pool's life of about 35 hours, holds ONE
  `make` event (diagram-backlog-b1, 2026-11-26T20:38:58Z), and the pool has been at
  its cap of 4 (`builder_pool::CAP`) ever since. All four trees are registered and held now. A cold tree comes only after a
  `make builder-tree-drop` or a raised cap.
- There is NO FREE DONOR at that moment: `make_cold` is reached only when `take` found no free tree. A seed would have to copy a
  HELD tree's live cache, which its builder may be writing at that moment, or the clone's or the landing's.
- COST: 3.3 GB more per seed. The cache is already well past its 100 GB budget (about 205 GB across the clone's build
  directories, observed 2026-11-27 with `du -sh`).
- The 14-30 minute cold figure the task line rests on was for CLOSING CHECKS (with coverage), which builders no longer run
  (two tiers, 451 T308/T381). Under the first tier, for these two gate crates, a cold tree cost about 4.3 minutes and a seeded
  one about 3.1.
- Verdict: about 1-2 minutes saved per cold tree, roughly one cold tree per pool's life. Not built. What would reopen it: the pool
  cap raised, or trees dropped routinely.

## (b) `make builder-tree-hold TREE= T=` - NOT BUILT: no case left

Every way a hold is made or ended now has a command:
- take: `make builder-tree` (and `make builder-brief`, which calls `builder_tree::run` take, `builder_brief.rs`);
- reuse: `take` returns the tree a task already holds ("already holds it");
- release: `builder-tree-release`, `builder-done` (step 5), `make land`/`land-batch` (`landed`), and the automatic free at the next
  handout for ticked tasks;
- an unregistered tree held: `make builder-tree-adopt TREE= T= F=`.

The pool's log shows 3 adopt, 71 take, 70 release, 29 done, 1 landed and 0 discard events; no state needs a hand edit. Over the
whole log, three tasks were taken on different trees (T304: t271, then b1; T300: t270, t271; T307: t271, t270). Each re-take
followed a deliberate release or a `done` hours earlier (the next builder of the task), never a builder's live work stranded.
T300's 18:57 take and release came in the same minute, a mistaken take freed at once.

The one plausible case was a successor (a closing half, a fix) that must continue in the SAME tree. Both routes cover it:
- the build half ends uncommitted (as this brief's does): the hold persists until the task lands, so `take T=<task>` returns the
  same tree;
- `builder-done` ran: its done commit is carried to the clone, a handout starts at HEAD, and `handout_waits` (builder_done.rs,
  T398) refuses a handout while that commit is uncarried, so any free tree will do.

The residual case is a hold released by mistake while its builder still works. Its tree then holds foreign uncommitted work, so
`take` refuses it and hands out another. The log shows it never happened, and `builder-tree-adopt` cannot re-register a tree
that is already in the pool, so a hold command would serve only that case. It does not pay. A tree for a
non-builder job (a measurement that loads the machine) is held by `make builder-tree T=<its task>`.

## (c) Each guard-message rewording costs a full `make hooks-test` - NOT BUILT HERE, as the brief says

451 T338 is the open task for it: a target that renders one guard's suite into the tree's message store, named in the first
tier, plus where a Rust-built message with no suite rendering is caught. Its text covers this candidate in full; the closing
half points the box at T338.

## (d) `make carry COMMITS=a..b` - NOT BUILT: no range exists to carry

Since T394 a builder's work is ONE done commit: `builder-done` commits everything once, a bundle (`T=a,b`) too, and writes
`refs/l7r/done/<feature>-<task>`. It refuses a second done commit while one waits uncarried (step 1), so a tree never holds two in
a row. Each task's done commit, from one tree or several, is a single commit on its own detached base (the clone's HEAD at its
handout) under its own ref, so they are siblings and never an `a..b` chain, and a range could not name them. Builders do not commit otherwise ("Do NOT stage, commit"). `make carry COMMIT=<sha>` alone
(T397 b, built) is the whole need. What remains, carrying several tasks' done commits in one go at landing, is 451 T397 (c),
still open: the closing half points the box there.

## Red-first, checks

No code, so no red-first. `make builder-checks CRATE="rust/gate/crates/task rust/gate/crates/land"` ran green twice as the
measurement's own arms, 260 s and 176 s, at HEAD's code with t271's sources.
