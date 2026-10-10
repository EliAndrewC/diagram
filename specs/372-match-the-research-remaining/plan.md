# Implementation Plan: the rows feature 328 left open (feature 372)

**Spec**: `spec.md` | **Request**: `request.md` | **Model**: `specs/328-match-the-research/plan.md` (its D1-D4, its wave cycle,
its batch close and its bookends) - this plan records only what differs and each wave's amendment.

## Summary

The work list is 328's ranking's open in-scope rows at wave 97, in ranking order, with the findings carried at its landing
(spec, "What it carries"). Waves are numbered on from 328's (the first is wave 98), so 328's `audit/waves.json` stays the one
column; this feature's measurements are its own `measurements.json`, its decisions its own spec's table.

## Constitution Check

As 328's (XII research, XIII no known regressions, XIV fix where found, XVI the literal thing); nothing new is owed.

## The cycle (328's, unchanged)

Edit -> test-file -> `make map` for each map the wave changes (the pool's hamlets diffed against HEAD's manifests; a Mode A
sheet's `make pack-audit` before and after) -> `make cohort N=48` when engine code changes (52/54 at the start; a newly failing
seed is a regression, reverted with its measurement) -> `impl-drift` on the owed claims -> records -> `make quick` ->
`spec-fidelity` -> tick -> commit. A batch of 4-5 waves closes with `make done`, its occasions, one timing pair and its
`perf-audit`, and LANDS (spec FR-003).

## Wave 98 (amendment 1, 2026-10-10) - batch 1

- **Scope**: `docs/buildings.md::Latrines and the rear service strip#privy size` (328's ranking, E3: the procedure allowed
  14-20 px, ~5-7 ft, and the hand sheets drew up to 22 px; 0101's drawing page draws a privy 5 ft square, a one-seat privy,
  its size a GUESS). Sheets redrawn (328's FR-009 by FR-002): **Hayakawa** (5 privies), **Ochiba** (4), **Ubame** (4) - every privy 15 x 15 px,
  kept against the wall or house face its nearest edge stood on (each anchored on the side with the smaller measured gap; a
  privy between two faces centered). The generated sheets (the county example, the roundtrip test) and Hoshigaoka already
  draw 15 px.
- **The section's re-check** (impl-drift, 9 claims): `#privies away from water` (328's E4 row) MISLABELED - relabeled GUESS
  at 0101's 15 ft from a well, the food-prep half UNRESEARCHED, as its own claim; three unclaimed decisions claimed (the
  privy's glyph, a CONVENTION; the rear strip as the service side and its storehouses, 0091). `#residence privy attached` and
  `#servants in the rear strip` re-read DRIFTED, as ranked (E3), left for their place in the run.
- **Records**: the procedure's claim (GUESS, 0101 drawing) and its body text; each sheet's notes history; `make pack-audit`
  before and after unchanged on all three sheets (m:wave98-privy-size).
- **Occasions**: glyph-redrawn: latrine on ubame-magistracy (one map stands for the three; the same glyph, the same size).
- **Verification**: the three `make map` runs (REGENERATED, no untagged ink), the pack audits, `impl-drift`, `spec-fidelity`.

## Performance bookends (constitution VI)

| batch | waves | pair | gate | close |
|---|---|---|---|---|
| 1 | 98- | owed at the batch close | at the batch close | open |
