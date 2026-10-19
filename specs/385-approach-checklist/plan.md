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

**Lands open**: T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T46, T66, T67, T68, T69, T70, T71, T72, T74, T75, T76, T77, T78, T79, T80, T81, T82, T83, T84, T85, T86, T87, T88, T89, T90, T91, T92, T93, T94, T95, T96, T97, T98, T99, T100, T102, T103, T104, T105, T106, T107, T109, T110, T111, T112, T113, T114, T115, T116, T117, T118, T119, T120, T121, T122, T123, T124, T125, T126, T127, T128, T129, T130, T131, T132, T133, T134, T135, T136, T137, T138, T139

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
<!-- plan-archive: T66 to T65 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T67 to T65 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T68 to T66 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T69 to T10 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T70 to T70 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T72 to T70 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T75 to T75 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T77 to T77 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
## T78 - the house style corrects what the tools write from an agent's reply (the GM-approved fix of 2026-10-18)

### T78 Approach (checklist part A)

1. **The goal, in the world.** An agent's British spelling never reaches a tracked file through a tool, so it never turns a gate red.
2. **The constraints.** CLAUDE.md, house style: American spellings everywhere, corrected rather than refused, a quotation of another's text kept (`<blockquote>`, `<q>`, 「」, “”), the GM's own writing never corrected. Amendment 6: "implement any obvious performance / tooling / process improvements along the way" - this applies the GM's own house-style rule on a route the hook does not see. The hook's word table (`hm_house.PAIRS`) is the one table. A test red without it.
3. **Where each comes from.** CLAUDE.md (G); the table is 236's (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19: T10's gate preflight was red on `dev/claims-index.json:51334: 'grey'`, a note `claims.py record` copied from an impl-drift reply; two writers copy agents' words into tracked files without the hook seeing them - `claims.py record` (the index notes) and `apply_edits.py` (the record and pop-up text of EDIT blocks).
5. **The order.** A module-level `americanize` in `hm_house.py`, its call in the two writers, then the tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: `claims.py record` writes `gray` where the reply's note said `grey`, and `apply_edits.py` writes an EDIT's new text with the table's corrections, a quotation held out as the hook holds it; `tests/tooling/test_claims_index.py` and `tests/tooling/test_apply_edits.py` red without it.
10. **Before moving a constant.** n/a - none moves.
11. **Before fitting things into room.** n/a - nothing is fitted.

### T78 part B (2026-10-19T01:27Z)

Owed by the hour-25 step-back (hour:385-approach-checklist@25, `continue`).

1. **What is refusing?** Nothing: T78 is built and landed, both tests green.
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither - the change is landed.
6. **The one-sentence test.** "A tool writes an agent's words in the house style" - true by its two tests.
7. **The next step is a measurement.** None owed for T78.
8. **Routes measured before asking?** n/a - no ask.
9. **After a ruling.** `continue`; its tooling fix (a tick claiming "landed") is its own task.

### T78 Decisions

**D97 - one corrector, three callers.** The hook's nested plain-text correction (`PAIRS` outside the held spans) becomes `hm_house.americanize(text) -> str`, which the hook calls as before; `claims.py record` passes each note it parsed from a reply through it (never the whole reply: a claim key or path carrying a British spelling must still match - the plan review's point, 2026-10-19), and `apply_edits.py` passes each EDIT's new text through it before writing (the old text is matched as written). An EDIT on a file the GM wrote (`specs/*/request.md`) is not corrected, as the hook does not correct one.

## T79 - a tick saying "landed" is refused while the landing is not on main (the round arbiter's fix on hour:385-approach-checklist@25)

### T79 Approach (checklist part A)

1. **The goal, in the world.** A task's tick never claims a landing that did not happen.
2. **The constraints.** The arbiter's fix: "`make tick` refuses a task whose NOTE says 'landed' while any file in that task's last `make land-tooling` FILES still differs from origin/main, or while that landing's log ends in a failure, naming the file and the log"; a note that does not say "landed" is not checked. A test red without it.
3. **Where each comes from.** The fix is the arbiter's (G); `make tick` is 188's (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the hour-25 bundle): at 00:49 `make tick F=385 T=T72` ticked with the note "landed" while T72's latest `make land-tooling` had failed - a whole-string replace in its test missed a dict the formatter had split across lines.
5. **The order.** `land-tooling.sh` records each run's FILES and outcome; `tick-task.py` reads the last record for the task; then the tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: a tick whose NOTE says "landed", in any case ("Landed" too), is refused while the task's last land-tooling run failed, or one of its FILES differs from origin/main, naming the file or the log; `tests/tooling/test_tick_task.py` red without it.
10. **Before moving a constant.** n/a - none moves.
11. **Before fitting things into room.** n/a - nothing is fitted.

### T79 Decisions

**D98 - the landing's record read at the tick.** `land-tooling.sh` appends `{task, files, outcome, utc}` to `<git dir>/land-tooling.jsonl` from an exit trap, so a run that dies early still leaves its row (outcome: the step it stopped at) (the task is the clone's active one, from `task-starts.jsonl`; `outcome` is "landed" or the step that failed). `tick-task.py`, when the NOTE matches `\blanded\b` in any case (`re.I` - the plan review: "Landed via make land-tooling" is the same claim), takes the task's last such row: a failed outcome refuses, naming the log; a landed one refuses where `git diff --quiet origin/main -- <file>` fails for a file in it (after a fetch), naming the file. A task with no row is not refused (it did not land through the tool, or lands with its feature).

<!-- plan-archive: T80 to T78 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T81 to T81 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T82 to T79 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
## T83 - a dictionary's claims keyed per entry (the GM 2026-10-18, step 5 of the approved order)

### T83 Approach (checklist part A)

