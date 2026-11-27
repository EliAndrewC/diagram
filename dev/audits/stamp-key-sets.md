---
kind: adopted
title: suite and gate stamps keep a bounded set of content keys
for: trees of different content stop invalidating each other's green suite and gate stamps in the shared git dir, so a tree does not rerun a suite another tree's write displaced
measured: 2026-11-27
measurement: 451 T304's read of the event log since 2026-11-23 - 17,170 suite runs; under the two tiers (2026-11-26T19Z on) 194 of 1,072 suite runs (18%, an upper bound) followed another tree's stamp write; hooks-test reran in 32 of 37 gate runs that followed another tree's gate
command: make rust-test CRATE=rust/gate/crates/tree (stamp::tests::trees_of_different_content_keep_each_others_green_keys); bash tests/hooks/test-parts.3.sh (the A-B-A case)
falsifier: a suite rerun in a tree whose content key is among the kept keys, or a stamp passing content no kept key vouches for
threshold: one such rerun in a week's event log, or one stale pass (either reopens it); STAMP_KEEP and HOOKS_STAMP_KEEP at 6 are GUESS knobs - a tree count past 6 trees writing one suite is the measurement that would raise them
cost: one line per kept key read at each stamp check (microseconds, in make task-time's hooks-test and gate rows)
last-audited: 2026-11-27
cadence-days: 30
covers: STAMP_KEEP
---

451 T304 (`rust/gate/crates/tree/src/stamp.rs`, `tests/hooks/hookrun.sh`, `rust/guard/src/suite_tools/trace.rs`): the
`gate-green-<area>` stamp and each suite's `hooks-test/<guard>` stamp hold one key per line, newest first, bounded by
`STAMP_KEEP` and `HOOKS_STAMP_KEEP` (6 each, GUESS knobs); a check passes on any kept key, and each suite key keeps its own
rendering and trace. Built under the GM's go-ahead of 2026-11-27 ("go ahead and do all of the load-bearing ones").
