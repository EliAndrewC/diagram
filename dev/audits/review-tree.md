---
kind: adopted
title: a plan review records its verdict in the tree it reviewed
for: a plan reviewer dispatched on a worktree's task records its verdict in that worktree at the first try, and one that records from another tree is told which tree holds the text
measured: 2026-11-25
measurement: the parallel trials 2-5: spec-fidelity ran make plan-verdict from the session clone, where a worktree task's section was still the template, and was refused on a section-hash mismatch in five tasks, each re-recorded by hand
command: make rust-test CRATE=rust/gate/crates/plan (the bundle's MANIFEST test and the refusal naming the worktree)
falsifier: a plan verdict refused for the wrong tree again in a parallel batch
threshold: more than one such refusal in a batch
cost: the MANIFEST's two lines and, on a refusal only, one git worktree list (make task-time books no row for it)
last-audited: 2026-11-25
cadence-days: 30
---

451 T257 (`rust/gate/crates/plan/src/plan/bundle.rs`, `elsewhere.rs`, `record.rs`; `.claude/agents/spec-fidelity.md`): the MODE 4
bundle's MANIFEST names the tree it was built from and gives `make -C <tree> plan-verdict ...`; `make plan-verdict`'s section
checks, on a mismatch, look in the trees `git worktree list` names and the refusal names the one that holds the reviewed text.
