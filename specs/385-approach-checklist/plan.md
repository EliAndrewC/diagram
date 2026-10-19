# Implementation Plan: the approach checklist - the front of 384, one task at a time (feature 385)

**Approach checklist**: specs/385-approach-checklist/checklist.md

**Spec**: `spec.md` | **Request**: `request.md` | **Checklist**: `checklist.md` | **Audit**: `audit.md` | **Builds on**: the lane
law (`l7r/diagram/hamletgen/ways/law.py`, `law_water.py`), its settle (`settle.py`, `last_resort.py`), 384's FR-000 and User
Story 0, and the event log behind `make feature-report` (feature 375).

## Summary

The tasks run one at a time, in the GM's order (2026-10-17: *"make the plan, then do the lane law as task one, work that under the
checklist with a retro afterwards, and then let's see how it goes"*). Each task's section below opens with its **Approach** block,
checklist part A answered, and the task is not ticked until its retro row is in `retro.md` and any change the row names is made.
The tooling that enforces this (FR-003 to FR-005) is T02, built after T01 so its first retro can shape it; T01's Approach block
and retro are kept by hand, and T02's per-task split is proven by replaying T01's events.

After T01 the session stops and reports to the GM before T02 (his "let's see how it goes").

## Constitution Check

- I-V: no SOURCE block or hand map is touched; pool hamlets re-roll as the engine changes (VI), measured on the cohort.
- XII: T01's decisions are classed in its rule table (research, the GM's ruling, a convention of ours); each changed rule's why
  is written at the predicate and on the lane drawing pages (0081, 0246).
- XIII: a seed that passes at HEAD and fails after T01 is a regression, measured on the 48-seed cohort against HEAD's run.
- XIV: the refusal that named lanes but not the rules they break (found while measuring T01) is fixed in T01 (D3).
- XVI: built as asked: the angle rules admit a meeting an obstruction forces, side-by-side lanes merge; no other rule is
  loosened.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
## Landing

Each task lands when it closes, with its retro row, while the tasks after it stay open: the feature is worked one task at a time by
design (FR-006), and each task's change - T01's lane law first - reaches main before the next starts, so the next task's
measurements are taken on it.

**Lands open**: T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T46, T66, T67

<!-- plan-archive: T03 to T05 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
## T04 to T10 - T48, T47's patch, five ranking rows

Each decided at its start, in this order (spec FR-007), its section added here and reviewed by `make decide`.

## T04 - T48: the web carries a re-deal of the seats (384 User Story 2, SC-004)

### T04 Approach (checklist part A)

1. **The goal, in the world.** Wave 155's pocket-well change (the well off the farmstead, `w155-pocket-attempt.patch`) moves
   where homesteads are seated; the lanes are trodden after the houses stand, so whatever seats the re-deal produces, the web
   walks round them - no seed refused for a web that could have been walked.
2. **The constraints.** SC-004: the re-deal cohort (`m:w156-redeal-cohort`'s method - `make cohort N=48`, then the patch applied
   and the same cohort) fails no seed that passes at HEAD; the lane law's rules (`ways/law.py`); the pool; 384 FR-002 (374's rules
   as amended). Baseline 2026-10-13: HEAD 50/54, patched 49/54 - 10 and 24 newly failing, 17 mended. T03 has since fixed 17, 21,
   40 and 45 at HEAD, so the baseline is retaken first.
3. **Where each comes from.** SC-004 is the GM's (G, 384). Each lane-law rule a refusal names is checked, R/G/O, from its claim,
   when it refuses (B2) - not listed in advance from memory.
4. **Do they describe the world here?** Asked of each refusal at the place it refuses, from a dump of the geometry (B1, B3):
   would a reader of the research call that map wrong?
5. **The order.** Homesteads first, then lanes (GM 2026-10-02): the fix is in the web, never a re-deal moved to suit a lane.
6. **The exits.** Weighed per refusal once measured: (a) an O number, (b) an exception the ground forces (`forced.py`), (c) a
   rule that dissolves it, (e) conform. (d) more room is the re-deal's own business, not the web's.
