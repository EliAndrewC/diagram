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

## Wave 33 (amendment 32, 2026-10-08)

- **Scope**: row 461 (`tasks.md` Phase 34): a farm's own garden beds, sheds, byres and retirement house are obstacles to its
  own path, only its dooryard (and its grove band) its own (0246: the way leaves round its own beds and fixtures). Row 434
  held for the GM; row 462 (the track's inner end joined however far) needs a routed run and is the next wave.
- **Occasions**: none - the five pool hamlets are unchanged.
- **On the unpushed waves 9-32** under condition (6): (1)-(5) held at wave 32's close (51da9771f, backed up); wave 33's
  own pair opens at 51da9771f.
- **Verification**: `impl-drift` on the touched claim, the gate, wave 33's own bookend pair.

## Wave 34 (amendment 33, 2026-10-08)

- **Scope**: the polder's reservoir seat and inlet stub tried and re-tiered E3 by measurement (the seat against the dike
  re-rolls Kuwabata into a joint zigzag the joints pass does not mend); rows 464 and 465 re-tiered E3 with their evidence
  (the pull-back is handed no hard ground, so a routed join spans fabric.py, web.py and route.py; the code names no spine);
  row 466 taken: `_one_joint` string-pulls a joint of two kinds like any other (0081) and splits the walk back into its two
  records, each keeping its width. Row 434 held for the GM.
- **Occasions**: none - no pool map changes.
- **On the unpushed waves 9-33** under condition (6): (1)-(5) held at wave 33's close (36977d8d1, in the clone - its push
  waits on the GM's call on the 329 merge commit's stray profiles); wave 34's own pair opens at 36977d8d1.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 34's own bookend pair.

## Wave 35 (amendment 34, 2026-10-08)

- **Scope**: wave 34's found rows tiered by a fresh reader (T95a): eight E0 claims written in the Mode A docs and `_one_joint`
  (`tasks.md` Phase 36), with the stale clerk line; the salt-ward Scale clause and the Z-to-T rule tiered E2, left for their
  place. No executed code changes.
- **Occasions**: none.
- **On the unpushed waves 9-34** under condition (6): (1)-(5) held at wave 34's close (900729a7d, in the clone - its push
  waits on the GM's call on the 329 merge commit's stray profiles); wave 35 changes no executed code, so it owes no pair.
- **Verification**: `impl-drift` on the touched claims, the gate.

## Wave 36 (amendment 35, 2026-10-08)

- **Scope**: wave 35's two found rows, E0 by a fresh reader (T97a): claims for the south-wall gate (0123 drawing; the sheet
  conventions' claim re-pointed there) and the divider walls between the courts (0090 drawing) (`tasks.md` Phase 37). No
  executed code changes.
- **Occasions**: none.
- **On the unpushed waves 9-35** under condition (6): (1) held but for the backup push, withheld pending the GM's call on the
  329 merge commit; (2)-(5) held at wave 35's close (0e87667c8); wave 36 changes no executed code, so it owes no pair.
- **Verification**: `impl-drift` on the touched claims, the gate.

## Wave 37 (amendment 36, 2026-10-08)

- **Scope**: rows 436 and 473 (`tasks.md` Phase 38): the Scale paragraph's salt-ward marker removed with the true-size list's
  mention (no sheet draws a ward since 2026-09-28; Hayakawa's notes line brought to its sheet); `_one_joint` makes only a fold
  a T and pulls a Z across a joint straight like any jog (0081), the joint moved back where the pull cannot clear it. Rows 434
  and 461 (the shrine cap) held for the GM.
- **Occasions**: none - no pool map changes.
- **On the unpushed waves 9-36** under condition (6): (1) held but for the backup push, withheld pending the GM's call on the
  329 merge commit; (2)-(5) held at wave 36's close (49824361c); wave 37's own pair opens at 49824361c.
- **Verification**: `impl-drift` on the touched claims, the gate, wave 37's own bookend pair.

## Wave 38 (amendment 37, 2026-10-08)

- **Scope**: wave 37's found rows tiered by a fresh reader (T101a): three claim lines in `_one_joint` (the T's stem GUESS, a
  pulled lane's clearance CONVENTION, no new kink on 0081's drawing page) (`tasks.md` Phase 39); the gate passage width
  tiered E3 and left for its place. Round 1 re-tiered the pulled lane's clearance E2 (the touch took in every fence; 0081:
  "may come right up to the buildings"): fixed in `joints.py` in round 2's form - the touch is the buildings' alone, and a
  pull keeps the usual clearance from every fence, grove, well, fixture and the crop.
- **Occasions**: none.
- **On the unpushed waves 9-37** under condition (6): (1) held but for the backup push, withheld pending the GM's call on the
  329 merge commit; (2)-(5) held at wave 37's close (989dbd862); wave 38's fence clearance is executed code, so it owes the pair.
