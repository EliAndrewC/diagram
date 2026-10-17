# Process pitfalls evidenced in the audit bundle

Pointer forms: `[UTC-minute session]` = a gm-prompts.txt header; `arbiter #N` = line N (0-based) of arbiter-signal.jsonl, with its
`utc`/`trigger`; `report-NNN` = the feature report. gm-review.jsonl only repeats arbiter rulings (no new pitfall). Voice errors read
silently (e.g. "role" = roll). The prompts file has multi-line prompts split into unheaded fragment lines; fragments are cited by
their text.

Ordered by cost x frequency, largest first.

## 1. Defending an unresearched number or rule (a knob treated as a requirement)
- **evidence**:
  - [2026-10-17T14:34 d2dc8c63] "a Claude Code session thrashing on trying to fit every farmhouse in a nucleated settlement within 700 feet of the rice paddies ... it said ... there was literally no reason for it ... we spent literal hours of wall clock time"
  - [2026-10-03T15:43 bf917120] "is the amount of area ... the result of our research findings? ... Or did we just kind of arbitrarily pick a density ... and then we are enforcing that ... a specific implementation that we have continued to follow blindly"
  - [2026-10-03T16:13 bf917120] "I had misunderstood about the 700 feet thing ... it is not a hard constraint" (the throw-away-and-relayout loop existed to honor it, see #2)
  - arbiter #118 (2026-10-13T10:38Z): "Both are the session's own guesses, and fitting the well more tightly into ground already taken is packing"
- **cost**: "literal hours" for the 700 ft (GM, 10-17); a whole relayout subsystem built around it (10-03); unstated otherwise.
- **what would have caught it**: "Is the number this code is failing against from the research, or a guess, convention or convenience value, and what happens if I move it?"
- **how often**: 4 (700 ft reach / nucleated-area cap, the 80 ft well seat and 22 ft lattice step, the 6 ft floor and similar "soft threshold" guesses surfaced in modals, and the 19-degree lane rule in #4 below counts separately).

## 2. Packing or relayout instead of giving more room
- **evidence**:
  - [2026-10-03T15:53 bf917120] "there is no polynomial solution to the bin packing problem ... I think that it probably makes sense to get rid of this pattern completely" (throw-away-and-redraw of farmhouses)
  - [2026-10-17T14:34 d2dc8c63] "we will try to implement a feature by essentially trying to solve the bin packing problem or to try to rearrange houses instead of rearranging paths"
  - feedback_room_before_packing.md: "Batch 13's bamboo strip burned five routes on seating order when room was never tried." Arbiter #116 (10-13T10:18Z): "This is packing ... widening the verge to 8 ft changed nothing, so the problem is a lack of room"; arbiter #121 (10-13T13:03Z): route matrix A-D each "put a refusal into the cohort", homestead ground 104 to 110 to 116 "took the cohort from 13/16 to 12/16"
- **cost**: batch 13 spent five routes and a superseded ruling (#107 then #109, 41 min apart); wave 155 engine change reverted (arbiter #121); several hours per the GM. Exact hours unstated.
- **what would have caught it**: "Before any packing or seating-order experiment: is the binding number researched, and is the first route more room per homestead?"
- **how often**: 4 independent (farmhouse relayout 10-03, batch 13 strip, w154 lane wells, w155 seed 10).

## 3. Rearranging houses (or reserving lanes first) to make footpaths tidy
- **evidence**:
  - [2026-10-17T14:34 d2dc8c63] fragment: "Nobody in real life moves their house so that a footpath will join with another footpath at a more intuitive angle ... betrays a fundamental misunderstanding of what we are doing and why"
  - [2026-10-03T03:08 bf917120] "I do not believe that we should reserve lanes first ... village lanes are footpaths that are worn by people walking between houses ... homesteads, and then the village lanes came after."
  - [2026-10-03T22:39 bf917120] "if there is a minimum distance between homesteads then doesn't that guarantee that it will always be possible to put a lane" (the session kept proposing an expensive access-path search; the GM supplied the cheap spacing rule)
- **cost**: unstated; the lanes-first idea was "tried before, and it made things harder" (10-03T03:08); the access-path search was dropped entirely once the gap rule was adopted (10-03T22:43).
- **what would have caught it**: "Does this change conform to how these things actually developed? Footpaths are walked after the houses exist; am I moving the cause to fix the effect?"
- **how often**: 3 (lanes-first, moving homestead features for footpaths, access-path search instead of a spacing rule).

## 4. Applying a rule without asking whether it applies under an exception
- **evidence**:
  - [2026-10-17T14:34 d2dc8c63] fragment: "our lane placement algorithm had a rule that ... two lanes shouldn't come together at a 19 degree angle. And then lanes would come together at that angle because of an obstruction ... at no point did the Claude Code session say ... should this rule actually apply when there are obstructions?"
  - same fragment: "multiple solutions to the thing that we were thrashing on, one of which was relaxing a restriction by placing a principled exception ... and one ... adding a new rule" (merge near-parallel footpaths into one)
- **cost**: "thrashing" (no hours stated).
- **what would have caught it**: "What was this rule for, does it still mean that when an obstruction forces the case, and would an exception or a new rule (merge) solve it?"
- **how often**: 1 stated by the GM (it is the same family as #1).

## 5. Check-round cascades: each edit re-owes every check, fixes applied one at a time
- **evidence**:
  - report-374, Dispatches and Rounds tables: impl-drift `claims-owed` 82 rounds, claims-triage 40, modal-triage 27, 679 check dispatches "over 12922 changed lines", 22 tripwires listed from 06:18 to 12:28 on one day
  - gm-prompts fragment (session self-analysis): "Research-record checks cascade. Each edit to a research page or modal re-owes every check ... The privy page (0047) went through about eight rounds for what amounted to a few sentences. Wave 61 alone took roughly 30 agent dispatches, most of them for prose." and "So the last five hours went into closing one batch, not into fixes."
  - [2026-10-11T12:44 d698c481] GM: "needing 3 rounds seems like a lot if it's consistently happening for pop-ups; does that imply a deficiency in our process"
- **cost**: five hours for one batch (session's own number); 25 min waiting for review agents in one stretch (GM, 10-11T12:44); 51% of 374's active time was "thinking".
- **what would have caught it**: "Am I about to edit a checked page once per suggestion? Batch the suggestions, apply once, check once."
- **how often**: 3 independent batches (privy page 0047, waves 61, the claims-owed / servants-quarters run on 10-12).

## 6. Finding gate failures only at the end of a batch, or re-running expensive tests every wave
- **evidence**:
  - [2026-10-08T13:38 8d3395e5] "That hook and guard exists specifically to prevent you from doing the thing that it sounds like you have been doing ... falling into the habit of running the expensive tests every time."
  - gm-prompts fragment: "Gate failures from earlier waves showed up only at the batch close. One was a test stale since wave 57"
  - report-374: gates green 27, red 12; Bash 8h12, `make hooks-test` 30 min, `make land-tooling` 1h03, `make ledger-owed` 25 min
- **cost**: 12 red gates in 374; unstated hours. Arbiter #112: the ledger guard fired about fourteen times and one hook refusal "took the printf before it down too, so the reply file was never written" (a session working around a guard instead of fixing it; it was fixed by the arbiter's tooling_fix).
- **what would have caught it**: "Which fast tests can I run per wave so a gate-only failure surfaces now, not at the close?"
- **how often**: 3.

## 7. Settling a route on a partial regression matrix, then having to supersede it
- **evidence**:
  - arbiter #107 (2026-10-13T00:05Z) accepted route A with valley seed 18 waived; arbiter #109 (00:46Z): "This ruling supersedes the accept of route A ... it never saw a pool reference map refuse. A refusing Inashiro is a regression it did not cover."
  - arbiter #109 tooling_fix: "make arbiter-ask refuses a route or regression question whose cited evidence lacks the pool roll's result for every route it offers"
  - arbiter #121 tooling_fix: the session opened a `settle_knots` probe when a known found row (`settle_the_web#a re-deal of the seats`) already listed the seeds
- **cost**: one ruling cycle plus a re-roll of five routes (A-E) (hours unstated); wave 155 reverted.
- **what would have caught it**: "Have I measured every route against the pool, cohort and the known-refusals list before asking?"
- **how often**: 2.

## 8. Continuing past a ruling, or writing prose as if the question were settled
- **evidence**:
  - arbiter #118 (10-13T10:38Z): after the 90 ft probe failed "the session switched to a finer well-lattice step ... which is packing, and the ruling did not name it ... wrote a well_siting--lane pop-up as if the lane form were settled ... also sent the T46 plan back for a round 3 over Sawada's well ... which the 10:19 ruling had already settled"
- **cost**: unstated (a pop-up, a plan round, and engine edits to undo).
- **what would have caught it**: "Is this step named in the ruling? If the ruling's probe failed, what is the next step it names?"
- **how often**: 1.

## 9. Filing features or deferring tooling fixes without telling the GM
- **evidence**:
  - [2026-10-10T19:00 56edb63e] "past Claude Code sessions have seen that there was work to be done, and then without asking me, filing a spec change feature for it, and then maybe they told me, but they told me in the middle of like two days worth of scrolling text"
  - [2026-10-10T22:49 d698c481] "I'm a little concerned that the arbiter recommended that tooling fix be made, and then maybe it just got lost ... the longer the session, the more likely it is that it will get lost"
  - [2026-10-12T04:35 20ffe008] a tooling fix "declined ... because of an interpretation of something that I had previously said"; the GM: "my words are being interpreted to mean something that I didn't necessarily intend"
- **cost**: GM surprise and a new approval rule (feature 377), a make-done double-run fix owed (arbiter #123/#124: "two make done runs of one clone at the same time"); hours unstated.
- **what would have caught it**: "Is this a new feature or a reopen? Say it in the final message and get approval first."
- **how often**: 3.

## 10. Reading the GM's ruling harder than he meant it
- **evidence**:
  - gm-prompts fragment (undated paste): "My 'ruling' on preferring to stay close was not a hard requirement; merely an 'all else being equal, try this first'. I don't see why that would add time."
  - [2026-10-12T04:35 20ffe008] "my words are being interpreted to mean something that I didn't necessarily intend" (a tooling fix declined over the About tab)
  - [2026-10-09T10:57 a46870c7] "I didn't realize there was a 250-word limit on About text. I don't think there should be such a small limit."
- **cost**: unstated.
- **what would have caught it**: "Is this a preference (tie-break) or a limit? Quote his words and ask how hard."
- **how often**: 3.

## 11. Documentation or plates showing something other than what the algorithm does
- **evidence**:
  - [2026-10-02T15:18 bf917120] "Yes, please fix that page to show what we are actually doing. For that matter, can you do an audit of that page to see what else might be inaccurate?"
  - gm-prompts fragment: "the red lines don't really make a lot of sense to me ... it does not look like the red lines actually correspond to the barriers that we would be using ... that shape extends into the rice paddy fields where certainly none of that could go"
- **cost**: GM questions over two exchanges (10-02T15:14, 19:13); the cost of a confusing plate was a wrong picture of "15 s for 15 households".
- **what would have caught it**: "Does the page/plate draw what the code does (the actual constraint), checked against one real run?"
- **how often**: 2.

## 12. Asking the GM what the research can decide
- **evidence**:
  - feedback_research_decides_tradeoffs.md (GM 2026-10-02): "the judgement call should ALWAYS be 'whichever of these options appears to be in accordance with our research findings'"
  - [2026-10-03T16:31 bf917120] the GM, asked, applied exactly that ("The seven hundred feet is based on real research, but ... this was the norm, this is what was expected") and chose overflow, i.e. a soft preference
- **cost**: unstated (blocking questions: the GM calls session stop-and-ask "worst of all", 10-10T22:49).
- **what would have caught it**: "Has the research comparison been run before I ask? Ask only if the record is silent or contradictory."
- **how often**: 1-2.

---

## (a) Approaches the GM praised or confirmed (keep these in the checklist)
1. [2026-10-03T22:43 bf917120] "I think we can do the gap rule plus some kind of cheap check; the lane layout is expensive and could be made relatively cheap if we guaranteed space for lanes during homestead placement. This does let us drop the search entirely" - a spacing rule instead of a search.
2. [2026-10-02T11:07 bf917120] "That's great work, and I'm glad that we've made it so much more efficient" after the GM's "there must be something deeply inefficient" push (40 households 427 s to 83 s per MEMORY); the lesson is that a number that will not move is a request to measure.
3. [2026-10-04T04:32 bf917120] "we should eliminate both the exit strip and the field way as things placed in advance of the homesteads ... it sounds like a complication we don't need" - remove a pre-reservation when the existing space does the job.
4. [2026-10-10T15:28 8d3395e5] "we need to enforce good procedure at the tooling level, because anything that requires someone to just remember to do the right thing is not tenable" - and [2026-10-11T01:32 d698c481] "things should go to the arbiter at the point where they were previously coming to me".
5. Arbiter #112 (10-13T05:30Z) confirmed a good batch: "it measured the sties, tried more room first (HOMESTEAD_GROUND_FT 110/116, SEATING_GROUND_FT 172) ... found that room only moved the ways web's refusals around, seated the sty after the ways stand" - room first, measure, then change order. Also [2026-10-12T02:50 d698c481] "measuring CPU time instead of wall clock time does seem best".

## (b) The three largest time sinks, from the reports (idle time excluded)
1. **Thinking**: 374 = 25 h 30 min (51% of active time); 375 = 18 h 47 min (63%); 383 = 3 h 19 min (46%). It dominates every report.
2. **Tool time in `Bash` and make targets**: 374 = "other tool" 14 h 36 min (29%), of which Bash 8 h 12 min, `make land-tooling` 1 h 03 min, `make hooks-test` 30 min, `make ledger-owed` 25 min, `make map` 24 min; 375 = other tool 4 h 31 min (Bash 2 h 30); 383 = 2 h 36 min (Bash 1 h 17, hooks-test 15 min).
3. **Review/check cascades**: 374 = 679 check dispatches over 12,922 changed lines; impl-drift 116 dispatches (`claims-owed` 82 rounds), general-purpose triage 87 (claims 40, modals 27), modal-depiction 158, spec-fidelity 107; waiting on subagents 3 h 10 min; 12 red gates; 35 plan reviews BLOCKED. Elsewhere: 383's plan-blocks spec-fidelity took 11 rounds; 375 had 50 spec-fidelity dispatches with 15 plan reviews BLOCKED; waiting on the GM was 4 h 28 min (374) and 4 h 09 min (375).

---

## Addendum: the 106 round-cap accepts (spec round 1, FR-002)

A second Sonnet extractor read every round-cap accept in `specs/*/arbiter.jsonl` (106 rulings), against pitfalls 1-12 above.



Counts are by my reading of each `why` (one primary cause per ruling; keyword checks: 45 say converged/no oscillation/nothing reversing, 58 mention an edit "since round 2"). Triggers: modal-depiction 40, modal-form 23, modal-research 22, quote-check 8, record-format 7, source-reader 3, building-review 2, translation-check 1. By feature: 343 = 44, 374 = 30, 352 = 27, 368 = 3, 335 = 2.

### Cause tally
| # | cause | n |
|---|---|---|
| A | Real finding each round, each smaller than the last, all applied, nothing reversing (the cap fired on a converging loop) | 39 |
| B | Round 2 clean; round 3 owed only by a LATER edit (a sibling check's wording fix, another check's answer, an unrelated wave) to text already passed | 27 |
| C | One fan-out round (modal-research/depiction/form on copse, grove, windbreak, homestead-grove) ruled once and copied to 21 triggers; "@3" overstated forms that ran once | 21 |
| D | Bundle or counter lacked the data: no Rounds section / edits.diff / kept reply ("Fired: (not in arbiter-owed.json)"), arbiter ruled from diffs and the session's account | 7 |
| E | Counter charged another feature's rounds (368's cascades on 0047 charged to 352) | 6 |
| F | Finding with "EDIT: none, the session must decide", or re-flagged as NEW though REPEATED; another round cannot settle it | 4 |
| G | building-review round cap (paperwork round, a lobe fix 1 ft past a guide) | 2 |

Examples and quotes:
- A: 0104 record-format (feature 343), "Every finding was glossary-level wording, every one was applied, and none reversed an earlier fix." Buckwheat depiction (row 73): "four rounds ... only NEW findings ... each was smaller than the one before". Several findings were on long-standing text, not on the last fix (field-dike, fish-trap, perimeter modals: "already in the tab before this feature").
- B: q:0190 quote-check: "This is not a loop ... The cap fired because two later edits, made to answer other checks, left the drawing page with text these checks had not read yet." q:0091: "round 3 is owed only by wave 124's two-bullet impl-drift edit". Garden-pond: "round 3 fired only because modal-form's round-2 commit touched the file afterwards" (clerks- modal-research).
- C: "Round 2 ... found at most one small item per pop-up ... Everything edited since round 2 is modal-form's period-for-document rewording" (rows 52-72 identical).
- D: nakamon/residence/garden/side-gate modal-form: "This bundle holds no rounds and no edits and says the trigger is not in arbiter-owed.json".
- E: "the counter charged 368's rounds to 352 and there is nothing of 352's on 0047 to re-check."
- F: side-gate depiction: "What stands is REPEATED and EDIT-none ... the bundle tags them NEW."
- Also (B/D): q:0219 "The owe of translation-check ... has no change behind it: in owes-round.diff that note is a context line only." Row 101: "The bundle missed both because it looks for the unit's path in the changed lines, and a modal's own lines never contain that path."

Almost every ruling (about 100 of 106) ends the same way: the next round would re-read text already passed; none found a genuinely reversing or oscillating loop.

### Existing pitfalls these add to
- #5 (check-round cascades, fixes one at a time): about 100 of 106 (A, B, C, plus the cap/owe mechanics of D-F). Example: rows 52-72, 21 triggers closed by one ruling after "modal-form's period-for-document rewording" re-owed research and depiction. Also feature 343 (44 rulings) and 352 (27) as further independent batches beyond privy 0047 and wave 61; modal 3-round pattern (A) confirms the GM's 10-11 question.
- #6 (gate/test cost at batch end): 0 here.
- #7-#10, #12: 0. Nothing in the file bears on packing, GM rulings or research asks.

## 13. (new) the round-cap tripwire fires on tooling error, not on a loop
- **evidence**: 13 rulings (E 6, D 7) plus part of B: counter charged to the wrong feature (rows 46-51); bundle lacks rounds/edits so the arbiter "rules on the session's account" (rows 2, 34, 35, 38, 40, 45); bundle's "owed" cause missing the real change (row 101, row 96/99 "no changed line names 0091", "context line only"). Several rulings carry `tooling_fix` text (row 0: do not owe another round when the only change is the check's own EDIT applied word for word).
- **cost**: one arbiter dispatch plus re-reading per trigger (106 dispatches; the asks are unpriced in the file, minutes each).
- **what would have caught it**: before dispatching an arbiter, check the owing diff names a visible-word change on the unit, and that the round count is this feature's own; a check's own EDIT applied verbatim should not re-owe the check.
- **how often**: 13 of 106 directly; B-type (edit by sibling check re-owing a passed check) 27 more.

### Top recurring subjects (trigger units, round suffix stripped)
1. q:0104 (343 and 335 pages; record-format, quote-check, source-reader) - 5
2. modal:sheet/nakamon, modal:sheet/residence, q:0047, modal:choice/kosatsuba_seat--bridgehead - 4 each
By feature: 343 = 44, 374 = 30, 352 = 27. Next most (3): modal:sheet/magistrate-s-dais, kneeling-positions, guest-quarters.
