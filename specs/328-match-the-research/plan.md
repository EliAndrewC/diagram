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
  reads or an in-use knob's registration reads, a knob in use (the registry's knob resolved by name, or its typing rule run - not a hamlet's own `hamletgen/`
  table rolled under the same name) and a module-level claim on one, a class executed code constructs, any unit under `hamletgen/`, or a listed check the gate runs on the kept maps; a claim whose value no kept map
  reads is deferred with its measured reason; never the gate's tests of the legacy
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
- **Scope**: the 5 open in-scope E0 rows, then the next contiguous run of in-scope E1 (FR-006, FR-010): rows 265-297
  (26 rows, `tasks.md` Phase 10), the homestead's fixtures, groves and fields, the cover, the polder gate, the surface
  water and the bundle's garden; the next open in-scope E1 row is 303.
- **Verification**: Inashiro first (`make map`, the PNG looked at), the pool through the gate; the bookends back to back
  with nothing else running; `impl-drift` on every touched unit; a held value becomes a found row.

## Wave 10 (amendment 9, 2026-10-07)

- **Wave 9 first (FR-006)**: its gate failed on Kuwabata (a zigzag across a joint), bisected by row to the yard privy's step,
  held as its found row's (the re-seat rule, E3); with it held three scaling rolls refused their web, bisected by row to the
  wood shed's step, held as its found row's (the web's reach at 20 and 40 households, E3) - the spec's route (Edge Cases,
  FR-004), as wave 2 held the brook's weight. Wave 9 closes in full (impl-drift, a green gate, the wave column, no measured
  regression) and is pushed if its bookends read band 2 or lower.
- **The exception (amendment 9 round 2, LEGITIMATE on these conditions)**: if wave 9's bookends still read band 3, its push
  waits for the GM's sign-off at a terminal (the one thing the session cannot give), and wave 10 starts on top of it in the
  clone - wave 10's opening bookend taken at wave 9's closing commit, so each wave's band is its own; the sign-off question
  goes on the list for the end of the feature (the GM, 2026-10-07: "defer it to the end of the feature").
- **The exception for wave 11 (exception check, 2026-10-07, LEGITIMATE on conditions)**: wave 10 reads band 3 on its own too
  (its fork-triangle and ring-step rows, measured), so its push waits on the GM's sign-off as wave 9's does. Wave 11 may start
  on the unpushed waves 9 and 10 only: (1) wave 10 closed in full first - impl-drift recorded, a green gate, its glyph-check, the
  wave column, no measured regression - and the backup branch pushed at its closing commit (`sync-with-main.sh done`, refused
  landing or not); (2) wave 11's opening bookend at wave 10's closing commit, its band its own and explained, each wave's pair
  shown to the GM beside the combined landing pair; (3) no fixed depth, but stacking stops the moment anything other than the
  GM's sign-off would refuse the push (a refused roll, a regression, a red gate, an unanswered review or record check, a claims
  finding the delta introduced) - fixed within the wave first; (4) any lossless fix that brings the landing pair to band 2 or
  lower pushes at once; (5) the sign-off on the end-of-feature list, for each wave; (6) wave 11 its own amendment with a reset
  review counter and a plan review before its first tick; wave 12 is covered only if (1)-(5) still hold when wave 11 closes.
- **Tiers by work (FR-002, FR-003)**: wave 9's found rows tiered by their work by a fresh reader (T38a; T38b for the 18 found
  after), and its three NEEDS-RESEARCH rows E4 with the research first (spec Edge Cases); the north annex's band row is "keep
  the 18 ft floor" (E2), never a named exception.
- **Scope**: the 20 open in-scope E0 rows, then the last contiguous run of in-scope E1 (FR-006, FR-010): rows 290-354 (20 rows,
  `tasks.md` Phase 11); after it every open in-scope row is E2 or above (the next, row 355).
- **The exception check on the four DEVIATION relabels** (2026-10-07): NOT LEGITIMATE, each - the crowns-per-clump floor
  and ceiling dropped (E1, in this wave), the planted bank's two forms and the free-standing storehouse E3 with the two annex
  claims after the storehouse row.
- **Verification**: as wave 9 - Inashiro first, the pool through a green gate (FR-005), the bookends back to back;
  `impl-drift` on every touched unit; a held value becomes a found row.

## Wave 11 (amendment 10, 2026-10-07)

- **T42a first**: wave 10's 19 found rows tiered by their work (5 moved).
- **Scope**: the last open in-scope E0 and E1 rows - 8 claims and 3 values (`tasks.md` Phase 12); after them every open
  in-scope row is E2 or above (the next, row 365, a Mode A procedure row).