1. **The goal, in the world.** One entry added to a claimed dictionary re-opens only the claims that entry bears on.
2. **The constraints.** The GM, 2026-10-18 (amendment 8): "instead of filing me per entry key ring feature, you should just work it. As a task on this existing feature", and earlier "I do want it, though, if it is helpful". Feature 375 FR-002's rule for a procedure section, applied to a dictionary: a claim's fingerprint is its own line; the body changing owes a TRIAGE of the changed blocks (`claims-triage`), which sends on to `impl-drift` only the claims a changed block touches; a one-time backfill re-keys the rows current under the old fingerprint, owing nothing. A claim's line changing still owes it in full. A test red without it.
3. **Where each comes from.** The GM (G); the section rule is 375 FR-002 (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (an AST pass over every claims-index unit): 57 module-level dict constants carry 132 claims over 404 entries; `_OVERLAP_EXEMPT` alone carries 17 claims over 41 entries, and one entry added there at T08 owed all of them (step-back-2026-10-18.md: a 64-claim round, 372 s and 1.29M input tokens). A claim is labeled by topic, not by key ("annexes abut their house"), so no key-to-claim map can be read off the code; the triage is what reads the changed entry against each claim.
5. **The order.** The engine's claims reader (`l7r/diagram/tools/claims.py`): a claimed dict's entries become its blocks and its claims' code their own line; `scripts/record/claims.py`: owed and the backfill take any unit with blocks, not only sections; the backfill run once; then the tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 90 min.
9. **Done, measured.** One goal: an entry added to a claimed dict owes its claims a triage (`section triage`), not `code changed`; a claim line edited owes that claim in full; after the backfill `make claims-owed` owes no dict claim it did not owe before; `tests/tools/test_claims.py` and `tests/tooling/test_claims_index.py` red without it.
10. **Before moving a constant.** n/a - no constant's value moves.
11. **Before fitting things into room.** n/a - nothing is fitted.

### T83 part B (2026-10-19T02:35Z)

Owed by the hour-26 step-back (hour:385-approach-checklist@26, `continue`).

1. **What is refusing?** Nothing: the gate is green and the landing cohort 54/54.
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither - landing what was checked.
6. **The one-sentence test.** "An entry added to a dictionary owes its claims a triage, not a full check" - true by the probe and the tests.
7. **The next step is a measurement.** The landing.
8. **Routes measured before asking?** n/a - no ask.
9. **After a ruling.** `continue`, no tooling fix.

### T83 Decisions

**D103 - a dictionary is read as its section is.** In `all_units`, a module-level constant whose value is a dict literal and which carries its own claims gets `blocks` = one per entry (`key: value`, its source unparsed, whitespace folded); `Unit.code` fingerprints such a claim by its own line, as a section's (`"section-claim"`), and `core` stays the whole value's.

**D104 - owed and backfilled as a section's.** `claims.py owed` owes `section triage` for a unit with blocks whose recorded `section` core differs (sections and dicts alike); `backfill-sections` re-keys a dict claim whose row is current under the old fingerprint (core plus line), recording its core and block digests, and leaves an owed one owed. The backfill runs once with this change, its count in the retro.

<!-- plan-archive: T84 to T84 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T85 - an edit to a plan section is refused while its review runs (proposal B, 2026-10-19)

### T85 Approach (checklist part A)

1. **The goal, in the world.** A plan review is never wasted on a section edited while it ran.
2. **The constraints.** The GM, 2026-10-18 23:00 EDT (amendment 9): "build all 7 of those as 385 tasks"; proposal B: "the plan-write path refuses an edit to a section whose review is running, naming the agent". Edits to other sections, and to the plan's other files, go through; the escape is `PLAN_EDIT_OK="<reason>"`, recorded, for a dead dispatch's hold only. A test red without it.
3. **Where each comes from.** The GM (G); the tools it changes are this feature's and 375's (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the second pass): 2 of the evening's 42 plan reviews returned unrecorded - `plan-verdict` refused them, "section_sha256 does not match ... it changed while it was being reviewed" - after I edited T76's and T77's sections while their reviews ran.
5. **The order.** The refusal in `hm_checks` (which knows each running dispatch and its bundle), wired to the Edit and Write tools and to a Bash write of the plan, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: an Edit of `specs/<f>/plan.md` whose old text lies in the section of a task with a plan review running, or a Bash command writing that plan and naming that task's section heading, is refused, naming the running review's agent; a block under a running `plan-delta` review is held the same way; an edit elsewhere passes; `tests/tooling/test_plan_edit_refusal.py` (new) red without it.
10. **Before moving a constant.** n/a - none moves.
11. **Before fitting things into room.** n/a - nothing is fitted.

### T85 part B (2026-10-19T04:58Z)

Owed by the hour-27 step-back (hour:385-approach-checklist@27, `continue`).

1. **What is refusing?** Nothing: T85 is landed and its suites green.
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither - landed as reviewed.
6. **The one-sentence test.** "A section under review cannot be edited under it" - true by its two tests.
7. **The next step is a measurement.** None owed for T85.
8. **Routes measured before asking?** n/a - no ask.
9. **After a ruling.** `continue`; its tooling fix (the foreground lint) is its own task.

### T85 Decisions

**D106 - the section or block under review is held.** Every running `spec-fidelity` plan review holds what its bundle names: a task preflight (`plan-<feature>-<T>`) that task's section, a block review (`make plan-delta`) each block in its `blocks.md`. A write that would change held text is refused, naming the running review's agent and its task or blocks: an `Edit` of the plan whose `old_string` lies in, or whose `new_string` lands in, held text; a `Write` of the plan whose new content differs from the plan in held text; a Bash command whose write targets (`hm_house.write_targets`) include the plan and whose text contains the held heading or any line of held text (the same test the Edit path applies). `PLAN_EDIT_OK="<reason>"` passes it, recorded, only for a hold a dead dispatch left (no agent of that review still running, by the pair state); a live review's held text has no escape - the session waits for it to return (the plan review, 2026-10-19). The suite shows the refusal red without the hook, never green by the escape, and covers the held-line case as well as the heading.

<!-- plan-archive: T86 to T86 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T87 to T87 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T88 to T88 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T89 to T89 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T90 to T90 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T91 to T91 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T31 - a footpath's 4 ft off a plot, recorded (ranking row 843, MISLABELED - a kind not yet tried)

Chosen at its start (FR-020): of the open rows still open in the claims index, the first kind not yet tried in T05-T10 (four
DRIFTED, one NEEDS-RESEARCH) is MISLABELED; row 827 (the first) is IN-STEP since, so row 843 is taken; row 841, which reads
the same constant, is T95.

### T31 Approach (checklist part A)

1. **The goal, in the world.** A footpath, walked in single file, runs closer to a garden fence than a lane does; the map says so
   and the record says why.
2. **The constraints.** Row 843's fix: "0246 answers this: 'a lane's middle keeps at least 7 ft clear of a garden fence', 3 ft
   footpath included; 4.0 departs from it, so the claim should be DEVIATION 0246, and 0246 must record the 4 ft (it does not) or
   the code is DRIFTED". Row 841's: "the joining leg's berth at 0246's 7 ft off a garden fence (it reads FOOTPATH_FABRIC_GAP, held at
   4 ft); the claim cites 0246". Room before packing (GM 2026-10-12).
3. **Where each comes from.** 0246's 7 ft is O: the page itself calls it "a map drawing convention, not a measured figure". The
   4 ft is O (feature 328 wave 4). Room before packing is G.
4. **Do they describe the world here?** Measured 2026-10-19 (`make cohort` with `FOOTPATH_FABRIC_GAP` at 7.0, then put back):
   4 seeds newly fail - 3, 4 and 903 refused by the web (`WebRefused`), 904 by a row rule - so a footpath held to the lane's 7 ft
   cannot reach farmhouses the cohort places today. Since the lane's margin is a convention, not research, room before packing
   does not bind it: an unresearched number is a knob to move, never a target to defend.
5. **The order.** The record first (0246's drawing page states the footpath's own convention and why), then the two claims point
   at it, then the stale comment.
6. **The exits.** (a) refine an O number - chosen: the footpath's 4 ft becomes 0246's own recorded convention; (d) more room - not
   chosen: re-seating to give four seeds 17 ft of footpath room (2 x 7 + 3) changes every hamlet's spacing for a convention, where
   the 4 ft asks 11 ft; (b), (c), (e) - none fits a margin that is a convention both ways.
7. **The search smell.** None - no search changes.
8. **The budget.** 60 min.
9. **Done, measured.** One goal: 0246's drawing page records a footpath's middle 4 ft off a garden fence as a map drawing
   convention, `FOOTPATH_FABRIC_GAP`'s claim cites it, and the claims check finds it IN-STEP; no value changes.
10. **Before moving a constant.** No constant's value moves. Its uses (measured 2026-10-19, a grep of `l7r/`): the footpath's clearance off
   a plot in `bund.py`, `street.py` (the joining leg), `track.py` (a footpath's clip and its `+ 1.0` and `+ CONNECTOR_WIDTH / 2`
   uses), and the door offsets `FOOTPATH_FABRIC_GAP + 4.0` in `serve.py`, `web.py` and `row_rules.py`.
11. **Before fitting things into room.** Footpath room between two plots: 2 x 4 + 3 = 11 ft at 4 ft, 2 x 7 + 3 = 17 ft at 7 ft.

### T31 Decisions

**D113 - the footpath's margin is 0246's own convention.** 0246's drawing page gains a block of its own beside the lane's 7 ft: a
footpath is narrower than a lane's tread, so it keeps its middle 4 ft off a garden fence, a map drawing convention, because held to
the lane's 7 ft some settlements leave a farmhouse with no footpath to it (the seeds in a comment). `FOOTPATH_FABRIC_GAP`'s claim
becomes a pointer to that page, and the comment above the constant records it. No value changes; row 841 (the street's joining leg,
which reads this constant but is drawn as a lane) is its own task, T95 (FR-015, one goal).


### T31 part B (2026-10-19T05:50Z)

Owed by the cohort record of 05:04Z (seeds 3, 4, 903 and 904 newly failing) - that run was the trial of `FOOTPATH_FABRIC_GAP` at
7 ft, not a landing.

1. **What is refusing?** Nothing now: the trial at 7 ft failed those four seeds, so the value stayed 4 ft (D113).
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged - the four seeds are the measurement the decision rests on.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither in this part B: the 4 ft recorded on 0246 is D113's change, decided and reviewed before it.
6. **The one-sentence test.** "0246 records a footpath's 4 ft and the constant's claim cites it" - true; the claims check found it IN-STEP.
7. **The next step is a measurement.** The landing cohort at 4 ft.

### T31 part B (2026-10-19T06:27Z)

Owed by the round arbiter's ruling on hour:385-approach-checklist@28 (change-route) and by the probe cohorts of 06:17Z that rolled
the four seeds at 7 ft again.

1. **What is refusing?** At 7 ft, cohort seeds 3, 4, 903 and 904 - all four the linear form - leave a farmhouse off the network
   (904 also a farm off its street), measured 2026-10-19 (`make cohort N=1 SEED=<n>` with the constant at 7.0, reverted).
2. **A3 again.** The 4 ft's reason as written is fit, not research - the arbiter's finding; the room route was named and not tried.
3. **A4 again.** Unchanged: 0246's 7 ft holds for a lane; the footpath's figure is open until room is tried.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither in this part B: the room route is its own task, worked with T43 before T32.
6. **The one-sentence test.** "T31's 4 ft is the record until the room task settles it" - true; the room task decides it.
7. **The next step is a measurement.** The linear form's farm and door spacing at the four seeds, with the constant at 7 ft.
8. **Every route measured before offering one?** Not yet, and none is offered here: the routes are T96's, which measures each on
   the four seeds and the cohort before choosing.
9. **After a ruling: the step it names?** Yes - the ruling names more room first, as its own task before T32; T96 is that task.
<!-- plan-archive: T92 to T31 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T96 - a footpath's 7 ft, room first (the round arbiter's ruling on hour:385-approach-checklist@28; worked with T43)

