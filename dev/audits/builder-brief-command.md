---
kind: adopted
title: a builder's brief is made and checked by the tooling
for: a builder's brief is sized before it is written and carries its standing block, because the command that prints the block refuses an oversized brief and a guard refuses a builder's dispatch without the block's marker
measured: 2026-11-26
measurement: the coordinating session's 110 Agent dispatches of the day (not its builders' own) replayed through the built guard on a fixture pool of the 18 trees they name - 56 refused, every one a builder's and every one for no marker (none carried one), 54 passed (36 checks, 17 ad-hoc agents whose prompt names no pool tree, the one claims round), no dispatch that was not a builder's refused; of the five briefs that broke the sizing rules that day the command's refusals take three from its caller's own words (T285 as a fix: a new mechanism, two builders; T298: JOBS=4; T315: MEASURES=7 or 15) and none for T316 or T308 (a measurement and a build in one brief of two jobs), which a truthful KIND=measurement marker leaves to the guard's narrow edit rule - it fires on T308's brief (by a word of its measurement line) and T347's and not on T316's
command: bash tests/hooks/test-builder-brief-hooks.sh (27 cases; 13 fail with the guard's branch removed); make rust-test CRATE=rust/gate/crates/task (builder_brief::tests); make guard-log GUARD=builder-brief (its refusals and escapes); the replay, by hand - the Agent calls of a session's transcript piped through tests/hooks/builder-brief-hooks.sh
falsifier: a builder reaching the context cap whose brief the command made, or the escape (BUILDER_BRIEF_OK, or the command's SIZING_OK) used more than once a day
threshold: one builder at the cap on a brief the command sized, or two escapes in a day (either reopens it); MEASURES_MAX (6) and JOBS_MAX (3) are GUESS knobs
cost: one command before each builder's brief (a pool handout, which the brief needed already); one read of the clones' pool registries on an Agent call whose prompt names a clone's path; the guard refusing a reader of a pool tree until it carries the escape line
last-audited: 2026-11-26
cadence-days: 7
covers: rust/guard/src/guards/builder_brief_hooks.rs
covers: MEASURES_MAX
covers: JOBS_MAX
---

451 T334 (`rust/gate/crates/task/src/builder_brief.rs`, `rust/guard/shared/src/builder_brief.rs`,
`rust/guard/src/guards/builder_brief_hooks.rs`). The GM, 2026-11-26: "is this also part of our checklist-based process for kicking
off and managing builders? Or do we not have such a checklist? ... I just want to make sure that we're putting the instructions in
the right place". `make builder-brief T= F= KIND=` sizes a brief, takes the pool tree and prints the standing block, whose first
line is a marker; the guard refuses a builder's dispatch - an ad-hoc agent whose prompt names a pool tree - without it.

Weighed and not taken: reading the jobs out of a brief's prose (the count is the caller's `JOBS=`, and a guard that parsed prose
would refuse correct briefs); the guard reading the task's line to refuse an unsplit mechanism (the command does, before a tree is
taken); a longer block that quotes the rules (the prefix guard refuses a prompt repeating 2,000 characters of an earlier one, so
the block stays under that and names `scripts/container/builder-brief.md`). What the guard does not catch is listed at the head of
its file: a marker typed by hand, more jobs than `JOBS=` states, a builder sent to work in the clone itself with no pool tree
named (17 ad-hoc dispatches of the replay's day named none, builders of the clone among them), a source edit a measurement brief orders outside a `Job <n>` line.

A bundle (`T=a,b`: tasks one builder builds in one tree, as T299 and T282 were on 2026-11-26) is briefed as one, the marker naming
both, where `make builder-tree T=a,b` hands the tree out: an escape on every bundle would spend this entry's falsifier on correct work.