- **On the unpushed waves 9 and 10** under the wave-11 exception (Wave 10 above): wave 10 closed in full at 6be618a9e, its backup
  pushed; wave 11's opening bookend at that commit; stacking stops the moment anything but the GM's sign-off would refuse the push.
- **Verification**: as wave 10 - Inashiro first, the pool through a green gate, the bookends, `impl-drift` on every touched unit.
- **Before any push of the stack**: the push's perf gate reads only the NEWEST pair, and wave 11's own pair (band 0) is now
  the newest - so the main-to-HEAD landing pair is retaken as the newest pair before the push, and the GM signs off its band
  with each wave's own pair beside it (waves 9 and 10 band 3, wave 11 band 0). A push on wave 11's pair alone would skip the
  sign-off the stack owes.

## Wave 12 (amendment 11, 2026-10-07)

- **T46a first**: wave 11's 12 found rows tiered by their work (none moved).
- **Scope**: wave 11's found E0 and E1 rows - 8 claims and 2 values (`tasks.md` Phase 13); after them every open in-scope
  row is E2 or above (the next, row 375).
- **On the unpushed waves 9-11** under the wave-11 exception's condition (6): (1)-(5) held at wave 11's close (6760d9bbf, its
  backup pushed, its own pair band 0); wave 12's own pair opens at 6760d9bbf.
- **Verification**: as wave 11.

## Wave 13 (amendment 12, 2026-10-07)

- **The Mode A rows sorted** (exception check, 2026-10-07): the Mode A sheets are in scope by the GM's words, so nothing is asked;
  FR-003 makes a row that redraws a hand sheet E3 - 6 rows re-tiered by a fresh reader's measurement of the sheets.
- **Scope**: wave 12's two byre claims, then the procedure-only Mode A E2 rows in ranking order (`tasks.md` Phase 14); the
  procedures change, each sheet records its roll in its notes - a seeded roll where the page says rolled, its expression written -
  and a row whose roll lands on a form the sheet does not draw is E3 (the second kami: Hayakawa's river kami and Ubame's wood kami). The country shrine's size bands widen in
  `types.json` (the generated table follows); Hoshigaoka's drawn sizes fall inside them.
- **On the unpushed waves 9-12** under the wave-11 exception's condition (6): (1)-(5) held at wave 12's close (c45460dd1, its
  backup pushed, its own pair band 0).
- **Verification**: `impl-drift` on the touched procedure claims, the gate, wave 13's own bookend pair.

## Wave 14 (amendment 13, 2026-10-07)

- **T51a first**: wave 13's 13 found rows tiered by their work (3 moved: one to E0 with its basis, two to E3).
- **Scope**: the 8 open in-scope E0 rows, all claims of the Mode A procedures (`tasks.md` Phase 15); no procedure text, sheet or
  engine line changes. After them the open in-scope rows are E2 and above (the deferred E1 rows aside).
- **On the unpushed waves 9-13** under the wave-11 exception's condition (6): (1)-(5) held at wave 13's close (2e0268412, its
  backup pushed, its own pair band 1 confirmed by perf-audit); wave 14's own pair opens at 2e0268412.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 14's own bookend pair.

## Wave 15 (amendment 14, 2026-10-07)

- **The filer reopens a closed row** (found 2026-10-07): wave 13's re-check called four rows of closed waves out of step, and
  the filing script had skipped every key already ranked; it now files such a finding as a found row and takes the row out of
  `waves.json`, its closing wave kept in `reopened`. T53a tiered the four by their work.
- **Scope**: the one open E0 row, then the E2 run in ranking order - six Mode A paragraphs and `hamletgen/cluster.py`'s two drain
  rows (`tasks.md` Phase 16). The seat loses its drain refusal (0058: a dispersed farmstead's rule, never a nucleated cluster's);
  the per-farm rule no seat enforced is filed E3. The stage and sumo-ring rows take the finding's second remedy - the default
  claimed as 0222's drawing page's GUESS - since a roll contradicts that page (tried, and withdrawn with its modal edits).
