# Feature Specification: Rethinking the settlement review

**Feature Branch**: `294-settlement-review-rethink`
**Created**: 2026-09-30
**Status**: Requested - NOT STARTED. The GM asked for this feature to be filed and not worked until feature 291 lands
(request.md). It is specified from request.md when it is taken up.

## Summary

Review how the `settlement-review` process works in general - its time and token cost, when it fires (the pair guard's
"a pool map's layout moved" trigger), and what it catches that nothing else would - and change it where the measurement
says to; including the narrower tweak the GM agreed to consider: reviewing only the maps whose form or subject a feature
changed, or making the review opt-in per feature.

## Inputs to gather when this is taken up

- The review ledger (`docs/review-ledger.md`) and the review verdicts: per round, what was found, how much was a real
  defect a coded rule later absorbed versus a nitpick or wording point, and the round's wall time and tokens.
- Feature 291's rounds as a worked example (its spec's review history and `measurements.json`).
- The overhead a round imposes besides itself: the FR-003 records owed for every finding, the FR-004/FR-005 prerequisites,
  NOT-REVIEWABLE rounds on a red gate.
