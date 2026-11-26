---
kind: adopted
title: the plan review record's merge driver
for: carrying a worktree's task into the session clone takes both tasks' plan verdicts with no hand merge of specs/*/plan-review.json, and never a false CLEAR
measured: 2026-11-25
measurement: the parallel trials 2-5: every carry-over conflicted on plan-review.json and was merged by hand as JSON; a scratch repo holding the real 2.8 MB record, two branches each adding a task's and a block's entry and a block_reviews row: git's text merge left 3 conflict hunks, the registered driver merged clean with both kept (303 rows to 305)
command: bash tests/hooks/test-sync-with-main.sh (case Z2); make rust-test CRATE=rust/gate/crates/plan (plan/merge/tests.rs)
falsifier: a hand merge of plan-review.json again, or a merged entry reading CLEAR on a text nobody cleared
threshold: one hand merge in a batch, or one false CLEAR
cost: none on the common path - it runs only at a merge or cherry-pick of the record (make task-time books no row for it)
last-audited: 2026-11-25
cadence-days: 30
---

451 T256: `.gitattributes` marks `specs/*/plan-review.json` `merge=plan-review`; `scripts/sync-with-main.sh`'s `ensure_git_config`
defines the driver at every sync-in, which runs `l7r-gate plan merge-record %O %A %B` (`rust/gate/crates/plan/src/plan/merge.rs`):
three-way, key by key, each entry whole, the later review winning a clash, `block_reviews` keeping every row. Chosen over per-task
files, which would touch about 39 files where the driver touches 4 (measured 2026-11-25, a grep over `rust/` and `scripts/`).
