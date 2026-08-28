# Implementation Plan: the hamlet coverage floor, and the sixteen-second roll

**Feature**: 145 | **Spec**: [spec.md](spec.md) (FAITHFUL, round 2) | **Date**: 2026-08-28

## Constitution Check

- VI (verification): perf bookends `144-start` (taken 2026-08-28T16:38Z, total 128.2 s over seeds 4/25/39/47) and `144-end`; unlocked `make done`; `make done FULL=1` for the floor (SC-003); settlement-review on the reference at acceptance (maps move).
- X (100% coverage on pure-logic packages): the feature EXTENDS the floor; nothing is exempted. The new floor is derived, and a guard test proves it fires (FR-003).
- XII (research): every task is `research: rendering` - nothing here is about how a place was built; the maps that move do so within rules already researched and recorded.
- XIII/XIV: baseline = `144-start`; every check that passes on it passes on `144-end` (SC-004); defects found on the way are fixed here.
- XVI: the spec was reviewed against the GM's words by `spec-fidelity`, two rounds.

## Technical approach

1. **The floor** (FR-001..003). `make test-full` (COV_FLOORS=1) gains a phase after the existing two reports: `python3 -m l7r.diagram.ci hamlet-floor` (or a `tools/` module - decided at T10 by where `rollcache`/`gencache` deps are read today) lists the module set = the union of `deps.functions` file paths recorded in the roll cache for the reference settlement, the polders and the cohort seeds, mapped to `l7r.diagram...` module names; refuses (exit 2, message names `make reference` / `make perf` as the producers) when no record exists; then `coverage report --include=<those files> --fail-under=100`. The settlement ratchet report stays. Guard test: a fixture coverage data file + a synthetic module set; a module in the set with a missed line fails, one outside passes.
2. **The hinterland** (FR-004, done in the clone): `RingIndex` in `_geom/indexes.py`, used by `commons` and `marsh`; then the crop-margin test inside `boxed_hit` (edge_dist over whole paddy rings per candidate - 18k calls, 2.4 s profiled) gets the same treatment.
3. **The field** (FR-005, done in the clone): `_predict_k` power-law step with the bracket kept; measured 4 carves -> 2 on the reference.
4. **Measure** (FR-006/007): `make perf LABEL=144-end`, `make durations` before/after for the settlement-geometry tests, recorded in research.md.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| the scatter's inside/feather answers come from an edge index - verdicts identical to the linear scan | rendering (an implementation of an existing rule; nothing physical changes) | `RingIndex` docstring |
| the field solver predicts the size multiplier by a power law instead of halving the bracket | rendering (the acreage rule and tolerance are unchanged; which fan is drawn may change within tolerance) | `_fit_at_aspect` comment, `_predict_k` docstring |
| the 100% floor is the set of modules the scripted rolls execute, module level | the GM's ruling 2026-08-28 | spec FR-001, gm-request.md |
