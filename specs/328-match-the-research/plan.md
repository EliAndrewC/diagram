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
| 5 | 62- | owed at the batch close, from a6004fdc6 | at the batch close | open |

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