- **Verification**: `impl-drift` on the touched claims, the gate, the timing pair, a glyph check of the village lane where
  the fix moved one (or the cap's recorded reason).

## Wave 39 (amendment 38, 2026-10-08)

- **Scope**: the grove crowns (`tasks.md` Phase 40): three E2 rows in `_draw_grove` - 0080's one crown band and no conifer
  inflation, 0046's grove giving way round the persimmon with every crown, the mixed broadleaf belt's crown band (its bamboo kept,
  claimed GUESS on 0075: one in twelve "in the village's shelter belt alike") - and
  two duplicate rows closed as already fixed in wave 9.
- **Occasions**: glyph-redrawn windbreak on inashiro (conifer-led) and kuwabata (mixed broadleaf), copse on kuwabata,
  homestead grove on kashikawa.
- **On the unpushed waves 9-38** under condition (6): as at wave 38's close; the pair is owed (executed code).
- **Verification**: the five tests red on the old code; `impl-drift` on the touched claims; the gate; the glyph checks;
  the timing pair.

## Wave 40 (amendment 39, 2026-10-08)

- **Scope**: the wet paddy's tint to 0007 drawing (only the draw or a pointed shape leaves a low plot green: four shape clauses
  and the outfall's keep-out, on no page, dropped; the class floor relabeled CONVENTION), and the belt's west arm as 0072 allows
  it (Inashiro's notes and 0072 drawing's measured arcs and areas restated; the belt's fallback wind the northwest, 0072). The
  class floor's promotion restricted to a plot on the drain (0007: only the lowest row takes the tint), the floor itself then a
  CONVENTION. The woods' crown band row is DEFERRED (legacy code only), its round-1 edit reverted (`tasks.md` Phase 41).
- **Occasions**: placement-changed wet paddy on sawada.
- **On the unpushed waves 9-39** under condition (6): as at wave 39's close; the pair is owed (executed code).
- **Verification**: the test red on the old code; `impl-drift` on the touched claims; the record checks on 0007, 0072 and
  the modal; the gate; the glyph check (round 2 after the outfall); the timing pair.

## Wave 41 (amendment 40, 2026-10-08)

- **Scope**: a channel's mouth judged inside the stream's drawn width (0054) - no confluence seated on a brook's corner, so no
  corner is ever held mitred (the hold tried in round 1 withdrawn); wave 40's two belt-figure rows re-cited (E0, T107a). Taken
  ahead of E2 rows 481-543 for its shared page with wave 40; the next wave returns to ranking order (`tasks.md` Phase 42).
- **Occasions**: none - the five hamlets regenerated 2026-10-08 with byte-identical manifests.
- **On the unpushed waves 9-40** under condition (6): as at wave 40's close; the pair is owed (executed code).
- **Verification**: the predicate's test at half the width; `impl-drift` on the touched claims; the gate; the pair.

## Wave 42 (amendment 41, 2026-10-08)

- **Scope**: in ranking order - row 481 closed as fixed in wave 34; wave 41's found row (T109a, E1, taken before E2 work per
  SC-003), a joiner's confluence inside the brook's drawn width tested from either end (0054). Row 492 was done and held for its
  turn (`audit/held-row492-nub.patch`); rows 482-492 are the next wave's (`tasks.md` Phase 43).
- **Occasions**: none - the five hamlets regenerated 2026-10-08 with byte-identical manifests.
- **On the unpushed waves 9-41** under condition (6): as at wave 41's close; the pair is owed (executed code).
- **Verification**: the confluence cases red on the old code; `impl-drift` on the touched claims; the gate; the pair.

## Wave 43 (amendment 42, 2026-10-08)

- **Scope**: rows 482-485 in ranking order - the connector hairpin folded as a T, the third gather form (wave 28's, reapplied),
  0246's reach to a steading, a near join refused where it is not walkable; wave 42's found row tiered E3 (T111a) (`tasks.md`
  Phase 44). Rows 486-492 next.
- **Occasions**: none - the five hamlets regenerated 2026-10-08 with byte-identical manifests after each change.
- **On the unpushed waves 9-42** under condition (6): as at wave 42's close (the 329 merge's history rewritten on the GM's
  approval, 2026-10-08); the pair is owed (executed code).
- **Verification**: the tests red on the old code; `impl-drift` on the touched claims; the gate; the pair.

## Wave 44 (amendment 43, 2026-10-08)

- **Scope**: row 486 in ranking order - a run within 25 ft of the network joined at a single point (`joined_link`, a cut end
  carried, a whole run's arriving vertex snapped or its link drawn as a join at the way's width, else refused), meeting spec-fidelity's wave-43 conditions; `reach_to_steading`
  measuring 0246's 60 ft to the house's center as the page's grounds note does; wave 43's found row (`geom.end_serves`)
  closed as not drifted with that measure (`tasks.md` Phase 45). Rows 487-492 next.
- **Occasions**: none - the five hamlets regenerated 2026-10-08 with byte-identical manifests.
- **On the unpushed waves 9-43** under condition (6): as at wave 43; the pair is owed (executed code).
- **Verification**: the tests red on the old code; `impl-drift` on the touched claims; the gate; the pair.

## Wave 45 (amendment 44, 2026-10-08)

- **Scope**: rows 487-490 in ranking order - 0081's returning leg (cut under 40 ft) and zigzag (pulled straight); the
  behind-the-back-wall rule removed, 0246 counting an end within 60 ft of the house or 12 ft of its built ground as reaching it
  on any side (`tasks.md` Phase 46). Rows 491-492 next; the settlement-side behind-the-wall rows in their turn.
- **Occasions**: none - the five hamlets regenerated 2026-10-08 with byte-identical manifests.
- **On the unpushed waves 9-44** under condition (6): as at wave 44; the pair is owed (executed code).
- **Verification**: the tests; `impl-drift` on the touched claims; the gate; the pair.

## Wave 46 (amendment 45, 2026-10-08)

- **Scope**: rows 491-494 in ranking order, and row 496 beside row 493 - 0081's "Every lane is pulled taut like a string"
  and "a returning leg under 40 ft is cut": the smoother cuts a hairpin arm even where its tip was the lane's only contact
  (the lane joined again at the fold within the 25 ft join reach, else committed uncut: the settle cuts an ordinary lane's
  returning leg, and a tree lane's refuses the web - no hairpin is drawn); a lane's end loses a last leg of 12 ft or less turning 90 degrees or more (the held
  `audit/held-row492-nub.patch`); the track out drawn taut (no 34/46 px wander) and judged by the bend rule like every
  lane, a kinked connector refused where it is chosen; the field spur drawn taut (no 14 ft midpoint swing). Row 496 is
  taken ahead of row 495 (the connector's clearance at a footprint's edge, a new test of the corridor) because it is the
  same sentence of 0081 in the same function family as row 493, and the spur's candidate is scored by the checker row 493
  changed; row 495 is next (`tasks.md` Phase 47). Found on the way: the track's fixed 4,000 ft reach stopped short of a
  5,600 ft canvas's far edge, so the reach now covers the canvas diagonal (XIV); and judged by the bend rule, Kashikawa's road
  was refused - a ford crossing squared on a 21 ft leg is a zigzag where the approach is oblique - so squaring takes a leg past
  0081's 40 ft where the short one adds a kink, and the refusal names what breaks each rule.
- **Occasions**: see `tasks.md` `## Occasions` (wave 46).
- **On the unpushed waves 9-45** under condition (6): as at wave 45; the pair is owed (executed code).
- **Verification**: the tests red on the old code; the five hamlets regenerated and their manifests diffed; `impl-drift` on
  the touched claims; the gate; the pair.

## Wave 47 (amendment 46, 2026-10-08) - batch 2's first wave

- **Scope**: batch 1's own findings first (FR-005: a review or pair finding on this feature's work is fixed where it is
  found) - the woodland glyph check's NEEDS-WORK on Kashikawa (the beyond-the-fields walk counts a row holding as field,
  0033's house lot, then field, then woodland) and the pair's band 2 (the track out to the canvas edge on its bearing and
  400 ft past it, `past_the_frame`, not the canvas diagonal every later pass sampled); then the open rows in ranking order:
  the two E1s T119a tiered (every grove and copse crown gives way round a yard persimmon wholly; 0072's Inashiro belt arc
  66 degrees), row 438 (the shrine's hierarchy stated per form) and row 442 (the road checkpoint tier described as 0110
  attests it, no garrison count); and the belt's page-edge exemption narrowed to the stretch the page cuts (round 1). Row 473 stays held as
  the GM's question; row 501 (the connector's clearance at a footprint's edge) opens wave 48. The merge of main's feature
  330 re-keyed the audit to `docs/building-programs.md` (main's move).
- **Occasions**: see `tasks.md` `## Occasions` (wave 47): woodland commons on kashikawa (round 4 of batch 1's NEEDS-WORK),
  copse and homestead grove (the give-way).
- **Verification**: the tests red on the old code; the five hamlets regenerated (the persimmon overlaps 28/3/24/23 -> 0);
  `impl-drift`; the record checks 0072's edit owed; `spec-fidelity`; the gate, the pair and the occasions at batch 2's close.

## Wave 48 (amendment 47, 2026-10-08) - batch 2

- **Scope**: rows 502-505 in ranking order (row 474 held as the GM's question): the corridor at the footprint's edge - every
  building corner 7 ft off a lane's middle at least (0246; the tread test held a 3 ft path's corners 5.5 ft off), so
  `LANE_CLEARANCE` carries 0246's 7 ft as it stands (was 40, the 7 carried to a center), which also closes rows 706, 736 and 738 and
  the skeleton arm's corridor (the corridor claims of `LANE_CLEARANCE`, the field path, the stepped spur and the skeleton arm, waiting on it); the skeleton arm clipped off the crop at its tread's edge (0081: a lane may touch a
  plot's boundary), the 20 ft kept for the wet ground and the ditches; an arm that would cross the brook takes the ford that
  makes its walk shortest, square (0035). Measured first: with the corridor at 7 ft no pool hamlet moved (the houses are
  seated before the lanes), and after each change the five hamlets regenerated byte-identical. Row 507 opens wave 49.
- **Occasions**: none - the five hamlets regenerated 2026-10-08 with byte-identical manifests after each change.
- **Verification**: the tests red on the old code; `impl-drift`; `spec-fidelity`; the gate and the pair at batch 2's close.

## Wave 49 (amendment 48, 2026-10-08) - batch 2

- **Scope**: rows 507-511 in ranking order. Rows 507 (`dwellings_shown`'s town branch) and 509-510's gate-complex and castle
  entries are DEFERRED on measure (`audit/scope.py`, `DEFERRED_ON_MEASURE`): no kept map draws a town, a city, a gate complex
  or a castle, so those branches never run on one - the GM's scope, "code actually executed by magistracies, country
  shrines, and scripted hamlets". Row 508 (0242: "the caption still goes down, where it covers the least"): an exception
  keeping feature 287's key for an all-hard caption was put to `spec-fidelity` (MODE 1) and ruled NOT LEGITIMATE - the
  GM's words name no key, 0242 already chose cover over legibility, and 0241 says "There is no key box" - so the key is
  removed whole (the placer, the hamlet's caption key, the hand sheet's key band, `WEIGHT_KEY`, `board_seat`'s key-mark
  pre-check) and a caption with no seat in the frame at all takes the first seat beside it moved inward until it fits. Measured:
  no kept map reached the key (no `caption_key`, no key band on any sheet); the five hamlets byte-identical. Row 511: the
  notice board's lane permission dropped - it stands 6 ft off the road's edge (`KOSATSUBA_VERGE_FT`, 0190), so it never
  needs to overlap a lane. Found on the way: the board's caption is proved against the 7 x 3 ft face its seat search tests,
  not the 16 x 6 ft board drawn (the key mark at the board's center hid it) - filed E2.
- **Occasions**: none - the five hamlets regenerated 2026-10-08, manifests byte-identical; no kept sheet reached the key.
- **Verification**: tests restated to the page (the six that pinned the key); `impl-drift`; `spec-fidelity`; the gate and
  the pair at batch 2's close.

## Wave 50 (amendment 49, 2026-10-08) - batch 2's last wave

- **Scope**: rows 512-513 and 523-532 in ranking order (514-522 DEFERRED: the town, city, castle and ministry entries no kept
  map runs, `audit/scope.py`). Row 512: the `{channels, dry_plots}` permission dropped (0006: the plots lie upslope of the
  canal behind a bank). Row 513: the sluice gate's drawn box from its recorded span (0179), never a fixed 11 x 11. Rows
  523-525: a footplank's seats per 0084's drawing page - a join of ditches rules a seat out (the 3x obliqueness ceiling and the
  deck widened over a junction retired), and where every wide seat is ruled out the crossing takes the widest seat left
  (`seat_order`). Row 526: a carried way's deck lands about 10 ft onto dry ground or is not seated (0087; the footplank's short
  abutment retired). Row 527: the threshing yard keyed off on no grain grown (`grows_grain`; 0037). Row 528: the north annex
  held at the band's floor, 18 x 10 ft, on a house under about 22 ft deep (0052). Row 529: the drained acres leave out the
  whole drain-side row (0007). Rows 530-532: the comb's outfall curves out of the collector at most 55 degrees a turn (0060),
  and its 33 ft corridor is kept on town and city maps only, in feet (0058).
- **Occasions**: none - the five hamlets regenerated 2026-10-08; only Kuwabata's two sluice records moved (each records its
  span, 20), no glyph or placement changed.
- **Verification**: tests red on the old code; `impl-drift`; `spec-fidelity`; then batch 2's close: the gate, the pair from
  2e3153b4e (re-measuring batch 1's band 2) and its perf-audit, and the batch's occasions.

## Wave 51 (amendment 50, 2026-10-08) - batch 3's first wave

- **Scope**: the next kept rows in ranking order. The comb's wet-paddy class made explicit, the drain-side row only (0007).
  The field pond drawn as a dish pond, an earthen bank ring on wet ground round its open water with reeds on the margin
  (0008: "low ground ringed with an embankment and dug out"). The winter crop's odds set by the site, barley weighing
  the drained share of the paddy, halved where a rolled town nearness is far (0009: the drainage and a town's nearness
  set the odds, how they weigh a GUESS). The wood shed seated off the house's own walls, never the front wall, with no
  extra outward pace (0043); its step HELD past the page's ken behind ranking row 101 (`refuse_unreached#every household reached`), as wave 9 held it. The pond feeder and the lotus draw are DEFERRED on measure: no kept map draws either.
- **Measured**: the five hamlets' winter crops unchanged. Inashiro and Kuwabata re-seat wood sheds. Inashiro and
  Mizuguchi draw the dish pond. The scaling rolls (10, 20 and 40 households; seeds 4, 25, 39, 47) lay every shed.
- **Occasions**: glyph-redrawn field pond on Inashiro and Mizuguchi; placement-changed wood shed on Inashiro and
  Kuwabata - at batch 3's close.
- **Verification**: tests red on the old code; `impl-drift`; `spec-fidelity`; the gate, the pair and the occasions at
  batch 3's close.

## Wave 52 (amendment 51, 2026-10-08) - batch 3

- **Scope**: the next kept rows. The belt's crossing allowance made each way's own (0072, "as written": two ways through one
  opening excuse 30 ft either side of each, the stretch between no more than twice that). The manure heap stepped beyond its
  privy along the line from the house's center (0042: "on the side away from the house"). The privy's barn seat withdrawn
  (spec-fidelity W52-3): 0047's barn is a building of its own and a hamlet farm draws no barn, so there is no barn seat and
  the barn's share goes to the yard, the front and the stable at their own weights; drawing the barn is filed as an E3
  found row (`found-wave52.jsonl`).
- **Tooling** (the GM's four-hour check, 2026-10-08): `make cohort HOUSEHOLDS=` rolls the scaling sizes untimed, the band
  lifted as the perf snapshot lifts it; measure-hooks reminds a `make perf` outside a pair's legs of it; `make perf-profile
  HOUSEHOLDS=` profiles a growth at the size it was measured.
- **Measured**: the 20- and 40-household cohorts match or better the commit before the wave (3/4 and 3/4, re-measured after the barn seat's withdrawal); seed 4's refusal at 20
  households predates it and is filed (`found-wave52.jsonl`). Privies and heaps re-seat across the five hamlets.
- **Occasions**: placement-changed privy on Sawada, manure pit on Sawada, manure heap on Inashiro - batch 3's close.
- **Verification**: tests red on the old code; `impl-drift`; `spec-fidelity`; the gate, pair and occasions at batch 3's close.

## Wave 53 (amendment 52, 2026-10-08) - batch 3

- **Scope**: the grove's crown density (rows 569, 571): one crown to ~180 sq ft real (0080's drawing page: 600 trees a
  hectare) at every grain, `GROVE_CROWN_SQFT` and `grove_crown_px2(ftpx)`, where it was 48 sq px at the town grain scaled
  by the building grain - one crown to ~71 sq ft on a hamlet at 1 ft/px. The band-piece cap (`farmsteads.py`) takes the
  same density, so a piece still holds 28 crowns' ground.
- **Measured**: drawn crowns fall 14-38% across the five hamlets (Inashiro 641 -> 528, Kashikawa 3,102 -> 2,673,
  Kuwabata 790 -> 576, Mizuguchi 546 -> 337, Sawada 961 -> 704). A windbreak's drawn conifer share moves 0.463 -> 0.508 as
  the canopy-layer cull thins less at the lower density (the throw stays 0.48 of the crowns); the test's tolerance is widened behind a found row to bring the drawn share back to 0.48 (spec-fidelity W53-3). The figures: m:wave53-grove-density.
- **Occasions**: glyph-redrawn homestead grove on Mizuguchi, windbreak on Inashiro - batch 3's close.
- **Verification**: tests red on the old code; `impl-drift`; `spec-fidelity`; the gate, pair and occasions at batch 3's close.

## Wave 54 (amendment 53, 2026-10-08) - batch 3

- **Scope**: the windbreak's drawn conifer share (found in wave 53, W53-3): 0072's 48% is of the crowns drawn, and the cull
  is asymmetric (a lesser crown over a conifer is not drawn), so a kind thrown with the crown drew 0.508. A windbreak crown's
  kind is now rolled where it is seated, nudged by the clump's drawn deficit (`0.48 + 0.48 * drawn - drawn conifers`), so the
  drawn share is 0.48; the test's tolerance back to 0.02, then tightened to 0.01 on the measurement.
- **Measured**: the unit sample draws 1,336 conifers of 2,791 crowns (0.479). The five hamlets reroll their windbreaks.
- **Found at this wave's plan review - a regression of wave 52**: three pool tests read the shipped manifests and went red
  unseen (`tests/hamletgen/test_pool_261.py`: a knot on Inashiro and on Kuwabata, a zigzag across a door joint on Sawada).
  Bisected: 013b667d5 passes, e4c99b277 (wave 52's privy and heap seats) fails. Probed in `settle_knots`' judge: every
  gather of each knot splits the web or leaves a farmhouse unreached - Inashiro's field way starts on a spur 9.4 ft from
  where it leaves a door lane, Kuwabata's lane 11 T's onto lane 9 21.8 ft from its door. A trial letting the field way's web
  end gather changed nothing. They are the ranked row `knots.py::settle_knots#a knot no lawful gather reaches` (E3), as
  Sawada's knot has been since wave 10: Inashiro and Kuwabata join `_KNOTS_WAITING` (Kuwabata since fixed, below), and Sawada's zigzag goes on a new
  strict `_ZIGZAGS_WAITING` behind a new E3 found row (`found-wave54.jsonl`) - each strict, so the day a map is fixed its
  name must come off. Kept, not reverted: the seats are 0042's and 0047's, and the knots are the web's limit they exposed.
  For the GM at the feature's end (the waiver exit of constitution XIII; fixing row 748 is the other).
- **The fix attempted (spec-fidelity W54-5, W54-7; constitution XIII's investigation)**, each probed in `settle_knots`' judge
  and `Lawful`, on Kuwabata's knot (lane 11's foot 21.8 ft from lane 9's door):
  1. the gathers the engine has (`moved_onto` both forms, `contracted`, `teed_onto`): every one re-aims lane 11's 209 ft last
     leg at the door and splits the web (lane 12 is teed onto that leg 51 ft from its start; the re-aimed leg passes 4.7 ft
     off it);
  2. a PIVOTED form (the leg kept to lane 12's foot, then turned onto the door): the web stays joined, but `Lawful`'s ground
     refuses it - the turned leg crosses house 9's dooryard;
  3. a SLIDE of the foot along lane 9 to 25.5 ft from the door (3.7 ft), plain and pivoted: ground refuses both - the foot
     already stands in that dooryard. Uncapped, the slide let the reference roll gather its way into a web the last resort
     refused (lanes 1, 4, 6, 7, 12), so a slide of more than a nudge is not safe either.
  Every trial was reverted. What is left is row 748's own fix - re-lay the household's way AT SEATING so it never arrives
  inside another's dooryard - which is the seating's change across modules (E3). Sawada's zigzag is the same ground: the
  chord that would take out lane 3's overshoot (4042.4, 2067.1) -> lane 1's door crosses house 1's front dooryard, so the
  smoothing keeps the turn. Neither stems from the fixtures themselves (none stands within 75 ft of Sawada's joint): wave
  52's seats moved the houses' ways and the web settled differently.
  Then row 748's own route, at SEATING (`gap_ways._way_for`): a household whose every exit leaves a knotted foot now searches
  `KNOTTED_TRIES` (3) times `GAP_TRIES` exits before keeping one - **Kuwabata's knot is FIXED** (a later exit gives lane 11 a
  knot-free way; only Kuwabata's manifest moves; its name off `_KNOTS_WAITING`; a unit test pins the breadth). For Sawada's
  zigzag two seating guards were tried and reverted: holding back a gathered join that would zigzag (it never fired: the
  overshoot is in the traced way itself, drawn as laid by `settle_reach`, unchanged through every settle step), and holding
  back any admitted way that zigzags at its foot (the zigzag moved to another household's way, lane 5, the same overshoot into
  lane 1's door, and Inashiro moved besides). The way into lane 1's door from the south-west must pass house 1's front
  dooryard to arrive without the overshoot, and no lawful route does: the zigzag stays on `_ZIGZAGS_WAITING`, T137 stays open
  for it alone, and the GM is asked at the feature's end (waive behind its row, or revert wave 52's seats).
- **Tooling** (so a reroll cannot hide this again): `make quick` runs the tests that read the shipped hamlet manifests
  whenever the manifests moved since its last green run (`scripts/gates/pool-readers.py`, its test in `tests/tooling/`);
  testmon selects by code, and a manifest is data. And `perf_profile.py`'s spec typed, which the quick type check
  refused (26 errors from wave 52's `HOUSEHOLDS=`).
- **Occasions**: the windbreak on Inashiro (wave 53's glyph-redrawn line) covers the share - batch 3's close.
- **Verification**: tests red on the old code (0.508 outside 0.02); `impl-drift`; `spec-fidelity`; the gate, pair and
  occasions at batch 3's close.

## Wave 55 (amendment 54, 2026-10-08) - batch 3's close, the homestead grove's glyph-check answered

- **Scope**: the grove's density AS DRAWN (glyph-check of Mizuguchi, round 1 NEEDS-WORK): wave 53 threw one crown to 0080's
  ~180 sq ft, but the culls (a crown under another's, the sun and building keep-outs, the persimmon) took more than half the
  throw, and the groves were drawn at ~400 sq ft a crown. A clump now keeps throwing until its drawn crowns hold its open
  ground (`open_share`: the box less what the keep-outs, earlier stands' crowns and persimmons cover) at `GROVE_CROWN_SQFT`,
  or `TOPUP_TRIES` (6) throws a crown wanted fail; the crowns are painted back to front after the top-up. Not the
  conifer-led belt (its rows are its own; its density a filed row). The same gap as wave 54's conifer share: thrown versus drawn.
- **Measured** (m:wave55-grove-density-as-drawn): drawn crowns rise on every hamlet (Mizuguchi 339 -> 601); Mizuguchi's
  bands hold one crown to 242 sq ft of their whole boxes, keep-out ground included. A top-up throw over the farm's bamboo
  patch is refused (impl-drift of wave 55: the culms' own ground).
- **Batch 3's close so far**: the gate green (waves 51-54); privy, manure heap and manure pit PASS; windbreak PASS (to be
  seen again with the top-up); homestead grove round 2 owed; the record checks the 0072 re-measure owed answered, their
  modal edits applied (a further depiction round owed); three found rows filed (`found-batch3.jsonl`: the privy's rolled seat
  honored, the windbreak's hover region, Kuwabata's bare runs). Two depiction findings were not taken as edits: Kuwabata's
  bare runs (filed, above), and the dispersed form's seating sentence, which keeps the research's wording while the code's
  drift stays the open row `stages.py::_seat_households#a scattered hamlet's seating` (the modal is not reworded to the drift).
  And wave 54's knotted fallback (`gap_ways._way_for`), read DRIFTED by impl-drift, was tried without and KEPT: three of
  Sawada's households lost their own way to the neighbor's-yard reach, which draws no walk; the knots it leaves are owed by
  `knots.py::settle_knots#a knot no lawful gather reaches`. The pair and perf-audit follow the reviews.
- **The seating that leaves no knot or stranded way, tried (perf-audit round 2's open criterion; T137/T140)**: perf-audit's
  own control showed the batch's every growth and seed 25's refusal come from the privy and heap re-seating alone (removed,
  each roll returns to its start and seed 25 draws). Mechanism: `PRIVY_SUNNY_SHARE` (0.727, Wang & Ochiai's figure) of privies take the sunny-side sector, the dooryard's
  front-right; the barn's withdrawal sent its share to front-wall seats; the heap steps beyond along the bearing - so the
  ground where the ways leave the dooryard fills. Tried: a "way out" strip kept clear of the searched fixtures in front of
  the yard's far edge (the yard's width, 20 ft out) - the reference roll (Inashiro, 15 households) then refused its web
  (four access lanes), worse than before; reverted. The web's outcome moves chaotically with the seats, so a local keep-out
  trades one map's refusal for another's; the remaining route is the seating's own search asking the way out of each
  household with its fixtures in place (E3, row 748) - attempted, see T140's investigation below.
- **T140's investigation (spec-fidelity B3-9: the named route attempted before any waiver)**: the seating's own search
  asking each household's way out with its fixtures in place. (1) The cause, measured at the refusal (seed 25, 40
  households): all fourteen failing access lanes foul the 7 ft fabric gap on their first leg, and the fabric each fouls
  is owner-less - a garden (m:t140-seed25-fouled-fabric), which since this feature is an obstacle to its own farm's path as to any other (0246: the way
  leaves round its own beds). (2) Attempted: `tree.admits` asked the settle's own fabric reading (`theirs`, 7 ft) of each
  household's way before admitting it. First form: it read only the manifest's yard lists, which hold 2 while the ways
  are laid (the rest stand in the house records' `geom` boxes) - no effect. Second form: the seated yards and gardens
  read from `geom` (gardens owner-less, as the law reads them) - the reference roll (Inashiro, 15 households) then refused
  its web (a needle join and lane 10). (3) Earlier: a way-out strip kept clear of the searched fixtures - the reference
  refused too (four access lanes). Each change moves which exit a household takes, and the web's outcome moves with it,
  trading one map's refusal for another's; the stricter admission leaves households only exits that fault elsewhere.
  Every trial was reverted. What would remain is a seating that places a household's garden and fixtures together with
  its way out (the bundle's layout asking the way, not the gap pass after) - a change across the seating (E3, row 748).
  T140 stays open, the batch held, and the GM is asked for the waiver or the go-ahead on that rebuild, with the band-3
  sign-off.
- **Two depiction findings declined at batch 3's close**: the mixed belt's wind side (the drift is the village roller's
  `_roll_windbreak`, deferred from this feature under amendment 8; the hamlet engine keeps 0072's bearing, its claims in
  step); and the conifer-led belt's "smaller" broadleaf crowns, kept (its lesser crowns are drawn at `LESSER_BROADLEAF_S`,
  0.75-0.85, against the rows' 1.0-1.1).
- **A one-off at batch 3's gate**: `tests/tooling/test_measured_surface.py` counted 39 hashed files outside `l7r/` and `tests/`
  where 38 stand (all pool `.gen.py`); re-counted after, 38, and the next gate green. Searched: no test writes a `.py` into the
  real `pool/`; the tracked and untracked lists hold 38. Unreproduced; if it recurs, list the files the count saw.
- **Verification**: tests red on the old code (the open clump drew under 0.9 of its density); `impl-drift`; `spec-fidelity`;
  glyph-check rounds on the homestead grove and the windbreak.

## Wave 56 (amendment 55, 2026-10-08) - batch 4's first wave

- **Scope**: the copse's and the village grove's SEATS kept off the plots' sun at the tree's 50 ft (0038: "50 ft east, west
  and south of a plot"; rows 580, 582, 583): the south strip was the farmhouse's 39 ft (`_sun_corridor_ft`) or a 22 default,
  and the morning lane ran east of the beds only, while the crowns were already held to 50 ft round every yard and bed
  (`_sun_keepouts`) - so a seat between was reserved and never planted. Now `CANOPY_SHADE_FT` south of every yard and bed and
  `EAST_REACH_FT` / `EAST_LANE_FT` east of the yard as of a bed, in `village_grove` and `WoodShares` / `copse_keepouts`
  together (feature 317: the two must move together, or a seat is reserved where the copse will not plant). The west lane
  is the hamlets' declared 50 ft already (`WEST_SUN_FT`).
- **Measured** (m:wave56-sun-strips): Inashiro 624 -> 690 crowns, Kuwabata 738 -> 673, Sawada 905 -> 907; the grove farms
  unchanged.
- **The south-east corner** (impl-drift round 2): both east lanes run down to 50 ft below the plot's south edge, as the west
  lane does (0038, "from the plot's north edge down"); Inashiro 661, Kuwabata 672, Sawada 920 crowns (m:wave56-sun-strips).
- **Side effects measured** (m:wave56-sun-strips): Inashiro's lane knot, on main's waiting list too, is gathered (off
  `_KNOTS_WAITING`); seed 25 at 40 households draws its web again (T140's refusal), to be confirmed in batch 4's pair before
  T140 is closed - the web moves with the seats.
- **Occasions**: placement-changed copse on Kuwabata - batch 4's close.
- **Verification**: a test of the 50 ft strips; `impl-drift`; `spec-fidelity`; the gate, the pair and the occasions at
  batch 4's close.

## Wave 57 (amendment 56, 2026-10-08) - batch 4

- **Scope**: the commons' look (rows 587, 588). (1) The scrub's ground: the claim said "a solid straw-gold ground", but the
  code draws the repeated block alone (`tiles.cover_path`: the pattern, no fill, no stroke) - in step with 0078 ("one small
  block of grass and brush, repeated, with no outline"); the claim restated, nothing redrawn. (2) The wood's edge: the scrub
  tile, which carries brush dots, ran 8 ft in under every wood's edge, where 0077 says grass only and no brush in a wood. The
  scrub now leaves each wood whole, and a grass-only tile (`wood_fringe_tile`: the scrub's tufts, no brush dot) fills the
  `WOOD_FRINGE_FT` band under its edge, in the scrub's slot and class - in two steps, the grass thinning inward as 0077 has it
  ("thinning out over the first few paces under the crowns"): the outer half at the tile's density, the inner half at
  `WOOD_FRINGE_THIN_KEEP` (0.5, a convention) of its tufts (impl-drift round 1: a uniform band stopped on a hard line). And
  the header's tiles and slots claimed as conventions, a scrub pine's reach and the crops' lean claimed. Round 2: no coppice
  crown is seated in a marsh (0074: woody growth stops at the marsh's edge; the crowns had thinned 46 ft into it). Rounds 3-4:
  the scrub pines' account restated to throws, the ponds' open water claimed (scrub, pines and coppice alike), and the
  crescent pond's grass margin scaled by the map's grain (`2.0 * bs`; the maps byte-identical at 1 ft/px).
- **Measured**: the five hamlets' manifests move by their cover records only.
- **Occasions**: glyph-redrawn scrub and rough grazing on Kashikawa (its woods' edges) - batch 4's close.
- **Verification**: tests (no brush dot in the fringe tile; the scrub tile stops at the wood's edge; the band drawn with the
  grass-only tile); `impl-drift`; `spec-fidelity`; the gate, the pair and the occasions at batch 4's close.

## Wave 58 (amendment 57, 2026-10-08) - batch 4

- **Scope**: (1) the notice board's entrance reach in feet (row 603): `kosatsuba_anchor` compared the 60 ft
  `KOSATSUBA_ENTRANCE_REACH_FT` with pixel distances; it now takes the map's `ftpx` (its caller passes `self.ftpx`) - the
  hamlets (1 ft/px) byte-identical, a 2 ft/px map's mouth 30 px nearer, tested. (2) Measured and noted, no code: row 595 (only
  plain houses keep a byre) excludes nothing a scripted hamlet seats, every house plain; row 584 (the storehouse) re-tiered
  E3 on measure - its no-lot clause runs only on the legacy roller, and its live clause (a scattered farm's kura drawn on the
  north wall unreserved, its bundle laid with shed=False) is a change across the bundle, the scattered layout's turn, the
  fixtures and the house record. Row 594 (the inner stable's mirror forms, run on Mizuguchi) re-tiered E3 on measure: a knob
  for the wing's end was written and reverted - 0048 joins the stable to the house's lower (doma) end and its mirror forms
  mirror the whole house plan; our houses keep the doma at -x, so the left end tried first is the lower end, in step, and the
  mirror form needs the plan mirrored (doma, stable, privy's stable seat, bath walls) as one knob. The never-arriving approach
  of `kosatsuba_anchor` claimed (impl-drift).
- **Occasions**: none - nothing a hamlet draws moves.
- **Verification**: the anchor test (red on the old signature); `impl-drift`; `spec-fidelity`.

## Wave 59 (amendment 58, 2026-10-08) - batch 4

- **Scope**: row 588 - `clear_east_of_beds` DROPS a band whose cut run would be shorter than its width (it was kept whole,
  standing in the bed's 50 ft east reach that 0038 keeps clear); the claim relabeled to cite 0038. Two defects found in the
  measuring, fixed in the wave (XIV): (1) the cut ran for the dispersed form alone (`if frame is not None`), so a linear or
  nucleated farm's own thin east band was never cleared - it now runs for every bundle with bands; (2) the cut tested
  overlap on the unrounded boxes while the rule (`grove_rules.gardens_east_shaded`) reads the records rounded to 0.1, so a
  band ending AT the bed's edge read as 0.015 px into it (cohort seed 901, pinned linear) - the cut now takes a band within
  a pixel of the bed's height and leaves it a pixel clear, as its comment already promised.
- **Measured**: the cohort (30 maps) at HEAD and after, 24 -> 25 passing (m:wave59-east-reach-cohort): Audit-901's `gardens_east_shaded` gone,
  nothing added; the pool: Kashikawa's manifest one line, the other four unchanged.
- **Occasions**: none - three of Kashikawa's bands a pixel shorter, their crowns re-scattered within the band (up to ~12 px); the band's glyph and the scatter's rule unchanged, so no element is redrawn or re-placed by a changed rule.
- **Verification**: `tests/settlement/test_grove_sides.py` (the stub dropped, the touching band cut; red on the old code);
  the cohort diff; `impl-drift`; `spec-fidelity`.

## Wave 60 (amendment 59, 2026-10-08) - batch 4

- **Row 590 HELD, re-tiered E3 on measure** (the spec's Edge Case; plan review W60-refusals). Under the SW and SE turns
  `canonical_farmstead`'s bed beside the yard is carried to the house's northeast or northwest. A `garden_west` flank (the bed
  on the yard's canonical west flank, which those turns carry south; the well pocket the other flank) was built, tested and
  REVERTED: on 48 declared-wind dispersed rolls the refusals went 3 -> 4 on other seeds, undiagnosed (m:wave60-garden-flank) -
  diagnosing and fixing them is the row's work. The sun is settled by 0038 (no canopy tree in a bed's sun, whatever stand it
  belongs to; a bed SE, SW, E or W): the windward band giving up about 21% of its ground to the moved bed's reach is 0038
  applied, and the code already culls those crowns (`_sun_keepouts`). The path runs only for a hamlet that DECLARES a SW or SE
  wind (`DEFAULT_WINDWARD` is the regional northwest). Recorded at the point of change as a fix that failed.
- **Found (impl-drift round 4)**: under a southern wind the turn puts the front, and the yard, away from the wind - off the
  house's south - where 0029 has the yard before the south wall and 0036 the front away from the wind: a conflict between
  two cited pages, filed as its own row (`found-wave60.jsonl`, `dispersed_layout#homestead turned to the map's wind`, E4,
  NEEDS-RESEARCH).
- **Claims (impl-drift)**: `canonical_farmstead#thin bands clear of the plots' sun` DRIFTED on its wording - it named the
  22 ft `YARD_SUN_STRIP` default where every scripted hamlet passes the 50 ft canopy reach and a crown (`sun_corridor`, opted in
  at `hamletgen/homesteads/stages.py`; the default runs only on a hand map that never opted in, deferred): restated to name
  both. Three UNCLAIMED decisions claimed as GUESS: the service strip and the way in through a ring (the words of ranked rows
  231 and 234, which claim the same at `_bundle_layout`), and the deep bands set `gap` + `back` off the works, their ground
  inside a plot's reach and their crowns culled there where the band is drawn (`groves.py`, `_sun_keepouts`).
  Round 4 (the revert): 10 in step, the garden row drifted as held - and the same turns put the yard north of the house
  (0036's front off the wind against 0029's south front), filed as its own E4 row; the 22 ft default claimed UNRESEARCHED.
- **Occasions**: none - no engine behavior changes (claim lines and a docstring).
- **Verification**: the five hamlets cached or byte-identical; `impl-drift`; `spec-fidelity`.

## Wave 61 (amendment 60, 2026-10-08) - batch 4

- **Scope**: row 564 - a privy off the sunny side (the 27.3% of households, 0047) now keeps its ROLLED place: `rolled_first`
  offers that place, slid along its wall (`along_its_wall`) and then stepped out, before the other attested places are
  tried; before, every place was tried at its first spot, and the stable's and the front's first spots fall on the work
  yard and the beds, so they went to the yard seat behind the house (Sawada 8 of 8 at batch 3's close). A sunny roll is
  offered as before - the sun-side sector, the attested places, every pace. `privy_places` names the three places once.
- **Measured** (m:wave61-privy-rolled-place; WITHDRAWN at wave 62 - the gain was privies slid past the gable, see wave 62):
  privies behind the house 37 -> 30 and at the stable end 4 -> 10 over the five hamlets as first counted. The cohort at 48 of 54 before and after (N=48); seeds 10 and 20 draw
  now, 06 and 09 are refused, 24-48 identical - fixture fits move the houses, and the existing refusal classes land on other
  seeds; each new one probed: 09 nine access lanes across the web break the lane law (no fixture at it), 06 a byre recorded on
  a lane after the stages (its nearest privy and wood shed 20-50 px off).
- **Tried and withdrawn** (recorded in `rolled_first`'s docstring): the sun-side sector stepped out ahead of the attested
  places (behind 37 -> 20, but cohort seeds 4 and 23 refused - the paces carried a privy and its heap past the threshing yard
  onto the household's way out), and a rolled place stepped straight out without the slide.
- **Claims (impl-drift)**: the privy places without the barn (`_seats#privy seats`, `privy_places`) say what the maps draw
  now - the barn left out while a hamlet draws none - behind the OPEN found row `_seats#privy seats - the barn 0047 names` (E3,
  wave 52's, re-keyed here: plan review W61-3 found it lost from the ranking - it shared its key with wave 9's closed row, and
  `merge.py` read the found files by name, so `found-wave9` overrode `found-wave52`, as `found-wave2b`/`3` overrode `13`/`15`'s
  magistrate's-manor rows; `merge.py` now reads them in the order they were found, `found_order`). 0047's drawing page says
  the same: "draw no barn yet ... drawing the barn the record names is open work". The slide-then-step order is recorded on the
  page and cited. FOUND AND FIXED: `FixtureForms`' default privy weights gave 35/30/20/15 to the yard, front, stable and barn
  where 0047 gives them to the stable, yard, front and barn - ranked row `FixtureForms#privy seat weights` (E1), closed at
  this wave (the hamlets roll their own from `_PRIVY_SEATS`, which was right: the five maps byte-identical after the fix).
  Ranked or filed, not fixed here: the yard privy's 9.5 ft (row 832, E3, held); the wood shed seats' 9.5 ft (found row after
  row 799, E3); the dike-pond sty drawn without the privy over it (`found-wave61`, which REPLACES ranked row `out2`'s by key at
  E2, keeping its `deviation-tempting` flag - plan review W61-5); 0044's drawing page calling the bath room's counted shares a
  GUESS (found row, E1).
- **Record (0047)**: the page edits checked - quote-check (5 notes SUPPORTS), record-format (the generated hamlets defined where
  they stand), and, on sugiura-1973-fuzoku-8, a fifth translated quotation from p.145 for the block's "three Miyagi hamlets"
  (quote-check's PARTIAL), its original corrected to the page's words on source-reader's read, a visible duplicate of a
  Japanese original removed, a gloss of the tables' privy mark "be" added; translation-check FAITHFUL. Three pre-existing
  record defects noticed, outside this feature's scope, FILED as feature 368 (`specs/368-record-0047-loose-ends/`): the 48 ft
  paragraph against its table, "earthfloored" against "earth-floored", "Type V1" undefined. The privy's and the manure's
  modal-depiction run at batch 4's close.
- **Occasions**: placement-changed, privy on kashikawa (the map where the most moved), at batch 4's close - the privies re-placed
  by the new order (the plan review's aside).
- **Verification**: `test_the_privys_rolled_seat_is_stepped_out_before_the_next_seat_is_tried` (red before),
  `test_the_rolled_place_and_its_paces_come_before_the_other_places`; the cohort pair; `impl-drift`; `spec-fidelity`.

## Wave 62 (amendment 61, 2026-10-09) - batch 5

- **Row 564 HELD, re-tiered E3 on measure** (the glyph-check of batch 4's close, NEEDS-WORK F1; plan review W62-bound and
  W62-hold-564). Wave 61's slide had no stop at the wall's end: two stable privies on Kashikawa stood 38 ft past their gable,
  and that was where its gain came from. The slide now runs only while the WHOLE seat stands along its wall (its outer edge
  within the gable), and the rolled place is no longer stepped straight out before the other places (that step put privies
  on four shipped hamlets' ways out). Measured per household (m:wave62-slide-bounded): of the 16 households whose privy rolled
  the stable or the front place, all 16 are refused it - the drawn threshing yard covers the rolled spot on 16 of 16 (with the
  house beside it on 4, a bed on 1), and no slide step fits wholly along the wall on any of them. The privies stand as at wave
  60 (37 behind the house, 4 at the stable end). The fix - the yard and the privy's seat laid out together - is the held
  row's (`overrides.json`, its files the bundle and the yard).
- **The cohort (XIII)**: against the merge base, waves 61 and 62 together leave the 48-seed cohort as wave 60 had it; the
  refused seeds are listed by name in m:wave62-slide-bounded (wave 60, wave 61, now) so the same count is shown to be the
  same seeds.
- **Record**: 0047's drawing page says the place is slid along its wall as far as the wall runs, and where the yard covers it
  the privy takes another; `rolled_first`'s docstring records the two orders withdrawn.
- **Occasions**: placement-changed, privy on kashikawa - batch 5's close (the second round of the glyph-check of batch 4's close).
- **Verification**: `test_a_slide_along_the_wall_stops_at_the_walls_end`, `test_a_rolled_stable_privy_never_stands_past_the_walls_end`,
  `test_the_rolled_place_and_its_paces_come_before_the_other_places`; the cohort; `impl-drift`; the record checks; `spec-fidelity`.

## Wave 63 (amendment 62, 2026-10-09) - batch 5

- **Scope**: the notice board's three E2 rows (0190: "a roofed frame 16 ft long and 6 ft deep, on a stone footing inside a
  fence ... about 2 ft wider all round, with a fence line at its edge"; "the board clears no ground" beyond its site). The
  board now draws its stone footing (`KOSATSUBA_FOOTING_FT`, 2 ft all round, scaled with the marker floor) with the fence line
  at its edge and the roofed frame on it; the record's drawn box (`vw`/`vh`, what the overlap matrix and the siting read) is
  the footing; the no-build ground is the footing alone, not the frame plus a flat 6 px.
- **Measured** (m:wave63-board-footing): at 1 ft/px the drawn box 16 x 6 -> 20 x 10 and the no-build ground 28 x 18 -> 20 x 10;
  the 48-seed cohort unchanged (the same six refused seeds); the three board modals already described the footing and fence,
  which the map now draws.
- **Found and fixed (impl-drift)**: the 6 ft off the road was measured to the 3 ft face tested, so with the footing drawn the
  footing stood 2.5 ft off the tread; `_route_seats` now seats and records the offset to the drawn board's footing - four
  shipped boards' footings stand 6.0 ft off the way they face (Sawada's 6 ft off the leg it faces, a bend of the same lane
  3.2 ft off, clear of the tread). 0190's drawing page now names the oversized marker at village AND city scale, as the code
  and the GM's call of 2026-07-24 draw it (it said city only - two claims DRIFTED on it, now in step); stale comments (a 12 x 5
  ft plank, a 12:5 aspect) corrected. The board modals tell the footing and fence, the village and city marker, the label above
  the crowns and a city's set of boards; the seat knob the choice modals describe (center, entrance, frontage) is not on 0190 -
  that is ranked E3 row `_knobs.py::<module>#kosatsuba_seat forms`, left to it.
- **Occasions**: glyph-redrawn, notice board on inashiro - batch 5's close.
- **Verification**: `test_a_notice_board_stands_on_a_fenced_footing_and_claims_only_that_ground`, the marker test restated for
  the footing; `impl-drift`; `spec-fidelity`.

## Wave 64 (amendment 63, 2026-10-09) - batch 5

- **Scope**: the notice board's two remaining kept E2 rows. `_board_routes#nominal widths` (0088: the highway "drawn 30 ft
  wide on every sheet"): each road was taken at 18 px whatever it was drawn at, so the 6 ft off its edge was measured from
  the wrong edge on any other width; each road now carries its recorded width. `place_kosatsuba#the caption proved against
  the board` (0190): the caption was proved against the 7 x 3 ft face the seat search tests while the board is drawn 16 x 6
  ft on its footing, so a caption drawn as proved could stand on the drawn board; all three steps (`board_caption_seat`,
  `terminal_caption`, `fallback_caption`) now prove it against `board_record`'s drawn box (`vw` x `vh`).
- **Measured** (m:wave64-board-widths-and-caption): the five hamlets reroll (each caption re-proved; the maps move a little,
  as a different subject does), the 48-seed cohort unchanged (the same six refused seeds); the canopy test replays the proof on
  the drawn board; the web-lane test now holds its board inside the web lane's 60 ft band (`KOSATSUBA_WAY_REACH_FT`), not
  within 40 px of its centerline, because the caption proved against the drawn board takes a seat 47.5 ft out where the verge
  seat's caption would foul a roof; the every-seat-fouled unit test grows 28.3 -> 36.5 s (359 terminal searches of about
  2,400 seats each, scored against a larger subject) - a degenerate case no kept map reaches, judged by the gate's `ratchet.py` at the batch close.
- **Found and fixed (impl-drift)**: the fallback for a road or a main street with no recorded width was 18 PIXELS (a width in
  feet that moved with the scale, below every width the record attests); it is now the drawer's own default - the 30 ft road
  (`lw(ROAD_W_FT)`, 0088) and the 24 ft town street (`lw(STREET_W_FT)`, 0136, a named constant in `lanes.py`) - in the
  main-way routes, the whole-network fallback and the punishment ground's routes alike; the board's search pad (an index radius that prunes the nearest-way search and never decides it, NONE), its siting default
  (`frontage`, 0190) and its bed clearance (UNRESEARCHED) newly claimed; the punishment ground's width fallbacks claimed. Left to their rows: the town tier's board placement knob (ranked E3 row 204), and the
  punishment ground's 60 ft measured center to center (`place_punishment_spot#within 60 ft of a street`, DRIFTED) -
  DEFERRED: only the legacy towns and cities run it. Two decisions impl-drift found unclaimed in that deferred unit (the ground's bed
  clearance, and its standing inside a lane's setback corridor) are left with it.
- **Verification**: `test_a_board_route_takes_each_roads_recorded_width`,
  `test_a_board_route_with_no_recorded_width_takes_the_ways_drawn_default`, the canopy and web-lane tests restated;
  `impl-drift`; `spec-fidelity`.

## Wave 65 (amendment 64, 2026-10-09) - batch 5

- **Scope**: the dry plots' two kept E2 rows (0006). `_dry_fields#crop per plot` ("each map picks its mix of the four crops
  at random"): each plot took a uniform choice of the four, so every map leaned to an even quarter each; `dry_crop_mix` now
  rolls one weight per crop once per map (in `_comb_dry_and_beans`, shared by every band and the wild middle's reserve) and
  each plot's crop is drawn on it, the 55% neighbor coherence kept. `_dry_fields#end plot split at every scale` (0006's plot
  size): the end cell the snap to the canal's length stretches past 1.35 plot widths was halved at coarse grains only, held
  back at the village grain for byte-stability; it is halved at every grain.
- **Measured** (m:wave65-crop-mix-and-end-split): at grain 1 over 40 seeds the widest plot along the canal 77.6 px with the
  old condition, at most 1.35 plot widths with the fix (the test goes red on the old condition); the five hamlets' dry-plot
  counts unchanged (81, 68, 26 on the three that draw a hem), their crop mixes now each map's own (Inashiro 30 barley and 12
  buckwheat of 81, Sawada no millet of 26); the hamlets draw at grain 2, where the end split already ran, so the split moves
  only a map at the village grain (2 ft/px); the 48-seed cohort unchanged (the same six refused seeds).
- **Found and fixed**: the first form drew the crops and the mix from the geometry's stream (`R`), which moved every later
  draw and Kashikawa's web refused (WebRefused: needle_loops) - a crop is a fill color, so the picks and the mix now draw from
  `crop_stream`, seeded from R's state without advancing it, and R keeps the draws it always took; Kashikawa draws again.
  spec-fidelity (round 1, CLEAR with two fixes): `crop_stream` seeded from eight words of R's state, which regenerate only
  every 624 outputs, handed the mix and the picks the same stream - it now seeds from the whole state, index included
  (`test_the_crop_stream_moves_with_the_geometry_stream_and_leaves_it_alone`, red on the old seeding), and `hem.py` makes ONE
  crop stream per map and continues it through every band and the reserve; the end split's comment said a hamlet's end plot
  was held back - it was the village grain's. A
  British spelling impl-drift wrote into `dev/claims-index.json` corrected. impl-drift on the wave: the hem's depth first cited
  to 0010 (the head hem 140 to 265 ft, the 70-132 px band at 2 ft/px), which round 2 found holds only at that scale - it is
  restated UNRESEARCHED at the scale the kept maps draw it (every kept hamlet at 1 ft/px: 70-132 ft; no page gives a hamlet's
  hem depth), its measuring line (8 g px off the canal's line) newly claimed, a caller's own band UNRESEARCHED, and the city-grain
  fork band's depth deferred on measure (`audit/scope.py`: laid only at `grain < 1.0`, no kept map); the neighbor-keep
  figure restated for a per-map mix (about 0.66 to 0.8, the docstring's "adjacent plots carry different crops" softened);
  `dry_acres` measured at the map's own scale, not a fixed 2 ft/px (a manifest figure no stage reads). Left to its row:
  `_dry_fields#off the water and the frame` (ranked row 213). The four crop modals already said each map's mix
  is rolled at random - now true.
- **The record**: impl-drift asked what a hamlet's plot comes to - 0006's drawing page said "the hamlet's garden-scale
  strips about 0.04", which dated from unscaled plots; the plots are tiled in real feet at every scale, so it now reads about
  0.15 (measured: medians 0.152 Inashiro, 0.17 Sawada; Kashikawa's 0.79-acre strips are its row holdings, `rows.py`). The page
  edit owed quote-check (SUPPORTS), record-format (clean), a claims triage (one claim sent on: `nearring.py`'s plot size,
  DRIFTED in a DEFERRED unit) and nine modals' depiction checks, which corrected the buckwheat color's reason, the winter
  barley choice's two overclaims, the grain-drift choice (the paddy kept untilted, 0031's deviation), the farm holding's dry
  edge (a dike too) and soy (beans among the greens drawn as the garden; 0011 linked for every map; steep ground's tracts run the contour), and linked 0009 from the
  cleared fan; each edited modal checked again. Filed, not taken: two found rows - the cleared fan middle drawn only as the
  hem (E4, a decision for the record) and the fork triangle left to scrub at village and hamlet grain against 0010 (E2, with
  0010's drawing page) - and feature 368 items 4-5 (0006's visible pointer to the holdings; what the plot outline stands for).
- **Verification**: `test_dry_plots_draw_the_maps_own_crop_mix`, `test_the_end_dry_plot_is_split_at_every_grain`,
  `test_the_crop_stream_moves_with_the_geometry_stream_and_leaves_it_alone`;
  `impl-drift`; `spec-fidelity`.

## Wave 66 (amendment 65, 2026-10-09) - batch 6

- **Scope**: `_pull_back#trim floor` (0246: "a lane end that reaches nothing is pulled back to the last house it serves"):
  the trim never cut a lane below 40% of its length, so a lane whose last house stood nearer its start than that came back
  whole, its end in the open. The floor is gone; a junction still holds a lane (`min_len`), and a lane that reaches nothing
  is still left whole. Without the floor the walk ran back to whatever stood nearest the start (in the test, the crossing
  way), so it now stops at the first point past the last thing served - walking back from the free end, the end stops at
  that house, as 0246 says - and, impl-drift's round 1, where two houses' reach zones chain, the walk is held to the FIRST
  thing it reached: `trim_lane_stubs`' predicate now names what an end reaches (a way, a house, a field), and the walk goes
  on only while the end reaches that same one (`test_pull_back_stops_at_the_last_house_where_reach_zones_chain`). The overlap exemption's reason for field graves restated to 0008 (impl-drift after the merge
  of main: an island or in a plot's corner against its bunds, on valley, terrace or strip paddy).
- **Measured** (m:wave66-pull-back): the five hamlets reroll byte-identical (no shipped lane ended inside the old floor);
  the 48-seed cohort unchanged (the same six refused seeds); the unit test - a 200 ft lane whose only house stands 40 to 70
  ft from its start - came back whole and now ends at the house.
- **Found and fixed**: the spec linter crashed (`spec_figures.appears`: float() of a dict) the first time a spec paragraph
  cited a measurement whose value is a table - every number nested in the record now counts (`recorded_numbers`), tested;
  the Decisions rows of waves 56-65 restated without bare figures (each points at its page or its `m:` record).
- **Left to their rows**: `reaches_dooryard` and `trim_lane_stubs#served at the dooryard` - to be fixed to 0246's any-side
  rule (an end within 60 ft of the house or 12 ft of its house, byre, shed, threshing yard or garden, on any side), as wave 45
  fixed the hamletgen twins (`off_the_back`, `settle_ends`: "reaches it on any side"), in a wave of their own with the lane
  review it owes; the dooryard-only rule of feature 287's water W57 stays only if a MODE 1 check rules it a legitimate
  exception (FR-004). The notice board's facing at an entrance (batch 5's found row) stays E2: its one predicate is
  `WayFacing.turn` (the gate test was retired at feature 287), fed the placement at the siting call.
- **Verification**: `test_pull_back_reaches_the_last_house_however_far_back_it_stands`,
  `test_a_figure_appears_in_a_table_valued_record`; `impl-drift`; `spec-fidelity`.

## Wave 67 (amendment 66, 2026-10-09) - batch 6

- **Scope**: the two dooryard rows (0246: "A lane end counts as reaching a farmhouse when it comes within 60 ft of the house, or
  within 12 ft of the steading's built ground - its house, byre, shed, threshing yard or garden", both figures its GUESS),
  fixed to the page's any-side rule as wave 45 fixed the scripted tier's twins (`off_the_back`, `settle_ends`).
  `reaches_dooryard` is the 12 ft test of the steading's built ground on any side (`dooryard_dist`, now reading the byre and
  shed from `geom.boxes`), where it counted the yard, the beds and a band before the front face; `trim_lane_stubs` counts an
  end within 60 ft of the house or 12 ft of its built ground, dropping feature 287 water W57's behind-the-house and
  walked-past refusals - so `behind_house`, `walked_past`, `vertex_behind` and `PAST_GRAIN_FT` go with them. No MODE 1
  exception was sought: the page is the research the claims cite, and wave 45 already took the same page's rule.
- **Measured** (m:wave67-dooryard-any-side): the five hamlets reroll byte-identical (the scripted tier settles its own lane
  ends by the same rule, so this trim moves no shipped end); the 48-seed cohort unchanged (the same six refused seeds); the
  unit tests - an end 11 ft behind a back wall has arrived and stays; 13 ft behind it, it has not; a byre counts.
- **impl-drift round 1**: `dooryard_dist` now claims 0246's built ground (it was the module's "lane geometry - NONE"), and
  `trim_lane_stubs`' claim and docstring restated for the any-side rule (they still said "not past or behind the house").
- **impl-drift round 2**: the 60 ft was measured from the house's CENTER (0246: "within 60 ft of the house") and neither
  reach was scaled (pixels, right only at 1 ft/px): the 60 ft is now measured from the drawn footprint and both reaches are
  `px(...)` (`test_trim_lane_stubs_reads_its_reaches_in_feet_at_the_maps_scale`, red on the unscaled code); its third point,
  the house prefilter, already meets every house by its whole steading's extent (`house_extent`), now said at the call.
  The bearing test's arm stops within 60 ft of the footprint (430), where it stopped within 60 ft of the center (440+).
- **impl-drift round 3**: the one-end-per-house rule's 60 ft (`fan_spread`) was also read as pixels - scaled now (`self.px`).
- **spec-fidelity (CLEAR)**: the reach comment in `_helpers.py` restated to the footprint; the scripted tier's twin still reads
  0246's 60 ft from the house's CENTER (`end_serves`), so the two tiers now read one figure two ways - filed as a found row
  (found-wave67.jsonl, E1) for the next wave.
- **Verification**: `test_a_lane_ending_behind_a_house_has_reached_it`,
  `test_an_end_serves_a_house_within_reach_of_its_built_ground_on_any_side`, the bearing test's arm; `impl-drift`;
  `spec-fidelity`.

## Wave 68 (amendment 67, 2026-10-09) - batch 6

- **Scope**: batch 5's found row `WayFacing.turn#board squared to its nearest way` (0190: a board is squared to the road it
  faces, "within 30 degrees of some stretch of that road"). An entrance board stands for the way out every departure passes,
  and at a handover the siting already prefers a seat on the approach (`c.approach`) - but every seat was turned to its
  NEAREST way, so Inashiro's board, on its connector, was turned to an access lane 2.5 ft nearer and stood 43.5 degrees off
  the track the other twelve households leave by. A seat on the approach is now turned to the approach itself (`rot`, its
  route's bearing); every other seat still faces its nearest way and is refused at an ambiguous corner (labels L12).
- **Measured** (m:wave68-board-faces-the-way-out, against HEAD): two entrance boards stood off their track out - Inashiro's
  43.5 -> 0.0 degrees (15.0 -> 14.0 ft from it) and Sawada's 76.4 -> 0.0 (14.1 -> 14.0 ft); Kashikawa's and Mizuguchi's were
  square already, Kuwabata's is at the center; those three byte-identical; the 48-seed cohort unchanged (the same six refused
  seeds); the gate's new `test_an_entrance_board_on_its_approach_is_squared_to_it` passes on the four entrance boards, and
  would have failed on two. (The first record said the four others were byte-identical: their before-images were taken
  after the gate test had already regenerated them - spec-fidelity round 1 caught Sawada.)
- **Found and fixed (spec-fidelity round 1)**: a route was flagged the approach whenever it was the connector, so where a
  map has no plain lane the connector offered to a center or frontage board would also have been squared to; the flag now
  marks the approach only for an entrance board at a handover (claimed UNRESEARCHED: 0190 names no entrance placement -
  impl-drift rounds 2-4). The gate test reads its distance in feet at the map's
  scale. The scripted twin's row (found-wave67) is E3: nine call sites in seven modules pass house centers, and `serves`'
  own keep test reads them.
- **Occasions**: placement-changed, notice board on inashiro and on sawada - batch 6's close.
- **Verification**: `tests/gate/test_board_facing.py`; the board-seat and fixture tests; `impl-drift`; `spec-fidelity`.

## Wave 69 (amendment 68, 2026-10-09) - batch 6

- **Row 215 HELD, re-tiered E3 on measure** (`comb.py::_canal_ft#canal narrows at each offtake`, the spec's Edge Case, as
  rows 590 and 564 were). 0069 narrows a supply canal by the square-root law - "the width grows only as the square root of
  the water" - and `_canal_ft` stepped it down in equal linear steps. `taper_w(tier[0], tier[1], i / n)`, the shared law,
  was built and unit-tested and REVERTED (m:wave69-canal-taper-reverted): the canal, wider through its middle, moved the
  field's geometry, four of the five hamlets moved, and the 48-seed cohort went 48 -> 45 - five seeds newly refused (04 and
  902 a farm off its street, 12 a needle loop, 40 a farmstead across the brook, 905 a farm without its channel), 22 and 33
  newly passing. Five downstream rules breaking is a change that ripples into placement - E3 by the ranking's own definition
  - and its work is those layouts. The failed fix is recorded at `_canal_ft` (constitution XIV: a fix that failed, at the
  point of change); the code and the maps are as wave 68 left them.
- **Verification**: the cohort's two runs (m:wave69-canal-taper-reverted); `spec-fidelity`.

## Wave 70 (amendment 69, 2026-10-09) - batch 7

- **Scope**: the E1 row `FixtureForms#bath room joined to the floored rooms` (found at wave 61): the code's shares for a bath
  room's place (0.8 beyond the stable wing, 0.03 joined to the floored rooms) are calibrated on 0044's counted registers, but
  0044's drawing page still said which place a bath takes "is chosen at random, and how often each is drawn is a GUESS". The
  page now states the shares drawn - beyond the stable wing about four in five, joined to the floored rooms about three in a
  hundred, by the main door the rest - linking the research page for the counts; the code is unchanged.
- **The record**: quote-check found the main-door share given no place by those registers (now said to be this project's
  choice, where the earliest registers' baths stood) and a PARTIAL on the "three houses of two villages" (the furo passage,
  the research page's own, added to the drawing page's note with its original); record-format clean; the three bath modals'
  depiction checks: the two settlement-choice modals no longer present the code's floored-rooms fallback (DRIFTED) as the rule
  and the stable-end one tells the shares house by house; the bath room's own modal tells the later share, the main door's
  share and the stable END (most map houses have no stable wing). Claims: `bath_room_seats#bath room seat fallback` and
  `bath_room_slides`' spot along a wall labeled GUESS (0044 gives the walls and the shares, no fallback or spot).
- **Left for the record**: whether the `bath_seat` settlement choice should exist - no kept map sets `meta.bath_seat`
  (the hamlets record per-house seats in `meta.bath_seats_drawn`); the measured seats (Kuwabata 4 of 5 at the floored rooms,
  no main door on any hamlet) are ranked row 154's work (`lay_fixtures#a main-door bath drawn`, E3), its text updated with
  the measured 16 / 6 / 0 of 22 so the floored rooms' excess survives the main-door fix; the bath_seat question is held for
  the GM in claims-followup.md. Spec-fidelity round 1: the two claims that still credited the main-door share to the research
  page (`bath_wall#the three walls rolled`, `FixtureForms#bath room beyond the stable wing`) now cite the drawing page's
  sentence naming it this project's choice; round 2: the hamlets' own `BATH_STABLE_SHARE` split the same way, and the comment
  above it no longer calls the floored rooms the last wall offered (rolled at 0.03). A grep finds no other claim crediting the
  main door to the research page.
- **Verification**: quote-check, record-format, modal-depiction (rounds to clean), the claims triage and `impl-drift`;
  `spec-fidelity`.

## Wave 71 (amendment 70, 2026-10-09) - batch 7

- **Scope**: `village_grove#the windbreak's hover region` (batch 3's glyph check, F3: Inashiro's page lit 'windbreak' over an
  empty arm of the belt). The page's hit region for a stand is its record's `cover` where it has one, else its `poly`
  (`interactive/page.py` `hit_regions`), and the belt's `poly` is its whole stocked box. The belt now records `cover`, the
  union of its drawn crowns (`stocking.crown_cover`: each windbreak clump's seat out to `crown_reach` plus 0.3 of a clump for a
  crown's spread, and a conifer-led belt's rank crowns at their drawn radius; the alder clumps, a class of their own, left
  out) - a CONVENTION: what the page lights is what the map draws.
- **Measured** (m:wave71-belt-cover): the box's ground with no crown, which the page lit, was 69% of Kuwabata's belt box,
  17% of Inashiro's and 0% of Sawada's; the cover is the crowns alone. The maps move only in the record (Inashiro,
  Kuwabata and Sawada carry the field; nothing drawn changes); the 48-seed cohort unchanged (the same six refused seeds).
- **Held on measure**: `village_grove#water-mouth grove drawn in the conifer-backed windbreak mix` (E2) - `village_grove`
  runs on every kept hamlet, but no kept map lays a grove of role water_mouth (no hamlet spec names one, no pool manifest
  records one), so its mix is read by no kept map: DEFERRED_ON_MEASURE in `audit/scope.py`, as the fork band's depth was.
  The re-derivation also moved `_pull_back`, `junction_floor` and `placer._strict_seat` to deferred: no kept map's roll
  reaches them (the scripted tier settles its own lane ends), which is why waves 66 and 67 moved no shipped map.
- **Verification**: `test_a_belts_cover_is_the_ground_its_crowns_draw`; `impl-drift`; `spec-fidelity`.

## Wave 72 (amendment 71, 2026-10-09) - batch 7

- **Closed on measure**: `BeltReading.holes#Kuwabata's bare runs` (0072: the planting continuous along the side it holds, a
  bare run past 30 ft a hole) asked to re-measure Kuwabata's three bare runs of 40-50 ft and fill them where they stand. The
  hole law over the five shipped manifests finds none on any belt (m:wave72-belt-holes: Inashiro, Kuwabata and Sawada 0;
  Kashikawa and Mizuguchi draw no village belt) - the waves since feature 287 closed them. 0072's drawing page's comment,
  which still recorded the runs, now records the re-measure (a comment: no record check is owed). The mixed-broadleaf
  belt's modal ("drawn unbroken") holds.
- **Closed as a stale label**: `_comb_brook#a brook from the outfall` (0060: "A drain is a dug channel that reaches a
  watercourse, never a brook of its own"). The settlement layer already draws the outfall's run as the drain's dug ditch -
  the collector's tail width, its hue and class, recorded in `channels`, to the map's edge (`settlement/fields/comb.py`,
  feature 230) - and only its start and first heading are read from `_comb_brook` (`outfall_run` draws the rest, curving
  onto the fall); its docstring and claims, which still called it a brook and gave it a course that is not drawn, are restated. No map moves.
- **Verification**: the hole law's measurement; `impl-drift`; `spec-fidelity`.

## Wave 73 (amendment 72, 2026-10-09) - batch 7

- **Scope**: the polder's three E2 rows (two closed; `channel widths` done but for its drain, re-tiered E3). `_polder_channels#channel widths` (0068: every channel's width stored in feet and drawn
  at the map's scale, placed on the ladder by what it waters): the ring's widths were fixed pixels (feeder 5.0 -> 4.0, toes
  3.4 -> 3.0, laterals 3.2 -> 2.4, drain 5.0 flat); each is now `chan_px` of its rung - the feeder the supply canal's 4.5 ->
  1.5 ft, the toes and the interior laterals the delivery ditch's 2.5 -> 1.2 ft, the drain widening 1.2 -> 5.5 ft.
  `BERM#bank beside a polder ditch` and `_plots_clear_of_channels#parcel stops at its ditch's bank`: the crop kept 5.5 px
  past every ditch alike; it now keeps each channel's own bank in feet (`channel_berm`) - beside an interior lateral its 8
  ft corridor (0022) less the ditch there, split per side - the band 4 ft each side all along - beside the feeder a supply
  canal's 5 ft bank, beside a toe a delivery ditch's 1.5 ft bund, beside the drain half a bund (0055).
- **Measured** (m:wave73-polder-widths, taken again as m:wave73-polder-widths-r2 after spec-fidelity round 1): Kuwabata's ditches at the ladder's widths (the 1.2 ft tails held at the hamlet's
  1.5 ft floor), its 35 parcels kept; the other four hamlets byte-identical (no polder); the 48-seed cohort unchanged.
- **impl-drift round 1** (found and fixed): the tapers ran the wrong way - the feeder is recorded far end first, so its
  4.5 ft head now stands at the inlet; the west toe runs drain -> feeder, its head now at the feeder; each lateral's head is
  capped at 0.8 of the feeder's width where it leaves it (0068), Kuwabata's at 2.5, 2.5, 2.4 and 1.9 ft. The bank is each
  channel's per 0055 - the feeder's 5 ft (a supply canal), a toe's 1.5 ft delivery bund, half a bund beside the drain - and is
  read at the ditch's half-width at each segment (`_nearest_band`), not its widest. Left open, re-tiered E3 on measure through
  `audit/overrides.json`: the row `channel widths`' remainder - the drain widening to an outfall that taps it mid-run (two
  runs, which the outfall brook, `_polder_close`, the comb draw and the footbridge sides each read as one channel), drawn
  meanwhile at its outfall width - with the unscaled inlet stub, outfall leg and notch (claimed UNRESEARCHED).
- **spec-fidelity round 1** (fixed): the east toe's head, which leaves the feeder at its narrow far end, is capped at 0.8 of
  the feeder there as the laterals' are (1.5 ft, the floor); a lateral's bank is the corridor less the ditch WHERE IT IS, so its
  band is 4 ft each side all along (`test_a_laterals_band_is_its_corridor_all_along`); a stale closed-tier entry for
  `channel widths` removed (the row is open at E3).
- **Occasions**: glyph-redrawn, pond canal and drainage ditch on kuwabata (the classes the dike-pond polder inks its channels as) - batch 7's close.
- **Verification**: the waterfields and hamletgen suites; `impl-drift`; `spec-fidelity`.

## Wave 74 (amendment 73, 2026-10-09) - batch 8

- **Row `_outside_command#set-back from the canal` HELD, re-tiered E2 -> E3 on measure** (as wave 69's canal taper was).
  0068 stands the paddies "5 ft back from a supply canal's water" - the stroke's local half-width plus a 5.0 ft berm - and
  0055's drawing page has "a bare earth bank 5 ft wide runs between a supply canal and the fields beside it"; the code bounded
  the planted ground a flat 4 grain (8 ft) down the fall from canal A's centerline, and canal B kept only a bund's margin. The
  change was built for EVERY supply canal (the head race and canals A and B, the `main` pieces: canal A alone would be "X
  except where Y" against 0055's every supply canal), unit-tested and REVERTED (m:wave74-supply-berm-reverted): the bank came
  out exactly (canal A median 5.04 ft, canal B 5.02, from 3.9 and 1.52), but the narrower planted ground re-fitted the fan
  (Mizuguchi -8.5%, Sawada +8.6% of their paddy) and the 48-seed cohort went 48 -> 46 - 04 and 901 the web refused, 19 farms
  without their channel, 42 a farm off its street, 22 and 906 newly passing; canal A's berm alone went to 42. Placement
  downstream of a re-fitted fan is E3 by the ranking's definition, its work those layouts. impl-drift on the change's ten
  claims: 9 IN-STEP, the one DRIFTED `_water`'s bund margin, a ranked row of its own. The failed fix is recorded at
  `_outside_command`; the patch is kept in the spec's `audit/reverted/`; the code and the maps are as wave 73 left them.
- **Batch 7 closed** (waves 70-73): gate green; the timing pair band 1 on a quiet host, confirmed consistent by `perf-audit`
  (m:batch7-pair; an earlier pair under another session's gate read band 2 on one seed with identical placer calls); the
  glyph checks PASS (pond canal and drainage ditch on Kuwabata, barley on Kashikawa), their nitpicks cut by
  `escalation-check` (its ledger row, 0 keep and 4 cut). `make verify` now refuses a second gate in a tree (`scripts/gates/one-gate.sh`), after a second one
  started beside the first and, stopped, took the first one's invocation token with it.
- **Verification**: the cohort's two runs and the bank measured on four hamlets (m:wave74-supply-berm-reverted);
  `impl-drift`; `spec-fidelity`.

## Wave 75 (amendment 74, 2026-10-09) - batch 8

- **Scope**: the E2 row `_parts_fit#whole farmstead off the fields`. 0124's drawing page tests "the whole farmstead
  (house, yard, garden and storehouse plot)" against the fields; the fit held only the threshing yard and the fixtures
  exactly off every paddy polygon, the house at its four corners (`_wall_on_the_bund`) and the beds and the storehouse only
  at the envelope's nine points. Every part of the farmstead - the house, the yard, the storehouse (`shed`), the byre, the
  well and each garden bed - is now held off exactly (`fit_index.farmstead_boxes`); the house's corner test stays, as the
  further set-back it carries (0029). The row's second clause: the beds-off-every-ditch rule, which 0124
  does not speak to, is a claim of its own labeled UNRESEARCHED.
- **Measured** (m:wave75-farmstead-off-paddy): the unit test red with the rule held to the yard alone, and red again with
  the house or the storehouse taken out, green with every part; the five hamlets byte-identical to HEAD; the 48-seed cohort
  unchanged (48/54, the same six refused).
- **spec-fidelity round 1** (BLOCKED, fixed): the house was left to its corner test, which admits a paddy's corner 4 ft
  inside a wall between its corners (the reviewer's probe, at the north wall's middle and 12 and 17 ft off it); its drawn box
  is now in `farmstead_boxes`, and the test asserts those three cases refused.
- **impl-drift round 1** (fixed): the beds-off-ditch clause split out (NEEDS-RESEARCH), `farmstead_boxes`' account naming
  the parts it returns (MISLABELED); round 2 all three IN-STEP; round 3 (the house added) IN-STEP, no claim owed.
- **Verification**: the settlement suite; `impl-drift`; `spec-fidelity`.

## Wave 76 (amendment 75, 2026-10-09) - batch 8

- **Scope**: the E2 row `furrows.py::settle_tract_seams#every seam reads`. 0006 runs a tract's rows along the contour or
  down to the outfall, leaned up to about 17 degrees (`TRACT_LEAN_RAD`); the settle that turns a tract whose seam would not
  read searched turns to +/-1.575 rad with no cap, so a settled tract could end some 45 degrees off both ways. It now takes
  the contour heading (`theta0`, the one `_dry_fields` lays from, passed by `_comb_dry_and_beans`) and admits a turn only
  where the tract's heading (`tract_heading`, its plots' mean as furrows) stays within `TRACT_LEAN_RAD` of a way
  (`way_lean`); a tract no lawful turn clears joins a neighbor, as a hemmed-in one already did.
- **Measured** (m:wave76-tract-lean-cap): the unit fixture's tract leans past the cap uncapped and within it capped, with
  every tract of the fixture within the lean; the five hamlets byte-identical to HEAD (no shipped tract leaned past it); the
  48-seed cohort unchanged.
- **impl-drift**: 13 claims IN-STEP (the hem's owed only for the call's changed line). One disagreement noted, not acted on:
  `_comb_dry_and_beans#fork band skipped on villages`, an open E2 row ranked from an earlier DRIFTED verdict, was judged
  IN-STEP on the same text (0010 plants the fork triangle only on a city map). Two readings of one claim differ, so the row
  stays open for its own wave to settle against 0010.
- **Verification**: the waterfields suite; `impl-drift`; `spec-fidelity`.

## Wave 77 (amendment 76, 2026-10-09) - batch 8

- **Scope**: the E2 row `settle.py::settle_cells#unlawful scraps left bare` (ranking fix: "after the rounds, absorb every
  still-failing scrap into the basin it shares the most bund with; leave bare only the needle strip 0005 names"). Measured
  first (m:wave77-bare-scraps): of the four pool hamlets with a comb fan only Sawada left scraps - two, 340 sq ft. The merge
  refused both, and running it to convergence (100 passes against `ROUNDS` 6) left the same two.
- **The fix** (after spec-fidelity round 1 BLOCKED the first plan, which recorded the second scrap as an unplaceable
  fallback): the reviewer's probe found each scrap had a neighbor whose union keeps every rule, refused only by the merge's
  plumbing - the union came out two polygons across a hairline bund the snapping left unfused, or held a 0.5 px² hole no
  cell fills. `opened_union` now WELDS such a union first (`welded`: closed by `GRID`, holes under `PINHOLE` filled); a union
  already one clean polygon is untouched. Measured after: no scrap left bare on any of the four (Sawada +345 sq ft planted,
  Kashikawa +1 where a pinhole filled; Inashiro and Mizuguchi byte-identical). The first plan's page sentence and narrowed
  claim are reverted; the claim keeps 0005's needle strip as the one bare ground.
- **The same fault in the grave-cut re-hold**: impl-drift round 5 asked whether `seams/close.py::_weld_within_rules` (the weld
  `hold_ring_rules` uses after a later cut) shared it. It did - a union holding any hole, a pinhole too, refused its host - so
  it welds the same way (`settle.welded`, now imported there); a test of a host whose union holds a 0.5 px² hole is red
  without it. `SIZE_ONLY`'s claim relabeled (MISLABELED: it admits the toe discipline and a staircase as well as size, a union
  still growing). The two `hold_ring_rules` CANNOT-TELLs that asked the question carry HEAD's records again (their unit's code
  and page unchanged).
- **impl-drift**: the first plan's page edit sent 0005's 57 claims through four rounds (counts as the impl-drift replies gave them, 2026-10-09). Fixed where found and kept:
  `MIN_ROW`, `ROW_CELL_SHARE` and `_rows_kept` labeled UNRESEARCHED (NEEDS-RESEARCH: 0005 gives no such width or share);
  `verdict#toe discipline`'s pointer adds 0014 (MISLABELED); three decisions found UNCLAIMED now claimed (`water_field`'s
  canals set in from the edges and its column bund's wander and straight row bunds; `hold_ring_rules` judging welds at the
  gate's lines). New DRIFTED verdicts became found rows (audit/found-wave77.jsonl): `hold_ring_rules#judged at the gate's
  lines` (E2, kept), `verdict#toe discipline` (E1, kept, with `_TOE_MIN_THICKNESS`), and `water_field`'s wander and straight
  rows (DEFERRED: no kept map executes `water_field`). With the page reverted, the 42 claims whose code did not change (the restore's count, 2026-10-09) carry
  HEAD's records again (judged on the page as it now stands); the rest are judged on the fix in round 5.
- **Record checks**: the first plan's page edit was checked (quote-check, record-format, and the ten modal-depiction units `make record-owed` named, 2026-10-09) and is
  now reverted; one pre-existing error those checks found stays fixed (`choice/plot_size--medium`: the hamlet basin "about 39
  ft square" against 0005's 48 by 31 ft, 1,500 sq ft), and one pre-existing conflict is left to its open row
  (`choice/plot_size--small_irregular`'s "no least width" against `_TOE_MIN_THICKNESS`).
- **Verification**: the waterfields suite (`welded` tested on a hairline, a pinhole, a real hole and a real gap); the cohort;
  `impl-drift`; `spec-fidelity`.

## Wave 78 (amendment 77, 2026-10-09) - batch 9

- **Scope**: the found row `seams/close.py::hold_ring_rules#judged at the gate's lines` (wave 77, E2). The re-hold a later cut
  calls (the grave island's, `settlement/fields/features.py`) kept split pieces and welds when `ring_violations` passed - the
  gate's 15 deg and 0.20-cell lines, a checker's margin - so a kept basin could carry a 15-25 deg point or 0.20-0.25 of a cell,
  against 0005's "no point sharper than 25 degrees" and "none under a quarter of the basin its field was cut to". A new
  `held_faults` adds the placer's lines under the gate's (`pointed_ring` at `_TOE_MIN_APEX`, `_TOE_MIN_AREA` of the cell,
  `is_chevron` at 40 deg / 0.90), and the re-hold uses it to pick the rings it re-holds, the pieces it keeps and the hosts it
  welds into. `_split_steps`' choice of cut, shared with the settle, is unchanged.
- **Measured** (m:wave78-rehold-placer-lines): the unit test - a 20-degree wedge and a 0.22-cell basin pass the gate's lines and
  fail `held_faults`, and the re-hold keeps no 20-degree point; the five hamlets byte-identical to HEAD; the 48-seed cohort
  unchanged. impl-drift: the six claims of the re-hold IN-STEP, no claim owed.
- **Verification**: the waterfields and settlement suites; the cohort; `impl-drift`; `spec-fidelity`.

## Wave 79 (amendment 78, 2026-10-09) - batch 9

- **Scope**: the E2 row `banks.py::hem_to_bank#drain with the fall left alone` (MISLABELED: a vertex inside a collector
  running within about 12 degrees of the fall - lean under 0.2 - was left in its water under an UNRESEARCHED label, against
  0055's bank, "never into its water"). Lifting up the fall buys nothing against such a drain, so the vertex now steps
  off at RIGHT ANGLES to the drain's nearest segment, onto the bank of the side it already lies on (`off_with_the_fall`), where
  it lies inside the bank on either side - `|gap| < need`, since the up-fall side `gap` is signed toward does not exist for a
  drain running with the fall (a clear vertex read as across the line was the first draft's bug, caught by the test). The
  scalar walk (`hem_to_bank`) and the array walk (`hem_rings_to_bank`) both; the claim cites 0055.
- **Measured** (m:wave79-off-with-the-fall): the unit test; the five hamlets byte-identical to HEAD; the 48-seed cohort
  unchanged. impl-drift: five claims IN-STEP; the docstring's "along the FALL" prose it noted stale now names the exception.
- **Verification**: the waterfields suite; the cohort; `impl-drift`; `spec-fidelity`.

## Wave 80 (amendment 79, 2026-10-09) - batch 9

- **Scope**: the E2 row `banks.py::round_channel_joints#swept bends` (DRIFTED: 0054 gives a bend RADIUS of about 2.5 channel
  widths capped at 35% of the run; the code set the tangent CUT-BACK to 2.5 widths on a quadratic, whose tightest radius is ~0.7
  of the cut-back at a right angle and varies with the turn). `swept_bend` now draws a circular arc of radius 2.5 widths tangent
  to both runs: its cut-back is radius x tan(turn / 2) - the radius at a right angle, far less at a gentle turn - and the
  RADIUS is capped at 35% of the shorter straight run (0054: "A bend's radius is capped at 35% of the straight run on either
  side"). impl-drift round 1 caught the first draft capping the cut-back instead (a shallow turn on a short run kept the full
  radius). A hairpin's cut-back is also kept within 90% of its run by tightening the radius further (geometry: a tangent
  point past the run's far end has nothing to stand on; its 90% margin claimed UNRESEARCHED, impl-drift round 2). impl-drift
  round 3: all three claims IN-STEP, no claim owed.
- **Measured** (m:wave80-swept-bends): the unit test; Kuwabata's polder ditches moved at their seam bends and nothing else on it;
  the other four hamlets byte-identical; the 48-seed cohort unchanged.
- **Occasions**: glyph-redrawn, pond canal and drainage ditch on kuwabata (the ditches' bends) - batch 9's close.
- **Decisions Recorded** (spec-fidelity round 1, FR-008): this wave's row in spec.md, and the rows waves 66-79 owed (none since
  wave 65 had been added; 69 and 74 were reverted and change nothing).
- **Verification**: the waterfields and settlement suites; the cohort; `impl-drift`; `spec-fidelity`.

## Wave 81 (amendment 80, 2026-10-09) - batch 9

- **Rows `Sectors.bound#past a thread's end` and `Sectors.thread_lines#sector pieces` HELD, re-tiered E2 -> E3 on measure**
  (as waves 69 and 74). Both MISLABELED: past its end a thread's column bund runs straight down the fall, where 0005's bunds
  "converge with" the fan toward its drain. Each thread was run on along its own last heading (`run_on`, falling back to the
  fall for a contour heading or a one-point thread), unit-tested and REVERTED (m:wave81-run-on-reverted): the reshaped cells
  re-seated Kashikawa's homesteads, and the 48-seed cohort, 48/54 both ways, traded seed 03 for seed 42 (the web refused); a
  first run also crashed five seeds on a one-point thread, guarded before the second. One seed newly refused is a regression
  (XIII); a change that ripples into placement is E3, its work that layout. The failed fix is recorded at `Sectors.bound`; the
  patch is kept in the spec's `audit/reverted/`; the code and the maps are as wave 80 left them.
- **Verification**: the cohort's runs (m:wave81-run-on-reverted); `spec-fidelity`.

## Wave 82 (amendment 81, 2026-10-09) - batch 9

- **Scope**: a defect wave 78 introduced, caught by batch 9's gate (`test_a_corner_grave_has_its_basin_bund_carried_round_it_to_the_corner`:
  1 plot where 2). Held at the placer's lines, the grave cut's re-hold dropped a whole 2,179 px² basin bare: the corner bite
  left a point between the gate's 15 deg and the placer's 25 deg (`held_faults` ['needle'], `ring_violations` none), and no
  split or weld clears a point. 0005 gives the step the re-hold lacked - "a point the maps refuse is cut off into a headland
  ... or taken into the basin beside it" - so a failing piece now first has every point under 25 deg cut off square to its
  bisector where the basin is `HEADLAND_PX` across (`blunt_points`: two new corners of 90 deg plus half the point, none
  sharper), and is kept if it then holds every line (`held_faults` decides; a sliver it refuses goes to the weld or bare).
- **Recorded on 0005's drawing page** (impl-drift: the page attests the headland only along the drain and gives cutting off and
  taking in as alternatives): "Where something cut into a basin after its fan was laid out, such as the corner of a grave
  island, leaves a point the maps refuse, the maps cut the point off into a headland before they try the basin beside it. That
  order is this project's choice, a DEVIATION". Its record checks answered (quote-check; record-format, which reworded it; the
  ten modal-depiction units 0005's Drawing: names, one of which - `choice/plot_size--small_irregular` - now says a sharp point
  "is cut off into a headland or taken in").
- **spec-fidelity round 1** (BLOCKED, fixed): the first draft spared a needle under 15 deg from the cut ("cutting it would leave
  a sliver") - measured by the reviewer, a blunted 7-degree spike is a lawful 533 px² basin; the floor is gone, W18's spike
  test now expects the point cut off and the basin kept, and the page's needle clause is removed. The Decisions Recorded row
  reclassed (the cut off the drain and its order this project's GUESS, recorded as a DEVIATION); the PLOT_SIZES found row
  tiered E4 (a NEEDS-RESEARCH verdict, the spec's Edge Cases).
- **impl-drift**: after the claims' records were reset to HEAD's where their code was unchanged (an uncommitted intermediate
  wording had forced every claim resting on the page on), the change's 18 claims - 16 IN-STEP; `_WELD_MIN_APEX` DRIFTED as at
  HEAD (its own ranked row); `PLOT_SIZES` NEEDS-RESEARCH on unchanged text, IN-STEP at HEAD - the E4 found row. Relabeled
  where found: `polder.py::unpoint_parcels#pointed parcel left as bank` UNRESEARCHED; `hold_ring_rules`' docstring brought to
  its one caller.
- **Measured** (m:wave82-point-cut-off): the gate's test passes again; the new test (a 20-degree wedge blunted and kept); the
  pool byte-identical; the 48-seed cohort unchanged.
- **Verification**: the waterfields and settlement suites; the cohort; `impl-drift`; `spec-fidelity`; the gate re-run.

## Wave 83 (amendment 82, 2026-10-09) - batch 10

- **Row `curves.py::fillet_polyline#interior bends` HELD, re-tiered E2 -> E3 on measure** (filed at batch 9's close from the
  drainage-ditch glyph check). 0054 gives a bend a radius of about 2.5 channel widths; `fillet_polyline` takes the value its
  callers pass (2.5 widths for a field ditch, `BROOK_BEND_WIDTHS` for a brook) as the cut-back on a quadratic, so a gentle
  turn's bend is drawn 13 to 25 widths wide. Each corner drawn as a circular arc of that radius, the radius capped at 35% of the
  shorter leg (the arc wave 80 drew at the seams, lifted into one body), was built, unit-tested and REVERTED
  (m:wave83-fillet-radius-reverted): every pool map moved, and the 48-seed cohort went 48 -> 45 (seeds 23, 40, 902 and 904
  newly refused - the web, a farm off its street; 33 newly passing). The bends feed every seat's clearance of the water, so the
  change ripples into placement: E3, as waves 69, 74 and 81. The failed fix is recorded at `fillet_polyline`; the patch kept in
  the spec's `audit/reverted/`; the code and the maps as wave 82 left them.
- **Verification**: the cohort (m:wave83-fillet-radius-reverted); `spec-fidelity`.

## Wave 84 (amendment 83, 2026-10-09) - batch 10

- **Row `hem.py::_comb_dry_and_beans#fork band skipped on villages` HELD, re-tiered E2 -> E3 on measure.** 0010 plants the fork
  triangle between the two supply canals with dry crops; the band that does so is laid only at a city's grain, so a village or
  hamlet leaves the triangle to the scrub. The grain gate dropped (the band at every grain) was built and REVERTED
  (m:wave84-fork-band-reverted): four of the five hamlets moved, and the 48-seed cohort went 48 -> 44 (seeds 12, 28, 31, 32, 40
  and 43 newly failing - the web, a dry exit, farm channels, a grove crossed, a house unseated; 10 and 906 newly passing). The
  band takes ground below the fork that the seats, lanes and farm channels use: E3, as waves 69, 74, 81 and 83. The failed fix
  is recorded at the grain gate; the patch kept in the spec's `audit/reverted/`; the code and the maps as wave 83 left them.
  `fork band depth` stays in `DEFERRED_ON_MEASURE` (no hamlet draws the band).
- **Verification**: the cohort (m:wave84-fork-band-reverted); `spec-fidelity`.

## Wave 85 (amendment 84, 2026-10-09) - batch 10

- **Row `comb.py::_comb_march#least spacing between ditch threads (GAP 26 px), child offset 0.55 GAP` HELD, re-tiered E2 -> E3
  on measure.** 0005 draws a hamlet basin some 40 to 60 ft across its ditch, and the march lets two ditch threads pinch to
  26 px. The floor derived from the basin was built twice and REVERTED both times (m:wave85-thread-floor-reverted): at the
  basin's width across (`plot_across`, 48 px) the cohort went 48 -> 45 (11, 21, 32, 40, 42 and 48 newly failing), and at the
  research's least width (40/48 of it) 48 -> 44, with Kashikawa refused by its lane web. The threads' spacing moves the field
  edges the lane web and the seats are laid against: E3, as waves 69, 74, 81, 83 and 84. The failed fix is recorded at `GAP`
  in `frame.py`; the patch kept in the spec's `audit/reverted/`; the code and the maps as wave 84 left them. The 0.55 child
  offset's CONVENTION claim waits for the row, so that the unit's claims are re-checked once.
- **Verification**: the two cohorts (m:wave85-thread-floor-reverted); `spec-fidelity`.

## Wave 86 (amendment 85, 2026-10-09) - batch 10

- **Row `pondstock.py::stage_pond_stock#privy over the sty` HELD, re-tiered E2 -> E3 on measure.** The record attests the pig
  toilet: an outhouse mounted over a pigsty, once common in rural China (0048, `pig-toilet-enwiki`), latrines customarily built
  above a pigsty in Han grave models (0047, `artic-pigsty-latrine`); the claim cites 0047's drawing page for "the sty drawn
  alone", which the page never says. An exception first proposed (the sty left alone as a DEVIATION) was ruled NOT LEGITIMATE
  by `spec-fidelity` (2026-10-09): it left out 0048 and read the 1639 pen, which held sheep, as a sty; it required the
  household's privy over its sty, the pair's place weighed and recorded as a GUESS, and the claim re-cited. A glyph-only form
  (the privy's mark on the sty's shed, the farmsteads keeping their own privies, recorded on 0025's drawing page) was built,
  checked and the cohort held at 48/54, but its plan was BLOCKED: keeping the farmstead privy leaves the household's privy
  where it was, and the reason given (a bank sty drawn as no one's) contradicts 0025's "it reads as a household's". Reverted.
  The whole fix needs a sty-to-household mapping (none exists) and a privy that leaves its farmstead under every rule that
  reads one - the finished-map gate `undrawn_rolls`, 0047's 48 ft reach, its four places and the sunny side; Kuwabata's two
  sties stand 186 and 195 ft from their nearest farmhouses (m:wave86-privy-over-the-sty-held). E3. The patch kept in the
  spec's `audit/reverted/`; the code, record and maps as wave 85 left them; the claim stays as found.
- **Verification**: the measurement (m:wave86-privy-over-the-sty-held); `spec-fidelity`.

## Wave 87 (amendment 86, 2026-10-09) - batch 11

- **A pre-existing defect fixed (constitution XIV), found by the null-perturbation measurement** (m:null-perturbation-cohort:
  every basin 1% wider flipped one seed, 43, refused for a lane on a well, as tripwire seed 906 is at HEAD). Probed on seed
  906: on a form that records no track out, `stage_track` chooses one from a gateway that stood on a household's well pocket,
  held in the registry since the seating (`hold_laid_parts`) but on no manifest list until drawn, so the fabric the track is
  threaded by (`_homestead_polys`) did not see it and the matrix refused the lane. The held parts - each well pocket as its
  drawn wellhead, each fixture seat as its box - now count in that fabric, as 0246's drawing page has wells and fixtures be
  fabric a lane keeps off. Seed 906 rolls clean; the cohort 48 -> 49/54, none newly failing; no pool map moved
  (m:wave87-held-parts-fabric).
- **Verification**: `tests/hamletgen/ways/test_fabric.py` (red before the fix, a KeyError on `wells`); the cohort; `impl-drift`
  on the claims owed; `spec-fidelity`.

## Wave 88 (amendment 87, 2026-10-09) - batch 11

- **A pre-existing defect fixed (constitution XIV): a road laid over a ford crossed the brook off it.** The baseline refusals
  are all the lane web (03, 10, 20, 22, 33); 03 and 22 end on `off_ford`. Probed on seed 22: the row road was laid over the
  ford at (878.7, 676.6) by `ford_crossing`, then `_thread_the_fabric` routed the run from its first point to its last and
  dropped both landings, so a road running beside its brook crossed it 64 px from the nearest ford, and nothing the last
  resort may drop could mend it (m:wave88-road-over-its-ford). `thread_over_the_ford` threads each leg to its landing apart
  and keeps the deck between them, as 0035 has a way cross the brook at a ford; it is taken only where the landing pair's
  middle is a recorded ford, else the run is threaded whole as before. `stage_track` takes it for the row road and the field
  spur. Seeds 03 and 22 roll clean; the cohort 49 -> 51/54, none newly failing. Kashikawa's row road runs on taut from its
  ford, one bend fewer; Sawada's lanes moved in draw order only, its field spur now recorded as folded back short of the field over marsh where it was recorded as isolated.
- **Occasion**: the row road on Kashikawa (a `village lane`) re-placed - a glyph-check at batch 11's close.
- **Verification**: `tests/hamletgen/ways/test_track.py` (leg by leg; no recorded ford, whole; a leg clipped short, whole);
  the cohort; `impl-drift` on the claims owed; `spec-fidelity`.

## Wave 89 (amendment 88, 2026-10-09) - batch 11

- **A pre-existing defect fixed (constitution XIV): a door path the law refused was never tried another way.** Seed 33 was
  refused with a row farm off the network. Probed: its door path's straight step to the street was clear at the footpath's
  test (a zero gap) but passed 1 ft from the farm's own garden bed, and the law keeps a lane 7 ft off a fence (0246,
  `WEB_FABRIC_GAP`); `door_path` tried only that step, or the route where the step was blocked, so all six candidates were
  refused and the farm got no path (m:wave89-door-path-at-the-law-s-gap). Where the law refuses the first path, a route at
  the law's own gap is now tried, pulled taut only as far as the law's ground half keeps each step. Seed 33 rolls clean; the
  cohort 51 -> 52/54, none newly failing. Kashikawa: one door path, already lawful, moved 4 to 5 px further from its garden (the declared
  `village lane` occasion); four maps unchanged.
- **Verification**: `tests/hamletgen/ways/test_doors.py` (the law's-gap route tried where the taut step is refused); the
  cohort; `impl-drift` on the claims owed; `spec-fidelity`.

## Wave 90 (amendment 89, 2026-10-09) - batch 11

- **The reverted rows re-run on the hardened web, and two guards found by it (constitution XIV).** With waves 87-89 in, the
  cohort stands at 52/54 (refused 10 and 20); the reverted patches were re-run against it (m:retake-after-wave89). Wave 84's
  fork band now breaks four seeds where it broke six, wave 83's fillet the same four as before - every one of those a row
  village - so both stay reverted, E3. Probing wave 83's seed 902 found a door path's end pulled out of the law's arrival
  reach: drawn from a door 8.5 ft off its yard, `straighten_joints` pulled the joint at the door straight and split the lanes
  back at its foot 4 px off, 12.1 ft off the yard, past `STEADING_ARRIVAL_FT`, and the tree lane's end dangled
  (m:wave90-door-ends-arrive). Two guards, as 0246 has a way's end reach what it serves: `door_off_fixtures` steps a door only
  to where a path's end still arrives (`_arrives_at`), and `_one_joint` refuses a pull that would move an arriving joint out
  of reach (`arrives_off`). Alone on HEAD the cohort holds 52/54, none newly failing, no pool map moved; with the fillet patch
  902 holds. Seed 10's field way, diagnosed in this wave, is filed as a found row (E3).
- **Verification**: `tests/hamletgen/ways/test_serve.py` and `test_joints.py` (the two guards); the cohorts; `impl-drift` on the
  claims owed; `spec-fidelity`.

## Performance bookends (constitution VI)

Wave 1 changes no engine behavior (claim lines only) - no bookend owed. Waves 2-45 that changed engine behavior took
`make perf LABEL=328-start` / `-end` themselves. FROM WAVE 46 THE PAIR IS BATCHED (GM 2026-10-08, FR-005): one pair per
batch of 4-5 waves, the start at the commit before the batch's first engine change and the end at its last, both legs in
scratch worktrees back to back on a quiet host, then `make perf-explain` and the `perf-audit` subagent; the gate
(`make done`) and the batch's review occasions run at the same close. Each wave keeps its test files, map rerolls (and
`make notes-census`), `impl-drift` and `spec-fidelity`.

| batch | waves | pair | gate | state |
|---|---|---|---|---|
| 1 | 42-46 | waves 42, 44, 45 taken alone (band 1, 1, 0; confirmed); the batch 4a9b7c077 -> 2e3153b4e band 2, its cause (the track out drawn the canvas' diagonal past the frame, wave 46) removed by wave 47's `past_the_frame` - perf-audit consistent, audit not-justified as measured: batch 2's pair re-measures it, and explains seed 47's +0.19 s web at 40 households | green 2026-10-08 | closed but for the pair |
| 2 | 47-50 | 2e3153b4e -> 3f91becf2: band 1, TOTAL -3.5%; batch 1's band 2 re-measured and gone. Its one growth (seed 39, 10 households, homesteads +0.24 s, web -0.2 s) is wave 47's past_the_frame candidate sending that roll's track out through the fabric router - perf-audit CONSISTENT on its own control (the candidate undone removes the growth), profiled with the new `make perf-profile HOUSEHOLDS=` | green 2026-10-08 (waves 47-51, the NEEDS-WORK fixes re-gated) | closed: 12 glyph checks PASS (field pond, woodland commons and wet paddy after rounds 2-3) |
| 3 | 51-55 | 3f91becf2 -> HEAD: band 3 - 40 households +5.7% from seed 47 (+23.8%, web and homesteads: wave 52's privy and heap re-seating, bisected per commit) and seed 25 refused (T140); 10 households -7.2%, 20 -1.3%; seed 4's hinterland growth fixed in the batch (field_height_near in one vector pass) - m:batch3-pair-and-controls; perf-audit round 2: explanation CONSISTENT, audit cannot-determine (re-run once T140's seating is decided); the GM's band-3 sign-off owed | green 2026-10-08 | closing: 7 glyph checks PASS (homestead grove at round 2), the record checks answered; T137 and T140 open for the GM |
| 4 | 56-61 | 50bcf4385 -> a67389b82: band 2 - reference TOTAL -6.2%, sizes 0.0 / -0.8 / -0.9%; the first pair's band 3 (seed 4 at 10 households +217.9%, wave 61's privy slide across a door's way) fixed in the batch, and the audit's per-bearing fabric scan and per-call sun boxes indexed (m:batch4-pair-and-slide-fix, m:batch4-seed39-causes); perf-audit round 2: explanation CONSISTENT, audit JUSTIFIED; T140 confirmed (seed 25 at 40 households draws) | green 2026-10-09 (three runs: the cover-slot test, the uncovered no-yard line, then the fixes) | closing: glyph checks scrub and rough grazing PASS, copse PASS, privy NEEDS-WORK (F1: slides past the gable) - answered by wave 62, its second round at batch 5's close |
| 5 | 62-65 | a6004fdc6 -> bf7558093: band 2 - reference TOTAL +2.4%, 10 households -5.2%, 20 -3.8%, 40 +3.7%; seed 47 +11.9% and seed 25 at 40 households +15.0%, both wave 62's privy move (privies no longer past their gables stand at other attested places: more caption proofs, a second web settle), about 0.1 s wave 63's footing (m:batch5-pair-causes); perf-audit round 2: explanation CONSISTENT, audit JUSTIFIED (round 1 corrected the first attribution to wave 64) | green 2026-10-09 (after merging main's feature 312) | closed: glyph checks notice board, barley and privy (round 2) PASS; the board's facing at an entrance filed as a found row; 26 earlier glyph-check rows backfilled to the ledger, feature 371 filed |
| 6 | 66-69 | 7fd78f9a1 -> HEAD, taken three times: beside two renders and two review agents (load 4.4) band 2, every stage grown in proportion - load; on a quiet host twice, band 1 - TOTAL -0.6% and -1.8%, each flagged growth (homesteads in one, field in the other, stages the diff does not reach) within the same commit's run-to-run spread (m:batch6-pair); perf-audit round 3 CONSISTENT | green 2026-10-09 (the second run: the measured-surface test's add-only rule made a set) | closed: glyph checks notice board on inashiro and barley on kashikawa PASS |
| 7 | 70-73 | c0bf2b4c8 -> 43fe6fde0, taken twice: under another session's gate band 2 on one seed (20 households seed 39 +17.9%, identical placer calls, the growth on stages the batch does not reach); on a quiet host band 1 - TOTAL -2.3%, every households total within one percent, the largest seed 40 households seed 47 +1.5% (m:batch7-pair); perf-audit CONSISTENT | green 2026-10-09 at cc61be373 (the third run: the first broken by a duplicate gate, the second by an abbreviated pointer) | closed: glyph checks pond canal and drainage ditch on kuwabata and barley on kashikawa PASS |
| 8 | 74-77 | 43fe6fde0 -> 856bceb76, on a quiet host: band 0 - TOTAL -1.2%, every households total down (m:batch8-pair); nothing owed | green 2026-10-09 at 077e47717 | closed: glyph checks pond canal and drainage ditch on kuwabata and barley on kashikawa PASS again (re-owed by the engine's move) |
| 9 | 78-82 | 856bceb76 -> 277593132, on a quiet host: band 1 - TOTAL -0.6%, every households total within 0.2%, the largest 40 households seed 4 +0.6% (windbreak +0.06 s, inside that stage's same-commit jitter); the field stage, where the batch's code runs, flat (m:batch9-pair); perf-audit CONSISTENT | green 2026-10-09 at f86f95ddc (the second run: the first caught wave 78's dropped grave-cut basin, fixed by wave 82) | closed: glyph checks pond canal and drainage ditch on kuwabata and barley on kashikawa PASS; the fillet radius filed as a found row |
| 10 | 83-86 | 277593132 -> 3197171ce, on a quiet host: band 1 - TOTAL -3.4%, 10 and 20 households down, 40 households +0.4% (seed 25 +0.7%, homesteads +0.1 s), every growth under the per-seed noise floor; the batch changed no executed code (three waves reverted, one held: comments only) - perf-audit consistent (m:batch10-pair) | green 2026-10-09 at 3197171ce | closed: no occasion owed (wave 86's glyph occasion withdrawn with its revert) |
| 11 | 87- | owed at the batch close | at the batch close | open |

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