Opened by the ruling's `what`: before T32's ranking row, a task for `FOOTPATH_FABRIC_GAP` (4 ft, recorded on 0246 by T31) whose first
route is more room; the footpath's tread-to-wall figure open in T43 is worked with it, not as a second row.

### T96 Approach (checklist part A)

1. **The goal, in the world.** A footpath keeps a lane's distance from the gardens it passes, and every farmhouse is still reached.
2. **The constraints.** 0246: a lane's middle, a 3 ft footpath's included, keeps at least 7 ft clear of a garden fence, and a household's own way may run beside its own fence (T43 item 3). 0081 and 0247: a tread keeps 3 ft off a farmhouse wall (T43 item 1). The GM, 2026-10-12: room before packing. The GM, 2026-10-02: homesteads before lanes, never lanes first. The ruling: the 4 ft stays only labeled UNRESEARCHED with the trial as its trail.
3. **Where each comes from.** 0246's 7 ft is O, a map drawing convention; the own-fence allowance is 0246's (O); 3 ft is 0081's and 0247's (O); the two rulings are the GM's (G).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (`make cohort N=1 SEED=<n>` with the constant at 7.0, reverted): cohort seeds 3, 4, 903 and 904 all the linear form, each leaving a farmhouse off the network (904 also breaks `undeckable`); with `DOOR_ROOM_FT` and `FOOTPATH_DOOR_OUT_FT` derived from the 7 ft (19 and 15 ft) the same farmhouses stay unreached at the same seats; seed 4's (1404, 3220) stands about 130 ft from the nearest way, its own threshing yard and garden beside its door (the refused manifest). The cause, measured 2026-10-19 (a scratch probe of seed 4 at 7 ft, logging `front_door` and `door_path`, then `make cohort N=1 SEED=<n>` and `make cohort`, each reverted): the door is found 11 ft out, but `door_off_fixtures` must stand it `FOOTPATH_FABRIC_GAP + 1` = 8 ft clear of the farm's own fixtures and grove bands, finds no spot, and the farm gets no path at all; with the door's step (8 ft) and its clearance off its own fixtures (5 ft) held at their own values and the fence gap at 7 ft, seeds 3, 4, 903 and 904 pass and the cohort passes 16 of 16.
5. **The order.** Why seed 4's way from its door is refused at 7 ft (the refused route's own reason), then the route that answers it, then the four seeds and the cohort at 7 ft.
6. **The exits.** (a) refine an O number: T43 item 1's 3 ft is a tread-to-wall figure, not a fence figure - weighed there; (b) an exception: none named - nothing obstructs yet; (c) a new rule: the own-fence allowance 0246 attests - a household's own way held 7 ft off others' fences only; (d) more room: wider spacing between the linear form's farms, where (c) leaves a seed failing; (e) conform: the 4 ft kept, labeled UNRESEARCHED with this trial, only where (c) and (d) both fail.
7. **The search smell.** None - a cause found, then one route.
8. **The budget.** 3 h.
9. **Done, measured.** One goal: `FOOTPATH_FABRIC_GAP` at 7 ft with the four seeds and the cohort passing, T31's 4 ft block taken out of 0246, and the claims checked IN-STEP; or, failing (c) and (d), the 4 ft relabeled UNRESEARCHED with both trials as its trail.
10. **Before moving a constant.** `FOOTPATH_FABRIC_GAP` is read in `ways/track.py`, `ways/web.py`, `ways/bund.py`, `ways/serve.py` and `homesteads/row_rules.py` (measured 2026-10-19, a grep); `DOOR_ROOM_FT` and `FOOTPATH_DOOR_OUT_FT` are written from it by hand and move with it.
11. **Before fitting things into room.** A footpath past others' fences: 7 + 1.5 + 1.5 + 7 = 17 ft between two fences; the nucleated form's growth gap is `MIN_WEB_GAP` (18 ft) already.

