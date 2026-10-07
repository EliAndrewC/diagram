# Implementation Plan: The implementation brought to the research, easiest first

**Spec**: `spec.md` | **Request**: `request.md` | **Created**: 2026-10-07

## Summary

Phase 1 ranks every finding of `make claims-report` (565 at `a52ff1bcd`) by the implementation work it takes (tiers
E0-E4, spec FR-003). Phase 2 fixes them in ranking order, in waves that each land as a verified unit, all inside feature 328:
only the current wave's rows are task boxes; the next wave's tasks are appended as an amendment once a wave lands (FR-006). The work stops at the armed 85% usage cap (FR-007).

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

- **Scope**: the two open E0 rows, then the next contiguous run of E1 (FR-006): row 143 (the row street) and rows 148-173
  (`tasks.md` Phase 6) - the tier glossary, the caption leader and its reach, the overlap matrix and taxonomy, the knobbed
  sizes, the castle, and the city's walls, bridges, canals, moat and governor's gate. 29 rows; the next run (the civic
  grounds onward) is the next wave.
- **D7 - the row street is 0033's**: a row village's street "runs on off the map as the road into it" (0033's drawing
  page); 0246's pull-back to the last house served is the clustered settlement's lane rule and does not govern it. So
  `trim_streets` no longer cuts a row street back to its last joint; the street runs to the frame. The pages do not
  conflict, so the row is fixed here, not re-tiered.
- **Verification**: the reference hamlet first (`make map` on Inashiro), Kashikawa and Mizuguchi for the row street (the
  PNGs looked at), then the pool through the gate; a town or city value no scripted map draws is proven by its unit test;
  the bookends back to back (start in a detached worktree at main, end in the clone); `impl-drift` on every touched unit;
  a held value becomes a found row (spec Edge Cases).
- **Closed rows keep their tier**: `audit/closed-tiers.json` records each closed row's tier at its wave's close and
  `audit/merge.py` keeps it, so re-tiering an open row never rewrites a closed one.

## Wave 6 (amendment 5, 2026-10-07)

- **Scope**: the 32 open E0 rows (`tasks.md` Phase 7), every one the re-checks of waves 4 and 5 found: claims to write,
  relabels to make. Claim lines only, so no map moves, no review occasion and no bookend.
- **D8 - a claim written or relabeled never carries a code change**: where the page a claim names answers the decision differently from the
  code (the inner moat's width, the rampart strip in px, the plank over a junction), the claim states the code against the
  page and the departure is ranked as a found row in its own tier, so E0 stays the claim alone (FR-003).

## Wave 7 (amendment 6, 2026-10-07)

- **T25a first**: the 34 found rows tiered by verdict alone (waves 4-6's re-checks) are tiered by their work by a fresh
  reader before the run is chosen, as T12a did before wave 3 (18 moved: three wall literals to E1, five claim relabels to
  E0, the water gate's arcade and the board's bridge-end seat to E3, the inner moat, the river tap's sweep, the plank's
  widest-left seat and the stone group to E2).
- **Scope**: the 7 open E0 rows, then the next contiguous run of E1 (FR-006): rows 183-234 (27 rows, `tasks.md`
  Phase 8), ending with the civic grounds' last row; the next open E1 row is 235. Mostly town and city values; the
  connector's clearance (0246's 7 ft against `LANE_CLEARANCE`'s 40) moves hamlet maps.
- **Verification**: as wave 5 - Inashiro first (`make map`, the PNG looked at), the pool through the gate, a town or city
  value by its unit test; the bookends back to back; `impl-drift` on every touched unit; a held value becomes a found row.

## Wave 8 (amendment 7, 2026-10-07)

- **T29a first**: the 14 found rows wave 7's re-checks tiered by verdict alone are tiered by their work by a fresh reader
  before the run is chosen (11 moved: the lane clearance and its stepped spur to E3, the skeleton margin, the plank's
  obliqueness ceiling, the kura's rear seat, the six jizo and the trough count to E2, the city figure to E4, three claim rows
  to E1 as values). Under D8 each E0 claim that states a drift names the found row that fixes it (`audit/found-wave8.jsonl`).
- **Scope**: the 18 open E0 rows, then the next contiguous run of E1 (FR-006): rows 187-247 (9 rows, `tasks.md`
  Phase 9, row 192 the farm frame found by round 1), ending with the civic grounds' last row; the next open E1 row is 253.
- **Verification**: as wave 7 - Inashiro first, the pool through the gate, a town or city value by its unit test; the
  bookends back to back; `impl-drift` on every touched unit; a held value becomes a found row.

## Scope (amendment 8, the GM 2026-10-07)

- **D9 - the feature fixes what the kept maps execute (FR-010)**: every row takes a scope from the gen cache's execution
  records (`audit/scope.py` -> `audit/scope.json`, shown in `ranking.md`): `kept` (a unit a kept map's own gen-cache entry -
  the pool hamlets, the magistracy sheets, the country shrine, on today's engine - records as executed, a constant such a unit
  reads, any unit under `hamletgen/`, or a listed check the gate runs on the kept maps; never the gate's tests of the legacy
  village roller, a unit test's roll or a stale entry), `mode-a` (the procedures) or `deferred`. A wave takes only
  `kept` and `mode-a` rows, still the next contiguous run of those in ranking order (FR-006). The deferred list
  (`dev/claims-deferred.json`) covers every claimed unit the records do not reach, so a legacy-only unit that drifts later
  reads DEFERRED too; `scripts/_claims.py` reads it for `make claims-report` and the push's claims gate. Re-derived when a wave
  lands (the cache must hold each kept map's entry).
- **The cap**: 85% (the GM's words), the armed hook re-armed at 85.
- **Rows already worked in deferred code stay closed**: waves 5-8 fixed town and city figures before the scope existed; that
  work stands, and its open remainder is deferred.

## Wave 9 (amendment 8, 2026-10-07)

- **T34a first**: the 5 found rows wave 8 tiered by verdict alone, tiered by their work (3 moved: the bund's 6 ft reach and
  the web lane's arrival to E2, the skeleton arm's corridor to E3 after the edge-based corridor row).
- **Scope**: the 6 open in-scope E0 rows, then the next contiguous run of in-scope E1 (FR-006, FR-010): rows 265-297
  (26 rows, `tasks.md` Phase 10), the homestead's fixtures, groves and fields, the cover, the polder gate, the surface
  water and the bundle's garden; the next open in-scope E1 row is 303.
- **Verification**: Inashiro first (`make map`, the PNG looked at), the pool through the gate; the bookends back to back
  with nothing else running; `impl-drift` on every touched unit; a held value becomes a found row.

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
