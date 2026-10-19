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

**Lands open**: T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T46, T66, T67, T68, T69, T70, T71, T72, T74, T75, T76, T77, T78, T79, T80, T81, T82, T83, T84, T85, T86, T87, T88, T89, T90, T91

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
## T91 - a landing's lint runs in the foreground (the round arbiter's fix on hour:385-approach-checklist@27)

### T91 Approach (checklist part A)

1. **The goal, in the world.** A lint slip in the files a landing carries is known in seconds, before the landing starts.
2. **The constraints.** The arbiter's fix: "make land-tooling should run its own lint stage (the same ruff check and format check the landing applies) in the foreground on the files it carries, and refuse before it goes to the background, so a lint failure shows in seconds rather than at the next tick or set-down". The landing's own lint (T52, T55, T67) stays. A test red without it.
3. **Where each comes from.** The fix is the arbiter's (G); the landing's lint is T52's (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the hour-27 bundle and the land-t85 logs): T85 was landed three times; two failures were lint (a format, a stray `f` prefix), each seen only when the backgrounded landing's log was read minutes later.
5. **The order.** The check in the make-only guard's Bash path (it already reads `make` commands), then its suite case.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 25 min.
9. **Done, measured.** One goal: a `make land-tooling FILES="..."` command whose Python files fail `ruff check --force-exclude` or `ruff format --check --force-exclude` is refused before it runs, naming the files and the `ruff format` command, whether or not it is run in the background; `tests/hooks/test-make-only-hooks.sh` red without it.
10. **Before moving a constant.** n/a - none moves.
11. **Before fitting things into room.** n/a - nothing is fitted.

### T91 Decisions

**D112 - the landing's lint, before the landing.** `make-only-hooks.sh`, for a Bash command invoking `make land-tooling` with `FILES=`, runs the landing's own lint (`ruff check --force-exclude` and `ruff format --check --force-exclude`, in the command's working tree) on the `.py` files named; a failure refuses the command with ruff's first lines and `python3 -m ruff format <files>`. No `.py` file named, or ruff absent: nothing is refused.

## T11 - the close

The checklist to `docs/`, the refusals extended to every feature's tasks (FR-001), the final report (SC-001, SC-002).