### T96 Decisions

**D118 - the household's own ground, not the fence gap (route (c), measured).** `FOOTPATH_FABRIC_GAP` becomes 0246's 7 ft. The
door's numbers, which only ever measured the household's own dooryard, stop reading the fence gap: a new `DOOR_STEP_FT` (8 ft, the
door's step past its yard, `front_door`'s offset) and `DOOR_FIXTURE_CLEAR_FT` (5 ft, the door kept off the farm's own fixtures and
grove bands, `door_off_fixtures`) - both UNRESEARCHED, as the claim on `lay_door_paths` already labels them - in `serve.py`, `web.py`
and `row_rules.py`; `rows.FOOTPATH_DOOR_OUT_FT` is derived from `DOOR_STEP_FT` (derive, never pin) and `DOOR_ROOM_FT`'s docstring
names the door's step, not the footpath's gap. T31's 4 ft block comes out of 0246, and `FOOTPATH_FABRIC_GAP`'s claim cites 0246's
7 ft. No house moves: route (d) is not needed, and (e) is not reached. T43's item 3 (`span_walkable` and a household's own garden)
stays T43's.


### T96 part B (2026-10-19T07:32Z)

Owed by the landing cohort of 07:15Z (cohort seed 22 newly failing) and the round arbiter's ruling on hour:385-approach-checklist@29
(continue).

1. **What is refusing?** At 7 ft, cohort seed 22 (linear) leaves two farms unreached: their doors stand, but no door path is lawful
   - measured 2026-10-19 (a scratch probe logging `door_path`).
2. **A3 again.** Unchanged.
3. **A4 again.** The trace names the cause: the door path's room off a grove is counted twice (bands grown 11 ft, then routed at the
   gap on top), a drift T96's claims round had already found.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither in this part B: the fix is T98's, decided and reviewed, and lands with T96.
6. **The one-sentence test.** "Seed 22 fails because 0036's room is counted twice" - true by the trace; with it counted once seed 22 passes.
7. **The next step is a measurement.** The landing cohort with T96 and T98 together.
8. **Every route measured before offering one?** Yes: the band margin was traced as the cause before T98 was written; room (d) waits if T98 does not settle it, as the ruling says.
9. **After a ruling: the step it names?** Yes - the ruling says go on with T98's review and landing.
<!-- plan-archive: T98 to T96 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T103 to T98 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T104 to T98 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T100 - web lanes off the water cite 0035's drawing page (found working T96, 2026-10-19)

### T100 Approach (checklist part A)

