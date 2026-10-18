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

**Lands open**: T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T46

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
## T42 - an absence note owes no source-reader (the round arbiter's fix on round:source-reader|q:0081@5)

### T42 Approach (checklist part A)

1. **The goal, in the world.** A source-reader round is owed only where there is a page to read.
2. **The constraints.** The arbiter's fix (three parts: "stop owing a source-reader round when a 'no publicly readable source'
   (absence) note's wording changes, since there is no page to read; take a READ on the sibling note it defers to as settling it,
   and net out of the owed list any note that the latest returned round READ with no edit since"); the record's other checks on an
   absence note unchanged (its quote-check, the page's record-format); a test red without it; tooling only.
3. **Where each comes from.** The fix is the arbiter's (G).
4. **Do they describe the world here?** Yes - measured on T07's check session (2026-10-18, the ruling on q:0081@5): the round-6
   source-reader came back 9 READ, 0 CONTRADICTED, yet five notes stood owed - two absence notes re-worded to defer to the
   2.2-chi figure, and three notes round 6 had READ with no edit since.
5. **The order.** The absence rule, then its tests.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: no source-reader unit is owed on an absence note, new or changed; a note READ at its current words
   is not owed; `tests/tooling/test_record_owed.py` red without it.

### T42 Decisions

**D57 - the three parts.** (a) `record_units.owed` owes no `source-reader` unit on a note whose words carry "no publicly readable
source" (`ABSENCE`), new or changed; its quote-check and the page's record-format are owed as before. (b) What such a note defers
to is its sibling notes' own reading - each is owed and read on its own words, so a READ on the sibling settles the absence note's
content with no unit of its own. (c) A note the latest returned round READ, unchanged since, is answered at its fingerprint (the
existing `answered` rule, `record_owed.py`). Measured 2026-10-18 on HEAD (`.git/record-checks/`, then `make record-owed
UNANSWERED=1`): the three notes the ruling found owed - 0081.drawing#wang-2021-qing-huabei-dishui-2, 0247#...-6 and -7 - each carry
round 6's own answer ("9 READ, 0 CONTRADICTED", recorded 14:17:55Z) at its current fingerprint, and none is unanswered: they stood
owed in the ruling's bundle only because round 6's answers were not yet recorded when it was built. So the netting is the existing
rule; `test_a_note_read_at_its_words_is_netted_and_an_absence_note_owes_no_reading` reproduces the q:0081 case (a READ note
netted, a re-worded absence note owing no reading - red without (a)).

<!-- plan-archive: T27 to T22 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
### T44 Decisions

**D58 - every session of the hour.** `stepback_bundle.sessions_of` lists every `sid` with events in the window, busiest first.
Without `--transcript`, `build` reads each one's transcript (`transcript_of`) and merges their records by timestamp, each tagged
with its session. `words.md` labels each entry with the session's first 8 characters when the hour has more than one, keeps the
newest over the cap (the existing shrink, then the cut, whose notice stays), and opens with the sessions it read and any whose
transcript it did not find ("left out"). `refusals.md` takes every session's refusals. `time.md` sums over the sessions read and
says so, since parallel sessions can sum past the hour. With `--transcript` (a replay) the one transcript is read as before.

<!-- plan-archive: T28 to T29 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
## T10 - a dike-pond village's water and dike split, rolled (the ranking row `settlement/fields/landuse.py::DIKEPOND_WATER_INSET#pond bank width`)

### T10 Approach (checklist part A)

1. **The goal, in the world.** A dike-pond village's ponds and banks stand in one of the splits the record gives, rolled per
   village, rather than every map in the one water-heavy split.
2. **The constraints.** The ranking row ("roll the dike-pond inset per village between the recorded splits (water-heavy,
   dike-heavy, 7:3)"); several attested forms are a knob rolled from the seed (CLAUDE.md); 0018's drawing page ("the split would
   be rolled village by village; our maps draw only the water-heavy order, so the dike-heavy order and the seven-to-three split
   are a known gap"); the mulberry rows, the banks' sties and the bank's lit ring all read the same inset; no known regression.
3. **Where each comes from.** The three splits are 0018's (R: six parts water to four of dike, six of dike to four of pond, seven of
   water to three of dike - each written as a number only in modern sources, as the page says); the even odds ours (GUESS); 23 ft is
   the water-heavy split's calibration on Kuwabata's parcels (O, labeled so).