- **The scope script keeps the page path** (spec-fidelity's aside, amendment 13 round 2): `render_png`, the raster tiles, the page
  vocabulary's tables and every Kind a kept map records a feature under.
- **On the unpushed waves 9-14** under the wave-11 exception's condition (6): (1)-(5) held at wave 14's close (68ee171f4, its
  backup pushed, its own pair band 1 confirmed); wave 15's own pair opens at 68ee171f4.
- **Verification**: `impl-drift` on the touched claims, the gate with the pool hamlets regenerated, wave 15's own bookend pair.

## Wave 16 (amendment 15, 2026-10-07)

- **T56a first**: wave 15's found rows tiered by their work (one stale row dropped).
- **Scope**: the E0 row, the privacy-baffle paragraph, then the E2 engine rows in ranking order through the notice board's siting
  (`tasks.md` Phase 17), with `stage_windbreak`'s two copse rows taken with `COPSE_SITINGS` (one retirement). Two knob forms
  feature 152 made from a settlement-review's candidates - the copse against the belt, the board at the drawing-water place - have
  no page behind them and are retired; each knob keeps its one form, so a spec declaring it still reads. Mizuguchi declared the
  belt-side copse only to exhibit that value; the declaration goes with it.
- **Occasions**: none, measured - the retired forms moved nothing drawn (Mizuguchi is linear and draws no copse; Kashikawa's and
  Sawada's boards stand where they stood); only each map's recorded knob changed.
- **On the unpushed waves 9-15** under the wave-11 exception's condition (6): (1)-(5) held at wave 15's close (799a0bf4b, its
  backup pushed, its own pair band 1 confirmed); wave 16's own pair opens at 799a0bf4b.
- **Verification**: `impl-drift` on the touched claims, the gate with the three maps regenerated, wave 16's own bookend pair.

## Wave 17 (amendment 16, 2026-10-07)

- **Scope**: wave 16's three UNCLAIMED rows (claims), then the E2 run: `WEB_HARD_GAP` measured E3 (five modules) and passed, the
  thicket's seat taken - every pass held just beyond the back row (its back edge, a labeled depth), the fallback along its whole length (`tasks.md`
  Phase 18). One stale found row dropped (its later round IN-STEP).
- **Occasions**: Kashikawa's thicket re-placed against its back row (a glyph check); Mizuguchi's unchanged (measured).
- **On the unpushed waves 9-16** under the wave-11 exception's condition (6): (1)-(5) held at wave 16's close (b49a6c221, its
  backup pushed, its own pair band 1 confirmed); wave 17's own pair opens at b49a6c221.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 17's own bookend pair.

## Wave 18 (amendment 17, 2026-10-07)

- **T61a first**: wave 17's found rows tiered by their work (two already fixed in wave 17).
- **Scope**: the two open E0 claims and the E2 run's head - the thicket's 70% passes dropped (`tasks.md` Phase 19).
- **Occasions**: none, measured - both pool thickets were seated at full size; their manifests are unchanged.
- **On the unpushed waves 9-17** under the wave-11 exception's condition (6): (1)-(5) held at wave 17's close (8c3b5cdef, its
  backup pushed, its own pair band 1 confirmed); wave 18's own pair opens at 8c3b5cdef.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 18's own bookend pair.

## Wave 19 (amendment 18, 2026-10-07)

- **Scope**: the next two E2 rows in ranking order - the belt into the marsh (its trees there alder, 0074 drawing) and the wood
  beyond the fields (0077 drawing), inverting feature 261's settlement-review preference (`tasks.md` Phase 20).
- **Occasions**: the woodland commons re-placed on Inashiro and Kashikawa (a glyph check each); the belt change moved no pool map
  (measured: each hamlet's manifest unchanged by it).
- **On the unpushed waves 9-18** under the wave-11 exception's condition (6): (1)-(5) held at wave 18's close (822e44c52, its
  backup pushed, its own pair band 1 confirmed); wave 19's own pair opens at 822e44c52.
- **Verification**: `impl-drift` on the touched claims, the glyph checks, the gate, wave 19's own bookend pair.

## Wave 20 (amendment 19, 2026-10-07)

- **T65a first**: the glyph check's found row tiered E2.
- **Scope**: four E2 rows in ranking order (`tasks.md` Phase 21): the level wood's real crossing, the seat order's tie toward the
  field, and the bath room's wall rolled per house at the registers' share.
- **Occasions**: the woodland commons re-placed or recorded off the sheet - the walk through the field asked on every tier
  (0077: beyond the fields and higher than them): Kashikawa one wood where three stood, Inashiro and Mizuguchi none on the sheet
  (recorded beyond it, N and W); the woodland glyph check's NEEDS-WORK fixed and verified by measurement (its two rounds spent).
- **On the unpushed waves 9-19** under the wave-11 exception's condition (6): (1)-(5) held at wave 19's close (43b353361, its
  backup pushed, its own pair band 1 confirmed); wave 20's own pair opens at 43b353361.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 20's own bookend pair.

## Wave 21 (amendment 20, 2026-10-07)

- **T67a first**: wave 20's two UNCLAIMED rows tiered E0.
- **Scope**: the two open E0 claims (`tasks.md` Phase 22); no code a map executes changes.
- **On the unpushed waves 9-20** under the wave-11 exception's condition (6): (1)-(5) held at wave 20's close (2ba8a8154, its
  backup pushed, its own pair band 1 confirmed); wave 21's own pair opens at 2ba8a8154.
- **Verification**: `impl-drift` on the two claims, the gate, wave 21's own bookend pair.

## Wave 22 (amendment 21, 2026-10-07)

- **Held and passed**: row 427 held for the GM (the research's shrine cap against the GM's T61 floor; exception check
  LEGITIMATE); row 428 measured E3 (two modules). Scope: row 429, the far-row holding three lots deep (`tasks.md` Phase 23).
- **Occasions**: the farm holding re-placed on Kashikawa (a glyph check); the other four manifests unchanged.
- **On the unpushed waves 9-21** under the wave-11 exception's condition (6): (1)-(5) held at wave 21's close (3c997ab6b, its
  backup pushed, its own pair band 1 confirmed); wave 22's own pair opens at 3c997ab6b.
- **Verification**: `impl-drift` on the touched claims, the glyph check, the gate, wave 22's own bookend pair.

## Wave 23 (amendment 22, 2026-10-08)

- **Scope**: six of wave 22's seven found rows, E0 by a fresh reader (T71a), written as claims (`tasks.md` Phase 24); no
  executed code changes. The well row is withdrawn as a drift (the curb is the page's 19 ft). The seventh,
  `seat_rows#farms to a street` (NEEDS-RESEARCH), is E4 and waits for its research pass (amendment 22 round 1).
- **Occasions**: none.
- **On the unpushed waves 9-22** under condition (6): (1)-(5) held at wave 22's close (049e951d4, its backup pushed, its own
  pair band 1 confirmed with a control); wave 23's own pair opens at 049e951d4.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 23's own bookend pair.

## Wave 24 (amendment 23, 2026-10-08)

- **Scope**: rows 436-438 in ranked order (434 held for the GM); row 437's step, found about 111 ft against 0038's 92 ft
  (envelope + lane room + sun added), is fixed by laying the rank's lane inside the yard's sun - the gap the larger of the two and wave 23's one found row, tiered first (`tasks.md`
  Phase 25). The rank step owes the yard's sun whichever way the ranks run (0038: no farmhouse within 39 ft south of a
  yard); the sty takes the bank seat nearest the houses (0025), the midpoints no longer ranked ahead.