1. **The goal, in the world.** The claim on how the web keeps off the water names the page that sets it.
2. **The constraints.** 0035's drawing page: "The ways between the two banks cross the brook squarely, on a plank bridge"; "A way keeps to its own bank unless crossing saves it more than about 150 ft of walking"; crossing places "every 160 ft or so along the brook". Feature 316: a claim cites the page that answers it. A claims check IN-STEP.
3. **Where each comes from.** 0035's drawing page (O); 316 (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (T96's impl-drift round on `web.stage_web#web lanes off the water`: MISLABELED, "UNRESEARCHED, but 0035's drawing page answers it", then a read of 0035): the web's cuts and joins are clipped at the watercourses and drawn channels, and a join crosses the brook only at a ford - 0035's crossing places (`FORD_SPACING`, 160 ft).
5. **The order.** The claim's text, then its claims check.
6. **The exits.** (e) conform - the code keeps 0035's rule; only its citation is wrong.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: the claim cites 0035's drawing page and the claims check finds it IN-STEP; no code changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T100 Decisions

**D122 - the web's water rule is 0035's.** `stage_web`'s claim reads "web lanes off the water - <0035's drawing page>: a way keeps to its own bank; web cuts and joins clipped at the watercourses and drawn channels, a join crossing the brook only at a ford, one of the crossing places".


### T100 part B (2026-10-19T09:02Z)

Owed by the round arbiter's ruling on hour:385-approach-checklist@30 (continue), taken while T100 was the active task.

1. **What is refusing?** Nothing in T100: its plan is CLEAR and its claim's triage is next.
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither.
6. **The one-sentence test.** "The web's water claim cites 0035" - true once the claims check finds it IN-STEP.
7. **The next step is a measurement.** The claim's triage, then its check.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - the ruling says land T104, then do T100.
<!-- plan-archive: T105 to T100 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T99 to T96 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T97 to T96 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T101 to T96 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T107 to T101 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T109 to T107 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T110 to T107 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T113 to T110 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T102 - the dry exit crosses at the crossing places (found working T98, 2026-10-19)

### T102 Approach (checklist part A)