7. **The search smell.** Watch for a retry or re-order loop in the settle; the third tuning of one thing is a step back (B5).
8. **The budget.** About two hours (a guess: the retaken baseline, two seeds' causes, their fixes, one cohort, the landing).
9. **Done, measured.** ONE goal: the patched 48-seed cohort fails no seed that passes at HEAD, both rolled now, compared by
   `cohort_known` (FIXED / NEWLY FAILING / WORSENED / PRE-EXISTING). T05 (re-landing the patch itself) is a separate task.

### T04 Decisions

**D35 - measured first, and the web already carries the re-deal: no engine change.** Retaken 2026-10-18 by
`m:w156-redeal-cohort`'s method on today's HEAD (055a12b5c): `make cohort N=48` passes 54/54
(`dev/cohort-log/20261018T023923Z-diagram-backlog-373625.json`); with `w155-pocket-attempt.patch` applied (it applies cleanly) the
same cohort passes 54/54 (`dev/cohort-log/20261018T024147Z-diagram-backlog-378026.json`; the reference map a roll-cache MISS, so
the patched engine rolled). Seeds 10 and 24, newly failing under the patch on 2026-10-13, pass: T03's fixes (the own-garden gap,
the last resort's join order, the sty band) were what the re-deal had been knotting on. SC-004 is met as the code stands;
building a web change to meet it would be a fix with nothing to fix. The patch is reverted in the tree - re-landing it, with its
pool and record checks, is T05's one goal (D34).

The tooling fix this task's measurement found (a cohort record rolled over an uncommitted engine diff reads as its commit's)
is its own task, T15 (D34: one goal a task; spec-fidelity, T04 round 1); the hour-9 step-back's tooling fix is T16. T04's goal is
384's SC-004 (here FR-007, SC-003).


### T04 part B (2026-10-18T02:49Z)

Owed by the hour-9 step-back (`hour:385-approach-checklist@9`, ruled `continue`).

1. **What is refusing?** Nothing in the maps: both cohorts pass 54/54. The plan review (round 1) BLOCKED D36 as a second goal.
2. **A3 again.** SC-004 is the GM's (G, 384); no lane-law rule refused, so none to place.
3. **A4 again.** n/a - no refusal on the ground.
4. **Moving something earlier for something later?** No: nothing moved.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "The re-deal already passes; nothing to build" - nothing for the GM to question but the measurement,
   which names both records.
7. **The next step is a measurement.** None owed: SC-004 is measured. The next step is T04's tick.
8. **Routes measured before asking?** Nothing is being asked.
9. **After a ruling.** `continue`; the step it names is T04's plan review, then the stamp - moved to T15 by that review.

## T05 - T47: the wave 155 pocket-well patch re-landed, no waiver (384 FR-007)

### T05 Approach (checklist part A)

1. **The goal, in the world.** A clustered hamlet's well stands off every farmstead, shared, as 0028 and 0196 describe ("shared
   off the farmstead"; "one or two" a hamlet, five to ten households a well); no household's homestead holds a pocket well.
2. **The constraints.** 374's W155-4 bar: no roll passing at HEAD refuses (the pool, the cohort); no well inside a homestead; every
   household within reach of water (`WATER_REACH_FT`, 760 ft, 0196); no well over ten households; the counts recorded. The lane
   law; the claims and record checks the patch's changes owe; three glyph-check occasions (a pool map's well moved: Inashiro,
   Kuwabata, Sawada - 374's tasks.md); the gate, green.
