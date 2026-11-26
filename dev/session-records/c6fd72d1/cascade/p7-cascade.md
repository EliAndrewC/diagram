# P7 cascade record (clone diagram-backlog at 849bffb552; 2026-11-24)

Raw outputs beside this file: claims-owed-{1,2,3}.txt, claims-triage-1.txt, claims-triage-reply-1.txt, impl-{1..5}.txt,
record-owed-1.txt, modal-triage-1.txt, modal-triage-reply-1.txt.

## Stage 1 - claims at the landing (L7R_LAND_ALONE=1)

| step | count | note |
|---|---|---|
| mixed-build answers read back (451 T223) | 270 | expected about 242 |
| - owe nothing at their last clean answer | 73 | 270 - 197; as expected |
| - owed again | 197 | 196 triage + the barracks row (code changed) |
| owed in all, first listing | 199 | 161 section triage, 35 code triage, 3 impl-drift (1 code changed, 2 rests changed) |
| cleared by the tool at `claims-triage` | 147 | all docs sections (86 docs/buildings.md, 61 docs/building-programs.md); as expected |
| bundled for the `claims-triage` agent | 49 | expected about 21. 14 docs-section claims (Magistrate's manor 9, Inner court 1, Outer court 2, Sacred features 2) + 35 code-triage claims of the landing's own rust/phases delta (driver, polder, field/build, field/dry, seat, seat/margins) |
| - agent cleared | 44 | one agent, 23 s, 40k tokens |
| - agent TOUCHES -> impl-drift | 5 | all rust/phases (driver.rs::roll 1, field/build.rs::build 4) - the landing's code, not P7 |
| impl-drift owed after triage | 8 claims in 5 files | 3 of P7 + 5 of the landing's code |
| impl-drift verdicts | 8 IN-STEP, 0 DRIFTED | 5 agents, one at a time (no Workflow tool in this agent: check-wave could not run) |
| `claims-owed` at the end | no claim is owed | |

Not owed, printed by `claims-owed` as flags: 41 `stale figure` lines (sun.rs constants LIT_SHARE / SUN_BED_H / HALF_SHADE_BED_H
against nine drawing pages; `stale.rs` says "a flag, never a refusal"; still printed at the end) and 3 `claims-label` lines
(docs/buildings.md Sacred features, bare GUESS whose account names 0116), printed only in the first listing while that section was
owed a triage, gone once it cleared. Neither was touched.

impl-drift, each verdict:

| claim | why owed | verdict |
|---|---|---|
| docs/buildings.md Outer court#barracks | code changed (P7 reworded the claim line: "up to ~145 ft long") | IN-STEP - "the ~145 ft ceiling, which the drawing page records as a GUESS" |
| program_rules.rs HIERARCHY#the cell under the barracks | rests changed (0097) | IN-STEP (tool dropped one rest, 0116.drawing, "a page it does not cite") |
| compound/emit.rs building#dwelling walls across the long side | rests changed (0097) | IN-STEP |
| phases/driver.rs roll#the stages in order | triage TOUCHES (landing code) | IN-STEP |
| phases/field/build.rs build#barley on the drained paddy | triage TOUCHES | IN-STEP |
| phases/field/build.rs build#the brook's flank unhemmed | triage TOUCHES | IN-STEP |
| phases/field/build.rs build#the climb's order | triage TOUCHES | IN-STEP |
| phases/field/build.rs build#the hem's line | triage TOUCHES | IN-STEP |

One NOTED, NOT FILED line came back with the build.rs reply (a cleared middle with the winter pinned bare draws only one hem
band; no spec sets that pin). `claims-checked` recorded 4 of 4 and filed nothing (451 T219).

## Stage 2 - P7's pop-ups

`make record-owed` at the start: 87 units owed by the delta, 32 unanswered = 9 pop-ups x 3 (accuracy, gaps, references) + 4
depictions + record-format:0097. Every pop-up line named BOTH 0097 and 0338 as "a page its Entry names moved".

| step | units | pop-ups |
|---|---|---|
| cleared by the tool at `make modal-triage` | 20 | armory, door, gatehouse, granary, main-gate, servants--quarters (x3 each) + depiction of door and servants--quarters. 0338 (the split) is not in the agent's bundle at all: it sent nothing on |
| bundled for the `modal-triage` agent | 11 | barracks (3 + depiction), retainers--quarters (3 + depiction), karo-s-house (3) |
| - agent cleared | 0 | |
| - agent TOUCHES | 11 | all three pop-ups, on 0097's findings page; barracks and retainers--quarters on the drawing page too |
| modal-research (one agent, 3 pop-ups, 110 s, 149k tokens) | 9 | barracks ACCURACY 1; karo-s-house ACCURACY 1, GAPS 1; retainers--quarters ACCURACY 1, GAPS 1; REFERENCES clean x3 |
| EDITs applied (`make apply-edits`) | 5, 0 refused | below |
| owed by the EDITs (About changed) | modal-form x3 | barracks, karo-s-house, retainers--quarters |

The five EDITs (old -> new):

1. barracks.md: "The rowhouses measured ran about 80 to 145 ft long and 12 to 24 ft deep:" -> "The rowhouses measured ran about 80 to 300 ft long, and the gate and foot soldiers' rows 12 to 24 ft deep:"
2. karo-s-house.md: "deep, and a retainer of higher rank had a longer one, up to about 36 ft along the row." -> "...up to about 36 ft along the row; one castle's guards, housed with their families, had dwellings about 30 ft square."
3. karo-s-house.md: "...the magistrate's own retainers seem to have lived in long-houses inside its grounds, while" -> "...inside its grounds, those of highest standing in a block of just two dwellings, while"
4. retainers--quarters.md: "A rowhouse ran about 80 to 145 ft long and 12 to 24 ft deep, built of bays about 12 to 18 ft wide." -> "The rowhouses measured ran about 80 to 300 ft long; the gate and foot soldiers' rows were 12 to 24 ft deep, built of bays about 12 to 18 ft wide."
5. retainers--quarters.md: "...are thought to have lodged in rowhouses inside its grounds." -> "...inside its grounds, those of highest standing seemingly in a block of just two dwellings."

modal-research also listed one OUTSIDE THE CHANGE note (retainers--quarters' Depiction says "never a square block"; left to
modal-depiction); `record-checked` filed nothing for it.

Stage 2, continued:

| step | units | result |
|---|---|---|
| modal-form (one agent, 3 pop-ups, 70 s) - owed only because the research EDITs changed each About | 3 | barracks 0 FIX 2 NOTE; karo-s-house 2 FIX 1 NOTE; retainers--quarters 0 FIX 1 NOTE |
| EDITs applied | 2 (karo-s-house), 1 skipped (barracks NOTE) | below; `apply-edits` first REFUSED the reply whole because the agent wrote three "EDIT: none - ..." lines (451 T195's form rule); applied from a copy with those lines reworded (modal-form-reply-1.apply.txt) |
| re-owed by the form EDITs | 0 | karo-s-house accuracy/gaps/references "settled with its answer - a wording round's EDITs alone moved it, no fact changed (451 T188)" |
| modal-depiction (one agent, 2 pop-ups, 48 s) | 2 | barracks and retainers--quarters: COVERAGE 0, TRUTH 0, LINKS 0; no EDIT |
| `make record-owed UNANSWERED=1` at the end | no record check is owed | |

modal-form EDITs:

6. karo-s-house.md (FIX M2): `About: The karo, the "house elder", was a lord's chief retainer.` -> `About: The karo's house was the home of the karo, the "house elder", a lord's chief retainer.`
7. karo-s-house.md (FIX M18): "in small houses (koya) and long-houses (nagaya)," -> "in small houses and long-houses (nagaya),"
8. NOT applied - barracks.md (NOTE M2): "and a gate rowhouse tiled; one row has earth walls" -> "and a gate rowhouse could be tiled; ...". A NOTE, on a sentence P7 did not touch; listed for the session.

modal-form NOTEs left with no edit (each "for the session"): (i) barracks About now reads "80 to 300 ft" while the map draws no
barracks over about 145 ft, and neither Depiction nor Guesses says so (the drawing page's new GUESS `barracks-length-ceiling` is on
no pop-up); (ii) karo-s-house says "long-house" where the sibling pop-ups say "rowhouse"; (iii) retainers--quarters' new "block of
just two dwellings" clause sits beside its Depiction's "never a square block".

## Stage 3 - record-format:0097 (the tripwire)

`make arbiter-bundle BATCH=1` found no owed round trigger, and the round counter (per active feature, 451 here) held 0 rounds of
`record-format|q:0097`, so the only trigger the tool would bundle was `round:record-format|q:0097@1` - though check-passes.jsonl
shows record-format dispatched on q-0097 four times today in P7's sessions. No guard would have stopped a further dispatch from
this session. record-format was NOT dispatched. The round-arbiter ruled ACCEPT (recorded in specs/451-.../arbiter.jsonl; the unit
then read answered): every block of 849bffb552's 0097 hunks was read in P7's rounds, the last round's two VOCABULARY findings are
answered in the commit. Its three follow-ups: (1) the `tamon turret` glossary term - confirmed present
(l7r/diagram/interactive/assets/glossary/28600-tamon turret.json; `glossary: in sync`); (2) 0338 owes only what the record lists
for it - nothing unanswered; (3) the 12-berth / 15-man barracks finding filed as a row - filed as 452 T25 (room first: five
dwellings in about 60 ft).

## Stage 4 - gates

`make page-check` exit 0; `make record CHECK=1` "builds cleanly (4361 page(s))"; `make quick` clean. No red.

## Stage 5 - ledger

`make ledger-owed WRITE=` wrote 8 rows (5 impl-drift, modal-research, modal-form, modal-depiction) and refused the 3 spec-fidelity
plan-review rows "as the landing's own - make land writes them"; appended by hand as instructed (T223 section CLEAR 230 s; plan-delta
of 25 blocks BLOCKED on a deferred defect 210 s, then CLEAR 93 s). `make ledger-owed` then lists nothing. If `make land` writes its
own copies, the three hand rows are duplicates to drop.

## PREDICTED vs ACTUAL

| unit | predicted | actual |
|---|---|---|
| sheet/retainers--quarters (research + drawing page) | re-check, change needed | triage TOUCHES both pages; ACCURACY 1 + GAPS 1, two EDITs; form NOTE; depiction clean - AS PREDICTED |
| sheet/barracks (research + drawing page) | re-check, change needed | triage TOUCHES both pages; ACCURACY 1, one EDIT; form 2 NOTE; depiction clean - AS PREDICTED |
| sheet/servants--quarters | in step | cleared by the TOOL (no agent read it); its "about 145 by 24 ft" is Shibata's row, unchanged - AS PREDICTED |
| sheet/armory, door, gatehouse, granary, main-gate | clear | all cleared by the tool - AS PREDICTED |
| sheet/karo-s-house | clear ("long, narrow, single-story" still true of a row) | NOT AS PREDICTED: triage TOUCHES (the squat Sakai block), modal-research ACCURACY 1 + GAPS 1 (two EDITs), modal-form 2 FIX (two EDITs) |
| sheet/door, servants--quarters depiction | clear | cleared by the tool - AS PREDICTED |
| docs/building-programs.md Magistrate's manor#staff housing knob; docs/buildings.md (others) | clear | staff housing knob: same mechanical clear in the index (IN-STEP 2026-11-24, feature 432), not in this round's bundle; the Outer court's other two bundled claims (stable below barracks etc.) cleared by the triage agent - AS PREDICTED |
| docs/buildings.md Outer court#barracks | re-check if it gives the limits | impl-drift, IN-STEP (P7 had already restated it to "up to ~145 ft long") - AS PREDICTED |
| program_rules.rs COMMON_ROOM_KIND, ROW_KINDS, lodging_entrances x2 | clear | never in this round's owed list or triage bundle; the index holds each IN-STEP (2026-11-18 / 11-23) with `cleared: mechanically: a page it cites moved and no block it rests on did (feature 432)` - AS PREDICTED |
| program_rules.rs HIERARCHY#the cell under the barracks | clear | full impl-drift ("rests changed"), IN-STEP - one check more than predicted |
| compound/emit.rs building#dwelling walls across the long side | clear | full impl-drift ("rests changed"), IN-STEP - one check more than predicted |
| the split to 0338 | (not predicted; must send nothing on) | sent nothing: every pop-up line named 0338 as moved, the tool cleared all of it, and 0338 never reached an agent's bundle |

## Judgment

(a) Over-cascade.
- The split: none. 0338 cost zero agent reads.
- The two "rests changed" claims (HIERARCHY cell, emit.rs dwelling walls) went straight to a full impl-drift without a triage.
  Neither states a length; both came back IN-STEP in 8-14 s. Cheap (about 110k tokens together), but a triage would have cleared
  them: the block each rests on changed, and the rule sends that on whatever the claim says.
- karo-s-house: the triage's reason (the squat Sakai block against "long, narrow") is defensible but thin - the pop-up's sentence
  describes a row, and 0097 still opens with the same sentence. Once in, it had no "change since" section, so modal-research read
  the WHOLE pop-up; its two EDITs do rest on P7's new facts (Matsusaka's 30 ft dwellings, the Sakai two-dwelling block). The two
  modal-form FIXes (the opening sentence, "(koya)") reword text P7 never touched: real form defects, correctly fixed once found,
  but found only because the research EDITs re-owed a whole-pop-up form read. That chain (page fact -> research EDIT -> form round
  on untouched words) is the one place this cascade edited beyond the change.
- modal-form on barracks and retainers--quarters: owed by the research EDITs, read only the changed pairs, no FIX. Proportionate.
- No check was dispatched twice in THIS round, and the record-format round was replaced by a ruling. But these were not first
  readings: modal-research's reply says "Round 2 passed this" (barracks) and "Round 3's applied fix holds" (retainers--quarters),
  and modal-form calls itself "a later round" - the pop-ups had been through two or three rounds earlier today for other changes.
  No guard counted them here, the same per-feature counter gap as record-format's. Not a missed tripwire for P7: the earlier
  rounds were on other changes, and each agent read only what changed since.
- At the landing: 35 code-triage claims of the landing's own rust/phases delta went to the agent (the 49 against the expected 21);
  5 went on to impl-drift, all IN-STEP. That is the landing's code, not P7 and not the mixed-build rule misfiring, and it is the
  whole miss, exactly: 270 - 242 = 49 - 21 = 28 more code-triage claims than estimated.

(b) Under-cascade.
- I read the three pop-ups. barracks.md and retainers--quarters.md now say "The rowhouses measured ran about 80 to 300 ft long"
  with the 12-24 ft depth limited to the gate and foot soldiers' rows: that agrees with 0097 as it stands (80 ft the Kaibara gate
  range, rows to about 298 ft, Matsusaka's dwellings 30 ft deep). servants--quarters.md's "about 145 by 24 ft" is the Shibata row
  (143 by 24) and agrees; the tool clearing it unread was right.
- No other SOURCE states the range: a grep for "80 to 145", "145 ft", "145 by 24" over docs/, l7r/, rust/ and pool/ finds only
  those three pop-ups and the docs/buildings.md barracks claim (pool/hamlets/mizuguchi's notes hit is an unrelated "145 ft" distance).
- BUILT COPIES ARE STALE: the five magistracy sheets' HTML (pool/magistracies/{county-magistracy-example,hayakawa-magistracy,
  ochiba-magistracy,ochiba-roundtrip-test,ubame-magistracy}/*.html) each still embed "80 to 145" once. They are untracked build
  products in this clone, so nothing here is wrong in git, but the old sentence shows until the sheets are rendered again (the
  landing's render / render-sync). Not regenerated here.
- ONE GAP LEFT OPEN: the drawing page's two new GUESS items (`barracks-length-ceiling`, `row-of-48-ft`) reach no pop-up. The
  barracks About now tells the reader rows ran to 300 ft while the map never draws one past 145 ft, and nothing on its Guesses or
  Depiction tab says the ceiling is this project's choice. modal-form saw it and left it "for the session"; modal-depiction ruled it
  not owed (a guess, not a convention); modal-research's GAPS did not raise it. No check owns "a new GUESS item on a drawing page
  belongs on the Guesses tab of the pop-up that draws it". Suggested: a Guesses bullet `{0097#barracks-length-ceiling}` on barracks
  (and `{0097#row-of-48-ft}` on retainers--quarters) - not done here, since it adds a fact and re-owes a research round.
- A wrinkle inside 0097 itself, untouched: its opening still says a rowhouse was "of one story" while its new Yamauchi row is "of
  two stories". The pop-ups' "one story" agrees with the opening.

(c) Today's rules.
- 451 T223 (mixed-build answers read back): behaved. 270 read back, 73 owed nothing, 147 cleared by the tool, the barracks row to
  impl-drift; no full impl-drift per claim. Counts off the estimate (270 not 242; 49 not 21 to the agent) for the reason above.
- 451 T218 (hold a "pages are silent" finding): did not fire; no reply said the pages were silent. One near case: the HIERARCHY
  verdict opens "no cited page ranks a cell against a barracks" yet is IN-STEP and was recorded without a hold - correct if T218
  holds only findings, worth a look if it was meant to catch that sentence.
- 451 T219 (outside notes listed, not filed): behaved - impl-drift's NOTED, NOT FILED line and modal-research's OUTSIDE THE CHANGE
  note filed nothing. Neither was echoed by the recording command, so "listed" means only in the saved reply.
- 451 T188 (a wording round's EDITs settle the fact checks): fired on karo-s-house and stopped a second research round.
- 451 T195 (EDIT block form): fired on modal-form's "EDIT: none" lines and refused the whole reply, FIX blocks included - the
  agent's contract and the parser disagree; one of them should change.
- 451 T220 (a claim marked a known departure is re-judged when its code or page moves) and T221 (a corrected claim's old verdict
  is cleared or re-owed): not exercised. All 8 impl-drift verdicts were IN-STEP on claims with no known-departure mark and no
  standing DRIFTED/MISLABELED verdict, so neither rule had an occasion.
- The round tripwire did NOT fire for record-format:0097: the counter is per active feature and P7's rounds were counted elsewhere.
  Only the brief's warning kept a fifth dispatch from going out.

## Files changed (uncommitted, unstaged)

dev/claims-index.json (large: 2560 insertions, 6894 deletions - worth a glance before committing); dev/review-ledger.md (11 rows);
l7r/diagram/interactive/assets/modals/sheet/{barracks,karo-s-house,retainers--quarters}.md;
specs/451-time-retro-and-efficiency/arbiter.jsonl (the arbiter's ruling); specs/452-building-plan-followups/tasks.md (T25).
No rust/ file touched. The clone is 37 commits behind main (hook notice); no sync-in was run.

## The build stamp (measured; informational)

The 191 claim answers this round recorded are stamped `build: {commit: fd7aa5d6dd, dirty: [12 rust/gate files]}`: the l7r-gate
binary in use was built at fd7aa5d6dd with T223's then-uncommitted code. Each of the 12 stamped blob hashes EQUALS the same file at
HEAD (`git rev-parse HEAD:<path>`, 12 of 12 match) - the dirty content is exactly what 42c13774ac committed - which is why
`L7R_LAND_ALONE=1 make claims-owed` ends "no claim is owed". The answers stand unless something under rust/gate changes before the
landing; then re-run that command. The index diff's size (2560 insertions, 6894 deletions) is the stamps: 270 old ones of up to
23 dirty files replaced by 191 of 12.

T25's filing was checked against the feature files: the 12-of-15 finding stood only as an OPEN line in
specs/449-rust-codebase/briefs/t371g-handoff.md, in no tasks.md (452 T014 is the neighboring 48 ft / 24 x 67 ft mismatch, a
different question).