1. **The goal, in the world.** Where every bearing out of a settlement is wet, the track out crosses its brook at a crossing place, as 0035 has a way do.
2. **The constraints.** 0035's drawing page: the ways between the two banks cross the brook squarely, on a plank bridge; a way keeps to its own bank unless crossing saves it more than about 150 ft of walking (a GUESS there); the maps set a crossing place every 160 ft or so. The rule of the record: every rendering decision is labeled, and a deliberate deviation is recorded in `research/` and at the point of change. A claims check IN-STEP.
3. **Where each comes from.** 0035's drawing page (O); the root CLAUDE.md's research rules (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (T98's claims round, `track.connector_dry_exit#brook not crossed` DRIFTED, then a read of `track.py`): the track's own router crosses the brook only at a ford at 0035's 150 ft (`set_crossing`, `BROOK_CROSSING_COST_FT`); its last resort, the flood fill `connector_dry_exit` runs where every bearing of the sweep is wet, treats every water line as a wall, so it never crosses.
5. **The order.** The fill's water lines gapped at the crossing places; its claim; the test; the cohort.
6. **The exits.** (b) a principled exception - refused by the plan review (round 1): a crossing place exists when the fill runs, so the reason was the algorithm's order, not how a track forms; (c) a new rule - chosen: the fill passes the brook within `FORD_HALF` of a crossing place (`brook_fords`), as the track's own checks gap it; (e) conform as the claim stood - refused: the claim said no water is crossed as if 0035 said so.
7. **The search smell.** None.
8. **The budget.** 40 min with its checks.
9. **Done, measured.** One goal: `connector_dry_exit` passes the brook within `FORD_HALF` of a crossing place and nowhere else; its claim cites 0035's crossing places and is IN-STEP; a test red without it; the cohort passes - measured 2026-10-19 (`make cohort` with it built: 16 of 16).
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T102 Decisions

**D131 - the last resort crosses where 0035 would.** `connector_dry_exit` runs its fill twice: as it was, the water lines walls,
and open within `FORD_HALF` of each crossing place `brook_fords` sets along the brook (every `FORD_SPACING`); it takes the open
fill's way where the own-bank fill finds none, or where the own-bank way is longer by more than `BROOK_CROSSING_COST_FT` (0035's
150 ft) - a way keeps to its own bank unless crossing saves it about 150 ft (measured 2026-10-19: T102's claims round found the
open fill alone crossed for free, DRIFTED; built so, the cohort passes 16 of 16). The claim reads "brook crossed at its crossing
places - <0035's drawing page>: the fill keeps to its own bank unless crossing at a crossing place finds a way it otherwise has
not, or saves more than `BROOK_CROSSING_COST_FT` of walk". No page edit.



### T102 part B (2026-10-19T12:35Z)

Owed by the round arbiter's ruling on hour:385-approach-checklist@33 (continue), taken while T102 was the active task.

1. **What is refusing?** Nothing: the crossing's charge was decided as D131, reviewed and built; the claims are IN-STEP.
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither in this part B: the change is D131's, decided and reviewed.
6. **The one-sentence test.** "The last resort crosses its brook where 0035 would" - true by the claims check and the cohort.
7. **The next step is a measurement.** The gate and the landing cohort, both run.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - the ruling says carry on with T102, then T106, T108, T111, T112.
<!-- plan-archive: T115 to T115 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T116 - a code change owes a triage first (amendment 10, the GM 2026-10-19)

### T116 Approach (checklist part A)

1. **The goal, in the world.** A change to a function sends to impl-drift only the claims it bears on, not every claim the function carries.
2. **The constraints.** Amendment 10, the GM: "I would also like to implement all 3 of your suggestions" - the first, "re-check only the claim lines a change touched". Feature 318's FR-016 and its triage (a page edit owes its claims a triage of the changed blocks; only the claims it names go on). Feature 316: a verdict is recorded at the fingerprints its bundle read. The 1,000-line bar. A test red without it.
3. **Where each comes from.** The GM (G); 318, 316 (O); the bar (G, 2026-08-31).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (T97's claims rounds: an edit to `web.stage_web` re-owed its 20 claims, 17 of them IN-STEP and unaffected; `make where-time F=385 BY=tick`: T97 53 min, 4 claims rounds among them; `claims.owed` names every claim of a unit whose code fingerprint moved "code changed"); `claims.py` stands at 1,000 lines.
5. **The order.** The owed logic moved to its own module (the bar); `owed` sending a many-claim unit's code change to a triage; the triage bundle showing the unit's diff against origin/main; the record clearing the untouched claims at their new code; the tests.
6. **The exits.** (c) - a code triage, as the page edit has, reusing the `claims-triage` agent; a static match of names in the diff against the claims was weighed and refused (a change can bear on a claim whose names it never touches).
7. **The search smell.** None.
8. **The budget.** 90 min.
9. **Done, measured.** One goal: a code change to a unit owes its claims a `code triage` - a bundle of the unit's diff hunks against origin/main and its claims - whose named claims go on to impl-drift and the rest are recorded at their new code; a new claim, a claim the triage named, or a unit with no diff to show goes to impl-drift as now; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves or is added in this task (a minimum claim count was weighed and dropped: the plan review of round 1 found its cost claim unmeasured, and the page triage it copies has none).
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T116 Decisions

**D133 - a code change triaged first.** `owed` marks a "code changed" claim "code triage", owed only a triage (`TRIAGED`), as a page edit's claims are - whatever the number of claims its unit carries; a claim the triage has named (`touched`) goes to impl-drift as now. The triage bundle shows, per such unit, the hunks of `git diff origin/main -- <file>` that overlap the unit's lines and its claims with their last verdicts; a unit with no hunk to show is owed in full (`forced`). `make claims-triaged` clears an untouched claim at its new code and core fingerprints, as it clears a page's at its new pages.

**D134 - the owed logic in its own module.** `owed`, `research_why`, `relabeled_only` and their helpers move from `claims.py` to `claims_owed.py`, re-exported by `claims.py`, so the bar holds.

### T116 part B (2026-10-19T13:06Z)

Owed by the round arbiter's ruling on hour:385-approach-checklist@34 (continue), taken while T116 was the active task.

1. **What is refusing?** Nothing: D133 and D134 were decided, reviewed CLEAR in round 2 and built; the tooling landed.
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither in this part B: the change is D133's, decided and reviewed.
6. **The one-sentence test.** "A code change re-checks only the claims its hunks bear on" - true by `tests/tooling/test_claims_scoping.py`, red without the code section.
7. **The next step is a measurement.** The claims tests, run whole, and the landing.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - the ruling says go on with the tooling round, T117 to T119.

<!-- plan-archive: T117 to T117 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T118 to T118 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T119 to T119 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T114 to T102 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T121 to T117 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T122 - a conflict with the clone's own landing is named, with its fix (found working T119, 2026-10-19)

### T122 Approach (checklist part A)

1. **The goal, in the world.** When a landing refuses because main conflicts with what this clone itself landed, the refusal names those files and the one line that resolves them.
2. **The constraints.** The round arbiter's ruling on hour:385-approach-checklist@35 (change-route): "T122 narrows to a message" - no resolver; name each conflicting file whose main-side commit is this clone's own land-tooling commit and print the line to keep the clone's side; the session resolves by hand, about a minute. Feature 385 D46: the clone merges main only when the patch fails to apply, and a conflicting merge is aborted and refused (unchanged). A test red without it.
3. **Where each comes from.** The round arbiter (O, binding); D46 (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (T119's second landing, 13:40-13:42): a new file landed, then edited, conflicted add/add with main's own land-tooling commit of it; the refusal said only "merging main into the clone conflicts - run scripts/sync-with-main.sh sync-in, resolve the conflict", and resolving it by hand took about 2 minutes.
5. **The order.** Before the abort, the conflicted files read and each one's last main commit checked against this clone's land-tooling subject; the refusal names them and the line; the suite case.
6. **The exits.** (c) - name and instruct; a resolver taking the clone's side was built and withdrawn (the arbiter: a rule around a sub-bar hazard, its reach the risk round 2 found).
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: when D46's merge conflicts, the refusal lists each conflicted file whose last commit on origin/main is this clone's own `Tooling from <clone>, landed alone mid-feature` commit, with `git checkout --ours <files> && git add <files> && git commit --no-edit` after `scripts/sync-with-main.sh sync-in`; other conflicts are refused as now; `tests/hooks/test-land-tooling.sh` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T122 part B (2026-10-19T14:30Z)

Owed by the round arbiter's ruling on hour:385-approach-checklist@35 (change-route), taken while T122 was the active task.

1. **What is refusing?** Nothing now: the ruling narrowed T122 to a refusal message; the resolver was withdrawn and round 3 stopped.
2. **A3 again.** Changed: the arbiter's ruling is now the binding constraint, written into item 2.
3. **A4 again.** Unchanged: the hand resolution measured about 2 minutes.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither in this part B: the change is D144's as rewritten by the ruling, decided and reviewed CLEAR.
6. **The one-sentence test.** "A conflict with the clone's own landing is named with the line that resolves it" - true by the suite's case 2a.
7. **The next step is a measurement.** The suite, run whole: 49/49.
8. **Every route measured before offering one?** No route is offered; the ruling's was taken.
9. **After a ruling: the step it names?** Yes - narrowed to a message, one plan review, the resolver discarded.

### T122 Decisions

**D144 - the self-landed conflict named.** In `land-tooling.sh`'s D46 branch, before `git merge --abort`, the conflicted files (`git diff --name-only --diff-filter=U`) whose `git log -1 --format=%s origin/main -- <file>` begins `Tooling from <this clone's name>,` are named in the refusal: "<files> conflict only with this clone's own earlier landing - run scripts/sync-with-main.sh sync-in, then git checkout --ours <files> && git add <files> && git commit --no-edit, then land again". The merge is aborted and the landing refused as now; nothing is resolved by the tool.

<!-- plan-archive: T123 to T114 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T106 to T97 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T108 - the yard's 7 ft claimed apart from the garden's (carried by the claims gate, FR-013)

### T108 Approach (checklist part A)

1. **The goal, in the world.** The two claims of the 7 ft foul margin say which half 0246 sets and which half no page sets.
2. **The constraints.** 0246's drawing page sets the 7 ft gap only from another household's garden fence; `law.span_walkable#a span off a threshing yard` already labels the yard's 7 ft UNRESEARCHED ("no page sets a gap from a yard"). Every rendering decision labeled. The claims check.
3. **Where each comes from.** 0246's drawing page (O); the sibling claim (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the claims index: `law.fouls_fabric#foul margin` and `settle.fouled_segment#off another household's yard or garden` NEEDS-RESEARCH, each "the yard part should be UNRESEARCHED, as span_walkable's claim already says").
5. **The order.** Each claim split in two, its garden half on 0246, its yard half UNRESEARCHED; the claims check.
6. **The exits.** (e) conform the claims to the page and to their sibling; a research pass for a yard gap was weighed and refused here (the sibling has stood UNRESEARCHED; a pass is the open-questions list's to run).
7. **The search smell.** None.
8. **The budget.** 15 min.
9. **Done, measured.** One goal: the two claims each split into a garden half citing 0246 and a yard half UNRESEARCHED; the claims check IN-STEP; no engine token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T108 Decisions

**Wording only.** Two claims split by what their pages set: `law.fouls_fabric#foul margin` and `settle.fouled_segment#off another household's yard or garden` each keep their garden half on 0246 and gain a yard half labeled UNRESEARCHED, in the sibling's words.

## T130 - the run-on reach labeled as the guess it is (impl-drift, T106's round)

### T130 Approach (checklist part A)

1. **The goal, in the world.** The run-on reach's claim cites no page for a figure no page gives.
2. **The constraints.** 0246's drawing page gives 60 ft only as the reach to a house or another way; 0014 says the nearest lane "runs on to the bund", with no distance. Every rendering decision labeled; a GUESS names its source only where one exists. The claims check.
3. **Where each comes from.** 0246, 0014 (O); the root CLAUDE.md's research rules (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (T106's claims round: `bund.RUN_ON_REACH_FT#run-on reach` MISLABELED, "The label should be GUESS with no page named").
5. **The order.** The claim relabeled; the claims check.
6. **The exits.** (e) conform the label to the pages.
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: the claim reads GUESS, naming 0246's 60 ft as the reach it reuses and no page as its source; the claims check IN-STEP; no engine token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T130 Decisions

**Wording only.** `bund.RUN_ON_REACH_FT#run-on reach` reads "GUESS: an end within 60 ft of the field is carried on to it - the reach 0246 gives to a house or a way (`WAY_END_REACH_FT`), reused for the field; no page gives a distance to the field".

## T136 - bund.py's turn limit labeled a convention, its sampling step claimed (impl-drift, T130's round)

### T136 Approach (checklist part A)

1. **The goal, in the world.** Two constants of `bund.py` say truly what they rest on.
2. **The constraints.** 0081's drawing page: "A lane run on to a bund turns no more than 60 degrees anywhere" and "The limits above are drawing conventions ... chosen at the scale of a dozen paces, not measured". Every unit carries a claim; plumbing is claimed NONE. The claims check.
3. **Where each comes from.** 0081's drawing page (O); feature 316 (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (T130's claims round: `RUN_ON_TURN_DEG`'s comment calls it a map drawing convention while its claim reads as a finding; `BRANCH_STEP_FT` carries no claim; then a read of 0081's page).
5. **The order.** The turn limit's claim labeled CONVENTION; the step claimed NONE; the claims check.
6. **The exits.** (e) conform the labels to the page.
7. **The search smell.** None.
8. **The budget.** 10 min.
9. **Done, measured.** One goal: `RUN_ON_TURN_DEG`'s claim reads CONVENTION citing 0081, `BRANCH_STEP_FT` carries a NONE claim; the claims check IN-STEP; no engine token changes.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T136 Decisions

**Wording only.** `RUN_ON_TURN_DEG`'s claim becomes "run-on turn limit - CONVENTION research/questions/0081-village-lanes.drawing.html: a lane run on to a bund turns no more than 60 degrees anywhere - the page's turn limits are drawing conventions"; `BRANCH_STEP_FT` gains "Research: branch sampling step - NONE: how often the nearest lane is sampled for a field path's branch".

<!-- plan-archive: T132 to T106 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
<!-- plan-archive: T125 to T106 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T137 - a malformed claim never lands by either route (found by the T132+T125 gate, 2026-10-19)

### T137 Approach (checklist part A)

1. **The goal, in the world.** A claim written in a form the claims tooling cannot read is refused before it lands, whichever route lands it.
2. **The constraints.** Feature 316: every unit in scope carries a claim in the claims grammar (`tools/claims.GRAMMAR`, `coverage`), held by `tests/tooling/test_claims_coverage.py` at the gate; the claims gate (`scripts/gates/claims-gate.sh`, `claims.py gate`) runs on both routes. The round arbiter's fix bar (amendment 10): a defect that reached main. A test red without it.
3. **Where each comes from.** 316 (O); the root CLAUDE.md's session-clone rules (O); the GM (G).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the T132+T125 gate, red in test-full on `test_every_unit_in_scope_carries_a_claim`): T136 landed `RUN_ON_TURN_DEG`'s claim as "CONVENTION <page>" - "`CONVENTION` takes no pointer" - by `sync-with-main.sh done`'s direct route (a docstring-only change, no gate), and the claims check had judged it IN-STEP, owing no form check.
5. **The order.** The claim corrected to a plain citation of the drawing page; `claims.py gate` refusing a `coverage` problem in a file the delta changed; the test.
6. **The exits.** (c) - the form check where both routes already pass; running the whole coverage test on the direct route was weighed and refused (the gate's own test does that; the push needs only the delta's files).
7. **The search smell.** None.
8. **The budget.** 30 min, landing with T132 and T125 by `make land-batch`.
9. **Done, measured.** One goal: `make claims-gate` refuses when a file changed since origin/main carries a claim `coverage` reports, naming it and the grammar; the corrected claim passes; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T137 part B (2026-10-19T15:28Z)

Owed by the round arbiter's ruling on hour:385-approach-checklist@36 (continue), taken while T137 was the active task.

1. **What is refusing?** Nothing now: the gate's red was the malformed claim, corrected.
2. **A3 again.** Unchanged.
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither in this part B: the change is D149's, decided and reviewed; the ruling's fix - reuse `form_problems`, no second check - is how D149 was built.
6. **The one-sentence test.** "A malformed claim in a changed file is refused at the push" - true by `test_the_gate_refuses_a_claim_the_grammar_cannot_read_in_a_changed_file`.
7. **The next step is a measurement.** The claims check, the gate and the landing cohort of the batch.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - T137, then the T132+T125 batch.

### T137 Decisions

**D149 - the form refused at the push.** `RUN_ON_TURN_DEG`'s claim cites 0081's drawing page plainly ("... - the page records its turn limits as drawing conventions"). `claims.py gate` adds to its refusals each `coverage` problem whose file is in `git diff --name-only origin/main...HEAD`: "<problem> - the claims grammar: <GRAMMAR>". No escape: a form is fixed, never carried.

<!-- plan-archive: T139 to T132 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->
## T43 - three findings carried at T07's landing, settled since (the round arbiter, ask:t07-two-findings-at-landing)

### T43 Approach (checklist part A)

1. **The goal, in the world.** The three findings carried at T07's landing are each fixed or re-checked clean before 385 closes (FR-013).
2. **The constraints.** FR-013: a carried finding is fixed or re-checked clean. The round arbiter's rulings on ask:t07-two-findings-at-landing and ask:t07-span-walkable-cannot-tell.
3. **Where each comes from.** FR-013, the rulings (O).
4. **Do they describe the world here?** No longer - measured 2026-10-19 (the claims index and the tree): (1) `houses._on_a_tread#a building's corners held to it` IN-STEP since 2026-10-18 (T96 and T101's work on the footpath's and the lane's room); (2) `settlement/rolling/roll.py` no longer exists - feature 388 retired `roll_village`, `_roll_cluster` with it; (3) `law.span_walkable#a walkable span` IN-STEP since 2026-10-19.
5. **The order.** Each finding read against the index and the tree; nothing to change.
6. **The exits.** (e) conform: the record already says what each now is.
7. **The search smell.** None.
8. **The budget.** 5 min.
9. **Done, measured.** One goal: each of the three stands IN-STEP or retired, read from the claims index and the tree; no file changes but this section.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T43 Decisions

**Wording only.** Nothing changes: the three carried findings were settled by T96, T101 and feature 388, each re-checked clean or removed.

## T32 - a weld that would leave a lump goes to the next host, recorded (ranking row: waterfields/banks.py _WELD_MIN_SOLIDITY, E2 DRIFTED)

### T32 Approach (checklist part A)

1. **The goal, in the world.** 0014's drawing page says where a paddy scrap too thin to stand alone is welded, including the case where the neighbor it shares most bund with would be left lumpy, and the claim cites that.
2. **The constraints.** FR-020: a ranking row of a kind not yet tried - E2, one rule (T06 a form, T07 research, T08 and T10 knobs, T09 a value, T31 a mislabel). 0014's drawing page: "It goes to the paddy it shares the most bund with, so the two walls become one." The ranking's fix: "drop the 0.85-solidity host preference". The finding (impl-drift): "the 0.85-solidity exception is not recorded there as a deviation - record it on the page or drop DEVIATION". The code's own record: the preference answers a defect settlement-review found on Sawada and Mizuguchi (2026-08-17) - a scrap handed to the lumpiest basin made bund prongs 5-11 ft wide with a free end, "a wall that goes out eleven feet and comes straight back retains water on neither side and costs a full share of azenuri"; 0.85 is the gap between the 18 clean welds (>= 0.90) and the two lumps (0.731, 0.78); it is a preference, never a veto. Every deviation recorded on the drawing page with its reason. Record checks and the claims check.
3. **Where each comes from.** FR-020 (G, amendment 7); 0014's drawing page (O); the ranking (O); the reviewer's finding and its measurement (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the claims index: `banks._WELD_MIN_SOLIDITY#weld lump` DRIFTED, its note as above; the code's comment block and 0014's page read): the rule the code runs is 0014's except where the best-sharing host would fall under 0.85 solidity and a clean host exists, and 0014 does not record that exception.
5. **The order.** The exception recorded on 0014's drawing page as a DEVIATION with its reason; the claim cites it; the record checks and the claims check.
6. **The exits.** (a) refine an O number: n/a - 0014 gives no number to refine; (b) a principled exception - chosen: a weld that makes a free-ended prong is a construction error 0014's own purpose (two walls become one) does not intend; the next-best host keeps the walls joined; (c) a new rule: n/a; (d) more room: n/a - nothing is packed; (e) conform as the ranking's fix says - refused: dropping the preference restores the free-ended prongs settlement-review found.
7. **The search smell.** None.
8. **The budget.** 40 min with its checks.
9. **Done, measured.** One goal: 0014's drawing page records the exception as a DEVIATION with its reason; the claim cites it; record checks and claims check pass; no engine token changes.
10. **Before moving a constant.** n/a - `_WELD_MIN_SOLIDITY` stays 0.85, its measurement on record in the code.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T32 Decisions

**D151 - the next host where the best would lump.** 0014's drawing page gains, after its weld block: "<li><strong>A strip is not joined where it would leave its neighbor lumpy.</strong><br>Where the paddy it shares the most bund with would be left with a lobe - a wall run out and straight back, which holds water on neither side - it goes to the next neighbor it shares bund with instead, and only where every neighbor would be left so does it go to the least lumpy. A DEVIATION from the rule above: a wall that holds no water is a construction error, and the two walls still become one.</li>". The claim reads "weld lump - DEVIATION research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a scrap goes to the basin it shares the most bund with unless that leaves the host under 0.85 solidity and a clean host exists".

## T11 - the close

The checklist to `docs/`, the refusals extended to every feature's tasks (FR-001), the final report (SC-001, SC-002).