4. **Do they describe the world here?** To be measured: the water share each inset leaves on the pool's dike-pond map (Kuwabata)
   and on the cohort's dike-pond seeds.
5. **The order.** The knob and its roll; the inset derived from the rolled share on the map's own parcels; every reader of the
   inset given the map's value; the drawing page's known-gap sentence brought up to the knob; tests, pool, cohort, glyph check.
6. **The exits.** (a) the 23 ft is ours and becomes the derived inset; (b)-(e) n/a.
7. **The search smell.** None - the record already holds the three splits.
8. **The budget.** 3 hours.
9. **Done, measured.** One goal: a dike-pond map's parcels are drawn at its rolled split's water share (within a few points,
   measured on its parcels), the split recorded in the manifest, all three splits coming up across seeds.

### T10 Approach (re-answered 2026-10-18T20:09Z)

Owed by D74b (all five recorded splits).

1. **The goal, in the world.** Unchanged: a dike-pond village's ponds and banks stand in one of the splits the record gives - now
   all five it gives.
2. **The constraints.** Part A's, and the knob rule: every attested form is rolled, so the ranking row's three are widened to
   0018's five (D74b).
3. **Where each comes from.** The five splits 0018's (R); the even odds, the one inset per village ours (GUESS).
4. **Do they describe the world here?** Measured: on Kuwabata (rolled 0.7) the median parcel draws 0.700 water, the parcels 0.56 to
   0.80; pool clean, cohort 54/54 at three splits.