3. **Where each comes from.** The bar is the GM's process (G, 374) over research rules: 0028/0196 (R) for off the farmstead and the
   count; 760 ft (R, 0196); the shares cut along the long axis (GUESS, W155-5, recorded); the third well for ten (R, 0196's range).
4. **Do they describe the world here?** Measured by T04 on today's engine: the patched cohort passes 54/54. Each refusal the pool
   or a check names is asked again at the place it refuses (B1-B3).
5. **The order.** The seating lays no pocket; the wells are seated after the houses (wave 154's forms) - nothing placed earlier
   moves for a well.
6. **The exits.** The patch's own were priced in 374 (W155-6: more room priced first, the third well inside the research range
   taken). Here: (e) conform - re-land as built, no waiver.
7. **The search smell.** None new: the patch's searches are wave 154's, measured.
8. **The budget.** About 90 min (the pool, the record and claims checks, three glyph checks, the gate).
9. **Done, measured.** One goal: the patch on main with no waiver - the pool clean, the cohort as HEAD (T04: 54/54 both), the
   wells measured (`m:w155-wells`'s quantities on the pool), every owed check answered, the gate green.

### T05 Decisions

**D41 - the patch re-landed as built.** `w155-pocket-attempt.patch` applies cleanly to today's HEAD (2026-10-18; the engine
unchanged since T04's cohorts). Its decisions are 374's W155-1 to W155-6, each ruled within by 374's plan review; nothing in
them changes here. Its bar is W155-4, measured on the pool and the 54-seed cohort (T04: 54/54 at HEAD and patched); the 44 rolls
of 374's scratch tooling (`tools13/roll13.sh`) are not reproducible from the repository, so the cohort stands in for them, as
384's SC-004 already did. The occasions are 374's three (placement-changed: well on Inashiro, Kuwabata, Sawada), each a
glyph-check of its map's wells.

### T05 part B (2026-10-18T03:50Z)

Owed by the hour-10 step-back (`hour:385-approach-checklist@10`, ruled `continue`).

1. **What is refusing?** Nothing on the maps: the pool rolls clean with the patch; no well on any homestead piece. The record
   checks found three wordings in 0196's changed block (applied together); the hour guard split one batch of dispatches (T20).
2. **A3 again.** The bar's rules as part A: 0028/0196 (R), 760 ft (R), the shares (GUESS, recorded).
3. **A4 again.** Asked at the pool's wells: they stand off every farmstead, each serving 3 to 10 households.
4. **Moving something earlier for something later?** No: the wells are seated after the houses.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "The patch re-lands as built, measured as 374 measured it" - nothing to question but the bar's
   numbers, recorded beside it.
7. **The next step is a measurement.** The remaining checks' answers, then the gate.
8. **Routes measured before asking?** Nothing is being asked.
9. **After a ruling.** `continue`; the step it names is re-dispatching the three refused checks (done) and the landing.

### T05 part B (2026-10-18T10:25Z)

Owed by the hour-12 step-back (`hour:385-approach-checklist@12`, ruled `continue`).

1. **What is refusing?** Nothing on the maps: the pool rolled on T05's tree is clean (`make maps SCOPE=all`, 2026-10-18), the gate
   green (199 s) after three reds of three causes (a reviewer's British spelling in a record, a stale notes census with Sawada's
   door zigzag gone - its strict xfail cleared - and `seat_wells`' early return uncovered), and the three well glyph-checks PASS.
   The claims gate refused only old behavior the patch's unit touched (the front row's size, the standoff), carried into T06 by
   ask:t05-old-drifts-at-landing.
2. **A3 again.** The bar's rules as part A; the claims relabeled to what the record says (0031 for the cluster shape, the 80 ft
   seat a GUESS 0196 names), the standoff split (house and yard on 0029; the shed in and the garden out UNRESEARCHED).
3. **A4 again.** Asked at the drawn wells by the glyph-checks: none stands in a farmstead, each serves 3 to 10 households; two seats
   read near a lane (Inashiro F6/F7, Kuwabata F8) - filed as found rows of wave 155, not tuned here.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: no number moved; every change since part A was a label, a test or a record.
6. **The one-sentence test.** "The patch re-lands as built, its claims saying what the record says" - true.
7. **The next step is a measurement.** The landing cohort (`make cohort-landing`), then the push.
8. **Routes measured before asking?** Yes - the pool rolled before ask:t05-old-drifts-at-landing.
9. **After a ruling.** `continue` (hour 12) and `continue` (the ask): land T05; its fixes T25 (landed) and T26 (in review).

<!-- plan-archive: T07 to T26 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T59 to T59 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T10 to T10 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
## T56 - a task's own heading wins its section (found by T47/T48 and T10's preflights)

### T56 Approach (checklist part A)

1. **The goal, in the world.** A task's decision preflight reviews that task's own section, never a heading that only names it.
2. **The constraints.** FR-003a (a task's decisions reviewed alone); the plans already written keep their headings; tooling only; a
   test red without it.
3. **Where each comes from.** `task_sections` is 375's (O, plan D3).
4. **Do they describe the world here?** Yes - measured 2026-10-18: the preflights of T47 and T48 reviewed the umbrella heading "T04
   to T10 - T48, T47's patch, five ranking rows", and T10's did too - the first heading naming an id took it, so each task's own
   later `## Txx - ...` section went unreviewed (the tasks were renumbered T49/T50 to get past it).
5. **The order.** The rule, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a plan with an umbrella heading naming T10 before T10's own section gives T10 its own section;
   `tests/tooling/test_plan_gate.py` red without it.

### T56 part B (2026-10-18T19:04Z)

Owed by the hour-20 step-back (hour:385-approach-checklist@20, `continue`), which fell while T56 was the active task.

1. **What is refusing?** Nothing of T56's: its test passes, red without the rule.
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged; measured on the three preflights.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither since part A.
6. **The one-sentence test.** "A task's preflight reviews its own section" - true by its test.
7. **The next step is a measurement.** T10's preflight on its own section.
8. **Routes measured before asking?** n/a.
9. **After a ruling.** `continue`; the ruling's tooling fix is its own task (T57).

### T56 Decisions

**D75 - own before mention.** `task_sections` first takes, for each id, the first heading whose title BEGINS with that id (`## T10 - ...`,
`### T10 Approach`); only an id no heading begins with falls back to the first heading that mentions it, as before.

<!-- plan-archive: T57 to T58 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T42 to T42 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T60 to T60 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T61 to T61 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T62 to T62 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T63 to T63 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T64 to T64 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T65 to T59 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
## T66 - a requirement cited from another feature is bundled from that feature (found by T65's plan review, 2026-10-18)

### T66 Approach (checklist part A)

1. **The goal, in the world.** A plan review reads the requirement a block cites, not a same-numbered requirement of another feature.
2. **The constraints.** Feature 375 amendment 11 (FR-046): `spec-cited.md` holds every requirement the blocks name, in full. Tooling only; a test red without it.
3. **Where each comes from.** Feature 375 (O); the defect is T65's plan review's finding (amendment 6, the GM's "obvious ... tooling ... improvements").
4. **Do they describe the world here?** Yes - measured 2026-10-18: T65's blocks cite "Feature 375 FR-044" and "FR-005(b)"; the bundle's `spec-cited.md` carried 385's own FR-005 (the per-task time split), a different requirement, and nothing of 375's - `plan_bundle.build` reads the ids against the reviewed feature's `spec.md` alone. 385's plan names another feature's requirement in this form ("feature 375 FR-0..", "375 FR-0..", "feature 375, FR-0..") in 22 places (a grep of plan.md for the form, 385 itself left out).
5. **The order.** The qualified reading in `build`, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 25 min.
9. **Done, measured.** One goal: a block citing `375 FR-044` (or `feature 375 FR-044`, `feature 375's FR-044`, `feature 375, FR-044`) gets 375's FR-044 paragraph in `spec-cited.md`, headed with its feature, and the reviewed feature's same-numbered requirement only when the block also cites it unqualified; `tests/tooling/test_plan_blocks.py` red without it.

### T66 Decisions

**D85 - a qualified citation read from its own feature.** `plan_bundle.build` reads `(?:feature )?NNN(?:'s|,)? (FR|SC)-NNN` as a citation of feature NNN's requirement, resolved from that feature's `specs/NNN-*/spec.md` (the one directory; none or several, it is left out as an unknown id is now) and written to `spec-cited.md` under a `<!-- feature NNN -->` line; an unqualified id is the reviewed feature's, as before - so a block that cites another feature's requirement writes the feature beside every id it means (the reviewer reads what the block names, no guess at which feature a bare id meant). `spec-index.md` is unchanged.

## T67 - land-tooling lints before it tests (found landing T65, 2026-10-18)

### T67 Approach (checklist part A)

1. **The goal, in the world.** A landing that will fail on lint fails in seconds, not after the tests.
2. **The constraints.** Feature 385 T52: land-tooling lints the Python it lands; the guard suites and tooling tests still run in parallel; every check's failure is still reported. Tooling only; a test red without it.
3. **Where each comes from.** T52 (O); the defect is measured landing T65 (amendment 6, the GM's "obvious ... tooling ... improvements").
4. **Do they describe the world here?** Yes - measured 2026-10-18 (`.git/land-tooling.log`): T65's landing ran the tooling tests 60.24 s and the checks step 122.20 s, then failed on `ruff format --check` (one test file would be reformatted), a check that took 0.05 s; the three checks run in parallel and the step waits for all of them.
5. **The order.** Lint alone first in `land-tooling.sh`, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a landing whose lint fails stops before the guard suites and the tooling tests start, with the lint message and the `ruff format` command; `tests/hooks/test-land-tooling.sh` (the script's suite) red without it.

### T67 Decisions

**D86 - lint first, alone.** `land-tooling.sh` runs the `lint` check before the other two; a lint failure dies at once with its output and the `ruff format <files>` line it prints now, the guard suites and tooling tests not started; a passing lint goes on to the two in parallel as now.

## T11 - the close

The checklist to `docs/`, the refusals extended to every feature's tasks (FR-001), the final report (SC-001, SC-002).