- **Occasions**: none - the rank search is reached by no pool map; Kuwabata's sties move a few feet along their own bank.
- **On the unpushed waves 9-23** under condition (6): (1)-(5) held at wave 23's close (397c005fb, backed up, its own pair
  band 1 confirmed); wave 24's own pair opens at 397c005fb.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 24's own bookend pair.

## Wave 25 (amendment 24, 2026-10-08)

- **Scope**: wave 24's found rows, tiered by a fresh reader (T75a): the E0 rows claimed or confirmed (`tasks.md` Phase 26);
  the scattered hamlet's rank rounds tiered E3 and left for its place in the run. No executed code changes.
- **Occasions**: none.
- **On the unpushed waves 9-24** under condition (6): (1)-(5) held at wave 24's close (5947e79ae, backed up, its own pair
  band 1 confirmed with a control); wave 25's own pair opens at 5947e79ae.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 25's own bookend pair.

## Wave 26 (amendment 25, 2026-10-08)

- **Scope**: row 447 (`tasks.md` Phase 27): a hamlet's drain registers no 33 ft no-build corridor, the town and city maps'
  rule (0058). A nucleated cluster is exempt from the below-drain rule; the dispersed farmsteads' rule is open as row 669 (E3). Row 434 held for the GM.
- **Occasions**: none - the five pool hamlets are unchanged.
- **On the unpushed waves 9-25** under condition (6): (1)-(5) held at wave 25's close (8e6e380ad, backed up, its own pair
  band 0); wave 26's own pair opens at 8e6e380ad.
- **Verification**: `impl-drift` on the touched claim, the gate, wave 26's own bookend pair.

## Wave 27 (amendment 26, 2026-10-08)

