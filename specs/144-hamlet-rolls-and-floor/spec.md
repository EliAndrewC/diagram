# Feature Specification: the hamlet coverage floor, and the sixteen-second roll

**Feature Branch**: none - `specs/144-hamlet-rolls-and-floor` (`SPECIFY_FEATURE=144-hamlet-rolls-and-floor`)
**Created**: 2026-08-28
**Status**: APPROVED by `spec-fidelity` - round 1 (2026-08-28) asked four changes (keep the settlement ratchet; tests not deletions; the unit-test time must be REDUCED; the 8 s / 40% figures are the session's targets, a miss is reported), all applied; round 2 verdict FAITHFUL. Implementation proceeds.
**Input**: [`gm-request.md`](gm-request.md), the GM's words verbatim (two messages, 2026-08-28)

## What the GM asked for

Two things, in the order the GM gave them, plus one ruling:

1. **A 100% coverage floor on "the hamlet generation and anything included with that", enforced automatically** - "I want that threshold to be automatic rather than something that we just remember to maintain if possible." Cities, towns and villages are exempt because nothing exercises them yet and "they might be deleted entirely". The GM anticipated the hard case ("some things where it's not obvious whether they relate only to hamlets or not") and then ruled on it: **module level is fine for now**, "because eventually, we will just go back to one hundred percent code coverage everywhere".
2. **Make the rolls fast** - "The roles themselves being sixteen seconds each sounds like the next obvious place to look ... What are we doing billions of computations on exactly?" - with an explicit release: "maps are now allowed to move. So if the only reason why we weren't fixing that was to keep the maps the same, then we should just go ahead and fix it." The GM's first interest is "the seventeen seconds of genuine unit tests. especially with the settlement geometry" - which are the same geometry at test size, so they shrink with the rolls and are re-measured after.

## User Scenarios & Testing

### US1 - the floor holds itself (Priority: P1)

A session adds a function to a module the scripted hamlet roll executes and writes no test for it. The next `make done FULL=1` (or the idle run) fails the coverage floor and names the module and lines. A session adds a city-only branch to a module the hamlet roll never touches - nothing fails. When the scripted tier grows to villages, the module set grows with it and no one edits a list.

**Acceptance**: the set of modules under the 100% floor is DERIVED from what the scripted rolls execute (the roll cache's recorded dependencies, module level), not hand-listed; a test proves that deleting a covering test turns the floor red, and that a module no scripted roll executes is not in the set.

### US2 - a roll costs what its geometry costs (Priority: P1)

The reference hamlet rolls in materially less than 16 s and the cohort's slow seeds in materially less than their present times, with every map still passing the gate, the pool still clean and every regression fixture still firing. Maps may move.

**Acceptance**: the perf bookends (`144-start` / `144-end`) show the reduction per seed and in total; `make done` (unlocked) is green; the settlement-review runs on the reference at acceptance (a moved map is a shipped map).

### US3 - the unit tests get faster (Priority: P1 - after US2 in ORDER only, because it depends on US2's measurement)

The GM's first-named interest: "the thing I am most interested in is the seventeen seconds of genuine unit tests. especially with the settlement geometry." Those tests exercise the same geometry at test size, so US2 is taken first and the pytest phase re-measured; whatever US2 does not deliver, the remaining settlement-geometry tests over the quick cutoff are made faster on their own merits in this feature.

**Acceptance**: the settlement-geometry share of the unlocked gate's pytest phase is REDUCED, measured before and after; any test deliberately left over the cutoff carries a written reason.

## Requirements

- **FR-001** The 100% coverage floor applies to every engine MODULE (file) that any scripted hamlet roll executes, and to nothing else by virtue of this feature (the existing floors on tooling modules stay as they are). The set is derived at floor time from the roll cache's dependency records for the reference settlement, the polder set and the cohort; a fallback list is refused, not silently used - if the records are absent the floor fails loudly and says how to produce them.
- **FR-002** The 100% hamlet-path floor is ADDED. The existing `settlement/` package ratchet (`SETTLEMENT_COV_FLOOR`) stays in place and is not lowered; modules the hamlet path does not execute acquire no new obligation (the GM: "it does not make sense to maintain code coverage for them because they might be deleted entirely"). Any hamlet-path module found under 100% at the first measurement is brought to 100% in this feature BY TESTS; `# pragma: no cover` is not used for it, and no engine code is deleted to make the floor green - if a hamlet-path module contains code only a non-hamlet tier reaches, that specific case is put to the GM (the GM: "eventually, we will just go back to one hundred percent code coverage everywhere").
- **FR-003** A guard test proves the floor fires (a module in the set with an uncovered line fails) and that a module outside the set does not.
- **FR-004** `stage_hinterland`'s per-sample polygon queries (point-in-polygon, distance-to-edge against the commons outline) are answered from a structure built once per outline, not by walking every edge per sample. Maps may change as a result.
- **FR-005** `fit_field` converges in fewer full carves than the present bisection (measured, recorded); the carve's own hot loops that scan unchanging geometry per candidate are hoisted or indexed. Maps may change as a result.
- **FR-006** Both changes are measured with the feature's perf bookends and recorded in `research.md` with the before/after per stage; a seed that gets SLOWER owes the feature-129 records.
- **FR-007** After FR-004/005, the gate's pytest phase is re-timed; the settlement-geometry unit-test time is REDUCED and the reduction recorded. Where FR-004/005 do not deliver it, the remaining tests over the quick cutoff are addressed on their own merits in this feature; anything deliberately left carries a written reason.
- **FR-008** The final task is the GM's acceptance, verbatim, after the session explains what changed and what remains.

## Success Criteria

- **SC-001** A measured, recorded, material reduction per seed and in total against the `144-start` bookend. The session's own targets - the reference roll under 8 s, the cohort total 40% below `144-start` - are stated here so a miss is REPORTED to the GM at acceptance, not treated as a failed criterion.
- **SC-002** The settlement-geometry unit tests' share of the gate's pytest phase is measurably lower than before the feature.
- **SC-003** `make done FULL=1` enforces 100% on every hamlet-path module and stays green.
- **SC-004** No regression: every gate check that passed on `144-start` passes on `144-end` for the reference, the polders and the cohort; the corpus fires as before.

## Assumptions

- "Hamlet generation and anything included with that" = the modules a scripted hamlet roll executes (module level, the GM's ruling). The interactive page and the check battery are on that path and therefore under the floor.
- "Maps may move" covers hinterland scatter and field convergence exactly as it covered the placement chords (feature 140).