5. **The order.** The two splits added, their pop-ups; 0018's drawing page, the stale "23 ft" and "six in ten" text elsewhere and
   the bank-width finding (the hour-21 ruling's guidance) in a page session; the claims; the pool, the cohort and the gate.
6. **The exits.** Unchanged.
7. **The search smell.** None.
8. **The budget.** 2 more hours.
9. **Done, measured.** Unchanged, at five splits.

### T10 part B (2026-10-18T20:09Z)

Owed by the hour-21 step-back (hour:385-approach-checklist@21, `continue`).

1. **What is refusing?** Nothing on the maps. The record check found two recorded splits not rolled (fixed, D74b) and text
   elsewhere still saying 23 ft and six in ten; the ruling asks that T10 close those, and settle the bank-width finding from 0018 and
   0027 before it goes to the GM.
2. **A3 again.** Unchanged, plus the two splits (R).
3. **A4 again.** Measured on Kuwabata: the derived inset leaves the median parcel at its share.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Changing: the roll widened to the record.
6. **The one-sentence test.** "A dike-pond village takes one of the five recorded splits, rolled" - true by the knob and its test.
7. **The next step is a measurement.** The page session's checks, then the claims.
8. **Routes measured before asking?** n/a - no ask.
9. **After a ruling.** `continue`, with its guidance taken into the page session; its tooling fix is its own task.

### T10 Decisions

**D74 - the split rolled, the inset derived.** The recorded splits as the water share of a parcel (three at first; all five since D74b), rolled per map
from its seed as a settlement knob (`dikepond_split`, a hamlet spec may pin it), even odds (GUESS). The inset is derived ONCE per map
from the rolled share on the map's median parcel - the depth `d` at which an inset of the parcel's area `A` and perimeter `P` leaves
that share water (`4d^2 - P d + (1 - f) A = 0`, the rectangle's law) - and stored on the settlement, so the pond's water outline,
the mulberry rows between bank and water, and the sties' bank seat (`pondstock.BANK_INSET_FT`, half the inset) all read the one
value. `DIKEPOND_WATER_INSET` (23 ft) stays as the water-heavy split's value on Kuwabata, labeled so, the fallback where no parcel
is known. The drawing page's known-gap sentence becomes the knob's (a page session).

**D74b - all five recorded splits** (T10's record check, 2026-10-18: "nobody has said why the record's 1:1 and three-to-seven splits
are not rolled"). 0018 records five forms, not the ranking row's three: six of water to four of dike, six of dike to four of pond,
seven of water to three of dike, one to one (a modern working paper, where the mulberry alone feeds the fish), and the Guangdong
gazetteer office's three-to-seven read in the order it names - three parts water to seven of dike. Several attested forms are a
knob, so `dikepond_split` rolls all five water shares (0.6, 0.4, 0.7, 0.5, 0.3), at even odds (GUESS); each has its title-card
pop-up, and 0018's drawing page names all five.

<!-- plan-archive: T30 to T52 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
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
## T59 - a refused dispatch leaves no reading behind (the arbiter's fix on round:modal-form|modal:choice/dikepond_split--0.7@3)

### T59 Approach (checklist part A)

1. **The goal, in the world.** A check dispatch that another hook refuses before any agent runs changes nothing a later dispatch's
   round count reads.
2. **The constraints.** The arbiter's fix: "hm_checks.py's round counter must not count, or keep as a pending round, a modal-form
   dispatch that the wave guard refused (WAVE_OK missing) before any agent ran, so a refused dispatch cannot push a unit to its round
   cap"; T41's rule (a round counted at its reply) unchanged; tooling only; a test red without it.
3. **Where each comes from.** The fix is the arbiter's (G); the round counter is 375's (O), T41's reply rule ours (O).
4. **Do they describe the world here?** Yes - measured 2026-10-18: the pair hook records a dispatch at PreToolUse, and the wave guard
   (a separate hook, run beside it) refused T10's modal-form wave; the refused dispatch's record still marked its units' notes read
   and opened a fresh round (`seen`, `notes_read`, the round's edits reset), so the next real dispatch was no longer a first look
   and was counted - the 0.7 card reached its cap.
5. **The order.** The marks deferred to the launch, then the test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: a dispatch recorded and never launched leaves `seen`, `notes_read` and the round's edits as they
   were, and the next dispatch of the same unit is a first look; `tests/tooling/test_hm_checks.py` red without it.

### T59 Decisions

**D78 - the marks applied at launch.** `hm_checks` keeps, on the pending dispatch record, what its reading WOULD mark (the units'
seen sentences, the notes read, the fresh round's edits reset) and applies it in `launched()`, when an agent id comes back. A
dispatch refused anywhere never launches, so it changes nothing but its own pending record, which expires as before (`_live`) and
counts no round.

## T60 - apply-edits takes a paragraph break and an emptied line (the arbiter's fix on hour:385-approach-checklist@22, part 1)

### T60 Approach (checklist part A)

1. **The goal, in the world.** A check's EDIT that splits a paragraph or empties a line applies as written, with no hand finish.
2. **The constraints.** The arbiter's fix, part 1: "scripts/record/apply_edits.py should apply an EDIT whose replacement is a bare paragraph break, and should drop the line an empty replacement empties instead of leaving a stray blank line, each with its test in tests/tooling/test_apply_edits.py"; every other EDIT applies as before; tooling only; a test red without it.
3. **Where each comes from.** The fix is the arbiter's (G); `apply_edits` is 250's (O).
4. **Do they describe the world here?** Yes - measured 2026-10-18: two hand finishes in T10's check session (the fruit-dike pop-up at 20:28, the perimeter dike at 20:53): an EDIT whose new text is one empty line parsed as no text and deleted the old instead of breaking it; an EDIT emptying a line left the blank line behind.
5. **The order.** The parse, the empty-line drop, then their tests
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: an EDIT whose new text is a lone empty line puts a paragraph break where its old text stood, and an empty replacement that empties its line removes the line; `tests/tooling/test_apply_edits.py` red without each.

### T60 Decisions

**D79 - the empty line kept, the emptied line dropped.** The EDIT pattern keeps what stands between `===` and `>>>`: a block whose new text is exactly one empty line replaces its old text with a paragraph break (`\n\n` inside a line, a blank line between lines); a block whose new text is empty and whose old text was the whole of its line removes that line and its newline. Every other block applies as before.

## T61 - a make call that sets one variable twice is refused (the arbiter's fix on hour:385-approach-checklist@22, part 2)

### T61 Approach (checklist part A)

1. **The goal, in the world.** A make call never silently drops a value it was given.
2. **The constraints.** The arbiter's fix, part 2: "a Bash guard should refuse a make invocation that assigns the same variable twice (e.g. `make quote-verbatim Q=0018 Q=0027`, where make silently keeps the last), naming the quoted-list form Q=\"0018 0027\" or one call per value"; a quoted list and distinct variables pass; tooling only; a test red without it.
3. **Where each comes from.** The fix is the arbiter's (G); the make-only guard is 127's (O).
4. **Do they describe the world here?** Yes - measured 2026-10-18: T10's round-2 check session ran `make ... Q=0018 Q=0027`, make kept 0027, and a record-format pass read a stale 0018 bundle and was thrown away (my brief told it to).
5. **The order.** The verdict in `hm_make.classify`, the refusal in `make-only-hooks.sh`, then the tests
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 30 min.
9. **Done, measured.** One goal: `make x Q=a Q=b` is refused naming `Q="a b"` or one call per value, while `make x Q="a b"` and `make x Q=a R=b` pass; `tests/hooks/test-make-only-hooks.sh` red without it.

### T61 Decisions

**D80 - a doubled assignment refused.** `hm_make.classify` returns `make-dup-var` when one `make` invocation (quotes and heredocs stripped, as the guard strips them) assigns one variable name twice; `make-only-hooks.sh` refuses it with the variable named and the two compliant forms. The escape is the guard's own `GUARD_EDIT_OK`, recorded.

## T62 - a changed constant names the pages still stating its old figure (the arbiter's fix on ask:t10-findings-at-landing)

### T62 Approach (checklist part A)

1. **The goal, in the world.** When a claimed constant's value or claim changes, every drawing page still stating its old figure is named at the change, not found at landing.
2. **The constraints.** The arbiter's fix: "When a claimed constant's value or derivation changes (here DIKEPOND_WATER_INSET going from a fixed 23 ft to a value derived per map by dikepond_inset), the claims check in scripts/record/claims.py should flag every research drawing page that still states the old figure for that unit, so stale pages like 0022/0024/0025 are caught at the edit rather than at landing"; a flag, never a refusal; tooling only; a test red without it.
3. **Where each comes from.** The fix is the arbiter's (G); the claims index is 316's (O).
4. **Do they describe the world here?** Measured 2026-10-18: of the seven drawing pages stating "23 ft", those that also link the constant's cited page (0018) are 0018 itself, 0022, 0025 and 0027 - the stale three among them; 0024 states the split as six in ten and no figure, so a figure search does not find it.
5. **The order.** The flag in `claims-owed`, then its test
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: `make claims-owed` lists, for each claimed constant whose value or claim changed since the merge base, every drawing page that states its old figure as a whole number and links a question its claim cites; `tests/tooling/test_claims_index.py` red without it.

### T62 Decisions

**D81 - the old figure looked for where the constant's research lives.** `claims.py` compares each claimed module-level constant's value and claim line at the merge base and the head; for one that changed, it searches the drawing pages for its OLD value as a whole number (not a digit of a longer one, whatever unit follows it - 23 ft, 19 degrees, 700 feet alike), keeping the pages that link any question the constant's claim cites, and `claims-owed` prints each as `stale figure: <page> states <figure> (<constant> was <old>)`. A flag only: wording elsewhere ("six in ten") is not found, and the claims rounds still read the pages. Measured 2026-10-18 (a grep of its links): 0024 links no question the claim cites, so no link-only rule would have caught it either.

## T63 - make tick archives finished plan sections (the GM 2026-10-18)

### T63 Approach (checklist part A)

1. **The goal, in the world.** A feature's `plan.md` holds only its open work, without anyone remembering to archive it.
2. **The constraints.** The GM, 2026-10-18 (amendment 8): "If you could have run plan archive but then forgot to do it before, then perhaps that should be something that is run automatically when certain actions are taken"; `make plan-archive`'s rule unchanged (every task of a section ticked, its review CLEAR); the archive never moves an open task's section; tooling only; a test red without it.
3. **Where each comes from.** The GM's (G); plan-archive is 375 FR-044 (O).
4. **Do they describe the world here?** Yes - measured 2026-10-18: 385's `plan.md` had grown to 168 KB and 2,054 lines (`wc -c -l`), 54 finished sections never archived (the count `make plan-archive` printed when it moved them); that one run took it to 27 KB.
5. **The order.** The call at the end of a successful tick, then its test
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a tick that finishes a section's last task moves that section to `plan-done.md` and says so; `tests/tooling/test_plan_gate.py` (or the tick's own test) red without it.

### T63 Decisions

**D82 - archived at the tick.** `tick-task.py`, after a tick it made, runs `plan_gate.archive` on the feature and prints the sections it moved; an archive error never refuses the tick (the tick has already been written), it is printed.

## T64 - make task-add (the GM 2026-10-18)

### T64 Approach (checklist part A)

1. **The goal, in the world.** A task is added to a feature with one command that picks its id and places it, with no hand-written insertion.
2. **The constraints.** The GM, 2026-10-18 (amendment 8): "inserting a task somewhere in the middle of the task list. Because as of now, that sounds like something that could potentially eat up a lot of tokens if we are doing it by hand. And hence why it should get tooling"; the box lands before the GM-review box, as `claims-carry` places its boxes; a plan section, when given, lands before the feature's close section; tooling only; a test red without it.
3. **Where each comes from.** The GM's (G).
4. **Do they describe the world here?** Yes - measured 2026-10-18: tasks T41-T64 (24) were each added by a hand-written insertion script, about 1-2k tokens of command text apiece (the scripts in this session's transcript; the T60-T64 one alone ran to about 9k characters), and two hand-picked ids (T47, T48) collided with an umbrella heading.
5. **The order.** The target and its script, then the test
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 40 min.
9. **Done, measured.** One goal: `make task-add F=<n> TITLE="..." [SECTION=<file>] [RESEARCH=physical]` writes the box with the next free id and prints it, and the plan section with `T64` filled; `tests/tooling/test_task_add.py` red without it.

### T64 Decisions

**D83 - the next id, the right places.** `scripts/task-add.py` takes the highest `T<n>` in `tasks.md` and `plan.md` together (so an id named only in a heading is never reused), adds one, writes the box before the GM-review box with its research line, and, given SECTION, writes that file's text with `{T}` replaced into `plan.md` before its `## T11 - the close` heading (or at the end). It prints the id.

## T65 - an archived block edited by a typo after its review is not owed (found ticking T59, 2026-10-18)

### T65 Approach (checklist part A)

1. **The goal, in the world.** Archiving a finished plan section never makes a review owed.
2. **The constraints.** Feature 375 FR-044: the archive moves a finished section and voids nothing; FR-005(b): a typo-scale change from the reviewed text is no change. Tooling only; a test red without it.
3. **Where each comes from.** Feature 375 (O); the defect is found at T63's first ticks (amendment 6, the GM's "obvious ... tooling ... improvements").
4. **Do they describe the world here?** Yes - measured 2026-10-18: `make tick F=385 T=T59` was refused for `(removed) ### T49 Approach` and `(removed) ### T49 Decisions`. Both blocks are in `plan-done.md` (a grep counts one heading there, none in `plan.md`), at a digest other than the reviewed one: the T47-to-T49 renumbering was a typo-scale edit after their review, which the live check accepts and the archived check (`block_status`, digest match only) does not.
5. **The order.** The archived check reads the typo rule, then its test.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** One goal: a recorded block that `plan-done.md` holds under its own key, its text there a typo-scale change from the reviewed text, is not owed; `tests/tooling/test_plan_gate.py` red without it, and T59's tick goes through.

### T65 Decisions

**D84 - the archived block judged as the live one is.** `block_status`'s removed-block loop skips a recorded key when `plan-done.md` holds a block of that key whose text is `typo_only` against the reviewed text (the record's own `text`, else the history's at its digest), exactly as a block still in `plan.md` is judged; a digest match still skips it as before, and anything more than a typo is owed as before.

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

## T11 - the close

The checklist to `docs/`, the refusals extended to every feature's tasks (FR-001), the final report (SC-001, SC-002).