- **Scope**: rows 448-451 (`tasks.md` Phase 28): the brook below its tap never climbs - a run across the fall takes no dip
  down it, the downhill check is strict, the 8 ft allowance retired (0054: strictly under 90); `flanks_commanded` as 0053
  states it - a flank of 150 ft or less not judged, a judged flank owed 80 ft or 30%, the lesser; the test that pinned the
  old refusal brought to the page. A first trial's E3 re-tier of the brook rows is withdrawn (amendment 26 round 1). Row
  434 held for the GM.
- **Occasions**: none - the five pool hamlets are unchanged.
- **On the unpushed waves 9-26** under condition (6): (1)-(5) held at wave 26's close (2657e36a5, backed up, its own pair
  band 0); wave 27's own pair opens at 2657e36a5.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 27's own bookend pair.

## Wave 28 (amendment 27, 2026-10-08)

- **Scope**: row 452 (`tasks.md` Phase 29). Its suggested fix, no edge wander, drew the rectangle 0027 and the GM's
  2026-09-28 ruling exclude (the glyph check, F1); 0019/0022's "fixed outer edge" means the drift leaves the edge alone. The
  code already curves the dike with the water as 0027 draws it, so the change is reverted and the row is E0: the claim
  restated against 0027, the 0.86 box-fill walk-down labeled a CONVENTION, a comment corrected. The knot form the trial
  needed is reverted with it and its gap filed as a found row. Row 434 still held.
- **Occasions**: none - no executed code differs from wave 27's close (the engine diff is comments and docstrings only).
- **On the unpushed waves 9-27** under condition (6): (1)-(5) held at wave 27's close (f51fbbbe4, backed up, its own pair
  band 1 diagnosed as load); wave 28 changes no executed code, so it owes no pair.
- **Verification**: `impl-drift` on the restated claim, the gate green.

## Wave 29 (amendment 28, 2026-10-08)

- **Scope**: wave 28's found rows tiered by a fresh reader (T83a): the E0 claims written in `_polder_candidate` (`tasks.md`
  Phase 30); the knot gap tiered E2 and left for its place in the run. No executed code changes.
- **Occasions**: none.
- **On the unpushed waves 9-28** under condition (6): (1)-(5) held at wave 28's close (792d74111, backed up); wave 29
  changes no executed code, so it owes no pair.
- **Verification**: `impl-drift` on the touched claims, the gate.

## Wave 30 (amendment 29, 2026-10-08)

- **Scope**: row 458 (`tasks.md` Phase 31), tried and reverted: 0061's two or three tenths of the paddy covers a high-ground
  pond that is its fields' only water, not a polder's source, the wild water its inlet sluice draws from, and no page sizes
  that; the fixed ellipse is claimed UNRESEARCHED and the row re-tiered E4, research first. Row 434 held for the GM.
- **Occasions**: none - no executed code or map differs from wave 29's close.
- **On the unpushed waves 9-29** under condition (6): (1)-(5) held at wave 29's close (2e33f31b3, backed up); wave 30
  changes no executed code, so it owes no pair.
- **Verification**: `impl-drift` on the relabeled claim, the gate.

## Wave 31 (amendment 30, 2026-10-08)

- **Scope**: row 459 tried and re-tiered E3 by measurement (its literal fix leaves Mizuguchi's field spur 22 ft off the
  street's end - a knot the pool test refuses - and the spur is laid downstream of the pass); row 460: `lanes_share_tread`
  and `served_network` join two lanes only where their treads meet (the ink tolerance), not anywhere within the 25 ft join
  reach - 0081's 25 ft is the knot pass's, joining ends at one point. The test that pinned 20 ft apart as joined brought to
  the page. Row 434 held for the GM.
- **Occasions**: none - no pool map changes.
- **On the unpushed waves 9-30** under condition (6): (1)-(5) held at wave 30's close (9a29aee8f, backed up); wave 31's
  own pair opens at 9a29aee8f.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 31's own bookend pair.

## Wave 32 (amendment 31, 2026-10-08)

- **Scope**: wave 30's found rows tiered by a fresh reader (T89a): two E0 claims written in `stage_polder` (the dike-pond
  conversion to 0020's drawing page, the polder fabric to 0022's; `tasks.md` Phase 33); the pond layout re-tiered E3 after
  impl-drift found it DRIFTED (the chessboard is attested and never rolled), left open; the reservoir's seat and the inlet
  stub tiered E2 and left for their place in the run. No executed code changes.
- **Occasions**: none.
- **On the unpushed waves 9-31** under condition (6): (1)-(5) held at wave 31's close (7f35ded74, backed up, its own pair
  band 0); wave 32 changes no executed code, so it owes no pair.
- **Verification**: `impl-drift` on the touched claims, the gate.

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
