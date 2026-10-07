# Implementation Plan: The implementation brought to the research, easiest first

**Spec**: `spec.md` | **Request**: `request.md` | **Created**: 2026-10-07

## Summary

Phase 1 ranks every finding of `make claims-report` (565 at `a52ff1bcd`) by the implementation work it takes (tiers
E0-E4, spec FR-003). Phase 2 fixes them in ranking order, in waves that each land as a verified unit, all inside feature 328:
only the current wave's rows are task boxes; the next wave's tasks are appended as an amendment once a wave lands (FR-006). The work stops at the armed 75% usage cap (FR-007).

## Technical Context

- **Input**: `dev/claims-index.json` (the findings, each with `impl-drift`'s reason). Snapshot committed as
  `findings.json` in this directory, so the ranking is checked against the report the audit read.
- **Output**: `ranking.json` (one object per finding: key, verdict, tier, fix, files, after, flag, wave) and
  `ranking.md` (the readable table, generated from the JSON, grouped by tier then module).
- **Check (FR-001)**: `tests/test_328_ranking.py` - every key of `findings.json` appears in `ranking.json` exactly once,
  with a tier in E0-E4 and a non-empty fix; `ranking.md` is current with the JSON.
- **Verification of a fix**: `make claims-bundle UNITS=<keys>` -> `impl-drift` -> `make claims-checked`; IN-STEP
  required. Then `make done` (lint, statics, pool roll, 100% coverage).
- **Reference artifact**: `pool/hamlets/inashiro.gen.py` (the hamlet every hamlet change is first proven on), then the
  pool (`make maps`). Mode A procedure fixes have no generator; their sheets are hand SVGs.

## Phase 1 - the audit (the GM's first step)

1. Snapshot the findings (`findings.json`, 565 rows).
2. Nine Opus agents, each one batch of 47-76 findings grouped by module, read-only, with the tier rules and the GM's
   direction in their brief (`ranking-brief.md`, committed). Each returns JSON Lines.
3. Merge to `ranking.json`; generate `ranking.md`; the test holds coverage of every key. The E0 rows the batches
   tiered on the brief's earlier, unbounded wording (any E0 that is not MISLABELED or UNCLAIMED) get a bounded re-check by
   a fresh Opus reader: each stays E0 only with a named page that already says what the code does, otherwise it is
   re-tiered by the implementation work. A row a dependency outranks takes that dependency's tier.
4. A second Opus reader samples 30 rows across tiers and re-tiers them blind; where it disagrees by more than one tier on
   more than 5 rows, the disagreeing batch is re-run (an estimate that does not reproduce does not order the work).
5. Commit; the ranking is the order of every later wave.

## Phase 2 - waves

- **Wave order**: E0 first, then E1, E2, E3, E4. Within a tier, by module, so one claims bundle and one re-check covers
  a module's rows; a row with `after` waits for its dependency.
- **Wave 1 (this feature)**: every E0 row - the claim lines corrected, no change to what a map draws. Re-checked with
  `impl-drift` by module. No map regeneration owed (no engine behavior moves); the gate runs because docstrings in
  `l7r/**` are engine files for the claims gate even though comment-only for the route.
- **Later waves (amendments to this feature's `tasks.md`)**: E1 by module (values; the reference hamlet, then the pool); E2; E3 (including
  the Mode A sheets); E4 (a research pass under the record's own checks before any code change).
- **Exception path**: a row flagged `deviation-tempting` is put to `spec-fidelity` with the request verbatim before it is
  fixed any other way (XVI).

## Wave 2 (amendment 1, 2026-10-07)

- **Scope**: the first sixteen E1 rows (`tasks.md` Phase 3). Eight are procedure text; eight are generator values
  (`hamletgen/cluster.py`, `consts.py` BUNDLE_PITCH, `hinterland/parcels.py`, `homesteads/farm_water.py`,
  `homesteads/fixtures.py`, `homesteads/wells.py`).
- **D5 - sheet rows re-tiered**: nine procedure rows the rankers put in E1 redraw a hand-drawn Mode A sheet (Ubame,
  Hayakawa, Ochiba, Hoshigaoka); FR-003 tiers a sheet redraw E3, so they moved there (`audit/overrides.json`).
- **D6 - the lane law is one wave**: the 32 E1 rows of `hamletgen/ways/` (wave 4) apply one rule set (0081's join reach
  and turn limits, 0246's 7 ft clear of a fence); fixed together, the lane network is never half under each law.
  `FOOTPATH_FABRIC_GAP` (consts.py) is the same constant as a lane-law row, so it waits for that wave.
- **Verification**: the reference hamlet first (`make map` on Inashiro, the PNG looked at), then the pool through the
  gate; the bookend pair `328-w2-start` / `328-w2-end` and the band's records; `impl-drift` on every touched unit.

## Wave 5 (amendment 4, 2026-10-07)

- **Scope**: the two open E0 rows, then the 23 E1 rows of the homestead and its fixtures (`tasks.md` Phase 6): the
  fixtures' seats and the privy's reach, the groves' crowns, conifer share and sun corridors (0037, 0038, 0071, 0072, 0080),
  the belt's least depth, the bundle's garden cap, the kura's west annex (0040), the farm wells' reach and dooryard (0196).
  Ranking order: the next modules of E1 after the lane law, each module's rows in one claims bundle.
- **D7 - the row street waits**: its fix sets 0033 (the street runs on off the map) against 0246 (a way pulled back to
  the last door it serves); it is read before it is tiered, so it is not a one-value fix in this wave.
- **Verification**: as wave 4 - the reference hamlet first (`make map` on Inashiro, the PNG looked at), then the pool
  through the gate; the bookends back to back (start in a detached worktree at main, end in the clone); `impl-drift` on
  every touched unit; a held value becomes a found row (spec Edge Cases).

## Performance bookends (constitution VI)

Wave 1 changes no engine behavior (claim lines only) - no bookend owed. Each later wave that changes engine behavior takes
`make perf LABEL=328-w<N>-start` / `-end` itself.

## Constitution Check

- I, II: N/A - no UI in this repository.
- III: N/A - no new pool content kind.
- IV, V: PASS - no SOURCE block touched.
- VI: PASS - each fix's verification is listed above (impl-drift IN-STEP, `make done`, maps where drawing changes, review
  occasions per feature 294).
- VII, VIII, IX: N/A - no in-world content, no setting detail.
- X: PASS - the one new Python file is a test; ruff/pyrefly/coverage hold through `make done`.
- XII: PASS - wave 1 draws nothing new; later waves carry their own opening (the cited research IS the opening: each fix
  matches an existing question) and closing (the rendered PNG re-examined) bookends.
- XII decisions for the reader: PASS - each fix's class at the claim line; the program decisions in the spec's table.
- XIII: PASS - wave 1 is behavior-free; later waves take their baseline on the clone while its engine content is main's, before the wave's first edit (the same unmodified tree a detached worktree would hold, with its gitignored artifacts), per the wave's plan amendment.
- XVI: PASS - the direction (implementation to research) is the GM's; exceptions go to spec-fidelity.

## Decisions

- **D1 - waves as amendments (FR-006)**: only the current wave's rows are boxes; the wave lands when they are ticked, then
  the next wave is appended and reviewed on a reset counter.
- **D2 - wave 1 is E0 only**: it is the cheapest and has no map effect, so the ranking's first wave lands quickly and
  proves the re-check loop on the largest number of rows per unit of work.
- **D3 - batches by module**: one re-check per module, not per row; the claims bundle takes several units.
- **D4 - the second reader's sample (Phase 1.4)**: the tiers are estimates from a judging agent; one run is not a stable
  oracle (CLAUDE.md), so a sample is re-judged before the order is trusted.

## Project Structure

```text
specs/328-match-the-research/
  request.md  spec.md  plan.md  tasks.md
  findings.json      # the audit's input, snapshotted
  ranking-brief.md   # the audit agents' brief
  ranking.json       # the ranking (data)
  ranking.md         # the ranking (readable, generated)
tests/test_328_ranking.py
```
